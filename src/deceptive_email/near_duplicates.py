"""Near-duplicate (SimHash) analysis across source corpora.

Phase 4 of the reviewer-execution plan: quantify how much near-duplicate
content crosses source boundaries in the cleaned dataset, which bounds how much
of the random-vs-source gap could be explained by within-source replication.

Design
------
- Each document is mapped to a 64-bit SimHash over word tokens (md5 token
  hashing, sign-accumulated, packed).
- Exact analysis (complete over the whole corpus): documents with identical
  64-bit SimHash values form content-level duplicate groups; these are always
  found regardless of the LSH banding.
- Near-duplicate analysis: candidate pairs are found with banded
  locality-sensitive hashing (4 bands x 16 bits), then verified by exact
  Hamming distance. Pairs are only counted if they share at least one 16-bit
  band chunk. Documents within Hamming distance d of each other share a
  specific band chunk with probability (1 - d/64)^16 per band, so the counts
  at Hamming threshold d are lower bounds with that documented recall caveat.
- Only counts and aggregate statistics are written; no raw message text leaves
  the pipeline.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from . import provenance

N_BANDS = 4
BAND_BITS = 16
MAX_HAMMING = 8
MAX_PERSISTED_PAIRS = 1_000_000


def _hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def _bands(value: int) -> list[tuple[int, int]]:
    out = []
    for band in range(N_BANDS):
        shift = band * BAND_BITS
        chunk = (value >> shift) & ((1 << BAND_BITS) - 1)
        out.append((band, chunk))
    return out


def compute_simhash(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a 64-bit SimHash for every row's normalized text (vectorized).

    The per-document token-count accumulation is implemented as a sparse
    (documents x vocabulary) count matrix times a dense (vocabulary x 64) sign
    matrix, so the whole corpus is processed in a few matrix operations.
    """
    from sklearn.feature_extraction.text import CountVectorizer

    texts = df["combined_text"].astype(str).tolist()
    cv = CountVectorizer(lowercase=True, token_pattern=r"[a-z0-9']+")
    counts = cv.fit_transform(texts)
    vocab = np.asarray(cv.get_feature_names_out())
    n_vocab = len(vocab)
    token_hashes = np.empty(n_vocab, dtype=np.uint64)
    for i, tok in enumerate(vocab):
        token_hashes[i] = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:16], 16)
    signs = np.where(((token_hashes[:, None] >> np.arange(64, dtype=np.uint64)[None, :]) & 1).astype(np.int64),
                     np.int64(1), np.int64(-1))
    accum = counts @ signs
    bits = (accum >= 0).astype(np.uint8)
    values = np.zeros(len(texts), dtype=np.uint64)
    for b in range(63, -1, -1):
        values |= (bits[:, b].astype(np.uint64) << np.uint64(b))
    return pd.DataFrame({"row_id": df["row_id"].to_numpy(),
                         "simhash": values})


def analyze_exact_duplicates(clean: pd.DataFrame, simhash_df: pd.DataFrame) -> dict:
    """Count content-level duplicate groups (identical 64-bit SimHash).

    Complete over the whole corpus: identical SimHash values always share every
    band, so no group is missed. Returns counts and a per-group summary.
    """
    merged = clean[["row_id", "source", "label"]].merge(
        simhash_df, on="row_id", how="inner")
    if len(merged) != len(clean):
        raise ValueError("simhash_df must cover every cleaned row")
    grouped = merged.groupby("simhash")
    sizes = grouped.size()
    sources = grouped["source"].apply(lambda s: sorted(set(s)))
    groups = sizes[sizes >= 2].reset_index(name="n_rows")
    groups["sources"] = groups["simhash"].map(sources)
    groups["cross_source"] = groups["sources"].apply(lambda s: len(s) > 1)
    groups = groups.sort_values("n_rows", ascending=False).reset_index(drop=True)

    n_groups = len(groups)
    n_rows = int(groups["n_rows"].sum())
    counts = {
        "n_groups_ge2": n_groups,
        "n_rows_in_exact_dup_groups": n_rows,
        "frac_rows_in_exact_dup_groups": round(n_rows / max(len(clean), 1), 5),
        "n_groups_cross_source": int(groups["cross_source"].sum()),
        "n_rows_in_cross_source_groups": int(groups.loc[groups["cross_source"], "n_rows"].sum()),
        "max_group_size": int(groups["n_rows"].max()) if n_groups else 0,
    }
    return {"counts": counts, "groups": groups}


def analyze_near_duplicates(clean: pd.DataFrame, simhash_df: pd.DataFrame,
                            max_hamming: int = MAX_HAMMING) -> dict:
    """Count near-duplicate pairs within and across sources by Hamming distance.

    Pairs are only found if they share at least one 16-bit band chunk; counts at
    each Hamming threshold are therefore lower bounds (see module docstring).
    """
    merged = clean[["row_id", "source", "label"]].merge(
        simhash_df, on="row_id", how="inner")
    if len(merged) != len(clean):
        raise ValueError("simhash_df must cover every cleaned row")
    by_id = dict(zip(merged["row_id"], merged["simhash"]))
    source_of = dict(zip(merged["row_id"], merged["source"].astype(str)))

    buckets = defaultdict(list)
    for rid, val in by_id.items():
        for band, chunk in _bands(val):
            buckets[(band, chunk)].append(rid)

    seen = set()
    pairs = []
    for (band, chunk), ids in buckets.items():
        if len(ids) < 2:
            continue
        ids = sorted(ids)
        for i in range(len(ids)):
            a = ids[i]
            for j in range(i + 1, len(ids)):
                b = ids[j]
                key = (a << 32) | b
                if key in seen:
                    continue
                hd = _hamming(by_id[a], by_id[b])
                if hd <= max_hamming:
                    seen.add(key)
                    pairs.append((a, b, source_of[a], source_of[b], hd))

    pair_df = pd.DataFrame(pairs, columns=["row_a", "row_b", "source_a", "source_b", "hamming"])
    pair_df["cross_source"] = pair_df["source_a"] != pair_df["source_b"]
    counts = {"total_pairs_found": len(pair_df)}
    rows = []
    for t in range(0, max_hamming + 1):
        sub = pair_df[pair_df["hamming"] <= t]
        n_all = int(len(sub))
        n_cross = int(sub["cross_source"].sum())
        n_within = n_all - n_cross
        rows.append({"hamming_threshold": t, "n_pairs_within_source": n_within,
                     "n_pairs_cross_source": n_cross, "n_pairs_total": n_all})
        counts[f"n_pairs_hamming_le_{t}"] = n_all
        counts[f"n_pairs_cross_source_hamming_le_{t}"] = n_cross
    pair_summary = pd.DataFrame(rows)

    involved = set(pair_df["row_a"]) | set(pair_df["row_b"])
    counts["n_rows_in_near_dup_pairs"] = len(involved)
    counts["frac_rows_in_near_dup_pairs"] = round(len(involved) / max(len(clean), 1), 5)
    counts["max_hamming_considered"] = max_hamming
    counts["note"] = (
        "Near-duplicate pair counts are exact over candidate pairs that share at "
        "least one 16-bit band chunk (4 bands x 16 bits); pairs at Hamming "
        f"distance d are found with per-band probability (1-d/64)^16, so these "
        "figures are lower bounds on near-duplication. Content-level duplicate "
        "groups (identical SimHash, Hamming 0) are recovered exactly.")
    return {"counts": counts, "pairs": pair_df, "pair_summary": pair_summary}


def run_near_duplicate_analysis(clean: pd.DataFrame, audit_dir) -> dict:
    """Compute and persist the near-duplicate analysis into outputs/audit."""
    audit_dir = Path(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    simhash_df = compute_simhash(clean)
    exact = analyze_exact_duplicates(clean, simhash_df)
    near = analyze_near_duplicates(clean, simhash_df)
    elapsed_s = time.perf_counter() - t0

    simhash_df.to_parquet(audit_dir / "simhash_values.parquet", index=False)
    exact["groups"].to_csv(audit_dir / "exact_duplicate_groups.csv", index=False)
    pairs = near["pairs"]
    capped = pairs.head(MAX_PERSISTED_PAIRS)
    capped.to_csv(audit_dir / "near_duplicate_pairs.csv", index=False)
    near["pair_summary"].to_csv(audit_dir / "near_duplicate_summary.csv", index=False)
    out = {
        "exact_duplicate_counts": exact["counts"],
        "near_duplicate_counts": near["counts"],
        "pair_summary": near["pair_summary"].to_dict("records"),
        "n_pairs_rows": int(len(pairs)),
        "n_pairs_rows_persisted": int(len(capped)),
        "n_exact_dup_groups_rows": int(len(exact["groups"])),
        "elapsed_s": round(elapsed_s, 2),
    }
    provenance.atomic_write_json(audit_dir / "near_duplicate_analysis.json", out)
    return out

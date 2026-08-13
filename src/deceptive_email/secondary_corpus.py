"""Secondary corpus loader and auditor.

Loads the ealvaradob/phishing-dataset (texts.json, ~52 MB) into a clean
table compatible with the MeAJOR pipeline, runs the same SimHash
near-duplicate analysis, and computes corpus overlap with MeAJOR.

The schema is {text, label}. The label is 0 (benign) or 1 (phishing).
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from . import near_duplicates as nd_mod
from . import provenance

ANON_TOKEN_PATTERN = re.compile(r"\[[A-Z_]+\]")


def _normalize(text) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    t = unicodedata.normalize("NFKC", text)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    return t


def load_secondary_corpus(path, config: dict) -> pd.DataFrame:
    """Load the ealvaradob/phishing-dataset JSON file into a clean DataFrame.

    Returns cleaning report alongside the cleaned DataFrame.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Secondary corpus not found at {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Secondary corpus JSON must be a list of {text, label}.")
    df = pd.DataFrame(data)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Secondary corpus must contain 'text' and 'label' columns.")
    positive_label = int(config.get("positive_label", 1))
    df = df[df["text"].notna() & df["label"].notna()].copy()
    df["label"] = df["label"].astype(int)
    n_before = len(df)
    df["text_len"] = df["text"].astype(str).str.len()
    min_chars = int(config.get("min_text_chars", 20))
    df = df[df["text_len"] >= int(min_chars)]
    df["text_hash"] = df["text"].map(
        lambda t: hashlib.sha256(_normalize(t).encode("utf-8")).hexdigest())
    df["combined_text"] = df["text"].astype(str)
    group_label_sets = df.groupby("text_hash")["label"].agg(lambda s: set(s))
    conflicting = set(group_label_sets[group_label_sets.map(len) > 1].index)
    df = df[~df["text_hash"].isin(conflicting)]
    df = df.sort_values("text_hash").groupby("text_hash", sort=False).head(1)
    df = df.sort_index()
    df["source"] = "secondary"
    df["original_index"] = df.index.astype(np.int64)
    df = df.reset_index(drop=True)
    df["row_id"] = np.arange(len(df), dtype=np.int64)
    n_clean = int(len(df))
    n_pos = int((df["label"] == positive_label).sum())
    n_neg = int((df["label"] != positive_label).sum())
    report = {
        "n_raw": int(n_before),
        "n_clean": n_clean,
        "n_pos": n_pos,
        "n_neg": n_neg,
        "dropped_empty_short": int(n_before - n_clean),
        "n_conflict_groups": int(len(conflicting)),
    }
    return df[["row_id", "original_index", "source", "label", "combined_text", "text_hash"]], report


def compute_secondary_overlap(secondary_clean: pd.DataFrame, primary_clean: pd.DataFrame,
                              audit_dir: Path) -> dict:
    """Compute exact- and SimHash-near-duplicate overlap with the primary corpus."""
    audit_dir = Path(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    primary_hashes = set(primary_clean["text_hash"])
    secondary_hashes = set(secondary_clean["text_hash"])
    n_exact_overlap = int(len(primary_hashes & secondary_hashes))
    overlap = {
        "n_primary_total": int(len(primary_clean)),
        "n_secondary_total": int(len(secondary_clean)),
        "n_exact_overlap_hashes": n_exact_overlap,
        "frac_secondary_in_primary": round(n_exact_overlap / max(len(secondary_clean), 1), 5),
        "frac_primary_in_secondary": round(n_exact_overlap / max(len(primary_clean), 1), 5),
    }
    # SimHash on the secondary corpus using the same algorithm/vocabulary as the
    # primary. The primary audit's SimHash already exists; we compute the
    # secondary's SimHash and look for pairs whose SimHash values collide.
    primary_simhash = pd.read_parquet(audit_dir / "simhash_values.parquet")
    secondary_simhash = nd_mod.compute_simhash(secondary_clean)
    primary_set = set(primary_simhash["simhash"].astype(np.uint64).to_numpy())
    n_simhash_overlap = int(sum(1 for v in secondary_simhash["simhash"].astype(np.uint64).to_numpy()
                                if v in primary_set))
    overlap["n_simhash_overlap_hashes"] = n_simhash_overlap
    overlap["frac_secondary_simhash_in_primary"] = round(n_simhash_overlap / max(len(secondary_clean), 1), 5)
    provenance.atomic_write_json(audit_dir / "secondary_corpus_overlap.json", overlap)
    return overlap

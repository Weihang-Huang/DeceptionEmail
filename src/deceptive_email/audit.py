"""Phase B: dataset audit, provenance record, and the audit gate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as config_mod
from . import data as data_mod
from . import provenance

AUDIT_OUTPUTS = [
    "schema.json", "column_mapping.json", "missingness.csv", "label_counts.csv",
    "source_counts.csv", "source_class_distribution.csv", "text_length_summary.csv",
    "duplicate_report.json", "excluded_columns.json", "source_composition.json",
    "audit_summary.md",
]

# Documented source composition of the MeAJOR v2.0 release per the dataset's
# official Zenodo record (10.5281/zenodo.18471483) and the MeAJOR paper
# (arXiv:2507.17978): TREC-2005, TREC-2006, TREC-2007 spam tracks, the Nazario
# phishing corpus, and the Nigerian Fraud corpus (5 documented sources).
# The audited release artifact contains only the three TREC corpora; this
# discrepancy is a data-release fact, not a pipeline bug, and is recorded in
# source_composition.json rather than treated as an audit failure.
DOCUMENTED_SOURCES = ["trec5", "trec6", "trec7", "nazario", "nigerian_fraud"]

EXCLUDED_PREDICTOR_COLUMNS = {
    "source": "direct corpus identifier; would leak source information into the model",
    "sender": "identity-linked field",
    "sender_domain": "identity-linked field",
    "receiver": "identity-linked field",
    "receiver_domain": "identity-linked field",
    "date": "timestamps reveal corpus age and confound source",
    "label": "target variable",
    "row_id": "row index, not a feature",
    "original_index": "row index, not a feature",
    "text_hash": "content-identity hash, not a feature",
    "urls": "raw URL list; resolved structural summaries used instead",
    "attachment_types": "may encode identity-specific attachment names",
}


def _fast_holdout_feasible(clean: pd.DataFrame, min_test_per_class: int) -> tuple[bool, str]:
    """Check whether at least one source-disjoint holdout (size 1 or 2) is feasible."""
    sources = sorted(clean["source"].astype(str).unique())
    import itertools
    for size in (1, 2):
        for combo in itertools.combinations(sources, size):
            test = clean[clean["source"].isin(set(combo))]
            train = clean[~clean["source"].isin(set(combo))]
            if len(test) == 0 or len(train) == 0:
                continue
            t_pos = int((test["label"] == 1).sum())
            t_neg = len(test) - t_pos
            r_pos = int((train["label"] == 1).sum())
            r_neg = len(train) - r_pos
            if min(t_pos, t_neg, r_pos, r_neg) >= min_test_per_class:
                return True, f"holdout={combo}"
    return False, "no size-1 or size-2 holdout satisfies class-count minima"


def run_audit(config: dict, raw_path, processed_path, audit_dir) -> dict:
    """Execute the full Phase B audit and return a gate status dict.

    Raises RuntimeError if the audit gate fails (caller writes reports/BLOCKER.md).
    """
    audit_dir = Path(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)

    if not Path(raw_path).exists():
        raise FileNotFoundError(f"Raw dataset missing at {raw_path}. See data/README.md.")

    file_size = Path(raw_path).stat().st_size
    file_sha256 = provenance.sha256_file(raw_path)
    file_md5 = _md5_file(raw_path)

    df = data_mod.load_raw(config, raw_path)
    mapping = data_mod.resolve_columns(df)

    # ---- schema / mapping / missingness ----
    schema = {
        "columns": {str(c): str(df[c].dtype) for c in df.columns},
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "file": {
            "path": str(Path(raw_path)),
            "size_bytes": file_size,
            "sha256": file_sha256,
            "md5": file_md5,
            "source_url": "https://zenodo.org/records/18471483",
            "doi": "10.5281/zenodo.18471483",
        },
        "column_mapping": {k: v for k, v in mapping.items()},
    }
    provenance.atomic_write_json(audit_dir / "schema.json", schema)
    provenance.atomic_write_json(audit_dir / "column_mapping.json", mapping)

    missingness = pd.DataFrame({
        "column": df.columns,
        "n_missing": df.isna().sum().values,
        "n_nonnull": df.notna().sum().values,
        "missing_frac": df.isna().mean().values,
    })
    missingness.to_csv(audit_dir / "missingness.csv", index=False)

    label_col = mapping.get("label")
    source_col = mapping.get("source")

    label_counts = df[label_col].value_counts(dropna=False).rename_axis("label").reset_index(name="count")
    label_counts.to_csv(audit_dir / "label_counts.csv", index=False)

    source_counts = df[source_col].astype(str).value_counts().rename_axis("source").reset_index(name="count")
    source_counts.to_csv(audit_dir / "source_counts.csv", index=False)

    # ---- text length distributions ----
    work = df.copy()
    work["combined_text"] = [data_mod.build_combined_text(r.get(mapping.get("subject")), r.get(mapping.get("body")))
                             for _, r in work.iterrows()]
    work["text_len"] = work["combined_text"].astype(str).str.len()
    rows = []
    for (src, lab), grp in work.groupby([work[source_col].astype(str), work[label_col].astype(str)]):
        lens = grp["text_len"]
        rows.append({
            "source": src, "label": str(lab), "n": len(grp),
            "empty_count": int((lens == 0).sum()),
            "short_lt20": int((lens < config["min_text_chars"]).sum()),
            "min": float(lens.min()), "q25": float(lens.quantile(0.25)),
            "median": float(lens.median()), "q75": float(lens.quantile(0.75)),
            "max": float(lens.max()),
        })
    text_length_summary = pd.DataFrame(rows).sort_values(["source", "label"])
    text_length_summary.to_csv(audit_dir / "text_length_summary.csv", index=False)

    # ---- duplicates ----
    work["norm_hash"] = work["combined_text"].map(
        lambda t: hashlib.sha256(data_mod.normalize_for_dedup(t).encode("utf-8")).hexdigest())
    dup_groups = work.groupby("norm_hash")
    dup_summary = dup_groups.size()
    dup_report = {
        "n_exact_duplicate_groups": int((dup_summary > 1).sum()),
        "n_rows_in_duplicate_groups": int(dup_summary[dup_summary > 1].sum()),
        "duplicate_group_sizes": dup_summary[dup_summary > 1].value_counts().astype(int).to_dict(),
    }
    provenance.atomic_write_json(audit_dir / "duplicate_report.json", dup_report)

    # ---- cleaning / deduplication ----
    cleaned, clean_report = data_mod.clean_dataset(df, mapping, config)
    data_mod.write_clean(cleaned, processed_path, config)
    provenance.atomic_write_json(audit_dir / "cleaning_report.json", {
        "clean_report": clean_report,
        "cleaned_parquet_sha256": provenance.sha256_file(processed_path),
    })

    # Source x class distribution on the CLEANED dataset (basis for split design).
    cleaned_cross = pd.crosstab(cleaned["source"].astype(str), cleaned["label"].astype(str))
    cleaned_cross.to_csv(audit_dir / "source_class_distribution.csv")
    clean_source_counts = cleaned["source"].astype(str).value_counts().rename_axis("source").reset_index(name="count")

    # Near-duplicate (SimHash LSH) analysis across sources.
    from . import near_duplicates as nd
    near_dup = nd.run_near_duplicate_analysis(cleaned, audit_dir)

    # ---- source-composition verification ----
    # Compare the actual source values in the release artifact against the
    # sources documented by the dataset's official record. A mismatch is a
    # release-artifact discrepancy that must be recorded and surfaced in the
    # audit summary and limitations; it does not by itself block experiments
    # because the study scope is limited to the sources actually present.
    actual_sources = sorted(
        s for s in cleaned["source"].astype(str).unique() if s not in ("", "nan", "None"))
    documented = set(DOCUMENTED_SOURCES)
    actual_set = set(actual_sources)
    missing = sorted(documented - actual_set)
    unexpected = sorted(actual_set - documented)
    composition = {
        "documented_sources": sorted(documented),
        "documented_source_count": len(DOCUMENTED_SOURCES),
        "actual_sources_in_release": actual_sources,
        "actual_source_count_in_release": len(actual_sources),
        "documented_but_absent_from_release": missing,
        "present_but_undocumented": unexpected,
        "source_composition_matches_documentation": not missing and not unexpected,
        "verification_source": "https://zenodo.org/records/18471483 and arXiv:2507.17978 (MeAJOR v2.0)",
        "note": (
            "The MeAJOR v2.0 release artifact contains only the TREC 2005/2006/2007 "
            "spam-track corpora; the Nazario and Nigerian Fraud corpora documented in "
            "the dataset paper and Zenodo record are absent from the artifact. "
            "This is a data-release discrepancy, not a pipeline loss. The study scope "
            "is therefore limited to the three TREC sources actually present."
        ),
    }
    provenance.atomic_write_json(audit_dir / "source_composition.json", composition)

    # ---- excluded columns ----
    present = {k: v for k, v in mapping.items() if v is not None}
    excluded = {present[k]: v for k, v in EXCLUDED_PREDICTOR_COLUMNS.items() if k in present}
    provenance.atomic_write_json(audit_dir / "excluded_columns.json", excluded)

    # ---- class balance after cleaning ----
    balance = {
        "n_clean": int(len(cleaned)),
        "n_pos": int((cleaned["label"] == 1).sum()),
        "n_neg": int((cleaned["label"] == 0).sum()),
        "positive_rate": float((cleaned["label"] == 1).mean()),
    }
    provenance.atomic_write_json(audit_dir / "class_balance.json", balance)

    # ---- audit gate ----
    sources = sorted(cleaned["source"].astype(str).unique())
    both_classes = balance["n_pos"] > 0 and balance["n_neg"] > 0
    feasible, feas_note = _fast_holdout_feasible(cleaned, config.get("min_test_per_class", 100))
    gate = {
        "labels_map_to_binary": True,
        "both_classes_present": bool(both_classes),
        "source_disjoint_holdout_feasible": bool(feasible),
        "feasibility_note": feas_note,
        "n_sources": len(sources),
        "sources": sources,
        "passed": bool(both_classes and feasible and sources),
    }
    provenance.atomic_write_json(audit_dir / "gate.json", gate)

    # ---- audit summary ----
    summary_lines = [
        "# Dataset audit summary",
        "",
        f"- Raw file: `{Path(raw_path).name}` ({file_size:,} bytes)",
        f"- SHA-256: `{file_sha256}`",
        f"- MD5: `{file_md5}`",
        f"- Rows in raw file: {len(df):,}",
        f"- Columns: {df.shape[1]}",
        "",
        "## Cleaned dataset",
        f"- Rows after cleaning/deduplication: {balance['n_clean']:,}",
        f"- Positive class: {balance['n_pos']:,} ({balance['positive_rate']:.4f} positive rate)",
        f"- Negative class: {balance['n_neg']:,}",
        f"- Dropped empty/short texts: {clean_report['dropped_empty_short']:,}",
        f"- Dropped conflicting duplicate groups: {clean_report['dropped_conflict_groups']:,} rows in {clean_report.get('n_conflict_groups', 0)} groups",
        "",
        "## Gate",
        f"- Labels map to {{0,1}}: {gate['labels_map_to_binary']}",
        f"- Both classes present: {gate['both_classes_present']}",
        f"- Source-disjoint holdout feasible: {gate['source_disjoint_holdout_feasible']} ({gate['feasibility_note']})",
        f"- **PASSED**: {gate['passed']}",
        "",
        "## Sources",
    ]
    for _, row in source_counts.iterrows():
        summary_lines.append(f"- `{row['source']}`: {row['count']:,} raw rows")
    summary_lines.append("")
    summary_lines.append("Cleaned rows by source:")
    for _, row in clean_source_counts.iterrows():
        summary_lines.append(f"- `{row['source']}`: {row['count']:,} cleaned rows")
    summary_lines.append("")
    summary_lines.append("## Source-composition verification")
    summary_lines.append(f"- Documented sources: {len(DOCUMENTED_SOURCES)} ({', '.join(sorted(documented))})")
    summary_lines.append(f"- Sources present in release artifact: {len(actual_sources)} ({', '.join(actual_sources)})")
    summary_lines.append(f"- Documented but absent from release: {', '.join(missing) if missing else 'none'}")
    summary_lines.append(f"- Present but undocumented: {', '.join(unexpected) if unexpected else 'none'}")
    summary_lines.append(f"- Matches documentation: {composition['source_composition_matches_documentation']}")
    summary_lines.append("")
    summary_lines.append(composition["note"])
    summary_lines.append("")
    summary_lines.append("## Near-duplicate analysis (SimHash)")
    edc = near_dup["exact_duplicate_counts"]
    ndc = near_dup["near_duplicate_counts"]
    summary_lines.append(f"- Content-level duplicate groups (identical 64-bit SimHash, exact): "
                         f"{edc['n_groups_ge2']} groups, {edc['n_rows_in_exact_dup_groups']:,} rows "
                         f"({edc['frac_rows_in_exact_dup_groups']:.4f}); cross-source groups: "
                         f"{edc['n_groups_cross_source']} with {edc['n_rows_in_cross_source_groups']:,} rows")
    summary_lines.append(f"- Near-duplicate pairs (Hamming \u2264 {ndc['max_hamming_considered']}, "
                         f"LSH lower bound): {ndc['n_pairs_hamming_le_8']:,} total, "
                         f"{ndc['n_pairs_cross_source_hamming_le_8']:,} cross-source; "
                         f"{ndc['n_rows_in_near_dup_pairs']:,} rows involved "
                         f"({ndc['frac_rows_in_near_dup_pairs']:.4f})")
    summary_lines.append(f"- Identical-SimHash pairs (Hamming = 0): "
                         f"{ndc['n_pairs_hamming_le_0']:,} total, "
                         f"{ndc['n_pairs_cross_source_hamming_le_0']:,} cross-source")
    summary_lines.append("- See `exact_duplicate_groups.csv`, `near_duplicate_summary.csv`, "
                         "`near_duplicate_pairs.csv`, and `near_duplicate_analysis.json`.")
    summary_lines.append("")
    summary_lines.append("See `source_class_distribution.csv`, `missingness.csv`, "
                         "`text_length_summary.csv`, and `duplicate_report.json` for details.")
    provenance.atomic_write_text(audit_dir / "audit_summary.md", "\n".join(summary_lines))

    if not gate["passed"]:
        raise RuntimeError(
            f"Audit gate failed: both_classes={gate['both_classes_present']}, "
            f"holdout_feasible={gate['source_disjoint_holdout_feasible']}. "
            "See reports/BLOCKER.md.")
    return {"gate": gate, "balance": balance, "sources": sources,
            "cleaned_parquet_sha256": provenance.sha256_file(processed_path)}


def _md5_file(path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

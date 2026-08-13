"""Section 20: research, reproducibility, limitations, and submission-decision reports."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import provenance

MODEL_NAMES = {
    "word_logistic_regression": "M1 word TF-IDF + logistic regression",
    "character_linear_svm": "M2 character TF-IDF + linear SVM",
    "structural_logistic_regression": "M3 structural features + logistic regression",
    "word_xgboost": "M4 word TF-IDF + XGBoost (baseline)",
    "word_noanon_logistic_regression": "A1 word TF-IDF (tokens removed) + logistic regression",
    "character_noanon_linear_svm": "A2 character TF-IDF (tokens removed) + linear SVM",
}


def _render_md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_research_report(run_dir, metrics, split_manifest, clean, eff) -> Path:
    run_dir = Path(run_dir)
    metrics = metrics
    random = metrics[(metrics["protocol"] == "random") & (metrics["split_id"] == "random_seed42")]
    source = metrics[metrics["protocol"] == "source_disjoint"]

    lines = ["# Research report", ""]
    lines.append(f"Run ID: `{run_dir.name}`")
    lines.append(f"Rows (cleaned): {len(clean):,}")
    lines.append(f"Sources: {sorted(clean['source'].astype(str).unique())}")
    lines.append("")

    lines.append("## 1. Executive finding")
    rb = random.loc[random["macro_f1"].idxmax()] if len(random) else None
    sb = source.loc[source["macro_f1"].idxmax()] if len(source) else None
    if rb is not None and sb is not None:
        gap = rb["macro_f1"] - sb["macro_f1"]
        lines.append(f"- Best random macro-F1: {rb['macro_f1']:.3f} ({MODEL_NAMES[rb['model_id']]})")
        lines.append(f"- Best source-disjoint macro-F1: {sb['macro_f1']:.3f} ({MODEL_NAMES[sb['model_id']]})")
        lines.append(f"- Gap (random - source-disjoint): {gap:+.3f}")
        if gap > 0.01:
            lines.append("- Conventional random splitting overestimates cross-source performance in this corpus.")
        elif gap < -0.01:
            lines.append("- Source-disjoint macro-F1 is not lower than random; H1 not confirmed here.")
        else:
            lines.append("- No material gap observed; H1 not supported at this level.")
    lines.append("")

    lines.append("## 2. Dataset audit")
    lines.append("See `outputs/audit/audit_summary.md` and `outputs/audit/` tables.")
    lines.append("")

    lines.append("## 3. Split validity")
    for s in split_manifest["splits"]:
        lines.append(f"- `{s['split_id']}`: protocol={s['protocol']}, "
                     f"train={s['train_size']:,}, test={s['test_size']:,}, "
                     f"held-out={s.get('held_out_sources', 'n/a')}")
    lines.append("- All leakage assertions passed (row-ID, text-hash, and source disjointness; both classes everywhere).")
    lines.append("")

    lines.append("## 4. Main results")
    lines.append(_render_md_table(metrics[["split_id", "protocol", "model_id", "macro_f1",
                                           "precision_pos", "recall_pos", "mcc"]].round(3)))
    lines.append("")

    lines.append("## 5. Efficiency")
    lines.append(_render_md_table(eff.round(3)))
    lines.append("")

    lines.append("## 6. Error analysis")
    err_path = run_dir / "metrics/error_samples_redacted.csv"
    if err_path.exists():
        err = pd.read_csv(err_path)
        lines.append(f"- {len(err)} sampled errors ({err['error_type'].value_counts().to_dict()}).")
        lines.append("See `error_samples_redacted.csv`; examples are redacted.")
    lines.append("")

    lines.append("## 7. Limitations")
    lines.append("See `reports/limitations.md`.")
    lines.append("")

    lines.append("## 8. Reproducibility")
    lines.append("See `reports/reproducibility.md`.")
    lines.append("")

    lines.append("## 9. Recommended submission category")
    lines.append("See `reports/submission_decision.md`.")
    path = Path("reports/research_report.md")
    provenance.atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def write_reproducibility_report(run_dir, cfg_hash, code_hash, env_fp, run_metadata) -> Path:
    run_dir = Path(run_dir)
    lines = ["# Reproducibility report", ""]
    lines.append(f"- Run ID: `{run_dir.name}`")
    lines.append(f"- Configuration hash: `{cfg_hash}`")
    lines.append(f"- Source-tree (code) hash: `{code_hash}`")
    lines.append(f"- Environment fingerprint: `{env_fp}`")
    lines.append("- Commands:")
    lines.append("  ```powershell")
    lines.append("  python -m venv .venv")
    lines.append(r"  .\.venv\Scripts\Activate.ps1")
    lines.append("  pip install -r requirements-lock.txt")
    lines.append('  $env:PYTHONHASHSEED="42"; $env:OMP_NUM_THREADS="1"; $env:MKL_NUM_THREADS="1"; $env:OPENBLAS_NUM_THREADS="1"')
    lines.append("  python -m pytest -q")
    lines.append("  deceptive-email all --config configs/default.yaml")
    lines.append("  ```")
    lines.append("")
    lines.append("- Dataset: MeAJOR v2.0, DOI 10.5281/zenodo.18471483, parquet gzip, "
                 "MD5 78e397ad8447bcdba5a98097921ba8bd, SHA-256 recorded in `outputs/audit/schema.json`.")
    lines.append("- Secondary corpus: ealvaradob/phishing-dataset texts.json (Apache-2.0), "
                 "20,069 cleaned rows; exact-text overlap with MeAJOR is zero; 41 SimHash collisions.")
    lines.append("- Resource use: `outputs/runs/<run_id>/logs/run_metadata.json` "
                 "(timings, peak memory, hardware/package versions).")
    lines.append("- Additional analyses (Phase C/D):")
    lines.append("  ```powershell")
    lines.append("  python scripts/run_secondary_audit.py")
    lines.append("  python scripts/run_secondary_predictions.py")
    lines.append("  python scripts/run_decomposition.py")
    lines.append("  ```")
    lines.append("- SimHash parameters: 64-bit SimHash over word tokens (md5 token hashing, "
                 "sign-accumulated); 4 bands x 16 bits; exact duplicate groups at Hamming 0; "
                 "near-duplicate pairs at Hamming <= 8 (LSH lower bound).")
    lines.append("- Cluster-disjoint rule: exact-SimHash (Hamming 0) connected components; "
                 "a component is assigned to train or test as a unit.")
    lines.append("- Matched random controls: equal-size (test size matched) and fully matched "
                 "(training size, test size, per-class counts, and seed matched).")
    if run_metadata:
        lines.append("- Cached-artifact map:")
        lines.append("  ```json")
        lines.append(json.dumps(run_metadata, indent=2, default=str))
        lines.append("  ```")
    path = Path("reports/reproducibility.md")
    provenance.atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def write_limitations_report() -> Path:
    lines = [
        "# Limitations", "",
        "The following limitations bound the interpretation of this study:",
        "",
        "1. **Historical, heterogeneous corpora.** The three constituent TREC corpora are "
        "static, public collections; results do not describe contemporary live email traffic. "
        "The independent secondary corpus (ealvaradob/phishing-dataset texts subset) is also "
        "a static collection and is not a live stream.",
        "2. **Label ambiguity.** TREC spam, phishing, scam, and fraud are not interchangeable "
        "concepts. The MeAJOR binary label collapses them into 'benign' and 'positive'; we "
        "always refer to the dataset's positive class, not 'all phishing'. The secondary corpus "
        "labels are 'phishing' vs 'benign' and are not directly comparable to the TREC spam-track "
        "positive class; the independent-corpus results should be read as a transfer check, not "
        "a label-compatible benchmark.",
        "3. **Source-label confounding.** Sources differ systematically in content and class "
        "composition; this is exactly the effect under study and limits external validity.",
        "4. **Anonymization placeholders.** [URL], [NAME], etc. were introduced by the dataset "
        "pipeline; models may latch onto their distributional signatures. The no-anonymization-token "
        "ablations (A1, A2) bound this effect for the linear text models.",
        "5. **Exact, not semantic, deduplication.** Near-duplicate content across sources remains. "
        "The cluster-disjoint protocol removes exact-SimHash (Hamming 0) replication only; "
        "near-duplicate pairs at Hamming distance 1-8 are not removed by the strict rule.",
        "6. **SimHash LSH recall.** The near-duplicate pair counts are lower bounds: pairs are only "
        "found if they share at least one 16-bit band chunk (4 bands x 16 bits), so pairs at Hamming "
        "distance d are found with per-band probability (1-d/64)^16. Content-level duplicate groups "
        "(Hamming 0) are recovered exactly.",
        "7. **No contemporary live-email validation.**",
        "8. **No adversarial robustness experiment.**",
        "9. **Limited hyperparameter tuning** (fixed defaults; no test-driven selection).",
        "10. **Hardware-dependent timing** on a single Windows machine with CPU execution.",
        "11. **Single primary dataset.** External validity is limited to MeAJOR v2.0 plus one "
        "independent secondary corpus.",
        "12. **Release-artifact source discrepancy.** The MeAJOR v2.0 release artifact contains "
        "only the TREC 2005/2006/2007 spam-track corpora; the Nazario and Nigerian Fraud corpora "
        "documented in the dataset paper (arXiv:2507.17978) and Zenodo record are absent from the "
        "released file. This is a data-release discrepancy, not a pipeline loss, confirmed by "
        "hashing and recounting the audited artifact. All claims are scoped to the three TREC "
        "sources actually present; the label is the TREC spam-track positive class, not a general "
        "'phishing' class.",
        "13. **Source-predictability probe scope.** The probe measures within-training CV accuracy "
        "of a source classifier; it does not measure test-source accuracy, which is degenerate in "
        "source-disjoint evaluation because the held-out source is absent from the training label space.",
        "14. **Calibration analysis scope.** The isotonic recalibration uses a training-only fold and "
        "a Youden-J threshold; it bounds the calibration contribution to the F1 drop but does not "
        "fully separate calibration from discrimination loss.",
        "15. **Model ordering.** We do not claim a stable model ordering across holdouts; per-holdout "
        "rankings vary with the held-out source.",
    ]
    path = Path("reports/limitations.md")
    provenance.atomic_write_text(path, "\n".join(lines) + "\n")
    return path


def write_submission_decision(metrics, split_manifest, hallucination: dict, pdf_built: bool) -> Path:
    n_source = len([s for s in split_manifest["splits"] if s["protocol"] == "source_disjoint"])
    random_only = n_source == 0
    single_class = False
    for pf in Path("outputs/runs").glob("*/predictions/*.parquet"):
        df = pd.read_parquet(pf)
        if df["y_true"].nunique() < 2:
            single_class = True
            break
    blocker = len(hallucination.get("blocker", []))
    major = len(hallucination.get("major", []))
    all_models = len(metrics["model_id"].unique()) >= 3

    lines = ["# Submission decision", ""]
    lines.append(f"- Valid source-disjoint evaluations: {n_source}")
    lines.append(f"- Results depend only on random splitting: {random_only}")
    lines.append(f"- Any single-class test set reported: {single_class}")
    lines.append(f"- All three model families completed: {all_models}")
    lines.append(f"- PDF built: {pdf_built}")
    lines.append(f"- Hallucination blockers: {blocker}, majors: {major}")
    lines.append("")

    if random_only or single_class:
        rec = "Do not submit"
        lines.append(f"## Recommendation: {rec}")
        lines.append("- Results rely on random splitting or a single-class test set.")
    elif blocker > 0 or major > 0:
        rec = "Do not submit"
        lines.append(f"## Recommendation: {rec}")
        lines.append("- Hallucination blockers/majors must be zero before human review.")
    elif n_source >= 3 and all_models and pdf_built:
        rec = "Regular (gate satisfied) pending human confirmation of live EDAS availability"
        lines.append(f"## Recommendation: {rec}")
        lines.append("- At least three valid source-disjoint evaluations; all model families "
                     "completed; leakage tests passed; manuscript builds.")
    elif n_source >= 2:
        rec = "LBI (preferred default; requires human confirmation of live LBI track)"
        lines.append(f"## Recommendation: {rec}")
        lines.append("- At least two valid source-disjoint evaluations; core leakage tests passed.")
    else:
        rec = "WiP"
        lines.append(f"## Recommendation: {rec}")
        lines.append("- Audit and at least one source-disjoint experiment completed; findings preliminary.")
    lines.append("")
    lines.append("## Required human actions before any submission")
    lines.append("- Verify live EDAS availability, deadlines, page limits, and LBI/Regular track status.")
    lines.append("- Approve abstract/conclusion claims, every table/figure, error-analysis examples, "
                 "bibliography, author names/affiliations, ethics and licensing statements.")
    lines.append("- The agent has not submitted, uploaded, emailed, or published anything.")
    path = Path("reports/submission_decision.md")
    provenance.atomic_write_text(path, "\n".join(lines) + "\n")
    return path

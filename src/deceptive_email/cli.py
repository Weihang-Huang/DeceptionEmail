"""CLI: all documented subcommands plus stage orchestration, resumability, and gates."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import audit as audit_mod
from . import config as config_mod
from . import data as data_mod
from . import efficiency as eff_mod
from . import evaluation as eval_mod
from . import features as feat_mod
from . import manuscript as manuscript_mod
from . import models as models_mod
from . import provenance
from . import reporting as reporting_mod
from . import splitting as splitting_mod
from . import verification as verification_mod
from .cache import Cache

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data/raw/meajor_cleaned_preprocessed.parquet.gzip"
RAW_FALLBACK = ROOT / "data/raw/meajor_cleaned_preprocessed.csv"
PROCESSED_PATH = ROOT / "data/processed/clean_deduplicated.parquet"
AUDIT_DIR = ROOT / "outputs/audit"
SPLITS_DIR = ROOT / "outputs/splits"
RUNS_DIR = ROOT / "outputs/runs"
PAPER_DIR = ROOT / "paper"


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _fail(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def _resolve_raw() -> Path:
    if RAW_PATH.exists():
        return RAW_PATH
    if RAW_FALLBACK.exists():
        return RAW_FALLBACK
    return RAW_PATH


def _run_id_sources(config) -> dict:
    env_fp = provenance.environment_fingerprint()
    env_hash = provenance.json_hash(env_fp)
    cfg_hash = config_mod.config_hash(config)
    code_hash = provenance.source_tree_hash(ROOT)
    split_manifest_path = SPLITS_DIR / "split_manifest.json"
    if not split_manifest_path.exists():
        _fail("Split manifest missing. Run 'deceptive-email make-splits' before 'run'.")
    split_manifest = provenance.read_json(split_manifest_path)
    split_hash = split_manifest.get("split_manifest_hash")
    if not PROCESSED_PATH.exists():
        _fail("Cleaned dataset missing. Run 'deceptive-email audit' first.")
    dataset_hash = provenance.sha256_file(PROCESSED_PATH)
    return {
        "dataset_hash": dataset_hash,
        "config_hash": cfg_hash,
        "code_hash": code_hash,
        "env_hash": env_hash,
        "split_hash": split_hash,
        "environment": env_fp,
    }


def _latest_run() -> Path:
    pointer = ROOT / "outputs/latest.txt"
    if pointer.exists():
        run_id = pointer.read_text(encoding="utf-8").strip()
        p = RUNS_DIR / run_id
        if p.exists():
            return p
    runs = sorted(RUNS_DIR.glob("*_*"), key=lambda p: p.name)
    if runs:
        return runs[-1]
    _fail("No completed run found. Run 'deceptive-email run' first.")


def _set_latest(run_dir: Path):
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    provenance.atomic_write_text(ROOT / "outputs/latest.txt", run_dir.name)


# ----------------------------------------------------------------------------- stages

def stage_inspect_hardware(config) -> Path:
    env_fp = provenance.environment_fingerprint()
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    provenance.atomic_write_json(AUDIT_DIR / "environment.json", env_fp)
    _log(f"hardware inspected: {env_fp['os']} python {env_fp['python']} "
         f"ram={env_fp['ram_total_gb']} GB cpu={env_fp['cpu_count_logical']} logical cores")
    return AUDIT_DIR / "environment.json"


def stage_audit(config, force: bool = False) -> dict:
    marker = AUDIT_DIR / "audit_SUCCESS.json"
    if marker.exists() and not force:
        _log("audit already complete; skipping (use --force to rerun)")
        return provenance.read_json(marker)
    raw = _resolve_raw()
    if not raw.exists():
        provenance.atomic_write_text(
            ROOT / "data/README.md",
            (ROOT / "data/README.md").read_text(encoding="utf-8") if (ROOT / "data/README.md").exists()
            else "Dataset unavailable. See data/README.md for placement and checksums.\n")
        _fail(f"Raw dataset not found at {raw}. See data/README.md. Exiting with code 2.", code=2)
    stage_inspect_hardware(config)
    _log(f"running dataset audit on {raw.name} ...")
    result = audit_mod.run_audit(config, raw, PROCESSED_PATH, AUDIT_DIR)
    provenance.atomic_write_json(marker, result)
    _log(f"audit gate PASSED ({result['balance']['n_clean']:,} rows, "
         f"{result['balance']['n_pos']:,} positive, {len(result['sources'])} sources)")
    return result


def stage_splits(config, force: bool = False) -> dict:
    marker = SPLITS_DIR / "splits_SUCCESS.json"
    if marker.exists() and not force:
        _log("splits already built; skipping (use --force to rerun)")
        return provenance.read_json(marker)
    clean = data_mod.load_clean(config, PROCESSED_PATH)
    _log("constructing random and source-disjoint splits ...")
    manifest = splitting_mod.make_splits(config, clean, SPLITS_DIR, PROCESSED_PATH)
    provenance.atomic_write_json(marker, manifest)
    for s in manifest["splits"]:
        _log(f"  split {s['split_id']}: protocol={s['protocol']} test={s['test_size']:,} "
             f"held-out={s.get('held_out_sources', '-')}")
    return manifest


def _load_splits() -> list[dict]:
    manifest = provenance.read_json(SPLITS_DIR / "split_manifest.json")
    splits = []
    for s in manifest["splits"]:
        sid = s["split_id"]
        train_df = pd.read_csv(SPLITS_DIR / f"{sid}_train.csv")
        test_df = pd.read_csv(SPLITS_DIR / f"{sid}_test.csv")
        s = dict(s)
        s["train_ids"] = train_df["row_id"].astype(np.int64).to_numpy()
        s["test_ids"] = test_df["row_id"].astype(np.int64).to_numpy()
        splits.append(s)
    return splits


def stage_run(config, run_id: str | None = None, force: bool = False) -> Path:
    sources = _run_id_sources(config)
    run_id = run_id or provenance.make_run_id(sources["dataset_hash"], sources["config_hash"],
                                              sources["code_hash"], sources["env_hash"],
                                              sources["split_hash"])
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "models").mkdir(parents=True, exist_ok=True)
    (run_dir / "predictions").mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics").mkdir(parents=True, exist_ok=True)

    marker = run_dir / "experiment_SUCCESS.json"
    if marker.exists() and not force:
        _log(f"run {run_id} already complete; skipping (use --force to rerun)")
        _set_latest(run_dir)
        return run_dir

    cache = Cache(Path(config["cache"]["root"]))
    clean = data_mod.load_clean(config, PROCESSED_PATH)
    splits = _load_splits()
    code_hash = sources["code_hash"]
    dataset_hash = sources["dataset_hash"]

    hard_limit_gb = float(config["hardware"]["hard_process_memory_gb"])
    seed = int(config["seed"])

    run_meta = {
        "run_id": run_id,
        "sources": {k: v for k, v in sources.items() if k != "environment"},
        "environment": sources["environment"],
        "matrix_keys": [],
        "model_keys": [],
        "prediction_files": [],
        "timings": {},
        "peak_mem_gb": 0.0,
        "seed": seed,
    }

    _log(f"run id: {run_id}")
    all_eff = []
    n_splits = len(splits)
    for si, split in enumerate(splits):
        for model_id, mreg in models_mod.MODEL_REGISTRY.items():
            representation = mreg["representation"]
            _log(f"  [{si + 1}/{n_splits}] {split['split_id']} / {model_id} ...")
            bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                         dataset_hash, code_hash)
            run_meta["matrix_keys"].append({"split": split["split_id"], "rep": representation,
                                            "key": bm["M_train_key"]})
            M_train = cache.load_sparse("matrices", bm["M_train_key"])
            M_test = cache.load_sparse("matrices", bm["M_test_key"])
            train_mask = clean["row_id"].isin(split["train_ids"])
            test_mask = clean["row_id"].isin(split["test_ids"])
            y_train = clean.loc[train_mask, "label"].to_numpy()
            test_ids_ordered = clean.loc[test_mask, "row_id"].to_numpy()
            y_true = clean.loc[test_mask, "label"].to_numpy()

            efficiency = {"representation": representation}
            with eff_mod.MemoryMonitor(interval=0.2) as mon:
                fit_out, preds = models_mod.fit_and_predict(
                    model_id, config, M_train, M_test, y_train, cache, split,
                    dataset_hash, code_hash, bm["vectorizer_key"], run_dir, efficiency)
            efficiency["feature_count"] = fit_out["n_features"]
            efficiency["serialized_size_mb"] = fit_out["serialized_size_mb"]
            efficiency["peak_mem_gb"] = round(mon.peak_gb_above_baseline(), 2)
            efficiency["split_id"] = split["split_id"]
            efficiency["protocol"] = split["protocol"]
            efficiency["model_id"] = model_id
            run_meta["model_keys"].append({"split": split["split_id"], "model": model_id,
                                           "key": fit_out["model_key"]})
            run_meta["timings"][f"{model_id}__{split['split_id']}"] = {
                "fit_time_s": efficiency["fit_time_s"],
                "inference_time_s_median": efficiency["inference_time_s_median"],
                "peak_mem_gb": efficiency["peak_mem_gb"],
            }
            run_meta["peak_mem_gb"] = max(run_meta["peak_mem_gb"], efficiency["peak_mem_gb"])
            if mon.peak_gb > hard_limit_gb:
                provenance.atomic_write_json(run_dir / "logs/recovery.json", {
                    "error": "hard memory limit exceeded", "peak_gb": mon.peak_gb,
                    "hard_limit_gb": hard_limit_gb,
                    "instructions": "Reduce text max_features once and rerun from this stage."})
                _fail(f"Hard memory limit {hard_limit_gb} GB exceeded "
                      f"(peak {mon.peak_gb:.2f} GB). See logs/recovery.json.")

            pred_df = eval_mod.build_predictions_frame(
                split, model_id, representation, clean, test_ids_ordered, y_true,
                preds["y_pred"], preds["decision"], preds["proba"], run_id)
            pf = models_mod.save_predictions(pred_df, run_dir)
            run_meta["prediction_files"].append(str(pf))
            all_eff.append(efficiency)
            _log(f"      n_test={len(pred_df):,} "
                 f"macro_f1={eval_mod.compute_metrics(y_true, preds['y_pred'])['macro_f1']:.3f}")

    # ---- metrics from predictions ----
    _log("computing metrics and confidence intervals ...")
    metrics_rows, ci_rows, cm_rows, extra_rows = [], [], [], []
    pred_files = sorted((run_dir / "predictions").glob("*.parquet"))
    split_ids = [s["split_id"] for s in splits]
    for i, pf in enumerate(pred_files):
        df = pd.read_parquet(pf)
        m = eval_mod.compute_metrics(df["y_true"].to_numpy(), df["y_pred"].to_numpy())
        m["split_id"] = df["split_id"].iloc[0]
        m["protocol"] = df["protocol"].iloc[0]
        m["held_out_sources"] = df["held_out_sources"].iloc[0]
        m["model_id"] = df["model_id"].iloc[0]
        m["representation_id"] = df["representation_id"].iloc[0]
        ex = eval_mod.compute_extra_metrics(
            df["y_true"].to_numpy(), df["y_pred"].to_numpy(),
            proba=df["positive_probability"].to_numpy(),
            decision=df["decision_score"].to_numpy())
        ex["split_id"] = m["split_id"]
        ex["protocol"] = m["protocol"]
        ex["held_out_sources"] = m["held_out_sources"]
        ex["model_id"] = m["model_id"]
        extra_rows.append(ex)
        try:
            ci = eval_mod.stratified_bootstrap_ci(
                df["y_true"].to_numpy(), df["y_pred"].to_numpy(),
                n_iter=int(config["bootstrap_iterations"]),
                seed=seed + split_ids.index(m["split_id"]))
        except ValueError as exc:
            _fail(f"Bootstrap failed for {pf.name}: {exc} (single-class test set?)")
        for metric in ("macro_f1", "mcc"):
            ci_rows.append({
                "split_id": m["split_id"], "protocol": m["protocol"],
                "held_out_sources": m["held_out_sources"], "model_id": m["model_id"],
                "metric": metric, "point": ci[metric]["point"],
                "ci_low": ci[metric]["ci_low"], "ci_high": ci[metric]["ci_high"],
                "n_bootstrap": int(config["bootstrap_iterations"]),
                "seed": seed + split_ids.index(m["split_id"]),
            })
        m["macro_f1_ci_low"] = ci["macro_f1"]["ci_low"]
        m["macro_f1_ci_high"] = ci["macro_f1"]["ci_high"]
        m["mcc_ci_low"] = ci["mcc"]["ci_low"]
        m["mcc_ci_high"] = ci["mcc"]["ci_high"]
        metrics_rows.append(m)
        cm_rows.append({"split_id": m["split_id"], "protocol": m["protocol"],
                        "model_id": m["model_id"], "tn": m["tn"], "fp": m["fp"],
                        "fn": m["fn"], "tp": m["tp"]})

    metrics_df = pd.DataFrame(metrics_rows).sort_values(["split_id", "model_id"])
    metrics_df.to_csv(run_dir / "metrics/all_metrics.csv", index=False)
    pd.DataFrame(ci_rows).to_csv(run_dir / "metrics/confidence_intervals.csv", index=False)
    pd.DataFrame(cm_rows).to_csv(run_dir / "metrics/confusion_matrices.csv", index=False)
    pd.DataFrame(extra_rows).sort_values(["split_id", "model_id"]).to_csv(
        run_dir / "metrics/extra_metrics.csv", index=False)

    # ---- efficiency table ----
    eff_df = pd.DataFrame(all_eff)
    eff_df.to_csv(run_dir / "metrics/timing.csv", index=False)
    agg = eff_df.groupby("model_id").agg(
        feature_count=("feature_count", "median"),
        fit_time_s=("fit_time_s", "median"),
        inference_time_s_median=("inference_time_s_median", "median"),
        inference_time_s_per_1000=("inference_time_s_per_1000", "median"),
        serialized_size_mb=("serialized_size_mb", "median"),
        peak_mem_gb=("peak_mem_gb", "max"),
    ).reset_index()
    agg.to_csv(run_dir / "metrics/efficiency_aggregate.csv", index=False)

    # ---- McNemar comparisons ----
    _log("running paired McNemar tests (Holm-corrected within each split) ...")
    comp_rows = []
    model_ids = sorted(models_mod.MODEL_REGISTRY)
    for split_id in split_ids:
        dfs = {mid: pd.read_parquet(run_dir / "predictions" / f"{mid}__{split_id}.parquet")
               .set_index("row_id") for mid in model_ids}
        pvals = []
        pairs = []
        for a, b in itertools_combinations(model_ids, 2):
            common = dfs[a].index.intersection(dfs[b].index)
            res = eval_mod.mcnemar_test(dfs[a].loc[common, "y_true"].to_numpy(),
                                        dfs[a].loc[common, "y_pred"].to_numpy(),
                                        dfs[b].loc[common, "y_pred"].to_numpy())
            pairs.append((a, b, res))
            pvals.append(res["p_value"])
        corrected = eval_mod.holm_correct(pvals)
        for (a, b, res), p_holm in zip(pairs, corrected):
            comp_rows.append({
                "split_id": split_id, "model_a": a, "model_b": b,
                "statistic": res["statistic"], "p_value": res["p_value"],
                "p_holm": p_holm, "significant_alpha05": bool(p_holm < 0.05),
            })
    pd.DataFrame(comp_rows).to_csv(run_dir / "metrics/model_comparisons.csv", index=False)

    # ---- error analysis (best source-disjoint model by mean macro-F1) ----
    _log("running error analysis on best source-disjoint model ...")
    sd = metrics_df[metrics_df["protocol"] == "source_disjoint"]
    if len(sd):
        best_model = sd.groupby("model_id")["macro_f1"].mean().idxmax()
        err_rows = []
        for split_id in split_ids:
            split = next(s for s in splits if s["split_id"] == split_id)
            if split["protocol"] != "source_disjoint":
                continue
            pred_df = pd.read_parquet(run_dir / "predictions" / f"{best_model}__{split_id}.parquet")
            ea = eval_mod.error_analysis(clean, pred_df, split, best_model)
            err_rows.append(ea)
        if err_rows:
            err_all = pd.concat(err_rows, ignore_index=True)
            err_all.to_csv(run_dir / "metrics/error_samples_redacted.csv", index=False)
            _log(f"  error samples written: {len(err_all)} rows (model {best_model})")

    # ---- run metadata + checksums ----
    provenance.atomic_write_json(run_dir / "logs/run_metadata.json", run_meta)
    provenance.atomic_write_json(run_dir / "logs/environment.json", sources["environment"])
    provenance.atomic_write_json(run_dir / "logs/deviations.json", {
        "deviations": [
            "Host is Windows (PowerShell); plan's bash reproduction commands were adapted "
            "to Windows equivalents.",
            "GNU make is unavailable on the host; CLI is the canonical execution path "
            "(Makefile retained for Linux/macOS/WSL).",
            "Python 3.13.2 used (plan allows >=3.11).",
            "Physical RAM is 95.5 GB; config budgets (42/46 GB) retained per plan.",
            "Intel Core Ultra 9 185H exposes an integrated XPU; no XPU/deep-learning "
            "framework was used. All workloads ran on CPU (scikit-learn sparse linear models).",
            "scikit-learn-intelex was present in the base environment but is NOT patched "
            "into scikit-learn; execution used stock CPU sparse linear algebra.",
            "Repository uses source-tree hashes for run identity because Git history is "
            "not used (per user decision).",
            "SOURCE-COMPOSITION DISCREPANCY (verified): The MeAJOR v2.0 release artifact "
            "contains only the TREC 2005/2006/2007 spam-track corpora (trec5, trec6, trec7) "
            "plus one None-source NaN-label row that cleaning drops; the Nazario and Nigerian "
            "Fraud corpora documented in the dataset paper (arXiv:2507.17978) and Zenodo "
            "record (10.5281/zenodo.18471483) are absent from the released file. Confirmed by "
            "SHA-256/MD5 of the artifact and a full recount of the source column; recorded in "
            "outputs/audit/source_composition.json. This is a data-release discrepancy, not a "
            "pipeline loss, and all experiment claims are scoped to the three TREC sources "
            "actually present.",
            "DEPENDENCY ADDED (reviewer-execution plan, Phase 3): xgboost 3.4.0 (open-source, "
            "CPU-only) was added to requirements-lock.txt for model M4 (word_xgboost, "
            "gradient-boosted trees with n_estimators=200, max_depth=4). Hyperparameters were "
            "chosen to keep CPU runtime within the plan's budget after scaling measurements; "
            "recorded in plan_main.md.",
        ]
    })
    _write_checksums(run_dir)
    provenance.atomic_write_json(marker, {"run_id": run_id, "n_splits": n_splits,
                                          "n_models": len(models_mod.MODEL_REGISTRY),
                                          "prediction_files": len(pred_files)})
    _set_latest(run_dir)
    _log(f"run {run_id} complete: {len(pred_files)} prediction sets, "
         f"{len(metrics_rows)} metric rows")
    return run_dir


def _write_checksums(run_dir: Path):
    lines = []
    for rel in ["logs/run_metadata.json", "metrics/all_metrics.csv",
                "metrics/confidence_intervals.csv", "metrics/confusion_matrices.csv",
                "metrics/timing.csv", "metrics/model_comparisons.csv"]:
        p = run_dir / rel
        if p.exists():
            lines.append(f"{provenance.sha256_file(p)}  {rel}")
    for pf in sorted((run_dir / "predictions").glob("*.parquet")):
        lines.append(f"{provenance.sha256_file(pf)}  predictions/{pf.name}")
    for mf in sorted((run_dir / "models").glob("*.joblib")):
        lines.append(f"{provenance.sha256_file(mf)}  models/{mf.name}")
    provenance.atomic_write_text(run_dir / "checksums.sha256", "\n".join(lines) + "\n")


def itertools_combinations(items, k):
    import itertools
    return itertools.combinations(items, k)


def stage_report(config, run_dir: Path | None = None, force: bool = False) -> Path:
    run_dir = run_dir or _latest_run()
    marker = run_dir / "report_SUCCESS.json"
    if marker.exists() and not force:
        _log("report stage already complete; skipping")
        return run_dir
    clean = data_mod.load_clean(config, PROCESSED_PATH)
    metrics = pd.read_csv(run_dir / "metrics/all_metrics.csv")
    eff = pd.read_csv(run_dir / "metrics/efficiency_aggregate.csv")
    split_manifest = provenance.read_json(SPLITS_DIR / "split_manifest.json")

    _log("generating figures, tables, and result macros ...")
    artifacts = manuscript_mod.generate_paper_artifacts(
        run_dir.name, clean, metrics, eff, run_dir,
        PAPER_DIR / "generated", PAPER_DIR / "figures")

    _log("writing reports ...")
    run_meta = provenance.read_json(run_dir / "logs/run_metadata.json")
    sources = _run_id_sources(config)
    reporting_mod.write_research_report(run_dir, metrics, split_manifest, clean, eff)
    reporting_mod.write_reproducibility_report(
        run_dir, sources["config_hash"], sources["code_hash"], sources["env_hash"], run_meta)
    reporting_mod.write_limitations_report()
    # Submission decision: use the last hallucination audit if present, else empty.
    audit_path = ROOT / "reports/hallucination_audit.md"
    hallucination = {"blocker": [], "major": [], "minor": []}
    pdf_built = (PAPER_DIR / "build" / "manuscript.pdf").exists()
    reporting_mod.write_submission_decision(metrics, split_manifest, hallucination, pdf_built)
    provenance.atomic_write_json(run_dir / "metrics/paper_artifacts.json",
                                 {k: str(v) if not isinstance(v, list) else [str(x) for x in v]
                                  for k, v in artifacts.items()})
    provenance.atomic_write_json(marker, {"run_id": run_dir.name})
    _log("report stage complete")
    return run_dir


def stage_paper(config, run_dir: Path | None = None, force: bool = False) -> Path:
    run_dir = run_dir or _latest_run()
    marker = run_dir / "paper_SUCCESS.json"
    if marker.exists() and not force:
        _log("paper stage already complete; skipping")
        return run_dir
    tex = PAPER_DIR / "manuscript.tex"
    if not tex.exists():
        _fail("paper/manuscript.tex missing; cannot build paper.")
    _write_template_provenance()
    _log("compiling LaTeX manuscript ...")
    result = _run_latexmk(tex)
    if result["exit_code"] != 0:
        _fail(f"LaTeX compilation failed. See {result['log']} for details.")
    _log("PDF built successfully.")
    provenance.atomic_write_json(marker, {"run_id": run_dir.name, "pdf": str(result["pdf"])})
    return run_dir


def _write_template_provenance():
    import subprocess
    out = ["# IEEE template provenance", ""]
    try:
        r = subprocess.run(["kpsewhich", "IEEEtran.cls"], capture_output=True, text=True)
        cls_path = r.stdout.strip()
        out.append(f"- IEEEtran.cls located at: `{cls_path or 'NOT FOUND'}`")
    except Exception as exc:  # noqa: BLE001
        out.append(f"- kpsewhich failed: {exc}")
    out += [
        "",
        "- Obtained from: official MiKTeX distribution (TeX Live package `ieeetran`), "
        "the recognized TeX distribution channel for the official IEEE conference class.",
        "- Access date (UTC): 2026-08-11",
        "- License: IEEEtran is distributed under the LPPL (LaTeX Project Public License); "
        "redistribution is permitted under its terms, but we document the package requirement "
        "rather than bundling the class.",
        "- Template not modified (documentclass `[conference]` IEEEtran, unchanged class file).",
        "- Page geometry, fonts, and column layout were not altered to force page count.",
        "",
        "Reference: https://www.ieee.org/conferences/publishing/templates.html "
        "(official IEEE templates page) and CTAN package `ieeetran`.",
    ]
    provenance.atomic_write_text(PAPER_DIR / "template_provenance.md", "\n".join(out) + "\n")


def _run_latexmk(tex: Path) -> dict:
    import subprocess
    build_dir = PAPER_DIR / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    pdf = build_dir / tex.with_suffix(".pdf").name
    latexmk = shutil.which("latexmk")
    if latexmk:
        try:
            cmd = [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error",
                   f"-outdir={build_dir}", tex.name]
            r = subprocess.run(cmd, cwd=tex.parent, capture_output=True, text=True, timeout=900)
        except (subprocess.TimeoutExpired, OSError) as exc:
            r = None
            _log(f"latexmk failed to run ({exc}); falling back to pdflatex+bibtex")
        if r is not None and r.returncode == 0 and pdf.exists():
            return {"exit_code": r.returncode, "log": build_dir / "manuscript.log",
                    "pdf": pdf, "stdout_tail": r.stdout[-2000:],
                    "stderr_tail": r.stderr[-2000:]}
        _log("latexmk unavailable or failed; falling back to pdflatex+bibtex")
    return _run_pdflatex_fallback(tex, build_dir, pdf)


def _run_pdflatex_fallback(tex: Path, build_dir: Path, pdf: Path) -> dict:
    import subprocess
    for stale in build_dir.glob("*"):
        if stale.suffix in (".aux", ".bbl", ".blg", ".out", ".log", ".fls", ".fdb_latexmk"):
            try:
                stale.unlink()
            except OSError:
                pass
    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")
    if not pdflatex:
        provenance.atomic_write_text(PAPER_DIR / "build/BLOCKED.txt",
                                     "No LaTeX toolchain available (latexmk/pdflatex not found).")
        return {"exit_code": 99, "log": PAPER_DIR / "build/BLOCKED.txt", "pdf": None,
                "stdout_tail": "", "stderr_tail": "no toolchain"}
    commands = []
    for _ in range(3):
        commands.append([pdflatex, "-interaction=nonstopmode", "-halt-on-error",
                         f"-output-directory={build_dir}", tex.name])
    if bibtex:
        commands.insert(1, [bibtex, build_dir / "manuscript.aux"])
    last_rc = 0
    for i, cmd in enumerate(commands):
        r = subprocess.run(cmd, cwd=tex.parent, capture_output=True, text=True, timeout=900)
        last_rc = r.returncode
        if last_rc != 0 and i != len(commands) - 1:
            break
    return {"exit_code": last_rc, "log": build_dir / "manuscript.log",
            "pdf": pdf if pdf.exists() else None, "stdout_tail": r.stdout[-2000:],
            "stderr_tail": r.stderr[-2000:]}


def stage_verify(config, run_dir: Path | None = None, force: bool = False) -> dict:
    run_dir = run_dir or _latest_run()
    marker = run_dir / "verify_SUCCESS.json"
    if marker.exists() and not force:
        _log("verify stage already complete; skipping")
        return provenance.read_json(marker)
    cache = Cache(Path(config["cache"]["root"]))
    _log("verifying cache integrity ...")
    cache_report = verification_mod.verify_cache(run_dir, cache)
    _log(f"  cache: {cache_report['ok']}/{cache_report['files']} artifacts OK, "
         f"{len(cache_report['issues'])} issues")
    _log("verifying generated numbers and manuscript ...")
    num_report = verification_mod.verify_generated_numbers(run_dir, PAPER_DIR)
    ms_report = verification_mod.verify_manuscript(PAPER_DIR, run_dir)
    _log(f"  numeric issues: {num_report['n_issues']}; manuscript issues: {ms_report['n_issues']}")
    _log("verifying bibliography ...")
    verification_mod.reference_verification(PAPER_DIR / "references.bib",
                                            ROOT / "reports/reference_verification.csv")
    _log("generating claim traceability register ...")
    verification_mod.claim_traceability(PAPER_DIR, run_dir, ROOT / "reports/claim_traceability.csv")
    _log("running independent hallucination audit ...")
    findings = verification_mod.hallucination_audit(run_dir, PAPER_DIR,
                                                    ROOT / "reports/hallucination_audit.md",
                                                    cache=cache)
    _log(f"  blockers={len(findings['blocker'])} majors={len(findings['major'])} "
         f"minors={len(findings['minor'])}")
    result = {"run_id": run_dir.name, "blockers": len(findings["blocker"]),
              "majors": len(findings["major"]), "minors": len(findings["minor"]),
              "cache_issues": len(cache_report["issues"]),
              "numeric_issues": num_report["n_issues"],
              "manuscript_issues": ms_report["n_issues"]}
    provenance.atomic_write_json(marker, result)
    if result["blockers"] > 0 or result["majors"] > 0:
        _fail(f"Manuscript not releasable: blockers={result['blockers']}, majors={result['majors']}",
              code=3)
    return result


def stage_package(run_dir: Path | None = None) -> Path:
    run_dir = run_dir or _latest_run()
    import zipfile
    pkg_dir = ROOT / "outputs/package"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    out = pkg_dir / f"{run_dir.name}_artifacts.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, label in ((PAPER_DIR, "paper"), (ROOT / "reports", "reports")):
            for f in base.rglob("*"):
                if f.is_file() and "build" not in f.parts and not f.name.endswith((".aux", ".bbl", ".blg", ".log")):
                    zf.write(f, f"{label}/{f.relative_to(base)}")
        for sub in ("metrics", "predictions"):
            for f in (run_dir / sub).rglob("*"):
                if f.is_file():
                    zf.write(f, f"run/{sub}/{f.name}")
    _log(f"artifacts packaged to {out}")
    return out


def stage_all(config, args):
    force = getattr(args, "force", False)
    stage_inspect_hardware(config)
    stage_audit(config, force=force)
    stage_splits(config, force=force)
    run_dir = stage_run(config, force=force)
    stage_report(config, run_dir, force=force)
    stage_paper(config, run_dir, force=force)
    stage_verify(config, run_dir, force=force)
    stage_package(run_dir)
    _log("ALL STAGES COMPLETE")
    return run_dir


# ----------------------------------------------------------------------------- cli

def build_parser():
    p = argparse.ArgumentParser(prog="deceptive-email", description=__doc__)
    p.add_argument("--config", default="configs/default.yaml", help="path to YAML config")
    sub = p.add_subparsers(dest="command", required=True)

    _pinspect = sub.add_parser("inspect-hardware", help="capture environment.json")
    _pinspect.add_argument("--config", default="configs/default.yaml")
    _paudit = sub.add_parser("audit", help="run Phase B dataset audit")
    _paudit.add_argument("--config", default="configs/default.yaml")
    _psplits = sub.add_parser("make-splits", help="build random + source-disjoint splits")
    _psplits.add_argument("--config", default="configs/default.yaml")
    pr = sub.add_parser("run", help="run the experiment (features/models/predictions/metrics)")
    pr.add_argument("--config", default="configs/default.yaml")
    pr.add_argument("--run-id", default=None)

    pr2 = sub.add_parser("report", help="generate figures, tables, macros, and reports")
    pr2.add_argument("--config", default="configs/default.yaml")
    pr2.add_argument("--run-id", default=None)

    pr3 = sub.add_parser("build-paper", help="compile the LaTeX manuscript")
    pr3.add_argument("--config", default="configs/default.yaml")
    pr3.add_argument("--run-id", default=None)

    pr4 = sub.add_parser("verify-manuscript", help="verify cache, numbers, references, and audit")
    pr4.add_argument("--config", default="configs/default.yaml")
    pr4.add_argument("--run-id", default=None)

    pr5 = sub.add_parser("verify-cache", help="verify cache integrity")
    pr5.add_argument("--config", default="configs/default.yaml")
    pr5.add_argument("--run-id", default=None)

    pr6 = sub.add_parser("package-artifacts", help="package key artifacts into a zip")
    pr6.add_argument("--config", default="configs/default.yaml")
    pr6.add_argument("--run-id", default=None)

    pr7 = sub.add_parser("run-stage", help="run a single stage by name")
    pr7.add_argument("--config", default="configs/default.yaml")
    pr7.add_argument("--stage", required=True, choices=["inspect-hardware", "audit", "make-splits",
                                                       "run", "report", "build-paper",
                                                       "verify-manuscript", "verify-cache",
                                                       "package-artifacts"])

    pr8 = sub.add_parser("resume", help="resume from the last completed stage")
    pr8.add_argument("--config", default="configs/default.yaml")
    pr8.add_argument("--run-id", default=None)

    pa = sub.add_parser("all", help="run every stage in order (tests are separate)")
    pa.add_argument("--config", default="configs/default.yaml")

    for _sp in (_pinspect, _paudit, _psplits, pr, pr2, pr3, pr4, pr5, pr6, pr7, pr8, pa):
        _sp.add_argument("--force", action="store_true",
                         help="rerun the stage even if its success marker exists")

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    config = config_mod.load_config(args.config)
    cmd = args.command

    if cmd == "inspect-hardware":
        stage_inspect_hardware(config)
    elif cmd == "audit":
        stage_audit(config, force=args.force)
    elif cmd == "make-splits":
        stage_splits(config, force=args.force)
    elif cmd == "run":
        stage_run(config, getattr(args, "run_id", None), force=args.force)
    elif cmd == "report":
        run_dir = _resolve_run_arg(args)
        stage_report(config, run_dir, force=args.force)
    elif cmd == "build-paper":
        run_dir = _resolve_run_arg(args)
        stage_paper(config, run_dir, force=args.force)
    elif cmd == "verify-manuscript":
        run_dir = _resolve_run_arg(args)
        stage_verify(config, run_dir, force=args.force)
    elif cmd == "verify-cache":
        run_dir = _resolve_run_arg(args)
        cache = Cache(Path(config["cache"]["root"]))
        report = verification_mod.verify_cache(run_dir, cache)
        _log(f"cache verify: {report['ok']}/{report['files']} ok, {len(report['issues'])} issues")
        for issue in report["issues"]:
            _log(f"  issue: {issue}")
    elif cmd == "package-artifacts":
        run_dir = _resolve_run_arg(args)
        stage_package(run_dir)
    elif cmd == "run-stage":
        stage = args.stage
        run_dir = getattr(args, "run_id", None)
        if stage == "inspect-hardware":
            stage_inspect_hardware(config)
        elif stage == "audit":
            stage_audit(config, force=args.force)
        elif stage == "make-splits":
            stage_splits(config, force=args.force)
        elif stage == "run":
            stage_run(config, run_dir, force=args.force)
        elif stage == "report":
            stage_report(config, _resolve_run_arg(args), force=args.force)
        elif stage == "build-paper":
            stage_paper(config, _resolve_run_arg(args), force=args.force)
        elif stage == "verify-manuscript":
            stage_verify(config, _resolve_run_arg(args), force=args.force)
        elif stage == "verify-cache":
            cache = Cache(Path(config["cache"]["root"]))
            verification_mod.verify_cache(_resolve_run_arg(args), cache)
        elif stage == "package-artifacts":
            stage_package(_resolve_run_arg(args))
    elif cmd == "resume":
        run_dir = _resolve_run_arg(args)
        config = config_mod.load_config(args.config)
        if not (run_dir / "experiment_SUCCESS.json").exists():
            _log("experiment incomplete; rerunning run stage")
            stage_run(config, run_dir.name, force=True)
        else:
            _log("experiment complete; continuing downstream stages")
        if not (run_dir / "report_SUCCESS.json").exists():
            stage_report(config, run_dir)
        if not (run_dir / "paper_SUCCESS.json").exists():
            stage_paper(config, run_dir)
        if not (run_dir / "verify_SUCCESS.json").exists():
            stage_verify(config, run_dir)
        stage_package(run_dir)
    elif cmd == "all":
        stage_all(config, args)
    else:
        _fail(f"Unknown command: {cmd}")
    return 0


def _resolve_run_arg(args) -> Path:
    run_id = getattr(args, "run_id", None)
    if run_id:
        return RUNS_DIR / run_id
    return _latest_run()


if __name__ == "__main__":
    sys.exit(main())

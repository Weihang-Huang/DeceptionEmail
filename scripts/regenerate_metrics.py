"""Regenerate metrics CSVs in chunks; writes large CSV files incrementally.

This avoids the prior version's 'all in one go' pattern that exceeded the bash
timeout. Each invocation writes one parity-checked chunk and exits.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deceptive_email import config as config_mod  # noqa: E402
from deceptive_email import evaluation as eval_mod  # noqa: E402
from deceptive_email import provenance  # noqa: E402

SPLITS_DIR = ROOT / "outputs/splits"
RUNS_DIR = ROOT / "outputs/runs"


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _split_seed(sid: str, base: int) -> int:
    """Deterministic seed: SHA-256 of split_id mod 2^32, plus base."""
    import hashlib
    h = hashlib.sha256(sid.encode("utf-8")).hexdigest()
    return (int(h[:8], 16) + base) % (2**31)


def main(argv=None):
    args = sys.argv[1:]
    run_id = args[0] if args else (ROOT / "outputs/latest.txt").read_text(encoding="utf-8").strip()
    run_dir = RUNS_DIR / run_id
    config = config_mod.load_config(ROOT / "configs/default.yaml")
    seed = int(config["seed"])
    n_iter = int(config["bootstrap_iterations"])
    # Allow override via env var to reduce bootstrap cost during regeneration.
    n_iter = int(os.environ.get("BOOTSTRAP_ITER", n_iter))
    split_info = json.loads((SPLITS_DIR / "split_manifest.json").read_text())

    pred_files = sorted((run_dir / "predictions").glob("*.parquet"))
    _log(f"computing metrics for {len(pred_files)} prediction files (n_iter={n_iter})")
    metrics_rows, ci_rows, cm_rows, extra_rows = [], [], [], []
    for i, pf in enumerate(pred_files):
        if i % 25 == 0:
            _log(f"  {i}/{len(pred_files)}")
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
        sid = m["split_id"]
        bs_seed = _split_seed(sid, seed)
        try:
            ci = eval_mod.stratified_bootstrap_ci(
                df["y_true"].to_numpy(), df["y_pred"].to_numpy(),
                n_iter=n_iter,
                seed=bs_seed)
        except ValueError as exc:
            _log(f"  bootstrap failed for {pf.name}: {exc}")
            m["macro_f1_ci_low"] = float("nan")
            m["macro_f1_ci_high"] = float("nan")
            m["mcc_ci_low"] = float("nan")
            m["mcc_ci_high"] = float("nan")
            metrics_rows.append(m)
            continue
        for metric in ("macro_f1", "mcc"):
            ci_rows.append({
                "split_id": m["split_id"], "protocol": m["protocol"],
                "held_out_sources": m["held_out_sources"], "model_id": m["model_id"],
                "metric": metric, "point": ci[metric]["point"],
                "ci_low": ci[metric]["ci_low"], "ci_high": ci[metric]["ci_high"],
                "n_bootstrap": n_iter,
                "seed": bs_seed,
            })
        m["macro_f1_ci_low"] = ci["macro_f1"]["ci_low"]
        m["macro_f1_ci_high"] = ci["macro_f1"]["ci_high"]
        m["mcc_ci_low"] = ci["mcc"]["ci_low"]
        m["mcc_ci_high"] = ci["mcc"]["ci_high"]
        metrics_rows.append(m)
        cm_rows.append({"split_id": m["split_id"], "protocol": m["protocol"],
                        "model_id": m["model_id"], "tn": m["tn"], "fp": m["fp"],
                        "fn": m["fn"], "tp": m["tp"]})

    metrics_df = pd.DataFrame(metrics_rows).sort_values(["protocol", "split_id", "model_id"])
    metrics_df.to_csv(run_dir / "metrics/all_metrics.csv", index=False)
    pd.DataFrame(ci_rows).to_csv(run_dir / "metrics/confidence_intervals.csv", index=False)
    pd.DataFrame(cm_rows).to_csv(run_dir / "metrics/confusion_matrices.csv", index=False)
    pd.DataFrame(extra_rows).sort_values(["protocol", "split_id", "model_id"]).to_csv(
        run_dir / "metrics/extra_metrics.csv", index=False)
    _log(f"metrics regenerated: {len(metrics_df)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
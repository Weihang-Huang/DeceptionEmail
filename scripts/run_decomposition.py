"""Run Phase C (decomposition) and Phase D (effect sizes) for a run."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deceptive_email import config as config_mod  # noqa: E402
from deceptive_email import data as data_mod  # noqa: E402
from deceptive_email import decomposition as dec_mod  # noqa: E402
from deceptive_email import effect_size as es_mod  # noqa: E402
from deceptive_email import provenance  # noqa: E402
from deceptive_email.cache import Cache  # noqa: E402

SPLITS_DIR = ROOT / "outputs/splits"
RUNS_DIR = ROOT / "outputs/runs"


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main(argv=None):
    run_id = (ROOT / "outputs/latest.txt").read_text(encoding="utf-8").strip()
    run_dir = RUNS_DIR / run_id
    config = config_mod.load_config(ROOT / "configs/default.yaml")
    cache = Cache(Path(config["cache"]["root"]))
    clean = data_mod.load_clean(config, ROOT / "data/processed/clean_deduplicated.parquet")
    if "simhash" not in clean.columns:
        sh = pd.read_parquet(ROOT / "outputs/audit/simhash_values.parquet")[["row_id", "simhash"]]
        clean = clean.merge(sh, on="row_id", how="left")
    code_hash = provenance.source_tree_hash(ROOT)
    dataset_hash = provenance.sha256_file(ROOT / "data/processed/clean_deduplicated.parquet")
    manifest = json.loads((SPLITS_DIR / "split_manifest.json").read_text())
    splits = []
    for s in manifest["splits"]:
        sid = s["split_id"]
        tr = pd.read_csv(SPLITS_DIR / f"{sid}_train.csv")
        te = pd.read_csv(SPLITS_DIR / f"{sid}_test.csv")
        s = dict(s)
        s["train_ids"] = tr["row_id"].astype(np.int64).to_numpy()
        s["test_ids"] = te["row_id"].astype(np.int64).to_numpy()
        splits.append(s)
    split_map = {s["split_id"]: s for s in splits}
    metrics = pd.read_csv(run_dir / "metrics/all_metrics.csv")
    split_ids = metrics["split_id"].unique()

    # ---- Phase C1: source predictability + divergence + coverage ----
    _log("computing source predictability, divergence, and coverage ...")
    dec_rows = []
    for sid in split_ids:
        if not sid.startswith("holdout_"):
            continue
        split = split_map[sid]
        try:
            sp = dec_mod.compute_source_predictability(split, clean, config, cache,
                                                       dataset_hash, code_hash)
        except Exception as exc:  # noqa: BLE001
            _log(f"  predictability failed {sid}: {exc}")
            sp = {"valid": False}
        try:
            div = dec_mod.compute_distribution_divergence(split, clean, config, cache,
                                                          dataset_hash, code_hash)
        except Exception as exc:  # noqa: BLE001
            _log(f"  divergence failed {sid}: {exc}")
            div = {}
        try:
            cov = dec_mod.compute_feature_coverage(split, clean, config, cache,
                                                   dataset_hash, code_hash)
        except Exception as exc:  # noqa: BLE001
            _log(f"  coverage failed {sid}: {exc}")
            cov = {}
        row = {"split_id": sid, "protocol": "source_disjoint"}
        row.update({k: sp.get(k) for k in ("valid", "cv_accuracy", "cv_accuracy_std",
                                            "cv_macro_f1", "chance_accuracy", "n_train",
                                            "n_sources", "reason")})
        row.update({k: div.get(k) for k in ("psi", "ks_statistic", "ks_p_value")})
        row.update({k: cov.get(k) for k in ("oov_share", "n_oov_tokens", "n_tokens_total")})
        dec_rows.append(row)
    dec_df = pd.DataFrame(dec_rows)
    dec_df.to_csv(run_dir / "metrics/distribution_divergence.csv", index=False)
    _log(f"  decomposition written: {len(dec_df)} rows")

    # ---- Phase C2: threshold recalibration ----
    _log("computing training-only threshold recalibration ...")
    cal_rows = []
    for sid in split_ids:
        if not sid.startswith("holdout_"):
            continue
        split = split_map[sid]
        for model_id in ("word_logistic_regression", "word_noanon_logistic_regression",
                         "structural_logistic_regression", "word_xgboost"):
            if model_id not in set(metrics[metrics["split_id"] == sid]["model_id"]):
                continue
            try:
                res = dec_mod.compute_threshold_recalibration(
                    split, clean, model_id, config, cache, dataset_hash, code_hash, run_dir)
            except Exception as exc:  # noqa: BLE001
                _log(f"  recalibration failed {sid}/{model_id}: {exc}")
                res = {"valid": False, "reason": str(exc)}
            res["split_id"] = sid
            res["model_id"] = model_id
            cal_rows.append(res)
    cal_df = pd.DataFrame(cal_rows)
    cal_df.to_csv(run_dir / "metrics/calibration_recalibration.csv", index=False)
    _log(f"  recalibration written: {len(cal_df)} rows")

    # ---- Phase D: effect sizes ----
    _log("computing paired effect sizes ...")
    gaps_df = es_mod.compute_all_protocol_gaps(metrics)
    gaps_df.to_csv(run_dir / "metrics/paired_delta.csv", index=False)
    _log(f"  paired delta written: {len(gaps_df)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
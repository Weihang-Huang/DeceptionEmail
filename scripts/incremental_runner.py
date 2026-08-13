"""Incremental runner: fits and predicts only for splits/models whose prediction
file is missing in the target run directory. Reuses the content-addressed cache
for vectorizers, matrices, and models. Idempotent on existing files."""
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
from deceptive_email import efficiency as eff_mod  # noqa: E402
from deceptive_email import evaluation as eval_mod  # noqa: E402
from deceptive_email import features as feat_mod  # noqa: E402
from deceptive_email import models as models_mod  # noqa: E402
from deceptive_email import provenance  # noqa: E402
from deceptive_email import splitting as split_mod  # noqa: E402
from deceptive_email.cache import Cache  # noqa: E402

SPLITS_DIR = ROOT / "outputs/splits"
RUNS_DIR = ROOT / "outputs/runs"


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


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


def main(argv=None):
    args = sys.argv[1:]
    run_id = args[0] if args else None
    if not run_id:
        latest = (ROOT / "outputs/latest.txt").read_text(encoding="utf-8").strip()
        run_id = latest
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        _log(f"run id {run_id} not found; aborting")
        return 1
    config = config_mod.load_config(ROOT / "configs/default.yaml")
    cache = Cache(Path(config["cache"]["root"]))
    clean = data_mod.load_clean(config, ROOT / "data/processed/clean_deduplicated.parquet")
    if "simhash" not in clean.columns:
        sh = pd.read_parquet(ROOT / "outputs/audit/simhash_values.parquet")[["row_id", "simhash"]]
        clean = clean.merge(sh, on="row_id", how="left")
    splits = _load_splits()
    code_hash = provenance.source_tree_hash(ROOT)
    dataset_hash = provenance.sha256_file(ROOT / "data/processed/clean_deduplicated.parquet")
    seed = int(config["seed"])
    hard_limit_gb = float(config["hardware"]["hard_process_memory_gb"])

    pred_dir = run_dir / "predictions"
    model_dir = run_dir / "models"
    pred_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    existing_preds = sorted(p.name for p in pred_dir.glob("*.parquet"))
    _log(f"existing predictions: {len(existing_preds)}")
    n_splits = len(splits)
    total = 0
    done = 0
    skip = 0
    fail = 0
    for si, split in enumerate(splits):
        for model_id in models_mod.MODEL_REGISTRY:
            total += 1
            key = f"{model_id}__{split['split_id']}.parquet"
            if key in existing_preds:
                skip += 1
                continue
            representation = models_mod.MODEL_REGISTRY[model_id]["representation"]
            try:
                _log(f"  [{si + 1}/{n_splits}] {split['split_id']} / {model_id}")
                bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                             dataset_hash, code_hash)
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
                peak_gb = mon.peak_gb_above_baseline()
                if mon.peak_gb > hard_limit_gb:
                    _log(f"  ! hard memory limit exceeded for {key} ({mon.peak_gb:.2f} GB)")
                    fail += 1
                    continue
                pred_df = eval_mod.build_predictions_frame(
                    split, model_id, representation, clean, test_ids_ordered, y_true,
                    preds["y_pred"], preds["decision"], preds["proba"], run_id)
                models_mod.save_predictions(pred_df, run_dir)
                done += 1
                _log(f"      fit={efficiency['fit_time_s']:.2f}s infer={efficiency['inference_time_s_median']*1000:.1f}ms "
                     f"peak={peak_gb:.2f}GB f1={eval_mod.compute_metrics(y_true, preds['y_pred'])['macro_f1']:.3f}")
            except Exception as exc:  # noqa: BLE001
                _log(f"  ! FAILED {split['split_id']}/{model_id}: {type(exc).__name__}: {exc}")
                fail += 1
    _log(f"DONE: total={total} done={done} skipped={skip} failed={fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
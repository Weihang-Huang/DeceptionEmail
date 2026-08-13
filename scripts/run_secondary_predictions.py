"""Train-and-predict on the secondary corpus using a model fitted on the
primary random split, then evaluate cross-corpus transfer.

Generates 6 prediction sets (one per model) and reports metrics.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deceptive_email import config as config_mod  # noqa: E402
from deceptive_email import efficiency as eff_mod  # noqa: E402
from deceptive_email import evaluation as eval_mod  # noqa: E402
from deceptive_email import features as feat_mod  # noqa: E402
from deceptive_email import models as models_mod  # noqa: E402
from deceptive_email import provenance  # noqa: E402
from deceptive_email.cache import Cache  # noqa: E402

PRIMARY_CLEAN = ROOT / "data/processed/clean_deduplicated.parquet"
SECONDARY_CLEAN = ROOT / "data/processed/secondary_clean.parquet"
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
    primary = pd.read_parquet(PRIMARY_CLEAN)
    secondary = pd.read_parquet(SECONDARY_CLEAN)
    code_hash = provenance.source_tree_hash(ROOT)
    dataset_hash = provenance.sha256_file(PRIMARY_CLEAN)
    seed = int(config["seed"])

    manifest = json.loads((SPLITS_DIR / "split_manifest.json").read_text())
    primary_split = next(s for s in manifest["splits"] if s["split_id"] == "random_seed42")
    primary_train_ids = pd.read_csv(SPLITS_DIR / "random_seed42_train.csv")["row_id"].astype(np.int64).to_numpy()
    primary_test_ids = pd.read_csv(SPLITS_DIR / "random_seed42_test.csv")["row_id"].astype(np.int64).to_numpy()
    primary_split["train_ids"] = primary_train_ids
    primary_split["test_ids"] = primary_test_ids
    pred_dir = run_dir / "predictions"
    out_dir = pred_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for model_id, mreg in models_mod.MODEL_REGISTRY.items():
        representation = mreg["representation"]
        key = f"{model_id}__secondary_test.parquet"
        _log(f"model {model_id} (representation {representation})")
        bm = feat_mod.build_matrices(representation, primary_split, primary, cache, config,
                                     dataset_hash, code_hash)
        M_train = cache.load_sparse("matrices", bm["M_train_key"])
        train_mask = primary["row_id"].isin(primary_train_ids)
        y_train = primary.loc[train_mask, "label"].to_numpy()
        # Now transform the secondary corpus with the *same* vectorizer.
        vec = cache.load_joblib("vectorizers", bm["vectorizer_key"])
        X_secondary = feat_mod.representation_inputs(secondary, representation)
        M_secondary = vec.transform(X_secondary)
        y_secondary = secondary["label"].to_numpy()
        efficiency = {}
        fit_out, preds = models_mod.fit_and_predict(
            model_id, config, M_train, M_secondary, y_train, cache,
            {"split_id": "secondary_test", "held_out_sources": [], "protocol": "random"},
            dataset_hash, code_hash, bm["vectorizer_key"], run_dir, efficiency)
        df_pred = eval_mod.build_predictions_frame(
            {"split_id": "secondary_test", "held_out_sources": [], "protocol": "random"},
            model_id, representation, secondary,
            secondary["row_id"].to_numpy(), y_secondary,
            preds["y_pred"], preds["decision"], preds["proba"], run_id)
        path = out_dir / key
        df_pred.to_parquet(path, index=False)
        m = eval_mod.compute_metrics(y_secondary, preds["y_pred"])
        ex = eval_mod.compute_extra_metrics(y_secondary, preds["y_pred"],
                                            proba=df_pred["positive_probability"].to_numpy(),
                                            decision=df_pred["decision_score"].to_numpy())
        m.update({"split_id": "secondary_test", "protocol": "secondary_test",
                  "model_id": model_id, "representation_id": representation,
                  "held_out_sources": "secondary"})
        m.update(ex)
        rows.append(m)
        _log(f"  f1={m['macro_f1']:.3f} mcc={m['mcc']:.3f} pos={m['precision_pos']:.3f}/{m['recall_pos']:.3f}")

    df = pd.DataFrame(rows)
    out = ROOT / "outputs/audit/secondary_corpus_metrics.csv"
    df.to_csv(out, index=False)
    _log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    import json
    sys.exit(main())
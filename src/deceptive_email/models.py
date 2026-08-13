"""Phase D: model definitions, fitting, prediction, and model caching."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import provenance
from .cache import Cache

MODEL_REGISTRY = {
    "word_logistic_regression": {
        "representation": "word",
        "label": "M1 word TF-IDF + logistic regression",
    },
    "character_linear_svm": {
        "representation": "character",
        "label": "M2 character TF-IDF + linear SVM",
    },
    "structural_logistic_regression": {
        "representation": "structural",
        "label": "M3 structural features + logistic regression",
    },
    "word_xgboost": {
        "representation": "word",
        "label": "M4 word TF-IDF + XGBoost (baseline)",
    },
    "word_noanon_logistic_regression": {
        "representation": "word_noanon",
        "label": "A1 word TF-IDF (tokens removed) + logistic regression",
    },
    "character_noanon_linear_svm": {
        "representation": "character_noanon",
        "label": "A2 character TF-IDF (tokens removed) + linear SVM",
    },
}


def build_classifier(model_id: str, config: dict):
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import LinearSVC
    mcfg = config["models"][model_id]
    if model_id in ("word_logistic_regression", "word_noanon_logistic_regression"):
        return LogisticRegression(C=mcfg["C"], class_weight=mcfg["class_weight"],
                                  solver=mcfg["solver"], max_iter=mcfg["max_iter"])
    if model_id in ("character_linear_svm", "character_noanon_linear_svm"):
        return LinearSVC(C=mcfg["C"], class_weight=mcfg["class_weight"], max_iter=2000)
    if model_id == "structural_logistic_regression":
        return LogisticRegression(C=mcfg["C"], class_weight=mcfg["class_weight"],
                                  solver=mcfg["solver"], max_iter=mcfg["max_iter"])
    if model_id == "word_xgboost":
        import xgboost as xgb
        return xgb.XGBClassifier(
            n_estimators=int(mcfg["n_estimators"]),
            max_depth=int(mcfg["max_depth"]),
            learning_rate=float(mcfg["learning_rate"]),
            subsample=float(mcfg["subsample"]),
            colsample_bytree=float(mcfg["colsample_bytree"]),
            min_child_weight=int(mcfg["min_child_weight"]),
            scale_pos_weight=None,
            tree_method=mcfg.get("tree_method", "hist"),
            n_jobs=int(mcfg.get("n_jobs", 4)),
            random_state=int(mcfg.get("random_state", 42)),
        )
    raise ValueError(f"Unknown model: {model_id}")


def model_has_probability(model_id: str) -> bool:
    return model_id not in ("character_linear_svm", "character_noanon_linear_svm")


def fit_and_predict(model_id: str, config: dict, M_train, M_test,
                    y_train, cache: Cache, split: dict,
                    dataset_hash: str, code_hash: str, vectorizer_key: str,
                    run_dir: Path, efficiency: dict) -> tuple[pd.DataFrame, dict]:
    """Fit classifier on train matrix, predict on test, cache model + predictions.

    efficiency dict is mutated with fit_time_s and inference_time_s_median.
    """
    import time
    from sklearn.pipeline import Pipeline

    run_dir = Path(run_dir)
    split_hash = provenance.json_hash(split)
    model_cfg_hash = provenance.json_hash(config["models"][model_id])
    base = {
        "dataset_hash": dataset_hash,
        "split_hash": split_hash,
        "model_config_hash": model_cfg_hash,
        "code_hash": code_hash,
        "vectorizer_key": vectorizer_key,
    }
    model_key = cache.key("models", model_id=model_id, **base)

    y_train = np.asarray(y_train)
    if cache.exists("models", model_key, ".joblib"):
        classifier = cache.load_joblib("models", model_key)
        efficiency["fit_time_s"] = float(cache.meta("models", model_key, ".joblib").get("fit_time_s", np.nan))
    else:
        classifier = build_classifier(model_id, config)
        t0 = time.perf_counter()
        classifier.fit(M_train, y_train)
        efficiency["fit_time_s"] = time.perf_counter() - t0
        cache.save_joblib("models", model_key, classifier,
                          meta={"model_id": model_id, "fit_on": "train_only",
                                "fit_time_s": efficiency["fit_time_s"], **base})

    # Timing: measure predict on test, repeated.
    reps = int(config["efficiency"]["repetitions"])
    batch = int(config["efficiency"]["inference_batch_size"])
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for start in range(0, M_test.shape[0], batch):
            Xb = M_test[start:start + batch]
            if hasattr(classifier, "decision_function"):
                classifier.decision_function(Xb)
            elif hasattr(classifier, "predict"):
                classifier.predict(Xb)
        times.append(time.perf_counter() - t0)
    efficiency["inference_time_s_median"] = float(np.median(times))
    efficiency["inference_time_s_per_1000"] = float(np.median(times) * 1000.0 / M_test.shape[0])

    # Predictions.
    y_pred = classifier.predict(M_test)
    if hasattr(classifier, "decision_function"):
        decision = classifier.decision_function(M_test)
    else:
        decision = None
    if hasattr(classifier, "predict_proba"):
        proba = classifier.predict_proba(M_test)[:, 1]
    else:
        proba = None

    # Copy the serialized model into the run dir (canonical location).
    src = cache.get_path("models", model_key, ".joblib")
    model_file = run_dir / "models" / f"{model_id}__{split['split_id']}.joblib"
    model_file.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(src, model_file)

    return {
        "model_key": model_key,
        "model_file": str(model_file),
        "serialized_size_mb": round(model_file.stat().st_size / (1024 ** 2), 3),
        "n_features": int(M_train.shape[1]),
    }, {"y_pred": y_pred, "decision": decision, "proba": proba}


def save_predictions(pred_df: pd.DataFrame, run_dir: Path) -> Path:
    pred_dir = Path(run_dir) / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    key = f"{pred_df['model_id'].iloc[0]}__{pred_df['split_id'].iloc[0]}"
    path = pred_dir / f"{key}.parquet"
    tmp = path.with_name(path.name + ".tmp")
    pred_df.to_parquet(tmp, index=False)
    tmp.replace(path)
    return path

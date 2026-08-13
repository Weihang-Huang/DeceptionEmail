"""Phase C: decomposition analyses.

1. Source predictability: how well can a classifier identify the source of a
   held-out email? Trained on the training partition only; evaluated on the
   source-disjoint test partition (3-way multinomial logistic regression).
2. Distribution divergence: PSI and two-sample KS between train and test
   TF-IDF row-sum distributions.
3. Feature coverage: OOV token share in the test set relative to the training
   vocabulary.
4. Training-only threshold recalibration: isotonic calibration fit on a
   training-only fold, applied to the test set; reports the macro-F1 at the
   recalibrated operating threshold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import confusion_matrix, f1_score

from . import features as feat_mod
from . import models as models_mod


def compute_source_predictability(split: dict, clean: pd.DataFrame,
                                  config: dict, cache, dataset_hash: str,
                                  code_hash: str) -> dict:
    """Measure how learnable the source label is within the training partition.

    Rationale: in a source-disjoint split the held-out source never appears in
    training, so a source classifier can never label it (its output space only
    covers training sources). Asking for test-set source accuracy is therefore
    degenerate by construction. The informative quantity is how much source
    signal the features carry: a 3-fold cross-validated multiclass source
    classifier trained on the training partition only. High CV accuracy means
    the features encode source, i.e. a random split could exploit source
    artefacts while a source-disjoint split cannot.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
    from sklearn.model_selection import StratifiedKFold

    if split.get("protocol", "random") == "random":
        return {"n_train": int(len(split.get("train_ids", []))), "valid": False}
    representation = "word"
    bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                 dataset_hash, code_hash)
    M_train = cache.load_sparse("matrices", bm["M_train_key"])
    train_mask = clean["row_id"].isin(split["train_ids"])
    y_train = clean.loc[train_mask, "source"].astype(str).to_numpy()
    classes = sorted(set(y_train))
    if len(classes) < 2:
        # Only one training source -> source is trivially non-learnable.
        return {"valid": False, "reason": "single training source",
                "n_train": int(len(y_train))}
    clf = LogisticRegression(C=1.0, max_iter=2000, solver="lbfgs")
    accs = []
    f1s = []
    try:
        skf = StratifiedKFold(n_splits=min(3, min(np.bincount(np.unique(y_train, return_inverse=True)[1]))),
                              shuffle=True, random_state=int(config["seed"]))
    except ValueError:
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=int(config["seed"]))
    for tr_idx, va_idx in skf.split(M_train, y_train):
        clf.fit(M_train[tr_idx], y_train[tr_idx])
        va = clf.predict(M_train[va_idx])
        accs.append(accuracy_score(y_train[va_idx], va))
        f1s.append(f1_score(y_train[va_idx], va, average="macro", zero_division=0))
    return {
        "valid": True,
        "n_train": int(len(y_train)),
        "n_sources": len(classes),
        "sources": classes,
        "cv_accuracy": float(np.mean(accs)),
        "cv_accuracy_std": float(np.std(accs)),
        "cv_macro_f1": float(np.mean(f1s)),
        "chance_accuracy": 1.0 / len(classes),
        "protocol_note": "within-training CV; test-source accuracy is degenerate "
                         "in source-disjoint evaluation because the held-out "
                         "source is absent from the training label space",
    }


def compute_distribution_divergence(split: dict, clean: pd.DataFrame,
                                    config: dict, cache, dataset_hash: str,
                                    code_hash: str) -> dict:
    """PSI and two-sample KS on train vs test TF-IDF row-sum distributions."""
    representation = "word"
    bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                 dataset_hash, code_hash)
    M_train = cache.load_sparse("matrices", bm["M_train_key"])
    M_test = cache.load_sparse("matrices", bm["M_test_key"])
    rs_train = np.asarray(M_train.sum(axis=1)).ravel()
    rs_test = np.asarray(M_test.sum(axis=1)).ravel()
    # PSI over 10 equal-frequency buckets defined on the combined distribution.
    all_vals = np.concatenate([rs_train, rs_test])
    edges = np.quantile(all_vals, np.linspace(0, 1, 11))
    edges[0] = -np.inf
    edges[-1] = np.inf
    def _buckets(vals):
        counts = np.histogram(vals, bins=edges)[0].astype(float)
        return counts / max(counts.sum(), 1e-9)
    p = _buckets(rs_train)
    q = _buckets(rs_test)
    p = np.clip(p, 1e-6, None)
    q = np.clip(q, 1e-6, None)
    psi = float(np.sum((p - q) * np.log(p / q)))
    ks = stats.ks_2samp(rs_train, rs_test)
    return {
        "psi": round(psi, 4),
        "ks_statistic": float(ks.statistic),
        "ks_p_value": float(ks.pvalue),
        "n_train": int(len(rs_train)),
        "n_test": int(len(rs_test)),
    }


def compute_feature_coverage(split: dict, clean: pd.DataFrame, config: dict,
                             cache, dataset_hash: str, code_hash: str) -> dict:
    """OOV token share in the test set relative to the training vocabulary."""
    representation = "word"
    bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                 dataset_hash, code_hash)
    vectorizer = cache.load_joblib("vectorizers", bm["vectorizer_key"])
    M_test = cache.load_sparse("matrices", bm["M_test_key"])
    # The vectorizer's vocabulary defines the training-side features. OOV tokens
    # are those present in the test text but absent from the vocabulary.
    vocab = set(vectorizer.vocabulary_.keys())
    test_texts = clean.loc[clean["row_id"].isin(split["test_ids"]), "combined_text"].astype(str)
    token_pattern = r"[a-z0-9']+"
    import re
    n_ov = 0
    n_all = 0
    for t in test_texts:
        toks = re.findall(token_pattern, t.lower())
        n_all += len(toks)
        n_ov += sum(1 for tok in toks if tok not in vocab)
    return {
        "n_oov_tokens": int(n_ov),
        "n_tokens_total": int(n_all),
        "oov_share": round(n_ov / max(n_all, 1), 5),
        "n_test": int(len(test_texts)),
    }


def compute_threshold_recalibration(split: dict, clean: pd.DataFrame,
                                    model_id: str, config: dict, cache,
                                    dataset_hash: str, code_hash: str,
                                    run_dir) -> dict:
    """Isotonic recalibration fit on a training-only fold.

    For a probabilistic model, fit an isotonic regressor on a 20% training
    holdout (from predict_proba on the training data), then apply it to the
    test set's probabilities and recompute macro-F1 at the operating threshold
    that maximises Youden's J on the recalibrated training fold. Reports the
    recalibrated macro-F1 and the delta versus the original.
    """
    from sklearn.isotonic import IsotonicRegression
    from pathlib import Path

    representation = models_mod.MODEL_REGISTRY[model_id]["representation"]
    bm = feat_mod.build_matrices(representation, split, clean, cache, config,
                                 dataset_hash, code_hash)
    M_train = cache.load_sparse("matrices", bm["M_train_key"])
    M_test = cache.load_sparse("matrices", bm["M_test_key"])
    train_mask = clean["row_id"].isin(split["train_ids"])
    test_mask = clean["row_id"].isin(split["test_ids"])
    y_train = clean.loc[train_mask, "label"].to_numpy()
    y_test = clean.loc[test_mask, "label"].to_numpy()

    model_file = Path(run_dir) / "models" / f"{model_id}__{split['split_id']}.joblib"
    if not model_file.exists():
        return {"valid": False, "reason": f"model file missing: {model_file.name}"}
    import joblib
    clf = joblib.load(model_file)
    if not hasattr(clf, "predict_proba"):
        return {"valid": False, "reason": "model has no predict_proba"}

    rng = np.random.default_rng(int(config["seed"]))
    cal_frac = float(config.get("decomposition", {}).get("calibration_fold_frac", 0.2))
    n_cal = int(len(y_train) * cal_frac)
    if n_cal < int(config.get("decomposition", {}).get("calibration_min_per_class", 30)):
        n_cal = max(n_cal, int(config.get("decomposition", {}).get("calibration_min_per_class", 30)))
    n_cal = min(n_cal, len(y_train))
    idx = rng.choice(len(y_train), size=n_cal, replace=False)
    mask = np.zeros(len(y_train), dtype=bool)
    mask[idx] = True
    proba_train = clf.predict_proba(M_train[mask])[:, 1]
    proba_test = clf.predict_proba(M_test)[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip")
    iso.fit(proba_train, y_train[mask])
    cal_proba_test = iso.predict(proba_test)
    # Choose threshold on the recalibrated training fold (Youden's J).
    proba_cal = clf.predict_proba(M_train[~mask])[:, 1]
    cal_cal = iso.predict(proba_cal)
    best_j = -np.inf
    best_thr = 0.5
    for thr in np.linspace(0.05, 0.95, 91):
        p = (cal_cal >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_train[~mask], p, labels=[0, 1]).ravel()
        tpr = tp / max(tp + fn, 1)
        fpr = fp / max(fp + tn, 1)
        j = tpr - fpr
        if j > best_j:
            best_j = j
            best_thr = float(thr)
    recal_pred = (cal_proba_test >= best_thr).astype(int)
    f1_orig = f1_score(y_test, (proba_test >= 0.5).astype(int), average="macro", zero_division=0)
    f1_recal = f1_score(y_test, recal_pred, average="macro", zero_division=0)
    return {
        "valid": True,
        "threshold": round(best_thr, 3),
        "f1_original_050": round(f1_orig, 4),
        "f1_recalibrated": round(f1_recal, 4),
        "delta_macro_f1": round(f1_recal - f1_orig, 4),
        "n_cal_train": int(mask.sum()),
        "n_recal_train": int((~mask).sum()),
    }

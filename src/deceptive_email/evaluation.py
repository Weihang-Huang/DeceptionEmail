"""Phase E: metrics, bootstrap confidence intervals, McNemar tests, error analysis."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             confusion_matrix, f1_score, matthews_corrcoef, precision_score,
                             recall_score, roc_auc_score)


def compute_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "n_test": int(len(y_true)),
        "n_pos": int((y_true == 1).sum()),
        "n_neg": int((y_true == 0).sum()),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "precision_pos": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "recall_pos": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }


def compute_extra_metrics(y_true, y_pred, proba=None, decision=None) -> dict:
    """Additional Phase-5 metrics: per-class precision/recall, FPR, PR-AUC,
    ROC-AUC, and Brier score.

    Ranking-based metrics (PR-AUC, ROC-AUC) use the positive-class probability
    when available, otherwise the decision score (higher = positive class) for
    non-probabilistic models. The Brier score requires true probabilities and is
    NaN for non-probabilistic models. AUC metrics are NaN when the test set has
    a single class (such a split is invalid by design, but we guard anyway).
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else float("nan")
    precision_neg = float(tn / (tn + fn)) if (tn + fn) > 0 else float("nan")
    recall_neg = float(tn / (tn + fp)) if (tn + fp) > 0 else float("nan")
    out = {"precision_neg": precision_neg, "recall_neg": recall_neg, "fpr": fpr}

    score = None
    proba_arr = np.asarray(proba, dtype=float) if proba is not None else None
    if proba_arr is not None and np.all(np.isfinite(proba_arr)):
        score = proba_arr
        out["brier"] = float(np.mean((y_true - score) ** 2))
    else:
        score = np.asarray(decision, dtype=float) if decision is not None else None
        out["brier"] = float("nan")

    if score is not None and len(np.unique(y_true)) == 2:
        try:
            out["pr_auc"] = float(average_precision_score(y_true, score))
            out["roc_auc"] = float(roc_auc_score(y_true, score))
        except ValueError:
            out["pr_auc"] = float("nan")
            out["roc_auc"] = float("nan")
    else:
        out["pr_auc"] = float("nan")
        out["roc_auc"] = float("nan")
    return out


def _safe_macro_f1(y, p):
    if set(y) != {0, 1} or set(p) != {0, 1}:
        return None
    return f1_score(y, p, average="macro")


def _safe_mcc(y, p):
    if set(y) != {0, 1} or set(p) != {0, 1}:
        return None
    return matthews_corrcoef(y, p)


def stratified_bootstrap_ci(y_true, y_pred, n_iter: int, seed: int) -> dict:
    """Stratified (within-class) bootstrap 95% CI for macro-F1 and MCC."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    rng = np.random.default_rng(seed)
    pos_idx = np.where(y_true == 1)[0]
    neg_idx = np.where(y_true == 0)[0]
    f1s, mccs = [], []
    for _ in range(n_iter):
        idx = np.concatenate([
            rng.choice(pos_idx, size=len(pos_idx), replace=True),
            rng.choice(neg_idx, size=len(neg_idx), replace=True),
        ])
        f1v = _safe_macro_f1(y_true[idx], y_pred[idx])
        mccv = _safe_mcc(y_true[idx], y_pred[idx])
        if f1v is not None and mccv is not None:
            f1s.append(f1v)
            mccs.append(mccv)
    f1s = np.asarray(f1s)
    mccs = np.asarray(mccs)
    if len(f1s) < 10:
        raise ValueError("Bootstrap produced too few valid replicates (single-class test set?).")
    return {
        "macro_f1": {"point": float(f1_score(y_true, y_pred, average="macro")),
                     "ci_low": float(np.percentile(f1s, 2.5)), "ci_high": float(np.percentile(f1s, 97.5))},
        "mcc": {"point": float(matthews_corrcoef(y_true, y_pred)),
                "ci_low": float(np.percentile(mccs, 2.5)), "ci_high": float(np.percentile(mccs, 97.5))},
        "n_valid_replicates": int(len(f1s)),
    }


def mcnemar_test(y_true, pred_a, pred_b) -> dict:
    y_true = np.asarray(y_true)
    a = np.asarray(pred_a)
    b = np.asarray(pred_b)
    both_wrong = int(((a != y_true) & (b != y_true)).sum())
    only_a_wrong = int(((a != y_true) & (b == y_true)).sum())
    only_b_wrong = int(((a == y_true) & (b != y_true)).sum())
    both_right = int(((a == y_true) & (b == y_true)).sum())
    table = np.array([[both_right, only_b_wrong], [only_a_wrong, both_wrong]])
    b_n, c_n = only_a_wrong, only_b_wrong
    if b_n + c_n == 0:
        p_value = 1.0
    else:
        chi2 = (abs(b_n - c_n) - 1) ** 2 / (b_n + c_n)
        p_value = float(stats.chi2.sf(chi2, 1))
    return {"both_wrong": both_wrong, "only_a_wrong": only_a_wrong,
            "only_b_wrong": only_b_wrong, "both_right": both_right,
            "statistic": chi2 if b_n + c_n else 0.0, "p_value": p_value}


def holm_correct(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni corrected p-values (monotone max form)."""
    n = len(p_values)
    order = np.argsort(np.asarray(p_values))
    corrected = np.zeros(n)
    prev = 0.0
    for rank, idx in enumerate(order, start=1):
        step = min(1.0, p_values[idx] * (n - rank + 1))
        corrected[idx] = max(prev, step)
        prev = corrected[idx]
    return corrected.tolist()


def build_predictions_frame(split: dict, model_id: str, representation: str,
                            clean: pd.DataFrame, test_ids, y_true, y_pred,
                            decision, proba, run_id: str) -> pd.DataFrame:
    sub = clean[clean["row_id"].isin(test_ids)].set_index("row_id")
    df = pd.DataFrame({
        "row_id": np.asarray(test_ids, dtype=np.int64),
        "split_id": split["split_id"],
        "protocol": split["protocol"],
        "held_out_sources": "|".join(split.get("held_out_sources", [])),
        "model_id": model_id,
        "representation_id": representation,
        "y_true": np.asarray(y_true, dtype=np.int64),
        "y_pred": np.asarray(y_pred, dtype=np.int64),
        "decision_score": np.asarray(decision, dtype=np.float64) if decision is not None else np.nan,
        "positive_probability": np.asarray(proba, dtype=np.float64) if proba is not None else np.nan,
        "source": sub["source"].astype(str).to_numpy(),
        "text_length": sub["combined_text"].astype(str).str.len().to_numpy(),
        "run_id": run_id,
    })
    df["correct"] = (df["y_true"] == df["y_pred"]).astype(int)
    return df


def error_analysis(clean: pd.DataFrame, pred_df: pd.DataFrame, split: dict,
                   model_id: str, max_per_class: int = 25) -> pd.DataFrame:
    sub = clean[clean["row_id"].isin(pred_df["row_id"])].set_index("row_id")
    rows = []
    for err_type, y_true in (("false_positive", 0), ("false_negative", 1)):
        mask = (pred_df["y_true"] == y_true) & (pred_df["y_pred"] != y_true)
        sample = pred_df[mask].head(max_per_class)
        for _, r in sample.iterrows():
            rid = int(r["row_id"])
            text = str(sub.at[rid, "combined_text"]) if rid in sub.index else ""
            rows.append({
                "split_id": split["split_id"],
                "model_id": model_id,
                "row_id": rid,
                "y_true": int(r["y_true"]),
                "y_pred": int(r["y_pred"]),
                "decision_score": float(r["decision_score"]) if pd.notna(r["decision_score"]) else None,
                "source": r["source"],
                "text_length": int(r["text_length"]),
                "anon_token_count": int(str(text).count("[")),
                "url_count": float(sub.at[rid, "url_count"]) if "url_count" in sub.columns else np.nan,
                "has_attachments": float(sub.at[rid, "has_attachments"]) if "has_attachments" in sub.columns else np.nan,
                "error_type": err_type,
                "text_preview_redacted": redact_text(str(text)[:300]),
            })
    return pd.DataFrame(rows)


def redact_text(text: str) -> str:
    import re
    t = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", "[REDACTED_EMAIL]", text)
    t = re.sub(r"https?://\S+", "[REDACTED_URL]", t)
    t = re.sub(r"(?<![A-Za-z0-9])[0-9]{6,}(?![A-Za-z0-9])", "[REDACTED_NUMBER]", t)
    return t

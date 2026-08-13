"""Tests for metrics, bootstrap CIs, McNemar, and Holm correction."""
import numpy as np
import pytest

from deceptive_email import evaluation as eval_mod


def test_compute_metrics_values():
    y = np.array([1, 1, 0, 0, 1])
    p = np.array([1, 0, 0, 0, 1])
    m = eval_mod.compute_metrics(y, p)
    assert m["tp"] == 2 and m["fp"] == 0 and m["fn"] == 1 and m["tn"] == 2
    assert abs(m["mcc"] - 0.666666667) < 1e-6
    assert m["accuracy"] == 4 / 5


def test_bootstrap_ci_range_and_determinism():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, size=400)
    p = y.copy()
    p[:50] = 1 - p[:50]
    ci1 = eval_mod.stratified_bootstrap_ci(y, p, n_iter=200, seed=1)
    ci2 = eval_mod.stratified_bootstrap_ci(y, p, n_iter=200, seed=1)
    assert ci1["macro_f1"]["point"] == ci2["macro_f1"]["point"]
    assert ci1["macro_f1"]["ci_low"] == ci2["macro_f1"]["ci_low"]
    assert ci1["macro_f1"]["ci_low"] <= ci1["macro_f1"]["ci_high"]
    assert ci1["n_valid_replicates"] == 200


def test_bootstrap_requires_both_classes_in_test():
    y = np.zeros(50, dtype=int)
    p = np.zeros(50, dtype=int)
    with pytest.raises(ValueError):
        eval_mod.stratified_bootstrap_ci(y, p, n_iter=100, seed=1)


def test_mcnemar_identical_models():
    y = np.array([0, 1, 0, 1, 1, 0])
    p = np.array([0, 1, 1, 0, 1, 0])
    res = eval_mod.mcnemar_test(y, p, p)
    assert res["only_a_wrong"] == 0 and res["only_b_wrong"] == 0
    assert res["p_value"] == 1.0


def test_mcnemar_perfect_agreement():
    y = np.array([0, 1, 0, 1])
    a = np.array([1, 0, 1, 1])
    b = np.array([1, 0, 1, 1])
    res = eval_mod.mcnemar_test(y, a, b)
    assert res["p_value"] == 1.0


def test_holm_correction():
    pvals = [0.01, 0.02, 0.9]
    corrected = eval_mod.holm_correct(pvals)
    assert corrected[0] == pytest.approx(0.03)   # 0.01*3
    assert corrected[1] == pytest.approx(0.04)   # max(0.03, 0.02*2)
    assert corrected[2] == pytest.approx(0.9)    # max(0.04, 0.9*1)


def test_extra_metrics_perfect():
    y = np.array([0, 0, 1, 1])
    p = np.array([0, 0, 1, 1])
    proba = np.array([0.1, 0.2, 0.9, 0.95])
    ex = eval_mod.compute_extra_metrics(y, p, proba=proba, decision=None)
    assert ex["fpr"] == 0.0
    assert ex["precision_neg"] == 1.0
    assert ex["recall_neg"] == 1.0
    assert ex["pr_auc"] == pytest.approx(1.0)
    assert ex["roc_auc"] == pytest.approx(1.0)
    assert ex["brier"] == pytest.approx(np.mean((y - proba) ** 2))


def test_extra_metrics_brier_nan_without_probability():
    y = np.array([0, 0, 1, 1])
    p = np.array([0, 1, 0, 1])
    ex = eval_mod.compute_extra_metrics(y, p, proba=None, decision=np.array([-1.0, -2.0, 1.0, 2.0]))
    assert np.isnan(ex["brier"])
    assert ex["fpr"] == pytest.approx(0.5)
    # The decision score perfectly separates the classes -> AUROC 1.0.
    assert ex["roc_auc"] == pytest.approx(1.0)


def test_extra_metrics_single_class_nan_auc():
    y = np.zeros(6, dtype=int)
    p = np.zeros(6, dtype=int)
    proba = np.full(6, 0.3)
    ex = eval_mod.compute_extra_metrics(y, p, proba=proba, decision=None)
    assert np.isnan(ex["pr_auc"]) and np.isnan(ex["roc_auc"])

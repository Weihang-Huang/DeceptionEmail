"""Tests for the noanon feature ablation and new model registry entries."""
import numpy as np
import pandas as pd
import pytest

from deceptive_email import features as feat_mod
from deceptive_email import models as models_mod


def _minimal_config():
    import yaml
    return yaml.safe_load(open("configs/default.yaml"))


def test_strip_anon_tokens():
    texts = ["click [URL] now [URL]", "free [EMAIL] [PHONE] here", "no tokens here"]
    out = feat_mod.strip_anon_tokens(texts)
    assert out == ["click  now ", "free   here", "no tokens here"]


def test_noanon_feature_config_flags():
    cfg = _minimal_config()
    assert feat_mod.feature_config("word_noanon", cfg)["strip_anon"] is True
    assert feat_mod.feature_config("character_noanon", cfg)["strip_anon"] is True
    assert feat_mod.feature_config("word", cfg)["strip_anon"] is False
    assert feat_mod.feature_config("character", cfg)["strip_anon"] is False


def test_registry_covers_new_models():
    cfg = _minimal_config()
    for model_id in ("word_xgboost", "word_noanon_logistic_regression",
                     "character_noanon_linear_svm"):
        assert model_id in models_mod.MODEL_REGISTRY
        assert model_id in cfg["models"], f"missing config block for {model_id}"


def test_build_and_fit_xgboost_small():
    cfg = _minimal_config()
    rng = np.random.default_rng(0)
    X = np.abs(rng.normal(size=(120, 30)))
    y = (X[:, 0] + X[:, 1] > 0.5).astype(int)
    clf = models_mod.build_classifier("word_xgboost", cfg)
    clf.fit(X, y)
    pred = clf.predict(X)
    assert pred.shape == (120,)
    assert set(np.unique(pred)) <= {0, 1}
    proba = clf.predict_proba(X)
    assert proba.shape == (120, 2)


def test_noanon_classifiers_fit():
    cfg = _minimal_config()
    rng = np.random.default_rng(1)
    X = np.abs(rng.normal(size=(80, 20)))
    y = (X[:, 0] > 0.6).astype(int)
    for model_id in ("word_noanon_logistic_regression", "character_noanon_linear_svm"):
        clf = models_mod.build_classifier(model_id, cfg)
        clf.fit(X, y)
        assert clf.predict(X).shape == (80,)
        assert not models_mod.model_has_probability(model_id) == (model_id == "character_noanon_linear_svm")


def test_representation_inputs_noanon():
    df = pd.DataFrame({"combined_text": ["see [URL] and [EMAIL] now", "plain text here"]})
    out = feat_mod.representation_inputs(df, "word_noanon")
    assert "URL" not in out[0]
    out2 = feat_mod.representation_inputs(df, "word")
    assert "[URL]" in out2[0]

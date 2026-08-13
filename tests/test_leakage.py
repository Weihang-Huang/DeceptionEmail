"""Leakage assertions: identity/source fields must never enter features."""
import pandas as pd

from deceptive_email import data as data_mod
from deceptive_email import splitting as split_mod


def test_features_do_not_contain_identity_fields():
    df = pd.DataFrame({
        "row_id": [0, 1, 2],
        "source": ["a", "b", "c"],
        "label": [0, 1, 0],
        "combined_text": ["x", "y", "z"],
        "url_count": [0, 1, 2],
        "has_attachments": [0, 1, 0],
        "content_types": ["text/plain", "text/html", "text/plain"],
        "language": ["en", "en", "en"],
    })
    feats = data_mod.compute_structural_features(df)
    forbidden = {"source", "label", "row_id", "original_index", "text_hash"}
    assert forbidden.isdisjoint(set(feats.columns))


def test_split_assertions_check_both_classes():
    df = pd.DataFrame({
        "row_id": [0, 1, 2, 3],
        "source": ["a", "a", "b", "b"],
        "label": [0, 0, 0, 0],
        "text_hash": ["x0", "x1", "x2", "x3"],
    })
    import pytest
    with pytest.raises(ValueError, match="both classes"):
        split_mod.assert_leakage(df, [0, 1], [2, 3])


def test_split_assertions_require_source_disjointness():
    df = pd.DataFrame({
        "row_id": [0, 1, 2, 3, 4, 5],
        "source": ["a", "a", "a", "b", "b", "b"],
        "label": [0, 1, 0, 1, 0, 1],
        "text_hash": ["x0", "x1", "x2", "x3", "x4", "x5"],
    })
    import pytest
    # Train includes source 'a' which is also held out.
    with pytest.raises(ValueError, match="held-out source"):
        split_mod.assert_leakage(df, [0, 1, 2], [3, 4, 5], held_out_sources=["a"])

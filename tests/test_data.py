"""Synthetic-fixture tests for data loading, cleaning, and deduplication."""
import hashlib

import numpy as np
import pandas as pd
import pytest

from deceptive_email import data as data_mod


def _make_df():
    return pd.DataFrame({
        "Source": ["trec5", "trec5", "nazario", "nazario", "nazario", "trec6"],
        "Label": [0, 0, 1, 1, 1, 1],
        "Subject": ["legit", "hi", "urgent", "update", "update", "tiny"],
        "Body": [
            "this is a legitimate message about the meeting tomorrow",
            "second legitimate note about the schedule",
            "please verify your account details immediately",
            "duplicate content appears here twice exactly",
            "duplicate content appears here twice exactly",
            "ok",
        ],
    })


def test_resolve_columns_case_insensitive():
    df = _make_df()
    mapping = data_mod.resolve_columns(df)
    assert mapping["source"] == "Source"
    assert mapping["label"] == "Label"
    assert mapping["subject"] == "Subject"
    assert mapping["body"] == "Body"


def test_build_combined_text():
    assert data_mod.build_combined_text("Subj", "Body") == "Subj\nBody"
    assert data_mod.build_combined_text(None, "Body") == "Body"
    assert data_mod.build_combined_text("Subj", None) == "Subj"
    assert data_mod.build_combined_text(None, None) == ""


def test_normalize_for_dedup():
    a = data_mod.normalize_for_dedup("Hello   World\r\n[URL]")
    b = data_mod.normalize_for_dedup("Hello World\n[URL]")
    assert a == b
    c = data_mod.normalize_for_dedup("ｆｏｏ")  # NFKC normalizes fullwidth
    assert c == "foo"


def test_clean_dataset_dedup_and_conflicts():
    df = _make_df()
    mapping = data_mod.resolve_columns(df)
    cleaned, report = data_mod.clean_dataset(df, mapping, {"min_text_chars": 5, "positive_label": 1})
    # rows: drop "short" (len 5 < min 5? boundary: >= 5 kept; use min 20 to drop it)
    cleaned, report = data_mod.clean_dataset(df, mapping, {"min_text_chars": 20, "positive_label": 1})
    # "d" subject+dup body appears twice with same label (1) -> deduped to one; "short" dropped.
    assert report["dropped_empty_short"] == 1
    assert report["kept_duplicates"] == 1
    assert len(cleaned) == 4
    assert set(cleaned["label"].unique()) == {0, 1}
    assert cleaned["text_hash"].is_unique


def test_clean_dataset_conflict_group_removed():
    df = pd.DataFrame({
        "Source": ["s1", "s1"],
        "Label": [0, 1],
        "Subject": ["x", "x"],
        "Body": ["identical text", "identical text"],
    })
    mapping = data_mod.resolve_columns(df)
    cleaned, report = data_mod.clean_dataset(df, mapping, {"min_text_chars": 1, "positive_label": 1})
    assert len(cleaned) == 0
    assert report["n_conflict_groups"] == 1
    assert report["dropped_conflict_groups"] == 2


def test_compute_structural_features_excludes_identity():
    df = pd.DataFrame({
        "row_id": [0, 1],
        "source": ["a", "b"],
        "label": [0, 1],
        "combined_text": ["hello [URL] 123", "world"],
        "url_count": [2, 0],
        "has_attachments": [0, 1],
        "content_types": ["text/plain", "text/html"],
        "language": ["en", "en"],
    })
    feats = data_mod.compute_structural_features(df)
    assert "source" not in feats.columns
    assert "label" not in feats.columns
    assert "row_id" not in feats.columns
    assert feats["anon_token_count"].iloc[0] == 1
    assert feats["digit_count"].iloc[0] == 3

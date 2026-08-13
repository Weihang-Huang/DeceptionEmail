"""Tests for the near-duplicate (SimHash) analysis module."""
import pandas as pd

from deceptive_email import near_duplicates as nd


def _make_clean_df(n=40):
    rows = []
    for i in range(n):
        src = "trec5" if i % 2 == 0 else "trec7"
        rows.append({"row_id": i, "source": src, "label": 1,
                     "combined_text": f"claim your prize now at example.com item {i}"})
    return pd.DataFrame(rows)


def _dup_df():
    rows = []
    rows.append({"row_id": 0, "source": "trec5", "label": 1,
                 "combined_text": "win big money today click here"})
    rows.append({"row_id": 1, "source": "trec7", "label": 1,
                 "combined_text": "win big money today click here"})
    rows.append({"row_id": 2, "source": "trec5", "label": 0,
                 "combined_text": "meeting agenda for tuesday afternoon"})
    return pd.DataFrame(rows)


def test_compute_simhash_consistent():
    df = _make_clean_df()
    sh = nd.compute_simhash(df)
    assert len(sh) == len(df)
    assert sh["simhash"].dtype == "uint64"
    assert set(sh["row_id"]) == set(df["row_id"])


def test_exact_duplicates_cross_source():
    df = _dup_df()
    sh = nd.compute_simhash(df)
    res = nd.analyze_exact_duplicates(df, sh)
    # Rows 0 and 1 are identical text -> identical simhash -> one cross-source group.
    assert res["counts"]["n_groups_ge2"] == 1
    assert res["counts"]["n_groups_cross_source"] == 1
    assert res["counts"]["n_rows_in_exact_dup_groups"] == 2
    assert res["groups"]["cross_source"].iloc[0]


def test_identical_text_is_hamming_zero():
    df = _dup_df()
    sh = nd.compute_simhash(df)
    near = nd.analyze_near_duplicates(df, sh, max_hamming=8)
    c = near["counts"]
    assert c["n_pairs_hamming_le_0"] >= 1
    assert c["n_pairs_cross_source_hamming_le_0"] >= 1
    assert c["n_rows_in_near_dup_pairs"] >= 2


def test_random_texts_no_identical_pairs():
    df = _make_clean_df(n=30)
    sh = nd.compute_simhash(df)
    res = nd.analyze_exact_duplicates(df, sh)
    # Distinct row_ids have distinct texts -> no exact dup groups expected.
    assert res["counts"]["n_groups_ge2"] == 0

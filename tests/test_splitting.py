"""Tests for random splitting, source-disjoint holdouts, and ranking."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from deceptive_email import splitting as split_mod


def _make_clean_df():
    rng = np.random.default_rng(0)
    rows = []
    sources = ["trec5", "trec6", "trec7", "nazario", "nigeria"]
    class_by_source = {
        "trec5": [0, 1], "trec6": [0, 1], "trec7": [0, 1],
        "nazario": [1], "nigeria": [1],
    }
    rid = 0
    for src in sources:
        labels = class_by_source[src]
        for i in range(1000):
            lab = labels[i % len(labels)]
            rows.append({"row_id": rid, "source": src, "label": lab,
                         "text_hash": f"h{rid:06d}", "combined_text": f"text {rid}"})
            rid += 1
    return pd.DataFrame(rows)


def test_random_split_stratified():
    df = _make_clean_df()
    tr, te = split_mod.random_split_ids(df, test_size=0.2, seed=42)
    assert set(tr).isdisjoint(set(te))
    tr_lab = df.set_index("row_id").loc[tr, "label"]
    te_lab = df.set_index("row_id").loc[te, "label"]
    assert set(tr_lab.unique()) == {0, 1}
    assert set(te_lab.unique()) == {0, 1}
    assert len(te) == int(len(df) * 0.2)


def test_holdout_validity():
    df = _make_clean_df()
    ok, reasons = split_mod.check_holdout_valid(df, {"trec5", "trec6", "trec7", "nigeria"},
                                                {"nazario"}, min_test_per_class=100)
    # nazario is single-class -> invalid
    assert not ok
    ok, reasons = split_mod.check_holdout_valid(df, {"trec7", "nazario", "nigeria"},
                                                {"trec5", "trec6"}, min_test_per_class=100)
    assert ok


def test_select_holdouts_returns_all_valid():
    df = _make_clean_df()
    config = {"min_test_per_class": 100}
    selected = split_mod.select_holdouts(df, config)
    assert len(selected) >= 1
    for c in selected:
        assert c["valid"]
    combos = [tuple(c["test_sources"]) for c in selected]
    assert len(set(combos)) == len(combos)


def test_holdout_id_descriptive():
    assert split_mod._holdout_id(["trec5"]) == "holdout_trec5"
    assert split_mod._holdout_id(["trec7", "trec5"]) == "holdout_trec5_trec7"


def test_random_split_exact_size():
    df = _make_clean_df()
    tr, te = split_mod.random_split_ids_exact_test_size(df, n_test=200, seed=7)
    assert len(te) == 200
    assert set(tr).isdisjoint(set(te))
    te_lab = df.set_index("row_id").loc[te, "label"]
    assert set(te_lab.unique()) == {0, 1}


def test_make_splits_writes_candidate_holdouts(tmp_path):
    df = _make_clean_df()
    config = {"min_test_per_class": 100, "seed": 42, "sensitivity_seeds": [7],
              "random_test_size": 0.2, "enable_equal_size_controls": True}
    clean_path = tmp_path / "clean.parquet"
    df.to_parquet(clean_path)
    manifest = split_mod.make_splits(config, df, tmp_path / "splits", clean_path)
    assert (tmp_path / "splits" / "candidate_holdouts.csv").exists()
    assert (tmp_path / "splits" / "split_manifest.json").exists()
    # random splits exist for each seed
    ids = [s["split_id"] for s in manifest["splits"]]
    assert "random_seed42" in ids and "random_seed7" in ids
    # each holdout has a matched equal-size control
    for h in manifest["source_holdouts"]:
        assert f"random_seed42_eq_{h['split_id']}" in ids


def test_assert_leakage_detects_overlap():
    df = _make_clean_df()
    tr = df["row_id"].to_numpy()[:500]
    te = df["row_id"].to_numpy()[400:900]  # overlapping
    with pytest.raises(ValueError, match="disjoint"):
        split_mod.assert_leakage(df, tr, te)


def _make_clean_df_with_clusters():
    """Synthetic dataset with a SimHash column for cluster tests."""
    rng = np.random.default_rng(0)
    rows = []
    sources = ["trec5", "trec6", "trec7"]
    rid = 0
    simhash = 1000
    for src in sources:
        for i in range(400):
            lab = i % 2
            # All three sources share cluster 1 (cross-source cluster) and have
            # one source-only cluster each.
            if i < 50:
                sh = 1
            elif i < 100:
                sh = {"trec5": 2, "trec6": 3, "trec7": 4}[src]
            else:
                sh = simhash
                simhash += 1
            rows.append({"row_id": rid, "source": src, "label": lab,
                         "text_hash": f"h{rid:06d}", "simhash": sh,
                         "combined_text": f"text {rid}"})
            rid += 1
    return pd.DataFrame(rows)


def test_full_match_control_matches_per_class_counts():
    df = _make_clean_df()
    n_train_per_class = {0: 600, 1: 600}
    n_test_per_class = {0: 200, 1: 200}
    tr, te = split_mod.random_split_ids_full_match(
        df, n_train_per_class, n_test_per_class, seed=42)
    assert len(tr) == 1200
    assert len(te) == 400
    train_lab = df.set_index("row_id").loc[tr, "label"]
    test_lab = df.set_index("row_id").loc[te, "label"]
    assert int((train_lab == 0).sum()) == 600
    assert int((train_lab == 1).sum()) == 600
    assert int((test_lab == 0).sum()) == 200
    assert int((test_lab == 1).sum()) == 200


def test_assert_cluster_disjoint_detects_shared_cluster():
    df = _make_clean_df_with_clusters()
    # Cluster 1 appears in train and test -> violation.
    tr = df["row_id"].to_numpy()[:60]
    te = df["row_id"].to_numpy()[20:80]
    with pytest.raises(ValueError, match="cluster-disjoint"):
        split_mod.assert_cluster_disjoint(df, tr, te, component_col="simhash")


def test_count_cross_split_pairs_counts_cross_source_pairs():
    df = _make_clean_df_with_clusters()
    # Cluster 1 contains 50 rows from each of trec5, trec6, trec7 (row_ids 0..49,
    # 400..449, 800..849). Put rows 0..40 (trec5 cluster-1) in train and 410..450
    # (trec6 cluster-1) in test.
    tr = df["row_id"].to_numpy()[0:40]
    te = df["row_id"].to_numpy()[410:450]
    counts = split_mod.count_cross_split_pairs(df, tr, te,
                                               component_col="simhash")
    assert counts["n_pairs"] > 0
    assert counts["n_pairs_cross_source"] > 0


def test_make_splits_emits_full_match_cluster_joint():
    df = _make_clean_df_with_clusters()
    config = {"min_test_per_class": 100, "seed": 42, "sensitivity_seeds": [7],
              "random_test_size": 0.2, "enable_equal_size_controls": True,
              "enable_full_match_controls": True,
              "enable_cluster_disjoint": True,
              "enable_joint_source_cluster_disjoint": True,
              "enable_pooled_cluster_disjoint": True}
    out_dir = Path(__file__).parent / "tmp_splits_phase_a1"
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_path = out_dir / "tmp_clean.parquet"
    df.to_parquet(clean_path)
    try:
        manifest = split_mod.make_splits(config, df, out_dir, clean_path)
    finally:
        import shutil
        shutil.rmtree(out_dir, ignore_errors=True)
    ids = [s["split_id"] for s in manifest["splits"]]
    assert any(i.startswith("random_seed42_fullmatch_") for i in ids)
    assert any(i.startswith("cluster_disjoint_holdout_") for i in ids)
    assert any(i.startswith("joint_source_cluster_disjoint_holdout_") for i in ids)
    assert any(i.startswith("random_cluster_disjoint_pooled_holdout_") for i in ids)


def test_pooled_cluster_disjoint_is_cluster_disjoint():
    df = _make_clean_df_with_clusters()
    tr, te = split_mod._make_pooled_cluster_disjoint_split(
        df, {0: 300, 1: 300}, {0: 100, 1: 100}, seed=42, component_col="simhash")
    assert len(tr) + len(te) == 800
    # No component may straddle the boundary.
    tr_sh = set(df.loc[df["row_id"].isin(tr), "simhash"])
    te_sh = set(df.loc[df["row_id"].isin(te), "simhash"])
    assert tr_sh.isdisjoint(te_sh)

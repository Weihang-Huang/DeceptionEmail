"""Phase C: split construction (random baseline and source-disjoint holdouts) with leakage assertions."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import provenance


def random_split_ids(clean: pd.DataFrame, test_size: float, seed: int) -> tuple[pd.Series, pd.Series]:
    """Stratified random train/test split on row_id."""
    from sklearn.model_selection import train_test_split
    train_ids, test_ids = train_test_split(
        clean["row_id"].to_numpy(),
        test_size=test_size,
        random_state=seed,
        stratify=clean["label"].to_numpy(),
    )
    return pd.Series(train_ids, name="row_id"), pd.Series(test_ids, name="row_id")


def random_split_ids_exact_test_size(clean: pd.DataFrame, n_test: int,
                                     seed: int) -> tuple[pd.Series, pd.Series]:
    """Stratified random split with an exact absolute number of test rows.

    Used for equal-size controls so that a random-split test partition has the
    same size as a matched source-disjoint holdout test partition.
    """
    from sklearn.model_selection import train_test_split
    n_test = int(n_test)
    if n_test <= 0 or n_test >= len(clean):
        raise ValueError(f"n_test must be in (0, {len(clean)}), got {n_test}")
    train_ids, test_ids = train_test_split(
        clean["row_id"].to_numpy(),
        test_size=n_test,
        random_state=seed,
        stratify=clean["label"].to_numpy(),
    )
    return pd.Series(train_ids, name="row_id"), pd.Series(test_ids, name="row_id")


def random_split_ids_full_match(clean: pd.DataFrame, n_train_per_class: dict,
                                n_test_per_class: dict,
                                seed: int) -> tuple[pd.Series, pd.Series]:
    """Stratified random split with explicit per-class train/test counts.

    Used for fully matched random controls: the train and test sets match the
    per-class sizes of a target source-disjoint holdout, drawn from the full
    corpus independently (not as the complement of the test sample). The seed
    is the same as the holdout's matched seed so that variance from the RNG is
    aligned across the matched pair.
    """
    rng = np.random.default_rng(int(seed))
    train_ids = []
    test_ids = []
    for cls in (0, 1):
        pool = clean.loc[clean["label"] == cls, "row_id"].to_numpy()
        if len(pool) < n_train_per_class[cls] + n_test_per_class[cls]:
            raise ValueError(
                f"Not enough class-{cls} rows ({len(pool)}) to draw "
                f"{n_train_per_class[cls]} train + {n_test_per_class[cls]} test")
        chosen_test = rng.choice(pool, size=n_test_per_class[cls], replace=False)
        remaining = np.setdiff1d(pool, chosen_test, assume_unique=False)
        chosen_train = rng.choice(remaining, size=n_train_per_class[cls], replace=False)
        train_ids.append(chosen_train)
        test_ids.append(chosen_test)
    train_ids = pd.Series(np.concatenate(train_ids), name="row_id")
    test_ids = pd.Series(np.concatenate(test_ids), name="row_id")
    return train_ids, test_ids


def _holdout_id(test_sources) -> str:
    """Descriptive split id like holdout_trec5 or holdout_trec5_trec6."""
    return "holdout_" + "_".join(sorted(test_sources))


def check_holdout_valid(clean: pd.DataFrame, train_sources, test_sources,
                        min_test_per_class: int) -> tuple[bool, list[str]]:
    reasons = []
    train = clean[clean["source"].isin(set(train_sources))]
    test = clean[clean["source"].isin(set(test_sources))]
    if len(train) == 0:
        reasons.append("empty training set")
    if len(test) == 0:
        reasons.append("empty test set")
    if len(reasons):
        return False, reasons
    for name, part in (("train", train), ("test", test)):
        counts = part["label"].value_counts()
        for cls in (0, 1):
            if cls not in counts.index:
                reasons.append(f"{name} lacks class {cls}")
            elif counts[cls] < min_test_per_class:
                reasons.append(f"{name} class {cls} has {counts[cls]} < {min_test_per_class}")
    if not reasons:
        return True, ["ok"]
    return False, reasons


def enumerate_holdout_candidates(clean: pd.DataFrame, min_test_per_class: int,
                                 max_holdout_size: int = 2) -> list[dict]:
    sources = sorted(clean["source"].astype(str).unique())
    candidates = []
    for size in range(1, max_holdout_size + 1):
        for combo in itertools.combinations(sources, size):
            test_sources = set(combo)
            train_sources = set(sources) - test_sources
            valid, reasons = check_holdout_valid(clean, train_sources, test_sources, min_test_per_class)
            test = clean[clean["source"].isin(test_sources)]
            posrate = float((test["label"] == 1).mean()) if len(test) else 0.0
            candidates.append({
                "test_sources": sorted(test_sources),
                "train_sources": sorted(train_sources),
                "holdout_size": size,
                "valid": valid,
                "reasons": reasons,
                "test_size": int(len(test)),
                "test_positive_rate": posrate,
                "test_n_pos": int((test["label"] == 1).sum()),
                "test_n_neg": int(len(test) - (test["label"] == 1).sum()),
                "rank": None,
                "selected": False,
            })
    return candidates


def rank_candidates(candidates: list[dict]) -> list[dict]:
    valid = [c for c in candidates if c["valid"]]
    valid.sort(key=lambda c: (
        abs(c["test_positive_rate"] - 0.5),
        -c["test_size"],
        tuple(c["test_sources"]),
    ))
    for i, c in enumerate(valid, start=1):
        c["rank"] = i
    return valid


def select_holdouts(clean: pd.DataFrame, config: dict) -> list[dict]:
    """Return ALL valid source-disjoint holdouts (ranked, no cap).

    Prefers size-1 and size-2 holdouts; falls back to size-3 only if no valid
    candidate exists at sizes 1-2. Raises if no valid candidate exists.
    """
    min_test = int(config.get("min_test_per_class", 100))
    candidates = enumerate_holdout_candidates(clean, min_test, max_holdout_size=2)
    ranked = rank_candidates(candidates)
    if len(ranked) < 2:
        # Fall back to including size-3 holdouts.
        candidates = enumerate_holdout_candidates(clean, min_test, max_holdout_size=3)
        ranked = rank_candidates(candidates)
    if not ranked:
        raise ValueError("No valid source-disjoint holdout could be constructed. "
                         "Write reports/BLOCKER.md and stop; do not substitute a random-only study.")
    for i, c in enumerate(ranked, start=1):
        c["selected"] = True
        c["selection_position"] = i
    return ranked


def assert_leakage(clean: pd.DataFrame, train_ids, test_ids,
                   held_out_sources=None) -> list[str]:
    """Run all leakage assertions; raise ValueError listing every violation."""
    problems = []
    train_mask = clean["row_id"].isin(train_ids)
    test_mask = clean["row_id"].isin(test_ids)
    train = clean[train_mask]
    test = clean[test_mask]

    if not set(train_ids).isdisjoint(set(test_ids)):
        problems.append("train/test row IDs are not disjoint")
    if len(set(train["text_hash"]) & set(test["text_hash"])):
        problems.append("normalized-text hashes appear in both train and test")
    if held_out_sources is not None:
        if set(train["source"]) & set(held_out_sources):
            problems.append("held-out source appears in training set")
        if not set(test["source"]).issubset(set(held_out_sources)):
            problems.append("test set contains sources outside the holdout set")
    for name, part in (("train", train), ("test", test)):
        if set(part["label"].unique()) != {0, 1}:
            problems.append(f"{name} does not contain both classes")
    if problems:
        raise ValueError("Leakage assertions failed:\n  " + "\n  ".join(problems))
    return problems


def assert_cluster_disjoint(clean: pd.DataFrame, train_ids, test_ids,
                            component_col: str = "simhash") -> None:
    """Assert that no SimHash component appears in both train and test.

    The component_col must already exist on `clean` and identify each row's
    cluster (exact-duplicate SimHash component for the strict rule). A row's
    cluster is the component value; rows sharing a value are in the same
    cluster.
    """
    if component_col not in clean.columns:
        raise ValueError(
            f"clean lacks cluster column '{component_col}'; run cluster audit first")
    train_mask = clean["row_id"].isin(train_ids)
    test_mask = clean["row_id"].isin(test_ids)
    train_clusters = set(clean.loc[train_mask, component_col].dropna().unique())
    test_clusters = set(clean.loc[test_mask, component_col].dropna().unique())
    common = train_clusters & test_clusters
    if common:
        raise ValueError(
            f"cluster-disjoint assertion failed: {len(common)} SimHash components "
            f"appear in both train and test")


def write_split_csv(ids: pd.Series, path: Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ids.to_csv(path, index=False)


def _random_seed_list(config: dict) -> list[int]:
    seeds = [int(config.get("seed", 42))]
    for s in config.get("sensitivity_seeds", []):
        s_int = int(s)
        if s_int not in seeds:
            seeds.append(s_int)
    return seeds


def _split_entry(clean: pd.DataFrame, split_id: str, protocol: str,
                 held_out_sources, train_ids, test_ids, seed: int | None) -> dict:
    train = clean[clean["row_id"].isin(train_ids)]
    test = clean[clean["row_id"].isin(test_ids)]
    return {
        "split_id": split_id,
        "protocol": protocol,
        "held_out_sources": sorted(held_out_sources) if held_out_sources else [],
        "seed": seed,
        "train_size": int(len(train)),
        "test_size": int(len(test)),
        "train_n_pos": int((train["label"] == 1).sum()),
        "test_n_pos": int((test["label"] == 1).sum()),
        "train_sources": sorted(train["source"].astype(str).unique()),
        "test_sources": sorted(test["source"].astype(str).unique()),
        "matched_holdout": split_id.rsplit("_eq_", 1)[-1] if "_eq_" in split_id else None,
    }


def count_cross_split_pairs(clean: pd.DataFrame, train_ids, test_ids,
                            component_col: str = "simhash") -> dict:
    """Count row pairs that share a cluster but straddle the train/test boundary.

    Returns a dict with `n_pairs`, `n_pairs_cross_source`, `n_pairs_within_source`,
    and `n_rows_involved` (the number of distinct rows that participate in at
    least one cross-split pair).
    """
    if component_col not in clean.columns:
        return {"n_pairs": 0, "n_pairs_cross_source": 0,
                "n_pairs_within_source": 0, "n_rows_involved": 0,
                "note": "no cluster column on clean; pair count is zero by definition"}
    train_set = set(int(x) for x in train_ids)
    test_set = set(int(x) for x in test_ids)
    work = clean[["row_id", "source", component_col]].copy()
    work["side"] = np.where(work["row_id"].isin(train_set), "train",
                            np.where(work["row_id"].isin(test_set), "test", "other"))
    straddling = work[work["side"] == "train"].merge(
        work[work["side"] == "test"],
        on=component_col, suffixes=("_a", "_b"))
    straddling = straddling[straddling["row_id_a"] < straddling["row_id_b"]]
    straddling["cross_source"] = straddling["source_a"] != straddling["source_b"]
    n_pairs = int(len(straddling))
    n_cross = int(straddling["cross_source"].sum())
    involved = set(straddling["row_id_a"]).union(set(straddling["row_id_b"]))
    return {"n_pairs": n_pairs,
            "n_pairs_cross_source": n_cross,
            "n_pairs_within_source": n_pairs - n_cross,
            "n_rows_involved": int(len(involved))}


def _make_cluster_disjoint_split(clean: pd.DataFrame, base_test_ids, base_train_ids,
                                 component_col: str,
                                 sources_train, sources_test) -> tuple[pd.Series, pd.Series]:
    """Build a cluster-disjoint split that respects a source rule.

    Each SimHash component is assigned to train or test as a unit. Components
    whose rows are all from `sources_train` go to train; components whose rows
    are all from `sources_test` go to test; mixed-source components are
    excluded from both partitions to preserve strict disjointness.
    """
    if component_col not in clean.columns:
        raise ValueError(
            f"clean lacks cluster column '{component_col}'")
    base_test = set(int(x) for x in base_test_ids)
    base_train = set(int(x) for x in base_train_ids)
    rows = clean[["row_id", "source", component_col]].copy()
    rows["in_base_test"] = rows["row_id"].isin(base_test)
    rows["in_base_train"] = rows["row_id"].isin(base_train)
    # Identify each component's sources.
    comp_sources = rows.groupby(component_col)["source"].apply(
        lambda s: frozenset(sorted(set(s))))
    eligible = rows.merge(comp_sources.rename("comp_sources"), on=component_col)
    only_train_src = eligible["comp_sources"].apply(
        lambda s: s.issubset(set(sources_train)))
    only_test_src = eligible["comp_sources"].apply(
        lambda s: s.issubset(set(sources_test)))
    train_row_ids = set(eligible.loc[only_train_src & eligible["in_base_train"], "row_id"].astype(int))
    test_row_ids = set(eligible.loc[only_test_src & eligible["in_base_test"], "row_id"].astype(int))
    train_ids = pd.Series(sorted(train_row_ids), name="row_id")
    test_ids = pd.Series(sorted(test_row_ids), name="row_id")
    return train_ids, test_ids


def _make_pooled_cluster_disjoint_split(clean: pd.DataFrame, n_train_per_class: dict,
                                        n_test_per_class: dict, seed: int,
                                        component_col: str = "simhash") -> tuple[pd.Series, pd.Series]:
    """Sources-pooled cluster-disjoint split: no source is held out, but every
    SimHash component is assigned to train or test as a unit.

    Start from a per-class stratified random draw with the exact train/test
    counts specified. Then enforce cluster-disjointness by reassigning any
    component that straddles the boundary to the side that contains the larger
    share of its members (ties broken randomly). The result is a split that
    isolates the contribution of template replication from source shift.
    """
    rng = np.random.default_rng(int(seed))
    train_ids, test_ids = random_split_ids_full_match(
        clean, n_train_per_class, n_test_per_class, seed)
    train_set = set(int(x) for x in train_ids)
    test_set = set(int(x) for x in test_ids)
    if component_col not in clean.columns:
        return train_ids, test_ids
    rid_to_sh = dict(zip(clean["row_id"].astype(int), clean[component_col]))
    comp_to_train = {}
    comp_to_test = {}
    for r in train_set:
        sh = rid_to_sh.get(r)
        if sh is None or pd.isna(sh):
            continue
        comp_to_train[sh] = comp_to_train.get(sh, 0) + 1
    for r in test_set:
        sh = rid_to_sh.get(r)
        if sh is None or pd.isna(sh):
            continue
        comp_to_test[sh] = comp_to_test.get(sh, 0) + 1
    all_comps = set(comp_to_train) | set(comp_to_test)
    for sh in all_comps:
        n_tr = comp_to_train.get(sh, 0)
        n_te = comp_to_test.get(sh, 0)
        if n_tr == 0 or n_te == 0:
            continue
        rows_in_comp = [int(r) for r in clean.loc[clean[component_col] == sh, "row_id"].astype(int)]
        if n_tr > n_te:
            for r in rows_in_comp:
                if r in test_set:
                    test_set.discard(r)
                    train_set.add(r)
        elif n_te > n_tr:
            for r in rows_in_comp:
                if r in train_set:
                    train_set.discard(r)
                    test_set.add(r)
        else:
            move_to_test = bool(rng.integers(0, 2))
            for r in rows_in_comp:
                if move_to_test:
                    if r in train_set:
                        train_set.discard(r)
                        test_set.add(r)
                else:
                    if r in test_set:
                        test_set.discard(r)
                        train_set.add(r)
    train_ids = pd.Series(sorted(train_set), name="row_id")
    test_ids = pd.Series(sorted(test_set), name="row_id")
    return train_ids, test_ids


def make_splits(config: dict, clean: pd.DataFrame, splits_dir, processed_path) -> dict:
    splits_dir = Path(splits_dir)
    processed_path = Path(processed_path)
    splits_dir.mkdir(parents=True, exist_ok=True)

    random_test_size = float(config.get("random_test_size", 0.20))
    enable_eqsize = bool(config.get("enable_equal_size_controls", True))
    enable_full_match = bool(config.get("enable_full_match_controls", True))
    enable_pooled_cd = bool(config.get("enable_pooled_cluster_disjoint", True))
    enable_cluster = bool(config.get("enable_cluster_disjoint", True))
    enable_joint = bool(config.get("enable_joint_source_cluster_disjoint", True))
    component_col = "simhash"
    if component_col not in clean.columns:
        simhash_path = splits_dir.parent / "audit" / "simhash_values.parquet"
        if simhash_path.exists():
            sh = pd.read_parquet(simhash_path)[["row_id", "simhash"]]
            clean = clean.merge(sh, on="row_id", how="left")
    has_clusters = component_col in clean.columns
    if enable_cluster and not has_clusters:
        enable_cluster = False
        enable_joint = False
    manifest = {"splits": [], "random": {}, "source_holdouts": [],
                "cluster_holdouts": [], "joint_holdouts": [],
                "matched_controls": [], "candidate_holdouts": [],
                "cluster_leakage": []}

    # Protocol 1: random baseline (one split per seed, including sensitivity seeds).
    for seed in _random_seed_list(config):
        split_id = f"random_seed{seed}"
        train_ids, test_ids = random_split_ids(clean, random_test_size, seed)
        assert_leakage(clean, train_ids, test_ids, held_out_sources=None)
        write_split_csv(train_ids, splits_dir / f"{split_id}_train.csv")
        write_split_csv(test_ids, splits_dir / f"{split_id}_test.csv")
        entry = _split_entry(clean, split_id, "random", [], train_ids, test_ids, seed)
        manifest["splits"].append(entry)
        if seed == int(config.get("seed", 42)):
            manifest["random"] = entry

    # Protocol 2: source-disjoint holdouts (all valid candidates).
    selected = select_holdouts(clean, config)
    all_candidates = enumerate_holdout_candidates(
        clean, int(config.get("min_test_per_class", 100)), max_holdout_size=3)
    ranked = rank_candidates(all_candidates)
    manifest["candidate_holdouts"] = ranked

    seed = int(config.get("seed", 42))
    for cand in selected:
        test_sources = cand["test_sources"]
        test_mask = clean["source"].isin(test_sources)
        test_ids = clean.loc[test_mask, "row_id"]
        train_ids = clean.loc[~test_mask, "row_id"]
        assert_leakage(clean, train_ids, test_ids, held_out_sources=test_sources)
        split_id = _holdout_id(test_sources)
        write_split_csv(train_ids, splits_dir / f"{split_id}_train.csv")
        write_split_csv(test_ids, splits_dir / f"{split_id}_test.csv")
        entry = _split_entry(clean, split_id, "source_disjoint", test_sources,
                             train_ids, test_ids, None)
        entry["test_positive_rate"] = cand["test_positive_rate"]
        entry["rank"] = cand["rank"]
        entry["reasons"] = cand["reasons"]
        manifest["splits"].append(entry)
        manifest["source_holdouts"].append(entry)

        # Equal-size control: stratified random split with the same test size.
        if enable_eqsize:
            eq_seed = seed
            eq_id = f"random_seed{eq_seed}_eq_{split_id}"
            eq_train, eq_test = random_split_ids_exact_test_size(
                clean, int(len(test_ids)), eq_seed)
            assert_leakage(clean, eq_train, eq_test, held_out_sources=None)
            write_split_csv(eq_train, splits_dir / f"{eq_id}_train.csv")
            write_split_csv(eq_test, splits_dir / f"{eq_id}_test.csv")
            eq_entry = _split_entry(clean, eq_id, "random", [], eq_train, eq_test, eq_seed)
            eq_entry["matched_holdout"] = split_id
            manifest["splits"].append(eq_entry)

        # Fully matched random control: per-class train and test counts match
        # the source-disjoint holdout's per-class counts (same random seed).
        if enable_full_match:
            train_part = clean.loc[~test_mask]
            test_part = clean.loc[test_mask]
            n_train_per_class = {int(c): int((train_part["label"] == c).sum())
                                 for c in (0, 1)}
            n_test_per_class = {int(c): int((test_part["label"] == c).sum())
                                for c in (0, 1)}
            fm_id = f"random_seed{seed}_fullmatch_{split_id}"
            fm_train, fm_test = random_split_ids_full_match(
                clean, n_train_per_class, n_test_per_class, seed)
            assert_leakage(clean, fm_train, fm_test, held_out_sources=None)
            write_split_csv(fm_train, splits_dir / f"{fm_id}_train.csv")
            write_split_csv(fm_test, splits_dir / f"{fm_id}_test.csv")
            fm_entry = _split_entry(clean, fm_id, "random", [],
                                    fm_train, fm_test, seed)
            fm_entry["matched_holdout"] = split_id
            fm_entry["matched_train_n_pos"] = n_train_per_class[1]
            fm_entry["matched_train_n_neg"] = n_train_per_class[0]
            fm_entry["matched_test_n_pos"] = n_test_per_class[1]
            fm_entry["matched_test_n_neg"] = n_test_per_class[0]
            manifest["splits"].append(fm_entry)
            manifest["matched_controls"].append(fm_entry)

        # Sources-pooled cluster-disjoint protocol: no source is held out, but
        # every SimHash component is assigned to train or test as a unit. This
        # isolates the contribution of template replication from source shift.
        if enable_pooled_cd and has_clusters:
            pcd_train, pcd_test = _make_pooled_cluster_disjoint_split(
                clean, n_train_per_class, n_test_per_class, seed,
                component_col=component_col)
            try:
                assert_cluster_disjoint(clean, pcd_train, pcd_test,
                                        component_col=component_col)
                assert_leakage(clean, pcd_train, pcd_test, held_out_sources=None)
                pcd_id = f"random_cluster_disjoint_pooled_{split_id}"
                write_split_csv(pcd_train, splits_dir / f"{pcd_id}_train.csv")
                write_split_csv(pcd_test, splits_dir / f"{pcd_id}_test.csv")
                pcd_entry = _split_entry(clean, pcd_id, "random_cluster_disjoint_pooled",
                                         [], pcd_train, pcd_test, seed)
                pcd_entry["matched_holdout"] = split_id
                manifest["splits"].append(pcd_entry)
                le_pcd = count_cross_split_pairs(clean, pcd_train, pcd_test,
                                                component_col=component_col)
                le_pcd["split_id"] = pcd_id
                le_pcd["protocol"] = "random_cluster_disjoint_pooled"
                manifest["cluster_leakage"].append(le_pcd)
            except ValueError:
                pass

        # Cluster-disjoint protocol.
        if enable_cluster:
            cd_train, cd_test = _make_cluster_disjoint_split(
                clean, test_ids, train_ids, component_col,
                sources_train=set(clean.loc[~test_mask, "source"].unique()),
                sources_test=set(test_sources))
            if len(cd_train) and len(cd_test):
                try:
                    assert_cluster_disjoint(clean, cd_train, cd_test,
                                            component_col=component_col)
                    assert_leakage(clean, cd_train, cd_test, held_out_sources=None)
                    cd_id = f"cluster_disjoint_{split_id}"
                    write_split_csv(cd_train, splits_dir / f"{cd_id}_train.csv")
                    write_split_csv(cd_test, splits_dir / f"{cd_id}_test.csv")
                    cd_entry = _split_entry(clean, cd_id, "cluster_disjoint", test_sources,
                                            cd_train, cd_test, None)
                    cd_entry["matched_holdout"] = split_id
                    manifest["splits"].append(cd_entry)
                    manifest["cluster_holdouts"].append(cd_entry)
                except ValueError as exc:
                    manifest["cluster_holdouts"].append({
                        "split_id": f"cluster_disjoint_{split_id}",
                        "valid": False,
                        "reasons": [str(exc)],
                        "matched_holdout": split_id,
                    })

        # Joint source-and-cluster-disjoint protocol.
        if enable_joint:
            joint_train, joint_test = _make_cluster_disjoint_split(
                clean, test_ids, train_ids, component_col,
                sources_train=set(clean.loc[~test_mask, "source"].unique()),
                sources_test=set(test_sources))
            if len(joint_train) and len(joint_test):
                try:
                    assert_cluster_disjoint(clean, joint_train, joint_test,
                                            component_col=component_col)
                    assert_leakage(clean, joint_train, joint_test,
                                   held_out_sources=test_sources)
                    jt_id = f"joint_source_cluster_disjoint_{split_id}"
                    write_split_csv(joint_train, splits_dir / f"{jt_id}_train.csv")
                    write_split_csv(joint_test, splits_dir / f"{jt_id}_test.csv")
                    jt_entry = _split_entry(clean, jt_id, "joint_source_cluster_disjoint",
                                            test_sources, joint_train, joint_test, None)
                    jt_entry["matched_holdout"] = split_id
                    manifest["splits"].append(jt_entry)
                    manifest["joint_holdouts"].append(jt_entry)
                except ValueError as exc:
                    manifest["joint_holdouts"].append({
                        "split_id": f"joint_source_cluster_disjoint_{split_id}",
                        "valid": False,
                        "reasons": [str(exc)],
                        "matched_holdout": split_id,
                    })

        # Cross-split leakage pair counts for every emitted split on this holdout.
        for sid, sids_train, sids_test in (
            (split_id, train_ids, test_ids),
        ):
            counts = count_cross_split_pairs(clean, sids_train, sids_test,
                                             component_col=component_col if has_clusters else "_none")
            counts["split_id"] = sid
            counts["protocol"] = "source_disjoint"
            manifest["cluster_leakage"].append(counts)
        if enable_cluster:
            for sid, sids_train, sids_test in [
                (f"cluster_disjoint_{split_id}", cd_train, cd_test)
            ] if 'cd_train' in locals() else []:
                counts = count_cross_split_pairs(clean, sids_train, sids_test,
                                                 component_col=component_col)
                counts["split_id"] = sid
                counts["protocol"] = "cluster_disjoint"
                manifest["cluster_leakage"].append(counts)
        if enable_joint:
            for sid, sids_train, sids_test in [
                (f"joint_source_cluster_disjoint_{split_id}", joint_train, joint_test)
            ] if 'joint_train' in locals() else []:
                counts = count_cross_split_pairs(clean, sids_train, sids_test,
                                                 component_col=component_col)
                counts["split_id"] = sid
                counts["protocol"] = "joint_source_cluster_disjoint"
                manifest["cluster_leakage"].append(counts)
        if enable_eqsize:
            for sid, sids_train, sids_test in [
                (f"random_seed{seed}_eq_{split_id}", eq_train, eq_test)
            ] if 'eq_train' in locals() else []:
                counts = count_cross_split_pairs(clean, sids_train, sids_test,
                                                 component_col=component_col)
                counts["split_id"] = sid
                counts["protocol"] = "random_eqsize"
                manifest["cluster_leakage"].append(counts)
        if enable_full_match:
            for sid, sids_train, sids_test in [
                (f"random_seed{seed}_fullmatch_{split_id}", fm_train, fm_test)
            ] if 'fm_train' in locals() else []:
                counts = count_cross_split_pairs(clean, sids_train, sids_test,
                                                 component_col=component_col)
                counts["split_id"] = sid
                counts["protocol"] = "random_fullmatch"
                manifest["cluster_leakage"].append(counts)

    manifest["split_manifest_hash"] = provenance.json_hash(manifest["splits"])
    manifest["clean_parquet_sha256"] = provenance.sha256_file(processed_path)

    provenance.atomic_write_json(splits_dir / "split_manifest.json", manifest)
    pd.DataFrame([
        {"split_id": s["split_id"], "protocol": s["protocol"],
         "held_out_sources": "|".join(s.get("held_out_sources", [])),
         "test_size": s["test_size"], "test_positive_rate": s.get("test_positive_rate", ""),
         "rank": s.get("rank", ""), "seed": s.get("seed", ""),
         "matched_holdout": s.get("matched_holdout", ""),
         "selected": s["split_id"].startswith("holdout_") or s["split_id"].startswith("random_seed")}
        for s in manifest["splits"]
    ]).to_csv(splits_dir / "splits_overview.csv", index=False)

    # candidate_holdouts.csv: every enumerated candidate with validity and rank.
    cand_rows = [{
        "test_sources": "|".join(c["test_sources"]),
        "train_sources": "|".join(c["train_sources"]),
        "holdout_size": c["holdout_size"],
        "valid": c["valid"],
        "reasons": "; ".join(c["reasons"]),
        "test_size": c["test_size"],
        "test_positive_rate": c["test_positive_rate"],
        "test_n_pos": c["test_n_pos"],
        "test_n_neg": c["test_n_neg"],
        "rank": c["rank"] if c["rank"] else "",
        "selected": c["selected"],
    } for c in all_candidates]
    pd.DataFrame(cand_rows).to_csv(splits_dir / "candidate_holdouts.csv", index=False)

    # cluster_leakage.csv: cross-split pair counts per emitted split.
    leak_rows = [{
        "split_id": c["split_id"],
        "protocol": c["protocol"],
        "n_pairs": c["n_pairs"],
        "n_pairs_cross_source": c["n_pairs_cross_source"],
        "n_pairs_within_source": c["n_pairs_within_source"],
        "n_rows_involved": c["n_rows_involved"],
    } for c in manifest["cluster_leakage"]]
    pd.DataFrame(leak_rows).to_csv(splits_dir / "cluster_leakage.csv", index=False)

    return manifest

"""Phase D: paired effect sizes.

For every model, compute the paired (per-holdout) delta between a protocol's
macro-F1 and the reference protocol (random_seed42), with a paired bootstrap
95% CI, Cohen's d on the delta distribution, and a Wilcoxon signed-rank p-value
across holdouts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def paired_delta_stats(gaps: np.ndarray, n_iter: int = 1000,
                       seed: int = 42) -> dict:
    """Bootstrap CI for the mean of paired deltas, plus Cohen's d."""
    gaps = np.asarray(gaps, dtype=float)
    gaps = gaps[np.isfinite(gaps)]
    rng = np.random.default_rng(seed)
    if len(gaps) == 0:
        return {"mean": np.nan, "median": np.nan, "min": np.nan, "max": np.nan,
                "ci_low": np.nan, "ci_high": np.nan, "cohen_d": np.nan,
                "wilcoxon_p": np.nan, "n": 0}
    means = np.empty(n_iter)
    for i in range(n_iter):
        sample = rng.choice(gaps, size=len(gaps), replace=True)
        means[i] = np.mean(sample)
    sd = gaps.std(ddof=1) if len(gaps) > 1 else np.nan
    cohen_d = np.mean(gaps) / sd if sd and np.isfinite(sd) and sd > 0 else np.nan
    try:
        stat, p = stats.wilcoxon(gaps, alternative="two-sided")
    except ValueError:
        p = np.nan
    return {
        "mean": float(np.mean(gaps)),
        "median": float(np.median(gaps)),
        "min": float(gaps.min()),
        "max": float(gaps.max()),
        "ci_low": float(np.percentile(means, 2.5)),
        "ci_high": float(np.percentile(means, 97.5)),
        "cohen_d": float(cohen_d) if np.isfinite(cohen_d) else np.nan,
        "wilcoxon_p": float(p) if np.isfinite(p) else np.nan,
        "n": int(len(gaps)),
    }


def compute_per_model_gaps(metrics: pd.DataFrame,
                           ref_protocol: str = "random",
                           ref_split: str = "random_seed42",
                           target_protocol: str = "source_disjoint") -> pd.DataFrame:
    """Per-model mean/median/range/worst gap vs the reference random split."""
    ref = metrics[(metrics["protocol"] == ref_protocol) &
                  (metrics["split_id"] == ref_split)]
    ref_map = dict(zip(ref["model_id"], ref["macro_f1"]))
    tgt = metrics[metrics["protocol"] == target_protocol]
    rows = []
    for model_id, f1_ref in ref_map.items():
        sub = tgt[tgt["model_id"] == model_id]
        if len(sub) == 0:
            continue
        gaps = f1_ref - sub["macro_f1"].to_numpy()
        stats_dict = paired_delta_stats(gaps)
        stats_dict.update({
            "model_id": model_id,
            "ref_macro_f1": float(f1_ref),
            "protocol": target_protocol,
        })
        rows.append(stats_dict)
    return pd.DataFrame(rows)


def compute_all_protocol_gaps(metrics: pd.DataFrame) -> pd.DataFrame:
    """Per-model gap stats for each protocol vs random_seed42 reference."""
    frames = []
    for protocol in ("source_disjoint", "cluster_disjoint", "joint_source_cluster_disjoint",
                     "random_cluster_disjoint_pooled"):
        frames.append(compute_per_model_gaps(
            metrics, ref_protocol="random", ref_split="random_seed42",
            target_protocol=protocol))
    return pd.concat(frames, ignore_index=True)

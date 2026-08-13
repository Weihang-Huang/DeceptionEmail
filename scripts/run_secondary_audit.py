"""Run the secondary corpus audit and overlap analysis."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deceptive_email import config as config_mod  # noqa: E402
from deceptive_email import secondary_corpus as sc_mod  # noqa: E402
from deceptive_email import provenance  # noqa: E402


def _log(msg: str):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def main(argv=None):
    args = sys.argv[1:]
    config = config_mod.load_config(ROOT / "configs/default.yaml")
    secondary_path = ROOT / "data/raw/phishing_email_dataset.json"
    primary_clean, _ = (
        pd.read_parquet(ROOT / "data/processed/clean_deduplicated.parquet"),
        None)
    audit_dir = ROOT / "outputs/audit"
    if not secondary_path.exists():
        _log(f"secondary corpus not found at {secondary_path}; aborting")
        return 1
    _log(f"loading secondary corpus from {secondary_path}")
    t0 = time.perf_counter()
    secondary_clean, report = sc_mod.load_secondary_corpus(secondary_path, config)
    _log(f"secondary cleaned: {report['n_clean']:,} rows ({report['n_pos']:,} positive, "
         f"{report['n_neg']:,} benign) in {time.perf_counter() - t0:.1f}s")
    out_path = ROOT / "data/processed/secondary_clean.parquet"
    secondary_clean.to_parquet(out_path, compression="gzip", index=False)
    _log(f"wrote {out_path}")
    overlap = sc_mod.compute_secondary_overlap(secondary_clean, primary_clean, audit_dir)
    _log(f"overlap: {overlap['n_exact_overlap_hashes']:,} exact hashes, "
         f"{overlap['n_simhash_overlap_hashes']:,} SimHash collisions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""Create a reproducibility manifest ZIP with SHA-256 checksums of the run's
canonical artifacts (predictions, metrics, models, splits, config, code hash).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deceptive_email import provenance  # noqa: E402
from deceptive_email import config as config_mod  # noqa: E402

RUNS_DIR = ROOT / "outputs/runs"
PKG_DIR = ROOT / "outputs/package"


def _sha256(path: Path) -> str:
    return provenance.sha256_file(path)


def main(argv=None):
    run_id = (ROOT / "outputs/latest.txt").read_text(encoding="utf-8").strip()
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists():
        print(f"run {run_id} not found")
        return 1
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    out = PKG_DIR / f"{run_id}_reproducibility_manifest.zip"
    manifest = {
        "run_id": run_id,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": {},
    }
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        # Predictions.
        for pf in sorted((run_dir / "predictions").glob("*.parquet")):
            rel = f"predictions/{pf.name}"
            manifest["files"][rel] = _sha256(pf)
            zf.write(pf, rel)
        # Metrics.
        for mf in sorted((run_dir / "metrics").glob("*.csv")):
            rel = f"metrics/{mf.name}"
            manifest["files"][rel] = _sha256(mf)
            zf.write(mf, rel)
        # Models (joblib).
        for mf in sorted((run_dir / "models").glob("*.joblib")):
            rel = f"models/{mf.name}"
            manifest["files"][rel] = _sha256(mf)
            zf.write(mf, rel)
        # Split manifests.
        splits_dir = ROOT / "outputs/splits"
        for sf in sorted(splits_dir.glob("*.csv")) + sorted(splits_dir.glob("*.json")):
            rel = f"splits/{sf.name}"
            manifest["files"][rel] = _sha256(sf)
            zf.write(sf, rel)
        # Config and code hash.
        cfg = ROOT / "configs/default.yaml"
        manifest["files"]["configs/default.yaml"] = _sha256(cfg)
        zf.write(cfg, "configs/default.yaml")
        manifest["code_hash"] = provenance.source_tree_hash(ROOT)
        manifest["config_hash"] = config_mod.config_hash(config_mod.load_config(cfg))
        # Manifest itself.
        manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
        zf.writestr("manifest.json", manifest_bytes)
    print(f"wrote {out} ({out.stat().st_size / 1024:.1f} KB, {len(manifest['files'])} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""Provenance: hashing, environment fingerprints, run identity, atomic IO."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import socket
import time
from pathlib import Path

import psutil

EXCLUDED_DIRS = {
    ".venv",
    "venv",
    ".git",
    "__pycache__",
    "data",
    "cache",
    "outputs",
    "reports",
    "paper",
    ".pytest_cache",
    ".egg-info",
    "build",
    "dist",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(data) -> str:
    return json.dumps(data, sort_keys=True, default=str, separators=(",", ":"))


def json_hash(data) -> str:
    return sha256_bytes(canonical_json(data).encode("utf-8"))


def source_tree_hash(root) -> str:
    """Hash all tracked source files under root (excluding heavy dirs)."""
    root = Path(root).resolve()
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.endswith(".egg-info")]
        for name in sorted(filenames):
            full = Path(dirpath) / name
            relpath = (rel / name).as_posix()
            try:
                entries.append((relpath, sha256_file(full)))
            except OSError:
                continue
    entries.sort()
    return json_hash({"entries": entries})


def environment_fingerprint() -> dict:
    """Collect package versions and hardware/software metadata for the environment.json record."""
    packages = ["pandas", "pyarrow", "numpy", "scipy", "scikit-learn", "joblib", "psutil",
                "PyYAML", "matplotlib", "seaborn", "pytest"]
    versions = {}
    for pkg in packages:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = None

    cpu_info = {}
    try:
        cpu_info = platform.processor() or platform.machine()
    except Exception:
        pass

    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "hostname": socket.gethostname(),
        "cpu": cpu_info,
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
        "disk_free_gb": round(shutil.disk_usage(Path.cwd()).free / (1024 ** 3), 2),
        "packages": versions,
    }


def check_disk_free(min_free_gb: float) -> bool:
    free = shutil.disk_usage(Path.cwd()).free / (1024 ** 3)
    return free >= min_free_gb


def make_run_id(dataset_hash: str, config_hash: str, code_hash: str,
                env_hash: str, split_hash: str) -> str:
    combined = json_hash({
        "dataset": dataset_hash,
        "config": config_hash,
        "code": code_hash,
        "env": env_hash,
        "splits": split_hash,
    })
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return f"{ts}_{combined[:8]}"


def atomic_write_text(path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)
    return path


def atomic_write_json(path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str, ensure_ascii=False)
    os.replace(tmp, path)
    return path


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

"""Content-addressed artifact cache with metadata and checksum verification."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import joblib

from . import provenance


class Cache:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def key(self, namespace: str, **inputs) -> str:
        data = {"namespace": namespace, **inputs}
        return provenance.json_hash(data)

    def _path(self, namespace: str, key: str, suffix: str) -> Path:
        return self.root / namespace / f"{key}{suffix}"

    def _meta_path(self, path: Path) -> Path:
        return path.with_name(path.name + ".meta.json")

    def exists(self, namespace: str, key: str, suffix: str) -> bool:
        path = self._path(namespace, key, suffix)
        if not path.exists():
            return False
        meta = self._meta_path(path)
        if not meta.exists():
            return False
        try:
            recorded = provenance.read_json(meta)["sha256"]
            return provenance.sha256_file(path) == recorded
        except Exception:
            return False

    def get_path(self, namespace: str, key: str, suffix: str) -> Path:
        if not self.exists(namespace, key, suffix):
            raise FileNotFoundError(f"Cache miss: {namespace}/{key}{suffix}")
        return self._path(namespace, key, suffix)

    def meta(self, namespace: str, key: str, suffix: str) -> dict:
        path = self.get_path(namespace, key, suffix)
        meta_path = self._meta_path(path)
        return provenance.read_json(meta_path) if meta_path.exists() else {}

    def save_bytes(self, namespace: str, key: str, suffix: str, data: bytes,
                   meta: dict | None = None) -> Path:
        path = self._path(namespace, key, suffix)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
        m = dict(meta or {})
        m["sha256"] = provenance.sha256_file(path)
        m["size_bytes"] = path.stat().st_size
        provenance.atomic_write_json(self._meta_path(path), m)
        return path

    def save_text(self, namespace: str, key: str, suffix: str, text: str,
                  meta: dict | None = None) -> Path:
        return self.save_bytes(namespace, key, suffix, text.encode("utf-8"), meta)

    def load_bytes(self, namespace: str, key: str, suffix: str) -> bytes:
        path = self.get_path(namespace, key, suffix)
        return path.read_bytes()

    def load_text(self, namespace: str, key: str, suffix: str) -> str:
        return self.load_bytes(namespace, key, suffix).decode("utf-8")

    def save_sparse(self, namespace: str, key: str, matrix, meta: dict | None = None) -> Path:
        import scipy.sparse
        path = self._path(namespace, key, ".npz")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp.npz")
        scipy.sparse.save_npz(tmp, matrix)
        os.replace(tmp, path)
        m = dict(meta or {})
        m["sha256"] = provenance.sha256_file(path)
        m["size_bytes"] = path.stat().st_size
        m["shape"] = [int(v) for v in matrix.shape]
        m["dtype"] = str(matrix.dtype)
        m["nnz"] = int(matrix.nnz)
        provenance.atomic_write_json(self._meta_path(path), m)
        return path

    def load_sparse(self, namespace: str, key: str):
        import scipy.sparse
        return scipy.sparse.load_npz(self.get_path(namespace, key, ".npz"))

    def save_joblib(self, namespace: str, key: str, obj, meta: dict | None = None) -> Path:
        path = self._path(namespace, key, ".joblib")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        joblib.dump(obj, tmp, compress=3)
        os.replace(tmp, path)
        m = dict(meta or {})
        m["sha256"] = provenance.sha256_file(path)
        m["size_bytes"] = path.stat().st_size
        provenance.atomic_write_json(self._meta_path(path), m)
        return path

    def load_joblib(self, namespace: str, key: str):
        if not self.exists(namespace, key, ".joblib"):
            raise FileNotFoundError(f"Cache miss: {namespace}/{key}.joblib")
        return joblib.load(self._path(namespace, key, ".joblib"))

    def write_success(self, stage: str, run_dir: Path, data: dict | None = None) -> Path:
        run_dir = Path(run_dir)
        marker = run_dir / "_SUCCESS.json"
        payload = {"stage": stage, "timestamp_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "data": data or {}}
        provenance.atomic_write_json(marker, payload)
        return marker

    def has_success(self, run_dir: Path, stage: str) -> bool:
        marker = Path(run_dir) / "_SUCCESS.json"
        if not marker.exists():
            return False
        try:
            return provenance.read_json(marker).get("stage") == stage
        except Exception:
            return False


def estimate_matrix_memory_gb(nnz: int) -> float:
    """Sparse CSR: ~12 bytes per nonzero (int32 index + float64 value) plus overhead."""
    return (nnz * 12) / (1024 ** 3)

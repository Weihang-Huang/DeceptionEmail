"""Tests for the content-addressed cache."""
import numpy as np
import pytest

from deceptive_email.cache import Cache, estimate_matrix_memory_gb


def test_cache_roundtrip_bytes(tmp_path):
    c = Cache(tmp_path / "cache")
    key = c.key("test", a=1, b="x")
    assert not c.exists("test", key, ".bin")
    c.save_bytes("test", key, ".bin", b"hello", meta={"k": 1})
    assert c.exists("test", key, ".bin")
    assert c.load_bytes("test", key, ".bin") == b"hello"
    assert c.meta("test", key, ".bin")["sha256"]


def test_cache_detects_tampering(tmp_path):
    c = Cache(tmp_path / "cache")
    key = c.key("test", a=2)
    path = c.save_bytes("test", key, ".bin", b"data", meta={})
    path.write_bytes(b"corrupted")
    assert not c.exists("test", key, ".bin")
    with pytest.raises(FileNotFoundError):
        c.load_bytes("test", key, ".bin")


def test_cache_sparse_roundtrip(tmp_path):
    import scipy.sparse as sp
    c = Cache(tmp_path / "cache")
    M = sp.csr_matrix(np.array([[1, 0], [0, 2], [3, 4]], dtype=np.float64))
    key = c.key("sparse", s="x")
    c.save_sparse("sparse", key, M)
    M2 = c.load_sparse("sparse", key)
    assert M2.nnz == M.nnz
    assert (M2.toarray() == M.toarray()).all()
    assert c.meta("sparse", key, ".npz")["shape"] == [3, 2]


def test_cache_joblib_roundtrip(tmp_path):
    c = Cache(tmp_path / "cache")
    key = c.key("j", v=1)
    c.save_joblib("j", key, {"a": [1, 2, 3]})
    assert c.load_joblib("j", key) == {"a": [1, 2, 3]}


def test_memory_estimate():
    assert estimate_matrix_memory_gb(100_000_000) > 0.9
    assert estimate_matrix_memory_gb(100_000_000) < 1.4

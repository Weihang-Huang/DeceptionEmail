"""Tests for provenance hashing, run identity, and atomic writes."""
import json

import pytest

from deceptive_email import provenance


def test_sha256_file(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")
    h1 = provenance.sha256_file(p)
    h2 = provenance.sha256_file(p)
    assert h1 == h2
    p.write_text("world", encoding="utf-8")
    assert provenance.sha256_file(p) != h1


def test_source_tree_hash_excludes_heavy_dirs(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "raw").mkdir()
    (tmp_path / "src" / "code.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "data" / "raw" / "big.parquet").write_text("B" * 1000, encoding="utf-8")
    h1 = provenance.source_tree_hash(tmp_path)
    (tmp_path / "data" / "raw" / "big2.parquet").write_text("C" * 1000, encoding="utf-8")
    h2 = provenance.source_tree_hash(tmp_path)
    assert h1 == h2  # heavy data dirs do not affect the source hash
    (tmp_path / "src" / "code2.py").write_text("y = 2", encoding="utf-8")
    h3 = provenance.source_tree_hash(tmp_path)
    assert h3 != h1


def test_make_run_id_deterministic():
    a = provenance.make_run_id("d1", "c1", "k1", "e1", "s1")
    b = provenance.make_run_id("d1", "c1", "k1", "e1", "s1")
    c = provenance.make_run_id("d2", "c1", "k1", "e1", "s1")
    assert a == b
    assert a != c
    assert a[8] == "T"
    assert a[-9] == "_"
    assert len(a) == 16 + 1 + 8  # UTC timestamp (16) + '_' + 8-char hash


def test_atomic_write(tmp_path):
    p = tmp_path / "out.json"
    provenance.atomic_write_json(p, {"a": 1, "b": [1, 2]})
    assert json.loads(p.read_text(encoding="utf-8")) == {"a": 1, "b": [1, 2]}
    assert not list(tmp_path.glob("*.tmp"))

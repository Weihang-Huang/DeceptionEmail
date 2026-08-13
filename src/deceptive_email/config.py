"""Configuration loading and hashing."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


def load_config(path) -> dict:
    """Load a YAML configuration file and return it as a dict."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict):
        raise ValueError(f"Configuration file {path} did not contain a mapping")
    return cfg


def config_hash(cfg: dict) -> str:
    """Return a stable SHA-256 hex digest of a configuration dict."""
    canonical = json.dumps(cfg, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def get(cfg: dict, dotted: str, default=None):
    """Fetch a nested value using a dotted key path."""
    node = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node

"""Phase D: feature vectorizers and sparse feature-matrix construction (training-only fitting)."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import config as config_mod
from . import data as data_mod
from . import provenance
from .cache import Cache

REPRESENTATIONS = ("word", "character", "structural", "word_noanon", "character_noanon")

STRUCTURAL_NUMERIC = ["url_count", "url_length_max", "url_length_avg", "url_subdom_max",
                      "url_subdom_avg", "attachment_count", "has_attachments"]
STRUCTURAL_DERIVED_NUMERIC = ["message_len", "punct_count", "digit_count", "anon_token_count"]
STRUCTURAL_CATEGORICAL = ["content_types", "language"]
STRUCTURAL_ALL_NUMERIC = STRUCTURAL_NUMERIC + STRUCTURAL_DERIVED_NUMERIC

ANON_TOKEN_RE = re.compile(r"\[[A-Z_]+\]")


def strip_anon_tokens(texts) -> list[str]:
    """Remove anonymization placeholders like [URL] for the noanon ablation."""
    return [ANON_TOKEN_RE.sub("", t) for t in texts]


def feature_config(representation: str, config: dict) -> dict:
    """Return the hashed configuration for a representation (used for cache keys)."""
    if representation in ("word", "word_noanon"):
        return {"representation": representation, "text": config["text"],
                "strip_anon": representation.endswith("_noanon")}
    if representation in ("character", "character_noanon"):
        return {"representation": representation, "text": config["text"],
                "strip_anon": representation.endswith("_noanon")}
    if representation == "structural":
        return {
            "representation": "structural",
            "numeric": STRUCTURAL_ALL_NUMERIC,
            "categorical": STRUCTURAL_CATEGORICAL,
        }
    raise ValueError(f"Unknown representation: {representation}")


def build_vectorizer(representation: str, config: dict):
    """Build an UNFITTED vectorizer/preprocessor. Must be fit on training data only."""
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.feature_extraction.text import TfidfVectorizer

    tcfg = config["text"]
    if representation in ("word", "word_noanon"):
        w = tcfg["word"]
        return TfidfVectorizer(
            ngram_range=tuple(w["ngram_range"]), min_df=w["min_df"], max_df=w["max_df"],
            max_features=w["max_features"], sublinear_tf=w["sublinear_tf"],
            lowercase=bool(tcfg["lowercase"]))
    if representation in ("character", "character_noanon"):
        c = tcfg["character"]
        return TfidfVectorizer(
            analyzer=c["analyzer"], ngram_range=tuple(c["ngram_range"]),
            min_df=c["min_df"], max_features=c["max_features"],
            sublinear_tf=c["sublinear_tf"], lowercase=bool(tcfg["lowercase"]))
    if representation == "structural":
        num = Pipeline([("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler())])
        cat = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True))])
        return ColumnTransformer([
            ("num", num, STRUCTURAL_ALL_NUMERIC),
            ("cat", cat, STRUCTURAL_CATEGORICAL),
        ])
    raise ValueError(f"Unknown representation: {representation}")


def representation_inputs(clean: pd.DataFrame, representation: str) -> object:
    """Return the input object expected by the vectorizer for a representation."""
    if representation in ("word", "character"):
        return clean["combined_text"].astype(str).to_numpy()
    if representation in ("word_noanon", "character_noanon"):
        return strip_anon_tokens(clean["combined_text"].astype(str).tolist())
    if representation == "structural":
        return data_mod.compute_structural_features(clean)
    raise ValueError(f"Unknown representation: {representation}")


def estimate_feature_matrix_memory(vectorizer, X_sample, sample_frac: float,
                                   budget_gb: float) -> tuple[float, bool]:
    """Fit vectorizer on a sample, extrapolate full-matrix memory, compare to budget."""
    import time
    from .cache import estimate_matrix_memory_gb
    X_fit = vectorizer.fit(X_sample)
    if hasattr(X_fit, "transform"):
        M = X_fit.transform(X_sample)
    else:
        M = X_sample
    nnz_sample = int(M.nnz) if hasattr(M, "nnz") else int(M.shape[0] * M.shape[1])
    est_nnz = nnz_sample / max(sample_frac, 1e-6)
    est_gb = estimate_matrix_memory_gb(est_nnz)
    return est_gb, est_gb <= budget_gb


def build_matrices(representation: str, split: dict, clean: pd.DataFrame,
                   cache: Cache, config: dict,
                   dataset_hash: str, code_hash: str) -> dict:
    """Fit vectorizer on train, transform train and test, cache matrices.

    Returns dict with matrix keys, feature count, and vectorizer key.
    """
    fcfg = feature_config(representation, config)
    split_hash = provenance.json_hash(split)
    train_mask = clean["row_id"].isin(split["train_ids"])
    test_mask = clean["row_id"].isin(split["test_ids"])
    train = clean[train_mask]
    test = clean[test_mask]

    base = {
        "dataset_hash": dataset_hash,
        "split_hash": split_hash,
        "feature_config_hash": provenance.json_hash(fcfg),
        "code_hash": code_hash,
    }

    # Vectorizer (fit on training data only).
    vec_key = cache.key("vectorizers", kind=representation, **base)
    if cache.exists("vectorizers", vec_key, ".joblib"):
        vectorizer = cache.load_joblib("vectorizers", vec_key)
    else:
        vectorizer = build_vectorizer(representation, config)
        budget_gb = float(config["hardware"]["target_process_memory_gb"])
        X_train_full = representation_inputs(train, representation)
        sample_frac = 0.1
        n_sample = max(500, int(len(train) * sample_frac))
        if hasattr(X_train_full, "iloc"):
            X_sample = X_train_full.iloc[:n_sample]
        elif hasattr(X_train_full, "__len__"):
            X_sample = X_train_full[:n_sample]
        else:
            X_sample = X_train_full
        est_gb, ok = estimate_feature_matrix_memory(vectorizer, X_sample,
                                                    sample_frac=n_sample / max(len(train), 1),
                                                    budget_gb=budget_gb)
        if not ok:
            raise MemoryError(
                f"Estimated feature matrix memory {est_gb:.2f} GB exceeds budget {budget_gb:.2f} GB "
                f"for representation '{representation}'. Reduce text max_features once and rerun.")
        vectorizer.fit(X_train_full)
        cache.save_joblib("vectorizers", vec_key, vectorizer,
                          meta={"representation": representation, "fit_on": "train_only",
                                **base})

    # Matrices.
    X_train = representation_inputs(train, representation)
    X_test = representation_inputs(test, representation)
    M_train_key = cache.key("matrices", kind="train", representation=representation, **base)
    M_test_key = cache.key("matrices", kind="test", representation=representation, **base)
    if not cache.exists("matrices", M_train_key, ".npz"):
        M_train = vectorizer.transform(X_train)
        cache.save_sparse("matrices", M_train_key, M_train, meta={**base, "split": split["split_id"]})
    else:
        M_train = cache.load_sparse("matrices", M_train_key)
    if not cache.exists("matrices", M_test_key, ".npz"):
        M_test = vectorizer.transform(X_test)
        cache.save_sparse("matrices", M_test_key, M_test, meta={**base, "split": split["split_id"]})
    else:
        M_test = cache.load_sparse("matrices", M_test_key)

    train_ids_key = cache.key("matrices", kind="train_ids", representation=representation, **base)
    test_ids_key = cache.key("matrices", kind="test_ids", representation=representation, **base)
    if not cache.exists("matrices", train_ids_key, ".npy"):
        cache.save_bytes("matrices", train_ids_key, ".npy",
                         np.asarray(split["train_ids"]).astype(np.int64).tobytes(), meta=base)
    if not cache.exists("matrices", test_ids_key, ".npy"):
        cache.save_bytes("matrices", test_ids_key, ".npy",
                         np.asarray(split["test_ids"]).astype(np.int64).tobytes(), meta=base)

    return {
        "representation": representation,
        "vectorizer_key": vec_key,
        "M_train_key": M_train_key,
        "M_test_key": M_test_key,
        "train_ids_key": train_ids_key,
        "test_ids_key": test_ids_key,
        "n_features": int(M_train.shape[1]),
        "n_train": int(M_train.shape[0]),
        "n_test": int(M_test.shape[0]),
        "nnz_train": int(M_train.nnz),
        "nnz_test": int(M_test.nnz),
    }

"""Dataset loading, column resolution, text construction, cleaning, and deduplication."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from . import provenance

ANON_TOKEN_PATTERN = re.compile(r"\[[A-Z_]+\]")

# Candidate column names, resolved case-insensitively.
COLUMN_CANDIDATES = {
    "source": ["source", "corpus", "dataset", "src", "source_name"],
    "label": ["label", "target", "class", "is_phishing", "phishing", "binary_label"],
    "subject": ["subject"],
    "body": ["body", "message", "content", "text", "email_body", "body_text"],
    "sender": ["sender"],
    "sender_domain": ["sender_domain"],
    "receiver": ["receiver"],
    "receiver_domain": ["receiver_domain"],
    "date": ["date", "sent_date", "timestamp", "datetime"],
    "content_types": ["content_types", "content_type", "mime_types"],
    "url_count": ["url_count", "num_urls", "number_of_urls", "n_urls"],
    "url_length_max": ["url_length_max", "max_url_length"],
    "url_length_avg": ["url_length_avg", "avg_url_length"],
    "url_subdom_max": ["url_subdom_max", "max_subdomains"],
    "url_subdom_avg": ["url_subdom_avg", "avg_subdomains"],
    "attachment_count": ["attachment_count", "num_attachments", "n_attachments"],
    "has_attachments": ["has_attachments", "attachments", "attachment_flag"],
    "attachment_types": ["attachment_types"],
    "language": ["language", "lang", "detected_language"],
    "urls": ["urls", "url_list"],
}


def _find_column(df: pd.DataFrame, candidates):
    lowered = {str(c).lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lowered:
            return lowered[cand]
    return None


def resolve_columns(df: pd.DataFrame) -> dict:
    """Resolve required and optional column names case-insensitively."""
    mapping = {}
    for key, candidates in COLUMN_CANDIDATES.items():
        mapping[key] = _find_column(df, candidates)
    return mapping


def build_combined_text(subject, body) -> str:
    parts = []
    if subject is not None and str(subject).strip():
        parts.append(str(subject))
    if body is not None and str(body).strip():
        parts.append(str(body))
    return "\n".join(parts)


def normalize_for_dedup(text) -> str:
    """Normalize Unicode form, line endings, and repeated whitespace for duplicate detection."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    t = unicodedata.normalize("NFKC", text)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    return t


def load_raw(config: dict, raw_path) -> pd.DataFrame:
    raw_path = Path(raw_path)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}. "
                                "See data/README.md for placement and checksum instructions.")
    if raw_path.suffix == ".csv":
        df = pd.read_csv(raw_path, low_memory=False)
    else:
        df = pd.read_parquet(raw_path)
    return df


def clean_dataset(df: pd.DataFrame, mapping: dict, config: dict) -> tuple[pd.DataFrame, dict]:
    """Build combined text, filter short/empty, and deduplicate exact normalized text.

    Returns (cleaned_df, report) where cleaned_df has columns:
      row_id, original_index, source, label, subject, body, combined_text, text_hash
      plus any structural columns found in the source data.
    """
    report = {"n_raw": int(len(df)), "dropped_empty_short": 0, "dropped_conflict_groups": 0,
              "kept_duplicates": 0, "conflict_groups": []}
    min_chars = int(config.get("min_text_chars", 20))
    positive_label = int(config.get("positive_label", 1))

    source_col = mapping.get("source")
    label_col = mapping.get("label")
    subject_col = mapping.get("subject")
    body_col = mapping.get("body")
    if source_col is None or label_col is None:
        raise ValueError("Raw dataset lacks a source column and/or a label column.")
    if subject_col is None and body_col is None:
        raise ValueError("Raw dataset lacks any usable text column (subject or body).")

    work = df.copy()
    work["combined_text"] = [
        build_combined_text(row.get(subject_col), row.get(body_col))
        for _, row in work.iterrows()
    ]
    # Canonical lowercase names for the two required fields.
    work = work.rename(columns={source_col: "source", label_col: "label"})
    source_col = "source"
    label_col = "label"
    # Binary label coercion.
    labels = work[label_col]
    unique_labels = set(str(v).strip().lower() for v in labels.dropna().unique())
    label_map = {}
    numeric = True
    for v in unique_labels:
        try:
            f = float(v)
        except ValueError:
            numeric = False
            break
        if f not in (0.0, 1.0):
            numeric = False
            break
    if numeric and unique_labels:
        label_map = {v: int(float(v)) for v in unique_labels}
    elif unique_labels == {"benign", "phishing"} or unique_labels == {"ham", "spam"}:
        benign_key = "benign" if "benign" in unique_labels else "ham"
        label_map = {v: 0 if v == benign_key else 1 for v in unique_labels}
    else:
        raise ValueError(f"Label values {unique_labels} cannot be mapped unambiguously to {{0,1}}.")
    work = work[labels.notna()]
    labels = work[label_col]
    work["label"] = [label_map[str(v).strip().lower()] for v in labels]

    work["text_len"] = work["combined_text"].astype(str).str.len()
    n_before = len(work)
    work = work[work["text_len"] >= min_chars]
    report["dropped_empty_short"] = n_before - len(work)

    work["text_hash"] = work["combined_text"].map(
        lambda t: hashlib.sha256(normalize_for_dedup(t).encode("utf-8")).hexdigest())

    # Deduplicate exact normalized text.
    group_label_sets = work.groupby("text_hash")["label"].agg(lambda s: set(s))
    conflicting = set(group_label_sets[group_label_sets.map(len) > 1].index)
    report["conflict_groups"] = sorted(conflicting)
    report["n_conflict_groups"] = len(conflicting)
    n_conflict_rows = int(work["text_hash"].isin(conflicting).sum())
    conflict_rows = work.loc[work["text_hash"].isin(conflicting)]
    report["dropped_conflict_groups"] = n_conflict_rows
    report["conflict_row_original_indices"] = [int(i) for i in conflict_rows.index]

    work = work[~work["text_hash"].isin(conflicting)]
    work = work.sort_values("text_hash").groupby("text_hash", sort=False).head(1)
    report["kept_duplicates"] = n_before - report["dropped_empty_short"] - n_conflict_rows - len(work)

    work = work.sort_index()
    work["original_index"] = work.index.astype(np.int64)
    work = work.reset_index(drop=True)
    work["row_id"] = np.arange(len(work), dtype=np.int64)

    keep_cols = ["row_id", "original_index", "source", "label", "combined_text", "text_hash"]
    for col in [subject_col, body_col]:
        if col is not None:
            keep_cols.append(col)
    structural = ["url_count", "url_length_max", "url_length_avg", "url_subdom_max",
                  "url_subdom_avg", "attachment_count", "has_attachments", "content_types",
                  "attachment_types", "language", "urls"]
    for key in structural:
        col = mapping.get(key)
        if col is not None:
            work[key] = work[col]
            keep_cols.append(key)

    cleaned = work[keep_cols].copy()
    cleaned["positive_label"] = positive_label
    report["n_clean"] = int(len(cleaned))
    report["n_pos"] = int((cleaned["label"] == positive_label).sum())
    report["n_neg"] = int((cleaned["label"] != positive_label).sum())
    return cleaned, report


def load_clean(config: dict, processed_path) -> pd.DataFrame:
    processed_path = Path(processed_path)
    if not processed_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {processed_path}. Run the audit stage first.")
    return pd.read_parquet(processed_path)


def write_clean(cleaned: pd.DataFrame, processed_path, config: dict) -> Path:
    processed_path = Path(processed_path)
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = processed_path.with_name(processed_path.name + ".tmp")
    cleaned.to_parquet(tmp, compression="gzip")
    provenance.atomic_write_json(tmp.with_suffix(".meta.json"), {
        "rows": int(len(cleaned)),
        "sha256": provenance.sha256_file(tmp),
    })
    tmp.replace(processed_path)
    return processed_path


def compute_structural_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the structural feature table for M3 from the cleaned dataset.

    Only defensible, non-identity fields are used. Identity-linked columns
    (source, sender, sender_domain, receiver, receiver_domain, date, label,
    row_id) are excluded by construction here and by the excluded-column audit.
    """
    numeric = ["url_count", "url_length_max", "url_length_avg", "url_subdom_max",
               "url_subdom_avg", "attachment_count", "has_attachments"]
    categorical = ["content_types", "language"]
    d = pd.DataFrame(index=df.index)
    for key in numeric:
        if key in df.columns:
            d[key] = pd.to_numeric(df[key], errors="coerce")
        else:
            d[key] = np.nan
    for key in categorical:
        if key in df.columns:
            d[key] = df[key].astype(str).replace({"nan": "", "None": ""})
        else:
            d[key] = ""
    text = df["combined_text"].astype(str)
    d["message_len"] = text.str.len()
    d["punct_count"] = text.str.count(r"[^\w\s]")
    d["digit_count"] = text.str.count(r"\d")
    d["anon_token_count"] = text.str.count(ANON_TOKEN_PATTERN)
    return d

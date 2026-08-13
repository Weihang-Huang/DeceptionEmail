# DeceptionEmail

Reproducible source-aware evaluation of lightweight, CPU-compatible classifiers for
deceptive email detection on the MeAJOR v2.0 corpus.

**Working title:** Beyond Random Splits: Cross-Source Generalisation of Lightweight
Models for Deceptive Email Detection

## Scientific question

Does conventional stratified random splitting overestimate the cross-source
generalisation of lightweight deceptive-email classifiers because source-specific
artefacts appear in both training and testing data?

## Layout

- `plan_main.md` — authoritative specification (read it first).
- `AGENTS.md` — non-negotiable operating rules.
- `configs/default.yaml` — experiment configuration (seed, text, models, hardware, cache).
- `src/deceptive_email/` — implementation package (CLI, data, audit, splitting,
  features, models, evaluation, efficiency, caching, provenance, manuscript,
  verification, reporting).
- `tests/` — unit tests with synthetic fixtures.
- `data/raw/` — immutable raw dataset (ignored by Git). See `data/README.md`.
- `data/processed/` — cleaned, deduplicated dataset (ignored by Git).
- `cache/` — content-addressed reusable artifacts (ignored by Git).
- `outputs/` — audit, splits, and per-run artifacts (ignored by Git).
- `reports/` — research, reproducibility, limitations, submission decision,
  hallucination-audit, claim-traceability, and reference-verification reports.
- `paper/` — IEEEtran LaTeX manuscript, generated tables/figures, build output.

## Quick start

Reproduction (Linux/macOS or WSL):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
export PYTHONHASHSEED=42
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python -m pytest -q
deceptive-email all --config configs/default.yaml
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-lock.txt
$env:PYTHONHASHSEED="42"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:OPENBLAS_NUM_THREADS="1"
python -m pytest -q
deceptive-email all --config configs/default.yaml
```

Paper rebuild from a completed run:

```bash
deceptive-email build-paper --run-id <run_id>
deceptive-email verify-manuscript --run-id <run_id>
```

## Status

The manuscript is for internal research use only. It is released for **human review
only** and must never be submitted, uploaded, or published automatically.

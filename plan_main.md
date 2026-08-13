# Agent-Executable Research and Manuscript Plan

## Project identity

**Working title:** Beyond Random Splits: Cross-Source Generalisation of Lightweight Models for Deceptive Email Detection

**Target venue:** IEEE CyberSciTech 2026

**Scientific track:** Track 2 — Cyber Security, Privacy & Trust

**Primary topic:** Cyber Crime, Fraud, Abuse & Forensics

**Secondary topic:** Cyber Security, Safety & Resilience

**Preferred submission category:** Late Breaking Innovation (LBI), unless a human confirms that the Regular track remains open and the Regular submission gate in this plan is satisfied.

**Research type:** Reproducible empirical measurement study, not a new-algorithm paper.

**Core question:** Does conventional stratified random splitting overestimate the cross-source generalisation of lightweight deceptive-email classifiers because source-specific artefacts occur in both training and testing data?

---

## 1. Required outcome

The implementation agent must deliver:

1. A complete, tested, reproducible Python repository.
2. A validated source-aware experiment using only open-source, CPU-compatible models.
3. Cached cleaned data, split manifests, fitted preprocessors, feature matrices where practical, every fitted model, every prediction, metrics, timings, and useful intermediate artifacts.
4. Publication-ready figures and tables generated from canonical result files.
5. A complete LaTeX manuscript using the official IEEE conference template.
6. A compiled manuscript PDF when a compatible LaTeX toolchain is available.
7. Claim-traceability and reference-verification registers.
8. A formal hallucination audit completed before the manuscript is returned for human review.
9. A submission recommendation of Regular, LBI, WiP, or Do not submit.

The agent must not stop at a paper outline. It must not invent data, experimental outcomes, references, execution logs, hardware use, or conclusions. It must not submit, upload, email, or publish the manuscript.

---

## 2. Agent operating rules

1. Read this entire file before changing the repository.
2. Inspect existing files before creating or overwriting anything.
3. Produce a numbered implementation checklist before coding.
4. Work phase by phase and run tests after each phase.
5. Keep raw data immutable and outside Git.
6. Fit every vectorizer, imputer, encoder, scaler, and model on training data only.
7. Never use `source`, `label`, sender identity, receiver identity, row index, or direct corpus identifiers as predictive features.
8. Never evaluate a binary classifier on a single-class test set.
9. Do not call all positive records “phishing” without qualification. Prefer “deceptive email,” “malicious/fraudulent email,” or “the dataset’s positive class.”
10. Do not treat spam, phishing, scam, and fraud as interchangeable concepts.
11. Use only open-source Python packages and CPU-compatible models.
12. Do not call proprietary APIs, commercial LLMs, hosted inference services, AutoML systems, or GPU-dependent models.
13. Record package versions, random seeds, commands, hardware, timings, memory measurements, checksums, configuration changes, and failures.
14. Prefer a correct small experiment over a large invalid experiment.
15. If the source/class composition prevents a valid source-disjoint evaluation, write `reports/BLOCKER.md` and stop. Do not silently substitute a random-only study.
16. Do not claim state-of-the-art performance, algorithmic novelty, deployment readiness, or generalisation beyond the evaluated corpora.
17. Every result in the manuscript must be traceable to a canonical artifact.
18. Every literature claim must be supported by a verified source.
19. Run an independent hallucination audit after drafting and after every substantive manuscript revision.
20. Human review remains mandatory before submission.

---

## 3. Research questions

- **RQ1:** How much does performance change between a conventional stratified random split and source-disjoint evaluation?
- **RQ2:** Which lightweight representation transfers best to unseen corpora: word TF–IDF, character TF–IDF, or structural features?
- **RQ3:** What accuracy–efficiency trade-offs do these models provide in training time, inference time, memory use, feature count, and serialized size?
- **RQ4:** Which corpus and class combinations produce the largest errors under source shift?

### Hypotheses

- **H1:** Random-split macro-F1 is higher than source-disjoint macro-F1.
- **H2:** Character n-grams are more robust under source shift than word n-grams.
- **H3:** At least one lightweight model offers a useful performance–cost balance without transformers or LLMs.

Treat these as testable propositions, not expected conclusions. Report contradictory, negative, or null findings honestly.

### Intended contributions

Use no more than these three contributions in the manuscript:

1. A source-aware audit of the MeAJOR corpus for deceptive-email evaluation.
2. A comparison of random and source-disjoint evaluation using transparent CPU-compatible models.
3. An empirical accuracy–efficiency analysis with a reproducible implementation.

---

## 4. Dataset

Use MeAJOR version 2.0, preferably the compressed Parquet release.

Expected local path:

```text
data/raw/meajor_cleaned_preprocessed.parquet.gzip
```

Accepted fallback:

```text
data/raw/meajor_cleaned_preprocessed.csv
```

The dataset paper and Zenodo record document five source corpora: TREC-05, TREC-06, TREC-07, Nazario, and Nigerian Fraud. The audited release artifact contains only the three TREC corpora (`trec5`, `trec6`, `trec7`) plus one `None`-source row; the Nazario and Nigerian Fraud corpora are absent from the released file. This is a data-release discrepancy, not a pipeline loss, and is recorded in `outputs/audit/source_composition.json`. The agent must verify actual source names and distributions from the loaded data rather than assuming them, and must scope all claims to the sources actually present (the three TREC spam tracks).

The agent may download the data only from the dataset’s official public record when network access is available. Record the source URL, access time, file name, size, and SHA-256. If the dataset is unavailable, create `data/README.md` with precise placement and checksum instructions, then exit with code 2. Never substitute synthetic data for the research experiment. Tiny synthetic fixtures are permitted only in unit tests.

### Required fields

Resolve names case-insensitively and document the mapping:

- Source corpus
- Binary label
- Subject, if present
- Body or message text
- Existing numerical or categorical structural features, if present

If no usable text field or binary target exists, write `reports/BLOCKER.md` and stop.

---

## 5. Repository structure

Create or normalize the repository to:

```text
.
├── plan_main.md
├── AGENTS.md
├── README.md
├── LICENSE
├── CITATION.cff
├── Makefile
├── pyproject.toml
├── requirements-lock.txt
├── configs/
│   └── default.yaml
├── data/
│   ├── README.md
│   ├── raw/                         # ignored by Git
│   └── processed/                   # ignored by Git
├── src/
│   └── deceptive_email/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── data.py
│       ├── audit.py
│       ├── splitting.py
│       ├── features.py
│       ├── models.py
│       ├── evaluation.py
│       ├── efficiency.py
│       ├── cache.py
│       ├── provenance.py
│       ├── manuscript.py
│       ├── verification.py
│       └── reporting.py
├── tests/
│   ├── test_data.py
│   ├── test_splitting.py
│   ├── test_leakage.py
│   ├── test_metrics.py
│   ├── test_cache.py
│   ├── test_provenance.py
│   └── test_manuscript_verification.py
├── cache/                            # ignored by Git
│   ├── features/
│   ├── matrices/
│   └── joblib/
├── outputs/                          # large contents ignored by Git
│   ├── audit/
│   ├── splits/
│   ├── runs/
│   │   └── <run_id>/
│   │       ├── manifest.json
│   │       ├── environment.json
│   │       ├── models/
│   │       ├── predictions/
│   │       ├── matrices/
│   │       ├── metrics/
│   │       ├── figures/
│   │       ├── logs/
│   │       └── checksums.sha256
│   └── latest -> runs/<run_id>
├── reports/
│   ├── research_report.md
│   ├── limitations.md
│   ├── reproducibility.md
│   ├── submission_decision.md
│   ├── hallucination_audit.md
│   ├── claim_traceability.csv
│   └── reference_verification.csv
└── paper/
    ├── manuscript.tex
    ├── references.bib
    ├── IEEEtran.cls                 # only if official and redistribution is allowed
    ├── generated/
    │   ├── result_macros.tex
    │   ├── dataset_table.tex
    │   ├── performance_table.tex
    │   ├── efficiency_table.tex
    │   └── holdout_table.tex
    ├── figures/
    ├── build/
    │   └── manuscript.pdf
    ├── README.md
    └── template_provenance.md
```

Add `.gitignore` entries for raw/processed data, caches, large outputs, fitted models, sparse matrices, virtual environments, LaTeX build debris, and temporary files. Final paper source, small generated tables, verification reports, and reproducibility metadata may be committed.

---

## 6. Environment and hardware

### Software

- Python 3.11 or newer
- Linux/macOS compatible
- CPU-based sparse linear models
- Fixed primary seed: 42
- Sensitivity seeds: 7 and 123 when affordable

### Allowed dependencies

```text
pandas
pyarrow
numpy
scipy
scikit-learn
joblib
psutil
pyyaml
matplotlib
seaborn
pytest
xgboost   # added 2026-08-11 for the word_xgboost baseline (reviewer plan); CPU-only, open source
```

Do not add TensorFlow, PyTorch, transformers, downloaded language models, proprietary SDKs, or AutoML.

### Available hardware

The expected machine has approximately 56 GB of system memory shared with one Intel XPU. The planned scikit-learn models are primarily CPU workloads.

Required policy:

1. Treat the Intel XPU as optional and nonessential.
2. Do not install deep-learning or oneAPI frameworks merely to use the XPU.
3. Use CPU sparse linear algebra unless a dependency already provides a verified drop-in XPU path with identical behavior and no material complexity.
4. Record CPU, RAM, OS, Python, scikit-learn, BLAS backend, disk capacity, and visible XPU metadata in `environment.json`.
5. If `xpu-smi` or an equivalent read-only command is available, record its output. Do not fail if absent.
6. Set the normal process-memory budget to 42 GB and hard safety threshold to 46 GB.
7. Run only one feature-building or model-fitting job at a time by default.
8. Default to four experiment threads and one deterministic verification thread.
9. Use sparse CSR/CSC matrices and never densify a full text matrix.
10. Estimate feature-matrix memory from a sample before full fitting.
11. Abort the current stage cleanly if resident memory crosses the hard limit, retaining prior valid caches and writing recovery instructions.

---

## 7. Configuration

Create `configs/default.yaml`:

```yaml
seed: 42
sensitivity_seeds: [7, 123]
run_all_source_holdouts: true
enable_equal_size_controls: true
positive_label: 1
min_text_chars: 20
min_test_per_class: 100
random_test_size: 0.20
bootstrap_iterations: 1000

text:
  combine_subject_body: true
  lowercase: true
  exact_deduplication: true
  word:
    ngram_range: [1, 2]
    min_df: 3
    max_df: 0.98
    max_features: 50000
    sublinear_tf: true
  character:
    analyzer: char_wb
    ngram_range: [3, 5]
    min_df: 3
    max_features: 100000
    sublinear_tf: true

models:
  word_logistic_regression:
    C: 1.0
    class_weight: balanced
    solver: liblinear
    max_iter: 1000
  character_linear_svm:
    C: 1.0
    class_weight: balanced
  structural_logistic_regression:
    C: 1.0
    class_weight: balanced
    solver: liblinear
    max_iter: 1000

efficiency:
  repetitions: 3
  inference_batch_size: 1000

hardware:
  execution_device: cpu
  detect_intel_xpu: true
  use_xpu: false
  total_shared_memory_gb: 56
  target_process_memory_gb: 42
  hard_process_memory_gb: 46
  experiment_threads: 4
  verification_threads: 1
  concurrent_models: 1

cache:
  enabled: true
  root: cache
  compression: 3
  cache_clean_data: true
  cache_split_manifests: true
  cache_vectorizers: true
  cache_feature_matrices: true
  cache_fitted_models: true
  cache_predictions: true
  cache_metrics: true
  cache_figures: true
  atomic_writes: true
  verify_checksums: true
  minimum_free_disk_gb: 20
```

If runtime or memory is excessive, reduce text `max_features` once, record the reason and old/new values in `outputs/runs/<run_id>/logs/deviations.json`, and rerun comparable models consistently. Do not tune configurations opportunistically using test performance.

---

## 8. CLI and Makefile

Implement these CLI commands:

```bash
deceptive-email inspect-hardware --config configs/default.yaml
deceptive-email audit --config configs/default.yaml
deceptive-email make-splits --config configs/default.yaml
deceptive-email run --config configs/default.yaml
deceptive-email report --config configs/default.yaml
deceptive-email all --config configs/default.yaml
deceptive-email run-stage --stage <stage> --config configs/default.yaml
deceptive-email resume --run-id <run_id>
deceptive-email build-paper --run-id <run_id>
deceptive-email verify-manuscript --run-id <run_id>
deceptive-email verify-cache --run-id <run_id>
deceptive-email package-artifacts --run-id <run_id>
```

Add equivalent `Makefile` targets:

```bash
make setup
make test
make audit
make experiment
make report
make paper
make verify
make all
```

`make all` must run tests, audit, validity gate, split construction, experiments, reporting, manuscript generation, verification, and LaTeX compilation in that order. It must stop on the first failed gate.

All commands must be idempotent or require `--force` before overwriting. A failed stage must not be marked successful.

---

## 9. Phase A: Bootstrap

### Tasks

1. Create the repository structure.
2. Create `pyproject.toml`, console entry point, and pinned dependencies.
3. Create `AGENTS.md` summarizing non-negotiable rules.
4. Implement the CLI and Makefile.
5. Add synthetic-fixture unit tests.
6. Implement structured logging and nonzero error codes.
7. Implement hardware inspection and initial environment capture.

### Gate

- `python -m pytest -q` passes.
- `deceptive-email --help` succeeds.
- No research result exists before an actual research command runs.

---

## 10. Phase B: Dataset audit

This phase gates all experiments.

### Text construction

Construct:

```text
combined_text = subject + "\n" + body
```

Use available components. Preserve anonymization placeholders such as `[URL]`. Normalize Unicode form, line endings, and repeated whitespace for duplicate detection. Do not remove punctuation for character models.

### Mandatory audits

1. Dataset dimensions and schema.
2. Column-name mapping.
3. Missing values by field.
4. Label values and counts.
5. Source names and counts.
6. Source-by-class cross-tabulation.
7. Text-length distributions by source and class.
8. Empty and short text counts.
9. Exact duplicate groups using SHA-256 of normalized text.
10. Duplicate-label conflicts.
11. Candidate predictors and explicit exclusions.
12. Class balance after cleaning and deduplication.
13. Dataset file fingerprint and provenance.

### Duplicate policy

- Remove exact duplicate text before splitting.
- If duplicate copies share a label, keep one deterministic row.
- If identical text has conflicting labels, remove the entire conflicting group and report it.
- Do not perform semantic near-duplicate detection in the minimum viable study.

### Outputs

```text
outputs/audit/schema.json
outputs/audit/source_class_distribution.csv
outputs/audit/missingness.csv
outputs/audit/text_length_summary.csv
outputs/audit/duplicate_report.json
outputs/audit/excluded_columns.json
outputs/audit/audit_summary.md
data/processed/clean_deduplicated.parquet
```

### Audit gate

Proceed only if:

- labels map unambiguously to 0 and 1;
- both classes remain after cleaning;
- at least one valid source-disjoint holdout can be constructed;
- training and test candidates each contain both classes;
- source and label fields are not required as predictors.

On failure, create `reports/BLOCKER.md` and stop.

### Human checkpoint 1

A human should approve the source/label mapping, positive-class interpretation, excluded columns, and duplicate policy before modelling.

---

## 11. Phase C: Split construction

Create and save row-ID manifests before feature extraction. Never regenerate splits independently for different models.

### Protocol 1: Random baseline

Create an 80/20 stratified split after deduplication using seed 42. Both partitions must contain both classes. Repeat the stratified random protocol with sensitivity seeds 7 and 123 so that random-split variance is quantified across the full pipeline (run all three seeds when resources allow). Add equal-size controls: for each selected source-disjoint holdout, construct a same-size stratified random split (same test-set size, same seed lineage) so that random-vs-source performance is compared at matched test sizes. Every random protocol must assert both classes in both partitions and disjoint normalized-text hashes.

### Protocol 2: Source-disjoint evaluation

Enumerate all valid source holdouts of size one and two (for three TREC sources: six candidates). A candidate is valid only if:

- no source occurs in both training and test sets;
- training contains both classes;
- test contains both classes;
- each test class has at least `min_test_per_class` rows;
- each training class has at least `min_test_per_class` rows.

Rank valid candidates deterministically by:

1. smallest absolute difference between test positive rate and 0.5;
2. largest test-set size;
3. lexicographic source-name order.

Run ALL valid candidates (do not cap at three); the earlier cap of three is removed. Save all candidates and reasons for selection or rejection in `candidate_holdouts.csv`.

If no size-one or size-two holdout is valid, enumerate size-three holdouts. If none is valid, fail rather than creating a pseudo-source-disjoint protocol.

### Leakage assertions

For every split assert:

- train/test row IDs are disjoint;
- normalized-text hashes are disjoint;
- source sets are disjoint for source-disjoint protocols;
- both classes occur in train and test;
- preprocessing objects are unfitted before training;
- excluded identifiers are absent from features.

### Outputs

```text
outputs/splits/random_seed42_train.csv
outputs/splits/random_seed42_test.csv
outputs/splits/random_seed7_train.csv
outputs/splits/random_seed7_test.csv
outputs/splits/random_seed123_train.csv
outputs/splits/random_seed123_test.csv
outputs/splits/random_eqsize_<holdout_id>_train.csv
outputs/splits/random_eqsize_<holdout_id>_test.csv
outputs/splits/source_holdout_<source>_train.csv
outputs/splits/source_holdout_<source>_test.csv
outputs/splits/split_manifest.json
outputs/splits/candidate_holdouts.csv
```

Split IDs are descriptive: `random_seed<seed>`, `random_eqsize_<source_holdout_id>`, and `holdout_<source>` (e.g. `holdout_trec5`, `holdout_trec6`, `holdout_trec7`, `holdout_trec5_trec6`). The manifest records protocol, train/test sizes, held-out sources, and per-class counts for every split.

### Human checkpoint 2

A human should approve the selected source-disjoint holdouts before full modelling.

---

## 12. Phase D: Features and models

Run exactly three primary pipelines. Do not add models merely to enlarge tables.

### M1: Word TF–IDF + logistic regression

- Word unigrams and bigrams
- Sparse TF–IDF
- Balanced logistic regression
- No stop-word removal unless justified in a recorded ablation

### M2: Character TF–IDF + linear SVM

- `char_wb` character 3–5 grams
- Sparse TF–IDF
- `LinearSVC`
- Primary robustness baseline

### M3: Structural features + logistic regression

Use only defensible non-identity fields, such as:

- URL counts or length summaries
- Attachment counts or flags
- Message length
- HTML or content-type indicators
- Punctuation or digit counts computed reproducibly

Use a training-only `ColumnTransformer` with imputation, numeric scaling, and one-hot encoding of low-cardinality categorical variables. Exclude source, sender, receiver, identity-linked domains, labels, row IDs, and timestamps that reveal corpus age unless explicitly justified.

If fewer than five defensible structural features exist, replace M3 with a combined word+character linear model only if the memory estimate is safe. Otherwise run two models and document the reason.

### Hyperparameters

Use configured defaults. If a minimal training-only search is necessary, allow only `C ∈ {0.1, 1, 10}` with three-fold stratified cross-validation inside training. Never use test results for selection.

### Human checkpoint 3

After the first model, inspect metrics and predictions for implausibly high performance, source leakage, duplicate leakage, row misalignment, or label inversion.

---

## 13. Caching and resumability

Every expensive or decision-relevant stage must be cached so the study can change direction without repeating prior work.

### Run identity

Generate a unique run ID from:

- Cleaned dataset SHA-256
- Configuration SHA-256
- Git commit, or source-tree hash if Git is unavailable
- Python/package environment fingerprint
- Split-manifest hash

Use a timestamp plus short hash, for example:

```text
20260811T031500Z_a19c82f5
```

Never overwrite a run. Point `outputs/latest` to the most recent completed valid run.

### Cache keys

Key artifacts by all relevant inputs:

```text
dataset_hash / split_hash / feature_config_hash / model_config_hash / code_hash
```

A cache hit is valid only when metadata and SHA-256 match. Quarantine and recompute invalid artifacts.

### Cache these artifacts

#### Data and audit

- Schema mapping
- Normalized text hashes
- Cleaned and deduplicated Parquet
- Audit tables
- Duplicate groups and removed IDs
- Excluded-column decisions

#### Splits

- Train/test row IDs
- Source and class counts
- Validity assertions
- Selected/rejected holdouts with reasons

#### Features

For every split and representation:

- Fitted vectorizer or preprocessor
- Vocabulary and feature names
- Sparse train/test matrices as `.npz`
- Labels as `.npy`
- Row order as Parquet or `.npy`
- Shape, dtype, nonzero count, and memory estimate

Reuse content-addressed feature caches across compatible models.

#### Models

Cache complete trusted-local scikit-learn pipelines with:

- Model identifier and version
- Hyperparameters
- Split and feature hashes
- Fitting duration
- Package versions
- Serialized size and checksum

Use `joblib`. Warn users never to load pickle/joblib artifacts from untrusted sources.

#### Predictions

Cache every model–split prediction set in Parquet with:

```text
row_id
split_id
protocol
held_out_sources
model_id
representation_id
y_true
y_pred
decision_score
positive_probability
source
text_length
correct
run_id
```

Use `positive_probability` only when genuinely produced. For `LinearSVC`, store the signed decision score and leave probability null.

Predictions are the canonical inputs for metrics, confidence intervals, statistical tests, error analysis, and manuscript results. These stages must rerun without model fitting.

#### Metrics and reports

Cache:

- Metric CSVs
- Bootstrap seeds or indices
- Confidence intervals
- Confusion matrices
- McNemar inputs/results
- Timing repetitions
- Error-analysis sample IDs
- Figure-ready tidy data
- Generated LaTeX tables and macros

### Atomicity and recovery

- Write to temporary files, then rename atomically.
- Create stage `_SUCCESS.json` only after all artifacts and checksums validate.
- A failed stage has no valid success marker.
- `resume` continues from the last valid stage.
- `verify-cache` checks hashes, metadata, readability, row alignment, and dependency relationships.

### Disk-pressure policy

If free disk is insufficient:

1. Always keep cleaned data, split manifests, fitted pipelines, predictions, metrics, and provenance.
2. Delete reproducible feature matrices before models or predictions.
3. Record deletions and regeneration commands.
4. Never silently disable prediction caching.

---

## 14. Phase E: Evaluation

### Primary metrics

For every model and split:

- Macro-F1
- Positive-class precision
- Positive-class recall
- Matthews correlation coefficient
- Balanced accuracy
- Confusion matrix

Accuracy is secondary only.

### Confidence intervals

Calculate stratified bootstrap 95% confidence intervals for macro-F1 and MCC with 1,000 iterations. Resample within class. Redraw replicates that lack both classes.

### Efficiency

On the same machine, report:

- Feature extraction time
- Training time
- Inference time per 1,000 messages
- Serialized pipeline size in MB
- Feature count
- Peak memory estimate when reliable

Repeat timing three times and report medians. Exclude import time. Record hardware and software metadata.

### Error analysis

For the best source-disjoint model by macro-F1:

- sample up to 25 false positives and 25 false negatives per holdout;
- report source, text length, anonymization-token counts, URL indicators, and decision score;
- identify recurring observable categories without inventing latent ground truth;
- redact accidental personal information;
- do not reproduce harmful links or operational phishing content.

### Statistical comparison

Use paired McNemar tests only for models evaluated on exactly the same rows. Apply Holm correction within each split. Do not confuse nonsignificance with equivalence.

### Outputs

```text
outputs/runs/<run_id>/metrics/all_metrics.csv
outputs/runs/<run_id>/metrics/confidence_intervals.csv
outputs/runs/<run_id>/metrics/confusion_matrices.csv
outputs/runs/<run_id>/metrics/timing.csv
outputs/runs/<run_id>/metrics/model_comparisons.csv
outputs/runs/<run_id>/metrics/error_samples_redacted.csv
outputs/runs/<run_id>/models/*.joblib
outputs/runs/<run_id>/predictions/*.parquet
outputs/runs/<run_id>/logs/run_metadata.json
outputs/runs/<run_id>/logs/deviations.json
```

---

## 15. Phase F: Figures and tables

Generate readable PDF and PNG figures.

### Figures

1. `source_class_distribution`: source-by-class counts.
2. `random_vs_source_disjoint`: macro-F1 by model and protocol.
3. `generalisation_gap`: random macro-F1 minus each source-disjoint macro-F1.
4. `accuracy_efficiency_tradeoff`: source-disjoint macro-F1 versus inference time or model size.

### Tables

1. Dataset/source audit.
2. Model and feature definitions.
3. Main performance with confidence intervals.
4. Efficiency results.
5. Per-holdout results.

Store raw values in CSV and rounded presentation values in generated LaTeX. Copy final visual artifacts into `paper/figures/` and tables into `paper/generated/`.

---

## 16. Interpretation rules

Separate observations from interpretations.

### Allowed conclusions

- Random splitting produced higher, lower, or similar performance compared with source-disjoint testing.
- A representation was more or less robust across the evaluated corpora.
- A model had a measured efficiency advantage on the recorded hardware.
- Corpus composition limits the external validity of deceptive-email detection claims.

### Disallowed conclusions

- The model detects all phishing.
- The model is operationally ready.
- Cross-corpus testing proves generalisation to current attacks.
- High accuracy implies semantic understanding.
- The method is state of the art without a comprehensive comparable benchmark.
- XPU acceleration occurred when the experiment ran on CPU.

### Required limitations

- Historical and heterogeneous corpora
- Ambiguity among spam, phishing, scam, and fraud labels
- Source–label confounding
- Anonymization placeholders
- Exact rather than semantic deduplication
- No contemporary live-email validation
- No adversarial robustness experiment
- Limited hyperparameter tuning
- Hardware-dependent timing

### Human checkpoint 4

A human should approve interpretations, limitations, and contribution wording before final manuscript drafting.

---

## 17. Full IEEE LaTeX manuscript

### Template requirement

Use the official IEEE conference LaTeX format appropriate for CyberSciTech proceedings, normally:

```latex
\documentclass[conference]{IEEEtran}
```

Do not invent or visually imitate a template.

The agent must:

1. Obtain the class/template only from an official IEEE or recognized TeX distribution.
2. Record source URL or package source, access date, class version, license, and checksum in `paper/template_provenance.md`.
3. Bundle `IEEEtran.cls` only if redistribution is permitted; otherwise document the package requirement.
4. Verify the template has not been modified.
5. Never alter margins, fonts, spacing, or column geometry to force page count.

If network access is unavailable and IEEEtran is not installed, produce valid source using `\documentclass[conference]{IEEEtran}`, document installation, complete all non-build checks, and mark PDF compilation blocked. Never substitute an unofficial template.

### Manuscript scope

Produce a complete manuscript, targeting 6–8 substantive pages where consistent with the human-verified live submission category. Do not assume the plan contains authoritative live deadline or page-limit information.

Required components:

- Title
- Author block, with explicit placeholders only where human identity details are unavailable
- Abstract based on real results
- Index terms
- Introduction
- Related work
- Dataset and label-scope discussion
- Source/class audit
- Threats to validity and leakage controls
- Methodology
- Experimental setup
- Results
- Efficiency analysis
- Error analysis
- Discussion
- Limitations
- Ethics statement
- Reproducibility statement
- Conclusion
- Verified bibliography

The manuscript must state that:

- it evaluates deceptive or malicious/fraudulent email according to dataset labels;
- TREC spam, phishing, scam, and fraud are not identical concepts;
- the contribution is evaluation methodology rather than a novel classifier;
- the selected models are intentionally transparent and CPU-compatible;
- external validity is limited to the evaluated corpora.

### Generated results

Do not manually copy machine-generated numbers when automation is possible. Generate `paper/generated/result_macros.tex`, for example:

```latex
\newcommand{\RandomBestMacroFOne}{0.000}
\newcommand{\SourceBestMacroFOne}{0.000}
\newcommand{\GeneralisationGap}{0.000}
```

Populate macros only from validated results. Use `\input{generated/...}` for tables. Every generated file must include run ID, timestamp, and source artifact hash in a comment.

No `0.000` placeholders, `TBD`, `TODO`, `FIXME`, `XX`, `??`, dummy citation, or example number may remain in the release manuscript.

### Paper build

Preferred:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
```

Fallback:

```bash
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

Fail on undefined references or citations. Scan logs for overfull boxes, missing fonts, duplicate labels, and unresolved references. Severe layout warnings block release.

---

## 18. Hallucination and traceability audit

Run this audit after drafting and after every substantive edit.

### Claim classes

Every factual manuscript statement must be:

1. **Experiment-derived:** supported by a specific local artifact.
2. **Dataset-derived:** supported by the audited dataset or official documentation.
3. **Literature-derived:** supported by a verified cited source.
4. **Methodological:** supported by documented library behavior or a cited definition.
5. **Qualified interpretation:** explicitly marked as an interpretation, hypothesis, limitation, or possible explanation.

Remove or rewrite claims fitting none of these classes.

### Claim register

Create `reports/claim_traceability.csv`:

```text
claim_id
tex_file
line_start
line_end
claim_text
claim_type
evidence_artifact
evidence_locator
evidence_hash
verification_method
status
review_notes
```

Register at minimum:

- Every number in the abstract, results, discussion, and conclusion
- Every comparative term such as “higher,” “best,” “largest,” or “more efficient”
- Every dataset-size and source-composition statement
- Every claimed contribution
- Every statement about prior work
- Any conference-policy statement retained in the paper

No release claim may remain unverified.

### Numerical verification

Implement a verifier that:

1. Parses result macros and generated LaTeX tables.
2. Reads corresponding canonical predictions and metrics.
3. Checks exact values and rounded displays.
4. Verifies direction words against actual differences.
5. Detects percentage/proportion confusion.
6. Checks sample counts against split manifests.
7. Ensures abstract, results, and conclusion use consistent values.
8. Flags unexplained numeric literals in result-bearing sections.

### Reference verification

Create `reports/reference_verification.csv`:

```text
bibkey
title
authors
year
venue
doi_or_official_url
verification_source
metadata_match
full_text_or_abstract_checked
claim_supported
status
notes
```

Rules:

- Never invent citations or bibliographic fields.
- Verify metadata against DOI registration, publisher pages, official repositories, DBLP, PubMed, arXiv, or the document itself.
- Prefer DOI and publisher metadata over secondary aggregators.
- Confirm that each source supports its nearby claim.
- If only an abstract was checked, do not claim full-text-only details.
- Remove unverifiable sources.
- Do not cite search snippets as if the underlying paper was read.

### Language and logic checks

Flag:

- Unresolved placeholders and dummy citations
- “State of the art,” “novel,” “first,” “proves,” “guarantees,” or “real-world ready” unless specifically supported
- Unsupported causal claims
- Interchangeable use of spam, phishing, scam, and fraud
- Claims beyond evaluated corpora
- Equivalence claims based only on nonsignificance
- Probability claims for models that supply only decision scores
- XPU acceleration claims when execution was CPU-based
- Unreported configuration deviations

### Independent verification pass

Start a fresh verification process that reads only:

- Manuscript
- Canonical run manifest
- Audited dataset summaries
- Split manifests
- Prediction files
- Metric files
- Generated tables/macros
- Bibliography and reference register

It must not rely on conversational memory or draft notes. Write `reports/hallucination_audit.md` with:

- **Blocker:** fabricated/untraceable result, invalid split, invented citation, unsupported major conclusion
- **Major:** incorrect number, misleading comparison, unsupported factual claim
- **Minor:** imprecision, incomplete qualification, or formatting issue

The manuscript is releasable for human review only when blocker and major counts are zero. Correct all such findings and rerun the audit.

### Human review boundary

A human author must still verify:

- Abstract and conclusion claims
- Every table and figure
- Error-analysis examples
- Bibliography
- Author names and affiliations
- Ethics and licensing statements
- Live conference template and page requirements

---

## 19. Manuscript workflow

Follow this order:

1. Complete dataset audit.
2. Pass the audit gate.
3. Freeze split manifests.
4. Pass leakage checks.
5. Fit models and cache artifacts.
6. Cache every prediction.
7. Generate metrics from predictions.
8. Generate tables, figures, and numeric macros.
9. Verify numerical artifacts.
10. Verify literature metadata and claims.
11. Draft the full LaTeX manuscript.
12. Build the PDF.
13. Run numerical, citation, language, logic, and template checks.
14. Correct all blockers and major issues.
15. Rebuild and rerun independent verification.
16. Produce the research, reproducibility, limitation, hallucination, and submission-decision reports.
17. Return the manuscript for human review, not automatic submission.

Changing direction should reuse caches:

- New metrics use cached predictions.
- New confidence intervals use predictions and stored seeds.
- New figures use tidy metrics/predictions.
- Revised error analysis uses predictions and cleaned rows.
- New framing rebuilds the manuscript without refitting.
- A new model reuses splits and compatible feature matrices.
- A new representation reuses cleaned data and splits.

---

## 20. Reports

Create `reports/research_report.md` containing:

1. Executive finding
2. Dataset audit
3. Split validity
4. Main results
5. Efficiency
6. Error analysis
7. Limitations
8. Reproducibility
9. Recommended submission category

Create `reports/reproducibility.md` containing:

- Dataset fingerprint and placement
- Environment and package versions
- Configuration and code hash
- Run ID and split hashes
- Commands
- Cached-artifact map
- Resource use
- Deviations

Create `reports/limitations.md`, `reports/submission_decision.md`, `reports/hallucination_audit.md`, `reports/claim_traceability.csv`, and `reports/reference_verification.csv`.

---

## 21. Submission decision gate

A human must verify live EDAS availability and deadlines. The agent must not infer them from this plan.

### Recommend Regular only if all are true

- At least three valid source-disjoint evaluations completed.
- All leakage tests passed.
- All three model families completed or a defensible substitution was documented.
- Confidence intervals and efficiency results exist.
- Error analysis is complete.
- The manuscript supports at least six substantive IEEE-format pages.
- Results establish a coherent empirical finding.
- Hallucination blockers and major issues are zero.

### Recommend LBI if

- At least two valid source-disjoint evaluations completed.
- Core leakage tests passed.
- Results are credible but validation or writing remains less complete.
- A human confirms the live LBI track permits submission.

### Recommend WiP if

- The audit and at least one valid source-disjoint experiment completed.
- Findings are explicitly preliminary.
- Regular/LBI gates are not met.

### Recommend no submission if

- Results rely only on random splitting.
- Any reported test set is single-class.
- Source–label confounding is hidden rather than addressed.
- Leakage cannot be corrected.
- Results or references cannot be verified.
- Any hallucination blocker or major issue remains.

### Human checkpoint 5

Verify EDAS category availability, deadline, page requirements, author details, and registration obligations before submission.

---

## 22. Reproduction commands

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
export PYTHONHASHSEED=42
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
python -m pytest -q
deceptive-email all --config configs/default.yaml
```

The `all` command must execute audit → gate → splits → features/models → predictions → evaluation → reporting → manuscript → verification → LaTeX build. It must exit nonzero on a failed validity gate.

To rebuild only the manuscript from a completed run:

```bash
deceptive-email build-paper --run-id <run_id>
deceptive-email verify-manuscript --run-id <run_id>
```

---

## 23. Acceptance tests

### Code

- Unit and integration tests pass.
- CLI and Makefile targets work.
- A deliberately interrupted run resumes successfully.
- Cache hashes and dependency metadata validate.
- Leakage assertions pass.

### Experiments

- Cleaned data and split manifests are immutable within a run.
- Every model is cached.
- Every model–split prediction set is cached.
- Every prediction row maps to one test row and split manifest.
- Metrics regenerate from predictions within documented floating-point tolerance.
- Hardware and resource measurements are recorded.

### Manuscript

- `paper/manuscript.tex` is complete.
- Figures and tables exist.
- Result numbers originate from generated artifacts.
- Bibliography metadata and claim support are verified.
- No unresolved reference, citation, or placeholder remains.
- Official template provenance is recorded.
- PDF compiles when the required toolchain exists.
- Hallucination blocker and major counts are zero.
- Limitations and label ambiguity are explicit.

### Release

- Required reports exist.
- Human-review requirements are stated.
- Exact reproduction and paper-build commands are documented.
- No external action has been taken.

---

## 24. Definition of done

The project is complete only when:

- all tests pass;
- all split and leakage assertions pass;
- every table and figure traces to machine-readable artifacts;
- every reported number is generated or independently verified;
- all fitted models and predictions are cached;
- a clean end-to-end run succeeds or a genuine external build dependency is clearly marked blocked;
- no proprietary or resource-intensive model was used;
- raw data and large artifacts are excluded from Git;
- limitations are explicit;
- the full LaTeX manuscript exists;
- template provenance is verified;
- hallucination blocker and major counts are zero;
- `reports/submission_decision.md` exists;
- the agent provides a concise changelog and exact reproduction commands;
- the manuscript is marked “ready for human review,” never “automatically ready for submission.”

---

## 25. OpenCode execution prompt

Paste this into OpenCode from the repository root:

```text
Read plan_main.md completely and implement it as the authoritative specification.

First inspect the repository and dataset, then produce a numbered checklist. Work phase by phase and run tests after each phase. Do not invent results, references, logs, or conclusions, and do not skip any audit or validity gate.

The required outcome is a complete reproducible Python repository plus a complete LaTeX research manuscript using the official IEEE conference template. Do not stop at an outline, and do not draft experimental findings before valid cached results exist.

Use only open-source, CPU-compatible methods. The machine has approximately 56 GB shared system/XPU memory and one Intel XPU, but the sparse scikit-learn models should remain CPU-based. Do not install deep-learning frameworks merely to use the XPU. Keep normal process memory at or below 42 GB, abort safely above 46 GB, use sparse matrices, estimate memory before fitting, and run one expensive task at a time.

Cache every expensive or decision-relevant artifact: cleaned data, audits, split manifests, fitted preprocessors and vectorizers, sparse matrices where disk permits, every fitted model, every prediction and decision score, metrics, bootstrap inputs, timings, tables, figures, and generated LaTeX macros. Use content-aware cache keys, checksums, atomic writes, stage success markers, and resumable execution. Predictions must always be retained even if feature matrices are later removed to save disk.

The scientific priority is valid source-disjoint evaluation. Audit source by class before modelling. Never use a single-class test set. Remove exact duplicate text before splitting, fit preprocessing on training data only, and exclude source and identity fields from predictors. Stop with reports/BLOCKER.md rather than making random-only cross-source claims.

After experiments, generate the full manuscript with official IEEEtran conference formatting. Generate numerical macros and tables from canonical artifacts rather than manually copying values. Verify every bibliography entry and confirm that each citation supports its nearby claim.

Before returning the manuscript, perform a fresh hallucination audit. Trace every numerical, comparative, dataset, and literature claim to a hashed artifact or verified source. Fail release on invented or untraceable results, fabricated references, invalid splits, unresolved placeholders, inconsistent numbers, unsupported superlatives, causal overclaims, or claims beyond the evaluated data. Correct all blocker and major findings, rebuild, and rerun verification.

Do not submit, upload, email, or publish anything. Finish by reporting repository status, tests, run ID, cached artifacts, resource use, manuscript build status, hallucination-audit status, remaining human-review tasks, deviations from plan, and exact reproduction and paper-build commands.
```

---

## 26. Final agent response format

```text
Repository implementation: PASS/FAIL
Unit/integration tests: PASS/FAIL (n passed, n failed)
Dataset audit gate: PASS/FAIL
Leakage checks: PASS/FAIL
Completed run ID: <run_id>
Models cached: <count/list>
Prediction sets cached: <count/list>
Feature matrices cached: <count/list or documented omissions>
Peak measured memory: <GB>
Execution device: CPU/XPU (expected CPU)
Manuscript source: PASS/FAIL
IEEE template verification: PASS/FAIL
PDF build: PASS/FAIL/BLOCKED
Claim traceability: PASS/FAIL
Reference verification: PASS/FAIL
Hallucination blockers: <count>
Hallucination major issues: <count>
Submission recommendation: Regular/LBI/WiP/Do not submit
Human review still required: YES
Reproduction command: <command>
Paper rebuild command: <command>
```

The agent must not report completion if a validity gate fails or a blocker/major hallucination issue remains.
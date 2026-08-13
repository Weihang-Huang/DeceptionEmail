# Agent operating rules (non-negotiable)

This file summarizes the non-negotiable rules that govern work in this repository. The
authoritative specification is `plan_main.md`; read it in full before any change.

1. Work phase by phase and run tests after each phase.
2. Keep raw data immutable and outside Git (`data/raw/`).
3. Fit every vectorizer, imputer, encoder, scaler, and model on training data only.
4. Never use `source`, `label`, sender/receiver identity, row index, or direct corpus
   identifiers as predictive features.
5. Never evaluate a binary classifier on a single-class test set.
6. Do not call all positive records "phishing" without qualification; prefer
   "deceptive email", "malicious/fraudulent email", or "the dataset's positive class".
7. Do not treat spam, phishing, scam, and fraud as interchangeable concepts.
8. Use only open-source Python packages and CPU-compatible models.
9. Do not call proprietary APIs, commercial LLMs, hosted inference services, AutoML
   systems, or GPU-dependent models.
10. Record package versions, random seeds, commands, hardware, timings, memory
    measurements, checksums, configuration changes, and failures.
11. Prefer a correct small experiment over a large invalid experiment.
12. If the source/class composition prevents a valid source-disjoint evaluation, write
    `reports/BLOCKER.md` and stop. Do not silently substitute a random-only study.
13. Do not claim state-of-the-art performance, algorithmic novelty, deployment readiness,
    or generalization beyond the evaluated corpora.
14. Every result in the manuscript must be traceable to a canonical artifact.
15. Every literature claim must be supported by a verified source.
16. Run an independent hallucination audit after drafting and after every substantive
    manuscript revision. The manuscript is releasable for human review only when blocker
    and major counts are zero.
17. Human review remains mandatory before submission. Never submit, upload, email, or
    publish the manuscript.

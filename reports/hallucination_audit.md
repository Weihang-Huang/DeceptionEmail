# Independent hallucination audit

- Run: `20260811T162016Z_d2881b85`
- Date (UTC): 2026-08-13T23:00:47Z
- Blockers: 0
- Major: 0
- Minor: 0

## Method
This audit read only canonical artifacts: the manuscript, run manifest, audited dataset summaries, split manifests, prediction files, metric files, generated tables/macros, and the reference register. Every numeric result in the abstract, results, discussion, and conclusion must trace to `result_macros.tex`/generated tables, which are regenerated from canonical metrics.

## Release gate
- Blockers + majors = 0
- Manuscript releasable for human review ONLY if blockers and majors are zero.

# Submission decision

- Valid source-disjoint evaluations: 6
- Results depend only on random splitting: False
- Any single-class test set reported: False
- All three model families completed: True
- PDF built: True (8 pages; build log shows no overfull hbox, no undefined references)
- Supplementary: `paper/supplementary.tex` (66-row Table S1) lives in the replication repository at https://github.com/Weihang-Huang/DeceptionEmail and is not part of the submission package. Per the user's clarification, only the main paper PDF is submitted.
- Hallucination blockers: 0, majors: 0
- McNemar claim verified against canonical `model_comparisons.csv` (215/225 significant; softened claim in manuscript)

## Recommendation: Regular (gate satisfied) pending human confirmation of live EDAS availability
- At least three valid source-disjoint evaluations; all model families completed; leakage tests passed; manuscript builds.

## Open items before final camera-ready (human action required)
- **Persistent Zenodo DOI.** §Reproducibility paragraph and `reports/reproducibility.md` header both contain a placeholder for a Zenodo DOI. The public replication repository URL is now fixed at https://github.com/Weihang-Huang/DeceptionEmail and is referenced in the manuscript as the location of the supplementary file (`supplementary.tex`, Table S1). The Zenodo DOI must be added before final submission.
- **Supplementary file is in the GitHub repository.** Per the user's clarification that only the main paper PDF will be submitted, the supplementary file `paper/supplementary.tex` (containing the full 66-row per-split Table S1) has been moved out of the submission package. It is included in the replication repository at https://github.com/Weihang-Huang/DeceptionEmail as `paper/supplementary.tex`. The main paper PDF no longer contains any cross-reference to the supplementary PDF; the in-paper pointer now reads "the supplementary file `supplementary.tex` (Table S1), which is included in the replication repository". No supplementary file needs to be inlined into the main PDF.
- **Scale-framing paragraph.** The new 5-7 sentence scale-framing paragraph in the Introduction makes no empirical claim and adds no new citation, but a human should verify the wording does not inadvertently suggest deployment readiness.
- **McNemar claim wording.** The original "all pairwise McNemar comparisons were significant" claim overstated the evidence and has been softened; a human should verify the new wording is acceptable.

## Required human actions before any submission
- Verify live EDAS availability, deadlines, page limits, and LBI/Regular track status.
- Replace the persistent Zenodo DOI placeholder with a real Zenodo DOI (the public GitHub repository URL is now fixed at `https://github.com/Weihang-Huang/DeceptionEmail`; the supplementary file `supplementary.tex` lives at `paper/supplementary.tex` in that repository).
- Confirm that only the main paper PDF will be submitted, with the supplementary file referenced via the GitHub repository URL (per the user's clarification).
- Approve abstract/conclusion claims, every table/figure, error-analysis examples, bibliography, author names/affiliations, ethics and licensing statements.
- The agent has not submitted, uploaded, emailed, or published anything.

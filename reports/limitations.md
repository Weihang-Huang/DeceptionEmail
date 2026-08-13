# Limitations

The following limitations bound the interpretation of this study:

1. **Historical, heterogeneous corpora.** The three constituent TREC corpora are static, public collections; results do not describe contemporary live email traffic. The independent secondary corpus (ealvaradob/phishing-dataset texts subset) is also a static collection and is not a live stream.
2. **Label ambiguity.** TREC spam, phishing, scam, and fraud are not interchangeable concepts. The MeAJOR binary label collapses them into 'benign' and 'positive'; we always refer to the dataset's positive class, not 'all phishing'. The secondary corpus labels are 'phishing' vs 'benign' and are not directly comparable to the TREC spam-track positive class; the independent-corpus results should be read as a transfer check, not a label-compatible benchmark.
3. **Source-label confounding.** Sources differ systematically in content and class composition; this is exactly the effect under study and limits external validity.
4. **Anonymization placeholders.** [URL], [NAME], etc. were introduced by the dataset pipeline; models may latch onto their distributional signatures. The no-anonymization-token ablations (A1, A2) bound this effect for the linear text models.
5. **Exact, not semantic, deduplication.** Near-duplicate content across sources remains. The cluster-disjoint protocol removes exact-SimHash (Hamming 0) replication only; near-duplicate pairs at Hamming distance 1-8 are not removed by the strict rule.
6. **SimHash LSH recall.** The near-duplicate pair counts are lower bounds: pairs are only found if they share at least one 16-bit band chunk (4 bands x 16 bits), so pairs at Hamming distance d are found with per-band probability (1-d/64)^16. Content-level duplicate groups (Hamming 0) are recovered exactly.
7. **No contemporary live-email validation.**
8. **No adversarial robustness experiment.**
9. **Limited hyperparameter tuning** (fixed defaults; no test-driven selection).
10. **Hardware-dependent timing** on a single Windows machine with CPU execution.
11. **Single primary dataset.** External validity is limited to MeAJOR v2.0 plus one independent secondary corpus.
12. **Release-artifact source discrepancy.** The MeAJOR v2.0 release artifact contains only the TREC 2005/2006/2007 spam-track corpora; the Nazario and Nigerian Fraud corpora documented in the dataset paper (arXiv:2507.17978) and Zenodo record are absent from the released file. This is a data-release discrepancy, not a pipeline loss, confirmed by hashing and recounting the audited artifact. All claims are scoped to the three TREC sources actually present; the label is the TREC spam-track positive class, not a general 'phishing' class.
13. **Source-predictability probe scope.** The probe measures within-training CV accuracy of a source classifier; it does not measure test-source accuracy, which is degenerate in source-disjoint evaluation because the held-out source is absent from the training label space.
14. **Calibration analysis scope.** The isotonic recalibration uses a training-only fold and a Youden-J threshold; it bounds the calibration contribution to the F1 drop but does not fully separate calibration from discrimination loss.
15. **Model ordering.** We do not claim a stable model ordering across holdouts; per-holdout rankings vary with the held-out source.

# Dataset audit summary

- Raw file: `meajor_cleaned_preprocessed.parquet.gzip` (86,278,230 bytes)
- SHA-256: `5a9de6c207634f068928ed0cc68d78ee2fd594ed9a587daf4048974c95715c1a`
- MD5: `78e397ad8447bcdba5a98097921ba8bd`
- Rows in raw file: 108,685
- Columns: 20

## Cleaned dataset
- Rows after cleaning/deduplication: 104,810
- Positive class: 46,810 (0.4466 positive rate)
- Negative class: 58,000
- Dropped empty/short texts: 85
- Dropped conflicting duplicate groups: 0 rows in 0 groups

## Gate
- Labels map to {0,1}: True
- Both classes present: True
- Source-disjoint holdout feasible: True (holdout=('trec5',))
- **PASSED**: True

## Sources
- `trec5`: 49,583 raw rows
- `trec7`: 44,096 raw rows
- `trec6`: 15,005 raw rows
- `None`: 1 raw rows

Cleaned rows by source:
- `trec5`: 46,762 cleaned rows
- `trec7`: 43,352 cleaned rows
- `trec6`: 14,696 cleaned rows

## Source-composition verification
- Documented sources: 5 (nazario, nigerian_fraud, trec5, trec6, trec7)
- Sources present in release artifact: 3 (trec5, trec6, trec7)
- Documented but absent from release: nazario, nigerian_fraud
- Present but undocumented: none
- Matches documentation: False

The MeAJOR v2.0 release artifact contains only the TREC 2005/2006/2007 spam-track corpora; the Nazario and Nigerian Fraud corpora documented in the dataset paper and Zenodo record are absent from the artifact. This is a data-release discrepancy, not a pipeline loss. The study scope is therefore limited to the three TREC sources actually present.

## Near-duplicate analysis (SimHash)
- Content-level duplicate groups (identical 64-bit SimHash, exact): 1632 groups, 10,640 rows (0.1015); cross-source groups: 78 with 5,118 rows
- Near-duplicate pairs (Hamming ≤ 8, LSH lower bound): 5,589,932 total, 1,463,061 cross-source; 57,278 rows involved (0.5465)
- Identical-SimHash pairs (Hamming = 0): 2,773,190 total, 559,382 cross-source
- See `exact_duplicate_groups.csv`, `near_duplicate_summary.csv`, `near_duplicate_pairs.csv`, and `near_duplicate_analysis.json`.

See `source_class_distribution.csv`, `missingness.csv`, `text_length_summary.csv`, and `duplicate_report.json` for details.
# Raw dataset placement

## MeAJOR v2.0

Expected file:

```text
data/raw/meajor_cleaned_preprocessed.parquet.gzip
```

Preferred format: Apache Parquet (compressed with GZIP), 86,278,230 bytes.

Accepted fallback:

```text
data/raw/meajor_cleaned_preprocessed.csv
```

## Official record

- Record: https://zenodo.org/records/18471483
- DOI: 10.5281/zenodo.18471483
- Version: 2.0
- License: CC-BY-4.0
- Description: "MeAJOR: Merged email Assets from Joint Open-source Repositories"

## Checksums (recorded from the official Zenodo API on 2026-08-11)

Parquet file `meajor_cleaned_preprocessed.parquet.gzip`:
- MD5: 78e397ad8447bcdba5a98097921ba8bd
- Size: 86278230 bytes

CSV file `meajor_cleaned_preprocessed.csv`:
- MD5: aa8f59e96787cbd696c0b650e5400dc9
- Size: 191121228 bytes

Direct download (Zenodo content endpoint):

```text
https://zenodo.org/api/records/18471483/files/meajor_cleaned_preprocessed.parquet.gzip/content
```

## Required columns (resolved case-insensitively)

`source`, `label`, `subject`, `body`, plus structural fields
(`url_count`, `url_length_max`, `url_length_avg`, `url_subdom_max`, `url_subdom_avg`,
`attachment_count`, `has_attachments`, `content_types`, `language`).

## Verification

```powershell
Get-FileHash data\raw\meajor_cleaned_preprocessed.parquet.gzip -Algorithm MD5
# expected: 78e397ad8447bcdba5a98097921ba8bd
```

The audit stage (`deceptive-email audit`) records SHA-256 and cross-checks the file
before any processing. Raw files must never be modified.

## Source-composition note (verified 2026-08-11)

The MeAJOR v2.0 dataset paper (arXiv:2507.17978) and the Zenodo record describe five
source corpora: TREC-2005, TREC-2006, TREC-2007 spam tracks, the Nazario phishing
corpus, and the Nigerian Fraud corpus. The downloaded release artifact
(`meajor_cleaned_preprocessed.parquet.gzip`, MD5 78e397ad8447bcdba5a98097921ba8bd)
was recounted and contains only:

```text
trec5    49583
trec7    44096
trec6    15005
None         1   (missing label; dropped by cleaning)
```

The Nazario and Nigerian Fraud corpora are absent from the release. This is a
data-release discrepancy, not a pipeline loss; no source rows were removed by our
processing. It is recorded in `outputs/audit/source_composition.json` and all study
claims are scoped to the three TREC sources actually present. The binary label is
interpreted as the TREC spam-track positive class, not a general "phishing" class.

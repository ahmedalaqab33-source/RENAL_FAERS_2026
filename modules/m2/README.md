# M2 — Synthetic Longitudinal Record Integrity Audit

Private healthcare data-engineering module derived from authentic Renal Safety Atlas audit logic. **Entirely artificial records; not FAERS ETL, source authentication, clinical validation or production certification. PUBLIC_RIGHTS_HOLD.**

Python standard library plus embedded SQLite provide streaming ingestion, strict era-specific schemas, lossless TEXT identities, source/chunk fingerprints, disk-backed global diagnostics, parent/child integrity and exact row conservation. No real records, drug names, reference vocabularies or research outputs are bundled.

## Reproduce

Tested locally with Python 3.12.14, SQLite 3.53.1, Windows x64. R is not required by the module; a separate private base-R check verified aggregate arithmetic only. No package installation is required.

From this directory, create an external work parent and new external destinations:

```text
python -c "from pathlib import Path; Path('../m2-work').mkdir(exist_ok=True)"
python -I m2_cli.py generate --output ../m2-input --rows 2000 --seed 1729
python -I m2_cli.py audit --input ../m2-input --output ../m2-output --work-dir ../m2-work --batch-size 64 --timeout 60
python -I test_m2.py --output ../m2-test-output
```

Paths may contain spaces when quoted. Generated input and output directories must be new; the work directory must exist outside input/code trees. The pipeline accepts only its exact two-file synthetic package contract, not RDS, FAERS archives or arbitrary database files. A synthetic label is a caller declaration, not an authenticity or privacy certificate: never relabel real data to feed this tool.

## What is implemented

- Separate legacy DEMO, modern DEMO and corresponding DRUG-style child schemas.
- Exact Unicode/TEXT identifiers, leading zeros retained; no trimming, case folding, Unicode normalization, numeric ID conversion or cross-namespace matching.
- Incremental JSONL reads, prepared SQLite inserts and bounded batches; no full-record population in Python memory. SQLite performs global grouping; chunk receipts stream directly to disk.
- Per-record canonical-value fingerprints, source-bound ordinal ranges, raw chunk SHA256 and an order-invariant multiset fingerprint.
- Stored duplicate occurrences, contradictory case/version mappings, cross-year identity groups, and orphan/ambiguous/unambiguous child counts.
- Invalid-row hash-only quarantine receipts and exact input/valid/quarantine/storage accounting. No winner selection, repair or case/cohort adoption.
- Cooperative output lock, staged directory finalization, deterministic aggregate products and cleanup on tested controlled failures. No checkpoint/resume.

See [contracts](CONTRACT.md), [architecture](ARCHITECTURE.md), [source provenance](SOURCE_PROVENANCE.md), [measured performance](PERFORMANCE.md) and [limitations](LIMITATIONS.md).

## Status and output contract

`CLEAN` exits 0 and includes `_SUCCESS`; allowed exact duplicates and cross-year reuse remain visible diagnostics. `QC_FINDINGS` exits 3 for conflicting mappings or orphan/ambiguous children and has no success marker. `INPUT_REJECTED` or `PROCESSING_FAILED` exits 2, never marks success, and distinguishes complete ingestion from partial processing. Preflight failure exits 2 without a completed output. Existing outputs are never intentionally overwritten.

Products: `audit.json`, `chunks.jsonl`, `quarantine.jsonl`, `OUTPUT_MANIFEST.json`, plus `_SUCCESS` only for a clean run. They contain counts, hashes and ordinals, not literal record IDs or private paths. Hashes are not a claim of anonymization for real records. Resource telemetry is returned separately on stdout and is not part of deterministic product hashes.

## Evidence boundary

31 local M2 unit/integration tests passed, including 19 schema/value subcases, an independent small in-memory grouping oracle, batch/order invariance, parameter binding, failure injection, timeout, locks and source preservation. Eight bounded synthetic benchmark runs used 2,000/10,000 rows, batch64/512, two repeats. No production-size, Linux, clean-environment or independent-human claim follows. Existing M1/QC tests were executed separately without modification; their counts are not M2 tests.

The original project scripts and databases were never executed or loaded. The historical 22 reports/98 drug occurrences remain untouched. All scientific/publication/independent-review restrictions and rejection of the old restricted canonical cohort remain. Source-specific public licensing approval for M2 has not been inferred from M1; no LICENSE or public release is granted here.

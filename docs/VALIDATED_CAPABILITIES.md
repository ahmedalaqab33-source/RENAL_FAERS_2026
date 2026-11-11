# Validated capabilities

| Capability | Executable evidence | Boundary |
|---|---|---|
| Count QC | `tools/release_qc.py`; `R/count_qc.R`; count suite | Artificial scalar counts; zero cells remain undefined |
| M1 sufficient-statistics validation | `python/m1_validator.py`, `R/validate_sufficient_statistics.R`; 186 parity comparisons | Observed-pair contract; not a cohort builder |
| M2 bounded streaming | `modules/m2/`; 31 synthetic tests | SQLite diagnostics; no clinical mapping |
| Aggregate metrics publication | `tools/build_project_metrics.py`; 10 regression tests | Requires separately reviewed aggregates; never establishes authority |
| Release integrity | `tools/ci_bootstrap.py`; exact-byte manifest | Synthetic component only |
| Private scale | [sanitized annual evidence](SCALE_EVIDENCE.csv), [case study](ENGINEERING_AT_SCALE.md) | Local evidence reconciliation, not public reconstruction of MASTER |

The public suite uses Python standard library and base R. Runtime targets are Python 3.12 and R 4.6.1; local verification uses Python 3.14.7 and R 4.6.1. No production-scale benchmark of the public modules is inferred from private processing.

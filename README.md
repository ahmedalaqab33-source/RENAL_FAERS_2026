# Renal Safety Atlas — Clinical Data Engineering and Statistical QC

Reproducible Python and R software for **synthetic count QC** and **sufficient-statistics data integrity** in pharmacoepidemiology engineering.

The initial 25-file synthetic QC component is public at commit
`e42ce89c10cf7f0d5b4f8c845a9ffa1bae3067ce`. This **unreleased private integration candidate** adds M1, an authentic contract extraction from the Atlas research code. No public update or hosted CI execution is claimed.

**SYNTHETIC / NOT FAERS:** all bundled fixtures are artificial. This executable component does not reproduce the full FAERS ETL, select real cohorts, resolve drug identities, validate signals, estimate patient risk or deploy clinical AI.

## Modules and maturity

| Module | What it does | Evidence boundary |
|---|---|---|
| Synthetic count QC | Strict scalar counts, ROR/PRR/Wald arithmetic on artificial tables; zero cells produce undefined estimates | Initial code public; local R/Python tests verified; no hosted CI claim |
| M1 sufficient-statistics contract | Exact schema, opaque IDs, observed-pair positivity, integer bounds, margins and shared N | Authentic source contract extracted and privately tested; this integration remains unreleased |
| Broader Atlas research | Source harmonization, identity, phenotype sensitivity, external knowledge concordance and exploratory representations | Private and scientifically conditional; not executed by these commands |

M1 does **not** calculate ROR, PRR, Fisher tests, BH/FDR or clinical signals. Both modules check engineering contracts; neither establishes clinical validity or independent human reproduction.

## Quick start

Use Python 3.12 and R 4.6.1, with `Rscript` on PATH or supplied explicitly. Only the Python standard library and base R are required; no pip or R package installation is needed. Local verification uses Windows, Python 3.12.14 and R 4.6.1. Linux and hosted Windows remain unverified.

Run from the component root, choosing a new external output directory whose parent exists:

```text
python -I run_demo.py --output ../count-demo-output --rscript Rscript
python -I run_m1_demo.py --output ../m1-demo-output --work-dir <existing-external-work-parent> --rscript Rscript
```

On Windows the explicit R work parent must contain no spaces. Quote interpreter/path arguments when needed. Component and output paths may contain spaces when a valid external work parent is supplied. No silent temporary-directory redirection is used. Destinations must be new and outside the source tree.

The count demo writes synthetic metric CSV/JSON and a manifest. The M1 demo calls the actual Python and R validators on the single bundled artificial fixture, verifies IDs, margins and N across languages, and writes `m1_validation.json` plus `OUTPUT_MANIFEST.csv`. It accepts no arbitrary dataset path and hard-codes no expected result table.

## Two explicit contracts

| Rule | Count QC | M1 |
|---|---|---|
| Counts | Plain finite nonnegative integer-valued scalars | Plain finite nonnegative integer-valued table columns/values |
| Bounds | Each cell and total <= 2^53-1 | Each count, margin and total <= 2^53-1; addition guarded before evaluation |
| `a=0` | Accepted; association values undefined | Rejected: historical observed-pair contract requires `a>0` |
| `b`, `c` or `d` zero | Accepted; association values undefined | Structurally accepted; no association estimates computed |
| Missing/Boolean/classed values | Rejected | Rejected; no silent coercion or imputation |
| IDs and margins | Not part of scalar API | Unique opaque string `pair_id`; exact `a+b=n_drug`, `a+c=n_event`; one shared N |

See [count contract](docs/COUNT_CONTRACT.md), [M1 API](docs/M1_CONTRACT.md) and [source provenance](docs/SOURCE_PROVENANCE.md). Numeric-looking IDs stay strings; rows are not independent patients or cases. M1 rejects empty tables and extra schema fields.

## Reproduce all local checks

```text
python -I tools/ci_bootstrap.py --output <new-external-output> --work-dir <existing-external-work-parent> --rscript Rscript
```

The bootstrap verifies the complete manifest, copies only its listed content to a temporary component path with spaces, and invokes `tools/run_all.py`. The dispatcher runs the unchanged count suite, complete M1 suite and coexistence/demo tests. Logs are external local diagnostics, not proposed export files.

Test categories stay separate: count QC has 13 original Python tests, 90 contract Python tests, 89 R cases, 36 runner tests and 8 CI guards; 15 metric, 89 classification, 40 numeric output comparisons and 3 repeated hashes. M1 has 65 shared cases in each language, 15 Python-native and 16 R-native cases, and 186 exact parity comparisons. Integration adds Python coexistence/failure tests, eight R coexistence checks and repeated M1 demo outputs. These counts are not a scientific validation score.

The [manual workflow](.github/workflows/synthetic-qc.yml) keeps its existing pinned actions, read-only permissions, Windows/Ubuntu targets and no-upload policy. Its bootstrap now selects the combined dispatcher. Workflow dispatch requires separate authorization; no passing badge or clean-environment success is asserted. See [CI contract](docs/CI_CONTRACT.md).

## Architecture, rights and limitations

See [architecture](docs/ARCHITECTURE.md) for actual executable boundaries. Functions do not load research data; fixture adapters read only bundled synthetic inputs. Outputs are deterministic on the tested runtime; cross-platform byte identity is not claimed.

Ahmed Alaqab confirmed ownership/licensing authority for both the original M1 source and extraction. [MIT](LICENSE) and [citation metadata](CITATION.cff) retain their confirmed author details. Citation version 0.1.0 is preserved from the baseline; no new release tag, publication date or DOI is invented for this unreleased integration. Software rights do not grant reference-data redistribution or institutional/clinical endorsement.

Scientific, publication and independent-review HOLDs remain. No supervised ML, causal estimation, real cohort reconstruction, reference mapping, manuscript editing or research-data release is performed. The rejected restricted canonical cohort is not reinstated. This is evidence of Clinical Data Engineering, Data Integrity, Statistical Quality Control and Reproducible Research, not a validated clinical product.

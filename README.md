# RENAL FAERS 2026 — Longitudinal Clinical Data Science and Reproducible Healthcare Data Engineering

> **Clinical Data Science research program:** The broader local Renal FAERS project targets **2004–2026 (23 calendar years; 2026 YTD)** across **DEMO, DRUG and REAC**, including data harmonization, frozen/master layers, lineage QA and planned pharmacovigilance analysis. **This public repository is the synthetic QC / data-engineering component, not the complete real-FAERS analysis pipeline or a certified scientific release.** See [Project scope, workstreams and evidence status](docs/CLINICAL_DATA_SCIENCE_PROJECT_PROFILE.md).


Reproducible Python and R software for **synthetic count QC** and **sufficient-statistics data integrity** in pharmacoepidemiology engineering.

The QC and M1 baseline is public at commit
`9cde735a1baa01bfaa4066dce2ef72059f710b74`. The current integration component includes the bounded M2 streaming/SQLite module. Its tests demonstrate synthetic engineering behavior; they do not certify the private research pipeline.

**SYNTHETIC / NOT FAERS:** all bundled fixtures are artificial. This executable component does not reproduce the full FAERS ETL, select real cohorts, resolve drug identities, validate signals, estimate patient risk or deploy clinical AI.

## Modules and maturity

| Module | What it does | Evidence boundary |
|---|---|---|
| Synthetic count QC | Strict scalar counts, ROR/PRR/Wald arithmetic on artificial tables; zero cells produce undefined estimates | Initial code public; local R/Python tests verified; no hosted CI claim |
| M1 sufficient-statistics contract | Exact schema, opaque IDs, observed-pair positivity, integer bounds, margins and shared N | Authentic source contract extracted; baseline public; local synthetic tests verified |
| M2 streaming/SQLite diagnostic | Bounded synthetic JSONL validation, namespace-preserving storage, conservation, quarantine and aggregate linkage diagnostics | Existing module integrated privately; local tests verified; no clinical mapping or production-scale claim |
| Broader Atlas research | Source harmonization, identity, phenotype sensitivity, external knowledge concordance and exploratory representations | Private and scientifically conditional; not executed by these commands |

M1 does **not** calculate ROR, PRR, Fisher tests, BH/FDR or clinical signals. All three modules check engineering contracts; none establishes clinical validity or independent human reproduction.

## Quick start

The hosted workflow specifies Python 3.12 and R 4.6.1, with `Rscript` on PATH or supplied explicitly. Only the Python standard library and base R are required; no pip or R package installation is needed. The 2026-11-07 full local verification used Windows, Python 3.14.7 and R 4.6.1. This run does not verify Linux or hosted Windows.

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

The [manual workflow](.github/workflows/synthetic-qc.yml) keeps its existing pinned actions, read-only permissions, Windows/Ubuntu targets and no-upload policy. Its bootstrap selects the combined dispatcher. The separate [project metrics workflow run 42334289294](https://github.com/ahmedalaqab33-source/RENAL_FAERS_2026/actions/runs/42334289294) succeeded for PR #1 at `7572648`; that result covers the earlier five metrics tests only. Full hosted integration remains NOT_TESTED for this change. See [CI contract](docs/CI_CONTRACT.md).

The full local dispatcher also runs ten aggregate-publisher tests. These reject extra CSV row fields and protect existing output artifacts. The release manifest covers the complete checkout excluding Git metadata; the content screen permits only the two explicitly named workflows. Regenerate and review the manifest after any source change before running the bootstrap.

The repository's `.gitattributes` preserves exact bytes across checkouts, preventing line-ending conversion from invalidating release hashes. Historical [run 40162390177](https://github.com/ahmedalaqab33-source/RENAL_FAERS_2026/actions/runs/40162390177) failed with a Windows source-manifest mismatch and an Ubuntu runner-suite failure. The historical Ubuntu log does not identify the failing assertion; bounded child-log tails now surface future failures. Neither platform is certified by the local Windows run.

## Architecture, rights and limitations

See [architecture](docs/ARCHITECTURE.md) for actual executable boundaries. Functions do not load research data; fixture adapters read only bundled synthetic inputs. Outputs are deterministic on the tested runtime; cross-platform byte identity is not claimed.

Ahmed Alaqab confirmed ownership/licensing authority for both the original M1 source and extraction. [MIT](LICENSE) and [citation metadata](CITATION.cff) retain their confirmed author details. Citation version 0.1.0 is preserved from the baseline; no new release tag, publication date or DOI is invented for this unreleased integration. Software rights do not grant reference-data redistribution or institutional/clinical endorsement.

Scientific, publication and independent-review HOLDs remain. No supervised ML, causal estimation, real cohort reconstruction, reference mapping, manuscript editing or research-data release is performed. The rejected restricted canonical cohort is not reinstated. This is evidence of Clinical Data Engineering, Data Integrity, Statistical Quality Control and Reproducible Research, not a validated clinical product.


## Integrated streaming/SQLite module

QC and M1 remain separate from the bounded M2 synthetic streaming diagnostic. M2 preserves TEXT namespaces, physical occurrences and typed missingness; it never selects cases or derives drug ingredients. It requires base Python only; the full inherited verification additionally requires base R. All examples are synthetic, not FAERS.

From the repository root:

```sh
python -I modules/m2/m2_cli.py generate --output /temporary/new-input --rows 2000 --seed 1729
python -I modules/m2/m2_cli.py audit --input /temporary/new-input --output /temporary/new-output --work-dir /temporary/existing-work --batch-size 64
```

Replace paths with new external directories; create the work directory first. Windows accepts equivalent native paths. The combined runner requires a no-space Windows R work path, at least 1 GiB free disk for M2, and writes outside fixtures. Run `python -I tools/ci_bootstrap.py --output NEW_EXTERNAL_OUTPUT --work-dir EXISTING_EXTERNAL_WORK --rscript Rscript`. M2 finding exit 3 differs from processing failure exit 2; only clean complete runs return 0. See modules/m2/CONTRACT.md, PERFORMANCE.md and INTEGRATION_STATUS.md. Existing GitHub Actions invokes this dispatcher, but hosted execution is not certified by local tests.

No real FAERS ETL, approved cohort, clinical prediction, terminology corpus or scientific validation is included. Broader research and publication remain HOLD.

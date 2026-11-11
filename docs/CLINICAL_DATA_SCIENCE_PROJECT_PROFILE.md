# Renal FAERS 2026 — Clinical Data Science project profile

**Research direction:** longitudinal pharmacovigilance, large-scale observational safety data, reproducible clinical data engineering, real-world evidence, and statistical quality control.

**Project owner:** Ahmed Alaqab.

## Research scope versus public software scope

The broader local research program targets **23 calendar years (2004–2026, with 2026 year-to-date)** and three FAERS source-table families: **DEMO, DRUG and REAC**. This is the *intended/local research coverage*, not a claim that 23 years have passed end-to-end public reproducibility or scientific release checks. The actual available quarterly data, year completeness, and lineage must be verified against private source inventories and approved manifests.

This GitHub repository currently distributes a **synthetic-only reproducibility and quality-control component**, not the private full-scale FAERS pipeline or patient/report-level data. It provides:
- Strict typed-count validation and diagnostic ROR/PRR/Wald arithmetic on artificial counts, with undefined states handled explicitly.
- M1 sufficient-statistics validation: opaque identifiers, count bounds, margins, observed-pair rules, and cross-language R/Python consistency.
- M2 bounded synthetic streaming/SQLite diagnostics: namespace preservation, occurrence accounting, quarantine, conservation and aggregate linkage checks.
- Test fixtures, reproducibility contracts, a release manifest, and a manually triggered GitHub Actions workflow.

The distinction matters: **software quality assurance is not equivalent to drug-safety signal validation or clinical causal inference**.

## Broader local research workflow — evidence status

The local program has undertaken historical FAERS source harmonization, year-specific data partitioning, frozen datasets, master-table preparation, integrity checking, duplicate-resolution investigations, and lineage auditing. These activities are described as **local research work**, not functionality available for public execution from this repository.

| Workstream | Research purpose | Public reproducibility status |
| --- | --- | --- |
| 2004–2026 data inventory and source acquisition | Establish quarterly/yearly availability and provenance | Private source files and inventories are not shipped |
| DEMO/DRUG/REAC harmonization | Normalize year-specific schemas and identifiers without conflating legacy ISR/CASE/FOLL_SEQ with modern PRIMARYID/CASEVERSION | Full ETL not shipped |
| Frozen and master data layers | Create controlled analysis inputs with checksums and traceability | Real master datasets not shipped |
| Identity and duplicate resolution | Document report/case selection rules and ambiguous matches | Historical contributor policies and complete replay not publicly certified |
| Technical QA and audit | Hash verification, structural checks, reconciliation and scoped replay | Public tests are synthetic; local real-data audit is separate |
| Statistical signal analysis | Define reproducible denominator, cohort, drug-event and multiple-testing policies | Final scientific estimates not supplied here |
| Publication outputs | Produce traceable tables, figures, limitations and sensitivity analyses | Manuscript-ready outputs not certified by this repository |

**Known gate:** the local 2026-11-07 FAERS_07 audit produced 207 expected year/table/layer slots but selected **zero** authority-manifest files and loaded **zero** real data layers. That run is evidence of an unresolved audit configuration, **not** evidence that the underlying 2004–2026 data are absent or corrupt. Earlier local tests must be assessed separately, with their exact scopes and logs.

**Known historical concern:** for 2006 DEMO, a harmonized SOURCE candidate, a FROZEN candidate and a MASTER candidate have been located locally, but source-to-frozen-to-master historical contributor proof and the legacy selection policy require further validation. Do not equate current-file hash identity with historical provenance.

## What this demonstrates professionally

The **publicly inspectable evidence** supports software-engineering competencies in:
- R and Python data-validation contracts;
- reproducible analytical workflows and deterministic synthetic fixtures;
- cross-language parity, numerical correctness and boundary-condition testing;
- data lineage governance and cautious release criteria;
- streaming/SQLite data engineering and data-quality diagnostics.

The **broader private research program**, once supported by reviewed execution logs and analysis artifacts, can additionally demonstrate large-scale clinical data science, pharmacovigilance, real-world evidence and longitudinal research operations. Avoid claiming verified record counts, clinically validated signals, independently signed-off data or production deployment without matching evidence.

## Scientific release and next milestones

1. Reconcile the local project tree with the public GitHub component without exporting restricted source data, identifiers, access-controlled documents or paths.
2. Bind each year/table/layer to a reviewed authority manifest and independent reference identities.
3. Replay source-to-frozen and frozen-to-master transformations, with era-aware case/report identifiers and documented duplicate policies.
4. Run statistical analysis only on approved analysis-ready cohorts; preserve denominators, sensitivity analyses and limitations.
5. Freeze reviewed manuscript tables/figures and publish a data-free reproduction protocol or synthetic demonstration.
6. Obtain scientific sign-off separately from code/CI success.

**Current public scientific-release status: NOT CERTIFIED.** This document is a transparent scope and evidence map, not a claim of completed production deployment.

## Separate readiness gates — 2026-11-07

| Gate | Status | Executed evidence and limits |
| --- | --- | --- |
| SOFTWARE_READY | PASS | Scoped to the Windows synthetic component: full `tools/ci_bootstrap.py` execution with Python 3.14.7 / R 4.6.1; count QC, M1, M2, integration, cross-language parity and reproducibility checks pass. This is not a real-data production qualification. |
| DATA_READY | HOLD | FAERS_07 authority template contains no selected inputs. A targeted read of three 2006 DEMO candidates confirms readable structures but missing case identifiers in the MASTER candidate. Historical contributor replay and legacy selection policy remain unresolved. |
| SCIENTIFIC_READY | HOLD | The existing private signal script uses candidate-filtered Fisher tests followed by BH adjustment; the testing family needs protocol review before any global FDR claim. Lineage, cohort/denominator approval and independent scientific review remain required. No new real-data signal analysis was executed. |

The local SOURCE candidate in the 2006 check is an already harmonized RDS artifact, not independently verified original FDA source material. Structural checks and before/after byte preservation do not establish historical authority. No unreviewed local record counts are published as certified project-scale metrics.

## Update — 2026-11-10 (supersedes the status cells above; the 2026-11-07 record is kept unchanged for history)

| Gate | Status | New executed evidence and limits |
| --- | --- | --- |
| SOFTWARE_READY | PASS (synthetic component) | Full `tools/ci_bootstrap.py` passes on Windows (Python 3.14.7 / R 4.6.1) for fresh clones with `core.autocrlf` = true, false and input. The Unix `Rscript` space-path fix is included. **A hosted CI run is still to be recorded.** |
| DATA_READY (MASTER layer) | CONDITIONAL PASS | All 66 MASTER partitions (2004–2025) match their manifest MD5, and recomputed row counts equal the manifest (197,651,666 table rows). Zero DRUG/REAC orphans and zero within-year duplicate report IDs. Checked by machine reconciliation, not independent human review. **Historical source-to-frozen-to-master contributor replay remains open.** The 2005–2012 MASTER DEMO rows carry no case identifiers (2004 carries case IDs but no valid versions), so legacy years are report-level only. |
| SCIENTIFIC_READY | HOLD | The candidate-filtered BH procedure is replaced by a pre-specified family. An exploratory methods pilot (3 pre-specified drug–AKI pairs, 2013–2025, report- vs case-level) was executed and independently verified (481/481 checks). Endpoint, salt and deleted-case policies, the mapping accuracy review and independent scientific review are pending. **No results are released.** |

Engineering scale and verification detail: [Engineering at scale](ENGINEERING_AT_SCALE.md). The 2026 quarterly files are outside the frozen MASTER layer; the verified range is 2004–2025 (22 years).
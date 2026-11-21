# Engineering at scale: the private FAERS research pipeline

This page documents what the **private** real-data pipeline behind this repository has done, and how each claim was checked.
- **Aggregate counts only.** No FAERS records, identifiers or restricted files are distributed.
- **Not reproducible from this repository.** The real-data steps run privately, against frozen local data. Evidence for each claim was verified locally on 2026-11-09/10 by machine reconciliation (hashes, recomputed row counts, an independent re-implementation). **It has not been reviewed by an independent human.** The public, reproducible part is the synthetic test suite.
- **Units matter.** Rows are table rows. Reports, cases and patients are different units and are never interchanged.

## Verified scale (frozen MASTER layer, 2004–2025)

| Quantity | Value | How it was checked |
|---|---:|---|
| Calendar years | 22 (2004–2025) | Partition manifest |
| Frozen partitions | 66 (22 years × DEMO, DRUG, REAC) | MD5 of every partition equals the manifest (66/66), re-checked before and after every run |
| Table rows, all partitions | **197,651,666** | Recomputed per partition; equals the manifest in every one of 66 partitions |
| DRUG or REAC rows without a same-year DEMO report | 0 | Recomputed for all 22 years |
| Duplicate report identifiers within a year | 0 | Recomputed for all 22 years |

The total is a combined **row** count across three table families (one DEMO row per report; several DRUG and REAC rows per report). It is **not** a count of patients, cases or reports. 2026 quarterly files exist locally but are not part of the frozen MASTER layer.

### Rows per year (MASTER layer)

| Year | DEMO rows | DRUG rows | REAC rows |
|---|---:|---:|---:|
| 2004 | 220,838 | 786,583 | 809,461 |
| 2005 | 325,037 | 1,219,539 | 1,342,484 |
| 2006 | 323,207 | 1,206,429 | 1,388,276 |
| 2007 | 377,233 | 1,330,705 | 1,276,454 |
| 2008 | 439,437 | 1,560,702 | 1,577,656 |
| 2009 | 489,610 | 1,914,289 | 1,753,142 |
| 2010 | 671,572 | 2,528,856 | 2,442,444 |
| 2011 | 781,912 | 2,926,152 | 2,927,203 |
| 2012 | 592,991 | 2,199,896 | 2,175,840 |
| 2013 | 812,593 | 2,648,682 | 2,478,349 |
| 2014 | 903,174 | 2,955,862 | 2,710,862 |
| 2015 | 1,319,812 | 4,408,809 | 3,819,653 |
| 2016 | 1,304,885 | 4,751,135 | 3,781,407 |
| 2017 | 1,369,547 | 4,856,431 | 4,016,005 |
| 2018 | 1,684,852 | 6,873,089 | 5,179,161 |
| 2019 | 1,727,296 | 7,208,229 | 5,576,692 |
| 2020 | 1,757,369 | 7,582,432 | 5,931,221 |
| 2021 | 1,860,388 | 8,539,028 | 5,915,587 |
| 2022 | 1,827,391 | 7,664,005 | 5,993,396 |
| 2023 | 1,673,637 | 7,473,084 | 5,758,661 |
| 2024 | 1,619,664 | 7,695,043 | 5,712,042 |
| 2025 | 1,617,313 | 7,469,819 | 5,587,113 |
| **Total** | **23,699,758** | **95,798,799** | **78,153,109** |

## Technical challenges

| Problem | Scientific consequence | Implementation | Test evidence | Remaining limitation |
|---|---|---|---|---|
| FAERS stores follow-up versions of a case as separate reports | Report-level and case-level counts have different units | Global latest-version selection per case identifier; ties and invalid versions withheld and counted, never guessed | 22 synthetic unit tests; two implementations agree exactly on real data | Global selection has look-ahead, so it is not valid for annual trend estimates |
| Case histories span years and quarters | Selecting a version within each year leaves duplicate cases | Hash partitioning on the case identifier, so every version of a case lands in one partition (asserted) | Identical outputs at 4 partition settings | — |
| FDA publishes deleted-case lists (2019Q1 onward, including a cumulative list) that had never been applied | Deleted cases inflate counts | Lists read in place from source archives; two exclusion scopes kept as sensitivity populations | Overlap counts reproduced independently | Primary policy is a pending human decision |
| Legacy (2004–2012) records lack usable case versions | Case-level selection is impossible in that era | Legacy years analysed at report level only | Per-year identifier coverage audit | Era split |
| Renal terminology changes across historical versions | An as-coded endpoint can be era-dependent | Quantified per year; harmonisation deferred to licensed, local LLT→PT mapping | Per-year term counts for all 22 years | Endpoint definition pending clinical approval |
| Drug identity: missing canonical ingredients and separate salt strings | Unknown exposure and salt handling can affect comparator definition | Unknown exposure counted, never silently treated as known; strict vs salt-to-base variants, with the crosswalk checked against a pinned RxNorm release | Per-year category reconciliation; crosswalk complete and correct against RxNorm | Mapping accuracy review pending (human) |
| Laptop-class memory (16 GB) against tens of millions of rows | A naive pipeline cannot finish | One process per year and per case partition; durable checkpoints; validation before each checkpoint is accepted | Peak ≤ 0.36 GB per partition; restart test byte-identical | Upstream construction of MASTER is not version-controlled |
| Integer overflow in 2×2 products at full scale (a·d > 2³¹) | Ratio estimates silently returned as missing | All cells held in double precision; regression tests | Found by output inspection; fixed; zero impact on final outputs | — |
| Multiple testing was originally applied to a pre-filtered candidate set | False-discovery control does not hold | Hypothesis family fixed before any threshold | Synthetic null experiment; 8 tests | — |
| Bootstrap resampling can silently drop failed replicates | Over-confident intervals for sparse pairs | Failed replicates counted; interval marked not estimable | Wrapper tests; full-window run had 0 failures | Zero-cell rule pending statistician decision |

## Independent verification (real data, full 2013–2025 window)
The base-R verifier **agrees on 481 of 481 checks** with the production pipeline:
- 11 population and identity counts;
- 120 contingency-table cells;
- 240 ratio, interval, p-value and FDR values;
- 30 bootstrap pattern and interval checks;
- 78 per-year exposure counts;
- 2 integrity checks.

A deliberately corrupted copy is detected as a failure.

## What this page does not claim
- No signal, incidence, risk or causal estimate is reported here.
- The exploratory methods-pilot results are not published: they await clinical and methodological approval.

## Public evidence and limits

[SCALE_EVIDENCE.csv](SCALE_EVIDENCE.csv) is a sanitized projection of the local integrity summary: annual table-row counts and number of matching partition hashes only. It contains no report/case identifiers, terms, paths or effect estimates. On 2026-11-10 its 22 rows were reconciled with the local summary and the 66-row post-verification hash comparison. Totals are DEMO 23,699,758; DRUG 95,798,799; REAC 78,153,109; combined 197,651,666.

The local 481-row verifier agreement file was inspected: all 481 agreement flags are true. Only check counts are described here; private analytic values are withheld. The underlying evidence remains private, so public readers can verify summary arithmetic but cannot independently reproduce the real-data result from this repository. MD5 establishes identity against the frozen manifest; it does not authenticate FDA origin or historical transformations.

Memory observations describe private bucket workers, not end-to-end memory or a benchmark of public M2. Source-to-MASTER contributor replay, ingredient review, terminology approvals and independent human methods review remain open. Synthetic equivalence tests cover their fixtures; they are not a proof for every possible input.

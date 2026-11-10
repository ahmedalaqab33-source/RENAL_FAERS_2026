# Research methodology (private pipeline, summarised; no data, no results)

This document describes the methods of the private FAERS research pipeline that this public engineering repository supports. **No code, data or result from that pipeline is included here.** Nothing below is a validated clinical finding.

## Data model
- FDA AERS/FAERS quarterly ASCII releases, 2004–2025, harmonised into year-partitioned DEMO, DRUG and REAC tables. Each partition is frozen, with an MD5 manifest.
- Integrity checks run on every partition:
  - row counts against the manifest;
  - schema;
  - orphan keys (DRUG/REAC without DEMO);
  - duplicate report identifiers within a year;
  - input hashes before and after every run.

## Units of analysis
- **Report level (A):** one row per report identifier, keeping the latest source year.
- **Case level (B):** per case identifier, the single report at the maximum valid integer case version. Tied maxima and cases without a valid version are *withheld and counted*, never guessed.
- **Sensitivity populations:**
  - B minus version-history anomalies (C);
  - B minus FDA-published deleted cases. Two list scopes are implemented; the choice of primary policy is pending.
- Legacy (pre-2013) records lack usable case versions and are analysed at report level only. Selection is global over the analysis window, so it is not valid for annual or temporal estimates.

## Exposure
- **Exposure** = primary-suspect (PS) role AND a recorded canonical ingredient.
  - Raw drug names are never entities. There is no fuzzy matching and no string stripping.
  - Rows without a canonical ingredient are *unknown*: they are counted, and their effect on the comparator is reported.
- **Salt handling:** two pre-specified variants.
  - *strict*: exact canonical string.
  - *salt-to-base*: adds precise-ingredient forms linked to the ingredient in a pinned RxNorm release.
  - Neither variant is designated primary yet.

## Outcome
- **Methods pilot:** an exact, as-coded preferred term.
- MedDRA versions change term structure over time. An as-coded endpoint can therefore be structurally era-dependent. Version-linked LLT→PT harmonisation and clinical endpoint review are required before any non-pilot use.

## Statistics
- 2×2 tables are built from binary per-unit membership, which prevents join inflation. Every table satisfies the invariant a+b+c+d = N = population size.
- **Point and interval estimates:**
  - ROR and PRR with 95% Wald intervals. Any zero cell → not estimated; no continuity correction.
  - One-sided Fisher exact test.
  - Information component with closed-form shrinkage (IC025) as a sparse-data sensitivity.
- **Multiplicity:** Benjamini–Hochberg over a family fixed *before* any threshold. It is never applied to a pre-filtered candidate set.
- **Report vs case comparison:** a paired case-cluster Poisson bootstrap of log(ROR_B/ROR_A), with Bonferroni 98.33% intervals.
  - Replicate patterns are ordered canonically, for reproducibility.
  - Non-finite replicates are reported, never silently dropped. When any occur, the interval is *not estimable*.
- Disproportionality describes **reporting associations**. It does not estimate incidence, risk or causal effects.

## Engineering
- Bounded-memory execution: one process per source year and per case bucket, with hash-partitioned intermediates and durable aggregate checkpoints.
- Exact equivalence to the reference implementation is proven on synthetic data, and the reference real-data window was reproduced exactly.
- Independent re-implementation in base R checks the critical counts.
- Only aggregate outputs leave the restricted environment.

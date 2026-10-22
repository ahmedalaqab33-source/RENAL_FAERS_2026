# Renal Safety Atlas: Synthetic Count QC Demonstration

**Version 0.1.0 — private final candidate; public release and hosted CI are pending.**

A small Python and R research-software component for strict count validation,
explicit undefined states and cross-language numerical quality control.
**Every bundled example is SYNTHETIC / NOT FAERS.** This component is associated
with the broader Renal Safety Atlas research project; it is not its full
analytical pipeline or evidence of scientific validation.

## What runs

```text
Manifest-bound synthetic CSV (read-only)
  -> Python coordinator
  -> Python metrics + base-R worker
  -> parity and conservation checks
  -> new external CSV / JSON / output manifest
```

The functions calculate descriptive ROR, PRR and positive-cell Wald bounds for
artificial 2x2 tables. The runner accepts only the bundled named fixtures, not
arbitrary clinical data paths. It performs no dataset downloads or terminology
queries. See [count contract](docs/COUNT_CONTRACT.md).

## Prerequisites and installation

Use Python 3.12 and R 4.6.1 with an accessible `Rscript` executable. Only Python's
standard library and base R are needed: no pip or R package installation is
required. Place the exact manifest-bound component in a local directory and
make Python/Rscript available on PATH, or supply Rscript explicitly.

Actual local execution was tested on Windows with Python 3.12.14 and R 4.6.1.
The draft workflow targets Windows 2022 and Ubuntu 24.04; hosted Windows/Linux,
other runtime versions and clean-environment execution are not yet verified.
No passing hosted-CI badge is claimed.

## Run the demonstration

From the component root, with an existing writable parent and a new destination:

```text
python -I run_demo.py --output ../demo-output --rscript Rscript
```

Select the other bundled example with `--fixture synthetic_counts.csv` and a
different new output directory. Quote an installed executable path containing
spaces when supplying `--rscript`. From another working directory, supply the
script path and explicit output location. Existing destinations are rejected.

On Windows, R may fail before loading a script if its temporary parent contains
spaces. Supply `--work-dir <existing-external-no-space-directory>` when needed.
The work parent must be outside the component, without ancestor overlap; the
runner rejects unsafe paths rather than silently redirecting temporary files.
See [reproduction guide](docs/REPRODUCE_DEMO.md) for exact path and exit contracts.

Outputs are `synthetic_results.csv`, `summary.json` and `OUTPUT_MANIFEST.csv`.
They are synthetic engineering examples, not findings about drugs or patients.
Repeat runs on the same runtime are tested for byte/hash equality; cross-platform
bitwise equality is not promised. Outputs contain no timestamps or personal paths.

## Input and numerical contract

- Four plain finite, nonnegative integer-valued counts; Boolean/logical values,
  missing values, fractions, nonfinite values and ambiguous coercions are rejected.
- Every cell and total must be <= 2^53-1 (9007199254740991). The CSV interface
  accepts canonical unsigned decimal integers and unique synthetic labels only.
- Zero cells are accepted, but all association estimates remain UNDEFINED:
  unknown is never converted to FALSE or to a zero effect.
- Exact counts/states must agree; numerical comparisons use absolute and relative
  tolerance 1e-12. No continuity correction or multiplicity adjustment is added.

## Tests and local CI reproduction

Run the complete suite using the same bootstrap as the manual workflow:

```text
python -I tools/ci_bootstrap.py --output <new-external-output> --work-dir <existing-external-work-parent> --rscript Rscript
```

Use an explicit no-space work parent on Windows. The bootstrap checks the whole
manifest, copies only listed files into temporary isolated content and invokes
the existing functions. It does not initialize or inspect Git credentials.
The suite includes 13 original Python tests, 90 strict-count Python tests,
89 R cases, 36 runner tests and 8 CI-guard tests; it compares 15 original metrics,
89 classifications, 40 accepted outputs and 3 repeated output hashes. These
categories are separate; they are not a single scientific validation score.

See [CI contract](docs/CI_CONTRACT.md) and the
[manual workflow](.github/workflows/synthetic-qc.yml). Workflow permissions are
read-only, actions are commit-pinned, and no artifacts are uploaded. Workflow
activation requires separate approval. File isolation is not a fresh OS or
independent human replication. Local logs stay outside this export tree.

## Scope and limitations

This release candidate does not execute the full FAERS Atlas ETL, report/case
selection, drug identity recovery, real exposure/cohort construction, signal
recomputation, clinical prediction or phenotype adjudication. It contains no
real FAERS records, licensed terminology, reference crosswalks or scientific
manuscript results. Synthetic arithmetic checks do not establish clinical
validity, causation, incidence or patient risk. Broader scientific, publication
and independent-review restrictions remain unchanged. See
[presentation scope](docs/PRESENTATION_SCOPE.md).

## License and citation

The rights owner authorized [MIT](LICENSE), copyright 2026 Ahmed Alaqab, for
this private software candidate. The license does not confer rights to external
data, reference vocabularies, clinical use or institutional endorsement.
Software citation metadata is in [CITATION.cff](CITATION.cff). No DOI, journal
publication, affiliation or public release date is asserted. Public commit,
push and release of this exact candidate remain subject to explicit approval.

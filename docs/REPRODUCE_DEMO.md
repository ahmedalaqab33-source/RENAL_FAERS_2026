# Reproduce the synthetic demonstration

**SYNTHETIC / NOT FAERS.** No real research records, references, accounts or network access are required. This is engineering arithmetic, not a scientific pipeline or validated prediction.

From the component root, use the single Python coordinator:

```text
python -I run_demo.py --output ../demo-output --rscript Rscript
```

If Rscript is not on PATH, supply the quoted installed executable path as `--rscript`. From another working directory, use the script's path and an explicit external output path. Interpreter paths are caller-supplied, never embedded. The output directory must not already exist; its parent must exist. R is mandatory: unavailable or failed R is an error, never a skipped check.

Windows R may refuse a temporary path containing spaces before loading any script. For output paths containing spaces, explicitly add `--work-dir <existing-external-temporary-directory-without-spaces>`. R temporary files are then created only under that caller-designated work parent and removed on completion; final products remain only in the designated output directory. The runner never silently redirects temporary writes elsewhere. Component and working-directory paths may contain spaces. A missing/unsafe work parent or a Windows work path containing spaces fails clearly. With no work override, temporary files stay under output. This is a documented runtime constraint, not a claim of unrestricted platform portability.

Runtime prerequisites: Python 3 standard library, base R with an Rscript executable, and local read/write permissions. Actual same-host tests use Python 3.12.14 and R 4.6.1; other versions/platforms are not asserted verified. No package install is necessary. Clean OS/container and remote CI remain NOT TESTED.

Only `demo_counts.csv` (default) and `synthetic_counts.csv` may be selected with `--fixture`. The runner verifies the exact component manifest before reading a fixture. It accepts no arbitrary data path. CSV has exactly `synthetic_id,a,b,c,d`, unique artificial `SYNTHETIC_` labels, 1–32 rows and at most 16 KiB. Count fields are canonical unsigned decimal integers, not text booleans, blanks, NA/null strings, fractions, scientific notation or leading-zero alternatives. The underlying functions also support plain integer-valued floats as documented in COUNT_CONTRACT.md; this CSV interface is intentionally narrower. Cells and exact table total must be at most 2^53-1. No input missingness is imputed. Valid zero cells produce UNDEFINED association values, not FALSE or zero estimates.

Both existing computation functions are called: Python `tools/release_qc.py::metrics`, R `R/count_qc.R::metrics`. Exact counts and undefined states must agree; numerical ratios/bounds use absolute/relative 1e-12 tolerance. The coordinator writes only three final files in the designated output directory: synthetic_results.csv, summary.json and OUTPUT_MANIFEST.csv. Temporary R files stay under the output directory or the explicit external work parent and are removed. No source/fixture file is rewritten; existing output is never overwritten.

CSV is UTF-8 with LF newlines, preserved fixture order and explicit UNDEFINED tokens. JSON keys are sorted. Outputs contain no timestamp, host path or account data. Repeated same-runtime runs with identical inputs must have identical output bytes/hashes; cross-platform bitwise identity is NOT claimed. The summary binds the fixture hash and labels all outputs synthetic. The output manifest covers the other two files and excludes itself.

Exit 0 means scoped synthetic success; exit 2 indicates bad inputs, component integrity, paths or missing interpreter; exit 3 is worker execution failure; exit 4 is parity/conservation failure. Failed runs have no successful summary; an empty output directory may remain after a worker failure.

Ownership and MIT licensing are owner-confirmed for this private candidate; public distribution approval remains pending. Export only the reviewed component subtree, never private staging reports or audit logs. A Day 4 CI handoff is not a successful CI run.

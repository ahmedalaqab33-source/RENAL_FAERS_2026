# M1 API and exact table contract

Source only `R/validate_sufficient_statistics.R` or import `python/m1_validator.py`; call the pure `validate_sufficient_statistics` function on caller-owned in-memory values. Never source the original analytical script.

Required fields exactly: `pair_id,a,b,c,d,n_drug,n_event`. Order does not matter. Missing, duplicate or extra schema fields are rejected. Python requires a built-in list of built-in dictionaries. R requires a plain data.frame with plain character IDs and unclassed/attribute-free integer or double count columns, all of matching length. Each language rejects its own ambiguous containers/classes. Integral numeric floating values are supported; text is not silently converted by the functions.

IDs must be unique nonempty ASCII strings matching `[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}` absolutely, without whitespace/control suffixes or normalization. Numeric-looking IDs and leading zeros are preserved. No ID is interpreted as a patient, report or verified ingredient identity.

All six numeric fields must be finite, nonnegative integers <= 2^53-1. Missing, NaN/Inf, Boolean/logical, fractional, negative, classed or attributed values are rejected. M1 requires `a>0`; zeros in b/c/d remain structurally valid. Empty input is rejected. Extra schema fields are rejected as deliberate narrow-interface hardening.

Each addition is guarded before evaluation to keep the total exactly representable. Exact equalities: `a+b=n_drug`, `a+c=n_event`, and shared `N=a+b+c+d` across all rows. Output is acceptance metadata, row count, exact N and preserved IDs. No input mutation, file/network access or statistical estimation occurs inside the function. Exceptions carry deterministic error codes; the function does not repair data.

Python's oracle and R use different arithmetic implementations under the same declared bound. This is cross-language computational verification on one host, not independent human or clinical validation. Upstream rounding before input cannot be reconstructed. Historical invariant reuse and new hardening are distinguished in SOURCE_PROVENANCE.md.

The full synthetic suite uses two manifest-bound case-definition CSVs. Tests interpret typed tokens independently; the pure functions never read them. The fixture-only demo is `run_m1_demo.py`; it accepts only the bundled m1_demo.csv and requires R rather than silently skipping a language.

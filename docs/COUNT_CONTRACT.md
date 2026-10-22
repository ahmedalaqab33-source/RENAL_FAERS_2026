# Strict synthetic count contract

This component is a generic synthetic engineering utility. It does not process real research records.

Each of four cells must be a plain scalar nonnegative finite integer-valued number. Python accepts built-in int or float only; bool, subclasses and containers are rejected. R accepts attribute-free, unclassed integer or double vectors of length one; logical values, factors, dates, named/classed scalars, arrays and containers are rejected. Integer-valued floating inputs such as 1.0 are supported; text is never coerced by the metric function.

None/NULL, typed NA, NaN and infinities are invalid input, never zero, FALSE or imputed counts. Any zero cell is accepted but all four association estimates/bounds remain None in Python or typed numeric NA in R. N remains the exact table total. This conservative zero-state rule is preserved from the original utility; it is not an absence-of-signal classification.

Every cell and the table total must be at most 2^53-1 (9007199254740991). Larger counts/totals are rejected rather than silently rounded or coerced through floating integer identifiers. The total bound is a deliberate staged tightening beyond the original per-cell-only check. No arbitrary-precision or integer64 support is implied. R integer and double inputs are accepted within the same range, including values above the signed32-bit range. Classification and count comparisons are exact; ratio/bound comparisons use absolute/relative tolerance 1e-12.

ROR=(a*d)/(b*c); PRR=[a/(a+b)]/[c/(c+d)]. The strictly positive-cell Wald bounds use exp(log(ROR) +/- 1.96*sqrt(1/a+1/b+1/c+1/d)). Formulas are unchanged. No testing, multiplicity adjustment, prediction or clinical inference is implemented.

contract_cases.csv contains artificial type/value test definitions, not observations. Each language independently decodes its own native representation; typed missing variants map to None in Python and distinct R NA types. A separate Python-only test rejects an arbitrary-precision integer beyond the shared numeric range.

Use only the component file manifest as an intended export allowlist. Ownership and MIT licensing are owner-confirmed for this private candidate; public distribution approval remains pending; successful synthetic tests do not authorize publication.

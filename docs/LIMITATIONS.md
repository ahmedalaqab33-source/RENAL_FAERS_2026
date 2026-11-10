# Known limitations and open gates

## Of this repository
- Synthetic fixtures only. The contracts are tested, but clinical or scientific validity is not.
- Hosted CI is defined but has not been executed under a documented authorisation.
- Cross-platform byte identity is not claimed.

## Of the private research programme (no data disclosed)

| Area | Limitation | Gate |
|---|---|---|
| Source data | Spontaneous reports: under-reporting, stimulated reporting, duplicates, missing fields | Inherent; disclosed |
| Case selection | Global latest-version selection has look-ahead | Not used for temporal estimates |
| Deleted cases | FDA deletion lists were not applied in the frozen tables | Sensitivity populations; policy decision pending |
| Drug identity | Part of the primary-suspect records lacks a canonical ingredient; salts and combinations are separate strings | Mapping accuracy review and salt policy pending (human) |
| Route | Not available in the frozen tables | Open |
| Outcome | The as-coded renal endpoint depends on the MedDRA version | Endpoint approval and LLT→PT harmonisation pending (human) |
| Statistics | Sparse pairs give non-estimable intervals; no empirical-Bayes (EB05) sensitivity yet | Biostatistician decision pending |
| Reproducibility | The upstream construction of the frozen tables is provenance-tracked but not version-controlled | Open |

No clinical deployment, signal confirmation or causal claim is made or supported.

# Authentic source contract and new interface

M1 originates from `31_R2_V3_PRIMARY_PS_ROR_PRR_OVERFLOW_SAFE_PATCHED.R`, SHA256 `3c22bcbe839e55849e882789be3a71494056b1839f5bb5259bd58a555278c182`. This identifies inspected source bytes, not authenticated historical execution or clinical validity. The original script is not redistributed or executed here.

| Original block | Retained or adapted |
|---|---|
| Lines 45–48: required schema | Six numeric fields retained; historical identity columns replaced by an explicit opaque pair_id; exact narrow schema added |
| Lines 50–54: numeric casts | Replaced by strict native-type/value checks; no text/logical/class coercion |
| Lines 56–58: one pooled total | Preserved as exact shared-N conservation with pre-addition bounds |
| Lines 68–69: positive a, nonnegative b/c/d | Preserved; zeros in b/c/d allowed; all fields finite integers |
| Lines 70–72: drug/event margins and N | Preserved mathematically; exact integer equality replaces the historical tolerance |
| Data loading, printing, metric/tier sections | Excluded; new functions return metadata only |

The original had no named validator. `validate_sufficient_statistics` is a newly extracted reusable API. Empty-table rejection, duplicate/opaque-ID checks, ASCII/control boundaries, plain-container/type restrictions, extra-field rejection and the 2^53-1 exact bound are explicit engineering hardening, not retroactive scientific corrections.

The R function and Python reference oracle are byte-identical to the separately verified private M1 extraction. Both were developed under one specification and checked with independently decoded synthetic inputs; this is not independent human replication. Early private test-construction/identifier-hardening defects were corrected and retained in private audit history. No real source identifiers, drug strings or terminology lists are needed for this contract.

Ahmed Alaqab explicitly confirmed source/extraction ownership and licensing authority for this private MIT-compatible integration. No institutional ownership, hidden contributors or clinical/publication approval is inferred. The MIT software grant does not extend rights to external data or vocabularies. This integration is not yet publicly released.

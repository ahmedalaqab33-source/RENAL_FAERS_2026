# Limitations and open gates

- Entirely synthetic,cap-limited local engineering. No authentic source-level eligibility,report/case independence,drug identity,clinical signals,causality or patient risk is established.
- Schema era boundaries and parent-context equivalence are explicit illustrative engineering rules,not adopted study estimands or historical repair policies. The held22reports/98drugoccurrences are never loaded or changed.
- No checkpoint/resume,case selection,record repair or source normalization. Interrupted runs require a new output;partial coverage never becomes a completed audit.
- Controlled exceptions/timeouts close SQLite and remove owned temporary DB/staging/lock paths in tested scenarios. Hard process kill,power loss,external filesystem errors and hostile races may leave orphan staging/work/lock paths. Cleanup is not crash-proof;no automatic adoption/resume of remnants.
- Same-volume directory rename and cooperative lock protect normal publication of products. No durable power-loss/fsync-directory guarantee,adversarial concurrent-writer isolation or multi-host transaction is claimed. Existing destinations are rejected under the supported cooperative protocol.
- SQLite hard_heap_limit is process-wide and may affect other SQLite connections;run the standalone CLI in its own process. Global grouping may stop at configured memory/disk/time limits. There is no OS-level hard process-memory sandbox.
- Source/dataset hashes authenticate compared bytes,not provenance truth. A synthetic manifest is a declaration,not proof records are fictional;never feed real identifiers. Quarantine/source hashes are not anonymization guarantees.
- Exact canonical row-value duplicate fingerprints are distinct from raw-line byte hashes and from report/case identities. Duplicate diagnostics do not delete rows or choose a latest version.
- Peak memory/temp disk sampling can miss short-lived peaks;benchmarks are small,local,warm-cache possible,andnotstatisticallypowered. No production SLA or linear scale extrapolation.
- PUBLIC_RIGHTS_HOLD:source-specific ownership/contributor/license confirmation and exact-tree export approval required. No Git commit,push,dispatch or upload authorized. M1 approval does not cover M2 automatically.
- Scientific/publication/independent-review HOLDs,NO_GO_SUPERVISED_ML,STEP41_GO_DESIGN_ONLY and rejected restricted canonical cohort remain unchanged. Automated QC is not independent human review.

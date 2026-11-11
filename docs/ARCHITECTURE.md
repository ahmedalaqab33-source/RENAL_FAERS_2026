# Architecture and execution boundaries

```mermaid
flowchart TB
  subgraph PUBLIC["Public synthetic component"]
    M[Exact-byte manifest] --> B[Manifest-only temporary copy]
    B --> D[Combined dispatcher]
    D --> Q[Python and R count QC]
    D --> C[M1 table contract and parity]
    D --> S[M2 SQLite streaming diagnostics]
    D --> I[Integration and conservation checks]
    F[Artificial fixtures] --> Q & C
    G[Synthetic generator] --> S
    Q & C & S & I --> O[External test outputs]
    P[Reviewed aggregate input] --> T[Strict metrics publisher]
  end
  subgraph PRIVATE["Private research context — not executable here"]
    A[FDA source releases] --> H[Historical harmonization]
    H --> R[Frozen annual MASTER partitions]
    R --> W[Per-year workers and case buckets]
    W --> V[Checkpointed aggregates and independent verifier]
  end
```

The historical source-to-MASTER build lacks version-controlled replay. The private pipeline does not feed the public fixtures. Only a manually reviewed, sanitized engineering-scale summary is included in documentation.

Count QC and M1 are separate APIs with different zero-cell contracts. M2 preserves text namespaces and physical occurrences; it does not infer clinical entities. The dispatcher tests all modules and checks source immutability. The bootstrap rejects unlisted files and copies no Git metadata.

Source navigation: [count implementation](../tools/release_qc.py), [R count implementation](../R/count_qc.R), [M1 contract](M1_CONTRACT.md), [M2](../modules/m2/README.md), [metrics publisher](../tools/build_project_metrics.py), [test dispatcher](../tools/run_all.py).

The synthetic workflow runs manually and on pull requests, is read-only, action-pinned and uploads no artifacts. The metrics workflow tests pull-request changes. Hosted execution and local test results are separate evidence classes.

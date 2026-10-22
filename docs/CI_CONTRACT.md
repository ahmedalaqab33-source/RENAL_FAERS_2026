# Synthetic CI candidate contract

This is a locally reviewed workflow candidate, not evidence of a hosted workflow run. It contains synthetic engineering checks only. Ownership and MIT licensing are owner-confirmed for this private candidate; public upload approval remains pending.

The manual-only workflow targets windows-2022 and ubuntu-24.04, sets up Python3.12 and R4.6.1, and invokes tools/ci_bootstrap.py. Python patch resolution is intentionally recorded at execution; it is not a historical lock. R is an explicit target, not proof its remote installation succeeded. Action revisions are pinned to verified upstream40-character commit identities. Publisher descriptors and selected inputs were inspected; transitive action code has not received a complete security audit.

The bootstrap excludes only top-level Git metadata and rejects all other unlisted checkout content. It does not read or copy Git configuration/credentials, modify the checkout or run Git commands. Manifest-verified bytes are copied into a temporary component path containing spaces. The shared tools/run_ci.py executes tests against this clean payload copy. No claim of a fresh OS follows from this file isolation.

The suite executes inherited13 Python tests,90 strict-count Python tests,89 R cases,36 runner tests and8 CI guard tests. It independently compares15 original metrics,89 classifications and40 accepted outputs, runs the actual demo twice, verifies3 repeated output hashes and rechecks the exact component manifest/source bytes. Numerical/undefined semantics remain those of the existing computation functions. No formulas,fixtures,cohorts or scientific outcomes are changed by CI.

Supply an explicit existing external work parent without spaces on Windows; it becomes R's temporary parent and is never silently bypassed. The output is a new external directory. Per-command default timeout is180seconds (bounded1–300),total synthetic execution budget1000seconds,disk reserve256MiB; matrix parallelism2,job timeout20minutes. Child process trees are stopped on command timeout. Data size remains bounded by fixture contracts. Memory/CPU are runner-managed; no hard OS memory limit or full historical environment restoration is claimed.

Workflow permissions are contents:read only; checkout credential persistence is disabled. Trigger is workflow_dispatch only,with no custom inputs,privileged PR trigger,secrets,package caching or artifact upload. Rtools/package installs are disabled; setup installs only required runtimes. Runtime/action downloads are expected only in a future authorized hosted setup; local validation does not execute them. The test component performs no reference/dataset lookup or network request.

Local invocation after resolving Rscript:

```text
python -I tools/ci_bootstrap.py --output <new-external-output> --work-dir <existing-external-work-parent> --rscript Rscript
```

CI_SUMMARY.json describes only that execution's synthetic scope,not GitHub provenance. Test command logs may contain environment-specific paths and are local temporary diagnostics;the workflow uploads no artifacts. A genuine hosted PASS needs an authentic run URL,commit identity,platform/runtime versions,full job result and recorded failures. CLEAN_ENVIRONMENT_NOT_TESTED remains until such execution exists. No badge,publication clearance or independent scientific review is conferred by a draft or same-host run.


## Private M1 integration context

The initial synthetic QC baseline is already public. This new integration remains private and awaits exact-tree update approval. Both code scopes have owner-confirmed MIT-compatible rights. Existing count algorithms and workflow policies are unchanged. M1 has a distinct observed-pair a>0 contract; see M1_CONTRACT.md and ARCHITECTURE.md. The bootstrap now invokes tools/run_all.py to include the existing suite, complete M1 suite and integration checks. Hosted CI is not claimed.

# Public reproducibility

Use a fresh clone of the review branch, Python 3.12 or the locally checked 3.14.7, and base R 4.6.1. Put Rscript on PATH or supply its full executable path. No pip or R package installation is required.

From the repository root, create an external work directory, then run:

```sh
python -B -I tools/ci_bootstrap.py --output ../atlas-check-output --work-dir ../atlas-work --rscript Rscript
```

The output must not already exist; its parent must exist. On Windows choose a work directory without spaces. The bootstrap intentionally stages source under a path with spaces. Exit 0 and `INTEGRATED_SUMMARY.json` with zero failures identify scoped synthetic success. Count, M1, integration, M2 and cross-module logs remain outside the source tree; the metrics tests run inside the count dispatcher.

For a smaller public demonstration:

```sh
python -B -I run_demo.py --output ../atlas-count-output --rscript Rscript
```

See [detailed demo contract](REPRODUCE_DEMO.md), [CI contract](CI_CONTRACT.md) and [M2 usage](../modules/m2/README.md). The exact-byte manifest excludes itself and top-level Git metadata. Avoid unlisted local files in the checkout. If an older checkout retains converted line endings, preserve all work and use a fresh clone; do not discard changes to repair hashes.

The private full-scale pipeline is not reproducible from these commands. Its upstream source-to-MASTER build is not version-controlled. Local machine agreement and synthetic tests do not establish clinical validity or independent human review. Hosted workflow status must be checked for the exact proposed commit.

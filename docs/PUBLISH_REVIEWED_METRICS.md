# Publishing evidence-backed project scale safely

The public repository does not include raw FAERS data, restricted source manifests or historical lineage artifacts. To show the scale of the local research **without inventing numbers**, use a reviewed, aggregate-only CSV with the exact header:

```csv
year,table,records,scope,verified_by,evidence_id
```

Each row must be supported by a separately retained, independently reviewed local source. Use short opaque tokens for reviewer and evidence ID, not names, paths, emails or private file identifiers. Do **not** paste patient/report IDs or private source filenames. Do not equate records in DRUG or REAC with unique patients.

From the repository root:

```bash
python -m unittest discover -s tests -p 'test_project_metrics.py'
python tools/build_project_metrics.py --input reviewed_aggregates.csv --output project_metrics_preview.md
```

The script rejects unexpected columns, duplicate year/table/layer combinations, malformed counts, and unsafe reviewer/evidence tokens. It produces Markdown locally; it **does not push to GitHub**. Inspect the output, confirm evidence/permissions and then separately decide whether to publish it.

Do not treat a local FAERS_07 audit run with zero authority-selected files as a verified volume source. Use existing previously reviewed QC manifests only after reconciling their precise scope and authority. The 23-year figure describes the **target calendar-year range**, not 23 certified complete annual cohorts.

## What is needed to claim end-to-end production readiness

- A data-free, runnable orchestration entrypoint and documented dependency/environment lock;
- approved source/quarter inventory and per-layer identities;
- source-to-frozen-to-master replay and era-aware deduplication checks;
- analysis protocol, population and denominator definitions, uncertainty and multiplicity rules;
- synthetic end-to-end test plus real-data execution evidence held privately;
- independent scientific approval and publication traceability.

The current public repository is an engineering demonstration, not a verified production deployment or a completed drug-safety analysis.

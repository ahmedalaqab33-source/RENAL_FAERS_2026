#!/usr/bin/env python3
"""Validate a manually reviewed, aggregate-only FAERS project metrics CSV.

This utility never reads raw FAERS records or repository secrets. It produces
a local Markdown summary; the user must inspect and explicitly commit it.
Usage:
 python tools/build_project_metrics.py --input reviewed_metrics.csv --output project_metrics.md

CSV schema: year,table,records,scope,verified_by,evidence_id
- scope must be one of SOURCE,FROZEN,MASTER
- verified_by and evidence_id must be nonempty, non-sensitive attestations
- records must be nonnegative integers
- no individual IDs, paths or hashes are accepted in the CSV schema
"""
import argparse
import csv
import pathlib
import re
import sys

FIELDS = ["year", "table", "records", "scope", "verified_by", "evidence_id"]
TABLES = {"DEMO", "DRUG", "REAC"}
LAYERS = {"SOURCE", "FROZEN", "MASTER"}
TOKEN = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")


def render(input_path: pathlib.Path) -> str:
    if input_path.stat().st_size > 100_000:
        raise ValueError("Aggregate metrics input exceeds 100 KB")
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("Exact expected CSV columns: " + ",".join(FIELDS))
        rows = list(reader)
    if not rows:
        raise ValueError("No reviewed metrics supplied")
    if len(rows) > 207:
        raise ValueError("More than 207 year/table/layer rows")
    seen = set()
    parsed = []
    for row in rows:
        if any(value is None for value in row.values()):
            raise ValueError("Missing field")
        year_s, table, count_s, scope, reviewer, evidence = [row[k].strip() for k in FIELDS]
        if not (year_s.isdecimal() and 2004 <= int(year_s) <= 2026):
            raise ValueError("Invalid year")
        if table not in TABLES or scope not in LAYERS:
            raise ValueError("Invalid table or layer")
        if not count_s.isdecimal():
            raise ValueError("Record count must be a nonnegative integer")
        if not TOKEN.fullmatch(reviewer) or not TOKEN.fullmatch(evidence):
            raise ValueError("Reviewer/evidence fields require short opaque tokens")
        key = (int(year_s), table, scope)
        if key in seen:
            raise ValueError("Duplicate year/table/layer")
        seen.add(key)
        parsed.append((*key, int(count_s), reviewer, evidence))
    parsed.sort()
    lines = [
        "# Reviewed FAERS project volume — aggregate evidence",
        "",
        "> These counts are supplied by an external, manually reviewed aggregate manifest.",
        "> They are not independently verified by this script or the public repository.",
        "> A count is not proof of historical contributor lineage or clinical validity.",
        "",
        "| Year | Table | Layer | Records | Evidence ID | Reviewer token |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for year, table, layer, count, reviewer, evidence in parsed:
        lines.append(f"| {year} | {table} | {layer} | {count:,} | {evidence} | {reviewer} |")
    lines += [
        "",
        f"**Verified-input entries provided:** {len(parsed)} / 207 possible year/table/layer slots.",
        "",
        "**Interpretation:** Counts are layer-specific and MUST NOT be summed across",
        "SOURCE/FROZEN/MASTER as if they were distinct patients or reports.",
        "DEMO, DRUG and REAC are different table families, not disjoint patient cohorts.",
        "Coverage and completeness must be established independently.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    if args.output.resolve() == args.input.resolve():
        parser.error("Input and output must differ")
    try:
        result = render(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, f"Validation failed: {exc}\n")
    print(f"Created local reviewed-metrics preview: {args.output}")
    print("No Git operation performed; inspect before publishing.")


if __name__ == "__main__":
    main()

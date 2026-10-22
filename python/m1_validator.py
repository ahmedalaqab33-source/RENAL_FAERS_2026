"""Pure synthetic sufficient-statistics contract; no scientific estimation or IO."""
import math
import re

def validate_sufficient_statistics(rows):
    fields = {"pair_id", "a", "b", "c", "d", "n_drug", "n_event"}
    counts = ("a", "b", "c", "d", "n_drug", "n_event")
    limit = 2**53 - 1
    def fail(code):
        raise ValueError(code)
    if type(rows) is not list:
        fail("M1_E_CONTAINER")
    if not rows:
        fail("M1_E_EMPTY")
    for row in rows:
        if type(row) is not dict:
            fail("M1_E_CONTAINER")
        if any(type(k) is not str for k in row) or set(row) != fields:
            fail("M1_E_SCHEMA")
    ids = [row["pair_id"] for row in rows]
    if any(type(v) is not str for v in ids):
        fail("M1_E_ID_TYPE")
    if any(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}", v, flags=re.ASCII) is None for v in ids):
        fail("M1_E_ID")
    if len(set(ids)) != len(ids):
        fail("M1_E_DUPLICATE_ID")
    for row in rows:
        for name in counts:
            value = row[name]
            if type(value) not in (int, float):
                fail("M1_E_COUNT_TYPE")
            if value < 0 or value > limit or not math.isfinite(value) or value != math.floor(value):
                fail("M1_E_COUNT_VALUE")
    totals = []
    for row in rows:
        # Conversion is internal exact representation after strict validation.
        values = {name: int(row[name]) for name in counts}
        if values["a"] <= 0:
            fail("M1_E_A_POSITIVE")
        total = 0
        for name in ("a", "b", "c", "d"):
            if total > limit - values[name]:
                fail("M1_E_TOTAL_BOUND")
            total += values[name]
        if values["a"] + values["b"] != values["n_drug"]:
            fail("M1_E_MARGIN_DRUG")
        if values["a"] + values["c"] != values["n_event"]:
            fail("M1_E_MARGIN_EVENT")
        totals.append(total)
    if len(set(totals)) != 1:
        fail("M1_E_SHARED_N")
    return {"accepted": True, "row_count": len(rows), "N": totals[0], "pair_ids": ids.copy()}

#!/usr/bin/env python3
"""THE 2023 COHORT, SCORED AS OF 2023-10-31 AND JOINED TO THE AUTHORS' OUTCOME.

    python3 sources/build_hydrogen_cohort.py            # writes the csv, prints the tables
    python3 sources/build_hydrogen_cohort.py --check    # rebuilds and diffs

WHAT THE COHORT IS. Every EUROPEAN entry in the October 2023 vintage whose `Date online`
is 2023 -- 73 of them. They are joined to the ladder population by reference number, and
THE JOIN IS EMPTY: not one of the 73 is among the current vintage's 237, not one is a
register row, not one is a candidate, and not one was reached by the admission search of
10 September 2026. That zero is the first finding and it is a fact about the threshold:
none of the 73 reaches 100 MW on its own `Capacity_MWel`, and the ladder's population is
filtered to 100 MW. The cohort and the ladder are two populations that do not meet.

THE OUTCOME IS DERIVED, AND THE DERIVATION IS THIS REGISTER'S, NOT THE AUTHORS'.
`IEA_Hydrogen_Projects_Database_2023_only2023_outcome.xlsx` carries no outcome column.
What it publishes is the same 124 references with `Status` and `Date online` RESTATED
after a re-check whose quality-check references are dated `Checked on` 2024-07-30, plus a
comment per row. So the three classes the brief names are read off those two restated
columns by a rule stated here and nowhere else:

    on time       the restated row is `Operational` and its restated `Date online` is
                  2023 or earlier -- the project was announced for 2023 and was running.
    delayed       the restated row carries a `Date online` AFTER 2023, at any status,
                  including the six that reached `Operational` in 2024. It happened, late.
    disappeared   the restated row carries NO `Date online` at all. The authors took the
                  date off, and their own comment says why.
    not assessed  the reference is not in the outcome file at all.

AND `disappeared` IS NOT ONE THING, WHICH IS WHY EVERY ROW CARRIES THE AUTHORS' COMMENT.
Of the eight worldwide rows with no restated date, three are the authors REMOVING A
DUPLICATE -- "Very likely the same project as Strandmollen Ljungby", "the same project as
Energy Hub at MIRA Technology Park", "Original reference points to the same project as
Steinbeis Innovation Center Braunschweig" -- one is a misclassification they struck out
("not a specific electrolyser project, but a research institute"), and the rest are
projects that stopped ("Project rejected", "Archived - project did not progress"). A table
that counted all eight as failures would be counting the authors' housekeeping as
industrial attrition. The comment is carried on every cohort line so the reader can see
which is which, and the count is printed split.

THE SCORE IS THE LADDER'S, AS OF 2023-10-31, UNDER THE RUNG TESTS FROZEN AT COMMIT
a9542fe (DECISIONS D-B1). The evidence is the census pass of
sources/hydrogen_cohort_census.json, which preferred Wayback captures dated at or before
the cut-off precisely so that there would be something a 2023 reader could have held.

NO MODEL. The brief asks for the tables and nothing else: rungs cleared against outcome,
and IEA status against outcome, computed from the csv this file writes.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import build_hydrogen_drift as drift  # noqa: E402
import build_ladder as L  # noqa: E402
import hydrogen_cohort_census as census  # noqa: E402

ROOT = bench.ROOT
OUT = ROOT / "sources" / "ladder" / "cohort_2023.csv"
CENSUS = ROOT / "sources" / "hydrogen_cohort_census.json"
CUTOFF = "2023-10-31"
OUTCOMES = ("on time", "delayed", "disappeared", "not assessed")


def outcome_rows():
    """{ref: restated row} from the authors' outcome workbook, with its comments."""
    _refs, qc = census.sheets(census.OUTCOME)
    out = {}
    for r in drift.load_workbook_projects(census.OUTCOME):
        qids = re.findall(r"\[(\d+)\]", str(r["Refs (quality check)"] or ""))
        out[r["Ref"]] = {
            "status": str(r["Status"] or ""),
            "date_online": str(r["Date online"] or "").strip(),
            "comments": [dict(qc.get(i, {}), number=i) for i in qids],
        }
    return out


def classify_outcome(rec):
    """The rule stated in the module docstring, and nowhere else."""
    if rec is None:
        return "not assessed"
    d = rec["date_online"]
    if not d:
        return "disappeared"
    try:
        year = int(float(d))
    except ValueError:
        return "delayed"
    if rec["status"].strip().lower() == "operational" and year <= 2023:
        return "on time"
    return "delayed"


def score(entry, cutoff=CUTOFF):
    """The six rungs for one cohort entry, as of the cut-off.

    A COHORT ENTRY IS NOT A REGISTER ROW, so there is no row to read: the evidence is the
    census pass, exactly as score_unadmitted reads the admission search for an entry the
    register does not hold. Rung 1 asks whether an owner or permit source names the site;
    rungs 2, 3, 5 and 6 have no owner document on file and the census is the record of
    looking; rung 4 reads the funder pass, which covers this geography and this period.

    AND THE CUT-OFF IS APPLIED BY build_ladder.apply_cutoff, the same function the as-of
    ladder uses, so the two tables cannot answer the question differently.
    """
    readable = [f for f in entry["fetches"] if f["text_chars"] >= 400]
    pre = [f for f in readable if f["archived"] and f["captured_at"]
           and f["captured_at"] <= cutoff]
    best = pre[0] if pre else (readable[0] if readable else None)
    src = "sources/hydrogen_cohort_census.json"
    date = (best or {}).get("captured_at") or ""
    cells = {}
    if entry.get("verdict") == "names the site":
        # THE CELL CITES THE DOCUMENT THAT DOES THE NAMING, not whichever fetch happens to
        # sort first. The hand review records which one it was, and a pass whose source is
        # the wrong document is the h2v-fos shape arriving by another door.
        cells["site"] = L.cell(
            "pass", entry["site_fetch_url"], entry.get("site_speaker") or "owner",
            entry.get("site_captured_at") or date,
            "not_after" if entry.get("site_archived") else "day",
            f"census pass, hand verdict: {entry.get('site_named')}",
            captured_at=entry.get("site_captured_at"))
    elif best is None:
        cells["site"] = L.cell("fail", src, "eufabric cohort census", date or cutoff, "day",
                               "census pass: no reference of this entry answered a "
                               "declared reader")
    else:
        cells["site"] = L.cell("fail", best["read_url"], "eufabric cohort census", date,
                               "not_after" if best.get("archived") else "day",
                               "census pass: the sources read name no site at municipality "
                               "or finer", captured_at=best.get("captured_at"))
    for r in ("capacity", "fid", "start", "input"):
        cells[r] = L.cell("fail", (best or {}).get("read_url") or src,
                          "eufabric cohort census", date or cutoff,
                          "not_after" if (best or {}).get("archived") else "day",
                          "no owner document on file for this rung; the cohort census is "
                          "the record of looking",
                          captured_at=(best or {}).get("captured_at"))
    funder_by_key, funder_read, _ref = L.load_funder_pass()
    funder_on = (json.loads(L.FUNDERS.read_text(encoding="utf-8"))["read_on"]
                 if L.FUNDERS.exists() else "")
    fc = L.funder_cell(f"iea:{entry['ref']}", funder_by_key, funder_read, funder_on)
    cells["funding"] = fc or L.cell("fail", src, "eufabric cohort census", cutoff, "day",
                                    "no funder list read for this entry", searched=False)
    cut, _changed = L.apply_cutoff(cells, cutoff)
    return cut


FIELDS = (["iea_ref", "name", "country", "iea_status_2023_vintage", "technology",
           "capacity_value", "capacity_unit", "announced_size", "ou_outcome",
           "ou_restated_status", "ou_restated_date_online", "ou_comment",
           "in_current_iea_vintage", "in_ladder_population", "register_class",
           "census_searched", "readable_capture_at_or_before_cutoff",
           "rungs_cleared_as_of"]
          + [f"{r}_{f}" for r in L.RUNGS for f in ("result", "searched", "source",
                                                   "speaker", "date", "precision", "note")]
          + ["as_of"])


def build():
    doc = json.loads(CENSUS.read_text(encoding="utf-8")) if CENSUS.exists() else {"entries": []}
    by_ref = {e["ref"]: e for e in doc["entries"]}
    outc = outcome_rows()
    cur_pop = drift.population("iea_hydrogen_production_projects", None)
    cur_file = drift.whole_file(None)
    rowrefs, candrefs = drift.register_references()
    lines = []
    for e in census.cohort():
        rec = by_ref.get(e["ref"], {**e, "fetches": [], "verdict": None,
                                    "readable_at_or_before_cutoff": False})
        cells = score(rec)
        o = outc.get(e["ref"])
        comment = " | ".join(f"[{c.get('number')}] {c.get('comment','')}"
                             for c in (o or {}).get("comments", []) if c.get("comment"))
        line = {
            "iea_ref": e["ref"], "name": e["name"], "country": e["country"],
            "iea_status_2023_vintage": e["status_2023_vintage"],
            "technology": e["technology"],
            "capacity_value": e["capacity_mwel"] if e["capacity_mwel"] is not None else "",
            "capacity_unit": "MWel" if e["capacity_mwel"] is not None else "",
            "announced_size": e["announced_size"],
            "ou_outcome": classify_outcome(o),
            "ou_restated_status": (o or {}).get("status", ""),
            "ou_restated_date_online": (o or {}).get("date_online", ""),
            "ou_comment": comment,
            "in_current_iea_vintage": "yes" if e["ref"] in cur_file else "no",
            "in_ladder_population": "yes" if e["ref"] in cur_pop else "no",
            "register_class": ("admitted, a row here" if e["ref"] in rowrefs
                               else "candidate, not yet a row" if e["ref"] in candrefs
                               else "never seen by this register"),
            "census_searched": "yes" if rec.get("fetches") else "no",
            "readable_capture_at_or_before_cutoff":
                "yes" if rec.get("readable_at_or_before_cutoff") else "no",
            "as_of": CUTOFF,
        }
        passed = 0
        for r in L.RUNGS:
            c = cells[r]
            line[f"{r}_result"] = c["result"]
            line[f"{r}_searched"] = "true" if c.get("searched", True) else "false"
            line[f"{r}_source"] = c["source"]
            line[f"{r}_speaker"] = c["speaker"]
            line[f"{r}_date"] = c["date"]
            line[f"{r}_precision"] = c["precision"]
            line[f"{r}_note"] = c["note"]
            if c["result"] == "pass":
                passed += 1
        line["rungs_cleared_as_of"] = passed
        lines.append(line)
    return lines


def crosstabs(lines):
    a = defaultdict(Counter)
    for l in lines:
        a[l["rungs_cleared_as_of"]][l["ou_outcome"]] += 1
    b = defaultdict(Counter)
    for l in lines:
        b[l["iea_status_2023_vintage"] or "(none)"][l["ou_outcome"]] += 1
    return a, b


def render(a, b, rowlabel):
    cols = [c for c in OUTCOMES]
    w = max(len(rowlabel), *(len(str(k)) for k in a)) if a else len(rowlabel)
    out = [f"  {rowlabel:{w}} " + " ".join(f"{c:>14}" for c in cols) + f" {'total':>7}",
           "  " + "-" * (w + 1 + 15 * len(cols) + 8)]
    tot = Counter()
    for k in sorted(a, key=lambda x: (isinstance(x, str), x)):
        row = a[k]
        out.append(f"  {str(k):{w}} " + " ".join(f"{row[c]:>14}" for c in cols)
                   + f" {sum(row.values()):>7}")
        tot.update(row)
    out.append(f"  {'total':{w}} " + " ".join(f"{tot[c]:>14}" for c in cols)
               + f" {sum(tot.values()):>7}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not (drift.available() and CENSUS.exists()):
        # REPORTED, NOT FAILED, on the same reading build_ladder uses: the vintages are the
        # IEA's and are not redistributable, so on a build server they are not present and
        # the committed table stands. Their identity is in benchmark_snapshots.json.
        print("build_hydrogen_cohort: the cached vintages or the census are not on this "
              "machine,\n  so the cohort table is not recomputed. The committed file "
              "stands.")
        return 0
    lines = build()
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\r\n")
    w.writeheader()
    for l in lines:
        w.writerow(l)
    if a.check:
        with OUT.open(encoding="utf-8", newline="") as fh:
            cur = fh.read() if OUT.exists() else ""
        if buf.getvalue() != cur:
            print("build_hydrogen_cohort --check: sources/ladder/cohort_2023.csv is not "
                  "what the\n  cohort, the census and the outcome file produce. Run "
                  "build_hydrogen_cohort.py.")
            return 1
        print(f"build_hydrogen_cohort --check: {len(lines)} cohort entries, the table "
              f"matches its sources.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for l in lines:
            w.writerow(l)
    ca, cb = crosstabs(lines)
    print(f"THE 2023 COHORT: {len(lines)} European entries announced for 2023 in the "
          f"October 2023 vintage,\nscored as of {CUTOFF} under the rung tests frozen at "
          f"a9542fe.\n")
    print(f"  joined to the ladder population by reference: "
          f"{sum(1 for l in lines if l['in_ladder_population'] == 'yes')}")
    print(f"  still in the current IEA file at any size:    "
          f"{sum(1 for l in lines if l['in_current_iea_vintage'] == 'yes')}")
    print(f"  a register row or candidate:                  "
          f"{sum(1 for l in lines if l['register_class'] != 'never seen by this register')}")
    noref = [l for l in lines if l["census_searched"] == "no"]
    print(f"  searched by the cohort census:                {len(lines)}"
          f"  ({len(noref)} of them carry no http reference in the vintage, so there was\n"
          f"                                                   nothing of the publisher's "
          f"own to read: refs "
          + ", ".join(l["iea_ref"] for l in noref) + ")")
    print(f"  with a readable capture at or before the cut-off: "
          f"{sum(1 for l in lines if l['readable_capture_at_or_before_cutoff'] == 'yes')}")
    print(f"\nRUNGS CLEARED AS OF {CUTOFF} AGAINST THE AUTHORS' OUTCOME\n")
    print(render(ca, cb, "rungs"))
    print(f"\nIEA STATUS IN THE OCTOBER 2023 VINTAGE AGAINST THE AUTHORS' OUTCOME\n")
    print(render(cb, ca, "iea status"))
    unmatched = [l for l in lines if l["ou_outcome"] == "not assessed"]
    print(f"\n  NOT ASSESSED BY THE AUTHORS ({len(unmatched)}) — in the cohort, absent from "
          f"their outcome file:")
    for l in unmatched:
        print(f"    ref {l['iea_ref']:>5}  {l['country']}  {l['technology'][:18]:18} "
              f"{l['name'][:52]}")
    dis = [l for l in lines if l["ou_outcome"] == "disappeared"]
    if dis:
        print(f"\n  DISAPPEARED ({len(dis)}) — the authors took the online date off. Their "
              f"own comment says why,\n  and a comment that says 'the same project as' is "
              f"housekeeping and not attrition:")
        for l in dis:
            print(f"    ref {l['iea_ref']:>5}  {l['name'][:40]:42} {l['ou_comment'][:70]}")
    print(f"\n  -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

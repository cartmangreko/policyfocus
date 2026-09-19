#!/usr/bin/env python3
"""THE CONFIRMATION LADDER ACROSS FIVE SECTORS, brief 11.

    python3 sources/build_ladder_all.py            # writes both files, prints the tables
    python3 sources/build_ladder_all.py --check    # recomputes and refuses a difference
    python3 sources/build_ladder_all.py --queue    # what a rung revealed that a row lacks

Writes sources/ladder/all.csv -- the hydrogen shape plus a `sector` column, one line
per entry across all five populations -- and sources/ladder/all_summary.json, computed
FROM the csv and never alongside it.

THE RULES ARE IN scope.md, "The confirmation ladder", and the sector readings of the
frozen tests are the subsection under it. THE SIX TESTS ARE UNCHANGED: `### The six
rungs` is byte-identical to its text at the D-B1 freeze and check_ladder.py fails on a
difference.

HYDROGEN'S LINES ARE NOT RESCORED HERE. They are build_ladder.build()'s own output,
imported. That is what makes "the hydrogen files must reconcile line by line with
hydrogen's rows in all.csv" true by construction rather than by a coincidence two
scorers happened to agree on -- and the gate checks it anyway, because a construction
that is never checked is a claim.

WHAT IS SCORED AND WHAT IS NOT. Three parts, on D-L1: perimeter exclusions are carried
with their clause and not scored, unread entries are counted and not scored, and the
rest are the scored population. A project this dataset is not about cannot fail to
confirm itself.

RUNG 4 IS SEARCHED EVERYWHERE NOW. sources/funder_pass.json reads the Innovation Fund's
own project table -- 413 projects, every call, every sector -- and 163 of its factsheets;
sources/hydrogen_funder_pass.json covers hydrogen as brief 12 left it. Once a list is
read, absence from it is a fail and not a not_searched.

RUNG 6 IS PROVISIONAL EVERYWHERE, and in two sectors it is mostly not searched. Every
edge in sources/edges.json carries `verdict: null`, so every rung 6 result is
`provisional: true`. And the dependency sweep of brief 9 covered all 66 hydrogen rows,
32 of 33 battery rows and all 8 steel rows, but only 8 of 34 cement rows and 3 of 43
transport-and-storage rows -- so most of those two sectors' rung 6 cells are
`not_searched`, which is a statement about brief 9's reach and not about the plants.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ladder as L  # noqa: E402
import ladder_population as lp  # noqa: E402
import sector_map as sm  # noqa: E402

ROOT = lp.ROOT
OUTDIR = ROOT / "sources" / "ladder"
CSV = OUTDIR / "all.csv"
SUMMARY = OUTDIR / "all_summary.json"
FUNDERS = ROOT / "sources" / "funder_pass.json"

RUNGS = L.RUNGS
SECTORS = lp.SECTORS

FIELDS = (["sector", "key", "list_key", "row_id", "name", "country", "register_class",
           "list_status", "capacity_value", "capacity_unit", "perimeter_clause",
           "rungs_passed", "scored", "unread"]
          + [f"{r}_{f}" for r in RUNGS
             for f in ("result", "searched", "source", "speaker", "date",
                       "precision", "note")]
          + ["input_provisional"])


# --------------------------------------------------------------------------
# RUNG 4 -- the funder pass, across sectors


def funder_index():
    doc = json.loads(FUNDERS.read_text(encoding="utf-8"))
    by_key = defaultdict(list)
    for a in doc["awards"]:
        by_key[a["population_key"]].append(a)
    return by_key, doc["read_on"]


def funding_cell(key, by_key, read_on):
    hit = (by_key.get(key) or [None])[0]
    if hit:
        return L.cell("pass", hit["source_url"], hit["funder"], hit["date"],
                      hit["date_precision"],
                      f"{hit['programme']} names {hit['project_as_published']!r} at "
                      f"{hit['amount_as_stated']}; the funder's own status is "
                      f"{hit['funder_status_as_published']}; matched on "
                      f"{hit['matched_on']}")
    return L.cell("fail", "sources/funder_pass.json", "eufabric funder pass", read_on,
                  "day", "the funder lists of sources/funder_pass.json — the Innovation "
                  "Fund's own project table of 413 projects and 163 of its factsheets — "
                  "name no award for this entry", searched=True)


# --------------------------------------------------------------------------
# RUNG 6 -- the dependency graph, per sector


def graph():
    edoc = json.loads(L.EDGES.read_text(encoding="utf-8"))
    by_project = defaultdict(list)
    for e in edoc["edges"]:
        if e.get("project_id"):
            by_project[e["project_id"]].append(e)
    swept = {o["project_id"] for o in edoc.get("owner_side", [])}
    return by_project, swept, L.graph_read(edoc)


def input_cell(row, row_id, by_project, swept, graph_date):
    """RUNG 6. `contract` passes; `framework` and `intent` fail; and a row the
    dependency sweep never reached is `not_searched`, not a fail.

    THE SWEEP'S REACH IS PART OF THE ANSWER. Brief 9 read the owner side of 117
    projects and recorded each in `owner_side`; a row outside that list has had no
    supplier question asked of it, and D-L2 is explicit that "nobody looked" and
    "there is nothing there" are different findings.
    """
    if row is not None and row_id in swept:
        return L.score_input(row, by_project, graph_date)
    if row is not None:
        c = L.cell("fail", "sources/edges.json", "eufabric dependency sweep", graph_date,
                   "day", "the dependency sweep of brief 9 did not reach this row: it is "
                   "not in `owner_side`, so no supplier question has been asked of it",
                   searched=False)
        c["provisional"] = True
        return c
    c = L.cell("fail", "sources/edges.json", "eufabric dependency sweep", graph_date,
               "day", "no register row, so no owner side to sweep; the graph names no "
               "edge for this entry", searched=False)
    c["provisional"] = False
    return c


# --------------------------------------------------------------------------
# SCORING AN ENTRY THAT IS NOT A ROW


CENSUS_SOURCE = {
    "batteries": "sources/batteries_benchmark.json",
    "cement": "sources/cement_ccs_entries.json",
    "transport and storage": "sources/cement_ccs_entries.json",
    "steel": "sources/steel_entries.json",
}
CENSUS_DATE = {"batteries": "2026-09-12", "cement": "2026-09-15",
               "transport and storage": "2026-09-15", "steel": "2026-09-18"}


def score_entry(e, sector, by_key, read_on, by_project, swept, graph_date):
    """Six cells for an entry with no register row behind it.

    THE CENSUS IS THE EVIDENCE EXAMINED, so the census is what a fail cites. The
    classes mean what the censuses made them mean:

      `named not admitted`  an owner or permit source NAMES the site and the
                            perimeter still refuses it -- rung 1 passes and the
                            other owner-statement rungs have no document
      `searched none found` the owner's own sources were read and say nothing
      `unreadable`          the publisher could not be read: `unread` on all six
      `perimeter exclusion` not scored at all, the clause travels instead
      `benchmark aggregate` a list line that is not one works: not scored
    """
    src = CENSUS_SOURCE[sector]
    on = CENSUS_DATE[sector]
    klass = e["register_class"]
    if klass == "unreadable":
        return {r: dict(L.UNREAD, note="the publisher could not be read; queued for a "
                        "browser pass") for r in RUNGS}
    if klass in ("perimeter exclusion", "benchmark aggregate", "not searched"):
        why = ("out of perimeter; not scored" if klass == "perimeter exclusion" else
               "a list line that is not one works; not scored" if klass == "benchmark aggregate"
               else "the census did not search this entry")
        return {r: L.cell("not_searched", src, "eufabric census", on, "day", why,
                          searched=False) for r in RUNGS}
    out = {}
    if klass == "named not admitted":
        out["site"] = L.cell("pass", e.get("site_source") or src,
                             e.get("site_speaker") or "owner or permit source",
                             on, "day",
                             "the census read an owner or permit source that names the "
                             "site and the perimeter still refuses the entry")
    else:
        out["site"] = L.cell("fail", src, "eufabric census", on, "day",
                             "the census read the owner's own sources and none names a "
                             "site for this project")
    for r in ("capacity", "fid", "start"):
        out[r] = L.cell("fail", src, "eufabric census", on, "day",
                        "no owner document on file; the census is the record of looking")
    out["funding"] = funding_cell(e["key"], by_key, read_on)
    out["input"] = input_cell(None, "", by_project, swept, graph_date)
    return out


# --------------------------------------------------------------------------


def line_for(sector, e, cells, row):
    cap_v = cap_u = ""
    if row is not None:
        cap_v = row.get("capacity_value") if row.get("capacity_value") is not None else ""
        cap_u = row.get("capacity_unit") or ""
    for c in e.get("list_claims") or []:
        if not cap_v and c.get("capacity_as_published"):
            cap_v, cap_u = c["capacity_as_published"], c.get("capacity_unit", "")
    status = ""
    for c in e.get("list_claims") or []:
        status = status or c.get("iea_status") or c.get("project_status") or ""
    line = {"sector": sector, "key": e["key"], "list_key": e["key"].split(":", 1)[-1]
            if ":" in e["key"] else "", "row_id": e.get("row_id", ""),
            "name": e.get("name", ""), "country": e.get("country", ""),
            "register_class": e["register_class"], "list_status": status,
            "capacity_value": cap_v, "capacity_unit": cap_u,
            "perimeter_clause": e.get("clause", "")}
    passed = 0
    for r in RUNGS:
        c = cells[r]
        line[f"{r}_result"] = c["result"]
        line[f"{r}_searched"] = "true" if c.get("searched", True) else "false"
        for f in ("source", "speaker", "date", "precision", "note"):
            line[f"{r}_{f}"] = c[f]
        if r == "input":
            line["input_provisional"] = "true" if c.get("provisional") else "false"
        if c["result"] == "pass":
            passed += 1
    line["rungs_passed"] = passed
    line["unread"] = "true" if all(cells[r]["result"] == "unread" for r in RUNGS) else "false"
    line["scored"] = "false" if (line["register_class"] in lp.NOT_SCORED
                                 or line["register_class"] == "benchmark aggregate"
                                 or line["unread"] == "true") else "true"
    return line


HYDROGEN_CSV = OUTDIR / "hydrogen.csv"


def hydrogen_lines():
    """HYDROGEN'S LINES ARE READ FROM sources/ladder/hydrogen.csv, NOT RESCORED.

    The first draft of this file called build_ladder.build() instead, which was
    wrong twice over and the second reason is the one that matters.

      *It disagreed.* `perimeter_exclusions_by_ref()` reads the IEA benchmark
      workbook, which is gitignored; on a machine without it the classifier
      returns nothing and all 53 hydrogen perimeter exclusions come out as
      `none found` — scored, and scored zero. The table said 224 hydrogen
      entries were scored where the committed one says 171, and every hydrogen
      pass rate in the cross-sector table was computed over the wrong
      denominator.

      *And it could never run on the build server.* scope.md, "A build-time gate
      reads tracked files only": a step wired into prebuild may not open a
      workbook. Rescoring hydrogen here would have put one in the chain.

    THE COMMITTED CSV IS THE DERIVED FILE AND IT IS TRACKED. build_ladder.py
    --check reconciles it against its own sources on a machine that holds them,
    and that is where the recomputation belongs. Here it is read, and the
    reconciliation gate then compares what this file wrote back to it — which
    is a real check precisely because the two files are written by different
    code paths.
    """
    out = []
    with open(HYDROGEN_CSV, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            n = {"sector": "hydrogen", "key": l["key"], "list_key": l["iea_ref"],
                 "row_id": l["row_id"], "name": l["name"], "country": l["country"],
                 "register_class": l["register_class"], "list_status": l["iea_status"],
                 "capacity_value": l["capacity_value"],
                 "capacity_unit": l["capacity_unit"],
                 "perimeter_clause": l["perimeter_clause"],
                 "rungs_passed": int(l["rungs_passed"]), "unread": l["unread"]}
            for r in RUNGS:
                for f in ("result", "searched", "source", "speaker", "date",
                          "precision", "note"):
                    n[f"{r}_{f}"] = l[f"{r}_{f}"]
            n["input_provisional"] = l["input_provisional"]
            # `unread` is a register class in the hydrogen table and a cell state
            # here; both mean the same thing and the scored flag reads either.
            n["scored"] = "false" if (n["register_class"] in lp.NOT_SCORED
                                      or n["register_class"] == "unread"
                                      or n["unread"] == "true") else "true"
            out.append(n)
    return out


def reconcile_hydrogen(lines):
    """THE GATE THE BRIEF ASKS FOR: hydrogen's rows in all.csv must match
    sources/ladder/hydrogen.csv line by line."""
    problems = []
    mine = [l for l in lines if l["sector"] == "hydrogen"]
    with open(HYDROGEN_CSV, newline="", encoding="utf-8") as fh:
        theirs = list(csv.DictReader(fh))
    if len(mine) != len(theirs):
        problems.append(f"all.csv carries {len(mine)} hydrogen lines, hydrogen.csv "
                        f"has {len(theirs)}")
        return problems
    shared = ["key", "row_id", "name", "country", "register_class", "rungs_passed",
              "unread"] + [f"{r}_{f}" for r in RUNGS
                           for f in ("result", "searched", "source", "speaker",
                                     "date", "precision", "note")]
    for a, b in zip(mine, theirs):
        if a["key"] != b["key"]:
            problems.append(f"order differs: {a['key']} vs {b['key']}")
            break
        for k in shared:
            if str(a.get(k, "")) != str(b.get(k, "")):
                problems.append(f"{a['key']} field {k}: all.csv {a.get(k)!r} vs "
                                f"hydrogen.csv {b.get(k)!r}")
    if not problems:
        s = json.loads((OUTDIR / "hydrogen_summary.json").read_text(encoding="utf-8"))
        n = sum(1 for l in mine if l["scored"] == "true")
        if n != s["population_structure"]["scored"]:
            problems.append(f"all.csv scores {n} hydrogen entries; "
                            f"hydrogen_summary.json says "
                            f"{s['population_structure']['scored']}")
        if len(mine) != s["population"]:
            problems.append(f"all.csv carries {len(mine)} hydrogen entries; "
                            f"hydrogen_summary.json says {s['population']}")
    return problems


def build():
    by_key, read_on = funder_index()
    by_project, swept, graph_date = graph()
    rows = {p["id"]: p for p in sm.load("project")}
    funding_by_project = L.load_funding()
    hyd_funder, hyd_read, _ = L.load_funder_pass()

    lines = hydrogen_lines()
    parts = {"hydrogen": {"population": sum(1 for l in lines if l["sector"] == "hydrogen"),
                          "note": "built by sources/build_ladder.py (brief 10)"}}
    for sector in SECTORS:
        if sector == "hydrogen":
            continue
        pop, p = lp.BUILDERS[sector]()
        parts[sector] = p
        for e in pop:
            row = rows.get(e["row_id"]) if e.get("row_id") else None
            if row is not None and e["register_class"] not in ("perimeter exclusion",):
                cells = L.score_row(row, by_project, graph_date, funding_by_project,
                                    {}, False, "", e["key"])
                cells["funding"] = funding_cell(e["key"], by_key, read_on)
                cells["input"] = input_cell(row, e["row_id"], by_project, swept, graph_date)
            else:
                cells = score_entry(e, sector, by_key, read_on, by_project, swept,
                                    graph_date)
            lines.append(line_for(sector, e, cells, row))
    return lines, parts


# --------------------------------------------------------------------------


def summarise(lines, parts):
    """COMPUTED FROM THE CSV'S OWN LINES, so the two files cannot disagree."""
    out = {"_comment": [
        "COMPUTED FROM sources/ladder/all.csv BY build_ladder_all.py. Never edited by",
        "hand: --check recomputes it and refuses a mismatch.",
        "",
        "THREE POPULATIONS PER SECTOR AND ONLY ONE IS SCORED, on D-L1. A perimeter",
        "exclusion is a project the dataset is not about and an unread entry is a",
        "publisher this register could not reach; neither failed to confirm itself.",
        "",
        "EVERY RUNG 6 RESULT IS PROVISIONAL while `verdict` is null on every edge in",
        "sources/edges.json. The count is per sector and is printed, not buried."],
        "sectors": {}, "cross_sector": {}}
    for s in SECTORS:
        ls = [l for l in lines if l["sector"] == s]
        scored = [l for l in ls if l["scored"] == "true"]
        excluded = [l for l in ls if l["register_class"] in lp.NOT_SCORED]
        unread = [l for l in ls if l["unread"] == "true"
                  or l["register_class"] == "unread"]
        agg = [l for l in ls if l["register_class"] == "benchmark aggregate"]
        per_rung = {}
        for r in RUNGS:
            p = sum(1 for l in scored if l[f"{r}_result"] == "pass")
            per_rung[r] = {
                "pass": p,
                "fail": sum(1 for l in scored if l[f"{r}_result"] == "fail"),
                "not_searched": sum(1 for l in scored
                                    if l[f"{r}_result"] == "not_searched"),
                "unread": sum(1 for l in scored if l[f"{r}_result"] == "unread"),
                "pass_rate_of_scored": round(p / len(scored), 3) if scored else None}
        by_class = defaultdict(Counter)
        for l in scored:
            for r in ("funding", "input"):
                if l[f"{r}_result"] == "pass":
                    by_class[r][l["register_class"]] += 1
        identity = (f"{len(scored)} scored + {len(excluded)} perimeter exclusions + "
                    f"{len(unread)} unread + {len(agg)} benchmark aggregates = {len(ls)}")
        out["sectors"][s] = {
            "population": len(ls),
            "population_parts": {k: v for k, v in parts[s].items() if k != "population"},
            "identity": identity,
            "identity_holds": len(scored) + len(excluded) + len(unread) + len(agg) == len(ls),
            "scored": len(scored),
            "perimeter_exclusions": len(excluded),
            "unread": len(unread),
            "benchmark_aggregates": len(agg),
            "scored_entries_by_rungs_cleared": {
                str(k): v for k, v in sorted(Counter(
                    l["rungs_passed"] for l in scored).items())},
            "per_rung": per_rung,
            "rung4_pass_by_register_class": dict(by_class["funding"]),
            "rung6_pass_by_register_class": dict(by_class["input"]),
            "rung6_provisional": sum(1 for l in scored
                                     if l["input_provisional"] == "true"),
            "rung6_not_searched": per_rung["input"]["not_searched"],
            # RUNG 4 BEFORE AND AFTER THIS PASS. "Before" is the state on main: the
            # funder pass of brief 12 covered hydrogen and nothing else, so rung 4
            # for the other four sectors was a question nobody had asked and every
            # cell was `not_searched`. D-L2 is the ruling that says a fail on an
            # unasked question is not a fail. "After" is this table.
            "rung4_before_this_pass": {
                "searched": s == "hydrogen",
                "pass": per_rung["funding"]["pass"] if s == "hydrogen" else 0,
                "not_searched": 0 if s == "hydrogen" else len(scored),
                "why": ("unchanged: sources/hydrogen_funder_pass.json was read in "
                        "brief 12 and is read again here" if s == "hydrogen" else
                        "no funder list had been read against this sector, so every "
                        "scored entry's rung 4 was not_searched")},
            "rung4_after_this_pass": {
                "searched": True,
                "pass": per_rung["funding"]["pass"],
                "fail": per_rung["funding"]["fail"],
                "not_searched": per_rung["funding"]["not_searched"]},
        }
    out["cross_sector"] = {
        "_shape": "rungs are rows, sectors are columns; the cell is passes out of scored",
        "rungs": {r: {s: {"pass": out["sectors"][s]["per_rung"][r]["pass"],
                          "of_scored": out["sectors"][s]["scored"]}
                      for s in SECTORS} for r in RUNGS},
        "population": {s: out["sectors"][s]["population"] for s in SECTORS},
        "scored": {s: out["sectors"][s]["scored"] for s in SECTORS},
        "total_population": sum(out["sectors"][s]["population"] for s in SECTORS),
        "total_scored": sum(out["sectors"][s]["scored"] for s in SECTORS)}
    return out


def write(lines, summary):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for l in lines:
            w.writerow({k: l.get(k, "") for k in FIELDS})
    SUMMARY.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")


def read_csv():
    with open(CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def tables(summary):
    print("\nTHE CROSS-SECTOR TABLE — rungs down, sectors across, passes out of scored\n")
    head = f"  {'rung':<10}" + "".join(f"{s[:13]:>15}" for s in SECTORS)
    print(head)
    print("  " + "-" * (len(head) - 2))
    for i, r in enumerate(RUNGS, 1):
        row = f"  {i}. {r:<7}"
        for s in SECTORS:
            c = summary["cross_sector"]["rungs"][r][s]
            row += f"{str(c['pass']) + '/' + str(c['of_scored']):>15}"
        print(row)
    print("  " + "-" * (len(head) - 2))
    print(f"  {'population':<10}" + "".join(
        f"{summary['sectors'][s]['population']:>15}" for s in SECTORS))
    print(f"  {'scored':<10}" + "".join(
        f"{summary['sectors'][s]['scored']:>15}" for s in SECTORS))
    print(f"  {'excluded':<10}" + "".join(
        f"{summary['sectors'][s]['perimeter_exclusions']:>15}" for s in SECTORS))
    print(f"  {'unread':<10}" + "".join(
        f"{summary['sectors'][s]['unread']:>15}" for s in SECTORS))
    print(f"\n  {summary['cross_sector']['total_population']} entries across five "
          f"populations; {summary['cross_sector']['total_scored']} scored.")

    print("\nEACH SECTOR'S POPULATION IDENTITY")
    for s in SECTORS:
        print(f"  {s:<24} {summary['sectors'][s]['identity']}")

    print("\nRUNG 6 — provisional, and where the sweep did not reach")
    for s in SECTORS:
        d = summary["sectors"][s]
        print(f"  {s:<24} {d['per_rung']['input']['pass']:>3} pass, "
              f"{d['rung6_provisional']:>3} provisional, "
              f"{d['rung6_not_searched']:>3} not searched, of {d['scored']} scored")

    print("\nRUNG 4 — before and after the funder pass")
    print(f"  {'sector':<24}{'before':>22}{'after':>26}")
    for s in SECTORS:
        d = summary["sectors"][s]
        b, a2 = d["rung4_before_this_pass"], d["rung4_after_this_pass"]
        print(f"  {s:<24}{b['pass']:>7} pass," 
              f"{b['not_searched']:>6} not searched"
              f"{a2['pass']:>10} pass,{a2['fail']:>5} fail,"
              f"{a2['not_searched']:>3} not searched")

    print("\nENTRIES BY RUNGS CLEARED, per sector")
    print(f"  {'sector':<24}" + "".join(f"{i:>5}" for i in range(7)))
    for s in SECTORS:
        d = summary["sectors"][s]["scored_entries_by_rungs_cleared"]
        print(f"  {s:<24}" + "".join(f"{d.get(str(i), 0):>5}" for i in range(7)))


def queue(lines):
    """WHAT A RUNG REVEALED THAT A ROW LACKS. Printed, never written."""
    out = []
    for l in lines:
        if l["funding_result"] == "pass" and l["register_class"] in (
                "named not admitted", "searched none found"):
            out.append((l["sector"], l["key"], l["name"],
                        "a funder names an award for an entry this register has not "
                        "admitted: " + l["funding_note"][:150]))
        if l["funding_result"] == "pass" and "status is Terminated" in l["funding_note"]:
            out.append((l["sector"], l["key"], l["name"],
                        "the funder's own factsheet says TERMINATED"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--queue", action="store_true")
    a = ap.parse_args()

    lines, parts = build()
    summary = summarise(lines, parts)
    problems = reconcile_hydrogen(lines)

    if a.check:
        have = read_csv()
        if len(have) != len(lines):
            print(f"build_ladder_all --check: FAILED — the csv has {len(have)} lines, "
                  f"the sources give {len(lines)}")
            return 1
        for h, l in zip(have, lines):
            for k in FIELDS:
                if str(h.get(k, "")) != str(l.get(k, "")):
                    print(f"build_ladder_all --check: FAILED at {h.get('key')} "
                          f"field {k}:\n  csv:     {h.get(k)!r}\n  sources: {l.get(k)!r}")
                    return 1
        if json.loads(SUMMARY.read_text(encoding="utf-8")) != summary:
            print("build_ladder_all --check: FAILED — the summary does not recompute "
                  "from the csv's own lines")
            return 1
        if problems:
            print("build_ladder_all --check: FAILED — hydrogen does not reconcile")
            for x in problems[:8]:
                print("  " + x)
            return 1
        print(f"build_ladder_all: --check, {len(lines)} lines across five sectors, "
              f"summary recomputed and equal; hydrogen reconciles line by line with "
              f"sources/ladder/hydrogen.csv.")
        return 0

    write(lines, summary)
    tables(summary)
    q = queue(lines)
    print(f"\nQUEUE — {len(q)} facts a rung revealed that a row does not carry. "
          f"Printed, never written.")
    for s, k, n, why in q:
        print(f"  [{s}] {k:<26} {n[:38]:40} {why[:110]}")
    if a.queue:
        return 0
    if problems:
        print("\nGATE FAILED — hydrogen does not reconcile with sources/ladder/hydrogen.csv")
        for x in problems[:8]:
            print("  " + x)
        return 1
    print("\nGATE PASSED — hydrogen's 245 lines in all.csv are line-for-line the "
          "committed sources/ladder/hydrogen.csv.")
    print(f"wrote {CSV.relative_to(ROOT)} and {SUMMARY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

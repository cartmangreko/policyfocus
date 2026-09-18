#!/usr/bin/env python3
"""DRIFT ACROSS FOUR VINTAGES OF ONE BENCHMARK, under the IEA's own reference numbers.

    python3 sources/build_hydrogen_drift.py            # prints the table, writes the json
    python3 sources/build_hydrogen_drift.py --check    # rebuilds and diffs; non-zero on drift

WHAT THIS EXTENDS. report_benchmark_gap.drift() reads one interval -- October 2023
against the current file -- because those were the only two vintages on file.
Odenweller and Ueckerdt publish three: the IEA's October 2021, October 2022 and
October 2023 databases, each quality-checked, each keeping the IEA's own reference
numbering. With the live endpoint that is four vintages and three intervals, and the
question rule 17 asks can be put to each of them.

    2021-10 -> 2022-10 -> 2023-10 -> current

LEAVING THE LIST IS VINTAGE DRIFT AND NOTHING ELSE. Not a stop event, not a stop
class, and no row's status_history is touched on the strength of it (scope.md). Rule
17 says the register must go and LOOK when an entry disappears, because the
disappearance may be hiding a failure nobody counted. It does not say the
disappearance is the failure.

THE POPULATION PER VINTAGE is the one the gap report already counts: European entries
at or above 100 MW, at ANY technology. Europe is bench.GEO. The threshold is read off
`Capacity_MWel` in the quality-checked workbooks and off `capacity (ktH2Y)` converted
at the IEA's own factor in the live endpoint, exactly as report_benchmark_gap does --
the two files state capacity in different columns and neither is converted here.

AND A REFERENCE MATCH ACROSS DISTANT VINTAGES IS NOT FREE. Reference numbers were
reassigned between vintages -- ref 1877 is "Sines refinery (phase 3)" at 600 MW in the
October 2023 file and "GalpH2Park-I (Phase I)" at 87 MW-equivalent in the live one
(sources/hydrogen_docket.md, "Three things the benchmarks did"). So every carried-over
pair is checked for name agreement and the disagreements are printed, and the register
cross-tab says which of its matches rest on a reference whose name also agrees.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import warnings
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402

ROOT = bench.ROOT
CACHE = ROOT / "sources" / "cache" / "hydrogen"
ODEN = CACHE / "odenweller"
OUT = ROOT / "sources" / "ladder" / "hydrogen_drift.json"

# The four vintages, oldest first. Each is (id, label, file or None for the endpoint).
VINTAGES = [
    ("odenweller_ueckerdt_2021", "2021-10",
     "IEA_Hydrogen_Projects_Database_2021_quality_checked.xlsx"),
    ("odenweller_ueckerdt_2022", "2022-10",
     "IEA_Hydrogen_Projects_Database_2022_quality_checked.xlsx"),
    ("odenweller_ueckerdt_2025", "2023-10",
     "IEA_Hydrogen_Projects_Database_2023_quality_checked.xlsx"),
    ("iea_hydrogen_production_projects", "current", None),
]

# THE QUALITY-CHECKED WORKBOOKS HAVE NO MACHINE HEADER ROW BEFORE 2023. The 2023
# files carry one at row 4 (`Ref`, `Project name`, `Technology_details`, ...); the
# 2021 and 2022 files carry `Column1`, `Column2` there instead. The column ORDER is
# identical across all three -- checked on a sample row of each -- so the columns are
# read by position and named here once, rather than by a header that two of the three
# files do not have.
COL = {"Ref": 0, "Project name": 1, "Country": 2, "Date online": 3,
       "Status": 5, "Technology": 6, "Announced Size": 25,
       "Capacity_MWel": 26, "Capacity_ktH2Y": 28, "Refs": 31,
       "Refs (quality check)": 32}


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_workbook_projects(path: pathlib.Path) -> list[dict]:
    """Every project row of a quality-checked workbook, by column position."""
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Projects"].iter_rows(values_only=True))
    wb.close()
    out = []
    for r in rows[4:]:
        if r[COL["Ref"]] is None:
            continue
        d = {k: (r[i] if i < len(r) else None) for k, i in COL.items()}
        d["Ref"] = str(d["Ref"]).strip()
        out.append(d)
    return out


def population(vid: str, fname: str | None) -> dict[str, dict]:
    """European entries at or above 100 MW, at any technology, keyed by reference.

    REF 0 IS NOT A REFERENCE. The workbooks carry aggregate lines -- "Other projects
    from confidential sources" -- under reference 0, several per vintage. None of them
    carries a country, so none reaches this population; the guard is here so that a
    future vintage that gives one a country cannot collapse several lines onto one key.
    """
    if fname is None:
        rows = bench.load_iea()
        out = {}
        for r in rows:
            if r["country"]["iso3"] not in bench.GEO:
                continue
            if (_f(r.get("capacity (ktH2Y)")) or 0) < bench.THRESHOLD_KT:
                continue
            ref = str(r["projectReference"])
            if ref == "0":
                continue
            out[ref] = {"ref": ref, "name": str(r.get("projectName") or ""),
                        "country": r["country"]["iso3"],
                        "status": str(r.get("status") or ""),
                        "technology": str(r.get("technolgy") or ""),
                        "date_online": r.get("dateOnline") or "",
                        "mwel": round((_f(r.get("capacity (ktH2Y)")) or 0)
                                      / bench.IEA_KT_PER_MW)}
        return out
    out = {}
    for r in load_workbook_projects(ODEN / fname):
        if r["Country"] not in bench.GEO:
            continue
        if (_f(r["Capacity_MWel"]) or 0) < 100:
            continue
        if r["Ref"] == "0":
            continue
        out[r["Ref"]] = {"ref": r["Ref"], "name": str(r["Project name"] or ""),
                         "country": r["Country"], "status": str(r["Status"] or ""),
                         "technology": str(r["Technology"] or ""),
                         "date_online": str(r["Date online"] or ""),
                         "mwel": round(_f(r["Capacity_MWel"]) or 0)}
    return out


def whole_file(fname: str | None) -> dict[str, dict]:
    """EVERY row of a vintage, keyed by reference, with no geography and no threshold.

    A DEPARTURE FROM THE POPULATION IS NOT THE SAME FACT AS A DEPARTURE FROM THE FILE,
    and the published drift table conflated them. Rule 17 is about a project that
    VANISHES from a database; an entry the publisher still carries, at a capacity it has
    since revised below the threshold, has not vanished and its failure is not uncounted.
    Fifteen of the 149 departures reported for 2023-10 -> current are of that second kind
    -- twelve of them at exactly the megawatts the IEA's own normalisation gives a 100 MW
    project -- so every departure is now tested against the end vintage's WHOLE file and
    the two kinds are counted apart.
    """
    if fname is None:
        return {str(r["projectReference"]): {
            "name": str(r.get("projectName") or ""),
            "country": r["country"]["iso3"],
            "status": str(r.get("status") or ""),
            "mwel": (round((_f(r.get("capacity (ktH2Y)")) or 0) / bench.IEA_KT_PER_MW)
                     if _f(r.get("capacity (ktH2Y)")) else None)}
            for r in bench.load_iea()}
    return {r["Ref"]: {"name": str(r["Project name"] or ""), "country": r["Country"],
                       "status": str(r["Status"] or ""),
                       "mwel": (round(_f(r["Capacity_MWel"]))
                                if _f(r["Capacity_MWel"]) is not None else None)}
            for r in load_workbook_projects(ODEN / fname)}


def register_references() -> tuple[dict[str, str], dict[str, str]]:
    """{reference: row id} and {reference: candidate id}, over BOTH recorded benchmarks.

    THE REFERENCE NUMBERING IS ONE NUMBERING. The register records references under two
    keys -- `odenweller_ueckerdt_2025` for the October 2023 vintage and
    `iea_hydrogen_production_projects` for the current one -- and they are the same
    IEA numbering (scope.md, "One benchmark in two vintages"). A departure from ANY
    interval is therefore looked for in the union of the two, which is what "under IEA
    reference numbers" means here.
    """
    import sector_map as sm
    rows, cands = {}, {}
    ids = set()
    for p in sm.load("project"):
        if p.get("sector") != "clean":
            continue
        ids.add(p["id"])
        for b in ("odenweller_ueckerdt_2025", "iea_hydrogen_production_projects"):
            for x in bench.as_list((p.get("benchmarks") or {}).get(b)):
                rows[str(x)] = p["id"]
    doc = json.loads((ROOT / "sources" / "hydrogen_candidates.json")
                     .read_text(encoding="utf-8"))
    for c in doc["candidates"]:
        if c["id"] in ids:
            continue
        for b in ("odenweller_ueckerdt_2025", "iea_hydrogen_production_projects"):
            for x in bench.as_list((c.get("benchmarks") or {}).get(b)):
                cands[str(x)] = c["id"]
    return rows, cands


def refused_references() -> set[str]:
    import report_benchmark_gap as rg
    return {ref for _b, ref in rg.REFUSED_BY_NAME}


CLASSES = ("admitted, a row here", "candidate, not yet a row",
           "refused with a clause", "never seen by this register")


def classify(ref: str, rowrefs, candrefs, refused) -> str:
    if ref in rowrefs:
        return CLASSES[0]
    if ref in candrefs:
        return CLASSES[1]
    if ref in refused:
        return CLASSES[2]
    return CLASSES[3]


def norm(n: str) -> str:
    return " ".join(str(n).strip().lower().split())


def departure_kind(e: dict, end_file: dict) -> tuple[str, str]:
    """Why an entry left the population: the file dropped it, or the entry moved.

    Returns (kind, what the end vintage says).
    """
    now = end_file.get(e["ref"])
    if now is None:
        return "absent from the end vintage's file", ""
    if now["country"] not in bench.GEO:
        return ("still on the list, outside the geography",
                f"{now['name']} is filed under {now['country']}")
    mw = now["mwel"]
    return ("still on the list, below the threshold",
            f"{now['name']} at {mw if mw is not None else 'no stated'} MW"
            + (f", {now['status']}" if now.get("status") else ""))


ARRIVAL_KINDS = ("new to the file", "already on the list, crossed the threshold")
DEPARTURE_KINDS = ("absent from the end vintage's file",
                   "still on the list, below the threshold",
                   "still on the list, outside the geography")


def interval(a: dict, b: dict, start_file: dict, end_file: dict,
             rowrefs, candrefs, refused) -> dict:
    """One interval: what left, what carried over, what was renamed, what arrived."""
    left = [a[r] for r in sorted(a, key=lambda x: int(x) if x.isdigit() else 0)
            if r not in b]
    carried = sorted(set(a) & set(b), key=lambda x: int(x) if x.isdigit() else 0)
    renamed = [{"ref": r, "was": a[r]["name"], "now": b[r]["name"]}
               for r in carried if norm(a[r]["name"]) != norm(b[r]["name"])]
    added = [b[r] for r in sorted(b, key=lambda x: int(x) if x.isdigit() else 0)
             if r not in a]
    cross, kinds = Counter(), Counter()
    departures = []
    for e in left:
        k = classify(e["ref"], rowrefs, candrefs, refused)
        kind, says = departure_kind(e, end_file)
        cross[k] += 1
        kinds[kind] += 1
        departures.append(dict(e, register_class=k, departure_kind=kind,
                               end_vintage_says=says,
                               register_id=rowrefs.get(e["ref"])
                               or candrefs.get(e["ref"]) or ""))
    akinds = Counter()
    arrivals = []
    for e in added:
        kind = (ARRIVAL_KINDS[1] if e["ref"] in start_file else ARRIVAL_KINDS[0])
        akinds[kind] += 1
        arrivals.append(dict(e, arrival_kind=kind))
    return {"left": len(left), "carried_over": len(carried),
            "of_which_renamed": len(renamed), "added": len(added),
            "start_total": len(a), "end_total": len(b),
            "identity_holds": (len(left) + len(carried) == len(a)
                               and len(carried) + len(added) == len(b)),
            "departures_by_kind": {k: kinds[k] for k in DEPARTURE_KINDS},
            "arrivals_by_kind": {k: akinds[k] for k in ARRIVAL_KINDS},
            "departures_by_register_class": {c: cross[c] for c in CLASSES},
            "departures": departures, "arrivals": arrivals, "renamed": renamed}


def build() -> dict:
    rowrefs, candrefs = register_references()
    refused = refused_references()
    pops, files = {}, {}
    for vid, label, fname in VINTAGES:
        pops[label] = population(vid, fname)
        files[label] = whole_file(fname)
    out = {"_comment": [
        "COMPUTED BY sources/build_hydrogen_drift.py FROM THE FOUR CACHED VINTAGES.",
        "Never edited by hand. --check rebuilds and diffs.",
        "",
        "LEAVING THE LIST IS VINTAGE DRIFT AND NOTHING ELSE. Rule 17 says go and look",
        "when an entry disappears, because the disappearance may hide a failure nobody",
        "counted; it does not say the disappearance IS the failure.",
        "",
        "THE ROWS ONLY SUM IF `of_which_renamed` SITS INSIDE `carried_over`. A renamed",
        "entry neither left nor arrived.",
    ], "vintages": [], "intervals": [], "whole_span": None}
    for _vid, label, fname in VINTAGES:
        out["vintages"].append({
            "vintage": label,
            "source": fname or "api.iea.org/hydrogen/project",
            "european_entries_at_or_above_100mw": len(pops[label]),
            "rows_in_the_whole_file": len(files[label]),
        })
    labels = [v[1] for v in VINTAGES]
    for a, b in zip(labels, labels[1:]):
        d = interval(pops[a], pops[b], files[a], files[b],
                     rowrefs, candrefs, refused)
        d = {"from": a, "to": b, **d}
        out["intervals"].append(d)
    span = interval(pops[labels[0]], pops[labels[-1]], files[labels[0]],
                    files[labels[-1]], rowrefs, candrefs, refused)
    out["whole_span"] = {"from": labels[0], "to": labels[-1], **span}
    return out


def table(doc: dict) -> str:
    lines = ["\nDRIFT ACROSS FOUR VINTAGES OF ONE BENCHMARK, under the IEA's own reference "
             "numbers.",
             "Odenweller & Ueckerdt publish the IEA's October 2021, 2022 and 2023 databases "
             "quality-checked;\nthe fourth vintage is the live endpoint. European entries at "
             "or above 100 MW, any technology:\n"]
    w = 12
    lines.append(f"  {'vintage':{w}} {'entries':>8} {'whole file':>11}")
    for v in doc["vintages"]:
        lines.append(f"  {v['vintage']:{w}} {v['european_entries_at_or_above_100mw']:>8} "
                     f"{v['rows_in_the_whole_file']:>11}")
    lines.append("")
    hdr = (f"  {'interval':{w+22}} {'left':>6} {'carried':>8} {'renamed':>8} "
           f"{'added':>6}  {'start':>6} {'end':>6}  sums")
    lines.append(hdr)
    lines.append("  " + "-" * (len(hdr) - 2))
    heads = [f"{d['from']}->{d['to']}" for d in doc["intervals"]] + ["whole span"]
    allint = doc["intervals"] + [doc["whole_span"]]
    for d in doc["intervals"] + [doc["whole_span"]]:
        tag = f"{d['from']} -> {d['to']}"
        if d is doc["whole_span"]:
            tag = f"{tag} (whole span)"
        lines.append(f"  {tag:{w+22}} {d['left']:>6} {d['carried_over']:>8} "
                     f"{d['of_which_renamed']:>8} {d['added']:>6}  "
                     f"{d['start_total']:>6} {d['end_total']:>6}  "
                     f"{'yes' if d['identity_holds'] else 'NO'}")
    lines.append("\n  left + carried over = the start vintage's total; carried over + added "
                 "= the end vintage's.\n  A renamed entry neither left nor arrived, so "
                 "`renamed` is shown INSIDE `carried`.")
    lines.append("\n  A DEPARTURE FROM THE POPULATION IS NOT A DEPARTURE FROM THE FILE, and "
                 "only the first\n  kind is what rule 17 is about — a project that VANISHES "
                 "from a database. Each departure\n  is tested against the end vintage's "
                 "whole file, with no geography and no threshold:\n")
    kw = max(len(k) for k in DEPARTURE_KINDS)
    lines.append(f"  {'departure':{kw}} " + " ".join(f"{h:>16}" for h in heads))
    lines.append("  " + "-" * (kw + 1 + 17 * len(heads)))
    for k in DEPARTURE_KINDS:
        lines.append(f"  {k:{kw}} " +
                     " ".join(f"{d['departures_by_kind'][k]:>16}" for d in allint))
    lines.append(f"  {'total':{kw}} " + " ".join(f"{d['left']:>16}" for d in allint))
    lines.append(f"\n  {'arrival':{kw}} " + " ".join(f"{h:>16}" for h in heads))
    lines.append("  " + "-" * (kw + 1 + 17 * len(heads)))
    for k in ARRIVAL_KINDS:
        lines.append(f"  {k:{kw}} " +
                     " ".join(f"{d['arrivals_by_kind'][k]:>16}" for d in allint))
    lines.append(f"  {'total':{kw}} " + " ".join(f"{d['added']:>16}" for d in allint))
    for d in allint:
        moved = [x for x in d["departures"]
                 if x["departure_kind"] != DEPARTURE_KINDS[0]]
        if not moved:
            continue
        lines.append(f"\n  {d['from']} -> {d['to']}: left the population and NOT the file "
                     f"({len(moved)}) — the publisher\n  still carries these and has "
                     f"revised what it says about them:")
        for x in moved:
            lines.append(f"    ref {x['ref']:>5}  {x['name'][:38]:38} "
                         f"{x['mwel'] if x['mwel'] is not None else '?':>5} MW -> "
                         f"{x['end_vintage_says'][:56]}")
    lines.append("\n  DEPARTURES AGAINST THIS REGISTER'S OWN CLASSES, per interval:\n")
    cw = max(len(c) for c in CLASSES)
    lines.append(f"  {'class':{cw}} " + " ".join(f"{h:>16}" for h in heads))
    lines.append("  " + "-" * (cw + 1 + 17 * len(heads)))
    for c in CLASSES:
        cells = " ".join(f"{d['departures_by_register_class'][c]:>16}" for d in allint)
        lines.append(f"  {c:{cw}} {cells}")
    lines.append(f"  {'total':{cw}} " +
                 " ".join(f"{d['left']:>16}" for d in allint))
    for d in allint:
        named = [x for x in d["departures"]
                 if x["register_class"] != "never seen by this register"]
        if not named:
            continue
        lines.append(f"\n  {d['from']} -> {d['to']}: departures this register knows by "
                     f"name — the case rule 17 was written for:")
        for x in named:
            lines.append(f"    ref {x['ref']:>5}  {x['status'][:18]:18} "
                         f"{x['name'][:44]:44} {x['register_id']}")
    lines.append("\n  RENAMED, per interval — every one of these would have broken a name "
                 "join, and the same\n  edit that breaks a join silently invents one "
                 "somewhere else:")
    for d in doc["intervals"]:
        lines.append(f"    {d['from']} -> {d['to']}: {d['of_which_renamed']}")
        for x in d["renamed"][:8]:
            lines.append(f"      ref {x['ref']:>5}  {x['was'][:40]:40} -> {x['now'][:40]}")
        if d["of_which_renamed"] > 8:
            lines.append(f"      and {d['of_which_renamed'] - 8} more")
    return "\n".join(lines)


def available() -> bool:
    return all((ODEN / f).exists() for _v, _l, f in VINTAGES if f) and \
        (CACHE / "iea_live_projects.json").exists()


def main() -> int:
    check = "--check" in sys.argv
    if not available():
        print("build_hydrogen_drift: the cached vintages are not on this machine, so the "
              "drift\n  table is not recomputed. The committed file stands; the bytes are "
              "the IEA's and\n  are held by hash in sources/benchmark_snapshots.json.")
        return 0
    doc = build()
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if text != current:
            print("build_hydrogen_drift --check: sources/ladder/hydrogen_drift.json is not "
                  "what the\n  four vintages produce. Run build_hydrogen_drift.py.")
            return 1
        print(f"build_hydrogen_drift --check: {len(doc['intervals'])} intervals, the drift "
              f"table matches its sources.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(table(doc))
    bad = [d for d in doc["intervals"] + [doc["whole_span"]] if not d["identity_holds"]]
    if bad:
        print("\n  IDENTITY FAILS on " + ", ".join(f"{d['from']}->{d['to']}" for d in bad))
        return 1
    print(f"\n  -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

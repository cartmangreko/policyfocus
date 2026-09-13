#!/usr/bin/env python3
"""THE CONFIRMATION LADDER, hydrogen first. Six independent checks per project.

    python3 sources/build_ladder.py          # writes both files, prints the tables

Writes sources/ladder/hydrogen.csv (one line per population entry) and
sources/ladder/hydrogen_summary.json (computed FROM the csv, never alongside it).

THE RULES ARE IN scope.md, "The confirmation ladder", and this file implements them
rather than restating them. What is repeated here is only what the code needs to be
read against:

  rung 1  site        owner or permitting authority names the location at
                      municipality or finer
  rung 2  capacity    owner states a capacity in any unit, recorded as stated
  rung 3  fid         owner states FID has been TAKEN; "expected" fails
  rung 4  funding     a FUNDER publishes an award naming the project; the owner's
                      claim of an award is not a pass
  rung 5  start       owner states a production or operation start WITH a date
                      precision; "mid-decade" fails
  rung 6  input       an edge with firmness `contract`; framework and intent fail

EACH CELL IS (result, source, speaker, date, precision). `pass`, `fail`, `unread`.

WHY EVERY CELL CARRIES A SOURCE, INCLUDING A FAIL. A fail is a finding about the
evidence, so it has to say which evidence was examined to reach it: for a row, the
row and the newest source on it; for a benchmark entry nobody has admitted, the
admission search record, which lists every fetch made and what each returned. A
cell with a result and nothing cited is the h2v-fos shape -- a hand-typed line that
survived three readings because nothing recomputed it -- and check_ladder.py
refuses the file over it.

MONOTONICITY IS NOT IMPOSED. A project may pass 5 and fail 2. See scope.md.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import sector_map as sm  # noqa: E402

ROOT = bench.ROOT
OUTDIR = ROOT / "sources" / "ladder"
CSV = OUTDIR / "hydrogen.csv"
SUMMARY = OUTDIR / "hydrogen_summary.json"
SEARCH = ROOT / "sources" / "hydrogen_gap_search.json"
EDGES = ROOT / "sources" / "edges.json"
CANDIDATES = ROOT / "sources" / "hydrogen_candidates.json"

RUNGS = ("site", "capacity", "fid", "funding", "start", "input")

# RUNG 3. The owner has to say the decision is TAKEN. Everything in the second
# tuple is a statement about a future decision and fails, which is the whole
# distinction the rung exists to draw.
FID_TAKEN = ("fid", "construction", "commissioning", "operating")
FID_INTENT_WORDS = ("expected", "targeted", "subject to", "planned for", "aims to",
                    "intends", "due to take", "anticipated")

# RUNG 4. THE FUNDER IS THE SPEAKER. A grant register is a funder publishing its own
# award; a company press release announcing the same award is the owner's claim and
# does not pass.
FUNDER_SOURCE_TYPES = ("grant_register",)

# RUNG 5. Milestones that are a production or operation start. `fid_target` is not
# one of them -- it is a date for rung 3's event, and rung 3 fails on a target.
START_MILESTONES = ("production_start", "commissioning", "operation_start")

# RUNG 6. `contract` passes; the other two fail by name.
FIRM_PASS = "contract"


def cell(result, source=None, speaker=None, date=None, precision=None, note=""):
    return {"result": result, "source": source or "", "speaker": speaker or "",
            "date": date or "", "precision": precision or "", "note": note}


UNREAD = cell("unread")


def newest(items, key="date"):
    dated = [i for i in items if i.get(key)]
    return max(dated, key=lambda i: i[key]) if dated else None


# --------------------------------------------------------------------------
# THE POPULATION


def population():
    """The current IEA vintage, plus every register row not on it.

    THE WIDE POPULATION, all technologies at or above the threshold -- the same one
    report_benchmark_gap.py counts, and for the same reason: a ladder that excluded
    fossil-with-capture could never report how much of it there is.
    """
    def f(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    iea = {str(r["projectReference"]): r for r in bench.load_iea()
           if r["country"]["iso3"] in bench.GEO
           and (f(r.get("capacity (ktH2Y)")) or 0) >= bench.THRESHOLD_KT}

    rows = [p for p in sm.load("project") if p.get("sector") == "clean"]
    by_ref = defaultdict(list)
    offlist = []
    for r in rows:
        refs = [str(x) for x in bench.as_list(
            (r.get("benchmarks") or {}).get("iea_hydrogen_production_projects"))]
        on = [x for x in refs if x in iea]
        for x in on:
            by_ref[x].append(r)
        if not on:
            offlist.append(r)
    return iea, rows, by_ref, offlist


def candidate_refs():
    """{iea ref: candidate} -- a candidate is admitted by the perimeter and waiting
    only on a position, so it is `admitted` for the register class."""
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    out = {}
    for c in doc["candidates"]:
        for x in bench.as_list((c.get("benchmarks") or {}).get(
                "iea_hydrogen_production_projects")):
            out[str(x)] = c
    return out


def search_records():
    doc = json.loads(SEARCH.read_text(encoding="utf-8"))
    return {str(e["ref"]): e for e in doc["entries"]}, doc.get("searched", "")


# --------------------------------------------------------------------------
# SCORING A ROW -- the only entries with register evidence behind them


def score_row(row, edges_by_project, graph_date=""):
    """Six cells from a register row's own fields."""
    out = {}
    sources = row.get("sources") or []
    base = newest(sources)
    base_id = base["url"] if base else ""
    base_pub = base.get("publisher", "") if base else ""
    base_date = base.get("date", "") if base else ""
    base_prec = base.get("date_precision", "") if base else ""

    # RUNG 1, SITE. The location_statement is the direct answer where there is one;
    # a located row whose position came from a company or permit source names the
    # site at least as finely. DRAWN STATUS IS NOT CONSULTED -- see scope.md.
    ls = row.get("location_statement")
    ls = ls[0] if isinstance(ls, list) and ls else ls
    if isinstance(ls, dict) and ls.get("names_location_finer_than_municipality"):
        out["site"] = cell("pass", ls.get("source_url"), "owner",
                           ls.get("source_date"), ls.get("source_date_precision"),
                           "location_statement names finer than municipality")
    elif isinstance(ls, dict):
        out["site"] = cell("fail", ls.get("source_url"), "owner",
                           ls.get("source_date"), ls.get("source_date_precision"),
                           "location_statement names the municipality and no finer")
    elif row.get("located") == "yes":
        out["site"] = cell("pass", base_id, "owner", base_date, base_prec,
                           "row carries a position from a company or permit source")
    else:
        out["site"] = cell("fail", base_id, "owner", base_date, base_prec,
                           "no location statement finer than municipality on the row")

    # RUNG 2, CAPACITY. Any unit, recorded as stated. Never converted.
    if row.get("capacity_value") is not None and row.get("capacity_unit"):
        out["capacity"] = cell(
            "pass", row.get("capacity_source_url") or base_id, "owner",
            row.get("capacity_as_of") or base_date,
            row.get("capacity_as_of_precision") or base_prec,
            f"{row['capacity_value']} {row['capacity_unit']} as stated")
    else:
        out["capacity"] = cell("fail", base_id, "owner", base_date, base_prec,
                               "no capacity stated by the owner on file")

    # RUNG 3, FID TAKEN. A status event moving the row to fid or beyond is the
    # owner saying the decision is made. A `fid_target` in stated_schedule is not.
    hist = row.get("status_history") or []
    fid = newest([e for e in hist if e.get("status_to") in FID_TAKEN])
    if fid:
        out["fid"] = cell("pass", fid.get("source_url"), "owner", fid.get("date"),
                          fid.get("date_precision"),
                          f"status_to {fid.get('status_to')}")
    else:
        tgt = [s for s in (row.get("stated_schedule") or [])
               if s.get("milestone") == "fid_target"]
        note = ("owner states an FID target, which is a future decision"
                if tgt else "no owner statement that FID has been taken")
        out["fid"] = cell("fail", base_id, "owner", base_date, base_prec, note)

    # RUNG 4, FUNDING. THE FUNDER IS THE SPEAKER.
    award = newest([e for e in hist
                    if e.get("source_type") in FUNDER_SOURCE_TYPES
                    or e.get("event_kind") == "financing"
                    and e.get("source_type") in FUNDER_SOURCE_TYPES])
    if award:
        out["funding"] = cell("pass", award.get("source_url"), "funder",
                              award.get("date"), award.get("date_precision"),
                              "award published by the funder")
    else:
        owner_claim = any(e.get("status_to") == "funded" for e in hist)
        note = ("the owner states an award and no funder publication is on file"
                if owner_claim else "no funder award naming the project on file")
        out["funding"] = cell("fail", base_id, "owner", base_date, base_prec, note)

    # RUNG 5, START DATE, WITH A PRECISION.
    st = newest([s for s in (row.get("stated_schedule") or [])
                 if s.get("milestone") in START_MILESTONES
                 and s.get("target_date") and s.get("target_precision")])
    if st:
        out["start"] = cell("pass", st.get("source_url"), st.get("speaker") or "owner",
                            st.get("date"), st.get("date_precision"),
                            f"{st.get('milestone')} {st.get('target_date')} "
                            f"at {st.get('target_precision')} precision")
    else:
        out["start"] = cell("fail", base_id, "owner", base_date, base_prec,
                            "no owner-stated start carrying a date precision")

    # RUNG 6, INPUT CONTRACTED. Brief 9's edges carry the firmness axis; the row's
    # own edges do not, so a row edge can only ever be the weaker evidence and is
    # read second.
    out["input"] = score_input(row, edges_by_project, graph_date)
    return out


def graph_read(edoc):
    """What to cite for a rung 6 FAIL when no edge names the project at all.

    THE EVIDENCE EXAMINED IS THE GRAPH, so the graph is what the cell cites. Brief 9
    records no sweep date in the file, so the date given is the NEWEST STATEMENT in
    it -- the graph's own coverage edge -- and the note says that is what it is
    rather than passing it off as the day somebody looked.
    """
    dates = [e.get("date") for e in edoc["edges"] if e.get("date")]
    return max(dates) if dates else ""


def score_input(row, edges_by_project, graph_date=""):
    """RUNG 6. `contract` passes, `framework` and `intent` fail, and EVERY result is
    provisional while `verdict` is null on the edge it rests on."""
    mine = edges_by_project.get(row["id"], [])
    firm = [e for e in mine if e.get("firmness") == FIRM_PASS]
    if firm:
        e = newest(firm) or firm[0]
        c = cell("pass", e.get("url"), e.get("speaker") or "supplier", e.get("date"),
                 e.get("date_precision"),
                 f"{e.get('edge_kind')} at firmness contract")
        c["provisional"] = e.get("verdict") is None
        return c
    if mine:
        e = newest(mine) or mine[0]
        c = cell("fail", e.get("url"), e.get("speaker") or "supplier", e.get("date"),
                 e.get("date_precision"),
                 f"{e.get('edge_kind')} at firmness {e.get('firmness')}")
        c["provisional"] = e.get("verdict") is None
        return c
    rowedges = [e for e in (row.get("edges") or []) if (e.get("evidence") or {}).get("url")]
    if rowedges:
        e = newest(rowedges, key="since") or rowedges[0]
        ev = e.get("evidence") or {}
        c = cell("fail", ev.get("url"), "owner", e.get("since") or graph_date, "day",
                 "row edge carries no firmness; brief 9's axis is where rung 6 reads")
        c["provisional"] = True
        return c
    c = cell("fail", "sources/edges.json", "eufabric dependency sweep", graph_date,
             "day", "no edge in the dependency graph names this project; the date is "
             "the graph's newest statement, not a sweep date")
    c["provisional"] = True
    return c


# --------------------------------------------------------------------------
# SCORING A BENCHMARK ENTRY NOBODY HAS ADMITTED


def score_unadmitted(ref, rec, searched_on, unreadable):
    """Rung 1 is scored for EVERY entry on the external list, admitted or not; the
    admission search is what scores it. The other five have no owner document on
    file at all -- the search is the record of looking and finding none.

    AN UNREADABLE ENTRY SCORES `unread` ON ALL SIX. It is not a fail: a publisher
    this register cannot read has not been shown to have said nothing.
    """
    if unreadable:
        return {r: dict(UNREAD, note="company source unreadable; queued for a "
                        "browser pass") for r in RUNGS}

    if rec is None:
        # On the list, not in the admission search: the search covered the class
        # `not searched by eufabric` and the rest were classified before it ran.
        return {r: cell("fail", "sources/hydrogen_gap_search.json", "eufabric search",
                        searched_on, "day",
                        "classified before the admission search; no owner document "
                        "on file") for r in RUNGS}

    src = "sources/hydrogen_gap_search.json"
    names = rec.get("outcome") == "owner or permit source names the site"
    out = {}
    if names:
        adm = rec.get("admission") if isinstance(rec.get("admission"), dict) else {}
        named_by = adm.get("named_by") or ""
        hit = next((f for f in rec.get("fetches") or [] if f.get("names_place")), None)
        out["site"] = cell("pass", (hit or {}).get("url") or src,
                           "owner" if (hit or {}).get("source_type") == "company"
                           else (hit or {}).get("source_type") or "owner",
                           searched_on, "day",
                           named_by or "admission search: owner or permit names the site")
    else:
        out["site"] = cell("fail", src, "eufabric search", searched_on, "day",
                           "admission search found no owner or permit source")
    for r in RUNGS[1:]:
        out[r] = cell("fail", src, "eufabric search", searched_on, "day",
                      "no owner document on file; the admission search is the record "
                      "of looking")
    return out


# --------------------------------------------------------------------------


def unreadable_refs(records):
    """Benchmark entries whose company source could not be read.

    TWO SOURCES, BOTH READ RATHER THAN TYPED, because the entries reached this state
    by two different routes and one of them predates the other:

      the admission search's own outcome, `source unreadable` -- 18 entries whose
      company domain answered 403, DNS or an empty body when the search ran

      report_benchmark_gap.UNREADABLE_BY_NAME -- entries located and measured BEFORE
      the admission search existed, so the search holds no record of them at all.
      Refs 928, 1806 and 1911 are the three: Uniper's H2Maasvlakte phase II, Shell's
      Holland Hydrogen 2 and the Shell-Mitsubishi MoU, each an unsettled duplicate
      of a held row whose confirmation waits on a publisher that will not answer.

    Taking only the first gave 18 and disagreed with the gap report's own class count
    of 21 for the same vintage. The two files now read the same list.
    """
    import report_benchmark_gap as rg
    out = {ref for ref, e in records.items()
           if e.get("outcome") == "source unreadable"}
    out |= {ref for (b, ref) in rg.UNREADABLE_BY_NAME
            if b == "iea_hydrogen_production_projects"}
    return out


def build():
    iea, rows, by_ref, offlist = population()
    records, searched_on = search_records()
    cands = candidate_refs()
    unread_refs = unreadable_refs(records)

    edoc = json.loads(EDGES.read_text(encoding="utf-8"))
    edges_by_project = defaultdict(list)
    for e in edoc["edges"]:
        if e.get("project_id"):
            edges_by_project[e["project_id"]].append(e)
    graph_date = graph_read(edoc)

    lines = []
    for ref in sorted(iea, key=lambda x: int(x) if x.isdigit() else 0):
        entry = iea[ref]
        held = by_ref.get(ref)
        cand = cands.get(ref)
        if held:
            row = held[0]
            cells = score_row(row, edges_by_project, graph_date)
            klass, rid = "admitted", row["id"]
        elif cand:
            cells = score_unadmitted(ref, records.get(ref), searched_on,
                                     ref in unread_refs)
            klass, rid = "admitted", cand["id"]
        else:
            unreadable = ref in unread_refs
            rec = records.get(ref)
            cells = score_unadmitted(ref, rec, searched_on, unreadable)
            if unreadable:
                klass = "unread"
            elif rec is None:
                klass = "none found"
            elif rec.get("outcome") == "owner or permit source names the site":
                klass = "named not admitted"
            else:
                klass = "none found"
            rid = ""
        lines.append(line_for(key=f"iea:{ref}", ref=ref, rid=rid, entry=entry,
                              row=held[0] if held else None, klass=klass, cells=cells))

    for row in offlist:
        cells = score_row(row, edges_by_project, graph_date)
        lines.append(line_for(key=f"row:{row['id']}", ref="", rid=row["id"],
                              entry=None, row=row, klass="admitted", cells=cells))
    return lines, iea, offlist


def line_for(key, ref, rid, entry, row, klass, cells):
    cap_v = cap_u = ""
    if row is not None:
        cap_v = row.get("capacity_value") if row.get("capacity_value") is not None else ""
        cap_u = row.get("capacity_unit") or ""
    elif entry is not None:
        cap_v, cap_u = entry.get("capacity (ktH2Y)") or "", "ktH2Y"

    stop = ""
    if row is not None:
        stopev = newest([e for e in (row.get("status_history") or [])
                         if e.get("status_to") in sm.STOPPED_STATUSES])
        if stopev:
            stop = f"{stopev.get('status_to')}@{stopev.get('date')}"

    dropped = ""
    if row is not None and row.get("dropped_from_benchmark"):
        d = row["dropped_from_benchmark"]
        dropped = f"{d.get('benchmark')}:{d.get('present_in')}->{d.get('absent_from')}"

    country = ""
    if row is not None:
        country = row.get("country") or ""
    elif entry is not None:
        country = (entry.get("country") or {}).get("iso3") or ""

    line = {"key": key, "iea_ref": ref, "row_id": rid, "sector": "clean",
            "country": country, "register_class": klass,
            "iea_status": (entry or {}).get("status", ""),
            "name": (entry or {}).get("projectName")
                    or (f"{row.get('company','')} {row.get('plant','')}".strip()
                        if row is not None else ""),
            "dropped_from_benchmark": dropped,
            "capacity_value": cap_v, "capacity_unit": cap_u,
            "stop_event": stop}
    passed = 0
    for r in RUNGS:
        c = cells[r]
        line[f"{r}_result"] = c["result"]
        line[f"{r}_source"] = c["source"]
        line[f"{r}_speaker"] = c["speaker"]
        line[f"{r}_date"] = c["date"]
        line[f"{r}_precision"] = c["precision"]
        line[f"{r}_note"] = c["note"]
        if r == "input":
            line["input_provisional"] = "true" if c.get("provisional") else "false"
        if c["result"] == "pass":
            passed += 1
    line["rungs_passed"] = passed
    line["unread"] = "true" if all(cells[r]["result"] == "unread" for r in RUNGS) else "false"
    return line


FIELDS = (["key", "iea_ref", "row_id", "name", "sector", "country", "register_class",
           "iea_status", "dropped_from_benchmark", "capacity_value", "capacity_unit",
           "stop_event", "rungs_passed", "unread"]
          + [f"{r}_{f}" for r in RUNGS
             for f in ("result", "source", "speaker", "date", "precision", "note")]
          + ["input_provisional"])


def summarise(lines):
    """COMPUTED FROM THE CSV'S OWN LINES, so the two files cannot disagree."""
    by_passed = Counter(l["rungs_passed"] for l in lines)
    per_rung = {r: Counter() for r in RUNGS}
    for l in lines:
        for r in RUNGS:
            if l[f"{r}_result"] == "pass":
                per_rung[r][l["register_class"]] += 1
    cross = defaultdict(Counter)
    for l in lines:
        cross[l["iea_status"] or "(not on the list)"][l["rungs_passed"]] += 1
    return {
        "_comment": [
            "COMPUTED FROM sources/ladder/hydrogen.csv BY build_ladder.py.",
            "Never edited by hand: the reconciliation gate check_ladder.py recomputes",
            "it and refuses a mismatch. See scope.md, 'The ladder is computed, never",
            "typed'.",
        ],
        "population": len(lines),
        "entries_by_rungs_passed": {str(k): by_passed[k] for k in sorted(by_passed)},
        "pass_count_per_rung_by_register_class":
            {r: dict(sorted(per_rung[r].items())) for r in RUNGS},
        "rungs_passed_by_iea_status":
            {k: {str(n): v[n] for n in sorted(v)} for k, v in sorted(cross.items())},
        "rung6_provisional": sum(1 for l in lines
                                 if l.get("input_provisional") == "true"),
        "unread_entries": sum(1 for l in lines if l["unread"] == "true"),
    }


def benchmark_available() -> bool:
    """Is the benchmark on this machine? The cache is gitignored and the bytes are
    not redistributable, so on a build server it is not -- and the ladder is then
    read from the committed files rather than recomputed. check_ladder.py still
    runs, and still reconciles; see its two modes."""
    return (ROOT / "sources" / "cache" / "hydrogen" / "iea_live_projects.json").exists()


def main() -> int:
    check = "--check" in sys.argv
    if not benchmark_available():
        # REPORTED, NOT FAILED. Fetching here would put api.iea.org in the build's
        # critical path and cache a file this repository may not redistribute.
        print("build_ladder: the IEA benchmark is not cached on this machine, so the "
              "ladder is not recomputed.\n  The committed files stand and "
              "check_ladder.py reconciles them against benchmark_snapshots.json.")
        return 0

    lines, iea, offlist = build()
    if check:
        import io
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\r\n")
        w.writeheader()
        for l in lines:
            w.writerow(l)
        # READ UNTRANSLATED. Path.read_text() turns the writer's CRLF into LF, so a
        # byte-for-byte comparison against what the writer produces fails on every
        # line ending and says the ladder has drifted when nothing has.
        with CSV.open(encoding="utf-8", newline="") as fh:
            current = fh.read() if CSV.exists() else ""
        if buf.getvalue() != current:
            print("build_ladder --check: sources/ladder/hydrogen.csv is not what the "
                  "register and the benchmark produce. Run build_ladder.py.")
            return 1
        print(f"build_ladder --check: {len(lines)} entries, the ladder matches its "
              f"sources.")
        return 0

    OUTDIR.mkdir(parents=True, exist_ok=True)
    with CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for l in lines:
            w.writerow(l)
    summary = summarise(lines)
    summary["reconciliation"] = {
        "iea_current_vintage": len(iea),
        "register_rows_not_on_the_list": len(offlist),
        "population": len(iea) + len(offlist),
    }
    SUMMARY.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print(f"build_ladder: {len(lines)} entries -> {CSV.relative_to(ROOT)} "
          f"and {SUMMARY.relative_to(ROOT)}")
    print(f"  population = {len(iea)} IEA + {len(offlist)} register rows not on the "
          f"list = {len(iea) + len(offlist)}")
    print(queue(lines))
    return 0


def queue(lines):
    """WHAT SCORING REVEALED AND THIS BRIEF DOES NOT WRITE.

    Nothing here edits a row. Brief 10 reads the register; a fact it turns up about
    a row is printed for a later brief to rule on, because a ladder that quietly
    improved the rows it scores would be marking its own work.
    """
    rows = {p["id"]: p for p in sm.load("project") if p.get("sector") == "clean"}
    out = ["\nQUEUE -- facts scoring turned up, PRINTED AND NOT WRITTEN:"]

    owner_claim = sorted({l["row_id"] for l in lines
                          if l["funding_result"] == "fail" and l["row_id"]
                          and "owner states an award" in l["funding_note"]})
    out.append(f"\n  1. AN OWNER'S AWARD WITH NO FUNDER PUBLICATION ON FILE ("
               f"{len(owner_claim)}). Rung 4 fails by the rule -- the funder is the"
               f"\n     speaker -- and the funder's own register would settle each "
               f"one.")
    for rid in owner_claim:
        r = rows.get(rid, {})
        out.append(f"       {rid:42} {r.get('company','')[:34]}")

    admit = [l for l in lines if l["register_class"] == "named not admitted"
             and l["site_result"] == "pass"]
    out.append(f"\n  2. NAMED BY AN OWNER OR PERMIT SOURCE, STILL NOT ADMITTED "
               f"({len(admit)}). Rung 1 passes\n     on a source already on file; "
               f"whether the perimeter admits them is a ruling, not a fetch.")

    no_cap = sorted({l["row_id"] for l in lines
                     if l["capacity_result"] == "fail" and l["row_id"]})
    out.append(f"\n  3. A ROW WITH NO OWNER-STATED CAPACITY ({len(no_cap)}). Rung 2 "
               f"fails on the row as it stands.")
    for rid in no_cap:
        out.append(f"       {rid}")

    no_start = sorted({l["row_id"] for l in lines
                       if l["start_result"] == "fail" and l["row_id"]})
    out.append(f"\n  4. A ROW WITH NO OWNER-STATED START CARRYING A PRECISION "
               f"({len(no_start)}). Several of these\n     have a start in a source "
               f"already cited on the row but not in stated_schedule; reading\n"
               f"     them across is a write and waits for a brief that permits one.")

    breach = [(rid, s) for rid, r in rows.items()
              for s in (r.get("sources") or [])
              if s.get("archived") and not s.get("captured_at")]
    out.append(f"\n  5. AN ARCHIVED SOURCE WITH NO captured_at ({len(breach)}), "
               f"against the clause corrected in\n     this PR: captured_at is the "
               f"date of the copy on file and archived says which.")
    for rid, s in breach:
        out.append(f"       {rid:42} {s['url'][:72]}")
    return "\n".join(out)


if __name__ == "__main__":
    raise SystemExit(main())

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
import re
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
FUNDERS = ROOT / "sources" / "hydrogen_funder_pass.json"

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


def cell(result, source=None, speaker=None, date=None, precision=None, note="",
         searched=True, captured_at=None):
    """One rung cell.

    `searched` SAYS WHETHER THE SOURCE CLASS THIS RUNG READS WAS EXAMINED for this
    entry -- owner or permit sources for rungs 1, 2, 3 and 5; funder publications
    for rung 4; the dependency graph or an owner statement for rung 6.

    A FAIL WITH `searched` FALSE IS NOT A FAIL. It is reported as `not_searched`,
    because "the owner does not state an FID" and "nobody has looked for one" are
    different findings and only the first is about the project. Ruled 15 September
    2026, after rung 4 was found reporting 71 fails on a question nobody had asked
    of those entries.
    """
    if result == "fail" and not searched:
        result = "not_searched"
    return {"result": result, "source": source or "", "speaker": speaker or "",
            "date": date or "", "precision": precision or "", "note": note,
            "searched": bool(searched), "captured_at": captured_at or ""}


UNREAD = cell("unread")


# --------------------------------------------------------------------------
# THE CUT-OFF


def on_file_by(c: dict, cutoff: str) -> bool:
    """Was the document this cell rests on readable on or before `cutoff`?

    THREE DATES ANSWER IT, in the order scope.md's archived-source rule sets them out:

      `date`         the document's own dateline, stored padded to the EARLIEST day its
                     stated precision allows -- a year sits on 1 January, a month on the
                     first. That padding is what makes the comparison a comparison at
                     all, and it is also why a coarse date can be admitted here on a
                     period that straddles the cut-off. Those are counted and printed
                     rather than resolved: reading "2023" as 31 December to be safe would
                     be this register inventing a month the publisher did not state, in
                     the opposite direction from the padding rule.
      `captured_at`  the day of the copy on file. A capture is an existence proof: the
                     text was there on the day somebody took it. It cannot make a
                     document EARLIER than its dateline, so it is read only where the
                     dateline is missing or later.
      `not_after`    the precision a document with no dateline carries, where `date` IS
                     the capture. Handled by the first clause without a special case,
                     because the stored date is already the capture -- an upper bound
                     that says the text existed by then, which is exactly what the
                     cut-off asks.

    A CELL WITH NO DATE AT ALL FAILS THE TEST. An undated document cannot be placed
    before a cut-off, and placing it there anyway would date the register's reading from
    the day it happened to look.
    """
    for d in (c.get("date"), c.get("captured_at")):
        if d and str(d)[:10] <= cutoff:
            return True
    return False


def straddles(c: dict, cutoff: str) -> bool:
    """A pass admitted on a date whose stated precision covers days after the cut-off.

    `2023` at year precision is stored as 2023-01-01 and admitted against a cut-off of
    2023-10-31; the document may have been published in December. Not resolved, counted.
    """
    d, p = str(c.get("date") or "")[:10], c.get("precision") or ""
    if not d or not on_file_by(c, cutoff):
        return False
    if p == "year":
        return d[:4] + "-12-31" > cutoff
    if p == "month":
        import calendar
        y, m = int(d[:4]), int(d[5:7])
        return f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}" > cutoff
    return False


def apply_cutoff(cells: dict, cutoff: str) -> tuple[dict, dict]:
    """Every cell whose document is not on file by `cutoff` becomes `not_searched`.

    IT APPLIES TO A FAIL AS WELL AS TO A PASS, and that is the whole of the rule. A fail
    is a finding about the evidence examined (see the module docstring), so a fail
    resting on a document published after the cut-off is a finding nobody could have made
    on that day -- it is not a fail as of then, it is nothing as of then. Leaving it a
    fail would let the ladder score a 2023 cohort out of what this register read in 2026.
    """
    out, changed = {}, {}
    for r, c in cells.items():
        if c["result"] == "unread" or on_file_by(c, cutoff):
            out[r] = dict(c)
            continue
        d = dict(c)
        was = d["result"]
        d["result"] = "not_searched"
        d["searched"] = False
        d["note"] = (f"as of {cutoff}: the document cited is dated {c.get('date') or 'nothing'}"
                     f", after the cut-off, so this rung was {was} on evidence that did "
                     f"not exist yet")
        out[r] = d
        changed[r] = was
    return out, changed


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


def score_row(row, edges_by_project, graph_date="", funding_by_project=None,
              funder_by_key=None, funder_read=False, funder_read_on="",
              population_key="", unread_owner=()):
    """Six cells from a register row's own fields."""
    funding_by_project = funding_by_project or {}
    funder_by_key = funder_by_key or {}
    pass_award = None
    for k in (population_key, "row:" + row["id"]):
        if k and funder_by_key.get(k):
            pass_award = funder_by_key[k][0]
            break
    out = {}
    sources = row.get("sources") or []
    base = newest(sources)
    base_id = base["url"] if base else ""
    base_pub = base.get("publisher", "") if base else ""
    base_date = base.get("date", "") if base else ""
    base_prec = base.get("date_precision", "") if base else ""
    # THE CAPTURE DATE TRAVELS WITH THE CELL. scope.md's archived-source rule puts the
    # publication date in `date` and the day of the copy on file in `captured_at`, and an
    # as-of cut-off has to be able to read both -- a document whose publisher has since
    # gone dark is still a document this register held on the day it captured it.
    captured = {s["url"]: s.get("captured_at") for s in sources if s.get("captured_at")}

    # RUNG 1, SITE. The location_statement is the direct answer where there is one;
    # a located row whose position came from a company or permit source names the
    # site at least as finely. DRAWN STATUS IS NOT CONSULTED -- see scope.md.
    # THE RUNG IS "MUNICIPALITY OR FINER" AND THIS USED TO TEST "FINER THAN
    # MUNICIPALITY". Corrected 15 September 2026. Two defects, and between them
    # they failed 50 admitted rows that answer the question the rung asks:
    #
    #   A location_statement naming exactly the municipality was failed. The rung
    #   admits a municipality by its own words, so it now passes.
    #
    #   THE `plant` FIELD WAS NEVER READ, and it is where a company-stated site
    #   name actually lives on these rows: "Maasvlakte, Port of Rotterdam",
    #   "Trafford Low Carbon Energy Park, Carrington", "Pyyryvainen, Oulu". The
    #   scorer looked only at `location_statement` and at `located`, which is a
    #   question about whether somebody has DRAWN the row -- and scope.md says in
    #   as many words that position is not an admission leg and drawn status is
    #   not consulted here.
    #
    # AN ADJACENCY STILL FAILS, and that is the one case that stays. A
    # location_statement with a `relation` names a feature the project supplies or
    # is applied in -- Tata Steel IJmuiden, the BAYERNOIL refinery -- and the
    # ruling of 13 September 2026 is that adjacency does not place a row. The
    # owner is naming somebody else's works, not its own site.
    ls = row.get("location_statement")
    ls = ls[0] if isinstance(ls, list) and ls else ls
    plant = (row.get("plant") or "").strip()
    if isinstance(ls, dict) and ls.get("relation"):
        out["site"] = cell("fail", ls.get("source_url"), "owner",
                           ls.get("source_date"), ls.get("source_date_precision"),
                           f"location_statement is an adjacency ({ls['relation']}) to "
                           f"{ls.get('anchor_feature', 'another works')}, which does not "
                           f"place this row")
    elif isinstance(ls, dict):
        finer = ls.get("names_location_finer_than_municipality")
        out["site"] = cell("pass", ls.get("source_url"), "owner",
                           ls.get("source_date"), ls.get("source_date_precision"),
                           "location_statement names " +
                           ("finer than municipality" if finer else "the municipality") +
                           ", which the rung admits")
    elif row.get("located") == "yes":
        out["site"] = cell("pass", base_id, "owner", base_date, base_prec,
                           "row carries a position from a company or permit source")
    elif plant:
        out["site"] = cell("pass", base_id, base_pub or "owner", base_date, base_prec,
                           f"the admitting source names the site as {plant!r}")
    else:
        out["site"] = cell("fail", base_id, "owner", base_date, base_prec,
                           "the row names no location at municipality or finer")

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
    #
    # THIS READ THE WRONG LAYER UNTIL 15 September 2026, and it is the same defect
    # as rung 1's: `public_funding` MOVED OFF THE ROW into
    # data/transition/funding.json, where capital allocation is a node with edges
    # out of it, and this scorer went on reading `status_history` for a funder
    # event that no longer lands there. Four admitted rows with an award on file
    # from the funder itself -- IPCEI Hy2Infra for bp and RWE at Lingen, PERTE ERHA
    # for Moeve at Huelva, IPCEI for Repsol at Muskiz -- were being reported as
    # fails on a question the register had already answered.
    #
    # AND A FAIL HERE IS ONLY A FAIL IF SOMEBODY READ A FUNDER LIST. Where no
    # funder publication has been examined for an entry, the cell is
    # `not_searched`: nobody has asked whether a funder named this project, and
    # recording that as the project's failure would be a claim about the project
    # made out of a gap in this register's reading.
    funder_rows = funding_by_project.get(row["id"], [])
    award = newest([e for e in hist
                    if e.get("source_type") in FUNDER_SOURCE_TYPES
                    or e.get("event_kind") == "financing"
                    and e.get("source_type") in FUNDER_SOURCE_TYPES])
    if pass_award:
        out["funding"] = cell("pass", pass_award["source_url"], pass_award["funder"],
                              pass_award["date"], pass_award["date_precision"],
                              f"{pass_award['programme']} names "
                              f"{pass_award['project_as_published']!r}; matched on "
                              f"{pass_award['matched_on']}")
    elif funder_rows:
        f = newest(funder_rows) or funder_rows[0]
        fsrc = (f.get("sources") or [{}])[0]
        out["funding"] = cell("pass", fsrc.get("url") or base_id, "funder",
                              f.get("date"), "day",
                              f"{f.get('programme', 'a funder')} publishes an award "
                              f"naming this project")
    elif award:
        out["funding"] = cell("pass", award.get("source_url"), "funder",
                              award.get("date"), award.get("date_precision"),
                              "award published by the funder")
    else:
        owner_claim = any(e.get("status_to") == "funded" for e in hist)
        if funder_read:
            note = ("the funder lists of sources/hydrogen_funder_pass.json name no award "
                    "for this project"
                    + ("; the OWNER states one, which rung 4 does not accept"
                       if owner_claim else ""))
            out["funding"] = cell("fail", "sources/hydrogen_funder_pass.json",
                                  "eufabric funder pass", funder_read_on, "day", note,
                                  searched=True)
        else:
            note = ("the owner states an award and no funder publication has been read "
                    "for this project"
                    if owner_claim else "no funder list has been read for this project")
            out["funding"] = cell("fail", base_id, "owner", base_date, base_prec, note,
                                  searched=False)

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
    out["input"] = score_input(row, edges_by_project, graph_date, unread_owner)
    for c in out.values():
        if not c.get("captured_at") and captured.get(c.get("source")):
            c["captured_at"] = captured[c["source"]]
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


def owner_unread(edoc) -> set:
    """Rows whose own cited sources ALL failed to answer the dependency sweep.

    `owner_side` records, per row, how many sources the register cites and how many
    of them the sweep could read. A row with sources cited and none read has had the
    owner half of rung 6 asked of nothing — see score_input, and DECISION D-24 in
    sources/dependency_docket.md.
    """
    return {o["project_id"] for o in edoc.get("owner_side", [])
            if o.get("sources_cited") and not o.get("sources_read")}


def score_input(row, edges_by_project, graph_date="", unread_owner=()):
    """RUNG 6. `contract` passes, `framework` and `intent` fail, and EVERY result is
    provisional while `verdict` is null on the edge it rests on.

    AND A ROW WHOSE ONLY SOURCE DOES NOT ANSWER IS `not_searched`, not a fail.
    Rung 6 reads two source classes — the dependency graph, and the owner's own
    statement naming a supplier. The graph is a file and always answers. The owner
    half is read by the sweep out of the sources the register cites, and for eight
    rows every one of those sources refused: an archive capture that 404s, a
    corporate page behind a login, a domain that stopped resolving. Scoring those a
    `fail` said "no supplier is contracted" on a question nobody could put.

    Corrected 21 September 2026, on D-24. It is the same ruling rung 4 took on 15
    September, when it was found reporting 71 fails on a question nobody had asked,
    and the same distinction D-L2 draws: "nobody looked" and "there is nothing
    there" are different findings.

    THE CONDITION IS BOTH HALVES SILENT. A row with an edge in the graph is scored
    on the edge whatever its own sources did — the sweep found the supplier from the
    other side, which is an answer.
    """
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
    if row["id"] in unread_owner:
        c = cell("not_searched", "sources/edges.json", "eufabric dependency sweep",
                 graph_date, "day",
                 "no edge in the dependency graph names this project AND the row's "
                 "own cited sources could not be read, so the owner half of this "
                 "rung was asked of nothing; the date is the graph's newest "
                 "statement, not a sweep date", searched=False)
        c["provisional"] = True
        return c
    c = cell("fail", "sources/edges.json", "eufabric dependency sweep", graph_date,
             "day", "no edge in the dependency graph names this project; the date is "
             "the graph's newest statement, not a sweep date")
    c["provisional"] = True
    return c


# --------------------------------------------------------------------------
# SCORING A BENCHMARK ENTRY NOBODY HAS ADMITTED


def score_unadmitted(ref, rec, searched_on, unreadable, excluded=False):
    """Rung 1 is scored for EVERY entry on the external list, admitted or not; the
    admission search is what scores it. The other five have no owner document on
    file at all -- the search is the record of looking and finding none.

    AN UNREADABLE ENTRY SCORES `unread` ON ALL SIX. It is not a fail: a publisher
    this register cannot read has not been shown to have said nothing.
    """
    if unreadable:
        return {r: dict(UNREAD, note="company source unreadable; queued for a "
                        "browser pass") for r in RUNGS}

    if excluded:
        # OUT OF PERIMETER. Not scored at all: the six questions are asked of
        # projects this dataset is about, and asking them of a blue-hydrogen plant
        # or a DRI works produces six fails that say nothing about either. The
        # clause travels with the entry instead.
        return {r: cell("not_searched", "sources/report_benchmark_gap.py",
                        "eufabric perimeter", searched_on, "day",
                        "out of perimeter; not scored", searched=False)
                for r in RUNGS}

    if rec is None:
        # On the list, not in the admission search: the search covered the class
        # `not searched by eufabric` and the rest were classified before it ran.
        # NOTHING WAS READ FOR THESE, so the cells are not_searched rather than
        # fails -- a fail would be a finding about the project made out of a gap
        # in this register's own reading.
        return {r: cell("fail", "sources/hydrogen_gap_search.json", "eufabric search",
                        searched_on, "day",
                        "classified before the admission search; no owner document "
                        "on file", searched=False) for r in RUNGS}

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


def funder_cell(key, funder_by_key, funder_read, funder_read_on):
    """RUNG 4 FOR AN ENTRY THAT IS NOT A ROW. The funder lists cover the population, not
    the register, so an unadmitted entry gets the same question asked of it."""
    hit = (funder_by_key.get(key) or [None])[0]
    if hit:
        return cell("pass", hit["source_url"], hit["funder"], hit["date"],
                    hit["date_precision"],
                    f"{hit['programme']} names {hit['project_as_published']!r}; "
                    f"matched on {hit['matched_on']}")
    if funder_read:
        return cell("fail", "sources/hydrogen_funder_pass.json", "eufabric funder pass",
                    funder_read_on, "day",
                    "the funder lists of sources/hydrogen_funder_pass.json name no award "
                    "for this entry", searched=True)
    return None


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


def load_funder_pass():
    """The funder pass of brief 12: {population key: award} and whether the lists were read.

    RUNG 4 IS `searched` FOR THE WHOLE POPULATION ONCE A POPULATION-WIDE LIST HAS BEEN
    READ, which is the brief's rule and the correction to D-L2's 71 `not_searched` cells.
    The Innovation Fund's three hydrogen auctions and the four hydrogen IPCEIs are
    European-Economic-Area-wide: every entry in this population is inside the geography
    those funders publish over, so reading them asks the rung's question of every entry
    and absence from them is a finding about the entry rather than a gap in the reading.

    THE NATIONAL LISTS DO NOT WIDEN `searched` AND DO NOT NARROW IT EITHER. They add
    awards where they were read (United Kingdom, Denmark, Norway, Spain, France) and one
    of them was refused outright (RVO, the Netherlands, 200 with an empty body). The file
    records both, and the refusal is printed with the table rather than buried, because a
    funder nobody could read is a different fact from a funder who named nobody.
    """
    if not FUNDERS.exists():
        return {}, False, []
    doc = json.loads(FUNDERS.read_text(encoding="utf-8"))
    wide = [f for f in doc["funders"]
            if f.get("read") == "readable"
            and "the whole ladder population" in (f.get("covers") or "")]
    by_key = {}
    for a in doc.get("awards", []):
        if a.get("population_key"):
            by_key.setdefault(a["population_key"], []).append(a)
        if a.get("matched_to"):
            by_key.setdefault("row:" + a["matched_to"], []).append(a)
    refused = [f for f in doc["funders"] if str(f.get("read", "")).startswith("REFUSED")]
    return by_key, bool(wide), refused


def load_funding():
    """{project_id: [funding rows]} from the capital-allocation layer.

    RUNG 4 READS THIS AND NOT THE ROW. `public_funding` moved off the project into
    data/transition/funding.json, where one award can finance several projects and
    a field on the recipient could only say so by repeating itself. The rung asks
    whether a FUNDER published an award naming the project, and this file is where
    the register records exactly that.
    """
    doc = json.loads((sm.DATA / "funding.json").read_text(encoding="utf-8"))
    out = defaultdict(list)
    for f in doc.get("funding", doc if isinstance(doc, list) else []):
        tgts = f.get("finances")
        for t in (tgts if isinstance(tgts, list) else [tgts]):
            if isinstance(t, str) and t.startswith("project:"):
                out[t.split(":", 1)[1]].append(f)
    return out


def perimeter_excluded():
    """{ref: clause} for the entries the hydrogen perimeter refuses.

    READ FROM report_benchmark_gap's OWN CLASSIFIER, never re-implemented here. A
    second copy of a boundary is a boundary that drifts, and this one has already
    been argued out once: `DRI or other perimeter exclusion` is steel, fuels and
    the refusals by name; `blue` is methane reforming with capture, which is out
    of a dataset about electrolytic hydrogen.
    """
    import report_benchmark_gap as gap
    return gap.perimeter_exclusions_by_ref()


def build(cutoff: str = ""):
    iea, rows, by_ref, offlist = population()
    records, searched_on = search_records()
    cands = candidate_refs()
    unread_refs = unreadable_refs(records)
    excluded = perimeter_excluded()
    funding_by_project = load_funding()
    funder_by_key, funder_read, funder_refused = load_funder_pass()
    funder_read_on = (json.loads(FUNDERS.read_text(encoding="utf-8"))["read_on"]
                      if FUNDERS.exists() else "")

    edoc = json.loads(EDGES.read_text(encoding="utf-8"))
    edges_by_project = defaultdict(list)
    for e in edoc["edges"]:
        if e.get("project_id"):
            edges_by_project[e["project_id"]].append(e)
    graph_date = graph_read(edoc)
    unread = owner_unread(edoc)

    lines, changes, straddling = [], Counter(), Counter()

    def cut(cells):
        """Apply the cut-off, counting what it moved and what it admits on a coarse date."""
        if not cutoff:
            return cells
        out, changed = apply_cutoff(cells, cutoff)
        for r in changed:
            changes[r] += 1
        for r, c in out.items():
            if c["result"] == "pass" and straddles(c, cutoff):
                straddling[r] += 1
        return out

    for ref in sorted(iea, key=lambda x: int(x) if x.isdigit() else 0):
        entry = iea[ref]
        held = by_ref.get(ref)
        cand = cands.get(ref)
        key = f"iea:{ref}"
        if held:
            row = held[0]
            cells = score_row(row, edges_by_project, graph_date,
                              funding_by_project, funder_by_key, funder_read,
                              funder_read_on, key, unread)
            klass, rid = "admitted", row["id"]
        elif cand:
            cells = score_unadmitted(ref, records.get(ref), searched_on,
                                     ref in unread_refs)
            fc = funder_cell(key, funder_by_key, funder_read, funder_read_on)
            if fc and cells["funding"]["result"] != "unread":
                cells["funding"] = fc
            klass, rid = "admitted", cand["id"]
        else:
            unreadable = ref in unread_refs
            rec = records.get(ref)
            cells = score_unadmitted(ref, rec, searched_on, unreadable,
                                     excluded=ref in excluded)
            fc = funder_cell(key, funder_by_key, funder_read, funder_read_on)
            if fc and not unreadable and ref not in excluded:
                cells["funding"] = fc
            if unreadable:
                klass = "unread"
            elif ref in excluded:
                # A PERIMETER EXCLUSION IS NOT A PROJECT THAT FAILED TO PROVE
                # ITSELF. It is a project this dataset is not about, and scoring
                # it zero out of six put 53 entries into the failure column that
                # no amount of reading could ever move. Carried with its clause
                # and left out of the scored population entirely.
                klass = "perimeter exclusion"
            elif rec is None:
                klass = "none found"
            elif rec.get("outcome") == "owner or permit source names the site":
                klass = "named not admitted"
            else:
                klass = "none found"
            rid = ""
        lines.append(line_for(key=f"iea:{ref}", ref=ref, rid=rid, entry=entry,
                              row=held[0] if held else None, klass=klass, cells=cut(cells),
                              clause=excluded.get(ref, "")))

    for row in offlist:
        cells = score_row(row, edges_by_project, graph_date, funding_by_project,
                          funder_by_key, funder_read, funder_read_on,
                          f"row:{row['id']}", unread)
        lines.append(line_for(key=f"row:{row['id']}", ref="", rid=row["id"],
                              entry=None, row=row, klass="admitted", cells=cut(cells)))
    return lines, iea, offlist, changes, straddling


def line_for(key, ref, rid, entry, row, klass, cells, clause=""):
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
            "stop_event": stop, "perimeter_clause": clause}
    passed = 0
    for r in RUNGS:
        c = cells[r]
        line[f"{r}_result"] = c["result"]
        line[f"{r}_source"] = c["source"]
        line[f"{r}_speaker"] = c["speaker"]
        line[f"{r}_date"] = c["date"]
        line[f"{r}_precision"] = c["precision"]
        line[f"{r}_searched"] = "true" if c.get("searched", True) else "false"
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
           "stop_event", "perimeter_clause", "rungs_passed", "unread"]
          + [f"{r}_{f}" for r in RUNGS
             for f in ("result", "searched", "source", "speaker", "date",
                       "precision", "note")]
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
    # THE POPULATION HAS THREE PARTS AND ONLY ONE OF THEM IS SCORED.
    # Ruled 15 September 2026. "Rungs passed" used to be reported over all 245
    # entries, which put 53 perimeter exclusions and 21 unreadable entries into the
    # zero-rung column and made the ladder look like a register that had failed to
    # confirm 122 projects. It had failed to confirm 48.
    excluded = [l for l in lines if l["register_class"] == "perimeter exclusion"]
    unread = [l for l in lines if l["unread"] == "true"]
    scored = [l for l in lines
              if l["register_class"] != "perimeter exclusion" and l["unread"] != "true"]
    scored_by_passed = Counter(l["rungs_passed"] for l in scored)
    keys = sorted(scored_by_passed, key=lambda k: int(k))
    identity = (f"{len(excluded)} perimeter exclusions + {len(unread)} unread + "
                + " + ".join(f"{scored_by_passed[k]} at {k}" for k in keys)
                + f" rungs = {len(lines)}")
    not_searched = {r: sum(1 for l in scored if l[f"{r}_result"] == "not_searched")
                    for r in RUNGS}
    return {
        "_comment": [
            "COMPUTED FROM sources/ladder/hydrogen.csv BY build_ladder.py.",
            "Never edited by hand: the reconciliation gate check_ladder.py recomputes",
            "it and refuses a mismatch. See scope.md, 'The ladder is computed, never",
            "typed'.",
            "",
            "THREE POPULATIONS, AND `rungs_passed` IS REPORTED ON ONE OF THEM.",
            "A perimeter exclusion is a project this dataset is not about; an unread",
            "entry is a publisher this register could not reach. Neither is a project",
            "that failed to confirm itself, and scoring them zero out of six said that",
            "they were.",
        ],
        "population": len(lines),
        "population_structure": {
            "perimeter_exclusions": len(excluded),
            "unread": len(unread),
            "scored": len(scored),
            "identity": identity,
            "identity_holds": len(excluded) + len(unread) + len(scored) == len(lines),
        },
        "scored_entries_by_rungs_passed":
            {str(k): scored_by_passed[k] for k in keys},
        "not_searched_cells_among_scored": not_searched,
        "entries_by_rungs_passed_all_245_deprecated":
            {str(k): by_passed[k] for k in sorted(by_passed, key=lambda x: int(x))},
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


ASOF_CSV = "hydrogen_asof_{}.csv"


def asof_path(cutoff: str):
    """sources/ladder/hydrogen_asof_2023-10.csv for a cut-off inside October 2023.

    NAMED BY THE MONTH AND NOT BY THE DAY, because a cut-off is a reading of a month's
    state and two cut-offs a fortnight apart are the same table with a different edge.
    The exact day is in the file's own `as_of` column on every line.
    """
    return OUTDIR / ASOF_CSV.format(cutoff[:7])


def main() -> int:
    check = "--check" in sys.argv
    cutoff = ""
    if "--as-of" in sys.argv:
        cutoff = sys.argv[sys.argv.index("--as-of") + 1]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cutoff):
            print("build_ladder --as-of takes a full YYYY-MM-DD. A cut-off padded from a "
                  "month\n  would claim a day nobody chose.")
            return 2
    if not benchmark_available():
        # REPORTED, NOT FAILED. Fetching here would put api.iea.org in the build's
        # critical path and cache a file this repository may not redistribute.
        print("build_ladder: the IEA benchmark is not cached on this machine, so the "
              "ladder is not recomputed.\n  The committed files stand and "
              "check_ladder.py reconciles them against benchmark_snapshots.json.")
        return 0

    lines, iea, offlist, changes, straddling = build(cutoff)

    if cutoff:
        # THE AS-OF TABLE IS A SECOND FILE AND NEVER OVERWRITES THE LADDER. The ladder
        # is what this register can see today; the as-of table is what it could have seen
        # on a day, and a reader has to be able to hold both.
        out = asof_path(cutoff)
        out.parent.mkdir(parents=True, exist_ok=True)
        fields = list(FIELDS) + ["as_of"]
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for l in lines:
                w.writerow(dict(l, as_of=cutoff))
        print(f"build_ladder --as-of {cutoff}: {len(lines)} entries -> "
              f"{out.relative_to(ROOT)}")
        print(f"\n  CELLS THAT CHANGED CLASS UNDER THE CUT-OFF — each one rested on a "
              f"document\n  published after {cutoff}, so as of that day it was not a pass "
              f"and not a fail\n  but a rung nobody had evidence on:\n")
        print(f"    {'rung':10} {'changed':>8} {'of':>6}")
        for r in RUNGS:
            print(f"    {r:10} {changes[r]:>8} {len(lines):>6}")
        print(f"    {'total':10} {sum(changes.values()):>8} {len(lines) * len(RUNGS):>6}"
              f"   cells")
        if sum(straddling.values()):
            print(f"\n  AND {sum(straddling.values())} PASSES REST ON A DATE COARSER THAN "
                  f"THE CUT-OFF. A document dated to a year\n  is stored on 1 January, "
                  f"which the cut-off admits, and may have been published after it.\n"
                  f"  Counted rather than resolved: reading a year as its last day would "
                  f"invent a month.\n")
            for r in RUNGS:
                if straddling[r]:
                    print(f"    {r:10} {straddling[r]:>8}")
        after = Counter(l["rungs_passed"] for l in lines
                        if l["register_class"] != "perimeter exclusion"
                        and l["unread"] != "true")
        print(f"\n  SCORED ENTRIES BY RUNGS PASSED, as of {cutoff}: "
              + ", ".join(f"{after[k]} at {k}" for k in sorted(after)))
        return 0

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

#!/usr/bin/env python3
"""THE 2023-POPULATION TEST: the ladder's own population, scored as of its own October
and joined to what became of it. Brief 13.

    python3 sources/build_hydrogen_test.py            # writes both files, prints the tables
    python3 sources/build_hydrogen_test.py --check    # rebuilds and diffs

WHAT THE POPULATION IS, AND HOW IT DIFFERS FROM BRIEF 12'S COHORT. The 255 European
entries at 100 MW and above in the October 2023 vintage, by IEA reference number -- THE
LADDER'S OWN POPULATION AS IT STOOD AT THE CUT-OFF. Brief 12's cohort was the 73 entries
announced for 2023 at any size, and its first finding was that the two populations do not
meet: none of the 73 reached the threshold the ladder is filtered to. This one is the
instrument's population frozen at a past day, so an as-of score over it is a test of the
instrument rather than of a sample drawn beside it.

THE TWO FREEZES BIND HERE. The rung tests are frozen at a9542fe (D-B1) and the outcome
definitions at 58ce11f (D-C1), both by commit hash and both before the data arrived.
Nothing in this file may loosen either. What it does is join them.

THE INSTRUMENT IS ONE INSTRUMENT ACROSS THE POPULATION. Sixty-one of the 255 are admitted
rows and 194 are not, and it would have been easy to score the rows off their own fields
and the rest off the archive pass -- which is what the live ladder does, because the live
ladder is asking what this register can see TODAY. As of 31 October 2023 that would have
been two instruments: a row's sources are mostly dated 2024 to 2026 and the cut-off rule
turns them into `not_searched`, so the rows would have scored lower than unadmitted
entries whose 2023 captures happen to be on file. So EVERY entry is scored from the same
archive pass, and a row's own sources enter that pass as a leg like any other, fetched at
their last capture at or before the cut-off. Rungs 4 and 6 are the exceptions and they are
exceptions in the brief: the funder pass and the dependency graph are population-wide
files with their own dates, read here exactly as brief 12 read them.

THE OUTCOME IS THIS REGISTER'S READING, UNDER FROZEN DEFINITIONS, AND IT IS NOT A STATUS.
`sources/hydrogen_test_2023_outcome.json` carries one outcome per entry with its source,
its speaker and its date, written by a person from the documents that pass fetched. The
six values and the assessment date of 30 September 2026 are scope.md's, fixed at 58ce11f.

NO MODEL. Counts only, which is the brief's instruction: five cross-tabs, a coverage
table, and the independent check against the entries Odenweller and Ueckerdt themselves
quality-checked.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import build_hydrogen_drift as drift  # noqa: E402
import build_ladder as L  # noqa: E402
import hydrogen_test_2023 as t23  # noqa: E402
import hydrogen_test_outcome as tout  # noqa: E402

ROOT = bench.ROOT
REVIEW = ROOT / "sources" / "hydrogen_test_2023_review.json"
CSV_OUT = ROOT / "sources" / "ladder" / "test_2023.csv"
JSON_OUT = ROOT / "sources" / "ladder" / "test_2023_summary.json"
CUTOFF = t23.CUTOFF
ASSESSED_ON = tout.ASSESSED_ON
OUTCOMES = ("operating", "committed", "pending", "delayed", "stopped", "unread",
            "not_read_yet")
BANDS = ((100, 200), (200, 500), (500, 1000), (1000, 10 ** 9))

# THE FROZEN COMMITS, NAMED IN THE FILE THEY GOVERN so that a reader of the table does not
# have to find the docket to know what it was scored under.
FROZEN_RUNGS = "a9542fe28f93eac7f66a3050070af6db93684e7e"
FROZEN_OUTCOMES = "58ce11f0282a44368f4842176a4844d49aa416d2"


def band(mw) -> str:
    if mw is None:
        return "(no capacity)"
    for lo, hi in BANDS:
        if lo <= mw < hi:
            return f"{lo}-{hi} MW" if hi < 10 ** 9 else f"{lo}+ MW"
    return "(below the threshold)"


# --------------------------------------------------------------------------
# SCORING ONE ENTRY AS OF THE CUT-OFF


def readable_pre_cutoff(entry: dict, hosts: dict) -> list[dict]:
    """Every leg of this entry readable from a capture dated at or before the cut-off.

    THE FULL SET, NOT THE FIRST ONE. The host legs are included -- they are this entry's
    legs, held once per host so the same front page is not fetched nine times -- and the
    list is what a fail cites, so a fail says which documents were examined.
    """
    legs = list(entry.get("fetches") or [])
    for h in entry.get("host_legs") or []:
        legs += (hosts.get(h) or {}).get("legs") or []
    return [g for g in legs if g.get("archived") and g.get("captured_at")
            and g["captured_at"] <= CUTOFF and (g.get("text_chars") or 0) >= 400]


def hand(entry: dict, key: str, default=None):
    """A hand-written field, or its default while nobody has written one."""
    v = entry.get(key)
    return default if v is None else v


def score(entry: dict, rev: dict, hosts: dict, funder_by_key, funder_read, funder_on,
          row, edges_by_project, graph_date, clause=""):
    """The six rungs for one entry of the 2023 population, as of the cut-off.

    THE CELLS COME FROM THE HAND REVIEW OF THE ARCHIVE PASS, and where the review has
    found nothing the cell is a fail citing the documents that were read -- which is what
    a fail is for. Where NO document dated at or before the cut-off is on file the cells
    are `not_searched`, because a fail would be a finding about the project made out of a
    gap in this register's own reading. Ruled 15 September 2026, and it is the whole
    reason `searched` is a field.
    """
    pre = readable_pre_cutoff(entry, hosts)
    src_of_looking = "sources/hydrogen_test_2023.json"
    covered = bool(hand(rev, "owner_or_permit_pre_cutoff", False))
    cells = {}

    if not pre:
        # NOTHING A 2023 READER COULD HAVE HELD. Reported, not scored.
        why = ("no reference of this entry answered a declared reader"
               if not (entry.get("fetches") or entry.get("host_legs"))
               else "no document of this entry is on file from a capture dated at or "
                    "before the cut-off")
        for r in L.RUNGS:
            cells[r] = L.cell("fail", src_of_looking, "eufabric 2023 population test",
                              CUTOFF, "day", f"{why}; the archive pass is the record of "
                              f"looking", searched=False)
    elif not covered:
        # DOCUMENTS, BUT NONE OF THEM THE OWNER'S OR A PERMIT AUTHORITY'S. The rungs ask
        # what a particular speaker said, so press coverage of a project answers none of
        # them -- and a fail read off a trade title would be this register scoring a
        # publisher's silence as an owner's.
        cited = pre[0]["read_url"]
        for r in L.RUNGS:
            cells[r] = L.cell("fail", cited, "eufabric 2023 population test",
                              pre[0]["captured_at"], "not_after",
                              f"{len(pre)} document(s) on file from at or before the "
                              f"cut-off, none of them the owner's or a permit "
                              f"authority's", searched=False)
    else:
        best = hand(rev, "owner_or_permit_url") or pre[0]["read_url"]
        best_cap = next((g["captured_at"] for g in pre if g["read_url"] == best),
                        pre[0]["captured_at"])
        for r, field, note in (
                ("site", "site_named",
                 "the owner or permit sources read name no site at municipality or finer"),
                ("capacity", "capacity_as_stated",
                 "the owner or permit sources read state no capacity"),
                ("fid", "fid_stated",
                 "the owner or permit sources read do not state that FID has been taken"),
                ("start", "start_as_stated",
                 "the owner or permit sources read state no operation start with a "
                 "precision this register can record")):
            got = hand(rev, field)
            if got:
                cells[r] = L.cell(
                    "pass", hand(rev, f"{r}_source", best),
                    hand(rev, f"{r}_speaker", "owner"),
                    hand(rev, f"{r}_date", best_cap),
                    hand(rev, f"{r}_precision", "not_after"),
                    f"archive pass, hand verdict: {got}",
                    captured_at=hand(rev, f"{r}_captured_at", best_cap))
            else:
                cells[r] = L.cell("fail", best, "eufabric 2023 population test", best_cap,
                                  "not_after", f"archive pass, hand verdict: {note}",
                                  captured_at=best_cap)
        got = hand(rev, "input_stated")
        if got:
            cells["input"] = L.cell(
                "pass", hand(rev, "input_source", best),
                hand(rev, "input_speaker", "owner"), hand(rev, "input_date", best_cap),
                hand(rev, "input_precision", "not_after"),
                f"archive pass, hand verdict: {got}", captured_at=best_cap)
        else:
            cells["input"] = L.cell("fail", best, "eufabric 2023 population test",
                                    best_cap, "not_after",
                                    "no owner statement naming a supplier at firmness "
                                    "contract in the sources read",
                                    captured_at=best_cap)

    # RUNG 4 IS THE FUNDER'S QUESTION AND IT IS ASKED OF THE WHOLE POPULATION, exactly as
    # brief 12 asks it: the Innovation Fund's auctions and the hydrogen IPCEIs publish
    # over this geography, so absence from them is a finding about the entry.
    fc = L.funder_cell(f"iea:{entry['ref']}", funder_by_key, funder_read, funder_on)
    if fc is not None:
        cells["funding"] = fc

    # RUNG 6 READS THE DEPENDENCY GRAPH WHERE THERE IS A ROW TO READ IT FOR. The graph is
    # keyed by project id and 194 of these entries have none, so for those the cell stays
    # what the archive pass made it.
    if row is not None:
        cells["input"] = L.score_input(row, edges_by_project, graph_date)

    if clause:
        # OUT OF PERIMETER. The clause travels with the entry as a covariate and the cells
        # still carry what was read, per D-C2: the perimeter classifier covers only the
        # entries still in the current vintage, so splitting this population on it would
        # split it unevenly.
        for r in L.RUNGS:
            cells[r] = dict(cells[r], note=cells[r]["note"] + f"; {clause}")

    cut, _changed = L.apply_cutoff(cells, CUTOFF)
    return cut, pre, covered


# --------------------------------------------------------------------------
# THE OUTCOME SIDE


def announced_start(entry: dict, rev: dict) -> tuple[str, str, str, str]:
    """The announced start, and WHICH of the two rules gave it.

    scope.md: the owner's stated start as of the cut-off where one exists, otherwise the
    2023 vintage's own `Date online`, and the line records which. A vintage year is a
    LIST CLAIM and the line says so in the speaker column, because the whole point of the
    rungs is that a list saying 2027 and an owner saying 2027 are different facts.
    """
    owner = hand(rev, "announced_start") or hand(rev, "start_as_stated")
    if owner:
        return (str(owner), hand(rev, "announced_start_precision", "year"),
                hand(rev, "announced_start_speaker", "owner"),
                "owner, stated at or before the cut-off")
    dv = (entry.get("date_online_2023_vintage") or "").strip()
    return (dv, "year" if dv else "", "IEA list claim, October 2023 vintage" if dv else "",
            "2023 vintage Date online" if dv else "neither: the vintage states no year")


def start_year(value: str):
    try:
        return int(float(str(value)[:4]))
    except (TypeError, ValueError):
        return None


def outcome_of(rev: dict) -> str:
    return hand(rev, "outcome", "not_read_yet")


# --------------------------------------------------------------------------
# THE INDEPENDENT CHECK, brief 13 item 6


def owner_mw(stated: str):
    """MEGAWATTS FROM THE OWNER'S OWN SENTENCE, OR NOTHING. No conversion, ever.

    scope.md, "Three units for one electrolyser, and no conversion between them": an owner
    stating 30,000 tonnes a year and a list stating 200 MWel are two claims in two units,
    and turning one into the other to make them agree or disagree would be this register
    inventing an efficiency neither speaker stated. So a comparison happens only where the
    owner states megawatts, and "not comparable, the owner states another unit" is a
    result of the check rather than a gap in it.
    """
    if not stated:
        return None
    s = str(stated).lower().replace(",", "").replace("\u00a0", " ")
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(gw|mw)", s)
    if not m:
        return None
    v = float(m.group(1))
    return v * 1000 if m.group(2) == "gw" else v


def independent_check(pop, rev_by_ref):
    """Odenweller and Ueckerdt's validated size and date, beside the owner's own.

    WHO IS "VALIDATED". The 2023 quality-checked workbook carries a `Refs (quality check)`
    column, and an entry with one is an entry the authors went and checked themselves --
    their reference, their date checked, their comment. That is the set. An entry without
    one carries the IEA's figures as the IEA published them, and comparing those to an
    owner would be a check on the IEA rather than on the authors' work.

    DISAGREEMENTS ARE RECORDED, NOT RESOLVED, which is the brief's instruction and the
    standing rule: two speakers on the same fact, in any field, is a disagreement and the
    register holds both.
    """
    out = []
    for e in pop:
        if not e["quality_check_reference_numbers"]:
            continue
        rev = rev_by_ref.get(e["ref"], {})
        os_size = hand(rev, "capacity_as_stated", "")
        os_start = hand(rev, "start_as_stated", "")
        mw = owner_mw(os_size)
        if not os_size:
            size_verdict = "not read: no owner capacity on file from before the cut-off"
        elif mw is None:
            size_verdict = "not comparable: the owner states another unit"
        elif e["capacity_mwel"] is None:
            size_verdict = "not comparable: the vintage states no MWel"
        elif abs(mw - e["capacity_mwel"]) < 0.5:
            size_verdict = "agree"
        else:
            size_verdict = "disagree"
        oy, vy = start_year(os_start), start_year(e["date_online_2023_vintage"])
        if not os_start:
            date_verdict = "not read: no owner start on file from before the cut-off"
        elif oy is None or vy is None:
            date_verdict = "not comparable"
        elif oy == vy:
            date_verdict = "agree"
        else:
            date_verdict = "disagree"
        qc = e["quality_check_references"][0] if e["quality_check_references"] else {}
        out.append({
            "iea_ref": e["ref"], "name": e["name"],
            "validated_size": e["announced_size"],
            "validated_mwel": e["capacity_mwel"],
            "validated_date_online": e["date_online_2023_vintage"],
            "authors_checked_on": qc.get("date_checked", ""),
            "authors_comment": qc.get("comment", ""),
            "owner_stated_size": os_size, "owner_stated_mw": mw,
            "owner_stated_start": os_start,
            "size": size_verdict, "date": date_verdict,
        })
    return out


# --------------------------------------------------------------------------
# THE LINES


FIELDS = (["iea_ref", "name", "country", "capacity_value", "capacity_unit",
           "capacity_band", "technology", "status_2023_vintage",
           "announced_start", "announced_start_precision", "announced_start_speaker",
           "announced_start_read_from", "rungs_cleared_as_of"]
          + [f"{r}_{f}" for r in L.RUNGS for f in ("result", "source", "speaker", "date",
                                                   "precision", "note")]
          + ["coverage", "documents_pre_cutoff", "readable_2026_documents",
             "outcome", "outcome_speaker", "outcome_source", "outcome_date",
             "outcome_date_precision", "outcome_note", "new_start", "slip_years",
             "paused", "resumption_date", "dropped_from_benchmark",
             "benchmark_departure_kind", "in_current_iea_vintage", "register_class",
             "row_id", "row_event_written", "perimeter_clause",
             "quality_checked_by_authors", "as_of", "assessed_on"])


def review_by_ref():
    doc = json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() \
        else {"entries": []}
    return {e["ref"]: e for e in doc["entries"]}


def check_block():
    rows = independent_check(t23.population(), review_by_ref())
    return {"entries": len(rows), "rows": rows,
            "size": dict(Counter(r["size"] for r in rows)),
            "date": dict(Counter(r["date"] for r in rows)),
            "_comment": ("DISAGREEMENTS ARE RECORDED AND NOT RESOLVED. Where the owner "
                         "and the authors' validated figure differ, both are on the line "
                         "and neither is corrected: scope.md, 'A disagreement is two "
                         "speakers on the same fact, in any field'.")}


def build():
    archive = json.loads(t23.OUT.read_text(encoding="utf-8")) if t23.OUT.exists() \
        else {"entries": [], "hosts": {}}
    by_ref = {e["ref"]: e for e in archive["entries"]}
    hosts = archive.get("hosts") or {}
    outc = json.loads(tout.OUT.read_text(encoding="utf-8")) if tout.OUT.exists() \
        else {"entries": []}
    oc_by_ref = {e["ref"]: e for e in outc["entries"]}
    # THE ONE FILE A PERSON WRITES. Both machine passes carry `verdict: null` and neither
    # is ever edited by hand; every judgement -- who was speaking, what they stated, and
    # which of the six outcomes it is -- lives here, keyed by IEA reference, so that the
    # review can be diffed against the documents it was written from. scope.md, "A
    # machine classification never writes to the record".
    review = json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() \
        else {"entries": []}
    rev_by_ref = {e["ref"]: e for e in review["entries"]}

    funder_by_key, funder_read, _refused = L.load_funder_pass()
    funder_on = (json.loads(L.FUNDERS.read_text(encoding="utf-8"))["read_on"]
                 if L.FUNDERS.exists() else "")
    edoc = json.loads(L.EDGES.read_text(encoding="utf-8"))
    edges_by_project = defaultdict(list)
    for e in edoc["edges"]:
        for p in bench.as_list(e.get("project")) or []:
            edges_by_project[p].append(e)
    graph_date = L.graph_read(edoc)
    rows_by_ref = t23.register_rows_by_ref()
    clauses = L.perimeter_excluded()

    cur_pop = drift.population("iea_hydrogen_production_projects", None)
    cur_file = drift.whole_file(None)
    rowrefs, candrefs = drift.register_references()
    qc_refs = {e["ref"] for e in t23.population()
               if e["quality_check_reference_numbers"]}

    lines = []
    for e in t23.population():
        ref = e["ref"]
        entry = by_ref.get(ref, dict(e, fetches=[], host_legs=[]))
        oc = oc_by_ref.get(ref, {})
        rev = rev_by_ref.get(ref, {})
        row = rows_by_ref.get(ref)
        cells, pre, covered = score(entry, rev, hosts, funder_by_key, funder_read,
                                    funder_on, row, edges_by_project, graph_date,
                                    clauses.get(ref, ""))
        a_start, a_prec, a_speaker, a_from = announced_start(entry, rev)
        # THE DEPARTURE IS COUNTED TWO WAYS, on the ruling of 17 September 2026: the
        # publisher dropping an entry and the publisher revising it below the threshold
        # are not the same fact, and only the first is what rule 17 is about.
        if ref in cur_pop:
            dropped, kind = "no", ""
        elif ref in cur_file:
            dropped, kind = "no", ("still in the current file, revised below the "
                                   "threshold")
        else:
            dropped, kind = "yes", "not in the current file at any size"
        line = {
            "iea_ref": ref, "name": e["name"], "country": e["country"],
            "capacity_value": e["capacity_mwel"] if e["capacity_mwel"] is not None else "",
            "capacity_unit": "MWel" if e["capacity_mwel"] is not None else "",
            "capacity_band": band(e["capacity_mwel"]),
            "technology": e["technology"],
            "status_2023_vintage": e["status_2023_vintage"],
            "announced_start": a_start, "announced_start_precision": a_prec,
            "announced_start_speaker": a_speaker, "announced_start_read_from": a_from,
            "coverage": ("owner or permit document at or before the cut-off" if covered
                         else "documents but none of them the owner's or a permit "
                              "authority's" if pre
                         else "no document at or before the cut-off"),
            "documents_pre_cutoff": len(pre),
            "readable_2026_documents": oc.get("readable_2026_documents", ""),
            "outcome": outcome_of(rev),
            "outcome_speaker": hand(rev, "outcome_speaker", ""),
            "outcome_source": hand(rev, "outcome_source", ""),
            "outcome_date": hand(rev, "outcome_date", ""),
            "outcome_date_precision": hand(rev, "outcome_date_precision", ""),
            "outcome_note": hand(rev, "outcome_note", ""),
            "new_start": hand(rev, "new_start", ""),
            "slip_years": hand(rev, "slip_years", ""),
            "paused": "yes" if hand(rev, "paused", False) else "",
            "resumption_date": hand(rev, "resumption_date", ""),
            "dropped_from_benchmark": dropped, "benchmark_departure_kind": kind,
            "in_current_iea_vintage": "yes" if ref in cur_file else "no",
            "register_class": ("admitted, a row here" if ref in rowrefs
                               else "candidate, not yet a row" if ref in candrefs
                               else "never seen by this register"),
            "row_id": (row or {}).get("id", ""),
            "row_event_written": hand(rev, "row_event_written", ""),
            "perimeter_clause": clauses.get(ref, ""),
            "quality_checked_by_authors": "yes" if ref in qc_refs else "no",
            "as_of": CUTOFF, "assessed_on": ASSESSED_ON,
        }
        passed = 0
        for r in L.RUNGS:
            c = cells[r]
            line[f"{r}_result"] = c["result"]
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


# --------------------------------------------------------------------------
# THE SUMMARY, COMPUTED FROM THE CSV AND NOT ALONGSIDE IT


def crosstab(lines, rowkey, colkey, cols=None):
    t = defaultdict(Counter)
    for l in lines:
        t[str(l[rowkey]) if not isinstance(l[rowkey], int) else l[rowkey]][str(l[colkey])] += 1
    out = {}
    for k in sorted(t, key=lambda x: (isinstance(x, str), x)):
        out[str(k)] = {c: t[k][c] for c in (cols or sorted(t[k])) if t[k][c] or cols}
        out[str(k)]["total"] = sum(t[k].values())
    return out


def summarise(lines, rows_from_csv=None, check=None):
    lines = rows_from_csv if rows_from_csv is not None else lines
    check = check or {"entries": 0, "rows": [], "size": {}, "date": {}}
    scored = [l for l in lines if str(l["rungs_cleared_as_of"]).isdigit()]
    covered = [l for l in lines
               if l["coverage"].startswith("owner or permit document")]
    uncovered = [l for l in lines
                 if not l["coverage"].startswith("owner or permit document")]
    per_rung = {}
    for r in L.RUNGS:
        t = defaultdict(Counter)
        for l in lines:
            t[l[f"{r}_result"]][l["outcome"]] += 1
        per_rung[r] = {k: dict(v, total=sum(v.values())) for k, v in sorted(t.items())}
    cov_by_status = Counter()
    cov_total_by_status = Counter()
    for l in lines:
        s = l["status_2023_vintage"] or "(none)"
        cov_total_by_status[s] += 1
        if int(l["documents_pre_cutoff"]):
            cov_by_status[s] += 1
    cov_by_band = Counter()
    cov_total_by_band = Counter()
    for l in lines:
        cov_total_by_band[l["capacity_band"]] += 1
        if int(l["documents_pre_cutoff"]):
            cov_by_band[l["capacity_band"]] += 1
    return {
        "_comment": [
            "COMPUTED FROM sources/ladder/test_2023.csv BY build_hydrogen_test.py.",
            "Never edited by hand: --check rebuilds it from the csv and diffs, and the",
            "csv is itself rebuilt from the archive pass, the outcome pass and the two",
            "frozen rule sets. See scope.md, 'The ladder is computed, never typed'.",
            "",
            "COUNTS ONLY. The brief asks for the cross-tabs and nothing else: no model,",
            "no rate, no fitted anything. A 255-line table with six outcome classes and",
            "seven rung levels does not support one, and printing one would invite a",
            "reader to take selection from archive coverage for a finding about projects.",
        ],
        "population": len(lines),
        "as_of": CUTOFF,
        "assessed_on": ASSESSED_ON,
        "frozen_rung_tests_at": FROZEN_RUNGS,
        "frozen_outcome_definitions_at": FROZEN_OUTCOMES,
        "coverage": {
            "entries_with_a_document_at_or_before_the_cutoff":
                sum(1 for l in lines if int(l["documents_pre_cutoff"])),
            "entries_with_an_owner_or_permit_document": len(covered),
            "entries_with_no_document_at_or_before_the_cutoff":
                sum(1 for l in lines if not int(l["documents_pre_cutoff"])),
            "by_2023_status": {s: {"covered": cov_by_status[s],
                                   "total": cov_total_by_status[s]}
                               for s in sorted(cov_total_by_status)},
            "by_capacity_band": {b: {"covered": cov_by_band[b],
                                     "total": cov_total_by_band[b]}
                                 for b in sorted(cov_total_by_band)},
        },
        "rungs_cleared_against_outcome": crosstab(lines, "rungs_cleared_as_of", "outcome"),
        "each_rung_against_outcome": per_rung,
        "status_2023_against_outcome": crosstab(lines, "status_2023_vintage", "outcome"),
        "rungs_cleared_against_dropped_from_benchmark":
            crosstab(lines, "rungs_cleared_as_of", "dropped_from_benchmark"),
        "outcome_of_covered_against_uncovered": {
            "covered": dict(Counter(l["outcome"] for l in covered)),
            "uncovered": dict(Counter(l["outcome"] for l in uncovered)),
            "_comment": ("SELECTION FROM ARCHIVE COVERAGE, PUT WHERE IT CAN BE SEEN. "
                         "Whether an entry has an owner's document on file from before "
                         "the cut-off is a fact about the archive and about this "
                         "register's reading, not about the project. If the two columns "
                         "have different outcome distributions then the rungs are being "
                         "scored on a selected part of the population, and any statement "
                         "about the instrument has to carry that."),
        },
        "scored_entries": len(scored),
        "perimeter_exclusions": sum(1 for l in lines if l["perimeter_clause"]),
        "outcomes_not_read_yet": sum(1 for l in lines if l["outcome"] == "not_read_yet"),
        "independent_check": check,
    }


# --------------------------------------------------------------------------
# RENDERING


def render(tab, rowlabel, cols):
    w = max([len(rowlabel)] + [len(str(k)) for k in tab]) if tab else len(rowlabel)
    head = f"  {rowlabel:{w}} " + " ".join(f"{c[:13]:>13}" for c in cols) + f" {'total':>7}"
    out = [head, "  " + "-" * (len(head) - 2)]
    tot = Counter()
    for k, row in tab.items():
        out.append(f"  {str(k):{w}} " + " ".join(f"{row.get(c, 0):>13}" for c in cols)
                   + f" {row.get('total', 0):>7}")
        for c in cols:
            tot[c] += row.get(c, 0)
        tot["total"] += row.get("total", 0)
    out.append(f"  {'total':{w}} " + " ".join(f"{tot[c]:>13}" for c in cols)
               + f" {tot['total']:>7}")
    return "\n".join(out)


def csv_text(lines) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\r\n")
    w.writeheader()
    for l in lines:
        w.writerow(l)
    return buf.getvalue()


def read_csv():
    with CSV_OUT.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not (drift.available() and t23.OUT.exists()):
        print("build_hydrogen_test: the cached vintages or the archive pass are not on "
              "this machine,\n  so the test table is not recomputed. The committed files "
              "stand.")
        return 0
    lines = build()
    text = csv_text(lines)
    if a.check:
        cur = CSV_OUT.read_text(encoding="utf-8") if CSV_OUT.exists() else ""
        if text != cur:
            print("build_hydrogen_test --check: sources/ladder/test_2023.csv is not what "
                  "the population,\n  the archive pass and the outcome pass produce. Run "
                  "build_hydrogen_test.py.")
            return 1
        want = summarise(lines, read_csv(), check_block())
        have = json.loads(JSON_OUT.read_text(encoding="utf-8")) if JSON_OUT.exists() else {}
        if json.dumps(want, sort_keys=True) != json.dumps(have, sort_keys=True):
            print("build_hydrogen_test --check: the summary is not what the csv "
                  "produces.")
            return 1
        print(f"build_hydrogen_test --check: {len(lines)} entries, the table and the "
              f"summary match their sources.")
        return 0

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for l in lines:
            w.writerow(l)
    # THE SUMMARY IS COMPUTED FROM THE FILE ON DISK, not from the objects in memory, so
    # that the two cannot disagree about anything the csv round-trip changes.
    s = summarise(lines, read_csv(), check_block())
    JSON_OUT.write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    print(f"THE 2023-POPULATION TEST: {len(lines)} European entries at 100 MW and above "
          f"in the\nOctober 2023 vintage, scored as of {CUTOFF} under the rung tests "
          f"frozen at {FROZEN_RUNGS[:7]}\nand assessed as of {ASSESSED_ON} under the "
          f"outcome definitions frozen at {FROZEN_OUTCOMES[:7]}.\n")
    c = s["coverage"]
    print(f"  with a document captured at or before the cut-off: "
          f"{c['entries_with_a_document_at_or_before_the_cutoff']:>3} of {len(lines)}")
    print(f"  of those, an owner's or a permit authority's:      "
          f"{c['entries_with_an_owner_or_permit_document']:>3}")
    print(f"  with nothing at or before the cut-off:             "
          f"{c['entries_with_no_document_at_or_before_the_cutoff']:>3}"
          f"  (reported, not scored)")
    print("\nCOVERAGE BY 2023-VINTAGE STATUS\n")
    print(render({k: {"covered": v["covered"], "total": v["total"]}
                  for k, v in c["by_2023_status"].items()}, "status",
                 ["covered"]))
    print("\nCOVERAGE BY CAPACITY BAND\n")
    print(render({k: {"covered": v["covered"], "total": v["total"]}
                  for k, v in c["by_capacity_band"].items()}, "band", ["covered"]))
    live = [o for o in OUTCOMES if any(l["outcome"] == o for l in lines)]
    print(f"\nRUNGS CLEARED AS OF {CUTOFF} AGAINST THE OUTCOME AS OF {ASSESSED_ON}\n")
    print(render(s["rungs_cleared_against_outcome"], "rungs", live))
    print("\nEACH RUNG'S RESULT AGAINST THE OUTCOME\n")
    for r in L.RUNGS:
        print(f"  rung {L.RUNGS.index(r) + 1}, {r}")
        print(render(s["each_rung_against_outcome"][r], "result", live))
        print()
    print("THE 2023 VINTAGE'S OWN STATUS AGAINST THE OUTCOME\n")
    print(render(s["status_2023_against_outcome"], "status", live))
    print("\nRUNGS CLEARED AGAINST LEAVING THE BENCHMARK\n")
    print(render(s["rungs_cleared_against_dropped_from_benchmark"], "rungs",
                 ["yes", "no"]))
    o = s["outcome_of_covered_against_uncovered"]
    print("\nTHE OUTCOME OF COVERED ENTRIES AGAINST UNCOVERED ONES\n")
    print(render({"covered": dict(o["covered"], total=sum(o["covered"].values())),
                  "uncovered": dict(o["uncovered"],
                                    total=sum(o["uncovered"].values()))},
                 "coverage", live))
    chk = s["independent_check"]
    print(f"\nTHE INDEPENDENT CHECK: the {chk['entries']} entries Odenweller and "
          f"Ueckerdt quality-checked themselves,\ntheir validated size and date beside "
          f"the owner's own as found from before the cut-off.\n")
    print(f"  {'ref':>5}  {'validated':>12} {'owner':>12}  {'size':<12} "
          f"{'val. date':>9} {'owner':>7}  {'date':<12} name")
    for r in chk["rows"]:
        print(f"  {r['iea_ref']:>5}  {str(r['validated_mwel'] or ''):>12} "
              f"{str(r['owner_stated_mw'] or '-'):>12}  {r['size'][:12]:<12} "
              f"{str(r['validated_date_online'] or ''):>9} "
              f"{str(r['owner_stated_start'] or '-'):>7}  {r['date'][:12]:<12} "
              f"{r['name'][:34]}")
    print(f"\n  size:  " + ", ".join(f"{k} {v}" for k, v in chk["size"].items()))
    print(f"  date:  " + ", ".join(f"{k} {v}" for k, v in chk["date"].items()))
    print(f"\n  -> {CSV_OUT.relative_to(ROOT)}\n  -> {JSON_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

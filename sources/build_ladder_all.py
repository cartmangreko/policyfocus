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
import re
import sys
import urllib.parse
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

FIELDS = (["sector", "layer", "key", "list_key", "row_id", "name", "country", "register_class",
           "list_status", "capacity_value", "capacity_unit", "perimeter_clause",
           "rungs_passed", "scored", "unread"]
          + [f"{r}_{f}" for r in RUNGS
             for f in ("result", "searched", "source", "speaker", "medium", "date",
                       "precision", "note")]
          + [f"{r}_speaker_type" for r in RUNGS]
          + [f"{r}_result_amended" for r in RUNGS]
          + ["rungs_passed_amended", "outcome_class_amended", "input_provisional",
             "target_year_owner", "target_year_owner_source",
             "target_year_list", "target_year_list_source",
             "target_year", "target_year_source"])


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
    if hit and L.award_is_terminated(hit.get("funder_status_as_published")):
        # D-A28. THE STATUS THE FUNDER PUBLISHES IS PART OF THE AWARD IT PUBLISHES.
        # This cell printed `the funder's own status is Terminated` inside a PASS, and
        # build_ladder_all --queue has been printing the same four rows as a fact a
        # rung revealed that no row carries. The rung reads the word now.
        return L.cell("fail", hit["source_url"], hit["funder"], hit["date"],
                      hit["date_precision"],
                      f"THE FUNDER'S OWN RECORD SAYS THE AWARD IS TERMINATED. "
                      f"{hit['programme']} names {hit['project_as_published']!r} at "
                      f"{hit['amount_as_stated']} and gives its status as "
                      f"{hit['funder_status_as_published']!r}; withdrawn funding is "
                      f"excluded (D-A28). The project's status does not move on it.")
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
    return by_project, swept, L.graph_read(edoc), L.owner_unread(edoc)


def input_cell(row, row_id, by_project, swept, graph_date, unread_owner=()):
    """RUNG 6. `contract` passes; `framework` and `intent` fail; and a row the
    dependency sweep never reached is `not_searched`, not a fail.

    THE SWEEP'S REACH IS PART OF THE ANSWER. Brief 9 read the owner side of 117
    projects and recorded each in `owner_side`; a row outside that list has had no
    supplier question asked of it, and D-L2 is explicit that "nobody looked" and
    "there is nothing there" are different findings.
    """
    if row is not None and row_id in swept:
        return L.score_input(row, by_project, graph_date, unread_owner)
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
    a = e.get("admission") or {}
    # RUNG 1 IS SCORED OFF THE DOCUMENT THE CENSUS READ, not off the class name.
    # Corrected 20 September 2026 (D-A11). A census admits a works because it read a
    # company document naming it, and it records that document; scoring rung 1 from
    # a generic "none names a site" sentence failed 20 admitted steel works on
    # evidence that was sitting in the entry. And a `named not admitted` entry whose
    # own note says FAILED LEG: SITE must FAIL rung 1 — passing every entry of that
    # class scored the class rather than the evidence.
    # THE FAILED LEG IS THE LEG, NOT THE SENTENCE ABOUT IT. This tested whether
    # "site" appeared anywhere in the failed_leg text, and a leg recorded as
    # "CAPACITY — the owner names the site and states no GWh" contains the word
    # `site` while failing on capacity. The same substring-on-prose mistake as the
    # Sines-inside-business screen of D-A5 and the name-derived hosts of L9; it is
    # the third time in three days and the fix is the same each time — read the
    # field, not the paragraph.
    _leg = re.split(r"[—,;:(]", (a.get("failed_leg") or ""), 1)[0].strip().lower()
    site_is_the_failed_leg = _leg.startswith("site") or _leg == "site"
    # D-A32: KEYED ON THE SOURCE'S TYPE, NOT ON `admitted_by`. The branch below was
    # written for exactly this case on 20 September and never fired on the three rows
    # that needed it, because `admitted_by` is "" on all three while the admitting
    # document is a CINEA fiche. `grant_register` is the funder's own award record.
    if klass == "admitted" and (a.get("admitted_by") == "funder"
                                or (a.get("source_type") or "") == "grant_register"):
        # THE AMENDMENT OF 20 SEPTEMBER ADMITS ON A FUNDER AND MOVES NO RUNG. Rung 1
        # asks whether the OWNER OR THE PERMITTING AUTHORITY names the site, and a
        # funder is neither. A funder-admitted entry with no owner document fails
        # rung 1 and clears rung 4, which is the pattern that made the amendment
        # necessary and is the whole reason it is allowed to change nothing here.
        out["site"] = L.cell(
            "fail", a.get("source") or src, a.get("speaker") or "funder", on, "day",
            "ADMITTED BY THE FUNDER AND THE OWNER LEG IS OPEN. The admitting document "
            "is a funder's award record, and rung 1 asks for the owner or the "
            "permitting authority. An owner look is queued under rule 17.")
    elif (klass == "admitted" and a.get("source")
          and (a.get("source_type") or "") not in sm.SITE_SPOKEN):
        # D-A32. The census recorded the document and the ladder passed rung 1 on it
        # without asking whose it was.
        out["site"] = L.cell(
            "fail", a["source"], a.get("speaker") or "", on, "day",
            f"ADMITTED ON A {(a.get('source_type') or 'untyped').upper()} DOCUMENT AND "
            f"RUNG 1 ASKS THE OWNER OR THE PERMITTING AUTHORITY (D-A32): "
            f"{(a.get('verbatim') or '')[:120]}")
    elif klass == "admitted" and a.get("source"):
        out["site"] = L.cell(
            "pass", a["source"], a.get("speaker") or "owner", on, "day",
            f"the census admitted this works on the owner's own document, which "
            f"names {a.get('municipality') or 'the works'}: "
            f"{(a.get('verbatim') or '')[:160]}")
    elif (klass == "named not admitted" and a.get("source")
          and not site_is_the_failed_leg
          and (a.get("source_type") or "") not in sm.SITE_SPOKEN):
        out["site"] = L.cell(
            "fail", a["source"], a.get("speaker") or "", on, "day",
            f"THE NAMING DOCUMENT IS A {(a.get('source_type') or 'untyped').upper()} "
            f"ONE AND RUNG 1 ASKS THE OWNER OR THE PERMITTING AUTHORITY (D-A32): "
            f"{(a.get('verbatim') or '')[:120]}")
    elif klass == "named not admitted" and a.get("source") and not site_is_the_failed_leg:
        out["site"] = L.cell(
            "pass", a["source"], a.get("speaker") or "owner or permit source", on,
            "day",
            f"the census read an owner or permit source that names the site and the "
            f"perimeter still refuses the entry on another leg"
            + (f" ({a['failed_leg']})" if a.get("failed_leg") else "") + ": "
            + (a.get("verbatim") or "")[:140])
    elif klass == "named not admitted" and site_is_the_failed_leg:
        out["site"] = L.cell(
            "fail", src, "eufabric census", on, "day",
            f"the census named this entry and refused it ON THE SITE LEG: "
            f"{a['failed_leg']}. A list naming a company and a country is not an "
            f"owner naming a works.")
    elif klass == "admitted" or klass == "named not admitted":
        out["site"] = L.cell(
            "fail", src, "eufabric census", on, "day",
            "the census records no owner or permit document for this entry")
    else:
        out["site"] = L.cell("fail", src, "eufabric census", on, "day",
                             "the census read the owner's own sources and none names a "
                             "site for this project"
                             + (f"; {len(a['looked_in_order'])} sources read in order"
                                if a.get("looked_in_order") else ""))
    for r in ("capacity", "fid", "start"):
        out[r] = L.cell("fail", src, "eufabric census", on, "day",
                        "no owner document on file; the census is the record of looking")
    out["funding"] = funding_cell(e["key"], by_key, read_on)
    out["input"] = input_cell(None, "", by_project, swept, graph_date)
    return out


# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# THE MEDIUM OF A RUNG CELL, and the press-quoted amendment


TRADE_PRESS = re.compile(
    r"trade press|Battery-News|SteelOrbis|GMK Center|Offshore Energy|Kallanish|"
    r"Bioenergy International|Il Sole|Reuters|Montel|Recharge|H2 View|Hydrogen Insight|"
    r"Argus|Platts|S&P Global", re.I)
QUOTES_THE_OWNER = re.compile(
    r"reported by [^,]+ from the compan|quoted in its own|quoting the owner|"
    r"the owner's own words|from the company's (own )?(release|statement|presentation)",
    re.I)
FUNDER_SPEAK = re.compile(r"CINEA|European Commission|Innovation Fund|IPCEI|"
                          r"grant register|funder pass", re.I)
PERMIT_SPEAK = re.compile(r"permit|authority|planning|environmental|omgeving|préfect", re.I)


def medium_of(c: dict) -> str:
    """WHAT KIND OF DOCUMENT A CELL RESTS ON. Five values and they are not a ranking.

    `owner`                the company's own site, release, report or filing
    `permit`               a permitting or planning authority
    `funder`               a funder's own register or award document
    `press_quoting_owner`  a trade or general title QUOTING THE OWNER DIRECTLY
    `press`                a title reporting in its own voice
    `register`             this register's own census, search or dependency graph

    THE DISTINCTION THE AMENDMENT TURNS ON IS THE LAST TWO. A newspaper saying a
    company will build a plant is the newspaper speaking; the same newspaper printing
    the company's own sentence is the company speaking through it, and refusing that
    would refuse the most common way a company's words reach a reader. The steel
    census already ruled this once, from the other side: D-S4's Taranto correction
    refused a newspaper's REPORT of what a company told a ministry, and the ruling
    said the perimeter asks for company confirmation. The amendment says the same
    thing precisely rather than by host.
    """
    sp, src, note = c.get("speaker") or "", c.get("source") or "", c.get("note") or ""
    blob = f"{sp} {note}"
    if src.startswith("sources/") or "eufabric" in sp.lower():
        return "register"
    if FUNDER_SPEAK.search(sp):
        return "funder"
    if TRADE_PRESS.search(blob):
        return "press_quoting_owner" if QUOTES_THE_OWNER.search(blob) else "press"
    if PERMIT_SPEAK.search(sp):
        return "permit"
    return "owner"


# --------------------------------------------------------------------------
# THE STATED TARGET YEAR, AND WHOSE IT IS
#
# THE OWNER FIRST AND THE LIST ONLY WHERE THE LIST HAS A FIELD. The brief's order,
# ruled 27 September 2026: the owner's own stated start year where the row carries one,
# then the list's own year WHERE THE LIST PUBLISHES ONE AS A FIELD, and otherwise `no
# stated year`. Never the machine's estimate and NEVER A YEAR PARSED OUT OF A NOTE —
# the IEA CCUS list carries no year field at all, and its operation years exist only
# inside prose this register wrote about it ("the IEA calls it Planned with operation
# 2032"). Reading a year out of that sentence would be this register quoting itself
# into a data column, which is the shape of every defect in these dockets.
#
# SO THREE SECTORS HAVE NO LIST-SIDE FALLBACK: hydrogen (the IEA hydrogen list carries
# a status and no year), cement and transport and storage (the IEA CCUS list carries
# status, type and capacity). Batteries has `year_as_published` from Battery-News and
# T&E; steel has LeadIT's `planned_commissioning` and `actual_start_year` and GEM's
# `forward_units[].start`. Where the owner is silent in the other three, the line says
# `no stated year`, which is a fact about what anybody has published.

YEAR = re.compile(r"\b(20\d{2})\b")


def _year_of(v) -> str:
    m = YEAR.search(str(v or ""))
    return m.group(1) if m else ""


def owner_target_year(row) -> tuple[str, str]:
    """(year, source) from the row's own stated_schedule, or ('', '').

    THE START MILESTONES ARE build_ladder's AND SO IS THE SPEAKER TEST, so the column
    and rung 5 read the same field on the same terms: production_start, commissioning or
    operation_start, dated, and stated in the OWNER'S OWN DOCUMENT. `fid_target` is not a
    start. The newest such statement wins, and the precision the owner gave is carried in
    the source string rather than dropped — a 2029 at `year` and a 2029-06 at `month` are
    both the year 2029 and the column says which it was.

    D-A30 PUT THE SPEAKER TEST HERE TOO, and Envision at Navalmoral de la Mata is why: a
    column called `target_year_owner` was reading the Junta de Extremadura's 2028-12
    timetable out of a regional newspaper, because that statement is the newest. AESC's
    own release saying 2026 was on file all along. A column named for a speaker must hold
    that speaker's number or it is worse than no column.
    """
    if row is None:
        return "", ""
    cands = [x for x in (row.get("stated_schedule") or [])
             if x.get("milestone") in L.START_MILESTONES and _year_of(x.get("target_date"))
             and x.get("source_type") == "company"]
    if not cands:
        return "", ""
    best = L.newest(cands) or cands[0]
    return (_year_of(best.get("target_date")),
            f"owner: {best.get('source_url') or 'no url on the statement'} "
            f"({best.get('milestone')} {best.get('target_date')} at "
            f"{best.get('target_precision') or 'no precision'})")


def list_target_year(e) -> tuple[str, str]:
    """(year, source) from a STRUCTURED field on the list's own claim, or ('', '')."""
    for c in e.get("list_claims") or []:
        for field in ("year_as_published", "planned_commissioning", "actual_start_year"):
            y = _year_of(c.get(field))
            if y:
                return y, f"list: {c.get('benchmark') or 'the list'} {field}={c[field]!r}"
        for u in c.get("forward_units") or []:
            y = _year_of(u.get("start"))
            if y:
                return y, (f"list: {c.get('benchmark') or 'the list'} "
                           f"forward_units start={u.get('start')!r} "
                           f"({u.get('kind')} {u.get('unit')})")
    return "", ""


def target_year_columns(e, row) -> dict:
    """The owner's year, the list's year, and the one the bands read — all four columns.

    THE TWO SPEAKERS GET A COLUMN EACH, ruled 27 September 2026. A single column with a
    source string could say which speaker won and could not say what the other one said,
    so the disagreement between them was computable only by a script outside the gate.
    Now `target_year` is DERIVED — the owner's where there is one, the list's otherwise —
    and both inputs sit beside it, which is the same shape the register uses everywhere
    else: keep what each party said, and derive the reading.
    """
    oy, osrc = owner_target_year(row)
    ly, lsrc = list_target_year(e)
    if oy:
        y, src = oy, osrc
    elif ly:
        y, src = ly, lsrc
    else:
        y, src = "no stated year", "none: neither the owner nor the list publishes a year"
    return {"target_year_owner": oy, "target_year_owner_source": osrc,
            "target_year_list": ly, "target_year_list_source": lsrc,
            "target_year": y, "target_year_source": src}


def year_gap(line) -> int | None:
    """|owner - list| where both are years, else None."""
    a, b = line.get("target_year_owner") or "", line.get("target_year_list") or ""
    if a.isdigit() and b.isdigit():
        return abs(int(a) - int(b))
    return None


def target_band(year: str) -> str:
    """The four bands the brief asks for. A band is a bucket and not a judgement."""
    if not year or not year.isdigit():
        return "no stated year"
    y = int(year)
    if y <= 2027:
        return "up to 2027"
    if y <= 2030:
        return "2028-2030"
    return "after 2030"


# --------------------------------------------------------------------------
# WHO CONFIRMED A CELL, AS A TYPE RATHER THAN AS FREE TEXT
#
# THE `speaker` COLUMN IS A NAME AND IT IS NOT A VOCABULARY. It holds 94 bare
# `owner`s, then company names — Eni UK, Heidelberg Materials, Tree Energy Solutions —
# and `company`, `eu`, `host_government`, `funder`, `eufabric census`. A table of who
# confirms cannot be computed off that without grouping names by hand, which is a table
# nobody can recompute. `speaker_type` is the typed column; `speaker` keeps the name,
# because the name is the more useful fact once the type is available.
#
# IT IS DERIVED INDEPENDENTLY OF `medium`, deliberately. medium_of() reads the speaker
# and the note; this reads the speaker and the SOURCE. Two derivations that disagree
# are a finding — see L12, which is exactly such a disagreement on two rows — and one
# derivation that feeds the other could not produce one.

SPEAKER_TYPES = ("owner", "permit", "funder", "supplier", "press", "host_government",
                 "register", "other")

# A GOVERNMENT BODY IS A FUNDER WHEN IT IS PUBLISHING AN AWARD, and a government
# otherwise. `iea:1969` passes rung 4 on DESNZ's own Hydrogen Production Business Model
# allocation at gov.uk — which is precisely what the frozen test means by "a national
# programme" — and a classifier that read DESNZ as the owner of the plant would make the
# who-confirms table say the company confirmed its own funding. So the rung is part of
# the question: on rung 4 a state body speaking is a funder; anywhere else it is
# `host_government`, which is a different thing a reader may want counted.
# THE HOSTS A TRADE TITLE PUBLISHES ON. Used only to COUNT the blind spot above; no
# result is computed from it, because changing what `medium` means is L12's job and this
# brief adds no rule.
TRADE_HOST = re.compile(
    r"offshore-energy|globalcement|cemnet|battery-news|batteriesnews|steelorbis|"
    r"gmk\.center|kallanish|hydrogeninsight|rechargenews|reuters|bloomberg|prnewswire|"
    r"globenewswire|businesswire|electrive|carbonherald|bioenergy-news|energy-pedia|"
    r"pv-magazine|ess-news|energynews|carboncapturemagazine", re.I)

GOV_HOST = re.compile(r"(^|\.)(gov\.uk|europa\.eu|gob\.es|gouv\.fr|bund\.de|"
                      r"kormany\.hu|government\.(se|no|nl)|regjeringen\.no|rvo\.nl)$",
                      re.I)
GOV_BODY = re.compile(r"DESNZ|BEIS|Ministry|Ministerio|Ministère|Bundesministerium|"
                      r"RVO|Bpifrance|Enova|NVE|Vinnova|Energimyndigheten|"
                      r"department for|agency", re.I)
SUPPLIER_WORDS = re.compile(r"supplier|OEM|licensor|technology provider|Axens|Capsol|"
                            r"Calix|Leilac|Carbon Clean|Polysius|SLB|Topsoe|Nel|"
                            r"Siemens Energy|thyssenkrupp nucera|Cummins|Plug Power",
                            re.I)


def speaker_type_of(c: dict, rung: str = "") -> str:
    """One of SPEAKER_TYPES for a rung cell. `register` is this register's own files."""
    sp = str(c.get("speaker") or "")
    src = str(c.get("source") or "")
    low = sp.lower()
    host = urllib.parse.urlsplit(src).netloc.lower() if src.startswith("http") else ""
    if src.startswith("sources/") or "eufabric" in low:
        return "register"
    if FUNDER_SPEAK.search(sp) or low in ("funder", "eu"):
        return "funder"
    state = (low == "host_government" or GOV_BODY.search(sp)
             or (host and GOV_HOST.search(host)))
    if state:
        return "funder" if rung == "funding" else "host_government"
    if PERMIT_SPEAK.search(sp):
        return "permit"
    if SUPPLIER_WORDS.search(sp):
        return "supplier"
    if TRADE_PRESS.search(sp):
        return "press"
    if low in ("owner", "company") or sp:
        return "owner"
    return "other"


def amend(cells_line: dict) -> tuple[dict, str]:
    """THE PRESS-QUOTED AMENDMENT, applied to one line. Returns the amended rung
    results and the outcome class.

    A PASS THAT RESTS ON A TITLE SPEAKING IN ITS OWN VOICE STOPS BEING A PASS, and
    an entry whose only passing evidence was of that kind gets the outcome class
    `press only` — which is a statement about the EVIDENCE and not about the project,
    exactly as `unread` is. A pass that rests on a title quoting the owner stands,
    because the speaker is the owner.

    BOTH TABLES ARE PRINTED. The frozen columns stay in the file beside the amended
    ones so the change is legible rather than retroactive, which is what brief 13's
    amendment did and what this follows.
    """
    out, lost = {}, 0
    for r in RUNGS:
        res, med = cells_line[f"{r}_result"], cells_line[f"{r}_medium"]
        if res == "pass" and med == "press":
            out[r] = "fail"
            lost += 1
        else:
            out[r] = res
    passes = sum(1 for r in RUNGS if out[r] == "pass")
    if cells_line["scored"] != "true":
        klass = ""
    elif lost and passes == 0:
        klass = "press only"
    elif lost:
        klass = "press dropped, other evidence stands"
    else:
        klass = ""
    return out, klass


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
    line = {"sector": sector, "layer": lp.LAYER[sector], "key": e["key"], "list_key": e["key"].split(":", 1)[-1]
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
        line[f"{r}_medium"] = medium_of(c)
        line[f"{r}_speaker_type"] = speaker_type_of(c, r)
        if r == "input":
            line["input_provisional"] = "true" if c.get("provisional") else "false"
        if c["result"] == "pass":
            passed += 1
    line["rungs_passed"] = passed
    line["unread"] = "true" if all(cells[r]["result"] == "unread" for r in RUNGS) else "false"
    line["scored"] = "false" if (line["register_class"] in lp.NOT_SCORED
                                 or line["register_class"] == "benchmark aggregate"
                                 or line["unread"] == "true") else "true"
    line.update(target_year_columns(e, row))
    am, klass = amend(line)
    for r in RUNGS:
        line[f"{r}_result_amended"] = am[r]
    line["rungs_passed_amended"] = sum(1 for r in RUNGS if am[r] == "pass")
    line["outcome_class_amended"] = klass
    return line


HYDROGEN_CSV = OUTDIR / "hydrogen.csv"


def hydrogen_lines(rows=None):
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
    rows = rows or {}
    out = []
    with open(HYDROGEN_CSV, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            n = {"sector": "hydrogen", "layer": lp.LAYER["hydrogen"],
                 "key": l["key"], "list_key": l["iea_ref"],
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
            for r in RUNGS:
                cell = {"speaker": l[f"{r}_speaker"], "source": l[f"{r}_source"],
                        "note": l[f"{r}_note"]}
                n[f"{r}_medium"] = medium_of(cell)
                n[f"{r}_speaker_type"] = speaker_type_of(cell, r)
            # THE HYDROGEN LIST CARRIES A STATUS AND NO YEAR, so hydrogen's target year
            # is the owner's or nothing. The row is looked up rather than rescored:
            # hydrogen.csv is read here, not recomputed (see this function's docstring).
            n.update(target_year_columns(
                {"list_claims": []}, rows.get(l["row_id"]) if l["row_id"] else None))
            # `unread` is a register class in the hydrogen table and a cell state
            # here; both mean the same thing and the scored flag reads either.
            n["scored"] = "false" if (n["register_class"] in lp.NOT_SCORED
                                      or n["register_class"] == "unread"
                                      or n["unread"] == "true") else "true"
            am, klass = amend(n)
            for r in RUNGS:
                n[f"{r}_result_amended"] = am[r]
            n["rungs_passed_amended"] = sum(1 for r in RUNGS if am[r] == "pass")
            n["outcome_class_amended"] = klass
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
    by_project, swept, graph_date, unread_owner = graph()
    rows = {p["id"]: p for p in sm.load("project")}
    funding_by_project = L.load_funding()
    hyd_funder, hyd_read, _ = L.load_funder_pass()

    lines = hydrogen_lines(rows)
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
                cells["input"] = input_cell(row, e["row_id"], by_project, swept,
                                            graph_date, unread_owner)
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
            "per_rung_amended": {
                r: {"pass": sum(1 for l in scored
                                if l[f"{r}_result_amended"] == "pass")} for r in RUNGS},
            "medium_of_passing_cells": {
                r: dict(Counter(l[f"{r}_medium"] for l in scored
                                if l[f"{r}_result"] == "pass")) for r in RUNGS},
            "outcome_class_amended": dict(Counter(
                l["outcome_class_amended"] for l in scored if l["outcome_class_amended"])),
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
    PRODUCING = [x for x in SECTORS if lp.LAYER[x] == "producing"]
    INFRA = [x for x in SECTORS if lp.LAYER[x] == "infrastructure"]
    for s2 in SECTORS:
        out["sectors"][s2]["layer"] = lp.LAYER[s2]

    def roll(group):
        ls = [l for l in lines if l["layer"] == group]
        sc = [l for l in ls if l["scored"] == "true"]
        return {"sectors": [x for x in SECTORS if lp.LAYER[x] == group],
                "population": len(ls), "scored": len(sc),
                "per_rung": {r: {"pass": sum(1 for l in sc if l[f"{r}_result"] == "pass"),
                                 "of_scored": len(sc),
                                 "pass_rate_of_scored": round(
                                     sum(1 for l in sc if l[f"{r}_result"] == "pass")
                                     / len(sc), 3) if sc else None}
                             for r in RUNGS}}

    # ------------------------------------------------------------------
    # THE FIVE CROSS-TABS, added 26 September 2026 for the paper's table. Each one
    # is a PAIR of checks read together, because the interesting thing about this
    # ladder is not how often a rung clears but which rungs clear WITHOUT the rung a
    # reader would expect beside them. Computed here from the csv's own lines like
    # everything else in this file, and --check refuses a difference.

    def _passes(l, *rungs):
        return all(l[f"{r}_result"] == "pass" for r in rungs)

    def _per_sector(pred):
        d = {s2: sum(1 for l in lines
                     if l["sector"] == s2 and l["scored"] == "true" and pred(l))
             for s2 in SECTORS}
        d["all_sectors"] = sum(d.values())
        return d

    producing_scored = [l for l in lines
                        if l["layer"] == "producing" and l["scored"] == "true"]
    # THE LIST STATUS AGAINST THE OWNER'S OWN FID. Steel is IN on GEM's own six values
    # (corrected 27 September 2026: the 103-of-147 count that kept it out was over the
    # whole population, and 31 of its 49 SCORED lines carry a status). Batteries is out
    # on a count that does hold — all 57 scored lines are blank, the benchmark being a
    # chart — and the two infrastructure sectors are out because their lists status a
    # pipeline and a reservoir rather than a plant.
    FID_VS_LIST = ("hydrogen", "cement", "steel")
    BUILT_OR_BUILDING = {"hydrogen": ("FID/Construction",),
                         "cement": ("Under construction", "Operational"),
                         "steel": ("Construction", "Operating")}
    out["cross_tabs"] = {
        "_comment": [
            "FIVE PAIRS, computed from sources/ladder/all.csv over SCORED lines only.",
            "A perimeter exclusion and an unread entry are not in any of them: neither",
            "failed to confirm itself, on D-L1.",
            "Rung names in this repository are site, capacity, fid, funding, start,",
            "input; `checks` in the paper's wording is the same six."],
        "checks_passed_distribution_producing_layer": {
            "_comment": ("how many of the six each scored line of the producing layer "
                         "clears; the infrastructure layer is summarised under `layers` "
                         "and is deliberately not averaged into this"),
            "scored": len(producing_scored),
            "sectors": [x for x in SECTORS if lp.LAYER[x] == "producing"],
            "distribution": {str(k): v for k, v in sorted(Counter(
                l["rungs_passed"] for l in producing_scored).items())}},
        "funding_pass_without_fid_pass": {
            "_comment": ("a funder has confirmed the money and the owner has not said "
                         "the decision is made — the pair that says where public money "
                         "is ahead of the company's own commitment"),
            "count": _per_sector(lambda l: _passes(l, "funding")
                                 and l["fid_result"] != "pass"),
            "of_funding_passes": _per_sector(lambda l: _passes(l, "funding"))},
        "site_pass_without_capacity_pass": {
            "_comment": ("the owner names where and does not say how big; the pair that "
                         "separates a located project from a specified one"),
            "count": _per_sector(lambda l: _passes(l, "site")
                                 and l["capacity_result"] != "pass"),
            "of_site_passes": _per_sector(lambda l: _passes(l, "site"))},
        "site_capacity_fid": {
            "_comment": ("located, sized and decided on the owner's own documents — the "
                         "three rungs that rest on nobody but the company"),
            "count": _per_sector(lambda l: _passes(l, "site", "capacity", "fid"))},
        "site_capacity_fid_start": {
            "_comment": "the same three plus a start date the owner has put a precision on",
            "count": _per_sector(lambda l: _passes(l, "site", "capacity", "fid",
                                                   "start"))},
        "list_status_vs_owner_fid": {
            "_comment": [
                "THE LIST'S OWN STATUS COLUMN AGAINST RUNG 3, which is the owner saying "
                "the decision is made. A list that calls a project FID/Construction "
                "while no owner document says FID has been taken is the disagreement "
                "this register exists to make visible.",
                "STEEL IS IN, ON GEM'S OWN VOCABULARY, AND THE EARLIER REASON FOR "
                "LEAVING IT OUT WAS WRONG. It said 103 of 147 lines carry no list "
                "status, which is true of the whole population and not of the scored "
                "one: 18 of steel's 49 scored lines are blank and the other 31 carry "
                "GEM's six values — Announced, Construction, Finalized (research & "
                "testing), Cancelled, Operating, Paused or postponed. Construction and "
                "Operating against rung 3 are exactly the pair this table is for. "
                "Corrected 27 September 2026.",
                "BATTERIES IS OUT and the reason is a count that holds: all 57 of its "
                "scored lines carry no list status, because the benchmark is a chart "
                "with no status column. The two infrastructure sectors are out because "
                "their lists status a pipeline and a reservoir rather than a plant."],
            "sectors": list(FID_VS_LIST),
            "excluded": {
                "batteries": "all 57 scored lines carry no list status — the benchmark "
                             "is a chart with no status column",
                "transport and storage": "an infrastructure list, not a plant list"},
            # THE COMBINED LINE THE PAPER QUOTES. Five stage values across the three
            # sectors say the list believes the thing is being built or is running —
            # hydrogen FID/Construction, cement Under construction and Operational,
            # steel Construction and Operating — and rung 3 asks whether the owner has
            # said the decision was taken. `Finalized (research & testing)` is NOT in it:
            # a finished pilot is not a works under construction, and folding it in would
            # move the line without saying so.
            "built_or_building_vs_owner_fid": {
                "stages": {"hydrogen": ["FID/Construction"],
                           "cement": ["Under construction", "Operational"],
                           "steel": ["Construction", "Operating"]},
                "lines": sum(1 for l in lines if l["scored"] == "true"
                             and l["sector"] in FID_VS_LIST
                             and l["list_status"] in BUILT_OR_BUILDING.get(l["sector"], ())),
                "owner_fid_pass": sum(1 for l in lines if l["scored"] == "true"
                                      and l["sector"] in FID_VS_LIST
                                      and l["list_status"] in BUILT_OR_BUILDING.get(l["sector"], ())
                                      and l["fid_result"] == "pass"),
                "per_sector": {s2: {
                    "lines": sum(1 for l in lines if l["scored"] == "true"
                                 and l["sector"] == s2
                                 and l["list_status"] in BUILT_OR_BUILDING.get(s2, ())),
                    "owner_fid_pass": sum(1 for l in lines if l["scored"] == "true"
                                          and l["sector"] == s2
                                          and l["list_status"] in BUILT_OR_BUILDING.get(s2, ())
                                          and l["fid_result"] == "pass")}
                    for s2 in FID_VS_LIST}},
            "table": {s2: {ls: dict(Counter(
                l["fid_result"] for l in lines
                if l["sector"] == s2 and l["scored"] == "true"
                and (l["list_status"] or "(none)") == ls))
                for ls in sorted({(l["list_status"] or "(none)") for l in lines
                                  if l["sector"] == s2 and l["scored"] == "true"})}
                for s2 in FID_VS_LIST}},
    }

    # ------------------------------------------------------------------
    # THE THREE TABLES OF THE STAGE-YEAR BRIEF, 27 September 2026. Each is the six
    # checks counted against something OUTSIDE the ladder — the list's own stage, the
    # stated target year, and who owns the plant — so that a reader can ask whether
    # confirmation tracks what the list claims, when the plant is meant to run, and
    # whether the owner has to file with anybody.

    def _six(group):
        """The six checks over one group of lines, with the group's size beside them."""
        return {"lines": len(group),
                **{r: sum(1 for l in group if l[f"{r}_result"] == "pass")
                   for r in RUNGS}}

    def _scored(sector=None, pred=None):
        return [l for l in lines if l["scored"] == "true"
                and (sector is None or l["sector"] == sector)
                and (pred is None or pred(l))]

    # 1 — BY THE LIST'S OWN STAGE. Hydrogen, cement and steel split by their lists'
    # own vocabularies; batteries takes one row because all 57 of its scored lines are
    # blank; and the lines on NO list at all are their own group rather than being
    # folded into a blank-status bucket, because "the list says nothing" and "there is
    # no list" are different facts.
    stage_tabs = {}
    for sector in ("hydrogen", "cement", "steel"):
        sc = _scored(sector)
        stages = sorted({(l["list_status"] or "no list stage") for l in sc if l["list_key"]})
        stage_tabs[sector] = {
            "vocabulary": ("the IEA hydrogen list's own status column"
                           if sector == "hydrogen" else
                           "the IEA CCUS database's own status column"
                           if sector == "cement" else
                           "GEM's own status column, six values"),
            "stages": {st: _six([l for l in sc if l["list_key"]
                                 and (l["list_status"] or "no list stage") == st])
                       for st in stages}}
    bat = _scored("batteries")
    stage_tabs["batteries"] = {
        "vocabulary": "none",
        "reason": (f"all {len(bat)} scored lines carry no list stage: the benchmark is "
                   f"Transport & Environment's chart and Battery-News's table, neither "
                   f"of which publishes a status column"),
        "stages": {"no list stage": _six(bat)}}
    off_list = [l for l in lines if l["scored"] == "true" and not l["list_key"]]
    stage_tabs["not_on_any_list"] = {
        "vocabulary": "none — these lines are register rows with no line on any list",
        "sectors": dict(Counter(l["sector"] for l in off_list)),
        "stages": {"not on any list": _six(off_list)}}

    # 2 — BY THE STATED TARGET YEAR, all five sectors. The band comes from the
    # `target_year` column, whose source is the owner first and a structured list field
    # second; see target_year_of().
    BANDS = ("up to 2027", "2028-2030", "after 2030", "no stated year")
    year_tabs = {}
    for sector in SECTORS:
        sc = _scored(sector)
        year_tabs[sector] = {
            "source_split": dict(Counter(
                l["target_year_source"].split(":")[0] for l in sc)),
            "bands": {b: _six([l for l in sc if target_band(l["target_year"]) == b])
                      for b in BANDS}}
    year_tabs["all_sectors"] = {
        "source_split": dict(Counter(
            l["target_year_source"].split(":")[0] for l in _scored())),
        "bands": {b: _six([l for l in _scored() if target_band(l["target_year"]) == b])
                  for b in BANDS}}
    # AND THE PRODUCING LAYER ON ITS OWN, WHICH IS WHAT THE PAPER REPORTS. A pipeline
    # and a reservoir answer rung 2 six times in 102 and rung 5 twice; averaging them
    # into a statement about plants describes neither, which is the ruling `layers`
    # already rests on. Both versions are in the file so the difference is legible.
    prod = [l for l in _scored() if l["layer"] == "producing"]
    year_tabs["producing_layer"] = {
        "_comment": ("the paper's version: hydrogen, batteries, cement and steel, "
                     "without the two infrastructure sectors"),
        "sectors": [x for x in SECTORS if lp.LAYER[x] == "producing"],
        "source_split": dict(Counter(
            l["target_year_source"].split(":")[0] for l in prod)),
        "bands": {b: _six([l for l in prod if target_band(l["target_year"]) == b])
                  for b in BANDS}}
    # THE TWO SPEAKERS DISAGREEING BY MORE THAN A YEAR, computed and named. A year is
    # not a claim about confirmation, so this moves no rung; it is the kind of thing the
    # register exists to make visible, and it is a count with row ids rather than a
    # sentence about batteries. The rows' own `disagreements` blocks wait for a reading
    # pass — each needs the speaker's sentence — and that is queued as L15.
    gaps = [(l, year_gap(l)) for l in _scored()]
    year_tabs["owner_versus_list"] = {
        "_comment": [
            "OVER SCORED LINES WHERE BOTH THE OWNER AND THE LIST PUBLISH A YEAR.",
            "`disagree_by_more_than_a_year` is the brief's threshold; the rows are named "
            "so a reader can go to them, and the two years are printed with each.",
            "NOT WRITTEN ONTO THE ROWS: a disagreement on this layer carries each "
            "speaker's own sentence, which is a reading and not a computation (L15)."],
        "both_publish_a_year": sum(1 for _l, g in gaps if g is not None),
        "agree_within_a_year": sum(1 for _l, g in gaps if g is not None and g <= 1),
        "disagree_by_more_than_a_year": sum(1 for _l, g in gaps if g is not None and g > 1),
        "rows": sorted(
            f"{l['key']} ({l['sector']}): owner {l['target_year_owner']} vs list "
            f"{l['target_year_list']}, {int(l['target_year_owner']) - int(l['target_year_list']):+d} years"
            for l, g in gaps if g is not None and g > 1)}

    # 3 — BY OWNER TYPE, and the coverage is the first number in it. `owner_listing` is
    # read off the `owners` list (scope.md) and is populated on 22 of 205 projects, so
    # this table describes 22 lines and says so rather than reading as a table about the
    # register. The field is NOT filled in this pass: who owns an operator is a reading,
    # and L13 carries the brief for it with the source rule to be written first.
    owner_listing = {p["id"]: p.get("owner_listing") for p in sm.load("project")}
    by_owner = defaultdict(list)
    for l in _scored():
        v = owner_listing.get(l["row_id"]) if l["row_id"] else None
        by_owner[v or ("no row" if not l["row_id"] else "not read")].append(l)
    owner_tab = {
        "_comment": [
            "THE REGISTER'S OWN VOCABULARY, not the brief's words: `private` is the "
            "brief's `unlisted` and `state-owned` is its `state`. OWNER_LISTINGS in "
            "sector_map.py is what the gate enforces and what the data holds.",
            "COVERAGE IS THE POINT AND IT IS SMALL: `owner_listing` is set on 22 of 205 "
            "projects. `not read` is a line whose row carries no listing — a gap in "
            "this register's reading, not a fact about the owner — and `no row` is a "
            "census entry with no register row at all.",
            "THIS TABLE DOES NOT ENTER THE PAPER until the L13 listing pass fills the "
            "field from a source rule. Ruled 27 September 2026. It stays here because a "
            "table computed over 22 of 205 rows is worth having and worth labelling, and "
            "because the number it reports is the coverage."],
        "coverage": {"projects_with_owner_listing": sum(1 for v in owner_listing.values() if v),
                     "projects": len(owner_listing),
                     "scored_lines_covered": sum(len(v) for k, v in by_owner.items()
                                                 if k not in ("no row", "not read"))},
        "by_owner_type": {k: _six(v) for k, v in sorted(by_owner.items())}}

    out["cross_tabs"].update({
        "checks_by_list_stage": stage_tabs,
        "checks_by_target_year": year_tabs,
        "checks_by_owner_type": owner_tab,
        # 4 — WHO CONFIRMED, FROM THE TYPED COLUMN. The old table counted `medium`, which
        # is derived from the speaker and the note; this counts `speaker_type`, derived
        # from the speaker and the SOURCE. The disagreement between them is reported
        # rather than resolved while L12 is open: medium_of() reads no hosts, so a
        # trade-press URL under an `owner` speaker reads as an owner document.
        "who_confirms_by_speaker_type": {
            "_comment": [
                "PASSING CELLS ONLY, over scored lines, per rung.",
                "`register` means the passing cell cites this register's own census, "
                "search or dependency graph — which for rungs 4 and 6 is the funder "
                "pass and the edge file, both of them records of somebody else's "
                "publication read here.",
                "DISAGREEMENT WITH `medium` IS LISTED AND NOT RESOLVED: L12 has "
                "medium_of() classifying from the speaker and the note rather than the "
                "host."],
            "per_rung": {r: dict(Counter(l[f"{r}_speaker_type"] for l in _scored()
                                         if l[f"{r}_result"] == "pass"))
                         for r in RUNGS},
            # AND THE BLIND SPOT BOTH DERIVATIONS SHARE, COUNTED. Neither reads the
            # document's host: medium_of() matches the speaker and the note, and
            # speaker_type_of() matches the speaker and the source's PREFIX. So a
            # passing cell whose source sits on a trade title while its speaker was set
            # to `owner` reads as an owner document in both columns. That is L12's
            # defect measured rather than described — 13 cells, not the 2 the first
            # report named — and it is what the medium fix has to move.
            "source_host_is_a_trade_title": sorted(
                f"{l['key']} {r}: {urllib.parse.urlsplit(l[f'{r}_source']).netloc} "
                f"(speaker_type={l[f'{r}_speaker_type']}, medium={l[f'{r}_medium']})"
                for l in _scored() for r in RUNGS
                if l[f"{r}_result"] == "pass"
                and TRADE_HOST.search(urllib.parse.urlsplit(l[f"{r}_source"]).netloc or "")),
            "disagrees_with_medium": sorted(
                {f"{l['key']} {r}: speaker_type={l[f'{r}_speaker_type']}, "
                 f"medium={l[f'{r}_medium']}"
                 for l in _scored() for r in RUNGS
                 if l[f"{r}_result"] == "pass"
                 and {l[f"{r}_speaker_type"], l[f"{r}_medium"]} in (
                     {"owner", "press"}, {"owner", "press_quoting_owner"},
                     {"press", "funder"}, {"owner", "permit"})})},
    })

    out["layers"] = {
        "_comment": [
            "THE CROSS-SECTOR TABLE IS COMPUTED FOR THE PRODUCING LAYER, and the",
            "infrastructure rows are summarised beneath it rather than averaged into",
            "it. A pipeline has no nameplate its owner publishes and a reservoir is",
            "not a plant; transport and storage answers rung 2 six times in 102 and",
            "rung 5 never, and mixing that into a rate about plants describes",
            "neither. NO DATA CHANGED: the same 644 lines, grouped."],
        "producing": roll("producing"),
        "infrastructure": roll("infrastructure")}

    out["cross_sector"] = {
        "_shape": "rungs are rows, sectors are columns; the cell is passes out of scored",
        "_layer": "the columns below are the PRODUCING layer; the infrastructure "
                  "layer is in `layers.infrastructure`",
        "rungs": {r: {s: {"pass": out["sectors"][s]["per_rung"][r]["pass"],
                          "of_scored": out["sectors"][s]["scored"]}
                      for s in PRODUCING} for r in RUNGS},
        "population": {s: out["sectors"][s]["population"] for s in PRODUCING},
        "scored": {s: out["sectors"][s]["scored"] for s in PRODUCING},
        "total_population": sum(out["sectors"][s]["population"] for s in PRODUCING),
        "total_scored": sum(out["sectors"][s]["scored"] for s in PRODUCING),
        "all_layers_population": sum(out["sectors"][s]["population"] for s in SECTORS),
        "all_layers_scored": sum(out["sectors"][s]["scored"] for s in SECTORS)}
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
    PROD = summary["layers"]["producing"]["sectors"]
    INFRA = summary["layers"]["infrastructure"]["sectors"]

    print("\nTHE CROSS-SECTOR TABLE — THE PRODUCING LAYER")
    print("  rungs down, sectors across, passes out of scored\n")
    head = f"  {'rung':<10}" + "".join(f"{s[:13]:>15}" for s in PROD)
    print(head)
    print("  " + "-" * (len(head) - 2))
    for i, r in enumerate(RUNGS, 1):
        row = f"  {i}. {r:<7}"
        for s in PROD:
            c = summary["cross_sector"]["rungs"][r][s]
            row += f"{str(c['pass']) + '/' + str(c['of_scored']):>15}"
        pl = summary["layers"]["producing"]["per_rung"][r]
        row += f"   |{str(pl['pass']) + '/' + str(pl['of_scored']):>12}"
        print(row)
    print("  " + "-" * (len(head) - 2))
    for label, key in (("population", "population"), ("scored", "scored"),
                       ("excluded", "perimeter_exclusions"), ("unread", "unread")):
        print(f"  {label:<10}" + "".join(
            f"{summary['sectors'][s][key]:>15}" for s in PROD))
    print(f"\n  the last column is the producing layer as one: "
          f"{summary['layers']['producing']['population']} entries, "
          f"{summary['layers']['producing']['scored']} scored.")

    print("\nBENEATH IT — THE INFRASTRUCTURE LAYER, summarised and not averaged in")
    inf = summary["layers"]["infrastructure"]
    print(f"  {', '.join(INFRA)}: {inf['population']} entries, {inf['scored']} scored")
    print("  " + "  ".join(f"{i}.{r} {inf['per_rung'][r]['pass']}/{inf['per_rung'][r]['of_scored']}"
                           for i, r in enumerate(RUNGS, 1)))
    print("  A pipeline has no nameplate its owner publishes and a reservoir is not a")
    print("  plant. Rung 2 clears 6 times in 102 and rung 5 never; averaging that into a")
    print("  rate about plants would describe neither. NO DATA CHANGED — the same lines.")
    print(f"\n  {summary['cross_sector']['all_layers_population']} entries across five "
          f"populations in total; "
          f"{summary['cross_sector']['all_layers_scored']} scored.")

    print("\nTHE PRESS-QUOTED AMENDMENT — BOTH TABLES, all five sectors")
    print("  a pass resting on a title speaking IN ITS OWN VOICE stops being a pass;")
    print("  a pass resting on a title QUOTING THE OWNER stands, because the speaker is")
    print("  the owner. Frozen | amended, passes out of scored.\n")
    hd = f"  {'rung':<10}" + "".join(f"{s[:13]:>17}" for s in SECTORS)
    print(hd)
    print("  " + "-" * (len(hd) - 2))
    for i, r in enumerate(RUNGS, 1):
        row = f"  {i}. {r:<7}"
        for s in SECTORS:
            d = summary["sectors"][s]
            a = d["per_rung"][r]["pass"]
            b = d["per_rung_amended"][r]["pass"]
            mark = " " if a == b else "*"
            row += f"{f'{a}|{b}{mark}':>17}"
        print(row)
    print("  " + "-" * (len(hd) - 2))
    print("  * the amendment moved this cell\n")
    print("  the medium every PASSING cell rests on, all sectors:")
    tot = Counter()
    for s in SECTORS:
        for r in RUNGS:
            tot.update(summary["sectors"][s]["medium_of_passing_cells"][r])
    for k, v in tot.most_common():
        print(f"    {k:<22} {v}")
    oc = Counter()
    for s in SECTORS:
        oc.update(summary["sectors"][s]["outcome_class_amended"])
    print("\n  outcome classes the amendment creates:")
    for k, v in (oc.most_common() or [("(none — no entry lost its last pass)", 0)]):
        print(f"    {k:<42} {v}")

    print("\nEACH SECTOR'S POPULATION IDENTITY")
    for s in SECTORS:
        print(f"  {s:<24} [{summary['sectors'][s]['layer'][:5]}] "
              f"{summary['sectors'][s]['identity']}")

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
        # THE TERMINATED AWARDS ARE NO LONGER A QUEUE ITEM, THEY ARE A RESULT (D-A28).
        # What stays worth printing is the pair a terminated award leaves behind: the
        # entry is still admitted or held on the funder's award while the same funder
        # says the money is gone, and for the two steel entries there is no row to
        # carry the stop fact on.
        if l["funding_result"] == "fail" and "TERMINATED" in l["funding_note"]:
            out.append((l["sector"], l["key"], l["name"],
                        "rung 4 fails on a terminated award"
                        + ("; there is no register row to carry the stop fact"
                           if not l["row_id"] else "")))
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

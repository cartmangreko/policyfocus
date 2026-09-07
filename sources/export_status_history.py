#!/usr/bin/env python3
"""Flatten the project status histories into one event per row, for the
attrition paper.

WHY A FLAT EXPORT AND NOT A QUERY. data/transition/projects.json is shaped for
the site: a project is a row and its history is a list inside it, which is the
right shape for drawing a status strip and the wrong shape for counting how long
things take. Attrition is a question about EVENTS — how many projects entered
construction, how many left it, how long they stayed — and every one of those is
a group-by over a table this file does not contain. So the table is built here,
once, rather than reconstructed differently by each thing that asks.

IT READS ONLY FROM data/ AND WRITES ONLY TO scratch/. Nothing on the site reads
its output and no gate runs it; it is an analysis artefact, and scratch/ is
ignored by git for exactly that reason.

WHAT IS NOT IN IT. Refused candidates and anything still in the manual queue are
not exported: a project the perimeter has not admitted has no status history to
flatten, and counting it would put the queue's shape into the attrition rate.
"""

import csv
import json
import os
import statistics
import sys
from collections import Counter, defaultdict
from calendar import monthrange
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = sm.ROOT
OUT = ROOT / "scratch"

# THE PAPER'S REPORTING GROUPS, AND THEY ARE THIS FILE'S ALONE.
#
# sector_map.PROJECT_ALIVE / PROJECT_STOPPED / PROJECT_COMPLETE are the schema's
# counting groups and sector_map.STOPPED_STATUSES is the site's drawing rule.
# Neither is touched here. An attrition paper needs its own cut: it is ABOUT the
# projects that stalled, so `paused` cannot be folded into either the ones that
# are proceeding or the ones that are over — the whole question is how many sit
# in between, and for how long.
#
#   active     work is proceeding and the plant is not yet built: the four rungs
#              below `operating`.
#   paused     its own group, because it is the finding.
#   stopped    it will not be built. `withdrawn` is named here for the same
#              reason the schema names it nowhere: it is a funding status, and
#              if a project status of that name ever lands it belongs here.
#   operating  it was built. Its own group, and NOT part of active.
#
# WHY `operating` LEFT `active`. It sat in `active` on the reading that a plant
# that was built did not stall, which is true and is not the whole of it: an
# attrition series divides by the projects that COULD still stall, and a built
# plant cannot. Leaving it in `active` mixes the denominator — a sector that has
# finished several plants reads as more active than one with the same number of
# projects still climbing, when the opposite is what the count is for. Splitting
# it out costs nothing, because `active + operating` recovers the old group
# exactly whenever the earlier reading is the one somebody wants.
#
# So this is four groups where the schema has three and the site has two, and
# all three readings stand — they answer different questions.
REPORTING_GROUPS = {
    "active": ("announced", "funded", "fid", "construction"),
    "paused": ("paused",),
    "stopped": ("cancelled", "withdrawn"),
    "operating": ("operating",),
}


COLUMNS = [
    "project_id", "sector", "company", "country", "technology", "transition",
    "capacity_value", "capacity_unit", "capacity_basis",
    "schedule_speaker", "first_stated_production_start",
    "latest_stated_production_start", "schedule_revisions", "months_slipped",
    "months_past_stated", "speakers_disagree", "disagreement_months",
    "event_date", "status_from", "status_to", "event_kind", "source_type",
    "source_url", "evidence_mode", "months_in_previous_state", "current_status",
    "months_in_current_state",
]

# WHY A ROW-LEVEL VALUE SITS ON AN EVENT ROW. `months_in_current_state` is a
# property of the PROJECT, not of the event, and it repeats down every event of
# the same project exactly as `current_status` already does. It is here because
# the question it answers — how long has this been sitting where it is — is
# asked of the same table as everything else, and making the reader join a
# second file to ask it is how the two get out of step. It is measured from the
# LAST event to the export date, so it is the open run and is censored: the
# project has not finished being in this state, and the true figure can only be
# larger. That is what makes a delay WITHOUT a status change visible at all —
# nothing else in this table moves when a project quietly stops moving.


def full(d: str) -> date:
    """A history date may be YYYY, YYYY-MM or YYYY-MM-DD — the schema allows all
    three and one row uses the first. A partial date is padded to the first of
    the period, which is the earliest day it can mean; every duration computed
    from it is therefore the longest reading, and that is said in the summary
    rather than hidden."""
    parts = [int(x) for x in str(d).split("-")]
    while len(parts) < 3:
        parts.append(1)
    return date(*parts[:3])


def months(a: date, b: date) -> float:
    """Whole months between two dates, to one decimal. Days are carried as a
    fraction of a 30.44-day month rather than dropped, because several of these
    intervals are shorter than a month and rounding them to zero would make a
    project look as though it never sat anywhere."""
    return round((b - a).days / 30.44, 1)


def num(v: float) -> str:
    """Plain digits with thousands separators. %g turns 7,750,000 into 7.75e+06,
    which is a capacity nobody can read at a glance and the wrong shape for a
    column somebody will paste into a paper."""
    return f"{v:,.0f}" if float(v) == int(v) else f"{v:,.2f}"


def no_cap(rows) -> int:
    """How many of these rows carry no capacity figure.

    PRINTED BESIDE EVERY CAPACITY-WEIGHTED TOTAL, per sources/scope.md,
    "Admission and capacity are separate questions". A row with no figure is
    admitted, is counted in every count-based table here, and cannot be weighted
    in a capacity-weighted one -- there is nothing to weight it by. A weighted
    total with a silent denominator reads as a statement about the sector when it
    is a statement about the part of the sector that published a number, so the
    excluded count travels with it. It is printed when it is zero too, so that a
    reader never has to work out whether it was checked."""
    return sum(1 for r in rows if r.get("capacity_value") in (None, ""))


def by_unit(rows) -> str:
    """A total per unit, never across them. t_per_year and t_co2_per_year are both
    tonnes and they are not the same tonne: one is product the works sells, the
    other is emissions it stops. Adding them would produce a number with no
    referent, which is the failure CAPACITY_UNITS exists to prevent, so the totals
    are printed side by side and never summed."""
    per: dict[str, float] = defaultdict(float)
    for r in rows:
        v = r.get("capacity_value")
        if v not in (None, ""):
            per[r.get("capacity_unit") or "?"] += float(v)
    return "; ".join(f"{num(v)} {u}" for u, v in sorted(per.items()))


# A TARGET IS READ AT THE END OF ITS PERIOD. "2029" is not missed until 31
# December 2029, and reading it as 1 January would call a project late for a year
# in which it is still on time. This is the opposite convention from a history
# date, which is padded to the first of its period because that is the earliest
# the event can have happened. Both are the reading that does not overstate.
def target_end(t: str) -> date:
    t = str(t)
    y = int(t[:4])
    if len(t) == 4:
        return date(y, 12, 31)
    tail = t[5:]
    if tail.startswith("H"):
        return date(y, 6, 30) if tail == "H1" else date(y, 12, 31)
    if tail.startswith("Q"):
        m = int(tail[1]) * 3
        return date(y, m, monthrange(y, m)[1])
    parts = [int(x) for x in t.split("-")]
    if len(parts) == 2:
        return date(y, parts[1], monthrange(y, parts[1])[1])
    return date(*parts)


def schedule(r: dict, today: date) -> dict:
    """The production_start story for one row, read under the speaker rule.

    A SLIP IS ONE SPEAKER CHANGING ITS MIND, AND ONLY THAT. Two speakers giving
    different dates for the same milestone have revised nothing; they disagree,
    which is a fact about the evidence and not about the project. Counting that as
    a slip manufactures delay out of a company and a government being asked on the
    same day, and it does so in the direction that flatters the register. So the
    slip series is computed WITHIN a speaker and the disagreement is reported in
    its own columns beside it.

    THE PRIMARY SPEAKER is the one with the most statements, and `company` wins a
    tie: the operator's own promise is the series a slip is really about, and a
    host government quoting it is not a second data point about the operator.

    months_past_stated IS BLANK FOR AN OPERATING PLANT, because "how long has this
    been late" has no meaning once the plant runs, and zero rather than negative
    for a target still ahead: a project that is not late is not early.
    """
    BLANK = {k: "" for k in ("schedule_speaker", "first_stated_production_start",
                             "latest_stated_production_start", "schedule_revisions",
                             "months_slipped", "months_past_stated",
                             "speakers_disagree", "disagreement_months")}
    ps = [h for h in (r.get("stated_schedule") or [])
          if h.get("milestone") == "production_start"]
    if not ps:
        return BLANK
    by_speaker: dict[str, list] = defaultdict(list)
    for h in ps:
        by_speaker[h.get("speaker") or "other"].append(h)
    for v in by_speaker.values():
        v.sort(key=lambda h: str(h["date"]))

    primary = max(by_speaker, key=lambda sp: (len(by_speaker[sp]), sp == "company"))
    series = by_speaker[primary]
    first, last = series[0], series[-1]

    out = dict(BLANK)
    out["schedule_speaker"] = primary
    out["first_stated_production_start"] = first["target_date"]
    out["latest_stated_production_start"] = last["target_date"]
    out["schedule_revisions"] = len(series) - 1
    out["months_slipped"] = months(target_end(first["target_date"]),
                                   target_end(last["target_date"]))
    if r.get("status") == "operating":
        out["months_past_stated"] = ""
    else:
        end = target_end(last["target_date"])
        out["months_past_stated"] = months(end, today) if today > end else 0.0

    # DISAGREEMENT: each speaker's latest word on the milestone, compared. Never
    # folded into the slip, and reported even when it is larger than the slip --
    # which on this dataset it always is.
    if len(by_speaker) > 1:
        latest = {sp: v[-1] for sp, v in by_speaker.items()}
        pairs = sorted(latest.items(), key=lambda kv: target_end(kv[1]["target_date"]))
        lo, hi = pairs[0], pairs[-1]
        out["speakers_disagree"] = f"{lo[0]} vs {hi[0]}"
        out["disagreement_months"] = months(target_end(lo[1]["target_date"]),
                                            target_end(hi[1]["target_date"]))
    return out


def load():
    with open(ROOT / "data" / "transition" / "projects.json", encoding="utf-8") as fh:
        return json.load(fh)["projects"]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    today = date.today()
    rows = load()

    events = []
    # Every closed run in a state, and the open one the project is sitting in
    # now, keyed by the state itself.
    dwell: dict[str, list[float]] = defaultdict(list)
    open_dwell: dict[str, list[float]] = defaultdict(list)

    for r in rows:
        history = r.get("status_history") or []
        sched = schedule(r, today)
        # Measured from the last event to the export date. A project with no
        # history has no event to measure from and is left empty rather than
        # given a zero, which would read as "changed today".
        in_current = (months(full(history[-1]["date"]), today) if history else "")
        prev_date = None
        for h in history:
            d = full(h["date"])
            events.append({
                "project_id": r["id"],
                "sector": r.get("sector", ""),
                "company": r.get("company", ""),
                "country": r.get("country", ""),
                "technology": " ".join(r.get("technology") or []),
                "transition": r.get("transition", ""),
                "capacity_value": r.get("capacity_value", ""),
                "capacity_unit": r.get("capacity_unit", ""),
                "capacity_basis": r.get("capacity_basis", ""),
                **sched,
                "event_date": h["date"],
                "status_from": h.get("status_from") or "",
                "status_to": h.get("status_to", ""),
                "event_kind": h.get("event_kind", ""),
                "source_type": h.get("source_type", ""),
                "source_url": h.get("source_url", ""),
                "evidence_mode": h.get("evidence_mode", ""),
                "months_in_previous_state": "" if prev_date is None else months(prev_date, d),
                "current_status": r.get("status", ""),
                "months_in_current_state": in_current,
            })
            if prev_date is not None and h.get("status_from"):
                dwell[h["status_from"]].append(months(prev_date, d))
            prev_date = d
        if history:
            open_dwell[history[-1].get("status_to") or r.get("status", "")].append(
                months(prev_date, today))

    csv_path = OUT / "status_history.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(events)

    # ---------------- summary ----------------
    def med(vals):
        return "-" if not vals else "%.1f" % statistics.median(vals)

    def table(headers, body):
        out = ["| " + " | ".join(headers) + " |",
               "|" + "|".join(["---"] * len(headers)) + "|"]
        for line in body:
            out.append("| " + " | ".join(str(c) for c in line) + " |")
        return "\n".join(out)

    sectors = sorted({r.get("sector", "") for r in rows})
    md = ["# Status history — summary",
          "",
          f"Exported {today.isoformat()} from data/transition/projects.json. "
          f"{len(rows)} projects, {len(events)} events.",
          ""]

    md += ["## Projects and capacity", ""]
    body = []
    for s in sectors:
        rs = [r for r in rows if r.get("sector") == s]
        filled = [r for r in rs if r.get("capacity_value") not in (None, "")]
        body.append([s, len(rs), len(filled), len(rs) - len(filled),
                     by_unit(filled) or "-"])
    md += [table(["sector", "projects", "capacity filled", "capacity empty",
                  "capacity total"], body)]

    md += ["", "## Events by kind", ""]
    kinds = list(sm.PROJECT_EVENT_KINDS)
    body = []
    for s in sectors:
        c = Counter(e["event_kind"] for e in events if e["sector"] == s)
        body.append([s, sum(c.values())] + [c.get(k, 0) for k in kinds])
    md += [table(["sector", "events"] + kinds, body)]

    md += ["", "## Events by evidence mode", ""]
    modes = list(sm.EVIDENCE_MODES)
    body = []
    for s in sectors:
        c = Counter(e["evidence_mode"] for e in events if e["sector"] == s)
        body.append([s, sum(c.values())] + [c.get(m, 0) for m in modes])
    md += [table(["sector", "events"] + modes, body)]

    md += ["", "## Events by source type", ""]
    types = list(sm.PROJECT_SOURCE_TYPES)
    body = []
    for s in sectors:
        c = Counter(e["source_type"] for e in events if e["sector"] == s)
        body.append([s, sum(c.values())] + [c.get(t, 0) for t in types])
    md += [table(["sector", "events"] + types, body)]

    md += ["", "## Transition matrix — counts, and capacity behind them", "",
           "Rows are status_from, columns status_to. `-` in the from column is a "
           "project's first entry, which comes from nowhere. Each cell is the "
           "number of events, and after the slash the capacity moving with them, "
           "totalled separately per unit and never across them — blank where none "
           "of those projects carries a figure. THE COUNT AND THE CAPACITY IN A "
           "CELL HAVE DIFFERENT DENOMINATORS: the count is every event, the "
           "capacity is only the events whose project carries a figure. The "
           "shortfall is in the table above and in `no capacity` below.", ""]
    froms = ["-"] + list(sm.PROJECT_STATUSES)
    tos = list(sm.PROJECT_STATUSES)
    cell_n: dict[tuple, int] = Counter()
    cell_rows: dict[tuple, list] = defaultdict(list)
    for e in events:
        key = (e["status_from"] or "-", e["status_to"])
        cell_n[key] += 1
        cell_rows[key].append(e)
    body = []
    for f in froms:
        if not any(cell_n.get((f, t)) for t in tos):
            continue
        line = [f]
        for t in tos:
            n = cell_n.get((f, t), 0)
            if not n:
                line.append("")
                continue
            cap = by_unit(cell_rows[(f, t)])
            line.append("%d / %s" % (n, cap) if cap else str(n))
        body.append(line)
    md += [table(["from \\ to"] + tos, body)]
    # THE TWO DENOMINATORS, NAMED, because this table is the one a paper lifts
    # straight into a figure and its two halves do not divide by the same thing.
    # A cell's count is over every row; its capacity is over the rows carrying a
    # figure. Printed per sector and for the file, so the caption travels with
    # the table instead of living in a methods section nobody copies with it.
    md += ["", "**The two denominators.** Counts in this table are over all rows; "
               "capacities are over the rows with a stated capacity. They are not "
               "the same denominator and a ratio must not be taken across them.", ""]
    body = []
    for s in sectors:
        rs = [r for r in rows if r.get("sector") == s]
        body.append([s, len(rs), len(rs) - no_cap(rs), no_cap(rs)])
    body.append(["all", len(rows), len(rows) - no_cap(rows), no_cap(rows)])
    md += [table(["sector", "rows", "rows with stated capacity",
                  "rows without"], body)]

    md += ["", "## Months in each state", "",
           "A closed run is a state a project has left; the open run is the state "
           "it is sitting in now, measured to the export date. They are kept "
           "apart because an open run is censored — the project has not finished "
           "being in that state — and a median over the two together understates "
           "every state a project is still stuck in.", ""]
    body = []
    for st in sm.PROJECT_STATUSES:
        body.append([st, len(dwell.get(st, [])), med(dwell.get(st, [])),
                     len(open_dwell.get(st, [])), med(open_dwell.get(st, []))])
    md += [table(["status", "closed runs", "median months (closed)",
                  "open runs", "median months (open, to export date)"], body)]

    md += ["", "## Months in current state, by sector", "",
           "How long each project has sat where it is, measured from its last "
           "event to the export date. This is the distribution behind the delays "
           "that no status change records: a project that stopped moving two "
           "years ago and was never paused appears nowhere else in this file. "
           "Every figure is censored — the runs are open, so each is a floor. "
           "Bands are months and are half-open, `24+` catching the tail.", ""]
    bands = [("0-6", 0, 6), ("6-12", 6, 12), ("12-24", 12, 24),
             ("24+", 24, float("inf"))]

    def dist(rs):
        vals = []
        for r in rs:
            h = r.get("status_history") or []
            if h:
                vals.append(months(full(h[-1]["date"]), today))
        line = [len(vals), med(vals),
                "%.1f" % max(vals) if vals else "-"]
        line += [sum(1 for v in vals if lo <= v < hi) for _, lo, hi in bands]
        return line

    body = []
    for s_ in sectors:
        body.append([s_] + dist([r for r in rows if r.get("sector") == s_]))
    body.append(["all"] + dist(rows))
    md += [table(["sector", "projects", "median months", "max months"]
                 + [b[0] for b in bands], body)]

    md += ["", "## Stated schedules, slip and disagreement, by sector", "",
           "What each project SAID it would do, from `stated_schedule` — a second "
           "history beside the status one. A slip is not a status change and never "
           "appears in the transition matrix: a plant whose start date moves from "
           "2026 to 2028 has not moved a rung, and this is the only table that "
           "sees it.", "",
           "**A slip is one speaker changing its mind.** Two speakers giving "
           "different dates for the same milestone have revised nothing — they "
           "disagree, and that is a fact about the evidence rather than about the "
           "project. Slip is therefore measured WITHIN a speaker and disagreement "
           "is counted separately; folding the second into the first would "
           "manufacture delay out of a company and a government being asked on the "
           "same day.", "",
           "`with a stated date` is the share of the sector's projects carrying at "
           "least one production_start statement — everything right of it is over "
           "THOSE rows and not over the sector. A target is read at the end of its "
           "period, so \"2029\" is not late until 31 December 2029.", ""]

    def sched_rows(rs):
        out = []
        for r in rs:
            h = [x for x in (r.get("stated_schedule") or [])
                 if x.get("milestone") == "production_start"]
            if h:
                out.append((r, schedule(r, today)))
        return out

    def sched_stats(rs):
        have = sched_rows(rs)
        if not have:
            return [f"0 of {len(rs)}", "-", "-", "-", "-"]
        slips = [x["months_slipped"] for _, x in have]
        revised = sum(1 for _, x in have if x["schedule_revisions"])
        dis = [x["disagreement_months"] for _, x in have if x["speakers_disagree"]]
        return [f"{len(have)} of {len(rs)} ({100 * len(have) // len(rs)}%)",
                med(slips), f"{revised} of {len(have)}",
                f"{len(dis)} of {len(have)}",
                f"{max(dis):.1f}" if dis else "-"]

    body = [[s] + sched_stats([r for r in rows if r.get("sector") == s])
            for s in sectors]
    body.append(["all"] + sched_stats(rows))
    md += [table(["sector", "with a stated date", "median months slipped",
                  "at least one revision", "speakers disagree",
                  "largest disagreement"], body)]

    have = sched_rows(rows)
    slipped = sorted([x for x in have if x[1]["months_slipped"]],
                     key=lambda x: -x[1]["months_slipped"])[:5]
    md += ["", "The five largest slips — one speaker moving its own date:", ""]
    if slipped:
        md += [table(["project", "sector", "speaker", "first stated",
                      "latest stated", "months slipped", "status now"],
                     [[r["id"], r.get("sector", ""), x["schedule_speaker"],
                       x["first_stated_production_start"],
                       x["latest_stated_production_start"],
                       "%.1f" % x["months_slipped"], r.get("status", "")]
                      for r, x in slipped])]
    else:
        md += ["**None. No speaker on this dataset has revised its own stated "
               "production start.** Every gap between two dates on this file is a "
               "gap between two different speakers, which the next table carries. "
               "That is a finding about the evidence and not a clean bill for the "
               "sector: a company that stops restating a date has not kept it, and "
               "nothing here can tell the two apart.", ""]

    dis = sorted([x for x in have if x[1]["speakers_disagree"]],
                 key=lambda x: -x[1]["disagreement_months"])
    md += ["", "Disagreements — two speakers, one milestone, never counted as slip:", ""]
    if dis:
        md += [table(["project", "sector", "speakers", "months apart", "status now"],
                     [[r["id"], r.get("sector", ""), x["speakers_disagree"],
                       "%.1f" % x["disagreement_months"], r.get("status", "")]
                      for r, x in dis])]
    else:
        md += ["None.", ""]

    md += ["", "## Status now, by reporting group", "",
           "`active`, `paused`, `stopped` and `operating` are this export's "
           "groups and are declared in this file. They are not sector_map's "
           "counting groups and not the site's STOPPED_STATUSES; all three "
           "readings stand and answer different questions. `paused` is its own "
           "group because it is what the paper is about, and `operating` is its "
           "own because a built plant can no longer stall and does not belong in "
           "the denominator — add `active` and `operating` to recover the "
           "earlier reading.", ""]
    names = list(REPORTING_GROUPS)
    body = []
    for s in sectors:
        c = Counter(r.get("status") for r in rows if r.get("sector") == s)
        line = [s] + [sum(c[x] for x in REPORTING_GROUPS[g]) for g in names]
        line.append(" ".join(f"{k}:{v}" for k, v in sorted(c.items())))
        body.append(line)
    c = Counter(r.get("status") for r in rows)
    body.append(["all"] + [sum(c[x] for x in REPORTING_GROUPS[g]) for g in names]
                + [" ".join(f"{k}:{v}" for k, v in sorted(c.items()))])
    md += [table(["sector"] + names + ["detail"], body)]

    md += ["", "## Capacity now, by reporting group", "",
           "The same four groups, weighted by capacity rather than counted. "
           "Totals are per unit and never across them. `no capacity` is the "
           "number of rows in that sector carrying no figure: they are admitted, "
           "they are counted in every table above, and they are absent from these "
           "totals because there is nothing to weight them by. Read every row of "
           "this table against it.", ""]
    body = []
    for s in sectors:
        rs = [r for r in rows if r.get("sector") == s]
        line = [s]
        for g in names:
            line.append(by_unit([r for r in rs
                                 if r.get("status") in REPORTING_GROUPS[g]]) or "-")
        line.append(f"{no_cap(rs)} of {len(rs)}")
        body.append(line)
    body.append(["all"] + [by_unit([r for r in rows
                                    if r.get("status") in REPORTING_GROUPS[g]]) or "-"
                           for g in names] + [f"{no_cap(rows)} of {len(rows)}"])
    md += [table(["sector"] + names + ["no capacity"], body)]

    unplaced = [st for st in sm.PROJECT_STATUSES
                if not any(st in v for v in REPORTING_GROUPS.values())]
    if unplaced:
        md += ["", f"**{len(unplaced)} project status(es) fall into no reporting "
                   f"group and are missing from the two tables above: "
                   f"{', '.join(unplaced)}.**"]

    md_path = OUT / "status_summary.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(csv_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

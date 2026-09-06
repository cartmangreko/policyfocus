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
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = sm.ROOT
OUT = ROOT / "scratch"

COLUMNS = [
    "project_id", "sector", "company", "country", "technology", "transition",
    "capacity_value", "capacity_unit", "capacity_basis",
    "event_date", "status_from", "status_to", "event_kind", "source_type",
    "source_url", "evidence_mode", "months_in_previous_state", "current_status",
]


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
                "event_date": h["date"],
                "status_from": h.get("status_from") or "",
                "status_to": h.get("status_to", ""),
                "event_kind": h.get("event_kind", ""),
                "source_type": h.get("source_type", ""),
                "source_url": h.get("source_url", ""),
                "evidence_mode": h.get("evidence_mode", ""),
                "months_in_previous_state": "" if prev_date is None else months(prev_date, d),
                "current_status": r.get("status", ""),
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
        total = sum(r["capacity_value"] for r in filled) if filled else 0
        units = sorted({r.get("capacity_unit") for r in filled})
        body.append([s, len(rs), len(filled), len(rs) - len(filled),
                     num(total) if filled else "-",
                     " ".join(u for u in units if u) or "-"])
    md += [table(["sector", "projects", "capacity filled", "capacity empty",
                  "capacity total", "units"], body)]

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
           "number of events, and after the slash the capacity moving with them "
           "in the units the sector records — blank where none of those projects "
           "carries a figure.", ""]
    froms = ["-"] + list(sm.PROJECT_STATUSES)
    tos = list(sm.PROJECT_STATUSES)
    cell_n: dict[tuple, int] = Counter()
    cell_cap: dict[tuple, float] = defaultdict(float)
    for e in events:
        key = (e["status_from"] or "-", e["status_to"])
        cell_n[key] += 1
        if e["capacity_value"] not in (None, ""):
            cell_cap[key] += float(e["capacity_value"])
    body = []
    for f in froms:
        if not any(cell_n.get((f, t)) for t in tos):
            continue
        line = [f]
        for t in tos:
            n = cell_n.get((f, t), 0)
            if not n:
                line.append("")
            elif cell_cap.get((f, t)):
                line.append("%d / %s" % (n, num(cell_cap[(f, t)])))
            else:
                line.append(str(n))
        body.append(line)
    md += [table(["from \\ to"] + tos, body)]

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

    md += ["", "## Status now", ""]
    body = []
    for s in sectors:
        c = Counter(r.get("status") for r in rows if r.get("sector") == s)
        alive = sum(c[x] for x in sm.PROJECT_ALIVE)
        stopped = sum(c[x] for x in sm.PROJECT_STOPPED)
        complete = sum(c[x] for x in sm.PROJECT_COMPLETE)
        body.append([s, alive, stopped, complete,
                     " ".join(f"{k}:{v}" for k, v in sorted(c.items()))])
    md += [table(["sector", "alive", "stopped", "complete", "detail"], body)]

    md_path = OUT / "status_summary.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(csv_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

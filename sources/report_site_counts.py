#!/usr/bin/env python3
"""What each sector has on file, what the site draws of it, and what it withholds.

    python3 report_site_counts.py           # prints; never fails a build
    python3 report_site_counts.py --json    # the same numbers, for a report

WHY THIS EXISTS. Brief 17 §A.1 asks for one table, per sector, of the rows on
file, the rows drawn, the rows admitted and undrawn, the stopped rows with
paused and cancelled named separately, and the split between rows with a stated
capacity and rows without. Those six numbers were available and were never in
one place: three of them come from the project store, one from the built frame,
one from capacity_clause.py and one from the hold file, and anybody who wanted
the table built it by hand out of four other scripts' output.

A NUMBER IN A REPORT IS QUOTED FROM A GATED FILE (sources/scope.md, 21 September
2026). Every figure here is read from one of four tracked files and the file is
named in the output, so a line of this table can be checked without trusting
this script:

    data/transition/projects.json         rows, status, capacity_value, location
    data/transition/maps/sector-*.json    marks, and the undrawn remainder
    data/transition/draw_holds.json       whether the page may be published
    data/prose.json                       nothing counted; the names only

AND IT IS A REPORT, NOT A GATE. Nothing here is a rule: the shortfall between
admitted and drawn is the state of the research, not a fault, and a build that
failed on it would take the site down for the ordinary condition of a census in
progress. The two gates that DO bind on these numbers are
sources/check_map_clusters.py (the frame's arithmetic) and
sources/check_capacity_clause.py (the denominator on a weighted figure).

WHY IT IS IN THE PREBUILD CHAIN. Same reason report_candidate_gaps.py and
report_status_age.py are: a number nobody is shown on every build is a number
that goes wrong quietly. The delta between a build and the one before it is the
thing this table is actually for, and it is only visible if the table is printed
every time.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capacity_clause as cc  # noqa: E402
import sector_map as sm  # noqa: E402

MAPS = sm.DATA / "maps"
HOLDS = sm.DATA / "draw_holds.json"

# The two statuses that stop a project, named separately in the output because
# they are two different facts and the brief asks for both: a paused project may
# resume and is what an attrition series measures; a cancelled one is off every
# frame but its own. See sources/sector_map.py, STOPPED_STATUSES, where the
# three readings of `paused` are written down.
PAUSED = "paused"
CANCELLED = "cancelled"


def _holds() -> dict:
    return json.loads(HOLDS.read_text(encoding="utf-8")) if HOLDS.exists() else {}


def _frame(sector: str) -> dict | None:
    path = MAPS / f"sector-{sector.replace('/', '__')}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def counts(projects: list[dict] | None = None) -> list[dict]:
    """One row per sector that has a project on file, in a fixed order.

    `drawn` IS READ OFF THE BUILT FRAME and not recomputed here. The frame is
    the thing a reader looks at, sources/build_maps.py decided what went on it,
    and a second count in a reporting script is a second answer that would be
    believed when it disagreed. Where no frame exists the field says so rather
    than reporting a zero, because no frame and an empty frame are different
    states.
    """
    rows = sm.load("project") if projects is None else projects
    holds = _holds()
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r.get("sector", ""), []).append(r)

    out = []
    for sector in sorted(by):
        rs = by[sector]
        frame = _frame(sector)
        stated, total = cc.denominators(sector, rows) if sector in cc.SECTORS else (
            sum(1 for r in rs if r.get("capacity_value") not in (None, "")), len(rs))
        out.append({
            "sector": sector,
            "rows": len(rs),
            # Drawn: marks on the overview, which is sites and not rows — one
            # project may stand on two. Both are given, because the standfirst
            # counts sites and the register counts rows.
            "drawn_sites": len(frame["marks"]) if frame else None,
            "drawn_rows": len({m["id"] for m in frame["marks"]}) if frame else None,
            "undrawn_rows": frame["undrawn"]["projects"] if frame else None,
            "clusters": len(frame["clusters"]["groups"])
                        if frame and "clusters" in frame else None,
            "country_views": len(frame["country_totals"])
                             if frame and "country_totals" in frame else None,
            "paused": sum(1 for r in rs if r.get("status") == PAUSED),
            "cancelled": sum(1 for r in rs if r.get("status") == CANCELLED),
            "capacity_stated": stated,
            "capacity_absent": total - stated,
            "hub_held": sector in (holds.get("holds") or {}),
            "project_pages_held": sector in (holds.get("project_page_holds") or {}),
        })
    return out


HEAD = ("sector", "rows", "drawn", "undrawn", "paused", "canc", "cap", "no cap",
        "clusters", "countries", "published")


def _cells(row: dict) -> tuple[str, ...]:
    drawn = ("—" if row["drawn_sites"] is None
             else f"{row['drawn_rows']} / {row['drawn_sites']} sites")
    published = ("hub held" if row["hub_held"] else
                 "pages held" if row["project_pages_held"] else "yes")
    return (
        row["sector"],
        str(row["rows"]),
        drawn,
        "—" if row["undrawn_rows"] is None else str(row["undrawn_rows"]),
        str(row["paused"]),
        str(row["cancelled"]),
        str(row["capacity_stated"]),
        str(row["capacity_absent"]),
        "—" if row["clusters"] is None else str(row["clusters"]),
        "—" if row["country_views"] is None else str(row["country_views"]),
        published,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true",
                    help="the same figures, as one JSON object")
    args = ap.parse_args()

    rows = counts()
    if args.json:
        print(json.dumps({"as_of_build": None, "sectors": rows}, indent=2))
        return 0

    table = [HEAD] + [_cells(r) for r in rows]
    widths = [max(len(r[i]) for r in table) for i in range(len(HEAD))]
    print("report_site_counts: every figure read from a tracked file — "
          "data/transition/projects.json (rows, status, capacity, position), "
          "data/transition/maps/sector-*.json (drawn, undrawn, clusters, "
          "countries), data/transition/draw_holds.json (published)")
    for i, r in enumerate(table):
        print("  " + "  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip())
        if i == 0:
            print("  " + "  ".join("-" * w for w in widths))
    totals = {
        "rows": sum(r["rows"] for r in rows),
        "drawn": sum(r["drawn_sites"] or 0 for r in rows),
        "clusters": sum(r["clusters"] or 0 for r in rows),
        "countries": sum(r["country_views"] or 0 for r in rows),
    }
    print(f"  {totals['rows']} row(s) in {len(rows)} sector(s); "
          f"{totals['drawn']} site(s) drawn across {totals['countries']} country "
          f"view(s), {totals['clusters']} of them grouped into a numbered marker")
    # WHAT IS WITHHELD, SAID OUT LOUD, for the same reason
    # report_candidate_gaps.py prints the draw holds: a hold nobody is reminded
    # of either stays on after its reason has gone or comes off without anybody
    # deciding it should.
    held = [r["sector"] for r in rows if r["hub_held"] or r["project_pages_held"]]
    if held:
        print(f"  withheld from the index: {', '.join(held)} — see "
              f"data/transition/draw_holds.json for the decision and who releases it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

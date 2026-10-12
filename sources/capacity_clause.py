#!/usr/bin/env python3
"""The denominator clause that must travel with a capacity-weighted figure.

WHY THIS EXISTS. sources/scope.md, "Admission and capacity are separate
questions", settles that a row with no stated capacity stays admitted, is
counted in count-based statistics and is absent from capacity-weighted ones.
That rule is safe in the export, where the shortfall is printed beside every
weighted table. It is not safe on a page: a sentence that says European cement
is building 3.1 Mt of capture reads as a statement about European cement, when
it is a statement about the four cement plants of eight that have published a
figure. The other four are not zero. They are unknown, and the sentence silently
scores them as zero.

SO EVERY CAPACITY-WEIGHTED FIGURE ON A SURFACE CARRIES ITS DENOMINATOR, in the
sentence, not in a footnote — "across the 4 of 8 plants with a stated capacity".
A reader who sees the figure sees what it is over.

THIS MODULE IS THE ONE PLACE THAT KNOWS THE NUMBERS. clause() builds the text a
surface renders; check_capacity_clause.py uses the same figures to fail a build
that prints a weighted figure without one. A gate and a renderer that computed
this separately would drift, and the drift would be invisible -- the clause would
go on saying 4 of 8 after the fifth plant published.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

# The sectors a capacity figure is sought for, and therefore the sectors a
# weighted figure can be built for. Read from sector_map so the two cannot drift.
SECTORS = sm.CAPACITY_SECTORS

# What a surface must say. `plants` because that is the word the pages use for a
# works; `projects` is accepted because the sector pages count projects and a
# sentence about projects should be allowed to say so.
CLAUSE_RE = r"across the (\d+) of (\d+) (?:plants|projects) with a stated capacity"


def rows_by_sector(rows=None) -> dict[str, list[dict]]:
    rows = sm.load("project") if rows is None else rows
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r.get("sector", ""), []).append(r)
    return out


def stated(rows) -> list[dict]:
    """The rows a weighted figure may be built from."""
    return [r for r in rows if r.get("capacity_value") not in (None, "")]


def denominators(sector: str, rows=None) -> tuple[int, int]:
    """(rows with a stated capacity, rows on file) for one sector."""
    rs = rows_by_sector(rows).get(sector, [])
    return len(stated(rs)), len(rs)


def clause(sector: str, rows=None, noun: str = "plants") -> str:
    """The clause a surface appends to a capacity-weighted figure.

    Rendered even when every row has a figure. "across the 8 of 8 plants with a
    stated capacity" is not noise: it is the difference between a reader knowing
    the total is complete and a reader assuming it.
    """
    have, total = denominators(sector, rows)
    return f"across the {have} of {total} {noun} with a stated capacity"


def weighted_totals(sector: str, rows=None) -> dict[str, float]:
    """Every capacity total this dataset can produce for a sector, per unit.

    These are the figures a surface would print, and therefore the figures the
    gate looks for. Totals are per unit and never across them -- a tonne of
    captured CO2 and a tonne of crude steel are different tonnes.
    """
    per: dict[str, float] = {}
    for r in stated(rows_by_sector(rows).get(sector, [])):
        u = r.get("capacity_unit") or "?"
        per[u] = per.get(u, 0.0) + float(r["capacity_value"])
    return per


def drawn(rows) -> list[dict]:
    """The rows whose capacity a PICTURE's figure is summed over.

    THE POPULATION THE RULE WAS WRITTEN ABOUT. The example in this module's
    docstring -- "European cement is building 3.1 Mt of capture ... the four
    cement plants of eight that have published a figure" -- is exactly this set:
    cement has eight placed rows, four of them state a capacity, and 3.1 Mt is
    their sum. Until 12 October 2026 the gate could not see such a figure,
    because the pots it computed were the whole sector and the status groups and
    this is neither.

    THE TWO CONDITIONS ARE sources/build_maps.py's, and they are the same two
    web/lib/transition.ts isDrawable applies: a row with no position has nothing
    to draw, and a cancelled row is off every frame but its own.
    """
    return [r for r in rows
            if (r.get("location") or []) and r.get("status") not in sm.UNDRAWN_STATUSES]


def undrawn(rows) -> list[dict]:
    """The complement: on file, and not on the picture. Its capacity is a real
    quantity about a real set and is stated separately, never added to the one
    above -- a megawatt that exists and a megawatt somebody has announced are
    not the same megawatt."""
    kept = {id(r) for r in drawn(rows)}
    return [r for r in rows if id(r) not in kept]


# THE POPULATIONS A SURFACE MAY SUM OVER, named once. A caller asking for a pot
# this does not name is asking for a figure no gate can recognise.
POPULATIONS = {
    "drawn": drawn,
    "undrawn": undrawn,
}


def population_totals(sector: str, rows=None) -> dict[str, dict[str, float]]:
    """{population: {unit: total}} for the two halves the picture divides a
    sector into. The figures web/lib/prose.ts puts in the two standfirst
    clauses, computed here so the gate looks for the numbers the page prints."""
    rs = rows_by_sector(rows).get(sector, [])
    return {name: _per_unit(stated(fn(rs))) for name, fn in POPULATIONS.items()}


def population_denominators(sector: str, rows=None) -> dict[str, tuple[int, int]]:
    rs = rows_by_sector(rows).get(sector, [])
    return {name: (len(stated(fn(rs))), len(fn(rs))) for name, fn in POPULATIONS.items()}


def _per_unit(rows) -> dict[str, float]:
    per: dict[str, float] = {}
    for r in rows:
        u = r.get("capacity_unit") or "?"
        per[u] = per.get(u, 0.0) + float(r["capacity_value"])
    return per


def group_totals(sector: str, groups: dict[str, tuple], rows=None) -> dict[str, dict[str, float]]:
    """The same, split by a caller's status groups -- a page may weight one
    group (what is operating, what was cancelled) rather than the whole sector,
    and such a figure needs the clause exactly as much."""
    rs = rows_by_sector(rows).get(sector, [])
    out: dict[str, dict[str, float]] = {}
    for g, statuses in groups.items():
        per: dict[str, float] = {}
        for r in stated([x for x in rs if x.get("status") in statuses]):
            u = r.get("capacity_unit") or "?"
            per[u] = per.get(u, 0.0) + float(r["capacity_value"])
        out[g] = per
    return out


if __name__ == "__main__":
    for s in SECTORS:
        print(f"{s:8} {clause(s)}   totals: "
              + ("; ".join(f"{v:,.2f} {u}" for u, v in weighted_totals(s).items()) or "-"))
        for name, (have, total) in population_denominators(s).items():
            per = population_totals(s)[name]
            print(f"         {name}: across the {have} of {total} projects with a stated "
                  f"capacity — "
                  + ("; ".join(f"{v:,.2f} {u}" for u, v in sorted(per.items())) or "-"))

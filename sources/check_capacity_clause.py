#!/usr/bin/env python3
"""Fail the build on a capacity-weighted figure rendered without its denominator.

    python3 check_capacity_clause.py      # non-zero on any unclaused figure

WHAT IT ENFORCES. sources/scope.md, "Admission and capacity are separate
questions": a row with no stated capacity is admitted and counted, and is absent
from capacity-weighted totals because there is nothing to weight it by. On a page
that absence is invisible unless the sentence says so, and a weighted total with
a silent denominator reads as a statement about the sector when it is a statement
about the part of it that published a number -- scoring the rest as zero. Cement
is the sharp case: four of its eight plants have a figure, and the other four are
not zero tonnes of capture. They are unknown.

WHY IT READS THE BUILT PAGES AND NOT THE DATA. The rule is about what a reader
sees. A gate on the data would have to guess which figures reach a surface and
would miss the first one that arrived by a route nobody told it about; the
rendered HTML is the thing the rule is actually about. Same reason
check_anchor_text.py and check_sitemap.py run in postbuild.

HOW A FIGURE IS RECOGNISED AS WEIGHTED, and why this is narrow on purpose. The
gate computes every capacity total this dataset can produce -- per sector, per
unit, whole-sector and by status group -- and looks for those values on the
pages. A number is flagged only when it MATCHES one of those totals and is not
also some single project's own capacity. That is deliberately conservative: a
page may print "50 GWh" for one plant, or "50 Mt CO2 per year" as the Net-Zero
Industry Act's injection objective, and neither is a weighted figure. What it
will not miss is the case the rule exists for -- a page that adds this dataset up
and prints the answer.

WHAT IT FINDS TODAY: NOTHING, AND THAT IS THE HONEST STATE. No surface currently
renders a capacity sum. Project pages print one row's own figure; the sector
pages print per-plant enumerations and legal parameters. The gate is written now
so the rule binds the moment a surface starts summing, rather than after -- and
it carries its own fixtures, below, because a gate that never fires on real data
would otherwise go green through any refactor that broke it.
"""

from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capacity_clause as cc  # noqa: E402
import sector_map as sm  # noqa: E402

PAGES = sm.ROOT / "web" / ".next" / "server" / "app"

# How the units reach a page. The capacity_* fields are machine names; a surface
# renders words. Both spellings are matched, with the multiplier that turns the
# rendered number back into the field's own unit.
UNIT_WORDS = {
    "GWh_per_year": [(r"GWh(?:\s*(?:per|/)\s*year|/yr)?", 1.0)],
    "t_per_year": [(r"Mt\b[^.]{0,40}?(?:per|/)\s*year", 1e6),
                   (r"(?:t|tonnes)\b[^.]{0,40}?(?:per|/)\s*year", 1.0)],
    "t_co2_per_year": [(r"Mt\b[^.]{0,40}?(?:per|/)\s*year", 1e6),
                       (r"(?:t|tonnes)\b[^.]{0,40}?(?:per|/)\s*year", 1.0)],
}

NUM = r"(\d[\d,   ]*(?:\.\d+)?)"
CLAUSE = re.compile(cc.CLAUSE_RE, re.I)
# How near the clause has to be. The rule is that the clause is IN the sentence;
# this is the slack that lets it sit after a comma or the following full stop.
WINDOW = 400
TOLERANCE = 0.005   # a rendered figure may be rounded; 0.5% is not a coincidence

GROUPS = {"operating": ("operating",),
          "stopped": ("cancelled",),
          "paused": ("paused",),
          "under way": ("announced", "funded", "fid", "construction",
                        "commissioning")}


def text_of(p: Path) -> str:
    raw = p.read_text(encoding="utf-8", errors="ignore")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def targets(rows) -> dict[str, dict[float, str]]:
    """Every weighted value that would need a clause, as {unit: {value: label}}."""
    out: dict[str, dict[float, str]] = {}
    for sector in cc.SECTORS:
        pots = {"whole sector": cc.weighted_totals(sector, rows)}
        pots.update(cc.group_totals(sector, GROUPS, rows))
        for label, per in pots.items():
            for unit, val in per.items():
                if val > 0:
                    out.setdefault(unit, {})[val] = f"{sector} / {label}"
    return out


def singles(rows) -> set[float]:
    return {float(r["capacity_value"]) for r in rows
            if r.get("capacity_value") not in (None, "")}


def scan(t: str, where: str, tgt, single) -> tuple[list[str], int]:
    """Every weighted figure in one page's text, and which of them lack a clause."""
    problems, found = [], 0
    for unit, values in tgt.items():
        for pattern, mult in UNIT_WORDS.get(unit, []):
            for m in re.finditer(NUM + r"\s*" + pattern, t, re.I):
                raw = float(re.sub(r"[,   ]", "", m.group(1))) * mult
                for val, label in values.items():
                    if abs(raw - val) > max(val * TOLERANCE, 1e-9):
                        continue
                    if any(abs(raw - s) <= max(s * TOLERANCE, 1e-9) for s in single):
                        continue        # one row's own figure, not a weighted one
                    found += 1
                    window = t[max(0, m.start() - WINDOW):m.end() + WINDOW]
                    if not CLAUSE.search(window):
                        problems.append(
                            f"  {where}: prints {m.group(0).strip()!r}, which is the "
                            f"{label} capacity total, with no denominator clause. Add "
                            f"{cc.clause(label.split(' / ')[0])!r} to the sentence — "
                            f"see sources/scope.md, 'Admission and capacity are "
                            f"separate questions'.")
                    break
    return problems, found


def self_check(tgt, single) -> None:
    """The gate's own fixtures, run on every build.

    THE SAME REASON check_anchor_text.py CARRIES ITS OWN, and a stronger one here.
    This gate finds nothing on today's pages, so nothing else would notice if a
    refactor quietly broke it: it would go on passing green until the day it was
    needed and did not fire. The fixtures are built from the LIVE totals, so they
    also fail if those stop being reachable.
    """
    cem = cc.weighted_totals("cement").get("t_co2_per_year")
    bat = cc.weighted_totals("batsol").get("GWh_per_year")
    if not cem or not bat:
        return                          # nothing to build a fixture from
    cases = [
        (f"European batteries is building {bat:,.2f} GWh per year of cells.", 1,
         "a whole-sector sum with no clause must fail"),
        (f"European batteries is building {bat:,.2f} GWh per year of cells, "
         f"{cc.clause('batsol')}.", 0, "the same sum with its clause must pass"),
        (f"Europe's cement plants capture {cem / 1e6:g} Mt CO2 per year.", 1,
         "the Mt spelling of a sum must fail"),
        ("It is built for 50 GWh per year.", 0,
         "one plant's own figure is not a weighted figure"),
    ]
    for text, expect, why in cases:
        got, _ = scan(text, "self_check", tgt, single)
        if len(got) != expect:
            raise SystemExit(
                f"check_capacity_clause: SELF-CHECK FAILED — {why}. Expected "
                f"{expect} problem(s), got {len(got)} on: {text!r}")


def main() -> int:
    rows = sm.load("project")
    tgt, single = targets(rows), singles(rows)
    self_check(tgt, single)
    if not PAGES.exists():
        print("check_capacity_clause: no built pages — run after `next build`.")
        return 0
    problems, checked, found = [], 0, 0
    for page in sorted(PAGES.rglob("*.html")):
        checked += 1
        pr, n = scan(text_of(page), str(page.relative_to(PAGES)), tgt, single)
        problems += pr
        found += n
    if problems:
        print(f"check_capacity_clause: {len(problems)} capacity-weighted figure(s) "
              f"rendered without a denominator clause\n")
        print("\n".join(problems))
        return 1
    print(f"check_capacity_clause: OK — {checked} pages, {found} capacity-weighted "
          f"figure(s), all claused; self-check passed."
          + ("" if found else
             " No surface sums capacity yet; the gate binds when one does."))
    for s in cc.SECTORS:
        have, total = cc.denominators(s, rows)
        print(f"  {s}: {have} of {total} plants with a stated capacity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
What a dataset in build-up is still missing, printed on every build.

    python3 report_candidate_gaps.py          # always exits 0; this reports

WHY THIS IS A REPORT AND NOT A GATE
===================================
A gate answers "is what is on file correct". This answers "how much of the
sector is on file at all", and there is no correct answer to it while a dataset
is being built -- only a number that should be going down.

Failing on it would be wrong twice over. It would break the build for the
ordinary state of unfinished research, and it would push somebody to close the
gap by lowering the standard, which is exactly the opposite of what the
perimeter is for.

WHY IT IS CODE AND NOT A PARAGRAPH
==================================
Because the alternative was tried for one turn and did not survive it. The
batteries docket carried the shortfall as prose -- "six rows landed, twenty-eight
candidates outstanding" -- and prose does not recount itself when a row lands. A
number nobody recomputes is a number that is wrong by the following week, and
this particular number decides whether the sector's picture can honestly be
drawn.

WHAT IT READS
=============
sources/<sector>_candidates.json: the admitted set, each entry carrying the
project id it will take, a company source or null, and a coordinate source type
or null. A candidate whose id is already a row in data/transition/projects.json
has landed and is not asked for again.

The two things a candidate needs are reported separately, because they are two
different pieces of work with different remedies. A missing COMPANY SOURCE means
nobody has read the operator saying it is building this. A missing COORDINATE
means nobody can put it on the paper -- and since the coordinate rule widened,
that is no longer the same as "OpenStreetMap has not drawn it".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import sector_map as sm

HERE = Path(__file__).resolve().parent


def candidate_files() -> list[Path]:
    """Every *_candidates.json beside this file. Found rather than listed, so a
    second sector in build-up is reported by existing rather than by an edit."""
    return sorted(HERE.glob("*_candidates.json"))


def report(path: Path, projects: dict[str, dict]) -> tuple[int, int, int]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc["candidates"]
    sector = doc.get("sector", "?")

    landed, no_source, no_coord, no_capacity, blocked = [], [], [], [], []
    for r in rows:
        if r["id"] in projects:
            landed.append(r)
            # A landed row can still be short of a capacity figure: the perimeter
            # admits one on a company or state description of commercial-scale
            # intent, and says the figure stays outstanding until it exists.
            if r.get("capacity_gwh") is None:
                no_capacity.append(r)
            continue
        if not r.get("company_source"):
            (blocked if r.get("company_source_blocked") else no_source).append(r)
        if not r.get("coordinate_source"):
            no_coord.append(r)

    total = len(rows)
    print(f"report_candidate_gaps: {sector} — {len(landed)} of {total} candidate(s) "
          f"on file, {total - len(landed)} outstanding")

    def block(title: str, items: list[dict], key: str) -> None:
        if not items:
            return
        print(f"\n  {title} ({len(items)}):")
        for r in sorted(items, key=lambda x: (x["country"], x["id"])):
            note = r.get("note")
            print(f"    {r['country']}  {r['id']:30} {r['company']}")
            if note:
                print(f"        {note}")

    block("no company source read", no_source, "company_source")
    # SEPARATED FROM THE ABOVE ON PURPOSE. These are not research, they are a
    # minute in a browser: the document is identified and the fetcher is being
    # refused. Mixed into the same list they look like the same problem and get
    # the same effort, which is how a five-minute job stays open for a month.
    if blocked:
        print(f"\n  company source located, this pipeline cannot read it ({len(blocked)}) "
              f"— open in a browser and quote it:")
        for r in sorted(blocked, key=lambda x: (x["country"], x["id"])):
            print(f"    {r['country']}  {r['id']:30} {r['company_source_blocked']}")
    block("no coordinate from a citable source", no_coord, "coordinate_source")
    block("on file, capacity figure still outstanding", no_capacity, "capacity_gwh")

    # WHAT THE PICTURE WOULD SAY IF DRAWN TODAY. The one number that decides
    # whether a sector overview can be published honestly, computed rather than
    # asserted: an overview drawn on a third of a sector is a picture that
    # understates it, and the standfirst has no clause that can rescue that.
    if landed and total:
        share = 100 * len(landed) / total
        print(f"\n  an overview drawn today would show {len(landed)} of {total} "
              f"admitted candidate(s) — {share:.0f}% of the sector as the perimeter "
              f"admits it")
    return len(landed), total, len(no_source) + len(no_coord)


def draw_holds() -> None:
    """Print any sector whose page is built and deliberately not drawn.

    Printed on every build, beside the gap it exists because of. A hold nobody
    is reminded of is a hold that either stays on after the reason has gone or
    comes off without anybody deciding it should.
    """
    path = sm.DATA / "draw_holds.json"
    if not path.exists():
        return
    holds = (json.loads(path.read_text(encoding="utf-8")).get("holds") or {})
    if not holds:
        return
    print(f"\nheld from drawing ({len(holds)}) — data built, page withheld:")
    for sector, h in sorted(holds.items()):
        print(f"  {sector}  since {h.get('since', '?')}")
        print(f"      {h.get('reason', '')}")
        print(f"      released by: {h.get('released_by', '?')}")


def capacity_queue() -> None:
    """Print the landed rows whose capacity is still outstanding.

    THE SAME REASON draw_holds IS HERE. The batteries docket carried its
    shortfall as prose and the prose was wrong by the following week, because a
    number nobody recomputes does not recount itself when a row lands. This one
    is read from sources/capacity_queue.json and counted on every build, and it
    empties itself: a row that gets a capacity_value is dropped from the print
    whether or not anybody remembered to edit the queue.

    A REPORT AND NOT A GATE, like everything else in this file. A row with no
    stated capacity is the ordinary state of unfinished research, and failing on
    it would push somebody to close the gap by inventing a figure -- which is
    the one outcome the perimeter exists to prevent.
    """
    path = sm.ROOT / "sources" / "capacity_queue.json"
    if not path.exists():
        return
    entries = (json.loads(path.read_text(encoding="utf-8")).get("outstanding") or [])
    if not entries:
        return
    projects = {r["id"]: r for r in sm.load("project")}
    open_ = [e for e in entries
             if projects.get(e["project"], {}).get("capacity_value") in (None, "")]
    landed = [e["project"] for e in entries if e not in open_]
    print(f"\ncapacity outstanding ({len(open_)}) — landed rows with no stated figure:")
    for e in sorted(open_, key=lambda x: x["project"]):
        print(f"  {e['project']}  [{e.get('kind', '?')}]")
        print(f"      {e.get('reason', '')}")
        print(f"      closes it: {e.get('closes_it', '?')}")
    if landed:
        print(f"  {len(landed)} entr(y/ies) now filled and can be dropped from the "
              f"queue: {', '.join(sorted(landed))}")


def schedule_queue() -> None:
    """Landed rows with no stated schedule, printed and self-emptying.

    Same shape and same reason as capacity_queue above: a shortfall carried as
    prose is wrong by the following week, and this one is the larger of the two.
    """
    path = sm.ROOT / "sources" / "schedule_queue.json"
    if not path.exists():
        return
    entries = (json.loads(path.read_text(encoding="utf-8")).get("outstanding") or [])
    if not entries:
        return
    projects = {r["id"]: r for r in sm.load("project")}
    open_ = [e for e in entries
             if not (projects.get(e["project"], {}).get("stated_schedule") or [])]
    if not open_:
        print("\nschedule outstanding: none — every queued row now states a date.")
        return
    kinds: dict[str, int] = {}
    for e in open_:
        kinds[e.get("kind", "?")] = kinds.get(e.get("kind", "?"), 0) + 1
    print(f"\nschedule outstanding ({len(open_)}) — landed rows stating no date: "
          + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())))
    for e in sorted(open_, key=lambda x: (x.get("sector", ""), x["project"])):
        print(f"  {e.get('sector', '?'):8} {e['project']:30} [{e.get('kind', '?')}]")


def coverage(projects: dict[str, dict]) -> None:
    """TWO NUMBERS PER SECTOR, because one of them has been doing the work of both.

    A sector's row count has always been read as its coverage, and since the ruling of
    9 September 2026 that POSITION IS NOT AN ADMISSION LEG, it cannot be: a row admitted
    with `located: "no"` is on file, counted, and on no map. Hydrogen went from 22 rows
    to 66 on 10 September and from 11 drawn to 11 drawn. A reader given only "66" would
    have concluded the picture had trebled.

    So both are stated, always, and the gap between them is the drawing backlog rather
    than a defect in the data.
    """
    by: dict[str, list] = {}
    for row in projects.values():
        sector = row.get("sector") or "?"
        e = by.setdefault(sector, [0, 0, {}, {}])
        drawn = row.get("located") == "yes"
        e[0 if drawn else 1] += 1
        v, unit = row.get("capacity_value"), row.get("capacity_unit")
        if v not in (None, "") and unit:
            pot = e[2] if drawn else e[3]
            pot[unit] = pot.get(unit, 0) + v

    def cap(pot: dict) -> str:
        # SUMMED PER UNIT AND NEVER ACROSS UNITS. Three units measure one electrolyser
        # here and the register does not convert between them.
        return "; ".join(f"{v:,.0f} {u}" for u, v in sorted(pot.items())) or "-"

    print("\nreport_candidate_gaps: coverage — rows drawn against rows admitted undrawn")
    print(f"  {'sector':10} {'drawn':>7} {'undrawn':>9} {'rows':>7}   "
          f"{'capacity drawn':>28}   capacity admitted undrawn")
    for sector in sorted(by):
        d, u, cd, cu = by[sector]
        print(f"  {sector:10} {d:>7} {u:>9} {d + u:>7}   {cap(cd):>28}   {cap(cu)}")
    d = sum(v[0] for v in by.values())
    u = sum(v[1] for v in by.values())
    print(f"  {'all':10} {d:>7} {u:>9} {d + u:>7}")
    print("  A row admitted undrawn is on file and on no map. The two numbers are stated "
          "side by\n  side because the first has been read as the second, and since "
          "position stopped being\n  an admission leg it cannot be. THE CAPACITIES ARE "
          "NOT ADDED EITHER: megawatts on a\n  row nobody has placed are not sited "
          "capacity, and a single total beside a map showing\n  eleven marks would invite "
          "exactly the reading the standfirst rule exists to prevent.")


def dropped_from_benchmark(projects: dict[str, dict]) -> None:
    """Rows whose benchmark entry left the list between vintages — RULE 17'S QUEUE.

    A project that vanishes from a database is a project whose failure nobody counts, so
    the register goes and looks. WHAT IT LOOKS AT IS WHETHER THE OWNER'S SOURCE STILL
    STANDS — not whether the project stopped. The benchmark's silence is evidence about
    the benchmark.

    `dropped_from_benchmark` is a ROW COVARIATE. It is never a rung, never a status, and
    no status_history event is written from it. Printed here as a queue so the look is
    somebody's task rather than somebody's memory.
    """
    queue = [(pid, r) for pid, r in sorted(projects.items())
             if r.get("dropped_from_benchmark")]
    if not queue:
        return
    n = sum(len(r["dropped_from_benchmark"]["entries"]) for _, r in queue)
    print(f"\nreport_candidate_gaps: dropped from the benchmark between vintages — "
          f"{len(queue)} row(s), {n} entr(ies).\n  RULE 17'S QUEUE: each is to be looked at "
          f"for whether the OWNER'S source still stands. The benchmark's\n  silence is "
          f"evidence about the benchmark. Not worked here.")
    for pid, r in queue:
        d = r["dropped_from_benchmark"]
        print(f"  {pid:34} {d['present_in']} -> absent")
        for e in d["entries"]:
            print(f"      ref {e['ref']:>5}  last status {e['last_status']:<18} {e['name'][:52]}")


def main() -> int:
    files = candidate_files()
    if not files:
        print("report_candidate_gaps: no *_candidates.json — nothing in build-up")
        return 0
    projects = {r["id"]: r for r in sm.load("project")}
    for path in files:
        report(path, projects)
    draw_holds()
    capacity_queue()
    schedule_queue()
    coverage(projects)
    dropped_from_benchmark(projects)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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


def main() -> int:
    files = candidate_files()
    if not files:
        print("report_candidate_gaps: no *_candidates.json — nothing in build-up")
        return 0
    projects = {r["id"]: r for r in sm.load("project")}
    for path in files:
        report(path, projects)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

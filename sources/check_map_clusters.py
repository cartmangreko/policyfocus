#!/usr/bin/env python3
"""The overview's clustering adds up, no marker spans a border, and every marker
has somewhere to go.

    python3 check_map_clusters.py          # exits non-zero on any violation

WHY A GATE AND NOT A TEST. Brief 16 puts a numbered marker on the continental
overview standing for several sites at one place, and a reader has no way of
checking it: a ring marked "4" is a claim about four rows, and the four are on
another page. The thing that makes the claim honest is arithmetic — every drawn
site is in exactly one group, every group's count is its membership, and the
groups and the singles add up to the marks on the paper — and arithmetic that
nobody recomputes is arithmetic that goes wrong the week after it is written.

WHAT IT CHECKS, and each one is a way the picture could lie:

1  THE PARTITION. singles + every group's membership == the marks on the frame,
   per sector. A mark in two groups would be drawn twice; a mark in none would
   be a site the picture dropped and the standfirst still counted.

2  NO GROUP SPANS A BORDER. A marker carries one country's count and links to
   one country's view, so a group holding Aachen and Maastricht would be a
   marker with two destinations and a count belonging to neither.

3  EVERY RADIUS IS KEPT. Every member of a group is within the recorded radius
   of the group's seed, measured in the projection the frame was laid out in.
   This is the one check that re-does the geometry rather than the bookkeeping,
   and it is what stops a refactor of the clustering from quietly producing
   markers that stand for a region.

4  EVERY MARKER AND EVERY LEGEND ROW HAS A TARGET, and the target is a country
   view that was built. A marker linking to a page that does not exist is the
   failure the whole clustering is for, wearing different clothes: a reader
   presses the ring to see the four sites and gets a 404.

5  THE LEGEND SUMS TO THE FRAME. Every country holding a mark has a legend row,
   every legend row's count is its marks, and nothing is in the legend that is
   not on the paper.

6  THE TWO READINGS OF `hasMap` AGREE. Which sectors render the product
   template is decided twice — sm.drawn_sectors() here, and
   web/lib/transition.ts `hasMap` on the web side — and brief 17 §B.3 separated
   that condition from the ranking one. Two readings of one rule held together
   by a comment asking somebody to edit both is what this repository calls a
   mechanism that is not one, so the condition is parsed out of the TypeScript
   and the sector lists are compared.

7  EVERY COUNTRY FRAME IS REACHED AND EVERY REACHED FRAME EXISTS. A frame no
   route enumerates is a file nothing reads; a route with no frame renders
   nothing. The route enumerates from the files, so this checks that the files
   and the marks they were built from still agree.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_maps as bm  # noqa: E402
import sector_map as sm  # noqa: E402

MAPS = sm.DATA / "maps"
TRANSITION_TS = sm.ROOT / "web" / "lib" / "transition.ts"

# How `hasMap` is written on the web side. Deliberately brittle: it recognises
# the exact shape the module uses, and a rewrite that changes the shape fails
# loudly here rather than passing vacuously. A gate that silently matches
# nothing is worse than no gate — the same note check_section_order.py carries.
HAS_MAP = re.compile(
    r"export function hasMap\(sector: string\): boolean \{\s*"
    r"return getProjects\(sector\)\.some\(isDrawable\);\s*\}")
IS_DRAWABLE = re.compile(
    r"export function isDrawable\(p: Project\): boolean \{\s*"
    r"return \(p\.location\?\.length \?\? 0\) > 0 && "
    r"!UNDRAWN_STATUSES\.includes\(p\.status\);\s*\}")
UNDRAWN_TS = re.compile(
    r"const UNDRAWN_STATUSES: readonly ProjectStatus\[\] = \[([^\]]*)\];")

# A rendered coordinate is rounded to a tenth of a canvas unit, and the radius
# is a kilometre figure measured on unrounded projection output. Half a
# kilometre of slack is well inside the rounding and nowhere near the 40 km the
# radius actually is.
SLACK_KM = 0.5


def frames() -> dict[str, dict]:
    out = {}
    for path in sorted(MAPS.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        out[path.name] = doc
    return out


def _km(a: dict, b: dict) -> float:
    ax, ay = bm.project(a["lon"], a["lat"])
    bx, by = bm.project(b["lon"], b["lat"])
    return math.hypot(ax - bx, ay - by)


def check_has_map(problems: list[str]) -> None:
    """The web side's condition, parsed, and its answer compared with ours."""
    src = TRANSITION_TS.read_text(encoding="utf-8")
    if not HAS_MAP.search(src):
        problems.append(
            "web/lib/transition.ts `hasMap` is not the shape this gate reads. It "
            "decides which sectors render the product template, sm.drawn_sectors() "
            "decides which sectors get a frame, and the two have to be one rule — "
            "see the note at the top of this file")
        return
    if not IS_DRAWABLE.search(src):
        problems.append(
            "web/lib/transition.ts `isDrawable` is not the shape this gate reads, so "
            "the condition `hasMap` applies cannot be compared with build_maps.drawn()")
        return
    m = UNDRAWN_TS.search(src)
    if not m:
        problems.append("web/lib/transition.ts states no UNDRAWN_STATUSES array")
        return
    ts_statuses = {v.strip().strip('"') for v in m.group(1).split(",") if v.strip()}
    if ts_statuses != set(bm.UNDRAWN_STATUSES):
        problems.append(
            f"UNDRAWN_STATUSES disagree: web/lib/transition.ts says "
            f"{sorted(ts_statuses)}, sources/build_maps.py says "
            f"{sorted(bm.UNDRAWN_STATUSES)}. One status group, two readings")


def main() -> int:
    projects = sm.load("project")
    docs = frames()
    problems: list[str] = []

    check_has_map(problems)

    # ---- which sectors have an overview at all ----------------------------
    expected = set(sm.drawn_sectors(projects))
    found = {d["subject"] for d in docs.values() if d["kind"] == "sector"}
    for sector in sorted(expected - found):
        problems.append(f"{sector} has a drawn row and no overview frame was written")
    for sector in sorted(found - expected):
        problems.append(f"an overview frame exists for {sector}, which has no drawn row")

    built_countries: set[tuple[str, str]] = {
        (d["sector"], d["country"]) for d in docs.values() if d["kind"] == "country"
    }
    reached: set[tuple[str, str]] = set()
    checked_groups = checked_marks = 0

    for name, doc in sorted(docs.items()):
        if doc["kind"] != "sector":
            continue
        sector = doc["subject"]
        marks = doc["marks"]
        clusters = doc.get("clusters")
        totals = doc.get("country_totals")
        if clusters is None or totals is None:
            problems.append(
                f"{name} is an overview with no clusters or no country legend. Every "
                f"overview carries both since brief 16; a frame without them is a "
                f"frame built by an older builder and left on disk")
            continue

        # ---- 1 the partition ---------------------------------------------
        members = [s for g in clusters["groups"] for s in g["sites"]]
        keys = [(s["id"], s["site"]) for s in members]
        if len(keys) != len(set(keys)):
            dupes = sorted({k for k in keys if keys.count(k) > 1})
            problems.append(f"{sector}: {dupes} appear(s) in more than one cluster")
        grouped = clusters["clustered_sites"]
        if grouped != len(members):
            problems.append(
                f"{sector}: clusters.clustered_sites says {grouped} and the groups "
                f"hold {len(members)} site(s)")
        if clusters["singles"] + len(members) != len(marks):
            problems.append(
                f"{sector}: {clusters['singles']} single(s) + {len(members)} "
                f"clustered site(s) is {clusters['singles'] + len(members)}, and the "
                f"frame draws {len(marks)} mark(s). Every drawn site belongs to "
                f"exactly one group")
        mark_keys = {(m["id"], m["site"]) for m in marks}
        for key in sorted(set(keys) - mark_keys):
            problems.append(f"{sector}: cluster holds {key}, which is not a mark on "
                            f"the frame")

        # ---- the drawn rows the register says there are -------------------
        want = [r for r in projects
                if r["sector"] == sector and bm.drawn(r) and bm._sites(r)]
        want_sites = sum(len(bm._sites(r)) for r in want)
        if want_sites != len(marks):
            problems.append(
                f"{sector}: the register holds {want_sites} drawn site(s) across "
                f"{len(want)} row(s) and the frame draws {len(marks)}")

        by_country: dict[str, int] = {}
        for m in marks:
            by_country[m["country"]] = by_country.get(m["country"], 0) + 1

        for g in clusters["groups"]:
            checked_groups += 1
            rows = [m for m in marks if (m["id"], m["site"]) in
                    {(s["id"], s["site"]) for s in g["sites"]}]
            # ---- 2 no group spans a border -------------------------------
            countries = {m["country"] for m in rows}
            if countries != {g["country"]}:
                problems.append(
                    f"{sector}: cluster {g['key']} says {g['country']} and holds sites "
                    f"in {sorted(countries)}. A marker carries one country's count and "
                    f"links to one country's view")
            if g["count"] != len(g["sites"]):
                problems.append(
                    f"{sector}: cluster {g['key']} says {g['count']} and lists "
                    f"{len(g['sites'])} site(s)")
            # ---- 3 the radius is kept ------------------------------------
            seed = next((m for m in rows
                         if f"{m['id']}::{m['site']}" == g["key"]), None)
            if seed is None:
                problems.append(
                    f"{sector}: cluster {g['key']} names a seed that is not one of its "
                    f"own sites, so the radius cannot be checked against anything")
            else:
                for m in rows:
                    far = _km(seed, m)
                    if far > clusters["radius_km"] + SLACK_KM:
                        problems.append(
                            f"{sector}: cluster {g['key']} holds {m['id']} "
                            f"({m['site']}) at {far:.1f} km from its seed, outside the "
                            f"recorded {clusters['radius_km']:g} km. A marker that "
                            f"reaches further than its radius stands for a region "
                            f"rather than for a place")
            # ---- 4 the marker has a target -------------------------------
            want_href = f"/sectors/{sector}/projects/{g['country']}"
            if g["href"] != want_href:
                problems.append(f"{sector}: cluster {g['key']} links to {g['href']!r} "
                                f"and should link to {want_href!r}")
            reached.add((sector, g["country"]))

        # ---- 4 every mark has a target too -------------------------------
        for m in marks:
            checked_marks += 1
            want_href = f"/sectors/{sector}/projects/{m['country']}"
            if m.get("country_href") != want_href:
                problems.append(
                    f"{sector}: mark {m['id']} ({m['site']}) carries country_href "
                    f"{m.get('country_href')!r} and should carry {want_href!r}")
            reached.add((sector, m["country"]))

        # ---- 5 the legend sums to the frame ------------------------------
        legend = {t["iso"]: t for t in totals}
        for iso, n in sorted(by_country.items()):
            row = legend.get(iso)
            if row is None:
                problems.append(f"{sector}: {iso} holds {n} mark(s) and has no legend "
                                f"row, so nothing on the page links to its view")
                continue
            if row["sites"] != n:
                problems.append(f"{sector}: the legend says {iso} holds "
                                f"{row['sites']} site(s) and the frame draws {n}")
            if row["href"] != f"/sectors/{sector}/projects/{iso}":
                problems.append(f"{sector}: the legend row for {iso} links to "
                                f"{row['href']!r}")
            reached.add((sector, iso))
        for iso in sorted(set(legend) - set(by_country)):
            problems.append(f"{sector}: the legend carries {iso}, which has no mark "
                            f"on the paper")

    # ---- 7 frames and routes ---------------------------------------------
    for pair in sorted(reached - built_countries):
        problems.append(f"{pair[0]}: a marker or legend row links to the {pair[1]} "
                        f"country view and no frame was written for it")
    for pair in sorted(built_countries - reached):
        problems.append(f"{pair[0]}: a frame exists for {pair[1]} and nothing on the "
                        f"overview links to it")

    # ---- the country frames' own arithmetic ------------------------------
    for name, doc in sorted(docs.items()):
        if doc["kind"] != "country":
            continue
        sector, iso = doc["sector"], doc["country"]
        want = [r for r in projects
                if r["sector"] == sector and r["country"] == iso
                and bm.drawn(r) and bm._sites(r)]
        want_sites = sum(len(bm._sites(r)) for r in want)
        if want_sites != len(doc["marks"]):
            problems.append(
                f"{sector}/{iso}: the register holds {want_sites} drawn site(s) and "
                f"the country frame draws {len(doc['marks'])}")
        for m in doc["marks"]:
            if m["country"] != iso:
                problems.append(f"{sector}/{iso}: the country frame draws "
                                f"{m['id']} ({m['site']}), which is in {m['country']}")
            if m.get("clustered"):
                problems.append(
                    f"{sector}/{iso}: {m['id']} is flagged clustered on a country "
                    f"frame. Nothing is grouped here — that is the point of the page")
        if "clusters" in doc:
            problems.append(f"{sector}/{iso}: a country frame carries a clustering, "
                            f"and a country frame clusters nothing")

    if problems:
        print(f"check_map_clusters: {len(problems)} problem(s)\n")
        print("\n".join(f"  {p}" for p in problems))
        return 1

    sectors = sum(1 for d in docs.values() if d["kind"] == "sector")
    print(f"check_map_clusters: OK — {sectors} overview(s), {checked_marks} mark(s) "
          f"partitioned into {checked_groups} cluster(s) and "
          f"{checked_marks - sum(g['count'] for d in docs.values() if d['kind'] == 'sector' for g in d['clusters']['groups'])} "
          f"single(s) at {bm.CLUSTER_RADIUS_KM:g} km; "
          f"{len(built_countries)} country frame(s), every one reached and every "
          f"marker and legend row targeted; `hasMap` and drawn_sectors() agree on "
          f"{', '.join(sorted(sm.drawn_sectors(projects)))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
The gate on where the register says things are: every sited coordinate in
data/transition/projects.json, held against the committed basemap.

    python3 check_coordinates.py          # exits non-zero on any point it cannot place

WHY THIS IS A GATE AND NOT A GLANCE. check_sector_schema.py already refuses a
project with no coordinates, a latitude outside -90..90 and a `precision` of
"town". None of that catches the failure that actually happens: a real number,
in range, in the wrong place. A transposed lat and lon puts Duisburg in the
Indian Ocean; a dropped decimal puts it two hundred kilometres north; a copied
row puts one plant on top of another. Every one of those renders. This is the
only check that reads the number as a position rather than as a value.

THE RULE, AND WHY IT HAS A TOLERANCE

A point passes if it is inside the country its row declares, or within
TOLERANCE_KM of it. Strict containment would fail five points that are correct:
Natural Earth at 1:10m is a generalisation, and a works on a quay, a pilot plant
on a headland or a terminal on a small island can all sit just outside a
coastline that has been smoothed past them. A tolerance of ten kilometres is
wide enough to absorb that and far narrower than any of the errors above --
the smallest of which, a dropped decimal at these latitudes, is tens of
kilometres.

THE EXCEPTIONS, AND WHY THEY ARE NOT A TOLERANCE

A geological store is genuinely offshore. Galata is twenty-three kilometres out
in the Black Sea and no honest tolerance covers it, because a tolerance wide
enough to admit it would be wide enough to admit a wrong plant. So offshore
stores are named here one at a time, each with the distance measured when it was
recorded and one line saying why it is out there. That is the whole difference
between an exception and a loophole: the list is short, every entry is a
sentence somebody wrote, and the gate prints all of them on every run.

An exception does not stop the point being checked. It replaces the question:
instead of "is this near land", the gate asks "is this still where the exception
says it is", and a point that drifts more than DRIFT_KM fails. An exception may
only cover a site on a `role: "storage"` row, so that the list cannot quietly
become the place bad plant coordinates go to be forgiven. An entry naming a site
that no longer exists fails too -- a stale exception is a rule nobody is
applying to anything.
"""

from __future__ import annotations

import sys

import natural_earth as ne
import sector_map as sm

# Wide enough for a generalised coastline, narrow enough to catch a dropped
# decimal. See the module docstring.
TOLERANCE_KM = 10.0

# How far a recorded exception may move before it stops covering its point. An
# exception is a statement about one position, not a licence for the row.
DRIFT_KM = 5.0

# ---------------------------------------------------------------------------
# The offshore stores. Keyed "<project id>::<site>", which is how a site is
# named in the data rather than by an index that renumbers when a list changes.
#
# `km` is the distance to the declared country measured when the entry was
# written. It is not a limit and not a target: it is the number the gate holds
# the point against, so that moving a store quietly is not something this list
# makes possible.
# ---------------------------------------------------------------------------
OFFSHORE = {
    "northern-lights::Øygarden receiving terminal, Naturgassparken": {
        "km": 4.17,
        "why": "Øygarden is an archipelago west of Bergen and the terminal is on "
               "Ljøsøyna; the 1:10m coastline drops the island the site is on.",
    },
    "galata-co2-storage::Galata gas field, Black Sea": {
        "km": 22.91,
        "why": "A depleted gas field on the continental shelf, which its source "
               "puts about 25 km south-east of Varna. The measured distance is "
               "the closest thing this register has to a check on that sentence.",
    },
    "prinos-co2-storage::Prinos production platforms, Gulf of Kavala": {
        "km": 7.55,
        "why": "Production platforms in the Gulf of Kavala, between Thasos and "
               "the mainland; the point is water on every map, correctly.",
    },
}


def main() -> int:
    lands = ne.countries()
    errors: list[str] = []
    noted: list[str] = []
    placed = 0
    used: set[str] = set()

    for project in sm.load("project"):
        pid = project["id"]
        rings = lands.get(project.get("country", ""))
        if rings is None:
            errors.append(f"project {pid}: country={project.get('country')!r} is not a "
                          f"country in the basemap, so no point on this row can be placed")
            continue
        for site in project.get("location") or []:
            key = f"{pid}::{site['site']}"
            point = (site["lon"], site["lat"])
            inside = ne.contains(point, rings)
            km = 0.0 if inside else ne.distance_km(point, rings)
            where = f"project {pid} location[{site['site']}]"

            exception = OFFSHORE.get(key)
            if exception:
                used.add(key)
                if project.get("role") != "storage":
                    errors.append(f"{where}: has an offshore exception and is not a storage "
                                  f"row. The list is for stores, not for plants that landed "
                                  f"in the sea")
                    continue
                drift = abs(km - exception["km"])
                if drift > DRIFT_KM:
                    # All three numbers, each labelled. An earlier wording gave the
                    # drift last and unlabelled, and it was read as the measured
                    # distance -- which makes a firing test look like a passing one.
                    errors.append(f"{where}: measured {km:.2f} km from "
                                  f"{project['country']}, recorded {exception['km']:.2f} km, "
                                  f"drift {drift:.2f} km, which is past the "
                                  f"{DRIFT_KM:.0f} km limit. Re-measure and re-record it, or "
                                  f"find out why the point changed")
                    continue
                noted.append(f"  {km:6.2f} km  {key}\n             {exception['why']}")
                placed += 1
                continue

            if inside or km <= TOLERANCE_KM:
                placed += 1
                continue

            errors.append(
                f"{where}: {km:.2f} km outside {project['country']}, past the "
                f"{TOLERANCE_KM:.0f} km tolerance. Either the coordinate is wrong — check "
                f"for a transposed latitude and longitude, or a lost decimal — or this is "
                f"genuinely offshore, in which case it is a storage row and belongs in "
                f"OFFSHORE in this file with its distance and a reason")

    for stale in sorted(set(OFFSHORE) - used):
        errors.append(f"OFFSHORE: {stale} names a site that is not in projects.json — a "
                      f"stale exception is a rule being applied to nothing")

    if errors:
        print(f"check_coordinates: {len(errors)} problem(s)\n")
        print("\n".join(f"  {line}" for line in errors))
        return 1

    print(f"check_coordinates: OK — {placed} sited point(s) placed against Natural Earth, "
          f"tolerance {TOLERANCE_KM:.0f} km")
    if noted:
        print(f"\noffshore exceptions ({len(noted)}) — recorded, never silent:")
        print("\n".join(noted))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(sm.ROOT / "sources"))
    raise SystemExit(main())

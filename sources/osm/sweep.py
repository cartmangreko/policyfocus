"""A coordinate sweep against a dated Geofabrik extract, read locally.

    python3 sources/osm/sweep.py <extract.osm.pbf> <lat> <lon> <radius_m> [label]

WHAT A SWEEP ANSWERS is not "is anything drawn here" but "is anything drawn here that is
the works". Four buckets, in the order the perimeter cares about:

    works   a named man_made=works, power=plant or tagged industrial feature that could be
            the plant itself
    estate  a named industrial park, port or business park — REFUSED as a position under
            the Subotica and Mo i Rana rule, and counted to size the problem
    parcel  unnamed industrial landuse or buildings, which a permit could later confirm
    none    nothing of any of those inside the radius

THE EXTRACT DATE IS PART OF THE ANSWER. Geofabrik redirects `-latest` to a dated filename
and this tool refuses a file whose date it cannot read, because a sweep that cannot say
which day's basemap it read is not repeatable and is therefore not evidence.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pbf  # noqa: E402

ESTATE_WORDS = ("industriegebiet", "gewerbe", "industrial estate", "industrial park",
                "polígono", "poligono", "zona industrial", "parque", "hafen", "port ",
                "puerto", "industripark", "zone industrielle", "bedrijventerrein")
DATED = re.compile(r"-(\d{6})\.osm\.pbf$")


def extract_date(path: Path) -> str:
    m = DATED.search(path.name)
    if not m:
        raise SystemExit(f"{path.name} carries no Geofabrik date; re-download the dated "
                         f"filename so the sweep can say which basemap it read")
    y, mo, d = m.group(1)[:2], m.group(1)[2:4], m.group(1)[4:]
    return f"20{y}-{mo}-{d}"


def metres(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def interesting(tags: dict) -> bool:
    return (tags.get("man_made") == "works" or tags.get("power") in ("plant", "substation")
            or tags.get("landuse") in ("industrial", "port") or "industrial" in tags
            or tags.get("building") == "industrial")


def sweep(path: Path, lat: float, lon: float, radius: int) -> dict:
    box = radius / 111320.0 * 1.6
    want_nodes: dict[int, list] = {}
    ways: list[tuple] = []
    named_here, parcels = [], 0

    for raw in pbf.blocks(path):
        for item in pbf.parse_block(raw):
            if item[0] == "node":
                _, _, la, lo, tags = item
                if not tags or not interesting(tags):
                    continue
                if abs(la - lat) > box or abs(lo - lon) > box:
                    continue
                if metres(lat, lon, la, lo) > radius:
                    continue
                if tags.get("name"):
                    named_here.append((tags["name"], tags))
                else:
                    parcels += 1
            else:
                _, _, refs, tags = item
                if not tags or not interesting(tags) or not refs:
                    continue
                ways.append((refs[0], tags))
                want_nodes[refs[0]] = None

    if want_nodes:                       # second pass: resolve one node per way
        for raw in pbf.blocks(path):
            for item in pbf.parse_block(raw):
                if item[0] != "node":
                    continue
                _, nid, la, lo, _ = item
                if nid in want_nodes:
                    want_nodes[nid] = (la, lo)

    for ref, tags in ways:
        pos = want_nodes.get(ref)
        if not pos or metres(lat, lon, pos[0], pos[1]) > radius:
            continue
        if tags.get("name"):
            named_here.append((tags["name"], tags))
        else:
            parcels += 1

    # AN ESTATE IS NAMED LIKE AN ESTATE. The first version of this test also sent every
    # landuse=industrial feature to `estate`, and that put "cimenterie Vicat" — the cement
    # works Hynovi's electrolyser is to stand on, drawn and named by its operator — in the
    # bucket the perimeter refuses. A polygon's landuse tag says what the land is used for,
    # not whether it is one company's works or forty companies' park; the NAME is what
    # distinguishes them, and where the name is a company's it is a works.
    works, estates = [], []
    for name, tags in named_here:
        low = name.lower()
        (estates if any(w in low for w in ESTATE_WORDS) else works).append(
            f"{name} [{tags.get('landuse') or tags.get('man_made') or tags.get('power') or 'industrial'}]")
    return {"basemap_date": extract_date(path), "extract": path.name,
            "lat": lat, "lon": lon, "radius_m": radius,
            "verdict": "works" if works else "estate" if estates
                       else "parcel" if parcels else "none",
            "named_works": sorted(set(works))[:12],
            "named_estates": sorted(set(estates))[:12],
            "unnamed_industrial_parcels": parcels}


if __name__ == "__main__":
    p = Path(sys.argv[1])
    out = sweep(p, float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]))
    if len(sys.argv) > 5:
        out["id"] = sys.argv[5]
    print(json.dumps(out, ensure_ascii=False, indent=1))

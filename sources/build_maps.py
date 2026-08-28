"""
Lay out the geography, deterministically, at build time.

    python3 build_maps.py            # writes data/transition/maps/*.json
    python3 build_maps.py --check    # rebuilds and diffs; non-zero on drift

WHY THE GEOMETRY IS COMPUTED HERE AND NOT IN THE BROWSER
========================================================
The same reason the sector diagram's is: a projection running in the page makes
the picture a function of the reader's browser, and the shipped basemap is a
5 MB shapefile nobody should be parsing on a phone. Coordinates computed here
are reviewable in a diff, identical for everybody, and the component that draws
them does no layout at all.

THE PROJECTION
==============
Lambert conformal conic on a sphere of radius 6371 km, with the parameters
EPSG:3034 uses for Europe -- standard parallels 35 N and 65 N, latitude of
origin 52 N, central meridian 10 E. That is the projection the European
statistical system draws the continent in, so the shape a reader sees here is
the shape they have seen everywhere else.

SPHERICAL RATHER THAN ELLIPSOIDAL, deliberately. The difference is a few parts
in a thousand across this frame, which is under a pixel at every size these
maps render at, and the spherical form is thirty lines that can be read and
checked. Nothing here is a survey.

WHAT A FRAME CONTAINS
=====================
A sector frame is EUROPE, fixed, identical for every sector. An overview whose
extent changed per sector would make two sectors' pictures incomparable at
exactly the moment a reader is comparing them, and the empty space is itself
information: steel's absence from the south is a fact about steel.

A project frame is a REGIONAL CROP, and it is built in the order the brief
gives:

  1  the project's own sites, always. A project with two sites gets both.
  2  the nodes it depends on, always -- the store its captured tonne reaches.
     These two sets fix the frame, which is then padded by PADDING_KM and
     grown to MIN_SPAN_KM if the result is tighter than that.
  3  then neighbours sharing a technology, and
  4  then neighbours in the same sector,
     drawn where they FALL INSIDE the frame already fixed. They are context,
     not subjects: a same-technology neighbour in Greece does not get to drag
     a Norwegian crop across the continent. Priority decides what a mark is
     labelled as, not whether the frame moves.

COASTLINES ARE STROKED, NOT FILLED, SO THEY ARE CLIPPED AS LINES
================================================================
Clipping a country polygon to the frame the usual way -- Sutherland-Hodgman --
closes the shape along the frame edge, which is correct for a fill and a lie for
a stroke: the reader gets a straight line down the side of the picture that
looks exactly like a coast. So each ring is walked as a sequence of segments and
emitted as one or more OPEN polylines, with the crossing segments clipped to the
boundary and nothing joining them. A country that leaves the frame and comes
back is two strokes, which is what it looks like on paper.

Internal borders are drawn twice, once from each side, because both countries
carry that boundary in their own ring. The two strokes are the same line to
within floating point and the duplication costs bytes rather than appearance;
de-duplicating shared boundaries is a graph problem this file is not going to
solve for a hairline.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import natural_earth as ne
import sector_map as sm

OUT_DIR = sm.ROOT / "data" / "transition" / "maps"

# ---------------------------------------------------------------------------
# Projection: EPSG:3034's parameters, spherical form
# ---------------------------------------------------------------------------
R_KM = 6371.0
STANDARD_PARALLELS = (35.0, 65.0)
ORIGIN_LAT = 52.0
CENTRAL_MERIDIAN = 10.0


def _lcc():
    p1, p2 = (math.radians(p) for p in STANDARD_PARALLELS)
    p0 = math.radians(ORIGIN_LAT)
    n = (math.log(math.cos(p1) / math.cos(p2))
         / math.log(math.tan(math.pi / 4 + p2 / 2) / math.tan(math.pi / 4 + p1 / 2)))
    f = math.cos(p1) * math.tan(math.pi / 4 + p1 / 2) ** n / n
    rho0 = R_KM * f / math.tan(math.pi / 4 + p0 / 2) ** n
    return n, f, rho0


_N, _F, _RHO0 = _lcc()


def project(lon: float, lat: float) -> tuple[float, float]:
    """(lon, lat) in degrees to (x, y) in kilometres, y already flipped so that
    north is up in a coordinate system where down is positive -- which is what
    SVG wants and what every consumer of this file expects."""
    phi, lam = math.radians(lat), math.radians(lon)
    rho = R_KM * _F / math.tan(math.pi / 4 + phi / 2) ** _N
    theta = _N * (lam - math.radians(CENTRAL_MERIDIAN))
    return rho * math.sin(theta), -(_RHO0 - rho * math.cos(theta))


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

# The continent, in degrees, sampled along its edges rather than at its corners:
# a conic projection bows a parallel, so the four corners of a lon/lat box are
# not the extremes of its projection.
EUROPE_DEGREES = (-11.0, 34.0, 31.0, 70.5)      # west, south, east, north

# A project crop. Padding is fixed, as the brief says, and the minimum span
# stops a project whose store is fifty kilometres away from being drawn at a
# scale where the coastline is all there is to see.
PADDING_KM = 80.0
MIN_SPAN_KM = 800.0



# Output canvases. Both are in the same units the projection produces, scaled to
# fit; the aspect is fixed per kind so that two sector overviews are the same
# picture at the same size, and every project crop is too.
SECTOR_CANVAS = (760.0, 790.0)
PROJECT_CANVAS = (760.0, 430.0)

# How hard the coastline is simplified, in output units. Douglas-Peucker at 0.5
# leaves a line that is smooth at the size these render and drops most of the
# vertices a 1:10m file carries for a continent.
SIMPLIFY = 0.5

# How far outside the frame geometry is kept before clipping, so that a stroke
# joining two vertices just outside the edge still crosses the visible area.
BLEED = 0.06

# Rings smaller than this across, in output units, are dropped. A 1:10m file
# carries every skerry off Norway and every islet in the Aegean, and at
# continental zoom those arrive as a scatter of two-pixel marks that read as
# dirt on the paper rather than as land -- and, worse, as MARKS, which is what
# this picture uses to mean a plant. Dropped at overview scale and kept at crop
# scale, which is the rule a cartographer applies by hand.
MIN_RING_SPAN = 1.6


def europe_frame() -> tuple[float, float, float, float]:
    w, s, e, n = EUROPE_DEGREES
    xs, ys = [], []
    steps = 200
    for i in range(steps + 1):
        lon = w + (e - w) * i / steps
        lat = s + (n - s) * i / steps
        for edge in ((lon, s), (lon, n), (w, lat), (e, lat)):
            x, y = project(*edge)
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def fit(frame: tuple[float, float, float, float],
        canvas: tuple[float, float]) -> tuple[float, float, float, float]:
    """Grow the frame's shorter side until it matches the canvas aspect, so the
    picture is never stretched. Growing rather than cropping: a frame is the set
    of things that have to be visible, and shrinking it to fit would drop one."""
    x0, y0, x1, y1 = frame
    cw, ch = canvas
    w, h = x1 - x0, y1 - y0
    if w / h < cw / ch:
        want = h * cw / ch
        cx = (x0 + x1) / 2
        x0, x1 = cx - want / 2, cx + want / 2
    else:
        want = w * ch / cw
        cy = (y0 + y1) / 2
        y0, y1 = cy - want / 2, cy + want / 2
    return x0, y0, x1, y1


# ---------------------------------------------------------------------------
# Clipping a ring into open polylines, and simplifying them
# ---------------------------------------------------------------------------

def _clip_segment(a, b, box):
    """Liang-Barsky. Returns the visible part of the segment, or None."""
    x0, y0, x1, y1 = box
    px, py = a
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, px - x0), (dx, x1 - px), (-dy, py - y0), (dy, y1 - py)):
        if p == 0:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            if t > t1:
                return None
            t0 = max(t0, t)
        else:
            if t < t0:
                return None
            t1 = min(t1, t)
    return ((px + t0 * dx, py + t0 * dy), (px + t1 * dx, py + t1 * dy))


def clip_ring(ring, box):
    """One closed ring to zero or more OPEN polylines inside the box.

    Runs are accumulated rather than each segment being emitted on its own, so a
    coastline that stays in frame is one path and not four hundred.
    """
    out, run = [], []
    n = len(ring)
    for i in range(n):
        piece = _clip_segment(ring[i], ring[(i + 1) % n], box)
        if piece is None:
            if len(run) > 1:
                out.append(run)
            run = []
            continue
        start, end = piece
        if not run:
            run = [start, end]
        elif abs(run[-1][0] - start[0]) < 1e-9 and abs(run[-1][1] - start[1]) < 1e-9:
            run.append(end)
        else:
            if len(run) > 1:
                out.append(run)
            run = [start, end]
    if len(run) > 1:
        out.append(run)
    return out


def simplify(points, tolerance):
    """Douglas-Peucker, iterative so a long coastline cannot blow the stack."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        if last <= first + 1:
            continue
        ax, ay = points[first]
        bx, by = points[last]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        worst, at = -1.0, first
        for i in range(first + 1, last):
            px, py = points[i]
            if norm == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if d > worst:
                worst, at = d, i
        if worst > tolerance:
            keep[at] = True
            stack.append((first, at))
            stack.append((at, last))
    return [p for p, k in zip(points, keep) if k]


def _round(value: float) -> float:
    return round(value, 1)


def land_paths(frame, canvas, tolerance=None, min_ring=None) -> list[str]:
    """Every coastline and border inside the frame, as SVG path data in canvas
    units. Sorted, because two builds of the same frame have to produce the same
    bytes and a dict iteration order is not a promise."""
    x0, y0, x1, y1 = frame
    cw, ch = canvas
    scale = cw / (x1 - x0)
    tolerance = SIMPLIFY if tolerance is None else tolerance
    min_ring = MIN_RING_SPAN if min_ring is None else min_ring
    bleed = ((x1 - x0) * BLEED, (y1 - y0) * BLEED)
    box = (x0 - bleed[0], y0 - bleed[1], x1 + bleed[0], y1 + bleed[1])

    paths: list[str] = []
    for _iso, rings in sorted(ne.countries().items()):
        for ring in rings:
            projected = [project(lon, lat) for lon, lat in ring]
            xs = [p[0] for p in projected]
            ys = [p[1] for p in projected]
            if max(xs) < box[0] or min(xs) > box[2] or max(ys) < box[1] or min(ys) > box[3]:
                continue
            if max(max(xs) - min(xs), max(ys) - min(ys)) * scale < min_ring:
                continue
            for run in clip_ring(projected, box):
                canvas_run = [((px - x0) * scale, (py - y0) * scale) for px, py in run]
                thinned = simplify(canvas_run, tolerance)
                if len(thinned) < 2:
                    continue
                head = f"M{_round(thinned[0][0])} {_round(thinned[0][1])}"
                tail = "".join(f"L{_round(px)} {_round(py)}" for px, py in thinned[1:])
                paths.append(head + tail)
    return sorted(paths)


def unproject(x: float, y: float) -> tuple[float, float]:
    """Back to degrees. Only the frame edges need this -- the coordinates line
    under a sector overview states the extent it is showing -- but a projection
    that cannot be inverted is one nobody can check, so it is here."""
    y = -y
    rho = math.copysign(math.hypot(x, _RHO0 - y), _N)
    theta = math.atan2(x, _RHO0 - y)
    lat = 2 * math.atan((R_KM * _F / rho) ** (1 / _N)) - math.pi / 2
    lon = theta / _N + math.radians(CENTRAL_MERIDIAN)
    return math.degrees(lon), math.degrees(lat)


def frame_degrees(frame) -> dict[str, float]:
    """The frame's extent in degrees, sampled along its edges for the same
    reason europe_frame samples: a conic bows a straight line."""
    x0, y0, x1, y1 = frame
    lons, lats = [], []
    steps = 60
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = y0 + (y1 - y0) * i / steps
        for corner in ((x, y0), (x, y1), (x0, y), (x1, y)):
            lon, lat = unproject(*corner)
            lons.append(lon)
            lats.append(lat)
    return {"west": round(min(lons), 3), "south": round(min(lats), 3),
            "east": round(max(lons), 3), "north": round(max(lats), 3)}


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------

# What a mark's presence in the picture is owed to, most specific first. The
# brief's order, and it decides emphasis, not the frame: see the module
# docstring.
RELATIONS = ("subject", "dependency", "technology", "sector")


def _sites(project: dict) -> list[dict]:
    return project.get("location") or []


def _mark(row: dict, site: dict, relation: str, frame, canvas) -> dict:
    """One mark. `row` is the project, never called `project` in this file --
    that name is the projection function and shadowing it here is how a
    coordinate silently becomes a row."""
    x0, y0, x1, y1 = frame
    scale = canvas[0] / (x1 - x0)
    px, py = project_point(site)
    return {
        "id": row["id"],
        "site": site["site"],
        "role": row.get("role", "plant"),
        "relation": relation,
        "status": row["status"],
        "label": row["name"],
        "sub": row["company"],
        "href": f"/projects/{row['id']}",
        "lat": site["lat"],
        "lon": site["lon"],
        "as_of": site["retrieved_date"],
        "x": round((px - x0) * scale, 1),
        "y": round((py - y0) * scale, 1),
    }


def project_point(site: dict) -> tuple[float, float]:
    return project(site["lon"], site["lat"])


def bounds(sites: list[dict]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for s in sites:
        x, y = project_point(s)
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def _pad(box):
    x0, y0, x1, y1 = box
    return x0 - PADDING_KM, y0 - PADDING_KM, x1 + PADDING_KM, y1 + PADDING_KM


def inside(frame, site) -> bool:
    x0, y0, x1, y1 = frame
    x, y = project_point(site)
    return x0 <= x <= x1 and y0 <= y <= y1


def relations_for(subject: dict, projects: list[dict]) -> dict[str, str]:
    """Every other project's relation to this one, at its strongest. A project
    that is both a same-technology neighbour and a same-sector one is a
    technology neighbour, because that is the closer claim.

    THE DEPENDENCY IS READ BOTH WAYS. A plant depends on the store its tonne
    reaches, and the store's own picture is incomplete without the plants that
    feed it -- a connection is not directional in a picture, whatever it is in
    the graph. Read one way only, Northern Lights' crop showed Northern Lights
    and an empty North Sea.
    """
    out: dict[str, str] = {subject["id"]: "subject"}
    storage = (subject.get("storage") or {}).get("project")
    if storage:
        out[storage] = "dependency"
    for p in projects:
        if (p.get("storage") or {}).get("project") == subject["id"]:
            out.setdefault(p["id"], "dependency")
    subject_tech = set(subject.get("technology") or [])
    for p in projects:
        if p["id"] in out:
            continue
        if subject_tech & set(p.get("technology") or []):
            out[p["id"]] = "technology"
        elif p["sector"] == subject["sector"]:
            out[p["id"]] = "sector"
    return out


# ---------------------------------------------------------------------------
# The two kinds of picture
# ---------------------------------------------------------------------------

# Overview and crop are simplified differently on purpose. At continental scale
# a fjord is noise; at four hundred kilometres across it is the shape of the
# place the plant is in.
SECTOR_DETAIL = {"tolerance": 1.0, "min_ring": 2.2}
PROJECT_DETAIL = {"tolerance": 0.4, "min_ring": 0.8}

PROJECTION = {
    "name": "Lambert conformal conic",
    "basis": "EPSG:3034 parameters (ETRS89-extended / LCC-Europe), spherical form",
    "standard_parallels": list(STANDARD_PARALLELS),
    "latitude_of_origin": ORIGIN_LAT,
    "central_meridian": CENTRAL_MERIDIAN,
    "radius_km": R_KM,
}


def _doc(map_id, kind, subject, frame, canvas, marks, detail) -> dict:
    return {
        "id": map_id,
        "kind": kind,
        "subject": subject,
        "canvas": {"width": canvas[0], "height": canvas[1]},
        "projection": PROJECTION,
        "extent": frame_degrees(frame),
        "land": land_paths(frame, canvas, detail["tolerance"], detail["min_ring"]),
        "marks": marks,
        "as_of": max((m["as_of"] for m in marks), default=""),
    }


def sector_map(sector: str, projects: list[dict]) -> dict:
    """Europe, and every project in the sector that is on it.

    The frame does not move with the data. A project outside it would be
    dropped silently, so build() checks that none is rather than trusting the
    frame to be generous.
    """
    frame = fit(europe_frame(), SECTOR_CANVAS)
    marks = []
    for row in projects:
        if row["sector"] != sector:
            continue
        for site in _sites(row):
            marks.append(_mark(row, site, "sector", frame, SECTOR_CANVAS))
    marks.sort(key=lambda m: (m["id"], m["site"]))
    doc = _doc(f"sector-{sector.replace('/', '__')}", "sector", sector,
               frame, SECTOR_CANVAS, marks, SECTOR_DETAIL)
    # The coordinates line under an overview states THE EXTENT OF WHAT IS
    # MARKED, not the frame's. `extent` is the frame and is kept in the file for
    # anyone checking the projection, but it is not a line to print: a conic's
    # rectangular crop fans out at its corners, so cement's frame truthfully
    # reaches 36 W, where there is nothing but Atlantic and no cement plant.
    doc["coordinates"] = [{
        "site": f"{len(marks)} sites",
        "south": min(m["lat"] for m in marks), "north": max(m["lat"] for m in marks),
        "west": min(m["lon"] for m in marks), "east": max(m["lon"] for m in marks),
        "as_of": doc["as_of"],
    }] if marks else []
    return doc


def project_map(subject: dict, projects: list[dict]) -> dict:
    """A regional crop around one project, grown in the brief's order.

    THE FRAME IS FIXED BY THE SUBJECT AND ITS DEPENDENCIES, and by nothing
    else. Those are drawn whatever it costs -- a store four hundred kilometres
    offshore is the fact the picture is for. Neighbours are then drawn where
    they FALL INSIDE that frame, technology before sector, and they never move
    it.

    THE OTHER READING WAS BUILT AND REJECTED. Letting neighbours grow the frame,
    nearest first, up to a cap gave Brevik a crop from Scotland to Estonia in
    order to reach Gotland: one small mark, two grey ones and a great deal of
    empty North Sea. The tighter rule says something instead -- this works, the
    store its tonne reaches, and the coast between them -- and where a crop is
    nearly empty that is a fact about the plant's isolation rather than a
    failure of the frame. Cement runs from Gotland to Attica; the picture that
    holds all of it is the sector overview, and it already exists.
    """
    index = {p["id"]: p for p in projects}
    relation = relations_for(subject, projects)

    core = list(_sites(subject))
    for pid, rel in relation.items():
        if rel == "dependency" and pid in index:
            core += _sites(index[pid])
    frame = _pad(bounds(core))

    cx, cy = (frame[0] + frame[2]) / 2, (frame[1] + frame[3]) / 2
    span_x = max(frame[2] - frame[0], MIN_SPAN_KM)
    span_y = max(frame[3] - frame[1], MIN_SPAN_KM * PROJECT_CANVAS[1] / PROJECT_CANVAS[0])
    frame = fit((cx - span_x / 2, cy - span_y / 2, cx + span_x / 2, cy + span_y / 2),
                PROJECT_CANVAS)

    marks = []
    for row in projects:
        rel = relation.get(row["id"])
        if rel is None:
            continue
        for site in _sites(row):
            if rel in ("subject", "dependency") or inside(frame, site):
                marks.append(_mark(row, site, rel, frame, PROJECT_CANVAS))
    marks.sort(key=lambda m: (RELATIONS.index(m["relation"]), m["id"], m["site"]))

    doc = _doc(f"project-{subject['id']}", "project", subject["id"],
               frame, PROJECT_CANVAS, marks, PROJECT_DETAIL)
    # The coordinates line under a project crop states THE PROJECT'S position,
    # not the frame's. A reader looking at a plant wants the plant's numbers,
    # and a two-site project gets both lines.
    doc["coordinates"] = [
        {"site": s["site"], "lat": s["lat"], "lon": s["lon"], "as_of": s["retrieved_date"]}
        for s in _sites(subject)
    ]
    return doc


def build() -> list[dict]:
    projects = sm.load("project")
    docs = [sector_map(s, projects) for s in sm.mapped_sectors()]
    for row in projects:
        docs.append(project_map(row, projects))
    return docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    docs = build()
    written = set()
    failed = False

    for doc in docs:
        # A sector overview whose frame does not hold one of its own projects
        # would drop it without saying so, which is the failure this whole layer
        # exists to make impossible.
        if doc["kind"] == "sector":
            w, h = doc["canvas"]["width"], doc["canvas"]["height"]
            for mark in doc["marks"]:
                if not (0 <= mark["x"] <= w and 0 <= mark["y"] <= h):
                    print(f"build_maps: {mark['id']} ({mark['site']}) falls outside the "
                          f"Europe frame — widen EUROPE_DEGREES rather than letting a "
                          f"project vanish from its own sector's overview", file=sys.stderr)
                    failed = True
        path = OUT_DIR / f"{doc['id']}.json"
        written.add(path.name)
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"build_maps: {path} is stale or missing — rebuild it", file=sys.stderr)
                failed = True
        else:
            path.write_text(text, encoding="utf-8")

    stale = {p.name for p in OUT_DIR.glob("*.json")} - written
    for name in sorted(stale):
        if args.check:
            print(f"build_maps: {name} is no longer built and is still on disk",
                  file=sys.stderr)
            failed = True
        else:
            (OUT_DIR / name).unlink()

    if failed:
        return 1
    verb = "--check," if args.check else "wrote"
    sectors = sum(1 for d in docs if d["kind"] == "sector")
    print(f"build_maps: {verb} {len(docs)} frame(s) — {sectors} sector, "
          f"{len(docs) - sectors} project, "
          f"{sum(len(d['land']) for d in docs)} stroke(s), "
          f"{sum(len(d['marks']) for d in docs)} mark(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

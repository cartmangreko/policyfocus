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

# THE MARK'S GEOMETRY LIVES HERE AND IS WRITTEN INTO EVERY FILE, because the
# label layout has to know how much room a mark takes and the component has to
# draw one the same size. Held in one place and shipped, rather than written
# twice: the day a mark grows, a copy in the stylesheet or the component would
# leave every label placed against the old radius and nothing would say so.
MARK_R = 4.6
STORE_SCALE = 1.25        # a store's triangle, against a works' dot
RING_SCALE = 3.4          # the ring that says which mark the page is about

MARK_GEOMETRY = {"r": MARK_R, "store_scale": STORE_SCALE, "ring_scale": RING_SCALE}


# What a mark's presence in the picture is owed to, most specific first. The
# brief's order, and it decides emphasis, not the frame: see the module
# docstring.
RELATIONS = ("subject", "dependency", "technology", "sector")


def _sites(project: dict) -> list[dict]:
    return project.get("location") or []


def name_line(row: dict, site: dict) -> str:
    """What the label on the paper calls this mark.

    A ONE-SITE PROJECT IS ITS NAME. A MULTI-SITE PROJECT IS ITS NAME AND WHICH
    SITE THIS IS, because the alternative is two marks in the same picture
    carrying identical labels: the ArcelorMittal row is one project standing on
    Bremen and Eisenhüttenstadt, and a reader seeing the same words twice reads a
    rendering fault rather than a two-site project. The site is appended only
    where it distinguishes something -- a suffix on every label would be noise
    on the eighteen projects that have one site.

    The tooltip is unaffected: it names the site in its own clause already, and
    `label` is left alone for it.
    """
    if len(_sites(row)) < 2:
        return row["name"]
    return f"{row['name']} — {site['site']}"


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
        "country": row["country"],
        "role": row.get("role", "plant"),
        "relation": relation,
        "status": row["status"],
        "label": row["name"],
        "name_line": name_line(row, site),
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
# Labels
# ---------------------------------------------------------------------------
#
# EVERY MARK CARRIES ITS NAME ON THE PAPER, on both frames, and a tooltip is not
# a label: it is reachable only by a reader who already has a pointer and
# already suspects there is something to point at. A picture that has to be
# hovered to be read cannot be read on a phone, in print, or in the screenshot
# somebody puts in a slide, and those are three of the four ways this one will
# be looked at.
#
# SO THE PLACEMENT IS HERE, with the rest of the geometry. The component draws
# what it is given and decides nothing, which is the rule the coastlines and the
# marks already work under. Text placement is the part of a picture most likely
# to come out differently on two machines, so it is the last part that should be
# left to one.
#
# TWO LAYOUTS ARE COMPUTED, NOT ONE, and this is the only place in this file
# that admits a viewport exists. The canvas is 760 units wide and scales to fit,
# so a label's size in UNITS is fixed while its size in PIXELS is not: 11 units
# is 11px on the 760px canvas a desktop gets and 5.6px on the 390px one a
# 430-wide phone has room for, which is not reading, it is a smudge. Holding the
# label legible at 430 means roughly doubling it in canvas units, and a label at
# twice the size collides far more often -- so the narrow frame genuinely needs
# its own placements and, in a crowd, its own shorter wording. A single layout
# would be either unreadable on a phone or absurd on a desk.

# The type size in canvas units per breakpoint, and the canvas width in pixels
# each is sized against: 760 is the max-width the stylesheet caps the figure at,
# and 390 is a 430-wide viewport less the 20px gutter the stylesheet drops to
# below 680. Both land the name at about eleven pixels, which is the size the
# coordinate line under the picture already sets and is read at.
BREAKPOINTS = {
    "wide": {"canvas_px": 760.0, "size": 11.0},
    "narrow": {"canvas_px": 390.0, "size": 21.0},
}

COMPANY_RATIO = 0.86      # the company line, against the name line
LINE_HEIGHT = 1.2         # multiples of each line's own size

# How far a label sits from its mark, in multiples of the ordinary gap. The
# first step is the ordinary position and draws no leader; a label pushed past
# it is joined to its mark by a hairline, because an offset label with nothing
# connecting it is a caption whose owner the reader has to guess.
LEAD_STEPS = (1.0, 2.3, 3.9, 6.0, 8.6)

# The longest a line may run before it is wrapped, as a fraction of the canvas
# width. Past this a label stops being a tag on a mark and becomes a banner
# across the picture.
MAX_LINE_FRACTION = 0.30

# Line budgets. The name gets three because a multi-site mark carries its site
# too -- "ArcelorMittal Bremen and Eisenhüttenstadt conversion — Bremen
# steelworks" is four times the width of the canvas at the narrow size and has
# to be allowed to stack rather than be crammed onto one overflowing line.
MAX_NAME_LINES = 3
MAX_COMPANY_LINES = 2

BOX_PAD = 0.30            # between two label boxes, in multiples of type size
EDGE_MARGIN = 0.35        # between a label box and the frame edge

# Advance widths as a fraction of the type size, by character class. A true font
# metric would need a font file and a parser for it -- a dependency and a build
# input, for the sake of positioning nineteen names. These are the classes a
# humanist sans actually differs across, taken off the stack the stylesheet asks
# for and rounded up. _WIDTH_SAFETY absorbs the error and errs WIDE on purpose:
# a box measured too big loses a placement that would have fitted, which costs a
# leader line, and a box measured too small puts one word on top of another,
# which costs the reader the label.
_WIDTH_SAFETY = 1.06
_NARROW_CHARS = set("ijlt.,;:'!|()[]{}/\\-")
_WIDE_CHARS = set("mw")
_CAP_WIDE = set("MW")


def text_width(text: str, size: float) -> float:
    total = 0.0
    for ch in text:
        if ch == " ":
            total += 0.28
        elif ch in _NARROW_CHARS:
            total += 0.30
        elif ch in _WIDE_CHARS:
            total += 0.84
        elif ch in _CAP_WIDE:
            total += 0.89
        elif ch.isdigit():
            total += 0.56
        elif ch.isupper():
            total += 0.67
        else:
            total += 0.53
    return total * size * _WIDTH_SAFETY


def wrap(text: str, size: float, limit: float, max_lines: int) -> list[str]:
    """Greedy wrap on spaces, never past max_lines. A word too long to fit on
    its own is left long rather than broken: a hyphen this file invented would
    be read as part of a company's name."""
    words = text.split()
    if not words:
        return []
    lines = [words[0]]
    for word in words[1:]:
        trial = f"{lines[-1]} {word}"
        if len(lines) >= max_lines or text_width(trial, size) <= limit:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


# Where a label is tried, in order. East and west first: a label beside a mark
# reads as belonging to it more immediately than one above or below, and every
# frame here has more room across than down.
DIRECTIONS = (
    ("e", 1.0, 0.0),
    ("w", -1.0, 0.0),
    ("ne", 0.72, -0.72),
    ("se", 0.72, 0.72),
    ("nw", -0.72, -0.72),
    ("sw", -0.72, 0.72),
    ("n", 0.0, -1.0),
    ("s", 0.0, 1.0),
)


def mark_clearance(mark: dict) -> float:
    """How much room a mark needs around it before a label may sit there. The
    subject wears a ring of MARK_R * 3.4 and a label crossing that ring reads as
    striking it through, so the subject asks for more than the rest."""
    if mark["relation"] == "subject":
        return MARK_R * 3.4 + 2.0
    return MARK_R * 1.7


def _lines_for(label: str, sub, size: float, limit: float) -> list[dict]:
    """The label's lines. THE NAME LINE IS NEVER THE THING THAT DROPS: on a
    multi-site mark it carries the site, which is the whole of what tells that
    mark from its twin, so the shortening rung takes the company and leaves this
    alone. The company is in the tooltip either way."""
    out = [{"text": t, "size": size, "role": "name"}
           for t in wrap(label, size, limit, MAX_NAME_LINES)]
    if sub:
        company = size * COMPANY_RATIO
        out += [{"text": t, "size": company, "role": "company"}
                for t in wrap(sub, company, limit, MAX_COMPANY_LINES)]
    return out


def _box_size(lines: list[dict]) -> tuple[float, float]:
    w = max((text_width(l["text"], l["size"]) for l in lines), default=0.0)
    h = sum(LINE_HEIGHT * l["size"] for l in lines)
    return w, h


def _place(mx, my, ux, uy, dist, w, h) -> tuple[float, float, float, float]:
    ax, ay = mx + ux * dist, my + uy * dist
    if ux > 0.1:
        x0 = ax
    elif ux < -0.1:
        x0 = ax - w
    else:
        x0 = ax - w / 2
    if uy > 0.1:
        y0 = ay
    elif uy < -0.1:
        y0 = ay - h
    else:
        y0 = ay - h / 2
    return x0, y0, x0 + w, y0 + h


def _overlap(a, b) -> float:
    dx = min(a[2], b[2]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[1], b[1])
    return dx * dy if dx > 0 and dy > 0 else 0.0


def _cost(box, placed, marks, subject, canvas, size) -> float:
    """Nought is a clean placement. Anything else is how much this label is in
    the way, in square units, so that the least-bad candidate can be ranked when
    no clean one exists.

    THE MARK BEING LABELLED IS EXEMPT from the clearance test -- the label is
    meant to be near it, that is the whole point -- and every other mark is not.
    """
    pad = BOX_PAD * size
    padded = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
    cost = sum(_overlap(padded, other) for other in placed)

    for m in marks:
        if m is subject:
            continue
        c = mark_clearance(m)
        cost += _overlap(box, (m["x"] - c, m["y"] - c, m["x"] + c, m["y"] + c))

    margin = EDGE_MARGIN * size
    w, h = canvas
    out_x = max(0.0, margin - box[0]) + max(0.0, box[2] - (w - margin))
    out_y = max(0.0, margin - box[1]) + max(0.0, box[3] - (h - margin))
    # Leaving the frame is weighted heavily rather than forbidden outright: a
    # label half off the paper is worse than one touching a coastline, and the
    # search still has to be able to rank two bad options against each other.
    cost += (out_x * (box[3] - box[1]) + out_y * (box[2] - box[0])) * 4.0
    return cost


def _render(lines, box, ux) -> dict:
    x0, y0, x1, _ = box
    if ux > 0.1:
        anchor, x = "start", x0
    elif ux < -0.1:
        anchor, x = "end", x1
    else:
        anchor, x = "middle", (x0 + x1) / 2
    out, y = [], y0
    for line in lines:
        out.append({"text": line["text"], "role": line["role"],
                    "size": _round(line["size"]),
                    "y": _round(y + line["size"] * 0.78)})
        y += LINE_HEIGHT * line["size"]
    return {"x": _round(x), "anchor": anchor, "lines": out}


def _leader(mx, my, box) -> list:
    """From the mark's edge to the nearest point on the label's box. Drawn only
    where a label had to be pushed out, so a hairline always means one thing:
    this word belongs to that mark and not to the nearer one."""
    tx = min(max(mx, box[0]), box[2])
    ty = min(max(my, box[1]), box[3])
    dx, dy = tx - mx, ty - my
    dist = math.hypot(dx, dy)
    start = MARK_R + 1.2
    if dist <= start:
        return []
    return [_round(mx + dx / dist * start), _round(my + dy / dist * start),
            _round(tx), _round(ty)]


def _search(mark, lines, marks, placed, canvas, size):
    """The best position for one wording of one label, and its cost."""
    w, h = _box_size(lines)
    base = mark_clearance(mark) + size * 0.55
    best = None
    for step_i, step in enumerate(LEAD_STEPS):
        for _name, ux, uy in DIRECTIONS:
            box = _place(mark["x"], mark["y"], ux, uy, base * step, w, h)
            cost = _cost(box, placed, marks, mark, canvas, size)
            if best is None or cost < best["cost"]:
                best = {"cost": cost, "box": box, "ux": ux,
                        "lines": lines, "step": step_i}
            if cost == 0.0:
                return best
    return best


def label_marks(marks: list[dict], canvas: tuple[float, float]) -> dict[str, list]:
    """Give every mark a permanent label under each breakpoint, in place.

    Greedy, in the order the marks already sort in, which is deterministic and
    is the whole reason this is reviewable in a diff.

    THE LADDER IS THE RULING'S. A clean placement beside the mark; then the same
    pushed out, with a leader drawn to it; then THE NAME ALONE pushed out, the
    company falling back to the tooltip that already carries it; and if nothing
    at all comes out clean, the least-bad position, KEPT AND REPORTED rather than
    dropped. A picture that silently omits whichever label it found hardest to
    place is a picture that lies worst exactly where it is most crowded, and the
    reader has no way of knowing a name was ever there.
    """
    boxes: dict[str, list] = {}
    for key, spec in BREAKPOINTS.items():
        size = spec["size"]
        limit = canvas[0] * MAX_LINE_FRACTION
        placed: list[tuple] = []
        for mark in marks:
            full = _search(mark, _lines_for(mark["name_line"], mark["sub"], size, limit),
                           marks, placed, canvas, size)
            if full["cost"] == 0.0:
                best, shortened = full, False
            else:
                short = _search(mark, _lines_for(mark["name_line"], None, size, limit),
                                marks, placed, canvas, size)
                if short["cost"] < full["cost"]:
                    best, shortened = short, True
                else:
                    best, shortened = full, False

            out = _render(best["lines"], best["box"], best["ux"])
            if best["step"] > 0:
                leader = _leader(mark["x"], mark["y"], best["box"])
                if leader:
                    out["leader"] = leader
            if shortened:
                out["shortened"] = True
            if best["cost"] > 0.0:
                out["crowded"] = True
            mark.setdefault("labels", {})[key] = out
            placed.append(best["box"])
        boxes[key] = placed
    return boxes


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------
#
# THE GROUND IS NAMED. A reader who does not already know the shape of Europe
# cannot tell Denmark from Schleswig-Holstein, and the picture was asking them
# to. The names are the faintest layer on the paper: they sit under the site
# labels in every sense, and where the two want the same space the country loses
# and is dropped rather than moved on top of a name that matters more.
#
# WHICH COUNTRIES ARE NAMED DIFFERS BY FRAME, and it is the same principle in
# two settings. A CROP names every country in view, because the reader is being
# shown a region and needs to know which one. AN OVERVIEW names only the
# countries that contain a drawn site, because Europe with forty-five names on
# it is an atlas, and the question the overview answers is where this sector is
# -- a name over a country with nothing in it answers a question nobody asked and
# crowds out one that was.
#
# INTERNAL BORDERS WERE ALREADY THERE. The ruling made the border layer
# conditional on the base geometry being coastline-only, and it is not: every
# country's ring carries its land boundaries as well as its coast, and
# land_paths has been drawing both since the first commit -- from both sides, in
# fact. Nothing was added, and the faintest-ink layer the ruling provided for is
# not needed.

# The name's size against the site name's, per breakpoint, and how it is placed.
COUNTRY_RATIO = 0.82

# A grid coarse enough to run and fine enough to find the middle of a country.
# The label point is the cell furthest from anywhere the country is not, which is
# what stops Norway's name landing in the North Sea: a centroid of a concave
# shape is routinely outside the shape, and a country outline is nothing if not
# concave.
COUNTRY_GRID = 26

# How far, in canvas units, a country's label point has to be from the nearest
# edge of the country or of the frame before the country is named at all. Below
# this the name is standing on a sliver of Denmark clipped by the frame, and it
# reads as belonging to whatever is next to it.
COUNTRY_MIN_ROOM = 9.0

# How many candidate middles a country offers the placement, and how far apart
# on the grid they have to be to count as different places.
COUNTRY_CANDIDATES = 4
COUNTRY_SPREAD = 4

# Rings simplified to this, in degrees, before any of the point work. Roughly
# eleven kilometres, which is invisible to the question "where is the middle of
# Poland" and is the difference between this running in seconds and in minutes.
COUNTRY_SIMPLIFY_DEG = 0.1

_RING_CACHE: dict[str, list] = {}


def _coarse_rings(iso: str) -> list:
    """A country's rings, simplified once and kept. Only ever used to answer
    where a name goes -- the drawn coastline is simplified separately, in canvas
    units, at a tolerance chosen for how it looks."""
    if iso not in _RING_CACHE:
        rings = []
        for ring in ne.countries()[iso]:
            thin = simplify(ring, COUNTRY_SIMPLIFY_DEG)
            if len(thin) >= 3:
                rings.append(thin)
        _RING_CACHE[iso] = rings
    return _RING_CACHE[iso]


def _inside(pt, rings) -> bool:
    """Even-odd, over the coarse rings, in degrees. The same parity rule
    natural_earth.contains uses and for the same reason: a hole is a ring."""
    x, y = pt
    hit = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]
            x2, y2 = ring[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    hit = not hit
    return hit


def _distance_transform(mask, w, h):
    """Chamfer, two passes, on the grid rather than on the geometry. Gives every
    inside cell its distance to the nearest outside cell in cell units, which is
    all that is needed to pick the roomiest one and is far cheaper than asking
    the same question of a coastline."""
    big = float(w + h)
    d = [[0.0 if not mask[j][i] else big for i in range(w)] for j in range(h)]
    for j in range(h):
        for i in range(w):
            if not mask[j][i]:
                continue
            best = d[j][i]
            if j > 0:
                best = min(best, d[j - 1][i] + 1.0)
                if i > 0:
                    best = min(best, d[j - 1][i - 1] + 1.414)
                if i + 1 < w:
                    best = min(best, d[j - 1][i + 1] + 1.414)
            if i > 0:
                best = min(best, d[j][i - 1] + 1.0)
            d[j][i] = best
    for j in range(h - 1, -1, -1):
        for i in range(w - 1, -1, -1):
            if not mask[j][i]:
                continue
            best = d[j][i]
            if j + 1 < h:
                best = min(best, d[j + 1][i] + 1.0)
                if i > 0:
                    best = min(best, d[j + 1][i - 1] + 1.414)
                if i + 1 < w:
                    best = min(best, d[j + 1][i + 1] + 1.414)
            if i + 1 < w:
                best = min(best, d[j][i + 1] + 1.0)
            d[j][i] = best
    return d


def country_points(iso: str, frame, canvas) -> list:
    """Where this country's name could go, in canvas units, roomiest first, or
    empty if the frame does not show enough of it to name.

    The frame's own edge counts as outside, so a country clipped to a corner is
    measured on what is VISIBLE of it rather than on what it is -- otherwise
    Sweden's name lands off the top of a crop that shows its southern tip.
    """
    rings = _coarse_rings(iso)
    if not rings:
        return []
    x0, y0, x1, y1 = frame
    scale = canvas[0] / (x1 - x0)

    lons, lats = [], []
    steps = 12
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        y = y0 + (y1 - y0) * i / steps
        for corner in ((x, y0), (x, y1), (x0, y), (x1, y)):
            lon, lat = unproject(*corner)
            lons.append(lon)
            lats.append(lat)
    west, east = min(lons), max(lons)
    south, north = min(lats), max(lats)

    rw = [p[0] for ring in rings for p in ring]
    rh = [p[1] for ring in rings for p in ring]
    west, east = max(west, min(rw)), min(east, max(rw))
    south, north = max(south, min(rh)), min(north, max(rh))
    if east <= west or north <= south:
        return []

    w = h = COUNTRY_GRID
    mask = [[False] * w for _ in range(h)]
    pts = [[None] * w for _ in range(h)]
    for j in range(h):
        lat = south + (north - south) * (j + 0.5) / h
        for i in range(w):
            lon = west + (east - west) * (i + 0.5) / w
            px, py = project(lon, lat)
            if not (x0 <= px <= x1 and y0 <= py <= y1):
                continue
            if _inside((lon, lat), rings):
                mask[j][i] = True
                pts[j][i] = ((px - x0) * scale, (py - y0) * scale)

    d = _distance_transform(mask, w, h)
    # One grid cell, in canvas units, so room measured on the grid can be
    # compared against a threshold written in the units everything else uses.
    cell = ((east - west) / w) * math.cos(math.radians((north + south) / 2)) * 111.32 * scale
    roomy = sorted(
        ((d[j][i], i, j) for j in range(h) for i in range(w)
         if mask[j][i] and d[j][i] * cell >= COUNTRY_MIN_ROOM),
        key=lambda t: (-t[0], t[2], t[1]))

    # MORE THAN ONE CANDIDATE, KEPT APART. The roomiest cell is the best place
    # for a name and is not the only one: Germany's is in the middle, which on a
    # crop of the Ruhr is exactly where the site labels are, and a country whose
    # single candidate is taken loses its name to a neighbour's works. Offering
    # the placement a few genuinely different middles recovers those without
    # letting a name wander out of its own country, which is what a large nudge
    # would do. Kept COUNTRY_SPREAD cells apart so the alternatives are places
    # rather than neighbours of the first one.
    out = []
    for dist, i, j in roomy:
        if any(max(abs(i - pi), abs(j - pj)) < COUNTRY_SPREAD for _, pi, pj in out):
            continue
        out.append((pts[j][i], i, j))
        if len(out) >= COUNTRY_CANDIDATES:
            break
    return [pt for pt, _i, _j in out]


def visible_countries(frame, canvas) -> list[str]:
    """Every country the frame shows enough of to name, in ISO order so two
    builds of one frame agree."""
    return [iso for iso in sorted(ne.countries())
            if country_points(iso, frame, canvas)]

# Where a country's name may be nudged to, and how far. SMALL, and small on
# purpose: a country label that has walked any distance is no longer over its
# country, and a name in the wrong country is worse than no name at all. Past
# these the name is dropped instead.
COUNTRY_NUDGES = (0.0, 0.7, 1.4, 2.2)


def country_names() -> dict[str, str]:
    doc = json.loads((sm.ROOT / "data" / "prose.json").read_text(encoding="utf-8"))
    return doc["country_names"]["names"]


def label_countries(isos, points, marks, canvas, placed) -> list[dict]:
    """Name the ground, under the site labels in every sense.

    A COUNTRY LABEL NEVER MOVES A SITE LABEL. The site labels are placed first
    and handed here as fixed boxes; this pass places around them, and where it
    cannot it DROPS THE NAME. That is the opposite of the rule for a site label,
    which is never dropped, and the asymmetry is the point: a missing site is a
    fact the reader cannot recover, and a missing country is a shape most readers
    know and all of them will be able to hover once the hit layer lands.
    """
    names = country_names()
    missing = [iso for iso in isos if iso not in names]
    if missing:
        raise SystemExit(
            f"build_maps: no name for {', '.join(missing)} — add them to "
            f"country_names in data/prose.json rather than letting a two-letter "
            f"code onto the paper")

    out = []
    for iso in isos:
        entry = {"iso": iso, "text": names[iso], "labels": {}}
        for key, spec in BREAKPOINTS.items():
            candidates = points[key].get(iso) or []
            if not candidates:
                continue
            size = spec["size"] * COUNTRY_RATIO
            limit = canvas[0] * MAX_LINE_FRACTION
            lines = [{"text": t, "size": size, "role": "country"}
                     for t in wrap(names[iso], size, limit, 2)]
            w, h = _box_size(lines)
            best = None
            for mx, my in candidates:
                for step in COUNTRY_NUDGES:
                    # The label point itself first, then the same ring of
                    # directions the site labels use, at a fraction of the reach.
                    tries = (("c", 0.0, 0.0),) if step == 0.0 else DIRECTIONS
                    for _n, ux, uy in tries:
                        box = _place(mx, my, ux, uy, size * step, w, h)
                        cost = _cost(box, placed[key], marks, None, canvas, size)
                        if best is None or cost < best["cost"]:
                            best = {"cost": cost, "box": box, "ux": ux, "lines": lines}
                        if cost == 0.0:
                            break
                    if best["cost"] == 0.0:
                        break
                if best["cost"] == 0.0:
                    break
            # Dropped rather than drawn badly: see the docstring.
            if best["cost"] > 0.0:
                continue
            entry["labels"][key] = _render(best["lines"], best["box"], best["ux"])
            placed[key].append(best["box"])
        if entry["labels"]:
            out.append(entry)
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


def _doc(map_id, kind, subject, frame, canvas, marks, detail, isos) -> dict:
    # Labels are laid out here, once the marks are final and before anything is
    # written, so that no consumer of this file ever sees a mark without one.
    #
    # ORDER MATTERS AND IS THE RULING. The site labels are placed first and
    # against nothing but each other; the country names are placed afterwards,
    # against the boxes the site labels have already taken. A country name can
    # therefore be nudged or dropped by a site name and never the other way
    # round, which is what "subordinate" has to mean once two layers want the
    # same square of paper.
    placed = label_marks(marks, canvas)
    candidates = {iso: country_points(iso, frame, canvas) for iso in isos}
    points = {key: candidates for key in BREAKPOINTS}
    countries = label_countries(isos, points, marks, canvas, placed)
    return {
        "id": map_id,
        "kind": kind,
        "subject": subject,
        "canvas": {"width": canvas[0], "height": canvas[1]},
        "mark_geometry": MARK_GEOMETRY,
        "projection": PROJECTION,
        "extent": frame_degrees(frame),
        "land": land_paths(frame, canvas, detail["tolerance"], detail["min_ring"]),
        "marks": marks,
        "countries": countries,
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
    # AN OVERVIEW NAMES ONLY WHERE IT HAS SOMETHING. Europe carries forty-five
    # countries and naming all of them makes an atlas out of a picture whose one
    # question is where this sector is; a name over a country with no site in it
    # answers a question nobody asked and takes the room from one that was.
    isos = sorted({m["country"] for m in marks})
    doc = _doc(f"sector-{sector.replace('/', '__')}", "sector", sector,
               frame, SECTOR_CANVAS, marks, SECTOR_DETAIL, isos)
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

    # A CROP NAMES EVERYTHING IN VIEW. The reader has been handed a region
    # without being told which one, and at 800 km across the outlines are not
    # the ones anybody recognises from memory.
    doc = _doc(f"project-{subject['id']}", "project", subject["id"],
               frame, PROJECT_CANVAS, marks, PROJECT_DETAIL,
               visible_countries(frame, PROJECT_CANVAS))
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

    # A label that could not be placed cleanly is REPORTED AND KEPT, never
    # dropped -- see label_marks. It is not a build failure: the picture is still
    # honest, every name is still on it, and the fix is a judgement about the
    # frame or the wording that nobody can make from a non-zero exit code.
    crowded = [f"{doc['id']} {bp}: {mark['id']} ({mark['site']})"
               for doc in docs for mark in doc["marks"]
               for bp, label in mark["labels"].items() if label.get("crowded")]
    for line in crowded:
        print(f"build_maps: label overlaps something at {line}", file=sys.stderr)

    # Country names that lost their square of paper to a site label. Counted and
    # printed rather than passed over: it is the one place the geography drops
    # something a reader might have wanted, and the number is how anybody notices
    # a frame has become too crowded to name its own ground.
    asked = sum(len(BREAKPOINTS) * len(d["countries"]) for d in docs)
    given = sum(len(c["labels"]) for d in docs for c in d["countries"])
    for doc in docs:
        for c in doc["countries"]:
            for bp in BREAKPOINTS:
                if bp not in c["labels"]:
                    print(f"build_maps: no room for {c['text']} on {doc['id']} "
                          f"({bp}) — a site label has it", file=sys.stderr)

    if failed:
        return 1
    verb = "--check," if args.check else "wrote"
    sectors = sum(1 for d in docs if d["kind"] == "sector")
    print(f"build_maps: {verb} {len(docs)} frame(s) — {sectors} sector, "
          f"{len(docs) - sectors} project, "
          f"{sum(len(d['land']) for d in docs)} stroke(s), "
          f"{sum(len(d['marks']) for d in docs)} mark(s), "
          f"{sum(1 for d in docs for m in d['marks'] for l in m['labels'].values() if l.get('shortened'))}"
          f" label(s) shortened, {len(crowded)} crowded; "
          f"{asked} country name slot(s), {asked - given} dropped to a site label")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

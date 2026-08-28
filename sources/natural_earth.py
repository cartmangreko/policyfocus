"""
Reading the committed Natural Earth basemap, with the standard library.

    import natural_earth as ne
    lands = ne.countries()               # {"NO": [ring, ring, ...], ...}
    ne.contains((9.6912, 59.0644), lands["NO"])
    ne.distance_km((28.1932, 43.0446), lands["BG"])

WHY THIS EXISTS RATHER THAN A DEPENDENCY. `sources/requirements.txt` holds four
packages and every one of them is load-bearing for fetching or triage. A
geometry stack would be the first dependency added for a check rather than for
an ingest, it would be the largest thing in the file by an order of magnitude,
and what is actually needed here is a shapefile reader and a point-in-polygon
test -- both of which are short, stable, and have no opinions. Anything that
needs projections, buffers or overlays is not this module's job and should not
be smuggled into it.

WHAT IT READS. data/geo/ne_10m_admin_0_countries.zip, exactly as fetched, gated
by sources/check_geo_source.py. The shapefile is read straight out of the zip:
unpacking it to disk would create a second copy that could drift from the one
whose checksum is recorded.

WHAT IT DOES NOT DO. It does not reproject. Natural Earth ships EPSG:4326 and
everything here works in degrees, converting to kilometres only at the last step
and only with a local equirectangular scaling, which is accurate to well under a
percent at the distances this is used for and wrong near the poles. If a caller
ever needs a real projection, it belongs in the renderer, not here.
"""

from __future__ import annotations

import math
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "data" / "geo" / "ne_10m_admin_0_countries.zip"
STEM = "ne_10m_admin_0_countries"

# Mean Earth radius in kilometres per degree of latitude. Longitude degrees
# shrink by cos(latitude), which is the only correction applied.
KM_PER_DEGREE = 111.32

Point = tuple[float, float]     # (lon, lat), in that order, as the file stores it
Ring = list[Point]

_CACHE: dict[str, list[Ring]] | None = None


# ---------------------------------------------------------------------------
# The two file formats, read directly
# ---------------------------------------------------------------------------

def _dbf_records(raw: bytes) -> list[dict[str, str]]:
    """The attribute table. Fixed-width fields, latin-1, padded with spaces or
    with NULs depending on who wrote the file -- both are stripped, because a
    country code that comes back as "NO\\x00" matches nothing and fails silently
    by never being looked up."""
    count, header_len, record_len = struct.unpack("<I H H", raw[4:12])
    fields: list[tuple[str, int]] = []
    off = 32
    while raw[off] != 0x0D:                       # 0x0D terminates the field list
        name = raw[off:off + 11].split(b"\0")[0].decode("latin-1")
        fields.append((name, raw[off + 16]))
        off += 32
    out = []
    for i in range(count):
        row, p = {}, header_len + i * record_len + 1   # +1 skips the deletion flag
        for name, width in fields:
            row[name] = raw[p:p + width].decode("latin-1").strip().strip("\0").strip()
            p += width
        out.append(row)
    return out


def _shp_polygons(raw: bytes) -> list[list[Ring]]:
    """The geometry. Only shape type 5, polygon, is read: Admin 0 Countries holds
    nothing else, and a file that suddenly did would be a different file than the
    one whose checksum is recorded."""
    shapes: list[list[Ring]] = []
    p = 100                                        # the file header
    while p < len(raw):
        _number, content_len = struct.unpack(">II", raw[p:p + 8])
        p += 8
        body = raw[p:p + content_len * 2]
        p += content_len * 2
        if struct.unpack("<I", body[0:4])[0] != 5:
            shapes.append([])
            continue
        nparts, npoints = struct.unpack("<II", body[36:44])
        parts = struct.unpack(f"<{nparts}I", body[44:44 + 4 * nparts])
        start = 44 + 4 * nparts
        flat = struct.unpack(f"<{2 * npoints}d", body[start:start + 16 * npoints])
        rings: list[Ring] = []
        for i, first in enumerate(parts):
            last = parts[i + 1] if i + 1 < nparts else npoints
            rings.append([(flat[2 * j], flat[2 * j + 1]) for j in range(first, last)])
        shapes.append(rings)
    return shapes


def countries() -> dict[str, list[Ring]]:
    """{ISO 3166-1 alpha-2: every ring of that country's land}, cached.

    The rings of all a country's parts are pooled into one list. That is enough
    for containment and for distance and would be wrong for anything that cared
    which island a point is on -- which nothing here does.

    ISO_A2_EH is preferred over ISO_A2 because Natural Earth sets the latter to
    "-99" for several territories it declines to code; EH carries the code the
    de-facto administration uses. WB_A2 is the last fallback.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    with zipfile.ZipFile(ARCHIVE) as z:
        records = _dbf_records(z.read(f"{STEM}.dbf"))
        shapes = _shp_polygons(z.read(f"{STEM}.shp"))
    out: dict[str, list[Ring]] = {}
    for row, rings in zip(records, shapes):
        for key in ("ISO_A2_EH", "ISO_A2", "WB_A2"):
            code = row.get(key)
            if code and code != "-99":
                out.setdefault(code, []).extend(rings)
                break
    _CACHE = out
    return out


# ---------------------------------------------------------------------------
# The two questions anybody asks of it
# ---------------------------------------------------------------------------

def _in_ring(pt: Point, ring: Ring) -> bool:
    """Even-odd ray casting. Holes are handled by the same parity that draws
    them: a point inside an outer ring and inside a hole crosses both and comes
    back out odd-plus-odd, which is even, which is outside."""
    x, y = pt
    hit = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                hit = not hit
    return hit


def contains(pt: Point, rings: list[Ring]) -> bool:
    """Whether the point is on this country's land, at this file's simplification.

    A false answer for a real coastal site is expected and is not a bug: at
    1:10m a quay, a spit and a small island are all things the generalisation
    may have removed. That is why callers work in tolerances rather than in
    yes and no.
    """
    return sum(1 for r in rings if _in_ring(pt, r)) % 2 == 1


def _segment_km(pt: Point, a: Point, b: Point, scale: float) -> float:
    px, py = pt[0] * scale, pt[1]
    ax, ay = a[0] * scale, a[1]
    bx, by = b[0] * scale, b[1]
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        t = 0.0
    else:
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy)) * KM_PER_DEGREE


def distance_km(pt: Point, rings: list[Ring]) -> float:
    """Kilometres from the point to the nearest edge of this country, or 0.0 if
    it is inside.

    To the nearest EDGE, not the nearest vertex. On a generalised coastline two
    vertices can be tens of kilometres apart along a straight run, and measuring
    to vertices would report a point sitting on that coast as far out to sea --
    which, in a gate with a ten-kilometre tolerance, is the difference between a
    rule and a coin toss.
    """
    if contains(pt, rings):
        return 0.0
    scale = math.cos(math.radians(pt[1]))
    best = float("inf")
    for ring in rings:
        for i in range(len(ring)):
            d = _segment_km(pt, ring[i], ring[(i + 1) % len(ring)], scale)
            if d < best:
                best = d
    return best

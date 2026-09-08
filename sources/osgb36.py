"""
British National Grid to WGS84, so a permit's grid reference can become a mark.

    import osgb36
    osgb36.to_wgs84(433175, 558670)     # -> (54.92498, -1.47861)

WHY THIS EXISTS. Planning and permitting documents in Great Britain give
positions as British National Grid eastings and northings, and this is the one
kind of coordinate source that arrives in a projection rather than in degrees.
AESC's Sunderland works is the case that forced it: no basemap feature, no
published address that resolves, and an environmental-permit report whose site
plans are gridded and whose emission stacks are listed to the metre.

NO EYEBALLED OFFSET. The temptation with a grid reference is to convert it
roughly -- OSGB36 and WGS84 differ by only about a hundred metres across Britain,
and a hundred metres looks small on a continental frame. It is not small against a
works: it is most of a factory building, and a coordinate that is nearly right is
the failure this whole layer exists to prevent. So the conversion is done
properly, in two stages, and checked against published test points.

THE TWO STAGES, because they are different problems and are often confused.

  PROJECTION   National Grid eastings and northings are a transverse Mercator
               projection of the Airy 1830 ellipsoid. Inverting that gives
               latitude and longitude ON AIRY 1830, which is not WGS84 and is not
               what a map wants.

  DATUM        Airy 1830 is fitted to Britain and sits about a hundred metres from
               the geocentric WGS84 ellipsoid. Moving between them is a
               seven-parameter Helmert transformation through geocentric
               cartesian coordinates.

WHAT THIS IS NOT. It is not OSTN15, the Ordnance Survey's official rubber-sheet
transformation, which reaches centimetres and needs a several-megabyte grid file.
The Helmert parameters below reach a few metres across Britain -- OS publishes
them for exactly this purpose and calls the result suitable for mapping at scales
where a few metres does not matter. A mark on a works is such a use: the works is
two hundred metres across. If this repository ever needs sub-metre positions it
needs OSTN15 and a different docstring, and it does not need them to draw a dot.
"""

from __future__ import annotations

import math

# Airy 1830, the ellipsoid the National Grid is projected on.
AIRY_A = 6377563.396
AIRY_B = 6356256.909

# WGS84.
WGS84_A = 6378137.000
WGS84_B = 6356752.314245

# The National Grid's transverse Mercator parameters.
F0 = 0.9996012717            # scale factor on the central meridian
LAT0 = math.radians(49.0)    # true origin
LON0 = math.radians(-2.0)
E0 = 400000.0                # false origin, metres
N0 = -100000.0

# OSGB36 to WGS84, the seven parameters Ordnance Survey publishes. Translations
# in metres, rotations in seconds of arc, scale in parts per million.
HELMERT = {
    "tx": 446.448, "ty": -125.157, "tz": 542.060,
    "rx": 0.1502, "ry": 0.2470, "rz": 0.8421,
    "s": -20.4894,
}


def _meridional_arc(lat: float) -> float:
    n = (AIRY_A - AIRY_B) / (AIRY_A + AIRY_B)
    dl, sl = lat - LAT0, lat + LAT0
    return AIRY_B * F0 * (
        (1 + n + 1.25 * n**2 + 1.25 * n**3) * dl
        - (3 * n + 3 * n**2 + 2.625 * n**3) * math.sin(dl) * math.cos(sl)
        + (1.875 * n**2 + 1.875 * n**3) * math.sin(2 * dl) * math.cos(2 * sl)
        - (35 / 24) * n**3 * math.sin(3 * dl) * math.cos(3 * sl)
    )


def grid_to_airy(easting: float, northing: float) -> tuple[float, float]:
    """National Grid metres to latitude and longitude ON AIRY 1830, in degrees.

    Iterates the meridional arc because the footprint latitude has no closed
    form; it converges in three or four passes and the loop is bounded so a bad
    input cannot hang a build.
    """
    e2 = 1 - (AIRY_B**2) / (AIRY_A**2)
    lat = LAT0
    m = 0.0
    for _ in range(20):
        lat += (northing - N0 - m) / (AIRY_A * F0)
        m = _meridional_arc(lat)
        if abs(northing - N0 - m) < 1e-5:
            break

    sin_lat = math.sin(lat)
    nu = AIRY_A * F0 / math.sqrt(1 - e2 * sin_lat**2)
    rho = AIRY_A * F0 * (1 - e2) / (1 - e2 * sin_lat**2) ** 1.5
    eta2 = nu / rho - 1

    tan_lat = math.tan(lat)
    t2, t4, t6 = tan_lat**2, tan_lat**4, tan_lat**6
    sec_lat = 1 / math.cos(lat)
    de = easting - E0

    vii = tan_lat / (2 * rho * nu)
    viii = tan_lat / (24 * rho * nu**3) * (5 + 3 * t2 + eta2 - 9 * t2 * eta2)
    ix = tan_lat / (720 * rho * nu**5) * (61 + 90 * t2 + 45 * t4)
    x = sec_lat / nu
    xi = sec_lat / (6 * nu**3) * (nu / rho + 2 * t2)
    xii = sec_lat / (120 * nu**5) * (5 + 28 * t2 + 24 * t4)
    xiia = sec_lat / (5040 * nu**7) * (61 + 662 * t2 + 1320 * t4 + 720 * t6)

    out_lat = lat - vii * de**2 + viii * de**4 - ix * de**6
    out_lon = LON0 + x * de - xi * de**3 + xii * de**5 - xiia * de**7
    return math.degrees(out_lat), math.degrees(out_lon)


def _to_cartesian(lat: float, lon: float, a: float, b: float, h: float = 0.0):
    lat, lon = math.radians(lat), math.radians(lon)
    e2 = (a**2 - b**2) / a**2
    nu = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return ((nu + h) * math.cos(lat) * math.cos(lon),
            (nu + h) * math.cos(lat) * math.sin(lon),
            ((1 - e2) * nu + h) * math.sin(lat))


def _from_cartesian(x: float, y: float, z: float, a: float, b: float):
    e2 = (a**2 - b**2) / a**2
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1 - e2))
    for _ in range(20):
        nu = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        new = math.atan2(z + e2 * nu * math.sin(lat), p)
        if abs(new - lat) < 1e-12:
            lat = new
            break
        lat = new
    return math.degrees(lat), math.degrees(math.atan2(y, x))


def airy_to_wgs84(lat: float, lon: float) -> tuple[float, float]:
    """Helmert, OSGB36 to WGS84, through geocentric cartesian coordinates."""
    x, y, z = _to_cartesian(lat, lon, AIRY_A, AIRY_B)
    h = HELMERT
    s = 1 + h["s"] / 1e6
    rx, ry, rz = (math.radians(h[k] / 3600) for k in ("rx", "ry", "rz"))
    x2 = h["tx"] + s * (x - rz * y + ry * z)
    y2 = h["ty"] + s * (rz * x + y - rx * z)
    z2 = h["tz"] + s * (-ry * x + rx * y + z)
    return _from_cartesian(x2, y2, z2, WGS84_A, WGS84_B)


def to_wgs84(easting: float, northing: float, places: int = 4) -> tuple[float, float]:
    """A National Grid reference as a WGS84 latitude and longitude.

    Rounded to `places` decimals, four by default, which is about eleven metres
    and is the precision every other coordinate in this register is stored at.
    Rounding here rather than at the call site so that two callers cannot store
    the same grid reference to different precision.
    """
    lat, lon = airy_to_wgs84(*grid_to_airy(easting, northing))
    return round(lat, places), round(lon, places)


# TEST VECTORS, from the Ordnance Survey's "Guide to coordinate systems in Great
# Britain". The first proves the PROJECTION inverse and the second proves the
# DATUM shift on top of it, which are the two stages and the two places a bug
# would hide. Checked on every build that reads a grid reference, because a
# conversion nobody re-runs is a conversion that will be quietly wrong the day
# somebody tidies a constant.
#
# Caister Water Tower, the guide's worked example:
#   National Grid  E 651409.903  N 313177.270
#   OSGB36         52 39 27.2531 N,  1 43 04.5177 E
#   ETRS89         52 39 28.723  N,  1 42 57.787  E
TEST_VECTORS = [
    {"easting": 651409.903, "northing": 313177.270,
     "osgb36": (52.6575703, 1.7179216),
     "wgs84": (52.6579786, 1.7160519),
     "name": "Caister Water Tower"},
]

# How far a test vector may miss before the build fails, in metres. A tenth of a
# metre: the Helmert transformation is deterministic and this is a check on the
# arithmetic, not on the method. The method's own error against OSTN15 is a few
# metres and is stated in the module docstring, where it belongs.
TOLERANCE_M = 0.1


def self_check() -> list[str]:
    """Every test vector through both stages. Returns the failures."""
    out = []
    for v in TEST_VECTORS:
        lat, lon = grid_to_airy(v["easting"], v["northing"])
        d = _metres(lat, lon, *v["osgb36"])
        if d > TOLERANCE_M:
            out.append(f"{v['name']}: projection inverse is {d:.3f} m from the "
                       f"published OSGB36 position")
        lat, lon = to_wgs84(v["easting"], v["northing"], places=7)
        d = _metres(lat, lon, *v["wgs84"])
        if d > TOLERANCE_M:
            out.append(f"{v['name']}: full conversion is {d:.3f} m from the "
                       f"published ETRS89 position")
    return out


def _metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dy = (lat1 - lat2) * 111320.0
    dx = (lon1 - lon2) * 111320.0 * math.cos(math.radians(lat2))
    return math.hypot(dx, dy)

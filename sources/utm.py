"""
ETRS89 / UTM to WGS84, so a Spanish permit's coordinates can become a mark.

    import utm
    utm.to_wgs84(285333, 4421360, zone=30)   # -> (39.9152, -5.5116)

WHY THIS EXISTS, AND WHY IT IS NOT osgb36.py. The same problem in a different
country. Planning and environmental authorisations on the continent give a
position as UTM eastings and northings on ETRS89, exactly as a British permit
gives a National Grid reference, and a register that could read one and not the
other would place a works in Sunderland and refuse to place one in Cáceres.
Envision AESC's Navalmoral de la Mata plant is the case that forced it: no
basemap feature naming the works, an industrial estate polygon that is refused
on the usual rule, and a Diario Oficial de Extremadura resolution that states
"las coordenadas geográficas representativas de la instalación son: X: 285.333;
Y: 4.421.360; ETRS89, huso 30".

ONE STAGE, NOT TWO, and that is the whole difference from the British case.
OSGB36 needs a projection inverse AND a datum shift, because Airy 1830 sits a
hundred metres from WGS84. ETRS89 is a WGS84-family datum: it was defined
coincident with WGS84 in 1989 and Europe has since drifted from it by a few tens
of centimetres. That is two orders of magnitude below the eleven metres four
decimal places store, so there is no Helmert transformation here and adding one
would be pretending to a precision the source does not have.

WHAT IS CHECKED, AND HOW A CONVERSION LIBRARY IS CHECKED WITHOUT ONE.
sources/osgb36.py holds itself against the Ordnance Survey's published worked
example. There is no equivalent published UTM vector carried here, so the check
is built from three things that cannot all pass on broken arithmetic:

  THE OS WORKED EXAMPLE, THROUGH THIS FILE'S OWN SERIES. The transverse Mercator
  inverse below is generic -- it takes the ellipsoid and the projection
  parameters -- so it can be run with the National Grid's, and its answer for
  Caister Water Tower can be held against the position the Ordnance Survey
  publishes for it. That is a published test point proving the series, borrowed
  from the one country that publishes one.

  A ROUND TRIP. The forward projection is implemented as well as the inverse and
  they have to invert each other to a millimetre across the zone. A single
  series with a wrong coefficient survives this; two independent series with the
  same wrong coefficient do not, which is why the OS vector is there too.

  THE DEFINITION. On the central meridian the easting is exactly the false
  easting, and at the equator the northing is exactly zero. Both are what UTM
  means rather than what it computes, and a sign error or a scale error breaks
  them.
"""

from __future__ import annotations

import math

# GRS80, the ellipsoid ETRS89 is defined on. WGS84's differs from it in the
# semi-minor axis by about a tenth of a millimetre.
GRS80_A = 6378137.0
GRS80_B = 6356752.314140356

# UTM's own constants. Every zone is the same projection with a different
# central meridian, which is why they are parameters below and not globals.
K0 = 0.9996
FALSE_EASTING = 500000.0
FALSE_NORTHING_SOUTH = 10000000.0


def central_meridian(zone: int) -> float:
    """The zone's central meridian in degrees. Zone 1 is centred on -177."""
    if not 1 <= zone <= 60:
        raise ValueError(f"UTM zone {zone} is outside 1..60")
    return -183.0 + 6.0 * zone


def _meridional_arc(lat: float, a: float, b: float, k0: float, lat0: float) -> float:
    """Distance along the meridian from lat0 to lat, scaled by k0."""
    n = (a - b) / (a + b)
    dl, sl = lat - lat0, lat + lat0
    return b * k0 * (
        (1 + n + 1.25 * n**2 + 1.25 * n**3) * dl
        - (3 * n + 3 * n**2 + 2.625 * n**3) * math.sin(dl) * math.cos(sl)
        + (1.875 * n**2 + 1.875 * n**3) * math.sin(2 * dl) * math.cos(2 * sl)
        - (35 / 24) * n**3 * math.sin(3 * dl) * math.cos(3 * sl)
    )


def tm_inverse(easting: float, northing: float, *, a: float, b: float, k0: float,
               lat0: float, lon0: float, e0: float, n0: float) -> tuple[float, float]:
    """A transverse Mercator grid position as latitude and longitude in degrees.

    The Ordnance Survey series, written once and given its parameters, because
    the National Grid and UTM are the same projection with different numbers in
    it. `lat0` and `lon0` are in degrees; the false origin is in metres.
    """
    lat0, lon0 = math.radians(lat0), math.radians(lon0)
    e2 = 1 - (b**2) / (a**2)

    # The footpoint latitude has no closed form. Bounded so a bad input cannot
    # hang a build, exactly as in sources/osgb36.py.
    lat = lat0
    m = 0.0
    for _ in range(20):
        lat += (northing - n0 - m) / (a * k0)
        m = _meridional_arc(lat, a, b, k0, lat0)
        if abs(northing - n0 - m) < 1e-5:
            break

    sin_lat = math.sin(lat)
    nu = a * k0 / math.sqrt(1 - e2 * sin_lat**2)
    rho = a * k0 * (1 - e2) / (1 - e2 * sin_lat**2) ** 1.5
    eta2 = nu / rho - 1

    tan_lat = math.tan(lat)
    t2, t4, t6 = tan_lat**2, tan_lat**4, tan_lat**6
    sec_lat = 1 / math.cos(lat)
    de = easting - e0

    vii = tan_lat / (2 * rho * nu)
    viii = tan_lat / (24 * rho * nu**3) * (5 + 3 * t2 + eta2 - 9 * t2 * eta2)
    ix = tan_lat / (720 * rho * nu**5) * (61 + 90 * t2 + 45 * t4)
    x = sec_lat / nu
    xi = sec_lat / (6 * nu**3) * (nu / rho + 2 * t2)
    xii = sec_lat / (120 * nu**5) * (5 + 28 * t2 + 24 * t4)
    xiia = sec_lat / (5040 * nu**7) * (61 + 662 * t2 + 1320 * t4 + 720 * t6)

    out_lat = lat - vii * de**2 + viii * de**4 - ix * de**6
    out_lon = lon0 + x * de - xi * de**3 + xii * de**5 - xiia * de**7
    return math.degrees(out_lat), math.degrees(out_lon)


def tm_forward(lat_deg: float, lon_deg: float, *, a: float, b: float, k0: float,
               lat0: float, lon0: float, e0: float, n0: float) -> tuple[float, float]:
    """Latitude and longitude in degrees to a transverse Mercator grid position.

    Here to be checked against, not to be used: nothing in this repository
    projects a position forward. A round trip is the cheapest honest test of an
    inverse whose answer nobody can look up.
    """
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    lat0r, lon0r = math.radians(lat0), math.radians(lon0)
    e2 = 1 - (b**2) / (a**2)

    sin_lat, cos_lat, tan_lat = math.sin(lat), math.cos(lat), math.tan(lat)
    nu = a * k0 / math.sqrt(1 - e2 * sin_lat**2)
    rho = a * k0 * (1 - e2) / (1 - e2 * sin_lat**2) ** 1.5
    eta2 = nu / rho - 1
    m = _meridional_arc(lat, a, b, k0, lat0r)

    t2, t4 = tan_lat**2, tan_lat**4
    dl = lon - lon0r

    i = m + n0
    ii = nu / 2 * sin_lat * cos_lat
    iii = nu / 24 * sin_lat * cos_lat**3 * (5 - t2 + 9 * eta2)
    iiia = nu / 720 * sin_lat * cos_lat**5 * (61 - 58 * t2 + t4)
    iv = nu * cos_lat
    v = nu / 6 * cos_lat**3 * (nu / rho - t2)
    vi = nu / 120 * cos_lat**5 * (5 - 18 * t2 + t4 + 14 * eta2 - 58 * t2 * eta2)

    northing = i + ii * dl**2 + iii * dl**4 + iiia * dl**6
    easting = e0 + iv * dl + v * dl**3 + vi * dl**5
    return easting, northing


def to_wgs84(easting: float, northing: float, zone: int, *, north: bool = True,
             places: int = 4) -> tuple[float, float]:
    """An ETRS89 UTM position as a WGS84 latitude and longitude.

    Rounded to `places` decimals, four by default, which is about eleven metres
    and is the precision every other coordinate in this register is stored at.
    Rounded here rather than at the call site so that two callers cannot store
    the same grid reference to different precision -- the same rule
    sources/osgb36.py runs under.
    """
    lat, lon = tm_inverse(
        easting, northing,
        a=GRS80_A, b=GRS80_B, k0=K0, lat0=0.0, lon0=central_meridian(zone),
        e0=FALSE_EASTING, n0=0.0 if north else -FALSE_NORTHING_SOUTH,
    )
    return round(lat, places), round(lon, places)


# The Ordnance Survey's worked example, run through this file's own series with
# the National Grid's parameters. See WHAT IS CHECKED in the module docstring:
# it is the one published transverse Mercator test point available, and what it
# proves is the series rather than the datum.
OS_VECTOR = {
    "name": "Caister Water Tower, through the National Grid's parameters",
    "easting": 651409.903, "northing": 313177.270,
    "airy": (52.6575703, 1.7179216),
    "params": {"a": 6377563.396, "b": 6356256.909, "k0": 0.9996012717,
               "lat0": 49.0, "lon0": -2.0, "e0": 400000.0, "n0": -100000.0},
}

# How far a check may miss before the build fails, in metres. A tenth of a
# metre, as in sources/osgb36.py: this tests arithmetic, not method.
TOLERANCE_M = 0.1

# Round-trip points, spread across the zones this register actually reads and
# from the equator to the top of Europe, because a series that is right in the
# middle of a zone and wrong at its edge is the bug this catches.
ROUND_TRIP = [
    (39.9152, -5.5116, 30),   # Navalmoral de la Mata, the case that forced this
    (0.0, -3.0, 30),          # equator, central meridian
    (60.0, -1.5, 30),         # the top of the zone, near its western edge
    (43.0, -1.0, 30),         # the zone's eastern half
    (48.8566, 2.3522, 31),    # Paris, a second zone
    (55.6761, 12.5683, 32),   # Copenhagen, a third
]


def self_check() -> list[str]:
    """Every check in the docstring. Returns the failures."""
    out: list[str] = []

    lat, lon = tm_inverse(OS_VECTOR["easting"], OS_VECTOR["northing"],
                          **OS_VECTOR["params"])
    d = _metres(lat, lon, *OS_VECTOR["airy"])
    if d > TOLERANCE_M:
        out.append(f"{OS_VECTOR['name']}: the projection inverse is {d:.3f} m from "
                   f"the position the Ordnance Survey publishes")

    for lat, lon, zone in ROUND_TRIP:
        params = {"a": GRS80_A, "b": GRS80_B, "k0": K0, "lat0": 0.0,
                  "lon0": central_meridian(zone), "e0": FALSE_EASTING, "n0": 0.0}
        e, n = tm_forward(lat, lon, **params)
        back_lat, back_lon = tm_inverse(e, n, **params)
        d = _metres(back_lat, back_lon, lat, lon)
        if d > 0.001:
            out.append(f"round trip at {lat}, {lon} (zone {zone}) misses by {d:.4f} m")

    # The definition. On the central meridian the easting is the false easting,
    # and the equator is the zero of northing.
    for zone in (29, 30, 31):
        params = {"a": GRS80_A, "b": GRS80_B, "k0": K0, "lat0": 0.0,
                  "lon0": central_meridian(zone), "e0": FALSE_EASTING, "n0": 0.0}
        e, n = tm_forward(0.0, central_meridian(zone), **params)
        if abs(e - FALSE_EASTING) > 0.001 or abs(n) > 0.001:
            out.append(f"zone {zone}: the origin projects to {e:.3f}, {n:.3f} rather "
                       f"than to {FALSE_EASTING}, 0")
    return out


def _metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dy = (lat1 - lat2) * 111320.0
    dx = (lon1 - lon2) * 111320.0 * math.cos(math.radians(lat2))
    return math.hypot(dx, dy)


if __name__ == "__main__":
    failures = self_check()
    print("\n".join(failures) if failures else "utm: self-check clean")
    print(to_wgs84(285333, 4421360, zone=30))

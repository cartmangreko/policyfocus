"""HD72 / EOV to WGS84, so a Hungarian permit's coordinates can become a mark.

    import eov
    eov.to_wgs84(835619, 251450)   # -> (47.5806, 21.5154)

WHY THIS FILE DOES NOT CONTAIN A PROJECTION. sources/osgb36.py and sources/utm.py
implement their own arithmetic, and they can: a transverse Mercator inverse is a
series anybody can transcribe from a published formula and hold against a
published worked example. EOV is not that. It is a double projection -- the HD72
ellipsoid onto a Gauss sphere, the sphere onto an oblique cylinder, at a rotation
chosen so the distortion band lies along Hungary -- and it sits on a datum that
needs a Helmert shift of some ninety metres to reach WGS84. Writing that by hand
would mean carrying a second, unverifiable copy of a definition the EPSG registry
already publishes and PROJ already implements. So this file converts nothing. It
names EPSG:23700, asks pyproj, and spends its whole length checking the answer.

WHAT THAT COSTS AND WHY IT IS PAID. pyproj is the first dependency the GATES
need rather than the fetcher, so it lives in sources/requirements-gates.txt and
sources/ensure_gate_deps.py installs it at the head of the prebuild -- in every
environment the build runs in, not only the one that added it. Where it is absent
the gate fails loudly rather than skipping: a coordinate check that quietly does
not run is worse than one that was never written.

WHAT IS CHECKED, WHICH IS NOT NOTHING JUST BECAUSE THE MATHS IS SOMEBODY ELSE'S.
Three properties, and no arrangement of a broken install passes all three:

  THE DEFINITIONAL ORIGIN. EOV's false origin, easting 650 000 northing 200 000,
  is the projection centre by definition, and the centre is published:
  47 deg 08' 39.8174" N, 19 deg 02' 54.8584" E. Converting the origin has to land
  NEAR that point, which proves the grid definition is EOV and not some other
  Hungarian system, and it has to land a measurable distance AWAY from it, which
  proves a datum shift is being applied rather than HD72 latitudes being handed
  back as though they were WGS84 ones. Both bounds matter; either alone passes on
  a plausible mistake.

  A ROUND TRIP. Forward and inverse have to invert each other to a tenth of a
  metre, three orders below what four decimal places store.

  THE GRID'S OWN SHAPE. EOV northings rise to the north and eastings to the east
  over Hungary, and the site this was written for has to keep the position it was
  landed with. A transposed easting and northing -- the mistake this projection
  invites, because Hungarian documents write the pair as "EOV Y" then "EOV X" and
  Y is the easting -- fails here.
"""

import math

# The point EOV is defined about, in degrees, and the false coordinates the
# projection gives it. Both are definitional: they come from the EPSG entry for
# EPSG:23700 rather than from any conversion this file could run.
ORIGIN_EN = (650000.0, 200000.0)
ORIGIN_LATLON = (47 + 8 / 60 + 39.8174 / 3600, 19 + 2 / 60 + 54.8584 / 3600)

# The datum shift HD72 -> WGS84 over Hungary is of the order of a hundred metres.
# The bounds are wide because the exact figure is PROJ's business and narrow
# enough that a missing shift (0 m) and a wrong datum (kilometres) both fail.
SHIFT_MIN_M, SHIFT_MAX_M = 10.0, 300.0

_R = 6371008.8  # mean Earth radius, for the metre distances in the checks only


def _transformers():
    """pyproj's two directions, or a failure a reader can act on."""
    try:
        from pyproj import Transformer
    except ImportError as exc:  # pragma: no cover - the message is the point
        raise RuntimeError(
            "sources/eov.py needs pyproj, which is not installed: "
            f"{exc}. Run `python3 -m pip install -r sources/requirements-gates.txt`. "
            "The gate fails rather than skipping the check, because a coordinate "
            "nobody recomputed is a coordinate nobody can defend."
        ) from exc
    return (
        Transformer.from_crs("EPSG:23700", "EPSG:4326", always_xy=True),
        Transformer.from_crs("EPSG:4326", "EPSG:23700", always_xy=True),
    )


def to_wgs84(easting: float, northing: float, *, places: int = 4) -> tuple:
    """EOV easting and northing to WGS84 latitude and longitude.

    Hungarian filings print the pair as "EOV Y" then "EOV X". Y IS THE EASTING.
    The argument order here is easting first, matching osgb36 and utm, so a value
    copied across in the order the document prints it is transposed.
    """
    forward, _ = _transformers()
    lon, lat = forward.transform(easting, northing)
    return round(lat, places), round(lon, places)


def to_eov(lat: float, lon: float) -> tuple:
    """WGS84 back to EOV easting and northing. Here for the round trip."""
    _, back = _transformers()
    return back.transform(lon, lat)


def _metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dy = math.radians(lat2 - lat1) * _R
    dx = math.radians(lon2 - lon1) * _R * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(dx, dy)


def self_check() -> list:
    """Run on every gate invocation. Returns a list of failures, empty when well."""
    out = []
    try:
        _transformers()
    except RuntimeError as exc:
        return [str(exc)]

    lat, lon = to_wgs84(*ORIGIN_EN, places=7)
    off = _metres(lat, lon, *ORIGIN_LATLON)
    if not SHIFT_MIN_M <= off <= SHIFT_MAX_M:
        out.append(
            f"the false origin E {ORIGIN_EN[0]:.0f} N {ORIGIN_EN[1]:.0f} converts to "
            f"{lat}, {lon}, which is {off:.1f} m from EOV's defined centre "
            f"{ORIGIN_LATLON[0]:.6f}, {ORIGIN_LATLON[1]:.6f}. Expected between "
            f"{SHIFT_MIN_M:.0f} and {SHIFT_MAX_M:.0f} m: nearer means the HD72 to "
            f"WGS84 shift is not being applied, further means this is not EOV"
        )

    for e, n in ((835619.0, 251450.0), ORIGIN_EN, (500000.0, 100000.0)):
        la, lo = to_wgs84(e, n, places=9)
        e2, n2 = to_eov(la, lo)
        d = math.hypot(e2 - e, n2 - n)
        if d > 0.1:
            out.append(f"round trip at E {e:.0f} N {n:.0f} misses by {d:.3f} m")

    north = to_wgs84(835619, 261450)[0]
    east = to_wgs84(845619, 251450)[1]
    here = to_wgs84(835619, 251450)
    if not north > here[0]:
        out.append(f"10 km of northing did not move the point north: {north} vs {here[0]}")
    if not east > here[1]:
        out.append(f"10 km of easting did not move the point east: {east} vs {here[1]}")
    if here != (47.5806, 21.5154):
        out.append(
            f"E 835619 N 251450, the position the Debrecen row stands on, now converts "
            f"to {here} and not (47.5806, 21.5154)"
        )
    return out


if __name__ == "__main__":
    failures = self_check()
    for failure in failures:
        print("FAIL:", failure)
    if not failures:
        print("eov: OK —", to_wgs84(835619, 251450), "for EOV Y 835619 / X 251450")

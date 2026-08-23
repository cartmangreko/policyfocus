"""
Colour arithmetic for the layer gate: hex in, CIE L*a*b* out, distances between.

Small on purpose. The gate needs exactly one question answered -- "are these two
colours far enough apart that a reader will not confuse them" -- and CIE76 is
enough to answer it. CIEDE2000 is more accurate about small differences, and the
differences this file is asked about are large ones: the whole point is to catch
a palette entry that has drifted INTO a reserved hue, and a metric that
disagrees with CIE76 about that is not a metric anybody needs here.

D65, sRGB, 2-degree observer.
"""

from __future__ import annotations


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"{value!r} is not a hex colour")
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _f(t: float) -> float:
    return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29


def hex_to_lab(value: str) -> tuple[float, float, float]:
    r, g, b = (_linear(c) for c in hex_to_rgb(value))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) / 1.00000
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    fx, fy, fz = _f(x), _f(y), _f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def distance(a: str, b: str) -> float:
    """CIE76 delta-E. Roughly: under 10 is a shade of the same colour, 20 is
    'related', 30+ is two colours a reader will name differently."""
    la, aa, ba = hex_to_lab(a)
    lb, ab, bb = hex_to_lab(b)
    return ((la - lb) ** 2 + (aa - ab) ** 2 + (ba - bb) ** 2) ** 0.5


def hue_degrees(value: str) -> float:
    """Lab hue angle, for reporting. Not used as a gate: two colours can share a
    hue angle and be told apart by lightness, and the gate should say so in the
    units it actually judges in."""
    import math
    _, a, b = hex_to_lab(value)
    return math.degrees(math.atan2(b, a)) % 360

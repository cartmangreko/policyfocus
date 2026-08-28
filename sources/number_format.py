"""
How this site writes a euro amount, on the Python side.

    import number_format as nf
    nf.money_long(3_250_000_000)    -> "€3.3 billion"
    nf.money_short(3_250_000_000)   -> "€3.3 bn"

THE RULES ARE NOT IN THIS FILE. They are in data/number_format.json, which
web/lib/money.ts reads too. This module is one of two implementations of that
contract; the other is TypeScript, and the whole reason the contract is a file
rather than a constant is that the two used to be written separately and
rounded a tie in opposite directions. See the comment in the JSON.

WHY THE ROUNDING IS DONE ON DIGITS. `f"{x:,.1f}"` rounds half to even and
JavaScript's toFixed rounds half away from zero, so 3.25 comes out 3.2 here and
3.3 there -- which is exactly the bug this file exists to close. Neither
language's built-in is used: both implementations round the shortest
round-trip decimal representation of the number, which Python spells repr()
and JavaScript spells String(), and which is the same string in both.

Scaling by a power of ten first would reintroduce the divergence in a subtler
place: 1.005 * 100 is 100.49999999999999 in binary, so a scale-then-round
implementation rounds it down while a digit implementation rounds it up.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "data" / "number_format.json"


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


_C = contract()


def round_decimal(value: float, decimals: int) -> float:
    """Round half away from zero, on the number's decimal digits.

    Mirrored character for character by roundDecimal in web/lib/money.ts. Any
    edit here is an edit there, and data/number_format.json's `cases` is what
    notices if it is not.
    """
    negative = value < 0
    text = repr(abs(float(value)))
    if "e" in text or "E" in text:
        text = f"{abs(float(value)):.20f}"
    if "." not in text:
        return float(value)
    whole, frac = text.split(".")
    if len(frac) <= decimals:
        return float(value)
    keep = whole + frac[:decimals]
    carry = 1 if int(frac[decimals]) >= 5 else 0
    out = (int(keep) + carry) / (10 ** decimals)
    return -out if negative else out


def _tier(value: float) -> dict:
    """The tier the figure belongs in, after rounding is taken into account.

    The tier is chosen by the raw value, and then PROMOTED once if rounding at
    that tier carries the figure up to the next threshold. Both halves are
    needed and each one alone is wrong:

      raw only        €999,999,999 sits in the millions, rounds to 1,000, and
                      renders "€1,000 million" — a billion said the long way.
      rounded only    €750,000 rounds to 1 at the million tier's resolution,
                      reaches the threshold, and renders "€1 million" — a
                      quarter of the figure thrown away to reach a rounder word.

    Promotion is one step, because a figure that rounds up through two
    thresholds does not exist: reaching the next tier takes a factor of a
    thousand and rounding moves a figure by less than one unit of its own
    resolution.
    """
    tiers = _C["tiers"]
    index = next((i for i, t in enumerate(tiers) if abs(value) >= t["at"]), len(tiers) - 1)
    tier = tiers[index]
    if index > 0:
        above = tiers[index - 1]
        rounded = round_decimal(abs(value) / tier["divide_by"], tier["decimals"])
        if rounded * tier["divide_by"] >= above["at"]:
            return above
    return tier


def _digits(value: float, tier: dict) -> str:
    scaled = round_decimal(value / tier["divide_by"], tier["decimals"])
    text = f"{scaled:,.{tier['decimals']}f}"
    if _C["group_separator"] != ",":
        text = text.replace(",", _C["group_separator"])
    if _C["decimal_separator"] != ".":
        text = text.replace(".", _C["decimal_separator"])
    return text


def money(value: float, form: str) -> str:
    """One euro amount. `form` is "long" for prose and "short" for a surface
    where the unit has to fit in a column.

    THE SIGN GOES OUTSIDE THE SYMBOL. "-€3.3 billion", never "€-3.3 billion":
    the minus is about the amount, not about the currency, and a reader scanning
    a column of figures finds it at the left edge where it belongs.
    """
    tier = _tier(value)
    word = tier[form]
    joint = _C["form_separator"][form]
    sign = "-" if value < 0 else ""
    body = _digits(abs(value), tier)
    return f"{sign}{_C['prefix']}{body}" + (f"{joint}{word}" if word else "")


def digits_of(figure: str) -> str:
    """The numeric token out of a rendered figure, for a fact that has to
    declare the number its sentence will print.

    A fact used to compute `value / 1e6` while the formatter chose its own
    scale from the size of the value; the two agreed up to €999 million and
    parted company above it. Reading the digits back off the rendered string
    cannot disagree with it.
    """
    import re as _re
    return _re.search(r"[\d,.]+", figure).group(0)


def money_long(value: float) -> str:
    return money(value, "long")


def money_short(value: float) -> str:
    return money(value, "short")


def money_compact(value: float) -> str:
    return money(value, "compact")


def money_rate(value: float, compact: bool = False) -> str:
    """A price per unit — "€75.46 per tonne".

    No tiers: a rate is quoted at the precision the thing is traded at, whatever
    its size. Running it through the amount tiers would turn a carbon price into
    "€0.0 million per tonne", which is the tiers being applied to a figure they
    were not written for.
    """
    rule = _C["rate"]
    scaled = round_decimal(value, rule["decimals"])
    sign = "-" if scaled < 0 else ""
    body = f"{abs(scaled):,.{rule['decimals']}f}"
    if compact:
        return f"{sign}{_C['prefix']}{body}{rule['compact_suffix']}"
    return f"{sign}{_C['prefix']}{body} {rule['suffix']}"


def cases() -> list[dict]:
    """The vectors, computed. `data/number_format.json` stores what this
    returns, and both implementations are checked against the stored copy."""
    return [{"value": v, "long": money_long(v), "short": money_short(v)}
            for v in _C.get("case_values", DEFAULT_CASE_VALUES)]


# Every tie and every tier boundary, plus the two figures that actually put
# this file here: steel's committed total and cement's, one on a tie and one
# nowhere near it.
DEFAULT_RATE_VALUES = [0, 1.005, 2.345, 75.46, 82.8, -75.455, 1234.5]

DEFAULT_CASE_VALUES = [
    0, 1, 2.5, 999_999, 750_000, 1_000_000, 1_500_000, 2_500_000, 421_000_000,
    999_999_999, 1_000_000_000, 1_250_000_000, 3_250_000_000, 3_350_000_000,
    12_345_000_000, 1_234_500_000, -3_250_000_000, -1_500_000, -421_000_000,
]

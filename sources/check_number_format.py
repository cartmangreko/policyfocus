"""
The gate on how this site writes a euro amount: data/number_format.json.

    python3 check_number_format.py       # exits non-zero on any problem

THE PYTHON HALF OF A PARITY GATE. web/lib/money.test.mts is the other half and
the prebuild chain runs it. Between them they hold two implementations of one
contract to the same behaviour, which is the thing that was missing when
build_opportunity.py and web/lib/transition.ts each formatted euros their own
way and disagreed about a tie: steel committed exactly €3,250,000,000 and the
sector page printed "€3.2 billion" and "€3.3 bn" four lines apart.

What is checked here:

  VECTORS       every case in the contract reproduces from this
                implementation. The cases are the behaviour; a declaration
                that both languages round half away from zero proves nothing
                about whether both do.

  COVERAGE      the vectors still cover the cases that matter — a tie at every
                tier, a value either side of every threshold, and a negative.
                Vectors that quietly stopped covering the tie would leave the
                gate green and the bug open.

  ONE SOURCE    no formatter anywhere in sources/ or web/lib/ builds a euro
                figure of its own. This is the check that actually keeps the
                contract single: the divergence did not come from anybody
                editing a shared rule, it came from two files each writing
                their own.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import number_format as nf

ROOT = Path(__file__).resolve().parent.parent

# A euro figure assembled inline: the currency symbol immediately followed by a
# format field, which is what every one of the private formatters looked like —
# f"€{value / 1e6:,.0f} million" and `€${(n / 1e9).toFixed(1)} bn`. Narrow on
# purpose: arithmetic on a euro value is not a formatter, and only the moment a
# symbol is welded to a substitution is a second way of writing money born.
INLINE_EURO = re.compile(r"€\$?\{")

# The two implementations, their test, and this gate.
ALLOWED = {
    "sources/number_format.py",
    "web/lib/money.ts",
    "web/lib/money.test.mts",
    "sources/check_number_format.py",
}


def check_vectors(problems: list[str]) -> None:
    contract = nf.contract()
    for case in contract["rate_cases"]:
        got = nf.money_rate(case["value"])
        if got != case["rate"]:
            problems.append(f"rate case {case['value']}: the contract stores "
                            f"{case['rate']!r} and this implementation produces {got!r}")
    for case in contract["cases"]:
        for form in ("long", "short", "compact"):
            got = nf.money(case["value"], form)
            if got != case[form]:
                problems.append(
                    f"case {case['value']}: the contract stores {case[form]!r} for the "
                    f"{form} form and this implementation produces {got!r}. Regenerate "
                    f"the vectors deliberately, or fix the implementation — but the two "
                    f"languages move together or not at all")


def check_coverage(problems: list[str]) -> None:
    contract = nf.contract()
    values = {c["value"] for c in contract["cases"]}
    tiers = contract["tiers"]

    if not any(v < 0 for v in values):
        problems.append("no negative in the vectors, and the three rounding modes in play "
                        "disagree about negatives more than they disagree about positives")

    for tier in tiers:
        if tier["at"] == 0:
            continue
        if not any(v == tier["at"] for v in values):
            problems.append(f"no vector sits exactly on the {tier['at']:,} threshold")
        if not any(tier["at"] > v >= tier["at"] * 0.999 for v in values):
            problems.append(f"no vector sits just under the {tier['at']:,} threshold, which "
                            f"is where a rounded figure gets promoted a tier")

    # A tie at each tier's own resolution: the case the whole contract is for.
    for tier in tiers:
        if tier["at"] == 0:
            continue  # whole euros; the tie there is half a cent and no surface has one
        step = tier["divide_by"] / (10 ** tier["decimals"])
        if not any(abs(v) % step == step / 2 for v in values if v):
            problems.append(f"no vector lands on a tie for the tier at {tier['at']:,} "
                            f"(a figure ending in half of {step:,.0f})")

    rates = {c["value"] for c in contract["rate_cases"]}
    if not any(round(abs(v) * 1000) % 10 == 5 for v in rates):
        problems.append("no rate vector lands on a tie at the rate's own precision")


def check_one_source(problems: list[str]) -> None:
    for path in sorted(list((ROOT / "sources").glob("*.py"))
                       + list((ROOT / "web" / "lib").glob("*.ts"))
                       + list((ROOT / "web" / "lib").glob("*.mts"))
                       + list((ROOT / "web" / "components").glob("*.tsx"))):
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWED:
            continue
        text = path.read_text(encoding="utf-8")
        # Strip comments: a docstring explaining the bug is not the bug.
        text = re.sub(r'"""[\s\S]*?"""|/\*[\s\S]*?\*/|^\s*(?:#|//).*$', "", text, flags=re.M)
        for match in INLINE_EURO.finditer(text):
            line = text[:match.start()].count("\n") + 1
            problems.append(
                f"{rel}:{line}: builds a euro figure of its own. There is one way this "
                f"site writes an amount and it is data/number_format.json — import "
                f"money_long/money_short, or moneyLong/moneyShort")


def main() -> int:
    problems: list[str] = []
    check_vectors(problems)
    check_coverage(problems)
    check_one_source(problems)
    if problems:
        print(f"check_number_format: {len(problems)} problems\n")
        for p in problems:
            print(f"  {p}")
        return 1
    n = len(nf.contract()["cases"])
    print(f"check_number_format: OK — {n} vectors reproduce, and no file outside "
          f"the two implementations formats a euro amount")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "sources"))
    raise SystemExit(main())

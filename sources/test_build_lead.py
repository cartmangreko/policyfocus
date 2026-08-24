"""
Tests for the lead gate. A gate is only worth the failures it catches, so each
case here breaks one rule from amendment brief 2 §4 on purpose and asserts that
the gate names it.

    python3 test_build_lead.py

These run against build_lead's own functions rather than against a copy of the
tree, because the thing under test is the gate and the composer, not the file
writing. The last case is the repository as it stands: the committed lead must
still build and pass, so a test run cannot leave a false green behind.
"""
from __future__ import annotations

import sys

import build_lead as bl


def fact(fid, text, as_of="2025-01-01", numbers=(), parts=None, sourced=()):
    return bl._fact(fid, fid.replace("_", " ").title(), text, as_of,
                    list(numbers), parts or {}, sourced)


FACTS = {
    "decisive_exposure": fact(
        "decisive_exposure", "CBAM certificates — €75.46 per tonne of cost.",
        "2026-08-21", ["75.46"],
        {"name": "CBAM certificates", "figure": "€75.46 per tonne",
         "direction": "cost", "bearer": "importer"},
        ("CBAM certificates",)),
    "binding_constraint": fact(
        "binding_constraint", "Green premium — a market constraint.",
        "2026-01-01", ["4", "3"],
        {"name": "Green premium", "type": "market", "count": 4, "weight": "3"},
        ("Green premium",)),
}

CASES: list[tuple[str, dict, str]] = [
    (
        "a number that is in no fact",
        {"text": "European cement carries €99.00 per tonne of cost.",
         "from": ["decisive_exposure"]},
        "is in no fact",
    ),
    (
        "a date that is no fact's as-of date",
        {"text": "It moved on 1 March 2020.", "from": ["decisive_exposure"]},
        "no fact's as-of date",
    ),
    (
        "three sentences where two are allowed",
        {"text": "One thing. Another thing. A third thing.",
         "from": ["decisive_exposure"]},
        "at most 2 allowed",
    ),
    (
        "a sentence mapping to no fact",
        {"text": "Something is the case.", "from": []},
        "no fact id",
    ),
    (
        "a sentence naming a fact that was not computed",
        {"text": "Something is the case.", "from": ["the_gap"]},
        "was not computed",
    ),
    (
        "a judgment adjective",
        {"text": "The constraint is critical.", "from": ["binding_constraint"]},
        "judgment adjective",
    ),
    (
        "a banned word outside a sourced fragment",
        {"text": "The register says so.", "from": ["binding_constraint"]},
        "banned word",
    ),
]


def main() -> int:
    failures = 0

    for name, block, expected in CASES:
        problems = bl.gate(block, FACTS)
        hit = any(expected in p for p in problems)
        print(f"{'ok  ' if hit else 'FAIL'} {name}")
        if not hit:
            failures += 1
            print(f"       expected {expected!r}, got {problems}")

    # A sourced fragment is exempt: the IEA's own unit is the IEA's sentence.
    facts = dict(FACTS)
    facts["the_gap"] = fact(
        "the_gap", "Premium: 75-150% above a conventional plant.", "2025",
        ["75-150"], {"figure": "75-150%", "rest": "above a conventional plant"},
        ("above a conventional plant",))
    problems = bl.gate(
        {"text": "The largest gap is 75-150% above a conventional plant.",
         "from": ["the_gap"]}, facts)
    print(f"{'ok  ' if not problems else 'FAIL'} a sourced fragment is exempt from the word ban")
    if problems:
        failures += 1
        print(f"       expected none, got {problems}")

    # The repository as it stands.
    doc = bl.build("cement")
    clean = not doc["notes"] and doc["why_it_matters"] is not None
    print(f"{'ok  ' if clean else 'FAIL'} cement builds a lead with no fallback and no flag")
    if not clean:
        failures += 1
        print(f"       notes: {doc['notes']}")

    print(f"\n{len(CASES) + 2 - failures}/{len(CASES) + 2} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

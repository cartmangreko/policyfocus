#!/usr/bin/env python3
"""
Which sectors no business duty reaches, split into the two answers that matter.

    python3 sector_coverage.py            # report
    python3 sector_coverage.py --strict   # exit non-zero if any SUSPECTED GAP

WHY THIS IS NOT ONE LIST
========================
"Sectors with no measures" is a number that cannot be acted on, because it
mixes two unlike things:

  EXPECTED SECTORLESS   The register has no business duty for it, and that is
                        the correct state of the world. batsol, clean and ccs
                        are policy categories rather than industries -- nothing
                        in the corpus addresses "clean tech" as an addressee.
                        A zero here is information, not a defect.

  SUSPECTED GAP         A sector in the spine, backed by a real FIGARO
                        industry, that no business duty reaches. That is either
                        a genuine finding (the corpus really does not regulate
                        it) or a hole in the extraction -- and the two are
                        indistinguishable from the outside, which is precisely
                        why it needs a human.

Reporting them together is how a real gap hides behind three expected zeros.

CLASS BUSINESS ONLY
===================
The question is what the register requires OF FIRMS. A sector reached only by
Member State duties has no operator-facing content, and counting those would
mark a sector covered when nothing in it addresses a company. Rows of class
state, commission, investor and household are therefore excluded from the
count, and reported alongside so the difference is visible rather than implied.

NAMED AND REACHED BOTH COUNT
============================
A sector reached through a supply chain is still reached. The report keeps the
two apart, because a sector that is only ever reached and never named is a
weaker kind of coverage -- worth seeing, not worth failing on.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from build_graph import REGISTER_FILES, SECTOR_SPINE

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

BUSINESS = "business"


def expected_sectorless() -> set[str]:
    """Sectors that are policy categories rather than FIGARO industries.

    The authority is data/exposure/_manifest.json: a slug with no exposure file
    has no industry behind it, so a zero is expected rather than suspicious.
    Derived rather than hardcoded, so adding a sector to the spine cannot
    silently land it in the wrong bucket.
    """
    manifest = json.loads((DATA / "exposure" / "_manifest.json").read_text(encoding="utf-8"))
    return {s for s in SECTOR_SPINE if s not in manifest}


def load_rows() -> list[dict]:
    rows = []
    for slug in REGISTER_FILES:
        rows.extend(json.loads((DATA / f"{slug}.json").read_text(encoding="utf-8")))
    return rows


def main() -> int:
    rows = load_rows()
    business = [r for r in rows if r.get("class") == BUSINESS]

    named = Counter(s for r in business for s in (r.get("sectors_named") or []))
    reached = Counter(s for r in business for s in (r.get("sectors_reached") or []))
    other = Counter(s for r in rows if r.get("class") != BUSINESS
                    for s in (r.get("sectors_named") or []) + (r.get("sectors_reached") or []))

    expected = expected_sectorless()
    covered, sectorless = [], []
    for slug in sorted(SECTOR_SPINE):
        (covered if named[slug] + reached[slug] else sectorless).append(slug)

    print(f"SECTOR COVERAGE — {len(business)} business rows of {len(rows)} total, "
          f"{len(SECTOR_SPINE)} sectors in the spine\n")

    print("COVERED BY A BUSINESS DUTY")
    for slug in covered:
        parent = SECTOR_SPINE[slug]["parent"]
        tag = f"   (child of {parent})" if parent else ""
        print(f"  {slug:16} named {named[slug]:4}   reached {reached[slug]:4}{tag}")

    exp = [s for s in sectorless if s in expected]
    gaps = [s for s in sectorless if s not in expected]

    print(f"\nEXPECTED SECTORLESS ({len(exp)}) — policy categories, no FIGARO industry")
    for slug in exp or []:
        extra = f"; {other[slug]} non-business row(s) do reach it" if other[slug] else ""
        print(f"  {slug:16} {SECTOR_SPINE[slug]['name']}{extra}")
    if not exp:
        print("  (none)")

    print(f"\nSUSPECTED GAPS ({len(gaps)}) — FIGARO-backed, no business duty reaches them")
    for slug in gaps:
        extra = (f"; {other[slug]} non-business row(s) reach it" if other[slug]
                 else "; nothing in the register reaches it at all")
        print(f"  {slug:16} {SECTOR_SPINE[slug]['name']} "
              f"(FIGARO {SECTOR_SPINE[slug]['figaro']}){extra}")
    if not gaps:
        print("  (none)")

    print("\nA suspected gap is not a verdict. It is either a real finding about the "
          "corpus\nor a hole in an extraction, and those look identical from here.")

    if "--strict" in sys.argv and gaps:
        print(f"\nSTRICT: {len(gaps)} suspected gap(s).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

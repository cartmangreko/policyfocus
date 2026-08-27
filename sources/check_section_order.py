"""
The sector page's section sequence, enforced.

    python3 check_section_order.py          # exits non-zero on any violation

WHAT IS BEING PROTECTED
=======================
Brief 5 §1: the sector page answers a fixed sequence of questions, and every
sector asks them in the same order so the interface is learned once. The
sequence lives in data/prose.json -> sector_sections, and this checks that the
template renders it -- the same ids, in the same order, with nothing on the page
that the sequence does not know about.

The failure this exists to catch is not somebody reordering the list on purpose.
It is the ordinary one: a section added to the component in the place it was
convenient to type it, six months after the specification said where it goes.

NAV ENTRIES EQUAL RENDERED SECTIONS
===================================
§8 asks for that as a separate property. It holds by construction rather than by
inspection -- components/SectorMap.tsx computes ONE list, `renderedSections()`,
renders its sections from it and hands the same array to SectionNav -- and what
is checked here is that the construction is still the one in place: that the
component calls renderedSections, that it passes that array to the nav, and that
every section it draws is gated on the `present` map the array is built from. A
section rendered outside that map would be a section the nav could not know
about, which is the only way the two can drift.

WHY IT READS THE TSX
====================
The alternative is a render test, which needs a bundler, a DOM and the data
layer, to establish something the source states plainly. The parse here is
deliberately small and deliberately brittle: it recognises the exact shape the
component uses, and a rewrite that changes the shape fails loudly rather than
passing vacuously. A gate that silently matches nothing is worse than no gate.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROSE = ROOT / "data" / "prose.json"
TEMPLATE = ROOT / "web" / "components" / "SectorMap.tsx"

# The one section element shape the template uses. Matching it exactly is the
# point: a section written any other way is not checked, and would be, if this
# accepted anything with an id on it.
SECTION = re.compile(r'<section className="tmap-section" id="([a-z-]+)">')


def main() -> int:
    prose = json.loads(PROSE.read_text(encoding="utf-8"))
    block = prose.get("sector_sections")
    if not block:
        print("check_section_order: data/prose.json has no sector_sections block")
        return 1

    spec = [s["id"] for s in block["sections"]]
    unnumbered = [u["id"] for u in block.get("unnumbered", [])]
    tsx = TEMPLATE.read_text(encoding="utf-8")
    rendered = SECTION.findall(tsx)
    problems: list[str] = []

    if not rendered:
        problems.append(
            f"{TEMPLATE.name} renders no section this gate can see. It matches "
            f'<section className="tmap-section" id="..."> exactly; if the template '
            f"now writes them another way, teach this file the new shape rather "
            f"than leaving it matching nothing")

    # ---- the order --------------------------------------------------------
    seen = [r for r in rendered if r in spec]
    if len(set(seen)) != len(seen):
        dupes = sorted({r for r in seen if seen.count(r) > 1})
        problems.append(f"section(s) rendered twice: {', '.join(dupes)}")
    positions = [spec.index(r) for r in seen]
    if positions != sorted(positions):
        problems.append(
            f"sections render as {' → '.join(seen)}; the sequence in data/prose.json "
            f"is {' → '.join(spec)}. Every sector asks the same questions in the same "
            f"order, which is the whole of brief 5 §1")

    # ---- nothing off the list ---------------------------------------------
    for r in rendered:
        if r not in spec and r not in unnumbered:
            problems.append(
                f'section id="{r}" is neither one of the numbered questions nor one of '
                f"the unnumbered headings in data/prose.json. A section on this page "
                f"either answers a question the specification asks or is declared as "
                f"an exception to that, and there is one of those")

    # ---- the unnumbered ones come last ------------------------------------
    for i, r in enumerate(rendered):
        if r in unnumbered and any(later in spec for later in rendered[i + 1:]):
            problems.append(
                f'"{r}" is an unnumbered section and renders before a numbered one. '
                f"Sources closes the page; it does not interrupt the sequence")

    # ---- one list, not two ------------------------------------------------
    if "renderedSections(" not in tsx:
        problems.append(
            f"{TEMPLATE.name} does not call renderedSections(). The section list and "
            f"the nav list have to be one array or §8's 'nav entries equal rendered "
            f"sections' becomes something a reader has to verify by eye")
    if not re.search(r"<SectionNav\s+sections=\{sections\}", tsx):
        problems.append(
            f"{TEMPLATE.name} does not hand `sections` to SectionNav. Whatever it "
            f"hands over instead is a second list")

    # ---- every section is gated on `present` ------------------------------
    present = re.search(r"const present: Record<string, boolean> = \{(.*?)\n  \};", tsx, re.S)
    if not present:
        problems.append(
            f"{TEMPLATE.name} has no `present` map this gate can read. It is the one "
            f"place a section's existence is decided and the array the nav is built "
            f"from; if it has moved, this file has to move with it")
    else:
        keys = set(re.findall(r"^\s{4}([a-z_]+):", present.group(1), re.M))
        for missing in [s for s in spec if s not in keys]:
            problems.append(
                f'"{missing}" is in the sequence and has no entry in `present`, so the '
                f"page can never render it and the nav can never list it")
        for extra in sorted(keys - set(spec)):
            problems.append(
                f'`present` carries "{extra}", which is not a section in the sequence')
        for r in rendered:
            if r in spec and not re.search(rf"present\.{r}\b", tsx):
                problems.append(
                    f'section id="{r}" renders without being gated on present.{r}. A '
                    f"section outside the map is a section the nav cannot know about")

    if problems:
        print(f"check_section_order: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    order = " → ".join(seen)
    tail = f" then {', '.join(r for r in rendered if r in unnumbered)}" if unnumbered else ""
    print(f"check_section_order: OK — {len(seen)} of {len(spec)} sections render, "
          f"in sequence: {order}{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

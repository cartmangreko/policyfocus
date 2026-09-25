"""
The sector hub's section sequence, enforced.

    python3 check_section_order.py          # exits non-zero on any violation

WHAT IS BEING PROTECTED
=======================
The hub answers a fixed sequence of questions, and every sector asks them in the
same order so the interface is learned once. The sequence lives in
data/prose.json -> sector_sections, and this checks that the template renders it
-- the same ids, in the same order, with nothing on the page that the sequence
does not know about.

The failure this exists to catch is not somebody reordering the list on purpose.
It is the ordinary one: a section added to the component in the place it was
convenient to type it, six months after the specification said where it goes.

WHAT BRIEF 15 CHANGED HERE
==========================
The hub used to render nine literal <section> elements and this gate read them
off the tsx with one regex. It now renders TWO literal sections -- the map and
Sources -- and four BLOCKS, which are one component called over the array
lib/hub.ts returns. So the order is in two places and both are read:

    the map          a literal <section ... id="map"> in SectorMap.tsx
    the four blocks  the return order of hubBlocks() in lib/hub.ts
    sources          a literal <section ... id="sources">, last

A block that rendered outside hubBlocks() would be a block whose place in the
sequence nothing states, which is the thing this file exists to prevent.

NAV ENTRIES EQUAL RENDERED SECTIONS
===================================
That holds by construction rather than by inspection -- SectorMap.tsx computes
ONE list, `renderedSections()`, and hands the same array to SectionNav -- and
what is checked here is that the construction is still the one in place.

WHY IT READS THE SOURCE
=======================
The alternative is a render test, which needs a bundler, a DOM and the data
layer, to establish something the source states plainly. The parse here is
deliberately small and deliberately brittle: it recognises the exact shapes the
components use, and a rewrite that changes a shape fails loudly rather than
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
BLOCKS = ROOT / "web" / "lib" / "hub.ts"

# The one literal section element shape the template uses. Matching it exactly
# is the point: a section written any other way is not checked, and would be, if
# this accepted anything with an id on it.
SECTION = re.compile(r'<section className="tmap-section" id="([a-z-]+)">')

# The blocks, in the order hubBlocks() returns them. Its body is one return of
# an array literal of calls named <id>Block, which is the shape this reads.
HUB_BLOCKS = re.compile(r"export function hubBlocks\([^)]*\)[^{]*\{\s*return \[(.*?)\];", re.S)
BLOCK_CALL = re.compile(r"\b([a-z][A-Za-z]*)Block\(")


def block_order(src: str) -> list[str] | None:
    m = HUB_BLOCKS.search(src)
    if not m:
        return None
    return [re.sub(r"(?<!^)([A-Z])", r"-\1", n).lower() for n in BLOCK_CALL.findall(m.group(1))]


def main() -> int:
    prose = json.loads(PROSE.read_text(encoding="utf-8"))
    block = prose.get("sector_sections")
    if not block:
        print("check_section_order: data/prose.json has no sector_sections block")
        return 1

    spec = [s["id"] for s in block["sections"]]
    unnumbered = [u["id"] for u in block.get("unnumbered", [])]
    tsx = TEMPLATE.read_text(encoding="utf-8")
    hub = BLOCKS.read_text(encoding="utf-8")
    literal = SECTION.findall(tsx)
    problems: list[str] = []

    if not literal:
        problems.append(
            f"{TEMPLATE.name} renders no section this gate can see. It matches "
            f'<section className="tmap-section" id="..."> exactly; if the template '
            f"now writes them another way, teach this file the new shape rather "
            f"than leaving it matching nothing")

    # ---- the blocks -------------------------------------------------------
    blocks = block_order(hub)
    if blocks is None:
        problems.append(
            f"{BLOCKS.name} has no hubBlocks() returning an array of <id>Block() calls. "
            f"That array IS the order of the four blocks on the page; if it has moved, "
            f"this file has to move with it")
        blocks = []
    if not re.search(r"const blocks = hubBlocks\(", tsx):
        problems.append(
            f"{TEMPLATE.name} does not build its blocks with hubBlocks(). A page that "
            f"assembled them one at a time could render three of four, and a missing "
            f"block is a build failure")
    if not re.search(r"<HubBlock\b", tsx):
        problems.append(f"{TEMPLATE.name} renders no <HubBlock>, so no block reaches the page")

    # ---- the whole sequence, in one list ----------------------------------
    # The map (and any other literal numbered section) in the place the template
    # draws it, the blocks in hubBlocks() order, the unnumbered ones last.
    rendered = [r for r in literal if r in spec] + blocks
    seen = [r for r in rendered if r in spec]
    if len(set(seen)) != len(seen):
        dupes = sorted({r for r in seen if seen.count(r) > 1})
        problems.append(f"section(s) rendered twice: {', '.join(dupes)}")
    positions = [spec.index(r) for r in seen]
    if positions != sorted(positions):
        problems.append(
            f"sections render as {' -> '.join(seen)}; the sequence in data/prose.json "
            f"is {' -> '.join(spec)}. Every sector asks the same questions in the same "
            f"order, which is the whole of the fixed sequence")
    for missing in [s for s in spec if s not in seen]:
        problems.append(
            f'"{missing}" is in the sequence and nothing renders it. A question the '
            f"specification asks and the page does not is a question a reader is owed")

    # ---- nothing off the list ---------------------------------------------
    for r in rendered + literal:
        if r not in spec and r not in unnumbered:
            problems.append(
                f'section id="{r}" is neither one of the numbered questions nor one of '
                f"the unnumbered headings in data/prose.json. A section on this page "
                f"either answers a question the specification asks or is declared as "
                f"an exception to that, and there is one of those")

    # ---- the unnumbered ones come last ------------------------------------
    for i, r in enumerate(literal):
        if r in unnumbered and any(later in spec for later in literal[i + 1:]):
            problems.append(
                f'"{r}" is an unnumbered section and renders before a numbered one. '
                f"Sources closes the page; it does not interrupt the sequence")
    if unnumbered and literal and literal[-1] not in unnumbered:
        problems.append(
            f"the last literal section in {TEMPLATE.name} is \"{literal[-1]}\"; Sources "
            f"closes the page")

    # ---- one list, not two ------------------------------------------------
    if "renderedSections(" not in tsx:
        problems.append(
            f"{TEMPLATE.name} does not call renderedSections(). The section list and "
            f"the nav list have to be one array or 'nav entries equal rendered "
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
        for r in literal:
            if r in spec and not re.search(rf"present\.{r}\b", tsx):
                problems.append(
                    f'section id="{r}" renders without being gated on present.{r}. A '
                    f"section outside the map is a section the nav cannot know about")
        # The blocks are gated as a set, on the same map, in one expression.
        if blocks and not re.search(r"present\[block\.id\]", tsx):
            problems.append(
                f"the blocks render without being gated on `present`. They are always "
                f"present today, and the guard is what makes that a decision "
                f"{TEMPLATE.name} states rather than one HubBlock assumes")

    if problems:
        print(f"check_section_order: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    order = " -> ".join(seen)
    tail = f" then {', '.join(r for r in literal if r in unnumbered)}" if unnumbered else ""
    print(f"check_section_order: OK -- {len(seen)} of {len(spec)} sections render, "
          f"in sequence: {order}{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

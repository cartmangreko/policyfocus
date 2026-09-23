"""
The hub carries the top of a list and never the whole of one.

    python3 check_hub_list_duplication.py   # exits non-zero on any violation

WHAT IS BEING PROTECTED
=======================
Brief 15's reduction, stated as three properties:

  1  the hub never renders more than HUB_BLOCK_CAP items of any kind;
  2  the complete lists exist only on the spokes;
  3  every block link resolves to a spoke whose count equals the link's n.

The failure this exists to catch is the one the hub already had once: a section
added with its full list because the list was there and the page was the only
place to put it. The spokes exist now, so a complete list on the hub is a
decision somebody has to make rather than the default, and this is what makes it
one.

WHY IT CHECKS THE CONSTRUCTION AND NOT THE ARITHMETIC
=====================================================
Property 3 could be checked by counting rows in Python and comparing them with
what the page renders. That means a second implementation of every population --
which projects belong to a sector, which measures are in its view -- and two
implementations of a count are two counts that agree until they do not. So the
count is computed ONCE, in web/lib/hub.ts, and the spoke and the hub link read
the same function; what is checked here is that they still do.

Property 1 is checked the same way: every block's `items` is a slice of its
population at the one cap, and the cap is one constant in one place.

Property 2 is the brittle one, deliberately. SectorMap.tsx is allowed to iterate
an enumerated set of things, listed below with the reason each is not a complete
list of a block's population. Anything else it iterates fails, including
something harmless -- because the alternative is a gate that recognises "a list"
by heuristic, and a heuristic here would pass the exact thing this is for.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "web" / "lib" / "hub.ts"
SPOKES = ROOT / "web" / "lib" / "spokes.ts"
TEMPLATE = ROOT / "web" / "components" / "SectorMap.tsx"
BLOCK_COMPONENT = ROOT / "web" / "components" / "HubBlock.tsx"

# What the hub template may iterate, and why none of them is a complete list of
# a block's population.
ALLOWED_ITERATION = {
    "blocks": "the four blocks themselves, each already capped",
    "transitions": "the sector's transition labels, a fixed handful",
    "grouped": "the unnumbered Sources register, which is page-level and unchanged",
    "g.sources": "one publisher's sources inside that register",
    "orientation.split(/\\n\\s*\\n/)": "the reviewed context paragraph, rendered as "
                                       "its beats",
    "(geoFrame.undrawn?.rows ?? [])": "what the picture does not draw, inside a "
                                      "<details>, which is the one level of disclosure "
                                      "the hub keeps",
}

# A list RENDERED is a `.map(` inside the component's returned JSX. The ones in
# its working above the return -- building a lookup, counting a set of countries
# -- are not lists on the page and are not what this is about.
def rendered_iterations(src: str) -> set[str]:
    """What the returned JSX calls .map() on, as written.

    Read by walking BACKWARDS over a balanced expression rather than by a
    regex, because the expressions are real ones -- an optional chain with a
    default, a split on a regex literal -- and a regex that matched them would
    be matching a subset of JavaScript by eye."""
    cut = src.rindex("\n  return (")
    jsx = src[cut:]
    found: set[str] = set()
    for m in re.finditer(r"\.map\(", jsx):
        i, depth = m.start(), 0
        j = i - 1
        while j >= 0:
            c = jsx[j]
            if c in ")]":
                depth += 1
            elif c in "([":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and not (c.isalnum() or c in "_$.?"):
                break
            j -= 1
        found.add(jsx[j + 1:i].strip())
    return found


def main() -> int:
    hub = HUB.read_text(encoding="utf-8")
    spokes = SPOKES.read_text(encoding="utf-8")
    tsx = TEMPLATE.read_text(encoding="utf-8")
    block_tsx = BLOCK_COMPONENT.read_text(encoding="utf-8")
    problems: list[str] = []

    # ---- 1. one cap, applied to every block -------------------------------
    caps = re.findall(r"export const HUB_BLOCK_CAP = (\d+);", hub)
    if len(caps) != 1:
        problems.append(
            f"HUB_BLOCK_CAP is declared {len(caps)} times in {HUB.name}. It is one "
            f"value in one place so that changing it is one change")
    elsewhere = [
        p.name for p in (TEMPLATE, BLOCK_COMPONENT, SPOKES)
        if re.search(r"HUB_BLOCK_CAP\s*=", p.read_text(encoding="utf-8"))
    ]
    for name in elsewhere:
        problems.append(f"{name} declares a cap of its own; there is one cap")

    blocks = re.findall(r"export function ([a-z][A-Za-z]*)Block\(slug: string\): HubBlock \{(.*?)\n\}",
                        hub, re.S)
    if not blocks:
        problems.append(
            f"{HUB.name} has no <id>Block(slug) functions this gate can see. They are "
            f"where the cap is applied; if they have moved, this file moves with them")
    for name, body in blocks:
        if not re.search(r"items:.*?\.slice\(0, HUB_BLOCK_CAP\)", body, re.S):
            problems.append(
                f"{name}Block does not cut its items with .slice(0, HUB_BLOCK_CAP). A "
                f"block that caps itself another way is a block that can stop capping "
                f"itself")

    # ---- 2. the complete lists are not on the hub -------------------------
    for expr in rendered_iterations(tsx):
        if expr not in ALLOWED_ITERATION:
            problems.append(
                f"{TEMPLATE.name} iterates `{expr}`, which is not one of the things "
                f"the hub may list: "
                + "; ".join(f"{k} ({v})" for k, v in ALLOWED_ITERATION.items())
                + ". A complete list belongs on a spoke")
    if "<table" in tsx:
        problems.append(
            f"{TEMPLATE.name} renders a table. The project register's table is the "
            f"spoke's; the hub carries the top five rows of it")
    if re.search(r"\.slice\(0,\s*(?!HUB_BLOCK_CAP)", tsx):
        problems.append(
            f"{TEMPLATE.name} caps a list with a number of its own. Every cap on this "
            f"page is HUB_BLOCK_CAP")

    # ---- 3. the link resolves to a spoke, and the counts are one call -----
    spoke_ids = re.findall(r'^\s*"([a-z]+)",$', re.search(
        r"export const SPOKE_IDS = \[(.*?)\] as const;", spokes, re.S).group(1), re.M) \
        if re.search(r"export const SPOKE_IDS = \[(.*?)\] as const;", spokes, re.S) else []
    if not spoke_ids:
        problems.append(f"{SPOKES.name} has no SPOKE_IDS this gate can read")
    for name, body in blocks:
        hrefs = re.findall(r"href: `/sectors/\$\{slug\}/([a-z]+)", body)
        if not hrefs:
            problems.append(
                f"{name}Block renders no link to a spoke. A block whose complete list "
                f"is nowhere is a block that has to carry it")
            continue
        for h in hrefs:
            if h not in spoke_ids:
                problems.append(
                    f'{name}Block links to /sectors/<slug>/{h}, which is not a spoke')
        if not re.search(r'label: `All \$\{', body) and not re.search(r'label: `All ', body):
            problems.append(
                f'{name}Block\'s link is not in the fixed form "All {{n}} ...". The '
                f"form is what tells a reader the hub is showing them part of "
                f"something")

    # THE COUNTS ARE ONE CALL. Every population the spoke lists is the function
    # the block was built from; spokeCount() is the one place that mapping is
    # written, and the blocks read the same functions.
    populations = set(re.findall(r"export function (sector[A-Za-z]+)\(", hub))
    used_by_spokes = set(re.findall(r"\b(sector[A-Za-z]+)\(slug\)", spokes))
    for pop in sorted(populations - used_by_spokes - {"sectorSupportRows"}):
        problems.append(
            f"{HUB.name} exports {pop}() and {SPOKES.name} does not use it. A "
            f"population the hub counts and the spoke does not read is two counts")
    if "export function spokeCount" not in spokes:
        problems.append(
            f"{SPOKES.name} has no spokeCount(). It is the n in every block link and "
            f"the length of every spoke, and it is one function so it is one number")

    # ---- the block component holds no list of its own ---------------------
    if not re.search(r"block\.items\.map\(", block_tsx):
        problems.append(
            f"{BLOCK_COMPONENT.name} does not render block.items. Whatever it renders "
            f"instead is a list nothing capped")

    if problems:
        print(f"check_hub_list_duplication: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    print(f"check_hub_list_duplication: OK -- {len(blocks)} blocks, all cut at "
          f"HUB_BLOCK_CAP={caps[0]}, each linking to one of "
          f"{len(spoke_ids)} spokes; the hub lists nothing else")
    return 0


if __name__ == "__main__":
    sys.exit(main())

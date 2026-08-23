"""
The colour layers, enforced.

    python3 check_colour_layers.py          # exits non-zero on any violation

FOUR LAYERS, AND WHY THEY ARE CONFINED
======================================
Colour on this site had drifted into meaning several things at once. Claret was
the burden hue, the brand rule, the link accent and the hover state; pine was
relief, the logomark, a readiness level and a confidence chip. When one colour
means four things it means nothing, and the specific casualty is the only
reading that has to survive: which way the money points.

So each layer is confined, and the confinement is checked:

  SIGNAL BLUE      brand and chrome only -- the seam in the logotype, the brand
                   rule, focus rings, interactive accents. Never data.

  CLARET / PINE    direction only. Cost and support on a euro figure; burden and
                   relief on a duty. Amendment brief 3 rules these one axis --
                   something lands on the firm, or it comes to it -- whatever
                   the unit. Never decoration, never identity, never a status,
                   a readiness, a confidence or a material type, all of which
                   borrowed them and none of which is a direction.

  DIAGRAM PALETTE  inside diagrams only, and disjoint from the three reserved
                   colours by construction. A diagram element that shows money
                   direction -- a measure node's cost line, an edge badge --
                   borrows claret or pine FOR THAT ELEMENT and nothing else.

  SECTOR ACCENTS   page-level identity: the photo duotone wash, a section
                   marker, the what-moved marks on that sector's own page.
                   Never on a figure, never on a diagram node.

Ochre is gone. It had no chrome role left once the focus token became signal
blue, and every remaining use was data -- a pending flag, an unresolved diff, an
override note -- which is the layer it is no longer allowed in.

HOW CLARET AND PINE ARE CHECKED
===============================
By naming, which is the only method that survives a refactor. A CSS rule may
emit claret or pine only if its selector NAMES A DIRECTION: one of the markers
in DIRECTION_MARKERS below appears in the selector. `.tag-neg`, `.led-add`,
`.netpos-row.is-neg`, `.tdir.cost` all say what they are; `.record-kind` and
`.crumb-link` do not, and that is exactly the drift this catches.

The convention is load-bearing rather than cosmetic: a component that wants the
direction hue has to say which direction it is showing, in the class name, where
the next reader will see it.

THE NUMERIC CHECK
=================
Every diagram and accent token is measured against claret, pine, signal and ink
in CIE L*a*b*, and must clear MIN_DELTA. This is what "disjoint" means when it
is checked rather than asserted: --acc-auto was #7c414a, which is 12 units from
claret and would have put a claret-coloured marker on the automotive page,
next to figures where claret means cost.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import colour

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "web" / "app" / "globals.css"
COMPONENTS = (ROOT / "web" / "components", ROOT / "web" / "app")

# CIE76. 30 is comfortably "a reader names these two colours differently";
# the palette is chosen with margin, so a value that only just clears is a
# value somebody nudged without re-reading this file.
MIN_DELTA = 30.0

RESERVED = ("--claret", "--pine", "--signal")

# A selector may emit claret or pine only if it names the direction it is
# showing. Kept explicit rather than clever: every entry is a word that appears
# in a class name and means one side of the axis.
DIRECTION_MARKERS = (
    "is-neg", "is-pos", "-neg", "-pos", "-add", "-rem",
    "cost", "support", "burden", "relief", "worsens", "relieves",
    "netpos", "tnet",
)

# Where signal blue is allowed: brand and chrome. Everything else is data.
CHROME_MARKERS = (
    "brand", "focus-visible", "focus", "wordmark", "mark-", "logomark",
    "source-link", "section-link", "backlink", "crumb", "seam", "ticker-dot",
    "selection",
    "searchbar", "query-arrow", "skip-link", "sector-live", "signin",
)

# Where the diagram palette is allowed. The diagram, the ego graph, the finding
# diagrams -- pictures, and nothing that is not a picture.
DIAGRAM_MARKERS = ("tdiagram", "tnode", "tedge", "ego-", "diagram", "fdiag")

# Where a sector accent is allowed: page identity. Never a figure.
ACCENT_MARKERS = (
    "sector-icon", "sector-map", "accent", "acc-", "tmap-head", "wash",
    "moved", "band-accent", "tmap-transitions",
)

# Files allowed to name a colour token inline rather than through a class. Each
# one draws SVG, where a stroke is an attribute and there is no stylesheet to
# put it in.
INLINE_ALLOWED = {
    "TransitionDiagram.tsx",
    "EgoGraph.tsx",
    "FindingDiagram.tsx",
    "DriverChart.tsx",
    "SectorIcon.tsx",
    "Logomark.tsx",
    "Mark.tsx",
}


def read_tokens(css: str) -> dict[str, str]:
    """The :root custom properties, as a name -> hex map. Only literal hex
    values: an alias (`--focus: var(--signal)`) is resolved by following it."""
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not root:
        raise SystemExit("check_colour_layers: no :root block in globals.css")
    raw: dict[str, str] = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", root.group(1)):
        raw[name] = value.strip()
    tokens: dict[str, str] = {}
    for name, value in raw.items():
        seen = set()
        while value.startswith("var(") and name not in seen:
            seen.add(name)
            inner = value[4:].split(",")[0].strip().rstrip(")")
            value = raw.get(inner, "").strip()
        if re.fullmatch(r"#[0-9a-fA-F]{3,8}", value):
            tokens[name] = value
    return tokens


def rules(css: str) -> list[tuple[str, str]]:
    """(selector, body) for every rule, comments stripped. At-rule blocks are
    flattened, which is fine here: the question is which selector emits which
    colour, and a media query does not change the answer."""
    stripped = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    return [(" ".join(sel.split()), body)
            for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", stripped)]


def uses(body: str, token: str) -> bool:
    return f"var({token})" in body


def main() -> int:
    css = CSS.read_text(encoding="utf-8")
    tokens = read_tokens(css)
    problems: list[str] = []

    # ---- ochre is retired -------------------------------------------------
    if any(name.startswith("--ochre") for name in tokens):
        problems.append(
            "--ochre is still declared. It is retired: it had no chrome role "
            "left once the focus token became signal blue, and every other use "
            "was data")
    for sel, body in rules(css):
        if uses(body, "--ochre"):
            problems.append(f"{sel}: uses --ochre, which is retired")

    # ---- the numeric check ------------------------------------------------
    anchors = {n: tokens[n] for n in ("--claret", "--pine", "--signal", "--ink")
               if n in tokens}
    missing = [n for n in ("--claret", "--pine", "--signal", "--ink") if n not in anchors]
    if missing:
        problems.append(f"missing anchor token(s) {missing} — the disjointness check "
                        f"cannot run without them")
    measured = {n: v for n, v in tokens.items()
                if n.startswith(("--dg-", "--acc-"))}
    for name, value in sorted(measured.items()):
        for anchor, avalue in anchors.items():
            d = colour.distance(value, avalue)
            if d < MIN_DELTA:
                problems.append(
                    f"{name} ({value}) is {d:.0f} from {anchor} ({avalue}), under the "
                    f"{MIN_DELTA:.0f} this file requires — a reader would take it for "
                    f"{anchor.lstrip('-')}")
    dg = sorted(n for n in measured if n.startswith("--dg-"))
    for i, a in enumerate(dg):
        for b in dg[i + 1:]:
            d = colour.distance(measured[a], measured[b])
            if d < MIN_DELTA:
                problems.append(f"{a} and {b} are {d:.0f} apart; the diagram needs its "
                                f"kinds told apart at a glance")

    # ---- layer confinement in CSS ----------------------------------------
    def confined(sel: str, markers: tuple[str, ...]) -> bool:
        low = sel.lower()
        return any(m in low for m in markers)

    for sel, body in rules(css):
        if sel.strip().startswith(("@", ":root")):
            continue
        for token in ("--claret", "--claret-soft", "--claret-lift",
                      "--pine", "--pine-soft"):
            if uses(body, token) and not confined(sel, DIRECTION_MARKERS):
                problems.append(
                    f"{sel}: emits {token} without naming a direction. Claret and pine "
                    f"are the direction layer; a selector that wants one has to say "
                    f"which side it is showing")
        if uses(body, "--signal") and not confined(sel, CHROME_MARKERS):
            problems.append(f"{sel}: emits --signal outside brand and chrome")
        for name in measured:
            if not uses(body, name):
                continue
            if name.startswith("--dg-") and not confined(sel, DIAGRAM_MARKERS):
                problems.append(f"{sel}: emits {name} outside a diagram")
            if name.startswith("--acc-") and confined(sel, DIAGRAM_MARKERS):
                problems.append(f"{sel}: puts a sector accent on a diagram element")

    # ---- inline colour in components -------------------------------------
    for directory in COMPONENTS:
        for path in sorted(directory.rglob("*.tsx")):
            if path.name in INLINE_ALLOWED:
                continue
            text = path.read_text(encoding="utf-8")
            for token in RESERVED + ("--ochre",):
                if f"var({token})" in text:
                    problems.append(
                        f"{path.relative_to(ROOT)}: names {token} inline. Colour lives in "
                        f"globals.css, where the gate can see which selector emits it")
            for m in re.finditer(r"#[0-9a-fA-F]{6}\b", text):
                problems.append(f"{path.relative_to(ROOT)}: literal colour {m.group(0)} — "
                                f"use a token")

    if problems:
        print(f"check_colour_layers: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    print(f"check_colour_layers: OK — {len(dg)} diagram hues and "
          f"{len(measured) - len(dg)} sector accents, all clear of claret, pine, "
          f"signal and ink by {MIN_DELTA:.0f} deltaE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

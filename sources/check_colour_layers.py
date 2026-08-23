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
import design_tokens

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "web" / "app" / "globals.css"
COMPONENTS = (ROOT / "web" / "components", ROOT / "web" / "app")

# CIE76. 30 is comfortably "a reader names these two colours differently";
# the palette is chosen with margin, so a value that only just clears is a
# value somebody nudged without re-reading this file.
MIN_DELTA = 30.0

# WCAG AA for body text. Not 3.0: almost everything measured here is small —
# 11px monospace as-of dates, 13px captions — and the large-text allowance does
# not apply to any of it.
MIN_CONTRAST = 4.5

# The ground type is read against. Everything defaults to the page; the
# selectors below sit on a fill of their own and are measured against that.
#
# A DECLARED LIST RATHER THAN A RESOLVER. Working out which ancestor painted
# the background behind a given rule is a layout question, and this file should
# not pretend to answer one. Six selectors put type on something other than
# paper; they are named here, and a seventh that appears without being added
# will be measured against paper and fail loudly, which is the right way round.
KNOCKOUT_GROUNDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("site-footer", "footer-", "wordmark-dark"), "--ink"),
    (("searchbar-submit",), "--ink"),
    (("led-count",), "--claret"),          # the lighter of the two bar fills
    (("diagram-node-act",), "--rule-dark"),
    (("selection",), "--signal"),
)

# Rungs that are no longer type. They are hairlines, hover borders, timeline
# dots and fill bars — a contrast ratio is not the question being asked of
# them, and the moment one is used as a `color:` it becomes the question and
# the answer is no. See the ink block in globals.css.
NON_TEXT_TOKENS = ("--ink-40", "--ink-25")

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
    tokens = design_tokens.tokens()
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

    def confined(sel: str, markers: tuple[str, ...]) -> bool:
        low = sel.lower()
        return any(m in low for m in markers)

    # ---- layer confinement in CSS ----------------------------------------
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

    # ---- contrast -------------------------------------------------------
    # Every colour set as type has to be readable on the ground it is set on.
    # This is the check that would have caught --ink-40 carrying every as-of
    # date on the site at 3.16:1, which no amount of palette discipline does:
    # the four layers are about what a colour MEANS, and this is about whether
    # anybody can read it.
    if "--paper" in tokens:
        for sel, body in rules(css):
            if sel.strip().startswith(("@", ":root")):
                continue
            # `color` exactly — not border-color, not outline-color, both of
            # which end in the same six letters and are not type.
            if "currentcolor" in body.lower():
                # The rule is setting `color` as a carrier for something else to
                # inherit — a gradient, a border, an SVG stroke. Nothing here is
                # read as words.
                continue
            for m in re.finditer(r"(?:^|[;{\s])color\s*:\s*[^;]*var\((--[\w-]+)\)", body):
                name = m.group(1)
                ground_token = "--paper"
                for markers, token in KNOCKOUT_GROUNDS:
                    if confined(sel, markers):
                        ground_token = token
                        break
                knockout = ground_token != "--paper"
                if name in NON_TEXT_TOKENS and not knockout:
                    problems.append(
                        f"{sel}: sets type in {name}, which is not a type colour. Muted "
                        f"type is --ink-55, and there is one of it")
                    continue
                if name.startswith(("--acc-", "--dg-")) or name == "--accent":
                    problems.append(
                        f"{sel}: sets type in {name}. A sector accent is a mark and a "
                        f"diagram hue is a fill; neither is a colour to read words in")
                    continue
                if name not in tokens:
                    continue
                if ground_token not in tokens:
                    problems.append(f"{sel}: declared ground {ground_token} is not a token")
                    continue
                got = colour.contrast(tokens[name], tokens[ground_token])
                if got < MIN_CONTRAST:
                    problems.append(
                        f"{sel}: {name} ({tokens[name]}) is {got:.2f}:1 on "
                        f"{ground_token.lstrip('-')}, under the {MIN_CONTRAST} AA wants "
                        f"for small text")

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
          f"signal and ink by {MIN_DELTA:.0f} deltaE; every type colour clears "
          f"{MIN_CONTRAST}:1 on its ground")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

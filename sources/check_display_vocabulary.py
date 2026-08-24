"""
Report the banned words in hand-written surface copy.

    python3 check_display_vocabulary.py            # always exits 0
    python3 check_display_vocabulary.py --strict   # exits 1 on any hit

WHY THIS REPORTS AND DOES NOT FAIL
==================================
The two lists in sources/display_vocabulary.py ban for different reasons, and
only one of them can be automated.

The internal list ("row", "valence", "docket") is decidable: those words have no
business on a page, ever. The brand list is not. "Plant" is banned when the site
uses it to say what it is for and correct inside the name of an installation;
"map" is banned as the name of the product and fine as the name of a picture;
"change record" is the name of one content tier and nothing else. A gate that
failed on the word would be a gate that made pages lie about installations to
stay green.

So the generators check hard -- build_sector_diagram.py refuses a label,
check_sector_schema.py refuses a labels file -- because a template has no
judgement to exercise, and this reports, because a sentence somebody wrote does.
The list is short enough to read on every build, and a hit that survives review
is a hit somebody has decided about.

--strict exists for the day the list is clean and somebody wants it to stay
clean; it is not wired into the prebuild.

WHAT IT READS
=============
The audience surfaces: every .tsx under web/app and web/components, and the
reviewed prose in data/prose.json. Comments are stripped first -- an internal
note explaining why a word is banned should not itself be a violation -- and so
are the attributes that carry no copy (className, href, and the rest), the
`${...}` slots inside template literals, and anything shaped like a module path,
a file name or a class list — because a CSS class named `sector-map` is a name in
the codebase, not a word on a page.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import display_vocabulary as dv

ROOT = Path(__file__).resolve().parent.parent
SURFACE_DIRS = (ROOT / "web" / "app", ROOT / "web" / "components")
PROSE = ROOT / "data" / "prose.json"

_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_JSX_COMMENT = re.compile(r"\{\s*/\*.*?\*/\s*\}", re.DOTALL)

# Attributes that carry identifiers rather than copy. Their values are names in
# this codebase and are allowed to say whatever the codebase calls the thing.
_NON_COPY_ATTRS = (
    "className|href|id|key|rel|target|type|src|xmlns|viewBox|d|fill|stroke|"
    "variable|subsets|weight|display|htmlFor|role|style|width|height|refX|refY|"
    "markerWidth|markerHeight|orient|x|y|rx"
)
_ATTR = re.compile(rf'\b({_NON_COPY_ATTRS})=\{{?["\'`][^"\'`]*["\'`]\}}?')

_STRING = re.compile(r'"([^"\n]{4,})"|\'([^\'\n]{4,})\'|`([^`]{4,})`')
_JSX_TEXT = re.compile(r">([^<>{}]{4,})<")

# Inside a template literal, ${...} is code. It is spliced out rather than
# checked, so `${named.map(...)}` stops reading as the word "map".
_SLOT = re.compile(r"\$\{[^{}]*\}")

# Not copy: module paths, file names, CSS class lists, custom properties. Each
# of these is a name in this codebase, and the codebase is allowed to call a
# picture a map.
_NOT_COPY = (
    re.compile(r"^[@./]"),                       # @/lib/records, ./globals.css
    re.compile(r"\.(json|css|svg|tsx|ts)$"),
    re.compile(r"^--?[\w-]+$"),                  # --acc-cement
    re.compile(r"^[a-z0-9]+([-_ :][a-z0-9]+)*$"),  # exp-row is-other, eur_per_tonne
    re.compile(r"[<>{}();]|=>"),                 # code the JSX scan swept up
)


def is_copy(text: str) -> bool:
    return not any(p.search(text) for p in _NOT_COPY)


def strings_in(source: str) -> list[str]:
    source = _JSX_COMMENT.sub(" ", source)
    source = _BLOCK_COMMENT.sub(" ", source)
    source = _LINE_COMMENT.sub("", source)
    source = _ATTR.sub(" ", source)
    out: list[str] = []
    for m in _STRING.finditer(source):
        out.append(next(g for g in m.groups() if g is not None))
    for m in _JSX_TEXT.finditer(source):
        out.append(m.group(1))
    cleaned = (_SLOT.sub(" ", t).strip() for t in out)
    return [t for t in cleaned if len(t) >= 4 and is_copy(t)]


def prose_strings() -> list[tuple[str, str]]:
    """Reviewed prose, block by block. `_comment` is internal documentation and
    is skipped for the same reason source comments are."""
    doc = json.loads(PROSE.read_text(encoding="utf-8"))
    out: list[tuple[str, str]] = []

    def walk(where: str, node) -> None:
        if isinstance(node, str):
            out.append((where, node))
        elif isinstance(node, dict):
            for k, v in node.items():
                if k in ("_comment", "status", "reviewed"):
                    continue
                walk(f"{where}.{k}", v)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(f"{where}[{i}]", v)

    for block, node in doc.items():
        if block == "_comment":
            continue
        walk(block, node)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    hits: list[str] = []
    for directory in SURFACE_DIRS:
        for path in sorted(directory.rglob("*.tsx")):
            rel = path.relative_to(ROOT)
            for text in strings_in(path.read_text(encoding="utf-8")):
                bad = dv.violations(text)
                if bad:
                    snippet = text if len(text) <= 88 else text[:87] + "…"
                    hits.append(f"  {rel}: {sorted(set(bad))} — {snippet}")

    for where, text in prose_strings():
        bad = dv.violations(text)
        if bad:
            snippet = text if len(text) <= 88 else text[:87] + "…"
            hits.append(f"  data/prose.json {where}: {sorted(set(bad))} — {snippet}")

    if not hits:
        print("check_display_vocabulary: clean")
        return 0

    print(f"check_display_vocabulary: {len(hits)} to review — reported, not failed "
          f"(see the module docstring for why):")
    print("\n".join(hits))
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())

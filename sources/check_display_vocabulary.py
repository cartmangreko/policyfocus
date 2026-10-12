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
The audience surfaces: every .tsx under web/app and web/components, the .ts
under web/lib -- which is where web/lib/prose.ts words every computed sentence
on the site -- and the reviewed prose in data/prose.json. Comments are stripped first -- an internal
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
# WHAT COUNTS AS A SURFACE, and web/lib is one — added 12 October 2026.
#
# It was web/app and web/components, which is where the MARKUP is, and that
# missed the one file where every computed sentence on this site is actually
# worded: web/lib/prose.ts opens by saying it is "the ONLY place these sentences
# are worded", and nothing was reading it. The sentence over every picture, the
# summary prose, the arrival line and the no-location paragraph are all in there.
# The miss was found the way these are usually found — by writing a new sentence
# with "rows" in it and having nothing object.
#
# web/lib IS MOSTLY NOT COPY, and that is handled rather than worked around: the
# filters below already strip comments, non-copy attributes, module paths and
# template slots, which is what leaves a data loader's field names alone while
# catching the sentence a template builds out of them.
SURFACE_DIRS = (ROOT / "web" / "app", ROOT / "web" / "components", ROOT / "web" / "lib")
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

_JSX_TEXT = re.compile(r">([^<>{}]{4,})<")

# THE LITERALS ARE SCANNED, NOT MATCHED BY A REGEX, and that is a correction
# rather than a refinement — 12 October 2026.
#
# WHAT THE REGEX DID. It was
#
#     r'"([^"\n]{4,})"|\'([^\'\n]{4,})\'|`([^`]{4,})`'
#
# and the backtick alternative pairs the NEAREST two backticks, which in
#
#     `one sentence. ` +
#     `and the next one.`
#
# are the CLOSING backtick of the first literal and the OPENING backtick of the
# second. So the thing captured is the glue — "` + `" — and the literals
# themselves are skipped, alternately, all the way down a concatenation chain.
# Every other sentence in a multi-line template was invisible to this gate.
#
# HOW IT WAS FOUND. web/lib was added to the surfaces on this pass, and
# web/lib/prose.ts — which opens by saying it is "the ONLY place these sentences
# are worded" — reported two hits. The paragraph a reader meets on every
# unplaced project's page says "this register holds no position for it", and
# `register` is on the brand list, and the gate said nothing about it. It is in
# the second half of a `+` chain.
#
# A SCANNER CANNOT HAVE THAT CLASS OF BUG. It walks the source once, knows which
# kind of quote it is inside, honours a backslash escape, and closes a literal
# only on its own quote character. The cost is thirty lines of Python against
# one line of regex, and the benefit is that the gate sees every string instead
# of half of them.
_QUOTES = "\"'`"


def _literals(source: str) -> list[str]:
    """Every string literal in a TypeScript source, in order.

    Not a parser. It does not know a regex literal from a division, and it does
    not need to: a `/` outside a string is passed over, and the comment strippers
    have already run. What it is careful about is the three quote characters and
    the backslash, which is the whole of what the old regex got wrong.
    """
    out: list[str] = []
    i, n = 0, len(source)
    while i < n:
        ch = source[i]
        if ch not in _QUOTES:
            i += 1
            continue
        quote, i, start = ch, i + 1, i + 1
        while i < n:
            c = source[i]
            if c == "\\":
                i += 2
                continue
            if c == quote:
                break
            # An unterminated single or double quote ends at the newline, which
            # is what the language says and what keeps an apostrophe in a
            # comment the strippers missed from swallowing the rest of the file.
            if c == "\n" and quote != "`":
                break
            i += 1
        if i < n and source[i] == quote:
            out.append(source[start:i])
        i += 1
    return out

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
    out: list[str] = _literals(source)
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
        # .ts AS WELL AS .tsx, because web/lib has no markup in it and is where
        # the sentences are. A test file is excluded: its strings are assertion
        # messages addressed to whoever broke the build, not copy addressed to a
        # reader, and "a measure page follows its own lead block" is a test name.
        files = [p for p in directory.rglob("*.tsx")]
        files += [p for p in directory.rglob("*.ts") if ".test." not in p.name]
        files += [p for p in directory.rglob("*.mts") if ".test." not in p.name]
        for path in sorted(files):
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

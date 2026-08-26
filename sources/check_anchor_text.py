"""
No anchor on this site reads out a URL.

    python3 check_anchor_text.py            # exits non-zero on any violation

Run AFTER the build, over the pages the build wrote, because this is a question
about what a reader sees and the only honest place to ask it is the rendered
HTML. A source-level version would have to know which expression ends up as
anchor text in every component on the site, and would answer for the components
it knew about.

THE RULE, AND WHY IT IS THIS BLUNT
==================================
Anchor text may not begin with `http` and may not contain a `?`.

Both halves catch the same failure, which is a link whose text is its own
address. It reached the sector page through `title ?? url`: every source
attached to a parameter carries no title, so the fallback ran, and the Sources
block printed a 214-character Eurostat Comext call -- eight query parameters,
none of them readable -- where a citation belongs. A reader could not tell from
it what had been asked of the dataset, which is the one thing the citation is
for.

The `?` half is the sharper of the two, and it is deliberately not limited to
strings that look like URLs: a question mark in anchor text is almost always a
query string that escaped, and a link whose text is a genuine question is rare
enough that the day one appears is a day worth having the conversation rather
than a day this gate should have stayed quiet. If that day comes, the fix is a
narrow allowance with the page named in it, not a softened rule.

The URL belongs in href. It is already there; that is what an anchor is.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "web" / ".next" / "server" / "app"

ANCHOR = re.compile(r"<a\b[^>]*>(.*?)</a>", re.S)
TAG = re.compile(r"<[^>]+>")


def text_of(anchor_inner: str) -> str:
    """What a reader reads: markup stripped, entities resolved, whitespace
    collapsed. An anchor wrapping an image reads as nothing and is not a
    violation -- it is a picture, and it has alt text for the question this
    gate is not asking."""
    return " ".join(html.unescape(TAG.sub(" ", anchor_inner)).split())


def main() -> int:
    if not PAGES.is_dir():
        print(f"check_anchor_text: no build at {PAGES.relative_to(ROOT)} — run this "
              f"after `next build`, not before it")
        return 1

    problems: list[str] = []
    pages = 0
    anchors = 0
    for page in sorted(PAGES.rglob("*.html")):
        pages += 1
        markup = page.read_text(encoding="utf-8", errors="replace")
        for inner in ANCHOR.findall(markup):
            text = text_of(inner)
            if not text:
                continue
            anchors += 1
            where = page.relative_to(PAGES)
            if text.lower().startswith("http"):
                problems.append(
                    f"{where}: anchor reads {text[:90]!r} — that is an address, not a "
                    f"citation. The URL is in href already")
            elif "?" in text:
                problems.append(
                    f"{where}: anchor reads {text[:90]!r} — a query string in the text "
                    f"of a link")

    if problems:
        # One page can carry the same bad anchor many times; the set is what a
        # reader has to fix.
        unique = sorted(set(problems))
        print(f"check_anchor_text: {len(unique)} violations\n")
        for p in unique[:40]:
            print(f"  {p}")
        if len(unique) > 40:
            print(f"  … and {len(unique) - 40} more")
        return 1

    print(f"check_anchor_text: OK — {anchors} anchors with text across {pages} pages, "
          f"none of them reading out a URL")
    return 0


if __name__ == "__main__":
    sys.exit(main())

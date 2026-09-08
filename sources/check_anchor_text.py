"""
No anchor on this site reads out a URL.

    python3 check_anchor_text.py            # exits non-zero on any violation

Run AFTER the build, over the pages the build wrote, because this is a question
about what a reader sees and the only honest place to ask it is the rendered
HTML. A source-level version would have to know which expression ends up as
anchor text in every component on the site, and would answer for the components
it knew about.

THE RULE
========
Anchor text may not be URL-SHAPED: it may not begin with `http`, may not contain
`://`, and may not carry a `?key=value` pair.

All three catch one failure, which is a link whose text is its own address. It
reached the sector page through `title ?? url`: every source attached to a
parameter carries no title, so the fallback ran, and the Sources block printed a
214-character Eurostat Comext call -- eight query parameters, none of them
readable -- where a citation belongs. A reader could not tell from it what had
been asked of the dataset, which is the one thing the citation is for.

THE DAY THIS RULE SAID IT WOULD COME, CAME. The `?` half used to be blunt: any
question mark in anchor text failed, on the reasoning that a genuine question in
a link was rare enough to be worth a conversation. The conversation is this
paragraph. Batteries International titled a piece "Battery gigafactories --
facing a temporary dip or a full-scale crisis?", the Italvolt row cites it, and
the gate called a verbatim title a query string.

TITLES ARE VERBATIM AND STAY. A citation quotes a publisher's title rather than
editing it -- that rule is older than this one and it wins -- so the gate is
narrowed to the shape it was always aiming at. A query string in prose is
`?key=value`; a question is a sentence that ends in a mark. The narrowing does
not soften what it was for: every URL that ever tripped this gate still trips it,
which is what `self_check` below exists to prove on every run.

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

# A QUERY PAIR, which is the thing a query string is made of: a question mark,
# a key, an equals sign. `?product=252310` matches and "a full-scale crisis?"
# does not, because a question ends where the sentence does. The key charset is
# what URLs actually use for one, brackets included -- Comext writes
# `?filter[time]=2025` -- and deliberately excludes the space, so a question
# followed by another sentence cannot be read as a pair.
QUERY_PAIR = re.compile(r"\?[A-Za-z0-9_%.\[\]-]+=")


def url_shaped(text: str) -> bool:
    """Whether this reads as an address rather than as a citation.

    Three tests and no fourth. A scheme at the front, a scheme separator
    anywhere, or a query pair. Each is a thing only a URL does; none of them is
    a thing a title does, which is the whole distinction this gate turns on.
    """
    lowered = text.lower()
    return (lowered.startswith("http")
            or "://" in lowered
            or bool(QUERY_PAIR.search(text)))


# WHAT THE RULE MUST AND MUST NOT CATCH, run on every invocation. A narrowed
# rule is only as good as the cases it was narrowed against, and a gate whose
# fixtures live in a test file nobody runs in CI is a gate that will be widened
# again by the next person in a hurry. These run before the pages are read, so
# a build fails on the rule before it can fail on the data.
MUST_FAIL = [
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DS-045409"
    "?format=JSON&flow=1&product=252310&reporter=EU27_2020&time=2025",
    "http://en.calb-tech.com/news_detail/5.html",
    "www.example.org/path?flow=1",
    "ec.europa.eu/eurostat?product=252310",
    "HTTPS://WWW.EUFABRIC.EU/sitemap.xml",
    "see https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20250731",
]
MUST_PASS = [
    # The title that forced the narrowing, verbatim.
    "Battery gigafactories — facing a temporary dip or a full-scale crisis?",
    "What is a low-carbon product?",
    "Hvilken plan gjelder for eiendommen min?",
    "Who pays for the transition? A note on the green premium",
    "Cement — Energy System",
    "Resolución de 17 de mayo de 2023, autorización ambiental integrada",
]


def self_check() -> list[str]:
    """Every fixture through the rule. Returns the failures."""
    out = []
    for text in MUST_FAIL:
        if not url_shaped(text):
            out.append(f"must fail and does not: {text[:70]!r}")
    for text in MUST_PASS:
        if url_shaped(text):
            out.append(f"must pass and does not: {text[:70]!r}")
    return out


def text_of(anchor_inner: str) -> str:
    """What a reader reads: markup stripped, entities resolved, whitespace
    collapsed. An anchor wrapping an image reads as nothing and is not a
    violation -- it is a picture, and it has alt text for the question this
    gate is not asking."""
    return " ".join(html.unescape(TAG.sub(" ", anchor_inner)).split())


def main() -> int:
    broken = self_check()
    if broken:
        print(f"check_anchor_text: the rule itself is wrong ({len(broken)} fixture(s))\n")
        print("\n".join(f"  {b}" for b in broken))
        return 1

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
            if url_shaped(text):
                problems.append(
                    f"{where}: anchor reads {text[:90]!r} — that is an address, not a "
                    f"citation. The URL is in href already")

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
          f"none of them reading out a URL "
          f"({len(MUST_FAIL)} address fixtures still caught, {len(MUST_PASS)} titles "
          f"still allowed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

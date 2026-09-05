"""
Tests for the anchor-text gate, and for the narrowing that a verbatim title
forced.

    python3 test_check_anchor_text.py

WHAT IS UNDER TEST. `url_shaped` decides whether a link's text is an address
rather than a citation, and it was widened once and narrowed once. The widening
is easy to keep: every URL that ever tripped this gate has to keep tripping it.
The narrowing is the fragile half — a title that ends in a question mark is a
title — so the cases below hold both sides at once, and the gate runs the same
fixtures itself on every build (`self_check`) so that neither half can be lost
by somebody who never runs this file.

THE CASE THAT FORCED IT is first: Batteries International titled a piece
"Battery gigafactories — facing a temporary dip or a full-scale crisis?", the
Italvolt row cites it, and the old rule — any question mark fails — called a
publisher's own title a query string. Titles are verbatim, so the rule moved.
"""
from __future__ import annotations

import check_anchor_text as gate


# (text, url_shaped, why). One line per case, and the `why` is what a reader of
# a failure sees, so it says what the case is about rather than repeating the
# expected value.
CASES = [
    # The narrowing, and the titles it protects.
    ("Battery gigafactories — facing a temporary dip or a full-scale crisis?", False,
     "the verbatim title that forced the narrowing"),
    ("What is a low-carbon product?", False, "a question is a sentence, not a query"),
    ("Hvilken plan gjelder for eiendommen min?", False, "and in another language"),
    ("Who pays? The green premium, in one figure", False,
     "a question mark mid-title, followed by more title"),
    ("Cement — Energy System", False, "an ordinary title with an em dash"),

    # The widening, which must survive it.
    ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DS-045409"
     "?format=JSON&flow=1&product=252310&reporter=EU27_2020&time=2025", True,
     "the Comext call this gate was written for"),
    ("http://en.calb-tech.com/news_detail/5.html", True, "a plain http address"),
    ("HTTPS://WWW.EUFABRIC.EU/sitemap.xml", True, "shouted, and still an address"),
    ("www.example.org/path?flow=1", True, "no scheme, and a query pair gives it away"),
    ("ec.europa.eu/eurostat?product=252310", True, "a bare host with a query"),
    ("see https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542", True,
     "an address inside a sentence is still an address in the anchor"),

    # The boundary itself, stated as cases rather than as a comment.
    ("A question? Yes.", False, "a question mark followed by a space is not a pair"),
    ("filter[time]=2025", False, "a pair needs its question mark"),
    ("?uri=CELEX:32023R1542", True, "and with it, it is one"),
]


def main() -> int:
    failures = 0

    for text, expected, why in CASES:
        got = gate.url_shaped(text)
        ok = got == expected
        verdict = "address" if got else "citation"
        print(f"{'ok  ' if ok else 'FAIL'} {why}")
        if not ok:
            failures += 1
            print(f"       {text[:80]!r} reads as a {verdict}")

    # The gate's own fixtures, which are what run on every build.
    broken = gate.self_check()
    print(f"{'ok  ' if not broken else 'FAIL'} the gate's own self-check is clean")
    if broken:
        failures += 1
        for b in broken:
            print(f"       {b}")

    # AND THE RULE STILL READS A PAGE. A predicate that is right about strings
    # and never reaches the anchors would pass everything above and gate
    # nothing, so one fixture page goes through the same extraction the build
    # uses -- markup stripped, entities resolved.
    page = (
        '<p><a href="https://x.test/a">Battery gigafactories &mdash; facing a '
        'temporary dip or a full-scale crisis?</a> '
        '<a href="https://x.test/b">https://x.test/b?flow=1&amp;product=252310</a></p>'
    )
    found = [gate.text_of(inner) for inner in gate.ANCHOR.findall(page)]
    flagged = [t for t in found if gate.url_shaped(t)]
    ok = len(found) == 2 and len(flagged) == 1 and flagged[0].startswith("https://")
    print(f"{'ok  ' if ok else 'FAIL'} over rendered markup, the title passes and the URL fails")
    if not ok:
        failures += 1
        print(f"       extracted {found}, flagged {flagged}")

    total = len(CASES) + 2
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

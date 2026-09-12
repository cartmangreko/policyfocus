"""A readable digest of a cached page: its date, its title, and the paragraphs a
person actually has to read.

    python3 dep_digest.py --file urls.txt [--all]

WHY PARAGRAPH LENGTH IS THE FILTER. Every newsroom on the perimeter wraps its
release in three hundred lines of navigation, product menu and cookie notice, and
each site wraps it differently. A selector per site would be twenty-seven
selectors to maintain and twenty-seven ways to silently drop the one paragraph
that mattered. A line over ~180 characters is a sentence somebody wrote; a line
under it is a menu item. That is crude, and it is crude in the safe direction --
it keeps too much rather than too little, and what it keeps is read by a person.

The digest does NOT decide anything. It does not say whether a page is an order,
who the customer is, or what the quantity was. It puts the candidate sentences in
front of a reader in date order. Every ruling in edges.json was made by reading
one of these and then opening the page.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import dep_text as T

PARA = 180
MONTHS = ("january february march april may june july august september october "
          "november december").split()
ABBR = [m[:3] for m in MONTHS]

DATE_PATTERNS = [
    re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
    re.compile(r"\b(\d{1,2})\.?\s*(" + "|".join(MONTHS + ABBR) + r")\.?\s*,?\s*(\d{4})\b", re.I),
    re.compile(r"\b(" + "|".join(MONTHS + ABBR) + r")\.?\s*(\d{1,2})\s*,?\s*(\d{4})\b", re.I),
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"),
]
SIGNAL = re.compile(
    r"\border|contract|award|purchase|agreement|framework|deliver|suppl|"
    r"letter of intent|\bLoI\b|\bMoU\b|memorandum|licen[cs]|selected|"
    r"\d[\d.,]*\s?(MW|GW|kW|MWe|t/y|tonnes|Mt|ktpa|Mtpa|GWh)\b", re.I)

# Consent banners, privacy policies and investor disclaimers are long enough to
# pass the paragraph filter and carry the word "agreement" often enough to pass
# the signal filter. They are the one boilerplate class worth naming explicitly,
# because every site on the perimeter has one and none of them is ever the story.
BOILER = re.compile(
    r"cookie|consent|privacy policy|forward-looking statement|newsletter|"
    r"subscribe|all rights reserved|terms of use|browsing experience|"
    r"third[- ]party provider|technical storage", re.I)


META_DATE = re.compile(
    r"(?:datePublished|article:published_time|dateCreated|pubdate|"
    r"<time[^>]*datetime)[^0-9]{0,25}(\d{4})-(\d{2})-(\d{2})", re.I)


def meta_date(url: str) -> str | None:
    """The publication date the page declares about itself, if it declares one.

    TRIED FIRST, because it is the page's own answer and the dateline is a guess at
    it. johncockerill.com prints no date anywhere a reader can see but carries a
    correct schema.org datePublished in the head; without this the whole of that
    newsroom collapses to year precision, and a sweep with a period boundary at 1
    January cannot afford to be a year out.
    """
    raw = T.body(url)
    if not raw or raw[:4] == b"%PDF":
        return None
    m = META_DATE.search(raw.decode("utf-8", "replace")[:200000])
    if not m:
        return None
    y, mo, d = (int(g) for g in m.groups())
    try:
        date(y, mo, d)
    except ValueError:
        return None
    return f"{y:04d}-{mo:02d}-{d:02d}" if 2010 <= y <= date.today().year else None


def parse_date(text: str) -> tuple[str | None, str]:
    """(YYYY-MM-DD, precision). The FIRST plausible date in the page, which on a
    press release is its own dateline. A year outside the sweep period is not
    accepted as the page date: it is far more often a copyright line."""
    for pat in DATE_PATTERNS:
        for m in pat.finditer(text[:6000]):
            g = m.groups()
            try:
                if pat is DATE_PATTERNS[0]:
                    y, mo, d = int(g[0]), int(g[1]), int(g[2])
                elif pat is DATE_PATTERNS[1]:
                    d, y = int(g[0]), int(g[2])
                    mo = _mon(g[1])
                elif pat is DATE_PATTERNS[2]:
                    mo, d, y = _mon(g[0]), int(g[1]), int(g[2])
                else:
                    d, mo, y = int(g[0]), int(g[1]), int(g[2])
                date(y, mo, d)
            except (ValueError, TypeError):
                continue
            if 2015 <= y <= date.today().year:
                return f"{y:04d}-{mo:02d}-{d:02d}", "day"
    m = re.search(r"\b(20[1-2]\d)\b", text[:2000])
    return (f"{m.group(1)}-01-01", "year") if m else (None, "unknown")


def _mon(s: str) -> int:
    s = s.lower()[:3]
    return ABBR.index(s) + 1


def paragraphs(text: str) -> list[str]:
    return [l for l in text.splitlines() if len(l) >= PARA]


def digest(url: str, signal_only: bool = True) -> str:
    txt = T.text(url)
    if not txt:
        return f"### {url}\n(not cached)\n"
    md = meta_date(url)
    d, prec = (md, "day") if md else parse_date(txt)
    paras = paragraphs(txt)
    paras = [p for p in paras if not BOILER.search(p)]
    if signal_only:
        paras = [p for p in paras if SIGNAL.search(p)]
    seen, uniq = set(), []
    for p in paras:                    # a release printed twice on one page is one release
        if p[:120] not in seen:
            seen.add(p[:120]); uniq.append(p)
    paras = uniq
    out = [f"### {d} [{prec}] {url}"]
    out += [f"  {p}" for p in paras[:12]]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    sig = "--all" not in args
    if args[0] == "--file":
        urls = [l.strip() for l in Path(args[1]).read_text().splitlines() if l.strip()]
    else:
        urls = [a for a in args if a.startswith("http")]
    rows = [(meta_date(u) or parse_date(T.text(u))[0] or "0000", digest(u, sig))
            for u in urls]
    for _, d in sorted(rows):
        print(d)

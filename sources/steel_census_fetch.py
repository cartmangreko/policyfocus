#!/usr/bin/env python3
"""Fetch for the steel census: gem.wiki as a starting point, owners as the source.

    python3 sources/steel_census_fetch.py --wiki --start 0 --count 45
    python3 sources/steel_census_fetch.py --owners --start 0 --count 45
    python3 sources/steel_census_fetch.py --plan          # what the wiki pages point at

TWO RULES, BOTH RULED 15 September 2026, AND THE FIRST IS THE IMPORTANT ONE.

**gem.wiki IS A STARTING POINT AND NEVER A SOURCE.** GEM's wiki page for a plant
cites the documents GEM itself read; this pass follows those citations out to the
owner's or the permit authority's own document and reads THAT. Nothing in this
census cites gem.wiki, and no rung-bearing fact comes from it. It is the same
standing as the IEA's `Ref` columns in the cement and CCS census — a place for a
search to start, which D83 and D88 were both written about.

**AND THE FURNACE TYPE IN GEM'S UNIT TABLE IS GEM'S CLAIM, NOT THE TEST.** The
clause "scrap EAF, no primary capacity" is applied only after the owner has been
read. An EAF that GEM records as scrap-fed may be an owner's stated replacement
for a blast furnace; the perimeter asks what the investment does to the iron, and
only the owner can say.

WHAT `--owners` FETCHES. Every external link a plant's wiki page carries, minus
the wiki's own infrastructure, capped per plant so one heavily-cited works cannot
eat the budget. Each fetch lands in sources/cache/steel/index.json with url, date,
size and hash, through sources/steel_search.py.
"""
from __future__ import annotations
import argparse, json, os, pathlib, re, sys
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steel_search as ss  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "sources" / "steel_entries.json"

# The wiki's own furniture, and the aggregators a wiki page links for context.
# None of these is an owner or a permit authority.
SKIP = re.compile(
    # the wiki's own furniture and the page's rendering machinery
    r"gem\.wiki|globalenergymonitor\.org|wikipedia\.org|wikimedia|creativecommons\.org|"
    r"mediawiki\.org|jsdelivr\.net|cloudflare|gstatic|googleapis|fontawesome|"
    r"archive\.today|doi\.org/10\.5281|"
    r"linkedin\.com|twitter\.com|x\.com|facebook\.com|youtube\.com|instagram\.com|"
    r"google\.com|bing\.com|duckduckgo|"
    # AND THE OTHER BENCHMARK. gem.wiki cites LeadIT's tracker on 23 of these pages,
    # which is one list citing another and is not an owner document. LeadIT is read
    # as a list in its own right, from its own file, and never through GEM.
    r"industrytransition\.org", re.I)


def entries() -> dict:
    return json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]


def index() -> dict:
    p = ROOT / "sources" / "cache" / "steel" / "index.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"fetches": []}


def fetched_urls() -> set[str]:
    return {f["url"] for f in index()["fetches"]}


def body_of(url: str) -> str:
    for f in index()["fetches"]:
        if f["url"] == url and f.get("sha256"):
            return ss.body_text(f["sha256"])
    return ""


def raw_of(url: str) -> str:
    for f in index()["fetches"]:
        if f["url"] == url and f.get("sha256"):
            p = ROOT / "sources" / "cache" / "steel" / f["sha256"]
            if p.exists():
                return p.read_bytes().decode("utf-8", "replace")
    return ""


def links_from_wiki(url: str, cap: int) -> list[str]:
    """The external documents a wiki page cites, in the order it cites them."""
    raw = raw_of(url)
    out, seen = [], set()
    for href in re.findall(r'href="(https?://[^"]+)"', raw):
        href = href.split("#")[0].rstrip("/")
        if SKIP.search(href) or href in seen:
            continue
        seen.add(href)
        out.append(href)
        if len(out) >= cap:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", action="store_true")
    ap.add_argument("--owners", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, default=45)
    ap.add_argument("--per-plant", type=int, default=3)
    a = ap.parse_args()

    ents = entries()
    keys = sorted(ents, key=lambda k: ents[k]["name"] or "")
    done = fetched_urls()

    if a.wiki:
        todo = [(k, ents[k]["gem_wiki"]) for k in keys
                if ents[k].get("gem_wiki") and ents[k]["gem_wiki"] not in done]
        chunk = todo[a.start:a.start + a.count]
        print(f"{len(todo)} wiki pages not yet fetched; this batch {len(chunk)}")
        for n, (k, u) in enumerate(chunk, 1):
            r = ss.fetch(u, "gem wiki (starting point, never a source)",
                         f"steel census: {k} {ents[k]['name']}")
            print(f"[{n}/{len(chunk)}] {r['outcome']:<20} {ents[k]['name'][:44]}")
        return 0

    plan = []
    for k in keys:
        w = ents[k].get("gem_wiki")
        if not w or w not in done:
            continue
        for u in links_from_wiki(w, a.per_plant):
            if u not in done:
                plan.append((k, u))

    if a.plan:
        by = {}
        for k, u in plan:
            by.setdefault(urlsplit(u).netloc, 0)
            by[urlsplit(u).netloc] += 1
        print(f"{len(plan)} owner/permit documents to fetch, "
              f"{len(by)} distinct hosts")
        for h, n in sorted(by.items(), key=lambda x: -x[1])[:25]:
            print(f"   {n:>4}  {h}")
        return 0

    chunk = plan[a.start:a.start + a.count]
    print(f"{len(plan)} owner documents outstanding; this batch {len(chunk)}")
    for n, (k, u) in enumerate(chunk, 1):
        r = ss.fetch(u, "owner or permit",
                     f"steel census: {k} {ents[k]['name']}")
        print(f"[{n}/{len(chunk)}] {r['outcome']:<20} {u[:84]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

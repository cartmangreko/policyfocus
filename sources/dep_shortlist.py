"""Which cached pages name a row this register holds, and the sentence that does.

    python3 dep_shortlist.py --node NODE_ID [--sector cement,steel] [--all]
    python3 dep_shortlist.py URL [URL ...]

THE MATCHER IS STILL DELIBERATELY DUMB (dep_sweep.matches) and this changes none of
that: it reports a customer name in a page and rules on nothing. What it adds is the
only thing a reader needs that the digest does not give — WHICH pages out of a
hundred and eleven mention anybody, and which paragraph does the mentioning.

Brief 9 read every digest in full. That is the right way to read a newsroom of forty
releases and it does not survive nine more nodes: the pages that name nobody are the
majority and reading them is how the ones that do get skimmed. So the shortlist comes
first and the digest second, and the digest is still where the reading happens.

`--all` prints the pages with no match too, as one line each, because "eighty-nine
pages named nobody" is the other half of the sweep's depth and a file that prints only
its hits cannot say it.

TWO FILTERS, AND NEITHER OF THEM RULES ON ANYTHING.

`--sector` keeps only matches that resolve to a row in the named sectors. A pass that
is about batteries, cement and steel still has to SEE the hydrogen matches — they are
already read and recorded — and does not have to read them again.

AND THE BOILERPLATE FILTER, which is the one that makes the output readable. Every
newsroom ends its releases with an "About the company" block naming its investors and
its partners, and on this perimeter those blocks name register companies: eleven
Carbon Clean releases about board appointments and cleantech awards match `cemex`
because the footer says CEMEX is an investor. A paragraph that appears on four or
more of a node's pages is that footer, and it is dropped from the shortlist ONLY —
the digest and the page still carry it, and a reading is still made against the page.
"""
from __future__ import annotations

import sys
from pathlib import Path

import dep_digest as D
import dep_sweep as S
import dep_text as T

HERE = Path(__file__).resolve().parent


def shortlist(urls: list[str], show_all: bool = False,
              sectors: set[str] | None = None) -> int:
    idx = S.register_index()
    sector_of = {r["id"]: r["sector"] for r in S.register_rows()}
    seen: dict[str, int] = {}
    for u in urls:
        for p in D.paragraphs(T.text(u)):
            seen[p[:120]] = seen.get(p[:120], 0) + 1
    hits = 0
    for u in urls:
        txt = T.text(u)
        if not txt:
            print(f"--- (not cached) {u}")
            continue
        paras = [p for p in D.paragraphs(txt)
                 if not D.BOILER.search(p) and seen.get(p[:120], 0) < 4]
        m = S.matches("\n".join(paras), idx)
        if sectors is not None:
            m = [(a, [i for i in ids if sector_of.get(i) in sectors], k)
                 for a, ids, k in m]
            m = [(a, ids, k) for a, ids, k in m if ids]
        d = D.meta_date(u) or D.parse_date(txt)[0] or "0000-00-00"
        if not m:
            if show_all:
                print(f"    {d}  {u}")
            continue
        hits += 1
        print(f"=== {d}  {u}")
        for alias, ids, kind in m:
            print(f"    [{kind}] {alias} -> {', '.join(ids)}")
        for p in paras:
            if any(f" {a} " in f" {S.norm(p)} " for a, _, _ in m):
                print(f"      {p[:400]}")
    print(f"\n{hits} of {len(urls)} cached pages name a register row.", file=sys.stderr)
    return 0


def main(argv: list[str]) -> int:
    show_all = "--all" in argv
    argv = [a for a in argv if a != "--all"]
    sectors = None
    if "--sector" in argv:
        i = argv.index("--sector")
        sectors = set(argv[i + 1].split(","))
        argv = argv[:i] + argv[i + 2:]
    if argv and argv[0] == "--node":
        f = HERE / f"dependency_cache/.cands-{argv[1]}.txt"
        urls = [l.strip() for l in f.read_text().splitlines() if l.strip()]
    else:
        urls = [a for a in argv if a.startswith("http")]
    return shortlist(urls, show_all, sectors)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

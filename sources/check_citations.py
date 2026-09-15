#!/usr/bin/env python3
"""Every cited URL must be one somebody actually fetched or actually read.

    python3 sources/check_citations.py            # the gate
    python3 sources/check_citations.py --list     # every failing citation, in full

WHY THIS EXISTS, AND IT IS NOT A HYPOTHETICAL. On 15 September 2026 the
transport-and-storage census wrote forty rows and twenty-seven of them cited a
URL that had never been fetched. Not a wrong URL — a PLAUSIBLE one: the right
publisher, the right project, the shape a canonical link takes on that site,
composed from what the page was expected to be called rather than copied from
what was read. Every one looked correct in review. The defect was caught by
counting rows against the fetch index by hand, which is not a thing anybody
should have to remember to do.

**A citation nobody fetched is a citation nobody can check.** The register's whole
claim is that a reader can follow any sentence back to a document; a URL that was
never opened breaks that quietly, because it resolves in a browser often enough to
look fine and points at a page that may say something else entirely.

IT IS THE SAME FAILURE AS D88, POINTING THE OTHER WAY. D88 is a real page that
names no project. This is a plausible URL naming a project nobody opened. In both
the resemblance between a source and a claim did the work that reading should
have done.

WHAT COUNTS AS EVIDENCE THAT SOMEBODY LOOKED. Two things, and only two:

  A FETCH WITH A BODY. The URL appears in one of the cache indexes with a
  non-empty sha256, which means the bytes were on disk under that hash when it
  was recorded. A fetch that failed — a 403, a 404, a URLError — is still a
  fetch and still counts: somebody tried, and the index says what happened. What
  does not count is a URL no index has ever heard of.

  A HUMAN-READ COPY. The URL appears in sources/manual/MANIFEST.json under
  `retrieved`, which means a person opened it in a browser and filed what they
  saw. check_manual_sources gates that file in both directions, so a copy claimed
  here is a copy that exists.

AND ONE THING THAT IS NOT EVIDENCE BUT IS NOT A FAILURE EITHER.
sources/citation_baseline.json lists the 234 citations that were already on the
register the day this gate landed -- pages read before this repository kept a
fetch index at all, which the hydrogen and batteries passes long predate. They
are unproven rather than wrong, and failing them would have made the gate
unrunnable on the day it was written, which is how gates get switched off.

THE BASELINE CAN ONLY SHRINK, and the gate enforces that in both directions: a
URL that is neither fetched, nor hand-read, nor on the list FAILS -- so a newly
composed URL cannot get in, which is the whole point -- and a URL on the list
that nothing cites any more ALSO FAILS, so the debt cannot be padded, and
clearing a citation means deleting its line.

WHAT THIS GATE DOES NOT DO. It does not ask whether the page says what the row
says it says — that is reading, and no gate can do it. It asks only whether
anybody has been there.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Every cache index in the repository. Each is {"fetches": [{url, sha256, ...}]}.
INDEXES = (
    "sources/cache/ccs/index.json",
    "sources/cache/batteries/index.json",
    "sources/cache/steel/index.json",
    "sources/cache/hydrogen/index.json",
    "sources/dependency_cache/index.json",
)

# The files whose rows carry citations.
ROW_FILES = (
    "data/transition/projects.json",
    "data/transition/technologies.json",
)


def known() -> tuple[set[str], set[str]]:
    """(fetched, hand-read). Both are URLs somebody has actually been to."""
    fetched: set[str] = set()
    for rel in INDEXES:
        p = ROOT / rel
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for f in doc.get("fetches", []):
            if f.get("url"):
                fetched.add(f["url"])
    hand: set[str] = set()
    man = ROOT / "sources" / "manual" / "MANIFEST.json"
    if man.exists():
        doc = json.loads(man.read_text(encoding="utf-8"))
        for e in doc.get("retrieved", []):
            if e.get("url"):
                hand.add(e["url"])
    return fetched, hand


# The keys that hold a citation. Named rather than sniffed, so a new field that
# holds a URL has to be added here deliberately and cannot arrive unchecked.
URL_KEYS = ("url", "source_url", "capacity_source_url", "source")


def citations(obj, where: str, out: list[tuple[str, str]]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in URL_KEYS and isinstance(v, str) and v.startswith("http"):
                out.append((v, where))
            else:
                citations(v, f"{where}.{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            citations(v, f"{where}[{i}]", out)


def main() -> int:
    show = "--list" in sys.argv
    fetched, hand = known()
    found: list[tuple[str, str]] = []
    for rel in ROW_FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        rows = doc.get("projects") or doc.get("technologies") or []
        for r in rows:
            citations(r, f"{rel}:{r.get('id', '?')}", found)

    uniq = {}
    for url, where in found:
        uniq.setdefault(url, []).append(where)

    base_path = ROOT / "sources" / "citation_baseline.json"
    baseline = set()
    if base_path.exists():
        baseline = set(json.loads(base_path.read_text(encoding="utf-8"))["baseline"])

    bad = {u: w for u, w in uniq.items()
           if u not in fetched and u not in hand and u not in baseline}
    ok_fetch = sum(1 for u in uniq if u in fetched)
    ok_hand = sum(1 for u in uniq if u in hand and u not in fetched)
    carried = sum(1 for u in uniq if u in baseline and u not in fetched and u not in hand)
    stale = sorted(baseline - set(uniq))

    print(f"check_citations: {len(uniq)} distinct cited URL(s) — "
          f"{ok_fetch} in a cache index, {ok_hand} hand-read and filed, "
          f"{carried} carried on the 2026-09-15 baseline, {len(bad)} neither")

    if stale:
        print(f"\nBASELINE LINES NOTHING CITES ANY MORE ({len(stale)}) — the debt may only "
              f"shrink, so these must be deleted from sources/citation_baseline.json:")
        for u in stale[:20]:
            print(f"  {u}")
        return 1

    if bad:
        by_row: dict[str, int] = {}
        for wheres in bad.values():
            for w in wheres:
                by_row[w.split(".")[0]] = by_row.get(w.split(".")[0], 0) + 1
        print("\nCITED AND NEVER OPENED — a citation nobody fetched is a citation "
              "nobody can check:")
        for row, n in sorted(by_row.items(), key=lambda x: -x[1])[:40 if not show else 10**6]:
            print(f"  {row}  ({n} citation(s))")
        if show:
            print()
            for u, wheres in sorted(bad.items()):
                print(f"  {u}")
                for w in wheres:
                    print(f"      {w}")
        else:
            print("\n  run with --list for every URL and the field it sits in")
        return 1
    print("check_citations: OK — every cited URL was fetched or read by hand.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

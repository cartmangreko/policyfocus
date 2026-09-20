#!/usr/bin/env python3
"""EVERY CITED URL AGAINST THE BYTES ON FILE. Pre-push only, never in the build.

    python3 sources/check_citation_bodies.py

`check_citations.py` asks whether a cited URL appears in a fetch index. That is a
STRING COMPARISON and it runs in the build, where it must, because the indexes are
tracked and the bodies are not. This asks the stronger question the string cannot:
**is there a body on this machine, under the hash the index records, for the URL the
row cites?**

WHY THE TWO ARE SEPARATE. sources/scope.md, "A build-time gate reads tracked files
only": the cache bodies are gitignored, so a byte check cannot run on a deployment
and must not be wired into `npm run build`. It runs in the pre-push chain, where the
machine that holds the bytes is the machine that checks them, and it passes quietly
where a cache is absent — a contributor without it is still entitled to push.

WHAT MADE IT NECESSARY. On 20 September 2026 the steel census was found to have
recorded twelve truncated URLs: it fetched a full URL and wrote a shortened one onto
the entry, so the citation pointed at a path that 404s while the document it was read
from answered 200. The URL check could not see it, because after a later probe the
truncated form was in the index too — as a 404 with no body. A CITATION WHOSE ONLY
FETCH RECORD CARRIES NO BODY IS A CITATION NOBODY HAS READ, and that is what this
gate refuses. sources/steel_docket.md, D-S12.

THREE ANSWERS AND THEY ARE DIFFERENT. A URL with bytes on file passes. A URL whose
only records are refusals — 403, 404, an empty body — is reported as CITED AND NEVER
READ, which is a defect in the citation. A URL that is hand-read and filed in
sources/manual/ passes on the file, which is what the manifest is for.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_citations as cc  # noqa: E402

ROOT = cc.ROOT


def bodies() -> tuple[dict[str, list[dict]], int]:
    """{url: [fetch records that have bytes on this machine]}, and how many caches
    were present."""
    out: dict[str, list[dict]] = {}
    present = 0
    for rel in cc.INDEXES:
        p = ROOT / rel
        if not p.exists():
            continue
        present += 1
        for f in json.loads(p.read_text(encoding="utf-8")).get("fetches", []):
            u, sha = f.get("url"), f.get("sha256")
            if u and sha and (p.parent / sha).exists():
                out.setdefault(u, []).append(f)
    return out, present


def main() -> int:
    have, present = bodies()
    if not have:
        print("check_citation_bodies: no cache body is on this machine, so nothing "
              "can be checked against bytes.\n  This is a skip and not a pass — see "
              "the module docstring.")
        return 0

    hand = set()
    man = ROOT / "sources" / "manual" / "MANIFEST.json"
    if man.exists():
        d = json.loads(man.read_text(encoding="utf-8"))
        for e in d.get("retrieved", []):
            if e.get("url") and (ROOT / "sources" / "manual" / e["file"]).exists():
                hand.add(e["url"])

    cited: list[tuple[str, str]] = []
    for rel in cc.ROW_FILES:
        p = ROOT / rel
        if p.exists():
            cc.citations(json.loads(p.read_text(encoding="utf-8")), rel, cited)

    # WHAT COUNTS AS A CITATION HERE, and what does not. A citation is a document a
    # class or a status RESTS on. Three things in these files carry a URL and are not
    # that, and counting them produced sixty-five false failures on the first run:
    #
    #   `.fetches[`        a search record — the list of what was tried, most of which
    #                      refused, which is the POINT of recording it
    #   `.owner_look.`     a rule 17 queue — pages nobody has read yet, by definition
    #   `looked_in_order`  the same thing under the censuses' own name for it
    #
    # A gate that calls those defects is a gate that punishes the register for writing
    # down its failures, which is most of what this repository is for.
    NOT_A_CITATION = (".fetches[", ".owner_look.", "looked_in_order")
    seen: dict[str, str] = {}
    for u, where in cited:
        if any(x in where for x in NOT_A_CITATION):
            continue
        seen.setdefault(u, where)

    on_bytes, on_hand, never_read, unknown = [], [], [], []
    for u, where in sorted(seen.items()):
        if u in have:
            on_bytes.append(u)
        elif u in hand:
            on_hand.append(u)
        elif any(u in [f.get("url") for f in json.loads((ROOT / rel).read_text(
                encoding="utf-8")).get("fetches", [])]
                 for rel in cc.INDEXES if (ROOT / rel).exists()):
            never_read.append((u, where))
        else:
            unknown.append((u, where))

    print(f"check_citation_bodies: {len(seen)} distinct cited URL(s) against the bytes "
          f"in {present} cache(s).")
    print(f"  {len(on_bytes)} have a body on file, {len(on_hand)} are hand-read and "
          f"filed, {len(never_read)} were fetched and returned nothing, "
          f"{len(unknown)} are in no index on this machine.")

    if never_read:
        print(f"\nCITED AND NEVER READ ({len(never_read)}) — every fetch of this URL "
              f"returned a refusal, so the citation points at a document nobody here "
              f"holds:")
        for u, where in never_read[:30]:
            print(f"  {u[:108]}\n      {where}")

    # A URL IN NO INDEX IS check_citations' JOB, not this one's: it runs in the build
    # and has already passed or failed on it. Printed here for completeness and not
    # counted against this gate, so the two cannot disagree about whose failure it is.
    if unknown:
        print(f"\nin no index on this machine ({len(unknown)}) — reported, not failed; "
              f"check_citations owns this question and runs in the build.")

    # REPORTED, NOT FAILED, AND THE REASON IS WHICH MACHINE THIS IS. A cache is
    # per-worktree and gitignored: a body fetched in one checkout is absent in
    # another, so "no bytes here" can mean the citation is bad OR that the bytes are
    # in the other worktree. THIS GATE CANNOT TELL THOSE APART and a gate that
    # blocks on the difference blocks on where somebody happens to be standing.
    #
    # It is also 21 September, mid-pass, and the standing rule of today is that no
    # rule changes until brief 14 and the supplier sweep are in. So the number is
    # printed, the list is written to sources/ladder_questions.json as L7, and
    # whether it becomes blocking is a ruling somebody makes afterwards.
    print("\ncheck_citation_bodies: reported, not failed — see L7 in "
          "sources/ladder_questions.json for why this is not yet a blocking gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

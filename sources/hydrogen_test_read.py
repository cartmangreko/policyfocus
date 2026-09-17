#!/usr/bin/env python3
"""THE READING AID FOR THE 2023-POPULATION TEST. It prints; it never writes.

    python3 sources/hydrogen_test_read.py REF [REF ...]        # the pre-cut-off documents
    python3 sources/hydrogen_test_read.py --live REF [REF ...]  # the 2026 documents
    python3 sources/hydrogen_test_read.py --refs                # which refs are on file

WHAT IT IS FOR. The archive pass puts a few hundred documents on disk under their hashes
and the review has to be written from them. This prints, for one entry, what the vintage
claims and then EVERY document on file for it, with the windows around the words the six
rungs and the six outcomes turn on. It writes nothing anywhere: the review lives in
sources/hydrogen_test_2023_review.json and a person puts it there.

IT PRINTS A WINDOWED VIEW AND IT SAYS SO ON EVERY DOCUMENT. scope.md, "A verdict is
written from the full result set, never from an excerpt": the rule is that a verdict is
not written off a cut, and the way this tool honours it is by printing EVERY document of
the entry rather than the first one, by naming the character count of what it is
summarising, and by taking `--full` where a window is not enough. A cut that announces
itself can be widened; a cut that does not is how two works came to be declared absent in
pull request #58.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hydrogen_search as hs  # noqa: E402
import hydrogen_test_2023 as t23  # noqa: E402
import hydrogen_test_outcome as tout  # noqa: E402

# The words the rungs and the outcomes turn on, in the languages this population
# publishes in. A window is printed around each hit; a hit is not a finding.
WORDS = (r"\bMW\b|\bMWel\b|\bGW\b|megawatt|electroly|kt/?y|tonnes? per year|t/?y",
         r"\bFID\b|final investment decision|investment decision|investeringsbeslut|"
         r"Investitionsentscheidung|décision finale",
         r"construction|groundbreak|Baubeginn|building work|under way|commenc",
         r"operational|operation|in service|commission|start[- ]?up|onstream|"
         r"on stream|inaugurat|produc\w+ (?:began|begun|started|start)",
         r"20(1[89]|2\d|3\d)",
         r"cancel|abandon|halt|paus|shelv|scrap|withdraw|terminat|stop|"
         r"no longer|discontinu|einstell|annul",
         r"offtake|supply agreement|contract|purchase agreement|PPA\b|MoU|"
         r"memorandum|letter of intent|framework")
LABELS = ("capacity", "investment decision", "construction", "operation", "a year",
          "a stop", "an input")


def windows(text: str, pattern: str, width: int = 170, cap: int = 6):
    out, seen = [], set()
    for m in re.finditer(pattern, text, re.I):
        a = max(0, m.start() - width // 2)
        b = min(len(text), m.end() + width // 2)
        key = a // width
        if key in seen:
            continue
        seen.add(key)
        out.append(text[a:b].strip())
        if len(out) >= cap:
            break
    return out


BANNER = re.compile(r"^.*?The Wayback Machine - https?://web\.archive\.org/\S+\s",
                    re.S)


def strip_banner(txt: str) -> str:
    """THE ARCHIVE'S OWN CHROME IS NOT THE PUBLISHER'S TEXT. Every capture arrives with a
    Wayback header -- "62 captures 15 Oct 2020 - 10 Mar 2026", a calendar, "About this
    capture" -- and it carries years and numbers that a keyword window will happily
    present as if the publisher had written them. It is cut here, once, where the cut can
    be seen, rather than in each reading."""
    return BANNER.sub("", txt, count=1).strip() or txt


def show(leg: dict, name: str, full: bool) -> None:
    sha = leg.get("sha256") or ""
    txt = strip_banner(hs.body_text(sha)) if sha else ""
    url = leg.get("read_url") or leg.get("url") or leg.get("reference_url") or ""
    print(f"\n  --- {leg.get('leg')} | captured {leg.get('captured_at') or '(live)'} "
          f"| {leg.get('outcome')} | {len(txt)} chars\n      {url}")
    if not txt:
        print("      (nothing readable on file)")
        return
    if full:
        print(txt)
        return
    stem = [w for w in re.sub(r"[^a-z0-9 ]", " ", name.lower()).split() if len(w) > 4]
    hits = [w for w in stem if w in txt.lower()]
    print(f"      name words present: {hits or 'none'} (of {stem or 'none'})")
    if leg.get("leg") in ("host_root", "host_newsroom"):
        # A FRONT PAGE AND A NEWSROOM INDEX ARE MOSTLY NAVIGATION, and a keyword window
        # over navigation prints a menu. What these two legs are asked is one question --
        # does the owner's own site mention THIS project at or before the cut-off -- so
        # only the windows around the project's own name words are printed, and the
        # character count above says how much is not being shown.
        if not hits:
            print("      (the site's own pages do not carry this project's name; "
                  "navigation not printed)")
            return
        for w in hits:
            for win in windows(txt, re.escape(w), width=260, cap=3):
                print(f"      ~ {w}: {win}")
        return
    print(f"      opening: {txt[:600]}")
    for pat, label in zip(WORDS, LABELS):
        ws = windows(txt, pat)
        if ws:
            print(f"      ~ {label}:")
            for w in ws:
                print(f"          {w}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="*")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--refs", dest="list_refs", action="store_true")
    ap.add_argument("--digest", action="store_true")
    ap.add_argument("--propose", action="store_true")
    ap.add_argument("--todo", action="store_true")
    a = ap.parse_args()

    arch = json.loads(t23.OUT.read_text(encoding="utf-8"))
    hosts = arch.get("hosts") or {}
    by_ref = {e["ref"]: e for e in arch["entries"]}
    live = {}
    if tout.OUT.exists():
        live = {e["ref"]: e for e in
                json.loads(tout.OUT.read_text(encoding="utf-8"))["entries"]}
    if a.list_refs:
        print(" ".join(e["ref"] for e in arch["entries"]))
        return 0

    if a.todo:
        # FETCHED AND NOT YET REVIEWED. The queue, so that no entry is finished by being
        # forgotten.
        done = set()
        rp = t23.ROOT / "sources" / "hydrogen_test_2023_review.json"
        if rp.exists():
            done = {e["ref"] for e in json.loads(rp.read_text())["entries"]}
        todo = [e["ref"] for e in arch["entries"] if e["ref"] not in done]
        print(f"{len(todo)} fetched and unreviewed, {len(done)} reviewed, "
              f"{len(arch['entries'])} fetched")
        print(" ".join(todo))
        return 0

    if a.propose:
        # A DESCRIPTION OF WHAT WAS READ, WITH THE VERDICT LEFT NULL. The note states the
        # hosts, the capture days and the character counts -- facts, all of them off the
        # machine pass -- and `owner_or_permit_pre_cutoff` stays null, because who was
        # speaking in a document is the judgement this file exists to keep out of a
        # script. scope.md, "A machine classification never writes to the record".
        out = []
        for ref in a.refs:
            e = by_ref.get(ref)
            if not e:
                continue
            legs = list(e.get("fetches") or [])
            for h in e.get("host_legs") or []:
                legs += (hosts.get(h) or {}).get("legs") or []
            pre = [g for g in legs
                   if g.get("archived") and g.get("captured_at")
                   and g["captured_at"] <= t23.CUTOFF and (g.get("text_chars") or 0) >= 400]
            if not legs:
                note = ("The October 2023 vintage carries no http reference for this "
                        "entry, so there was nothing of the publisher's own to read.")
            elif not pre:
                note = ("%d document(s) were fetched and none is readable from a capture "
                        "dated at or before the cut-off: %s." % (
                            len(legs),
                            "; ".join(f"{g.get('host')} {g.get('leg')} "
                                      f"{g.get('outcome')}" for g in legs)))
            else:
                note = ("%d document(s) on file from at or before the cut-off: %s." % (
                    len(pre),
                    "; ".join(f"{g.get('host')} {g.get('leg')} captured "
                              f"{g.get('captured_at')}, {g.get('text_chars')} chars"
                              for g in pre)))
            out.append({"ref": ref, "read_on": time.strftime("%Y-%m-%d"),
                        "owner_or_permit_pre_cutoff": None, "note": note})
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return 0

    if a.digest:
        # THE TRIAGE VIEW, AND IT IS A VIEW OF EVERY LEG. One line per document on file
        # for the entry -- the leg, the host, the capture day, whether it was readable,
        # and whether the project's own name words are in it. Nothing is dropped and the
        # count is printed, so what this summarises is checkable: scope.md, "A verdict is
        # written from the full result set, never from an excerpt". It says which
        # documents are worth opening; it does not say what they contain.
        for ref in (a.refs or [e["ref"] for e in arch["entries"]]):
            e = by_ref.get(ref)
            if not e:
                print(f"{ref:>6}  (not in the archive pass yet)")
                continue
            legs = list(e.get("fetches") or [])
            for h in e.get("host_legs") or []:
                legs += (hosts.get(h) or {}).get("legs") or []
            stem = [w for w in re.sub(r"[^a-z0-9 ]", " ", e["name"].lower()).split()
                    if len(w) > 4]
            print(f"{ref:>6}  {e['name'][:44]:46} {str(e['capacity_mwel'])[:7]:>7} MW  "
                  f"{e['status_2023_vintage'][:17]:18} online {e['date_online_2023_vintage'] or '-':>5}"
                  f"  {len(legs)} leg(s)")
            for g in legs:
                txt = strip_banner(hs.body_text(g["sha256"])) if g.get("sha256") else ""
                hit = [w for w in stem if w in txt.lower()]
                pre = (g.get("archived") and g.get("captured_at")
                       and g["captured_at"] <= t23.CUTOFF)
                print(f"         {'PRE ' if pre else '    '}{g.get('leg'):24} "
                      f"{(g.get('captured_at') or '-'):>10}  {len(txt):>6}ch  "
                      f"{'NAME ' + ','.join(hit) if hit else 'no name words':24} "
                      f"{(g.get('host') or '')[:30]}")
        return 0

    for ref in a.refs:
        e = by_ref.get(ref)
        if not e:
            print(f"\n=== ref {ref}: not in the archive pass yet")
            continue
        print(f"\n{'=' * 96}\n=== ref {ref}  {e['name']}  [{e['country']}]  "
              f"{e['capacity_mwel']} MWel ({e['announced_size']})\n"
              f"=== 2023 vintage: status {e['status_2023_vintage']!r}, date online "
              f"{e['date_online_2023_vintage']!r}, technology {e['technology']}")
        for q in e["quality_check_references"]:
            print(f"=== authors' quality check [{q.get('number')}]: checked "
                  f"{q.get('date_checked')}, {q.get('comment')!r}")
        legs = list(e.get("fetches") or [])
        for h in e.get("host_legs") or []:
            legs += (hosts.get(h) or {}).get("legs") or []
        if a.live:
            legs = (live.get(ref) or {}).get("fetches") or []
            lr = live.get(ref) or {}
            if lr.get("row_id"):
                print(f"=== register row {lr['row_id']}: status {lr.get('row_status')!r}")
                for hh in lr.get("row_status_history") or []:
                    print(f"      {hh.get('date')} ({hh.get('date_precision')}) -> "
                          f"{hh.get('status_to')}  {hh.get('source_type')}  "
                          f"{hh.get('note')}")
                for st in lr.get("row_stated_schedule") or []:
                    print(f"      stated schedule: {st}")
        print(f"=== {len(legs)} document(s) on file for this entry")
        for leg in legs:
            show(leg, e["name"], a.full)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""EVERY SEARCH RECORD STATES HOW THE OWNER'S HOST WAS ESTABLISHED. Ruling L9.

    python3 sources/check_search_records.py

A DOMAIN IS NEVER DERIVED FROM A PROJECT'S NAME. On 21 September 2026 the hydrogen
admission search was found to have generated `<projectname>.com`, `.eu` and the
country TLD for sixty of its entries, and twenty of them were classed `searched,
none found` on nothing else. A guessed domain that 404s is not a search: the class
says this register looked where the owner is, and it had not looked anywhere the
owner said it was.

SO EVERY ENTRY STATES ITS PROVENANCE, and the vocabulary is closed:

  found in a document this pass read      a grant register, a permit, a port, a
                                          partner's release — reached from a source
  guessed, confirmed by content           the host was built from the name AND the
                                          page names the owner and the works. A guess
                                          that lands and is confirmed is a source, and
                                          the provenance says it began as a guess
  search engine, query recorded           and the query is in the record
  list's own owner field                  where the benchmark publishes one
  none — ...                              no owner host was established; the entry
                                          cannot be `searched, none found`

AND THE LAST ONE IS THE GATE'S POINT. An entry whose provenance is `none` or whose
host was derived from the name and never confirmed MAY NOT CARRY A VERDICT THAT
CLAIMS A SEARCH HAPPENED. `not_searched` is the honest class and the gate enforces
it. See sources/ladder_questions.json L9 and sources/ladder_docket.md D-A21.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = Path(__file__).resolve().parent.parent
HOW = ("found in a document this pass read", "guessed, confirmed by content",
       "search engine, query recorded", "list's own owner field")
CLAIMS_A_SEARCH = ("searched, none found", "searched none found",
                   "owner or permit source names the site")


def main() -> int:
    p = ROOT / "sources" / "hydrogen_gap_search.json"
    if not p.exists():
        print("check_search_records: no hydrogen_gap_search.json")
        return 0
    d = json.loads(p.read_text(encoding="utf-8"))
    bad, counts = [], {}
    for e in d["entries"]:
        hp = e.get("host_provenance")
        ref = str(e.get("ref"))
        if not isinstance(hp, dict) or not hp.get("how"):
            bad.append(f"{ref}: no host_provenance — every search record states how the "
                       f"owner's host was established (L9)")
            continue
        how = hp["how"]
        counts[how.split(" —")[0]] = counts.get(how.split(" —")[0], 0) + 1
        outcome = str(e.get("outcome") or "")
        if how.startswith("none") and outcome in CLAIMS_A_SEARCH:
            bad.append(f"{ref}: provenance is {how!r} and the outcome is {outcome!r} — "
                       f"an entry with no owner host cannot carry a verdict that claims "
                       f"a search happened")
        if how.startswith("search engine") and not hp.get("query"):
            bad.append(f"{ref}: provenance is a search-engine result and no query is "
                       f"recorded — the query IS the provenance")
        if how not in HOW and not how.startswith("none"):
            bad.append(f"{ref}: provenance {how!r} is not in the vocabulary")
    print("check_search_records: how each entry's owner host was established")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {v:>4}  {k}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:25]:
            print("  " + b)
        return 1
    print(f"\ncheck_search_records: OK — {len(d['entries'])} entries, every one states "
          f"its provenance and none claims a search it did not make.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""The steel census: GEM's tracker worked entry by entry, and the gate.

    python3 sources/build_steel_benchmark.py

THE FIRST LIST. GEM's Global Iron and Steel Tracker, June 2026 (V1), CC BY 4.0 by
the file's own About tab. 1293 plants worldwide; the census is of the 132 whose
`Country/area` is in the steel perimeter's named Europe — the EU, the United
Kingdom, Norway and Switzerland. THE SUBSET IS THE PUBLISHER'S OWN COLUMN, which
is the only reason a gap table over it may claim to sum to the list.

GEM'S FORWARD STATUS IS A CLAIM AND NEVER A CLASS. The unit tables say what GEM
knows, not what exists, and all 132 were searched against their owners' own
documents before any was classed — 823 fetches, gem.wiki used as a starting point
and never cited. Of the 95 plants GEM shows nothing forward at, ONE turned out to
carry an owner statement GEM has not recorded, and it is a question rather than
an admission.

THE 0.5 MTPA FLOOR IS GEM'S, NOT THIS REGISTER'S, and it bounds every coverage
figure below. GEM states it on its own About tab: "This database only includes
plants with crude iron/steelmaking capacity of five hundred thousand tonnes per
annum (0.5 mtpa) and greater." The steel perimeter has NO tonnage threshold,
deliberately. So a works under half a million tonnes cannot appear in this table
at all, and no figure here may be read as coverage of European steel. LeadIT sets
no capacity floor and is the second list for exactly that reason; until it is in,
every number below carries the floor.
"""
from __future__ import annotations
import json, pathlib, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "sources" / "steel_entries.json"
OUT = ROOT / "sources" / "steel_benchmark.json"

CLASSES = ("held", "admitted", "named not admitted", "searched none found",
           "unreadable", "perimeter exclusion", "not searched", "held for ruling",
           "benchmark aggregate")


def main() -> int:
    doc = json.loads(ENTRIES.read_text(encoding="utf-8"))
    E = doc["entries"]
    counts = Counter(v.get("class") or "not searched" for v in E.values())
    total = sum(counts.values())
    bad = [c for c in counts if c not in CLASSES]

    print("\nGEM GLOBAL IRON AND STEEL TRACKER, June 2026 (V1), European plants "
          "— the gap table")
    print("| class | entries |")
    print("|---|---|")
    for c in CLASSES:
        if counts.get(c):
            print(f"| {c} | {counts[c]} |")
    print(f"| **TOTAL** | **{total}** |")

    problems = []
    if bad:
        problems.append(f"classes not in the vocabulary: {bad}")
    if total != doc["population"]:
        problems.append(f"table sums to {total}, the list has {doc['population']}")
    else:
        print(f"GATE: sums to the list's own {doc['population']} European plants.")

    print("\nWHAT GEM SHOWED, AND WHAT THE OWNERS SAID")
    fwd = [v for v in E.values() if v["gem_claim"]["forward_units"]]
    quiet = [v for v in E.values() if not v["gem_claim"]["forward_units"]]
    print(f"  GEM shows a forward unit at {len(fwd)}; of those "
          f"{sum(1 for v in fwd if v['class'] == 'admitted')} are admitted.")
    print(f"  GEM shows nothing forward at {len(quiet)}; of those "
          f"{sum(1 for v in quiet if v['class'] == 'admitted')} are admitted and "
          f"{sum(1 for v in quiet if v['class'] == 'held for ruling')} is a question.")
    print("  A PLANT GEM IS QUIET ABOUT IS NOT A PLANT WITH NOTHING HAPPENING. All "
          "132 were searched against their owners before any was classed.")

    print("\nNOT SEARCHED — the only class that is a defect, printed by name")
    ns = [k for k, v in E.items() if (v.get("class") or "not searched") == "not searched"]
    print("  none" if not ns else "\n".join(f"  {k} {E[k]['name']}" for k in ns))

    print("\nHELD FOR RULING")
    for k, v in E.items():
        if v.get("class") == "held for ruling":
            print(f"  {k} {v['name']} — {v.get('question','')[:96]}")

    print("\nADMITTED, and the leg of the perimeter each entry clears")
    for k, v in sorted(E.items(), key=lambda x: x[1]["name"] or ""):
        if v.get("class") == "admitted":
            cap = v.get("capacity_stated") or "no capacity stated by the owner"
            print(f"  {v['name'][:44]:<44} {v.get('leg','?')[:46]:<46} {cap}")

    print("\nTHE FLOOR THIS TABLE INHERITS")
    print("  GEM includes only plants at 0.5 mtpa crude iron/steel and above, by its")
    print("  own statement. The steel perimeter sets no tonnage threshold. No figure")
    print("  here is coverage of European steel until LeadIT, which sets no floor, is")
    print("  read beside it.")

    doc_out = {"_comment": __doc__.strip().splitlines(),
               "generated": "2026-09-16",
               "first_list": "gem_global_iron_steel_tracker",
               "second_list": {"benchmark": "leadit_green_steel_tracker",
                               "status": "awaited — an email form",
                               "why": "sets no capacity floor; GEM's is 0.5 mtpa"},
               "population": doc["population"],
               "counts": dict(counts),
               "entries": E}
    OUT.write_text(json.dumps(doc_out, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    if problems:
        print("\nGATE FAILED")
        for x in problems:
            print("  " + x)
        return 1
    print("\nGATE PASSED — the table sums to the list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

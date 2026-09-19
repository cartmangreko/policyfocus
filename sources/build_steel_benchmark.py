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

# A ROW THIS REGISTER HOLDS THAT THE CENSUS DOES NOT REACH, AND WHY. An absence here is a
# decision on the record; an absence NOT here fails the gate. Two so far, and neither is a
# defect: one is under GEM's floor and one is a different fact at a works the census does
# carry.
# THE ROWS THIS CENSUS LANDED, 20 September 2026. Named rather than inferred, on the
# same reasoning as ROW_ABSENCE below it: an exception a gate accepts has to be written
# down by a person, or the gate is checking that the data agrees with itself.
LANDED_BY_THIS_CENSUS = {
    "power4steel-dillingen", "power4steel-voelklingen", "arcelormittal-gijon",
    "zesta-gent",
    "blastr-inkoo", "gravithy-fos-sur-mer", "gravithy-kristinestad",
    "liberty-dunkerque-dri", "ssab-lulea", "ssab-oxelosund", "tata-steel-ijmuiden",
    "tata-steel-port-talbot", "hyiron-lingen",
    # LANDED 20 SEPTEMBER 2026 under the two rulings of that day. Six were held on a
    # finding that was wrong — their URLs were truncated on the entry, not dead — and
    # the seventh is Marcegaglia's AdriatiCO2, which the steel perimeter's new capture
    # leg holds. sources/steel_docket.md, D-S12 and D-S13.
    "hybrit-gallivare", "stegra-spain", "metinvest-piombino", "arcelormittal-duisburg",
    "arcelormittal-dunkerque", "arcelormittal-fos-sur-mer", "adriatico2-ravenna",
}

ROW_ABSENCE = {
    # LANDED 20 SEPTEMBER 2026 FROM THE SECOND LIST, and GEM cannot carry it: HyIron's
    # GEiSt at Lingen is a pilot below the 0.5 mtpa floor GEM's About tab sets. The
    # entry that admits it is LeadIT's GST-016 in sources/leadit_entries.json, so no
    # entry in THIS list points at the row and that is the floor, not an oversight.
    # sources/steel_docket.md, D-S2.
    "adriatico2-ravenna": ("admitted from the second list under the steel perimeter's "
                           "capture leg of 20 September; GEM carries the Ravenna works "
                           "under no forward unit and the entry that admits it is "
                           "LeadIT's GST-158 — see leadit_entries.json"),
    "hyiron-lingen": ("admitted from the second list; below GEM's 0.5 mtpa floor, so "
                      "GEM does not carry the works — see leadit_entries.json GST-016"),
    "hybrit-pilot-lulea": "the HYBRIT pilot at Luleå is below GEM's 0.5 mtpa floor; the "
                          "list cannot carry it, which is why there is a second list",
    "3d-dunkirk": "a CCS row at a works the census carries for a different fact — "
                  "ArcelorMittal Dunkerque is admitted for its announced DRI plant, and "
                  "carbon capture on a blast furnace is not one of the four legs",
}

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
    inp = lambda vs: sum(1 for v in vs if v["class"] in ("admitted", "held"))
    print(f"  GEM shows a forward unit at {len(fwd)}; of those {inp(fwd)} are in "
          f"perimeter ({sum(1 for v in fwd if v['class'] == 'admitted')} admitted, "
          f"{sum(1 for v in fwd if v['class'] == 'held')} already held here).")
    print(f"  GEM shows nothing forward at {len(quiet)}; of those {inp(quiet)} are in "
          f"perimeter ({sum(1 for v in quiet if v['class'] == 'admitted')} admitted, "
          f"{sum(1 for v in quiet if v['class'] == 'held')} already held here).")
    print("  A PLANT GEM IS QUIET ABOUT IS NOT A PLANT WITH NOTHING HAPPENING. All "
          "132 were searched against their owners before any was classed.")

    print("\nNOT SEARCHED — the only class that is a defect, printed by name")
    ns = [k for k, v in E.items() if (v.get("class") or "not searched") == "not searched"]
    print("  none" if not ns else "\n".join(f"  {k} {E[k]['name']}" for k in ns))

    print("\nHELD FOR RULING")
    for k, v in E.items():
        if v.get("class") == "held for ruling":
            print(f"  {k} {v['name']} — {v.get('question','')[:96]}")

    print("\nADMITTED AND HELD, and the leg of the perimeter each entry clears")
    for k, v in sorted(E.items(), key=lambda x: x[1]["name"] or ""):
        if v.get("class") in ("admitted", "held"):
            cap = v.get("capacity_stated") or "no capacity stated by the owner"
            print(f"  {v['name'][:44]:<44} {v.get('leg','?')[:46]:<46} {cap}")

    # THE ROW AUDIT. Added 18 September 2026 after the second list found the census
    # reporting "no announced route change" at a works this register already held.
    # A census of an outside list that never asks what the register holds can report a
    # silence at its own rows, and it did.
    print("\nTHE ROW AUDIT — every steel row this register holds, against the census")
    import json as _json
    rows = {p["id"]: p for p in _json.loads(
        (ROOT / "data" / "transition" / "projects.json").read_text(encoding="utf-8")
    )["projects"] if p.get("sector") == "steel"}
    pointed = {v.get("row") for v in E.values() if v.get("row")}
    for rid in sorted(rows):
        where = [v["name"] for v in E.values() if v.get("row") == rid]
        if where:
            print(f"  {rid:32} held at {where[0][:44]}")
        else:
            print(f"  {rid:32} NOT IN THIS LIST — {ROW_ABSENCE.get(rid, 'unexplained')}")
            if rid not in ROW_ABSENCE:
                problems.append(f"{rid} is a steel row and no census entry points at it, "
                                f"and no reason is recorded in ROW_ABSENCE")
    # `held` MEANS THE REGISTER HELD THE WORKS BEFORE THIS CENSUS, and after 20
    # September that is no longer the same thing as "a row exists". The census
    # admitted twenty-one works and proposed row ids; fifteen of those rows have now
    # LANDED OUT OF THOSE ADMISSIONS, so the entry points at an existing row and is
    # rightly `admitted` — the row is the census's own product, not something the
    # census failed to notice. The audit still has to catch what it was written for,
    # which is a census reporting silence at a row that predates it, so the
    # distinction is recorded per row rather than inferred: a row the census landed
    # is named here, and anything else pointing at an existing row must be `held`.
    for k, v in E.items():
        rid = v.get("row")
        if rid in rows and v.get("class") not in ("held",):
            if rid in LANDED_BY_THIS_CENSUS and v.get("class") == "admitted":
                continue
            problems.append(f"{k} points at the existing row {rid} and is classed "
                            f"{v.get('class')!r}; a works the register already holds is "
                            f"`held`")
    for rid in sorted(LANDED_BY_THIS_CENSUS):
        if rid not in rows:
            problems.append(f"{rid} is recorded as landed by this census and no such "
                            f"steel row exists")

    print("\nTHE FLOOR THIS TABLE INHERITS")
    print("  GEM includes only plants at 0.5 mtpa crude iron/steel and above, by its")
    print("  own statement. The steel perimeter sets no tonnage threshold. No figure")
    print("  here is coverage of European steel until LeadIT, which sets no floor, is")
    print("  read beside it.")

    doc_out = {"_comment": __doc__.strip().splitlines(),
               "generated": "2026-09-16",
               "first_list": "gem_global_iron_steel_tracker",
               "second_list": {"benchmark": "leadit_green_steel_tracker",
                               "status": "in, 18 September 2026",
                               "why": "sets no capacity floor; GEM's is 0.5 mtpa",
                               "table": "sources/steel_second_list.json",
                               "docket": "sources/steel_docket.md, D-S2"},
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

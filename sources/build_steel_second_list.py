#!/usr/bin/env python3
"""The second list, and the drift between the two: LeadIT beside GEM.

    python3 sources/build_steel_second_list.py       # the tables, and the gate

THE SECOND LIST. LeadIT's Green Steel Tracker, version 2026-09-04, CC BY 4.0 by the file's
own About tab. 161 project rows worldwide; 68 whose `Continent` is Europe; 65 in the steel
perimeter's own Europe -- the EU, the United Kingdom, Norway and Switzerland. Each of the
65 ends in exactly one class and the counts must sum to 65 or this script exits non-zero,
which is the same gate the first list is held to.

WHY THERE IS A SECOND LIST HERE AND NOT IN CEMENT. The cement census recorded its second
list as DROPPED and said why: CO2RE renders rows a person can read and never states how
many there are, and a gap table is gated on summing to the list's own count. LeadIT states
its rows, carries its own identifier, and publishes a `GEM Plant ID` column -- so the two
lists can be joined on a publisher's key rather than on a name this register folded.

DRIFT HERE IS BETWEEN TWO PUBLISHERS, NOT BETWEEN TWO VINTAGES. The hydrogen drift table
measures one list against its own past. This one measures two lists against each other on
the same day, which answers a different question: not what a publisher changed its mind
about, but what each publisher can see. GEM sees plants at 0.5 mtpa and above. LeadIT sees
projects at any size and disqualifies by an editorial test of its own. NEITHER IS THE
POPULATION, and the table's job is to say how much of each the other misses.
"""
from __future__ import annotations
import json, pathlib, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEADIT = ROOT / "sources" / "leadit_entries.json"
GEM = ROOT / "sources" / "steel_entries.json"
OUT = ROOT / "sources" / "steel_second_list.json"

CLASSES = ("held", "admitted", "named not admitted", "searched none found",
           "unreadable", "perimeter exclusion", "not searched", "held for ruling",
           "benchmark aggregate")


def main() -> int:
    L = json.loads(LEADIT.read_text(encoding="utf-8"))
    E = L["entries"]
    G = json.loads(GEM.read_text(encoding="utf-8"))
    GE = G["entries"]
    problems = []

    counts = Counter(v.get("class") or "not searched" for v in E.values())
    total = sum(counts.values())
    print("\nLEADIT GREEN STEEL TRACKER, 2026-09-04, the perimeter's Europe — the gap table")
    print("| class | entries |")
    print("|---|---|")
    for c in CLASSES:
        if counts.get(c):
            print(f"| {c} | {counts[c]} |")
    print(f"| **TOTAL** | **{total}** |")
    if [c for c in counts if c not in CLASSES]:
        problems.append(f"classes not in the vocabulary: "
                        f"{[c for c in counts if c not in CLASSES]}")
    if total != L["population"]:
        problems.append(f"table sums to {total}, the list has {L['population']}")
    else:
        print(f"GATE: sums to the list's own {L['population']} entries in the perimeter's "
              f"Europe.")
    print(f"  LeadIT's own Europe is {L['leadit_europe']} rows; "
          f"{L['leadit_europe'] - L['population']} are outside the perimeter's four "
          f"countries ({', '.join(L['outside_the_perimeter_geography'])}) and are counted "
          f"out here rather than dropped quietly.")

    # ------------------------------------------------------------------ the drift
    joined = {k: v for k, v in E.items() if v["gem"]["key"]}
    new = {k: v for k, v in E.items() if not v["gem"]["key"]}
    gem_plants_seen = {v["gem"]["key"] for v in joined.values()}
    byhand = {k: v for k, v in joined.items()
              if v["gem"]["matched_on"].startswith("by works")}

    print("\nWHAT EACH LIST CARRIES OF THE OTHER")
    print(f"  GEM's European plants:                      {G['population']}")
    print(f"  LeadIT's European entries (perimeter):      {L['population']}")
    print(f"  LeadIT entries at a GEM plant:              {len(joined)}"
          f"  (at {len(gem_plants_seen)} distinct plants)")
    print(f"     of those, joined on LeadIT's own key:    {len(joined) - len(byhand)}")
    print(f"     joined BY HAND, by works:                {len(byhand)}"
          f"  — LeadIT carries no GEM id for these")
    print(f"  LeadIT entries GEM does not carry:          {len(new)}")
    print(f"  GEM plants LeadIT does not carry:           "
          f"{G['population'] - len(gem_plants_seen)}")

    print("\n  THE THREE LEADIT DOES NOT LINK, AND A NAME MATCH IS NOT HOW THEY WERE FOUND")
    for k, v in byhand.items():
        print(f"    {k}  {v['name'][:40]:42} -> {v['gem']['name']} ({v['gem']['class']})")
    print("    LeadIT's cross-reference is incomplete, which is a fact about the column")
    print("    and not about the works. Each was matched by reading the two rows, one at a")
    print("    time; the docket's diacritic ruling is what a folded-name match costs.")

    print("\nWHAT THE FLOOR HIDES — the 13 entries GEM cannot carry, by class")
    for c in CLASSES:
        n = sum(1 for v in new.values() if v.get("class") == c)
        if n:
            print(f"  {n:>3}  {c}")
    adm = [v for v in new.values() if v.get("class") == "admitted"]
    print(f"\n  ADMITTED FROM THE SECOND LIST AND FROM NOWHERE ELSE: {len(adm)}")
    for v in adm:
        print(f"    {v['name']} — {v['company']}, {v['country']}")
        print(f"      {v['leg']}; {v['speaker']}")
        print(f"      \"{v['verbatim'][:150]}\"")

    print("\nWHERE THE TWO LISTS DISAGREE ABOUT THE SAME WORKS")
    dis = []
    for k, v in joined.items():
        gclass = v["gem"]["class"]
        q = v["leadit_claim"]["qualified_for_tracker"].lower().startswith("yes")
        fwd = bool(GE[v["gem"]["key"]]["gem_claim"]["forward_units"])
        if q and gclass in ("perimeter exclusion", "named not admitted",
                            "searched none found"):
            dis.append((k, v, f"LeadIT qualifies it; this register has it as {gclass}"))
        elif q and not fwd:
            dis.append((k, v, "LeadIT qualifies it; GEM shows no forward unit at the plant"))
    for k, v, why in dis:
        print(f"  {k}  {v['name'][:38]:40} {why}")
        print(f"       LeadIT: {v['leadit_claim']['project_status']}, "
              f"{v['leadit_claim']['technology_category'][:40]}")
    print(f"  ({len(dis)} of {len(joined)})")

    print("\nWHAT LEADIT SAYS ABOUT THE WORKS THIS REGISTER HOLDS OR ADMITS")
    adm_gem = {k for k, v in GE.items() if v.get("class") in ("admitted", "held")}
    seen = {v["gem"]["key"] for v in joined.values() if v["gem"]["key"] in adm_gem}
    print(f"  in perimeter from GEM (admitted or held): {len(adm_gem)}; LeadIT carries "
          f"{len(seen)} of them, and is silent on {len(adm_gem - seen)}.")
    for key in sorted(adm_gem - seen, key=lambda x: GE[x]["name"]):
        print(f"    silent: {GE[key]['name']}")
    stat = Counter()
    for k, v in joined.items():
        if v["gem"]["key"] in adm_gem:
            stat[v["leadit_claim"]["project_status"] or "(blank)"] += 1
    print("  LeadIT's own status for the works it does carry:")
    for s, n in stat.most_common():
        print(f"    {n:>3}  {s}")

    doc = {"_comment": __doc__.strip().splitlines(),
           "generated": "2026-09-18",
           "first_list": {"benchmark": "gem_global_iron_steel_tracker",
                          "vintage": "June 2026 (V1)", "population": G["population"],
                          "floor": "0.5 mtpa crude iron/steel, GEM's own"},
           "second_list": {"benchmark": "leadit_green_steel_tracker",
                           "vintage": L["vintage"], "population": L["population"],
                           "floor": "none"},
           "counts": dict(counts),
           "drift": {
               "leadit_entries_at_a_gem_plant": len(joined),
               "distinct_gem_plants_leadit_carries": len(gem_plants_seen),
               "joined_on_leadit_own_key": len(joined) - len(byhand),
               "joined_by_hand_by_works": sorted(byhand),
               "leadit_entries_gem_does_not_carry": len(new),
               "gem_plants_leadit_does_not_carry": G["population"] - len(gem_plants_seen),
               "admitted_from_the_second_list_alone": [v["name"] for v in adm],
               "disagreements_about_the_same_works": [
                   {"leadit_id": k, "name": v["name"], "why": why} for k, v, why in dis],
               "in_perimeter_works_leadit_is_silent_on": sorted(
                   GE[k]["name"] for k in adm_gem - seen)},
           "entries": E}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
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

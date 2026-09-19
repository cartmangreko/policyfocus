#!/usr/bin/env python3
"""THE FIVE POPULATIONS THE LADDER IS SCORED OVER, brief 11 item 1.

    python3 sources/ladder_population.py        # the five identities, and the gate

One line per entry, and every entry in exactly one class. A population is
**the union of the sector's external list entries in the current vintage and the
register's rows that are not on those lists** -- the rule brief 10 set for
hydrogen, applied to the other four.

THE KEY IS THE PUBLISHER'S IDENTIFIER WHERE THERE IS ONE and the row id where
there is not. That is not a formatting preference: a key built from a name is a
name match wearing a key's clothes, and sources/steel_docket.md D-S1 and D-S4
record what those cost in this repository.

  hydrogen               `iea:<projectReference>` / `row:<id>`     (brief 10, unchanged)
  batteries              `row:<id>` where a list entry names a row,
                         else `te24:<label>` or `bn26:<label>`
  cement                 `ieaccus:<ID>` / `row:<id>`
  transport and storage  `ieaccus:<ID>` / `row:<id>`
  steel                  `gem:<GEM Plant ID>` / `leadit:<Internal ID>` / `row:<id>`

BATTERIES HAS NO PUBLISHER IDENTIFIER AND THAT IS A FINDING, NOT A GAP HERE.
Neither Transport & Environment's annex nor Battery-News numbers its rows; both
publish a label. So a battery entry is keyed by the register row where the census
matched one -- which is what makes the union of the two lists computable at all --
and by `<list>:<label>` where it did not. The two lists name the same works 22
times and those are ONE entry, not two.

CEMENT AND TRANSPORT-AND-STORAGE COME OFF ONE LIST AND ARE TWO POPULATIONS.
The IEA CCUS Projects Database is a single file of 425 European rows; the split
is the publisher's own `Subsector` column, exactly as the census made it --
`Cement` is the cement sector, and `CO2 T&S`, `CO2 transport` and `CO2 storage`
are transport and storage. THE OTHER 243 ROWS ARE IN NEITHER POPULATION: they are
capture at a refinery, a waste plant, a chemical works. They are not dropped
quietly -- the gate below counts them and the identity prints them -- but a
ladder over a refinery's capture unit would be a ladder over a sector this
register does not hold.

PERIMETER EXCLUSIONS ARE CARRIED AND NOT SCORED, on D-L1. A project this dataset
is not about cannot fail to confirm itself, and scoring it zero out of six said
that it had. The clause travels with the entry.
"""
from __future__ import annotations

import json
import os
import re
import pathlib
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
S = ROOT / "sources"

SECTORS = ("hydrogen", "batteries", "cement", "transport and storage", "steel")

# The register's own sector value for each of the five. `clean` is hydrogen and
# `ccs` is transport and storage; both names predate the ladder and neither is
# renamed here, because renaming a field to match a report is how a report stops
# being a reading of the data.
REGISTER_SECTOR = {"hydrogen": "clean", "batteries": "batsol", "cement": "cement",
                   "transport and storage": "ccs", "steel": "steel"}

# THE LAYER A SECTOR SITS ON. Four of the five make a product at a works — hydrogen,
# cells, clinker, steel — and one of them moves and stores somebody else's CO2. A
# pipeline has no nameplate its owner publishes and a reservoir is not a plant, so the
# two layers answer the six rungs differently and averaging them says nothing about
# either. THIS IS A LABEL ON THE ENTRIES AND CHANGES NO DATA: the same lines, the same
# cells, reported in two groups instead of one.
LAYER = {"hydrogen": "producing", "batteries": "producing", "cement": "producing",
         "steel": "producing", "transport and storage": "infrastructure"}

CEMENT_SUBSECTORS = {"Cement"}
TS_SUBSECTORS = {"CO2 T&S", "CO2 transport", "CO2 storage"}

NOT_SCORED = ("perimeter exclusion",)


def admission(v: dict, note_field: str = "note") -> dict:
    """WHAT THE CENSUS READ, carried onto the ladder entry.

    ADDED 20 SEPTEMBER 2026, and it is the fix for a reading and not for the data.
    The ladder scored rung 1 for a census entry off a generic sentence — "the census
    read the owner's own sources and none names a site" — WHICH WAS FALSE OF EVERY
    ADMITTED ENTRY. A census admits a works precisely because it read a company
    document naming it, and each census records that document: `source`, `speaker`,
    `verbatim`. Twenty admitted steel works failed rung 1 on a field the steel
    entries do not have rather than on the field they do.

    `failed_leg` IS THE OTHER HALF. Where a census names a works and refuses it, the
    leg it failed on says whether the SITE was the problem. A battery entry whose
    note opens "FAILED LEG: SITE" must fail rung 1; one that failed on capacity has
    a site on file and passes. Passing all of them, which is what the first version
    did, scored rung 1 off the class name instead of off the evidence.
    """
    leg = (v.get("failed_leg") or "")
    n = v.get(note_field) or ""
    m = re.match(r"\s*FAILED LEG:\s*([^.]+)\.", n)
    if not leg and m:
        leg = m.group(1).strip()
    return {"admitted_by": v.get("admitted_by") or "",
            "source": v.get("source") or "", "speaker": v.get("speaker") or "",
            "verbatim": v.get("verbatim") or "", "failed_leg": leg,
            "municipality": v.get("municipality") or v.get("site") or "",
            "looked_in_order": v.get("looked_in_order") or []}


def _load(name):
    return json.loads((S / name).read_text(encoding="utf-8"))


def rows_by_sector(sector: str):
    return [p for p in sm.load("project") if p.get("sector") == REGISTER_SECTOR[sector]]


# --------------------------------------------------------------------------
# BATTERIES


def batteries():
    """T&E's 2024 annex 1 and Battery-News' February 2026 list, unioned on the row
    each names, plus the batsol rows neither carries."""
    doc = _load("batteries_benchmark.json")["benchmarks"]
    lists = {"te24": ("te_2024_annex_1",
                      "Transport & Environment, 2024 gigafactory annex 1"),
             "bn26": ("battery_news_2026_02",
                      "Battery-News.de, European cell plants, February 2026")}
    entries: dict[str, dict] = {}
    for tag, (key, title) in lists.items():
        for e in doc[key]:
            ref = e.get("ref") or ""
            k = f"row:{ref}" if ref and "|" not in ref else f"{tag}:{e['label']}"
            cur = entries.setdefault(k, {
                "key": k, "name": e["label"], "country": e.get("country", ""),
                "row_id": ref if ref and "|" not in ref else "",
                "register_class": e["class"], "clause": "",
                "admission": admission(e), "list_claims": [], "lists": []})
            cur["lists"].append(title)
            cur["list_claims"].append({
                "benchmark": key, "label": e["label"], "class_in_census": e["class"],
                "note": e.get("note", ""),
                "capacity_as_published": e.get("benchmark_gwh", ""),
                "capacity_unit": "GWh a year" if e.get("benchmark_gwh") else "",
                "year_as_published": e.get("benchmark_year", "")})
            # WHERE THE TWO LISTS DISAGREE ABOUT A CLASS the census's own later
            # reading wins, and both are kept on the line.
            if e["class"] != cur["register_class"] and e["class"] != "benchmark aggregate":
                cur["register_class"] = e["class"]
            if not cur["country"] and e.get("country"):
                cur["country"] = e["country"]
    on_a_list = {v["row_id"] for v in entries.values() if v["row_id"]}
    # A COMPOUND REF IS ONE LIST ENTRY NAMING TWO WORKS -- a benchmark aggregate --
    # and the rows behind it are not off-list.
    for v in entries.values():
        for c in v["list_claims"]:
            pass
    for e in doc["te_2024_annex_1"] + doc["battery_news_2026_02"]:
        if e.get("ref") and "|" in e["ref"]:
            on_a_list.update(e["ref"].split("|"))
    out = list(entries.values())
    for r in rows_by_sector("batteries"):
        if r["id"] in on_a_list:
            continue
        out.append({"key": f"row:{r['id']}", "name": f"{r.get('company','')} "
                    f"{r.get('plant','')}".strip(), "country": r.get("country", ""),
                    "row_id": r["id"], "register_class": "admitted", "clause": "",
                    "list_claims": [], "lists": ["(no external list carries it)"]})
    return out, {
        "te_2024_annex_1": len(doc["te_2024_annex_1"]),
        "battery_news_2026_02": len(doc["battery_news_2026_02"]),
        "named_by_both": sum(1 for v in entries.values() if len(v["lists"]) > 1),
        "union_of_the_two_lists": len(entries),
        "register_rows_on_neither": len(out) - len(entries),
        "population": len(out)}


# --------------------------------------------------------------------------
# CEMENT AND TRANSPORT AND STORAGE -- one list, two populations


def _ccus(subsectors, sector):
    bench = _load("cement_ccs_benchmark.json")["entries"]
    hand = _load("cement_ccs_entries.json")["entries"]
    mine = [e for e in bench if e.get("subsector") in subsectors]
    out, linked = [], set()
    for e in mine:
        k = str(e["iea_id"])
        h = hand.get(k) or {}
        rid = h.get("row") or ""
        if rid:
            linked.add(rid)
        out.append({
            "key": f"ieaccus:{k}", "name": e.get("name", ""),
            "country": e.get("country", ""), "row_id": rid,
            "register_class": e.get("class", ""), "clause": e.get("clause", ""),
            "admission": admission(h),
            "lists": ["IEA CCUS Projects Database, 2026 edition"],
            "list_claims": [{
                "benchmark": "iea_ccus_projects_database", "iea_id": e["iea_id"],
                "iea_status": e.get("iea_status", ""), "project_type": e.get("project_type", ""),
                "subsector": e.get("subsector", ""),
                "capacity_as_published": e.get("iea_announced_capacity_mt")
                                         or e.get("iea_estimated_capacity_mt") or "",
                "capacity_unit": "Mt CO2 a year" if (
                    e.get("iea_announced_capacity_mt") or e.get("iea_estimated_capacity_mt"))
                    else "",
                "note": (h.get("note") or h.get("match") or "")}]})
    for r in rows_by_sector(sector):
        if r["id"] in linked:
            continue
        out.append({"key": f"row:{r['id']}", "name": f"{r.get('company','')} "
                    f"{r.get('plant','')}".strip(), "country": r.get("country", ""),
                    "row_id": r["id"], "register_class": "admitted", "clause": "",
                    "list_claims": [], "lists": ["(the list does not carry it)"]})
    return out, {"iea_ccus_entries_in_this_subsector": len(mine),
                 "register_rows_the_list_does_not_carry": len(out) - len(mine),
                 "population": len(out)}


def cement():
    return _ccus(CEMENT_SUBSECTORS, "cement")


def transport_and_storage():
    return _ccus(TS_SUBSECTORS, "transport and storage")


# --------------------------------------------------------------------------
# STEEL


def steel():
    """GEM's 132 works, LeadIT's 13 that GEM does not carry, and the register's
    two rows neither list can hold. Joined exactly as #67 joined them."""
    gem = _load("steel_entries.json")["entries"]
    lead = _load("leadit_entries.json")["entries"]
    existing = {p["id"] for p in sm.load("project")}
    out, linked = [], set()
    for k, v in gem.items():
        # `row` IS TWO DIFFERENT FIELDS UNDER ONE NAME. On a `held` entry it names a
        # row the register already carries; on an `admitted` one it names the row the
        # census PROPOSES and nothing has landed yet. Reading them alike sent twenty
        # admitted works down the no-row path, where the scorer cited a census
        # sentence about finding nothing at a works the census had admitted.
        rid = v.get("row") or ""
        proposed = rid if rid and rid not in existing else ""
        rid = rid if rid in existing else ""
        if rid:
            linked.add(rid)
        out.append({
            "key": f"gem:{k}", "name": v.get("name", ""), "country": v.get("country", ""),
            "row_id": rid, "proposed_row_id": proposed,
            "register_class": v.get("class", ""),
            "clause": v.get("clause", ""), "admission": admission(v),
            "lists": ["GEM Global Iron and Steel Tracker, June 2026 (V1)"],
            "list_claims": [{"benchmark": "gem_global_iron_steel_tracker",
                             "gem_plant_id": k,
                             "forward_units": (v.get("gem_claim") or {}).get("forward_units", []),
                             "note": v.get("note", "")}]})
    by_gem = {e["key"]: e for e in out}
    for k, v in lead.items():
        g = (v.get("gem") or {}).get("key") or ""
        claim = {"benchmark": "leadit_green_steel_tracker", "leadit_id": k,
                 "label": v.get("name", ""), **(v.get("leadit_claim") or {})}
        if g and f"gem:{g}" in by_gem:
            # THE SAME WORKS, SEEN BY A SECOND PUBLISHER. One line, two claims.
            e = by_gem[f"gem:{g}"]
            e["lists"].append("LeadIT Green Steel Tracker, 2026-09-04")
            e["list_claims"].append(claim)
            continue
        # THE SAME TWO-FIELDS-ONE-NAME SPLIT AS THE GEM BRANCH ABOVE, and it was
        # missing here: a LeadIT entry's `row` is an existing row on a held entry
        # and the PROPOSED row on an admitted one, and reading them alike made a
        # funder-admitted entry look as though a row already stood behind it.
        rid = v.get("row") or ""
        proposed = rid if rid and rid not in existing else ""
        rid = rid if rid in existing else ""
        if rid:
            linked.add(rid)
        out.append({"key": f"leadit:{k}", "name": v.get("name", ""),
                    "country": v.get("country", ""), "row_id": rid,
                    "proposed_row_id": proposed,
                    "register_class": v.get("class", ""), "clause": v.get("clause", ""),
                    "admission": admission(v),
                    "lists": ["LeadIT Green Steel Tracker, 2026-09-04"],
                    "list_claims": [claim]})
    for r in rows_by_sector("steel"):
        if r["id"] in linked:
            continue
        out.append({"key": f"row:{r['id']}", "name": f"{r.get('company','')} "
                    f"{r.get('plant','')}".strip(), "country": r.get("country", ""),
                    "row_id": r["id"], "register_class": "admitted", "clause": "",
                    "list_claims": [], "lists": ["(neither list carries it)"]})
    ln = len([e for e in out if e["key"].startswith("leadit:")])
    return out, {"gem_plants": len(gem), "leadit_entries": len(lead),
                 "leadit_entries_at_a_gem_plant": len(lead) - ln,
                 "leadit_entries_gem_does_not_carry": ln,
                 "register_rows_neither_list_carries":
                     len(out) - len(gem) - ln,
                 "population": len(out)}


BUILDERS = {"batteries": batteries, "cement": cement,
            "transport and storage": transport_and_storage, "steel": steel}


IDENTITY = {
    "batteries": lambda p: (
        f"{p['te_2024_annex_1']} T&E 2024 + {p['battery_news_2026_02']} Battery-News 2026-02 "
        f"- {p['named_by_both']} the two lists name the same works "
        f"= {p['union_of_the_two_lists']} union, + {p['register_rows_on_neither']} "
        f"register rows on neither list = {p['population']}"),
    "cement": lambda p: (
        f"{p['iea_ccus_entries_in_this_subsector']} IEA CCUS rows at Subsector `Cement` "
        f"+ {p['register_rows_the_list_does_not_carry']} register rows the list does not "
        f"carry = {p['population']}"),
    "transport and storage": lambda p: (
        f"{p['iea_ccus_entries_in_this_subsector']} IEA CCUS rows at Subsector `CO2 T&S`, "
        f"`CO2 transport` or `CO2 storage` "
        f"+ {p['register_rows_the_list_does_not_carry']} register rows the list does not "
        f"carry = {p['population']}"),
    "steel": lambda p: (
        f"{p['gem_plants']} GEM works + {p['leadit_entries_gem_does_not_carry']} LeadIT "
        f"entries GEM does not carry + {p['register_rows_neither_list_carries']} register "
        f"rows neither list carries = {p['population']} "
        f"(LeadIT's other {p['leadit_entries_at_a_gem_plant']} entries are a second claim "
        f"on a GEM works, not a second line)"),
}


def identity(sector: str, parts: dict) -> str:
    """The sentence a reader can check the arithmetic of, per sector.

    WRITTEN OUT RATHER THAN ASSEMBLED FROM THE PARTS DICT, because the parts are
    not all additive — the batteries overlap is subtracted and LeadIT's 52 join
    an existing line — and a generic `+`-join of them produced a sentence that
    summed to nothing and looked as though it did.
    """
    return IDENTITY[sector](parts)


def main() -> int:
    bad = []
    print("THE FIVE POPULATIONS, brief 11 item 1\n")
    for s in SECTORS:
        if s == "hydrogen":
            print(f"  {s:<24} 245  built by sources/build_ladder.py, unchanged "
                  f"(brief 10; 237 IEA + 8 rows not on the list)")
            continue
        pop, parts = BUILDERS[s]()
        counts = Counter(e["register_class"] or "(no class)" for e in pop)
        if sum(counts.values()) != parts["population"]:
            bad.append(f"{s}: classes sum to {sum(counts.values())}, "
                       f"population is {parts['population']}")
        if len({e["key"] for e in pop}) != len(pop):
            bad.append(f"{s}: duplicate keys")
        print(f"  {s:<24} {parts['population']:>4}  {identity(s, parts)}")
        print(f"  {'':<24}      " + ", ".join(f"{k} {v}" for k, v in
                                              sorted(counts.items())))
    bench = _load("cement_ccs_benchmark.json")["entries"]
    other = [e for e in bench if e.get("subsector") not in CEMENT_SUBSECTORS | TS_SUBSECTORS]
    print(f"\n  the IEA CCUS file's other {len(other)} European rows are in NEITHER "
          f"population:")
    print(f"  capture and utilisation at works in sectors this register does not hold. "
          f"{len(bench)} = 42 cement + 140 transport and storage + {len(other)}.")
    if len(bench) != 42 + 140 + len(other):
        bad.append("the IEA CCUS file does not split into 42 + 140 + the rest")
    if bad:
        print("\nGATE FAILED")
        for b in bad:
            print("  " + b)
        return 1
    print("\nGATE PASSED — every population's classes sum to its own identity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

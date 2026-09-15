#!/usr/bin/env python3
"""The cement and CCS census: one outside list, every entry in exactly one class.

    python3 sources/build_cement_ccs_benchmark.py     # the tables, and the gate

THE LIST. The IEA CCUS Projects Database, 2026 edition — "IEA CCUS Projects
Database 2026.xlsx", updated 27/03/2026, project announcements as of February
2026. 1110 project rows worldwide; the census is of the 425 the publisher's own
`Region` column calls Europe. THE SUBSET IS THE PUBLISHER'S AND NOT THIS
REGISTER'S: no judgement of ours picks the 425, which is the only reason a gap
table over them is allowed to claim it sums to the list.

The file is held by hash and not by copy — sources/benchmark_snapshots.json,
`iea_ccus_projects_database`, where the IEA's two statements about its own
licence are recorded rather than reconciled. Entries are keyed by the IEA's own
`ID`, which is what the brief means by the benchmark's own identifier.

THERE IS NO SECOND LIST FOR THIS SECTOR AND NO DRIFT TABLE. Both absences are
findings, and each has a reason that is not the same as the other's:

  CO2RE, the Global CCS Institute's facilities database, is the second list the
  brief names, and it is DROPPED — not deferred. Its facilities table is a Power
  BI publish-to-web embed with export disabled. Read in a browser by George
  Christopoulos on 14 September 2026 (Region EUROPE, Location All, Facility
  Status All) it renders rows a person can read, and it never states how many
  rows Europe has. A gap table is gated on summing to the list's own entry count,
  and an embed that shows rows without ever stating their number cannot supply
  one. That is the refusal class: READABLE, NOT ENUMERABLE.

  DRIFT IS NOT MEASURABLE FOR THIS SECTOR. Drift needs two vintages and this
  register has one. The IEA product page's Schedule tab records past releases —
  April 2025, March 2024, March 2023 — and its Data sets tab offers exactly one
  file, the 2026 edition; no past-edition URL exists in the page. This is a fact
  about what this register holds, NOT a finding about the list.

CLASSES, AND THE GATE. Each of the 425 ends in exactly one class and the counts
must sum to 425 or this script exits non-zero.

THE OUT-OF-PERIMETER CLASSES ARE DERIVED, NOT TRANSCRIBED. An entry whose
sector the perimeter does not hold is refused on the publisher's own `Subsector`
value, mechanically, in `perimeter_clause()` below — 243 entries. Hand-listing
them would have invited a typo to become a class. The clause NAMES THE INDUSTRY,
per sources/scope.md "Sector perimeters": those entries are read later for the
supplier nodes and a refusal recording only "out of perimeter" throws away the
one fact that makes the later read possible.

THE IN-PERIMETER ENTRIES ARE WORKED BY HAND, one at a time, in
sources/cement_ccs_entries.json — 42 cement and 140 CO2 transport and storage.
Each carries its class, the sources read, and for an admission the capacity AT
THE UNIT THE COMPANY STATED.

NO CAPACITY COMES OFF THIS LIST. The IEA publishes two capacity columns and one
of them, "Estimated capacity by IEA", is the IEA's own computation from plant
details through the conversion factors on the workbook's Definitions tab. The
brief says no capacity conversion, capacity at the unit stated, so neither IEA
column is ever written onto a row: an admitted row takes the figure its owner
states or it carries none. Where the list's figure and the company's differ, both
are recorded as a disagreement and neither is reconciled.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from collections import Counter, OrderedDict

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "sources" / "cache" / "ccs" / "iea_ccus_projects_2026.xlsx"
SHEET = "DRAFT CCUS Projects Database"
HAND = ROOT / "sources" / "cement_ccs_entries.json"
OUT = ROOT / "sources" / "cement_ccs_benchmark.json"

CLASSES = ("held", "admitted", "named not admitted", "searched none found",
           "unreadable", "perimeter exclusion", "not searched",
           "held for ruling", "benchmark aggregate")

# The named Europe of sources/scope.md, "Sector perimeters": the twenty-seven
# member states, the United Kingdom, Norway, Switzerland, the Western Balkans and
# Ukraine. ICELAND IS NOT ON IT, and the IEA's European region carries ten
# Icelandic entries — Carbfix, Climeworks and the Coda terminal among them. They
# are refused on geography rather than on anything about the works. The list is
# closed, so this is the rule applying and not a gap in it; it is printed by name
# in the report because ten entries is a consequence a reader should see.
EUROPE = {
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark",
    "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
    "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    "United Kingdom", "Norway", "Switzerland",
    "Albania", "Bosnia and Herzegovina", "Kosovo", "Montenegro",
    "North Macedonia", "Serbia", "Ukraine",
}

# The IEA spells Iceland two ways in one column — "Iceland" (7 entries) and
# "Island" (3, the Coda terminal phases). Recorded as the publisher's variant,
# not corrected: both are refused on geography either way, and a register that
# silently normalised a publisher's spelling would be editing the list it counts.
GEOGRAPHY_VARIANTS = {"Island": "Iceland"}

# What the perimeter holds, by the publisher's own Subsector.
IN_PERIMETER_SUBSECTORS = {"Cement", "CO2 T&S", "CO2 transport", "CO2 storage"}

# The clause an out-of-perimeter entry is refused with, by Subsector. The
# industry is NAMED: sources/scope.md, CCS — "capture, refinery", "capture,
# waste-to-energy", "capture, chemicals" — rather than one clause for all.
CAPTURE_CLAUSES = {
    "Iron and steel": "capture, iron and steel",
    "Chemicals": "capture, chemicals",
    "Fertiliser": "capture, fertiliser",
    "Lime": "capture, lime",
    "Pulp and paper": "capture, pulp and paper",
    "Aluminium": "capture, aluminium",
    "Other industry": "capture, other industry",
    "Natural gas processing/LNG": "capture, natural gas processing",
    "Hydrogen or ammonia": "capture, hydrogen or ammonia",
    "Refining": "capture, refining",
    "Biogas": "capture, biogas",
    "Biodiesel": "capture, biodiesel",
    "Bioethanol": "capture, bioethanol",
    "Power (bioenergy)": "capture, power (bioenergy)",
    "Power and heat (waste)": "capture, waste-to-energy",
    "Power (gas)": "capture, power (gas)",
    "Power (coal)": "capture, power (coal)",
    "Direct Air Capture": "direct air capture, no host works",
}

# IRON AND STEEL IS NAMED OUT HERE AND HELD IN ANOTHER SECTOR, and the two are
# not in conflict. The cement perimeter holds capture at a CEMENT works; the
# steel perimeter (brief 8 sector 3) holds a route change in the iron, which a
# capture unit bolted to a blast furnace is not. An entry refused here with
# "capture, iron and steel" is refused by THIS sector's perimeter and says
# nothing about whether the steel census holds the works.


def entries() -> list[dict]:
    wb = openpyxl.load_workbook(BOOK, read_only=True, data_only=True)
    ws = wb[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    hdr = list(rows[0])
    return [dict(zip(hdr, r)) for r in rows[1:] if r[1] is not None]


def european() -> list[dict]:
    return [d for d in entries() if d["Region"] == "Europe"]


def countries(d: dict) -> list[str]:
    """One entry may name several. 'Poland, Latvia, Lithuania', 'France-Italy'."""
    raw = str(d["Country or economy"] or "")
    parts = [p.strip() for p in raw.replace("-", ",").split(",") if p.strip()]
    return [GEOGRAPHY_VARIANTS.get(p, p) for p in parts]


def in_europe(d: dict) -> bool:
    """A cross-border entry is in if ANY of the countries it names is.

    A pipeline from Zeebrugge to Germany is European infrastructure whichever
    end a reader stands at, and an entry that named one country on the list and
    one off it would otherwise leave on a technicality.
    """
    cs = countries(d)
    if not cs or cs == ["Unknown"]:
        return False
    if cs == ["Multiple Europe"]:
        return True
    return any(c in EUROPE for c in cs)


def perimeter_clause(d: dict) -> str | None:
    """The clause this entry is refused with, or None if it is in perimeter.

    Geography is tested first and named as geography: an Icelandic cement works
    would be out because it is Icelandic, and recording it as an industry
    refusal would say something false about the industry.
    """
    if not in_europe(d):
        named = "/".join(countries(d)) or "unstated"
        return f"geography, outside the named Europe ({named})"
    sub = d["Subsector"]
    if sub in IN_PERIMETER_SUBSECTORS:
        return None
    if sub in CAPTURE_CLAUSES:
        return CAPTURE_CLAUSES[sub]
    return f"out of perimeter, subsector not in the vocabulary ({sub})"


def hand() -> dict:
    if not HAND.exists():
        return {"_comment": [], "entries": {}}
    return json.loads(HAND.read_text(encoding="utf-8"))


def build() -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    h = hand()["entries"]
    out = []
    for d in european():
        iid = str(d["ID"])
        clause = perimeter_clause(d)
        rec = {
            "iea_id": d["ID"],
            "name": d["Project name"],
            "country": d["Country or economy"],
            "project_type": d["Project type"],
            "subsector": d["Subsector"],
            "iea_status": d["Project status"],
            "iea_phase": d["Project phase"],
            "iea_announced_capacity_mt": d["Announced capacity (Mt CO2/yr)"],
            "iea_estimated_capacity_mt": d["Estimated capacity by IEA (Mt CO2/yr)"],
        }
        if clause is not None and iid not in h:
            rec["class"] = "perimeter exclusion"
            rec["clause"] = clause
            rec["derived"] = True
        elif iid in h:
            rec.update(h[iid])
            rec["derived"] = False
            if clause is not None and rec.get("class") != "perimeter exclusion":
                problems.append(
                    f"{iid}: hand entry classes it '{rec.get('class')}' but the "
                    f"perimeter refuses it — {clause}")
        else:
            rec["class"] = "not searched"
            rec["derived"] = False
        out.append(rec)
    return out, problems


def table(rows: list[dict], title: str, expected: int) -> tuple[bool, list[str]]:
    counts = Counter(r["class"] for r in rows)
    bad = [c for c in counts if c not in CLASSES]
    total = sum(counts.values())
    print(f"\n{title}")
    print("| class | entries |")
    print("|---|---|")
    for c in CLASSES:
        if counts.get(c):
            print(f"| {c} | {counts[c]} |")
    print(f"| **TOTAL** | **{total}** |")
    problems = []
    if bad:
        problems.append(f"classes not in the vocabulary: {bad}")
    if total != expected:
        problems.append(f"table sums to {total}, the list has {expected} entries")
    else:
        print(f"GATE: sums to the list's own {expected} European entries.")
    return not problems, problems


def main() -> int:
    rows, problems = build()
    ok, p = table(rows, "THE IEA CCUS PROJECTS DATABASE 2026, European entries — "
                        "the gap table", 425)
    problems += p

    # --- the two absences, printed rather than left to be noticed ------------
    print("\nDRIFT — not measurable for this sector, and why")
    print("  One vintage held: the 2026 edition, announcements as of February 2026.")
    print("  The IEA product page's Schedule tab records past releases (April 2025,")
    print("  March 2024, March 2023); its Data sets tab offers one file and the page")
    print("  carries no past-edition URL. This is what this register holds. It is not")
    print("  a finding about the list.")

    print("\nSECOND LIST — dropped, with the refusal class")
    print("  CO2RE (Global CCS Institute) — READABLE, NOT ENUMERABLE. A Power BI")
    print("  publish-to-web embed with export disabled; rows render for a person and")
    print("  the row count is never stated. A gap table gated on the list's own entry")
    print("  count cannot be built on it.")

    # --- by perimeter, so a reader can see what the sector actually held -----
    print("\nWHAT THE PERIMETER HELD, of the 425")
    held_in = [r for r in rows if r["class"] != "perimeter exclusion"]
    excl = [r for r in rows if r["class"] == "perimeter exclusion"]
    print(f"  in perimeter: {len(held_in)}   refused by the perimeter: {len(excl)}")
    by_clause = Counter(r.get("clause", "?") for r in excl)
    print("\n| refusal clause | entries |")
    print("|---|---|")
    for c, n in by_clause.most_common():
        print(f"| {c} | {n} |")

    print("\nNOT SEARCHED — the only class that is a defect, printed by name")
    ns = [r for r in rows if r["class"] == "not searched"]
    if not ns:
        print("  none")
    for r in ns:
        print(f"  {r['iea_id']:>5} {r['name'][:60]} ({r['subsector']})")

    print("\nHELD FOR RULING — questions the perimeter does not settle")
    hr = [r for r in rows if r["class"] == "held for ruling"]
    if not hr:
        print("  none")
    for r in hr:
        print(f"  {r['iea_id']:>5} {r['name'][:60]} — {r.get('question', '')[:80]}")

    print("\nADMITTED BY THIS PASS")
    adm = [r for r in rows if r["class"] == "admitted"]
    for r in adm:
        cap = r.get("capacity_stated") or "no capacity stated by the owner"
        print(f"  {r['iea_id']:>5} {r['name'][:44]:<44} → {r.get('row', '?'):<28} {cap}")
    print(f"  {len(adm)} row(s).")

    hm = hand()
    doc = {"_comment": __doc__.strip().splitlines(),
           "generated": "2026-09-14",
           "benchmark": "iea_ccus_projects_database",
           "vintage": "2026 edition, updated 27/03/2026, announcements as of "
                      "February 2026",
           "entry_list": "Sheet 'DRAFT CCUS Projects Database', 1110 project rows "
                         "worldwide, 425 with Region=Europe. The European subset is "
                         "the publisher's own column, not this register's judgement.",
           "second_list": {
               "benchmark": "global_ccs_institute",
               "outcome": "dropped",
               "refusal_class": "readable, not enumerable",
               "read_on": "2026-09-14",
               "read_by": "George Christopoulos",
               "how": "co2re.co/FacilityData in a browser, Region EUROPE, Location "
                      "All, Facility Status All; columns Country, Name, Facility "
                      "Status, Operational Year, Industry, Facility Type, Capture "
                      "Capacity (Max; mtpa).",
               "why": "The facilities table is an app.powerbi.com publish-to-web "
                      "embed with export disabled. It renders rows a person can "
                      "read and never states how many rows the filter returns. A "
                      "gap table is gated on summing to the list's own entry count, "
                      "and this list does not publish one.",
               "evidence": "sources/manual/co2re-facilities--europe-filter-"
                           "2026-09-14.png"},
           "drift": {"measurable": False,
                     "why": "One vintage held. The IEA product page's Schedule tab "
                            "records past releases (April 2025, March 2024, March "
                            "2023) and its Data sets tab offers only the 2026 file; "
                            "no past-edition URL is in the page. This records what "
                            "this register holds and is not a finding about the "
                            "list."},
           "entries": rows,
           "disagreements": hm.get("disagreements", []),
           "reference_debts": hm.get("reference_debts", [])}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
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

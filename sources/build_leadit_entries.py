#!/usr/bin/env python3
"""THE SECOND LIST, ENTRY BY ENTRY: LeadIT's Green Steel Tracker against GEM's.

    python3 sources/build_leadit_entries.py        # writes sources/leadit_entries.json

WHY A SECOND LIST AT ALL, AND WHY THIS ONE. GEM's tracker carries only plants at 0.5 mtpa
crude iron/steel and above -- its own About tab says so -- and the steel perimeter sets NO
tonnage threshold, deliberately: "a small DRI module and a large one are the same kind of
fact about a works leaving the blast furnace, and a threshold would drop the early ones --
which are disproportionately the ones that stop". Every coverage figure in the first-list
table therefore carries GEM's floor. LeadIT sets no floor. It is the second list for
exactly that reason and the first-list pass said so before this one was run.

THE POPULATION IS LEADIT'S OWN COLUMN, FILTERED BY THE PERIMETER'S OWN GEOGRAPHY. 161
project rows worldwide on the `3. All Projects` sheet; 68 whose `Continent` is Europe; 65
whose `Country` is one of the EU, the United Kingdom, Norway or Switzerland -- the four
named in the steel perimeter. Türkiye (2) and Russia (1) are in LeadIT's Europe and not in
the perimeter's, and they are counted out here rather than dropped quietly.

THE JOIN IS THE PUBLISHER'S OWN KEY WHERE THERE IS ONE, AND A HAND MATCH WHERE THERE IS
NOT. LeadIT carries a `GEM Plant ID` column: 49 of the 65 name a plant in GEM's 132 and
join on it, with no name matching anywhere in this pass. THREE MORE ARE AT PLANTS GEM DOES
CARRY AND LEADIT HAS NOT LINKED -- SSAB Raahe, Stegra's Spanish plant and Outokumpu Tornio
-- and those three are matched BY HAND, by works, and the line says so. That is a finding
about the cross-reference, not a licence to fold names together: the diacritic ruling in
the docket is what a name match costs.

THE REMAINING THIRTEEN ARE NEW TO THIS REGISTER and are classed here, against the same
perimeter and by the same rule the first list was worked under: the company's own document
or nothing.
"""
from __future__ import annotations
import json, pathlib, warnings
warnings.filterwarnings("ignore")
import openpyxl

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "sources" / "cache" / "steel" / "leadit_green_steel_tracker.xlsx"
GEM = ROOT / "sources" / "steel_entries.json"
OUT = ROOT / "sources" / "leadit_entries.json"

# The steel perimeter's Europe, from sources/scope.md: the EU, the United Kingdom, Norway
# and Switzerland. Written out rather than imported so that a change to one is not a silent
# change to the other.
PERIMETER_EUROPE = {
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia",
    "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania",
    "Slovakia", "Slovenia", "Spain", "Sweden", "United Kingdom", "Norway", "Switzerland"}

# THE THREE LEADIT LEAVES AT A GEM PLANT THAT LEADIT HAS NOT LINKED. Matched by works, by
# hand, one at a time, and named here so the hand step is auditable rather than implied.
HAND_MATCHED = {
    "GST-088": ("P100000120468", "SSAB Raahe steel plant"),
    "GST-040": ("P100000121222", "Stegra Spain steel plant"),
    "GST-161": ("P100000120469", "Outokumpu Tornio steel plant"),
}

# THE THIRTEEN GEM DOES NOT CARRY, CLASSED HERE. Each carries the class, the clause or the
# leg, and where a company was read, what it said.
NEW = {
 "GST-016": {
   "class": "admitted", "leg": "announced DRI plant",
   "speaker": "HyIron, own site",
   "source": "https://hyiron.com/",
   "verbatim": ("The project GEiSt (German for “Green Iron for the steel Industry”) "
                "pilots the technology in Lingen, Germany, in cooperation with RWE and "
                "Benteler. The main purpose of the pilot plant is to optimize the process "
                "and test various iron ores"),
   "note": ("THE SECOND LIST'S FIRST ADMISSION, AND IT IS EXACTLY WHAT THE FLOOR HID. A "
            "hydrogen direct-reduction plant at Lingen, confirmed by its owner on its own "
            "site, at a scale GEM's 0.5 mtpa threshold cannot carry. The perimeter sets no "
            "tonnage threshold and gives the reason in as many words -- the early ones are "
            "disproportionately the ones that stop -- so a pilot that reduces iron with "
            "hydrogen is an announced DRI plant on the perimeter's own terms. RWE and "
            "Benteler are named by the owner as partners; the register holds neither as "
            "the owner of this plant.")},
 "GST-011": {
   "class": "perimeter exclusion",
   "clause": "research pilot of an electrolytic iron route; none of the four legs",
   "note": ("SIDERWIN is iron by electrolysis -- neither DRI, nor an EAF against a blast "
            "furnace, nor greenfield DRI/EAF, nor a hydrogen-ready furnace. It is a "
            "primary route change and the perimeter does not name it, which is a gap in "
            "the perimeter rather than a fact about the project: asked as S5.")},
 "GST-023": {
   "class": "perimeter exclusion",
   "clause": "equipment vendor's test centre, no primary capacity at a works",
   "note": ("Metso's DRI smelting furnace pilot at Pori is a technology supplier proving a "
            "furnace at its own research centre. No works changes route here, and the "
            "perimeter holds works.")},
 "GST-059": {
   "class": "perimeter exclusion",
   "clause": "hydrogen supply to a works; fuel switch, no primary route change",
   "note": ("SeaH2Land is offshore-wind hydrogen for the Zeeland cluster. It is the same "
            "shape the ArcelorMittal Sestao clause was written for: the hydrogen is an "
            "input and the iron is counted at the works that makes it.")},
 "GST-067": {
   "class": "perimeter exclusion", "clause": "CO2 transport and storage, not steel",
   "note": "LeadIT disqualifies it itself -- 'Not explicitly for steel'. Northern Lights is "
           "the CCS service this register holds in the CCS sector, not in steel."},
 "GST-072": {
   "class": "perimeter exclusion", "clause": "hydrogen supply, not steel",
   "note": "Blue hydrogen for the Humber. LeadIT's own reason is 'Not explicitly for "
           "steel' and the perimeter reaches the same answer by the four legs."},
 "GST-084": {
   "class": "perimeter exclusion", "clause": "hydrogen imports, not one of the four legs",
   "note": "H-vision is hydrogen supply into Rotterdam. LeadIT records it as having no new "
           "updates; the perimeter refuses it whatever its state."},
 "GST-093": {
   "class": "perimeter exclusion", "clause": "hydrogen supply, not steel",
   "note": "HyDeal Espana at Asturias supplies hydrogen; ArcelorMittal's Gijon works is "
           "admitted at ref P100000120458 on its own DRI announcement, and the iron is "
           "counted once, there."},
 "GST-125": {
   "class": "perimeter exclusion", "clause": "a consortium, not a project",
   "note": "LeadIT's own reason, and this register's too: there is no works and no unit."},
 "GST-070": {
   "class": "named not admitted",
   "note": ("THE LIST CARRIES NO PROJECT NAME: LeadIT writes 'Not available' and its own "
            "reason is 'Not enough information'. What it does carry is a company and a "
            "site -- Salzgitter at Wilhelmshaven, a DRI feasibility study. A feasibility "
            "study is not a company-confirmed plant and the entry is named not admitted "
            "rather than searched, because there is no project name to search for.")},
 "GST-094": {
   "class": "named not admitted",
   "note": ("The second of LeadIT's two unnamed Salzgitter Wilhelmshaven rows, this one "
            "an electrolysis study. Same answer and for the same reason.")},
 "GST-120": {
   "class": "named not admitted",
   "note": ("A memorandum of understanding between GreenIron and Vale to study hydrogen "
            "reduction at Sandviken. LeadIT's own note says it is saved 'in prospective "
            "for future updates'. An agreement to study is not a company-confirmed "
            "plant.")},
 "GST-158": {
   "class": "named not admitted",
   "speaker": "Marcegaglia, own site",
   "source": "https://www.marcegaglia.com/en/press-room",
   "note": ("QUALIFIED BY LEADIT AND NOT SOURCEABLE FROM THE OWNER, AND THE REASON IS A "
            "SHAPE THIS REGISTER HAS A RULE FOR ONE STEP OVER. marcegaglia.com answers a "
            "declared reader with 200 and 21,704 characters on EVERY path tried -- the "
            "front page, the English and Italian press rooms, and a project URL -- and the "
            "body is byte-identical each time: a single-page application serving one shell "
            "and rendering its content in a browser. scope.md calls a 200 with an EMPTY "
            "body a refusal; this is a 200 with the SAME body, which is the same failure "
            "wearing a different number, and it is recorded against the URLs rather than "
            "against the project. AdriatiCO2 at Ravenna would be an announced DRI plant if "
            "the owner's own words could be read; until they are, the entry is named not "
            "admitted, exactly as Port Talbot was under S3.")},
}


def main() -> int:
    wb = openpyxl.load_workbook(BOOK, read_only=True, data_only=True)
    ws = wb["3. All Projects"]
    rows = [r for r in ws.iter_rows(values_only=True)]
    cols = [str(c).strip() if c else "" for c in rows[4]]
    ix = {c: i for i, c in enumerate(cols) if c}
    data = [r for r in rows[5:] if r and r[0]]
    wb.close()

    def g(r, c):
        v = r[ix[c]] if c in ix else None
        return "" if v is None else str(v).strip()

    gem = json.loads(GEM.read_text(encoding="utf-8"))["entries"]
    europe = [r for r in data if g(r, "Continent").lower() == "europe"]
    pop = [r for r in europe if g(r, "Country") in PERIMETER_EUROPE]
    outside = [g(r, "Country") for r in europe if g(r, "Country") not in PERIMETER_EUROPE]

    entries = {}
    for r in pop:
        gid = g(r, "GEM Plant ID")
        key = g(r, "Internal ID")
        joined, how = None, None
        if gid in gem:
            joined, how = gid, "LeadIT's own GEM Plant ID"
        elif key in HAND_MATCHED:
            joined, how = HAND_MATCHED[key][0], ("by works, by hand — LeadIT carries no "
                                                 "GEM Plant ID for this row")
        e = {
            "name": g(r, "Project name"),
            "company": g(r, "Company"),
            "country": g(r, "Country"),
            "site": g(r, "Location (specific)"),
            "leadit_claim": {
                "benchmark": "leadit_green_steel_tracker",
                "vintage": "2026-09-04",
                "qualified_for_tracker": g(r, "Qualified for Tracker"),
                "reason_leadit_gives": g(r, "Reason for Disqualification/Qualification"),
                "technology_category": g(r, "Technology category"),
                "specific_equipment": g(r, "Specific equipment used"),
                "project_scale": g(r, "Project scale"),
                "project_status": g(r, "Project status"),
                "planned_commissioning": g(r, "Planned commissioning"),
                "actual_start_year": g(r, "Actual start year (yyyy)"),
                "gem_plant_named": g(r, "GEM Production plant"),
                "gem_plant_id": gid,
                "note": ("A BENCHMARK CLAIM, NOT A CLASS. LeadIT's columns say what LeadIT "
                         "knows as of its 2026-09-04 version. Its `Qualified for Tracker` "
                         "value is ITS OWN editorial test and is never this register's "
                         "class: a row LeadIT disqualifies may be admitted here and a row "
                         "it qualifies may be refused by the perimeter."),
            },
            "gem": {"key": joined,
                    "name": gem[joined]["name"] if joined else "",
                    "class": gem[joined].get("class") if joined else None,
                    "matched_on": how or "not in GEM's 132 European plants"},
        }
        if joined:
            e["class"] = gem[joined].get("class")
            e["class_from"] = ("the first-list census, inherited on the join — this pass "
                               "re-classes nothing GEM already carries")
        else:
            hand = NEW.get(key)
            if hand is None:
                e["class"] = "not searched"
            else:
                e.update(hand)
                e["class_from"] = "classed by this pass; GEM does not carry this works"
        entries[key] = e

    doc = {"_comment": __doc__.strip().splitlines(),
           "generated": "2026-09-18",
           "benchmark": "leadit_green_steel_tracker",
           "vintage": "2026-09-04",
           "population": len(pop),
           "leadit_europe": len(europe),
           "outside_the_perimeter_geography": sorted(set(outside)),
           "entries": entries}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"LeadIT Europe {len(europe)} rows; in the perimeter's geography {len(pop)}; "
          f"outside it {sorted(set(outside))}")
    print(f"joined to GEM: {sum(1 for e in entries.values() if e['gem']['key'])} "
          f"({sum(1 for e in entries.values() if e['gem']['matched_on'].startswith('LeadIT'))} "
          f"on LeadIT's own key, "
          f"{sum(1 for e in entries.values() if e['gem']['matched_on'].startswith('by works'))} "
          f"by hand)")
    print(f"new to this register: {sum(1 for e in entries.values() if not e['gem']['key'])}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

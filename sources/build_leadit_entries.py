#!/usr/bin/env python3
"""THE SECOND LIST, ENTRY BY ENTRY: LeadIT's Green Steel Tracker against GEM's.

    python3 sources/build_leadit_entries.py           # writes sources/leadit_entries.json
    python3 sources/build_leadit_entries.py --check   # recomputes and refuses a mismatch

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

THIS STEP IS NOT IN THE BUILD CHAIN, AND THE RULE SAYS WHY. It opens a workbook with
openpyxl, and the workbook is in the gitignored cache. scope.md, "A build-time gate reads
tracked files only": a step that needs a package or a byte the build image does not have
runs in the local pre-push chain, where the machine that has those things is the one
running it. So `sources/leadit_entries.json` is MATERIALISED -- a tracked derived file --
and it carries the SHA-256 of the workbook it was read from. `--check` recomputes the whole
file from the workbook and refuses a mismatch; it passes quietly where the workbook is
absent, because a contributor without it is still entitled to push. The tracked-only half
of the check is in build_steel_second_list.py, which runs in prebuild and verifies the
recorded hash against the one benchmark_snapshots.json pins.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys, warnings
warnings.filterwarnings("ignore")

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
   "class": "admitted",
   "admitted_by": "funder",
   "owner_leg": "open — no owner document on file; owner look queued under rule 17",
   "row": "adriatico2-ravenna",
   "leg": "announced DRI plant",
   "speaker": "European Commission (CINEA), Innovation Fund project factsheet — THE FUNDER, NOT THE OWNER",
   "source": "https://ec.europa.eu/assets/cinea/project_fiches/innovation_fund/101191172.pdf",
   "verbatim": "The project, led by Marcegaglia Ravenna S.p.A., aims to reduce CO2 emissions in the Ravenna industrial district through Carbon Capture Utilisation and Storage (CCUS) technologies.",
   "amount_as_stated": "EUR 31,238,542",
   "class_before_20_september": "named not admitted",
   "note": "ADMITTED BY THE FUNDER, 20 September 2026, under the amendment of that day. THE ORIGINAL CLASS WAS NOT A SEARCH MISS. `named not admitted` was correct on the evidence: question S6 records that marcegaglia.com answers 200 with one identical body on every path — 21,704 characters on 18 September, 21,711 on 20 September, the same on /en/sustainability and /en/media/press-releases — so the owner's own words are unreadable to a declared reader and no amount of searching would have reached them. The funder's document is readable and names the company, the district and the technology. The owner leg is open and an owner look is queued under rule 17; S6 stays open with it.",
   "owner_look": {
     "why": "A FUNDER HAS SPOKEN AND THE OWNER HAS NOT, and this entry has no register row for the event to sit on — the steel census admits a works and proposes a row id, and nothing has landed. The look is rule 17's: whether the OWNER's source still stands.",
     "queued": "2026-09-20",
     "no_row_yet": "adriatico2-ravenna",
     "urls": [
      {
       "publisher": "Marcegaglia (one identical body on every path — S6)",
       "url": "https://www.marcegaglia.com/en/sustainability"
      },
      {
       "publisher": "Marcegaglia Ravenna",
       "url": "https://www.marcegaglia.com/en/"
      },
      {
       "publisher": "Emilia-Romagna permitting authority",
       "url": "https://ambiente.regione.emilia-romagna.it/"
      }
     ]
    }},
}


def build() -> dict:
    import openpyxl  # LAZY: the build image has neither this nor the workbook.
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
           "source_file": str(BOOK.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(BOOK.read_bytes()).hexdigest(),
           "source_bytes": BOOK.stat().st_size,
           "source_note": ("THE BYTES ARE NOT IN THE REPOSITORY AND THE HASH IS. "
                           "This file is a tracked derived file so the build image never "
                           "opens a workbook; the hash is what lets a reader fetch the "
                           "same file from LeadIT and prove these rows came from it. "
                           "build_steel_second_list.py checks it against the pin in "
                           "benchmark_snapshots.json on every build."),
           "population": len(pop),
           "leadit_europe": len(europe),
           "outside_the_perimeter_geography": sorted(set(outside)),
           "entries": entries}
    return doc


def report(doc) -> None:
    entries = doc["entries"]
    print(f"LeadIT Europe {doc['leadit_europe']} rows; in the perimeter's geography "
          f"{doc['population']}; outside it {doc['outside_the_perimeter_geography']}")
    print(f"joined to GEM: {sum(1 for e in entries.values() if e['gem']['key'])} "
          f"({sum(1 for e in entries.values() if e['gem']['matched_on'].startswith('LeadIT'))} "
          f"on LeadIT's own key, "
          f"{sum(1 for e in entries.values() if e['gem']['matched_on'].startswith('by works'))} "
          f"by hand)")
    print(f"new to this register: {sum(1 for e in entries.values() if not e['gem']['key'])}")


def main() -> int:
    check = "--check" in sys.argv
    if not BOOK.exists():
        # QUIETLY, AND SAYING SO. A contributor without the workbook is still entitled to
        # push; a step that is silent about skipping is the failure mode this split exists
        # to avoid, so it names what it did not do.
        print(f"build_leadit_entries: {BOOK.relative_to(ROOT)} is not on this machine, so "
              f"the workbook was not read. sources/leadit_entries.json stands as committed; "
              f"its hash is checked against benchmark_snapshots.json in prebuild.")
        return 0
    doc = build()
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if check:
        have = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if have != text:
            print("build_leadit_entries --check: FAILED. The workbook does not produce the "
                  "committed sources/leadit_entries.json.")
            old = json.loads(have) if have else {}
            if old.get("source_sha256") != doc["source_sha256"]:
                print(f"  the workbook on this machine hashes "
                      f"{doc['source_sha256'][:16]}…; the file records "
                      f"{str(old.get('source_sha256'))[:16]}… — A DIFFERENT FILE.")
            else:
                print("  same workbook, different rows: the builder or a hand class "
                      "changed and the derived file was not rebuilt.")
            return 1
        report(doc)
        print(f"build_leadit_entries --check: {OUT.relative_to(ROOT)} recomputes from the "
              f"workbook, entry by entry, and matches.")
        return 0
    OUT.write_text(text, encoding="utf-8")
    report(doc)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

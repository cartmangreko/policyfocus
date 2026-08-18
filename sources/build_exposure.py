#!/usr/bin/env python3
"""
Build data/exposure/<slug>.json from the FIGARO flatfile.

Why this exists
---------------
The first eleven exposure files arrived as a delivered artefact: someone ran a
computation off-repo and handed over JSON. That was fine while the sector spine
was frozen, but the spine is not frozen -- PPWR adds paper, wood, food & drink,
retail, hotels & restaurants and a plastics child -- and a spine that can grow
needs a builder in the repo rather than a favour from outside it.

So this reconstructs the delivered methodology rather than inventing one. The
proof that it IS the delivered methodology is --check, which rebuilds all
eleven original files and diffs them against what is on disk. That gate passed
byte-for-byte before any new sector was written, and it is the reason the new
files can be trusted: they come out of the same arithmetic that produced the
originals, not out of a plausible-looking guess.

    python3 build_exposure.py --check        # rebuild the 11, diff, write nothing
    python3 build_exposure.py --write        # write every slug in SECTOR_CODES
    python3 build_exposure.py --write paper  # named slugs only

------------------------------------------------------------------------------
THE METHODOLOGY, as recovered
------------------------------------------------------------------------------
Source: Eurostat FIGARO 2026 edition, 2024 reference year, EU inter-country
input-output tables, industry by industry. One row is
(refArea, rowIi) -> (counterpartArea, colIi): the value that industry rowIi in
refArea sold to industry colIi in counterpartArea.

A "view" is an area whose economy we are looking at: the EU as one block, or a
single member state. For a sector with FIGARO code T and view area A:

  suppliers    rows with colIi == T and counterpartArea in A.
               Grouped by rowIi, over every refArea. Share is a percent of
               total inputs.
  customers    rows with rowIi == T and refArea in A.
               Grouped by colIi. Share is a percent of total intermediate
               output.
  import_dep   the share of total inputs whose refArea is outside A. For the
               EU view "outside" means outside the 27; for a country view it
               means outside that country, so intra-EU trade counts as import.
  origins      those foreign inputs, grouped by refArea, as a percent of
               foreign inputs.

Three exclusions carry the result, plus one redundant guard. Each was forced
by the numbers rather than assumed:

1. NON_INDUSTRY rows (D1 compensation of employees, B2A3G operating surplus,
   the tax rows, the OP_ rows) are value added, not a supplier. Leaving them in
   put D1 second on the chemicals supplier list and moved import dependency
   from 21.9 to 42.7.
2. refArea W2 is where value added is filed, NOT a world aggregate. This was
   originally recorded here as "a world aggregate that restates rows already
   present, so it double-counts", which was wrong about the mechanism. Checked
   against the flatfile on 2026-08-18: W2 carries exactly and only the six
   NON_INDUSTRY codes, and those codes appear under no other area. The 62 % of
   chemicals' foreign inputs it accounted for was value added being read as an
   import, which is correction 1 restated -- so the W2 skip is redundant and
   --check passes without it. Three corrections do the work here, not four.
3. FINAL_DEMAND columns (household, government and NPISH consumption, capital
   formation) are excluded from the customers denominator. With them in, every
   customer share was understated by a fifth; without them, all eight
   chemicals rows matched to the decimal.
4. The sector's own code is dropped from its displayed supplier and customer
   lists -- self-consumption is not a supply-chain link a reader can act on --
   but it stays in the denominator, which is why it is the OTHER row that
   absorbs it rather than the shares being rescaled.

Shares are rounded to one decimal at the end and never rescaled. OTHER is the
remainder to 100 taken BEFORE rounding, which is what the delivered files do.
"""
import argparse
import csv
import io
import json
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLATFILE_ZIP = ROOT / "data" / "flatfile_eu-ic-io_ind-by-ind_26ed_2024.zip"
EXPOSURE_DIR = ROOT / "data" / "exposure"

PROVENANCE = ("Eurostat FIGARO 2026 edition, 2024 reference year "
              "(EU inter-country input-output tables, industry by industry)")

EU27 = frozenset("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL "
                 "PL PT RO SK SI ES SE".split())

# Value added and the operating-surplus rows: not industries, not suppliers.
NON_INDUSTRY = frozenset({"B2A3G", "D1", "D21X31", "D29X39", "OP_NRES", "OP_RES"})
# Where FIGARO files value added. Not a world aggregate -- see the note in the
# docstring. Skipping it is redundant with NON_INDUSTRY and kept only as a
# guard against a future edition filing something else here.
AGGREGATE_AREA = "W2"
# Final uses. Excluded from the customers denominator.
FINAL_DEMAND = frozenset({"P3_S13", "P3_S14", "P3_S15", "P51G", "P5M", "P3"})

TOP_N = 8
OTHER = "OTHER"

# slug -> FIGARO code. Several slugs deliberately share a code: FIGARO has no
# finer split, and pretending otherwise would invent a distinction the source
# cannot support. Those pairs carry a note on the file.
SECTOR_CODES = {
    # the original eleven
    "steel": "C24", "alu": "C24", "cement": "C23", "glass": "C23",
    "chem": "C20", "power": "D35", "waste": "E37T39", "ship": "H50",
    "air": "H51", "auto": "C29", "build": "F",
    # added with the PPWR taxonomy expansion
    "paper": "C17", "wood": "C16", "foodbev": "C10T12",
    "retail": "G47", "horeca": "I", "chem/plastics": "C22",
}

ORIGINAL_ELEVEN = ("steel alu cement glass chem power waste ship air auto build").split()

SHARED_CODE_NOTE = {
    "C24": "FIGARO groups steel & alu under one code (C24); these share a profile in this data source.",
    "C23": "FIGARO groups cement & glass under one code (C23); these share a profile in this data source.",
}

SHARES_BASIS = ("percent of sector's total inputs (suppliers) / total output "
                "(customers); OTHER row carries the remainder to 100")

# Labels are lifted from the delivered files so the new sectors speak the same
# vocabulary as the old ones. The three at the end never surfaced in a top-8 of
# the original eleven, so they had no delivered label; these follow the FIGARO
# naming of the neighbouring rows.
LABELS = {
    "A01": "crop & animal farming", "A02": "forestry", "A03": "fishing",
    "B": "mining", "C10T12": "food, drink & tobacco",
    "C13T15": "textiles & clothing", "C16": "wood products", "C17": "paper",
    "C18": "printing", "C19": "refined petroleum", "C20": "chemicals",
    "C21": "pharmaceuticals", "C22": "rubber & plastics",
    "C23": "cement, glass & ceramics", "C24": "basic metals (steel & aluminium)",
    "C25": "fabricated metal products", "C26": "electronics",
    "C27": "electrical equipment", "C28": "machinery", "C29": "vehicles",
    "C30": "other transport equipment", "C31_32": "furniture & other manufacturing",
    "C33": "machinery repair", "D35": "electricity & gas", "E36": "water supply",
    "E37T39": "waste & sewerage", "F": "construction", "G45": "vehicle trade",
    "G46": "wholesale trade", "G47": "retail trade", "H49": "land transport",
    "H50": "water transport", "H51": "air transport", "H52": "warehousing",
    "H53": "postal", "I": "hotels & restaurants", "J58": "publishing",
    "J59_60": "film & broadcasting", "J61": "telecoms", "J62_63": "IT services",
    "K64": "finance", "K65": "insurance", "K66": "other finance",
    "L": "real estate", "M69_70": "legal, accounting & consulting",
    "M71": "architecture & engineering", "M72": "R&D", "M73": "advertising",
    "M74_75": "other professional", "N77": "leasing",
    "N78": "employment agencies", "N79": "travel agencies",
    "N80T82": "security & facilities", "O84": "public administration",
    "P85": "education", "Q86": "health", "Q87_88": "social work",
    "R90T92": "arts", "R93": "sport & recreation", "S94": "membership orgs",
    "S95": "repair of computers & personal goods", "S96": "other services",
    "T": "household activities", "U": "extraterritorial bodies",
    "FIGW1": "rest of world", OTHER: "everything else",
}


def label_for(code):
    """Industries come from LABELS; a country is its own label, as delivered."""
    if code in LABELS:
        return LABELS[code]
    if code.isalpha() and len(code) == 2:
        return code
    raise KeyError(f"no label for FIGARO code {code!r}; add it to LABELS")


# ---------------------------------------------------------------------------
# The single pass
# ---------------------------------------------------------------------------

def stream_rows():
    """
    Yield (refArea, rowIi, counterpartArea, colIi, value) from the zipped
    flatfile. The CSV is 390 MB uncompressed, so it is never written to disk:
    the zip member is read as a stream and parsed a line at a time.
    """
    with zipfile.ZipFile(FLATFILE_ZIP) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as raw:
            reader = csv.reader(io.TextIOWrapper(raw, encoding="utf-8", newline=""))
            header = next(reader)
            expected = ["icioiRow", "icioiCol", "refArea", "rowIi",
                        "counterpartArea", "colIi", "obsValue"]
            if header != expected:
                raise SystemExit(f"unexpected FIGARO header: {header}")
            for row in reader:
                yield row[2], row[3], row[4], row[5], float(row[6])


def accumulate(codes):
    """
    One pass, every requested FIGARO code at once.

    Returns nested dicts keyed [code][view] where view is "EU" or a member
    state. Reading the 390 MB file once per sector would be sixteen passes for
    no gain; the accumulators are a few tens of thousands of floats.
    """
    codes = set(codes)
    sup = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    final = defaultdict(lambda: defaultdict(float))
    cus = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    org = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    tot_in = defaultdict(lambda: defaultdict(float))
    tot_out = defaultdict(lambda: defaultdict(float))
    foreign = defaultdict(lambda: defaultdict(float))

    for ref, row, cp, col, val in stream_rows():
        # refArea W2 is where FIGARO files VALUE ADDED. Checked against the
        # 2026-edition flatfile: W2 carries exactly and only the six
        # NON_INDUSTRY codes, and those codes appear under no other area. So
        # this skip is REDUNDANT -- NON_INDUSTRY already removes everything W2
        # holds, and --check reproduces all eleven delivered files with this
        # line deleted. It is kept as a cheap structural guard in case a future
        # edition files something else under W2, not because it is load-bearing.
        if ref == AGGREGATE_AREA:
            continue

        # inputs: someone in `cp` bought from industry `row` in `ref`
        if col in codes and cp in EU27 and row not in NON_INDUSTRY:
            for view in ("EU", cp):
                sup[col][view][row] += val
                tot_in[col][view] += val
                # foreign is relative to the view's own boundary: outside
                # the 27 for the EU view, outside the country for a country
                # view -- so intra-EU trade is an import to a member state.
                is_foreign = (ref not in EU27) if view == "EU" else (ref != cp)
                if is_foreign:
                    foreign[col][view] += val
                    org[col][view][ref] += val

        # output: industry `row` in `ref` sold to industry `col`
        if row in codes and ref in EU27:
            if col in FINAL_DEMAND:
                # Final uses -- households, government, NPISH, capital
                # formation. Outside the customers denominator by design, and
                # counted here so the panel can say how much it is leaving out.
                for view in ("EU", ref):
                    final[row][view] += val
            elif col != AGGREGATE_AREA:
                for view in ("EU", ref):
                    cus[row][view][col] += val
                    tot_out[row][view] += val

    return sup, cus, org, tot_in, tot_out, foreign, final


# ---------------------------------------------------------------------------
# Shaping one view
# ---------------------------------------------------------------------------

def top_rows(totals, denominator, drop):
    """
    Top eight by value as {code, label, share}, then OTHER for the remainder.

    `drop` is the sector's own code: self-consumption is not a supply-chain
    link, so it is not displayed -- but it is already inside `denominator`, so
    it lands in OTHER rather than inflating everyone else.
    """
    if denominator <= 0:
        return []
    # Value descending, then code ASCENDING. The tiebreak is not cosmetic:
    # Malta buys exactly 0.546 of basic metals from each of GB and ES, and
    # sorting the pair the other way silently reorders a published row.
    ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
    top = [(v, k) for k, v in ranked if k != drop][:TOP_N]
    rows = [{"code": k, "label": label_for(k), "share": round(100 * v / denominator, 1)}
            for v, k in top]
    # OTHER is the remainder of the UNROUNDED shares. Summing the rounded ones
    # instead moves it by a tenth on about a third of the views -- which is how
    # this was found, since every named row already matched and only OTHER did
    # not. The displayed column can therefore be off by 0.1; the alternative is
    # a remainder that disagrees with the delivered data.
    tail = 100 - sum(100 * v / denominator for v, _ in top)
    rows.append({"code": OTHER, "label": LABELS[OTHER], "share": round(tail, 1)})
    return rows


def build_view(code, view, sup, cus, org, tot_in, tot_out, foreign, final):
    ti = tot_in[code][view]
    fo = foreign[code][view]
    inter = tot_out[code][view]
    fd = final[code][view]
    return {
        "import_dependency_pct": round(100 * fo / ti, 1) if ti else 0.0,
        # What share of everything this sector sells goes to FINAL use rather
        # than to another industry. The customers list is intermediate sales
        # only, so without this a reader of a retail or hotels panel sees the
        # 20 % of the business that is B2B and none of the 80 % that is not.
        "final_demand_share_pct": round(100 * fd / (fd + inter), 1) if (fd + inter) else 0.0,
        "suppliers": top_rows(sup[code][view], ti, code),
        "customers": top_rows(cus[code][view], inter, code),
        "foreign_input_origins": top_rows(org[code][view], fo, None),
    }


def build_sector(slug, code, acc):
    sup, cus, org, tot_in, tot_out, foreign, final = acc
    return {
        "slug": slug,
        "figaro_code": code,
        "figaro_label": label_for(code),
        "shares_basis": SHARES_BASIS,
        "note": SHARED_CODE_NOTE.get(code),
        "eu": build_view(code, "EU", sup, cus, org, tot_in, tot_out, foreign, final),
        "by_country": {
            c: build_view(code, c, sup, cus, org, tot_in, tot_out, foreign, final)
            for c in sorted(EU27)
        },
    }


# Fields this repo added AFTER the eleven files were delivered. --check exists
# to prove the reconstructed methodology reproduces the delivered numbers, so
# it compares the delivered surface only; a field invented here would otherwise
# turn a real proof into a tautology about our own output.
ADDED_FIELDS = ("final_demand_share_pct",)


def strip_added_fields(sector):
    out = json.loads(json.dumps(sector))
    for view in [out["eu"], *out["by_country"].values()]:
        for f in ADDED_FIELDS:
            view.pop(f, None)
    return out


def path_for(slug):
    """chem/plastics lives at exposure/chem__plastics.json -- one flat dir."""
    return EXPOSURE_DIR / f"{slug.replace('/', '__')}.json"


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="slugs to build (default: all)")
    ap.add_argument("--check", action="store_true",
                    help="rebuild the original eleven and diff; write nothing")
    ap.add_argument("--write", action="store_true", help="write the JSON files")
    args = ap.parse_args()

    if not (args.check or args.write):
        ap.error("pass --check or --write")

    slugs = args.slugs or (ORIGINAL_ELEVEN if args.check else sorted(SECTOR_CODES))
    unknown = [s for s in slugs if s not in SECTOR_CODES]
    if unknown:
        ap.error(f"unknown slug(s): {unknown}")

    codes = {SECTOR_CODES[s] for s in slugs}
    print(f"reading {FLATFILE_ZIP.name} for {len(codes)} FIGARO code(s)...", flush=True)
    acc = accumulate(codes)

    if args.check:
        bad = []
        for slug in slugs:
            built = strip_added_fields(build_sector(slug, SECTOR_CODES[slug], acc))
            on_disk = strip_added_fields(json.loads(path_for(slug).read_text(encoding="utf-8")))
            if built == on_disk:
                print(f"  MATCH  {slug}")
            else:
                bad.append(slug)
                print(f"  DIFFER {slug}")
        if bad:
            print(f"\n{len(bad)} file(s) not reproduced: {bad}")
            print("The builder does not reproduce the delivered data. "
                  "Do not write new sectors from it.")
            return 1
        print(f"\nAll {len(slugs)} delivered files reproduced exactly.")
        return 0

    manifest_path = EXPOSURE_DIR / "_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for slug in slugs:
        sector = build_sector(slug, SECTOR_CODES[slug], acc)
        path_for(slug).write_text(dump(sector), encoding="utf-8")
        manifest[slug] = {
            "code": SECTOR_CODES[slug],
            "eu_import_dependency_pct": sector["eu"]["import_dependency_pct"],
        }
        print(f"  wrote {path_for(slug).relative_to(ROOT)} "
              f"(import dependency {sector['eu']['import_dependency_pct']}%)")
    manifest_path.write_text(dump(dict(sorted(manifest.items()))), encoding="utf-8")
    print(f"  wrote {manifest_path.relative_to(ROOT)} ({len(manifest)} slugs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

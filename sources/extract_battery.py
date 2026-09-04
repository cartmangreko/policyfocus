"""
Extract the Batteries Regulation -- Regulation (EU) 2023/1542, consolidated at
31 July 2025 (CELEX 02023R1542-20250731) -- into data/battery.json.

    python3 extract_battery.py --check     # report, write nothing
    python3 extract_battery.py             # write ../data/battery.json

Anchor-based, in the extract_nzia.py idiom: every source_text is SLICED out of
sources/battery.txt by a start/end anchor rather than retyped, so a span cannot
drift from the act by a stray character. A missing or ambiguous anchor is a hard
failure and nothing is written.

A SINGLE PASS, DECLARED AS A PRELIMINARY READING. Brief 6 §5. Every other
register file has been through two independent reads and a reconciliation; this
one has not, and the coverage page says so in the same words PPWR's declaration
uses. That declaration is not a formality -- it is the difference between "we
have checked this twice" and "one person has read it once", and a reader is
entitled to know which they are looking at.

WHAT THIS ACT IS, AND WHY THE READING IS SHAPED THE WAY IT IS
=============================================================
It is a standing act read at its current consolidation, like NZIA, so `direction`
is "add" almost everywhere: a standing act states duties, it does not remove
them. The exceptions are the provisions that switch a duty OFF -- Art. 4's free
movement, Art. 47's carve-out of small operators from due diligence -- which are
the obligation side, direction "rem".

THE DATES ARE THE HARD PART AND THEY ARE OFTEN NOT DATES. Article 96 sets a
general application of 18 February 2024 with three carve-outs. But the act's most
consequential requirements do not run from a date at all: the carbon footprint
declaration, the recycled-content shares and the green procurement criteria each
apply from "X, or N months after the entry into force of the delegated act,
WHICHEVER IS THE LATEST" -- and those delegated acts do not exist. A `when` that
printed only the calendar date would state as settled a thing the act leaves
open, so those rows carry the conditional in full and say what it hangs on.

THAT IS ALSO WHY THERE IS NO MONEY MODEL HERE. Brief 6 §6 rules that nothing
about the carbon-footprint declaration is computable per plant, and Article 7 is
why: it requires a declaration "for each battery model per manufacturing plant"
calculated "in accordance with the implementing act referred to in the fourth
subparagraph", and that implementing act is on watch rather than in the register.
The per-plant arithmetic has no methodology to run, so there is no model and no
placeholder.

WHERE THE BOUNDARY WITH CIRCULAR MATERIALS FALLS
================================================
Chapter VIII is waste batteries -- collection, treatment, recycling efficiency.
The batteries PERIMETER excludes recycling sites from the projects dataset and
gives them to circular materials. That is a rule about which ecosystem claims a
WORKS, and it does not travel to measures: a provision in this act that regulates
waste batteries still binds the battery producer, and `sectors_named` says so.
The rows below name `batsol` throughout and add `waste` where the duty falls on a
treatment operator. Nothing here decides which ecosystem draws a recycling plant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "battery.txt"
FILE_KEY = "battery"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20250731"

# The consolidated text opens with a banner and the amendment table. Nothing is
# quoted from there, and confining the search to the operative part keeps an
# anchor from landing in it.
OPERATIVE_ANCHOR = "Article 1 Subject matter"

B = "business"
S = "state"
C = "commission"
H = "household"

# Article 96(2). The general date and its three carve-outs.
WHEN_GENERAL = "Applies from 18 February 2024 (Art. 96(2))"
WHEN_REMOVABILITY = "From 18 February 2027 (Art. 96(2)(a))"
WHEN_CHAPTER_VI = "From 18 August 2024 (Art. 96(2)(b))"
WHEN_CHAPTER_VIII = "From 18 August 2025 (Art. 96(2)(c))"

# THE DATES THAT ARE NOT DATES. Each of these applies from a calendar date OR a
# stated interval after a delegated or implementing act enters into force,
# whichever is LATER -- and the act in question has not been adopted. Written out
# rather than reduced to the calendar date, because the calendar date is the one
# thing that is certainly not when the duty starts.
WHEN_CARBON_EV = ("18 February 2025, or 12 months after the delegated and implementing acts under "
                  "Art. 7(1) enter into force, whichever is the latest. Neither act has been "
                  "adopted, so the date is not yet fixed")
WHEN_RECYCLED_CONTENT = ("18 August 2028, or 24 months after the delegated act under Art. 8(1) "
                         "enters into force, whichever is the latest. That act has not been "
                         "adopted, so the date is not yet fixed")
WHEN_LABELLING = ("18 August 2026, or 18 months after the implementing act under Art. 13(10) "
                  "enters into force, whichever is the latest")
WHEN_DUE_DILIGENCE = "From 18 August 2027, as amended (Art. 48(1))"
WHEN_PASSPORT = "From 18 February 2027 (Art. 77(1))"
WHEN_GPP = ("12 months after the first delegated act under Art. 85(3) enters into force. That act "
            "has not been adopted, so the date is not yet fixed")

# The sector this act is about. `batsol` is the register's key for the batteries
# and solar cell; the batteries ecosystem covers the battery half of it and solar
# carries no ecosystem edge. See data/transition/ecosystems.json.
BAT = ["batsol"]

ROWS: list[tuple] = [

    # ----------------------------------------------------------- free movement
    ("FM-01",
     "Member States shall not, for reasons relating to the sustainability, safety, labelling and "
     "information requirements for batteries covered by this Regulation, prohibit, restrict or "
     "impede the making available on the market or the putting into service of batteries that "
     "comply with this Regulation.",
     "",
     dict(measure_type="right", direction="add",
          benefit="A battery that complies with this Regulation may be placed on the market anywhere "
                  "in the Union without a Member State restricting it on sustainability, safety, "
                  "labelling or information grounds.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="a battery that complies with this Regulation",
          frequency="continuous", verification="market surveillance authority",
          article="Art. 4(1)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"], named=BAT, reached=["auto"],
          right_basis=dict(
            text="Member States shall not, for reasons relating to the sustainability, safety, "
                 "labelling and information requirements for batteries covered by this Regulation, "
                 "prohibit, restrict or impede the making available on the market or the putting "
                 "into service of batteries that comply with this Regulation.",
            kind="conferral"),
          note="The free-movement clause is read as a conferral on the operator rather than as a "
               "duty on the Member State, on the rule the benefit axis already applies: measure_type "
               "follows the OBJECT the provision acts on, and what this one acts on is the "
               "operator's ability to sell.")),

    # -------------------------------------------------- substances and design
    ("SUB-01",
     "In addition to the restrictions set out in Annex XVII to Regulation (EC) No 1907/2006 and in "
     "Article 4(2), point (a), of Directive 2000/53/EC, batteries shall not contain substances for "
     "which Annex I to this Regulation contains a restriction unless the conditions of that "
     "restriction are complied with.",
     "",
     dict(measure_type="prohibition", direction="add",
          duty="Do not place on the market a battery containing a substance restricted by Annex I "
               "otherwise than on the conditions that Annex sets.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="a battery containing mercury, cadmium or lead above the Annex I limits",
          frequency="per battery model", verification="market surveillance authority",
          article="Art. 6(1)", when=WHEN_GENERAL,
          drivers=["D1"], named=BAT, reached=["auto", "chem"])),

    ("CF-01",
     "For electric vehicle batteries, rechargeable industrial batteries with a capacity greater than "
     "2 kWh and LMT batteries a carbon footprint declaration shall be drawn up for each battery "
     "model per manufacturing plant",
     "a web link giving access to a public version of the study supporting the carbon footprint "
     "values referred to in points (d) and (e).",
     dict(measure_type="obligation", direction="add",
          duty="Draw up a carbon footprint declaration for each battery model per manufacturing "
               "site, giving the site's geographic location and the battery's carbon footprint in "
               "kg CO2-equivalent per kWh delivered over its service life.",
          addressee="Manufacturers of electric vehicle, rechargeable industrial and LMT batteries",
          cls=B, trigger="each battery model, at each manufacturing site",
          frequency="per model per site", verification="notified body",
          article="Art. 7(1)", when=WHEN_CARBON_EV,
          drivers=["D1", "D3"], named=BAT, reached=["auto"],
          note="THE ONE PROVISION IN THIS ACT THAT IS PER-SITE, and the reason there is no money "
               "model for this sector. The declaration is drawn up per manufacturing site and its "
               "methodology sits in a delegated and an implementing act, neither adopted. Until "
               "they exist nothing about the declaration is computable for a named works, so the "
               "sector page carries no arithmetic here and no placeholder for it.")),

    ("RC-01",
     "industrial batteries with a capacity greater than 2 kWh, except those with exclusively "
     "external storage, electric vehicle batteries and SLI batteries that contain cobalt, lead, "
     "lithium or nickel in active materials, shall be accompanied by documentation containing "
     "information about the percentage share of cobalt, lithium or nickel",
     "for each battery model per year and per manufacturing plant.",
     dict(measure_type="obligation", direction="add",
          duty="Accompany the battery with documentation stating the percentage of cobalt, lithium "
               "or nickel in active materials recovered from battery manufacturing waste or "
               "post-consumer waste, and the percentage of lead recovered from waste, per model per "
               "year per manufacturing site.",
          addressee="Manufacturers of industrial, electric vehicle and SLI batteries",
          cls=B, trigger="a battery containing cobalt, lead, lithium or nickel in active materials",
          frequency="per model per year per site", verification="notified body",
          article="Art. 8(1)", when=WHEN_RECYCLED_CONTENT,
          drivers=["D1", "D2"], named=BAT, reached=["auto", "waste"])),

    ("REM-01",
     "Any natural or legal person that places on the market products incorporating portable "
     "batteries shall ensure that those batteries are readily removable and replaceable by the "
     "end-user at any time during the lifetime of the product.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure a portable battery in a product placed on the market is readily removable "
               "and replaceable by the end-user, using commercially available tools, at any time "
               "in the product's life.",
          addressee="Any person placing products incorporating portable batteries on the market",
          cls=B, trigger="a product incorporating a portable battery",
          frequency="per product model", verification="market surveillance authority",
          article="Art. 11(1)", when=WHEN_REMOVABILITY,
          drivers=["D1"], named=BAT, reached=["auto"])),

    ("LAB-01",
     "batteries shall bear a label containing the general information on batteries set out in Part "
     "A of Annex VI.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Bear a label carrying the general information on batteries set out in Part A of "
               "Annex VI.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="every battery placed on the market",
          frequency="per battery", verification="market surveillance authority",
          article="Art. 13(1)", when=WHEN_LABELLING,
          drivers=["D1"], named=BAT, reached=["auto"])),

    # -------------------------------------------------- economic operator duties
    ("MAN-01",
     "Before placing a battery on the market or putting it into service, manufacturers shall draw "
     "up the technical documentation referred to in Annex VIII and carry out the relevant "
     "conformity assessment procedure, referred to in Article 17, or have it carried out.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Draw up the Annex VIII technical documentation and carry out, or have carried out, "
               "the conformity assessment procedure before placing a battery on the market.",
          addressee="Manufacturers of batteries",
          cls=B, trigger="before a battery is placed on the market or put into service",
          frequency="per battery model", verification="notified body",
          article="Art. 38(2)", when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=BAT, reached=["auto"])),

    ("SUP-01",
     "Suppliers of battery cells and battery modules shall provide the information and "
     "documentation necessary to comply with the requirements of this Regulation when supplying "
     "battery cells or modules to a manufacturer. That information and documentation shall be "
     "provided free of charge.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Supply, free of charge, the information and documentation a battery manufacturer "
               "needs to comply with this Regulation when supplying it cells or modules.",
          addressee="Suppliers of battery cells and battery modules",
          cls=B, trigger="supplying cells or modules to a battery manufacturer",
          frequency="per supply", verification="none",
          article="Art. 39", when=WHEN_CHAPTER_VI,
          drivers=["D4"], named=BAT, reached=["auto"],
          note="THE ONE PROVISION ADDRESSED TO A CELL MAKER AS SUCH. Everything else in Chapter VI "
               "speaks to whoever places the finished battery on the market; this speaks to the "
               "works that made the cell, which is the population the projects dataset draws.")),

    # ------------------------------------------------------------ due diligence
    ("DD-01",
     "economic operators that place batteries on the market or put them into service shall fulfil "
     "the due diligence obligations laid down in paragraphs 2 and 3 of this Article, and in "
     "Articles 49, 50 and 52 and shall, to that end, set up and implement battery due diligence "
     "policies.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Set up and implement a battery due diligence policy covering the raw materials in "
               "the battery and the social and environmental risks in their supply chain.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="placing a battery on the market or putting it into service",
          frequency="continuous", verification="notified body",
          article="Art. 48(1)", when=WHEN_DUE_DILIGENCE,
          drivers=["D1", "D4"], named=BAT, reached=["auto", "alu", "chem"])),

    ("DD-02",
     "Economic operators referred to in paragraph 1 of this Article shall have their battery due "
     "diligence policies verified by a notified body in accordance with Article 51",
     "The notified body shall provide the audited economic operator with an audit report.",
     dict(measure_type="obligation", direction="add",
          duty="Have the battery due diligence policy verified by a notified body and periodically "
               "audited by it, and hold the audit report.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="holding a battery due diligence policy",
          frequency="periodic", verification="notified body",
          article="Art. 48(2)", when=WHEN_DUE_DILIGENCE,
          drivers=["D4"], named=BAT, reached=["auto"])),

    ("DD-03",
     "This Chapter does not apply to economic operators that had a net turnover of less than EUR 40 "
     "million",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Comply with the battery due diligence obligations in Chapter VII.",
          addressee="Economic operators below the turnover threshold",
          cls=B, trigger="net turnover below EUR 40 million in the preceding financial year",
          frequency="annual test", verification="none",
          article="Art. 47", when=WHEN_DUE_DILIGENCE,
          named=BAT, reached=[],
          note="Direction rem on an obligation row: the duty exists and this provision switches it "
               "off for a named class. That is the Simplification reading the valence rule takes, "
               "and is the same shape as NZIA Art. 6(5). It carries NO value_drivers and NO "
               "access_frictions, and the validator is right to insist: those fields assert a "
               "conferred faculty, and relieving a duty is not the same act as conferring one. "
               "The relief is expressed by direction rem on the duty, which is what the valence "
               "rule reads as Simplification.")),

    # ------------------------------------------------------------ the passport
    ("BP-01",
     "each LMT battery, each industrial battery with a capacity greater than 2 kWh and each "
     "electric vehicle battery placed on the market or put into service shall have an electronic "
     "record (‘battery passport’).",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Give each LMT, larger industrial and electric vehicle battery an electronic record "
               "carrying the Annex XIII information, accessible through the QR code on the battery.",
          addressee="Economic operators placing batteries on the market",
          cls=B, trigger="an LMT, industrial over 2 kWh, or electric vehicle battery",
          frequency="per battery", verification="market surveillance authority",
          article="Art. 77(1)", when=WHEN_PASSPORT,
          drivers=["D1", "D4"], named=BAT, reached=["auto", "waste"])),

    # -------------------------------------------------------------- procurement
    ("GPP-01",
     "contracting entities, as defined in Article 4(1) of Directive 2014/25/EU shall, when "
     "procuring batteries or products containing batteries in situations covered by those "
     "Directives, take account of the environmental impacts of those batteries over their life "
     "cycle with a view to ensuring that such impacts are kept to a minimum.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Take account of the life-cycle environmental impacts of batteries when procuring "
               "batteries or products containing them.",
          addressee="Contracting authorities and contracting entities",
          cls=S, trigger="a public procurement of batteries or products containing batteries",
          frequency="per procurement", verification="none",
          article="Art. 85(1)", when=WHEN_GPP,
          drivers=["D3"], named=BAT, reached=["auto"],
          note="The duty is on the buyer and the effect is on the seller, which is why this is an "
               "obligation on the state rather than a right for the operator: nothing here confers "
               "a faculty on anybody, it constrains how a contracting authority may buy.")),

    # ------------------------------------------------------------ waste chapter
    ("EPR-01",
     "Producers shall have extended producer responsibility for batteries that they make available "
     "on the market for the first time within the territory of a Member State.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Carry extended producer responsibility for every battery first made available on a "
               "Member State's market, including the cost of collection, treatment and recycling.",
          addressee="Producers of batteries",
          cls=B, trigger="making a battery available on a Member State's market for the first time",
          frequency="continuous", verification="competent authority",
          article="Art. 56(1)", when=WHEN_CHAPTER_VIII,
          drivers=["D1", "D2"], named=BAT, reached=["auto", "waste"])),

    ("REC-01",
     "Collected waste batteries shall not be disposed of or be the subject of an energy recovery "
     "operation.",
     "",
     dict(measure_type="prohibition", direction="add",
          duty="Do not dispose of collected waste batteries or send them for energy recovery.",
          addressee="Operators of waste battery treatment facilities",
          cls=B, trigger="waste batteries that have been collected",
          frequency="continuous", verification="competent authority",
          article="Art. 70(1)", when=WHEN_CHAPTER_VIII,
          drivers=["D1"], named=BAT, reached=["waste"])),

    ("PEN-01",
     "Member States shall lay down the rules on penalties applicable to infringements of this "
     "Regulation",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Lay down and notify rules on penalties for infringements of this Regulation, and "
               "take the measures necessary to ensure they are applied.",
          addressee="Member States",
          cls=S, trigger="entry into application of the Regulation",
          frequency="one-off", verification="none",
          article="Art. 93", when="By 18 August 2025 (Art. 93)",
          drivers=[], named=BAT, reached=[])),
]


def slice_span(text: str, start: str, end: str, rid: str) -> str:
    i = text.find(start)
    if i == -1:
        raise LookupError(f"{rid}: START anchor not found: {start[:70]!r}")
    if text.count(start) > 1:
        raise LookupError(
            f"{rid}: START anchor is ambiguous, {text.count(start)} matches: {start[:70]!r}")
    if not end:
        return start
    j = text.find(end, i)
    if j == -1:
        raise LookupError(f"{rid}: END anchor not found after start: {end[:70]!r}")
    return text[i:j + len(end)]


def build() -> tuple[list[dict], list[str]]:
    raw = canonical((HERE / ACT).read_text(encoding="utf-8"))
    cut = raw.find(OPERATIVE_ANCHOR)
    if cut == -1:
        raise LookupError(f"operative anchor missing from {ACT}")
    act = raw[cut:]

    rows, errors = [], []
    for rid, start, end, meta in ROWS:
        try:
            span = slice_span(act, start, end, rid)
        except LookupError as exc:
            errors.append(str(exc))
            continue
        row = {
            "id": rid,
            "measure_type": meta["measure_type"],
            "addressee": meta["addressee"],
            "class": meta["cls"],
            "trigger": meta["trigger"],
            "frequency": meta["frequency"],
            "verification": meta["verification"],
            "direction": meta["direction"],
            "article": meta["article"],
            "when": meta["when"],
            "source_text": span,
            "drivers": meta.get("drivers", []),
            "sectors_named": meta["named"],
            "sectors_reached": meta["reached"],
            "provision_id": None,
            "file": FILE_KEY,
            "source_url": SOURCE_URL,
            "value_drivers": meta.get("value_drivers", []),
            "access_frictions": meta.get("frictions", []),
        }
        if meta["measure_type"] == "right":
            row["benefit"] = meta["benefit"]
        else:
            row["duty"] = meta["duty"]
        if meta.get("right_basis"):
            row["right_basis"] = meta["right_basis"]
        if meta.get("note"):
            row["reading_note"] = meta["note"]
        rows.append(row)
    return rows, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rows, errors = build()
    if errors:
        print(f"extract_battery: ANCHOR FAILURES ({len(errors)}) — nothing written:",
              file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    out = DATA / "battery.json"
    text = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print(f"extract_battery: {out} is stale or missing — re-run", file=sys.stderr)
            return 1
        print(f"extract_battery: --check, {len(rows)} measure(s) match")
        return 0

    out.write_text(text, encoding="utf-8")
    kinds: dict[str, int] = {}
    for r in rows:
        kinds[r["measure_type"]] = kinds.get(r["measure_type"], 0) + 1
    print(f"extract_battery: wrote {out} — {len(rows)} measure(s): "
          + ", ".join(f"{v} {k}" for k, v in sorted(kinds.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

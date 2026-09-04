"""
Extract the CO2 emission performance standards for cars and vans --
Regulation (EU) 2019/631, consolidated at 9 July 2025 (CELEX 02019R0631-20250709)
-- into data/fleet.json.

    python3 extract_fleet.py --check     # report, write nothing
    python3 extract_fleet.py             # write ../data/fleet.json

Anchor-based, in the extract_nzia.py idiom: every source_text is SLICED out of
sources/fleet.txt rather than retyped, and a missing or ambiguous anchor writes
nothing.

A SINGLE PASS, DECLARED AS A PRELIMINARY READING, like the batteries regulation
alongside it. The coverage page says so.

WHY THIS ACT IS IN A BATTERIES REGISTER AT ALL
==============================================
It never mentions batteries. It is a register of CO2 grams per kilometre for new
cars and vans, addressed to vehicle manufacturers, and on a naive reading it
belongs to the automotive sector and stops there.

It is here because it is the demand. A fleet-wide target of a 100 % reduction on
the 2021 baseline from 1 January 2035 is a requirement that new cars emit no CO2
at the tailpipe, and the only volume technology that meets it is a battery
electric vehicle. Every gigafactory row in this dataset exists because somebody
believes that sentence. An industrial-policy platform that held the supply side
and not the rule creating the demand would be describing an investment boom with
its cause missing.

THE EDGE TYPE THIS ACT EXISTS TO POPULATE
=========================================
`creates_demand_for` was reserved in the graph and never used, because nothing
in the register supported it: `applies_to` says a measure BINDS a sector, and
nothing in this platform could say a measure MAKES A MARKET for one. Those are
different claims and collapsing them would be a lie in the reader's favour --
the batteries sector page would show a duty it does not carry.

So the rows below carry `creates_demand_for` where, and only where, the act's own
text supports it:

  * Art. 1(5a), the 2035 100 % target. The strongest case in the act and the
    reason the edge exists.
  * Art. 1(5), the 2030 55 % and 50 % targets. A reduction of that size is not
    reachable on internal combustion alone at fleet scale.
  * Art. 4(1), the manufacturer's own duty to meet its specific emissions
    target, which is where the fleet-wide number becomes an obligation on a
    named company.
  * Art. 8, the excess emissions premium. The price of not meeting the target,
    which is what makes the target bite.

WHAT DOES NOT CARRY IT, and the restraint is the point. Monitoring and reporting
(Art. 7), publication of performance (Art. 9), derogations for small
manufacturers (Art. 10), eco-innovation credits (Art. 11), in-service
verification (Art. 13) are all real duties on a carmaker and none of them makes
a market for a cell. An edge on every row would say the whole act is a batteries
instrument, which is exactly the overreach `creates_demand_for` was kept out of
the register to avoid until something could be said precisely.

THE DIRECTION OF THE EDGE. measure -> sector, the same shape as `applies_to`,
read as "this measure creates demand for what this sector makes". It is NOT an
`applies_to` edge with a nicer name: none of these rows binds a battery maker,
and `sectors_named` on all of them is `auto`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "fleet.txt"
FILE_KEY = "fleet"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R0631-20250709"

OPERATIVE_ANCHOR = "Article 1 Subject matter and objectives"

B = "business"
S = "state"
C = "commission"

WHEN_2025 = "From 1 January 2025 (Art. 1(4))"
WHEN_2030 = "From 1 January 2030 (Art. 1(5))"
WHEN_2035 = "From 1 January 2035 (Art. 1(5a))"
WHEN_GENERAL = "In force; applies to each calendar year"

AUTO = ["auto"]
BAT = ["batsol"]

ROWS: list[tuple] = [

    ("TGT-2030",
     "From 1 January 2030, the following EU fleet-wide targets shall apply: (a) for the average "
     "emissions of the new passenger car fleet, an EU fleet-wide target equal to a ►M5 55 % ◄ "
     "reduction of the target in 2021",
     "reduction of the target in 2021 determined in accordance with point 6.1.2 of Part B of "
     "Annex I.",
     dict(measure_type="obligation", direction="add",
          duty="Meet an EU fleet-wide target of a 55% reduction on the 2021 baseline for new "
               "passenger cars, and 50% for new light commercial vehicles.",
          addressee="Manufacturers of new passenger cars and light commercial vehicles",
          cls=B, trigger="the new vehicle fleet registered in the Union in a calendar year",
          frequency="annual", verification="the Commission",
          article="Art. 1(5)", when=WHEN_2030,
          drivers=["D1", "D3"], named=AUTO, reached=["batsol"],
          demand=BAT,
          note="A 55% fleet reduction is not reachable on internal combustion alone at fleet "
               "scale, which is what makes this a demand instrument for cells and not only a "
               "duty on a carmaker.")),

    ("TGT-2035",
     "From 1 January 2035, the following EU fleet-wide targets shall apply: (a) for the average "
     "emissions of the new passenger car fleet, an EU fleet-wide target equal to a 100 % reduction "
     "of the target in 2021",
     "Part A, point 6.1.3, of Annex I;",
     dict(measure_type="obligation", direction="add",
          duty="Meet an EU fleet-wide target of a 100% reduction on the 2021 baseline for new "
               "passenger cars from 2035.",
          addressee="Manufacturers of new passenger cars",
          cls=B, trigger="the new passenger car fleet registered in the Union in a calendar year",
          frequency="annual", verification="the Commission",
          article="Art. 1(5a)", when=WHEN_2035,
          drivers=["D1", "D3"], named=AUTO, reached=["batsol"],
          demand=BAT,
          note="THE PROVISION THIS SECTOR IS BUILT ON. A 100% reduction on the tailpipe measure is "
               "a requirement that new cars emit no CO2 where they are driven, and the only volume "
               "technology that meets it is a battery electric vehicle. Every gigafactory row in "
               "the projects dataset exists because somebody believes this sentence.")),

    ("TGT-01",
     "The manufacturer shall ensure that its average specific emissions of CO2 do not exceed the "
     "following specific emissions targets:",
     "in accordance with that derogation.",
     dict(measure_type="obligation", direction="add",
          duty="Ensure the manufacturer's average specific CO2 emissions do not exceed its "
               "specific emissions target for the calendar year.",
          addressee="Manufacturers of new passenger cars and light commercial vehicles",
          cls=B, trigger="a manufacturer's new vehicles registered in a calendar year",
          frequency="annual", verification="the Commission",
          article="Art. 4(1)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=AUTO, reached=["batsol"],
          demand=BAT,
          note="Where the fleet-wide number becomes an obligation on a named company. The "
               "fleet-wide targets in Art. 1 set the level; this is the row a manufacturer is "
               "actually held to.")),

    ("PREM-01",
     "In respect of each calendar year, the Commission shall impose an excess emissions premium on "
     "a manufacturer or pool manager, as appropriate, where a manufacturer's average specific "
     "emissions of CO2 exceed its specific emissions target.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Pay an excess emissions premium of EUR 95 per gram per kilometre of exceedance, "
               "multiplied by the number of newly registered vehicles.",
          addressee="Manufacturers of new passenger cars and light commercial vehicles",
          cls=B, trigger="average specific emissions above the manufacturer's target",
          frequency="annual", verification="the Commission",
          article="Art. 8(1)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=AUTO, reached=["batsol"],
          demand=BAT,
          note="The price of missing the target, which is what makes the target bite. Carried as a "
               "demand edge because a priced obligation is the mechanism by which the fleet target "
               "reaches a procurement decision; the premium itself is money out of a carmaker, not "
               "money into a cell maker, and no money model is built from it here.")),

    # ---------------------------------------------------- duties that are NOT demand
    ("MON-01",
     "For each calendar year, each Member State shall record information for each new passenger car "
     "and each new light commercial vehicle registered in its territory",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Record and report to the Commission, for each calendar year, the registration "
               "information for every new passenger car and light commercial vehicle.",
          addressee="Member States",
          cls=S, trigger="each new vehicle registered in the territory",
          frequency="annual", verification="the Commission",
          article="Art. 7(1)", when=WHEN_GENERAL,
          drivers=["D4"], named=AUTO, reached=[],
          note="A real duty and NOT a demand instrument. Carried without a creates_demand_for edge "
               "on purpose: monitoring makes no market for a cell, and an edge on every row in "
               "this act would say the whole regulation is a batteries instrument.")),

    ("DER-01",
     "An application for a derogation from the specific emissions target calculated in accordance "
     "with Annex I may be made by a manufacturer of fewer than 10 000 new passenger cars or 22 000 "
     "new light commercial vehicles registered in the Union per calendar year",
     "",
     dict(measure_type="right", direction="add",
          benefit="A small-volume manufacturer may apply for a derogation from its specific "
                  "emissions target.",
          addressee="Manufacturers below the small-volume thresholds",
          cls=B, trigger="fewer than 10 000 cars or 22 000 vans registered in the Union per year",
          frequency="per application", verification="the Commission",
          article="Art. 10(1)", when=WHEN_GENERAL,
          value_drivers=["V1"], frictions=["F4"], named=AUTO, reached=[],
          right_basis=dict(
            text="An application for a derogation from the specific emissions target calculated in "
                 "accordance with Annex I may be made by a manufacturer of fewer than 10 000 new "
                 "passenger cars or 22 000 new light commercial vehicles registered in the Union "
                 "per calendar year",
            kind="procedure"))),
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
        # Only where the act's own text supports it. See the module docstring.
        if meta.get("demand"):
            row["creates_demand_for"] = meta["demand"]
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
        print(f"extract_fleet: ANCHOR FAILURES ({len(errors)}) — nothing written:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    out = DATA / "fleet.json"
    text = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print(f"extract_fleet: {out} is stale or missing — re-run", file=sys.stderr)
            return 1
        print(f"extract_fleet: --check, {len(rows)} measure(s) match")
        return 0

    out.write_text(text, encoding="utf-8")
    demand = sum(1 for r in rows if r.get("creates_demand_for"))
    print(f"extract_fleet: wrote {out} — {len(rows)} measure(s), "
          f"{demand} carrying creates_demand_for")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Extract the electricity market design flexibility provisions --
Regulation (EU) 2019/943, consolidated at 16 July 2024 (CELEX 02019R0943-20240716),
as amended by Directive (EU) 2024/1747 -- into data/emd.json.

    python3 extract_emd.py --check     # report, write nothing
    python3 extract_emd.py             # write ../data/emd.json

Anchor-based, in the extract_fleet.py idiom: every source_text is SLICED out of
sources/emd.txt rather than retyped, and a missing or ambiguous anchor writes
nothing.

A SINGLE PASS OVER ONE BLOCK OF ONE ACT, AND THE PAGE SAYS SO. Regulation (EU)
2019/943 is the electricity market regulation: bidding zones, capacity
mechanisms, congestion income, ENTSO-E's tasks, the whole internal market. None
of that is read here. What is read is Articles 19e to 19h, the non-fossil
flexibility block that Directive (EU) 2024/1747 inserted in 2024, and the rows
below are the whole of this file's claim about the act.

WHY THIS BLOCK AND NOT THE RENEWABLES DIRECTIVE
===============================================
The question this ingestion answers is which measure carries a STORAGE-SIDE
`creates_demand_for` edge -- the storage half of `batsol`, where the cell half
already has one from the CO2 standards for cars and vans.

The renewables directive was the alternative, and it was not taken. Its targets
are shares of renewable ENERGY: a Member State that meets them with wind, solar
and interconnection has complied, and storage benefits consequentially rather
than because anything asked for it. A consequence is not a demand instrument,
and an edge drawn from it would be this platform inferring a market rather than
reading one.

Article 19f asks for a number, and names storage inside it:

    "each Member State shall define ... an indicative national objective for
    non-fossil flexibility, INCLUDING THE RESPECTIVE SPECIFIC CONTRIBUTIONS OF
    BOTH DEMAND RESPONSE AND ENERGY STORAGE to that objective"

That is a quantified national objective with a storage component stated in the
law's own words, which has to be written into the Member State's integrated
national energy and climate plan and reported on afterwards. It is the closest
thing in EU law in force to a storage target, and it is the only provision read
here that carries the edge.

WHAT DOES NOT CARRY IT, AND WHY THE RESTRAINT IS DELIBERATE
===========================================================
Article 19g lets a Member State pay for available non-fossil flexibility
capacity, and Article 19h(b) limits such schemes to "new investment in
non-fossil flexibility resources such as demand side response and energy
storage". That is money, pointed at storage, and a case could be made. It is not
made here, for two reasons a reader can check: the payment is PERMISSIVE ("may
apply") and CONDITIONAL on the 19f objective not being met by other means, so
nothing in the text obliges a single euro to be spent; and the edge was ruled
onto 19f specifically. If the reading is later extended, it should be extended
on the record rather than by an extractor quietly widening it.

The assessment duties in Article 19e carry no edge either. A report that
"consider[s] the potential of non-fossil flexibility resources such as demand
response and energy storage" is a study, and a study makes no market. It is
extracted because the 19f objective is built on it -- the objective is due six
months after the report, and cannot be read without it.

THE DIRECTION OF THE EDGE. measure -> sector, the same shape as in
extract_fleet.py, read as "this measure creates demand for what this sector
makes". `sectors_named` is `power`: the act binds Member States and their
regulatory authorities in the electricity market, and it names no battery maker.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "emd.txt"
FILE_KEY = "emd"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R0943-20240716"

# Everything read here was inserted by the 2024 amendment, so the slice starts at
# the flexibility chapter rather than at Article 1. A start anchor inside the
# operative text also keeps the recitals out, which matters more here than in
# most files: the 2024 recitals talk about storage at length and none of them is
# a provision.
OPERATIVE_ANCHOR = "Article 19e"

B = "business"
S = "state"
C = "commission"

POWER = ["power"]
BAT = ["batsol"]

# THE DATES ARE RELATIVE, AND THE ROWS SAY SO RATHER THAN INVENTING A CALENDAR.
# The chain is: ENTSO-E and the EU DSO entity propose a methodology by 17 April
# 2025 (Art. 19e(6)); ACER approves or amends within three months; the first
# national flexibility-needs report is due one year after that approval (Art.
# 19e(1)); the indicative national objective is due six months after the report
# (Art. 19f). Only the first of those is a fixed date in the act, so only the
# first is printed as one.
WHEN_REPORT = ("One year after ACER approves the methodology, and every two years thereafter; "
               "the methodology proposal was due by 17 April 2025 (Art. 19e(1) and (6))")
WHEN_DATA = "In force; on each preparation of the report under Art. 19e(1)"
WHEN_OBJECTIVE = ("Six months after the first report under Art. 19e(1); a Member State may set a "
                  "provisional objective before then (Art. 19f)")
WHEN_SCHEME = "In force; applies where a Member State chooses to apply such a scheme"

ROWS: list[tuple] = [

    # ------------------------------------------------------- the assessment
    ("FLEX-01",
     "No later than one year after the approval by ACER of the methodology pursuant to "
     "paragraph 6, and every two years thereafter, the regulatory authority or another authority "
     "or entity designated by a Member State, shall adopt a report on the estimated flexibility "
     "needs",
     "potential availability of cross-border flexibility.",
     dict(measure_type="obligation", direction="add",
          duty="Adopt, every two years, a report on the estimated national flexibility needs for "
               "at least the next 5 to 10 years.",
          addressee="The regulatory authority, or another authority or entity designated by the "
                    "Member State",
          cls=S, trigger="the biennial cycle, starting one year after ACER approves the "
                         "methodology",
          frequency="every two years", verification="ACER",
          article="Art. 19e(1)", when=WHEN_REPORT,
          drivers=["D1", "D5"], named=POWER, reached=[],
          note="The study the objective is built on, and NOT a demand instrument. Extracted "
               "because Art. 19f's objective is due six months after this report and cannot be "
               "read without it.")),

    ("FLEX-02",
     "consider the potential of non-fossil flexibility resources such as demand response and "
     "energy storage, including aggregation and interconnection, to fulfil the flexibility needs, "
     "both at transmission and distribution levels;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Consider, in that report, the potential of non-fossil flexibility resources — "
               "demand response and energy storage — to meet the flexibility needs, at both "
               "transmission and distribution level.",
          addressee="The regulatory authority, or another authority or entity designated by the "
                    "Member State",
          cls=S, trigger="the content requirements of the report under Art. 19e(1)",
          frequency="every two years", verification="ACER",
          article="Art. 19e(2)(b)", when=WHEN_REPORT,
          drivers=["D1", "D5"], named=POWER, reached=["batsol"],
          note="WHERE STORAGE FIRST APPEARS AS A THING TO BE COUNTED. It reaches batsol without "
               "naming a battery maker, which is what sectors_reached is for, and it carries no "
               "demand edge: an obligation to consider a potential is not an obligation to "
               "procure anything.")),

    ("FLEX-03",
     "The transmission system operators and distribution system operators of each Member State "
     "shall provide the data and analyses that are needed for the preparation of the report",
     "coordinate the gathering of the relevant information where necessary for the purposes of "
     "this Article.",
     dict(measure_type="obligation", direction="add",
          duty="Provide the data and analyses needed for the flexibility-needs report, in the "
               "type and format defined by ENTSO-E and the EU DSO entity.",
          addressee="Transmission system operators and distribution system operators",
          cls=B, trigger="the preparation of the report under Art. 19e(1)",
          frequency="every two years", verification="the regulatory authority",
          article="Art. 19e(3)", when=WHEN_DATA,
          drivers=["D1", "D4", "D5"], named=POWER, reached=[],
          note="The data duty underneath the report. Carried as a business row because a system "
               "operator is the addressee, and with D4 because the methodology defines a data "
               "type and format that did not exist before it.")),

    # ------------------------------------------------------- the objective
    ("OBJ-01",
     "No later than six months after the submission of the report pursuant to Article 19e(1) of "
     "this Regulation, each Member State shall define, on the basis of that report, an indicative "
     "national objective for non-fossil flexibility, including the respective specific "
     "contributions of both demand response and energy storage to that objective.",
     "Member States may define provisional indicative national objectives until the report is "
     "adopted pursuant to Article 19e(1) of this Regulation.",
     dict(measure_type="obligation", direction="add",
          duty="Define an indicative national objective for non-fossil flexibility, stating the "
               "specific contributions of demand response and of energy storage to it, and "
               "reflect it in the integrated national energy and climate plan and progress "
               "reports.",
          addressee="Member States",
          cls=S, trigger="six months after the flexibility-needs report is submitted",
          frequency="one-off, then reported on in the national energy and climate progress "
                    "reports",
          verification="the Commission, under Art. 9 of Regulation (EU) 2018/1999",
          article="Art. 19f", when=WHEN_OBJECTIVE,
          drivers=["D1", "D5"], named=POWER, reached=["batsol"],
          demand=BAT,
          note="THE PROVISION THE STORAGE SIDE OF THIS SECTOR IS BUILT ON. It is the only place "
               "in EU law in force that asks a Member State to put a NUMBER on energy storage: "
               "the objective is indicative rather than binding, and its storage contribution is "
               "named in the act's own words rather than inferred. The renewables directive's "
               "targets were the alternative and were not taken — they ask for a share of "
               "renewable energy, which storage serves consequentially and which names it "
               "nowhere. Indicative is not binding, and this row does not say it is; what it says "
               "is that the law asks for the number.")),

    # ------------------------------------------------------- the money, and its conditions
    ("SUP-01",
     "Where investment in non-fossil flexibility is insufficient to achieve the indicative "
     "national objective",
     "without prejudice to Articles 12 and 13.",
     dict(measure_type="right", direction="add",
          benefit="A Member State may pay for the available capacity of non-fossil flexibility "
                  "through a support scheme, where investment falls short of its indicative "
                  "national objective.",
          addressee="Member States",
          cls=S, trigger="investment insufficient to achieve the indicative national objective",
          frequency="per scheme", verification="State aid control",
          article="Art. 19g(1)", when=WHEN_SCHEME,
          value_drivers=[], frictions=[], named=POWER, reached=["batsol"],
          right_basis=dict(
            text="Where investment in non-fossil flexibility is insufficient to achieve the "
                 "indicative national objective or, where relevant, provisional indicative "
                 "national objectives defined pursuant to Article 19f, Member States may apply "
                 "non-fossil flexibility support schemes consisting of payments for the available "
                 "capacity of non-fossil flexibility",
            kind="procedure"),
          note="MONEY POINTED AT STORAGE, AND NO DEMAND EDGE ON IT. The payment is permissive and "
               "conditional: 'may apply', and only where investment is insufficient. Nothing in "
               "the text obliges a euro to be spent, so the edge stays on Art. 19f, which asks "
               "for the number. See the module docstring.")),

    ("SUP-02",
     "Member States which apply a capacity mechanism shall consider to make the necessary "
     "adaptations in the design of the capacity mechanisms to promote the participation of "
     "non-fossil flexibility such as demand side response and energy storage",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Consider adapting the design of an existing capacity mechanism to promote the "
               "participation of non-fossil flexibility, including demand side response and "
               "energy storage.",
          addressee="Member States operating a capacity mechanism",
          cls=S, trigger="operating a capacity mechanism",
          frequency="one-off", verification="none",
          article="Art. 19g(1), second sentence", when=WHEN_SCHEME,
          drivers=[], named=POWER, reached=["batsol"],
          note="A duty to CONSIDER, which is the weakest operative verb in the block and is "
               "recorded as what it is. No demand edge: a Member State that considers and "
               "declines has complied.")),

    ("DES-01",
     "Non-fossil flexibility support schemes applied by Member States in accordance with Article "
     "19g(1) shall:",
     "be limited to new investment in non-fossil flexibility resources such as demand side "
     "response and energy storage;",
     dict(measure_type="obligation", direction="add",
          duty="Where such a scheme is applied, keep it within what is necessary to meet the "
               "objective cost-effectively and limit it to NEW investment in non-fossil "
               "flexibility resources such as demand side response and energy storage.",
          addressee="Member States applying a non-fossil flexibility support scheme",
          cls=S, trigger="applying a scheme under Art. 19g(1)",
          frequency="per scheme", verification="State aid control",
          article="Art. 19h(a) and (b)", when=WHEN_SCHEME,
          drivers=[], named=POWER, reached=["batsol"],
          note="The condition that would matter most to a storage developer if the money were "
               "obligatory: support is limited to NEW investment, so a scheme cannot be spent on "
               "assets already built. Carried without a demand edge for the same reason as "
               "SUP-01 — the scheme it conditions is itself optional.")),
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
        print(f"extract_emd: ANCHOR FAILURES ({len(errors)}) — nothing written:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    out = DATA / "emd.json"
    text = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print(f"extract_emd: {out} is stale or missing — re-run", file=sys.stderr)
            return 1
        print(f"extract_emd: --check, {len(rows)} measure(s) match")
        return 0

    out.write_text(text, encoding="utf-8")
    demand = sum(1 for r in rows if r.get("creates_demand_for"))
    print(f"extract_emd: wrote {out} — {len(rows)} measure(s), "
          f"{demand} carrying creates_demand_for")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

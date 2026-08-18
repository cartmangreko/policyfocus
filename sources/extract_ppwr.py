"""
Extract the Packaging and Packaging Waste Regulation -- Regulation (EU) 2025/40
(CELEX 32025R0040) -- into data/ppwr.json.

    python3 extract_ppwr.py --check     # report, write nothing
    python3 extract_ppwr.py             # write ../data/ppwr.json

THIS FILE IS SINGLE-PASS. IT HAS BEEN READ ONCE.
================================================
One independent read, hand-authored, with its own ids and its own spans. There
is no Pass B, no crosswalk, no rulings file and no reconciliation. It is not
reconciled and reconciliation_gate.py reports it as such. Re-running the same
model over the same text would not be a second pass and none was manufactured.

Treat every classification here as unconfirmed. The four reconciled files each
moved substantially on their second read -- CRMA went from 54 rows to 90 -- and
there is no reason to think this one is closer to right on the first attempt
than they were.

Anchor-based, in the extract_crma.py / extract_nzia.py idiom: every source_text
is SLICED out of sources/ppwr.txt by a start/end anchor rather than retyped, so
a quote cannot drift from the act by a typo. Anchors run against canonical()
because the XHTML pads article numbers and paragraph markers with NBSP. A
missing or ambiguous anchor is a hard failure and nothing is written.

WHICH TEXT, AND WHY NOT THE CONSOLIDATION
=========================================
The base act. Cellar's branch notice announces a consolidated member
02025R0040-20250122 but serves it in no format -- xhtml, fmx4 and pdf are all
404 -- so 32025R0040 is the only retrievable text. sources/manifest.json
records that, and the note should be revisited when the consolidation appears.

WHY THIS ACT IS IN THE REGISTER
===============================
scope.md's third IN rule is sector reach. PPWR reaches the tracked sectors
through materials and through the operators who put them on the market: glass
and aluminium through the material recycling targets and the beverage-container
deposit system, chemicals through the substance restrictions, waste through the
whole of Chapter VIII, and -- via the spine expansion that landed with it --
paper and board, wood, plastics converting, food and drink, retail and HORECA.
It is also the first act in the register that REPEALS its predecessor rather
than amending it, which is why `repeals` exists as an edge relation.

THE BENEFIT AXIS HERE
=====================
Read on the object rule, and the gate was applied before any row was written.

Six benefit-side rows survive, each with a verbatim basis object:

  * Art. 4(2) free movement -- the conferral is on the operator, the duty is on
    the Member State, so the provision yields TWO linked measures and keeps
    provision_id.
  * Art. 6(10) innovative packaging -- a five-year faculty to market packaging
    that does not meet the recyclability requirement.
  * Art. 12(12) -- a three-year sell-through for stock made before the
    labelling deadlines.
  * Art. 28(4) -- a faculty to refuse an unhygienic container, and an express
    liability shield with it.
  * Art. 29(12) -- pooling to meet the beverage re-use target. Member-State
    conditional, and the conditionality is carried in `trigger` rather than
    quietly dropped.
  * Art. 45(9) -- an express right to challenge a fulfilment-service suspension
    before a court.

Four candidates were REJECTED at the gate and carry no benefit row:

  * Art. 6(8) and 7(7) EPR fee modulation. A graduated LEVY, not a support. The
    object rule cuts support only where a support's amount, rate, eligibility
    or existence falls, and nothing here is a support.
  * Art. 63 green public procurement. Opens "In order to incentivise the supply
    and demand for environmentally sustainable packaging" -- recital rhetoric.
    The operative content is a Commission rulemaking duty and a condition on
    contracting authorities.
  * Art. 51(2) and 43(5)-(6) Member State incentive menus. A list of things a
    Member State MAY do. Nothing is conferred on anyone yet.
  * Art. 31(7) re-use observatory and Art. 48(2) priority access. Institutional
    and permissive; no basis object to quote.

THE CARRY-OVERS
===============
Three of this act's headline numbers are NOT new. Checked line by line against
sources/ppwr_prior_01994L0062-20180704.txt:

  * Art. 52(1) recycling targets are numerically identical to Art. 6(1)(f)-(i)
    of 94/62/EC as amended by Directive (EU) 2018/852. 65 % and 70 % overall,
    and every material line -- plastic 50/55, wood 25/30, ferrous 70/80,
    aluminium 50/60, glass 70/75, paper and board 75/85.
  * Art. 5(4)'s 100 mg/kg heavy-metals limit is 94/62/EC Art. 11(1), third
    indent, restated. 100 ppm and 100 mg/kg are the same concentration.
  * Art. 34's 40 bags per capita is 94/62/EC Art. 4(1a)(a).

Each carries direction "unchanged", which derives Neutral, plus a resolved
prior_rule quoted from the directive and an affected_delta saying the level
does not move. Each also carries reclass_from: they were filed as "add" in the
first extraction, when the enum had only add|rem and a restated rule had no way
to say it was restated.

Art. 34 is the one that had to SPLIT. Its single sentence carries a level that
did not move and a recurrence clause that did -- "and subsequently by
31 December each year thereafter" turns a 2025 endpoint into a standing annual
ceiling, and the directive's alternative route of not supplying bags free of
charge is gone. BAG-02 is the carried-over level, unchanged and Neutral;
BAG-01 is the delta, add and Requirement. One row would have had to misstate
one of the two.

THE PROHIBITIONS
================
Four provisions forbid conduct outright rather than conditioning it: Art. 5(5)
PFAS in food-contact packaging, Art. 25(1) and the Annex V formats, Art. 10(2)
false bottoms and double walls, and Art. 12(8) misleading labels. They are
measure_type "prohibition", which renders "Prohibition". Each carries
reclass_from recording that it was an obligation in the first extraction,
because the enum had no prohibition value then and the id may not change.

SIZE BANDS
==========
The A-D bands are employee and turnover bands inherited from the CSRD context.
PPWR does not band by them: its thresholds are the micro-enterprise definition
in Recommendation 2003/361/EC, a 10-tonne registration threshold, a 1 000 kg
re-use exemption, and sales-area floors of 100 m2 and 400 m2. Marking a micro
carve-out as removing band A would be false, since band A runs to 500
employees. So size_scope records whether the duty reaches each band at all,
and size_scope_note carries the threshold that actually operates.

Per the same instruction, micro-enterprise and threshold carve-outs are
ELIGIBILITY ATTRIBUTES on the obligation rows, not standalone benefit rows.

WHAT IS NOT HERE, AND WHY
=========================
  * Arts. 64-65, delegation and comitology. Institutional plumbing, out on the
    same scope.md boundary that keeps the CRMA Board and the NZIA SET Plan
    group out.
  * Arts. 66-67, the amendments to Regulation (EU) 2019/1020 and Directive (EU)
    2019/904. The duties those amendments create belong to the amended acts;
    the amendment instructions themselves are procedural. The graph carries
    them as `amends` edges from the manifest, which is the right place.
  * Art. 69, the 2034 Commission evaluation, and the further Commission
    review-and-report clauses through the act (Arts. 5(9), 6(7), 6(12),
    7(12)-(15), 8, 9(5), 25(5), 29(18), 34(5), 41, 43(9), 50(11), 52(4)).
    A duty to write a report to itself is not a duty on an operator or a
    Member State in the sense rule 2 of scope.md means.
  * Art. 3, definitions. Carried by the rows that depend on them.
  * Art. 70, repeal and transition. Modelled as the `repeals` graph edge with
    its four survivals, not as a register row.
  * Annexes. Their operative content is reached through the article that
    invokes each -- Annex V through Art. 25, Annex VI through Arts. 26-28,
    Annex X through Art. 50, Annex XII through Arts. 23 and 56.

Nothing else in the enacting part is omitted. Where a provision is carried in
compressed form -- Arts. 15 to 23 are nine articles of operator duties and
become eight rows -- the row says so in `duty` rather than dropping a limb.

IDS ARE PERMANENT
=================
Prefix by subject, two digits, assigned once. An id published here is never
renumbered: a URL that resolved to a measure must keep resolving to the same
measure. A row withdrawn later leaves its id burnt rather than reused.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from benefit_axis import DUTY_SIDE_TYPES
from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "ppwr.txt"
PRIOR_94_62 = "ppwr_prior_01994L0062-20180704.txt"
FILE_KEY = "ppwr"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R0040"
PRIOR_DOC = "Directive 94/62/EC, consolidated 4 July 2018 (01994L0062-20180704)"

OPERATIVE_ANCHOR = "HAVE ADOPTED THIS REGULATION:"

# Art. 71: in force on the twentieth day after publication of 22.1.2025;
# applies from 12 August 2026. Most rows carry their own later date, because
# this act's duties are almost all staged.
WHEN_GENERAL = "From 12 August 2026 (Art. 71)"

B = "business"
S = "state"
C = "commission"

# Material streams. These enter as REACHED, not named: Art. 52's material lines
# address the Member State, and the material is the channel the duty travels
# down, not the addressee.
MATERIALS = ["glass", "alu", "steel", "paper", "wood", "chem/plastics"]
# Packaging producers and converters, as addressed across Chapters II-IV.
CONVERTERS = ["chem/plastics", "paper", "glass", "alu", "wood"]
# Everyone who fills or sells packaged product.
FILLERS = ["foodbev", "retail"]

# All four size bands reached: PPWR binds by packaging placed on the market,
# not by company size. Rows with a real threshold override this.
ALL_BANDS = {"A": "in", "B": "in", "C": "in", "D": "in"}
NO_BANDS = {"A": "na", "B": "na", "C": "na", "D": "na"}

ROWS: list[tuple] = [

    # =====================================================  Ch. I  free movement
    # Art. 4 yields two measures from one provision: the prohibition binds the
    # Member State, the market access it creates belongs to the operator.
    # Neither reading is the whole provision, so both are kept and linked.
    ("FREE-01", "Packaging shall only be placed on the market if it complies with this Regulation.", "",
     dict(measure_type="obligation", direction="add",
          duty="Place packaging on the market only if it complies with this Regulation.",
          addressee="Any economic operator placing packaging on the market",
          cls=B, trigger="placing packaging on the market",
          frequency="continuous", verification="self-assessment",
          article="Art. 4(1)", when=WHEN_GENERAL,
          drivers=["D7"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold: the duty attaches to the packaging, not to the operator's size.",
          affected_delta="Every operator placing packaging on the EU market, whatever the material. 94/62/EC Art. 9(1) had the same gate against its Annex II essential requirements; what changes is the content of the requirements, carried by the Art. 5-12 rows.")),

    ("FREE-02", "Member States shall not prohibit, restrict or impede the placing on the market of packaging that complies with the sustainability, labelling and information requirements laid down in or pursuant to Articles 5 to 12.", "",
     dict(measure_type="obligation", direction="add",
          duty="Do not prohibit, restrict or impede the placing on the market of packaging that complies with Arts. 5 to 12, and do not enforce additional national requirements against compliant packaging.",
          addressee="Member States",
          cls=S, trigger="compliant packaging offered on the national market",
          frequency="continuous", verification="none",
          article="Art. 4(2) and (3)", when=WHEN_GENERAL,
          drivers=[], named=["waste"], reached=CONVERTERS + FILLERS,
          provision_id="ppwr-art4-free-movement",
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS,
          size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States. Art. 70(4) suspends this for national restrictions on the Annex V point 2 and 3 formats until 1 January 2030.")),

    ("FREE-03", "Member States shall not prohibit, restrict or impede the placing on the market of packaging that complies with the sustainability, labelling and information requirements laid down in or pursuant to Articles 5 to 12.", "",
     dict(measure_type="right", direction="add",
          benefit="Packaging that meets Arts. 5 to 12 may be placed on the market anywhere in the Union: no Member State may block it, and no additional national sustainability or information requirement may be enforced against it. One compliance route replaces 27.",
          addressee="Economic operators placing compliant packaging on the market",
          cls=B, trigger="packaging compliant with Arts. 5 to 12",
          frequency="continuous", verification="self-assessment",
          article="Art. 4(2) and (3)", when=WHEN_GENERAL,
          value_drivers=["V1"], frictions=["F1"],
          named=CONVERTERS + FILLERS, reached=["waste"],
          provision_id="ppwr-art4-free-movement",
          right_basis=dict(text="Member States shall not prohibit, restrict or impede the placing on the market of packaging that complies with the sustainability, labelling and information requirements laid down in or pursuant to Articles 5 to 12.",
                           kind="existence"),
          note="The object rule splits this provision. Art. 4(2) acts on Member State conduct, which is FREE-02; the market access it creates is a faculty the operator did not hold against a divergent national rule, which is this row. Kept as two linked measures rather than one, because neither reading contains the other.",
          nature="new_right", weight="Relief",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          affected_delta="Every operator selling packaging across more than one Member State. Suspended for the Annex V point 2 and 3 formats until 1 January 2030 by Art. 70(4).")),

    # ==============================================  Ch. II  substances (Art. 5)
    ("SUB-01", "Packaging placed on the market shall be so manufactured that the presence and concentration of substances of concern as constituents of the packaging material", "adverse impact on the environment due to microplastics.",
     dict(measure_type="obligation", direction="add",
          duty="Manufacture packaging so that the presence and concentration of substances of concern is minimised, including in emissions and in waste-management outputs such as secondary raw materials and ashes.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="manufacturing packaging placed on the market",
          frequency="continuous", verification="self-assessment",
          article="Art. 5(1)", when=WHEN_GENERAL,
          drivers=["D4"], named=["chem/plastics", "chem"], reached=["waste", "paper", "glass", "alu"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          affected_delta="All packaging manufacturers. 'Substances of concern' takes the ESPR definition via Art. 3(1); what counts is therefore set outside this act.",
          pending="Art. 5(2) requires a Commission report by 31 December 2026, assisted by ECHA, which may list the substances of concern actually caught. Until it lands, 'minimised' has no operative list behind it.")),

    ("SUB-02", "the sum of the concentrations of lead, cadmium, mercury and hexavalent chromium resulting from substances present in packaging or packaging components shall not exceed 100 mg/kg.", "",
     dict(measure_type="obligation", direction="unchanged",
          duty="Keep the sum of lead, cadmium, mercury and hexavalent chromium in packaging or packaging components at or below 100 mg/kg.",
          addressee="Manufacturers and importers of packaging",
          cls=B, trigger="packaging or a packaging component placed on the market",
          frequency="continuous", verification="technical documentation (Annex VII)",
          article="Art. 5(4)", when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=CONVERTERS, reached=["waste", "chem"],
          nature="carry_over", weight="Neutral",
          reclass_from=dict(direction="add",
              note="Filed as 'add' in the single-pass extraction because the direction enum had only add|rem, so a restated rule had to be recorded as an addition and rendered Requirement. `unchanged` now exists and this row takes it: 100 ppm and 100 mg/kg are the same concentration and the limit has bound since 2001."),
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="packaging or packaging components placed on the market",
              obligation="Sum of lead, cadmium, mercury and hexavalent chromium not to exceed 100 ppm by weight, five years from the date in Art. 22(1) of the Directive.",
              source_text="100 ppm by weight five years after the date referred to in Article 22 (i).",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging or a packaging component placed on the market",
              obligation="Sum of lead, cadmium, mercury and hexavalent chromium not to exceed 100 mg/kg."),
          affected_delta="THE LEVEL DOES NOT MOVE. 100 ppm and 100 mg/kg are the same concentration, and the limit has bound since 2001 under 94/62/EC Art. 11(1). Reading this row as a new restriction would be wrong. What does move is the exemption regime, which is SUB-03.",
          note="Carried as a row rather than omitted because the duty is live under this act and an operator has to comply with it; the delta model is what says it is not new.")),

    ("SUB-03", "Delegated acts adopted in accordance with this paragraph shall only be adopted to amend derogations es", "",
     dict(measure_type="obligation", direction="add",
          duty="Rely on a heavy-metals exemption only where a Commission delegated act grants it; the exemptions are now time-limited, subject to marking, information and regular reporting requirements, and reviewable.",
          addressee="Manufacturers relying on a heavy-metals derogation",
          cls=B, trigger="packaging claiming an exemption from the 100 mg/kg limit",
          frequency="per derogation",
          verification="technical documentation (Annex VII)",
          article="Art. 5(8)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=["glass", "chem/plastics"], reached=["waste"],
          nature="reduction", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="packaging entirely made of lead crystal glass",
              obligation="The heavy-metals concentration limits did not apply at all to packaging entirely made of lead crystal glass, with no time limit, no marking duty and no review.",
              source_text="The concentration levels referred to in paragraph 1 shall not apply to packaging entirely made of lead crystal glass as defined in Directive 69/493/EEC",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging claiming an exemption from the 100 mg/kg limit",
              obligation="Exemptions exist only via delegated act amending Decisions 2001/171/EC and 2009/292/EC, must be justified case by case, time-limited, marked, reported on and regularly reviewed."),
          affected_delta="Glass packaging in particular: 94/62/EC gave lead crystal glass a standing statutory exemption in Art. 11(2), and PPWR carries no equivalent. Any continuing relief now has to come through a delegated act with conditions attached.")),

    ("SUB-04", "From 12 August 2026, food-contact packaging shall not be placed on the market if it contains per", "250 ppb for the sum of PFAS measured as the sum of targeted PFAS analysis, where applicable with prior degradation of precursors (polymeric PFAS excluded from quantification); and",
     dict(measure_type="prohibition", direction="add",
          duty="Do not place food-contact packaging on the market at or above 25 ppb for any single PFAS, 250 ppb for the sum of targeted PFAS, or 50 ppm for total PFAS including polymeric.",
          addressee="Manufacturers and importers of food-contact packaging",
          cls=B, trigger="food-contact packaging placed on the market",
          frequency="continuous",
          verification="technical documentation (Annex VII), targeted PFAS analysis",
          article="Art. 5(5)", when="From 12 August 2026 (Art. 5(5))",
          drivers=["D1", "D4", "D7"], named=["chem/plastics", "paper", "foodbev"],
          reached=["chem", "retail", "horeca", "waste"],
          nature="new_obligation", weight="Burden",
          reclass_from=dict(measure_type="obligation",
              note="Art. 5(5) forbids placing food-contact packaging containing PFAS above the limit values on the market. Recorded as obligation/add in the single-pass extraction only because the enum had no prohibition value."),
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="Food-contact packaging across the board, and hardest on fibre-based packaging where PFAS is the standard grease barrier. Genuinely new: 94/62/EC restricted only the four heavy metals, and no PFAS limit existed for packaging.",
          note="A prohibition on the object rule: the provision acts on the placing on the market of a defined product, closing the route rather than conditioning it.",
          pending="Art. 5(5) applies only 'to the extent that the placing on the market of packaging containing such a concentration of PFAS is not prohibited pursuant to another Union legal act', and Art. 5(5) final subparagraph has the Commission evaluate by 12 August 2030 whether to amend or repeal the paragraph to avoid overlap with REACH, 1935/2004 and the POPs Regulation.")),

    ("SUB-05", "if total fluorine exceeds 50 mg/kg the manufacturer, importer or downstream user as defined respectively in Article 3, points (9), (11) and (13) of Regulation (EC) No 1907/2006 shall, upon request, provide", "in order for them to draw up the technical documentation as referred to in Annex VII to this Regulation.",
     dict(measure_type="obligation", direction="add",
          duty="Where total fluorine exceeds 50 mg/kg, supply on request proof of whether the measured fluorine is PFAS or non-PFAS, so the packaging manufacturer or importer can complete its technical documentation.",
          addressee="Manufacturers, importers and downstream users under REACH supplying materials to packaging makers",
          cls=B, trigger="a request where total fluorine in the material exceeds 50 mg/kg",
          frequency="per request", verification="technical documentation (Annex VII)",
          article="Art. 5(5)(c)", when="From 12 August 2026 (Art. 5(5))",
          drivers=["D1", "D4"], named=["chem"], reached=["chem/plastics", "paper", "foodbev"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          affected_delta="Chemicals suppliers upstream of food-contact packaging. This is the supply-chain limb of the PFAS restriction: the duty to prove the content sits one step back from the operator who has to document it.")),

    # ============================================  Ch. II  recyclability (Art. 6)
    ("REC-01", "All packaging placed on the market shall be recyclable.", "",
     dict(measure_type="obligation", direction="add",
          duty="Make all packaging recyclable: designed for material recycling, and collectable, sortable and recycled at scale when it becomes waste.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="packaging placed on the market",
          frequency="continuous", verification="technical documentation (Annex VII)",
          article="Art. 6(1) and (2)",
          when="Design for recycling from 1 January 2030 or 24 months after the Art. 6(4) delegated acts, whichever is later; recycled-at-scale from 1 January 2035 (Art. 6(2))",
          drivers=["D1", "D4", "D7"], named=CONVERTERS, reached=["waste"] + FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="All packaging manufacturers. 94/62/EC Annex II required packaging to be 'recoverable' in general terms; a binary recyclability gate with design criteria behind it is new.",
          pending="The design-for-recycling criteria are set by delegated act due 1 January 2028 (Art. 6(4)) and the recycled-at-scale methodology by implementing act due 1 January 2030 (Art. 6(5)). Until both land, the substantive content of this duty is not knowable.",
          note="Art. 6(11) excludes immediate and outer packaging of medicines and medical devices, contact-sensitive infant formula and medical-food packaging, dangerous-goods transport packaging, and sales packaging of lightweight wood, cork, textile, rubber, ceramic, porcelain or wax.")),

    ("REC-02", "Packaging recyclability shall be expressed in the recyclability performance grades A, B or C as described in Table 3 of Annex II.", "",
     dict(measure_type="obligation", direction="add",
          duty="Assess and grade each packaging unit A, B or C for recyclability; from 2030 do not place packaging below grade C on the market, and from 1 January 2038 do not place packaging below grade B.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="assessing packaging before placing it on the market",
          frequency="per packaging unit", verification="technical documentation (Annex VII)",
          article="Art. 6(3)",
          when="Grade C floor from 1 January 2030 or 24 months after the Art. 6(4) delegated acts, whichever is later; grade B floor from 1 January 2038 (Art. 6(3))",
          drivers=["D1", "D4"], named=CONVERTERS, reached=["waste"] + FILLERS,
          nature="extension", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All packaging manufacturers, on a rising floor: grade C from 2030, grade B from 2038. The 2038 step removes an entire performance grade from the market.")),

    ("REC-03", "Economic operators shall comply with new or updated design for recycling criteria within 3 years of the date of entry into force of the relevant delegated act.", "",
     dict(measure_type="obligation", direction="add",
          duty="Re-comply with design-for-recycling criteria within 3 years each time the Commission adopts or updates them by delegated act.",
          addressee="Economic operators placing packaging on the market",
          cls=B, trigger="entry into force of a new or updated design-for-recycling delegated act",
          frequency="per delegated act", verification="technical documentation (Annex VII)",
          article="Art. 6(4), final subparagraph", when=WHEN_GENERAL,
          drivers=["D4", "D5"], named=CONVERTERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="A standing re-tooling obligation with no end date: every future revision of the criteria restarts a three-year clock for every affected format.")),

    ("REC-04", "the financial contributions paid by producers in order to comply with their extended producer responsibility obligations as laid down in Article 45 shall be modulated in accordance with the recyclability performance grades", "",
     dict(measure_type="obligation", direction="add",
          duty="Pay EPR financial contributions modulated by the packaging's recyclability performance grade.",
          addressee="Producers subject to extended producer responsibility",
          cls=B, trigger="EPR contributions falling due on packaging with a recyclability grade",
          frequency="annual", verification="producer responsibility organisation",
          article="Art. 6(8)", when="18 months after the Art. 6(4) and 6(5) acts enter into force (Art. 6(8))",
          drivers=["D5", "D6"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Every producer paying EPR fees. Better-graded packaging pays less and worse-graded pays more, so the effect is dispersed rather than uniform.",
          note="REJECTED as a benefit row. Fee modulation looks like an incentive and is written as one in the recitals, but the object rule cuts support only where a support's amount, rate, eligibility or existence moves. This is a graduated LEVY on the producer, so it stays on the obligation side whichever way an individual producer's bill goes.")),

    ("REC-05", "innovative packaging that does not comply with the requirements under paragraph 2 may be made available on the market up to 5 years from the end of the calendar year in which it was placed on the market.", "",
     dict(measure_type="right", direction="add",
          benefit="Packaging that qualifies as innovative may be sold for up to five years from the end of the year it was first placed on the market even though it does not meet the recyclability requirement -- a run-in period no other packaging gets.",
          addressee="Economic operators placing innovative packaging on the market",
          cls=B, trigger="packaging notified to the competent authority as innovative, with technical details and a timeline for reaching the recycled-at-scale requirement",
          frequency="per packaging", verification="competent authority",
          article="Art. 6(10)", when="From 1 January 2030 (Art. 6(10))",
          value_drivers=["V2"], frictions=["F1", "F4"],
          named=CONVERTERS, reached=["waste"],
          right_basis=dict(text="innovative packaging that does not comply with the requirements under paragraph 2 may be made available on the market up to 5 years from the end of the calendar year in which it was placed on the market.",
                           kind="existence"),
          nature="new_right", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Operators bringing genuinely novel formats to market. The competent authority decides whether the packaging is innovative; if it says no, the operator must comply with the existing criteria.")),

    # ==========================================  Ch. II  recycled content (Art. 7)
    ("RCY-01", "By 1 January 2030 or 3 years from the date of entry into force of the implementing act referred to in paragraph 8 of this Article, whichever is the latest, any plastic part of packaging placed on the market shall contain", "35 % for plastic packaging other than those referred to in points (a), (b) and (c) of this paragraph.",
     dict(measure_type="obligation", direction="add",
          duty="Meet minimum recycled content in every plastic part of packaging, averaged per manufacturing plant per year: 30% for contact-sensitive PET, 10% for other contact-sensitive plastics, 30% for single-use plastic beverage bottles, 35% for all other plastic packaging.",
          addressee="Manufacturers and importers of plastic packaging",
          cls=B, trigger="a plastic part of packaging placed on the market",
          frequency="annual, averaged per manufacturing plant",
          verification="technical documentation (Annex VII), third-party audit possible under Art. 7(8)",
          article="Art. 7(1)",
          when="From 1 January 2030 or 3 years after the Art. 7(8) implementing act, whichever is later (Art. 7(1))",
          drivers=["D1", "D2", "D4", "D5", "D7"],
          named=["chem/plastics", "foodbev"], reached=["waste", "chem", "retail"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="All plastic packaging converters and their importers. Genuinely new: 94/62/EC set recycling targets for the waste stream but never required recycled content in the product. The feedstock must also be post-consumer, collected in the Union or to equivalent standards, and recycled in an installation meeting Directive 2010/75/EU-equivalent emission rules.",
          pending="Art. 7(13) lets the Commission lower the percentages by delegated act where recycled plastic is unavailable or excessively priced, but only in exceptional cases with severe adverse effects for health, food security or the environment.",
          note="Art. 7(4) and (5) exclude medicinal and veterinary immediate and outer packaging, contact-sensitive medical-device packaging, compostable plastic packaging, dangerous-goods packaging, infant and young-child food packaging, food-contact plastic where recycled content would breach Regulation (EC) No 1935/2004, and any plastic part under 5% of the unit's weight.")),

    ("RCY-02", "By 1 January 2040, any plastic part of packaging placed on the market shall contain the following minimum percentage of recycled content", "65 % for plastic packaging other than those referred to in points (a), (b) and (c) of this paragraph.",
     dict(measure_type="obligation", direction="add",
          duty="Meet the 2040 recycled-content step: 50% for contact-sensitive PET, 25% for other contact-sensitive plastics, 65% for single-use plastic beverage bottles, 65% for all other plastic packaging.",
          addressee="Manufacturers and importers of plastic packaging",
          cls=B, trigger="a plastic part of packaging placed on the market",
          frequency="annual, averaged per manufacturing plant",
          verification="technical documentation (Annex VII)",
          article="Art. 7(2)", when="From 1 January 2040 (Art. 7(2))",
          drivers=["D4", "D5"], named=["chem/plastics", "foodbev"], reached=["waste", "chem", "retail"],
          nature="extension", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="The same population as RCY-01 at roughly double the level. Kept as its own row rather than folded into the 2030 duty because the two bind at different dates and an operator planning capital spend needs them separable.",
          pending="Art. 7(14) has the Commission report by 12 February 2032 on the 2030 percentages and on the feasibility of these, possibly with a legislative proposal amending them.")),

    ("RCY-03", "the calculation and verification of the percentage of recycled content contained in packaging under paragraph 1 shall comply with the rules laid down in the implementing act adopted pursuant to paragraph 8.", "",
     dict(measure_type="obligation", direction="add",
          duty="Calculate and verify recycled-content percentages by the Commission's methodology, and where the methodology requires it submit to independent third-party audit.",
          addressee="Manufacturers of recycled content and of plastic packaging placed on the market",
          cls=B, trigger="claiming a recycled-content percentage",
          frequency="annual", verification="independent third-party audit where the implementing act requires it",
          article="Art. 7(11), with Art. 7(8)",
          when="From 1 January 2029 or 24 months after the Art. 7(8) implementing act, whichever is later (Art. 7(11))",
          drivers=["D1", "D2", "D4", "D5"],
          named=["chem/plastics"], reached=["waste", "chem"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Plastic packaging converters and the recyclers supplying them. This is the verification limb of RCY-01 and binds a year earlier than the content requirement itself.")),

    # ===================================  Ch. II  compostables and minimisation
    ("CMP-01", "sticky labels affixed to fruit and vegetables are placed on the market, that packaging and sticky labels shall be compatible with the standard for composting in industrially controlled conditions", "",
     dict(measure_type="obligation", direction="add",
          duty="Make the packaging listed in Art. 3(1) point (1)(f) and sticky labels on fruit and vegetables compostable in industrially controlled conditions, and home-compostable where the Member State requires it.",
          addressee="Manufacturers of the listed packaging and of fruit and vegetable labels",
          cls=B, trigger="placing the listed packaging or sticky labels on the market",
          frequency="continuous", verification="technical documentation (Annex VII)",
          article="Art. 9(1)", when="By 12 February 2028 (Art. 9(1))",
          drivers=["D1", "D4", "D7"], named=["chem/plastics", "paper", "foodbev"],
          reached=["waste", "retail"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="A narrow set of formats -- tea and coffee singles, sticky fruit labels -- but for those it reverses the general rule: they must be compostable rather than recyclable, by derogation from Art. 6(1).",
          pending="Art. 9(6) has the Commission request harmonised standards for industrial and home compostability by 12 February 2026. The duty bites in 2028 whether or not those standards exist.")),

    ("CMP-02", "packaging other than that referred to in paragraphs 1 and 2, including packaging made of biodegradable plastic polymers and other biodegradable materials, shall be designed for material recycling in accordance with Article 6", "",
     dict(measure_type="obligation", direction="add",
          duty="Design biodegradable-polymer and other biodegradable packaging for material recycling under Art. 6, without affecting the recyclability of other waste streams.",
          addressee="Manufacturers of biodegradable packaging",
          cls=B, trigger="biodegradable packaging outside the Art. 9(1) and 9(2) lists",
          frequency="continuous", verification="technical documentation (Annex VII)",
          article="Art. 9(3)", when="By 12 February 2028 (Art. 9(3))",
          drivers=["D4"], named=["chem/plastics"], reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Closes the route of claiming biodegradability instead of recyclability: outside the two listed cases, biodegradable packaging is held to the same recycling design duty as everything else.")),

    ("MIN-01", "the manufacturer or importer shall ensure that the packaging placed on the market is designed so that its weight and volume is reduced to the minimum necessary to ensure its functionality", "",
     dict(measure_type="obligation", direction="add",
          duty="Design packaging so weight and volume are reduced to the minimum necessary for functionality, and document the assessment against the Annex IV performance criteria.",
          addressee="Manufacturers and importers of packaging",
          cls=B, trigger="packaging placed on the market",
          frequency="per packaging design", verification="technical documentation (Annex VII)",
          article="Art. 10(1) and (4)", when="By 1 January 2030 (Art. 10(1))",
          drivers=["D1", "D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All packaging designers. The documentation limb is the heavy one: Art. 10(4) requires the technical specifications used, the design requirement that prevents further reduction for each Annex IV criterion, and any test results, studies, modelling or simulations relied on.",
          pending="Art. 10(3) has the Commission request harmonised standards by 12 February 2027 specifying maximum weight and volume limits and, where appropriate, wall thickness and maximum empty space for common formats.")),

    ("MIN-02", "packaging with characteristics that aim only to increase the perceived volume of the product, including double walls, false bottoms and unnecessary layers, is not placed on the market", "",
     dict(measure_type="prohibition", direction="add",
          duty="Do not place on the market packaging failing the Annex IV performance criteria, or packaging whose features exist only to increase perceived product volume -- double walls, false bottoms, unnecessary layers.",
          addressee="Manufacturers and importers of packaging",
          cls=B, trigger="packaging design with volume-inflating features",
          frequency="continuous", verification="technical documentation (Annex VII)",
          article="Art. 10(2)", when="By 1 January 2030 (Art. 10(1))",
          drivers=["D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          reclass_from=dict(measure_type="obligation",
              note="Art. 10(2) forbids placing volume-inflating packaging on the market. Recorded as obligation/add in the single-pass extraction only because the enum had no prohibition value."),
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Cosmetics, confectionery and gift packaging most directly. Art. 10(2) exempts designs protected as a Community design or trademark before 11 February 2025 where compliance would destroy the novelty or distinctiveness, and packaging for geographical-indication or quality-scheme products.",
          note="A prohibition on the object rule: it closes a route rather than conditioning it.")),

    ("REU-01", "Packaging placed on the market from 11 February 2025 shall be considered to be reusable where it fulfils all of the following requirements:", "it fulfils the requirements specific to recyclable packaging set out in Article 6, so that it can be recycled when it becomes waste.",
     dict(measure_type="obligation", direction="add",
          duty="Meet all nine reusability criteria before packaging counts as reusable: designed for multiple rotations, emptiable and refillable without damage, reconditionable per Annex VI Part B, labellable, safe to handle, and recyclable at end of life.",
          addressee="Manufacturers of reusable packaging",
          cls=B, trigger="packaging claimed or counted as reusable",
          frequency="per packaging design", verification="technical documentation (Annex VII)",
          article="Art. 11(1)", when="From 11 February 2025 (Art. 11(1))",
          drivers=["D1", "D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Anyone counting packaging towards the Art. 29 re-use targets. Note the date: this definition binds from 11 February 2025, well before the Regulation generally applies on 12 August 2026, so packaging placed on the market in the interim is already being measured against it.",
          pending="The minimum number of rotations for the most-used reusable formats is set by delegated act due 12 February 2027 (Art. 11(2)). Until then criterion (b) has no number behind it.")),

    # ==============================================  Ch. III  labelling (Arts. 12-14)
    ("LAB-01", "packaging placed on the market shall be marked with a harmonised label containing information on its material composition in order to facilitate consumer sorting.", "",
     dict(measure_type="obligation", direction="add",
          duty="Mark packaging with the harmonised material-composition label, pictogram-based and understandable including for people with disabilities; mark compostable packaging as compostable, not home-compostable and not for disposal in nature.",
          addressee="Economic operators placing packaging on the market",
          cls=B, trigger="packaging placed on the market",
          frequency="per packaging unit", verification="market surveillance authority",
          article="Art. 12(1)",
          when="From 12 August 2028 or 24 months after the Art. 12(6) or 12(7) implementing acts, whichever is later (Art. 12(1))",
          drivers=["D1", "D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="extension", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="packaging placed on the market",
              obligation="Packaging had to indicate the nature of the packaging material used for identification and classification by industry, on the basis of Commission Decision 97/129/EC, marked clearly, visibly, legibly and durably on the packaging or the label.",
              source_text="To facilitate collection, reuse and recovery including recycling, packaging shall indicate for the purposes of its identification and classification by the industry concerned the nature of the packaging material(s) used on the basis of Commission Decision 97/129/EC",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging placed on the market",
              obligation="A harmonised, pictogram-based label aimed at CONSUMER SORTING, set by Commission implementing act, with digital marking for packaging containing substances of concern."),
          affected_delta="A real change of addressee, not just of format: 94/62/EC's marking was for identification by industry, and this is a sorting instruction for the consumer. Transport packaging and packaging in a deposit and return system are excluded, e-commerce packaging is not.",
          note="Art. 12(1), second subparagraph, separately requires packaging containing substances of concern to be marked by standardised open digital-marking technologies. Carried in this row's duty rather than split, because it is the same marking obligation with a second trigger.")),

    ("LAB-02", "Reusable packaging placed on the market from 12 February 2029 or 30 months from the date of entry into force of the implementing act adopted pursuant to paragraph 6, whichever is the latest, shall bear a label informing users that the packaging is reusable.", "",
     dict(measure_type="obligation", direction="add",
          duty="Label reusable packaging as reusable, carry a QR code or open digital data carrier giving re-use system and collection-point information and enabling trip and rotation counting, and distinguish reusable from single-use packaging at the point of sale.",
          addressee="Economic operators placing reusable packaging on the market",
          cls=B, trigger="reusable packaging placed on the market",
          frequency="per packaging unit", verification="market surveillance authority",
          article="Art. 12(2)",
          when="From 12 February 2029 or 30 months after the Art. 12(6) implementing act, whichever is later (Art. 12(2))",
          drivers=["D1", "D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="Anyone using reusable packaging. Genuinely new: 94/62/EC had no reusability labelling at all. Art. 12(3) exempts open-loop systems with no system operator under Annex VI.")),

    ("LAB-03", "economic operators shall not provide or display labels, marks, symbols or inscriptions that are likely to mislead or confuse consumers or other end users with respect to the sustainability requirements for packaging", "",
     dict(measure_type="prohibition", direction="add",
          duty="Do not display labels, marks, symbols or inscriptions likely to mislead or confuse consumers about packaging sustainability, other packaging characteristics, or waste-management options where this Regulation has harmonised the labelling.",
          addressee="Economic operators",
          cls=B, trigger="any label, mark, symbol or inscription on packaging",
          frequency="continuous", verification="market surveillance authority",
          article="Art. 12(8)", when=WHEN_GENERAL,
          drivers=[], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          reclass_from=dict(measure_type="obligation",
              note="Art. 12(8) forbids displaying misleading sustainability labels. Recorded as obligation/add in the single-pass extraction only because the enum had no prohibition value."),
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All operators using on-pack environmental marks. Bites hardest on voluntary eco-labels and recyclability claims that duplicate or contradict the harmonised label.",
          note="A prohibition on the object rule: it closes a route rather than conditioning it.")),

    ("LAB-04", "Packaging as referred to in paragraphs 1, 2 and 4 that is manufactured in the Union or imported before the deadlines referred in those paragraphs and that does not comply with the criteria laid down in those paragraphs may be made available on the market until 3 years from the date of entry into force of the labelling requirements laid down in those paragraphs.", "",
     dict(measure_type="right", direction="add",
          benefit="Packaging made or imported before the labelling deadlines may still be sold for three years after those requirements enter into force, so existing stock and pre-printed material do not have to be written off on the deadline.",
          addressee="Economic operators holding pre-deadline packaging stock",
          cls=B, trigger="packaging manufactured in the Union or imported before the Art. 12(1), (2) or (4) deadlines",
          frequency="continuous", verification="none",
          article="Art. 12(12)", when="From the Art. 12 labelling deadlines (Art. 12(12))",
          value_drivers=["V1"], frictions=[],
          named=CONVERTERS + FILLERS, reached=["retail", "waste"],
          right_basis=dict(text="may be made available on the market until 3 years from the date of entry into force of the labelling requirements laid down in those paragraphs.",
                           kind="existence"),
          nature="exemption", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Everyone holding packaging stock or pre-printed film at the labelling deadlines. A sell-through window, not a permanent exemption.")),

    ("LAB-05", "Member States shall ensure that harmonised labels that enable the separate collection of each material specific fraction of packaging waste that is intended to be discarded in separate receptacles are affixed, printed or engraved visibly, legibly and indelibly on all waste receptacles for collection of packaging waste.", "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure harmonised labels enabling separate collection of each material fraction are affixed visibly, legibly and indelibly on all packaging-waste receptacles.",
          addressee="Member States",
          cls=S, trigger="waste receptacles for the collection of packaging waste",
          frequency="continuous", verification="none",
          article="Art. 13(1)",
          when="From 12 August 2028 or 30 months after the Art. 13(2) implementing acts, whichever is later (Art. 13(1))",
          drivers=["D4"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States, and through Art. 45(2)(a) the cost falls on producers via EPR fees. Receptacles under a deposit and return system are excluded.")),

    ("LAB-06", "Environmental claims as defined in Article 2, point (o), of Directive 2005/29/EC concerning packaging properties for which legal requirements are set out in this Regulation may be made in relation to packaging placed on the market if they fulfil the following requirements:", "the claims specify whether they relate to the packaging unit, part of the packaging unit or all packaging placed on the market by the economic operator.",
     dict(measure_type="obligation", direction="add",
          duty="Make an environmental claim about a packaging property regulated here only where the packaging exceeds the applicable minimum requirement, and state whether the claim covers the unit, part of it, or all the operator's packaging.",
          addressee="Economic operators making environmental claims about packaging",
          cls=B, trigger="an environmental claim about a packaging property regulated by this Regulation",
          frequency="per claim", verification="technical documentation (Annex VII)",
          article="Art. 14", when=WHEN_GENERAL,
          drivers=["D1"], named=CONVERTERS + FILLERS, reached=["retail"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Brand owners and retailers making on-pack green claims. The bar is 'exceeding the applicable minimum requirements' -- claiming compliance with the law is no longer a claim that may be made.")),

    # ==========================  Ch. IV  economic operator obligations (Arts. 15-23)
    ("OPS-01", "Before placing packaging on the market, manufacturers shall carry out the conformity assessment procedure referred to in Article 38 or have it carried out on their behalf, and shall draw up the technical documentation referred to in Annex VII.", "",
     dict(measure_type="obligation", direction="add",
          duty="Carry out the Annex VII conformity assessment, draw up the technical documentation and the EU declaration of conformity, and keep both for 5 years for single-use and 10 years for reusable packaging.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="before placing packaging on the market",
          frequency="per packaging type", verification="self-assessment against Annex VII",
          article="Art. 15(2) and (3)", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D5", "D7"], named=CONVERTERS, reached=FILLERS + ["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="Every packaging manufacturer selling into the EU. This is the single largest new administrative burden in the act: 94/62/EC had a presumption-of-conformity mechanism but no conformity assessment procedure, no technical documentation file and no EU declaration of conformity for packaging.")),

    ("OPS-02", "Manufacturers shall ensure that procedures are in place for series production of packaging to remain in conformity with this Regulation.", "",
     dict(measure_type="obligation", direction="add",
          duty="Keep series production in conformity, tracking changes in packaging design and characteristics and in harmonised standards, common specifications and other technical specifications.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="series production of packaging",
          frequency="continuous", verification="self-assessment",
          article="Art. 15(4)", when=WHEN_GENERAL,
          drivers=["D4", "D5"], named=CONVERTERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All packaging manufacturers running series production. A standing quality-system duty rather than a one-off assessment.")),

    ("OPS-03", "Suppliers shall provide the manufacturer with all the information and documentation necessary for the manufacturer to demonstrate the conformity of the packaging and the packaging materials with this Regulation", "That information and documentation shall be provided in either paper or electronic form.",
     dict(measure_type="obligation", direction="add",
          duty="Give the packaging manufacturer all information and documentation it needs to demonstrate conformity, including the Annex VII technical documentation, in a language the manufacturer easily understands.",
          addressee="Suppliers of packaging or packaging materials",
          cls=B, trigger="supplying packaging or packaging materials to a manufacturer",
          frequency="continuous", verification="none",
          article="Art. 16", when=WHEN_GENERAL,
          drivers=["D1"], named=["chem", "paper", "chem/plastics", "glass", "alu", "wood"],
          reached=FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Material suppliers one step upstream of the packaging manufacturer -- resin producers, paper mills, glass and metal suppliers -- who were not previously in a packaging compliance chain at all.")),

    ("OPS-04", "Importers shall only place on the market packaging which is in conformity with the requirements laid down in or pursuant to Articles 5 to 12.", "",
     dict(measure_type="obligation", direction="add",
          duty="Before placing packaging on the market, verify that the manufacturer carried out the conformity assessment and drew up the technical documentation, that the packaging is labelled under Art. 12 and accompanied by the required documents, and mark your own name, trade name and contact address on the packaging.",
          addressee="Importers of packaging",
          cls=B, trigger="before placing imported packaging on the market",
          frequency="per consignment", verification="documentary check on the manufacturer",
          article="Art. 18(1) to (3)", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D5", "D7"], named=CONVERTERS + FILLERS, reached=["retail", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All importers of packaging and packaged goods. Art. 21 turns an importer or distributor into a manufacturer for Art. 15 purposes where it sells under its own name or trademark, or modifies packaging in a way affecting compliance.")),

    ("OPS-05", "Before making packaging available on the market, distributors shall verify that:", "the manufacturer and the importer have complied with the requirements set out in Article 15(5) and (6) and Article 18(3), respectively.",
     dict(measure_type="obligation", direction="add",
          duty="Before making packaging available, verify that the producer is registered in the Art. 44 register, that the packaging carries its Art. 12 labelling, and that the manufacturer and importer have marked their identification; do not make it available until any non-compliance is corrected.",
          addressee="Distributors of packaging",
          cls=B, trigger="before making packaging available on the market",
          frequency="continuous", verification="documentary check on the producer register",
          article="Art. 19(1) to (3)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=["retail"], reached=CONVERTERS + FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Wholesalers and retailers. A due-diligence duty over the register and the labelling of everything they stock, plus a duty to protect conformity during their own storage and transport.")),

    ("OPS-06", "Fulfilment service providers shall ensure that for packaging, whether empty or with a product, that they handle, the conditions during warehousing, handling and packing, addressing or dispatching do not jeopardise the packaging’s compliance", "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure warehousing, handling, packing, addressing and dispatch conditions do not jeopardise the packaging's compliance with Arts. 5 to 12.",
          addressee="Fulfilment service providers",
          cls=B, trigger="handling packaging in the course of a fulfilment service",
          frequency="continuous", verification="none",
          article="Art. 20", when=WHEN_GENERAL,
          drivers=["D4"], named=["retail"], reached=CONVERTERS + FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Third-party logistics and e-commerce fulfilment operators, newly inside a packaging compliance regime.")),

    ("OPS-07", "Economic operators shall, upon request, provide information to the market surveillance authorities on the following:", "as regards reusable packaging: for 10 years from the date they have supplied or been supplied with the reusable packaging.",
     dict(measure_type="obligation", direction="add",
          duty="On request, identify to market surveillance authorities every operator that supplied you with packaging or packaged products and every operator you supplied, retaining the ability to do so for 5 years for single-use and 10 years for reusable packaging.",
          addressee="Economic operators",
          cls=B, trigger="a market surveillance authority request",
          frequency="per request", verification="market surveillance authority",
          article="Art. 22", when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Every operator in the packaging chain. A ten-year traceability record for reusable packaging is a data-retention duty, not just a reporting one.")),

    ("OPS-08", "Packaging waste management operators shall, on an annual basis, provide the competent authorities with the information on packaging waste listed in Table 3 of Annex XII", "",
     dict(measure_type="obligation", direction="add",
          duty="Report the Annex XII Table 3 packaging-waste information to the competent authority annually through the Art. 35(1) electronic registry, and give producers or their producer responsibility organisation everything they need for their own Art. 44(10) reporting.",
          addressee="Packaging waste management operators",
          cls=B, trigger="each calendar year of packaging waste managed",
          frequency="annual", verification="competent authority",
          article="Art. 23", when=WHEN_GENERAL,
          drivers=["D1", "D4", "D5"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Waste management operators across the Union. Their reporting is what the Member State's Art. 56 return to the Commission is built from, so the data duty is load-bearing for the whole targets regime.")),

    # =====================  Ch. V  excessive packaging, bans, re-use (Arts. 24-34)
    ("EXC-01", "economic operators who fill grouped packaging, transport packaging or e-commerce packaging shall ensure that the maximum empty space ratio, expressed as a percentage, is 50 %.", "",
     dict(measure_type="obligation", direction="add",
          duty="Keep empty space in grouped, transport and e-commerce packaging at or below 50%, counting filling materials such as paper cuttings, air cushions, bubble wrap and foam chips as empty space.",
          addressee="Economic operators who fill grouped, transport or e-commerce packaging",
          cls=B, trigger="filling grouped, transport or e-commerce packaging",
          frequency="continuous", verification="self-assessment against the Art. 24(2) methodology",
          article="Art. 24(1)",
          when="From 1 January 2030 or 3 years after the Art. 24(2) implementing acts, whichever is later (Art. 24(1))",
          drivers=["D4", "D7"], named=["retail", "foodbev"], reached=["paper", "chem/plastics", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=None,
          affected_delta="E-commerce and distribution most of all. Genuinely new: 94/62/EC's Annex II required packaging volume and weight to be the minimum needed, but set no ratio and no measurable test. Art. 24(5) exempts operators using sales packaging as e-commerce packaging or reusable packaging within a re-use system.")),

    ("EXC-02", "the economic operators who fill sales packaging shall ensure that empty space is reduced to the minimum necessary for ensuring the packaging functionality, including product protection.", "",
     dict(measure_type="obligation", direction="add",
          duty="Reduce empty space in sales packaging to the minimum necessary for functionality and product protection, assessed at the time of filling for products subject to settlement or requiring headspace.",
          addressee="Economic operators who fill sales packaging",
          cls=B, trigger="filling sales packaging",
          frequency="continuous", verification="self-assessment",
          article="Art. 24(4)", when="By 12 February 2028 (Art. 24(4))",
          drivers=["D4"], named=["foodbev", "retail"], reached=["paper", "chem/plastics", "glass", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Food, drink and consumer-goods fillers. No fixed ratio here, unlike Art. 24(1): the standard is qualitative, which makes it harder to plan against and easier to dispute.")),

    ("BAN-01", "From 1 January 2030, economic operators shall not place on the market packaging in the formats and for the uses listed in Annex V.", "",
     dict(measure_type="prohibition", direction="add",
          duty="Do not place on the market any packaging in the formats and for the uses listed in Annex V -- single-use grouped packaging for multipacks, single-use packaging for unprocessed fresh fruit and vegetables, single-use packaging for food and drink consumed on premises in the HORECA sector, single-use condiment and sauce sachets, hotel miniature toiletries, and very light plastic carrier bags outside hygiene or loose-food use.",
          addressee="Economic operators placing packaging on the market",
          cls=B, trigger="packaging in an Annex V format placed on the market",
          frequency="continuous", verification="market surveillance authority",
          article="Art. 25(1)", when="From 1 January 2030 (Art. 25(1))",
          drivers=["D7"], named=["chem/plastics", "foodbev", "retail", "horeca"],
          reached=["paper", "waste"],
          nature="new_obligation", weight="Burden",
          reclass_from=dict(measure_type="obligation",
              note="Art. 25(1) forbids placing the Annex V formats on the market. Recorded as obligation/add in the single-pass extraction only because the enum had no prohibition value."),
          size_scope=ALL_BANDS,
          size_scope_note="No size band is removed, but Art. 25(4) lets Member States allow MICRO-ENTERPRISES as defined in Recommendation 2003/361/EC to keep using the Annex V point 3 formats where it is demonstrably not technically feasible to avoid them or to reach re-use infrastructure. An eligibility carve-out on this duty, not a separate benefit.",
          prior_rule=None,
          affected_delta="HORECA, retail and fresh-produce packers most directly. Genuinely new as EU-wide law: 94/62/EC had no format bans at all, only the carrier-bag reduction duty. Art. 70(4) lets Member States keep pre-2025 national restrictions on the Annex V point 2 and 3 formats until 1 January 2030, and suspends Art. 4(3) for them until then.",
          note="A prohibition on the object rule: the provision acts on the placing on the market of named formats, closing the route rather than conditioning it.")),

    ("RSY-01", "Economic operators who make reusable packaging available on the territory of a Member State for the first time shall ensure that a system is in place in that Member State for the re-use of that packaging which includes an incentive to ensure the collection of that packaging and which meets the requirements laid down in Annex VI.", "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure a re-use system meeting Annex VI, including a collection incentive, exists in each Member State where you first make reusable packaging available, and document the system's compliance in the technical documentation with written confirmations from system participants.",
          addressee="Economic operators first making reusable packaging available in a Member State",
          cls=B, trigger="making reusable packaging available in a Member State for the first time",
          frequency="per Member State", verification="technical documentation (Annex VII), written confirmations from participants",
          article="Art. 26", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D4", "D7"], named=CONVERTERS + FILLERS, reached=["waste", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Anyone introducing reusable packaging into a new national market. Using an existing re-use system already in place satisfies the duty, so the burden falls hardest where no system exists yet.")),

    ("RSY-02", "Economic operators that make use of reusable packaging shall participate in one or more re-use systems and shall ensure that the re-use systems within which the reusable packaging can be re-used comply with the requirements laid down in Part A of Annex VI.", "",
     dict(measure_type="obligation", direction="add",
          duty="Participate in one or more Annex VI Part A re-use systems, recondition reusable packaging per Annex VI Part B before offering it again, and in closed-loop systems return packaging to an approved collection point.",
          addressee="Economic operators using reusable packaging",
          cls=B, trigger="use of reusable packaging",
          frequency="continuous", verification="re-use system operator",
          article="Art. 27", when=WHEN_GENERAL,
          drivers=["D3", "D5"], named=CONVERTERS + FILLERS, reached=["waste", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All users of reusable packaging. Art. 27(3) allows a third party to be appointed to run mutualised systems and to carry these obligations on the operator's behalf.")),

    ("RFL-01", "Economic operators who offer the possibility to purchase products through refill shall inform end users of the following (‘rules for refill’):", "The rules for refill shall be regularly updated and shall be either clearly displayed on the premises or otherwise provided to end users.",
     dict(measure_type="obligation", direction="add",
          duty="Publish and keep updated the rules for refill -- permitted container types, hygiene standards, and the end user's own health and safety responsibility -- displayed on the premises or otherwise provided.",
          addressee="Economic operators offering refill",
          cls=B, trigger="offering products for purchase through refill",
          frequency="continuous", verification="none",
          article="Art. 28(1)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=["retail", "horeca"], reached=["foodbev", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Retailers and HORECA operating refill stations.")),

    ("RFL-02", "Economic operators who offer the possibility to purchase products through refill shall ensure that refill stations comply with the requirements laid down in Part C of Annex VI", "",
     dict(measure_type="obligation", direction="add",
          duty="Make refill stations comply with Annex VI Part C and with other Union requirements for selling through refill, and do not give away free packaging or containers at refill stations unless they meet Annex VI or sit in a deposit and return system.",
          addressee="Economic operators offering refill",
          cls=B, trigger="operating a refill station",
          frequency="continuous", verification="market surveillance authority",
          article="Art. 28(2) and (3)", when=WHEN_GENERAL,
          drivers=["D4"], named=["retail", "horeca"], reached=["foodbev", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Retail and HORECA refill operators. Art. 28(3) closes the loophole of handing out free single-use containers at the refill point.")),

    ("RFL-03", "Economic operators may refuse to refill a container provided by the end user if the end user does not comply with the rules for refill communicated by the economic operator pursuant to paragraph 1", "Economic operators shall bear no liability for hygiene or food safety issues that arise from the use of containers provided by the end user.",
     dict(measure_type="right", direction="add",
          benefit="An operator may refuse to fill a customer's own container where the refill rules are not met -- in particular where the container is unhygienic or unsuitable for food or drink -- and bears no liability for hygiene or food-safety problems arising from a container the customer supplied.",
          addressee="Economic operators offering refill",
          cls=B, trigger="an end user presenting a container that does not meet the published rules for refill",
          frequency="per refill", verification="none",
          article="Art. 28(4)", when=WHEN_GENERAL,
          value_drivers=["V1"], frictions=[],
          named=["retail", "horeca"], reached=["foodbev"],
          right_basis=dict(text="Economic operators shall bear no liability for hygiene or food safety issues that arise from the use of containers provided by the end user.",
                           kind="existence"),
          nature="new_right", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Retail and HORECA refill operators. The liability shield is the operative half: without it the refill duties in Arts. 32 and 33 would carry an uninsurable food-safety exposure.")),

    ("RFL-04", "final distributors with a sales area of more than 400 m2 shall endeavour to dedicate 10 % of that sales area to refill stations for both food and non-food products.", "",
     dict(measure_type="obligation", direction="add",
          duty="Endeavour to dedicate 10% of sales area to refill stations for food and non-food products.",
          addressee="Final distributors with a sales area over 400 m2",
          cls=B, trigger="a sales area of more than 400 m2",
          frequency="continuous", verification="none",
          article="Art. 28(5)", when="From 1 January 2030 (Art. 28(5))",
          drivers=["D4"], named=["retail"], reached=["foodbev", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Banded by SALES AREA, not by employees or turnover: only final distributors above 400 m2 are in scope. The A-D bands cannot express that, so they record only that the duty is not employee-banded.",
          affected_delta="Large-format grocery and general retail. An endeavour obligation, not a hard target -- it carries no measurement or reporting duty and no penalty limb under Art. 68(2).",
          note="Carried as an obligation despite 'shall endeavour' because the addressee, trigger and content are all fixed; the softness is in the standard of compliance, which `duty` states rather than hides.")),

    ("RTG-01", "economic operators that use transport packaging, or sales packaging used for transporting products, including for products distributed via e-commerce, within the territory of the Union, in the form of pallets", "shall ensure that at least 40 % of such packaging in total is reusable packaging within a re-use system.",
     dict(measure_type="obligation", direction="add",
          duty="Ensure at least 40% of transport packaging -- pallets, foldable plastic boxes, trays, crates, IBCs, pails, drums, canisters, pallet wrappings and straps -- is reusable within a re-use system, rising to an endeavour of 70% from 2040.",
          addressee="Economic operators using transport packaging in the Union",
          cls=B, trigger="use of transport or transport-purpose sales packaging within the Union",
          frequency="annual, per calendar year",
          verification="competent authority, on the Art. 31 report",
          article="Art. 29(1)", when="From 1 January 2030; 70% endeavour from 1 January 2040 (Art. 29(1))",
          drivers=["D4", "D5", "D7"], named=["retail", "foodbev"],
          reached=["chem/plastics", "wood", "paper", "waste", "auto", "build"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Art. 29(13) exempts an operator that in a calendar year both made available not more than 1 000 kg of packaging in the Member State and falls within the micro-enterprise definition in Recommendation 2003/361/EC. Both limbs must be met. An eligibility carve-out on this duty, not a separate benefit.",
          prior_rule=None,
          affected_delta="Manufacturing and distribution across every sector that ships on pallets. Genuinely new: 94/62/EC set no re-use targets at all -- its Art. 5 merely permitted Member States to encourage re-use. Art. 29(4) excludes dangerous-goods packaging, custom packaging for large machinery, flexible food-contact transport packaging, and cardboard boxes.")),

    ("RTG-02", "economic operators that use transport packaging or sales packaging used for transporting products, in the forms as listed in paragraph 1 of this Article, within the territory of the Union, between different sites on which the operator performs its activity", "shall ensure that such packaging is reusable within a re-use system.",
     dict(measure_type="obligation", direction="add",
          duty="Use only reusable transport packaging within a re-use system for movements between your own sites and those of linked or partner enterprises.",
          addressee="Economic operators moving goods between their own or linked sites",
          cls=B, trigger="transport between sites of the operator or of a linked or partner enterprise",
          frequency="continuous", verification="competent authority, on the Art. 31 report",
          article="Art. 29(2)", when="From 1 January 2030 (Art. 29(2))",
          drivers=["D4", "D7"], named=["retail", "foodbev"],
          reached=["chem/plastics", "wood", "paper", "waste", "auto", "build"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Same Art. 29(13) micro-enterprise and 1 000 kg carve-out as RTG-01.",
          affected_delta="A 100% requirement, not a percentage target: intra-group and inter-site movements must be fully reusable. Much sharper than the 40% in Art. 29(1) and easy to miss because it sits as a derogation.")),

    ("RTG-03", "economic operators that use transport packaging or sales packaging used for transporting products, including for products distributed via e-commerce, in the forms as listed in paragraph 1, to deliver products to another economic operator within the same Member State", "shall ensure that such packaging is reusable within a re-use system.",
     dict(measure_type="obligation", direction="add",
          duty="Use only reusable transport packaging within a re-use system for deliveries to another economic operator inside the same Member State.",
          addressee="Economic operators delivering to another operator in the same Member State",
          cls=B, trigger="B2B delivery within a single Member State",
          frequency="continuous", verification="competent authority, on the Art. 31 report",
          article="Art. 29(3)", when="From 1 January 2030 (Art. 29(3))",
          drivers=["D4", "D7"], named=["retail", "foodbev"],
          reached=["chem/plastics", "wood", "paper", "waste", "auto", "build"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Same Art. 29(13) micro-enterprise and 1 000 kg carve-out as RTG-01.",
          affected_delta="Domestic B2B distribution, again at 100% rather than a percentage. Cross-border B2B stays on the 40% target in Art. 29(1), so the duty differs by whether a delivery crosses a national border.")),

    ("RTG-04", "economic operators that use grouped packaging in the form of boxes, excluding cardboard, outside of sales packaging to group a certain number of products to create a stock-keeping or distribution unit shall ensure that at least 10 % of such packaging is reusable packaging within a re-use system.", "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure at least 10% of grouped packaging in the form of boxes, excluding cardboard, is reusable within a re-use system, rising to an endeavour of 25% from 2040.",
          addressee="Economic operators using grouped packaging boxes",
          cls=B, trigger="use of non-cardboard grouped packaging boxes",
          frequency="annual, per calendar year", verification="competent authority, on the Art. 31 report",
          article="Art. 29(5)", when="From 1 January 2030; 25% endeavour from 1 January 2040 (Art. 29(5))",
          drivers=["D4", "D5"], named=["retail", "foodbev"], reached=["chem/plastics", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Same Art. 29(13) micro-enterprise and 1 000 kg carve-out as RTG-01.",
          affected_delta="Note the cardboard exclusion: this target pushes against plastic crates and boxes specifically, and leaves fibre-based grouped packaging outside it.")),

    ("RTG-05", "final distributors that make alcoholic and non-alcoholic beverages in sales packaging available on the territory of a Member State to consumers shall ensure that at least 10 % of those products are made available in reusable packaging within a re-use system.", "",
     dict(measure_type="obligation", direction="add",
          duty="Make at least 10% of alcoholic and non-alcoholic beverages available in reusable packaging within a re-use system, rising to an endeavour of 40% from 2040, and ensure own-brand packaged products contribute fairly and proportionately.",
          addressee="Final distributors of beverages",
          cls=B, trigger="making beverages in sales packaging available to consumers in a Member State",
          frequency="annual, per calendar year", verification="competent authority, on the Art. 31 report",
          article="Art. 29(6)", when="From 1 January 2030; 40% endeavour from 1 January 2040 (Art. 29(6))",
          drivers=["D4", "D5", "D7"], named=["retail", "foodbev"],
          reached=["glass", "chem/plastics", "alu", "waste", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Three carve-outs, all eligibility attributes on this duty: Art. 29(10) exempts a final distributor with a sales area of not more than 100 m2 in that year; Art. 29(11) lets Member States exempt sales areas on islands under 2 000 inhabitants or in municipalities under 54 persons/km2, except population centres over 5 000; Art. 29(13) exempts micro-enterprises under the 1 000 kg limb.",
          affected_delta="Beverage producers and grocery retail, and the single most commercially significant target in the act. Art. 29(7) excludes highly perishable beverages, milk and milk products, most grapevine products, aromatised wine, similar fruit and vegetable fermented drinks, and spirits -- so the target lands on water, soft drinks and beer.")),

    ("RTG-06", "Final distributors as referred to in paragraph 6 shall take back, free of charge, all reusable packaging of the same type, form and size as the packaging made available on the market by them", "The final distributor shall fully redeem associated deposits or notify the return of the packaging according to the governance rules of the specific re-use system in order that any associated deposits be redeemed, as the case may be.",
     dict(measure_type="obligation", direction="add",
          duty="Take back free of charge all reusable packaging of the same type, form and size you made available, at or close to the point of handover, and fully redeem or notify the associated deposit.",
          addressee="Final distributors subject to the beverage re-use target",
          cls=B, trigger="a consumer returning reusable beverage packaging",
          frequency="continuous", verification="none",
          article="Art. 29(9)", when="From 1 January 2030 (Art. 29(6))",
          drivers=["D4", "D6", "D7"], named=["retail"], reached=["foodbev", "glass", "waste", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Applies even to distributors exempted from the target itself: Art. 29(11) requires an exempted distributor that nonetheless sells in reusable packaging to arrange take-back under this paragraph.",
          affected_delta="Grocery retail. Take-back requires physical space, handling and deposit reconciliation at every store, and it survives the target exemptions.")),

    ("RTG-07", "Member States may allow final distributors to form pools for the purpose of meeting their obligations laid down in paragraph 6", "only covers beverage categories made available on the territory of a Member State by all pool members.",
     dict(measure_type="right", direction="add",
          benefit="Where the Member State allows it, final distributors may pool to meet the beverage re-use target together rather than each hitting 10% alone -- up to five members, up to 40% of the relevant beverage category's market share.",
          addressee="Final distributors subject to the Art. 29(6) beverage target",
          cls=B, trigger="a Member State that has allowed pooling, and a pool within the 40% market-share and five-member limits (the member limit not applying to distributors under one brand)",
          frequency="per calendar year", verification="competent authority",
          article="Art. 29(12)", when="From 1 January 2030 (Art. 29(6))",
          value_drivers=["V1"], frictions=["F1", "F4"],
          named=["retail"], reached=["foodbev", "waste"],
          right_basis=dict(text="Member States may allow final distributors to form pools for the purpose of meeting their obligations laid down in paragraph 6",
                           kind="existence"),
          nature="new_right", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Smaller grocery chains in Member States that switch pooling on. The conditionality is real and is carried in `trigger`: this faculty does not exist unless the Member State creates it, so its availability differs across the internal market.",
          note="Kept on the benefit side despite the Member State gate because the basis object is verbatim and the object acted on is the distributor's compliance route. The gate is recorded in `trigger` rather than dropped, which is the honest way to carry a conditional conferral.",
          pending="The detailed conditions and reporting requirements for pooling are set by delegated act due 1 January 2028 (Art. 29(12), final subparagraph). Pool members must also satisfy Arts. 101 and 102 TFEU and must not share prospective sales data.")),

    ("RTG-08", "For the purpose of demonstrating the achievement of the targets set out in Article 29(1) and (5), the economic operator using the packaging shall calculate, for each target separately, the following:", "the total number of sales units or total volume of beverages made available on the territory of a Member State in packaging other than that referred to in point (a) in a calendar year.",
     dict(measure_type="obligation", direction="add",
          duty="Calculate achievement of each re-use target separately, in equivalent units of the listed formats for transport and grouped packaging, and in sales units or volume of beverages for the final-distributor targets.",
          addressee="Economic operators and final distributors subject to the Art. 29 targets",
          cls=B, trigger="demonstrating achievement of an Art. 29 or Art. 33 target",
          frequency="annual, per calendar year", verification="competent authority",
          article="Art. 30(1) and (2)", when="From 1 January 2030 (Art. 29)",
          drivers=["D1", "D4", "D5"], named=["retail", "foodbev"], reached=["chem/plastics", "wood", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="Follows the carve-outs on the underlying targets.",
          affected_delta="Everyone inside an Art. 29 target. The counting unit differs by target, so an operator caught by several of them runs several parallel calculations.")),

    ("RTG-09", "Economic operators as referred to in Article 29(1) to (8) shall submit a report containing data concerning the achievement of the re-use targets set out in Article 29 for each calendar year to the competent authority referred to in Article 40.", "",
     dict(measure_type="obligation", direction="add",
          duty="Report re-use target achievement to the competent authority within 6 months of each reporting year's end, through its electronic system and in its format, with further information on request.",
          addressee="Economic operators subject to the Art. 29 re-use targets",
          cls=B, trigger="the end of a reporting year, first year 2030",
          frequency="annual", verification="competent authority",
          article="Art. 31", when="First reporting year 2030 (Art. 31(3))",
          drivers=["D1", "D5"], named=["retail", "foodbev"], reached=["chem/plastics", "wood", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="Follows the carve-outs on the underlying targets.",
          affected_delta="The report is made public by the Member State under Art. 31(6), so this is a disclosure duty as well as a reporting one.")),

    ("TKA-01", "final distributors that conduct their business activity in the HORECA sector and that make available on the territory of a Member State hot or cold beverages in take-away packaging shall provide a system for consumers to bring their own container to be filled;", "",
     dict(measure_type="obligation", direction="add",
          duty="Provide a system letting consumers bring their own container to be filled with take-away hot or cold beverages and with ready-prepared food, at no higher cost and on no less favourable terms than the same product in single-use packaging, and inform consumers of the option at the point of sale.",
          addressee="Final distributors in the HORECA sector selling take-away food and drink",
          cls=B, trigger="making take-away beverages or ready-prepared food available",
          frequency="continuous", verification="none",
          article="Art. 32", when="By 12 February 2027 (Art. 32(1))",
          drivers=["D4", "D7"], named=["horeca", "retail"], reached=["foodbev", "chem/plastics", "paper", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No micro-enterprise exemption here, unlike Art. 33(4). Every HORECA final distributor selling take-away is in scope regardless of size.",
          prior_rule=None,
          affected_delta="The whole HORECA take-away trade, and the earliest hard operational date in the act at 12 February 2027. The no-higher-cost rule removes the option of pricing the behaviour away. Genuinely new -- no equivalent in 94/62/EC.")),

    ("TKA-02", "final distributors that conduct their business activity in the HORECA sector and that make available on the territory of a Member State hot or cold beverages or ready-prepared food in take-away packaging shall give consumers the option of obtaining the products in re-useable packaging within a system for re-use.", "",
     dict(measure_type="obligation", direction="add",
          duty="Offer consumers the option of take-away food and drink in reusable packaging within a re-use system, at no higher cost and on no less favourable terms than single-use, informed at the point of sale; from 2030 endeavour to offer 10% of products in a reusable format.",
          addressee="Final distributors in the HORECA sector selling take-away food and drink",
          cls=B, trigger="making take-away beverages or ready-prepared food available",
          frequency="continuous", verification="none",
          article="Art. 33", when="By 12 February 2028; 10% endeavour from 2030 (Art. 33(1) and (5))",
          drivers=["D3", "D4", "D7"], named=["horeca", "retail"],
          reached=["foodbev", "chem/plastics", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Art. 33(4) exempts final distributors falling within the micro-enterprise definition in Recommendation 2003/361/EC as applicable on 11 February 2025. An eligibility carve-out on this duty, not a separate benefit -- and note it does NOT extend to the Art. 32 bring-your-own-container duty.",
          affected_delta="HORECA above micro size. Heavier than Art. 32 because it requires an actual re-use system -- collection, washing, logistics -- not merely accepting a customer's container.")),

    # Art. 34(1) carries TWO things and they move in opposite directions: a
    # consumption level that is carried over untouched, and a recurrence clause
    # that is genuinely new. Marking the whole provision `unchanged` would
    # assert the recurrence did not happen; marking it all `add` reads the 40
    # as a new ceiling. So it splits, on the same multi-perspective rule that
    # splits Art. 4 -- BAG-02 is the carried-over level, BAG-01 the delta.
    ("BAG-01", "A sustained reduction is considered to be achieved if the annual consumption does not exceed 40 lightweight plastic carrier bags per capita, or the equivalent target in weight, by 31 December 2025 and subsequently by 31 December each year thereafter.", "",
     dict(measure_type="obligation", direction="add",
          duty="Meet the 40-bags-per-capita ceiling in EVERY year after 2025, not only in 2025, and lose the alternative route of discharging the duty by ensuring bags are not supplied free of charge.",
          addressee="Member States",
          cls=S, trigger="annual national consumption of lightweight plastic carrier bags, in each year after 2025",
          frequency="annual", verification="reporting to the Commission under Art. 56(1)(b)",
          article="Art. 34(1), second subparagraph", when="Each year from 31 December 2026 (Art. 34(1))",
          drivers=["D5"], named=["waste"], reached=["chem/plastics", "retail"],
          provision_id="ppwr-art34-carrier-bags",
          nature="extension", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="annual national consumption of lightweight plastic carrier bags",
              obligation="Measures ensuring the annual consumption level does not exceed 90 lightweight plastic carrier bags per person by 31 December 2019 and 40 by 31 December 2025, or equivalent targets in weight -- a one-off endpoint with no obligation stated for the years after 2025.",
              source_text="the adoption of measures ensuring that the annual consumption level does not exceed 90 lightweight plastic carrier bags per person by 31 December 2019 and 40 lightweight plastic carrier bags per person by 31 December 2025, or equivalent targets set in weight.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="annual national consumption of lightweight plastic carrier bags",
              obligation="Consumption not to exceed 40 lightweight plastic carrier bags per capita by 31 December 2025 AND subsequently by 31 December each year thereafter."),
          affected_delta="This row is the DELTA only. The directive set 2025 as an endpoint; PPWR makes 40 a standing annual ceiling with no terminal date, and drops the alternative compliance route in Art. 4(1a)(b) under which a Member State could instead ensure bags were not supplied free of charge. Both are real new burdens on the Member State, so this row is `add` and renders Requirement. The 40 itself is BAG-02 and is unchanged.",
          note="Split from BAG-02 on the multi-perspective rule. Art. 34(1) states one sentence that does two things, and a single row would have to lie about one of them.")),

    ("BAG-02", "Member States shall take measures to achieve a sustained reduction in the consumption of lightweight plastic carrier bags on their territory.", "",
     dict(measure_type="obligation", direction="unchanged",
          duty="Keep annual consumption of lightweight plastic carrier bags at or below 40 per capita -- the level itself, unchanged from the repealed directive.",
          addressee="Member States",
          cls=S, trigger="annual national consumption of lightweight plastic carrier bags",
          frequency="annual", verification="reporting to the Commission under Art. 56(1)(b)",
          article="Art. 34(1), first subparagraph", when="By 31 December 2025 (Art. 34(1))",
          drivers=["D5"], named=["waste"], reached=["chem/plastics", "retail"],
          provision_id="ppwr-art34-carrier-bags",
          nature="carry_over", weight="Neutral",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="annual national consumption of lightweight plastic carrier bags",
              obligation="Measures ensuring the annual consumption level does not exceed 40 lightweight plastic carrier bags per person by 31 December 2025, or an equivalent target set in weight.",
              source_text="the adoption of measures ensuring that the annual consumption level does not exceed 90 lightweight plastic carrier bags per person by 31 December 2019 and 40 lightweight plastic carrier bags per person by 31 December 2025, or equivalent targets set in weight.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="annual national consumption of lightweight plastic carrier bags",
              obligation="Annual consumption not to exceed 40 lightweight plastic carrier bags per capita, or the equivalent target in weight."),
          affected_delta="THE NUMBER DOES NOT MOVE. 40 per capita is 94/62/EC Art. 4(1a)(a) unchanged, and has bound since 2015. This row exists so the level can be recorded as carried over while BAG-01 records what actually changed around it.")),

    # ===========================  Ch. VII  conformity (Arts. 35-39)
    ("CNF-01", "tests, measurements and calculations shall be made using reliable, accurate and reproducible methods which take into account the generally recognised state-of-the art methods and whose results are considered to be of low uncertainty.", "",
     dict(measure_type="obligation", direction="add",
          duty="Demonstrate compliance with Arts. 5 to 12, 24 and 26 using reliable, accurate and reproducible test, measurement and calculation methods reflecting the state of the art, with results of low uncertainty.",
          addressee="Economic operators demonstrating conformity",
          cls=B, trigger="testing, measuring or calculating for conformity",
          frequency="per assessment", verification="self-assessment or accredited conformity assessment body",
          article="Art. 35", when=WHEN_GENERAL,
          drivers=["D2", "D4"], named=CONVERTERS, reached=FILLERS + ["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All operators demonstrating conformity. The standard is qualitative until harmonised standards exist under Art. 36 or common specifications under Art. 37.")),

    ("CNF-02", "Packaging which is in conformity with harmonised standards or parts thereof, the references of which have been published in the Official Journal of the European Union, shall be presumed to be in conformity with the requirements laid down in or pursuant to Articles 5 to 12, 24 and 26 covered by those standards or parts thereof.", "",
     dict(measure_type="obligation", direction="rem",
          duty="No longer required to prove conformity from first principles where a harmonised standard covers the requirement: conformity is presumed, and Art. 37 adds a Commission common-specification fallback where no standard exists or the standard is inadequate.",
          addressee="Economic operators demonstrating conformity of packaging",
          cls=B, trigger="packaging conforming to a harmonised standard, a part of one, or a common specification",
          frequency="per assessment", verification="self-assessment",
          article="Arts. 36(1)-(3) and 37", when=WHEN_GENERAL,
          drivers=[], named=CONVERTERS, reached=FILLERS + ["waste"],
          provision_id="ppwr-presumption-of-conformity",
          nature="reduction", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="packaging complying with relevant harmonised standards, or with national standards where no harmonised standard existed",
              obligation="Member States presumed compliance with the essential requirements in Annex II for packaging complying with relevant harmonised standards published in the Official Journal, or with notified national standards in areas where no harmonised standard existed.",
              source_text="Member States shall, from the date set out in Article 22 (1), presume compliance with all essential requirements set out in this Directive including Annex II in the case of packaging which complies:",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging conforming to a harmonised standard or a Commission common specification",
              obligation="Conformity is presumed against the whole of Arts. 5 to 12, 24 and 26 -- a far wider requirement set than the old Annex II essential requirements -- and Art. 36(2) additionally presumes conformity for methods performed by accredited conformity assessment bodies. Where no harmonised standard exists or an existing one is inadequate, Art. 37 lets the Commission adopt common specifications that carry the same presumption."),
          affected_delta="All packaging manufacturers. The presumption now covers substances, recyclability, recycled content, compostability, minimisation, reusability, labelling, empty space and re-use systems, where before it covered only the Annex II essential requirements. The common-specification fallback is new: under the directive, an absent standard simply left the operator to prove compliance itself.",
          note="This provision is genuinely mixed, so it is carried as TWO linked measures rather than one averaged row. This is the Simplification limb -- broader presumption plus a fallback where standardisation fails. CNF-03 is the narrowing limb. The split is clean because the two move in opposite directions on different populations and each has its own prior state in 94/62/EC Art. 9(2).")),

    ("CNF-03", "Test, measurement or calculation methods referred to in Article 35 which are in conformity with harmonised standards or parts thereof, the references of which have been published in the Official Journal of the European Union, shall be presumed to be in conformity with the requirements covered by those standards or parts thereof set out in that Article.", "",
     dict(measure_type="obligation", direction="add",
          duty="Prove conformity without relying on a national standard: the route by which a notified national standard conferred a presumption of conformity where no harmonised standard existed is not carried over.",
          addressee="Economic operators in Member States that had notified national packaging standards",
          cls=B, trigger="a requirement covered by a national standard but by no harmonised standard or common specification",
          frequency="per assessment", verification="self-assessment",
          article="Art. 36(1), by omission of the 94/62/EC Art. 9(2)(b) route", when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=CONVERTERS, reached=FILLERS,
          provision_id="ppwr-presumption-of-conformity",
          nature="reduction", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="packaging complying with a notified national standard in an area where no harmonised standard existed",
              obligation="Compliance with a relevant national standard, communicated to the Commission and published in the Official Journal, conferred a presumption of conformity with the essential requirements wherever no harmonised standard covered the area.",
              source_text="with the relevant national standards referred to in paragraph 3 in so far as, in the areas covered by such standards, no harmonized standards exist.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="a requirement covered by no harmonised standard and no common specification",
              obligation="No presumption is available. The operator demonstrates conformity directly under Art. 35, using state-of-the-art methods of low uncertainty."),
          affected_delta="Operators in Member States with an established national packaging standards estate, who lose a compliance route they had under the directive. The Art. 37 common-specification power is the intended replacement, but it is a Commission power rather than an operator's entitlement and nothing obliges the Commission to exercise it.",
          note="The narrowing limb of the Art. 36/37 split; CNF-02 is the Simplification limb. A route that is NOT carried over has no sentence of its own in the new act, so source_text anchors on Art. 36(1) -- which lists the presumption routes that do survive, and is therefore where the omission is visible. The before-state is carried by a resolved, sourced prior_rule quoted from the directive, which is exactly the shape the deletion guardrail demands.")),

    ("CNF-04", "Conformity assessment of packaging as regards the requirements laid down in or pursuant to Articles 5 to 12 shall be carried out in accordance with the procedure set out in Annex VII.", "",
     dict(measure_type="obligation", direction="add",
          duty="Run the Annex VII internal production control conformity assessment procedure for the Arts. 5 to 12 requirements.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="conformity assessment of packaging",
          frequency="per packaging type", verification="self-assessment against Annex VII",
          article="Art. 38", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D5"], named=CONVERTERS, reached=FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All packaging manufacturers. New in kind: packaging had no conformity assessment procedure under 94/62/EC.")),

    ("CNF-05", "The EU declaration of conformity shall state that the fulfilment of the requirements laid down in or pursuant to Articles 5 to 12 has been demonstrated.", "",
     dict(measure_type="obligation", direction="add",
          duty="Draw up, continuously update and keep the EU declaration of conformity in the Annex VIII model, translated as the Member State of marketing requires, and assume responsibility for the packaging's compliance by drawing it up.",
          addressee="Manufacturers of packaging",
          cls=B, trigger="packaging placed on the market",
          frequency="per packaging type, continuously updated",
          verification="competent authority risk-based checks under Art. 39(5)",
          article="Art. 39", when=WHEN_GENERAL,
          drivers=["D1", "D5", "D6"], named=CONVERTERS, reached=FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="All packaging manufacturers. Where packaging or the packaged product falls under several Union acts requiring a declaration, a single combined declaration may be drawn up.")),

    # ===================  Ch. VIII  authorities, prevention, EPR (Arts. 40-47)
    ("AUT-01", "Member States shall designate one or more competent authorities to be responsible for implementation and enforcement of the obligations set out in this Chapter and in Article 6(10), Article 29(1) to (7) and (9) and Articles 30 to34.", "",
     dict(measure_type="obligation", direction="add",
          duty="Designate competent authorities for this Chapter and for Arts. 6(10), 29(1)-(7) and (9) and 30 to 34, lay down their organisation and the administrative and procedural rules for registration, reporting oversight, EPR supervision, EPR authorisation and information, and notify the Commission by 12 July 2025.",
          addressee="Member States",
          cls=S, trigger="implementation of this Regulation",
          frequency="once, then on change", verification="none",
          article="Art. 40", when="Notification by 12 July 2025 (Art. 40(3))",
          drivers=["D1"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States, and the earliest deadline in the act -- 12 July 2025, before the Regulation generally applies.")),

    ("AUT-02", "Member States shall include in the waste management plans required pursuant to Article 28 of Directive 2008/98/EC a dedicated chapter on the management of packaging and packaging waste", "a dedicated chapter on the prevention of packaging, packaging waste and packaging discarded as litter, including measures taken pursuant to Articles 43 and 51 of this Regulation.",
     dict(measure_type="obligation", direction="add",
          duty="Add a dedicated packaging chapter to the Directive 2008/98/EC waste management plan covering Arts. 48, 50 and 52 measures, and a dedicated packaging chapter to the waste prevention programme covering Arts. 43 and 51 measures and litter.",
          addressee="Member States",
          cls=S, trigger="waste management plans and waste prevention programmes under Directive 2008/98/EC",
          frequency="per plan revision", verification="none",
          article="Art. 42", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States, folded into planning machinery that already exists under the Waste Framework Directive.")),

    ("PRV-01", "Each Member State shall reduce the packaging waste generated per capita, as compared to the packaging waste generated per capita in 2018 as reported to the Commission in accordance with Decision 2005/270/EC, by at least:", "15 % by 2040.",
     dict(measure_type="obligation", direction="add",
          duty="Reduce packaging waste generated per capita against a 2018 baseline by at least 5% by 2030, 10% by 2035 and 15% by 2040, and endeavour to reduce plastic packaging waste specifically.",
          addressee="Member States",
          cls=S, trigger="national packaging waste generated per capita",
          frequency="continuous, measured against 2030, 2035 and 2040",
          verification="reporting to the Commission under Art. 56",
          article="Art. 43(1) and (4)", when="2030, 2035 and 2040 (Art. 43(1))",
          drivers=["D4", "D5"], named=["waste"], reached=MATERIALS + FILLERS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=None,
          affected_delta="All 27 Member States, and the first absolute waste-reduction target in EU packaging law. 94/62/EC Art. 4 required only that preventive measures be implemented, with no quantified reduction. Art. 43(8) let a Member State request a base year other than 2018 by 31 December 2025 on evidence of a reporting-driven distortion.",
          pending="The tourism correction factor, which materially changes the target for high-tourism Member States, is set by implementing act due 12 February 2027 (Art. 43(2)).")),

    ("REG-01", "Producers shall be obliged to register in the register referred to in paragraph 1 of this Article in each Member State where they make packaging or packaged products available on the territory of the Member State for the first time", "",
     dict(measure_type="obligation", direction="add",
          duty="Register in the national producer register of every Member State where you first make packaging or packaged products available, or where you unpack packaged products without being an end user, supplying the Annex IX Part A information; do not make packaging available at all until registered.",
          addressee="Producers of packaging and packaged products",
          cls=B, trigger="first making packaging or packaged products available in a Member State, or unpacking without being an end user",
          frequency="per Member State, then on change", verification="competent authority, within 12 weeks",
          article="Art. 44(2), (4) and (5)", when="18 months after the first Art. 44(14) implementing act (Art. 44(1))",
          drivers=["D1", "D3", "D7"], named=CONVERTERS + FILLERS, reached=["waste", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="No exemption from registration by size. The 10-tonne threshold in Art. 44(8) reduces what must be REPORTED, not whether registration is required -- see REG-02.",
          prior_rule=None,
          affected_delta="Every producer selling packaged goods into more than one Member State faces up to 27 separate registrations. Genuinely new at Union level: 94/62/EC had no producer register, only the Art. 7(2) requirement that EPR schemes exist by end-2024. Art. 44(11)(d) lets competent authorities charge cost-based registration fees.")),

    ("REG-02", "shall submit the information set out in Part B, point 1, of Annex IX to the competent authority responsible for the register, by 1 June for each full preceding calendar year.", "",
     dict(measure_type="obligation", direction="add",
          duty="Report the Annex IX Part B information to the register by 1 June each year for the preceding calendar year, with a lighter Part B point 2 return for producers under 10 tonnes; submit quarterly instead where the Member State requires it for budgetary reasons, and notify changes and cessation without undue delay.",
          addressee="Producers, their authorised representatives, or their producer responsibility organisation",
          cls=B, trigger="the close of a calendar year in which packaging was made available",
          frequency="annual by 1 June, quarterly where required",
          verification="competent authority; Member States may require independent audit and certification",
          article="Art. 44(7) to (9) and (12)", when="Following registration under Art. 44(1)",
          drivers=["D1", "D4", "D5"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS,
          size_scope_note="Art. 44(8) gives a producer that made available under 10 tonnes in a calendar year a lighter Annex IX Part B point 2 return instead of the full point 1 return. A Member State may set a LOWER threshold where it would otherwise lack data. An eligibility carve-out on the reporting duty, not a separate benefit.",
          affected_delta="Every registered producer. Member States may require the figures to be audited and certified by independent auditors, which turns an annual return into an assurance engagement.")),

    ("EPR-01", "Producers shall have extended producer responsibility under the schemes established in accordance with Articles 8 and 8a of Directive 2008/98/EC and with this Section for the packaging, including packaging of packaged products, that they make available for the first time on the territory of a Member State or that they unpack without being end users.", "",
     dict(measure_type="obligation", direction="add",
          duty="Carry extended producer responsibility for all packaging first made available or unpacked in a Member State, with financial contributions additionally covering the cost of labelling waste receptacles under Art. 13 and of compositional surveys of mixed municipal waste.",
          addressee="Producers of packaging and packaged products",
          cls=B, trigger="packaging first made available in a Member State, or unpacked without being an end user",
          frequency="continuous", verification="producer responsibility organisation and competent authority",
          article="Art. 45(1) and (2)", when=WHEN_GENERAL,
          drivers=["D5", "D6"], named=CONVERTERS + FILLERS, reached=["waste", "horeca"],
          nature="extension", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          prior_rule=dict(
              trigger="all packaging placed on the national market",
              obligation="Member States had to ensure that extended producer responsibility schemes were established for all packaging by 31 December 2024, in accordance with Arts. 8 and 8a of Directive 2008/98/EC.",
              source_text="Member States shall ensure that, by 31 December of 2024, extended producer responsibility schemes are established for all packaging in accordance with Articles 8 and 8a of Directive 2008/98/EC.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging first made available in a Member State, or unpacked without being an end user",
              obligation="EPR is imposed directly on the producer by the Regulation rather than through a Member State duty to set up a scheme, and the cost base is widened to include receptacle labelling and mixed-municipal-waste compositional surveys."),
          affected_delta="EPR itself is not new -- it has been required since 31 December 2024 under 94/62/EC Art. 7(2). What moves is the addressee, now the producer directly, and the cost base, which grows by two new categories.")),

    ("EPR-02", "providers of online platforms that fall within the scope of Section 4 of Chapter III of that Regulation and that allow consumers to conclude distance contracts with producers shall obtain the following information from producers", "a self-certification by the producer confirming that it only offers packaging with regard to which the extended producer responsibility requirements referred to in paragraphs 1, 2 and3 of this Article are complied with in the Member State where the consumer is located.",
     dict(measure_type="obligation", direction="add",
          duty="Before allowing a producer to use the platform, obtain its Art. 44 registration details and registration number for the consumer's Member State and a self-certification of EPR compliance, and make best efforts to assess whether that information is complete and reliable.",
          addressee="Providers of online platforms allowing distance contracts with producers",
          cls=B, trigger="a producer seeking to offer packaging or packaged products to EU consumers via the platform",
          frequency="per producer onboarding", verification="platform due diligence",
          article="Art. 45(4) and (6)", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D5"], named=["retail"], reached=CONVERTERS + FILLERS + ["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="Scoped to platforms within Section 4 of Chapter III of Regulation (EU) 2022/2065, not by employee or turnover band.",
          affected_delta="Online marketplaces, as the enforcement point for EPR against non-EU and hard-to-reach producers. Free-riding on EPR is largely a distance-selling problem, and this is how the act reaches it.")),

    ("EPR-03", "the fulfilment service provider shall, through the use of any freely accessible official online database or online interface made available by a Member State or the Union", "The fulfilment service provider shall provide the producer with the reasons for the suspension.",
     dict(measure_type="obligation", direction="add",
          duty="Check the producer's registration and EPR self-certification against an official database or the public register, require correction where the information looks inaccurate, incomplete or out of date, and suspend the service until it is corrected, giving reasons.",
          addressee="Fulfilment service providers",
          cls=B, trigger="concluding a contract with a producer offering packaging to EU consumers",
          frequency="per producer contract", verification="fulfilment provider due diligence",
          article="Art. 45(8)", when=WHEN_GENERAL,
          drivers=["D1", "D3", "D5"], named=["retail"], reached=CONVERTERS + FILLERS + ["waste"],
          provision_id="ppwr-art45-fulfilment-suspension",
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Logistics and fulfilment operators, made responsible for policing their customers' EPR compliance and required to cut off service where it fails.")),

    ("EPR-04", "the producer concerned shall have the right to challenge the decision of the fulfilment service provider before a court in a Member State in which the fulfilment service provider is established.", "",
     dict(measure_type="right", direction="add",
          benefit="A producer whose fulfilment service is suspended for an EPR information failure may challenge that decision before a court in the Member State where the fulfilment service provider is established.",
          addressee="Producers whose fulfilment service has been suspended",
          cls=B, trigger="suspension of a fulfilment service under Art. 45(8)",
          frequency="per suspension", verification="national court",
          article="Art. 45(9)", when=WHEN_GENERAL,
          value_drivers=["V1"], frictions=["F3"],
          named=CONVERTERS + FILLERS, reached=["retail"],
          provision_id="ppwr-art45-fulfilment-suspension",
          right_basis=dict(text="the producer concerned shall have the right to challenge the decision of the fulfilment service provider before a court in a Member State in which the fulfilment service provider is established.",
                           kind="existence"),
          nature="new_right", weight="Relief",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Producers dependent on third-party fulfilment. Linked to EPR-03 by provision_id: the same provision creates a private enforcement power and the remedy against it, and neither reading contains the other.",
          note="An express right in the act's own words -- 'shall have the right' -- so the basis object needed no construction. It is the counterweight to a duty the act places on a private party rather than an authority, which is why it exists at all.")),

    ("EPR-05", "The producer, in the case of individual fulfilment of extended producer responsibility obligations, or the producer responsibility organisation entrusted with carrying out those obligations, in the case of collective fulfilment of extended producer responsibility obligations, shall apply for an authorisation on fulfilment of extended producer responsibility from the competent authority.", "",
     dict(measure_type="obligation", direction="add",
          duty="Apply to the competent authority for authorisation to fulfil extended producer responsibility, individually or through a producer responsibility organisation, and notify changes or cessation without undue delay.",
          addressee="Producers fulfilling EPR individually, and producer responsibility organisations",
          cls=B, trigger="fulfilment of extended producer responsibility obligations",
          frequency="once, then on change",
          verification="competent authority or independent expert, within 18 weeks of a complete dossier",
          article="Art. 47(1) and (4)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Producers and PROs in all 27 Member States. The authorisation may be revoked under Art. 47(5), which makes it a licence to trade in packaged goods rather than a formality.")),

    ("EPR-06", "shall provide an adequate guarantee intended to cover the costs related to waste management operations owed by the producer or the producer responsibility organisation, in the event of non-compliance with the extended producer responsibility obligations", "",
     dict(measure_type="obligation", direction="add",
          duty="Provide an adequate financial guarantee covering waste management costs owed in the event of non-compliance, permanent cessation of operations or insolvency.",
          addressee="Producers fulfilling EPR individually, and producer responsibility organisations",
          cls=B, trigger="fulfilment of extended producer responsibility obligations",
          frequency="continuous", verification="competent authority",
          article="Art. 47(6)", when=WHEN_GENERAL,
          drivers=["D6"], named=CONVERTERS + FILLERS, reached=["waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="A balance-sheet duty, not an administrative one: capital or an instrument has to stand behind the EPR obligation. Member States may add requirements, and the guarantee may take the form of a public fund financed by producers' fees.")),

    # ===================  Ch. VIII  collection, deposits, targets (Arts. 48-57)
    ("COL-01", "Member States shall ensure that systems and infrastructures are set up to provide for the return and separate collection of all packaging waste from the end users", "Incineration and landfill of such packaging shall be prohibited, with the exception of waste resulting from subsequent treatment operations of separately collected packaging waste for which recycling is not feasible or does not deliver the best environmental outcome.",
     dict(measure_type="obligation", direction="add",
          duty="Set up return and separate collection covering the whole territory and all packaging waste, open to operators, authorities and third parties and to imported products on non-discriminatory terms; collect design-for-recycling-compliant packaging for recycling and prohibit its incineration and landfill.",
          addressee="Member States",
          cls=S, trigger="packaging waste arising from end users",
          frequency="continuous", verification="reporting to the Commission under Art. 56",
          article="Arts. 48(1) and (5)", when=WHEN_GENERAL,
          drivers=["D4", "D5"], named=["waste"], reached=MATERIALS,
          nature="extension", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="used packaging and packaging waste from consumers and other final users",
              obligation="Member States had to ensure systems were set up for the return and/or collection of used packaging and packaging waste in order to channel it to the most appropriate waste management alternative, and for its reuse or recovery including recycling. Collection did not have to be separate.",
              source_text="the return and/or collection of used packaging and/or packaging waste from the consumer, other final user, or from the waste stream in order to channel it to the most appropriate waste management alternatives;",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="all packaging waste from end users",
              obligation="Return and SEPARATE collection of all packaging waste, covering the whole territory including public spaces, business premises and residential areas, with an outright prohibition on incinerating or landfilling packaging that meets the design-for-recycling criteria."),
          affected_delta="The material change is the landfill and incineration ban on recyclable packaging, which has no equivalent in the directive, plus the shift from 'return and/or collection' to mandatory separate collection. Art. 48(3) allows derogations for formats where co-collection does not damage output quality.")),

    ("COL-02", "Member States shall set mandatory collection objectives and take the necessary measures to ensure that the collection of the materials listed in Article 52 is consistent with the recycling targets set out in that Article and with the mandatory recycled content targets set out in Article 7.", "",
     dict(measure_type="obligation", direction="add",
          duty="Set mandatory national collection objectives for the Art. 52 materials, consistent with the recycling targets and with the Art. 7 recycled-content requirements.",
          addressee="Member States",
          cls=S, trigger="the material streams listed in Art. 52",
          frequency="continuous", verification="reporting to the Commission under Art. 56",
          article="Art. 49", when="By 1 January 2029 (Art. 49)",
          drivers=["D4", "D5"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States. This is the provision that links collection to the recycled-content duty on converters: without enough collected feedstock, Art. 7 cannot be met, and this makes that a Member State obligation rather than a market problem.")),

    ("DRS-01", "Member States shall take the necessary measures to ensure the separate collection of at least 90 % per year by weight of the following packaging formats made available on the market for the first time in that Member State in a given calendar year:", "single-use metal beverage containers with a capacity of up to three litres.",
     dict(measure_type="obligation", direction="add",
          duty="Separately collect at least 90% by weight per year of single-use plastic beverage bottles and single-use metal beverage containers up to three litres.",
          addressee="Member States",
          cls=S, trigger="single-use plastic beverage bottles and metal beverage containers up to three litres",
          frequency="annual", verification="reporting to the Commission under Art. 56(1)(c)",
          article="Art. 50(1)", when="By 1 January 2029 (Art. 50(1))",
          drivers=["D4", "D5"], named=["waste"], reached=["chem/plastics", "alu", "steel", "foodbev", "retail"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=None,
          affected_delta="All 27 Member States. Genuinely new in PPWR terms -- 94/62/EC set no format-specific collection rate. The 90% figure matches the Single-Use Plastics Directive's bottle target but extends it to metal beverage containers, which is the new reach.")),

    ("DRS-02", "Member States shall take the necessary measures to ensure that deposit and return systems are set up for the relevant packaging formats referred to in paragraph 1 and that a deposit is charged at the point of sale.", "",
     dict(measure_type="obligation", direction="add",
          duty="Set up deposit and return systems for single-use plastic beverage bottles and metal beverage containers, with a deposit charged at the point of sale, meeting the Annex X minimum requirements.",
          addressee="Member States",
          cls=S, trigger="the packaging formats in Art. 50(1)",
          frequency="continuous", verification="reporting to the Commission under Art. 56(1)(c)",
          article="Art. 50(2) and (11)", when="By 1 January 2029 (Art. 50(1) and (11))",
          drivers=["D4", "D5", "D6"], named=["waste", "retail"],
          reached=["chem/plastics", "alu", "steel", "foodbev", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size, though the retail take-back it forces reaches every point of sale.",
          affected_delta="Member States without a DRS today face building national return infrastructure, and retail carries the return points. Art. 50(5) exempts a Member State that already reached 80% separate collection of the format in 2026 and notifies an implementation plan by 1 January 2028 -- but Art. 50(7) withdraws the exemption if the rate stays below 90% for three consecutive years.",
          note="Art. 50(3) lets Member States exempt HORECA from charging the deposit where the packaging is opened, consumed and returned on the premises. Art. 50(4) excludes wine and grapevine products, aromatised wine, similar fermented fruit and vegetable drinks, spirits, and milk and milk products. Both are eligibility carve-outs on this duty.")),

    ("DRS-03", "Member States shall ensure that return points and opportunities for reusable packaging with a similar purpose and format to those established under paragraph 1 are as convenient for end users as return points and opportunities are to return single-use packaging to a deposit and return system.", "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure return points for reusable packaging are as convenient for end users as the return points for single-use packaging in a deposit and return system.",
          addressee="Member States",
          cls=S, trigger="reusable packaging of similar purpose and format to DRS single-use formats",
          frequency="continuous", verification="none",
          article="Art. 50(10)", when="By 1 January 2029 (Art. 50(1))",
          drivers=["D4"], named=["waste", "retail"], reached=["glass", "foodbev"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="Stops a well-run single-use DRS from making single-use more convenient than re-use -- the perverse outcome the re-use targets would otherwise run into.")),

    ("RRF-01", "Member States shall take measures to encourage the establishment of re-use systems for packaging with sufficient incentives for return and of refill systems in an environmentally sound manner.", "Those systems shall comply with the requirements laid down in Articles 27 and 28 and Annex VI and shall not compromise food hygiene or the safety of consumers.",
     dict(measure_type="obligation", direction="add",
          duty="Take measures encouraging re-use and refill systems that comply with Arts. 27 and 28 and Annex VI without compromising food hygiene or consumer safety, and ensure EPR schemes and deposit and return systems allocate a minimum share of their budget to reduction and prevention.",
          addressee="Member States",
          cls=S, trigger="national re-use and refill systems",
          frequency="continuous", verification="none",
          article="Art. 51(1) and (3)", when=WHEN_GENERAL,
          drivers=["D4"], named=["waste"], reached=FILLERS + ["horeca", "glass", "chem/plastics"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States. The budget-allocation limb in Art. 51(3) is the operative one: it directs EPR and DRS money towards prevention rather than only towards collection.",
          note="Art. 51(2)'s menu of measures -- deposit systems, economic incentives, single-use charges, obligations to sell a percentage in reusable packaging -- was REJECTED as a benefit row. It is a list of things a Member State MAY do; nothing is conferred on anyone until one is chosen.")),

    ("RCT-01", "Member States shall take the necessary measures to achieve the following recycling targets covering the whole of their territory:", "85 % of paper and cardboard.",
     dict(measure_type="obligation", direction="unchanged",
          duty="Achieve recycling of at least 65% of all packaging waste by weight by 31 December 2025 and 70% by 31 December 2030, with material lines of 50/55% plastic, 25/30% wood, 70/80% ferrous metals, 50/60% aluminium, 70/75% glass and 75/85% paper and cardboard.",
          addressee="Member States",
          cls=S, trigger="packaging waste generated on the national territory",
          frequency="continuous, measured at 2025 and 2030",
          verification="reporting to the Commission under Art. 56(1)(a)",
          article="Art. 52(1)", when="31 December 2025 and 31 December 2030 (Art. 52(1))",
          drivers=["D4", "D5"], named=["waste"], reached=MATERIALS,
          nature="carry_over", weight="Neutral",
          reclass_from=dict(direction="add",
              note="Filed as 'add' in the single-pass extraction because the direction enum had only add|rem, which forced the register's most-quoted carry-over to render Requirement. Every figure is identical to 94/62/EC Art. 6(1)(f)-(i) as amended, so the row now takes `unchanged` and renders Neutral."),
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="packaging waste generated on the national territory",
              obligation="Identical targets: 65% of all packaging waste recycled by 31 December 2025 and 70% by 31 December 2030, with the same six material lines at the same percentages -- plastic 50/55, wood 25/30, ferrous metals 70/80, aluminium 50/60, glass 70/75, paper and cardboard 75/85.",
              source_text="no later than 31 December 2025 a minimum of 65 % by weight of all packaging waste will be recycled;",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="packaging waste generated on the national territory",
              obligation="65% by 31 December 2025 and 70% by 31 December 2030, with the same six material lines at the same percentages."),
          affected_delta="NOTHING MOVES. Every figure in Art. 52(1) is identical to 94/62/EC Art. 6(1)(f) to (i) as amended by Directive (EU) 2018/852: 65/70 overall, plastic 50/55, wood 25/30, ferrous 70/80, aluminium 50/60, glass 70/75, paper and cardboard 75/85. Anything presenting PPWR as raising the recycling targets is wrong. The postponement mechanism in Art. 52(2) is likewise carried over from Art. 6(1a).",
          note="Carried as a row because the duty is live under this act and Member States comply with it under this act, not under a repealed directive. The delta model is what prevents it reading as a new burden. See the file docstring on why it cannot be RENDERED neutral.")),

    ("RCT-02", "Member States shall calculate the weight of packaging waste generated in a given calendar year.", "",
     dict(measure_type="obligation", direction="add",
          duty="Calculate packaging waste generated and packaging waste recycled each calendar year on the Art. 53 rules, exhaustively, adjusted for comparability, reliability and completeness under the Art. 56(7) implementing act.",
          addressee="Member States",
          cls=S, trigger="each calendar year of packaging waste",
          frequency="annual", verification="reporting to the Commission under Art. 56",
          article="Art. 53", when=WHEN_GENERAL,
          drivers=["D1", "D4", "D5"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States. The calculation point rules decide whether a target is met, so this is where the recycling targets are really enforced.")),

    ("RCT-03", "A Member State may decide to achieve an adjusted level of the targets set out in Article 52(1) for a given year by taking into account the average share, in the preceding 3 years, of reusable sales packaging placed on the market for the first time and re-used within a re-use system.", "",
     dict(measure_type="obligation", direction="add",
          duty="Where an adjusted recycling target is claimed for re-use, calculate it by subtracting the three-year average share of reusable sales packaging, capped at five percentage points, and account separately for wooden packaging repaired for re-use.",
          addressee="Member States claiming a re-use adjustment",
          cls=S, trigger="a decision to achieve an adjusted target level",
          frequency="annual", verification="reporting to the Commission under Art. 56",
          article="Art. 54", when=WHEN_GENERAL,
          drivers=["D4"], named=["waste"], reached=["wood", "glass", "chem/plastics"],
          nature="reduction", weight="Relief",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="a decision to achieve an adjusted target level for reusable sales packaging",
              obligation="The same adjustment existed, on the same three-year average and the same five-percentage-point cap, against the targets in Art. 6(1)(f) to (i).",
              source_text="No more than five percentage points of such share shall be taken into account for the calculation of the respective adjusted target level.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="a decision to achieve an adjusted target level for reusable sales packaging",
              obligation="Unchanged in substance: three-year average share of reusable sales packaging subtracted from the Art. 52(1) targets, capped at five percentage points, with a separate limb for wooden packaging repaired for re-use."),
          affected_delta="Carried over from 94/62/EC Art. 6a with no change of substance. Recorded because it is the mechanism by which a Member State's headline recycling obligation can legitimately fall.")),

    ("INF-01", "shall make available to end users, in particular consumers, the following information regarding the prevention and management of packaging waste with respect to the packaging that the producers supply on the territory of a Member State:", "",
     dict(measure_type="obligation", direction="add",
          duty="Make available to end users information on their role in waste prevention, the re-use arrangements available, their role in separate collection including for packaging containing hazardous products, the meaning of on-pack labels and symbols, and the impact of littering and of discarding packaging in mixed municipal waste.",
          addressee="Producers, producer responsibility organisations, or appointed public authorities",
          cls=B, trigger="packaging supplied on the territory of a Member State",
          frequency="continuous", verification="competent authority",
          article="Art. 55", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=CONVERTERS + FILLERS, reached=["retail", "waste"],
          nature="new_obligation", weight="Burden",
          size_scope=ALL_BANDS, size_scope_note="No size threshold.",
          affected_delta="Producers, on top of the Art. 8a(2) Waste Framework Directive information duty and the Art. 12 labelling duty. A consumer-communication obligation distinct from what goes on the pack.")),

    ("INF-02", "Article 56 Reporting to the Commission 1. Member States shall submit the following data to the Commission for each calendar year:", "the annual consumption of very lightweight plastic carrier bags, lightweight plastic carrier bags, thick plastic carrier bags and very thick plastic carrier bags per capita, separately for each category as listed in Table 4 of Annex XII;",
     dict(measure_type="obligation", direction="add",
          duty="Report to the Commission each calendar year on recycling target implementation and reusable packaging, per-capita consumption of each carrier-bag category, the DRS separate collection rate, and the quantities of packaging made available, collected and recycled by category.",
          addressee="Member States",
          cls=S, trigger="the close of a calendar year",
          frequency="annual", verification="Commission review",
          article="Art. 56(1) and (2)", when=WHEN_GENERAL,
          drivers=["D1", "D4", "D5"], named=["waste"], reached=MATERIALS + ["retail"],
          nature="extension", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          prior_rule=dict(
              trigger="each calendar year",
              obligation="Member States reported data on packaging and packaging waste to the Commission, including annual lightweight plastic carrier bag consumption from 27 May 2018.",
              source_text="From 27 May 2018 Member States shall report on the annual consumption of lightweight plastic carrier bags when providing data on packaging and packaging waste to the Commission in accordance with Article 12.",
              status="sourced", source_document=PRIOR_DOC),
          new_rule=dict(
              trigger="each calendar year",
              obligation="Reporting extended to four separate carrier-bag categories rather than one, to the DRS separate collection rate, to reusable packaging data, and to packaging made available, collected and recycled per Annex XII category."),
          affected_delta="Reporting existed under 94/62/EC Art. 12; its granularity roughly triples. The carrier-bag return alone goes from one figure to four.")),

    ("INF-03", "Member States shall take the necessary measures to ensure that databases on packaging and packaging waste are established, where not already in place, on a harmonised basis", "",
     dict(measure_type="obligation", direction="add",
          duty="Establish harmonised packaging and packaging waste databases carrying the Annex XII data and information on flows, made publicly accessible in a machine-readable, interoperable and re-usable format.",
          addressee="Member States",
          cls=S, trigger="the reporting obligations in Art. 56",
          frequency="continuous", verification="none",
          article="Art. 57", when="12 months after the Art. 56(7) implementing acts (Art. 57(1))",
          drivers=["D1", "D4"], named=["waste"], reached=MATERIALS,
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States. The public-accessibility requirement is what makes the packaging data auditable from outside the Member State reporting it.")),

    # ===================  Ch. IX-XII  surveillance, procurement, penalties
    ("MSV-01", "Member States shall lay down the rules on penalties applicable to infringements of this Regulation and shall take all measures necessary to ensure that they are implemented.", "",
     dict(measure_type="obligation", direction="add",
          duty="Lay down effective, proportionate and dissuasive penalties for infringements, including administrative fines for breaches of Arts. 24 to 29, and notify the Commission of the rules and of any later amendment.",
          addressee="Member States",
          cls=S, trigger="infringement of this Regulation",
          frequency="once, then on amendment", verification="none",
          article="Art. 68", when="By 12 February 2027 (Art. 68(1) and (3))",
          drivers=["D6"], named=["waste"], reached=CONVERTERS + FILLERS + ["retail", "horeca"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States, and through them every operator. Note which duties carry MANDATORY administrative fines under Art. 68(2): Arts. 24 to 29 -- excessive packaging, format bans, re-use systems, refill and the re-use targets. That is the act's enforcement priority stated in its own structure.")),

    ("MSV-02", "where the market surveillance authorities of a Member State have sufficient reason to believe that packaging covered by this Regulation presents a risk to the environment or human health", "",
     dict(measure_type="obligation", direction="add",
          duty="Where there is sufficient reason to believe packaging presents a risk to the environment or human health, evaluate it against all relevant requirements, require the operator to take corrective action, and where the operator does not act, prohibit or restrict the packaging or withdraw or recall it.",
          addressee="Member State market surveillance authorities",
          cls=S, trigger="sufficient reason to believe packaging presents a risk",
          frequency="per case", verification="market surveillance authority",
          article="Arts. 58 to 60", when=WHEN_GENERAL,
          drivers=["D3", "D6"], named=["waste"], reached=CONVERTERS + FILLERS + ["retail"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="All 27 Member States, with the Union safeguard procedure in Art. 59 escalating a contested national measure to the Commission. For operators, the practical exposure is withdrawal or recall, which is new for packaging.")),

    ("MSV-03", "Market surveillance authorities shall, without delay, communicate to the authorities designated pursuant to Article 25(1) of Regulation (EU) 2019/1020 the measures referred to in Article 58(5) of this Regulation where the non-compliance is not restricted to their territory.", "",
     dict(measure_type="obligation", direction="add",
          duty="Communicate national non-compliance measures without delay to the Art. 25(1) authorities under Regulation (EU) 2019/1020 so they feed the border risk analysis, and act on formal non-compliance under Art. 62.",
          addressee="Member State market surveillance and designated border authorities",
          cls=S, trigger="a national measure against non-compliant packaging whose effect is not restricted to one territory",
          frequency="per case", verification="market surveillance authority",
          article="Arts. 61 and 62", when=WHEN_GENERAL,
          drivers=["D3"], named=["waste"], reached=CONVERTERS + FILLERS + ["retail"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a Member State, not a company by size.",
          affected_delta="Border authorities in all 27 Member States, and importers of packaged goods, who now face release being suspended for a packaging documentation failure. This is the limb PPWR's Art. 66 amendment to Regulation (EU) 2019/1020 switches on by adding the act to its Annex I.")),

    ("GPP-01", "the Commission shall, by 12 February 2030, adopt implementing acts specifying minimum mandatory requirements for public contracts", "",
     dict(measure_type="obligation", direction="add",
          duty="Apply the Commission's minimum mandatory green public procurement requirements when awarding contracts where packaging or packaged products represent more than 30% of the estimated contract value or of the value of products used by the contracted services.",
          addressee="Contracting authorities and contracting entities under Directives 2014/24/EU and 2014/25/EU",
          cls=S, trigger="a public contract where packaging exceeds 30% of the estimated value",
          frequency="per procurement", verification="procurement procedure",
          article="Art. 63", when="Implementing acts by 12 February 2030, applying to procedures started 12 months later (Art. 63(1) and (2))",
          drivers=["D1", "D3"], named=["waste"], reached=CONVERTERS + FILLERS + ["retail"],
          nature="new_obligation", weight="Burden",
          size_scope=NO_BANDS, size_scope_note="Binds a contracting authority, not a company by size.",
          affected_delta="Public buyers across the Union, and through them their packaging suppliers, for whom the requirements become a condition of bidding. Contracting authorities may derogate in duly justified cases on public security or public health grounds, or for unresolvable technical difficulties.",
          note="REJECTED as a benefit row. Art. 63(1) opens 'In order to incentivise the supply and demand for environmentally sustainable packaging', which is exactly the rhetorical opportunity language the basis gate exists to catch. The operative content is a Commission rulemaking duty and a condition on contracting authorities: no amount, rate, eligibility or existence is conferred on any supplier.")),
]


def slice_span(text: str, start: str, end: str, rid: str) -> str:
    """The span for one row, sliced out of the act rather than retyped.

    Both anchors must be unique. An ambiguous START is a hard failure and not a
    "take the first match", because the first match is only the right one by
    luck and nothing downstream would ever notice the difference.
    """
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
    prior = canonical((HERE / PRIOR_94_62).read_text(encoding="utf-8"))

    rows, errors = [], []
    seen_ids: set[str] = set()

    for rid, start, end, meta in ROWS:
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate id -- ids are permanent and unique")
            continue
        seen_ids.add(rid)

        try:
            span = slice_span(act, start, end, rid)
        except LookupError as exc:
            errors.append(str(exc))
            continue

        row = {"id": rid, "measure_type": meta["measure_type"]}
        if meta["measure_type"] in DUTY_SIDE_TYPES:
            row["duty"] = meta["duty"]
        else:
            row["benefit"] = meta["benefit"]

        row.update({
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
            "provision_id": meta.get("provision_id"),
            "file": FILE_KEY,
            "source_url": SOURCE_URL,
            "value_drivers": meta.get("value_drivers", []),
            "access_frictions": meta.get("frictions", []),
        })

        # The diff model. Only omnibus carried these before; the brief asks for
        # them here, and the carry-over rows are unreadable without them.
        for key in ("nature", "affected_delta", "weight", "size_scope",
                    "size_scope_note", "new_rule"):
            if meta.get(key) is not None:
                row[key] = meta[key]
        if "prior_rule" in meta:
            row["prior_rule"] = meta["prior_rule"]

        if meta.get("pending"):
            row["pending"] = meta["pending"]
        if meta.get("note"):
            row["benefit_axis_note"] = meta["note"]
        if meta.get("right_basis"):
            row["right_basis"] = meta["right_basis"]
        if meta.get("opportunity_basis"):
            row["opportunity_basis"] = meta["opportunity_basis"]
        if meta.get("support_cut_basis"):
            row["support_cut_basis"] = meta["support_cut_basis"]
        # Review flags. `q` is a question this pass could not close, not a note.
        if meta.get("q"):
            row["q"] = meta["q"]
        # Provenance for a classification that MOVED after first publication.
        # The id does not change -- ids are permanent -- so this is the only
        # record that the row used to say something else.
        if meta.get("reclass_from"):
            row["reclass_from"] = meta["reclass_from"]

        # A prior_rule that claims to be sourced has to actually be in the
        # prior corpus. Checking it here rather than trusting the author is the
        # whole point of the deletion guardrail, applied one step earlier.
        pr = row.get("prior_rule")
        if isinstance(pr, dict) and pr.get("source_text"):
            if canonical(pr["source_text"]) not in prior:
                errors.append(
                    f"{rid}: prior_rule.source_text is not verbatim in {PRIOR_94_62}: "
                    f"{pr['source_text'][:70]!r}")

        rows.append(row)

    return rows, errors


def main() -> int:
    write = "--check" not in sys.argv
    rows, errors = build()

    if errors:
        print(f"FAILURES ({len(errors)}) — nothing written:")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"ppwr: {len(rows)} rows  [SINGLE-PASS, NOT RECONCILED]")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")
    flags = Counter(r["q"] for r in rows if r.get("q"))
    if flags:
        print(f"  review flags: {dict(flags)}")
    named = Counter(s for r in rows for s in r["sectors_named"])
    print(f"  sectors named:   {dict(named)}")
    reached = Counter(s for r in rows for s in r["sectors_reached"])
    print(f"  sectors reached: {dict(reached)}")

    if write:
        (DATA / "ppwr.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written ../data/ppwr.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

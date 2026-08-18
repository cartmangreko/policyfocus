"""
Extract the Net-Zero Industry Act -- Regulation (EU) 2024/1735, consolidated at
17 August 2025 (CELEX 02024R1735-20250817) -- into data/nzia.json.

    python3 extract_nzia.py --check     # report, write nothing
    python3 extract_nzia.py             # write ../data/nzia.json

Anchor-based, in the extract_cbam.py idiom: every source_text is SLICED out of
sources/nzia.txt by a start/end anchor rather than retyped, so a span cannot
drift from the act by a stray character. A missing or ambiguous anchor is a hard
failure and nothing is written.

WHAT IS DIFFERENT ABOUT THIS FILE
=================================
Every register file until now has been an AMENDING instrument -- a proposal that
moves an existing rule. This one is a standing act read at its current
consolidation, which changes three things:

  * `direction` is "add" almost everywhere. Not because the reading was lazy:
    a standing act states duties, it does not remove them. The four "rem" rows
    are provisions that switch a duty OFF for a named class (Art. 6(5) no
    duplicate studies, Art. 23(7)-(8) the injection-capacity exemption,
    Art. 25(9)-(10) the procurement escape hatches), which is the obligation
    side, direction rem -- Simplification -- on the object rule.

  * There is no prior_rule anywhere. prior_rule exists so a deletion has a
    legible before-state; nothing here deletes anything. PRIOR_SOURCES has no
    nzia entry for the same reason.

  * `when` mostly resolves to Article 49, which is unusually specific: the act
    applies from 29 June 2024, EXCEPT that Art. 25(1) is confined to central
    purchasing bodies and EUR 25 million contracts until 30 June 2026, and
    Arts. 26 and 28 apply only from 30 December 2025. Those three carve-outs
    are the WHEN_* constants below and the rows that need them say so.

THE BENEFIT AXIS HERE
=====================
NZIA is the act the Industrial Accelerator Act amends, and it is read on the
same rule -- measure_type follows the OBJECT the provision acts on.

  * Permit-granting time limits (Arts. 9, 16) are duties on the AUTHORITY, not
    conferrals on the promoter: obligation / state / add. That is the reading
    IAA PRM-02 and PRM-03 already took of the same architecture.
  * Strategic-project status (Arts. 13, 15, 18(4)) IS a conferral -- the
    promoter holds something they did not hold -- so it is `right`, matching
    IAA PRM-04 and IAA-B AA-06 on the identical mechanism. right_basis kind
    "scope" where the status attaches to a class of project, "conferral" where
    a named faculty is handed over, "procedure" where what is conferred is a
    route (appeal to the Commission, splitting a project, joining a scheme).
  * Art. 25(7) and Art. 26 are two-faced and are extracted as PAIRS sharing a
    provision_id, the way IAA's lead-market rows are: the tenderer carries the
    origin cap and the evidence duty (obligation), and the EU or diversified
    producer gets the demand share it creates (incentive, V2). Writing only
    one side of those would misstate the act in opposite directions.
  * Art. 23 -- the individual CO2 injection-capacity contribution on authorised
    oil and gas producers -- is the heaviest obligation in the act: a quantified
    volume, a plan, an annual report, and Member State penalties behind it.

WHAT IS NOT HERE, AND WHY
=========================
Purely institutional plumbing: the SET Plan Steering Group (Arts. 35-37), the
Platform's own structure (Arts. 38-40), comitology and delegation (Arts. 43-45),
and the Commission's evaluation duties (Arts. 20(3)-(7), 24, 42(6)-(8), 46).
scope.md rules out "purely institutional, budgetary, or procedural acts", and
the same boundary applies inside an act: a body's own composition binds nobody
in a tracked sector. The Academies (Arts. 30-32) are in the act and out of the
register on the same test -- they produce voluntary learning content, and the
one provision there that does bind a Member State (Art. 31(1), identify
equivalence and report the reasons if not) is carried as SKL-01.

RECONCILED, AND WHAT THAT COST
==============================
This file was one pass when it was written. extract_nzia_pass_b.py is the second
read -- a paragraph-by-paragraph sweep of Arts. 5 to 48 -- and
reconciliation_gate.py certifies the result. What the second read did:

  * 3 classification disagreements, ALL HELD FOR THIS FILE. Each was the same
    argument (a provision binding a Member State in order to confer something on
    a firm), and the object rule decides it the way this file already read it.
    Ruled, not merely outlived: nzia_rulings.CLASSIFICATION records all three.
  * 2 application dates WRONG HERE and corrected. Art. 49(3) confines Art. 25(1)
    and nothing else, and this file had applied that carve-out across the whole
    procurement family. PP-03b moved with PP-03a as a consequential ruling.
  * 33 provisions promoted, which is why this file is 89 rows and not 56. The
    promotions are built from the pass rows rather than retyped -- see
    promoted_rows() -- so a promoted row cannot drift from what the second read
    said. Six candidates were rejected with reasons.

The two disagreements that remain live are SPC-02/N-06 and SP-01/N-30, both
ruled for this file. A fresh reconcile.py run will report them for as long as
both files exist; that is a recorded decision, not unfinished work, and the gate
checks that every live disagreement is one of the rulings that held.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "nzia.txt"
FILE_KEY = "nzia"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1735-20250817"

# The consolidated text opens with a banner, the amendment table and the
# corrigenda list before the enacting terms. Nothing is quoted from there, and
# confining the search to the operative part keeps an anchor from landing in the
# banner or the amendment table.
OPERATIVE_ANCHOR = "Article 1 Subject matter"

# Article 49. The general date, and the two carve-outs that displace it.
WHEN_GENERAL = "Applies from 29 June 2024 (Art. 49(2))"
# Art. 49(3) names Art. 25(1) AND NOTHING ELSE. This constant therefore belongs
# only to rows that are about Art. 25(1) -- PP-01, and PP-04 which disapplies
# Art. 25(1) to (4). It was originally applied to the whole procurement family
# by theme, which dated PP-02, PP-03a and PP-03b as if a EUR 25 million floor
# stood in front of them until mid-2026. The second pass caught all three;
# nzia_rulings.DATES and CONSEQUENTIAL_DATES rule on them.
WHEN_PROCUREMENT = ("Applies from 29 June 2024; until 30 June 2026 Art. 25(1) reaches only "
                    "central purchasing bodies and contracts of EUR 25 million or more (Art. 49(3))")
WHEN_AUCTIONS = "From 30 December 2025 (Art. 49(4))"

B = "business"
S = "state"
C = "commission"
H = "household"

# The technologies Art. 4(1) lists, as register slugs. Used where a provision
# reaches the act's whole subject matter rather than a named sector.
NZT = ["batsol", "clean", "ccs", "power"]
# Art. 3(8) and 3(17) name these sectors for energy-intensive industry
# decarbonisation projects, in the act's own words.
EII = ["steel", "alu", "chem", "cement", "glass"]

ROWS: list[tuple] = [

    # ------------------------------------------------------------- benchmarks
    ("BEN-01", "The Commission and Member States shall support net-zero manufacturing projects",
     "necessary to achieve the Union’s 2030 climate and energy targets;",
     dict(measure_type="obligation", direction="add",
          duty="Support net-zero manufacturing projects so that Union manufacturing capacity reaches at least 40% of the Union's annual deployment needs for net-zero technologies by 2030.",
          addressee="The Commission and Member States",
          cls=S, trigger="net-zero technologies listed in Art. 4(1)",
          frequency="continuous", verification="none",
          article="Art. 5(1)(a)", when=WHEN_GENERAL,
          drivers=[], named=NZT, reached=["build"])),

    # ------------------------------------------------- permitting: the plumbing
    ("SPC-01", "By 30 December 2024 Member States shall establish or designate one or more authorities as single points of contact",
     "including information on when an application is considered to be completed in accordance with Article 9(10).",
     dict(measure_type="obligation", direction="add",
          duty="Establish or designate one or more single points of contact responsible for facilitating and coordinating the permit-granting process for net-zero technology manufacturing projects.",
          addressee="Member States",
          cls=S, trigger="entry into application of the Regulation",
          frequency="one-off", verification="none",
          article="Art. 6(1)", when="By 30 December 2024",
          drivers=["D4"], named=NZT, reached=[])),

    ("SPC-02", "Project promoters shall be allowed to submit any documents relevant to the permit-granting process in electronic form.",
     "",
     dict(measure_type="right", direction="add",
          benefit="Project promoters may file every document in the permit-granting process electronically, in any Member State.",
          addressee="Promoters of net-zero technology manufacturing projects",
          cls=B, trigger="any document relevant to the permit-granting process",
          frequency="per application", verification="competent authority",
          article="Art. 6(4)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=[],
          right_basis=dict(text="Project promoters shall be allowed to submit any documents relevant to the permit-granting process in electronic form.",
                           kind="conferral"),
          note="A faculty the promoter did not hold against a Member State that ran the file on paper. The operative verb confers ('shall be allowed to'), so it is right, not a duty being eased.")),

    ("SPC-03", "The competent authorities shall ensure that any relevant studies carried out",
     "unless otherwise required under Union or national law.",
     dict(measure_type="obligation", direction="rem",
          duty="Re-run studies or re-obtain permits and authorisations already carried out or issued for the same project.",
          addressee="Promoters of net-zero technology manufacturing projects",
          cls=B, trigger="a study, permit or authorisation already exists for the project",
          frequency="per application", verification="competent authority",
          article="Art. 6(5)", when=WHEN_GENERAL,
          drivers=[], named=NZT, reached=[],
          note="A duplicated procedural step is switched off. No support moves, so this is the obligation side, direction rem -- Simplification -- not an Opportunity.")),

    ("SPC-04", "The authorities involved in the permit-granting process and other authorities concerned shall specify",
     "before the permit-granting process commences.",
     dict(measure_type="obligation", direction="add",
          duty="Specify and hand to the single point of contact the requirements and the extent of the information that will be demanded of a project promoter, before the permit-granting process starts.",
          addressee="Authorities involved in the permit-granting process",
          cls=S, trigger="a permit-granting process for a net-zero technology manufacturing project",
          frequency="recurring", verification="none",
          article="Art. 6(9)", when=WHEN_GENERAL,
          drivers=[], named=NZT, reached=[])),

    ("INF-01", "Member States shall provide access to the following information on processes relevant to net-zero technology manufacturing projects",
     "online and in a centralised and easily accessible manner:",
     dict(measure_type="obligation", direction="add",
          duty="Publish online, centrally, the single points of contact, the permit-granting process, financing and investment services, funding possibilities and business support services.",
          addressee="Member States",
          cls=S, trigger="processes relevant to net-zero technology manufacturing projects",
          frequency="one-off, kept updated", verification="none",
          article="Art. 7", when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=NZT, reached=[])),

    ("ADM-01", "Member States shall provide administrative support to net-zero technology manufacturing projects located on their territory",
     "paying particular attention to SMEs involved in the projects, including by providing:",
     dict(measure_type="obligation", direction="add",
          duty="Provide administrative support to net-zero technology manufacturing projects, including help with compliance, with informing the public, and with the permit-granting process, with particular attention to SMEs.",
          addressee="Member States",
          cls=S, trigger="a net-zero technology manufacturing project located on the territory",
          frequency="per project", verification="none",
          article="Art. 8", when=WHEN_GENERAL,
          drivers=[], named=NZT, reached=[])),

    ("PRM-01", "The permit-granting process for net-zero technology manufacturing projects shall not exceed any of the following time limits:",
     "18 months for the construction or expansion of net-zero technology manufacturing projects with a yearly manufacturing capacity of 1 GW or more.",
     dict(measure_type="obligation", direction="add",
          duty="Complete the permit-granting process for a net-zero technology manufacturing project within 12 months below 1 GW of yearly manufacturing capacity, or 18 months at 1 GW or more.",
          addressee="Member State permit-granting authorities and single points of contact",
          cls=S, trigger="a permit-granting application for a net-zero technology manufacturing project",
          frequency="per application", verification="none",
          article="Art. 9(1)", when=WHEN_GENERAL,
          drivers=["D5"], named=NZT, reached=[],
          provision_id="nzia-9-1")),

    ("PRM-02", "No later than 45 days from the receipt of the permit-granting application",
     "shall serve as the start of the permit-granting process for that particular application.",
     dict(measure_type="obligation", direction="add",
          duty="Acknowledge that a permit application is complete, or state exactly what is missing, within 45 days; a second request for information may be made within 30 days and may not open new subjects.",
          addressee="Single points of contact",
          cls=S, trigger="receipt of a permit-granting application",
          frequency="per application", verification="none",
          article="Art. 9(10)", when=WHEN_GENERAL,
          drivers=["D5"], named=NZT, reached=[])),

    ("PRM-03", "No later than two months from the date of the receipt of the application, the single point of contact shall draw up",
     "The schedule shall be published by the single point of contact on a free access website.",
     dict(measure_type="obligation", direction="add",
          duty="Draw up a detailed schedule for the permit-granting process within two months of the application and publish it on a free-access website.",
          addressee="Single points of contact",
          cls=S, trigger="receipt of a permit-granting application",
          frequency="per application", verification="none",
          article="Art. 9(11)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=NZT, reached=[])),

    ("PRM-04", "Where energy-intensive industry decarbonisation projects, including when recognised as strategic projects, require the construction of several facilities",
     "for the purposes of complying with the applicable time limits.",
     dict(measure_type="right", direction="add",
          benefit="A decarbonisation project spanning several facilities on one site may be split, by agreement with the single point of contact, into smaller projects so each fits the permitting time limits.",
          addressee="Promoters of energy-intensive industry decarbonisation projects",
          cls=B, trigger="the project requires the construction of several facilities or units on one site",
          frequency="per project", verification="competent authority",
          article="Art. 9(3)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=EII, reached=[],
          right_basis=dict(text="the project promoter and the single point of contact may agree on splitting the project into several smaller projects for the purposes of complying with the applicable time limits",
                           kind="procedure"))),

    ("PRM-05", "the project promoter concerned may request, before submitting the application, an opinion from the single point of contact",
     "no later than 45 days from the date on which the project promoter submitted its request for an opinion.",
     dict(measure_type="right", direction="add",
          benefit="A promoter may obtain, before filing, a binding-in-practice scoping opinion on how detailed the environmental impact assessment report has to be, answered within 45 days.",
          addressee="Promoters of net-zero technology manufacturing projects",
          cls=B, trigger="an environmental impact assessment is required under Arts. 5 to 9 of Directive 2011/92/EU",
          frequency="per project", verification="competent authority",
          article="Art. 10(1)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=[],
          right_basis=dict(text="the project promoter concerned may request, before submitting the application, an opinion from the single point of contact on the scope and level of detail of the information to be included in the environmental impact assessment report",
                           kind="procedure"))),

    ("ENV-01", "Where the obligation to assess the effects on the environment arises simultaneously",
     "Member States shall ensure that a coordinated or joint procedures fulfilling all the requirements of those Union legislative acts are applied.",
     dict(measure_type="obligation", direction="add",
          duty="Where two or more environmental assessment duties arise at once, run a coordinated or joint procedure that satisfies all of them.",
          addressee="Member States",
          cls=S, trigger="assessment duties arising simultaneously under two or more of eight listed environmental directives",
          frequency="per project", verification="competent authority",
          article="Art. 10(2)", when=WHEN_GENERAL,
          drivers=[], named=NZT, reached=[])),

    ("ENV-02", "Member States shall ensure that the competent authorities issue the reasoned conclusion referred to in Article 1(2), point (g)(iv), of Directive 2011/92/EU on the environmental impact assessment within 90 days",
     "and after completing the consultations referred to in Articles 6 and 7 of that Directive.",
     dict(measure_type="obligation", direction="add",
          duty="Issue the reasoned conclusion on the environmental impact assessment within 90 days of receiving all necessary information and completing consultations.",
          addressee="Member State competent authorities",
          cls=S, trigger="a completed environmental impact assessment for a net-zero technology manufacturing project",
          frequency="per project", verification="none",
          article="Art. 10(3)", when=WHEN_GENERAL,
          drivers=["D5"], named=NZT, reached=[])),

    # ------------------------------------------------------ strategic projects
    ("SP-01", "Member States shall recognise as net-zero strategic projects net-zero technology manufacturing projects located in the Union",
     "and fulfil at least one of the following criteria:",
     dict(measure_type="right", direction="add",
          benefit="A manufacturing project meeting any one of the resilience, supply-chain or sustainability criteria is recognised as a net-zero strategic project, which carries the priority permitting track and the public-interest status of Art. 15.",
          addressee="Promoters of net-zero technology manufacturing projects in the Union",
          cls=B, trigger="the project meets at least one of the criteria in Art. 13(1)(a), (b) or (c)",
          frequency="per project", verification="competent authority",
          article="Art. 13(1)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1", "F4"],
          named=NZT, reached=EII,
          right_basis=dict(text="Member States shall recognise as net-zero strategic projects net-zero technology manufacturing projects located in the Union that contribute to achieving the objectives set out in Article 1",
                           kind="scope"),
          note="Phrased as a duty on the Member State; the object is the STATUS conferred on the project, which is what unlocks Arts. 15 and 16. Same reading as IAA PRM-04 and PRM-06 on the identical mechanism.")),

    ("SP-02", "The application referred to in paragraph 1 shall contain the following:",
     "the Union level objective of CO2 injection capacity referred to in Article 20.",
     dict(measure_type="obligation", direction="add",
          duty="File an application for strategic-project recognition containing evidence against the criteria, a business plan evaluating financial viability, and a draft timetable showing when the project contributes to the Union benchmark.",
          addressee="Promoters applying for net-zero strategic project status",
          cls=B, trigger="an application for recognition as a net-zero strategic project",
          frequency="per application", verification="competent authority",
          article="Art. 14(2)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=NZT, reached=EII)),

    ("SP-03", "Member States shall assess the application referred to in paragraph 1 through a fair and transparent process within one month of the receipt of the complete application.",
     "The decision resulting from this process shall be reasoned and shall be communicated to the project promoter and to the Platform referred to in Articles 38 and 39.",
     dict(measure_type="obligation", direction="add",
          duty="Assess a strategic-project application within one month of completeness, request missing information once only, and give a reasoned decision to the promoter and the Platform.",
          addressee="Member States",
          cls=S, trigger="receipt of a complete strategic-project application",
          frequency="per application", verification="none",
          article="Art. 14(3)", when=WHEN_GENERAL,
          drivers=["D5"], named=NZT, reached=[])),

    ("SP-04", "Where a Member State rejects the application, the applicant shall have the right to submit the application to the Commission, which shall assess the application within 20 working days.",
     "",
     dict(measure_type="right", direction="add",
          benefit="A rejected applicant may take the application to the Commission, which must assess it within 20 working days.",
          addressee="Promoters whose strategic-project application was rejected",
          cls=B, trigger="a Member State rejects the application for recognition",
          frequency="if it happens", verification="competent authority",
          article="Art. 14(5)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=NZT, reached=[],
          right_basis=dict(text="the applicant shall have the right to submit the application to the Commission, which shall assess the application within 20 working days",
                           kind="procedure"),
          note="The Commission's assessment is expressly without prejudice to the Member State's decision, so what is conferred is a route to a second reading, not an appeal that overturns.")),

    ("SP-05", "A net-zero technology manufacturing project located in the Union that contributes to achieving the objectives set out in Article 1(1) and that benefits from the ETS Innovation Fund",
     "without the project promoter having to submit a formal application under Article 14(2).",
     dict(measure_type="right", direction="add",
          benefit="Projects already backed by the ETS Innovation Fund, an IPCEI, a European Hydrogen Valley or the Hydrogen Bank get strategic-project status on a written request, with no formal application.",
          addressee="Promoters of Innovation Fund, IPCEI, Hydrogen Valley and Hydrogen Bank backed manufacturing projects",
          cls=B, trigger="the project benefits from one of the named Union funding routes supporting manufacturing capacity",
          frequency="per project", verification="competent authority",
          article="Art. 13(5)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=NZT, reached=EII,
          right_basis=dict(text="shall be recognised by Member States as a net-zero strategic project under Article 14(3) upon the written request of the project promoter without the project promoter having to submit a formal application under Article 14(2)",
                           kind="procedure"))),

    ("SP-06", "A project which is no longer recognised as a net-zero strategic project shall lose all rights connected to that status under this Regulation.",
     "",
     dict(measure_type="right", direction="rem",
          benefit="Strategic-project status, and every right attached to it, is lost where the project changes substantially, stops meeting the criteria, or was recognised on incorrect information.",
          addressee="Promoters of net-zero strategic projects",
          cls=B, trigger="substantial change, loss of the Art. 13 criteria, or recognition based on incorrect information",
          frequency="if it happens", verification="competent authority",
          article="Art. 14(8)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=NZT, reached=[],
          right_basis=dict(text="A project which is no longer recognised as a net-zero strategic project shall lose all rights connected to that status under this Regulation.",
                           kind="conferral"),
          note="The one withdrawal in the act: direction rem on a right row, which the valence rule reads as Entitlement withdrawn. The repeal decision under Art. 14(7) is taken after hearing the promoter.")),

    ("SP-07", "Net-zero strategic projects shall be considered to contribute to the security of supply of net-zero technologies in the Union and, therefore, to be in the public interest.",
     "provided that all the conditions set out in those acts are fulfilled.",
     dict(measure_type="right", direction="add",
          benefit="Strategic projects count as being in the public interest, and may be treated as of overriding public interest, in the derogations of the Water, Birds and Habitats Directives and of nature-restoration law.",
          addressee="Promoters of net-zero strategic projects",
          cls=B, trigger="recognition as a net-zero strategic project",
          frequency="per project", verification="competent authority",
          article="Art. 15(3)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=EII,
          right_basis=dict(text="net-zero strategic projects in the Union shall be considered to be of public interest and may be considered to have an overriding public interest and to serve the interests of public health and safety",
                           kind="conferral"))),

    ("SP-08", "Without prejudice to obligations provided for in Union law, where a project is recognised as a net-zero strategic project, Member States shall grant that net-zero strategic project the status of the highest national significance possible",
     "and, where data is available, to spatial planning.",
     dict(measure_type="right", direction="add",
          benefit="A recognised strategic project is given the highest national significance status the Member State's own law provides, and is treated accordingly in permitting, environmental assessment and spatial planning.",
          addressee="Promoters of net-zero strategic projects",
          cls=B, trigger="recognition as a net-zero strategic project, where national law provides such a status",
          frequency="per project", verification="competent authority",
          article="Art. 15(2)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=[],
          right_basis=dict(text="Member States shall grant that net-zero strategic project the status of the highest national significance possible, where such a status exists in national law",
                           kind="conferral"))),

    ("SP-09", "All dispute resolution procedures, litigation, appeals and judicial remedies related to net-zero strategic projects before any national courts",
     "Project promoters of net-zero strategic projects shall participate in such urgency procedures, where applicable.",
     dict(measure_type="right", direction="add",
          benefit="Litigation and appeals touching a strategic project are treated as urgent wherever national permitting law has an urgency procedure -- with the promoter required to take part in it.",
          addressee="Promoters of net-zero strategic projects",
          cls=B, trigger="dispute resolution, litigation, appeal or judicial remedy related to a net-zero strategic project",
          frequency="if it happens", verification="none",
          article="Art. 15(4)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=[],
          right_basis=dict(text="shall be treated as urgent if and to the extent to which national law concerning permit-granting processes provides for such urgency procedures",
                           kind="scope"),
          note="Carries a participation duty in its final sentence. The object is still the conferred urgency track; the duty is the condition of using it, not a separate burden, so it is not extracted twice.")),

    ("PRM-06", "The permit-granting process for net-zero strategic projects shall not exceed:",
     "18 months for all necessary permits to operate a storage site in accordance with Directive 2009/31/EC.",
     dict(measure_type="obligation", direction="add",
          duty="Complete the permit-granting process for a net-zero strategic project within 9 months below 1 GW, 12 months at 1 GW or more, and 18 months for the permits to operate a CO2 storage site.",
          addressee="Member State permit-granting authorities and single points of contact",
          cls=S, trigger="a permit-granting application for a recognised net-zero strategic project",
          frequency="per application", verification="none",
          article="Art. 16(1)", when=WHEN_GENERAL,
          drivers=["D5"], named=NZT, reached=[],
          provision_id="nzia-9-1")),

    # ---------------------------------------------------------------- valleys
    ("VAL-01", "A decision by a Member State to designate a Valley shall be accompanied by a plan setting out concrete national measures to increase its attractiveness as a location for manufacturing activities",
     "make information about the Valley accessible online in accordance with Article 7.",
     dict(measure_type="obligation", direction="add",
          duty="Accompany any designation of a net-zero Acceleration Valley with a plan carrying at least four support schemes: infrastructure, private investment, reskilling, and online information.",
          addressee="Member States designating net-zero Acceleration Valleys",
          cls=S, trigger="a decision to designate a net-zero Acceleration Valley",
          frequency="per designation", verification="none",
          article="Art. 17(3)", when=WHEN_GENERAL,
          drivers=["D1"], named=NZT, reached=[])),

    ("VAL-02", "Net-zero technology manufacturing projects in Valleys shall be considered to contribute to the security of supply of net-zero technologies in the Union",
     "provided that all the conditions set out in those acts are fulfilled.",
     dict(measure_type="right", direction="add",
          benefit="Siting a manufacturing project in a designated Valley confers the public-interest status -- and the possible overriding public interest -- in the environmental derogations, without the project having to be recognised as strategic.",
          addressee="Promoters of net-zero technology manufacturing projects sited in a Valley",
          cls=B, trigger="the project is located in a designated net-zero Acceleration Valley",
          frequency="per project", verification="competent authority",
          article="Art. 18(4)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=NZT, reached=[],
          right_basis=dict(text="net-zero technology manufacturing projects in Valleys in the Union shall be considered to be of public interest and may be considered to have an overriding public interest",
                           kind="scope"))),

    ("FIN-01", "The Platform shall, at the request of the net-zero strategic project promoter, discuss and advise on how the financing of the project can be completed",
     "relevant Union funding and financing programmes.",
     dict(measure_type="right", direction="add",
          benefit="A strategic-project promoter may call the Platform in to work through how to close the project's financing, across private sources, the EIB Group and other IFIs, national instruments and Union programmes.",
          addressee="Promoters of net-zero strategic projects",
          cls=B, trigger="a request by the promoter of a recognised net-zero strategic project",
          frequency="per project", verification="none",
          article="Art. 19(2)", when=WHEN_GENERAL,
          value_drivers=["V4"], frictions=["F3"],
          named=NZT, reached=[],
          right_basis=dict(text="The Platform shall, at the request of the net-zero strategic project promoter, discuss and advise on how the financing of the project can be completed",
                           kind="procedure"),
          note="What is conferred is access to a financing-coordination process, not money. right, not incentive: no support amount, rate, eligibility or existence moves.")),

    # ------------------------------------------------------ CO2 storage duties
    ("CO2-01", "oblige entities which are or have been holders of an authorisation as defined in Article 1, point 3, of Directive 94/22/EC",
     "the availability or need for transport infrastructure and modes suitable for safely transporting CO2 to reach the site.",
     dict(measure_type="obligation", direction="add",
          duty="Publish, on a non-reliance basis, the geological data on decommissioned production sites -- and any economic assessment of the cost of enabling CO2 injection -- covering whether the site can safely and permanently store CO2 and what transport it would need.",
          addressee="Current and former holders of hydrocarbon authorisations under Directive 94/22/EC",
          cls=B, trigger="a production site that has been decommissioned or whose decommissioning has been notified, unless the holder has applied for a CO2 exploration permit",
          frequency="one-off", verification="competent authority",
          article="Art. 21(1)(b)", when="By 30 December 2024",
          drivers=["D1", "D7"], named=["ccs", "power"], reached=[])),

    ("CO2-02", "Each entity holding an authorisation as defined in Article 1, point 3, of Directive 94/22/EC shall be subject to an individual contribution",
     "shall be excluded from this calculation and shall not be subject to a contribution.",
     dict(measure_type="obligation", direction="add",
          duty="Deliver an individual share of the Union's 50 Mt/year CO2 injection capacity target by 2030, calculated pro-rata on the entity's share of Union crude oil and natural gas production over 2020-2023, as permitted capacity available to the market.",
          addressee="Authorised oil and gas producers above the de minimis production threshold",
          cls=B, trigger="holding a hydrocarbon authorisation with Union crude oil and natural gas production 2020-2023 above the threshold set by delegated act",
          frequency="one-off (capacity in place by 2030)", verification="competent authority",
          article="Art. 23(1)", when="Contribution to be available to the market by 2030",
          drivers=["D4", "D6", "D7"], named=["ccs", "power"], reached=EII,
          provision_id="nzia-23",
          pending="The threshold below which a producer is excluded, and the arrangements for counting third-party storage agreements, are set by delegated act under Art. 23(12).")),

    ("CO2-03", "By 30 June 2025, the entities referred to in paragraph 1 shall submit to the Commission a plan specifying in detail how they intend to meet their contribution",
     "specify the means and the milestones for reaching the targeted volume.",
     dict(measure_type="obligation", direction="add",
          duty="Submit a plan to the Commission confirming the targeted volume of new CO2 storage and injection capacity to be commissioned by 2030, and the means and milestones for reaching it.",
          addressee="Authorised oil and gas producers subject to an individual contribution",
          cls=B, trigger="being identified as an entity subject to a contribution under Art. 23(1)",
          frequency="one-off", verification="competent authority",
          article="Art. 23(4)", when="By 30 June 2025",
          drivers=["D1", "D3", "D6"], named=["ccs", "power"], reached=[],
          provision_id="nzia-23")),

    ("CO2-04", "By 30 June 2026 and every year thereafter, the entities referred to in paragraph 1 shall submit a report to the Commission detailing their progress towards meeting their contribution.",
     "The Commission shall make those reports public.",
     dict(measure_type="obligation", direction="add",
          duty="Report annually to the Commission on progress towards the individual CO2 injection-capacity contribution; the reports are published.",
          addressee="Authorised oil and gas producers subject to an individual contribution",
          cls=B, trigger="being subject to a contribution under Art. 23(1)",
          frequency="annual", verification="competent authority",
          article="Art. 23(6)", when="By 30 June 2026, annually thereafter",
          drivers=["D1", "D5"], named=["ccs", "power"], reached=[],
          provision_id="nzia-23",
          pending="The content of these reports is set by delegated act under Art. 23(12)(c).")),

    ("CO2-05", "In order to meet their targeted volumes of available injection capacity, the entities referred to in paragraph 1 may:",
     "enter into agreements with third-party storage project developers or investors to fulfil their contribution.",
     dict(measure_type="right", direction="add",
          benefit="A producer may discharge its injection-capacity contribution by investing in or developing storage itself, by contracting with another obligated producer, or by contracting with third-party storage developers or investors.",
          addressee="Authorised oil and gas producers subject to an individual contribution",
          cls=B, trigger="meeting the targeted volume of available injection capacity under Art. 23(1)",
          frequency="per project", verification="competent authority",
          article="Art. 23(5)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F5"],
          named=["ccs"], reached=[],
          provision_id="nzia-23",
          right_basis=dict(text="enter into agreements with third-party storage project developers or investors to fulfil their contribution",
                           kind="scope"),
          note="Three compliance routes where a bare quota would have allowed one. The faculty is the pooling itself, on the same reading as ETS FRE-06's joint decarbonisation investment agreement.")),

    ("CO2-06", "By way of derogation from paragraph 1, a Member State may request the Commission to exempt the entities referred to in that paragraph from individual contributions",
     "the application is submitted before the end of 2027.",
     dict(measure_type="obligation", direction="rem",
          duty="Deliver an individual CO2 injection-capacity contribution for production carried out in a Member State whose permitted, FID-reached storage capacity already exceeds the sum of those contributions.",
          addressee="Authorised oil and gas producers active in a Member State that obtains the exemption",
          cls=B, trigger="the Member State applies before the end of 2027 and its permitted storage capacity exceeds the sum of the individual contributions",
          frequency="one-off", verification="competent authority",
          article="Art. 23(7)-(8)", when="Application to be submitted before the end of 2027",
          drivers=[], named=["ccs", "power"], reached=[],
          provision_id="nzia-23",
          note="The duty itself is switched off for a named class. Obligation side, direction rem. Exempted entities may still contract under Art. 23(5)(b)-(c), but only above the exempted volume.")),

    ("CO2-07", "By 30 December 2024 and each year thereafter, each Member State shall submit to the Commission a report, which shall be made publicly available",
     "an estimation of the necessary future CO2 transport projects’ capacity to match the corresponding capture and storage capacity.",
     dict(measure_type="obligation", direction="add",
          duty="Report annually, publicly, on CO2 capture, storage and transport projects in progress, the injection and storage capacity they need, national support measures, capture targets, and cross-border cooperation.",
          addressee="Member States",
          cls=S, trigger="CO2 capture, storage and transport activity on the territory",
          frequency="annual", verification="none",
          article="Art. 21(2)", when="By 30 December 2024, annually thereafter",
          drivers=["D1", "D4", "D5"], named=["ccs"], reached=EII)),

    ("CO2-08", "By 30 September 2024, Member States shall identify and report to the Commission the entities referred to in paragraph 1 and their volumes in crude oil and natural gas production from 1 January 2020 to 31 December 2023.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Identify the authorised oil and gas producers on the territory and report their 2020-2023 crude oil and natural gas production volumes to the Commission.",
          addressee="Member States",
          cls=S, trigger="authorised hydrocarbon producers on the territory",
          frequency="one-off", verification="none",
          article="Art. 23(2)", when="By 30 September 2024",
          drivers=["D1", "D4"], named=["ccs", "power"], reached=[])),

    ("CO2-09", "No later than 30 June 2026, Member States shall lay down penalties by means of administrative procedures, legal proceedings, or both",
     "Those penalties shall be effective, proportionate and dissuasive.",
     dict(measure_type="obligation", direction="add",
          duty="Lay down effective, proportionate and dissuasive penalties for producers that infringe their CO2 injection-capacity obligations.",
          addressee="Member States",
          cls=S, trigger="infringement by an entity subject to a contribution under Art. 23(1)",
          frequency="one-off", verification="none",
          article="Art. 23(13)", when="By 30 June 2026",
          drivers=["D6"], named=["ccs", "power"], reached=[])),

    ("CO2-10", "Member States shall take the necessary measures to enable access to CO2 transport networks and to storage sites",
     "in accordance with Article 21 of Directive 2009/31/EC.",
     dict(measure_type="obligation", direction="add",
          duty="Take the measures needed to open access to CO2 transport networks and storage sites for geological storage, as far as it is economically feasible or where a potential customer is willing to pay.",
          addressee="Member States",
          cls=S, trigger="captured CO2 seeking access to transport networks or storage sites",
          frequency="continuous", verification="none",
          article="Art. 22(2)", when=WHEN_GENERAL,
          drivers=[], named=["ccs"], reached=EII)),

    # -------------------------------------------------------------- procurement
    ("PP-01", "contracting authorities and contracting entities shall apply minimum mandatory requirements regarding environmental sustainability established in the implementing act referred to in paragraph 5 of this Article.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Apply the Commission's minimum mandatory environmental sustainability requirements in every procurement whose subject matter includes solar, wind, battery, heat pump, hydrogen, biogas, CCS, grid, nuclear or sustainable-fuel technology, and in works contracts including it.",
          addressee="Contracting authorities and contracting entities",
          cls=S, trigger="a procurement under Directives 2014/23/EU, 2014/24/EU or 2014/25/EU with Art. 4(1)(a)-(k) net-zero technologies as part of its subject matter",
          frequency="per tender", verification="none",
          article="Art. 25(1)", when=WHEN_PROCUREMENT,
          drivers=["D1"], named=NZT, reached=["build"],
          provision_id="nzia-25-1")),

    ("PP-02", "contracting authorities and contracting entities shall apply at least one of the following conditions, requirements or contractual obligations for the works contracts and works concessions referred to in paragraph 1:",
     "if such legislation exists.",
     dict(measure_type="obligation", direction="add",
          duty="Attach to net-zero works contracts at least one of: a social or employment contract-performance clause, a cybersecurity compliance requirement, or a hard on-time delivery obligation backed by a charge.",
          addressee="Contracting authorities and contracting entities",
          cls=S, trigger="works contracts and works concessions including Art. 4(1)(a)-(k) net-zero technologies",
          frequency="per tender", verification="none",
          article="Art. 25(3)", when=WHEN_GENERAL,
          drivers=["D1", "D6"], named=NZT, reached=["build"])),

    ("PP-03a", "an obligation for the duration of the contract not to supply more than 50 % of the value of the specific net-zero technology referred to in this paragraph from each individual third country as determined by the Commission;",
     "an obligation to pay a proportionate charge, in the event of non-observance of the conditions referred in point (a) or (b), of at least 10 % of the value of the specific net-zero technologies of the contract referred to in this paragraph.",
     dict(measure_type="obligation", direction="add",
          duty="Where the Commission has found a third country supplies more than 50% of a net-zero technology in the Union, hold supply from each such country below 50% of contract value -- for the technology and for its main components -- prove it on request, and pay at least 10% of the contract value if the cap is breached.",
          addressee="Tenderers and successful contractors supplying net-zero technologies to public buyers",
          cls=B, trigger="a Commission determination under Art. 29(2) that one third country exceeds 50% of Union supply, or has gained 10 percentage points over two years and reaches 40%",
          frequency="per contract", verification="self-declaration",
          article="Art. 25(7), second subparagraph", when=WHEN_GENERAL,
          drivers=["D1", "D6"], named=NZT, reached=["build"],
          provision_id="nzia-25-7")),

    ("PP-03b", "If the Commission, at the time of the call for competition for a public procurement procedure as referred to in paragraph 1 of this Article, or commencement of such a procedure, has determined in accordance with Article 29(2)",
     "contracting authorities and contracting entities shall include the following conditions for the public procurement procedures referred to in paragraph 1 of this Article:",
     dict(measure_type="incentive", direction="add",
          benefit="Public demand is reserved away from a dominant third-country source: once the Commission finds one country above 50% of Union supply, no more than half the contract value of that technology, or of its main components, may come from that country -- the balance falls to Union and diversified producers.",
          addressee="Union and diversified non-dominant producers of net-zero technologies and their main components",
          cls=B, trigger="a Commission determination under Art. 29(2) on the concentration of Union supply of a specific net-zero technology",
          frequency="per tender", verification="self-declaration",
          article="Art. 25(7)", when=WHEN_GENERAL,
          value_drivers=["V2"], frictions=["F1"],
          named=NZT, reached=["build"],
          provision_id="nzia-25-7",
          opportunity_basis=dict(text="not to supply more than 50 % of the value of the specific net-zero technology referred to in this paragraph from each individual third country as determined by the Commission",
                                 kind="rate"),
          note="The buyer-side half of this provision is PP-03a. Extracted as a pair on one provision_id, as IAA's lead-market rows are: the cap is a duty on the tenderer and a demand share for everyone outside the dominant source, and stating only one of those misreads the act.")),

    ("PP-04", "Contracting authorities and contracting entities may, on an exceptional basis, decide not to apply paragraphs 1 to 4, where:",
     "Estimated cost differences above 20 %, based on objective and transparent data, may be presumed by contracting authorities and contracting entities to be disproportionate.",
     dict(measure_type="obligation", direction="rem",
          duty="Apply the minimum environmental sustainability requirements where there is a single possible supplier, where a comparable earlier tender drew no suitable bids, or where compliance would cost disproportionately or break technical compatibility.",
          addressee="Contracting authorities and contracting entities",
          cls=S, trigger="sole supplier, an earlier failed tender within two years, or disproportionate cost -- presumed above a 20% cost difference",
          frequency="per tender", verification="none",
          article="Art. 25(9)-(10)", when=WHEN_PROCUREMENT,
          drivers=[], named=NZT, reached=[],
          provision_id="nzia-25-1",
          note="An escape hatch from PP-01's duty, with a quantified presumption attached. A condition is lifted, no support moves: obligation side, direction rem.")),

    # ---------------------------------------------------------------- auctions
    ("AUC-01", "For the technologies listed in Article 4(1), points (a) to (j) that are renewable energy technologies, Member States shall, when designing auctions for the deployment of energy from renewable sources, include:",
     "pre-qualification criteria or award criteria to assess the auction’s sustainability and resilience contribution as referred to in paragraph 2.",
     dict(measure_type="obligation", direction="add",
          duty="Build responsible business conduct, cyber and data security, and delivery-capability pre-qualification into renewable energy auctions, plus pre-qualification or award criteria for the auction's sustainability and resilience contribution.",
          addressee="Member States designing renewable energy auctions",
          cls=S, trigger="an auction for the deployment of energy from renewable sources",
          frequency="per auction", verification="none",
          article="Art. 26(1)", when=WHEN_AUCTIONS,
          drivers=["D1"], named=["clean", "batsol", "power"], reached=[],
          provision_id="nzia-26")),

    ("AUC-02", "Member States shall give to each of the criteria to assess the auction’s sustainability and resilience contribution, when applied as award criteria, a minimum weight of 5 % and a combined weight of between 15 % and 30 % of the award criteria.",
     "",
     dict(measure_type="incentive", direction="add",
          benefit="In renewable energy auctions, sustainability and resilience criteria carry at least 5% each and 15-30% combined of the award score, and the regime bites on at least 30% of the volume auctioned per Member State per year -- a priced advantage for producers outside a dominant third-country source.",
          addressee="Manufacturers of renewable energy technologies and their main components supplying auction participants",
          cls=B, trigger="award criteria in an auction to which Art. 26(1)-(5) applies",
          frequency="per auction", verification="none",
          article="Art. 26(4), with Art. 26(7)", when=WHEN_AUCTIONS,
          value_drivers=["V2"], frictions=["F1"],
          named=["clean", "batsol", "power"], reached=[],
          provision_id="nzia-26",
          opportunity_basis=dict(text="a minimum weight of 5 % and a combined weight of between 15 % and 30 % of the award criteria",
                                 kind="rate"))),

    ("AUC-03", "Member States shall not be obliged to apply the considerations relating to the pre-qualification and award criteria laid down in paragraph 1 where, by applying those criteria, they would incur disproportionate costs.",
     "Estimated cost differences above 15 % per auction, based on objective and verifiable data, may be presumed by Member States to be disproportionate.",
     dict(measure_type="obligation", direction="rem",
          duty="Apply the auction pre-qualification and award criteria where doing so would cost disproportionately -- presumed above a 15% cost difference per auction.",
          addressee="Member States designing renewable energy auctions",
          cls=S, trigger="estimated cost difference above 15% per auction on objective and verifiable data",
          frequency="per auction", verification="none",
          article="Art. 26(5)", when=WHEN_AUCTIONS,
          drivers=[], named=["clean", "batsol", "power"], reached=[],
          provision_id="nzia-26")),

    # -------------------------------------------------- purchase support schemes
    ("SCH-01", "when deciding to set up new schemes or to update existing schemes benefitting households, companies or consumers which incentivise the purchase of net-zero technology final products",
     "while considering the accessibility of the schemes for citizens living in energy poverty.",
     dict(measure_type="obligation", direction="add",
          duty="Design any new or updated scheme that subsidises the purchase of net-zero technology final products so that it favours products with a high sustainability and resilience contribution, either by paying more for them or by making them the eligibility condition.",
          addressee="Member States, regional and local authorities and bodies governed by public law running purchase-support schemes",
          cls=S, trigger="setting up or updating a scheme incentivising the purchase of net-zero technology final products",
          frequency="per scheme", verification="none",
          article="Art. 28(1)", when=WHEN_AUCTIONS,
          drivers=["D1"], named=NZT, reached=["build", "auto"],
          provision_id="nzia-28")),

    ("SCH-02", "The additional financial compensation granted by authorities in accordance with paragraph 1 of this Article, due to the application of the criteria laid down in paragraph 4",
     "shall not exceed 5 % of the cost of the net-zero technology final product for the consumer",
     dict(measure_type="incentive", direction="add",
          benefit="Buyers of net-zero technology final products that score on sustainability and resilience can be paid additional compensation of up to 5% of the product's cost -- up to 15% for households in energy poverty.",
          addressee="Households, companies and consumers buying net-zero technology final products under a public support scheme",
          cls=H, trigger="the purchased product meets the sustainability and resilience criteria of Art. 28(4); energy-poverty status under Regulation (EU) 2023/955 raises the cap",
          frequency="per purchase", verification="self-declaration",
          article="Art. 28(2)", when=WHEN_AUCTIONS,
          value_drivers=["V1"], frictions=["F1"],
          named=NZT, reached=["build", "auto"],
          provision_id="nzia-28",
          opportunity_basis=dict(text="shall not exceed 5 % of the cost of the net-zero technology final product for the consumer",
                                 kind="rate"),
          note="The 15% ceiling for citizens in energy poverty sits in the same sentence, after the footnote marker for Regulation (EU) 2023/955, which is why the span stops at the 5% general cap.")),

    ("SCH-03", "Any net-zero technology final product shall be entitled to apply to join the scheme at any time.",
     "",
     dict(measure_type="right", direction="add",
          benefit="Any net-zero technology final product may apply to join a purchase-support scheme at any time, and the authority must assess it through an open, non-discriminatory and transparent process against a published pass mark.",
          addressee="Manufacturers of net-zero technology final products",
          cls=B, trigger="an existing scheme incentivising the purchase of net-zero technology final products",
          frequency="per scheme", verification="competent authority",
          article="Art. 28(3)", when=WHEN_AUCTIONS,
          value_drivers=["V2"], frictions=["F4"],
          named=NZT, reached=[],
          provision_id="nzia-28",
          right_basis=dict(text="Any net-zero technology final product shall be entitled to apply to join the scheme at any time.",
                           kind="conferral"),
          note="An entry right against a national support scheme -- the anti-lock-in provision of the demand-side chapter. Conferral is explicit: 'shall be entitled to apply'.")),

    ("SCH-04", "Member States shall publish on a single free access website all information relating to schemes pursuant to paragraph 1 for each relevant net-zero technology final product.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish, on one free-access website, all information on purchase-support schemes for each relevant net-zero technology final product.",
          addressee="Member States",
          cls=S, trigger="a scheme incentivising the purchase of net-zero technology final products",
          frequency="per scheme", verification="none",
          article="Art. 28(5)", when=WHEN_AUCTIONS,
          drivers=["D1", "D4"], named=NZT, reached=[])),

    # ------------------------------------------------------ innovation sandboxes
    ("SBX-01", "By 30 March 2025, Member States shall, when setting up net-zero regulatory sandboxes, establish or designate one or more contact points.",
     "A sole contact point shall be responsible for each request to establish a net-zero regulatory sandbox pursuant to this Article.",
     dict(measure_type="obligation", direction="add",
          duty="Establish or designate contact points for net-zero regulatory sandboxes, with one sole contact point responsible for each request.",
          addressee="Member States",
          cls=S, trigger="setting up net-zero regulatory sandboxes",
          frequency="one-off", verification="none",
          article="Art. 33(1)", when="By 30 March 2025",
          drivers=["D4"], named=NZT, reached=[])),

    ("SBX-02", "Member States shall establish net-zero regulatory sandboxes, in close collaboration with industry and, where relevant, research institutes, the social partners and civil society, in accordance with paragraph 1 at the request of any company, organisation or consortium developing innovative net-zero technologies",
     "that has been selected by the competent authorities following the selection procedure referred to in the paragraph 3, second subparagraph, point (b).",
     dict(measure_type="right", direction="add",
          benefit="Any company, organisation or consortium developing innovative net-zero technologies can require a Member State to set up a regulatory sandbox for it, if it meets the eligibility criteria and is selected.",
          addressee="Companies, organisations and consortia developing innovative net-zero technologies",
          cls=B, trigger="a request meeting the eligibility and selection criteria of the implementing act under Art. 33(3)",
          frequency="per project", verification="competent authority",
          article="Art. 33(2)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=NZT, reached=[],
          provision_id="nzia-33",
          right_basis=dict(text="Member States shall establish net-zero regulatory sandboxes, in close collaboration with industry and, where relevant, research institutes, the social partners and civil society, in accordance with paragraph 1 at the request of any company, organisation or consortium developing innovative net-zero technologies",
                           kind="conferral"),
          pending="The eligibility criteria, selection procedure and terms of participation are set by implementing acts under Art. 33(3).")),

    ("SBX-03", "Participants in the net-zero regulatory sandbox shall remain liable under applicable Union and Member States’ liability law for any material harm inflicted on third parties as a result of the testing taking place in the net-zero regulatory sandbox.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Carry full liability under Union and national law for any material harm caused to third parties by testing inside the sandbox.",
          addressee="Participants in net-zero regulatory sandboxes",
          cls=B, trigger="material harm inflicted on third parties as a result of sandbox testing",
          frequency="if it happens", verification="none",
          article="Art. 33(6)", when=WHEN_GENERAL,
          drivers=["D6"], named=NZT, reached=[],
          provision_id="nzia-33",
          note="The price of the sandbox, stated in the same article that grants it: regulatory flexibility does not travel with a liability shield.")),

    ("SME-01", "provide SMEs and start-ups with priority access to the net-zero regulatory sandboxes to the extent that they fulfil the eligibility conditions laid down in Article 33;",
     "",
     dict(measure_type="right", direction="add",
          benefit="SMEs and start-ups get priority access to net-zero regulatory sandboxes, plus a dedicated communication channel and administrative support to take part.",
          addressee="SMEs and start-ups developing innovative net-zero technologies",
          cls=B, trigger="an SME or start-up meeting the Art. 33 eligibility conditions",
          frequency="per project", verification="competent authority",
          article="Art. 34(1)(a)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=NZT, reached=[],
          provision_id="nzia-33",
          right_basis=dict(text="provide SMEs and start-ups with priority access to the net-zero regulatory sandboxes to the extent that they fulfil the eligibility conditions laid down in Article 33",
                           kind="scope"))),

    # ------------------------------------------------------------------- skills
    ("SKL-01", "Within nine months after the completion of the learning content and materials developed by an Academy and every two years thereafter, Member States shall strive to identify whether the learning programmes developed by that Academy are equivalent",
     "Member States shall ensure that the results of the assessments are made public and easily accessible online.",
     dict(measure_type="obligation", direction="add",
          duty="Assess whether an Academy's learning programmes are equivalent to the national qualifications required for regulated professions of interest to the net-zero industry, publish the results, and report the reasons to the Platform where equivalence is not found or not sought.",
          addressee="Member States",
          cls=S, trigger="completion of learning content and materials by a European net-zero industry Academy",
          frequency="every two years", verification="none",
          article="Art. 31(1)", when="Within nine months of an Academy completing its learning content, then every two years",
          drivers=["D1", "D5"], named=NZT, reached=[])),

    # --------------------------------------------------------------- monitoring
    ("MON-01", "Where they are not already included in, or in accordance with the elements of, the national energy and climate plans, each Member State shall submit to the Commission a report setting out the data referred to in paragraph 2 by 15 March 2027 and every three years thereafter.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Collect and report, at least every three years, data on trade obstacles, market and price developments, manufacturing capacity and employment, SME participation, permit-granting outcomes and durations, sandboxes, and CO2 stored underground.",
          addressee="Member States",
          cls=S, trigger="data collection duties under Art. 42(2)",
          frequency="every three years", verification="none",
          article="Art. 42(2)-(3)", when="By 15 March 2027, every three years thereafter",
          drivers=["D1", "D4", "D5"], named=NZT, reached=[],
          note="Art. 42(4) lets a Member State withhold the report where it would run against essential security interests under Art. 346 TFEU.")),

    ("SDG-01", "in Annex III, the following point is added:",
     "including for the purposes of Article 18(1) of that Regulation and contact points established or designated pursuant to Article 33(1) thereof.",
     dict(measure_type="obligation", direction="add",
          duty="Carry net-zero technology manufacturing projects in the Single Digital Gateway: a new information area, the permit procedures and their outputs, and the single points of contact as assistance services.",
          addressee="Member States and the Commission, through the Single Digital Gateway",
          cls=S, trigger="net-zero technology manufacturing projects and net-zero strategic projects",
          frequency="one-off", verification="none",
          article="Art. 48, amending Annexes I, II and III of Regulation (EU) 2018/1724",
          when=WHEN_GENERAL,
          drivers=["D1", "D4"], named=NZT, reached=[],
          note="The only amending provision in the act. Directed at the Single Digital Gateway Regulation, and carried here because it is what puts the permit route in front of a promoter in another Member State.")),
]


# ---------------------------------------------------------------------------
# PROMOTIONS FROM THE SECOND PASS
#
# 33 provisions the paragraph sweep in extract_nzia_pass_b.py found and this
# file did not carry, each ruled `promote` in nzia_rulings.PASS_B_ONLY.
#
# They are BUILT FROM THE PASS ROW, not retyped from it. Retyping is how a
# promoted row drifts from what the second read actually said, and the drift is
# invisible: the row still verifies, because the span is still verbatim, while
# the classification or the addressee has quietly become this file's opinion of
# the provision rather than the pass's. Importing the row makes that impossible
# and makes the provenance mechanical -- pass_origin names the row, and the row
# is the row.
#
# What promotion changes, and nothing else: the id (NZIAB- prefix, matching the
# ETSB-/IAAB-/CBAMB- convention), pass_origin, and provision_id where the ruling
# pairs the promoted row with one already here.
PROMOTED_PROVISION_IDS = {
    "NZIAB-AUC-04": "nzia-26",   # the Member State duty half of AUC-02's pair
}


def promoted_rows() -> list[dict]:
    import extract_nzia_pass_b as passb
    import nzia_rulings as rulings

    b_rows, b_errors = passb.build()
    if b_errors:
        raise LookupError(f"pass B does not build, so nothing can be promoted from it: {b_errors}")
    by_id = {r["id"]: r for r in b_rows}

    out = []
    for pass_id, ruling in sorted(rulings.PASS_B_ONLY.items()):
        if ruling["ruling"] != "promote":
            continue
        src = by_id.get(pass_id)
        if src is None:
            raise LookupError(f"ruling promotes {pass_id}, which pass B does not produce")
        row = dict(src)
        row["id"] = ruling["register_id"]
        # Same key shape the CBAM promotions use: the pass file stem, not its
        # filename. reconciliation_gate.py builds the same key to check that a
        # promoted row exists and a rejected one does not.
        row["pass_origin"] = f"{rulings.PASS_FILE.removesuffix('.json')}:{pass_id}"
        row["provision_id"] = PROMOTED_PROVISION_IDS.get(ruling["register_id"])
        out.append(row)
    return out


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
    # Anchored and sliced against the CANONICAL form of the act, not the raw
    # bytes. The consolidated XHTML writes "Article\xa01" and pads every
    # paragraph number with NBSP, so a raw-byte anchor would have to encode
    # typography that carries no legal meaning -- and canonical() is the same
    # fold verify_pass.py applies on both sides when it checks a span is
    # verbatim, so a span sliced here passes that gate by construction.
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

        row = {"id": rid, "measure_type": meta["measure_type"]}
        if meta["measure_type"] == "obligation":
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
        rows.append(row)

    if not errors:
        rows.extend(promoted_rows())

    return rows, errors


def main() -> int:
    write = "--check" not in sys.argv
    rows, errors = build()

    if errors:
        print(f"ANCHOR FAILURES ({len(errors)}) — nothing written:")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"nzia: {len(rows)} rows")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")

    if write:
        (DATA / "nzia.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written ../data/nzia.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

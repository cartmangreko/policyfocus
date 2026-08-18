"""
Extract the Critical Raw Materials Act -- Regulation (EU) 2024/1252,
consolidated at 3 May 2024 (CELEX 02024R1252-20240503) -- into data/crma.json.

    python3 extract_crma.py --check     # report, write nothing
    python3 extract_crma.py             # write ../data/crma.json

Anchor-based, in the extract_cbam.py / extract_nzia.py idiom: every source_text
is SLICED out of sources/crma.txt by a start/end anchor rather than retyped. A
missing or ambiguous anchor is a hard failure and nothing is written. Anchors
run against the CANONICAL form of the act for the reason set out in
extract_nzia.py: the consolidated XHTML pads article numbers and paragraph
markers with NBSP, and canonical() is the same fold verify_pass.py applies to
both sides when it checks that a span is verbatim.

WHY THIS ACT IS IN THE REGISTER
===============================
scope.md's third IN rule is sector reach, and CRMA reaches the tracked sectors
from the input side rather than the emissions side: it is the act that decides
what a battery, electrolyser, wind generator, traction motor or heat pump maker
must know and declare about the materials going in. Two of its duties are
product duties in the ordinary sense -- the permanent-magnet label and data
carrier (Art. 28) and the recycled-content disclosure (Art. 29) -- and they land
on automotive, clean-tech and battery manufacturers directly, with CE marking
and a conformity assessment behind them (Art. 33).

It is also the act NZIA's scope provision defers to: Art. 2(1) of Regulation
(EU) 2024/1735 excludes critical raw materials falling under this Regulation,
and Art. 2(2) resolves integrated facilities by final product. The two files
are the two halves of one boundary, which is why they are extracted together.

THE BENEFIT AXIS HERE
=====================
Read on the object rule, exactly as the other four files are.

  * Strategic Project recognition (Art. 6(1)), the priority status that follows
    (Art. 10), the three-year grandfathering when Annex I moves (Art. 7(13)),
    and the joint-negotiation faculty (Art. 25(5)) are conferrals -- `right`.
  * The permit-granting time limits (Art. 11) are duties on the AUTHORITY:
    obligation / state / add. Art. 11(7) is the exception in that article and
    is filed as a business duty, because the act puts publication of the
    schedule on the PROJECT PROMOTER, not on the single point of contact.
  * Art. 17's offtake system is the one incentive row: it creates a demand-side
    matching mechanism that did not exist, so opportunity_basis kind
    "existence" -- there is no rate or amount in it to quote, and inventing one
    would be worse than naming what actually moved.
  * Art. 24(3) and Art. 27(1), second subparagraph, are the honest "rem" rows:
    each switches a duty off for a named class -- a company whose suppliers do
    not answer may assess on public data; an operator who can show the waste
    holds no technically recoverable critical raw materials is exempt from the
    study. A condition lifted is the obligation side, direction rem.

WHAT IS NOT HERE, AND WHY
=========================
The Board and its subgroups (Arts. 35-36), Strategic Partnerships (Art. 37),
delegation and comitology (Arts. 38-39), and the Commission's own monitoring,
stress-testing and evaluation duties (Arts. 20, 44, 48) -- institutional
plumbing, out on the same scope.md boundary that keeps the SET Plan Steering
Group out of the NZIA file. Arts. 40-43 amend four other regulations to add
market-surveillance and type-approval hooks for Arts. 28-29; the duties those
hooks enforce are carried here at their source, and the amendments themselves
are procedural.

RECONCILED
==========
This file was one pass when written. extract_crma_pass_b.py is the second read
and reconciliation_gate.py certifies the result:

  * 2 classification disagreements, both HELD FOR THIS FILE (Art. 6(1)
    recognition, Art. 17 offtake) on the object rule.
  * 3 application dates corrected here. Two were real: Art. 5(1)'s benchmarks
    are 2030 targets and this file dated them to entry into force. The third
    was a wording defect -- Art. 28(1) said "entry into force of the labelling
    implementing act", which reads to the date extractor as a commitment to the
    REGULATION's entry into force.
  * 36 provisions promoted, which is why this file is 90 rows and not 54,
    including three whole articles it had missed: Art. 9(3)-(8), Art. 18 and
    Art. 19. One candidate rejected.

The second pass has holes of its own -- it missed Arts. 11(2), 27(4), 31(11),
32(1), 33 and 47, all of which this file carries. That asymmetry is recorded in
crma_rulings.py and in the crosswalk, and it is the best evidence available
that the two reads were genuinely separate.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "crma.txt"
FILE_KEY = "crma"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1252-20240503"

OPERATIVE_ANCHOR = "Article 1 Subject matter and objectives"

# Art. 49(1): twentieth day after OJ publication of 3.5.2024. Art. 49(2) holds
# Arts. 40 and 41 -- the type-approval amendments -- back to 24 May 2029.
WHEN_GENERAL = "From entry into force, 23 May 2024 (Art. 49(1))"

B = "business"
S = "state"
C = "commission"

# The downstream sectors Art. 24(1) and Art. 28(1) name in the act's own words.
DOWNSTREAM = ["batsol", "clean", "auto", "air"]
# Extraction, processing and recycling of the materials themselves.
UPSTREAM = ["waste", "alu", "steel"]

ROWS: list[tuple] = [

    # ------------------------------------------------------------- benchmarks
    ("CBEN-01", "The Commission and Member States shall strengthen the different stages of the strategic raw materials value chain",
     "is capable of recycling significantly increasing amounts of each strategic raw material from waste;",
     dict(measure_type="obligation", direction="add",
          duty="Build Union capacity towards extracting 10%, processing 40% and recycling 25% of the Union's annual consumption of each strategic raw material by 2030.",
          addressee="The Commission and Member States",
          cls=S, trigger="the strategic raw materials listed in Annex I",
          frequency="continuous", verification="none",
          article="Art. 5(1)(a)", when="By 2030 (Art. 5(1))",
          drivers=[], named=UPSTREAM, reached=DOWNSTREAM)),

    ("CBEN-02", "diversify the Union’s imports of strategic raw materials with a view to ensuring that, by 2030",
     "no third country accounts for more than 65 % of the Union’s annual consumption of such a strategic raw material.",
     dict(measure_type="obligation", direction="add",
          duty="Diversify imports so that no single third country supplies more than 65% of the Union's annual consumption of any strategic raw material by 2030.",
          addressee="The Commission and Member States",
          cls=S, trigger="Union consumption of a strategic raw material at any relevant stage of processing",
          frequency="continuous", verification="none",
          article="Art. 5(1)(b)", when="By 2030 (Art. 5(1))",
          drivers=[], named=UPSTREAM, reached=DOWNSTREAM)),

    # ------------------------------------------------------ strategic projects
    ("CSP-01", "Following an application of the project promoter and in accordance with the procedure established in Article 7, the Commission shall recognise as Strategic Projects raw material projects that meet the following criteria:",
     "the project would be mutually beneficial for the Union and the third country concerned by adding value in that third country.",
     dict(measure_type="right", direction="add",
          benefit="A raw materials project meeting all five criteria -- supply-security contribution, technical feasibility, sustainable implementation, cross-border benefit, and mutual benefit for third countries -- is recognised by the Commission as a Strategic Project, which carries the priority permitting track, the financing subgroup and the offtake system.",
          addressee="Promoters of critical raw material projects in the Union, third countries and OCTs",
          cls=B, trigger="an application meeting all criteria in Art. 6(1)(a) to (e), assessed against Annex III",
          frequency="per project", verification="competent authority",
          article="Art. 6(1)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1", "F4"],
          named=UPSTREAM, reached=DOWNSTREAM,
          right_basis=dict(text="the Commission shall recognise as Strategic Projects raw material projects that meet the following criteria",
                           kind="scope"),
          note="Recognition is by the COMMISSION here, unlike NZIA where the Member State recognises. The status is still the object, so the reading is the same as NZIA SP-01 and IAA PRM-04.")),

    ("CSP-02", "Applications for recognition of a critical raw material project as a Strategic Project shall be submitted by the project promoter to the Commission.",
     "as well as measures to address the outcomes of the consultation.",
     dict(measure_type="obligation", direction="add",
          duty="File a Strategic Project application carrying ten items: evidence against the criteria, a UN Framework Classification, a permitting timetable, a public-acceptance plan, ownership and control information, a business plan, a jobs and skills estimate, a post-exploitation environmental restoration plan, an alternative-locations assessment in protected areas, and an indigenous-peoples consultation plan.",
          addressee="Promoters applying for Strategic Project recognition",
          cls=B, trigger="an application for recognition as a Strategic Project",
          frequency="per application", verification="competent authority",
          article="Art. 7(1)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=UPSTREAM, reached=DOWNSTREAM,
          pending="The single application template, which fixes how much documentation each of the ten items actually takes, is set by implementing act under Art. 7(2).")),

    ("CSP-03", "The Commission shall, taking account of the opinion of the Board referred to in paragraph 6, adopt its decision on the recognition of the project as a Strategic Project within 90 days",
     "The Commission shall provide its decision to the Board and to the Member State or third country whose territory is concerned by the project.",
     dict(measure_type="obligation", direction="add",
          duty="Decide on Strategic Project recognition within 90 days of acknowledging a complete application, give reasons, and notify the applicant, the Board and the territory concerned.",
          addressee="The Commission",
          cls=C, trigger="a complete application acknowledged under Art. 7(4)",
          frequency="per application", verification="none",
          article="Art. 7(9)", when=WHEN_GENERAL,
          drivers=["D5"], named=UPSTREAM, reached=[],
          note="Extendable once by up to 90 days under Art. 7(10), and only on notice given at least 20 days before the deadline.")),

    ("CSP-04", "Projects which are no longer recognised as Strategic Projects shall lose all rights connected to that status under this Regulation.",
     "",
     dict(measure_type="right", direction="rem",
          benefit="Strategic Project status, and every right attached to it, is lost where the project stops meeting the Art. 6(1) criteria or was recognised on materially incorrect information.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="withdrawal of recognition by the Commission under Art. 7(11)",
          frequency="if it happens", verification="competent authority",
          article="Art. 7(12)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="Projects which are no longer recognised as Strategic Projects shall lose all rights connected to that status under this Regulation.",
                           kind="conferral"),
          note="Withdrawal is preceded by reasons and a right of reply under Art. 7(11), second subparagraph.")),

    ("CSP-05", "Strategic Projects that no longer fulfil the criteria laid down in Article 6(1) solely due to an update of Annex I shall be allowed to maintain their status as Strategic Projects for three years from the date of that update.",
     "",
     dict(measure_type="right", direction="add",
          benefit="A project that falls out of the criteria only because the list of strategic raw materials moved keeps its status, and everything attached to it, for three years.",
          addressee="Promoters of Strategic Projects affected by an update of Annex I",
          cls=B, trigger="an update of Annex I that alone takes the project outside Art. 6(1)",
          frequency="if it happens", verification="none",
          article="Art. 7(13)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="shall be allowed to maintain their status as Strategic Projects for three years from the date of that update",
                           kind="scope"))),

    ("CSP-06", "The project promoter shall, every two years after the date of recognition as a Strategic Project, submit a report to the Commission containing information on at least:",
     "progress in financing the Strategic Project, including information on public financial support.",
     dict(measure_type="obligation", direction="add",
          duty="Report to the Commission every two years on implementation progress and permitting, on any slippage against the timetable and how it will be recovered, and on progress in financing including public support received.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="recognition as a Strategic Project",
          frequency="every two years", verification="none",
          article="Art. 8(1)", when="Every two years from the date of recognition",
          drivers=["D1", "D5"], named=UPSTREAM, reached=[])),

    ("CSP-07", "The Commission may, where necessary, request additional information from project promoters relevant to the implementation of the Strategic Project to ascertain the continuing fulfilment of the criteria laid down in Article 6(1).",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Supply additional information on the project when the Commission asks for it to check that the recognition criteria are still met.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="a Commission request for additional information",
          frequency="if it happens", verification="none",
          article="Art. 8(2)", when=WHEN_GENERAL,
          drivers=["D1"], named=UPSTREAM, reached=[])),

    ("CSP-08", "The project promoter shall notify the Commission of:",
     "changes in control of the undertakings involved in the Strategic Project on a lasting basis, compared to the information referred to in Article 7(1), point (e).",
     dict(measure_type="obligation", direction="add",
          duty="Notify the Commission of changes to the project that affect the recognition criteria, and of any lasting change of control over the undertakings involved.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="a change affecting the Art. 6(1) criteria or a lasting change of control",
          frequency="if it happens", verification="none",
          article="Art. 8(3)", when=WHEN_GENERAL,
          drivers=["D1"], named=UPSTREAM, reached=[])),

    ("CSP-09", "The project promoter shall establish and regularly update the undertaking’s website or a dedicated project website with information relevant to the local population",
     "It shall be available in a language or languages that can be easily understood by the local population.",
     dict(measure_type="obligation", direction="add",
          duty="Run a free-access project website, in a language the local population understands and requiring no personal data to read, carrying at least the environmental, social and economic impacts and benefits of the project, and keep it updated.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="recognition as a Strategic Project",
          frequency="continuous", verification="none",
          article="Art. 8(5)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=UPSTREAM, reached=[])),

    # -------------------------------------------------------------- permitting
    ("CSPC-01", "By 24 February 2025, Member States shall establish or designate one or more authorities as single points of contact.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Establish or designate single points of contact, with at most one per administrative level and stage of the critical raw materials value chain, and list them on an accessible website.",
          addressee="Member States",
          cls=S, trigger="entry into application of the Regulation",
          frequency="one-off", verification="none",
          article="Art. 9(1)", when="By 24 February 2025",
          drivers=["D4"], named=UPSTREAM, reached=[])),

    ("CPRM-01", "With regard to the environmental impacts or obligations addressed in Article 6(4) and Article 16(1), point (c), of Directive 92/43/EEC",
     "and may be considered to have an overriding public interest provided that all the conditions set out in those Union legislative acts are fulfilled.",
     dict(measure_type="right", direction="add",
          benefit="Strategic Projects in the Union count as being of public interest or serving public health and safety, and may be treated as of overriding public interest, in the derogations of the Habitats, Water and Birds Directives and of ecosystem-restoration law.",
          addressee="Promoters of Strategic Projects in the Union",
          cls=B, trigger="recognition as a Strategic Project",
          frequency="per project", verification="competent authority",
          article="Art. 10(2)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="Strategic Projects in the Union shall be considered to be of public interest or serving public health and safety, and may be considered to have an overriding public interest",
                           kind="conferral"))),

    ("CPRM-02", "Without prejudice to obligations provided for in Union law, Strategic Projects in the Union shall be granted the status of the highest national significance possible",
     "and be treated accordingly in the permit-granting processes.",
     dict(measure_type="right", direction="add",
          benefit="A Strategic Project is given the highest national significance status the Member State's own law provides, and is treated accordingly throughout permitting.",
          addressee="Promoters of Strategic Projects in the Union",
          cls=B, trigger="recognition as a Strategic Project, where national law provides such a status",
          frequency="per project", verification="competent authority",
          article="Art. 10(4)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="Strategic Projects in the Union shall be granted the status of the highest national significance possible, where such a status exists in national law",
                           kind="conferral"))),

    ("CPRM-03", "All dispute resolution procedures, litigation, appeals and judicial remedies related to the permit-granting process and the issuance of permits for Strategic Projects",
     "Project promoters of Strategic Projects shall participate in such urgency procedures, where applicable.",
     dict(measure_type="right", direction="add",
          benefit="Litigation, appeals and remedies over a Strategic Project's permits are treated as urgent wherever national law has an urgency procedure -- with the promoter required to take part in it.",
          addressee="Promoters of Strategic Projects in the Union",
          cls=B, trigger="dispute resolution, litigation, appeal or judicial remedy over the permit-granting process",
          frequency="if it happens", verification="none",
          article="Art. 10(5)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="shall be treated as urgent if and to the extent to which national law provides for such urgency procedures",
                           kind="scope"))),

    ("CPRM-04", "For Strategic Projects in the Union, the permit-granting process shall not exceed:",
     "15 months for Strategic Projects involving only processing or recycling.",
     dict(measure_type="obligation", direction="add",
          duty="Complete the permit-granting process for a Strategic Project within 27 months where it involves extraction, or 15 months where it involves only processing or recycling.",
          addressee="Member State permit-granting authorities and single points of contact",
          cls=S, trigger="a permit-granting application for a recognised Strategic Project",
          frequency="per application", verification="none",
          article="Art. 11(1)", when=WHEN_GENERAL,
          drivers=["D5"], named=UPSTREAM, reached=[],
          provision_id="crma-11",
          note="Extendable once, by six months for extraction and three for processing or recycling, under Art. 11(4).")),

    ("CPRM-05", "for Strategic Projects in the Union that were subject to the permit-granting process before being recognised as Strategic Projects and for extensions of existing Strategic Projects that have already been granted a permit",
     "12 months for Strategic Projects involving only processing or recycling.",
     dict(measure_type="obligation", direction="add",
          duty="Where the project was already in permitting before recognition, or is an extension of a permitted Strategic Project, finish within 24 months for extraction or 12 months for processing or recycling, counted from recognition.",
          addressee="Member State permit-granting authorities and single points of contact",
          cls=S, trigger="a project already in the permit-granting process at the time of recognition, or an extension of a permitted Strategic Project",
          frequency="per application", verification="none",
          article="Art. 11(2)", when=WHEN_GENERAL,
          drivers=["D5"], named=UPSTREAM, reached=[],
          provision_id="crma-11")),

    ("CPRM-06", "No later than 45 days following the receipt of a permit-granting application related to a Strategic Project, the single point of contact concerned shall acknowledge that the application is complete",
     "The date of the acknowledgement referred to in the first subparagraph shall serve as the start of the permit-granting process.",
     dict(measure_type="obligation", direction="add",
          duty="Acknowledge completeness of a Strategic Project permit application within 45 days or state exactly what is missing, and on a second pass ask only for evidence completing what was already identified.",
          addressee="Single points of contact",
          cls=S, trigger="receipt of a permit-granting application for a Strategic Project",
          frequency="per application", verification="none",
          article="Art. 11(6)", when=WHEN_GENERAL,
          drivers=["D5"], named=UPSTREAM, reached=[])),

    ("CPRM-07", "The schedule shall be published by the project promoter on the website referred to in Article 8(5).",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish the permit-granting schedule drawn up by the single point of contact on the project's own free-access website.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="a detailed permitting schedule drawn up under Art. 11(7)",
          frequency="per project", verification="none",
          article="Art. 11(7)", when=WHEN_GENERAL,
          drivers=["D1"], named=UPSTREAM, reached=[],
          note="The one duty in the permitting article that lands on the promoter rather than the authority: NZIA Art. 9(11) puts the same publication on the single point of contact.")),

    ("CENV-01", "the relevant project promoter shall request, no later than 30 days after the notification of the recognition as a Strategic Project and before submitting the application, an opinion from the single point of contact concerned",
     "within a period of time not exceeding 45 days from the date on which the project promoter submitted its request for an opinion.",
     dict(measure_type="obligation", direction="add",
          duty="Request a scoping opinion on the environmental impact assessment report within 30 days of being notified of Strategic Project recognition, and before filing the permit application.",
          addressee="Promoters of Strategic Projects requiring an environmental impact assessment",
          cls=B, trigger="an environmental impact assessment required under Arts. 5 to 9 of Directive 2011/92/EU",
          frequency="per project", verification="competent authority",
          article="Art. 12(1)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=UPSTREAM, reached=[],
          note="The mirror image of NZIA Art. 10(1), which makes the same scoping opinion a faculty ('may request'). Here it is compulsory and clocked, so it is a duty, not a right -- the operative verb decides.")),

    ("CENV-02", "In the case of Strategic Projects for which the obligation to carry out assessments of the effects on the environment arises simultaneously",
     "Member States shall ensure that a coordinated or a joint procedure fulfilling all the requirements of those Union legislative acts is applied.",
     dict(measure_type="obligation", direction="add",
          duty="Where two or more environmental assessment duties arise at once for a Strategic Project, run a coordinated or joint procedure satisfying all of them.",
          addressee="Member States",
          cls=S, trigger="assessment duties arising simultaneously under two or more of seven listed environmental directives",
          frequency="per project", verification="competent authority",
          article="Art. 12(2)", when=WHEN_GENERAL,
          drivers=[], named=UPSTREAM, reached=[])),

    ("CENV-03", "Member States shall ensure that the competent authorities issue the reasoned conclusion referred to in Article 1(2), point (g)(iv), of Directive 2011/92/EU on the environmental impact assessment of a Strategic Project within 90 days",
     "and after completing the consultations referred to in Articles 6 and 7 of that Directive.",
     dict(measure_type="obligation", direction="add",
          duty="Issue the reasoned conclusion on a Strategic Project's environmental impact assessment within 90 days of receiving all necessary information and completing consultations.",
          addressee="Member State competent authorities",
          cls=S, trigger="a completed environmental impact assessment for a Strategic Project",
          frequency="per project", verification="none",
          article="Art. 12(3)", when=WHEN_GENERAL,
          drivers=["D5"], named=UPSTREAM, reached=[])),

    # ------------------------------------------------------------- enabling
    ("CFIN-01", "The standing subgroup established pursuant to Article 36(8), point (a) shall, at the request of a project promoter of a Strategic Project, discuss and provide advice on how the financing of its project can be completed",
     "relevant Union funding and financing programmes, with a particular focus on the Global Gateway Initiative for Strategic Projects in third countries or in OCTs.",
     dict(measure_type="right", direction="add",
          benefit="A Strategic Project promoter may call in the Board's financing subgroup to work through how to close the project's financing, across private sources, the EIB Group and other IFIs, national instruments and export credit agencies, and Union programmes including Global Gateway.",
          addressee="Promoters of Strategic Projects",
          cls=B, trigger="a request by the promoter of a recognised Strategic Project",
          frequency="per project", verification="none",
          article="Art. 16(1)", when=WHEN_GENERAL,
          value_drivers=["V4"], frictions=["F3"],
          named=UPSTREAM, reached=[],
          right_basis=dict(text="at the request of a project promoter of a Strategic Project, discuss and provide advice on how the financing of its project can be completed",
                           kind="procedure"),
          note="Access to a financing-coordination process, not money -- so right, not incentive. Same reading as NZIA FIN-01 on the equivalent Platform provision.")),

    ("COFF-01", "The Commission shall set up a system to facilitate the conclusion of offtake agreements related to Strategic Projects, in accordance with competition rules.",
     "",
     dict(measure_type="incentive", direction="add",
          benefit="A Commission-run matching system where offtakers bid volumes, qualities, prices and durations and Strategic Project promoters post offers, with the Commission introducing the two sides -- demand-side access a project developer did not previously have.",
          addressee="Promoters of Strategic Projects and offtakers of strategic raw materials",
          cls=B, trigger="a Strategic Project seeking offtake, or a buyer seeking strategic raw materials",
          frequency="continuous", verification="none",
          article="Art. 17(1)-(4)", when=WHEN_GENERAL,
          value_drivers=["V2"], frictions=["F1"],
          named=UPSTREAM, reached=DOWNSTREAM,
          opportunity_basis=dict(text="The Commission shall set up a system to facilitate the conclusion of offtake agreements related to Strategic Projects, in accordance with competition rules.",
                                 kind="existence"),
          note="kind 'existence': the mechanism itself is what moves. There is no rate or amount in Art. 17 to quote, and manufacturing one would be worse than naming the conferral the act actually makes.")),

    # -------------------------------------------------------------- monitoring
    ("CMON-01", "Member States shall identify key market operators along the critical raw materials value chain established in their territory and shall:",
     "without delay notify the Commission of major events that may hinder the regular operations of the activities of key market operators.",
     dict(measure_type="obligation", direction="add",
          duty="Identify the key market operators in the critical raw materials value chain on the territory, monitor them through public data and proportionate surveys, report the results, and notify the Commission without delay of major events disrupting them.",
          addressee="Member States",
          cls=S, trigger="key market operators along the critical raw materials value chain established on the territory",
          frequency="recurring", verification="none",
          article="Art. 21(2)", when=WHEN_GENERAL,
          drivers=["D4", "D5"], named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-21-2")),

    ("CMON-02", "They shall submit such data only to the extent that it is already available to them.",
     "it shall provide the requesting Member State with reasons therefor.",
     dict(measure_type="obligation", direction="add",
          duty="Answer a Member State's monitoring survey with the data already held, and give reasons for any refusal or claim that the data is unavailable.",
          addressee="Key market operators along the critical raw materials value chain",
          cls=B, trigger="a Member State survey under Art. 21(2)(a)",
          frequency="recurring", verification="none",
          article="Art. 21(2), third subparagraph", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-21-2")),

    ("CMON-03", "Key market operators may refuse to submit data requested pursuant to point (a) of the first subparagraph if the sharing of such data would lead to the disclosure of trade or business secrets.",
     "",
     dict(measure_type="right", direction="add",
          benefit="A key market operator may refuse a monitoring data request where answering it would disclose trade or business secrets, and is never obliged to generate data it does not already hold.",
          addressee="Key market operators along the critical raw materials value chain",
          cls=B, trigger="a monitoring data request that would disclose trade or business secrets",
          frequency="if it happens", verification="none",
          article="Art. 21(2), third subparagraph", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F1"],
          named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-21-2",
          right_basis=dict(text="Key market operators may refuse to submit data requested pursuant to point (a) of the first subparagraph if the sharing of such data would lead to the disclosure of trade or business secrets.",
                           kind="scope"),
          note="The paired half of CMON-02, on one provision_id: the same subparagraph creates the answering duty and the trade-secret carve-out, and reporting only one of them would misstate the reach of the survey power.")),

    ("CSTK-01", "Member States shall, in their reports submitted pursuant to Article 45, submit to the Commission information on the state of their strategic stocks of strategic raw materials.",
     "Where a Member State refuses to provide such information, it shall provide a justified notice.",
     dict(measure_type="obligation", direction="add",
          duty="Report the state of national strategic stocks -- levels in tonnes and as a share of annual consumption, chemical form and purity, five-year evolution, and the rules for release and distribution -- or give a justified notice for withholding it on defence or national security grounds.",
          addressee="Member States",
          cls=S, trigger="strategic stocks held by public authorities, publicly owned companies or economic operators charged by the Member State",
          frequency="recurring", verification="none",
          article="Art. 22(1)-(2)", when=WHEN_GENERAL,
          drivers=["D1", "D5"], named=UPSTREAM, reached=DOWNSTREAM,
          note="Art. 23(8) is explicit that neither article obliges a Member State to hold or release stocks; what is created is a reporting duty over whatever is held.")),

    # -------------------------------------------------- company risk preparedness
    ("CRSK-01", "By 24 May 2025 and within 12 months of each update of the list of strategic raw materials pursuant to Article 3(3), Member States shall identify the large companies operating on their territory",
     "rocket launchers, satellites or advanced chips.",
     dict(measure_type="obligation", direction="add",
          duty="Identify the large companies on the territory that use strategic raw materials to make batteries, hydrogen equipment, renewable generation equipment, aircraft, traction motors, heat pumps, data and mobile equipment, additive manufacturing and robotics equipment, drones, rocket launchers, satellites or advanced chips.",
          addressee="Member States",
          cls=S, trigger="an update of the list of strategic raw materials under Art. 3(3)",
          frequency="one-off, then within 12 months of each list update", verification="none",
          article="Art. 24(1)", when="By 24 May 2025",
          drivers=["D4"], named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-24")),

    ("CRSK-02", "Large companies as referred to in paragraph 1 shall, at least every three years and to the extent the required information is available to them, carry out a risk assessment of their raw materials supply chain of strategic raw materials",
     "an assessment of their vulnerabilities to supply disruptions.",
     dict(measure_type="obligation", direction="add",
          duty="Carry out, at least every three years, a supply-chain risk assessment mapping where the strategic raw materials used are extracted, processed or recycled, analysing what could affect their supply, and assessing the company's vulnerability to disruption.",
          addressee="Large companies making batteries, hydrogen, renewable, aerospace, traction, heat pump, electronics, robotics or chip equipment with strategic raw materials",
          cls=B, trigger="identification by a Member State under Art. 24(1)",
          frequency="every three years", verification="self-declaration",
          article="Art. 24(2)", when="First assessment following identification, from 24 May 2025",
          drivers=["D1", "D5"], named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-24")),

    ("CRSK-03", "Where the information referred to in paragraph 2 of this Article is not made available to large companies as referred to in paragraph 1 of this Article by their suppliers upon request",
     "or otherwise publicly available information, to the extent possible.",
     dict(measure_type="obligation", direction="rem",
          duty="Obtain supply-chain information from suppliers in order to carry out the risk assessment.",
          addressee="Large companies subject to the Art. 24(2) risk assessment",
          cls=B, trigger="suppliers do not provide the requested information",
          frequency="every three years", verification="self-declaration",
          article="Art. 24(3)", when=WHEN_GENERAL,
          drivers=[], named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-24",
          note="A due-diligence duty that would otherwise run down the supply chain is capped: where suppliers do not answer, the company may assess on the Commission's published monitoring data. A condition is lifted, no support moves -- obligation side, direction rem.")),

    ("CRSK-04", "If significant vulnerabilities to supply disruptions are detected as a result of the risk assessment referred to in paragraph 2, large companies as referred to under paragraph 1 shall take efforts to mitigate those vulnerabilities",
     "including by assessing the possibility to diversify its raw materials supply chains or to substitute the strategic raw materials.",
     dict(measure_type="obligation", direction="add",
          duty="Where the risk assessment finds significant vulnerabilities, take mitigating action, including assessing whether supply chains can be diversified or the strategic raw materials substituted.",
          addressee="Large companies subject to the Art. 24(2) risk assessment",
          cls=B, trigger="significant vulnerabilities to supply disruptions detected by the assessment",
          frequency="every three years", verification="self-declaration",
          article="Art. 24(4)", when=WHEN_GENERAL,
          drivers=["D1"], named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-24")),

    ("CRSK-05", "Member States may require large companies as referred to in paragraph 1 to present to their board of directors the report referred to in paragraph 5 and the requests for information referred to in paragraph 3.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Present the risk-assessment report, and the information requests made to suppliers, to the board of directors.",
          addressee="Large companies in Member States that exercise the Art. 24(6) option",
          cls=B, trigger="a Member State requiring board presentation under Art. 24(6)",
          frequency="every three years", verification="self-declaration",
          article="Art. 24(6)", when=WHEN_GENERAL,
          drivers=["D1", "D3"], named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-24",
          pending="A national option, not a Union duty: it binds only in Member States that exercise it, and the register cannot say which have until national measures are notified.")),

    ("CJP-01", "Union undertakings participating in the system referred to in paragraph 1 may, on a transparent basis, jointly negotiate the purchase",
     "Participating Union undertakings shall comply with Union law, including Union competition law.",
     dict(measure_type="right", direction="add",
          benefit="Undertakings in the Commission's demand-aggregation system may jointly negotiate purchases -- prices and other terms included -- to win better conditions from suppliers or head off shortages, on a transparent basis and within competition law.",
          addressee="Union undertakings consuming strategic raw materials",
          cls=B, trigger="participation in the Commission's demand aggregation system under Art. 25(1)",
          frequency="per purchase", verification="none",
          article="Art. 25(5)", when=WHEN_GENERAL,
          value_drivers=["V2"], frictions=["F5"],
          named=DOWNSTREAM, reached=UPSTREAM,
          provision_id="crma-25",
          right_basis=dict(text="may, on a transparent basis, jointly negotiate the purchase, including the prices or other terms and conditions of the purchasing agreement or use joint purchasing in order to achieve better conditions with their suppliers or to prevent shortages",
                           kind="conferral"),
          note="Buyers acting together on price is exactly what competition law normally forbids; the faculty is the point of the provision, and the closing sentence is its limit.")),

    ("CJP-02", "Entities shall be excluded from participating in demand aggregation and joint purchasing as well as from participating as suppliers or service providers if they are:",
     "directly or indirectly owned or controlled by, or acting on behalf or at the direction of natural or legal persons, entities or bodies targeted by such Union restrictive measures.",
     dict(measure_type="obligation", direction="add",
          duty="Stay out of demand aggregation and joint purchasing, as participant, supplier or service provider, where sanctioned under Art. 215 TFEU or owned, controlled by or acting for a sanctioned person.",
          addressee="Entities targeted by Union restrictive measures, and entities they own, control or direct",
          cls=B, trigger="being targeted by Union restrictive measures adopted under Art. 215 TFEU, or owned, controlled by or acting for such a target",
          frequency="continuous", verification="competent authority",
          article="Art. 25(6)", when=WHEN_GENERAL,
          drivers=[], named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-25")),

    # ------------------------------------------------------------- circularity
    ("CCIR-01", "Each Member State shall, by two years from the date of entry into force of the implementing act referred to in paragraph 7, adopt and implement, or include in, national programmes containing measures designed to:",
     "where relevant, support the use of Union quality standards for recycling processes of waste streams containing critical raw materials.",
     dict(measure_type="obligation", direction="add",
          duty="Adopt and run national circularity programmes: incentivise resource efficiency, promote re-use and repair, raise collection and processing of critical-raw-material-bearing waste including metal scrap, use recycled content in procurement award criteria or financial incentives, mature recycling technologies, build workforce skills, modulate extended producer responsibility fees, police waste exports, and support Union recycling quality standards.",
          addressee="Member States",
          cls=S, trigger="entry into force of the implementing act listing products, components and waste streams with recovery potential",
          frequency="one-off, reviewed within five years", verification="none",
          article="Art. 26(1)", when="Within two years of entry into force of the implementing act under Art. 26(7)",
          drivers=["D1"], named=["waste"], reached=UPSTREAM + DOWNSTREAM,
          pending="The list of products, components and waste streams with relevant critical raw materials recovery potential -- which fixes what the programmes have to reach -- is set by implementing act under Art. 26(7).")),

    ("CCIR-02", "Member States shall identify separately, and report, the quantities of components containing relevant amounts of critical raw materials removed from waste electrical and electronic equipment and the quantities of critical raw materials recovered from such equipment.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Identify and report separately the quantities of critical-raw-material-bearing components removed from waste electrical and electronic equipment, and the quantities of critical raw materials recovered from it.",
          addressee="Member States",
          cls=S, trigger="waste electrical and electronic equipment reporting under Art. 16(6) of Directive 2012/19/EU",
          frequency="annual", verification="none",
          article="Art. 26(5)", when="First reporting period is the first full calendar year after the implementing act is adopted",
          drivers=["D1", "D4", "D5"], named=["waste"], reached=UPSTREAM)),

    ("CEXW-01", "Operators obliged to draw up waste management plans in accordance with Article 5 of Directive 2006/21/EC shall provide to the competent authority",
     "the extractive waste being generated or, where considered more effective, from the extracted volume prior to it becoming waste.",
     dict(measure_type="obligation", direction="add",
          duty="Produce and file a preliminary economic assessment study of the potential to recover critical raw materials from the extractive waste stored in the facility and from waste being generated, estimating quantities and concentrations and assessing technical and economic recoverability.",
          addressee="Operators of extractive waste facilities under Directive 2006/21/EC",
          cls=B, trigger="an obligation to draw up a waste management plan under Art. 5 of Directive 2006/21/EC",
          frequency="one-off", verification="competent authority",
          article="Art. 27(1)-(3)", when="By 24 November 2026; new facilities file with their waste management plan",
          drivers=["D1", "D3", "D4"], named=["waste", "alu", "steel"], reached=UPSTREAM,
          provision_id="crma-27")),

    ("CEXW-02", "Operators shall be exempt from the obligation laid down in the first subparagraph of this paragraph where they can demonstrate to the competent authority",
     "that the extractive waste does not contain critical raw materials that are technically recoverable.",
     dict(measure_type="obligation", direction="rem",
          duty="Produce the preliminary economic assessment study on recovering critical raw materials from extractive waste.",
          addressee="Operators of extractive waste facilities holding no technically recoverable critical raw materials",
          cls=B, trigger="demonstrating to the competent authority, with a high degree of certainty, that the waste holds no technically recoverable critical raw materials",
          frequency="one-off", verification="competent authority",
          article="Art. 27(1), second subparagraph", when=WHEN_GENERAL,
          drivers=[], named=["waste"], reached=[],
          provision_id="crma-27",
          note="The study duty is switched off for a named class, on a demonstration to the authority. Obligation side, direction rem -- the exemption still costs the operator the demonstration.")),

    ("CEXW-03", "Member States shall establish a database of the closed extractive waste facilities located on their territory",
     "any additional information considered relevant by the Member State to enable the recovery of critical raw materials from the extractive waste facility.",
     dict(measure_type="obligation", direction="add",
          duty="Build a public database of closed and abandoned extractive waste facilities carrying location, extent and waste volume, the operator or successor, and the quantities and concentrations of raw materials held -- backed by permit-file review, geochemical sampling and detailed characterisation.",
          addressee="Member States",
          cls=S, trigger="closed and abandoned extractive waste facilities on the territory",
          frequency="one-off, updated at least every three years", verification="none",
          article="Art. 27(4), with Art. 27(6)-(7)", when="Database in place by 24 November 2025, populated by 24 May 2027",
          drivers=["D1", "D4", "D5"], named=["waste"], reached=UPSTREAM)),

    # ---------------------------------------------------------- permanent magnets
    ("CMAG-01", "any natural or legal person that places on the market magnetic resonance imaging devices, wind energy generators, industrial robots, motor vehicles",
     "ferrite.",
     dict(measure_type="obligation", direction="add",
          duty="Label MRI devices, wind generators, industrial robots, motor vehicles, light means of transport, cooling generators, heat pumps, electric motors, washing machines, driers, microwaves, vacuum cleaners and dishwashers with a conspicuous, legible and indelible statement of whether they contain permanent magnets and of which of the four magnet types.",
          addressee="Anyone placing the listed products on the Union market",
          cls=B, trigger="placing a listed product on the Union market",
          frequency="per product model", verification="self-declaration",
          article="Art. 28(1)", when="Two years after the labelling implementing act; 24 May 2029 for MRI devices, motor vehicles and category L vehicles",
          drivers=["D1", "D7"], named=["auto", "clean"], reached=["batsol"],
          provision_id="crma-28",
          pending="The label format is set by implementing act under Art. 28(2), and the two-year clock runs from that act's entry into force.")),

    ("CMAG-02", "any natural or legal person that places on the market products referred to in paragraph 1 incorporating one or more permanent magnets of the types referred in paragraph 1, point (b) shall ensure that a data carrier is present on or in the product.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Put a data carrier on or in every listed product containing a permanent magnet, linked to a unique product identifier giving the responsible person's identity, the weight, location and chemical composition of each magnet including coatings, glues and additives, and the steps, tools and technologies for accessing and safely removing them.",
          addressee="Anyone placing listed products containing permanent magnets on the Union market",
          cls=B, trigger="placing a listed product incorporating a neodymium-iron-boron, samarium-cobalt, aluminium-nickel-cobalt or ferrite magnet on the market",
          frequency="per product model", verification="self-declaration",
          article="Art. 28(3)-(4)", when="Two years after the labelling implementing act",
          drivers=["D1", "D4", "D7"], named=["auto", "clean"], reached=["batsol"],
          provision_id="crma-28")),

    ("CMAG-03", "The natural or legal person placing a product referred to in paragraph 3 on the market shall ensure that information referred to in paragraph 4 is complete, up-to-date, and accurate",
     "The information referred to in paragraph 4 shall be accessible to repairers, recyclers, market surveillance authorities and customs authorities.",
     dict(measure_type="obligation", direction="add",
          duty="Keep the magnet information complete, current and accurate, and available for the product's typical lifetime plus ten years -- surviving insolvency, liquidation or exit from the Union -- and accessible to repairers, recyclers, market surveillance and customs.",
          addressee="Anyone placing listed products containing permanent magnets on the Union market",
          cls=B, trigger="a listed product incorporating a permanent magnet placed on the market",
          frequency="continuous", verification="competent authority",
          article="Art. 28(7)", when="Two years after the labelling implementing act",
          drivers=["D1", "D5"], named=["auto", "clean"], reached=["batsol"],
          provision_id="crma-28")),

    ("CMAG-04", "9. Products primarily designed for defence or space applications shall be exempt from the requirements laid down in this Article.",
     "vehicles produced in small series, as defined in Article 3, point (30), of Regulation (EU) 2018/858.",
     dict(measure_type="obligation", direction="rem",
          duty="Carry the permanent-magnet label, data carrier and magnet information.",
          addressee="Makers of defence and space products, special purpose vehicles, multi-stage type-approved vehicle parts and small-series vehicles",
          cls=B, trigger="a product primarily designed for defence or space, a special purpose vehicle, a non-base vehicle part type-approved in multi-stage approval of category N1, N2, N3, M2 or M3, or a small-series vehicle",
          frequency="per product model", verification="none",
          article="Art. 28(9) and 28(11)", when=WHEN_GENERAL,
          drivers=[], named=["auto"], reached=[],
          provision_id="crma-28",
          note="Art. 28(8) adds a further switch-off: where Union harmonisation legislation sets magnet recycling information requirements for a listed product, those apply in place of this article.")),

    ("CMAG-05", "By 24 May 2027 or two years from the entry into force of the delegated act referred to in paragraph 2, whichever is later, any natural or legal person that places on the market products referred to in Article 28(1)",
     "recovered from post-consumer waste present in the permanent magnets incorporated in the product.",
     dict(measure_type="obligation", direction="add",
          duty="Publish, on a free-access website, the share of neodymium, dysprosium, praseodymium, terbium, boron, samarium, nickel and cobalt recovered from post-consumer waste in the product's permanent magnets, once the total magnet weight passes 0.2 kg.",
          addressee="Anyone placing listed products with more than 0.2 kg of rare-earth or samarium-cobalt magnets on the market",
          cls=B, trigger="total weight of neodymium-iron-boron, samarium-cobalt or aluminium-nickel-cobalt magnets in the product exceeding 0,2 kg",
          frequency="per product model", verification="self-declaration",
          article="Art. 29(1)", when="By 24 May 2027, or two years from the calculation-rules delegated act, whichever is later; five years for MRI devices, motor vehicles and category L vehicles",
          drivers=["D1", "D4"], named=["auto", "clean"], reached=["batsol", "waste"],
          provision_id="crma-29",
          pending="The rules for calculating and verifying the recycled share -- and the conformity assessment module that goes with them -- are set by delegated act under Art. 29(2), due 24 May 2026.")),

    ("CMAG-06", "the Commission shall adopt delegated acts supplementing this Regulation by laying down minimum shares for neodymium, dysprosium, praseodymium, terbium, boron, samarium, nickel and cobalt recovered from post-consumer waste that must be present in the permanent magnet",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Meet minimum recycled shares of neodymium, dysprosium, praseodymium, terbium, boron, samarium, nickel and cobalt in the permanent magnets of listed products.",
          addressee="Anyone placing listed products with permanent magnets on the Union market",
          cls=B, trigger="delegated acts setting minimum recycled shares, which may differ by product and may exclude products",
          frequency="per product model", verification="accredited third party",
          article="Art. 29(3)", when="Delegated acts due after the Art. 29(2) rules and in any event by 31 December 2031, with transitional periods",
          drivers=["D1", "D2", "D4"], named=["auto", "clean"], reached=["batsol", "waste"],
          provision_id="crma-29",
          pending="The substance of this duty -- the actual minimum shares, which products they reach, and the transitional periods -- is entirely in delegated acts not yet adopted. The register carries the hook, not a number.")),

    ("CMAG-07", "when offering the products referred to in paragraph 1 for sale, including in the case of distance selling, or displaying them in the course of a commercial activity",
     "likely to mislead or confuse customers with respect to the information referred to in paragraph 1.",
     dict(measure_type="obligation", direction="add",
          duty="Give customers access to the recycled-content information before they are bound by a sales contract, including in distance selling, and display no label, mark, symbol or inscription likely to mislead or confuse them about it.",
          addressee="Anyone placing listed products with permanent magnets on the Union market",
          cls=B, trigger="offering a listed product for sale or displaying it in the course of a commercial activity",
          frequency="continuous", verification="competent authority",
          article="Art. 29(5)", when="From the date the Art. 29(1) disclosure requirement applies",
          drivers=["D1"], named=["auto", "clean"], reached=["batsol"],
          provision_id="crma-29")),

    # ------------------------------------------- footprint, conformity, schemes
    ("CFP-01", "Any natural or legal person that places on the market critical raw materials, including processed and recycled, for which the Commission has adopted calculation and verification rules pursuant to paragraph 1 shall make available an environmental footprint declaration.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish an environmental footprint declaration for each critical raw material type placed on the market once calculation rules exist for it, naming the responsible person, the material type, the countries and regions of extraction, processing, refining and recycling, the calculated footprint, its performance class, and a link to the supporting study.",
          addressee="Anyone placing critical raw materials, including processed and recycled, on the Union market",
          cls=B, trigger="the Commission having adopted calculation and verification rules for that critical raw material",
          frequency="per material type", verification="accredited third party",
          article="Art. 31(6)-(7)", when="From adoption of the calculation and verification rules for the material concerned",
          drivers=["D1", "D2", "D4"], named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-31",
          pending="Conditional on a two-step Commission process: a report by 24 November 2025 prioritising materials, then a necessity and proportionality assessment, then calculation and verification rules by delegated act. No material carries this duty until that runs. It does not reach critical raw materials inside intermediate or final products.")),

    ("CFP-02", "When offering critical raw materials for sale, including in the case of distance selling, or displaying them in the course of a commercial activity, natural and legal persons placing on the market critical raw materials shall ensure that their customers have access to the environmental footprint declaration before being bound by a sales contract.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Give customers access to the environmental footprint declaration before they are bound by a sales contract, and display nothing likely to mislead or confuse them about what it says.",
          addressee="Anyone placing critical raw materials on the Union market",
          cls=B, trigger="offering critical raw materials for sale or displaying them in the course of a commercial activity",
          frequency="continuous", verification="competent authority",
          article="Art. 31(11)", when="From adoption of the calculation and verification rules for the material concerned",
          drivers=["D1"], named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-31")),

    ("CCNF-01", "Before placing a product covered by Article 28 or 29 on the market, the natural or legal persons responsible shall ensure that the applicable conformity assessment procedure has been carried out and that the required technical documentation has been drawn up.",
     "the natural or legal persons responsible shall ensure that an EU declaration of conformity has been drawn up and the CE marking has been affixed.",
     dict(measure_type="obligation", direction="add",
          duty="Run the applicable conformity assessment, draw up the technical documentation and the EU declaration of conformity, and affix the CE marking, before placing a magnet-labelling or recycled-content product on the market.",
          addressee="Persons responsible for placing products covered by Arts. 28 or 29 on the market",
          cls=B, trigger="placing a product covered by Art. 28 or Art. 29 on the Union market",
          frequency="per product model", verification="self-declaration",
          article="Art. 33(1)-(2)", when="From the date the Art. 28 or Art. 29 requirements apply to the product",
          drivers=["D1", "D7"], named=["auto", "clean"], reached=["batsol"],
          note="The assessment route is Annex IV of Directive 2009/125/EC -- internal design control, hence self-declaration -- unless the product also carries Art. 29, in which case the module comes from the Art. 29(2) rules and may require third-party involvement.")),

    ("CFM-01", "Member States shall not, for reasons relating to information for recycling or recycled content of permanent magnets or for reasons relating to information on the environmental footprint of critical raw material covered by this Regulation, prohibit, restrict or impede",
     "of critical raw materials that comply with this Regulation.",
     dict(measure_type="obligation", direction="add",
          duty="Do not prohibit, restrict or impede the marketing or putting into service of compliant products containing permanent magnets, or of compliant critical raw materials, on magnet-information, recycled-content or environmental-footprint grounds.",
          addressee="Member States",
          cls=S, trigger="products incorporating permanent magnets or critical raw materials that comply with the Regulation",
          frequency="continuous", verification="none",
          article="Art. 32(1)", when=WHEN_GENERAL,
          drivers=[], named=["auto", "clean"], reached=["batsol"],
          note="A free-movement clause: the operative verb binds the Member State, so it is an obligation on the state, not a right row -- even though the producer is who benefits.")),

    ("CREC-01", "Governments, industry associations and groupings of interested organisations that have developed and oversee certification schemes related to the sustainability of critical raw materials (scheme owners) may apply to have their schemes recognised by the Commission.",
     "",
     dict(measure_type="right", direction="add",
          benefit="A certification scheme owner may have its scheme recognised by the Commission against the Annex IV criteria, with the recognised coverage published in a public register -- and recognition feeds the Art. 6(1)(c) sustainability assessment for Strategic Projects.",
          addressee="Governments, industry associations and groupings owning critical raw materials sustainability certification schemes",
          cls=B, trigger="an application containing evidence of fulfilment of the Annex IV criteria",
          frequency="per scheme", verification="competent authority",
          article="Art. 30(1)-(2)", when=WHEN_GENERAL,
          value_drivers=["V3"], frictions=["F4"],
          named=UPSTREAM, reached=DOWNSTREAM,
          provision_id="crma-30",
          right_basis=dict(text="scheme owners) may apply to have their schemes recognised by the Commission",
                           kind="procedure"))),

    ("CREC-02", "Owners of recognised schemes shall inform the Commission without delay of any changes or updates related to the fulfilment of the criteria laid down in Annex IV",
     "The Commission shall assess whether such changes or updates affect the basis for the recognition and take appropriate action.",
     dict(measure_type="obligation", direction="add",
          duty="Tell the Commission without delay of any change or update to a recognised scheme bearing on the Annex IV criteria.",
          addressee="Owners of recognised certification schemes",
          cls=B, trigger="a change or update to the scheme affecting the Annex IV criteria",
          frequency="if it happens", verification="none",
          article="Art. 30(5)", when=WHEN_GENERAL,
          drivers=["D1"], named=UPSTREAM, reached=[],
          provision_id="crma-30",
          note="Backed by withdrawal: repeated failures by operators implementing the scheme trigger an examination under Art. 30(6), a remedial period of up to 12 months under Art. 30(7), and withdrawal of recognition under Art. 30(8).")),

    ("CPEN-01", "Member States shall lay down rules on penalties applicable to infringements of this Regulation and shall take all measures necessary to ensure that they are implemented.",
     "shall notify it, without delay, of any subsequent amendment affecting them.",
     dict(measure_type="obligation", direction="add",
          duty="Lay down effective, proportionate and dissuasive penalties for infringements of the Regulation, put them into effect, and notify them and any amendment to the Commission without delay.",
          addressee="Member States",
          cls=S, trigger="infringement of any obligation under the Regulation",
          frequency="one-off", verification="none",
          article="Art. 47", when="By 24 November 2025",
          drivers=["D6"], named=UPSTREAM, reached=DOWNSTREAM)),
]


# ---------------------------------------------------------------------------
# PROMOTIONS FROM THE SECOND PASS
#
# 36 provisions extract_crma_pass_b.py found and this file did not carry, each
# ruled `promote` in crma_rulings.PASS_B_ONLY. Built from the pass row rather
# than retyped, for the reason set out in extract_nzia.py: a retyped promotion
# drifts into this file's opinion of the provision while still verifying, and
# the drift is invisible.
def promoted_rows() -> list[dict]:
    import extract_crma_pass_b as passb
    import crma_rulings as rulings

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
        row["pass_origin"] = f"{rulings.PASS_FILE.removesuffix('.json')}:{pass_id}"
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

    print(f"crma: {len(rows)} rows")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")

    if write:
        (DATA / "crma.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written ../data/crma.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

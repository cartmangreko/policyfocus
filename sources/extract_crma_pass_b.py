"""
Critical Raw Materials Act (Regulation (EU) 2024/1252, consolidated 03.05.2024):
SECOND independent extraction pass. Writes sources/crma_pass_b.json.

    python3 extract_crma_pass_b.py --check   # report, write nothing
    python3 extract_crma_pass_b.py           # write crma_pass_b.json

METHOD, AND THE SAME HONEST CAVEAT AS NZIA'S
============================================
Written the way extract_nzia_pass_b.py was: a walk of the enacting terms
ARTICLE BY ARTICLE AND PARAGRAPH BY PARAGRAPH from Art. 5 to Art. 47, asking of
each numbered paragraph only whether it puts a duty on someone or hands someone
something. Pass A (data/crma.json) was written thematically and one row deep per
theme; this pass is one row per paragraph that binds. Ids are C-01..C-84 in the
act's order.

Pass A was written first, in this session, and was visible. That weakens the
agreement signal and not the disagreement signal. Same disclosure, same reason.

WHAT THE SWEEP FOUND THAT THE THEMATIC READ DID NOT
===================================================
Three whole articles the register has no row for:

  * Art. 9(2)-(9). Pass A carries Art. 9(1) -- designate single points of
    contact -- and nothing of what they must then do: the website, the sole
    contact, the named administrative unit that must stay reachable, electronic
    filing, no duplicate studies, dispute-settlement access.
  * Art. 18. Online accessibility of administrative information, the CRMA twin
    of NZIA Art. 7 which the register does carry (INF-01).
  * Art. 19. National exploration programmes -- the mapping, geochemical and
    geoscientific campaigns, and the free-access maps of mineral occurrences
    with more detail available on request. This is the act's entire upstream
    information layer.

And two provisions that bind firms directly and were missed:

  * Art. 45(1), second subparagraph: "Economic operators shall not be required
    to submit information in addition to the information provided in the
    context of the provisions listed in the first subparagraph." A ceiling on
    what Member States may ask of operators, and relief the register did not
    record.
  * Art. 43, amending Art. 4(5) of Regulation (EU) 2019/1020: CRMA products
    join the list requiring an economic operator ESTABLISHED IN THE UNION before
    they may be placed on the market. Pass A treated Arts. 40-43 as procedural.

TWO CLASSIFICATION SPLITS, TAKEN AS READ
========================================
C-04 (Art. 6(1)) and C-33 (Art. 17) both follow the operative verb to the
Commission where Pass A followed the object to the firm -- the same argument the
NZIA reconciliation had three times and lost three times. Taken here anyway
rather than pre-conceded: a second pass that anticipates the ruling is not a
second reading, and the ledger is where the argument gets settled.

ONE DATE CLAIM
==============
C-01/C-02 (Art. 5(1)) date the capacity and diversification benchmarks to 2030,
which is the only date in the provision. Pass A dated them to entry into force,
which is when the DUTY TO WORK TOWARDS them starts and not what the row commits
to. Stated as a claim for the reconciliation to test.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
ACT = "crma.txt"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1252-20240503"
OPERATIVE_ANCHOR = "Article 1 Subject matter and objectives"

EIF = "From entry into force, 23 May 2024 (Art. 49(1))"

B, S, C = "business", "state", "commission"
DOWN = ["batsol", "clean", "auto", "air"]
UP = ["waste", "alu", "steel"]


def O(**kw):
    kw["measure_type"] = "obligation"; return kw


def R(**kw):
    kw["measure_type"] = "right"; return kw


def I(**kw):
    kw["measure_type"] = "incentive"; return kw


ROWS: list[tuple] = [

    # ---------------------------------------------------------- benchmarks
    ("C-01", "Art. 5(1)(a)",
     "Union extraction capacity is capable of extracting the ores, minerals or concentrates needed to produce at least 10 %", "is capable of recycling significantly increasing amounts of each strategic raw material from waste;",
     O(duty="Raise Union capacity to extract 10%, process 40% and recycle 25% of annual consumption of each strategic raw material by 2030.",
       addressee="The Commission and Member States", cls=S, trigger="strategic raw materials listed in Annex I",
       frequency="continuous", verification="none", direction="add", when="By 2030 (Art. 5(1))",
       drivers=[], named=UP, reached=DOWN,
       note="DATE. The provision's only date is 2030. Pass A dated it to entry into force, which is when the duty to work towards it starts, not what the row commits to.")),

    ("C-02", "Art. 5(1)(b)",
     "diversify the Union’s imports of strategic raw materials with a view to ensuring that, by 2030", "no third country accounts for more than 65 % of the Union’s annual consumption of such a strategic raw material.",
     O(duty="Diversify imports so no single third country supplies more than 65% of Union annual consumption of any strategic raw material by 2030.",
       addressee="The Commission and Member States", cls=S, trigger="Union consumption at any relevant stage of processing",
       frequency="continuous", verification="none", direction="add", when="By 2030 (Art. 5(1))",
       drivers=[], named=UP, reached=DOWN)),

    ("C-03", "Art. 5(2)",
     "The Commission and Member States shall undertake efforts to incentivise technological progress and resource efficiency in order to moderate the expected increase in Union consumption of critical raw materials", "",
     O(duty="Work to moderate the expected increase in Union consumption of critical raw materials below the Art. 44(1) reference projection, through technological progress and resource efficiency.",
       addressee="The Commission and Member States", cls=S, trigger="the reference projection under Art. 44(1)",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=[], named=UP, reached=DOWN)),

    # ---------------------------------------------------- strategic projects
    ("C-04", "Art. 6(1)",
     "the Commission shall recognise as Strategic Projects raw material projects that meet the following criteria:", "the project would be mutually beneficial for the Union and the third country concerned by adding value in that third country.",
     O(duty="Recognise as Strategic Projects the raw material projects meeting all five criteria, assessed against the elements and evidence in Annex III.",
       addressee="The Commission", cls=C, trigger="an application meeting the Art. 6(1) criteria",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=["D3"], named=UP, reached=DOWN,
       note="Follows the operative verb to the Commission. Pass A follows the object -- the status recognition creates -- and files it as right/business.")),

    ("C-05", "Art. 6(3)",
     "The recognition of a project as a Strategic Project pursuant to this Article shall not affect the requirements applicable to the relevant project or project promoter under Union, national or international law.", "",
     O(duty="Continue to meet every requirement under Union, national and international law; Strategic Project recognition changes none of them.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="recognition as a Strategic Project",
       frequency="continuous", verification="competent authority", direction="add", when=EIF,
       drivers=[], named=UP, reached=[],
       note="The limit on the whole status. A register that carries the privileges of recognition and not this sentence overstates what the status buys.")),

    ("C-06", "Art. 7(1)",
     "Applications for recognition of a critical raw material project as a Strategic Project shall be submitted by the project promoter to the Commission.", "as well as measures to address the outcomes of the consultation.",
     O(duty="File an application carrying ten items, from evidence against the criteria and a UN Framework classification to a public-acceptance plan, an ownership statement, a business plan, a jobs and skills plan, a site-restoration plan, an alternative-locations assessment and an indigenous-peoples consultation plan.",
       addressee="Promoters applying for Strategic Project recognition", cls=B, trigger="an application for recognition",
       frequency="per application", verification="competent authority", direction="add", when=EIF,
       drivers=["D1", "D3"], named=UP, reached=DOWN)),

    ("C-07", "Art. 7(3)-(4)",
     "The Commission shall assess the applications referred to in paragraph 1 through an open call with regular cut-off dates.", "specifying which additional information is required.",
     O(duty="Run an open call with at least four cut-off dates a year and tell applicants within 30 days of the cut-off whether the application is complete.",
       addressee="The Commission", cls=C, trigger="applications for Strategic Project recognition",
       frequency="per cut-off date", verification="none", direction="add", when=EIF,
       drivers=["D5"], named=UP, reached=[],
       note="The application window itself. A promoter cannot plan a filing without it, and the register carries only the 90-day decision that follows.")),

    ("C-08", "Art. 7(8)",
     "On the basis of an objection by the Member State whose territory is concerned by a proposed project, the project shall not be considered for recognition as a Strategic Project.", "The Member State concerned shall substantiate its objection during the discussions referred to in paragraph 6.",
     O(duty="Accept that a single objection by the host Member State ends the application; the Member State must substantiate it before the Board.",
       addressee="Promoters of proposed Strategic Projects, and the host Member State", cls=B,
       trigger="an objection by the Member State whose territory is concerned", frequency="per application",
       verification="competent authority", direction="add", when=EIF,
       drivers=["D3"], named=UP, reached=[],
       note="A host-state veto over the whole route, and for projects in third countries the Commission may not approve without that country's explicit approval. Absent from the register.")),

    ("C-09", "Art. 7(9)",
     "adopt its decision on the recognition of the project as a Strategic Project within 90 days of acknowledging the completeness of the application", "",
     O(duty="Decide within 90 days of acknowledging completeness, give reasons, and notify the applicant, the Board and the territory concerned.",
       addressee="The Commission", cls=C, trigger="a complete application", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=UP, reached=[])),

    ("C-10", "Art. 7(10)",
     "the Commission may, on a case-by-case basis and no later than 20 days before the expiry of the time limit referred to in paragraph 9, extend that time limit by a maximum of 90 days", "",
     O(duty="Hold the 90-day decision deadline where the application's nature, complexity or size, or the number received, requires longer.",
       addressee="Promoters awaiting a recognition decision", cls=B, trigger="an exceptional case or too many applications before a cut-off",
       frequency="if it happens", verification="none", direction="rem", when=EIF,
       drivers=[], named=UP, reached=[])),

    ("C-11", "Art. 7(11)",
     "Before adopting a decision to withdraw recognition, the Commission shall provide the project promoter with reasons for its decision, the project promoter shall be given the opportunity to reply", "",
     R(benefit="Before recognition is withdrawn the promoter gets the Commission's reasons, an opportunity to reply, and a reply the Commission must take into account.",
       addressee="Promoters facing withdrawal of Strategic Project recognition", cls=B,
       trigger="a Commission finding that the criteria are no longer met or the application was materially incorrect",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=UP, reached=[],
       right_basis=dict(text="the project promoter shall be given the opportunity to reply and the Commission shall take into account the project promoter’s reply", kind="procedure"))),

    ("C-12", "Art. 7(12)",
     "Projects which are no longer recognised as Strategic Projects shall lose all rights connected to that status under this Regulation.", "",
     R(benefit="Strategic Project status and every right attached to it are lost when recognition ends.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="withdrawal of recognition",
       frequency="if it happens", verification="competent authority", direction="rem", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=UP, reached=[],
       right_basis=dict(text="Projects which are no longer recognised as Strategic Projects shall lose all rights connected to that status under this Regulation.", kind="conferral"))),

    ("C-13", "Art. 7(13)",
     "Strategic Projects that no longer fulfil the criteria laid down in Article 6(1) solely due to an update of Annex I shall be allowed to maintain their status", "",
     R(benefit="A project that falls out of the criteria only because Annex I moved keeps its status for three years.",
       addressee="Promoters affected by an update of Annex I", cls=B, trigger="an Annex I update that alone removes the criteria",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=UP, reached=[],
       right_basis=dict(text="shall be allowed to maintain their status as Strategic Projects for three years from the date of that update", kind="scope"))),

    ("C-14", "Art. 8(1)",
     "every two years after the date of recognition as a Strategic Project, submit a report to the Commission containing information on at least:", "progress in financing the Strategic Project, including information on public financial support.",
     O(duty="Report to the Commission every two years on implementation and permitting progress, delays and recovery plans, and financing progress including public support.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="recognition as a Strategic Project",
       frequency="every two years", verification="none", direction="add", when="Every two years from recognition",
       drivers=["D1", "D5"], named=UP, reached=[])),

    ("C-15", "Art. 8(2)",
     "The Commission may, where necessary, request additional information from project promoters relevant to the implementation of the Strategic Project", "",
     O(duty="Supply additional information on request so the Commission can check the criteria are still met.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="a Commission request", frequency="if it happens",
       verification="none", direction="add", when=EIF, drivers=["D1"], named=UP, reached=[])),

    ("C-16", "Art. 8(3)",
     "changes to the Strategic Project affecting its fulfilment of the criteria laid down in Article 6(1);", "changes in control of the undertakings involved in the Strategic Project on a lasting basis",
     O(duty="Notify changes affecting the recognition criteria and any lasting change of control over the undertakings involved.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="a change to the project or its control",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=UP, reached=[])),

    ("C-17", "Art. 8(5)",
     "The project promoter shall establish and regularly update the undertaking’s website or a dedicated project website", "It shall be available in a language or languages that can be easily understood by the local population.",
     O(duty="Run and update a free-access project website in a language the local population understands, carrying at least the environmental, social and economic impacts and benefits.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="recognition as a Strategic Project",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=["D1", "D5"], named=UP, reached=[])),

    # ------------------------------------------------------------ permitting
    ("C-18", "Art. 9(1)",
     "By 24 February 2025, Member States shall establish or designate one or more authorities as single points of contact.", "",
     O(duty="Establish or designate single points of contact, at most one per administrative level and value-chain stage.",
       addressee="Member States", cls=S, trigger="entry into application", frequency="one-off",
       verification="none", direction="add", when="By 24 February 2025", drivers=["D4"], named=UP, reached=[])),

    ("C-19", "Art. 9(2)",
     "it shall provide a simple, accessible website on which all points of contact, including their address and electronic means of communication, are clearly listed and categorised", "",
     O(duty="Publish a simple accessible website listing every point of contact with its address and electronic contact details, categorised by administrative level and value-chain stage.",
       addressee="Member States with more than one point of contact", cls=S, trigger="more than one point of contact designated",
       frequency="one-off", verification="none", direction="add", when=EIF, drivers=["D1", "D4"], named=UP, reached=[])),

    ("C-20", "Art. 9(3)-(4)",
     "shall be responsible for facilitating and coordinating the permit-granting process for critical raw material projects and providing information on the elements referred to in Article 18", "shall assist the project promoter in understanding any administrative matter relevant to the permit-granting process.",
     O(duty="Facilitate and coordinate the permit-granting process, provide the Art. 18 information, act as the sole point of contact, and help the promoter understand any administrative matter in the process.",
       addressee="Single points of contact", cls=S, trigger="a critical raw material project in permitting",
       frequency="per project", verification="none", direction="add", when=EIF,
       drivers=[], named=UP, reached=[])),

    ("C-21", "Art. 9(5)",
     "Project promoters of critical raw materials projects shall have the possibility to contact the relevant administrative unit, within the single point of contact, responsible for the tasks provided for in this Article.", "",
     R(benefit="A promoter can reach the named administrative unit handling its file, and that unit keeps its responsibilities until the promoter has been notified of any change.",
       addressee="Promoters of critical raw material projects", cls=B, trigger="a project in the permit-granting process",
       frequency="per project", verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=UP, reached=[],
       right_basis=dict(text="shall have the possibility to contact the relevant administrative unit, within the single point of contact, responsible for the tasks provided for in this Article", kind="conferral"))),

    ("C-22", "Art. 9(6)",
     "Project promoters shall be allowed to submit all documents relevant to the permit-granting process in electronic form.", "",
     O(duty="Accept all permit-granting documents in electronic form.",
       addressee="Member States and their permit-granting authorities", cls=S, trigger="any relevant document",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=["D4"], named=UP, reached=[])),

    ("C-23", "Art. 9(7)",
     "The Member States shall ensure that any valid studies carried out, or permits or authorisations issued, for a given critical raw material project are taken into account", "",
     O(duty="Re-run valid studies or re-obtain permits already issued for the same project.",
       addressee="Promoters of critical raw material projects", cls=B, trigger="a valid study, permit or authorisation already exists",
       frequency="per application", verification="competent authority", direction="rem", when=EIF,
       drivers=[], named=UP, reached=[])),

    ("C-24", "Art. 9(8)",
     "Member States shall ensure that applicants have easy access to information on and procedures for the settlement of disputes concerning the permit-granting process for critical raw materials projects", "",
     O(duty="Give applicants easy access to dispute-settlement information and procedures, including alternative dispute resolution where applicable.",
       addressee="Member States", cls=S, trigger="a permit-granting process for a critical raw material project",
       frequency="continuous", verification="none", direction="add", when=EIF, drivers=["D1"], named=UP, reached=[])),

    ("C-25", "Art. 10(2)",
     "Strategic Projects in the Union shall be considered to be of public interest or serving public health and safety, and may be considered to have an overriding public interest", "",
     R(benefit="Strategic Projects count as being of public interest or serving public health and safety, and may be treated as of overriding public interest, in the environmental derogations.",
       addressee="Promoters of Strategic Projects in the Union", cls=B, trigger="recognition as a Strategic Project",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=UP, reached=[],
       right_basis=dict(text="Strategic Projects in the Union shall be considered to be of public interest or serving public health and safety", kind="conferral"))),

    ("C-26", "Art. 10(3)",
     "project promoters and all authorities concerned shall ensure that that process is carried out in the most rapid way possible in accordance with Union and national law.", "",
     O(duty="Carry the permit-granting process out in the most rapid way Union and national law allow -- a duty on the promoter as much as on the authorities.",
       addressee="Promoters of Strategic Projects and all authorities concerned", cls=B, trigger="recognition as a Strategic Project",
       frequency="per project", verification="none", direction="add", when=EIF, drivers=[], named=UP, reached=[])),

    ("C-27", "Art. 10(4)",
     "Strategic Projects in the Union shall be granted the status of the highest national significance possible, where such a status exists in national law", "",
     R(benefit="A Strategic Project gets the highest national significance status national law provides, and is treated accordingly in permitting.",
       addressee="Promoters of Strategic Projects in the Union", cls=B, trigger="recognition, where such a status exists",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=UP, reached=[],
       right_basis=dict(text="Strategic Projects in the Union shall be granted the status of the highest national significance possible, where such a status exists in national law", kind="conferral"))),

    ("C-28", "Art. 10(5)",
     "All dispute resolution procedures, litigation, appeals and judicial remedies related to the permit-granting process and the issuance of permits for Strategic Projects", "Project promoters of Strategic Projects shall participate in such urgency procedures, where applicable.",
     R(benefit="Litigation and appeals over a Strategic Project's permits are treated as urgent wherever national law provides an urgency procedure.",
       addressee="Promoters of Strategic Projects in the Union", cls=B, trigger="litigation or appeal over the permit-granting process",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=UP, reached=[],
       right_basis=dict(text="shall be treated as urgent if and to the extent to which national law provides for such urgency procedures", kind="scope"))),

    ("C-29", "Art. 11(1)",
     "27 months for Strategic Projects involving extraction;", "15 months for Strategic Projects involving only processing or recycling.",
     O(duty="Complete Strategic Project permitting within 27 months for extraction and 15 months for processing or recycling only.",
       addressee="Member State permit-granting authorities", cls=S, trigger="a permit application for a Strategic Project",
       frequency="per application", verification="none", direction="add", when=EIF, drivers=["D5"], named=UP, reached=[])),

    ("C-30", "Art. 11(4)",
     "Member States may extend, before their expiry and on a case-by-case basis, the time limits referred to in:", "paragraph 1, point (b), and paragraph 2, point (b), by a maximum of three months.",
     O(duty="Hold the permitting time limits where the project's nature, complexity, location or size requires longer -- six months more for extraction, three for processing or recycling.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="an exceptional case turning on nature, complexity, location or size",
       frequency="if it happens", verification="competent authority", direction="rem", when=EIF,
       drivers=[], named=UP, reached=[])),

    ("C-31", "Art. 11(5)",
     "the determination of whether the Strategic Project is to be made subject to an assessment in accordance with Articles 5 to 10 of that Directive shall be made within 30 days", "",
     O(duty="Decide within 30 days of the developer submitting the required information whether the Strategic Project needs a full environmental impact assessment.",
       addressee="Member State competent authorities", cls=S, trigger="information submitted under Art. 4(4) of Directive 2011/92/EU",
       frequency="per project", verification="none", direction="add", when=EIF, drivers=["D5"], named=UP, reached=[])),

    ("C-32", "Art. 11(6)",
     "the single point of contact concerned shall acknowledge that the application is complete or, if the project promoter has not sent all the information required to process an application, request the project promoter to submit a complete application", "",
     O(duty="Acknowledge completeness within 45 days or say what is missing, and on a second pass ask only for evidence completing what was already identified.",
       addressee="Single points of contact", cls=S, trigger="receipt of a permit application for a Strategic Project",
       frequency="per application", verification="none", direction="add", when=EIF, drivers=["D5"], named=UP, reached=[])),

    ("C-33", "Art. 11(7)",
     "The schedule shall be published by the project promoter on the website referred to in Article 8(5).", "",
     O(duty="Publish the permitting schedule drawn up by the single point of contact on the project's own free-access website.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="a schedule drawn up under Art. 11(7)",
       frequency="per project", verification="none", direction="add", when=EIF, drivers=["D1"], named=UP, reached=[])),

    ("C-34", "Art. 12(1)",
     "the relevant project promoter shall request, no later than 30 days after the notification of the recognition as a Strategic Project", "within a period of time not exceeding 45 days from the date on which the project promoter submitted its request for an opinion.",
     O(duty="Request the environmental-impact-assessment scoping opinion within 30 days of being notified of recognition and before filing the application.",
       addressee="Promoters of Strategic Projects needing an environmental impact assessment", cls=B,
       trigger="an assessment required under Arts. 5 to 9 of Directive 2011/92/EU", frequency="per project",
       verification="competent authority", direction="add", when=EIF, drivers=["D1", "D3"], named=UP, reached=[])),

    ("C-35", "Art. 12(2)-(3)",
     "Member States shall ensure that a coordinated or a joint procedure fulfilling all the requirements of those Union legislative acts is applied.", "within 90 days of receiving all necessary information",
     O(duty="Run a coordinated or joint environmental procedure where duties arise simultaneously, and issue the reasoned conclusion within 90 days of receiving all necessary information.",
       addressee="Member States", cls=S, trigger="simultaneous assessment duties under two or more directives",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       drivers=["D5"], named=UP, reached=[])),

    ("C-36", "Art. 12(6)",
     "Paragraph 1 shall not apply to the permit-granting process for Strategic Projects that had entered in the permit-granting process before being recognised as a Strategic Project.", "",
     O(duty="Request the scoping opinion within 30 days of recognition.",
       addressee="Promoters whose project was already in permitting before recognition", cls=B,
       trigger="the project entered the permit-granting process before being recognised", frequency="per project",
       verification="competent authority", direction="rem", when=EIF, drivers=[], named=UP, reached=[])),

    ("C-37", "Art. 13(1)",
     "National, regional and local authorities responsible for preparing plans, including zoning, spatial plans and land use plans, shall consider including in such plans, where appropriate, provisions for the development of critical raw materials projects.", "",
     O(duty="Consider making room for critical raw materials projects in zoning, spatial and land use plans, with priority to built, industrial, brownfield and mined land.",
       addressee="National, regional and local planning authorities", cls=S, trigger="preparation of plans",
       frequency="per plan", verification="none", direction="add", when=EIF, drivers=["D1"], named=UP, reached=[])),

    ("C-38", "Art. 13(2)",
     "Where plans including provisions for the development of critical raw material projects are subject to an assessment pursuant to Directive 2001/42/EC", "those impacts shall also be covered in the combined assessment.",
     O(duty="Combine the strategic environmental and habitats assessments for plans making room for critical raw materials projects, covering water bodies and the marine environment.",
       addressee="Member States", cls=S, trigger="a plan subject to both assessments", frequency="per plan",
       verification="competent authority", direction="add", when=EIF, drivers=[], named=UP, reached=[])),

    ("C-39", "Art. 14(2)",
     "All decisions adopted pursuant to this Section shall be made publicly available in an easily understandable manner", "",
     O(duty="Publish every permitting decision in an easily understandable form, with all decisions on one project on one website.",
       addressee="Member States and their authorities", cls=S, trigger="a decision under the permitting section",
       frequency="per decision", verification="none", direction="add", when=EIF, drivers=["D1"], named=UP, reached=[])),

    ("C-40", "Art. 15(2)",
     "The Member State whose territory is concerned by a Strategic Project shall take measures to facilitate its timely and effective implementation.", "further increase the ability of project promoters to ensure the meaningful involvement and active participation of the communities affected by the Strategic Project.",
     O(duty="Take measures to facilitate timely implementation of a Strategic Project, including help with administrative and reporting compliance and with community involvement.",
       addressee="Member States hosting a Strategic Project", cls=S, trigger="a Strategic Project on the territory",
       frequency="per project", verification="none", direction="add", when=EIF, drivers=[], named=UP, reached=[])),

    ("C-41", "Art. 16(1)",
     "at the request of a project promoter of a Strategic Project, discuss and provide advice on how the financing of its project can be completed", "",
     R(benefit="A Strategic Project promoter can call in the Board's financing subgroup on how to close the project's financing, across private sources, IFIs, national instruments and Union programmes.",
       addressee="Promoters of Strategic Projects", cls=B, trigger="a request by the promoter", frequency="per project",
       verification="none", direction="add", when=EIF, value_drivers=["V4"], frictions=["F3"], named=UP, reached=[],
       right_basis=dict(text="at the request of a project promoter of a Strategic Project, discuss and provide advice on how the financing of its project can be completed", kind="procedure"))),

    ("C-42", "Art. 17(1)-(4)",
     "The Commission shall set up a system to facilitate the conclusion of offtake agreements related to Strategic Projects", "the Commission shall bring project promoters of Strategic Projects in contact with potential offtakers relevant for their project.",
     O(duty="Set up and run a system where offtakers bid volumes, qualities, prices and durations, promoters post offers, and the Commission introduces the two sides.",
       addressee="The Commission", cls=C, trigger="Strategic Projects seeking offtake", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=["D4"], named=UP, reached=DOWN,
       note="Follows the operative verb to the Commission. Pass A follows the object -- demand-side access a developer did not have -- and files it as an incentive.")),

    ("C-43", "Art. 18(1)",
     "Member States shall provide the following information on administrative processes relevant to critical raw material projects online", "business support services, including but not limited to corporate tax declaration, local tax laws or labour law.",
     O(duty="Publish online and centrally the points of contact, the permit-granting and related processes, financing and investment services, funding possibilities, and business support services.",
       addressee="Member States", cls=S, trigger="administrative processes relevant to critical raw material projects",
       frequency="one-off, kept updated", verification="none", direction="add", when=EIF,
       drivers=["D1", "D4"], named=UP, reached=[],
       note="The CRMA twin of NZIA Art. 7, which the register carries as INF-01. Missing here.")),

    ("C-44", "Art. 18(2)",
     "The Commission shall, in a centralised and easily accessible manner, provide online information on administrative processes relevant to the recognition of Strategic Projects and on the benefits of such recognition.", "",
     O(duty="Publish centralised online information on how Strategic Project recognition works and what it is worth.",
       addressee="The Commission", cls=C, trigger="the Strategic Project recognition process", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=["D1", "D4"], named=UP, reached=[])),

    # ------------------------------------------------------------ exploration
    ("C-45", "Art. 19(1)-(2)",
     "By 24 May 2025, each Member State shall draw up a national programme for general exploration targeted at critical raw materials and carrier minerals", "reprocessing of existing geoscientific survey data to check for unidentified mineral occurrences containing critical raw materials and carrier minerals of critical raw materials.",
     O(duty="Draw up and review a national exploration programme covering mineral mapping, geochemical campaigns, geoscientific surveys and reprocessing of existing survey data.",
       addressee="Member States", cls=S, trigger="critical raw materials and carrier minerals on the territory",
       frequency="reviewed at least every five years", verification="none", direction="add", when="By 24 May 2025",
       drivers=["D1", "D4"], named=UP, reached=DOWN,
       note="The act's entire upstream information layer, and the register has no row in it.")),

    ("C-46", "Art. 19(6)",
     "Member States shall make maps that show basic information on mineral occurrences containing critical raw materials gathered through the measures set out in the national programmes", "shall be made available upon request.",
     O(duty="Publish free-access maps of mineral occurrences with UN Framework classification where applicable, and release processed geophysical and geochemical data and large-scale mapping on request.",
       addressee="Member States", cls=S, trigger="occurrences identified through the national exploration programme",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=["D1", "D4"], named=UP, reached=DOWN,
       note="What a prospector or a processor can actually obtain about Union deposits. The 'upon request' limb is a faculty for firms and there is nothing on it in the register.")),

    # --------------------------------------------------- monitoring and stocks
    ("C-47", "Art. 20(4)",
     "The Commission shall make publicly available on a free-access website and regularly update a monitoring dashboard", "general suggestions for suitable mitigation strategies to decrease supply risk",
     O(duty="Publish and keep updated a free-access monitoring dashboard carrying the parameter trends, the supply-risk calculation, and where appropriate mitigation suggestions.",
       addressee="The Commission", cls=C, trigger="monitoring of supply risks", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=["D1", "D4"], named=UP, reached=DOWN,
       note="The published data Art. 24(3) then lets a large company rely on when its suppliers do not answer. The register carries the fallback and not the source it points at.")),

    ("C-48", "Art. 21(1)",
     "Member States shall, in their reports submitted pursuant to Article 45, provide information to the Commission on new or existing critical raw material project on their territory", "",
     O(duty="Report new and existing critical raw material projects on the territory, classified under the UN Framework Classification for Resources.",
       addressee="Member States", cls=S, trigger="critical raw material projects on the territory", frequency="annual",
       verification="none", direction="add", when=EIF, drivers=["D1", "D5"], named=UP, reached=[])),

    ("C-49", "Art. 21(2)",
     "Member States shall identify key market operators along the critical raw materials value chain established in their territory", "without delay notify the Commission of major events that may hinder the regular operations of the activities of key market operators.",
     O(duty="Identify key market operators, monitor them through public data and proportionate surveys, report the results, and notify the Commission without delay of major disruptive events.",
       addressee="Member States", cls=S, trigger="key market operators established on the territory", frequency="recurring",
       verification="none", direction="add", when=EIF, drivers=["D4", "D5"], named=UP, reached=DOWN)),

    ("C-50", "Art. 21(2), third subparagraph",
     "They shall submit such data only to the extent that it is already available to them.", "it shall provide the requesting Member State with reasons therefor.",
     O(duty="Answer a Member State monitoring survey with the data already held, and give reasons for a refusal or an unavailability claim.",
       addressee="Key market operators along the critical raw materials value chain", cls=B,
       trigger="a survey under Art. 21(2)(a)", frequency="recurring", verification="none", direction="add",
       when=EIF, drivers=["D1", "D5"], named=UP, reached=DOWN)),

    ("C-51", "Art. 21(2), third subparagraph",
     "Key market operators may refuse to submit data requested pursuant to point (a) of the first subparagraph if the sharing of such data would lead to the disclosure of trade or business secrets.", "",
     R(benefit="A key market operator may refuse a monitoring request that would disclose trade or business secrets, and never has to generate data it does not hold.",
       addressee="Key market operators along the critical raw materials value chain", cls=B,
       trigger="a request that would disclose trade or business secrets", frequency="if it happens",
       verification="none", direction="add", when=EIF, value_drivers=["V3"], frictions=["F1"], named=UP, reached=DOWN,
       right_basis=dict(text="Key market operators may refuse to submit data requested pursuant to point (a) of the first subparagraph if the sharing of such data would lead to the disclosure of trade or business secrets.", kind="scope"))),

    ("C-52", "Art. 21(3)",
     "Member States shall transmit the data collated pursuant to paragraph 2, points (a) and (b), of this Article to national statistical authorities and to Eurostat", "",
     O(duty="Pass the collated monitoring data to national statistical authorities and Eurostat, and designate the authority responsible for doing so.",
       addressee="Member States", cls=S, trigger="data collated under Art. 21(2)", frequency="recurring",
       verification="none", direction="add", when=EIF, drivers=["D4"], named=UP, reached=[],
       note="Where an operator's survey answers actually end up. The register records the duty to answer and not the onward transmission.")),

    ("C-53", "Art. 22(1)-(2)",
     "submit to the Commission information on the state of their strategic stocks of strategic raw materials", "unless sharing such information jeopardises the protection of trade or business secrets or other sensitive, confidential or classified information.",
     O(duty="Report national strategic stock levels in tonnes and as a share of consumption, their chemical form and purity, their five-year evolution, and the rules for release and distribution.",
       addressee="Member States", cls=S, trigger="strategic stocks held by public authorities or on their behalf",
       frequency="annual", verification="none", direction="add", when=EIF, drivers=["D1", "D5"], named=UP, reached=DOWN)),

    ("C-54", "Art. 23(4)",
     "the Commission and the Board shall give particular weight to the need to maintain and promote incentives for private operators, which rely on strategic raw materials as inputs, to constitute their own strategic stocks", "",
     O(duty="Give particular weight, when opining on national stocks, to keeping private operators' incentives to hold their own strategic stocks and manage their own supply-risk exposure.",
       addressee="The Commission and the Board", cls=C, trigger="preparing opinions under Art. 23(3)",
       frequency="every two years", verification="none", direction="add", when=EIF,
       drivers=[], named=UP, reached=DOWN,
       note="The provision that protects a private stockholder from being crowded out by state stockpiling. It is the only thing in the stocks articles that speaks to firms at all.")),

    ("C-55", "Art. 24(1)",
     "Member States shall identify the large companies operating on their territory that use strategic raw materials to manufacture batteries for energy storage and e-mobility", "rocket launchers, satellites or advanced chips.",
     O(duty="Identify the large companies on the territory using strategic raw materials to make the listed battery, hydrogen, renewable, aerospace, traction, heat pump, electronics, robotics and chip products.",
       addressee="Member States", cls=S, trigger="an update of the list of strategic raw materials", frequency="one-off, then per list update",
       verification="none", direction="add", when="By 24 May 2025", drivers=["D4"], named=DOWN, reached=UP)),

    ("C-56", "Art. 24(2)",
     "carry out a risk assessment of their raw materials supply chain of strategic raw materials, including:", "an assessment of their vulnerabilities to supply disruptions.",
     O(duty="Carry out at least every three years a supply-chain risk assessment mapping extraction, processing and recycling, analysing what could affect supply, and assessing vulnerability to disruption.",
       addressee="Large companies identified under Art. 24(1)", cls=B, trigger="identification by a Member State",
       frequency="every three years", verification="self-declaration", direction="add",
       when="First assessment following identification, from 24 May 2025", drivers=["D1", "D5"], named=DOWN, reached=UP)),

    ("C-57", "Art. 24(3)",
     "they may carry out their risk assessment on the basis of the information published by the Commission pursuant to Article 20(4), or otherwise publicly available information", "",
     O(duty="Obtain the supply-chain information from suppliers in order to run the risk assessment.",
       addressee="Large companies subject to the Art. 24(2) assessment", cls=B, trigger="suppliers not providing the information on request",
       frequency="every three years", verification="self-declaration", direction="rem", when=EIF,
       drivers=[], named=DOWN, reached=UP)),

    ("C-58", "Art. 24(4)",
     "large companies as referred to under paragraph 1 shall take efforts to mitigate those vulnerabilities", "",
     O(duty="Take mitigating action where significant vulnerabilities are found, including assessing diversification and substitution.",
       addressee="Large companies subject to the Art. 24(2) assessment", cls=B, trigger="significant vulnerabilities detected",
       frequency="every three years", verification="self-declaration", direction="add", when=EIF,
       drivers=["D1"], named=DOWN, reached=UP)),

    ("C-59", "Art. 24(5)",
     "Large companies as referred to in paragraph 1 may present a report to their board of directors containing the results of the risk assessment referred to in paragraph 2", "",
     R(benefit="A large company may take the risk assessment to its own board, with the sources, the risks found and the mitigation planned -- and does not have to unless its Member State requires it.",
       addressee="Large companies identified under Art. 24(1)", cls=B, trigger="completion of the Art. 24(2) assessment",
       frequency="every three years", verification="self-declaration", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=DOWN, reached=UP,
       right_basis=dict(text="Large companies as referred to in paragraph 1 may present a report to their board of directors containing the results of the risk assessment referred to in paragraph 2", kind="procedure"),
       note="The permissive limb Art. 24(6) then lets a Member State make compulsory. The register carries the compulsory version and not the default, which is the one that applies everywhere else.")),

    ("C-60", "Art. 24(6)",
     "Member States may require large companies as referred to in paragraph 1 to present to their board of directors the report referred to in paragraph 5", "",
     O(duty="Present the risk-assessment report and the supplier information requests to the board of directors.",
       addressee="Large companies in Member States exercising the Art. 24(6) option", cls=B,
       trigger="a Member State requiring board presentation", frequency="every three years",
       verification="self-declaration", direction="add", when=EIF, drivers=["D1", "D3"], named=DOWN, reached=UP)),

    ("C-61", "Art. 25(1)-(4)",
     "The Commission shall set up and operate a system to aggregate the demand of interested undertakings consuming strategic raw materials established in the Union", "Participation in the system referred to in paragraph 3, point (b) shall be open and transparent to all interested undertakings established in the Union.",
     O(duty="Set up and operate an open, transparent demand-aggregation system covering unprocessed and processed strategic raw materials, after assessing the competition impact and setting minimum participation volumes with SMEs in mind.",
       addressee="The Commission", cls=C, trigger="demand from Union undertakings consuming strategic raw materials",
       frequency="continuous", verification="none", direction="add", when=EIF, drivers=["D4"], named=UP, reached=DOWN)),

    ("C-62", "Art. 25(5)",
     "Union undertakings participating in the system referred to in paragraph 1 may, on a transparent basis, jointly negotiate the purchase", "Participating Union undertakings shall comply with Union law, including Union competition law.",
     R(benefit="Participating undertakings may jointly negotiate purchases, prices and terms included, to win better conditions or head off shortages, within competition law.",
       addressee="Union undertakings consuming strategic raw materials", cls=B, trigger="participation in the demand-aggregation system",
       frequency="per purchase", verification="none", direction="add", when=EIF,
       value_drivers=["V2"], frictions=["F5"], named=DOWN, reached=UP,
       right_basis=dict(text="may, on a transparent basis, jointly negotiate the purchase, including the prices or other terms and conditions of the purchasing agreement or use joint purchasing in order to achieve better conditions with their suppliers or to prevent shortages", kind="conferral"))),

    ("C-63", "Art. 25(6)",
     "Entities shall be excluded from participating in demand aggregation and joint purchasing as well as from participating as suppliers or service providers if they are:", "targeted by such Union restrictive measures.",
     O(duty="Stay out of demand aggregation and joint purchasing, as participant, supplier or service provider, where sanctioned or owned, controlled by or acting for a sanctioned person.",
       addressee="Entities targeted by Union restrictive measures and those they control", cls=B,
       trigger="being targeted by measures under Art. 215 TFEU or controlled by such a target", frequency="continuous",
       verification="competent authority", direction="add", when=EIF, drivers=[], named=UP, reached=DOWN)),

    # ------------------------------------------------------------ circularity
    ("C-64", "Art. 26(1)",
     "adopt and implement, or include in, national programmes containing measures designed to:", "where relevant, support the use of Union quality standards for recycling processes of waste streams containing critical raw materials.",
     O(duty="Adopt and run national circularity programmes across nine measures, from resource efficiency and re-use to collection and processing of critical-raw-material-bearing waste, recycled content in procurement, recycling technology, skills, extended producer responsibility modulation, waste export control and quality standards.",
       addressee="Member States", cls=S, trigger="entry into force of the Art. 26(7) implementing act",
       frequency="one-off, reviewed within five years", verification="none",
       direction="add", when="Within two years of the Art. 26(7) implementing act",
       drivers=["D1"], named=["waste"], reached=UP + DOWN)),

    ("C-65", "Art. 26(3)",
     "the introduction of financial incentives, such as discounts, monetary rewards or deposit-refund systems, to encourage the preparation for re-use and re-use of products with relevant critical raw materials recovery potential", "",
     I(benefit="National circularity programmes may pay for circularity directly -- discounts, monetary rewards or deposit-refund systems for re-use, and for the collection and treatment of waste from products with recovery potential.",
       addressee="Holders and collectors of products and waste with critical raw materials recovery potential", cls=B,
       trigger="a Member State choosing to introduce the incentives in its programme", frequency="per scheme",
       verification="none", direction="add", when=EIF, value_drivers=["V1"], frictions=["F2"], named=["waste"], reached=UP,
       opportunity_basis=dict(text="the introduction of financial incentives, such as discounts, monetary rewards or deposit-refund systems", kind="existence"),
       note="The only support instrument in the act, and it is optional for the Member State. Recorded as an incentive whose existence is conditional rather than left out because it is conditional.")),

    ("C-66", "Art. 26(5)",
     "Member States shall identify separately, and report, the quantities of components containing relevant amounts of critical raw materials removed from waste electrical and electronic equipment", "",
     O(duty="Identify and report separately the critical-raw-material-bearing components removed from waste electrical and electronic equipment and the materials recovered from it.",
       addressee="Member States", cls=S, trigger="WEEE reporting under Directive 2012/19/EU", frequency="annual",
       verification="none", direction="add", when="First full calendar year after the implementing act",
       drivers=["D1", "D4", "D5"], named=["waste"], reached=UP)),

    ("C-67", "Art. 27(1)",
     "shall provide to the competent authority as defined in Article 3, point (27), of that Directive a preliminary economic assessment study regarding the potential recovery of critical raw materials", "the extractive waste being generated or, where considered more effective, from the extracted volume prior to it becoming waste.",
     O(duty="Produce and file a preliminary economic assessment study on recovering critical raw materials from stored and newly generated extractive waste.",
       addressee="Operators of extractive waste facilities under Directive 2006/21/EC", cls=B,
       trigger="an obligation to draw up a waste management plan under Art. 5 of Directive 2006/21/EC",
       frequency="one-off", verification="competent authority", direction="add",
       when="By 24 November 2026; new facilities with their waste management plan",
       drivers=["D1", "D3", "D4"], named=["waste", "alu", "steel"], reached=UP)),

    ("C-68", "Art. 27(1), second subparagraph",
     "Operators shall be exempt from the obligation laid down in the first subparagraph of this paragraph where they can demonstrate to the competent authority", "",
     O(duty="Produce the preliminary economic assessment study.",
       addressee="Operators whose extractive waste holds no technically recoverable critical raw materials", cls=B,
       trigger="demonstrating that to the competent authority with a high degree of certainty", frequency="one-off",
       verification="competent authority", direction="rem", when=EIF, drivers=[], named=["waste"], reached=[])),

    ("C-69", "Art. 27(2)",
     "The study referred to in paragraph 1 shall at least include an estimation of the quantities and concentrations of critical raw materials contained in the extractive waste", "Operators shall specify the methods used to estimate those quantities and concentrations.",
     O(duty="Put quantities and concentrations, an assessment of technical and economic recoverability, and the estimation methods used into the study.",
       addressee="Operators of extractive waste facilities", cls=B, trigger="the Art. 27(1) study", frequency="one-off",
       verification="competent authority", direction="add", when=EIF, drivers=["D1", "D4"], named=["waste"], reached=UP,
       note="The content specification is what makes the study expensive, and it is separately stated from the duty to produce one.")),

    ("C-70", "Art. 27(8)",
     "Where such factors inhibit the activities, the Member State authorities shall seek the cooperation of the operator or owner of the extractive waste facility.", "",
     O(duty="Cooperate with the Member State's sampling and characterisation of closed extractive waste facilities where national property, mineral or environmental law prevents the authority acting alone.",
       addressee="Operators and owners of closed extractive waste facilities", cls=B,
       trigger="national legal constraints on the Member State's Art. 27(7) activities", frequency="if it happens",
       verification="competent authority", direction="add", when=EIF, drivers=[], named=["waste"], reached=[],
       note="A duty that lands on a former operator of a CLOSED facility -- a party that may have no other obligation under the act at all.")),

    # -------------------------------------------------------- magnets, footprint
    ("C-71", "Art. 28(1)",
     "shall ensure that those products bear a conspicuous, clearly legible and indelible label indicating:", "ferrite.",
     O(duty="Label the listed products with whether they contain permanent magnets and which of the four magnet types.",
       addressee="Anyone placing the listed products on the Union market", cls=B, trigger="placing a listed product on the market",
       frequency="per product model", verification="self-declaration", direction="add",
       when="Two years after the labelling implementing act; 24 May 2029 for MRI devices, motor vehicles and category L vehicles",
       drivers=["D1", "D7"], named=["auto", "clean"], reached=["batsol"])),

    ("C-72", "Art. 28(3)-(4)",
     "shall ensure that a data carrier is present on or in the product.", "without prejudice to the provision of information to treatment facilities pursuant to Article 15(1) of Directive 2012/19/EU.",
     O(duty="Put a data carrier on or in the product linked to a unique identifier giving the responsible person, the weight, location and composition of each magnet including coatings, glues and additives, and the steps and tools for safe removal.",
       addressee="Anyone placing listed products containing permanent magnets on the market", cls=B,
       trigger="placing a listed product with a covered magnet type on the market", frequency="per product model",
       verification="self-declaration", direction="add", when="Two years after the labelling implementing act",
       drivers=["D1", "D4", "D7"], named=["auto", "clean"], reached=["batsol"])),

    ("C-73", "Art. 28(5)-(6)",
     "For products where the incorporated permanent magnets are exclusively contained in one or more electric motors incorporated in the product", "the information referred to in paragraph 4 shall be included in that product passport.",
     O(duty="Give magnet information at electric-motor level where the magnets sit only in motors, and put the information in the product passport where another Union act requires one.",
       addressee="Anyone placing listed products containing permanent magnets on the market", cls=B,
       trigger="magnets contained exclusively in electric motors, or a product passport required by another act",
       frequency="per product model", verification="self-declaration", direction="rem", when=EIF,
       drivers=[], named=["auto", "clean"], reached=["batsol"],
       note="Two simplifications inside the magnet regime: a coarser disclosure where the magnets are all in motors, and one passport instead of two. The register carries the burden and not the relief.")),

    ("C-74", "Art. 28(7)",
     "shall ensure that information referred to in paragraph 4 is complete, up-to-date, and accurate and remains available for a period at least equal to the product’s typical lifetime plus 10 years", "The information referred to in paragraph 4 shall be accessible to repairers, recyclers, market surveillance authorities and customs authorities.",
     O(duty="Keep the magnet information complete, current and accurate for the product's typical lifetime plus ten years, surviving insolvency or exit from the Union, and accessible to repairers, recyclers, market surveillance and customs.",
       addressee="Anyone placing listed products containing permanent magnets on the market", cls=B,
       trigger="a listed product with a magnet placed on the market", frequency="continuous",
       verification="competent authority", direction="add", when="Two years after the labelling implementing act",
       drivers=["D1", "D5"], named=["auto", "clean"], reached=["batsol"])),

    ("C-75", "Art. 28(8)-(9), 28(11)",
     "Where information requirements relating to the recycling of permanent magnets are established in Union harmonisation legislation for any of the products listed in paragraph 1", "vehicles produced in small series, as defined in Article 3, point (30), of Regulation (EU) 2018/858.",
     O(duty="Carry the permanent-magnet label, data carrier and information.",
       addressee="Makers of defence and space products, special purpose vehicles, multi-stage type-approved parts and small-series vehicles, and products covered by other Union harmonisation legislation",
       cls=B, trigger="another Union act setting magnet recycling information requirements, or one of the named vehicle and defence exclusions",
       frequency="per product model", verification="none", direction="rem", when=EIF,
       drivers=[], named=["auto"], reached=[])),

    ("C-76", "Art. 29(1)",
     "shall make publicly available on a free-access website the share of neodymium, dysprosium, praseodymium, terbium, boron, samarium, nickel and cobalt recovered from post-consumer waste present in the permanent magnets", "",
     O(duty="Publish on a free-access website the post-consumer recycled share of the eight named elements in the product's permanent magnets, once total magnet weight passes 0,2 kg.",
       addressee="Anyone placing listed products with more than 0,2 kg of covered magnets on the market", cls=B,
       trigger="total covered magnet weight above 0,2 kg", frequency="per product model",
       verification="self-declaration", direction="add",
       when="By 24 May 2027 or two years after the Art. 29(2) delegated act, whichever is later",
       drivers=["D1", "D4"], named=["auto", "clean"], reached=["batsol", "waste"])),

    ("C-77", "Art. 29(3)",
     "laying down minimum shares for neodymium, dysprosium, praseodymium, terbium, boron, samarium, nickel and cobalt recovered from post-consumer waste that must be present in the permanent magnet", "",
     O(duty="Meet the minimum post-consumer recycled shares for the eight named elements in the magnets of listed products.",
       addressee="Anyone placing listed products with permanent magnets on the market", cls=B,
       trigger="delegated acts setting the minimum shares", frequency="per product model",
       verification="accredited third party", direction="add",
       when="Delegated acts after the Art. 29(2) rules and by 31 December 2031 at the latest",
       drivers=["D1", "D2", "D4"], named=["auto", "clean"], reached=["batsol", "waste"])),

    ("C-78", "Art. 29(5)",
     "natural and legal persons placing on the market products referred to in paragraph 1 shall ensure that their customers have access to the information referred to in paragraph 1 before being bound by a sales contract.", "",
     O(duty="Give customers access to the recycled-content information before they are bound by a sales contract, and display nothing likely to mislead them about it.",
       addressee="Anyone placing listed products with permanent magnets on the market", cls=B,
       trigger="offering a listed product for sale or displaying it commercially", frequency="continuous",
       verification="competent authority", direction="add", when="From the date Art. 29(1) applies",
       drivers=["D1"], named=["auto", "clean"], reached=["batsol"])),

    ("C-79", "Art. 30(1)",
     "may apply to have their schemes recognised by the Commission.", "",
     R(benefit="A certification scheme owner may have its scheme recognised against the Annex IV criteria, with the recognised coverage published in a public register.",
       addressee="Governments, industry associations and groupings owning certification schemes", cls=B,
       trigger="an application with evidence of the Annex IV criteria", frequency="per scheme",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=UP, reached=DOWN,
       right_basis=dict(text="scheme owners) may apply to have their schemes recognised by the Commission", kind="procedure"))),

    ("C-80", "Art. 30(5)-(7)",
     "Owners of recognised schemes shall inform the Commission without delay of any changes or updates related to the fulfilment of the criteria", "it may grant the scheme owner an appropriate period, of not longer than 12 months, within which to take remedial action.",
     O(duty="Tell the Commission without delay of changes bearing on the Annex IV criteria, and take remedial action within the period set -- at most 12 months -- where deficiencies are found.",
       addressee="Owners of recognised certification schemes", cls=B, trigger="a change to the scheme, or deficiencies identified by the Commission",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       drivers=["D1", "D6"], named=UP, reached=[])),

    ("C-81", "Art. 31(6)-(7)",
     "shall make available an environmental footprint declaration.", "a web link providing access to a public version of the study supporting the environmental footprint declaration results.",
     O(duty="Publish an environmental footprint declaration per critical raw material type once calculation rules exist, naming the responsible person, the material, the countries of extraction, processing, refining and recycling, the footprint, its performance class, and a link to the supporting study.",
       addressee="Anyone placing critical raw materials on the Union market", cls=B,
       trigger="calculation and verification rules adopted for that material", frequency="per material type",
       verification="accredited third party", direction="add", when="From adoption of the rules for the material",
       drivers=["D1", "D2", "D4"], named=UP, reached=DOWN)),

    ("C-82", "Art. 32(2)",
     "At trade fairs, exhibitions, demonstrations or similar events, Member States shall not prevent the showing of products incorporating permanent magnets or of critical raw materials which do not comply with this Regulation", "",
     R(benefit="Non-compliant products and materials may still be shown at trade fairs and demonstrations, provided a visible sign says they are non-compliant and cannot be marketed until they are.",
       addressee="Exhibitors of products incorporating permanent magnets and of critical raw materials", cls=B,
       trigger="a trade fair, exhibition, demonstration or similar event", frequency="if it happens",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=["auto", "clean"], reached=["batsol"],
       right_basis=dict(text="Member States shall not prevent the showing of products incorporating permanent magnets or of critical raw materials which do not comply with this Regulation, provided that a visible sign clearly indicates that such products or critical raw materials do not comply", kind="scope"))),

    ("C-83", "Art. 43(1)",
     "This Article applies only in relation to products that are subject to Regulations (EU) No 305/2011", "",
     O(duty="Have an economic operator established in the Union responsible for the product under Art. 4 of Regulation (EU) 2019/1020 before placing it on the market.",
       addressee="Manufacturers, importers and authorised representatives of products covered by this Regulation", cls=B,
       trigger="a product subject to Regulation (EU) 2024/1252 placed on the Union market", frequency="per product model",
       verification="competent authority", direction="add", when=EIF,
       drivers=["D1", "D7"], named=["auto", "clean"], reached=["batsol"],
       note="Art. 43 adds this Regulation to the list in Art. 4(5) of the market surveillance Regulation, which is the provision requiring a responsible economic operator ESTABLISHED IN THE UNION. Pass A read Arts. 40-43 as procedural amendments; this one creates an establishment requirement for every covered product.")),

    ("C-84", "Art. 45(1), second subparagraph",
     "Economic operators shall not be required to submit information in addition to the information provided in the context of the provisions listed in the first subparagraph.", "",
     O(duty="Supply information beyond what the reporting provisions listed in Art. 45(1) already require.",
       addressee="Economic operators along the critical raw materials value chain", cls=B,
       trigger="a Member State compiling its annual report to the Commission", frequency="annual",
       verification="none", direction="rem", when="By 24 May 2026 and annually thereafter",
       drivers=[], named=UP, reached=DOWN,
       note="A ceiling on what may be asked of operators when a Member State assembles its report. Real relief, stated once, and the register has nothing on it.")),
]


def slice_span(text: str, start: str, end: str, rid: str) -> str:
    i = text.find(start)
    if i == -1:
        raise LookupError(f"{rid}: START anchor not found: {start[:70]!r}")
    if text.count(start) > 1:
        raise LookupError(f"{rid}: START anchor is ambiguous, {text.count(start)} matches: {start[:70]!r}")
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
    for rid, article, start, end, meta in ROWS:
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
            "addressee": meta["addressee"], "class": meta["cls"], "trigger": meta["trigger"],
            "frequency": meta["frequency"], "verification": meta["verification"],
            "direction": meta["direction"], "article": article, "when": meta["when"],
            "source_text": span, "drivers": meta.get("drivers", []),
            "sectors_named": meta["named"], "sectors_reached": meta["reached"],
            "provision_id": None, "file": "crma", "source_url": SOURCE_URL,
            "value_drivers": meta.get("value_drivers", []),
            "access_frictions": meta.get("frictions", []),
        })
        if meta.get("note"):
            row["benefit_axis_note"] = meta["note"]
        if meta.get("right_basis"):
            row["right_basis"] = meta["right_basis"]
        if meta.get("opportunity_basis"):
            row["opportunity_basis"] = meta["opportunity_basis"]
        rows.append(row)
    return rows, errors


def main() -> int:
    write = "--check" not in sys.argv
    rows, errors = build()
    if errors:
        print(f"ANCHOR FAILURES ({len(errors)}) — nothing written:")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"crma pass B: {len(rows)} rows")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")
    if write:
        (HERE / "crma_pass_b.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written crma_pass_b.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

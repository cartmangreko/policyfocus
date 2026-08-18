"""
Net-Zero Industry Act (Regulation (EU) 2024/1735, consolidated 17.08.2025):
SECOND independent extraction pass. Writes sources/nzia_pass_b.json.

    python3 extract_nzia_pass_b.py --check    # report, write nothing
    python3 extract_nzia_pass_b.py            # write nzia_pass_b.json

WHY THIS EXISTS
===============
data/nzia.json was one read, and said so. ETS, IAA and CBAM each carry two
reads that reconcile.py compares; this is NZIA's second, so
`reconcile.py ../data/nzia.json nzia_pass_b.json nzia` can be run and the
register's fifth file carries the same disagreement signal as the other three.

WHAT "INDEPENDENT" MEANS HERE, AND WHAT IT DOES NOT
==================================================
The METHOD is independent and deliberately different. Pass A was written
thematically -- permitting, strategic projects, CO2, procurement, auctions --
and carries one row per theme-level duty. This pass was written by walking the
enacting terms ARTICLE BY ARTICLE AND PARAGRAPH BY PARAGRAPH from Art. 5 to
Art. 48, asking of each numbered paragraph only: does this paragraph, on its
own words, put a duty on someone or hand someone something? Every paragraph
that does gets a row, whether or not a neighbouring paragraph already covered
the ground. Ids are N-01..N-93 in the act's own order and deliberately do not
reuse Pass A's family prefixes -- matching two passes on id coincidence is what
PASS_B_CROSSWALK exists to prevent.

It is NOT independent in the strong sense the ETS and IAA pairs are, where the
two passes were taken before either could see the other. Pass A was written
first, in this same session, and was visible. That weakens the AGREEMENT signal
-- where the two passes agree, the agreement is worth less than it looks -- and
it does not weaken the DISAGREEMENT signal, which is what a second pass is
actually for. Recorded here rather than left for a reader to discover, on the
precedent extract_cbam_pass_b.py set.

The paragraph sweep is what makes the disagreement signal real despite that.
Reading for "which paragraph imposes something" rather than "what does this act
require of firms" reaches provisions a thematic read has no reason to visit,
and 37 of the rows below are provisions Pass A does not carry. Two of them are
duties on operators rather than authorities, which is the class of miss that
matters most.

WHERE THIS PASS DISAGREES WITH THE REGISTER, AND WHY IT IS NOT HEDGING
======================================================================
Four rows classify a provision differently from Pass A. In each the second read
follows THE OPERATIVE VERB AND ITS SUBJECT, and lands on the duty-bearer rather
than on the beneficiary:

  * N-06 (Art. 6(4)) "Project promoters shall be allowed to submit ..." -- the
    sentence is passive and its duty-bearer is the Member State that must
    permit electronic filing. Pass A reads the conferral (right/business).
  * N-30 (Art. 13(1)) "Member States shall recognise as net-zero strategic
    projects ..." -- a duty on the Member State. Pass A reads the STATUS the
    recognition creates (right/business), on the IAA PRM-04 precedent.
  * N-76 (Art. 26(4)) "Member States shall give to each of the criteria ... a
    minimum weight of 5 %" -- a duty on the auction designer. Pass A reads the
    demand advantage the weighting creates (incentive/business).
  * N-46 (Art. 15(4), final sentence) is a granularity split, not a
    reclassification: Pass A's SP-09 carries the urgency conferral and the
    promoter's participation duty as one row, and this pass splits them.

These are the two readings of a status-conferring provision that the benefit
axis exists to arbitrate, and they are recorded as taken, not softened towards
the register's answer. reconcile.py reports them; the ruling decides them.

TWO DATE DISAGREEMENTS, AND THE ONE THIS PASS THINKS IT WINS
===========================================================
Art. 49(3) confines ONE provision -- Art. 25(1) -- to central purchasing bodies
and EUR 25 million contracts until 30 June 2026. Pass A applied that carve-out
to its whole procurement family, including the rows on Art. 25(3) and Art.
25(7). On the words of Art. 49(3) those two apply from 29 June 2024 like
everything else, and this pass dates them that way (N-69, N-71). Stated as a
claim the reconciliation should test, not as a correction already made.

THE SPAN DISCIPLINE
===================
Same as Pass A and for the same reason: anchors run against canonical() of the
act, and a missing or ambiguous anchor is a hard failure. Where a provision is
also quoted by Pass A this pass quotes a DIFFERENT part of it wherever the
paragraph allows, so an identical span is evidence the two reads landed on the
same sentence rather than an artefact of copying.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from textnorm import canonical

HERE = Path(__file__).resolve().parent
ACT = "nzia.txt"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1735-20250817"
OPERATIVE_ANCHOR = "Article 1 Subject matter"

EIF = "Applies from 29 June 2024 (Art. 49(2))"
EIF_25_1 = ("Applies from 29 June 2024; until 30 June 2026 Art. 25(1) reaches only central "
            "purchasing bodies and contracts of EUR 25 million or more (Art. 49(3))")
DEC2025 = "From 30 December 2025 (Art. 49(4))"

B = "business"
S = "state"
C = "commission"
H = "household"

NZT = ["batsol", "clean", "ccs", "power"]
EII = ["steel", "alu", "chem", "cement", "glass"]


def O(**kw):
    kw["measure_type"] = "obligation"
    return kw


def R(**kw):
    kw["measure_type"] = "right"
    return kw


def I(**kw):
    kw["measure_type"] = "incentive"
    return kw


# (id, article, start_anchor, end_anchor, meta)
ROWS: list[tuple] = [

    # ================================================== CHAPTER II, benchmarks
    ("N-01", "Art. 5(1)(a)",
     "a benchmark of at least 40 % of the Union’s annual deployment needs", "necessary to achieve the Union’s 2030 climate and energy targets;",
     O(duty="Support net-zero manufacturing projects towards a Union manufacturing capacity of at least 40% of annual deployment needs by 2030.",
       addressee="The Commission and Member States", cls=S,
       trigger="net-zero technologies listed in Art. 4(1)", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[])),

    ("N-02", "Art. 5(1)(b)",
     "an increased Union share for the corresponding technologies with a view to reaching 15 % of world production by 2040", "necessary to achieve the Union’s 2040 climate and energy targets.",
     O(duty="Raise the Union share of world production of net-zero technologies towards 15% by 2040, unless the added capacity would run significantly beyond Union deployment needs.",
       addressee="The Commission and Member States", cls=S,
       trigger="monitoring under Art. 42 showing the Union share", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[])),

    # ============================================ Section II, permitting plumbing
    ("N-03", "Art. 6(1)",
     "By 30 December 2024 Member States shall establish or designate one or more authorities as single points of contact", "for net-zero technology manufacturing projects, including for net-zero strategic projects",
     O(duty="Establish or designate single points of contact responsible for facilitating and coordinating the permit-granting process.",
       addressee="Member States", cls=S, trigger="entry into application", frequency="one-off",
       verification="none", direction="add", when="By 30 December 2024",
       drivers=["D4"], named=NZT, reached=[])),

    ("N-04", "Art. 6(2)",
     "the Member State shall provide tools to help project promoters identify the appropriate established or designated contact point", "",
     O(duty="Where more than one single point of contact exists, provide tools on the Art. 7 web page that let a promoter identify the right one.",
       addressee="Member States with more than one single point of contact", cls=S,
       trigger="more than one single point of contact designated", frequency="one-off",
       verification="none", direction="add", when=EIF, drivers=["D4"], named=NZT, reached=[])),

    ("N-05", "Art. 6(3)",
     "It shall coordinate and facilitate the submission of all relevant documents and information and shall notify the project promoter of the outcome of the comprehensive decision.", "",
     O(duty="Act as the sole point of contact for the promoter: coordinate and facilitate submission of all documents, and notify the promoter of the comprehensive decision.",
       addressee="Single points of contact", cls=S, trigger="a permit-granting process for a project",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-06", "Art. 6(4)",
     "Project promoters shall be allowed to submit any documents relevant to the permit-granting process in electronic form.", "",
     O(duty="Accept every document relevant to the permit-granting process in electronic form.",
       addressee="Member States and their permit-granting authorities", cls=S,
       trigger="any document relevant to the permit-granting process", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D4"], named=NZT, reached=[],
       note="Passive sentence: the beneficiary is named and the duty-bearer is not. Read on the operative verb, what the paragraph compels is the AUTHORITY's acceptance of electronic filing. Pass A reads the conferral instead and files it as a right on the promoter.")),

    ("N-07", "Art. 6(5)",
     "and that no duplicate studies, permits or authorisations are required, unless otherwise required under Union or national law.", "",
     O(duty="Re-run studies or re-obtain permits already carried out or issued for the same project.",
       addressee="Promoters of net-zero technology manufacturing projects", cls=B,
       trigger="a study, permit or authorisation already exists for the project",
       frequency="per application", verification="competent authority", direction="rem", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-08", "Art. 6(6)",
     "Member States shall ensure that applicants have easy access to information on and procedures for the settlement of disputes concerning the permit-granting process", "if such procedures are provided for by national law.",
     O(duty="Give applicants easy access to information on, and procedures for, settling disputes over the permit-granting process, including alternative dispute resolution where national law provides it.",
       addressee="Member States", cls=S, trigger="a permit-granting process for a project",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[])),

    ("N-09", "Art. 6(7)",
     "Member States shall ensure that the single point of contact and all competent authorities responsible for any step along the permit-granting processes", "for the effective performance of their tasks under this Regulation.",
     O(duty="Resource the single point of contact and every authority in the permit chain with enough qualified staff and enough financial, technical and technological means, including for upskilling and reskilling.",
       addressee="Member States", cls=S, trigger="tasks under the Regulation", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[])),

    ("N-10", "Art. 6(9)",
     "shall specify and make available to the single point of contact concerned, the requirements and extent of information requested of a project promoter", "",
     O(duty="Specify and give the single point of contact the requirements and extent of information that will be asked of a promoter, before the process starts.",
       addressee="Authorities involved in the permit-granting process", cls=S,
       trigger="a permit-granting process for a project", frequency="recurring",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[])),

    ("N-11", "Art. 7",
     "the single points of contact referred to in Article 6(1);", "business support services, including but not limited to corporate tax declaration, local tax laws or labour law.",
     O(duty="Publish online and centrally: the single points of contact, the permit-granting process and dispute settlement, financing and investment services, funding possibilities, and business support services.",
       addressee="Member States", cls=S, trigger="processes relevant to net-zero technology manufacturing projects",
       frequency="one-off, kept updated", verification="none", direction="add", when=EIF,
       drivers=["D1", "D4"], named=NZT, reached=[])),

    ("N-12", "Art. 8",
     "assistance with regard to compliance with applicable administrative and reporting obligations;", "assistance to project promoters along the permit-granting process, in particular for SMEs.",
     O(duty="Provide administrative support to projects: compliance assistance, help informing the public to build acceptance, and support through permitting, with particular attention to SMEs.",
       addressee="Member States", cls=S, trigger="a project located on the territory",
       frequency="per project", verification="none", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-13", "Art. 9(1)",
     "12 months for the construction or expansion of net-zero technology manufacturing projects with a yearly manufacturing capacity of less than 1 GW;", "with a yearly manufacturing capacity of 1 GW or more.",
     O(duty="Complete permitting within 12 months below 1 GW of yearly manufacturing capacity and 18 months at 1 GW or more.",
       addressee="Member State permit-granting authorities", cls=S,
       trigger="a permit-granting application for a manufacturing project", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=NZT, reached=[])),

    ("N-14", "Art. 9(2)",
     "The permit-granting process for net-zero technology manufacturing projects for which a yearly manufacturing capacity is not measured in GW, shall not exceed a time limit of 18 months.", "",
     O(duty="Complete permitting within 18 months where the project's yearly manufacturing capacity is not measured in GW.",
       addressee="Member State permit-granting authorities", cls=S,
       trigger="a project whose capacity is not measured in GW", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=NZT, reached=EII,
       note="The limb that catches every non-electrical manufacturing project, including the energy-intensive decarbonisation projects of Art. 3(17). Pass A carries only the GW-denominated limits of Art. 9(1).")),

    ("N-15", "Art. 9(3)",
     "the project promoter and the single point of contact may agree on splitting the project into several smaller projects", "",
     R(benefit="A decarbonisation project spanning several facilities on one site may be split by agreement into smaller projects, so each fits the permitting time limits.",
       addressee="Promoters of energy-intensive industry decarbonisation projects", cls=B,
       trigger="the project requires several facilities or units on one site", frequency="per project",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=EII, reached=[],
       right_basis=dict(text="the project promoter and the single point of contact may agree on splitting the project into several smaller projects", kind="procedure"))),

    ("N-16", "Art. 9(5)",
     "the single point of contact may give the project promoter the opportunity to submit additional information. In that case, the single point of contact shall notify the project promoter of the date when the additional information is due", "shall not be counted towards the duration of the permit-granting process referred to in paragraphs 1 and 2 of this Article.",
     O(duty="Where consultation shows the environmental impact assessment report needs supplementing, give the promoter at least 30 days to file the additional information; that period does not count against the permitting clock.",
       addressee="Single points of contact", cls=S,
       trigger="consultation under Art. 1(2)(g)(ii) of Directive 2011/92/EU requiring additional information",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[],
       note="Cuts both ways and is filed on the duty side: the promoter gains a floor of 30 days, and the clock the time limits run on stops while it is used.")),

    ("N-17", "Art. 9(6)",
     "a Member State may once extend the time limits referred to in paragraphs 1, 2 and 7 of this Article and in Article 16(1) and (2) by a maximum of 3 months", "",
     O(duty="Hold the permitting time limits for a project whose nature, complexity, location or size requires longer.",
       addressee="Promoters of net-zero technology manufacturing and strategic projects", cls=B,
       trigger="exceptional case turning on the nature, complexity, location or size of the project",
       frequency="if it happens", verification="competent authority", direction="rem", when=EIF,
       drivers=[], named=NZT, reached=[],
       note="An extension power is the time limit being switched off for one project. Recorded from the promoter's side, where the effect lands, and as direction rem because what moves is the duty on the authority.")),

    ("N-18", "Art. 9(7)",
     "it may extend the time limits referred to in paragraphs 1 and 2 of this Article and in Article 16 (1) and (2) by 6 months, within 6 months of the start of the permit-granting process.", "",
     O(duty="Hold the permitting time limits for a project raising exceptional risks to the health and safety of workers or the general population.",
       addressee="Promoters of net-zero technology manufacturing and strategic projects", cls=B,
       trigger="exceptional risks to health and safety needing time to establish that measures are in place",
       frequency="if it happens", verification="competent authority", direction="rem", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-19", "Art. 9(8)",
     "the single point of contact shall inform the project promoter in writing of the reasons for the extension and of the date when the comprehensive decision is expected.", "",
     O(duty="Inform the promoter in writing of the reasons for any extension and of the date the comprehensive decision is now expected.",
       addressee="Single points of contact", cls=S, trigger="an extension under Art. 9(6) or 9(7)",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[])),

    ("N-20", "Art. 9(10)",
     "the single point of contact concerned shall acknowledge that the application is complete or, if the project promoter has not sent all the information required to process the application, request the project promoter to submit a complete application", "shall be entitled only to request further evidence to complete the identified missing information.",
     O(duty="Acknowledge completeness within 45 days or say exactly what is missing; a second request must come within 30 days and may not open subjects the first did not raise.",
       addressee="Single points of contact", cls=S, trigger="receipt of a permit-granting application",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=["D5"], named=NZT, reached=[])),

    ("N-21", "Art. 9(11)",
     "a detailed schedule for the permit-granting process. That schedule shall start from the moment when the single point of contact acknowledges the completeness of the application.", "",
     O(duty="Draw up a detailed permitting schedule within two months of the application, in cooperation with the other authorities, and publish it on a free-access website.",
       addressee="Single points of contact", cls=S, trigger="receipt of a permit-granting application",
       frequency="per application", verification="none", direction="add", when=EIF,
       drivers=["D1", "D5"], named=NZT, reached=[])),

    ("N-22", "Art. 10(1)",
     "The single point of contact shall ensure that the opinion is issued as soon as possible and no later than 45 days from the date on which the project promoter submitted its request for an opinion.", "",
     R(benefit="A promoter may obtain, before filing, an opinion on the scope and level of detail of the environmental impact assessment report, answered within 45 days.",
       addressee="Promoters of net-zero technology manufacturing projects", cls=B,
       trigger="an environmental impact assessment required under Arts. 5 to 9 of Directive 2011/92/EU",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=NZT, reached=[],
       right_basis=dict(text="the project promoter concerned may request, before submitting the application, an opinion from the single point of contact on the scope and level of detail of the information to be included in the environmental impact assessment report", kind="procedure"))),

    ("N-23", "Art. 10(2)",
     "Under the coordinated procedure referred to in the first subparagraph, a competent authority shall coordinate the various individual assessments", "The application of the joint or coordinated procedure shall not affect the content of the environmental impact assessment.",
     O(duty="Run a coordinated or joint procedure where environmental assessment duties arise simultaneously under two or more of the listed directives.",
       addressee="Member States", cls=S, trigger="simultaneous assessment duties under two or more directives",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-24", "Art. 10(3)",
     "issue the reasoned conclusion referred to in Article 1(2), point (g)(iv), of Directive 2011/92/EU on the environmental impact assessment within 90 days of receiving all necessary information", "",
     O(duty="Issue the reasoned conclusion on the environmental impact assessment within 90 days of receiving all necessary information and completing consultations.",
       addressee="Member State competent authorities", cls=S,
       trigger="a completed environmental impact assessment", frequency="per project",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=NZT, reached=[])),

    ("N-25", "Art. 10(5)",
     "The timeframes for consulting the public concerned as referred to in Article 1(2), point (e), of Directive 2011/92/EU", "that period shall be extended to a maximum of 90 days on a case-by-case basis.",
     O(duty="Hold public and authority consultation on the environmental report to between 30 and 85 days, extended to at most 90 in the cases Art. 6(4) of Directive 2011/92/EU covers.",
       addressee="Member States", cls=S, trigger="consultation on the environmental impact assessment report",
       frequency="per project", verification="none", direction="add", when=EIF,
       drivers=["D5"], named=NZT, reached=[],
       note="A ceiling on consultation, which is where the permitting timetable is usually lost. Pass A carries Art. 10(2) and 10(3) and not this.")),

    ("N-26", "Art. 10(6)",
     "have a sufficient number of qualified staff and sufficient financial, technical and technological resources necessary to fulfil their obligations under this Article.", "",
     O(duty="Resource the environmental assessment authorities with enough qualified staff and enough financial, technical and technological means to meet the deadlines of Art. 10.",
       addressee="Member States", cls=S, trigger="obligations under Art. 10", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[])),

    ("N-27", "Art. 11(1)",
     "National, regional and local authorities responsible for preparing plans, including zoning, spatial plans and land use plans, shall consider including in such plans", "Member States shall ensure that all relevant spatial planning data is available online in accordance with Article 7.",
     O(duty="Consider making room for net-zero manufacturing projects, strategic projects and Valleys in zoning, spatial and land use plans -- giving priority to artificial, built, industrial and brownfield surfaces -- and put all relevant spatial planning data online.",
       addressee="National, regional and local planning authorities", cls=S,
       trigger="preparation of zoning, spatial or land use plans", frequency="per plan",
       verification="none", direction="add", when=EIF, drivers=["D1", "D4"], named=NZT, reached=["build"],
       note="Pass A carries no planning row at all. The land-side duty is where a manufacturing project is enabled or blocked before any permit is applied for.")),

    ("N-28", "Art. 11(2)",
     "those assessments shall be combined. Where applicable, the combined assessment shall also address the impact on potentially affected water bodies", "The combined assessment shall be carried out in a manner that does not lead to a prolongation of the time limits set out in this Regulation.",
     O(duty="Combine the strategic environmental assessment and the habitats assessment where a plan makes room for net-zero projects, covering water bodies and, where relevant, the marine environment, without lengthening the Regulation's time limits.",
       addressee="Member States", cls=S, trigger="a plan subject to assessment under Directive 2001/42/EC and Art. 6 of Directive 92/43/EEC",
       frequency="per plan", verification="competent authority", direction="add", when=EIF,
       drivers=[], named=NZT, reached=["build"])),

    ("N-29", "Art. 12(2)",
     "All decisions adopted pursuant to this Section and Articles 8, 15, 16 and 28 shall be made publicly available in an easily understandable manner", "",
     O(duty="Publish every decision under the permitting section and Arts. 8, 15, 16 and 28 in an easily understandable form, with all decisions on one project on the same website.",
       addressee="Member States and their authorities", cls=S, trigger="any decision under the named provisions",
       frequency="per decision", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[])),

    # ============================================ Section III, strategic projects
    ("N-30", "Art. 13(1)",
     "Member States shall recognise as net-zero strategic projects net-zero technology manufacturing projects located in the Union", "including contributing to the Union’s climate or energy targets",
     O(duty="Recognise as net-zero strategic projects the manufacturing projects that contribute to the Art. 1 objectives and meet at least one of the resilience, supply-chain or sustainability criteria.",
       addressee="Member States", cls=S, trigger="a project meeting at least one Art. 13(1) criterion",
       frequency="per application", verification="competent authority", direction="add", when=EIF,
       drivers=["D3"], named=NZT, reached=EII,
       note="The operative verb binds the Member State and the sentence has no conferring language in it. Pass A reads the status the recognition creates and files it as right/business on the IAA PRM-04 precedent. Both readings are on the table; this pass takes the one the sentence states.")),

    ("N-31", "Art. 13(3)",
     "Member States shall recognise as net-zero strategic projects CO2 storage projects that meet all of the following criteria:", "shall also be recognised as a net-zero strategic project.",
     R(benefit="A CO2 storage project sited in the Union that contributes to the Art. 20 injection objective and has applied for a storage permit is recognised as strategic -- and so is any capture project and any transport infrastructure project attached to it.",
       addressee="Promoters of CO2 storage, capture and transport projects", cls=B,
       trigger="a storage site in the Union, contributing to Art. 20, with a Directive 2009/31/EC permit applied for",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1", "F4"], named=["ccs"], reached=EII,
       right_basis=dict(text="Any CO2 capture project related to a CO2 storage project that fulfils the criteria referred to in the first subparagraph, and any related CO2 infrastructure project necessary for the transport of captured CO2shall also be recognised as a net-zero strategic project.", kind="scope"),
       note="The whole CCS chain route into strategic status. Pass A carries Art. 13(1) and 13(5) and not this, so the register has no row for how a storage or capture project gets the status.")),

    ("N-32", "Art. 13(4)",
     "Net-zero technology manufacturing projects corresponding to a net-zero technology, located in ‘less developed and transition regions’ and Just Transition Fund territories", "without the project promoter having to submit a formal application under Article 14(2).",
     R(benefit="A project in a less developed or transition region or a Just Transition Fund territory, eligible under cohesion rules, is recognised as strategic on a written request once the award procedure has run -- with no formal application.",
       addressee="Promoters of cohesion-funded projects in less developed and transition regions and Just Transition Fund territories",
       cls=B, trigger="award procedure completed for a project eligible under cohesion policy rules",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=EII,
       right_basis=dict(text="recognised by Member States as net-zero strategic projects under Article 14(3) upon the written request of the project promoter without the project promoter having to submit a formal application under Article 14(2)", kind="procedure"),
       note="The cohesion-region twin of the funding route Pass A carries as SP-05 from Art. 13(5). Same mechanism, different qualifying condition, and the register has only one of the two.")),

    ("N-33", "Art. 13(5)",
     "that benefits from the ETS Innovation Fund or is part of Important Projects of Common European Interest, of European Hydrogen Valleys or of the Hydrogen Bank", "",
     R(benefit="A project backed by the ETS Innovation Fund, an IPCEI, a European Hydrogen Valley or the Hydrogen Bank is recognised as strategic on a written request, with no formal application.",
       addressee="Promoters of Union-funded manufacturing projects", cls=B,
       trigger="the project benefits from one of the named Union funding routes supporting manufacturing capacity",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=EII,
       right_basis=dict(text="shall be recognised by Member States as a net-zero strategic project under Article 14(3) upon the written request of the project promoter without the project promoter having to submit a formal application under Article 14(2)", kind="procedure"))),

    ("N-34", "Art. 13(6)",
     "If there are net-zero technologies for which a Member State intends not to recognise projects as strategic projects, that Member State shall communicate that as soon as possible and publicly.", "",
     O(duty="Where a Member State will not recognise projects in a technology it does not accept in its energy mix, say so publicly and as soon as possible.",
       addressee="Member States refusing recognition for a technology", cls=S,
       trigger="a value chain for a technology the Member State does not accept in its energy supply",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[],
       note="The provision that lets a Member State close a technology out of the strategic-project route entirely. A promoter needs it to know whether the route exists where it is building, and the register carries nothing on it.")),

    ("N-35", "Art. 14(2)",
     "relevant evidence related to the fulfilment of the criteria laid down in Article 13(1) or (3);", "The Commission shall provide a pre-set form to submit the applications referred to in paragraph 1.",
     O(duty="File evidence against the criteria, a business plan on financial viability consistent with quality job creation, and a first draft timetable, on the Commission's pre-set form.",
       addressee="Promoters applying for strategic-project status", cls=B,
       trigger="an application for recognition", frequency="per application",
       verification="competent authority", direction="add", when=EIF,
       drivers=["D1", "D3"], named=NZT, reached=EII)),

    ("N-36", "Art. 14(3)",
     "through a fair and transparent process within one month of the receipt of the complete application", "The date of the acknowledgement of the completeness of the submission shall serve as the start of the assessment process.",
     O(duty="Assess a strategic-project application within one month of completeness, asking for missing information once only, and give a reasoned decision.",
       addressee="Member States", cls=S, trigger="receipt of a complete application", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=NZT, reached=[])),

    ("N-37", "Art. 14(4)",
     "the project promoter may notify the Member State and request without undue delay that the Member State provide the project promoter with an updated deadline", "which shall not be later than 30 days from the original deadline.",
     R(benefit="Where the Member State misses the one-month deadline, the promoter can demand a new one, and it may be no more than 30 days past the original.",
       addressee="Promoters awaiting a decision on strategic-project recognition", cls=B,
       trigger="no decision within the Art. 14(3) timeframe", frequency="if it happens",
       verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="the project promoter may notify the Member State and request without undue delay that the Member State provide the project promoter with an updated deadline", kind="procedure"),
       note="The only thing in the act that bites when a Member State simply does not answer. Pass A carries the Commission review of a REJECTION (Art. 14(5)) and not the remedy for silence.")),

    ("N-38", "Art. 14(5)",
     "Where a Member State rejects the application, the applicant shall have the right to submit the application to the Commission", "",
     R(benefit="A rejected applicant may take the application to the Commission, which assesses it within 20 working days.",
       addressee="Promoters whose application was rejected", cls=B, trigger="rejection by a Member State",
       frequency="if it happens", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="the applicant shall have the right to submit the application to the Commission, which shall assess the application within 20 working days", kind="procedure"))),

    ("N-39", "Art. 14(7)",
     "it shall inform the project promoter concerned. After hearing the project promoter, the Member State may repeal the decision recognising a project as a net-zero strategic project.", "",
     O(duty="Inform the promoter and hear it before repealing a recognition on grounds of substantial change, loss of the criteria, or incorrect information.",
       addressee="Member States and the Commission", cls=S,
       trigger="a finding of substantial change, loss of criteria, or incorrect information",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-40", "Art. 14(8)",
     "A project which is no longer recognised as a net-zero strategic project shall lose all rights connected to that status under this Regulation.", "",
     R(benefit="Strategic-project status, and every right attached to it, is lost when recognition ends.",
       addressee="Promoters of net-zero strategic projects", cls=B,
       trigger="repeal of the recognition decision", frequency="if it happens",
       verification="competent authority", direction="rem", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="A project which is no longer recognised as a net-zero strategic project shall lose all rights connected to that status under this Regulation.", kind="conferral"))),

    ("N-41", "Art. 14(9)",
     "The Commission shall set up and maintain an openly available registry of net-zero strategic projects.", "",
     O(duty="Set up and maintain an openly available registry of net-zero strategic projects.",
       addressee="The Commission", cls=C, trigger="recognition of net-zero strategic projects",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=["D1", "D4"], named=NZT, reached=[])),

    ("N-42", "Art. 15(1)",
     "Project promoters and all authorities concerned shall ensure that for net-zero strategic projects the relevant processes are treated in the most rapid way possible", "",
     O(duty="Handle every process touching a strategic project in the most rapid way Union and national law allow -- a duty on the promoter as much as on the authorities.",
       addressee="Promoters of net-zero strategic projects and all authorities concerned", cls=B,
       trigger="recognition as a net-zero strategic project", frequency="per project",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[],
       note="Art. 15's first paragraph names the PROMOTER first among those bound. The priority track has a duty attached to it, and Pass A carries only the conferring paragraphs of this article.")),

    ("N-43", "Art. 15(2)",
     "Member States shall grant that net-zero strategic project the status of the highest national significance possible, where such a status exists in national law", "",
     R(benefit="A recognised strategic project is given the highest national significance the Member State's law provides, and treated accordingly in permitting, environmental assessment and spatial planning.",
       addressee="Promoters of net-zero strategic projects", cls=B, trigger="recognition, where national law provides such a status",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=NZT, reached=[],
       right_basis=dict(text="Member States shall grant that net-zero strategic project the status of the highest national significance possible, where such a status exists in national law", kind="conferral"))),

    ("N-44", "Art. 15(3)",
     "Net-zero strategic projects shall be considered to contribute to the security of supply of net-zero technologies in the Union and, therefore, to be in the public interest.", "",
     R(benefit="Strategic projects count as being in the public interest, and may be treated as of overriding public interest, in the environmental derogations.",
       addressee="Promoters of net-zero strategic projects", cls=B, trigger="recognition as a strategic project",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=NZT, reached=EII,
       right_basis=dict(text="net-zero strategic projects in the Union shall be considered to be of public interest and may be considered to have an overriding public interest and to serve the interests of public health and safety", kind="conferral"))),

    ("N-45", "Art. 15(4), first sentence",
     "All dispute resolution procedures, litigation, appeals and judicial remedies related to net-zero strategic projects before any national courts", "provided that the usually applicable rights of defence of individuals or of local communities are respected.",
     R(benefit="Litigation and appeals touching a strategic project are treated as urgent wherever national permitting law has an urgency procedure.",
       addressee="Promoters of net-zero strategic projects", cls=B,
       trigger="dispute resolution, litigation, appeal or judicial remedy on a strategic project",
       frequency="if it happens", verification="none", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=NZT, reached=[],
       right_basis=dict(text="shall be treated as urgent if and to the extent to which national law concerning permit-granting processes provides for such urgency procedures", kind="scope"))),

    ("N-46", "Art. 15(4), final sentence",
     "Project promoters of net-zero strategic projects shall participate in such urgency procedures, where applicable.", "",
     O(duty="Take part in the urgency procedures that apply to disputes over the project.",
       addressee="Promoters of net-zero strategic projects", cls=B,
       trigger="an urgency procedure applying to a dispute on the project", frequency="if it happens",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[],
       note="A granularity split, not a reclassification: Pass A's SP-09 carries this sentence inside the row that states the urgency conferral. Read on its own it is a duty with its own addressee and its own trigger.")),

    ("N-47", "Art. 16(1)-(2)",
     "9 months for the construction or expansion of net-zero strategic projects with a yearly manufacturing capacity of less than 1 GW;", "For net-zero strategic projects for which a yearly manufacturing capacity is not measured in GW, the permit-granting process shall not exceed 12 months.",
     O(duty="Complete strategic-project permitting within 9 months below 1 GW, 12 months at 1 GW or more, 18 months for the permits to operate a storage site, and 12 months where capacity is not measured in GW.",
       addressee="Member State permit-granting authorities", cls=S,
       trigger="a permit-granting application for a recognised strategic project", frequency="per application",
       verification="none", direction="add", when=EIF, drivers=["D5"], named=NZT, reached=[])),

    ("N-48", "Art. 17(2)",
     "define a clear geographic and technology scope for the Valleys;", "ensure synergies, where possible, with the designation of renewables acceleration areas as established by Directive (EU) 2023/2413",
     O(duty="Designate a Valley only with a defined geographic and technology scope, priority to built and brownfield land, a strategic environmental assessment and where applicable a habitats assessment, and synergies with renewables acceleration areas.",
       addressee="Member States designating Valleys", cls=S, trigger="a decision to designate a Valley",
       frequency="per designation", verification="competent authority", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[],
       note="The area-level environmental assessment is what the Art. 18(2)-(3) project-level streamlining is bought with. Pass A carries the Art. 17(3) support plan and not the conditions on the designation itself.")),

    ("N-49", "Art. 17(3)",
     "facilitate the development of the necessary infrastructure in the Valley;", "make information about the Valley accessible online in accordance with Article 7.",
     O(duty="Accompany a Valley designation with a plan carrying at least four support schemes: infrastructure, private investment, reskilling, and online information.",
       addressee="Member States designating Valleys", cls=S, trigger="a decision to designate a Valley",
       frequency="per designation", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[])),

    ("N-50", "Art. 18(1)",
     "Sections II and III shall apply to individual projects in Valleys. A single point of contact, shall be designated for each Valley.", "",
     O(duty="Designate a single point of contact for each Valley, with the permitting and strategic-project rules applying to individual projects inside it.",
       addressee="Member States designating Valleys", cls=S, trigger="designation of a Valley",
       frequency="per designation", verification="none", direction="add", when=EIF,
       drivers=["D4"], named=NZT, reached=[])),

    ("N-51", "Art. 18(3)",
     "The single point of contact shall make available to project promoters templates indicating the specific permits needed for projects in Valleys.", "to facilitate the determination by a competent authority as to whether the project is to be made subject to an assessment pursuant to Article 4(2) to (6) of that Directive.",
     O(duty="Give promoters templates naming the specific permits a Valley project needs, carrying the project features and mitigation measures that decide whether an environmental impact assessment is required at all.",
       addressee="Single points of contact for Valleys", cls=S, trigger="a project in a designated Valley",
       frequency="per project", verification="none", direction="add", when=EIF,
       drivers=["D1"], named=NZT, reached=[],
       note="The mechanism that keeps Valley projects out of full environmental impact assessment where they qualify -- the practical half of the Valley regime, and absent from the register.")),

    ("N-52", "Art. 18(4)",
     "Net-zero technology manufacturing projects in Valleys shall be considered to contribute to the security of supply of net-zero technologies in the Union", "",
     R(benefit="Siting a project in a Valley confers the public-interest status in the environmental derogations without the project having to be recognised as strategic.",
       addressee="Promoters of projects sited in a Valley", cls=B, trigger="the project is located in a designated Valley",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F1"], named=NZT, reached=[],
       right_basis=dict(text="net-zero technology manufacturing projects in Valleys in the Union shall be considered to be of public interest and may be considered to have an overriding public interest", kind="scope"))),

    ("N-53", "Art. 19(2)",
     "The Platform shall, at the request of the net-zero strategic project promoter, discuss and advise on how the financing of the project can be completed", "",
     R(benefit="A strategic-project promoter may call the Platform in to work through how to close the project's financing.",
       addressee="Promoters of net-zero strategic projects", cls=B, trigger="a request by the promoter",
       frequency="per project", verification="none", direction="add", when=EIF,
       value_drivers=["V4"], frictions=["F3"], named=NZT, reached=[],
       right_basis=dict(text="The Platform shall, at the request of the net-zero strategic project promoter, discuss and advise on how the financing of the project can be completed", kind="procedure"))),

    # ================================================= Chapter III, CO2 injection
    ("N-54", "Art. 20(2)",
     "All storage sites shall be designed to operate for a minimum of five years and shall respect the principles of fair and open access provided in a transparent and non-discriminatory manner", "",
     O(duty="Design every CO2 storage site to operate for at least five years, and run it on fair and open access, transparently and without discrimination.",
       addressee="Operators of CO2 storage sites counting towards the Union injection objective", cls=B,
       trigger="a geological storage site permitted under Directive 2009/31/EC",
       frequency="per site", verification="competent authority", direction="add", when=EIF,
       drivers=["D3", "D7"], named=["ccs"], reached=EII,
       note="A DUTY ON OPERATORS sitting in an article that otherwise sets a Union objective, which is how a thematic read misses it: Pass A carries Art. 20 as a target and has no row for the design life or the access principle. It is the provision that decides whether a captured-CO2 emitter can get into someone else's store.")),

    ("N-55", "Art. 21(1)(a)",
     "make data on all areas where CO2 storage sites could be permitted on their territory, including saline aquifers, publicly available", "",
     O(duty="Publish the data on every area where a CO2 storage site could be permitted, saline aquifers included, to at least the detail the national energy and climate plan guidance asks for.",
       addressee="Member States", cls=S, trigger="areas on the territory where storage could be permitted",
       frequency="one-off", verification="none", direction="add", when="By 30 December 2024",
       drivers=["D1", "D4"], named=["ccs"], reached=EII)),

    ("N-56", "Art. 21(1)(b)",
     "geological data relating to production sites that have been decommissioned or whose decommissioning has been notified to the competent authority", "unless the entity has applied for an exploration permit in accordance with Directive 2009/31/EC, including data on:",
     O(duty="Publish, on a non-reliance basis, geological data on decommissioned production sites and any economic assessment of the cost of enabling CO2 injection.",
       addressee="Current and former holders of hydrocarbon authorisations under Directive 94/22/EC", cls=B,
       trigger="a decommissioned production site, unless an exploration permit has been applied for",
       frequency="one-off", verification="competent authority", direction="add", when="By 30 December 2024",
       drivers=["D1", "D7"], named=["ccs", "power"], reached=[])),

    ("N-57", "Art. 21(2)",
     "a mapping of CO2 capture projects in progress on its territory or in cooperation with other Member States", "an estimation of the necessary future CO2 transport projects’ capacity to match the corresponding capture and storage capacity.",
     O(duty="Report annually and publicly on capture, storage and transport projects in progress, the capacities they need, national support measures, capture targets, and cross-border cooperation.",
       addressee="Member States", cls=S, trigger="CO2 capture, storage and transport activity on the territory",
       frequency="annual", verification="none", direction="add", when="By 30 December 2024, annually thereafter",
       drivers=["D1", "D4", "D5"], named=["ccs"], reached=EII)),

    ("N-58", "Art. 21(3)",
     "Should the report referred to in paragraph 2 show that no CO2 storage projects are in progress on their territory, Member States shall report on plans to facilitate the decarbonisation of industrial sectors.", "",
     O(duty="Where no storage projects are in progress, report instead on the plans to decarbonise industry, including cross-border transport to stores in other Member States and CO2 utilisation projects.",
       addressee="Member States with no CO2 storage projects in progress", cls=S,
       trigger="an Art. 21(2) report showing no storage projects on the territory", frequency="annual",
       verification="none", direction="add", when=EIF, drivers=["D1", "D5"], named=["ccs"], reached=EII,
       note="What an emitter in a Member State with no domestic store is actually told to expect. Pass A has no row for it.")),

    ("N-59", "Art. 22(2)",
     "Member States shall take the necessary measures to enable access to CO2 transport networks and to storage sites", "",
     O(duty="Take the measures needed to open access to CO2 transport networks and storage sites, so far as economically feasible or where a customer is willing to pay.",
       addressee="Member States", cls=S, trigger="captured CO2 seeking access to networks or sites",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=[], named=["ccs"], reached=EII)),

    ("N-60", "Art. 23(1)",
     "Those individual contributions shall be calculated pro-rata on the basis of each entity’s share in the Union’s crude oil and natural gas production from 1 January 2020 to 31 December 2023", "available to the market by 2030.",
     O(duty="Deliver an individual share of the Union's 50 Mt/year CO2 injection capacity target by 2030, pro-rata to 2020-2023 Union oil and gas production, as permitted capacity available to the market.",
       addressee="Authorised oil and gas producers above the de minimis threshold", cls=B,
       trigger="a hydrocarbon authorisation with 2020-2023 Union production above the delegated-act threshold",
       frequency="one-off (capacity in place by 2030)", verification="competent authority",
       direction="add", when="Contribution to be available to the market by 2030",
       drivers=["D4", "D6", "D7"], named=["ccs", "power"], reached=EII)),

    ("N-61", "Art. 23(2)",
     "Member States shall identify and report to the Commission the entities referred to in paragraph 1 and their volumes in crude oil and natural gas production", "",
     O(duty="Identify the authorised producers on the territory and report their 2020-2023 oil and gas production volumes to the Commission.",
       addressee="Member States", cls=S, trigger="authorised hydrocarbon producers on the territory",
       frequency="one-off", verification="none", direction="add", when="By 30 September 2024",
       drivers=["D1", "D4"], named=["ccs", "power"], reached=[])),

    ("N-62", "Art. 23(4)",
     "confirm the entity's contribution, expressed in terms of targeted volume of new CO2 storage and injection capacity commissioned by 2030;", "specify the means and the milestones for reaching the targeted volume.",
     O(duty="Submit a plan confirming the targeted volume of new storage and injection capacity to be commissioned by 2030, with the means and milestones for reaching it.",
       addressee="Authorised oil and gas producers subject to a contribution", cls=B,
       trigger="being subject to a contribution under Art. 23(1)", frequency="one-off",
       verification="competent authority", direction="add", when="By 30 June 2025",
       drivers=["D1", "D3", "D6"], named=["ccs", "power"], reached=[])),

    ("N-63", "Art. 23(5)",
     "invest in, or develop, CO2 storage projects alone or in cooperation;", "enter into agreements with third-party storage project developers or investors to fulfil their contribution.",
     R(benefit="A producer may meet its contribution by investing in or developing storage itself, by contracting with another obligated producer, or by contracting with third-party developers or investors.",
       addressee="Authorised oil and gas producers subject to a contribution", cls=B,
       trigger="meeting the targeted volume of available injection capacity", frequency="per project",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F5"], named=["ccs"], reached=[],
       right_basis=dict(text="enter into agreements with third-party storage project developers or investors to fulfil their contribution", kind="scope"))),

    ("N-64", "Art. 23(6)",
     "the entities referred to in paragraph 1 shall submit a report to the Commission detailing their progress towards meeting their contribution", "",
     O(duty="Report annually to the Commission on progress towards the injection-capacity contribution; the reports are published.",
       addressee="Authorised oil and gas producers subject to a contribution", cls=B,
       trigger="being subject to a contribution", frequency="annual", verification="competent authority",
       direction="add", when="By 30 June 2026, annually thereafter",
       drivers=["D1", "D5"], named=["ccs", "power"], reached=[])),

    ("N-65", "Art. 23(7)-(8)",
     "the overall annual injection capacity of all storage sites operated by any entity that has received a storage permit", "the Commission shall adopt a decision exempting the entities concerned from their individual contribution in relation to the production activities they have carried out on the territory of the Member State submitting the request.",
     O(duty="Deliver an individual injection-capacity contribution for production in a Member State whose permitted, FID-reached storage capacity already exceeds the sum of those contributions.",
       addressee="Authorised producers active in a Member State that obtains the exemption", cls=B,
       trigger="a Member State application before the end of 2027 meeting the capacity condition",
       frequency="one-off", verification="competent authority", direction="rem",
       when="Application to be submitted before the end of 2027",
       drivers=[], named=["ccs", "power"], reached=[])),

    ("N-66", "Art. 23(9)",
     "Entities exempted pursuant to paragraph 8 may enter into agreements in accordance with paragraph 5, points (b) and (c), only in respect of any injection capacity exceeding the individual contribution from which they are exempted", "",
     O(duty="Keep any agreements under Art. 23(5)(b)-(c) to injection capacity above the exempted contribution and above the sum of the exempted contributions.",
       addressee="Producers exempted under Art. 23(8)", cls=B, trigger="an exemption granted under Art. 23(8)",
       frequency="per project", verification="competent authority", direction="add", when=EIF,
       drivers=["D6"], named=["ccs"], reached=[],
       note="The anti-double-counting limb of the exemption. Pass A carries the exemption and not the condition attached to it, so the register currently reads the relief as wider than it is.")),

    ("N-67", "Art. 23(13)",
     "Member States shall lay down penalties by means of administrative procedures, legal proceedings, or both, applicable to infringements by entities referred to in paragraph 1", "",
     O(duty="Lay down effective, proportionate and dissuasive penalties for producers infringing their injection-capacity obligations.",
       addressee="Member States", cls=S, trigger="infringement by an entity subject to a contribution",
       frequency="one-off", verification="none", direction="add", when="By 30 June 2026",
       drivers=["D6"], named=["ccs", "power"], reached=[])),

    # ================================================== Chapter IV, market access
    ("N-68", "Art. 25(1)",
     "where contracts have net-zero technologies listed in Article 4(1), points (a) to (k), of this Regulation as part of their subject matter", "shall apply minimum mandatory requirements regarding environmental sustainability established in the implementing act referred to in paragraph 5 of this Article.",
     O(duty="Apply the Commission's minimum mandatory environmental sustainability requirements in procurement whose subject matter includes the listed net-zero technologies.",
       addressee="Contracting authorities and contracting entities", cls=S,
       trigger="a procurement with Art. 4(1)(a)-(k) technologies as part of its subject matter",
       frequency="per tender", verification="none", direction="add", when=EIF_25_1,
       drivers=["D1"], named=NZT, reached=["build"])),

    ("N-69", "Art. 25(3)",
     "a special condition that relates to social or employment-related considerations that takes the form of a contract performance clause", "that goes beyond the requirements provided for in applicable national legislation, if such legislation exists.",
     O(duty="Attach to net-zero works contracts at least one of a social or employment performance clause, a cybersecurity requirement, or an on-time delivery obligation backed by a charge.",
       addressee="Contracting authorities and contracting entities", cls=S,
       trigger="works contracts and works concessions including the listed net-zero technologies",
       frequency="per tender", verification="none", direction="add", when=EIF,
       drivers=["D1", "D6"], named=NZT, reached=["build"],
       note="DATE DISAGREEMENT. Pass A dates this with the Art. 49(3) carve-out. Art. 49(3) names Art. 25(1) and nothing else, so on its words this paragraph applies from 29 June 2024 with no threshold.")),

    ("N-70", "Art. 25(6)",
     "A Member State shall not discriminate against, or subject to unjustified different treatment, a provider or net-zero products from another Member State.", "",
     O(duty="Do not discriminate against, or treat differently without justification, a provider or net-zero products from another Member State.",
       addressee="Member States", cls=S, trigger="application of the resilience and sustainability requirements in procurement",
       frequency="per tender", verification="none", direction="add", when=EIF_25_1,
       drivers=[], named=NZT, reached=[],
       note="The internal-market limit on the resilience regime. A supplier bidding across a border needs it, and the register has no row for it.")),

    ("N-71", "Art. 25(7)",
     "an obligation for the duration of the contract not to supply more than 50 % of the value of the specific net-zero technology", "of at least 10 % of the value of the specific net-zero technologies of the contract referred to in this paragraph.",
     O(duty="Hold supply from each dominant third country below 50% of contract value for the technology and its main components, prove it on request, and pay at least 10% of contract value if the cap is breached.",
       addressee="Tenderers and successful contractors supplying net-zero technologies", cls=B,
       trigger="a Commission determination under Art. 29(2) on concentration of Union supply",
       frequency="per contract", verification="self-declaration", direction="add", when=EIF,
       drivers=["D1", "D6"], named=NZT, reached=["build"],
       note="DATE DISAGREEMENT, same ground as N-69: Art. 49(3) confines Art. 25(1) only.")),

    ("N-72", "Art. 25(8)",
     "For contracts covered by the Union’s Appendix I to the GPA as well as by other relevant international agreements by which the Union is bound", "where the specific net-zero technology or its main specific components originates from sources of supply that are signatories to those agreements.",
     O(duty="Apply the origin cap, the evidence duty and the 10% charge to supply originating with parties to the GPA and the Union's other relevant international agreements.",
       addressee="Contracting authorities, and tenderers supplying from GPA signatory sources", cls=S,
       trigger="a contract covered by the GPA or another relevant international agreement",
       frequency="per tender", verification="none", direction="rem", when=EIF,
       drivers=[], named=NZT, reached=[],
       note="The carve-out that decides how much of world supply the resilience conditions actually reach. Pass A carries the cap and the domestic escape hatches and not this one.")),

    ("N-73", "Art. 25(9)-(10)",
     "the required net-zero technology can only be supplied by a specific economic operator and no reasonable alternative or substitute exists", "may be presumed by contracting authorities and contracting entities to be disproportionate.",
     O(duty="Apply the minimum sustainability requirements where there is a sole supplier, where a comparable tender in the last two years drew no suitable bids, or where compliance would cost disproportionately -- presumed above 20%.",
       addressee="Contracting authorities and contracting entities", cls=S,
       trigger="sole supplier, an earlier failed tender, or disproportionate cost", frequency="per tender",
       verification="none", direction="rem", when=EIF_25_1, drivers=[], named=NZT, reached=[])),

    ("N-74", "Art. 25(11)",
     "Where the application of the resilience contribution pursuant to paragraph 7 of this Article has led to a situation where no suitable tenders", "decide not to apply paragraph 7 of this Article in a specific subsequent public procurement procedure that aims to address the same needs",
     O(duty="Apply the resilience conditions in a re-run procurement addressing the same needs, where applying them drew no suitable tenders the first time.",
       addressee="Contracting authorities and contracting entities", cls=S,
       trigger="no suitable tenders or requests to participate after applying the resilience contribution",
       frequency="per tender", verification="none", direction="rem", when=EIF,
       drivers=[], named=NZT, reached=[],
       note="The release valve on the origin cap itself, distinct from the Art. 25(9) sustainability escape hatch Pass A carries.")),

    ("N-75", "Art. 26(1)",
     "pre-qualification criteria related to:", "pre-qualification criteria or award criteria to assess the auction’s sustainability and resilience contribution as referred to in paragraph 2.",
     O(duty="Build responsible business conduct, cyber and data security and delivery-capability pre-qualification into renewable auctions, plus criteria for the sustainability and resilience contribution.",
       addressee="Member States designing renewable energy auctions", cls=S, trigger="an auction for renewable energy deployment",
       frequency="per auction", verification="none", direction="add", when=DEC2025,
       drivers=["D1"], named=["clean", "batsol", "power"], reached=[])),

    ("N-76", "Art. 26(4)",
     "when applied as award criteria, a minimum weight of 5 % and a combined weight of between 15 % and 30 % of the award criteria", "",
     O(duty="Give each sustainability and resilience criterion at least 5% weight, and 15% to 30% combined, when applying them as award criteria.",
       addressee="Member States designing renewable energy auctions", cls=S,
       trigger="sustainability and resilience criteria applied as award criteria", frequency="per auction",
       verification="none", direction="add", when=DEC2025,
       drivers=["D1"], named=["clean", "batsol", "power"], reached=[],
       note="The sentence sets a weighting a Member State must apply -- a design duty on the auction. Pass A reads the demand advantage the weighting creates for producers and files it as incentive/business. The object rule is exactly what is in dispute here.")),

    ("N-77", "Art. 26(5)",
     "Member States shall not be obliged to apply the considerations relating to the pre-qualification and award criteria laid down in paragraph 1 where, by applying those criteria, they would incur disproportionate costs.", "",
     O(duty="Apply the auction pre-qualification and award criteria where doing so would cost disproportionately -- presumed above a 15% cost difference per auction.",
       addressee="Member States designing renewable energy auctions", cls=S,
       trigger="estimated cost difference above 15% per auction", frequency="per auction",
       verification="none", direction="rem", when=DEC2025,
       drivers=[], named=["clean", "batsol", "power"], reached=[])),

    ("N-78", "Art. 26(7)",
     "Paragraphs 1 to 5 shall apply to at least 30 % of the volume auctioned per year per Member State or alternatively to at least 6 Gigawatt per year per Member State.", "",
     O(duty="Apply the auction regime to at least 30% of the volume auctioned per year, or alternatively at least 6 GW per year.",
       addressee="Member States designing renewable energy auctions", cls=S, trigger="annual auctioned volume",
       frequency="annual", verification="none", direction="add", when=DEC2025,
       drivers=["D5"], named=["clean", "batsol", "power"], reached=[],
       note="The provision that decides how much of the market the regime touches, with its own carve-outs in Art. 26(10)-(11) for sub-10 MW installations, undersubscribed volumes and low-volume Member States. Pass A folds the 30% into an incentive row's benefit statement rather than carrying it.")),

    ("N-79", "Art. 28(1)",
     "shall design those schemes in such a way as to promote the purchase by beneficiaries of net-zero technology final products with a high sustainability and resilience contribution", "while considering the accessibility of the schemes for citizens living in energy poverty.",
     O(duty="Design any new or updated purchase-support scheme to favour products with a high sustainability and resilience contribution, by paying more for them or by making them the eligibility condition.",
       addressee="Member States, regional and local authorities and bodies governed by public law", cls=S,
       trigger="setting up or updating a scheme incentivising purchase of net-zero final products",
       frequency="per scheme", verification="none", direction="add", when=DEC2025,
       drivers=["D1"], named=NZT, reached=["build", "auto"])),

    ("N-80", "Art. 28(2)",
     "shall not exceed 5 % of the cost of the net-zero technology final product for the consumer, with the exception of schemes targeting citizens living in energy poverty", "",
     I(benefit="Buyers of qualifying net-zero final products can receive additional compensation of up to 5% of the product's cost, and up to 15% under schemes targeting citizens in energy poverty.",
       addressee="Households, companies and consumers buying under a public support scheme", cls=H,
       trigger="the product meets the Art. 28(4) sustainability and resilience criteria",
       frequency="per purchase", verification="self-declaration", direction="add", when=DEC2025,
       value_drivers=["V1"], frictions=["F1"], named=NZT, reached=["build", "auto"],
       opportunity_basis=dict(text="shall not exceed 5 % of the cost of the net-zero technology final product for the consumer", kind="rate"))),

    ("N-81", "Art. 28(3)",
     "Any net-zero technology final product shall be entitled to apply to join the scheme at any time.", "",
     R(benefit="Any net-zero final product may apply to join a purchase-support scheme at any time, assessed openly against a published pass mark.",
       addressee="Manufacturers of net-zero technology final products", cls=B,
       trigger="an existing purchase-support scheme", frequency="per scheme",
       verification="competent authority", direction="add", when=DEC2025,
       value_drivers=["V2"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="Any net-zero technology final product shall be entitled to apply to join the scheme at any time.", kind="conferral"))),

    ("N-82", "Art. 28(5)",
     "Member States shall publish on a single free access website all information relating to schemes pursuant to paragraph 1", "",
     O(duty="Publish all information on purchase-support schemes for each relevant net-zero final product on one free-access website.",
       addressee="Member States", cls=S, trigger="a purchase-support scheme", frequency="per scheme",
       verification="none", direction="add", when=DEC2025, drivers=["D1", "D4"], named=NZT, reached=[])),

    # ================================================ Chapters V-VIII, the rest
    ("N-83", "Art. 31(1)",
     "Member States shall strive to identify whether the learning programmes developed by that Academy are equivalent to the specific qualifications required by the host Member State", "the differences between the learning programmes developed by the Academies and the specific qualifications required by that host Member State, and how to achieve equivalence.",
     O(duty="Assess whether an Academy's learning programmes are equivalent to national qualifications for regulated professions, publish the results, and tell the Platform the reasons where equivalence is not found or not sought.",
       addressee="Member States", cls=S, trigger="an Academy completing learning content and materials",
       frequency="every two years", verification="none", direction="add",
       when="Within nine months of an Academy completing its content, then every two years",
       drivers=["D1", "D5"], named=NZT, reached=[])),

    ("N-84", "Art. 33(1)",
     "By 30 March 2025, Member States shall, when setting up net-zero regulatory sandboxes, establish or designate one or more contact points.", "",
     O(duty="Establish or designate sandbox contact points, one sole contact point per request.",
       addressee="Member States", cls=S, trigger="setting up net-zero regulatory sandboxes", frequency="one-off",
       verification="none", direction="add", when="By 30 March 2025", drivers=["D4"], named=NZT, reached=[])),

    ("N-85", "Art. 33(2)",
     "at the request of any company, organisation or consortium developing innovative net-zero technologies that fulfils the eligibility and selection criteria", "",
     R(benefit="A company, organisation or consortium developing innovative net-zero technologies can require a Member State to set up a regulatory sandbox for it, if eligible and selected.",
       addressee="Companies, organisations and consortia developing innovative net-zero technologies", cls=B,
       trigger="a request meeting the eligibility and selection criteria", frequency="per project",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="Member States shall establish net-zero regulatory sandboxes, in close collaboration with industry and, where relevant, research institutes, the social partners and civil society, in accordance with paragraph 1 at the request of any company, organisation or consortium developing innovative net-zero technologies", kind="conferral"))),

    ("N-86", "Art. 33(5)",
     "Competent authorities shall ensure that any significant risk to health, safety or the environment identified during the development and testing of innovative net-zero technologies", "until such risk is mitigated.",
     O(duty="Publicly communicate any significant risk to health, safety or the environment found during sandbox testing and immediately suspend development and testing until it is mitigated.",
       addressee="Competent authorities supervising net-zero regulatory sandboxes, and the participants they supervise",
       cls=S, trigger="a significant risk identified during sandbox development or testing",
       frequency="if it happens", verification="competent authority", direction="add", when=EIF,
       drivers=["D6"], named=NZT, reached=[],
       note="The stop button on a sandbox, and the exceptional-risk safeguard that follows it. A participant weighing the sandbox needs to know the testing can be halted mid-programme; the register carries only the liability rule.")),

    ("N-87", "Art. 33(6)",
     "Participants in the net-zero regulatory sandbox shall remain liable under applicable Union and Member States’ liability law for any material harm inflicted on third parties", "",
     O(duty="Carry full liability under Union and national law for material harm caused to third parties by sandbox testing.",
       addressee="Participants in net-zero regulatory sandboxes", cls=B,
       trigger="material harm to third parties from sandbox testing", frequency="if it happens",
       verification="none", direction="add", when=EIF, drivers=["D6"], named=NZT, reached=[])),

    ("N-88", "Art. 33(7)",
     "The duration of the net-zero regulatory sandbox may be extended through the same procedure upon agreement of the national competent authority.", "",
     R(benefit="A sandbox can be extended beyond its original duration by agreement with the national competent authority, through the same procedure.",
       addressee="Participants in net-zero regulatory sandboxes", cls=B,
       trigger="agreement of the national competent authority", frequency="per project",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="The duration of the net-zero regulatory sandbox may be extended through the same procedure upon agreement of the national competent authority.", kind="procedure"))),

    ("N-89", "Art. 34(1)(a)",
     "provide SMEs and start-ups with priority access to the net-zero regulatory sandboxes", "",
     R(benefit="SMEs and start-ups get priority access to net-zero regulatory sandboxes where they meet the eligibility conditions.",
       addressee="SMEs and start-ups developing innovative net-zero technologies", cls=B,
       trigger="an SME or start-up meeting the Art. 33 eligibility conditions", frequency="per project",
       verification="competent authority", direction="add", when=EIF,
       value_drivers=["V3"], frictions=["F4"], named=NZT, reached=[],
       right_basis=dict(text="provide SMEs and start-ups with priority access to the net-zero regulatory sandboxes to the extent that they fulfil the eligibility conditions laid down in Article 33", kind="scope"))),

    ("N-90", "Art. 34(2)",
     "Member States shall take into account the specific interests and needs of SMEs and start-ups, and provide adequate administrative support to take part in the net-zero regulatory sandboxes.", "",
     O(duty="Take account of SME and start-up needs, give them adequate administrative support to take part in sandboxes, and tell them what financial support is available.",
       addressee="Member States", cls=S, trigger="SME and start-up participation in sandboxes",
       frequency="continuous", verification="none", direction="add", when=EIF,
       drivers=[], named=NZT, reached=[])),

    ("N-91", "Art. 42(2)-(3)",
     "obstacles to trade in net-zero technologies or in goods that use net-zero technologies within the internal market and their potential drivers", "by 15 March 2027 and every three years thereafter.",
     O(duty="Collect and report at least every three years on trade obstacles, market and price developments, manufacturing capacity and employment, SME participation, permitting outcomes and durations, sandboxes, and CO2 stored underground.",
       addressee="Member States", cls=S, trigger="data collection duties under Art. 42(2)",
       frequency="every three years", verification="none", direction="add",
       when="By 15 March 2027, every three years thereafter",
       drivers=["D1", "D4", "D5"], named=NZT, reached=[])),

    ("N-92", "Art. 47(2)",
     "Member States and the Commission shall ensure the protection of trade and business secrets and other sensitive, confidential and classified information obtained and processed in application of this Regulation", "",
     O(duty="Protect the trade and business secrets and other sensitive, confidential and classified information obtained under the Regulation, including in the recommendations and measures taken on it.",
       addressee="Member States and the Commission", cls=S,
       trigger="information obtained and processed in application of the Regulation", frequency="continuous",
       verification="none", direction="add", when=EIF, drivers=[], named=NZT, reached=[],
       note="What a promoter's business plan, timetable and injection-capacity plan are protected by once filed. The register carries the filing duties and nothing on their confidentiality.")),

    ("N-93", "Art. 48",
     "in Annex I, in the first column, a new row ‘R. Net-zero technology manufacturing projects’ is added;", "including for the purposes of Article 18(1) of that Regulation and contact points established or designated pursuant to Article 33(1) thereof.",
     O(duty="Carry net-zero technology manufacturing projects in the Single Digital Gateway: a new information area, the permit procedures and their outputs, and the single points of contact as assistance services.",
       addressee="Member States and the Commission, through the Single Digital Gateway", cls=S,
       trigger="net-zero technology manufacturing and strategic projects", frequency="one-off",
       verification="none", direction="add", when=EIF, drivers=["D1", "D4"], named=NZT, reached=[])),
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
            "addressee": meta["addressee"],
            "class": meta["cls"],
            "trigger": meta["trigger"],
            "frequency": meta["frequency"],
            "verification": meta["verification"],
            "direction": meta["direction"],
            "article": article,
            "when": meta["when"],
            "source_text": span,
            "drivers": meta.get("drivers", []),
            "sectors_named": meta["named"],
            "sectors_reached": meta["reached"],
            "provision_id": None,
            "file": "nzia",
            "source_url": SOURCE_URL,
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
    print(f"nzia pass B: {len(rows)} rows")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")
    if write:
        (HERE / "nzia_pass_b.json").write_text(
            json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written nzia_pass_b.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

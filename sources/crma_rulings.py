"""
The rulings on the CRMA reconciliation. One entry per open item in the frozen
docket (crma_reconciliation_docket.json), checked by reconciliation_gate.py.

Same discipline as cbam_rulings.py and nzia_rulings.py. What is distinctive
here is on the pass side rather than the register side: the second pass MISSED
SIX PROVISIONS the first pass caught -- Arts. 11(2), 27(4), 31(11), 32(1), 33
and 47, registered as CPRM-05, CEXW-03, CFP-02, CFM-01, CCNF-01 and CPEN-01.
reconcile.py cannot report that, because it reports Pass-B-only rows and has no
symmetric list, so it is recorded here and in the crosswalk comment. It is the
strongest evidence available that the two reads are independent: a pass built by
editing the register could not have holes the register does not have.

  classification -> "pass_a" keeps the register's reading and forbids
                    reclass_from; "pass_b" requires the row to have moved and
                    to record what it was.
  date           -> now_signature is the exact date set the row must commit to
                    in the register AND in the pass.
  promote        -> a register row carrying that pass row's pass_origin.
  reject         -> a reason, and no register row carrying it.
"""

PASS_FILE = "crma_pass_b.json"
DATA_FILE = "crma"

_OBJECT_RULE = (
    "benefit_axis.py sets measure_type by the OBJECT the provision acts on, not by the "
    "duty-bearer its sentence names. The second pass followed the operative verb to the "
    "Commission both times. "
)

# --------------------------------------------------------------------------
# CLASSIFICATION -- both to Pass A, on the rule NZIA's three were decided on
# --------------------------------------------------------------------------
CLASSIFICATION = {
    "CSP-01": dict(
        pass_id="C-04", ruling="pass_a",
        now=dict(measure_type="right", direction="add"),
        reason=(
            _OBJECT_RULE +
            "Art. 6(1) is the Commission's duty to recognise, and what recognition produces "
            "is the Strategic Project STATUS -- priority permitting, the financing subgroup, "
            "the offtake system. The status is the object. Decided the same way as NZIA "
            "SP-01 on the same mechanism three days of work earlier in the same register; "
            "the only difference between the two acts is that CRMA's recogniser is the "
            "Commission and NZIA's is the Member State, which changes who is bound and not "
            "what the provision does.")),
    "COFF-01": dict(
        pass_id="C-42", ruling="pass_a",
        now=dict(measure_type="incentive", direction="add"),
        reason=(
            _OBJECT_RULE +
            "Art. 17 sets up a market: offtakers post bids with volumes, qualities, prices "
            "and durations, promoters post offers, the Commission introduces them. The "
            "object is demand-side access that a project developer did not previously have, "
            "which is a support movement -- opportunity_basis kind 'existence', because what "
            "moved is the mechanism itself and there is no rate or amount in the article to "
            "quote. Filed as a Commission duty it would say the Commission must run a "
            "system and say nothing about what a promoter gets, which is the half that "
            "matters. "
            "Pass B's C-42 is not promoted alongside it, unlike NZIA's N-76: Art. 26(4) of "
            "NZIA imposed a weighting a Member State had to apply and nothing in the "
            "register said so, whereas here the Commission-side duty adds no obligation on "
            "any tracked actor.")),
}

# --------------------------------------------------------------------------
# APPLICATION DATES -- all three to Pass B
# --------------------------------------------------------------------------
DATES = {
    "CBEN-01": dict(pass_id="C-01", ruling="pass_b", now_signature=["y2030"],
                    reason="Art. 5(1)(a) states one date and it is 2030: extraction 10 %, "
                    "processing 40 %, recycling 25 % of annual consumption BY 2030. The "
                    "register dated it to entry into force, which is when the duty to work "
                    "towards the benchmark starts and not what the row commits to. A reader "
                    "filtering the register by date would have seen a 2024 capacity target."),
    "CBEN-02": dict(pass_id="C-02", ruling="pass_b", now_signature=["y2030"],
                    reason="Art. 5(1)(b), the 65 % single-country import ceiling, same "
                    "sentence structure and the same error."),
    "CMAG-01": dict(pass_id="C-71", ruling="pass_b",
                    now_signature=["24 may 2029", "y2029"],
                    reason="Art. 28(1). Both passes read the same two dates -- two years "
                    "after the labelling implementing act, and 24 May 2029 for MRI devices, "
                    "motor vehicles and category L vehicles. The register's wording put "
                    "'entry into force' in front of the implementing act, and the date "
                    "signature cannot tell that phrase from a commitment to the "
                    "REGULATION's entry into force, so the row read as if it bit in 2024. "
                    "The substance did not move; the wording that misrepresented it did. "
                    "CMAG-02 and CMAG-03 carried the identical phrase and were corrected "
                    "with it: reconcile.py did not flag them only because their pass "
                    "counterparts commit to no parseable date at all, which the date check "
                    "skips rather than reports. Fixing the one that surfaced and leaving its "
                    "two siblings wrong would be repairing the symptom."),
}

CONSEQUENTIAL_DATES = {}


def _p(register_id, reason):
    return dict(ruling="promote", register_id=register_id, reason=reason)


def _r(reason):
    return dict(ruling="reject", reason=reason)


# --------------------------------------------------------------------------
# PASS-B-ONLY -- 36 promoted, 1 rejected
# --------------------------------------------------------------------------
_SPOC = ("Art. 9 gives the single point of contact a role and the register carried only its "
         "creation. ")

PASS_B_ONLY = {
    "C-03": _p("CRMAB-BEN-03",
               "Art. 5(2). The demand-side limb of the benchmark article: moderate the "
               "expected increase in Union consumption below the Art. 44(1) reference "
               "projection through technological progress and resource efficiency. The "
               "register carried the supply-side benchmarks only."),
    "C-05": _p("CRMAB-SP-10",
               "Art. 6(3). Recognition does not affect any requirement applicable under "
               "Union, national or international law. The limit on the whole status -- a "
               "register carrying the privileges without it overstates what recognition "
               "buys."),
    "C-07": _p("CRMAB-SP-11",
               "Art. 7(3)-(4). The open call with at least four cut-off dates a year, and "
               "the 30-day completeness response. A promoter cannot plan a filing without "
               "the window; the register carried only the 90-day decision that follows it."),
    "C-08": _p("CRMAB-SP-12",
               "Art. 7(8). An objection by the host Member State ends the application, and "
               "for third-country projects the Commission may not approve without that "
               "country's explicit approval. A veto over the entire route, unrecorded."),
    "C-10": _p("CRMAB-SP-13",
               "Art. 7(10). The 90-day decision deadline can be extended by up to 90 days "
               "where the application is complex or the cut-off was oversubscribed, on "
               "notice at least 20 days before expiry. The register stated the deadline as "
               "if it were absolute."),
    "C-11": _p("CRMAB-SP-14",
               "Art. 7(11). Before recognition is withdrawn the promoter gets reasons, an "
               "opportunity to reply, and a reply the Commission must take into account. "
               "CSP-04 registers the loss of every right; the process that must run first "
               "belongs with it."),
    "C-20": _p("CRMAB-SPC-02",
               _SPOC + "Art. 9(3)-(4): facilitate and coordinate the permit-granting "
               "process, provide the Art. 18 information, be the SOLE contact, and help the "
               "promoter understand any administrative matter."),
    "C-21": _p("CRMAB-SPC-03",
               _SPOC + "Art. 9(5): the promoter can reach the named administrative unit "
               "handling its file, and that unit keeps its responsibilities until the "
               "promoter has been notified of a change. A continuity guarantee against "
               "reorganisation mid-permit."),
    "C-22": _p("CRMAB-SPC-04",
               _SPOC + "Art. 9(6): all documents may be filed electronically. NZIA's "
               "equivalent is registered as SPC-02; CRMA's was not."),
    "C-23": _p("CRMAB-SPC-05",
               _SPOC + "Art. 9(7): valid studies, permits and authorisations already issued "
               "are taken into account and no duplicates required. NZIA's equivalent is "
               "SPC-03, and it is one of the few relief rows either act contains."),
    "C-24": _p("CRMAB-SPC-06",
               _SPOC + "Art. 9(8): easy access to dispute-settlement information and "
               "procedures, including alternative dispute resolution."),
    "C-26": _p("CRMAB-PRM-08",
               "Art. 10(3). 'Project promoters AND all authorities concerned shall ensure "
               "that that process is carried out in the most rapid way possible.' The "
               "priority track carries a duty for the promoter too, and the register had "
               "only the conferring paragraphs of Art. 10."),
    "C-30": _p("CRMAB-PRM-09",
               "Art. 11(4). Six months more for extraction and three for processing or "
               "recycling, case by case. The register stated the 27/15 and 24/12 month "
               "limits without their extension."),
    "C-31": _p("CRMAB-PRM-10",
               "Art. 11(5). The screening decision -- whether a full environmental impact "
               "assessment is needed at all -- must be made within 30 days of the developer "
               "submitting the required information, by derogation from Directive "
               "2011/92/EU. One of the sharpest accelerations in the act."),
    "C-36": _p("CRMAB-ENV-04",
               "Art. 12(6). The 30-day scoping-opinion duty does not apply to projects "
               "already in permitting when recognised, and Arts. 12(2)-(5) apply to them "
               "only for steps not yet completed. CENV-01 registered the duty without the "
               "class it does not reach."),
    "C-37": _p("CRMAB-PLAN-01",
               "Art. 13(1). Planning authorities must consider making room for critical raw "
               "materials projects in zoning, spatial and land use plans, with priority to "
               "built, industrial, brownfield and mined land. No planning row existed."),
    "C-38": _p("CRMAB-PLAN-02",
               "Art. 13(2). The plan-level strategic environmental and habitats assessments "
               "are combined, covering water bodies and the marine environment."),
    "C-39": _p("CRMAB-INF-03",
               "Art. 14(2). Every permitting decision is published in an easily "
               "understandable form, with all decisions on one project on one website."),
    "C-40": _p("CRMAB-SP-15",
               "Art. 15(2). The host Member State takes measures to facilitate timely "
               "implementation, including help with administrative and reporting compliance "
               "and with community involvement. The state-side counterpart of the promoter's "
               "own reporting duties."),
    "C-43": _p("CRMAB-INF-01",
               "Art. 18(1). Online, centralised publication of the points of contact, the "
               "permit-granting and related processes, financing and investment services, "
               "funding possibilities and business support services. The exact twin of "
               "NZIA Art. 7, which the register carries as INF-01. A whole article missing."),
    "C-44": _p("CRMAB-INF-02",
               "Art. 18(2). The Commission publishes centralised online information on how "
               "Strategic Project recognition works and what it is worth."),
    "C-45": _p("CRMAB-EXP-01",
               "Art. 19(1)-(2). National exploration programmes: mineral mapping, "
               "geochemical campaigns, geoscientific surveys, reprocessing of existing "
               "survey data, reviewed every five years. The act's entire upstream "
               "information layer, and the register had no row in it."),
    "C-46": _p("CRMAB-EXP-02",
               "Art. 19(6). Free-access maps of mineral occurrences with UN Framework "
               "classification, and processed geophysical and geochemical data and "
               "large-scale mapping released ON REQUEST. What a prospector or processor can "
               "actually obtain about Union deposits."),
    "C-47": _p("CRMAB-MON-04",
               "Art. 20(4). The Commission's public monitoring dashboard. CRSK-03 already "
               "registers a company's right to fall back on 'information published by the "
               "Commission pursuant to Article 20(4)' when suppliers do not answer -- so the "
               "register pointed at a source it did not carry."),
    "C-48": _p("CRMAB-MON-05",
               "Art. 21(1). Member States report new and existing critical raw material "
               "projects on their territory, classified under the UN Framework "
               "Classification for Resources."),
    "C-52": _p("CRMAB-MON-06",
               "Art. 21(3). The collated monitoring data goes to national statistical "
               "authorities and Eurostat, with a designated authority responsible. Where an "
               "operator's survey answers actually end up."),
    "C-54": _p("CRMAB-STK-02",
               "Art. 23(4). In opining on national stocks the Commission and Board must give "
               "particular weight to keeping private operators' incentives to hold their own "
               "strategic stocks. The only provision in the stocks articles that speaks to "
               "firms at all, and the one that protects a private stockholder from being "
               "crowded out by state stockpiling."),
    "C-59": _p("CRMAB-RSK-06",
               "Art. 24(5). A large company MAY take the risk assessment to its board. "
               "CRSK-05 registers the version a Member State can make compulsory under "
               "Art. 24(6); this is the default that applies everywhere else, and carrying "
               "only the compulsory limb misstated the baseline."),
    "C-61": _p("CRMAB-JP-03",
               "Art. 25(1)-(4). The demand-aggregation system itself: open and transparent "
               "to all interested Union undertakings, with a competition-impact assessment "
               "first and minimum participation volumes set with SMEs in mind. CJP-01 "
               "registers the joint-negotiation faculty that participation unlocks and not "
               "the participation route."),
    "C-65": _p("CRMAB-CIR-03",
               "Art. 26(3). Discounts, monetary rewards and deposit-refund systems to "
               "encourage re-use and the collection and treatment of waste from products "
               "with recovery potential. THE ONLY SUPPORT INSTRUMENT IN THE ACT, and the "
               "register had no incentive row for it. Optional for the Member State, which "
               "is a reason to record the conditionality, not a reason to omit the measure."),
    "C-69": _p("CRMAB-EXW-04",
               "Art. 27(2). What the preliminary economic assessment study must contain -- "
               "quantities and concentrations, technical and economic recoverability, and "
               "the estimation methods used. The content specification is what makes the "
               "study expensive and it is stated separately from the duty to produce one."),
    "C-70": _p("CRMAB-EXW-05",
               "Art. 27(8). Where national property, mineral or environmental law stops the "
               "authority sampling a closed facility alone, it must seek the cooperation of "
               "the operator or owner. A duty landing on the FORMER operator of a CLOSED "
               "facility, a party with no other obligation under the act."),
    "C-73": _p("CRMAB-MAG-08",
               "Art. 28(5)-(6). Two reliefs inside the magnet regime: motor-level "
               "information where the magnets sit only in electric motors, and one product "
               "passport instead of a separate data carrier where another Union act already "
               "requires a passport. The register carried the burden and neither relief."),
    "C-82": _p("CRMAB-FM-02",
               "Art. 32(2). Non-compliant products and materials may still be SHOWN at trade "
               "fairs, exhibitions and demonstrations behind a visible non-compliance sign. "
               "A conferred faculty; CFM-01 carried only the free-movement duty on Member "
               "States."),
    "C-83": _p("CRMAB-CNF-02",
               "Art. 43, amending Art. 4(5) of Regulation (EU) 2019/1020. Products covered "
               "by this Regulation join the list requiring an economic operator ESTABLISHED "
               "IN THE UNION before they may be placed on the market. Pass A read "
               "Arts. 40-43 as procedural amendments; this one creates an establishment "
               "requirement reaching every non-EU manufacturer of a covered product, which "
               "is a scope fact, not plumbing."),
    "C-84": _p("CRMAB-REP-01",
               "Art. 45(1), second subparagraph. 'Economic operators shall not be required "
               "to submit information in addition to the information provided in the context "
               "of the provisions listed in the first subparagraph.' A ceiling on what a "
               "Member State may ask of operators when assembling its annual report -- real "
               "relief, stated once, and absent from the register."),

    # ---- rejection
    "C-19": _r(
        "Art. 9(2). The website listing every point of contact with its address and "
        "electronic contact details. CSPC-01's duty statement already carries it -- "
        "'establish or designate single points of contact ... and list them on an accessible "
        "website' -- and its span is the paragraph this row quotes. Registering it again "
        "would double-count one duty. The rest of Art. 9 is promoted above precisely because "
        "it is NOT in CSPC-01."),
}

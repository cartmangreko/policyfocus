"""
The rulings on the NZIA reconciliation. One entry per open item in the frozen
docket, and reconciliation_gate.py refuses to pass unless every one of them is
both ruled here and EVIDENCED in data/nzia.json.

Same ledger discipline as cbam_rulings.py, and for the same reason: once the
corrections are applied reconcile.py reports zero, and zero proves nothing on
its own -- a reconciliation that never ran reports zero too. The open items are
frozen in nzia_reconciliation_docket.json exactly as reconcile.py produced them
before anything was ruled, and the gate reads that file, not a fresh run.

HOW THIS ONE DIFFERS FROM CBAM'S
================================
CBAM's twelve disagreements all went to Pass B. NZIA's three go to PASS A, and
that is the more interesting result. All three are the same argument -- a
provision that binds a Member State in order to confer something on a firm --
and Pass B read the duty-bearer every time while Pass A read the object. The
benefit axis says measure_type follows THE OBJECT THE PROVISION ACTS ON, so
Pass A is right on the rule the register already runs on, and IAA PRM-04 decided
the identical question on the identical mechanism before either pass existed.

Recording three rulings that change nothing in the register is the point of a
ledger. "Pass A holds" is a decision; leaving the disagreement unruled is not.

The date disagreements went the other way: both to Pass B, and they are real
errors in the register that nothing else would have caught.

WHERE THE VALUE ACTUALLY WAS
============================
Not in the three classification splits. In the 38 provisions Pass B carried and
Pass A did not: 32 are promoted below. Ten of those put a duty or a faculty on a
FIRM rather than an authority, and one of them -- Art. 20(2), the five-year
design life and fair-and-open-access rule on CO2 storage sites -- is a duty on
operators sitting inside an article that otherwise states a Union target. A
thematic read has no reason to open it. That is the case for paragraph sweeps.

WHAT A RULING HAS TO SAY
========================
  classification -> ruling "pass_a" means the register keeps what it says and
                    must NOT carry reclass_from for it; ruling "pass_b" means
                    the row moved and reclass_from must record what it was.
                    `now` is checked against the register either way.
  date           -> `now_signature` is the set of dates the row's `when` must
                    commit to, in the register AND in its Pass B counterpart.
  promote        -> a register row must exist carrying that pass row's
                    pass_origin.
  reject         -> a reason, and NO register row carrying that pass_origin.
"""

PASS_FILE = "nzia_pass_b.json"
DATA_FILE = "nzia"

# The argument all three classification rulings turn on, stated once.
_OBJECT_RULE = (
    "benefit_axis.py sets measure_type by the OBJECT the provision acts on, not by "
    "the instrument or the duty-bearer its sentence happens to name. Pass B followed "
    "the operative verb to the Member State; the object is what the Member State is "
    "made to hand over. "
)

# --------------------------------------------------------------------------
# CLASSIFICATION DISAGREEMENTS -- all three to Pass A
# --------------------------------------------------------------------------
CLASSIFICATION = {
    "SPC-02": dict(
        pass_id="N-06", ruling="pass_a",
        now=dict(measure_type="right", direction="add"),
        reason=(
            _OBJECT_RULE +
            "Art. 6(4) is one passive sentence -- 'Project promoters shall be allowed to "
            "submit any documents ... in electronic form' -- and the only party it names "
            "is the promoter. What the paragraph moves is a faculty the promoter did not "
            "hold against a Member State that ran the file on paper. Pass B's reading is "
            "not wrong about who must act; it is wrong about what the provision is for. "
            "Filed as a state duty it would disappear into the permitting plumbing rows "
            "and stop answering the question a promoter asks of it.")),
    "SP-01": dict(
        pass_id="N-30", ruling="pass_a",
        now=dict(measure_type="right", direction="add"),
        reason=(
            _OBJECT_RULE +
            "Art. 13(1) reads 'Member States shall recognise as net-zero strategic "
            "projects ...', and the object of that recognition is the STATUS, which is "
            "what unlocks Arts. 15 and 16. IAA PRM-04 and PRM-06 decided this exact "
            "question on this exact mechanism -- automatic strategic-project status -- and "
            "were themselves reclassifications away from the obligation side, recorded in "
            "reclass_from. Deciding it the other way here would put the register in "
            "disagreement with itself across two files describing one regime.")),
    "AUC-02": dict(
        pass_id="N-76", ruling="pass_a",
        now=dict(measure_type="incentive", direction="add"),
        reason=(
            _OBJECT_RULE +
            "Art. 26(4) fixes what the sustainability and resilience criteria are WORTH -- "
            "5 % each, 15-30 % combined -- and a weight in an award formula is a price "
            "advantage for the producers who score on it. That is a support movement, so "
            "incentive/add with a rate basis. "
            "BUT Pass B was right that the duty half was missing: nothing in the register "
            "said a Member State must apply those weights at all. N-76 is therefore also "
            "PROMOTED, as NZIAB-AUC-04, sharing provision_id nzia-26 with this row. The "
            "disagreement was half a disagreement and half a gap, and it is disposed of as "
            "both.")),
}

# --------------------------------------------------------------------------
# APPLICATION-DATE DISAGREEMENTS -- both to Pass B
# --------------------------------------------------------------------------
_ART49 = (
    "Art. 49(3) reads: 'Until 30 June 2026, Article 25(1) shall apply only to contracts "
    "concluded by central purchasing bodies ... and for contracts of a value equal to or "
    "higher than EUR 25 million.' It names Art. 25(1) and nothing else. "
)

DATES = {
    "PP-02": dict(pass_id="N-69", ruling="pass_b", now_signature=["29 june 2024", "y2024"],
                  reason=_ART49 + "PP-02 is Art. 25(3), the obligation to attach a social, "
                  "cybersecurity or on-time-delivery condition to net-zero works contracts. "
                  "The register carried the carve-out across its whole procurement family "
                  "by theme rather than by provision, which understated who is bound before "
                  "30 June 2026: on the words of Art. 49(3) this applies to every covered "
                  "works contract from 29 June 2024, with no EUR 25 million floor and no "
                  "central-purchasing-body limit."),
    "PP-03a": dict(pass_id="N-71", ruling="pass_b", now_signature=["29 june 2024", "y2024"],
                   reason=_ART49 + "PP-03a is Art. 25(7), the third-country origin cap, the "
                   "evidence duty and the 10 % charge. Same error as PP-02 and a more "
                   "expensive one: the row that tells a tenderer it can be charged 10 % of "
                   "contract value was dated as if it did not bite on smaller contracts "
                   "until mid-2026."),
}

# PP-03b has no Pass B counterpart -- Pass B read only the tenderer's side of
# Art. 25(7) -- so it is not in the docket and cannot be ruled from it. It is
# the incentive half of PP-03a's pair, sharing provision_id nzia-25-7, and a
# pair whose two halves state different application dates for one provision is
# incoherent however each half was reached. Ruled here explicitly rather than
# fixed silently, and the gate checks it alongside the two above.
CONSEQUENTIAL_DATES = {
    "PP-03b": dict(follows="PP-03a", now_signature=["29 june 2024", "y2024"],
                   reason="The demand-side half of Art. 25(7). Moves with PP-03a because it "
                   "is the same provision read from the other side; leaving it on the "
                   "Art. 49(3) wording would have the register give one provision two "
                   "application dates."),
}

# --------------------------------------------------------------------------
# PASS-B-ONLY PROVISIONS -- 32 promoted, 6 rejected
#
# Promotions keep Pass B's reading intact: extract_nzia.py builds them by
# importing the pass row and relabelling it, rather than by retyping it, so a
# promoted row cannot drift from what the second pass actually said.
# --------------------------------------------------------------------------
def _p(register_id, reason):
    return dict(ruling="promote", register_id=register_id, reason=reason)


def _r(reason):
    return dict(ruling="reject", reason=reason)


PASS_B_ONLY = {
    # ---- benchmarks
    "N-02": _p("NZIAB-BEN-02",
               "Art. 5(1)(b). The register carried the 2030 40 % benchmark and not the 2040 "
               "15 %-of-world-production one, which is the only forward-looking capacity "
               "target in the act and the one the Art. 42 monitoring is measured against."),

    # ---- permitting
    "N-14": _p("NZIAB-PRM-07",
               "Art. 9(2). The 18-month limit for projects whose capacity is NOT measured in "
               "GW. PRM-01 carries only the GW-denominated limbs of Art. 9(1), so every "
               "energy-intensive industry decarbonisation project under Art. 3(17) -- steel, "
               "cement, chemicals, glass -- fell outside the register's account of its own "
               "permitting deadlines."),
    "N-16": _p("NZIAB-PRM-08",
               "Art. 9(5). The promoter gets no less than 30 days to supplement the "
               "environmental impact assessment report, and the clock the time limits run on "
               "stops while it does. A deadline whose stop conditions are unrecorded is not "
               "a deadline a reader can rely on."),
    "N-17": _p("NZIAB-PRM-09",
               "Art. 9(6). A single 3-month extension on the nature, complexity, location or "
               "size of the project. The register stated the limits as if they were absolute."),
    "N-18": _p("NZIAB-PRM-10",
               "Art. 9(7). A further 6-month extension where the project raises exceptional "
               "health and safety risks. Distinct trigger from N-17 and separately available, "
               "so together they can put 9 months on an 18-month limit."),
    "N-25": _p("NZIAB-ENV-03",
               "Art. 10(5). Consultation of the public and the authorities is held between 30 "
               "and 85 days, extended to at most 90. Consultation is where a permitting "
               "timetable is usually lost, and this is the provision that bounds it."),
    "N-27": _p("NZIAB-PLAN-01",
               "Art. 11(1). Planning authorities must CONSIDER making room for these projects "
               "in zoning, spatial and land use plans, with priority to built and brownfield "
               "land, and all spatial planning data goes online. The register had no planning "
               "row at all, and land is where a project is enabled or blocked before any "
               "permit is applied for."),
    "N-28": _p("NZIAB-PLAN-02",
               "Art. 11(2). The plan-level strategic environmental and habitats assessments "
               "are combined, covering water bodies and the marine environment, without "
               "lengthening the act's time limits. The plan-level twin of ENV-01."),
    "N-29": _p("NZIAB-INF-02",
               "Art. 12(2). Every decision under the permitting section and Arts. 8, 15, 16 "
               "and 28 is published in an easily understandable form, with all decisions on "
               "one project on one website. Publication duties are already registered on the "
               "same footing at SCH-04 and PRM-03."),

    # ---- strategic projects
    "N-31": _p("NZIAB-SP-10",
               "Art. 13(3). THE CCS ROUTE INTO STRATEGIC STATUS: a storage project in the "
               "Union contributing to the Art. 20 objective and holding a Directive "
               "2009/31/EC permit application, plus any capture project and any transport "
               "infrastructure attached to it. The register carried Art. 13(1) and 13(5) "
               "only, so it described a CCS chapter without saying how a CCS project reaches "
               "the priority track the chapter depends on."),
    "N-32": _p("NZIAB-SP-11",
               "Art. 13(4). The cohesion twin of SP-05: projects in less developed and "
               "transition regions and Just Transition Fund territories get the status on a "
               "written request with no formal application. Same mechanism as the row the "
               "register already had, different qualifying condition, and carrying one "
               "without the other made the fast route look narrower than it is."),
    "N-34": _p("NZIAB-SP-12",
               "Art. 13(6). A Member State may refuse recognition for a technology it does "
               "not accept in its energy mix, and must say so publicly and as soon as "
               "possible. This decides whether the strategic-project route exists at all "
               "where a promoter is building -- the first thing to check, and absent."),
    "N-37": _p("NZIAB-SP-13",
               "Art. 14(4). Where the Member State misses the one-month deadline the promoter "
               "can demand a new one, capped at 30 days past the original. SP-04 carries the "
               "remedy for a REJECTION; this is the only remedy for silence, which is the "
               "more common failure."),
    "N-39": _p("NZIAB-SP-14",
               "Art. 14(7). The promoter is informed and heard before a recognition is "
               "repealed. SP-06 registers the loss of every right attached to the status; the "
               "process that must run first belongs with it."),
    "N-41": _p("NZIAB-SP-15",
               "Art. 14(9). The Commission's openly available registry of net-zero strategic "
               "projects -- the public record of who holds the status, and a Commission-class "
               "duty of the kind the IAA file already carries five of."),
    "N-42": _p("NZIAB-SP-16",
               "Art. 15(1). 'Project promoters AND all authorities concerned shall ensure "
               "that ... the relevant processes are treated in the most rapid way possible.' "
               "The priority track names the promoter first among those bound. The register "
               "carried only the conferring paragraphs of Art. 15."),
    "N-46": _p("NZIAB-SP-17",
               "Art. 15(4), final sentence. The promoter must participate in the urgency "
               "procedures. Pass A carries it inside SP-09's span, where it is a sentence "
               "attached to a right rather than a duty with its own addressee, trigger and "
               "frequency. The split is the honest read; SP-09 keeps the conferral."),

    # ---- valleys
    "N-48": _p("NZIAB-VAL-03",
               "Art. 17(2). A Valley may only be designated with a defined geographic and "
               "technology scope, priority to built and brownfield land, a strategic "
               "environmental assessment and where applicable a habitats assessment, and "
               "synergies with renewables acceleration areas. The area-level assessment is "
               "what buys the project-level streamlining, and VAL-01 carried only the "
               "support plan."),
    "N-50": _p("NZIAB-VAL-04",
               "Art. 18(1). Sections II and III apply to individual projects inside a Valley "
               "and each Valley gets its own single point of contact -- the provision that "
               "connects the Valley regime to the permitting regime."),
    "N-51": _p("NZIAB-VAL-05",
               "Art. 18(3). Templates naming the specific permits a Valley project needs, "
               "carrying the features and mitigation measures that decide whether an "
               "environmental impact assessment is required at all. This is the practical "
               "half of the Valley regime and the register did not have it."),

    # ---- CO2
    "N-54": _p("NZIAB-CO2-11",
               "Art. 20(2). 'All storage sites shall be designed to operate for a minimum of "
               "five years and shall respect the principles of fair and open access provided "
               "in a transparent and non-discriminatory manner.' A DUTY ON OPERATORS inside "
               "an article that otherwise states a Union objective, which is exactly how a "
               "thematic read loses it. It is also the provision that decides whether a "
               "captured-CO2 emitter can get into someone else's store, so it stands behind "
               "every CBAM- and ETS-side decarbonisation route that ends in geological "
               "storage. The single most valuable find in this reconciliation."),
    "N-55": _p("NZIAB-CO2-12",
               "Art. 21(1)(a). Member States publish the data on every area where a storage "
               "site could be permitted, saline aquifers included. CO2-01 registers the duty "
               "on licence holders and this is the duty on the state that sits beside it."),
    "N-58": _p("NZIAB-CO2-13",
               "Art. 21(3). Where no storage projects are in progress, the Member State "
               "reports instead on how it will decarbonise industry, including cross-border "
               "transport to stores elsewhere. This is what an emitter in a Member State with "
               "no domestic store is actually told to expect."),
    "N-66": _p("NZIAB-CO2-14",
               "Art. 23(9). Exempted producers may contract under Art. 23(5)(b)-(c) only for "
               "capacity ABOVE the exempted contribution and above the sum of exempted "
               "contributions. CO2-06 registered the exemption without its anti-double-"
               "counting condition, which made the relief read wider than it is."),

    # ---- procurement and auctions
    "N-70": _p("NZIAB-PP-05",
               "Art. 25(6). No discrimination against, or unjustified different treatment of, "
               "a provider or net-zero products from another Member State -- the internal-"
               "market limit on a resilience regime built out of origin conditions. A "
               "supplier bidding across a border needs it and the register had nothing."),
    "N-72": _p("NZIAB-PP-06",
               "Art. 25(8). The origin cap, the evidence duty and the 10 % charge do not "
               "apply where the technology originates with a party to the GPA or another "
               "relevant agreement. This decides how much of world supply the cap actually "
               "reaches; registering PP-03a without it overstated the cap's reach."),
    "N-74": _p("NZIAB-PP-07",
               "Art. 25(11). Where applying the resilience contribution drew no suitable "
               "tenders, the buyer may re-run without it or use the negotiated procedure. "
               "PP-04 is the escape hatch from the SUSTAINABILITY requirements; this is the "
               "distinct escape hatch from the ORIGIN cap."),
    "N-76": _p("NZIAB-AUC-04",
               "Art. 26(4), promoted alongside the CLASSIFICATION ruling on AUC-02 above. "
               "AUC-02 keeps the producer-side reading; this carries the Member State's duty "
               "to apply the weights, sharing provision_id nzia-26. Extracted as a pair the "
               "way PP-03a and PP-03b are."),
    "N-78": _p("NZIAB-AUC-05",
               "Art. 26(7). The regime bites on at least 30 % of annual auctioned volume or "
               "alternatively 6 GW per Member State per year. Pass A folded this figure into "
               "an incentive row's benefit sentence, which is not the same as carrying the "
               "provision: the scope limb has its own carve-outs in Art. 26(10)-(11) for "
               "sub-10 MW installations, undersubscribed volumes and low-volume Member "
               "States, and none of that was anywhere in the register."),

    # ---- sandboxes and SMEs
    "N-86": _p("NZIAB-SBX-04",
               "Art. 33(5). Any significant risk to health, safety or the environment found "
               "in testing is publicly communicated and development and testing are "
               "immediately suspended until it is mitigated. A participant weighing a sandbox "
               "needs to know the programme can be halted mid-flight; SBX-03 gave it only the "
               "liability rule."),
    "N-88": _p("NZIAB-SBX-05",
               "Art. 33(7). The sandbox can be extended by agreement with the national "
               "competent authority, through the same procedure. A faculty attached to the "
               "conferral SBX-02 already registers."),
    "N-90": _p("NZIAB-SME-02",
               "Art. 34(2). Member States take account of SME and start-up needs, give "
               "adequate administrative support to take part, and inform them of available "
               "financial support. SME-01 carries the priority access in Art. 34(1)(a) and "
               "not the support that makes it usable."),

    # ---- confidentiality
    "N-92": _p("NZIAB-CNF-01",
               "Art. 47(2). Trade and business secrets and other sensitive, confidential and "
               "classified information obtained under the Regulation are protected. The "
               "register carries the duties to file a business plan, a project timetable and "
               "an injection-capacity plan, and said nothing about what protects them once "
               "filed. Art. 47(4) even lets a Member State object to the Commission "
               "disclosing aggregated Art. 23 information on national security grounds."),

    # ---- rejections
    "N-04": _r(
        "Art. 6(2). Tools helping a promoter find the right contact point where a Member "
        "State designated several. It is a delivery detail of the single-point-of-contact "
        "duty SPC-01 already registers, on the web page INF-01 already registers, and it "
        "creates no step a promoter or an authority takes that those two do not already "
        "describe."),
    "N-05": _r(
        "Art. 6(3). That the single point of contact is the SOLE contact, coordinates "
        "submission and notifies the comprehensive decision. This is the definition of the "
        "role SPC-01 creates -- SPC-01's duty statement already says 'responsible for "
        "facilitating and coordinating the permit-granting process'. Registering it "
        "separately would double-count one duty."),
    "N-08": _r(
        "Art. 6(6). Easy access to dispute-settlement information and procedures. Art. 7(b), "
        "which INF-01 registers, requires exactly this information to be published online: "
        "'the permit-granting process, including information on dispute settlement'. Same "
        "duty reached from the other side."),
    "N-09": _r(
        "Art. 6(7). Sufficient qualified staff and sufficient financial, technical and "
        "technological resources for the authorities in the permit chain. An administrative "
        "capacity provision addressed to the Member State's own organisation: it binds no "
        "operator, sets no threshold, and nothing turns on it that a reader could act on. "
        "scope.md's exclusion of purely institutional provisions is the boundary, and it is "
        "applied inside an act the same way it is applied between acts."),
    "N-19": _r(
        "Art. 9(8). Written reasons for an extension and the new expected decision date. It "
        "is the notice condition attached to the extensions themselves, which are promoted "
        "as NZIAB-PRM-09 and NZIAB-PRM-10; the reasons duty has no life apart from them and "
        "both rows state it."),
    "N-26": _r(
        "Art. 10(6). Sufficient staff and resources for the environmental assessment "
        "authorities. Rejected on the same ground as N-09, and deliberately given the same "
        "reason rather than a differently worded one: two provisions rejected on one "
        "principle should be legible as one decision."),
}

"""
The rulings on the CBAM reconciliation. One entry per open item, and the gate
in reconciliation_gate.py refuses to pass unless every one of them is both
ruled here and EVIDENCED in data/cbam.json.

WHY A LEDGER AND NOT JUST A FIXED REGISTER
==========================================
Once the corrections are applied, reconcile.py reports zero disagreements. That
number proves nothing on its own: a reconciliation that was never run reports
zero too, and so does one where the passes were quietly edited to agree. The
ETS/IAA verify_pass docstring already names that failure -- "agreement between
two passes means nothing once one of them has been corrected to agree" -- and
the same trap is one step further along here, where the REGISTER is what got
corrected.

So the open items are frozen first, in cbam_reconciliation_docket.json, which is
the disagreement report exactly as reconcile.py produced it at commit be65a46,
before anything was ruled. The gate reads that frozen docket, not the current
one, and requires a ruling for every item in it. A disagreement cannot be
disposed of by making it disappear; it has to be answered.

WHAT A RULING HAS TO SAY
========================
Each ruling names the outcome and carries the evidence the gate then checks in
the register:

  classification  -> `was` must appear in the row's reclass_from, and `now` must
                     be what the row currently says. Correcting a row without
                     recording what it used to say fails.
  date            -> `now_signature` must be the set of dates the row's `when`
                     commits to AND the set its Pass B counterpart commits to.
                     Requiring the literal expected signature is the point: two
                     rows agreeing on the same wrong date would satisfy
                     reconcile and must not satisfy this.
  promote         -> a register row must exist carrying pass_origin for that
                     pass row.
  reject          -> a reason, and NO register row carrying that pass_origin.
                     A rejection that quietly got promoted anyway is a failure
                     in the same way an unruled disagreement is.

`ruling` is "pass_b" where the second read was right, "pass_a" where the first
was, "both" where each had half. All twelve here went to Pass B, which is worth
saying plainly rather than leaving to be counted: the second read did not merely
add coverage, it overturned the first read every time the two differed.
"""

PASS_FILE = "cbam_pass_b.json"
DATA_FILE = "cbam"

# --------------------------------------------------------------------------
# CLASSIFICATION DISAGREEMENTS
# --------------------------------------------------------------------------
CLASSIFICATION = {
    "FIN-06": dict(
        pass_id="B-21",
        ruling="pass_b",
        was=dict(direction="add"),
        now=dict(measure_type="obligation", direction="rem"),
        reason=(
            "Art. 9(2) third sentence. The register read 'certified by a person that is "
            "independent from the authorities of the third country' as a new requirement. "
            "The prior sentence required independence from the authorised CBAM declarant "
            "AND from those authorities; the replacement keeps the second limb only. So "
            "nothing is added -- what is removed is the limb that stopped a declarant "
            "certifying through a person it controls. Requirement becomes Simplification. "
            "The provision is a REPLACEMENT rather than a deletion, so the deletion gate "
            "never demanded a prior_rule and the error was invisible to every automatic "
            "check; only reading the consolidation found it. prior_rule is attached now."),
    ),
    "ELEC-02": dict(
        pass_id="B-56",
        ruling="pass_b",
        was=dict(measure_type="right", direction="add"),
        now=dict(measure_type="obligation", direction="rem"),
        reason=(
            "Annex IV point 4.2.2. The register filed this `right`/add -- Entitlement -- on "
            "the operative verb 'may be used'. The verb is there and it is not new: the "
            "demonstration route, the permissive verb and the comparison against both "
            "benchmarks are quoted from the prior rule. Only the metric changes, from 'CO2 "
            "emission factor' to 'emission factor for electricity'. A faculty the addressee "
            "already held cannot be conferred, so the object rule returns it to the "
            "obligation side: what moved is the basis on which the liability is computed. "
            "The benefit-axis guardrail could not catch this, because a basis check runs "
            "against THIS act and a pre-existing faculty is invisible to it -- which is the "
            "general lesson, not a CBAM one."),
    ),
}

# --------------------------------------------------------------------------
# APPLICATION-DATE DISAGREEMENTS
#
# Article 2 of the proposal gives three sentences, not a date per provision, and
# the second and third name amending POINTS by number. Nine rows were matched
# against the wrong list, in both directions. The tenth, DECL-01, had the right
# date inside wording that read as the wrong one.
# --------------------------------------------------------------------------
_ART2 = ("Art. 2 names the amending points that take each date: 'Points 1 and 6 of "
         "Annex II' from 1 January 2026; 'Article 1(6), point (a), Article 1(8), "
         "points (a), (b) and (c), Article 1(21), (23), and (24), and point 2 of "
         "Annex II' from 1 January 2028; everything else on entry into force. ")

DATES = {
    "DECL-01": dict(pass_id="B-12", ruling="pass_b", now_signature=["entry-into-force"],
                    reason=_ART2 + "Art. 1(5)(a)(2) is in neither list. The date was "
                    "already right; the wording named Art. 1(6)(a)'s 2028 date first and "
                    "read as if this row took it."),
    "DECL-06": dict(pass_id="B-19", ruling="pass_b", now_signature=["entry-into-force"],
                    reason=_ART2 + "Art. 1(6)(b) is not in the 2028 list -- only "
                    "Art. 1(6), point (a) is."),
    "CALC-06": dict(pass_id="B-20", ruling="pass_b", now_signature=["entry-into-force"],
                    reason=_ART2 + "Art. 1(6)(c) is not in the 2028 list."),
    "DATA-02": dict(pass_id="B-28", ruling="pass_b", now_signature=["entry-into-force"],
                    reason=_ART2 + "Art. 1(8)(d) is not in the 2028 list, which names "
                    "points (a), (b) and (c) of Art. 1(8) only."),
    "DATA-03": dict(pass_id="B-29", ruling="pass_b", now_signature=["entry-into-force"],
                    reason=_ART2 + "Same provision as DATA-02, same omission."),
    "CALC-02": dict(pass_id="B-53", ruling="pass_b", now_signature=["1 january 2028", "y2028"],
                    reason=_ART2 + "This is point 2 of Annex II, which the 2028 sentence "
                    "names. The register had it at 1 January 2026, reading it as Annex II "
                    "point 1 -- two years early."),
    "CALC-03": dict(pass_id="B-54", ruling="pass_b", now_signature=["1 january 2028", "y2028"],
                    reason=_ART2 + "Also point 2 of Annex II. The register had it on entry "
                    "into force."),
    "ELEC-04": dict(pass_id="B-58", ruling="pass_b", now_signature=["1 january 2026", "y2026"],
                    reason=_ART2 + "Annex II point 6(a). Recital 53 confirms the intent: "
                    "the conditions for applying actual embedded emissions in imported "
                    "electricity 'should apply to imports of electricity that occurred as "
                    "of 1 January 2026'."),
    "ELEC-05": dict(pass_id="B-59", ruling="pass_b", now_signature=["1 january 2026", "y2026"],
                    reason=_ART2 + "Annex II point 6(b). Same sentence as ELEC-04."),
    "ELEC-06": dict(pass_id="B-60", ruling="pass_b", now_signature=["1 january 2026", "y2026"],
                    reason=_ART2 + "Annex II point 6(c). Same sentence as ELEC-04."),
}

# --------------------------------------------------------------------------
# PASS-B-ONLY PROVISIONS
# Eight promoted, one rejected.
# --------------------------------------------------------------------------
PASS_B_ONLY = {
    "B-48": dict(ruling="promote", register_id="CBAMB-SCP-07",
                 reason=(
                     "Annex I point (1) REPLACES the existing 'Iron and steel' table while "
                     "point (2) ADDS the 'Combined metal products' table, and the first pass "
                     "read only the added one. The replacement brings in 2601 12 00 "
                     "agglomerated iron ores and concentrates, 7312 10 stranded wire and "
                     "cables, 7314 39 00 unplated welded grill, two spring headings, two "
                     "household-articles headings and 7325 other cast articles. Iron ore is "
                     "an upstream input entering CBAM scope, which the downstream story does "
                     "not describe at all. A missed scope extension is the most expensive "
                     "kind of miss the register can make.")),
    "B-51": dict(ruling="promote", register_id="CBAMB-ELEC-09",
                 reason=(
                     "Annex IV point 1(e) redefines 'emission factor for electricity' from "
                     "the intensity of electricity CONSUMED in production to the weighted "
                     "average CO2 intensity of electricity PRODUCED in a geographic area. "
                     "ELEC-01, ELEC-02 and ELEC-03 are each nothing but the substitution of "
                     "that term into Annex IV points 4.2.1, 4.2.2 and 4.3 -- so without this "
                     "row the register asserted their effect while not holding the definition "
                     "that produces it. It also applies from 1 January 2026, before all "
                     "three.")),
    "B-52": dict(ruling="promote", register_id="CBAMB-ELEC-10",
                 reason=(
                     "Annex IV point 1(f) adds 'and that involves the physical delivery of "
                     "electricity' to the definition of a power purchase agreement, "
                     "excluding financial and virtual PPAs from the actual-emissions route. "
                     "It sits in the same Annex II point as ELEC-04's relaxation and cuts the "
                     "other way, so registering the relief without it overstated ELEC-04.")),
    "B-06": dict(ruling="promote", register_id="CBAMB-SCP-08",
                 reason=(
                     "Art. 2(11) gains the EEA-incorporation ground and the Art. 28a urgency "
                     "procedure for amending the Annex III lists. Annex III listing is what "
                     "switches the CBAM off for a country's goods, so this is a scope power "
                     "rather than the institutional plumbing it resembles -- and ELEC-08 "
                     "already registers the Art. 2(8) listing assessment on that footing.")),
    "B-07": dict(ruling="promote", register_id="CBAMB-VER-02",
                 reason=(
                     "Art. 2(12) gains a mutual-recognition limb for third-country "
                     "accreditation bodies accrediting verifiers under Art. 18. The object is "
                     "the verification condition, which today forces a third-country "
                     "installation to use a Union-accredited verifier.")),
    "B-14": dict(ruling="promote", register_id="CBAMB-DECL-07",
                 reason=(
                     "Art. 6(6) extends the declaration format to carry information 'for each "
                     "installation and country of origin or other third country and type of "
                     "goods', the carbon price paid, and the Art. 9(4) default carbon price. "
                     "That is a per-installation reporting granularity the prior sentence did "
                     "not demand, not a bare empowerment.")),
    "B-15": dict(ruling="promote", register_id="CBAMB-ANTI-05",
                 reason=(
                     "Art. 6(6a) is the instrument that decides the reach of DECL-01: until "
                     "it names the goods and the evidence, that duty binds nobody. ANTI-03 "
                     "and ANTI-04 are both registered on the same reasoning; this was visible "
                     "only as a `pending` note.")),
    "B-41": dict(ruling="promote", register_id="CBAMB-CUST-05",
                 reason=(
                     "Art. 25(6) changes 'paragraph 2' to 'paragraphs 2 and 3', bringing the "
                     "competent-authority information flow under implementing-act control for "
                     "the first time. The thinnest of the eight, and promoted because the "
                     "flow it newly governs is a duty the register already carries as "
                     "CUST-03; leaving it out would have registered three of four Art. 25 "
                     "amendments.")),
    "B-24": dict(ruling="reject", register_id=None,
                 reason=(
                     "REJECTED, not missed. Art. 1(7)(b)(2) adds a free-standing Art. 9(5) "
                     "subparagraph stating that the certifier's qualifications 'shall include "
                     "the granting of accreditation by a national accreditation body'. The "
                     "proposal states that same rule twice: the identical sentence also sits "
                     "inside the Art. 9(5) first subparagraph, which FIN-08 already quotes "
                     "whole. Promoting it would enter a second register row for a rule the "
                     "register states once -- the call the ETS reconciliation made for 22 of "
                     "its 27 blocked rows. The duplication is a drafting slip in the proposal "
                     "and is recorded in FIN-08's note rather than reproduced as a row.")),
}

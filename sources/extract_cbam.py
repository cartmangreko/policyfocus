"""
Extract the CBAM extension proposal (COM(2025) 989, CELEX 52025PC0989) into
data/cbam.json.

Anchor-based, in the extract.py idiom: every source_text is SLICED out of the
fetched source by a start/end anchor rather than retyped, so a span cannot drift
from the act by a stray character. A missing or ambiguous anchor is a hard
failure, not a warning -- a row whose evidence cannot be located is not written.

    python3 extract_cbam.py --check     # report, write nothing
    python3 extract_cbam.py             # write ../data/cbam.json

WHY THIS FILE IS ALMOST ENTIRELY OBLIGATION-SIDE
================================================
CBAM is a charge, not a support scheme. The object rule in benefit_axis.py sends
a provision to the incentive side only when it moves the support itself -- its
amount, rate, eligibility or existence. Nothing here does: the favourable
provisions in this proposal narrow a duty, ease a condition or lower the basis on
which the CBAM liability is computed, which is the obligation side, direction
"rem" (Simplification). Reading a lower default value or a dropped condition as
an "Opportunity" would be exactly the instrument-not-object error the rule
exists to stop -- the same error that put nine ETS rows on the wrong side.

`right` is used where the text genuinely confers a faculty the addressee did not
hold, on the same test as the register's other right rows: the operative verb.
"An operator may disclose ... to another operator" confers; "shall not apply to"
does not.

THE SECOND READ EXISTS, AND ITS DISAGREEMENTS HAVE BEEN RULED ON
================================================================
This file used to say it could not claim a second read. extract_cbam_pass_b.py
is that read; it found 2 classification disagreements, 10 application-date
disagreements and 9 provisions this file did not carry, and every one of them
has now been answered in the rows below.

  * FIN-06 was Requirement and is Simplification. Art. 9(2)'s replaced third
    sentence looked like a new certification duty; against the consolidation it
    is the surviving HALF of a two-limb test, and the dropped limb is
    independence from the declarant itself.
  * ELEC-02 was Entitlement and is Simplification. The faculty it conferred was
    quoted from the prior rule -- only the metric changed.
  * Nine `when` values were wrong, in both directions, because Article 2 gives
    three dates and names amending POINTS by number rather than dating each
    provision. The dates are now chosen from the EIF/J2026/J2028 constants
    below, which carry the list membership that justifies them.
  * Eight provisions were promoted, under the CBAMB- prefix with `pass_origin`.
    One, B-24, was rejected as a duplicate of a rule FIN-08 already quotes.

The audit trail is not in this docstring. cbam_reconciliation_docket.json is the
disagreement report frozen before any of it was ruled, cbam_rulings.py answers
every item in it, and reconciliation_gate.py refuses to pass unless each ruling
is evidenced in data/cbam.json. Run that gate, not this file, to ask whether
CBAM is reconciled.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

ACT = "cbam_ext.txt"
ANNEX = "cbam_ext_annexes.txt"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52025PC0989"

# The act being amended, for prior_rule spans only. Deliberately NOT in
# benefit_axis.FILE_SOURCES: a source_text must be evidence for what THIS act
# says, and a span counts if it matches any file listed there. prior_rule sits
# outside that check and carries `status` and `source_document` instead.
PRIOR = "cbam_ext_prior_02023R0956-20251020.txt"
PRIOR_DOC = "Regulation (EU) 2023/956 as consolidated at 2025-10-20, CELEX 02023R0956-20251020"

# Where the operative part starts, so an anchor cannot accidentally match the
# explanatory memorandum, which paraphrases the same provisions in similar
# words. Article 1 begins at the "Amendments to Regulation (EU) 2023/956"
# heading; everything before it is recitals and memorandum.
OPERATIVE_ANCHOR = "Amendments to Regulation (EU) 2023/956"

# ---------------------------------------------------------------------------
# THE THREE APPLICATION DATES, read off Article 2 of the proposal ONCE.
#
# Article 2 does not give a date per provision. It gives three sentences, and
# the second and third name amending POINTS by number:
#
#   "Points 1 and 6 of Annex II, shall apply from 1 January 2026."
#   "However, Article 1(6), point (a), Article 1(8), points (a), (b) and (c),
#    Article 1(21), (23), and (24), and point 2 of Annex II shall apply from
#    1 January 2028."
#
# Everything not named in either falls back on entry into force, the third day
# after publication. So `when` is read off a DIFFERENT SENTENCE from every other
# field on a row, by matching that row's amending point against two lists -- and
# the first pass got nine of them wrong, in both directions. Naming the lists as
# constants is the fix: the date is now chosen by picking a constant, and the
# constant carries the list membership that justifies it.
EIF = "from entry into force (third day after publication), Art. 2"
J2026 = "applies from 1 January 2026 per Art. 2 (points 1 and 6 of Annex II)"
J2028 = "applies from 1 January 2028 per Art. 2"

B = "business"
S = "state"

# (id, source-file, start anchor, end anchor, metadata)
# end anchor "" means: take the start anchor alone as the span.
ROWS: list[tuple] = [

    # ---------------------------------------------------------------- scope
    ("SCP-01", ACT,
     "Upon its incorporation in the EEA Agreement, this Regulation also applies to processed products",
     "provided that they are imported to those countries.",
     dict(measure_type="obligation", direction="add",
          duty="CBAM applies to processed products made from Annex I goods under inward processing where they are re-exported to Norway or Iceland, bringing those consignments into the CBAM regime.",
          addressee="Importers and authorised CBAM declarants of processed products re-exported to Norway or Iceland",
          cls=B, trigger="processed products from Annex I goods resulting from inward processing are re-exported to the customs territory of Norway or Iceland and imported there",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(a), inserting Art. 2(2a) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation in the EEA Agreement",
          drivers=["D7", "D1"], named=["steel", "alu"], reached=[],
          pending="Detailed conditions for applying the CBAM to these products are left to Commission implementing acts under the new Art. 2(2a).")),

    ("SCP-02", ACT,
     "Upon its incorporation into the EEA Agreement, by way of derogation from paragraphs 1 and 2, this Regulation shall not apply",
     "within the customs territory of the respective EFTA States.",
     dict(measure_type="obligation", direction="rem",
          duty="Comply with the CBAM regime for goods originating in third countries that were previously released for free circulation in the customs territory of an EFTA State that has incorporated the CBAM.",
          addressee="Customs declarants importing goods previously released for free circulation in a CBAM-integrated EFTA State",
          cls=B, trigger="goods previously released for free circulation in the customs territory of an EFTA State that incorporated the CBAM",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(b), adding a subparagraph to Art. 2(4) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation into the EEA Agreement",
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-2-4",
          note="The CBAM integrated area with the EEA EFTA countries: a consignment already cleared in an integrated EFTA State is not charged twice. A duty is switched off, no support moves. Object rule -> obligation side, direction rem. Its proof condition is the companion row SCP-03.")),

    ("SCP-03", ACT,
     "The customs declarant shall bear responsibility for the availability of this proof at the time of lodging of the customs declaration.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Bear responsibility for having documentation proving prior release for free circulation in an EFTA State available at the moment the customs declaration is lodged.",
          addressee="Customs declarants relying on the EFTA prior-free-circulation exemption",
          cls=B, trigger="customs declarant claims the Art. 2(4) EFTA exemption in a customs declaration",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(b), adding a subparagraph to Art. 2(4) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation into the EEA Agreement",
          drivers=["D1", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-2-4",
          note="The condition attached to the SCP-02 exemption. Filed separately because the exemption and the evidence burden that gates it fall on the same declarant but move in opposite directions.")),

    ("SCP-04", ANNEX,
     "‘[Combined metal products",
     "(excl. plated or coated with zinc or coated with plastics)",
     dict(measure_type="obligation", direction="add",
          duty="A new 'Combined metal products' category enters CBAM scope, pulling downstream steel- and aluminium-containing manufactured goods into the embedded-emissions declaration and certificate-surrender regime for the first time.",
          addressee="Importers and authorised CBAM declarants of downstream steel- and aluminium-containing goods",
          cls=B, trigger="importation of goods listed in the new 'Combined metal products' table of Annex I",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (2) adding the 'Combined metal products' table to Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4", "D2", "D6"],
          named=["steel", "alu"], reached=["auto", "build"],
          note="The headline measure of the proposal. Scope extension is the strongest form of 'add': these importers were outside the regime altogether (D7). The table runs to prefabricated buildings, metal furniture, trailer parts and medical instruments, which is why the reach is construction and automotive rather than the basic-material sectors alone.")),

    ("SCP-05", ANNEX,
     "ex- 9406 90 90 – Prefabricated buildings, containing steel or aluminium",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Prefabricated buildings containing steel or aluminium are named in CBAM scope, carrying the embedded-emissions declaration and surrender duty into construction products.",
          addressee="Importers of prefabricated buildings containing steel or aluminium",
          cls=B, trigger="importation of prefabricated buildings falling within CN ex- 9406 90 90 containing steel or aluminium",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (2) adding the 'Combined metal products' table to Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4"], named=["build"], reached=["steel", "alu"],
          note="Carried as its own row because it is the clearest case of the scope extension reaching a sector CBAM has never touched: the addressee is a construction-products importer, not a metals importer.")),

    ("SCP-06", ACT,
     "The Commission shall monitor the situation at Union level with a view to monitoring the impact of the CBAM on the Union internal market.",
     "to remove this good from Annex I until those serious and unforeseeable circumstances have passed.",
     dict(measure_type="obligation", direction="rem",
          duty="Comply with CBAM for a good whose inclusion in Annex I is causing severe harm to the Union internal market through serious and unforeseen price effects.",
          addressee="Importers of goods withdrawn from Annex I under the safeguard",
          cls=B, trigger="Commission finds that the inclusion of a good in Annex I causes severe harm to the internal market due to serious and unforeseen circumstances affecting prices",
          frequency="if it happens", verification="none",
          article="Art. 1(17), inserting Art. 27a of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu"], reached=["auto", "build"],
          pending="No good has been removed: the safeguard is an empowerment to adopt delegated acts, and none exists yet.",
          note="A safeguard valve on scope. The object is the scope of the CBAM duty, which the Commission may withdraw a good from. Object rule -> obligation side, direction rem. It is not an incentive: no support amount, rate or eligibility moves, and nothing is conferred on any firm.")),

    # -------------------------------------------------- declaration content
    ("DECL-01", ACT,
     "‘(e) where applicable for the purpose of addressing the risk of misdeclaration resulting from the lack of supply chain traceability, evidence that the goods imported during the preceding calendar year were produced at the declared installation",
     "and at the actual time of production referred to in the CBAM declaration;",
     dict(measure_type="obligation", direction="add",
          duty="Include in the CBAM declaration evidence that the imported goods were actually produced at the declared installation and at the declared time of production.",
          addressee="Authorised CBAM declarants for goods flagged for supply-chain traceability risk",
          cls=B, trigger="goods identified by implementing act as carrying a misdeclaration risk from lack of supply chain traceability",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(a)(2), adding point (e) to Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="Which goods and which specific evidence are set by Commission implementing acts under the new Art. 6(6a).",
          note="Anti-circumvention. A traceability evidence duty attached to the declaration.")),

    ("DECL-02", ACT,
     "(f) where, in accordance with a delegated act adopted in accordance with paragraph 7, the embedded emissions are determined on the basis of actual emissions for a combination of goods and origins that are subject to a high risk of abusive practices",
     "evidence demonstrating that the high risk of abusive practices has not materialised.",
     dict(measure_type="obligation", direction="add",
          duty="Where a goods/origin combination is designated high-risk for abusive practices and actual emissions are claimed, prove in the declaration that the abuse risk has not materialised.",
          addressee="Authorised CBAM declarants claiming actual emissions for high-risk goods/origin combinations",
          cls=B, trigger="declarant claims actual emissions for a combination of goods and origins designated by delegated act as high risk of abusive practices",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(a)(2), adding point (f) to Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The high-risk combinations, and the evidence that discharges the duty, are set by delegated acts under the new Art. 6(7).",
          note="A reversed burden of proof: the declarant must demonstrate a negative. Filed as its own row because the trigger (designation of a goods/origin combination) is different from DECL-01's.")),

    ("DECL-03", ACT,
     "‘(b) the total embedded emissions in the goods referred to in point (a) of this paragraph, expressed in tonnes of CO2e emissions per megawatt-hour of electricity",
     "verified in accordance with Article 8;",
     dict(measure_type="obligation", direction="add",
          duty="Report total embedded emissions per tonne of goods (or per MWh for electricity), and have them verified where actual emissions are supplied by the operator through the CBAM registry.",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="submission of the annual CBAM declaration",
          frequency="annual", verification="accredited third party",
          article="Art. 1(5)(a)(1), replacing point (b) of Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D2", "D4", "D5"], named=["steel", "alu", "cement", "chem", "power"], reached=[])),

    ("DECL-04", ACT,
     "‘(h) EORI number or other national identification number, names and contact information of the persons on behalf of whom the applicant is acting, if applicable.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Identify in the authorisation application, by EORI or national identification number, every person on whose behalf the applicant acts.",
          addressee="Applicants for authorised CBAM declarant status acting on behalf of others",
          cls=B, trigger="application for authorisation as a CBAM declarant on behalf of other persons",
          frequency="one-off", verification="competent authority",
          article="Art. 1(4), replacing point (h) of Art. 5(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D3"], named=[], reached=[],
          note="Indirect-representation transparency: it makes the chain behind an authorised declarant visible to the competent authority.")),

    ("DECL-05", ACT,
     "‘2a. Where the embedded emissions are determined on the basis of actual emissions, the Commission or the competent authority of the Member State where the CBAM declarant is established may",
     "request the authorised CBAM declarant to provide evidence that the goods imported were produced at the installation referred to in the CBAM declaration.",
     dict(measure_type="obligation", direction="add",
          duty="Produce, on request during review of the CBAM declaration, evidence that the imported goods were produced at the installation named in the declaration.",
          addressee="Authorised CBAM declarants determining embedded emissions on actual emissions",
          cls=B, trigger="Commission or competent authority reviews a CBAM declaration based on actual emissions",
          frequency="if it happens", verification="competent authority",
          article="Art. 1(11), inserting Art. 19(2a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="The review-stage counterpart of DECL-01: DECL-01 puts the evidence in the declaration, this lets the reviewer demand it afterwards.")),

    ("DECL-06", ACT,
     "‘5. The authorised CBAM declarant shall keep records of the information disclosed in accordance with Article 10(7) that is required to calculate the embedded emissions",
     "review the CBAM declaration in accordance with Article 19(2).",
     dict(measure_type="obligation", direction="rem",
          duty="Keep the full underlying records required to calculate embedded emissions, rather than the information actually disclosed to the declarant under Art. 10(7).",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="determination of embedded emissions for the CBAM declaration",
          frequency="annual", verification="competent authority",
          article="Art. 1(6)(b), replacing Art. 7(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Streamlining named as such in the explanatory memorandum: the record-keeping duty is narrowed to what the operator actually disclosed under Art. 10(7), which a declarant can hold, instead of the operator's underlying data, which it cannot. A duty narrows. Object rule -> obligation side, direction rem.")),

    # ------------------------------------------------- emissions accounting
    ("CALC-01", ACT,
     "‘2a. Embedded emissions in input materials (precursors) listed in Annex VIII shall be considered in the determination of embedded emissions in goods.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Count the embedded emissions of Annex VIII input materials (precursors) when determining the embedded emissions of the goods.",
          addressee="Operators and authorised CBAM declarants calculating embedded emissions",
          cls=B, trigger="production of CBAM goods using input materials listed in the new Annex VIII",
          frequency="annual", verification="accredited third party",
          article="Art. 1(6)(a), inserting Art. 7(2a) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D2"], named=["steel", "alu"], reached=[],
          note="Widens the emissions base rather than the goods base: the same import now carries more embedded emissions, so more certificates. Companion of CALC-04, which supplies the Annex VIII list.")),

    ("CALC-02", ANNEX,
     "Only input materials (precursors) listed in Annex I and Annex VIII and originating in third countries and territories that are not exempted pursuant to Annex III, Section 1 are to be considered.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Apply the complex-goods calculation counting precursors from both Annex I and the new Annex VIII, excluding those from exempted third countries.",
          addressee="Operators of installations producing complex CBAM goods",
          cls=B, trigger="determination of specific actual embedded emissions of complex goods",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (2) replacing point 3 of Annex IV of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D2"], named=["steel", "alu"], reached=[])),

    ("CALC-03", ANNEX,
     "However, for goods listed in sections ‘Iron and Steel’, ‘Aluminium’ and ‘Combined Metal Goods’ of Annex I, Mi is a function of the content of goods used as input materials (precursors) in the manufacturing of the good.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="For iron and steel, aluminium and combined metal goods, derive the precursor mass from the content of input goods in the finished product rather than from a directly measured mass.",
          addressee="Operators of installations producing iron and steel, aluminium and combined metal goods",
          cls=B, trigger="calculation of embedded emissions for goods in the Iron and Steel, Aluminium or Combined Metal Goods sections of Annex I",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (2) replacing point 3 of Annex IV of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4"], named=["steel", "alu"], reached=["auto", "build"],
          note="The calculation rule that makes the downstream extension operable: without a content-based mass, a manufactured good's precursor emissions cannot be attributed.")),

    ("CALC-04", ANNEX,
     "ex 7204 Ferrous waste and scrap; remelting scrap ingots and steel except post-consumer scrap",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Treat ferrous waste and scrap, other than post-consumer scrap, as a precursor whose embedded emissions count towards the goods.",
          addressee="Operators and declarants using ferrous scrap as an input material",
          cls=B, trigger="use of ferrous waste and scrap other than post-consumer scrap as an input material",
          frequency="annual", verification="accredited third party",
          article="Art. 1(24); Annex III adding Annex VIII to Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4"], named=["steel"], reached=["waste"],
          provision_id="cbam-annex-viii",
          note="The post-consumer scrap carve-out is the load-bearing part: recycled input from end-of-life goods stays outside the emissions base, so scrap-based production is not penalised for material it did not cause to be made.")),

    ("CALC-05", ANNEX,
     "ex 7602 Aluminium waste and scrap except post-consumer scrap",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Treat aluminium waste and scrap, other than post-consumer scrap, as a precursor whose embedded emissions count towards the goods.",
          addressee="Operators and declarants using aluminium scrap as an input material",
          cls=B, trigger="use of aluminium waste and scrap other than post-consumer scrap as an input material",
          frequency="annual", verification="accredited third party",
          article="Art. 1(24); Annex III adding Annex VIII to Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4"], named=["alu"], reached=["waste"],
          provision_id="cbam-annex-viii")),

    ("CALC-06", ACT,
     "‘The implementing acts referred to in the first subparagraph may provide a list of downstream goods for which, due to the complexity of the supply chain and without prejudice to the environmental integrity of the CBAM, no mark-up is to apply.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Bear the mark-up added to default values when declaring downstream goods with complex supply chains.",
          addressee="Importers and declarants of listed downstream goods using default values",
          cls=B, trigger="downstream good placed by implementing act on the list of goods for which no mark-up applies",
          frequency="annual", verification="none",
          article="Art. 1(6)(c), adding a subparagraph to Art. 7(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu"], reached=["auto", "build"],
          pending="No list exists: the relief depends on implementing acts that have not been adopted.",
          note="The mark-up is part of how the liability is computed, not a support: dropping it lowers the quantum of the duty. Object rule -> obligation side, direction rem. Read as Opportunity it would imply CBAM confers a benefit, which it does not.")),

    # ---------------------------------------------------- anti-circumvention
    ("ANTI-01", ACT,
     "‘(35) ‘abusive practices’ are practices pursued by an actor for the purpose of gaining a benefit by unduly avoiding, wholly or partially, the CBAM financial liability",
     "and thereby undermining the effectiveness of the CBAM to address the risk of carbon leakage in the EU.",
     dict(measure_type="obligation", direction="add",
          duty="Refrain from practices whose purpose is to gain a benefit by unduly avoiding, wholly or partly, the CBAM financial liability.",
          addressee="All actors in the CBAM supply chain",
          cls=B, trigger="any practice pursued for the purpose of unduly avoiding CBAM financial liability",
          frequency="n/a", verification="competent authority",
          article="Art. 1(3), adding point (35) to Art. 3 of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          note="A definition, carried as a row because it is the operative hook the whole anti-abuse machinery hangs on -- DECL-02 and the Art. 6(7) designation power both turn on it. Same treatment as Omnibus DD-01, which carries the 'stakeholders' definition as a row.")),

    ("ANTI-02", ACT,
     "‘(c) artificially adjusting the supply chains to make the goods benefit from lower default values.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Refrain from artificially adjusting supply chains so that goods qualify for lower default values; doing so is circumvention.",
          addressee="Importers, declarants and operators in CBAM supply chains",
          cls=B, trigger="alteration of a supply chain whose purpose is to obtain lower default values",
          frequency="n/a", verification="competent authority",
          article="Art. 1(16), adding point (c) to Art. 27(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Names origin-shopping on default values as circumvention. Distinct from ANTI-01: this is a specific practice added to the circumvention list, not the general definition.")),

    ("ANTI-03", ACT,
     "7. The Commission shall monitor at Union level the impact of the CBAM on the Union internal market. Where the Commission, taking into account relevant information",
     "as well as the evidence to be provided to demonstrate that no abuse has taken place.",
     dict(measure_type="obligation", direction="add",
          duty="Monitor the CBAM's internal-market impact, warn importers, declarants, competent and customs authorities of high-risk goods/origin combinations, and legislate the conditions for using actual emissions for them.",
          addressee="European Commission",
          cls=S, trigger="sufficient evidence pointing towards a high risk of abusive practices for a combination of goods and origins",
          frequency="if it happens", verification="none",
          article="Art. 1(5)(c), adding Art. 6(7) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          note="The designation power that DECL-02's duty depends on. Carried as a state-class row because the trigger and addressee are the Commission's, not a firm's.")),

    ("ANTI-04", ACT,
     "The Commission shall adopt the delegated acts referred to in the first subparagraph within three months of finding that there is sufficient evidence pointing towards a high risk of abusive practices",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Adopt the high-risk delegated acts within three months of finding sufficient evidence of a high risk of abusive practices.",
          addressee="European Commission",
          cls=S, trigger="Commission finds sufficient evidence of a high risk of abusive practices",
          frequency="if it happens", verification="none",
          article="Art. 1(5)(c), adding Art. 6(7) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=[], reached=[],
          note="A hard deadline on the Commission, which is what keeps ANTI-03's power from being open-ended. Separated from ANTI-03 because it is a time-bound duty, not a discretion.")),

    # ---------------------------------------------------------- financial
    ("FIN-01", ACT,
     "‘5a. By way of derogation from paragraph 5, where the competent authority finds that the applicant or the authorised CBAM declarant does not demonstrate its financial capacity",
     "The guarantee provided shall be a bank guarantee, payable at first demand, by a financial institution operating in the Union or another form of guarantee which provides equivalent assurance.",
     dict(measure_type="obligation", direction="add",
          duty="Provide a bank guarantee payable at first demand, sized on the certificates that would have to be surrendered, where the competent authority finds financial capacity is not demonstrated.",
          addressee="Applicants and authorised CBAM declarants failing to demonstrate financial capacity",
          cls=B, trigger="competent authority finds the applicant or declarant does not demonstrate financial capacity, including by failing the Art. 22(2) holding requirement",
          frequency="if it happens", verification="competent authority",
          article="Art. 1(9)(a), inserting Art. 17(5a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D3", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-17-guarantee",
          note="The heaviest new burden in the proposal for smaller importers: a first-demand bank guarantee is working capital, and the amount is set on a full year of surrender liability.")),

    ("FIN-02", ACT,
     "Where a guarantee is required in accordance with paragraph 5a, the competent authority shall release the guarantee immediately after 30 September of the second year",
     "Notwithstanding the foregoing, the competent authority may decide to extend the duration of the guarantee where such extension is duly justified.",
     dict(measure_type="obligation", direction="add",
          duty="Leave the guarantee in place until after 30 September of the second surrender year, and for longer where the competent authority justifies an extension.",
          addressee="Authorised CBAM declarants that have provided an Art. 17(5a) guarantee",
          cls=B, trigger="guarantee required under Art. 17(5a)",
          frequency="per period", verification="competent authority",
          article="Art. 1(9)(b), replacing Art. 17(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=[], reached=[],
          provision_id="cbam-17-guarantee",
          note="The duration limb of the FIN-01 guarantee. The extension power has no stated ceiling, which is worth a human read.")),

    ("FIN-03", ACT,
     "‘From 2028, the calculation referred to in the first subparagraph shall be based only on CBAM certificates purchased by the authorised CBAM declarant during that same year.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="From 2028, satisfy the quarterly certificate-holding requirement using only certificates bought in the same year, so certificates carried over from earlier years no longer count.",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="quarterly calculation of the CBAM certificate holding requirement",
          frequency="per quarter", verification="competent authority",
          article="Art. 1(13), adding a subparagraph to Art. 22(2) of Regulation (EU) 2023/956",
          when="from 2028",
          drivers=["D5", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Closes a cash-flow strategy: banking cheap certificates in an earlier year no longer discharges the holding requirement. Tightens a duty, moves no support.")),

    ("FIN-04", ACT,
     "‘For those calendar weeks in which there is no auction on the auction platform, the price of CBAM certificates shall be the average of the closing prices of EU ETS allowances of the last week in which auctions on the auction platform took place.",
     "the price of CBAM certificates shall be the average of that closing price and the closing prices of the last week in which several auctions took place on the auction platform.",
     dict(measure_type="obligation", direction="add",
          duty="Pay the CBAM certificate price as fixed by the fallback rules for weeks with no auction or a single auction.",
          addressee="Authorised CBAM declarants purchasing CBAM certificates",
          cls=B, trigger="calendar week in which no auction, or only one auction, takes place on the auction platform",
          frequency="weekly", verification="none",
          article="Art. 1(12)(a), replacing the second subparagraph of Art. 21(1) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          note="Price-formation plumbing, but it sets the price a declarant actually pays in thin-auction weeks, so it is an economic term of the duty and not merely procedural.")),

    ("FIN-05", ACT,
     "‘The excess CBAM certificates shall be repurchased through the common central platform referred to in Article 20.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Repurchase the excess CBAM certificates through the common central platform on behalf of the Member State where the authorised CBAM declarant is established.",
          addressee="European Commission",
          cls=S, trigger="authorised CBAM declarant requests repurchase of excess CBAM certificates",
          frequency="annual", verification="none",
          article="Art. 1(14), replacing the first sentence of the second subparagraph of Art. 23(1) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=[], reached=[],
          note="Checked against the prior rule (32023R0956 as consolidated) before classifying, because the new sentence reads like a fresh routing rule and is not one: repurchase already ran through the common central platform. What the amendment removes is the Commission's express role as the actor doing it on the Member State's behalf, leaving the sentence in the passive. So the duty that moves is the Commission's, not a declarant's, and this is a state-class row. Nothing changes for a firm -- flagged in the report as the one row here whose company-facing content is nil.")),

    ("FIN-06", ACT,
     "‘The information contained in that documentation shall be certified by a person that is independent from the authorities of the third country.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Have the documentation evidencing a carbon price paid in a third country certified by a person independent from the authorised CBAM declarant AS WELL AS from that country's authorities.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="claim for a reduction of certificates on account of a carbon price paid in a third country",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(1), replacing the third sentence of Art. 9(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-9-2",
          prior=dict(
              start="The information contained in that documentation shall be certified by a\xa0person that is independent from the authorised CBAM declarant and from the authorities of the third country.",
              end="",
              trigger="authorised CBAM declarant keeping documentation to demonstrate a carbon price effectively paid in a third country",
              obligation="The prior third sentence of Art. 9(2) required the certifying person to be independent from the authorised CBAM declarant AND from the authorities of the third country. The replacement keeps the second limb only.",
              source_document=PRIOR_DOC + ", Article 9(2), third sentence",
              note="This is a replacement, not a deletion, so nothing in the pipeline forced the prior text to be resolved and the guardrail could not see the error. Resolving it inverts the row."),
          reclass_from=dict(
              direction="add",
              commit="be65a46",
              note="Read from this act alone the sentence looks like a fresh requirement, and the first pass filed it that way. Against the consolidation it is the surviving HALF of a two-limb test: the dropped limb is independence from the declarant itself, which is what stopped a declarant certifying through a person it controls. Nothing is added; a condition is removed. Found by Pass B as B-21."),
          note="A relaxation that reads as a tightening. The remaining limb -- independence from the third country's authorities -- was already law; what changed is that the certifier may now be connected to the declarant.")),

    ("FIN-07", ACT,
     "‘The independent person referred to in the first subparagraph may be a legal person accredited by a national accreditation body for the relevant scope of accreditation.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Find a certifying person meeting the independence test without the benefit of an express route through national accreditation.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="declarant seeks a certifier for third-country carbon price documentation",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(2), adding a subparagraph to Art. 9(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=[], reached=[],
          provision_id="cbam-9-2",
          note="Names an accredited legal person as an acceptable certifier, which removes the uncertainty FIN-06 would otherwise create about who qualifies. Object is the evidencing duty, eased. Object rule -> obligation side, direction rem.")),

    ("FIN-08", ACT,
     "‘The Commission is empowered to adopt implementing acts, based on the principle of equivalence, concerning the conversion of the yearly average carbon price effectively paid",
     "The Commission is also empowered to regulate the conditions for deducting carbon credits under Article 6 of the Paris Agreement.",
     dict(measure_type="obligation", direction="add",
          duty="Apply the Commission's conversion rules when turning a carbon price paid abroad into a reduction in CBAM certificates, including the evidence of actual payment and any deduction of Paris Agreement Article 6 carbon credits.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="claim for a reduction of CBAM certificates on account of a carbon price paid in a third country",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(b)(1), replacing the first subparagraph of Art. 9(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The conversion methodology, the evidence standard and the treatment of Paris Agreement Art. 6 credits all sit in implementing acts that have not been adopted.",
          note="The mechanism that decides how much a carbon price paid abroad is actually worth against the CBAM liability, and the first time Paris Agreement Art. 6 credits are brought into that calculation. Economically the most consequential of the Art. 9 changes, which is why it is carried separately from the FIN-06/FIN-07 certification pair. The qualifications sentence quoted inside this span is stated a SECOND time by the proposal, as the free-standing subparagraph added by Art. 1(7)(b)(2). Pass B raised that subparagraph as B-24; it was rejected as a promotion rather than registered, because it states the same rule this row already quotes and a second row would make the register say once-stated law twice. The duplication is a drafting slip in the proposal, recorded here rather than reproduced.")),

    # -------------------------------------------------------- electricity
    ("ELEC-01", ANNEX,
     "Specific default values shall be set at the emission factor for electricity in the third country, group of third countries or region within a third country, based on the best data available to the Commission.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Accept default values for imported electricity that reflect fossil generation only, regardless of the exporting country's actual generation mix.",
          addressee="Importers and authorised CBAM declarants of electricity",
          cls=B, trigger="determination of embedded emissions of imported electricity using specific default values",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (3) replacing point 4.2.1 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          note="Rebases the electricity default on the exporting country's actual emission factor rather than on fossil generation alone, so a clean exporter is no longer charged as if it burned coal. The object is the basis on which the liability is computed -- a duty's quantum, not a support. Object rule -> obligation side, direction rem.")),

    ("ELEC-02", ANNEX,
     "Where it can be demonstrated, on the basis of reliable data, that the emission factor for electricity in a third country, a group of third countries or a region within a third country is lower than the specific default value determined by the Commission or lower than the emission factor for electricity in the Union",
     "an alternative default value based on that emission factor for electricity may be used for that third country, group of third countries or region within a third country.",
     dict(measure_type="obligation", direction="rem",
          duty="Take the alternative default value from the CO2 emission factor, rather than from the emission factor for electricity, when demonstrating that the exporting area's electricity is cleaner than the applicable default.",
          addressee="Importers and authorised CBAM declarants of electricity from lower-carbon third countries",
          cls=B, trigger="reliable data demonstrate an electricity emission factor lower than the specific default value or the Union factor",
          frequency="annual", verification="competent authority",
          article="Art. 1(22); Annex II, point (4) replacing point 4.2.2 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          named=["power"], reached=[],
          prior=dict(
              start="Where it can be demonstrated, on the basis of reliable data, that the CO2 emission factor in a third country, a group of third countries or a region within a third country is lower than the specific default value determined by the Commission or lower than the CO2 emission factor in the Union, an alternative default value based on that CO2 emission factor may be used",
              end="",
              trigger="declarant demonstrating a lower electricity emission factor for the exporting area",
              obligation="The prior point 4.2.2 already provided that where reliable data show the CO2 emission factor in a third country, group of third countries or region is lower than the specific default value or than the Union CO2 emission factor, 'an alternative default value based on that CO2 emission factor may be used'. The demonstration route, the permissive verb and the comparison against both benchmarks are all pre-existing.",
              source_document=PRIOR_DOC + ", Annex IV, point 4.2.2, second paragraph",
              note="The ONLY change this provision makes is the metric: 'CO2 emission factor' becomes 'emission factor for electricity', the term redefined by CBAMB-ELEC-09."),
          reclass_from=dict(
              measure_type="right", direction="add",
              commit="be65a46",
              note="Filed Entitlement on the operative verb 'may be used'. The verb is there, but it is not new -- it is quoted from the prior rule. A faculty the addressee already held cannot be conferred, so the `right` test fails and the object rule sends it back to the obligation side: what moved is the basis on which the liability is computed, and the new metric is the lower one for a clean grid. The guardrail could not catch this, because a basis check runs against THIS act and a pre-existing faculty is invisible to it. Found by Pass B as B-56."),
          note="Simplification, not Entitlement. See prior_rule: the demonstration route is older than this proposal.")),

    ("ELEC-03", ANNEX,
     "‘Where a third country, or a group of third countries, demonstrates to the Commission, on the basis of reliable data, that the average electricity mix emission factor or CO2 emission factor of price-setting sources",
     "an alternative default value based on that average electricity mix emission factor or on that average CO2 emission factor shall be established for this country or group of countries.",
     dict(measure_type="obligation", direction="rem",
          duty="Accept the standard default value for indirect emissions where the exporting country's actual electricity mix is cleaner than that default.",
          addressee="Importers of goods with indirect emissions from lower-carbon third countries",
          cls=B, trigger="third country demonstrates to the Commission an average electricity mix or CO2 emission factor lower than the default for indirect emissions",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (5) replacing the second paragraph of point 4.3 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=["steel", "alu", "cement", "chem"],
          note="Reads 'shall be established' and is addressed to the Commission on a third country's demonstration, so unlike ELEC-02 nothing is conferred on the declarant to exercise. The indirect-emissions quantum falls. Object rule -> obligation side, direction rem.")),

    ("ELEC-04", ANNEX,
     "‘(a) the amount of electricity for which the use of actual embedded emissions is claimed is covered by a power purchase agreement between the importer or authorised CBAM declarant and a producer of electricity located in a third country. Power purchase agreements involving intermediaries shall also be allowed",
     "in relation to the electricity for which the use of actual emissions is claimed;",
     dict(measure_type="obligation", direction="rem",
          duty="Hold a power purchase agreement directly with the third-country electricity producer, with no intermediary in the chain, in order to claim actual emissions.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(a) replacing point (a) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=[], named=["power"], reached=[],
          note="Admits intermediated PPAs provided the contractual chain is verifiable, which is what makes the actual-emissions route usable in practice. A condition on a duty is relaxed. Object rule -> obligation side, direction rem. Read with CBAMB-ELEC-10: the same Annex II point that admits intermediaries into the PPA chain also redefines a power purchase agreement to require the physical delivery of electricity. The relief is real but narrower than this row alone suggests -- an intermediated chain qualifies only if the electricity physically moves through it -- and both apply from 1 January 2026.")),

    ("ELEC-05", ANNEX,
     "(b)\n\xa0\xa0\xa0point (b) is deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Demonstrate that the generating installation is directly connected to the Union transmission system, or that no physical network congestion existed at the time of export, in order to claim actual emissions for imported electricity.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(b) deleting point (b) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=[], named=["power"], reached=[],
          prior=dict(
              start="the installation producing electricity is either directly connected to the Union transmission system",
              end="between the installation and the Union transmission system;",
              trigger="authorised CBAM declarant applying actual embedded emissions instead of default values for imported electricity",
              obligation="One of the cumulative criteria in Annex IV point 5 required the generating installation to be directly connected to the Union transmission system, or required a demonstration that no physical network congestion existed anywhere between the installation and the Union transmission system at the time of export.",
              source_document=PRIOR_DOC + ", Annex IV, point 5, point (b)",
              note="Resolving the deleted text is what makes the label defensible. The grid-connection and no-congestion test is a cumulative criterion a declarant had to satisfy, so removing it removes a condition and the row is a Simplification. Note what survives: point (c), the 550 g CO2/kWh cap on the generating installation, is untouched, so this is a relaxation of the physical-delivery proof and not of the emissions standard."),
          note="The span this act supplies is only the amending instruction '(b) point (b) is deleted;'. Everything that decides the valence lives in the prior rule, which is attached rather than inferred.")),

    ("ELEC-06", ANNEX,
     "‘(d) the amount of electricity for which the use of actual embedded emissions is claimed has been firmly nominated to the allocated interconnection capacity",
     "This criterion shall not be fulfilled in cases where transmission capacity for the import of electricity is allocated through implicit capacity allocation;",
     dict(measure_type="obligation", direction="add",
          duty="Firmly nominate the claimed electricity to allocated interconnection capacity across origin, destination and transit, matching production within the same hour, and forgo the claim where capacity is allocated implicitly.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(c) replacing point (d) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=["D4", "D1"], named=["power"], reached=[],
          note="Cuts the other way from ELEC-04: the nomination and hourly-matching test is tightened, and implicit capacity allocation is excluded outright, which shuts the actual-emissions route for market-coupled borders.")),

    ("ELEC-07", ACT,
     "‘Where a third country has requested to integrate its electricity market into that of the Union through market coupling pursuant to an international agreement",
     "the timeline for the implementation of a carbon pricing instrument equivalent to the EU ETS, insofar as electricity generation is concerned.",
     dict(measure_type="obligation", direction="add",
          duty="Conclude, and then honour, a Memorandum of Understanding setting the timeline for the Art. 2(7) exemption and for putting an EU ETS-equivalent carbon price on electricity generation.",
          addressee="Third countries seeking electricity market coupling with the Union, and the Commission",
          cls=S, trigger="third country requests to integrate its electricity market with the Union's through market coupling under an international agreement",
          frequency="if it happens", verification="none",
          article="Art. 1(1)(c), inserting Art. 2(7a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          note="The gateway to the Art. 2(7) electricity exemption. State-class: the addressees are the Commission and a third country, and no firm can invoke it, but it decides whether electricity from that country is charged at all.")),

    ("ELEC-08", ACT,
     "‘A third country or territory that fulfils all the conditions set out in paragraph 7, shall be listed in point 2 of Annex III.",
     "the Commission shall take into account advancements in accordance with the timeline laid down in a Memorandum of Understanding under Article 2(7a).",
     dict(measure_type="obligation", direction="add",
          duty="Assess third-country listing for the electricity exemption against the Memorandum of Understanding timeline as well as the paragraph 7 conditions.",
          addressee="European Commission",
          cls=S, trigger="assessment of whether a third country or territory fulfils the Art. 2(7) conditions",
          frequency="if it happens", verification="none",
          article="Art. 1(1)(d), replacing Art. 2(8) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          note="Companion of ELEC-07: the MoU it creates becomes a criterion the Commission must weigh when listing a country for the exemption.")),

    # ------------------------------------------------------ data disclosure
    ("DATA-01", ACT,
     "‘An operator may disclose the information on the conditions for the use of actual emissions, for the relevant combinations of goods and origins pursuant to Article 6(7), the verification of embedded emissions and the carbon price paid in a third country referred to in paragraph 5 of this Article to an authorised CBAM declarant or to another operator.",
     "",
     dict(measure_type="right", direction="add",
          benefit="An operator may pass verified emissions and carbon-price information not only to an authorised CBAM declarant but to another operator, so verified data can move along the supply chain.",
          addressee="Operators of installations in third countries registered in the CBAM registry",
          cls=B, trigger="operator holds verified emissions or carbon-price information registered under Art. 10(5)",
          frequency="if it happens", verification="none",
          article="Art. 1(8)(c), replacing the first sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=J2028,
          value_drivers=["V3"], frictions=["F1"],
          named=["steel", "alu", "cement", "chem"], reached=[],
          right_basis={"text": "An operator may disclose the information on the conditions for the use of actual emissions, for the relevant combinations of goods and origins pursuant to Article 6(7), the verification of embedded emissions and the carbon price paid in a third country referred to in paragraph 5 of this Article to an authorised CBAM declarant or to another operator.",
                       "kind": "scope"},
          note="Named in the explanatory memorandum as 'clarifying that operators may share verified emissions data with other operators'. The operative verb confers a faculty and the addition is the words 'or to another operator' -- an operator-to-operator channel that did not exist. Object rule alone would have filed it as a duty being eased; nothing is eased, something new is permitted.")),

    ("DATA-02", ACT,
     "‘The operator may disclose to the authorised CBAM declarant only a summary of the information contained in paragraph 5, points (a), (b), (c) and (e).",
     "The authorised CBAM declarant shall be entitled to use that disclosed information in order to fulfil the obligation referred to in Article 8.",
     dict(measure_type="right", direction="add",
          benefit="An operator may limit what it hands the declarant to a summary of the registered information, and the declarant is entitled to rely on that summary to discharge its Article 8 verification obligation.",
          addressee="Operators of third-country installations and the authorised CBAM declarants they supply",
          cls=B, trigger="operator discloses registered information to an authorised CBAM declarant",
          frequency="annual", verification="none",
          article="Art. 1(8)(d), replacing the second sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=EIF,
          value_drivers=["V3"], frictions=["F1"],
          named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-10-7-summary",
          right_basis={"text": "The authorised CBAM declarant shall be entitled to use that disclosed information in order to fulfil the obligation referred to in Article 8.",
                       "kind": "conferral"},
          note="Two conferrals in one sentence pair: the operator may withhold detail behind a summary, and the declarant is expressly entitled to rely on it. Protects the operator's commercially sensitive emissions data without leaving the declarant unable to file.")),

    ("DATA-03", ACT,
     "Where the authorised CBAM declarant chooses to submit the CBAM declaration on the basis of this disclosed information, the authorised CBAM declarant shall remain responsible for surrendering the correct number of CBAM certificates pursuant to Article 22(1).",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Remain responsible for surrendering the correct number of CBAM certificates even where the declaration was built on information disclosed by the operator.",
          addressee="Authorised CBAM declarants relying on operator-disclosed information",
          cls=B, trigger="declarant submits a CBAM declaration on the basis of information disclosed by an operator",
          frequency="annual", verification="competent authority",
          article="Art. 1(8)(d), replacing the second sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-10-7-summary",
          note="The counterweight to DATA-02. Relying on a summary you cannot audit does not transfer the liability: the risk of the operator's data being wrong stays with the declarant.")),

    ("DATA-04", ACT,
     "‘(e) ensure, where applicable pursuant to Article 6(7), that the conditions laid down for the use of actual emissions, for relevant combinations of goods and origins, are met.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure that the conditions laid down for using actual emissions are met for the relevant combinations of goods and origins.",
          addressee="Operators of installations registered in the CBAM registry",
          cls=B, trigger="registered operator supplies actual emissions for a goods/origin combination covered by Art. 6(7)",
          frequency="annual", verification="accredited third party",
          article="Art. 1(8)(b), adding point (e) to Art. 10(5) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D2"], named=["steel", "alu", "cement", "chem"], reached=[])),

    ("DATA-05", ACT,
     "‘1. To allow the verification of embedded emissions on the basis of actual emissions as well as the determination, where applicable, of the carbon price paid in a third country, the Commission shall, upon request by an operator of an installation located in a third country, register the information",
     "on that operator and on its installation in the CBAM registry referred to in Article 14.",
     dict(measure_type="right", direction="add",
          benefit="A third-country operator may have its installation registered in the CBAM registry not only to support actual-emissions verification but to establish the carbon price it has paid at home.",
          addressee="Operators of installations located in third countries",
          cls=B, trigger="request by an operator of an installation located in a third country",
          frequency="one-off", verification="none",
          article="Art. 1(8)(a), replacing Art. 10(1) of Regulation (EU) 2023/956",
          when=J2028,
          value_drivers=["V3"], frictions=["F1"],
          named=["steel", "alu", "cement", "chem"], reached=[],
          right_basis={"text": "the Commission shall, upon request by an operator of an installation located in a third country, register the information",
                       "kind": "scope"},
          note="Registration on the operator's own request was already a faculty; what this adds is its extension to establishing the third-country carbon price, which is the gateway to the Art. 9 deduction. The extent of a conferred faculty widens, so right_basis kind is scope.")),

    # ------------------------------------------------------------ customs
    ("CUST-01", ACT,
     "‘2. The customs authorities shall periodically and automatically, in particular by means of the surveillance mechanism established pursuant to Article 56(5) of Regulation (EU) No 952/2013, communicate to the Commission specific information on the goods declared for importation.",
     "the customs authorities shall also communicate the name, address and, where available, contact information of the importer to the Commission.",
     dict(measure_type="obligation", direction="add",
          duty="Communicate import data to the Commission automatically, now including bills of discharge, re-export declarations and equivalent customs documentation, and the importer's identity where there is no EORI number.",
          addressee="Customs authorities of the Member States",
          cls=S, trigger="goods listed in Annex I, or processed products obtained from them, are declared for importation",
          frequency="continuous", verification="none",
          article="Art. 1(15)(a), replacing Art. 25(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4", "D5"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="The surveillance feed that makes the anti-circumvention provisions enforceable: bills of discharge and re-export declarations are exactly the documents that reveal inward-processing and transhipment routes.")),

    ("CUST-02", ACT,
     "The CBAM account number provided in the customs declaration or any other relevant document when declaring goods listed in Annex I or processed products obtained from such goods for importation, shall determine the authorised CBAM declarant assuming the obligations set out in this Regulation.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Accept that the CBAM account number entered in the customs declaration fixes which authorised CBAM declarant assumes the obligations for that consignment.",
          addressee="Authorised CBAM declarants and importers",
          cls=B, trigger="CBAM account number is provided in a customs declaration for Annex I goods or processed products",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(15)(a), replacing Art. 25(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Settles who is on the hook. An account number keyed into a customs field now allocates statutory liability, which makes control of that number a compliance risk in its own right.")),

    ("CUST-03", ACT,
     "‘Where the competent authority considers that the information is incorrect or inaccurate, the competent authority may request the customs authorities or the Commission to verify the correctness or the accuracy of that information.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Verify, on a competent authority's request, the correctness or accuracy of communicated customs information.",
          addressee="Customs authorities and the Commission",
          cls=S, trigger="competent authority considers communicated information incorrect or inaccurate",
          frequency="if it happens", verification="none",
          article="Art. 1(15)(b), adding a subparagraph to Art. 25(3) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=[], reached=[])),

    ("CUST-04", ACT,
     "‘7. The Commission is empowered to adopt implementing acts to identify the material and chemical compositions of goods listed in Annex I.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Apply the material and chemical compositions that the Commission fixes by implementing act for Annex I goods.",
          addressee="Importers and authorised CBAM declarants of Annex I goods",
          cls=B, trigger="Commission adopts implementing acts identifying material and chemical compositions",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(15)(d), adding Art. 25(7) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4"], named=["steel", "alu"], reached=["auto", "build"],
          pending="The compositions themselves sit in implementing acts that have not been adopted.",
          note="Load-bearing for the downstream extension: a 'combined metal product' only has a determinable steel or aluminium content once composition rules exist, and the mark-up and precursor mass both depend on it.")),

    # --------------------------------------------------------- verification
    ("VER-01", ACT,
     "‘Those delegated acts shall also specify the verification procedures to be used by verifiers.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Follow the verification procedures the Commission specifies by delegated act.",
          addressee="Accredited verifiers of embedded emissions",
          cls=B, trigger="verification of embedded emissions under Art. 8",
          frequency="annual", verification="accredited third party",
          article="Art. 1(10), adding a sentence to Art. 18(3) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D2"], named=[], reached=[],
          pending="The procedures are left to delegated acts that have not been adopted.")),

    # ------------------------------------------------------- governance
    ("GOV-01", ACT,
     "‘For its 2027 assessment due by 30 April 2027, the Commission shall use the import data of goods contained in Annex I to this Regulation and in Annex I to Regulation (EU) XX/XX [Amending Regulation]",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Base the 2027 assessment due by 30 April 2027 on import data for the goods in both the existing and the newly extended Annex I.",
          addressee="European Commission",
          cls=S, trigger="the 2027 assessment due by 30 April 2027",
          frequency="one-off", verification="none",
          article="Art. 1(2), adding a subparagraph to Art. 2a(3) of Regulation (EU) 2023/956",
          when="by 30 April 2027",
          drivers=["D5"], named=["steel", "alu"], reached=[],
          note="Makes the 2027 assessment cover the downstream goods before they become chargeable in 2028.")),

    ("GOV-02", ACT,
     "‘Before 1 January 2028, as well as every two years thereafter, the Commission shall present a report to the European Parliament and to the Council on the application of this Regulation and functioning of the CBAM.",
     "(d) aggregated information on the emission intensity for each country of origin for the different goods listed in Annex I.;",
     dict(measure_type="obligation", direction="add",
          duty="Report to Parliament and Council before 1 January 2028 and biennially thereafter on CBAM's operation, covering carbon leakage, internal-market and price effects, governance, circumvention practices, penalties and per-country emission intensity.",
          addressee="European Commission",
          cls=S, trigger="the biennial CBAM review cycle",
          frequency="biennial", verification="none",
          article="Art. 1(20), replacing the second subparagraph of Art. 30(6) of Regulation (EU) 2023/956",
          when="before 1 January 2028, then every two years",
          drivers=["D1", "D5"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          note="The review clause that governs future scope extensions -- it is the instrument under which cement, fertiliser and hydrogen downstream goods would be brought in.")),

    ("GOV-03", ACT,
     "‘(ka) material composition of each downstream good;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="State the material composition of each downstream good in the verification report.",
          addressee="Accredited verifiers preparing CBAM verification reports",
          cls=B, trigger="preparation of a verification report covering a downstream good",
          frequency="annual", verification="accredited third party",
          article="Art. 1(23)(b), inserting point (ka) in point 2 of Annex VI of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D1", "D4"], named=["steel", "alu"], reached=["auto", "build"],
          provision_id="cbam-annex-vi-2",
          note="The reporting counterpart of CUST-04: composition has to be declared per good, not merely defined in the abstract.")),

    ("GOV-04", ACT,
     "(a)points (g) to (j) are deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Set out in the verification report the quantities of each type of goods produced, the quantification of the installation's direct emissions, how those emissions are attributed across goods, and the energy and emissions flows not associated with those goods.",
          addressee="Accredited verifiers preparing CBAM verification reports",
          cls=B, trigger="preparation of a verification report under Article 8",
          frequency="annual", verification="accredited third party",
          article="Art. 1(23)(a), deleting points (g) to (j) of point 2 of Annex VI of Regulation (EU) 2023/956",
          when=J2028,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-annex-vi-2",
          prior=dict(
              start="quantities of each type of declared goods produced in the reporting period;",
              end="quantitative information on the goods, emissions and energy flows not associated with those goods;",
              trigger="verifier preparing a verification report establishing the embedded emissions of the goods",
              obligation="Points (g) to (j) of Annex VI point 2 required the verification report to state the quantities of each type of declared goods produced in the reporting period, the quantification of the installation's direct emissions, a description of how those emissions are attributed to different types of goods, and quantitative information on goods, emissions and energy flows not associated with those goods.",
              source_document=PRIOR_DOC + ", Annex VI, point 2, points (g) to (j)",
              note="Resolving the prior text corrected the addressee as well as substantiating the label. Annex VI point 2 is headed 'CONTENT OF A VERIFICATION REPORT', so these duties fall on the accredited verifier, not on the operator or the declarant as first extracted. Four required contents of that report are removed, so the row is a Simplification for the verifier."),
          note="The span this act supplies is only the amending instruction '(a)points (g) to (j) are deleted;'. The prior rule carries what was actually removed.")),

    ("GOV-05", ACT,
     "‘The Commission shall publish the price of CBAM certificates on its website or in any other appropriate manner on the first working day of the following calendar week.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish the CBAM certificate price on the first working day of the following calendar week.",
          addressee="European Commission",
          cls=S, trigger="close of each calendar week's certificate pricing",
          frequency="weekly", verification="none",
          article="Art. 1(12)(b), replacing the first sentence of Art. 21(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=[], reached=[],
          note="Companion of FIN-04: the fallback price rules are only usable if the resulting price is published on a predictable day.")),

    # =====================================================================
    # PROMOTED FROM PASS B
    #
    # Eight provisions the second read caught and the first did not. They keep
    # the CBAMB- prefix the ETSB-/IAAB- rows established for a Pass-B-origin
    # promotion, and `pass_origin` records the lineage machine-readably.
    #
    # A ninth candidate, B-24 (Art. 1(7)(b)(2), the free-standing Art. 9(5)
    # subparagraph on certifier qualifications), was REJECTED rather than
    # promoted. The proposal states that rule twice -- once inside the Art. 9(5)
    # first subparagraph, which is already quoted whole in FIN-06's sibling
    # FIN-08, and again as this subparagraph -- so promoting it would enter a
    # second register row for a rule the register already states once. That is
    # the call the ETS reconciliation made for 22 of its 27 blocked rows, and it
    # is the same call here. The duplication is a drafting slip in the proposal
    # and is recorded on FIN-08 instead.
    # =====================================================================

    ("CBAMB-SCP-07", ANNEX,
     "2601 12 00 – Agglomerated iron ores and concentrates, other than roasted iron pyrites",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Declare embedded emissions and surrender certificates for goods added to the existing 'Iron and steel' table -- agglomerated iron ore, stranded wire and cables, unplated welded grill and netting, springs, enamelled and other household articles, and other cast articles of iron or steel.",
          addressee="Importers and authorised CBAM declarants of the newly listed iron and steel goods",
          cls=B, trigger="importation of goods under the CN codes added to the Annex I 'Iron and steel' table",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (1) replacing the 'Iron and Steel' table in point 2 of Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4", "D2", "D6"],
          named=["steel"], reached=["auto", "build"],
          pass_origin="cbam_pass_b:B-48",
          note="The scope extension the first pass missed, because Annex I point (2) ADDS a table and point (1) REPLACES one, and only the added table was read. Diffed against the prior Annex I, the replacement adds 2601 12 00 (agglomerated iron ores and concentrates), 7312 10 (stranded wire, ropes and cables), 7314 39 00 (unplated welded grill, netting and fencing), 7320 20 89 and 7320 90 90 (springs), 7323 94 00 and 7323 99 00 (household articles) and 7325 (other cast articles). Agglomerated iron ore is the one that does not fit the downstream story at all: it is an upstream input entering CBAM scope, reaching the sintering and pelletising trade. D7 for the same reason SCP-04 carries it -- these importers were outside the regime.")),

    ("CBAMB-ELEC-09", ANNEX,
     "‘(e) ‘emission factor for electricity’ means the weighted average of the CO2 intensity of the electricity produced within a geographic area;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Use, as the emission factor for electricity, the weighted average CO2 intensity of all electricity produced in the geographic area, in place of a factor representing the emission intensity of the electricity consumed in producing the goods.",
          addressee="Importers and authorised CBAM declarants of electricity and of goods carrying embedded indirect emissions",
          cls=B, trigger="determination of default values for imported electricity or for embedded indirect emissions",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (1) replacing point (e) of point 1 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=["D4"], named=["power"], reached=["steel", "alu", "cement", "chem"],
          provision_id="cbam-annex-iv-1",
          pass_origin="cbam_pass_b:B-51",
          prior=dict(
              start="‘emission factor for electricity’ means the default value, expressed in CO2e, representing the emission intensity of electricity consumed in production of goods;",
              end="",
              trigger="determination of default values for imported electricity",
              obligation="The prior Annex IV point 1(e) defined the emission factor for electricity as 'the default value, expressed in CO2e, representing the emission intensity of electricity consumed in production of goods'.",
              source_document=PRIOR_DOC + ", Annex IV, point 1, point (e)",
              note="Two things move: the basis goes from electricity CONSUMED in production to electricity PRODUCED in a geographic area, and it becomes a weighted average of CO2 intensity."),
          note="Definitional and load-bearing. ELEC-01, ELEC-02 and ELEC-03 are each nothing but the substitution of THIS term for 'CO2 emission factor' in Annex IV points 4.2.1, 4.2.2 and 4.3 -- so without this row the register states the effect of those substitutions while not holding the definition that produces it. It also applies from 1 January 2026, before all three.")),

    ("CBAMB-ELEC-10", ANNEX,
     "(f) ‘power purchase agreement’ means a contract under which a person agrees to purchase electricity directly from an electricity producer and that involves the physical delivery of electricity;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Hold a power purchase agreement that involves the physical delivery of electricity, not merely a direct contractual purchase, in order to claim actual embedded emissions for imported electricity.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity under Annex IV point 5",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (1) replacing point (f) of point 1 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=["D4", "D1"], named=["power"], reached=[],
          provision_id="cbam-annex-iv-1",
          pass_origin="cbam_pass_b:B-52",
          prior=dict(
              start="‘power purchase agreement’ means a contract under which a person agrees to purchase electricity directly from an electricity producer;",
              end="",
              trigger="authorised CBAM declarant relying on a power purchase agreement to claim actual embedded emissions",
              obligation="The prior Annex IV point 1(f) defined a power purchase agreement as 'a contract under which a person agrees to purchase electricity directly from an electricity producer', with no delivery requirement.",
              source_document=PRIOR_DOC + ", Annex IV, point 1, point (f)",
              note="The added words are 'and that involves the physical delivery of electricity'. A financial or virtual PPA satisfied the prior definition and does not satisfy this one."),
          note="Cuts against ELEC-04 in the same Annex II point. ELEC-04 relaxes the PPA condition to admit intermediaries; this tightens the same instrument to require physical delivery through them. Registering the relief without the restriction overstated ELEC-04, which now carries a cross-reference.")),

    ("CBAMB-SCP-08", ACT,
     "‘11. The Commission is empowered to adopt delegated acts in accordance with Article 28 in order to amend the lists of third countries",
     "the procedure provided for in Article 28a shall apply to delegated acts adopted pursuant to this paragraph.",
     dict(measure_type="obligation", direction="add",
          duty="A third country or territory may be added to or removed from the Annex III exemption lists by delegated act, including as a consequence of CBAM incorporation into the EEA Agreement, and under urgency where imperative grounds require it.",
          addressee="European Commission; importers of goods originating in third countries listed in Annex III",
          cls=S, trigger="conditions in Art. 2(6), (7) or (9) are or cease to be fulfilled for a third country, or the CBAM is incorporated into the EEA Agreement",
          frequency="if it happens", verification="none",
          article="Art. 1(1)(e), replacing Art. 2(11) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power", "steel", "alu", "cement", "chem"], reached=[],
          pass_origin="cbam_pass_b:B-06",
          note="Annex III listing is what switches the CBAM off for a country's goods, so the power to amend the list is a scope power and not the institutional plumbing it resembles. Two things are new against the prior Art. 2(11): the EEA-incorporation ground, and the Art. 28a urgency procedure, which lets a country be ADDED to the exemption list with immediate effect. Registered on the same footing as ELEC-08, which already carries the Art. 2(8) listing assessment.")),

    ("CBAMB-VER-02", ACT,
     "The Union may conclude agreements with third countries or territories with a view to taking into account carbon pricing mechanisms",
     "the mutual recognition of third-country accreditation bodies for the accreditation of a legal person to be a verifier pursuant to Article 18.",
     dict(measure_type="obligation", direction="rem",
          duty="Use a verifier accredited by a Member State national accreditation body, there being no route to recognition of a third-country accreditation body.",
          addressee="Authorised CBAM declarants and third-country operators procuring verification",
          cls=S, trigger="Union concludes an agreement with a third country covering mutual recognition of accreditation bodies",
          frequency="if it happens", verification="accredited third party",
          article="Art. 1(1)(e), replacing Art. 2(12) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          pass_origin="cbam_pass_b:B-07",
          pending="No such agreement exists. The provision is an enabling power, and until one is concluded nothing changes for a declarant.",
          prior=dict(
              start="The Union may conclude agreements with third countries or territories with a view to taking into account carbon pricing mechanisms in such countries or territories for the purposes of the application of Article 9.",
              end="",
              trigger="Union concluding an agreement with a third country on carbon pricing",
              obligation="The prior Art. 2(12) allowed agreements 'with a view to taking into account carbon pricing mechanisms in such countries or territories for the purposes of the application of Article 9', and stopped there.",
              source_document=PRIOR_DOC + ", Article 2(12)",
              note="The mutual-recognition limb is entirely new. The object it acts on is the verification condition, which is why this is filed as a verifier row and not an Art. 9 carbon-price row."),
          note="The verification bottleneck for third-country operators: today an installation in a third country needs a verifier accredited in the Union. This opens the route to recognising its own country's accreditation body.")),

    ("CBAMB-DECL-07", ACT,
     "‘The Commission is empowered to adopt implementing acts concerning the standard format of the CBAM declaration",
     "in particular as regards the process and the selection by the authorised CBAM declarant of certificates to be surrendered.",
     dict(measure_type="obligation", direction="add",
          duty="Report, in the standard declaration format, the detail supporting each total -- per installation and per country of origin -- including the carbon price paid and the default carbon price for the purposes of Art. 9(4).",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="submission of the CBAM declaration in the standard format",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(b), replacing the first sentence of Art. 6(6) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          pass_origin="cbam_pass_b:B-14",
          pending="The format is itself the implementing act; the reporting granularity binds once it is adopted.",
          note="Not the bare empowerment it looks like. The format must now carry information 'for each installation and country of origin or other third country and type of goods', the carbon price paid, and the Art. 9(4) default carbon price -- a per-installation granularity the prior sentence did not demand, and the reporting counterpart of DECL-03's per-tonne totals.")),

    ("CBAMB-ANTI-05", ACT,
     "‘6a. The Commission is empowered to adopt implementing acts concerning the identification of goods or combination of goods and origins",
     "in accordance with the examination procedure referred to in Article 29(2).",
     dict(measure_type="obligation", direction="add",
          duty="Designate, by implementing act, the goods or goods/origin combinations for which traceability evidence must accompany the declaration, and the type of evidence required.",
          addressee="European Commission",
          cls=S, trigger="identification of a supply-chain traceability risk",
          frequency="if it happens", verification="none",
          article="Art. 1(5)(c), adding Art. 6(6a) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          pass_origin="cbam_pass_b:B-15",
          note="Registered for the same reason ANTI-03 and ANTI-04 both are: it is the instrument that decides the reach of an operative duty. DECL-01 binds nobody until this implementing act names the goods and the evidence, and it was previously visible only as DECL-01's `pending` note.")),

    ("CBAMB-CUST-05", ACT,
     "‘The Commission is empowered to adopt implementing acts defining the scope of information and the periodicity, timing and means for communicating that information pursuant to paragraphs 2 and 3 of this Article.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Communicate customs information at the scope, periodicity, timing and by the means the implementing acts prescribe, for the competent-authority flow under Art. 25(3) as well as the customs flow under Art. 25(2).",
          addressee="Member State customs authorities and competent authorities",
          cls=S, trigger="adoption of the Art. 25(6) implementing acts",
          frequency="continuous", verification="none",
          article="Art. 1(15)(c), replacing the first sentence of Art. 25(6) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4"], named=["steel", "alu", "cement", "chem"], reached=[],
          pass_origin="cbam_pass_b:B-41",
          prior=dict(
              start="The Commission is empowered to adopt implementing acts defining the scope of information and the periodicity, timing and means for communicating that information pursuant to paragraph 2 of this Article.",
              end="",
              trigger="Commission setting the format of customs information flows",
              obligation="The prior Art. 25(6) empowered implementing acts on the scope, periodicity, timing and means of communication 'pursuant to paragraph 2 of this Article' only.",
              source_document=PRIOR_DOC + ", Article 25(6), first sentence",
              note="The single-word change is 'paragraph 2' to 'paragraphs 2 and 3', which brings the Art. 25(3) competent-authority flow under implementing-act control for the first time."),
          note="The thinnest of the eight, and promoted rather than rejected because the flow it newly governs is a duty the register already carries: CUST-03 is the Art. 25(3) verification request. Leaving Art. 25(6) out would have left three of the four Art. 25 amendments registered.")),
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
    sources = {}
    for name in (ACT, ANNEX, PRIOR):
        raw = (HERE / name).read_text(encoding="utf-8")
        if name == ACT:
            # Confine matching to the operative part. The explanatory memorandum
            # restates these provisions in near-identical words, and an anchor
            # that landed there would quote a summary as if it were the law.
            cut = raw.find(OPERATIVE_ANCHOR)
            if cut == -1:
                raise LookupError(f"operative anchor missing from {name}")
            raw = raw[cut:]
        sources[name] = raw

    rows, errors = [], []
    for rid, src, start, end, meta in ROWS:
        try:
            span = slice_span(sources[src], start, end, rid)
        except LookupError as exc:
            errors.append(str(exc))
            continue

        row = {
            "id": rid,
            "measure_type": meta["measure_type"],
        }
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
            "file": "cbam",
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
        # A row whose classification was CHANGED keeps the record of what it was
        # and why, the way ETS FRE-04 and IAA PRM-04 do. Without it a corrected
        # row is indistinguishable from one that was always right, and the
        # reconciliation that produced the correction becomes unauditable.
        if meta.get("reclass_from"):
            row["reclass_from"] = meta["reclass_from"]
        # A row the SECOND pass found and the first did not. The value is the
        # pass id it came from, matching the ETSB-/IAAB- convention.
        if meta.get("pass_origin"):
            row["pass_origin"] = meta["pass_origin"]

        # A deletion amendment has no legible before-state in its own span, so
        # the text it removes is sliced out of the amended act and attached as
        # prior_rule. Enforced by benefit_axis.deletion_prior_ok.
        if meta.get("prior"):
            p = meta["prior"]
            try:
                pspan = slice_span(sources[PRIOR], p["start"], p.get("end", ""), rid + " (prior)")
            except LookupError as exc:
                errors.append(str(exc))
                continue
            row["prior_rule"] = {
                "trigger": p["trigger"],
                "obligation": p["obligation"],
                "source_text": pspan,
                "status": "sourced",
                "source_document": p["source_document"],
                "note": p["note"],
            }
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

    from collections import Counter
    print(f"cbam: {len(rows)} rows")
    print(f"  measure_type: {dict(Counter(r['measure_type'] for r in rows))}")
    print(f"  class:        {dict(Counter(r['class'] for r in rows))}")
    print(f"  direction:    {dict(Counter(r['direction'] for r in rows))}")

    if write:
        (DATA / "cbam.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print("written ../data/cbam.json")
    else:
        print("check only, nothing written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

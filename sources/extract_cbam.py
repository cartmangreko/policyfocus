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

The one thing this file cannot claim is a second read. ETS and IAA each have two
independent extraction passes that reconcile.py compares; CBAM has one. So the
disagreement signal that backs those two files does not exist here, and
reconcile cannot be run for cbam until a second pass is written. Said plainly
because a register file that looks like the others should not be assumed to
carry the same evidence behind it.
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

# Where the operative part starts, so an anchor cannot accidentally match the
# explanatory memorandum, which paraphrases the same provisions in similar
# words. Article 1 begins at the "Amendments to Regulation (EU) 2023/956"
# heading; everything before it is recitals and memorandum.
OPERATIVE_ANCHOR = "Amendments to Regulation (EU) 2023/956"

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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="from entry into force",
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
          when="applies from 1 January 2028 per Art. 2 for Art. 1(6)(a); the Art. 6(2) points apply on entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2026 per Art. 2 (Annex II point 1) and otherwise on entry into force",
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
          when="from entry into force",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
          drivers=[], named=[], reached=[],
          note="Checked against the prior rule (32023R0956 as consolidated) before classifying, because the new sentence reads like a fresh routing rule and is not one: repurchase already ran through the common central platform. What the amendment removes is the Commission's express role as the actor doing it on the Member State's behalf, leaving the sentence in the passive. So the duty that moves is the Commission's, not a declarant's, and this is a state-class row. Nothing changes for a firm -- flagged in the report as the one row here whose company-facing content is nil.")),

    ("FIN-06", ACT,
     "‘The information contained in that documentation shall be certified by a person that is independent from the authorities of the third country.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Have the documentation evidencing a carbon price paid in a third country certified by a person independent of that country's authorities.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="claim for a reduction of certificates on account of a carbon price paid in a third country",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(1), replacing the third sentence of Art. 9(2) of Regulation (EU) 2023/956",
          when="from entry into force",
          drivers=["D1", "D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-9-2",
          note="Tightens the evidence for the carbon-price deduction: certification must now come from outside the exporting state's own administration.")),

    ("FIN-07", ACT,
     "‘The independent person referred to in the first subparagraph may be a legal person accredited by a national accreditation body for the relevant scope of accreditation.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Find a certifying person meeting the independence test without the benefit of an express route through national accreditation.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="declarant seeks a certifier for third-country carbon price documentation",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(2), adding a subparagraph to Art. 9(2) of Regulation (EU) 2023/956",
          when="from entry into force",
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
          when="from entry into force",
          drivers=["D1", "D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The conversion methodology, the evidence standard and the treatment of Paris Agreement Art. 6 credits all sit in implementing acts that have not been adopted.",
          note="The mechanism that decides how much a carbon price paid abroad is actually worth against the CBAM liability, and the first time Paris Agreement Art. 6 credits are brought into that calculation. Economically the most consequential of the Art. 9 changes, which is why it is carried separately from the FIN-06/FIN-07 certification pair.")),

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
          when="from entry into force",
          drivers=[], named=["power"], reached=[],
          note="Rebases the electricity default on the exporting country's actual emission factor rather than on fossil generation alone, so a clean exporter is no longer charged as if it burned coal. The object is the basis on which the liability is computed -- a duty's quantum, not a support. Object rule -> obligation side, direction rem.")),

    ("ELEC-02", ANNEX,
     "Where it can be demonstrated, on the basis of reliable data, that the emission factor for electricity in a third country, a group of third countries or a region within a third country is lower than the specific default value determined by the Commission or lower than the emission factor for electricity in the Union",
     "an alternative default value based on that emission factor for electricity may be used for that third country, group of third countries or region within a third country.",
     dict(measure_type="right", direction="add",
          benefit="Where reliable data show the exporting country's electricity emission factor is lower than the applicable default, an alternative default value based on that lower factor may be used.",
          addressee="Importers and authorised CBAM declarants of electricity from lower-carbon third countries",
          cls=B, trigger="reliable data demonstrate an electricity emission factor lower than the specific default value or the Union factor",
          frequency="annual", verification="competent authority",
          article="Art. 1(22); Annex II, point (4) replacing point 4.2.2 of Annex IV of Regulation (EU) 2023/956",
          when="from entry into force",
          value_drivers=["V3"], frictions=["F1", "F4"],
          named=["power"], reached=[],
          right_basis={"text": "an alternative default value based on that emission factor for electricity may be used for that third country, group of third countries or region within a third country",
                       "kind": "conferral"},
          named_note="", note="The operative verb confers: 'may be used' hands the declarant an option it did not hold, on evidence it chooses to bring. Not a Simplification -- no duty narrows on its own, the declarant must demonstrate the lower factor to get it. Same test as ETS FRE-06 ('may request to form a pool').")),

    ("ELEC-03", ANNEX,
     "‘Where a third country, or a group of third countries, demonstrates to the Commission, on the basis of reliable data, that the average electricity mix emission factor or CO2 emission factor of price-setting sources",
     "an alternative default value based on that average electricity mix emission factor or on that average CO2 emission factor shall be established for this country or group of countries.",
     dict(measure_type="obligation", direction="rem",
          duty="Accept the standard default value for indirect emissions where the exporting country's actual electricity mix is cleaner than that default.",
          addressee="Importers of goods with indirect emissions from lower-carbon third countries",
          cls=B, trigger="third country demonstrates to the Commission an average electricity mix or CO2 emission factor lower than the default for indirect emissions",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (5) replacing the second paragraph of point 4.3 of Annex IV of Regulation (EU) 2023/956",
          when="from entry into force",
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
          when="from entry into force",
          drivers=[], named=["power"], reached=[],
          note="Admits intermediated PPAs provided the contractual chain is verifiable, which is what makes the actual-emissions route usable in practice. A condition on a duty is relaxed. Object rule -> obligation side, direction rem.")),

    ("ELEC-05", ANNEX,
     "(b)\n\xa0\xa0\xa0point (b) is deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Satisfy the deleted point (b) condition of Annex IV point 5 in order to claim actual emissions for imported electricity.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (6)(b) deleting point (b) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when="from entry into force",
          drivers=[], named=["power"], reached=[],
          note="A bare deletion. The span is the amending instruction itself, because that is all the proposal contains -- the deleted condition lives in the consolidated CBAM Regulation (32023R0956), not in this act. Flagged in the report: the substance requires reading the prior rule.")),

    ("ELEC-06", ANNEX,
     "‘(d) the amount of electricity for which the use of actual embedded emissions is claimed has been firmly nominated to the allocated interconnection capacity",
     "This criterion shall not be fulfilled in cases where transmission capacity for the import of electricity is allocated through implicit capacity allocation;",
     dict(measure_type="obligation", direction="add",
          duty="Firmly nominate the claimed electricity to allocated interconnection capacity across origin, destination and transit, matching production within the same hour, and forgo the claim where capacity is allocated implicitly.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(c) replacing point (d) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="applies from 1 January 2028 per Art. 2",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          when="from entry into force",
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
          duty="Report the material composition of each downstream good in the information supplied for the CBAM declaration.",
          addressee="Operators and authorised CBAM declarants of downstream goods",
          cls=B, trigger="reporting of information under Annex VI point 2 for a downstream good",
          frequency="annual", verification="accredited third party",
          article="Art. 1(23)(b), inserting point (ka) in point 2 of Annex VI of Regulation (EU) 2023/956",
          when="applies from 1 January 2028 per Art. 2",
          drivers=["D1", "D4"], named=["steel", "alu"], reached=["auto", "build"],
          provision_id="cbam-annex-vi-2",
          note="The reporting counterpart of CUST-04: composition has to be declared per good, not merely defined in the abstract.")),

    ("GOV-04", ACT,
     "(a)points (g) to (j) are deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Report the information required by points (g) to (j) of point 2 of Annex VI.",
          addressee="Operators and authorised CBAM declarants",
          cls=B, trigger="reporting of information under Annex VI point 2",
          frequency="annual", verification="none",
          article="Art. 1(23)(a), deleting points (g) to (j) of point 2 of Annex VI of Regulation (EU) 2023/956",
          when="applies from 1 January 2028 per Art. 2",
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-annex-vi-2",
          note="A bare deletion: four reporting fields go. As with ELEC-05 the span is the amending instruction, because the deleted content is in the consolidated CBAM Regulation and not in this act. Flagged in the report.")),

    ("GOV-05", ACT,
     "‘The Commission shall publish the price of CBAM certificates on its website or in any other appropriate manner on the first working day of the following calendar week.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish the CBAM certificate price on the first working day of the following calendar week.",
          addressee="European Commission",
          cls=S, trigger="close of each calendar week's certificate pricing",
          frequency="weekly", verification="none",
          article="Art. 1(12)(b), replacing the first sentence of Art. 21(2) of Regulation (EU) 2023/956",
          when="from entry into force",
          drivers=["D5"], named=[], reached=[],
          note="Companion of FIN-04: the fallback price rules are only usable if the resulting price is published on a predictable day.")),
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
    for name in (ACT, ANNEX):
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

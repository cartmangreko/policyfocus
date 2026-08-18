"""
CBAM extension proposal (COM(2025) 989, CELEX 52025PC0989): SECOND independent
extraction pass. Writes sources/cbam_pass_b.json.

    python3 extract_cbam_pass_b.py --check    # report, write nothing
    python3 extract_cbam_pass_b.py            # write cbam_pass_b.json

WHY THIS EXISTS
===============
extract_cbam.py said the one thing this file could not claim was a second read:
ETS and IAA each have two passes that reconcile.py compares, and CBAM had one.
This is that second read, so `reconcile.py ../data/cbam.json cbam_pass_b.json
cbam` can now be run and the register's fourth file carries the same
disagreement signal as the other three.

WHAT "INDEPENDENT" MEANS HERE, AND WHAT IT DOES NOT
===================================================
The reading is independent: this pass was written by walking Article 1 point by
point through cbam_ext.txt and cbam_ext_annexes.txt and enumerating every
amending instruction, then classifying each one from the amended text and, where
the instruction only says what moves, from the prior consolidation. It was NOT
written by editing Pass A, and its ids are its own.

It is not independent in the strong sense the ETS and IAA pairs are, where the
two passes were taken before either could see the other. Some Pass A rows were
visible while this was written. That weakens the agreement signal -- where the
two passes agree, the agreement is worth less than it looks -- and it does not
weaken the disagreement signal, which is what a second pass is actually for.
Recorded here rather than left for a reader to discover.

IDS AND THE CROSSWALK
=====================
Ids are B-01..B-62 in the order the provisions appear in the act. They
deliberately do not reuse Pass A's family prefixes: matching two passes on id
coincidence is what reanchor_passes.PASS_B_CROSSWALK exists to prevent. The
crosswalk entry for cbam_pass_b.json states which register row rules on the same
provision, and rows with no entry there are the ones this pass found and the
register does not carry.

THE SPAN DISCIPLINE
===================
Same as extract_cbam.py: every source_text is SLICED from the fetched source by
a start/end anchor, never retyped, and a missing or ambiguous anchor is a hard
failure that writes nothing. Anchors into the act are matched only from the
operative part, because the explanatory memorandum restates the same provisions
in near-identical words.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

ACT = "cbam_ext.txt"
ANNEX = "cbam_ext_annexes.txt"

PRIOR = "cbam_ext_prior_02023R0956-20251020.txt"
PRIOR_DOC = ("Regulation (EU) 2023/956 as consolidated at 2025-10-20, "
             "CELEX 02023R0956-20251020")

OPERATIVE_ANCHOR = "Amendments to Regulation (EU) 2023/956"

B = "business"
S = "state"

# Article 2 of the proposal sets three application dates, and every `when` below
# is read off it rather than defaulted:
#   entry into force  -- third day after publication (the residual case)
#   1 January 2026    -- points 1 and 6 of Annex II
#   1 January 2028    -- Art. 1(6)(a), Art. 1(8)(a)(b)(c), Art. 1(21), (23),
#                        (24), and point 2 of Annex II
EIF = "from entry into force (third day after publication), Art. 2"
J2026 = "applies from 1 January 2026 per Art. 2 (points 1 and 6 of Annex II)"
J2028 = "applies from 1 January 2028 per Art. 2"

# (id, source-file, start anchor, end anchor, metadata)
# end anchor "" means: take the start anchor alone as the span.
ROWS: list[tuple] = [

    # ------------------------------------------------------------ Article 2
    ("B-01", ACT,
     "‘2a. Upon its incorporation in the EEA Agreement, this Regulation also applies to processed products",
     "provided that they are imported to those countries.",
     dict(measure_type="obligation", direction="add",
          duty="Account for CBAM on processed products made from Annex I goods under inward processing that are re-exported to Norway or Iceland.",
          addressee="Importers and authorised CBAM declarants of processed products re-exported to Norway or Iceland",
          cls=B, trigger="processed products from Annex I goods under inward processing are re-exported to and imported in Norway or Iceland",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(a), inserting Art. 2(2a) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation in the EEA Agreement",
          drivers=["D7", "D1"], named=["steel", "alu"], reached=[],
          pending="The detailed conditions are left to implementing acts under the new Art. 2(2a); nothing is operable until they exist.")),

    ("B-02", ACT,
     "‘Upon its incorporation into the EEA Agreement, by way of derogation from paragraphs 1 and 2, this Regulation shall not apply",
     "within the customs territory of the respective EFTA States.",
     dict(measure_type="obligation", direction="rem",
          duty="Comply with CBAM for third-country goods that were already released for free circulation in an EFTA State that has incorporated the CBAM.",
          addressee="Customs declarants importing goods previously released for free circulation in a CBAM-integrated EFTA State",
          cls=B, trigger="goods previously released for free circulation in the customs territory of an EFTA State that incorporated the CBAM",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(b), adding a subparagraph to Art. 2(4) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation into the EEA Agreement",
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-2-4",
          note="A duty switched off inside an integrated CBAM area, so no consignment is charged twice. No support moves: obligation side, direction rem. B-03 is the evidence condition attached to it.")),

    ("B-03", ACT,
     "The customs declarant shall bear responsibility for the availability of this proof at the time of lodging of the customs declaration.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Have the documentation proving prior release for free circulation in an EFTA State available at the moment the customs declaration is lodged.",
          addressee="Customs declarants relying on the EFTA prior-free-circulation exemption",
          cls=B, trigger="declarant claims the Art. 2(4) EFTA exemption in a customs declaration",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(1)(b), adding a subparagraph to Art. 2(4) of Regulation (EU) 2023/956",
          when="upon incorporation of the Regulation into the EEA Agreement",
          drivers=["D1", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-2-4")),

    ("B-04", ACT,
     "‘Where a third country has requested to integrate its electricity market into that of the Union through market coupling",
     "insofar as electricity generation is concerned.",
     dict(measure_type="obligation", direction="add",
          duty="Conclude and then honour a Memorandum of Understanding fixing the timeline for the Art. 2(7) electricity exemption and for an EU ETS-equivalent carbon price on generation.",
          addressee="Third countries seeking electricity market coupling with the Union, and the Commission",
          cls=S, trigger="third country requests to integrate its electricity market with the Union's under an international agreement",
          frequency="if it happens", verification="none",
          article="Art. 1(1)(c), inserting Art. 2(7a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          note="The gateway to the Art. 2(7) exemption. State class: no firm can invoke it, but it decides whether electricity from that country is charged at all.")),

    ("B-05", ACT,
     "When assessing whether the conditions set out in paragraph 7 of this Article are fulfilled, the Commission shall take into account advancements in accordance with the timeline laid down in a Memorandum of Understanding under Article 2(7a).",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Take the Memorandum of Understanding timeline into account when assessing whether a third country qualifies for the Annex III point 2 exemption.",
          addressee="European Commission",
          cls=S, trigger="assessment of a third country against the Art. 2(7) conditions",
          frequency="if it happens", verification="none",
          article="Art. 1(1)(d), replacing Art. 2(8) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[])),


    ("B-06", ACT,
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
          note="NOT IN PASS A. Annex III listing is what switches the CBAM off for a country's goods, so the power to amend the list is a scope power, not a procedural one. Two things are new against the prior Art. 2(11): the EEA-incorporation ground, and the Art. 28a urgency procedure, which lets a country be ADDED to the exemption list with immediate effect.")),

    ("B-07", ACT,
     "The Union may conclude agreements with third countries or territories with a view to taking into account carbon pricing mechanisms",
     "the mutual recognition of third-country accreditation bodies for the accreditation of a legal person to be a verifier pursuant to Article 18.",
     dict(measure_type="obligation", direction="rem",
          duty="Use a verifier accredited by a national accreditation body of a Member State, there being no route to recognition of a third-country accreditation body.",
          addressee="Authorised CBAM declarants and third-country operators procuring verification",
          cls=S, trigger="Union concludes an agreement with a third country covering accreditation bodies",
          frequency="if it happens", verification="accredited third party",
          article="Art. 1(1)(e), replacing Art. 2(12) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="No such agreement exists; the provision is an enabling power, and until one is concluded nothing changes for a declarant.",
          note="NOT IN PASS A. The prior Art. 2(12) stopped at carbon pricing mechanisms 'for the purposes of the application of Article 9'. The mutual-recognition limb is new and its object is the verification condition, which is why it is filed rem rather than as an Art. 9 row.")),

    ("B-08", ACT,
     "‘For its 2027 assessment due by 30 April 2027, the Commission shall use the import data of goods contained in Annex I",
     "in Annex I to Regulation (EU) XX/XX [Amending Regulation]’;",
     dict(measure_type="obligation", direction="add",
          duty="Base the 2027 threshold assessment on import data for the goods in both the existing Annex I and the Annex I of this amending Regulation.",
          addressee="European Commission",
          cls=S, trigger="the Art. 2a(3) assessment falling due in 2027",
          frequency="one-off", verification="none",
          article="Art. 1(2), adding a subparagraph to Art. 2a(3) of Regulation (EU) 2023/956",
          when="by 30 April 2027",
          drivers=["D5"], named=[], reached=["steel", "alu", "auto", "build"],
          note="Reads the new downstream scope back into the mass-based de minimis threshold: the assessment that sets the threshold must count the newly covered goods.")),

    ("B-09", ACT,
     "‘(35) ‘abusive practices’ are practices pursued by an actor for the purpose of gaining a benefit by unduly avoiding",
     "undermining the effectiveness of the CBAM to address the risk of carbon leakage in the EU.’;",
     dict(measure_type="obligation", direction="add",
          duty="Avoid practices whose purpose is to gain a benefit by unduly avoiding, wholly or partly, the CBAM financial liability.",
          addressee="Importers, authorised CBAM declarants and third-country operators",
          cls=B, trigger="any conduct bearing on the CBAM financial liability",
          frequency="continuous", verification="competent authority",
          article="Art. 1(3), adding point (35) to Art. 3 of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="A definition, filed as a row because three operative duties hang off it -- Art. 6(2)(f) evidence, Art. 6(7) delegated acts and the Art. 27 circumvention regime -- and its breadth ('unduly avoiding') is what fixes their reach.")),

    ("B-10", ACT,
     "‘(h) EORI number or other national identification number, names and contact information of the persons on behalf of whom the applicant is acting, if applicable.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Identify by EORI or national identification number every person on whose behalf the applicant acts, in the authorisation application.",
          addressee="Applicants for authorised CBAM declarant status acting on behalf of others",
          cls=B, trigger="application for authorisation as a CBAM declarant on behalf of other persons",
          frequency="one-off", verification="competent authority",
          article="Art. 1(4), replacing point (h) of Art. 5(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1"], named=[], reached=["steel", "alu", "cement", "chem"],
          note="Anti-circumvention through the indirect-representation route: the prior point (h) named the represented persons, this adds their identification numbers so a chain of representatives can be traced.")),

    ("B-11", ACT,
     "‘(b) the total embedded emissions in the goods referred to in point (a) of this paragraph, expressed in tonnes of CO2e emissions per megawatt-hour of electricity",
     "verified in accordance with Article 8;’;",
     dict(measure_type="obligation", direction="add",
          duty="Declare total embedded emissions per MWh for electricity or per tonne for other goods, and have them verified where they rest on actual emissions supplied by the operator through the CBAM registry.",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="submission of the annual CBAM declaration",
          frequency="annual", verification="accredited third party",
          article="Art. 1(5)(a)(1), replacing point (b) of Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D2", "D4", "D5"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          note="The verification duty is newly conditioned on the emissions being 'provided by the operator via the CBAM registry in accordance with Article 10', which ties Art. 8 verification to the Art. 10 registry channel rather than to any actual-emissions claim.")),

    ("B-12", ACT,
     "‘(e) where applicable for the purpose of addressing the risk of misdeclaration resulting from the lack of supply chain traceability",
     "and at the actual time of production referred to in the CBAM declaration;",
     dict(measure_type="obligation", direction="add",
          duty="Include in the CBAM declaration evidence that the goods imported in the preceding calendar year were produced at the declared installation and at the declared time of production.",
          addressee="Authorised CBAM declarants for goods flagged for supply-chain traceability risk",
          cls=B, trigger="goods identified by implementing act as carrying a misdeclaration risk from lack of supply chain traceability",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(a)(2), adding point (e) to Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="Which goods, and which specific evidence, are set by implementing acts under the new Art. 6(6a).")),

    ("B-13", ACT,
     "(f) where, in accordance with a delegated act adopted in accordance with paragraph 7, the embedded emissions are determined on the basis of actual emissions",
     "evidence demonstrating that the high risk of abusive practices has not materialised.’;",
     dict(measure_type="obligation", direction="add",
          duty="Where a goods/origin combination is designated high-risk for abusive practices and actual emissions are claimed, prove in the declaration that the risk has not materialised.",
          addressee="Authorised CBAM declarants claiming actual emissions for high-risk goods/origin combinations",
          cls=B, trigger="delegated act designates a combination of goods and origins as high risk of abusive practices and the declarant claims actual emissions for it",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(a)(2), adding point (f) to Art. 6(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4", "D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The high-risk combinations, and the evidence that discharges the duty, are set by delegated acts under the new Art. 6(7).",
          note="A reversed burden of proof: the declarant must demonstrate a negative, and the only alternative is to abandon the actual-emissions claim and take the default value with its mark-up.")),

    ("B-14", ACT,
     "‘The Commission is empowered to adopt implementing acts concerning the standard format of the CBAM declaration",
     "in particular as regards the process and the selection by the authorised CBAM declarant of certificates to be surrendered.’;",
     dict(measure_type="obligation", direction="add",
          duty="Report, in the standard declaration format, the detail supporting each total -- per installation and country of origin -- including the carbon price paid and the default carbon price for the purposes of Art. 9(4).",
          addressee="Authorised CBAM declarants; European Commission as the act's author",
          cls=B, trigger="submission of the CBAM declaration in the standard format",
          frequency="annual", verification="competent authority",
          article="Art. 1(5)(b), replacing the first sentence of Art. 6(6) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          pending="The format itself is the implementing act; the declaration content follows it.",
          note="NOT IN PASS A. The empowerment is not new, but its content is extended: the format must now carry information 'for each installation and country of origin or other third country and type of goods', the carbon price paid, and the Art. 9(4) default carbon price. That is a per-installation reporting granularity the prior sentence did not demand.")),

    ("B-15", ACT,
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
          note="NOT IN PASS A, where it appears only as B-12's `pending`. Carried as a row because it is the instrument that decides the reach of the Art. 6(2)(e) duty, and until it is adopted that duty binds nobody.")),

    ("B-16", ACT,
     "7. The Commission shall monitor at Union level the impact of the CBAM on the Union internal market.",
     "the evidence to be provided to demonstrate that no abuse has taken place.",
     dict(measure_type="obligation", direction="add",
          duty="Monitor the CBAM's internal-market impact, warn importers, declarants, competent and customs authorities where a goods/origin combination shows a high risk of abusive practices, and set by delegated act the identification method, the information to be declared and the evidence required.",
          addressee="European Commission",
          cls=S, trigger="sufficient evidence pointing towards a high risk of abusive practices for a combination of goods and origins",
          frequency="continuous", verification="none",
          article="Art. 1(5)(c), adding Art. 6(7) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="The engine behind B-13 and B-26. Note the informing limb: the Commission 'may inform importers and authorised CBAM declarants about these risks' -- a designation that is public before any delegated act exists.")),

    ("B-17", ACT,
     "The Commission shall adopt the delegated acts referred to in the first subparagraph within three months of finding that there is sufficient evidence pointing towards a high risk of abusive practices",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Adopt the abusive-practices delegated act within three months of finding sufficient evidence of a high risk.",
          addressee="European Commission",
          cls=S, trigger="Commission finds sufficient evidence of a high risk of abusive practices",
          frequency="if it happens", verification="none",
          article="Art. 1(5)(c), adding Art. 6(7), second subparagraph, to Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="A hard deadline on the Commission, filed separately from B-16 because it is the only thing in Art. 6(7) that is not discretionary: everything else in that paragraph is 'may'.")),

    ("B-18", ACT,
     "‘2a. Embedded emissions in input materials (precursors) listed in Annex VIII shall be considered in the determination of embedded emissions in goods.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Count the embedded emissions of Annex VIII input materials -- ferrous and aluminium waste and scrap other than post-consumer scrap -- in the embedded emissions of the goods.",
          addressee="Authorised CBAM declarants and third-country operators of installations producing Annex I goods",
          cls=B, trigger="determination of embedded emissions in goods produced from Annex VIII input materials",
          frequency="annual", verification="accredited third party",
          article="Art. 1(6)(a), inserting Art. 7(2a) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1", "D2"], named=["steel", "alu"], reached=["auto", "build"],
          note="Closes the scrap route. Under the prior rule only Annex I precursors counted, and scrap sat outside Annex I, so an EAF route through imported scrap carried no precursor emissions. The carve-out for post-consumer scrap is what keeps genuine recycling out.")),

    ("B-19", ACT,
     "‘5. The authorised CBAM declarant shall keep records of the information disclosed in accordance with Article 10(7) that is required to calculate the embedded emissions",
     "to review the CBAM declaration in accordance with Article 19(2).’;",
     dict(measure_type="obligation", direction="rem",
          duty="Keep records detailed enough to let an accredited verifier verify the embedded emissions under Art. 8 and Annex VI, over the full information required to calculate them rather than over what the operator disclosed under Art. 10(7).",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="calculation of embedded emissions for the CBAM declaration",
          frequency="annual", verification="competent authority",
          article="Art. 1(6)(b), replacing Art. 7(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Two limbs move together. The record set narrows to what was disclosed under Art. 10(7), which the declarant actually holds, and the verifier-enablement limb of the prior sentence is dropped, leaving only Commission and competent-authority review. Both are relief; the second is the larger one and is invisible from this act's text alone.")),

    ("B-20", ACT,
     "The implementing acts referred to in the first subparagraph may provide a list of downstream goods for which, due to the complexity of the supply chain",
     "no mark-up is to apply.’;",
     dict(measure_type="obligation", direction="rem",
          duty="Carry the default-value mark-up on downstream goods whose supply-chain complexity makes actual emissions impractical to establish.",
          addressee="Importers and authorised CBAM declarants of listed downstream goods",
          cls=B, trigger="implementing act lists a downstream good as exempt from the mark-up",
          frequency="annual", verification="none",
          article="Art. 1(6)(c), adding a subparagraph to Art. 7(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu"], reached=["auto", "build"],
          pending="The list is a Commission implementing act and does not exist; no good benefits until it is adopted.",
          note="The object is the basis on which the CBAM liability is computed, not any support -- so obligation side, direction rem, per the object rule. This is the main relief offered to the downstream importers B-49 pulls in.")),

    ("B-21", ACT,
     "‘The information contained in that documentation shall be certified by a person that is independent from the authorities of the third country.’;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Have the carbon-price documentation certified by a person independent from the authorised CBAM declarant AS WELL AS from the authorities of the third country.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="claim to deduct a carbon price effectively paid in a third country",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(1), replacing the third sentence of Art. 9(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-9-2",
          prior=dict(
              start="The information contained in that documentation shall be certified by a\xa0person that is independent from the authorised CBAM declarant and from the authorities of the third country.",
              end="",
              trigger="authorised CBAM declarant keeping documentation to demonstrate a carbon price effectively paid in a third country",
              obligation="The prior third sentence of Art. 9(2) required the certifying person to be independent from the authorised CBAM declarant AND from the authorities of the third country. The replacement keeps only the second limb.",
              source_document=PRIOR_DOC + ", Article 9(2), third sentence",
              note="DISAGREES WITH PASS A FIN-06, which files this as direction 'add' and states the duty as 'have the documentation certified by a person independent of that country's authorities'. That duty is not new -- it is the surviving half of a two-limb test. What this provision actually does is DELETE the requirement that the certifier be independent of the declarant itself, which is the limb that stopped a declarant certifying through a person it controls. Read from this act alone the row looks like a fresh requirement; read against the consolidation it is a relaxation."),
          note="The span is a replacement, not a deletion, so nothing in the pipeline forces the prior text to be resolved. It is attached anyway, because the direction is unreadable without it.")),

    ("B-22", ACT,
     "‘The independent person referred to in the first subparagraph may be a legal person accredited by a national accreditation body for the relevant scope of accreditation.’;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Establish that a certifying person meets the Art. 9(2) independence test without an express route through national accreditation.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="selection of the person certifying carbon-price documentation",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(a)(2), adding a subparagraph to Art. 9(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-9-2",
          note="Reads 'may be', which is permissive about WHO QUALIFIES rather than conferring anything on the addressee, so it fails the operative-verb test for `right` and stays obligation/rem. Same conclusion as Pass A FIN-07.")),

    ("B-23", ACT,
     "‘The Commission is empowered to adopt implementing acts, based on the principle of equivalence, concerning the conversion of the yearly average carbon price",
     "The Commission is also empowered to regulate the conditions for deducting carbon credits under Article 6 of the Paris Agreement.",
     dict(measure_type="obligation", direction="add",
          duty="Convert a carbon price paid abroad into a reduction in certificates to be surrendered on the terms the implementing act sets, and satisfy the evidence, currency-conversion and certifier-qualification conditions it lays down.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country; European Commission",
          cls=B, trigger="claim to reduce the number of CBAM certificates on account of a carbon price paid in a third country",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(b)(1), replacing the first subparagraph of Art. 9(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The conversion implementing act does not exist. The Paris Article 6 limb is an empowerment only -- no carbon credit is deductible until it is used.",
          note="Two substantive additions against the prior subparagraph: the yearly DEFAULT carbon prices under Art. 9(4) are brought into the conversion, and the Commission is empowered to regulate deduction of Paris Art. 6 credits, which the prior text did not contemplate at all.")),

    ("B-24", ACT,
     "‘The qualifications referred to in the first subparagraph shall include the granting of accreditation by a national accreditation body, the specification of the certification procedures",
     "the Commission and competent authorities.’;",
     dict(measure_type="obligation", direction="add",
          duty="Use a certifying person holding accreditation from a national accreditation body, following specified certification procedures and subject to information exchange with accreditation bodies, the Commission and competent authorities.",
          addressee="Authorised CBAM declarants claiming a carbon price paid in a third country",
          cls=B, trigger="selection of the person certifying carbon-price documentation",
          frequency="annual", verification="accredited third party",
          article="Art. 1(7)(b)(2), adding a subparagraph to Art. 9(5) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-9-2",
          note="NOT IN PASS A. It matters despite reading as boilerplate: taken with B-22, accreditation stops being one permitted route to independence ('may be') and becomes a mandatory element of the qualifications ('shall include'). The proposal states the same sentence twice -- once inside the Art. 9(5) first subparagraph replaced by B-23 and again as this free-standing subparagraph -- which looks like a drafting slip and is recorded rather than silently merged.")),

    ("B-25", ACT,
     "‘1. To allow the verification of embedded emissions on the basis of actual emissions as well as the determination, where applicable, of the carbon price paid in a third country",
     "register the information on that operator and on its installation in the CBAM registry referred to in Article 14.’;",
     dict(measure_type="right", direction="add",
          benefit="An operator of a third-country installation may have its installation registered in the CBAM registry for the purpose of establishing the carbon price it paid, not only its actual emissions.",
          addressee="Operators of installations located in third countries",
          cls=B, trigger="request by an operator of an installation located in a third country",
          frequency="one-off", verification="competent authority",
          article="Art. 1(8)(a), replacing Art. 10(1) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D1"], named=["steel", "alu", "cement", "chem"], reached=[],
          right_basis=dict(text="as well as the determination, where applicable, of the carbon price paid in a third country", kind="scope"),
          note="The registration faculty existed; its purpose is widened to carbon-price determination, so what is conferred is extent, not the faculty itself -- hence a `scope` basis rather than `conferral`. Same conclusion as Pass A DATA-05.")),

    ("B-26", ACT,
     "‘(e) ensure, where applicable pursuant to Article 6(7), that the conditions laid down for the use of actual emissions, for relevant combinations of goods and origins, are met.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Ensure that the conditions laid down for the use of actual emissions are met for the relevant goods/origin combinations.",
          addressee="Operators of installations located in third countries registered in the CBAM registry",
          cls=B, trigger="goods/origin combination designated under Art. 6(7) and actual emissions used",
          frequency="annual", verification="accredited third party",
          article="Art. 1(8)(b), adding point (e) to Art. 10(5) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Pushes the abuse-risk conditions upstream onto the third-country operator, where the prior Art. 10(5) list stopped at emissions data and verification reports.")),

    ("B-27", ACT,
     "‘An operator may disclose the information on the conditions for the use of actual emissions, for the relevant combinations of goods and origins pursuant to Article 6(7)",
     "to an authorised CBAM declarant or to another operator.",
     dict(measure_type="right", direction="add",
          benefit="An operator may disclose its verified emissions, carbon-price and actual-emissions-condition information to another operator, not only to an authorised CBAM declarant.",
          addressee="Operators of installations located in third countries",
          cls=B, trigger="operator holds Art. 10(5) information another operator needs",
          frequency="if it happens", verification="none",
          article="Art. 1(8)(c), replacing the first sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=J2028,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          right_basis=dict(text="to an authorised CBAM declarant or to another operator.", kind="conferral"),
          note="A channel that did not exist: the prior sentence allowed disclosure to the declarant only, which broke the chain for a precursor producer supplying a downstream operator. Operative verb 'may disclose' confers. Same conclusion as Pass A DATA-01.")),

    ("B-28", ACT,
     "‘The operator may disclose to the authorised CBAM declarant only a summary of the information contained in paragraph 5, points (a), (b), (c) and (e).",
     "The authorised CBAM declarant shall be entitled to use that disclosed information in order to fulfil the obligation referred to in Article 8.",
     dict(measure_type="right", direction="add",
          benefit="The operator may hand over only a summary of its Art. 10(5) information, and the declarant is entitled to use that summary to discharge its Art. 8 verification obligation.",
          addressee="Operators of third-country installations and the authorised CBAM declarants they supply",
          cls=B, trigger="operator discloses Art. 10(5) information to a declarant",
          frequency="annual", verification="accredited third party",
          article="Art. 1(8)(d), replacing the second sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          right_basis=dict(text="shall be entitled to use that disclosed information in order to fulfil the obligation referred to in Article 8", kind="conferral"),
          note="Confidentiality relief for the operator and a usable evidence base for the declarant, in one sentence. Two-sided with B-29, which is the price of it.")),

    ("B-29", ACT,
     "Where the authorised CBAM declarant chooses to submit the CBAM declaration on the basis of this disclosed information, the authorised CBAM declarant shall remain responsible for surrendering the correct number of CBAM certificates",
     "pursuant to Article 22(1).’;",
     dict(measure_type="obligation", direction="add",
          duty="Remain responsible for surrendering the correct number of CBAM certificates even where the declaration rests on a summary disclosed by the operator.",
          addressee="Authorised CBAM declarants relying on operator-disclosed summaries",
          cls=B, trigger="declaration submitted on the basis of information disclosed by the operator",
          frequency="annual", verification="competent authority",
          article="Art. 1(8)(d), replacing the second sentence of Art. 10(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="The liability that makes B-28 less generous than it reads: the declarant may rely on a summary it cannot check, and still carries the shortfall.")),

    ("B-30", ACT,
     "‘5a. By way of derogation from paragraph 5, where the competent authority finds that the applicant or the authorised CBAM declarant does not demonstrate its financial capacity",
     "another form of guarantee which provides equivalent assurance.’;",
     dict(measure_type="obligation", direction="add",
          duty="Provide a first-demand bank guarantee, or equivalent, sized on the certificates that would have to be surrendered, where the competent authority finds financial capacity is not demonstrated.",
          addressee="Applicants for and holders of authorised CBAM declarant status",
          cls=B, trigger="competent authority finds the applicant or declarant does not demonstrate financial capacity, including by failing the Art. 22(2) holding requirement",
          frequency="if it happens", verification="competent authority",
          article="Art. 1(9)(a), inserting Art. 17(5a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6", "D3", "D1"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="The heaviest business row in the proposal. Note the third sizing basis: 'an estimation as if the single mass-based threshold were exceeded', which lets an authority size a guarantee against imports that have not happened. Prior Art. 17(5) allowed a guarantee only for a declarant not established for two financial years.")),

    ("B-31", ACT,
     "‘7. Where a guarantee is required in accordance with paragraph 5, the competent authority shall release the guarantee immediately after 30 September of the second year",
     "based on the number of certificates that should have been surrendered and the price of certificates on the date where the decision was taken.’;",
     dict(measure_type="obligation", direction="add",
          duty="Leave the guarantee outstanding until after 30 September of the second surrender year, and for longer where the authority duly justifies an extension; the authority may draw on it to recover an unpaid adjustment.",
          addressee="Authorised CBAM declarants that have provided a guarantee",
          cls=B, trigger="guarantee required under Art. 17(5) or the new Art. 17(5a)",
          frequency="if it happens", verification="competent authority",
          article="Art. 1(9)(b), replacing Art. 17(7) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="Filed 'add' on the discretionary extension and the recovery mechanism, both of which are new. The release rule for paragraph-5 guarantees is carried over unchanged, so nothing is relieved.")),

    ("B-32", ACT,
     "‘Those delegated acts shall also specify the verification procedures to be used by verifiers.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Follow the verification procedures the Art. 18(3) delegated acts specify.",
          addressee="Accredited verifiers, and the European Commission as the act's author",
          cls=S, trigger="verification of embedded emissions under Art. 8",
          frequency="annual", verification="accredited third party",
          article="Art. 1(10), adding a sentence to Art. 18(3) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D2"], named=["steel", "alu", "cement", "chem"], reached=[],
          pending="The delegated acts specifying the procedures do not exist yet.",
          note="Reads as procedural, but it is the counterweight to B-46: the verification-report content requirements deleted from Annex VI move into delegated acts that have not been written.")),

    ("B-33", ACT,
     "‘2a. Where the embedded emissions are determined on the basis of actual emissions, the Commission or the competent authority of the Member State where the CBAM declarant is established may",
     "provide evidence that the goods imported were produced at the installation referred to in the CBAM declaration.’;",
     dict(measure_type="obligation", direction="add",
          duty="Produce, on request during review of the declaration, evidence that the imported goods were produced at the installation named in it.",
          addressee="Authorised CBAM declarants using actual emissions",
          cls=B, trigger="Commission or competent authority reviews a CBAM declaration based on actual emissions",
          frequency="if it happens", verification="competent authority",
          article="Art. 1(11), inserting Art. 19(2a) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D1", "D4"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="The review-stage twin of B-12: the same installation-of-production evidence, but demandable from any actual-emissions declarant rather than only for goods designated as traceability risks.")),

    ("B-34", ACT,
     "‘For those calendar weeks in which there is no auction on the auction platform, the price of CBAM certificates shall be the average of the closing prices of EU ETS allowances",
     "the closing prices of the last week in which several auctions took place on the auction platform.’;",
     dict(measure_type="obligation", direction="add",
          duty="Pay the certificate price fixed by the fallback rule in weeks with no auction or a single auction, computed off the last week in which auctions (or several auctions) took place.",
          addressee="Authorised CBAM declarants purchasing CBAM certificates",
          cls=B, trigger="calendar week with no auction, or with only one auction, on the auction platform",
          frequency="weekly", verification="none",
          article="Art. 1(12)(a), replacing the second subparagraph of Art. 21(1) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=["steel", "alu", "cement", "chem", "power"], reached=[],
          note="A pricing-basis change, filed 'add' because it introduces a determinate rule where the prior subparagraph left the single-auction week unaddressed. It moves the price a declarant pays, not any support, so it stays obligation side.")),

    ("B-35", ACT,
     "‘The Commission shall publish the price of CBAM certificates on its website or in any other appropriate manner on the first working day of the following calendar week.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Publish the CBAM certificate price on the first working day of the following calendar week.",
          addressee="European Commission",
          cls=S, trigger="close of each calendar week's certificate pricing",
          frequency="weekly", verification="none",
          article="Art. 1(12)(b), replacing the first sentence of Art. 21(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D5"], named=[], reached=["steel", "alu", "cement", "chem", "power"],
          note="Companion to B-34: the fallback price rules are only usable if the resulting price appears on a predictable day.")),

    ("B-36", ACT,
     "‘From 2028, the calculation referred to in the first subparagraph shall be based only on CBAM certificates purchased by the authorised CBAM declarant during that same year.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="From 2028, satisfy the quarterly certificate-holding requirement out of certificates purchased in that same year, with no carry-over from earlier holdings.",
          addressee="Authorised CBAM declarants",
          cls=B, trigger="quarterly assessment of the Art. 22(2) certificate holding",
          frequency="quarterly", verification="competent authority",
          article="Art. 1(13), adding a subparagraph to Art. 22(2) of Regulation (EU) 2023/956",
          when="from 2028",
          drivers=["D6", "D5"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="A working-capital tightening: banking certificates bought cheaply in an earlier year no longer counts toward the holding requirement. It also feeds B-30, because failing Art. 22(2) is an express ground for demanding a guarantee.")),

    ("B-37", ACT,
     "‘The excess CBAM certificates shall be repurchased through the common central platform referred to in Article 20.’;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Direct the repurchase request to the Commission acting on behalf of the Member State of establishment.",
          addressee="Authorised CBAM declarants requesting repurchase of excess certificates",
          cls=B, trigger="request to repurchase excess CBAM certificates after surrender",
          frequency="annual", verification="none",
          article="Art. 1(14), replacing the first sentence of the second subparagraph of Art. 23(1) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          note="WEAK ROW, recorded as weak. Against the consolidated text the change is that the sentence stops naming the Commission as the actor repurchasing 'on behalf of the Member State' and states the repurchase passively. The platform was already the channel. Pass A FIN-05 also files it rem; both of us are labelling a drafting tidy-up, and it is closer to Neutral than to Simplification.")),

    ("B-38", ACT,
     "‘2. The customs authorities shall periodically and automatically, in particular by means of the surveillance mechanism established pursuant to Article 56(5)",
     "the customs authorities shall also communicate the name, address and, where available, contact information of the importer to the Commission.",
     dict(measure_type="obligation", direction="add",
          duty="Communicate to the Commission, periodically and automatically, the CBAM account number, customs procedure, bills of discharge, re-export declarations and equivalent customs documentation alongside the existing import data, and the importer's name and address where there is no EORI number.",
          addressee="Member State customs authorities",
          cls=S, trigger="importation of goods listed in Annex I or processed products obtained from them",
          frequency="continuous", verification="none",
          article="Art. 1(15)(a), replacing Art. 25(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4", "D5"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="The data spine of the anti-circumvention package: bills of discharge and re-export declarations are what make the inward-processing route in B-01 auditable.")),

    ("B-39", ACT,
     "The CBAM account number provided in the customs declaration or any other relevant document when declaring goods listed in Annex I or processed products obtained from such goods for importation",
     "shall determine the authorised CBAM declarant assuming the obligations set out in this Regulation.’;",
     dict(measure_type="obligation", direction="add",
          duty="Accept that the CBAM account number quoted in the customs declaration fixes which authorised declarant carries the obligations for that consignment.",
          addressee="Authorised CBAM declarants and importers quoting a CBAM account number",
          cls=B, trigger="a CBAM account number is provided in a customs declaration or accompanying document",
          frequency="per consignment", verification="customs authorities",
          article="Art. 1(15)(a), replacing Art. 25(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="An attribution rule with real consequences: liability follows the account number quoted at the border, so a misquoted or borrowed number lands the obligation on its holder.")),

    ("B-40", ACT,
     "‘Where the competent authority considers that the information is incorrect or inaccurate, the competent authority may request the customs authorities or the Commission to verify the correctness or the accuracy of that information.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Verify, on a competent authority's request, the correctness or accuracy of communicated customs information.",
          addressee="Member State customs authorities and the European Commission",
          cls=S, trigger="competent authority considers communicated information incorrect or inaccurate",
          frequency="if it happens", verification="none",
          article="Art. 1(15)(b), adding a subparagraph to Art. 25(3) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[])),

    ("B-41", ACT,
     "‘The Commission is empowered to adopt implementing acts defining the scope of information and the periodicity, timing and means for communicating that information pursuant to paragraphs 2 and 3 of this Article.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Communicate customs information at the scope, periodicity, timing and by the means the implementing acts prescribe.",
          addressee="Member State customs authorities",
          cls=S, trigger="adoption of the Art. 25(6) implementing acts",
          frequency="continuous", verification="none",
          article="Art. 1(15)(c), replacing the first sentence of Art. 25(6) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4"], named=["steel", "alu", "cement", "chem"], reached=[],
          note="NOT IN PASS A. Thin on its own -- the empowerment existed and is extended to cover paragraph 3 as well as paragraph 2 -- and carried so the Art. 25 amendments are complete rather than three of four.")),

    ("B-42", ACT,
     "‘7. The Commission is empowered to adopt implementing acts to identify the material and chemical compositions of goods listed in Annex I.",
     "in accordance with the examination procedure referred to in Article 29(2).’;",
     dict(measure_type="obligation", direction="add",
          duty="Determine the embedded emissions of downstream goods against the material and chemical compositions the Commission identifies by implementing act.",
          addressee="Importers and authorised CBAM declarants of Annex I goods, in particular downstream goods",
          cls=B, trigger="adoption of implementing acts identifying material and chemical compositions",
          frequency="annual", verification="accredited third party",
          article="Art. 1(15)(d), adding Art. 25(7) to Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D4"], named=["steel", "alu"], reached=["auto", "build"],
          pending="The composition implementing acts do not exist. Without them the mass-of-precursor rule in B-54 cannot be applied to a combined metal product.",
          note="The hinge between the scope extension and the calculation rules: a combined metal product's CBAM liability turns on how much steel or aluminium it is deemed to contain, and this is where that number will come from.")),

    ("B-43", ACT,
     "‘(c) artificially adjusting the supply chains to make the goods benefit from lower default values.’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Refrain from artificially adjusting supply chains so that goods qualify for lower default values.",
          addressee="Importers, authorised CBAM declarants and third-country operators",
          cls=B, trigger="restructuring of a supply chain that changes which default value applies",
          frequency="continuous", verification="competent authority",
          article="Art. 1(16), adding point (c) to Art. 27(2) of Regulation (EU) 2023/956",
          when=EIF,
          drivers=["D6"], named=["steel", "alu", "cement", "chem"], reached=["auto", "build"],
          note="Named circumvention practice, so it carries the Art. 27 consequences. It bites hardest on the country-specific default values in B-55 and B-56: routing output through a lower-factor country is now nameable as circumvention.")),

    ("B-44", ACT,
     "Where the Commission, taking into account the relevant evidence, considers that the inclusion of a good in Annex I causes severe harm to the Union internal market",
     "to remove this good from Annex I until those serious and unforeseeable circumstances have passed.’;",
     dict(measure_type="obligation", direction="rem",
          duty="Comply with CBAM for a good whose inclusion in Annex I is causing severe harm to the internal market through serious and unforeseen price effects.",
          addressee="Importers of goods withdrawn from Annex I under the safeguard",
          cls=B, trigger="Commission finds that a good's inclusion in Annex I causes severe harm to the internal market due to serious and unforeseen circumstances affecting prices",
          frequency="if it happens", verification="none",
          article="Art. 1(17), inserting Art. 27a of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu"], reached=["auto", "build"],
          pending="An empowerment to adopt delegated acts, with no good yet removed.",
          note="A safeguard valve on scope: the object is the reach of the CBAM duty, so obligation side, direction rem. Nothing is conferred on any firm -- no operator can trigger it.")),

    ("B-45", ACT,
     "‘Before 1 January 2028, as well as every two years thereafter, the Commission shall present a report to the European Parliament and to the Council",
     "aggregated information on the emission intensity for each country of origin for the different goods listed in Annex I.;’",
     dict(measure_type="obligation", direction="add",
          duty="Report to the Parliament and Council before 1 January 2028 and every two years after, covering internal-market and territorial impact, inflation and commodity prices, downstream user industries, the suitability of the default-value and mark-up methods, guarantee administration, and the mass-based threshold.",
          addressee="European Commission",
          cls=S, trigger="the biennial reporting cycle",
          frequency="biennial", verification="none",
          article="Art. 1(20), replacing the second subparagraph of Art. 30(6) of Regulation (EU) 2023/956",
          when="before 1 January 2028, then every two years",
          drivers=["D5"], named=[], reached=["steel", "alu", "cement", "chem", "auto", "build"],
          note="The review hooks worth tracking are the new ones: mark-up suitability, guarantee administration, and 'the possibility of increasing that threshold and of introducing a supplementary consignment-based threshold' -- the route by which the de minimis could move again.")),

    ("B-46", ACT,
     "(a)points (g) to (j) are deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="State in the verification report the quantities of each type of declared goods produced, the quantification of the installation's direct emissions, how those emissions are attributed across types of goods, and the goods, emissions and energy flows not associated with them.",
          addressee="Accredited verifiers preparing CBAM verification reports",
          cls=B, trigger="preparation of a verification report under Art. 8",
          frequency="annual", verification="accredited third party",
          article="Art. 1(23)(a), deleting points (g) to (j) of point 2 of Annex VI of Regulation (EU) 2023/956",
          when=J2028,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=[],
          provision_id="cbam-annex-vi-2",
          prior=dict(
              start="quantities of each type of declared goods produced in the reporting period;",
              end="quantitative information on the goods, emissions and energy flows not associated with those goods;",
              trigger="verifier preparing a verification report establishing the embedded emissions of the goods",
              obligation="Points (g) to (j) of Annex VI point 2 required the verification report to state the quantities of each type of declared goods produced in the reporting period, the quantification of the installation's direct emissions during the reporting period, a description of how the installation's emissions are attributed to different types of goods, and quantitative information on the goods, emissions and energy flows not associated with those goods.",
              source_document=PRIOR_DOC + ", Annex VI, point 2, points (g) to (j)",
              note="RE-CHECKED AGAINST THE PRIOR CORPUS INDEPENDENTLY. Confirms Pass A GOV-04 on all three counts. The four points are at lines 2715-2733 of the prior consolidation, under the heading '2. CONTENT OF A VERIFICATION REPORT', whose chapeau reads 'The verifier shall prepare a verification report ... including, at least, the following information'. So the addressee is the accredited verifier, not the operator or the declarant; the deleted contents are exactly the four described; and removing four mandatory report contents is relief, so direction rem is right. Nothing to correct."),
          note="The act supplies only the amending instruction. Everything deciding the valence is in the prior rule. See B-32: the same detail may return via Art. 18(3) delegated acts.")),

    ("B-47", ACT,
     "‘(ka) material composition of each downstream good;’;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="State the material composition of each downstream good in the verification report.",
          addressee="Accredited verifiers preparing CBAM verification reports",
          cls=B, trigger="preparation of a verification report covering downstream goods",
          frequency="annual", verification="accredited third party",
          article="Art. 1(23)(b), inserting point (ka) in point 2 of Annex VI of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["steel", "alu"], reached=["auto", "build"],
          provision_id="cbam-annex-vi-2",
          note="The new content that replaces what B-46 deletes, and it is the harder one for a combined metal product: it requires a bill of materials for goods whose producer may be several tiers away from the steel mill.")),

    # ---------------------------------------------------------- Annex I of the act
    ("B-48", ANNEX,
     "2601 12 00 – Agglomerated iron ores and concentrates, other than roasted iron pyrites",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Declare embedded emissions and surrender certificates for goods newly added to the 'Iron and steel' table -- agglomerated iron ore, stranded wire and cables, unplated welded grill and netting, springs, enamelled and other household articles, and other cast articles of iron or steel.",
          addressee="Importers and authorised CBAM declarants of the newly listed iron and steel goods",
          cls=B, trigger="importation of goods under the CN codes added to the Annex I 'Iron and steel' table",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (1) replacing the 'Iron and Steel' table in point 2 of Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4", "D2", "D6"],
          named=["steel"], reached=["auto", "build"],
          note="NOT IN PASS A, which carries the new 'Combined metal products' table (Annex I point (2)) as SCP-04/SCP-05 but nothing for the REPLACEMENT of the existing 'Iron and steel' table. The replacement is not cosmetic. Diffed against the prior Annex I it adds 2601 12 00 (agglomerated iron ores and concentrates), 7312 10 (stranded wire, ropes and cables), 7314 39 00 (unplated welded grill, netting and fencing), 7320 20 89 and 7320 90 90 (springs), 7323 94 00 and 7323 99 00 (household articles) and 7325 (other cast articles). Agglomerated iron ore is the significant one: it is an upstream input, not a downstream good, and it reaches the sintering and pelletising trade that the downstream story does not describe. The row anchors on the iron-ore line as the clearest single instance.")),

    ("B-49", ANNEX,
     "‘[Combined metal products",
     "(excl. plated or coated with zinc or coated with plastics)",
     dict(measure_type="obligation", direction="add",
          duty="Declare embedded emissions and surrender certificates for the new 'Combined metal products' category -- downstream manufactured goods containing steel or aluminium, which were outside the CBAM entirely.",
          addressee="Importers and authorised CBAM declarants of downstream steel- and aluminium-containing goods",
          cls=B, trigger="importation of goods listed in the new 'Combined metal products' table of Annex I",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (2) adding the 'Combined metal products' table to Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4", "D2", "D6"],
          named=["steel", "alu"], reached=["auto", "build"],
          note="The headline measure. Scope extension is the strongest form of 'add' -- D7, newly inside the regime. The table runs from fencing wire to prefabricated buildings, trailer parts and medical instruments, so the addressee is usually a manufacturer or distributor with no prior CBAM exposure and no relationship with the mill that made the metal.")),

    ("B-50", ANNEX,
     "ex- 9406 90 90 – Prefabricated buildings, containing steel or aluminium",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Declare embedded emissions and surrender certificates for imported prefabricated buildings containing steel or aluminium.",
          addressee="Importers of prefabricated buildings containing steel or aluminium",
          cls=B, trigger="importation of prefabricated buildings under CN ex- 9406 90 90 containing steel or aluminium",
          frequency="per consignment", verification="accredited third party",
          article="Art. 1(21); Annex I, point (2) adding the 'Combined metal products' table to Annex I of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D7", "D1", "D4"], named=["build"], reached=["steel", "alu"],
          note="Kept as its own row for the same reason Pass A does: it is the clearest case of the extension reaching a sector CBAM has never touched, and the addressee is a construction-products importer rather than a metals importer.")),

    # --------------------------------------------------------- Annex II of the act
    ("B-51", ANNEX,
     "‘(e) ‘emission factor for electricity’ means the weighted average of the CO2 intensity of the electricity produced within a geographic area;",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Use, as the emission factor for electricity, the weighted average CO2 intensity of all electricity produced in the geographic area, in place of a factor representing the emission intensity of the electricity consumed in producing the goods.",
          addressee="Importers and authorised CBAM declarants of electricity and of goods with indirect emissions",
          cls=B, trigger="determination of default values for imported electricity or for embedded indirect emissions",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (1) replacing point (e) of point 1 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=["D4"], named=["power"], reached=["steel", "alu", "cement", "chem"],
          provision_id="cbam-annex-iv-1",
          note="NOT IN PASS A, and it is load-bearing rather than definitional. The prior point (e) defined the term as 'the default value, expressed in CO2e, representing the emission intensity of electricity consumed in production of goods'. Two things change: the basis moves from electricity CONSUMED in production to electricity PRODUCED in a geographic area, and it becomes a weighted average of CO2 intensity. Every one of Pass A's ELEC-01, ELEC-02 and ELEC-03 turns on the substitution of this term for 'CO2 emission factor' in points 4.2.1, 4.2.2 and 4.3 -- so the register currently states the effect of those substitutions without carrying the definition that produces it. Filed 'add' because it imposes a new measurement basis, and it applies from 1 January 2026, before any of them.")),

    ("B-52", ANNEX,
     "(f) ‘power purchase agreement’ means a contract under which a person agrees to purchase electricity directly from an electricity producer and that involves the physical delivery of electricity;’;",
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
          prior=dict(
              start="‘power purchase agreement’ means a contract under which a person agrees to purchase electricity directly from an electricity producer;",
              end="",
              trigger="authorised CBAM declarant relying on a power purchase agreement to claim actual embedded emissions",
              obligation="The prior Annex IV point 1(f) defined a power purchase agreement as 'a contract under which a person agrees to purchase electricity directly from an electricity producer', with no delivery requirement.",
              source_document=PRIOR_DOC + ", Annex IV, point 1, point (f)",
              note="The added words are 'and that involves the physical delivery of electricity'. A financial or virtual PPA satisfied the prior definition and does not satisfy this one."),
          note="NOT IN PASS A. This cuts the opposite way from ELEC-04's relaxation on intermediaries, and it is the tighter of the two: intermediated chains are now allowed, but only if physical delivery runs through them. Filed as a definition row because the condition it changes lives in Annex IV point 5(a), which Pass A reads as relief without this qualification.")),

    ("B-53", ANNEX,
     "Only input materials (precursors) listed in Annex I and Annex VIII and originating in third countries and territories that are not exempted pursuant to Annex III, Section 1 are to be considered.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Compute complex-goods emissions counting precursors from Annex VIII as well as Annex I, excluding those originating in exempted third countries.",
          addressee="Third-country operators and authorised CBAM declarants for complex goods",
          cls=B, trigger="determination of specific actual embedded emissions of complex goods",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (2) replacing point 3 of Annex IV of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["steel", "alu"], reached=["auto", "build"],
          provision_id="cbam-annex-iv-3",
          note="Operationalises B-18. DISAGREES WITH PASS A CALC-02 ON `when` ONLY: CALC-02 reads '1 January 2026 per Art. 2 (Annex II point 1)', but this provision is Annex II point (2), and Art. 2 puts point 2 of Annex II in the 2028 sentence, not the 2026 one. Points 1 and 6 of Annex II are the 2026 ones.")),

    ("B-54", ANNEX,
     "However, for goods listed in sections ‘Iron and Steel’, ‘Aluminium’ and ‘Combined Metal Goods’ of Annex I, Mi is a function of the content of goods used as input materials (precursors) in the manufacturing of the good.",
     "",
     dict(measure_type="obligation", direction="add",
          duty="For iron and steel, aluminium and combined metal goods, derive the precursor mass from the content of input goods in the finished product rather than from a directly measured input mass.",
          addressee="Third-country operators and authorised CBAM declarants for iron, steel, aluminium and combined metal goods",
          cls=B, trigger="determination of specific actual embedded emissions for goods in those three Annex I sections",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (2) replacing point 3 of Annex IV of Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["steel", "alu"], reached=["auto", "build"],
          provision_id="cbam-annex-iv-3",
          note="The only route by which a downstream importer can compute anything: it will rarely know the mass of steel consumed at the mill, but it can be attributed the metal content of what it imports. Depends entirely on B-42's composition implementing acts. DISAGREES WITH PASS A CALC-03 ON `when`: CALC-03 reads 'from entry into force', but Art. 2 puts point 2 of Annex II at 1 January 2028. Note also that the section is named 'Combined Metal Goods' here while Annex I creates a table called 'Combined metal products'; the two names do not match, which is a defect in the proposal and is recorded, not smoothed over.")),

    ("B-55", ANNEX,
     "Specific default values shall be set at the emission factor for electricity in the third country, group of third countries or region within a third country, based on the best data available to the Commission.",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Take specific default values for imported electricity from the CO2 emission factor in the exporting country, rather than from the weighted average CO2 intensity of the electricity produced there.",
          addressee="Importers and authorised CBAM declarants of electricity",
          cls=B, trigger="determination of specific default values for imported electricity",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (3) replacing point 4.2.1 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          provision_id="cbam-annex-iv-4-2-1",
          note="Agrees with Pass A ELEC-01 on direction. Recorded with a caveat Pass A does not carry: the ONLY textual change is 'CO2 emission factor' -> 'emission factor for electricity', and the relief comes entirely from B-51's redefinition of that term. Read against this act alone the sentence says nothing about fossil generation either way, and the register presently asserts the effect without holding the definition.")),

    ("B-56", ANNEX,
     "Where it can be demonstrated, on the basis of reliable data, that the emission factor for electricity in a third country, a group of third countries or a region within a third country is lower than the specific default value",
     "may be used for that third country, group of third countries or region within a third country.’;",
     dict(measure_type="obligation", direction="rem",
          duty="Accept the specific or Union default value where the exporting country's electricity emissions are lower, measured as a CO2 emission factor rather than as an emission factor for electricity.",
          addressee="Importers and authorised CBAM declarants of electricity",
          cls=B, trigger="reliable data show the exporting area's electricity emission factor is below the applicable default",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (4) replacing point 4.2.2 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["power"], reached=[],
          provision_id="cbam-annex-iv-4-2-2",
          prior=dict(
              start="Where it can be demonstrated, on the basis of reliable data, that the CO2 emission factor in a third country, a group of third countries or a region within a third country is lower than the specific default value determined by the Commission or lower than the CO2 emission factor in the Union, an alternative default value based on that CO2 emission factor may be used",
              end="",
              trigger="declarant demonstrating a lower electricity emission factor for the exporting area",
              obligation="The prior point 4.2.2 already provided that where reliable data show the CO2 emission factor in a third country, group of third countries or region is lower than the specific default value or than the Union CO2 emission factor, 'an alternative default value based on that CO2 emission factor may be used'. The faculty is word-for-word the prior faculty with the metric changed.",
              source_document=PRIOR_DOC + ", Annex IV, point 4.2.2, second paragraph",
              note="DISAGREES WITH PASS A ELEC-02, which files this as measure_type 'right', direction 'add', valence Entitlement, on a `scope` basis quoting the demonstration sentence. Nothing is conferred: the demonstration route, the 'may be used' verb and the comparison against both benchmarks are all in the prior text. Only the metric changes, from 'CO2 emission factor' to 'emission factor for electricity'. Under the operative-verb test a faculty the addressee already held cannot be an Entitlement, and the guardrail did not catch it because a prior faculty is invisible to a basis check run against this act alone."),
          note="Filed obligation/rem: the object is the basis on which the liability is computed, and the new metric is the lower one for a clean grid. That is Simplification, not Entitlement.")),

    ("B-57", ANNEX,
     "‘Where a third country, or a group of third countries, demonstrates to the Commission, on the basis of reliable data, that the average electricity mix emission factor or CO2 emission factor of price-setting sources",
     "shall be established for this country or group of countries.’;",
     dict(measure_type="obligation", direction="rem",
          duty="Take the alternative default value for indirect emissions from the average CO2 emission factor alone, with no route through the average electricity mix emission factor.",
          addressee="Importers and authorised CBAM declarants of goods carrying embedded indirect emissions",
          cls=B, trigger="third country demonstrates a lower factor than the default value for indirect emissions",
          frequency="annual", verification="none",
          article="Art. 1(22); Annex II, point (5) replacing the second paragraph of point 4.3 of Annex IV of Regulation (EU) 2023/956",
          when=EIF,
          drivers=[], named=["steel", "alu", "cement", "chem"], reached=["power"],
          provision_id="cbam-annex-iv-4-3",
          prior=dict(
              start="an alternative default value based on that average CO2 emission factor shall be established for this country or group of countries.",
              end="",
              trigger="third country demonstrating a lower indirect-emissions factor",
              obligation="The prior second paragraph of point 4.3 let a country demonstrate a lower average electricity mix emission factor OR CO2 emission factor of price-setting sources, but then established the alternative default value 'based on that average CO2 emission factor' only.",
              source_document=PRIOR_DOC + ", Annex IV, point 4.3, second paragraph",
              note="A gap in the prior drafting: the two things a country could demonstrate were not the two things the value could be based on. The replacement closes it by allowing either."),
          note="Agrees with Pass A ELEC-03 on direction, with the prior text attached so the mechanism is legible: the relief is that the demonstrated electricity-mix factor can now actually be used.")),

    ("B-58", ANNEX,
     "Power purchase agreements involving intermediaries shall also be allowed, as long as a verifiable contractual relationship between the producer of electricity, the intermediaries, and the importer, or CBAM declarant, can be demonstrated",
     "in relation to the electricity for which the use of actual emissions is claimed;’;",
     dict(measure_type="obligation", direction="rem",
          duty="Hold the power purchase agreement directly between the authorised CBAM declarant and the third-country producer, with no intermediary in the chain.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(a) replacing point (a) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=[], named=["power"], reached=[],
          provision_id="cbam-annex-iv-5",
          note="Agrees with Pass A ELEC-04 on direction, DISAGREES ON `when`: ELEC-04 reads 'from entry into force', but Art. 2 says 'Points 1 and 6 of Annex II, shall apply from 1 January 2026' and this is Annex II point 6(a). Recital 53 confirms the intent -- the conditions for applying actual embedded emissions in imported electricity 'should apply to imports of electricity that occurred as of 1 January 2026'. The relief is also narrower than it looks: B-52 adds a physical-delivery requirement to the same PPA in the same Annex II point 1, so an intermediated chain qualifies only if the electricity physically moves through it.")),

    ("B-59", ANNEX,
     "(b)\n\xa0\xa0\xa0point (b) is deleted;",
     "",
     dict(measure_type="obligation", direction="rem",
          duty="Demonstrate that the generating installation is directly connected to the Union transmission system, or that no physical network congestion existed anywhere between it and that system at the time of export, in order to claim actual emissions for imported electricity.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(b) deleting point (b) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=[], named=["power"], reached=[],
          provision_id="cbam-annex-iv-5",
          prior=dict(
              start="the installation producing electricity is either directly connected to the Union transmission system",
              end="between the installation and the Union transmission system;",
              trigger="authorised CBAM declarant applying actual embedded emissions instead of default values for imported electricity",
              obligation="Point (b) of Annex IV point 5 was one of the cumulative criteria for applying actual embedded emissions: the generating installation had to be either directly connected to the Union transmission system, or it had to be demonstrated that at the time of export there was no physical network congestion at any point in the network between the installation and the Union transmission system.",
              source_document=PRIOR_DOC + ", Annex IV, point 5, point (b)",
              note="RE-CHECKED AGAINST THE PRIOR CORPUS INDEPENDENTLY. Confirms Pass A ELEC-05. The deleted point is at line 2567 of the prior consolidation, inside '5. CONDITIONS FOR APPLYING ACTUAL EMBEDDED EMISSIONS IN IMPORTED ELECTRICITY', whose chapeau reads 'may apply actual embedded emissions instead of default values ... if the following cumulative criteria are met'. Cumulative is the word that decides it: removing one of five criteria relieves, so direction rem is right. Pass A's observation that the surviving point (c) keeps the 550 g CO2/kWh cap also checks out -- Annex II point (6) touches only (a), (b) and (d), so (c) and (e) stand. Nothing to correct in the reading. The one thing to correct is next to it: `when`, which Pass A gives as 'from entry into force' and Art. 2 puts at 1 January 2026."),
          note="The act supplies only the instruction '(b) point (b) is deleted;'. Everything deciding the valence is in the prior rule.")),

    ("B-60", ANNEX,
     "‘(d) the amount of electricity for which the use of actual embedded emissions is claimed has been firmly nominated to the allocated interconnection capacity",
     "This criterion shall not be fulfilled in cases where transmission capacity for the import of electricity is allocated through implicit capacity allocation;’.",
     dict(measure_type="obligation", direction="add",
          duty="Firmly nominate the claimed electricity to allocated interconnection capacity in the countries of origin, destination and transit, match nomination to production within the same hour, and forgo the claim entirely where capacity is allocated implicitly.",
          addressee="Importers and authorised CBAM declarants of electricity claiming actual emissions",
          cls=B, trigger="claim to use actual embedded emissions for imported electricity",
          frequency="annual", verification="accredited third party",
          article="Art. 1(22); Annex II, point (6)(c) replacing point (d) of point 5 of Annex IV of Regulation (EU) 2023/956",
          when=J2026,
          drivers=["D4", "D1"], named=["power"], reached=[],
          provision_id="cbam-annex-iv-5",
          note="The nomination and hourly-matching test was already in the prior point (d); what is new is the final sentence excluding implicit capacity allocation, which shuts the actual-emissions route for market-coupled borders outright. Agrees with Pass A ELEC-06 on direction, DISAGREES ON `when` for the same reason as B-58 and B-59.")),

    # -------------------------------------------------------- Annex III of the act
    ("B-61", ANNEX,
     "ex 7204 Ferrous waste and scrap; remelting scrap ingots and steel except post-consumer scrap",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Count the embedded emissions of imported ferrous waste and scrap, other than post-consumer scrap, as a precursor in the embedded emissions of the goods produced from it.",
          addressee="Third-country operators and authorised CBAM declarants for steel goods produced from imported scrap",
          cls=B, trigger="ferrous waste or scrap used as an input material in producing an Annex I good",
          frequency="annual", verification="accredited third party",
          article="Art. 1(24); Annex III adding Annex VIII to Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["steel"], reached=["auto", "build"],
          note="Annex VIII is a list of NON-CBAM goods treated as precursors: the scrap itself is not chargeable on import, but its emissions now travel into whatever is made from it. The post-consumer carve-out keeps genuine recycling outside.")),

    ("B-62", ANNEX,
     "ex 7602 Aluminium waste and scrap except post-consumer scrap",
     "",
     dict(measure_type="obligation", direction="add",
          duty="Count the embedded emissions of imported aluminium waste and scrap, other than post-consumer scrap, as a precursor in the embedded emissions of the goods produced from it.",
          addressee="Third-country operators and authorised CBAM declarants for aluminium goods produced from imported scrap",
          cls=B, trigger="aluminium waste or scrap used as an input material in producing an Annex I good",
          frequency="annual", verification="accredited third party",
          article="Art. 1(24); Annex III adding Annex VIII to Regulation (EU) 2023/956",
          when=J2028,
          drivers=["D4", "D1"], named=["alu"], reached=["auto", "build"],
          note="The aluminium twin of B-61, and the more consequential of the two: secondary aluminium is a much larger share of the trade than secondary steel.")),
]


def slice_span(text: str, start: str, end: str, rid: str) -> str:
    """Locate one span by anchors. Ambiguity and absence are both fatal."""
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


def build():
    act_full = (HERE / ACT).read_text(encoding="utf-8")
    cut = act_full.find(OPERATIVE_ANCHOR)
    if cut == -1:
        raise LookupError(
            f"operative-part anchor not found in {ACT}: {OPERATIVE_ANCHOR!r}. "
            "Refusing to match anchors against the explanatory memorandum, which "
            "paraphrases the same provisions.")
    texts = {ACT: act_full[cut:], ANNEX: (HERE / ANNEX).read_text(encoding="utf-8")}
    prior_text = (HERE / PRIOR).read_text(encoding="utf-8")

    rows, errors = [], []
    for rid, src, start, end, meta in ROWS:
        try:
            span = slice_span(texts[src], start, end, rid)
        except LookupError as exc:
            errors.append(str(exc))
            continue

        row = {
            "id": rid,
            "measure_type": meta["measure_type"],
            "addressee": meta["addressee"],
            "class": meta["cls"],
            "trigger": meta["trigger"],
            "frequency": meta["frequency"],
            "verification": meta["verification"],
            "direction": meta["direction"],
            "article": meta["article"],
            "when": meta["when"],
            "source_text": span,
            "drivers": meta["drivers"],
            "sectors_named": meta["named"],
            "sectors_reached": meta["reached"],
        }
        if meta.get("duty"):
            row["duty"] = meta["duty"]
        if meta.get("benefit"):
            row["benefit"] = meta["benefit"]
        for optional in ("right_basis", "provision_id", "pending", "note"):
            if meta.get(optional):
                row[optional] = meta[optional]

        prior = meta.get("prior")
        if prior:
            # Same discipline as the act spans: the prior text is SLICED from the
            # prior consolidation, never retyped, so a `sourced` prior_rule cannot
            # quietly become a paraphrase of the rule it claims to have read.
            try:
                prior_span = slice_span(prior_text, prior["start"], prior.get("end", ""),
                                        rid + "/prior")
            except LookupError as exc:
                errors.append(str(exc))
                continue
            row["prior_rule"] = {
                "status": "sourced",
                "trigger": prior["trigger"],
                "obligation": prior["obligation"],
                "source_document": prior["source_document"],
                "source_text": prior_span,
                "note": prior["note"],
            }

        rows.append(row)

    return rows, errors


def main():
    check_only = "--check" in sys.argv
    rows, errors = build()

    if errors:
        print(f"{len(errors)} ANCHOR FAILURES — nothing written:")
        for e in errors:
            print("  " + e)
        return 1

    counts = {}
    for r in rows:
        counts[(r["measure_type"], r["direction"])] = counts.get(
            (r["measure_type"], r["direction"]), 0) + 1
    print(f"{len(rows)} rows, all anchors resolved")
    for (mt, d), n in sorted(counts.items()):
        print(f"  {mt}/{d}: {n}")

    if check_only:
        print("--check: nothing written")
        return 0

    out = HERE / "cbam_pass_b.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

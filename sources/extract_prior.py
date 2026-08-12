import json

with open('COM2025_81.txt', encoding='utf-8') as f:
    content = f.read()

# recital-sourced prior-law descriptions: (id, start_anchor, end_anchor)
specs = [
("AUD-01", "Article 26a(3), second subparagraph, of Directive 2006/43/EC empowers the Commission to adopt standards for reasonable assurance by 1 October 2028, following an assessment of feasibility.", ""),
("RPT-01", "Article 19a(1) of Directive 2013/34/EU requires large undertakings and small and medium-sized undertakings with securities admitted to trading on an EU regulated market, excluding micro-undertakings, to prepare and publish a sustainability statement at individual level.", ""),
("RPT-02", "Article 29a(1) of Directive 2013/34/EU requires parent undertakings of large groups to prepare and publish a sustainability statement at consolidated level.", ""),
("RPT-03", "Article 19a(3) of Directive 2013/34/EU requires undertakings to report information about the undertaking’s own operations and about its value chain.", ""),
("RPT-04", "The European Financial Stability Facility (EFSF) established by the EFSF Framework Agreement is subject to the sustainability reporting requirements set out in Directive 2013/34/EU, although it is exempted from the sustainability reporting regime set out in Directive 2004/109/EC of the European Parliament and of the Council pursuant to Article 8 of that Directive.", ""),
("RPT-05", "Article 29b(1), third subparagraph, Directive 2013/34/EU empowers the Commission to adopt sector-specific reporting standards by way of delegated acts, with a first set of such standards to be adopted by 30 June 2026.", ""),
("RPT-06", "Article 29d of Directive 2013/34/EU requires undertakings subject to the requirements in Articles 19a and 29a of that Directive to prepare their management report, or consolidated management report, where applicable, in the electronic reporting format specified in Article 3 of Commission Delegated Regulation (EU) 2019/815", "and to mark up their sustainability reporting, including the disclosures provided for in Article 8 of Regulation (EU) 2020/852 of the European Parliament and of the Council, in accordance with the electronic reporting format to be specified in that Delegated Regulation."),
("RPT-07", "Article 33(1) of Directive 2013/34/EU specifies that the members of the administrative, management and supervisory bodies of an undertaking have collective responsibility for ensuring that the following documents are drawn up and published in accordance with the requirements of that Directive.", ""),
("RPT-09", "Pursuant to Article 40a(1), fourth and fifth subparagraph of Directive 2013/34/EU, a subsidiary in the Union of a third-county undertaking that generates a net turnover of more than EUR 150 million in the Union, or, in the absence of such subsidiary, a branch in the Union that generates a net turnover of more than EUR 40 million, is to publish and make accessible sustainability information at the group level of the third-country parent undertaking.", ""),
("RPT-10", "Article 1(3) of Directive 2013/34/EU specifies that credit institutions and insurance undertakings that are large undertakings or small and medium-size undertakings", "with securities admitted to trading on an EU regulated market are subject to the sustainability reporting requirements set out in that Directive, regardless of their legal form."),
("DD-02", "Article 4(1) of Directive (EU) 2024/1760 prohibits Member States from introducing, in their national law, provisions within the field covered by the Directive laying down human rights and environmental due diligence obligations diverging from those laid down in Article 8(1) and (2), and Article 10(1) of that Directive.", ""),
("DD-03", "Article 5 of Directive (EU) 2024/1760 obliges Member States to ensure that large companies above a certain size conduct risk-based human rights and environmental due diligence.", ""),
("DD-09", "paragraph (8) amends Article 15 of the CSDDD on monitoring to extend the intervals in which companies need to regularly assess the adequacy and effectiveness of due diligence measures, from 1 year to five years.", ""),
("DD-11", "the requirement to put into effect the transition plan for climate change mitigation should be replaced by a clarification that the obligation of companies to adopt a transition plan includes outlining implementing actions, planned and taken.", ""),
("PEN-00", "Article 27(4) of that Directive requires Member States to base any imposed pecuniary penalties on the net worldwide turnover of the company concerned.", ""),
("PEN-01", "Article 27(1) of Directive EU 2024/1760 requires Member States to lay down penalties that are to be", "effective, proportionate and dissuasive”."),
("PEN-02", "Article 27(2) of that Directive requires Member States, when deciding whether to impose penalties and, if so, when determining their nature and appropriate level, to take due account of a series of factors that determine the gravity of the infringement and attenuating or aggravating circumstances.", ""),
("LIA-01", "the specific, Union-wide liability regime currently provided for in Article 29(1) of that Directive should be removed", ""),
("LIA-03", "in view of the different rules and traditions that exist at national level when it comes to allowing representative action, to delete the specific requirement set out in the CSDDD in this regard", ""),
("LIA-04", "for the same reason, by deleting the requirement for Member States to ensure that the liability rules are of overriding mandatory application in cases where the law applicable to claims to that effect is not the national law of the Member State", ""),
("GOV-01", "Article 36(1) of Directive (EU) 2024/1760 requires the Commission to submit by no later than 26 July 2026 a report to the European Parliament and to the Council on the necessity of laying down additional sustainability due diligence requirements tailored to regulated financial undertakings with respect to the provision of financial services and investment activities, and the options for such due diligence requirements", "and their impacts."),
]

out = {}
errors = []
for id_, start, end in specs:
    i = content.find(start)
    if i == -1:
        errors.append((id_, "START NOT FOUND", start[:70]))
        continue
    if end:
        j = content.find(end, i)
        if j == -1:
            errors.append((id_, "END NOT FOUND", end[:70]))
            continue
        text = content[i:j+len(end)]
    else:
        text = content[i:i+len(start)]
    out[id_] = text

for id_, t in out.items():
    print(f"=== {id_} ===")
    print(t)
    print()

if errors:
    print("ERRORS:", errors)

with open('extracted_prior.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

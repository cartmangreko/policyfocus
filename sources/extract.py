import json, sys

with open('COM2025_81.txt', encoding='utf-8') as f:
    content = f.read()

# (id, start_anchor, end_anchor) -- end_anchor's end index is included in the slice
specs = [
("AUD-01", "To avoid an increase in costs of assurance for undertakings, the requirement to adopt such standards", "for reasonable assurance should be removed."),
("RPT-01", "Large undertakings which, on their balance sheet dates, exceed the average number of 1000 employees during the financial year shall include in their management report information necessary to understand the undertaking", "affect the undertaking’s development, performance and position."),
("RPT-02", "Parent undertakings of a large group which, on their balance sheet dates, exceed the average number of 1000 employees, on a consolidated basis, during the financial year, shall include in the consolidated management report", "affect the group’s development, performance and position."),
("RPT-03", "Member States shall ensure that, for the reporting of sustainability information as required by this Directive, undertakings do not seek to obtain from undertakings in their value chain which, on their balance sheet dates, do not exceed the average number of 1000 employees during the financial year", "except for additional sustainability information that is commonly shared between undertakings in the sector concerned."),
("RPT-04", "The coordination measures prescribed by Articles 19a, 29a and 29d shall not apply to the European Financial Stability Facility (EFSF) established by the EFSF Framework Agreement", "point (12), (b) and (f) of Regulation (EU) 2019/2088 of the European Parliament and of the Council*."),
("RPT-05", "in paragraph 1, the third and fourth subparagraphs are deleted", "in paragraph 4, first subparagraph, the last sentence is replaced"),
("RPT-06", "Until such rules on the marking up are adopted by way of that  Delegated Regulation, undertakings shall not be required to markup", "sustainability reporting."),
("RPT-07", "By way of derogation from subparagraph 1, Member States shall ensure that the members of the administrative, management and supervisory bodies of an undertaking, acting within the competences assigned to them by national law, do not have collective responsibility for ensuring that the management report, or consolidated management report, where applicable, is prepared in accordance with Article 29d", "."),
("RPT-08", "Member States shall ensure that the opinion referred to in paragraph 1, second subparagraph, point (aa), is prepared in full respect of the obligation on undertakings not to seek to obtain from undertakings in their value chain", "any information that exceeds the information specified in the standards for voluntary use referred to in Article 29ca, except for additional sustainability information that is commonly shared between undertakings in the sector concerned."),
("RPT-09", "The first and third subparagraphs shall only apply to the subsidiary undertakings or branches referred to in those subparagraphs where the third-country undertaking, at its group level, or, if not applicable, the individual level, generated a net turnover in the Union exceeding EUR 450\xa0000\xa0000", "for each of the last two consecutive financial years."),
("TAX-01", "Member States shall ensure that, by way of derogation from Article 8 of Regulation (EU) 2020/852, undertakings as referred to in Article 19a(1) of this Directive which, on their balance sheet dates, do not exceed a net turnover of EUR 450 000 000 during the financial year shall apply the paragraphs 2, 3 and 4", "of this Directive."),
("TAX-02", "In particular, a non-financial undertaking that claims that its activities are associated with economic activities that qualify as environmentally sustainable under Articles 3 and 9 of Regulation (EU) 2020/852 shall disclose the following indicators", "processes associated with economic activities that qualify as environmentally sustainable under Articles 3 and 9 of that Regulation."),
("STD-01", "To facilitate voluntary reporting of sustainability information by undertakings other than those referred to in Articles 19a(1) and 29a(1), the Commission shall adopt a delegated act by [4 months after entry into force of this Directive]", "to provide for sustainability reporting standards for voluntary use by such undertakings."),
("DD-01", "‘stakeholders’ means the company’s employees, the employees of its subsidiaries and of its business partners, and their trade unions and workers’ representatives, and individuals or communities whose rights or interests are or could be directly affected", "and the legitimate representatives of those individuals or communities;"),
("DD-02", "Member States shall not introduce, in their national law, provisions within the field covered by this Directive laying down human rights and environmental due diligence obligations diverging from those laid down in Articles 6 and 8, Article 10(1) to (5), Article 11(1) to (6) and Article 14.", ""),
("DD-03", "based on the results of the mapping as referred to in point (a), carry out and in-depth assessment of their own operations, those of their subsidiaries and, where related to their chains of activities, those of their direct business partners", "in the areas where adverse impacts were identified to be most likely to occur and most severe."),
("DD-04", "Where a company has plausible information that suggests that adverse impacts at the level of the operations of an indirect business partner have arisen or may arise, it shall carry out an in-depth assessment.", "Where the assessment confirms the likelihood or existence of the adverse impact, it is deemed to have been identified."),
("DD-05", "irrespective of whether plausible information is available about indirect business partners, a company shall seek contractual assurances from a direct business partner that that business partner will ensure compliance with the company’s code of conduct by establishing corresponding contractual assurances from its business partners.", ""),
("DD-06", "Member States shall ensure that, for the mapping provided for in paragraph 2, point (a), companies do not seek to obtain information from direct business partners with fewer than 500 employees that exceeds the information specified in the standards for voluntary use referred to in Article 29a of Directive 2013/34/EU.", ""),
("DD-07", "the company shall, as a last resort:\n(a)\trefrain from entering into new, or extending existing, relations with a business partner in connection with which, or in the chain of activities of which, the impact has arisen", "(c)\tuse or increase its leverage through the suspension of the business relationship with respect to the activities concerned."),
("DD-08", "Consultation of relevant stakeholders shall take place at the following stages of the due diligence process:", ""),
("DD-09", "Such assessments shall be based, where appropriate, on qualitative and quantitative indicators and be carried out without undue delay after a significant change occurs, but at least every 5 years", "or that new risks of the occurrence of those adverse impacts may arise."),
("DD-10", "The guidelines referred to in paragraph 2, point (a), shall be made available by 26 July 2026, those referred to in paragraph 2, points (d) and (e), by 26 January 2027, and those referred to in paragraph 2, points (b), (f) and (g), by 26 July 2027.", ""),
("DD-11", "Member States shall ensure that companies referred to in Article 2(1), points (a), (b) and (c), and Article 2(2), points (a), (b) and (c), adopt a transition plan for climate change mitigation, including implementing actions, which aim to ensure, through best efforts,", "and where relevant, the exposure of the company to coal-, oil- and gas-related activities."),
("PEN-01", "The Commission, in collaboration with Member States, shall issue guidance to assist supervisory authorities in determining the level of penalties in accordance with this Article.", ""),
("PEN-02", "Member States shall not set a maximum limit of pecuniary penalties in their national law transposing this Directive that would prevent supervisory authorities from imposing penalties in accordance with the principles and factors set out in paragraphs 1 and 2.", ""),
("LIA-01", "Article 29 is amended as follows:\nparagraph 1 is deleted", ""),
("LIA-02", "Where a company is held liable pursuant to national law for damage caused to a natural or legal person by a failure to comply with the due diligence requirements under this Directive, Member States shall ensure that those persons have a right to full compensation.", "Full compensation shall not lead to overcompensation, whether by means of punitive, multiple or other types of damages."),
("LIA-03", "in paragraph 3, point (d) is deleted", ""),
("LIA-04", "paragraph 7 is deleted", ""),
("LIA-05", "The civil liability of a company for damages as referred to in this Article shall be without prejudice to the civil liability of its subsidiaries or of any direct and indirect business partners in the chain of activities of the company.", ""),
("RPT-10", "The coordination measures prescribed by Articles 19a, 19b, 29a, 29aa, 29d, 30 and 33, Article 34(1), second subparagraph, point (aa), Article 34(2) and (3), and Article 51 of this Directive shall also apply", "exceed the average number of 1000 employees  during the financial year:"),
("PEN-00", "the need to base pecuniary penalties on the net worldwide turnover of the company concerned is superfluous.", ""),
("GOV-01", "in Article 36, paragraph 1 is deleted.", ""),
("GOV-02", "Member States shall bring into force the laws, regulations and administrative provisions necessary to comply with this Directive by [12 months after entry into force] at the latest.", "They shall forthwith communicate to the Commission the text of those provisions."),
]

out = {}
errors = []
for id_, start, end in specs:
    i = content.find(start)
    if i == -1:
        errors.append((id_, "START NOT FOUND", start[:60]))
        continue
    count = content.count(start)
    if end:
        j = content.find(end, i)
        if j == -1:
            errors.append((id_, "END NOT FOUND", end[:60]))
            continue
        text = content[i:j+len(end)]
    else:
        text = content[i:i+len(start)]
    out[id_] = {"text": text, "start_count": count, "start_idx": i}

for id_, d in out.items():
    flag = "  <<< DUPLICATE START" if d["start_count"] > 1 else ""
    print(f"=== {id_} (idx {d['start_idx']}){flag} ===")
    print(d["text"])
    print()

if errors:
    print("ERRORS:")
    for e in errors:
        print(e)

with open('extracted.json', 'w', encoding='utf-8') as f:
    json.dump({k: v["text"] for k, v in out.items()}, f, ensure_ascii=False, indent=2)

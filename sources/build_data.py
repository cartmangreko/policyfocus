import json, re, sys

with open('extracted.json', encoding='utf-8') as f:
    SRC = json.load(f)

with open('COM2025_81.txt', encoding='utf-8') as f:
    FULLTEXT = f.read()

FILE_SLUG = "omnibus"
SOURCE_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52025PC0081"
WAVE_NOTE = "Once transposed by Member States (transposition due within 12 months of this Directive's entry into force)"

# each row: id, duty, addressee, class, trigger, frequency, verification, direction, article, when, drivers, burden, pending(optional)
ROWS = [
dict(id="AUD-01", duty="No longer required to adopt delegated-act standards for 'reasonable assurance' of sustainability reporting by 1 October 2028",
     addressee="European Commission", cls="commission", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 1(1), replacing Art. 26a(3) of Directive 2006/43/EC", when="On entry into force",
     drivers=[], burden="Relief",
     pending="The limited-assurance standards themselves remain to be adopted by the Commission via delegated act, now with no fixed deadline."),

dict(id="RPT-01", duty="Include in the management report information necessary to understand the undertaking's sustainability impacts and how sustainability matters affect its development, performance and position",
     addressee="Large undertakings that exceed 1000 employees on average during the financial year", cls="business",
     trigger="More than 1000 employees on average during the financial year (large-undertaking criteria under Art. 3(4))",
     freq="annual", verification="accredited third party",
     direction="rem", article="Art. 2(2), amending Art. 19a(1) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=["D5"], burden="Relief"),

dict(id="RPT-02", duty="Include in the consolidated management report information necessary to understand the group's sustainability impacts and how sustainability matters affect its development, performance and position",
     addressee="Parent undertakings of a large group that exceed 1000 employees on average, on a consolidated basis", cls="business",
     trigger="More than 1000 employees on average, on a consolidated basis, during the financial year",
     freq="annual", verification="accredited third party",
     direction="rem", article="Art. 2(4), amending Art. 29a(1) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=["D5"], burden="Relief"),

dict(id="RPT-03", duty="Do not seek from value-chain undertakings with 1000 or fewer employees any sustainability information beyond the voluntary reporting standard, except sustainability information commonly shared sector-wide",
     addressee="Large undertakings preparing individual or consolidated sustainability statements", cls="business",
     trigger="Value-chain counterparty does not exceed 1000 employees on average during the financial year",
     freq="annual", verification="none",
     direction="add", article="Art. 2(2) and 2(4), amending Art. 19a(3) and Art. 29a(3) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Low",
     pending="The cap's ceiling is set by the voluntary reporting standard the Commission is due to adopt by delegated act under the new Art. 29ca."),

dict(id="RPT-04", duty="Exempted from individual sustainability reporting, consolidated sustainability reporting and single-electronic-format/markup duties",
     addressee="The European Financial Stability Facility (EFSF) and financial products under Art. 2, point (12)(b) and (f) of Regulation (EU) 2019/2088", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 2(1), replacing Art. 1(4) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="RPT-05", duty="Commission's empowerment to adopt sector-specific sustainability reporting standards by delegated act is removed (no sector-specific ESRS will be developed)",
     addressee="European Commission", cls="commission", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 2(6), amending Art. 29b(1) of Directive 2013/34/EU", when="On entry into force",
     drivers=[], burden="Relief"),

dict(id="RPT-06", duty="Not required to mark up (digitally tag) sustainability reporting until the Commission adopts a Delegated Regulation specifying the markup format",
     addressee="Undertakings subject to Art. 19a and Art. 29a sustainability reporting", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 2(9), replacing Art. 29d of Directive 2013/34/EU", when="Until the Delegated Regulation on markup is adopted",
     drivers=[], burden="Relief",
     pending="Depends on the Commission adopting a Delegated Regulation specifying the digital markup / taxonomy format."),

dict(id="RPT-07", duty="Collective responsibility of administrative, management and supervisory body members for the management report's digitalisation is limited to ensuring its publication in the single electronic format",
     addressee="Members of an undertaking's administrative, management and supervisory bodies", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 2(10), replacing Art. 33(1) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="RPT-08", duty="Prepare the sustainability assurance opinion in full respect of the obligation not to seek excess value-chain information from undertakings with 1000 or fewer employees",
     addressee="Statutory auditors and assurance providers verifying sustainability reporting", cls="business",
     trigger="n/a", freq="annual", verification="accredited third party",
     direction="add", article="Art. 2(11), inserting Art. 34(2a) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=["D2"], burden="Low",
     pending="Depends on the voluntary reporting standard the Commission is due to adopt under Art. 29ca."),

dict(id="RPT-09", duty="Third-country group sustainability reporting duty on EU subsidiaries/branches now applies only above raised turnover thresholds",
     addressee="EU subsidiaries and branches of third-country undertakings", cls="business",
     trigger="Third-country parent's net turnover in the Union exceeding EUR 450 000 000 for each of the last two consecutive financial years (raised from EUR 150 000 000); branch threshold raised from EUR 40 000 000 to EUR 50 000 000",
     freq="annual", verification="none",
     direction="rem", article="Art. 2(12), amending Art. 40a(1) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="TAX-01", duty="Eligible to use a more flexible opt-in Taxonomy disclosure regime instead of full Article 8 Taxonomy Regulation reporting",
     addressee="Large undertakings (over 1000 employees) with net turnover not exceeding EUR 450 000 000", cls="business",
     trigger="Net turnover not exceeding EUR 450 000 000 during the financial year (or on a consolidated basis for parent undertakings)",
     freq="annual", verification="none",
     direction="rem", article="Art. 2(3) and 2(5), inserting Art. 19b(1) and Art. 29aa(1) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="TAX-02", duty="Disclose the proportion of turnover and capital expenditure associated with Taxonomy-aligned (or partially-aligned) economic activities, if claiming alignment; operating-expenditure disclosure is optional",
     addressee="Large undertakings under the opt-in Taxonomy regime that claim Taxonomy-aligned or partially-aligned activities", cls="business",
     trigger="Claims that activities are associated with environmentally sustainable, or partially-aligned, economic activities under Regulation (EU) 2020/852",
     freq="annual", verification="accredited third party",
     direction="add", article="Art. 2(3) and 2(5), inserting Art. 19b(2)-(4) and Art. 29aa(2)-(4) of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=["D1"], burden="Low",
     pending="The content, presentation and methodology for partial-alignment reporting are to be specified by Commission delegated act under Art. 49."),

dict(id="STD-01", duty="Adopt a delegated act providing sustainability reporting standards for voluntary use by out-of-scope (under 1000 employee) undertakings",
     addressee="European Commission", cls="commission", trigger="n/a", freq="one-off", verification="none",
     direction="add", article="Art. 2(8), inserting Art. 29ca of Directive 2013/34/EU", when="By 4 months after entry into force of this Directive",
     drivers=["D1"], burden="Low"),

dict(id="DD-01", duty="Definition of 'stakeholders' who must be consulted is narrowed to workers/their representatives and individuals or communities directly affected by the company's, its subsidiaries', or its business partners' products, services and operations",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(2), replacing Art. 3(1)(n) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="DD-02", duty="Do not introduce national due-diligence rules that diverge from Articles 6, 8, 10(1)-(5), 11(1)-(6) and 14 of the Directive",
     addressee="Member States", cls="state", trigger="n/a", freq="n/a", verification="none",
     direction="add", article="Art. 4(3), replacing Art. 4 of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Medium"),

dict(id="DD-03", duty="Limit the in-depth impact assessment, as a general rule, to your own operations, your subsidiaries and your direct business partners",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="event-driven", verification="none",
     direction="rem", article="Art. 4(4), replacing Art. 8(2)(b) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="DD-04", duty="Carry out an in-depth assessment of an indirect business partner where plausible information suggests an adverse impact there, or where an indirect structure is used to circumvent the direct-partner-only rule",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="Plausible information suggesting an adverse impact at an indirect business-partner level, or an artificial arrangement circumventing the direct-partner assessment rule",
     freq="event-driven", verification="none",
     direction="add", article="Art. 4(4), inserting Art. 8(2a) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=["D1"], burden="Low"),

dict(id="DD-05", duty="Seek contractual assurances from direct business partners that they will cascade the company's code of conduct to their own business partners",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="event-driven", verification="none",
     direction="add", article="Art. 4(4), inserting Art. 8(2a), third subparagraph of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=["D1"], burden="Low"),

dict(id="DD-06", duty="Do not seek more information than the voluntary standard from direct business partners with fewer than 500 employees when mapping the chain of activities, unless additional information is necessary and cannot reasonably be obtained elsewhere",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="add", article="Art. 4(4), inserting Art. 8(5) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Low",
     pending="The cap's ceiling is set by the voluntary reporting standard referred to in Art. 29a of Directive 2013/34/EU."),

dict(id="DD-07", duty="Suspend (rather than terminate) the business relationship as a last resort where adverse impacts cannot be prevented or mitigated, after assessing that suspension is not manifestly more harmful, with reasonable notice to the business partner",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="Adverse impacts that could not be prevented or adequately mitigated by other measures",
     freq="event-driven", verification="none",
     direction="rem", article="Art. 4(5) and 4(6), replacing Art. 10(6) and Art. 11(7) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="DD-08", duty="Consult relevant stakeholders only at the specified stages of the due diligence process (two previously-listed stages removed)",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="event-driven", verification="none",
     direction="rem", article="Art. 4(7), amending Art. 13(3) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="DD-09", duty="Reassess whether due-diligence measures remain adequate and effective at least every 5 years, or ad hoc after a significant change or reasonable grounds for doubt",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="At least every 5 years, or ad hoc when triggered", verification="none",
     direction="rem", article="Art. 4(8), amending Art. 15 of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=["D5"], burden="Relief"),

dict(id="DD-10", duty="Make available the general due-diligence guidelines, in three phased sets",
     addressee="European Commission", cls="commission", trigger="n/a", freq="one-off, in three phases", verification="none",
     direction="add", article="Art. 4(9), replacing Art. 19(3) of Directive (EU) 2024/1760", when="By 26 July 2026, 26 January 2027 and 26 July 2027",
     drivers=["D1"], burden="Low"),

dict(id="DD-11", duty="Adopt a transition plan for climate change mitigation, including implementing actions planned and taken, aimed at aligning the business model and strategy with the 1.5 degC pathway and EU climate-neutrality targets",
     addressee="Companies referred to in Art. 2(1)(a)-(c) and Art. 2(2)(a)-(c) of Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="Ongoing, updated periodically", verification="competent authority",
     direction="rem", article="Art. 4(10), replacing Art. 22(1) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="PEN-01", duty="Issue guidance, jointly with Member States, to help supervisory authorities determine penalty levels",
     addressee="European Commission", cls="commission", trigger="n/a", freq="n/a", verification="none",
     direction="add", article="Art. 4(11), replacing Art. 27(4) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Low"),

dict(id="PEN-02", duty="Do not set a maximum limit on pecuniary penalties in national law that would prevent supervisory authorities imposing penalties in line with Art. 27(1)-(2)",
     addressee="Member States", cls="state", trigger="n/a", freq="n/a", verification="none",
     direction="add", article="Art. 4(11), replacing Art. 27(4) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=["D6"], burden="Medium"),

dict(id="LIA-01", duty="EU-wide harmonised civil liability regime for due-diligence failures is removed from the Directive",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(12), deleting Art. 29(1) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="LIA-02", duty="Ensure that persons harmed by a company's due-diligence failure have a right to full compensation, without overcompensation",
     addressee="Member States", cls="state", trigger="n/a", freq="If it happens", verification="none",
     direction="add", article="Art. 4(12), replacing Art. 29(2) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=["D6"], burden="Medium"),

dict(id="LIA-03", duty="Specific requirement to provide for representative actions on behalf of injured parties is deleted",
     addressee="Member States", cls="state", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(12), deleting Art. 29(3), point (d) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="LIA-04", duty="Requirement that liability rules be of overriding mandatory application, where the applicable law is not a Member State's own law, is deleted",
     addressee="Member States", cls="state", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(12), deleting Art. 29(7) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="LIA-05", duty="A company's civil liability for due-diligence damages is expressly without prejudice to the separate civil liability of its subsidiaries or of its direct and indirect business partners",
     addressee="Companies subject to due diligence duties under Directive (EU) 2024/1760", cls="business",
     trigger="n/a", freq="n/a", verification="none",
     direction="add", article="Art. 4(12), replacing Art. 29(5), first subparagraph of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Low"),

dict(id="RPT-10", duty="Sustainability-reporting coordination measures apply to credit institutions and insurance undertakings only once they exceed 1000 employees on average (previously also caught smaller large undertakings and listed SMEs in these categories)",
     addressee="Credit institutions and insurance undertakings", cls="business",
     trigger="More than 1000 employees on average during the financial year",
     freq="annual", verification="none",
     direction="rem", article="Art. 2(1), replacing Art. 1(3) introductory wording of Directive 2013/34/EU", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="PEN-00", duty="Requirement to base pecuniary penalties on a company's net worldwide turnover, and the former minimum turnover-based cap floor, is removed",
     addressee="Member States", cls="state", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(11), replacing Art. 27(4) of Directive (EU) 2024/1760", when=WAVE_NOTE,
     drivers=[], burden="Relief"),

dict(id="GOV-01", duty="Obligation to report by 26 July 2026 on the need for due-diligence rules tailored to financial services is deleted",
     addressee="European Commission", cls="commission", trigger="n/a", freq="n/a", verification="none",
     direction="rem", article="Art. 4(13), deleting Art. 36(1) of Directive (EU) 2024/1760", when="On entry into force",
     drivers=[], burden="Relief"),

dict(id="GOV-02", duty="Bring into force the laws, regulations and administrative provisions necessary to comply with this Directive, and communicate the text to the Commission",
     addressee="Member States", cls="state", trigger="n/a", freq="one-off", verification="none",
     direction="add", article="Art. 5", when="By [12 months after entry into force]",
     drivers=["D1"], burden="Low"),
]

assert len(ROWS) == len(SRC), f"row/src mismatch {len(ROWS)} vs {len(SRC)}"

out = []
for r in ROWS:
    rid = r["id"]
    rec = {
        "id": rid,
        "file": FILE_SLUG,
        "duty": r["duty"],
        "addressee": r["addressee"],
        "class": r["cls"],
        "trigger": r["trigger"],
        "frequency": r["freq"],
        "verification": r["verification"],
        "direction": r["direction"],
        "article": r["article"],
        "when": r["when"],
        "source_text": SRC[rid],
        "source_url": SOURCE_URL,
        "drivers": r["drivers"],
        "burden": r["burden"],
        "sectors_named": [],
        "sectors_reached": [],
    }
    if "pending" in r:
        rec["pending"] = r["pending"]
    out.append(rec)

with open('../data/omnibus.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# ---- mechanical validation ----
print(f"Total rows: {len(out)}")
fail = []
for rec in out:
    # 1. verbatim check
    if rec["source_text"] not in FULLTEXT:
        fail.append((rec["id"], "VERBATIM_FAIL"))
    # 4. driver sanity
    if rec["direction"] == "rem" and rec["burden"] != "Relief":
        fail.append((rec["id"], "REM_NOT_RELIEF"))
    if "D7" in rec["drivers"] and rec["burden"] != "High":
        fail.append((rec["id"], "D7_NOT_HIGH"))
    if rec["direction"] == "add":
        d = rec["drivers"]
        should_high = ("D7" in d) or ("D3" in d and "D6" in d) or (len(d) >= 3)
        if should_high and rec["burden"] != "High":
            fail.append((rec["id"], f"ADD_SHOULD_BE_HIGH drivers={d}"))

if fail:
    print("VALIDATION FAILURES:")
    for f_ in fail:
        print(" ", f_)
else:
    print("All mechanical checks passed (verbatim, driver sanity).")

from collections import Counter
print("\nBy direction:", Counter(r["direction"] for r in out))
print("By class:", Counter(r["class"] for r in out))
print("By burden:", Counter(r["burden"] for r in out))

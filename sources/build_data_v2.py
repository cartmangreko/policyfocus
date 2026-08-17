import json

from textnorm import canonical

with open('../data/omnibus.json', encoding='utf-8') as f:
    rows = json.load(f)
with open('extracted_prior.json', encoding='utf-8') as f:
    PRIOR_SRC = json.load(f)
# The proposal is where a row's own source_text and most prior rules live.
# Taxonomy_2020_852.txt is here because two prior rules (TAX-01, TAX-02) are
# quoted from the act being amended rather than from this proposal's recitals.
# It has to be in the corpus the verbatim re-check runs against, or those two
# spans would be emitted as "sourced" without anything ever checking them.
with open('COM2025_81.txt', encoding='utf-8') as f:
    FULLTEXT = f.read()
with open('Taxonomy_2020_852.txt', encoding='utf-8') as f:
    FULLTEXT += "\n" + f.read()

by_id = {r['id']: r for r in rows}

NATURE_TO_WEIGHT = {
    "exemption": "Relief",
    "reduction": "Relief",
    "new_obligation": "Burden",
    "extension": "Burden",
    "unchanged": "Neutral",
}

# per-row: nature, affected_delta, prior_rule override (trigger/obligation/note), new_rule override (optional)
META = {
"AUD-01": dict(nature="exemption",
    prior_trigger="n/a — a Commission rulemaking empowerment, not an undertaking-facing trigger",
    prior_obligation="Commission empowered/required to work toward reasonable-assurance standards (upgrading from limited assurance) by 1 October 2028, following a feasibility assessment",
    affected_delta="No undertaking population changes hands directly — this exempts the Commission from a future rulemaking duty, forestalling a heavier assurance regime that would otherwise have eventually reached all reporting undertakings and their auditors."),
"RPT-01": dict(nature="exemption",
    prior_trigger="Large undertaking under Art. 3(4) of Directive 2013/34/EU (commonly summarised as exceeding 2 of 3: >250 employees / turnover >EUR 50m / balance sheet >EUR 25m, though this proposal's own text does not restate those figures) or an SME with securities on an EU regulated market",
    prior_obligation=None,  # filled from recital
    affected_delta="Large undertakings between the old size test and 1000 employees, and all listed SMEs, lose the individual sustainability-reporting duty entirely."),
"RPT-02": dict(nature="exemption", prior_trigger="Parent undertaking of a large group under Art. 3(4)-(7) of Directive 2013/34/EU (no employee/turnover figure restated in this proposal's own text)",
    prior_obligation=None,
    affected_delta="Parent undertakings of large groups below 1000 employees on a consolidated basis lose the consolidated sustainability-reporting duty entirely."),
"RPT-03": dict(nature="new_obligation",
    prior_trigger="n/a — no predecessor cap existed",
    prior_obligation=None,
    affected_delta="Large reporting undertakings gain a new restriction on what they may demand from value-chain counterparties with 1000 or fewer employees; those smaller counterparties correspondingly gain protection from open-ended information requests."),
"RPT-04": dict(nature="exemption", prior_trigger="n/a — EFSF and the named SFDR financial products were previously in scope by default", prior_obligation=None,
    affected_delta="The EFSF and the two named categories of SFDR financial products lose all Accounting-Directive sustainability-reporting duties."),
"RPT-05": dict(nature="exemption", prior_trigger="n/a — Commission rulemaking empowerment", prior_obligation=None,
    affected_delta="No sector-specific ESRS will now be adopted; every undertaking that would eventually have faced a sector-specific reporting layer on top of the general ESRS is relieved of that future duty."),
"RPT-06": dict(nature="exemption", prior_trigger="Undertakings subject to Art. 19a/29a reporting, pending the digital taxonomy", prior_obligation=None,
    affected_delta="All undertakings subject to Art. 19a/29a reporting are relieved of the markup duty until the Commission separately adopts the markup Delegated Regulation — this merely restates the existing de facto position, since that Regulation was never adopted, but now says so on the face of the Directive."),
"RPT-07": dict(nature="reduction", prior_trigger="n/a — same population, narrower liability", prior_obligation=None,
    affected_delta="Administrative, management and supervisory body members keep collective responsibility for the substantive report, but are carved out from responsibility for digital-format (Art. 29d) compliance specifically."),
"RPT-08": dict(nature="new_obligation", prior_trigger="n/a — no predecessor provision", prior_obligation=None,
    affected_delta="Statutory auditors and assurance providers gain a new constraint on how they must frame their limited-assurance opinion."),
"RPT-09": dict(nature="exemption", prior_trigger="Third-country parent turnover in the Union > EUR 150 000 000 (subsidiary route) or EU branch turnover > EUR 40 000 000 (branch route)", prior_obligation=None,
    affected_delta="Third-country groups whose EU turnover sits between the old (EUR 150m parent / EUR 40m branch) and new (EUR 450m parent / EUR 50m branch) thresholds lose the group-level sustainability-disclosure duty entirely."),
"RPT-10": dict(nature="exemption", prior_trigger="Credit institution or insurance undertaking that is a large undertaking, or an SME with securities on an EU regulated market", prior_obligation=None,
    affected_delta="Credit institutions and insurance undertakings below 1000 employees (previously caught via the broader large-undertaking/listed-SME test) lose the sustainability-reporting duty entirely."),
# TAX-01/TAX-02: prior rule sourced from the Taxonomy Regulation itself, not
# from this proposal's recitals. Resolved in 21d6c23, which added
# Taxonomy_2020_852.txt and edited data/omnibus.json directly without updating
# this table -- so the builder regenerated them as "unresolved" and silently
# undid the resolution. The spans below are verified against that file by the
# verbatim re-check, same as every other span here.
"TAX-01": dict(nature="exemption",
    prior_trigger="Any undertaking subject to Art. 19a or 29a of Directive 2013/34/EU non-financial reporting, regardless of size or turnover",
    prior_obligation="Full mandatory Article 8 Taxonomy Regulation disclosure applied to every undertaking in scope of Art. 19a/29a — no turnover-based opt-in or flexibility existed.",
    prior_status="sourced",
    prior_source_text="Any undertaking which is subject to an obligation to publish non-financial information pursuant to Article 19a or Article 29a of Directive 2013/34/EU shall include in its non-financial statement or consolidated non-financial statement information on how and to what extent the undertaking’s activities are associated with economic activities that qualify as environmentally sustainable under Articles 3 and 9 of this Regulation.",
    prior_source_document="Regulation (EU) 2020/852, Article 8 (as in force, unaffected by this Omnibus)",
    affected_delta="Large undertakings with turnover not exceeding EUR 450 000 000 gain an opt-in, lighter Taxonomy disclosure track instead of full Article 8 reporting."),
"TAX-02": dict(nature="new_obligation",
    prior_trigger="Any undertaking subject to Art. 19a or 29a of Directive 2013/34/EU non-financial reporting",
    prior_obligation="Mandatory disclosure of turnover AND capital expenditure AND operating expenditure proportions (all three, not turnover/CapEx with OpEx optional) associated with Taxonomy-aligned activities.",
    prior_status="sourced",
    prior_source_text="In particular, non-financial undertakings shall disclose the following: (a) the proportion of their turnover derived from products or services associated with economic activities that qualify as environmentally sustainable under Articles 3 and 9; and (b) the proportion of their capital expenditure and the proportion of their operating expenditure related to assets or processes associated with economic activities that qualify as environmentally sustainable under Articles 3 and 9.",
    prior_source_document="Regulation (EU) 2020/852, Article 8 (as in force, unaffected by this Omnibus)",
    affected_delta="Undertakings using the opt-in track that claim Taxonomy alignment must still disclose turnover/CapEx KPIs (OpEx optional) — a lighter but real, newly-conditioned duty replacing the old blanket Article 8 duty."),
"STD-01": dict(nature="new_obligation", prior_trigger="n/a", prior_obligation=None,
    affected_delta="The European Commission gains a new delegated-act drafting duty; out-of-scope undertakings gain access to a voluntary reporting standard that did not exist before."),
"DD-01": dict(nature="reduction", prior_trigger="n/a — same addressee population, narrower consultation pool", prior_obligation=None, prior_status="unresolved",
    prior_note="The recitals present the new, narrower definition without restating the prior wording of Art. 3(1)(n) verbatim.",
    affected_delta="Companies' mandatory-engagement pool shrinks to those directly affected; individuals or communities only indirectly affected, and broader civil-society representatives, drop out of the mandatory-consultation population."),
"DD-02": dict(nature="extension", prior_trigger="n/a — Member States, narrower prohibition", prior_obligation=None,
    affected_delta="Member States' freedom to gold-plate national due-diligence rules narrows further across a much wider set of core provisions (Arts. 6, 8, 10(1)-(5), 11(1)-(6), 14 — up from just Art. 8(1)-(2) and Art. 10(1))."),
"DD-03": dict(nature="reduction", prior_trigger="n/a — general risk-based due diligence duty, not explicitly tiered to direct/indirect partners", prior_obligation=None, prior_status="unresolved",
    prior_note="The recital describes the general due-diligence duty in Art. 5 as context; it does not restate the pre-amendment wording of Art. 8(2)(b) specifically.",
    affected_delta="The mandatory in-depth-assessment population narrows from potentially the whole chain of activities to, as a general rule, direct business partners only — indirect partners drop out of the default duty (though a conditional duty to reach them survives via new Art. 8(2a), see DD-04)."),
"DD-04": dict(nature="extension", prior_trigger="n/a — newly-inserted conditional trigger", prior_obligation=None,
    affected_delta="Companies must still reach indirect business partners, but now only when specific trigger conditions (plausible information, or circumvention) are met — narrower than a blanket chain-wide duty, but a real, newly-codified conditional obligation."),
"DD-05": dict(nature="new_obligation", prior_trigger="n/a — no predecessor provision", prior_obligation=None,
    affected_delta="Companies gain a new, standing duty to seek contractual cascading assurances from direct business partners, regardless of whether any plausible-information trigger exists."),
"DD-06": dict(nature="new_obligation", prior_trigger="n/a — no predecessor cap existed", prior_obligation=None,
    affected_delta="Direct business partners with fewer than 500 employees gain protection from open-ended mapping-stage information requests; large companies gain a corresponding new restriction on what they may request from them."),
"DD-07": dict(nature="reduction", prior_trigger="n/a — same population, softer last-resort measure", prior_obligation="As a last resort, the company was required to terminate the business relationship for unaddressed adverse impacts, not merely suspend it.", prior_status="unresolved",
    prior_note="This is the well-established substance of Directive (EU) 2024/1760 as adopted, but is not restated as a clean quotable sentence in this proposal's own recitals.",
    affected_delta="Companies' last-resort escalation duty softens from termination to suspension (with an exemption where suspension would itself be manifestly more harmful)."),
"DD-08": dict(nature="reduction", prior_trigger="n/a — same population, fewer mandatory stages", prior_obligation=None, prior_status="unresolved",
    prior_note="The full original stage list (points (a) through (g)) is not restated in this proposal's recitals.",
    affected_delta="The set of due-diligence process stages that trigger mandatory stakeholder consultation shrinks by two (points (c) and (e) of the list are dropped)."),
"DD-09": dict(nature="reduction", prior_trigger="At least every 1 year", prior_obligation=None,
    affected_delta="Companies' periodic due-diligence-effectiveness reassessment burden drops from an annual to a five-yearly cycle (with ad hoc reassessment still required when triggered)."),
"DD-10": dict(nature="extension", prior_trigger="n/a — Commission, earlier deadline for the same underlying guideline duty", prior_obligation=None, prior_status="unresolved",
    prior_note="The original Art. 19(3) deadline is not restated in this proposal's recitals.",
    affected_delta="No population change on the company side — the Commission's own publication deadline moves earlier, shortening the runway in-scope companies get to digest the guidance before their due-diligence obligations bite."),
"DD-11": dict(nature="reduction", prior_trigger="n/a — same population, softer operational bar", prior_obligation=None,
    affected_delta="Companies required to adopt a transition plan keep that duty, but the operational bar drops from 'putting it into effect' to including planned/taken implementing actions on a best-efforts basis."),
"PEN-00": dict(nature="exemption", prior_trigger="n/a — Member States", prior_obligation=None,
    affected_delta="Member States (and, downstream, companies facing penalties) are relieved of the turnover-based penalty-calibration requirement and the associated minimum-cap floor."),
"PEN-01": dict(nature="new_obligation", prior_trigger="n/a — no predecessor Commission task", prior_obligation=None,
    affected_delta="The European Commission gains a new penalty-guidance-issuing duty, layered onto Member States' pre-existing duty to lay down effective, proportionate and dissuasive penalties."),
"PEN-02": dict(nature="new_obligation", prior_trigger="n/a — no predecessor prohibition", prior_obligation=None,
    affected_delta="Member States gain a new binding floor under national penalty caps; companies facing enforcement in Member States that previously set low caps may face steeper penalties."),
"LIA-01": dict(nature="exemption", prior_trigger="n/a — companies and injured parties", prior_obligation=None,
    affected_delta="Companies (and the counterparties who could have sued under the EU-wide regime) lose the Directive's own harmonised civil-liability cause of action; liability for due-diligence failures now depends entirely on national law."),
"LIA-02": dict(nature="extension", prior_trigger="n/a — same right, new limiting clause", prior_obligation="A right to full compensation for due-diligence-failure damage already existed under the prior Art. 29(2).", prior_status="unresolved",
    prior_note="The pre-amendment wording of Art. 29(2) is not restated in this proposal's recitals; its prior existence is inferred from the enacting text using 'replaced' rather than 'inserted'.",
    affected_delta="Claimants keep the right to full compensation for proven due-diligence-failure damage, but recoverable damages are now expressly capped against punitive or multiple-damages awards."),
"LIA-03": dict(nature="exemption", prior_trigger="n/a — Member States", prior_obligation=None,
    affected_delta="The specific EU-mandated duty on Member States to enable representative actions on behalf of injured parties is removed (national law on representative actions still applies wherever it independently allows this)."),
"LIA-04": dict(nature="exemption", prior_trigger="n/a — Member States", prior_obligation=None,
    affected_delta="Member States lose the EU-mandated requirement to make their liability-implementing rules an overriding mandatory provision under conflict-of-laws rules."),
"LIA-05": dict(nature="extension", prior_trigger="n/a — same population, new express clause", prior_obligation=None, prior_status="unresolved",
    prior_note="Paragraph 5's first subparagraph is 'replaced', implying a predecessor existed, but its exact wording is not restated in this proposal's recitals.",
    affected_delta="No population change — clarifies that a company's own civil liability does not shield its subsidiaries or business partners from their own separate liability."),
"GOV-01": dict(nature="exemption", prior_trigger="n/a — European Commission", prior_obligation=None,
    affected_delta="The Commission is relieved of a scheduled review-and-report duty on financial-sector-specific due-diligence rules; regulated financial undertakings lose the (indirect) prospect of a tailored regime being actively reconsidered on that timeline."),
"GOV-02": dict(nature="new_obligation", prior_trigger="n/a — no predecessor, this directive is itself the new instrument", prior_obligation=None,
    affected_delta="Member States gain the standard transposition duty inherent to any new amending directive."),
}

assert set(META.keys()) == set(by_id.keys()), f"mismatch: {set(META.keys()) ^ set(by_id.keys())}"

out = []
mismatches = []
for r in rows:
    m = META[r['id']]
    nature = m['nature']
    derived_weight = NATURE_TO_WEIGHT[nature]
    old_burden = r['burden']
    old_is_relief = old_burden == "Relief"
    old_is_burden = old_burden in ("High", "Medium", "Low")
    if derived_weight == "Relief" and not old_is_relief:
        mismatches.append((r['id'], old_burden, derived_weight))
    if derived_weight == "Burden" and not old_is_burden:
        mismatches.append((r['id'], old_burden, derived_weight))

    # A prior rule normally comes from this proposal's own recitals, via
    # extracted_prior.json. A META override supplies the ones that live in the
    # amended act instead -- the Taxonomy Regulation for TAX-01/TAX-02 -- which
    # extracted_prior.json cannot carry, since it is keyed to this proposal.
    prior_source_text = m.get('prior_source_text') or PRIOR_SRC.get(r['id'])
    prior_status = m.get('prior_status')
    if prior_source_text and not prior_status:
        prior_status = "recital"  # verbatim quote from this proposal's own recital describing pre-amendment law
    elif not prior_source_text and not prior_status:
        prior_status = "unresolved"

    if nature == "new_obligation" and prior_source_text is None and m.get('prior_obligation') is None and not m.get('prior_note'):
        prior_rule = None  # genuinely new, no predecessor -- per spec, null is correct here
    else:
        prior_rule = {
            "trigger": m['prior_trigger'],
            "obligation": m['prior_obligation'] if m['prior_obligation'] else (prior_source_text if prior_source_text else None),
            "source_text": prior_source_text,
            "status": prior_status,
        }
        if m.get('prior_source_document'):
            # Names the act the span was taken from, when that is not this
            # proposal. Without it a reader has no way to tell that a "sourced"
            # prior rule was quoted from a different instrument.
            prior_rule["source_document"] = m['prior_source_document']
        if m.get('prior_note'):
            prior_rule["note"] = m['prior_note']

    new_rule = {
        "trigger": r['trigger'],
        "obligation": r['duty'],
    }

    rec = dict(r)  # keep all existing fields (id, file, duty, addressee, class, trigger, frequency,
                   # verification, article, when, source_text, source_url, drivers, sectors_named, sectors_reached, pending)
    rec["nature"] = nature
    rec["new_rule"] = new_rule
    rec["prior_rule"] = prior_rule
    rec["affected_delta"] = m["affected_delta"]
    rec["weight"] = derived_weight          # derived — replaces independently-stored burden as ground truth
    rec["weight_intensity"] = old_burden if old_burden != "Relief" else None  # keep granularity where it existed
    # direction retained for tag rendering, now derived from nature
    rec["direction"] = "add" if nature in ("new_obligation", "extension") else ("rem" if nature in ("exemption", "reduction") else "n/a")
    out.append(rec)

print(f"Total rows: {len(out)}")
print(f"Weight/nature mismatches (stored vs derived): {len(mismatches)}")
for mm in mismatches:
    print(" ", mm)

from collections import Counter
print("\nBy nature:", Counter(r["nature"] for r in out))
print("By weight:", Counter(r["weight"] for r in out))
print("Prior rule status:", Counter((r["prior_rule"]["status"] if r["prior_rule"] else "null (genuinely new)") for r in out))

# Re-verify verbatim for both source_text and any prior_rule.source_text.
# Canonicalised, like every other verbatim check in the pipeline: the Taxonomy
# text is PDF-derived and line-wrapped, so a raw substring test reports two real
# spans as missing. See textnorm.canonical.
CANON_FULLTEXT = canonical(FULLTEXT)
fail = []
for r in out:
    if canonical(r['source_text']) not in CANON_FULLTEXT:
        fail.append((r['id'], 'new source_text FAIL'))
    prior = r['prior_rule']
    if prior and prior['source_text'] and canonical(prior['source_text']) not in CANON_FULLTEXT:
        fail.append((r['id'], 'prior source_text FAIL'))
print("\nVerbatim re-check:", "ALL PASS" if not fail else fail)

# Nothing is written until the spans check out, so a failed re-check cannot
# leave a half-verified register on disk.
if fail:
    raise SystemExit(1)

with open('../data/omnibus.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

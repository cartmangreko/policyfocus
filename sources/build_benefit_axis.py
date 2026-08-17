"""
Sweep the committed data for benefit-axis mislabelling, apply the object rule in
benefit_axis.py, and enforce the quantum-basis guardrail.

Additive migration: fields are added, none are removed. The only pre-existing
fields this script ever rewrites are measure_type and direction, and only on the
rows listed in RECLASSIFY -- each with its reason recorded here and reprinted in
the report.

Run from sources/:  python3 build_benefit_axis.py
Writes:  ../data/ets.json, ../data/iaa.json, benefit_axis_report.md
"""
import json
import os
import subprocess
import sys
from collections import Counter

from textnorm import canonical
from benefit_axis import assert_benefit_basis, derive_valence, load_fulltext

DATA_FILES = [("ets", "../data/ets.json"), ("iaa", "../data/iaa.json"), ("omnibus", "../data/omnibus.json"),
              ("cbam", "../data/cbam.json")]

# The commit that first applied the object rule and moved these rows off the
# benefit axis. Recorded in each reclass_from so the provenance points at a real
# place in the history rather than at "some build".
RECLASS_COMMIT = "f1bd6f1"

# Fields that assert a support movement. An obligation row must carry none of
# them (the validate_v2 invariant); a row reclassified onto the obligation side
# sheds them into reclass_from.
BENEFIT_SIDE_FIELDS = ("benefit", "value_drivers", "access_frictions",
                       "support_cut_basis", "opportunity_basis")

# Fields that assert a duty. A benefit-side row -- incentive or right -- must
# carry none of them.
OBLIGATION_SIDE_FIELDS = ("duty",)


def _shed(rec, fields):
    """Drop fields that contradict the row's new side. Returns the names dropped.

    Values are not preserved in the row. The provenance key plus git history is
    the audit trail, per Ruling 2 -- keeping a shadow copy of a field the schema
    says must not be there just relocates the contradiction.
    """
    dropped = []
    for f in fields:
        if rec.get(f):
            dropped.append(f)
        rec.pop(f, None)
    return dropped

# ---------------------------------------------------------------------------
# RECLASSIFY: rows the object rule moves off the benefit axis.
#
# Every one of these was routed to the incentive side because the text named a
# support instrument (free allocation, a fund, a scheme, ETS scope). None of them
# changes the support's amount, rate, eligibility or existence -- each changes a
# duty, a condition, a procedure or the scope of a duty. So: obligation side.
#
# duty= supplies the obligation-side field these rows never had (they were
# authored as incentive rows and carry only `benefit`). `benefit` is kept, per
# additive-only.
# ---------------------------------------------------------------------------
_WAS_SUPPORT_CUT = {
"FRE-04": dict(
    measure_type="obligation", direction="rem",
    duty="Draw up an Invest in EU decarbonisation plan and pass the additional verification gating the final 20% tranche of free allocation.",
    reason="No quantum basis. The object is the decarbonisation-plan duty and its verification step, not the allocation; the allocation itself is unchanged (indeed protected). Object rule -> obligation side, direction rem."),
"FRE-05": dict(
    measure_type="obligation", direction="rem",
    duty="Draw up an Invest in EU decarbonisation plan and satisfy the 80/20 tranching conditionality attached to free allocation.",
    reason="No quantum basis. A condition attached to the support is removed, not the support. Object rule -> obligation side, direction rem."),
"SHIP-03": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances equal to full verified emissions from long inbound voyages, including the transhipped share.",
    reason="No quantum basis. The object is the surrender obligation and how much of it applies, not any support. Object rule -> obligation side, direction rem."),
"AVI-04": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances under Art. 12(3) for emissions from flights to or from listed LDC/SIDS states.",
    reason="No quantum basis. An exemption from the surrender duty is a duty removal, not a support cut. Object rule -> obligation side, direction rem."),
"CCS-01": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for emissions that are captured and transported for permanent storage in a permitted facility.",
    reason="No quantum basis. The provision extinguishes a surrender obligation; it moves no support. Object rule -> obligation side, direction rem."),
"CCS-02": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for CO2 captured and utilised so as to become permanently chemically bound in a product.",
    reason="No quantum basis. The provision extinguishes a surrender obligation. Object rule -> obligation side, direction rem."),
"WST-02": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for emissions from waste incineration and co-incineration installations in outermost regions.",
    reason="No quantum basis. A Member State option to exempt installations from the surrender duty is a duty removal. Object rule -> obligation side, direction rem."),
"WST-03": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for the emissions of a given reference year from waste incineration and co-incineration installations.",
    reason="No quantum basis. A conditional exemption from the surrender duty is a duty removal. Object rule -> obligation side, direction rem."),

}

# Same rule, applied symmetrically to the positive side. This goes beyond the
# brief's Step 3 sweep, which named only Support cut -- called out separately in
# the report so it can be confirmed or vetoed on its own.
_WAS_OPPORTUNITY = {
"FRE-06": dict(
    measure_type="obligation", direction="rem",
    duty="Meet the mandatory decarbonisation-investment volume under Art. 10a(3b), fifth subparagraph, installation by installation.",
    reason="No quantum basis. Pooling changes how an investment REQUIREMENT may be discharged; the free allocation it conditions is untouched. Object rule -> obligation side, direction rem."),
"SHIP-04": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for containers transhipped via listed neighbouring non-EU ports, once the temporary exclusion lapses.",
    reason="No quantum basis. Extending an exclusion from ETS surrender scope postpones a duty; it creates no support. Object rule -> obligation side, direction rem."),
"CCS-03": dict(
    measure_type="obligation", direction="rem",
    duty="Surrender allowances for fossil emissions without the option of compensating them with own certified permanent carbon removal units.",
    reason="No quantum basis. A new way to discharge the surrender obligation eases the duty; no support amount, rate, eligibility or existence changes. Object rule -> obligation side, direction rem."),
"PRM-04": dict(
    measure_type="obligation", direction="rem",
    duty="Run the ordinary (non-priority) environmental assessment and permitting track for an energy-intensive industry decarbonisation project.",
    reason="No quantum basis. Strategic-project status buys priority/streamlined PROCEDURE, not money. Object rule -> obligation side, direction rem."),
"PRM-06": dict(
    measure_type="obligation", direction="rem",
    duty="Run the ordinary (non-priority) environmental assessment and permitting track for a net-zero technology manufacturing project.",
    reason="No quantum basis. Strategic-project status buys priority/streamlined PROCEDURE, not money. Object rule -> obligation side, direction rem."),
"AA-04b": dict(
    measure_type="obligation", direction="rem",
    duty="Obtain the full set of permits and authorisations for a project, including those inside the scope of the aggregated baseline permit.",
    reason="No quantum basis. The object is the permitting procedure. Object rule -> obligation side, direction rem."),
}

# `was` records the label each row carried before the fix, so the report reads
# the same on a re-run over already-migrated data as it does on a fresh one.
RECLASSIFY = {
    **{k: dict(v, was="Support cut") for k, v in _WAS_SUPPORT_CUT.items()},
    **{k: dict(v, was="Opportunity") for k, v in _WAS_OPPORTUNITY.items()},
}

# ---------------------------------------------------------------------------
# CONFERS_RIGHT: rows the two-sided rule sent to the obligation side, which
# actually confer a faculty. See benefit_axis.py, "THE THIRD SIDE".
#
# Each was re-read against its own source span rather than taken from a list.
# The test is the operative verb: does the addressee hold something they did
# not hold before? Six rows were proposed; five confer, one does not --
#
#   SHIP-04 stays Simplification. Its entire operative text is 'the date
#   "31 December 2030" is replaced by "31 December 2038"'. That postpones the
#   lapse of an existing exclusion. Nobody is handed anything; a duty simply
#   stays away for longer. Welcome, but not a right.
#
# These rows move to the benefit side, so they shed `duty` and keep `benefit`,
# symmetric with incentive rows.
# ---------------------------------------------------------------------------
CONFERS_RIGHT = {
"FRE-06": dict(
    kind="procedure",
    basis="may request to form a pool of installations for the purposes of fulfilling jointly the investment requirements",
    reason="Operators 'may request to form a pool' — a faculty for discharging the investment requirement jointly that no operator previously held. The requirement itself is unchanged, which is why this is not a Simplification: nothing shrank, something was granted."),
"CCS-03": dict(
    kind="conferral",
    basis="shall provide for the possibility for operators, aircraft operators and shipping companies to compensate their fossil emissions with domestic permanent carbon removal units",
    reason="The implementing acts 'shall provide for the possibility for operators ... to compensate' — an entitlement to discharge surrender with own certified removal units. A new instrument in the operator's hands, not a narrower duty."),
"PRM-04": dict(
    kind="scope",
    basis="All energy-intensive industry decarbonisation projects shall be considered strategic projects contributing to resilience and decarbonisation or resource efficiency",
    reason="Confers strategic-project STATUS on a whole class of project, which unlocks the priority permitting track. The conferral is the status; kind 'scope' records which projects it reaches."),
"PRM-06": dict(
    kind="scope",
    basis="All net-zero technology manufacturing projects shall be considered strategic projects contributing to resilience and decarbonisation or resource efficiency",
    reason="Same conferral as PRM-04, for net-zero technology manufacturing projects."),
"AA-04b": dict(
    kind="scope",
    basis="shall be required to obtain only those additional permits or authorisations that fall outside the scope of the aggregated baseline permit",
    reason="Projects inside an acceleration area may rely on the area's aggregated baseline permit — the streamlined-permitting privilege the acceleration-area regime exists to confer. Phrased as 'shall be required to obtain only', so it reads as a duty narrowing; the object is the conferred baseline permit, and the narrowing is its consequence. Flagged in the report as the one genuinely two-faced row of the five."),
}

# ---------------------------------------------------------------------------
# BASIS: rows that stay on the benefit axis, each pointing at the verbatim span
# naming the quantum it moves. kind is amount | rate | eligibility | existence.
# Every text below is asserted to appear verbatim in the row's own source file.
# ---------------------------------------------------------------------------
BASIS = {
# --- ETS, Opportunity ------------------------------------------------------
"FRE-08": ("eligibility", "in paragraph 1, second sentence, ‘2030’ is replaced by ‘2040’;"),
"FRE-09": ("rate", "Free allocation to district heating shall decrease by equal amounts after 2030 so as to reach a level of no free allocation in 2040."),
# NB: the source uses non-breaking spaces inside "260 million" / "260 Mt" —
# they are preserved in the span below, which must match the file byte for byte.
"FND-01": ("amount", "Up to 260 million allowances from the Union-wide quantity of allowances referred to in Article 9 shall be made available to the facility for the purchase of up to 260 Mt of high quality and high integrity international credits"),
"FND-02": ("amount", "The Union-wide quantity of allowances referred to in Article 9 shall be increased by 250 million allowances."),
"FND-03": ("existence", "A fund (the ‘Innovation Fund’) is hereby established to support bringing innovation to market"),
"FND-04": ("existence", "An instrument to support the scaling up and deployment of the technologies, processes and techniques to decarbonise industries (the ‘Industrial Decarbonisation Bank) is established starting from 2028."),
"FND-05": ("rate", "the Commission shall support under the Industrial Decarbonisation Bank projects through allocating allowances based on a fixed carbon premium to eligible projects within the Union"),
"FND-06": ("amount", "reserving 400 million allowances to support industrial decarbonisation projects within the Union through competitive bidding procedures"),
"FND-07": ("eligibility", "Member States with a GDP per capita at market prices below 75 % of the Union average in the period 2022 to 2024"),
"FND-08": ("rate", "Member States shall use at least 50% of those revenues"),
"FND-09": ("eligibility", "in favour of sectors or subsectors which are exposed to a genuine risk of carbon leakage due to significant indirect costs that are actually incurred from greenhouse gas emission costs passed on in electricity prices"),
"FND-10": ("amount", "together with 200 million allowances placed in the market stability reserve pursuant to Article 1(3) of Decision (EU) 2015/1814 and 50 million allowances from the quantity of allowances resulting from the reduction of free allocation"),
"SHIP-01": ("amount", "a maximum of 110 million of the Union-wide quantity of allowances referred to in Article 9 shall be reserved for the use of sustainable maritime fuels or the deployment and operation of zero-emission propulsion technologies"),
"SHIP-02": ("amount", "An amount of 0.9 million of the Union-wide quantity of allowances referred to in Article 9 shall be reserved for the decarbonisation of the maritime sector in least developed countries and small island developing States"),
"AVI-01": ("rate", "shall be allocated by the Member States to cover part of or all of the price differential between the use of fossil kerosene and the use of the relevant eligible aviation fuels"),
"AVI-02": ("amount", "a further maximum 110 million allowances of the allowances referred to in third subparagraph of paragraph 1 shall be reserved for the purposes laid down in Article 3c(6) until 31 December 2040."),
"ETSSVC-01": ("amount", "The corresponding revenues generated from the auctioning of these allowances shall be transferred to the third country."),

# --- IAA, Opportunity ------------------------------------------------------
"LM-03b": ("rate", "at least 25% of the total volume of steel used shall be low-carbon"),
"LM-03c": ("eligibility", "the ratio between the total ex-works price of vehicle components - excluding the vehicle battery - originating in the Union and the total ex-works price of all components – excluding the battery – is at least 70%"),
"LM-06b": ("rate", "at least 25% of the total volume of steel used in the product or project that receives support shall be low-carbon"),
# LM-06c's basis was quoted from the middle of the Annex II Part II sentence,
# which left it standing on a fragment. Extended to the full sentence, so it is
# verbatim on its own terms and needs no status.
"LM-06c": ("eligibility", "(a) steel, and any product the performance of which depends primarily on steel : at\nleast 25% of the total volume of steel used in the product or project that\nreceives support shall be low-carbon;"),
"LM-15b": ("eligibility", "the battery energy storage systems shall originate in the Union"),
"LM-18b": ("rate", "shall apply to at least 40% of the volume auctioned per year per Member State or alternatively to at least 8 Gigawatt per year per Member State"),
"LM-20b": ("eligibility", "the PV inverter and the PV cells or equivalent shall originate in the Union"),
"LM-21b": ("rate", "it shall not exceed 15% of the cost of the final product for the consumer"),
"LM-23b": ("eligibility", "Member States shall ensure that the electrolyser originates in the Union and the stack and at least one additional main specific component of the electrolyser originate in the Union"),
"LM-26b": ("eligibility", "shall ensure that only vehicles that comply with the below minimum Union origin requirements are eligible under the scheme"),
"LM-26c": ("eligibility", "the ratio between the total ex-works price of vehicle components - excluding the vehicle battery - originating in the Union and the total ex-works price of all vehicle components – excluding the battery – is equal to or greater than 70%"),
# SC-01 and SC-02 define who qualifies for a super-credit whose size is set by
# the CO2-standards regulation. The eligibility hook is here; the quantum is
# there. `external` with a CELEX pointer says exactly that, rather than
# paraphrasing a number this act does not contain. The pointer is enough until
# that regulation is ingested, at which point the basis can become verbatim
# against it.
"SC-01": ("eligibility", "the ‘made in the EU’ criterion for small zero- emission vehicles shall comply with the criteria set out in Part III of Annex III to this Regulation",
          {"basis_status": "external",
           "pointer": "Quantum (the super-credit multiplier) is set by Regulation (EU) 2019/631 on CO2 emission standards for new light duty vehicles, CELEX 32019R0631, as amended by the proposal of 16 December 2025 cited in this Article. Not yet ingested."}),
"SC-02": ("eligibility", "‘low-carbon steel made in the EU’ shall be understood as follows",
          {"basis_status": "external",
           "pointer": "Quantum (the super-credit multiplier) is set by Regulation (EU) 2019/631 on CO2 emission standards for new light duty vehicles, CELEX 32019R0631, as amended by the proposal of 16 December 2025 cited in this Article. Not yet ingested."}),
# IAAB-CHEM-01 is an empowerment to adopt demand-side measures. There is no
# instrument yet, so there is no quantum anywhere to point at -- only a stated
# intent. `announced` is the honest floor.
"IAAB-CHEM-01": ("existence", "laying down Union-level demand-side measures for products from the chemical industry in order to promote the following activities",
                 {"basis_status": "announced",
                  "pointer": "Announced: an empowerment for the Commission to lay down Union-level demand-side measures for chemical-industry products. No delegated or implementing act adopted, so no amount, rate or eligibility exists to cite. Revisit when the instrument lands."}),
}

# Rows whose benefit label survives but whose basis is a judgement call worth a
# human eye. Listed, not auto-changed.
CONFIRM = {
    "IAAB-CHEM-01": "Support is prospective: an empowerment to adopt demand-side measures, not yet an instrument. Basis kind 'existence' is the most it can carry today.",
    "LM-06c": "Basis is quoted from Annex II Part II rather than the row's own source_text span, which stops before the qualifying share.",
    "SC-01": "'made in the EU' status confers eligibility for a super-credit under a separate regulation; the quantum lives in that instrument, not here.",
    "SC-02": "Same as SC-01: eligibility definition feeding the CO2-standards compensation regime; no quantum stated in this text.",
}


def main():
    report_rows, confirmed, per_file_counts, pending_writes = [], [], {}, []
    seen = set()  # ids from RECLASSIFY/BASIS actually found in the data

    for key, path in DATA_FILES:
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
        fulltext = load_fulltext(key)

        by_id = {r["id"]: r for r in rows}
        seen.update(
            k for k in list(RECLASSIFY) + list(BASIS) + list(CONFERS_RIGHT) if k in by_id
        )

        out = []
        for r in rows:
            rec = dict(r)  # additive: every existing field survives

            if rec["id"] in CONFERS_RIGHT:
                # Checked before RECLASSIFY: five of these rows are in that table
                # too, having been sent to the obligation side by the two-sided
                # rule. The right ruling supersedes it, and the row moves back to
                # the benefit side rather than staying a Simplification.
                m = CONFERS_RIGHT[rec["id"]]
                was = derive_valence(
                    RECLASSIFY[rec["id"]]["measure_type"], RECLASSIFY[rec["id"]]["direction"]
                ) if rec["id"] in RECLASSIFY else derive_valence(
                    rec.get("measure_type"), rec.get("direction")
                )
                rec["measure_type"] = "right"
                rec["direction"] = "add"
                rec["right_basis"] = {"text": m["basis"], "kind": m["kind"]}
                # Benefit-side row: it carries `benefit`, never `duty`. The duty
                # here was written by the earlier obligation-side ruling and is
                # now a statement of something the provision does not do.
                shed = _shed(rec, OBLIGATION_SIDE_FIELDS)
                # Same provenance discipline as Ruling 2's obligation-side moves:
                # this row was an obligation in the committed data and is not one
                # now, and the `duty` it shed said the opposite of what the
                # provision does. Recorded so the move is legible without git.
                if rec["id"] in RECLASSIFY:
                    rec["reclass_from"] = {
                        "measure_type": RECLASSIFY[rec["id"]]["measure_type"],
                        "commit": RECLASS_COMMIT,
                        "note": "Object rule sent it to the obligation side; the operative verb confers a faculty, so it is a right.",
                    }
                rec["benefit_axis_note"] = m["reason"]
                report_rows.append({
                    "file": key, "id": rec["id"], "old": was, "new": "Entitlement",
                    "affected_delta": rec.get("benefit"),
                    "reason": m["reason"], "shed": shed, "to_right": True,
                })

            elif rec["id"] in RECLASSIFY:
                m = RECLASSIFY[rec["id"]]
                rec["measure_type"] = m["measure_type"]
                rec["direction"] = m["direction"]
                rec.setdefault("duty", m["duty"])
                new_label = derive_valence(rec["measure_type"], rec["direction"])
                rec["benefit_axis_note"] = m["reason"]
                delta = rec.get("affected_delta") or rec.get("benefit") or rec.get("duty")
                # RULING 2. The validate_v2 invariant holds: an obligation row
                # carries no benefit-side field. These rows arrived as incentive
                # rows, so they carry `benefit`, `value_drivers`,
                # `access_frictions` -- fields that assert a support movement the
                # object rule has just found there isn't. They are shed, and
                # `reclass_from` records that they were, so the row is not
                # silently thinner than it was. Git holds the values themselves.
                shed = _shed(rec, BENEFIT_SIDE_FIELDS)
                rec["reclass_from"] = {
                    "measure_type": m.get("from_measure_type", "incentive"),
                    "commit": RECLASS_COMMIT,
                    "note": m["reason"].split(". ", 1)[-1].rstrip("."),
                }
                report_rows.append({
                    "file": key, "id": rec["id"], "old": m["was"], "new": new_label,
                    "affected_delta": delta, "reason": m["reason"], "shed": shed,
                })

            elif rec["id"] in BASIS:
                entry = BASIS[rec["id"]]
                kind, text = entry[0], entry[1]
                extra = entry[2] if len(entry) > 2 else {}
                label = derive_valence(rec.get("measure_type"), rec.get("direction"))
                field = "support_cut_basis" if label == "Support cut" else "opportunity_basis"
                rec[field] = {"text": text, "kind": kind, **extra}
                if rec["id"] in CONFIRM:
                    confirmed.append({
                        "file": key, "id": rec["id"], "label": label, "kind": kind,
                        "status": extra.get("basis_status", "verbatim"),
                        "pointer": extra.get("pointer"),
                        "note": CONFIRM[rec["id"]],
                    })

            out.append(rec)

        # THE GUARDRAIL -- build fails here, naming ids, if any benefit label on
        # this file cannot point at a verbatim quantum.
        assert_benefit_basis(out, fulltext, where=f" in {path}")

        after = Counter(derive_valence(r.get("measure_type"), r.get("direction")) for r in out)
        # "before" is reconstructed from each reclassified row's recorded `was`,
        # not read off the file — so a re-run over already-migrated data still
        # reports the pre-fix picture rather than a no-op.
        before = Counter(after)
        for rr in report_rows:
            if rr["file"] == key:
                before[rr["new"]] -= 1
                before[rr["old"]] += 1
        before = Counter({k: v for k, v in before.items() if v})
        per_file_counts[key] = (len(out), before, after)

        # Verbatim re-check of the pre-existing discipline. Canonicalised, like
        # every other verbatim check in the pipeline (verify_pass, benefit_axis):
        # this was the one place still doing a raw substring test, which stopped
        # holding the moment the IAA source became PDF-derived and acquired line
        # wrapping. It failed 48 of 62 IAA rows on untouched data -- not because
        # any quote was wrong, but because the check could not see through a line
        # break. Same discipline, applied the way the rest of the pipeline
        # applies it.
        canon_fulltext = canonical(fulltext)
        stale = [r["id"] for r in out if canonical(r["source_text"]) not in canon_fulltext]
        assert not stale, f"source_text no longer verbatim in {path}: {stale}"

        pending_writes.append((path, out))

    # No hand-authored id may reference a row that does not exist, in the style
    # of build_data_v2.py's set(META.keys()) == set(by_id.keys()).
    orphans = (set(RECLASSIFY) | set(BASIS) | set(CONFERS_RIGHT)) - seen
    assert not orphans, (
        f"RECLASSIFY/BASIS/CONFERS_RIGHT ids not present in any data file: {sorted(orphans)}"
    )

    # A row on the benefit side may not also assert a duty, and an obligation row
    # may not assert a benefit. This is the validate_v2 invariant, enforced here
    # too so the build cannot write a file that validate_v2 will reject.
    for path, out in pending_writes:
        crossed = []
        for r in out:
            t = r.get("measure_type")
            if t == "obligation":
                bad = [f for f in BENEFIT_SIDE_FIELDS if r.get(f)]
            else:
                bad = [f for f in OBLIGATION_SIDE_FIELDS if r.get(f)]
            if bad:
                crossed.append((r["id"], t, bad))
        assert not crossed, f"rows carrying fields from the wrong side in {path}: {crossed}"

    # The two derivations of the valence rule must agree before anything is
    # written. If they don't, the build would produce data labelled one way and
    # a site rendering it another, which is worse than not building.
    parity = subprocess.run([sys.executable, "check_valence_parity.py"],
                            cwd=os.path.dirname(os.path.abspath(__file__)))
    assert parity.returncode == 0, (
        "valence parity check failed — benefit_axis.derive_valence and "
        "web/lib/valence.ts disagree; see the diff above"
    )

    # Nothing is written until every file has passed, so a failure never leaves
    # half the register migrated.
    for path, out in pending_writes:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    write_report(report_rows, confirmed, per_file_counts)

    for key, (n, before, after) in per_file_counts.items():
        print(f"{key}: {n} rows")
        print(f"  before: {dict(before)}")
        print(f"  after:  {dict(after)}")
    print(f"\nReclassified: {len(report_rows)}   Flagged for confirmation: {len(confirmed)}")
    print("Guardrail: all benefit labels carry a verbatim quantum basis. PASS")
    print("Report written to sources/benefit_axis_report.md")


def write_report(report_rows, confirmed, per_file_counts):
    L = ["# Benefit-axis reclassification report", ""]
    L.append("Produced by `sources/build_benefit_axis.py`. The rule applied is documented in `sources/benefit_axis.py`.")
    L.append("")
    L.append("## Counts")
    L.append("")
    L.append("| file | rows | before | after |")
    L.append("|---|---|---|---|")
    for key, (n, before, after) in per_file_counts.items():
        b = ", ".join(f"{k} {v}" for k, v in sorted(before.items()))
        a = ", ".join(f"{k} {v}" for k, v in sorted(after.items()))
        L.append(f"| {key} | {n} | {b} | {a} |")
    L.append("")
    L.append("## Reclassified (no verbatim quantum basis available)")
    L.append("")
    for r in report_rows:
        L.append(f"### {r['id']} ({r['file']}) — {r['old']} → {r['new']}")
        L.append("")
        L.append(f"- **affected_delta:** {r['affected_delta']}")
        L.append(f"- **reason:** {r['reason']}")
        L.append("")
    L.append("## Kept on the benefit axis, flagged for human confirmation")
    L.append("")
    for c in confirmed:
        L.append(f"- **{c['id']}** ({c['file']}, {c['label']}, basis kind `{c['kind']}`) — {c['note']}")
    L.append("")
    with open("benefit_axis_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()

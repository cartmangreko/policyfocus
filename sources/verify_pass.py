"""
Mechanically verify one extraction pass (a JSON array of records) against its
source text file(s). Rejects/flags any row whose source_text is not an exact
substring, and any row failing basic schema sanity.

Also enforces the benefit-axis guardrail: a row may only carry the "Support cut"
or "Opportunity" valence if it cites a verbatim quantum basis. See
benefit_axis.py for the classification rule that decides measure_type in the
first place -- measure_type follows the OBJECT the provision acts on, never the
instrument its text happens to name.

Usage: python3 verify_pass.py <rows.json> <source1.txt> [source2.txt ...]

WHAT TO POINT IT AT
===================
The register -- ../data/ets.json, ../data/iaa.json, ../data/omnibus.json. Those
are the files this gate is the gate for, and all three pass.

NOT the extraction passes. sources/*_pass_a.json and *_pass_b.json are the
frozen record of two independent reads of the same act, and their disagreement
is the signal reconcile.py exists to measure. Running this over them reports 28
ETS and 16 IAA failures, and every one is an artefact of the passes predating
the rules being checked: a pass file is a PROPOSAL, the register is the RULING.
The benefit-axis guardrail was written after those snapshots were taken, so it
asks them for bases that the classification rule had not yet demanded. All 44
are accounted for in the register -- 14 rows reclassified, 30 given a verbatim
basis -- and none is a sourcing failure.

They are deliberately not backported. Editing Pass A to carry conclusions
reached after it was written would make the reconciliation vacuous: agreement
between two passes means nothing once one of them has been corrected to agree.
"""
import sys, json

from textnorm import canonical
from benefit_axis import (BASIS_FIELD, MEASURE_TYPES, benefit_basis_ok,
                          derive_valence)

# Kept here rather than imported from build_benefit_axis: that module is the
# migration, this one is the gate, and the gate should not depend on the thing
# it checks.
BENEFIT_SIDE_FIELDS = ("benefit", "value_drivers", "access_frictions",
                       "support_cut_basis", "opportunity_basis")

def main():
    pass_path = sys.argv[1]
    source_paths = sys.argv[2:]
    with open(pass_path, encoding='utf-8') as f:
        rows = json.load(f)
    sources = []
    for p in source_paths:
        with open(p, encoding='utf-8') as f:
            # Canonicalised once here rather than per row: the substring check
            # must ignore line wrapping and PDF hyphenation, which differ by
            # source format without changing a word. See textnorm.
            sources.append((p, canonical(f.read())))
    all_text = "\n".join(text for _, text in sources)

    ok, fail = [], []
    for r in rows:
        rid = r.get('id', '???')
        st = r.get('source_text', '')
        found_in = [p for p, text in sources if st and canonical(st) in text]
        errs = []
        if not st:
            errs.append("empty source_text")
        elif not found_in:
            errs.append("source_text NOT an exact substring of any source file")
        if r.get('measure_type') not in MEASURE_TYPES:
            errs.append(f"bad measure_type: {r.get('measure_type')!r}")
        if r.get('direction') not in ('add', 'rem'):
            errs.append(f"bad direction: {r.get('direction')!r}")
        if r.get('measure_type') == 'obligation':
            if not r.get('duty'):
                errs.append("obligation row missing duty")
            # The validate_v2 invariant: an obligation row asserts no support
            # movement. Rows moved here by the object rule shed those fields into
            # reclass_from rather than keeping a claim the rule has just denied.
            crossed = [f for f in BENEFIT_SIDE_FIELDS if r.get(f)]
            if crossed:
                errs.append(f"obligation row carries benefit-side fields: {crossed}")
        if r.get('measure_type') == 'incentive':
            if not r.get('benefit'):
                errs.append("incentive row missing benefit")
            if not r.get('value_drivers'):
                errs.append("incentive row missing value_drivers (need >=1)")
        if r.get('measure_type') == 'right':
            # Symmetric with incentive: a right row states what the addressee may
            # now do, and never a duty.
            if not r.get('benefit'):
                errs.append("right row missing benefit")
            if r.get('duty'):
                errs.append("right row carries a duty (benefit-side rows state no duty)")
        if not benefit_basis_ok(r, all_text):
            label = derive_valence(r.get('measure_type'), r.get('direction'))
            errs.append(f"{label} without a verbatim quantum basis in {BASIS_FIELD[label]}")
        if errs:
            fail.append((rid, errs, found_in))
        else:
            ok.append((rid, found_in))

    print(f"{pass_path}: {len(rows)} rows, {len(ok)} passed, {len(fail)} failed")
    if fail:
        print("\nFAILURES:")
        for rid, errs, found_in in fail:
            print(f"  {rid}: {errs}")
    # Exit non-zero on failure. Previously main() always returned None, so the
    # process exited 0 whatever it found and the gate could only be read by a
    # human looking at the output -- which makes it useless in a build or a CI
    # step, the two places it most needs to bite.
    return 1 if fail else 0

if __name__ == '__main__':
    sys.exit(main())

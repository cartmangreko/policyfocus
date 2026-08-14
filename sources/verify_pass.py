"""
Mechanically verify one extraction pass (a JSON array of records) against its
source text file(s). Rejects/flags any row whose source_text is not an exact
substring, and any row failing basic schema sanity.

Also enforces the benefit-axis guardrail: a row may only carry the "Support cut"
or "Opportunity" valence if it cites a verbatim quantum basis. See
benefit_axis.py for the classification rule that decides measure_type in the
first place -- measure_type follows the OBJECT the provision acts on, never the
instrument its text happens to name.

Usage: python3 verify_pass.py <pass.json> <source1.txt> [source2.txt ...]
"""
import sys, json

from textnorm import canonical
from benefit_axis import BASIS_FIELD, benefit_basis_ok, derive_valence

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
        if r.get('measure_type') not in ('obligation', 'incentive'):
            errs.append(f"bad measure_type: {r.get('measure_type')!r}")
        if r.get('direction') not in ('add', 'rem'):
            errs.append(f"bad direction: {r.get('direction')!r}")
        if r.get('measure_type') == 'obligation' and not r.get('duty'):
            errs.append("obligation row missing duty")
        if r.get('measure_type') == 'incentive':
            if not r.get('benefit'):
                errs.append("incentive row missing benefit")
            if not r.get('value_drivers'):
                errs.append("incentive row missing value_drivers (need >=1)")
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

if __name__ == '__main__':
    main()

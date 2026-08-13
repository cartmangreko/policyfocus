"""
Mechanically verify one extraction pass (a JSON array of records) against its
source text file(s). Rejects/flags any row whose source_text is not an exact
substring, and any row failing basic schema sanity.

Usage: python3 verify_pass.py <pass.json> <source1.txt> [source2.txt ...]
"""
import sys, json

def main():
    pass_path = sys.argv[1]
    source_paths = sys.argv[2:]
    with open(pass_path, encoding='utf-8') as f:
        rows = json.load(f)
    sources = []
    for p in source_paths:
        with open(p, encoding='utf-8') as f:
            sources.append((p, f.read()))

    ok, fail = [], []
    for r in rows:
        rid = r.get('id', '???')
        st = r.get('source_text', '')
        found_in = [p for p, text in sources if st and st in text]
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

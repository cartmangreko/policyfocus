import json
from collections import Counter, defaultdict

with open('../data/omnibus.json', encoding='utf-8') as f:
    rows = json.load(f)

fail = []

for r in rows:
    # every row has measure_type and a computable valence
    if r.get('measure_type') not in ('obligation', 'incentive'):
        fail.append((r['id'], f"missing/invalid measure_type: {r.get('measure_type')!r}"))
        continue
    if r['direction'] not in ('add', 'rem'):
        fail.append((r['id'], f"direction not add/rem, valence not computable: {r['direction']!r}"))

    if r['measure_type'] == 'obligation':
        if not r.get('duty'):
            fail.append((r['id'], "obligation row missing duty"))
        if r.get('benefit') or r.get('value_drivers') or r.get('access_frictions'):
            fail.append((r['id'], "obligation row has benefit-side fields set"))
    else:  # incentive
        if not r.get('benefit'):
            fail.append((r['id'], "incentive row missing benefit statement"))
        if not r.get('value_drivers'):
            fail.append((r['id'], "incentive row has no value_driver (needs at least one)"))

# provision_id: any row sharing one must have >=2 siblings (a real split, not orphaned)
by_pid = defaultdict(list)
for r in rows:
    if r.get('provision_id'):
        by_pid[r['provision_id']].append(r['id'])
for pid, ids in by_pid.items():
    if len(ids) < 2:
        fail.append((ids[0], f"provision_id {pid!r} has no sibling record"))

# migration check: every row currently in the Omnibus file is obligation-only,
# no benefit-side field set, matching the relief-heavy simplification file
migration_ok = all(
    r['measure_type'] == 'obligation' and not r.get('benefit')
    and not r.get('value_drivers') and not r.get('access_frictions')
    for r in rows
)

print(f"Total rows: {len(rows)}")
print(f"measure_type: {Counter(r['measure_type'] for r in rows)}")
print(f"Migration check (all obligation, no benefit fields set): {'PASS' if migration_ok else 'FAIL'}")
print(f"provision_id groups: {len(by_pid)}")

if fail:
    print(f"\nVALIDATION FAILURES ({len(fail)}):")
    for f_ in fail:
        print(" ", f_)
else:
    print("\nAll v2 validation checks passed.")

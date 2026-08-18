"""
v2 schema validation for the register.

Checks the invariants that make a row readable without reading the source: a
row sits on exactly one side, carries that side's fields, and carries none of
the other side's.

Previously this read only ../data/omnibus.json, which is the one file where
every row is an obligation -- so the invariant it exists to enforce was never
tested against a file that could break it. It now walks all three.

    python3 validate_v2.py      # exits non-zero on any failure
"""
import json
import sys
from collections import Counter, defaultdict

from benefit_axis import BENEFIT_SIDE_TYPES, MEASURE_TYPES

DATA_FILES = [
    ("omnibus", "../data/omnibus.json"),
    ("ets", "../data/ets.json"),
    ("iaa", "../data/iaa.json"),
    ("cbam", "../data/cbam.json"),
]

# Fields that assert a support movement or a conferred faculty. An obligation
# row must carry none of them.
BENEFIT_SIDE_FIELDS = ("benefit", "value_drivers", "access_frictions",
                       "support_cut_basis", "opportunity_basis", "right_basis")

# Fields that assert a duty. A benefit-side row must carry none of them.
OBLIGATION_SIDE_FIELDS = ("duty",)


def validate(key, rows):
    fail = []

    for r in rows:
        rid = r.get("id", "???")

        if r.get("measure_type") not in MEASURE_TYPES:
            fail.append((rid, f"missing/invalid measure_type: {r.get('measure_type')!r}"))
            continue
        if r.get("direction") not in ("add", "rem"):
            fail.append((rid, f"direction not add/rem, valence not computable: {r.get('direction')!r}"))

        mt = r["measure_type"]

        if mt == "obligation":
            if not r.get("duty"):
                fail.append((rid, "obligation row missing duty"))
            # THE INVARIANT, unrelaxed. A row reclassified off the benefit side
            # sheds these fields; `reclass_from` records that it did. The
            # provenance key is metadata about a past classification, not a live
            # claim, so it is permitted here -- the fields themselves are not.
            crossed = [f for f in BENEFIT_SIDE_FIELDS if r.get(f)]
            if crossed:
                fail.append((rid, f"obligation row has benefit-side fields set: {crossed}"))

        else:  # incentive | right -- the benefit side
            if not r.get("benefit"):
                fail.append((rid, f"{mt} row missing benefit statement"))
            crossed = [f for f in OBLIGATION_SIDE_FIELDS if r.get(f)]
            if crossed:
                fail.append((rid, f"{mt} row has obligation-side fields set: {crossed}"))
            if mt == "incentive" and not r.get("value_drivers"):
                fail.append((rid, "incentive row has no value_driver (needs at least one)"))
            if mt == "right" and not r.get("right_basis"):
                fail.append((rid, "right row has no right_basis"))

        # reclass_from, where present, must actually say something
        # reclass_from must record a note and a classification that ACTUALLY
        # MOVED. It used to demand measure_type specifically, which assumed
        # every reclassification crosses the benefit axis. It does not: CBAM
        # FIN-06 stayed an obligation and flipped direction add -> rem, turning
        # the user-facing valence from Requirement to Simplification without
        # changing measure_type at all. Under the old rule that correction could
        # not be recorded in the field built to record corrections, so the only
        # way to pass the gate was to drop the audit trail. Either field may
        # carry the movement now; at least one must, and each given must differ
        # from what the row says today.
        rf = r.get("reclass_from")
        if rf is not None:
            if not isinstance(rf, dict) or not rf.get("note"):
                fail.append((rid, f"reclass_from must carry a note: {rf!r}"))
            elif not (rf.get("measure_type") or rf.get("direction")):
                fail.append((rid, f"reclass_from records no prior measure_type or "
                                  f"direction, so nothing is said to have moved: {rf!r}"))
            else:
                unmoved = [f for f in ("measure_type", "direction")
                           if rf.get(f) is not None and rf[f] == r[f]]
                if unmoved:
                    fail.append((rid, f"reclass_from records the same {', '.join(unmoved)} "
                                      "the row now has"))

    # provision_id: any row sharing one must have >=2 siblings (a real split)
    by_pid = defaultdict(list)
    for r in rows:
        if r.get("provision_id"):
            by_pid[r["provision_id"]].append(r["id"])
    for pid, ids in by_pid.items():
        if len(ids) < 2:
            fail.append((ids[0], f"provision_id {pid!r} has no sibling record"))

    return fail, by_pid


def main():
    total_fail = 0
    for key, path in DATA_FILES:
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
        fail, by_pid = validate(key, rows)

        print(f"{key}: {len(rows)} rows")
        print(f"  measure_type: {dict(Counter(r.get('measure_type') for r in rows))}")
        print(f"  provision_id groups: {len(by_pid)}")
        reclassed = [r["id"] for r in rows if r.get("reclass_from")]
        if reclassed:
            print(f"  reclass_from recorded on {len(reclassed)}: {', '.join(sorted(reclassed))}")

        if key == "omnibus":
            # Omnibus is the simplification file: every row is an obligation.
            # Scoped to this file deliberately -- ets and iaa legitimately carry
            # incentive and right rows, so this is a fact about omnibus, not an
            # invariant of the schema.
            all_obligation = all(r.get("measure_type") == "obligation" for r in rows)
            print(f"  migration check (all obligation): {'PASS' if all_obligation else 'FAIL'}")
            if not all_obligation:
                fail.append(("(file)", "omnibus contains a non-obligation row"))

        if fail:
            print(f"  VALIDATION FAILURES ({len(fail)}):")
            for rid, msg in fail:
                print(f"    {rid}: {msg}")
            total_fail += len(fail)
        print()

    if total_fail:
        print(f"FAILED: {total_fail} validation failures")
        return 1
    print("All v2 validation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

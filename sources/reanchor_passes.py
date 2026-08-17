"""
Re-anchor an extraction pass against the register.

The pass files were written against sources that have since moved: ets.txt was
replaced by the fetched Cellar text, and the IAA quotes were repaired for PDF
page-furniture pollution. The spans in the passes still point at the old texts,
so verify_pass rejects nearly every row -- not because a classification is
wrong, but because the evidence no longer resolves.

This copies the source-anchored and classification fields down from
data/<file>.json onto the matching pass row, by id. Everything else on the pass
row is left exactly as it was, including interpretive fields the two passes
disagree about: this is a re-anchoring, not a merge, and the disagreements are
the thing reconcile exists to measure.

    python3 reanchor_passes.py --check      # report, write nothing
    python3 reanchor_passes.py              # rewrite in place

WHAT ACTUALLY FAILED, AND WHAT DID NOT
======================================
Not the spans. Every source_text in all four passes still resolves verbatim
against the current sources -- 0 failures on that check, before this script
touches anything. The sources did not move out from under the passes. What the
passes lack is the basis objects and the classifications the register ruled
later: 28, 27, 16 and 21 rows respectively, every one of them a missing or
invalid basis and nothing else. So this script changes no source_text; it
supplies what the guardrail asks for and the ruling decided.

THE B PASSES CANNOT BE FULLY RE-ANCHORED, AND THAT IS THE FINDING
=================================================================
Pass A and Pass B were independent extractions, so Pass B invented its own ids:
ALC-01, PEN-03, NZT-13b. 21 of 46 rows in ets_pass_b and 37 of 54 in iaa_pass_b
carry an id no register row has -- which is exactly why reconcile matches on
article overlap rather than id.

Article overlap does not rescue them. Of those 58, only 11 hit exactly one
register row; 32 hit several (four register rows share "Art. 1(15)(d)"); and 15
hit none at all -- Pass B found provisions the register does not carry, which is
the Pass-B-only signal reconcile exists to surface.

So rows are re-anchored by id wherever an id matches, in every pass. What
remains is 12 ETS-B and 15 IAA-B rows that both fail the guardrail and have no
register row to copy from. Picking one candidate out of four, or authoring a
basis for a provision nobody has reviewed, would fabricate exactly the evidence
this pipeline exists to check. They are listed instead.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# The fields the register is authoritative for: everything verify_pass checks
# against the sources, plus the classification that decides which basis is
# required in the first place.
SYNCED_FIELDS = (
    "source_text",
    "measure_type",
    "direction",
    "support_cut_basis",
    "opportunity_basis",
    "right_basis",
    "reclass_from",
)

# Fields that must not survive on the wrong side once measure_type is synced.
# A pass row authored as an incentive carries `benefit` and `value_drivers`; if
# the register has since ruled it an obligation, those fields contradict the
# ruling and verify_pass rejects them. Same invariant as validate_v2.
BENEFIT_SIDE_FIELDS = ("benefit", "value_drivers", "access_frictions",
                       "support_cut_basis", "opportunity_basis", "right_basis")
OBLIGATION_SIDE_FIELDS = ("duty",)

PAIRS = [
    ("ets_pass_a.json", "ets.json", ("ets.txt", "ets_annexes.txt")),
    ("ets_pass_b.json", "ets.json", ("ets.txt", "ets_annexes.txt")),
    ("iaa_pass_a.json", "iaa.json", ("iaa.txt", "iaa_annexes.txt")),
    ("iaa_pass_b.json", "iaa.json", ("iaa.txt", "iaa_annexes.txt")),
]


def reanchor(pass_name: str, data_name: str, sources: tuple, write: bool):
    from textnorm import canonical
    from benefit_axis import benefit_basis_ok

    pass_path, data_path = HERE / pass_name, DATA / data_name
    rows = json.loads(pass_path.read_text(encoding="utf-8"))
    data = {r["id"]: r for r in json.loads(data_path.read_text(encoding="utf-8"))}
    fulltext = canonical("\n".join((HERE / s).read_text(encoding="utf-8") for s in sources))

    touched, untouched, unmatched, field_counts = 0, 0, [], {}
    for row in rows:
        src = data.get(row["id"])
        if src is None:
            # No register row of this id. Only a problem if the row also fails
            # the guardrail -- a Pass-B-only find that already verifies needs
            # nothing from us.
            if not benefit_basis_ok(row, fulltext):
                unmatched.append(row["id"])
            else:
                untouched += 1
            continue

        before = json.dumps(row, sort_keys=True, ensure_ascii=False)

        for f in SYNCED_FIELDS:
            if f == "source_text":
                # Only replaced when the pass's own span no longer resolves.
                # Pass B quoted the same provisions through a different window,
                # and that independent choice of span is the second read. As it
                # happens no span in any pass has gone stale, so this branch
                # never fires today -- it is here for the day a source really
                # does move, which is the case the brief was written against.
                if canonical(row.get("source_text", "")) not in fulltext:
                    row[f] = src[f]
                continue
            if f in src:
                row[f] = src[f]
            else:
                # The register does not carry this field for this row, so the
                # pass must not either -- a basis the ruling dropped is a claim
                # nobody is making any more.
                row.pop(f, None)

        # Shed whatever the synced measure_type now contradicts. The values are
        # in git; keeping them here would just move the contradiction.
        wrong_side = (BENEFIT_SIDE_FIELDS if row.get("measure_type") == "obligation"
                      else OBLIGATION_SIDE_FIELDS)
        for f in wrong_side:
            if f in SYNCED_FIELDS and f in src:
                continue  # the register itself supplies it; keep the synced value
            row.pop(f, None)

        # An obligation row states a duty and a benefit-side row states a
        # benefit. Where the register has one and the pass lost it in the shed
        # above, take the register's -- otherwise the row fails verify_pass for
        # a field the register can supply.
        for f in ("duty", "benefit", "value_drivers"):
            need = (f == "duty") if row.get("measure_type") == "obligation" else (f != "duty")
            if need and not row.get(f) and src.get(f):
                row[f] = src[f]

        after = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if before == after:
            untouched += 1
        else:
            touched += 1
            for f in SYNCED_FIELDS:
                if json.loads(before).get(f) != row.get(f):
                    field_counts[f] = field_counts.get(f, 0) + 1

    if write:
        pass_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return {"pass": pass_name, "rows": len(rows), "touched": touched,
            "untouched": untouched, "unmatched": unmatched, "fields": field_counts}


def main() -> int:
    write = "--check" not in sys.argv
    reports = [reanchor(p, d, s, write) for p, d, s in PAIRS]

    blocked = []
    for r in reports:
        print(f"{r['pass']}: {r['rows']} rows — {r['touched']} re-anchored, "
              f"{r['untouched']} untouched")
        for f, n in sorted(r["fields"].items()):
            print(f"    {f}: {n}")
        if r["unmatched"]:
            blocked.append((r["pass"], r["unmatched"]))

    print("\n" + ("written" if write else "check only, nothing written"))

    if blocked:
        print("\nNOT RE-ANCHORED — no register row of this id, and the row fails")
        print("the basis guardrail. These are Pass-B-only finds: provisions the")
        print("second read caught that the register does not carry. Nothing was")
        print("improvised for them; each needs a ruling (extract into the")
        print("register, or retire from the pass).")
        for name, ids in blocked:
            print(f"\n  {name} ({len(ids)}):")
            for i in sorted(ids):
                print(f"    {i}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

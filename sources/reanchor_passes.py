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

THOSE 27 HAVE NOW BEEN RULED ON, AND THE RULING IS THE CROSSWALK BELOW
======================================================================
Listing them was the right stop, and reading the list closed it: the blocker
was never that the register lacked these provisions. It is that automatic id
matching cannot see a provision the two passes named differently. Checked span
by span against the register (canonical compare, basis fields included), 22 of
the 27 are provisions the register already carries under a Pass A id -- several
of them verbatim, and three where the Pass B span IS the register row's basis
text (AVI-05 = AVI-02.opportunity_basis, FND-12 = ETSSVC-01.opportunity_basis,
NZT-09b = LM-22). The register had also already made exactly the calls the
object rule demands: FLX-01's provision is FRE-06, ruled `right`; AA-05b's is
AA-04b, ruled `right`; the NZT sourcing conditions are LM-13/LM-14/LM-22, ruled
`obligation`. Promoting any of the 22 would have entered a second row for a
provision the register states once.

The remaining 5 were genuine gaps and are now in the register, keeping the
ETSB-/IAAB- prefix this file's sibling rows already use for a Pass-B-origin
promotion (ETSB-MRV-02, IAAB-CHEM-01), with `pass_origin` recording the
lineage machine-readably.

So the crosswalk is a statement of identity -- "these two ids name one
provision" -- and nothing more. It is deliberately NOT a merge: the synced
fields are the same ones any id-matched row gets, so Pass B keeps its own span,
addressee, trigger and wording. That matters, because those are what reconcile
compares once the classification is anchored, and a crosswalk that copied them
would be the vacuous agreement verify_pass.py's docstring warns against.
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

# Pass B ids -> the register id that rules on the SAME provision.
#
# Only Pass B needs this: Pass A's ids are the register's. Every entry was
# established by canonical span comparison against the register (source_text and
# basis fields), not by article overlap -- article overlap is what fails here,
# since four register rows share "Art. 1(15)(d)".
#
# The five marked NEW are the provisions the register genuinely lacked; they
# were extracted in rather than crosswalked to something else.
PASS_B_CROSSWALK = {
    "ets_pass_b.json": {
        "ALC-01": "CBAM-01",       # Art. 10a(1a) CBAM factor schedule
        "ALC-02": "FRE-02",        # Art. 10a(3c) 80/20 tranching  (span identical)
        "ALC-03": "FRE-04",        # Art. 10a(3c) 4th subpara, IDB/IF derogation
        "ALC-04": "FRE-05",        # Art. 10a(3c) 6th subpara, top-decile exemption
        "ALC-05": "ETSB-ALC-05",   # NEW -- Art. 10b(4) other-sectors limb
        "AVI-05": "AVI-02",        # span IS AVI-02's opportunity_basis
        "AVI-06": "ETSB-AVI-06",   # NEW -- Art. 3c(8) outermost-region flights
        "CCU-01": "CCS-02",        # Art. 12(3b) CCU surrender carve-out
        "FLX-01": "FRE-06",        # Art. 10a(3d) installation pooling
        "FND-11": "FND-07",        # Art. 10d(1) Modernisation Fund
        "FND-12": "ETSSVC-01",     # span IS ETSSVC-01's opportunity_basis
        "WST-03b": "WST-03",       # Art. 12b(1) waste opt-out
        # Not one of the 27 -- it already verified, so it was never blocked. It
        # is here because it is the same kind of fact: an earlier Pass-B-origin
        # promotion whose register id the matcher cannot otherwise reach, which
        # left it reported as a coverage gap it is not.
        "MRV-02": "ETSB-MRV-02",   # Art. 12(9) CORSIA cancellation deadlines
    },
    "iaa_pass_b.json": {
        "AA-05b": "AA-04b",        # Art. 27(3) baseline-permit scope
        "AA-06": "IAAB-AA-06",     # NEW -- Art. 27(4) strategic-project status
        "CHEM-01": "IAAB-CHEM-01",  # already promoted under the IAAB- convention
        "LM-07b": "IAAB-LM-07b",   # NEW -- Art. 13 corporate-vehicles origin hook
        "LM-09b": "LM-03b",        # Annex II Part I minimum shares
        "LM-10c": "LM-06c",        # Annex II Part II household/company schemes
        "LM-11b": "LM-03c",        # Annex III Part I vehicle origin
        "NZT-01": "PRM-06",        # Art. 9(14) strategic-project status
        "NZT-02b": "LM-13",        # Art. 25(7)(a) 50% single-country cap
        "NZT-03b": "LM-14",        # Art. 25a(1) third-country exclusion
        "NZT-05b": "LM-15b",       # new Annex II Part I battery storage
        "NZT-06b": "IAAB-NZT-06b",  # NEW -- new Annex II Part II auctions
        "NZT-09b": "LM-22",        # Art. 28b high-risk suppliers (span identical)
        "NZT-10c": "LM-20b",       # new Annex II Part III household schemes
        "NZT-13b": "LM-23b",       # new Annex II Part IV electrolyser support
    },
}

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

    crosswalk = PASS_B_CROSSWALK.get(pass_name, {})
    # A crosswalk entry naming a register row that does not exist would silently
    # fall back to id matching and re-list the row as unmatched, which reads as
    # "still needs a ruling" when what actually happened is that the ruling moved.
    missing = sorted({t for t in crosswalk.values()} - set(data))
    if missing:
        raise SystemExit(
            f"reanchor: {pass_name} crosswalk points at register ids that are not "
            f"in {data_name}: {missing}. Re-check the ruling before re-anchoring."
        )

    touched, untouched, unmatched, field_counts = 0, 0, [], {}
    for row in rows:
        src = data.get(crosswalk.get(row["id"], row["id"]))
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

"""
The gate that says whether CBAM is RECONCILED, not merely built.

    python3 reconciliation_gate.py

Six checks, and it exits non-zero if any fails. verify_pass.py answers "does
this row's evidence resolve"; validate_v2.py answers "is this row well formed".
Neither answers the question this one does: has the second read actually been
disposed of, or has it just been outlived.

  1. EVERY DISAGREEMENT HAS A RULING. Read from the FROZEN docket -- the
     disagreement report exactly as reconcile.py produced it before anything was
     ruled -- not from a fresh run. A fresh run reports zero once the register is
     fixed, and would also report zero if the reconciliation had never happened,
     so it cannot distinguish the two. The frozen docket can.
  2. EVERY PASS-B-ONLY PROVISION IS PROMOTED OR REJECTED WITH A REASON. A
     promotion must be findable in the register by pass_origin; a rejection must
     carry a reason AND must actually have held -- no register row may carry the
     pass_origin of a rejected row.
  3. ALL APPLICATION DATES RECONCILED. Not "the two agree": each ruled row must
     commit to the EXACT date set the ruling names, in the register and in the
     pass alike. Two rows agreeing on the same wrong date satisfies reconcile
     and must not satisfy this.
  4. FIN-06 AND ELEC-02 CARRY THEIR CORRECTED VALENCE, with reclass_from
     recording what they said before. A correction with no audit trail is
     indistinguishable from a row that was always right.
  5. THE REGISTER PASSES THE SAME GATES AS THE OTHERS -- verify_pass against the
     live sources, validate_v2, and the valence parity check, each invoked the
     way the other three register files are.
  6. THE DERIVED LAYERS ARE REBUILT FROM THE RECONCILED FILE. The graph is
     rebuilt and must contain a measure node for every register row; every
     sector a CBAM row names must resolve in the exposure manifest.

ON CHECK 6 AND THE WORD "REBUILT". The exposure layer is NOT derived from the
register: data/exposure/*.json is FIGARO input-output data keyed by sector, an
INPUT to the graph rather than an output of the register, and no register change
can rebuild it. What is rebuilt from the reconciled file is the graph layer,
which is where register rows meet sectors and, through them, the exposure data.
So the check on exposure is a join check -- every sector a CBAM row names must
exist in the exposure manifest, or the row reaches a page that cannot show it.
Said here because "rebuild the exposure layer" is a reasonable thing to ask for
and the honest answer is that there is nothing to rebuild.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import cbam_rulings as R
from benefit_axis import FILE_SOURCES, derive_valence
from reanchor_passes import PASS_B_CROSSWALK
from reconcile import when_signature

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
DOCKET = HERE / "cbam_reconciliation_docket.json"

failures: list[str] = []
notes: list[str] = []


def check(ok: bool, label: str, detail: str = "") -> bool:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(f"{label}{': ' + detail if detail else ''}")
        if detail:
            print(f"        {detail}")
    return ok


def run(argv: list[str]) -> tuple[int, str]:
    r = subprocess.run([sys.executable, *argv], capture_output=True, text=True, cwd=HERE)
    return r.returncode, (r.stdout + r.stderr).strip()


def main() -> int:
    docket = json.loads(DOCKET.read_text(encoding="utf-8"))
    register = json.loads((DATA / "cbam.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in register}
    passb = json.loads((HERE / R.PASS_FILE).read_text(encoding="utf-8"))
    passb_by_id = {r["id"]: r for r in passb}
    crosswalk = PASS_B_CROSSWALK[R.PASS_FILE]

    # ---------------------------------------------------------------- 1
    print("\n1. EVERY DISAGREEMENT HAS A RULING")
    print(f"   docket frozen at reconciliation: {len(docket['disagreements'])} "
          f"classification, {len(docket['date_disagreements'])} date, "
          f"{len(docket['b_only'])} Pass-B-only")

    unruled = [d["a_id"] for d in docket["disagreements"] if d["a_id"] not in R.CLASSIFICATION]
    check(not unruled, "every docketed classification disagreement is ruled", str(unruled))

    unruled_d = [d["a_id"] for d in docket["date_disagreements"] if d["a_id"] not in R.DATES]
    check(not unruled_d, "every docketed date disagreement is ruled", str(unruled_d))

    # And no ruling may be invented for something never in dispute.
    docketed = {d["a_id"] for d in docket["disagreements"]}
    extra = sorted(set(R.CLASSIFICATION) - docketed)
    check(not extra, "no classification ruling without a docketed disagreement", str(extra))
    docketed_d = {d["a_id"] for d in docket["date_disagreements"]}
    extra_d = sorted(set(R.DATES) - docketed_d)
    check(not extra_d, "no date ruling without a docketed disagreement", str(extra_d))

    # The live run must now be clean, or a ruling did not take.
    rc, out = run(["reconcile.py", str(DATA / "cbam.json"), R.PASS_FILE, "cbam"])
    live = json.loads((HERE / "cbam_disagreements.json").read_text(encoding="utf-8"))
    check(rc == 0 and not live["disagreements"],
          "live reconcile reports 0 classification disagreements",
          json.dumps(live["disagreements"])[:300])
    check(not live["date_disagreements"],
          "live reconcile reports 0 date disagreements",
          json.dumps(live["date_disagreements"])[:300])

    # ---------------------------------------------------------------- 2
    print("\n2. EVERY PASS-B-ONLY PROVISION PROMOTED OR REJECTED WITH A REASON")
    unruled_b = [b["id"] for b in docket["b_only"] if b["id"] not in R.PASS_B_ONLY]
    check(not unruled_b, "every docketed Pass-B-only row is ruled", str(unruled_b))

    origins = {r.get("pass_origin"): r["id"] for r in register if r.get("pass_origin")}
    promoted, rejected = [], []
    bad = []
    for pid, ruling in R.PASS_B_ONLY.items():
        if not ruling.get("reason", "").strip():
            bad.append(f"{pid}: no reason")
            continue
        key = f"cbam_pass_b:{pid}"
        if ruling["ruling"] == "promote":
            rid = ruling["register_id"]
            if rid not in by_id:
                bad.append(f"{pid}: promoted to {rid}, which is not in the register")
            elif origins.get(key) != rid:
                bad.append(f"{pid}: {rid} does not carry pass_origin {key!r}")
            else:
                promoted.append(pid)
        elif ruling["ruling"] == "reject":
            if key in origins:
                bad.append(f"{pid}: rejected, but {origins[key]} carries its pass_origin")
            else:
                rejected.append(pid)
        else:
            bad.append(f"{pid}: unknown ruling {ruling['ruling']!r}")
    check(not bad, f"{len(promoted)} promoted with pass_origin, {len(rejected)} "
                   f"rejected with a reason and no register row", "; ".join(bad))

    # The strong claim: every row of Pass B is accounted for, by crosswalk or by
    # an explicit rejection. Nothing falls between the two.
    unaccounted = sorted(r["id"] for r in passb
                         if r["id"] not in crosswalk
                         and R.PASS_B_ONLY.get(r["id"], {}).get("ruling") != "reject")
    check(not unaccounted,
          f"all {len(passb)} Pass B rows accounted for (crosswalked or rejected)",
          str(unaccounted))

    # ---------------------------------------------------------------- 3
    print("\n3. ALL APPLICATION DATES RECONCILED")
    bad_dates = []
    for rid, ruling in R.DATES.items():
        want = set(ruling["now_signature"])
        row = by_id.get(rid)
        if row is None:
            bad_dates.append(f"{rid}: not in register")
            continue
        got = when_signature(row.get("when"))
        if got != want:
            bad_dates.append(f"{rid}: register commits to {sorted(got)}, ruling says {sorted(want)}")
            continue
        pb = passb_by_id.get(ruling["pass_id"])
        if pb is None:
            bad_dates.append(f"{rid}: pass row {ruling['pass_id']} missing")
        elif when_signature(pb.get("when")) != want:
            bad_dates.append(f"{rid}: pass row {ruling['pass_id']} commits to "
                             f"{sorted(when_signature(pb.get('when')))}")
    check(not bad_dates, f"all {len(R.DATES)} ruled dates match the ruling in BOTH "
                         "register and pass", "; ".join(bad_dates))

    # Every register row that commits to a date at all must agree with its pass
    # counterpart -- not only the ten that were in dispute.
    reverse = {v: k for k, v in crosswalk.items()}
    drift = []
    for r in register:
        pid = reverse.get(r["id"])
        if not pid or pid not in passb_by_id:
            continue
        a, b = when_signature(r.get("when")), when_signature(passb_by_id[pid].get("when"))
        if a and b and a != b:
            drift.append(f"{r['id']}/{pid}")
    check(not drift, f"all {len(register)} register rows agree with their pass "
                     "counterpart on dates", str(drift))

    # ---------------------------------------------------------------- 4
    print("\n4. FIN-06 AND ELEC-02 CARRY THEIR CORRECTED VALENCE")
    for rid, ruling in R.CLASSIFICATION.items():
        row = by_id.get(rid)
        if row is None:
            check(False, f"{rid} present", "missing from register")
            continue
        now_ok = all(row.get(k) == v for k, v in ruling["now"].items())
        rf = row.get("reclass_from") or {}
        was_ok = bool(rf) and all(rf.get(k) == v for k, v in ruling["was"].items())
        prior_ok = isinstance(row.get("prior_rule"), dict) and \
            row["prior_rule"].get("status") in ("sourced", "recital")
        label = derive_valence(row.get("measure_type"), row.get("direction"))
        was_label = derive_valence(
            ruling["was"].get("measure_type", row.get("measure_type")),
            ruling["was"].get("direction", row.get("direction")))
        check(now_ok and was_ok and prior_ok,
              f"{rid}: {was_label} -> {label}, reclass_from recorded, prior_rule resolved",
              f"now_ok={now_ok} was_ok={was_ok} prior_ok={prior_ok}")

    # ---------------------------------------------------------------- 5
    print("\n5. THE REGISTER PASSES THE SAME GATES AS THE OTHERS")
    rc, out = run(["verify_pass.py", str(DATA / "cbam.json"),
                   *FILE_SOURCES["cbam"]])
    check(rc == 0, f"verify_pass: {out.splitlines()[0] if out else ''}", out[-400:])
    rc, out = run(["validate_v2.py"])
    check(rc == 0, "validate_v2 (all four register files)", out[-400:])
    rc, out = run(["check_valence_parity.py"])
    check(rc == 0, "check_valence_parity (python/TS labels agree)", out[-400:])

    # ---------------------------------------------------------------- 6
    print("\n6. DERIVED LAYERS REBUILT FROM THE RECONCILED FILE")
    rc, out = run(["build_graph.py"])
    check(rc == 0, "build_graph rebuilt", out[-400:])
    nodes = json.loads((DATA / "graph" / "nodes.json").read_text(encoding="utf-8"))
    node_ids = {n["id"] for n in nodes}
    missing = sorted(f"measure:cbam:{r['id']}" for r in register
                     if f"measure:cbam:{r['id']}" not in node_ids)
    check(not missing, f"graph carries a measure node for all {len(register)} CBAM rows",
          str(missing[:8]))

    manifest = json.loads((DATA / "exposure" / "_manifest.json").read_text(encoding="utf-8"))
    used = {s for r in register for s in r.get("sectors_named", []) + r.get("sectors_reached", [])}
    unresolved = sorted(used - set(manifest))
    check(not unresolved, f"all {len(used)} sectors named by CBAM rows resolve in the "
                          "exposure manifest", str(unresolved))

    # ---------------------------------------------------------------- verdict
    print()
    if failures:
        print(f"NOT RECONCILED — {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"CBAM RECONCILED. {len(register)} register rows, {len(passb)} Pass B rows, "
          f"{len(R.CLASSIFICATION)} classification and {len(R.DATES)} date disagreements "
          f"ruled, {len(promoted)} promotions, {len(rejected)} rejection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
The gate that says whether a register file is RECONCILED, not merely built.

    python3 reconciliation_gate.py            # every file with a ruling ledger
    python3 reconciliation_gate.py cbam       # one of them
    python3 reconciliation_gate.py nzia

It was written for CBAM, which was the only file with a second read that had
been ruled on. NZIA now has one too, so the six checks below are driven by a
FILES table -- ruling ledger, frozen docket, register file -- rather than by
CBAM constants. Adding a third file is adding a row to that table.

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
  4. EVERY CLASSIFICATION RULING IS EVIDENCED IN THE ROW. A ruling for the
     second pass means the row MOVED, so it must carry reclass_from recording
     what it said before -- a correction with no audit trail is
     indistinguishable from a row that was always right. A ruling for the FIRST
     pass means nothing moved, so the row must still say what the ruling
     records AND must NOT carry reclass_from: inventing an audit trail for a
     correction that never happened is the same failure in the other
     direction. CBAM's twelve all went to Pass B; NZIA's three all went to
     Pass A, which is why this check now has to state both halves.
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

A seventh check runs once for the whole suite rather than per file: the
findings layer (build_findings.py) must resolve every published claim against
the register as it now stands. It is not a per-file check because a finding
cites rows across files.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import cbam_rulings
import crma_rulings
import nzia_rulings
from benefit_axis import FILE_SOURCES, derive_valence, is_deletion_amendment
from reanchor_passes import PASS_B_CROSSWALK
from reconcile import when_signature

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# One row per file that has a second read AND a ruling ledger disposing of it.
# A file with a Pass B and no ledger does not belong here: the gate would have
# nothing to check the pass against, and "reconciled" would mean "compared".
FILES = {
    "cbam": dict(rulings=cbam_rulings, docket="cbam_reconciliation_docket.json"),
    "nzia": dict(rulings=nzia_rulings, docket="nzia_reconciliation_docket.json"),
    "crma": dict(rulings=crma_rulings, docket="crma_reconciliation_docket.json"),
}

# Files that have been read ONCE. They cannot pass the six checks -- there is
# no second pass to check anything against -- and the point of listing them is
# that silence would be indistinguishable from reconciliation. A reader of this
# report has to be able to see which files are standing on one read.
SINGLE_PASS = {
    "ppwr": "ppwr_reconciliation_docket.json",
}

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


def gate(key: str) -> tuple[int, str]:
    """Run the six checks for one file. Returns (failures_before, verdict line)."""
    spec = FILES[key]
    R = spec["rulings"]
    docket = json.loads((HERE / spec["docket"]).read_text(encoding="utf-8"))
    register = json.loads((DATA / f"{key}.json").read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in register}
    passb = json.loads((HERE / R.PASS_FILE).read_text(encoding="utf-8"))
    passb_by_id = {r["id"]: r for r in passb}
    crosswalk = PASS_B_CROSSWALK[R.PASS_FILE]
    origin_prefix = R.PASS_FILE.removesuffix(".json")

    print(f"\n{'=' * 70}\n{key.upper()}\n{'=' * 70}")

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

    # THE LIVE RUN. A ruling FOR PASS B moves the register, so that disagreement
    # disappears from a fresh run. A ruling FOR PASS A does not: the pass still
    # says what it said, and reconcile.py will report that pair for as long as
    # both files exist. So the live run is not required to be empty -- it is
    # required to contain nothing that has not been ruled, and nothing that was
    # ruled for Pass B. A standing disagreement is a recorded decision; an
    # unrecorded one is the failure this gate exists to catch.
    rc, out = run(["reconcile.py", str(DATA / f"{key}.json"), R.PASS_FILE, key])
    live = json.loads((HERE / f"{key}_disagreements.json").read_text(encoding="utf-8"))
    held_for_a = {rid for rid, v in R.CLASSIFICATION.items() if v["ruling"] == "pass_a"}
    live_ids = {d["a_id"] for d in live["disagreements"]}
    check(rc == 0 and live_ids <= held_for_a,
          f"live reconcile reports only the {len(held_for_a)} disagreement(s) ruled for Pass A",
          json.dumps(sorted(live_ids - held_for_a))[:300])
    check(not live["date_disagreements"],
          "live reconcile reports 0 date disagreements",
          json.dumps(live["date_disagreements"])[:300])

    # ---------------------------------------------------------------- 2
    print("\n2. EVERY PASS-B-ONLY PROVISION PROMOTED OR REJECTED WITH A REASON")
    unruled_b = [b["id"] for b in docket["b_only"] if b["id"] not in R.PASS_B_ONLY]
    check(not unruled_b, "every docketed Pass-B-only row is ruled", str(unruled_b))

    # A ruling in PASS_B_ONLY for a row that was NOT docketed as B-only is
    # allowed in exactly one case: it was docketed as a classification
    # disagreement and the ruling both kept Pass A's reading and promoted the
    # pass row as the other half of the provision. Anything else is a ruling
    # invented for a row nobody disputed.
    docketed_b = {b["id"] for b in docket["b_only"]}
    classification_pass_ids = {v["pass_id"] for v in R.CLASSIFICATION.values()}
    stray = sorted(set(R.PASS_B_ONLY) - docketed_b - classification_pass_ids)
    check(not stray, "no Pass-B-only ruling without a docketed row", str(stray))

    origins = {r.get("pass_origin"): r["id"] for r in register if r.get("pass_origin")}
    promoted, rejected, bad = [], [], []
    for pid, ruling in R.PASS_B_ONLY.items():
        if not ruling.get("reason", "").strip():
            bad.append(f"{pid}: no reason")
            continue
        key_origin = f"{origin_prefix}:{pid}"
        if ruling["ruling"] == "promote":
            rid = ruling["register_id"]
            if rid not in by_id:
                bad.append(f"{pid}: promoted to {rid}, which is not in the register")
            elif origins.get(key_origin) != rid:
                bad.append(f"{pid}: {rid} does not carry pass_origin {key_origin!r}")
            else:
                promoted.append(pid)
        elif ruling["ruling"] == "reject":
            if key_origin in origins:
                bad.append(f"{pid}: rejected, but {origins[key_origin]} carries its pass_origin")
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

    # A date the second pass never saw, moved because the provision's OTHER half
    # moved. It has no pass counterpart to check against, so what is checked is
    # the register row and the row it follows -- which must now say the same
    # thing, that being the whole reason the ruling exists.
    consequential = getattr(R, "CONSEQUENTIAL_DATES", {})
    bad_cons = []
    for rid, ruling in consequential.items():
        row, other = by_id.get(rid), by_id.get(ruling["follows"])
        if row is None or other is None:
            bad_cons.append(f"{rid}: row or its antecedent missing")
            continue
        want = set(ruling["now_signature"])
        if when_signature(row.get("when")) != want:
            bad_cons.append(f"{rid}: commits to {sorted(when_signature(row.get('when')))}")
        elif when_signature(other.get("when")) != want:
            bad_cons.append(f"{rid}: antecedent {ruling['follows']} disagrees")
        elif row.get("provision_id") != other.get("provision_id"):
            bad_cons.append(f"{rid}: not on the same provision_id as {ruling['follows']}")
    if consequential:
        check(not bad_cons, f"all {len(consequential)} consequential date(s) match the row "
                            "they follow, on one provision_id", "; ".join(bad_cons))

    # Every register row that commits to a date at all must agree with its pass
    # counterpart -- not only the ones that were in dispute.
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
    print("\n4. EVERY CLASSIFICATION RULING IS EVIDENCED IN THE ROW")
    for rid, ruling in R.CLASSIFICATION.items():
        row = by_id.get(rid)
        if row is None:
            check(False, f"{rid} present", "missing from register")
            continue
        now_ok = all(row.get(k) == v for k, v in ruling["now"].items())
        rf = row.get("reclass_from") or {}
        label = derive_valence(row.get("measure_type"), row.get("direction"))

        if ruling["ruling"] == "pass_b":
            # The row moved. It must say so.
            was_ok = bool(rf) and all(rf.get(k) == v for k, v in ruling["was"].items())
            # A deletion row's before-state has to be legible too -- but only a
            # deletion row has one, so this is asked of the rows that have to
            # answer it rather than of every corrected row.
            prior_ok = (not is_deletion_amendment(row)) or (
                isinstance(row.get("prior_rule"), dict)
                and row["prior_rule"].get("status") in ("sourced", "recital"))
            was_label = derive_valence(
                ruling["was"].get("measure_type", row.get("measure_type")),
                ruling["was"].get("direction", row.get("direction")))
            check(now_ok and was_ok and prior_ok,
                  f"{rid}: {was_label} -> {label}, reclass_from recorded"
                  + (", prior_rule resolved" if is_deletion_amendment(row) else ""),
                  f"now_ok={now_ok} was_ok={was_ok} prior_ok={prior_ok}")
        else:
            # Pass A held. Nothing moved, so nothing may claim it did.
            check(now_ok and not rf,
                  f"{rid}: {label} held against the second read, no reclass_from",
                  f"now_ok={now_ok} reclass_from={rf or None}")

    # ---------------------------------------------------------------- 5
    print("\n5. THE REGISTER PASSES THE SAME GATES AS THE OTHERS")
    rc, out = run(["verify_pass.py", str(DATA / f"{key}.json"), *FILE_SOURCES[key]])
    check(rc == 0, f"verify_pass: {out.splitlines()[0] if out else ''}", out[-400:])
    rc, out = run(["validate_v2.py"])
    check(rc == 0, "validate_v2 (every register file)", out[-400:])
    rc, out = run(["check_valence_parity.py"])
    check(rc == 0, "check_valence_parity (python/TS labels agree)", out[-400:])

    # ---------------------------------------------------------------- 6
    print("\n6. DERIVED LAYERS REBUILT FROM THE RECONCILED FILE")
    rc, out = run(["build_graph.py"])
    check(rc == 0, "build_graph rebuilt", out[-400:])
    nodes = json.loads((DATA / "graph" / "nodes.json").read_text(encoding="utf-8"))
    node_ids = {n["id"] for n in nodes}
    missing = sorted(f"measure:{key}:{r['id']}" for r in register
                     if f"measure:{key}:{r['id']}" not in node_ids)
    check(not missing, f"graph carries a measure node for all {len(register)} {key.upper()} rows",
          str(missing[:8]))

    # THE JOIN CHECK, AND THE THREE SLUGS THAT LEGITIMATELY DO NOT JOIN.
    # batsol, clean and ccs are policy categories, not FIGARO industries, so
    # data/exposure/ has no file for them by construction -- build_graph.SECTORS
    # says so in its own comment. CBAM names none of them and passed a bare
    # manifest check; NZIA names all three, and failing it for that would be the
    # gate reporting a fact about the exposure layer as a defect in the register.
    # So what is checked is the app's sector VOCABULARY -- an unknown slug is a
    # row pointing at a page that does not exist, and still fails -- and the
    # economic join is reported as a note.
    from build_graph import SECTORS as APP_SECTORS
    manifest = json.loads((DATA / "exposure" / "_manifest.json").read_text(encoding="utf-8"))
    used = {s for r in register for s in r.get("sectors_named", []) + r.get("sectors_reached", [])}
    unknown_slugs = sorted(used - set(APP_SECTORS))
    check(not unknown_slugs, f"all {len(used)} sectors named by {key.upper()} rows are in the "
                             "app sector vocabulary", str(unknown_slugs))
    no_exposure = sorted(used - set(manifest))
    if no_exposure:
        notes.append(f"{key}: {len(no_exposure)} sector(s) carry no FIGARO exposure file "
                     f"({', '.join(no_exposure)}) — policy categories, not industries")
        print(f"  NOTE  {no_exposure} have no exposure file: policy categories, not FIGARO "
              "industries")

    held = sum(1 for v in R.CLASSIFICATION.values() if v["ruling"] == "pass_a")
    verdict = (f"{key.upper()} RECONCILED. {len(register)} register rows, {len(passb)} Pass B "
               f"rows, {len(R.CLASSIFICATION)} classification ({held} held for Pass A) and "
               f"{len(R.DATES)} date disagreements ruled, {len(promoted)} promotions, "
               f"{len(rejected)} rejections.")
    return len(failures), verdict


def main() -> int:
    keys = [a for a in sys.argv[1:] if not a.startswith("-")] or list(FILES)
    unknown = [k for k in keys if k not in FILES]
    if unknown:
        sys.exit(f"no ruling ledger for: {unknown}. Known: {list(FILES)}")

    verdicts = []
    for k in keys:
        before = len(failures)
        _, verdict = gate(k)
        verdicts.append((k, verdict, len(failures) == before))

    # THE FINDINGS LAYER. Run once, after the files, rather than inside gate():
    # a finding cites rows across several register files, so it can only be
    # checked against the whole register, and running it per key would ask the
    # same question three times. It is here because a finding is the only thing
    # on the site that restates the register in its own words -- if a ruling
    # moved a row out from under a published claim, this is where that shows up.
    # SINGLE-PASS FILES. Not a verdict on quality -- a statement of standing.
    # The only thing checkable here is that the declaration matches the file it
    # describes, so a docket cannot go stale while the register moves under it.
    single_pass_lines = []
    for key, docket_name in sorted(SINGLE_PASS.items()):
        print(f"\nSINGLE-PASS FILE: {key}")
        docket = json.loads((HERE / docket_name).read_text(encoding="utf-8"))
        rows = json.loads((DATA / f"{key}.json").read_text(encoding="utf-8"))
        check(docket.get("reconciled") is False,
              f"{key}: docket declares the file NOT reconciled")
        ok = check(docket.get("register_rows") == len(rows),
                   f"{key}: docket row count matches the register file",
                   f"docket says {docket.get('register_rows')}, file has {len(rows)}")
        for q in docket.get("known_open_questions", []):
            print(f"        open: {q.split('.')[0][:88]}")
        for r in docket.get("resolved_since_first_publication", []):
            print(f"        closed: {r.split('—')[0].strip()}")
        single_pass_lines.append(
            f"{key.upper()} NOT RECONCILED — single-pass, {len(rows)} register rows, "
            f"{len(docket.get('known_open_questions', []))} open question(s). "
            f"Read once on {docket.get('declared_at')}; every classification is unconfirmed."
            if ok else f"{key.upper()} single-pass docket does not match the register file.")

    # SECTOR COVERAGE. --strict fails only on a SUSPECTED GAP: a FIGARO-backed
    # sector that no business duty reaches. An expected-sectorless slug is a
    # policy category with no industry behind it and must not fail anything --
    # that distinction is the whole reason the report has two buckets.
    print("\nSECTOR COVERAGE")
    rc, out = run(["sector_coverage.py", "--strict"])
    tail = [l for l in out.splitlines() if l.startswith(("EXPECTED SECTORLESS", "SUSPECTED GAPS"))]
    check(rc == 0, f"sector_coverage: no suspected gaps ({'; '.join(tail)})", out[-500:])

    print("\n7. THE FINDINGS LAYER RESOLVES AGAINST THE REGISTER")
    rc, out = run(["build_findings.py"])
    check(rc == 0, f"build_findings: {out.strip().splitlines()[0] if out.strip() else ''}",
          out[-600:])

    print()
    if failures:
        print(f"NOT RECONCILED — {len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1
    for n in notes:
        print(f"note: {n}")
    if notes:
        print()
    for _, verdict, _ok in verdicts:
        print(verdict)
    for line in single_pass_lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())

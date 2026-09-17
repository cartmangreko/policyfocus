#!/usr/bin/env python3
"""THE 2023-POPULATION TEST'S RECONCILIATION GATE. Fails the build; runs in the prebuild
chain.

    python3 sources/check_hydrogen_test.py      # 0 clean, 1 the test file is wrong

WHAT IT CHECKS, AND WHY EACH CHECK IS HERE RATHER THAN IN A READING.

  THE POPULATION IS THE ONE THE BRIEF NAMES: the 255 European entries at 100 MW and above
  in the October 2023 vintage. Recounted from the cached workbook where it is on the
  machine, and otherwise reconciled against the figure `benchmark_snapshots.json` records
  for the file its sha256 identifies -- never read back out of the summary the builder
  wrote, which would check a file against itself.

  EVERY RUNG CELL CARRIES A SOURCE AND A DATE OR IS `unread`, which is check_ladder's rule
  and the h2v-fos error's legacy: a result resting on nothing looks exactly like a finding.
  AND A PASS OR A FAIL IS DATED AT OR BEFORE THE CUT-OFF, which is D-B11 made mechanical.
  A `not_searched` cell is exempt because it cites the too-new document that made it one.

  EVERY OUTCOME IS ONE OF THE SIX FROZEN VALUES AND CARRIES A SPEAKER, A SOURCE AND A
  DATE unless it is `unread` -- because `unread` is the value whose whole content is that
  there is no document. `not_read_yet` is refused: it is the builder's placeholder for an
  entry nobody has read, and a committed table full of them would publish a test that was
  never run.

  THE TWO COMPUTABLE OUTCOMES ARE RECOMPUTED FROM THE COLUMNS. `pending` and `delayed`
  differ by one comparison -- the announced start against the assessment date -- and that
  comparison is in scope.md, frozen at 58ce11f. So the gate does it again from the line's
  own `announced_start`, and a line whose value does not follow from its own columns fails.
  THIS IS THE FREEZE MADE MECHANICAL. A definition fixed by commit hash and enforced by
  nothing is a definition that drifts in the reading; four of the six values need a
  document read by a person, and these two do not, so these two are checked.

  A PAUSE WITH A RESUMPTION DATE IS NOT A STOP. scope.md's pause clause is the one place
  the outcome vocabulary and the register's status vocabulary disagree on purpose, so it
  is the clause most likely to be applied loosely, and it is checked both ways.

  AND `dropped_from_benchmark` IS NEVER AN OUTCOME. Rule 17 and the covariate ruling: a
  database that drops an entry has said something about the database. The gate refuses the
  word in the outcome column.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_test as T  # noqa: E402
import build_ladder as L  # noqa: E402

OUTCOMES = ("operating", "committed", "pending", "delayed", "stopped", "unread")
SNAPSHOT = L.ROOT / "sources" / "benchmark_snapshots.json"
VINTAGE_FILE = "ou_quality_checked_2023.xlsx"


def snapshot_population():
    """The 100 MW population recorded against the 2023 workbook's sha256, read out of the
    `entry_list` line rather than stored twice."""
    doc = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    for s in doc["snapshots"]:
        if s.get("file") == VINTAGE_FILE:
            m = re.search(r"(\d+) of those are at or above 100 MW",
                          s.get("entry_list", ""))
            return int(m.group(1)) if m else None
    return None


def vintage_cached() -> bool:
    """Is the workbook on this machine, AND is it the file the snapshot names?"""
    doc = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    want = next((s.get("sha256") for s in doc["snapshots"]
                 if s.get("file") == VINTAGE_FILE), None)
    path = T.t23.VINTAGE
    if not path.exists() or not want:
        return False
    return hashlib.sha256(path.read_bytes()).hexdigest() == want


def main() -> int:
    if not T.CSV_OUT.exists() or not T.JSON_OUT.exists():
        print("check_hydrogen_test: the test has not been built. Run "
              "build_hydrogen_test.py.")
        return 1

    lines = list(csv.DictReader(T.CSV_OUT.open(encoding="utf-8")))
    summary = json.loads(T.JSON_OUT.read_text(encoding="utf-8"))
    bad = []

    # 1. THE POPULATION.
    recorded = snapshot_population()
    if vintage_cached():
        want = len(T.t23.population())
        mode = "recounted from the cached October 2023 workbook"
        if recorded is not None and want != recorded:
            bad.append(f"the cached workbook yields {want} entries at or above 100 MW; "
                       f"benchmark_snapshots.json records {recorded} for the file its "
                       f"sha256 identifies")
    elif recorded is not None:
        want = recorded
        mode = ("reconciled against benchmark_snapshots.json; the workbook is not cached, "
                "so membership is unchecked")
    else:
        want, mode = None, "not reconcilable"
        bad.append("no 100 MW population recorded on the 2023 snapshot and no cached "
                   "workbook to recount: the population cannot be reconciled")
    if want is not None and len(lines) != want:
        bad.append(f"the table has {len(lines)} lines against a population of {want}")
    refs = [l["iea_ref"] for l in lines]
    if len(set(refs)) != len(refs):
        dup = sorted({r for r in refs if refs.count(r) > 1})
        bad.append(f"{len(dup)} duplicate references: {', '.join(dup[:5])}")

    # 2. EVERY RUNG CELL.
    for l in lines:
        for r in L.RUNGS:
            res = l[f"{r}_result"]
            if res not in ("pass", "fail", "unread", "not_searched"):
                bad.append(f"ref {l['iea_ref']} rung {r}: {res!r} is not in the "
                           f"vocabulary")
                continue
            if res == "unread":
                continue
            if not l[f"{r}_source"].strip():
                bad.append(f"ref {l['iea_ref']} rung {r}: {res} with nothing cited")
            if not l[f"{r}_date"].strip():
                bad.append(f"ref {l['iea_ref']} rung {r}: {res} with no date")
            # A PASS OR A FAIL IS DATED AT OR BEFORE THE CUT-OFF; A `not_searched` IS
            # NOT, AND THAT IS THE POINT OF IT. apply_cutoff turns a cell resting on a
            # later document into `not_searched` and leaves the later document cited, so
            # a reader can see WHICH document was too new. Checking the date on those
            # would be the gate refusing the record of its own rule.
            if res in ("pass", "fail") and l[f"{r}_date"].strip() > T.CUTOFF:
                bad.append(f"ref {l['iea_ref']} rung {r}: {res} on a document dated "
                           f"{l[f'{r}_date']}, after the {T.CUTOFF} cut-off")

    # 3. EVERY OUTCOME.
    for l in lines:
        o = l["outcome"]
        if o not in OUTCOMES:
            bad.append(f"ref {l['iea_ref']}: outcome {o!r} is not one of the six frozen "
                       f"values")
            continue
        if o == "unread":
            continue
        for f in ("outcome_speaker", "outcome_source", "outcome_date"):
            if not l[f].strip():
                bad.append(f"ref {l['iea_ref']}: outcome {o} with no {f[8:]}")
        if l["outcome_speaker"].strip() and l["outcome_speaker"] not in (
                "owner", "permit", "regulator"):
            bad.append(f"ref {l['iea_ref']}: outcome speaker "
                       f"{l['outcome_speaker']!r} is not the owner, a permit authority "
                       f"or a regulator")

    # 4. THE TWO COMPUTABLE OUTCOMES, RECOMPUTED.
    for l in lines:
        y = T.start_year(l["announced_start"])
        if l["outcome"] == "pending":
            # AN ENTRY WITH NO ANNOUNCED START AT ALL IS THE ONE CASE THE FROZEN
            # DEFINITIONS DO NOT COVER, and the gate makes the gap visible rather than
            # closing it. `pending` and `delayed` are both defined against an announced
            # start, and six entries have none: the vintage gives them no date online and
            # no owner stated one at or before the cut-off. They are read as pending --
            # nothing has been promised by a day that has passed -- and what the gate
            # enforces is that the ABSENCE IS RECORDED on the line, in
            # `announced_start_read_from`, rather than assumed by whoever filled the
            # column. The question goes to the questions file as Q13; the definition is
            # not amended here, because D-C1 says it is not amended in this brief.
            if y is None and not l["announced_start_read_from"].startswith("neither"):
                bad.append(f"ref {l['iea_ref']}: pending with no announced start to be "
                           f"pending against, and no record that neither speaker "
                           f"states one")
            elif f"{y}-01-01" <= T.ASSESSED_ON and l["announced_start_precision"] == "year":
                bad.append(f"ref {l['iea_ref']}: pending on an announced start of "
                           f"{l['announced_start']}, which is on or before "
                           f"{T.ASSESSED_ON} under the padding rule")
        if l["outcome"] == "delayed":
            if y is None:
                bad.append(f"ref {l['iea_ref']}: delayed with no announced start to be "
                           f"late against")
            elif f"{y}-01-01" > T.ASSESSED_ON:
                bad.append(f"ref {l['iea_ref']}: delayed on an announced start of "
                           f"{l['announced_start']}, which is after {T.ASSESSED_ON}")

    # 5. THE PAUSE CLAUSE, BOTH WAYS.
    for l in lines:
        if l["paused"] == "yes" and l["resumption_date"].strip() \
                and l["outcome"] == "stopped":
            bad.append(f"ref {l['iea_ref']}: stopped on a pause that states a resumption "
                       f"date of {l['resumption_date']}; scope.md counts that pause as "
                       f"not stopped")
        if l["resumption_date"].strip() and l["paused"] != "yes":
            bad.append(f"ref {l['iea_ref']}: a resumption date on an entry not recorded "
                       f"as paused")

    # 6. THE COVARIATE IS NOT AN OUTCOME.
    for l in lines:
        if l["dropped_from_benchmark"] not in ("yes", "no"):
            bad.append(f"ref {l['iea_ref']}: dropped_from_benchmark is "
                       f"{l['dropped_from_benchmark']!r}")
        if "dropped" in l["outcome"]:
            bad.append(f"ref {l['iea_ref']}: dropped_from_benchmark has been written "
                       f"into the outcome column, which rule 17 forbids")

    # 7. THE COVERAGE FLAG AGREES WITH THE DOCUMENT COUNT.
    for l in lines:
        n = int(l["documents_pre_cutoff"] or 0)
        cov = l["coverage"]
        if n == 0 and not (cov.startswith("no document")
                           or cov.startswith("owner or permit document held under")):
            bad.append(f"ref {l['iea_ref']}: no pre-cut-off document but coverage says "
                       f"{cov!r}")
        if n and cov.startswith("no document"):
            bad.append(f"ref {l['iea_ref']}: {n} pre-cut-off document(s) but coverage "
                       f"says {cov!r}")
        if cov == "owner or permit document at or before the cut-off" and not n:
            bad.append(f"ref {l['iea_ref']}: an owner or permit document and no "
                       f"pre-cut-off document count")
        if cov.startswith("owner or permit document held under another") and n:
            bad.append(f"ref {l['iea_ref']}: coverage says the document is held under "
                       f"another entry's legs, but this entry has {n} of its own")

    # 8. THE SUMMARY IS THE CSV'S OWN ARITHMETIC.
    recomputed = T.summarise(None, lines, T.check_block())
    for field in ("population", "coverage", "rungs_cleared_against_outcome",
                  "each_rung_against_outcome", "status_2023_against_outcome",
                  "rungs_cleared_against_dropped_from_benchmark",
                  "outcome_of_covered_against_uncovered", "independent_check"):
        if json.dumps(summary.get(field), sort_keys=True) != \
                json.dumps(recomputed.get(field), sort_keys=True):
            bad.append(f"summary {field} does not match the csv it is computed from")

    if bad:
        print(f"check_hydrogen_test: {len(bad)} problem(s).\n")
        for b in bad[:40]:
            print(f"  {b}")
        if len(bad) > 40:
            print(f"  ... and {len(bad) - 40} more")
        return 1
    print(f"check_hydrogen_test: {len(lines)} lines, every rung cell sourced and dated "
          f"at or before {T.CUTOFF},\n  every outcome one of the six frozen values, the "
          f"two computable ones recomputed,\n  summary equal to the csv. Population "
          f"{mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""THE LADDER'S RECONCILIATION GATE. Fails the build; runs in the prebuild chain.

    python3 sources/check_ladder.py         # 0 clean, 1 the ladder is wrong

TWO CHECKS, AND THE h2v-fos ERROR IS WHY THERE ARE ANY.

  THE POPULATION IS THE ONE THE RULE NAMES. It must equal the current IEA vintage
  plus the register rows not on that list, recomputed here from the same files the
  builder read -- not read back out of the summary the builder wrote, which would
  check the file against itself.

  EVERY RUNG CELL CARRIES A SOURCE OR IS `unread`. A result with nothing cited is
  the shape that let a hand-typed h2v-fos line survive three readings: it looked
  like a finding and rested on nothing. There are six cells on each of 245 lines
  and no person is going to re-read them, so the gate does.

AND THE SUMMARY IS RECOMPUTED FROM THE CSV. The two files are published together
and a reader will quote whichever they open first; if they can disagree, one of
them is wrong and nobody will know which.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ladder as L  # noqa: E402


def snapshot_population():
    """The entry count recorded against the IEA file's sha256, read out of the
    `entry_list` line rather than stored twice."""
    doc = json.loads((L.ROOT / "sources" / "benchmark_snapshots.json")
                     .read_text(encoding="utf-8"))
    for s in doc["snapshots"]:
        if s.get("file") == "iea_live_projects.json":
            m = re.search(r"(\d+) European entries", s.get("entry_list", ""))
            return int(m.group(1)) if m else None
    return None


def benchmark_cached() -> bool:
    """Is the benchmark on this machine, AND is it the file the snapshot names?

    A cache that does not match the recorded sha256 is not used to recount: it would
    silently move the population to whatever happened to be downloaded.
    """
    path = L.ROOT / "sources" / "cache" / "hydrogen" / "iea_live_projects.json"
    if not path.exists():
        return False
    doc = json.loads((L.ROOT / "sources" / "benchmark_snapshots.json")
                     .read_text(encoding="utf-8"))
    want = next((s.get("sha256") for s in doc["snapshots"]
                 if s.get("file") == "iea_live_projects.json"), None)
    return hashlib.sha256(path.read_bytes()).hexdigest() == want


def main() -> int:
    if not L.CSV.exists() or not L.SUMMARY.exists():
        print("check_ladder: the ladder has not been built. Run build_ladder.py.")
        return 1

    lines = list(csv.DictReader(L.CSV.open(encoding="utf-8")))
    summary = json.loads(L.SUMMARY.read_text(encoding="utf-8"))
    bad = []

    # 1. THE POPULATION. TWO MODES, because the benchmark's bytes are not
    #    redistributable and the cache is gitignored, so on a build server there is
    #    no file to recount. Which mode ran is printed; a silent fallback would be a
    #    gate that passes for a reason nobody can see.
    recorded, mode = snapshot_population(), ""
    iea_lines = [l for l in lines if l["key"].startswith("iea:")]
    row_lines = [l for l in lines if l["key"].startswith("row:")]

    if benchmark_cached():
        iea, _rows, _by_ref, offlist = L.population()
        mode = "recounted from the cached benchmark"
        if recorded is not None and len(iea) != recorded:
            bad.append(f"the cached benchmark yields {len(iea)} European entries at "
                       f"or above the threshold; benchmark_snapshots.json records "
                       f"{recorded} for the file its sha256 identifies. The cache has "
                       f"drifted from the snapshot, or the snapshot is stale")
        want = len(iea) + len(offlist)
        if len(lines) != want:
            bad.append(f"population is {len(lines)} lines; the current IEA vintage "
                       f"({len(iea)}) plus register rows not on it ({len(offlist)}) "
                       f"is {want}")
        if len(iea_lines) != len(iea):
            bad.append(f"{len(iea_lines)} benchmark lines against {len(iea)} entries")
        if len(row_lines) != len(offlist):
            bad.append(f"{len(row_lines)} off-list row lines against {len(offlist)}")
    else:
        # WITHOUT THE FILE, THE SIZE IS CHECKED AND THE MEMBERSHIP IS NOT, and that
        # is said rather than glossed. The recorded figure is a measurement of the
        # file the snapshot's sha256 identifies, not a number typed here.
        mode = ("reconciled against benchmark_snapshots.json; the benchmark is not "
                "cached, so membership is unchecked")
        if recorded is None:
            bad.append("no population recorded on the IEA snapshot and no cached "
                       "benchmark to recount: the population cannot be reconciled")
        elif len(iea_lines) != recorded:
            bad.append(f"{len(iea_lines)} benchmark lines; benchmark_snapshots.json "
                       f"records {recorded} entries for that vintage")
        offlist_ids = {l["row_id"] for l in row_lines}
        held = set()
        for l in iea_lines:
            if l["row_id"]:
                held.add(l["row_id"])
        clean = {p["id"] for p in L.sm.load("project") if p.get("sector") == "clean"}
        if offlist_ids | held != clean:
            missing = sorted(clean - (offlist_ids | held))
            extra = sorted((offlist_ids | held) - clean)
            bad.append(f"the ladder's rows do not cover the register's clean rows: "
                       f"{len(missing)} missing, {len(extra)} not in the register")
    keys = [l["key"] for l in lines]
    if len(set(keys)) != len(keys):
        dup = sorted({k for k in keys if keys.count(k) > 1})
        bad.append(f"{len(dup)} duplicate keys: {', '.join(dup[:5])}")

    # 2. EVERY CELL: A RESULT FROM THE VOCABULARY, AND A SOURCE UNLESS UNREAD.
    for l in lines:
        for r in L.RUNGS:
            res = l[f"{r}_result"]
            if res not in ("pass", "fail", "unread", "not_searched"):
                bad.append(f"{l['key']} rung {r}: result {res!r} is not in the "
                           f"vocabulary")
                continue
            if res == "unread":
                continue
            # `not_searched` STILL CITES WHAT WAS NOT SEARCHED. Added 15 September
            # 2026 with the searched flag: the cell says which source class the
            # rung reads and records that it was not examined for this entry, so
            # it carries a source and a date like any other non-unread cell.
            # A FAIL AND A not_searched ARE DIFFERENT FINDINGS: the first is about
            # the project, the second about this register's reading.
            if res == "not_searched" and l.get(f"{r}_searched") != "false":
                bad.append(f"{l['key']} rung {r}: not_searched with searched!=false")
            if not l[f"{r}_source"].strip():
                bad.append(f"{l['key']} rung {r}: {res} with nothing cited")
            if not l[f"{r}_date"].strip():
                bad.append(f"{l['key']} rung {r}: {res} with no date")

    # 3. UNREAD IS ALL SIX OR NONE. A partly-unread line would mean the ladder had
    #    scored an entry whose sources it could not read, which the rule forbids.
    for l in lines:
        n = sum(1 for r in L.RUNGS if l[f"{r}_result"] == "unread")
        if n not in (0, len(L.RUNGS)):
            bad.append(f"{l['key']}: {n} of {len(L.RUNGS)} rungs unread; an "
                       f"unreadable entry is unread on every rung")
        if (l["unread"] == "true") != (n == len(L.RUNGS)):
            bad.append(f"{l['key']}: the unread column disagrees with its cells")

    # 4. THE SUMMARY IS THE CSV'S OWN ARITHMETIC.
    recomputed = L.summarise(lines)
    for field in ("population", "entries_by_rungs_passed",
                  "pass_count_per_rung_by_register_class",
                  "rungs_passed_by_iea_status", "rung6_provisional",
                  "unread_entries"):
        if summary.get(field) != recomputed.get(field):
            bad.append(f"summary {field} does not match the csv it is computed from")

    # 5. RUNGS ARE INDEPENDENT, so monotonicity is NOT checked. Recorded here so the
    #    absence reads as a decision rather than an oversight: a line passing rung 5
    #    and failing rung 2 is a finding, and a gate that rejected it would be
    #    enforcing a ladder nobody ruled.

    if bad:
        print(f"check_ladder: {len(bad)} problem(s).\n")
        for b in bad[:40]:
            print(f"  {b}")
        if len(bad) > 40:
            print(f"  ... and {len(bad) - 40} more")
        return 1
    print(f"check_ladder: {len(lines)} lines, every rung cell sourced or unread, "
          f"summary recomputed and equal.\n  population {mode}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

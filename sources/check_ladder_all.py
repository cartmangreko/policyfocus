#!/usr/bin/env python3
"""THE CROSS-SECTOR LADDER'S RECONCILIATION GATE, brief 11. Fails the build.

    python3 sources/check_ladder_all.py     # 0 clean, 1 the ladder is wrong

FOUR CHECKS.

  THE SIX RUNG TESTS ARE THE FROZEN ONES. `### The six rungs` in sources/scope.md
  must hash to the value it had at the D-B1 freeze, commit a9542fe. D-B1 froze the
  tests in prose and D-A1 re-anchored the freeze on this block; prose does not fail
  a build, and this does. A reading added under the frozen test changes the SECTION
  and must not change the BLOCK.

  EVERY POPULATION'S IDENTITY HOLDS. Scored + perimeter exclusions + unread +
  benchmark aggregates = the population, per sector, recomputed from the csv's own
  lines rather than read back out of the summary.

  EVERY RUNG CELL CARRIES A SOURCE OR IS `unread`. Six cells on each of 644 lines
  and no person is going to re-read them. The h2v-fos error is why the gate exists:
  a hand-typed line that looked like a finding and rested on nothing.

  AND HYDROGEN RECONCILES LINE BY LINE with sources/ladder/hydrogen.csv, which the
  brief asks for in as many words. The two files are written by different code
  paths — brief 10's scorer and brief 11's — so the comparison is a real one.

THE SUMMARY IS RECOMPUTED FROM THE CSV, never read alongside it: the two files are
published together and a reader will quote whichever they open first.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ladder_all as A  # noqa: E402
import ladder_population as lp  # noqa: E402

# THE HASH OF `### The six rungs` AT COMMIT a9542fe, the D-B1 freeze. Recomputed on
# every build. If this line has to change, a rung test changed, and that is a ruling
# somebody has to make in the docket rather than a number somebody updates here.
FROZEN_SIX_RUNGS = "47b0859d80b3e44cb2711e9011cccce2e4832390b26817f073b8294530dccea9"
FREEZE_COMMIT = "a9542fe28f93eac7f66a3050070af6db93684e7e"


def six_rungs_sha() -> tuple[str, int]:
    s = (lp.ROOT / "sources" / "scope.md").read_text(encoding="utf-8")
    i = s.index("### The six rungs")
    j = s.index("### Sector readings of the frozen tests")
    block = s[i:j].rstrip() + "\n"
    return hashlib.sha256(block.encode()).hexdigest(), len(block.encode())


def main() -> int:
    bad = []

    sha, n = six_rungs_sha()
    if sha != FROZEN_SIX_RUNGS:
        bad.append(
            f"THE FROZEN RUNG TESTS HAVE CHANGED. `### The six rungs` hashes to "
            f"{sha} and the D-B1 freeze at {FREEZE_COMMIT} is {FROZEN_SIX_RUNGS}. "
            f"A reading of a test goes in the subsection below it; a change to a "
            f"test is a ruling and goes in sources/ladder_docket.md first.")

    with open(A.CSV, newline="", encoding="utf-8") as fh:
        lines = list(csv.DictReader(fh))
    summary = json.loads(A.SUMMARY.read_text(encoding="utf-8"))

    if len(lines) != summary["cross_sector"]["total_population"]:
        bad.append(f"all.csv has {len(lines)} lines; the summary says "
                   f"{summary['cross_sector']['total_population']}")

    for s in lp.SECTORS:
        ls = [l for l in lines if l["sector"] == s]
        d = summary["sectors"][s]
        scored = [l for l in ls if l["scored"] == "true"]
        excl = [l for l in ls if l["register_class"] in lp.NOT_SCORED]
        unread = [l for l in ls if l["unread"] == "true"
                  or l["register_class"] == "unread"]
        agg = [l for l in ls if l["register_class"] == "benchmark aggregate"]
        if len(scored) + len(excl) + len(unread) + len(agg) != len(ls):
            bad.append(f"{s}: the population identity does not hold — "
                       f"{len(scored)} + {len(excl)} + {len(unread)} + {len(agg)} "
                       f"!= {len(ls)}")
        if len(ls) != d["population"]:
            bad.append(f"{s}: {len(ls)} lines, the summary says {d['population']}")
        if len(scored) != d["scored"]:
            bad.append(f"{s}: {len(scored)} scored, the summary says {d['scored']}")

    # EVERY CELL CARRIES A SOURCE OR IS unread.
    for l in lines:
        for r in A.RUNGS:
            res, src = l[f"{r}_result"], l[f"{r}_source"]
            if res not in ("pass", "fail", "unread", "not_searched"):
                bad.append(f"{l['key']} {r}: result {res!r} is not in the vocabulary")
            if res in ("pass", "fail", "not_searched") and not src:
                bad.append(f"{l['key']} {r}: {res} with nothing cited")
            if res == "fail" and l[f"{r}_searched"] == "false":
                bad.append(f"{l['key']} {r}: a fail with searched=false should have "
                           f"been recorded not_searched (D-L2)")

    # THE SUMMARY RECOMPUTES FROM THE CSV'S OWN LINES.
    rebuilt, parts = A.build()
    if A.summarise(rebuilt, parts) != summary:
        bad.append("the summary does not recompute from the sources the csv came from")

    # HYDROGEN, LINE BY LINE.
    bad += A.reconcile_hydrogen(rebuilt)

    if bad:
        print(f"check_ladder_all: {len(bad)} problem(s).\n")
        for b in bad[:30]:
            print("  " + b)
        if len(bad) > 30:
            print(f"  ... and {len(bad) - 30} more")
        return 1
    print(f"check_ladder_all: {len(lines)} lines across five sectors; every identity "
          f"holds, every rung cell is sourced or unread,\n"
          f"  the summary recomputes, and hydrogen's 245 lines are line-for-line "
          f"sources/ladder/hydrogen.csv.\n"
          f"  the six rung tests hash to {sha[:16]}… — unchanged since the D-B1 "
          f"freeze at {FREEZE_COMMIT[:7]} ({n} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""THE DERIVED POPULATION AGAINST THE WORKBOOK IT CLAIMS TO COME FROM.

    python3 sources/check_hydrogen_workbook.py    # 0 clean, 1 the derived file is wrong

LOCAL ONLY. THIS IS THE CHECK THAT NEEDS openpyxl AND THE GITIGNORED BYTES, so it runs
in the pre-push chain and NEVER in `npm run build`. See scope.md, "A build-time gate
reads tracked files only".

WHY IT EXISTS. Materialising the population into a tracked file removed openpyxl from
the build image and, with it, the only thing that was checking the derived rows against
the workbook. A derived file nothing verifies is a file that drifts: somebody edits a
row by hand, or rebuilds from a different copy of the workbook, and every gate
downstream keeps passing because they all read the same wrong file. This is the one
place the two are compared.

WHAT IT CHECKS.

  THE ROWS ARE THE WORKBOOK'S. Recomputed from the workbook and compared entry by
  entry, not by count -- a count matches while every row is wrong.

  THE RECORDED HASH IS THE WORKBOOK ON THIS MACHINE, and that hash is the one
  benchmark_snapshots.json pins. A derived file built from another copy fails here.

ON A MACHINE WITHOUT THE WORKBOOKS it reports that and passes: there is nothing to
compare, and failing would make the tracked file unpushable from a machine that is
perfectly entitled to hold it.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hydrogen_test_2023 as t23  # noqa: E402

SNAPSHOT = t23.ROOT / "sources" / "benchmark_snapshots.json"
VINTAGE_FILE = "ou_quality_checked_2023.xlsx"


def main() -> int:
    path = t23.POPULATION_OUT
    if not path.exists():
        print(f"check_hydrogen_workbook: {path.name} is missing. It is tracked; run "
              f"build_hydrogen_test.py.")
        return 1

    derived = json.loads(path.read_text(encoding="utf-8"))
    if not t23.VINTAGE.exists():
        print("check_hydrogen_workbook: the October 2023 workbook is not on this "
              "machine, so the derived\n  population is not re-read. Nothing is "
              "compared and nothing is claimed.")
        return 0

    bad = []

    # 1. THE RECORDED IDENTITY IS THIS WORKBOOK, AND THIS WORKBOOK IS THE PINNED ONE.
    here = hashlib.sha256(t23.VINTAGE.read_bytes()).hexdigest()
    recorded = derived.get("sources") or []
    if not any(s.get("sha256") == here for s in recorded):
        bad.append(f"the derived population records "
                   f"{', '.join(s.get('sha256', '?')[:12] for s in recorded) or 'nothing'}"
                   f" and the workbook here is {here[:12]}: it was built from another copy")
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    pinned = next((s.get("sha256") for s in snap["snapshots"]
                   if s.get("file") == VINTAGE_FILE), None)
    if pinned and here != pinned:
        bad.append(f"the workbook on this machine is {here[:12]} and "
                   f"benchmark_snapshots.json pins {pinned[:12]} for {VINTAGE_FILE}")

    # 2. THE ROWS THEMSELVES, ENTRY BY ENTRY.
    fresh = t23.population_from_workbook()
    stored = derived.get("entries") or []
    if len(fresh) != len(stored):
        bad.append(f"the workbook yields {len(fresh)} entries and the derived file "
                   f"carries {len(stored)}")
    else:
        drifted = [f["ref"] for f, s in zip(fresh, stored)
                   if json.dumps(f, sort_keys=True) != json.dumps(s, sort_keys=True)]
        if drifted:
            bad.append(f"{len(drifted)} entries differ from the workbook: "
                       f"{', '.join(drifted[:8])}"
                       f"{' ...' if len(drifted) > 8 else ''}")

    if bad:
        print(f"check_hydrogen_workbook: {len(bad)} problem(s).\n")
        for b in bad:
            print(f"  {b}")
        print("\n  run build_hydrogen_test.py to rewrite the derived population from "
              "the workbook.")
        return 1
    print(f"check_hydrogen_workbook: {len(stored)} entries, identical to the workbook "
          f"{t23.VINTAGE.name}\n  at sha256 {here[:12]}, which is the file "
          f"benchmark_snapshots.json pins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

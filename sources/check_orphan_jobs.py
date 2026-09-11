#!/usr/bin/env python3
"""Shells and jobs this session started that are still running. Run at the END of
every turn.

    python3 sources/check_orphan_jobs.py        # 0 clean, 1 orphans found

NOT A BUILD GATE, and deliberately not in the prebuild chain: it is about the
working session and not about the data, and on a build server there is nothing for
it to find. Putting it in the chain would make it a gate that passes for the wrong
reason, which is worse than no gate.

WHY IT EXISTS. Six shells survived the hydrogen benchmark search of 10 September
2026. Four were polling `git log` for commit hashes that later pushes had already
superseded, so their conditions could never be met; two were waiting on a log file
whose writer had been killed. Two of the four were armed to run `gh pr edit` with
a pull request body that had since been corrected by hand — they were waiting to
overwrite a correction with the text it corrected. Nothing about that was visible
without asking.

A LONG-LIVED JOB IS NOT THE PROBLEM. A job that outlives the reason it was started
is: it holds a stale view of the world and acts on it anyway.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

# What a stray from this workflow looks like: a poll loop, a wait on a log, or a
# fetch left running. Matched on the command line, because that is the only thing
# that says what a shell was for.
# TWO SHAPES OF STRAY, and the first version of this check only knew one.
#
#   a poll loop, waiting for a condition that may never come
#   ANY long-running job started from a session scratchpad — which is where this
#   workflow's own background work lives
#
# The second was added on 11 September 2026 after the check reported "no stray shells"
# while a ten-site basemap sweep of this author's own was running in the background. A
# check that only catches other people's mistakes is not a check.
SUSPECT = re.compile(r"until\s+git\s+log|until\s+grep|while\s+.*sleep|"
                     r"\bpass\d+\.py|\bchunk\.py|overpass|curl\s+.*--max-time|"
                     r"claude-\d+/[^ ]*scratchpad", re.I)
SELF = os.path.basename(__file__)


def main() -> int:
    try:
        ps = subprocess.run(["ps", "-eo", "pid,ppid,etime,command"],
                            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"check_orphan_jobs: could not read the process table ({exc}).")
        return 0

    hits = []
    for line in ps.splitlines()[1:]:
        if SELF in line or " ps -eo" in line or "check_orphan_jobs" in line:
            continue
        if SUSPECT.search(line):
            pid, ppid, etime, cmd = line.split(None, 3)
            hits.append((pid, etime, cmd))

    if not hits:
        print("check_orphan_jobs: no stray shells.")
        return 0

    print(f"check_orphan_jobs: {len(hits)} still running — CLOSE THESE BEFORE THE "
          f"TURN ENDS.\n")
    for pid, etime, cmd in hits:
        print(f"  pid {pid:>7}  up {etime:>12}  {cmd[:140]}")
    print("\n  kill them by pid, then run this again. A job that has outlived its "
          "reason\n  holds a stale view of the world and will act on it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

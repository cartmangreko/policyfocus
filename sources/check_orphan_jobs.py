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
                     r"claude-\d+/[^ ]*scratchpad|"
                     # A HUNG NETWORK CHILD. git-upload-pack and git-receive-pack are the
                     # remote halves of fetch and push; when the transport dies mid-stream
                     # the local ssh can sit forever with nothing to read. One of these
                     # survived 1h51m after a `git ls-remote` met the same fault that had
                     # just broken two pushes, and the check walked straight past it
                     # because its command line says nothing about loops or scratchpads.
                     r"git-upload-pack|git-receive-pack", re.I)

# EVERY RULE IS SCOPED BY ANCESTRY, NOT JUST THE AGE RULE. Corrected 13 September 2026.
# The pattern rule above used to match any line in the process table, so running this check
# from a second session reported the FIRST session's `run14.py` as a stray and invited a
# kill of work that was doing exactly what it was told. A check that reports other sessions'
# live jobs as strays is worse than no check: it is a standing instruction to kill them.
#
# ANCESTRY, NOT COMMAND TEXT, because the shapes that matter do not name themselves. An
# `ssh git-receive-pack` left behind by a push carries nothing in its command line tying it
# to this session — but its parent chain runs back to the shell that ran `git push`. Walking
# ppid to the snapshot catches it; matching on the command line cannot.
#
# AND A CATCH-ALL BY AGE, SCOPED TO THIS SESSION. Everything above matches a pattern
# somebody thought of after being caught by it, which is a poor way to find the next one.
# A shell of THIS session still alive after ten minutes at the end of a turn is a stray
# whatever it is running.
#
# SCOPED BY THE SHELL SNAPSHOT, so a concurrent session's work is never reported and
# never killed. Two Claude sessions on one machine share a process table and do not share
# a snapshot file; this check finds its own by reading its own ancestry, and if it cannot
# it says so rather than guessing.
OLD_ENOUGH_MIN = 10

# THE BLIND SPOT, STATED RATHER THAN PAPERED OVER. When a backgrounded grandchild
# outlives the `zsh -c` that started it, macOS reparents it to launchd and the ancestry
# is gone. If its own command line does not carry the snapshot either, NOTHING ON THIS
# MACHINE STILL SAYS WHOSE IT WAS: `ps -E` will not show another process's environment
# under SIP, and `SESS` is 0 for every process here, so neither the session id nor the
# inherited CLAUDE_CODE_SESSION_ID can be read back. Measured on 13 September 2026.
#
# Such a process is NOT reported, and that is the deliberate choice: the alternative is
# to report every long-running job on the machine and invite a kill of a concurrent
# session's work, which is the exact bug this scoping fixes. The poll loops that caused
# this check to be written are `zsh -c source .../snapshot-...sh && until git log ...`
# and DO carry the snapshot in their own command line, so the shapes on record are still
# caught after reparenting. A stray that names nothing and has outlived its parent is
# not.


def my_snapshot() -> str | None:
    """The shell-snapshot path this session's shells are started from."""
    try:
        me = subprocess.run(["ps", "-o", "command=", "-p", str(os.getppid())],
                            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.search(r"snapshot-zsh-\d+-[a-z0-9]+", me)
    return m.group(0) if m else None


def minutes(etime: str) -> float:
    """ps ELAPSED — [[dd-]hh:]mm:ss — in minutes."""
    days, _, rest = etime.rpartition("-")
    parts = [float(x) for x in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, sec = parts
    return (float(days or 0) * 1440) + h * 60 + m + sec / 60
SELF = os.path.basename(__file__)


def main() -> int:
    try:
        ps = subprocess.run(["ps", "-eo", "pid,ppid,etime,command"],
                            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"check_orphan_jobs: could not read the process table ({exc}).")
        return 0

    snap = my_snapshot()

    # THE PROCESS TREE, so a pattern hit can be asked whose it is.
    parent, command = {}, {}
    for line in ps.splitlines()[1:]:
        try:
            pid, ppid, etime, cmd = line.split(None, 3)
        except ValueError:
            continue
        parent[pid], command[pid] = ppid, cmd

    claude = os.environ.get("CLAUDE_PID") or ""

    def mine(pid: str) -> bool:
        """Does this process belong to THIS session?

        Two signals, because one of them is not always there:

          the command line carries this session's snapshot path -- true of every
          `zsh -c source .../snapshot-zsh-N-x.sh && ...` the tool starts, which is
          the shape the classic poll-loop strays actually have; it survives the
          parent's death because it is the process's own text

          the ancestry reaches such a shell, or reaches this session's `claude`
          process -- which is how a child that names nothing is claimed, the
          `ssh git-receive-pack` left by a push being the case that prompted it

        Without a snapshot nothing is claimed. Guessing here gets another session's
        work killed, which is the failure this scoping exists to prevent.
        """
        if not snap:
            return False
        seen = set()
        while pid and pid not in seen and pid != "0":
            seen.add(pid)
            if snap in command.get(pid, "") or (claude and pid == claude):
                return True
            pid = parent.get(pid, "")
        return False

    # THE SESSION'S OWN SPINE IS NOT A STRAY. `claude` itself, the shell it runs in and
    # the terminal above it are this session, not jobs it left behind; claiming the
    # ancestry made the check report `claude code` as a stray of nearly seven days. Only
    # DESCENDANTS are candidates, so every ancestor of this very process is excluded.
    spine, cur = set(), str(os.getpid())
    while cur and cur not in spine and cur != "0":
        spine.add(cur)
        cur = parent.get(cur, "")

    hits = []
    for line in ps.splitlines()[1:]:
        if SELF in line or " ps -eo" in line or "check_orphan_jobs" in line:
            continue
        try:
            pid, ppid, etime, cmd = line.split(None, 3)
        except ValueError:
            continue
        if pid in spine:
            continue          # THE SESSION ITSELF, NOT A JOB IT LEFT RUNNING.
        if not mine(pid):
            continue          # ANOTHER SESSION'S JOB IS NOT THIS CHECK'S BUSINESS.
                              # AND SO IS AN UNATTRIBUTABLE ONE -- see BLIND SPOT.
        why = None
        if SUSPECT.search(line):
            why = "matches a known stray shape"
        elif minutes(etime) >= OLD_ENOUGH_MIN:
            why = f"this session's shell, alive {minutes(etime):.0f} min"
        if why:
            hits.append((pid, etime, cmd, why))

    if not hits:
        scope = f" (scoped to {snap})" if snap else \
                " (SCOPE OFF: this session's shell snapshot could not be read, so no "
        print(f"check_orphan_jobs: no stray shells{scope}.")
        if not snap:
            print("  process was claimed. Nothing was checked; do not read this as clean.")
        return 0

    print(f"check_orphan_jobs: {len(hits)} still running — CLOSE THESE BEFORE THE "
          f"TURN ENDS.\n")
    for pid, etime, cmd, why in hits:
        print(f"  pid {pid:>7}  up {etime:>12}  {why}\n      {cmd[:130]}")
    print("\n  kill them by pid, then run this again. A job that has outlived its "
          "reason\n  holds a stale view of the world and will act on it.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
Prove the Python and TypeScript readings of "is this entry a transition" agree.

There are two implementations of one rule. sector_map.is_transition decides what
the built leads say; web/lib/transition.ts statusTransitions decides what the
project page's status rail says. They are the same rule expressed twice, held
together by nothing but a comment on each side saying so -- which is the shape
the reach-channel inference is in, and the shape that fails silently.

WHAT THE RULE IS AND WHY IT HAS TO BE HELD

A project's status_history is a list of EVENTS in date order. Most are
transitions: the project moved, and the entry's date is the date it moved. Some
are not. Slite was paused on 19 November 2025 when the Swedish Energy Agency
declined to co-fund it, and its permit application was withdrawn on 1 January
2026 -- a later source on a project whose status it does not change. Both belong
in the history; only the first is a transition.

An entry is a transition if its status differs from the entry before it. The
first entry always is.

WHY A DISAGREEMENT WOULD BE INVISIBLE. Three sentence templates render an entry
as a transition -- "{project} was paused on {date}" -- and if the two sides
disagreed about which entries qualify, the built lead and the page would each
name a different date for the same event, both confidently, with nothing in
either output saying which. That is the failure this gate exists to make
impossible, and it is the same failure check_valence_parity.py was written for.

THE TYPESCRIPT IS EXECUTED, NOT PARSED. Reimplementing statusTransitions in
Python to check statusTransitions against Python would only prove a third copy
agrees with the first two. It is compiled with the project's own tsc and run
under node, so what is checked is the code that actually ships.

THE CROSS PRODUCT IS EXHAUSTIVE FOR A LOCAL RULE. Every history up to four
entries long over the seven statuses plus one status neither side knows -- 4,681
of them, including the empty history and every run, alternation and repeat. The
rule only ever compares an entry with its predecessor, so four entries is past
the length at which a longer case could say anything new; the length is there to
demonstrate that rather than to be argued. The unknown status is in for the same
reason the valence gate feeds deriveValence values its signature forbids: an
input no row currently carries is the one a later edit reaches for first.

    python3 check_transition_parity.py       # exits non-zero on any mismatch

Skips with a clear message (not a pass) if node or the web install is absent, so
a machine without them cannot quietly turn the gate green.
"""

from __future__ import annotations

import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile

import sector_map as sm

_HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(_HERE), "web")

# The seven the register uses, plus one it does not. See the module docstring.
ALPHABET = list(sm.PROJECT_STATUSES) + ["bogus"]
MAX_LENGTH = 4


def histories() -> list[list[str]]:
    """Every status sequence up to MAX_LENGTH, shortest first, empty included.

    Dates are not part of the rule and are not generated: is_transition compares
    statuses and nothing else, and a date column here would be a second thing to
    keep in step for no gain. The gate on date ORDER is check_sector_schema's,
    which is where append-only is enforced.
    """
    out: list[list[str]] = [[]]
    for n in range(1, MAX_LENGTH + 1):
        out += [list(c) for c in itertools.product(ALPHABET, repeat=n)]
    return out


# Masks rather than entries: the question is WHICH entries each side calls a
# transition, and comparing the objects would compare the fixture as much as the
# rule. "0110" reads as an answer and diffs as one.
PROBE_TS = """
import { statusTransitions } from "./transition";
import fs from "node:fs";

type Row = { status: string; date: string; source_url: string };

const cases: string[][] = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = cases.map((statuses) => {
  const history: Row[] = statuses.map((status, i) => ({
    status,
    // Ordered and distinct so nothing here can be mistaken for the real thing
    // if this fixture ever escapes the temporary directory it is built in.
    date: `2000-01-0${i + 1}`,
    source_url: "https://example.invalid/probe",
  }));
  // The cast is the point of the probe: statusTransitions is typed against
  // Project and reads only status_history, and feeding it a bare history is how
  // the rule gets asked its question without a fixture of everything else a
  // project carries.
  const kept = statusTransitions({ status_history: history } as never);
  const at = new Set(kept.map((h) => h.date));
  return history.map((h) => (at.has(h.date) ? "1" : "0")).join("");
});
console.log(JSON.stringify(out));
"""


def ts_masks(cases: list[list[str]]) -> list[str] | None:
    """Compile and run transition.ts, returning one 0/1 mask per case. None if
    the toolchain is unavailable."""
    tsc = os.path.join(WEB, "node_modules", ".bin", "tsc")
    if not os.path.exists(tsc) or shutil.which("node") is None:
        return None

    with tempfile.TemporaryDirectory() as tmp:
        # transition.ts imports money.ts, and neither reads a file at module
        # scope -- both defer to a function -- so the pair imports cleanly from
        # a directory with no data beside it. If that ever stops being true this
        # gate fails loudly at the import rather than quietly skipping.
        for name in ("transition.ts", "money.ts"):
            shutil.copy(os.path.join(WEB, "lib", name), os.path.join(tmp, name))
        with open(os.path.join(tmp, "probe.ts"), "w", encoding="utf-8") as fh:
            fh.write(PROBE_TS)
        cases_path = os.path.join(tmp, "cases.json")
        with open(cases_path, "w", encoding="utf-8") as fh:
            json.dump(cases, fh)

        result = subprocess.run(
            # esModuleInterop, which the valence gate does not need and this
            # one does: transition.ts and money.ts do `import fs from
            # "node:fs"`, and without interop the commonjs emit reads `.default`
            # off a namespace object that has none. The project's own tsconfig
            # sets it; the flag is here so the probe compiles the way the app
            # does rather than the way a bare tsc invocation would.
            [tsc, "probe.ts", "transition.ts", "money.ts",
             "--outDir", "out", "--module", "commonjs", "--target", "es2020",
             "--esModuleInterop",
             "--skipLibCheck", "--noEmitOnError", "false"],
            cwd=tmp, capture_output=True, text=True,
        )
        js = os.path.join(tmp, "out", "probe.js")
        if not os.path.exists(js):
            print("check_transition_parity: tsc emitted nothing\n"
                  + result.stdout + result.stderr, file=sys.stderr)
            return None

        run = subprocess.run(["node", js, cases_path], capture_output=True, text=True)
        if run.returncode != 0:
            print("check_transition_parity: node failed\n" + run.stderr, file=sys.stderr)
            return None
        return json.loads(run.stdout)


def python_mask(statuses: list[str]) -> str:
    history = [{"status": s, "date": f"2000-01-0{i + 1}",
                "source_url": "https://example.invalid/probe"}
               for i, s in enumerate(statuses)]
    return "".join("1" if sm.is_transition(history, i) else "0"
                   for i in range(len(history)))


def entered_agrees(statuses: list[str], mask: str) -> bool:
    """`entered` is derived from the same rule and is what two of the three
    sentence templates actually call, so it is checked against the mask rather
    than trusted to follow from it. It is the LAST transition -- the first entry
    of the trailing run of the current status."""
    history = [{"status": s, "date": f"2000-01-0{i + 1}",
                "source_url": "https://example.invalid/probe"}
               for i, s in enumerate(statuses)]
    got = sm.entered({"status_history": history})
    if not statuses:
        return got is None
    return got is not None and got["date"] == f"2000-01-0{mask.rindex('1') + 1}"


def main() -> int:
    cases = histories()
    ts = ts_masks(cases)
    if ts is None:
        print("check_transition_parity: SKIPPED — needs node and `npm install` in web/.")
        print("  This is not a pass. The gate cannot confirm the two readings agree.")
        return 2

    if len(ts) != len(cases):
        print(f"check_transition_parity: probe returned {len(ts)} masks, "
              f"expected {len(cases)}", file=sys.stderr)
        return 1

    mismatches = []
    derived = []
    for statuses, got in zip(cases, ts):
        py = python_mask(statuses)
        if py != got:
            mismatches.append((statuses, py, got))
        elif not entered_agrees(statuses, py):
            derived.append((statuses, py))

    if mismatches:
        print(f"check_transition_parity: {len(mismatches)} of {len(cases)} "
              f"histories disagree\n")
        for statuses, py, got in mismatches[:12]:
            print(f"  {' → '.join(statuses) or '(empty)'}")
            print(f"      python={py!r} typescript={got!r}")
        if len(mismatches) > 12:
            print(f"  … and {len(mismatches) - 12} more")
        print("\nsector_map.is_transition and web/lib/transition.ts statusTransitions")
        print("express one rule twice. Fix both, not one.")
        return 1

    if derived:
        print(f"check_transition_parity: {len(derived)} history/histories where "
              f"sector_map.entered is not the last transition its own rule found\n")
        for statuses, py in derived[:12]:
            print(f"  {' → '.join(statuses) or '(empty)'}  mask={py!r}")
        return 1

    print(f"check_transition_parity: {len(cases)}/{len(cases)} histories agree "
          f"(every sequence to {MAX_LENGTH} entries over "
          f"{len(ALPHABET)} statuses), and `entered` follows the mask in all of them")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

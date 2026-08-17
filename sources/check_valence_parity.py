"""
Prove the Python and TypeScript valence derivations agree, for every input.

There are two implementations of one rule. benefit_axis.derive_valence decides
what the build writes; web/lib/valence.ts decides what a reader sees. They are
the same rule expressed twice, and for most of this project's life the only
thing holding them together was a comment saying "kept in sync by hand". That
works right up until it doesn't, and the failure is silent: the register would
say Entitlement and the page would say Neutral, with nothing to notice.

So this walks the full cross product of measure_type x direction -- including
the unrepresented and the nonsensical -- through both implementations and diffs
the labels. It runs in the build gate.

The TypeScript is executed, not parsed. Reimplementing valence.ts in Python to
check valence.ts against Python would only prove that a third copy agrees with
the first two. It is compiled with the project's own tsc and run under node, so
what is checked is the code that actually ships.

    python3 check_valence_parity.py          # exits non-zero on any mismatch

Skips with a clear message (not a pass) if node or the web install is absent, so
a machine without them cannot quietly turn the gate green.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

from benefit_axis import derive_valence

_HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(os.path.dirname(_HERE), "web")

# The cross product, deliberately wider than the data. Combinations no row
# currently uses are exactly the ones a later edit will reach for first, and an
# unrepresented combination that disagrees across the two implementations is a
# bug already written, just not yet triggered. None/"" cover a row whose
# measure_type is absent, which deriveValence defaults to obligation.
MEASURE_TYPES = ["obligation", "incentive", "right", None, "", "bogus"]
DIRECTIONS = ["add", "rem", None, "", "bogus"]

# valence.ts names the stored valence in the data's vocabulary and maps it to a
# display label; Python returns the label directly. The parity that matters is
# the label -- it is what the register and the page each assert about a row.
# Emitted as positional triples rather than keyed by an interpolated string:
# `${null}` and `${""}` both stringify to values Python spells differently, so a
# string key would manufacture mismatches that are only encoding artefacts. The
# first version of this file did exactly that and reported eight false ones.
PROBE_TS = """
import { valenceLabel } from "./valence";

const measureTypes = %s;
const directions = %s;
const out = [];
for (const t of measureTypes) {
  for (const d of directions) {
    out.push([t, d, valenceLabel(t, d)]);
  }
}
console.log(JSON.stringify(out));
"""


def ts_labels() -> list[list] | None:
    """Compile and run valence.ts, returning [measure_type, direction, label]
    triples. None if the toolchain is unavailable."""
    tsc = os.path.join(WEB, "node_modules", ".bin", "tsc")
    if not os.path.exists(tsc) or shutil.which("node") is None:
        return None

    def js_literal(values):
        # `null` and "" must survive as themselves: they probe the defaulting
        # branch, which is where a mismatch is most likely to hide.
        return json.dumps(values)

    with tempfile.TemporaryDirectory() as tmp:
        for name in ("valence.ts", "types.ts"):
            shutil.copy(os.path.join(WEB, "lib", name), os.path.join(tmp, name))
        with open(os.path.join(tmp, "probe.ts"), "w", encoding="utf-8") as fh:
            fh.write(PROBE_TS % (js_literal(MEASURE_TYPES), js_literal(DIRECTIONS)))

        # Types are deliberately not enforced here. The probe feeds deriveValence
        # values its signature forbids (null, "bogus") precisely to check the
        # runtime fallback, so a type error is the expected outcome of asking the
        # question, not a failure to answer it.
        result = subprocess.run(
            [tsc, "probe.ts", "valence.ts", "types.ts",
             "--outDir", "out", "--module", "commonjs", "--target", "es2020",
             "--skipLibCheck", "--noEmitOnError", "false"],
            cwd=tmp, capture_output=True, text=True,
        )
        js = os.path.join(tmp, "out", "probe.js")
        if not os.path.exists(js):
            print("check_valence_parity: tsc emitted nothing\n" + result.stdout + result.stderr,
                  file=sys.stderr)
            return None

        run = subprocess.run(["node", js], capture_output=True, text=True)
        if run.returncode != 0:
            print("check_valence_parity: node failed\n" + run.stderr, file=sys.stderr)
            return None
        return json.loads(run.stdout)


def main() -> int:
    ts = ts_labels()
    if ts is None:
        print("check_valence_parity: SKIPPED — needs node and `npm install` in web/.")
        print("  This is not a pass. The gate cannot confirm the two derivations agree.")
        return 2

    mismatches = []
    for t, d, got in ts:
        py = derive_valence(t, d)
        if py != got:
            mismatches.append((t, d, py, got))

    total = len(ts)
    expected = len(MEASURE_TYPES) * len(DIRECTIONS)
    if total != expected:
        print(f"check_valence_parity: probe returned {total} combinations, expected {expected}",
              file=sys.stderr)
        return 1
    if mismatches:
        print(f"check_valence_parity: {len(mismatches)} of {total} combinations disagree\n")
        for t, d, py, got in mismatches:
            print(f"  measure_type={t!r} direction={d!r}: python={py!r} typescript={got!r}")
        print("\nbenefit_axis.derive_valence and web/lib/valence.ts express one rule twice.")
        print("Fix both, not one.")
        return 1

    print(f"check_valence_parity: {total}/{total} combinations agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

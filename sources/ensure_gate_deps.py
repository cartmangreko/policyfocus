#!/usr/bin/env python3
"""
Make sure the build gates have what they import, before the first gate runs.

    python3 ensure_gate_deps.py            # install if missing, then verify
    python3 ensure_gate_deps.py --check    # verify only, never install

WHY THIS EXISTS. The gates were standard-library-only until sources/eov.py, which
asks pyproj for EPSG:23700 rather than reimplementing a double projection on a
datum ninety metres from WGS84. That was the right call for the arithmetic and it
put a wheel in the path of every environment the build runs in — including the
deployment, which installs Node packages and knows nothing about Python. The
first build after that change failed there and nowhere else, which is the worst
shape a dependency can have: green on the machine that added it.

So the prebuild installs it, from sources/requirements-gates.txt, and says so.
The alternative was an install command in a deployment config, which would fix
one environment and leave the next one to discover the same failure.

IT NEVER SKIPS. If the install fails, this exits non-zero with pip's own output.
A gate that quietly does not run is worse than one nobody wrote, and the check
this dependency serves is a coordinate recomputation — the thing standing between
a stored latitude and somebody having typed it.
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIREMENTS = HERE / "requirements-gates.txt"

# Import name -> what it is for, printed when it has to be installed.
NEEDED = {"pyproj": "EPSG:23700 for sources/eov.py"}


def _pip(*extra: str) -> subprocess.CompletedProcess:
    """One pip invocation, with whatever extra flags the caller has earned."""
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
         *extra, "-r", str(REQUIREMENTS)],
        capture_output=True, text=True)


def missing() -> list:
    out = []
    for module in NEEDED:
        try:
            __import__(module)
        except ImportError:
            out.append(module)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report only; never install")
    args = ap.parse_args()

    gone = missing()
    if not gone:
        print(f"ensure_gate_deps: OK — {', '.join(sorted(NEEDED))} present")
        return 0
    if args.check:
        print(f"ensure_gate_deps: MISSING {', '.join(gone)} — "
              f"run `python3 -m pip install -r {REQUIREMENTS.name}`", file=sys.stderr)
        return 1

    print(f"ensure_gate_deps: installing {', '.join(gone)} "
          f"({'; '.join(NEEDED[m] for m in gone)}) from {REQUIREMENTS.name}",
          flush=True)
    proc = _pip()
    # PEP 668. A build image's interpreter is usually marked externally managed,
    # which is a sensible default for a machine somebody lives on and the wrong
    # one for a container that exists for four minutes. The retry is narrow on
    # purpose: only this error, only after the ordinary install has been tried,
    # and it says out loud that it happened. It is never reached on a laptop,
    # where the first attempt succeeds.
    if proc.returncode != 0 and "externally-managed-environment" in (
            proc.stderr + proc.stdout):
        print("ensure_gate_deps: the interpreter is externally managed (PEP 668); "
              "retrying with --break-system-packages, which is what a build image "
              "is for", flush=True)
        proc = _pip("--break-system-packages")
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        print(f"ensure_gate_deps: pip failed ({proc.returncode}) — the gates that "
              f"need {', '.join(gone)} cannot run, and are not being skipped",
              file=sys.stderr)
        return 1

    still = missing()
    if still:
        print(f"ensure_gate_deps: pip reported success and {', '.join(still)} is "
              f"still not importable", file=sys.stderr)
        return 1
    print(f"ensure_gate_deps: installed {', '.join(gone)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

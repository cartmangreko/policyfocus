#!/usr/bin/env python3
"""RUN THE PREBUILD CHAIN AS THE BUILD IMAGE WOULD SEE IT, and fail on anything that
only works here.

    python3 sources/check_build_image.py            # 0 clean, 1 a step needs this machine
    python3 sources/check_build_image.py --list     # what it would run and what it blocks

LOCAL ONLY, and necessarily so: it is the check that simulates the absence of the things
this machine has. It runs in the pre-push chain and never in `npm run build`.

WHY IT EXISTS. scope.md's rule -- "A build-time gate reads tracked files only" -- was
written after the production build failed at d96903a, and it was written as prose. Prose
does not catch the next step that reaches for a workbook. The audit that accompanied it
was a one-off measurement, true on the day and never repeated. THIS IS THAT MEASUREMENT
MADE A GATE.

WHAT THE BUILD IMAGE HAS, AND HOW THIS KNOWS.

  TRACKED FILES ONLY. The sandbox is `git archive HEAD` unpacked into a temporary
  directory, which is exactly the set of files a deployment checks out: no gitignored
  cache bodies, no workbooks, no manual copies that were never committed.

  THE STANDARD LIBRARY, PLUS sources/requirements-gates.txt. That file is the contract
  -- ensure_gate_deps.py installs it at the head of every prebuild, everywhere the build
  runs -- so what it names is present and everything else third-party is not.

  THE BLOCK LIST IS DERIVED, NEVER TYPED. Every third-party module imported anywhere in
  sources/ is found by reading the imports, and the ones requirements-gates.txt does not
  name are blocked. A package added to a script next month is blocked automatically; a
  hand-written list would have to be remembered, and the failure it prevents is exactly
  the failure of somebody not remembering.

  node_modules IS SYMLINKED IN, because the deployment runs `npm install` and therefore
  has it. Blocking it would fail the two node steps for a reason the build image would
  never produce.

WHAT IT DOES NOT DO. It does not run check_links. That step reaches publishers, the
build image has network, and it passes or fails on other people's servers rather than on
anything this gate is about -- it has already run once in the same push, and running it
twice adds two minutes of somebody else's uptime to every push. NAMED RATHER THAN
QUIETLY DROPPED, which is the same rule the chain applies to itself.

THE STEPS COME FROM web/package.json, parsed. A copy of the list here would drift from
the chain it claims to check, and a gate that checks yesterday's chain is worse than
none: it reports green about something nobody runs.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACKAGE_JSON = ROOT / "web" / "package.json"
REQUIREMENTS = HERE / "requirements-gates.txt"

# Reached over the network by design; see the module docstring.
SKIP = ("check_links.py",)


def script_of(step: str) -> str:
    """The file a step runs, not the interpreter that runs it.

    `step.split()[0]` is `python3`, which matched nothing and silently ran the one step
    this gate means to skip -- caught on the first --list.
    """
    for tok in step.split():
        if tok.endswith((".py", ".mjs", ".mts")):
            return tok.split("/")[-1]
    return step.split()[0]


def prebuild_steps() -> list[str]:
    """The prebuild chain, read from the file npm actually runs."""
    scripts = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))["scripts"]
    return [s.strip() for s in scripts["prebuild"].split("&&") if s.strip()]


def allowed_packages() -> set[str]:
    """What the build image installs: requirements-gates.txt, by import name.

    The distribution name and the import name agree for everything in there now, and if
    one day they do not, the gate that notices is this one failing on a package the
    build image actually has -- which is a visible wrong answer rather than a silent
    permission.
    """
    out = set()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.add(re.split(r"[<>=!\[;]", line)[0].strip().replace("-", "_").lower())
    return out


def third_party_imports() -> set[str]:
    """Every non-stdlib, non-local module imported anywhere in sources/."""
    local = {p.stem for p in HERE.glob("*.py")}
    std = set(sys.stdlib_module_names)
    out = set()
    for f in HERE.glob("*.py"):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for n in ast.walk(tree):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                names = [n.module.split(".")[0]]
            for m in names:
                if m not in std and m not in local:
                    out.add(m)
    return out


def blocked_packages() -> set[str]:
    return {m for m in third_party_imports() if m.lower() not in allowed_packages()}


def write_blockers(shim: Path, blocked: set[str]) -> None:
    """A stub for each blocked package that raises ImportError on import.

    THE SAME ERROR THE BUILD IMAGE RAISES. A stub that returned an empty module would
    let a step import it and fail later, somewhere less legible; ImportError at the
    import line is what Vercel actually produces.
    """
    shim.mkdir(parents=True, exist_ok=True)
    for m in sorted(blocked):
        (shim / f"{m}.py").write_text(
            f"raise ImportError(\"No module named '{m}'\")\n", encoding="utf-8")


def build_sandbox(tmp: Path) -> Path:
    """Tracked files at HEAD, unpacked. Exactly what a deployment checks out.

    AT HEAD, NOT IN THE WORKING TREE, and that is the right question for a pre-push
    hook: what is being pushed is what the deployment will build. An uncommitted fix
    for a failure this reports will not clear it until it is committed, which is the
    same discipline the rest of the chain applies.
    """
    sandbox = tmp / "tree"
    sandbox.mkdir(parents=True)
    archive = tmp / "head.tar"
    with archive.open("wb") as fh:
        subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, stdout=fh, check=True)
    subprocess.run(["tar", "-xf", str(archive), "-C", str(sandbox)], check=True)
    archive.unlink()

    # THE DEPLOYMENT RUNS npm install, SO node_modules IS THERE. Symlinked rather than
    # copied: it is hundreds of megabytes and nothing in the chain writes to it.
    nm = ROOT / "web" / "node_modules"
    if nm.exists():
        (sandbox / "web" / "node_modules").symlink_to(nm, target_is_directory=True)
    return sandbox


def run(steps, sandbox: Path, shim: Path, verbose: bool) -> list[tuple[str, str]]:
    env = dict(os.environ)
    # THE SHIM GOES FIRST so its stubs win over anything installed here. PYTHONNOUSERSITE
    # stops a user site-packages copy of a blocked package from being found behind it.
    env["PYTHONPATH"] = os.pathsep.join([str(shim), env.get("PYTHONPATH", "")]).rstrip(
        os.pathsep)
    env["PYTHONNOUSERSITE"] = "1"
    failures = []
    for step in steps:
        if script_of(step) in SKIP:
            print(f"  skipped  {step}   (network; see the docstring)")
            continue
        started = time.time()
        proc = subprocess.run(step, shell=True, cwd=sandbox / "web", env=env,
                              capture_output=True, text=True)
        took = time.time() - started
        if proc.returncode == 0:
            print(f"  ok       {step}   {took:.0f}s")
            if verbose and proc.stdout.strip():
                print("\n".join("           " + l
                                for l in proc.stdout.strip().splitlines()[:3]))
        else:
            print(f"  FAILED   {step}   {took:.0f}s")
            failures.append((step, (proc.stdout + proc.stderr).strip()))
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true",
                    help="print the steps and the block list, run nothing")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    steps = prebuild_steps()
    blocked = blocked_packages()

    if a.list:
        print(f"check_build_image: {len(steps)} prebuild step(s), "
              f"{len(SKIP)} skipped by name.")
        for s in steps:
            mark = "skip" if script_of(s) in SKIP else "run "
            print(f"  {mark}  {s}")
        print(f"\nallowed (requirements-gates.txt): "
              f"{', '.join(sorted(allowed_packages())) or 'nothing'}")
        print(f"blocked (local-only): {', '.join(sorted(blocked)) or 'nothing'}")
        return 0

    if not shutil.which("git"):
        print("check_build_image: git is not on PATH; the sandbox cannot be built.")
        return 1

    print(f"check_build_image: {len(steps) - len(SKIP)} prebuild step(s) against a "
          f"tracked-files-only tree at HEAD,\n  with {len(blocked)} local-only "
          f"package(s) blocked: {', '.join(sorted(blocked)) or 'none'}")

    with tempfile.TemporaryDirectory(prefix="eufabric-buildimage-") as td:
        tmp = Path(td)
        shim = tmp / "blocked"
        write_blockers(shim, blocked)
        try:
            sandbox = build_sandbox(tmp)
        except subprocess.CalledProcessError as exc:
            print(f"check_build_image: could not build the sandbox ({exc}).")
            return 1
        failures = run(steps, sandbox, shim, a.verbose)

    if failures:
        print(f"\ncheck_build_image: {len(failures)} step(s) need something the build "
              f"image does not have.\n")
        for step, out in failures:
            print(f"  {step}")
            tail = [l for l in out.splitlines() if l.strip()][-6:]
            for l in tail:
                print(f"      {l[:150]}")
            print()
        print("  A step in `npm run build` may read only tracked files and import only\n"
              "  what requirements-gates.txt names. Move it to the pre-push chain, or\n"
              "  materialise what it needs into a tracked derived file. See scope.md,\n"
              "  \"A build-time gate reads tracked files only\".")
        return 1

    print(f"\ncheck_build_image: every prebuild step passes on tracked files alone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

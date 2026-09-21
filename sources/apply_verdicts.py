#!/usr/bin/env python3
"""Read the filled-in verdict worklist back, and write the verdicts onto the edges.

    python3 sources/apply_verdicts.py                # what the file says, changing nothing
    python3 sources/apply_verdicts.py --write        # write sources/verdicts.json
    python3 sources/apply_verdicts.py --write --rebuild   # …and rebuild the graph

THE FILE IS THE READER'S AND THIS SCRIPT IS THE READER'S HAND. `verdict` takes one
of three words — `accept`, `reject`, `unclear` — and anything else is refused by
name rather than coerced or ignored. An empty cell is not a verdict: it is a line
nobody has read yet, and it stays null.

WHY A VERDICT DOES NOT GO INTO edges.json. That file is built: `dep_records.py
--build` writes it from the readings, and a verdict typed into it would be gone the
next time anybody rebuilt. So the verdicts live in `sources/verdicts.json`, keyed by
edge id and carrying who ruled and when, and the build reads them onto the edges —
the same shape as every other derived field here. A verdict survives a rebuild
because it is an input to one.

WHAT A VERDICT MEANS, and it is narrower than it sounds:

  accept    the sentence says what the edge claims, and the edge is about this row.
  reject    it does not. The edge stays in the file with the verdict on it, because
            a reading somebody refused is a fact about the reading.
  unclear   the reader could not tell from the document. The note says what would
            settle it.

AND WHAT IT MOVES. Rung 6 of the confirmation ladder is `provisional` while the edge
it rests on carries `verdict: null` — that is the whole of the flag's meaning. This
prints how many rung 6 cells stop being provisional when the file is applied, which
is the only number a verdicting session needs to watch.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

CSV_IN = HERE / "verdicts_worklist.csv"
OUT = HERE / "verdicts.json"
VERDICTS = ("accept", "reject", "unclear")
BY = "George Christopoulos"

HEAD = [
    "VERDICTS ON THE DEPENDENCY GRAPH'S EDGES, one entry per edge id.",
    "",
    "Written by apply_verdicts.py from sources/verdicts_worklist.csv, which is where",
    "a person reads and rules. dep_records.py puts these onto the edges at build time,",
    "so a verdict survives a rebuild: edges.json is derived and a value typed into it",
    "would not be.",
    "",
    "`verdict` is one of accept | reject | unclear. `by` and `date` say who ruled and",
    "when. A rejected edge KEEPS ITS PLACE in the graph with the verdict on it,",
    "because a reading somebody refused is a fact about the reading and deleting it",
    "would leave the file looking as though nobody had ever made it.",
]


def read_csv() -> tuple[dict, list[str]]:
    if not CSV_IN.exists():
        return {}, [f"no {CSV_IN.name} — run `python3 sources/dep_worklist.py --csv`"]
    out, bad = {}, []
    with CSV_IN.open(newline="", encoding="utf-8") as fh:
        for i, r in enumerate(csv.DictReader(fh), 2):
            v = (r.get("verdict") or "").strip().lower()
            if not v:
                continue
            eid = (r.get("edge_id") or "").strip()
            if v not in VERDICTS:
                bad.append(f"line {i} ({eid}): verdict {r['verdict']!r} is not one of "
                           f"{' | '.join(VERDICTS)}")
                continue
            if eid in out:
                bad.append(f"line {i}: {eid} is verdicted twice")
                continue
            out[eid] = {"verdict": v, "by": BY, "date": time.strftime("%Y-%m-%d"),
                        "note": (r.get("note") or "").strip()}
    return out, bad


def graph_edges() -> list[dict]:
    return json.loads((HERE / "edges.json").read_text(encoding="utf-8"))["edges"]


def would_stop_being_provisional(new: dict) -> list[tuple[str, str]]:
    """(row id, edge id) for every rung 6 cell that stops being provisional.

    ASKED OF THE SCORER RATHER THAN GUESSED AT. `build_ladder.score_input` picks
    which edge a row's rung 6 rests on — the newest `contract` if there is one, the
    newest of the rest otherwise — and the flag follows that edge and no other. So
    the same function is asked, with the verdicts applied to a copy of the graph in
    memory. A row whose deciding edge is still unverdicted does not count, however
    many of its other edges have been ruled on.
    """
    import build_ladder as L
    rows = {p["id"]: p for p in json.loads(
        (HERE.parent / "data" / "transition" / "projects.json")
        .read_text(encoding="utf-8"))["projects"]}
    by_project: dict[str, list[dict]] = {}
    for e in graph_edges():
        if e["project_id"]:
            e = dict(e)
            if e["id"] in new:
                e["verdict"] = new[e["id"]]["verdict"]
            by_project.setdefault(e["project_id"], []).append(e)
    out = []
    for pid, edges in sorted(by_project.items()):
        row = rows.get(pid)
        if row is None:
            continue
        before = L.score_input(row, {pid: [dict(e, verdict=None) for e in edges]})
        after = L.score_input(row, {pid: edges})
        if before.get("provisional") and not after.get("provisional"):
            firm = [e for e in edges if e.get("firmness") == L.FIRM_PASS]
            pick = (L.newest(firm) or firm[0]) if firm else (L.newest(edges) or edges[0])
            out.append((pid, pick["id"]))
    return out


def main(argv: list[str]) -> int:
    new, bad = read_csv()
    if bad:
        print(f"apply_verdicts: {len(bad)} problem(s), nothing written\n", file=sys.stderr)
        for b in bad:
            print("  " + b, file=sys.stderr)
        return 1

    known = {e["id"] for e in graph_edges()}
    missing = sorted(set(new) - known)
    if missing:
        print(f"apply_verdicts: {len(missing)} verdict(s) name an edge that is not in "
              f"the graph: {', '.join(missing)}", file=sys.stderr)
        return 1

    counts = {v: sum(1 for x in new.values() if x["verdict"] == v) for v in VERDICTS}
    print(f"apply_verdicts: {len(new)} verdict(s) in {CSV_IN.name} — "
          + ", ".join(f"{k} {counts[k]}" for k in VERDICTS)
          + f"; {len(known) - len(new)} edge(s) still unverdicted.")

    moves = would_stop_being_provisional(new)
    print(f"apply_verdicts: {len(moves)} check 6 cell(s) stop being provisional.")
    for pid, eid in moves:
        print(f"  {pid:<30} on {eid}")

    if "--write" not in argv:
        print("\napply_verdicts: nothing written. Add --write to record them.")
        return 0

    doc = {"_comment": HEAD, "verdicts": dict(sorted(new.items()))}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\napply_verdicts: wrote {OUT.relative_to(HERE.parent)}")
    if "--rebuild" in argv:
        # THE BUILD IS WHAT PUTS THE VERDICT ON THE EDGE, and the ladder reads the
        # edge. Run in one go so the two files cannot be a rebuild apart.
        for cmd in (["dep_records.py", "--build"], ["build_ladder.py"],
                    ["build_ladder_all.py"]):
            r = subprocess.run([sys.executable, *cmd], cwd=HERE,
                               capture_output=True, text=True)
            print(f"  {cmd[0]}: {'ok' if r.returncode == 0 else 'FAILED'}")
            if r.returncode:
                print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
                return 1
    else:
        print("apply_verdicts: run `python3 sources/dep_records.py --build` and the two "
              "ladder builders, or pass --rebuild.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

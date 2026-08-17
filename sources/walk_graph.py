"""
Schema-blind walk of data/graph. The acceptance test for build_graph.py.

Schema-blind means exactly that: this script knows a node has an `id` and a
`kind`, and an edge has a `rel`, a `from` and a `to`. It knows NOTHING about
what act, measure, sector or country mean, and it has no table of which
relations connect which kinds. If the graph is only navigable by a reader who
already knows the domain, it is not a graph, it is a JSON dump -- so the test
is deliberately ignorant.

    python3 sources/walk_graph.py                  # walk from sector:cement
    python3 sources/walk_graph.py measure:iaa:LM-01 --depth 2
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "data" / "graph"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("start", nargs="?", default="sector:cement")
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--limit", type=int, default=6, help="edges shown per relation")
    args = ap.parse_args()

    nodes = {n["id"]: n for n in json.loads((GRAPH / "nodes.json").read_text("utf-8"))}
    edges = json.loads((GRAPH / "edges.json").read_text("utf-8"))

    out = defaultdict(list)
    inc = defaultdict(list)
    for e in edges:
        out[e["from"]].append(e)
        inc[e["to"]].append(e)

    if args.start not in nodes:
        print(f"no such node: {args.start}")
        return 1

    print(f"{len(nodes)} nodes, {len(edges)} edges\n")

    seen: set[str] = set()
    frontier = [args.start]
    for depth in range(args.depth):
        nxt: list[str] = []
        for nid in frontier:
            if nid in seen:
                continue
            seen.add(nid)
            show(nid, nodes, out, inc, args.limit, depth)
            for e in out[nid] + inc[nid]:
                nxt += [e["from"], e["to"]]
        frontier = [n for n in dict.fromkeys(nxt) if n not in seen]

    # The claim the walk has to earn: every edge end is a node that exists.
    dangling = [e for e in edges if e["from"] not in nodes or e["to"] not in nodes]
    naked = [e for e in edges if not e.get("since") or not e.get("evidence", {}).get("source")]
    print("\n--- invariants ---")
    print(f"dangling edge ends            : {len(dangling)}")
    print(f"edges missing since/evidence  : {len(naked)}")
    reachable = walk_all(args.start, out, inc)
    print(f"reachable from {args.start:<16}: {len(reachable)} / {len(nodes)} nodes")
    orphans = [n for n in nodes if not out[n] and not inc[n]]
    print(f"nodes with no edge at all     : {len(orphans)}"
          + (f"  {orphans[:5]}" if orphans else ""))
    return 1 if (dangling or naked) else 0


def show(nid, nodes, out, inc, limit, depth):
    pad = "  " * depth
    n = nodes[nid]
    print(f"{pad}{n['id']}  [{n['kind']}]")
    print(f"{pad}  {n.get('label', '')[:110]}")
    grouped = defaultdict(list)
    for e in out[nid]:
        grouped[f"-> {e['rel']}"].append(e["to"])
    for e in inc[nid]:
        grouped[f"<- {e['rel']}"].append(e["from"])
    for rel in sorted(grouped):
        targets = grouped[rel]
        head = ", ".join(targets[:limit])
        more = f" (+{len(targets) - limit} more)" if len(targets) > limit else ""
        print(f"{pad}  {rel:<18} {len(targets):>3}  {head}{more}")
    print()


def walk_all(start, out, inc) -> set[str]:
    seen, stack = {start}, [start]
    while stack:
        nid = stack.pop()
        for e in out[nid] + inc[nid]:
            for end in (e["from"], e["to"]):
                if end not in seen:
                    seen.add(end)
                    stack.append(end)
    return seen


if __name__ == "__main__":
    raise SystemExit(main())

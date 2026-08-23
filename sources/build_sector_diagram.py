"""
Lay out one sector's transition diagram, deterministically, at build time.

    python3 build_sector_diagram.py            # writes data/transition/diagrams/*.json
    python3 build_sector_diagram.py --check    # rebuilds and diffs; non-zero on drift

WHY THE LAYOUT IS COMPUTED HERE AND NOT IN THE BROWSER
======================================================
Same reason the finding diagrams are: a layout engine in the page makes the
picture a function of the reader's browser, and this picture is an argument.
Coordinates computed here are reviewable in a diff, identical for everybody, and
cheap to render. The component that draws it does no layout at all -- it draws
what this file says and adds hover.

WHAT IS IN THE PICTURE
======================
Four columns, left to right, which is also the sentence the page is making:

    measures  ->  bottlenecks  <-  technologies  <-  projects

A measure worsens or relieves a constraint. A technology addresses it. A project
deploys the technology. The arrowheads keep the direction honest where the flow
runs against the reading order; the columns keep the sentence readable.

Only measures IN THE SECTOR VIEW appear -- the ones that passed the money or
linkage gate in build_importance.py. Drawing all 72 would be the register again,
with edges.

CROSSING REDUCTION, AND ITS LIMIT
=================================
One barycentre pass per column, left to right then right to left: a node sits at
the average height of what it connects to. It is not optimal and does not try to
be. What it buys is that neighbours in the graph are neighbours on the page,
which is the only property a reader actually uses. A second pass moved nothing
on cement and is not run.

STABILITY
=========
Ties break on id, never on dict order, so adding a project cannot silently
reshuffle the diagram above it. The output is sorted and pretty-printed, so a
data change shows up in the diff as the nodes that moved.
"""

from __future__ import annotations

import argparse
import json
import sys

import sector_map as sm
import build_importance as bi

OUT_DIR = sm.ROOT / "data" / "transition" / "diagrams"

# Geometry. One place, because the component reads the numbers rather than
# recomputing them: node boxes are positioned here and drawn there.
COL_X = {"measure": 0, "bottleneck": 300, "technology": 600, "project": 900}
NODE_W = 236
NODE_H = 38
ROW_GAP = 16
PAD = 12

KIND_ORDER = ["measure", "bottleneck", "technology", "project"]


def build(sector: str) -> dict:
    imp = bi.build(sector, bi.date.today().year)
    bottlenecks = [b for b in sm.load("bottleneck") if b["sector"] == sector]
    technologies = [t for t in sm.load("technology") if sector in t["sectors"]]
    projects = [p for p in sm.load("project") if p["sector"] == sector]
    in_view = [m for m in imp["measures"] if m["in_sector_view"]]

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def add(node_id, kind, label, sub, href, **attrs):
        nodes[node_id] = {"id": node_id, "kind": kind, "label": label, "sub": sub,
                          "href": href, **attrs}

    for m in in_view:
        money = m["money"]
        if money["computable"]:
            sub = (f"€{money['per_tonne']:,.2f}/t" if money["per_tonne"] is not None
                   else f"€{money['value'] / 1e6:,.0f}m")
            sub += f" · {money['direction']}"
        else:
            sub = f"linkage {m['bottleneck_linkage']['weight']}"
        file_slug, row_id = m["measure"].split(":", 1)
        add(f"measure:{m['measure']}", "measure", m["measure"], sub,
            f"/measures/{file_slug}/{row_id}",
            rank=m["rank"], direction=money["direction"])

    for b in bottlenecks:
        add(f"bottleneck:{b['id']}", "bottleneck", b["name"], b["type"],
            f"#bottleneck-{b['id']}", type=b["type"])
        for m in b.get("measures") or []:
            src = f"measure:{m['measure']}"
            if src in nodes:
                edges.append({"from": src, "to": f"bottleneck:{b['id']}",
                              "rel": m["rel"], "weight": m["weight"]})
        for tid in b.get("addressed_by", []):
            edges.append({"from": f"technology:{tid}", "to": f"bottleneck:{b['id']}",
                          "rel": "addresses", "weight": 1})

    for t in technologies:
        add(f"technology:{t['id']}", "technology", t["name"], t["readiness"]["level"],
            f"#technology-{t['id']}", readiness=t["readiness"]["level"])

    for p in projects:
        add(f"project:{p['id']}", "project", p["name"], f"{p['country']} · {p['status']}",
            f"/projects/{p['id']}", status=p["status"])
        for tid in p.get("technology", []):
            if f"technology:{tid}" in nodes:
                edges.append({"from": f"project:{p['id']}", "to": f"technology:{tid}",
                              "rel": "deploys", "weight": 1})

    # Drop edges whose endpoints did not make the picture. A technology that
    # addresses a bottleneck in another sector, a measure below the view gate:
    # the edge is real in the graph and has nothing to join here.
    edges = [e for e in edges if e["from"] in nodes and e["to"] in nodes]
    edges.sort(key=lambda e: (e["from"], e["to"], e["rel"]))

    columns = {k: [n for n in nodes.values() if n["kind"] == k] for k in KIND_ORDER}
    # Starting order per column: measures by rank (the ranking IS the order the
    # page argues for), everything else alphabetical so it is stable.
    columns["measure"].sort(key=lambda n: (n["rank"], n["id"]))
    for k in ("bottleneck", "technology", "project"):
        columns[k].sort(key=lambda n: n["label"].lower())

    neighbours: dict[str, list[str]] = {n: [] for n in nodes}
    for e in edges:
        neighbours[e["from"]].append(e["to"])
        neighbours[e["to"]].append(e["from"])

    def positions(col):
        return {n["id"]: i for i, n in enumerate(col)}

    def barycentre(col, fixed_pos):
        def key(n):
            ns = [fixed_pos[x] for x in neighbours[n["id"]] if x in fixed_pos]
            return (sum(ns) / len(ns) if ns else 1e9, n["label"].lower(), n["id"])
        col.sort(key=key)

    # Left to right, then back. Measures keep their ranking order in both
    # passes: the column that carries the argument does not get reordered to
    # make the lines prettier.
    for i in range(1, len(KIND_ORDER)):
        barycentre(columns[KIND_ORDER[i]], positions(columns[KIND_ORDER[i - 1]]))
    for i in range(len(KIND_ORDER) - 2, 0, -1):
        barycentre(columns[KIND_ORDER[i]], positions(columns[KIND_ORDER[i + 1]]))

    tallest = max(len(c) for c in columns.values())
    height = tallest * NODE_H + (tallest - 1) * ROW_GAP + 2 * PAD

    for kind, col in columns.items():
        span = len(col) * NODE_H + (len(col) - 1) * ROW_GAP
        top = (height - span) / 2
        for i, n in enumerate(col):
            n["x"] = COL_X[kind]
            n["y"] = round(top + i * (NODE_H + ROW_GAP), 1)
            n["w"] = NODE_W
            n["h"] = NODE_H

    ordered = [n for k in KIND_ORDER for n in columns[k]]
    return {
        "_comment": [
            "BUILT FILE — do not edit. sources/build_sector_diagram.py computes the layout;",
            "web/components/TransitionDiagram.tsx draws it and adds nothing but hover.",
            "Coordinates are in the diagram's own units; the component scales the viewBox.",
        ],
        "sector": sector,
        "width": COL_X[KIND_ORDER[-1]] + NODE_W + 2 * PAD,
        "height": round(height, 1),
        "columns": [{"kind": k, "x": COL_X[k], "count": len(columns[k])} for k in KIND_ORDER],
        "nodes": ordered,
        "edges": edges,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sector", action="append", default=None)
    args = ap.parse_args()

    sectors = args.sector or ["cement"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = False
    for sector in sectors:
        doc = build(sector)
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = OUT_DIR / f"{sector.replace('/', '__')}.json"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"build_sector_diagram: {path} is stale or missing — rebuild it",
                      file=sys.stderr)
                failed = True
                continue
            print(f"build_sector_diagram: --check, {sector} matches "
                  f"({len(doc['nodes'])} nodes, {len(doc['edges'])} edges)")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"build_sector_diagram: wrote {path} — "
                  f"{len(doc['nodes'])} nodes, {len(doc['edges'])} edges, "
                  f"{doc['width']}x{doc['height']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

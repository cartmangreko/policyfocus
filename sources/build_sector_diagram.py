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

WHAT A MEASURE NODE SAYS
========================
Its short label, not its id. `cbam:FIN-03` is how the register, the graph and
the gates name a measure and it tells a reader nothing; the label is computed
from data/transition/measure_labels.json by one template shared across sectors.
The id is still on the node, in `measure_id`, and the component prints it in the
hover detail -- so the thing you can look up has not been hidden, it has stopped
being the headline.

Three gates run here, at the point the label is made rather than on a page
review: the label exists for every measure in the view, it is unique within this
diagram (two nodes reading alike is a picture that lies), and it carries no word
from sources/display_vocabulary.py.

THE STATIC COPY, AND WHO IT IS FOR
==================================
The same picture is also written as a standalone SVG under web/public/diagrams/.
On a phone the interactive diagram is not worth its weight -- there is no hover,
the columns do not fit, and a reader pinching at a 1160-unit canvas inside a
375-point viewport is fighting the page. So small screens get the flat file,
linked so a tap opens it full size, and the component is not rendered at all.

It carries literal hexes because a file served on its own has no stylesheet.
They come from sources/design_tokens.py, which reads them out of globals.css, so
there is still exactly one definition of the diagram palette and the colour gate
still governs it.

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

import design_tokens as dt
import display_vocabulary as dv
import sector_map as sm
import build_importance as bi

OUT_DIR = sm.ROOT / "data" / "transition" / "diagrams"
STATIC_DIR = sm.ROOT / "web" / "public" / "diagrams"

# Geometry. One place, because the component reads the numbers rather than
# recomputing them: node boxes are positioned here and drawn there.
COL_X = {"measure": 0, "bottleneck": 300, "technology": 600, "project": 900}
NODE_W = 236
NODE_H = 38
ROW_GAP = 16
PAD = 12

KIND_ORDER = ["measure", "bottleneck", "technology", "project"]


def measure_label(measure_id: str, labels: dict) -> str:
    """One measure's short label, or a build failure saying which entry to add."""
    entry = labels.get(measure_id)
    if entry is None:
        raise SystemExit(
            f"build_sector_diagram: {measure_id} is in a sector view and has no entry in "
            f"data/transition/measure_labels.json — a node cannot be drawn without a name, "
            f"and the id is not a name"
        )
    instrument = entry.get("instrument")
    if instrument is not None and instrument not in sm.INSTRUMENTS:
        raise SystemExit(
            f"build_sector_diagram: {measure_id} instrument {instrument!r} is not in "
            f"sector_map.INSTRUMENTS {sm.INSTRUMENTS}"
        )
    label = sm.short_label(entry)
    if len(label) > sm.MAX_SHORT_LABEL:
        raise SystemExit(
            f"build_sector_diagram: {measure_id} label {label!r} is {len(label)} characters, "
            f"over the {sm.MAX_SHORT_LABEL} a node can draw without an ellipsis"
        )
    dv.check(label, f"build_sector_diagram: {measure_id}")
    return label


def build(sector: str) -> dict:
    imp = bi.build(sector, bi.date.today().year)
    labels = sm.measure_labels()
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
        add(f"measure:{m['measure']}", "measure", measure_label(m["measure"], labels), sub,
            f"/measures/{file_slug}/{row_id}",
            rank=m["rank"], direction=money["direction"], measure_id=m["measure"])

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
    seen: dict[str, str] = {}
    for n in nodes.values():
        if n["kind"] != "measure":
            continue
        if n["label"] in seen:
            raise SystemExit(
                f"build_sector_diagram: {sector}: {n['measure_id']} and {seen[n['label']]} both "
                f"label as {n['label']!r} — two nodes reading alike is a picture that lies"
            )
        seen[n["label"]] = n["measure_id"]

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


# What the standalone file needs as literals. Fails loudly rather than falling
# back to a colour, because a diagram drawn in a default grey is a diagram that
# has silently stopped saying which kind each node is.
STATIC_TOKENS = ("--ink", "--ink-55", "--paper", "--card", "--rule",
                 "--claret", "--pine",
                 "--dg-measure", "--dg-bottleneck", "--dg-technology", "--dg-project")

KIND_TOKEN = {"measure": "--dg-measure", "bottleneck": "--dg-bottleneck",
              "technology": "--dg-technology", "project": "--dg-project"}
REL_TOKEN = {"worsens": "--dg-measure", "relieves": "--dg-measure",
             "addresses": "--dg-technology", "deploys": "--dg-project"}


def _edge_path(a: dict, b: dict) -> str:
    """The same curve web/components/TransitionDiagram.tsx draws. Duplicated
    deliberately and kept to four lines: the alternative is a layout engine
    shared across two languages, and this is a cubic with one control offset."""
    forward = a["x"] < b["x"]
    x1 = a["x"] + a["w"] if forward else a["x"]
    x2 = b["x"] if forward else b["x"] + b["w"]
    y1, y2 = a["y"] + a["h"] / 2, b["y"] + b["h"] / 2
    dx = max(40, abs(x2 - x1) * 0.45) * (1 if forward else -1)
    return f"M {x1} {y1} C {x1 + dx} {y1}, {x2 - dx} {y2}, {x2} {y2}"


def static_svg(doc: dict) -> str:
    """The diagram as a file that stands on its own: no CSS, no script, no
    hover. What a phone gets, and what the export button has always produced."""
    c = dt.require(*STATIC_TOKENS)
    by_id = {n["id"]: n for n in doc["nodes"]}
    pad_bottom = 34
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {doc["width"]} '
        f'{doc["height"] + pad_bottom}" width="{doc["width"]}" '
        f'height="{doc["height"] + pad_bottom}" fill="none" '
        f'role="img" aria-label="{doc["sector"]}: measures, bottlenecks, technologies '
        f'and projects, and how they connect">',
        f'<rect width="{doc["width"]}" height="{doc["height"] + pad_bottom}" '
        f'fill="{c["--paper"]}"/>',
        "<defs>",
    ]
    for rel, token in sorted(set(REL_TOKEN.items())):
        out.append(
            f'<marker id="a-{rel}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 1 L 7 4 L 0 7 z" fill="{c[token]}"/></marker>')
    out.append("</defs>")

    for e in doc["edges"]:
        a, b = by_id.get(e["from"]), by_id.get(e["to"])
        if not a or not b:
            continue
        dash = ' stroke-dasharray="5 3"' if e["rel"] == "relieves" else ""
        out.append(
            f'<path d="{_edge_path(a, b)}" stroke="{c[REL_TOKEN[e["rel"]]]}" '
            f'stroke-width="{1.6 if e["weight"] >= 1 else 1}"{dash} opacity="0.85" '
            f'marker-end="url(#a-{e["rel"]})" fill="none"/>')

    for n in doc["nodes"]:
        hue = c[KIND_TOKEN[n["kind"]]]
        sub_fill = c["--ink-55"]
        if n.get("direction") == "cost":
            sub_fill = c["--claret"]
        elif n.get("direction") == "support":
            sub_fill = c["--pine"]
        label = n["label"] if len(n["label"]) <= 30 else n["label"][:29] + "\u2026"
        out.append(
            f'<g><rect x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" rx="2" '
            f'fill="{c["--card"]}" stroke="{c["--rule"]}" stroke-width="1"/>'
            f'<rect x="{n["x"]}" y="{n["y"]}" width="3" height="{n["h"]}" fill="{hue}"/>'
            f'<text x="{n["x"] + 12}" y="{n["y"] + 16}" font-family="Helvetica Neue,Helvetica,'
            f'Arial,sans-serif" font-size="12" font-weight="500" fill="{c["--ink"]}">'
            f'{_xml(label)}</text>'
            f'<text x="{n["x"] + 12}" y="{n["y"] + 29}" font-family="ui-monospace,Menlo,'
            f'monospace" font-size="11" fill="{sub_fill}">{_xml(n["sub"])}</text></g>')

    out.append(
        f'<text x="12" y="{doc["height"] + 22}" font-family="ui-monospace,Menlo,monospace" '
        f'font-size="12" fill="{c["--ink-55"]}">eufabric \u00b7 {_xml(doc["sector"])}</text>')
    out.append("</svg>")
    return "".join(out) + "\n"


def _xml(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sector", action="append", default=None)
    args = ap.parse_args()

    sectors = args.sector or ["cement"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    failed = False
    for sector in sectors:
        doc = build(sector)
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = OUT_DIR / f"{sector.replace('/', '__')}.json"
        svg_path = STATIC_DIR / f"{sector.replace('/', '__')}.svg"
        svg = static_svg(doc)
        if args.check:
            stale = [p for p, want in ((path, text), (svg_path, svg))
                     if not p.exists() or p.read_text(encoding="utf-8") != want]
            if stale:
                for p in stale:
                    print(f"build_sector_diagram: {p} is stale or missing — rebuild it",
                          file=sys.stderr)
                failed = True
                continue
            print(f"build_sector_diagram: --check, {sector} matches "
                  f"({len(doc['nodes'])} nodes, {len(doc['edges'])} edges, + static SVG)")
        else:
            path.write_text(text, encoding="utf-8")
            svg_path.write_text(svg, encoding="utf-8")
            print(f"build_sector_diagram: wrote {path} and {svg_path.name} — "
                  f"{len(doc['nodes'])} nodes, {len(doc['edges'])} edges, "
                  f"{doc['width']}x{doc['height']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Build the ego views: data/graph/ego/<file>.json, one per register file.

    python3 build_ego_views.py            # write the views
    python3 build_ego_views.py --check    # recompute and diff against what is
                                          # stored; non-zero exit on any drift

An ego view is one act's immediate neighbourhood in the graph, aggregated to
what a page can draw: the act at the centre, and around it every act it amends
or repeals, every act its measures depend on or cite, and every sector its
measures apply to. It is READ from data/graph/nodes.json + edges.json — the
files build_graph.py wrote and build_graph.py --check holds in sync with the
register — and it invents nothing: every spoke is an aggregation of edges that
exist, every count is the number of such edges, and every `detail` string is
composed here from those counts so the front end never writes a number.

AGGREGATION, NOT OMISSION. A register file's measures are up to 90 nodes; a
drawing of 90 spokes is noise. So measure-level edges are rolled up to their
target: "12 measures cite the CSDDD" is one spoke with count 12, and the
evidence trail is one hop away on the act page's own measure list. What is
NEVER rolled away is absence: a file whose measures apply to no sector at all
(the omnibus — its duties bind by company size and status, not by industry)
gets an explicit computed `note` saying exactly that, instead of a sector ring
that quietly is not there. Silence and absence look identical in a picture;
the note is what tells them apart.

DETERMINISM. Groups are in fixed order, spokes sorted by weight descending
then label, JSON written with sorted layout — byte-identical output for the
same inputs, so --check is a plain equality and runs in the web prebuild
alongside build_graph.py --check.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from build_graph import REGISTER_FILES, SECTORS

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
GRAPH = DATA / "graph"
OUT = GRAPH / "ego"

# Fixed group order: what the act does to other law first, then what its
# measures rest on, then who it lands on.
GROUPS = ("amends", "repeals", "depends_on", "cites", "sectors")

GROUP_TITLES = {
    "amends": "Amends",
    "repeals": "Repeals",
    "depends_on": "Depends on",
    "cites": "Cites",
    "sectors": "Sectors",
}


def load_graph() -> tuple[dict[str, dict], list[dict]]:
    nodes = {n["id"]: n for n in json.loads((GRAPH / "nodes.json").read_text(encoding="utf-8"))}
    edges = json.loads((GRAPH / "edges.json").read_text(encoding="utf-8"))
    return nodes, edges


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def build_view(file: str, nodes: dict[str, dict], edges: list[dict],
               act_to_file: dict[str, str]) -> dict:
    prefix = f"measure:{file}:"
    own_measures = {e["to"] for e in edges if e["rel"] == "contains" and e["to"].startswith(prefix)}
    centers = sorted({e["from"] for e in edges if e["rel"] == "contains" and e["to"].startswith(prefix)})
    if len(centers) != 1:
        raise SystemExit(f"EGO VIEWS NOT BUILT — {file!r} measures are contained by "
                         f"{len(centers)} acts ({centers}); an ego view has one centre")
    center = centers[0]

    # Self-reference is not a connection: the centre act, plus the acts it
    # amends, are the file's own body of law — the same exclusion
    # web/lib/acts.ts applies when naming an intermediating act.
    self_acts = {center} | {e["to"] for e in edges if e["rel"] == "amends" and e["from"] == center}

    def act_spoke(act_id: str, detail: str, weight: int) -> dict:
        target_file = act_to_file.get(act_id)
        return {
            "id": act_id,
            "kind": "act",
            "label": nodes[act_id]["label"],
            "file": target_file,
            "href": f"/acts/{target_file}" if target_file else None,
            "detail": detail,
            "weight": weight,
        }

    spokes: dict[str, list[dict]] = {g: [] for g in GROUPS}

    for rel in ("amends", "repeals"):
        for e in edges:
            if e["rel"] == rel and e["from"] == center:
                spokes[rel].append(act_spoke(e["to"], f"since {e['since']}", 0))

    counted: dict[str, dict[str, int]] = {"depends_on": defaultdict(int), "cites": defaultdict(int)}
    for e in edges:
        if e["rel"] in counted and e["from"] in own_measures and e["to"] not in self_acts:
            counted[e["rel"]][e["to"]] += 1
    for rel in ("depends_on", "cites"):
        for act_id, n in counted[rel].items():
            verb = ("depends on it" if n == 1 else "depend on it") if rel == "depends_on" \
                else ("cites it" if n == 1 else "cite it")
            spokes[rel].append(act_spoke(act_id, f"{plural(n, 'measure')} {verb}", n))

    named: dict[str, int] = defaultdict(int)
    reached: dict[str, int] = defaultdict(int)
    for e in edges:
        if e["rel"] == "applies_to" and e["from"] in own_measures:
            slug = e["to"].removeprefix("sector:")
            (named if e.get("basis") == "named" else reached)[slug] += 1
    for slug in set(named) | set(reached):
        parts = []
        if named.get(slug):
            parts.append(f"named by {plural(named[slug], 'measure')}")
        if reached.get(slug):
            parts.append(f"reached by {plural(reached[slug], 'measure')}")
        spokes["sectors"].append({
            "id": f"sector:{slug}",
            "kind": "sector",
            "label": SECTORS[slug],
            "file": None,
            "href": f"/sectors/{slug}",
            "detail": " · ".join(parts),
            "weight": named.get(slug, 0) + reached.get(slug, 0),
        })

    groups = [
        {"rel": g, "title": GROUP_TITLES[g],
         "spokes": sorted(spokes[g], key=lambda s: (-s["weight"], s["label"]))}
        for g in GROUPS if spokes[g]
    ]

    view = {
        "file": file,
        "center": {"id": center, "label": nodes[center]["label"], "file": file},
        "measure_count": len(own_measures),
        "groups": groups,
    }

    # The honesty note: a file that applies to no sector states so as a
    # computed fact, because on a drawing "no sector ring" and "sectors not
    # drawn" are indistinguishable.
    if not spokes["sectors"]:
        n_acts = len({s["id"] for g in groups for s in g["spokes"] if s["kind"] == "act"})
        view["note"] = (
            f"0 of this file's {view['measure_count']} measures names or reaches a sector. "
            f"Every connection shown is one of the {plural(n_acts, 'act')} its measures "
            "amend, cite or depend on."
        )
    return view


def build(write: bool = True) -> int:
    nodes, edges = load_graph()
    act_to_file: dict[str, str] = {}
    for e in edges:
        if e["rel"] == "contains":
            act_to_file[e["from"]] = e["to"].split(":")[1]

    rendered: dict[str, str] = {}
    for file in REGISTER_FILES:
        view = build_view(file, nodes, edges, act_to_file)
        rendered[file] = json.dumps(view, ensure_ascii=False, indent=2) + "\n"

    if write:
        OUT.mkdir(exist_ok=True)
        for stale in OUT.glob("*.json"):
            if stale.stem not in rendered:
                stale.unlink()
        for file, text in rendered.items():
            (OUT / f"{file}.json").write_text(text, encoding="utf-8")
        print(f"build_ego_views: wrote {len(rendered)} view(s) to {OUT.relative_to(DATA.parent)}/")
        return 0

    # --check: what is stored must be byte-identical to what the graph says.
    problems = []
    for file, text in rendered.items():
        path = OUT / f"{file}.json"
        if not path.exists():
            problems.append(f"{path.relative_to(DATA.parent)} is missing")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"{path.relative_to(DATA.parent)} is stale — rerun build_ego_views.py")
    for path in sorted(OUT.glob("*.json")) if OUT.exists() else []:
        if path.stem not in rendered:
            problems.append(f"{path.relative_to(DATA.parent)} matches no register file")
    if problems:
        print(f"EGO VIEWS STALE — {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"build_ego_views: --check, {len(rendered)} view(s) match the graph")
    return 0


if __name__ == "__main__":
    sys.exit(build(write="--check" not in sys.argv[1:]))

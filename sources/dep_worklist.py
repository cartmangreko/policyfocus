"""The order to verdict the edges in, printed from edges.json rather than pasted.

    python3 dep_worklist.py            # print
    python3 dep_worklist.py --write    # print and write dependency_worklist.md
    python3 dep_worklist.py --csv      # write sources/verdicts_worklist.csv
    python3 dep_worklist.py --csv-round2   # …and the second round, from
                                           #    sources/verdicts_round2.json

WHY THIS IS A SCRIPT. Every edge in edges.json carries `verdict: null` and the
verdict is the reader's field. The list of what is still unverdicted is therefore
a number that changes every time one is filled in, and a pasted list would be
wrong by the following morning. This regenerates.

THE ORDER IS THE RULING'S. Edges matched to an admitted register row come first
and are grouped by row, because those are the ones a verdict moves something: a
row gains a supplier, or it does not. Then the edges that name a site this
register does not hold, grouped by site, because those are the census's question.
Then everything else, grouped by node.

WHAT EACH LINE CARRIES is what the ruling asked for and nothing else: firmness,
speaker, date, source, verdict. `firmness` is first because rung 6 of the
confirmation ladder passes on `contract` and on nothing else, so a reader
verdicting for the ladder can stop at the first column.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_OUT = HERE / "verdicts_worklist.csv"
ROUND2_IN = HERE / "verdicts_round2.json"
ROUND2_OUT = HERE / "verdicts_worklist_round2.csv"

# THE COLUMNS, AND THE LAST TWO ARE THE ONLY ONES A PERSON FILLS IN. Everything
# before `verdict` is copied out of edges.json so the reader does not have to open
# it: the sentence the firmness rests on, who said it, when, and the hash of the
# page it was read from. `verdict` takes one of three words and `note` takes
# whatever the reader wants to say; apply_verdicts.py refuses anything else.
CSV_FIELDS = [
    "row_id", "row_name", "sector", "edge_id", "supplier", "customer_as_stated",
    "site_as_stated", "edge_kind", "firmness", "speaker", "source_type", "date",
    "date_precision", "quantity", "match_basis", "sentence", "source_url",
    "source_sha256", "captured_at", "archived", "verdict", "note",
]
VERDICTS = ("accept", "reject", "unclear")


def load() -> tuple[list[dict], dict[str, dict]]:
    edges = json.loads((HERE / "edges.json").read_text())["edges"]
    nodes = {n["id"]: n for n in json.loads((HERE / "nodes.json").read_text())["nodes"]}
    return edges, nodes


def line(e: dict, nodes: dict) -> list[str]:
    q = e["quantity"]
    out = [f"- **{e['id']}**  `{e['firmness']}`  {e['date']}"
           + (f" ({e['date_precision']})" if e["date_precision"] != "day" else "")
           + f"  speaker: {e['speaker']}  verdict: **null**",
           f"  - {nodes[e['node_id']]['name']} → {e['customer_name_as_stated']}"
           + (f" — {q['value']:,g} {q['unit']}" if q else " — no quantity stated"),
           f"  - source: {e['url']}"]
    if e["captured_at"]:
        out.append(f"  - copy on file captured {e['captured_at']}")
    if e["inherited_by"]:
        out.append(f"  - inherited by {e['inherited_by']['node_id']} "
                   f"from {e['inherited_by']['since']}")
    out.append(f"  - cited for firmness: “{e['firmness_basis']}”")
    return out


def sha_for(url: str) -> str:
    """The SHA-256 of the page this reading was made against, from the fetch cache.

    THE HASH IS WHAT MAKES THE SENTENCE CHECKABLE. A verdict is a person agreeing
    that a sentence says what the edge claims, and a sentence belongs to a
    particular set of bytes; the url alone can have been rewritten since. Empty
    where the cache has no body — some readings rest on an archive capture this
    machine holds only as a re-read, and the column says so by being blank rather
    than by carrying a hash of the wrong copy.
    """
    import dep_text as T
    e = T.index().get(hashlib.sha1(url.encode()).hexdigest()[:16]) or {}
    return e.get("sha256") or "" if T.original(url) else ""


def csv_rows() -> list[dict]:
    """One line per edge matched to a register row, grouped by row.

    ALL SECTORS, and the order is the worklist's own: rows alphabetically, edges
    within a row oldest first, which is the order a relationship happened in.
    """
    edges, nodes = load()
    rows = {p["id"]: p for p in json.loads(
        (HERE.parent / "data" / "transition" / "projects.json")
        .read_text(encoding="utf-8"))["projects"]}
    matched = [e for e in edges if e["project_id"]]
    by_row = collections.defaultdict(list)
    for e in matched:
        by_row[e["project_id"]].append(e)
    out = []
    for pid in sorted(by_row):
        row = rows.get(pid, {})
        for e in sorted(by_row[pid], key=lambda x: (x["date"], x["id"])):
            q = e["quantity"]
            out.append({
                "row_id": pid,
                "row_name": row.get("name", ""),
                "sector": row.get("sector", ""),
                "edge_id": e["id"],
                "supplier": nodes[e["node_id"]]["name"],
                "customer_as_stated": e["customer_name_as_stated"],
                "site_as_stated": e["site_as_stated"] or "",
                "edge_kind": e["edge_kind"],
                "firmness": e["firmness"],
                "speaker": e["speaker"],
                "source_type": e["source_type"],
                "date": e["date"],
                "date_precision": e["date_precision"],
                "quantity": f"{q['value']:g} {q['unit']}" if q else "",
                "match_basis": e["match_basis"],
                "sentence": e["firmness_basis"] or "",
                "source_url": e["url"],
                "source_sha256": sha_for(e["url"]),
                "captured_at": e["captured_at"] or "",
                "archived": "" if e["archived"] is None else str(bool(e["archived"])).lower(),
                "verdict": "",
                "note": "",
            })
    return out


def write_csv() -> int:
    """Write the file, and NEVER OVER A VERDICT ALREADY IN IT.

    The worklist regenerates because edges.json does; a person filling it in over a
    week must not lose a morning's work to a rebuild. Any verdict and note already
    on file for an edge id is carried into the new file, and an edge that has left
    the graph is reported rather than silently dropped.
    """
    keep = {}
    if CSV_OUT.exists():
        with CSV_OUT.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("verdict") or r.get("note"):
                    keep[r["edge_id"]] = (r.get("verdict", ""), r.get("note", ""))
    rows = csv_rows()
    ids = {r["edge_id"] for r in rows}
    for r in rows:
        if r["edge_id"] in keep:
            r["verdict"], r["note"] = keep[r["edge_id"]]
    gone = sorted(set(keep) - ids)
    with CSV_OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    n_rows = len({r["row_id"] for r in rows})
    print(f"verdicts_worklist.csv — {len(rows)} line(s) across {n_rows} register row(s), "
          f"{sum(1 for r in rows if r['verdict'])} already verdicted, "
          f"{len(rows) - sum(1 for r in rows if r['verdict'])} open.")
    print(f"  verdict takes one of: {' | '.join(VERDICTS)}. Empty means not yet read.")
    if gone:
        print(f"  {len(gone)} verdict(s) were on edges no longer in the graph and are NOT "
              f"in the new file: {', '.join(gone)}")
    return len(rows)


def write_round2() -> int:
    """The second round: the twelve edges the first could not be ruled on.

    SAME BUILDER, SAME COLUMNS, THREE MORE. `why_reread` says what sent the edge
    back, `sentence_on_reread` carries what the source actually states where that
    differs from what the edge carries, and `what_the_re_read_found` is the finding
    — including, twice, that the document states no agreement at all, which is an
    answer and not a gap.

    `copy_on_file` is the column that decides how much the sentence is worth:
    `original` means the bytes are the artefact the cache index records and the
    citation gate rules on them; `re-read` means this machine holds a later copy of
    the same address, the gate declines, and the sentence is as good as today's
    page. Neither is a verdict. The verdict column is empty, as it was in round one.
    """
    import dep_text as T
    pack = json.loads(ROUND2_IN.read_text(encoding="utf-8"))
    want = {e["edge_id"]: e for e in pack["edges"]}
    rows = [r for r in csv_rows() if r["edge_id"] in want]
    missing = sorted(set(want) - {r["edge_id"] for r in rows})
    if missing:
        raise SystemExit(f"dep_worklist --csv-round2: {', '.join(missing)} is not an "
                         f"edge matched to a register row")
    fields = CSV_FIELDS[:-2] + ["copy_on_file", "why_reread", "sentence_on_reread",
                                "what_the_re_read_found", "verdict", "note"]
    for r in rows:
        w = want[r["edge_id"]]
        r["copy_on_file"] = "original" if T.original(r["source_url"]) else "re-read"
        r["why_reread"] = w["why"]
        r["sentence_on_reread"] = w.get("sentence_on_reread", "")
        r["what_the_re_read_found"] = w.get("what_the_re_read_found", "")
    with ROUND2_OUT.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)
    orig = sum(1 for r in rows if r["copy_on_file"] == "original")
    print(f"verdicts_worklist_round2.csv — {len(rows)} line(s): "
          f"{sum(1 for r in rows if not r['sentence_on_reread'])} that had no sentence "
          f"at all and now carry one, {sum(1 for r in rows if r['sentence_on_reread'])} "
          f"ruled unclear and re-read.")
    print(f"  {orig} rest on the artefact the index records; {len(rows) - orig} on a "
          f"later re-read of the same address, where the citation gate declines to rule.")
    print(f"  verdict takes one of: {' | '.join(VERDICTS)}. All twelve are empty.")
    return len(rows)


def render() -> str:
    edges, nodes = load()
    matched = [e for e in edges if e["project_id"]]
    outside = [e for e in edges if e["outside_perimeter"]]
    done = {e["id"] for e in matched} | {e["id"] for e in outside}
    rest = [e for e in edges if e["id"] not in done]
    L: list[str] = [
        "# Verdict worklist — brief 9",
        "",
        "Regenerated by `python3 sources/dep_worklist.py --write`. Every edge below "
        "carries `verdict: null`; filling one in is an edit to `sources/dep_readings.py` "
        "and a rebuild, not an edit to this file.",
        "",
        f"**{len(matched)} matched to a register row · {len(outside)} at a site this "
        f"register does not hold · {len(rest)} neither · {len(edges)} edges in total.**",
        "",
        "Firmness counts across the whole file: "
        + ", ".join(f"{k} {v}" for k, v in
                    sorted(collections.Counter(e["firmness"] for e in edges).items()))
        + ". Rung 6 of the confirmation ladder passes on `contract` only.",
        "",
        "---",
        "",
        "## 1. Matched to a register row — work these first",
        "",
        "A verdict here attaches a supplier to an admitted row, or refuses to. "
        "`match_basis` says what the link rests on: `site only` is a place name with no "
        "company agreement and is the weakest of the three.",
        "",
    ]
    by_row = collections.defaultdict(list)
    for e in matched:
        by_row[e["project_id"]].append(e)
    for pid in sorted(by_row):
        group = sorted(by_row[pid], key=lambda e: e["date"])
        bases = sorted({e["match_basis"] for e in group})
        L += [f"### `{pid}` — {len(group)} edge(s), matched on {', '.join(bases)}", ""]
        for e in group:
            L += line(e, nodes)
        L.append("")

    L += ["---", "",
          "## 2. A named site this register does not hold",
          "",
          "`outside_perimeter: true`. These count toward the supplier's totals and "
          "toward no project. Grouped by the site as the supplier stated it.",
          ""]
    by_site = collections.defaultdict(list)
    for e in outside:
        by_site[e["site_as_stated"]].append(e)
    for site in sorted(by_site):
        group = sorted(by_site[site], key=lambda e: e["date"])
        sectors = sorted({e["sector"] for e in group if e["sector"]})
        L += [f"### {site}" + (f" — {', '.join(sectors)}" if sectors else ""), ""]
        for e in group:
            L += line(e, nodes)
        L.append("")

    L += ["---", "",
          "## 3. Everything else",
          "",
          "A customer nobody named, or a company named without a site. Grouped by node.",
          ""]
    by_node = collections.defaultdict(list)
    for e in rest:
        by_node[e["node_id"]].append(e)
    for nid in sorted(by_node):
        group = sorted(by_node[nid], key=lambda e: e["date"])
        L += [f"### {nodes[nid]['name']} — {len(group)} edge(s)", ""]
        for e in group:
            L += line(e, nodes)
        L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if "--csv-round2" in sys.argv[1:]:
        write_round2()
        raise SystemExit(0)
    if "--csv" in sys.argv[1:]:
        write_csv()
        raise SystemExit(0)
    text = render()
    if "--write" in sys.argv[1:]:
        (HERE / "dependency_worklist.md").write_text(text)
        print(f"dependency_worklist.md — {text.count(chr(10))} lines")
    else:
        print(text)

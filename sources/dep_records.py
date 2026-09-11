"""Where the sweep's readings are written down, and the two files they become.

    python3 dep_records.py --check       # shape, vocabulary and cache checks
    python3 dep_records.py --build       # write nodes.json / edges.json / unmatched

A READING IS A HAND ENTRY AND IS MEANT TO LOOK LIKE ONE. Nothing in this module is
derived: every edge below is one sentence somebody read in one cached page, and the
url on it is the page. dep_digest.py put the sentence in front of the reader; this
file is what the reader concluded. Keeping the two apart is the point -- the digest
can be regenerated from the cache at any time and will not change what was ruled.

`add_edge` takes the brief's fields and no others, plus `note`, which is declared in
DECISION D-3: several readings are only honest with a sentence saying what was and
was not stated, and a null field cannot carry that.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import dep_sweep as S

HERE = Path(__file__).resolve().parent
EDGES: list[dict] = []
NODE_CAPACITY: dict[str, list[dict]] = {}
UNMATCHED: dict[str, dict] = {}

_IDX: dict[str, list[str]] | None = None


def _idx() -> dict[str, list[str]]:
    global _IDX
    if _IDX is None:
        _IDX = S.register_index()
    return _IDX


def resolve(customer: str, site: str = "") -> tuple[str | None, str | None]:
    """(project_id, ambiguity note) for a customer name as the supplier stated it."""
    hits = S.matches(f"{customer} {site}", _idx())
    ids = sorted({i for _, cand in hits for i in cand})
    if not ids:
        return None, None
    if len(ids) == 1:
        return ids[0], None
    return None, ("names " + ", ".join(a for a, _ in hits) +
                  ", which in this register could be " + " or ".join(ids) +
                  "; the source does not say which — DECISION D-2")


def add_edge(node_id: str, customer: str, edge_kind: str, speaker: str,
             source_type: str, url: str, date: str, date_precision: str = "day",
             quantity: tuple[float, str] | None = None, project_id: str | None = None,
             site: str = "", note: str | None = None, country: str | None = None,
             sector: str | None = None) -> dict:
    pid, amb = (project_id, None) if project_id else resolve(customer, site)
    if amb:
        note = f"{note}. {amb}" if note else amb
    e = {"id": f"e{len(EDGES) + 1:04d}",
         "project_id": pid,
         "customer_name_as_stated": customer,
         "node_id": node_id,
         "edge_kind": edge_kind,
         "quantity": None if quantity is None else {"value": quantity[0], "unit": quantity[1]},
         "speaker": speaker,
         "source_type": source_type,
         "url": url,
         "date": date,
         "date_precision": date_precision,
         "verdict": None,
         "note": note}
    EDGES.append(e)
    if pid is None and country is not None:
        u = UNMATCHED.setdefault(customer, {
            "customer_name_as_stated": customer, "country": country,
            "sector_guess": sector, "sources": [], "edge_ids": []})
        if url not in u["sources"]:
            u["sources"].append(url)
        u["edge_ids"].append(e["id"])
    return e


def add_capacity(node_id: str, value: float, unit: str, basis: str, speaker: str,
                 source_type: str, url: str, date: str, date_precision: str = "day",
                 note: str | None = None) -> None:
    NODE_CAPACITY.setdefault(node_id, []).append(
        {"value": value, "unit": unit, "basis": basis, "speaker": speaker,
         "source_type": source_type, "url": url, "date": date,
         "date_precision": date_precision, "note": note})


# --- gates and output --------------------------------------------------------

def check() -> list[str]:
    """Every way a reading can be wrong that a machine can see.

    THE URL CHECK IS THE ONE THAT EARNS ITS KEEP. Every url in dep_readings.py was
    typed by a person from a digest, and a mistyped slug on a supplier's newsroom
    does not 404 loudly in a file -- it sits there looking like a citation. If a url
    is not in the fetch cache with a 200 and a SHA-256, then the page behind this
    reading was never read at this address, and the reading is unsupported.
    """
    import dep_text as T
    idx, bad = T.index(), []
    ok = {e["url"] for e in idx.values() if e.get("sha256")}
    seen_ids = set()
    for e in EDGES:
        w = f"edge {e['id']} ({e['node_id']} / {e['customer_name_as_stated']})"
        if e["id"] in seen_ids:
            bad.append(f"{w}: duplicate id")
        seen_ids.add(e["id"])
        if e["url"] not in ok:
            bad.append(f"{w}: url not in the fetch cache as a 200 — {e['url']}")
        if e["edge_kind"] not in S.EDGE_KINDS:
            bad.append(f"{w}: edge_kind {e['edge_kind']!r} is not in the vocabulary")
        if e["speaker"] not in S.SPEAKERS:
            bad.append(f"{w}: speaker {e['speaker']!r} is not in the vocabulary")
        if e["source_type"] not in S.SOURCE_TYPES:
            bad.append(f"{w}: source_type {e['source_type']!r} is not in the vocabulary")
        if e["date_precision"] not in ("day", "month", "year"):
            bad.append(f"{w}: date_precision {e['date_precision']!r}")
        if not (S.PERIOD[0] <= e["date"] <= S.PERIOD[1]):
            bad.append(f"{w}: date {e['date']} is outside the sweep period")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]):
            bad.append(f"{w}: date {e['date']!r} is not YYYY-MM-DD")
        if e["node_id"] not in {n[0] for n in S.NODES}:
            bad.append(f"{w}: node_id {e['node_id']!r} is not on the perimeter")
    for nid, caps in NODE_CAPACITY.items():
        for c in caps:
            w = f"capacity on {nid} ({c['value']} {c['unit']})"
            if c["url"] not in ok:
                bad.append(f"{w}: url not in the fetch cache as a 200 — {c['url']}")
            if c["basis"] not in S.BASES:
                bad.append(f"{w}: basis {c['basis']!r} is not in the vocabulary")
            if c["source_type"] not in S.SOURCE_TYPES:
                bad.append(f"{w}: source_type {c['source_type']!r}")
    return bad


SEARCHED: dict[str, dict] = {}     # node_id -> what was swept for it
OWNER: dict[str, dict] = {}        # project id -> owner-side search result


def searched(node_id: str, **kw) -> None:
    SEARCHED[node_id] = kw


def owner(project_id: str, urls_read: int, found: list[str], note: str = "") -> None:
    OWNER[project_id] = {"project_id": project_id, "sources_read": urls_read,
                         "supplier_or_store_named": found, "note": note}


def build() -> None:
    nodes = []
    for nid, kind, name, home, listing in S.NODES:
        nodes.append({"id": nid, "kind": kind, "name": name, "listing": listing,
                      "home": home,
                      "stated_capacity": NODE_CAPACITY.get(nid, []),
                      "sweep": SEARCHED.get(nid)})
    (HERE / "nodes.json").write_text(
        json.dumps({"_comment": NODES_COMMENT, "nodes": nodes},
                   indent=1, ensure_ascii=False) + "\n")
    (HERE / "edges.json").write_text(
        json.dumps({"_comment": EDGES_COMMENT, "edges": EDGES,
                    "owner_side": list(OWNER.values())},
                   indent=1, ensure_ascii=False) + "\n")
    (HERE / "dependency_unmatched.json").write_text(
        json.dumps({"_comment": UNMATCHED_COMMENT,
                    "customers": sorted(UNMATCHED.values(),
                                        key=lambda u: u["customer_name_as_stated"])},
                   indent=1, ensure_ascii=False) + "\n")


NODES_COMMENT = [
    "Suppliers and stores swept for Brief 9, and the capacity each STATES for itself.",
    "",
    "The perimeter is sources/dep_sweep.py:NODES and is fixed by the brief. `listing`",
    "is the node's own equity status, which decides whether an annual or quarterly",
    "report exists for it at all -- eleven of these twenty-seven are unlisted and",
    "publish no order backlog anywhere.",
    "",
    "`stated_capacity` IS A LIST AND IS NOT RECONCILED. A supplier states its capacity",
    "many times over six years and the figures do not agree, because they are answers",
    "to different questions: nameplate is what a line can build, backlog is what has",
    "been sold, delivery_commitment is what has been promised for a date. No value here",
    "is converted, averaged or superseded -- the 2022 Herxya nameplate and the 2025",
    "sentence saying those same lines are idling both stand, and the second is why the",
    "first cannot be read as output.",
    "",
    "`sweep` records what was actually read for this node: the index pages walked, how",
    "many items they listed, how many were fetched, and where the sweep could not go.",
    "A node with sweep null was not searched, which is a different fact from a node",
    "that was searched and yielded nothing.",
]
EDGES_COMMENT = [
    "One edge is one document stating one relationship between a supplier or store on",
    "the perimeter and a customer. Brief 9.",
    "",
    "AN EDGE IS A STATEMENT, NOT A STATE. The same order appears here two or three",
    "times -- as a letter of intent, as a firm contract, as a cancellation -- each with",
    "its own date and speaker, because the brief asks for what was said and not for a",
    "reconciled current position. Summing this file without reading `note` will",
    "double-count, and that is the correct behaviour for a file of statements.",
    "",
    "`quantity.unit` IS THE UNIT AS STATED, never converted. That is why some edges",
    "carry MW, some carry fuelling stations and some carry tonnes of CO2 a year, and",
    "why the docket's arithmetic section can only compare a subset of them.",
    "",
    "`project_id` is null when the customer matches no admitted row, AND when the",
    "customer names a company that holds several rows and the document does not say",
    "which site -- DECISION D-2. The two cases are told apart by `note`.",
    "",
    "`verdict` is null on every edge in this file. It is the reader's field.",
    "",
    "`owner_side` is the other direction: every admitted row whose own cached sources",
    "were re-read for supplier and store names. `supplier_or_store_named` empty means",
    "searched and none found. A row absent from this list was not searched.",
]
UNMATCHED_COMMENT = [
    "Customers a supplier named that match no admitted row in data/transition/projects.json.",
    "",
    "NO ROWS WERE CREATED. The brief is explicit and the reason is the perimeter: a",
    "cement customer that this register does not hold may be out of scope, or may be a",
    "gap, and a sweep of suppliers is not the instrument that decides which. `country`",
    "and `sector_guess` are what the supplier's own release says or implies, so that a",
    "later pass can sort these without re-reading every page.",
    "",
    "An UNDISCLOSED customer is not here. 'an undisclosed European client' is a customer",
    "nobody named, not a customer nobody matched, and putting it in this file would",
    "turn the supplier's silence into a candidate.",
]

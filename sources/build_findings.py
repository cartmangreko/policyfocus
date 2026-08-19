"""
The gate for findings -- the conclusion layer that sits above the register.

    python3 build_findings.py            # validate every finding, write the index
    python3 build_findings.py --check    # validate only, write nothing

A finding is a hand-authored claim of the form "this measure set means X for
sector Y". It is NOT extracted, NOT derived, and NOT trusted: everything it
asserts has to resolve against data the register already holds, or the build
stops. Same contract as the other gates in this directory -- non-zero exit on
any failure, deterministic output, nothing written until everything passes.

WHAT THIS GATE IS FOR. A finding is the one object on the site that a reader
cannot check by reading a source sentence: it is a sentence about many
provisions at once. So the honesty has to be structural. Six checks:

  1. SCHEMA. Required fields present, types right, id matches the filename,
     no duplicate ids, headline within length, date parses.
  2. MEASURE EVIDENCE RESOLVES. Every evidence.measures entry names a register
     file and a row id that exist. A finding with no measure evidence does not
     exist -- an empty list fails here rather than rendering a claim with no
     provenance.
  3. EXPOSURE EVIDENCE RESOLVES, INCLUDING THE NUMBER. The partner appears in
     the stated relation list for the stated view, AND the share the finding
     prints matches the stored share within 0.1pp. A finding may not assert a
     number the exposure data does not hold; approximately-right is a way of
     being wrong that a reader has no means of catching.
  4. CONTROLLED VOCABULARIES. sectors are app sector slugs (build_graph.SECTORS,
     the same vocabulary reconciliation_gate.py checks register rows against);
     files are register file slugs.
  5. BASIS STATUS. What the finding claims about the legal standing of its
     evidence must be what the manifest says. See STATUS_RULE below.
  6. TEMPLATE. One of the known templates, every one of which names an
     arithmetic shape. There is deliberately NO editorial template: a finding
     may only state what the data computes (counts, shares, chains,
     before/after deltas) — no judgment about importance, no recommendations.
     `check_template_set` holds that line structurally, so the escape hatch
     cannot be quietly re-added.

WHY THE INDEX IS AN OUTPUT AND NOT A DIRECTORY READ. data/findings/index.json is
written here, by the gate, after every check passes. The front end reads the
index and never the directory, so a finding that has not been through this file
cannot reach a page -- dropping a JSON file into the directory publishes
nothing. The index is sorted (date descending, then id) so a rebuild that
changes no finding produces no diff.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from build_graph import SECTORS as APP_SECTORS

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
FINDINGS_DIR = DATA / "findings"
INDEX_PATH = FINDINGS_DIR / "index.json"
DIAGRAMS_DIR = FINDINGS_DIR / "diagrams"
MANIFEST_PATH = HERE / "manifest.json"

SCHEMA_VERSION = 1
MAX_HEADLINE = 140

TEMPLATES = (
    "reach",
    "indirect_exposure",
    "support_mismatch",
    "net_position",
    "country_concentration",
)

# Templates that must never be in the set. `editorial` existed as an escape
# hatch for hand-written prose and was removed under the arithmetic-only rule
# in sources/scope.md ("A finding states arithmetic"): every template has to
# name a computable shape, and a template whose content is judgment cannot be
# checked by this gate at all. The check runs on every build so the hatch
# cannot be re-added without deleting this line and its reason.
EDITORIAL_TEMPLATES = ("editorial",)


def check_template_set() -> None:
    """The documented no-editorial-template check. Fails the build, not just
    the finding: a bad template SET is a defect in the gate itself."""
    banned = [t for t in TEMPLATES if t in EDITORIAL_TEMPLATES]
    if banned:
        print(
            f"FINDINGS NOT BUILT — template set contains editorial template(s) {banned}; "
            "findings are arithmetic-only (sources/scope.md, 'A finding states arithmetic')",
            file=sys.stderr,
        )
        sys.exit(1)

BASIS_STATUSES = ("adopted", "proposed", "mixed")
RELATIONS = ("supplier", "customer", "import_origin")

# Register file slug -> the manifest entries that file was read from, plus the
# declared status for the one file the manifest cannot answer for. The table
# lives in register_files.json rather than here because web/lib/files.ts needs
# the same mapping to build the coverage page: two copies of it would drift,
# and the drift would show up as a page calling a proposal settled law.
#
# A register file in neither the table nor the manifest is a hard failure
# rather than a default. Guessing the legal standing of a file is the one thing
# this gate exists to prevent.
_REGISTER_FILES = json.loads((HERE / "register_files.json").read_text(encoding="utf-8"))["files"]
FILE_MANIFEST_KEYS = {k: tuple(v.get("manifest_keys") or ()) for k, v in _REGISTER_FILES.items()}
DECLARED_STATUS = {
    k: (v["declared_status"],) for k, v in _REGISTER_FILES.items() if v.get("declared_status")
}

# STATUS_RULE. The set of statuses the referenced files actually carry decides
# what the finding is allowed to claim, in both directions:
#
#   {adopted}            -> "adopted"
#   {proposed}           -> "proposed"
#   {adopted, proposed}  -> "mixed"
#
# The brief states the one-way rule -- a finding citing a proposal may not claim
# `adopted`. This is that rule plus its mirror: a finding citing only law in
# force may not claim `mixed` or `proposed` either. Both directions mislead. A
# banner saying "subject to change" over settled law teaches a reader to ignore
# the banner, which is how the honest case stops working.
STATUS_RULE = {
    frozenset({"adopted"}): "adopted",
    frozenset({"proposed"}): "proposed",
    frozenset({"adopted", "proposed"}): "mixed",
}

failures: list[str] = []


def fail(fid: str, check: str, detail: str) -> None:
    """Every failure names the finding and the check, per the acceptance rule."""
    failures.append(f"{fid}: [{check}] {detail}")


# ---------------------------------------------------------------------------
# The data the findings are checked against. Read once; read-only.
# ---------------------------------------------------------------------------

def load_register() -> dict[str, set[str]]:
    """Register file slug -> the row ids it holds."""
    out: dict[str, set[str]] = {}
    for slug in FILE_MANIFEST_KEYS:
        path = DATA / f"{slug}.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        out[slug] = {r["id"] for r in rows}
    return out


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_exposure_manifest() -> dict:
    path = DATA / "exposure" / "_manifest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_exposure(sector: str) -> dict | None:
    # A child slug contains a slash; the exposure directory is flat and
    # flattens it to "__" — the same rule as web/lib/exposure.ts and
    # build_graph.exposure_filename, so all three resolve the same file.
    path = DATA / "exposure" / f"{sector.replace('/', '__')}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def file_statuses(files: list[str], manifest: dict) -> set[str]:
    out: set[str] = set()
    for f in files:
        if f in DECLARED_STATUS:
            out.update(DECLARED_STATUS[f])
        for key in FILE_MANIFEST_KEYS.get(f, ()):
            entry = manifest.get(key)
            if entry and entry.get("status"):
                out.add(entry["status"])
    return out


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_schema(fid: str, doc: dict, stem: str) -> bool:
    """Structural check. Returns False when the document is too broken to check
    further -- the later checks index into fields this one guarantees."""
    ok = True

    if doc.get("schema_version") != SCHEMA_VERSION:
        fail(fid, "schema", f"schema_version must be {SCHEMA_VERSION}, got {doc.get('schema_version')!r}")
        ok = False

    if doc.get("id") != stem:
        fail(fid, "schema", f"id {doc.get('id')!r} does not match filename {stem}.json")
        ok = False

    if not isinstance(doc.get("id"), str) or not doc.get("id"):
        fail(fid, "schema", "id missing")
        return False
    if doc["id"] != doc["id"].lower() or not all(c.isalnum() or c == "-" for c in doc["id"]):
        fail(fid, "schema", f"id {doc['id']!r} is not a lowercase hyphenated slug")
        ok = False
    # FND- is an ETS register row prefix. A finding id that collides with one
    # makes "FND-03" ambiguous in a URL and in conversation.
    if doc["id"].upper().startswith("FND-"):
        fail(fid, "schema", "id uses the FND- prefix, which collides with ETS register row ids")
        ok = False

    for field in ("template", "headline", "body", "basis_status", "date"):
        if not isinstance(doc.get(field), str) or not doc.get(field, "").strip():
            fail(fid, "schema", f"{field} missing or empty")
            ok = False

    for field in ("sectors", "files"):
        if not isinstance(doc.get(field), list) or not doc.get(field):
            fail(fid, "schema", f"{field} must be a non-empty list")
            ok = False

    if doc.get("template") not in TEMPLATES:
        fail(fid, "template", f"unknown template {doc.get('template')!r}; known: {list(TEMPLATES)}")
        ok = False

    headline = doc.get("headline") or ""
    if len(headline) > MAX_HEADLINE:
        fail(fid, "schema", f"headline is {len(headline)} chars, limit {MAX_HEADLINE}")
        ok = False

    if doc.get("basis_status") not in BASIS_STATUSES:
        fail(fid, "schema", f"basis_status must be one of {list(BASIS_STATUSES)}, got {doc.get('basis_status')!r}")
        ok = False

    try:
        date.fromisoformat(doc.get("date", ""))
    except (ValueError, TypeError):
        fail(fid, "schema", f"date {doc.get('date')!r} is not an ISO date")
        ok = False

    ev = doc.get("evidence")
    if not isinstance(ev, dict):
        fail(fid, "schema", "evidence missing")
        return False
    if not isinstance(ev.get("measures"), list) or not ev.get("measures"):
        # The load-bearing one. No measure evidence, no finding.
        fail(fid, "evidence", "evidence.measures is required and must be non-empty")
        ok = False
    if "exposure" in ev and not isinstance(ev["exposure"], list):
        fail(fid, "schema", "evidence.exposure must be a list when present")
        ok = False

    review = doc.get("review")
    if review is not None:
        if not isinstance(review, dict) or review.get("status") not in ("open", "resolved"):
            fail(fid, "schema", f"review.status must be open or resolved, got {review!r}")
            ok = False

    return ok


def check_measures(fid: str, doc: dict, register: dict[str, set[str]]) -> None:
    for i, m in enumerate(doc["evidence"].get("measures") or []):
        where = f"evidence.measures[{i}]"
        if not isinstance(m, dict) or not m.get("file") or not m.get("row_id"):
            fail(fid, "evidence", f"{where} needs both file and row_id")
            continue
        f, rid = m["file"], m["row_id"]
        if f not in register:
            fail(fid, "evidence", f"{where} names unknown register file {f!r}; known: {sorted(register)}")
            continue
        if rid not in register[f]:
            fail(fid, "evidence", f"{where} row {rid!r} is not in data/{f}.json")


def check_exposure(fid: str, doc: dict, exp_manifest: dict) -> None:
    """Resolve each exposure reference against data/exposure/<sector>.json.

    Two sectors can share one FIGARO code (steel/alu are both C24, cement/glass
    both C23), so the partner is resolved through the manifest's code and the
    check is on the code, not the label. The `note` field in the exposure file
    already tells a reader when a figure is shared; this gate does not need to
    re-litigate that, only to confirm the number is the stored one.
    """
    for i, e in enumerate(doc["evidence"].get("exposure") or []):
        where = f"evidence.exposure[{i}]"
        if not isinstance(e, dict):
            fail(fid, "exposure", f"{where} is not an object")
            continue

        sector, partner = e.get("sector"), e.get("partner_sector")
        relation, view = e.get("relation"), e.get("view")
        share = e.get("share_pct")

        if relation not in RELATIONS:
            fail(fid, "exposure", f"{where} relation must be one of {list(RELATIONS)}, got {relation!r}")
            continue
        if not isinstance(share, (int, float)):
            fail(fid, "exposure", f"{where} share_pct must be a number, got {share!r}")
            continue

        exposure = load_exposure(sector) if isinstance(sector, str) else None
        if exposure is None:
            fail(fid, "exposure", f"{where} sector {sector!r} has no data/exposure/<sector>.json")
            continue

        views = {"EU": exposure.get("eu"), **exposure.get("by_country", {})}
        if view not in views:
            fail(fid, "exposure", f"{where} view {view!r} not in this sector's exposure file "
                                  "(expected \"EU\" or an EU member ISO 3166-1 alpha-2 code)")
            continue
        v = views[view]

        # Suppliers and customers are industries, keyed by FIGARO code, so the
        # partner is a sector slug resolved through the manifest. Import
        # origins are countries, so the partner IS the code in the row.
        if relation == "import_origin":
            rows = v.get("foreign_input_origins") or []
            code = partner
        else:
            rows = v.get("suppliers" if relation == "supplier" else "customers") or []
            entry = exp_manifest.get(partner) if isinstance(partner, str) else None
            if not entry:
                fail(fid, "exposure", f"{where} partner_sector {partner!r} is not in the exposure manifest")
                continue
            code = entry["code"]

        row = next((r for r in rows if r.get("code") == code), None)
        if row is None:
            fail(fid, "exposure", f"{where} {partner!r} (code {code!r}) is not a {relation} of "
                                  f"{sector!r} in the {view} view")
            continue

        if abs(float(row["share"]) - float(share)) > 0.1:
            fail(fid, "exposure", f"{where} says {share}% but the data holds {row['share']}% "
                                  f"({partner} as {relation} of {sector}, {view} view)")


def check_vocabularies(fid: str, doc: dict, register: dict[str, set[str]]) -> None:
    for s in doc.get("sectors") or []:
        if s not in APP_SECTORS:
            fail(fid, "vocabulary", f"sector {s!r} is not an app sector slug; known: {sorted(APP_SECTORS)}")
    for f in doc.get("files") or []:
        if f not in register:
            fail(fid, "vocabulary", f"file {f!r} is not a register file; known: {sorted(register)}")

    # `files` is the finding's own statement of what it is about, and the
    # evidence is what it actually cites. If they disagree, one of them is
    # wrong, and the reader is shown the first while being protected by the
    # second.
    cited = {m.get("file") for m in (doc["evidence"].get("measures") or []) if isinstance(m, dict)}
    declared = set(doc.get("files") or [])
    if cited - declared:
        fail(fid, "vocabulary", f"evidence cites files not declared in `files`: {sorted(cited - declared)}")
    if declared - cited:
        fail(fid, "vocabulary", f"`files` declares files nothing in the evidence cites: {sorted(declared - cited)}")


def check_basis(fid: str, doc: dict, manifest: dict) -> None:
    files = [f for f in (doc.get("files") or []) if f in FILE_MANIFEST_KEYS]
    if not files:
        return  # already reported by the vocabulary check
    statuses = file_statuses(files, manifest)
    if not statuses:
        fail(fid, "basis", f"no status could be resolved for files {files}")
        return
    expected = STATUS_RULE.get(frozenset(statuses))
    if expected is None:
        fail(fid, "basis", f"files carry statuses {sorted(statuses)}, which no rule covers")
        return
    if doc.get("basis_status") != expected:
        fail(fid, "basis", f"claims basis_status {doc.get('basis_status')!r} but its files "
                           f"({', '.join(files)}) are {sorted(statuses)} -> {expected!r}")


# ---------------------------------------------------------------------------
# Diagrams. A finding may carry a `diagram` spec: nodes (acts and sectors) and
# edges whose labels are COMPUTED here from the register and the exposure
# files — the same gate-checked sources the graph is built from, with
# build_graph.py --check holding data/graph in sync. Nothing in a label is
# typed in: the spec names a quantity, this gate computes it, and a computed
# value that contradicts the finding fails the build. Written to
# data/findings/diagrams/<id>.json only after every check passes.
# ---------------------------------------------------------------------------

from benefit_axis import derive_valence

# Duty-side valences — the same set the support-gap finding's notes state:
# Requirement or Prohibition, plus benefit-side movements withdrawn.
DUTY_VALENCES = {"Requirement", "Prohibition", "Support cut", "Entitlement withdrawn"}

DIAGRAM_QUANTITY_KINDS = ("duty_count", "named_count", "reach_count", "exposure_share")


def load_register_rows() -> dict[str, list[dict]]:
    """Register file slug -> its full rows, for the diagram quantity checks."""
    out: dict[str, list[dict]] = {}
    for slug in FILE_MANIFEST_KEYS:
        path = DATA / f"{slug}.json"
        if path.exists():
            out[slug] = json.loads(path.read_text(encoding="utf-8"))
    return out


def _attributed(row: dict, sector: str) -> bool:
    return sector in (row.get("sectors_named") or []) or sector in (row.get("sectors_reached") or [])


def _fmt(value) -> str:
    """A count prints plain; a share prints as stored (21.6, not 21.60)."""
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def resolve_stored_share(sector: str, partner: str, relation: str, view: str, exp_manifest: dict):
    """The stored share for one exposure reference, or (None, reason)."""
    exposure = load_exposure(sector)
    if exposure is None:
        return None, f"sector {sector!r} has no exposure file"
    views = {"EU": exposure.get("eu"), **exposure.get("by_country", {})}
    if view not in views:
        return None, f"view {view!r} not in {sector!r}'s exposure file"
    v = views[view]
    if relation == "import_origin":
        rows, code = v.get("foreign_input_origins") or [], partner
    else:
        entry = exp_manifest.get(partner)
        if not entry:
            return None, f"partner_sector {partner!r} is not in the exposure manifest"
        rows = v.get("suppliers" if relation == "supplier" else "customers") or []
        code = entry["code"]
    row = next((r for r in rows if r.get("code") == code), None)
    if row is None:
        return None, f"{partner!r} (code {code!r}) is not a {relation} of {sector!r} in the {view} view"
    return float(row["share"]), None


def compute_diagram_quantity(fid: str, where: str, q: dict, doc: dict,
                             rows_by_file: dict[str, list[dict]], exp_manifest: dict):
    """Returns the computed value, or None after recording a failure."""
    kind = q.get("kind")
    if kind not in DIAGRAM_QUANTITY_KINDS:
        fail(fid, "diagram", f"{where} quantity kind must be one of {list(DIAGRAM_QUANTITY_KINDS)}, got {kind!r}")
        return None

    if kind in ("duty_count", "named_count", "reach_count"):
        file, sector = q.get("file"), q.get("sector")
        rows = rows_by_file.get(file)
        if rows is None:
            fail(fid, "diagram", f"{where} names unknown register file {file!r}")
            return None
        if sector not in APP_SECTORS:
            fail(fid, "diagram", f"{where} names unknown sector {sector!r}")
            return None
        if kind == "duty_count":
            return sum(
                1 for r in rows
                if _attributed(r, sector)
                and derive_valence(r.get("measure_type"), r.get("direction")) in DUTY_VALENCES
            )
        named = sum(1 for r in rows if sector in (r.get("sectors_named") or []))
        # named_count is the mirror of reach_count and exists for the same
        # reason: an act naming a sector in its own text and an act arriving at
        # it through a chain are different claims, and a diagram that blurs
        # them is the confusion these findings exist to remove. Named and
        # reached are disjoint by ruling (sources/scope.md), so the two counts
        # never double-count a row.
        if kind == "named_count":
            return named
        if q.get("require_named_zero") and named != 0:
            fail(fid, "diagram", f"{where} claims the act never names {sector!r}, but {named} row(s) name it")
            return None
        return sum(1 for r in rows if sector in (r.get("sectors_reached") or []))

    # exposure_share
    share, reason = resolve_stored_share(
        q.get("sector"), q.get("partner_sector"), q.get("relation"), q.get("view"), exp_manifest
    )
    if share is None:
        fail(fid, "diagram", f"{where} {reason}")
        return None
    # If the finding's evidence carries the same reference, the two must agree
    # — one figure, one source, stated once.
    for e in doc["evidence"].get("exposure") or []:
        if (e.get("sector"), e.get("partner_sector"), e.get("relation"), e.get("view")) == (
            q.get("sector"), q.get("partner_sector"), q.get("relation"), q.get("view")
        ):
            if abs(float(e.get("share_pct", 0)) - share) > 0.1:
                fail(fid, "diagram", f"{where} stored share {share} disagrees with evidence.exposure {e.get('share_pct')}")
                return None
    return share


def check_diagram(fid: str, doc: dict, rows_by_file: dict[str, list[dict]], exp_manifest: dict):
    """Validate one finding's diagram spec and return the resolved diagram
    (nodes with labels and hrefs, edges with computed labels), or None."""
    spec = doc.get("diagram")
    if spec is None:
        return None
    before = len(failures)

    nodes_out, node_ids = [], set()
    for i, n in enumerate(spec.get("nodes") or []):
        nid = n.get("id") or ""
        kind, _, slug = nid.partition(":")
        if kind == "act":
            if slug not in FILE_MANIFEST_KEYS:
                fail(fid, "diagram", f"nodes[{i}] {nid!r} is not a register file")
                continue
            label, href = n.get("label"), f"/acts/{slug}"
            if not label:
                fail(fid, "diagram", f"nodes[{i}] act node needs a display label")
                continue
        elif kind == "sector":
            if slug not in APP_SECTORS:
                fail(fid, "diagram", f"nodes[{i}] {nid!r} is not an app sector slug")
                continue
            # Default label is the canonical sector name; an override is
            # allowed for a stated reason (e.g. steel/alu sharing one
            # exposure code) but must contain the canonical name so it can
            # never point at a different industry.
            label, href = n.get("label") or APP_SECTORS[slug], f"/sectors/{slug}"
            if APP_SECTORS[slug].lower() not in label.lower():
                fail(fid, "diagram", f"nodes[{i}] label {label!r} does not contain {APP_SECTORS[slug]!r}")
                continue
        else:
            fail(fid, "diagram", f"nodes[{i}] id {nid!r} must be act:<file> or sector:<slug>")
            continue
        node_ids.add(nid)
        nodes_out.append({"id": nid, "kind": kind, "label": label, "href": href})

    if not (3 <= len(nodes_out) <= 5):
        fail(fid, "diagram", f"a diagram is a 3-5 node flow, got {len(nodes_out)}")

    edges_out = []
    for i, e in enumerate(spec.get("edges") or []):
        where = f"diagram.edges[{i}]"
        if e.get("from") not in node_ids or e.get("to") not in node_ids:
            fail(fid, "diagram", f"{where} references an undeclared node")
            continue
        template = e.get("label_template") or ""
        if "{n}" not in template:
            fail(fid, "diagram", f"{where} label_template must carry the {{n}} slot")
            continue
        value = compute_diagram_quantity(fid, where, e.get("quantity") or {}, doc, rows_by_file, exp_manifest)
        if value is None:
            continue
        rendered = _fmt(value)
        if (e.get("quantity") or {}).get("body_check") and rendered not in doc["body"]:
            fail(fid, "diagram", f"{where} computes {rendered}, which the finding body never states")
            continue
        edges_out.append({"from": e["from"], "to": e["to"], "label": template.replace("{n}", rendered)})

    # The renderer draws a vertical flow: every node after the first must
    # connect to exactly one earlier node, so any passing diagram is
    # guaranteed to lay out.
    for i, n in enumerate(nodes_out[1:], start=1):
        prior = {m["id"] for m in nodes_out[:i]}
        links = [e for e in edges_out if
                 (e["from"] == n["id"] and e["to"] in prior) or (e["to"] == n["id"] and e["from"] in prior)]
        if len(links) != 1:
            fail(fid, "diagram", f"node {n['id']} must connect to exactly one earlier node, has {len(links)}")

    if len(failures) > before:
        return None
    return {"id": doc["id"], "nodes": nodes_out, "edges": edges_out}


# ---------------------------------------------------------------------------

def build(write: bool = True) -> int:
    check_template_set()
    if not FINDINGS_DIR.exists():
        print(f"build_findings: no {FINDINGS_DIR.relative_to(DATA.parent)} directory; nothing to do")
        return 0

    register = load_register()
    manifest = load_manifest()
    exp_manifest = load_exposure_manifest()
    rows_by_file = load_register_rows()
    diagrams: list[dict] = []

    paths = sorted(p for p in FINDINGS_DIR.glob("*.json") if p.name != "index.json")
    docs: list[dict] = []
    seen: dict[str, str] = {}

    for path in paths:
        stem = path.stem
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(stem, "schema", f"not valid JSON: {exc}")
            continue
        if not isinstance(doc, dict):
            fail(stem, "schema", "top level is not an object")
            continue

        fid = doc.get("id") or stem
        if fid in seen:
            fail(fid, "schema", f"duplicate id, already defined by {seen[fid]}")
            continue
        seen[fid] = path.name

        if not check_schema(fid, doc, stem):
            continue
        check_measures(fid, doc, register)
        check_exposure(fid, doc, exp_manifest)
        check_vocabularies(fid, doc, register)
        check_basis(fid, doc, manifest)
        diagram = check_diagram(fid, doc, rows_by_file, exp_manifest)
        if diagram is not None:
            diagrams.append(diagram)
        docs.append(doc)

    if failures:
        print(f"FINDINGS NOT BUILT — {len(failures)} check(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    # Newest first, id as the tiebreak, so the file is stable across rebuilds
    # and the front end never has to sort.
    index = sorted(
        (
            {
                "id": d["id"],
                "template": d["template"],
                "headline": d["headline"],
                "sectors": d["sectors"],
                "files": d["files"],
                "basis_status": d["basis_status"],
                "date": d["date"],
            }
            for d in docs
        ),
        key=lambda r: (r["date"], r["id"]),
        reverse=True,
    )

    if write:
        INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Diagrams are outputs of this gate exactly like the index: written only
        # after every check passes, stale files removed so the directory always
        # mirrors the findings that carry a diagram.
        DIAGRAMS_DIR.mkdir(exist_ok=True)
        wanted = {d["id"] for d in diagrams}
        for stale in DIAGRAMS_DIR.glob("*.json"):
            if stale.stem not in wanted:
                stale.unlink()
        for d in diagrams:
            (DIAGRAMS_DIR / f"{d['id']}.json").write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    n_measures = sum(len(d["evidence"]["measures"]) for d in docs)
    n_exposure = sum(len(d["evidence"].get("exposure") or []) for d in docs)
    print(f"build_findings: {len(docs)} finding(s) pass — {n_measures} measure reference(s) and "
          f"{n_exposure} exposure reference(s) resolved against the register")
    print(f"build_findings: {len(diagrams)} diagram(s) computed"
          + ("" if not diagrams else " — " + ", ".join(sorted(d["id"] for d in diagrams))))
    if write:
        print(f"build_findings: wrote {INDEX_PATH.relative_to(DATA.parent)} and "
              f"{len(diagrams)} file(s) in {DIAGRAMS_DIR.relative_to(DATA.parent)}/")
    else:
        print("build_findings: --check, index not written")
    return 0


def main() -> int:
    return build(write="--check" not in sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())

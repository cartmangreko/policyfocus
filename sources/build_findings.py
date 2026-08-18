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
  6. TEMPLATE. One of the known templates; `editorial` is the escape hatch for
     a hand-written finding that fits none of them, and is still bound by 1-5.

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
MANIFEST_PATH = HERE / "manifest.json"

SCHEMA_VERSION = 1
MAX_HEADLINE = 140

TEMPLATES = (
    "reach",
    "indirect_exposure",
    "support_mismatch",
    "net_position",
    "country_concentration",
    "editorial",
)

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
    path = DATA / "exposure" / f"{sector}.json"
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

def build(write: bool = True) -> int:
    if not FINDINGS_DIR.exists():
        print(f"build_findings: no {FINDINGS_DIR.relative_to(DATA.parent)} directory; nothing to do")
        return 0

    register = load_register()
    manifest = load_manifest()
    exp_manifest = load_exposure_manifest()

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

    n_measures = sum(len(d["evidence"]["measures"]) for d in docs)
    n_exposure = sum(len(d["evidence"].get("exposure") or []) for d in docs)
    print(f"build_findings: {len(docs)} finding(s) pass — {n_measures} measure reference(s) and "
          f"{n_exposure} exposure reference(s) resolved against the register")
    if write:
        print(f"build_findings: wrote {INDEX_PATH.relative_to(DATA.parent)}")
    else:
        print("build_findings: --check, index not written")
    return 0


def main() -> int:
    return build(write="--check" not in sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())

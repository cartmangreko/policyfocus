"""
The gate for change records -- the event layer that sits beside the findings.

    python3 build_records.py            # validate every record, write the index
    python3 build_records.py --check    # validate only, write nothing

A change record is one permanent page per legislative event: what changed, in
which act, which sectors it names and which it reaches. It is a record of an
event rather than a comment on one, and it never goes stale, so everything it
says has to be recomputable from the register on any later build. Same contract
as the other gates here -- non-zero exit on any failure, deterministic output,
nothing written until every check passes.

WHAT THIS GATE IS FOR. A finding is a claim about many provisions at once; a
record is a claim about a MOMENT -- and a moment is the one thing the register
cannot re-derive later, because the register only ever holds the current state.
That asymmetry is the whole risk. So the rule is that a record may state a date
and an act, and everything else on it is recomputed from the register every
build. Five checks:

  1. SCHEMA AND ID. Required fields, types, id matches the filename, id is
     date-prefixed and its YYYY-MM agrees with event_date, no duplicates.
     The id is permanent (sources/scope.md, "Measure ids are permanent",
     which the record ids follow) -- restructuring buys a redirect, not a
     rename.
  2. REFERENCES RESOLVE. The register file exists; every measure reference
     names a row that is actually in it; every manifest key the file was read
     from is in manifest.json. A record pointing at a measure that is not
     there is a dead link on a permanent page.
  3. COUNTS ARE RECOMPUTED AND MATCHED EXACTLY. Every number the record
     carries is recomputed here from the register and compared. Not "within
     tolerance": these are counts, and a count is either right or wrong. (The
     0.1pp tolerance in build_findings.py is for exposure SHARES, which no
     record template prints today; a template that prints one has to route
     through that gate's resolver, not around it.)
  4. TEMPLATE. The record's family is one of the known families AND has a
     template in data/prose.json. Every {slot} in that template resolves to a
     value this gate computed; an unknown slot fails the build. An event that
     fits no family fails with a message saying a new reviewed template is
     needed -- the machine stops rather than composing, the same rule as the
     sectorless ego-note guard in build_ego_views.py.
  5. DIAGRAM. Every record carries a diagram, checked and computed by
     build_findings.check_diagram -- the same machinery, deliberately imported
     rather than copied, so a record diagram and a finding diagram cannot drift
     into two dialects. Its computed labels are then cross-checked against the
     record's own counts, so the picture and the prose can never disagree.

WHY THE INDEX IS AN OUTPUT AND CARRIES THE RENDERED PROSE. data/records/*.json
is what a person authors; data/records/index.json is what the front end reads,
and it is written here, after the checks, with the headline and body already
rendered. Two consequences, both wanted: a JSON file dropped into the directory
publishes nothing until it has been through this gate, and no rendering of a
reviewed template happens at request time (sources/scope.md, "No free-generated
text on the site" -- tier 2 renders unchanged or not at all).

NO PER-RECORD REVIEW FIELD. Records carried a `review` block for a while, on
the model of a finding's. It is gone by ruling: a record is generated when a
watch-agent PR is merged, and the merge IS the approval of both the data and
the record, so a second per-record status was a checkbox recording something
the git history already recorded. What still gates rendering is the TEMPLATE
status below -- the wording, reviewed once, not the individual record. A record
that turns out to be wrong is corrected in place, like any other page.

DRAFT TEMPLATES. data/prose.json's record_templates block carries a status. This
gate builds on 'draft-pending-george-review' and prints a loud warning, because
the three backfilled records exist precisely so George can read them rendered.
It stamps the status into every built record, and the page layer must refuse to
render any record whose prose_status is not 'approved'. A draft cannot reach a
reader by being forgotten about.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import build_findings as bf
from build_graph import SECTORS as APP_SECTORS

# PF_RECORDS_DIR and PF_PROSE_PATH exist for test_build_records.py, which has to run this
# gate against deliberately broken inputs without touching the real ones. Nothing else
# sets them; unset, the gate reads the repo.
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
RECORDS_DIR = Path(os.environ["PF_RECORDS_DIR"]) if os.environ.get("PF_RECORDS_DIR") else DATA / "records"
INDEX_PATH = RECORDS_DIR / "index.json"
DIAGRAMS_DIR = RECORDS_DIR / "diagrams"
PROSE_PATH = Path(os.environ["PF_PROSE_PATH"]) if os.environ.get("PF_PROSE_PATH") else DATA / "prose.json"
MANIFEST_PATH = HERE / "manifest.json"
GRAPH_NODES_PATH = DATA / "graph" / "nodes.json"
SECTORS_PATH = DATA / "sectors.json"
REGISTER_FILES_PATH = HERE / "register_files.json"
DATA_TS_PATH = HERE.parent / "web" / "lib" / "data.ts"

SCHEMA_VERSION = 1
MAX_HEADLINE = 140

# The four event shapes. A family is not a label -- it names which counts the
# gate recomputes and which template renders, so adding one is adding a
# reviewed template AND deciding what its numbers mean.
FAMILIES = (
    "new_act_ingested",   # a new act enters coverage
    "amendment",          # a tracked act is amended
    "delegated_act",      # a delegated or implementing act lands on a dependency
    "status_change",      # a tracked file moves proposed -> adopted
)

# Families whose subject is the whole file, so `measures` would restate the
# register: the measures involved are all of them, and the page links to the
# act. Every other family is about a SUBSET, and has to name it.
WHOLE_FILE_FAMILIES = ("new_act_ingested", "status_change")

BASIS_STATUSES = ("adopted", "proposed", "mixed")
RENDERABLE_PROSE_STATUS = "approved"
DRAFT_PROSE_STATUS = "draft-pending-george-review"

# The prior_rule statuses that count as RESOLVED — the wording of the earlier
# rule is on file and can be shown. Same set benefit_axis.assert_unchanged_prior
# admits (sources/scope.md, "`unchanged` needs a resolved prior_rule").
RESOLVED_PRIOR_STATUSES = ("sourced", "recital")

ID_RE = re.compile(r"^(\d{4})-(\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*$")
SLOT_RE = re.compile(r"\{([a-z0-9_]+)\}")

_REGISTER_FILES = json.loads(REGISTER_FILES_PATH.read_text(encoding="utf-8"))["files"]
DISPLAY_NAMES = {k: v["display_name"] for k, v in _REGISTER_FILES.items()}

failures: list[str] = []
warnings: list[str] = []


def fail(rid: str, check: str, detail: str) -> None:
    """Every failure names the record and the check, per the acceptance rule."""
    failures.append(f"{rid}: [{check}] {detail}")


# ---------------------------------------------------------------------------
# Inputs. Read once, read-only.
# ---------------------------------------------------------------------------

def load_prose() -> dict:
    block = json.loads(PROSE_PATH.read_text(encoding="utf-8")).get("record_templates")
    if not isinstance(block, dict):
        sys.exit("RECORDS NOT BUILT — data/prose.json has no record_templates block")
    return block


def load_register_rows() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for slug in _REGISTER_FILES:
        path = DATA / f"{slug}.json"
        if path.exists():
            out[slug] = json.loads(path.read_text(encoding="utf-8"))
    return out


def load_sector_labels() -> dict[str, str]:
    """Sector slug -> the name an audience sees.

    data/sectors.json carries TWO strings per sector and they are not the same
    string: `name` is the short internal one the gates and the graph are
    written against, and `label` is what the site prints -- "Retail" against
    "Retail and distribution", "Chemicals" against "Chemicals and refining",
    twelve of the twenty differing. Record prose is an audience surface, so it
    takes `label` (sources/scope.md, display vocabulary: the display layer says
    the sector's display name). Printing `name` would put one name in the
    sentence and a different one on the chip beside it, on the same page.
    """
    spine = json.loads(SECTORS_PATH.read_text(encoding="utf-8"))["sectors"]
    return {slug: meta.get("label") or meta["name"] for slug, meta in spine.items()}


def load_node_labels() -> dict[str, str]:
    """Act node id -> display label, from the graph. The graph is the one place
    the acts a register file points at already carry audience-facing names."""
    if not GRAPH_NODES_PATH.exists():
        return {}
    return {n["id"]: n.get("label") or "" for n in
            json.loads(GRAPH_NODES_PATH.read_text(encoding="utf-8")) if n.get("kind") == "act"}


def check_display_name_parity() -> None:
    """The act display name lives in register_files.json for the Python side and
    in web/lib/data.ts FILES for the TypeScript side. Two copies drift, and the
    drift would show as a record printing one name for an act the rest of the
    site calls something else -- on a permanent page. So every name this gate is
    willing to print must still be present in data.ts verbatim. A rename on one
    side only fails the build, which is the cheap version of the parity check
    check_valence_parity.py runs for the valence labels."""
    if not DATA_TS_PATH.exists():
        return  # the gate runs from sources/ in contexts with no web/ checkout
    ts = DATA_TS_PATH.read_text(encoding="utf-8")
    missing = sorted(n for n in DISPLAY_NAMES.values() if f'"{n}"' not in ts)
    if missing:
        print(
            "RECORDS NOT BUILT — act display name(s) in sources/register_files.json are not in "
            f"web/lib/data.ts FILES: {missing}. Rename on both sides or neither.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# The computed values. Everything a record is allowed to say, recomputed here.
# ---------------------------------------------------------------------------

def compute_facts(file: str, rows: list[dict], family: str, measures: list[dict]) -> dict:
    """The record's arithmetic, from the register as it stands right now.

    NAMED AND REACHED ARE DISJOINT PER MEASURE (sources/scope.md) but not per
    file: an act can name a sector on one measure and reach it on another. So
    the reached count is reached-minus-named -- the sectors this act arrives at
    ONLY through a chain. Counting them all would tell a reader that an act
    touches more sectors than it does.
    """
    subject = rows
    if family not in WHOLE_FILE_FAMILIES:
        wanted = {m["row_id"] for m in measures}
        subject = [r for r in rows if r.get("id") in wanted]

    prior_resolved = sum(
        1 for r in subject
        if isinstance(r.get("prior_rule"), dict)
        and r["prior_rule"].get("status") in RESOLVED_PRIOR_STATUSES
    )

    named_counts: dict[str, int] = {}
    named: set[str] = set()
    reached: set[str] = set()
    for r in subject:
        for s in r.get("sectors_named") or []:
            named.add(s)
            named_counts[s] = named_counts.get(s, 0) + 1
        for s in r.get("sectors_reached") or []:
            reached.add(s)
    reached_only = sorted(reached - named)

    # Deterministic: most-named wins, slug breaks the tie. A record must not
    # change which sector it leads on because a dict iterated differently.
    top = sorted(named_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "measure_count": len(subject),
        "prior_resolved_count": prior_resolved,
        "sectors_named": sorted(named),
        "sectors_reached": reached_only,
        "named_count": len(named),
        "reached_count": len(reached_only),
        "top_sector": top[0][0] if top else None,
        "top_sector_named_count": top[0][1] if top else 0,
    }


def reach_suppression(file: str, manifest: dict) -> tuple[bool, str]:
    """Whether this act's reach may be STATED, and why not when it may not.

    Reach is computed against the act as ingested. For an amending proposal
    that is the proposal text alone, so the sectors it is recorded as reaching
    include sectors of the BASE regime it amends rather than of the change it
    makes — the ETS revision comes out reaching aluminium, cement and power,
    which the ETS already reaches and the proposal does not extend it to.
    Publishing that on a permanent page repeats the error that withdrew the
    first ETS finding, so the clause is suppressed until reach is computed
    against the consolidated base as amended. sources/scope.md, "Reach is not
    stated on a record about an amending proposal".

    The condition is structural rather than a list of files, so the next
    amending proposal inherits it without anyone remembering the ruling.
    """
    keys = bf.FILE_MANIFEST_KEYS.get(file, ())
    for key in keys:
        entry = manifest.get(key) or {}
        if entry.get("status") == "proposed" and (entry.get("amends") or []):
            return True, (f"{file} is read from {key}, a proposal amending "
                          f"{', '.join(entry['amends'])}; its reach is computed against the "
                          "proposal rather than the act it amends")
    if not keys and "proposed" in bf.DECLARED_STATUS.get(file, ()):
        # No manifest entry, so what it amends cannot be read. Suppression is
        # the safe direction: the cost of omitting a true reach clause is a
        # thinner sentence, and the cost of printing a false one is permanent.
        return True, (f"{file} declares itself a proposal but has no manifest entry, so what it "
                      "amends cannot be checked")
    return False, ""


def prior_act(rid: str, doc: dict, manifest: dict, node_labels: dict) -> dict | None:
    """The act a record's measures change, and the verb for what they do to it.

    Both come from the manifest and the graph, never from the record: an act
    that REPEALS its predecessor replaces it, and one that AMENDS it amends it,
    and a template that hardcoded either would state the wrong relationship on
    the other. PPWR is the live case for the first (sources/scope.md,
    "Carry-overs come from repeal, not from amendment").
    """
    celex = doc.get("prior_act")
    if not celex:
        fail(rid, "references", f"template {doc.get('template')!r} states what an earlier rule "
                                "said, so the record must name the act it changes in `prior_act`")
        return None
    for key in bf.FILE_MANIFEST_KEYS.get(doc["file"], ()):
        entry = manifest.get(key) or {}
        if celex in (entry.get("repeals") or {}):
            record = entry["repeals"][celex]
            relationship = "replaces"
            # The date the repeal takes effect, quoted from the act itself.
            basis_date = record.get("since")
            basis_note = " ".join(x for x in (record.get("article"), record.get("quote")) if x)
            break
        if celex in (entry.get("amends") or []):
            relationship = "amends"
            # manifest.json records WHICH acts a file amends, not WHEN each
            # amendment takes effect. Until an ingestion records that date, an
            # amendment record against this act has no basis for its event
            # date and must fail rather than fall back.
            basis_date, basis_note = None, ""
            break
    else:
        fail(rid, "references", f"prior_act {celex!r} is not recorded in sources/manifest.json as "
                                f"an act {doc['file']} repeals or amends")
        return None
    label = node_labels.get(f"act:{celex}")
    if not label or label == celex:
        fail(rid, "references", f"prior_act {celex!r} has no display name in data/graph/nodes.json; "
                                "a record may not print a CELEX number at a reader")
        return None
    return {"celex": celex, "relationship": relationship, "name": label,
            "event_date": basis_date, "basis": basis_note}


def check_event_date_basis(rid: str, doc: dict, prior: dict) -> bool:
    """THE EVENT DATE IS THE DATE OF THE EVENT (sources/scope.md, "A record's
    event date is the date of the event it describes").

    A new_act_ingested record describes the platform reading an act, so its
    date is the reading. An amendment record describes something that happened
    in law, so its date has to come from the law -- and if the manifest does
    not record one, the record fails here rather than quietly inheriting the
    day the file was ingested. A permanent page dated to our reading rather
    than to the event is a small lie that never expires.
    """
    basis = prior.get("event_date")
    if not basis:
        fail(rid, "event_date", f"the manifest records no date for {doc['file']} "
                                f"{prior['relationship']} {prior['celex']}, so this record has no "
                                "basis for its event date. Record the date at ingestion; do not "
                                "fall back to the date the file was read.")
        return False
    if doc["event_date"] != basis:
        fail(rid, "event_date", f"event_date {doc['event_date']} is not the date of the event: the "
                                f"manifest has {doc['file']} {prior['relationship']} "
                                f"{prior['celex']} on {basis}"
                                + (f" ({prior['basis']})" if prior.get("basis") else ""))
        return False
    return True


def act_identifiers(file: str, manifest: dict) -> dict:
    """The proposal identifiers a status note may print, taken from the manifest
    rather than typed into the record."""
    out: dict[str, str] = {}
    for key in bf.FILE_MANIFEST_KEYS.get(file, ()):
        entry = manifest.get(key) or {}
        if entry.get("status") == "proposed":
            if entry.get("com"):
                out["com"] = entry["com"]
            if entry.get("procedure"):
                out["procedure"] = entry["procedure"]
            break
    return out


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_schema(rid: str, doc: dict, stem: str) -> bool:
    """Returns False when the document is too broken for the later checks,
    which index into fields this one guarantees."""
    ok = True

    if doc.get("schema_version") != SCHEMA_VERSION:
        fail(rid, "schema", f"schema_version must be {SCHEMA_VERSION}, got {doc.get('schema_version')!r}")
        ok = False

    rec_id = doc.get("id")
    if not isinstance(rec_id, str) or not rec_id:
        fail(rid, "schema", "id missing")
        return False
    if rec_id != stem:
        fail(rid, "schema", f"id {rec_id!r} does not match filename {stem}.json")
        ok = False

    m = ID_RE.match(rec_id)
    if not m:
        fail(rid, "id", f"id {rec_id!r} is not a date-prefixed slug of the form YYYY-MM-<slug> "
                        "(lowercase, hyphenated)")
        ok = False

    for field in ("template", "file", "act_label", "basis_status", "event_date"):
        if not isinstance(doc.get(field), str) or not doc.get(field, "").strip():
            fail(rid, "schema", f"{field} missing or empty")
            ok = False

    if doc.get("basis_status") not in BASIS_STATUSES:
        fail(rid, "schema", f"basis_status must be one of {list(BASIS_STATUSES)}, "
                            f"got {doc.get('basis_status')!r}")
        ok = False

    event_date = doc.get("event_date")
    try:
        parsed = date.fromisoformat(event_date)
    except (ValueError, TypeError):
        fail(rid, "schema", f"event_date {event_date!r} is not an ISO date")
        return ok and False
    # The id carries a date, so the id and the date have to be the same claim.
    if m and (int(m.group(1)), int(m.group(2))) != (parsed.year, parsed.month):
        fail(rid, "id", f"id {rec_id!r} is prefixed {m.group(1)}-{m.group(2)} but event_date is "
                        f"{event_date}")
        ok = False

    if not isinstance(doc.get("counts"), dict):
        fail(rid, "schema", "counts missing")
        ok = False

    for field in ("sectors_named", "sectors_reached"):
        if not isinstance(doc.get(field), list):
            fail(rid, "schema", f"{field} must be a list")
            ok = False

    if "measures" in doc and not isinstance(doc["measures"], list):
        fail(rid, "schema", "measures must be a list when present")
        ok = False

    if doc.get("diagram") is None:
        # Not optional here, unlike a finding: Part 3 of the brief gives every
        # record a shareable graphic, and a record with no diagram would be the
        # one page type that cannot be shared.
        fail(rid, "schema", "diagram missing; every record carries one")
        ok = False

    return ok


def check_references(rid: str, doc: dict, rows_by_file: dict[str, list[dict]], manifest: dict) -> bool:
    file = doc.get("file")
    if file not in rows_by_file:
        fail(rid, "references", f"file {file!r} is not a register file; known: {sorted(rows_by_file)}")
        return False

    if doc.get("act_label") != DISPLAY_NAMES.get(file):
        fail(rid, "references", f"act_label {doc.get('act_label')!r} is not this act's display name "
                                f"{DISPLAY_NAMES.get(file)!r} (sources/register_files.json)")

    keys = bf.FILE_MANIFEST_KEYS.get(file, ())
    unknown = [k for k in keys if k not in manifest]
    if unknown:
        fail(rid, "references", f"file {file!r} was read from manifest entr(ies) {unknown} that "
                                "sources/manifest.json does not hold")
    if not keys and file not in bf.DECLARED_STATUS:
        fail(rid, "references", f"file {file!r} has neither manifest keys nor a declared status")

    ids = {r.get("id") for r in rows_by_file[file]}
    measures = doc.get("measures") or []
    family = doc.get("template")
    if family in WHOLE_FILE_FAMILIES:
        if measures:
            fail(rid, "references", f"template {family!r} is about the whole act, so it must not "
                                    "list measures; the act page holds them all")
    elif not measures:
        fail(rid, "references", f"template {family!r} is about particular measures and must name "
                                "them in `measures`")

    for i, m in enumerate(measures):
        where = f"measures[{i}]"
        if not isinstance(m, dict) or not m.get("file") or not m.get("row_id"):
            fail(rid, "references", f"{where} needs both file and row_id")
            continue
        if m["file"] != file:
            fail(rid, "references", f"{where} names file {m['file']!r}, but the record is about "
                                    f"{file!r}")
            continue
        if m["row_id"] not in ids:
            fail(rid, "references", f"{where} measure {m['row_id']!r} is not in data/{file}.json")
    return True


def check_counts(rid: str, doc: dict, facts: dict) -> None:
    """Check 3. Exact, in both directions: a record may not overstate a count,
    and may not quietly understate one either -- an understated count reads as
    modesty and is the same defect."""
    counts = doc.get("counts") or {}
    expected = {
        "measures": facts["measure_count"],
        "sectors_named": facts["named_count"],
        "sectors_reached": facts["reached_count"],
        "top_sector_named": facts["top_sector_named_count"],
    }
    for key, want in expected.items():
        got = counts.get(key)
        if got != want:
            fail(rid, "counts", f"counts.{key} says {got!r}; the register computes {want}")
    for extra in sorted(set(counts) - set(expected)):
        fail(rid, "counts", f"counts.{extra} is not a count this gate computes; "
                            f"computable: {sorted(expected)}")

    if doc.get("top_sector") != facts["top_sector"]:
        fail(rid, "counts", f"top_sector {doc.get('top_sector')!r} is not the most-named sector "
                            f"{facts['top_sector']!r}")
    if list(doc.get("sectors_named") or []) != facts["sectors_named"]:
        fail(rid, "counts", f"sectors_named does not match the register: record says "
                            f"{doc.get('sectors_named')}, register says {facts['sectors_named']}")
    if list(doc.get("sectors_reached") or []) != facts["sectors_reached"]:
        fail(rid, "counts", f"sectors_reached does not match the register: record says "
                            f"{doc.get('sectors_reached')}, register says {facts['sectors_reached']}")

    for s in (doc.get("sectors_named") or []) + (doc.get("sectors_reached") or []):
        if s not in APP_SECTORS:
            fail(rid, "vocabulary", f"sector {s!r} is not an app sector slug")


def check_basis(rid: str, doc: dict, manifest: dict) -> None:
    """The same STATUS_RULE the findings gate applies, for the same reason: a
    record about a proposal that reads as settled law is the one error a reader
    has no way to catch."""
    file = doc.get("file")
    statuses = bf.file_statuses([file], manifest)
    if not statuses:
        fail(rid, "basis", f"no status could be resolved for file {file!r}")
        return
    expected = bf.STATUS_RULE.get(frozenset(statuses))
    if expected is None:
        fail(rid, "basis", f"file carries statuses {sorted(statuses)}, which no rule covers")
        return
    if doc.get("basis_status") != expected:
        fail(rid, "basis", f"claims basis_status {doc.get('basis_status')!r} but {file} is "
                           f"{sorted(statuses)} -> {expected!r}")


def render(rid: str, where: str, template: str, ctx: dict) -> str | None:
    """Check 4's teeth. A slot the gate did not compute fails the build; it is
    never filled with an empty string, because a sentence with a hole in it is
    how a wrong number gets published quietly."""
    unknown = sorted({m.group(1) for m in SLOT_RE.finditer(template)} - set(ctx))
    if unknown:
        fail(rid, "template", f"{where} uses slot(s) {unknown} this gate does not compute; "
                              f"computable slots: {sorted(ctx)}")
        return None
    return SLOT_RE.sub(lambda m: str(ctx[m.group(1)]), template)


def check_template(rid: str, doc: dict, facts: dict, prose: dict, manifest: dict,
                   node_labels: dict, sector_labels: dict) -> dict | None:
    """Returns {"headline", "body", "reach"} rendered, or None."""
    family = doc.get("template")
    if family not in FAMILIES:
        fail(rid, "template", f"event shape {family!r} fits no template family. Known families: "
                              f"{list(FAMILIES)}. A new shape needs a new REVIEWED template in "
                              "data/prose.json before a record can use it — this gate will not "
                              "compose one.")
        return None

    fam = (prose.get("families") or {}).get(family)
    if not isinstance(fam, dict) or not fam.get("headline") or not fam.get("body"):
        fail(rid, "template", f"family {family!r} has no headline+body template in "
                              "data/prose.json record_templates.families")
        return None

    if facts["top_sector"] is None:
        fail(rid, "template", "this act names no sector at all, and every family template leads on "
                              "the sector it names most. A sectorless act needs its own reviewed "
                              "template — the same guard build_ego_views.py applies to a sectorless "
                              "act's note.")
        return None
    suppressed, reason = reach_suppression(doc["file"], manifest)

    if not suppressed and facts["reached_count"] == 0:
        fail(rid, "template", "this act reaches no sector beyond the ones it names, and the "
                              "reach-stating template states a reach count. That shape needs its "
                              "own reviewed template rather than a sentence saying 'and 0 more'.")
        return None

    ctx = {
        "act_name": doc["act_label"],
        "measure_count": facts["measure_count"],
        "named_count": facts["named_count"],
        "top_sector": sector_labels[facts["top_sector"]],
        "top_sector_named_count": facts["top_sector_named_count"],
    }
    # THE SUPPRESSION, AND WHY IT IS A MISSING SLOT RATHER THAN AN IF. Dropping
    # reached_count from the computable slots means a template that mentions
    # reach fails the build as an unknown slot. A conditional in the renderer
    # would silently pick the safe variant and leave the unsafe one one edit
    # away from rendering; this way the failure is the default.
    if not suppressed:
        ctx["reached_count"] = facts["reached_count"]

    if family == "amendment":
        prior = prior_act(rid, doc, manifest, node_labels)
        if prior is None:
            return None
        if not check_event_date_basis(rid, doc, prior):
            return None
        if facts["prior_resolved_count"] == 0:
            fail(rid, "template", "no measure on this record has the earlier wording on file, so "
                                  "there is no before to show against the after. A change with an "
                                  "unresolved before renders single-state, which needs its own "
                                  "reviewed template — the register's own rule (sources/scope.md, "
                                  "\"`unchanged` needs a resolved prior_rule\").")
            return None
        ctx["prior_act_name"] = prior["name"]
        ctx["relationship"] = prior["relationship"]
        ctx["prior_resolved_count"] = facts["prior_resolved_count"]

    body_key = "body_no_reach" if suppressed else "body"
    if not fam.get(body_key):
        fail(rid, "template", f"family {family!r} has no {body_key!r} template in data/prose.json, "
                              + ("and this act's reach may not be stated: " + reason if suppressed
                                 else "which every family must carry"))
        return None

    headline = render(rid, "headline", fam["headline"], ctx)
    body = render(rid, "body", fam[body_key], ctx)

    note_template = (prose.get("status_notes") or {}).get(doc["basis_status"])
    if not note_template:
        fail(rid, "template", f"no status note for basis_status {doc['basis_status']!r} in "
                              "data/prose.json record_templates.status_notes")
        return None
    note = render(rid, "status_note", note_template, act_identifiers(doc["file"], manifest))

    if headline is None or body is None or note is None:
        return None
    if len(headline) > MAX_HEADLINE:
        fail(rid, "template", f"rendered headline is {len(headline)} chars, limit {MAX_HEADLINE}")
        return None
    return {
        "headline": headline,
        "body": f"{body} {note}",
        "reach": {"suppressed": suppressed, "reason": reason} if suppressed else {"suppressed": False},
    }


def check_diagram(rid: str, doc: dict, prose_text: dict, rows_by_file: dict, exp_manifest: dict,
                  facts: dict) -> dict | None:
    """Check 5. The diagram spec is validated and its labels computed by the
    findings gate's machinery, against a document shaped the way that gate
    expects. Importing it is the point: a record diagram IS a finding diagram
    with a record's counts, and two copies of the label arithmetic would be two
    places for a number to be wrong."""
    # A record about particular measures counts over those measures. The ids
    # come from the record's own `measures` list rather than being repeated in
    # the diagram spec: one list, checked once, so the picture cannot be scoped
    # to a different set than the prose.
    spec = json.loads(json.dumps(doc["diagram"]))
    row_ids = [m["row_id"] for m in (doc.get("measures") or [])]
    for edge in spec.get("edges") or []:
        quantity = edge.get("quantity") or {}
        if quantity.pop("scope", None) == "record_measures":
            if not row_ids:
                fail(rid, "diagram", "an edge is scoped to this record's measures, but the record "
                                     "lists none")
                return None
            quantity["row_ids"] = row_ids

    shim = {
        "id": doc["id"],
        "body": prose_text["body"],
        "diagram": spec,
        "evidence": {"exposure": []},
    }
    before = len(bf.failures)
    diagram = bf.check_diagram(rid, shim, rows_by_file, exp_manifest)
    for f in bf.failures[before:]:
        failures.append(f)
    if diagram is None:
        return None

    # The picture and the prose state the same numbers, or neither ships. The
    # body_check flag in the spec already asserts a labelled value appears in
    # the body; this asserts the leading edge is the count the record carries,
    # so a diagram cannot lead on a sector the prose never mentions.
    top_label_expected = str(facts["top_sector_named_count"])
    lead = [e for e in diagram["edges"] if e["to"] == f"sector:{facts['top_sector']}"]
    if not lead:
        fail(rid, "diagram", f"the diagram has no edge to sector:{facts['top_sector']}, the sector "
                             "the record's prose leads on")
        return None
    if top_label_expected not in lead[0]["label"]:
        fail(rid, "diagram", f"the edge to sector:{facts['top_sector']} is labelled "
                             f"{lead[0]['label']!r}, which does not carry the record's count "
                             f"{top_label_expected}")
        return None
    return diagram


# ---------------------------------------------------------------------------

def build(write: bool = True) -> int:
    check_display_name_parity()
    if not RECORDS_DIR.exists():
        print(f"build_records: no {RECORDS_DIR} directory; nothing to do")
        return 0

    prose = load_prose()
    prose_status = prose.get("status")
    if prose_status not in (RENDERABLE_PROSE_STATUS, DRAFT_PROSE_STATUS):
        print(f"RECORDS NOT BUILT — record_templates status is {prose_status!r}; must be "
              f"{RENDERABLE_PROSE_STATUS!r} or {DRAFT_PROSE_STATUS!r}", file=sys.stderr)
        return 1
    if prose_status == DRAFT_PROSE_STATUS:
        warnings.append(
            "record templates are DRAFT (data/prose.json record_templates.status = "
            f"{DRAFT_PROSE_STATUS!r}). Records build so they can be read rendered; the page layer "
            "must not render a record whose prose_status is not 'approved'."
        )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rows_by_file = load_register_rows()
    exp_manifest = bf.load_exposure_manifest()
    node_labels = load_node_labels()
    sector_labels = load_sector_labels()

    paths = sorted(p for p in RECORDS_DIR.glob("*.json") if p.name != "index.json")
    built: list[dict] = []
    diagrams: list[dict] = []
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

        rid = doc.get("id") or stem
        if rid in seen:
            fail(rid, "schema", f"duplicate id, already defined by {seen[rid]}")
            continue
        seen[rid] = path.name

        if not check_schema(rid, doc, stem):
            continue
        if not check_references(rid, doc, rows_by_file, manifest):
            continue
        check_basis(rid, doc, manifest)

        facts = compute_facts(doc["file"], rows_by_file[doc["file"]], doc["template"],
                              doc.get("measures") or [])
        check_counts(rid, doc, facts)
        text = check_template(rid, doc, facts, prose, manifest, node_labels, sector_labels)
        if text is None:
            continue
        diagram = check_diagram(rid, doc, text, rows_by_file, exp_manifest, facts)
        if diagram is not None:
            diagrams.append(diagram)

        # A SUPPRESSED RECORD SHIPS WITHOUT ITS REACH FIELDS. The authored file
        # keeps them, and they are still checked against the register above --
        # they are true, they are just not sayable yet. What the front end gets
        # is the sentence and the data it is allowed to draw: leaving the
        # sectors in the index would put a reach strip one component away from
        # rendering exactly what the prose is forbidden to state.
        counts = dict(doc["counts"])
        entry = {
            "id": doc["id"],
            "template": doc["template"],
            "event_date": doc["event_date"],
            "file": doc["file"],
            "act_label": doc["act_label"],
            "basis_status": doc["basis_status"],
            "headline": text["headline"],
            "body": text["body"],
            "prose_status": prose_status,
            "top_sector": doc["top_sector"],
            "sectors_named": doc["sectors_named"],
            "measures": doc.get("measures") or [],
            "reach": text["reach"],
        }
        if text["reach"]["suppressed"]:
            counts.pop("sectors_reached", None)
        else:
            entry["sectors_reached"] = doc["sectors_reached"]
        if doc.get("prior_act"):
            entry["prior_act"] = doc["prior_act"]
        entry["counts"] = counts
        built.append(entry)

    if failures:
        print(f"RECORDS NOT BUILT — {len(failures)} check(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    # Newest first, id as the tiebreak, so a rebuild that changes no record
    # produces no diff.
    index = sorted(built, key=lambda r: (r["event_date"], r["id"]), reverse=True)

    if write:
        INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        DIAGRAMS_DIR.mkdir(exist_ok=True)
        wanted = {d["id"] for d in diagrams}
        for stale in DIAGRAMS_DIR.glob("*.json"):
            if stale.stem not in wanted:
                stale.unlink()
        for d in diagrams:
            (DIAGRAMS_DIR / f"{d['id']}.json").write_text(
                json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for w in warnings:
        print(f"build_records: WARNING — {w}")
    suppressed = sorted(r["id"] for r in built if r["reach"]["suppressed"])
    if suppressed:
        print(f"build_records: reach clause suppressed on {len(suppressed)} record(s) — "
              + ", ".join(suppressed) + " (amending proposals; see sources/scope.md)")
    families = sorted({r["template"] for r in built})
    print(f"build_records: {len(built)} record(s) pass — families {families}, "
          f"{len(diagrams)} diagram(s) computed")
    if write:
        print(f"build_records: wrote {INDEX_PATH} and {len(diagrams)} file(s) in {DIAGRAMS_DIR}/")
    else:
        print("build_records: --check, index not written")
    return 0


def main() -> int:
    return build(write="--check" not in sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())

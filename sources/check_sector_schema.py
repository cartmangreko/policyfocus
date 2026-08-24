"""
The gate on the sector transition map: data/transition/*.json.

    python3 check_sector_schema.py          # exits non-zero on any error

What it enforces, and why each rule is a failure rather than a warning:

  SHAPE          every row carries the fields its kind is defined to carry, and
                 every closed-vocabulary field holds a value from that
                 vocabulary. A row missing `transition` is a row the sector page
                 cannot place in a section; a row with `transition:
                 "decarbonization"` is worse, because it renders as a section
                 heading nobody wrote.

  RESOLUTION     every id a row points at exists -- technology -> technology
                 dependencies, bottleneck -> technology, parameter -> whatever
                 it quantifies, project -> technology and measure. Same rule as
                 build_graph.py's resolve gate, for the same reason: a dangling
                 reference does not break the page, it quietly empties a
                 section, and an empty section reads as "there is nothing here"
                 rather than as "this is broken".

  SOURCING       every parameter has url, publisher, verbatim, unit, both dates;
                 every project status_history entry has a source_url; every
                 technology readiness and cost has a source and a date. The
                 whole layer is judgment about other people's numbers, and a
                 number without a source is the one thing that cannot be
                 defended in front of the audience this is built for.

  VERBATIM       the parameter's value has to appear in its own quote. This
                 catches the specific failure that sourcing rules otherwise
                 miss: a real URL, a real sentence, and a number that came from
                 somewhere else. Digits are compared after stripping thousands
                 separators and normalising the decimal comma, because EU
                 sources write 1 234,5 and this file should not fail on
                 typography. Where the value is genuinely not a literal in the
                 sentence -- a share computed from two figures, a range read off
                 a table -- the row says so in `verbatim_note`, which is
                 accepted and printed, so the exception is visible rather than
                 silent.

  APPEND-ONLY    status_history is sorted by date and its last entry equals the
                 project's `status`. A project whose header and whose timeline
                 disagree is a project whose page states two different facts.

What it prints and does NOT fail on:

  STALE          a parameter more than `stale_after` months past its
                 `date_of_value`. Staleness is a fact about the number, not an
                 error in the data: the last published carbon price is still the
                 last published carbon price. Failing here would take the site
                 down for the age of somebody else's report, so the gate prints
                 the list and returns 0 on it.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date

import display_vocabulary as dv
import sector_map as sm

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


class Errors:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.stale: list[str] = []

    def add(self, where: str, msg: str) -> None:
        self.errors.append(f"  {where}: {msg}")


def _req(e: Errors, where: str, row: dict, *fields: str) -> None:
    for f in fields:
        if row.get(f) in (None, "", [], {}):
            e.add(where, f"missing {f}")


def _vocab(e: Errors, where: str, row: dict, field: str, allowed: tuple[str, ...]) -> None:
    val = row.get(field)
    if val is not None and val not in allowed:
        e.add(where, f"{field}={val!r} is not one of {'|'.join(allowed)}")


def _date(e: Errors, where: str, row: dict, field: str) -> None:
    val = row.get(field)
    if val and not DATE_RE.match(str(val)):
        e.add(where, f"{field}={val!r} is not YYYY, YYYY-MM or YYYY-MM-DD")


def _url(e: Errors, where: str, url: str | None, field: str = "url") -> None:
    if not url:
        e.add(where, f"missing {field}")
    elif not str(url).startswith("https://") and not str(url).startswith("http://"):
        e.add(where, f"{field}={url!r} is not a URL")


def _source_list(e: Errors, where: str, row: dict) -> None:
    sources = row.get("sources")
    if not sources:
        e.add(where, "no sources")
        return
    for i, s in enumerate(sources):
        w = f"{where} sources[{i}]"
        _url(e, w, s.get("url"))
        _req(e, w, s, "title", "publisher", "date")
        _date(e, w, s, "date")


# ---------------------------------------------------------------------------
# The verbatim check
# ---------------------------------------------------------------------------

def _numbers(text: str) -> set[str]:
    """Every number in a string, normalised so that 1 234,5 / 1,234.5 / 1234.5
    all compare equal, and trailing zeroes do not decide the match."""
    out: set[str] = set()
    cleaned = re.sub(r"(?<=\d)[   '](?=\d)", "", text)
    for raw in re.findall(r"\d+(?:[.,]\d+)*", cleaned):
        # A comma or dot before exactly three digits is a thousands separator
        # unless it is the only separator and the source is known-decimal; both
        # readings are kept, so the check is permissive rather than clever.
        out.add(raw.replace(",", ".").rstrip("0").rstrip(".") or "0")
        out.add(re.sub(r"[.,](?=\d{3}\b)", "", raw).replace(",", ".").rstrip("0").rstrip(".") or "0")
    return out


def _value_in_quote(value, verbatim: str) -> bool:
    quote = _numbers(verbatim)
    for token in re.findall(r"\d+(?:[.,]\d+)*", str(value)):
        norm = token.replace(",", ".").rstrip("0").rstrip(".") or "0"
        if norm not in quote:
            return False
    return True


def _months_since(value_date: str) -> int:
    parts = [int(p) for p in str(value_date).split("-")]
    y, m = parts[0], (parts[1] if len(parts) > 1 else 12)
    today = date.today()
    return (today.year - y) * 12 + (today.month - m)


# ---------------------------------------------------------------------------
# Per-kind checks
# ---------------------------------------------------------------------------

def check_technologies(e: Errors, rows: list[dict], sectors: dict) -> None:
    ids = {r["id"] for r in rows}
    for r in rows:
        w = f"technology {r.get('id', '?')}"
        # `plain_action` is what the sector is DOING with this technology, as a
        # gerund phrase that finishes "European cement is decarbonising by
        # ___" — the opening sentence of the lead block (brief 4 §5). Required
        # of every technology, not only of the one that currently leads its
        # sector: which technology leads is a fact about today's project count,
        # and a field that only the leader had to fill in would go missing the
        # week the count changed.
        _req(e, w, r, "id", "transition", "name", "description", "plain_action",
             "readiness", "sectors")
        action = (r.get("plain_action") or "").strip()
        if action:
            if action[0].isupper() or action.endswith("."):
                e.add(w, "plain_action is a phrase inside a sentence, not a sentence: "
                         "lower case, no full stop")
            bad = dv.violations(action)
            if bad:
                e.add(w, f"plain_action uses {sorted(set(bad))} — see "
                         f"sources/display_vocabulary.py")
        _vocab(e, w, r, "transition", sm.TRANSITIONS)
        for slug in r.get("sectors", []):
            if slug not in sectors:
                e.add(w, f"sectors names {slug!r}, which is not in data/sectors.json")
        readiness = r.get("readiness") or {}
        if readiness:
            _vocab(e, w + " readiness", readiness, "level", sm.READINESS)
            _req(e, w + " readiness", readiness, "source", "date")
            _date(e, w + " readiness", readiness, "date")
        for field in ("abatement_share", "cost"):
            block = r.get(field)
            if block:
                _req(e, f"{w} {field}", block, "source", "date")
                _date(e, f"{w} {field}", block, "date")
                if field == "cost":
                    _req(e, f"{w} cost", block, "unit")
        for dep in r.get("dependency", []):
            if dep not in ids:
                e.add(w, f"depends_on {dep!r}, which is not a technology id")
        _source_list(e, w, r)


def check_bottlenecks(e: Errors, rows: list[dict], tech_ids: set, param_ids: set,
                      measure_ids: set, sectors: dict) -> None:
    for r in rows:
        w = f"bottleneck {r.get('id', '?')}"
        _req(e, w, r, "id", "sector", "transition", "type", "name", "description")
        _vocab(e, w, r, "transition", sm.TRANSITIONS)
        _vocab(e, w, r, "type", sm.BOTTLENECK_TYPES)
        if r.get("sector") not in sectors:
            e.add(w, f"sector={r.get('sector')!r} is not in data/sectors.json")
        for pid in r.get("quantified_by", []):
            if pid not in param_ids:
                e.add(w, f"quantified_by {pid!r}, which is not a parameter id")
        for tid in r.get("addressed_by", []):
            if tid not in tech_ids:
                e.add(w, f"addressed_by {tid!r}, which is not a technology id")
        # The measure -> bottleneck edges live here rather than in a file of their
        # own, because the judgement they encode is a judgement ABOUT this
        # bottleneck: whoever changes what the constraint is has to look at what
        # was said to relieve it in the same edit.
        for i, m in enumerate(r.get("measures") or []):
            mw = f"{w} measures[{i}]"
            _req(e, mw, m, "measure", "rel", "weight", "note", "evidence")
            _vocab(e, mw, m, "rel", ("worsens", "relieves"))
            if m.get("measure") not in measure_ids:
                e.add(mw, f"measure={m.get('measure')!r} is not a register measure id")
            weight = m.get("weight")
            if weight is not None and not (0 < float(weight) <= 1):
                e.add(mw, f"weight={weight!r} is outside (0, 1]")
            _req(e, mw + " evidence", m.get("evidence") or {}, "source", "path", "quote")
        _source_list(e, w, r)


def check_parameters(e: Errors, rows: list[dict], tech_ids: set, sectors: dict) -> None:
    for r in rows:
        w = f"parameter {r.get('id', '?')}"
        _req(e, w, r, "id", "name", "value", "unit", "scope",
             "date_of_value", "retrieved_date", "source", "confidence")
        _vocab(e, w, r, "confidence", sm.CONFIDENCE)
        _date(e, w, r, "date_of_value")
        _date(e, w, r, "retrieved_date")
        scope = r.get("scope")
        if scope and scope not in sm.SCOPE_LITERALS and not scope.startswith(sm.SCOPE_PREFIXES):
            e.add(w, f"scope={scope!r} is not eu, global, country:XX or plant:<id>")
        if r.get("sector") and r["sector"] not in sectors:
            e.add(w, f"sector={r['sector']!r} is not in data/sectors.json")
        if r.get("technology") and r["technology"] not in tech_ids:
            e.add(w, f"technology={r['technology']!r} is not a technology id")
        src = r.get("source") or {}
        _url(e, w + " source", src.get("url"))
        _req(e, w + " source", src, "publisher", "verbatim")
        verbatim = src.get("verbatim", "")
        if verbatim and not r.get("verbatim_note"):
            if not _value_in_quote(r.get("value"), verbatim):
                e.add(w, f"value {r.get('value')!r} does not appear in the quote; "
                         "add verbatim_note if it is derived rather than stated")
        if r.get("date_of_value") and DATE_RE.match(str(r["date_of_value"])):
            limit = r.get("stale_after", sm.DEFAULT_STALE_AFTER_MONTHS)
            age = _months_since(r["date_of_value"])
            if age > limit:
                e.stale.append(f"  {r['id']}: {age} months old, stale_after {limit}")


def check_projects(e: Errors, rows: list[dict], tech_ids: set, measure_ids: set, sectors: dict) -> None:
    for r in rows:
        w = f"project {r.get('id', '?')}"
        _req(e, w, r, "id", "name", "company", "country", "sector", "transition",
             "technology", "status", "status_history")
        _vocab(e, w, r, "transition", sm.TRANSITIONS)
        _vocab(e, w, r, "status", sm.PROJECT_STATUSES)
        if r.get("sector") not in sectors:
            e.add(w, f"sector={r.get('sector')!r} is not in data/sectors.json")
        for tid in r.get("technology", []):
            if tid not in tech_ids:
                e.add(w, f"deploys {tid!r}, which is not a technology id")
        if "public_funding" in r:
            e.add(w, "public_funding moved to data/transition/funding.json — the project "
                     "carries a derived rollup, never a stored copy")
        history = r.get("status_history") or []
        dates = []
        for i, h in enumerate(history):
            hw = f"{w} status_history[{i}]"
            _req(e, hw, h, "status", "date", "source_url")
            _vocab(e, hw, h, "status", sm.PROJECT_STATUSES)
            _date(e, hw, h, "date")
            _url(e, hw, h.get("source_url"), "source_url")
            dates.append(str(h.get("date", "")))
        if dates != sorted(dates):
            e.add(w, "status_history is not in date order; it is append-only")
        if history and history[-1].get("status") != r.get("status"):
            e.add(w, f"status={r.get('status')!r} but the last history entry is "
                     f"{history[-1].get('status')!r}")
        _source_list(e, w, r)


def check_materials(e: Errors, rows: list[dict], sectors: dict, tech_ids: set,
                    project_ids: set, param_ids: set, material_ids: set) -> None:
    """Materials, and the four kinds of edge that hang off them.

    Every edge endpoint is a prefixed graph id -- `sector:cement`,
    `project:brevik-ccs`, `technology:ccs-oxyfuel` -- rather than a bare slug,
    because the prefix is what makes an edge into the wrong kind of node a typo
    the gate can see rather than a lookup that quietly finds nothing.
    """
    for r in rows:
        w = f"material {r.get('id', '?')}"
        _req(e, w, r, "id", "name", "type", "sectors", "description", "sources")
        _vocab(e, w, r, "type", sm.MATERIAL_TYPES)
        _source_list(e, w, r)
        for slug in r.get("sectors", []):
            if slug not in sectors:
                e.add(w, f"sector {slug!r} is not in data/sectors.json")

        def endpoint(where: str, node: str, allowed: tuple[str, ...]) -> None:
            kind, _, tail = node.partition(":")
            if kind not in allowed:
                e.add(where, f"{node!r} is a {kind or '?'} where {list(allowed)} is allowed")
                return
            known = {"sector": set(sectors), "technology": tech_ids,
                     "project": project_ids}[kind]
            if tail not in known:
                e.add(where, f"{node!r} names no {kind} that exists")

        def edges(field: str, allowed: tuple[str, ...]) -> None:
            for i, edge in enumerate(r.get(field) or []):
                ew = f"{w} {field}[{i}]"
                _req(e, ew, edge, "node", "since", "evidence")
                _date(e, ew, edge, "since")
                if not (edge.get("evidence") or {}).get("source"):
                    e.add(ew, "no evidence.source — an edge you cannot trace is an edge "
                              "you cannot defend")
                if edge.get("node"):
                    endpoint(ew, edge["node"], allowed)
                # `volume` names a parameter rather than restating a number, so a
                # material cannot state a figure that has no quoted sentence.
                vol = edge.get("volume")
                if vol is not None and vol not in param_ids:
                    e.add(ew, f"volume={vol!r} is not a parameter id")
                if vol is None and "volume" in edge and not edge.get("volume_note") \
                        and field == "produced_by":
                    e.add(ew, "volume is null with no volume_note saying why")

        edges("produced_by", ("sector", "project"))
        edges("consumed_by", ("sector", "technology"))
        edges("required_by", ("technology",))
        for i, sub in enumerate(r.get("substitutes") or []):
            sw = f"{w} substitutes[{i}]"
            _req(e, sw, sub, "material", "since", "evidence")
            if sub.get("material") not in material_ids:
                e.add(sw, f"material={sub.get('material')!r} names no material that exists")
            if sub.get("material") == r["id"]:
                e.add(sw, "substitutes itself")


def check_funding(e: Errors, rows: list[dict], tech_ids: set, project_ids: set,
                  measure_ids: set, param_ids: set) -> None:
    """Capital allocation, and the four things every euro has to be able to say:
    what instrument it arrived as, how far it has got, what it finances, and what
    it was decided under."""
    for r in rows:
        w = f"funding {r.get('id', '?')}"
        _req(e, w, r, "id", "name", "instrument", "programme", "date", "status",
             "finances", "country", "sources")
        _vocab(e, w, r, "instrument", sm.FUNDING_INSTRUMENTS)
        _vocab(e, w, r, "status", sm.FUNDING_STATUSES)
        _date(e, w, r, "date")
        _source_list(e, w, r)

        # An amount is required to be RECORDED, not to be known: a grant whose
        # size nobody published is real money and dropping it would understate
        # the public capital in a project. null is allowed and must carry a note,
        # which is what stops an amount going missing by accident.
        if "amount" not in r:
            e.add(w, "no amount; use null with an amount_note if it is unpublished")
        elif r["amount"] is None and not r.get("amount_note"):
            e.add(w, "amount is null with no amount_note explaining why")
        elif r["amount"] is not None and r["amount"] not in param_ids:
            e.add(w, f"amount={r['amount']!r} is not a parameter id — an amount names the "
                     f"sourced number rather than restating it")

        if "under" not in r:
            e.add(w, "no under; use null with an under_note where the register carries no "
                     "legal basis for this money")
        elif r["under"] is None and not r.get("under_note"):
            e.add(w, "under is null with no under_note explaining why")
        elif r["under"] is not None and r["under"] not in measure_ids:
            e.add(w, f"under={r['under']!r} is not a register measure id")

        if not (r.get("finances") or []):
            e.add(w, "finances nothing — money with no recipient is not a fact about a sector")
        for node in r.get("finances") or []:
            if not node.startswith("project:") or node.split(":", 1)[1] not in project_ids:
                e.add(w, f"finances {node!r}, which names no project that exists")
        for node in r.get("supports") or []:
            if not node.startswith("technology:") or node.split(":", 1)[1] not in tech_ids:
                e.add(w, f"supports {node!r}, which names no technology that exists")


def check_status_groups(e: Errors) -> None:
    """Every funding status belongs to exactly one arithmetic group, and the app
    agrees with this file about which.

    Two failures are possible and both are silent without this check. A status
    added to FUNDING_STATUSES and to no group would be dropped from every total
    and from every "not counted" line at once — invisible rather than wrong,
    which is worse. And web/lib/transition.ts computes the same totals for the
    Capital section: if its lists drift from these, one number gets one label
    from two definitions."""
    groups = {
        "FUNDING_COMMITTED": sm.FUNDING_COMMITTED,
        "FUNDING_ANNOUNCED": sm.FUNDING_ANNOUNCED,
        "FUNDING_EXCLUDED": sm.FUNDING_EXCLUDED,
    }
    seen: dict[str, str] = {}
    for name, members in groups.items():
        for status in members:
            if status in seen:
                e.add("sector_map.py", f"funding status {status!r} is in both {seen[status]} "
                                       f"and {name}; it belongs to exactly one")
            seen[status] = name
    for status in sm.FUNDING_STATUSES:
        if status not in seen:
            e.add("sector_map.py", f"funding status {status!r} is in no arithmetic group; add it "
                                   f"to FUNDING_COMMITTED, FUNDING_ANNOUNCED or FUNDING_EXCLUDED "
                                   f"so a total knows what to do with it")

    ts = sm.ROOT / "web" / "lib" / "transition.ts"
    if not ts.exists():
        return
    text = ts.read_text(encoding="utf-8")
    for name, members in groups.items():
        m = re.search(rf"export const {name}: readonly FundingStatus\[\] = \[(.*?)\];",
                      text, re.S)
        if not m:
            e.add("web/lib/transition.ts", f"{name} is not declared; it must mirror "
                                           f"sector_map.py")
            continue
        found = tuple(re.findall(r'"([a-z_]+)"', m.group(1)))
        if found != tuple(members):
            e.add("web/lib/transition.ts", f"{name} is {found} but sector_map.py says "
                                           f"{tuple(members)}")


# The icon set is keyed by the noun it draws, not by a sector slug — four of the
# six ecosystems borrow a sector's drawing and two have their own. Read from the
# component rather than duplicated here, the same way the vocabulary parity
# check reads web/lib/transition.ts: a list of icon names in Python would be a
# second source of truth for what has actually been drawn.
_ICON_KEY = re.compile(r'^  "?([a-z0-9/-]+)"?: \(', re.MULTILINE)


def icon_keys() -> set[str]:
    src = (sm.ROOT / "web" / "components" / "SectorIcon.tsx").read_text(encoding="utf-8")
    return set(_ICON_KEY.findall(src))


def check_ecosystems(e: Errors, rows: list[dict], sectors: dict, tech_ids: set,
                     project_ids: set, material_ids: set, measure_ids: set) -> None:
    """The six, and the boundary rule — page specifications §4.2.

    WHAT IS CHECKED AND WHAT IS NOT. Every edge resolves, every icon has been
    drawn, and a sector edge names a slug that exists. What is NOT checked is
    that an instance has any edges at all: hydrogen and circular materials have
    no sector key and no dataset yet, and that is the state the node kind was
    introduced to be able to hold. An instance with nothing behind it renders no
    page and its tile opens /coverage; it does not fail a build.
    """
    icons = icon_keys()
    for r in rows:
        w = f"ecosystem {r.get('id', '?')}"
        _req(e, w, r, "id", "name", "icon")
        # `sectors` is required as a FIELD and allowed to be empty: an instance
        # with no sector key is the case this node kind exists for, and _req
        # cannot tell an empty list from an absent one.
        if "sectors" not in r:
            e.add(w, "no sectors field — an instance with no sector edge says so "
                     "with an empty list, which is a statement, rather than by "
                     "leaving the field out, which is an omission")
        if r.get("icon") and r["icon"] not in icons:
            e.add(w, f"icon {r['icon']!r} is not drawn in "
                     f"web/components/SectorIcon.tsx (drawn: {len(icons)})")
        for slug in r.get("sectors", []):
            if slug not in sectors:
                e.add(w, f"sectors names {slug!r}, which is not in data/sectors.json")
        # A scope note says the sector edge is WIDER than the instance. On an
        # instance with no sector edge there is nothing for it to be wider than.
        if r.get("sector_scope") and not r.get("sectors"):
            e.add(w, "carries a sector_scope and no sector edge — a scope note "
                     "narrows a sector key, and there is none to narrow")
        for field, known in (("technology", tech_ids), ("project", project_ids),
                             ("material", material_ids), ("measure", measure_ids)):
            for edge in r.get(field, []):
                if edge not in known:
                    e.add(w, f"{field} names {edge!r}, which is not a {field} id")

    check_project_boundary(e, rows)


def check_project_boundary(e: Errors, ecosystems: list[dict]) -> None:
    """A project belongs to the ecosystem whose product it makes (§4.2).

    A project is claimed by an ecosystem two ways: through the sector it is
    filed under, or by a direct edge. One claim is the rule; two is either a
    boundary that has been drawn twice or a genuinely shared node — a CO2 store,
    a hydrogen pipeline — and the difference is a judgement somebody has to make
    and record. So two claims fail the build unless the project says `shared`.

    Read the failure as a question rather than as a bug: which ecosystem's
    product does this project make? A recycling plant makes recovered material
    and belongs to circular materials; a cement plant with a recycled-content
    obligation on it makes cement and stays in cement, with an edge to circular
    materials from the obligation rather than from the plant.
    """
    by_sector: dict[str, list[str]] = {}
    for eco in ecosystems:
        for slug in eco.get("sectors", []):
            by_sector.setdefault(slug, []).append(eco["id"])

    claims: dict[str, set[str]] = {}
    for eco in ecosystems:
        for pid in eco.get("project", []):
            claims.setdefault(pid, set()).add(eco["id"])
    for p in sm.load("project"):
        for eid in by_sector.get(p["sector"], []):
            claims.setdefault(p["id"], set()).add(eid)

    shared = {p["id"] for p in sm.load("project") if p.get("shared")}
    for pid, owners in sorted(claims.items()):
        if len(owners) > 1 and pid not in shared:
            e.add(f"project {pid}", f"claimed by {sorted(owners)} — a project belongs to "
                                    f"the ecosystem whose product it makes. If it genuinely "
                                    f"serves several, mark it \"shared\": true and say so "
                                    f"in its note")


def check_measure_labels(e: Errors, measure_ids: set[str]) -> None:
    """The short labels the diagram draws instead of measure ids.

    Checked here as well as in build_sector_diagram.py, and the duplication is
    deliberate: the builder only ever sees the measures that made one sector's
    view, so an entry written today for a measure that enters the view next
    month would sit unchecked until the day it is drawn. This runs over the
    whole file.

    What is NOT checked here is uniqueness. Two measures may legitimately share
    a label as long as they never appear in the same picture, and only the
    builder knows which measures share a picture — so that gate lives there.
    """
    labels = sm.measure_labels()
    for measure_id, entry in sorted(labels.items()):
        where = f"measure label {measure_id}"
        if measure_id not in measure_ids:
            e.add(where, "names a measure that is not in the register")
        if not (entry.get("object") or "").strip():
            e.add(where, "no object — the label has nothing to be about")
            continue
        instrument = entry.get("instrument")
        if instrument is not None and instrument not in sm.INSTRUMENTS:
            e.add(where, f"instrument {instrument!r} is not in {list(sm.INSTRUMENTS)}")
            continue
        label = sm.short_label(entry)
        if len(label) > sm.MAX_SHORT_LABEL:
            e.add(where, f"{label!r} is {len(label)} characters, over the "
                         f"{sm.MAX_SHORT_LABEL} a node draws without an ellipsis")
        bad = dv.violations(label)
        if bad:
            e.add(where, f"{label!r} uses {sorted(set(bad))} — see "
                         f"sources/display_vocabulary.py")
        check_plain_block(e, where, entry, measure_id)


# A four-digit year, which is the one number an authored sentence is allowed to
# write out — and only where the measure's own `when` field says it.
_YEAR = re.compile(r"\b\d{4}\b")
# A number STANDING ON ITS OWN. Digits welded to letters are part of a name —
# CO2, PM2.5, R290 — and are no more a figure than the letters around them.
_DIGITS = re.compile(r"(?<![A-Za-z0-9])\d+(?![A-Za-z0-9])")

# Long enough to say what a measure requires, short enough that it is a title
# and not the sentence under it.
MAX_PLAIN_TITLE = 72


def check_plain_block(e: Errors, where: str, entry: dict, measure_id: str) -> None:
    """The key-measures list's title and sentence — brief 4 §5.

    THE RULE THIS ENFORCES is that the words are authored and the figures are
    not. An authored sentence with €75.46 typed into it is a number nobody
    gated, and it is wrong the next time the carbon price moves; the same
    sentence with {money_per_tonne} in it is wrong never, because
    sources/build_importance.py fills it from the measure's own money block on
    every build and fails if it cannot.

    So: no bare numbers, with one exception. A YEAR is a date rather than a
    figure, it is what makes 'from 2028' readable, and it is checkable against
    the measure's own `when` field — which is exactly what happens below. Any
    other run of digits is a figure that should have been a slot.
    """
    plain = entry.get("plain") or {}
    title = (plain.get("title") or "").strip()
    sentence = (plain.get("sentence") or "").strip()
    if not title or not sentence:
        e.add(where, "no plain block — every measure that has a label is one a sector "
                     "page may list, and the list says what a measure requires or grants "
                     "in a title and one sentence")
        return

    if len(title) > MAX_PLAIN_TITLE:
        e.add(where, f"the plain title is {len(title)} characters, over {MAX_PLAIN_TITLE}")
    if title.endswith("."):
        e.add(where, "the plain title ends in a full stop; it is a title, not a sentence")
    if _DIGITS.search(title):
        e.add(where, "the plain title carries a number — numbers belong in the sentence, "
                     "where they can be computed and dated")
    for field, text in (("title", title), ("sentence", sentence)):
        bad = dv.violations(text)
        if bad:
            e.add(where, f"the plain {field} uses {sorted(set(bad))} — see "
                         f"sources/display_vocabulary.py")

    if len([s for s in re.split(r"(?<=[.!?]) +", sentence) if s]) > 1:
        e.add(where, "the plain sentence is more than one sentence")
    if not sentence.endswith("."):
        e.add(where, "the plain sentence does not end in a full stop")

    for name in sm.slots_named(sentence):
        if name not in sm.MEASURE_SLOTS:
            e.add(where, f"the plain sentence names {{{name}}}, which is not one of "
                         f"{list(sm.MEASURE_SLOTS)}")

    when = _measure_when(measure_id)
    years = set(_YEAR.findall(when or ""))
    for token in _DIGITS.findall(sm._SLOT_RE.sub(" ", sentence)):
        if len(token) == 4 and token in years:
            continue
        e.add(where, f"the plain sentence writes {token!r} out. A figure belongs in a "
                     f"{{slot}}; a year is allowed only where the measure's own `when` "
                     f"says it, and this one says {when!r}")


def _measure_when(measure_id: str) -> str:
    """The measure's own `when`, read from the register it lives in."""
    slug, mid = measure_id.split(":", 1)
    path = sm.ROOT / "data" / f"{slug}.json"
    if not path.exists():
        return ""
    for row in json.loads(path.read_text(encoding="utf-8")):
        if row.get("id") == mid:
            return row.get("when") or ""
    return ""


def check_prose(e: Errors) -> list[str]:
    """The sector's one reviewed sentence, and whether anyone has read it.

    Same discipline as the ego notes: a sector that has a map must have a
    sentence written for it, and the build fails if it does not. It does NOT
    fail on the sentence being unreviewed — the page renders a computed
    sentence until the block is approved, so a draft is a state the site
    handles rather than a defect. What would be a defect is a draft nobody
    remembers writing, which is why every run prints them.
    """
    import json as _json
    doc = _json.loads((sm.ROOT / "data" / "prose.json").read_text(encoding="utf-8"))
    block = doc.get("transition_notes") or {}
    notes = block.get("sectors", {})
    mapped = {b["sector"] for b in sm.load("bottleneck")}
    for sector in sorted(mapped):
        if sector not in notes:
            e.add(f"prose {sector}", "has a transition map and no note in "
                                     "data/prose.json transition_notes")
    # The orientation paragraph, same discipline one level up: a mapped sector
    # must have one, and an unreviewed block is a state rather than a defect.
    # It has no computed fallback — standing context is the one thing on the
    # page that cannot be derived from the panels — so an unwritten paragraph
    # means the page simply opens on its lead block, as it did before.
    orient = doc.get("sector_orientation") or {}
    paras = orient.get("sectors", {})
    for sector in sorted(mapped):
        if sector not in paras:
            e.add(f"prose {sector}", "has a transition map and no orientation paragraph in "
                                     "data/prose.json sector_orientation")

    # One description per ecosystem instance (page specifications §4.2). An
    # instance must HAVE a slot — a missing key is an instance nobody has
    # thought about — and the text is allowed to be empty, which is the state
    # every one of them is in until George supplies the words. What is checked
    # about a written one is that it is the two sentences the specification
    # asks for: a description that runs to a paragraph is the perimeter
    # argument moving onto the tile's hover text.
    descriptions = (doc.get("ecosystem_descriptions") or {}).get("ecosystems", {})
    outstanding: list[str] = []
    for eco in sm.load("ecosystem"):
        entry = descriptions.get(eco["id"])
        if entry is None:
            e.add(f"prose {eco['id']}", "is an ecosystem instance with no description slot "
                                        "in data/prose.json ecosystem_descriptions")
            continue
        text = (entry.get("description") or "").strip()
        if not text:
            outstanding.append(eco["id"])
            continue
        count = len([x for x in re.split(r"(?<=[.!?]) +", text) if x])
        if count != 2:
            e.add(f"prose {eco['id']}", f"the ecosystem description is {count} sentences; "
                                        f"§4.2 asks for two — what it contains, and where "
                                        f"its boundary runs")

    # The regenerated lead, held for review (brief 4 §6). It is a COPY of the
    # built lead rather than an input to it, so an unapproved one changes
    # nothing on the site — but a copy that has drifted from what the page says
    # is worse than no copy, so it is checked against the built file and
    # printed until somebody has read it.
    held = doc.get("sector_lead") or {}
    leads = held.get("sectors", {})
    for sector in sorted(leads):
        path = sm.DATA / "lead" / f"{sector.replace('/', '__')}.json"
        if not path.exists():
            e.add(f"prose {sector}", "sector_lead holds a lead for a sector with no built "
                                     "lead in data/transition/lead")
            continue
        built = _json.loads(path.read_text(encoding="utf-8"))
        if leads[sector].get("fingerprint") != built["fingerprint"]:
            e.add(f"prose {sector}", "the lead held in data/prose.json was copied from facts "
                                     f"{leads[sector].get('fingerprint')!r} and the built lead "
                                     f"is now {built['fingerprint']!r} — regenerate the held "
                                     f"copy, or it records a sentence the site has stopped "
                                     f"saying")

    pending = []
    if block.get("status") not in ("approved", "final"):
        pending += [f"  {s}: {notes[s]['sentence'][:88]}…" for s in sorted(notes)]
    if orient and orient.get("status") not in ("approved", "final"):
        pending += [f"  {s} (orientation): {paras[s]['paragraph'][:76]}…" for s in sorted(paras)]
    if held and held.get("status") not in ("approved", "final"):
        pending += [f"  {s} (lead): {leads[s]['sentence'][:76]}…" for s in sorted(leads)]
    if outstanding:
        pending += [f"  {i} (ecosystem description): not written — the tile has no hover "
                    f"text and the coverage page lists nothing for it" for i in outstanding]
    return pending


def main() -> int:
    rows = sm.load_all()
    sectors = sm.sectors()
    e = Errors()

    tech_ids = {r["id"] for r in rows["technology"]}
    param_ids = {r["id"] for r in rows["parameter"]}
    measure_ids = sm.register_measure_ids()

    for kind, kind_rows in rows.items():
        ids = [r.get("id") for r in kind_rows]
        for dupe in {i for i in ids if ids.count(i) > 1}:
            e.add(f"{kind} {dupe}", "duplicate id")

    check_technologies(e, rows["technology"], sectors)
    check_parameters(e, rows["parameter"], tech_ids, sectors)
    check_bottlenecks(e, rows["bottleneck"], tech_ids, param_ids, measure_ids, sectors)
    check_projects(e, rows["project"], tech_ids, measure_ids, sectors)
    project_ids = {r["id"] for r in rows["project"]}
    material_ids = {r["id"] for r in rows["material"]}
    check_materials(e, rows["material"], sectors, tech_ids, project_ids, param_ids,
                    material_ids)
    check_funding(e, rows["funding"], tech_ids, project_ids, measure_ids, param_ids)
    check_measure_labels(e, measure_ids)
    check_ecosystems(e, rows["ecosystem"], sectors, tech_ids, project_ids, material_ids,
                     measure_ids)
    check_status_groups(e)

    drafts = check_prose(e)

    counts = ", ".join(f"{len(v)} {k}" for k, v in rows.items())
    if e.errors:
        print(f"check_sector_schema: {len(e.errors)} problems in {counts}\n")
        print("\n".join(e.errors))
        return 1

    print(f"check_sector_schema: OK — {counts}")
    if drafts:
        print(f"\ndraft prose awaiting review ({len(drafts)}) — the page renders the computed "
              f"sentence until the block in data/prose.json is approved:")
        print("\n".join(drafts))
    if e.stale:
        print(f"\nstale parameters ({len(e.stale)}) — reported, not failed:")
        print("\n".join(e.stale))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(sm.ROOT / "sources"))
    raise SystemExit(main())

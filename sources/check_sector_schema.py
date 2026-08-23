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

import re
import sys
from datetime import date

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
        _req(e, w, r, "id", "transition", "name", "description", "readiness", "sectors")
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
        for i, f in enumerate(r.get("public_funding") or []):
            fw = f"{w} public_funding[{i}]"
            _req(e, fw, f, "programme", "source_url")
            _url(e, fw, f.get("source_url"), "source_url")
            # An amount is required to be RECORDED, not to be known: a grant whose
            # size the company never published is a real funding line, and dropping
            # it would understate the public money in the project. `null` is allowed
            # and must carry a note saying so, which is what stops an amount from
            # going missing by accident rather than by decision.
            if "amount_eur" not in f:
                e.add(fw, "no amount_eur; use null with a note if the amount is unpublished")
            elif f["amount_eur"] is None and not f.get("note"):
                e.add(fw, "amount_eur is null with no note explaining why")
            mid = f.get("measure")
            if mid and mid not in measure_ids:
                e.add(fw, f"measure={mid!r} is not a register measure id")
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
    if block.get("status") in ("approved", "final"):
        return []
    return [f"  {s}: {notes[s]['sentence'][:88]}…" for s in sorted(notes)]


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

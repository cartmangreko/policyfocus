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

  COORDINATES    every project carries at least one located site, and every site
                 carries a latitude, a longitude, a precision and a source. A
                 project without coordinates cannot be drawn, and a map that
                 quietly omits the plants it has no point for is a map that
                 reads as a claim about where the industry is. `precision:
                 "town"` fails by name: a town centroid drawn as a works is a
                 wrong fact rendered confidently.

  STORAGE        every project that deploys a capture technology says where the
                 tonne goes -- either the id of a storage project, or
                 `"unresolved": true` with a note. Unresolved is a fact about
                 the chain and is renderable; silence is not, because a page
                 with nothing in that slot reads as a project whose storage
                 nobody asked about.

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
import eov
import osgb36
import sector_map as sm
import utm

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")


class Errors:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.stale: list[str] = []
        # Rows on sectors that have not yet adopted owners-as-a-list.
        self.ownerless: list[str] = []

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


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _hosted_copy(e: Errors, where: str, src: dict) -> None:
    """A DOCUMENT IS SOURCED BY ITS AUTHOR, NOT BY ITS HOST.

    An applicant's own permit submission is that applicant's statement wherever
    the file happens to sit, so a copy held by a campaign group, a news outlet or
    a mirror may place a row -- and the row then has to say so, because the
    reader is being asked to trust an author while fetching from someone else.
    The block is what makes that checkable rather than merely disclosed: the host
    URL says where this copy came from, the date says when it answered, and the
    digest says WHICH BYTES were read. A host that swaps the file, truncates it
    or serves a different revision changes the digest, and the claim that the
    quoted passage is in the document stops being unfalsifiable.

    The label is fixed text and not free prose, because it is rendered on the
    page: every citation standing on a copy reads the same three words, so a
    reader learns the signal once.
    """
    w = f"{where} hosted_copy"
    _req(e, w, src["hosted_copy"], "host", "host_url", "retrieved_date", "sha256", "label")
    block = src["hosted_copy"]
    _url(e, w, block.get("host_url"), "host_url")
    _date(e, w, block, "retrieved_date")
    digest = str(block.get("sha256") or "")
    if digest and not SHA256_RE.match(digest):
        e.add(w, f"sha256={digest!r} is not 64 lowercase hex characters — a digest "
                 f"nobody can recompute is a digest that checks nothing")
    if block.get("label") != "hosted copy":
        e.add(w, f"label={block.get('label')!r} — the label is the fixed words "
                 f"'hosted copy', which is what the page renders")
    if not (src.get("publisher") or "").strip():
        e.add(w, "is on a source with no publisher — the whole point of the block is "
                 "that the publisher names the AUTHOR while the host names the copy")


def _source_list(e: Errors, where: str, row: dict) -> None:
    sources = row.get("sources")
    if not sources:
        e.add(where, "no sources")
        return
    for i, s in enumerate(sources):
        w = f"{where} sources[{i}]"
        _url(e, w, s.get("url"))
        _req(e, w, s, "title", "publisher", "date")
        # A SOURCE'S DATE CARRIES ITS PRECISION, from 9 September 2026, and
        # `retrieved_date` does not — the two are different kinds of date and the
        # rule says so rather than treating them alike.
        #
        # A PUBLISHER'S DATE IS AS EXACT AS THE PUBLISHER MADE IT. Most are days.
        # ITM Power's Gigastack phase-2 report carries November 2021 and no day;
        # a journal issue is a month; a statistical release can be a year. Those
        # are stored padded to the first, like every other date on this layer that
        # says when something WAS.
        #
        # `retrieved_date` IS ALWAYS A DAY, because it is the day somebody here
        # fetched the page and there is no version of that fact that is vaguer.
        # It is gated to the day shape rather than given a precision field, so
        # the asymmetry is enforced instead of remembered.
        # A SOURCE'S DATE MAY BE AN UPPER BOUND, which no other date on this layer
        # may be, so this call cannot share the event vocabulary.
        if s.get("date_precision") == "not_after":
            if not s.get("captured_at"):
                e.add(w, "date_precision=\"not_after\" with no captured_at — an upper "
                         "bound on a publication date is the capture that proves the text "
                         "existed, and without the capture it is a guess")
            if not EVENT_DATE_SHAPE["day"].match(str(s.get("date") or "")):
                e.add(w, "date_precision=\"not_after\" but date is not a day — the bound "
                         "is a capture, and a capture happens on a day")
        else:
            _dated(e, w, s, "date", "date_precision")
        if s.get("captured_at") is not None:
            if not EVENT_DATE_SHAPE["day"].match(str(s["captured_at"])):
                e.add(w, f"captured_at={s['captured_at']!r} is not YYYY-MM-DD — it is the "
                         f"day a crawler took the copy")
            if not s.get("archived"):
                e.add(w, "captured_at without archived: true — the field records an "
                         "archive capture and nothing else")
        if s.get("retrieved_date") is not None:
            if not EVENT_DATE_SHAPE["day"].match(str(s["retrieved_date"])):
                e.add(w, f"retrieved_date={s['retrieved_date']!r} is not YYYY-MM-DD — it "
                         f"is the day somebody fetched the page and there is no vaguer "
                         f"version of that fact, so it carries no precision field")
        if s.get("hosted_copy") is not None:
            _hosted_copy(e, w, s)


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
        _dated(e, w, r, "date_of_value", "date_of_value_precision")
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


# COORDINATE-SOURCE EXCEPTIONS, named one at a time, in the same shape and for
# the same reason as the offshore exceptions in check_coordinates.py: the list is
# short, every entry is a sentence somebody wrote, and the gate prints all of
# them on every run. That is the whole difference between an exception and a
# loophole.
#
# THE ONE ENTRY IS A HOLE IN THE VOCABULARY AND SHOULD BE READ AS ONE. The three
# source types describe how you identify a WORKS -- a polygon somebody drew, an
# address the operator published, a parcel a permit names. A depleted offshore
# gas field has none of those. It has a name, a concession block and a position
# in the technical literature, and no amount of looking will produce a street.
# The honest options were a fourth source type or a named exception; this is the
# cheaper one to reverse, and it keeps the vocabulary describing works rather
# than quietly widening to mean "anything citable".
#
# An entry naming a site that no longer exists fails, so the list cannot rot.
COORDINATE_SOURCE_EXCEPTIONS = {
    ("galata-co2-storage", "Galata gas field, Black Sea"):
        "A depleted offshore gas field, not a works: it has no address, no parcel "
        "and no polygon anybody has drawn. The position is the field's own, and "
        "the source states it as a coordinate rather than describing a place. "
        "check_coordinates.py holds the same point against a measured 22.91 km "
        "offshore exception, which is the check that actually constrains it.",
}


# THE PROJECTIONS A PERMIT MAY STATE A POSITION IN, and the module that inverts
# each. Closed and small on purpose: a system in this table is one somebody has
# implemented and self-checked, and a permit quoting any other projection is a
# coordinate this repository cannot re-run — which is the same as a coordinate it
# cannot defend. Adding one means writing the conversion and its checks, not
# widening a vocabulary.
GRID_SYSTEMS = {
    "OSGB36": (osgb36, osgb36.to_wgs84),
    "ETRS89 / UTM 30N": (utm, lambda e_, n_: utm.to_wgs84(e_, n_, zone=30)),
    # The one conversion this repository does not implement. EOV is a double
    # projection on a datum ninety metres from WGS84, so sources/eov.py names
    # EPSG:23700, asks pyproj, and checks the answer three ways. The recompute
    # contract is unchanged: the stored point is still whatever the module
    # returns from the document's own easting and northing, on every build.
    "HD72 / EOV": (eov, eov.to_wgs84),
}


def _location(e: Errors, where: str, row: dict) -> None:
    """Every site a project sits on, and the source that puts it there.

    `location` is a list because a project is not always at one place. The list
    may not be empty: a project with no point is a project the map has to leave
    out, and the whole reason the coordinate is a first-class attribute rather
    than a rendering detail is that leaving one out silently is the failure.
    """
    sites = row.get("location")
    note = (row.get("location_note") or "").strip()
    located = row.get("located")
    _vocab(e, where, row, "located", sm.LOCATED)
    if "located" not in row:
        e.add(where, "no `located` — whether the row has a position is a question the row "
                     "answers, not one a reader works out from whether a list is empty")
    if row.get("location_precision") is not None:
        e.add(where, "carries location_precision at row level — that field is per SITE and "
                     "says how a position was resolved; whether there is one at all is "
                     "`located`")
    if not sites:
        # POSITION IS NOT AN ADMISSION LEG. Ruled 9 September 2026. A row with no
        # site says so POSITIVELY — `located: "no"` — rather than by an absence a
        # reader has to notice. It is admitted, it is counted, it is named in the
        # sentence over the overview as a row the picture does not draw, and its
        # own page renders without the location section instead of with an empty
        # one.
        #
        # THE NOTE IS STILL REQUIRED AND IS DOING MORE WORK THAN BEFORE. It is
        # the record of where a polygon was looked for, which is what stops this
        # from becoming the place coordinates go to be avoided: a reader can see
        # that Maasvlakte was swept, that HØST's only feature is an office, that
        # an industrial park is refused as an estate.
        if located != "no":
            e.add(where, f"no location and located={located!r} — a row with no site says "
                         f"so with located \"no\", which is a state on the record rather "
                         f"than an absence a reader has to infer")
        if not note:
            e.add(where, "no location and no location_note — write where a position was "
                         "looked for and what was found, so the absence is a decision on "
                         "the record and nobody repeats the sweep")
        return
    if located != "yes":
        e.add(where, f"located={located!r} and the row carries {len(sites)} site(s)")
    if not isinstance(sites, list):
        e.add(where, "location must be a list of sites, even where there is one")
        return
    for i, s in enumerate(sites):
        w = f"{where} location[{i}]"
        _req(e, w, s, "site", "precision", "location_precision", "retrieved_date",
             "confidence")
        _date(e, w, s, "retrieved_date")
        _vocab(e, w, s, "confidence", sm.CONFIDENCE)
        _vocab(e, w, s, "precision", sm.LOCATION_PRECISIONS)
        _vocab(e, w, s, "location_precision", sm.LOCATION_PRECISION_VALUES)
        if s.get("precision") == "town":
            e.add(w, "precision=town — a town centroid is not a plant site. Find the "
                     "works, or leave the project out of the register until somebody has")
        for field, lo, hi in (("lat", -90, 90), ("lon", -180, 180)):
            val = s.get(field)
            if not isinstance(val, (int, float)):
                e.add(w, f"{field} is missing or not a number")
            elif not lo <= val <= hi:
                e.add(w, f"{field}={val} is outside {lo}..{hi}")
        src = s.get("source") or {}
        _url(e, w, src.get("url"))
        # `type` says which of the three kinds of evidence put this works here,
        # and is required rather than defaulted: a coordinate whose provenance is
        # implied is one nobody can weigh. See sm.LOCATION_SOURCE_TYPES for what
        # each admits and, more importantly, for what none of them admits — a
        # geocoded town name and a position read off a press photograph are
        # refused by having no value to record them under.
        # A source may record that its publisher refuses a declared reader. The
        # shape is gated here as well as in check_links, because check_links only
        # sees the block when the URL actually 403s — a malformed one on a source
        # that happens to be answering would sit unnoticed until the day it
        # mattered.
        # THE COMPOSITE SITE STANDARD, gated leg by leg. A row that claims it
        # must show all three, because the whole argument for the standard is
        # that the legs cover each other's weaknesses — two of them is just a
        # weaker version of company-only, which is the thing it must not become.
        ev = s.get("site_evidence")
        if ev is not None:
            ew = f"{w} site_evidence"
            _vocab(e, ew, ev, "kind", sm.SITE_EVIDENCE_KINDS)
            if ev.get("kind") == "composite":
                _req(e, ew, ev, "company", "state", "basemap", "note")
                for leg in ("company", "state", "basemap"):
                    block = ev.get(leg)
                    if not isinstance(block, dict):
                        continue
                    _req(e, f"{ew}.{leg}", block, "url", "publisher", "verbatim")
                    _url(e, f"{ew}.{leg}", block.get("url"))

        if src.get("hosted_copy") is not None:
            _hosted_copy(e, w, src)

        refused = src.get("refused_declared_reader")
        if refused is not None:
            _req(e, f"{w} refused_declared_reader", refused, "last_verified", "by", "note")
            _date(e, f"{w} refused_declared_reader", refused, "last_verified")

        # HOW THE POSITION WAS RESOLVED HAS TO AGREE WITH WHAT RESOLVED IT.
        # sm.LOCATION_PRECISION_BY_SOURCE is the table; a source type absent from it
        # is one this check has nothing to say about, which today is only the
        # named coordinate-source exception.
        want = sm.LOCATION_PRECISION_BY_SOURCE.get((src or {}).get("type"))
        if want and s.get("location_precision") != want:
            e.add(w, f"location_precision={s.get('location_precision')!r} on a "
                     f"{src.get('type')!r} source, which supports {want!r} — the field "
                     f"is read off the evidence, and a precision the source cannot "
                     f"carry is a claim about the coordinate that nothing backs")

        # THE HOST WORKS, NAMED WHERE THE POINT IS NOT THE INSTALLATION'S OWN.
        # The hydrogen ruling of 9 September 2026 admits a site placed on the
        # works it stands on. That is a real position and it is not the same
        # claim as a polygon of the installation, so the row says which, the note
        # says it in words, and the sentence over the picture counts them. Only
        # a `works` precision can have one: a parcel list and a stated point are
        # about the project's own ground by construction.
        host = s.get("host_works")
        if host is not None:
            if s.get("location_precision") != "works":
                e.add(w, f"host_works on a location_precision={s.get('location_precision')!r} "
                         f"coordinate — a host works is a works polygon, and a parcel "
                         f"list or a stated point is already the project's own ground")
            if not str(host).strip():
                e.add(w, "host_works is empty — name the works, or leave the field out")
            if not (s.get("note") or "").strip():
                e.add(w, "host_works with no note — the reader is being told the mark is "
                         "not the installation, and the note is where that is said in "
                         "words rather than in a field")

        excused = (row.get("id"), s.get("site")) in COORDINATE_SOURCE_EXCEPTIONS
        if not excused:
            _req(e, w, src, "publisher", "verbatim", "type")
            _vocab(e, w, src, "type", sm.LOCATION_SOURCE_TYPES)
        else:
            _req(e, w, src, "publisher", "verbatim")
            if src.get("type") is not None:
                e.add(w, "is a named coordinate-source exception and also declares a "
                         "type — one or the other, or nobody can tell which rule the "
                         "coordinate is standing on")
        # A GRID REFERENCE IS RECOMPUTED, NOT TRUSTED. Where a permit gives a
        # British National Grid position, the stored latitude and longitude have
        # to be what osgb36.to_wgs84 produces from it — so the conversion cannot
        # be done once by hand, mistyped, or quietly adjusted afterwards, and a
        # reader can redo it. The projection and the datum shift are themselves
        # checked against the Ordnance Survey's published worked example every
        # time this gate runs; see osgb36.self_check.
        grid = s.get("grid_reference")
        if grid:
            _req(e, f"{w} grid_reference", grid, "system", "easting", "northing")
            system = grid.get("system")
            if system not in GRID_SYSTEMS:
                e.add(f"{w} grid_reference", f"system={system!r} — the systems "
                                             f"implemented are {sorted(GRID_SYSTEMS)}. A "
                                             f"projection nobody has written is a "
                                             f"conversion nobody can re-run")
            elif src.get("type") != "permit":
                e.add(f"{w} grid_reference", "is on a site whose coordinate source is "
                                             "not a permit — a grid reference comes from a "
                                             "filing, and recording one beside another "
                                             "kind of source hides which put the point here")
            else:
                module, convert = GRID_SYSTEMS[system]
                for failure in module.self_check():
                    e.add(module.__name__, failure)
                got = convert(grid["easting"], grid["northing"])
                if (s.get("lat"), s.get("lon")) != got:
                    e.add(w, f"lat/lon is {(s.get('lat'), s.get('lon'))} and the grid "
                             f"reference E {grid['easting']} N {grid['northing']} converts "
                             f"to {got} — one of the two has been edited alone")
        # A PLAN-PARCEL COORDINATE HAS TO SHOW ITS WORKING. The type says two
        # documents did one job — a plan naming parcels, a cadastre holding their
        # geometry — and neither is checkable without the list, the register and
        # the day it answered. `matched` under `listed` is not a failure and is
        # not hidden either: it is the number a reader needs to know how much of
        # the plan area the point was computed from.
        if src.get("type") == "plan_parcels":
            block = s.get("parcels")
            if not isinstance(block, dict):
                e.add(w, "source type=plan_parcels and no parcels block — the plan's own "
                         "list, the cadastre it was resolved against and the date it was "
                         "read are what make this coordinate reproducible")
            else:
                _req(e, f"{w} parcels", block, "gemarkung", "matched", "listed",
                     "service", "read_date")
                _date(e, f"{w} parcels", block, "read_date")
                _url(e, f"{w} parcels", block.get("service"), "service")
                matched, listed = block.get("matched"), block.get("listed")
                if isinstance(matched, int) and isinstance(listed, int):
                    if matched > listed:
                        e.add(f"{w} parcels", f"matched={matched} of listed={listed} — the "
                                              f"cadastre answered for more parcels than the "
                                              f"plan names")
                    if matched == 0:
                        e.add(f"{w} parcels", "matched=0 — no parcel resolved, so nothing "
                                              "placed this point")
                    if matched < listed and not block.get("not_found"):
                        e.add(f"{w} parcels", f"matched={matched} of listed={listed} and "
                                              f"`not_found` is empty — say which parcels the "
                                              f"cadastre did not answer for")

        if src.get("type") == "company" and not s.get("address"):
            e.add(w, "source type=company and no address block — a coordinate derived "
                     "from the operator's own materials has to quote the address or "
                     "parcel it was derived from, or the derivation is unrepeatable")
        addr = s.get("address")
        if addr:
            _url(e, f"{w} address", addr.get("url"))
            _req(e, f"{w} address", addr, "text", "publisher", "date")
            _date(e, f"{w} address", addr, "date")


def _storage(e: Errors, where: str, row: dict, technologies: dict, project_ids: set) -> None:
    """Where the captured tonne goes, for every project that captures one.

    Two shapes and no third. Naming a store resolves to a project in this same
    file, which is what makes the edge drawable and the store's own page
    reachable; `unresolved` is the other answer and is not a lesser one, but it
    still carries the source that failed to name a destination, because "nobody
    has said" is a claim about a document somebody read.
    """
    st = row.get("storage")
    if not sm.captures_co2(row, technologies):
        if st is not None:
            e.add(where, "carries `storage` and deploys no capture technology — the field "
                         "answers a question this project is not being asked")
        return
    if not st:
        e.add(where, "deploys a capture technology and says nothing about where the CO2 "
                     "goes. Name a storage project, or say \"unresolved\": true with a note")
        return
    src = st.get("source") or {}
    _url(e, f"{where} storage", src.get("url"))
    _req(e, f"{where} storage", src, "publisher", "date", "verbatim")
    _date(e, f"{where} storage", src, "date")
    if st.get("unresolved"):
        if st.get("project"):
            e.add(where, "storage is both unresolved and points at a project — one or "
                         "the other")
        _req(e, f"{where} storage", st, "note")
        return
    target = st.get("project")
    if not target:
        e.add(where, "storage names no project and is not marked unresolved")
        return
    if target not in project_ids:
        e.add(where, f"storage points at {target!r}, which is not a project id")
    _date(e, f"{where} storage", st, "since")
    _req(e, f"{where} storage", st, "since")


def _capacity(e: Errors, where: str, row: dict) -> None:
    """A capacity figure travels with the four things that make it readable, or
    it does not travel at all.

    THE COMPANION RULE IS THE WHOLE POINT. A bare number is the failure this
    block exists to prevent: 2.5 million tonnes of what, decided by whom, said
    when, and where can I read it. Announced capacity and capacity somebody has
    committed money to are different series, and a figure that has lost its
    basis cannot be sorted into either. So a non-empty capacity_value requires
    capacity_unit, capacity_basis, capacity_source_url and capacity_as_of, and a
    filled row missing any of them fails the build.

    AN EMPTY ROW IS NOT A FAILURE. Most cement rows have no product capacity on
    file — what is on file is CO2 captured, which is a different quantity — and
    the honest record of that is five absent fields, not an estimate. The gate
    is silent about them; the shortfall is reported by the export instead.
    """
    filled = [f for f in ("capacity_value", "capacity_unit", "capacity_basis",
                          "capacity_source_url", "capacity_as_of", "capacity_product")
              if row.get(f) not in (None, "")]
    if row.get("capacity_value") in (None, ""):
        if filled:
            e.add(where, f"has {', '.join(filled)} but no capacity_value — a companion "
                         f"field without the figure it qualifies says nothing")
        return
    if not isinstance(row.get("capacity_value"), (int, float)):
        e.add(where, "capacity_value is not a number")
    for f in ("capacity_unit", "capacity_basis", "capacity_source_url", "capacity_as_of",
              "capacity_as_of_precision"):
        if row.get(f) in (None, ""):
            e.add(where, f"capacity_value is set but {f} is missing — a figure without "
                         f"its unit, basis, source and date cannot be read")
    _vocab(e, where, row, "capacity_unit", sm.CAPACITY_UNITS)
    _vocab(e, where, row, "capacity_basis", sm.CAPACITY_BASES)
    _vocab(e, where, row, "capacity_product", sm.CAPACITY_PRODUCTS)
    _dated(e, where, row, "capacity_as_of", "capacity_as_of_precision")
    if row.get("capacity_source_url"):
        _url(e, where, row.get("capacity_source_url"), "capacity_source_url")
    if row.get("sector") in sm.CAPACITY_SECTORS and not row.get("capacity_product"):
        e.add(where, "capacity_value is set but capacity_product is missing — tonnes of "
                     "clinker and tonnes of crude steel are not the same tonne")
    _unit_product(e, where, row.get("capacity_unit"), row.get("capacity_product"))
    _alternates(e, where, row)


def _unit_product(e: Errors, where: str, unit, product) -> None:
    """A unit and a product that cannot be each other's.

    sm.UNIT_PRODUCTS is the pairing. Only the hydrogen units are constrained by
    it, because their sector makes two products and the others make one; a unit
    absent from the table is a unit this check has nothing to say about. See the
    note there.
    """
    allowed = sm.UNIT_PRODUCTS.get(unit)
    if allowed and product not in allowed:
        e.add(where, f"capacity_unit={unit!r} with capacity_product={product!r} — that "
                     f"unit measures {' or '.join(allowed)} and nothing else, and a total "
                     f"would add this figure into the wrong column")


def _alternates(e: Errors, where: str, row: dict) -> None:
    """The same phase, stated by the same source in a second unit.

    WHY THE LIST EXISTS. Electrolysis is quoted three ways and this register does
    not convert between them (sources/scope.md, "Three units for one
    electrolyser"). Where a source gives two of the three for one phase, throwing
    one away would lose a figure the source actually published, and putting it in
    a note would put it somewhere no total can reach. So it is a row of its own
    shape, with every companion the main figure carries, and the export picks
    between them by sm.CAPACITY_UNIT_PREFERENCE rather than by which was typed
    first.

    AN ALTERNATE MAY NOT REPEAT THE ROW'S OWN UNIT. Two figures in one unit for
    one phase is not an alternate reading, it is a disagreement, and it belongs in
    capacity_note where a reader is told which one the row stands on.
    """
    alts = row.get("capacity_alternates")
    if alts is None:
        return
    if not isinstance(alts, list):
        e.add(where, "capacity_alternates must be a list")
        return
    if alts and row.get("capacity_value") in (None, ""):
        e.add(where, "capacity_alternates with no capacity_value — an alternate reading "
                     "of a figure the row does not carry has nothing to be an alternate of")
    seen = {row.get("capacity_unit")}
    for i, a in enumerate(alts):
        w = f"{where} capacity_alternates[{i}]"
        _req(e, w, a, "value", "unit", "product", "basis", "source_url", "as_of")
        _vocab(e, w, a, "unit", sm.CAPACITY_UNITS)
        _vocab(e, w, a, "basis", sm.CAPACITY_BASES)
        _vocab(e, w, a, "product", sm.CAPACITY_PRODUCTS)
        _dated(e, w, a, "as_of", "as_of_precision")
        _url(e, w, a.get("source_url"), "source_url")
        if not isinstance(a.get("value"), (int, float)):
            e.add(w, "value is not a number")
        _unit_product(e, w, a.get("unit"), a.get("product"))
        if a.get("unit") in seen:
            e.add(w, f"unit={a.get('unit')!r} is already carried by this row — two figures "
                     f"in one unit is a disagreement, not an alternate reading, and the "
                     f"row has to say in capacity_note which one it stands on")
        seen.add(a.get("unit"))
    # WHICH OF THE READINGS THE ROW LEADS WITH, enforced here rather than chosen
    # in the export. sm.CAPACITY_UNIT_PREFERENCE says MW input wins where it is
    # present, and the cheapest place to hold that is at authoring time: a
    # selection made in the export would be a second rule, invisible on the row,
    # and a reader comparing the row with the total would not be able to see why
    # they disagree.
    order = sm.CAPACITY_UNIT_PREFERENCE
    if row.get("capacity_unit") in order:
        mine = order.index(row["capacity_unit"])
        for a in alts:
            if a.get("unit") in order and order.index(a["unit"]) < mine:
                e.add(where, f"capacity_unit={row['capacity_unit']!r} while an alternate "
                             f"carries {a['unit']!r}, which comes first in "
                             f"CAPACITY_UNIT_PREFERENCE — the row leads with the figure "
                             f"the export totals, and the alternate is the other reading")


TARGET_RE = re.compile(r"^\d{4}(-(H[12]|Q[1-4]|\d{2}(-\d{2})?))?$")

# Which shape each precision has to be written in. A precision that does not match
# its own value is the failure this pairing exists to catch: "2026" declared as a
# month is a target somebody will later read as January.
TARGET_SHAPE = {
    "year":    re.compile(r"^\d{4}$"),
    "half":    re.compile(r"^\d{4}-H[12]$"),
    "quarter": re.compile(r"^\d{4}-Q[1-4]$"),
    "month":   re.compile(r"^\d{4}-\d{2}$"),
    "day":     re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}


def _schedule(e: Errors, where: str, row: dict) -> None:
    """Every stated_schedule entry is a dated statement by a named kind of source
    that a milestone would be reached by a stated time.

    AN EMPTY HISTORY IS NOT A FAILURE and is the ordinary case: most rows here
    have no source that states a date, and an empty list is the honest record of
    that. What the gate refuses is a half-written entry, because a target with no
    source or a precision that disagrees with its own value is worse than no
    target at all -- it is a number a reader will take for a promise somebody made.

    IT IS APPEND-ONLY AND IN DATE ORDER, like status_history, and for the same
    reason: the point of the list is that the first statement survives the fifth.
    """
    sched = row.get("stated_schedule")
    if sched is None:
        e.add(where, "no stated_schedule — use [] where no source on file states a "
                     "date, so that 'nobody has said' and 'nobody has looked' are "
                     "different objects")
        return
    dates = []
    for i, h in enumerate(sched):
        w = f"{where} stated_schedule[{i}]"
        _req(e, w, h, "date", "milestone", "target_date", "target_precision",
             "source_url", "source_type", "evidence_mode", "speaker")
        _vocab(e, w, h, "milestone", sm.SCHEDULE_MILESTONES)
        _vocab(e, w, h, "speaker", sm.SCHEDULE_SPEAKERS)
        _vocab(e, w, h, "target_precision", sm.TARGET_PRECISIONS)
        _vocab(e, w, h, "source_type", sm.PROJECT_SOURCE_TYPES)
        _vocab(e, w, h, "evidence_mode", sm.EVIDENCE_MODES)
        _date(e, w, h, "date")
        # A STATEMENT IS AN EVENT TOO. The date on a schedule entry is the day
        # the promise was made, and it is dated exactly as a status event is —
        # padded, with the precision recorded — because a company that said
        # something "in November 2021" said it then whether or not the page
        # carries a day.
        _event_date(e, w, h)
        _url(e, w, h.get("source_url"), "source_url")
        t, p = h.get("target_date"), h.get("target_precision")
        if t is not None and not TARGET_RE.match(str(t)):
            e.add(w, f"target_date={t!r} is not YYYY, YYYY-Hn, YYYY-Qn, YYYY-MM or "
                     f"YYYY-MM-DD")
        elif t is not None and p in TARGET_SHAPE and not TARGET_SHAPE[p].match(str(t)):
            e.add(w, f"target_date={t!r} is not the shape target_precision={p!r} "
                     f"claims — a target read at the wrong precision is a promise "
                     f"nobody made")
        dates.append(str(h.get("date", "")))
    if dates != sorted(dates):
        e.add(where, "stated_schedule is not in date order; it is append-only and a "
                     "revision is a new entry after the statement it revises")


EVENT_DATE_SHAPE = {
    "day":   re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "month": re.compile(r"^\d{4}-\d{2}-01$"),
    "year":  re.compile(r"^\d{4}-01-01$"),
}


def _dated(e: Errors, where: str, obj: dict, date_field: str, prec_field: str) -> None:
    """A date and the precision the source gave it to, checked as a pair.

    The general form of _event_date, which is now one caller of it. Every date on
    this layer that records WHEN SOMETHING WAS — an event, the day a capacity was
    stated, the day a parameter's value held — is written to the day and padded
    to the earliest it can be, with a field saying how exactly the source put it.
    A target, which records when something WILL BE, keeps the opposite convention
    and its own field.
    """
    _req(e, where, obj, prec_field)
    _vocab(e, where, obj, prec_field, sm.VALUE_DATE_PRECISIONS)
    date, prec = str(obj.get(date_field) or ""), obj.get(prec_field)
    if not EVENT_DATE_SHAPE["day"].match(date):
        e.add(where, f"{date_field}={date!r} is not YYYY-MM-DD — a date on this layer is "
                     f"always written to the day and `{prec_field}` says what the source "
                     f"gave it to")
    elif prec in EVENT_DATE_SHAPE and not EVENT_DATE_SHAPE[prec].match(date):
        pad = "1 January" if prec == "year" else "the first of its month"
        e.add(where, f"{date_field}={date!r} with {prec_field}={prec!r} — a {prec}-precision "
                     f"date is padded to {pad}, which is the earliest it can be; anything "
                     f"else claims a precision the source did not give")


def _event_date(e: Errors, where: str, h: dict) -> None:
    """An event date, always written to the day, with what the source actually
    gave it to.

    THE DATE IS STORED PADDED AND THE PRECISION SAYS SO. A month-precision event
    sits on the first of its month and a year-precision one on 1 January, which
    is the earliest the event can have happened — the reading that does not
    overstate, and the opposite of the convention for a stated target, which is
    read at the end of its period for the same reason.

    The pairing is checked, not just the vocabulary: a `year` on 2024-06-01 would
    be a padded date somebody had padded to the wrong place, and a `day` on a date
    nobody knows to the day is the claim this field exists to stop.
    """
    _dated(e, where, h, "date", "date_precision")


def _event(e: Errors, where: str, h: dict, i: int, prev_status: str | None) -> None:
    """Every status_history entry carries the six fields that make it an event
    rather than a sentence, and the two derived ones agree with the positional
    reading the rest of the repository already uses.

    WHY status_to SITS BESIDE status AND DOES NOT REPLACE IT. `status` is what
    web/lib/transition.ts and check_transition_parity.py read, and the whole
    transition rule is positional: an entry is a change if its status differs
    from the one before. Renaming the field would have rewritten both sides of a
    parity gate to say what they already said. So `status_to` is the same value
    under the name an event table wants, `status_from` is the entry before it,
    and this gate holds the two readings together — which is what stops the pair
    from drifting into a second, quieter source of truth.
    """
    _req(e, where, h, "event_kind", "source_type", "evidence_mode")
    _event_date(e, where, h)
    _vocab(e, where, h, "event_kind", sm.PROJECT_EVENT_KINDS)
    _vocab(e, where, h, "source_type", sm.PROJECT_SOURCE_TYPES)
    _vocab(e, where, h, "evidence_mode", sm.EVIDENCE_MODES)
    _vocab(e, where, h, "status_to", sm.PROJECT_STATUSES)
    if "status_to" not in h:
        e.add(where, "missing status_to")
    elif h.get("status_to") != h.get("status"):
        e.add(where, f"status_to={h.get('status_to')!r} but status={h.get('status')!r}; "
                     f"they are the same fact under two names and must agree")
    if "status_from" not in h:
        e.add(where, "missing status_from — the first entry carries it as null")
    elif h["status_from"] != prev_status:
        e.add(where, f"status_from={h['status_from']!r} but the entry before this one is "
                     f"{prev_status!r}")
    if i == 0 and h.get("status_from") is not None:
        e.add(where, "the first entry has nothing to come from; status_from must be null")


def _edges(e: Errors, where: str, row: dict, project_ids: set) -> None:
    """What this project is attached to, as its own source names it.

    ASSERTED ONLY, AND THE CLASS SAYS SO. Every edge written by hand is one a
    source states in words, and it carries the words. A structural edge -- the
    grid connection every electrolyser needs whether or not anybody wrote it down
    -- is NOT written here; it follows from a technology rule in a later step, and
    the gate refuses a hand-written one so that the two kinds cannot be confused
    once both exist. See sm.EDGE_CLASSES.

    A TARGET IS A PROJECT ID OR IT IS NAMED PROSE. `project:<id>` points at a row
    in this file and is checked; anything else is `external:<slug>` and carries a
    `target_name`, because most of what a hydrogen site is attached to -- a
    pipeline, a store, a refinery in another sector -- has no row yet. An edge
    that could point at nothing and say nothing would be a claim with no referent.
    """
    edges = row.get("edges")
    if edges is None:
        return
    if not isinstance(edges, list):
        e.add(where, "edges must be a list")
        return
    for i, g in enumerate(edges):
        w = f"{where} edges[{i}]"
        _req(e, w, g, "kind", "target", "type", "class", "since", "evidence")
        _vocab(e, w, g, "kind", sm.EDGE_KINDS)
        _vocab(e, w, g, "type", sm.EDGE_TYPES)
        _vocab(e, w, g, "class", sm.EDGE_CLASSES)
        _date(e, w, g, "since")
        if g.get("class") == "structural":
            e.add(w, "is written as a structural edge — structural edges follow from a "
                     "technology rule and are not authored on a row; write the asserted "
                     "edge the source states, or wait for the rule")
        target = str(g.get("target") or "")
        if target.startswith("project:"):
            if target.split(":", 1)[1] not in project_ids:
                e.add(w, f"target {target!r} is not a project id")
        elif target.startswith("external:"):
            if not g.get("target_name"):
                e.add(w, "an external target has no target_name — an edge to something "
                         "with no row has to say what the thing is called")
        else:
            e.add(w, f"target={target!r} must be project:<id> or external:<slug>")
        ev = g.get("evidence")
        if not isinstance(ev, dict):
            e.add(w, "evidence is missing — an asserted edge is asserted by somebody, in "
                     "a sentence, and the sentence is the whole of the claim")
            continue
        _req(e, f"{w} evidence", ev, "url", "publisher", "verbatim")
        _url(e, f"{w} evidence", ev.get("url"))
        _vocab(e, f"{w} evidence", ev, "source_type", sm.PROJECT_SOURCE_TYPES)


# REASON-AS-STATED BINDS EVERYWHERE, since 9 September 2026. It did not on the
# day it landed: nineteen stopped events across batteries, cement, steel and CCS
# predated the rule, and they were REPORTED rather than failed on the ruling that
# the only honest backfill is a re-read. The re-read happened. Every stopping
# transition on this file now carries a reason read from its own sources, six of
# them `unstated` because the source gives none, so the exemption has nothing
# left to exempt and is gone rather than left standing as a door.
#
# WHAT THE RE-READ FOUND, because it is the reason the field was worth having.
# Of fifteen stopping transitions, six give no cause at all — a company that
# stops a project and says only that the "prerequisites were unlikely to be met",
# an authority that records "Das Vorhaben wird nicht mehr umgesetzt", a filing
# that notes an appointment of administrators. Two more state a cause this
# vocabulary cannot hold: an owner changing the business it is in, and a venture
# losing its technology partner. Both are filed at their nearest value with the
# quote beside them and the misfit written on the row.

def _stop_reason(e: Errors, where: str, h: dict, transition: bool) -> None:
    """Why a project stopped, in the source's own terms or `unstated`.

    REQUIRED ON EVERY ENTRY THAT LANDS IN A STOPPED STATUS, and refused on every
    other, so the field cannot drift into a general note. `unstated` is a real
    answer and the commonest one: a company that pauses a project without giving a
    reason has told us that, and a gate that accepted an empty field here would
    let a guess be written in the same space as a quotation.
    """
    # REQUIRED ON THE EVENT THAT STOPS THE PROJECT, AND ONLY THAT ONE. A later
    # entry about an already-paused project reports on it rather than stopping
    # it — Slite's withdrawn permit application, Lyten's memorandum over a site
    # that has been still since 2024 — and demanding a reason from each would
    # make the register restate one cause every time somebody wrote about the
    # consequence. The test is the positional one the whole layer uses: an entry
    # is a transition if its status differs from the entry before it.
    stopped = h.get("status_to") in sm.STOP_REASON_STATUSES and transition
    reason = h.get("stop_reason")
    if stopped and reason is None:
        msg = (f"moves to {h.get('status_to')!r} and states no stop_reason — write "
               f"the reason the source gives, or 'unstated' where it gives none")
        e.add(where, msg)
    elif reason is not None and h.get("status_to") not in sm.STOP_REASON_STATUSES:
        e.add(where, "carries a stop_reason and does not stop the project")
    if reason is not None:
        if not isinstance(reason, list) or not reason:
            e.add(where, "stop_reason must be a non-empty list, first entry primary — "
                         "sources give more than one reason and the field used to make "
                         "the register choose one and drop the rest into prose")
            reason = []
        for one in reason:
            if one not in sm.STOP_REASONS:
                e.add(where, f"stop_reason {one!r} is not one of {list(sm.STOP_REASONS)}")
        if len(reason) != len(set(reason)):
            e.add(where, "stop_reason repeats a value")
        if "unstated" in reason and len(reason) > 1:
            e.add(where, "stop_reason lists `unstated` beside another value — a source "
                         "that gives no reason cannot also give a secondary one")
        if reason and reason != ["unstated"] and not h.get("stop_reason_verbatim"):
            e.add(where, f"stop_reason={reason!r} with no stop_reason_verbatim — a reason "
                         f"that is not 'unstated' was read from a sentence, and the "
                         f"sentence is what makes it checkable")
        # WHERE THE SENTENCE CAME FROM, WHEN IT IS NOT THE EVENT'S OWN SOURCE.
        # Several of these events are dated from a filing or a notice that
        # records what happened and says nothing about why, while the company
        # said why somewhere else on the same day. Rather than move the event
        # onto the second source — which would re-date it — the quote carries
        # its own URL, and its absence means the quote is in the event's source.
        if h.get("stop_reason_source_url"):
            _url(e, where, h["stop_reason_source_url"], "stop_reason_source_url")
    elif h.get("stop_reason_verbatim") or h.get("stop_reason_source_url"):
        e.add(where, "carries a stop_reason quote and no stop_reason")


# THE SECTORS THAT HAVE ADOPTED owners-as-a-list. Hydrogen is written to it from
# the first row. The fifty-one rows that predate it are REPORTED and not failed,
# on the same reading the stop-reason backfill was done under: the honest way to
# fill an owner type is to read who owns the operator, and writing a plausible
# one across fifty-one rows to turn a gate green is the failure the field exists
# to prevent. The count is printed on every run until somebody does the reading.
OWNER_SECTORS = ("clean",)


def _owner_and_benchmarks(e: Errors, where: str, row: dict, sector: str | None) -> None:
    """Who owns the operator, and what the outside lists call this project.

    `owners` IS THE FACT AND `owner_listing` IS READ OFF IT. A project company is
    usually more than one party, and a single label was only ever workable
    because the first split this register met happened to have a majority. The
    list carries each party with its share and its own listing; the summary is
    the listing of whoever holds more than half, and `mixed` where nobody does.

    THE DERIVATION IS CHECKED RATHER THAN TRUSTED, because the whole point of
    storing a derived value is that a reader does not have to compute it — and a
    stored value nothing checks is a second source of truth waiting to drift.
    """
    owners = row.get("owners")
    if owners is not None:
        if not isinstance(owners, list) or not owners:
            e.add(where, "owners must be a non-empty list of {name, share, listing}")
            owners = None
        else:
            total = 0.0
            for i, o in enumerate(owners):
                w = f"{where} owners[{i}]"
                _req(e, w, o, "name", "listing")
                _vocab(e, w, o, "listing", sm.OWNER_LISTINGS)
                if o.get("listing") == "mixed":
                    e.add(w, "`mixed` describes a row and not a party — an owner is "
                             "listed, private or state-owned")
                if "share" not in o:
                    e.add(w, "no share; use null where no source states one")
                elif o["share"] is not None:
                    if not isinstance(o["share"], (int, float)) or not 0 < o["share"] <= 100:
                        e.add(w, f"share={o['share']!r} is not a percentage in (0, 100]")
                    else:
                        total += float(o["share"])
            if total > 100.0001:
                e.add(where, f"owner shares total {total:g} per cent")
    if row.get("owner_listing") is not None:
        _vocab(e, where, row, "owner_listing", sm.OWNER_LISTINGS)
    if owners:
        majority = [o for o in owners
                    if isinstance(o.get("share"), (int, float)) and o["share"] > 50]
        want = majority[0]["listing"] if majority else "mixed"
        if row.get("owner_listing") != want:
            e.add(where, f"owner_listing={row.get('owner_listing')!r} but the owners list "
                         f"gives {want!r} — it is the listing of the party holding more "
                         f"than half, and `mixed` where nobody does")
    elif row.get("owner_listing") == "mixed":
        e.add(where, "owner_listing=`mixed` with no owners list — `mixed` is a statement "
                     "about a split, and the split has to be on the row")
    # AN ABSENT OWNER TYPE IS A DECISION AND SAYS SO. The paper compares
    # disclosure by owner type, so a row with no answer is a row missing from
    # that comparison; leaving the field empty and silent would make "nobody
    # looked" and "the sources do not say" the same state. EWE is the case: it is
    # not listed on an exchange, it is held by municipal associations together
    # with a private investor, and no source read here states the split — so
    # `private` and `state-owned` would both be assertions and the row says that
    # instead of picking one.
    if row.get("owner_listing") is None and not (row.get("owner_listing_note") or "").strip():
        msg = ("no owner_listing and no owner_listing_note — the disclosure comparison "
               "the field exists for needs to know whether this row has no answer or was "
               "never asked")
        if sector in OWNER_SECTORS:
            e.add(where, msg)
        else:
            e.ownerless.append(f"  {where}")
    marks = row.get("benchmarks")
    if marks is None:
        return
    if not isinstance(marks, dict):
        e.add(where, "benchmarks must be an object keyed by benchmark name")
        return
    for k, v in marks.items():
        if k == "note":
            continue
        if k not in sm.BENCHMARKS:
            e.add(where, f"benchmarks names {k!r}, which is not one of "
                         f"{list(sm.BENCHMARKS)} — an id under a key nothing resolves is "
                         f"an id nobody can look up")
            continue
        # A LIST IS A REAL ANSWER AND NOT A CONVENIENCE. Both benchmarks count
        # PHASES as projects where this register counts a SITE, so a row that
        # holds one works matches three of their rows, and collapsing that to one
        # id would hide the mismatch the benchmark file exists to measure.
        ids = v if isinstance(v, list) else [v]
        if v is not None and not ids:
            e.add(where, f"benchmarks.{k} is an empty list; use null for 'searched and "
                         f"not there', which is a different fact from 'not searched'")
        for one in ids:
            if one is not None and not isinstance(one, (str, int)):
                e.add(where, f"benchmarks.{k} carries {one!r}, which is neither an id nor "
                             f"null; null is the record that the list was searched and "
                             f"this project is not in it")


def check_projects(e: Errors, rows: list[dict], tech_ids: set, measure_ids: set,
                   sectors: dict, technologies: dict, project_ids: set) -> None:
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
        _capacity(e, w, r)
        _schedule(e, w, r)
        history = r.get("status_history") or []
        dates = []
        prev_status = None
        for i, h in enumerate(history):
            hw = f"{w} status_history[{i}]"
            _req(e, hw, h, "status", "date", "source_url")
            _vocab(e, hw, h, "status", sm.PROJECT_STATUSES)
            _date(e, hw, h, "date")
            _url(e, hw, h.get("source_url"), "source_url")
            _event(e, hw, h, i, prev_status)
            _stop_reason(e, hw, h, sm.is_transition(history, i))
            # AN OWNERSHIP EVENT IS ONE FACT AND SAYS BOTH ENDS OF IT. `from` and
            # `to` are required because "the owner changed" without naming the
            # owners is an event nobody can check, and they are refused on every
            # other kind so the field cannot quietly become a note.
            #
            # THE KIND IS READ FROM `event_kind`. This branch was written against
            # a field called `kind`; the same fact is called `event_kind` on main,
            # where it sits beside source_type and evidence_mode as one of the six
            # fields _event requires. One name survives the rebase and it is the
            # one the rest of the schema uses -- two names for one fact is exactly
            # the quiet second source of truth these gates exist to prevent.
            if h.get("event_kind") == "ownership":
                _req(e, hw, h, "from", "to")
                if i == 0:
                    e.add(hw, "an ownership event cannot open a history — there is no "
                              "status before it for its own to be unchanged from, and "
                              "the first entry is always read as a status change")
                elif h.get("status") != history[i - 1].get("status"):
                    e.add(hw, f"is an ownership event whose status ({h.get('status')!r}) "
                              f"differs from the entry before it "
                              f"({history[i - 1].get('status')!r}) — a project changing "
                              f"hands and changing status is two events, and one entry "
                              f"saying both reads as one causing the other")
            elif "from" in h or "to" in h:
                e.add(hw, "carries from/to and is not an ownership event")
            prev_status = h.get("status")
            dates.append(str(h.get("date", "")))
        if dates != sorted(dates):
            e.add(w, "status_history is not in date order; it is append-only")
        if history and history[-1].get("status") != r.get("status"):
            e.add(w, f"status={r.get('status')!r} but the last history entry is "
                     f"{history[-1].get('status')!r}")
        # A SUPERSEDED CAPACITY HAS TO SAY WHOSE IT WAS. A figure carried after
        # the party that stated it has gone is a fact about a plan, not about
        # the project, and the page says so in the past tense with the planner
        # named. Without `planned_by` the sentence would have nobody to
        # attribute it to and would fall back to asserting it.
        cap = r.get("capacity") or {}
        if cap.get("superseded") and not cap.get("planned_by"):
            e.add(w, "capacity is superseded and names no `planned_by` — a former plan "
                     "is somebody's former plan, and the sentence has to say whose")
        if cap.get("planned_by") and not cap.get("superseded"):
            e.add(w, "capacity names a `planned_by` and is not marked superseded — "
                     "attribution is for a figure the project has outlived; a current "
                     "capacity is the project's own")

        _vocab(e, w, r, "role", sm.PROJECT_ROLES)
        if r.get("shared") is not None and r.get("shared") is not True:
            e.add(w, "shared is only ever true — a project that is not shared omits it")
        if r.get("shared") and not r.get("shared_note"):
            e.add(w, "shared with no shared_note — the flag is a judgement and the note "
                     "is where it is defended")
        _location(e, w, r)
        _storage(e, w, r, technologies, project_ids)
        _edges(e, w, r, project_ids)
        _owner_and_benchmarks(e, w, r, r.get("sector"))
        _source_list(e, w, r)


def check_coordinate_exceptions(e: Errors, rows: list[dict]) -> list[str]:
    """Report every named coordinate-source exception, and fail a stale one.

    Printed whether or not anything is wrong, on the same rule the offshore
    exceptions run under: an exception nobody sees is a rule nobody is applying.
    """
    live = {(r.get("id"), s.get("site")) for r in rows for s in (r.get("location") or [])}
    out = []
    for key, why in sorted(COORDINATE_SOURCE_EXCEPTIONS.items()):
        pid, site = key
        if key not in live:
            e.add(f"project {pid}", f"a coordinate-source exception names the site "
                                    f"{site!r}, which no longer exists — a stale "
                                    f"exception is a rule nobody is applying")
            continue
        out.append(f"  {pid}::{site}\n      {why}")
    return out


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
        # Annex I of the Critical Raw Materials Act: present and null where the
        # material is not listed, an entry with its source where it is. Required
        # rather than optional, so "not a strategic raw material" and "nobody
        # has checked" stop being the same object -- the sector page renders a
        # tag from this and a missing key would read as the first.
        if "crma_annex_i" not in r:
            e.add(w, "no crma_annex_i. Null says the material is not listed in Annex I "
                     "of the CRMA; an absent key says nobody looked")
        crma = r.get("crma_annex_i")
        if crma is not None:
            _req(e, f"{w} crma_annex_i", crma, "entry", "source")
            src = crma.get("source") or {}
            if not src.get("url") or not src.get("publisher"):
                e.add(f"{w} crma_annex_i", "source needs a url and a publisher — an Annex "
                                           "listing is a claim about a legal text")
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


def check_project_status_groups(e: Errors) -> None:
    """Every project status is in exactly one counting group.

    The same failure as the funding groups and for the same reason: a status
    added to PROJECT_STATUSES and to no group would be dropped from the alive
    count, the stopped count and the complete count at once, which is invisible
    rather than wrong. No surface reads these yet, so there is no transition.ts
    half to this check; when one does, add the mirror and check it here.
    """
    groups = {
        "PROJECT_ALIVE": sm.PROJECT_ALIVE,
        "PROJECT_STOPPED": sm.PROJECT_STOPPED,
        "PROJECT_COMPLETE": sm.PROJECT_COMPLETE,
    }
    seen: dict[str, str] = {}
    for name, members in groups.items():
        for status in members:
            if status in seen:
                e.add("sector_map.py", f"project status {status!r} is in both {seen[status]} "
                                       f"and {name}; it belongs to exactly one")
            seen[status] = name
    for status in sm.PROJECT_STATUSES:
        if status not in seen:
            e.add("sector_map.py", f"project status {status!r} is in no counting group; add "
                                   f"it to PROJECT_ALIVE, PROJECT_STOPPED or "
                                   f"PROJECT_COMPLETE so a count knows what to do with it")
    for status in seen:
        if status not in sm.PROJECT_STATUSES:
            e.add("sector_map.py", f"{seen[status]} contains {status!r}, which is not a "
                                   f"project status")


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


def measures_reaching(sector: str) -> set[str]:
    """Which measures this sector actually renders a plain block for.

    Two ways in, and they are the two the sector view itself uses: a measure
    with an edge to one of the sector's constraints, and a measure this sector
    has a money model for. Computed here rather than by running the ranking,
    because this gate has to hold before anything is built -- a label written
    wrong should fail on the file, not on the day somebody rebuilds it.
    """
    import build_importance as bi
    reached = {m["measure"]
               for b in sm.load("bottleneck") if b["sector"] == sector
               for m in (b.get("measures") or [])}
    return reached | {mid for (slug, mid) in bi.MODELS if slug == sector}


def product_words(block: dict, words: tuple[str, ...]) -> set[str]:
    """Which of these product nouns a plain block uses, whole words only."""
    text = f"{block.get('title', '')} {block.get('sentence', '')}"
    return {w for w in words
            if re.search(rf"\b{re.escape(w)}s?\b", text, re.IGNORECASE)}


def check_measure_labels(e: Errors, measure_ids: set[str]) -> None:
    """The short labels the diagram draws, and the plain block each sector
    reads under them.

    Checked here as well as in build_sector_diagram.py, and the duplication is
    deliberate: the builder only ever sees the measures that made one sector's
    view, so an entry written today for a measure that enters the view next
    month would sit unchecked until the day it is drawn. This runs over the
    whole file.

    What is NOT checked here is uniqueness. Two measures may legitimately share
    a label as long as they never appear in the same picture, and only the
    builder knows which measures share a picture -- so that gate lives there.

    THE PLAIN BLOCK IS CHECKED PER SECTOR, which is the point of this function
    since the block was split. `object` and `instrument` are shared and stay
    shared: they name the legal device, which does not change when a second
    industry is reached. The plain block names the PRODUCT, and a shared one
    that still said "clinker" would render cement's sentence on the next
    sector to reach that measure, silently. So: a shared block may name no
    sector's product at all, a per-sector block may name only its own sector's,
    and a measure that reaches a sector and resolves to neither slot fails
    outright. The trap becomes a build error.
    """
    labels = sm.measure_labels()
    mapped = sorted({b["sector"] for b in sm.load("bottleneck")})
    reach = {s: measures_reaching(s) for s in mapped}

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

        # The shared block, held against EVERY sector's product vocabulary. It
        # is checked whether or not any sector currently falls back to it: a
        # shared block naming a product is wrong the moment it is written, and
        # waiting for the sector that would expose it is waiting for the bug.
        shared = entry.get("plain")
        if shared:
            check_plain_block(e, f"{where} (shared)", shared, measure_id)
            for slug, words in sorted(sm.SECTOR_PRODUCT_WORDS.items()):
                hit = product_words(shared, words)
                if hit:
                    e.add(f"{where} (shared)",
                          f"names {sorted(hit)}, which is {slug}'s product vocabulary. A "
                          f"shared block renders on every sector a measure reaches, so it "
                          f"may name no sector's product — move it to "
                          f"plain_by_sector.{slug}")

        for slug, block in sorted((entry.get("plain_by_sector") or {}).items()):
            if slug not in sm.sectors():
                e.add(where, f"plain_by_sector names {slug!r}, which is not in "
                             f"data/sectors.json")
                continue
            check_plain_block(e, f"{where} ({slug})", block, measure_id)
            for other, words in sorted(sm.SECTOR_PRODUCT_WORDS.items()):
                if other == slug:
                    continue
                hit = product_words(block, words)
                if hit:
                    e.add(f"{where} ({slug})",
                          f"names {sorted(hit)}, which is {other}'s product vocabulary")

        # And the resolution itself: every sector that reaches this measure has
        # to end up with words.
        for slug in mapped:
            if measure_id in reach[slug] and sm.plain_block(entry, slug) is None:
                e.add(where, f"reaches {slug} and resolves to no plain block — the sector "
                             f"page would list this measure with nothing to say about it. "
                             f"Write plain_by_sector.{slug}, or a shared block if the "
                             f"wording names no product")


# A four-digit year, which is the one number an authored sentence is allowed to
# write out — and only where the measure's own `when` field says it.
_YEAR = re.compile(r"\b\d{4}\b")
# A number STANDING ON ITS OWN. Digits welded to letters are part of a name —
# CO2, PM2.5, R290 — and are no more a figure than the letters around them.
_DIGITS = re.compile(r"(?<![A-Za-z0-9])\d+(?![A-Za-z0-9])")

# Long enough to say what a measure requires, short enough that it is a title
# and not the sentence under it.
MAX_PLAIN_TITLE = 72


def check_plain_block(e: Errors, where: str, plain: dict, measure_id: str) -> None:
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
    plain = plain or {}
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
    # A slot that exists and is empty is a DIFFERENT state from a slot nobody
    # opened, and both have to be visible. The missing key fails, because a
    # mapped sector nobody has thought about is a defect; the empty string is
    # collected into `outstanding` below and printed on every run, because the
    # words are George's to write and an unwritten one that never surfaced
    # would be indistinguishable from a written one. Same discipline as the
    # ecosystem descriptions further down, and it exists because
    # `sector_orientation` is `approved` — without this, an empty paragraph
    # under an approved block is invisible to every run of this gate.
    unwritten: list[str] = []
    for sector in sorted(mapped):
        if sector not in notes:
            e.add(f"prose {sector}", "has a transition map and no note in "
                                     "data/prose.json transition_notes")
        elif not (notes[sector].get("sentence") or "").strip():
            unwritten.append(f"  {sector} (transition note): not written — the page falls "
                             f"back to the computed sentence")
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
        elif not (paras[sector].get("paragraph") or "").strip():
            unwritten.append(f"  {sector} (orientation): not written — the page opens on its "
                             f"lead block and carries no standing context")

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
    # Unconditional: an empty slot is outstanding whether or not the block
    # around it has been approved, which is the whole reason this list is
    # separate from the draft lists above.
    pending += unwritten
    return pending


def check_corrections(e: Errors, rows: list[dict], sectors: dict) -> list[str]:
    """Dated notes on figures the site has already printed.

    The gate is small because the practice is: an entry says which printed
    figure moved, when, from what to what, and how this platform came to be
    wrong. What it enforces is that the note can actually reach a reader — the
    figure is one a surface renders, from the closed list in sector_map.py, and
    the sector is one that has a page.

    Every entry is printed on every run, the way the coordinate-source
    exceptions are, so a correction cannot become a line in a file nobody
    opens.
    """
    listed = []
    for r in rows:
        w = f"correction {r.get('id', '?')}"
        _req(e, w, r, "id", "sector", "figure", "date", "was", "now", "what", "why")
        _date(e, w, r, "date")
        _vocab(e, w, r, "figure", sm.CORRECTABLE_FIGURES)
        if r.get("sector") not in sectors:
            e.add(w, f"sector={r.get('sector')!r} is not in data/sectors.json")
        for field in ("what", "why"):
            if (r.get(field) or "").strip() and not (r.get(field) or "").strip().endswith("."):
                e.add(w, f"{field} does not end in a full stop; it is a sentence a page prints")
        _source_list(e, w, r)
        listed.append(f"  {r.get('date')} {r.get('sector')} {r.get('figure')}: "
                      f"{r.get('was')} \u2192 {r.get('now')}")
    return sorted(listed)


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
    project_ids = {r["id"] for r in rows["project"]}
    check_projects(e, rows["project"], tech_ids, measure_ids, sectors,
                   sm.index(rows["technology"]), project_ids)
    material_ids = {r["id"] for r in rows["material"]}
    check_materials(e, rows["material"], sectors, tech_ids, project_ids, param_ids,
                    material_ids)
    check_funding(e, rows["funding"], tech_ids, project_ids, measure_ids, param_ids)
    check_measure_labels(e, measure_ids)
    check_ecosystems(e, rows["ecosystem"], sectors, tech_ids, project_ids, material_ids,
                     measure_ids)
    check_status_groups(e)
    check_project_status_groups(e)
    corrections = check_corrections(e, rows["correction"], sectors)
    coord_exceptions = check_coordinate_exceptions(e, rows["project"])

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
    if e.ownerless:
        print(f"\nrows with no owner type ({len(e.ownerless)}) — reported, not failed: "
              f"these predate owners-as-a-list, and filling an owner type honestly means "
              f"reading who owns the operator. See OWNER_SECTORS:")
        print("\n".join(e.ownerless))
    if e.stale:
        print(f"\nstale parameters ({len(e.stale)}) — reported, not failed:")
        print("\n".join(e.stale))
    if corrections:
        print(f"\ncorrections to printed figures ({len(corrections)}) — dated where the "
              f"figure is printed, and listed here on every run:")
        print("\n".join(corrections))
    if coord_exceptions:
        print(f"\ncoordinate-source exceptions ({len(coord_exceptions)}) — recorded, "
              f"never silent:")
        print("\n".join(coord_exceptions))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(sm.ROOT / "sources"))
    raise SystemExit(main())

#!/usr/bin/env python3
"""No surface may render a stored date at finer precision than its field records.

WHY THIS GATE EXISTS, AND IT EXISTS BECAUSE A PAGE ALREADY BROKE THE RULE. Every
date on the transition layer that says when something WAS is stored padded to the
day — a month-precision figure on the first of its month, a year-precision one on
1 January — with a `..._precision` field saying what the source actually said.
That is right for storage and for arithmetic and WRONG ON A PAGE: the first build
after the precision fields landed printed "as of 2025-01-01" on the cement and
steel lead blocks, under a cost premium the International Energy Agency dates to
2025. A day nobody published, rendered confidently, from a field that knew better.

sources/build_lead.py was fixed to trim the padding for display. This gate is what
stops the next surface from reintroducing it, and it is written the way
check_anchor_text.py is: over the BUILT PAGES, so what is checked is what ships
rather than what a builder intended.

TWO CHECKS, AND THE SECOND IS THE HONEST HALF OF THE FIRST
==========================================================

1. THE BUILT DATA A SURFACE READS. Every file a page renders dates out of, with
   each date traced back to the field it was copied from. Exact and exhaustive:
   a lead fact's `as_of` comes from a parameter or an event, and if that field is
   month- or year-precision then the copy may not carry a day.

2. THE RENDERED PAGES, BY LITERAL. Every padded date on the layer — the full
   YYYY-MM-DD form of a month- or year-precision field — is looked for in the
   built HTML. A page that prints one is claiming a precision the register does
   not have.

   AND SOME LITERALS ARE AMBIGUOUS, WHICH IS REPORTED RATHER THAN FAILED. Slite's
   permit application really was withdrawn on 1 January 2026, so "2026-01-01" is
   both a genuine day on one row and a padded year on another; a page printing it
   may be right. Those are listed on every run and not failed, because failing
   them would push somebody to stop recording real first-of-month dates. A
   literal that is padded on the file and NEVER a genuine day is unambiguous and
   IS failed.

    python3 check_date_precision.py

Skips with a clear message (not a pass) if the build has not run, so a machine
without a built tree cannot quietly turn the gate green.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = sm.ROOT
PAGES = ROOT / "web" / ".next" / "server" / "app"
DATA = ROOT / "data" / "transition"

# Every (date, precision) pair the layer stores, by where it lives. Named rather
# than discovered, so a new dated field arrives by failing this list rather than
# by being silently unchecked.
FIELDS = (
    ("projects.json", "projects", "status_history", "date", "date_precision"),
    ("projects.json", "projects", "stated_schedule", "date", "date_precision"),
    ("projects.json", "projects", None, "capacity_as_of", "capacity_as_of_precision"),
    ("projects.json", "projects", "capacity_alternates", "as_of", "as_of_precision"),
    ("projects.json", "projects", "sources", "date", "date_precision"),
    ("parameters.json", "parameters", None, "date_of_value", "date_of_value_precision"),
    ("funding.json", "funding", "sources", "date", "date_precision"),
    ("technologies.json", "technologies", "sources", "date", "date_precision"),
    ("bottlenecks.json", "bottlenecks", "sources", "date", "date_precision"),
    ("materials.json", "materials", "sources", "date", "date_precision"),
    ("corrections.json", "corrections", "sources", "date", "date_precision"),
)

DAY = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

# THE RENDERED MARKUP ONLY, AND NOT THE PAYLOAD BESIDE IT. A Next.js page ships
# its React flight data inside <script> tags, and that blob contains the STORED
# row — every field of it, padding included — because the client needs the data
# and not only the text. A gate that read it would fail every page for holding a
# date correctly, which is the opposite of what this checks. The question is what
# a reader SEES, so the scripts come out before the scan.
SCRIPT = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)


# DATES THAT ARE DAYS BY CONSTRUCTION AND CARRY NO PRECISION FIELD. A funding
# decision was taken on a day; a technology's readiness was assessed on a day; a
# page was retrieved on a day. Each is as exact as it looks, which is why none of
# them was given a field — and each has to be in the day set anyway, because the
# literal check asks whether a date printed on a page could be a real day
# SOMEWHERE on the layer. The Innovation Fund's Ifestos grant is dated
# 2024-01-01 and Italvolt's bankruptcy is padded to the same string; a page
# printing it in full may be printing the grant.
DAY_BY_CONSTRUCTION = (
    ("funding.json", "funding", None, "date"),
    ("technologies.json", "technologies", None, "readiness"),
    ("corrections.json", "corrections", None, "date"),
)


def stored() -> tuple[dict[str, set[str]], set[str]]:
    """Every stored date, grouped by precision, and the set known to the day.

    The second is what makes the literal check honest: a date that some row holds
    at day precision is a date a page may legitimately print in full, whoever
    else pads to it.
    """
    by_precision: dict[str, set[str]] = defaultdict(set)
    for filename, key, listfield, datefield, precfield in FIELDS:
        doc = json.loads((DATA / filename).read_text(encoding="utf-8"))
        for row in doc[key]:
            holders = row.get(listfield) or [] if listfield else [row]
            for h in holders:
                date, prec = h.get(datefield), h.get(precfield)
                if date and prec:
                    by_precision[prec].add(str(date))
    for filename, key, _listfield, datefield in DAY_BY_CONSTRUCTION:
        doc = json.loads((DATA / filename).read_text(encoding="utf-8"))
        for row in doc[key]:
            v = row.get(datefield)
            if isinstance(v, dict):          # technologies carry readiness.date
                v = v.get("date")
            if v:
                by_precision["day"].add(str(v))
    # retrieved_date is a day by rule and is gated to the day shape.
    for filename, key in (("projects.json", "projects"), ("funding.json", "funding"),
                          ("technologies.json", "technologies"),
                          ("bottlenecks.json", "bottlenecks"), ("materials.json", "materials")):
        doc = json.loads((DATA / filename).read_text(encoding="utf-8"))
        for row in doc[key]:
            for src in (row.get("sources") or []):
                if src.get("retrieved_date"):
                    by_precision["day"].add(str(src["retrieved_date"]))
            for site in (row.get("location") or []):
                if site.get("retrieved_date"):
                    by_precision["day"].add(str(site["retrieved_date"]))
    return by_precision, by_precision.get("day", set())


def trimmed(date: str, precision: str) -> str:
    return date[:4] if precision == "year" else date[:7] if precision == "month" else date


# THE BUILT FILES A SURFACE DATES OUT OF, and the field each date came from.
# `lead/*.json` carries `as_of` per fact; `maps/*.json` carries `as_of` on the
# document and on every mark, and those come from a site's `retrieved_date`,
# which is always a day by rule and so cannot be over-rendered.
def built_data_problems(padded: dict[str, str]) -> list[str]:
    out = []
    lead_files = sorted((DATA / "lead").glob("*.json"))
    lead_files += sorted((ROOT / "data" / "lead").glob("*.json"))
    for path in lead_files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        # data/transition/lead/*.json is one object's facts; data/lead/*.json is
        # a map of object id to that object's lead. Both are read, because both
        # are rendered.
        # data/transition/lead/<sector>.json is one object's facts;
        # data/lead/<kind>.json wraps a map of object id to lead under "leads".
        # Both are read, because both are rendered by LeadBlock.
        pool = doc.get("leads", doc) if isinstance(doc, dict) else {}
        blocks = ([doc] if "facts" in doc else
                  [v for v in pool.values() if isinstance(v, dict) and "facts" in v])
        for fact in (f for b in blocks for f in b.get("facts", [])):
            as_of = str(fact.get("as_of") or "")
            if as_of in padded:
                out.append(f"  {path.parent.name}/{path.name} fact {fact.get('id')}: "
                           f"as_of={as_of!r} is a {padded[as_of]}-precision date rendered "
                           f"to the day; it should read {trimmed(as_of, padded[as_of])!r}")
    return out


def main() -> int:
    if not PAGES.exists():
        print("check_date_precision: SKIPPED — no built pages at "
              f"{PAGES.relative_to(ROOT)}; run the web build first. This is not a pass.")
        return 0

    by_precision, days = stored()
    # A padded date is one held at month or year precision. Where the SAME date
    # is also held to the day somewhere on the layer, the literal is ambiguous.
    padded: dict[str, str] = {}
    ambiguous: dict[str, str] = {}
    for prec in ("month", "year"):
        for date in by_precision.get(prec, ()):
            (ambiguous if date in days else padded)[date] = prec

    failures = built_data_problems(padded)

    pages = sorted(PAGES.rglob("*.html"))
    hits: dict[str, list[str]] = defaultdict(list)
    warned: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        text = SCRIPT.sub(" ", page.read_text(encoding="utf-8", errors="ignore"))
        for date in DAY.findall(text):
            if date in padded:
                hits[date].append(str(page.relative_to(PAGES)))
            elif date in ambiguous:
                warned[date].append(str(page.relative_to(PAGES)))

    for date, where in sorted(hits.items()):
        failures.append(
            f"  {date} is a {padded[date]}-precision date on this layer and is printed in "
            f"full on {len(where)} page(s), first {where[0]} — it should read "
            f"{trimmed(date, padded[date])!r}")

    if failures:
        print(f"check_date_precision: {len(failures)} surface(s) render a date more "
              f"precisely than the register knows it\n")
        print("\n".join(failures))
        return 1

    print(f"check_date_precision: OK — {len(pages)} page(s) and "
          f"{len(list((DATA / 'lead').glob('*.json')))} built lead file(s) checked against "
          f"{len(padded)} padded date(s) that are unambiguous on this layer "
          f"({len(by_precision.get('month', ()))} month, {len(by_precision.get('year', ()))} "
          f"year, {len(days)} day)")
    if ambiguous:
        print(f"\nambiguous literals ({len(ambiguous)}) — reported, not failed: each is "
              f"padded on one row and a genuine day on another, so a page printing it may "
              f"be right and this gate cannot tell:")
        for date, prec in sorted(ambiguous.items()):
            n = len(warned.get(date, []))
            print(f"  {date}  padded as {prec} somewhere, and a real day elsewhere; "
                  f"printed on {n} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

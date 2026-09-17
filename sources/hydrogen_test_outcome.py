#!/usr/bin/env python3
"""THE OUTCOME PASS OVER THE 2023 POPULATION, brief 13 items 3 and 4.

    python3 sources/hydrogen_test_outcome.py --fetch [--limit N] [--offset N]
    python3 sources/hydrogen_test_outcome.py --report

WHAT IT READS FOR, AND UNDER WHICH RULE. The outcome definitions were frozen at commit
58ce11f0282a44368f4842176a4844d49aa416d2 -- scope.md, "An outcome is one of six values,
fixed on a stated day, and it is not a status" -- and D-C1 records the freeze. This pass
runs AFTER that commit and may not amend it. The six values are `operating`, `committed`,
`pending`, `delayed`, `stopped` and `unread`, the assessment date is 30 September 2026,
and the speaker is the owner, a permit authority or a regulator.

THIS IS THE LIVE-PAGE MIRROR OF hydrogen_test_2023.py. That pass asked the archive what a
reader could have held on 31 October 2023; this one asks the publishers what they say now.
Same legs, no capture preference: the entry's own references as the publisher serves them
today, the newsroom of a host the publisher cited, and -- for an entry this register holds
as a row -- the row's own sources. A URL that has stopped answering is recorded as a
refusal against that URL, which is the reading rule and not a finding about the project.

AND FOR SIXTY-ONE OF THE 255 THE REGISTER IS ALREADY THE ANSWER. Those entries are
admitted rows, and a row carries the owner's own dated statements in `status_history`
because that is what admission required. The outcome for those is read off the row FIRST
and the live pass is the check on it, not the source of it. Where this pass finds an
owner-stated event a row does not carry, the event is written to the row through the normal
path -- status_history, evidence mode, a DECISIONS entry -- because the register is the
record of what owners said, and brief 13 item 4 says so in as many words. THE OUTCOME WORD
ITSELF IS NEVER WRITTEN TO A ROW.

NOTHING HERE WRITES A VERDICT. `outcome` is null on every entry until a person reads the
pages and fills it in, on the machine-classification ruling. A six-way classification of
255 projects is precisely the shape of work that ruling exists to stop a script doing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import hydrogen_search as hs  # noqa: E402
import hydrogen_test_2023 as t23  # noqa: E402

ROOT = bench.ROOT
OUT = ROOT / "sources" / "hydrogen_test_2023_outcome.json"
ASSESSED_ON = "2026-09-30"
MAX_LEGS = 4

OUTCOMES = ("operating", "committed", "pending", "delayed", "stopped", "unread")


def legs_for(e: dict, rows_by_ref: dict, archive_doc: dict) -> list[tuple[str, str]]:
    """The URLs this entry is asked of in 2026, in the order they are read.

    THE ROW'S OWN SOURCES COME FIRST where there is a row: they are the owner's pages and
    they are why the row exists. Then the publisher's citations, then the newsroom of a
    host the publisher cited -- which is the leg most likely to carry a 2026 statement,
    because a project page is written once and a newsroom is written weekly.
    """
    out = []
    for u in t23.row_sources(e["ref"], rows_by_ref):
        out.append((u, "register_row_source_live"))
    for u in e["iea_references"]:
        if u.lower().startswith("http") and u not in [x for x, _ in out]:
            out.append((u, "iea_reference_live"))
    hosts = (archive_doc.get("hosts") or {})
    for h in e.get("host_legs") or []:
        for leg in (hosts.get(h) or {}).get("legs") or []:
            if leg["leg"] == "host_newsroom" and leg.get("reference_url"):
                u = leg["reference_url"]
                if u.lower().startswith("http") and u not in [x for x, _ in out]:
                    out.append((u, "host_newsroom_live"))
    return out[:MAX_LEGS]


def fetch_entry(e: dict, rows_by_ref: dict, archive_doc: dict) -> dict:
    got = []
    for u, leg in legs_for(e, rows_by_ref, archive_doc):
        rec = hs.fetch(u, t23.census.source_type(u),
                       f"2023 population test, IEA ref {e['ref']}: {leg}, read live for "
                       f"the outcome as of {ASSESSED_ON}")
        got.append({"leg": leg, "url": u, "read_on": rec["date"], "http": rec["http"],
                    "outcome": rec["outcome"], "sha256": rec["sha256"],
                    "text_chars": rec["text_chars"],
                    "host": urllib.parse.urlsplit(u).netloc.lower()})
    row = rows_by_ref.get(e["ref"])
    return {
        "ref": e["ref"], "name": e["name"], "country": e["country"],
        "capacity_mwel": e["capacity_mwel"],
        "status_2023_vintage": e["status_2023_vintage"],
        "date_online_2023_vintage": e["date_online_2023_vintage"],
        "row_id": (row or {}).get("id"),
        # THE ROW'S OWN ANSWER, COPIED HERE SO THE READING CAN BE CHECKED AGAINST IT. It
        # is the register's record of what the owner said, not this pass's finding.
        "row_status": (row or {}).get("status"),
        "row_status_history": [
            {k: h.get(k) for k in ("event_kind", "date", "date_precision", "status_to",
                                   "source_url", "source_type", "evidence_mode", "note",
                                   "stop_reason")}
            for h in ((row or {}).get("status_history") or [])],
        "row_stated_schedule": (row or {}).get("stated_schedule") or [],
        "fetches": got,
        "readable_2026_documents": sum(1 for g in got if g["text_chars"] >= 400),
        # EVERY ONE OF THESE IS FILLED IN BY A PERSON.
        "announced_start": None, "announced_start_precision": None,
        "announced_start_speaker": None, "announced_start_source": None,
        "announced_start_read_from": None,
        "outcome": None, "outcome_speaker": None, "outcome_source": None,
        "outcome_date": None, "outcome_date_precision": None, "outcome_note": None,
        "new_start": None, "new_start_precision": None, "slip_years": None,
        "paused": None, "resumption_date": None,
        "row_event_written": None, "verdict": None,
    }


def load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"_comment": __doc__.strip().split("\n"), "assessed_on": ASSESSED_ON,
            "frozen_at": "58ce11f0282a44368f4842176a4844d49aa416d2",
            "read_from": time.strftime("%Y-%m-%d"), "entries": []}


def save(doc):
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()

    archive_doc = json.loads(t23.OUT.read_text(encoding="utf-8")) if t23.OUT.exists() \
        else {"entries": [], "hosts": {}}
    arch_by_ref = {e["ref"]: e for e in archive_doc["entries"]}
    doc = load()
    done = {e["ref"] for e in doc["entries"]}
    pop = t23.population()

    if a.fetch:
        rows_by_ref = t23.register_rows_by_ref()
        todo = [e for e in pop if e["ref"] not in done][a.offset:a.offset + a.limit]
        print(f"outcome pass: {len(pop)} entries, {len(done)} already on file, "
              f"{len(todo)} this batch")
        for i, e in enumerate(todo, 1):
            merged = dict(e, host_legs=(arch_by_ref.get(e["ref"], {}).get("host_legs")
                                        or []))
            doc["entries"].append(fetch_entry(merged, rows_by_ref, archive_doc))
            save(doc)
            last = doc["entries"][-1]
            print(f"  {i:>3}/{len(todo)} ref {e['ref']:>5} {e['name'][:38]:40} "
                  f"{len(last['fetches'])} fetched, {last['readable_2026_documents']} "
                  f"readable{', a row' if last['row_id'] else ''}")
        return 0

    n = len(doc["entries"])
    print(f"outcome pass: {n} of {len(pop)} entries fetched, assessed as of {ASSESSED_ON}")
    print(f"  fetches: {sum(len(e['fetches']) for e in doc['entries'])}")
    print(f"  entries with a readable 2026 document: "
          f"{sum(1 for e in doc['entries'] if e['readable_2026_documents'])}")
    print(f"  entries that are register rows: "
          f"{sum(1 for e in doc['entries'] if e['row_id'])}")
    print(f"  outcomes written by a person: "
          f"{sum(1 for e in doc['entries'] if e['outcome'] is not None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

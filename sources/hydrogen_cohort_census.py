#!/usr/bin/env python3
"""THE CENSUS PASS OVER THE 2023 COHORT, brief 12 item 5.

    python3 sources/hydrogen_cohort_census.py --fetch [--limit N] [--offset N]
    python3 sources/hydrogen_cohort_census.py --report

THE COHORT is every EUROPEAN entry in the October 2023 vintage whose `Date online` is
2023 -- 73 entries. None of them is in the current 237, none is a register row, none is a
candidate, and NONE was touched by the admission search of 10 September 2026: the search
covered the class `not searched by eufabric` on the CURRENT vintage, and these are on the
old one. So the whole cohort is unsearched, and this is the pass that searches it.

THE PUBLISHER'S OWN REFERENCES ARE THE FIRST SEARCH, on the rule the CCS census set: the
IEA carries a `Refs` column into its own References sheet, so every entry arrives with
the sources its publisher stood on, and reading those first means the search starts where
the list's claim comes from rather than at a domain this register guessed. Seventy of the
seventy-three carry at least one http reference. Odenweller and Ueckerdt's own quality-check
reference is read beside it where there is one, with its reference date, its date checked
and its comment -- those are the authors' additions, MIT-licensed, cited by their number.

ARCHIVE CAPTURES DATED BEFORE OCTOBER 2023 ARE PREFERRED, which is the brief's instruction
and is what makes the cohort scorable as of 2023-10-31 at all. For every reference the
Wayback CDX index is asked for the LAST capture at or before the cut-off; where one exists
that capture is what is read, `captured_at` is derived from its timestamp and `archived` is
true. Where none exists the live page is read and the record says so -- and a live page read
in 2026 cannot date anything to 2023, which the as-of rule then handles by scoring the cell
`not_searched` rather than by pretending.

NOTHING HERE WRITES A VERDICT. Every entry carries `verdict: null` and `names_site: null`
until a person fills them in, on the ruling of 10 September 2026: a machine that proposes is
useful, a machine that files is a forgery. What the script computes is `signals` -- whether
the fetched text contains the project's own name -- and a signal is not a finding.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import warnings
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import build_hydrogen_drift as drift  # noqa: E402
import hydrogen_search as hs  # noqa: E402

ROOT = bench.ROOT
OUT = ROOT / "sources" / "hydrogen_cohort_census.json"
VINTAGE = drift.ODEN / "IEA_Hydrogen_Projects_Database_2023_quality_checked.xlsx"
OUTCOME = drift.ODEN / "IEA_Hydrogen_Projects_Database_2023_only2023_outcome.xlsx"
CUTOFF = "2023-10-31"
CDX = "https://web.archive.org/cdx/search/cdx"
MAX_REFS = 3


def sheets(path):
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    refs, qc = {}, {}
    if "References" in wb.sheetnames:
        for r in wb["References"].iter_rows(values_only=True):
            if r[0] is not None and str(r[0]).strip().isdigit():
                refs[str(r[0]).strip()] = str(r[1] or "").strip()
    if "References (quality check)" in wb.sheetnames:
        for r in wb["References (quality check)"].iter_rows(values_only=True):
            if r[0] is not None and str(r[0]).strip().isdigit():
                qc[str(r[0]).strip()] = {
                    "url": str(r[1] or "").strip(),
                    "reference_date": str(r[2] or "")[:10],
                    "date_checked": str(r[3] or "")[:10],
                    "comment": str(r[4] or "").strip()}
    wb.close()
    return refs, qc


def cohort():
    """The 73, with everything the vintage says about each."""
    refs, qc = sheets(VINTAGE)
    out = []
    for r in drift.load_workbook_projects(VINTAGE):
        if r["Country"] not in bench.GEO:
            continue
        if str(r["Date online"]).strip() != "2023":
            continue
        ids = re.findall(r"\[(\d+)\]", str(r["Refs"] or ""))
        qids = re.findall(r"\[(\d+)\]", str(r["Refs (quality check)"] or ""))
        out.append({
            "ref": r["Ref"], "name": str(r["Project name"] or ""),
            "country": r["Country"],
            "status_2023_vintage": str(r["Status"] or ""),
            "technology": str(r["Technology"] or ""),
            "announced_size": str(r["Announced Size"] or ""),
            "capacity_mwel": drift._f(r["Capacity_MWel"]),
            "capacity_kth2y": drift._f(r["Capacity_ktH2Y"]),
            "iea_reference_numbers": ids,
            "iea_references": [refs.get(i, "") for i in ids],
            "quality_check_reference_numbers": qids,
            "quality_check_references": [dict(qc.get(i, {}), number=i) for i in qids],
        })
    return out


def wayback_before(url: str, cutoff: str = CUTOFF):
    """The LAST capture at or before the cut-off, or None. One request, recorded."""
    q = urllib.parse.urlencode({
        "url": url, "output": "json", "fl": "timestamp,original",
        "filter": "statuscode:200", "to": cutoff.replace("-", "") + "235959",
        "limit": "-1"})
    try:
        req = urllib.request.Request(CDX + "?" + q, headers={"User-Agent": hs.UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            rows = json.loads(r.read().decode("utf-8", "replace") or "[]")
    except Exception:                                          # noqa: BLE001
        return None
    rows = [x for x in rows if x and x[0] != "timestamp"]
    if not rows:
        return None
    ts = rows[-1][0]
    return {"timestamp": ts,
            "captured_at": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}",
            "url": f"https://web.archive.org/web/{ts}/{rows[-1][1]}"}


def source_type(url: str) -> str:
    """A COARSE LABEL AND NOT A VERDICT. Whether a page is an owner or a permit source is
    read by a person from the page; this only says what kind of host it is, so the record
    can be sorted."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    if any(k in host for k in (".gov", "gouv.", ".gob.", "bund.de", "europa.eu",
                               "overheid", "regjeringen", "ens.dk", "rvo.nl")):
        return "permit_or_official"
    return "unclassified"


def fetch_entry(e: dict) -> dict:
    urls = [u for u in e["iea_references"] if u.lower().startswith("http")][:MAX_REFS]
    for q in e["quality_check_references"]:
        if q.get("url", "").lower().startswith("http") and q["url"] not in urls:
            urls.append(q["url"])
    got = []
    for u in urls:
        cap = wayback_before(u)
        target, archived, captured_at = u, False, ""
        if cap:
            target, archived, captured_at = cap["url"], True, cap["captured_at"]
        rec = hs.fetch(target, source_type(u),
                       f"2023 cohort census, IEA ref {e['ref']}: "
                       + ("Wayback capture at or before " + CUTOFF
                          if archived else "no capture at or before " + CUTOFF
                          + "; the live page was read"))
        txt = hs.body_text(rec["sha256"]) if rec["sha256"] else ""
        stem = re.sub(r"[^a-z0-9 ]", " ", e["name"].lower()).split()
        stem = [w for w in stem if len(w) > 4][:3]
        got.append({
            "reference_url": u, "read_url": target, "archived": archived,
            "captured_at": captured_at, "http": rec["http"], "outcome": rec["outcome"],
            "sha256": rec["sha256"], "text_chars": rec["text_chars"],
            "source_type": rec["source_type"],
            "signals": {"contains_a_name_word": bool(stem) and all(
                w in txt.lower() for w in stem)},
        })
    return {**e, "fetches": got,
            "readable_at_or_before_cutoff": any(
                g["archived"] and g["text_chars"] >= 400 for g in got),
            "names_site": None, "site_named": None, "site_speaker": None,
            "verdict": None}


def load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"_comment": __doc__.strip().split("\n"), "cutoff": CUTOFF, "entries": []}


def save(doc):
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--offset", type=int, default=0)
    a = ap.parse_args()

    doc = load()
    done = {e["ref"] for e in doc["entries"]}
    all_ = cohort()
    if a.fetch:
        todo = [e for e in all_ if e["ref"] not in done][a.offset:a.offset + a.limit]
        print(f"cohort census: {len(all_)} entries, {len(done)} already on file, "
              f"{len(todo)} this batch")
        for i, e in enumerate(todo, 1):
            doc["entries"].append(fetch_entry(e))
            save(doc)
            last = doc["entries"][-1]
            ok = sum(1 for g in last["fetches"] if g["text_chars"] >= 400)
            arch = sum(1 for g in last["fetches"] if g["archived"])
            print(f"  {i:>3}/{len(todo)} ref {e['ref']:>5} {e['name'][:40]:42} "
                  f"{len(last['fetches'])} fetched, {ok} readable, {arch} from a capture "
                  f"at or before {CUTOFF}")
        return 0

    n = len(doc["entries"])
    arch = sum(1 for e in doc["entries"] if e["readable_at_or_before_cutoff"])
    print(f"cohort census: {n} of {len(all_)} entries searched; {arch} have at least one "
          f"readable capture dated on or before {CUTOFF}.")
    print(f"  fetches: {sum(len(e['fetches']) for e in doc['entries'])}")
    print(f"  verdicts written by a person: "
          f"{sum(1 for e in doc['entries'] if e['verdict'] is not None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

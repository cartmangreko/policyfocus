#!/usr/bin/env python3
"""Fetch the IEA's OWN references for a set of CCUS entries, through the reader.

    python3 sources/ccs_census_fetch.py 1462 1138 658 ...      # by IEA ID
    python3 sources/ccs_census_fetch.py --subsector Cement --unheld
    python3 sources/ccs_census_fetch.py --max-refs 2 1462 1138

WHY THE PUBLISHER'S OWN LINKS ARE THE FIRST SEARCH. The IEA carries Ref 1..7 per
entry -- "Data collection and processing by the IEA. All public references are
available by project" -- so every entry arrives with the sources its publisher
stood on. Reading those first means the search starts where the list's own claim
comes from rather than at a domain this register guessed, which is the mistake
D42 was written about.

IT IS A FIRST SEARCH AND NOT THE WHOLE ONE. An IEA reference is frequently trade
press, and trade press is not an owner or permit source. What these fetches
settle is whether the entry has a readable company or permit source AT ALL and
where it is; the class an entry ends in is decided on what those say.

Every fetch lands in sources/cache/ccs/index.json with url, date, size and hash,
through sources/ccs_search.py. Nothing here decides a class.
"""
from __future__ import annotations
import argparse, json, os, pathlib, sys
import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ccs_search as cs  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOK = ROOT / "sources" / "cache" / "ccs" / "iea_ccus_projects_2026.xlsx"
SHEET = "DRAFT CCUS Projects Database"

# The eight cement and three CCS rows this register already holds, against the
# IEA entries they match. Company AND works agree on every one; each is printed
# on every run for confirmation, never treated as settled by this file.
HELD = {
    201: "brevik-ccs", 1012: "gezero-geseke", 560: "anrav-devnya",
    557: "go4zero-obourg", 207: "carbon2business-lagerdorf", 79: "slite-ccs",
    1141: "ifestos-kamari", 236: "k6-lumbres",
    295: "northern-lights", 296: "northern-lights",
    688: "prinos-co2-storage", 689: "prinos-co2-storage",
}


def entries() -> list[dict]:
    wb = openpyxl.load_workbook(BOOK, read_only=True, data_only=True)
    ws = wb[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    hdr = list(rows[0])
    return [dict(zip(hdr, r)) for r in rows[1:] if r[1] is not None]


def european() -> list[dict]:
    return [d for d in entries() if d["Region"] == "Europe"]


def refs(d: dict) -> list[str]:
    out = []
    for i in range(1, 8):
        v = d.get(f"Ref {i}")
        if v and str(v).strip().lower().startswith("http"):
            out.append(str(v).strip())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", type=int)
    ap.add_argument("--subsector")
    ap.add_argument("--sector")
    ap.add_argument("--unheld", action="store_true")
    ap.add_argument("--max-refs", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    eu = european()
    sel = eu
    if a.ids:
        want = set(a.ids)
        sel = [d for d in eu if d["ID"] in want]
    if a.subsector:
        sel = [d for d in sel if d["Subsector"] == a.subsector]
    if a.sector:
        sel = [d for d in sel if d["Sector"] == a.sector]
    if a.unheld:
        sel = [d for d in sel if d["ID"] not in HELD]

    done = set()
    idx = json.loads((ROOT / "sources/cache/ccs/index.json").read_text())
    for f in idx["fetches"]:
        done.add(f["url"])

    plan = []
    for d in sel:
        for u in refs(d)[: a.max_refs]:
            if u not in done:
                plan.append((d, u))
                done.add(u)

    print(f"{len(sel)} entries, {len(plan)} fetches not already in the index")
    if a.dry_run:
        for d, u in plan:
            print(f"  {d['ID']:>5} {d['Project name'][:34]:<34} {u[:90]}")
        return 0

    for n, (d, u) in enumerate(plan, 1):
        r = cs.fetch(u, "iea reference",
                     f"cement/CCS census: IEA {d['ID']} {d['Project name']}")
        print(f"[{n}/{len(plan)}] {d['ID']:>5} {r['outcome']:<22} {u[:88]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

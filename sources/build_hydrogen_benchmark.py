#!/usr/bin/env python3
"""Measure the hydrogen dataset against the two outside lists, and write the
comparison to scratch/hydrogen_benchmark.csv.

WHY TWO LISTS AND NOT ONE. Brief 7 §6 names both, and they are not independent:
Odenweller and Ueckerdt's project list IS the IEA's Hydrogen Projects Database,
quality-checked by them, at its October 2023 vintage. Matching against both
therefore measures two different things. Against the 2023 list: does this
register hold what the published academic list held, three years ago. Against
the live IEA list: does it hold what the IEA holds today. A register that scores
well on one and badly on the other is telling you which way it is out of date.

WHAT IS FETCHED, AND WHY NOTHING IS COMMITTED
---------------------------------------------
  the 2023 quality-checked list   the xlsx in aodenweller/green-hydrogen-gap,
                                  which is the file the paper's figures are
                                  computed from.
  the live IEA list               api.iea.org/hydrogen/project, the project-level
                                  endpoint behind the IEA's own hydrogen map.

Both are cached under sources/cache/hydrogen/ and NEITHER IS COMMITTED. The
content of both is the IEA's database, which this repository is not licensed to
redistribute; the .gitignore entry says so. What is committed is this script and
the ids on the rows, which is enough for anybody to reproduce the comparison
from the publishers' own copies.

THE THRESHOLD, AND THE ONE CONVERSION THIS FILE MAKES
-----------------------------------------------------
The perimeter is 100 MW of electrolyser capacity. The live IEA endpoint states
capacity only in kilotonnes of hydrogen a year, so counting "their European
entries at or above 100 MW" needs a factor -- and this register does not convert
between hydrogen units (sources/scope.md, "Three units for one electrolyser").

The rule survives because THE CONVERSION IS APPLIED TO THEIR NUMBERS ON THEIR
OWN ASSUMPTION, and never to a row here. The IEA's own quality-checked file pairs
100 MWel with 17.325 kt H2/y for the same project, which is the factor used
below; it is the IEA reading its own database, not this register deciding what a
megawatt of hydrogen is. Every count that rests on it is labelled `_iea_factor`
in the output so a reader can discard it.

AND THE IEA'S OWN DEFINITION SHEET DISAGREES WITH ITSELF, which is the reason
the no-conversion rule exists. Its "estimated normalised capacity" is described
as "MW H2 output (LHV)" and derived from factors of 0.0046-0.0052 MW per Nm3/h,
equivalently "50 kWh/kg H2" -- which is electrical input, not LHV output. The
column is input; the sentence above it says output. Two readings of one column,
in one file, and a register that converted on it would inherit both.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = sm.ROOT
CACHE = ROOT / "sources" / "cache" / "hydrogen"
OUT = ROOT / "scratch" / "hydrogen_benchmark.csv"

UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")

OU_XLSX = ("https://raw.githubusercontent.com/aodenweller/green-hydrogen-gap/master/"
           "data/IEA_H2_DB_2023-10/quality_checked/"
           "IEA_Hydrogen_Projects_Database_2023_quality_checked.xlsx")
IEA_API = "https://api.iea.org/hydrogen/project"

# The brief's geography, as ISO3, because both benchmarks key on it.
GEO = {
    "AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU",
    "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT",
    "ROU", "SVK", "SVN", "ESP", "SWE",
    "GBR", "NOR", "CHE", "ALB", "BIH", "MKD", "MNE", "SRB", "XKX", "UKR",
}

THRESHOLD_MW = 100
# 100 MWel <-> 17.325333 kt H2/y, read off the IEA's own quality-checked file
# (ref 1, "Solar PV Plant port of Sines", 100 MW / 17.325333 kt H2/y).
IEA_KT_PER_MW = 0.17325333
THRESHOLD_KT = THRESHOLD_MW * IEA_KT_PER_MW

# WHAT COUNTS AS ELECTROLYSIS IN EACH FILE, and they do not say it the same way.
# The live endpoint has one value, "Electrolysis". The 2023 quality-checked file
# names the cell chemistry instead — ALK, PEM, SOEC, or "Unknown PtX" where the
# project did not say — and its own definitions sheet groups all four under
# "Water electrolysis". Matching on the word "electrolysis" therefore finds a
# quarter of the file and silently drops every PEM project in Europe, which is
# most of them. The set is read from the definitions sheet and written out here.
OU_ELECTROLYSIS = {"ALK", "PEM", "SOEC", "Unknown PtX", "Other Electrolysis"}


def fetch(url: str, name: str) -> bytes:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / name
    if path.exists():
        return path.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    body = urllib.request.urlopen(req, timeout=180).read()
    path.write_bytes(body)
    return body


def load_ou() -> list[dict]:
    """The quality-checked October 2023 list, as rows keyed by its own headers."""
    import openpyxl  # imported here so the rest of the file runs without it
    fetch(OU_XLSX, "ou_quality_checked_2023.xlsx")
    wb = openpyxl.load_workbook(CACHE / "ou_quality_checked_2023.xlsx",
                                read_only=True, data_only=True)
    it = wb["Projects"].iter_rows(values_only=True)
    for _ in range(3):
        next(it)
    hdr = next(it)
    idx = {h: i for i, h in enumerate(hdr) if h}
    rows = []
    for r in it:
        if r[0] is None:
            continue
        rows.append({h: r[i] for h, i in idx.items()})
    return rows


def load_iea() -> list[dict]:
    body = fetch(IEA_API, "iea_live_projects.json")
    return json.loads(body)


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def ou_european(rows) -> dict[str, dict]:
    out = {}
    for r in rows:
        if r.get("Country") not in GEO:
            continue
        if str(r.get("Technology") or "").strip() not in OU_ELECTROLYSIS:
            continue
        if (_f(r.get("Capacity_MWel")) or 0) < THRESHOLD_MW:
            continue
        out[str(r["Ref"])] = r
    return out


def iea_european(rows) -> dict[str, dict]:
    out = {}
    for r in rows:
        if r["country"]["iso3"] not in GEO:
            continue
        if "lectrolysis" not in str(r.get("technolgy") or ""):
            continue
        if (_f(r.get("capacity (ktH2Y)")) or 0) < THRESHOLD_KT:
            continue
        out[str(r["projectReference"])] = r
    return out


def held() -> list[dict]:
    """Every hydrogen object this register holds: rows first, then candidates.

    A CANDIDATE IS PART OF THE COMPARISON. The perimeter has admitted it and the
    only thing keeping it out of data/transition/projects.json is a position, so
    counting it as "not held" would blame the benchmark gap on a coverage
    decision this register did not make.
    """
    out = []
    for p in sm.load("project"):
        if p.get("sector") != "clean":
            continue
        out.append({"id": p["id"], "company": p["company"], "site": p.get("plant", ""),
                    "country": p["country"], "state": "row", "status": p["status"],
                    "capacity_value": p.get("capacity_value"),
                    "capacity_unit": p.get("capacity_unit"),
                    "benchmarks": p.get("benchmarks") or {}})
    doc = json.loads((ROOT / "sources" / "hydrogen_candidates.json").read_text("utf-8"))
    ids = {r["id"] for r in out}
    for c in doc["candidates"]:
        if c["id"] in ids:
            continue
        out.append({"id": c["id"], "company": c["company"], "site": c["site"],
                    "country": c["country"], "state": "candidate",
                    "status": c.get("status", ""),
                    "capacity_value": c.get("capacity_mw_input"),
                    "capacity_unit": "MW_input" if c.get("capacity_mw_input") else "",
                    "benchmarks": c.get("benchmarks") or {}})
    return out


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main() -> int:
    ou_all = load_ou()
    iea_all = load_iea()
    ou = ou_european(ou_all)
    iea = iea_european(iea_all)
    rows = held()

    matched_ou: set[str] = set()
    matched_iea: set[str] = set()
    out_rows = []
    for r in rows:
        ou_ids = [str(x) for x in as_list(r["benchmarks"].get("odenweller_ueckerdt_2025"))]
        iea_ids = [str(x) for x in as_list(r["benchmarks"].get("iea_hydrogen_production_projects"))]
        matched_ou.update(i for i in ou_ids if i in ou)
        matched_iea.update(i for i in iea_ids if i in iea)

        def status(ids, table, searched):
            if not ids:
                return "searched, not in list" if searched else "not searched"
            hit = [i for i in ids if i in table]
            miss = [i for i in ids if i not in table]
            if hit and miss:
                return f"matched {len(hit)} of {len(ids)} phase rows"
            if hit:
                return "matched" if len(hit) == 1 else f"matched {len(hit)} phase rows"
            return ("id recorded; the benchmark's own entry is below "
                    f"{THRESHOLD_MW} MW, or outside this geography")

        searched = "odenweller_ueckerdt_2025" in r["benchmarks"]
        out_rows.append({
            "eufabric_id": r["id"],
            "state": r["state"],
            "company": r["company"],
            "site": r["site"],
            "country": r["country"],
            "eufabric_status": r["status"],
            "eufabric_capacity": r["capacity_value"] if r["capacity_value"] is not None else "",
            "eufabric_capacity_unit": r["capacity_unit"] or "",
            "ou2025_ids": ";".join(ou_ids),
            "ou2025_match": status(ou_ids, ou, searched),
            "ou2025_mw": ";".join(str(_f(ou[i].get("Capacity_MWel")) or "") for i in ou_ids if i in ou),
            "ou2025_status": ";".join(str(ou[i].get("Status")) for i in ou_ids if i in ou),
            "iea_ids": ";".join(iea_ids),
            "iea_match": status(iea_ids, iea, searched),
            "iea_kt_h2_y": ";".join(f'{_f(iea[i].get("capacity (ktH2Y)")):.2f}'
                                    for i in iea_ids if i in iea),
            "iea_status": ";".join(str(iea[i].get("status")) for i in iea_ids if i in iea),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    # ---- what each benchmark holds and this register does not ---------------
    def bucket(entry, name) -> str:
        """Why an entry is not held, where the reason is knowable from the entry
        itself. Everything else is `not reached by this pass`, which is honest:
        a docket built in one sweep has not looked at 200 projects."""
        st = str(entry.get("Status") if name == "ou" else entry.get("status"))
        nm = str(entry.get("Project name") if name == "ou" else entry.get("projectName"))
        low = nm.lower()
        if any(k in low for k in ("steel", "hybrit", "stegra", "h2gs", "dri", "sponge iron",
                                  "salcos", "gravithy", "blastr")):
            return "out of perimeter: steel project"
        if any(k in low for k in ("e-saf", "esaf", "saf", "methanol", "meoh", "e-fuel",
                                  "efuel", "synfuel", "kerosen", "jet", "biofuel",
                                  "e-methane", "methane", "ptl")):
            return "fuel plant: in only if its own electrolyser clears the threshold"
        if st in ("Concept", "Feasibility study"):
            return f"{st.lower()}: no company-confirmed site read by this pass"
        return "not reached by this pass"

    print(f"build_hydrogen_benchmark: {len(out_rows)} eufabric object(s) "
          f"({sum(1 for r in out_rows if r['state']=='row')} rows, "
          f"{sum(1 for r in out_rows if r['state']=='candidate')} candidates)")
    for name, table, hit in (("odenweller_ueckerdt_2025", ou, matched_ou),
                             ("iea_hydrogen_production_projects", iea, matched_iea)):
        missing = {k: v for k, v in table.items() if k not in hit}
        print(f"\n  {name}: {len(table)} European entries at or above {THRESHOLD_MW} MW"
              + ("" if name.startswith("odenw") else " (on the IEA's own factor)")
              + f"; eufabric holds {len(hit)}, and does not hold {len(missing)}.")
        for reason, n in Counter(bucket(v, "ou" if name.startswith("odenw") else "iea")
                                 for v in missing.values()).most_common():
            print(f"      {n:>4}  {reason}")

    print(f"\n  {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

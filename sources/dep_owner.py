"""The other direction: every admitted row, re-read for supplier and store names.

    python3 dep_owner.py --fetch      # cache every source url the register cites
    python3 dep_owner.py --scan       # report which of them name a perimeter node

THE POINT IS THE EMPTY RESULT. A row whose sources were read and named no supplier
gets an empty list; a row nobody read is absent from the file entirely. Those are
different facts and the brief asks for both, so the scan records `sources_read`
even when it finds nothing — a zero beside a count of five is a search, a row that
is simply missing is not.

WHAT IS NOT SEARCHED, and why. OpenStreetMap urls are skipped: they are the
coordinate provenance, they are 51 of the 235 urls the register cites, and a
basemap relation does not name a supplier. Everything else is fetched, including
the Wayback captures the register already cites — the register reached the same
conclusion about dead company domains that DECISION D-7 reaches.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import dep_sweep as S
import dep_text as T

HERE = Path(__file__).resolve().parent
PROJECTS = HERE.parent / "data" / "transition" / "projects.json"
SKIP = re.compile(
    r"openstreetmap\.org|/relation/|/way/|/node/"       # coordinate provenance
    r"|api\.iea\.org|odenweller|zenodo\.org", re.I)   # benchmark lists

# WHY THE BENCHMARK LISTS ARE SKIPPED, AND IT IS NOT SQUEAMISHNESS. The IEA
# Hydrogen Projects Database at api.iea.org/hydrogen/project is one JSON blob
# listing every hydrogen project in the world, and twenty-two rows cite it as their
# benchmark source. Scanning it for supplier names matched SIX nodes on every one of
# those rows — Air Liquide, Linde, Northern Lights, Plug Power, Porthos and Siemens
# Energy — because all six appear somewhere in a global database. That is not the
# owner of a plant naming its supplier; it is a haystack matching every needle.

# What a node looks like when an OWNER writes it down. Deliberately generous on
# spelling and deliberately anchored: "Nel" unanchored matches "channel", "panel"
# and "Nelson", which is how a supplier gets credited with a plant nobody sold it.
NAMES: dict[str, str] = {
    "nel": r"\bNel Hydrogen\b|\bNel ASA\b|\bNel\b(?=[ ,.]|'s)",
    "itm-power": r"\bITM Power\b|\bITM Linde\b",
    "tk-nucera": r"thyssenkrupp nucera|thyssenkrupp Uhde Chlorine",
    "siemens-energy": r"\bSiemens Energy\b",
    "sunfire": r"\bSunfire\b",
    "plug-power": r"\bPlug Power\b|\bPlug\b(?= Power|,)",
    "john-cockerill": r"John Cockerill",
    "mcphy": r"\bMcPhy\b",
    "slb-capturi": r"SLB Capturi|Aker Carbon Capture",
    "mhi": r"Mitsubishi Heavy Industries|\bMHI\b|\bMHIENG\b",
    "shell-cansolv": r"\bCansolv\b",
    "linde": r"\bLinde\b",
    "air-liquide": r"Air Liquide",
    "midrex": r"\bMidrex\b|MIDREX",
    "primetals": r"\bPrimetals\b",
    "tenova": r"\bTenova\b|ENERGIRON|Energiron",
    "danieli": r"\bDanieli\b",
    "sms-group": r"\bSMS group\b|\bSMS Group\b|Paul Wurth",
    "wuxi-lead": r"Wuxi Lead|Lead Intelligent",
    "manz": r"\bManz\b",
    "hitachi": r"\bHitachi\b",
    "northern-lights": r"Northern Lights",
    "porthos": r"\bPorthos\b",
    "aramis": r"\bAramis\b",
    "greensand": r"Greensand",
    "ravenna-ccs": r"Ravenna CCS",
    "endurance-nep": r"Northern Endurance|\bEndurance\b(?= store| reservoir| partnership)|"
                     r"Net Zero Teesside",
}
COMPILED = {k: re.compile(v) for k, v in NAMES.items()}


def source_urls(obj) -> set[str]:
    out: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if (k in ("url", "source_url", "capacity_source_url", "company_source")
                    and isinstance(v, str) and v.startswith("http")):
                out.add(v)
            else:
                out |= source_urls(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= source_urls(v)
    return out


def rows() -> list[dict]:
    return json.loads(PROJECTS.read_text())["projects"]


def per_row() -> dict[str, list[str]]:
    return {p["id"]: sorted(u for u in source_urls(p) if not SKIP.search(u))
            for p in rows()}


def scan() -> dict:
    """{project id: what its own cited sources say about the perimeter}."""
    mapping = per_row()
    by_id = {p["id"]: p for p in rows()}
    idx = T.index()
    ok = {e["url"] for e in idx.values() if e.get("sha256")}
    out = {}
    for pid, urls in sorted(mapping.items()):
        read, found, unread = 0, set(), []
        for u in urls:
            if u not in ok:
                unread.append(u)
                continue
            read += 1
            text = "\n".join(l for l in T.text(u).splitlines() if len(l) >= 180)
            for node, pat in COMPILED.items():
                if pat.search(text):
                    found.add(node)
        owner = " ".join(str(by_id[pid].get(k, "")) for k in ("company", "name"))
        out[pid] = {"cited": len(urls), "read": read, "unreadable": unread,
                    "named": sorted(found),
                    "names_its_own_owner": sorted(
                        n for n in found if COMPILED[n].search(owner))}
    return out


def main(argv: list[str]) -> int:
    mapping = per_row()
    if "--fetch" in argv:
        urls = sorted({u for v in mapping.values() for u in v})
        lst = HERE / "dependency_cache/.owner-urls.txt"
        lst.write_text("\n".join(urls))
        print(f"{len(urls)} urls", file=sys.stderr)
        subprocess.run([sys.executable, "dep_fetch.py", "--file", str(lst), "--jobs", "3"],
                       cwd=HERE)
        return 0

    by_id = {p["id"]: p for p in rows()}
    idx = T.index()
    ok = {e["url"] for e in idx.values() if e.get("sha256")}
    out = {}
    for pid, urls in sorted(mapping.items()):
        read, found, unread = 0, set(), []
        for u in urls:
            if u not in ok:
                unread.append(u)
                continue
            read += 1
            # PARAGRAPHS ONLY, for the same reason dep_digest reads them: a page's
            # navigation, its related-articles rail and its footer name companies
            # the article never mentions.
            text = "\n".join(l for l in T.text(u).splitlines() if len(l) >= 180)
            for node, pat in COMPILED.items():
                if pat.search(text):
                    found.add(node)
        # A row whose OWNER is itself a node on the perimeter names that node in
        # every source it has, trivially. Air Liquide's own electrolyser rows name
        # Air Liquide; the Northern Lights row names Northern Lights. Flagged rather
        # than filtered, because "the owner is the supplier" is a real finding about
        # the market and not noise to be removed.
        owner = " ".join(str(v) for k, v in by_id[pid].items()
                         if k in ("company", "name")) if pid in by_id else ""
        selfnamed = sorted(n for n in found if COMPILED[n].search(owner))
        out[pid] = {"cited": len(urls), "read": read, "unreadable": unread,
                    "named": sorted(found), "names_its_own_owner": selfnamed}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

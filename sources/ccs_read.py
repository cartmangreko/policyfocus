#!/usr/bin/env python3
"""Print what the cached pages say about one CCUS entry, for a reader.

    python3 sources/ccs_read.py 1462 1138 658

A selector finds candidate sentences; a person decides what they say. Nothing
here assigns a class, and nothing here is imported by the census build — see the
note in sources/dep_text.py about why the gate chain does not depend on a PDF
engine. pypdf is used HERE, in the reading tool, and nowhere in the gates.
"""
from __future__ import annotations
import io, json, os, pathlib, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ccs_census_fetch as cf  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources" / "cache" / "ccs"

KEYS = ("captur", "CO2", "CO₂", "abscheid", "capture", "kt ", "Mt", "million tonnes",
        "tonnes", "tonnage", "storage", "stock", "cement", "zement", "ciment",
        "cimente", "kiln", "plant", "works", "usine", "werk", "planta",
        "operational", "commission", "2027", "2028", "2029", "2030", "2031",
        "2032", "2033", "investment decision", "FID", "construction")


def text_for(sha: str) -> str:
    p = CACHE / sha
    if not p.exists():
        return ""
    b = p.read_bytes()
    if b[:4] == b"%PDF":
        try:
            import pypdf
            r = pypdf.PdfReader(io.BytesIO(b))
            return re.sub(r"\s+", " ", " ".join((pg.extract_text() or "")
                                                for pg in r.pages))
        except Exception as e:                                  # noqa: BLE001
            return f"[pdf unreadable: {type(e).__name__}]"
    import ccs_search as cs
    return cs.text_of(b, "")


def sentences(t: str, want: int = 6) -> list[str]:
    out, seen = [], set()
    for s in re.split(r"(?<=[.!?])\s+|\s{3,}|\|", t):
        s = s.strip()
        if not (60 <= len(s) <= 340):
            continue
        score = sum(1 for k in KEYS if k.lower() in s.lower())
        if score >= 2 and s not in seen:
            seen.add(s)
            out.append((score, s))
    out.sort(key=lambda x: -x[0])
    return [s for _, s in out[:want]]


def main() -> int:
    ids = [int(x) for x in sys.argv[1:]]
    idx = json.loads((CACHE / "index.json").read_text())
    by_url = {f["url"]: f for f in idx["fetches"]}
    eu = {d["ID"]: d for d in cf.european()}
    for i in ids:
        d = eu[i]
        print("=" * 96)
        print(f"IEA {i} | {d['Project name']} | {d['Country or economy']} | "
              f"{d['Project type']} | {d['Subsector']} | {d['Project status']}")
        print(f"   partners: {d['Partners']}")
        print(f"   announced={d['Announced capacity (Mt CO2/yr)']}  "
              f"iea_estimate={d['Estimated capacity by IEA (Mt CO2/yr)']}  "
              f"phase={d['Project phase']}  announced_yr={d['Announcement']}  "
              f"FID={d['FID']}  operation={d['Operation']}")
        for u in cf.refs(d):
            f = by_url.get(u)
            if not f:
                print(f"   -- not fetched: {u}")
                continue
            print(f"   -- {f['outcome']:<20} {u}")
            if not f["sha256"]:
                continue
            for s in sentences(text_for(f["sha256"])):
                print(f"        {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

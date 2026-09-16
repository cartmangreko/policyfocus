#!/usr/bin/env python3
"""Print what the cached owner documents say about one steel plant, for a reader.

    python3 sources/steel_read.py P100000123456 [...]
    python3 sources/steel_read.py --forward      # the plants GEM shows something at
    python3 sources/steel_read.py --quiet        # the plants GEM shows nothing at

A selector finds candidate sentences; a person decides what they say. Nothing
here assigns a class.

WHAT IT LOOKS FOR, AND WHY THESE WORDS. The steel perimeter turns on what an
investment does to the IRON: an announced DRI plant, an EAF replacing
blast-furnace capacity at an existing works, greenfield DRI/EAF primary
steelmaking, a hydrogen-ready furnace. So the terms are the route words in the
languages these owners publish in — direct reduction, Direktreduktion, réduction
directe, reducción directa — and the words that distinguish a replacement from an
addition.

gem.wiki IS EXCLUDED FROM WHAT THIS PRINTS. It is where the search started and it
is never a source, so a sentence from it must not reach a reader deciding a
class.
"""
from __future__ import annotations
import io, json, os, pathlib, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steel_search as ss  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources" / "cache" / "steel"
ENTRIES = ROOT / "sources" / "steel_entries.json"

ROUTE = re.compile(
    r"direct[- ]reduc|direktreduktion|réduction directe|reducci[oó]n directa|"
    r"riduzione diretta|\bDRI\b|\bHBI\b|\bDRP\b|shaft furnace|"
    r"electric arc furnace|elektrolichtbogenofen|four à arc|horno de arco|"
    r"forno elettrico|\bEAF\b|\bEOF\b|"
    r"hydrogen[- ]ready|wasserstofffähig|wasserstoffbereit|h2[- ]ready|"
    r"hydrogen|wasserstoff|hydrog[eè]ne|hidrógeno|idrogeno|"
    r"blast furnace|hochofen|haut fourneau|alto horno|altoforno|"
    r"decarbonis|dekarbonis|décarbon|descarboniz|decarboniz|"
    r"replace|ersetz|remplace|sustituir|sostituire|"
    r"green steel|grüner stahl|acier vert|acero verde|"
    r"scrap|schrott|ferraille|chatarra|rottame", re.I)

STRONG = ("direct reduc", "direktreduktion", "réduction directe", "reducción directa",
          "dri plant", "dri module", "hydrogen-ready", "wasserstofffähig",
          "h2-ready", "replace the blast furnace", "replacing the blast furnace",
          "ersetzt den hochofen", "electric arc furnace", "elektrolichtbogenofen")


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
    return ss.text_of(b, "")


def sentences(t: str, want: int = 5) -> list[str]:
    out, seen = [], set()
    for s in re.split(r"(?<=[.!?])\s+|\s{3,}|\|", t):
        s = s.strip()
        if not (55 <= len(s) <= 330):
            continue
        if not ROUTE.search(s):
            continue
        score = len(ROUTE.findall(s)) + 3 * sum(1 for w in STRONG if w in s.lower())
        if s not in seen:
            seen.add(s)
            out.append((score, s))
    out.sort(key=lambda x: -x[0])
    return [s for _, s in out[:want]]


def main() -> int:
    ents = json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]
    idx = json.loads((CACHE / "index.json").read_text(encoding="utf-8"))
    by_plant: dict[str, list[dict]] = {}
    for f in idx["fetches"]:
        n = f.get("note", "")
        if n.startswith("steel census: ") and f.get("source_type") == "owner or permit":
            by_plant.setdefault(n.split()[2], []).append(f)

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--forward" in sys.argv:
        args = [k for k in ents if ents[k]["gem_claim"]["forward_units"]]
    elif "--quiet" in sys.argv:
        args = [k for k in ents if not ents[k]["gem_claim"]["forward_units"]]

    for k in args:
        e = ents[k]
        g = e["gem_claim"]
        fwd = ", ".join(f"{u['kind']} {u['status']}" for u in g["forward_units"]) or "nothing forward"
        print("=" * 94)
        print(f"{k} | {e['name']} | {e['owner']} | {e['country']}")
        print(f"   GEM CLAIM (June 2026 V1): {fwd}; units present: {','.join(g['unit_kinds_present']) or 'none'}")
        for f in by_plant.get(k, []):
            if f["text_chars"] < 400 or not f.get("sha256"):
                continue
            ss_ = sentences(text_for(f["sha256"]))
            if not ss_:
                continue
            print(f"   -- {f['url'][:88]}")
            for s in ss_:
                print(f"        {s[:270]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

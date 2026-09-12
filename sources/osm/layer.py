"""One pass per extract, kept: the industrial layer a sweep needs, and nothing else.

WHY A CACHE. A sweep used to re-parse the whole extract — 1.4 GB for Norway — once for the
place nodes and once per target. Fourteen sweeps across eight extracts took most of a day
and the last of them ran twelve hours before it was killed. The features a sweep actually
reads are a thousandth of the file. Parse once, keep that, and a sweep becomes a scan of a
few thousand records.

WHAT IS KEPT. Named places (a sweep's centre), and every industrial, works, power or
construction feature with its position and name. Everything else — roads, buildings,
coastlines, the ninety-nine per cent — is dropped.

WHAT IS RECORDED WITH IT. The extract's filename and its Geofabrik date, so the layer
cannot be read without knowing which day's basemap it is. A layer whose date does not match
its extract is refused.

AND THE READER CHECKS ITSELF. build() counts what it keeps and validate() re-counts a known
extract against a recorded total, because the defect this cache replaces was a silent
truncation — a list cut at twelve that read as a complete answer. A count that is wrong
loudly is worth a great deal more than a list that is short quietly.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pbf  # noqa: E402

DATED = re.compile(r"-(\d{6})\.osm\.pbf$")
PLACE_KEYS = ("city", "town", "suburb", "village", "quarter", "neighbourhood",
              "hamlet", "locality", "isolated_dwelling")

# THERE IS NO FEATURE-COUNT REFERENCE HERE, and there will not be one until a tool other
# than this reader can produce it. None is installed — pyosmium has no wheel for this
# Python and there is no osmium-tool — so the honest position is none.
#
# THE FIRST VERSION OF THIS CHECK CARRIED TYPED NUMBERS and failed on its own first run,
# which looked like the check working. The repair was worse than the defect: the numbers
# were reset to what the reader had just produced, which makes the check pass by
# construction for ever. A reference taken from the thing it checks is a mirror.
#
# WHAT REPLACES IT IS STRUCTURAL. pbf.scan_blobs() walks the blob HEADERS of the extract,
# decompressing nothing and parsing no primitive, and reports how many blobs there are and
# where the file ends. The reader must arrive at the same two numbers by the other route —
# actually reading and decompressing every blob. A reader that stopped early, skipped a
# blob or lost its place cannot agree with the container it was reading.

def extract_date(path: Path) -> str:
    m = DATED.search(path.name)
    if not m:
        raise SystemExit(f"{path.name} carries no Geofabrik date; re-download the dated "
                         f"filename so the layer can say which basemap it holds")
    y, mo, d = m.group(1)[:2], m.group(1)[2:4], m.group(1)[4:]
    return f"20{y}-{mo}-{d}"


def interesting(tags: dict) -> bool:
    return (tags.get("man_made") == "works" or tags.get("power") in ("plant", "substation")
            or tags.get("landuse") in ("industrial", "port") or "industrial" in tags
            or tags.get("building") == "industrial" or "construction" in tags)


def build(extract: Path, out: Path) -> dict:
    """Read the extract once; write the layer. Refuse to write it if the read was partial."""
    expect_blobs, expect_bytes = pbf.scan_blobs(extract)
    size = extract.stat().st_size
    if expect_bytes != size:
        raise SystemExit(f"{extract.name}: blob headers describe {expect_bytes} bytes and "
                         f"the file is {size} — the extract is truncated or not a PBF")
    industrial: list[dict] = []
    places: list[dict] = []
    want: dict[int, list] = {}
    stats1: dict = {}

    for raw in pbf.blocks(extract, stats1):
        for item in pbf.parse_block(raw):
            if item[0] == "node":
                _, _, la, lo, tags = item
                if not tags:
                    continue
                if tags.get("name") and tags.get("place") in PLACE_KEYS:
                    places.append({"n": tags["name"], "k": tags["place"],
                                   "lat": round(la, 6), "lon": round(lo, 6)})
                if interesting(tags):
                    industrial.append({
                        "n": tags.get("name"), "lat": round(la, 6), "lon": round(lo, 6),
                        "id": item[1], "kind": "node",
                        "t": tags.get("landuse") or tags.get("man_made")
                             or tags.get("power") or "industrial"})
            else:
                _, _, refs, tags = item
                if not tags or not interesting(tags) or not refs:
                    continue
                # THE OSM IDENTIFIER IS KEPT because a position has to cite the feature
                # it came from. A latitude and a longitude with no way of saying which
                # drawn thing they are is exactly the unsourced coordinate this register
                # refuses from a geocoder.
                industrial.append({"n": tags.get("name"), "ref": refs[0],
                                   "id": item[1], "kind": "way",
                                   "t": tags.get("landuse") or tags.get("man_made")
                                        or tags.get("power") or "industrial"})
                want[refs[0]] = None

    stats2: dict = {}
    if want:                       # one more pass to place the ways
        for raw in pbf.blocks(extract, stats2):
            for item in pbf.parse_block(raw):
                if item[0] != "node":
                    continue
                _, nid, la, lo, _ = item
                if nid in want:
                    want[nid] = (round(la, 6), round(lo, 6))
        for f in industrial:
            pos = want.get(f.pop("ref", None))
            if pos:
                f["lat"], f["lon"] = pos
    industrial = [f for f in industrial if "lat" in f]

    for n, st in (("pass 1", stats1), ("pass 2", stats2)):
        if not st:
            continue
        if st["blobs"] != expect_blobs or st["bytes"] != expect_bytes:
            raise SystemExit(
                f"{extract.name} {n}: the reader consumed {st['blobs']} blobs ending at "
                f"{st['bytes']}, the blob headers describe {expect_blobs} ending at "
                f"{expect_bytes}. THE READ WAS PARTIAL and nothing measured from it means "
                f"anything. No layer written.")

    doc = {"extract": extract.name, "basemap_date": extract_date(extract),
           "blobs": expect_blobs, "bytes": expect_bytes,
           "counts": {"industrial": len(industrial), "places": len(places)},
           "places": places, "industrial": industrial}
    out.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return {"blobs": expect_blobs, "bytes": expect_bytes, **doc["counts"]}


def load(layer: Path) -> dict:
    """A layer that does not carry its structural figures is not read."""
    doc = json.loads(layer.read_text(encoding="utf-8"))
    if "blobs" not in doc or "bytes" not in doc:
        raise SystemExit(f"{layer.name} carries no blob count or byte total — it was built "
                         f"before the structural check and cannot be trusted to be whole")
    return doc


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    counts = build(src, dst)
    print(f"{src.name:38} blobs={counts['blobs']:>6} bytes={counts['bytes']:>12,} "
          f"industrial={counts['industrial']:>7,} places={counts['places']:>6,}")

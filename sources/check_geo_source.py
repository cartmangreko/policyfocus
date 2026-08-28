"""
The gate on the map ground: data/geo/.

    python3 check_geo_source.py          # exits non-zero on any mismatch

WHY A GATE ON A FILE NOBODY EDITS. Precisely because nobody edits it. A vector
basemap is the one input here that is opaque -- a zip of binary shapefiles that
no reviewer reads and no diff shows. If it were replaced, truncated by a failed
fetch, or quietly swapped for a different scale, the maps would keep rendering
and would be drawn on a ground nobody chose. The checksum is what turns that
from an invisible change into a build failure.

It checks three things and nothing else:

  RECORDED    every file in data/geo/ has a record in SOURCE.json, and every
              record names a file that is there. A basemap with no provenance
              is a picture of Europe somebody found.

  INTACT      the bytes hash to what the record says. This is the whole point.

  COMPLETE    the zip holds the members the record lists, so a shapefile
              missing its .dbf or .prj fails here rather than in a renderer.

What is NOT here: whether the register's coordinates land where they should.
That reads the basemap rather than checking it, and it lives in
sources/check_coordinates.py, which runs next.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "geo"
RECORD = GEO / "SOURCE.json"

REQUIRED = ("file", "title", "publisher", "licence", "url", "retrieved_date",
            "sha256", "bytes", "contains", "crs")


def main() -> int:
    errors: list[str] = []

    if not RECORD.exists():
        print(f"check_geo_source: {RECORD} is missing — the basemap has no provenance")
        return 1
    record = json.loads(RECORD.read_text(encoding="utf-8"))

    for field in REQUIRED:
        if not record.get(field):
            errors.append(f"SOURCE.json: missing {field}")

    name = record.get("file")
    path = GEO / name if name else None

    on_disk = {p.name for p in GEO.iterdir() if p.name not in ("SOURCE.json",)}
    unrecorded = on_disk - {name}
    for extra in sorted(unrecorded):
        errors.append(f"{extra}: in data/geo/ and not in SOURCE.json — record it or remove it")

    if path and not path.exists():
        errors.append(f"SOURCE.json names {name}, which is not in data/geo/")
    elif path:
        raw = path.read_bytes()
        if len(raw) != record.get("bytes"):
            errors.append(f"{name}: {len(raw)} bytes on disk, {record.get('bytes')} recorded")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != record.get("sha256"):
            errors.append(f"{name}: sha256 {digest} does not match the recorded "
                          f"{record.get('sha256')} — this is not the file that was fetched")
        if zipfile.is_zipfile(path):
            members = set(zipfile.ZipFile(path).namelist())
            for wanted in record.get("contains") or []:
                if wanted not in members:
                    errors.append(f"{name}: recorded member {wanted} is not in the archive")

    if errors:
        print(f"check_geo_source: {len(errors)} problem(s)\n")
        print("\n".join(f"  {line}" for line in errors))
        return 1

    print(f"check_geo_source: OK — {record['title']}, {record['bytes']:,} bytes, "
          f"{record['licence']}, fetched {record['retrieved_date']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

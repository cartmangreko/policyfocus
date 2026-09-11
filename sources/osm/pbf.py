"""A minimal OpenStreetMap PBF reader, standard library only.

WHY THIS EXISTS. The 44 coordinate sweeps have to be repeatable, and a public Overpass
endpoint is not: overpass.kumi.systems answered a small query in 39 seconds and then 504'd
for an hour on 10 September 2026, and overpass-api.de refuses this client's requests to
/api/interpreter at the web-server layer. A sweep whose answer depends on which minute it
ran is not evidence. A dated Geofabrik extract is: the same file gives the same answer
tomorrow, and its date is part of the record.

WHY IT IS HAND-WRITTEN. pyosmium publishes no wheel for CPython 3.11 on arm64 and there is
no Homebrew here to install osmium-tool, so the alternative to 200 lines of protobuf was no
local reading at all. The format is small enough to be worth it: a PBF is a sequence of
length-prefixed blobs, each a zlib-compressed PrimitiveBlock, and everything this register
needs lives in three message types.

WHAT IT DOES NOT DO. Relations, history, changesets, and ways whose geometry matters beyond
a representative point. A works is looked for by NAME and TAG here; its polygon is a
separate question, and the perimeter refuses an estate polygon anyway.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

WIRE_VARINT, WIRE_64, WIRE_BYTES, WIRE_32 = 0, 1, 2, 5


def _varint(buf: bytes, i: int) -> tuple[int, int]:
    shift = result = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, i
        shift += 7


def _zigzag(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def fields(buf: bytes):
    """(field number, wire type, value) for one protobuf message."""
    i, n = 0, len(buf)
    while i < n:
        key, i = _varint(buf, i)
        fn, wt = key >> 3, key & 7
        if wt == WIRE_VARINT:
            v, i = _varint(buf, i)
        elif wt == WIRE_BYTES:
            ln, i = _varint(buf, i)
            v, i = buf[i:i + ln], i + ln
        elif wt == WIRE_64:
            v, i = struct.unpack_from("<Q", buf, i)[0], i + 8
        elif wt == WIRE_32:
            v, i = struct.unpack_from("<I", buf, i)[0], i + 4
        else:
            raise ValueError(f"wire type {wt} at {i}")
        yield fn, wt, v


def _packed(buf: bytes, zig: bool = False):
    i, n = 0, len(buf)
    while i < n:
        v, i = _varint(buf, i)
        yield _zigzag(v) if zig else v


def blocks(path: Path):
    """Every OSMData PrimitiveBlock in the file, decompressed."""
    with open(path, "rb") as fh:
        while True:
            head = fh.read(4)
            if len(head) < 4:
                return
            (hlen,) = struct.unpack(">I", head)
            header = fh.read(hlen)
            btype, dsize = None, 0
            for fn, _, v in fields(header):
                if fn == 1:
                    btype = v.decode()
                elif fn == 3:
                    dsize = v
            blob = fh.read(dsize)
            if btype != "OSMData":
                continue
            raw = None
            for fn, _, v in fields(blob):
                if fn == 1:
                    raw = v
                elif fn == 3:
                    raw = zlib.decompress(v)
            if raw:
                yield raw


def _strings(buf: bytes) -> list[bytes]:
    return [v for fn, _, v in fields(buf) if fn == 1]


def parse_block(raw: bytes):
    """Yield ("node", id, lat, lon, tags) and ("way", id, refs, tags)."""
    st: list[bytes] = []
    groups: list[bytes] = []
    gran, lat_off, lon_off = 100, 0, 0
    for fn, _, v in fields(raw):
        if fn == 1:
            st = _strings(v)
        elif fn == 2:
            groups.append(v)
        elif fn == 17:
            gran = v
        elif fn == 19:
            lat_off = v
        elif fn == 20:
            lon_off = v

    def coord(raw_v, off):
        return 1e-9 * (off + gran * raw_v)

    def s(i):
        return st[i].decode("utf-8", "replace")

    for g in groups:
        for fn, _, v in fields(g):
            if fn == 1:                                   # Node
                nid = lat = lon = 0
                keys, vals = [], []
                for f2, _, v2 in fields(v):
                    if f2 == 1:
                        nid = _zigzag(v2)
                    elif f2 == 2:
                        keys = list(_packed(v2))
                    elif f2 == 3:
                        vals = list(_packed(v2))
                    elif f2 == 8:
                        lat = _zigzag(v2)
                    elif f2 == 9:
                        lon = _zigzag(v2)
                yield ("node", nid, coord(lat, lat_off), coord(lon, lon_off),
                       {s(k): s(w) for k, w in zip(keys, vals)})
            elif fn == 2:                                 # DenseNodes
                ids = lats = lons = kv = []
                for f2, _, v2 in fields(v):
                    if f2 == 1:
                        ids = list(_packed(v2, True))
                    elif f2 == 8:
                        lats = list(_packed(v2, True))
                    elif f2 == 9:
                        lons = list(_packed(v2, True))
                    elif f2 == 10:
                        kv = list(_packed(v2))
                nid = la = lo = 0
                j = 0
                for n in range(len(ids)):
                    nid += ids[n]
                    la += lats[n]
                    lo += lons[n]
                    tags = {}
                    if kv:
                        while j < len(kv) and kv[j] != 0:
                            tags[s(kv[j])] = s(kv[j + 1])
                            j += 2
                        j += 1
                    yield ("node", nid, coord(la, lat_off), coord(lo, lon_off), tags)
            elif fn == 3:                                 # Way
                wid = 0
                keys, vals, refs = [], [], []
                for f2, _, v2 in fields(v):
                    if f2 == 1:
                        wid = v2
                    elif f2 == 2:
                        keys = list(_packed(v2))
                    elif f2 == 3:
                        vals = list(_packed(v2))
                    elif f2 == 8:
                        r = 0
                        for d in _packed(v2, True):
                            r += d
                            refs.append(r)
                yield ("way", wid, refs, {s(k): s(w) for k, w in zip(keys, vals)})

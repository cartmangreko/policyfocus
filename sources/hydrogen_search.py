#!/usr/bin/env python3
"""The declared reader for the hydrogen funder pass, and its cache index.

    python3 sources/hydrogen_search.py URL [URL ...]

Every fetch this pass makes goes through here: the URL, the day, the byte count
and the SHA-256 land in sources/cache/hydrogen/index.json, and the body lands
beside it under its hash. That is what makes "somebody looked" checkable rather
than asserted.

SAME READER AS sources/ccs_search.py AND sources/battery_search.py, POINTED AT A
DIFFERENT CACHE. It is a copy rather than an import because each pass is
snapshotted separately and a shared module would let a change made for one
silently rewrite another's record of what it did. The pace, the User-Agent and
the empty-body threshold are identical and deliberately so.

AN EMPTY BODY IS A REFUSAL AND IT IS RECORDED AS ONE. Under 400 characters of
readable text on a 200 is written down as "200, empty body", not as a fetch that
succeeded. sources/scope.md, "A 200 with an empty body is a refusal, and the link
checker cannot see it". D41 measured exactly that against the EU's own grant
registers on 10 September 2026, and the funder pass of brief 12 re-measures it
rather than inheriting the answer.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys, threading, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources" / "cache" / "hydrogen"
INDEX = CACHE / "index.json"
UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")
PAUSE = 2.0

# THE INDEX IS ONE FILE AND A FETCH IS A READ-MODIFY-WRITE OF IT. Added 17 September 2026,
# when the 2023-population pass began fetching on several threads: the pace is unchanged --
# every worker still waits PAUSE after its own request -- but two workers appending to the
# index at once would lose one of the two records, and a fetch that happened and is not in
# the index is exactly the thing this file exists to prevent. A lock is cheap; a silently
# unrecorded fetch is not recoverable.
_LOCK = threading.Lock()

_HEAD = [
    "THE CACHE INDEX FOR THE HYDROGEN PASSES. One entry per fetch: the URL, the day,",
    "the byte count and the SHA-256 of what came back. Bodies are held beside this",
    "file under their hash and are NOT committed -- the index is the part that makes a",
    "claim checkable, and it holds no publisher's text.",
    "",
    "BENCHMARK FILES ARE INDEXED HERE TOO, as fetches with no http status where they",
    "were retrieved by hand. Their hashes are the snapshot -- see",
    "sources/benchmark_snapshots.json.",
]


def _index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"_comment": _HEAD, "fetches": []}


def _write(idx: dict) -> None:
    INDEX.write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def text_of(body: bytes, ctype: str) -> str:
    if "pdf" in (ctype or ""):
        return ""
    t = body.decode("utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    import html as _h
    return re.sub(r"\s+", " ", _h.unescape(t)).strip()


def fetch(url: str, source_type: str, note: str = "") -> dict:
    """One request, recorded either way. Never raises."""
    CACHE.mkdir(parents=True, exist_ok=True)
    rec = {"url": url, "domain": urllib.parse.urlsplit(url).netloc,
           "source_type": source_type, "date": time.strftime("%Y-%m-%d"),
           "http": None, "bytes": 0, "sha256": "", "text_chars": 0,
           "outcome": "", "note": note}
    try:
        # A NON-ASCII URL IS STILL A URL, and urllib will not send one: it encodes the
        # request line as ASCII and raises UnicodeEncodeError, so the request never
        # leaves. THE STEEL CENSUS LOST TWENTY OF THE LARGEST WORKS IN EUROPE TO THIS
        # in September 2026 — every plant whose name carries a diacritic — and recorded
        # each as a fetch that had happened and returned nothing, which made an
        # unsearched works look searched. The same shape bites on a space in a path
        # (InvalidURL). Percent-encode the path and the query, punycode the host, and
        # keep the URL as the publisher writes it in the record so a reader can follow
        # it. See sources/steel_docket.md, D-S1, and sources/check_fetch_records.py.
        parts = urllib.parse.urlsplit(url)
        safe = urllib.parse.urlunsplit((
            parts.scheme,
            parts.netloc.encode("idna").decode("ascii")
            if any(ord(c) > 127 for c in parts.netloc) else parts.netloc,
            urllib.parse.quote(parts.path, safe="/%:@&=+$,~()'*!"),
            urllib.parse.quote(parts.query, safe="/%:@&=+$,~()'*!?"),
            ""))
        req = urllib.request.Request(safe, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read()
            rec["http"] = r.status
            ctype = r.headers.get("Content-Type", "")
        rec["bytes"] = len(body)
        rec["sha256"] = hashlib.sha256(body).hexdigest()
        txt = text_of(body, ctype)
        rec["text_chars"] = len(txt)
        (CACHE / rec["sha256"]).write_bytes(body)
        if rec["text_chars"] < 400 and "pdf" not in ctype:
            rec["outcome"] = f"{rec['http']}, empty body"
        else:
            rec["outcome"] = f"{rec['http']}, {rec['text_chars']} chars"
    except urllib.error.HTTPError as e:
        rec["http"] = e.code
        rec["outcome"] = f"{e.code}"
    except Exception as e:                                    # noqa: BLE001
        rec["outcome"] = f"{type(e).__name__}"
    with _LOCK:
        idx = _index()
        idx["fetches"].append(rec)
        _write(idx)
    time.sleep(PAUSE)
    return rec


def body_bytes(sha: str) -> bytes:
    p = CACHE / sha
    return p.read_bytes() if p.exists() else b""


def body_text(sha: str) -> str:
    b = body_bytes(sha)
    if not b:
        return ""
    return text_of(b, "" if b[:4] != b"%PDF" else "pdf")


def record_manual(path: pathlib.Path, url: str, note: str,
                  source_type: str = "benchmark", outcome: str = "") -> dict:
    """A file somebody retrieved by hand, indexed with the same fields.

    No http status: nothing here made a request. The hash is the point.
    """
    idx = _index()
    b = path.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    for r in idx["fetches"]:
        if r.get("sha256") == sha and r.get("file") == str(path.relative_to(ROOT)):
            return r
    rec = {"url": url, "domain": urllib.parse.urlsplit(url).netloc,
           "source_type": source_type, "date": time.strftime("%Y-%m-%d"),
           "http": None, "bytes": len(b), "sha256": sha,
           "text_chars": 0, "outcome": outcome or "retrieved by hand",
           "note": note, "file": str(path.relative_to(ROOT))}
    idx["fetches"].append(rec)
    _write(idx)
    return rec


if __name__ == "__main__":
    for u in sys.argv[1:]:
        r = fetch(u, "grant_register")
        print(f"{r['outcome']:28} {r['url']}")

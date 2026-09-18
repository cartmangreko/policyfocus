#!/usr/bin/env python3
"""The declared reader for the steel census, and its cache index.

    python3 sources/steel_search.py URL [URL ...]

Every fetch this pass makes goes through here: the URL, the day, the byte count
and the SHA-256 land in sources/cache/steel/index.json, and the body lands beside
it under its hash. That is what makes "somebody looked" checkable rather than
asserted — the hydrogen pass recorded 881 fetches over 167 entries and the
batteries pass its own, for the same reason.

SAME READER AS sources/battery_search.py, POINTED AT A DIFFERENT CACHE. It is a
copy rather than an import because the two passes are snapshotted separately and
a shared module would let a change made for one silently rewrite the other's
record of what it did. The pace, the User-Agent and the empty-body threshold are
identical and deliberately so.

WHAT THIS PASS READS, AND UNDER WHOSE TERMS. The benchmark is GEM's Global Iron
and Steel Tracker, June 2026 (V1), and its licence is settled in a way neither of
the other two sectors' was: THE FILE STATES IT ITSELF, on its own About tab —
"Distributed under a Creative Commons Attribution 4.0 International License."
That is the first benchmark in brief 8 whose terms did not have to be read off a
product page and held as a disagreement.

THE BYTES STAY OUT OF THE REPOSITORY ANYWAY, on the hydrogen and batteries
precedent: this repository holds identities and its own reasoning, and a
publisher's file is reproducible from its hash and its URL. CC BY would permit a
copy; not taking one is a choice about what this repository is for.

AN EMPTY BODY IS A REFUSAL AND IT IS RECORDED AS ONE. Under 400 characters of
readable text on a 200 is written down as "200, empty body", not as a fetch that
succeeded. sources/scope.md, "A 200 with an empty body is a refusal, and the link
checker cannot see it".
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources" / "cache" / "steel"
INDEX = CACHE / "index.json"
UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")
PAUSE = 2.0

_HEAD = [
    "THE CACHE INDEX FOR THE STEEL CENSUS, brief 8 sector 3. One entry per",
    "fetch: the URL, the day, the byte count and the SHA-256 of what came back. Bodies",
    "are held beside this file under their hash and are NOT committed -- the index is",
    "the part that makes a claim checkable, and it holds no publisher's text.",
    "",
    "THE BENCHMARK FILE IS INDEXED HERE TOO, as a fetch with no http status: it was",
    "retrieved by hand past an account login, which is an acceptance this pipeline may",
    "not give. Its hash is the snapshot -- see sources/benchmark_snapshots.json.",
]


def _index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"_comment": _HEAD, "fetches": []}


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
    idx = _index()
    rec = {"url": url, "domain": urllib.parse.urlsplit(url).netloc,
           "source_type": source_type, "date": time.strftime("%Y-%m-%d"),
           "http": None, "bytes": 0, "sha256": "", "text_chars": 0,
           "outcome": "", "note": note}
    try:
        # A NON-ASCII URL IS STILL A URL. urllib refuses to send one — it encodes
        # the request line as ASCII — and raised UnicodeEncodeError on twenty of
        # this census's plants, every one of them a works whose name carries a
        # diacritic: SSAB Luleå and Oxelösund, ArcelorMittal Kraków and Dąbrowa
        # Górnicza, Eisenhüttenstadt, Liepājas Metalurgs. THE FAILURE WAS SILENT
        # IN THE WORST WAY: the entry recorded a fetch that had happened and
        # returned nothing, so the plant looked searched and was not — and the
        # twenty were disproportionately the large integrated works this
        # perimeter is most about. Percent-encode the path and the query, leave
        # the scheme and host alone, and record the URL as the publisher writes
        # it so a reader can still follow it.
        parts = urllib.parse.urlsplit(url)
        safe = urllib.parse.urlunsplit((
            parts.scheme, parts.netloc.encode("idna").decode("ascii")
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
    idx["fetches"].append(rec)
    INDEX.write_text(json.dumps(idx, indent=1, ensure_ascii=False), encoding="utf-8")
    time.sleep(PAUSE)
    return rec


def body_text(sha: str) -> str:
    p = CACHE / sha
    if not p.exists():
        return ""
    b = p.read_bytes()
    return text_of(b, "" if b[:4] != b"%PDF" else "pdf")


def record_manual(path: pathlib.Path, url: str, note: str) -> dict:
    """A file somebody retrieved by hand, indexed with the same fields.

    No http status: nothing here made a request. The hash is the point.
    """
    idx = _index()
    b = path.read_bytes()
    rec = {"url": url, "domain": urllib.parse.urlsplit(url).netloc,
           "source_type": "benchmark", "date": time.strftime("%Y-%m-%d"),
           "http": None, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
           "text_chars": 0, "outcome": "retrieved by hand past an account login",
           "note": note, "file": str(path.relative_to(ROOT))}
    idx["fetches"].append(rec)
    INDEX.write_text(json.dumps(idx, indent=1, ensure_ascii=False), encoding="utf-8")
    return rec


if __name__ == "__main__":
    for u in sys.argv[1:]:
        r = fetch(u, "company")
        print(r["outcome"], r["url"])

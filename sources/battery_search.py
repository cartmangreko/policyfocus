#!/usr/bin/env python3
"""The declared reader for the batteries census, and its cache index.

Every fetch this pass makes goes through here: the URL, the day, the byte count
and the SHA-256 land in sources/cache/batteries/index.json, and the body lands
beside it under its hash. That is what makes "somebody looked" checkable rather
than asserted -- the hydrogen pass recorded 881 fetches over 167 entries for the
same reason.

READING PACE. One request at a time with a pause between, the declared
User-Agent, and no retry loop. The publishers this pass reads (T&E, Battery-News)
are read under their own terms, recorded in sources/benchmark_snapshots.json.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "sources" / "cache" / "batteries"
INDEX = CACHE / "index.json"
UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")
PAUSE = 2.0


def _index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"_comment": [
        "THE CACHE INDEX FOR THE BATTERIES CENSUS. One entry per fetch: the URL, the day,",
        "the byte count and the SHA-256 of what came back. Bodies are held beside this file",
        "under their hash and are NOT committed -- the index is the part that makes a claim",
        "checkable, and it holds no publisher's text.",
    ], "fetches": []}


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
        req = urllib.request.Request(url, headers={"User-Agent": UA})
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


if __name__ == "__main__":
    for u in sys.argv[1:]:
        r = fetch(u, "company")
        print(r["outcome"], r["url"])

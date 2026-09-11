"""The fetch cache for the supplier-side dependency sweep (Brief 9).

    python3 dep_fetch.py URL [URL ...]        # fetch, cache, print index lines
    python3 dep_fetch.py --file urls.txt
    python3 dep_fetch.py --list               # what is cached

WHY A SECOND CACHE. sources/cache/ holds EUR-Lex manifestations, keyed by CELEX,
fetched by fetch_eurlex.py. Nothing in this repository cached an ordinary web page
before: the register cites publishers' live URLs and check_links.py re-fetches them
to see whether they still answer. That is the right discipline for a citation and
the wrong one for a sweep, because a sweep reads a page once and then wants to read
it again ten times -- after a ruling, after a vocabulary change, after somebody asks
where a number came from -- and each of those re-reads must see the same bytes the
first read saw. So: one file per URL, and an index recording url, date, size and
SHA-256, per the brief.

WHAT IS STORED IS THE BYTES AS SERVED. No rendering, no readability pass, no
normalisation. Extraction is a separate step (dep_text.py) and may be redone; if it
were done here, redoing it would mean re-fetching, and the page may have changed.

STORED GZIPPED, AND THE BODIES ARE NOT COMMITTED. The SHA-256 in the index is of
the bytes as served, not of the compressed copy, so it verifies against a re-fetch.
sources/cache/hydrogen/ set the precedent and set it for the right reason: a
repository that redistributes somebody else's corpus has taken on a licensing
question it was never asked. The index IS committed, so what was read, when, and
at what hash is in history even on a machine that has never run the sweep.

A FAILED FETCH IS AN ENTRY. status 403, 404, a timeout: recorded with the status and
no body. A supplier whose newsroom refuses the reader is a finding about that
supplier -- it is exactly the "publishes nothing in English" shape the brief asks to
be written down rather than filled in from press -- and an empty result that leaves no
trace is indistinguishable from a search nobody ran.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
CACHE = HERE / "dependency_cache"
INDEX = CACHE / "index.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TIMEOUT = 40
PAUSE = 0.7          # per host, seconds; a sweep is not a load test
EXT = {"text/html": ".html", "application/xhtml+xml": ".html",
       "application/pdf": ".pdf", "text/xml": ".xml", "application/xml": ".xml",
       "application/rss+xml": ".xml", "text/plain": ".txt",
       "application/json": ".json"}


def load() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text())
    return {}


def save(idx: dict) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(idx, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def key(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def fetch(url: str, idx: dict, force: bool = False) -> dict:
    k = key(url)
    if k in idx and not force and idx[k].get("sha256"):
        return idx[k]
    tmp = CACHE / f".tmp-{k}"
    CACHE.mkdir(parents=True, exist_ok=True)
    # A FULL BROWSER HEADER SET, and not for fun. plugpower.com's edge answers 403
    # to a request carrying only a User-Agent and 200 to the same request carrying
    # the Accept, Sec-Fetch-* and Upgrade-Insecure-Requests headers a browser sends.
    # Several other newsrooms on this perimeter do the same. This is the difference
    # between "the supplier publishes nothing" and "the sweep was refused at the
    # door", and the sweep must not be able to confuse the two.
    args = ["curl", "-sSL", "-m", str(TIMEOUT), "-A", UA, "--compressed",
            "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,*/*;q=0.8",
            "-H", "Accept-Language: en-US,en;q=0.9",
            "-H", "Sec-Fetch-Dest: document", "-H", "Sec-Fetch-Mode: navigate",
            "-H", "Sec-Fetch-Site: none", "-H", "Upgrade-Insecure-Requests: 1",
            "-w", "%{http_code}\t%{content_type}\t%{url_effective}",
            "-o", str(tmp), url]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT + 15)
        meta = r.stdout.strip().split("\t")
        code = int(meta[0]) if meta and meta[0].isdigit() else 0
        ctype = (meta[1] if len(meta) > 1 else "").split(";")[0].strip()
        final = meta[2] if len(meta) > 2 else url
        err = r.stderr.strip()[:300]
    except (subprocess.TimeoutExpired, OSError) as exc:
        code, ctype, final, err = 0, "", url, f"{type(exc).__name__}: {exc}"[:300]

    entry = {"url": url, "final_url": final, "fetched_at": now, "status": code,
             "content_type": ctype, "bytes": 0, "sha256": None, "file": None,
             "error": err or None}
    if code and 200 <= code < 300 and tmp.exists() and tmp.stat().st_size:
        body = tmp.read_bytes()
        ext = EXT.get(ctype) or (".pdf" if body[:4] == b"%PDF" else ".html")
        dest = CACHE / f"{k}{ext}.gz"
        dest.write_bytes(gzip.compress(body))
        entry.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
                     file=dest.name)
    if tmp.exists():
        tmp.unlink()
    idx[k] = entry
    return entry


def main(argv: list[str]) -> int:
    idx = load()
    if "--list" in argv:
        for k, e in sorted(idx.items(), key=lambda kv: kv[1]["url"]):
            print(f"{e['status']:>3} {e['bytes']:>9} {(e['sha256'] or '-')[:12]} {e['url']}")
        print(f"{len(idx)} entries", file=sys.stderr)
        return 0
    force = "--force" in argv
    urls: list[str] = []
    rest = [a for a in argv if a not in ("--force",)]
    if rest and rest[0] == "--file":
        urls = [l.strip() for l in Path(rest[1]).read_text().splitlines()
                if l.strip() and not l.startswith("#")]
    else:
        urls = rest
    jobs = 1
    if "--jobs" in rest:
        i = rest.index("--jobs")
        jobs = int(rest[i + 1])
        urls = [u for u in urls if u not in (rest[i], rest[i + 1])]
    todo = [u for u in urls if force or key(u) not in idx or not idx[key(u)].get("sha256")]
    for u in urls:
        if u not in todo:
            e = idx[key(u)]
            print(f"{e['status']:>3} {e['bytes']:>9} {(e['sha256'] or '-')[:12]} cached {u}")

    # Threads, not processes, and a small number of them: the work is entirely
    # waiting on somebody else's web server. THREE IS THE CEILING ON PURPOSE. A
    # sweep that reads a supplier's whole newsroom is a guest on it; the pause
    # below keeps a single host to roughly one request a second whatever --jobs
    # says, which is the rate a person clicking through the archive would make.
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock
    lock, last = Lock(), {}

    def one(u: str) -> None:
        host = urlsplit(u).netloc
        while True:
            with lock:
                gap = time.time() - last.get(host, 0)
                if gap >= PAUSE:
                    last[host] = time.time()
                    break
            time.sleep(max(0.05, PAUSE - gap))
        e = fetch(u, idx, force)
        with lock:
            print(f"{e['status']:>3} {e['bytes']:>9} {(e['sha256'] or '-')[:12]} {e['url']}",
                  flush=True)
            save(idx)

    with ThreadPoolExecutor(max_workers=max(1, min(3, jobs))) as pool:
        list(pool.map(one, todo))
    save(idx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

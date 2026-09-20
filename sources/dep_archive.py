"""Captures of a newsroom whose live host refuses a declared reader.

    python3 dep_archive.py NODE_ID HOST/PATH-PREFIX [more prefixes] [--limit N]

WHEN THIS IS THE RIGHT TOOL AND WHEN IT IS NOT. A supplier that answers 200 is read
live; the archive is for the door that is shut — a 403, a WAF, a domain that has gone
— and the capture is then the speaker's own document under DECISION D-7, cited as the
capture and filed with `captured_at`. It is not a way round a slow site or a
paginated index.

THE CDX INDEX RATE-LIMITS AND SAYS SO WITH A 503, and a 503 read as "no capture"
would be a silence the archive never uttered. An exhausted retry prints `refused` and
records nothing, which is the refusal ruling one layer down — the same shape
hydrogen_test_2023.cdx() uses, and the reason this asks by path prefix rather than
scanning a host.

The urls printed carry the `id_/` infix, which is the archive's raw-artefact form: the
bytes as captured, with none of the archive's own banner markup in them. dep_records'
capture_date() reads the timestamp straight out of that url, so nothing here is typed
twice.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CDX = "https://web.archive.org/cdx/search/cdx"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def cdx(params, timeout=90, tries=4):
    url = CDX + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace") or "[]")
        except Exception:                                      # noqa: BLE001
            if i == tries - 1:
                return None
            time.sleep(4 * (i + 1))
    return None


def main(argv: list[str]) -> int:
    limit = 300
    if "--limit" in argv:
        i = argv.index("--limit")
        limit = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    node, prefixes = argv[0], argv[1:]
    urls, refused = [], []
    for p in prefixes:
        rows = cdx([("url", p), ("matchType", "prefix"), ("output", "json"),
                    ("fl", "timestamp,original"), ("filter", "statuscode:200"),
                    ("collapse", "urlkey"), ("limit", str(limit))])
        if rows is None:
            refused.append(p)
            continue
        for ts, original in [r for r in rows if r and r[0] != "timestamp"]:
            urls.append(f"https://web.archive.org/web/{ts}id_/{original}")
    out = HERE / f"dependency_cache/.cands-{node}.txt"
    out.write_text("\n".join(sorted(set(urls))))
    print(f"{node}: {len(set(urls))} captures"
          + (f", {len(refused)} prefix(es) refused by the index" if refused else ""),
          file=sys.stderr)
    for u in refused:
        print(f"  refused: {u}", file=sys.stderr)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

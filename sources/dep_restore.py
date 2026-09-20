"""Put the cache bodies back on a machine that has the index and not the corpus.

    python3 dep_restore.py --need          # what a build needs and cannot read
    python3 dep_restore.py --run [--all]   # re-fetch those, keep only byte-identical

WHY THIS EXISTS. The fetch cache is two things: `index.json`, which is COMMITTED and
records what was read, when, at what size and at what SHA-256; and the bodies, which
are gitignored (D-9) because redistributing somebody else's corpus is a licensing
question this repository was never asked. On the machine that ran brief 9 those two
live together. On any other machine — a fresh clone, or the same machine after a
clean — there is an index naming 2,674 pages and not one page.

That is fine for reading and fatal for WRITING. `dep_records.py --build` recomputes
`owner_side` by running dep_owner over the sources the register cites, so a rebuild
on a machine with no bodies would write an edges.json saying every row is unreadable
— which is false, and worse, is false in the shape of a finding.

SO THE BODIES COME BACK IN TWO CLASSES, AND THEY ARE NEVER THE SAME CLASS. Each page
is fetched again and its SHA-256 is compared with the one the index already records.

  MATCH — the artefact itself, byte for byte, whatever has happened to the site
  since. The body is written under the name the index gives it and everything that
  reads the cache is back where brief 9 left it.

  MISMATCH — the page answered and it is NOT the page that was read. The bytes are
  kept, because a later copy of a publisher's own page is worth reading and this
  pass has rows to read it for; and they are kept SOMEWHERE ELSE:
  `sources/dependency_cache/reread.json`, one entry per url, carrying today's date,
  today's hash and the hash it did not match. `dep_text.original()` is how anything
  that cares tells them apart, and the citation gate cares: a sentence cited from
  the page as it was on 11 September cannot be confirmed OR refuted by the page as
  it is today, so the gate goes on skipping those edges rather than ruling on the
  wrong artefact.

ONLY 5 OF THE FIRST 79 PAGES CAME BACK IDENTICAL, which is the number that decided
the shape: a newsroom rotates a teaser, a token, a build hash, and the body a reader
sees is unchanged while the bytes are not. A restore that kept only exact matches
would have restored six per cent of the corpus and called the rest missing.

INDEX.JSON IS NEVER TOUCHED. `dep_fetch.py --force` would re-fetch and rewrite the
entry, and the new `fetched_at` and `sha256` would erase the record of what was read
on 11 September 2026. The whole value of the index is that it is the older statement.
A re-read is a second statement about the same address and it goes in its own file.

WHAT COUNTS AS NEEDED. The urls a build actually opens: every edge's source, every
capacity and status source, and every source url the register cites for a row. The
other ~2,200 pages of the sweep are the reading behind those and are not re-fetched
by default; `--all` does the whole index for anybody who wants the corpus back.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import dep_fetch as F
import dep_text as T

HERE = Path(__file__).resolve().parent
REPORT = HERE / "dependency_restore.json"


def needed() -> list[str]:
    """Urls a build opens: the readings' sources and the register's own citations."""
    import dep_owner as O
    import dep_records as R
    import dep_readings  # noqa: F401  -- importing it IS the reading pass
    urls = {e["url"] for e in R.EDGES}
    urls |= {c["url"] for caps in R.NODE_CAPACITY.values() for c in caps}
    urls |= {ev["source_url"] for evs in R.NODE_STATUS.values() for ev in evs}
    urls |= {u for v in O.per_row().values() for u in v}
    return sorted(urls)


def missing(urls: list[str]) -> list[str]:
    idx = T.index()
    out = []
    for u in urls:
        e = idx.get(F.key(u))
        if e and e.get("sha256") and T.body(u) is None:
            out.append(u)
    return out


def run(urls: list[str]) -> dict:
    idx = T.index()
    reread = json.loads(T.REREAD.read_text()) if T.REREAD.exists() else {}
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    restored, changed, failed = [], [], []
    for u in urls:
        e = idx[F.key(u)]
        args = ["curl", "-sSL", "-m", str(F.TIMEOUT), "-A", F.UA, "--compressed",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,*/*;q=0.8",
                "-H", "Accept-Language: en-US,en;q=0.9",
                "-H", "Sec-Fetch-Dest: document", "-H", "Sec-Fetch-Mode: navigate",
                "-H", "Sec-Fetch-Site: none", "-H", "Upgrade-Insecure-Requests: 1",
                "-w", "%{http_code}", "-o", "-", u]
        try:
            r = subprocess.run(args, capture_output=True, timeout=F.TIMEOUT + 15)
            out = r.stdout
        except (subprocess.TimeoutExpired, OSError):
            out = b""
        # curl -w writes the status onto the same stream as the body with -o -,
        # so the trailing digits are the code and the rest is the page.
        code = out[-3:].decode("ascii", "replace") if len(out) >= 3 else ""
        body = out[:-3] if code.isdigit() else out
        got = hashlib.sha256(body).hexdigest() if body else None
        if got and got == e["sha256"]:
            (F.CACHE / e["file"]).write_bytes(gzip.compress(body))
            restored.append(u)
            state = "ok   "
        elif got:
            name = f"{F.key(u)}.reread{Path(e['file']).suffix.replace('.gz','') or '.html'}.gz"
            (F.CACHE / name).write_bytes(gzip.compress(body))
            reread[F.key(u)] = {
                "url": u, "fetched_at": now, "status": int(code) if code.isdigit() else 0,
                "bytes": len(body), "sha256": got, "file": name,
                "recorded_sha256": e["sha256"], "recorded_at": e["fetched_at"],
                "recorded_bytes": e["bytes"]}
            changed.append(u)
            state = "reread"
        else:
            failed.append({"url": u, "status": int(code) if code.isdigit() else None})
            state = "fail "
        print(f"{state} {u}", file=sys.stderr, flush=True)
    T.REREAD.write_text(json.dumps(
        {"_comment": [
            "A SECOND COPY OF A PAGE THIS CACHE ALREADY HAS AN OLDER STATEMENT ABOUT.",
            "Written by dep_restore.py when a re-fetch did not hash to what index.json",
            "records. The older entry in index.json is the artefact a brief-9 reading",
            "was made against and is never overwritten; this is the page as it is now.",
            "dep_text.original() distinguishes them and the citation gate skips an edge",
            "whose original body this machine does not hold.",
         ], "pages": reread}, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    return {"restored": restored, "changed": changed, "failed": failed}


def main(argv: list[str]) -> int:
    urls = sorted(T.index()[k]["url"] for k in T.index()) if "--all" in argv else needed()
    todo = missing(urls)
    if "--need" in argv:
        print(f"{len(urls)} urls a build opens, {len(todo)} of them with no body here")
        for u in todo[:20]:
            print("  " + u)
        return 0
    if "--run" not in argv:
        print(__doc__)
        return 0
    out = run(todo)
    REPORT.write_text(json.dumps({
        "_comment": [
            "A re-fetch of cache bodies this machine did not hold. `restored` hashed to",
            "what sources/dependency_cache/index.json already recorded and are the",
            "artefacts themselves; `changed` answered with different bytes and are on",
            "file as a re-read (dependency_cache/reread.json), never as the original;",
            "`failed` did not answer at all and stay missing.",
        ],
        "ran": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "asked": len(todo), "restored": len(out["restored"]),
        "changed": len(out["changed"]), "failed_count": len(out["failed"]),
        "failed": out["failed"]}, indent=1, ensure_ascii=False) + "\n")
    print(f"restored {len(out['restored'])}, re-read {len(out['changed'])}, "
          f"failed {len(out['failed'])} of {len(todo)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

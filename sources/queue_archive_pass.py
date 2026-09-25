#!/usr/bin/env python3
"""THE ARCHIVE PASS OVER THE BROWSER QUEUE, run before anybody opens a browser.

    python3 sources/queue_archive_pass.py              # ask the archive, record, write
                                                       #   nothing tracked
    python3 sources/queue_archive_pass.py --save       # …and submit the misses to
                                                       #   Save Page Now, then poll
    python3 sources/queue_archive_pass.py --write      # file what has a body, from the
                                                       #   record, asking nothing again
    python3 sources/queue_archive_pass.py --report     # cleared / empty shell / no capture

WHY THIS RUNS FIRST. `sources/manual/browser_queue.csv` is 66 entries a declared reader
could not read, and working one costs a person a browser, a save and a folder. Some of
those pages are already held by somebody else: the Internet Archive has a capture of the
URL that refused us, and a capture is a copy on file under the rule scope.md already
carries — "When a publisher goes dark after a page was read, cite the capture". An entry
whose document the archive holds does not need a morning of anybody's time, so the queue
is asked of the archive before it is handed over.

WHAT IT DOES TO ONE QUEUED URL, in order:

  1  asks the availability endpoint for the LATEST capture. That is the same question
     hydrogen_test_2023.availability_before() asks with a cut-off, without one: this pass
     is not scoring anything as of a date, it is looking for a readable copy.
  2  where there is none and --save is given, submits the URL to Save Page Now and polls
     availability until the capture appears or the wait runs out. SPN NEEDS CREDENTIALS —
     an anonymous POST answers `401 You need to be logged in` — so the keys are read from
     IA_ACCESS_KEY / IA_SECRET_KEY and, where they are absent, THE MISS IS RECORDED AS A
     MISS THIS PASS COULD NOT TEST rather than as an absent capture.
  3  reads the capture's raw bytes through the `id_` infix, which is the archive's
     artefact form — the bytes as captured, none of the archive's banner markup in them,
     the same form dep_archive.py hands on — and takes text with the sector's own reader.
  4  files a capture WITH A BODY through the archived-source rule: the document's own
     dateline in `date` at the precision it states, the capture's day in `captured_at`,
     `archived` true, and the ORIGINAL url in `url` with the Wayback url beside it in
     `read_url`, so the record cites the publisher and says how this register reached it.
     A capture with no dateline takes `date = captured_at` at `not_after`, which is the
     bound it is and not a day the publisher published on.

AN EMPTY SHELL IS RECORDED AND STAYS IN THE QUEUE. A capture of a page that draws itself
with a script is a capture of the script: 200, a few hundred bytes of chrome, and no
document. scope.md calls a 200 with an empty body a refusal, and this pass calls a capture
of one the same thing — it is filed as a fetch with `empty body` in its outcome so the
next reader can see the archive was asked and what it held, AND THE ENTRY STAYS IN THE
BROWSER QUEUE. A person still has to open it. The one thing this pass may not do is let
an empty shell stand in for a document and quietly take an entry off somebody's list.

A REFUSAL IS A MEASUREMENT OF A REQUEST. The availability endpoint and the CDX index both
rate-limit, and both say so with a 429 or a 503. An exhausted retry is recorded as
`refused` and counted apart from `no capture`: "the archive did not answer" and "the
archive holds nothing" are different facts and only one of them is about the URL.

NOTHING HERE WRITES A CLASS. Same rule as the pass it feeds: what this produces is a
record, a filed copy and a signal per entry. A person classes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = HERE.parent
QUEUE = ROOT / "sources" / "manual" / "browser_queue.csv"
PASS = ROOT / "sources" / "research_pass_14.json"
STATE = ROOT / "sources" / "queue_archive_pass.json"

READER = {"hydrogen": "hydrogen_search", "batteries": "battery_search",
          "cement": "ccs_search", "transport and storage": "ccs_search"}

AVAIL = "https://archive.org/wayback/available"
SAVE = "https://web.archive.org/save"
CDX = "https://web.archive.org/cdx/search/cdx"
UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")
PAUSE = 2.0                 # between requests, the pace the sector readers keep
READABLE = 400              # chars of text below which a body is a shell, as everywhere

# THE DATELINE, WHERE THE PUBLISHER PUT ONE. Read in the order a publisher means them:
# the article's own published time first, the structured-data date second, a dated
# <time> element third. A URL path saying /2022/12/ is NOT read — that is the
# publisher's filing and not the document's dateline (sector_map, `not_after`).
DATELINE = (
    re.compile(rb"""<meta[^>]+(?:property|name)=["'](?:article:published_time|"""
               rb"""og:published_time|publishdate|pubdate|date|DC\.date\.issued)["']"""
               rb"""[^>]+content=["']([^"']+)""", re.I),
    re.compile(rb"""<meta[^>]+content=["']([^"']+)["'][^>]+(?:property|name)="""
               rb"""["'](?:article:published_time|og:published_time)["']""", re.I),
    re.compile(rb""""datePublished"\s*:\s*"([^"]+)""", re.I),
    re.compile(rb"""<time[^>]+datetime=["'](\d{4}-\d{2}(?:-\d{2})?[^"']*)""", re.I),
)


# --------------------------------------------------------------------------
# THE ARCHIVE, ASKED


def _get(url: str, timeout=45, tries=3, data=None, headers=None):
    """(body, http, refusal). A 429 or a 503 exhausted is `refused`, not `nothing`.

    The distinction is the one ce6e1fe made in the dependency sweep and it is the same
    here: an index that throttled this reader has not told us the URL is unheld.
    """
    hdr = {"User-Agent": UA}
    hdr.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=hdr)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.status, ""
        except urllib.error.HTTPError as e:
            body = b""
            try:
                body = e.read()
            except Exception:                                  # noqa: BLE001
                pass
            if e.code in (429, 502, 503, 504, 520, 523) and i < tries - 1:
                time.sleep(8 * (i + 1))
                continue
            return body, e.code, (f"refused: {e.code}"
                                  if e.code in (429, 502, 503, 504, 520, 523) else "")
        except Exception as e:                                 # noqa: BLE001
            if i < tries - 1:
                time.sleep(4 * (i + 1))
                continue
            return b"", None, f"refused: {type(e).__name__}"
    return b"", None, "refused: retries exhausted"


def _capture(ts: str, url: str, status: str = "", via: str = "") -> dict:
    return {"timestamp": ts, "captured_at": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}",
            "crawl_status": status, "found_via": via,
            "read_url": f"https://web.archive.org/web/{ts}id_/{url}"}


def cdx_latest(url: str) -> dict:
    """The last capture the CDX index holds of this URL, or why there is none.

    THE SLOW ROUTE, ASKED WHERE THE FAST ONE SAID NOTHING, and the reason is the one
    hydrogen_test_2023.availability_before() already wrote down: the availability
    endpoint returns an empty `archived_snapshots` for URLs the CDX index does answer
    for, so an empty answer from it is not a finding. Only this one can say "the archive
    holds nothing", and a 503 from it is `refused` rather than nothing.
    """
    q = urllib.parse.urlencode({"url": url, "output": "json",
                                "fl": "timestamp,original,statuscode",
                                "limit": "-5"})
    body, http, refused = _get(f"{CDX}?{q}", timeout=90)
    time.sleep(PAUSE)
    if refused:
        return {"capture": None, "refused": refused}
    try:
        rows = json.loads(body.decode("utf-8", "replace") or "[]")
    except Exception:                                          # noqa: BLE001
        return {"capture": None, "refused": f"refused: unreadable index answer ({http})"}
    rows = [r for r in rows if r and r[0] != "timestamp"]
    if not rows:
        return {"capture": None, "refused": ""}
    ts, original = rows[-1][0], rows[-1][1]
    status = rows[-1][2] if len(rows[-1]) > 2 else ""
    return {"refused": "", "capture": _capture(ts, original, status, "the CDX index")}


def latest_capture(url: str) -> dict:
    """The archive's newest capture of this URL, or why there is none on file.

    THE STATUS IS RECORDED AND NOT FILTERED ON. dep_archive asks the CDX index with
    `filter=statuscode:200`; this asks availability first, which answers with whatever
    the crawler got — ignis.es's newest capture carries `202`. Filtering here would throw
    away a capture whose bytes this pass is about to read and judge on their own text,
    which is the better test and the only one that distinguishes a document from a shell.

    TWO SHAPES OF REQUEST, AND A CONCLUSION ONLY FROM THE ONE THAT CAN SUPPORT IT.
    Availability is a second where the index is twelve, so it is asked first; but it
    answers empty for URLs the index does hold, so an empty answer falls through to the
    index rather than being recorded as "no capture".
    """
    q = urllib.parse.urlencode({"url": url})
    body, http, refused = _get(f"{AVAIL}?{q}", timeout=30)
    time.sleep(PAUSE)
    if refused:
        return {"capture": None, "refused": refused}
    try:
        doc = json.loads(body.decode("utf-8", "replace") or "{}")
    except Exception:                                          # noqa: BLE001
        return {"capture": None, "refused": f"refused: unreadable answer ({http})"}
    snap = ((doc.get("archived_snapshots") or {}).get("closest") or {})
    ts = str(snap.get("timestamp") or "")
    if not snap.get("available") or len(ts) < 8:
        return cdx_latest(url)
    return {"refused": "", "capture": _capture(ts, url, str(snap.get("status") or ""),
                                               "the availability endpoint")}


def save_page_now(url: str, wait: int = 90) -> dict:
    """Submit to Save Page Now and poll for the capture. Never invents one.

    SPN IS NOT ANONYMOUS. `POST https://web.archive.org/save` answers
    `401 You need to be logged in to use Save Page Now` without credentials, so this
    asks for the S3-style keys the archive issues at archive.org/account/s3.php and, with
    none in the environment, says exactly that and records the URL as untested rather
    than as unheld. A pass that reported "no capture" for a request it never made would
    be making a claim about the archive out of a gap in its own configuration.
    """
    key, secret = os.environ.get("IA_ACCESS_KEY"), os.environ.get("IA_SECRET_KEY")
    if not (key and secret):
        return {"submitted": False,
                "outcome": "not submitted — Save Page Now needs credentials; set "
                           "IA_ACCESS_KEY and IA_SECRET_KEY (archive.org/account/s3.php)"}
    data = urllib.parse.urlencode({"url": url, "capture_all": "1"}).encode()
    body, http, refused = _get(SAVE, timeout=90, tries=2, data=data,
                               headers={"Accept": "application/json",
                                        "Authorization": f"LOW {key}:{secret}",
                                        "Content-Type": "application/x-www-form-urlencoded"})
    if refused or http not in (200, 201):
        txt = body.decode("utf-8", "replace")[:200] if body else ""
        return {"submitted": False, "outcome": refused or f"save refused: {http} {txt}"}
    waited = 0
    while waited < wait:
        time.sleep(15)
        waited += 15
        got = latest_capture(url)
        cap = got.get("capture")
        if cap and cap["captured_at"] >= time.strftime("%Y-%m-%d"):
            return {"submitted": True, "outcome": f"saved, captured {cap['captured_at']}",
                    "capture": cap}
    return {"submitted": True,
            "outcome": f"submitted and no capture had appeared after {wait}s"}


# --------------------------------------------------------------------------
# THE CAPTURE, READ


def dateline_of(body: bytes) -> tuple[str, str]:
    """(date padded to the earliest day its precision allows, precision). ('', '') where
    the document carries no dateline — the caller then uses the capture as `not_after`."""
    head = body[:400000]
    for pat in DATELINE:
        m = pat.search(head)
        if not m:
            continue
        raw = m.group(1).decode("utf-8", "replace").strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}", raw):
            return raw[:10], "day"
        if re.match(r"^\d{4}-\d{2}$", raw):
            return raw + "-01", "month"
        if re.match(r"^\d{4}$", raw):
            return raw + "-01-01", "year"
    return "", ""


def read_capture(url: str, cap: dict, mod) -> dict:
    """The capture's own bytes, hashed, filed in the sector cache, and read for text."""
    body, http, refused = _get(cap["read_url"], timeout=60)
    time.sleep(PAUSE)
    if refused or not body:
        return {"outcome": refused or f"capture unreadable: {http}",
                "bytes": 0, "sha256": "", "text_chars": 0}
    text = mod.text_of(body, "pdf" if body[:4] == b"%PDF" else "")
    sha = hashlib.sha256(body).hexdigest()
    mod.CACHE.mkdir(parents=True, exist_ok=True)
    (mod.CACHE / sha).write_bytes(body)
    date, prec = dateline_of(body)
    if not date:
        date, prec = cap["captured_at"], "not_after"
    return {"outcome": (f"{http}, {len(text)} chars" if len(text) >= READABLE
                        else f"{http}, empty body"),
            "bytes": len(body), "sha256": sha, "text_chars": len(text),
            "date": date, "date_precision": prec}


def verdict(rec: dict) -> str:
    """cleared | empty shell | no capture | refused — the four a URL can end in."""
    if rec.get("refused"):
        return "refused"
    if not rec.get("capture"):
        return "no capture"
    if rec.get("text_chars", 0) >= READABLE:
        return "cleared"
    return "empty shell"


# --------------------------------------------------------------------------
# THE QUEUE, THE STATE FILE AND THE FILING


def queue_rows() -> list[dict]:
    if not QUEUE.exists():
        raise SystemExit("queue_archive_pass: no sources/manual/browser_queue.csv — run "
                         "`python3 sources/research_pass.py --queue-csv`")
    with QUEUE.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def state_load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"_comment": [ln for ln in __doc__.strip().splitlines()[:6]],
            "started": time.strftime("%Y-%m-%d"),
            "rule": "scope.md, the archived-source rule: the dateline in `date`, the "
                    "capture's day in `captured_at`, `archived` true, the publisher's "
                    "own URL in `url`",
            "asked": {}}


def state_save(doc: dict) -> None:
    STATE.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8")


def targets(rows: list[dict]) -> list[tuple[str, str, str]]:
    """(entry_id, sector, url) for every URL the queue carries, in queue order.

    The same URL under two entries is asked once and recorded once; it is filed for both,
    because a capture that answers for two entries answers for both of them.
    """
    out = []
    for r in rows:
        for u in (r["urls_to_open"] or "").split(" | "):
            u = u.strip()
            if u:
                out.append((r["entry_id"], r["sector"], u))
    return out


def ask(args) -> int:
    rows = queue_rows()
    if args.sector:
        rows = [r for r in rows if r["sector"] == args.sector]
    doc = state_load()
    asked = doc["asked"]
    todo = [t for t in targets(rows) if t[2] not in asked or args.again]
    seen, uniq = set(), []
    for t in todo:
        if t[2] not in seen:
            seen.add(t[2])
            uniq.append(t)
    uniq = uniq[:args.limit]
    nourl = [r for r in rows if not (r["urls_to_open"] or "").strip()]
    print(f"queue_archive_pass: {len(rows)} queue entries, "
          f"{len(set(t[2] for t in targets(rows)))} distinct URLs, "
          f"{len(asked)} already asked, {len(uniq)} to ask now.")
    print(f"  {len(nourl)} entries carry no URL at all and are not this pass's to ask "
          f"— they are stage 2's.\n")

    for i, (entry_id, sector, url) in enumerate(uniq, 1):
        mod = __import__(READER[sector])
        rec = {"url": url, "entry_ids": sorted({e for e, _, u in targets(rows)
                                                if u == url}),
               "sector": sector, "asked_on": time.strftime("%Y-%m-%d")}
        got = latest_capture(url)
        rec["refused"] = got["refused"]
        rec["capture"] = got["capture"]
        if not rec["capture"] and not rec["refused"] and args.save:
            spn = save_page_now(url, wait=args.wait)
            rec["save_page_now"] = spn["outcome"]
            if spn.get("capture"):
                rec["capture"] = spn["capture"]
        if rec["capture"]:
            rec.update(read_capture(url, rec["capture"], mod))
        rec["verdict"] = verdict(rec)
        asked[url] = rec
        state_save(doc)
        print(f"  {i:>3}/{len(uniq)}  {rec['verdict']:<11} {url[:64]:<66} "
              f"{rec.get('outcome') or rec.get('refused') or rec.get('save_page_now', '')}")
    state_save(doc)
    return report(rows, doc)


def file_captures(rows: list[dict], doc: dict) -> int:
    """Every cleared and every empty-shell capture, into the sector index and the pass.

    THE INDEX RECORD CITES THE PUBLISHER. `url` is the original — that is what a row
    would cite and what check_links.py checks — and `read_url` is the Wayback URL this
    register actually read, with `archived` and `captured_at` saying it is a copy and
    whose. The empty shells are filed too, with `empty body` in the outcome: the next
    reader should be able to see that the archive was asked and what it held.
    """
    pas = json.loads(PASS.read_text(encoding="utf-8"))
    by_entry = {r["entry_id"]: r for r in rows}
    indexes, filed, touched = {}, 0, {}
    for url, rec in sorted(doc["asked"].items()):
        if not rec.get("capture") or not rec.get("sha256"):
            continue
        mod = __import__(READER[rec["sector"]])
        if mod.INDEX not in indexes:
            indexes[mod.INDEX] = (mod, json.loads(mod.INDEX.read_text(encoding="utf-8"))
                                  if mod.INDEX.exists() else {"_comment": [],
                                                              "fetches": []})
        _, idx = indexes[mod.INDEX]
        cap = rec["capture"]
        for entry_id in rec["entry_ids"]:
            row = by_entry.get(entry_id)
            entry = pas["entries"].get(entry_id)
            if row is None or entry is None:
                continue
            note = (f"browser queue archive pass, {entry_id}: the live URL "
                    f"{rec.get('outcome', '')} from a capture; queued because "
                    f"{row['reason'][:120]}")
            if not any(f.get("sha256") == rec["sha256"] and f.get("url") == url
                       for f in idx["fetches"]):
                idx["fetches"].append({
                    "url": url, "read_url": cap["read_url"],
                    "domain": urllib.parse.urlsplit(url).netloc,
                    "source_type": "company",
                    "date": rec.get("date") or cap["captured_at"],
                    "date_precision": rec.get("date_precision") or "not_after",
                    "captured_at": cap["captured_at"], "archived": True,
                    "http": None, "bytes": rec["bytes"], "sha256": rec["sha256"],
                    "text_chars": rec["text_chars"],
                    "outcome": f"archive capture, {rec['outcome']}",
                    "note": note})
            words = None
            if rec["text_chars"] >= READABLE:
                import research_pass as R
                words = R.names_it(mod.body_text(rec["sha256"]), entry)
            entry["searched"] = [g for g in entry["searched"]
                                 if g.get("sha256") != rec["sha256"]] + [{
                                     "url": url, "read_url": cap["read_url"],
                                     "archived": True,
                                     "captured_at": cap["captured_at"],
                                     "outcome": f"archive capture, {rec['outcome']}",
                                     "text_chars": rec["text_chars"],
                                     "sha256": rec["sha256"],
                                     "name_words_present": words}]
            entry["owner_page_names_it"] = any(g.get("name_words_present")
                                               for g in entry["searched"])
            entry["browser_queue"] = all(g["text_chars"] < READABLE
                                         for g in entry["searched"])
            touched[entry_id] = entry
            filed += 1
    for path, (_, idx) in indexes.items():
        path.write_text(json.dumps(idx, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    PASS.write_text(json.dumps(pas, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    left = sum(1 for v in pas["entries"].values() if v["browser_queue"])
    out = sum(1 for k in touched if not touched[k]["browser_queue"])
    print(f"\nqueue_archive_pass --write: {filed} capture(s) filed against "
          f"{len(touched)} entr(y/ies); {out} left the browser queue, {left} still in it.")
    print("  Then: python3 sources/research_pass.py --queue-csv   (rewrites the queue)")
    print("        python3 sources/research_pass.py --check        (rewrites the summary)")
    print("        python3 sources/check_fetch_records.py")
    return 0


def report(rows: list[dict], doc: dict) -> int:
    asked = doc["asked"]
    by_url = Counter(verdict(r) for r in asked.values())
    print(f"\n  BY URL ({len(asked)} asked)")
    for k in ("cleared", "empty shell", "no capture", "refused"):
        print(f"    {k:<12} {by_url.get(k, 0):>4}")
    # AND BY ENTRY, WHICH IS WHAT THE QUEUE IS MADE OF. An entry clears when ONE of its
    # URLs came back with a body; an entry all of whose URLs are shells stays.
    best = {}
    order = {"cleared": 3, "empty shell": 2, "refused": 1, "no capture": 0}
    for entry_id, _s, url in targets(rows):
        v = verdict(asked[url]) if url in asked else "not asked"
        if order.get(v, -1) >= order.get(best.get(entry_id, "not asked"), -1):
            best[entry_id] = v
    nourl = [r["entry_id"] for r in rows if not (r["urls_to_open"] or "").strip()]
    by_entry = Counter(best.get(r["entry_id"], "no URL to ask") for r in rows)
    print(f"\n  BY ENTRY ({len(rows)} in the queue, {len(nourl)} of them with no URL)")
    for k, n in by_entry.most_common():
        print(f"    {k:<16} {n:>4}")
    cleared = [e for e, v in sorted(best.items()) if v == "cleared"]
    if cleared:
        print(f"\n  CLEARED BY A CAPTURE — a copy on file, to be filed with --write:")
        for e in cleared:
            print(f"    {e}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true",
                    help="submit URLs with no capture to Save Page Now and poll")
    ap.add_argument("--write", action="store_true",
                    help="file what is already recorded; asks the archive nothing")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--again", action="store_true",
                    help="re-ask URLs already in the state file")
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--wait", type=int, default=90)
    ap.add_argument("--sector", default="")
    a = ap.parse_args()

    rows = queue_rows()
    doc = state_load()
    if a.write:
        return file_captures(rows, doc)
    if a.report:
        print(f"queue_archive_pass: {len(doc['asked'])} URL(s) asked of the archive.")
        return report(rows, doc)
    return ask(a)


if __name__ == "__main__":
    raise SystemExit(main())

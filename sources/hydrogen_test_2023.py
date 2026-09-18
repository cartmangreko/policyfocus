#!/usr/bin/env python3
"""THE ARCHIVE PASS OVER THE 2023 POPULATION, brief 13 item 2.

    python3 sources/hydrogen_test_2023.py --fetch [--limit N] [--offset N]
    python3 sources/hydrogen_test_2023.py --report

THE POPULATION IS THE LADDER'S, AS IT STOOD AT THE CUT-OFF: the 255 European entries at
100 MW and above in the October 2023 vintage, by IEA reference number. It is NOT the
cohort of brief 12 -- that was the 73 entries announced for 2023, at any size, and the two
populations barely meet. This one is the instrument's own population frozen at a past day,
which is what makes an as-of score over it a test of the instrument rather than of a
sample somebody drew.

WHAT IS FETCHED, AND WHY EACH LEG EXISTS. Every leg starts from a document the PUBLISHER
ITSELF cited or from a row this register already holds. Nothing here guesses a domain from
a project name: that is the error the machine-classification ruling was written for, and a
pass over 255 entries is exactly the scale at which it would be committed again.

    iea_reference            the entry's own `Refs` URLs, up to three. The IEA carries a
                             reference column into its References sheet, so every entry
                             arrives with the sources its publisher stood on.
    quality_check_reference  Odenweller and Ueckerdt's added reference where there is one,
                             with its reference date and its comment, cited by number.
    register_row_source      for an entry this register holds as a row, the row's own
                             sources -- which are the owner's pages, because that is what
                             admission required.
    host_root                the front page of a host the publisher cited that is not on
                             the press list below. An owner's own site as it stood before
                             the cut-off.
    host_newsroom            the newsroom of that same host, found by asking the CDX index
                             which paths under it were captured before the cut-off and
                             keeping those whose path carries a newsroom word. THE HOST
                             CAME FROM THE PUBLISHER'S CITATION AND THE PATH CAME FROM THE
                             INDEX; neither is a guess about who owns what.

ARCHIVE CAPTURES DATED AT OR BEFORE THE CUT-OFF ARE PREFERRED, on the ruling of 17
September 2026: for every URL the Wayback CDX index is asked for the LAST capture at or
before 2023-10-31, and where one exists that capture is what is read -- `captured_at` is
the capture's day, `archived` is true, and the document's own dateline still governs
`date`. Where none exists the live page is read and the record says so, and the as-of rule
then scores that cell `not_searched` rather than admitting a 2026 reading into a 2023
question.

NOTHING HERE WRITES A VERDICT. Every entry carries `verdict: null` until a person fills it
in. What the script computes is `signals`, and a signal is not a finding. The press list
below is a coarse label of the same kind: it decides whether a host is worth a second
request, and it NEVER decides whether a document counts -- that is read off the page.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import build_hydrogen_drift as drift  # noqa: E402
import hydrogen_cohort_census as census  # noqa: E402
import hydrogen_search as hs  # noqa: E402

ROOT = bench.ROOT
OUT = ROOT / "sources" / "hydrogen_test_2023.json"
VINTAGE = census.VINTAGE

# THE POPULATION, MATERIALISED AND TRACKED. The workbooks are gitignored -- they are
# Odenweller and Ueckerdt's bytes and this repository is not licensed to redistribute
# them -- and openpyxl is not in the build image. A gate that read them therefore
# passed locally and failed on Vercel, which is what happened at d96903a.
#
# SO THE WORKBOOK IS READ ONCE, HERE, AND WRITTEN DOWN. The derived file carries the
# 255 entries and the sha256 of every workbook they came from, so a reader can prove
# which bytes produced it without holding those bytes. See scope.md, "A build-time
# gate reads tracked files only".
POPULATION_OUT = ROOT / "sources" / "hydrogen_test_2023_population.json"
CUTOFF = "2023-10-31"
MAX_REFS = 3
MAX_OWNER_HOSTS = 2

# THE WAITING IS OVERLAPPED AND THE PACE IS NOT CHANGED. Ruled and recorded 17 September
# 2026 as D-C5. Sequentially this pass ran at 150 seconds an entry, nine and a half hours
# for the population, and almost all of it was one worker WAITING: a CDX lookup takes
# eight to fourteen seconds of somebody else's server thinking, and the register's own
# two-second pause is on top of that. Threads do not make the requests come faster; they
# make the idle time of one request coincide with the idle time of another. Every worker
# still waits PAUSE after its own fetch, so the request rate to the archive stays where
# the declared reader set it, and the cache index is written under a lock because a fetch
# that happened and is not in the index is the one failure this whole apparatus exists to
# prevent.
DEFAULT_WORKERS = 6

_HOST_LOCK = threading.Lock()
_HOST_LOCKS: dict[str, threading.Lock] = {}
_DOC_LOCK = threading.Lock()

# A COARSE LABEL AND NOT A VERDICT, written by hand and kept here where it can be read in
# a diff. IT WAS WRONG TWICE ON THE FIRST WRITING, and the corrections are the argument for
# keeping it where a diff can find it: `h2v.net` is the developer H2V's own site -- "H2V
# investit, developpe et construit des gigafactory" -- and `www.smartenergy.net` is
# Smartenergy's, the developer of the Valencia project, and both were listed here as trade
# press. Thirteen entries cite the first and two the second, and each of them lost its
# host legs to the mistake until they were re-fetched. A hand list of hosts is exactly as
# fallible as the classifier ruling of 10 September 2026 says a machine's guess is; what
# makes it acceptable is that it is short, it is read by a person, and it is in the diff. A host on this list is a wire, a trade title, a newspaper, an aggregator or a
# search engine: its front page and its newsroom say nothing about any one project, so no
# second request is spent on them. THE ENTRY'S OWN REFERENCE IS STILL FETCHED whatever the
# host, because the publisher cited it and what it says is a question for the reading.
PRESS_HOSTS = {
    "direct.argusmedia.com", "www.argusmedia.com", "fuelcellsworks.com",
    "www.h2-view.com", "www.rechargenews.com", "renewablesnow.com", "www.spglobal.com",
    "www.reuters.com", "www.wsj.com", "www.ft.com", "www.barrons.com",
    "hydrogen-central.com", "www.hydrogeninsight.com", "www.hydrogenfuelnews.com",
    "www.greencarcongress.com", "www.greentechmedia.com", "energynews.biz",
    "www.energynews.es", "renews.biz", "www.renews.biz", "bioenergyinternational.com",
    "balkangreenenergynews.com", "www.offshore-energy.biz", "www.offshorewind.biz",
    "www.offshore-mag.com", "www.eleconomista.es", "www.europapress.es",
    "cincodias.elpais.com", "sevilla.abc.es", "www.heraldo.es", "www.hispanidad.com",
    "www.lavozdeasturias.es", "www.lavozdegalicia.es", "elperiodicodelaenergia.com",
    "www.energias-renovables.com", "www.independent.ie", "www.japantimes.co.jp",
    "www.euractiv.com", "www.usinenouvelle.com", "www.constructioncayola.com",
    "www.euro-petrole.com", "www.finanztreff.de", "www.energate-messenger.com",
    "www.enerdata.net", "reneweconomy.com.au", "thewest.com.au", "ijglobal.com",
    "renewable-carbon.eu", "www.h2-mobile.fr", "www.hydroreview.com", "w3.windfair.net",
    "news.cision.com", "www.epressi.com", "www.google.com",
    "web.archive.org", "static1.squarespace.com", "assets.ey.com", "ir.q4europe.com",
}

# The path words a newsroom is published under, in the languages this population is
# published in. A path is kept only if the CDX index actually captured it before the
# cut-off, so the list proposes and the index disposes.
NEWSROOM_WORDS = ("news", "press", "media", "newsroom", "presse", "aktuelles",
                  "actualites", "actualité", "noticias", "prensa", "nieuws",
                  "pressemeddelelser", "nyheder", "notizie", "comunicati")

CDX = census.CDX


def population() -> list[dict]:
    """The 255, with everything the October 2023 vintage says about each.

    READS THE TRACKED DERIVED FILE where it exists, which is everywhere the repository
    is checked out, and the workbook only when it does not. NOTHING IN THE BUILD CHAIN
    REACHES THE WORKBOOK THROUGH THIS FUNCTION: on a build image the derived file is
    present and openpyxl is not, and the fallback is for a machine that has just
    deleted the derived file and still has the workbook to rebuild it from.
    """
    if POPULATION_OUT.exists():
        return json.loads(POPULATION_OUT.read_text(encoding="utf-8"))["entries"]
    return population_from_workbook()


def workbook_sources() -> list[dict]:
    """Every workbook the population is read from, by name, size and sha256.

    RECORDED INSIDE THE DERIVED FILE so that the identity travels with the data. The
    bytes cannot be committed; the hash can, and it is what lets anybody fetch the
    same workbook from the authors and prove it is the one these 255 rows came from.
    """
    import hashlib
    out = []
    for path in (VINTAGE,):
        if not path.exists():
            continue
        body = path.read_bytes()
        out.append({"file": path.name, "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest()})
    return out


def write_population() -> int:
    """Materialise the population. Called by the build script WHEN THE WORKBOOKS ARE
    PRESENT, and never otherwise -- a machine without them leaves the tracked file
    exactly as it found it rather than writing an empty one over it."""
    if not VINTAGE.exists():
        return 0
    entries = population_from_workbook()
    POPULATION_OUT.write_text(json.dumps({
        "_comment": [
            "THE OCTOBER 2023 POPULATION, MATERIALISED FROM THE WORKBOOK. Derived and",
            "tracked: written by build_hydrogen_test.py where the workbooks are on the",
            "machine, read by everything else.",
            "",
            "WHY IT EXISTS. The workbooks are gitignored, being Odenweller and",
            "Ueckerdt's bytes, and openpyxl is not installed in the build image. The",
            "production build failed at d96903a because check_hydrogen_test.py read",
            "them through this module. A build-time gate reads tracked files only;",
            "anything needing openpyxl or a cache body runs in the local pre-push",
            "chain. See scope.md.",
            "",
            "`sources` below is the identity of the workbooks these rows came from.",
            "The bytes are not redistributable; the hash is, and it is what makes the",
            "derivation checkable. check_hydrogen_workbook.py, which runs locally and",
            "never in the build, recomputes these rows and refuses a mismatch.",
        ],
        "entries_count": len(entries),
        "sources": workbook_sources(),
        "entries": entries,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(entries)


def population_from_workbook() -> list[dict]:
    """The 255, read from the workbook itself. NEEDS openpyxl AND the gitignored
    bytes, so it runs locally and never in the build chain."""
    refs, qc = census.sheets(VINTAGE)
    out = []
    for r in drift.load_workbook_projects(VINTAGE):
        if r["Country"] not in bench.GEO:
            continue
        if (drift._f(r["Capacity_MWel"]) or 0) < 100:
            continue
        if r["Ref"] == "0":
            continue
        ids = re.findall(r"\[(\d+)\]", str(r["Refs"] or ""))
        qids = re.findall(r"\[(\d+)\]", str(r["Refs (quality check)"] or ""))
        out.append({
            "ref": r["Ref"], "name": str(r["Project name"] or ""),
            "country": r["Country"],
            "status_2023_vintage": str(r["Status"] or ""),
            "date_online_2023_vintage": str(r["Date online"] or "").strip(),
            "technology": str(r["Technology"] or ""),
            "announced_size": str(r["Announced Size"] or ""),
            "capacity_mwel": drift._f(r["Capacity_MWel"]),
            "capacity_kth2y": drift._f(r["Capacity_ktH2Y"]),
            "iea_reference_numbers": ids,
            "iea_references": [refs.get(i, "") for i in ids],
            "quality_check_reference_numbers": qids,
            "quality_check_references": [dict(qc.get(i, {}), number=i) for i in qids],
        })
    return out


def cdx(params, timeout=90, tries=4):
    """One CDX request, with a backoff. THE INDEX RATE-LIMITS AND IT SAYS SO WITH A 503,
    and a pass that read a 503 as "no capture" would record a silence the archive never
    uttered -- the refusal ruling, one layer down. Exhausted retries return None, which
    the callers write down as a refusal rather than as an absence."""
    import time
    url = CDX + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": hs.UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace") or "[]")
        except Exception:                                      # noqa: BLE001
            if i == tries - 1:
                return None
            time.sleep(4 * (i + 1))
    return None


# THE NEWSROOM IS ASKED FOR BY PATH, ONE PREFIX QUERY PER WORD, and not by scanning a
# host. The first form of this query asked the CDX index to regex the whole of a host's
# captures and took 160 seconds on rwe.com; asking `host/news` as a prefix takes three.
# A word here PROPOSES a path and the index DISPOSES of it: nothing is recorded unless the
# archive actually holds a capture of that path at or before the cut-off, so the list can
# be generous without asserting anything. The host itself came from the publisher's own
# citation, which is the part that must not be guessed.
NEWSROOM_PATHS = ("news", "press", "media", "newsroom", "presse", "noticias")

# THE PREFIX SWEEP IS TWO WORDS, NOT SIX, AND THE REASON IS COST. Each word is a
# request to an index that rate-limits, and the first form of this pass spent ninety
# seconds a host on six of them. The citation-derived hint above answers most hosts in
# one request; the sweep is the fallback, and it asks the two words that carry a
# newsroom in this population and lets the rest go unfound rather than unpaced.
SWEEP_PATHS = ("news", "press")


def is_newsroom_segment(seg: str) -> bool:
    """`news`, `news-stories`, `press_releases` -- a newsroom word at the head of a path
    segment. A word INSIDE a segment does not count: `newspaper-mill` is not a newsroom,
    and neither is an image called `dest_PR_media.jpg`."""
    s = seg.lower()
    return any(s == w or s.startswith(w + "-") or s.startswith(w + "_")
               for w in NEWSROOM_PATHS)


def cdx_paths(host: str, cutoff: str = CUTOFF, limit: int = 50):
    """Newsroom-shaped paths under a host captured at or before the cut-off.

    Returns (rows, refused): `refused` is true where the index would not answer, which is
    a measurement of the request and not a statement that the host has no newsroom.
    """
    out, refused = [], False
    for word in SWEEP_PATHS:
        rows = cdx([("url", f"{host}/{word}"), ("matchType", "prefix"),
                    ("output", "json"), ("fl", "timestamp,original"),
                    ("filter", "statuscode:200"),
                    ("to", cutoff.replace("-", "") + "235959"),
                    ("collapse", "urlkey"), ("limit", str(limit))])
        if rows is None:
            refused = True
            continue
        out += [{"timestamp": x[0], "original": x[1]}
                for x in rows if x and x[0] != "timestamp"]
    return out, refused


AVAIL = "https://archive.org/wayback/available"


def availability_before(url: str, cutoff: str = CUTOFF):
    """THE FAST ROUTE TO THE SAME CAPTURE, and it is the same capture for a reason worth
    stating. The availability endpoint answers in about a second where the CDX index takes
    twelve, and what it returns is the capture CLOSEST to the timestamp asked for. Ask it
    for the cut-off and, IF the answer is dated at or before the cut-off, that answer is
    necessarily the LAST capture at or before it -- any later one on the right side of the
    cut-off would have been closer. So this is not a different rule read faster; it is the
    same rule.

    A MISS PROVES NOTHING AND IS NOT RECORDED AS ONE. The endpoint returns an empty
    `archived_snapshots` for URLs the CDX index does answer for -- gasunie.nl's own news
    page among them -- so an empty answer, or an answer dated after the cut-off, falls
    through to the index. Two shapes of request, and a conclusion only from the one that
    can support it: scope.md, "A refusal is a measurement of a request, not of a
    publisher".
    """
    q = urllib.parse.urlencode({"url": url,
                                "timestamp": cutoff.replace("-", "") + "235959"})
    try:
        req = urllib.request.Request(AVAIL + "?" + q, headers={"User-Agent": hs.UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            doc = json.loads(r.read().decode("utf-8", "replace") or "{}")
    except Exception:                                          # noqa: BLE001
        return None
    snap = ((doc.get("archived_snapshots") or {}).get("closest") or {})
    ts = str(snap.get("timestamp") or "")
    if not snap.get("available") or str(snap.get("status")) != "200" or len(ts) < 8:
        return None
    day = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"
    if day > cutoff:
        return None
    return {"timestamp": ts, "captured_at": day,
            "url": f"https://web.archive.org/web/{ts}/{url}"}


def wayback_before(url: str, cutoff: str = CUTOFF):
    """The LAST capture at or before the cut-off, or None; None also where the index
    refused, and the caller records which."""
    fast = availability_before(url, cutoff)
    if fast:
        return fast
    rows = cdx([("url", url), ("output", "json"), ("fl", "timestamp,original"),
                ("filter", "statuscode:200"),
                ("to", cutoff.replace("-", "") + "235959"), ("limit", "-1")])
    if not rows:
        return None
    rows = [x for x in rows if x and x[0] != "timestamp"]
    if not rows:
        return None
    ts = rows[-1][0]
    return {"timestamp": ts, "captured_at": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}",
            "url": f"https://web.archive.org/web/{ts}/{rows[-1][1]}"}


def newsroom_hints(urls) -> list[str]:
    """The newsroom a cited URL is already standing in, read off its own path.

    THE BEST CANDIDATE IS IN THE CITATION. Gasunie's reference is
    `gasunie.nl/en/news/europes-largest-green-hydrogen-project`, so its newsroom is
    `gasunie.nl/en/news/` -- and the prefix queries below never found it, because they ask
    for `host/news` and this one is language-prefixed. Truncating a cited URL at its own
    newsroom segment is not a guess about the host: the publisher put the path there.
    """
    out = []
    for u in urls:
        parts = urllib.parse.urlsplit(u)
        segs = [s for s in parts.path.split("/") if s]
        for i, s in enumerate(segs):
            if is_newsroom_segment(s) and i < len(segs) - 1:
                cand = f"{parts.scheme}://{parts.netloc}/" + "/".join(segs[:i + 1]) + "/"
                if cand not in out:
                    out.append(cand)
                break
    return out


def newsroom_of(host: str, cutoff: str = CUTOFF, hints=()):
    """The shallowest captured newsroom path under a host, at its last pre-cut-off
    capture, or None.

    SHALLOWEST, because `/news` is the newsroom and `/news/2019/some-release` is one
    release in it, and what this leg is for is the page that lists what the owner said.
    THE CITATION'S OWN PATH IS TRIED FIRST, per `newsroom_hints`.
    """
    for cand in hints:
        cap = wayback_before(cand, cutoff)
        if cap:
            return {**cap, "original": cand}
    rows, refused = cdx_paths(host, cutoff)
    best = None
    for row in rows:
        path = urllib.parse.urlsplit(row["original"]).path.lower().strip("/")
        segs = [s for s in path.split("/") if s]
        if not segs or "." in segs[-1]:
            continue
        if not any(is_newsroom_segment(s) for s in segs):
            continue
        depth = len(segs)
        if best is None or depth < best[0]:
            best = (depth, row)
    if best is None:
        return None if not refused else {"refused": True}
    cap = wayback_before(best[1]["original"], cutoff)
    ts = (cap or {}).get("timestamp") or best[1]["timestamp"]
    return {"timestamp": ts, "captured_at": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}",
            "url": (cap or {}).get("url")
                   or f"https://web.archive.org/web/{ts}/{best[1]['original']}",
            "original": best[1]["original"]}


# A URL THAT IS ALREADY A CAPTURE CARRIES ITS OWN DATE, AND THE FIRST FORM OF THIS PASS
# THREW IT AWAY. The register stores a source as a Wayback URL wherever the publisher went
# dark after the page was read -- scope.md, "When a publisher goes dark after a page was
# read, cite the capture" -- so seven of the row-source legs arrive as
# web.archive.org/web/<timestamp>/<original>. Asking the CDX index for a capture OF a
# capture finds nothing, so those legs were read live and recorded `archived: false` with
# no `captured_at`, and the as-of rule then scored them out of the table although the
# document on file is demonstrably a copy taken before the cut-off. The timestamp is in
# the URL; it is read from there.
CAPTURE_URL = re.compile(r"^https?://web\.archive\.org/web/(\d{14})(?:[a-z_]+)?/(.*)$")


def already_a_capture(url: str):
    m = CAPTURE_URL.match(url)
    if not m:
        return None
    ts = m.group(1)
    return {"timestamp": ts, "captured_at": f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}", "url": url}


def read(url: str, leg: str, note: str, name: str, prefer_capture: bool = True) -> dict:
    """One leg: the pre-cut-off capture where there is one, the live page where not."""
    cap = already_a_capture(url)
    if cap is None:
        cap = wayback_before(url) if prefer_capture else None
    elif cap["captured_at"] > CUTOFF:
        cap = None
    target, archived, captured_at = url, False, ""
    if cap:
        target, archived, captured_at = cap["url"], True, cap["captured_at"]
    rec = hs.fetch(target, census.source_type(url), note)
    txt = hs.body_text(rec["sha256"]) if rec["sha256"] else ""
    stem = [w for w in re.sub(r"[^a-z0-9 ]", " ", name.lower()).split() if len(w) > 4][:3]
    return {
        "leg": leg, "reference_url": url, "read_url": target, "archived": archived,
        "captured_at": captured_at, "http": rec["http"], "outcome": rec["outcome"],
        "sha256": rec["sha256"], "text_chars": rec["text_chars"],
        "source_type": rec["source_type"], "host": urllib.parse.urlsplit(url).netloc.lower(),
        "signals": {"contains_a_name_word": bool(stem) and all(w in txt.lower()
                                                               for w in stem)},
    }


def row_sources(ref: str, rows_by_ref: dict) -> list[str]:
    row = rows_by_ref.get(ref)
    if not row:
        return []
    return [s["url"] for s in (row.get("sources") or []) if s.get("url")][:MAX_REFS]


def host_legs(host: str, doc: dict, hints=()) -> list[dict]:
    """The front page and the newsroom of one host, fetched ONCE for the whole pass.

    A HOST IS NOT AN ENTRY. Nine entries cite topsectorenergie.nl and five cite
    iberdrola.com, and fetching the same front page nine times would spend an hour of
    somebody else's bandwidth to put the same bytes in the cache under the same hash. So
    the host legs live in `hosts` on this file, keyed by host, and an entry's `host_legs`
    names which hosts it drew on.
    """
    cached = doc.setdefault("hosts", {})
    if host in cached:
        return cached[host]["legs"]
    # ONE HOST IS RESOLVED ONCE EVEN WITH SIX WORKERS. Without this, two entries citing
    # the same host would both resolve it, spend the requests twice and race on the dict.
    with _HOST_LOCK:
        lock = _HOST_LOCKS.setdefault(host, threading.Lock())
    with lock:
        if host in cached:
            return cached[host]["legs"]
        return _host_legs_uncached(host, cached, hints)


def _host_legs_uncached(host: str, cached: dict, hints=()) -> list[dict]:
    legs = [read(f"https://{host}/", "host_root",
                 f"2023 population test: the front page of a host the publisher cited, "
                 f"as captured at or before {CUTOFF}", "")]
    nr = newsroom_of(host, hints=hints)
    if nr and not nr.get("refused"):
        rec = hs.fetch(nr["url"], census.source_type(nr["original"]),
                       f"2023 population test: the newsroom the CDX index holds under "
                       f"{host} at or before {CUTOFF}")
        legs.append({
            "leg": "host_newsroom", "reference_url": nr["original"],
            "read_url": nr["url"], "archived": True, "captured_at": nr["captured_at"],
            "http": rec["http"], "outcome": rec["outcome"], "sha256": rec["sha256"],
            "text_chars": rec["text_chars"], "source_type": rec["source_type"],
            "host": host, "signals": {}})
    else:
        legs.append({
            "leg": "host_newsroom", "reference_url": f"https://{host}/", "read_url": "",
            "archived": False, "captured_at": "", "http": None,
            "outcome": ("the CDX index would not answer for this host"
                        if nr and nr.get("refused")
                        else f"no newsroom path in the CDX index at or before {CUTOFF}"),
            "sha256": "", "text_chars": 0, "source_type": "unclassified",
            "host": host, "signals": {}})
    with _DOC_LOCK:
        cached[host] = {"legs": legs, "resolved_on": legs[0].get("captured_at") or ""}
    return legs


def fetch_entry(e: dict, rows_by_ref: dict, doc: dict) -> dict:
    urls = [(u, "iea_reference") for u in e["iea_references"]
            if u.lower().startswith("http")][:MAX_REFS]
    urls += [(q["url"], "quality_check_reference") for q in e["quality_check_references"]
             if q.get("url", "").lower().startswith("http")
             and q["url"] not in [u for u, _ in urls]]
    urls += [(u, "register_row_source") for u in row_sources(e["ref"], rows_by_ref)
             if u not in [x for x, _ in urls]]
    got = []
    for u, leg in urls:
        got.append(read(u, leg, f"2023 population test, IEA ref {e['ref']}: {leg}, "
                                f"Wayback capture at or before {CUTOFF} where one exists",
                        e["name"]))

    hosts, seen = [], set()
    for u, _leg in urls:
        h = urllib.parse.urlsplit(u).netloc.lower()
        if h and h not in seen and h not in PRESS_HOSTS:
            seen.add(h)
            hosts.append(h)
    hosts = hosts[:MAX_OWNER_HOSTS]
    cited = [u for u, _l in urls]
    for h in hosts:
        host_legs(h, doc, hints=[c for c in newsroom_hints(cited)
                                 if urllib.parse.urlsplit(c).netloc.lower() == h])

    http_refs = [u for u in e["iea_references"] if u.lower().startswith("http")]
    return {**e, "fetches": got, "host_legs": hosts,
            # SAID RATHER THAN HIDDEN. Three references an entry is the cap the cohort
            # census set, and six entries in this population carry more; the count of
            # what was left unread is on the line so a reader is not told that three is
            # all there was.
            "iea_references_not_read": max(0, len(http_refs) - MAX_REFS),
            "any_pre_cutoff_document": any(
                g["archived"] and g["captured_at"] and g["captured_at"] <= CUTOFF
                and g["text_chars"] >= 400 for g in got),
            # FILLED IN BY A PERSON, from the pages above. Null is the honest value until
            # somebody has read them: `owner_or_permit_pre_cutoff` is the coverage flag
            # the brief asks for and it is a judgement about who is speaking, which no
            # host list can make.
            "owner_or_permit_pre_cutoff": None, "owner_or_permit_url": None,
            "names_site": None, "site_named": None, "site_speaker": None,
            "site_fetch_url": None, "site_captured_at": None, "site_archived": None,
            "verdict": None}


def load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"_comment": __doc__.strip().split("\n"), "cutoff": CUTOFF,
            "hosts": {}, "entries": []}


def save(doc):
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# THE TWO BENCHMARK KEYS ARE ONE NUMBERING. The register files an IEA reference under
# `odenweller_ueckerdt_2025` for the October 2023 vintage and under
# `iea_hydrogen_production_projects` for the current one, and scope.md's "One benchmark in
# two vintages" says they are the same numbering. A row is matched on either.
BENCHMARK_KEYS = ("odenweller_ueckerdt_2025", "iea_hydrogen_production_projects")


def register_rows_by_ref() -> dict:
    """{IEA reference: row} for the rows this register holds, over both benchmark keys."""
    import sector_map as sm
    out = {}
    for row in sm.load("project"):
        if row.get("sector") != "clean":
            continue
        for key in BENCHMARK_KEYS:
            for x in bench.as_list((row.get("benchmarks") or {}).get(key)):
                out.setdefault(str(x), row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    a = ap.parse_args()

    doc = load()
    done = {e["ref"] for e in doc["entries"]}
    all_ = population()
    if a.fetch:
        rows_by_ref = register_rows_by_ref()
        todo = [e for e in all_ if e["ref"] not in done][a.offset:a.offset + a.limit]
        order = {e["ref"]: i for i, e in enumerate(all_)}
        print(f"2023 population test: {len(all_)} entries, {len(done)} already on file, "
              f"{len(todo)} this batch, {a.workers} worker(s)")
        counter = {"n": 0}

        def one(e):
            rec = fetch_entry(e, rows_by_ref, doc)
            with _DOC_LOCK:
                doc["entries"].append(rec)
                # THE FILE STAYS IN POPULATION ORDER whatever order the workers finish in,
                # so a diff of it reads as a diff and not as a shuffle.
                doc["entries"].sort(key=lambda x: order.get(x["ref"], 10 ** 6))
                save(doc)
                counter["n"] += 1
                n = counter["n"]
            ok = sum(1 for g in rec["fetches"] if g["text_chars"] >= 400)
            arch = sum(1 for g in rec["fetches"]
                       if g["archived"] and g["captured_at"] <= CUTOFF)
            print(f"  {n:>3}/{len(todo)} ref {e['ref']:>5} {e['name'][:38]:40} "
                  f"{len(rec['fetches'])} fetched, {ok} readable, {arch} from a capture "
                  f"at or before {CUTOFF}", flush=True)

        if a.workers <= 1:
            for e in todo:
                one(e)
        else:
            with ThreadPoolExecutor(max_workers=a.workers) as pool:
                list(pool.map(one, todo))
        return 0

    n = len(doc["entries"])
    pre = sum(1 for e in doc["entries"] if e["any_pre_cutoff_document"])
    print(f"2023 population test: {n} of {len(all_)} entries searched; {pre} have at "
          f"least one readable document captured on or before {CUTOFF}.")
    print(f"  fetches: {sum(len(e['fetches']) for e in doc['entries'])}")
    print(f"  coverage flags written by a person: "
          f"{sum(1 for e in doc['entries'] if e['owner_or_permit_pre_cutoff'] is not None)}")
    print(f"  site verdicts written by a person:  "
          f"{sum(1 for e in doc['entries'] if e['verdict'] is not None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

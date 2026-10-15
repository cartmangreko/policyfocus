"""
Every outbound URL in the transition layer still resolves.

    python3 check_links.py                 # exits non-zero on a dead link
    python3 check_links.py --offline       # inventory only; no network, no pass

The layer's whole claim is that each figure on a sector page walks back to
somebody's published sentence. A 404 breaks that claim silently: the page still
renders, the citation still looks like a citation, and the sentence it points at
is gone. So the links are checked, and a dead one fails the build.

ARCHIVED LINKS. A source that has gone off the web is not a data error -- it is
the ordinary fate of company press releases. Such a source carries
`archived: true` and a `snapshot` path into this repository, and is reported
rather than fetched. That is the same discipline the register uses for act
texts: the fetched version is kept, so the claim survives the publisher.

WHAT IS AND IS NOT A FAILURE
  4xx                     failure. The page is gone or refuses us by URL.
  429, after a retry      reported, not failed. A rate limiter says NOT NOW; it
                          does not say the page is not there, and it is answering
                          about the request rather than about the URL. The build
                          of 21 September 2026 failed on a trade title's 429 that
                          the same request got a 200 from on a developer machine
                          twenty minutes earlier — a gate that fails on that makes
                          the build depend on whose IP asked. Retried once with a
                          pause first, because a rate limiter usually relents and
                          a page that is really gone will not.
  5xx, timeout, DNS       reported, not failed. A publisher's bad afternoon is
                          not a defect in this repository, and failing on it
                          would make the build depend on other people's uptime.
  403 from a known
  bot-hostile publisher   reported, not failed, and listed by name below. A CDN
                          blocking a datacentre IP tells us nothing about
                          whether the page exists.
  4xx with a recorded
  `refusal`               reported, not failed. The row records that this
                          pipeline observed the publisher refusing to serve
                          the page, on a stated day, with the code it
                          answered. It accepts only that code, it prints the
                          date on every run, and it carries no claim that the
                          document is still there — see OBSERVED_REFUSAL.
  404 inside a section
  that declares itself
  under maintenance       reported, not failed. A publisher whose own section
                          index redirects to a maintenance page, or answers 503,
                          is making a statement about that section; the 404s
                          inside it are that statement and not a removed page.
                          Asked of the path the page sits under rather than of
                          the page, for the same reason the 429 is asked twice,
                          and it fails again the day the section is back. See
                          section_in_maintenance.

Requests are sequential and slow on purpose: this is a gate that runs at build,
against a few dozen URLs, and hammering a trade-press site to save nine seconds
would be a good way to earn a permanent block.

STANDARD LIBRARY ONLY, like every other gate in the prebuild chain. This one
used `requests` and was the single exception, which held until the chain ran
somewhere that installs Node dependencies and not Python ones: the deployment
build failed on ModuleNotFoundError after every other gate had passed. The
fetching this does is a GET with a header and a timeout, which urllib does, so
the dependency bought nothing and cost a build. sources/requirements.txt still
lists requests for the fetcher, which runs on a machine where someone has
installed it.
"""

from __future__ import annotations

import argparse
import json
import datetime as dt
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

import sector_map as sm

TIMEOUT = 20
# How long to wait before asking a rate limiter a second time. Long enough that a
# per-minute window has moved on, short enough that a build does not notice.
RATE_LIMIT_RETRY_PAUSE = 8
# A DECLARED IDENTITY WITH A CONTACT ADDRESS, because several publishers require
# one and are right to. The SEC's fair-access policy is explicit: an automated
# reader states who it is and how to reach it, and anything that does not gets a
# 403 whatever it asks for. The address is the platform's own, not a person's.
#
# THE `Mozilla/5.0 (compatible; …)` WRAPPER IS THE CONVENTION AND NOT A DISGUISE.
# It is the form Googlebot and every other well-behaved crawler uses, and the
# thing inside the parentheses is the whole identity: a name, a URL and an
# address. What it is NOT is the previous string, which opened with the same
# token and then said nothing a publisher could contact. That one got past
# filters by looking like a browser, which is a thing to stop doing rather than a
# feature to keep — and stopping cost three citations that now report as 403,
# recorded below rather than quietly recovered by wearing a browser's name.
UA = ("Mozilla/5.0 (compatible; Eufabric/1.0; "
      "+https://www.eufabric.eu; data@eufabric.eu)")

# Hosts that answer a datacentre IP with 403 whatever the URL. A 403 from these
# is reported, never failed. Anything not on this list that 403s IS a failure,
# so the list stays short and each entry is added deliberately.
BOT_HOSTILE = {
    "www.weforum.org",
    "reports.weforum.org",
    "tradingeconomics.com",
    "www.iea.org",
    # Added with the batteries dataset. Each of these serves the document to a
    # browser and 403s a datacentre IP, which is why sources/manual/ exists: the
    # row cites the publisher's live URL, a person retrieves the page, and the
    # copy they read is filed with its provenance. A 403 here is a fact about
    # how we are reaching the page and not about whether the page is there.
    # SURFACED BY DECLARING OURSELVES HONESTLY. These two answered the old
    # string, which opened with a bare "Mozilla/5.0" and named nobody; they
    # refuse a User-Agent that says what it is. They are here rather than on
    # `refused_declared_reader` for one reason: that state carries the date a
    # PERSON last opened the page, and nobody has opened these. They belong on
    # it the moment somebody does. See the note under REFUSED_STATE.
    "www.globalcement.com",
    "www.stellantis.com",
    # ADDED 19 SEPTEMBER 2026, and it is not this branch's. project[47] has cited
    # this page since the batteries census and check_links passed on it as recently
    # as the steel chain on 18 September; on 19 September it answers HTTP 403 to the
    # declared reader from Apache, with no CDN header — the publisher's own server
    # refusing, the same shape as the two above. NO ROW WAS EDITED HERE AND NOTHING
    # WAS RE-READ: the citation stands, the 403 is a fact about how this register
    # reaches the page, and it moves to `refused_declared_reader` with a date the
    # moment a person opens it.
    "www.elektroniknet.de",
    # ADDED 12 OCTOBER 2026, and like the entry above it this is not the
    # branch's own doing. Two Lyten press releases are cited by the batteries
    # rows that record the Northvolt acquisitions; both answer HTTP 403 from
    # CLOUDFLARE, and they answer it to a browser User-Agent exactly as they
    # answer it to the declared reader. That is a CDN refusing this address, not
    # a publisher refusing this reader and not a page that has gone -- which is
    # the case this list is for, and the reason it is this list rather than
    # `refused_declared_reader`: that state carries the day a PERSON opened the
    # page, and nobody has opened these. NO ROW WAS EDITED AND NOTHING WAS
    # RE-READ. They move to the recorded state the moment somebody opens them.
    "lyten.com",
}

# A SECTION IN MAINTENANCE IS NOT A PAGE THAT HAS BEEN REMOVED
# ============================================================
# A 404 means "gone", and that is why it fails: the sentence a figure walks back
# to is not there any more. It means something else when the publisher has taken
# the section down. co2llect.de is the case this was written from: every path
# under /en/ answers 404, and /en/ ITSELF REDIRECTS to /en/maintenance, while the
# German root serves normally. The page has not been removed -- its whole
# language section is being worked on -- and the 404 will stop without anybody
# editing anything.
#
# THIS IS THE 429 RULE APPLIED TO A SECOND CODE. A 429 is reported rather than
# failed because it is about the request and not the resource, and the way the
# two are told apart is to ASK AGAIN -- a rate limiter relents, a page that has
# gone answers the same way all day. Here the second question is asked of the
# PATH THE PAGE SITS UNDER instead of the page: if the section announces
# maintenance, the 404s inside it are that announcement.
#
# IT WALKS UP, which is what makes it work on a site that is only partly down.
# /en/project/ asks /en/ and then /, and stops at the first answer. A whole-host
# outage is the case where the last step answers; co2llect is the case where the
# first one does, and asking only the root would have missed it.
#
# NARROW, EVIDENCED AND SELF-CLEARING, which is what keeps it from becoming a
# way of passing dead links. It fires only on an explicit statement by the
# publisher about itself -- a redirect to a path saying maintenance, or a 503 --
# never on a guess from a body; it is REPORTED rather than silent, with the
# evidence printed; and the day the section comes back a genuinely dead page
# fails again. At most a handful of extra requests, and only for a URL that has
# already 404ed.
MAINTENANCE_MARKERS = ("maintenance", "wartung", "under-construction", "under-maintenance")
_section_state: dict[str, str | None] = {}


def _probe_section(url: str) -> str | None:
    """One ancestor path's own statement about itself, or None."""
    if url in _section_state:
        return _section_state[url]
    verdict: str | None = None
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            landed = r.geturl()
            if any(m in landed.lower() for m in MAINTENANCE_MARKERS):
                verdict = f"{url} redirects to {landed}"
    except urllib.error.HTTPError as exc:
        if exc.code == 503:
            verdict = f"{url} answers HTTP 503"
    except OSError:
        verdict = None
    _section_state[url] = verdict
    return verdict


def section_in_maintenance(url: str) -> str | None:
    """The publisher's own statement that the section this URL sits in is down,
    or None. Returns the EVIDENCE rather than a boolean, because a downgrade
    from a failure to a report has to be able to say what it rests on."""
    parts = urlparse(url)
    segments = [p for p in parts.path.split("/") if p]
    # The immediate parent first, then outwards to the root.
    for cut in range(len(segments) - 1, -1, -1):
        prefix = "/".join(segments[:cut])
        ancestor = f"{parts.scheme}://{parts.netloc}/" + (f"{prefix}/" if prefix else "")
        verdict = _probe_section(ancestor)
        if verdict:
            return verdict
    return None

# THE RECORDED STATE FOR A PUBLISHER THAT REFUSES A DECLARED READER
# =================================================================
# A host list says "requests from here fail" and nothing else. It cannot say
# whether the page is still there, and it quietly converts an unverified claim
# into a permanent green line — which is the failure mode a link checker exists
# to prevent, arriving through the back door.
#
# So a source may instead carry, beside its url:
#
#     "refused_declared_reader": {
#         "last_verified": "2026-09-03",
#         "by": "George Christopoulos",
#         "note": "why the refusal is the publisher's policy and not a dead page"
#     }
#
# and that is a stronger claim than a host list, not a weaker one. It says a
# named person opened this exact URL on a stated day and found the document
# there. `last_verified` is REQUIRED — a state that could be claimed without one
# would be the host list again, wearing a better name.
#
# THE HONEST DEGRADED STATE IS THIS PLUS A FILED COPY. Where the row also carries
# `retrieved_manually`, the chain is complete: the publisher's own URL for the
# claim, a person's word that it resolves, and the text that was actually read
# sitting in sources/manual/ for anyone to check. What is NOT an option is
# putting a browser's name in the User-Agent to make the line green, which
# recovers the appearance of verification and none of it.
REFUSED_STATE = "refused_declared_reader"

# THE PUBLISHER IS REFUSING TO SERVE THIS, OBSERVED ON A DAY
# ==========================================================
# A second recorded state, added 15 October 2026 on George's ruling about the
# CO2LLECT citation, and it is NOT the one above wearing a different name. The
# difference is whose word the record is:
#
#   refused_declared_reader   A PERSON opened this exact URL on a stated day and
#                             found the document there. It is a human
#                             verification, it requires a name, and it is the
#                             strongest thing this register can say about a page
#                             it cannot fetch.
#   refusal                   THIS PIPELINE observed the publisher refusing to
#                             serve the page on a stated day, and says which code
#                             it answered with. Nobody has opened it. It is a
#                             measurement of a request, which is what
#                             sources/scope.md calls it ("A refusal is a
#                             measurement of a request, not of a publisher").
#
# WHY THE SECOND ONE HAD TO EXIST. The CO2LLECT page answers 404 under a section
# that redirects to /en/maintenance, and the body was read and cached on
# 2026-09-14 — the index holds the hash, 82,603 bytes, 6,750 characters of text —
# but the BODY IS NOT ON FILE: sources/cache/*/ bodies are gitignored by design
# and only the indexes are tracked. So `dead_since` is not available: the rule of
# 20 September accepts a removed page on the CACHED COPY, and checks that there
# are bytes behind the hash precisely so that a missing body cannot be passed off
# as a held one. What is true here is narrower and is what this records: the page
# was read once, the publisher is now refusing it, and the citation stands
# because the sentence it points at was quoted from a document somebody fetched.
#
# WHAT IT COSTS AND WHAT IT DOES NOT. It is REPORTED with its date on every run,
# never silent; it accepts only the code it records, so a 404 that becomes a 500
# is a new fact and fails; and it carries no claim that the document is still
# there, which is the whole difference from the state above.
OBSERVED_REFUSAL = "refusal"

# How old a human verification may get before it is worth saying so. Reported,
# never failed: a year-old check is not a broken link, it is a check worth
# repeating, and failing a build over it would push somebody to re-date the field
# rather than re-open the page.
VERIFICATION_STALE_DAYS = 365


def _age_days(date: str) -> int | None:
    try:
        return (dt.date.today() - dt.date.fromisoformat(date)).days
    except (ValueError, TypeError):
        return None


def urls_in(obj, path="") -> list[tuple[str, str, bool, str | None, dict | None]]:
    """Walk any of the transition files and yield
    (url, where, archived, snapshot, dead_since, refused, refusal).
    Written as a walk rather than as per-kind knowledge because the URL-bearing
    fields differ per kind and a new one should be checked the day it is added,
    not the day someone remembers to update this function."""
    found = []
    if isinstance(obj, dict):
        url = obj.get("url") or obj.get("source_url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            found.append((url, path, bool(obj.get("archived")), obj.get("snapshot"),
                          obj.get("dead_since"),
                          obj.get(REFUSED_STATE),
                          obj.get(OBSERVED_REFUSAL)))
        for k, v in obj.items():
            found += urls_in(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += urls_in(v, f"{path}[{i}]")
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="list the URLs and exit 2; this is not a pass")
    args = ap.parse_args()

    seen: dict[str, str] = {}
    archived: list[tuple[str, str]] = []
    # url -> (where, the recorded state). A publisher that refuses a declared
    # reader is a fact about the publisher, recorded per source with the date a
    # person last opened it; see REFUSED_STATE.
    declared: dict[str, tuple[str, dict]] = {}
    # A DEAD LINK IS NOT A DEAD SOURCE, ruled 20 September 2026. Where a source
    # carries `dead_since`, the publisher has taken down a page this register READ
    # and cached: the body is on file under its SHA-256 in the sector's index, and
    # that copy is the document. The gate checks the copy exists rather than
    # checking the URL still answers. sources/scope.md, "A dead link is not a dead
    # source". A 200 with an empty body is NOT covered: `dead_since` says a page was
    # removed, and it cannot say that about a page nobody got.
    on_file: list[tuple[str, str, dict]] = []
    # url -> (where, the recorded state). The publisher refused to serve this on
    # a stated day, observed by this pipeline rather than by a person; see
    # OBSERVED_REFUSAL.
    refusals: dict[str, tuple[str, dict]] = {}
    for kind in ("technology", "bottleneck", "parameter", "project"):
        for url, where, is_archived, snapshot, dead_since, refused, refusal in urls_in(
                sm.load(kind), kind):
            if dead_since is not None:
                on_file.append((url, where, dead_since))
                continue
            if is_archived:
                archived.append((url, snapshot or "NO SNAPSHOT PATH"))
                continue
            seen.setdefault(url, where)
            if refused is not None:
                declared[url] = (where, refused)
            if refusal is not None:
                refusals[url] = (where, refusal)

    if args.offline:
        print(f"check_links: {len(seen)} live URLs, {len(archived)} archived — "
              f"not checked (--offline). This is not a pass.")
        for url in sorted(seen):
            print(f"  {url}")
        return 2

    dead: list[str] = []
    soft: list[str] = []
    refused_ok: list[str] = []
    # ITS OWN BUCKET, because the heading over it is a different claim. The list
    # above says a PERSON opened the page and found the document; this says this
    # pipeline watched the publisher refuse it. Printing them under one heading
    # would have put "verified by hand" over a URL nobody has opened, which is
    # the one thing the two-state split exists to prevent.
    refusal_ok: list[str] = []

    def status_of(url: str) -> int:
        """The response code, following redirects. urlopen raises on 4xx/5xx
        rather than returning them, so the error carries the code we want and
        is unwrapped here; everything else that goes wrong is a network problem
        and reaches the caller as OSError."""
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status
        except urllib.error.HTTPError as exc:
            return exc.code

    for url in sorted(seen):
        host = urlparse(url).netloc
        try:
            code = status_of(url)
        except OSError as exc:
            soft.append(f"{url} — {type(exc).__name__}: {exc}")
            continue
        if code == 403 and url in declared:
            where, state = declared[url]
            missing = [f for f in ("last_verified", "by") if not state.get(f)]
            if missing:
                dead.append(f"{url} — declares {REFUSED_STATE} with no "
                            f"{', '.join(missing)}  ({where}). The state is a person's word "
                            f"that the page is there; without a name and a date it is a host "
                            f"list wearing a better name")
            else:
                age = _age_days(state["last_verified"])
                stale = (f", LAST CHECKED {age} DAYS AGO — worth re-opening"
                         if age is not None and age > VERIFICATION_STALE_DAYS else "")
                refused_ok.append(
                    f"{url}\n      publisher refuses a declared reader; "
                    f"{state['by']} opened it on {state['last_verified']}{stale}")
        elif code == 403 and host in BOT_HOSTILE:
            soft.append(f"{url} — 403 from a known bot-hostile host")
        elif code == 429:
            # ASKED TWICE BEFORE IT IS BELIEVED. A 429 is the only 4xx that is
            # about the request rather than the resource, and the second ask is
            # what tells the two apart: a rate limiter lets the next one through,
            # a page that has gone answers the same way all day.
            time.sleep(RATE_LIMIT_RETRY_PAUSE)
            try:
                code = status_of(url)
            except OSError as exc:
                soft.append(f"{url} — {type(exc).__name__}: {exc} (after a 429)")
                continue
            if code == 429:
                soft.append(f"{url} — HTTP 429 twice; the publisher is rate-limiting "
                            f"this reader, which says nothing about the page")
            elif 400 <= code < 500:
                dead.append(f"{url} — HTTP {code}  ({seen[url]})")
            elif code >= 500:
                soft.append(f"{url} — HTTP {code} (after a 429)")
        elif 400 <= code < 500:
            # A RECORDED REFUSAL IS ASKED FIRST, because it is the row's own
            # statement and needs no network to read. It accepts only the code it
            # records: a 404 that becomes a 410 or a 500 is a new fact about the
            # page and fails.
            state = refusals.get(url)
            if state and int(state[1].get("http") or 0) == code:
                where, rec = state
                missing = [f for f in ("observed", "by", "note") if not rec.get(f)]
                if missing:
                    dead.append(
                        f"{url} — declares {OBSERVED_REFUSAL} with no "
                        f"{', '.join(missing)}  ({where}). A refusal is a measurement "
                        f"of a request, and a measurement with no date and nothing "
                        f"saying who made it is an excuse rather than a record")
                else:
                    age = _age_days(rec["observed"])
                    stale = (f", OBSERVED {age} DAYS AGO — worth asking again"
                             if age is not None and age > VERIFICATION_STALE_DAYS else "")
                    refusal_ok.append(
                        f"{url}\n      HTTP {code}, observed by {rec['by']} on "
                        f"{rec['observed']}{stale}\n      {rec['note']}")
                continue
            if state:
                dead.append(
                    f"{url} — HTTP {code}, and the row records a {OBSERVED_REFUSAL} of "
                    f"HTTP {state[1].get('http')}. The publisher is answering "
                    f"differently from the day that was observed, which is a new fact "
                    f"about the page  ({seen[url]})")
                continue
            # THE SITE IS ASKED BEFORE THE PAGE IS DECLARED GONE. See
            # site_in_maintenance: a publisher that has taken its whole site
            # down is making a statement about itself, and the 404s underneath
            # it are that statement rather than a removed page.
            why = section_in_maintenance(url) if code == 404 else None
            if why:
                soft.append(f"{url} — HTTP 404, and {why}. A section that declares "
                            f"itself under maintenance has not removed the page; this "
                            f"fails again the day it is back  ({seen[url]})")
            else:
                dead.append(f"{url} — HTTP {code}  ({seen[url]})")
        elif code >= 500:
            soft.append(f"{url} — HTTP {code}")

    for url, snapshot in archived:
        if snapshot == "NO SNAPSHOT PATH" or not (sm.ROOT / snapshot).exists():
            dead.append(f"{url} — marked archived with no readable snapshot ({snapshot})")

    # THE CACHED BODY IS THE COPY ON FILE. Every fetch this register makes lands in
    # a sector cache index with its SHA-256 and the bytes beside it, so a source
    # whose URL has since gone is checkable against the copy rather than the URL.
    import json as _json
    cached: dict[str, list[dict]] = {}
    for idxp in sorted((sm.ROOT / "sources").glob("cache/*/index.json")):
        for rec in _json.loads(idxp.read_text(encoding="utf-8")).get("fetches", []):
            if rec.get("sha256") and (idxp.parent / rec["sha256"]).exists():
                cached.setdefault(rec["url"], []).append(rec)
    for url, where, ds in on_file:
        recs = cached.get(url) or []
        readable = [r for r in recs if "empty body" not in str(r.get("outcome", ""))]
        if not recs:
            dead.append(f"{url} — carries dead_since and no cached body is on file "
                        f"({where}); a citation whose document nobody holds is a "
                        f"citation nobody can check")
        elif not readable:
            dead.append(f"{url} — carries dead_since and the only cached body is an "
                        f"EMPTY one ({where}); a 200 with an empty body is a refusal on "
                        f"the day it was made, and a later 404 does not turn a refusal "
                        f"into a reading")

    # A SOURCE THAT DECLARES THE STATE AND IS THEN SERVED. Reported, because the
    # state is a claim about the publisher and the publisher has just contradicted
    # it: the block can come off, and leaving it on would keep a 403 excused that
    # nothing is causing any more.
    for url, (where, _state) in sorted(declared.items()):
        if url in seen and url not in "".join(refused_ok) and url not in "".join(dead):
            soft.append(f"{url} — declares {REFUSED_STATE} and answered normally; "
                        f"the state can be removed  ({where})")
    # THE SAME FOR AN OBSERVED REFUSAL, and it is the half that matters most:
    # this state exists because a section was under maintenance, and the day it
    # comes back the record is the only thing standing between a citation nobody
    # has re-read and a green line. Reported so the block comes off.
    for url, (where, _rec) in sorted(refusals.items()):
        if url in seen and url not in "".join(refusal_ok) and url not in "".join(dead):
            soft.append(f"{url} — declares {OBSERVED_REFUSAL} and answered normally; "
                        f"the page is back, so re-read it and remove the state  "
                        f"({where})")

    print(f"check_links: {len(seen)} live URLs checked, {len(archived)} archived, "
          f"{len(on_file)} read before the publisher removed them and held on the "
          f"cached body")
    for url, where, ds in sorted(on_file):
        print(f"  dead_since {ds.get('on', '?') if isinstance(ds, dict) else ds}  "
              f"{url[:96]}")
    if refused_ok:
        print(f"\npublisher refuses a declared reader ({len(refused_ok)}) — verified by hand, "
              f"not failed:")
        for r in refused_ok:
            print(f"  {r}")
    if refusal_ok:
        print(f"\npublisher refusing a page this register has read ({len(refusal_ok)}) — "
              f"observed and dated, not failed:")
        for r in refusal_ok:
            print(f"  {r}")
    if soft:
        print(f"\nreported, not failed ({len(soft)}):")
        for s in soft:
            print(f"  {s}")
    if dead:
        print(f"\nFAILED ({len(dead)}):", file=sys.stderr)
        for d in dead:
            print(f"  {d}", file=sys.stderr)
        print("\nFix the URL, or archive the source: set archived: true and add a "
              "`snapshot` path to a fetched copy in this repository.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

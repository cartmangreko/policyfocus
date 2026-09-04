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
  5xx, timeout, DNS       reported, not failed. A publisher's bad afternoon is
                          not a defect in this repository, and failing on it
                          would make the build depend on other people's uptime.
  403 from a known
  bot-hostile publisher   reported, not failed, and listed by name below. A CDN
                          blocking a datacentre IP tells us nothing about
                          whether the page exists.

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
import urllib.error
import urllib.request
from urllib.parse import urlparse

import sector_map as sm

TIMEOUT = 20
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
}

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
    (url, where, archived, snapshot, refused).
    Written as a walk rather than as per-kind knowledge because the URL-bearing
    fields differ per kind and a new one should be checked the day it is added,
    not the day someone remembers to update this function."""
    found = []
    if isinstance(obj, dict):
        url = obj.get("url") or obj.get("source_url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            found.append((url, path, bool(obj.get("archived")), obj.get("snapshot"),
                          obj.get(REFUSED_STATE)))
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
    for kind in ("technology", "bottleneck", "parameter", "project"):
        for url, where, is_archived, snapshot, refused in urls_in(sm.load(kind), kind):
            if is_archived:
                archived.append((url, snapshot or "NO SNAPSHOT PATH"))
                continue
            seen.setdefault(url, where)
            if refused is not None:
                declared[url] = (where, refused)

    if args.offline:
        print(f"check_links: {len(seen)} live URLs, {len(archived)} archived — "
              f"not checked (--offline). This is not a pass.")
        for url in sorted(seen):
            print(f"  {url}")
        return 2

    dead: list[str] = []
    soft: list[str] = []
    refused_ok: list[str] = []

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
        elif 400 <= code < 500:
            dead.append(f"{url} — HTTP {code}  ({seen[url]})")
        elif code >= 500:
            soft.append(f"{url} — HTTP {code}")

    for url, snapshot in archived:
        if snapshot == "NO SNAPSHOT PATH" or not (sm.ROOT / snapshot).exists():
            dead.append(f"{url} — marked archived with no readable snapshot ({snapshot})")

    # A SOURCE THAT DECLARES THE STATE AND IS THEN SERVED. Reported, because the
    # state is a claim about the publisher and the publisher has just contradicted
    # it: the block can come off, and leaving it on would keep a 403 excused that
    # nothing is causing any more.
    for url, (where, _state) in sorted(declared.items()):
        if url in seen and url not in "".join(refused_ok) and url not in "".join(dead):
            soft.append(f"{url} — declares {REFUSED_STATE} and answered normally; "
                        f"the state can be removed  ({where})")

    print(f"check_links: {len(seen)} live URLs checked, {len(archived)} archived")
    if refused_ok:
        print(f"\npublisher refuses a declared reader ({len(refused_ok)}) — verified by hand, "
              f"not failed:")
        for r in refused_ok:
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

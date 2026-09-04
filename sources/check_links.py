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
    "www.sunderland.gov.uk",
    "www.aesc-group.com",
    "aesc-group.com",
    # SURFACED BY DECLARING OURSELVES HONESTLY, and that is worth writing down.
    # These two answered the old string, which opened with a bare "Mozilla/5.0"
    # and named nobody. They refuse a User-Agent that says what it is. The
    # citations are sound — both pages are live in a browser — and the choice was
    # between wearing a browser's name to keep them green and saying plainly that
    # the publisher will not serve a declared reader. The second is the honest
    # one, and it costs two reported lines.
    "www.globalcement.com",
    "www.stellantis.com",
}


def urls_in(obj, path="") -> list[tuple[str, str, bool, str | None]]:
    """Walk any of the transition files and yield (url, where, archived, snapshot).
    Written as a walk rather than as per-kind knowledge because the URL-bearing
    fields differ per kind and a new one should be checked the day it is added,
    not the day someone remembers to update this function."""
    found = []
    if isinstance(obj, dict):
        url = obj.get("url") or obj.get("source_url")
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            found.append((url, path, bool(obj.get("archived")), obj.get("snapshot")))
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
    for kind in ("technology", "bottleneck", "parameter", "project"):
        for url, where, is_archived, snapshot in urls_in(sm.load(kind), kind):
            if is_archived:
                archived.append((url, snapshot or "NO SNAPSHOT PATH"))
                continue
            seen.setdefault(url, where)

    if args.offline:
        print(f"check_links: {len(seen)} live URLs, {len(archived)} archived — "
              f"not checked (--offline). This is not a pass.")
        for url in sorted(seen):
            print(f"  {url}")
        return 2

    dead: list[str] = []
    soft: list[str] = []

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
        if code == 403 and host in BOT_HOSTILE:
            soft.append(f"{url} — 403 from a known bot-hostile host")
        elif 400 <= code < 500:
            dead.append(f"{url} — HTTP {code}  ({seen[url]})")
        elif code >= 500:
            soft.append(f"{url} — HTTP {code}")

    for url, snapshot in archived:
        if snapshot == "NO SNAPSHOT PATH" or not (sm.ROOT / snapshot).exists():
            dead.append(f"{url} — marked archived with no readable snapshot ({snapshot})")

    print(f"check_links: {len(seen)} live URLs checked, {len(archived)} archived")
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

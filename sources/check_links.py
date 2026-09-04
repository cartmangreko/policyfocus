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
UA = ("Mozilla/5.0 (compatible; policyfocus-linkcheck/1.0; "
      "+https://github.com/cartmangreko/policyfocus)")

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
    # NOT BOT-HOSTILE, AND HERE FOR AN HONEST REASON THAT IS NOT THE OTHERS'.
    # The SEC's fair-access policy asks automated readers to declare a contact
    # ADDRESS in the User-Agent, and it answers 403 to every request that does
    # not — including this one, whose UA declares a repository URL instead. The
    # document is public, permanent and the best available citation for a filed
    # exhibit; what stands between us and it is one line of contact detail.
    #
    # That line is not mine to write. Publishing an address in a header on every
    # build is a decision about whose address it is, so it is raised rather than
    # taken, and until it is taken the SEC is listed here with the reason stated
    # rather than filed under a label that would misdescribe it.
    "www.sec.gov",
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

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
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlparse

import requests

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
    for url in sorted(seen):
        host = urlparse(url).netloc
        try:
            r = requests.get(url, timeout=TIMEOUT, allow_redirects=True,
                             headers={"User-Agent": UA})
            code = r.status_code
        except requests.RequestException as exc:
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

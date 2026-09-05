"""
The sitemap asks for nothing the pages refuse.

    python3 check_sitemap.py            # exits non-zero on any violation

Run AFTER the build, over the file the build wrote, for the same reason
check_anchor_text.py is: this is a question about what was PUBLISHED, and the
only honest place to ask it is the artefact. A source-level version would check
the rule and not the file, which is exactly the gap this gate was asked to
close — web/lib/launch.test.mts already proves the classification is coherent on
a fixture of five paths, and would pass on a build whose sitemap listed every
demoted page in the register.

WHAT IT CHECKS
==============
NO PUBLISHED URL IS A PAGE THAT SAYS noindex. §0.8 makes indexability follow the
lead block: a page that renders one is the product and is published, a page that
does not carries `noindex, follow` in its own head. Since launched robots.txt
disallows nothing, the sitemap is this site's ONE published statement of what it
asks to have indexed — so a demoted URL in it is the site asking a crawler for a
page whose own head refuses. The two are compared here as they were rendered,
not as they were meant.

NO URL IS EMITTED TWICE. Not fatal to a crawler; fatal to a reader of the file,
because it means two code paths contribute the same route and one of them is
unaccounted for.

EVERY URL IS ON THE CANONICAL HOST, read from web/lib/routes.ts so that the
constant and the file agree. A sitemap of redirects publishes an address that is
not the one that ends up in the index.

THE PRE-LAUNCH STATE IS NOT A PASS AND NOT A FAILURE
====================================================
`SITE_LAUNCHED` unset means every page on the site renders noindex, including
the product pages, because the switch dominates (web/lib/launch.ts). Comparing
the sitemap against the pages in that state would fail every URL and prove
nothing — the closure is global and says nothing about any route's class. So in
that state the demotion comparison is SKIPPED AND SAID OUT LOUD, and the
duplicate and host checks still run. A local build is pre-launch; production is
not, and this gate does its whole job there.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "web" / ".next" / "server" / "app"
SITEMAP = APP / "sitemap.xml.body"
ROBOTS = APP / "robots.txt.body"
ROUTES_TS = ROOT / "web" / "lib" / "routes.ts"

LOC = re.compile(r"<loc>([^<]+)</loc>")
SITE_URL = re.compile(r'export const SITE_URL = "([^"]+)"')
# Next writes the robots metadata as a meta tag in the prerendered head.
NOINDEX = re.compile(r'<meta name="robots" content="([^"]*)"')


def canonical_origin() -> str | None:
    """The origin the sitemap is supposed to be built on, read from the module
    that owns it rather than repeated here."""
    m = SITE_URL.search(ROUTES_TS.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def page_html(path: str) -> Path | None:
    """The prerendered HTML for a route path, or None where the build wrote
    none. `/` is index.html; everything else is <path>.html."""
    rel = "index" if path == "/" else path.lstrip("/")
    candidate = APP / f"{rel}.html"
    return candidate if candidate.is_file() else None


def main() -> int:
    if not SITEMAP.is_file():
        print(f"check_sitemap: no sitemap at {SITEMAP.relative_to(ROOT)} — run this "
              f"after `next build`, not before it")
        return 1

    origin = canonical_origin()
    if not origin:
        print("check_sitemap: web/lib/routes.ts states no SITE_URL")
        return 1

    urls = LOC.findall(SITEMAP.read_text(encoding="utf-8"))
    failures: list[str] = []

    if not urls:
        failures.append("the sitemap is empty")

    seen: dict[str, int] = {}
    for url in urls:
        seen[url] = seen.get(url, 0) + 1
    for url, count in sorted(seen.items()):
        if count > 1:
            failures.append(f"{url} — emitted {count} times")

    paths: list[str] = []
    for url in sorted(seen):
        if url == origin:
            paths.append("/")
        elif url.startswith(f"{origin}/"):
            paths.append(url[len(origin):])
        else:
            failures.append(f"{url} — not on the canonical origin {origin}")

    # THE SWITCH. Pre-launch every page is noindex and the comparison is
    # meaningless; robots.txt is where that state is legible in the build.
    robots_txt = ROBOTS.read_text(encoding="utf-8") if ROBOTS.is_file() else ""
    launched = "Disallow: /" not in robots_txt

    checked = 0
    if launched:
        for path in paths:
            html_file = page_html(path)
            if html_file is None:
                failures.append(f"{path} — published and the build wrote no page for it")
                continue
            checked += 1
            for content in NOINDEX.findall(html_file.read_text(encoding="utf-8")):
                if "noindex" in content:
                    failures.append(
                        f"{path} — published in the sitemap and renders "
                        f"'{content}'. The sitemap asks for a page whose own head "
                        f"refuses; §0.8 says indexability follows the lead block, "
                        f"and these two readings of it disagree")

    if failures:
        print(f"check_sitemap: {len(failures)} problem(s) in {len(urls)} published URL(s)\n")
        print("\n".join(f"  {f}" for f in failures))
        return 1

    print(f"check_sitemap: OK — {len(urls)} URL(s), all distinct, all on {origin}")
    if launched:
        print(f"  {checked} page(s) checked against their own robots tag; none says noindex")
    else:
        print("  the demotion check is SKIPPED: this build is pre-launch, every page "
              "renders noindex, and the closure is the switch rather than any route's "
              "class. It runs on a launched build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

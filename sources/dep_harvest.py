"""One supplier's newsroom, from index pages to a digest a person can read.

    python3 dep_harvest.py NODE_ID --index URL [URL ...] --match REGEX [--no-filter]
    python3 dep_harvest.py NODE_ID --sitemap URL --match REGEX

Four steps, in order, and each one is cached so re-running is free:
  1  fetch the index or sitemap pages,
  2  pull every link whose href matches --match, keeping its anchor text as title,
  3  fetch the ones whose title passes dep_sweep.is_candidate (unless --no-filter),
  4  print a digest of all of them, oldest first.

WHAT IT PRINTS TO STDERR IS PART OF THE OUTPUT. `listed / candidates / fetched` is
what the docket reports as the sweep's depth for that node, and it is the only
honest way to say how much of a newsroom was actually looked at. A supplier whose
index paginates behind JavaScript gives `listed 0`, and that number is the finding.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import dep_sweep as S
import dep_text as T

HERE = Path(__file__).resolve().parent


def harvest(index_urls: list[str], match: str, sitemap: bool = False) -> dict[str, str]:
    subprocess.run([sys.executable, "dep_fetch.py", *index_urls, "--jobs", "3"],
                   cwd=HERE, capture_output=True)
    pat, out = re.compile(match, re.I), {}
    for u in index_urls:
        b = T.body(u)
        if not b:
            continue
        if sitemap:
            for loc in T.sitemap_urls(b):
                if pat.search(loc):
                    out.setdefault(loc, "")
        else:
            for href, txt in T.links(b, u):
                if pat.search(href) and txt and len(txt) > 12:
                    if len(txt) > len(out.get(href, "")):
                        out[href] = txt
    return out


def main(argv: list[str]) -> int:
    node = argv[0]
    def opt(name: str) -> list[str]:
        if name not in argv:
            return []
        i = argv.index(name) + 1
        vals = []
        while i < len(argv) and not argv[i].startswith("--"):
            vals.append(argv[i]); i += 1
        return vals

    sitemap = bool(opt("--sitemap"))
    idx_urls = opt("--sitemap") or opt("--index")
    match = opt("--match")[0]
    titles = harvest(idx_urls, match, sitemap)
    cands = [u for u, t in titles.items()
             if "--no-filter" in argv or not t or S.is_candidate(t)]
    print(f"{node}: listed {len(titles)}  candidates {len(cands)}", file=sys.stderr)
    (HERE / f"dependency_cache/.titles-{node}.json").write_text(
        json.dumps(titles, indent=1, ensure_ascii=False))
    lst = HERE / f"dependency_cache/.cands-{node}.txt"
    lst.write_text("\n".join(cands))
    subprocess.run([sys.executable, "dep_fetch.py", "--file", str(lst), "--jobs", "3"],
                   cwd=HERE, capture_output=True)
    r = subprocess.run([sys.executable, "dep_digest.py", "--file", str(lst)],
                       cwd=HERE, capture_output=True, text=True)
    print(r.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

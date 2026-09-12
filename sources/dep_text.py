"""Reading what dep_fetch.py cached: text out of a page, links out of a page.

Standard library only, and deliberately. The gate chain already refuses to depend
on a PDF engine and an LLM client (sources/requirements-gates.txt says why); a
sweep that needed an HTML parser installed would be a sweep that could not be
re-run on a machine that had not been prepared for it. What is here is a tag
stripper and an href scraper, which is all the sweep asks of a page: the ruling on
what a sentence says is made by a reader, not by a selector.
"""
from __future__ import annotations

import gzip
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit

HERE = Path(__file__).resolve().parent
CACHE = HERE / "dependency_cache"
INDEX = CACHE / "index.json"

DROP = re.compile(r"<(script|style|noscript|svg|head)\b.*?</\1>", re.S | re.I)
BLOCK = re.compile(r"</?(p|div|br|li|tr|h[1-6]|section|article|td)\b[^>]*>", re.I)
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"[ \t\r\f\v]+")
NL = re.compile(r"\n{3,}")


def to_text(raw: bytes) -> str:
    if raw[:4] == b"%PDF":
        return pdf_text(raw)
    s = raw.decode("utf-8", "replace")
    s = DROP.sub(" ", s)
    s = BLOCK.sub("\n", s)
    s = TAG.sub(" ", s)
    s = html.unescape(s)
    s = WS.sub(" ", s)
    s = "\n".join(l.strip() for l in s.splitlines())
    return NL.sub("\n\n", s).strip()


def pdf_text(raw: bytes) -> str:
    # `import pymupdf`, NOT `import fitz`. The legacy alias prints a deprecation
    # warning to STDOUT, not stderr, which put a line of English at the top of this
    # module's JSON output and made it unparseable. A library that writes to stdout
    # is a library that has to be imported by its current name.
    try:
        import pymupdf
    except ImportError:
        return ""
    with pymupdf.open(stream=raw, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def links(raw: bytes, base: str) -> list[tuple[str, str]]:
    """(absolute url, anchor text). Duplicates kept: the same href with two
    different anchor texts is two different claims about what it is."""
    s = DROP.sub(" ", raw.decode("utf-8", "replace"))
    out = []
    for m in re.finditer(r"<a\b[^>]*?href\s*=\s*[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>",
                         s, re.S | re.I):
        href, txt = m.group(1), html.unescape(TAG.sub(" ", m.group(2)))
        out.append((urljoin(base, href.strip()), WS.sub(" ", txt).strip()))
    return out


def sitemap_urls(raw: bytes) -> list[str]:
    s = raw.decode("utf-8", "replace")
    return [html.unescape(m.group(1).strip())
            for m in re.finditer(r"<loc>(.*?)</loc>", s, re.S | re.I)]


def index() -> dict:
    return json.loads(INDEX.read_text()) if INDEX.exists() else {}


def body(url: str) -> bytes | None:
    import hashlib
    e = index().get(hashlib.sha1(url.encode()).hexdigest()[:16])
    if not e or not e.get("file"):
        return None
    raw = (CACHE / e["file"]).read_bytes()
    return gzip.decompress(raw) if e["file"].endswith(".gz") else raw


def text(url: str) -> str:
    b = body(url)
    return to_text(b) if b else ""


if __name__ == "__main__":
    mode, url = sys.argv[1], sys.argv[2]
    b = body(url)
    if b is None:
        print("not cached", file=sys.stderr); raise SystemExit(1)
    if mode == "text":
        print(to_text(b))
    elif mode == "links":
        for u, t in links(b, url):
            print(f"{u}\t{t[:120]}")
    elif mode == "sitemap":
        print("\n".join(sitemap_urls(b)))

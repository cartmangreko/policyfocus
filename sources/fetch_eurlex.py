#!/usr/bin/env python3
"""
Fetch source legislative text from EUR-Lex/Cellar by CELEX, verify it is the
real enacting text rather than a landing page, and hand it to the extraction
pipeline. Nothing downstream changes: this only produces sources/<slug>.txt
(plus annexes and prior-rule texts) with a provenance sidecar.

Usage:
    python3 fetch_eurlex.py                 # every slug in manifest.json
    python3 fetch_eurlex.py ets cbam_ext    # named slugs only
    python3 fetch_eurlex.py --dry-run ets   # fetch and verify, write nothing
    python3 fetch_eurlex.py --overwrite ets # replace an existing source text
    python3 fetch_eurlex.py --refresh ets   # ignore the on-disk cache
    python3 fetch_eurlex.py --formats xhtml,fmx4,pdf

An existing sources/<slug>.txt is never replaced without --overwrite: those
files are the inputs to extraction work already done. Exit code is non-zero if
any slug ends fetch_failed, so a build step can gate on it.

------------------------------------------------------------------------------
RUNTIME FINDINGS (each checked against the live endpoints)
------------------------------------------------------------------------------
1. eur-lex.europa.eu/legal-content/... answers automated requests with HTTP 202
   and a zero-byte body (a JS bot challenge), with or without a browser
   User-Agent. It is unusable as a fetch target and is NOT in the format chain.
   Everything below goes to the Publications Office repository (Cellar), which
   serves the same documents under content negotiation and has no challenge.
2. XHTML is the primary text format, ahead of Formex, which reverses the
   brief's stated order. Formex is better structured, but ElementTree.itertext
   splits inline markup mid-sentence -- "(the CBAM)" comes back as three lines
   and loses its quotes -- which breaks the verbatim source_text substring
   check in verify_pass.py. XHTML keeps the sentence intact. Formex is kept as
   the next fallback, and --formats overrides the order.
3. Proposals (5...PC....) answer 300 Multiple Choices listing DOC_1, DOC_2...
   streams: the act and its annexes as separate documents. Both are fetched;
   the annexes land in <slug>_annexes.txt, matching the existing iaa.txt /
   iaa_annexes.txt convention.
4. consolidated_date: "latest" does NOT resolve implicitly -- bare 02023R0956
   is a 404. The available consolidation dates are read out of the act's branch
   notice and the newest is taken. Superseded consolidations are listed there
   but only the newest carries retrievable content (02023R0956-20230516 is a
   404 in every format while -20251020 serves both XHTML and Formex).
"""
import argparse
import io
import json
import os
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

import requests

SOURCES_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(SOURCES_DIR, "manifest.json")
CACHE_DIR = os.path.join(SOURCES_DIR, "cache")

CELLAR = "https://publications.europa.eu/resource/celex/{celex}"

# Cellar wants ISO 639-3 in Accept-Language; the manifest carries the familiar
# two-letter form.
LANG3 = {"EN": "eng", "FR": "fra", "DE": "deu", "ES": "spa", "IT": "ita", "NL": "nld"}

ACCEPT = {
    "xhtml": "application/xhtml+xml",
    "fmx4": "application/zip;mtype=fmx4",
    "pdf": "application/pdf",
}
DEFAULT_FORMATS = ["xhtml", "fmx4", "pdf"]

# Polite and serial. Cellar is not rate-limited aggressively, but the terms of
# use ask for restraint and the cache means a given CELEX is pulled once.
REQUEST_GAP_S = 1.0
RETRY_BACKOFF_S = 5.0
TIMEOUT_S = 90

# The floor exists to catch interstitials -- a language picker, a "document
# does not exist" notice, a cookie wall -- which run to a few hundred
# characters. It is deliberately not set at "a full regulation": short acts are
# real. Decision 2015/1814 establishing the market stability reserve is a
# legitimate 15k characters consolidated, and a 20k floor rejected it. The
# structural checks below (Article 1, adoption formula or consolidation banner,
# identity echo) are what separate a real short act from a landing page.
MIN_CHARS = {"act": 8000, "annex": 1200, "prior": 5000}

_last_request = 0.0


# ---------------------------------------------------------------------------
# CELEX conventions
# ---------------------------------------------------------------------------

def celex_sector(celex):
    return celex[:1]


def celex_kind(celex):
    """proposal | consolidated | adopted -- read off the CELEX sector digit."""
    sector = celex_sector(celex)
    if sector == "5":
        return "proposal"
    if sector == "0":
        return "consolidated"
    if sector == "3":
        return "adopted"
    return "unknown"


def status_for_kind(kind):
    return "proposed" if kind == "proposal" else "adopted"


def consolidated_celex(base_celex):
    """32023R0956 -> 02023R0956 (the consolidated family, still undated)."""
    return "0" + base_celex[1:]


COM_NUMBER = re.compile(r"COM\s*\(\s*(\d{4})\s*\)\s*(\d{1,4})")
# "2026/0068(COD)", "2026/0068 (COD)", "2026/0068(NLE)" -- the interinstitutional
# procedure code, printed on the cover page of every Commission proposal.
PROCEDURE_CODE = re.compile(r"(\d{4})\s*/\s*(\d{4})\s*\(?\s*([A-Z]{3})\s*\)?")


def celex_from_com(com):
    """
    "COM(2026) 100" -> "52026PC0100". The deterministic mapping, used only as a
    recovery candidate when the manifest's CELEX does not resolve.
    """
    m = COM_NUMBER.search(com or "")
    if not m:
        return None
    return f"5{m.group(1)}PC{int(m.group(2)):04d}"


def procedure_in_head(head, procedure):
    """
    Is this the document the manifest's procedure code names?

    The procedure code is the one identifier that survives a CELEX/COM
    divergence: it is printed on the proposal's own cover ("2026/0068 (COD)")
    and is assigned by the interinstitutional register rather than by the
    document's filing. Matching is tolerant of the spacing and the optional
    parentheses, which vary between the XHTML and PDF renderings.
    """
    m = PROCEDURE_CODE.search(procedure or "")
    if not m:
        return None  # nothing to check against
    year, num, kind = m.groups()
    return bool(
        re.search(rf"{year}\s*/\s*{num}\s*\(?\s*{kind}\s*\)?", head)
    )


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _get(url, accept, lang3, stream_binary=False):
    """One serial, polite GET. Returns the requests.Response."""
    global _last_request
    gap = time.time() - _last_request
    if gap < REQUEST_GAP_S:
        time.sleep(REQUEST_GAP_S - gap)
    headers = {"Accept-Language": lang3}
    if accept:
        headers["Accept"] = accept
    resp = requests.get(url, headers=headers, timeout=TIMEOUT_S, allow_redirects=True)
    _last_request = time.time()
    return resp


def get_with_retry(url, accept, lang3):
    """Retry once after a back-off on throttling or a server-side wobble."""
    resp = _get(url, accept, lang3)
    if resp.status_code in (429, 500, 502, 503, 504):
        time.sleep(RETRY_BACKOFF_S)
        resp = _get(url, accept, lang3)
    return resp


# ---------------------------------------------------------------------------
# Format handling
# ---------------------------------------------------------------------------

MULTI_CHOICE_ITEM = re.compile(
    r'href="(?P<url>[^"]+/DOC_\d+)"(?P<tail>.*?)(?=<li title="item"|</ul></li></ul>|$)',
    re.S,
)
STREAM_NAME = re.compile(r'<li title="stream_name">(?P<name>[^<]+)</li>')

# Cellar labels a proposal's annex stream "..._annexe_...". Anything else in a
# 300 listing is act text.
ANNEX_STREAM = re.compile(r"annex", re.I)


def parse_multiple_choices(body):
    """A 300 body -> [(url, stream_name)] in stream order."""
    out = []
    for m in MULTI_CHOICE_ITEM.finditer(body):
        name_m = STREAM_NAME.search(m.group("tail"))
        out.append((unescape(m.group("url")), name_m.group("name") if name_m else ""))
    return out


def xhtml_to_text(raw):
    """
    Tags out, entities decoded, block elements become line breaks. Deliberately
    conservative: NBSP is left as U+00A0 because the register's quoted amounts
    ("EUR 450\xa0000\xa0000") carry it, and collapsing it would break the
    verbatim source_text check.
    """
    s = raw
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<(p|div|br|tr|li|h[1-6]|table|thead|tbody)\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|tr|li|h[1-6]|table)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip()
    # Cellar prefixes the stream's source filename ("1_EN_ACT_part1_v12.docx")
    # as the first line. It is production metadata, not text of the act, and
    # its version suffix changes between revisions -- leaving it in would put a
    # spurious diff at the top of every re-fetch.
    return re.sub(r"^\S+\.(?:docx?|pdf|rtf)\s*\n", "", s, count=1).strip()


def formex_to_text(zip_bytes):
    """
    Formex ZIP -> text. The .doc.xml sidecar is metadata, not content; the
    document itself is the largest remaining XML. See finding 2 in the module
    docstring for why this is a fallback rather than the primary.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".xml") and not n.lower().endswith(".doc.xml")]
        if not names:
            raise ValueError("Formex archive contains no document XML")
        chunks = []
        for name in sorted(names, key=lambda n: zf.getinfo(n).file_size, reverse=True):
            try:
                root = ET.fromstring(zf.read(name))
            except ET.ParseError as exc:
                raise ValueError(f"Formex XML {name} did not parse: {exc}") from exc
            text = "\n".join(t.strip() for t in root.itertext() if t and t.strip())
            if text:
                chunks.append(text)
        return "\n\n".join(chunks).strip()


# PDF text arrives with typographic artefacts that no other format has. These
# are cosmetic in a reader and fatal to a verbatim substring check, so they are
# repaired once, here, before the text is ever written or quoted from.
LIGATURES = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi",
    "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
}
# A word broken across a line break: "se-\ncurity". Only joined when both sides
# are lower-case letters, so "carbon-\nbased" style compounds and enumerations
# like "(a)-\n" are left alone.
LINE_BREAK_HYPHEN = re.compile(r"([a-zà-ÿ])-\n([a-zà-ÿ])")


def normalize_pdf_text(text):
    """
    Repair PDF extraction artefacts. Applied to PDF-derived text only.

    XHTML and Formex text is not put through this: it has no ligature or
    hyphenation damage to undo, and rewriting it would risk breaking the exact
    matches the existing sources/*.txt files already satisfy.

    Line structure is deliberately preserved rather than reflowed into
    paragraphs. The existing hand-made sources (iaa.txt, ~63 chars a line)
    keep the PDF's hard wraps and the register's quoted source_text carries
    the newlines with it, so reflowing would break every existing quote for no
    gain -- extraction quotes from this same file, so it only has to be
    self-consistent.
    """
    for lig, plain in LIGATURES.items():
        text = text.replace(lig, plain)
    # Soft hyphens and zero-width joiners are invisible and unquotable.
    text = text.replace("­", "").replace("​", "").replace("﻿", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Re-join words split across a line break, losing the hyphen with them.
    text = LINE_BREAK_HYPHEN.sub(r"\1\2", text)
    # PDF layout leaves runs of spaces where the reader saw kerning. NBSP is
    # preserved -- quoted amounts ("EUR 450\xa0000\xa0000") depend on it.
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Running headers and footers. A PDF has no notion of "body text", so the
# language-code footer Commission documents carry ("EN 45 EN") is emitted in
# reading order and lands mid-sentence, inside anything quoted across a page
# break. Two rules, because neither is sufficient alone: the margin bands catch
# furniture generally, and the explicit pattern catches the language footer on
# the landscape annex pages, where it sits at 0.896 of the page height and no
# safe band reaches it.
HEADER_BAND = 0.06
FOOTER_BAND = 0.88
LANGUAGE_FOOTER = re.compile(r"^\s*[A-Z]{2}\s*\d*\s*[A-Z]{2}\s*$")


def is_page_furniture(block, height):
    _x0, y0, _x1, y1, text = block[0], block[1], block[2], block[3], block[4]
    if y1 < height * HEADER_BAND or y0 > height * FOOTER_BAND:
        return True
    return bool(LANGUAGE_FOOTER.match(re.sub(r"\s+", " ", text)))


def pdf_to_text(pdf_bytes):
    """
    PDF -> normalized text. Commission proposals are frequently PDF-only (the
    Industrial Accelerator Act, 52026PC0100, has no XHTML or Formex
    manifestation at all), which makes this path load-bearing for exactly the
    new proposals the pipeline most wants to catch -- not a last resort that
    can be left inert.
    """
    try:
        import pymupdf
    except ImportError:
        pymupdf = None
    if pymupdf is not None:
        pages = []
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                height = page.rect.height
                kept = [
                    block[4]
                    for block in page.get_text("blocks")
                    if not is_page_furniture(block, height)
                ]
                pages.append("\n".join(kept))
        return normalize_pdf_text("\n".join(pages))

    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None
    if PdfReader is not None:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        return normalize_pdf_text("\n".join(p.extract_text() or "" for p in reader.pages))

    from shutil import which
    import subprocess
    import tempfile

    if which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as fh:
            fh.write(pdf_bytes)
            fh.flush()
            out = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", fh.name, "-"],
                capture_output=True,
                check=True,
            )
        return normalize_pdf_text(out.stdout.decode("utf-8", errors="replace"))

    raise ValueError(
        "PDF fallback reached but no text extractor is installed "
        "(tried pymupdf, pypdf, pdftotext) -- pip install pymupdf"
    )


def has_pdf_extractor():
    for mod in ("pymupdf", "pypdf"):
        try:
            __import__(mod)
            return True
        except ImportError:
            pass
    from shutil import which

    return which("pdftotext") is not None


# ---------------------------------------------------------------------------
# Verification. A 200 is not evidence of the right document.
# ---------------------------------------------------------------------------

ADOPTION_FORMULA = re.compile(
    r"HAV[EIS]\s+ADOPTED|HAS\s+ADOPTED|ONT\s+ARR[ÊE]T[ÉE]|ADOPTED\s+THIS", re.I
)
ARTICLE_1 = re.compile(r"\bArticle\s+(1|premier)\b", re.I)
ANNEX_MARKER = re.compile(r"\bANNEX(?:ES)?\b|\bANNEXE\b", re.I)
# What a consolidated text opens with in place of a preamble. The banner is
# localised, so it is matched per language; a language with no banner pattern
# here skips the check rather than failing every consolidated act in it.
CONSOLIDATION_BANNER = {
    "EN": re.compile(r"Consolidated\s+TEXT|meant purely as a documentation tool", re.I),
    "FR": re.compile(r"TEXTE\s+consolidé|seulement un outil de documentation", re.I),
    "DE": re.compile(r"Konsolidierter\s+TEXT|dient lediglich der Information", re.I),
}
NOT_FOUND_PAGE = re.compile(
    r"document does not exist|no documents matching|does not exist in this language", re.I
)
LANG_PICKER = re.compile(r"choose (the )?language|available languages", re.I)

# Crude but sufficient language guard: EUR-Lex silently serving French or
# German instead of English is the failure mode, and these words separate them
# decisively over a document of this length.
LANG_MARKERS = {
    "EN": (" the ", " shall ", " of the "),
    "FR": (" les ", " doit ", " de la "),
    "DE": (" der ", " und ", " nicht "),
}


def looks_like_language(text, lang):
    sample = text[:200000].lower()
    scores = {code: sum(sample.count(w) for w in words) for code, words in LANG_MARKERS.items()}
    want = scores.get(lang.upper(), 0)
    return want > 0 and want == max(scores.values())


def verify(text, *, role, celex, kind, com=None, procedure=None, expect_annexes=False, lang="EN"):
    """
    Returns [] when the text is safe to hand on, else a list of reasons. Every
    check is a failure the endpoints actually produce, not a hypothetical.

    kind decides which enacting structure is required. A consolidated text is
    an editorial compilation and is published without its preamble -- it says
    so in its own header -- so "HAVE ADOPTED THIS REGULATION" is absent by
    design and the consolidation banner stands in for it. Requiring the
    adoption formula there would reject every valid consolidated act.
    """
    errs = []
    if not text or not text.strip():
        errs.append("empty body")
        return errs

    if NOT_FOUND_PAGE.search(text[:4000]):
        errs.append("'document does not exist' notice rather than a document")
    if LANG_PICKER.search(text[:2000]) and len(text) < 5000:
        errs.append("language-picker interstitial rather than a document")

    floor = MIN_CHARS[role]
    if len(text) < floor:
        errs.append(f"body is {len(text)} chars, below the {floor}-char floor for a {role}")

    # Identity: does the response actually belong to the CELEX requested?
    #
    # A bare act number is NOT enough. EU acts cite each other constantly, so
    # "2003/87" appears in the opening pages of the CBAM regulation and a loose
    # substring test passes the wrong document. Each kind is therefore matched
    # on what that kind prints about *itself* in its own header.
    head = text[:6000]
    # A consolidated CELEX carries a date suffix that the document itself never
    # prints; the undated stem is what appears in its header.
    stem = celex.split("-")[0]
    number = re.match(r"^[035](\d{4})[A-Z]{1,2}(\d{4})$", stem)
    year, num = (number.group(1), str(int(number.group(2)))) if number else (None, None)

    if kind == "consolidated":
        # Prints "02023R0956 — EN — 20.10.2025" in the banner line.
        matched = stem in head or ("3" + stem[1:]) in head
        want = stem
    elif kind == "proposal" and com:
        # Prints "COM(2025) 989 final" on the cover.
        matched = com in head or com.replace(" ", "\xa0") in head
        want = com
    elif year:
        # An original adopted act titles itself "REGULATION (EU) 2023/956 OF
        # THE ...". The number must sit next to the act type, not float loose.
        matched = bool(
            re.search(
                rf"(REGULATION|DIRECTIVE|DECISION)[^\n]{{0,80}}\b{year}/{num}\b",
                head,
                re.I,
            )
        )
        want = f"{year}/{num} in a title line"
    else:
        matched, want = stem in head, stem

    if not matched:
        errs.append(f"response head does not echo {want} for {celex}")

    # The procedure code is checked independently of the CELEX, so a CELEX that
    # resolves to a real-but-wrong proposal is caught rather than trusted.
    if role == "act" and kind == "proposal":
        proc_ok = procedure_in_head(head, procedure)
        if proc_ok is False:
            errs.append(f"procedure {procedure} does not appear on the cover of {celex}")

    if role in ("act", "prior"):
        if not ARTICLE_1.search(text):
            errs.append("no 'Article 1' -- not an enacting text")
        if kind == "consolidated":
            banner = CONSOLIDATION_BANNER.get(lang.upper())
            if banner and not banner.search(head):
                errs.append("no consolidation banner -- not a consolidated text")
        elif not ADOPTION_FORMULA.search(text):
            errs.append("no adoption formula ('HAVE ADOPTED' / 'HAS ADOPTED')")
        if expect_annexes and not ANNEX_MARKER.search(text):
            errs.append("annexes expected but no ANNEX marker present")
    elif role == "annex":
        if not ANNEX_MARKER.search(text):
            errs.append("annex document carries no ANNEX marker")

    if not looks_like_language(text, lang):
        errs.append(f"body does not read as {lang} -- wrong language served")

    return errs


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def cache_path(celex, fmt, lang):
    """
    The language is part of the key. Cellar serves the same CELEX in any
    language from the same URL, so a key of CELEX+format alone lets a French
    fetch be handed back to an English one -- which the verifier then rejects
    as "wrong language served" on a document that was never re-fetched.
    """
    ext = {"xhtml": "xhtml", "fmx4": "zip", "pdf": "pdf"}[fmt]
    return os.path.join(CACHE_DIR, f"{celex}.{lang.upper()}.{ext}")


def cached_bytes(celex, fmt, lang, refresh):
    path = cache_path(celex, fmt, lang)
    if refresh or not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def store_bytes(celex, fmt, lang, blob):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path(celex, fmt, lang), "wb") as fh:
        fh.write(blob)


# ---------------------------------------------------------------------------
# Fetching one CELEX
# ---------------------------------------------------------------------------

class FetchError(Exception):
    pass


def decode(blob, resp=None):
    enc = None
    if resp is not None:
        enc = resp.encoding if resp.encoding and resp.encoding.lower() != "iso-8859-1" else None
    return blob.decode(enc or "utf-8", errors="replace")


def fetch_documents(celex, lang, formats, refresh, log):
    """
    Fetch one CELEX and return (format_used, [(role, text)]).

    role is "act" or "annex". Formats are tried in order and the first that
    yields text wins; verification happens in the caller, so a format that
    returns something unverifiable still falls through to the next one.
    """
    lang3 = LANG3.get(lang.upper(), lang.lower())
    url = CELLAR.format(celex=celex)
    problems = []

    for fmt in formats:
        if fmt == "pdf" and not has_pdf_extractor():
            problems.append("pdf: no text extractor installed")
            continue

        blob = cached_bytes(celex, fmt, lang, refresh)
        if blob is not None:
            # A multi-stream work caches its annexes separately; read them back
            # too, or a cache hit would silently return a document short of the
            # annexes the live fetch produced.
            annex_blob = cached_bytes(f"{celex}_annexes", fmt, lang, refresh)
            log(f"    {fmt}: cache hit" + (" (act + annexes)" if annex_blob else ""))
            try:
                docs = [("act", to_text(fmt, blob))]
                if annex_blob:
                    docs.append(("annex", to_text(fmt, annex_blob)))
                return fmt, docs
            except ValueError as exc:
                problems.append(f"{fmt}: {exc}")
                continue
        else:
            resp = get_with_retry(url, ACCEPT[fmt], lang3)

            if resp.status_code == 300:
                # A multi-document work: act plus annexes as separate streams.
                items = parse_multiple_choices(resp.text)
                if not items:
                    problems.append(f"{fmt}: 300 with no DOC_n streams")
                    continue
                docs = []
                for item_url, stream in items:
                    part = get_with_retry(item_url, None, lang3)
                    if part.status_code != 200 or not part.content:
                        problems.append(f"{fmt}: stream {stream or item_url} -> {part.status_code}")
                        continue
                    role = "annex" if ANNEX_STREAM.search(stream) else "act"
                    docs.append((role, part.content, stream))
                if not docs:
                    continue
                # Cache the act stream under the CELEX; annexes alongside it.
                for role, content, _stream in docs:
                    suffix = celex if role == "act" else f"{celex}_annexes"
                    store_bytes(suffix, fmt, lang, content)
                log(f"    {fmt}: 300 -> {len(docs)} stream(s)")
                return fmt, [(role, to_text(fmt, content)) for role, content, _ in docs]

            if resp.status_code == 406:
                problems.append(f"{fmt}: 406, format not available for this CELEX")
                continue
            if resp.status_code == 404:
                problems.append(f"{fmt}: 404, no such document in this format")
                continue
            if resp.status_code != 200 or not resp.content:
                problems.append(f"{fmt}: HTTP {resp.status_code}, {len(resp.content)} bytes")
                continue

            blob = resp.content
            store_bytes(celex, fmt, lang, blob)
            log(f"    {fmt}: 200, {len(blob)} bytes")

        try:
            return fmt, [("act", to_text(fmt, blob))]
        except ValueError as exc:
            problems.append(f"{fmt}: {exc}")
            continue

    raise FetchError("; ".join(problems) or "no formats attempted")


def to_text(fmt, blob):
    if fmt == "xhtml":
        return xhtml_to_text(decode(blob))
    if fmt == "fmx4":
        return formex_to_text(blob)
    return pdf_to_text(blob)


CONSOLIDATED_DATE = re.compile(r"\b(0\d{4}[A-Z]{1,2}\d{4})-(\d{8})\b")


def resolve_consolidated(base_celex, lang, log):
    """
    "latest" -> the newest consolidation date, read from the base act's branch
    notice. Returns (celex_with_date, date_str) or (None, None) when the act
    has never been consolidated.
    """
    lang3 = LANG3.get(lang.upper(), lang.lower())
    resp = get_with_retry(CELLAR.format(celex=base_celex), "application/xml;notice=branch", lang3)
    if resp.status_code != 200:
        return None, None
    family = consolidated_celex(base_celex)
    dates = sorted({d for c, d in CONSOLIDATED_DATE.findall(resp.text) if c == family})
    if not dates:
        return None, None
    log(f"    consolidations available: {', '.join(dates)}")
    return f"{family}-{dates[-1]}", dates[-1]


# ---------------------------------------------------------------------------
# One manifest entry
# ---------------------------------------------------------------------------

def write_text(path, text, overwrite, dry_run=False):
    """
    Existing source texts are hand-curated inputs to work already done (the
    440k-char sources/ets.txt, for one), so a fetch never silently replaces
    one. --overwrite is the deliberate opt-in.
    """
    if dry_run:
        return len(text)
    if os.path.exists(path) and not overwrite:
        with open(path, encoding="utf-8") as fh:
            if fh.read() == text:
                return len(text)
        raise FetchError(
            f"{os.path.basename(path)} already exists with different content; "
            "pass --overwrite to replace it"
        )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return len(text)


def process(slug, entry, formats, refresh, overwrite, dry_run, log):
    """Fetch, verify and hand off one slug. Returns the provenance record."""
    lang = entry.get("lang", "EN")
    celex = entry["celex"]
    kind = entry.get("kind") or celex_kind(celex)
    declared_status = entry.get("status") or status_for_kind(kind)

    record = {
        "slug": slug,
        "celex": celex,
        "kind": kind,
        "status": declared_status,
        "lang": lang,
        "com": entry.get("com"),
        "procedure": entry.get("procedure"),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "outputs": [],
        "prior_rule_sources": [],
    }

    # The CELEX sector digit is the authority on proposal vs law; a manifest
    # that disagrees with it is a manifest bug worth surfacing.
    derived = celex_kind(celex)
    if derived != "unknown" and kind == "consolidated" and derived == "adopted":
        pass  # consolidated_date resolution below turns 3... into 0...
    elif derived != "unknown" and derived != kind:
        record.setdefault("warnings", []).append(
            f"manifest says kind={kind} but CELEX sector implies {derived}"
        )
    if status_for_kind(kind) != declared_status:
        record.setdefault("warnings", []).append(
            f"manifest says status={declared_status} but kind={kind} implies {status_for_kind(kind)}"
        )

    target = celex
    fetched_kind = kind
    if kind == "consolidated":
        requested = entry.get("consolidated_date", "latest")
        base = celex if celex_sector(celex) == "3" else "3" + celex[1:]
        if requested == "latest":
            resolved, date = resolve_consolidated(base, lang, log)
            if not resolved:
                # Honest fallback: some adopted acts are never consolidated.
                log("    no consolidated version; falling back to the original text")
                record["consolidated"] = "unavailable"
                target = base
                fetched_kind = "adopted"
            else:
                target = resolved
                record["consolidated_date"] = date
        else:
            target = f"{consolidated_celex(base)}-{requested}"
            record["consolidated_date"] = requested
    record["fetched_celex"] = target

    log(f"  fetching {target} ({fetched_kind}, {lang})")
    try:
        fmt, docs = fetch_documents(target, lang, formats, refresh, log)
    except FetchError as exc:
        # Recovery belt: a hand-entered CELEX can be wrong or stale. The COM
        # number gives a second candidate, and the procedure code on the cover
        # decides whether what comes back is really this entry's document --
        # so a wrong guess is rejected rather than silently substituted.
        candidate = celex_from_com(entry.get("com")) if fetched_kind == "proposal" else None
        if not candidate or candidate == target:
            raise
        log(f"    {target} did not resolve; trying {candidate} derived from {entry['com']}")
        fmt, docs = fetch_documents(candidate, lang, formats, refresh, log)
        act = next((t for r, t in docs if r == "act"), docs[0][1])
        if procedure_in_head(act[:6000], entry.get("procedure")) is False:
            raise FetchError(
                f"{target} did not resolve and the COM-derived {candidate} carries a "
                f"different procedure than {entry.get('procedure')}"
            ) from exc
        record.setdefault("warnings", []).append(
            f"manifest CELEX {target} did not resolve; used {candidate} derived from "
            f"{entry['com']}, confirmed by procedure {entry.get('procedure')}"
        )
        target = candidate
        record["fetched_celex"] = target
    record["format"] = fmt

    has_annex_doc = any(role == "annex" for role, _ in docs)
    for role, text in docs:
        errs = verify(
            text,
            role=role,
            celex=target,
            kind=fetched_kind,
            com=entry.get("com"),
            procedure=entry.get("procedure"),
            # Annexes carried as their own document need no marker in the act.
            expect_annexes=False,
            lang=lang,
        )
        if errs:
            raise FetchError(f"{role} document failed verification: {'; '.join(errs)}")

    for role, text in docs:
        name = f"{slug}.txt" if role == "act" else f"{slug}_annexes.txt"
        path = os.path.join(SOURCES_DIR, name)
        size = write_text(path, text, overwrite, dry_run)
        record["outputs"].append({"role": role, "file": name, "chars": size})
        log(f"    verified -> sources/{name} ({size} chars)")
    record["annexes"] = has_annex_doc

    # An act needs the text it changes, or the before/after delta has no
    # prior-rule source.
    #
    # This used to run only for proposals, on the assumption that a delta is
    # always a proposal amending something. An adopted regulation that REPEALS
    # a directive breaks that assumption: PPWR replaces 94/62/EC outright, and
    # the deletion guardrail cannot resolve a single prior_rule without the
    # directive's text -- but PPWR is adopted, so it got nothing. The condition
    # is therefore about whether the act changes an earlier one, not about its
    # own status.
    prior_targets = list(entry.get("amends", []))
    prior_targets += [t for t in entry.get("repeals", {}) if t not in prior_targets]
    if prior_targets:
        for amended in prior_targets:
            log(f"  prior rule: {amended}")
            resolved, date = resolve_consolidated(amended, lang, log)
            prior_celex = resolved or amended
            consolidated_note = date or "unavailable"
            try:
                pfmt, pdocs = fetch_documents(prior_celex, lang, formats, refresh, log)
            except FetchError as exc:
                record["prior_rule_sources"].append(
                    {"celex": prior_celex, "status": "fetch_failed", "reason": str(exc)}
                )
                log(f"    FAILED: {exc}")
                continue
            ptext = "\n\n".join(t for r, t in pdocs if r == "act") or pdocs[0][1]
            perrs = verify(
                ptext,
                role="prior",
                celex=prior_celex,
                kind="consolidated" if resolved else "adopted",
                lang=lang,
            )
            if perrs:
                record["prior_rule_sources"].append(
                    {"celex": prior_celex, "status": "fetch_failed", "reason": "; ".join(perrs)}
                )
                log(f"    FAILED verification: {'; '.join(perrs)}")
                continue
            name = f"{slug}_prior_{prior_celex}.txt"
            size = write_text(os.path.join(SOURCES_DIR, name), ptext, overwrite, dry_run)
            record["prior_rule_sources"].append(
                {
                    "celex": prior_celex,
                    "status": "ok",
                    "format": pfmt,
                    "consolidated_date": consolidated_note,
                    "file": name,
                    "chars": size,
                }
            )
            log(f"    verified -> sources/{name} ({size} chars)")

    return record


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="manifest slugs to fetch (default: all)")
    ap.add_argument("--refresh", action="store_true", help="ignore the on-disk cache")
    ap.add_argument("--overwrite", action="store_true", help="replace existing sources/<slug>.txt")
    ap.add_argument("--dry-run", action="store_true", help="fetch and verify but write nothing")
    ap.add_argument("--formats", default=",".join(DEFAULT_FORMATS), help="format order")
    args = ap.parse_args()

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    bad = [f for f in formats if f not in ACCEPT]
    if bad:
        ap.error(f"unknown format(s): {', '.join(bad)}")

    with open(MANIFEST_PATH, encoding="utf-8") as fh:
        manifest = json.load(fh)

    slugs = args.slugs or list(manifest)
    missing = [s for s in slugs if s not in manifest]
    if missing:
        ap.error(f"not in manifest: {', '.join(missing)}")

    def log(msg):
        print(msg, flush=True)

    results = {}
    failed = []
    for slug in slugs:
        log(f"{slug}:")
        try:
            results[slug] = process(slug, manifest[slug], formats, args.refresh, args.overwrite, args.dry_run, log)
        except FetchError as exc:
            log(f"  FETCH FAILED: {exc}")
            results[slug] = {
                "slug": slug,
                "celex": manifest[slug].get("celex"),
                "status": "fetch_failed",
                "reason": str(exc),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            failed.append(slug)

    # Provenance sidecars, one per slug, next to the text they describe.
    for slug, record in ({} if args.dry_run else results).items():
        with open(os.path.join(SOURCES_DIR, f"{slug}.fetch.json"), "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    ok = [s for s in slugs if s not in failed]
    log("")
    log(f"{len(ok)}/{len(slugs)} fetched and verified" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

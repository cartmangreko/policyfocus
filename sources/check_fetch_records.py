#!/usr/bin/env python3
"""Every fetch record carries a body on disk or an explicit refusal class.

    python3 sources/check_fetch_records.py           # the gate
    python3 sources/check_fetch_records.py --list     # every defective record

WHY THIS EXISTS, AND IT HID TWENTY OF THE LARGEST WORKS IN EUROPE. On 15
September 2026 the steel census fetched the gem.wiki page of all 132 European
plants and believed it had. Twenty had returned nothing: `urllib` encodes its
request line as ASCII and refuses a URL with a diacritic in it, so every works
whose name carries one was never requested at all — SSAB Luleå and Oxelösund,
which are the HYBRIT sites; ArcelorMittal Kraków, Dąbrowa Górnicza and
Eisenhüttenstadt; Liepājas Metalurgs; Hüttenwerke Krupp Mannesmann; Saarstahl
Völklingen; U. S. Steel Košice.

**THE INDEX RECORDED A FETCH THAT HAD HAPPENED AND RETURNED NOTHING**, which is
the worst shape a record can take: the plant looked searched and was not. Had the
census classed on that state it would have reported "searched, none found" on the
very works where the transition is happening, and the gap table would have summed
perfectly while being wrong.

THE DISTINCTION THE GATE DRAWS, and it is the whole point:

  A PUBLISHER REFUSAL is an answer. 403, 404, 503, a DNS failure, a timeout, a
  200 with an empty body — in every one of these the request left this machine
  and something came back, or nothing came back for a reason outside it. That is
  a finding about the source and it is allowed to stand with no body on disk.

  A CLIENT-SIDE FAILURE IS NOT AN ANSWER. UnicodeEncodeError, and anything else
  that means the request was never sent, says nothing whatever about the
  publisher. Recording it in the outcome column next to the refusals makes it
  read as one. It is a defect in this register's own machinery and the gate
  blocks on it.

SO: a record with no body on disk must name a refusal the PUBLISHER gave. A
record that names a client-side failure is `fetched, empty, no refusal` and is
printed by name.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# {sector: (path, shape)}. `flat` is {"fetches": [...]}; `keyed` is {hash: {...}}.
INDEXES = {
    "cement and CCS": ("sources/cache/ccs/index.json", "flat"),
    "batteries": ("sources/cache/batteries/index.json", "flat"),
    "steel": ("sources/cache/steel/index.json", "flat"),
    # ADDED 18 SEPTEMBER 2026. The audit named four indexes and the largest was not among
    # them: the hydrogen pass has more fetch records than the other three together, and it
    # carries records whose outcome is `InvalidURL` — the same client-side failure as the
    # diacritic one, from a space in a path. An audit that omits the biggest index is an
    # audit of the indexes somebody remembered.
    "hydrogen": ("sources/cache/hydrogen/index.json", "flat"),
    # ADDED 19 SEPTEMBER 2026, brief 11. The cross-sector funder pass reads the
    # Commission's own award documents and files them under `funders` rather than
    # under a sector, because a funder is not a sector. Same rule as the five above:
    # the index is tracked and the bodies are not.
    "funders": ("sources/cache/funders/index.json", "flat"),
    "dependency sweep": ("sources/dependency_cache/index.json", "keyed"),
}

# A refusal the publisher gave, or the network gave on its behalf. All of these
# are answers and may stand with no body.
PUBLISHER_REFUSAL = re.compile(
    r"^\s*\d{3}\b"                      # an HTTP status
    r"|URLError|HTTPError|timed out|timeout|TimeoutError"
    r"|does not resolve|Could not resolve|Failed to connect"
    r"|RemoteDisconnected|ConnectionReset|IncompleteRead|SSLError|CertificateError"
    r"|LibreSSL|SSL|curl: \(\d+\)"
    r"|empty body"                      # a 200 that said nothing: scope.md calls this a refusal
    r"|retrieved by hand",              # a hand retrieval, indexed with no request
    re.I)

# A failure of this register's own machinery. The request never left. These are
# the defect.
CLIENT_DEFECT = re.compile(
    r"UnicodeEncodeError|UnicodeDecodeError|UnicodeError"
    r"|InvalidURL|LocationParseError|MissingSchema|InvalidSchema",
    re.I)


def records(path: str, shape: str) -> list[dict]:
    p = ROOT / path
    if not p.exists():
        return []
    doc = json.loads(p.read_text(encoding="utf-8"))
    if shape == "flat":
        return doc.get("fetches", [])
    return [v for v in doc.values() if isinstance(v, dict)]


def outcome_of(r: dict) -> str:
    """Whatever this index calls the result. The shapes differ by sector."""
    bits = [r.get("outcome"), r.get("error"), r.get("status"), r.get("http")]
    return " ".join(str(b) for b in bits if b not in (None, ""))


def has_body(r: dict) -> bool:
    return bool(r.get("sha256") or r.get("sha"))


def main() -> int:
    show = "--list" in sys.argv
    total = 0
    defects: list[tuple[str, dict, str]] = []
    nonascii_total = 0

    print("check_fetch_records: a record with no body must name a refusal the "
          "publisher gave.\n")
    for sector, (path, shape) in INDEXES.items():
        rs = records(path, shape)
        if not rs:
            print(f"  {sector:<18} no index at {path}")
            continue
        total += len(rs)
        bodyless = [r for r in rs if not has_body(r)]
        bad = []
        for r in bodyless:
            o = outcome_of(r)
            # A DEFECTIVE RECORD MAY STAND IF IT SAYS SO AND NAMES ITS RECOVERY.
            # This register does not delete fetches (D42), so the failure stays on
            # the record; what the gate requires is that it be labelled a defect
            # rather than left in the outcome column reading like a refusal, and
            # that it point at the re-fetch that replaced it.
            if r.get("defect") and r.get("superseded_by"):
                continue
            if CLIENT_DEFECT.search(o) or not PUBLISHER_REFUSAL.search(o):
                bad.append(r)
                defects.append((sector, r, o))
        na = sum(1 for r in rs if any(ord(c) > 127 for c in str(r.get("url", ""))))
        nonascii_total += na
        flag = "" if not bad else f"  <-- {len(bad)} DEFECTIVE"
        print(f"  {sector:<18} records={len(rs):<5} no body={len(bodyless):<4} "
              f"non-ASCII URL={na:<4}{flag}")

    print(f"\n  {total} fetch records across {len(INDEXES)} indexes; "
          f"{nonascii_total} carry a non-ASCII URL.")

    if defects:
        print(f"\nFETCHED, EMPTY, NO REFUSAL ({len(defects)}) — the request never "
              f"left this machine, so the record says nothing about the publisher "
              f"and must not be read as though it did:")
        for sector, r, o in defects[: (10 ** 6 if show else 25)]:
            print(f"  [{sector}] {o[:40]:<40} {str(r.get('url'))[:80]}")
        if not show and len(defects) > 25:
            print(f"  ... and {len(defects) - 25} more; run with --list")
        print("\n  Re-fetch these through the corrected reader. A class that rests "
              "on one of them is reopened, not assumed.")
        return 1

    print("\ncheck_fetch_records: OK — every bodyless record names a refusal the "
          "publisher gave.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

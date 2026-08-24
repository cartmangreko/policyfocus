"""
The watch agent: find EU acts the register should know about, and open a PR.

Runs on a schedule (.github/workflows/watch.yml). It discovers candidate
documents from CELLAR, drops the ones it has seen before, asks a model whether
each one is in scope, ingests the clear cases, and assembles a pull request for
review. It never merges anything and it never edits main.

    python3 sources/watch.py --seed        # record today's world as "seen", ingest nothing
    python3 sources/watch.py --dry-run     # discover and triage, write nothing
    python3 sources/watch.py               # the real run


WHY A PULL REQUEST AND NOT A COMMIT
===================================
Every ingested row changes what the site tells people the law requires. A
mistake here is not a broken build, it is a false statement about a legal duty.
So the agent's output is a proposal: the branch, the diff, and the triage
reasoning that produced it, in a PR body a human reads before merging. The
agent has no path to main.


TWO DISCOVERY CHANNELS
======================
(a) THE WATCHLIST -- what the manifest already tracks moved.

    For each tracked CELEX: the other documents in its procedure dossier (the
    Council position, the adopted act, the corrigendum), and newer consolidated
    versions of the prior rules it amends. This channel is high precision and
    is the one to trust first: everything it finds is definitionally related to
    something already in the register.

(b) THE TOPIC QUERY -- something in scope that nobody told us about.

    A narrow EuroVoc query over recent documents. Lower precision by
    construction, which is why triage exists and why the concept list in
    watch_config.json is deliberately short.


FAILING LOUDLY
==============
A watch agent that fails quietly is worse than no watch agent: the register
goes stale while the runs stay green, and nobody notices for months. So:

  * A discovery error is a failure, not an empty result. If CELLAR is down the
    run exits non-zero rather than reporting "nothing new".
  * A suspicious zero is a failure. The watchlist channel is anchored on CELEX
    values known to exist; if it returns nothing at all, the query broke rather
    than the world going quiet. A genuine no-op still returns the anchors.
  * Only a run that discovered candidates and found none of them new exits 0
    with "checked, nothing new".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOURCES = Path(__file__).resolve().parent
ROOT = SOURCES.parent

MANIFEST_PATH = SOURCES / "manifest.json"
CONFIG_PATH = SOURCES / "watch_config.json"
SEEN_PATH = SOURCES / "seen.json"
SCOPE_PATH = SOURCES / "scope.md"

SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
CDM = "http://publications.europa.eu/ontology/cdm#"

REQUEST_GAP_S = 1.0
TIMEOUT_S = 120
RETRIES = 3
RETRY_BACKOFF_S = 5.0

_last_request = 0.0


class WatchError(Exception):
    """Anything that means the run cannot be trusted. Always exits non-zero."""


# ---------------------------------------------------------------------------
# CELLAR
# ---------------------------------------------------------------------------


def sparql(query: str, *, what: str) -> list[dict]:
    """Run a SPARQL query. Raises rather than returning empty on failure."""
    global _last_request

    body = urllib.parse.urlencode(
        {"query": query, "format": "application/sparql-results+json"}
    ).encode()

    last_error: Exception | None = None
    for attempt in range(RETRIES):
        gap = REQUEST_GAP_S - (time.time() - _last_request)
        if gap > 0:
            time.sleep(gap)
        _last_request = time.time()

        req = urllib.request.Request(
            SPARQL,
            data=body,
            headers={
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "policyfocus-watch/1.0 (+https://github.com/cartmangreko/policyfocus)",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return [
                {k: v.get("value") for k, v in row.items()}
                for row in payload["results"]["bindings"]
            ]
        except Exception as exc:  # noqa: BLE001 -- retry anything, then surface it
            last_error = exc
            if attempt < RETRIES - 1:
                time.sleep(RETRY_BACKOFF_S * (attempt + 1))

    raise WatchError(f"CELLAR query failed after {RETRIES} attempts ({what}): {last_error}")


def q_literal(value: str) -> str:
    """A CELEX literal as CELLAR stores it: xsd:string-typed, not a plain literal."""
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'^^<http://www.w3.org/2001/XMLSchema#string>"


# ---------------------------------------------------------------------------
# channel (a): the watchlist
# ---------------------------------------------------------------------------


def discover_watchlist(manifest: dict, cfg: dict) -> tuple[list[dict], list[str]]:
    """Documents related to what the manifest already tracks.

    Returns (candidates, notes). Notes record decisions worth seeing in the run
    report -- most importantly which dossiers were skipped for being too broad.
    """
    candidates: dict[str, dict] = {}
    notes: list[str] = []
    anchors_resolved = 0

    for slug, entry in sorted(manifest.items()):
        celex = entry["celex"]

        dossiers = sparql(
            f"""
            PREFIX cdm: <{CDM}>
            SELECT DISTINCT ?dossier (COUNT(DISTINCT ?member) AS ?size) WHERE {{
              ?anchor cdm:resource_legal_id_celex {q_literal(celex)} ;
                      cdm:work_part_of_dossier ?dossier .
              ?w cdm:work_part_of_dossier ?dossier ;
                 cdm:resource_legal_id_celex ?member .
            }} GROUP BY ?dossier
            """,
            what=f"dossiers of {celex}",
        )
        if dossiers:
            anchors_resolved += 1

        for row in dossiers:
            size = int(row["size"])
            if size > cfg["watchlist"]["max_dossier_members"]:
                notes.append(
                    f"{slug}: skipped a {size}-member dossier as too broad to be a "
                    f"procedure (guard is {cfg['watchlist']['max_dossier_members']})"
                )
                continue

            members = sparql(
                f"""
                PREFIX cdm: <{CDM}>
                SELECT DISTINCT ?celex ?date ?title WHERE {{
                  ?w cdm:work_part_of_dossier <{row['dossier']}> ;
                     cdm:resource_legal_id_celex ?celex ;
                     cdm:work_date_document ?date .
                  OPTIONAL {{ ?w cdm:work_title ?title }}
                }}
                """,
                what=f"members of a dossier of {celex}",
            )
            for m in members:
                _put_candidate(
                    candidates,
                    m,
                    channel="watchlist",
                    why=f"in the same procedure dossier as {celex} ({slug})",
                )

        if not cfg["watchlist"]["follow_consolidations"]:
            continue

        # Newer consolidations of the prior rules this act amends. A new
        # consolidated text means the baseline the register measures against
        # has moved, even though no new act was adopted.
        for prior in sorted(entry.get("amends", [])):
            family = "0" + prior[1:] if prior[:1] == "3" else prior
            base = family.split("-")[0]
            versions = sparql(
                f"""
                PREFIX cdm: <{CDM}>
                SELECT DISTINCT ?celex WHERE {{
                  ?w cdm:resource_legal_id_celex ?celex .
                  FILTER(STRSTARTS(STR(?celex), '{base}-'))
                }}
                """,
                what=f"consolidations of {prior}",
            )
            for v in versions:
                _put_candidate(
                    candidates,
                    {"celex": v["celex"], "date": None, "title": None},
                    channel="watchlist",
                    why=f"consolidated version of {prior}, a prior rule {slug} amends",
                )

    if manifest and anchors_resolved == 0:
        raise WatchError(
            "the watchlist channel resolved none of its "
            f"{len(manifest)} anchor CELEXes. Those are known to exist, so this is a "
            "broken query or a changed CELLAR schema, not a quiet week."
        )

    return list(candidates.values()), notes


# ---------------------------------------------------------------------------
# channel (b): the topic query
# ---------------------------------------------------------------------------


def discover_topic(cfg: dict) -> list[dict]:
    topic = cfg["topic"]
    since = (datetime.now(timezone.utc) - timedelta(days=topic["lookback_days"])).date()
    values = " ".join(f"<{c['uri']}>" for c in topic["eurovoc_concepts"])

    rows = sparql(
        f"""
        PREFIX cdm: <{CDM}>
        SELECT DISTINCT ?celex ?date ?title WHERE {{
          VALUES ?c {{ {values} }}
          ?w cdm:work_is_about_concept_eurovoc ?c ;
             cdm:resource_legal_id_celex ?celex ;
             cdm:work_date_document ?date .
          OPTIONAL {{ ?w cdm:work_title ?title }}
          FILTER(?date >= '{since}'^^<http://www.w3.org/2001/XMLSchema#date>)
        }} ORDER BY DESC(?date)
        """,
        what="EuroVoc topic query",
    )

    labels = ", ".join(c["label"] for c in topic["eurovoc_concepts"])
    candidates: dict[str, dict] = {}
    for row in rows:
        _put_candidate(
            candidates,
            row,
            channel="topic",
            why=f"published since {since} and indexed under: {labels}",
        )
    return list(candidates.values())


def _put_candidate(store: dict, row: dict, *, channel: str, why: str):
    celex = (row.get("celex") or "").strip()
    if not celex:
        return
    existing = store.get(celex)
    if existing is None:
        store[celex] = {
            "celex": celex,
            "date": row.get("date"),
            "title": (row.get("title") or "").strip() or None,
            "channel": channel,
            "why": why,
        }
    else:
        # A document both channels found is a watchlist hit -- the stronger
        # provenance wins, and the reason gets both.
        if existing["channel"] != channel:
            existing["channel"] = "watchlist"
            existing["why"] = f"{existing['why']}; also matched the topic query"
        existing["title"] = existing["title"] or (row.get("title") or "").strip() or None
        existing["date"] = existing["date"] or row.get("date")


# ---------------------------------------------------------------------------
# structural filter
# ---------------------------------------------------------------------------

SECTOR5_TYPE = re.compile(r"^5\d{4}([A-Z]{2})")
SECTOR3_TYPE = re.compile(r"^3\d{4}([A-Z])")

INSTRUMENT = {"L": "directive", "R": "regulation", "D": "decision",
              "H": "recommendation", "A": "opinion", "X": "other"}


def structurally_eligible(celex: str, cfg: dict, manifest: dict) -> tuple[bool, str]:
    """Cheap type filter, applied before triage is paid for.

    Only excludes documents that scope.md rules out by DOCUMENT TYPE, or that
    the register already tracks. Anything excluded on CONTENT goes to the model,
    not to this function -- a filter that guesses at substance from a CELEX is
    how a measure gets dropped without anyone deciding to drop it.
    """
    rules = cfg["celex"]

    # The manifest's own acts come back as members of their own dossiers.
    # They are already in the register; re-triaging them would spend a call to
    # be told what the manifest already says.
    for slug, entry in manifest.items():
        if entry.get("celex") == celex:
            return False, f"already tracked in the manifest as '{slug}'"

    sector = celex[:1]
    if sector not in rules["allowed_sectors"]:
        return False, f"CELEX sector {sector} is not tracked"

    for pattern in rules.get("exclude_patterns", []):
        if re.search(pattern, celex):
            return False, f"matches excluded CELEX pattern {pattern}"

    if sector == "3":
        m = SECTOR3_TYPE.match(celex)
        if not m:
            # A consolidated-style or otherwise unusual sector-3 CELEX. Not
            # confidently excludable by type, so it goes to triage.
            return True, ""
        letter = m.group(1)
        if letter not in rules["allowed_sector3_types"]:
            return False, (
                f"sector-3 descriptor {letter} is a {INSTRUMENT.get(letter, 'non-binding act')}, "
                "out of scope by type (scope.md: recommendations and opinions bind nobody)"
            )

    if sector == "5":
        m = SECTOR5_TYPE.match(celex)
        if not m:
            return False, "unreadable sector-5 CELEX"
        if m.group(1) not in rules["allowed_sector5_types"]:
            return False, (
                f"sector-5 document type {m.group(1)} is out of scope by type "
                "(scope.md: staff working documents and communications)"
            )
    return True, ""


# ---------------------------------------------------------------------------
# triage
# ---------------------------------------------------------------------------

TRIAGE_SYSTEM = """You triage EU legal documents for the Eufabric register.

You are shown the scope standard, then one candidate document. Decide whether it
belongs in the register: "in", "borderline", or "out".

You are working from a title and a CELEX, not the full text. Say what that
evidence supports and nothing more. If the title does not tell you whether the
act creates an obligation, that is exactly what "borderline" is for -- reach for
it rather than guessing in either direction. A wrong "out" drops a legal duty
silently; a wrong "in" produces a register row someone has to unwind. Borderline
costs a human one minute and is the correct answer under real uncertainty.

Ground your reasoning in the specific document. "Appears related to emissions
trading" is not a reason; "amends the free-allocation benchmark values in Annex
I of the ETS Directive, which the register tracks" is."""


class Triage:
    """Wraps the classifier so a missing key or SDK is a clear failure."""

    def __init__(self, cfg: dict, scope: str):
        self.cfg = cfg["triage"]
        self.scope = scope
        try:
            import anthropic  # noqa: PLC0415 -- optional until triage actually runs
        except ImportError as exc:
            raise WatchError(
                "triage needs the anthropic SDK: pip install -r sources/requirements.txt"
            ) from exc
        if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
            raise WatchError("triage needs ANTHROPIC_API_KEY in the environment")
        self.client = anthropic.Anthropic()

        from typing import Literal  # noqa: PLC0415

        from pydantic import BaseModel, Field  # noqa: PLC0415

        class Verdict(BaseModel):
            # Literal rather than str: it becomes a JSON-schema enum, so the
            # three verdicts are enforced by the API rather than by hoping.
            verdict: Literal["in", "borderline", "out"] = Field(
                description="Whether the document belongs in the register"
            )
            reason: str = Field(
                description=(
                    "One or two sentences naming what in this specific document "
                    "decided it, tied to a rule in the scope standard."
                )
            )
            touches: list[str] = Field(
                default_factory=list,
                description=(
                    "Tracked sector slugs the document appears to reach, from: "
                    "steel, alu, cement, glass, chem, power, waste, ship, air, "
                    "auto, build, batsol, clean, ccs. Empty if none are evident."
                ),
            )

        self.Verdict = Verdict

    def classify(self, candidate: dict) -> dict:
        # The scope standard is the stable prefix and is identical on every
        # call in the run, so it carries the cache breakpoint; the candidate
        # goes after it and varies per call.
        response = self.client.messages.parse(
            model=self.cfg["model"],
            max_tokens=2000,
            system=[
                {"type": "text", "text": TRIAGE_SYSTEM},
                {
                    "type": "text",
                    "text": f"<scope_standard>\n{self.scope}\n</scope_standard>",
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            thinking={"type": "adaptive"},
            output_config={"effort": self.cfg["effort"]},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Candidate document:\n"
                        f"  CELEX: {candidate['celex']}\n"
                        f"  Date: {candidate.get('date') or 'unknown'}\n"
                        f"  Title: {candidate.get('title') or '(none recorded in CELLAR)'}\n"
                        f"  Found because: {candidate['why']}\n\n"
                        "Does it belong in the register?"
                    ),
                }
            ],
        )
        if response.stop_reason == "refusal":
            raise WatchError(
                f"triage of {candidate['celex']} was declined by the model "
                f"({getattr(response.stop_details, 'category', None)})"
            )
        parsed = response.parsed_output
        if parsed is None:
            raise WatchError(f"triage of {candidate['celex']} returned no parsable verdict")

        verdict = parsed.verdict.strip().lower()
        if verdict not in {"in", "borderline", "out"}:
            # The schema enum should make this unreachable. If it ever fires,
            # the answer is borderline, never "out" -- "out" is the direction
            # that loses a measure with nobody deciding to lose it.
            verdict = "borderline"
        return {"verdict": verdict, "reason": parsed.reason, "touches": parsed.touches}


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------


def slug_for(celex: str, manifest: dict) -> str:
    base = f"watch-{celex.lower()}"
    slug, n = base, 2
    while slug in manifest:
        slug, n = f"{base}-{n}", n + 1
    return slug


def ingest(candidates: list[dict], manifest: dict, log) -> tuple[list[str], list[str]]:
    """Upsert the manifest, fetch and verify, then run the graph gate.

    Returns (ingested_slugs, failures). A fetch failure is reported and the
    slug is rolled back out of the manifest -- a manifest entry whose text
    never verified would make the next run think the act is handled.
    """
    ingested: list[str] = []
    failures: list[str] = []

    for c in candidates:
        celex = c["celex"]
        slug = slug_for(celex, manifest)
        manifest[slug] = {
            "celex": celex,
            "kind": "proposal" if celex[:1] == "5" else "adopted",
            "lang": "EN",
            "status": "proposed" if celex[:1] == "5" else "adopted",
            "amends": [],
            "_discovered_by": "watch",
            "_discovered_at": datetime.now(timezone.utc).date().isoformat(),
        }
        _write_json(MANIFEST_PATH, manifest)

        log(f"  fetching {slug} ({celex})")
        result = subprocess.run(
            [sys.executable, str(SOURCES / "fetch_eurlex.py"), slug],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
            failures.append(f"{celex}: fetch/verify failed -- {' / '.join(tail)}")
            manifest.pop(slug, None)
            _write_json(MANIFEST_PATH, manifest)
            continue

        ingested.append(slug)

    if ingested:
        log("  rebuilding the graph")
        gate = subprocess.run(
            [sys.executable, str(SOURCES / "build_graph.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if gate.returncode != 0:
            # The gate writes nothing when it fails, so the graph on disk is
            # still the last good one. Report loudly and let the human see it.
            failures.append(f"graph gate failed: {gate.stderr.strip()[:400]}")

    return ingested, failures


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def render_report(run: dict) -> str:
    lines = [
        "# Watch run",
        "",
        f"- Ran: {run['ran_at']}",
        f"- Discovered: {run['discovered']} candidates "
        f"({run['by_channel'].get('watchlist', 0)} watchlist, "
        f"{run['by_channel'].get('topic', 0)} topic)",
        f"- Already seen: {run['already_seen']}",
        f"- Filtered by document type: {run['filtered']}",
        f"- Triaged: {run['triaged']}",
        "",
    ]

    if run["in_scope"]:
        lines += ["## In scope -- ingested", ""]
        for c in run["in_scope"]:
            lines += [
                f"### `{c['celex']}`",
                f"{c.get('title') or '_(no title recorded in CELLAR)_'}",
                "",
                f"- **Found:** {c['why']}",
                f"- **Triage:** {c['reason']}",
                f"- **Sectors:** {', '.join(c['touches']) or '_none evident_'}",
                "",
            ]

    if run["borderline"]:
        lines += [
            "## Borderline -- needs a human ruling",
            "",
            "Not ingested. Each of these plausibly belongs but could not be "
            "settled from the title alone.",
            "",
        ]
        for c in run["borderline"]:
            lines += [
                f"- **`{c['celex']}`** — {c.get('title') or '_(no title)_'}",
                f"  - Found: {c['why']}",
                f"  - Triage: {c['reason']}",
            ]
        lines.append("")

    if run["out"]:
        lines += ["<details><summary>Out of scope (" + str(len(run["out"])) + ")</summary>", ""]
        for c in run["out"]:
            lines.append(f"- `{c['celex']}` — {c['reason']}")
        lines += ["", "</details>", ""]

    if run["notes"]:
        lines += ["## Notes", ""] + [f"- {n}" for n in run["notes"]] + [""]

    if run["failures"]:
        lines += [
            "## Failures",
            "",
            "These did not ingest. The run is marked failed so it is not mistaken "
            "for a quiet week.",
            "",
        ] + [f"- {f}" for f in run["failures"]] + [""]

    lines += [
        "---",
        "",
        "Opened by `sources/watch.py`. Nothing here is merged automatically: every "
        "row changes what the site says the law requires, so a human rules on it "
        "first. Check the quoted `source_text` against the fetched act before merging.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def _read_json(path: Path, default=None):
    if not path.exists():
        if default is None:
            raise WatchError(f"missing required file: {path.relative_to(ROOT)}")
        return default
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, payload):
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, sort_keys=True)
        fh.write("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", action="store_true",
                    help="record everything discoverable now as seen; ingest nothing")
    ap.add_argument("--dry-run", action="store_true",
                    help="discover and triage, write nothing")
    ap.add_argument("--no-triage", action="store_true",
                    help="discover only; report candidates without classifying them")
    ap.add_argument("--report", type=Path, help="write the run report here")
    args = ap.parse_args()

    def log(msg):
        print(msg, flush=True)

    try:
        cfg = _read_json(CONFIG_PATH)
        manifest = _read_json(MANIFEST_PATH)
        seen = _read_json(SEEN_PATH, default={"celex": {}})
        scope = SCOPE_PATH.read_text(encoding="utf-8")

        candidates: list[dict] = []
        notes: list[str] = []

        if cfg["watchlist"]["enabled"]:
            log("discovering: watchlist")
            found, notes = discover_watchlist(manifest, cfg)
            candidates += found
            log(f"  {len(found)} candidates")

        if cfg["topic"]["enabled"]:
            log("discovering: topic query")
            found = discover_topic(cfg)
            candidates += found
            log(f"  {len(found)} candidates")

        merged: dict[str, dict] = {}
        for c in candidates:
            _put_candidate(merged, c, channel=c["channel"], why=c["why"])
        candidates = sorted(merged.values(), key=lambda c: c["celex"])

        if not candidates:
            raise WatchError(
                "both channels returned nothing at all. The watchlist is anchored on "
                "CELEXes known to exist, so an empty result is a broken query, not a "
                "quiet week."
            )

        by_channel: dict[str, int] = {}
        for c in candidates:
            by_channel[c["channel"]] = by_channel.get(c["channel"], 0) + 1

        if args.seed:
            for c in candidates:
                seen["celex"][c["celex"]] = {
                    "first_seen": datetime.now(timezone.utc).date().isoformat(),
                    "verdict": "seeded",
                    "channel": c["channel"],
                }
            _write_json(SEEN_PATH, seen)
            log(f"\nseeded {len(candidates)} CELEXes as seen; ingested nothing")
            return 0

        fresh, already = [], 0
        for c in candidates:
            if c["celex"] in seen["celex"]:
                already += 1
            else:
                fresh.append(c)

        eligible, filtered = [], 0
        for c in fresh:
            ok, why_not = structurally_eligible(c["celex"], cfg, manifest)
            if ok:
                eligible.append(c)
            else:
                filtered += 1
                seen["celex"][c["celex"]] = {
                    "first_seen": datetime.now(timezone.utc).date().isoformat(),
                    "verdict": "filtered",
                    "reason": why_not,
                }

        log(f"\n{len(candidates)} discovered, {already} seen before, "
            f"{filtered} filtered by type, {len(eligible)} to triage")

        cap = cfg["triage"]["max_candidates_per_run"]
        if len(eligible) > cap:
            raise WatchError(
                f"{len(eligible)} candidates to triage exceeds the cap of {cap}. "
                "This is almost always a query that got too broad or a CELLAR "
                "backfill, not a real surge -- rule on it before spending the run."
            )

        in_scope, borderline, out = [], [], []
        if eligible and not args.no_triage:
            triage = Triage(cfg, scope)
            for c in eligible:
                log(f"  triaging {c['celex']}")
                c.update(triage.classify(c))
                {"in": in_scope, "borderline": borderline, "out": out}[c["verdict"]].append(c)
        elif eligible:
            borderline = [dict(c, verdict="borderline", reason="triage skipped (--no-triage)",
                               touches=[]) for c in eligible]

        failures: list[str] = []
        if in_scope and not args.dry_run:
            log("\ningesting")
            _, failures = ingest(in_scope, manifest, log)

        if not args.dry_run:
            today = datetime.now(timezone.utc).date().isoformat()
            for c in eligible:
                seen["celex"][c["celex"]] = {
                    "first_seen": today,
                    "verdict": c.get("verdict", "unknown"),
                    "channel": c["channel"],
                }
            _write_json(SEEN_PATH, seen)

        run = {
            "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "discovered": len(candidates),
            "by_channel": by_channel,
            "already_seen": already,
            "filtered": filtered,
            "triaged": len(eligible),
            "in_scope": in_scope,
            "borderline": borderline,
            "out": out,
            "notes": notes,
            "failures": failures,
        }
        report = render_report(run)
        if args.report:
            args.report.write_text(report, encoding="utf-8")
        log("\n" + report)

        if failures:
            return 1
        if not in_scope and not borderline:
            log("\nchecked, nothing new")
        return 0

    except WatchError as exc:
        print(f"\nwatch: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

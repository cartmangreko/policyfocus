"""
The first screen of a sector page: one sentence, why it matters, and the facts.

    python3 build_lead.py             # writes data/transition/lead/*.json
    python3 build_lead.py --check     # rebuilds and diffs; non-zero on drift

WHAT THIS REPLACES, AND WHY
===========================
The sector page opened with a one-sentence lead read from data/prose.json: one
reviewed sentence per sector, written by hand. That does not scale past the
sector somebody is currently thinking about, and it has a worse problem than
scale -- a hand-written lead can say something the page below it no longer
supports, and nothing catches it.

So the lead is computed from the page's own panels, and the discipline that
makes it safe is the one this repository already uses on every other number:

  * The FACTS come first and are the only inputs. Five computed lines, one per
    kind, each selected by the same scores that rank the measures.
  * The SENTENCES are templates over those facts. Every number in a sentence has
    to appear in a fact; every date has to be a fact's as-of date; every sentence
    names the fact ids it came from.
  * A GATE runs before anything is written, and a failure falls back to the
    dullest possible sentence rather than shipping the interesting one.

This is tier 1 of the three-tier prose rule in sources/scope.md -- computed
text, no review needed -- with a tier-2 door: `summary_override` in
data/transition/overrides.json is a reviewed sentence that replaces the
generated one.

THE OVERRIDE NEVER SILENTLY REGENERATES
=======================================
An override is a reviewer's sentence about a particular set of facts. When those
facts move, the sentence may or may not still be true, and only a person can
say. So the facts are fingerprinted, the fingerprint is stored with the
override, and a mismatch sets `override_stale` and prints -- while the override
KEEPS RENDERING. Reverting to generated text on a fingerprint change would
silently discard reviewed prose, which is the failure mode the rule exists to
prevent; showing stale reviewed prose with a flag on the build is the lesser
one, and it is visible on every run.

THE FIVE FACTS
==============
  binding_constraint  the bottleneck the most measure weight lands on
  decisive_exposure   the top-ranked measure with a computable money figure
  pipeline_state      how far the pipeline has got, and how much of it is past FID
  the_gap             the largest sourced gap parameter
  the_latest          the most recent status change, dated

A fact that cannot be computed is omitted rather than faked, and the templates
that would have used it are skipped -- which is what the fallback path is for.

WHAT "LARGEST GAP" MEANS, AND THE UNIT RULE
===========================================
A gap parameter is one flagged `states_gap` -- a number that measures a shortfall
rather than a level. A capture retrofit's capital cost is a level; the premium
near-zero cement carries over conventional cement is a gap.

Largest is computed on the upper bound of the value, and all of a sector's gap
parameters must share a unit or the build fails. This is the same rule the money
score enforces with `scale`: comparing a percentage with a euro figure to decide
which is "largest" is not a comparison, and a sector page that did it would be
stating a ranking it cannot defend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date

import display_vocabulary as dv
import sector_map as sm
import build_importance as bi

OUT_DIR = sm.ROOT / "data" / "transition" / "lead"

# Bumped when a template changes. It is in the output so a diff shows whether a
# sentence moved because the data moved or because the template did.
TEMPLATE_VERSION = 1

# A project at or past this point has committed the money. `funded` is a grant
# award and is deliberately below the line: an Innovation Fund letter is not a
# final investment decision, and the pipeline fact would overstate itself.
COMMITTED = ("fid", "construction", "operating")

# Ordered as a project advances. paused/cancelled are not on the ladder: they
# are where a project left it.
ADVANCE = ("announced", "funded", "fid", "construction", "operating")

# Words that make a claim the facts cannot carry. The generated sentences are
# templates and should never produce one; the gate is here because a template
# edited in a hurry is exactly how one arrives.
JUDGMENT_ADJECTIVES = (
    "critical", "crucial", "significant", "dramatic", "severe", "vital",
    "huge", "massive", "key", "major", "unprecedented", "striking",
    "impressive", "alarming", "dire", "remarkable", "urgent", "stark",
    "important", "essential", "devastating", "extraordinary",
)

MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

_DATE_LONG = re.compile(rf"\b(\d{{1,2}}) ({'|'.join(MONTHS)}) (\d{{4}})\b")
_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_NUMBER = re.compile(r"\d[\d–.,-]*")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _norm_number(token: str) -> str:
    """Compare numbers by their digits and separators, not their typography."""
    return token.replace(",", "").replace("–", "-").rstrip(".-")


def _long_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def _upper_bound(value) -> float:
    """The top of a range, or the number itself. '75-150' -> 150.0"""
    if isinstance(value, (int, float)):
        return float(value)
    parts = re.split(r"[-–]", str(value))
    return max(float(p) for p in parts if p.strip())


def _fact(fid, label, text, as_of, numbers, parts, sourced=(), href=None) -> dict:
    """One fact line.

    `text` is what the page prints. `parts` is the same fact in pieces, and it
    exists so the sentence templates compose from fields rather than from
    sliced-up display strings -- a template that split `text` on an em dash
    would break the day somebody rewrote the line it was slicing.

    `sourced` names the fragments that came from somebody else's document: a
    parameter's unit, an installation's name, a status. They are exempt from the
    display-vocabulary check, because the ruling is about how this platform
    frames itself and the IEA's "% above a conventional plant" is the IEA's
    sentence. Everything outside them is this file's own wording and is checked.
    """
    return {
        "id": fid,
        "label": label,
        "text": text,
        "as_of": as_of,
        "numbers": [_norm_number(n) for n in numbers],
        "parts": parts,
        "sourced": list(sourced),
        "href": href,
    }


# ---------------------------------------------------------------------------
# the facts
# ---------------------------------------------------------------------------

def fact_binding_constraint(bottlenecks: list[dict]) -> dict | None:
    """The bottleneck carrying the most measure weight.

    Weight rather than count: an edge marked 1.0 is a measure the register's own
    wording ties to the constraint, and a 0.5 is a reading. Counting them
    equally would let two weak links outrank one stated one.
    """
    scored = []
    for b in bottlenecks:
        edges = b.get("measures") or []
        weight = sum(m["weight"] for m in edges)
        if weight <= 0:
            continue
        scored.append((weight, len(edges), b))
    if not scored:
        return None
    weight, count, b = max(scored, key=lambda s: (s[0], s[1], s[2]["id"]))
    as_of = max((s.get("date") or "" for s in b["sources"]), default="")
    return _fact(
        "binding_constraint", "Binding constraint",
        f"{b['name']} — a {b['type']} constraint, acted on by {count} ranked measures "
        f"at {weight:g} of combined weight.",
        as_of, [f"{count}", f"{weight:g}"],
        {"name": b["name"], "type": b["type"], "count": count, "weight": f"{weight:g}"},
        sourced=(b["name"],),
        href=f"#bottleneck-{b['id']}",
    )


def fact_decisive_exposure(imp: dict, params: dict, labels: dict) -> dict | None:
    """The top-ranked measure that has a euro figure, with its direction.

    Direction is not decoration here. The ranking sorts on magnitude, and a
    sentence that stated a magnitude without saying which way it points would
    say the same thing about a grant and a levy -- the exact failure
    check_importance.py gates the score against.
    """
    priced = [m for m in imp["measures"]
              if m["in_sector_view"] and m["money"]["computable"]]
    if not priced:
        return None
    m = min(priced, key=lambda m: m["rank"])
    money = m["money"]
    entry = labels.get(m["measure"])
    name = sm.short_label(entry) if entry else m["measure"]

    if money["per_tonne"] is not None:
        figure = f"€{money['per_tonne']:,.2f} per tonne"
        numbers = [f"{money['per_tonne']:,.2f}"]
    else:
        figure = f"€{money['value'] / 1e6:,.0f}m"
        numbers = [f"{money['value'] / 1e6:,.0f}"]

    bearer = money["bearer"].replace("_", " ")
    as_of = max((params[p]["date_of_value"] for p in money["inputs"] if p in params),
                default="")
    return _fact(
        "decisive_exposure", "Decisive exposure",
        f"{name} — {figure} of {money['direction']}, borne by the {bearer}.",
        as_of, numbers,
        {"name": name, "figure": figure, "direction": money["direction"],
         "bearer": bearer},
        sourced=(name,),
        href=f"#measure-{m['file']}-{m['id']}",
    )


def fact_pipeline_state(projects: list[dict]) -> dict | None:
    """How far the pipeline has got, and how much of it has committed money."""
    live = [p for p in projects if p["status"] in ADVANCE]
    if not live:
        return None
    furthest = max(live, key=lambda p: (ADVANCE.index(p["status"]), p["id"]))
    committed = sum(1 for p in projects if p["status"] in COMMITTED)
    as_of = max((h["date"] for p in projects for h in p["status_history"]), default="")
    return _fact(
        "pipeline_state", "Pipeline",
        f"{len(projects)} projects, the furthest of them {furthest['status']} "
        f"({furthest['name']}); {committed} at or past a final investment decision.",
        as_of, [f"{len(projects)}", f"{committed}"],
        {"total": str(len(projects)), "committed": str(committed),
         "furthest": furthest["name"], "furthest_status": furthest["status"]},
        sourced=(furthest["name"],),
        href="#projects",
    )


def fact_the_gap(params: dict, sector: str, bottlenecks: list[dict]) -> dict | None:
    """The largest sourced gap parameter. See the module docstring on units."""
    gaps = [p for p in params.values()
            if p.get("states_gap") and p.get("sector") == sector]
    if not gaps:
        return None
    units = {p["unit"] for p in gaps}
    if len(units) > 1:
        raise SystemExit(
            f"build_lead: {sector}: gap parameters in more than one unit {sorted(units)} — "
            f"'largest' across units is not a comparison. Either they share a unit or the "
            f"page cannot rank them, the same rule the money score enforces with `scale`."
        )
    p = max(gaps, key=lambda p: (_upper_bound(p["value"]), p["id"]))
    # A percentage sits against its number; every other unit stands off it.
    if p["unit"].startswith("%"):
        figure, rest = f"{p['value']}%", p["unit"][1:].strip()
    else:
        figure, rest = f"{p['value']} {p['unit']}", ""
    # Parameters have no anchor of their own -- they render as chips inside the
    # bottleneck they quantify, so the link goes there.
    owner = next((b for b in bottlenecks if p["id"] in b.get("quantified_by", [])), None)
    return _fact(
        "the_gap", "The gap",
        f"{p['name']}: {figure}{' ' + rest if rest else ''}.",
        p["date_of_value"], [str(p["value"])],
        {"figure": figure, "rest": rest, "name": p["name"]},
        sourced=(p["name"], p["unit"], rest),
        href=f"#bottleneck-{owner['id']}" if owner else "#bottlenecks",
    )


def fact_the_latest(projects: list[dict]) -> dict | None:
    """The most recent status change anywhere in the sector's pipeline."""
    events = [(h["date"], p, h) for p in projects for h in p["status_history"]]
    if not events:
        return None
    _, p, h = max(events, key=lambda e: (e[0], e[1]["id"]))
    return _fact(
        "the_latest", "The latest",
        f"{p['name']} moved to {h['status']} on {_long_date(h['date'])}.",
        h["date"], [],
        {"project": p["name"], "status": h["status"], "date": _long_date(h["date"])},
        sourced=(p["name"],),
        href=f"/projects/{p['id']}",
    )


# ---------------------------------------------------------------------------
# the sentences
# ---------------------------------------------------------------------------

def compose(sector_name: str, facts: dict[str, dict]) -> tuple[dict, dict | None]:
    """The two generated blocks, as templates over the facts and nothing else.

    Each names the fact ids it drew on, so a reader following a claim back has a
    path and the gate has something to check. Everything comes out of `parts`:
    no template reads another template's output.
    """
    exposure = facts.get("decisive_exposure")
    constraint = facts.get("binding_constraint")
    gap = facts.get("the_gap")
    pipeline = facts.get("pipeline_state")
    latest = facts.get("the_latest")
    sector = sector_name.lower()

    # THE SENTENCE. What the sector is under: the priced measure and the
    # constraint, in one line, with no verb doing more work than "is".
    if exposure and constraint:
        e = exposure["parts"]
        sentence = {
            "text": f"European {sector} carries {e['figure']} of {e['direction']} from "
                    f"{e['name']} on the {e['bearer']}, and its binding constraint is the "
                    f"{constraint['parts']['name'].lower()}.",
            "from": ["decisive_exposure", "binding_constraint"],
        }
    elif exposure:
        e = exposure["parts"]
        sentence = {
            "text": f"European {sector} carries {e['figure']} of {e['direction']} from "
                    f"{e['name']} on the {e['bearer']}.",
            "from": ["decisive_exposure"],
        }
    elif constraint:
        sentence = {
            "text": f"European {sector}'s binding constraint is the "
                    f"{constraint['parts']['name'].lower()}.",
            "from": ["binding_constraint"],
        }
    else:
        return {"text": "", "from": []}, None

    # WHY IT MATTERS. Two sentences at most: how big the gap is, then what is
    # being built against it and when that last moved.
    parts: list[str] = []
    used: list[str] = []
    if gap:
        g = gap["parts"]
        parts.append(
            f"The largest gap the sector's own numbers state is {g['figure']}"
            f"{' ' + g['rest'] if g['rest'] else ''}"
        )
        used.append("the_gap")
    if pipeline and latest:
        pp, ll = pipeline["parts"], latest["parts"]
        parts.append(
            f"{pp['total']} projects are building against it, {pp['committed']} at or past "
            f"a final investment decision, and the most recent move was {ll['project']} to "
            f"{ll['status']} on {ll['date']}"
        )
        used += ["pipeline_state", "the_latest"]
    if not parts:
        return sentence, None
    why = {"text": ". ".join(parts) + ".", "from": used}
    return sentence, why


# ---------------------------------------------------------------------------
# the gate
# ---------------------------------------------------------------------------

def gate(block: dict, facts: dict[str, dict]) -> list[str]:
    """Every rule from amendment brief 2 §4, applied to one generated block."""
    problems: list[str] = []
    text = block["text"]
    if not text:
        return ["empty"]

    sentences = [s for s in re.split(r"(?<=[.!?]) +", text.strip()) if s]
    if len(sentences) > 2:
        problems.append(f"{len(sentences)} sentences, at most 2 allowed")

    if not block["from"]:
        problems.append("no fact id — a sentence nothing maps to")
    for fid in block["from"]:
        if fid not in facts:
            problems.append(f"names fact {fid!r}, which was not computed")

    known = {n for f in facts.values() for n in f["numbers"]}
    stripped = _DATE_LONG.sub(" ", _ISO.sub(" ", text))
    for token in _NUMBER.findall(stripped):
        if _norm_number(token) not in known:
            problems.append(f"the number {token!r} is in no fact")

    as_ofs = {f["as_of"] for f in facts.values()}
    for m in _DATE_LONG.finditer(text):
        iso = f"{m.group(3)}-{MONTHS.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}"
        if iso not in as_ofs:
            problems.append(f"the date {m.group(0)!r} is no fact's as-of date")

    lowered = text.lower()
    for adjective in JUDGMENT_ADJECTIVES:
        if re.search(rf"\b{adjective}\b", lowered):
            problems.append(f"the judgment adjective {adjective!r}")

    exempt = tuple(frag for f in facts.values() for frag in f["sourced"])
    problems += [f"the banned word {w!r}"
                 for w in dv.violations(text, exempt=exempt)]
    return problems


def fingerprint(facts: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def build(sector: str) -> dict:
    imp = bi.build(sector, bi.date.today().year)
    params = sm.index(sm.load("parameter"))
    bottlenecks = [b for b in sm.load("bottleneck") if b["sector"] == sector]
    projects = [p for p in sm.load("project") if p["sector"] == sector]
    labels = sm.measure_labels()
    sector_name = sm.sectors()[sector]["name"]

    computed = [
        fact_binding_constraint(bottlenecks),
        fact_decisive_exposure(imp, params, labels),
        fact_pipeline_state(projects),
        fact_the_gap(params, sector, bottlenecks),
        fact_the_latest(projects),
    ]
    facts = [f for f in computed if f]
    by_id = {f["id"]: f for f in facts}
    for f in facts:
        dv.check(f["text"], f"build_lead: {sector} fact {f['id']}",
                 exempt=tuple(f["sourced"]))

    sentence, why = compose(sector_name, by_id)
    notes: list[str] = []

    problems = gate(sentence, by_id)
    if problems:
        notes.append(f"the sentence failed its gate ({'; '.join(problems)}) — "
                     f"fell back to the template")
        exposure = by_id.get("decisive_exposure")
        constraint = by_id.get("binding_constraint")
        # The dullest sentence the facts support: the top measure and the
        # binding constraint, named, with nothing composed around them.
        priced = (f"{exposure['parts']['figure']} of {exposure['parts']['direction']} from "
                  f"{exposure['parts']['name']}" if exposure else "no priced measure")
        held = (constraint["parts"]["name"].lower() if constraint else "nothing recorded")
        sentence = {
            "text": f"European {sector_name.lower()}: {priced}, against {held}.",
            "from": [f for f in ("decisive_exposure", "binding_constraint") if f in by_id],
        }
        why = None

    if why:
        problems = gate(why, by_id)
        if problems:
            notes.append(f"why-it-matters failed its gate ({'; '.join(problems)}) — dropped")
            why = None

    sentence["source"] = "generated"
    if why:
        why["source"] = "generated"

    fp = fingerprint(facts)
    doc = {
        "_comment": [
            "BUILT FILE — do not edit. sources/build_lead.py computes it from the sector's",
            "own panels; web/components/LeadBlock.tsx draws it and adds nothing.",
            "A reviewed replacement goes in data/transition/overrides.json under",
            "summary_override, never here.",
        ],
        "sector": sector,
        "template_version": TEMPLATE_VERSION,
        "fingerprint": fp,
        "sentence": sentence,
        "why_it_matters": why,
        "facts": facts,
        "override_stale": False,
        "notes": notes,
    }
    apply_override(doc, sector)
    return doc


def apply_override(doc: dict, sector: str) -> None:
    """A reviewer's sentence, and the flag that says the facts moved under it."""
    store = json.loads(OVERRIDES().read_text(encoding="utf-8"))
    entry = (store.get("summary_overrides") or {}).get(sector)
    if not entry:
        return
    for key in ("sentence", "why_it_matters"):
        text = entry.get(key)
        if not text:
            continue
        doc[key] = {
            "text": text,
            "from": entry.get("from", []),
            "source": "override",
            "reviewed": entry["reviewed"],
        }
    if entry.get("fingerprint") != doc["fingerprint"]:
        doc["override_stale"] = True
        doc["notes"].append(
            f"the reviewed lead was written against facts {entry.get('fingerprint')!r} and the "
            f"facts are now {doc['fingerprint']!r} — it still renders, and it needs re-reading"
        )


def OVERRIDES():
    return sm.ROOT / "data" / "transition" / "overrides.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sector", action="append", default=None)
    args = ap.parse_args()

    sectors = args.sector or ["cement"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = False
    for sector in sectors:
        doc = build(sector)
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = OUT_DIR / f"{sector.replace('/', '__')}.json"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"build_lead: {path} is stale or missing — rebuild it", file=sys.stderr)
                failed = True
                continue
            print(f"build_lead: --check, {sector} matches ({len(doc['facts'])} facts)")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"build_lead: wrote {path} — {len(doc['facts'])} facts")
        print(f"  {doc['sentence']['text']}")
        if doc["why_it_matters"]:
            print(f"  {doc['why_it_matters']['text']}")
        for note in doc["notes"]:
            print(f"  ! {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

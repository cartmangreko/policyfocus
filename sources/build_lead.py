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

THE SIX FACTS
=============
  routes              every route the sector is building, with the count on each
  binding_constraint  the bottleneck the most measure weight lands on
  decisive_exposure   the top-ranked measure with a computable money figure
  pipeline_state      how far the pipeline has got, and how much of it is past FID
  the_gap             the largest sourced gap parameter
  the_latest          the most recent status change, dated

A fact that cannot be computed is omitted rather than faked, and the templates
that would have used it are skipped -- which is what the fallback path is for.

WHAT BRIEF 4 §5 CHANGED, AND WHY IT WAS A REWRITE RATHER THAN AN EDIT
=====================================================================
The first version of these templates composed the facts in the SCHEMA'S OWN
WORDS, and the result was unreadable to anybody who had not read the schema:

    European cement carries EUR75.46 per tonne of cost from CBAM certificates on
    the importer, and its binding constraint is the green premium against
    willingness to pay.

Four things are wrong with that sentence and only one of them is style. It
opens on a per-tonne cost that falls on IMPORTERS, which is not what European
cement pays. It states a percentage ("75-150% above a conventional plant") whose
base is somewhere else on the page. It labels a constraint instead of describing
one. And it does all of it in two clauses, so a reader who loses the thread has
nowhere to pick it up.

The rules now, one per sentence on the surface:

  * The FIRST SENTENCE states the sector's situation, one idea: what it is doing
    and what the open question about it is. No figures.
  * WHY IT MATTERS is one sentence, and it has to work for somebody who does not
    know what a bottleneck is.
  * EACH FACT LINE is one plain sentence with its own subject. Every number says
    what it is a number OF, and carries the as-of date of the value under it.
  * SCHEMA VOCABULARY DOES NOT APPEAR: no constraint, no gap, no exposure, no
    bearer, no willingness to pay. The thing gets described instead of labelled,
    and SCHEMA_WORDS below fails the build if one gets through.

The facts themselves did not change -- the same five are computed from the same
panels by the same selection rules. What changed is that four of them are now
written as sentences and the fifth, the binding constraint, no longer surfaces
at all: it is what the opening sentence is ABOUT, and printing it twice, once as
a sentence and once as a label, was most of what made the block unreadable.

THE THREE AUTHORED VOCABULARIES
===============================
Three maps below turn a closed schema list into English. They are authored, they
are small, and each is keyed to a vocabulary that fails loudly when it grows:

  TRANSITION_VERB   what a sector under this transition is doing
  OPEN_QUESTION     what the open question is, by the type of its binding
                    constraint
  STATUS_VERB       what a project did, by the status it moved to

A missing key raises. That is the point: the day a sixth transition or an eighth
project status is added, this file stops rather than printing a sentence with a
schema word wedged into it.

The fourth vocabulary is not here. `plain_action` -- "capturing the CO2 its kilns
emit" -- is a per-technology field in data/transition/technologies.json, because
it is a fact about that technology rather than about this template.

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
TEMPLATE_VERSION = 3

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

# The schema's own words, banned on this surface by brief 4 §5. They are not in
# sources/display_vocabulary.py because they are not a positioning problem and
# they are legitimate everywhere else in this repository -- a bottleneck is
# called a bottleneck in every file that builds one. What they cannot do is
# appear in the four sentences a reader meets first.
#
# `importer` is deliberately NOT here, and the brief's own example is why: "the
# importer" as a bearer label is the schema talking, and "importers of cement
# pay for its carbon" is a sentence with a subject. The ban is on the label, and
# a label is what a template produces; the phrase survives because a person
# wrote it into a template as English.
SCHEMA_WORDS = (
    "binding constraint", "constraint", "the gap", "exposure", "bearer",
    "borne by", "willingness to pay", "linkage", "in view", "sector view",
    "attention count", "score", "weight",
)

# What a sector under this transition is DOING, as a present participle. See the
# module docstring: a missing key raises rather than degrading.
TRANSITION_VERB = {
    "decarbonisation": "decarbonising",
    "circularity": "moving on to recycled material",
    "supply_security": "trying to secure its own supply",
    "digital": "digitising how it runs",
    "defence": "rebuilding for defence demand",
}

# One sentence's worth of why-it-matters, by the same key. Each says what the
# constraint MEANS for somebody outside the industry, and none of them says
# "constraint".
WHY_BY_TYPE = {
    "market": "{Sector} made this way costs more than the {sector} it replaces, so whether "
              "Europe gets it depends on who covers the difference.",
    "financial": "Converting a site costs a large fraction of what the site is worth, so "
                 "whether {sector} is made this way depends on who covers the difference.",
    "infrastructure": "What is being built depends on pipelines, grids and sites that "
                      "other parties own, so the two have to arrive together or neither "
                      "works.",
    "technical": "The difficulty is not only the money: the technology still has to do "
                 "at full scale what it has done at demonstration scale.",
    "political": "Most of the money behind these projects is public and revocable, so a "
                 "funder changing its position stops a project outright.",
}

# What a project DID, by the status it moved to. Keyed to
# sector_map.PROJECT_STATUSES.
STATUS_VERB = {
    "announced": "was announced",
    "funded": "was awarded public funding",
    "fid": "took a final investment decision",
    "construction": "went into construction",
    "operating": "started operating",
    "paused": "was paused",
    "cancelled": "was cancelled",
}

# How the top priced measure reads as a sentence, by the money model that
# produced the figure. The model is what the number MEANS -- a certificate price
# on an import, an allowance being withdrawn, a grant that has landed -- so it is
# the right key, and a model without a line here raises.
MODEL_LINE = {
    "cbam_certificates":
        "Importers of {sector} pay for the carbon in what they bring into Europe, "
        "currently {figure}.",
    "free_allocation_phaseout":
        "European {sector} makers are losing the free carbon allowances they used to "
        "get, worth {figure} at today's carbon price.",
    "grant_programme":
        "{figure} of EU grant money has been awarded to {sector} projects in Europe.",
}

# The order the surfaced facts read in: how big the problem is, what is being
# built about it, what it costs today, what moved last. Anything not listed here
# is computed and kept, and does not appear on the page.
SURFACE_ORDER = ("the_gap", "pipeline_state", "decisive_exposure", "the_latest")

# Abbreviations that end in a full stop and do not end a sentence. Without this
# list "Art. 1(13), adding a subparagraph to Art. 22(2)" counts as three
# sentences, and a fact line carrying a legal citation — which is most of them
# on a measure page — fails a rule it has not broken.
_ABBREV = ("Art.", "Arts.", "No.", "Nos.", "para.", "paras.", "pt.", "Reg.", "Dir.",
           "cf.", "e.g.", "i.e.", "Ann.")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?]) +")


def sentences(text: str) -> list[str]:
    """Split into sentences, honouring the abbreviations above."""
    masked = text
    for i, abbr in enumerate(_ABBREV):
        masked = masked.replace(abbr, f"\x00{i}\x00")
    return [p for p in _SENTENCE_SPLIT.split(masked.strip()) if p]


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
        # The label is what the fact IS, and it is kept for the build report and
        # for anything downstream that has to name a fact. It is not drawn:
        # brief 4 §5 rules that a fact line is a sentence with its own subject,
        # and a sentence under a label saying the same thing in schema words is
        # the thing the label was doing wrong.
        "label": label,
        "text": text,
        "as_of": as_of,
        "numbers": [_norm_number(n) for n in numbers],
        "parts": parts,
        "sourced": list(sourced),
        "href": href,
        # Computed for everything, drawn for SURFACE_ORDER. The binding
        # constraint is the one fact that is computed and not drawn: it is what
        # the opening sentence is about.
        "surface": fid in SURFACE_ORDER,
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


def fact_decisive_exposure(imp: dict, params: dict, labels: dict, sector: str) -> dict | None:
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
        figure = f"€{money['value'] / 1e6:,.0f} million"
        numbers = [f"{money['value'] / 1e6:,.0f}"]

    bearer = money["bearer"].replace("_", " ")
    as_of = max((params[p]["date_of_value"] for p in money["inputs"] if p in params),
                default="")
    model = money["model"]
    if model not in MODEL_LINE:
        raise SystemExit(
            f"build_lead: money model {model!r} has no sentence in MODEL_LINE — the "
            f"number cannot be stated without saying what it is a number of"
        )
    return _fact(
        "decisive_exposure", "Decisive exposure",
        MODEL_LINE[model].format(sector=sector, figure=figure),
        as_of, numbers,
        {"name": name, "figure": figure, "direction": money["direction"],
         "bearer": bearer, "model": model},
        sourced=(name,),
        href=f"#measure-{m['file']}-{m['id']}",
    )


def fact_pipeline_state(projects: list[dict], sector: str) -> dict | None:
    """How far the pipeline has got, how much of it has committed money, and
    what has stopped.

    UNDER WAY MEANS UNDER WAY. The count was over every project in the sector,
    which put a paused plant and a cancelled conversion inside a number the
    sentence calls "under way" -- and the two sectors on the platform have one
    each, so the figure was wrong on both. Active is `ADVANCE`: the ladder a
    project climbs. `paused` and `cancelled` are where a project left it, and
    they are named in the same sentence when there are any rather than being
    dropped, because a project that vanishes from the count reads as a project
    that never existed.
    """
    live = [p for p in projects if p["status"] in ADVANCE]
    if not live:
        return None
    furthest = max(live, key=lambda p: (ADVANCE.index(p["status"]), p["id"]))
    committed = sum(1 for p in projects if p["status"] in COMMITTED)
    paused = sum(1 for p in projects if p["status"] == "paused")
    cancelled = sum(1 for p in projects if p["status"] == "cancelled")
    as_of = max((h["date"] for p in projects for h in p["status_history"]), default="")

    stopped = []
    if paused:
        stopped.append(f"{paused} {'is' if paused == 1 else 'are'} paused")
    if cancelled:
        stopped.append(f"{cancelled} {'has' if cancelled == 1 else 'have'} been cancelled")
    tail = f", and {' and '.join(stopped)}" if stopped else ""

    numbers = [f"{len(live)}", f"{committed}"]
    numbers += [f"{paused}"] if paused else []
    numbers += [f"{cancelled}"] if cancelled else []
    return _fact(
        "pipeline_state", "Pipeline",
        f"{len(live)} European {sector} projects are under way, "
        f"{committed} of them have taken a final investment decision{tail}.",
        as_of, numbers,
        {"total": str(len(live)), "committed": str(committed),
         "paused": str(paused), "cancelled": str(cancelled),
         "furthest": furthest["name"], "furthest_status": furthest["status"]},
        sourced=(furthest["name"],),
        href="#projects",
    )


# Small numbers read better as words in a sentence, and a word is not a figure
# the gate has to trace to a fact. Past ten the digit is clearer than the word.
_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight",
          "nine", "ten")


def _count_word(n: int) -> str:
    return _WORDS[n] if n < len(_WORDS) else str(n)


def _join(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def fact_routes(projects: list[dict], technologies: list[dict]) -> dict | None:
    """Every route the sector is actually building, with the count on each.

    WHY EVERY ROUTE AND NOT THE LEADING ONE. The opening sentence used to name
    the technology with the most projects behind it and stop, which stated one
    route as though it were the sector's answer -- on steel that named hydrogen
    direct reduction and said nothing about the blast-furnace capture route
    competing with it, and the tension between the two is most of what the
    sector is. A sector page that names one route is picking a winner in a
    template.

    Counted over ACTIVE projects only, the same reading as the pipeline fact:
    a route whose only project was cancelled is not a route the sector is
    building. Enabling technologies are out -- a technology another one depends
    on is what the sector is waiting for, not a route it has taken -- which is
    the rule `lead_technology` already applied and the reason CO2 transport and
    storage never described cement.

    ROUTE COUNTS DO NOT PARTITION THE PIPELINE. A plant converting to direct
    reduction and running it on hydrogen is on two routes and is one project,
    so these counts sum above the pipeline total by construction. The sentence
    says "on" rather than "of" for that reason and states no total of its own.
    """
    own = [x for x in technologies
           if x["id"] not in {d for y in technologies for d in y.get("dependency", [])}]
    live = [p for p in projects if p["status"] in ADVANCE]
    counted = []
    for tech in own:
        n = sum(1 for p in live if tech["id"] in p.get("technology", []))
        if n:
            counted.append((n, tech))
    if not counted:
        return None
    counted.sort(key=lambda c: (-c[0], c[1]["id"]))

    # The count goes after the name in brackets rather than in front of it with
    # a preposition. "2 on electric arc furnace on scrap" reads the second `on`
    # as part of the count's phrase and the name stops parsing; the bracketed
    # form takes no preposition at all and so cannot collide with a name that
    # contains one. The word "projects" is said once, on the first item.
    parts = [f"{tech['name'][0].lower()}{tech['name'][1:]} "
             f"({n}{' project' + ('s' if n != 1 else '') if i == 0 else ''})"
             for i, (n, tech) in enumerate(counted)]
    return _fact(
        "routes", "Routes",
        f"{_count_word(len(counted)).capitalize()} route"
        f"{'s' if len(counted) != 1 else ''} are being built in this sector: "
        f"{_join(parts)}.",
        max((h["date"] for p in live for h in p["status_history"]), default=""),
        [str(n) for n, _ in counted],
        {"count": len(counted), "list": _join(parts),
         "names": [tech["name"] for _, tech in counted]},
        sourced=tuple(tech["name"] for _, tech in counted),
        href="#technologies",
    )


def fact_the_gap(params: dict, sector: str, bottlenecks: list[dict],
                 sector_name: str) -> dict | None:
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
    sector_word = sector_name
    # A percentage sits against its number; every other unit stands off it.
    if p["unit"].startswith("%"):
        figure, rest = f"{p['value']}%", p["unit"][1:].strip()
    else:
        figure, rest = f"{p['value']} {p['unit']}", ""
    # Parameters have no anchor of their own -- they render as chips inside the
    # bottleneck they quantify, so the link goes there.
    owner = next((b for b in bottlenecks if p["id"] in b.get("quantified_by", [])), None)
    # The publisher, without the report it was published in: "International
    # Energy Agency — Breakthrough Agenda Report 2025" is a citation, and the
    # sentence needs the name of whoever is saying it. The citation is intact on
    # the parameter chip, which is what the fact links to.
    publisher = p["source"]["publisher"].split(" — ")[0].strip()
    return _fact(
        "the_gap", "The gap",
        f"Low-carbon {sector_word} costs {figure}{' ' + rest if rest else ''} to make, "
        f"on the {publisher}'s figures.",
        p["date_of_value"], [str(p["value"])],
        {"figure": figure, "rest": rest, "name": p["name"], "publisher": publisher},
        sourced=(p["name"], p["unit"], rest, publisher),
        href=f"#bottleneck-{owner['id']}" if owner else "#bottlenecks",
    )


def fact_the_latest(projects: list[dict]) -> dict | None:
    """The most recent status change anywhere in the sector's pipeline."""
    events = [(h["date"], p, h) for p in projects for h in p["status_history"]]
    if not events:
        return None
    _, p, h = max(events, key=lambda e: (e[0], e[1]["id"]))
    if h["status"] not in STATUS_VERB:
        raise SystemExit(
            f"build_lead: project status {h['status']!r} has no verb in STATUS_VERB"
        )
    return _fact(
        "the_latest", "The latest",
        f"{p['name']} {STATUS_VERB[h['status']]} on {_long_date(h['date'])}.",
        h["date"], [],
        {"project": p["name"], "status": h["status"], "date": _long_date(h["date"])},
        sourced=(p["name"],),
        href=f"/projects/{p['id']}",
    )


# ---------------------------------------------------------------------------
# the sentences
# ---------------------------------------------------------------------------

def compose(sector_name: str, facts: dict[str, dict], transitions: list[str]) -> tuple[dict, dict | None]:
    """The two generated blocks, as templates over the facts and nothing else.

    Each names the fact ids it drew on, so a reader following a claim back has a
    path and the gate has something to check. Everything comes out of `parts`:
    no template reads another template's output.

    THE OPENING SENTENCE IS THE ROUTES AND THEIR COUNTS, AND NOTHING ELSE. It
    used to name the single technology with the most projects behind it and then
    say what "the main question" was. Both halves were wrong for the slot. The
    first stated one route as the sector's answer, which on a sector building
    four of them at once is a template picking a winner -- and it contradicted
    the page below it, where the other routes have their own cards, their own
    readiness and their own constraints. The second was a verdict: "the main
    question is who pays for it" is a reading of the sector, not a fact computed
    from it, and a generated slot is the one place on this page that may not
    carry one. What a reader needs before the figures is what is being built and
    how much of each, which is countable.

    EVERY TRANSITION THE SECTOR IS UNDER, not the transition of whichever
    technology happened to lead. Steel is under two and the old sentence
    asserted one of them; a sector page that renders a circularity section and
    opens by calling the sector decarbonising is arguing with itself.

    The judgement that survives is `why_it_matters`, which is a separate,
    labelled line and is keyed to the constraint's type -- brief 4 §5 asks for
    exactly one sentence of it, under its own heading, and that is where it
    belongs.
    """
    routes = facts.get("routes")
    sector = sector_name.lower()

    verbs = [TRANSITION_VERB[x] for x in transitions if x in TRANSITION_VERB]
    if not verbs or not routes:
        # Nothing to say that is not a schema word. The caller's fallback path
        # takes it from here.
        return {"text": "", "from": []}, None

    sentence = {
        "text": f"European {sector} is {_join(verbs)} on "
                f"{_count_word(routes['parts']['count'])} route"
                f"{'s' if routes['parts']['count'] != 1 else ''}: "
                f"{routes['parts']['list']}.",
        "from": ["routes"],
        "sourced": list(routes["parts"]["names"]),
    }
    constraint = facts.get("binding_constraint")
    ctype = (constraint or {}).get("parts", {}).get("type")

    # WHY IT MATTERS. One sentence, keyed to the same constraint type, and only
    # where the sector's own numbers state a shortfall that the sentence can be
    # about -- the gap fact is what makes "costs more than what it replaces" a
    # claim this page can stand behind rather than a general remark about
    # industrial decarbonisation.
    why = None
    if facts.get("the_gap") and ctype in WHY_BY_TYPE:
        why = {
            "text": WHY_BY_TYPE[ctype].format(sector=sector, Sector=sector.capitalize()),
            "from": ["the_gap", "binding_constraint"],
        }
    return sentence, why


# ---------------------------------------------------------------------------
# the gate
# ---------------------------------------------------------------------------

def schema_words(text: str) -> list[str]:
    """The schema's own words, where brief 4 §5 does not allow them."""
    lowered = text.lower()
    return [w for w in SCHEMA_WORDS if re.search(rf"\b{re.escape(w)}\b", lowered)]


def gate_fact(fact: dict) -> list[str]:
    """One surfaced fact line: one sentence, its own subject, no schema words.

    Only surfaced facts are checked for vocabulary. The binding constraint is
    computed, kept and never drawn, and its text is allowed to say what it is —
    the ruling is about what a reader is shown, not about what the build knows.
    """
    problems: list[str] = []
    text = fact["text"]
    if len(sentences(text)) != 1:
        problems.append("more than one sentence")
    if not fact["as_of"]:
        problems.append("no as-of date, and every figure on this block carries one")
    problems += [f"the schema word {w!r}" for w in schema_words(text)]
    exempt = tuple(fact["sourced"])
    problems += [f"the banned word {w!r}" for w in dv.violations(text, exempt=exempt)]
    return problems


def gate(block: dict, facts: dict[str, dict], *, max_sentences: int = 1) -> list[str]:
    """Amendment brief 2 §4 and brief 4 §5, applied to one generated block.

    `max_sentences` is 1 now rather than 2. Brief 4 §5 gives the opening
    sentence one idea and why-it-matters one sentence, and the two-sentence
    allowance is what let the first version of this template pack a cost, a
    constraint and a project count into a block nobody could parse.
    """
    problems: list[str] = []
    text = block["text"]
    if not text:
        return ["empty"]

    # FRAGMENTS THAT CAME FROM SOMEBODY ELSE'S DOCUMENT are struck out before
    # the number, adjective and vocabulary checks — the same exemption a fact
    # line already carries, for the same reason. A measure's addressee is the
    # register's own wording ("Large companies subject to the Art. 24(2) risk
    # assessment", "products with more than 0.2 kg of rare-earth magnets"), and
    # the numbers inside it are the act's, not figures this template computed
    # and owes a fact for. `critical raw material` is the same case one word
    # down: a judgment adjective in this file's vocabulary and a legal term of
    # art in the Critical Raw Materials Act.
    #
    # THE RULE ON DECLARING ONE. A sourced fragment has to be traceable to a
    # stored field that somebody else wrote. A template that declared its own
    # sentence sourced would be exempting itself from every check below, which
    # is the one way this mechanism can be abused, and the reason it is spelled
    # out here rather than left as a parameter.
    checked = text
    for fragment in block.get("sourced") or ():
        if fragment:
            checked = checked.replace(fragment, " ")

    count = len(sentences(text))
    if count > max_sentences:
        problems.append(f"{count} sentences, at most {max_sentences} allowed")

    problems += [f"the schema word {w!r}" for w in schema_words(checked)]

    if not block["from"]:
        problems.append("no fact id — a sentence nothing maps to")
    for fid in block["from"]:
        if fid not in facts:
            problems.append(f"names fact {fid!r}, which was not computed")

    known = {n for f in facts.values() for n in f["numbers"]}
    # CO2 is a name, not a figure. Digits welded to letters are struck out
    # before the number check, the same rule sources/check_sector_schema.py
    # applies to an authored key-measure sentence.
    stripped = re.sub(r"[A-Za-z]\d+", " ", _DATE_LONG.sub(" ", _ISO.sub(" ", checked)))
    for token in _NUMBER.findall(stripped):
        if _norm_number(token) not in known:
            problems.append(f"the number {token!r} is in no fact")

    as_ofs = {f["as_of"] for f in facts.values()}
    for m in _DATE_LONG.finditer(text):
        iso = f"{m.group(3)}-{MONTHS.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}"
        if iso not in as_ofs:
            problems.append(f"the date {m.group(0)!r} is no fact's as-of date")

    lowered = checked.lower()
    for adjective in JUDGMENT_ADJECTIVES:
        if re.search(rf"\b{adjective}\b", lowered):
            problems.append(f"the judgment adjective {adjective!r}")

    exempt = tuple(frag for f in facts.values() for frag in f["sourced"])
    problems += [f"the banned word {w!r}"
                 for w in dv.violations(checked, exempt=exempt)]
    return problems


def fingerprint(facts: list[dict]) -> str:
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:16]


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def lead_technology(sector: str) -> dict | None:
    """The technology the sector is actually building, for the opening sentence.

    Most projects wins, and a technology that another one DEPENDS ON is out of
    the running however many projects touch it. CO2 transport and storage is on
    every capture project in cement, and it is not what cement is doing — it is
    what cement is waiting for. Naming it in the opening sentence would say the
    sector is decarbonising by moving CO2 around, which is the shared enabler
    describing itself as the industry.
    """
    techs = [t for t in sm.load("technology") if sector in t.get("sectors", [])]
    depended_on = {d for t in techs for d in t.get("dependency", [])}
    own = [t for t in techs if t["id"] not in depended_on] or techs
    if not own:
        return None
    counts: dict[str, int] = {}
    for p in sm.load("project"):
        if p["sector"] != sector:
            continue
        for tid in p.get("technology", []):
            counts[tid] = counts.get(tid, 0) + 1
    return max(own, key=lambda t: (counts.get(t["id"], 0), t["id"]))


def build(sector: str) -> dict:
    imp = bi.build(sector, bi.date.today().year)
    params = sm.index(sm.load("parameter"))
    bottlenecks = [b for b in sm.load("bottleneck") if b["sector"] == sector]
    projects = [p for p in sm.load("project") if p["sector"] == sector]
    labels = sm.measure_labels()
    sector_name = sm.sectors()[sector]["name"]
    sector_word = sector_name.lower()

    technologies = [x for x in sm.load("technology") if sector in x.get("sectors", [])]
    # Every transition the sector is actually under, busiest first. The same
    # set web/lib/transition.ts `getTransitions` reads, and ordered by how much
    # of the pipeline sits under each so the sentence leads with the one the
    # sector is mostly doing rather than with whichever sorts first.
    counts: dict[str, int] = {}
    for row in bottlenecks + projects:
        counts[row["transition"]] = counts.get(row["transition"], 0) + 1
    transitions = sorted(counts, key=lambda x: (-counts[x], x))

    computed = [
        fact_binding_constraint(bottlenecks),
        fact_routes(projects, technologies),
        fact_decisive_exposure(imp, params, labels, sector_word),
        fact_pipeline_state(projects, sector_word),
        fact_the_gap(params, sector, bottlenecks, sector_word),
        fact_the_latest(projects),
    ]
    facts = [f for f in computed if f]
    # In reading order, with the facts nobody sees after the ones they do.
    facts.sort(key=lambda f: (SURFACE_ORDER.index(f["id"]) if f["surface"]
                              else len(SURFACE_ORDER)))
    by_id = {f["id"]: f for f in facts}
    for f in facts:
        dv.check(f["text"], f"build_lead: {sector} fact {f['id']}",
                 exempt=tuple(f["sourced"]))

    notes: list[str] = []
    # A surfaced fact that fails its own gate is not shown. It is still built,
    # still in this file and still printed on every run — what it is not is a
    # sentence in front of a reader that nobody checked.
    for f in facts:
        if not f["surface"]:
            continue
        problems = gate_fact(f)
        if problems:
            f["surface"] = False
            notes.append(f"the fact {f['id']} failed its gate "
                         f"({'; '.join(problems)}) — computed, not shown")

    sentence, why = compose(sector_name, by_id, transitions)

    problems = gate(sentence, by_id)
    if problems:
        notes.append(f"the sentence failed its gate ({'; '.join(problems)}) — "
                     f"fell back to the template")
        # The dullest sentence the facts support. It used to name the priced
        # measure and the binding constraint, which meant the fallback for a
        # block that had failed its vocabulary gate was a sentence built out of
        # schema words. It now says the one thing that is always true and always
        # plain: what the sector is under, and nothing else.
        verbs = [TRANSITION_VERB[x] for x in transitions if x in TRANSITION_VERB]
        sentence = {
            "text": (f"European {sector_word} is {_join(verbs)}." if verbs
                     else f"European {sector_word}."),
            "from": [],
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

    sectors = args.sector or sm.mapped_sectors()
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

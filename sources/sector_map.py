"""
The sector transition map: schema, vocabularies, and the loader every other
script on this layer reads through.

WHY THIS FILE EXISTS
====================
The register answers "what does this act require". It cannot answer "what
transition is this sector under, which measures decide whether it pays, who is
building what, and what is blocking it" -- because the objects that question is
about (technologies, bottlenecks, projects, and the numbers that quantify them)
are not legal provisions and have no place in a register row.

So they get their own node kinds, in their own files, under data/transition/.
The register is not replaced: it becomes the candidate pool that the measure
importance score ranks. Nothing here rewrites data/*.json.

THE FILES
=========
  data/transition/technologies.json   shared across sectors, never duplicated
  data/transition/bottlenecks.json    one sector + one transition each
  data/transition/parameters.json     every number that any surface states
  data/transition/projects.json       real installations, append-only history
  data/transition/materials.json      what a sector makes, consumes and throws off
  data/transition/funding.json        capital allocated, and what it was allocated under
  data/transition/measure_labels.json what a measure is CALLED on a diagram
  data/transition/corrections.json    dated notes on figures already printed

Each file is {"_comment": [...], "<kind>s": [ ... ]} -- the same arrangement
data/sectors.json uses, for the same reason: a data file that cannot say what
it is for gets misread by the next person to open it.

TRANSITION IS AN ATTRIBUTE, NOT A PRODUCT
=========================================
A sector can be under more than one transition at once. Cement has one
(decarbonisation); chemicals or automotive would carry several. Transition is
therefore a field on the technology, the bottleneck and the project -- never a
separate file, a separate route, or a separate build. The vocabulary is closed
(TRANSITIONS below) and a value outside it is a build failure, because the
sector page groups by it and an unrecognised value would render as a section
nobody wrote.

`digital` is in the vocabulary and is deliberately unused: a transition is
added to a sector only where a money component can be computed and a public
project pipeline exists, and digital regulation has neither yet.

EVERY NUMBER CARRIES ITS SOURCE
===============================
The rule from the register layer holds here without exception. A parameter is
{value, unit, scope, date_of_value, retrieved_date, source{url, publisher,
verbatim}, confidence}. There is no field for a number somebody remembered.
`verbatim` is the sentence the number was read from, not a paraphrase of it --
if the quote does not contain the number, the parameter is not sourced.

Staleness is recorded, not enforced: `stale_after` months past `date_of_value`
makes a parameter STALE, which the gate prints and does not fail on. A stale
carbon price is still the last carbon price anybody wrote down; failing the
build over it would take the whole site down for the age of one number.

CONFIDENCE
==========
  primary     the number is in the source document, stated by the body that
              produced it (a registry, a regulation, the company's own release)
  secondary   a third party reporting somebody else's number
  estimate    the source itself calls it an estimate, a range, or a forecast

The distinction is not decoration: the money model in build_importance.py
weights nothing by confidence, but a reviewer ranking a sector needs to see at
a glance whether the top measure rests on a registry figure or on a consultancy
projection.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import number_format as nf

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "transition"

# ---------------------------------------------------------------------------
# Closed vocabularies. Every one of these is closed on purpose: an open list
# here becomes a set of one-off values nobody can group by six months later.
# ---------------------------------------------------------------------------

TRANSITIONS = (
    "decarbonisation",
    "circularity",
    "supply_security",
    "digital",
    "defence",
)

READINESS = (
    "research",
    "pilot",
    "demonstration",
    "early-commercial",
    "commercial",
)

BOTTLENECK_TYPES = (
    "technical",
    "financial",
    "infrastructure",
    "market",
    "political",
)

# Append-only in spirit as well as in the data: a project moves forward through
# these, and `paused` / `cancelled` are terminal-ish states that the status
# strip has to be able to draw without pretending the project never existed.
PROJECT_STATUSES = (
    "announced",
    "funded",
    "fid",
    "construction",
    "operating",
    "paused",
    "cancelled",
)


# WHAT KIND OF EVENT AN ENTRY IS. `status` is the default and is left off the
# entry; an entry that says nothing is the project moving from one status to the
# next. `ownership` is the project changing hands, which the batteries dataset
# forced: Northvolt Ett is one continuous site whose OWNER broke, not one project
# that ended and another that began at the same coordinates, and a history that
# could not say so would have had to choose between a cancellation that did not
# happen and an acquisition that never appears.
#
# AN OWNERSHIP EVENT STILL CARRIES A STATUS, and it is the status the project was
# already in. Three things fall out of that and all three are wanted:
#
#   the append-only invariant survives -- the last entry's status still equals
#   the project's, so a header and a timeline cannot disagree;
#
#   is_transition already handles it -- the status is unchanged, so an ownership
#   event is not a transition, and the three sentence templates that render an
#   entry as "was paused on {date}" skip it without being told to;
#
#   and the feed, which wants the latest thing on file rather than the latest
#   MOVE, shows it with a true status chip beside it.
#
# ONE FACT PER ENTRY. An ownership event may not also change the status: the gate
# refuses one whose status differs from the entry before it, because a company
# changing hands on the same day a project is paused is two events and reads as
# one cause. For the same reason an ownership event may not be the first entry --
# there is nothing for its status to be unchanged FROM, and is_transition would
# have to call it a status change.
PROJECT_EVENT_KINDS = (
    "status",
    "ownership",
)


# NOT EVERY ENTRY IN A STATUS HISTORY IS A STATUS CHANGE, and the difference has
# to be named because three sentence templates on this site render an entry as
# one: "{project} was paused on {date}".
#
# A history is a list of EVENTS, in date order. Most are transitions -- the
# project moved from one status to the next, and the entry's date is the date it
# moved. Some are not: a later source reports on a project whose status it does
# not change. Slite is the case that forced this. It was paused on 19 November
# 2025 when the Swedish Energy Agency declined to co-fund it; on 1 January 2026
# Heidelberg Materials withdrew the permit application, which is a fact about a
# paused project rather than a project becoming paused. Both belong in the
# history -- the second is the evidence that the register has read the later
# news and still says paused -- and rendering the second as a transition would
# put "Slite CCS was paused on 1 January 2026" on three pages, which no source
# says.
#
# THE RULE IS POSITIONAL, not a flag on the row. An entry is a transition if its
# status differs from the entry before it; the first entry always is. That
# cannot fall out of step with the data the way a hand-set `transition: false`
# would, and it needs nothing added to any row.
#
# IT IS WRITTEN TWICE, AND HELD BY A GATE. web/lib/transition.ts
# statusTransitions is the same rule for the page, and check_transition_parity.py
# runs both readings over every history up to four entries long -- 4,681 of them
# -- and fails the build on any disagreement. The two sides used to be held by a
# comment on each saying "edit both", which is what the reach-channel inference
# is still held by and is not a mechanism.

# WHERE A PROJECT HAS STOPPED MOVING, and it is a different question from where
# it has stopped being reported. Two statuses are TERMINAL for that question:
# `operating` has climbed the whole ladder and has nowhere left to go, and
# `cancelled` will not move again. Everything else is a project that is supposed
# to be going somewhere, including `paused` -- a paused project can resume, and
# one that has been paused for three years is exactly what a stalling listing is
# for.
TERMINAL_STATUSES = frozenset({"operating", "cancelled"})


def is_transition(history: list[dict], i: int) -> bool:
    """Whether entry `i` is the moment the project's status changed."""
    return i == 0 or history[i]["status"] != history[i - 1]["status"]


def transitions(project: dict) -> list[dict]:
    """Only the entries that changed the status. What a feed of "what moved"
    should be built from, and what a sentence saying a project MOVED may use."""
    history = project.get("status_history") or []
    return [h for i, h in enumerate(history) if is_transition(history, i)]


def entered(project: dict) -> dict | None:
    """The entry that put the project into the status it is in now -- the first
    of the trailing run, not the last entry.

    This is the date "was paused on" means. `status_history[-1]` is the latest
    thing ON FILE about the project, which is a different question and is the
    right answer for a feed, a "last change" column or an "as of" date.
    """
    changes = transitions(project)
    return changes[-1] if changes else None

# WHAT KIND OF PLACE A PROJECT ROW IS. `plant` is the default and is left off the
# row; a row that says nothing is a works. `storage` is a permitted or proposed
# geological store -- the place a captured tonne ends, which the graph referred
# to as a technology long before it named one. Closed, and short on purpose: a
# role is a mark on a map, and a vocabulary with eight of them would be eight
# marks nobody can tell apart.
PROJECT_ROLES = (
    "plant",
    "storage",
)

# WHERE A COORDINATE CAME FROM, and it is recorded per site rather than assumed.
#
# The rule this vocabulary enforces has not changed and is the one the register
# has always had: a coordinate must come from a citable source that identifies
# THE WORKS SPECIFICALLY. What changed is that the basemap is no longer the only
# thing that can do that. Batteries made the old reading untenable -- ACC's
# Kaiserslautern site is real, company-confirmed and carries no OpenStreetMap
# feature at all, and a rule that admits a works only when a volunteer has
# already drawn it is a rule about OpenStreetMap's coverage rather than about
# evidence.
#
# So three kinds of source may put a works on the paper:
#
#   basemap     an OpenStreetMap feature, with its tags quoted, so a reader can
#               see that the polygon is the works and not the industrial estate
#               around it. Still the best of the three, because the geometry and
#               the identification are the same object.
#   company     the operator's own materials naming a street address or a land
#               parcel. The company knows where its works is; what this costs is
#               that the coordinate is then derived from an address rather than
#               read off a shape, so the address itself is quoted alongside.
#   permit      a state permitting, planning or zoning filing. Often the most
#               precise of the three -- a zoning decision names parcels -- and it
#               is a public document that outlives a press release.
#
# WHAT IS STILL REFUSED, and this is the whole point of naming the three. A town
# name run through a geocoder is not a source about a works, it is a source about
# a town, and `precision: "town"` already fails by name. A position read off a
# picture in a news story is not citable: nobody can check it and the next reader
# gets a different number. Neither has a value in this vocabulary, so neither can
# be recorded without inventing one, which is the point of a closed list.
#
# AND WE DO NOT DRAW THE POLYGON OURSELVES. Where the basemap has no feature for a
# works, the answer is a permit, a published address, or the row staying off file
# -- never an edit to OpenStreetMap made in order to cite it. The temptation is
# real and the reasoning is easy: we know where the works is, OSM is editable, and
# `basemap` would then be true of the row. It would also be circular. The
# coordinate's whole claim is that somebody independent put the works there, and
# an edit made to be cited LAUNDERS AN ASSERTION INTO A SOURCE TYPE -- it converts
# "we believe this is the site" into "the basemap says so", which is a stronger
# claim than we hold and one no reader could unpick.
#
# This says nothing against improving OpenStreetMap. It says that a coordinate
# this repository publishes may not rest on an edit this repository made for the
# purpose, and that the two must not be done in the same breath.
LOCATION_SOURCE_TYPES = (
    "basemap",
    "company",
    "permit",
)


# HOW A SITE IS CONFIRMED, WHEN ONE SOURCE CANNOT DO IT ALONE
# ===========================================================
# The perimeter's site rule is company-only: a project whose specific site the
# company has not confirmed is not held. That rule is right and it has already
# refused a candidate outright -- InoBat's Spanish site, where the only company
# statement was conditional and nothing followed it.
#
# Sunwoda is the case it could not decide. The company confirms the project and
# the country and never names the town: its newsroom release says "Hungary", its
# 2025 Shenzhen-filed interim report lists "Hungary Sunwoda Power Technology Co.,
# Ltd" with Hungary as its place of business, and neither says Nyíregyháza. The
# Hungarian government's own briefing room does say it, and the basemap carries a
# works whose name is the operator's own subsidiary at an address in that town.
#
# Read strictly, company-only refuses a site that three independent sources agree
# on. Read loosely, it stops meaning anything. So it is neither stretched nor
# abandoned: a SECOND, NAMED standard is defined, and a row says which one it
# stands on.
#
# THE COMPOSITE STANDARD HAS THREE LEGS AND ALL THREE ARE REQUIRED:
#
#   company    the operator's own materials confirming the project and the
#              country. Not the town -- if the company named the town, the
#              ordinary standard is met and this one is not needed.
#   state      a primary of the host state naming the site. A government's own
#              publication, not an agency's summary of it and not press relaying
#              either.
#   basemap    a feature carrying the operator's name, corroborating that
#              something of theirs stands where the state says it does.
#
# WHY THIS IS NOT A WEAKENING. Each leg is weak where the others are strong. The
# company knows what it is building and will not always say where; the state
# knows where because it permitted and subsidised it; the basemap knows what is
# physically there and nothing about who intends what. One source doing all three
# jobs is the ordinary case; three sources doing one job each is not a lower bar,
# it is a different one, and it is only available when no single source clears
# the first.
#
# EVERY LEG IS CITED ON THE ROW, and the note says plainly that the company
# source names no city. A reader who disagrees with the standard can see exactly
# what it was applied to.
SITE_EVIDENCE_KINDS = (
    "company",      # the ordinary standard: the operator names its own site
    "composite",    # the three legs above, all cited
)


# HOW EXACT A COORDINATE IS. `plant` is the works itself; `site` is a store, a
# field or a receiving terminal, which has a position but not a street. `town`
# is listed and is not allowed on a project: the gate refuses it by name, so the
# refusal reads as a rule rather than as a missing value. A town centroid drawn
# as a plant is a wrong fact rendered confidently, which is worse than no map.
LOCATION_PRECISIONS = (
    "plant",
    "site",
    "town",
)

# The precisions a project or a plant may actually carry. See the note above.
LOCATION_PRECISIONS_ALLOWED = ("plant", "site")

# The legal device a measure acts with, as a diagram says it. Closed for the
# usual reason and one extra: these words are the only part of a measure label
# that repeats across sectors, so an open list would give every sector its own
# word for the same device and quietly break the comparison the labels exist to
# make. `None` is a legitimate value -- see data/transition/measure_labels.json.
INSTRUMENTS = (
    "obligation",
    "prohibition",
    "requirements",
    "phase-out",
    "grants",
    "levy",
    "target",
    "threshold",
    "access rule",
)

# A diagram node is 236 units wide and the label sits at 12px. Past this it is
# an ellipsis, and an ellipsis on the one word that says what the measure does
# is worse than no label at all.
MAX_SHORT_LABEL = 26

# What a material IS in the chain, which is the only thing that decides where it
# is drawn. `by_product` and `waste_stream` are kept apart on purpose: a
# by-product has a buyer (granulated slag is sold into cement), a waste stream
# does not yet (captured CO2 has to be paid to take away), and a sector page
# that grouped them would be asserting a market that may not exist.
MATERIAL_TYPES = (
    "feedstock",
    "intermediate",
    "energy_carrier",
    "by_product",
    "waste_stream",
)

# How the money arrives. Capital allocation is a first-class object here rather
# than a field on a project, because the same decision often finances several
# projects, and a field on one of them cannot say so.
FUNDING_INSTRUMENTS = (
    "grant",
    "state_aid",
    "eib_financing",
    "ipcei",
    "auction_support",
    "equity",
    "project_finance",
    "guarantee",
)

# Where the money has got to. A press release announcing a grant, a Commission
# decision approving it, a signed agreement and a disbursement are four
# different facts, and a page that showed them as one would let an announcement
# read as money in the ground.
FUNDING_STATUSES = (
    "announced",
    "approved",
    "signed",
    "disbursed",
    "withdrawn",
)

# WHICH STATUSES A TOTAL MAY ADD UP. The vocabulary above records where the
# money has got to; these three groups record what that means for arithmetic,
# in one place, because a total that quietly spans them is the failure the
# vocabulary exists to prevent.
#
#   COMMITTED   a decision has been taken and the money is attached to a
#               project: approved, signed, disbursed. This is what a figure
#               labelled "awarded" may contain and nothing else.
#   ANNOUNCED   said out loud and not yet decided. Shown as its own figure,
#               never folded into the committed one.
#   EXCLUDED    withdrawn. Out of every total, shown as its own line, because a
#               withdrawal that vanishes silently reads as money that was never
#               promised.
#
# Every status is in exactly one group; the gate checks that, so adding a
# status to FUNDING_STATUSES without deciding what it means for a sum fails
# rather than defaulting into invisibility.
FUNDING_COMMITTED = ("approved", "signed", "disbursed")
FUNDING_ANNOUNCED = ("announced",)
FUNDING_EXCLUDED = ("withdrawn",)

CONFIDENCE = ("primary", "secondary", "estimate")

# Scope of a parameter value. `country:XX` and `plant:<id>` are checked by
# prefix rather than listed, because the tail is data.
SCOPE_LITERALS = ("eu", "global")
SCOPE_PREFIXES = ("country:", "plant:")

DEFAULT_STALE_AFTER_MONTHS = 12


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

# WHICH PRINTED FIGURES A CORRECTION MAY BE PINNED TO. Closed, because the
# whole value of a correction note is that it appears beside the figure it
# corrects: an entry naming a figure no surface renders is a correction nobody
# is told about, and a typo would produce exactly that in silence. Each entry is
# `<section>.<figure>` and names something a page actually prints.
CORRECTABLE_FIGURES = (
    "opportunity.money_in",
)


_FILES = {
    "technology": ("technologies.json", "technologies"),
    "bottleneck": ("bottlenecks.json", "bottlenecks"),
    "parameter": ("parameters.json", "parameters"),
    "project": ("projects.json", "projects"),
    "material": ("materials.json", "materials"),
    "funding": ("funding.json", "funding"),
    "ecosystem": ("ecosystems.json", "ecosystems"),
    "correction": ("corrections.json", "corrections"),
}


def load(kind: str) -> list[dict]:
    """Read one kind's file and return its rows. Raises if the file is absent:
    an empty layer is a state this project has never been in, and a silently
    empty list would make every downstream count read as zero rather than as
    broken."""
    filename, key = _FILES[kind]
    path = DATA / filename
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc[key]
    if not isinstance(rows, list):
        raise TypeError(f"{path}: '{key}' must be a list")
    return rows


def load_all() -> dict[str, list[dict]]:
    return {kind: load(kind) for kind in _FILES}


def index(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def mapped_sectors() -> list[str]:
    """The sectors that have a transition map, which is the set every builder
    on this layer runs over by default.

    A sector has a map when something names a constraint in it -- the same
    condition web/lib/transition.ts `hasMap` reads and the sector route
    branches on. It was a literal ["cement"] in four builders' argument
    parsers, which meant the second sector had to be remembered in four places
    and would be silently absent from --check in any one of them that was
    missed. Derived here so the third sector arrives by having data.
    """
    return sorted({b["sector"] for b in load("bottleneck")})


# The technology every capture route eventually leans on. Named once here rather
# than matched on the `ccs-` prefix in three places: the prefix is a naming
# habit, the dependency is the fact.
CO2_STORAGE_TECHNOLOGY = "co2-transport-storage"


def captures_co2(project: dict, technologies: dict[str, dict]) -> bool:
    """Whether this project puts a captured tonne on the road, and therefore owes
    an answer about where the tonne goes.

    Read off the dependency graph, not off the row: a project deploys a capture
    technology, and that technology declares it cannot run without CO2 transport
    and storage. A project that deploys transport and storage ITSELF is the far
    end of that chain and owes nothing -- it is the answer, not the question.
    """
    tech_ids = project.get("technology") or []
    if CO2_STORAGE_TECHNOLOGY in tech_ids and project.get("role") == "storage":
        return False
    for tid in tech_ids:
        row = technologies.get(tid) or {}
        if CO2_STORAGE_TECHNOLOGY in (row.get("dependency") or []):
            return True
    return False


def sectors() -> dict[str, dict]:
    """The sector spine, read from the same file build_graph.py and
    web/lib/data.ts read, so this layer cannot invent a sector."""
    doc = json.loads((ROOT / "data" / "sectors.json").read_text(encoding="utf-8"))
    return doc["sectors"]


def register_measure_ids() -> set[str]:
    """Every measure id in the register, as `<file>:<id>` -- the form the
    transition layer references a measure by, and the tail of the graph node id
    `measure:<file>:<id>`."""
    ids: set[str] = set()
    files = json.loads((ROOT / "sources" / "register_files.json").read_text(encoding="utf-8"))
    for slug in files["files"]:
        path = ROOT / "data" / f"{slug}.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows:
            ids.add(f"{slug}:{row['id']}")
    return ids


def measure_labels() -> dict[str, dict]:
    """The {object, instrument} pair per register measure id."""
    doc = json.loads((DATA / "measure_labels.json").read_text(encoding="utf-8"))
    return doc["labels"]


def short_label(entry: dict) -> str:
    """The template. One line, one place, so twenty sectors read alike.

    Kept deliberately dumb: the judgement is in the two authored fields, and a
    template with a branch per measure would be the free labels this replaced.
    """
    obj = entry["object"].strip()
    instrument = entry.get("instrument")
    return obj if not instrument else f"{obj} {instrument.strip()}"


# The figures an authored key-measure sentence may ask for, and nothing else.
# Closed, because a sentence that could name any field would be a template over
# the whole money block and would break silently the day one of those fields
# changed shape. See the plain block in data/transition/measure_labels.json.
MEASURE_SLOTS = ("money_per_tonne", "money_annual", "money_awarded")

_SLOT_RE = re.compile(r"\{([a-z_]+)\}")


def slots_named(text: str) -> list[str]:
    """Every {slot} in an authored sentence, in the order it appears."""
    return _SLOT_RE.findall(text or "")


def money_slots(money: dict) -> dict[str, str]:
    """The slot values a measure's own money block can answer for.

    Only what is computable: a measure with no per-tonne figure has no
    `money_per_tonne`, and a sentence that asks for one fails rather than
    printing an empty string where a euro figure was promised.

    Rounding is by scale, not by taste, and the scale is not chosen here: a rate
    goes through nf.money_rate and a stock through nf.money_long, both of which
    read data/number_format.json. This function used to write its own euro
    strings, which is how the site came to render one total two ways.
    """
    out: dict[str, str] = {}
    if not money or not money.get("computable"):
        return out
    if money.get("per_tonne") is not None:
        out["money_per_tonne"] = nf.money_rate(money["per_tonne"])
    if money.get("annual_total"):
        out["money_annual"] = f"{nf.money_long(money['annual_total'])} a year"
    if money.get("value") and money.get("scale") == "eur_awarded":
        out["money_awarded"] = nf.money_long(money["value"])
    return out


# WHAT A SECTOR'S PRODUCT IS CALLED, per sector, and the reason this list is
# here rather than in the gate: it is the vocabulary that makes a plain block
# sector-specific, and both the resolver and the gate have to agree about it.
#
# A shared plain block may contain none of these words, because a shared block
# is rendered on every sector a measure reaches and a product word in one is a
# sentence about the wrong industry. A per-sector block may contain its own
# sector's words and no other's. Adding a sector to the platform means adding
# its nouns here, and a sector with no entry has no product vocabulary to
# violate -- which is correct for the instances that are not industries.
SECTOR_PRODUCT_WORDS = {
    "cement": ("clinker", "cement", "concrete", "kiln"),
    "steel": ("steel", "hot metal", "crude steel", "directly reduced iron", "DRI",
              "blast furnace", "scrap", "electric arc furnace", "EAF", "iron ore"),
    # Both spellings of the plural are listed because the check matches a word
    # plus an optional "s", and "batteries" is not "batterys".
    "batsol": ("battery", "batteries", "cell", "cathode", "anode", "gigafactory"),
}


def plain_block(entry: dict, sector: str) -> dict | None:
    """The plain block this measure renders IN THIS SECTOR, or None.

    The sector's own wording wins; the shared block is the fallback and exists
    only for measures whose wording names no product. None is a real answer and
    the gate fails on it -- see data/transition/measure_labels.json. Returning
    the shared block regardless would be the trap this split was made to close.
    """
    per_sector = (entry.get("plain_by_sector") or {}).get(sector)
    return per_sector or entry.get("plain") or None


def plain_measure(entry: dict, money: dict, sector: str) -> dict:
    """The authored title and the slot-filled sentence, for one measure.

    The words are reviewed and stored; the figures are computed on every build.
    An unfillable slot raises, because the alternative is a sentence that says
    a measure costs nothing when what happened is that a parameter went
    missing.
    """
    plain = plain_block(entry, sector)
    if plain is None:
        raise SystemExit(
            f"sector_map: this measure has a label but no plain block for {sector!r} — "
            f"a sector view listing it would print an empty title and an empty sentence. "
            f"Write plain_by_sector.{sector}, or a shared block if the wording names no "
            f"product; see data/transition/measure_labels.json"
        )
    title, sentence = plain.get("title", ""), plain.get("sentence", "")
    values = money_slots(money)
    for name in slots_named(sentence):
        if name not in MEASURE_SLOTS:
            raise SystemExit(
                f"sector_map: key-measure sentence names {{{name}}}, which is not one of "
                f"{list(MEASURE_SLOTS)} — see data/transition/measure_labels.json"
            )
        if name not in values:
            raise SystemExit(
                f"sector_map: key-measure sentence asks for {{{name}}} and this measure's "
                f"money block cannot answer for it — either the sentence is about a figure "
                f"the measure does not carry, or the figure has gone missing"
            )
    return {
        "title": title,
        "sentence": _SLOT_RE.sub(lambda m: values[m.group(1)], sentence),
    }

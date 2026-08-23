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
  data/transition/measure_labels.json what a measure is CALLED on a diagram

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
from pathlib import Path

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

CONFIDENCE = ("primary", "secondary", "estimate")

# Scope of a parameter value. `country:XX` and `plant:<id>` are checked by
# prefix rather than listed, because the tail is data.
SCOPE_LITERALS = ("eu", "global")
SCOPE_PREFIXES = ("country:", "plant:")

DEFAULT_STALE_AFTER_MONTHS = 12


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

_FILES = {
    "technology": ("technologies.json", "technologies"),
    "bottleneck": ("bottlenecks.json", "bottlenecks"),
    "parameter": ("parameters.json", "parameters"),
    "project": ("projects.json", "projects"),
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

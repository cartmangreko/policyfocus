"""
The words an audience surface is not allowed to use, in one place.

    import display_vocabulary as dv
    dv.violations("the cement transition map")   -> ["map", "transition"]

WHY A MODULE RATHER THAN A PARAGRAPH IN scope.md
================================================
The display-vocabulary ruling (sources/scope.md, "Display vocabulary") has been
prose since it was made, and prose does not fail a build. It held anyway while
the only computed strings were counts. It stops holding the moment surfaces
start carrying GENERATED labels and GENERATED sentences -- a short label per
measure, a lead block per sector -- because those are written by a template that
has never read scope.md.

So the list lives here, the generators check against it, and a violation is a
build failure at the point the string is made rather than a note somebody leaves
on a page review.

TWO LISTS, BECAUSE THEY BAN FOR DIFFERENT REASONS
=================================================
INTERNAL is the original ruling: the pipeline's own words. "row", "valence",
"docket" are precise inside the repo and meaningless outside it. They are banned
on every audience surface, always.

BRAND is the Eufabric ruling (amendment brief 2, §1). These words are ordinary
English and several of them are accurate; what they are wrong about is
POSITIONING. A platform that calls itself a register, a tracker or a reference
has told the reader it is a place where things are written down. Eufabric's
claim is that it is intelligence -- signal, ranking, exposure, pipeline,
readiness, linkage -- and the nouns have to agree with the claim.

`plant` and `map`/`transition` are the two entries that need their exception
stated, because they are banned in FRAMING and legitimate in FACT:

  plant       "Brevik cement plant" is the installation's name and is fine.
              "what moved at a plant" is the site describing what it is for,
              in the vocabulary of somebody who sells to cement producers.
  map         a diagram is a diagram; "the transition map" as the name of the
              product is the old positioning wearing the new one's clothes.

The module cannot tell framing from fact -- that is a judgement about the
sentence, not about the word. What it can do is refuse the word in the places
the generators write, which are all framing, and report (never fail) the word in
hand-written surface copy, which is where the judgement belongs. `check` is the
first mode; sources/check_display_vocabulary.py is the second.
"""

from __future__ import annotations

import re

# The original ruling. Internal precision, meaningless to a reader.
INTERNAL = (
    "row",
    "duty-side",
    "benefit-side",
    "FIGARO",
    "docket",
    "reconciled",
    "valence",
    "slug",
)

# Amendment brief 2, §1. Banned as product nouns and in framing copy.
BRAND = (
    "reference",
    "tracker",
    "register",
    "record",
    "plant",
    "map",
    "transition",
)

# What the surfaces say instead. Not enforced -- a positive list cannot be a
# gate -- but written down here so the replacement is not reinvented per page.
PREFERRED = (
    "intelligence",
    "signal",
    "ranking",
    "exposure",
    "pipeline",
    "readiness",
    "linkage",
)


def _pattern(terms: tuple[str, ...]) -> re.Pattern[str]:
    # Whole words only, and plurals: "records" is the same violation as
    # "record", while "recording" and "mapping" are different words and are
    # left to the reviewer.
    body = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
    return re.compile(rf"\b({body})s?\b", re.IGNORECASE)


_INTERNAL_RE = _pattern(INTERNAL)
_BRAND_RE = _pattern(BRAND)


def violations(text: str, *, brand: bool = True) -> list[str]:
    """Every banned word in `text`, lowercased, in the order they appear.

    `brand=False` checks the internal list only -- for a surface where the
    brand ruling is not the question being asked."""
    found = [m.group(0).lower() for m in _INTERNAL_RE.finditer(text)]
    if brand:
        found += [m.group(0).lower() for m in _BRAND_RE.finditer(text)]
    return found


def check(text: str, where: str, *, brand: bool = True) -> None:
    """Raise on any violation. Used by the generators, where a banned word is
    a bug in a template rather than a sentence somebody chose."""
    bad = violations(text, brand=brand)
    if bad:
        raise ValueError(
            f"{where}: display-vocabulary violation {sorted(set(bad))} in {text!r} — "
            f"see sources/display_vocabulary.py for what the surfaces say instead"
        )

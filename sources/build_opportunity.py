"""
The Opportunity section's own facts, and the one sentence that opens it.

    python3 build_opportunity.py            # writes data/transition/opportunity/<sector>.json
    python3 build_opportunity.py --check    # fails if the stored file is stale

WHAT THIS IS FOR
================
Brief 5 §4 makes Opportunity four computed views over graph objects: the money
flowing in, the rules that pay, the rules that create demand, and the open
application windows. §4.5 gives the section one generated sentence at the top of
it, built at build time from the section's OWN facts and by the same mechanism
as the sector lead -- gated to the panel facts, an override slot in
overrides.json, a re-review flag when the facts move underneath a reviewed
sentence.

"THE SAME MECHANISM" IS MEANT LITERALLY. The gate is imported from
build_lead.py rather than written again here, exactly as build_object_leads.py
imports it: page specifications §0.2 asks for one set of rules across the page
types that carry a generated sentence, and two copies of a rule is one rule that
will eventually disagree with itself. What this file owns is which facts the
sentence may speak from; the rules about how a generated sentence may be worded
belong to one file and it is not this one.

WHAT THE FACTS ARE, AND WHAT THEY DELIBERATELY ARE NOT
======================================================
Counts and sums, per §4.5. Money committed and the projects it finances; the
number of allocations announced and withdrawn; the number of measures whose
money direction for the bearer is support, and what they have paid.

Not here, and not anywhere in the section: technology cost figures, abatement
costs, carbon-price arithmetic and any comparison of a cost against a price.
§4 rules all four out of Opportunity explicitly, and the reason they would
otherwise arrive is that the sector layer HAS them -- the green premium is a
parameter, the CBAM certificate cost is computed per tonne. A section about
where money comes from that opened by netting it against what decarbonising
costs would be answering a different question, and a harder one, in a sentence.

ANNOUNCED MONEY IS COUNTED AND NOT SUMMED (§4.1, ruled). There is no announced
total in this file, none in web/lib/transition.ts, and no template in
data/prose.json that takes one. A figure that is never computed cannot be
rendered by mistake.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

import build_lead as bl
import display_vocabulary as dv
import sector_map as sm
import build_importance as bi

OUT_DIR = sm.ROOT / "data" / "transition" / "opportunity"

# Bumped when a template changes, so a diff says whether the sentence moved
# because the data moved or because the wording did.
TEMPLATE_VERSION = 1


def _prose() -> dict:
    return json.loads((sm.ROOT / "data" / "prose.json").read_text(encoding="utf-8"))


def _amount(row: dict, params: dict) -> float | None:
    """One allocation's euros, or None where nobody published a figure.

    The conversion is build_importance's, not a second copy of it. Its `_eur`
    raises on a unit nobody has ruled on rather than defaulting the scale, which
    is the one bug a funding total can have that nobody notices: every amount in
    this store is written "EUR million", and a builder that multiplied by one
    would be wrong by a factor of a million and would still look like money.
    """
    pid = row.get("amount")
    return bi._eur(params.get(pid)) if pid else None


def _money(value: float) -> str:
    if value >= 1e9:
        return f"€{value / 1e9:,.1f} billion"
    if value >= 1e6:
        return f"€{value / 1e6:,.0f} million"
    return f"€{value:,.0f}"


def _n(count: int, singular: str, plural: str | None = None) -> str:
    return f"{count} {singular if count == 1 else (plural or singular + 's')}"


def _digits(figure: str) -> str:
    """The numeric token out of a rendered money string, so a fact declares the
    number the sentence will actually print.

    It was `total / 1e6` written straight into the fact while `_money` chose
    its own scale from the size of the total. The two agree up to €999 million
    and part company above it: the first sector to commit more than a billion
    produced a sentence saying "€3.2 billion" and a fact declaring 3200, and
    build_lead.gate dropped the sentence for stating a number no fact carried.
    Cement never crossed the boundary, so the bug shipped invisible and steel
    found it -- which is the whole argument for a second sector.
    """
    return re.search(r"[\d,.]+", figure).group(0)


# ---------------------------------------------------------------------------
# the facts
# ---------------------------------------------------------------------------

def fact_money_in(funding: list[dict], params: dict) -> dict | None:
    """§4.1. The committed sum, what it finances, and the two counts that are
    counts on purpose.

    `undisclosed` is why the sum is a floor and says so: an allocation nobody
    published a figure for is not an allocation of nothing, and a total that
    folded it in as zero would read as complete.
    """
    committed = [f for f in funding if f["status"] in sm.FUNDING_COMMITTED]
    announced = [f for f in funding if f["status"] in sm.FUNDING_ANNOUNCED]
    withdrawn = [f for f in funding if f["status"] in sm.FUNDING_EXCLUDED]
    if not committed:
        return None

    total = 0.0
    undisclosed = 0
    for f in committed:
        amount = _amount(f, params)
        if amount is None:
            undisclosed += 1
        else:
            total += amount
    projects = {n for f in committed for n in f["finances"] if n.startswith("project:")}
    # The as-of date is the most recent committed allocation, which is what the
    # sum is complete THROUGH. Not the build date: the build ran today and that
    # says nothing about when the money last moved.
    as_of = max(f["date"] for f in committed)

    # "3 of the 6", not "3 more": the allocations without a figure are inside the
    # set the sum is taken over, which is what makes the sum a floor rather than
    # a total. A reader who took them for extra rows would read the floor as
    # complete, which is the one thing this line exists to prevent.
    text = (f"{_money(total)} is committed to {_n(len(projects), 'project')}, "
            + (f"and {undisclosed} of the {len(committed)} allocations carry no "
               f"published figure." if undisclosed
               else f"across {_n(len(committed), 'allocation')}."))
    return bl._fact(
        "money_in", "Money flowing in", text, as_of,
        [_digits(_money(total)), str(len(projects)), str(len(committed))]
        + ([str(undisclosed)] if undisclosed else []),
        {
            "committed": _money(total),
            "committed_count": len(committed),
            "projects": _n(len(projects), "project"),
            "project_count": len(projects),
            "undisclosed": undisclosed,
            # Counted, never summed. See the module docstring.
            "announced_count": len(announced),
            "withdrawn_count": len(withdrawn),
        },
    )


def fact_rules_that_pay(imp: dict) -> dict | None:
    """§4.2. The measures whose money direction for the bearer is support, and
    what they have paid. The direction field is the register's, not a reading
    taken here."""
    support = [m for m in imp["measures"]
               if (m.get("money") or {}).get("direction") == "support"]
    if not support:
        return None
    paid = sum(float((m["money"].get("value") or 0)) for m in support
               if m["money"].get("computable"))
    text = (f"{_n(len(support), 'measure')} in EU law "
            f"{'pays' if len(support) == 1 else 'pay'} into this sector"
            f"{f', {_money(paid)} of it so far' if paid else ''}.")
    return bl._fact(
        "rules_that_pay", "Rules that pay", text, str(bi.date.today().year),
        [str(len(support))] + ([_digits(_money(paid))] if paid else []),
        {
            "support_measures": _n(len(support), "measure"),
            "support_count": len(support),
            "support_verb": "pays" if len(support) == 1 else "pay",
            "paid": _money(paid) if paid else None,
            "measures": [m["measure"] for m in support],
        },
    )


# ---------------------------------------------------------------------------
# the sentence
# ---------------------------------------------------------------------------

def compose(short: str, by_id: dict[str, dict], templates: dict) -> dict:
    """One sentence, from whichever of the two facts exist. Three templates
    rather than one with optional halves: a template with a clause that
    sometimes disappears is a template nobody can read, and the three cases here
    are the three a sector can actually be in."""
    money = by_id.get("money_in")
    pays = by_id.get("rules_that_pay")
    slots = {"short": short}
    if money:
        slots["committed"] = money["parts"]["committed"]
        slots["projects"] = money["parts"]["projects"]
    if pays:
        slots["support_measures"] = pays["parts"]["support_measures"]
        slots["support_verb"] = pays["parts"]["support_verb"]

    if money and pays:
        key, frm = "template", ["money_in", "rules_that_pay"]
    elif money:
        key, frm = "template_no_support", ["money_in"]
    elif pays:
        key, frm = "template_no_money", ["rules_that_pay"]
    else:
        return {"text": "", "from": []}

    text = templates[key]
    for slot, value in slots.items():
        text = text.replace("{" + slot + "}", str(value))
    return {"text": " ".join(text.split()), "from": frm}


def apply_override(doc: dict, sector: str) -> None:
    """A reviewer's sentence, and the flag that says the facts moved under it.
    The same two rules as the sector lead: a reviewed sentence keeps rendering
    when the fingerprint changes, and the build says so loudly. Reverting to
    generated text would silently discard reviewed prose, which is the failure
    the review rule exists to prevent."""
    store = json.loads(bl.OVERRIDES().read_text(encoding="utf-8"))
    entry = (store.get("opportunity_overrides") or {}).get(sector)
    if not entry:
        return
    if entry.get("sentence"):
        doc["sentence"] = {
            "text": entry["sentence"],
            "from": entry.get("from", []),
            "source": "override",
            "reviewed": entry["reviewed"],
        }
    if entry.get("fingerprint") != doc["fingerprint"]:
        doc["override_stale"] = True
        doc["notes"].append(
            f"the reviewed opportunity sentence was written against facts "
            f"{entry.get('fingerprint')!r} and the facts are now {doc['fingerprint']!r} — "
            f"it still renders, and it needs re-reading")


def build(sector: str) -> dict:
    imp = bi.build(sector, bi.date.today().year)
    params = sm.index(sm.load("parameter"))
    projects = {p["id"] for p in sm.load("project") if p["sector"] == sector}
    funding = [f for f in sm.load("funding")
               if any(n.startswith("project:") and n.split(":", 1)[1] in projects
                      for n in f["finances"])]

    prose = _prose()["opportunity"]
    names = _prose()["sector_names"]["sectors"]
    # The name slots are keyed on ecosystem instance, not sector slug (brief 5
    # §2.1). One instance owns this sector, or the sentence has no subject.
    ecosystems = json.loads(
        (sm.ROOT / "data" / "transition" / "ecosystems.json").read_text(encoding="utf-8")
    )["ecosystems"]
    owner = next((e["id"] for e in ecosystems if sector in e["sectors"]), None)
    if owner is None or owner not in names:
        raise SystemExit(
            f"build_opportunity: {sector} belongs to no ecosystem instance with name "
            f"slots, so its sentence has no subject")
    short = names[owner]["short"]

    computed = [fact_money_in(funding, params), fact_rules_that_pay(imp)]
    facts = [f for f in computed if f]
    by_id = {f["id"]: f for f in facts}
    for f in facts:
        dv.check(f["text"], f"build_opportunity: {sector} fact {f['id']}",
                 exempt=tuple(f["sourced"]))

    notes: list[str] = []
    for f in facts:
        problems = bl.gate_fact(f)
        if problems:
            f["surface"] = False
            notes.append(f"the fact {f['id']} failed its gate "
                         f"({'; '.join(problems)}) — computed, not shown")

    sentence = compose(short, by_id, prose["lead"])
    if sentence["text"]:
        problems = bl.gate(sentence, by_id)
        if problems:
            # NO FALLBACK SENTENCE. The sector lead has one because a sector page
            # without an opening sentence is a page with a hole at the top of it.
            # This section has a heading that already asks the question, and the
            # honest thing for a sentence that failed its own gate is not to be
            # there. The section still renders; it opens on the money.
            notes.append(f"the sentence failed its gate ({'; '.join(problems)}) — dropped")
            sentence = {"text": "", "from": []}
    if sentence["text"]:
        sentence["source"] = "generated"

    doc = {
        "_comment": [
            "BUILT FILE — do not edit. sources/build_opportunity.py computes it from the",
            "sector's funding rows and its support-direction measures; the Opportunity",
            "section draws it and adds nothing. A reviewed replacement goes in",
            "data/transition/overrides.json under opportunity_overrides, never here.",
        ],
        "sector": sector,
        "template_version": TEMPLATE_VERSION,
        "fingerprint": bl.fingerprint(facts),
        "sentence": sentence,
        "facts": facts,
        "override_stale": False,
        "notes": notes,
    }
    apply_override(doc, sector)
    return doc


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
                print(f"build_opportunity: {path} is stale or missing — rebuild it",
                      file=sys.stderr)
                failed = True
                continue
            print(f"build_opportunity: --check, {sector} matches "
                  f"({len(doc['facts'])} facts)")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"build_opportunity: wrote {path} — {len(doc['facts'])} facts")
        if doc["sentence"]["text"]:
            print(f"  {doc['sentence']['text']}")
        for note in doc["notes"]:
            print(f"  ! {note}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

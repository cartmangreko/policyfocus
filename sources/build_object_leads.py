"""
Lead blocks for the two object kinds that did not have one: measures, projects.

    python3 build_object_leads.py            # writes data/lead/*.json
    python3 build_object_leads.py --check     # rebuilds and diffs; non-zero on drift

WHY THIS EXISTS
===============
§0.2 of the page specifications puts a lead block on every page type, and §0.8
makes indexability follow it. Until now only the sector page had one: the
measure and project pages were listed as owing theirs, and at the index opening
the measure pages were demoted until they arrived. This is their arrival, and it
is what returns 480-odd pages to the index -- one at a time, each on the day its
own lead block passes its gate.

THE SAME DISCIPLINE AS sources/build_lead.py, AND MOST OF ITS MACHINERY
=======================================================================
The gate is imported rather than re-implemented: `gate`, `gate_fact`,
`schema_words` and `fingerprint` come from build_lead, so a rule added there --
the schema-vocabulary ban, the one-sentence limit, numbers that appear in no
fact -- applies here the day it is written and not the day somebody remembers to
copy it.

What is NOT shared is the facts. A sector's facts come from panels; a measure's
come from the register row it was decoded into, and a project's from its status
history and the money attached to it.

WHAT THE MEASURE LEAD SAYS, AND WHAT IT DELIBERATELY DOES NOT
=============================================================
The measure page already puts the decoded provision at the top -- the duty text
IS the page's heading. So the lead does not restate it. It answers the five
things the provision itself does not say and a reader arriving from a search
engine needs first: who it lands on, whether it is law yet, when it bites, which
industries it names, and what it costs where anybody has priced it.

That is why the opening sentence is about STANDING and ADDRESSEE rather than
about content. A lead that repeated the heading in other words would be the
longest way yet devised to say nothing.

THE MONEY LINE IS BORROWED, NOT REWRITTEN. Where a measure is priced in a
sector's importance file, the sentence comes from build_lead.MODEL_LINE -- the
same template the sector page's lead uses for the same figure. Two sentences for
one number, differing in wording, is how a reader learns not to trust either.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

import build_importance as bi
import build_lead as bl
import display_vocabulary as dv
import number_format as nf
import sector_map as sm

OUT_DIR = sm.ROOT / "data" / "lead"
DATA = sm.ROOT / "data"
HERE = sm.ROOT / "sources"

TEMPLATE_VERSION = 1

# At most five fact lines, per §0.2. The order is the order they are computed
# in; what falls off the end is the least specific.
MAX_FACTS = 5

# What each kind of measure does, said in a verb the addressee is the subject
# of. The four keys are the register's own closed list.
TYPE_VERB = {
    "obligation": "must comply",
    "prohibition": "are prohibited",
    "right": "are given a right",
    "incentive": "are offered support",
}

# What a project's status means, in one plain clause. Keyed to
# sector_map.PROJECT_STATUSES; a missing key raises rather than degrading.
STATUS_MEANING = {
    "announced": "Nothing has been committed to it yet.",
    "funded": "It has money awarded and has not taken a final investment decision.",
    "fid": "The money is committed.",
    "construction": "It is being built.",
    "operating": "It is running.",
    "paused": "Work has stopped, and the reason is in its history below.",
    "cancelled": "It will not be built.",
}

_COUNTRY = re.compile(r'^  ([A-Z]{2}): "([^"]+)"', re.MULTILINE)


def country_names() -> dict[str, str]:
    """ISO code -> country name, read from web/lib/countries.ts.

    Read rather than duplicated, for the reason every parity check in this
    repository exists: two lists of the same 30 countries would differ within a
    year, and the difference would show up as one page calling a place by its
    code and another by its name.
    """
    src = (sm.ROOT / "web" / "lib" / "countries.ts").read_text(encoding="utf-8")
    return dict(_COUNTRY.findall(src))


def register_files() -> dict:
    return json.loads((HERE / "register_files.json").read_text(encoding="utf-8"))["files"]


def manifest() -> dict:
    return json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))


def fetched_at(slug: str, files: dict) -> str | None:
    """The day the act's text was last fetched, as an ISO date.

    This is the as-of date for everything the register says about a measure:
    the article it sits in, its timing, the industries it names. All of them are
    facts about a document, and the honest date on a fact about a document is
    the day the document was read.
    """
    dates = []
    for key in files.get(slug, {}).get("manifest_keys", ()):
        path = HERE / f"{key}.fetch.json"
        if path.exists():
            stamp = json.loads(path.read_text(encoding="utf-8")).get("fetched_at")
            if stamp:
                dates.append(stamp[:10])
    return max(dates) if dates else None


def standing(slug: str, files: dict, mf: dict) -> str | None:
    """`adopted`, `proposed` or `mixed`, by the same STATUS_RULE the findings
    gate applies. Guessing is the one thing that rule exists to prevent, so an
    unanswerable file returns None and its measures get no lead."""
    entry = files.get(slug) or {}
    seen = set()
    if entry.get("declared_status"):
        seen.add(entry["declared_status"])
    for key in entry.get("manifest_keys", ()):
        status = (mf.get(key) or {}).get("status")
        if status:
            seen.add(status)
    return _status_of(seen)


def _status_of(seen: set[str]) -> str | None:
    if seen == {"adopted"}:
        return "adopted"
    if seen == {"proposed"}:
        return "proposed"
    if seen == {"adopted", "proposed"}:
        return "mixed"
    return None


STANDING_WHY = {
    "adopted": "This is law in force, not a proposal.",
    "proposed": "This is a Commission proposal: it is not law yet, and it can change "
                "before it is.",
    "mixed": "The act this comes from is partly law in force and partly a proposal that "
             "can still change.",
}

STANDING_CLAUSE = {
    "adopted": "and this is law in force",
    "proposed": "and this is not law yet",
    "mixed": "and it sits in an act that is partly law and partly a proposal",
}


def _fact(fid, text, as_of, numbers=(), sourced=(), href=None) -> dict:
    return {
        "id": fid,
        "text": text,
        "as_of": as_of or "",
        "numbers": [bl._norm_number(n) for n in numbers],
        "sourced": list(sourced),
        "href": href,
        "surface": True,
    }


# ---------------------------------------------------------------------------
# measures
# ---------------------------------------------------------------------------

def sector_names() -> dict[str, str]:
    return {k: v["name"] for k, v in sm.sectors().items()}


def priced_lines(measure_id: str, names: dict[str, str]) -> list[dict]:
    """The money a measure carries, one line per sector that has priced it.

    The sentence is build_lead.MODEL_LINE — the same template the sector page
    uses for the same figure, keyed by the same money model. Two wordings for
    one number is how a reader learns to trust neither.
    """
    out = []
    imp_dir = DATA / "transition" / "importance"
    if not imp_dir.exists():
        return out
    for path in sorted(imp_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        sector = doc["sector"]
        for m in doc["measures"]:
            if m["measure"] != measure_id or not m["money"]["computable"]:
                continue
            money = m["money"]
            model = money["model"]
            if model not in bl.MODEL_LINE:
                continue
            if money["per_tonne"] is not None:
                figure = nf.money_rate(money["per_tonne"])
                numbers = [f"{money['per_tonne']:,.2f}"]
            else:
                figure = nf.money_long(money["value"])
                numbers = [f"{money['value'] / 1e6:,.0f}"]
            out.append(_fact(
                f"priced_{sector.replace('/', '_')}",
                bl.MODEL_LINE[model].format(sector=names[sector].lower(), figure=figure),
                str(doc["priced_year"]), numbers,
                href=f"/sectors/{sector}",
            ))
    return out


def measure_lead(row: dict, slug: str, files: dict, mf: dict,
                 names: dict[str, str]) -> dict | None:
    """One measure's lead block, or None where the register cannot answer.

    None is a real outcome and not a failure: a measure whose act has no
    recorded legal standing cannot be given a sentence that says whether it is
    law, and a lead that left that out would be the one sentence a reader most
    needs missing. The page stays demoted until the register can say.
    """
    stand = standing(slug, files, mf)
    verb = TYPE_VERB.get(row.get("measure_type") or "")
    addressee = (row.get("addressee") or "").strip().rstrip(".")
    as_of = fetched_at(slug, files)
    # No fetch date means the act text was read before the fetcher existed
    # (omnibus, and only omnibus). Every fact this lead would carry is a fact
    # about a document, and the honest as-of for one of those is the day the
    # document was read — so there is no lead, and by §0.8 no index entry,
    # until the act is fetched properly. `skipped` counts it on every run.
    if not (stand and verb and addressee and as_of):
        return None
    display = files[slug]["display_name"]
    facts: list[dict] = []

    if as_of:
        facts.append(_fact(
            "provision",
            f"It is {row['article']}, in the {display}.",
            as_of, sourced=(row["article"], display),
        ))
        # `when` is the act's own words for its timing and is quoted as such:
        # the field runs from "from 2028" to "upon incorporation of the
        # Regulation in the EEA Agreement", and no template turns both of those
        # into the same sentence without breaking one of them.
        facts.append(_fact(
            "timing",
            f"The act gives its timing as: {row['when']}.",
            as_of, sourced=(row["when"],),
        ))
        named = [names[s] for s in row.get("sectors_named", []) if s in names]
        if named:
            listed = ", ".join(named[:-1]) + (" and " if len(named) > 1 else "") + named[-1]
            facts.append(_fact(
                "reach",
                f"It names {len(named)} industries by name: {listed}."
                if len(named) > 1 else f"It names one industry by name: {listed}.",
                as_of, [str(len(named))], sourced=tuple(named),
            ))
        else:
            facts.append(_fact(
                "reach",
                "It names no industry: it applies across the economy rather than to one "
                "of them.",
                as_of,
            ))
        if row.get("verification") and row.get("frequency"):
            facts.append(_fact(
                "checked",
                f"Compliance is checked by {row['verification']}, {row['frequency']}.",
                as_of, sourced=(row["verification"], row["frequency"]),
            ))

    facts += priced_lines(f"{slug}:{row['id']}", names)

    # Both blocks trace to the provision fact: the article and act named there
    # are where the addressee, the type and the legal standing all come from.
    sentence = {
        "text": f"{addressee} {verb}, {STANDING_CLAUSE[stand]}.",
        "from": ["provision"],
        # The addressee is the register's wording, and the numbers and terms of
        # art inside it are the act's rather than this template's.
        "sourced": [addressee],
        "source": "generated",
    }
    why = {"text": STANDING_WHY[stand], "from": ["provision"], "source": "generated"}
    return assemble(f"{slug}:{row['id']}", sentence, why, facts)


# ---------------------------------------------------------------------------
# projects
# ---------------------------------------------------------------------------

def _uncapitalise(name: str) -> str:
    """A name set mid-sentence, without flattening an acronym. "Post-combustion
    carbon capture" lowercases; "CO2 transport and storage" does not, and a
    blanket .lower() turned it into "co2", which is a different substance as far
    as a reader is concerned."""
    return name[0].lower() + name[1:] if len(name) > 1 and name[1].islower() else name


def _possessive(name: str) -> str:
    """Heidelberg Materials' project, not Heidelberg Materials's."""
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def project_lead(p: dict, params: dict, funding: list[dict], techs: dict,
                 countries: dict[str, str], names: dict[str, str]) -> dict | None:
    history = p.get("status_history") or []
    if not history or p["status"] not in STATUS_MEANING:
        return None
    # THE STATUS FACT DATES FROM WHEN THE STATUS WAS ENTERED, which is not
    # always the last entry: a history may carry later sources on a project
    # whose status they do not change. "Slite CCS was paused on" takes the date
    # it was paused, not the date of the most recent thing written about it.
    # `as_of`, which is a different claim, still takes the latest source.
    last = sm.entered(p) or history[-1]
    source_dates = [s["date"] for s in p.get("sources", []) if s.get("date")]
    as_of = max(source_dates) if source_dates else history[-1]["date"]
    where = countries.get(p.get("country", ""), p.get("country", ""))
    place = f"{p['plant']}, {where}" if p.get("plant") else where

    facts = [
        _fact("status", f"{p['name']} {bl.STATUS_VERB[last['status']]} on "
                        f"{bl._long_date(last['date'])}.",
              last["date"], sourced=(p["name"],), href=last.get("source_url")),
        _fact("where", f"It is at {place}.", as_of, sourced=(place,)),
    ]

    tech_names = [_uncapitalise(techs[t]["name"]) for t in p.get("technology", [])
                  if t in techs]
    if tech_names:
        listed = ", ".join(tech_names[:-1]) + (" and " if len(tech_names) > 1 else "") \
            + tech_names[-1]
        facts.append(_fact("technology", f"It uses {listed}.", as_of,
                           sourced=tuple(tech_names)))

    cap = p.get("capacity") or {}
    if cap.get("value") and cap.get("unit"):
        param = params.get(cap.get("parameter") or "")
        facts.append(_fact(
            "capacity",
            f"It is built for {cap['value']:,} {cap['unit']}.",
            (param or {}).get("date_of_value") or as_of,
            [f"{cap['value']:,}"], sourced=(cap["unit"],),
        ))

    total, latest = 0.0, None
    for f in funding:
        if f"project:{p['id']}" not in (f.get("finances") or []):
            continue
        if f["status"] not in sm.FUNDING_COMMITTED:
            continue
        amount = params.get(f.get("amount") or "")
        if amount and isinstance(amount.get("value"), (int, float)):
            # IN EUROS, NOT IN WHATEVER THE PARAMETER IS DENOMINATED IN. A
            # funding amount is stored as the sourced figure and its unit —
            # 191 "EUR million" — and this loop used to add the 191 and then
            # divide the total by a million, so every project lead on the site
            # read "€0 million of public money has been committed to it".
            # bi._eur does the conversion and raises on a unit nobody has ruled
            # on, which is the whole reason it exists.
            total += bi._eur(amount)
            latest = max(latest or f["date"], f["date"])
    if total:
        facts.append(_fact(
            "funding",
            f"{nf.money_long(total)} of public money has been committed to it.",
            latest or as_of, [f"{total / 1e6:,.0f}"], href="#funding",
        ))
    else:
        facts.append(_fact(
            "funding", "No committed public money is on file for it.", as_of,
        ))

    sector = names.get(p["sector"], p["sector"]).lower()
    sentence = {
        "text": f"{p['name']} is {_possessive(p['company'])} {sector} project at {place}.",
        "from": ["where"],
        "sourced": [p["name"], p["company"], place],
        "source": "generated",
    }
    why = {"text": STATUS_MEANING[p["status"]], "from": ["status"], "source": "generated"}
    return assemble(p["id"], sentence, why, facts)


# ---------------------------------------------------------------------------
# assembly, and the gate
# ---------------------------------------------------------------------------

def assemble(oid: str, sentence: dict, why: dict, facts: list[dict]) -> dict | None:
    """Everything that has to be true before a page is allowed to open.

    A FAILED GATE COSTS THE PAGE ITS INDEX ENTRY, which is the whole point: §0.8
    says indexability follows the lead block, so a lead block that cannot be
    trusted has to take the page down with it rather than render anyway. That is
    why this returns None rather than falling back to a duller sentence the way
    the sector lead does — a sector page has other reasons to exist, and there
    is exactly one of these per page.
    """
    notes: list[str] = []
    for f in list(facts):
        problems = bl.gate_fact(f)
        if problems:
            f["surface"] = False
            notes.append(f"{f['id']}: {'; '.join(problems)}")
    facts = [f for f in facts if f["surface"]][:MAX_FACTS] + \
            [f for f in facts if not f["surface"]]
    by_id = {f["id"]: f for f in facts}

    for block in (sentence, why):
        problems = bl.gate(block, by_id)
        if problems:
            return None
    if not [f for f in facts if f["surface"]]:
        return None

    return {
        "id": oid,
        "template_version": TEMPLATE_VERSION,
        "fingerprint": bl.fingerprint(facts),
        "sentence": sentence,
        "why_it_matters": why,
        "facts": facts,
        "override_stale": False,
        "notes": notes,
    }


COMMENT = [
    "BUILT FILE — do not edit. sources/build_object_leads.py computes it; the pages draw",
    "it through web/components/LeadBlock.tsx and add nothing.",
    "",
    "Keyed by object id. An object with no entry has no lead block, which by §0.8 of the",
    "page specifications means its page is not indexable — so an absence here is a",
    "decision the gate made, and `skipped` says how many were made and why.",
]


def build() -> tuple[dict, dict]:
    files, mf = register_files(), manifest()
    names, countries = sector_names(), country_names()
    params = sm.index(sm.load("parameter"))
    techs = sm.index(sm.load("technology"))
    funding = sm.load("funding")

    measures, skipped = {}, 0
    for slug in sorted(files):
        path = DATA / f"{slug}.json"
        if not path.exists():
            continue
        for row in json.loads(path.read_text(encoding="utf-8")):
            lead = measure_lead(row, slug, files, mf, names)
            if lead:
                measures[lead["id"]] = lead
            else:
                skipped += 1

    projects = {}
    for p in sm.load("project"):
        lead = project_lead(p, params, funding, techs, countries, names)
        if lead:
            projects[p["id"]] = lead

    for store in (measures, projects):
        for lead in store.values():
            for f in lead["facts"]:
                dv.check(f["text"], f"build_object_leads: {lead['id']} fact {f['id']}",
                         exempt=tuple(f["sourced"]))

    return (
        {"_comment": COMMENT, "kind": "measure", "skipped": skipped, "leads": measures},
        {"_comment": COMMENT, "kind": "project", "skipped": 0, "leads": projects},
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = False
    for doc, name in zip(build(), ("measures", "projects")):
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = OUT_DIR / f"{name}.json"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"build_object_leads: {path} is stale or missing — rebuild it",
                      file=sys.stderr)
                failed = True
                continue
            print(f"build_object_leads: --check, {name} matches "
                  f"({len(doc['leads'])} leads, {doc['skipped']} without one)")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"build_object_leads: wrote {path} — {len(doc['leads'])} leads, "
                  f"{doc['skipped']} without one")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

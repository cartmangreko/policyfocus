"""
Rank the register's measures for one sector, by what they are worth to it.

    python3 build_importance.py                # writes data/transition/importance/*.json
    python3 build_importance.py --check        # rebuilds and diffs; exits non-zero on drift

The register knows 71 measures that reach cement. A sector page that listed all
71 would be the register again with a different heading. So the measures are
ranked, and the ranking is computed from data rather than asserted, because a
ranking nobody can reproduce is an opinion with a table around it.

THREE COMPONENTS
================
1. MONEY -- a euro figure computed from the measure and the sector's parameters,
   by a named model. Every input is a parameter id, so the number on the page
   walks back to a quoted sentence in someone else's document. A measure with no
   model scores 0 here and SAYS SO, naming the parameters that would give it
   one. Silence and zero are different states and the output distinguishes them.

2. BOTTLENECK_LINKAGE -- the sum of the weights on this measure's edges to named
   bottlenecks, from data/transition/bottlenecks.json. This is the judgement
   layer, and it is bounded on both sides: the thing being judged is a named
   constraint, and the edge carries the register's own wording as evidence.

3. ATTENTION -- mentions in the last 24 months across a fixed source list,
   collected by the watch agent. It is a CROSS-CHECK, never a lift: a measure
   with 0 money and 0 linkage does not enter the sector view because the trade
   press is talking about it. What attention is for is the opposite finding --
   a measure everybody is discussing that this model scores at nothing is either
   a missing model or a missing edge, and the sanity report at the end of the
   run is where that shows up.

RANK = money, then bottleneck_linkage, then attention as tie-break. Money first
is a deliberate bet about the audience: an investor covering European
industrials is asking which instrument moves the P&L, and the honest answer
usually is not the one with the most commentary attached.

THE UNIT PROBLEM, AND WHY THE RANKING SURVIVES IT
=================================================
The free-allocation model wants a sector total: allowances withdrawn x carbon
price x sector output. The first two are sourced; sector output is not (see
data/transition/GAPS.md). So money is computed per tonne of clinker and the
output field says `eur_per_tonne_clinker` rather than `eur`.

This is not a fudge, and the reason is worth stating: within one sector, the
missing scalar is the SAME scalar for every measure, so it cannot reorder
anything. It matters when cement is compared with steel, and it will be wrong to
do that until an output parameter exists for both. The scale field is carried on
every score precisely so a later comparison cannot quietly mix the two.

WHICH YEAR
==========
The free-allocation cost is a schedule, not a level, so a rank computed from it
has to pick a year. It picks the current one: the question the page answers is
what this measure costs the sector now, and a measure that bites in 2030 has
four more years of arguing ahead of it. The 2030 figure is computed too and
carried as context on the same score, so the trajectory is visible without
letting it decide the order.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import sector_map as sm

OUT_DIR = sm.ROOT / "data" / "transition" / "importance"
ATTENTION_FILE = sm.ROOT / "data" / "transition" / "attention.json"
OVERRIDES_FILE = sm.ROOT / "data" / "transition" / "overrides.json"

ATTENTION_WINDOW_MONTHS = 24


# ---------------------------------------------------------------------------
# Money models
#
# One function per model. Each returns a dict with the same shape whether or not
# it could compute anything, because "not computable, and here is what is
# missing" is a result the page prints, not an error the build swallows.
# ---------------------------------------------------------------------------

def _money(value, scale, model, inputs, formula, missing=(), context=None):
    return {
        "value": value,
        "scale": scale,
        "model": model,
        "computable": value is not None,
        "inputs": list(inputs),
        "formula": formula,
        "missing": list(missing),
        "context": context or [],
    }


def model_free_allocation_phaseout(params: dict, year: int) -> dict:
    """Allowances withdrawn x carbon price, per tonne of clinker.

    Withdrawn share is (1 - CBAM factor): in 2026 the factor is 97,5 %, so 2,5 %
    of the free allocation a cement kiln would otherwise receive is gone, and the
    kiln buys that fraction of its benchmarked allowances at the market price.
    """
    factor = params.get(f"cbam-factor-{year}")
    bench = params.get("clinker-benchmark-2026-2030")
    price = params.get("eua-price-spot")
    needed = [f"cbam-factor-{year}", "clinker-benchmark-2026-2030", "eua-price-spot"]
    missing = [n for n, p in zip(needed, (factor, bench, price)) if p is None]
    formula = "(1 - cbam_factor) x clinker_benchmark x eua_price"
    if missing:
        return _money(None, "eur_per_tonne_clinker", "free_allocation_phaseout",
                      [n for n in needed if n not in missing], formula, missing)
    withdrawn = 1 - (factor["value"] / 100)
    value = round(withdrawn * bench["value"] * price["value"], 2)
    return _money(value, "eur_per_tonne_clinker", "free_allocation_phaseout",
                  needed, formula)


def model_cbam_certificates(params: dict) -> dict:
    """Embedded emissions x carbon price x import volume.

    Declared and not computable: neither the cement import volume nor the CBAM
    default embedded-emissions value for cement has been sourced yet. The model
    is written out anyway so that the missing parameters are named on the page
    rather than left as an absence.
    """
    needed = ["cement-import-volume", "cbam-cement-embedded-emissions", "eua-price-spot"]
    missing = [n for n in needed if n not in params]
    formula = "embedded_emissions x eua_price x import_volume"
    if missing:
        return _money(None, "eur_per_year", "cbam_certificates",
                      [n for n in needed if n not in missing], formula, missing)
    value = (params["cbam-cement-embedded-emissions"]["value"]
             * params["eua-price-spot"]["value"]
             * params["cement-import-volume"]["value"])
    return _money(round(value, 2), "eur_per_year", "cbam_certificates", needed, formula)


def model_grant_programme(measure_id: str, projects: list[dict]) -> dict:
    """Public money awarded to this sector's projects UNDER THIS MEASURE.

    A funding line counts only where it names a register measure. The Innovation
    Fund grants in projects.json name a programme and not a measure, because the
    register has read the ETS revision and not the Fund's own decisions -- so
    this model correctly returns nothing today, and will start returning
    something the moment a Fund provision is ingested.
    """
    total = 0
    contributing = []
    for p in projects:
        for f in p.get("public_funding") or []:
            if f.get("measure") == measure_id and f.get("amount_eur"):
                total += f["amount_eur"]
                contributing.append(p["id"])
    formula = "sum of public_funding.amount_eur where public_funding.measure = this measure"
    if not contributing:
        return _money(None, "eur_awarded", "grant_programme", [], formula,
                      ["no project funding line names this measure"])
    return _money(total, "eur_awarded", "grant_programme", contributing, formula)


# Which model applies to which measure. Keyed by `<file>:<id>` so it is explicit
# rather than pattern-matched: a model firing on a measure nobody checked is the
# failure mode that would put a wrong euro figure on a page.
#
# ets:CBAM-02 is deliberately absent. It phases out free allocation for product
# categories ADDED to the CBAM list later, on the same schedule -- pricing it at
# the cement clinker benchmark today would double-count the same euro against
# cement and rank a measure about future goods second in a cement view.
MODELS = {
    "ets:CBAM-01": "free_allocation_phaseout",
    "cbam:FIN-03": "cbam_certificates",
    "cbam:DECL-03": "cbam_certificates",
    "cbam:FIN-01": "cbam_certificates",
}


def money_for(measure_id: str, params: dict, projects: list[dict], year: int) -> dict:
    model = MODELS.get(measure_id)
    if model == "free_allocation_phaseout":
        score = model_free_allocation_phaseout(params, year)
        later = model_free_allocation_phaseout(params, 2030)
        if later["computable"]:
            score["context"] = [{
                "label": f"the same model at 2030",
                "value": later["value"],
                "scale": later["scale"],
            }]
        return score
    if model == "cbam_certificates":
        return model_cbam_certificates(params)
    if model == "grant_programme":
        return model_grant_programme(measure_id, projects)
    return _money(None, None, None, [], None,
                  ["no money model applies to this measure"])


# ---------------------------------------------------------------------------
# The build
# ---------------------------------------------------------------------------

def load_attention() -> dict:
    """Mention counts per measure, written by the watch agent's project channel.

    Absent until that channel has run. Absent is reported as absent: a zero
    attention count and "no data" are not the same claim, and the sanity report
    below refuses to run on the second one."""
    if not ATTENTION_FILE.exists():
        return {"available": False, "window_months": ATTENTION_WINDOW_MONTHS, "counts": {}}
    doc = json.loads(ATTENTION_FILE.read_text(encoding="utf-8"))
    doc["available"] = True
    return doc


def load_overrides() -> dict:
    if not OVERRIDES_FILE.exists():
        return {}
    return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8")).get("overrides", {})


def register_rows(sector: str) -> list[dict]:
    rows = []
    files = json.loads((sm.ROOT / "sources" / "register_files.json").read_text(encoding="utf-8"))
    for slug in files["files"]:
        path = sm.ROOT / "data" / f"{slug}.json"
        if not path.exists():
            continue
        for r in json.loads(path.read_text(encoding="utf-8")):
            reach = set(r.get("sectors_reached") or []) | set(r.get("sectors_named") or [])
            if sector in reach:
                rows.append({"file": slug, "row": r})
    return rows


def build(sector: str, year: int) -> dict:
    params = sm.index(sm.load("parameter"))
    bottlenecks = sm.load("bottleneck")
    projects = [p for p in sm.load("project") if p["sector"] == sector]
    attention = load_attention()
    overrides = load_overrides().get(sector, {})

    linkage: dict[str, list[dict]] = {}
    for b in bottlenecks:
        if b["sector"] != sector:
            continue
        for m in b.get("measures") or []:
            linkage.setdefault(m["measure"], []).append({
                "bottleneck": b["id"],
                "bottleneck_name": b["name"],
                "type": b["type"],
                "rel": m["rel"],
                "weight": m["weight"],
                "note": m["note"],
                "evidence": m["evidence"],
            })

    scored = []
    for entry in register_rows(sector):
        slug, row = entry["file"], entry["row"]
        mid = f"{slug}:{row['id']}"
        money = money_for(mid, params, projects, year)
        edges = linkage.get(mid, [])
        weight_sum = round(sum(e["weight"] for e in edges), 3)
        count = attention["counts"].get(mid, 0) if attention["available"] else None
        scored.append({
            "measure": mid,
            "file": slug,
            "id": row["id"],
            "measure_type": row.get("measure_type"),
            "article": row.get("article"),
            "when": row.get("when"),
            "duty": row.get("duty") or row.get("entitlement") or "",
            "money": money,
            "bottleneck_linkage": {
                "count": len(edges),
                "weight": weight_sum,
                "edges": edges,
            },
            "attention": {
                "available": attention["available"],
                "count": count,
                "window_months": attention.get("window_months", ATTENTION_WINDOW_MONTHS),
            },
        })

    def sort_key(s):
        return (
            -(s["money"]["value"] or 0),
            -s["bottleneck_linkage"]["weight"],
            -(s["attention"]["count"] or 0),
            s["measure"],
        )

    scored.sort(key=sort_key)
    for i, s in enumerate(scored, start=1):
        s["rank"] = i
        # THE SECTOR-VIEW GATE. A measure reaches the sector page only on money or
        # on a named bottleneck. Everything else stays in the register, which is
        # where the other 60-odd cement measures belong: reachable, not ranked.
        s["in_sector_view"] = bool((s["money"]["value"] or 0) > 0
                                   or s["bottleneck_linkage"]["weight"] > 0)
        ov = overrides.get(s["measure"])
        if ov:
            s["override_rank"] = ov["rank"]
            s["override_reason"] = ov["reason"]

    if overrides:
        scored.sort(key=lambda s: (s.get("override_rank") or s["rank"], s["measure"]))

    return {
        "_comment": [
            "BUILT FILE — do not edit. Written by sources/build_importance.py; the gate",
            "rebuilds it and fails on any difference. Change the inputs, not this.",
            "Inputs: the register (data/*.json), data/transition/bottlenecks.json,",
            "data/transition/parameters.json, data/transition/attention.json (when the",
            "watch agent has run) and data/transition/overrides.json.",
        ],
        "sector": sector,
        "priced_year": year,
        "built_from": {
            "parameters": sorted({p for s in scored for p in s["money"]["inputs"]
                                  if p in params}),
            "attention_available": attention["available"],
        },
        "measures": scored,
    }


def sanity_report(doc: dict) -> list[str]:
    """Top five by score against top five by attention. Disjoint sets are the
    finding: either the model is missing a euro figure everybody else can see,
    or the commentary is chasing something that costs nobody anything. It is
    printed at build time and never rendered -- it is a note to whoever is
    reviewing the ranking, not a page."""
    lines = []
    top = [m for m in doc["measures"] if m["in_sector_view"]][:5]
    lines.append("  top five by score:")
    for m in top:
        money = m["money"]
        money_str = (f"{money['value']} {money['scale']}" if money["computable"]
                     else f"no money ({', '.join(money['missing'])})")
        lines.append(f"    {m['rank']}. {m['measure']} — {money_str}"
                     f", linkage {m['bottleneck_linkage']['weight']}")
    if not doc["built_from"]["attention_available"]:
        lines.append("  top five by attention: NOT AVAILABLE — the watch agent's project")
        lines.append("    channel has not written data/transition/attention.json yet, so the")
        lines.append("    cross-check on this ranking has not been run.")
        return lines
    by_attention = sorted(doc["measures"], key=lambda m: -(m["attention"]["count"] or 0))[:5]
    lines.append("  top five by attention:")
    for m in by_attention:
        lines.append(f"    {m['measure']} — {m['attention']['count']} mentions")
    disjoint = {m["measure"] for m in top} ^ {m["measure"] for m in by_attention}
    if disjoint:
        lines.append(f"  FLAGGED for review — in one list and not the other: "
                     f"{', '.join(sorted(disjoint))}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild and diff against what is committed; write nothing")
    ap.add_argument("--sector", action="append", default=None)
    ap.add_argument("--year", type=int, default=date.today().year)
    args = ap.parse_args()

    sectors = args.sector or ["cement"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failed = False

    for sector in sectors:
        doc = build(sector, args.year)
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        path = OUT_DIR / f"{sector}.json"
        if args.check:
            if not path.exists():
                print(f"build_importance: {path} is missing; run without --check")
                failed = True
                continue
            if path.read_text(encoding="utf-8") != text:
                print(f"build_importance: {path} is stale — rebuild it")
                failed = True
                continue
            print(f"build_importance: {sector} up to date "
                  f"({sum(1 for m in doc['measures'] if m['in_sector_view'])} of "
                  f"{len(doc['measures'])} measures in the sector view)")
        else:
            path.write_text(text, encoding="utf-8")
            print(f"build_importance: wrote {path} — "
                  f"{sum(1 for m in doc['measures'] if m['in_sector_view'])} of "
                  f"{len(doc['measures'])} measures in the sector view")
        print("\n".join(sanity_report(doc)))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

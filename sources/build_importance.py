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

def _money(value, scale, model, inputs, formula, missing=(), *,
           direction=None, bearer=None, per_tonne=None, annual_total=None,
           context=None, caveats=()):
    """One money score, the same shape whether or not it computed.

    DIRECTION AND BEARER. A withdrawn allowance and a grant are both money
    attached to a measure, and a ranking that shows only magnitude says the same
    thing about both. `direction` is cost or support, from the point of view of
    the sector; `bearer` is who actually pays or receives -- an EU producer, an
    importer, a project developer. The pair is what lets the sector view net a
    column instead of adding unlike things, and it is why the CBAM certificate
    cost can rank first without implying it lands on a European kiln.

    TWO FIGURES, DELIBERATELY. `per_tonne` is what the ranking sorts on, because
    cement is thought about in euros per tonne and because it survives the
    missing sector-output scalar. `annual_total` is the number an investor
    quotes, and exists only where a volume parameter makes it real.
    """
    return {
        "value": value,
        "scale": scale,
        "model": model,
        "direction": direction,
        "bearer": bearer,
        "per_tonne": per_tonne,
        "annual_total": annual_total,
        "computable": value is not None,
        "inputs": list(inputs),
        "formula": formula,
        "missing": list(missing),
        "caveats": list(caveats),
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
                      [n for n in needed if n not in missing], formula, missing,
                      direction="cost", bearer="eu_producer")
    withdrawn = 1 - (factor["value"] / 100)
    value = round(withdrawn * bench["value"] * price["value"], 2)
    return _money(value, "eur_per_tonne_clinker", "free_allocation_phaseout",
                  needed, formula, direction="cost", bearer="eu_producer",
                  per_tonne=value,
                  caveats=[
                      "The figure is the cost of the WITHDRAWN benchmark allocation, not the full "
                      "carbon cost of a plant: a kiln emitting above the benchmark pays for its "
                      "excess on top of this, and always did.",
                      "The carbon price is held flat at today's level across the whole schedule. "
                      "That is an assumption, not a forecast, and the model is linear in it.",
                  ])


def model_cbam_certificates(params: dict, year: int) -> dict:
    """Embedded emissions net of the free-allocation adjustment, x carbon price,
    x import volume. Two CN lines: clinker and grey Portland cement.

    THE ADJUSTMENT IS THE WHOLE POINT. Gross embedded emissions times the carbon
    price overstates the obligation by an order of magnitude in 2026, because the
    certificates to surrender are reduced to reflect the free allocation EU
    producers still get -- an importer in 2026 pays for the sliver the CBAM
    factor has opened, the same sliver ets:CBAM-01 charges a European kiln for.
    Modelled here as benchmark x CBAM factor, which is the shape of the
    adjustment; Commission Implementing Regulation (EU) 2025/2620 sets its exact
    form and has not been read, so the figure is carried as an approximation and
    says so.

    The clinker line maps onto the clinker benchmark one to one. The cement line
    does not -- a tonne of cement contains less than a tonne of clinker -- so the
    same benchmark is applied to it, which UNDERSTATES the adjustment and
    therefore overstates the cost of that line. Stated rather than fudged.
    """
    needed = ["cbam-default-grey-clinker-2026", "cbam-default-grey-cement-2026",
              "cement-imports-clinker-2025", "cement-imports-grey-cement-2025",
              "clinker-benchmark-2026-2030", f"cbam-factor-{year}", "eua-price-spot"]
    missing = [n for n in needed if n not in params]
    formula = ("(default_embedded_emissions - clinker_benchmark x cbam_factor) "
               "x eua_price x import_volume, per CN line")
    if missing:
        return _money(None, "eur_per_year", "cbam_certificates",
                      [n for n in needed if n not in missing], formula, missing,
                      direction="cost", bearer="importer")

    price = params["eua-price-spot"]["value"]
    bench = params["clinker-benchmark-2026-2030"]["value"]
    factor = params[f"cbam-factor-{year}"]["value"] / 100
    free = bench * factor

    lines = []
    total = 0.0
    for label, dflt, vol in (
        ("CN 2523 10 clinker", "cbam-default-grey-clinker-2026", "cement-imports-clinker-2025"),
        ("CN 2523 29 grey cement", "cbam-default-grey-cement-2026", "cement-imports-grey-cement-2025"),
    ):
        chargeable = max(0.0, params[dflt]["value"] - free)
        per_t = chargeable * price
        line_total = per_t * params[vol]["value"] * 1e6
        total += line_total
        lines.append({"label": label,
                      "chargeable_tco2_per_t": round(chargeable, 3),
                      "eur_per_tonne": round(per_t, 2),
                      "volume_mt": params[vol]["value"],
                      "eur_per_year": round(line_total, 0)})

    # The ranking figure is the clinker line: it is the one whose adjustment maps
    # cleanly onto the benchmark, and it is the number an analyst compares with
    # the free-allocation cost on a European kiln.
    per_tonne = lines[0]["eur_per_tonne"]
    return _money(round(total, 0), "eur_per_year", "cbam_certificates", needed, formula,
                  direction="cost", bearer="importer",
                  per_tonne=per_tonne, annual_total=round(total, 0),
                  context=[{"label": l["label"],
                            "value": l["eur_per_tonne"],
                            "scale": "eur_per_tonne_of_goods",
                            "detail": f"{l['volume_mt']} Mt imported, "
                                      f"{l['chargeable_tco2_per_t']} tCO2/t chargeable"}
                           for l in lines],
                  caveats=[
                      "The free-allocation adjustment is modelled as benchmark x CBAM factor. "
                      "IR (EU) 2025/2620 sets its exact form and has not been read, so this is an "
                      "approximation of the right shape rather than the statutory calculation.",
                      "The cement line applies the clinker benchmark to a tonne of cement, which "
                      "understates its adjustment and so overstates that line's cost.",
                      "Volumes are 2025 full-year imports, which ran about 23% above 2024 ahead of "
                      "the definitive period. A repeat of 2025 is an assumption, not a projection.",
                  ])


def model_grant_programme(measure_id: str, projects: list[dict]) -> dict:
    """Public money awarded to this sector's projects UNDER THIS MEASURE.

    A funding line counts only where it names a register measure, and the notes
    on those lines are part of the result: the Innovation Fund awards below were
    made under the Fund as it stands, while the register knows the Fund through
    the ETS revision's Art. 10cb. The total is real money into real plants either
    way, which is why it is counted, and the caveat travels with it.

    This is a STOCK, not a rate: grants awarded to date, not euros per year and
    not euros per tonne. It therefore never competes with a per-tonne figure in
    the ranking, and the sector view nets it separately or not at all.
    """
    total = 0
    contributing = []
    caveats = []
    unpriced = 0
    for p in projects:
        for f in p.get("public_funding") or []:
            if f.get("measure") != measure_id:
                continue
            if f.get("amount_eur"):
                total += f["amount_eur"]
                contributing.append(p["id"])
            else:
                unpriced += 1
            if f.get("measure_note") and f["measure_note"] not in caveats:
                caveats.append(f["measure_note"])
    formula = "sum of public_funding.amount_eur where public_funding.measure = this measure"
    if not contributing:
        return _money(None, "eur_awarded", "grant_programme", [], formula,
                      ["no project funding line names this measure"],
                      direction="support", bearer="project_developer")
    if unpriced:
        caveats.append(f"{unpriced} further funding line(s) under this measure carry no published "
                       f"amount and are not in the total, which is therefore a floor.")
    return _money(total, "eur_awarded", "grant_programme", contributing, formula,
                  direction="support", bearer="project_developer",
                  annual_total=None, caveats=caveats)


# Which model applies to which measure. Keyed by `<file>:<id>` so it is explicit
# rather than pattern-matched: a model firing on a measure nobody checked is the
# failure mode that would put a wrong euro figure on a page.
#
# ets:CBAM-02 is deliberately absent. It phases out free allocation for product
# categories ADDED to the CBAM list later, on the same schedule -- pricing it at
# the cement clinker benchmark today would double-count the same euro against
# cement and rank a measure about future goods second in a cement view.
#
# Only ONE of the CBAM rows carries the certificate model. The obligation to hold
# and surrender certificates is what costs money; the reporting and verification
# rows around it are how that obligation is administered, and pricing each of
# them at the full certificate bill would state the same euro four times.
MODELS = {
    "ets:CBAM-01": "free_allocation_phaseout",
    "ets:FND-03": "grant_programme",
    "cbam:FIN-03": "cbam_certificates",
}


def money_for(measure_id: str, params: dict, projects: list[dict], year: int) -> dict:
    model = MODELS.get(measure_id)
    if model == "free_allocation_phaseout":
        score = model_free_allocation_phaseout(params, year)
        later = model_free_allocation_phaseout(params, 2030)
        if later["computable"]:
            score["context"] = [{
                "label": "the same model at 2030",
                "value": later["value"],
                "scale": later["scale"],
            }]
        return score
    if model == "cbam_certificates":
        return model_cbam_certificates(params, year)
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


def register_rows(sector: str, projects: list[dict]) -> list[dict]:
    """The measures this sector's ranking considers, and how each one got here.

    TWO WAYS IN, and the second one is new. The first is the register's own
    reading: the measure names the sector or reaches it. The second is MONEY --
    a measure that has demonstrably paid for plants in this sector reaches it
    through the grant, whatever its text names.

    The Innovation Fund is why the second exists. Its provision names ccs,
    shipping, aviation and clean tech, and not cement; on the register's reading
    it does not reach cement at all. It has also put €381 million into European
    cement plants, which is the largest single support figure on this page. A
    ranking that dropped it because the article does not say "cement" would be
    obeying the letter of the register against the evidence in its own project
    file.

    The route is recorded on the row as `reach`, so the sector page can say why a
    measure is there rather than leaving a reader to assume the text names them.
    """
    funded_by: dict[str, list[str]] = {}
    for p in projects:
        for f in p.get("public_funding") or []:
            if f.get("measure"):
                funded_by.setdefault(f["measure"], []).append(p["id"])

    rows = []
    files = json.loads((sm.ROOT / "sources" / "register_files.json").read_text(encoding="utf-8"))
    for slug in files["files"]:
        path = sm.ROOT / "data" / f"{slug}.json"
        if not path.exists():
            continue
        for r in json.loads(path.read_text(encoding="utf-8")):
            mid = f"{slug}:{r['id']}"
            reach = set(r.get("sectors_reached") or []) | set(r.get("sectors_named") or [])
            if sector in reach:
                rows.append({"file": slug, "row": r, "reach": "register", "via": []})
            elif mid in funded_by:
                rows.append({"file": slug, "row": r, "reach": "funding",
                             "via": sorted(funded_by[mid])})
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
    for entry in register_rows(sector, projects):
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
            "reach": entry["reach"],
            "reached_via": entry["via"],
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
        # Per-tonne first, and only against other per-tonne figures. A stock of
        # grants awarded and a cost per tonne of clinker are both money, and
        # sorting one list by their raw magnitudes would rank €381 000 000 above
        # €1.36 for no reason except that euros are bigger than euros-per-tonne.
        # So the key is (has a rate, the rate), then (has a stock, the stock).
        money = s["money"]
        rate = money["per_tonne"]
        stock = money["value"] if rate is None else None
        return (
            0 if rate is not None else 1,
            -(rate or 0),
            -(stock or 0),
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
        "net": net_position(scored),
        "measures": scored,
    }


def net_position(scored: list[dict]) -> dict:
    """What the measures add up to, netted per bearer and per scale.

    Netting is only ever done inside one (scale, bearer) pair. A euro per tonne
    of clinker charged to a European kiln and a euro of grant paid to a project
    developer do not cancel: they are different units landing on different
    balance sheets, and a single headline number that mixed them would be the
    most confidently wrong figure on the page.

    So the output is a small table rather than a total, and the sector view
    renders it as one. Where a bearer has only costs or only support, that is
    itself the finding.
    """
    buckets: dict[tuple[str, str], dict] = {}
    for s in scored:
        m = s["money"]
        if not m["computable"] or not m["direction"]:
            continue
        rate_scale = "eur_per_tonne" if m["per_tonne"] is not None else m["scale"]
        key = (rate_scale, m["bearer"])
        b = buckets.setdefault(key, {"scale": rate_scale, "bearer": m["bearer"],
                                     "cost": 0.0, "support": 0.0, "measures": []})
        amount = m["per_tonne"] if m["per_tonne"] is not None else m["value"]
        b[m["direction"]] += amount
        b["measures"].append({"measure": s["measure"], "direction": m["direction"],
                              "amount": amount})
    out = []
    for b in sorted(buckets.values(), key=lambda x: (x["scale"], x["bearer"])):
        b["net"] = round(b["support"] - b["cost"], 2)
        b["cost"] = round(b["cost"], 2)
        b["support"] = round(b["support"], 2)
        out.append(b)
    return {
        "_note": ("Netted within one scale and one bearer only. Costs per tonne on an EU "
                  "producer and grants awarded to a developer are different units on "
                  "different balance sheets and are never summed together."),
        "buckets": out,
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
        if money["computable"]:
            rate = (f"€{money['per_tonne']}/t " if money["per_tonne"] is not None else "")
            money_str = (f"{rate}[{money['direction']} → {money['bearer']}] "
                         f"{money['value']:,.0f} {money['scale']}"
                         if money["scale"] != "eur_per_tonne_clinker"
                         else f"€{money['value']}/t clinker [{money['direction']} → {money['bearer']}]")
        else:
            money_str = f"no money ({', '.join(money['missing'])})"
        via = "" if m["reach"] == "register" else f"  (reached via funding: {', '.join(m['reached_via'])})"
        lines.append(f"    {m['rank']}. {m['measure']} — {money_str}"
                     f", linkage {m['bottleneck_linkage']['weight']}{via}")
    lines.append("  net, per scale and bearer (never across):")
    for b in doc["net"]["buckets"]:
        lines.append(f"    {b['bearer']:<18} {b['scale']:<16} "
                     f"cost {b['cost']:>14,.2f}  support {b['support']:>14,.2f}  "
                     f"net {b['net']:>14,.2f}")
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

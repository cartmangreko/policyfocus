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
import datetime as dt
import json
from datetime import date
from pathlib import Path

import number_format as nf
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


# WHICH BENCHMARK THE PHASE-OUT BITES ON, PER SECTOR.
#
# Cement collapses to one product benchmark and steel does not: the free
# allocation a steel site receives is set per tonne of hot metal on the
# integrated route and per tonne of EAF steel on the scrap route, and those are
# benchmarks of DIFFERENT PRODUCTS. They are therefore listed rather than
# summed -- euros per tonne of hot metal plus euros per tonne of EAF steel is
# the unit error `scale` exists to prevent -- and the FIRST route is the one the
# ranking sorts on, with the rest carried as context beside it. That is the
# shape model_cbam_certificates already uses for its two CN lines.
#
# `token` is the benchmark's name inside the formula string and `installation`
# is what the caveat calls the thing that emits, because a caveat that said
# "kiln" on a steel page would be the cement model talking.
FREE_ALLOCATION_ROUTES = {
    "cement": {
        "installation": "kiln",
        "routes": (
            ("clinker", "clinker-benchmark-2026-2030", "eur_per_tonne_clinker",
             "clinker_benchmark"),
        ),
    },
    "steel": {
        "installation": "site",
        "routes": (
            ("hot metal", "hot-metal-benchmark-2026-2030", "eur_per_tonne_hot_metal",
             "hot_metal_benchmark"),
            ("EAF carbon steel", "eaf-carbon-steel-benchmark-2026-2030",
             "eur_per_tonne_eaf_carbon_steel", "eaf_carbon_steel_benchmark"),
        ),
    },
}


def model_free_allocation_phaseout(sector: str, params: dict, year: int) -> dict:
    """Allowances withdrawn x carbon price, per tonne of the sector's product.

    Withdrawn share is (1 - CBAM factor): in 2026 the factor is 97,5 %, so 2,5 %
    of the free allocation an installation would otherwise receive is gone, and it
    buys that fraction of its benchmarked allowances at the market price.

    ONE FIGURE PER ROUTE, NEVER A SUM. See FREE_ALLOCATION_ROUTES above: the
    routes are per tonne of different products, so the model ranks on the first
    and reports the rest, and nothing anywhere adds them together.
    """
    config = FREE_ALLOCATION_ROUTES[sector]
    routes = config["routes"]
    lead_scale = routes[0][2]
    factor = params.get(f"cbam-factor-{year}")
    price = params.get("eua-price-spot")
    needed = ([f"cbam-factor-{year}"] + [r[1] for r in routes] + ["eua-price-spot"])
    missing = [n for n in needed if n not in params]
    formula = f"(1 - cbam_factor) x {routes[0][3]} x eua_price"
    if missing:
        return _money(None, lead_scale, "free_allocation_phaseout",
                      [n for n in needed if n not in missing], formula, missing,
                      direction="cost", bearer="eu_producer")
    withdrawn = 1 - (factor["value"] / 100)
    priced = [(label, scale, round(withdrawn * params[pid]["value"] * price["value"], 2))
              for label, pid, scale, _ in routes]
    value = priced[0][2]
    context = [{"label": f"the same model on {label}", "value": amount, "scale": scale}
               for label, scale, amount in priced[1:]]
    return _money(value, lead_scale, "free_allocation_phaseout",
                  needed, formula, direction="cost", bearer="eu_producer",
                  per_tonne=value, context=context,
                  caveats=[
                      "The figure is the cost of the WITHDRAWN benchmark allocation, not the full "
                      f"carbon cost of a plant: a {config['installation']} emitting above the "
                      "benchmark pays for its excess on top of this, and always did.",
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


# What a euro parameter is denominated in. Explicit and closed: a funding row
# names the sourced parameter rather than restating its number, so the code has
# to do the conversion, and a conversion inferred from a string it has never
# seen is how a €191 million grant becomes €191.
EUR_UNITS = {
    "EUR": 1,
    "EUR million": 1_000_000,
    "EUR billion": 1_000_000_000,
}


def _eur(param: dict | None) -> float | None:
    """A sourced amount in euros, or None. Raises on a unit nobody has ruled on."""
    if not param:
        return None
    scale = EUR_UNITS.get(param["unit"])
    if scale is None:
        raise SystemExit(
            f"build_importance: parameter {param['id']!r} is a funding amount in "
            f"{param['unit']!r}, which is not in EUR_UNITS {list(EUR_UNITS)} — add the "
            f"unit deliberately rather than letting the total be wrong by a factor of a "
            f"million"
        )
    return float(param["value"]) * scale


def model_grant_programme(measure_id: str, funding: list[dict], params: dict,
                          project_ids: set[str]) -> dict:
    """Public money awarded to this sector's projects UNDER THIS MEASURE.

    A funding line counts only where it names a register measure, and the notes
    on those lines are part of the result: the Innovation Fund awards below were
    made under the Fund as it stands, while the register knows the Fund through
    the ETS revision's Art. 10cb. The total is real money into real plants either
    way, which is why it is counted, and the caveat travels with it.

    This is a STOCK, not a rate: grants awarded to date, not euros per year and
    not euros per tonne. It therefore never competes with a per-tonne figure in
    the ranking, and the sector view nets it separately or not at all.

    ONLY COMMITTED MONEY IS IN THE TOTAL. The scale is called eur_awarded, so it
    may hold approved, signed and disbursed lines and nothing else
    (sm.FUNDING_COMMITTED). An announcement is not an award and a withdrawal is
    not money; both are counted, named in the caveats, and left out of the sum.
    Today every cement line is approved, so this changes no number — which is
    the point of doing it before the watch channel starts writing announcements.
    """
    total = 0
    contributing = []
    caveats = []
    unpriced = 0
    announced = 0
    withdrawn = 0
    for f in funding:
        if f.get("under") != measure_id:
            continue
        # Money that lands outside this sector's projects is somebody else's
        # fact. The funding node is shared across sectors by design, so the
        # filter is here rather than in the loader.
        if not any(n.split(":", 1)[1] in project_ids for n in f.get("finances", [])):
            continue
        status = f.get("status")
        if status in sm.FUNDING_EXCLUDED:
            withdrawn += 1
            continue
        if status in sm.FUNDING_ANNOUNCED:
            announced += 1
            continue
        amount = _eur(params.get(f["amount"])) if f.get("amount") else None
        if amount:
            total += amount
            contributing.append(f["id"])
        else:
            unpriced += 1
        if f.get("under_note") and f["under_note"] not in caveats:
            caveats.append(f["under_note"])
    formula = ("sum of funding.amount where funding.under = this measure "
               "and funding.status is committed (approved, signed, disbursed)")
    if not contributing:
        why = ["no funding row names this measure as its legal basis"]
        if announced or withdrawn:
            why = [f"no committed funding under this measure: {announced} announced, "
                   f"{withdrawn} withdrawn"]
        return _money(None, "eur_awarded", "grant_programme", [], formula,
                      why,
                      direction="support", bearer="project_developer")
    if unpriced:
        caveats.append(f"{unpriced} further funding line(s) under this measure carry no published "
                       f"amount and are not in the total, which is therefore a floor.")
    if announced:
        caveats.append(f"{announced} announced funding line(s) under this measure are not in the "
                       f"total: an announcement is not an award.")
    if withdrawn:
        caveats.append(f"{withdrawn} withdrawn funding line(s) under this measure are not in the "
                       f"total.")
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
# KEYED ON (SECTOR, MEASURE), NOT ON THE MEASURE ALONE.
#
# It was keyed on the measure, and that was a sector-level figure wearing a
# measure-level key: ets:CBAM-01 reaches cement and steel, and a lookup that
# could not tell them apart would have priced a steel site at the cement
# clinker benchmark and put the answer on the steel page. The models themselves
# were never the problem -- grant_programme already filters on the sector's own
# projects -- so this is the key doing the work the key was always meant to do.
#
# ("cement", "ets:CBAM-02") is deliberately absent. It phases out free allocation
# for product categories ADDED to the CBAM list later, on the same schedule --
# pricing it at the cement clinker benchmark today would double-count the same
# euro against cement and rank a measure about future goods second in a cement
# view.
#
# Only ONE of the CBAM rows carries the certificate model. The obligation to hold
# and surrender certificates is what costs money; the reporting and verification
# rows around it are how that obligation is administered, and pricing each of
# them at the full certificate bill would state the same euro four times.
#
# ("steel", "cbam:FIN-03") is absent and is not an oversight: steel is the
# largest CBAM sector by trade volume and the certificate model matters more
# there than it does for cement, but it needs the CN lines of chapters 72-73 and
# their import volumes sourced, which is a research task of its own. Tracked as
# its own issue; until then steel's import-side carbon cost is a stated gap
# rather than a number nobody sourced.
MODELS = {
    ("cement", "ets:CBAM-01"): "free_allocation_phaseout",
    ("cement", "ets:FND-03"): "grant_programme",
    ("cement", "cbam:FIN-03"): "cbam_certificates",
    ("steel", "ets:CBAM-01"): "free_allocation_phaseout",
    ("steel", "ets:FND-03"): "grant_programme",
}


def money_for(sector: str, measure_id: str, params: dict, funding: list[dict],
              project_ids: set[str], year: int) -> dict:
    model = MODELS.get((sector, measure_id))
    if model == "free_allocation_phaseout":
        score = model_free_allocation_phaseout(sector, params, year)
        later = model_free_allocation_phaseout(sector, params, 2030)
        if later["computable"]:
            score["context"] = score["context"] + [{
                "label": "the same model at 2030",
                "value": later["value"],
                "scale": later["scale"],
            }]
        return score
    if model == "cbam_certificates":
        return model_cbam_certificates(params, year)
    if model == "grant_programme":
        return model_grant_programme(measure_id, funding, params, project_ids)
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


def register_rows(sector: str, funding: list[dict], project_ids: set[str]) -> list[dict]:
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
    for f in funding:
        if not f.get("under"):
            continue
        for node in f.get("finances", []):
            pid = node.split(":", 1)[1]
            if pid in project_ids:
                funded_by.setdefault(f["under"], []).append(pid)

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


def mid_in_labels(scored_row: dict) -> bool:
    return scored_row["measure"] in sm.measure_labels()


def build(sector: str, year: int) -> dict:
    params = sm.index(sm.load("parameter"))
    bottlenecks = sm.load("bottleneck")
    projects = [p for p in sm.load("project") if p["sector"] == sector]
    project_ids = {p["id"] for p in projects}
    funding = sm.load("funding")
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

    # The authored plain block per measure — what it requires or grants, in a
    # title and one sentence, with its figures slotted in here. Brief 4 §5: the
    # key-measures list is read by somebody who has not read the act, and
    # neither `duty` (the decoded provision) nor the diagram's 26-character
    # label is written for them.
    labels = sm.measure_labels()

    scored = []
    for entry in register_rows(sector, funding, project_ids):
        slug, row = entry["file"], entry["row"]
        mid = f"{slug}:{row['id']}"
        money = money_for(sector, mid, params, funding, project_ids, year)
        edges = linkage.get(mid, [])
        weight_sum = round(sum(e["weight"] for e in edges), 3)
        # The same predicate as `in_sector_view` below, needed here because the
        # plain block is only ever rendered by the key-measures list and the
        # key-measures list is that predicate. Kept as one expression in two
        # places rather than two rules: see the assertion after the loop.
        in_view = bool((money["value"] or 0) > 0 or weight_sum > 0)
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
            # Absent for a measure this sector does not list. A label is shared
            # across every sector a measure reaches and the words under it are
            # not, so asking for a sector's wording on a measure that sector
            # never shows would demand prose for a page that does not exist.
            # The gate requires one for every measure a sector DOES list.
            "plain": (sm.plain_measure(labels[mid], money, sector)
                      if in_view and mid in labels else None),
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
        # The two places that compute this predicate must agree, or a measure
        # gets its words from one rule and its place on the page from another.
        if s["in_sector_view"] and mid_in_labels(s) and s["plain"] is None:
            raise SystemExit(
                f"build_importance: {s['measure']} is in the {s.get('sector', '')} sector "
                f"view with a label and no plain block — the two readings of "
                f"in_sector_view have drifted apart"
            )
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
            rate = (f"{nf.money_rate(money['per_tonne'], compact=True)} "
                    if money["per_tonne"] is not None else "")
            money_str = (f"{rate}[{money['direction']} → {money['bearer']}] "
                         f"{money['value']:,.0f} {money['scale']}"
                         if money["scale"] != "eur_per_tonne_clinker"
                         else f"{nf.money_rate(money['value'], compact=True)} clinker "
                              f"[{money['direction']} → {money['bearer']}]")
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


HOLDS = sm.DATA / "draw_holds.json"


def hold_on_first_ranking(sector: str) -> str:
    """Record a draw hold for a sector that has just got its first ranking.

    Returns a line for the build log. Does nothing if the sector is already
    held or has been explicitly released — a release is a decision somebody
    made, and re-holding a released sector on the next rebuild would undo it
    silently.
    """
    doc = json.loads(HOLDS.read_text(encoding="utf-8")) if HOLDS.exists() else {
        "holds": {}, "released": {}}
    doc.setdefault("holds", {})
    doc.setdefault("released", {})
    if sector in doc["holds"]:
        return "already held"
    if sector in doc["released"]:
        return "previously released; not re-held"
    doc["holds"][sector] = {
        "since": dt.date.today().isoformat(),
        "reason": (f"Placed automatically when {sector} first got a ranking. A ranking is what "
                   f"turns hasMap true, so without this the sector's page would begin drawing a "
                   f"Europe-wide overview on whatever rows happen to exist. Nobody has judged "
                   f"whether they are enough."),
        "released_by": "George, on an explicit judgement that the data is complete enough to draw.",
    }
    HOLDS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "hold written to data/transition/draw_holds.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="rebuild and diff against what is committed; write nothing")
    ap.add_argument("--sector", action="append", default=None)
    ap.add_argument("--year", type=int, default=date.today().year)
    args = ap.parse_args()

    sectors = args.sector or sm.mapped_sectors()
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
            # A SECTOR IS HELD FROM DRAWING THE MOMENT IT FIRST HAS A RANKING.
            # `hasMap` turns true the instant this file exists, so a sector's
            # page goes from a directory template to a full page with a
            # Europe-wide overview on it as a side effect of running a builder.
            # Batteries did exactly that, and the picture it would have drawn was
            # short of a third of the sector.
            #
            # So the hold is placed HERE, before the first render, and it is
            # placed automatically because the one time it mattered nobody
            # thought to place it. It is never lifted here: releasing is a
            # judgement about whether the data is honest enough to publish, and a
            # builder is not entitled to make it.
            first_time = not path.exists()
            path.write_text(text, encoding="utf-8")
            if first_time:
                held = hold_on_first_ranking(sector)
                print(f"build_importance: {sector} is HELD FROM DRAWING — {held}")
            print(f"build_importance: wrote {path} — "
                  f"{sum(1 for m in doc['measures'] if m['in_sector_view'])} of "
                  f"{len(doc['measures'])} measures in the sector view")
        print("\n".join(sanity_report(doc)))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

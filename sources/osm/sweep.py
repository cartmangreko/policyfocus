"""A coordinate sweep against a cached layer built from a dated Geofabrik extract.

    python3 sources/osm/sweep.py <layer.json> <place name> <radius_m> [target ...]

WHAT A SWEEP ANSWERS is not "is anything drawn here" but "is anything drawn here that is
THE WORKS". The targets are the names the owner or the permit uses, and `target_hits` is
the finding; everything else in the record is context.

THE CENTRE COMES FROM THE LAYER'S OWN PLACE NODES and is never written down. Never a
geocoder — a geocoding service returns a third party's coordinate, which this register has
refused as a position since the perimeter was written, and calling it a search hint would
launder the refusal. The centre is scaffolding, discarded when the search ends; what is
recorded is the NAME of the place matched, so a reader can see where the search pointed.

NOTHING IS TRUNCATED. The named lists are returned whole. They were cut at twelve
alphabetically until 12 September 2026, which made a works whose name sorts late — Tata
Steel, Sniace — indistinguishable from a works nobody had drawn, and every miss measured
that way was void (D76).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import layer as osm_layer  # noqa: E402

ESTATE_WORDS = ("industriegebiet", "gewerbe", "industrial estate", "industrial park",
                "polígono", "poligono", "zona industrial", "parque", "hafen", "port ",
                "puerto", "industripark", "zone industrielle", "bedrijventerrein",
                "zone d'activités", "zone d'activites", "teollisuusalue",
                # ADDED 13 SEPTEMBER 2026: "Energie- und Technologiepark Lubmin" is the
                # estate occupying the decommissioned nuclear station's ground, and it was
                # being offered as a host works because none of the words above appear in
                # it. A park by any of its national names is an estate.
                "technologiepark", "technology park", "business park", "science park",
                "energiepark", "erhvervspark", "næringspark", "naringspark")
# WHAT MAY BE A HOST WORKS, by tag and not by name. `industrial` is the landuse of works
# ground; `works` is man_made=works. Everything else the layer keeps — substations, power
# plants, construction sites, pumping stations, street cabinets — may be NEAR a works, may
# be named after one, and is not one. `plant` is excluded deliberately: a power station is
# a works for its own purposes, and where a hydrogen project stands on one the row says so
# through a named target, not through a tag that also matches every solar farm.
HOST_WORKS_TAGS = ("industrial", "works")

PLACE_RANK = {"city": 0, "town": 1, "suburb": 2, "village": 3, "quarter": 4,
              "neighbourhood": 5, "hamlet": 6, "locality": 7, "isolated_dwelling": 8}


def metres(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def centre(doc: dict, names: set[str]):
    """Every place node whose name is one of `names`. THE CALLER DECIDES, AND MAY NOT GUESS.

    An earlier version returned the highest-ranked single match and the caller passed it a
    set that included fallbacks — the owner's place plus its parent city plus the village
    the benchmark's coordinate fell in. It silently centred Europoort on ROTTERDAM CITY
    CENTRE, twenty kilometres away, and Eemshaven on Pieterburen, and both returned lists
    of real named industry that would have been recorded as the works not being drawn.
    That is the truncation defect wearing different clothes: a wrong answer shaped like a
    right one.

    So this returns all of them and the three outcomes are kept apart by the caller:

        one match    sweep it
        no match     NOT SWEPT — the owner-named place is not a place node in this
                     extract, which is a fact about the basemap and not a miss
        many         NOT SWEPT — ambiguous. Brandenburg has three villages called
                     Falkenhagen; picking one is a guess, and a guess here produces a
                     finding about somewhere else.
    """
    return [(PLACE_RANK.get(p["k"], 9), p["n"], p["k"], p["lat"], p["lon"])
            for p in doc["places"] if p["n"].casefold() in names]


def sweep(doc: dict, lat: float, lon: float, radius: int,
          targets: list[str] | None = None) -> dict:
    works, estates, host_works, parcels = [], [], [], 0
    box = radius / 111320.0 * 1.6
    for f in doc["industrial"]:
        if abs(f["lat"] - lat) > box or abs(f["lon"] - lon) > box:
            continue
        if metres(lat, lon, f["lat"], f["lon"]) > radius:
            continue
        name = f.get("n")
        if not name:
            parcels += 1
            continue
        label = f"{name} [{f['t']}]"
        low = name.casefold()
        is_estate = any(w in low for w in ESTATE_WORDS)
        (estates if is_estate else works).append(label)
        if f["t"] in HOST_WORKS_TAGS and not is_estate:
            host_works.append(label)

    named_works, named_estates = sorted(set(works)), sorted(set(estates))
    out = {"basemap_date": doc["basemap_date"], "extract": doc["extract"],
           "radius_m": radius,
           "verdict": "works" if works else "estate" if estates
                      else "parcel" if parcels else "none",
           "named_works": named_works, "named_estates": named_estates,
           "host_works_candidates": sorted(set(host_works)),
           "named_count": len(named_works) + len(named_estates),
           "unnamed_industrial_parcels": parcels}
    if targets:
        # A NAME MATCH ON THE WRONG KIND OF FEATURE IS NOT A HOST WORKS. Ruled 13
        # September 2026 after five of nine answered sweeps matched a substation or a
        # railway carrying a works's name: two substations called "Zeeland refinery", the
        # 400 kV substation at Idomlund, SNIACE's cogeneration substation, and "Obras tren
        # a Punta Langosteira", which is the railway being built TO the port. Pembroke
        # produced nine street cabinets with the word Substation in them.
        #
        # A works is industrial GROUND or a works feature. The electricity that leaves it
        # and the railway that reaches it are named after it and are not it.
        hits = {t: [n for n in host_works if t.casefold() in n.casefold()] for t in targets}
        out["target_hits"] = {k: v for k, v in hits.items() if v}
        out["target_found"] = any(hits.values())
        # Kept apart rather than discarded: a name match on an ancillary is evidence the
        # works is THERE, and it is not evidence of where its ground is.
        named_by = {t: [n for n in named_works + named_estates
                        if t.casefold() in n.casefold() and n not in host_works]
                    for t in targets}
        out["named_after_but_not_the_works"] = {k: v for k, v in named_by.items() if v}
    return out


if __name__ == "__main__":
    doc = osm_layer.load(Path(sys.argv[1]))
    cs = centre(doc, {sys.argv[2].casefold()})
    if len(cs) != 1:
        raise SystemExit(f"{len(cs)} place nodes named {sys.argv[2]!r} in {doc['extract']} "
                         f"— one is required; none means the place is not in the basemap "
                         f"and several means picking one would be a guess")
    _, pname, pkind, la, lo = cs[0]
    res = sweep(doc, la, lo, int(sys.argv[3]), sys.argv[4:] or None)
    res["centre_place"] = f"{pname} ({pkind})"
    print(json.dumps(res, ensure_ascii=False, indent=1))

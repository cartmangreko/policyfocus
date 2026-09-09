#!/usr/bin/env python3
"""Every European entry at or above 100 MW in the two benchmark lists that this
register does NOT hold, classified — and the residue named so it can be worked.

WHY A SECOND SCRIPT AND NOT A COLUMN IN THE FIRST. build_hydrogen_benchmark.py
answers "what does this register hold, and how does each row compare". This one
answers the opposite question, which is the one a reader distrusts a register
over: what do the outside lists hold that you do not, and is each absence a
decision or an oversight. Those are different populations — the first is over
twenty rows, this is over four hundred and ninety-two entries — and a column
that tried to be both would be a column nobody could total.

THE POPULATION IS WIDER HERE, DELIBERATELY. The first script counts electrolysis
only, because that is the perimeter. This one counts EVERY technology at or above
the threshold, because `blue` is one of the classes and a population that excluded
fossil-with-capture could never report how much of it there is.

THE SIX CLASSES, IN THE ORDER THEY ARE TESTED. First match wins, and the order is
the argument: an entry is excluded by the perimeter before it is judged on its
stage, and it is judged a duplicate before either, because a phase of a site this
register already holds is not a gap at all.

  duplicate of a held row     another phase of a site with a eufabric row. Both
                              lists count phases where this register counts
                              sites, so RWE's Lingen works is three entries there
                              and one here.
  DRI or other perimeter
  exclusion                   a steel project making its own hydrogen, a fuel
                              works whose electrolyser is not separately stated,
                              or electrolyser manufacture. Refused by a stated
                              clause of the perimeter.
  blue                        methane reforming with capture. Out of THIS dataset
                              and listed rather than refused, because whether it
                              belongs is a ruling nobody has made.
  below threshold on reading  the benchmark's own `Announced Size` — the figure
                              as the project stated it — is below 100 MW, and the
                              entry only clears the threshold through the IEA's
                              normalisation. Reading the company gets a different
                              answer from reading the column.
  no company-confirmed site   the entry is a concept or a feasibility study. The
                              perimeter admits a site a company has confirmed, and
                              a feasibility study is a company saying it might.
  not searched                everything else: an entry at FID, in construction or
                              operating that none of the above explains. THIS IS
                              THE ONLY CLASS THAT IS A DEFECT, and it is printed
                              by name rather than counted, because the answer to
                              it is to go and look.

    python3 report_benchmark_gap.py        # the table, and the residue by name
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import sector_map as sm  # noqa: E402

OUT = bench.ROOT / "scratch" / "hydrogen_benchmark_gap.csv"

CLASSES = ("duplicate of a held row", "DRI or other perimeter exclusion", "blue",
           "below threshold on reading", "no company-confirmed site", "not searched")

STEEL = re.compile(r"steel|hybrit|stegra|h2gs|\bdri\b|sponge iron|salcos|gravithy|blastr"
                   r"|iron\s*&|ironmaking|thyssenkrupp|arcelor", re.I)
FUEL = re.compile(r"e-?saf\b|\bsaf\b|methanol|meoh|e-?fuel|synfuel|kerosen|\bjet\b|biofuel"
                  r"|e-?methan|ptl\b|ammonia plant|fertig", re.I)
MAKER = re.compile(r"gigafactory|electroly[sz]er (?:factory|plant|manufactur)|stack factory", re.I)
BLUE = re.compile(r"\bblue\b|\bsmr\b|\batr\b|reform", re.I)

# ENTRIES REFUSED ONE AT A TIME, BY NAME, WITH THE CLAUSE THAT REFUSED THEM.
# The same device the coordinate-source exceptions use, for the same reason: the
# residue this report produces is the only class that is a defect, and an entry
# that leaves it should leave by somebody deciding rather than by a regex
# widening. Every entry here is printed on every run.
#
# Keyed on (benchmark, ref) so the two lists cannot be confused: reference
# numbers were reassigned between the vintages, and 1877 means two different
# projects in the two files.
REFUSED_BY_NAME = {
    ("odenweller_ueckerdt_2025", "580"): (
        "Centurion — a FEASIBILITY STUDY, and one about storage rather than about "
        "producing hydrogen for a works. Innovate UK financed it in 2018 to 'explore the "
        "electrolytic production, pipeline transmission, salt cavern storage and gas grid "
        "injection of green hydrogen at an industrial scale', testing ITM Power's PEM "
        "electrolyser at INOVYN's Runcorn site. Two clauses of the perimeter refuse it "
        "independently: no company statement confirms a project, only a study of one; and "
        "its object is grid injection and cavern storage, which this perimeter puts "
        "outside as dependency nodes. The benchmark carries it with status "
        "'Other/Unknown', which is what a list looks like when it has stopped following "
        "a study that ended."),
}

# The announced size as the project stated it. "100 MW" and "1GW" clear the
# threshold; "50MW", "22 MW" and a figure quoted only in tonnes or Nm3 do not.
MW = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:MW|MWel|MW el)", re.I)
GW = re.compile(r"(\d+(?:[.,]\d+)?)\s*GW", re.I)


def stated_mw(text: str) -> float | None:
    """The largest megawatt figure the benchmark records the project as stating,
    or None where it states none — a project quoted only in tonnes of methanol
    has no electrolyser rating in this column at all."""
    if not text:
        return None
    best = None
    for m in GW.finditer(text):
        best = max(best or 0, float(m.group(1).replace(",", ".")) * 1000)
    for m in MW.finditer(text):
        best = max(best or 0, float(m.group(1).replace(",", ".")))
    return best


def stem(name: str) -> str:
    """A project name with its phase suffix removed, so the phases of one site
    group together. Deliberately blunt: it exists to find SIBLINGS of a held row
    and a false grouping shows up as a duplicate that names a different site."""
    s = (name or "").lower()
    s = re.sub(r"[-–—,(]?\s*(phase|fase|stage|tranche)\s*[ivx0-9]+.*$", "", s)
    s = re.sub(r"[-–—,(]?\s*(completion|final|expansion|extension|future phases)\b.*$", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def classify(entry: dict, name: str, status: str, tech: str, size: str,
             held_stems: set[str], key: tuple[str, str] | None = None) -> str:
    if key in REFUSED_BY_NAME:
        return "DRI or other perimeter exclusion"
    if stem(name) in held_stems:
        return "duplicate of a held row"
    if STEEL.search(name) or MAKER.search(name):
        return "DRI or other perimeter exclusion"
    if "ccus" in tech.lower() or "fossil" in tech.lower() or BLUE.search(name):
        return "blue"
    if FUEL.search(name):
        return "DRI or other perimeter exclusion"
    mw = stated_mw(size)
    if size and (mw is None or mw < 100):
        return "below threshold on reading"
    if status in ("Concept", "Feasibility study"):
        return "no company-confirmed site"
    return "not searched"


def main() -> int:
    ou_all, iea_all = bench.load_ou(), bench.load_iea()
    rows = bench.held()

    def f(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    ou = {str(r["Ref"]): r for r in ou_all
          if r.get("Country") in bench.GEO and (f(r.get("Capacity_MWel")) or 0) >= 100}
    iea = {str(r["projectReference"]): r for r in iea_all
           if r["country"]["iso3"] in bench.GEO
           and (f(r.get("capacity (ktH2Y)")) or 0) >= bench.THRESHOLD_KT}

    held_ou, held_iea = set(), set()
    for r in rows:
        held_ou.update(str(x) for x in bench.as_list(
            r["benchmarks"].get("odenweller_ueckerdt_2025")))
        held_iea.update(str(x) for x in bench.as_list(
            r["benchmarks"].get("iea_hydrogen_production_projects")))

    # The stems of every entry a eufabric row matches, in either list. A phase of
    # one of those is a duplicate wherever it appears.
    held_stems = {stem(ou[i]["Project name"]) for i in held_ou if i in ou}
    held_stems |= {stem(iea[i]["projectName"]) for i in held_iea if i in iea}
    held_stems.discard("")

    out, counts = [], {"odenweller_ueckerdt_2025": Counter(),
                       "iea_hydrogen_production_projects": Counter()}
    for i, r in sorted(ou.items(), key=lambda kv: int(kv[0])):
        if i in held_ou:
            continue
        c = classify(r, str(r["Project name"]), str(r["Status"]),
                     str(r.get("Technology") or ""), str(r.get("Announced Size") or ""),
                     held_stems, ("odenweller_ueckerdt_2025", i))
        counts["odenweller_ueckerdt_2025"][c] += 1
        out.append({"benchmark": "odenweller_ueckerdt_2025", "ref": i,
                    "country": r["Country"], "name": r["Project name"],
                    "status": r["Status"], "technology": r.get("Technology"),
                    "announced_size": r.get("Announced Size"),
                    "normalised_mwel": f(r.get("Capacity_MWel")), "class": c})
    for i, r in sorted(iea.items(), key=lambda kv: int(kv[0])):
        if i in held_iea:
            continue
        c = classify(r, str(r["projectName"]), str(r["status"]), str(r.get("technolgy") or ""),
                     str((ou.get(i) or {}).get("Announced Size") or ""), held_stems,
                     ("iea_hydrogen_production_projects", i))
        counts["iea_hydrogen_production_projects"][c] += 1
        out.append({"benchmark": "iea_hydrogen_production_projects", "ref": i,
                    "country": r["country"]["iso3"], "name": r["projectName"],
                    "status": r["status"], "technology": r.get("technolgy"),
                    "announced_size": (ou.get(i) or {}).get("Announced Size"),
                    "normalised_mwel": round((f(r.get("capacity (ktH2Y)")) or 0)
                                             / bench.IEA_KT_PER_MW), "class": c})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    print(f"report_benchmark_gap: {len(ou)} O&U and {len(iea)} IEA European entries at or "
          f"above 100 MW; eufabric holds {len(held_ou & set(ou))} and "
          f"{len(held_iea & set(iea))}.\n")
    print(f"| {'class':32} | {'O&U':>5} | {'IEA':>5} |")
    print(f"|{'-' * 34}|{'-' * 7}|{'-' * 7}|")
    for c in CLASSES:
        print(f"| {c:32} | {counts['odenweller_ueckerdt_2025'][c]:5} | "
              f"{counts['iea_hydrogen_production_projects'][c]:5} |")
    print(f"| {'held by eufabric':32} | {len(held_ou & set(ou)):5} | "
          f"{len(held_iea & set(iea)):5} |")
    print(f"| {'TOTAL':32} | {len(ou):5} | {len(iea):5} |")

    residue = [r for r in out if r["class"] == "not searched"]
    if residue:
        print(f"\nNOT SEARCHED ({len(residue)}) — the only class that is a defect. Each of "
              f"these is at FID, in construction or operating, in the geography, above the "
              f"threshold, and neither held nor explained:")
        for r in residue:
            print(f"  {r['benchmark'][:4]:4} ref {r['ref']:>5}  {r['country']}  "
                  f"{r['normalised_mwel'] or '?':>6} MW  {r['status'][:18]:18} {r['name'][:58]}")
    else:
        print("\nNOT SEARCHED (0) — every absence is a decision.")
    print(f"\nrefused by name ({len(REFUSED_BY_NAME)}) — recorded, never silent:")
    for (b, ref), why in sorted(REFUSED_BY_NAME.items()):
        print(f"  {b[:4]} ref {ref}: {why}")

    print(f"\n  {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

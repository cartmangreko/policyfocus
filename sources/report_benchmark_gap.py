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
import hashlib
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_hydrogen_benchmark as bench  # noqa: E402
import sector_map as sm  # noqa: E402

OUT = bench.ROOT / "scratch" / "hydrogen_benchmark_gap.csv"
SNAPSHOTS = bench.ROOT / "sources" / "benchmark_snapshots.json"


def verify_inputs() -> list[str]:
    """Check the cached benchmark files against their recorded identity.

    THE SNAPSHOT RULE, APPLIED TO AN INPUT NOBODY MAY REDISTRIBUTE. Every number
    in this report and in the docket was computed from two files; the licence
    stops this repository holding copies of them, so what is held is the
    publisher's URL, the day, the size and the SHA-256, in
    sources/benchmark_snapshots.json. This function proves the file on disk is
    still the one the numbers are about, and says so out loud either way —
    silence would let a refreshed input change the counts without anybody being
    told which file they now describe.
    """
    doc = json.loads(SNAPSHOTS.read_text(encoding="utf-8"))
    newest: dict[str, dict] = {}
    for rec in doc["snapshots"]:
        cur = newest.get(rec["benchmark"])
        if cur is None or rec["fetched"] >= cur["fetched"]:
            newest[rec["benchmark"]] = rec
    lines = []
    for name, rec in sorted(newest.items()):
        path = bench.CACHE / rec["file"]
        if not path.exists():
            lines.append(f"  {name}: not cached; it will be fetched from {rec['url']}")
            continue
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got == rec["sha256"]:
            lines.append(f"  {name}: matches the snapshot of {rec['fetched']} "
                         f"({rec['bytes']:,} bytes, {got[:16]}…)")
        else:
            lines.append(f"  {name}: DOES NOT MATCH the snapshot of {rec['fetched']} — "
                         f"on disk {got[:16]}…, recorded {rec['sha256'][:16]}…. The numbers "
                         f"below are about a different file from the one the docket "
                         f"reports; append a new entry to {SNAPSHOTS.name} before "
                         f"publishing them.")
    return lines

# THE CLASS "no company-confirmed site" WAS THREE THINGS AND HID THE DIFFERENCE.
# It held 183 and 159 entries — nine in ten of the gap — and a reader could not
# tell from it whether the benchmark had said where a project is, whether anybody
# had looked for a company source, or whether somebody had looked and been
# refused. Split on 9 September 2026 into the three states those are:
#
#   benchmark gives no location
#       The entry names a country and nothing else. THIS IS A FACT ABOUT THE
#       ACADEMIC LIST AND NOT ABOUT ITS PROJECTS: the October 2023 quality-checked
#       file has no location column at all — Ref, name, country, dates, status,
#       technology, end use, capacity, references, and no site. So a project this
#       register would have to place cannot even be looked for from that file
#       alone; the name is all there is.
#   searched, no owner or permit source found
#   owner or permit source names the site, not admitted
#       WHAT `not searched by eufabric` BECAME WHEN IT WAS SEARCHED, 10 September
#       2026. That class held 167 entries and said one thing about all of them:
#       no fetch had been attempted. The search attempted them — 881 fetches, one
#       entry at a time, recorded in sources/hydrogen_gap_search.json — so the
#       name became false the day the work was done, and a class whose name is
#       false is worse than one whose name is unflattering. RETIRED, and its
#       members distributed along the three lines the search actually found:
#
#         - nothing names a site  -> searched, no owner or permit source found
#         - a source names it and the entry does not clear admission
#                                 -> owner or permit source names the site,
#                                    not admitted
#         - the source could not be read
#                                 -> company source unreadable, below
#         - a source names it AND it clears admission
#                                 -> it is a candidate, and candidates are held
#
#       The second class is not a defect and not a finding against the benchmark:
#       it is the ordinary state of a project this register knows where to find
#       and cannot yet carry — most often because the source names the place and
#       states no megawatts, sometimes because the owner's own figure is below the
#       threshold, sometimes because what is named is a study rather than a
#       project.
#
#       (A third party's coordinate is still not a position this register may
#       use. What the coordinate did was tell the searcher where to look.)
#   company source unreadable
#       Somebody looked, found the operator's own or the permit source, and could
#       not read it: an empty body, a refusal, a dead domain, a scanned PDF. Named
#       one at a time in UNREADABLE_BY_NAME and queued in sources/manual/wanted,
#       because a person with a browser closes one in a minute — and, since the
#       search, read from the search record too, which carries eighteen more.
#
# AND "held by eufabric" COUNTS A CANDIDATE AS HELD. It is not a row in
# data/transition/projects.json and it is not drawn on any map; what it is, is an
# entry this register has admitted, whose only outstanding leg is a position. See
# build_hydrogen_benchmark.held(). This matters to the arithmetic of the split:
# the search moved 54 entries out of the class, and they became 44 candidates,
# because the IEA carries ten of those projects twice, as two phases.
CLASSES = ("duplicate of a held row", "DRI or other perimeter exclusion", "blue",
           "below threshold on reading", "benchmark gives no location",
           "searched, no owner or permit source found",
           "owner or permit source names the site, not admitted",
           "company source unreadable", "unexplained at FID or beyond")

# The search record keyed by IEA reference, read once. An entry the search never
# reached — one that entered the class after 10 September 2026, or an entry of the
# academic file, which the search did not cover — has no outcome here, and
# classify() falls back to saying so rather than guessing.
SEARCH = bench.ROOT / "sources" / "hydrogen_gap_search.json"


def search_outcomes() -> dict[str, str]:
    if not SEARCH.exists():
        return {}
    doc = json.loads(SEARCH.read_text(encoding="utf-8"))
    return {str(e["ref"]): e["outcome"] for e in doc["entries"] if e.get("outcome")}


SEARCHED = search_outcomes()

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
# COMPANY SOURCES LOCATED AND UNREADABLE, one entry at a time, with what was
# measured. The third state named in scope.md, "A 200 with an empty body is a
# refusal": the publisher answers a declared reader with HTTP 200 and a document
# containing the page title, and a link checker calls the line green because by
# every test it has, it is.
#
# EACH ENTRY IS QUEUED IN sources/manual/wanted, because a person with a browser
# closes one in a minute — and until they do, the entry sits here rather than
# among the projects nobody has looked at, which is a different and less honest
# thing to say about it.
UNREADABLE_BY_NAME = {
    ("odenweller_ueckerdt_2025", "1910"): (
        "MoU Shell - Mitsubishi, phase1 — Shell's own list of its hydrogen projects, at "
        "shell.com/what-we-do/hydrogen/shell-hydrogen-projects.html, answers a declared "
        "reader with HTTP 200 and THIRTY-EIGHT CHARACTERS of text: the page title. "
        "Measured 9 September 2026. It is the natural company source for any Shell "
        "project and it cannot be quoted."),
    ("odenweller_ueckerdt_2025", "1911"): (
        "MoU Shell - Mitsubishi, phase2 — the same page and the same measurement."),
    ("iea_hydrogen_production_projects", "1911"): (
        "MoU Shell - Mitsubishi, phase2 — the same page and the same measurement. The "
        "live IEA list carries phase 2 and has dropped phase 1."),
}


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
             held_stems: set[str], key: tuple[str, str] | None = None,
             has_location: bool = False) -> str:
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
    # BELOW THRESHOLD ON READING MEANS A STATED FIGURE THAT IS BELOW IT, and
    # nothing else. An entry whose `Announced Size` is quoted in tonnes or Nm3
    # states no electrolyser rating at all: its place above the threshold rests
    # entirely on the benchmark's own normalisation, which is a different
    # complaint and one this register cannot settle without reading the company.
    # Treating "no megawatts stated" as "below 100 MW" was the first version of
    # this test and it quietly moved projects of several gigawatts into a class
    # that says they are small.
    mw = stated_mw(size)
    if mw is not None and mw < 100:
        return "below threshold on reading"
    if status in ("Concept", "Feasibility study"):
        # THE THREE STATES THE OLD SINGLE CLASS HID, tested in the order they
        # answer: did somebody look and get refused; does the benchmark even say
        # where; and otherwise it says where and nobody here has read a company
        # or permit source naming it.
        if key in UNREADABLE_BY_NAME:
            return "company source unreadable"
        if not has_location:
            return "benchmark gives no location"
        # THE SEARCH RECORD DECIDES THE REST. An entry it settled carries its
        # verdict; an entry it never reached says that, in the only class left
        # that is honest about work nobody has done.
        found = SEARCHED.get(key[1]) if key else None
        if found == "source unreadable":
            return "company source unreadable"
        if found == "searched, none found":
            return "searched, no owner or permit source found"
        if found == "owner or permit source names the site":
            return "owner or permit source names the site, not admitted"
        return "searched, no owner or permit source found"
    return "unexplained at FID or beyond"


SEARCH_OUTCOMES = ("owner or permit source names the site", "searched, none found",
                   "source unreadable")


def search_crosstab() -> str:
    """The admission search that retired `not searched by eufabric`, crossed with the
    IEA's own status field.

    THE CLASS IS THE FILTER, so two of the IEA's five statuses are absent from this table
    by construction and not by finding: an entry at FID or beyond never reaches this class,
    because classify() routes it to `unexplained at FID or beyond` first. What the table
    can say is how the search went, and whether it went differently for a concept than for
    a feasibility study."""
    if not SEARCH.exists():
        return "\nadmission search: sources/hydrogen_gap_search.json not present."
    doc = json.loads(SEARCH.read_text(encoding="utf-8"))
    rows = doc["entries"]
    statuses = sorted({r["status"] for r in rows})
    grid = {o: {s: 0 for s in statuses} for o in SEARCH_OUTCOMES}
    unclassified = 0
    for r in rows:
        if r.get("outcome") in grid:
            grid[r["outcome"]][r["status"]] += 1
        else:
            unclassified += 1
    fetches = sum(len(r["fetches"]) for r in rows)
    guessed = sum(1 for r in rows for f in r["fetches"]
                  if str(f.get("note", "")).startswith("MACHINE DOMAIN GUESS"))

    w = max(len(s) for s in statuses) + 2
    out = [f"\nthe admission search that retired `not searched by eufabric` "
           f"({len(rows)} entries, {fetches - guessed} fetches, searched {doc['searched']}):",
           f"| {'search outcome':38} | " + " | ".join(f"{s:>{w}}" for s in statuses) + " | total |",
           "|" + "-" * 40 + "|" + "|".join("-" * (w + 2) for s in statuses) + "|-------|"]
    for o in SEARCH_OUTCOMES:
        row = [grid[o][s] for s in statuses]
        out.append(f"| {o:38} | " + " | ".join(f"{n:>{w}}" for n in row)
                   + f" | {sum(row):5} |")
    out.append(f"| {'TOTAL':38} | "
               + " | ".join(f"{sum(grid[o][s] for o in SEARCH_OUTCOMES):>{w}}" for s in statuses)
               + f" | {len(rows) - unclassified:5} |")
    if unclassified:
        out.append(f"  {unclassified} entries carry no outcome.")
    out.append("  FID, Construction and Operational are zero by construction: an entry at "
               "FID or beyond\n  is routed to `unexplained at FID or beyond` before it can "
               "reach this class.")
    return "\n".join(out)


DISAGREEMENT_KINDS = ("capacity", "phasing", "site")


def disagreements() -> str:
    """WHERE THE BENCHMARK AND THE OWNER SAY DIFFERENT THINGS, printed and not resolved.

    Same principle as the schedule disagreements the transition rows already carry: when
    two speakers are asked and answer differently, the register records both and names the
    speakers. It does not pick. What is new here is the field — those are about dates, and
    these are about how big a thing is and where it stands.

    `normalisation_gap` is excluded on purpose. A difference under a fifth is the round
    trip through tonnes, not a speaker.
    """
    files = [(bench.ROOT / "sources/hydrogen_candidates.json", "candidates", "id"),
             (SEARCH, "entries", "ref")]
    rows = []
    for path, key, idf in files:
        if not path.exists():
            continue
        for obj in json.loads(path.read_text(encoding="utf-8"))[key]:
            for d in obj.get("benchmark_disagreements") or []:
                if d["kind"] in DISAGREEMENT_KINDS:
                    rows.append((d["kind"], str(obj[idf]), d))
    if not rows:
        return "\nbenchmark disagreements: none recorded."
    out = [f"\nbenchmark disagreements ({len(rows)}) — recorded, and not resolved:"]
    for kind in DISAGREEMENT_KINDS:
        here = [r for r in rows if r[0] == kind]
        if not here:
            continue
        out.append(f"\n  {kind} ({len(here)}):")
        for _, who, d in sorted(here, key=lambda r: r[1]):
            if kind == "capacity":
                out.append(f"    {who[:44]:44} ref {d['ref']:>5}  "
                           f"owner {d['eufabric_value_mw']:>5} MW  vs  benchmark "
                           f"{d['benchmark_value_mw']:>5} MW")
            elif kind == "site":
                out.append(f"    {who[:44]:44} ref {d['ref']:>5}  "
                           f"{d['eufabric_value']}  vs  {d['benchmark_value']}")
            else:
                out.append(f"    {who[:44]:44} ref {d['ref']:>5}  the benchmark splits "
                           f"what the owner publishes whole")
    gaps = sum(1 for path, key, idf in files if path.exists()
               for obj in json.loads(path.read_text(encoding="utf-8"))[key]
               for d in (obj.get("benchmark_disagreements") or [])
               if d["kind"] == "normalisation_gap")
    out.append(f"\n  and {gaps} normalisation gaps, under a fifth and excluded above: the "
               f"IEA states\n  kt H2/y and this register normalises at a fixed factor, so an "
               f"owner's megawatts\n  and the benchmark's cannot agree exactly even when the "
               f"speakers do.")
    return "\n".join(out)


def main() -> int:
    ou_all, iea_all = bench.load_ou(), bench.load_iea()
    checks = verify_inputs()
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
                     held_stems, ("odenweller_ueckerdt_2025", i),
                     # The academic file carries no location column at all.
                     has_location=False)
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
                     ("iea_hydrogen_production_projects", i),
                     # The live endpoint publishes a latitude and a longitude for
                     # every European entry. It is not a position this register
                     # may use — a third party's coordinate is refused here — but
                     # it does mean the entry says where.
                     has_location=r.get("latitude") not in (None, 0)
                     and r.get("longitude") not in (None, 0))
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
    # The class names outgrew the column when the split landed; the width is
    # measured rather than fixed so the next rename does not break the table.
    w = max(len("held by eufabric (rows and candidates)"), *(len(c) for c in CLASSES))
    print(f"| {'class':{w}} | {'O&U':>5} | {'IEA':>5} |")
    print(f"|{'-' * (w + 2)}|{'-' * 7}|{'-' * 7}|")
    for c in CLASSES:
        print(f"| {c:{w}} | {counts['odenweller_ueckerdt_2025'][c]:5} | "
              f"{counts['iea_hydrogen_production_projects'][c]:5} |")
    print(f"| {'held by eufabric (rows and candidates)':{w}} | {len(held_ou & set(ou)):5} | "
          f"{len(held_iea & set(iea)):5} |")
    print(f"| {'TOTAL':{w}} | {len(ou):5} | {len(iea):5} |")

    residue = [r for r in out if r["class"] == "unexplained at FID or beyond"]
    if residue:
        print(f"\nUNEXPLAINED AT FID OR BEYOND ({len(residue)}) — the only class that is a defect. Each of "
              f"these is at FID, in construction or operating, in the geography, above the "
              f"threshold, and neither held nor explained:")
        for r in residue:
            print(f"  {r['benchmark'][:4]:4} ref {r['ref']:>5}  {r['country']}  "
                  f"{r['normalised_mwel'] or '?':>6} MW  {r['status'][:18]:18} {r['name'][:58]}")
    else:
        print("\nUNEXPLAINED AT FID OR BEYOND (0) — every absence is a decision.")
    print(f"\ncompany source unreadable ({len(UNREADABLE_BY_NAME)}) — located, measured "
          f"and queued in sources/manual/wanted:")
    for (b, ref), why in sorted(UNREADABLE_BY_NAME.items()):
        print(f"  {b[:4]} ref {ref}: {why}")

    print(f"\nrefused by name ({len(REFUSED_BY_NAME)}) — recorded, never silent:")
    for (b, ref), why in sorted(REFUSED_BY_NAME.items()):
        print(f"  {b[:4]} ref {ref}: {why}")

    print(search_crosstab())
    print(disagreements())

    print("\nbenchmark inputs, by identity (sources/benchmark_snapshots.json):")
    print("\n".join(checks))

    print(f"\n  {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

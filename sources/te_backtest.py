#!/usr/bin/env python3
"""Back-test T&E's battery gigafactory risk lists against this register.

    python3 te_backtest.py        # writes scratch/te_backtest.csv, prints the summary

WHAT COULD BE EXTRACTED, AND WHAT COULD NOT. Both reports were fetched and read
with the declared User-Agent:

  2023  "How not to lose it all", March 2023, 25 pages.
  2024  "An industrial blueprint for batteries in Europe", May 2024, 80 pages.

THE PER-FACTORY RISK TABLE IS NOT IN EITHER TEXT LAYER. The 2023 report's
per-plant assignment is Figure 5, "Risk assessment of European battery cell
production capacities in 2030 by factory", and page 15 carries 92 characters of
text and two images; the 2024 equivalent is Figure 4. Both are charts. So a list
of 50 plants each with a class and a 2030 capacity cannot be read out of these
files, and none is invented here.

WHAT IS IN THE TEXT is Table 1 of the 2024 update — 24 named projects with
company, country and affected capacity in GWh, grouped by what changed — plus the
handful of projects either report classes in words. Those are the rows below, and
every one carries the page it came from. `te_class` is filled ONLY where a report
states a class for that project; the change category is recorded separately and is
not converted into a class.
"""
import csv, json, os, sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm

GROUPS = OrderedDict([("active", ("announced", "funded", "fid", "construction")),
                      ("paused", ("paused",)), ("stopped", ("cancelled", "withdrawn")),
                      ("operating", ("operating",))])

R23 = "TE-Battery-risk-report.pdf (March 2023)"
R24 = "An-industrial-blueprint-for-batteries-in-Europe.pdf (May 2024)"

# (te_project, country, capacity_gwh, class, change_category, source, page, match)
# match: a project id, or ("refused", clause) or ("unmatched", reason)
TE = [
 # --- 2024 Table 1, pages 17-18
 ("ACC", "France", 13, "", "started production", R24, 17, "acc-billy-berclau"),
 ("InoBat", "Slovakia", 10, "", "started production", R24, 17,
  ("unmatched", "InoBat's own Slovak line (Voderady); the perimeter's Slovak entry is the "
                "Gotion/InoBat Surany JV, listed separately in the same table")),
 ("ElevenES", "Serbia", 0.5, "", "started production", R24, 17,
  ("unmatched", "0.5 GWh, below the perimeter's 1 GWh scale rule")),
 ("Northvolt", "Germany", 60, "", "risk improvement", R24, 17, "lyten-heide"),
 ("CATL", "Hungary", 30, "", "risk improvement", R24, 17, "catl-debrecen"),
 ("EVE Energy", "Hungary", 28, "", "risk improvement", R24, 17, "eve-power-debrecen"),
 ("Envision AESC", "Spain", 10, "", "risk improvement", R24, 17, "envision-aesc-extremadura"),
 ("Phi4Tech", "Spain", 10, "", "risk improvement", R24, 17,
  ("unmatched", "not in the candidate set")),
 ("InoBat", "Serbia", 4, "", "risk improvement", R24, 17,
  ("unmatched", "not in the candidate set")),
 ("Tesla", "Germany", 25, "high", "risk downgrade, medium to high", R24, 17,
  "tesla-gruenheide-cells"),
 ("Svolt", "Finland", 50, "", "new announcement", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("Prologium", "France", 48, "", "new announcement", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("Tata Group / JLR", "UK", 40, "", "new announcement", R24, 18, "agratas-bridgwater"),
 ("Finnish Minerals Group", "Finland", 27, "", "new announcement", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("InoBat", "Spain", 24, "", "new announcement", R24, 18,
  ("refused", "site — the only company statement is a conditional declaration of intent "
              "with Valladolid, 19 October 2022")),
 ("Romvolt", "Romania", 22, "medium", "new announcement", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("InoBat & Gotion", "Slovakia", 20, "", "new announcement", R24, 18, "gib-surany"),
 ("Italvolt", "Italy", 45, "", "cancelled", R24, 18, "italvolt-scarmagno"),
 ("Freyr (Vaasa)", "Finland", 40, "", "cancelled", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("Freyr Nordic Battery Belt", "Nordics", 40, "", "cancelled", R24, 18,
  ("unmatched", "no named site; the perimeter refuses a project whose site is unconfirmed")),
 ("Volkswagen PowerCo", "Eastern Europe", 40, "", "cancelled", R24, 18,
  ("unmatched", "no named site; the perimeter refuses a project whose site is unconfirmed")),
 ("Farasis", "Germany", 16, "", "cancelled", R24, 18, "farasis-bitterfeld"),
 ("Freyr (Mo i Rana)", "Norway", 14, "", "cancelled", R24, 18, "freyr-mo-i-rana"),
 ("Blackstone Resources", "Germany", 10, "", "cancelled", R24, 18,
  ("unmatched", "not in the candidate set")),
 ("Eurocell", "Netherlands", 3, "", "cancelled", R24, 18,
  ("unmatched", "not in the candidate set")),
 # --- 2024 narrative, page 19 and page 17
 ("West Midlands Gigafactory", "UK", None, "medium", "named at medium risk", R24, 19,
  ("unmatched", "not in the candidate set")),
 ("CATL", "Germany", 14, "", "capacity revised down from 80 GWh", R24, 17, "catl-arnstadt"),
 ("CALB", "Portugal", 15, "", "capacity revised down from 45 GWh", R24, 17, "calb-sines"),
 # --- 2023 report
 ("Northvolt (Heide)", "Germany", None, "medium", "worked example in Annex 1", R23, 25,
  "lyten-heide"),
 ("Tesla (Berlin)", "Germany", None, "", "named as standing to lose the greatest volumes",
  R23, 2, "tesla-gruenheide-cells"),
 ("Northvolt (northern Germany)", "Germany", None, "",
  "named as standing to lose the greatest volumes", R23, 2, "lyten-heide"),
 ("Italvolt (near Turin)", "Italy", None, "",
  "named as standing to lose the greatest volumes", R23, 2, "italvolt-scarmagno"),
]


def main() -> int:
    rows = {r["id"]: r for r in sm.load("project")}
    out_dir = sm.ROOT / "scratch"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / "te_backtest.csv"
    cols = ["te_project", "te_country", "te_class", "te_change_category",
            "te_capacity_gwh_2030", "te_report", "te_page", "eufabric_id",
            "match_kind", "unmatched_reason", "current_status", "reporting_group",
            "capacity_on_file", "capacity_unit"]
    recs = []
    for name, country, cap, klass, change, rep, page, match in TE:
        rec = dict.fromkeys(cols, "")
        rec.update(te_project=name, te_country=country, te_class=klass,
                   te_change_category=change, te_report=rep, te_page=page,
                   te_capacity_gwh_2030="" if cap is None else cap)
        if isinstance(match, tuple):
            rec["match_kind"], rec["unmatched_reason"] = match[0], match[1]
        else:
            r = rows[match]
            grp = next((g for g, st in GROUPS.items() if r.get("status") in st), "")
            rec.update(eufabric_id=match, match_kind="row", current_status=r.get("status"),
                       reporting_group=grp,
                       capacity_on_file=r.get("capacity_value", ""),
                       capacity_unit=r.get("capacity_unit", ""))
        recs.append(rec)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(recs)

    print(f"{path}\n")
    print("T&E entries by risk class and where they are now")
    print("Class is filled only where a report states one; `not stated` is the rest.\n")
    hdr = ["te_class", "entries", "active", "paused", "stopped", "operating",
           "refused", "unmatched"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join(["---"] * len(hdr)) + "|")
    order = ["high", "medium", "low", "not stated", "ALL"]
    for k in order:
        sel = recs if k == "ALL" else [r for r in recs if (r["te_class"] or "not stated") == k]
        if not sel and k != "ALL":
            continue
        c = Counter(r["reporting_group"] or r["match_kind"] for r in sel)
        print("| " + " | ".join([k, str(len(sel))]
              + [str(c.get(x, 0)) for x in ("active", "paused", "stopped", "operating",
                                            "refused", "unmatched")]) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

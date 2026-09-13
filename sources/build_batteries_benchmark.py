#!/usr/bin/env python3
"""The batteries census: two outside lists, every entry in exactly one class.

    python3 sources/build_batteries_benchmark.py     # the tables, and the gate

WHAT THE BENCHMARK IS, AND WHY IT TOOK A READ RATHER THAN A DOWNLOAD.
T&E publishes no dataset behind its gigafactory work. The per-factory assignment
is a CHART in both editions -- Figure 5 on page 15 of the March 2023 report, and
Annex 1 on page 61 of the May 2024 one -- and `sources/te_backtest.py` recorded,
correctly, that no list of plants with a class and a 2030 capacity can be read
out of the PDFs' TEXT LAYER. That finding was about the text layer and was read
here for a year as a finding about the reports.

IT IS NOT. The charts are raster PNGs with the works' NAMES printed along the
axis, and the names are legible. So the entry list exists, it is the publisher's
own, and it is enumerable:

    2023 Figure 5   51 rows -- 50 named works and one "Others"
    2024 Annex 1    50 rows -- 49 named works and one "Others"

Both counts were taken twice and by different means: transcribed by reading the
label column at 600 dpi, and counted independently by finding the label blocks in
the pixels. The two agree, which is the only reason a gap table is allowed to
claim it sums to the list.

WHAT IS READ OFF THE CHART AND WHAT IS NOT. The NAMES are text and are recorded.
The CAPACITIES are bar lengths and are NOT: a number read off a pixel offset is
a number this register invented, and no entry below carries a capacity from a
T&E chart. The RISK CLASS is a colour, and it is recorded only as the colour the
publisher used, never converted into a judgement of this register's own. Several
bars are stacked across two classes, which is T&E splitting one works' capacity
by phase; where that happens the entry carries both.

THE SECOND LIST IS BATTERY-NEWS.DE and it is genuinely independent: different
authors (Gerrit Bockey and Heiner Heimes, PEM at RWTH Aachen), a different method
(official announcements), and a vintage fourteen months newer than T&E's latest.
Its atlas is a graphic too, but its figures are TYPED into the graphic rather
than drawn, so its capacities ARE readable and are recorded as the list's own.

MATCHING, AND WHAT IS NOT A JOIN. T&E's entries carry no identifier, so THE
BENCHMARK'S OWN IDENTIFIER IS ITS CHART LABEL -- a company and a works, together.
An entry is matched to a row here when the company AND the works agree; that is
two stated attributes agreeing, not a name stem, and it is the only route used.
Where a label names a company and a COUNTRY -- "SVOLT Finland", "VW East.
Europe", "Freyr Nordic Battery Belt" -- there is no works to agree with and no
join is attempted. Every match below is printed for confirmation, because the
standing rule is that a resemblance proposes and a person disposes.

THE CLASSES, AND THE GATE. Each entry ends in exactly one, and the counts must
sum to the list's own row count or this script exits non-zero. `not searched` is
the only class that is a defect, and it is printed by name.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sector_map as sm  # noqa: E402

ROOT = pathlib.Path(sm.ROOT)
OUT = ROOT / "sources" / "batteries_benchmark.json"

CLASSES = ("held", "admitted", "named not admitted", "searched none found",
           "unreadable", "perimeter exclusion", "not searched",
           "held for ruling", "aggregate")

# ---------------------------------------------------------------------------
# The register's standing battery refusals, from sources/batteries_docket.md
# §2 "Refused, and by which clause". Quoted here so an entry that lands on one
# carries the clause somebody already wrote rather than a new one invented to
# fit the benchmark.
STANDING_REFUSALS = {
    "varta": ("scale", "VARTA, Ellwangen / Nördlingen — small-format cells"),
    "customcells": ("scale", "CustomCells, Itzehoe and Tübingen — specialty cells well "
                             "under 1 GWh"),
    "inobat-spain": ("site", "InoBat, Spain — the only company statement is a conditional "
                             "declaration of intent with Valladolid of 19 October 2022, "
                             "'if Spain is selected', and nothing since"),
}

# ---------------------------------------------------------------------------
# T&E 2024, Annex 1, page 61. In the chart's own order, top to bottom.
# (label, klass, ref, note)
TE2024 = [
 ("LG Energy Solution Wroclaw", "held", "lges-wroclaw", ""),
 ("Tesla Berlin", "held", "tesla-gruenheide-cells", ""),
 ("CATL Debrecen", "held", "catl-debrecen", ""),
 ("Envision AESC Navalmoral de la Mata", "held", "envision-aesc-extremadura", ""),
 ("West Midlands Gigafactory Coventry", "searched none found", "",
  "wmgigafactory.com and wmgigafactory.co.uk both fail to resolve; coventry.gov.uk "
  "answers 200 with a council home page that names no works. The project's own site is "
  "gone, which is itself the interesting fact and is not read here as a stop."),
 ("Northvolt Skellefteå", "held", "northvolt-ett-skelleftea", ""),
 ("Northvolt Heide", "held", "lyten-heide", ""),
 ("Volvo & Northvolt Gothenburg", "held", "novo-energy-gothenburg", ""),
 ("Verkor Dunkirk", "held", "verkor-dunkirk", ""),
 ("SVOLT Finland", "named not admitted", "",
  "FAILED LEG: SITE. The entry names a company and a country and no works. "
  "svolt-eu.com answers 200 with an empty body, so the company's own statement could "
  "not be read either."),
 ("Prologium Dunkirk", "searched none found", "",
  "prologium.com/news answers 200 with 12,831 characters and the string 'Dunkirk' is "
  "not among them. The company's own newsroom does not name the works T&E names."),
 ("ElevenEs Subotica", "held", "elevenes-subotica",
  "A CANDIDATE, NOT A ROW. Open question C in the batteries docket: 8 GWh or 1 GWh, "
  "the sources conflict, and the scale rule cannot be applied until it is settled."),
 ("Morrow Arendal", "held", "morrow-arendal", ""),
 ("VW PowerCo Salzgitter", "held", "powerco-salzgitter", ""),
 ("VW PowerCo Sagunto", "held", "powerco-sagunto", ""),
 ("Tata Group/JLR Bridgwater", "held", "agratas-bridgwater", ""),
 ("Samsung SDI Göd", "held", "samsung-sdi-god", ""),
 ("Elinor Batteries Orkland", "searched none found", "",
  "elinorbatteries.com answers 200 with 1,349 characters of navigation and no works; "
  "its /news path is 404."),
 ("ACC Termoli", "held", "acc-termoli", ""),
 ("ACC Kaiserslautern", "held", "acc-kaiserslautern", ""),
 ("ACC Douvrin", "held", "acc-billy-berclau", ""),
 ("BMZ/TerraE Karlstein am Main", "named not admitted", "",
  "FAILED LEG: COMPANY-CONFIRMED CELL WORKS. bmz-group.com names Karlstein am Main "
  "exactly once, in the imprint — 'BMZ Battery Solutions GmbH … Sitz der Gesellschaft: "
  "Zeche Gustav 1, 63791 Karlstein am Main' — which is a registered office. Under the "
  "address corollary a Sitz der Gesellschaft never places a works, and it does not "
  "confirm one either."),
 ("InoBat Cuprija", "searched none found", "",
  "inobat.eu answers 200 with 7,484 characters and neither 'Cuprija' nor 'Ćuprija' "
  "appears in them."),
 ("Envision AESC Sunderland", "held", "envision-aesc-sunderland", ""),
 ("SK On Ivancsa", "held", "sk-on-ivancsa", ""),
 ("Envision AESC Douai", "held", "envision-aesc-douai", ""),
 ("Freyr Mo i Rana", "held", "freyr-mo-i-rana", ""),
 ("EVE Energy Debrecen", "held", "eve-power-debrecen", ""),
 ("FMG Group Kotka", "perimeter exclusion", "",
  "CLAUSE: BATTERY MATERIALS. Finnish Minerals Group's own news index calls it 'the "
  "Kotka CAM plant' — cathode active material. Cathode works are refused by name in the "
  "battery perimeter, and this is the entry the clause was named for in scope.md's "
  "Sector perimeters: an outside list carries it among battery cell entries and it is "
  "not one."),
 ("SVOLT Überherrn", "held", "svolt-uberherrn", ""),
 ("InoBat Valladolid", "named not admitted", "",
  "FAILED LEG: SITE, on the register's standing refusal. inobat.eu answers 200 and does "
  "not name Valladolid at all."),
 ("Romvolt (ABEE) Galati", "unreadable", "",
  "REFUSAL CLASS: DNS. abee.eu and www.abee.eu both fail to resolve for the declared "
  "reader. Queued for a browser."),
 ("QuantumScape Salzgitter", "named not admitted", "",
  "FAILED LEG: WHOSE WORKS IT IS. quantumscape.com/newsroom answers 200 and names "
  "PowerCo repeatedly and Salzgitter never: QuantumScape licenses cells that PowerCo "
  "makes. The Salzgitter works is held here as powerco-salzgitter. This is NOT filed as "
  "a duplicate, because identifier match is the only duplicate route and nobody has "
  "written T&E's entry onto that row."),
 ("InoBat & Gotion Surany", "held", "gib-surany", ""),
 ("SK On Komarom", "held", "sk-on-komarom", ""),
 ("CTAG Vigo", "searched none found", "",
  "ctag.com/en/news answers 200 with 25,024 characters and none of 'cell', 'GWh', "
  "'bater' or 'Vigo' appears in a battery-works sense. CTAG is an automotive technology "
  "centre."),
 ("MES Horní Suchá", "unreadable", "",
  "REFUSAL CLASS: DNS. mes-battery.com and www.mes-battery.com both fail to resolve."),
 ("CALB Sines", "held", "calb-sines", ""),
 ("CATL Arnstadt", "held", "catl-arnstadt", ""),
 ("SVOLT Lauchhammer", "held", "svolt-lauchhammer", ""),
 ("Phi4Tech Badajoz", "perimeter exclusion", "",
  "CLAUSE: PRODUCT. phi4tech.com's own news says the Badajoz works is a 'fábrica de "
  "celdas de supercondensadores' — supercapacitor cells — with a nanomaterials research "
  "centre beside it. A supercapacitor is not a battery cell, and the perimeter is a rule "
  "about what a works makes."),
 ("InoBat Voderady", "perimeter exclusion", "",
  "CLAUSE: PILOT/R&D. inobat.eu's own timeline: 'Received investment from Rio Tinto to "
  "support the completion of R&D centre and pilot battery line in Voderady'. The "
  "perimeter refuses a pilot line unless the company states it as a phase of a "
  "commercial project, and InoBat states the opposite — the pilot 'will provide the "
  "foundation for a manufacturing production line'."),
 ("Beyonder Rogaland", "unreadable", "",
  "REFUSAL CLASS: 200 WITH AN EMPTY BODY. beyonder.no answers 200 to the declared "
  "reader with a document carrying no article. Queued for a browser."),
 ("Basquevolt Alava", "named not admitted", "",
  "FAILED LEG: CAPACITY, AND A COMMERCIAL WORKS. basquevolt.com/en answers 200 and the "
  "only Álava address on it is 'Parque Tecnológico, C/Albert Einstein 35, 01510 "
  "Vitoria-Gasteiz' — a technology park, stated as the company's address rather than as "
  "a works. No GWh anywhere on the page."),
 ("AMTE Power Thurso", "unreadable", "",
  "REFUSAL CLASS: DNS. amteplc.com does not resolve. AMTE Power went into "
  "administration in 2024, which is the likely reason and is not read here as a status "
  "event on anything."),
 ("FAAM Teverola", "searched none found", "",
  "seri-industrial.it/en — FAAM's parent — answers 200 with 3,366 characters and does "
  "not name Teverola."),
 ("Swiss Clean Battery Domat-Ems", "searched none found", "",
  "swisscleanbattery.ch answers 200 with 3,409 characters and names neither Domat nor "
  "Ems nor a capacity."),
 ("Leclanché Willstätt", "held", "leclanche-willstatt",
  "A CANDIDATE, NOT A ROW."),
 ("Varta Ellwangen", "perimeter exclusion", "",
  "CLAUSE: SCALE, on the register's standing refusal — VARTA's Ellwangen and Nördlingen "
  "works make small-format cells."),
 ("Others", "aggregate", "",
  "T&E's own residual bar. Not a works and not a gap: it is the publisher saying that "
  "capacity exists below its naming threshold. It is carried in the table because the "
  "table must sum to the list, and it is never searched."),
]

# ---------------------------------------------------------------------------
# T&E 2023, Figure 5, page 15. In the chart's own order.
TE2023 = [
 ("Tesla Grünheide", "held", "tesla-gruenheide-cells", ""),
 ("LG Chem Wroclaw", "held", "lges-wroclaw", ""),
 ("CATL Debrecen", "held", "catl-debrecen", ""),
 ("CATL Erfurt", "held", "catl-arnstadt",
  "The works T&E calls Erfurt in 2023 and Arnstadt in 2024. One works, two names, and "
  "the rename is in the drift table."),
 ("West Midlands", "searched none found", "", "As 2024."),
 ("Northvolt Skellefteå", "held", "northvolt-ett-skelleftea", ""),
 ("Northvolt Heide", "held", "lyten-heide", ""),
 ("Volvo & Northvolt", "held", "novo-energy-gothenburg", ""),
 ("Verkor Dunkerque", "held", "verkor-dunkirk", ""),
 ("Italvolt Scarmagno", "held", "italvolt-scarmagno", ""),
 ("CALB Sines", "held", "calb-sines", ""),
 ("Morrow Arendal", "held", "morrow-arendal", ""),
 ("Freyr Mo i Rana", "held", "freyr-mo-i-rana", ""),
 ("VW Salzgitter", "held", "powerco-salzgitter", ""),
 ("VW Valencia", "held", "powerco-sagunto",
  "Sagunto is in the province of Valencia; T&E names the province in 2023 and the town "
  "in 2024."),
 ("VW East. Europe", "named not admitted", "",
  "FAILED LEG: SITE. A company and a region. VW never named the works and the project "
  "is in T&E's own 2024 table as cancelled."),
 ("Samsung SDI Göd", "held", "samsung-sdi-god", ""),
 ("InoBat & Gotion", "held", "gib-surany", ""),
 ("Freyr Vaasa", "searched none found", "",
  "t1energy.com — FREYR's successor — answers 200 with 3,067 characters and names "
  "neither Vaasa nor Finland."),
 ("Freyr Nordic Battery Belt", "named not admitted", "",
  "FAILED LEG: SITE. A programme name covering no named works."),
 ("ACC Termoli", "held", "acc-termoli", ""),
 ("ACC Kaiserslautern", "held", "acc-kaiserslautern", ""),
 ("ACC Douvrin", "held", "acc-billy-berclau", ""),
 ("InoBat Serbia", "searched none found", "",
  "inobat.eu answers 200 and names no Serbian works. T&E's 2024 vintage calls the same "
  "entry InoBat Cuprija, which is in the rename table."),
 ("Envision AESC France", "held", "envision-aesc-douai", ""),
 ("SKI Iváncsa", "held", "sk-on-ivancsa", ""),
 ("Eve Energy Debrecen", "held", "eve-power-debrecen", ""),
 ("Envision AESC Spain", "held", "envision-aesc-extremadura", ""),
 ("Envision AESC Sunderland", "held", "envision-aesc-sunderland", ""),
 ("SKI Komarom", "held", "sk-on-komarom", ""),
 ("SVOLT Saarland", "held", "svolt-uberherrn", ""),
 ("QuantumScape", "named not admitted", "", "As 2024."),
 ("Phi4Tech", "perimeter exclusion", "", "CLAUSE: PRODUCT. As 2024 — supercapacitors."),
 ("Gotion Göttingen", "unreadable", "",
  "REFUSAL CLASS: DNS. gotion.com.hk does not resolve for the declared reader."),
 ("SVOLT Brandenburg", "held", "svolt-lauchhammer", ""),
 ("Farasis", "held", "farasis-bitterfeld", ""),
 ("ElevenEs", "held", "elevenes-subotica", "A CANDIDATE, NOT A ROW."),
 ("MES", "unreadable", "", "REFUSAL CLASS: DNS. As 2024."),
 ("Customcells", "perimeter exclusion", "",
  "CLAUSE: SCALE, on the register's standing refusal."),
 ("Microvast", "unreadable", "",
  "REFUSAL CLASS: DNS. microvast.com does not resolve for the declared reader."),
 ("InoBat Slovakia", "perimeter exclusion", "",
  "CLAUSE: PILOT/R&D. The Slovak works is Voderady; see 2024."),
 ("Blackstone Resources", "unreadable", "",
  "REFUSAL CLASS: DNS. blackstoneresources.ch does not resolve."),
 ("Basquevolt", "named not admitted", "", "As 2024."),
 ("AMTE Power Thurso", "unreadable", "", "REFUSAL CLASS: DNS. As 2024."),
 ("FAAM Teverola", "searched none found", "", "As 2024."),
 ("Swiss Clean Battery", "searched none found", "", "As 2024."),
 ("Leclanché", "held", "leclanche-willstatt", "A CANDIDATE, NOT A ROW."),
 ("Eurocell", "not searched", "",
  "THE ONE DEFECT IN THIS TABLE, AND IT IS PRINTED BY NAME. A Dutch entry T&E's 2024 "
  "table carries as cancelled, with no company domain identified in this pass. Nobody "
  "has looked, and the answer is to go and look."),
 ("Varta", "perimeter exclusion", "", "CLAUSE: SCALE, on the standing refusal."),
 ("EAS Batteries", "named not admitted", "",
  "FAILED LEG: SCALE. eas-batteries.com answers 200 and confirms the works — 'EAS "
  "Batteries GmbH, Lokomotivenstraße 21, 99734 Nordhausen' — and cells for heavy duty "
  "and space, and states no capacity. The only figure anybody publishes is "
  "Battery-News.de's 0.5 GWh, which is below the 1 GWh rule and is the SECOND LIST'S "
  "figure rather than the company's. Recorded as failing on scale with the source of "
  "the figure named, not as a refusal on a number the company never gave."),
 ("Others", "aggregate", "", "T&E's own residual bar. As 2024."),
]

# ---------------------------------------------------------------------------
# Battery-News.de, "Battery Cell Manufacturers (Europe) as of February 2026".
# The list states company, site, year and GWh as text, so all four are recorded.
# (country, company, site, year, gwh, klass, ref, note)
BN2026 = [
 ("SE", "NOVO", "Gothenburg", "2026", "50", "held", "novo-energy-gothenburg",
  "The list marks it '(Paused)', which agrees with the row."),
 ("SE", "Volvo", "Mariestad", "2030", "X", "searched none found", "",
  "volvogroup.com's news index answers 200 with 3,465 characters and does not name "
  "Mariestad."),
 ("SE", "LYTEN", "Skelleftea", "X", "X", "held", "northvolt-ett-skelleftea", ""),
 ("GB", "AGRATAS", "Sommerset", "2027", "40", "held", "agratas-bridgwater",
  "The list spells the county 'Sommerset'; the works is at Bridgwater in Somerset."),
 ("GB", "AESC", "Sunderland", "2030", "35", "held", "envision-aesc-sunderland", ""),
 ("FR", "TIAMAT", "Douvrin", "2029", "5", "named not admitted", "",
  "FAILED LEG: SITE, AND IT IS A DISAGREEMENT RATHER THAN A GAP. Tiamat's own site says "
  "'TIAMAT plan to build a gigafactory to produce Sodium ion batteries, 10km south-east "
  "of the city of Amiens in the ZAC Jules Verne 2 industrial estate close to the commune "
  "of Boves'. The company names Amiens/Boves; the second list names Douvrin, 120 km "
  "away. Two speakers on one fact, and the company is the one the perimeter asks."),
 ("FR", "ACC", "Douvrin", "2030", "40", "held", "acc-billy-berclau", ""),
 ("FR", "VERKOR", "Dunkirk", "2030", "50", "held", "verkor-dunkirk", ""),
 ("FR", "Blue Solutions", "Quimper", "2032", "25", "searched none found", "",
  "blue-solutions.com answers 200 with 5,532 characters and names neither Quimper nor a "
  "capacity."),
 ("FR", "AESC", "Douai", "2029", "30", "held", "envision-aesc-douai", ""),
 ("FR", "ProLogium", "Dunkirk", "2030", "16", "searched none found", "", "As T&E 2024."),
 ("PT", "CALB", "Sines", "2028", "15", "held", "calb-sines", ""),
 ("ES", "PowerCo", "Sagunt", "202X", "40", "held", "powerco-sagunto", ""),
 ("ES", "BASQUEVOLT", "Vitoria-Gasteiz", "2027", "10", "named not admitted", "",
  "FAILED LEG: CAPACITY FROM THE COMPANY. The 10 GWh is the second list's figure; "
  "basquevolt.com states none."),
 ("ES", "AESC", "Navalmoral de la Mata", "2025", "50", "held",
  "envision-aesc-extremadura", ""),
 ("ES", "CATL / STELLANTIS", "Zaragoza", "20XX", "50", "held",
  "catl-stellantis-zaragoza", ""),
 ("ES", "InoBat", "Valladolid", "2029", "32", "named not admitted", "",
  "FAILED LEG: SITE, on the standing refusal. As T&E 2024."),
 ("NO", "MORROW", "Agder", "20XX", "X", "held", "morrow-arendal",
  "Arendal is in Agder county; the list names the county. Marked '(Paused)' by the "
  "list, where this register holds the row as cancelled — Morrow filed for bankruptcy on "
  "6 May 2026, three months after the list's vintage. A disagreement of vintage, not of "
  "fact, and it is in the disagreements table."),
 ("NO", "BEYONDER", "Rogaland", "202X", "X", "unreadable", "",
  "REFUSAL CLASS: 200 WITH AN EMPTY BODY. As T&E 2024."),
 ("DE", "Leclanché", "Willstätt", "2020", "2.5", "held", "leclanche-willstatt",
  "A CANDIDATE, NOT A ROW."),
 ("DE", "PowerCo", "Salzgitter", "202X", "40", "held", "powerco-salzgitter", ""),
 ("DE", "CATL", "Erfurt", "202X", "14", "held", "catl-arnstadt", ""),
 ("DE", "EAS", "Nordhausen", "202X", "0.5", "named not admitted", "",
  "FAILED LEG: SCALE. 0.5 GWh is the list's own figure and is below the 1 GWh rule; the "
  "company states no capacity at all. See T&E 2023."),
 ("DE", "LYTEN", "Heide", "202X", "X", "held", "lyten-heide", ""),
 ("DE", "UniverCell", "Flintbek", "2026", "10", "admitted", "univercell-flintbek",
  "ADMITTED BY THIS PASS, AND THE SECOND LIST IS WHY IT WAS FOUND. Neither T&E vintage "
  "carries this works. UniverCell's own company page carries all three admission legs: "
  "'jetzt betreiben wir eine erfolgreiche Gigafactory, die bereit ist, über 1,5 GWh "
  "hinaus zu skalieren', 'Unser Standort: Konrad-Zuse-Ring 1, 24220 Flintbek, "
  "Deutschland', and electrode AND cell production. The row carries 1.5 GWh, the "
  "company's figure; the list's 10 GWh is a disagreement and is recorded as one."),
 ("DE", "TESLA", "Grünheide", "2027", "X", "held", "tesla-gruenheide-cells", ""),
 ("DE", "V4SMART", "Nördlingen", "2024", "X", "searched none found", "",
  "varta-ag.com/en answers 200 with 2,348 characters and names neither Nördlingen nor "
  "V4Smart. VARTA's Nördlingen works is separately refused on scale in the register's "
  "standing refusals; V4Smart is the VARTA/Porsche venture and is not the same object, "
  "so it is recorded as searched rather than folded into that refusal."),
 ("PL", "LG Energy Solution", "Wroclaw", "2025", "115", "held", "lges-wroclaw", ""),
 ("SK", "InoBat", "Voderady", "2020", "10", "perimeter exclusion", "",
  "CLAUSE: PILOT/R&D. As T&E 2024."),
 ("SK", "InoBat / Gotion", "Šurany", "202X", "40", "held", "gib-surany", ""),
 ("HU", "CATL", "Debrecen", "2025", "100", "held", "catl-debrecen", ""),
 ("HU", "EVE", "Debrecen", "2026", "28", "held", "eve-power-debrecen", ""),
 ("HU", "SAMSUNG", "Göd", "202X", "40", "held", "samsung-sdi-god", ""),
 ("HU", "SK innovation", "Komarom & Ivancsa", "2028", "47.3", "held",
  "sk-on-komarom|sk-on-ivancsa",
  "ONE BENCHMARK ENTRY OVER TWO HELD ROWS. The list sums two works into one line and "
  "one capacity. This register holds them separately because they are two works, and "
  "the 47.3 GWh cannot be split between them by anybody here."),
 ("HU", "SUNWODA", "Nyiregyhaza", "202X", "X", "held", "sunwoda-nyiregyhaza", ""),
 ("IT", "FAAM", "Terevola", "2024", "8", "searched none found", "",
  "The list spells it 'Terevola'; the works is Teverola. As T&E 2024."),
 ("RS", "InoBat", "Serbia", "2032", "32", "searched none found", "", "As T&E 2023."),
 ("RS", "ElevenEs", "Subotica", "2027", "48", "held", "elevenes-subotica",
  "A CANDIDATE, NOT A ROW."),
]

# Disagreements: two speakers on one fact. Recorded, never resolved by this script.
DISAGREEMENTS = [
 {"object": "univercell-flintbek", "field": "capacity",
  "speakers": [{"who": "UniverCell Holding GmbH", "type": "company",
                "says": "1.5 GWh available, ready to scale beyond it",
                "url": "https://www.univercell.de/unternehmen"},
               {"who": "Battery-News.de", "type": "benchmark",
                "says": "10 GWh against a 2026 date",
                "url": "https://battery-news.de/en/europe-battery-cell-production/"}],
  "held": "The company's figure is on the row. The list's is here."},
 {"object": "morrow-arendal", "field": "status",
  "speakers": [{"who": "Morrow Batteries", "type": "company",
                "says": "bankruptcy filed 6 May 2026 — the row is cancelled",
                "url": ""},
               {"who": "Battery-News.de", "type": "benchmark",
                "says": "(Paused), as of February 2026",
                "url": "https://battery-news.de/en/europe-battery-cell-production/"}],
  "held": "A disagreement of VINTAGE, not of fact: the list is dated three months before "
          "the filing. It is recorded because a reader comparing the two needs to know "
          "which is older, and NOT read as the list being wrong."},
 {"object": "tiamat", "field": "site",
  "speakers": [{"who": "Tiamat Energy", "type": "company",
                "says": "a gigafactory 10 km south-east of Amiens, at ZAC Jules Verne 2 "
                        "near Boves",
                "url": "https://www.tiamat-energy.com/"},
               {"who": "Battery-News.de", "type": "benchmark",
                "says": "Douvrin",
                "url": "https://battery-news.de/en/europe-battery-cell-production/"}],
  "held": "No row either way — the entry fails the site leg. The disagreement is the "
          "reason it fails rather than a detail of a row that exists."},
]

# Reference debts: same-works pairs this register believes are one object and has
# no source identifying as one. Rule 30 — record the identifier, never guess the join.
REFERENCE_DEBTS = [
 {"pair": ["T&E 2023 'CATL Erfurt'", "T&E 2024 'CATL Arnstadt'"],
  "believed": "one works, held here as catl-arnstadt",
  "missing": "T&E never states that the two labels are the same entry. The rename is "
             "read from position in an ordered list and from the register's own "
             "knowledge of the works, not from a source that names both."},
 {"pair": ["T&E 2023 'VW Valencia'", "T&E 2024 'VW PowerCo Sagunto'"],
  "believed": "one works, held here as powerco-sagunto",
  "missing": "Same. Sagunto is in Valencia province and T&E says so nowhere."},
 {"pair": ["T&E 2023 'InoBat Serbia'", "T&E 2024 'InoBat Cuprija'"],
  "believed": "one entry",
  "missing": "Same, and neither is held here, so the debt is between two benchmark "
             "entries rather than between a benchmark and a row."},
 {"pair": ["T&E 2023 'SVOLT Saarland'", "T&E 2024 'SVOLT Überherrn'"],
  "believed": "one works, held here as svolt-uberherrn",
  "missing": "Same. Überherrn is in Saarland."},
 {"pair": ["T&E 2023 'SVOLT Brandenburg'", "T&E 2024 'SVOLT Lauchhammer'"],
  "believed": "one works, held here as svolt-lauchhammer",
  "missing": "Same. Lauchhammer is in Brandenburg."},
 {"pair": ["T&E 2023 'Envision AESC France'", "T&E 2024 'Envision AESC Douai'"],
  "believed": "one works, held here as envision-aesc-douai",
  "missing": "Same."},
 {"pair": ["T&E 2023 'Envision AESC Spain'",
           "T&E 2024 'Envision AESC Navalmoral de la Mata'"],
  "believed": "one works, held here as envision-aesc-extremadura",
  "missing": "Same."},
 {"pair": ["T&E 2023 'InoBat Slovakia'", "T&E 2024 'InoBat Voderady'"],
  "believed": "one works",
  "missing": "Same. Both are refused on the pilot/R&D clause either way."},
 {"pair": ["Battery-News 'MORROW Agder'", "T&E 'Morrow Arendal'"],
  "believed": "one works, held here as morrow-arendal",
  "missing": "One list names the county and the other the town; no source names both."},
 {"pair": ["Battery-News 'SK innovation Komarom & Ivancsa'",
           "sk-on-komarom and sk-on-ivancsa"],
  "believed": "one benchmark line over two held works",
  "missing": "The list gives one capacity for two works and no split. Nothing here can "
             "divide 47.3 GWh between them."},
]

# The rename pairs, as read for the drift table. Same evidence as the debts above:
# a person read them, and each is printed for confirmation rather than joined.
RENAMED = OrderedDict([
 ("CATL Erfurt", "CATL Arnstadt"),
 ("LG Chem Wroclaw", "LG Energy Solution Wroclaw"),
 ("Tesla Grünheide", "Tesla Berlin"),
 ("Verkor Dunkerque", "Verkor Dunkirk"),
 ("Volvo & Northvolt", "Volvo & Northvolt Gothenburg"),
 ("West Midlands", "West Midlands Gigafactory Coventry"),
 ("VW Salzgitter", "VW PowerCo Salzgitter"),
 ("VW Valencia", "VW PowerCo Sagunto"),
 ("InoBat & Gotion", "InoBat & Gotion Surany"),
 ("InoBat Serbia", "InoBat Cuprija"),
 ("Envision AESC France", "Envision AESC Douai"),
 ("Envision AESC Spain", "Envision AESC Navalmoral de la Mata"),
 ("SKI Iváncsa", "SK On Ivancsa"),
 ("SKI Komarom", "SK On Komarom"),
 ("Eve Energy Debrecen", "EVE Energy Debrecen"),
 ("SVOLT Saarland", "SVOLT Überherrn"),
 ("SVOLT Brandenburg", "SVOLT Lauchhammer"),
 ("QuantumScape", "QuantumScape Salzgitter"),
 ("Phi4Tech", "Phi4Tech Badajoz"),
 ("ElevenEs", "ElevenEs Subotica"),
 ("MES", "MES Horní Suchá"),
 ("InoBat Slovakia", "InoBat Voderady"),
 ("Basquevolt", "Basquevolt Alava"),
 ("Swiss Clean Battery", "Swiss Clean Battery Domat-Ems"),
 ("Leclanché", "Leclanché Willstätt"),
 ("Varta", "Varta Ellwangen"),
])


def _rows(spec, kind):
    out = []
    for rec in spec:
        if kind == "bn":
            country, company, site, year, gwh, klass, ref, note = rec
            label = f"{company} {site}"
            out.append({"label": label, "country": country, "company": company,
                        "site": site, "benchmark_year": year, "benchmark_gwh": gwh,
                        "class": klass, "ref": ref, "note": note})
        else:
            label, klass, ref, note = rec
            out.append({"label": label, "class": klass, "ref": ref, "note": note})
    return out


def gate(name, rows, expected):
    counts = Counter(r["class"] for r in rows)
    bad = [c for c in counts if c not in CLASSES]
    total = sum(counts.values())
    ok = total == expected and not bad
    return ok, counts, total, bad


def table(counts, total, title):
    print(f"\n{title}")
    print("| class | entries |")
    print("|---|---|")
    for c in CLASSES:
        if counts.get(c):
            print(f"| {c} | {counts[c]} |")
    print(f"| **TOTAL** | **{total}** |")


def main() -> int:
    te24 = _rows(TE2024, "te")
    te23 = _rows(TE2023, "te")
    bn = _rows(BN2026, "bn")

    problems = []
    for name, rows, exp in (("T&E 2024 Annex 1", te24, 50),
                            ("T&E 2023 Figure 5", te23, 51),
                            ("Battery-News February 2026", bn, 38)):
        ok, counts, total, bad = gate(name, rows, exp)
        table(counts, total, f"{name} — the gap table")
        if bad:
            problems.append(f"{name}: classes not in the vocabulary: {bad}")
        if total != exp:
            problems.append(f"{name}: table sums to {total}, the list has {exp} rows")
        else:
            print(f"GATE: sums to the list's own {exp} rows.")

    # --- drift between the two T&E vintages ---------------------------------
    n23 = [r["label"] for r in te23]
    n24 = [r["label"] for r in te24]
    carried = []
    for old in n23:
        new = RENAMED.get(old, old)
        if new in n24:
            carried.append((old, new))
    left = [o for o in n23 if RENAMED.get(o, o) not in n24]
    carried_new = {new for _, new in carried}
    added = [n for n in n24 if n not in carried_new]

    print("\nDRIFT, T&E March 2023 → T&E May 2024")
    print("Renamed sits INSIDE carried over: a renamed entry neither left nor arrived.")
    print("| movement | entries |")
    print("|---|---|")
    print(f"| left | {len(left)} |")
    print(f"| carried over | {len(carried)} |")
    print(f"|   of which renamed | {sum(1 for o, n in carried if o != n)} |")
    print(f"| added | {len(added)} |")
    print(f"| **2023 total** (left + carried over) | **{len(left) + len(carried)}** |")
    print(f"| **2024 total** (carried over + added) | **{len(carried) + len(added)}** |")
    if len(left) + len(carried) != 51:
        problems.append(f"drift: left+carried = {len(left)+len(carried)}, 2023 has 51")
    if len(carried) + len(added) != 50:
        problems.append(f"drift: carried+added = {len(carried)+len(added)}, 2024 has 50")

    print("\nLEFT THE LIST, against this register's own classes")
    print("Leaving a list is drift. It is not a stop, and no status_history is touched.")
    by = Counter()
    left_detail = []
    for lab in left:
        rec = next(r for r in te23 if r["label"] == lab)
        by[rec["class"]] += 1
        left_detail.append({"label": lab, "eufabric_class": rec["class"],
                            "ref": rec["ref"]})
    print("| this register's class | departed entries |")
    print("|---|---|")
    for c in CLASSES:
        if by.get(c):
            print(f"| {c} | {by[c]} |")
    print(f"| **TOTAL** | **{sum(by.values())}** |")
    for d in left_detail:
        print(f"    left: {d['label']}  →  {d['eufabric_class']}"
              + (f" ({d['ref']})" if d["ref"] else ""))

    # --- drift between the lists -------------------------------------------
    print("\nDRIFT, T&E May 2024 ↔ Battery-News February 2026")
    print("Two independent lists, so this is not a vintage. It is what each holds that")
    print("the other does not, joined only through this register's own rows.")
    te_refs = {r["ref"] for r in te24 if r["ref"]}
    bn_refs = set()
    for r in bn:
        for x in (r["ref"] or "").split("|"):
            if x:
                bn_refs.add(x)
    print(f"| both lists, via a row here | {len(te_refs & bn_refs)} |")
    print(f"| T&E only, via a row here | {len(te_refs - bn_refs)} |")
    print(f"| Battery-News only, via a row here | {len(bn_refs - te_refs)} |")
    print("  T&E only:        " + ", ".join(sorted(te_refs - bn_refs)))
    print("  Battery-News only: " + ", ".join(sorted(bn_refs - te_refs)))

    # --- the defect class, by name -----------------------------------------
    print("\nNOT SEARCHED — the only class that is a defect, printed by name")
    ns = [(n, r["label"]) for n, rows in (("2024", te24), ("2023", te23), ("BN", bn))
          for r in rows if r["class"] == "not searched"]
    if not ns:
        print("  none")
    for n, lab in ns:
        print(f"  {n}: {lab}")

    print("\nADMITTED BY THIS PASS")
    adm = [r for rows in (te24, te23, bn) for r in rows if r["class"] == "admitted"]
    for r in adm:
        print(f"  {r['label']} → {r['ref']}")
    print(f"  {len(adm)} row(s).")

    doc = {"_comment": __doc__.strip().splitlines(),
           "generated": "2026-09-12",
           "benchmarks": {"te_2024_annex_1": te24, "te_2023_figure_5": te23,
                          "battery_news_2026_02": bn},
           "drift_te_vintages": {"left": left_detail,
                                 "renamed": [{"from": o, "to": n}
                                             for o, n in carried if o != n],
                                 "carried_over": len(carried), "added": added},
           "disagreements": DISAGREEMENTS,
           "reference_debts": REFERENCE_DEBTS}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")

    if problems:
        print("\nGATE FAILED")
        for p in problems:
            print("  " + p)
        return 1
    print("\nGATE PASSED — every table sums to its list.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

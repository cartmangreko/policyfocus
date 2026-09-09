# Hydrogen — perimeter and candidate docket

**Brief 7, Steps 1 and 2, complete.** This file is the stop the brief asks for: the
perimeter as proposed reviewed prose, the docket with its counts, and the
judgements the rows forced.

**UPDATED TWICE ON 9 SEPTEMBER 2026, ON TWO SETS OF GEORGE'S RULINGS.** The
first accepted D13 — a site may be placed on the works it stands on — and landed
three of thirteen. The second went further and settled the question the first one
left: **position is not an admission leg.** All twenty admitted candidates are now
rows. Sections 4 and 5 carry every decision in the order it was made, including
the ones later rulings overtook, because a decision edited out of a docket is a
decision nobody can see was made. It is the same object `sources/batteries_docket.md` is, written to
the same standard, and it stays in the repository after the rows land because it
is the record of what was refused and why.

---

## 1. The perimeter

### The proposed reviewed prose

Written for `/coverage`, so it clears the display vocabulary. `plant`, `record`,
`register`, `map` and `transition` are on the banned lists and none of them
appears below; the brief's own phrase "electrolyser plant" is therefore rendered
as **site**, which is the word the geography layer already uses in running text.

> **Hydrogen.** Eufabric holds an electrolytic hydrogen production site when three
> things are true of it at once: it makes hydrogen by splitting water, it stands in
> Europe as this platform draws it, and the company itself has confirmed a named
> site with an electrolyser capacity of at least 100 MW. Phases count towards that
> figure only where the company states the total; a first line stated on its own is
> a phase and not a smaller project.
>
> Europe here is the same named list of countries the battery boundary uses: the
> twenty-seven member states, together with the United Kingdom, Norway,
> Switzerland, the Western Balkans and Ukraine, with Türkiye outside it.
>
> Six things follow, and each is stated rather than left to judgement. Hydrogen
> made from methane with the carbon captured is out of this boundary for now, and
> is listed rather than refused, because whether it belongs is a question nobody
> here has answered. Steelworks that make their own hydrogen to reduce iron are
> steel sites and are already held as such. Pipelines, stores and import terminals
> are out: they are what a site depends on rather than sites in their own right,
> and they appear as links from the sites that name them. Works that build
> electrolysers are out, and belong with the rest of clean-technology
> manufacturing. Ammonia synthesis fed by electrolytic hydrogen is in. Methanol,
> e-fuel and aviation-fuel works are out unless their own electrolyser clears the
> threshold, in which case the electrolyser is what is held and the fuel works is a
> note on it.
>
> Capacity for an electrolyser is quoted three ways — the electricity it draws, the
> hydrogen it makes stated as a power or a flow, and the tonnes a year it is
> expected to produce — and this platform keeps whichever the source used and
> never converts between them. Where one source states two, both are kept. A site
> whose capacity nobody has stated is still held, and is listed as outstanding
> until a figure exists.

**Word check:** `python3 -c "import display_vocabulary as dv; print(dv.violations(TEXT))"`
returns `[]`. Confirmed before this file was written.

**"100 MW" appears verbatim**, in the sentence that states the rule rather than in
a note under it.

### What the perimeter refuses, each stated

| Class | Ruling | Where it goes |
|---|---|---|
| Hydrogen-DRI steelworks | OUT — a steel project, already held as one | Refusals below; the steel rows already carry them |
| Blue hydrogen (methane reforming with capture) | OUT of this dataset, and a candidate class for a later ruling | `sources/hydrogen_candidates.json` reason "blue, out of perimeter" — never refusals |
| Pipelines, stores, import terminals | OUT — dependency nodes, not sites | Asserted `depends_on` edges on the sites that name them |
| Electrolyser manufacturing | OUT — NZIA manufacturing, a later sector | Refusals below |
| Pilots and demonstrators below 100 MW | OUT | Refusals below |
| Methanol, e-fuel, SAF | OUT unless the electrolyser itself clears 100 MW | La Robla Green is the first case, admitted as its electrolyser |
| Ammonia fed by electrolytic hydrogen | IN | HØST PtX Esbjerg is the first case |

### How admission is enforced

The brief's admission test is company-confirmed site, by a company statement
naming the site or by the composite standard, all legs gated. Nothing new was
needed for it: `_location` in `sources/check_sector_schema.py` already refuses a
row without a position and already gates the three legs of the composite
standard, and no hydrogen row needed the composite standard — every operator on
this docket names its own site plainly.

---

## 2. The docket

| | count |
|---|---|
| Candidates the perimeter admits | **22** |
| — of them, rows on file in `data/transition/projects.json` | **22** |
| — of them, still candidates | **0** |
| Refused, by class, below | **8 classes named; 27 named instances** |
| In the manual queue for a browser | **2** |
| In `sources/schedule_queue.json` — no date from any admissible source | **2** |

`sources/report_candidate_gaps.py` prints the first three lines on every build:
`report_candidate_gaps: clean — 22 of 22 candidate(s) on file, 0 outstanding`.

### THE DOCKET IS AT ITS END, AND IT TOOK TWO RULINGS TO GET THERE

Read this before the rows.

Batteries stalled on **company confirmation**: the sweep kept finding sites the
operator had never named. Hydrogen never stalled there — every one of the twenty
candidates has a company source naming its site and stating its megawatts, usually
in the first paragraph of a release. It stalled on **position**, and on nothing
else, for thirteen of them.

**Ruling one, D13: a site may be placed on the works it stands on.** It landed
three — Hamburg Green Hydrogen Hub onto the dead Moorburg coal station, Uniper
onto its own Maasvlakte power station, Repsol onto its Tarragona refinery.

**Ruling two: position is not an admission leg.** It landed the other ten, and it
is the larger of the two. The ten have no works polygon of ANY kind — not their
own, not a host's — because they are construction fields on reclaimed land, in
ports, inside industrial parks and on greenfield. Under the old rule this register
would have reported European hydrogen while omitting Shell's largest plant, Air
Liquide's second, the biggest single electrolyser figure any company on the file
states, and the only project here with an insolvency in its history. That is not a
cautious register; it is a register that reports OpenStreetMap's coverage and
calls it industry.

### How the twenty-two are placed

| `located` | how, per site | rows |
|---|---|---|
| yes | `works` — the installation's own polygon | 2 |
| yes | `works` — a host works, named on the row | 9 |
| no | — the row says so, and carries its sweep | 11 |

The two on their own outlines are RWE's `GET H₂ Nukleus (300 MW)` at Lingen and
Air Liquide's `Normand'Hy`, both tagged `landuse=construction` and both carrying
the operator's name.

**The eleven unplaced rows carry their sweep on the row.** Each `location_note` says
where a polygon was looked for and what was found instead: the Maasvlakte box
from 51.94 N to 52.00 N, where the Porthos compressor station and three TenneT
converter stations are drawn and two 200 MW electrolysers are not; Emden, with
the Volkswagen works and thirty builders' yards; HØST, whose only feature naming
the developer is an *office*; Lubmin and Rostock, where what exists is an estate
and a port, both refused on the rule Subotica and Mo i Rana settled; La Robla,
where the one polygon found is the biomass half of a project this perimeter holds
the electrolyser of.

**And they are named, not merely absent.** The sector overview's sentence gains a
third clause — "no citable source places the works" — beside "cancelled" and
"location not sought", because the three are different facts. Each row's own page
renders without the location section and says in words that the company has
confirmed the site, that nobody has drawn it, and that the row is held anyway.

### The twenty-two rows

| # | Company | Site | Country | Capacity | Status | Position |
|---|---|---|---|---|---|---|
| 1 | RWE Generation SE | Lingen (Ems) | DE | 300 MW | commissioning | its own outline |
| 2 | BP Europa SE | Lingen (Ems) | DE | 100 MW · 11,000 t/y | construction | host: the refinery |
| 3 | Air Liquide | Port-Jérôme | FR | 200 MW | fid | its own outline |
| 4 | Shell Deutschland | Wesseling | DE | 100 MW · 15,000 t/y | fid | host: the chemicals park |
| 5 | Repsol | Muskiz | ES | 100 MW · 15,000 t/y | fid | host: the refinery |
| 6 | Galp | Sines | PT | 100 MW · 15,000 t/y | construction | host: the refinery |
| 7 | Moeve | Palos de la Frontera | ES | 300 MW · 45,000 t/y | fid | host: the refinery |
| 8 | Hamburg Green Hydrogen Hub | Hamburg-Moorburg | DE | 100 MW · 10,000 t/y | construction | host: a dead coal station |
| 9 | Uniper | Maasvlakte | NL | 100 MW | announced | host: its own power station |
| 10 | Repsol | La Pobla de Mafumet | ES | 150 MW | announced | host: the refinery |
| 11 | Shell Nederland | Tweede Maasvlakte | NL | 200 MW | construction | none |
| 12 | Air Liquide | Maasvlakte | NL | 200 MW | fid | none |
| 13 | EWE AG | Emden | DE | 320 MW | construction | none |
| 14 | OMV | Bruck an der Leitha | AT | 140 MW · 23,000 t/y | construction | none |
| 15 | Repsol | Cartagena | ES | 100 MW · 15,000 t/y | fid | none |
| 16 | Reolum | La Robla, León | ES | 200 MW · 28,000 t/y | announced | none |
| 17 | Copenhagen Infrastructure Partners | Måde, Esbjerg | DK | 100,000 t H2/y · 600,000 t NH3/y | announced | none |
| 18 | H2APEX Group | Lubmin | DE | 100 MW | announced | none |
| 19 | RWE Generation SE (JV of four) | Rostock port | DE | 100 MW | funded | none |
| 20 | Copenhagen Infrastructure Partners | Andorra, Teruel | ES | 500 MW · 40,000 t/y | announced | none |
| 21 | Phillips 66 (consortium of four) | Humber Refinery | GB | 100 MW | paused | host: the refinery |
| 22 | INOVYN (INEOS) | Köln-Worringen | DE | 100 MW | announced | none |

Rows 21 and 22 came from the benchmark gap report rather than the perimeter
sweep; §2b is where they came from.

**3,610 MW of electrolyser capacity, plus one row stated in tonnes.** All
twenty-two carry a stated figure — `clean: 22 of 22 plants with a stated
capacity`, still the only sector on this platform where that is true. Row 17 is the reason the
no-conversion rule was worth writing: HØST states an annual mass and no megawatts
at all, and the gigawatt figure that circulates for it is on no company page read
here.

**Two ownership events and two stops.** OMV's venture with Masdar on
6 November 2025 (49 per cent), and H2APEX taking sole ownership of HH2E Werk
Lubmin out of insolvency plan proceedings on 2 July 2025 — this sector's first
stop, `finance`, whose only surviving company source is the acquirer's, because
HH2E's own domain now refuses a connection outright. The second stop is Gigastack, paused in
August 2023 when its consortium withdrew from the UK's first electrolytic
allocation round.

**The first slip anywhere in this dataset is still row 1.** RWE said the first
Lingen electrolyser would be commissioned in 2024, then in 2025 — one speaker,
one milestone, twelve months. Across three other sectors the slip table has only
ever held disagreements.

### 2b. The benchmark gap, classified — and the two rows it found

`sources/report_benchmark_gap.py` takes the opposite question to the benchmark
file: not *how does each row compare*, but *what do the outside lists hold that
this register does not, and is each absence a decision or an oversight*. It runs
over every European entry at or above 100 MW in either list, **at any technology**
— the wider population, because `blue` is one of the classes and a population
that excluded fossil-with-capture could never report how much of it there is.

| class | O&U | IEA |
|---|---|---|
| duplicate of a held row | 4 | 2 |
| DRI or other perimeter exclusion | 25 | 31 |
| blue | 0 | 22 |
| below threshold on reading | 1 | 0 |
| benchmark gives no location | 202 | 0 |
| benchmark gives a location, no company or permit source names the site | 0 | 167 |
| company source unreadable | 2 | 1 |
| **not searched** | **0** | **0** |
| held by eufabric | 21 | 14 |
| **TOTAL** | **255** | **237** |

### The three states the old class hid

"no company-confirmed site" held nine in ten of the gap and a reader could not
tell from it whether the benchmark had said where a project is, whether anybody
had looked for a company source, or whether somebody had looked and been refused.
Those are three different things and they are now three classes.

**The split falls almost entirely along the line between the two files, and that
is the finding.** The October 2023 quality-checked file **has no location column
at all** — Ref, name, country, dates, status, technology, end use, capacity,
references, and nothing that says where. So every unresolved entry in it is
`benchmark gives no location`: a project this register would have to place cannot
even be looked for from that file, because the name is all there is. The IEA's
live endpoint publishes **a latitude and a longitude for all 237** of its European
entries, so every unresolved entry there is `benchmark gives a location`. **That
coordinate is not a position this register may use** — a third party's coordinate
is refused here and always has been — but it does mean the entry says where, and
what is missing is a company or permit source naming the site.

**`company source unreadable` has three members and they are all one page.**
Shell's own list of its hydrogen projects answers a declared reader with HTTP 200
and thirty-eight characters of text: the page title. The "MoU Shell – Mitsubishi"
entries — phases 1 and 2 in the academic list, phase 2 in the live one — sit here
rather than among the projects nobody has looked at, because somebody looked. The
page is queued in `sources/manual/wanted`.

**`below threshold on reading` fell from 22 to 1 when the test was corrected, and
the correction is worth recording.** The first version read "no megawatt figure
in `Announced Size`" as "below 100 MW", which quietly moved projects of several
gigawatts — quoted in tonnes or Nm³ — into a class that says they are small. It
now means only what it says: a stated figure that is below the threshold. One
entry in either list is that.

**`not searched` is the only class that is a defect**, and the report prints its
members by name rather than counting them, because the answer to it is to go and
look. It found **four**, all in the older academic list and three of them carrying
status "Other/Unknown" — which is what a list looks like when it has stopped
following a project rather than recorded that the project stopped.

| found | outcome |
|---|---|
| Gigastack–Hornsea 2, phase I (ref 552) | **landed.** 100 MW PEM at the Phillips 66 Humber Refinery, paused August 2023 |
| Gigastack–Hornsea 2, phase II (ref 1374) | a later phase of the same site — duplicate once phase I is held |
| INEOS Köln site (ref 1388) | **landed.** 100 MW announced October 2021, and nothing since |
| Centurion (ref 580) | **refused by name**, on two clauses at once |

**The inputs are snapshotted by identity.** `sources/benchmark_snapshots.json`
records each file's publisher URL, the day it was fetched, its size and its
SHA-256, and the report verifies the cache against it on every run. The bytes are
NOT archived, and the difference is a licence rather than a preference: both files
are the IEA's database and this repository may not redistribute it. A hash does
what the snapshot rule asks — makes every published number reconstructible — with
no copy nobody may pass on. The record is append-only, so a refreshed benchmark is
a new entry and the counts in this docket stay attached to the file they were
computed from.

**THIS IS A DISCOVERY ROUTE, AND THE BATTERIES FILE PREDICTED IT.** That file
recorded that the funding trail found two candidates the perimeter sweep had
missed, and said the lesson was worth remembering. The benchmark trail is the
second such route and it is better than the first, because it is exhaustive over
a published list and it can be re-run. It found a paused 100 MW project at a
British refinery that this register would otherwise never have known existed —
and the live IEA list has dropped that project entirely, which is a fact about
the list rather than about the project: **a paused project that vanishes from a
database is a project whose failure nobody counts.**

**Centurion is refused in `REFUSED_BY_NAME`, one entry with its clause**, the
same device the coordinate-source exceptions use: it is a 2018 Innovate UK
*feasibility study* about grid injection and salt-cavern storage, and the
perimeter refuses it twice over — no company statement confirms a project, and
storage is a dependency node rather than a site. Printed on every run.

**Two of the six classes are worth reading as findings rather than as bookkeeping.**
`below threshold on reading` is 22 and 9: entries that clear 100 MW only through
the IEA's normalisation, whose own `Announced Size` — the figure as the project
stated it — is below it. And `no company-confirmed site` is 183 and 159, which is
nine in ten of the gap: the perimeter admits what a company has confirmed, and a
feasibility study is a company saying it might.

### Refused, by class

**Steel projects making their own hydrogen (10 named).** Stegra Boden, HYBRIT
demo, HYBRIT expansion, SALCOS Salzgitter, tkH2Steel Duisburg, GravitHy
Fos-sur-Mer, Blastr Inkoo, Iberdrola–H2 Green Steel, Hydrogen-Reduced Sponge Iron
(Finland), GreenMotionSteel. Four of these are already rows in the steel sector.

**Electrolyser manufacturing (4 named).** thyssenkrupp nucera, Sunfire, Siemens
Energy and John Cockerill all appear on this docket as suppliers to admitted
sites, and their own works are NZIA manufacturing.

**Pipelines, stores and terminals (5 named).** The GET H2 pipeline network
(Nowega, OGE, SYNEQT), RWE Gas Storage West's Gronau-Epe cavern, the German
hydrogen core network, EWE's Huntorf cavern, OMV's 22 km Bruck–Schwechat
pipeline. All five are named by an admitted site's own source and all five are
recorded as asserted edges rather than as rows.

**Below the threshold (8 named).** REFHYNE 1 (10 MW, and still the largest PEM
electrolyser operating in Europe), OMV UpHy phase 1 (10 MW), Repsol Petronor's
2.5 MW and 10 MW units, Iberdrola Puertollano (20 MW), BASF Hy4Chem Ludwigshafen
(54 MW), EWE Bremen (50 MW), Kassø/Port of Aabenraa (45 MW).

**Blue hydrogen — LISTED, NOT REFUSED,** on the brief's own instruction. The live
IEA list carries **23** European fossil-with-capture entries at or above the
threshold, headed by H21 Leeds City Gate, HyNet Northwest and H2BE. They are a
class awaiting a ruling, not a class this perimeter has decided against.

---

## 3. What the benchmark file says

`scratch/hydrogen_benchmark.csv`, built by
`sources/build_hydrogen_benchmark.py`, matches all twenty objects — seven rows
and thirteen candidates — against both lists.

| | Odenweller and Ueckerdt (2025) | IEA, live |
|---|---|---|
| European electrolysis entries at or above 100 MW | 254 | 214 |
| of which eufabric holds | 18 | 13 |
| of which eufabric does not hold | 236 | 201 |

Reasons where they are knowable from the benchmark's own entry:

| Reason | O&U | IEA |
|---|---|---|
| Concept or feasibility study — no company-confirmed site read by this pass | 209 | 168 |
| Fuel works — in only if its own electrolyser clears the threshold | 13 | 26 |
| Out of perimeter: steel project | 10 | 7 |
| Not reached by this pass | 4 | 0 |

**The gap is a stage gap, not a coverage gap.** Nine in ten of what either list
holds and this register does not is a concept or a feasibility study. That is the
perimeter working: eufabric admits a site a company has confirmed, and a
feasibility study is a company saying it might. Read the other way round, of the
nine entries the live IEA list carries at FID or construction in Europe at or
above 100 MW, this register holds or has admitted **seven**; the two it does not
are Stegra and HYBRIT, which are steel.

### Three things the benchmarks did that a matcher has to know about

**They count phases; this register counts sites.** RWE's Lingen works is three
rows in both files and one row here. So `benchmarks` on a row accepts a LIST of
ids, and the gate takes one.

**Reference numbers were reassigned between vintages.** Ref 1877 is
"Sines refinery (phase 3)", 600 MW, concept in the 2023 file and
"GalpH2Park-I (Phase I)", 87 MW-equivalent, FID/construction in the live one. A
match made on the id alone, across vintages, puts a row against a phase six times
its size. Both ids are therefore stored separately, per benchmark, never as one.

**The IEA's own normalisation puts several 100 MW projects below 100 MW.** The
live endpoint publishes only kilotonnes of hydrogen a year; on the IEA's own
factor, each 100 MW phase of GET H2 Nukleus is 87 MW, REFHYNE 2 is 78 MW and
Galp Sines is 87 MW. Counting "their entries at or above 100 MW" therefore
excludes projects whose operators say 100 MW. The count is reported on their
factor and labelled, and no eufabric row is converted.

**And the IEA's definition sheet disagrees with itself about what its own column
is.** "Estimated normalised capacity" is described as "MW H₂ output (LHV)" and
derived from 0.0046–0.0052 MW per Nm³/h, which the sheet itself glosses as
"50 kWh/kg H₂" — electrical input. The column is input; the sentence above it says
output. This is the single best argument for the no-conversion rule in §2 of the
brief, and it is why that rule is now a standing ruling in `sources/scope.md`
rather than a note in a builder.

---

## 4. DECISIONS

Every judgement this pass made that the brief did not settle, in the order it
came up. Repeated verbatim in the pull request.

**D1. Hydrogen rows are filed under the `clean` sector key and the ecosystem
claims them by explicit edge.** The sector spine is keyed on FIGARO industries and
hydrogen is not one; `clean` ("Wind, heat pumps, hydrogen") already exists and no
ecosystem claims it by sector, so the hydrogen instance names its seven projects
one by one. That satisfies the boundary rule with exactly one claim per row, and
it is what "edge-defined" in the brief's §7 means in this schema.

**D2. `sector_scope` on the hydrogen ecosystem stays null.** The gate refuses a
scope note on an instance with no sector edge, and it is right to: a scope note
narrows a sector key and there is none to narrow. The reasoning moved into the
file's own comment.

**D3. `hydrogen-supply` becomes a shared technology rather than a second one.**
Steel reaches it as a dependency; hydrogen reaches it as the thing being built. A
duplicate under another name would have split the readiness assessment in two.

**D4. Air Liquide's Normand'Hy is `fid` although Air Liquide never says "final
investment decision".** The company announces "an investment of over 400 million
euros for the construction of" the electrolyser. The brief's rule that a grant, an
IPCEI notification, a Hydrogen Bank award and an EIB approval are `announced` is
about third-party money; this is the company committing its own to construction,
and it is the thing the `fid` rung is for. Flagged because it is the one status on
these rows read from a paraphrase rather than a phrase.

**D5. RWE's Lingen works is `construction`, not `operating`, although it is
producing hydrogen.** RWE says both things in the same release: "initial
quantities of renewable hydrogen are being produced", and "Over the coming
months, we will prepare the plants for commercial operation." This schema has no
rung between construction and operating, so the status is read from what the
company says about commercial operation. See new rule 6.

**D6. Galp Sines is dated from the EIB and not from Galp.** Galp's own FID
release is readable and undated to a declared reader — the site renders its
publication dates in the browser. An undated statement cannot date an event, so
the history starts at the EIB's release of 29 September 2025 and Galp's page is
cited beside it, carrying no date and dating nothing. Queued for a browser.

**D7. The EIB is filed as `grant_register` and the fit is bad.** The EIB is a
lender publishing a financing decision. `regulator` would say it acted on the
project, `official_register` would say the state wrote down a fact, and neither
is true. `grant_register` is the nearest and the row says so. **A lender source
type is a candidate class for a ruling.**

**D8. Moeve's Onuba carries 300 MW and not 405.** The company states 300 with an
option on 105 more "subject to obtaining additional grid capacity and board
approval", which is the opposite of stating a total. The 405 figure is real and
belongs to the grant, so it sits on the funding row with a note saying why the two
differ.

**D9. HØST PtX Esbjerg is `decarbonisation`, not the ammonia default.** The
brief's default is `supply_security` unless the source states decarbonisation.
This source states it.

**D10. The stop-reason rule binds on hydrogen and is reported for the other three
sectors.** `STOP_REASON_SECTORS` is `("clean",)`. Nineteen stopped events on
batteries, cement, steel and CCS predate the rule; the gate prints them on every
run and does not fail. Writing `unstated` across all nineteen to turn the gate
green would put a made-up distribution of reasons into the one field whose whole
purpose is that it is not made up. **The backfill is a re-read and it is George's
call whether it is worth one.**

**D11. Benchmark ids are stored on candidates as well as on rows.** Thirteen of
the eighteen sites eufabric matches to the academic list are candidates. Storing
ids only on rows would have dropped them out of the comparison at the point the
comparison is most interesting.

**D12. The benchmark input files are fetched and not committed.** Both are the
IEA's database and this repository is not licensed to redistribute it. The script
fetches from the publishers; `.gitignore` says why.

**D13. Step 1 delivered seven fully coded rows, not twenty.** The brief asks for
the first twenty admitted rows fully coded, including coordinates. Twenty
candidates were admitted and coded to the point their evidence allows; seven
cleared every leg. Thirteen are held out by the position rule, which is the
perimeter's own rule and the gate enforces it. **Inventing a position, or reading
one off a map tag, was the only way to make twenty, and neither is available
here.** Section 2 says what each of the thirteen is waiting on and where it was
looked for. If the answer is to admit a site on the host works alone, that is a
ruling that would land most of the thirteen immediately, and it is the single
most valuable thing to decide on this read.

### Step 2 decisions, after the first set of rulings on 9 September 2026

**D14. `location_precision` is recorded per SITE, not per row.** The ruling says
"every project row", and a row is not always at one place: ArcelorMittal covers
Bremen and Eisenhüttenstadt. One field on the row would have to pick between two
answers. Every row carries it in the only place it can be true — on each of its
sites — and 53 existing sites were backfilled from the source type that produced
them: `basemap` → `works`, `plan_parcels` → `parcel`, `company` and `permit` →
`point`, and the one named coordinate-source exception → `point`. The mapping is
declared in `sector_map.SITE_PRECISION_BY_SOURCE` and gated, so a row cannot
claim a precision its source cannot carry.

**D15. Two battery rows gained `host_works` as well as the hydrogen ones.** The
notes on PowerCo Salzgitter and Tesla Grünheide already said the polygon was the
host's — a Volkswagen works and a Tesla vehicle factory. Leaving them out would
have made the sector overview's new clause understate itself the day it landed.
Seven sites carry `host_works` in all.

**D16. Hamburg Green Hydrogen Hub is `private`, and the split resolves.** The
project company is Luxcara at 74.9 per cent and Hamburger Energiewerke, which the
City of Hamburg owns outright, at 25.1. The field is about the operator and the
majority of the operating company is private. **Had the split been the other way
this row would have had nothing honest to say**, and that is a real gap rather
than a near miss — see new rule 10.

**D17. Six stopping transitions are `unstated` and two are filed at a value that
does not fit.** The re-read of the nineteen found that six sources give no cause
at all, and that two give one this vocabulary cannot hold: FREYR's owner changed
the business it is in, and NOVO Energy lost its technology partner. Both are
filed at `ownership`, their nearest value, with the quote beside them and the
misfit written on the row. **A vocabulary that cannot hold two of fifteen stated
reasons is a candidate class for a ruling.**

**D18. `stop_reason_source_url` was needed and is new.** Slite's pause is dated
from a trade publisher this pipeline cannot read, and Heidelberg Materials said
why on its own Swedish site the same day. Moving the event onto the second source
would have re-dated it; so the quote carries its own URL and the event keeps its
date.

**D19. The stop-reason rule now binds on the event that STOPS a project and on no
other.** Four of the nineteen are later entries about already-stopped projects —
Slite's withdrawn permit application, Lyten's memorandum, Northvolt Ett's change
of owner. Asking each for a reason would make the register restate one cause
every time somebody wrote about a consequence.

**D20. Repsol Tarragona landed on one sentence, and it is the thinnest row here.**
It is named inside the Petronor release — "a large electrolyzer in Tarragona, with
a capacity of 150 MW" — and has no release of its own. That clears the perimeter,
which asks for a company-confirmed site and a figure, and the row says in its own
capacity note that this is all it rests on.

### Step 4 decisions, after the event-date ruling of 9 September 2026

**D28. `date_precision` goes on `stated_schedule` as well as on `status_history`.**
The ruling names event dates. A schedule entry's `date` is the day the promise was
made, which is an event, and Gigastack's two schedule entries come from a page
dated to a month. What the entry PROMISES keeps its own `target_precision`, read
at the end of its period; the two fields sit side by side and answer opposite
questions about the same line.

**D29. Italvolt's cancellation moved from 31 January to 1 January 2024.** It sat
at the month's END on a convention written in its own note — putting it late so as
not to claim precision — which contradicted the padding rule and which no count
could read. The note now records the correction rather than the old convention.

**D30. Four events were month-padded and one was a bare year, and all five were
already on the file.** carbon2business-lagerdorf carried `"2023"`, which the date
regex tolerated and no count could compare with a dated event. The other four —
Italvolt, H2APEX Lubmin, Gigastack and Samsung SDI Göd — were padded correctly
and said so only in prose. The field makes all five machine-readable and changed
one date.

**D31. Galp's capacity stayed `announced` for one day and is now `fid`.** The
first ruling let an EVENT carry year precision and put the final investment
decision on the history; the capacity could not follow, because `capacity_as_of`
had no precision field and would have claimed 1 January 2023 as a day, so the
figure stayed on the EIB's dated sentence with the lender's basis. The second
ruling gave every value date the same field. **The figure is now on the company's
sentence at `fid`, dated 2023 at year precision** — capacity_basis read from the
sentence that states both the decision and the megawatts — and the EIB's sentence
stays on the row as a second source, two years later, on the same 100 MW.

**D32a. Padding is undone for display, and a page caught it.** The first build
after the backfill printed "as of 2025-01-01" on the cement and steel lead blocks,
under a cost premium the International Energy Agency dates to 2025 — a day nobody
published, which is the error the precision field exists to prevent, arriving one
layer further out. `build_lead.py` now renders every value date at its own
precision, in one helper: a year shows as a year, a month as a month. The stored
date keeps its padding. A source's own `date` still has none and is printed as
stored — rule 21.

**D32. Nine other value dates moved with it.** Four Innovation Fund grants and a
journal figure to `month`; two Comext import totals and two cost premiums from a
bare `2025` to `2025-01-01` at `year`; EVE Power Debrecen's capacity from `2025-05`
to `2025-05-01` at `month`; Gigastack's to `month`. Every one was already padded
and said so only in prose, and one — the bare `2025` — was a date nothing could
compare with a dated value.

### Step 3 decisions, after the second set of rulings on 9 September 2026

**D21. `location_precision: "none"` is a ROW-level field and the other three are
per-site.** A row with sites carries the precision on each of them, because a row
is not always at one place; a row with no sites carries `none` on itself, because
there is nothing to hang it on. The gate refuses a row-level value where sites
exist and refuses a row with no sites that does not say `none` — so the state is
always positive and never inferred from an absence.

**D22. The no-position sentence branches on whether the project stopped.** A
stopped row's location was never sought; an active row's was sought and not
found. Telling the reader of a live 200 MW electrolyser that "looking for one was
not thought worth doing" would be false about work that was done, so
`projectNoLocationProse` has two sentences and the row's own note carries the
sweep.

**D23. The overview's undrawn clause has three reasons, not two.** Cancelled,
location not sought, and no citable source places the works. Folding the third
into the second would have said nobody looked.

**D24. EWE AG carries no owner type at all, and the gate now requires that to be
a decision.** EWE is not listed on an exchange and is held by municipal
associations together with a private investor; no source read here states the
split, so `private` and `state-owned` would both be assertions and `mixed`
describes a row rather than a party. The row carries a note instead, and a row
with neither value nor note now fails — on the sectors that have adopted the
field. The fifty-one that predate it are reported, not failed, on the same
reading the stop-reason backfill was done under.

**D25. Repsol Cartagena's owners are recorded as 75/25 and the 75 is derived.**
The release states that Enagás Renovable "holds a 25% stake in the project" and
says nothing about the rest. Recording Repsol at 75 is arithmetic on a two-party
statement rather than a figure the company gives, and it is the only share on
these rows that is not quoted. It changes nothing — the majority is Repsol's
either way — and it is written here because a share that looks sourced and is not
is exactly the thing this docket exists to catch.

**D26. FREYR and NOVO were refiled and the notes keep the day they were wrong.**
`strategy` and `partner` now exist; both rows were filed at `ownership` for one
day with the misfit written beside them, and the note on each says so rather than
being rewritten as though the values had always been there.

**D27. Twenty rows, and the benchmark file no longer has a candidate column
worth reading.** Every admitted object is a row, so `state` is `row` for all
twenty and the comparison is simply this register against the two lists.

---

## 5. Rules the first rows required that did not exist before

1. **Three units for one electrolyser, and no conversion between them.** New
   standing ruling in `sources/scope.md`. Four units added to `CAPACITY_UNITS`;
   `UNIT_PRODUCTS` refuses a unit paired with a product it cannot measure.
2. **`capacity_alternates`.** A second reading of the same phase, from the same
   source, in another unit — with every companion field the main figure carries.
   Five of the seven rows have one. The gate refuses an alternate repeating the
   row's own unit, because that is a disagreement and belongs in `capacity_note`.
3. **`CAPACITY_UNIT_PREFERENCE`, enforced on the row.** The brief says the export
   uses MW input where present. Holding that in the export would have been a
   second, invisible rule; the gate refuses a row that leads with a figure when an
   alternate carries a unit that comes first.
4. **`edges` — asserted dependency edges.** `supplies` / `depends_on`, four types,
   every edge carrying the sentence it was read from. `structural` is in the
   vocabulary and the gate REFUSES a hand-written one, so that when the technology
   rule lands the two kinds cannot be confused.
5. **`stop_reason` and `stop_reason_verbatim`.** Required on every event landing
   in a stopped status, refused on every other, `unstated` a real answer, and a
   verbatim required for every answer that is not `unstated`.
6. **A commissioning rung was missing, was named here, and is now on its own
   branch.** RWE's Lingen works was producing hydrogen and was not in commercial
   operation, and the ladder had nowhere to put that: `construction` said nothing
   was being made, `operating` said the project had arrived, and the company
   denied both in one paragraph. George ruled it in on 9 September 2026 and it is
   built on `status-commissioning`, cut from this branch — `commissioning` sits
   between construction and operating, is ALIVE for the counting groups and
   `active` for the paper's, is not terminal, and the parity gate now proves the
   two readings agree over 14,762 histories instead of 9,362. RWE's row moves on
   its own source; nothing else moves.
7. **`owner_listing`.** `listed` / `private` / `state-owned` on the row, for the
   disclosure-by-owner-type comparison the paper makes. Six of the seven rows are
   listed companies; Moeve is the private case. Hamburg Green Hydrogen Hub, when it
   lands, is the first split case — a city utility and a private asset manager in
   one project company.
8. **`benchmarks`, taking a list.** Both external lists count phases; this register
   counts sites.
9. **A third kind of unreadable page.** shell.com and galp.com answer a declared
   reader with HTTP 200 and a body containing the page title. A link checker calls
   that live, because it is. The manual queue's comment now names the state and
   two entries are filed under it.
10. **`owner_listing` cannot describe a joint venture, and one row nearly proved
    it.** Hamburg Green Hydrogen Hub is 74.9 per cent private and 25.1 per cent
    city-owned; the majority settles it this time. A 50:50 venture, or a listed
    company and a state one in partnership, has no honest value in the list. The
    fix is either a fourth value or a second field naming the split, and neither
    should be invented on a row.
11. **`stop_reason` is single-valued and sources are not.** SVOLT names tariffs,
    unevenly distributed subsidies and a lost customer project in one sentence;
    ArcelorMittal names energy costs and then weak demand and high imports;
    Northvolt lists four things. The field takes what CHANGED and the verbatim
    keeps the rest, which works and is a convention rather than a rule anything
    enforces.
12. **`location_precision` and `precision` are two fields about one coordinate and a
    reader will confuse them.** `precision` says what kind of place the point is
    (a works or a site); `location_precision` says how the position was resolved.
    Both are needed, both are gated, and the names do not tell them apart. Worth
    renaming before a third sector arrives.
13. **A party's listing has no value for "not listed and the split is unknown".**
    EWE AG is the case. The row-level `mixed` cannot be used, because it is a
    statement about a split between named parties, and neither `private` nor
    `state-owned` is sourced. The row carries no value and a note, which works
    and is not a vocabulary.
14. **`location_precision` at row level and at site level is one name for two
    scopes.** `none` can only be a row and `works`/`parcel`/`point` can only be a
    site, which is coherent and is not obvious from the name. Rule 12 asked for a
    rename before a third sector; this makes it two names, not one.
15. **The undrawn clause will not scale.** It names every undrawn row, which is
    right at ten and unreadable at fifty. The hydrogen overview is not drawn yet,
    so nothing renders it today; the sentence needs a cutoff before it does.
16. **`stop_reason` has no value for "the project is not ready".** Gigastack's
    consortium paused it saying "further project maturation and supply chain
    development is needed", which is neither finance, offtake, policy,
    infrastructure, cost, ownership, strategy nor partner. It is filed at
    `policy`, read from what they DID — withdrawing from the revenue-support
    round their own 2021 report made the schedule conditional on — with the
    misfit written on the row. A `readiness` or `supply_chain` value is the
    candidate class.
17. **A benchmark that drops a project drops its failure.** Gigastack is in the
    October 2023 academic list twice, with status "Other/Unknown", and is gone
    from the live IEA list altogether. A register built by following an outside
    list would have recorded this project's existence and never its pause. The
    gap report is the mechanism that caught it and it should be re-run whenever
    either list is refreshed.
18. **A class that holds nine in ten of a gap is not a class.** "no
    company-confirmed site" was three states — the benchmark says nothing about
    where, the benchmark says where and nobody has read a company source, and
    somebody read one and was refused — and the count was useless until they were
    separated. The general lesson is that a residual class should be watched for
    growth, not just for members.
19. **`maturity` is the third value a re-read forced.** After `strategy` and
    `partner`: the owner cites its own readiness, in technology or in supply
    chain. Gigastack was filed at `policy` for part of a day, read from what the
    consortium DID rather than what it SAID.
20. **CLOSED.** `capacity_as_of`, an alternate's `as_of` and a parameter's
    `date_of_value` all carry a precision now, on the same vocabulary and the same
    padding as an event. Galp's figure moved to the company's sentence the moment
    they did, which is the shortest a rule on this file has ever gone from being
    named to being closed.
21. **`retrieved_date` and a source's `date` do not carry one, and should be
    looked at next.** A source `date` is the day a publisher published, which is a
    day or it is nothing — but several on this file are the day a standing,
    undated page was read, and one, ITM Power's phase-2 report, is a page dated to
    a month and stored as its first day with the padding in a note. The same
    argument that closed rule 20 applies, one layer down.

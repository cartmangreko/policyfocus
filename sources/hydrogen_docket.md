# Hydrogen — perimeter and candidate docket

**Brief 7, Step 1.** This file is the stop the brief asks for: the perimeter as
proposed reviewed prose, the docket with its counts, and the judgements the first
rows forced. It is the same object `sources/batteries_docket.md` is, written to
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
| Candidates the perimeter admits | **20** |
| — of them, rows on file in `data/transition/projects.json` | **7** |
| — of them, still candidates | **13** |
| Refused, by class, below | **8 classes named; 27 named instances** |
| In the manual queue for a browser | **2** |
| In `sources/schedule_queue.json` — no date from any admissible source | **2** |

`sources/report_candidate_gaps.py` prints the first three lines on every build:
`report_candidate_gaps: clean — 7 of 20 candidate(s) on file, 13 outstanding`.

### THE THIRTEEN ARE NOT WAITING ON EVIDENCE. THEY ARE WAITING ON A DOT.

This is the finding of the pass and it should be read before the rows are.

Batteries stalled on **company confirmation**: the sweep kept finding sites the
operator had never named, and the composite standard was written for exactly that.
Hydrogen does not stall there at all. Every one of the twenty candidates has a
company source that names its site and states its megawatts, most of them in the
first paragraph of a press release. Twelve of the thirteen outstanding candidates
are outstanding for one reason and one reason only: **no citable source states
where the works is.**

The cause is not secrecy. It is that these works mostly do not exist yet. They are
construction fields inside refineries and chemical parks, and OpenStreetMap has
drawn two of them — RWE's `GET H₂ Nukleus (300 MW)` at Lingen and Air Liquide's
`Normand'Hy` at Port-Jérôme, both tagged `landuse=construction` and both carrying
the operator's name. Everywhere else the choice is the host works' polygon, which
places the mark within a few hundred metres and says so, or nothing.

Five of the seven rows that landed therefore stand on a **host works** polygon —
the refinery or chemical park the company names as the site — with a note on each
saying that is what it is. Two stand on the electrolyser itself.

Where a position was hunted and not found, the entry in
`sources/hydrogen_candidates.json` says where it was hunted, so nobody repeats
the sweep: Maasvlakte, Emden, Moorburg, Bruck an der Leitha, Lubmin, Escombreras
and La Robla were each swept for every named `man_made`, `landuse`, `power` and
`plant:source` feature on 9 September 2026.

### The seven rows

| # | Company | Site | Country | Capacity | Status | Position stands on |
|---|---|---|---|---|---|---|
| 1 | RWE Generation SE | Lingen (Ems) | DE | 300 MW_input | construction | the electrolyser itself |
| 2 | BP Europa SE | Lingen (Ems) | DE | 100 MW_input · 11,000 t/y | construction | the refinery |
| 3 | Air Liquide | Port-Jérôme | FR | 200 MW_input | fid | the electrolyser itself |
| 4 | Shell Deutschland | Wesseling | DE | 100 MW_input · 15,000 t/y | fid | the chemicals park |
| 5 | Repsol | Muskiz | ES | 100 MW_input · 15,000 t/y | fid | the refinery |
| 6 | Galp | Sines | PT | 100 MW_input · 15,000 t/y | construction | the refinery |
| 7 | Moeve | Palos de la Frontera | ES | 300 MW_input · 45,000 t/y | fid | the refinery |

1,200 MW of electrolyser capacity, all seven with a stated figure —
`check_capacity_clause` prints `clean: 7 of 7 plants with a stated capacity`,
which is the first sector on this platform where that is true.

### The thirteen candidates, and what each waits on

Every one is in `sources/hydrogen_candidates.json` with the sentence its capacity
was read from. In summary:

| Candidate | Country | MW | Waiting on |
|---|---|---|---|
| Shell Holland Hydrogen 1, Maasvlakte | NL | 200 | position — Maasvlakte swept, nothing drawn |
| Air Liquide ELYgator, Maasvlakte | NL | 200 | position — same sweep |
| EWE, Emden | DE | 320 | position — Emden swept |
| Hamburg Green Hydrogen Hub, Moorburg | DE | 100 | position — Moorburg swept |
| OMV, Bruck an der Leitha | AT | 140 | position — Bruck swept |
| Repsol, Cartagena | ES | 100 | position — Escombreras swept |
| Reolum, La Robla Green | ES | 200 | position — the brownfield found is the biomass half |
| CIP, HØST PtX Esbjerg | DK | — (100 kt H2/y) | position — Nominatim returns an office, refused |
| H2APEX, Lubmin (ex-HH2E) | DE | 100 | position — Lubmin swept |
| HyTechHafen Rostock | DE | 100 | position, and which of four JV partners is the operator |
| Uniper H2Maasvlakte | NL | 100 | position, and the company source read through this pipeline |
| CIP, Catalina | ES | 500 | a company source naming the electrolyser site |
| Repsol, Tarragona | ES | 150 | a release of its own |

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
6. **A commissioning rung is missing and this pass did not add one.** RWE's Lingen
   works is producing hydrogen and is not in commercial operation, and the ladder
   has nowhere to put that. Adding a rung touches `PROJECT_STATUSES`, the
   transition parity gate on both sides, the counting groups and the paper's own
   groups, which is more than this brief should do on its own. **Named here so it
   is a decision rather than a silence.**
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

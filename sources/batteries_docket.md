# Batteries — perimeter and candidate docket

**Brief 6, items 1 and 2. Nothing here is built yet.** This file is the stop the
brief asks for: the perimeter as proposed reviewed prose, and every candidate the
perimeter admits or refuses, with the clause that decided it and the source that
supports it. No rows, no graph, no page. It leaves this file when the dataset
lands.

---

## 1. The perimeter

### The proposed reviewed prose

Written for `/coverage`, so it clears the display vocabulary: `plant`, `register`,
`record`, `map` and `transition` are all on the banned lists and none of them
appears below. The brief's own phrase "battery cell manufacturing plant" is
therefore rendered as **site**, which is the word the geography layer already uses
in running text.

> **Batteries.** Eufabric holds a battery cell manufacturing site when three
> things are true of it at once: it makes battery cells, it stands in Europe as
> this platform draws it, and the company itself has confirmed a named site with
> an announced capacity of at least 1 GWh per year. Announced capacity means the
> capacity the company states it is building towards at that site; a smaller
> first line is a phase of it and not a different number.
>
> Europe here is a named list of countries rather than a coastline: the
> twenty-seven member states, together with the United Kingdom, Norway,
> Switzerland, the Western Balkans and Ukraine. Türkiye is outside it for now, as
> a whole country rather than by where a site stands relative to the Bosphorus,
> because a boundary that runs through one country's own industry is a boundary
> that will be argued with every time it is applied.
>
> Four things follow, and each is enforced rather than left to judgement. Pack
> and module assembly is out: a site that buys cells and builds them into packs
> is not making cells, and the great majority of what that removes is inside
> vehicle factories. A cell line inside a vehicle factory is IN — the rule is
> about what a site makes and not about who owns the gate. Cathode, anode,
> separator and electrolyte works are out for now: they are the inputs to a cell
> rather than a cell, and they arrive later either as material links or as a
> widened perimeter. Battery recycling is out here and belongs to circular
> materials, on the standing boundary rule that a site is claimed by the
> ecosystem whose product it makes; links back appear when that dataset exists.
> Pilot and research lines are out unless the company states the line as a phase
> of a commercial project.
>
> A project whose specific site the company has not confirmed is not held at all.
> That one needs no separate enforcement: every site on this platform carries a
> latitude and a longitude from a quoted source, and a site nobody has named
> cannot have one. Capacity is the one figure that may be sourced at any tier,
> with the tier written down; a site whose capacity nobody has stated is held
> only where a company or a government has described it as commercial-scale, and
> it is listed as outstanding until a figure exists.

**Word check:** `python3 -c "import display_vocabulary as dv; print(dv.violations(TEXT))"`
returns `[]`. Confirmed before this file was written.

**"1 GWh" appears verbatim**, as the brief requires, in the sentence that states
the rule rather than in a note under it.

### Two things the perimeter had to settle that the brief did not spell out

**Cell lines inside vehicle factories are IN.** The exclusion is of pack and
module assembly, and it is a rule about the **product**, not about who owns the
gate. Tesla's Grünheide site, PowerCo's Salzgitter site and the CATL/Stellantis
Zaragoza site are all cell manufacturing standing on or beside a vehicle factory,
and all three are admitted. Reading the exclusion as "no automotive sites" would
have thrown out three of the largest genuine cell projects in Europe. The prose
above says "including the assembly lines inside vehicle factories" so that the
distinction is drawn where a reader will look for it.

**"Geographic Europe" is wider than the EU**, and deliberately: it admits the
United Kingdom, Norway, Switzerland and Serbia, all of which have real candidates.
It has one edge that needs your ruling — see open question **D**.

### How each consequence is enforced

| Consequence | Enforcement | Silent? |
|---|---|---|
| Cells only — no pack/module assembly | Product rule in the gate; a candidate is admitted on what it makes | No — refused by name |
| No cathode/anode/separator/electrolyte | Product rule in the gate | No — refused by name, ROADMAP entry for the widening |
| No recycling | Boundary rule; claimed by circular materials | No — refused by name, edges back when that dataset exists |
| No pilot/R&D unless a stated commercial phase | Product rule in the gate | No — refused by name |
| Named company-confirmed site | Location layer, mechanically: no coordinate may be missing | No — the build fails |
| ≥ 1 GWh per year announced | Scale rule in the gate | No — refused by name |

The gate fails a candidate breaching the **product**, **site** or **scale** rule,
as the brief specifies. It is a gate and not a report because all three are
answerable from the data on the candidate itself; the two things that are *not*
answerable that way — the paused/cancelled distinction, and whether an announcement
is still live — are reports, per items 2 and 3.

---

## 2. The candidate docket

### How to read the source column

The perimeter requires a **company-confirmed** site. This pass identified
candidates and got as far as it could on sources in one sweep; the column says
honestly how far that is, because the difference decides whether a candidate can
become a held site at all.

- **company** — a company or joint-venture publication naming the site is in hand.
- **state** — a government or agency publication (HIPA, AICEP, National Grid, a
  state-aid decision). Good evidence, and **not** what the perimeter asks for.
- **press** — trade press only. **Not admissible as it stands.**

**Every `press` and `state` candidate below needs a company source fetched before
it can be admitted.** That is the perimeter doing its job, not a defect in the
docket, and it is the largest single piece of work between this file and the rows.

### Admitted — operating

| # | Company | Site | Country | GWh | Status basis | Source |
|---|---|---|---|---|---|---|
| 1 | ACC | Billy-Berclau / Douvrin | FR | 13 (block 1) | Inaugurated May 2023 | **company** (acc-emotion.com) |
| 2 | Verkor | Gigafactory Bourbourg, Dunkirk | FR | 16 | Inaugurated Dec 2025 | **company** (verkor.com) |
| 3 | PowerCo (VW) | Salzgitter | DE | up to 20 | Commissioned | **company** (volkswagen-group.com) |
| 4 | Envision AESC | Douai | FR | 10 (phase 1) | Operational 2025 | press |
| 5 | Envision AESC | Sunderland | UK | — | Second site began ops Dec 2025 | press |
| 6 | CATL | Arnstadt, Thuringia | DE | 14 | Cells since Dec 2022 | press |
| 7 | Tesla | Grünheide (Giga Berlin) 4680 line | DE | 8 → 18 target | Ramping; €250m expansion May 2026 | press |
| 8 | LG Energy Solution | Biskupice Podgórne, Wrocław | PL | ~86–90 | Operating | press |
| 9 | Samsung SDI | Göd | HU | — | Operating | press |
| 10 | SK On | Iváncsa | HU | — | Operating | press |
| 11 | SK On | Komárom | HU | — | Operating | press |

### Admitted — under construction

| # | Company | Site | Country | GWh | Status basis | Source |
|---|---|---|---|---|---|---|
| 12 | CATL | Debrecen | HU | 100 planned / 40 initial | Production from early 2026 | press |
| 13 | PowerCo (VW) | Sagunto, Valencia | ES | 40 planned / 20 at start | Series production July 2027 | **company** (volkswagen-group.com) |
| 14 | Agratas (Tata) | Gravity, Bridgwater, Somerset | UK | 40 | Piling complete; grid works under way | state (National Grid) |
| 15 | Gotion InoBat Batteries | Šurany | SK | 20 (→40) | Construction began Oct 2025 | **company** (inobat.eu / gibenergy.com) |
| 16 | Envision AESC | Navalmoral de la Mata, Extremadura | ES | — | Ground broken; first production 2026 | press |
| 17 | CATL / Stellantis JV | Zaragoza | ES | up to 50 | JV Dec 2024; production targeted end 2026 | **company** (stellantis.com) |
| 18 | Sunwoda | Nyíregyháza | HU | — | Under construction, on schedule | state (HIPA) |

### Admitted — announced

| # | Company | Site | Country | GWh | Status basis | Source | Newest source |
|---|---|---|---|---|---|---|---|
| 19 | EVE Power | Debrecen | HU | 30 (phase 1) | Environmental permit; production 2027 | state (HIPA) | 2026-07 |
| 20 | CALB | Sines | PT | 15 | Investment contract signed 20 Jan 2026 | state (AICEP) | 2026-01 |
| 21 | InoBat | Spain (site to confirm) | ES | — | Funding secured Sep 2025 | press | 2025-09 |

### Admitted — paused

| # | Company | Site | Country | GWh | Status basis | Source |
|---|---|---|---|---|---|---|
| 22 | ACC | Kaiserslautern | DE | — | **See open question A** | press |
| 23 | ACC | Termoli | IT | — | **See open question A** | press |
| 24 | FREYR / T1 Energy | Mo i Rana | NO | — | Cell manufacturing on hold; company pivoted to US | press |
| 25 | Lyten (ex-Northvolt) | Heide (Northvolt Drei) | DE | 60 originally | StaRUG restructuring; Lyten plans smaller | press |

### Admitted — cancelled

| # | Company | Site | Country | GWh | Status basis | Source |
|---|---|---|---|---|---|---|
| 26 | SVOLT | Überherrn, Saarland | DE | — | Withdrawn 2023 | press |
| 27 | SVOLT | Lauchhammer, Brandenburg | DE | — | Cancelled May 2023 | press |
| 28 | Britishvolt | Cambois, Blyth, Northumberland | UK | 35 | Administration Jan 2023 | press |
| 29 | Italvolt | Scarmagno | IT | — | Bankrupt Jan 2024; moved to UAE | press |
| 30 | Farasis | Bitterfeld-Wolfen | DE | 16 | Cancelled | press |
| 31 | Morrow Batteries | Arendal | NO | — | Filed for bankruptcy 6 May 2026 | press |
| 32 | Northvolt | Borlänge | SE | — | Cancelled | press |

### Admitted — status unresolved

| # | Company | Site | Country | GWh | Why unresolved |
|---|---|---|---|---|---|
| 33 | Lyten (ex-Northvolt) | Northvolt Ett, Skellefteå | SE | — | **See open question B** |
| 34 | ElevenEs | Subotica | RS | 8 or 1 — conflicting | **See open question C** |

### Refused, and by which clause

| Candidate | Clause | Note |
|---|---|---|
| Cellforce Group, Kirchentellinsfurt (Porsche) | scale, then product | Sub-1 GWh; site being shut down entirely |
| CustomCells, Itzehoe | scale | Specialty cells well under 1 GWh; insolvent 2025, new owners |
| CustomCells, Tübingen | scale | Closed and will not reopen |
| VARTA, Ellwangen / Nördlingen | scale | Small-format cells |
| Northvolt Labs, Västerås | pilot/R&D | R&D site, not a stated phase of a commercial project |
| Northvolt Poland, Gdańsk | product | Energy-storage system assembly — module and pack work |
| Umicore, Nysa | product | Cathode material |
| BASF, Schwarzheide | product | Cathode material |
| Every pack/module line at a vehicle factory | product | The exclusion's main population |
| Hydrovolt, Librec, Altilium and other recyclers | boundary | Circular materials; links back when that dataset exists |

**The refusals are the perimeter earning its place.** Four of the six clauses
actually bite on real candidates in this sector, which is not true of every
perimeter — the scale rule alone removes four German sites that a naive "battery
factories in Europe" sweep would have carried in.

---

## 3. Open questions — these need your ruling before rows are written

### A. ACC Kaiserslautern and Termoli: paused or cancelled?

**This is the Slite case again, twice, and bigger.** The brief asks for the
paused/cancelled distinction to be sourced with the same rigour, and the sources
do not currently settle it:

- The Italian metalworkers' union UILM said on **7 February 2026** that ACC
  management had confirmed the plans were **"definitively shelved."**
- ACC's own statement is weaker: *"It is clear that the prerequisites for
  restarting ACC's projects in Germany and Italy are not in place."*
- ACC was reported as **"considering shutting down the projects"** and in talks
  with unions **"over the modalities for a potential shutdown"** — which is the
  language of a decision not yet taken.

So the strongest word ("definitively shelved") is the **union's**, not the
company's, and the company's own words describe a condition rather than a
cancellation. Under the standing press ruling, status comes from the project's own
sources. On that reading both are **paused**, and I have entered them as paused
above — but flagged, not decided, because two of the largest European projects
turning on a union's adverb is exactly the call the brief says to bring to you.

This matters more than it did for Slite: under the #47 ruling, cancelled means
**undrawn** on the batteries overview. Ruling these cancelled removes two of the
sector's largest sites from the picture.

### B. Northvolt Ett / Lyten, Skellefteå — one project or two?

Northvolt filed for bankruptcy in March 2025, the largest in modern Swedish
history. Lyten acquired the assets and **completed the acquisition in February
2026**, assuming operations at Ett and Labs, with production planned to restart in
the second half of 2026.

The data model has no vocabulary for this. Options:

1. **One continuous project** that changed hands: status history runs
   operating → paused → (restart), with the company changing. The schema has no
   company-change event.
2. **Two projects**: Northvolt Ett, cancelled at bankruptcy; and a new Lyten
   project at the same site, announced. Honest about the discontinuity, and it
   double-counts the site on the overview.

I lean to (1) with the company as Lyten and the history carrying the bankruptcy
and the acquisition as events, because the site, the building and the equipment
are continuous and it is the *ownership* that broke. But this is a modelling
ruling, not a sourcing one, and the same question will recur.

### C. ElevenEs Subotica — does it clear 1 GWh?

Sources conflict badly. One line has a Subotica gigafactory at **8 GWh** launching
2026 with 40 GWh to follow; another has the February 2026 Series B financing
supporting a **1 GWh** LFP mega-factory with construction starting February 2026.
A third describes the existing facility as already "fully operational."

At 8 GWh it is comfortably in. At 1 GWh it is exactly on the threshold, and
"at least 1 GWh" admits it — but only if 1 GWh is the *announced capacity* rather
than a first phase of something smaller. **Needs a company source before it can be
admitted**, and it is the row that will test the scale rule's wording hardest.

### D. Does "geographic Europe" include European Turkey?

Turkey has real cell candidates (Siro, a Togg/Farasis joint venture, at Gemlik).
Gemlik is in Bursa province, on the **Asian** side of the Sea of Marmara, so on a
strict geographic reading it is out — but the rule then turns on which side of a
strait a site stands, which is a poor thing for a perimeter to rest on. Three ways
to close it: name the continental boundary explicitly; say "Europe" and let the
basemap's own country set decide; or scope to Europe plus named neighbours. **No
candidate is admitted or refused on this today** — I flag it because the perimeter
becomes a gate, and a gate needs the answer.

### E. Capacity is missing for eight admitted candidates

Rows 5, 9, 10, 11, 16, 18, 22, 23 have no announced capacity figure in hand. The
scale rule cannot be applied to them mechanically until it exists. All eight are
very likely well over 1 GWh — these are the Korean majors' Hungarian and Polish
sites and the two ACC projects — but "very likely" is not what the gate reads.

---

## 4. Staleness, applied by hand

Item 3 asks for a standing report on announced candidates whose newest source is
older than twelve months. That report is not built yet — it comes after this stop
— but the test is worth running now, because it is one of the things you are
reading this docket to judge. Against a **1 September 2026** clock:

| Candidate | Newest source | Age | Zombie? |
|---|---|---|---|
| EVE Power, Debrecen | 2026-07 | 2 months | No |
| CALB, Sines | 2026-01 | 7 months | No |
| InoBat, Spain | 2025-09 | ~12 months | **On the line** |

**Only one announced candidate is anywhere near the threshold**, and that is
because this sector's dead projects mostly died loudly — bankruptcies and union
statements — rather than going quiet. The zombie population the report exists to
catch is smaller here than the brief anticipated. The report is still worth
building: it is cheap, it generalises, and the sector's shape can change in a
quarter.

---

## 5. What this docket says about the sector

The standfirst clause the brief anticipates is real and is bigger than steel's.
Of 34 admitted candidates: **11 operating, 7 under construction, 3 announced,
4 paused, 7 cancelled, 2 unresolved.** Eleven of thirty-four are stopped or
dead — roughly a third — against steel's one in eight. One independent European
cell maker (Northvolt) went through the largest bankruptcy in modern Swedish
history; a second (Morrow) filed in May 2026; a third (FREYR) left for the United
States. The European-owned share of this sector's operating capacity is small and
falling, and most of what is operating or building is Chinese, Korean or a
carmaker's own subsidiary.

That is a fact about the sector, and the page should carry it rather than a
pipeline number that quietly counts dead projects as live.

---

## 6. The location layer, checked against batteries (brief item 9)

The brief predicts the geography lights up for batteries with zero geometry work
and asks me to report if it does not. **It half does**, and the half that does not
would fail the build rather than degrade quietly.

I checked this by running the real functions in `build_maps.py` against the
extreme candidate sites rather than by reading the code.

**Geometry: nothing to do, exactly as predicted.** Every candidate site falls
inside the fixed Europe overview frame — Sines at 37.9 N and 8.9 W, Mo i Rana at
66.3 N, Šurany, Subotica, Skellefteå, Bridgwater — so `EUROPE_DEGREES` needs no
widening and the out-of-frame gate in `build_maps.main` stays silent. Crops are
computed per subject and need nothing. The layer is genuinely sector-neutral.

**Ground naming: four names are missing, and each is a hard build failure.**
`label_countries` raises `SystemExit` rather than letting a two-letter code onto
the paper, and a crop names *every* country in view. Batteries reaches parts of
Europe no cement or steel crop has:

| Crop | Countries it would name | Unnamed in `country_names` |
|---|---|---|
| Sines, Portugal | 2 | **ES, PT** |
| Bridgwater, UK | 3 | **IE** |
| Šurany, Slovakia | 12 | **UA** |
| Skellefteå / Subotica / Mo i Rana | 4 / 9 / 2 | none |

So `data/prose.json` `country_names` needs **Spain, Portugal, Ireland and
Ukraine** before the first batteries crop builds. Cement and steel never reached
Iberia, Ireland or the Ukrainian border, so the gap has been latent since the
geography landed.

They are four one-line additions and I have **not** made them: country names are
reviewed prose, and the stop is before anything is built. Flagging them now
because they are a prerequisite rather than a consequence — the batteries build
fails at the first Spanish crop without them, with this message:

    build_maps: no name for ES — add them to country_names in data/prose.json
    rather than letting a two-letter code onto the paper

which is the gate working, and is cheaper to know about now than at the build.

---

## 7. Rulings applied, and what confirmation turned up

The rulings of 2 September 2026 are folded in. What follows is what changed and
what the company-source pass actually found, because the answer moved several
candidates.

**A — ACC stays paused, with the February 2026 reports as events.** ACC's own
words are that the conditions for restarting "are unlikely to be met" and that it
has begun a "constructive dialogue" with unions over potential discontinuation;
"definitively shelved" is UILM's. Both are on the Termoli row as a second event
with the status unchanged, which is the machinery the Slite ruling built.

**B — Northvolt Ett is one continuous project**, and `status_history` now has an
event kind. `ownership` carries `from`, `to` and the status the project was
already in. Three things fell out of that and all three were wanted: the
append-only invariant survives, `is_transition` already skips it — the status is
unchanged, so the "was paused on {date}" templates need no teaching — and the feed
still shows it with a true status chip. The gate refuses an ownership event that
opens a history or that also changes the status, because a company changing hands
on the day a project is paused is two events and one entry saying both reads as
one causing the other. The parity gate now runs every case twice, once with the
entries marked `ownership`, so the two languages cannot start disagreeing about
whether a kind matters: **9,362 histories agree.**

**C, D, E** are in the perimeter prose above.

### What company-source confirmation actually found

**Six rows landed.** They are in `data/transition/projects.json` and every gate
passes. Each has a company source, a works-level coordinate from OpenStreetMap
with the tags quoted, and a status history whose entries each carry a link.

| Row | Status | Company source | Exercises |
|---|---|---|---|
| `acc-billy-berclau` | operating | acc-emotion.com, 2023-05-30 | — |
| `verkor-dunkirk` | operating | verkor.com, 2025-12-11 | — |
| `powerco-salzgitter` | operating | volkswagen-group.com, 2025-12-17 | cell line at a vehicle works |
| `northvolt-ett-skelleftea` | paused | northvolt.com + lyten.com | **ruling B** |
| `acc-termoli` | paused | ACC quoted, 2026-02-09 | **ruling A** |
| `catl-stellantis-zaragoza` | announced | stellantis.com, 2024-12-10 | cell line at a vehicle works |

**And two candidates were stopped by the rules rather than by effort**, which is
worth recording because it is the perimeter and the location layer doing exactly
what they are for:

- **ACC Kaiserslautern has no OpenStreetMap feature.** The site is real and ACC's
  own, but the basemap carries no polygon for it, so there is no coordinate from a
  quoted source and the location rule keeps it off file. It is not a judgement and
  cannot be argued around; it needs a source for the position.
- **PowerCo Sagunto and GIB Šurany have company sources and no works-level
  coordinate.** The basemap has the industrial park at Sagunt and nothing named at
  Šurany. Same rule, same remedy.

**A fifth country name was needed beyond the four approved.** The four — Spain,
Portugal, Ireland, Ukraine — are in. The Termoli crop then failed the build asking
for **Montenegro**, because at 800 km across it reaches the far side of the
Adriatic, which my pre-check missed by only testing the sites I then wrote rows
for. It is added, and it is flagged here rather than buried: it is a fifth name
on a list of four that were approved.

### The dataset is complete by the perimeter's own definition

Six rows is not a sixth of the sector — it is all of the sector that is **on
file**, because the perimeter says a site the company has not confirmed is not
held. The other 28 candidates in §2 are candidates, not omissions.

That distinction is honest and it is also a real editorial problem for the page:
an overview drawn today would show six sites and would not show CATL Debrecen, the
Korean majors' Hungarian and Polish works, or any of the seven cancelled ones. The
picture would understate the sector badly. **The confirmation work is therefore
not tidying — it is the thing standing between this dataset and a page that can
honestly be published**, and it should finish before the sector page is drawn
rather than after.

---

## 8. Track (a) progress, and what the confirmation work is actually hitting

**The gap is no longer narrated here.** `sources/batteries_candidates.json` holds
the admitted set machine-readably and `report_candidate_gaps.py` prints what is
outstanding on every build. This section records what the second pass learnt; the
count itself is the report's job now.

**Seven rows on file, 27 outstanding.** The new row is CATL Arnstadt, on CATL's
own release of 21 December 2022 and the `CATL Werk G1` polygon.

### The two halves of the work are not equally hard, and it is the opposite of what I expected

**Coordinates turned out to be the easy half.** A sweep of the remaining 27 found
usable OpenStreetMap features for seven of them — Tesla Grünheide, LG Energy
Solution Wrocław, Morrow Arendal, Envision AESC Douai, CATL Debrecen, CATL
Arnstadt and, weakly, Samsung SDI Göd. Every reference is recorded on its
candidate as `coordinate_ref` so the lookup is not repeated.

**Company sources are the binding constraint**, and by some distance: 24 of 34
candidates still have none read. That is the reverse of the position after the
first pass, when coordinates looked like the blocker.

**Two refusals worth recording, because both are the rules working:**

- **SK On Iváncsa's only OpenStreetMap feature is an office node** — `office=company`
  on a point, not the works. A coordinate has to identify the works specifically,
  and an office at an address is not that. Refused, and recorded as refused so the
  next pass does not rediscover it and accept it.
- **Samsung SDI Göd's polygon is tagged only `Samsung`.** It identifies the
  industrial estate rather than the cell works. Recorded as weak rather than
  taken; it needs a second source before it is used.

**And the sector's largest project has no company source.** CATL Debrecen — 100
GWh planned, 40 GWh initial, production from early 2026 — is carried entirely by
trade press and Hungarian state agencies. Its coordinate exists
(`relation/18559299`, still tagged `landuse=construction`). The perimeter keeps it
off file until CATL says it, which is the rule doing exactly what it is for on the
one row where it costs the most.

### The acts track is less blocking than it looked

Batteries already carries **153 measures**: 101 naming `batsol` and 52 reaching it,
from CRMA, IAA and NZIA. Item 5's instruction to add `applies_to` edges to
batteries where CRMA and NZIA support them is largely already satisfied by the
existing reads. What is genuinely missing is the two new acts — the Battery
Regulation and the fleet standards — and neither is needed for the sector to have
a measure base.

---

## 9. The company-source sweep

**Eleven rows on file, 23 outstanding — 32% of the sector.** Four rows landed on
this pass: LG Energy Solution Wrocław, CATL Debrecen, Northvolt Drei at Heide,
and Morrow at Arendal.

**CATL Debrecen matters most.** It is the sector's largest project — 100 GWh,
€7.34 billion, 221 hectares in the Southern Industrial Park — and CATL's own
announcement of 12 August 2022 says so in as many words. It was the row the
perimeter was holding out at the greatest cost, and it is now in.

**Your expectation was right, with one correction.** The constraint was reading
rather than existence: every operator that has built at scale has documented it
in its own materials, and the sites came out of newsrooms, network pages and
investor copy exactly where you said they would. The correction is that the
constraint has **split in two**, and only one half is research:

### A source can be located and still unusable, and that is now its own state

`company_source_blocked` records a document that has been found and named and
that this pipeline cannot read. It is reported separately from "no source read",
because mixing them makes a five-minute job look like a research task and it then
gets a research task's priority.

- **AESC answers 403 to everything.** All three Envision AESC sites — Douai,
  Sunderland, Extremadura — have the right release identified and unreadable. The
  Douai coordinate is already in hand. Somebody with a browser closes all three.
- **SK On's English site serves a certificate for another host.** `eng.sk-on.com`
  presents a certificate for `*.skenergy.com`, so the page listing Iváncsa at
  "HRSZ 99/48, Iváncsa 2454" with 30 GWh from 2024 cannot be read here. SK
  Innovation's own network page was readable and gave Komárom.

### The published address is a company source and often not a coordinate

The widened rule admits an operator's own address, and three operators publish
one. It closes the source question and frequently not the position question:

- **Samsung SDI** names "2131 Göd, Schenek István utca 1". The street is not in
  the basemap; the address yields no point.
- **SK On** names "2900 Komárom, Klapka György út 39.". The street geocodes to two
  segments 700 m apart. A street centroid is no more a works than a town centroid
  is, so it is refused on the same rule.
- **Agratas** was read and gives the site and its state — 4,000 tonnes of steel
  standing at Bridgwater — and the basemap has nothing there under any name tried.

So both moved from "no company source" to "company source read, coordinate
outstanding", which is real progress and does not put them on the paper.

### Refusals recorded as refusals

- **SK On Iváncsa**: the only basemap feature is `office=company` on a point. An
  office is not the works and does not become the works by being the only thing
  available.
- **Samsung SDI Göd**: `relation/16364462` is tagged only `Samsung`. It identifies
  the industrial estate.

### One capacity that the ruling settled

Morrow Arendal is carried at **43 GWh**, not the 1 GWh of the cell factory that
was inaugurated. Ruling C says announced capacity is the company's stated target
for the site and a smaller first line is a phase of it, and Morrow's own release
describes the 1 GWh Morrow Cell Factory followed by three 14 GWh modules. It is
also, now, a cancelled project carrying a 43 GWh target, which is the sector's
shape in one row.

---

## Stopping here

A–E are resolved and the first six rows are in. What is left, in order:

1. **Company sources and coordinates for the remaining 28 candidates.** The
   binding constraint is coordinates as much as sources — three candidates
   already have a company source and no works polygon.
2. **Bottlenecks and the ranking**, which is what `hasMap` reads: until
   `data/transition/bottlenecks.json` carries batteries rows and
   `build_importance.py` writes `importance/batsol.json`, the tile keeps opening
   the holding page and no sector overview is drawn. Project crops already build,
   and the six are on disk.
3. **Materials**, for the CRMA Annex I links the technology nodes want.
4. **The two acts**, each a single pass declared as a preliminary reading.
5. **Funding rows**, then the prose slots, then the page.

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
| Northvolt Borlänge (Northvolt Fem) | product | **Refused on the second pass.** Admitted in error: Northvolt's own release of 9 September 2024 says Kvarnsveden was 'envisioned as a new facility for cathode active material production'. Cathode is refused by name |
| InoBat, Spain | site | **Refused on the third pass.** The only company statement is a conditional declaration of intent with Valladolid of 19 October 2022 — "if Spain is selected" — and InoBat's newsroom has carried nothing about Spain since. A site the company has never confirmed choosing is not a site |
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

## 10. The sweep continued: bounding boxes, and the limits of this pipeline

**Fifteen rows on file, 19 outstanding — 44%.** Four more landed: PowerCo Sagunto,
Agratas Bridgwater, GIB Šurany and Samsung SDI Göd.

### The coordinate problem was a search problem

Nominatim searches by name, and a works whose polygon is unnamed, named in the
local language, or named for its function is invisible to it. **A bounding-box
query over Overpass finds them.** That single change turned up six works the name
search had reported as absent:

| Site | What the basemap actually calls it |
|---|---|
| Agratas Bridgwater | `Agratas Battery Factory` — indexed under nothing I had searched |
| Samsung SDI Göd | `Cella gyártás` — *cell manufacturing*, tagged by function |
| GIB Šurany | unnamed, identified only by `operator=GIB EnergyX Slovakia` |
| PowerCo Sagunto | `Gigafactoria Volkswagen` |
| CALB Sines | `Construção da Unidade Industrial de Baterias de Lítio da CALB` |
| Italvolt Scarmagno | `Officine Olivetti`, the site's historic name |

Samsung SDI's is the one worth keeping. The estate polygon is tagged `Samsung`
and was refused last pass for identifying the site rather than the works; inside
it sits a building tagged **`Cella gyártás`**, which is exactly the works and
says so. The refusal was right and the thing it was holding out for existed.

**Bounding-box first, name search second**, for anything this dataset needs next.

### Three things this pipeline cannot do, and a person can

The sweep did not exhaust — it hit a wall, and the wall has three courses. All
eleven are queued in `sources/manual/MANIFEST.json`.

1. **A publisher that refuses us.** AESC answers `403` to every URL and language
   variant. Three sites.
2. **A certificate that does not match its host.** `eng.sk-on.com` presents a
   certificate for `*.skenergy.com`; `en.calb-tech.com` presents one for
   `cloudfront.net`. Two sites, both with the right document identified.
3. **The Internet Archive, which is unreachable from here.** This is the one that
   matters, because it is not a quirk. **Six of the seven cancelled projects are
   cancelled because their companies no longer exist**, and a defunct company's
   own materials survive nowhere else. Britishvolt, Italvolt, Farasis, SVOLT
   twice, Northvolt Borlänge: the perimeter requires company confirmation, the
   company is gone, and the only copy of what it said is behind a fetch this
   pipeline cannot make.

That third course is a structural fact about a dataset whose subject is failure.
It is not an argument for weakening the site rule — a cancelled project is
exactly where a loose source would do most damage, because nobody is left to
contradict it. It is an argument for the drop folder, which is why there is one.

### Two coordinates refused on judgement rather than absence

- **ACC Kaiserslautern**: the Opel works is in the basemap as six numbered
  buildings — K16, K18, K19, K25, K30, K70 — and nothing says which parcel the
  cell works was to take. Picking one would be a guess wearing a coordinate's
  clothes.
- **SK On Komárom**: the published address geocodes to a street returned as two
  segments 700 m apart.

### One row that reads oddly and is right

**GIB Šurany is `announced`** while its own coordinate polygon is tagged
`landuse=construction` and trade press reports building started in October 2025.
No company statement that construction began has been read, and under the
standing press ruling the project's own sources decide. The note on the row says
all three things so the oddity is legible rather than looking like a stale status.

---

## 11. The wire sweep

**Sixteen rows on file, 17 outstanding — 48% of a set that is now 33 rather than 34.**

The ruling that a wire-distributed release is the company's own text did most of
the work here, and it also ratified a row already written: CATL Arnstadt has cited
PR Newswire since it landed.

### It resolved two of the six defunct companies

- **Britishvolt.** The site-selection release is live on PR Newswire, 10 December
  2020: 95 hectares at Blyth, the former Blyth Power Station.
- **Italvolt.** The land-purchase release, PR Newswire, 10 September 2021: a
  million square metres at Scarmagno, 45 GWh, "where the former Olivetti factory
  stood". That is the sentence that ties the row to the `Officine Olivetti`
  polygon, which carries the site under its historic name and nothing else.
  **Italvolt is a row.**

### It refused a third out of the perimeter altogether

**Northvolt Borlänge was admitted in error and is now refused.** Northvolt's own
release of 9 September 2024 says the Kvarnsveden site was "envisioned as a new
facility for cathode active material production" and that the programme "will be
terminated". Cathode is refused by name. The first pass carried it as a cancelled
cell project on trade-press summaries that described it as both; the company's own
words settle it.

The admitted set is 33, not 34, and the cancelled population is six rather than
seven. **The sweep's most useful result was not a source but a correction.**

### And it leaves three for the Archive

- **SVOLT.** The Saarland announcement did exist on presseportal and now answers
  **410 Gone**. Nothing on any other wire, and a withdrawal is not the kind of
  thing a company wires. Two sites, one archive URL.
- **Farasis Bitterfeld.** Nothing on any wire. The only presseportal item is a
  newspaper's release about the project, which is not the company speaking.

### One coordinate that will probably never exist

**Britishvolt has a company source and no coordinate, and the reason is not that
nobody has drawn it.** The basemap carries the parcel as `Site for QTS AI Data
Center`. The site was sold in April 2024 for redevelopment; there is no longer a
battery works there to identify, and a polygon naming a data centre identifies a
data centre. This is the first candidate where the coordinate is not outstanding
but absent, and the honest record is that the row stays off file unless the
company's own materials give an address or the planning file does.

### Extremadura, entered against its own timeline

The AESC release is queued for retrieval. Two supporting sources are recorded on
the candidate now:

- **La Moncloa**, 8 July 2024 — state — the cornerstone, and nearly €1 billion in
  the first phase.
- **The June 2026 regional-government update**, currently held as an elEconomista
  relay because the Junta de Extremadura's own page has not been read: ground
  preparation only, first cells December 2028.

Read against the row: it lands as **construction**, because ground works have
begun, with a note that **four and a half years separate the cornerstone from the
first cell**. Against the staleness test it is not stale — the newest source is
three months old. Which is the useful part: staleness catches announcements that
went quiet, and this is an announcement that is being actively updated and is
still four years from a cell. Those are different failures and only one of them
has a report.

---

## 12. The permit route, the state primary, and a second report

### Britishvolt: I was wrong that the coordinate was absent

The permit route worked. Northumberland County Council application
**21/00818/FULES** — "Land At Former Power Station Site On Northern Side Of
Cambois", 92.2 hectares, validated 3 March 2021, permitted 6 July 2021 — names the
parcel exactly and is a state permitting filing, which the widened rule admits.

What failed was the fetch, twice: the committee report on `moderngov` answers
**403**, and the public-access portal answers *"This application is no longer
available for viewing."* So the coordinate is **not absent**; it is behind a
document a browser opens, and it has joined the queue as the ninth page.

The correction matters beyond this row. Last turn I read "no OpenStreetMap
feature, and a data centre on the parcel now" as evidence that no coordinate could
exist. Both facts were true and neither was the question. **The row records where
the project was sited, not what stands there now** — and the permit is a source
about the former, which is why it is in the vocabulary.

### Extremadura: one primary found, one not, and the note stands

Per the ruling, the relay is replaced where a state primary is locatable:

- **The Junta de Extremadura's own cornerstone page is located** and is now on the
  candidate beside La Moncloa's, not instead of it — two arms of the state
  reporting the same ceremony is corroboration, not duplication.
- **The environmental-authorisation line** is recorded too: the 108-hectare plot
  in the Industrial Development Park of Northern Extremadura, and a four-phase
  build to 2028 reaching 94.24 GWh, which has not been read against an AESC
  figure and is flagged as such.
- **The June 2026 update has no state primary that I could find.** The Junta's
  newsroom carries the cornerstone and a 2025 visit to AESC's Zama works and
  nothing from June 2026; the Assembly's records did not surface one. **The
  substitution note therefore stands**: the elEconomista relay is kept, and it is
  recorded as press relaying a state source rather than as the state source.

### The second report: `report_status_age.py`

Every project whose status is not terminal, ordered by how long it has held that
status, with the date it entered it. **No threshold and no verdict** — a threshold
would invent a number nobody has ruled on, and "stalled" is a conclusion about a
company's intentions from a file that knows only dates.

`TERMINAL_STATUSES` is `operating` and `cancelled`, named in `sector_map.py` with
the rest of the status groups. **`paused` is deliberately not terminal**: a paused
project can resume, and one paused for three years is what the listing is for.

**Time is counted from the transition, not the last entry**, reusing
`sector_map.entered`. A project whose history carries a later event with the
status unchanged — a permit withdrawn, a company changing hands — has not moved,
and dating it from that entry would reset the clock on exactly the projects the
listing exists to show.

It runs across every sector, not only batteries, and its first output is worth
reading: **CATL Debrecen has been `construction` for four years** on its own last
transition, and Galata has been `announced` for four years and one month. Neither
is a finding. Both are the kind of thing somebody should look at.

**Why it is separate from staleness**, which was the ruling's point and is worth
recording where the two disagree: staleness asks when somebody last *said*
anything; this asks when the project last *moved*. Navalmoral is the case that
forced the split — nothing has gone quiet, so staleness finds nothing, and four
and a half years separate the ceremony from the first cell. One report would have
had to choose which fact to be about and would have hidden the other.

---

## 13. The first two manual pages, filed

**Seventeen rows on file, 16 outstanding — 52%.** The drop folder has its first
two entries and the protocol survived contact.

### What each page settled

**Douai is a row.** The release records a start-of-production ceremony with
President Macron: *"With an annual production capacity of 10 GWh, the facility
currently supplies advanced batteries for Renault."* It also settles that the site
is a cell works rather than an assembly line — it runs "electrode production, cell
assembly, and module integration". The coordinate was already in hand.

**Sunderland is settled and still not a row.** *"Production is now officially
underway at Envision AESC's new 15.8 GWh plant"* fixes status and capacity at
company tier, and AESC's own index on the same page dates the release 2025-12-16.
**The coordinate is the blocker, and it is a refusal rather than an absence**: the
only basemap features are the International Advanced Manufacturing Park, which is
the estate, and Nissan Motor Manufacturing, which is another company's works. The
release publishes no address. That is the same refusal as Sagunto's industrial
park and Göd's estate polygon, and it should be the same refusal.

### Two things worth knowing about the retrieved pages

**Neither page carries its own date.** Sunderland's is recoverable — AESC's "More
articles" index, captured in the same print, dates it 2025-12-16 — and Douai's is
not. The Douai row therefore dates from contemporaneous reporting of the ceremony
and **says so in the note**, rather than letting a date inferred from press wear
the company source's authority.

**The live URL passes `check_links` even though `WebFetch` is refused.** 107 URLs
checked, all live, the two AESC ones included. So the 403 is specific to how this
pipeline reads a page for content, not to whether the citation resolves — which
is exactly the split the drop folder was built for: the row cites the publisher's
live URL, the gate confirms it resolves, and the quoted sentence comes from a copy
a person actually read.

### The queue is seven, and Extremadura's URL form is now known

The two retrieved pages confirm the live URL form is
`aesc-group.com/newsInfo?id=<slug>`, not the `\/news\/<slug>` path I had recorded
from search results. The dead form is replaced everywhere. **Extremadura's slug is
still unknown and is not guessed** — the queue entry carries the form and the
release title.

### One label is crowded, for the first time

`build_maps` reports `project-agratas-bridgwater narrow: envision-aesc-douai`.
That is the first crowded label in this repository, and it is a density signal
rather than a defect: the narrow layout has held 0 crowded through cement, steel
and sixteen battery sites, and the seventeenth put two works close enough on one
crop to cost a placement. The label is kept and reported, which is the rule. Worth
watching as the remaining sixteen land — if the count climbs, the crop's minimum
span or the narrow type size is the thing to revisit, not the labels.

---

## 14. Two rules written down, and a sweep that exhausted without a row

**No rows landed this pass.** Seventeen on file, unchanged. What it bought was a
rule, a chain of evidence that stops just short, and the difference between "not
found" and "not there".

### We do not draw the polygon ourselves

Written into `sector_map.LOCATION_SOURCE_TYPES` and into the geography design
note, because it is a rule about our own conduct and those only survive where the
next person looks. Where the basemap has no feature, the answer is a permit, a
published address, or the row staying off file — **never an edit to OpenStreetMap
made in order to cite it.** That edit would be circular: the coordinate's whole
claim is that somebody independent put the works there, and an edit made to be
cited turns "we believe this is the site" into "the basemap says so", which is a
stronger claim than we hold and one no reader could unpick.

It says nothing against improving OpenStreetMap. It says the two must not be done
in the same breath.

**Crowding is ratified in advance**: if narrow crowding climbs, the lever is crop
span or narrow type size. Labels stay.

### Sunderland: the permit chain runs and stops one link short

The route worked as far as evidence goes. Sunderland City Council's register gives
AESC Plant 2 as **21/01764/HE4**, varied by **23/01542/VA4**, and the address is
**1 International Drive, Sunderland SR5 3FH** — tied to AESC through a
discharge-of-condition application that names the s73 in its own description.

Every document that would carry a position refuses this pipeline: the
environmental-permit installation details and the s73 non-technical summary on
`sunderland.gov.uk`, and the Plant 3 planning statement on
`docs.planning.org.uk`. The one readable register, `planning.org.uk`, **disclaims
its own map** — "map location should not be relied on for accuracy" — which is
that aggregator being honest about geocoding an address, and is exactly the thing
the coordinate rule refuses.

And the postcode does not resolve it: at SR5 3FH on International Drive the
basemap holds the **Innovation Centre**, a different building, and the IAMP estate
polygon, which is an estate. Three pages escalated.

### "Exhausted" is now a recorded state, distinct from "outstanding"

Three candidates have a company source and were run through a full bounding-box
sweep with no result:

| Candidate | Sweep | Result |
|---|---|---|
| ElevenEs Subotica | 400 features | nothing named or operated by ElevenEs |
| SK On Komárom | 400 features | nothing for SK On or SK Battery Manufacturing |
| ACC Kaiserslautern | 96 features | the Opel works as numbered halls, nothing naming ACC |

These are not outstanding for want of looking. Their notes say so, so the next
pass does not repeat the sweep and reach the same nothing.

### One thing the wire ruling does not reach

**PR Newswire is readable here and Business Wire is not.** FREYR's operations
update of 29 November 2023 — where the Giga Arctic suspension is stated — answers
403, and so does T1 Energy's own investor site. So which wire a company happened
to use decides whether its release can be quoted, which is arbitrary and worth
knowing. It is the eleventh page in the queue.

---

## 15. Sunderland lands on a grid reference

**Eighteen rows on file, 15 outstanding — 55%.**

### The conversion is done properly and proved on every build

`sources/osgb36.py` converts British National Grid to WGS84 in the two stages
these are always confused between: the transverse Mercator inverse off the Airy
1830 ellipsoid, then a seven-parameter Helmert shift through geocentric cartesian
coordinates. It is not OSTN15 and says so — OSTN15 reaches centimetres and needs a
several-megabyte grid file; Helmert reaches a few metres, and a mark on a
two-hundred-metre works is the use Ordnance Survey publishes those parameters for.

**It is checked against the OS worked example on every build that reads a grid
reference.** Caister Water Tower, both stages: the projection inverse lands
**0.000 m** from the published OSGB36 position and the full conversion within a
tenth of a metre of the published ETRS89 one.

That check earned itself immediately. The first run appeared to be out by up to
1.5 km against reference values I had written from memory — and **the reference
values were wrong, not the code**: they were OSGB36 positions mislabelled as
WGS84, which is the exact confusion the two-stage docstring is about. Without a
published vector the natural next move is to "correct" working code until it
matches a bad number.

### The stored coordinate is recomputed, not trusted

The site carries its `grid_reference` and the gate derives latitude and longitude
from it. Verified by breaking it — moving the latitude to a plausible-looking
54.9250 fails with:

    lat/lon is (54.925, -1.4839) and the grid reference E 433175 N 558670
    converts to (54.9216, -1.4839) — one of the two has been edited alone

So the conversion cannot be done once by hand, mistyped, or quietly adjusted.

### What the row carries

E 433175, N 558670 — the centre of the block the Appendix 1 site plans put the
factory building in — converting to **54.9216 N, 1.4839 W**. The block is tied to
the works rather than to the estate by the installation's own VOC stacks being
listed inside it.

**The permit is the source of the position and no basemap feature is.** An
unnamed `landuse=construction` polygon sits 95 m away and the IAMP estate 560 m
away; both corroborate the conversion and neither places it. That distinction is
the whole of why this coordinate is admissible where the estate polygon was not.

**The discrepancy is carried, not resolved.** The 2023 filing calls the works
"Giga 1" at up to 9 GWh per annum; the December 2025 launch release calls it
"Plant 2" at 15.8 GWh. The row carries the company's current figure and the note
holds both. A permit states a consented maximum at its filing date and a launch
release states what was built, so the capacities need not agree — **but the naming
does not follow from that, and nothing read so far explains it.**

Product scope is confirmed at permit tier: electrode production, cell assembly and
module production on site.

### Two hosts added to the bot-hostile list

`sunderland.gov.uk` and `aesc-group.com` serve to a browser and 403 a datacentre
IP. `check_links` now reports rather than fails on them, on the same distinction
`sources/manual/` rests on: a 403 is a fact about how we are reaching a page, not
about whether the page is there.

**The row's quotes from the permit are second-hand until the file lands** — the
grid references are George's reading, not this pipeline's. The queue entry carries
a `drop_as` path.

---

## 16. The sweep continues, and the two halves keep landing separately

Eighteen rows, and the admitted set is **32**: InoBat Spain is refused.

### A candidate refused on the site rule for the first time

**InoBat Spain is out.** Its only company statement is a declaration of intent
signed with Valladolid on 19 October 2022, and it is explicitly conditional — the
release says InoBat was still weighing sites in the United Kingdom and would
decide "if Spain is selected". The company's newsroom has carried nothing about
Spain since; the September 2025 funding story is trade press. **A site the company
has never confirmed choosing is not a site**, which is the perimeter's own words
and the first time that clause has done the refusing.

Northvolt Borlänge went on the product rule and this goes on the site rule. Two of
the six perimeter clauses have now removed a candidate that a plausible sweep
would have carried.

### Two candidates each moved one half, and neither moved both

**EVE Power has its company source and no coordinate.** EVE's own page of 29
September 2025 names Debrecen: "The EVE Energy Hungarian factory, approved for
construction this year, is expected to be completed and put into operation in
2026." A sweep of 117 features across Debrecen returns the CATL site and nothing
in the northwest industrial zone.

**Sunwoda has its coordinate and no company-confirmed site.** The basemap names
the works in full — *Hungary Sunwoda Electronics Automotive Energy Techonology
Kft. épülő akkumulátor gyára*, at Déli út, Nyíregyháza — and Sunwoda's own release
of 10 August 2023 says only "Hungary", names no city, and describes the output as
"lithium-ion batteries and power battery systems", which does not settle the
product rule either. Site confirmation is company-only, so a basemap feature
naming the operator does not close it.

That pair is the sweep's shape in miniature: **the two halves are independent, and
finding one tells you nothing about the other.**

---

## 17. The permit arrives, and the row is rebuilt on what it says

The file is in `sources/manual/`, 70 pages, and the Sunderland row's quotes are no
longer second-hand. Reading it changed three things and confirmed the rest.

**The coordinate moved, and is better founded.** It was the centre of the block
the site plans were described as putting the building in. It is now the **centroid
of the 61 emission-point positions the report lists**, each given to the
millimetre — VOC 04 at E 433151.055, N 558774.146 and sixty more. They span E
433070–433459 by N 558555–558868, and their centroid is the one point in that
spread the document itself supports. E 433189, N 558718 → **54.9221 N, 1.4837 W**,
about 55 m from where the row stood. The stacks *are* the installation, which is
what makes their centroid a claim about the works rather than about a rectangle
somebody drew around it.

**The date is exact.** Issued 26 September 2023, not "September 2023".

**The product rule is settled at permit tier, and not by a summary.** The report
walks the Electrode Area, then "Area A – Cell Assembly", "Area B – Cell
Processing" and "Area C – Module Production". Electrodes are made and cells are
assembled on site, so this is a cell works and the module line is downstream of
that rather than instead of it. That is the distinction the perimeter's product
clause turns on, and here it is answered by the operator's own process
description.

**The naming discrepancy has a likely explanation, which is recorded as an
observation and not as a finding.** The report is titled for the "Giga 1 Car
Battery Manufacturing Facility" and consents up to 9 GWh per annum *"split across
two battery manufacturing plants separated by a central spine of offices"*. AESC's
launch release calls the works "Plant 2". Two manufacturing plants inside one Giga
1 installation is the obvious reading of how "Plant 2" arises — and **no source
read so far says so**, so the row records the phrase and stops. The capacities
still need not agree: a permit states a consented maximum at its filing date and a
launch release states what was built.

**And the position is corroborated by the document's own prose.** It places the
site "to the west of the A19, and to the south of the River Don", which the
converted coordinate agrees with — a check the grid references alone could not
give.

The queue is **eight**.

---

## 18. The decision point

Nineteen rows on file of 32 admitted — **59%** — and both acts read. This is the
stop brief 6 §10 set: nothing ships or draws before George's read.

### The overview is not honest yet, and my judgement is not to draw it

Thirteen candidates are outstanding. Six of them are in the manual queue and
cannot move without a browser. What an overview drawn today would omit:

- **Envision AESC Extremadura**, a site whose cornerstone the Spanish prime
  minister laid.
- **SK On Iváncsa**, 30 GWh, and **SK On Komárom**, both operating.
- **CALB Sines**, 15 GWh, whose coordinate is already in hand.
- **Four of the six cancelled projects** — SVOLT twice, Farasis, Britishvolt.

The last of those is the one that decides it. This sector's defining fact is how
much of it died, and the docket has been saying so since the first pass: a third
of the admitted set is stopped or dead. An overview that draws two of six
cancelled projects and none of the four whose companies no longer exist would
show a sector in better health than it is in — and it would do it silently,
because a reader cannot see what is not drawn.

The standfirst's "on file and not drawn" clause was built for cancelled projects
the perimeter deliberately excludes. It cannot carry candidates missing because
nobody could reach a webpage.

### What the acts wait on

Twenty-two measure rows, both declared preliminary readings. The Battery
Regulation's 16 and the fleet standards' 6, including the four
`creates_demand_for` edges — the first this graph has carried.

### What is not built, and is not started

Brief items 6, 7 and 8, and the materials half of item 4:

- **Money model.** No funding rows for batteries. IPCEI decisions, Innovation
  Fund awards, state aid approvals and announced project finance are all
  unstarted. The compliance-cost side is settled and stays empty, for the reason
  Article 7 gives.
- **Exposure.** The exclusion is decided and not yet written into a page.
- **Prose slots.** `sector_names` already carries batteries. `transition_notes`,
  `sector_orientation`, `sector_lead` and the ecosystem description carry cement
  and steel and nothing else.
- **CRMA Annex I material links** from the technology nodes.
- **Bottlenecks and the ranking**, which is what `hasMap` reads. Until
  `bottlenecks.json` carries batteries rows and `build_importance` writes
  `importance/batsol.json`, the tile keeps opening the holding page. Project
  crops already build and all nineteen are on disk.

---

## 19. The ranking is completed, the materials land, and one sweep exhausts

Ten measures enter the batteries sector view, five strategic raw materials and a
sixth that is deliberately not one land as material nodes, and the FREYR
coordinate stops being blocked and starts being absent.

### The ranking now has something to rank

`batsol` had a ranking with nothing in its sector view: 174 measures reach the
sector on the register's own reading, and **none of them was in the view**,
because the view is entered on money or on a named constraint and batteries has
no money model and had no bottleneck edges. The page's tile opened a ranking of
nothing.

**Ten measures are now in, on ten edges across the four constraints.** Every edge
carries the register's own wording as evidence, quoted verbatim from the field it
names:

- **Committing capacity against uncertain vehicle demand** — `fleet:TGT-2035` at
  1.0, `fleet:TGT-2030` and `fleet:PREM-01` at 0.5. The 2035 target is the only
  provision that removes the demand question rather than answering it, and the
  premium is weighted below the targets it enforces because it is money out of a
  carmaker rather than money into a cell maker.
- **European cells against imported cells** — `iaa:LM-15a` at 1.0, `iaa:LM-26a`
  and `nzia:SCH-01` at 0.5. LM-15a is the only provision in the register that
  names battery storage in an origin requirement. None of the three lowers a
  European cost per kWh; they close part of the demand a cheaper cell can
  compete for, which is a different claim and is what the notes say.
- **Ramping a cell line to yield** — `ets:FND-03` alone, at 0.5. **Nothing in the
  register reaches scrap rates.** The Innovation Fund reaches the constraint's
  financial deadline and not the constraint, and the single edge is the honest
  shape of that.
- **Cell capacity without the materials behind it** — `crma:CBEN-01` at 1.0,
  `crma:CBEN-02` and `crma:CSP-02` at 0.5.

**No edge is a `worsens` edge, and that is a finding rather than an omission.**
Cement and steel both carry one: `ets:CBAM-01` raises a European producer's cost
before the fix it pays for exists. Batteries has no equivalent, because every
duty in the Batteries Regulation bites at the point a battery is *placed on the
market* — so it falls on an imported cell exactly as it falls on a European one.
A compliance cost that both sides carry does not widen the gap this sector's
defining constraint is about.

### A decision the ranking cannot make for itself, and I have not made

With no money model, the ranking sorts on linkage weight alone, and **three
measures tie at 1.0**: `crma:CBEN-01`, `fleet:TGT-2035`, `iaa:LM-15a`. The tie
breaks on measure id, so the CRMA benchmark ranks first and the 2035 target
second — alphabetically. The fleet standards' own reading note says of TGT-2035:
*"Every gigafactory row in the projects dataset exists because somebody believes
this sentence."* If that is right, the top of this ranking is in the wrong order
for a reason that has nothing to do with the data.

`data/transition/overrides.json` exists for exactly this and takes a rank and a
reason. **Left for George**: either an override putting TGT-2035 first, or a
ruling that alphabetical tie-breaking is honest where nothing distinguishes the
weights.

### Ten labels, and the batteries product vocabulary

Nine measures had no diagram label and no plain block, and one — `ets:FND-03` —
had blocks for cement and steel and none for batteries. All ten are written. The
Innovation Fund's batteries block **states no figure**: the three Battery Call
grants carry null amounts, so `{money_awarded}` cannot be filled, and asking for
it would have failed the build by design. The sentence says the Commission
published no figure instead, which is the fact.

`sector_map.SECTOR_PRODUCT_WORDS` gains a `batsol` entry — battery, batteries,
cell, cathode, anode, gigafactory — so a shared block that names a battery now
fails the gate the way one naming clinker always has. Both plural spellings are
listed because the check matches a word plus an optional `s`.

### Five strategic raw materials, and the one that is on the list for not being on it

`crma_annex_i` has been a field on every material since the layer was written and
has been null on every row in it. It is now populated: **lithium, cobalt, nickel,
manganese and natural graphite**, each carrying the Annex I entry in the annex's
own words with the article it sits in.

Four of the five carry the qualifier *battery grade* in Annex I itself, which is
the Union stating the link this dataset was going to have to argue for. Graphite
is the row that says least and marks the most: the anode side of the dependence,
listed as strategic by the Union, with **no source read here stating where a
European line buys it** — and anode works are outside the perimeter, so this
dataset holds none.

**Sodium is on the platform for what it removes.** It is in no annex, and that is
the whole of its interest: a `substitutes` edge to lithium, evidenced from the
sodium-ion route's own description, is the layer saying that a chemistry can
answer a supply constraint by leaving the listed metal out. It is the first
substitution edge in the materials layer — the slag one the brief asked for is
still unwritten for want of a source.

Every consumption edge is to a **technology and not to a sector**, on the
membership rule hydrogen is held to: no site here is sourced as consuming a
stated tonnage of any of them.

### FREYR: the sweep exhausted, and the coordinate is absent rather than blocked

Overpass answered today. Three queries: a name search for Freyr, FREYR, Giga
Arctic and T1 Energy; a bounding-box sweep of Mo Industripark returning **309
industrial and construction features, of which five carry a name** — a former
ironworks, three power stations, and the estate; and an operator and brand search
over a box roughly 90 km by 100 km. **Nothing names the works.** T1 Energy's own
site says "Mo i Rana, Norway" and publishes no address.

So the estate polygon is all there is, and it is refused on the same rule that
refused IAMP and Parc Sagunt II. The candidate's note now says the sweep ran
rather than that Overpass was unavailable, which is the difference between a
coordinate nobody has looked for and one **no admissible source states**.

### The acts come back ratified, with two changes

George ratified `sources/battery_acts_review.md` on 5 September 2026. Everything
stands as written, **including all four demand edges and the two deliberate
non-edges**, and two things move.

**`CF-01`'s dates were one date where the act gives four.** Art. 7(1), second
subparagraph, staggers the carbon footprint declaration by battery category —
electric vehicle batteries at 18 February 2025 or 12 months after the delegated
and implementing acts, rechargeable industrial batteries except those with
exclusively external storage at 18 February 2026 or 18 months, LMT batteries at
18 August 2028 or 18 months, and rechargeable industrial batteries with external
storage at 18 August 2030 or 18 months. The row carried the electric-vehicle date
alone, which said the duty reaches an LMT battery three and a half years before it
does. Checked against the act's own text and now carried in full.

**The fleet targets say they are under legislative question.** COM(2025) 995 of
16 December 2025 — CELEX 52025PC0995, verified against CELLAR rather than taken
from memory — proposes moving the 2035 target from a 100% reduction to 90% with
compensation credits, averaging the 2030 target over a period, moving the van
target to 40%, and changing the premium formula. It is under Parliament and
Council review. `TGT-2030` and `TGT-2035` each gain a sentence: *a Commission
proposal to revise this target is under legislative review; this row reads the
law in force.* The proposal goes on watch in `sources/queued.json` and **is not
extracted**: a proposal is not the law, and every row here is the law in force.

That matters more here than it would on another sector. Three of the ten measures
in the batteries ranking are fleet rows, and the highest-weighted edge on the
demand constraint is `TGT-2035`. The sentence is what stops a reader taking the
sector's foundation for settled.

### The cement correction, and the practice it now stands on

The Innovation Fund retro-check moved cement's committed money from €421 million
to €655 million, and the page had been printing the old figure. Corrections to
printed figures now carry a dated note **where the figure is printed**:
`data/transition/corrections.json` holds the practice and the entry, the schema
gate validates it and lists every correction on every run, and the Opportunity
section renders it under the total it corrects.

The anchor is a closed vocabulary — `sector_map.CORRECTABLE_FIGURES` — because a
note pinned to a figure no surface renders is a note nobody is told about, and a
typo would produce exactly that in silence.

### The money model's boundary

Ruled and written into the method prose at the top of `funding.json`: the model
holds **capital committed to building an admitted works**, and research and pilot
funding is out. The two findings that forced it — €14.8 million of Horizon 2020
money at 3D Dunkirk, about €12 million at H2Future Linz — are recorded there
rather than landed as rows, and `ROADMAP.md` carries an entry for the
research-funding layer that could hold them properly.

### What this does not change

**The draw hold stands.** Twenty of 34 candidates are on file, fourteen are
outstanding, and four of six cancelled projects are unreachable, and a completed ranking is not an answer to
that. The hold is what stops a better ranking from becoming a worse picture.

---

## 20. Four pages arrive by hand, and three of them become rows

Twenty-three rows on file of 34 candidates — **68%** — and eleven outstanding.

### CALB Sines, on the composite standard

The second row to stand on it, and the first outside Hungary. **CALB's own release
names a country and no city**: "On February 24, local time, construction commenced
on CALB's Portugal facility, which will be a zero-carbon AI gigafactory with
delivery expected in 2027." No town, no lot, no capacity — the same shape as
Sunwoda's "Hungary", and the reason the ordinary company-only standard cannot
confirm this site.

The three legs, all cited on the row:

- **company** — the release above, retrieved by hand and filed.
- **state** — the Portuguese Government's own briefing room, 24 February 2025:
  *"O Ministro da Economia, Pedro Reis, esteve presente na cerimónia de lançamento
  do projeto de uma nova fábrica de baterias de lítio em Sines da CALB."* It names
  the town, the company and the product, and puts its economy minister at the
  ceremony the company's release describes without locating. **AICEP announced the
  same investment and is named rather than cited**: the state leg is the
  Government's publication, not its investment agency's summary of it — the same
  line HIPA fell on at Nyíregyháza.
- **basemap** — a plot under construction carrying the operator's own name:
  *Construção da Unidade Industrial de Baterias de Lítio da CALB*, official name
  *Calb Europe, S.A.*, at ZILS Lote 1A3.3, Sines.

**Capacity is state tier and is not absent**, which is where this row differs from
Sunwoda: the Government states 15 GWh. It writes it without a period, so the row
records GWh per year and says in a note that the "per year" is this platform's
reading and not the source's.

### SK On on its own published addresses, twice

The parcel line was the payload, as expected, and it turned into two rows rather
than one.

**Iváncsa.** SK On publishes the works in two forms — `HRSZ 99/48 Iváncsa 2454`
on its global places-of-business page, and `H-2454 Iváncsa, SK út 1.` on its
Hungarian site — and the row's position walks back to the second. **The parcel
places nothing here**: HRSZ 99/48 geocodes to the settlement and this pipeline has
no cadastral source that would resolve it. The industrial buildings 300 to 800
metres north along SK út are unnamed, so no polygon places the works either. What
places it is the address, which is the coordinate rule's second source type doing
the work it was written for.

**Komárom.** Two published addresses, neither resolving to a house number, and a
basemap building named `SK Battery` standing on the first of the two streets. The
point is that building; what admits it is the address. **One point for what the
state calls two plants**, said on the row rather than split on an address nobody
can resolve.

**Status splits the two rows.** Komárom is `operating` on the Hungarian
government's own sentence — *"A cég első két tengerentúli gyára Komáromban
működik"*, the company's first two overseas plants operate in Komárom — and the
row records that this is the earliest sourced statement that it runs, not the date
it started. Iváncsa stops at `construction`: trade reporting describes mass
production from 2024 at 30 GWh, and **no source this pipeline can read states a
production start**, so the row does not claim one and joins the status-age report.
Capacity is absent on both.

### The two SVOLT captures do not become rows, and the reason is a coordinate

Both company sources are now in hand and both are strong. Überherrn is the
stronger: *"In Überherrn on 'Linslerfeld', a battery cell factory with 24 GWh of
installed capacity in the final expansion stage is to be built"* — site, cell
product and capacity in one sentence. Lauchhammer gives the site as the former
Vestas rotor-blade plant taken over at the end of August 2022, and **states no
capacity**, so that half joins the standing report the moment the row lands.

Neither lands, and the constraint is the same on both: **nothing in the basemap
names either works**. A name sweep for Vestas and SVOLT across Brandenburg returns
nothing; a sweep of every industrial and construction feature at Lauchhammer
returns thirty-six named works and none of them this one; nothing anywhere is
named Linslerfeld, and the Überherrn works was never built, so there is no works
to name — what stands on that land now is a solar park. The company publishes no
site address, only its Frankfurt office.

So they move from *no company source* to *company source in hand, coordinate
outstanding*, which is EVE Power's state: the two halves are independent, and
having one tells you nothing about the other. **The `archived: true` citation form
is endorsed for when they land** — the publisher's copy is gone with the company,
so the row will cite the capture URL with the filed page as its snapshot rather
than citing a live URL nobody can open.

### A "blocked" source that was not blocked

Both hosts behind the manual queue's certificate entries — `en.calb-tech.com` and
`eng.sk-on.com` — **serve over plain http**. The certificate does not match the
host, so https fails; nothing else does. `check_links` reaches both, and the filed
copies are byte-for-byte what the URLs serve.

Worth writing down because the queue entry said *"certificate does not match the
host"* and the working assumption around it was that the page could not be read
here at all. Those are different failures and only one of them needs a person.
**The filed copies stay** — they are what was actually read, and the row cites the
publisher's URL either way — but the next certificate mismatch gets an http
attempt before it gets a queue entry.

---

## 21. The tie is broken by a rule, and the permit route is tried on both SVOLT sites

### Demand edges become the tie-break, and the pin is not needed

The batteries ranking had three measures tied at 1.0 and broke the tie on
measure id, which put a raw-materials benchmark above the 2035 fleet target.
**Neither an override nor the alphabet decides it now.** `creates_demand_for` —
an edge the register has carried since the fleet standards landed — is a fourth
component of the ranking, and the rule is general:

> A measure carrying `creates_demand_for` into the sector ranks above a tied peer
> without one.

It is written into the method note at the top of `build_importance.py`, where the
other three components are, and it is **a tie-break and not a lift**, on the same
principle attention runs under: a demand edge does not put a measure into the
sector view and does not move it past a measure with more money or more linkage.
It orders equals.

Above attention, deliberately. A demand edge is a reading of the measure's own
text; attention is a count of other people talking about it.

**What it does to the ranking**: `fleet:TGT-2035` first, `crma:CBEN-01` second,
`iaa:LM-15a` third — and within the 0.5 group, the two remaining fleet rows rise
above the CRMA and NZIA rows they were tied with. Cement and steel do not move at
all: no measure reaching either carries a demand edge, so every row there gains
the field `false` and nothing reorders. That is the test of a general rule — it
had to be able to do nothing.

The editorial pin in `overrides.json` was the fallback and is not used. A rule
computed from an edge the register already carries decides the next tie the same
way without anybody remembering to.

### Überherrn: the permit route works, and stops one step short

The plan exists and it is exactly what was hoped for. A **vorhabenbezogener
Bebauungsplan "Industriegebiet Linsler Feld"**, adopted by the Überherrn
municipal council on 7 March 2024 — the vote the company's own capture documents
— legally binding from September 2024, and written for this works in the
authority's own words: *"der die planungsrechtlichen Voraussetzungen für die
Ansiedlung einer Batteriezellfabrik schaffen sollte"*.

It gives three things the company source could not:

- **The site at authority tier**, not merely at company tier.
- **The scale**: a plan area of about 99 hectares, a works area of about 52, a
  building height of 30 m and a stack of 34.
- **The cancellation, stated by the authority**. The council resolved on 7 May
  2026 to repeal the plan, and the notice says *"Das Vorhaben wird nicht mehr
  umgesetzt"* — the project will not be implemented. The area falls back to
  `Außenbereich`. This is far better than press for the status event when the row
  lands.

**And it does not give a coordinate.** Unlike Sunderland's permit there is no grid
reference anywhere in it: the summary declaration lists no parcels for the works,
the repeal notice locates the area verbally — *"östlich der Siedlungslage von
Überherrn zwischen der B 269, der L 168 und der L 279"* — and the 1:5.000
Lageplan is a cadastral map whose text layer carries parcel numbers and no
coordinate grid. Placing it from three bounding roads would be **drawing the
polygon ourselves**, which is the rule this dataset refused at Sunderland and
will not now break for a better-documented site.

The next thing to try is named on the candidate: the plan's own Planzeichnung, or
the Geltungsbereich geometry from the state map service the repeal notice itself
points at.

### Lauchhammer: the permit route finds nothing, which is itself consistent

No BImSchG procedure for SVOLT at Lauchhammer appears in the Landesamt für
Umwelt's public notices or Brandenburg's UVP portal. That is what a works bought
and never converted looks like in a permitting system: the company took over an
existing plant and never applied to change what it does.

The only address for the former Vestas rotor-blade works comes from commercial
directories and a county business listing. **A directory is none of the three
coordinate source types** — not a polygon somebody drew, not an address the
operator published, not a parcel a permit names — and the row will not stand on
one. SVOLT publishes only its Frankfurt office.

### So both settle into EVE Power's state, with more on file than when they entered it

Company source in hand, coordinate outstanding. What changed is that the reason is
now specific and written down per site, with the next document named, rather than
"no basemap feature".

---

## 22. A Spanish permit states its own coordinates, and a second projection is written

Twenty-four rows on file of 34 candidates — **71%** — and ten outstanding.

### The company source arrives, and it is the ordinary standard

AESC's first-stone release of 8 July 2024, from the Internet Archive because the
rebuilt site has removed it. **It names the town**, so this row stands on the
ordinary company standard and not on the composite one: *"Today, Monday, July 8,
marked the groundbreaking ceremony of AESC's future gigafactory for batteries in
Navalmoral de la Mata, Cáceres."* Product is company tier and specific — *"advanced
Lithium Iron Phosphate (LFP) batteries at scale"* — and so is the money, over a
billion euros in the first phase and up to 900 direct jobs. The attendance list,
Sánchez and Guardiola and the mayor, corroborates La Moncloa's record of the same
ceremony from the other side.

**The capture filed is 2 October 2024**, not the 19 September one the retrieval
was described against; the Wayback bar on the saved copy says so and the row cites
the capture that is actually on disk. Cited `archived: true` with the file as its
snapshot, on the SVOLT pattern.

### And then the permit did what the SVOLT permits could not

The Extremadura environmental authorisation of 17 May 2023, in the Diario Oficial,
**states the installation's own coordinates**:

> Las coordenadas geográficas representativas de la instalación son: X: 285.333;
> Y: 4.421.360; ETRS89, huso 30.

It also names the cadastral parcel, `I-67` in the Polígono Industrial
Expacionavalmoral, on 1 088 211 m², and gives the four-phase capacity: 94,24 GWh a
year at the end of phase four in 2028. This is the Sunderland shape exactly — a
filing that gives a projected position to the metre — in a country whose permits
use a different projection.

**So a second projection is written.** `sources/utm.py` inverts ETRS89 UTM to
WGS84, and the row's latitude and longitude are recomputed from the easting and
northing on every build, exactly as Sunderland's are from its National Grid
reference. Verified by breaking it: moving the latitude to a plausible 39.9200
fails with *"lat/lon is (39.92, -5.5116) and the grid reference E 285333 N 4421360
converts to (39.9152, -5.5116) — one of the two has been edited alone"*.

**One stage rather than two**, and that is the whole difference from the British
case. OSGB36 needs a projection inverse and a Helmert datum shift because Airy
1830 sits a hundred metres from WGS84; ETRS89 is a WGS84-family datum and the
drift since 1989 is tens of centimetres, two orders of magnitude below what four
decimal places store. Adding a datum shift would be pretending to a precision the
source does not have.

**How a conversion is checked when nobody publishes a test vector for it.** The
Ordnance Survey publishes a worked example and Spain does not, so the new module's
transverse Mercator inverse is written generically — it takes the ellipsoid and
the projection parameters — and is run with the National Grid's parameters against
the OS's own Caister Water Tower position. That is a published test point proving
the series, borrowed from the one country that publishes one. Beside it: a forward
projection that has to invert the inverse to a millimetre across three zones, and
the definitional identity that the central meridian is the false easting and the
equator is zero. The systems a permit may quote are a closed table in the schema
gate, so a projection nobody has implemented is a coordinate the build refuses
rather than one it approximates.

**The estate corroborates and does not place.** The point falls 152 m outside the
mapped edge of the `Expacio Navalmoral` polygon — the park the permit names — which
is a check on the arithmetic and nothing more. An estate is refused as a position
here, as it was at Mo i Rana, IAMP and Parc Sagunt II.

### Two dates that disagree, and both are carried

The 2024 release says the plant *"is scheduled to begin production in 2026"*. The
June 2026 update — the Junta's secretaria general de Economía before the
Extremadura Assembly, relayed by press because no Assembly record of the session
was found — puts assembly finished in September 2027, construction concluded in
November 2027 and **first cells in December 2028**, at 977 million euros and 900
jobs. In the same session an opposition deputy said that two years after the
ceremony there is *"la primera piedra y nada más"*. The row's status is what none
of them disputes — ground was broken, no cell has been made — and **the
four-and-a-half-year gap between the ceremony and the first cell is carried as
the fact rather than resolved by taking the newest number in silence**.

**The relay was changed on the way in.** The locator the candidate carried
answers 403 to this pipeline, and a citation nobody here can open is not one this
row will stand on; a second outlet reporting the same Assembly session serves and
is cited instead. It is used for the timetable it relays and **not for dates it
states itself**: it puts the first stone in July 2022, where the company's own
release and La Moncloa both put it in July 2024.

The same discipline on the money: AESC says *over* one billion euros in the first
phase, La Moncloa says *nearly* one billion. Neither is stored as a number,
because they are not the same claim and nothing read here settles it.

---

## Stopping here

Twenty-four rows on file of 34 candidates, ten outstanding. What is left, in
order:

1. **Coordinates**, still the binding constraint: both SVOLT sites, ACC
   Kaiserslautern, FREYR and Farasis. The Extremadura permit is the pattern to
   try first on each — a state filing that states its own position — and it is
   now a route this pipeline can read in two projections.
2. **The four pages still parked for a browser**, in `sources/manual/MANIFEST.json`:
   Britishvolt's committee report, Farasis from the Internet Archive, and two
   Sunderland corroborations that nothing waits on.
3. **Prose slots**: `transition_notes`, `sector_orientation`, `sector_lead` and the
   ecosystem description carry cement and steel and nothing else, and the batteries
   blocks that exist are drafts awaiting review.
4. **The exposure exclusion**, decided and not yet written into a page.
5. **The draw hold**, which only George lifts, and only on a judgement that the
   retrieval gap has closed far enough for the overview to be honest.

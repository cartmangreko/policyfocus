# Cement and CCS — the census, and where it stopped first

**Brief 8, sector 2.** The procedure is hydrogen's and batteries': a recognised external
list, every entry worked to a class, a gap table that sums to the list's own entry count,
and drift measured against a second list.

**This file was written when the pass could not start, and the top of it is kept that
way.** Sections 1 to 5 are the record of the block. Section 6 onwards is the census that
ran once the block cleared on 14 September 2026. A stop that leaves no record behind is a
stop somebody repeats, and a stop edited out once it clears is a register telling itself
the work was always easy.

---

## 1. The perimeter is already written

`sources/scope.md`, "Sector perimeters", landed in pull request #59. Restated here only so
a reader of the docket is not sent looking:

- **Cement** — a capture project at a cement works, any capture technology including
  oxyfuel with capture, company-confirmed. Any other investment at a cement works is
  refused with the clause **"cement, no capture"**.
- **CCS** — CO₂ transport and storage infrastructure: stores, pipelines, shipping
  terminals, hubs. Capture at works in industries outside the four sectors is refused with
  **the industry named in the clause** — "capture, refinery", "capture, waste-to-energy" —
  rather than one clause covering all of them, because those entries are read later for the
  supplier nodes and a refusal recording only "out of perimeter" throws away the one fact
  that makes the later read possible.

**One clause was added to the cement perimeter by this census**, on 14 September 2026, and
it is D79 in §8 below.

## 2. What this register already holds

Eleven rows, and they are the population the gap is measured against. Eight cement, three
CCS:

| sector | rows |
|---|---|
| cement | brevik-ccs, gezero-geseke, anrav-devnya, go4zero-obourg, carbon2business-lagerdorf, slite-ccs, ifestos-kamari, k6-lumbres |
| ccs | northern-lights, galata-co2-storage, prinos-co2-storage |

**Four of the eight cement rows carry a stated capacity and four do not**, which is the
count `check_capacity_clause` prints beside any capacity-weighted figure. **None of the
three CCS rows carries one.**

## 3. Where it stopped, and why that was not the brief's stop clause

Both lists were behind an **affirmative acceptance**: a step where a person agrees to
something. Neither was behind a term that forbids the snapshot.

| list | role | barrier |
|---|---|---|
| IEA CCUS Projects Database | first list | **account login** — `IEA CCUS Projects Database 2026.xlsx`, updated 27/03/2026 |
| Global CCS Institute / CO2RE | second list | **click-through acceptance**, then an `app.powerbi.com` embed with no data behind it |

**The brief's stop clause is "terms that forbid the snapshot", and these terms do not.**
A hash-referenced snapshot holds an identity rather than a copy: it redistributes nothing
and needs no grant of rights, so it is permitted under the strictest reading of either
publisher's terms. What stopped the pass is that passing a login or ticking an agreement
**binds the account holder**, and that is not a signature this pipeline may write.

### The routes that were tried before concluding

Recorded so nobody repeats them:

- `api.iea.org/ccus` answers **200 with 333,510 bytes** — and it is the **CCUS legal and
  regulatory database**, 89 rows keyed `Base legislation`, `Description`, `Issue`, `Link`,
  `Region`, `Regulation or law`. It is not the projects database. **A 200 is not the file
  you wanted**, and this is the second time that lesson has cost a pass an hour.
- `api.iea.org/ccus/projects`, `/ccus/project`, `/ccusprojects`, `/ccus/projects-database`
  and `/ccus-projects-database/ccus` — **404**.
- `api.iea.org/sdmx/dataflow` — **404**. `sdmx.iea.org` and `data.iea.org` — do not resolve.
- The CCUS Projects Explorer page exposes only `A17.PUBLIC_API_ENDPOINT='https://api.iea.org'`
  and no dataset path.
- `co2re.co/FacilityData` carries **no `.json`, `.csv` or `.xlsx` URL and no `/api` path**.
  Its "Terms" and "Data Use Policy" links both point at the same Terms of Use page, which
  **was** read.

## 4. The IEA describes this file two ways, and both are recorded

**A disagreement inside one publisher**, held rather than resolved, in
`sources/benchmark_snapshots.json`:

- **The product page for this very file** states `Licence CC BY 4.0`, and prints a CC BY
  citation string for it.
- **The general Terms and Conditions** exclude "Standalone datasets, data explorers and
  databases" from the CC BY 4.0 Open Use Terms.

**This register does not decide between two statements by one speaker**, and it does not
have to: a hash-referenced snapshot is permitted on either reading, and the stricter
reading is what the pass works to. The bytes stay out of the repository,
`sources/cache/ccs/` is gitignored except its index, and entries are cited by the
publisher's own identifier.

## 5. What unblocked it

George retrieved the IEA file past the account login on 14 September 2026 and dropped it at
the path the queue named. Its identity is in `sources/cache/ccs/index.json` and in
`sources/benchmark_snapshots.json`:

    sources/cache/ccs/iea_ccus_projects_2026.xlsx
    618,023 bytes
    sha256 9afde5c0ba8f8b3f314ebc44eed7bdaa0a54d479be70c242369e696857272bd8

**CO2RE did not unblock and will not.** §7.

---

## 6. The census, 14 September 2026

**The list.** Sheet `DRAFT CCUS Projects Database`, 1110 project rows worldwide, 34
columns, announcements as of February 2026. The census is of the **425 entries the
publisher's own `Region` column calls Europe**. That the subset is the publisher's and not
this register's is the only reason a gap table over them may claim it sums to the list — a
denominator chosen by the counter is the mirror D77 was written about.

**Cement is complete. Transport and storage is not**, and goes on its own branch after this
one merges. The gap table below is the whole list; the 133 CO₂ T&S entries stand in it as
`not searched`, which is the class that is a defect and is printed by name on every run.

### The gap table

| class | entries |
|---|---|
| held | 12 |
| admitted | 26 |
| named not admitted | 4 |
| searched none found | 4 |
| perimeter exclusion | 246 |
| not searched | 133 |
| **TOTAL** | **425** |

`sources/build_cement_ccs_benchmark.py` exits non-zero if it stops summing to 425.

### Cement, the 42 entries, closed

| class | entries |
|---|---|
| held | 8 |
| admitted | 26 |
| named not admitted | 4 |
| searched none found | 4 |
| **TOTAL** | **42** |

**All eight held rows matched on company AND works**, never on a name stem, and every match
is printed on each run for confirmation. The four rows that carry a capacity agree exactly
with the list's announced figure — Brevik 0.4, Geseke 0.7, Devnya 0.8, Lägerdorf 1.2 Mt
CO₂/yr — which is a corroboration and is recorded as one.

### The 246 the perimeter refuses are DERIVED, not transcribed

An entry whose sector the perimeter does not hold is refused mechanically on the
publisher's own `Subsector`, in `perimeter_clause()`. Hand-listing 246 refusals would have
invited a typo to become a class. The largest are waste-to-energy (63), hydrogen or ammonia
(35), power from bioenergy (25), refining (23) and power from gas (22). **Each names its
industry**, because the supplier sweep reads them later.

**Ten are refused on geography and a reader should see which.** The IEA's European region
carries ten Icelandic entries — Carbfix, Climeworks Orca and Mammoth, and the three Coda
terminal phases. Iceland is not on the named Europe list in scope.md, so they are out.
**The list is closed and this is the rule applying, not a gap in it.** The IEA spells the
country two ways in one column, "Iceland" (7) and "Island" (3); both are recorded as the
publisher's variant and neither is silently normalised, because a register that edits a
publisher's spelling is editing the list it counts.

## 7. The second list is dropped, and the refusal has a name

**CO2RE — READABLE, NOT ENUMERABLE.**

George read `co2re.co/FacilityData` in a browser on 14 September 2026 at 08:36, Region
EUROPE, Location All, Facility Status All, sorted ascending by Operational Year. The capture
is filed at `sources/manual/co2re-facilities--europe-filter-2026-09-14.png` with a manifest
entry, and `check_manual_sources` gates it in both directions.

**The capture shows the earlier description was both too harsh and too kind.** The table is
not unreadable: it renders seven columns — Country, Name, Facility Status, Operational Year,
Industry, Facility Type, Capture Capacity (Max; mtpa) — and rows a person can read straight
off, from MOL Szank Field CO2-EOR Site (HUN, 1992) to Eni Ravenna Phase 1 (ITA, 2024). It is
an `app.powerbi.com` publish-to-web embed with export disabled.

**What it never does is state how many rows the Europe filter returns.** The gap table is
gated on summing to the list's own entry count, and this list does not publish one. So the
refusal is not "a 403", not "an empty body" and not "a click-through" — those were the
barriers, and they are not the reason. The reason is that **a list which shows its rows
without ever stating their number cannot be a denominator**, and a census measured against
it could never prove it was complete.

This is a new refusal class for this register, and the first that is about counting rather
than about reading.

## 8. DECISIONS

**D79. THE CEMENT PERIMETER HAS NO PILOT CLAUSE, AND NOW SAYS SO.** Ruled 14 September
2026, on a question this census raised over four entries and did not decide for itself. A
capture project at a cement works is in perimeter **at any scale**; the register does not
convert and does not rank. The owner's own designation — "pilot", "demonstration",
"semi-industrial", "phase 1" — is kept on the row as a stated attribute with its speaker,
and is not a refusal. Written into `sources/scope.md`, Sector perimeters, Cement. Touches
IEA 202 (LEILAC 2, Hanover), 539 (CycloneCC, Rüdersdorf), 1359 (catch4climate,
Mergelstetten) and 1459 (ECCO2-LH, Carboneras), all four moved from `held for ruling` to
`admitted`. The question and its ruling stay in `sources/cement_ccs_questions.json`, because
a reader who finds the clause is entitled to see the entries that made somebody write it.

**D80. A CAPACITY IS NEVER ANNUALISED TO MAKE PROJECTS COMPARABLE.** CEMEX's CycloneCC unit
at Rüdersdorf is stated by its technology partner at **100 tonnes of CO₂ per day** and the
row carries it per day. Turning that into a yearly figure would be this register inventing
an operating pattern nobody stated, and it would do it in the direction that makes a small
project look like a comparable one. Follows D79 and is recorded separately because it binds
every sector.

**D81. A CANCELLATION IS A STOP EVENT ONLY FROM THE OWNER OR THE CONSORTIUM.** Ruled 14
September 2026. The IEA carries IEA 1459, ECCO2-LH at Carboneras, as `Cancelled`, and
nothing read here is Holcim saying so. The row lands on its announcement and takes **no
stopped `status_history` event**; the list's status is recorded against it as a
`benchmark_claim` with its speaker and the vintage it was made in. Rule 17 says a project
that vanishes from a database is a project whose failure nobody counts — and the converse is
this decision: a database saying a project failed is not the project's owner saying so.

**D82. NEITHER IEA CAPACITY COLUMN IS EVER WRITTEN ONTO A ROW.** The workbook publishes
`Announced capacity (Mt CO2/yr)` and `Estimated capacity by IEA (Mt CO2/yr)`, and the second
is the IEA's **own computation** from plant details through the conversion factors printed
on the Definitions tab — 0.9105 kg CO₂/nm³ H₂, a 90 % capture rate, a 95 % plant capacity
factor. The brief says no capacity conversion and capacity at the unit stated, so an
admitted row takes the figure its owner states or it carries none. **Twelve of the 26
admitted cement rows carry no capacity**, and that count is printed beside every
capacity-weighted figure the sector produces. IEA 1065 (Cauldon) shows why the distinction
matters: the entry carries **no announced capacity at all**, only the IEA's estimate of 0.54
Mt, and a pass that did not separate the columns would have read a publisher's arithmetic as
an owner's claim.

**D83. THE IEA'S OWN REFERENCE COLUMNS ARE NOT RELIABLE PER ENTRY, AND EVERY ONE WAS READ.**
The workbook carries `Ref 1..7` per project and the Notes tab says "All public references
are available by project". Three read here point at a different project altogether: **IEA
1018** (Acorn Isle of Grain to Peterhead shipping) cites
`netl.doe.gov/coal/carbon-storage/atlas/secarb`, a United States atlas; **IEA 460** (Northern
Endurance phase 3) cites `gov.louisiana.gov`; **IEA 775** (the Norwegian Poseidon storage
licence) cites an article about Perenco's unrelated **UK** Poseidon project, a different
project with the same name. The references are where a search STARTS and never what it
concludes on. Recorded as a finding about the list because a later pass treating the column
as evidence would inherit the error silently.

**D84. A BOUND IS NOT A NUMBER.** NEXE states capture of "> 700 thousand t CO₂ per year" at
Našice and the IEA announces 0.739 Mt. The row carries the bound as the owner made it.
Converting a lower bound into the point value that satisfies it is inventing precision, and
it would make the register's figure look like an independent measurement of the list's.

**D85. TWO SPEAKERS COUNTING DIFFERENT SUBSTANCES IS NOT A DISAGREEMENT ABOUT A NUMBER.**
Holcim states 2 million tonnes of **near-zero cement** a year at Câmpulung; the IEA announces
1 Mt of **CO₂**. Both are recorded with the substance named on each, so a reader comparing
them does not read one as the other. The same shape appears at Sagunto, where the owner
states 560,000 t of CO₂ **avoided** and the list states 0.6 Mt of capture **capacity**.

**D86. A FILENAME IS THE PUBLISHER'S FILING AND NOT THE DOCUMENT'S DATELINE.** The OLYMPUS
FEED release is served at a path ending `…feed-contract-for-olympus-ccs-project-12-12-2024_vs2.pdf`
and its first line reads **"Athens, 19 December 2024"**. The row takes the 19th. This is the
same shape as the Ørsted case in scope.md — a URL path reading `/news/2022/12/` which is the
publisher's filing — and it is recorded separately because a filename is more tempting than a
path: it carries a full date, it looks authoritative, and a dating pass that trusted it would
have been a week out with no way to notice. **Every dateline in this pass was read off the
document**, not off its URL.

A second case in the same pass ran the other way. The first-pass extractor returned
2020-06-24 for the C2PAT release from deep in the body; the raw markup carries **no date
metadata of any kind**, so that number was a stray and not a dateline. The row is dated
`not_after` 2026-09-14 instead. **A date found in a document is not the same thing as a
document's dateline**, and only reading tells the two apart.

**D87. AN EVENT MAY NOW BE AN UPPER BOUND, AND TWELVE ROWS RECORD A SILENCE AS A
TECHNOLOGY.** Two vocabulary changes this census forced, both ruled 14 September 2026.

`not_after` joins `EVENT_DATE_PRECISIONS`, with the meaning it already had on a source: the
event is dated by the copy on file, as a bound. Three admitted rows — C2PAT Mannersdorf,
CO2LLECT Rüdersdorf, Go4ECOPlanet Kujawy — have an announcement that is real, read and
quoted, and an owner document that carries no dateline. The old vocabulary offered a false
`day` or no event at all. Display renders it **"by 14 September 2026"**.

And `ccs-capture-unspecified` enters the technology registry as a **placeholder**: twelve of
the twenty-six admitted cement projects have an owner who confirms the works, the project and
often the tonnage and never says how the CO₂ is to be captured. Filing them under
post-combustion because it is the commonest retrofit would have attributed a method to twelve
real works on this register's guess. **It is excluded from every technology count, tile and
diagram node** — a reader meeting it on a page would read it as a thing somebody is building —
and it keeps `co2-transport-storage` as a dependency, so those rows still owe an answer about
where the tonne goes. Thirteen rows carry what their owners said; OLYMPUS carries two ids
because HERACLES names two. LEILAC 2 gets `ccs-direct-separation`, a third method the registry
did not have, sourced to Calix's own design description.

**D88. A READABLE REFERENCE ABOUT A DIFFERENT PROJECT IS THE WORST KIND, AND FIVE ENTRIES
CARRY ONE.** D83 recorded that the IEA's `Ref` columns are not reliable per entry, on three
cases that announce themselves — a United States atlas, the Louisiana governor's office, an
article about a different Poseidon. **This is the form that does not announce itself.** The
reference answers 200, carries thousands of characters of real prose about a real CO₂
project, and never mentions the entry it is filed against:

- **IEA 654, 655, 656** — the three C Zero phases (Air Liquide, Lhoist, Duisport) cite
  `carbonbridge.de`, which is **IEA 1471**, a different project at Bremerhaven, and reads as
  22,000 characters of CCS prose.
- **IEA 679, 1361** — both NL CCS Direct Injection phases (Eni, EBN, OneDyas) cite
  `benelux.rwe.com`, which is about **NoordKaap**, a different network project.

All five are `searched none found`. **NO ADMISSION EVER RESTS ON A REFERENCE THAT DOES NOT
NAME THE PROJECT**, and the rule has to be stated because the failure is invisible to every
check this register runs: `check_links` calls the page live because it is, the fetch cache
records a healthy 200 with a high character count, and a reader skimming for CCS vocabulary
finds it in abundance. The only thing that catches it is reading the page for the project's
name. That is now what the reading step is for.

**The near-name family this belongs to.** Rule 30 says record the identifier, never guess
the join; D83 says a reference is where a search starts. D88 is the third face of the same
thing: **a source is evidence for an entry only if it names that entry.** Resemblance
between a reference and a project — shared vocabulary, shared sector, a plausible domain —
proposes nothing at all.

## 9. Disagreements, held and not resolved

Six, in `sources/cement_ccs_benchmark.json`:

| object | field | the two speakers |
|---|---|---|
| slite-ccs | status | Heidelberg Materials: paused. IEA: Planned, operation 2032. |
| accsion-aalborg | capacity | Aalborg Portland: up to 1.5 Mt. IEA: 1.4 Mt. |
| go4ecoplanet-kujawy | date | Holcim Polska: capture starts 2027. IEA: FID 2027, operation 2031. |
| co2ntessa-nasice | capacity | NEXE: > 700,000 t/yr. IEA: 0.739 Mt/yr. |
| hoever-ccs | capacity | Holcim: ~90 % of the works' ~500,000 t emissions. IEA: 0.8 Mt announced. |
| cpt01-campulung | capacity | Holcim: 2 Mt of cement. IEA: 1 Mt of CO₂. |

**The Höver pair is the one to look at twice**: the list's announced capacity for the
project, 0.8 Mt, **exceeds the works' own stated total annual emissions**, about 0.5 Mt.
Nothing here resolves it and no capture capacity is written onto the row.

## 10. Reference debts — four pairs, none merged

Rule 30: record the identifier, never guess the join.

1. **IEA 561 (VAIA HyNoVi) and IEA 1461 (VAIA)** — one Vicat works, Montalieu-Vercieu, two
   entries. HyNoVi captures 40 % into methanol (2021); VAIA captures 1.2 Mt, nearly 100 %,
   into storage (2025). Vicat never states the relation. 1461 is admitted; 561 is named and
   not admitted and opens no second row.
2. **IEA 539 and IEA 540** — one CEMEX works, Rüdersdorf, two capture projects at different
   scales with different partners. **Both admitted**, because both are capture projects at a
   cement works and neither owner says the one is a stage of the other.
3. **IEA 1459 and IEA 1478** — one Holcim España works, Carboneras. A 2020 pilot the list
   calls cancelled and a 2025 entry it calls planned. Whether the second replaces the first
   is stated nowhere read.
4. **IEA 202 and IEA 556 — the Hanover debt, and it is the one that matters.** Two entries
   name a cement works at Hanover under **two different owners**. Under the ruling of 14
   September 2026 the debt closes as two works only if an owner states a relocation, and **no
   owner does**. What the search added instead is four dated location statements:

   - **2021-02-01, HeidelbergCement**: LEILAC 2 decided for "the HeidelbergCement cement
     plant in Hanover, Germany".
   - **2025-02-26, Leilac (Calix)**, via the Internet Archive because `leilac.com` answers
     403 to a declared reader: Leilac-2 "will be retrofitted into a Heidelberg Materials
     plant" — **the page names no site at all.** By 2025 the technology partner had stopped
     naming the host works.
   - **2026-09-14, Heidelberg Materials Deutschland**, own list of its German cement works:
     ten named — Burglengenfeld, Ennigerloh, Geseke, **Hannover**, Königs Wusterhausen,
     Leimen, Lengfurt, Mainz, Paderborn, Schelklingen. Höver is not among them. The same
     site's CCUS project list names GeZero-Geseke, CAP2U-Lengfurt and
     catch4climate-Mergelstetten and **does not carry LEILAC 2**.
   - **2026-08-21, Holcim Deutschland**: its own works is "Zementwerk Höver, Niedersachsen".

   Each company names a works of its own and neither names the other's. **Calling those two
   places different would be this register reading a map rather than a source, and calling
   them the same would be merging two owners' works on a resemblance.** Both entries are
   admitted as separate rows and the debt is carried on both. What would close it: a
   Heidelberg statement giving LEILAC 2's host works after 2021, or a permit for either works
   naming its operator and its place together.

## 11. Drift — not measurable for this sector

**A fact about what this register holds, not a finding about the list.** Drift needs two
vintages and there is one. The IEA product page's Schedule tab records past releases — April
2025, March 2024, March 2023 — and its Data sets tab offers exactly one file, the 2026
edition; no past-edition URL exists in the page markup. If the logged-in download view offers
a past-editions selector, the 2025 edition would make drift measurable, and nothing in this
pass can see behind the login.

The second list, which drift would otherwise have been measured against, is dropped for the
reason in §7.

## 12. The unread list

Pages a declared reader could not read, by refusal class:

| class | pages |
|---|---|
| 403 | `leilac.com` (project page and root), `globalcement.com` (four items), `enmin.lrv.lt`, `agg-net.com`, `carbonherald.com` |
| 404 | `coolplanettech.com` press PDFs (two), `padeswoodccs.co.uk` brochure |
| 200, empty body | `cemex.es` and `cemex.es/-/somzero`, `gateway.euronext.com` |
| URLError | `greencem.dk` |

**`cemex.es` answering 200 with a body carrying no readable text is the class that costs a
row.** IEA 1277, SOMZERO CO₂, is `searched none found` because CEMEX is the only named
partner and its Spanish site will not speak to a declared reader. That is the hydrogen lesson
again — a link checker calls that page live, because it is.

## 13. Transport and storage, 15 September 2026 — the sector closes

**The gap table now has no defect class.** `not searched` is zero: every one of the
publisher's 425 European entries is in exactly one class.

| class | entries |
|---|---|
| held | 12 |
| admitted | 83 |
| named not admitted | 23 |
| searched none found | 25 |
| unreadable | 12 |
| perimeter exclusion | 270 |
| **TOTAL** | **425** |

**83 admitted entries over 66 works** — 26 cement rows, merged in #61, and **40 new CCS
rows** from 57 transport-and-storage entries.

### The list splits a project and the register does not

The IEA carries a project by leg, by phase and by operation year. The register holds **one
row per works**, and every entry still takes its own class so the table keeps summing to the
publisher's count:

| works | list entries |
|---|---|
| Porthos | 2 — offshore T&S and onshore transport |
| Aramis | 3 — storage phase 1, storage phase 2, transport phase 1 |
| Viking CCS | 3 phases |
| Sullom Voe hub | 3, by operation year: 2033, 2038, 2040 |
| STARFISH / Havstjerne | 3, under two of the IEA's own hub names |
| Norne | 5 entries over **4 works** — two stores, two terminals |
| Acorn, Antwerp@C, CO2next, Bifrost, Greensand, Grenaa, Liverpool Bay | 2 each |

**Norne is the one that is not a phase split.** Five entries, four works: the Gassum and
Havnsø stores are different places from the Aalborg and Kalundborg terminals, and Kalundborg
is one terminal the IEA carries twice at 4 and 8 Mt. Splitting on phase would have merged
two stores; splitting on place is what the register's rule already says.

### Twenty-three licences leave, and two regulators drew the line first

The Q2 ruling reaches beyond the ten Norwegian entries it was asked about: Perenco's UK
Poseidon in three phases, EnQuest, Orion in two, the three Tellus entries **whose names are
their licence numbers** (CS020, CS021, CS022), Humberside, Thorning, and both Smeaheia
phases. Every excluded entry keeps its licensee's stated capacity and timing.

**The Danish Energy Agency states the test in one sentence**: exploration licence first, and
"if the area is shown to be suitable for environmentally safe storage of CO₂, the licensee
can apply for a storage permit". **And Sodir's own legend distinguishes `EL`, an exploitation
licence, from `EXL`, an exploration licence** — every Norwegian entry here is an EXL.

**Sullom Voe splits the way the ruling asks.** Veri Energy holds four carbon storage
licences and a terminal. The **terminal is admitted**; the licences are not.

**Smeaheia is the hard case and it is excluded.** Equinor has acquired 3D seismic and drilled
two appraisal wells under the licence — which is finding out whether the store is there,
not a plan to build one. It is the store the Wilhelmshaven chain is drawn to, and it stays
out until its licensee says it is a store.

### Enhanced oil recovery, ruled 15 September 2026

**D89. EOR IS REFUSED WITH THE CLAUSE "enhanced oil recovery", AND THE TEST IS THE
PUBLISHER'S COLUMN.** The perimeter holds infrastructure whose purpose is permanent storage;
EOR injects CO₂ in order to produce oil. The IEA's `Fate of carbon` already separates
`Dedicated storage` from `EOR`, so the boundary is checkable by anybody holding the same
file. Written into `sources/scope.md`, Sector perimeters, CCS.

It reaches **one** entry here, and a working one: **Žutica South, Operational since 2020**,
the register's only European CO₂ T&S entry with an EOR fate. The clause removes an
installation that runs, not a plan. **INA/MOL's own words stay on the entry** — "permanent
disposal of 2.9 billion m3 CO2 or 5.4 million tonnes" — because the ruling takes the
publisher's column as the test and does not contradict the operator about what its injection
achieves.

**The second EOR entry keeps the clause it already had.** IEA 669, MOL Szank field, is
capture at a natural gas processing plant and is refused with "capture, natural gas
processing". A refusal in this sector names the **industry**, because those entries are read
later for the supplier nodes; overwriting that with a fate would throw the industry away.

**Both appear in the second list too**, and it is the only use this register has made of
CO2RE: the filed capture shows "MOL Szank Field CO2-EOR Site (HUN), Operational, 1992" and
"INA/MOL CO2 EOR Croatia (HRV), Operational, 2014" among its ten visible European rows.

### Northern Endurance is named and not admitted, and it is queued

The entry most likely to be read as an error. The IEA's own reference 404s; the surviving
cluster site describes **NZT Power**, a gas-fired station with capture that this perimeter
refuses anyway; `nzt.co.uk` answers 200 with an empty body; phase 2's reference is a dead Eni
link and phase 3's is the Louisiana governor's office. BP, Equinor and TotalEnergies are the
partners and none of their own pages could be read — **Equinor's partnership page answers 200
with an empty body**, which is the class a link checker cannot see.

All three partner pages are in `sources/manual/MANIFEST.json` under `wanted`, with the
outcome each gave. **The class stands until somebody reads them in a browser.**

### What the sector could not read

25 entries searched with nothing found, 12 unreadable. Beyond the five D88 cases:

- **Two entries carry no reference at all** — Gismarvik CO₂ hub, and **OCAP**, which has
  moved CO₂ to Dutch greenhouses since 2005 and is the oldest operational entry in the
  European set. Eighteen European entries have an empty `Ref` column.
- **An owner lost with its company.** `neptuneenergy.com` no longer answers since Eni's
  acquisition, so the one owner page cited for L10 is gone with the publisher.
- **A video is not a source this reader can quote**, and the IEA cites one for both Protos
  phases.
- **The EU record says "tbd" twice** for ORLEN's Baltic Sea Storage — the clearest statement
  in this census that a project exists and its size does not.

### Figures that are not capacities, kept off their rows

Eni's **330 Mt** is what the Hewett field holds, not a yearly rate. The Bluestreak **30 Mt**
is a market estimate the IEA carries as an announced capacity. Greensand's **0.5-1 Mt/yr** is
a stated *potential*. The Peak cluster's **3 Mt** is avoided emissions for a whole cluster.
CinfraCap's **4 Mt** is what an investigation examined the possibility of handling. None is
written onto a row.

**Highway58 is the counter-example and the reason the distinction is worth drawing**: Pipe58
states "20 MtCO₂ annual capacity for phase 1" on its own site, and that figure **is** on the
row.

## 14. What is still to come on this branch

- **The 40 CCS rows themselves.** The classification is complete and gated; writing the rows
  is the same job the 26 cement rows were — datelines read page by page, `not_after` where a
  document carries none, capacities at the owner's unit, storage blocks, retrospective
  status histories, then the derived-artefact chain. They land as a second commit on this
  branch before it merges. The sector holds 3 CCS rows today and will hold 43.
- **Northern Endurance**, until its three partner pages are read in a browser. Queued.
- **Drift**, for the reason in §11: one vintage, and the product page offers only the 2026
  file.
- **The reverse gap is still not measured by this table.** `galata-co2-storage` is carried by
  no IEA entry, and the table counts the list's entries rather than the register's rows.

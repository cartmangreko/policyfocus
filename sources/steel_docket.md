# Steel — two lists, and what each of them cannot see

**Written 18 September 2026, when the second list arrived.** The census of the first list
ran from 14 to 16 September; this docket is written after the second, because the second
list changed what the first one's table means and found a defect in it.

The register's own rules for this sector are in `sources/scope.md`, "Steel", and are not
repeated here: four legs, company-confirmed, in the EU, the United Kingdom, Norway or
Switzerland, **no tonnage threshold**, with three refusal clauses. This file is the record
of applying them to two outside lists.

## 1. What this register already holds

Eight steel rows, landed before either census: `stegra-boden`, `tkh2steel-duisburg`,
`salcos-salzgitter`, `am-bremen-eisenhuettenstadt`, `hybrit-pilot-lulea`, `3d-dunkirk`,
`greentec-donawitz`, `greentec-linz`.

**Six of the eight are in the first list; two cannot be.** `hybrit-pilot-lulea` is a pilot
below GEM's floor, and `3d-dunkirk` is carbon capture on a blast furnace — a different fact
at a works the census does carry for its DRI announcement. Both absences are recorded in
`ROW_ABSENCE` in `sources/build_steel_benchmark.py`, and an absence that is NOT recorded
there fails the gate. That check did not exist until this pass; D-S3 is why.

## 2. The first list — GEM, and the floor it brings with it

GEM's Global Iron and Steel Tracker, June 2026 (V1), CC BY 4.0 by the file's own About tab.
1,293 plants worldwide; **132 in the perimeter's Europe**, on GEM's own `Country/area`
column. Every one was searched against its owner's documents before any was classed — 956
fetches — and GEM's forward status was treated as a claim throughout, never as a class.

**THE FLOOR IS GEM'S AND IT BOUNDS EVERY NUMBER IN THAT TABLE.** GEM's About tab: "This
database only includes plants with crude iron/steelmaking capacity of five hundred thousand
tonnes per annum (0.5 mtpa) and greater." The steel perimeter sets no threshold on purpose:
a small DRI module and a large one are the same kind of fact about a works leaving the blast
furnace, and a threshold drops the early ones, which are disproportionately the ones that
stop. So the first list can never be read as coverage of European steel.

| class | entries |
|---|---|
| held | 7 |
| admitted | 20 |
| named not admitted | 5 |
| searched none found | 10 |
| perimeter exclusion | 90 |
| **TOTAL** | **132** |

## 3. The second list — LeadIT, and why this sector has one

LeadIT's Green Steel Tracker, version 2026-09-04, CC BY, a research collaboration of the
Leadership Group for Industry Transition and the Stockholm Environment Institute. 161
project rows worldwide; 68 in LeadIT's Europe; **65 in the perimeter's Europe**. Türkiye
(2) and Russia (1) are in LeadIT's Europe and not in this perimeter's, and they are counted
out rather than dropped quietly.

**IT SETS NO CAPACITY FLOOR.** That is the whole reason it is read: it is the only way to
say anything about what GEM's 0.5 mtpa cannot see. The first-list pass said so before this
one ran, which is the order that makes the claim worth anything.

| class | entries |
|---|---|
| held | 20 |
| admitted | 20 |
| named not admitted | 8 |
| searched none found | 4 |
| perimeter exclusion | 13 |
| **TOTAL** | **65** |

**THE TWO TABLES COUNT DIFFERENT THINGS AND MUST NOT BE ADDED.** GEM's rows are PLANTS and
LeadIT's are PROJECTS: the 52 LeadIT entries that sit at a GEM plant sit at only 31 distinct
plants, because LeadIT carries several projects at one works. A class in the second table is
inherited from the first wherever the two meet, so those 52 re-class nothing; only the 13
GEM does not carry were classed here.

## 4. The drift between the two lists

Drift in this sector is **between two publishers on one day**, not between two vintages of
one list. It answers a different question from the hydrogen drift table: not what a
publisher changed its mind about, but what each publisher can see.

| | |
|---|---|
| GEM's European plants | 132 |
| LeadIT's European entries (perimeter) | 65 |
| LeadIT entries at a GEM plant | 52, at 31 distinct plants |
| — joined on LeadIT's own `GEM Plant ID` | 49 |
| — joined by hand, by works | 3 |
| LeadIT entries GEM does not carry | 13 |
| GEM plants LeadIT does not carry | 101 |
| In perimeter from GEM, and LeadIT silent on | 6 of 27 |

**WHAT THE FLOOR HIDES IS ONE ADMISSION AND TWELVE REFUSALS.** Of the 13 entries GEM cannot
carry: one admitted, four named not admitted, eight perimeter exclusions. The admission is
**HyIron's GEiSt at Lingen** — a hydrogen direct-reduction plant confirmed by its owner on
its own site, at a scale GEM's threshold excludes by construction. One works in 197 list
entries is a small yield, and it is the honest one: the second list's value here is mostly
that it lets the first list's silence be read.

**AND LEADIT IS SILENT ON SIX WORKS THIS REGISTER HOLDS OR ADMITS** — ArcelorMittal
Duisburg, GravitHy Kristinestad, Hüttenwerke Krupp Mannesmann, Liberty Steel Dunkerque,
Saarstahl Völklingen and Tata Steel Port Talbot. The last is the largest single steel
investment in the United Kingdom. A second list is not a check on the first; it is a second
partial view.

## 5. DECISIONS

**D-S1. THE DIACRITIC BUG: TWENTY OF THE LARGEST WORKS IN EUROPE WERE NEVER REQUESTED, AND
THE INDEX SAID THEY HAD BEEN.** On 15 September 2026 the census fetched the gem.wiki page
of all 132 European plants and believed it had. Twenty returned nothing. `urllib` encodes
its request line as ASCII and refuses a URL with a diacritic in it, so **every works whose
name carries one was never requested at all**: SSAB Luleå and Oxelösund, which are the
HYBRIT sites; ArcelorMittal Kraków, Dąbrowa Górnicza and Eisenhüttenstadt; Liepājas
Metalurgs; Hüttenwerke Krupp Mannesmann; Saarstahl Völklingen; U. S. Steel Košice.

**THE SHAPE OF THE FAILURE IS WORSE THAN THE FAILURE.** The index recorded a fetch that had
happened and returned nothing, so the plant looked searched and was not. Had the census
classed on that state it would have reported "searched, none found" on the very works where
the transition is happening, **and the gap table would have summed to 132 perfectly while
being wrong**. A gate that checks a total cannot see this; only a gate that checks what a
record means can.

**THE SELECTION IS THE POINT.** The twenty were not a random twenty. Diacritics cluster in
Nordic, German, Polish, Baltic and Slovak plant names, which is where the large integrated
works and the whole of HYBRIT are. **A character-set bug had become a geographic bias**, and
nothing in the pass would have shown it.

**THE FIX, IN THREE PARTS.**

  - *The reader.* `sources/steel_search.py` percent-encodes the path and the query and
    punycodes the host, and records the URL as the publisher writes it so a reader can still
    follow it. A non-ASCII URL is still a URL.
  - *The gate.* `sources/check_fetch_records.py` draws the distinction the index could not:
    **a publisher refusal is an answer and may stand with no body** — a 403, a 404, a DNS
    failure, a timeout, a 200 with an empty body — **and a client-side failure is not**.
    UnicodeEncodeError, InvalidURL and their kin mean the request never left this machine
    and say nothing whatever about the publisher. A record with no body that names one of
    those is a defect and the gate blocks on it.
  - *The audit.* Every earlier index was re-read under the same rule.

**AND THE CLASS WAS STILL OPEN WHEN THIS PASS STARTED, WHICH IS THE PART WORTH RECORDING.**
The fix went into the steel reader and the other readers were left as they were. On 18
September 2026 `sources/ccs_search.py` and `sources/battery_search.py` still sent the URL
unencoded and are corrected here with the same three lines. **`sources/hydrogen_search.py`
has the same defect and is not on this branch**: it carries nine records whose outcome is
`InvalidURL`, all from a space in a path on `topsectorenergie.nl`, and the pass that read
them wrote "answered with nothing" against four entries — a publisher recorded as silent
that was never asked. The gate's index list also named four indexes and omitted the largest;
`hydrogen` is added to it here, and reports honestly that the file is not on this branch.

**Fixing the one place a defect was found does not fix it.** That is the same lesson the
truncation ruling reached from the other direction, and this is what it looks like in a
fetcher.

**D-S2. THE SECOND LIST IS IN, AND IT EARNED ITS PLACE ONCE.** The cement census recorded
its second list as DROPPED, with a reason — CO2RE renders rows a person can read and never
states how many there are, and a gap table is gated on summing to the list's own count.
LeadIT states its rows, carries its own identifier and publishes a `GEM Plant ID` column, so
this sector's second list is in and its table sums to 65.

**What it found is one admission and a way of reading the first table.** HyIron's GEiSt at
Lingen is a DRI plant GEM's floor cannot carry, confirmed by its owner: "The project GEiSt
(German for 'Green Iron for the steel Industry') pilots the technology in Lingen, Germany,
in cooperation with RWE and Benteler." **One in 197 is the yield, and it is reported as one
rather than dressed up**, because the reason to run a second list is not the hit rate — it
is that without it no number from the first list can be called coverage.

**D-S3. THE CENSUS REPORTED NO ROUTE CHANGE AT A WORKS THIS REGISTER ALREADY HELD, AND THE
SECOND LIST IS WHAT FOUND IT.** `ArcelorMittal Bremen steel plant` and `ArcelorMittal
Eisenhüttenstadt steel plant` were classed `searched none found` — "an integrated works with
no announced route change" — while `am-bremen-eisenhuettenstadt` sat in
`data/transition/projects.json` as a cancelled row. LeadIT's GST-036 and GST-037 qualify
both works at status Cancelled, which is what sent this pass back to look.

**THE SEARCH WAS NOT WRONG AND THE CLASS WAS.** ArcelorMittal's own pages carry nothing
about the conversion; the row itself says so — "No primary source for the earlier
announcement has been read". What was missing is that **a census of an outside list never
asked what the register already holds**. Seven entries are reclassed to `held`: the two
Bremen works, the three whose proposed row id already existed, and **voestalpine Donawitz
and Linz, whose proposed ids `voestalpine-donawitz` and `voestalpine-linz` would have landed
a second copy of `greentec-donawitz` and `greentec-linz`**.

**The gate is the row audit** in `build_steel_benchmark.py`: every steel row must be pointed
at by a census entry or have its absence recorded in `ROW_ABSENCE`, and an entry pointing at
an existing row must be classed `held`. `held` means the register already holds this works —
the same sense the hydrogen gap table uses in "duplicate of a held row".

**D-S4. LEADIT'S CROSS-REFERENCE TO GEM IS INCOMPLETE, AND THE THREE MISSING LINKS WERE
FOUND BY READING, NOT BY FOLDING NAMES.** 49 of the 65 carry a `GEM Plant ID` that lands in
GEM's 132. Three more are at plants GEM does carry and LeadIT has not linked — SSAB Raahe,
Stegra's Spanish plant and Outokumpu Tornio — and each was matched **by hand, by works, one
at a time**, with the method recorded on the line.

**The temptation here is exactly the one D-S1 is about.** Matching "Outukumpu Biocoke Green
Stainless Steel" to "Outokumpu Tornio steel plant" by folding the strings would have worked;
it would also have matched things it should not, and this sector's names are full of the
characters that make a folded match look clever — Hüttenwerke, Völklingen, Luleå, Gijón,
Maizières-lès-Metz. **A publisher's key, then a person; never a normaliser.**

**D-S5. A 200 WITH THE SAME BODY IS THE SAME REFUSAL AS A 200 WITH AN EMPTY ONE.**
`marcegaglia.com` answers a declared reader with 200 and 21,704 characters on every path
tried — the front page, the English and Italian press rooms, and a project URL — and the
body is identical each time. It is a single-page application that renders its content in a
browser, so a declared reader can reach the site and can reach nothing in it.

`scope.md` already calls a 200 with an empty body a refusal. **This is the same failure
wearing a different number**, and it is recorded against the URLs rather than against the
project: Marcegaglia's AdriatiCO2 at Ravenna would be an announced DRI plant if the owner's
own words could be read, and until they are the entry is `named not admitted` — the same
place Port Talbot sat under S3 until the right domain was tried.

**D-S6. LEADIT'S `Qualified for Tracker` IS ITS EDITORIAL TEST AND IS NEVER THIS REGISTER'S
CLASS.** The two disagree about seven of the 52 works they share. LeadIT qualifies projects
at four works this register searched and found nothing at, at one it refused by the
perimeter, and at one it named and did not admit. Each is a **lead, not a correction**: a
list is not a company, and the perimeter asks for the company.

The seven are printed on every run by `build_steel_second_list.py` and are the first place a
later pass should look.

**D-S7. THE FLOOR IS A PROPERTY OF A LIST, AND SO IS QUALIFICATION.** GEM sees plants at 0.5
mtpa and above. LeadIT sees projects of any size that pass its own test — its methodology
tracks renewable hydrogen, molten oxide electrolysis, electrowinning and electric smelting
reduction. **Neither is the population.** Every coverage figure in this docket names which
list it came from, and no figure in it is offered as coverage of European steel.

**D-S8. THE HYDROGEN HALF OF D-S1 IS CLOSED, AND CLOSING IT TURNED A BUILD RED FIRST.**
D-S1 reported `hydrogen_search.py` as carrying the same defect on another branch, with nine
`InvalidURL` records to show for it. Merging main brought that branch's work here, and with
it the hydrogen index — so the gate this pass wrote began failing on a defect this pass had
only described. **That is the gate working.** The reader is corrected, the two URLs behind
all nine records were re-fetched, and the nine are marked `defect` with `superseded_by`
rather than deleted, because this register does not delete fetches (D42).

**WHAT THE PUBLISHER ACTUALLY SAID IS NOT WHAT FOUR ENTRIES RECORDED.** The URL is a TKI
Gas overview PDF whose path carries spaces; the request never left. Asked properly,
`topsectorenergie.nl` answers **403** — it refuses a declared reader, which is an answer —
and the Wayback capture of 26 January 2022 returns 200 whose 10,128 bytes are the archive's
own banner around a PDF that yields no text. The 2023 population test had written "answered
with nothing" against refs 1115, 1116 and 1118. **The classes do not move and the reasons
do**: no readable document still stands, on evidence rather than on a request that was
never made.

**D-S9. THE BUILD-TIME RULE WAS APPLIED BEFORE IT COULD FAIL, WHICH IS THE ONLY TIME THAT
HAS HAPPENED.** Main's #66 settled that a step wired into `npm run build` may read tracked
files only. Three of this branch's steps were already in prebuild when that arrived and one
of them, `build_leadit_entries.py`, opens an 8.8 MB workbook with `openpyxl` — neither of
which exists in the build image. It is now in the pre-push chain; `sources/leadit_entries.json`
is a tracked derived file carrying the workbook's SHA-256 and byte count; `--check` rebuilds
all 65 entries from the workbook locally and refuses a mismatch; and
`build_steel_second_list.py` verifies the recorded hash against `benchmark_snapshots.json`
**inside the build**, which is the half of the question a machine without the bytes can
still ask. `check_fetch_records.py` and `build_steel_benchmark.py` stay in prebuild: every
file they read, the five cache `index.json` included, is tracked.

**Verified rather than reasoned about**: all 37 prebuild steps were run against a tree
holding only `git ls-files` content with `openpyxl` blocked. The three steel steps pass.

## 6. Disagreements, held and not resolved

  - **Stegra's Spanish plant.** This register admits it; LeadIT's GST-040 carries it as
    "Paused or postponed" with the reason "No new updates, project has been assumed
    postponed indefinitely". A list assuming a postponement is not an owner stating one, and
    the class does not move.
  - **SSAB Raahe.** GEM shows a forward unit; the register has it `named not admitted`;
    LeadIT carries two entries for it, one qualified and cancelled, one not qualified.
  - **The seven of D-S6**, each with LeadIT's own status against this register's class.

## 7. Questions

`sources/steel_questions.json` — S1 and S2 are rule questions on the perimeter, S3 and S4
are a search question and a correction, and this pass adds **S5** (does the perimeter reach
a primary route that is neither DRI nor EAF — SIDERWIN is electrowinning, and LeadIT tracks
that class) and **S6** (is a single-page application that serves one body on every path a
refusal, and should the reading rules name it).

# The confirmation ladder across five sectors — brief 11

**The ladder was built for hydrogen and this is the pass that takes it to the other four.**
The rules are in `sources/scope.md`, "The confirmation ladder". This file records what had
to be decided to apply them outside the sector they were written in, and it is written in
the order the work was done: the freeze first, then the populations, then the reading.

`D-L1` … `D-L7` are in `sources/hydrogen_docket.md` and are corrections to the hydrogen
scorer. `D-B1` … `D-B19` are brief 12's, also there. This file starts at **D-A1**.

## Rulings of 19 September 2026, written before anything was scored

**D-A1. THE SIX RUNG TESTS ARE BYTE-IDENTICAL TO THE D-B1 FREEZE, AND THIS PASS ADDS
READINGS RATHER THAN TESTS.** D-B1 froze the rung tests at commit
`a9542fe28f93eac7f66a3050070af6db93684e7e` and recorded the SHA-256 of the whole
`## The confirmation ladder` section. That section has since gained subsections — brief
12's work and this one's — so its hash has moved, and a hash that is expected to move
proves nothing.

**So the freeze is re-anchored on the block that must not move.** `### The six rungs`, the
2,324 bytes that state the six tests, hashes to
`47b0859d80b3e44cb2711e9011cccce2e4832390b26817f073b8294530dccea9` both at `a9542fe` and at
HEAD. It is unchanged. `check_ladder.py` recomputes it on every build and fails on a
difference, so the freeze is now enforced rather than asserted — the same move #68 made
about the build-image rule, for the same reason: prose does not fail a build.

**WHAT A READING IS ALLOWED TO DO.** Rung 2 asks for a capacity "in any unit, recorded as
stated" and rung 6 for an input edge at `firmness: contract`. Neither sentence names a
sector, and both need one to be filled in from a battery row or a storage row. The readings
say **which unit a sector's owners use** and **which dependency is the one rung 6 is about**
— a cement works with a firm electricity contract and no capture technology provider must
not clear a rung that is about its capture plant. **A reading may not make a rung easier or
harder to clear.** Where one would, it is a proposed test and goes to
`sources/ladder_questions.json`.

**AND THE READINGS WERE WRITTEN BEFORE A SINGLE CELL WAS SCORED**, in the first commit of
this branch, for the reason D-B1 gives: an instrument tuned after its answer is visible is
not an instrument. **That commit is `fbac46f`**, the first on this branch; it touches
`sources/scope.md` and this file and nothing else, and it was pushed before the populations
were built.

## Rulings of 19 September 2026, after the populations were built and before they were read

**D-A2. FIVE POPULATIONS, AND EACH IS KEYED BY ITS PUBLISHER'S OWN IDENTIFIER WHERE THERE
IS ONE.** 644 entries: hydrogen 245, batteries 69, cement 42, transport and storage 141,
steel 147. `sources/ladder_population.py` builds four of them and prints an identity per
sector that a reader can check the arithmetic of; the gate refuses a population whose
classes do not sum to it.

**BATTERIES HAS NO PUBLISHER IDENTIFIER AND THAT IS THE FINDING.** Neither Transport &
Environment's 2024 annex nor Battery-News numbers its rows; both publish a label. So a
battery entry is keyed by the register row where the census matched one — which is the only
thing that makes the union of the two lists computable — and by `<list>:<label>` where it
did not. **The two lists name the same works 22 times and those are one entry, not two**:
50 + 38 − 22 = 66, plus the 3 rows neither list carries = 69.

**CEMENT AND TRANSPORT AND STORAGE COME OFF ONE FILE AND ARE TWO POPULATIONS**, split on
the publisher's own `Subsector` column exactly as the census split them: `Cement` is one,
and `CO2 T&S`, `CO2 transport` and `CO2 storage` are the other. **The IEA file's other 243
European rows are in neither**, and they are counted rather than dropped: 425 = 42 + 140 +
243. A ladder over a refinery's capture unit would be a ladder over a sector this register
does not hold.

**D-A3. HYDROGEN IS NOT RESCORED HERE, AND THE FIRST VERSION OF THIS FILE THAT DID RESCORE
IT WAS WRONG IN A WAY WORTH KEEPING.** `build_ladder_all.py` first called
`build_ladder.build()` for hydrogen. That function classifies perimeter exclusions through
`report_benchmark_gap.perimeter_exclusions_by_ref()`, which reads the IEA benchmark
workbook — **and the workbook is gitignored**. On a machine without it the classifier
returns nothing, all 53 hydrogen perimeter exclusions come out as `none found`, and they
are SCORED — at zero. The table read 224 hydrogen entries scored where the committed one
says 171, and **every hydrogen pass rate in the cross-sector table was computed over the
wrong denominator**.

**It would also never have run on the build server**, for the same reason and by the rule
#66 wrote: a build-time gate reads tracked files only. So hydrogen's lines are **read from
the committed `sources/ladder/hydrogen.csv`**, which is the tracked derived file, and
`build_ladder.py --check` goes on recomputing it from the workbook where the workbook is.
The reconciliation the brief asks for is then a real comparison rather than a tautology:
the two files are written by different code paths and the gate compares them line by line
on every shared field, plus the scored and population counts in `hydrogen_summary.json`.

**THE LESSON IS THE ONE D-S1 REACHED FROM THE OTHER END.** A missing input produced a
plausible answer instead of an error, and the answer was wrong in the direction that makes
an instrument look better: 224 scored entries flatter no rate, but 53 zero-scoring entries
added to the denominator make every sector's hydrogen comparison wrong.

**D-A4. THE FUNDER PASS IS CROSS-SECTOR NOW, AND THE LIST IS THE INNOVATION FUND'S OWN
PROJECT TABLE.** 413 projects across every call and every sector, with the call, the
sector, the country and the status; 280 carry a project factsheet PDF and **163 were read**
— every one whose sector, category or technology pathway could touch these five sectors.
The factsheet carries the coordinator, the grant amount, the expected avoidance and the
start, financial-close and operation dates. **The table is the list and the factsheet is
the award.**

**RUNG 4 GOES FROM ASKED-OF-ONE-SECTOR TO ASKED-OF-ALL-FIVE.** Before this pass: hydrogen
20 passes, and 250 scored entries in the other four sectors whose rung 4 was
`not_searched`, because no funder list had been read against them. After: 32 passes and no
`not_searched` cell anywhere — cement 17 of 42, batteries 6 of 57, steel 5 of 49, transport
and storage 4 of 102. **A fail now means the funder's list was read and this project is not
on it**, which is what D-L2 asked for.

**THIS READER PARSES PDFs AND ITS SIBLINGS DO NOT.** `sources/funder_search.py` imports
PyMuPDF lazily, because the Commission publishes its awards as PDFs and returning empty
text for them records a refusal the publisher never gave. The package is in
`sources/requirements.txt` and **not** in `requirements-gates.txt`: this reader is never in
the build chain.

**D-A5. SEVEN MATCHES WERE REFUSED AND THE SHARPEST IS ONE LETTER WIDE.** The register
holds **`greensand`** (INEOS Energy, Harbour Energy) and **`greenstore`** (Harbour Energy,
INEOS Energy, Nordsøfonden) — two Danish North Sea stores, the same two companies, names
one letter apart. The Innovation Fund's Greensand Future award names the 2023 Greensand
pilot and Nini West, so it lands on `greensand` and nowhere else. A name fold would have
hit both.

**AND ONE REFUSAL IS RECORDED FOR HOW IT AROSE RATHER THAN FOR WHAT IT WAS.** A first
screen matched three unrelated awards to CALB's plant at **Sines** because the letters of
"Sines" occur inside "business" once punctuation and case are stripped. Nothing was classed
on it — the screen produces candidates and a person rules — and it is written down because
it is the smallest clear example in this repository of why D-S4 forbids a normaliser.

**D-A6. TWO ENTRIES THIS REGISTER HAS NOT ADMITTED CLEAR RUNG 4, AND THAT IS THE LADDER
WORKING.** The Commission's own factsheet states **a direct reduction plant and two
electric arc furnaces at ArcelorMittal Gent**, at EUR 262,094,637 — a works the steel census
classed `searched none found` after reading ArcelorMittal's own pages. And it states EUR
31,238,542 to **Marcegaglia's AdriatiCO2 at Ravenna**, the entry whose owner's website
serves one identical body on every path (steel question S6) and therefore cannot be read at
all. A third, TarraCO2, is `named not admitted` in transport and storage.

**RUNG 4 PASSES AND RUNG 1 DOES NOT, AND NEITHER MOVES A CLASS.** The perimeter asks for
company confirmation and a funder is not the company; the rungs are independent by
construction, and here that independence is doing exactly the work it was built for —
recording that a second party with its own register has confirmed a project whose owner
this register cannot read. All three go to the queue.

**D-A7. RUNG 6 IS PROVISIONAL EVERYWHERE AND NOT SEARCHED IN TWO SECTORS, AND THE TWO ARE
DIFFERENT STATEMENTS.** Every edge in `sources/edges.json` carries `verdict: null`, so every
rung 6 result that rests on an edge is `provisional: true` — 76 hydrogen, 33 batteries, 34
cement, 62 transport and storage, 9 steel.

**A CELL THAT RESTS ON NO EDGE IS NOT PROVISIONAL, IT IS NOT SEARCHED.** The first draft
marked every scored entry provisional, which made the provisional count a count of the
scored population and said nothing. `provisional` means *a verdict is owed on the edge this
rests on*; where brief 9's sweep never reached the row, no verdict is owed and none is
awaited. The sweep recorded an owner side for 117 projects — all 66 hydrogen rows, 32 of 33
battery, all 8 steel, **8 of 34 cement and 3 of 43 transport and storage** — so rung 6 is
`not_searched` on 34 of 42 scored cement entries and 97 of 102 in transport and storage.

**THAT COLUMN IS ABOUT BRIEF 9'S REACH AND NOT ABOUT THE PLANTS**, and question L3 says so
in the questions file so that a reader of the table cannot miss it.

**D-A8. SIX QUESTIONS, AND NOT ONE RUNG TEST MOVED.** `sources/ladder_questions.json`
carries L1 (does rung 2 ask a question storage operators answer? 6 of 102 clear it), L2 (the
battery IPCEIs are read and name nobody — is that a fail or an unread?), L3 (rung 6's
coverage), L4 (a column is a list, not a sector), L5 (does rung 4 record that an award was
made, or that it stands? four of 33 are terminated) and L6 (why steel clears rung 1 least
often, and why that is the rung working).

**Every one of them is a proposal that is NOT made here**, and the reason is D-B1's: the
pass that scores an instrument is the worst possible pass to loosen it in, because a rung
that scores badly looks like a defect in the rung and may only be a finding. The gate now
enforces that rather than asking for it — `check_ladder_all.py` recomputes the SHA-256 of
`### The six rungs` on every build and fails on a difference.

## Rulings of 19 September 2026, from the gate chain

**D-A9. THE LADDER'S 53 PERIMETER EXCLUSIONS WERE READ OUT OF A GITIGNORED SCRATCH FILE,
AND THE DEFECT HID BEHIND A SECOND MISSING INPUT.** `build_ladder.perimeter_excluded()`
calls `report_benchmark_gap.perimeter_exclusions_by_ref()`, which read
`scratch/hydrogen_benchmark_gap.csv`. `scratch/` is gitignored. So which of the 245
hydrogen entries were classed out of perimeter depended on **whether somebody had happened
to run the gap report on that machine**.

**IT NEVER FAILED BECAUSE IT NEVER RAN.** `build_ladder --check` is guarded on
`benchmark_available()`, which tests for the IEA cache — also gitignored — and on a machine
missing that it prints *"the ladder is not recomputed"* and passes. The two untracked
inputs went missing together, so the step skipped and the gap stayed invisible. On 19
September the census worktree fetched the IEA benchmark live; the benchmark was suddenly
present, the scratch file was not, **and the classifier returned zero exclusions**. All 53
came back `none found` — scored, at zero.

**THE SAME SHAPE AS D-A3, ONE LAYER DOWN, AND WORSE.** D-A3 was this pass's own first draft
making that mistake; this was the committed scorer making it, on main, since brief 10.

**MATERIALISED, on the #66 precedent.** `report_benchmark_gap.py` now writes
`sources/hydrogen_perimeter_exclusions.json` — tracked, 53 entries, 31 `DRI or other
perimeter exclusion` and 22 `blue` — and `perimeter_exclusions_by_ref()` reads that first,
falling back to the scratch classifier only where the tracked file is absent. With the
scratch file deleted, `build_ladder --check` now passes and reports 245 entries matching
their sources. **THE COMMITTED hydrogen.csv WAS RIGHT ALL ALONG**, which is the one piece
of luck in this entry and not a reason to leave the dependency where it was.

**D-A10. A LINK CHECK FAILED ON A HOST THAT IS NOT THIS BRANCH'S BUSINESS, AND IT IS
RECORDED RATHER THAN STEPPED AROUND.** `elektroniknet.de`, cited by a battery row since that
census, answered HTTP 403 to the declared reader on 19 September — from its own Apache, with
no CDN header — having passed as recently as the steel chain the day before. It is added to
`BOT_HOSTILE` in `check_links.py`, which is `reported, not failed` and not silence: the
citation stands, no row was edited, nothing was re-read, and it moves to
`refused_declared_reader` with a date the moment a person opens it. That is the same
handling globalcement.com and stellantis.com have, and the comment there already describes
this exact case — a publisher that refuses a User-Agent which says what it is.

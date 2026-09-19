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

## Rulings of 20 September 2026, the follow-up to #69

**D-A11. STEEL FAILED RUNG 1 TWENTY-ONE TIMES ON A FIELD ITS ENTRIES DO NOT HAVE, AND THE
FIX IS TO THE READING.** Of the 31 scored steel entries failing rung 1, **twenty-one were
`admitted`** — and every one of them records a municipality and an owner speaker, because
a census admits a works precisely by reading a company document that names it. The scorer
never looked: `row` on a steel entry is **two different fields under one name** — an
existing row id on a `held` entry, the row the census PROPOSES on an `admitted` one — so
all twenty went down the no-row path, where the cell cited "the census read the owner's own
sources and none names a site for this project". **That sentence was false of every one of
them.** SHS at Dillingen, ArcelorMittal at Gijón, Duisburg, Dunkerque, Hamburg and Fos, HKM,
Blastr at Inkoo, GravitHy at Fos, Hydnum at Puertollano, SSAB at Luleå and Oxelösund, Tata
at Velsen-Noord and Port Talbot: all named by their owners, all scored as unnamed.

**The other ten are `searched none found` and they record no speaker at all.** They still
fail, and correctly — the reading fix changes nothing about them, which is the check that
it is a fix and not a loosening. Steel rung 1: **18 of 49 to 35 of 49.**

**AND THE SAME CORRECTION TAKES EIGHT PASSES AWAY FROM BATTERIES.** Rung 1 was passing
every `named not admitted` entry on the class name. Six battery entries record their own
refusal as `FAILED LEG: SITE` — SVOLT Finland is a company and a country, Freyr's Nordic
Battery Belt is a programme name covering no works — and an entry the census refused
*because* no site was named cannot clear the rung that asks for one. Batteries: **41 to 33.**
A reading fix that only ever raised a number would not be a reading fix.

**D-A12. THE THREE FUNDER-FOUND ENTRIES WERE RE-SEARCHED ON THEIR OWNERS' OWN DOMAINS AND
NOT ONE OWNER CONFIRMS.** Under S3's order — the owner's newsroom first, never the list's
citations.

  - **ArcelorMittal Gent.** `belgium.arcelormittal.com` answers and carries careers and
    site news with no DRI, no EAF and no ZESTA; `arcelormittal.com/media/news` answers with
    navigation; `corporate.arcelormittal.com` **403s a declared reader** on every path
    tried. The Commission's factsheet states a direct reduction plant and two electric arc
    furnaces at Ghent at EUR 262,094,637. **The class stands at `searched none found`**,
    and the gap between a funder's specificity and an owner's silence is now measured
    rather than suspected.
  - **Marcegaglia AdriatiCO2.** `marcegaglia.com/en/sustainability` and
    `/en/media/press-releases` both answer 200 with **21,711 characters, identical to each
    other**; `marcegagliasteel.com` does not resolve. Question S6 re-confirmed on a second
    day and a second pair of paths. **Class stands at `named not admitted`.**
  - **TarraCO2.** Repsol's press room and its climate-change page are both readable and
    **neither contains the string "Tarra"**. **Class stands at `named not admitted`.**

**NO ADMISSION, NO RECLASS, AND THAT IS A RESULT AND NOT A FAILURE OF THE PASS.** D-A6 said
these three were the ladder's independence doing its work; a re-search that found the owner
after all would have been the better story and the evidence does not support it.

**D-A13. THE FOUR TERMINATED AWARDS GET THE CATALINA TREATMENT, AND ONLY TWO OF THEM HAVE A
ROW TO PUT IT ON.** `freyr-mo-i-rana` and `anrav-devnya` each gain a `status_history` entry:
`event_kind: financing`, `date_precision: not_after` 2026-09-09 — the fiche's own dateline,
because the document gives no date for the termination itself — source the factsheet,
`source_type: grant_register`, and the funder's figures in the note. **Neither status
moves**: Freyr's stays `cancelled` and ANRAV's stays `funded`, because a funder withdrawing
its money is a fact about the award and reading a cancellation out of it would be this
register deciding something the owner has not said. D-B19, applied.

**HYBRIT's Gällivare and Oxelösund HAVE NO ROW.** Both are census entries the steel pass
admitted with a proposed row id and nothing has landed; there is no `status_history` to
write to. Both go to the owner-look queue with the other two, and the absence is recorded
here rather than left to look like an oversight. **One award, two works, four queue items.**

**D-A14. FOUR OF THIRTY RE-SEARCHED ENTRIES CHANGE CLASS, AND THE THRESHOLD WAS TWO.**
`sources/ladder_research_audit.json`, `random.seed(11)` written down so the draw can be
repeated. FAAM at Teverola, InoBat in Serbia, OCAP and PYCASSO all move from `searched none
found` to `named not admitted` — **not four projects that changed but four searches that
missed a readable owner page**, every one found by starting at the owner's own domain.
**The four sectors get the full pass as a further brief.**

**THE CORRECTED READER REPAIRED NOTHING HERE AND THE AUDIT SAYS SO.** None of the 44 URLs
the thirty entries recorded is non-ASCII and none had failed client-side, so D-S1's fix had
nothing to do in this sample. What the audit actually tested was the search ORDER.

**AND THIRTEEN OF THE THIRTY RECORDED NO SOURCE URL AT ALL** — a class of `searched none
found` with no list of what was searched, which cannot be audited by re-reading and only by
searching again from the owner's name. That is a finding about the censuses' record-keeping
and it belongs in the further brief's scope.

**THE FOUR RECLASSES ARE RECORDED AND NOT WRITTEN**, because applying four corrections to a
population a full pass is about to re-read would leave the censuses half corrected and the
halves undated.

**D-A15. THE PRESS-QUOTED AMENDMENT, AND BOTH TABLES ARE IN THE FILE.** Every rung cell now
carries a `medium` — `owner`, `permit`, `funder`, `press_quoting_owner`, `press`,
`register` — and `all.csv` carries `<rung>_result_amended`, `rungs_passed_amended` and
`outcome_class_amended` beside the frozen columns. **The frozen block is untouched and the
gate proves it**: `### The six rungs` still hashes to `47b0859d…`.

**A DIRECT OWNER STATEMENT QUOTED IN THE PRESS PASSES; A TITLE IN ITS OWN VOICE DOES NOT.**
Of 582 passing cells across five sectors: **503 owner, 60 funder, 12 permit, 6 press, and
one press quoting the owner** — Metinvest at Piombino, reported by Kallanish from the
company's own statement, which stands. The six move, all of them rung 1, and six entries
gain the outcome class **`press only`**.

**PRESS-ONLY IS AN OUTCOME CLASS AND NOT A FAILURE**, on the rule the hydrogen amendment of
18 September set: silence, refusal and press-only are three different things and none of
them may share a class. The gate enforces the shape — the amendment may only take a pass
away, only from medium `press`, and an entry classed `press only` must clear no rung.

**D-A16. THE LAYER SPLIT, AND NO DATUM MOVES.** Every entry carries `producing` or
`infrastructure`; transport and storage is the infrastructure layer and the other four are
producing. **The cross-sector table is computed for the producing layer and the
infrastructure rows are summarised beneath it** rather than averaged in. Transport and
storage clears rung 2 six times in 102 and rung 5 not once; a pipeline has no nameplate its
owner publishes and a reservoir is not a plant, so a single rate over both describes
neither. The same 644 lines, grouped — and question L1 is the one this makes answerable
rather than the one it answers.

## Ruling of 20 September 2026 — the admission rule is amended

**D-A17. A FUNDER'S OWN AWARD RECORD ADMITS A PROJECT, AND IT IS THE FIRST TIME ANYTHING
BUT THE COMPANY HAS BEEN ALLOWED TO.** Written into `sources/scope.md` as *"A funder's own
award record admits a project"*, beside the company-confirmation test rather than in place
of it. An Innovation Fund factsheet, an IPCEI decision or a national programme's published
grant, **naming the company as beneficiary**, admits the project; the admitting speaker is
recorded as `admitted_by: funder`; **the owner leg stays open** and carries an owner look
under rule 17.

**WHY A FUNDER AND NOT A NEWSPAPER, ON THE SAME DAY THE PRESS AMENDMENT REFUSED ONE.** A
funder is a party to the project — its own register, its own money, its own exposure to
the description being wrong. A trade title has none of those. The test is not whether the
speaker is reliable but **whether the speaker is a party with a record of its own**, which
is the same test the dependency graph already applies when it lets a supplier's order book
speak about a customer's plant. D-A15 and D-A17 are one rule stated from two sides.

**APPLIED TO THREE, AND THE THREE ARE NOT THE SAME CASE.**

| entry | was | why it was that, and why it moves |
|---|---|---|
| ArcelorMittal Gent | `searched none found` | **NOT A SEARCH MISS.** Read on 15 September and again on 20 September under the S3 order; `corporate.arcelormittal.com` **403s a declared reader** and the readable domains carry nothing. The owner has published nothing this register can reach. |
| Marcegaglia AdriatiCO2 | `named not admitted` | **NOT A SEARCH MISS.** S6: marcegaglia.com serves one identical body on every path — 21,704 characters on 18 September, 21,711 on 20 September. No search reaches those words. |
| TarraCO2 | `named not admitted` | **NOT A SEARCH MISS.** Repsol's press room and climate-change page are both readable and **neither contains the string "Tarra"**. |

**IN NONE OF THE THREE DID THE READING CHANGE. THE RULE CHANGED**, and the docket says so
rather than letting three reclasses look like three better searches.

**AND THE AMENDMENT MOVES NO RUNG, WHICH IS WHAT MAKES IT SAFE.** Rung 1 asks for the owner
or the permitting authority and a funder is neither, so **a funder-admitted entry fails
rung 1 and clears rung 4**. The scorer had to be corrected to say so: it was passing rung 1
for any `admitted` entry with a source, which would have let the amendment quietly hand
three entries a site statement nobody made. Steel rung 1 goes **35 to 34** on this branch —
an admission that *lowers* a rung count, which is the shape an honest amendment has.

**ONE AWARD IS NOT APPLIED, AND THE BOUNDARY IS THE POINT.** The Innovation Fund's CUSTARD
award names Acciaierie Bertoli Safau at its own steel plant, and the entry stays a
**perimeter exclusion**. The amendment settles **who may confirm a project, not which
projects are in scope**; carbon capture and use at a scrap-EAF works is refused on the
route test and a funder's money does not change the route.

**WHERE THE ROW LANDED AND WHERE IT DID NOT.** `tarraco2-storage` is a new `ccs` row — the
cement and CCS census admits with a row, so that is its normal path. The two steel entries
are reclassed in the census with proposed row ids (`zesta-gent`, `adriatico2-ravenna`) and
no row, **because that is where the steel census's other twenty admissions sit** and
landing two rows out of twenty-two would make the file mean two different things.
`report_candidate_gaps.py` gained a second rule-17 block so that the owner look for a
funder-admitted entry with no row is printed too — without it the queue would have lost
exactly the entries the amendment creates.

**PROSPECTIVE.** The rule applies to every funder-found entry the further brief turns up,
in all sectors. Today's funder passes hold 33 cross-sector awards and 55 hydrogen ones, and
these three were the only matched awards against an unadmitted, in-perimeter entry.

## Brief 14 — the re-search pass, 21 September 2026

**D-A18. THE ADMISSION SEARCH OF 10 SEPTEMBER INVENTED DOMAINS FROM PROJECT NAMES, AND
THIS PASS INHERITED THEM.** Quoted from `sources/research_pass_14_summary.json`, key
`the_admission_search_guessed_domains`: of its 167 entries, **47 had every non-EU host
derived from the project's own name**. `www.labskive.com` for Green Lab Skive,
`www.castellon.com` for BP's Castellón refinery, `www.ccuaalborg.com` for the Green CCU
Hub at Aalborg — and `www.barseback.com` for the Barsebäck Hydrogen Hub, **which is a golf
resort**.

**THE GUESS IS OFTEN RIGHT, WHICH IS HOW IT SURVIVED.** Twenty-eight of the 47 came back
`owner or permit source names the site`, because a project frequently is at its own name,
and a guessed domain that answers and names the works is a fact however it was reached.
**Fifteen are the problem**: classed `searched, none found` where every domain tried was
one this register invented. For those, "none found" is a statement about a guess. Held as
question L9.

**AND BRIEF 14's OWN SEARCH READ THOSE GUESSES BACK.** `research_pass.py` takes an entry's
owner host from the hosts in its own records and refuses to derive one from a name — and
the records already contained derived hosts. **A rule against folding a name into a key is
only as good as the records it reads.**

**D-A19. THE PASS SEARCHED ALL 164 AND CHANGED NO CLASS, WHICH IS THE STANDING RULE
WORKING.** 164 entries, 296 fetches, every one recorded in
`sources/research_pass_14.json` with the entry it was made for and what the text
contained. The before and after tables are **identical in every figure** — population,
scored, exclusions and unread across all five sectors, quoted from
`sources/ladder/all_summary.json` — because the rule of 21 September holds an entry rather
than amending anything mid-pass.

**THE SIGNAL IS A SUBSTRING MATCH AND IT IS SPLIT RATHER THAN COUNTED.** 59 entries have an
owner page containing a distinctive word of the entry's name; **28 of those are the domain
echoing the project's own name back** — `hyperionrenewables.com` contains "Hyperion" —
which says the register had the right company's website and nothing about this works. 31
are candidates a person should read. A report that said "the owner names 59 of them" would
be the flattering-number failure the standing rule was written for, one day later.

**TWO ARE REAL AND BOTH ARE HELD** as question L8. Volvo's own press release of 10
September 2026 names Mariestad and "the intended battery cell production site"; ProLogium's
front page carries "Dunkirk Gigafactory Groundbreaking". Both are classed `searched none
found` today and neither is: something was found.

**AND FOUR THAT LOOK LIKE HITS ARE NOT.** EAS Nordhausen, BMZ Karlstein and BASQUEVOLT
Vitoria-Gasteiz match on the place name **in the imprint**, which is exactly what the
battery census already recorded as the failure. Holcim's Carboneras match is a photo
exhibition, *"Carboneras en fotos"*.

**D-A20. THE BROWSER QUEUE IS 82 ENTRIES AND TWELVE OF THEM ARE QUEUED AGAINST A DOMAIN
THAT NEVER EXISTED.** `python3 sources/research_pass.py --queue` prints it with the reason
per entry: a page that answered nothing, or an entry whose own records name no owner host.
The twelve are D-A18's, and they should be struck from the queue rather than handed to a
person to open — reading `www.crinorway.com` in a browser will fail for the same reason it
failed here.

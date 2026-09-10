# Eufabric scope

This file is the triage standard. The watch agent shows it to a model along with
one candidate document and asks: does this belong in the register?

It is written to be read by a classifier, so it states the boundary rather than
describing the project. Every rule here should be decidable from a title, a
CELEX, and a short extract — the triage step does not have the full text.

## What the register is

Eufabric's register layer tracks **what EU industrial-decarbonisation law requires of firms,
and what it offers them** — provision by provision. Each row is one duty or one
incentive, with the source sentence quoted verbatim, the addressee named, and
the sector reach recorded.

The register currently covers the EU ETS revision, the Industrial Accelerator
Act, the CBAM extension, the Omnibus simplification of CSRD/CSDDD, and three
standing acts read at their current consolidation: the Net-Zero Industry Act
(Regulation (EU) 2024/1735), the Critical Raw Materials Act (Regulation (EU)
2024/1252) and the Packaging and Packaging Waste Regulation (Regulation (EU)
2025/40). The first two of those are the baseline the Industrial Accelerator
Act amends and the input-side boundary NZIA's own scope provision defers to,
so a new consolidation of either moves what the register measures against.

**PPWR has been read once.** It is a single-pass file: 88 rows from one
independent extraction, no second pass, and therefore not reconciled.
`sources/ppwr_reconciliation_docket.json` declares that and
`reconciliation_gate.py` prints it as `PPWR NOT RECONCILED — single-pass`
alongside the three reconciled verdicts, so a reader cannot mistake one for
the other. A single-pass file is honest, not finished: the four reconciled
files each moved substantially on their second read, and the expectation is
that this one is wrong in the same proportion.

Three open questions are carried on the rows themselves as a `q` flag rather
than resolved silently:

- `prohibition-type-pending` — four rows encode a ban as `obligation`/`add`
  because the live `measure_type` enum has no `prohibition` value.
- `carry-over-renders-as-requirement` — three rows carry a resolved
  `prior_rule` proving the level does not move, but still render as
  "Requirement", because valence derives from `(measure_type, direction)`
  alone and no combination of the two yields Neutral for an obligation.
- The Art. 36/37 presumption of conformity is split into two linked measures,
  one Simplification and one narrowing. Whether that is the right reading is
  exactly what a second pass exists to test.

## IN scope

A document is in scope when **all three** hold.

1. **It is EU law or a proposal for EU law.** Regulations, Directives,
   Decisions, and Commission proposals for any of those. Delegated and
   implementing acts count.

2. **It creates, changes, or removes an obligation or a support measure** that
   an operator, producer, importer, investor, or Member State authority has to
   act on. A duty, a threshold, a reporting requirement, a verification step, a
   free-allocation rule, a fund, a procurement condition, an exemption.

3. **It reaches one of the tracked sectors** — steel, aluminium, cement, glass,
   paper and board, wood, food and drink, retail, hotels and restaurants,
   chemicals (and its child, plastics converting), power, waste, shipping,
   aviation, automotive, construction, batteries and solar, clean tech, or
   carbon capture and storage — through emissions, energy, industrial
   products, or the trade rules that govern them.

   ### The sector spine, and when a child exists

   The spine lives in `data/sectors.json`, read by both `sources/build_graph.py`
   and `web/lib/data.ts` so the two sides cannot drift. It is **two levels and
   no more**: a sector is a parent, or a child of exactly one parent, written
   `<parent>/<child>` — which is also its URL.

   **The evidence rule.** A child exists only where at least one measure
   applies to the child and *not* to the parent. The `evidence` field on the
   child records which measures forced it. A child that cannot point to such a
   measure is not a finer view of the parent, it is a duplicate of it, and it
   should be folded back in. `chem/plastics` qualifies because PPWR's
   recyclability grades, recycled-content minimums and format bans fall on
   converting polymer into packaging, not on chemicals manufacture.

   Two consequences follow and are enforced:

   - **Parents roll up, children do not roll down.** A measure on
     `chem/plastics` appears on the chemicals page, in whichever list it
     earned on the child. The child shows only what applies to the child.
   - **No exposure inheritance.** A child gets an exposure panel only where
     FIGARO resolves a code of its own — `chem/plastics` is C22, distinct from
     chemicals' C20. A child with no code of its own shows no panel rather than
     borrowing one that describes a different industry.

Specific things that ARE in scope, because they have been missed before:

- Benchmark values, allocation rules, and free-allocation decisions under the
  ETS. These look technical and are load-bearing.
- Amendments to an act already in the register, however narrow.
- Consolidated versions of a tracked prior rule: a new consolidation means the
  baseline the register measures against has moved.
- Acts defining terms that tracked measures depend on — most of all the
  delegated acts under the ESPR and the CPR that will define "low-carbon" for
  steel, concrete, and aluminium. The register carries a placeholder node
  waiting on exactly these.

## OUT of scope

- **Staff working documents, impact assessments, and evaluations.** They
  accompany a proposal rather than impose anything. The proposal itself is in
  scope; its SWDs are not.
- **Communications, recommendations, opinions, and green papers.** No binding
  obligation. A Communication that announces a future proposal is out; the
  proposal, when it lands, is in.
- **Corrigenda** that fix typography or translation without changing a duty.
- **Anything whose only connection is a passing citation of a tracked act.**
  Many acts cite the ETS Directive without touching the ETS.
- **Purely institutional, budgetary, or procedural acts** — committee
  appointments, agency establishment, comitology procedure, financing decisions
  with no conditions on recipients.
- **State aid decisions on individual cases.** The framework is in scope; a
  single company's approval is not.
- **Agriculture, food, forestry, and land use**, unless the act imposes a duty
  on one of the tracked sectors.

## BORDERLINE

Use this when the document plausibly satisfies all three IN rules but you
cannot confirm one of them from the title and extract alone. Borderline is the
honest answer for:

- A title that names a tracked act but gives no clue what it changes.
- An act reaching a tracked sector where it is unclear whether any duty is
  created or the act is purely procedural.
- A definitional act whose relevance turns on wording not visible in the
  extract.

Borderline items go into the pull request for a human to rule on. They are not
ingested. **Prefer borderline to a confident wrong call in either direction** —
a false "out" silently drops a measure and nobody finds out; a false "in"
produces a bad register row that has to be unwound. Borderline costs one human
minute.

## STANDING RULINGS

Decisions taken once and binding on later work. They are here rather than in a
commit message because the next person to touch this needs them before they
start, not after they have guessed.

### Edges are evidenced claims about the world; filing decisions are not edges

The graph's edge set holds assertions that something is true outside this
repository: this act amends that one, this act repeals that one from that date,
this sector supplies that one. Every edge carries `since` and an evidence
pointer because every edge is defensible against a source.

How this register *files* things is a different kind of fact. That plastics
converting sits under chemicals is a choice about presentation, revisable at
any time without anything in the world changing. So sector parentage is a node
**attribute**, not an edge. Making it an edge would put a taxonomy decision on
the same footing as a repeal clause, and a reader walking the edge set would
have no way to tell the two apart.

The general form: if the relation would survive this repository being deleted,
it is an edge. If it would not, it is an attribute.

### A finding states arithmetic

A finding may only state what the data computes — counts, shares, chains,
before/after deltas. No judgment about importance and no recommendations: the
moment a finding says what a number *means* rather than what it *is*, it stops
being checkable against the register, and checkability is the only licence a
finding has to exist. Findings are a small fixed set, not a feed.

Structurally: every template in `build_findings.TEMPLATES` names an arithmetic
shape, there is no editorial template, and `check_template_set` fails the
build if one is ever added back. Connecting prose that a human must write is
carried as an explicit TODO on a draft, never generated.

### No free-generated text on the site

Every readable sentence on the site is one of two things: template-rendered
from the register (the summary strips and their prose forms, the reach and
arrival sentences, the computed titles and meta descriptions — all worded
once, in `web/lib/prose.ts` and the metadata templates, and fed only
gate-checked objects), or George-reviewed content stored as data (findings
past their draft TODOs, the tagline and perimeter lines once written). No
model-generated paragraph ships as page copy, and no generic explanatory
paragraphs about what the ETS or CBAM is — a reader who needs a primer is one
link from EUR-Lex, and a primer is where drift and error live. A sentence
that cannot point at the data it renders or the human who signed it off does
not go on a page.

Three tiers. (1) Computed prose: template-rendered sentences from gate-checked
data, generated every build, unlimited. (2) Reviewed prose: drafted text (by
anyone, including an LLM) stored as data with a recorded review status;
renders unchanged until deliberately edited; review depth proportionate to
stakes. (3) Banned: prose generated at build or request time that no one
reviewed, or reviewed prose regenerated silently. Per-act overview paragraphs
are tier 2, and are expected to be added one per act in a future PR.

### A citation separates with a comma or a middle dot, never an em dash

Every source on the site renders a citation, and `web/lib/citation.ts` is the
one place one is worded. It joins with a middle dot; clauses inside a single
fact are joined with a comma. It never joins with an em dash.

The reason is that the em dash is already taken, twice over. Publishers use it
inside their own titles — "Cement — Energy System", "Carbon sequestration and
reuse — capital and operating cost estimates" — and the `publisher` field uses
it to hold a group heading and a citation in one string, which is the split the
Sources block makes to get its headings. A citation that also joined with an em
dash left a reader no way to see where a publisher's punctuation stopped and the
citation's own structure began.

The rule is about the separator a citation EMITS. A title keeps whatever
punctuation it was published with: a citation quotes a title, it does not edit
one.

The URL is not part of a citation at all. It belongs in `href` and nowhere else,
which is the standing rule `sources/check_anchor_text.py` enforces over the
built pages: no anchor's text may begin with `http` or contain a query string.

### Display vocabulary: internal terms never reach an audience surface

Audience-facing surfaces — pages, components, computed-prose templates,
titles, meta descriptions, structured data — never use the pipeline's internal
vocabulary: no "row", "duty-side", "benefit-side", "FIGARO", "docket",
"reconciled", "valence", "slug". The display layer says: measure, requirement,
prohibition, support measure, right, the act's display name, the sector's
display name, and "Eurostat input-output data" for FIGARO-derived figures. The
translation happens at render time only: data files, gates, ids, field names,
and internal documentation keep the internal vocabulary unchanged, because the
internal terms are the precise ones and the gates are written against them. A
reviewed tier-2 text is authored in display vocabulary from the start; a
computed template translates at the template.

A second list is banned for a different reason. "Reference", "tracker",
"register", "record", "plant", "map" and "transition" are ordinary English and
several of them are accurate; what they are wrong about is positioning. A
platform that calls itself a register or a tracker has told the reader it is a
place where things are written down, and Eufabric's claim is that it is
intelligence — signal, ranking, exposure, pipeline, readiness, linkage. Two of
them are banned in framing and legitimate in fact: an installation's name may
contain "plant", and a diagram is a diagram, but neither word describes the
product. "Change record" survives as the name of one content tier and nowhere
else.

Both lists live in `sources/display_vocabulary.py`, which is the enforcement
point rather than this paragraph: every generated label and every generated
sentence is checked against them at the moment it is made, and a violation
fails the build. Hand-written surface copy is reported by
`sources/check_display_vocabulary.py` and left to a reviewer, because the
framing-versus-fact distinction is a judgement about the sentence and not
about the word.

### Snapshots are append-only

Each release archives the register state and all fetched source versions
under a dated path — `snapshots/<date>/`, written by `sources/snapshot.py`
with a SHA-256 manifest. Ingestion and rebuilds never overwrite a prior
snapshot: the tool refuses an existing path and has no force flag. A wrong
snapshot is deleted by a human with git, where the deletion stays visible in
history; it is never replaced in place. The archive is what makes every
published number reconstructible after the register has moved on.

### Measure ids are permanent

A measure id, and the URL built from it (`/measures/<file>/<id>`), never
changes meaning. A row whose classification moves keeps its id and records
the move in `reclass_from`; a row that is withdrawn stays resolvable rather
than being reused. Any future change to an id or a URL shape requires a
redirect from the old address — that is policy, not preference, and it is
stated publicly on /coverage. Citations are the product: an id that cannot be
cited into next year is not worth extracting.

### The exposure methodology is reconstructed, and proved by reproduction

`data/exposure/*.json` is built by `sources/build_exposure.py` from the raw
FIGARO flatfile. The first eleven files predate the builder — they were
delivered from outside the repo — so the builder had to recover their
methodology rather than define one. `--check` rebuilds those eleven and diffs
them against what is on disk, and it passed exactly before any new sector was
written. That gate is the licence to trust the new files: they come out of the
same arithmetic, not out of a plausible-looking guess. **Do not add a sector
whose exposure file was produced any other way, and do not change the builder
without `--check` still passing.**

Four things were changed during the reconstruction. Three are load-bearing;
the second turned out on later checking to be redundant, and is recorded as
such rather than quietly dropped:

1. **Value added is not a supplier.** FIGARO's `rowIi` includes compensation of
   employees (`D1`), gross operating surplus (`B2A3G`) and the tax rows. Left
   in, they are read as industries selling into the sector: `D1` ranked second
   on the chemicals supplier list, and **chemicals' import dependency came out
   at 42.7 % against the delivered 21.9 %** — a number that would have been
   published, looked plausible, and been wrong by a factor of two.
2. **`refArea` `W2` is where value added is filed** — *not* a world aggregate.
   This entry originally read "a world aggregate, restating rows already
   present", which was wrong about the mechanism and is corrected here.
   Verified against the flatfile on 2026-08-18: `W2` carries exactly and only
   the six value-added codes, and those codes appear under no other area. The
   62 % of chemicals' foreign inputs it accounted for was value added being
   read as an import — correction 1 restated. The `W2` skip is therefore
   **redundant**, and `--check` reproduces all eleven delivered files without
   it. It is kept as a cheap guard against a future edition filing something
   else there. **Three corrections do the work, not four.**
3. **Final demand is outside the customers denominator.** Household, government
   and NPISH consumption and capital formation are final uses, not customers.
   With them in the denominator every customer share was understated by about a
   fifth; with them out, all eight chemicals rows matched to the decimal.
4. **`OTHER` is the remainder taken before rounding**, not the remainder of the
   rounded shares. The difference is a tenth of a point on roughly a third of
   the views. It was found because every named row already matched and only
   `OTHER` did not.

A fifth correction was a genuine tie rather than a methodology error: Malta
buys exactly 0.546 of basic metals from each of `GB` and `ES`, so the sort
breaks ties on value descending, then code **ascending**. A tiebreak is not
cosmetic when it silently reorders a published row.


### The valence matrix says what the act does, or it says Neutral

Valence is derived from `(measure_type, direction)` and never stored. Two
values were added because the matrix could not express what PPWR contains.

**`direction: "unchanged"` derives Neutral.** It is not a third movement, it is
the explicit assertion that there is NO movement. Before it existed, a rule
carried over verbatim from a repealed act had to be filed as `add` and rendered
"Requirement" however plainly its `prior_rule` said the level was identical —
which is the precise misreading the delta model exists to prevent. PPWR's
Art. 52 recycling targets are the case that forced it: every figure is
identical to 94/62/EC Art. 6(1)(f)–(i) as amended, and the site was calling
them a new requirement.

`unchanged` is admissible **only** on a duty-side row carrying a RESOLVED
`prior_rule`. "Nothing changed" is a claim about the prior law, and a row that
cannot quote the prior law is not entitled to make it — it is entitled to say
`add` and be read as a requirement, which is the honest default when the
before-state is unknown. `benefit_axis.assert_unchanged_prior` enforces this,
in the same shape as the deletion guardrail and for the same reason.

**`prohibition` is a first-class measure_type**, duty-side alongside
`obligation`, rendering "Prohibition" / "Prohibition lifted". "Do not place
this on the market" and "keep this below 100 mg/kg" are different instruments:
one closes a route, the other conditions it. Collapsing them made four PPWR
bans — the PFAS limit, the Annex V formats, false bottoms, misleading labels —
read as ordinary requirements.

Both label pairs are scoped to a single type, on the rule that sank the earlier
Cost/Saving pair: **no label may mean two different movements depending on the
type it lands on.**

`check_valence_parity.py` walks the full cross product through both the Python
and the TypeScript implementation — 42 combinations including the nonsensical
ones — and fails the build on any disagreement. A row whose classification
moves after first publication keeps its id and records the move in
`reclass_from`; ids are permanent, so that field is the only trace.


### Named and reached are disjoint

A sector is NAMED by a provision or REACHED by it, never both. The two lists
answer different questions, and a slug in both makes the row assert both at
once. `validate_v2` fails the build on it.

It needed a gate rather than a convention because the defect is **invisible in
the product**: `web/lib/data.ts` puts a row in `named` if it is named and only
otherwise in `reached`, so a duplicate is silently discarded at render and
every count still looks right. Fifteen rows carried it — nine in PPWR, six in
CRMA, all from row definitions that composed the two lists out of shared
constants which legitimately overlap. Extractors now subtract `named` from
`reached` where the two meet, so the class cannot recur; the validator holds
the line for any file built another way.

### Reach is not stated on a record about an amending proposal

**Temporary suppression, until the reach model reads the consolidated base.**

Reach is computed against the act as ingested. For an amending proposal that is
the proposal text alone, so the sectors the proposal is recorded as reaching
include sectors that belong to the BASE regime it amends, not to the change it
makes. The ETS revision is the clear case: aluminium, cement and power come out
as reached, and they are reached by the ETS as it already stands — the proposal
does not extend the system to them. Stating that on a change record would
publish the same error that withdrew the first ETS finding, on a page that is
permanent by design.

So `sources/build_records.py` renders the named-sectors sentence only, and omits
the reach clause entirely, for any record whose act is an amending proposal:
a register file with at least one manifest entry that is `status: proposed` and
carries a non-empty `amends` list. A file with no manifest entry at all that
declares itself proposed is treated the same way, because the check cannot see
what it amends and suppression is the safe direction. CBAM's extension is
covered too — all twelve of its rows that carry reach are sourced to
`52025PC0989`, the proposal, so none of its reach derives from the consolidated
base. PPWR is adopted law and keeps the full sentence.

It is a gate, not a convention, for the reason every rule here is: the builder
drops `reached_count` from the slots it computes for a suppressed act, so a
template that mentions reach fails the build as an unknown slot rather than
rendering. The suppressed record also ships without its reach fields, so no
page can render what the prose is forbidden to say. The next amending proposal
inherits the suppression without anyone remembering this ruling.

The suppression lifts when reach is computed against the consolidated base act
as amended by the proposal, at which point the number means what a reader
would take it to mean and the clause can render for every family.

### A record's event date is the date of the event it describes

Not the date the platform found out. The two coincide often enough that the
difference is easy to miss, and a change record is permanent, so a page dated
to our reading rather than to the event is a small lie with no expiry.

Which date that is follows from what the record is about, per family:

- `new_act_ingested` describes the platform reading an act. The reading IS the
  event, so the date is the ingestion date from git history.
- `amendment` describes something that happened in law, so the date comes from
  the law. PPWR replaces Directive 94/62/EC on 12 August 2026 — Art. 70(1),
  "Directive 94/62/EC is repealed with effect from 12 August 2026", recorded in
  `manifest.json` under `repeals.<celex>.since` — so the record is dated the
  12th, not the 18th, when the file was read.
- `delegated_act` takes the date of the delegated act, and `status_change` the
  date of the procedural step, on the same principle, when those families are
  first exercised.

`build_records.py` fails an amendment record whose event date is not the date
the manifest records for the relationship, AND fails one where the manifest
records no date at all — the manifest today says WHICH acts a file amends but
not WHEN each amendment took effect, so an amendment record against an amended
(rather than repealed) act cannot be dated until an ingestion records it. The
failure is the point: falling back to the ingestion date would produce a record
that looks right and is wrong, which is the class of defect every gate here
exists to make impossible.

### Carry-overs come from repeal, not from amendment

`direction: "unchanged"` was added for PPWR, and the obvious worry was that the
gap had been silently forcing rows into "Requirement" across the whole
register. It had not. All 31 rows in the other six files carrying a resolved
`prior_rule` — omnibus 22, CBAM 8, IAA 1 — state a before that genuinely
DIFFERS from the after.

The reason is structural and worth keeping in mind when the next act lands.
**An amending act writes deltas by construction**: it exists to change
particular words, and every row it produces is a change. **A repealing act
restates**, and a replacement text carries its predecessor's numbers forward
untouched wherever policy did not move. PPWR is the first act in this register
that repeals rather than amends, which is why it is the first to contain a
carry-over at all. Expect the question again at the next repeal-and-replace,
and not before.

### `unchanged` needs a resolved prior_rule

"Nothing changed" is a claim about the PRIOR law, so a row may not make it
without quoting that law. `direction: "unchanged"` is admissible only on a
duty-side row whose `prior_rule` is resolved — status `sourced` or `recital`,
a stated prior obligation, and a span verbatim in the prior corpus.
`benefit_axis.assert_unchanged_prior` enforces it.

This is the same shape as the deletion guardrail and rests on the same
reasoning: a classification that cannot be substantiated does not get to
render as a confident label. A row that cannot reach the prior text is
entitled to say `add` and be read as a requirement — the honest default when
the before-state is unknown.

### Press may name a destination the company has already asserted

A capture project's storage chain is recorded in
`data/transition/projects.json` under `storage`: either the id of the store the
tonne reaches, or `"unresolved": true`. The question this ruling settles is when
a trade report may supply the store's identity.

**The company's own source has to assert the relationship, and describe the
destination specifically enough that the press report is identifying it rather
than adding it.** Press then supplies the name and nothing else. Where the
company asserts no destination at all, or asserts a different fate for the CO2,
a press claim is not recorded and the chain is unresolved.

The three worked cases, which is why this is written down:

- **ANRAV** — the Innovation Fund fiche says the project links Devnya "with CO2
  storage in a depleted gas field in the Black Sea, through an onshore and
  offshore pipeline system". The company asserts the relationship, the mode and
  a describable destination. There is one depleted gas field this can be, and
  the press names it Galata. **Recorded.**
- **IFESTOS** — the project's own site says the CO2 "will be liquified and
  transported to a permanent storage site in the Mediterranean". Same shape:
  the relationship is asserted and the destination is described. Press names
  Prinos. **Recorded.**
- **Carbon2Business** — Holcim's pages say the purified CO2 "will either be
  processed into e-methanol through methanol synthesis or reprocessed as a raw
  material to produce plastics". That is a different fate, not an unnamed
  storage destination. Trade press reporting a thirty-kilometre pipeline to
  Brunsbüttel is asserting a chain the company does not. **Not recorded; the
  chain is unresolved.**

The line is between naming something the company has already put in the world
and supplying a fact it has not. The first is what a specialist press is for;
the second is this register borrowing somebody else's confidence.

Two consequences that are not optional. The `storage` block carries the press
source with its verbatim, and a `note` saying the company's own wording is
weaker — so the reader sees the join rather than a flat assertion. And the
site's `confidence` stays `secondary`, which is what it is.

### A draw hold gates publication

**A hold withholds a page from the index. It does not stop the page being
built.** A held sector renders its product template like any other, is
type-checked, crawled by the anchor gate and drawn into every frame the build
writes; what the hold does is keep the URL out of `sitemap.xml` and put
`noindex` in its head until somebody lifts it.

**The case this is written from.** The batteries hold made `hasMap` return
false, so the route rendered the register directory instead of the product page
and the held page **was never built at all** — for two weeks. The first render
after the hold came off failed immediately, on a technology with no `dependency`
key against a TypeScript type that said the array was required. The bug was as
old as the hold, and nothing could have found it: **a gate that stops a page
being drawn also stops it being tested.**

A hold is a judgement that the data is not yet honest enough to publish. That is
a statement about readers, not about the build, and it has no business
suppressing the one mechanism that would tell you whether the page works.

`web/lib/transition.ts` `hasMap` therefore asks only whether the data exists;
`web/lib/siteRoutes.ts` `sectorIsIndexable` is where the hold is read, and it is
read by the page's own robots tag and by the sitemap together, so the two cannot
disagree.

### A stopped row does not enter the location queue

**Location is sought for active rows.** A project whose status is `cancelled` or
`paused` may stand in the register without a position, carrying a
`location_note` that says the position was not sought and why.

The reasoning is what the coordinate is for. A mark on a picture is a claim that
something is at a place, and the research behind it — a permit's grid reference,
a plan's parcel list, an operator's published address — pays for itself on a
works somebody might visit, buy from or object to. **A project that will not be
built has no works to place.** Hunting the parcel of a factory cancelled two
years ago buys a dot that a reader would take for a building, at the cost of the
only thing the hunt was for.

**The note is the whole of the allowance.** `sources/check_sector_schema.py`
refuses an empty `location` on any other status, refuses it without the note, and
refuses a note on a row that has a position — so the absence is always a decision
on the record and never an oversight that looks like one. A row that returns to
an active status fails the gate until its position is found, which is the
mechanism that stops this from becoming the place coordinates go to be avoided.

**What the surfaces do with it.** No crop is built (`sources/build_maps.py`
skips it), the project page renders the note where the picture would have been
with no placeholder standing in for the map, and the sector overview's
not-drawn clause names the row and its status — so a reader counting sites
against the projects table finds the difference accounted for by name.

**And it does not lower the perimeter.** The site rule is unchanged: a company
still has to have confirmed the site, and a row still says which standard it
stands on. What is dropped is the coordinate hunt, and only where nothing will
ever stand there.

### A failure you observe is blocking

**"Pre-existing" describes when a failure started. It is not a reason to push
over it.** A red gate is red whoever made it red, and a branch that ships with a
known failure hands the next person a build they cannot trust and a question
they did not ask for.

So: **a failure observed before a push is reported and ruled on, never stepped
around.** If it is inside the branch's scope, fix it. If it is outside — a gate
that has been failing since before this work started, a dependency that broke on
somebody else's clock — it is brought to George as a failure, in those words,
before the push, and he decides whether it is fixed here, fixed elsewhere or
knowingly carried. What is not available is a push accompanied by a note saying
the failure was already there.

**The case this is written from.** `check_anchor_text` failed on the Italvolt
page for days. It was described in commit messages and in conversation as
pre-existing and out of scope, which was true and was not the point: the branch
was pushed green four times over a gate that was red, because the hook that says
"gate chain green" was running `prebuild` and the failing gate runs after the
build. Two things were wrong and only one of them was the gate — see
`.githooks/pre-push`, which now runs the whole chain.

**Why this is a ruling and not a habit.** The pull towards stepping around it is
strongest exactly when the failure is genuinely not yours, which is when the
reasoning sounds best and the outcome is worst: an unrelated red gate is how a
build stops being a signal at all.

### A node in the geo layer requires a source-stated position

Scoped to the geo layer and to nothing else. Every project row carries
`location`, `sources/check_coordinates.py` places every point against the
basemap, and both rest on the same precondition: a row in this layer is a row
somebody can draw. So **admission to this layer requires a position a source
states, to plant or site precision.** A facility that is named but not sited is
not admitted here, and the thing that names it records the chain as unresolved
instead.

Antwerp@C is the worked case. Holcim names it as GO4ZERO's export hub, so it is
a real, named destination; the Port of Antwerp-Bruges sites it only as "a plot
of land… inside the port", which is a port and not a place. A point invented
for it would be a mark a reader takes for a terminal, several kilometres from
wherever the terminal turns out to be. So it is not admitted, and
`go4zero-obourg` carries `"unresolved": true` with a note naming the hub — which
is more information than a wrong dot, not less.

**This settles admission to the geo layer and nothing beyond it.** Whether a
named-but-unsited facility should exist as a node in some other layer — carrying
its name, its operator and its role, with no coordinate — is an open question
this ruling does not reach and must not be read as foreclosing. It is a live
option: the register already holds facts about places it cannot draw. The two
readings agree on the case in front of us either way, because under both,
Antwerp@C has no position and GO4ZERO's chain is unresolved.

#### Corollary: an address places a row only where it is the address of the works

An operator's published address is one of the source types that may put a works
on the paper — the company knows where its works is. What that type does not
carry is any claim about which of the company's addresses it is. **A registered
office, a filing address, a correspondence address or a headquarters is an
address for serving papers on a company, and it never places a works**, however
plainly the operator publishes it and however official the register it is filed
in. The coordinate rule asks what the address is an address OF, and only the
source can answer that.

The pair that settled it, both read on 5 September 2026:

**Iváncsa is placed.** SK On publishes `H-2454 Iváncsa, SK út 1.` on its
Hungarian site as the location of the works, and `HRSZ 99/48 Iváncsa 2454` — the
land-registry parcel — as the same thing on its global places-of-business page.
The address is the works', the operator says so, and the point stands on it.

**Giga Arctic is refused.** The Norwegian company register carries T1 ENERGY
GIGA ARCTIC AS and T1 ENERGY NORWAY AS at `Terminalveien 22, 8624 Mo i Rana`,
and Kartverket's address register gives that address a position on gnr 20 bnr
538. It is a *forretningsadresse* — the address the company files — and it sits
at Langneset, the harbour end of Mo Industripark, among warehouses and an office
block, about 2.5 km from the Central Plot where every account puts the
gigafactory. Same source type as Iváncsa, same official quality, and it places
nothing.

The two look identical in a data model that records only "the operator published
an address". They are told apart by reading what was published, which is why the
row carries the address text itself and why the note has to say what the position
walks back to. **The failure this forecloses** is the easy one: a register that
takes an operator's most findable address, geocodes it, and draws a factory on an
office — with every field on the row true and the mark in the wrong place.


### A document is sourced by its author, not by its host

**Ruled 7 September 2026.** A document's provenance is the question of who wrote
it, and that question is not answered by where the file is served from. **An
applicant's own permit submission may place a row while sitting on a third
party's website**, because the statement in it is the applicant's wherever the
bytes live. A campaign group hosting a copy of a company's environmental impact
documentation has not authored anything; it has kept a copy, and a register that
refused to read it would be refusing the company's own words on the ground that
somebody else is holding them.

The allowance is conditional, and the conditions are what make it something other
than an excuse to cite anything found anywhere. The copy must:

  1. **name the applicant** — the company, and enough of its registration for the
     applicant to be identified as the operator the row is about;
  2. **name the procedure** — which authorisation, before which authority, so the
     document can be asked for from the authority by anybody who wants the
     original;
  3. **be internally consistent on the site** — the parcel, the stated area, any
     coordinate and any polygon have to agree with each other. A copy that has
     been edited to say something else about where the works is fails here, and
     this is the condition that does the work.

And the row must record **the host URL, the retrieval date, the SHA-256 of the
file read, and the label `hosted copy`**, which the page renders on the citation.
The digest is the point of the four: it fixes which bytes were read, so a host
that later swaps, truncates or re-issues the file cannot silently change what
this register is quoting. Gated by `_hosted_copy` in check_sector_schema.py.

**The case that settled it.** EVE Power's Debrecen cell plant. The Hajdú-Bihar
county government office serves its notice board to a browser and not to a
declared reader, so the authority's own decision could not be retrieved. The
submission it decided on could: Eve Power Hungary Kft.'s combined KHV/IPPC
application, held by an environmental association, naming the applicant with its
company register number, naming the office and the procedure, and giving parcel
Debrecen 0237/405, the site area 450 000 m², and the central EOV pair
Y 835 619 / X 251 450. The nine-corner polygon in the same document encloses that
pair and comes to 450 022 m². Three facts written independently in one document
that agree to within a rounding — which is a document about this site, whoever is
serving it.

**What this does not open.** It is not a licence to cite a copy in place of an
original that answers. It is not a licence to cite a host's *description* of a
document, or an extract, or a re-typing: the file itself is what is read and
hashed. And it says nothing about authority for the claim — an applicant's plan
remains a plan, which is why the Debrecen row lands as `announced` and takes its
capacity as the figure the applicant filed rather than as a plant that exists.

### A conversion is either implemented here or asked of a library, and never half

**Ruled 7 September 2026.** sources/osgb36.py and sources/utm.py implement their
own projections because a transverse Mercator inverse is a published series that
can be transcribed and held against a published worked example. EOV is not that:
a double projection through a Gauss sphere onto an oblique cylinder, on a datum
some ninety metres from WGS84. **Where the definition is beyond honest
transcription, the conversion is asked of pyproj by EPSG code rather than
hand-written**, and sources/eov.py names EPSG:23700 and does nothing else.

What does not change is the recompute contract. The stored latitude and longitude
are still whatever the module returns from the document's own easting and
northing, on every build, and the module still self-checks on every gate run —
here against EOV's definitional origin, a round trip, and the grid's own
orientation. What changes is only who owns the arithmetic.

**A gate dependency is installed everywhere the gates run, not everywhere
somebody remembered.** pyproj is the first thing the gates need that the standard
library does not carry, and the first build after it was added passed on the
laptop that added it and failed on the deployment — which is the worst shape a
dependency can have. So it lives in `sources/requirements-gates.txt`, separate
from the fetcher's heavier `requirements.txt`, and `sources/ensure_gate_deps.py`
installs it at the head of the prebuild. Where it cannot be installed the gate
**fails**: a coordinate check that quietly does not run is worse than one nobody
wrote.

Superseded 7 Sep 2026 by the paragraph above: pyproj joins the fetcher's own
dependencies in `sources/requirements.txt` — the first one the GATES need rather
than the fetcher — and the gate **fails** when it is absent rather than skipping
the check: a coordinate check that quietly does not run is worse than one nobody
wrote.

WHY THE SUPERSEDED PARAGRAPH IS STILL HERE. A ruling is a record of what this
register decided and when, and a record that silently loses its earlier readings
cannot be audited — a reader who finds a row written under the old arrangement
has nothing to read it against. So a ruling is never deleted, only superseded in
place, with the superseding paragraph above it and the date on the line that
says so. The two here disagree about one thing only: which file the dependency
lives in, and therefore whether every environment that runs the gates installs
it.



### capacity_basis is read from the source sentence, never derived from status

`capacity_basis` is one of `announced`, `fid` or `operating`, and it records how
firm the FIGURE is — at what stage of the project the number in
`capacity_value` was stated. The project's own `status` records something else:
how far the project has got. The two look alike, they are often equal, and the
temptation is to fill the first from the second, because the second is already
on the row and never missing.

**They are not the same field and one is never computed from the other.** A
company announces a 60 GWh plant, takes FID on a first 20 GWh phase and says
nothing new about the rest: the status is `fid` and the basis of the 60 GWh
figure is still `announced`. A plant that reached `operating` on a capacity
nobody has restated since the announcement carries an `announced` basis while
operating. Deriving the basis from the status would silently promote every one
of those figures to a firmness no source gives them, and the promotion would be
invisible — the field would still be populated, still be in the enum, and still
be wrong, in the direction that flatters the dataset.

So the basis comes from the sentence the figure comes from, and where the source
states a figure without saying at what stage it was fixed, the basis is what the
sentence supports and not what the ladder suggests.

**A grant award is `announced`, not `fid`.** This is the case that forces the
ruling, because a grant is the most FID-like thing that is not one. An
Innovation Fund award, a state aid clearance or a national programme's grant
list is a third party committing ITS money, on a capacity the applicant put in
the application. It is not the board of the company committing the company's
money to build that capacity, which is what FID is and what an `fid` basis
asserts. The award moves the project's status — that is what the `funded` rung
is for — and it leaves the basis of the capacity figure exactly where the
company's own announcement left it.

The consequence is that a capacity with no stated stage stays `announced`
however much money is visible around it, and a row whose source states no figure
at all leaves `capacity_value` empty rather than borrowing one from a grant
document.


### Admission and capacity are separate questions

**Ruled 7 September 2026, reversing a ruling of the same day.** For one commit
this register held that a row whose admitting source states no capacity should
never have been admitted, and seven battery rows were moved back to the candidate
list on that reading. The reading was wrong and the rows are restored. It is
written down here rather than quietly reverted, because the wrong version was on
the branch and somebody reading the history is entitled to know why it went.

**Admission requires a company-confirmed site.** That is the whole of the
admission test: the company itself has confirmed a named site, in Europe as this
platform draws it, making battery cells. What admits a row is that the operator
says the works is theirs and says where it is.

**Capacity is a separate attribute of an admitted row, and it has two acceptable
origins.** Either a **company statement**, or an **official record naming the
site** — a permit, a state aid decision, a host-state grant decision. A figure
from an official record is recorded with `capacity_basis: "official"`, which
exists so that the two origins can be told apart in every series built on them: a
number the company gave an authority, or a number an authority was willing to pay
against, is not the same claim as the company saying today what it is building
towards.

**A row with neither stays admitted with an empty capacity.** It is a real works
that a real company has confirmed, and the register knows where it is and who
runs it. What it does not know is how big it is.

The consequence is a rule about arithmetic, and it is the reason the two
questions had to be separated:

- **a row with no capacity is INCLUDED in count-based statistics.** How many
  battery projects were cancelled is a question about projects, and dropping the
  ones whose size nobody published would answer a different question — and answer
  it in a predictable direction, because the sites that never published a figure
  are disproportionately the ones that failed early.
- **a row with no capacity is EXCLUDED from capacity-weighted statistics**, of
  necessity: there is nothing to weight it by.

**So every summary prints the number of rows without a capacity, per sector,
beside the capacity-weighted tables it affects.** A weighted total with a silent
denominator is the failure this rule exists to prevent: it reads as a statement
about the sector when it is a statement about the part of the sector that
published a number. The count is printed whether it is zero or not, so that a
reader never has to work out whether it was checked.

**Why the earlier ruling was wrong.** It conflated the scale threshold with the
admission test. The perimeter's "at least 1 GWh per year" is a rule about which
sites are big enough to be worth holding, and it was never a rule that the
admitting document must be the thing that states the figure. Applied as the
latter it deleted seven real, company-confirmed works — Tesla's own Berlin cell
line among them — from a dataset whose whole purpose is to count what is being
built and what stops. It also had the effect of making the dataset look complete:
25 rows all carrying capacities, with the gap moved somewhere the totals could
not see it. A register that improves its own numbers by dropping the rows that
embarrass them is measuring itself and not the sector.

### The hydrogen perimeter

**Written 9 September 2026, brief 7.** The fourth sector this platform holds
projects for, and the first whose boundary had to be drawn against three
neighbouring datasets at once — steel, chemicals and clean-technology
manufacturing — rather than against a product.

The reviewed prose, which is what `/coverage` renders:

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

**Six exclusions, each stated rather than left to judgement:**

- **Hydrogen-DRI steelworks are OUT.** A works that makes its own hydrogen to
  reduce iron is a steel project and is already held as one. Stegra at Boden,
  HYBRIT, SALCOS and tkH2Steel are steel rows, not hydrogen rows, and the
  740 MW electrolyser at Boden is a fact about a steel row.
- **Blue hydrogen is OUT of this dataset and is LISTED rather than refused.**
  Methane reforming with capture is a class nobody here has ruled on; it goes to
  `sources/hydrogen_candidates.json` with the reason "blue, out of perimeter", so
  that the day somebody rules, the list of what the ruling affects already exists.
- **Pipelines, stores and import terminals are OUT.** They are what a site
  depends on rather than sites in their own right, and they arrive as asserted
  `depends_on` edges from the sites whose sources name them.
- **Electrolyser manufacturing is OUT.** It is NZIA manufacturing and belongs to a
  later sector, however tempting it is to hold the supplier beside the customer.
- **Pilots and demonstrators below the threshold are OUT.** REFHYNE 1 at Wesseling
  is the case that shows the threshold is doing work: at 10 MW it is still the
  largest PEM electrolyser operating in Europe, and it is out while REFHYNE 2 on
  the same site is in.
- **Methanol, e-fuel and SAF works are OUT unless their own electrolyser clears
  the threshold**, in which case the electrolyser is the project and the fuel
  works is a note on it. La Robla Green is the first case: a 200 MW electrolyser
  feeding a 100,000 t/y e-methanol plant, held as the electrolyser.

**Ammonia synthesis fed by electrolytic hydrogen is IN**, with `transition` read
as `supply_security` unless the source states decarbonisation.

**And the perimeter's binding constraint here is not the one batteries had.**
Batteries stalled on company confirmation — sites the operator had never named,
which is what the composite standard was written for. Hydrogen does not stall
there: these operators name their sites and publish their megawatts. It stalls on
POSITION, because these works are mostly not built yet, and the basemap draws
buildings rather than intentions. That is a fact about the sector's stage, it is
counted in `sources/hydrogen_docket.md` rather than described, and it is the
reason the first pass landed seven rows out of twenty admitted candidates.

### Three units for one electrolyser, and no conversion between them

An electrolysis project is quoted three ways, by three different kinds of source:
the **electricity the electrolyser draws** (MW input), the **hydrogen it makes**
stated as a power or as a flow (MW output, Nm³/h), and the **tonnes a year** it is
expected to produce. They are related only through an efficiency and a capacity
factor, and the source almost never states either.

**So a row records the figure in the unit its source used, and this platform
never converts between them.** Where one source states the same phase in two
units, both are kept — `capacity_alternates` on the row, with every companion
field the main figure carries — and the row leads with the unit that comes first
in `CAPACITY_UNIT_PREFERENCE`, which is MW input where it exists. The gate refuses
a row that leads with a lower-ranked unit while carrying a higher-ranked
alternate, so the choice is enforced on the row rather than made invisibly in an
export.

**The reason this is a ruling and not a preference is the IEA's own database.**
Its "estimated normalised capacity" column is the number every hydrogen study
compares against. Its definitions sheet describes that column as
"estimated normalised hydrogen production capacity in MW H₂ output (LHV)", and
then gives the factors it was computed with — 0.0046 MW per Nm³/h for alkaline,
0.0052 for PEM, and the gloss "0.0045 MW/Nm³ H₂/hour (equivalent to 50 kWh/kg
H₂)". Fifty kilowatt-hours per kilogram is electrical input; the lower heating
value of hydrogen is thirty-three. **The column is input and the sentence above it
says output.** Two readings of one column, in one file, from the body that
publishes it.

A register that converted between these units would inherit that ambiguity and
hide it behind a number of its own. So it does not convert, and the one place a
factor is applied — counting the benchmarks' European entries at or above 100 MW
in `sources/build_hydrogen_benchmark.py` — applies the IEA's own factor to the
IEA's own rows, labels every count that rests on it, and touches no row here.

### Reason as stated, or unstated

**Every event that moves a project to `paused` or `cancelled` carries a
`stop_reason`** from a closed list — `finance`, `offtake`, `policy`,
`infrastructure`, `cost`, `ownership`, `unstated` — read from what the source
says and from nothing else. A reason that is not `unstated` carries the sentence
it was read from, in `stop_reason_verbatim`.

**`unstated` is a real answer and is expected to be the commonest one.** A company
that stops a project without saying why has told us something. Filling that space
with the most plausible reason would turn the single most interesting fact about
industrial attrition — that reasons are usually not given — into a distribution of
reasons somebody invented, and it would do so in whichever direction the person
filling it in found natural.

**The rule is required on the event that STOPS the project and on no other.** A
later entry about an already-paused project reports on it rather than stopping
it — Slite's withdrawn permit application, Lyten's memorandum over a site that
has been still since 2024 — and asking each of those for a reason would make the
register restate one cause every time somebody wrote about a consequence. The
test is the positional one the whole layer uses.

**It binds on every sector, and it did not on the day it landed.** Nineteen
stopped events predated it and were reported rather than failed, on the ruling
that the only honest backfill is a re-read. The re-read was done on 9 September
2026 and the exemption is gone. Fifteen stopping transitions now carry a reason
from their own sources; where the quote comes from somewhere other than the
event's own source — a company saying why on the day a trade publisher this
pipeline cannot read reported it — `stop_reason_source_url` carries it, so the
event keeps its date and the quote keeps its provenance.

**What the re-read found is the argument for the field.** Six of the fifteen give
no cause at all: a company that stops two factories and says only that the
"prerequisites" to restart them "were unlikely to be met"; a council that records
"Das Vorhaben wird nicht mehr umgesetzt"; a Gazette notice that states an
appointment of administrators and nothing else. Two more state a cause the
vocabulary cannot hold — an owner changing the business it is in, and a venture
losing its technology partner — and both are filed at their nearest value with
the quote beside them and the misfit written on the row rather than smoothed
into it. **And several sources give more than one reason** where the field takes
one: SVOLT names tariffs, unevenly distributed subsidies and a lost customer
project in a single sentence. The field takes the thing that changed and the
quote keeps the rest.

### An asserted edge carries the sentence; a structural edge is not written by hand

A hydrogen site is defined by what it is attached to: the power it draws, the
pipeline it feeds, the works that buys the molecule. Two kinds of edge say so and
only one of them is data.

- **Asserted.** The project's own source names the thing — "the hydrogen will be
  delivered to the refinery in Gonfreville", "directly connected to the hydrogen
  core network". It carries `kind` (`supplies` or `depends_on`), `type`
  (`infrastructure`, `material`, `regulatory`, `funding`), a `since` date and the
  evidence with its verbatim. This is what is authored.
- **Structural.** It follows from the technology — every electrolyser needs a grid
  connection and water, every DRI furnace needs hydrogen — and it is **not**
  authored on a row. It follows from a technology rule, applied once, so that the
  graph can always say which of its edges somebody asserted and which it derived.

**The gate refuses a hand-written structural edge**, by name, for that reason: two
kinds of edge that look identical on the page, with only the author knowing which
is which, is a graph nobody can audit. `EDGE_CLASSES` carries the value so the
refusal reads as a rule rather than as a missing feature.

### A 200 with an empty body is a refusal, and the link checker cannot see it

A publisher that answers a declared reader with **HTTP 200 and a document
containing the page title, the navigation and no article** has refused it. The
page is there; a browser renders it; a link checker calls the line green,
because by every test a link checker has, it is.

**This is a third state and it needed naming.** The first is a 403, which says
"not to you" and which `BOT_HOSTILE` in `sources/check_links.py` reports and does
not fail. The second is `refused_declared_reader`, which is stronger than a host
list: a named person opened this exact URL on a stated day and found the document
there. The third is this one, and it is the quietest of the three — nothing fails,
nothing is reported, and the only symptom is that a source nobody can quote sits
on a row looking exactly like a source somebody can.

**Two publishers on this file are in it and they cost different things.**
shell.com serves eighty-five characters to a declared reader: the row for
REFHYNE 2 therefore quotes the REFHYNE consortium's own site instead, which is
the operator speaking through the project it leads, and Shell's URL is queued.
galp.com is worse and more interesting: the article text comes back and the
**publication date does not**, because Galp renders every date in the browser. An
undated statement cannot date an event, so a project with a final investment
decision has its history dated from its lender's release instead, and Galp's page
is cited beside it carrying no date and dating nothing.

**Both are queued in `sources/manual/wanted`,** with what filing each would close
— a schedule this register does not hold, and an FID event this register cannot
date. A person with a browser closes either in a minute.

**What is NOT the answer is a browser's name in the User-Agent.** That recovers
the appearance of a citation and none of it, and the reasoning is the same one
`check_links.py` already sets out for the 403s: an honest identity is what makes
a refusal visible, and a refusal that is visible is a fact on the record rather
than a green line nobody checked.

### A site may be placed on the works it stands on

**Ruled 9 September 2026, on the hydrogen docket's D13.** A project whose own
outline nobody has drawn may take its position from the **host works** — the
refinery, chemical park or power station it is being built inside — and the row
says so in three places: `location_precision`, `host_works`, and the sentence over
the picture.

**Why the earlier reading had to give.** The hydrogen pass admitted twenty sites
whose operators name them plainly and publish their capacities, and could draw
seven. The other thirteen failed on position alone, and not because anybody was
hiding anything: these works mostly do not exist yet. They are construction
fields inside somebody else's fence, and a rule that admits a site only once a
volunteer has drawn the building is a rule about OpenStreetMap's coverage of
things that have not been built. That is the same reasoning that widened the
coordinate vocabulary past `basemap` when batteries hit ACC's Kaiserslautern
site, applied one turn further on.

**What it does not do is lower the standard.** The coordinate is still a shape
somebody independent drew, carrying a works' own name, quoted with its tags. What
changes is which works: the point is the ground the installation stands on rather
than its own outline, and the difference is a few hundred metres inside a fence
the company named.

**So it is recorded rather than absorbed.** `location_precision` — `works`, `parcel`,
`point` or `none` — says how the position was resolved, on every site of every project
in every sector, and is checked against the source type that produced it.
`host_works` names the works where the point is not the installation's, and the
gate refuses one without a note. The standfirst over a project's crop says
"Its position is the Petronor refinery, the works it stands on, rather than the
installation itself", and the sector overview says how many of its marks are
which. A reader who thinks the ruling is wrong can see exactly which marks it
moved.

**And the ruling did not land everything.** Three of the thirteen came in on it:
Hamburg Green Hydrogen Hub onto the dead Moorburg coal station, Uniper onto its
own Maasvlakte power station, Repsol onto its Tarragona refinery. The other ten
have no works polygon of ANY kind — not the installation's, not a host's — because
they are greenfield sites, port estates and industrial parks, and an estate
polygon is refused on the rule Subotica and Mo i Rana already settled. The
constraint moved; it did not vanish.

### Position is not an admission leg

**Ruled 9 September 2026, and it reverses the oldest rule on the geography
layer.** A project the perimeter admits is held whether or not anybody can place
it. `located: "no"` on the row is the state, and it is a state rather than an
absence.

**Why the old rule had to go, and it is not the reason the host-works ruling
went.** That one was about which works a coordinate may be taken from. This one
is about whether a coordinate is a condition of existing. The hydrogen pass
settled it: twenty sites whose operators name them and publish their capacities,
of which ten had no works polygon of any kind — not their own, not a host's —
because they are construction fields on reclaimed land, in ports, inside
industrial parks and on greenfield. Holding position as an admission leg meant a
register of European hydrogen that omitted Shell's largest plant, Air Liquide's
second one, the largest single electrolyser figure any company on the file
states, and the only project on the file with an insolvency in its history.
**That is not a cautious register. It is a register that reports the coverage of
OpenStreetMap and calls it industry.**

**TWO FIELDS, TWO SCOPES, from later the same day.** `located` is `yes` or `no`
and sits on the ROW; `location_precision` is `works`, `parcel` or `point` and
sits on each SITE, only where the row is located. One name was doing two jobs at
two scales — `none` could only ever be a row and the other three could only ever
be a site — which is coherent and unreadable, and the gate now refuses each in
the other's place.

**What the row owes instead.** A `location_note` saying WHERE A POSITION WAS
LOOKED FOR AND WHAT WAS FOUND, which is what stops this from becoming the place
coordinates go to be avoided. The ten notes name the sweeps: Maasvlakte from
51.94 N to 52.00 N; Emden, where the Volkswagen works and thirty builders' yards
are drawn and the electrolyser is not; HØST, whose only feature is an office;
Lubmin and Rostock, where what exists is an estate and a port and both are
refused on the rule Subotica and Mo i Rana settled; La Robla, where the one
polygon found is the biomass half of a project this perimeter holds the
electrolyser of.

**And it is said everywhere it matters.** The row is counted in every count-based
statistic. The sentence over the sector overview names it in a clause of its own
— **"no citable source places the works"**, which is a third reason beside
"cancelled" and "location not sought", and the three do not mean the same thing.
Its own page renders **without** the location section rather than with an empty
one, and the sentence there says the company has confirmed the site, that nobody
has drawn it, and that the row is held anyway.

**What has not changed is what a coordinate means.** A row that HAS one still
carries a shape somebody independent drew, quoted with its tags, at a stated
precision. Nothing was softened; a second, honest state was added beside it.

### An owner is a list, and a stop has an ordered list of reasons

**Two fields became lists on 9 September 2026, for the same reason: a single
value was making the register choose, and the choice was invisible.**

**`owners` is `[{name, share, listing}]` and `owner_listing` is read off it** —
the listing of the party holding more than half, and `mixed` where nobody does.
The gate checks the derivation rather than trusting it. Hamburg Green Hydrogen
Hub is the case that forced it: 74.9 per cent a private asset manager and 25.1
per cent a city utility, where the single field said `private` and a reader had
no way to see that a quarter of it is the Free and Hanseatic City of Hamburg. A
50:50 venture would not have been sayable at all. HyTechHafen Rostock is a
four-way venture with no stated shares and is `mixed`; Catalina is five-way.

**AND `unknown` IS THE FOURTH VALUE, for the state where the split itself is not
on file.** EWE AG is not listed on an exchange and is held by municipal
associations together with a private investor, and no source read here says in
what proportion — so `private` and `state-owned` would both be assertions, and
`mixed` is a statement about a split between named parties rather than about one
nobody here can see. The row carried nothing at all for part of a day, which
could not tell "the sources do not say" from "nobody asked". `unknown` can, and
it still carries the note. The fifty-one rows that predate the field are reported on every run,
not failed, on the same reading the stop-reason backfill was done under.

**`stop_reason` is an ordered list, first entry primary.** Sources give more than
one and the single-valued field pushed the rest into prose where nothing could
count them: SVOLT names threatened tariffs, unevenly distributed subsidies AND a
lost customer project in one sentence; Northvolt names a financing failure and
then four things that eroded the position; ArcelorMittal names energy costs and
then weak demand and high imports. **The first entry is what CHANGED** — what
stopped the project now, as against the conditions it was already living with —
and it is what a single-reason series should be built on. `unstated` may only
appear alone.

**Three values were added because re-reads demanded them.** `strategy` is the
owner changing the business it is in, which FREYR did and which `ownership`
described as the owner changing hands. `partner` is a party the project cannot
proceed without withdrawing or failing, and it is neither the owner nor the
customer: NOVO Energy has money, a site and a customer, and no technology.
`maturity` is the owner citing its OWN readiness — the technology or the supply
chain that would build it — which is what Gigastack's consortium said and what
`policy` could only describe by reading their actions instead of their words.
Each had been filed at its nearest value with the misfit written on the row, and
each note keeps the record of the day it did not fit.

**THE PATTERN IS WORTH NAMING.** Three values in one day, each found by reading a
source rather than by designing a vocabulary. A closed list is right and it will
keep being wrong, and the way it gets fixed is that a row says plainly it does not
fit — which is what the notes are for and why a nearest-value filing is recorded
rather than smoothed.

### Every absence from a benchmark is a decision, and the residue is printed

`sources/report_benchmark_gap.py` asks the question a reader distrusts a register
over: **what do the outside lists hold that you do not, and is each absence a
decision or an oversight.** It runs over every European entry at or above 100 MW
in either benchmark, at any technology, and puts each into one of six classes —
duplicate of a held row, DRI or other perimeter exclusion, blue, below threshold
on reading, no company-confirmed site, and **not searched**.

**Only the last is a defect, and it is printed by name rather than counted**,
because the answer to it is to go and look. On the first run it held four
entries, of which three carried the benchmark's status "Other/Unknown" — what a
list looks like when it has stopped following a project rather than recorded that
the project stopped. Two became rows, one was a later phase of the first, and one
is refused in `REFUSED_BY_NAME` with its clause, on the same device the
coordinate-source exceptions use: an entry leaves the residue by somebody
deciding, never by a regex widening.

**THE BENCHMARK IS A DISCOVERY ROUTE AND NOT ONLY A SCORE.** The batteries file
recorded that the funding trail found two candidates the perimeter sweep had
missed and said the lesson was worth remembering. This is the second such route
and it is better, because it is exhaustive over a published list and it can be
re-run. It found a paused 100 MW electrolyser at a British refinery that nothing
else here would have reached.

**A RESIDUAL CLASS IS WATCHED FOR GROWTH, NOT ONLY FOR MEMBERS.** "no
company-confirmed site" held nine in ten of the gap on the first run and was
split on the same day into the three states it was hiding: the benchmark says
nothing about where; the benchmark says where and nobody here has read a company
or permit source naming it; somebody read one and was refused. The split falls
almost exactly along the line between the two files — **the academic file has no
location column at all**, and the IEA's live endpoint publishes a coordinate for
every European entry. That coordinate is still refused as a position here, and it
still means the entry says where.

**THE INPUTS ARE SNAPSHOTTED BY IDENTITY AND NOT BY COPY.**
`sources/benchmark_snapshots.json` holds each file's publisher URL, the day it
was fetched, its size and its SHA-256, append-only, and the report verifies the
cache against it on every run and says so either way. The bytes are not archived
because both files are the IEA's database and this repository may not
redistribute it — and a hash does what "Snapshots are append-only" asks of an
archive, which is to make a published number reconstructible after the register
has moved on, without holding a copy nobody may pass on. A refreshed benchmark is
a new entry: the counts in the docket stay attached to the file they were computed
from.

**And it found the reason a register cannot simply follow a list.** That project
is in the October 2023 academic file twice, with an unknown status, and is gone
from the live IEA file altogether. A register built by tracking the benchmark
would have recorded its existence and never its pause: **a project that vanishes
from a database is a project whose failure nobody counts.** The report is re-run
whenever either list is refreshed.

### An event date carries its precision, and is padded to the earliest it can be

**Ruled 9 September 2026.** An event date is always written as a full
`YYYY-MM-DD`, and `date_precision` — `day`, `month` or `year` — says what the
source actually gave it to. A month-precision event sits on the **first of its
month** and a year-precision event on **1 January**, because that is the earliest
the event can have happened.

**It is the opposite convention from a stated target and for the same reason.** A
target is read at the END of its period — "2029" is not missed until 31 December
2029 — and an event is padded to the START of its. Neither may claim more than
the source did, and the two rules point in opposite directions because
overstating a promise and overstating a date are opposite errors.

**What it closes is a convention that lived in prose.** The Italvolt row carried
`2024-01-31` for a bankruptcy the source dated only to "January 2024", with a
note explaining that the month's END had been chosen "rather than a claim to
precision". That contradicted the padding rule above, and no count could read it:
a series measuring how long that project lasted would have taken the 31st for a
day somebody knew. It is now `2024-01-01` at `month`, and the note records the
correction rather than the old convention.

**And it is what let Galp's own decision onto its own row.** galp.com renders its
publication dates in the browser, so the company's FID release comes back to a
declared reader with its text and no date; an undated statement cannot date an
event, and that row's history therefore began at its LENDER's release, with a
construction event, more than two years after the decision it was about. Galp's
project page says "In 2023, Galp took a decisive step by making the final
investment decision … and 100 MW of electrolysers for the production of green
hydrogen." The company said a year. The register can now hold a year as a year,
rather than as a false day or as nothing at all, and the EIB entry becomes what
it always was — the corroboration rather than the spine.

**A STATEMENT IS AN EVENT TOO.** `stated_schedule` entries carry the same field
on the same rule: the date there is the day the promise was made, and a company
that said something "in November 2021" said it then whether or not the page
carries a day. What the ENTRY promises keeps its own `target_precision`, read at
the end of its period; the two fields sit side by side and answer opposite
questions about the same line.

**AND IT IS NOT ONLY EVENTS — ruled one turn later, the same day.**
`capacity_as_of`, an alternate's `as_of` and a parameter's `date_of_value` carry
`..._precision` on the same vocabulary and the same padding. They are dates of the
same kind, answering the same question: when was this true, and how exactly does
the source say so.

The cost of their not having it was visible for exactly one day, on the Galp row.
Its capacity had to stay on the EIB's sentence — `announced`, because the brief
makes a lender's approval that — while the row's own history showed a final
investment decision, because the company's sentence states the figure and the
decision together and is dated to a year, and `capacity_as_of` could not say so.
It can now. **The figure is on the company's sentence at `fid`, dated 2023 at year
precision**, and the EIB's sentence stays on the row as what it is: a second
source, two years later, on the same 100 MW.

**Nine other values moved with it**, all of them already padded and saying so only
in prose — four Innovation Fund grants dated to a month, a journal figure dated to
a month, two Comext import totals and two cost premiums dated to a year, and one
capacity from a permit application dated to a month.

**PADDED IN STORAGE, UNPADDED ON THE PAGE.** The padding is right for storage and
for arithmetic and wrong on a surface: "as of 2025-01-01" under a cost premium the
source dates to 2025 claims a day nobody published, which is the error the field
was added to prevent, arriving one layer further out. So `sources/build_lead.py`
undoes the padding for display from the same field, in one place — a year shows as
a year, a month as a month — and the cement and steel lead blocks went back to
saying "as of 2025" the moment they were rebuilt. A source's own `date` has no
precision field yet and is printed as stored; that is the next one to look at.

**One convention for every date that says when something WAS, and the opposite one
for a target.** Padded to the earliest it can be, against read at the end of its
period. Both are the reading that does not overstate, and they point in opposite
directions because overstating a promise and overstating a fact are opposite
errors.

### A source date carries its precision; a retrieval date is always a day

**Ruled 9 September 2026, closing rule 21.** Every entry in a `sources` list
carries `date_precision` beside its `date`, on the same vocabulary and the same
padding as an event. `retrieved_date` does not, and is gated to the day shape
instead — the two are different kinds of date and the rule says so rather than
treating them alike.

**A publisher's date is as exact as the publisher made it.** Most are days. ITM
Power's Gigastack phase-2 report carries November 2021 and no day; a journal issue
is a month; a statistical release can be a year. Those are stored padded to the
first, like every other date on this layer that says when something WAS.

**A retrieval date is a day because there is no vaguer version of the fact.**
Somebody here fetched a page, on a day. The asymmetry is enforced rather than
remembered: a `retrieved_date` that is not `YYYY-MM-DD` fails.

**AND A SOURCE DATED TO THE DAY IT WAS READ IS STILL A DAY.** Several sources on
this file are standing pages their publishers never dated — refhyne.eu, hghh.eu,
laroblagreen.com, hoestptxesbjerg.dk, galp.com — and their `date` is the day this
register read them. That is `day` precision and it is honest: the date IS known
to the day, because it is a fact about the reading. What it is not is a
publication date, and each of those rows says so in its own note. The precision
field cannot carry that distinction and is not being asked to.

### No surface renders a date at finer precision than its field records

`sources/check_date_precision.py`, in the postbuild chain beside the anchor and
capacity-clause gates. It exists because **a page had already broken the rule**:
the first build after the precision fields landed printed "as of 2025-01-01" on
the cement and steel lead blocks, under a cost premium the International Energy
Agency dates to 2025. A day nobody published, rendered confidently, from a field
that knew better.

**Two checks, and the second is the honest half of the first.**

- **The built data a surface reads.** Every lead file, with each `as_of` traced
  to the field it was copied from. Exact and exhaustive.
- **The rendered pages, by literal.** Every padded date on the layer is looked
  for in the built HTML, with the React flight payload stripped first — that blob
  carries the stored row, padding and all, because the client needs the data and
  not only the text, and a gate that read it would fail every page for holding a
  date correctly.

**AMBIGUOUS LITERALS ARE REPORTED AND NOT FAILED, and the list is the interesting
part.** The Innovation Fund's Ifestos grant was signed on 1 January 2024 and
Italvolt's bankruptcy is padded to the same string; Slite's permit application
really was withdrawn on 1 January 2026. A page printing one of those in full may
be right, and this gate cannot tell which row it came from. Failing them would
push somebody to stop recording real first-of-month dates, so they are printed on
every run with a count of the pages that show them. **A literal that is padded on
the file and never a genuine day anywhere is unambiguous, and IS failed.**

The gate found three surfaces on its first run: the status rail on a project page,
the object lead built by `build_object_leads.py`, and the sector lead already
fixed by hand. All three now render through one function, `atPrecision` in
`web/lib/dates.ts`, and a fourth surface that forgets it will be caught by the
build rather than by a reader.

### A slip is one speaker changing its mind

`stated_schedule` records what a project said it would do. Every entry carries a
`speaker` — `company`, `host_government`, `eu` or `other` — which is a different
question from `source_type`. Source type says how the statement reached this
register; speaker says whose statement it is. The two come apart constantly, and
the gap is where the meaning is: the Junta de Extremadura telling its own Assembly
that cells come in December 2028 is a **host government** statement that arrived
through a newspaper, and filing it as "press" would lose the fact that a
government said it.

**A revision is counted only between events of the same speaker.** Two speakers
giving different dates for the same milestone have revised nothing. They
disagree, and that is a fact about the evidence rather than about the project.
It is recorded as a disagreement, with the months between them, and never as a
slip.

The reason is that the alternative manufactures delay. CALB said its Sines works
would deliver in 2027 and the Portuguese government said it would be fully
operational in 2028 — on the same day, 24 February 2025. Nobody changed their
mind and nothing slipped; two bodies were asked at once and gave different
answers. Counting that as a twelve-month slip would turn the register's own
breadth of sourcing into evidence of a project running late, and it would do so
in the direction that makes the dataset look more informative than it is. The
same reading applies to Navalmoral de la Mata, where AESC's 2026 has never been
revised by AESC and the twenty-four-month gap is between the operator and its
host.

**Both numbers are real and they answer different questions.** A slip is evidence
about the project. A disagreement is evidence about who believes what, and on
this dataset it is the larger and more common of the two — which is itself the
finding, and the reason they are printed side by side rather than added.

**What neither number can see is silence.** A company that stated 2026 once and
has never mentioned it again has not kept that date; it has stopped talking about
it. That project shows a slip of zero, and nothing in this layer distinguishes it
from one that is on time. The summary says so wherever the slip column is
printed, because a zero that means "no second statement exists" and a zero that
means "the date held" cannot be told apart here.

### A disagreement is two speakers on the same fact, in any field

The slip rule above settled this for dates. The benchmark search of 10 September
2026 found that the same thing happens to **size** and to **place**, and far more
often: eleven capacity disagreements, nine phasing disagreements and eleven site
disagreements over 54 entries, against two schedule disagreements in the whole
transition file.

The treatment is the same and the fields are new. A `benchmark_disagreements`
entry on a candidate or on a search record carries the `kind`, the reference it
disagrees with, both values, and which speaker said which. **The register does not
pick.** Eneco's own release says its Europoort electrolyser reaches 800 MW and the
IEA's row for it says 225 MW; both are on file, attributed, and the row would
carry the owner's figure with the disagreement beside it, exactly as a schedule
carries the company's date with the government's beside it.

**Three kinds, kept apart, because they are three different claims.**

- `capacity` — the two speakers state a different size for the same thing.
- `phasing` — the benchmark carries as two rows what the owner publishes as one
  plant. This is not a size disagreement even when the megawatts differ, and
  filing it as one double-counts: three entries were mis-filed under `capacity`
  for an hour and were caught because the report printed the same number in both
  columns.
- `site` — the benchmark's coordinate or its own project name puts the works
  somewhere the owner does not. Distances run from 7 km to 700 km, and the largest
  is an entry that contradicts itself: "Barsebäck Hydrogen Hub" is named for a
  place in Skåne and carries a coordinate in Medelpad.

**And a gap under a fifth is not a disagreement.** The IEA states kt H2/y and this
register normalises at a fixed factor, so an owner's megawatts and the benchmark's
normalised megawatts cannot agree exactly even when the speakers agree completely.
Those are recorded as `normalisation_gap` and excluded from the count, because a
conversion artefact filed as a disagreement would make the benchmark look less
reliable than it is — the mirror of the error the slip rule prevents.

**What has no home yet is the row.** These live on candidates and on the search
record because that is where the objects are. `data/transition/projects.json` has
no field for a capacity or a site disagreement, and the first of these forty-four
to become a row will need one.

### A machine classification never writes to the record

It writes to a file whose name says it is machine output, with every verdict null,
and a person moves what survives review. Nothing reaches `sources/` or `data/`
except through that review.

This is not a preference. A classifier built to clear the benchmark gap at scale
matched `nemo.eu` for a Greek project whose place name normalises to an empty
ASCII string — and an empty string is contained in every document; matched
`wilhelmshaven.de`, the city's own website, for a project named after the town;
and searched `crane.com`, a valve manufacturer, for "Green Crane". It wrote all of
that straight into the worklist, where it was indistinguishable from work somebody
had done. Worse, the process that wrote it **outlived the decision to throw it
away**: four copies were still running hours later, quietly restoring the rejected
verdicts under a review that had already rejected them.

The same discipline caught its own error the second time round. The disagreement
sweep of 10 September 2026 wrote 54 proposals to a machine file with `verdict:
null`, and the hand review kept 31, rejected 23 as artefacts of ASCII folding and
adjacent villages, and found one thing neither had expected: a candidate this
register had placed at Bremanger, which is a different project's municipality 150
km up the coast, on no source at all. **A machine that proposes is useful. A
machine that files is a forgery.**

### No run ends with a shell still alive

`python3 sources/check_orphan_jobs.py` at the end of every turn, and act on what
it prints. Background work that outlives the reason it was started is not idle: it
holds a stale view of the world and acts on it. Six shells survived the hydrogen
search — four polling `git log` for commit hashes that had already been superseded,
two waiting on a log file whose writer was dead — and **two of them were armed to
run `gh pr edit 52` with a body that had since been corrected.** They would have
overwritten the correction with the text it corrected, hours after the fact, with
nobody watching.

A background job should carry its own deadline. Where it cannot, the check is the
deadline.

### A municipality name is not a point

`location_precision: "point"` requires a **stated address or a stated coordinate**, from
a company or a permit source. A release that names only the town does not place a works,
and a row whose best source says "in Kokkola" is `located: "no"` — not a point at the town
centre.

The reason is that a town centre is a real position that is wrong. Drawn on a map it
looks exactly like a works somebody surveyed, and nothing on the surface distinguishes
"we know where this is" from "we know which municipality wrote the permit". The register
already refuses an industrial estate's polygon for the same reason at one scale down; a
municipality is that error two scales up.

**This is what most of the forty-four are waiting on.** Of the sources that name a site in
the admission search of 10 September 2026, the commonest shape by far is a company naming
a town — Kokkola, Kristinestad, Esbjerg, Albacete, Nivala — and the second commonest is a
company naming somebody else's works, which the host-works rule already handles. An
address appears in one: Carlton Power publishes "Manchester Rd Carrington, Manchester,
M31 4AY".

### A benchmark's coordinate corroborates a position; it is never one

The IEA's live endpoint publishes a latitude and a longitude for every European entry.
Those coordinates may be used to **decide where to look** and to **agree with** a position
a company or a permit has stated. They may never become the position on a row, and they
may never be the reason a row is drawn.

**Barsebäck Hydrogen Hub is the recorded reason.** The entry is named for a place in
Skåne and its coordinate falls at Njurunda in Medelpad, **seven hundred kilometres north**.
Nothing in the row disagrees with itself except the row. A register that took that
coordinate would have drawn a hydrogen project in the wrong half of Sweden and been unable
to say why, because the only source that placed it there was the one that also named it
after somewhere else.

It is not an isolated defect. The same search found the IEA's second row for Eneco's
Europoort electrolyser at Warffum, 200 km away; ENERTRAG's Falkenhagen plant at
Schwedt/Oder, 150 km away; ErasmoPower2X at Almodóvar del Campo when Power2X says
Saceruela; EnergHys at Borssele when the project's own site says the Van Citters harbour
at Vlissingen-Oost. Eleven site disagreements in fifty-four entries is not noise.

**Corroboration is still worth having.** A permit that gives an address and a benchmark
coordinate that falls on it are two speakers agreeing, and that is worth recording. What
the coordinate cannot do is stand alone.

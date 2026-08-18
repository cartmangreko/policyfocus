# PolicyFocus scope

This file is the triage standard. The watch agent shows it to a model along with
one candidate document and asks: does this belong in the register?

It is written to be read by a classifier, so it states the boundary rather than
describing the project. Every rule here should be decidable from a title, a
CELEX, and a short extract — the triage step does not have the full text.

## What the register is

PolicyFocus tracks **what EU industrial-decarbonisation law requires of firms,
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

Four corrections were forced by mismatches during the reconstruction. Each is
load-bearing and none is cosmetic:

1. **Value added is not a supplier.** FIGARO's `rowIi` includes compensation of
   employees (`D1`), gross operating surplus (`B2A3G`) and the tax rows. Left
   in, they are read as industries selling into the sector: `D1` ranked second
   on the chemicals supplier list, and **chemicals' import dependency came out
   at 42.7 % against the delivered 21.9 %** — a number that would have been
   published, looked plausible, and been wrong by a factor of two.
2. **`refArea` `W2` is a world aggregate**, restating rows already present in
   the file. It double-counts, and before exclusion it accounted for 62 % of
   chemicals' foreign inputs.
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

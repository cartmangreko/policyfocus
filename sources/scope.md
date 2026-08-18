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

**PPWR has been read once.** It is a single-pass file: one independent
extraction, no second pass, and therefore not reconciled. The reconciliation
docket says so and `reconciliation_gate.py` reports it that way. A single-pass
file is honest, not finished — treat its classifications as unconfirmed until
a second read disagrees with them or does not.

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

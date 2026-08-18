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
Act, the CBAM extension, the Omnibus simplification of CSRD/CSDDD, and two
standing acts read at their current consolidation: the Net-Zero Industry Act
(Regulation (EU) 2024/1735) and the Critical Raw Materials Act (Regulation (EU)
2024/1252). Those last two are the baseline the Industrial Accelerator Act
amends and the input-side boundary NZIA's own scope provision defers to, so a
new consolidation of either moves what the register measures against.

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
   chemicals, power, waste, shipping, aviation, automotive, construction,
   batteries and solar, clean tech, or carbon capture and storage — through
   emissions, energy, industrial products, or the trade rules that govern them.

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

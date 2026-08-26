# What the cement layer is missing

This file is part of the data. Everything in `data/transition/` is sourced to a
quoted sentence, which means everything that could not be sourced is *absent* —
and an absence that is not written down reads, on a page, exactly like a fact
that does not exist. So it is written down here: what is missing, what it would
unlock, and which document would fill it.

An entry leaves this file when the parameter, technology or project row lands.

---

## Blocking a number the page states

### IR (EU) 2025/2620 — the exact free-allocation adjustment

The CBAM certificate model subtracts a free-allocation adjustment before pricing
an imported tonne, because gross embedded emissions times the carbon price
overstates the 2026 obligation by roughly an order of magnitude. The adjustment
is modelled as `clinker benchmark × CBAM factor`, which is the right shape and
is not the statutory calculation: Commission Implementing Regulation (EU)
2025/2620 sets that, and it has not been read. Two consequences travel with the
figure as caveats — the clinker line is approximate, and the cement line applies
a clinker benchmark to a tonne of cement, which understates its adjustment and
so overstates its cost.

This is the single most valuable gap on the list, because it is the only one
that makes a number already on the page more accurate rather than adding a new
one.

### EU clinker output — blocks the sector total

`build_importance.py` computes the free-allocation cost as **euros per tonne of
clinker**. Per tonne is the display unit by decision, not by default — cement is
thought about in euros per tonne — but the sector total is a second number and it
is missing.

The agreed method when EUTL lands: verified emissions for activity-code-29
installations divided by the 0.656 clinker benchmark gives an approximate EU
clinker output, with the method stated on the surface; Eurostat PRODCOM is the
cross-check. The data is public and bulk-downloadable. Not a blocker for step 3.

### A primary EU allowance price

`eua-price-spot` is Trading Economics — secondary, and both money models are
linear in it, so it is the single number most able to move a rank. EEX publishes
primary auction clearing prices; a settled series from there would make this
primary and would let the price be a monthly average rather than one day's close.

---

## Bottlenecks stated without a number

### Share of cement CO2 that is process emissions from calcination

`cement-process-emissions` states the constraint without quantifying it: the
IEA's cement page carries the figure in a chart rather than in text, and the
CEMBUREAU page that states it serves a self-signed certificate. The IEA cement
technology roadmap or IRENA would fill it.

### Buyer willingness to pay

`cement-green-premium` now carries the production-cost side of the gap — the
IEA's 75–150% premium for near-zero cement — but not the demand side. The WEF
Net-Zero Industry Tracker is the obvious source and returns 403 to this
repository's link checker; a figure needs to come from the PDF or from RMI's
book-and-claim work.

### Capacity utilisation and closures

The brief lists this as a market bottleneck; it is not in `bottlenecks.json`
because no figure has been read at source. ZKG's 2023 analysis gives 65.3%
cement and 71.2% clinker capacity utilisation for 2021, and EU27 cement
production of 179.5 Mt/a — secondary, and old enough to want checking.

---

## Materials

### Slag and fly ash — the clinker substitute

The material layer carries clinker and captured CO2 and not the third material
the brief asks for. The reason is the rule rather than the effort: an edge here
carries `since` and `evidence` like every other edge in this repository, and no
source stating the substitution has been read. Nothing in the fetched texts
mentions granulated blast-furnace slag or fly ash — CBAM's cement annex lists
clinker, Portland cement and calcined clay, and the IAA's low-carbon procurement
annex names concrete without naming what goes into it.

What would fill it: CEN EN 197-1, which defines the cement types by their
clinker share and is the document the substitution ratio actually lives in; or
the IEA cement technology roadmap for the EU average clinker-to-cement ratio.
Either gives the material, its `substitutes` edge to clinker, and the number
that makes the edge worth drawing.

It is worth more than its size suggests. Slag is the one material that would
join two sectors honestly — it leaves steel as a by-product and arrives in
cement as a feedstock, one node with an edge on each side — and the bottleneck
the original brief names, SCM supply falling as blast furnaces close, cannot be
stated until it exists.

### CN 252329 — Portland cement, non-white, has no material node

The Comext citations on the cement page name what was asked of the dataset,
including the product code and the register's name for it. One of the two calls
resolves and one does not: CN 252310 matches clinker's `cn_code` and renders
"CN 252310 (clinker)"; CN 252329 — Portland cement other than white, which is
the ordinary grey product the sector sells — matches nothing, and the citation
renders the bare code.

That is the right output rather than a bug. `web/lib/citation.ts` names a
product only where the register knows it, and a name invented at render time
would be the citation asserting something the data does not hold. But the
absence is real: the platform tracks the intermediate that carries the CO2 and
not the product that leaves the gate, so the import figure the parameter states
has no node to hang off.

What would fill it: a material row for Portland cement with `cn_code`
"2523 29 00", a `produced_by` edge from the sector, and a `substitutes` edge
from nothing yet — the clinker-to-cement ratio is what makes that edge worth
drawing and it is the same document the slag entry above is waiting on
(CEN EN 197-1). CBAM's cement annex lists the code, and IR (EU) 2025/2621
Annex I quotes it against a default value already in `parameters.json`
("2523 29 00 Grey Portland cement 1,360 …"), so the sourcing is in hand; what
is missing is the node, not the evidence.

Until it lands, the citation renders the code alone, and this entry is why.

### The CRMA strategic raw materials list, as stub nodes

Amendment brief 2 asks for the Critical Raw Materials Act's strategic list
ingested as stubs, for the sectors that come after cement — storage needs
lithium, graphite and black mass on day one. `sources/crma.txt` carries the
articles and not the annexes: Art. 3 says the list is in Annex I, Section 1,
and Annex I is not in the fetched text. `sources/fetch_eurlex.py` against CELEX
32024R1252 with the annexes included is the whole of the work, and it is
ingestion rather than schema — the material kind is built and takes them as
they are.

---

## Technologies

Four of the seven in the brief are absent, each for the same reason: no source
stating a readiness level has been read, and `readiness` is required rather than
defaulted.

- **calcined clay / LC3** — the most consequential absence: it is the route that
  does not need CO2 infrastructure.
- **clinker substitution (slag, fly ash)** — and with it the cross-sector
  bottleneck the brief names, SCM supply falling as blast furnaces close. That
  bottleneck is also absent, and it is the one FIGARO edge that would earn its
  place on the cement page.
- **kiln electrification**
- **non-clinker binders**

---

## Projects

Eight are recorded against the fifteen to twenty the brief asks for. The missing
ones are mostly the smaller and the newer: the 2024 Innovation Fund call's cement
awards (the Commission's March 2026 announcement names none of them
individually), Aalborg Portland, Cemex Rüdersdorf, the French and Polish
projects.

Two project-level facts are missing from rows that exist:

- **Brevik's share of Longship.** The Heidelberg release places the plant
  inside Longship without an amount, so the funding row's `amount` is null with
  a note. The Norwegian government's own Longship documents carry the figure,
  and it matters more than most: Brevik is the worked example, and the state's
  share of it is the number the `cement-subsidy-dependence` bottleneck is really
  about. Two of the four Innovation Fund rows are undisclosed for the same
  reason — the company announced the award and not the size — and the
  Commission's own award tables would close all three at once.
- **Status histories start late.** Several histories begin at the grant or the
  groundbreaking rather than at the announcement, because no primary source for
  the earlier event has been read. The watch agent's project channel will extend
  them forward; backfilling is manual.

---

## Filled since the first pass

Kept briefly, then deleted — a gap list that only grows stops being read.

- CBAM default embedded emissions — IR (EU) 2025/2621, Annex I fallback table.
- Cement import volumes — Eurostat Comext CN 2523 10 and 2523 29, 2025 full year.
- Innovation Fund awards — linked to `ets:FND-03`, €381 m across four projects.
- CCS retrofit capital cost — CEMBUREAU, via the Internet Archive.
- Production-cost premium for near-zero cement — IEA Breakthrough Agenda 2025.

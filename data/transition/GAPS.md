# What the cement transition map is missing

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

- **Brevik's public funding share.** The Heidelberg release places the plant
  inside Longship without an amount, so `amount_eur` is null with a note. The
  Norwegian government's own Longship documents carry the figure, and it matters
  more than most: Brevik is the worked example, and the state's share of it is
  the number the `cement-subsidy-dependence` bottleneck is really about.
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

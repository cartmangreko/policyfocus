# What the cement transition map is missing

This file is part of the data. Everything in `data/transition/` is sourced to a
quoted sentence, which means everything that could not be sourced is *absent* —
and an absence that is not written down reads, on a page, exactly like a fact
that does not exist. So it is written down here: what is missing, what it would
unlock, and which document would fill it.

An entry leaves this file when the parameter, technology or project row lands.

---

## Parameters

### EU cement clinker output — blocks the sector-total money figure

`build_importance.py` computes the free-allocation cost as **euros per tonne of
clinker**, not as a sector total, because no sourced parameter states EU clinker
production. The ranking is unaffected (the missing scalar is common to every
measure in the sector, so it cannot reorder anything) but the headline number an
investor wants — what the phase-out costs the European cement industry in a year
— cannot be stated until this lands.

Candidate sources: Cembureau's activity report and trade statistics (the site
served a self-signed certificate when this was attempted, so it needs fetching by
hand); Eurostat PRODCOM; the EUTL installation-level data. ZKG's 2023 analysis
gives EU27 cement production of 179.5 Mt/a for 2021 and a 74% clinker factor,
which is a secondary source and old enough to want checking before it is used.

### EU cement free allocation and verified emissions (EUTL) — the same gap, one level up

Installation-level allocation and verified emissions from the Union Registry
would let the money model be computed bottom-up per operator rather than per
tonne, which is the form a company-level reader actually wants. The data is
public and bulk-downloadable; nobody has ingested it.

### Cement import volume and CBAM default embedded emissions — blocks the CBAM money model

`model_cbam_certificates` is written and returns "not computable", naming
`cement-import-volume` and `cbam-cement-embedded-emissions`. Cembureau's trade
statistics carry the first (11.3 Mt of cement and clinker imported in 2024,
unverified here); the CBAM implementing act's default values carry the second.
Until both land, the CBAM certificate obligation ranks on bottleneck linkage
alone, which understates it.

### Share of cement CO2 that is process emissions from calcination

The `cement-process-emissions` bottleneck states the constraint without a number,
because the number could not be sourced to a quotable sentence: the IEA's cement
page carries it in a chart rather than in text, and the Cembureau page that
states it did not fetch. A figure from the IEA's cement technology roadmap or
IRENA would let the bottleneck be quantified.

### CCS retrofit capital cost per plant

Wanted for the `cement-retrofit-finance` bottleneck. Cembureau's low-carbon
economy site states a range (€100–300 million post-combustion, ~€100 million
oxyfuel) but served a self-signed certificate, so nothing was read from it
directly and nothing was recorded. The project-level figures that ARE recorded —
GO4ZERO's €500 million, the Innovation Fund grants — are a partial substitute.

### Green premium and buyer willingness to pay

Wanted for the `cement-green-premium` bottleneck, which today carries no
parameter at all. The WEF Net-Zero Industry Tracker is the cited source but
returns 403 to this repository's link checker and could not be read; a figure
needs to come from the PDF version or from RMI's work on book-and-claim.

### Capacity utilisation and closures

The brief lists this as a market bottleneck; it is not in `bottlenecks.json`
because no sourced figure exists here yet. ZKG's analysis gives 65.3% cement and
71.2% clinker capacity utilisation for 2021, which needs reading at source before
it is used.

### A primary EU allowance price

`eua-price-spot` is Trading Economics — secondary, and the money model is linear
in it, so it is the single number most able to move a rank. EEX publishes primary
auction clearing prices; a settled series from there would make this primary and
would let the price be a monthly average rather than one day's close.

---

## Technologies

Four of the seven in the brief are absent, each for the same reason: no source
that states a readiness level was read, and `readiness` is required rather than
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

- **Brevik's public funding share.** The brief asks for the Norwegian state's
  share of Brevik; the Heidelberg release places the plant inside Longship
  without an amount, so `amount_eur` is null with a note. The Norwegian
  government's own Longship documents carry the figure.
- **Status histories start late.** Several projects' histories begin at the grant
  or the groundbreaking rather than at the announcement, because no primary
  source for the earlier event has been read. The watch agent's project channel
  will extend them forward; backfilling them is manual.

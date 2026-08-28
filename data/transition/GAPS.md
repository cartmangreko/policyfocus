# What the transition layer is missing

This file is part of the data. Everything in `data/transition/` is sourced to a
quoted sentence, which means everything that could not be sourced is *absent* —
and an absence that is not written down reads, on a page, exactly like a fact
that does not exist. So it is written down here: what is missing, what it would
unlock, and which document would fill it.

An entry leaves this file when the parameter, technology or project row lands.

**One file, one section per sector.** It was "what the cement layer is missing"
while cement was the only sector. Splitting it per sector would have hidden the
entries that belong to neither and to both — the allowance price, the CO2
network, the slag that leaves one industry and arrives in the other — so the
sector sections sit under a shared one instead.

---

## Across every sector

### A primary EU allowance price

`eua-price-spot` is Trading Economics — secondary, and every carbon-cost model
on the platform is linear in it, so it is the single number most able to move a
rank. It now moves two sectors rather than one. EEX publishes primary auction
clearing prices; a settled series from there would make this primary and would
let the price be a monthly average rather than one day's close.

---

## Cement

### Blocking a number the page states

#### IR (EU) 2025/2620 — the exact free-allocation adjustment

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

#### EU clinker output — blocks the sector total

`build_importance.py` computes the free-allocation cost as **euros per tonne of
clinker**. Per tonne is the display unit by decision, not by default — cement is
thought about in euros per tonne — but the sector total is a second number and it
is missing.

The agreed method when EUTL lands: verified emissions for activity-code-29
installations divided by the 0.656 clinker benchmark gives an approximate EU
clinker output, with the method stated on the surface; Eurostat PRODCOM is the
cross-check. The data is public and bulk-downloadable. Not a blocker for step 3.

---

### Bottlenecks stated without a number

#### Share of cement CO2 that is process emissions from calcination

`cement-process-emissions` states the constraint without quantifying it: the
IEA's cement page carries the figure in a chart rather than in text, and the
CEMBUREAU page that states it serves a self-signed certificate. The IEA cement
technology roadmap or IRENA would fill it.

#### Buyer willingness to pay

`cement-green-premium` now carries the production-cost side of the gap — the
IEA's 75–150% premium for near-zero cement — but not the demand side. The WEF
Net-Zero Industry Tracker is the obvious source and returns 403 to this
repository's link checker; a figure needs to come from the PDF or from RMI's
book-and-claim work.

#### Capacity utilisation and closures

The brief lists this as a market bottleneck; it is not in `bottlenecks.json`
because no figure has been read at source. ZKG's 2023 analysis gives 65.3%
cement and 71.2% clinker capacity utilisation for 2021, and EU27 cement
production of 179.5 Mt/a — secondary, and old enough to want checking.

---

### Materials

#### Slag and fly ash — the clinker substitute

The material layer carries clinker and captured CO2 and not the third material
the brief asks for. The reason is the rule rather than the effort: an edge here
carries `since` and `evidence` like every other edge in this repository, and no
source stating the substitution has been read. Nothing in the fetched texts
mentions granulated blast-furnace slag or fly ash — CBAM's cement annex lists
clinker, Portland cement and calcined clay, and the IAA's low-carbon procurement
annex names concrete without naming what goes into it.

**Half filled by the steel dataset.** `granulated-blast-furnace-slag` now
exists, with a `produced_by` edge from `sector:steel` and a `substitutes` edge
to clinker, both sourced to ZKG 6/2023 — so the node the entry asked for is on
the platform and the two sectors are joined in the graph. Fly ash is still
absent.

What is still missing is the CEMENT SIDE and the ratio. There is no
`consumed_by` edge into `sector:cement`, because that is a claim about cement's
inputs and needs a cement-side source; and there is no substitution ratio, which
is what would make the edge worth drawing rather than merely true. CEN EN 197-1
defines the cement types by their clinker share and is the document the ratio
lives in; the IEA cement technology roadmap carries the EU average
clinker-to-cement ratio.

The bottleneck the original brief names — SCM supply falling as blast furnaces
close — is now sourced on one side and unstated on the other. `parameters.json`
carries `gbs-lost-per-blast-furnace`: 150-800 thousand tonnes of slag vanish
with each blast furnace substituted. That is a fact about steel's transition
that lands on cement, and it cannot become a cement bottleneck row until the
cement-side edge above exists. It is the sharpest cross-sector finding the
platform currently holds and cannot draw.

#### CN 252329 — Portland cement, non-white, has no material node

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

#### The CRMA strategic raw materials list, as stub nodes

Amendment brief 2 asks for the Critical Raw Materials Act's strategic list
ingested as stubs, for the sectors that come after cement — storage needs
lithium, graphite and black mass on day one. `sources/crma.txt` carries the
articles and not the annexes: Art. 3 says the list is in Annex I, Section 1,
and Annex I is not in the fetched text. `sources/fetch_eurlex.py` against CELEX
32024R1252 with the annexes included is the whole of the work, and it is
ingestion rather than schema — the material kind is built and takes them as
they are.

---

### Technologies

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

### Projects

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

## Steel

### Blocking a number the page states

#### The CBAM certificate model, and the CN lines it needs

`cbam:FIN-03` is in steel's sector view on its constraint edge and carries no
euro figure, because `model_cbam_certificates` is written around cement's two CN
lines and cement's import volumes. Steel is the larger CBAM sector by trade
volume, so the number this model would produce matters more here than it does
where the model already runs.

What would fill it: the CBAM iron-and-steel annex read for its CN lines, the
default embedded emissions for each from IR (EU) 2025/2621 Annex I, and Eurostat
Comext volumes per line — then `model_cbam_certificates` generalised over a
sector's lines rather than copied. Tracked as its own issue; the plain block for
`cbam:FIN-03` on steel is deliberately written without a `{money_per_tonne}`
slot until it lands, because a sentence must never ask for a number the platform
cannot compute.

#### EU crude steel output — blocks the sector total

The free-allocation cost is computed per tonne of hot metal, and per tonne is
the display unit by decision. The sector total is a second number and it is
missing, exactly as it is for cement: EUTL verified emissions divided by the
1,248 hot metal benchmark would give an approximate output, with the method
stated on the surface, and EUROFER's own production series is the cross-check.

#### The other route benchmarks

Free allocation is priced on hot metal and EAF carbon steel. The annex to IR
(EU) 2026/1412 also sets benchmarks for coke (0,143), agglomerated iron ore
(0,086) and EAF high alloy steel (0,176), and none of the tracked sites is
recorded as running those sub-installations, so none is a parameter yet. They
are cheap to add the day a project needs one — the model takes a list of routes.

### Bottlenecks stated without a number

#### The electricity price the electric route runs on

`steel-conversion-finance` records that conversions stopped, and ArcelorMittal's
stated reason was the cost of power. No European industrial electricity price
has been read at source, so the constraint names the cause and quantifies the
money that was handed back instead. Eurostat's `nrg_pc_205` series for
non-household consumers would fill it, and it would be the first parameter on
the platform that belongs to the electric route rather than to carbon.

#### Scrap availability, as a volume

`steel-scrap-availability` is quantified by the EAF share of production, which
says how much of the route exists and not how much scrap Europe has. The
constraint is about the second. EUROFER and the Bureau of International
Recycling publish EU scrap collection, consumption and net exports; the export
figure is the one the constraint really turns on, and none of the three has been
read.

### Materials

#### Hydrogen has no consumed_by edge to a plant

`materials.json` allows `consumed_by` to point at a `sector:` or a
`technology:`, and not at a `project:`. Hydrogen is consumed at one pilot site
and by no European industry yet, so neither permitted endpoint states the truth:
`sector:steel` would assert an industry-wide consumption that has not started,
and `technology:h2-dri` confers no sector membership, so the material does not
appear in steel's inputs at all.

The edge recorded is the technology one, which is honest and incomplete. Cement
never hit this because nothing in cement consumed anything. Widening
`consumed_by` to accept a `project:` endpoint — which `produced_by` already
does — is a one-line change to the gate and a decision about the schema, so it
is written down here rather than taken.

### Technologies

Capture on blast-furnace gas is recorded at `pilot` on the DMX unit at Dunkirk,
and it carries **no `abatement_share`**. The source states a capture rate on the
stream the unit treats, which is not the same claim as a share of the site's
emissions — the figure cement's equivalent carries. A source stating what a
full-scale unit would remove from an integrated site's total would fill it.

Two routes in the brief are absent for the usual reason, no readiness source
read: **smelting reduction** (HIsarna and the Belgian and Spanish work around
it), and **electrolytic ironmaking**, which is the only route that skips both
coke and hydrogen.

### Projects

Eight are recorded. The absences are mostly the newer and the smaller: **Tata
Steel IJmuiden**, whose Dutch state agreement has been reported and whose
primary documents have not been read; **the HYBRIT demonstration plant at
Gällivare**, which is the industrial-scale sequel to the pilot that is recorded
and whose permit and investment decisions need sourcing; and the Spanish and
French conversions.

Two project-level facts are missing from rows that exist:

- **The Dunkirk pilot's capture volume.** The Axens release states a capture
  rate and no tonnage, so `captured-co2`'s edge from that project carries a null
  volume with a note. A figure would make steel's contribution to the CO2
  network comparable with cement's.
- **Status histories start late.** Four of the eight begin at the event this
  repository first sourced — the grant, the result, the release — rather than at
  the announcement. The same condition cement's file records, for the same
  reason, and the watch channel extends them forward rather than backwards.

---

## Filled since the first pass

Kept briefly, then deleted — a gap list that only grows stops being read.

- CBAM default embedded emissions — IR (EU) 2025/2621, Annex I fallback table.
- Cement import volumes — Eurostat Comext CN 2523 10 and 2523 29, 2025 full year.
- Innovation Fund awards — linked to `ets:FND-03`, €381 m across four projects.
- CCS retrofit capital cost — CEMBUREAU, via the Internet Archive.
- Production-cost premium for near-zero cement — IEA Breakthrough Agenda 2025.
- Granulated blast furnace slag, the steel side — the node, its `produced_by`
  edge and the volume that vanishes per furnace converted. The cement side is
  still open and is now the only half missing; see Cement → Materials above.
- Free-allocation benchmarks for steel — IR (EU) 2026/1412, Annex, hot metal and
  EAF carbon steel.

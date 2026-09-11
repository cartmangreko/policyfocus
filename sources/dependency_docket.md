# Supplier-side dependency sweep — docket

**Brief 9. Nothing here surfaces.** `projects.json`, `scope.md` and every rendered
page are untouched on this branch. The outputs are four new files under `sources/`
— this docket, `nodes.json`, `edges.json`, `dependency_unmatched.json` — plus the
machinery that produced them and the fetch cache index that says what was read.

Every `verdict` in `edges.json` is null. Every ruling below is provisional and is
listed in DECISIONS with the ids it touches, so a later ruling maps to a known
re-run.

---

## 1. What was swept

Twenty-seven suppliers and stores across five node kinds, 1 January 2020 to 11
September 2026. The perimeter is the brief's and is copied into
`sources/dep_sweep.py:NODES` rather than inferred.

The sweep read **2,673 index and article pages** into a fetch cache that records
url, fetch date, byte size and SHA-256 for every one of them (2,583 returned a body; the rest are recorded refusals)
(`sources/dependency_cache/index.json`, tracked; the bodies are gitignored on the
`sources/cache/hydrogen/` precedent — see DECISION D-9).

### Depth, node by node

`nodes.json` carries a `sweep` block for all 27. Summarised:

| Kind | Nodes | Swept as intended | Blocked or partial |
|---|---|---|---|
| electrolyser_oem | 8 | 6 | plug-power (detail pages 403, read through the IR feed), mcphy (domain gone) |
| capture_technology | 5 | 4 | shell-cansolv (**nothing readable at all**) |
| dri_plant | 5 | 3 | danieli (403, archive partial), sms-group (WAF, archive holds none of its European decarbonisation orders) |
| battery_equipment | 3 | 2 | hitachi (subsidiary 403, corporate page lists five items) |
| co2_storage_or_transport | 6 | 5 | ravenna-ccs (index renders by script; release reached directly) |

**Eight of twenty-seven nodes could not be swept the way the brief intends.** That
is the largest single fact in this docket and it is not a defect in the method:
three supplier websites that existed when these orders were placed do not exist
now, and four more refuse a reader at the door.

---

## 2. Report

### 2.1 Nodes by kind, and what they state about their own capacity

| Kind | Nodes | With a stated capacity | Bases used |
|---|---|---|---|
| electrolyser_oem | 8 | 7 | nameplate ×10, backlog ×2, delivery_commitment ×1 |
| capture_technology | 5 | 2 | backlog ×2, delivery_commitment ×1 |
| co2_storage_or_transport | 6 | 3 | nameplate ×5 |
| dri_plant | 5 | **0** | — |
| battery_equipment | 3 | **0** | — |

**Two whole kinds state no capacity for themselves, and for different reasons.**
A DRI supplier licenses a process and engineers a plant; it has no line with a
rate, and the tonnages in this sweep are its customers' plants. That is a fact
about what the node kind is, and it means the arithmetic in §2.5 can say nothing
about Midrex, Primetals, Tenova, Danieli or SMS group. The battery-equipment
suppliers state nothing because two of the three could not be read and the third
publishes marketing.

Of the twelve nodes that do state a capacity, **eight state more than one figure**,
and the file does not reconcile them. Nel states 500 MW/yr in April 2022, 1 GW/yr
in August 2022, 500 MW/yr for a different factory in February 2023 and 1 GW/yr of
a different technology in December 2025 — and in the last of those says the two
500 MW atmospheric lines are "currently idling". A nameplate is not an output.

### 2.2 Edges

240 edges. By node kind and edge kind:

| | equipment_order | framework_agreement | technology_licence | co2_storage | co2_transport |
|---|---|---|---|---|---|
| electrolyser_oem | 93 | 52 | 2 | — | 1 |
| capture_technology | 9 | 33 | 5 | — | 3 |
| dri_plant | 16 | 5 | — | — | — |
| co2_storage_or_transport | — | 8 | — | 12 | — |
| battery_equipment | 1 | — | — | — | — |

By speaker: **supplier 239, owner 1**. By source type: supplier_press 237,
grant_award 2, owner_press 1.

That single owner edge is worth naming. It is Midrex's page about ArcelorMittal's
Hamburg plant, which says of itself that it is "adapted from a 7 September 2021
ArcelorMittal news release" — a supplier's newsroom carrying somebody else's
announcement does not make the supplier the speaker. **Every other edge in this
file is a supplier talking about itself.** The brief's third instruction — record
both sides where owner and supplier state the same edge — is therefore satisfied
almost nowhere, and §2.3 is why.

**A framework agreement with no named site is 98 of the 240**, 41%. Under the
brief these are recorded with `project_id` null and whether they count as demand
is your ruling. They range from a signed capacity reservation with money behind it
(ITM Power/Shell, 100 MW) to a memorandum to explore a possibility (Aramis, no
counterparty named).

### 2.3 Owner side: 117 rows, 12 that name a supplier

Every admitted row on main was read — all five sectors, all 117 rows, including
the 66 hydrogen rows that arrived with #54.

| Sector | Rows | Name a supplier or store | Empty list | No readable source |
|---|---|---|---|---|
| cement | 8 | 4 | 4 | 0 |
| steel | 8 | 2 | 6 | 0 |
| ccs | 3 | 0 | 3 | 0 |
| batsol | 32 | **0** | 30 | 2 |
| clean | 66 | 6 | 55 | 5 |
| **total** | **117** | **12** | **98** | **7** |

An empty list means the row's own cited sources were read and named nobody on the
perimeter. A row with no readable source is a different thing and is listed by id
in `edges.json`.

**Not one of the thirty-two battery rows names its equipment supplier.** Combined
with a battery_equipment kind that produced one edge, the sweep has almost nothing
to say about who builds Europe's cell lines — from either direction.

**Two of the seven unreadable rows are Plug Power detail pages that the register
cites and a declared reader cannot open** (`plugpower-kokkola`,
`plugpower-kristinestad`). The same text is available through the Q4 investor feed
this sweep used; that is a cheap fix for the register and is flagged rather than
made, because this branch does not touch `projects.json`.

### 2.4 Unmatched customers

**146 customers named by a supplier that match no admitted row.** No rows were
created.

No single class holds most of them. The largest is hydrogen at 20 (14%), then
steel 13, refining 7, waste-to-energy 7, industrial gases 6, cement 6. By country:
Germany 23, United Kingdom 20, France 19, Norway 14, Spain 10.

The answer to the brief's question is therefore **no** — and the shape of the
spread is the finding. This is not one missing class; it is a long tail of
industries the register's five perimeters were never drawn to hold: lime (Lhoist
at Réty), glass (Ardagh at Limmared), aluminium recycling (Hydro Havrand),
manganese smelting (Eramet at Sauda), silicon (WACKER at Holla), paper
(Kimberly-Clark at Northfleet and Barrow), district heating (Stockholm Exergi,
Öresundskraft), waste-to-energy (Twence, Hafslund Celsio, AEB Amsterdam, Fortum
Nyborg, Limeco, Evero), fertiliser and ammonia (Yara at Sluiskil and Herøya,
Iberdrola at Puertollano), and refining (Neste, Moeve, Galp, Bondalti, Essar).

Three unmatched customers deserve naming on their own:

- **Heidelberg Materials appears at three cement works the register does not
  hold** — Padeswood (MHI, 800 kt/yr, in execution after FID), Lengfurt (Linde, 70
  kt/yr) and Edmonton, Alberta — while holding three rows that it does.
- **Aalborg Portland / Cementir** (Air Liquide, ACCSION, 1.5 Mt CO2/yr avoided,
  EUR 220m from the Innovation Fund) is the largest single unmatched cement tonnage
  in the sweep.
- **A Spanish cement producer nobody named** bought ITM Power's first electrolyser
  into the cement industry. A cement edge with an anonymous cement customer is
  exactly the shape the register cannot yet hold.

### 2.5 First read: edge sums against stated capacity

No drafting. Four things are true and they are different from each other.

**(a) Where units match, two nodes are oversubscribed against their own stated
figure.**

| Node | Edge sum | Stated | Difference |
|---|---|---|---|
| tk-nucera | 2,220 MW | 1,500 MW backlog (2025-08-28) | +720 MW |
| sunfire | 1,110.1 MW | 800 MW backlog (2024-12-19) | +310.1 MW |

The arithmetic: tk-nucera 200 (Shell) + 700 (H2 Green Steel) + 120 (Neste) + 300
(Cepsa) + 600 (anonymous FEED) + 300 (Moeve) = 2,220 MW against a backlog the
company stated as "around 1.5 gigawatts". Sunfire 0.72 + 1 + 10 + 3.2 + 20 + 10 +
2.6 + 30 + 30 + 100 + 500 + 100 + 50 + 10 + 2.6 + 40 + 200 = 1,110.1 MW against
"an order backlog exceeding 800 megawatts".

**Neither is necessarily a contradiction**, and the docket will not call it one.
A backlog is a snapshot at a date and these sums run past it; an order announced
can be cancelled, and this file records cancellations as edges rather than
removing them. What the arithmetic does say is that the announced total and the
stated backlog are not the same number and never were.

**(b) One store is oversubscribed against its phase 1 nameplate.** Northern Lights:
Yara 800,000 + Ørsted 430,000 + Stockholm Exergi 900,000 + Eramet 260,000 =
2,390,000 t CO2/yr against a phase 1 nameplate of 1,500,000 t/yr — **+890,000**.
It is comfortably inside phase 2's "minimum of 5 million", and phase 2's FID was
taken on the strength of the Stockholm Exergi contract that causes the overrun.
The capacity and the demand that justified it are in one release.

**(c) One store is contracted exactly to its nameplate and says so.** Porthos:
2.5 Mt/yr, and the FID release states "Porthos has contracted its full storage
capacity". Its four edges — Air Liquide, Air Products, ExxonMobil, Shell — carry
**no quantity at all**, because the release gives only a combined figure and
splitting it would be inventing the split. A store sold out with an unsplit
customer list is a real shape and the file holds it honestly.

**(d) Units prevent the comparison on eighteen of the twenty-seven nodes.** The
cases, by reason:

- **MW against MW/yr.** Every electrolyser OEM except the two in (a). An edge is a
  plant of *n* megawatts; a node capacity is a factory that builds *n* megawatts
  *a year*. ITM Power's 2,753.5 MW of edges against 1,500 MW/yr is six years of
  orders against an annual rate, and subtracting one from the other would be
  meaningless. **This is the single most common obstacle in the file.**
- **A count of things against a rate.** SLB Capturi states "seven carbon capture
  plants" and then "eight"; MHI states "13 commercial facilities". Their edges are
  in tonnes of CO2 a year (3,590,000 and 2,450,000 respectively). Plants cannot be
  divided into tonnes.
- **No stated capacity at all.** All five dri_plant nodes, plus plug-power, linde,
  air-liquide, wuxi-lead, greensand, porthos's customers, aramis, endurance-nep,
  manz, hitachi, shell-cansolv, sms-group.
- **Mixed units inside one node.** Nel carries MW, "H2Station fuelling station",
  "H2Station fuelling system" and "hydrogen fuelling site" — four units, because
  four releases said four different things and nothing was converted. Air Liquide
  carries tonnes CO2 per **day** (Stockholm Exergi, 3,500) beside tonnes per
  **year** (Cementir, 1,500,000). Primetals and Tenova carry tonnes of DRI a year,
  tonnes of steel a year and tonnes per hour in the same node.
- **A quantity that is not the node's product.** John Cockerill's Volteron edge is
  80,000 tonnes of iron plate a year — an ironmaking output from an electrolyser
  company. Plug Power's H2CAST and Hynetwork edges are tonnes of hydrogen
  delivered, not equipment.

**And 93 of 240 edges carry no quantity at all.** A supplier that says "several
H2Station modules" or "a leading refinery in Europe" has not been imprecise by
accident; it has said what it was willing to say.

### 2.6 Disagreements found

Recorded in the same shape as `projects.json`'s `disagreements` field: the field,
the two values, and which speaker said which.

**D-A — `company`, at Måde, Esbjerg.**
- Speaker 1, Plug Power (2026-06-24): the Måde Power-to-X facility in Esbjerg is
  "developed and operated by **European Energy**".
- Speaker 2, the register (`hoest-ptx-esbjerg`): the plant at "Måde, Esbjerg" is
  **Copenhagen Infrastructure Partners**' HØST PtX, sole owner.
- Either one project whose ownership two speakers state differently, or two plants
  in one place. The sweep does not link it: edge `e0128` carries `refuse_match`.
  **Not touched in `projects.json`.**

**D-B — `capacity`, at Klemetsrud, Oslo.**
- Speaker 1, Aker Carbon Capture (2023-11-24 and 2023-12-04): a Just Catch 400
  "with a design capacity to capture up to **400,000** tonnes of CO2 per year".
- Speaker 2, SLB Capturi (2025-01-27), the same company after a rename: "expected
  to capture **350,000** metric tons of CO2 annually".
- One speaker, two figures, fourteen months apart. Edges `e0146`, `e0148`, `e0156`.

**D-C — `capacity`, at Salzgitter.**
- Speaker 1, Tenova (2022-03-08): Salzgitter "intends to order a DRI plant from
  Tenova with an annual capacity of **2.1 million tons**".
- Speaker 2, Tenova (2023-05-24): the contracted plant "has a production capacity
  of **more than 2 million tons**".
- Edges `e0213`, `e0214`. A softening, not a correction, and both stand.

**D-D — `customer`, on a 40 MW alkaline contract.**
- Speaker 1, Nel (2022-11-14): "a high quality North European energy company",
  NOK 120 million.
- Speaker 2, Nel (2025-04-30): "**Statkraft** has cancelled the 40 MW alkaline
  electrolyser contract".
- The same speaker named the customer two and a half years later, in the release
  that says it is gone. Edges `e0024`, `e0034`.

**D-E — a project date that two parts of one page disagree about.**
Northern Lights' Ørsted release prints "May 15, 2023" in its own dateline and says
in the body that the agreement "is effective from 1 January 2026". The date
heuristic took the second. Caught by hand; edge `e0227` carries the correct date
and the note says what nearly happened.

---

## 3. DECISIONS

Every ruling taken without you. Provisional; each lists what it touches.

**D-1 — The perimeter admits a supplier's European customers whatever the product,
and the unit stays as stated.** Nel's hydrogen refuelling stations are recorded
beside its electrolysers rather than filtered out, with quantity in stations. The
alternative — deciding which of a supplier's products count — is a scope judgement
the brief did not delegate.
*Touches:* the fuelling-station edges on `nel` — `e0003`, `e0004`, `e0012`, `e0013`,
`e0017`, `e0019`, `e0020`, `e0023`, `e0032` — and the "units prevent the
comparison" line for `nel` in §2.5.

**D-2 — A row is identified by a site, and a site name alone is not enough.**
A company alias narrows the candidates and never resolves one; a site alias
resolves only when no company alias points elsewhere. Where they disagree, the
edge keeps `project_id` null and the note says what was seen. Every edge carries
`match_basis`: `site+company` (11), `site only` (9), `explicit` (5), `refused`
(4), `unmatched` (211).
*Touches:* every edge. The nine `site only` matches are the ones to review first.

**D-3 — Edges and nodes carry three fields the brief did not specify: `note`,
`match_basis` and `inherited_by`.** A null field cannot say why it is null. `note`
carries the sentence that makes a reading honest; `match_basis` says what a link
rests on; `inherited_by` records an acquirer.
*Touches:* the shape of `edges.json` and `nodes.json`.

**D-4 — A node is swept for the product its kind names.** Siemens Energy's
turbines, Linde's and Air Liquide's industrial-gas supply contracts, and Primetals'
and Tenova's rolling mills are read and counted, not recorded. Twenty-two of
Siemens Energy's 353 releases concern electrolysis; the other 331 are a different
company's worth of European orders.
*Touches:* the `siemens-energy`, `linde`, `air-liquide`, `primetals` and `tenova`
sweeps; nothing is recorded, which is the point.

**D-5 — For a dri_plant node, an electric arc furnace is recorded when the release
places it inside a stated decarbonisation programme, and not otherwise.** The
boundary is arguable: an EAF is not a DRI plant. Salzgitter's and voestalpine's are
in because the releases call them the first step of SALCOS and greentec steel;
HKM's is in because its transformation is the release's subject; Acciaierie Venete's
is the weakest of its kind in the file and says so.
*Touches:* `e0206`, `e0209`, `e0210`, `e0214`, `e0216`, `e0217`, `e0239`.

**D-6 — Where a supplier's detail pages refuse a reader and its own feed does not,
the edge cites the feed.** Plug Power's `/press-releases/news-details/` URLs answer
403 to a full browser header set; the Q4 feed at `ir.plugpower.com` answers 200
with the same text. The `url` is the artefact that was fetched, hashed and cached;
the public permalink is in the note. Citing a page nobody could open would be
citing something nobody read.
*Touches:* all 22 `plug-power` edges.

**D-7 — (Yours, 11 September 2026.)** A Wayback capture of a release published on
the speaker's own domain is the speaker's document; cite it with the capture
timestamp as source date and file the copy. Applied to McPhy (whole node) and
Danieli (partial). **The capture timestamp is DERIVED from the URL by
`dep_records.capture_note`, never typed** — the two hand-written capture dates had
already drifted from the captures they named before the function existed.
**One thing to confirm:** the edge's `date` field holds the release's own dateline,
not the capture date, because that field is what the sweep period is measured
against and a 2020 release captured in 2024 would otherwise leave the period. The
capture date is recorded in the note. If you meant `date` itself, it is a one-line
change and a re-run.
*Touches:* `e0195`–`e0203` (McPhy), `e0239` and `e0240` (Danieli), and both `mcphy`
capacity entries.

**D-8 — The four false links the matcher produced, and the rule each forced.**
Recorded here as the basis for alias kinds, at your instruction.

| Wrong link | Cause | Rule it forced |
|---|---|---|
| ITM Power's Uniper **Humber H2ub** contract → `uniper-h2maasvlakte` | Company-only match. "Uniper" resolved to exactly one row, so it looked unambiguous — the worst case, because a confident match to the wrong single row produces a link a reader would believe | A company name never resolves a row |
| Sunfire's **Bad Lauchstädt** and **Stenungsund** orders → the same Rotterdam row | Same cause | Same rule |
| Nel's HyCC order at **Delfzijl** → `lhyfe-delfzijl` | Site-only match. Two companies are building two plants in one Dutch town and the town is one of them's site alias | A site match is refused when a company alias points at a different row |
| Every **Shell** and **TotalEnergies** contract in Europe → `northern-lights` | The JV shareholder list in "Northern Lights JV DA (Equinor, Shell, TotalEnergies)" had been split into aliases, making "Shell" an alias of a reservoir under the North Sea | A parenthetical becomes an alias only when it holds no comma |

Two more were caught after the rule was written, both coarse places, and both are
refused by hand rather than by a rule: **"Aberdeenshire"** is a county and put a
gas-fired station at Peterhead onto a hydrogen project at Kintore (`e0166`);
**"Dunkirk"** is a city and put a CO2 export terminal onto ArcelorMittal's DMX unit
(`e0188`). **"Duisburg"** would have put HKM's furnace onto thyssenkrupp's plant
(`e0239`). A rule for "this alias is too coarse" is not attempted; `refuse_match`
with a reason is.
*Touches:* `dep_sweep.aliases`, `dep_records.resolve`, and `e0026`, `e0030`,
`e0058`, `e0061`, `e0092`, `e0094`, `e0128`, `e0166`, `e0188`, `e0239`.

**D-9 — The fetch cache index is tracked; the bodies are not.** Url, date, size and
SHA-256 for all 2,673 fetches are in `sources/dependency_cache/index.json` and in
git history. The bodies are gitignored on the `sources/cache/hydrogen/` precedent,
which was set for the right reason: a repository that redistributes somebody else's
corpus has taken on a licensing question it was never asked.

**D-10 — Supplier nodes carry a `status_history` in the shape `projects.json`
uses.** (Yours.) Same field names, same append-only discipline, same
source-per-entry rule; the `status` vocabulary is the supplier's own, because
`operating` says nothing useful about a company. Nine events on three nodes:
`slb-capturi` (2), `mcphy` (1), `manz` (6).

**D-11 — John Cockerill inherits McPhy's edges by reference, not by copy.** Each
of McPhy's nine edges carries
`inherited_by: {node_id: "john-cockerill", since: "2025-07-08", source_url: ...}`.
The edges stay on `mcphy` because McPhy is who signed them; duplicating them onto
`john-cockerill` would double every sum in §2.5.
*Touches:* `e0195`–`e0203`.

**D-12 — Where an aggregator is cited as a source, the owner-side scan skips it.**
`api.iea.org/hydrogen/project` is one JSON blob listing every hydrogen project in
the world and 22 rows cite it as a benchmark. Scanning it matched six nodes on
every one of those rows. A haystack that matches every needle is not evidence.
*Touches:* the owner-side counts in §2.3 — without this, 39 rows would appear to
name a supplier instead of 12.

**D-13 — The owner-side scan reads paragraphs, not pages, and flags self-naming.**
A page's navigation and related-articles rail name companies the article never
mentions. And a row whose owner is itself a node names that node trivially:
`airliquide-elygator-maasvlakte`, `totalenergies-airliquide-zeeland` and
`northern-lights` name only their own owners, and are flagged rather than filtered,
because "the owner is the supplier" is a finding about the market.

---

## 4. New vocabulary the sweep forced

Flagged, not adopted. Each names the item that forced it.

- **`hydrogen_transport`** — Plug Power's first fill of Hynetwork's 32 km pipeline
  in Rotterdam (`e0127`) is filed under `co2_transport`, which is wrong in kind.
  There is no value for moving hydrogen.
- **A molecule supply is not an equipment order** — Plug Power's 44.5 tonnes of
  hydrogen to the H2CAST cavern project (`e0122`) is filed as `equipment_order`
  because nothing closer exists.
- **`basis` has no value for "sold in a year"** — John Cockerill's "close to 200
  megawatts" of 2021 sales is filed as `delivery_commitment`, which it is not. It
  is neither nameplate nor backlog.
- **`source_type` has no value for a supplier republishing an owner's release** —
  Midrex's ArcelorMittal Hamburg page (`e0192`) is filed as `owner_press` with
  `speaker: owner`, which is right about the speaker and silent about the host.
- **Units that no vocabulary reconciles** — "carbon capture plants", "commercial
  facilities", "H2Station fuelling station", "tonnes per hour", "tonnes of iron
  plate per year", "GWh per year". All as stated, none converted.

---

## 5. Counterparties read and deliberately not recorded

Listed so that a later reader knows they were seen.

**The node is the buyer, not the seller.** Nel buying compressors from Howden;
Sunfire's component partnership with Vitesco (recorded and flagged, because the
direction is the ruling); ITM Power buying membranes from Gore and power supplies
from FRIEM.

**Integration, EPC and reseller partnerships where nobody takes delivery of a
plant.** Nel with Wood, Aibel, Kvaerner, Hydrasun, Saipem and SAMSUNG E&A;
John Cockerill with Technip Energies (recorded, as the Rely joint venture);
MHI with Saipem and KBR (recorded, as technology licences, because a licence is a
sale of the product this node kind names).

**Non-European delivery.** Nel's Korean, Californian, Canadian and Australian
fuelling stations and its 200 MW US order; Plug Power's Allied Green Ammonia and
Uzbekistan projects; MHI's Dofasco and Edmonton work; Tenova's ArcelorMittal
Dofasco DRI plant; Danieli's Algoma and Alter Steel. French Guiana is treated as
outside this sweep's Europe (McPhy/CEOG, `e0203`) and no country is recorded for it.

---

## 6. What a re-run should do first

1. **Rule on D-7's date field** — one line, one re-run, and it moves McPhy's and
   Danieli's eleven edges.
2. **Review the nine `site only` matches.** All nine read correctly by hand, but
   each rests on a place name with no company agreement.
3. **Finish Danieli.** Nine of 107 archive captures retrieved; the Internet Archive
   throttles hard enough that this needs its own run.
4. **Decide whether the 98 framework agreements are demand.** They are 41% of the
   file and the brief reserved the ruling.
5. **The two Plug Power URLs the register cites that a reader cannot open.**
   `plugpower-kokkola` and `plugpower-kristinestad`. The text is in the Q4 feed.

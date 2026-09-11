# Supplier-side dependency sweep — docket

**Brief 9. Nothing here surfaces.** `projects.json`, `scope.md` and every rendered
page are untouched on this branch. The outputs are six files under `sources/` —
this docket, `nodes.json`, `edges.json`, `dependency_unmatched.json`,
`dependency_worklist.md` and `cement_candidates.json` — plus the machinery that
produced them and the fetch cache index that says what was read.

Every `verdict` in `edges.json` is null. Every ruling below is provisional and is
listed in DECISIONS with the ids it touches, so a later ruling maps to a known
re-run.

**REVISED 11 SEPTEMBER 2026 AGAINST GEORGE'S BATCH RULINGS.** What the sweep now
serves is a confirmation-ladder audit whose rung 6 is "an input contracted",
scored per project with a speaker, and a supplier-side view of the same edges for
listed equipment makers. The ladder itself is brief 10 and is not built here. What
this batch did was leave the edges in a shape brief 10 can read: keyed by register
row where matched, and carrying **speaker, firmness, date, source and verdict on
every edge**. Sections 2.5, 2.6 and 3 are the ones that changed most, and two
findings in 2.5 were withdrawn — they were arithmetic, and the dates dissolved
them.

---

## 1. What was swept

Twenty-eight suppliers and stores across five node kinds, 1 January 2020 to 11
September 2026. It was twenty-seven until this batch: Aker Carbon Capture ASA is
now its own node beside SLB Capturi, under the McPhy ruling, and the fourteen
edges it signed stay where they were signed. The perimeter is the brief's and is copied into
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
| capture_technology | 6 | 4 | shell-cansolv (**nothing readable at all**), aker-carbon-capture (own domain serves nothing) |
| dri_plant | 5 | 3 | danieli (403, archive partial), sms-group (WAF, archive holds none of its European decarbonisation orders) |
| battery_equipment | 3 | 2 | hitachi (subsidiary 403, corporate page lists five items) |
| co2_storage_or_transport | 6 | 5 | ravenna-ccs (index renders by script; release reached directly) |

**Nine of twenty-eight nodes could not be swept the way the brief intends** — it
was eight of twenty-seven before the Aker split, and the same two dead domains now
belong to two nodes. That is the largest single fact in this docket and it is not
a defect in the method: supplier websites that existed when these orders were
placed do not exist now, and others refuse a reader at the door.

Each of the nine now carries a `state` block in `nodes.json` naming its
**refusal class**, because the four kinds are not interchangeable and a reader
should not have to infer which from prose:

| Node | Refusal class | What the door actually does |
|---|---|---|
| plug-power | `403` | Detail pages 403; the IR feed answers 200 with the same text (D-6) |
| danieli | `403` | Every path, http and https, with and without www, full browser headers. **incomplete** |
| hitachi | `403` | hitachi-hightech.com newsroom and sitemap both. **incomplete** |
| sms-group | `waf_challenge` | AWS WAF, 202 and a JavaScript challenge, sitemap included. **incomplete** |
| shell-cansolv | `empty_body_200` | 10,475 bytes of markup, **zero characters of text** |
| mcphy | `domain_gone` | mcphy.com does not resolve; www redirects to the acquirer |
| slb-capturi | `domain_unaddressed` | slbcapturi.com has no address record — SLB holds the domain and publishes no host for it |
| aker-carbon-capture | `domain_resolves_serves_nothing` | Resolves to 35.187.120.37; nginx 404 over http, wrong certificate over https |
| ravenna-ccs | `script_rendered_index` | The media index renders by script; the release was reached directly |

**Three of those were checked again on 11 September 2026 and one earlier line was
wrong.** The sweep had recorded that "akercarboncapture.com and slbcapturi.com do
not resolve". Only one of them does not. slbcapturi.com publishes no A record at
all and therefore resolves nowhere on slb.com — but it is not abandoned, because
its nameservers are `dns0/dns1.slb.com` and `dns0/dns1.slb.net`: SLB holds the
domain and serves no host from it, and the live home is capturi.slb.com, which
answers 200. akercarboncapture.com **does** resolve, and serves nothing. "Resolves
and serves nothing" and "does not resolve" are different facts about who can still
read a supplier, and the file now tells them apart.

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

**And now by FIRMNESS, which is the axis rung 6 of the ladder reads.** It is a
second axis and not a refinement of the first: an `equipment_order` can be a signed
purchase order or a letter of intent, and a `co2_storage` edge can be a binding
transport agreement or an agreement to investigate one.

| | contract | framework | intent | total |
|---|---|---|---|---|
| electrolyser_oem | 90 | 53 | 5 | 148 |
| capture_technology | 12 | 33 | 5 | 50 |
| dri_plant | 13 | 5 | 3 | 21 |
| co2_storage_or_transport | 11 | 8 | 1 | 20 |
| battery_equipment | 1 | — | — | 1 |
| **all** | **127** | **99** | **14** | **240** |

**Every one of the 127 contracts and 14 intents cites the sentence it was read
off**, in `firmness_basis`, quoted from the page at `url` — and a gate refuses any
edge whose cited sentence is not in the cached body. That gate caught six bad
citations while this batch was being written, all of them the same mistake, and
none of them would have been visible in a diff.

The 99 frameworks are the 98 `framework_agreement` edges, ruled en bloc under
D-14, plus one `equipment_order` that had to be read down: ITM Power's four
NEPTUNE II units for EDF Renewables and Hynamics at Tees Green Hydrogen (`e0055`,
8 MW) announce an engineering package against **a capacity reservation** the same
release names, and a reservation is not a contracted input.

**Only 14 rows in this register have a contracted supplier edge at all** — 21
contract edges across 14 admitted rows. That is the number rung 6 starts from, and
it is a sixth of the 117 rows on file.

By speaker: **supplier 239, owner 1**. By source type: supplier_press 237,
grant_award 2, owner_press 1.

That single owner edge is worth naming. It is Midrex's page about ArcelorMittal's
Hamburg plant, which says of itself that it is "adapted from a 7 September 2021
ArcelorMittal news release" — a supplier's newsroom carrying somebody else's
announcement does not make the supplier the speaker. **Every other edge in this
file is a supplier talking about itself.** The brief's third instruction — record
both sides where owner and supplier state the same edge — is therefore satisfied
almost nowhere, and §2.3 is why.

**A framework agreement is 98 of the 240**, 41%, and your ruling of 11 September
2026 settles them: they stay as edges to the supplier node, they count toward the
supplier's contracted total, and they never reach rung 6 for any project. They are
verdicted en bloc as `framework` and no source was re-read for one.

**One correction to the sentence this paragraph used to carry.** It said a
framework agreement has no named site. **Thirty-seven of the 98 do name a site**,
and four of those resolve to an admitted row — `uniper-h2maasvlakte`,
`3d-dunkirk`, `salcos-salzgitter` and `northern-lights` itself. The sites are kept
rather than nulled, because a site the source states is a fact about the source,
and the four `project_id`s are kept too: rung 6 excludes them on firmness, which
is the axis the ruling actually turns on, so nothing is gained by throwing the
identification away as well.

They still range from a signed capacity reservation with money behind it (ITM
Power/Shell, 100 MW) to a memorandum to explore a possibility (Aramis, no
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
  kt/yr) and Edmonton, Alberta — while holding four rows that it does (Brevik,
  Geseke, Devnya, Slite). **These now have a file.** `sources/cement_candidates.json`
  opens the cement candidate list for the brief 8 census, in the same shape as the
  hydrogen and batteries lists and read by `report_candidate_gaps.py` on every
  build like both of them. Padeswood and Lengfurt are candidates, each carrying
  `discovered_by` — the edge ids that found it — and the supplier's release as the
  company source. Edmonton is in an `outside_perimeter` list in the same file
  rather than among the candidates: it is in Alberta, this sweep records European
  delivery only, and there is therefore **no edge for it** and no document in this
  file. It is named so that a reader of the candidate list does not have to wonder
  where the third works went.
- **Aalborg Portland / Cementir** (Air Liquide, ACCSION, 1.5 Mt CO2/yr avoided,
  EUR 220m from the Innovation Fund) is the largest single unmatched cement tonnage
  in the sweep.
- **A Spanish cement producer nobody named** bought ITM Power's first electrolyser
  into the cement industry. A cement edge with an anonymous cement customer is
  exactly the shape the register cannot yet hold.

### 2.5 Second read: edge sums against stated capacity, with the dates kept

**TWO OF THE THREE OVERSHOOTS THE FIRST READ REPORTED ARE NOT THERE.** They were
arithmetic done without the dates and without the firmness, and your ruling asked
for both. Nothing was corrected in either speaker's figures; the sums were rebuilt.

**(a) Neither electrolyser OEM is oversubscribed against its own stated backlog.**
A backlog is a snapshot at a date. The honest comparison is against the edges that
existed when the snapshot was taken, split by how firm each one is.

| Node | Backlog stated | As of | Contract, on or before | Framework, on or before | Announced after |
|---|---|---|---|---|---|
| tk-nucera | 1,500 MW | 2025-08-28 | **900 MW** | 1,020 MW | 300 MW |
| sunfire | 800 MW | 2024-12-19 | **347.5 MW** | 510 MW | 252.6 MW |

tk-nucera's 900 MW is Shell's Holland Hydrogen I (200 MW, January 2022) and
H2 Green Steel's Boden plant (700 MW, May 2023). The +720 MW the first read
reported came from summing 1,020 MW of frameworks — Neste 120, Cepsa 300, an
anonymous 600 MW FEED — into the total, and from a 300 MW contract with Moeve
signed in **March 2026**, seven months after the company spoke.

Sunfire's 347.5 MW is eleven contracts from Salzgitter's 0.72 MW in August 2020 to
Ren-Gas's 50 MW in November 2024, and it includes a 2.6 MW double count: Neste's
MultiPLHY appears as a delivery in 2022 and a start-up in 2025, because this file
records statements and not a reconciled position. The +310.1 MW came from 550 MW
of frameworks — one of them a single anonymous 500 MW agreement — plus 252.6 MW
announced after the backlog was stated.

**What is left is still a disagreement and it points the other way.** A supplier's
stated backlog is larger than the sum of the contracts it has named, which is
ordinary — not every order is announced — and is the opposite of oversubscription.
Both are recorded as disagreements on the node in §2.6, with both values, both
dates and both speakers, and neither figure is corrected.

**(b) The Northern Lights overshoot is not there either, and the dates are why.**
The store's capacity is now a dated list: phase and availability date on each
entry, from the one release that states both.

| Phase | Capacity | Available from | Contracted against it | Of which contract |
|---|---|---|---|---|
| phase 1 | 1,500,000 t/yr | 2024 | Yara 800,000 (from 2026) + Ørsted 430,000 (from 1 Jan 2026) | 1,230,000 |
| phase 2 | ≥ 5,000,000 t/yr | second half of 2028 | Stockholm Exergi 900,000 (from 2028) + Eramet 260,000 (MoU, from 2028) | 900,000 |

Phase 1 is **270,000 t/yr short of full**, not 890,000 over. The +890,000 came
from summing all four agreements against the first phase's nameplate when two of
them do not start until the second phase opens — and one of those two is an MoU,
not a contract. The release that announces the expansion says both halves in its
own words: "Ready to receive CO2 from 2024" for phase 1, and "the expansion is
expected to be completed and ready for operation in the second half of 2028" for
phase 2.

**(c) Porthos stands exactly as it was, by your ruling, and it is the cleanest
case in the file.** 2.5 Mt/yr, and the FID release states "Porthos has contracted
its full storage capacity". Its four edges — Air Liquide, Air Products, ExxonMobil,
Shell — carry **no quantity at all**, because the release gives only a combined
figure and splitting it would be inventing the split. A store sold out with an
unsplit customer list is a real shape and the file holds it honestly. It is
recorded as `not_comparable` for that reason and not for a unit clash: the units
would agree if the edges carried a number.

**(d) 24 of the 28 nodes cannot be compared at all, and for two different
reasons.** Each is recorded on the node in a `comparison` block with **both units
named**, rather than described in prose here. No derived figure is written
anywhere in this file and no delivery window is assumed.

| | Nodes | |
|---|---|---|
| The units clash | **8** | nel, itm-power, siemens-energy, mcphy, john-cockerill, slb-capturi, mhi, porthos |
| The node states no capacity at all | **16** | plug-power, aker-carbon-capture, shell-cansolv, linde, air-liquide, midrex, primetals, tenova, danieli, sms-group, wuxi-lead, manz, hitachi, aramis, greensand, endurance-nep |
| Comparable | **4** | tk-nucera, sunfire, northern-lights, ravenna-ccs |

The first read gave this as "eighteen of the twenty-seven nodes", which mixed the
two classes together and counted one node twice. They are different obstacles with
different remedies: a unit clash is a vocabulary problem somebody could rule on, and
a node with no stated capacity is a supplier that has never published a rate.

The clashes themselves, by kind:

- **MW against MW/yr.** Every electrolyser OEM except the two in (a). An edge is a
  plant of *n* megawatts; a node capacity is a factory that builds *n* megawatts
  *a year*. ITM Power's 2,753.5 MW of edges against 1,500 MW/yr is six years of
  orders against an annual rate. **The single most common obstacle in the file.**
- **A count of things against a rate.** SLB Capturi states "seven carbon capture
  plants" and then "eight"; MHI states "13 commercial facilities". Their edges are
  in tonnes of CO2 a year. Plants cannot be divided into tonnes.
- **The units match and the bases do not.** John Cockerill's one figure is "close
  to 200 megawatts" *sold in 2021* — a year's sales, filed as
  `delivery_commitment` because the vocabulary has no value for it — against plant
  sizes across six years. Same unit, different question.
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

**Two of them are now on the node rather than in this prose** — `disagreements` in
`nodes.json`, same shape — because they are the arithmetic of §2.5(a) and a number
kept only in a docket is a number nobody recomputes.

**D-0a — `backlog_mw`, on tk-nucera.**
- Speaker 1, thyssenkrupp nucera (2025-08-28): "engineering orders totaling 1.5
  gigawatts", in the Q3 report. **1,500 MW.**
- Speaker 2, this file's sum (2025-08-28): the contracts the company had announced
  by that date. **900 MW.**
- The company's own backlog is larger than the orders it has named. Neither figure
  is corrected.

**D-0b — `backlog_mw`, on sunfire.**
- Speaker 1, Sunfire (2024-12-19): "an order backlog exceeding 800 megawatts".
  **800 MW.**
- Speaker 2, this file's sum (2024-12-19): eleven contracts, one of which is a
  restatement of another. **347.5 MW.**
- Same shape, and a wider gap. Sunfire is unlisted and publishes no order book.

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

**D-3 — Edges and nodes carry fields the brief did not specify.** A null field
cannot say why it is null. `note` carries the sentence that makes a reading
honest; `match_basis` says what a link rests on; `inherited_by` records an
acquirer. Your batch rulings added `firmness` and `firmness_basis` (D-14),
`captured_at` (D-7), `site_as_stated`, `sector` and `outside_perimeter` (D-15) to
edges, and `phase` and `available_from` (D-17), `disagreements`, `comparison` and
`state` to nodes.
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

**D-7 — (Yours, 11 September 2026, and REVISED by you the same day.)** A Wayback
capture of a release published on the speaker's own domain is the speaker's
document; cite it and file the copy.

**THIS SUPERSEDES THE "CAPTURE TIMESTAMP AS SOURCE DATE" WORDING.** The capture
timestamp is not the source date. It is a field of its own, `captured_at`, on
edges and on capacity entries alike; `date` keeps the release's own dateline,
because that is what the sweep period is measured against and a 2020 release
captured in 2024 would otherwise leave the period. **A document with no dateline
takes `date = captured_at`, and `date_precision` says `capture_upper_bound`** —
the release exists at or before that date and this file will not say how much
before. The hydrogen-gap session aligns to the same shape.

`captured_at` is DERIVED, never typed: from the Internet Archive URL where there
is one, and from this sweep's own `fetched_at` in the cache index where the copy
on file is a live fetch. The two hand-written capture dates had already drifted
from the captures they named before the function existed.

**Three things fell out of the re-read, and two of them were errors.**

- **Both Danieli captures carry a dateline after all.** The first pass dated them
  by year — 2025-01-01 and 2022-01-01 — because danieli.com prints the category,
  then the date, then the headline in one run of text that reads as navigation.
  `e0239` is **3 February 2025** and `e0240` is **23 May 2022**, both to the day.
- **`e0240`'s body is readable after all.** The note said the capture had a
  headline and nothing else. It has an article: a ministerial visit to Cargnacco
  and an expansion announcement, which is why its firmness is `intent` and not
  `contract`. Nothing is claimed about what was sold.
- **One document in the whole file has no dateline at all** — Midrex's page on
  thyssenkrupp Steel's construction approval (`e0194`), which carries no printed
  date and no metadata date. It now takes this sweep's own fetch date as an upper
  bound, and the year the first pass inferred from the text is withdrawn.

*Touches:* `e0195`–`e0203` (McPhy), `e0239` and `e0240` (Danieli), `e0194`
(Midrex), and both `mcphy` capacity entries.

**D-14 — (Yours.) Every edge carries `firmness`, and `edge_kind` maps rather than
being recorded twice.** `contract` is a firm order or a signed supply agreement;
`framework` is an agreement with no named site or no quantity; `intent` is an MoU,
a study, a pre-FEED, a letter of intent or a selection the document itself calls
conditional. **Read from the source sentence and cited** — `firmness_basis` quotes
it, and a gate refuses any edge whose cited sentence is not in the cached body.

`framework_agreement` already encodes its own firmness, so the 98 edges of that
kind map to `framework` and carry the en-bloc ruling as their basis rather than a
second field saying the same thing. **No source was re-read for one of them**, as
you ruled. The other 142 were read: 127 contract, 14 intent, and one
`equipment_order` read down to `framework` because the release says its megawatts
sit on a capacity reservation (`e0055`).

*Touches:* every edge; `dep_sweep.FIRMNESS`; the citation gate in
`dep_records.check`.

**D-15 — (Yours.) A named site that matches no admitted row stays on the supplier
node, with a sector tag and `outside_perimeter: true`.** Ninety-four edges. They
are demand on the same supplier capacity as a matched edge and they belong in the
supplier's totals; they belong to no project. A company named **without** a site
is not this — it may well be a row nobody could identify — and those edges carry
`outside_perimeter: false`, which is a different fact and is kept as one.

Heidelberg Materials' three cement works leave this class for
`sources/cement_candidates.json` and the brief 8 census, each carrying the edge
that discovered it.

*Touches:* 94 edges; `sources/cement_candidates.json`, new.

**D-16 — (Yours.) Aker Carbon Capture takes the McPhy ruling: its own node, a
status event for the transfer, and its edges inherited by reference.** Fourteen
edges signed between April 2023 and April 2024 under the company's own name and
its own listing stay on `aker-carbon-capture`, each carrying
`inherited_by: {node_id: "slb-capturi", since: "2024-06-14", source_url: ...}`.
The transfer is a `status_history` event on both sides — the seller's and the
receiver's — with the date on each. Folding them onto one node would lose the
speaker and double any sum that read both.

**It is not defunct in the way the file said it was**, and the check you asked for
is in §1: slbcapturi.com resolves **nowhere** on slb.com, publishing no address
record while SLB's own nameservers hold the domain; akercarboncapture.com resolves
and serves nothing. Both are recorded as refusal classes rather than as one
sentence about domains being gone.

*Touches:* `e0140`–`e0153`; `dep_sweep.NODES`; `slb-capturi`'s `home`, which was
pointing at the domain with no address record and now points at capturi.slb.com.

**D-17 — (Yours.) A store's capacity is a dated list, and the dates decide the
arithmetic.** `phase` and `available_from` on every capacity entry that states
them. Northern Lights gets phase 1 and phase 2 as separate entries and each
contract is summed against the phase whose availability date it states; Ravenna
CCS gets the same treatment from the same kind of release; Porthos stands as it
was, by your ruling. The +890,000 t/yr overshoot does not survive it — see
§2.5(b).

*Touches:* both `northern-lights` capacity entries, both `ravenna-ccs` entries,
`dep_records.add_capacity`.

**D-18 — (Mine, and flagged rather than acted on.) One reading is not supported by
the page it cites.** `e0023` records an undisclosed Dutch H2Station order dated
10 August 2022. The page now cached at that URL is Nel's release of **17 December
2019** about a named customer, OrangeGas — a different customer and a date before
this sweep's period. Either Nel reused the slug or the reading took its date from
somewhere the document does not say it. The edge stands, with the whole of that in
its note, because deleting a reading is your call and not a re-run's.

*Touches:* `e0023`.

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
`operating` says nothing useful about a company. Ten events on four nodes:
`manz` (6), `slb-capturi` (2), `mcphy` (1), `aker-carbon-capture` (1) — the last
added by D-16, and it is the seller's side of the same transfer slb-capturi
records as the receiver's.

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

Rewritten 11 September 2026. Four of the five items the first version listed are
now done: D-7's date field is ruled and applied, the 98 frameworks are ruled, the
Aker node is split and the storage phases are dated.

1. **Verdict the edges, in the order in `sources/dependency_worklist.md`.** 25
   matched to a register row first, grouped by row; then the 94 at a site this
   register does not hold, grouped by site; then the other 121. Every verdict is
   still null. The worklist regenerates — `python3 sources/dep_worklist.py --write`
   — because a pasted list of outstanding work is wrong by the following morning.
2. **Finish Danieli.** Nine of 107 archive captures retrieved; the node is marked
   `incomplete: true` in `nodes.json` and **anybody summing it is summing a
   sample**. The Internet Archive throttles hard enough that this needs its own
   run, and this batch deliberately did not start one.
3. **Rule on `e0023`** — DECISION D-18. A reading whose cited page is a different
   release about a different customer, flagged rather than deleted.
4. **Review the nine `site only` matches.** All nine read correctly by hand, but
   each rests on a place name with no company agreement, and rung 6 will score
   them.
5. **The two Plug Power URLs the register cites that a reader cannot open.**
   `plugpower-kokkola` and `plugpower-kristinestad`. The text is in the Q4 feed.
6. **Retrieve the Shell Cansolv page by hand.** Queued in
   `sources/manual/MANIFEST.json` beside the two Shell hydrogen items, for the same
   refusal and one other: shell.com answers 200 with zero characters of text, and
   humberzero.co.uk answers 404 on every path.
7. **The three counts in the batch report did not reconcile with the file**, and
   the file is what this docket reports. The ruling asked for 94 edges matched to
   register rows: the matched set is **25** (11 `site+company`, 9 `site only`, 5
   explicit), and 94 is the count of the *other* class — the site-named edges
   outside the perimeter, which is where that ruling landed. The ruling asked for
   48 of those; there are **94**. And the 18 unit mismatches are **8**, with a
   further 16 nodes stating no capacity at all — the first read had mixed the two
   classes into one number. Nothing was bent to fit a count; the classes are ruled
   as ruled and the numbers are recomputed on every build.

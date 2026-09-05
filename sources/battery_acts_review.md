# Brief 6 §5 — the two acts, for review

**22 measure rows, both declared preliminary readings.** Nothing here has been through a
second independent pass; the coverage page says so in the same words PPWR's declaration
uses.

Every `source_text` below is **sliced from the consolidated act by a start and end anchor**,
never retyped — `extract_battery.py` and `extract_fleet.py` fail and write nothing if an
anchor is missing or ambiguous. So the quoted span is the act's own characters.

Read for: whether the duty summarises the span correctly, whether the addressee and class
are right, whether the conditional dates are fairly stated, and — on the fleet rows —
whether the demand edges are drawn in the right places.

**RATIFIED 5 SEPTEMBER 2026, WITH TWO CHANGES.** Everything else stands as written, including
all four demand edges and the two deliberate non-edges. The changes: `CF-01`'s `When` cell now
carries Art. 7(1)'s per-category split, and `TGT-2030` and `TGT-2035` each gain a sentence
saying that a Commission proposal to revise the target is under legislative review and that
the row reads the law in force. The proposal — COM(2025) 995 of 16 December 2025, CELEX
52025PC0995 — is on watch in `sources/queued.json` and is not read here: a proposal is not
the law.

---

## Batteries Regulation — Regulation (EU) 2023/1542

consolidated at 31 July 2025 (CELEX 02023R1542-20250731) · [source](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02023R1542-20250731) · **16 rows**

### `FM-01` — Art. 4(1)

**right** · direction `add` · class `business`

**Benefit:** A battery that complies with this Regulation may be placed on the market anywhere in the Union without a Member State restricting it on sustainability, safety, labelling or information grounds.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | a battery that complies with this Regulation |
| Frequency | continuous |
| Verification | market surveillance authority |
| **When** | Applies from 18 February 2024 (Art. 96(2)) |
| Names | batsol |
| Reaches | auto |
| Benefit axis | value V3 · frictions F1 |

> Member States shall not, for reasons relating to the sustainability, safety, labelling and
> information requirements for batteries covered by this Regulation, prohibit, restrict or impede
> the making available on the market or the putting into service of batteries that comply with
> this Regulation.

*Right basis (conferral):* “Member States shall not, for reasons relating to the sustainability, safety, labelling and information requirements for batteries covered by this Regulation, prohibit, restrict or impede the making av”

**Reading note.** The free-movement clause is read as a conferral on the operator rather than as a duty on the Member State, on the rule the benefit axis already applies: measure_type follows the OBJECT the provision acts on, and what this one acts on is the operator's ability to sell.

### `SUB-01` — Art. 6(1)

**prohibition** · direction `add` · class `business`

**Duty:** Do not place on the market a battery containing a substance restricted by Annex I otherwise than on the conditions that Annex sets.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | a battery containing mercury, cadmium or lead above the Annex I limits |
| Frequency | per battery model |
| Verification | market surveillance authority |
| **When** | Applies from 18 February 2024 (Art. 96(2)) |
| Names | batsol |
| Reaches | auto, chem |
| Drivers | D1 |

> In addition to the restrictions set out in Annex XVII to Regulation (EC) No 1907/2006 and in
> Article 4(2), point (a), of Directive 2000/53/EC, batteries shall not contain substances for
> which Annex I to this Regulation contains a restriction unless the conditions of that
> restriction are complied with.

### `CF-01` — Art. 7(1)

**obligation** · direction `add` · class `business`

**Duty:** Draw up a carbon footprint declaration for each battery model per manufacturing site, giving the site's geographic location and the battery's carbon footprint in kg CO2-equivalent per kWh delivered over its service life.

| | |
|---|---|
| Addressee | Manufacturers of electric vehicle, rechargeable industrial and LMT batteries |
| Trigger | each battery model, at each manufacturing site |
| Frequency | per model per site |
| Verification | notified body |
| **When** | Staggered by battery category (Art. 7(1), second subparagraph), each date being the later of the date given and the interval stated after the delegated and implementing acts enter into force: electric vehicle batteries 18 February 2025 or 12 months; rechargeable industrial batteries except those with exclusively external storage 18 February 2026 or 18 months; LMT batteries 18 August 2028 or 18 months; rechargeable industrial batteries with external storage 18 August 2030 or 18 months. Neither act has been adopted, so none of the dates is yet fixed |
| Names | batsol |
| Reaches | auto |
| Drivers | D1, D3 |

> For electric vehicle batteries, rechargeable industrial batteries with a capacity greater than 2
> kWh and LMT batteries a carbon footprint declaration shall be drawn up for each battery model
> per manufacturing plant, in accordance with the implementing act referred to in the fourth
> subparagraph and containing, at least, the following information: (a) administrative information
> about the manufacturer; (b) information about the battery model; (c) information about the
> geographic location of the battery manufacturing plant; (d) the carbon footprint of the battery,
> calculated as kg of carbon dioxide equivalent per one kWh of the total energy provided by the
> battery over its expected service life; (e) the carbon footprint of the battery differentiated
> according to life cycle stage as described in point 4 of Annex II; (f) the identification number
> of the EU declaration of conformity of the battery; (g) a web link giving access to a public
> version of the study supporting the carbon footprint values referred to in points (d) and (e).

**Reading note.** THE ONE PROVISION IN THIS ACT THAT IS PER-SITE, and the reason there is no money model for this sector. The declaration is drawn up per manufacturing site and its methodology sits in a delegated and an implementing act, neither adopted. Until they exist nothing about the declaration is computable for a named works, so the sector page carries no arithmetic here and no placeholder for it.

### `RC-01` — Art. 8(1)

**obligation** · direction `add` · class `business`

**Duty:** Accompany the battery with documentation stating the percentage of cobalt, lithium or nickel in active materials recovered from battery manufacturing waste or post-consumer waste, and the percentage of lead recovered from waste, per model per year per manufacturing site.

| | |
|---|---|
| Addressee | Manufacturers of industrial, electric vehicle and SLI batteries |
| Trigger | a battery containing cobalt, lead, lithium or nickel in active materials |
| Frequency | per model per year per site |
| Verification | notified body |
| **When** | 18 August 2028, or 24 months after the delegated act under Art. 8(1) enters into force, whichever is the latest. That act has not been adopted, so the date is not yet fixed |
| Names | batsol |
| Reaches | auto, waste |
| Drivers | D1, D2 |

> industrial batteries with a capacity greater than 2 kWh, except those with exclusively external
> storage, electric vehicle batteries and SLI batteries that contain cobalt, lead, lithium or
> nickel in active materials, shall be accompanied by documentation containing information about
> the percentage share of cobalt, lithium or nickel that is present in active materials and that
> has been recovered from battery manufacturing waste or post-consumer waste, and the percentage
> share of lead that is present in the battery and that has been recovered from waste, for each
> battery model per year and per manufacturing plant.

### `REM-01` — Art. 11(1)

**obligation** · direction `add` · class `business`

**Duty:** Ensure a portable battery in a product placed on the market is readily removable and replaceable by the end-user, using commercially available tools, at any time in the product's life.

| | |
|---|---|
| Addressee | Any person placing products incorporating portable batteries on the market |
| Trigger | a product incorporating a portable battery |
| Frequency | per product model |
| Verification | market surveillance authority |
| **When** | From 18 February 2027 (Art. 96(2)(a)) |
| Names | batsol |
| Reaches | auto |
| Drivers | D1 |

> Any natural or legal person that places on the market products incorporating portable batteries
> shall ensure that those batteries are readily removable and replaceable by the end-user at any
> time during the lifetime of the product.

### `LAB-01` — Art. 13(1)

**obligation** · direction `add` · class `business`

**Duty:** Bear a label carrying the general information on batteries set out in Part A of Annex VI.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | every battery placed on the market |
| Frequency | per battery |
| Verification | market surveillance authority |
| **When** | 18 August 2026, or 18 months after the implementing act under Art. 13(10) enters into force, whichever is the latest |
| Names | batsol |
| Reaches | auto |
| Drivers | D1 |

> batteries shall bear a label containing the general information on batteries set out in Part A
> of Annex VI.

### `MAN-01` — Art. 38(2)

**obligation** · direction `add` · class `business`

**Duty:** Draw up the Annex VIII technical documentation and carry out, or have carried out, the conformity assessment procedure before placing a battery on the market.

| | |
|---|---|
| Addressee | Manufacturers of batteries |
| Trigger | before a battery is placed on the market or put into service |
| Frequency | per battery model |
| Verification | notified body |
| **When** | Applies from 18 February 2024 (Art. 96(2)) |
| Names | batsol |
| Reaches | auto |
| Drivers | D1, D4 |

> Before placing a battery on the market or putting it into service, manufacturers shall draw up
> the technical documentation referred to in Annex VIII and carry out the relevant conformity
> assessment procedure, referred to in Article 17, or have it carried out.

### `SUP-01` — Art. 39

**obligation** · direction `add` · class `business`

**Duty:** Supply, free of charge, the information and documentation a battery manufacturer needs to comply with this Regulation when supplying it cells or modules.

| | |
|---|---|
| Addressee | Suppliers of battery cells and battery modules |
| Trigger | supplying cells or modules to a battery manufacturer |
| Frequency | per supply |
| Verification | none |
| **When** | From 18 August 2024 (Art. 96(2)(b)) |
| Names | batsol |
| Reaches | auto |
| Drivers | D4 |

> Suppliers of battery cells and battery modules shall provide the information and documentation
> necessary to comply with the requirements of this Regulation when supplying battery cells or
> modules to a manufacturer. That information and documentation shall be provided free of charge.

**Reading note.** THE ONE PROVISION ADDRESSED TO A CELL MAKER AS SUCH. Everything else in Chapter VI speaks to whoever places the finished battery on the market; this speaks to the works that made the cell, which is the population the projects dataset draws.

### `DD-01` — Art. 48(1)

**obligation** · direction `add` · class `business`

**Duty:** Set up and implement a battery due diligence policy covering the raw materials in the battery and the social and environmental risks in their supply chain.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | placing a battery on the market or putting it into service |
| Frequency | continuous |
| Verification | notified body |
| **When** | From 18 August 2027, as amended (Art. 48(1)) |
| Names | batsol |
| Reaches | auto, alu, chem |
| Drivers | D1, D4 |

> economic operators that place batteries on the market or put them into service shall fulfil the
> due diligence obligations laid down in paragraphs 2 and 3 of this Article, and in Articles 49,
> 50 and 52 and shall, to that end, set up and implement battery due diligence policies.

### `DD-02` — Art. 48(2)

**obligation** · direction `add` · class `business`

**Duty:** Have the battery due diligence policy verified by a notified body and periodically audited by it, and hold the audit report.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | holding a battery due diligence policy |
| Frequency | periodic |
| Verification | notified body |
| **When** | From 18 August 2027, as amended (Art. 48(1)) |
| Names | batsol |
| Reaches | auto |
| Drivers | D4 |

> Economic operators referred to in paragraph 1 of this Article shall have their battery due
> diligence policies verified by a notified body in accordance with Article 51 (‘third-party
> verification’) and periodically audited by that notified body to make sure that the battery due
> diligence policies are maintained and applied in accordance with Articles 49, 50 and 52. The
> notified body shall provide the audited economic operator with an audit report.

### `DD-03` — Art. 47

**obligation** · direction `rem` · class `business`

**Duty:** Comply with the battery due diligence obligations in Chapter VII.

| | |
|---|---|
| Addressee | Economic operators below the turnover threshold |
| Trigger | net turnover below EUR 40 million in the preceding financial year |
| Frequency | annual test |
| Verification | none |
| **When** | From 18 August 2027, as amended (Art. 48(1)) |
| Names | batsol |
| Reaches | — |

> This Chapter does not apply to economic operators that had a net turnover of less than EUR 40
> million

**Reading note.** Direction rem on an obligation row: the duty exists and this provision switches it off for a named class. That is the Simplification reading the valence rule takes, and is the same shape as NZIA Art. 6(5). It carries NO value_drivers and NO access_frictions, and the validator is right to insist: those fields assert a conferred faculty, and relieving a duty is not the same act as conferring one. The relief is expressed by direction rem on the duty, which is what the valence rule reads as Simplification.

### `BP-01` — Art. 77(1)

**obligation** · direction `add` · class `business`

**Duty:** Give each LMT, larger industrial and electric vehicle battery an electronic record carrying the Annex XIII information, accessible through the QR code on the battery.

| | |
|---|---|
| Addressee | Economic operators placing batteries on the market |
| Trigger | an LMT, industrial over 2 kWh, or electric vehicle battery |
| Frequency | per battery |
| Verification | market surveillance authority |
| **When** | From 18 February 2027 (Art. 77(1)) |
| Names | batsol |
| Reaches | auto, waste |
| Drivers | D1, D4 |

> each LMT battery, each industrial battery with a capacity greater than 2 kWh and each electric
> vehicle battery placed on the market or put into service shall have an electronic record
> (‘battery passport’).

### `GPP-01` — Art. 85(1)

**obligation** · direction `add` · class `state`

**Duty:** Take account of the life-cycle environmental impacts of batteries when procuring batteries or products containing them.

| | |
|---|---|
| Addressee | Contracting authorities and contracting entities |
| Trigger | a public procurement of batteries or products containing batteries |
| Frequency | per procurement |
| Verification | none |
| **When** | 12 months after the first delegated act under Art. 85(3) enters into force. That act has not been adopted, so the date is not yet fixed |
| Names | batsol |
| Reaches | auto |
| Drivers | D3 |

> contracting entities, as defined in Article 4(1) of Directive 2014/25/EU shall, when procuring
> batteries or products containing batteries in situations covered by those Directives, take
> account of the environmental impacts of those batteries over their life cycle with a view to
> ensuring that such impacts are kept to a minimum.

**Reading note.** The duty is on the buyer and the effect is on the seller, which is why this is an obligation on the state rather than a right for the operator: nothing here confers a faculty on anybody, it constrains how a contracting authority may buy.

### `EPR-01` — Art. 56(1)

**obligation** · direction `add` · class `business`

**Duty:** Carry extended producer responsibility for every battery first made available on a Member State's market, including the cost of collection, treatment and recycling.

| | |
|---|---|
| Addressee | Producers of batteries |
| Trigger | making a battery available on a Member State's market for the first time |
| Frequency | continuous |
| Verification | competent authority |
| **When** | From 18 August 2025 (Art. 96(2)(c)) |
| Names | batsol |
| Reaches | auto, waste |
| Drivers | D1, D2 |

> Producers shall have extended producer responsibility for batteries that they make available on
> the market for the first time within the territory of a Member State.

### `REC-01` — Art. 70(1)

**prohibition** · direction `add` · class `business`

**Duty:** Do not dispose of collected waste batteries or send them for energy recovery.

| | |
|---|---|
| Addressee | Operators of waste battery treatment facilities |
| Trigger | waste batteries that have been collected |
| Frequency | continuous |
| Verification | competent authority |
| **When** | From 18 August 2025 (Art. 96(2)(c)) |
| Names | batsol |
| Reaches | waste |
| Drivers | D1 |

> Collected waste batteries shall not be disposed of or be the subject of an energy recovery
> operation.

### `PEN-01` — Art. 93

**obligation** · direction `add` · class `state`

**Duty:** Lay down and notify rules on penalties for infringements of this Regulation, and take the measures necessary to ensure they are applied.

| | |
|---|---|
| Addressee | Member States |
| Trigger | entry into application of the Regulation |
| Frequency | one-off |
| Verification | none |
| **When** | By 18 August 2025 (Art. 93) |
| Names | batsol |
| Reaches | — |

> Member States shall lay down the rules on penalties applicable to infringements of this
> Regulation

---

## CO2 standards for cars and vans — Regulation (EU) 2019/631

consolidated at 9 July 2025 (CELEX 02019R0631-20250709) · [source](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02019R0631-20250709) · **6 rows** · **4 carrying `creates_demand_for`**

### `TGT-2030` — Art. 1(5)

**obligation** · direction `add` · class `business` · **→ creates demand for `batsol`**

**Duty:** Meet an EU fleet-wide target of a 55% reduction on the 2021 baseline for new passenger cars, and 50% for new light commercial vehicles.

| | |
|---|---|
| Addressee | Manufacturers of new passenger cars and light commercial vehicles |
| Trigger | the new vehicle fleet registered in the Union in a calendar year |
| Frequency | annual |
| Verification | the Commission |
| **When** | From 1 January 2030 (Art. 1(5)) |
| Names | auto |
| Reaches | batsol |
| Drivers | D1, D3 |

> From 1 January 2030, the following EU fleet-wide targets shall apply: (a) for the average
> emissions of the new passenger car fleet, an EU fleet-wide target equal to a ►M5 55 % ◄
> reduction of the target in 2021 determined in accordance with point 6.1.2 of Part A of Annex I;
> (b) for the average emissions of the new light commercial vehicles fleet, an EU fleetwide target
> equal to a ►M5 50 % ◄ reduction of the target in 2021 determined in accordance with point 6.1.2
> of Part B of Annex I.

**Reading note.** A 55% fleet reduction is not reachable on internal combustion alone at fleet scale, which is what makes this a demand instrument for cells and not only a duty on a carmaker. A Commission proposal to revise this target is under legislative review; this row reads the law in force.

### `TGT-2035` — Art. 1(5a)

**obligation** · direction `add` · class `business` · **→ creates demand for `batsol`**

**Duty:** Meet an EU fleet-wide target of a 100% reduction on the 2021 baseline for new passenger cars from 2035.

| | |
|---|---|
| Addressee | Manufacturers of new passenger cars |
| Trigger | the new passenger car fleet registered in the Union in a calendar year |
| Frequency | annual |
| Verification | the Commission |
| **When** | From 1 January 2035 (Art. 1(5a)) |
| Names | auto |
| Reaches | batsol |
| Drivers | D1, D3 |

> From 1 January 2035, the following EU fleet-wide targets shall apply: (a) for the average
> emissions of the new passenger car fleet, an EU fleet-wide target equal to a 100 % reduction of
> the target in 2021 determined in accordance with Part A, point 6.1.3, of Annex I;

**Reading note.** THE PROVISION THIS SECTOR IS BUILT ON. A 100% reduction on the tailpipe measure is a requirement that new cars emit no CO2 where they are driven, and the only volume technology that meets it is a battery electric vehicle. Every gigafactory row in the projects dataset exists because somebody believes this sentence. A Commission proposal to revise this target is under legislative review; this row reads the law in force.

### `TGT-01` — Art. 4(1)

**obligation** · direction `add` · class `business` · **→ creates demand for `batsol`**

**Duty:** Ensure the manufacturer's average specific CO2 emissions do not exceed its specific emissions target for the calendar year.

| | |
|---|---|
| Addressee | Manufacturers of new passenger cars and light commercial vehicles |
| Trigger | a manufacturer's new vehicles registered in a calendar year |
| Frequency | annual |
| Verification | the Commission |
| **When** | In force; applies to each calendar year |
| Names | auto |
| Reaches | batsol |
| Drivers | D1, D3 |

> The manufacturer shall ensure that its average specific emissions of CO2 do not exceed the
> following specific emissions targets: (a) for the calendar year 2020, the specific emissions
> target determined in accordance with points 1 and 2 of Part A of Annex I in the case of
> passenger cars, or points 1 and 2 of Part B of Annex I in the case of light commercial vehicles,
> or where a manufacturer is granted a derogation under Article 10, in accordance with that
> derogation; (b) for each calendar year from 2021 until 2024, the specific emissions targets
> determined in accordance with points 3 and 4 of Part A or B of Annex I, as appropriate, or,
> where a manufacturer is granted a derogation under Article 10, in accordance with that
> derogation and point 5 of Part A or B of Annex I; (c) for each calendar year, starting from
> 2025, the specific emissions targets determined in accordance with point 6.3 of Part A or B of
> Annex I, or, where a manufacturer is granted a derogation under Article 10, in accordance with
> that derogation.

**Reading note.** Where the fleet-wide number becomes an obligation on a named company. The fleet-wide targets in Art. 1 set the level; this is the row a manufacturer is actually held to.

### `PREM-01` — Art. 8(1)

**obligation** · direction `add` · class `business` · **→ creates demand for `batsol`**

**Duty:** Pay an excess emissions premium of EUR 95 per gram per kilometre of exceedance, multiplied by the number of newly registered vehicles.

| | |
|---|---|
| Addressee | Manufacturers of new passenger cars and light commercial vehicles |
| Trigger | average specific emissions above the manufacturer's target |
| Frequency | annual |
| Verification | the Commission |
| **When** | In force; applies to each calendar year |
| Names | auto |
| Reaches | batsol |
| Drivers | D1, D3 |

> In respect of each calendar year, the Commission shall impose an excess emissions premium on a
> manufacturer or pool manager, as appropriate, where a manufacturer's average specific emissions
> of CO2 exceed its specific emissions target.

**Reading note.** The price of missing the target, which is what makes the target bite. Carried as a demand edge because a priced obligation is the mechanism by which the fleet target reaches a procurement decision; the premium itself is money out of a carmaker, not money into a cell maker, and no money model is built from it here.

### `MON-01` — Art. 7(1)

**obligation** · direction `add` · class `state`

**Duty:** Record and report to the Commission, for each calendar year, the registration information for every new passenger car and light commercial vehicle.

| | |
|---|---|
| Addressee | Member States |
| Trigger | each new vehicle registered in the territory |
| Frequency | annual |
| Verification | the Commission |
| **When** | In force; applies to each calendar year |
| Names | auto |
| Reaches | — |
| Drivers | D4 |

> For each calendar year, each Member State shall record information for each new passenger car
> and each new light commercial vehicle registered in its territory

**Reading note.** A real duty and NOT a demand instrument. Carried without a creates_demand_for edge on purpose: monitoring makes no market for a cell, and an edge on every row in this act would say the whole regulation is a batteries instrument.

### `DER-01` — Art. 10(1)

**right** · direction `add` · class `business`

**Benefit:** A small-volume manufacturer may apply for a derogation from its specific emissions target.

| | |
|---|---|
| Addressee | Manufacturers below the small-volume thresholds |
| Trigger | fewer than 10 000 cars or 22 000 vans registered in the Union per year |
| Frequency | per application |
| Verification | the Commission |
| **When** | In force; applies to each calendar year |
| Names | auto |
| Reaches | — |
| Benefit axis | value V1 · frictions F4 |

> An application for a derogation from the specific emissions target calculated in accordance with
> Annex I may be made by a manufacturer of fewer than 10 000 new passenger cars or 22 000 new
> light commercial vehicles registered in the Union per calendar year

*Right basis (procedure):* “An application for a derogation from the specific emissions target calculated in accordance with Annex I may be made by a manufacturer of fewer than 10 000 new passenger cars or 22 000 new light comme”

---

## What to look hardest at

**The conditional dates.** Three battery rows — `CF-01`, `RC-01`, `GPP-01` — apply from a
calendar date *or* a stated interval after a delegated act enters into force, whichever is
later, and none of those acts exists. The `When` cell carries the conditional in full
rather than printing the calendar date, because the calendar date is the one thing that is
certainly not when the duty starts.

**And on `CF-01` the conditional is four conditionals.** Ratified 5 September 2026, on a
check of Art. 7(1)'s second subparagraph: the declaration applies from a different date for
each battery category — electric vehicle batteries at 18 February 2025 or 12 months after
the acts, rechargeable industrial batteries except those with exclusively external storage
at 18 February 2026 or 18 months, LMT batteries at 18 August 2028 or 18 months, and
rechargeable industrial batteries with external storage at 18 August 2030 or 18 months. The
row carried the electric-vehicle date alone, which said the duty reaches an LMT battery
three and a half years before it does. The `When` cell now carries the split.

**`CF-01` is why this sector has no money model.** It is the only provision in either act
that is per-manufacturing-site, and its methodology sits in an implementing act that is on
watch rather than in the register.

**The four demand edges, and the two rows that deliberately lack them.** `MON-01`
(monitoring) and `DER-01` (small-volume derogation) are real duties on a carmaker and
neither makes a market for a cell. An edge on every row would say the whole regulation is a
batteries instrument.


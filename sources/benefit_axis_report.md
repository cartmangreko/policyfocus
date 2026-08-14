# Benefit-axis reclassification report

Produced by `sources/build_benefit_axis.py`. The rule applied is documented in `sources/benefit_axis.py`.

## Counts

| file | rows | before | after |
|---|---|---|---|
| ets | 49 | Opportunity 20, Requirement 19, Simplification 2, Support cut 8 | Opportunity 17, Requirement 19, Simplification 13 |
| iaa | 62 | Opportunity 17, Requirement 44, Simplification 1 | Opportunity 14, Requirement 44, Simplification 4 |
| omnibus | 35 | Requirement 14, Simplification 21 | Requirement 14, Simplification 21 |

## Reclassified (no verbatim quantum basis available)

### FRE-04 (ets) — Support cut → Simplification

- **affected_delta:** Installations already implementing an Industrial Decarbonisation Bank, Investment Booster or Innovation Fund-supported project are excused from drawing up the Invest in EU decarbonisation plan and automatically receive 80% of their free allocation without additional verification.
- **reason:** No quantum basis. The object is the decarbonisation-plan duty and its verification step, not the allocation; the allocation itself is unchanged (indeed protected). Object rule -> obligation side, direction rem.

### FRE-05 (ets) — Support cut → Simplification

- **affected_delta:** The most efficient 10% of installations in a sector, zero-emission/low-carbon installations, and installations that voluntarily remain in the ETS after falling below the combustion threshold are excused entirely from the Invest in EU decarbonisation plan and the 80/20 tranching conditionality.
- **reason:** No quantum basis. A condition attached to the support is removed, not the support. Object rule -> obligation side, direction rem.

### FRE-06 (ets) — Opportunity → Simplification

- **affected_delta:** Operators may pool multiple installations under a joint decarbonisation investment agreement to satisfy the mandatory decarbonisation-investment volume jointly rather than installation-by-installation.
- **reason:** No quantum basis. Pooling changes how an investment REQUIREMENT may be discharged; the free allocation it conditions is untouched. Object rule -> obligation side, direction rem.

### SHIP-03 (ets) — Support cut → Simplification

- **affected_delta:** Large containerships (10,000+ TEU) on long inbound voyages (over 300 nautical miles) from outside the EU can surrender fewer allowances than their actual verified emissions until 2035, reduced pro-rata by the share of containers transhipped onward.
- **reason:** No quantum basis. The object is the surrender obligation and how much of it applies, not any support. Object rule -> obligation side, direction rem.

### SHIP-04 (ets) — Opportunity → Simplification

- **affected_delta:** The temporary exclusion of container transhipment at listed neighbouring non-EU ports from the EU ETS surrender scope is extended eight years, to 31 December 2038.
- **reason:** No quantum basis. Extending an exclusion from ETS surrender scope postpones a duty; it creates no support. Object rule -> obligation side, direction rem.

### AVI-04 (ets) — Support cut → Simplification

- **affected_delta:** Aircraft operators flying to/from listed least-developed and small island developing states are excused from surrendering any allowances for those flights' emissions through 2035.
- **reason:** No quantum basis. An exemption from the surrender duty is a duty removal, not a support cut. Object rule -> obligation side, direction rem.

### CCS-01 (ets) — Support cut → Simplification

- **affected_delta:** Operators who capture and permanently store their CO2 (in an EU-permitted storage facility, or from 2031 reciprocally in a linked third country's permitted facility) are excused entirely from surrendering allowances for those captured emissions.
- **reason:** No quantum basis. The provision extinguishes a surrender obligation; it moves no support. Object rule -> obligation side, direction rem.

### CCS-02 (ets) — Support cut → Simplification

- **affected_delta:** CO2 that is captured and permanently chemically bound into a product (carbon capture and utilisation) is excused from the surrender obligation.
- **reason:** No quantum basis. The provision extinguishes a surrender obligation. Object rule -> obligation side, direction rem.

### CCS-03 (ets) — Opportunity → Simplification

- **affected_delta:** Operators, aircraft operators and shipping companies will be able to offset their fossil CO2 emissions using their own certified domestic permanent carbon removal units (from storage of biogenic emissions), reducing the number of allowances they must surrender.
- **reason:** No quantum basis. A new way to discharge the surrender obligation eases the duty; no support amount, rate, eligibility or existence changes. Object rule -> obligation side, direction rem.

### WST-02 (ets) — Support cut → Simplification

- **affected_delta:** Member States may fully exempt waste incineration/co-incineration installations located in outermost regions from any surrender obligation until the end of 2035.
- **reason:** No quantum basis. A Member State option to exempt installations from the surrender duty is a duty removal. Object rule -> obligation side, direction rem.

### WST-03 (ets) — Support cut → Simplification

- **affected_delta:** Waste incineration/co-incineration installations can be fully exempted from surrendering ETS allowances (up to 2035) if their Member State meets at least two of three conditions: an equivalent national carbon tax, being on track for EU recycling targets, or being on track for landfill-diversion targets.
- **reason:** No quantum basis. A conditional exemption from the surrender duty is a duty removal. Object rule -> obligation side, direction rem.

### PRM-04 (iaa) — Opportunity → Simplification

- **affected_delta:** Automatic classification as a 'strategic project' contributing to resilience and decarbonisation or resource efficiency, granting access to the priority/streamlined treatment of the future Environmental Assessment Regulation.
- **reason:** No quantum basis. Strategic-project status buys priority/streamlined PROCEDURE, not money. Object rule -> obligation side, direction rem.

### PRM-06 (iaa) — Opportunity → Simplification

- **affected_delta:** Automatic 'strategic project' status for all net-zero technology manufacturing projects, granting streamlined treatment under the future Environmental Assessment Regulation.
- **reason:** No quantum basis. Strategic-project status buys priority/streamlined PROCEDURE, not money. Object rule -> obligation side, direction rem.

### AA-04b (iaa) — Opportunity → Simplification

- **affected_delta:** Project promoters within an acceleration area only need to obtain additional permits that fall outside the scope of the aggregated baseline permit, cutting the permitting burden.
- **reason:** No quantum basis. The object is the permitting procedure. Object rule -> obligation side, direction rem.

## Kept on the benefit axis, flagged for human confirmation

- **LM-06c** (iaa, Opportunity, basis kind `eligibility`) — Basis is quoted from Annex II Part II rather than the row's own source_text span, which stops before the qualifying share.
- **SC-01** (iaa, Opportunity, basis kind `eligibility`) — 'made in the EU' status confers eligibility for a super-credit under a separate regulation; the quantum lives in that instrument, not here.
- **SC-02** (iaa, Opportunity, basis kind `eligibility`) — Same as SC-01: eligibility definition feeding the CO2-standards compensation regime; no quantum stated in this text.
- **IAAB-CHEM-01** (iaa, Opportunity, basis kind `existence`) — Support is prospective: an empowerment to adopt demand-side measures, not yet an instrument. Basis kind 'existence' is the most it can carry today.

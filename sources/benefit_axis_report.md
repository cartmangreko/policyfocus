# Benefit-axis reclassification report

Produced by `sources/build_benefit_axis.py`. The rule applied is documented in `sources/benefit_axis.py`.

## Counts

| file | rows | before | after |
|---|---|---|---|
| ets | 51 | Opportunity 18, Requirement 19, Simplification 5, Support cut 9 | Entitlement 2, Opportunity 17, Requirement 19, Simplification 12, Support cut 1 |
| iaa | 65 | Entitlement 1, Opportunity 16, Requirement 44, Simplification 4 | Entitlement 4, Opportunity 16, Requirement 44, Simplification 1 |
| omnibus | 35 | Requirement 14, Simplification 21 | Requirement 14, Simplification 21 |

## Reclassified (no verbatim quantum basis available)

### FRE-04 (ets) — Support cut → Simplification

- **affected_delta:** Draw up an Invest in EU decarbonisation plan and pass the additional verification gating the final 20% tranche of free allocation.
- **reason:** No quantum basis. The object is the decarbonisation-plan duty and its verification step, not the allocation; the allocation itself is unchanged (indeed protected). Object rule -> obligation side, direction rem.

### FRE-05 (ets) — Support cut → Simplification

- **affected_delta:** Draw up an Invest in EU decarbonisation plan and satisfy the 80/20 tranching conditionality attached to free allocation.
- **reason:** No quantum basis. A condition attached to the support is removed, not the support. Object rule -> obligation side, direction rem.

### FRE-06 (ets) — Simplification → Entitlement

- **affected_delta:** Operators may pool multiple installations under a joint decarbonisation investment agreement to satisfy the mandatory decarbonisation-investment volume jointly rather than installation-by-installation.
- **reason:** Operators 'may request to form a pool' — a faculty for discharging the investment requirement jointly that no operator previously held. The requirement itself is unchanged, which is why this is not a Simplification: nothing shrank, something was granted.

### SHIP-03 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances equal to full verified emissions from long inbound voyages, including the transhipped share.
- **reason:** No quantum basis. The object is the surrender obligation and how much of it applies, not any support. Object rule -> obligation side, direction rem.

### SHIP-04 (ets) — Opportunity → Simplification

- **affected_delta:** Surrender allowances for containers transhipped via listed neighbouring non-EU ports, once the temporary exclusion lapses.
- **reason:** No quantum basis. Extending an exclusion from ETS surrender scope postpones a duty; it creates no support. Object rule -> obligation side, direction rem.

### AVI-04 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances under Art. 12(3) for emissions from flights to or from listed LDC/SIDS states.
- **reason:** No quantum basis. An exemption from the surrender duty is a duty removal, not a support cut. Object rule -> obligation side, direction rem.

### CCS-01 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances for emissions that are captured and transported for permanent storage in a permitted facility.
- **reason:** No quantum basis. The provision extinguishes a surrender obligation; it moves no support. Object rule -> obligation side, direction rem.

### CCS-02 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances for CO2 captured and utilised so as to become permanently chemically bound in a product.
- **reason:** No quantum basis. The provision extinguishes a surrender obligation. Object rule -> obligation side, direction rem.

### CCS-03 (ets) — Simplification → Entitlement

- **affected_delta:** Operators, aircraft operators and shipping companies will be able to offset their fossil CO2 emissions using their own certified domestic permanent carbon removal units (from storage of biogenic emissions), reducing the number of allowances they must surrender.
- **reason:** The implementing acts 'shall provide for the possibility for operators ... to compensate' — an entitlement to discharge surrender with own certified removal units. A new instrument in the operator's hands, not a narrower duty.

### WST-02 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances for emissions from waste incineration and co-incineration installations in outermost regions.
- **reason:** No quantum basis. A Member State option to exempt installations from the surrender duty is a duty removal. Object rule -> obligation side, direction rem.

### WST-03 (ets) — Support cut → Simplification

- **affected_delta:** Surrender allowances for the emissions of a given reference year from waste incineration and co-incineration installations.
- **reason:** No quantum basis. A conditional exemption from the surrender duty is a duty removal. Object rule -> obligation side, direction rem.

### PRM-04 (iaa) — Simplification → Entitlement

- **affected_delta:** Automatic classification as a 'strategic project' contributing to resilience and decarbonisation or resource efficiency, granting access to the priority/streamlined treatment of the future Environmental Assessment Regulation.
- **reason:** Confers strategic-project STATUS on a whole class of project, which unlocks the priority permitting track. The conferral is the status; kind 'scope' records which projects it reaches.

### PRM-06 (iaa) — Simplification → Entitlement

- **affected_delta:** Automatic 'strategic project' status for all net-zero technology manufacturing projects, granting streamlined treatment under the future Environmental Assessment Regulation.
- **reason:** Same conferral as PRM-04, for net-zero technology manufacturing projects.

### AA-04b (iaa) — Simplification → Entitlement

- **affected_delta:** Project promoters within an acceleration area only need to obtain additional permits that fall outside the scope of the aggregated baseline permit, cutting the permitting burden.
- **reason:** Projects inside an acceleration area may rely on the area's aggregated baseline permit — the streamlined-permitting privilege the acceleration-area regime exists to confer. Phrased as 'shall be required to obtain only', so it reads as a duty narrowing; the object is the conferred baseline permit, and the narrowing is its consequence. Flagged in the report as the one genuinely two-faced row of the five.

## Kept on the benefit axis, flagged for human confirmation

- **LM-06c** (iaa, Opportunity, basis kind `eligibility`) — Basis is quoted from Annex II Part II rather than the row's own source_text span, which stops before the qualifying share.
- **SC-01** (iaa, Opportunity, basis kind `eligibility`) — 'made in the EU' status confers eligibility for a super-credit under a separate regulation; the quantum lives in that instrument, not here.
- **SC-02** (iaa, Opportunity, basis kind `eligibility`) — Same as SC-01: eligibility definition feeding the CO2-standards compensation regime; no quantum stated in this text.
- **IAAB-CHEM-01** (iaa, Opportunity, basis kind `existence`) — Support is prospective: an empowerment to adopt demand-side measures, not yet an instrument. Basis kind 'existence' is the most it can carry today.

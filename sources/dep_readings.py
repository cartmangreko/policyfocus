"""Every edge and every stated capacity the sweep read, one call per reading.

Written by hand from the digests (dep_digest.py) against the cached pages
(dep_fetch.py). The url on each line is the page the sentence is in; the date is
the page's own dateline. Nothing here is inferred from anything else here.

CONVENTIONS, all of them consequences of the brief:

  * QUANTITY IS AS STATED, in the unit stated. No conversion, ever -- 20 MW stays
    20 MW, "several H2Station modules" has no value and gets quantity None, and a
    contract value in euros is not a quantity because euros are not capacity.
  * A REVISION OF ONE ORDER IS A SEPARATE EDGE. Nel's Everfuel contract was
    announced, then board-approved, then delivered; HH2E's was an LoI, then firm.
    Each announcement is its own edge with its own date, because the brief asks
    for the documents and not for a reconciled current state.
  * A CANCELLATION IS AN EDGE. `edge_kind` still says what was cancelled and the
    note says it was; an order that vanishes from the file when it is cancelled is
    a file that cannot answer "how much of this backlog held".
  * EXCLUDED, and listed in the docket instead of here: agreements in which the
    node is the BUYER (Nel buying compressors from Howden), and integration, EPC
    and reseller partnerships where nobody takes delivery of a plant (Wood, Aibel,
    Kvaerner, Hydrasun, Saipem, SAMSUNG E&A's licence of Nel technology). They are
    real relationships and they are not demand on the node's capacity.
"""
from __future__ import annotations

from dep_records import add_capacity as C
from dep_records import add_edge as E

N = "https://nelhydrogen.com/press-release/"

# =============================================================================
# electrolyser_oem
# =============================================================================

# --- Nel ASA ------------------------------------------------------------------
# Newsroom swept in full: 573 releases listed at nelhydrogen.com/press-releases/
# over 58 listing pages, 166 fetched on the title filter, 88 of those in period.
C("nel", 500, "MW/yr", "nameplate", "supplier", "supplier_press",
  N + "nel-asa-official-opening-of-the-heroya-facility/", "2022-04-20",
  note="Herøya alkaline stack line at opening. Same release states it can rise to "
       "2 GW with further investment and that Nel targets 10 GW by 2025 'if required "
       "by the market' — an ambition, not a nameplate, and not recorded as one.")
C("nel", 1000, "MW/yr", "nameplate", "supplier", "supplier_press",
  N + "nel-asa-will-build-a-second-production-line-at-heroya/", "2022-08-11",
  note="Second fully automated Herøya line, 'doubling its capacity ... to ~1 GW'.")
C("nel", 500, "MW/yr", "nameplate", "supplier", "supplier_press",
  N + "nel-asa-expanding-production-capacity-in-wallingford/", "2023-02-28",
  note="Wallingford, Connecticut PEM line, 'towards 500 MW in 2025'. US capacity; "
       "recorded because the node is the supplier, not the site.")
C("nel", 1000, "MW/yr", "nameplate", "supplier", "supplier_press",
  N + "nel-asa-strengthens-its-industry-leadership-as-the-final-investment-decision-"
      "has-been-taken-to-industrialize-the-next-generation-pressurized-alkaline-platform/",
  "2025-12-12",
  note="FID on up to 1 GW of pressurized-alkaline capacity at Herøya. The same "
       "release says the two 500 MW atmospheric alkaline lines are 'currently idling' "
       "— so the 2022 nameplate above is stated capacity that is not stated output.")

E("nel", "Lhyfe Labs SAS", "framework_agreement", "supplier", "supplier_press",
  N + "nel-asa-enters-into-framework-agreement-for-delivery-of-electrolysers-in-france/",
  "2020-04-21", quantity=(60, "MW"), country="FR", sector="hydrogen",
  note="'up to 60 megawatt'. No site named in the release.")
E("nel", "a customer in Europe", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-a-2-5-mw-pem-electrolyser-in-europe/",
  "2020-06-10", quantity=(2.5, "MW"),
  note="Customer undisclosed; 'a customer in Europe' is the whole of what is stated. "
       "No unmatched row — an undisclosed customer is not a customer nobody matched.")
E("nel", "Everfuel Europe A/S", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-h2station-from-everfuel/",
  "2020-10-05", quantity=(1, "H2Station fuelling station"), country="DK",
  sector="hydrogen refuelling")
E("nel", "ZE PAK SA", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-first-h2station-order-in-poland/", "2020-10-14",
  quantity=None, country="PL", sector="power / hydrogen refuelling",
  note="'H2Station™ hydrogen fueling stations' — plural, no count stated.")
E("nel", "Statkraft AS", "framework_agreement", "supplier", "supplier_press",
  N + "nel-signs-loi-with-statkraft-for-a-green-hydrogen-project-with-up-to-50mw-of-"
      "electrolyser-capacity/", "2020-10-30", quantity=(50, "MW"), country="NO",
  sector="hydrogen", note="Letter of intent for 40–50 MW; the upper figure is recorded "
                          "and the range is the statement.")
E("nel", "Iberdrola", "framework_agreement", "supplier", "supplier_press",
  N + "nel-asa-selected-by-iberdrola-as-preferred-supplier-for-a-20-mw-green-fertilizer-"
      "project-in-spain/", "2020-11-03", quantity=(20, "MW"), country="ES",
  sector="fertiliser", note="Preferred supplier; the release says contract award is "
                            "subject to conditions. Superseded by the 2021-01-14 award.")
E("nel", "Iberdrola", "framework_agreement", "supplier", "supplier_press",
  N + "nel-asa-enters-into-mou-with-iberdrola-to-develop-large-scale-green-hydrogen-"
      "project-and-the-hydrogen-technology-value-chain-in-spain/", "2020-11-18",
  quantity=None, country="ES", sector="fertiliser")
E("nel", "Everfuel A/S", "equipment_order", "supplier", "supplier_press",
  N + "awarded-everfuel-contract-for-fredericia-hydrogen-project/", "2020-12-30",
  quantity=(20, "MW"), country="DK", sector="hydrogen",
  note="HySynergy, adjacent to the Fredericia refinery.")
E("nel", "Everfuel A/S", "equipment_order", "supplier", "supplier_press",
  N + "approval-of-everfuel-contract-nel-asa/", "2021-01-10", quantity=(20, "MW"),
  country="DK", sector="hydrogen",
  note="Board approval of the 2020-12-30 contract. Same order, second document.")
E("nel", "Iberdrola", "equipment_order", "supplier", "supplier_press",
  N + "awarded-iberdrola-contract-for-20-mw-green-fertilizer-project-in-spain/",
  "2021-01-14", quantity=(20, "MW"), country="ES", sector="fertiliser",
  note="EUR 13.5 million contract; Puertollano.")
E("nel", "SGN", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-5mw-alkaline-electrolyser/", "2021-09-24",
  quantity=(5, "MW"), country="GB", sector="gas network")
E("nel", "Communauté de communes Touraine Vallée de l'Indre (CCTVI)", "equipment_order",
  "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-the-community-of-cities-touraine-vallee-de-"
      "lindre-cctvi-for-a-hydrogen-fueling-station-h2station-to-be-located-in-the-regi/",
  "2021-09-28", quantity=(1, "H2Station fuelling station"), country="FR",
  sector="local authority / mobility")
E("nel", "MaserFrakt AB", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-maserfrakt-ab-for-h2station-hydrogen-fueling-"
      "station-in-sweden/", "2021-09-30", quantity=(1, "H2Station fuelling station"),
  country="SE", sector="haulage")
E("nel", "Ovako", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-20mw-alkaline-electrolyser-from-ovako/",
  "2021-11-25", quantity=(20, "MW"), country="SE", sector="steel",
  note="Hofors, Sweden — hydrogen to replace propane in steel REHEATING furnaces, not "
       "iron reduction. A steel customer that the register's steel perimeter does not "
       "hold, which is the finding, not a miss.")
E("nel", "a new, European customer", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-alkaline-electrolyser-system/", "2021-12-24",
  quantity=None, note="Customer undisclosed.")
E("nel", "Solar Foods", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-nel-to-supply-an-alkaline-electrolyser-system-for-solar-foods/",
  "2022-03-16", quantity=None, country="FI", sector="food / protein",
  note="Factory 01. No capacity stated in the release.")
E("nel", "HysetCo", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-several-h2station-modules-in-france/",
  "2022-03-21", quantity=None, country="FR", sector="hydrogen refuelling",
  note="'several H2Station modules', Paris. No count stated.")
E("nel", "an undisclosed European customer", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-in-europe/",
  "2022-03-28", quantity=None,
  note="Firm order following the 23 March 2022 commercial update.")
E("nel", "Biproraf (Grupa Technologiczna ASE)", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-from-biproraf-for-hydrogen-fueling-equipment-in-"
      "poland/", "2022-04-01", quantity=(1, "H2Station fuelling station"), country="PL",
  sector="engineering / hydrogen refuelling")
E("nel", "a European customer", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-two-purchase-orders-for-h2station-fueling-systems-from-a-european-"
      "client/", "2022-04-27", quantity=(2, "H2Station fuelling system"),
  note="Two firm purchase orders; customer undisclosed.")
E("nel", "Glencore Nikkelverk", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-system-from-glencore-"
      "nikkelverk/", "2022-06-02", quantity=None, country="NO",
  sector="non-ferrous metals", note="Kristiansand. No capacity stated.")
E("nel", "Skovgaard Energy ApS", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-system-from-skovgaard-"
      "energy/", "2022-07-08", quantity=None, country="DK", sector="hydrogen / ammonia",
  note="Lemvig, western Jutland. The register holds a Skovgaard row in the hydrogen "
       "class, which is out of the owner-side perimeter on this branch until #54 "
       "merges — DECISION D-5.")
E("nel", "an undisclosed European client", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-multiple-h2station-units-in-the-netherlands/",
  "2022-08-10", quantity=None,
  note="'several H2Station™ units' for light- and heavy-duty vehicles; the title places "
       "them in the Netherlands.")
E("nel", "a high quality North European energy company", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-40-mw-electrolyser-order-from-undisclosed-north-european-client/",
  "2022-11-14", quantity=(40, "MW"),
  note="NOK 120 million. Nel's 2025-04-30 cancellation release names this contract as "
       "Statkraft's — see the disagreement entry in the docket.")
E("nel", "HH2E", "framework_agreement", "supplier", "supplier_press",
  N + "nel-asa-nel-signs-agreement-with-hh2e-for-potential-120-mw-capacity-in-germany/",
  "2023-01-06", quantity=(120, "MW"), country="DE", sector="hydrogen",
  note="FEED study and Letter of Intent for two 60 MW plants.")
E("nel", "HyCC", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-40-mw-electrolyser-equipment-from-hycc/",
  "2023-02-06", quantity=(40, "MW"), country="NL", sector="hydrogen",
  note="H2eron, Delfzijl. About EUR 12 million.")
E("nel", "HH2E", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-firm-purchase-order-from-hh2e-for-120-mw-of-electrolyser-equipment/",
  "2023-03-14", quantity=(120, "MW"), country="DE", sector="hydrogen",
  note="Firm contract following the January LoI.")
E("nel", "Hyd'Occ", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-20-mw-electrolyser-equipment-from-hydocc/",
  "2023-07-14", quantity=(20, "MW"), country="FR", sector="hydrogen",
  note="Port-la-Nouvelle. About EUR 9 million.")
E("nel", "Bondalti", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-40-mw-electrolyser-equipment-from-bondalti/",
  "2023-07-17", quantity=(40, "MW"), country="PT", sector="chemicals",
  note="H2 Enable phase one, Estarreja. About EUR 11 million.")
E("nel", "HyCC", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-hycc-has-cancelled-the-40-mw-purchase-order-due-to-market-conditions/",
  "2023-12-12", quantity=(40, "MW"), country="NL", sector="hydrogen",
  note="CANCELLATION of the 2023-02-06 order. Recorded as an edge so the backlog it "
       "left can be seen leaving.")
E("nel", "an undisclosed customer (a European project)", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-for-electrolyser-equipment/", "2024-07-01",
  quantity=None,
  note="'a follow-on equipment order of more than EUR 7 million for a European project'. "
       "Neither customer nor capacity stated.")
E("nel", "Alperia Greenpower SRL", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-alperia-greenpower-srl-for-hydrogen-fueling-"
      "equipment-in-italy/", "2024-05-30", quantity=(1, "hydrogen fuelling site"),
  country="IT", sector="utility / hydrogen refuelling",
  note="Placed with a Cavendish Hydrogen ASA subsidiary, itself then a Nel subsidiary.")
E("nel", "Aberdeen Hydrogen Hub", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-one-mc500-containerized-pem-electrolyser/",
  "2025-03-20", quantity=(2.5, "MW"), country="GB", sector="hydrogen",
  note="One MC500 for the Aberdeen Hydrogen Hub, north-east Scotland. Announced by "
       "Nel Hydrogen US, which is where the order was booked and not where it lands.")
E("nel", "Statkraft", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-statkraft-has-cancelled-the-40-mw-alkaline-electrolyser-contract/",
  "2025-04-30", quantity=(40, "MW"), country="NO", sector="hydrogen",
  note="CANCELLATION, and the document that names the 2022-11-14 'undisclosed North "
       "European client' as Statkraft.")
E("nel", "H2 Energy (for Verein für Abfallentsorgung, Buchs)", "equipment_order",
  "supplier", "supplier_press",
  N + "nel-asa-receives-its-third-purchase-order-for-a-containerized-pem-solution-from-"
      "h2-energy/", "2025-10-07", quantity=(2.5, "MW"), country="CH",
  sector="waste management / hydrogen refuelling",
  note="Ordered by H2 Energy, delivered to VfA Buchs, Switzerland. Two parties, one "
       "order; the customer as stated is the one that placed it.")
E("nel", "Kaupanes Hydrogen AS and HyFuel AS", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-pem-purchase-order-from-the-hyfuel-and-kaupanes-hydrogen-projects-"
      "valued-at-more-than-usd-50-million/", "2025-11-05", quantity=None, country="NO",
  sector="hydrogen", note="More than USD 50 million; developed by Hydrogen Solutions AS "
                          "(HYDS). No MW figure in the release.")

# --- ITM Power plc ------------------------------------------------------------
# Newsroom swept from itm-power.com/sitemap.xml: 133 news items, all fetched (the
# sitemap carries no titles, so the title filter could not be applied and was not
# needed). Coverage is thin for parts of 2021 and 2022 — the sitemap lists 12 and
# 11 items for those years against 20 for 2020 — so the RNS record on the
# investors/news page may hold items this sweep did not see. Written down rather
# than filled in from press.
I = "https://itm-power.com/news/"

C("itm-power", 1000, "MW/yr", "nameplate", "supplier", "supplier_press",
  I + "manufacturing-commences-at-the-itm-power-gigafactory", "2021-01-04",
  note="Bessemer Park, Sheffield, at practical completion: '1GW (1,000MW) per annum'.")
C("itm-power", 1500, "MW/yr", "nameplate", "supplier", "supplier_press",
  I + "appointment-of-chief-executive-officer", "2022-11-25",
  note="'capacity planned to reach 1.5 GW (1,500 MW) per annum'. PLANNED, not built — "
       "the same sentence adds an ambition of 5 GW, which is not recorded at all.")

E("itm-power", "an undisclosed UK customer", "equipment_order", "supplier",
  "supplier_press", I + "funding-award-to-supply-an-8mw-electrolyser", "2020-04-30",
  quantity=(8, "MW"), note="£10m including project costs; 'further details will be "
                           "announced in due course'.")
E("itm-power", "BOC", "equipment_order", "supplier", "supplier_press",
  I + "first-project-to-deliver-a-10mw-electrolyser-to-glasgow-facility", "2020-09-16",
  quantity=(10, "MW"), country="GB", sector="industrial gases",
  note="Operated by BOC with power from ScottishPower Renewables; Glasgow.")
E("itm-power", "Linde", "equipment_order", "supplier", "supplier_press",
  I + "sale-to-linde-of-world-s-largest-pem-electrolyser", "2021-01-13",
  quantity=(24, "MW"), country="DE", sector="industrial gases",
  note="For the Leuna Chemical Complex, Germany. Linde is itself a node on this "
       "perimeter (capture_technology) and here is the buyer — the same firm appears "
       "on both sides of the sweep, which is the finding, not a clash.")
E("itm-power", "an undisclosed customer", "equipment_order", "supplier",
  "supplier_press", I + "12mw-electrolyser-sale", "2021-11-15", quantity=(12, "MW"),
  note="'The customer and location remain confidential due to commercial sensitivities.'")
E("itm-power", "Linde Engineering (for Yara Norge AS)", "equipment_order", "supplier",
  "supplier_press", I + "24mw-sale-to-yara", "2022-01-28", quantity=(24, "MW"),
  country="NO", sector="fertiliser",
  note="Sold to Linde Engineering, installed at Yara's Herøya site outside Porsgrunn. "
       "Two parties again; the buyer is Linde Engineering and the site is Yara's.")
E("itm-power", "Linde Engineering (for RWE, Lingen)", "equipment_order", "supplier",
  "supplier_press", I + "two-100-mw-electrolyser-contracts-signed", "2023-01-31",
  quantity=(200, "MW"), country="DE", sector="power / hydrogen",
  note="TWO contracts of 100 MW each; recorded as one edge of 200 MW because the "
       "release states them as one signing. GET H2 Nukleus.")
E("itm-power", "an undisclosed customer (a 100MW project in Germany)", "equipment_order",
  "supplier", "supplier_press",
  I + "itm-power-contract-award-towards-100mw-project-in-germany", "2023-07-17",
  quantity=(100, "MW"),
  note="Long-lead materials and MEP30 skids only, not the whole plant. 'the third "
       "100MW project we are entrusted to execute'.")
E("itm-power", "an undisclosed customer", "framework_agreement", "supplier",
  "supplier_press", I + "multi-hundred-mw-feed-contract-signed", "2024-02-12",
  quantity=None, note="A FEED contract at '100MW+ scale'; neither customer nor a "
                      "figure is stated in the release.")
E("itm-power", "Hygen", "framework_agreement", "supplier", "supplier_press",
  I + "hygen-appoint-itm-as-preferred-supplier", "2024-04-26", quantity=(200, "MW"),
  country="GB", sector="hydrogen",
  note="Preferred supplier; 'up to 200 MW of electrolyser projects over the coming "
       "years', phase 1 about 50MW. No site named.")
E("itm-power", "Shell", "framework_agreement", "supplier", "supplier_press",
  I + "500mw-capacity-reservation", "2024-07-08", quantity=(100, "MW"), country="GB",
  sector="oil and gas", note="Not this release's subject: it is the sentence 'Following "
                             "the already announced capacity reservation for 100MW from "
                             "Shell'. Recorded from the page that states it, which is "
                             "the only page this sweep read that does.")
E("itm-power", "a global industrial customer", "framework_agreement", "supplier",
  "supplier_press", I + "500mw-capacity-reservation", "2024-07-08",
  quantity=(500, "MW"), note="Capacity reservation; customer undisclosed, no site.")
E("itm-power", "a large utility company", "framework_agreement", "supplier",
  "supplier_press", I + "capacity-reservation", "2024-07-16", quantity=(8, "MW"),
  note="Four NEPTUNE II units at 2 MW for a project in the UK. The 2025-03-27 Hynamics "
       "release identifies this reservation as EDF Renewables UK / Hynamics.")
E("itm-power", "Shell (REFHYNE II, Rheinland)", "equipment_order", "supplier",
  "supplier_press", I + "100mw-refhyne-ii-contract-signed", "2024-08-13",
  quantity=(100, "MW"), country="DE", sector="refining",
  note="Following Shell's FID; Linde Engineering is the EPC integrator.")
E("itm-power", "Guttroff GmbH", "equipment_order", "supplier", "supplier_press",
  I + "first-contract-signed-for-neptune-v", "2024-11-08", quantity=(5, "MW"),
  country="DE", sector="industrial gases", note="One NEPTUNE V unit, 5 MW.")
E("itm-power", "an undisclosed green hydrogen plant developer", "framework_agreement",
  "supplier", "supplier_press", I + "50mw-feed-contract-signed", "2024-12-20",
  quantity=(50, "MW"), note="FEED for a 50MW site 'in the European Union'; ten NEPTUNE "
                            "V units; FID expected 2025.")
E("itm-power", "an undisclosed customer (three German refuelling projects)",
  "equipment_order", "supplier", "supplier_press", I + "contract-for-three-neptune-v",
  "2024-12-23", quantity=(15, "MW"),
  note="Three NEPTUNE V units at 5 MW, into three individual projects supplying "
       "refuelling stations in Germany.")
E("itm-power", "a European energy company", "framework_agreement", "supplier",
  "supplier_press", I + "feed-contract-signed", "2025-01-24", quantity=(10, "MW"),
  note="A standard 10MW design the customer intends to deploy in several UK projects. "
       "One design, several sites, none named.")
E("itm-power", "La Française de l'Energie SA (FDE)", "equipment_order", "supplier",
  "supplier_press", I + "contract-for-four-neptune-v", "2025-02-13", quantity=(20, "MW"),
  country="FR", sector="energy", note="Four NEPTUNE V units totalling 20MW.")
E("itm-power", "EDF Renewables UK and Hynamics", "equipment_order", "supplier",
  "supplier_press", I + "engineering-integration-package-for-hynamics", "2025-03-27",
  quantity=(8, "MW"), country="GB", sector="energy",
  note="Plant integration engineering package for Tees Green Hydrogen phase 1; four "
       "NEPTUNE II units, and the release names this as the 2024-07-16 reservation.")
E("itm-power", "Deutsche Bahn AG", "framework_agreement", "supplier", "supplier_press",
  I + "itm-and-deutsche-bahn-forge-partnership-for-sustainable-transportation-and-infrastructure", "2025-03-31",
  quantity=None, country="DE", sector="rail")
E("itm-power", "Westnetz GmbH", "equipment_order", "supplier", "supplier_press",
  I + "sale-of-neptune-v", "2025-05-06", quantity=(5, "MW"), country="DE",
  sector="gas and electricity distribution", note="Dortmund-based DSO. One NEPTUNE V.")
E("itm-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  I + "selected-by-uniper-for-120mw-green-hydrogen-project", "2025-05-08",
  quantity=(120, "MW"), country="GB", sector="power",
  note="Selection, not a contract: Humber H2ub (Green), six 20MW POSEIDON modules, "
       "shortlisted in HAR2.")
E("itm-power", "a leading Spanish cement producer", "equipment_order", "supplier",
  "supplier_press", I + "sale-of-neptune-ii", "2025-05-09", quantity=(2, "MW"),
  country="ES", sector="cement",
  note="ITM's FIRST system into the cement industry, hydrogen co-fired with natural gas "
       "in the kiln. The producer is not named, so it matches no row and cannot be "
       "made into one; a cement edge with an anonymous cement customer is exactly the "
       "shape the register cannot yet hold.")
E("itm-power", "an undisclosed customer (a UK HAR2 project and a smaller UK project)",
  "framework_agreement", "supplier", "supplier_press", I + "selected-for-two-uk-projects",
  "2025-06-17", quantity=None,
  note="Preferred supplier on two UK projects, both pre-FID. The 2025-08-13 MorGen "
       "release confirms one of the two is West Wales Hydrogen.")
E("itm-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  I + "feed-contract-for-uniper's-120mw-green-hydrogen-project", "2025-06-23",
  quantity=(120, "MW"), country="GB", sector="power",
  note="FEED contract following the 8 May selection. Still subject to FID.")
E("itm-power", "MorGen Energy", "equipment_order", "supplier", "supplier_press",
  I + "20mw-supply-agreement-signed", "2025-08-13", quantity=(20, "MW"), country="GB",
  sector="hydrogen", note="West Wales Hydrogen, Milford Haven; HAR1. Supply agreement "
                          "and binding heads of terms.")
E("itm-power", "RWE", "framework_agreement", "supplier", "supplier_press",
  I + "capacity-reservation-with-rwe-for-150mw-of-neptune-v-units", "2025-09-22",
  quantity=(150, "MW"), country="DE", sector="power",
  note="30 NEPTUNE V units, call-offs by 2027. Repeat business alongside the 200MW "
       "Lingen delivery.")
E("itm-power", "Stablegrid Group", "framework_agreement", "supplier", "supplier_press",
  I + "stablegrid-group-selects-itm-power-for-710-mw-of-energy-infrastructure-projects-"
      "in-germany", "2025-11-21", quantity=(710, "MW"), country="DE",
  sector="grid balancing / hydrogen",
  note="Two named German projects: Netzbrücke 410 at Rüstringen (30 MW, FID expected "
       "2026) and a second of 680 MW (pre-FEED from January 2026, FID anticipated "
       "2028). 710 MW is the sum the release states, and 680 of it is a 2028 decision.")
E("itm-power", "a project managed by Octopus Energy Generation (Kimberly-Clark "
  "Northfleet)", "equipment_order", "supplier", "supplier_press",
  I + "12.5-mw-contract-with-octopus-energy-generation", "2025-12-18",
  quantity=(12.5, "MW"), country="GB", sector="paper / consumer products",
  note="NEPTUNE V systems at Kimberly-Clark's Northfleet plant, Gravesend, Kent.")
E("itm-power", "MorGen Energy", "equipment_order", "supplier", "supplier_press",
  I + "morgen-energy-20-mw-project-fid-and-ltsa-signed", "2026-03-11",
  quantity=(20, "MW"), country="GB", sector="hydrogen",
  note="FID and long-term services agreement on the 2025-08-13 supply agreement.")
E("itm-power", "Rheinmetall", "framework_agreement", "supplier", "supplier_press",
  I + "strategic-collaboration-with-rheinmetall-for-the-giga-ptx-project", "2026-04-17",
  quantity=None, country="DE", sector="defence / e-fuels",
  note="Giga PtX: 'several hundred decentralised production plants across Europe, each "
       "with an electrolysis capacity of up to 50 MW'. An envisaged programme, not an "
       "order, and no quantity is recorded for it.")
E("itm-power", "Protium", "framework_agreement", "supplier", "supplier_press",
  I + "strategic-partnership-with-protium-for-uk-green-hydrogen-projects", "2026-06-03",
  quantity=None, country="GB", sector="hydrogen")
E("itm-power", "DB Systemtechnik GmbH", "framework_agreement", "supplier",
  "supplier_press",
  I + "itm-and-db-systemtechnik-to-forge-an-innovation-and-research-partnership",
  "2026-06-24", quantity=None, country="DE", sector="rail",
  note="Letter of intent for an innovation and research partnership.")
E("itm-power", "RWE (GET H2 Nukleus, Lingen)", "equipment_order", "supplier",
  "supplier_press", I + "first-hydrogen-from-lingen-reaches-customer", "2026-08-04",
  quantity=(200, "MW"), country="DE", sector="power / hydrogen",
  note="DELIVERY milestone on the 2023-01-31 order, first hydrogen produced. Same 200 "
       "MW, third document.")

# --- thyssenkrupp nucera AG & Co. KGaA ---------------------------------------
# Newsroom swept in full from the TYPO3 sitemap: 93 items under
# /newsroom/news-press-releases/, all fetched. THE ARTICLE PAGES CARRY NO DATE —
# no dateline in the markup, no datePublished, no <time> — so every date below
# comes from the listing page /newsroom/news-press-releases, which prints one
# beside each item. Where the article text opens with its own dateline the two
# agree; where it does not, the listing is the only source and is cited as such.
K = "https://www.thyssenkrupp-nucera.com/newsroom/news-press-releases/"

C("tk-nucera", 1000, "MW/yr", "nameplate", "supplier", "supplier_press",
  K + "expansion-to-5-gigawatts-of-annual-production-capacity-bmbf", "2021-10-08",
  note="'the existing supply chain of 1 gigawatt (GW) of electrolysis cells'. The "
       "release is about a EUR 8.5m BMBF subsidy for R&D towards 5 GW; the 5 GW is the "
       "aim of the research and is not recorded as capacity.")
C("tk-nucera", 1500, "MW", "backlog", "supplier", "supplier_quarterly_report",
  K + "thyssenkrupp-nucera-continues-stable-business-development-in-the-third-quarter",
  "2025-08-28",
  note="'a capacity of around 1.5 gigawatts (GW) produced last year', and in the same "
       "paragraph 'engineering orders totaling 1.5 gigawatts'. Two different 1.5 GWs — "
       "one delivered, one in engineering — stated one sentence apart. Recorded once, "
       "as backlog, with the ambiguity written here rather than resolved.")

E("tk-nucera", "Shell (Holland Hydrogen I)", "equipment_order", "supplier",
  "supplier_press",
  K + "thyssenkrupp-to-install-200-mw-green-hydrogen-facility-for-shell-in-port-of-"
      "rotterdam", "2022-01-13", quantity=(200, "MW"), country="NL", sector="refining",
  note="Engineer, procure and fabricate; ten 20 MW alkaline modules. Signed as "
       "thyssenkrupp Uhde Chlorine Engineers, the node's former name.")
E("tk-nucera", "a European customer from a carbon-intensive industry",
  "framework_agreement", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-and-customer-signed-contract-to-reserve-large-scale-"
      "electrolyzer-production-capacity-for-green-hydrogen", "2023-02-27", quantity=None,
  note="First reservation agreement the company sold. 'The two companies have agreed "
       "not to disclose further contract details' — no capacity, no country, no sector "
       "beyond 'carbon-intensive'.")
E("tk-nucera", "H2 Green Steel", "equipment_order", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-supplies-the-electrolyzers-for-h2-green-steel-to-build-one-of-"
      "the-largest-integrated-green-steel-plants-in-europe", "2023-05-22",
  quantity=(700, "MW"), country="SE", sector="steel",
  note="'more than 700 MW' of 20 MW scalum modules at Boden. H2 Green Steel is the "
       "former name of Stegra and the register's stegra-boden row is the same plant; "
       "the alias index matches on 'Boden'.")
E("tk-nucera", "Neste", "framework_agreement", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-and-neste-sign-agreement-to-reserve-production-capacities-for-"
      "120-mw-water-electrolyser-at-nestes-refinery-in-finland", "2023-10-10",
  quantity=(120, "MW"), country="FI", sector="refining",
  note="Six 20 MW scalum modules for the Porvoo refinery. A reservation agreement, not "
       "an order.")
E("tk-nucera", "Cepsa", "framework_agreement", "supplier", "supplier_press",
  K + "cepsa-selects-thyssenkrupp-nucera-as-preferred-supplier-of-a300-mw-electrolyzer-"
      "for-green-hydrogen-plant-in-spain", "2024-05-13", quantity=(300, "MW"),
  country="ES", sector="refining / energy",
  note="Preferred supplier plus a basic engineering design package through to FID; "
       "15 scalum units. Cepsa is now Moeve — see the 2026-03-18 edge.")
E("tk-nucera", "an anonymous customer (a 600 MW project in Europe)",
  "framework_agreement", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-signs-feed-study-for-a-600-mw-green-hydrogen-project-in-europe",
  "2025-06-16", quantity=(600, "MW"),
  note="FEED study; the hydrogen is for 'hard-to-abate industries'. FID possibly 2026.")
E("tk-nucera", "Moeve", "equipment_order", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-supplies-electrolyzers-for-moeve-to-build-southern-europes-"
      "largest-green-hydrogen-project", "2026-03-18", quantity=(300, "MW"), country="ES",
  sector="refining / energy",
  note="Engineering, procurement, fabrication and supply; 15 units of 20 MW for phase "
       "one (Onuba) of the Andalusian Green Hydrogen Valley at La Rábida, Huelva. "
       "Moeve took FID in early March 2026. Same 300 MW as the 2024 Cepsa selection, "
       "two years and a company rename later.")
E("tk-nucera", "an unnamed alliance of European transmission operators and industry",
  "framework_agreement", "supplier", "supplier_press",
  K + "european-multinational-industry-alliance-to-establish-hydrogen-single-market-via-"
      "h2med-corridor", "2024-12-11", quantity=None,
  note="H2Med corridor alliance. Not an order and not demand on a factory; recorded "
       "because it is an admissible supplier statement naming European counterparties, "
       "and left for the ruling.")

# --- Siemens Energy AG --------------------------------------------------------
# Newsroom swept from the global/en sitemap: 353 items under /press-releases/, all
# fetched. THE PERIMETER FOR THIS NODE IS ELECTROLYSERS AND NOTHING ELSE — DECISION
# D-4. Siemens Energy's press output is mostly grid connections, gas and steam
# turbines and wind, and its largest European contracts by value in this period are
# for equipment this node kind does not name. Twenty-two of the 353 releases are
# about electrolysis; those are read, and the rest are counted and not read.
G = "https://www.siemens-energy.com/global/en/home/press-releases/"

C("siemens-energy", 3000, "MW/yr", "nameplate", "supplier", "supplier_press",
  G + "opening-of-the-siemens-energy-electrolyzer-factory.html", "2023-11-08",
  note="Berlin, opened with Air Liquide: 'By 2025, at least three gigawatts of "
       "electrolysis capacity per year are to be brought to market from there.' A 2025 "
       "target stated in 2023 — the release does not say the line ran at that rate on "
       "the day it opened.")

E("siemens-energy", "Air Liquide", "framework_agreement", "supplier", "supplier_press",
  G + "siemens-energy-and-air-liquide-develop-large-scale-electrolyzer-partnership.html",
  "2021-02-08", quantity=None, country="FR", sector="industrial gases",
  note="MoU to combine PEM expertise. Air Liquide is itself a node on this perimeter.")
E("siemens-energy", "Messer Group", "framework_agreement", "supplier", "supplier_press",
  G + "siemens-energy-and-messer-group-cooperate-hydrogen-electrolysis-integrated-hub-"
      "concept.html", "2021-04-23", quantity=(70, "MW"), country="DE",
  sector="industrial gases",
  note="Cooperation for 5–50 MW projects. The 70 MW is not an order: it is the total of "
       "three projects Messer Ibérica had submitted to the Spanish government at "
       "Tarragona. Recorded because it is the only figure stated, with this caveat.")
E("siemens-energy", "European Energy", "equipment_order", "supplier", "supplier_press",
  G + "siemens-energy-secures-electrolyzer-order-european-energy-worlds-first-large-"
      "scale.html", "2022-03-02", quantity=(50, "MW"), country="DK",
  sector="e-methanol / renewables", note="Kassø, near Aabenraa; e-methanol for Maersk "
                                         "and Circle K. Three full PEM arrays.")
E("siemens-energy", "Air Liquide", "framework_agreement", "supplier", "supplier_press",
  G + "siemens-energy-and-air-liquide-form-joint-venture-european-production-large-"
      "scale.html", "2022-06-23", quantity=None, country="FR", sector="industrial gases",
  note="Joint venture, 74.9/25.1, for the Berlin stack factory. A shareholding, not an "
       "order; recorded because the same factory is this node's stated capacity and the "
       "JV is who owns it.")
E("siemens-energy", "Air Liquide (Normand'Hy)", "equipment_order", "supplier",
  "supplier_press", G + "250,000-tons-less-CO2-thanks-to-renewable-hydrogen.html",
  "2023-09-15", quantity=(200, "MW"), country="FR", sector="industrial gases",
  note="12 electrolysers, 200 MW total, Port-Jérôme, Normandy; 28,000 t of hydrogen a "
       "year from 2026. Air Liquide is the operator, the JV partner and a node — the "
       "same firm in three roles in one sweep.")
E("siemens-energy", "EWE", "equipment_order", "supplier", "supplier_press",
  G + "siemens-energy-wins-contract-for-large-scale-hydrogen-project-fr.html",
  "2024-07-25", quantity=(280, "MW"), country="DE", sector="utility",
  note="Emden, part of Clean Hydrogen Coastline; operation expected 2027, up to 26,000 "
       "t/yr. A ten-year service contract was agreed alongside.")

# --- Sunfire GmbH / SE --------------------------------------------------------
# Newsroom swept in full from the sitemap: 100 English items under /en/news/, all
# fetched. Sunfire is UNLISTED, so there is no annual report, no order book and no
# quarterly order-intake line; the only figure the company has published for its
# own backlog is in a year-in-review post, and it is recorded as such.
F = "https://sunfire.de/en/news/"

C("sunfire", 800, "MW", "backlog", "supplier", "supplier_press",
  F + "sunfire-year-in-review-2024/", "2024-12-19",
  note="'an order backlog exceeding 800 megawatts'. Backlog, not factory capacity — "
       "Sunfire is unlisted and publishes no nameplate figure for its lines. The one "
       "capacity statement it does make (2022-01-14) is that it will manufacture 'for "
       "hydrogen projects on the 100 MW scale', which is a product size and not a rate.")

E("sunfire", "Salzgitter Flachstahl GmbH", "equipment_order", "supplier",
  "supplier_press",
  F + "grinhy2-0-sunfire-delivers-the-worlds-largest-high-temperature-electrolyzer-to-"
      "salzgitter-flachstahl/", "2020-08-25", quantity=(0.72, "MW"),
  project_id="salcos-salzgitter", country="DE", sector="steel",
  note="GrInHy2.0, 720 kW HTE inside Salzgitter Flachstahl's works. project_id set by "
       "hand: the bare alias 'Salzgitter' is ambiguous between the steel row and the "
       "PowerCo battery row, and a high-temperature electrolyser feeding a steel plant "
       "is not ambiguous to a reader. The 2021-07-14 release names SALCOS explicitly.")
E("sunfire", "TotalEnergies", "equipment_order", "supplier", "supplier_press",
  F + "totalenergies-sunfire-and-fraunhofer-give-the-go-ahead-for-green-methanol-in-leuna/",
  "2021-06-15", quantity=(1, "MW"), country="FR", sector="refining",
  note="e-CO2Met at Leuna; 1 MW high-temperature electrolyser.")
E("sunfire", "ENERTRAG", "framework_agreement", "supplier", "supplier_press",
  F + "new-hydrogen-center-enertrag-and-sunfire-start-cooperation-to-operate-a-10-mw-"
      "pressurized-alkaline-electrolyzer/", "2021-09-09", quantity=(10, "MW"),
  country="DE", sector="renewables",
  note="Cooperation agreement to operate a 10 MW pressurized alkaline electrolyser at a "
       "new hydrogen centre.")
E("sunfire", "Demo4Grid project partners (MPREIS)", "equipment_order", "supplier",
  "supplier_press",
  F + "the-demo4grid-project-partners-have-successfully-installed-a-3-2-mw-pressurized-"
      "alkaline-electrolyzer/", "2021-12-21", quantity=(3.2, "MW"), country="AT",
  sector="food retail", note="Völs, Tyrol. Installed at the MPREIS site — see the "
                             "2022-03-28 first-hydrogen release.")
E("sunfire", "P2X Solutions", "equipment_order", "supplier", "supplier_press",
  F + "finlands-first-green-hydrogen-production-plant-will-run-on-sunfires-electrolysis-"
      "technology/", "2022-03-22", quantity=(20, "MW"), country="FI", sector="hydrogen",
  note="Harjavalta; Finland's first industrial green hydrogen plant.")
E("sunfire", "RWE", "equipment_order", "supplier", "supplier_press",
  F + "rwe-realizes-electrolysis-project-with-sunfire/", "2022-05-03", quantity=(10, "MW"),
  country="DE", sector="power", note="Pressurized alkaline; the Lingen site.")
E("sunfire", "Neste", "equipment_order", "supplier", "supplier_press",
  F + "worlds-largest-high-temperature-electrolysis-module-deliveries-started/",
  "2022-07-05", quantity=(2.6, "MW"), country="NL", sector="refining",
  note="MultiPLHY, Neste's Rotterdam refinery. EU-funded under Clean Hydrogen "
       "Partnership grant 875123.")
E("sunfire", "Uniper", "equipment_order", "supplier", "supplier_press",
  F + "bad-lauchstaedt-uniper-orders-sunfire-electrolyzer/", "2022-08-04",
  quantity=(30, "MW"), country="DE", sector="utility",
  note="Bad Lauchstädt Energy Park, Central German Chemical Triangle.")
E("sunfire", "Vitesco Technologies", "framework_agreement", "supplier", "supplier_press",
  F + "sunfire-and-vitesco-technologies-become-strategic-partners/", "2023-01-12",
  quantity=None, country="DE", sector="automotive components",
  note="Strategic partnership on electrolyser component manufacture — Vitesco is a "
       "supplier INTO Sunfire here, not a customer. Recorded and flagged; the ruling on "
       "direction is the reader's, and this one plainly runs the other way.")
E("sunfire", "Uniper (Project Air)", "equipment_order", "supplier", "supplier_press",
  F + "project-air-in-sweden-uniper-commissions-sunfire-to-build-a-30-mw-electrolyzer/",
  "2023-01-31", quantity=(30, "MW"), country="SE", sector="chemicals",
  note="Stenungsund, Sweden; Project Air, with Perstorp as the site owner.")
E("sunfire", "a leading refinery in Europe", "equipment_order", "supplier",
  "supplier_press",
  F + "sunfire-receives-purchase-order-for-100-mw-pressurized-alkaline-electrolyzer/",
  "2023-08-24", quantity=(100, "MW"),
  note="Ten 10 MW modules. Sunfire's first commercial 100 MW order; the customer is "
       "described only as 'a leading refinery in Europe'.")
E("sunfire", "an undisclosed customer (a 500 MW European project)", "framework_agreement",
  "supplier", "supplier_press",
  F + "sunfire-conducts-feed-study-for-500-mw-green-hydrogen-project/", "2024-04-18",
  quantity=(500, "MW"),
  note="FEED study for a 500 MW pressurized alkaline plant, operation targeted 2028; "
       "hydrogen for refinery operations and ammonia.")
E("sunfire", "RWE", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-builds-100-megawatt-electrolyzer-for-rwe/", "2024-09-11",
  quantity=(100, "MW"), country="DE", sector="power", note="RWE's Lingen site.")
E("sunfire", "Ren-Gas", "equipment_order", "supplier", "supplier_press",
  F + "ren-gas-selects-sunfire-electrolyzer-for-its-tampere-e-methane-plant/",
  "2024-11-19", quantity=(50, "MW"), country="FI", sector="e-methane")
E("sunfire", "Basque Hydrogen (Petronor / Repsol, Enagás Renovable, Ente Vasco de la "
  "Energía)", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-enters-spanish-market-with-new-electrolysis-project/", "2025-04-09",
  quantity=(10, "MW"), country="ES", sector="refining")
E("sunfire", "Neste", "equipment_order", "supplier", "supplier_press",
  F + "worlds-largest-soec-electrolyzer-startet-up-at-nestes-rotterdam-refinery/",
  "2025-10-06", quantity=(2.6, "MW"), country="NL", sector="refining",
  note="START-UP of the 2022-07-05 delivery, twelve SOEC modules. Same plant, second "
       "document.")
E("sunfire", "P2X Solutions", "framework_agreement", "supplier", "supplier_press",
  F + "p2x-solutions-and-sunfire-expand-partnership-with-new-hydrogen-project/",
  "2025-10-08", quantity=(40, "MW"), country="FI", sector="hydrogen",
  note="FEED study for a 40 MW project at Joensuu.")
E("sunfire", "Rheinmetall (Giga PtX)", "framework_agreement", "supplier", "supplier_press",
  F + "german-industrial-giants-and-tech-companies-announce-rheinmetall-partnership-for-"
      "giga-ptx/", "2025-11-03", quantity=None, country="DE", sector="defence / e-fuels",
  note="The same Giga PtX programme ITM Power announced on 2026-04-17. Two nodes on "
       "this perimeter named as partners in one programme, five months apart.")
E("sunfire", "Repsol and Enagás Renovable (Cartagena); Petronor (Muskiz)",
  "equipment_order", "supplier", "supplier_press",
  F + "sunfire-secures-200-mw-electrolyzer-orders-in-spain/", "2026-01-27",
  quantity=(200, "MW"), country="ES", sector="refining",
  note="TWO 100 MW plants stated in one release — Cartagena and Muskiz — recorded as "
       "one 200 MW edge because that is how the release states the order. Ten 10 MW "
       "modules each, commissioning 2029, up to 15,000 t H2/yr each.")
E("sunfire", "Nordic Ren-Gas", "framework_agreement", "supplier", "supplier_press",
  F + "nordic-ren-gas-announces-partnership-agreement-with-sunfire/", "2026-07-22",
  quantity=None, country="FI", sector="e-methane")
E("sunfire", "BASF", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-to-build-electrolysis-test-facility-at-basf-site-in-schwarzheide/",
  "2026-05-11", quantity=None, country="DE", sector="chemicals",
  note="An SOEC TEST facility at BASF's Schwarzheide site under the H2Giga flagship. "
       "A test rig is not plant demand and is recorded with no quantity.")

# --- Plug Power Inc. ----------------------------------------------------------
# 317 releases 2020–2026, listed and read through the Q4 investor-relations feed
# at www.ir.plugpower.com/feed/PressRelease.svc, one call per year, bodyType=1 so
# the feed returns the full release text.
#
# THE DETAIL PAGES ARE NOT READABLE BY THIS SWEEP. plugpower.com's edge answers 403
# to every /press-releases/news-details/ URL even with a full browser header set,
# while the feed the same site publishes answers 200 with the same content. The url
# on each edge below is therefore the FEED URL — the artefact that was actually
# fetched, hashed and cached — and the note carries the public permalink for a
# reader. Citing a page this sweep could not open would be citing something nobody
# read. DECISION D-6.
def PF(year: int) -> str:
    return ("https://www.ir.plugpower.com/feed/PressRelease.svc/GetPressReleaseList?"
            "LanguageId=1&bodyType=1&pressReleaseDateFilter=3&categoryId="
            "00000000-0000-0000-0000-000000000000&pageSize=200&pageNumber=0&"
            f"year={year}&excludeSelection=1")

P = "https://www.ir.plugpower.com/press-releases/news-details/"

E("plug-power", "Groupe Renault", "framework_agreement", "supplier", "supplier_press",
  PF(2021), "2021-01-12", quantity=None, country="FR", sector="automotive",
  note="MoU for the 50-50 HYVIA joint venture on fuel-cell light commercial vehicles. "
       "Permalink " + P + "2021/Groupe-Renault-Plug-Power-Join-Forces-to-Become-Leader-"
       "in-Hydrogen-LCV/default.aspx")
E("plug-power", "ACCIONA", "framework_agreement", "supplier", "supplier_press",
  PF(2021), "2021-02-16", quantity=None, country="ES", sector="renewables",
  note="MoU for an Iberian green hydrogen joint venture targeting 'more than 100 tons "
       "per day'. Tonnes of hydrogen a day, not MW — this quantity cannot be compared "
       "with the node's MW capacity and is left out of `quantity` rather than converted.")
E("plug-power", "Lhyfe", "framework_agreement", "supplier", "supplier_press",
  PF(2021), "2021-10-27", quantity=(300, "MW"), country="FR", sector="hydrogen",
  note="Commercial arrangement to develop plants across Europe: '300MW ... sites to "
       "start operation in 2025' and an initiative towards a 1 GW site.")
E("plug-power", "ACCIONA Energía", "framework_agreement", "supplier", "supplier_press",
  PF(2021), "2021-11-30", quantity=None, country="ES", sector="renewables",
  note="AccionaPlug formed. Same venture as the February MoU, now finalised.")
E("plug-power", "H2 Energy Europe", "equipment_order", "supplier", "supplier_press",
  PF(2022), "2022-05-17", quantity=(1000, "MW"), country="DK", sector="hydrogen",
  note="Plug's largest electrolyser order to that date, for a production complex in "
       "Denmark; up to 100,000 t/yr of hydrogen for northern European transport.")
E("plug-power", "Lhyfe", "equipment_order", "supplier", "supplier_press",
  PF(2022), "2022-09-08", quantity=(50, "MW"), country="FR", sector="hydrogen",
  note="Ten 5 MW European-manufactured PEM systems; 'Plug's largest multi-site "
       "electrolyzer order in Europe'.")
E("plug-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  PF(2023), "2023-03-07", quantity=(100, "MW"), country="NL", sector="utility",
  note="Selected to DESIGN the 100 MW electrolyser package for H2Maasvlakte at the Port "
       "of Rotterdam. A design selection, not a supply order.")
E("plug-power", "Ardagh Glass Limmared AB", "equipment_order", "supplier",
  "supplier_press", PF(2023), "2023-05-22", quantity=(5, "MW"), country="SE",
  sector="glass packaging",
  note="One of three deals in one release. East of Gothenburg; 2.1 t/day of hydrogen "
       "replacing part of the natural gas at the works. First industrial-scale green "
       "hydrogen in glass manufacture.")
E("plug-power", "Hydro Havrand", "equipment_order", "supplier", "supplier_press",
  PF(2023), "2023-05-22", quantity=(5, "MW"), country="NO", sector="aluminium recycling",
  note="A unit of Norsk Hydro ASA. Second of the three deals in the 22 May release.")
E("plug-power", "APEX Group", "equipment_order", "supplier", "supplier_press",
  PF(2023), "2023-05-22", quantity=(5, "MW"), country="DE", sector="steel",
  note="Third of the three. The release names steel manufacturing as the application. "
       "A STEEL customer of an electrolyser OEM that matches no row in the register's "
       "steel perimeter — the same shape as Nel/Ovako.")
E("plug-power", "an undisclosed customer (an oil refining project in Europe)",
  "equipment_order", "supplier", "supplier_press", PF(2023), "2023-07-13",
  quantity=(100, "MW"),
  note="'the largest announced project in the oil and gas sector in Europe'; ~43 t/day "
       "of hydrogen replacing grey hydrogen in refining. Delivery and installation 2024. "
       "Very likely the Galp Sines project named from 2025 onward, and the sweep does "
       "not assert that, because neither document says so.")
E("plug-power", "an undisclosed customer (a 500MW European project)",
  "framework_agreement", "supplier", "supplier_press", PF(2024), "2024-02-02",
  quantity=(500, "MW"), note="Basic Engineering and Design Package signed 29 January "
                             "2024; takes Plug's global BEDP total to 4.1 GW.")
E("plug-power", "undisclosed customers (two BEDP projects, Europe and the US)",
  "framework_agreement", "supplier", "supplier_press", PF(2024), "2024-04-25",
  quantity=(350, "MW"),
  note="Two contracts, combined up to 350 MW, split between Europe and the US in an "
       "unstated proportion. Recorded whole, with that written here: splitting it would "
       "be inventing the split.")
E("plug-power", "an undisclosed customer in Europe", "equipment_order", "supplier",
  "supplier_press", PF(2024), "2024-06-21", quantity=(25, "MW"),
  note="Five 5 MW containerised PEM systems.")
E("plug-power", "Castellón Green Hydrogen S.L. (bp and Iberdrola joint venture)",
  "equipment_order", "supplier", "supplier_press", PF(2024), "2024-09-18",
  quantity=(25, "MW"), country="ES", sector="refining",
  note="Five 5 MW units to decarbonise bp's Castellón refinery, Valencia.")
E("plug-power", "Galp", "equipment_order", "supplier", "supplier_press",
  PF(2025), "2025-10-01", quantity=(100, "MW"), country="PT", sector="refining",
  note="First 10 MW module delivered of ten for the Sines refinery.")
E("plug-power", "Gasunie and STORAG ETZEL (H2CAST)", "equipment_order", "supplier",
  "supplier_press", PF(2025), "2025-10-21", quantity=(44.5, "tonnes of hydrogen"),
  country="DE", sector="gas storage",
  note="A MOLECULE supply, not equipment: 44.5 t of hydrogen delivered for cavern "
       "storage testing, with a new contract for 35 t more. edge_kind equipment_order "
       "is the closest the vocabulary comes and it is wrong in kind — flagged as new "
       "vocabulary pressure in the docket.")
E("plug-power", "H2 Hollandia", "equipment_order", "supplier", "supplier_press",
  PF(2025), "2025-11-05", quantity=(5, "MW"), country="NL", sector="hydrogen",
  note="Plug's first commercial electrolyser deployment in the Netherlands.")
E("plug-power", "Carlton Power", "framework_agreement", "supplier", "supplier_press",
  PF(2025), "2025-11-17", quantity=(55, "MW"), country="GB", sector="hydrogen",
  note="Equipment supply and LTSA for three UK projects, SUBJECT TO FID: Barrow-in-"
       "Furness 30 MW (offtake to Kimberly-Clark), Trafford 15 MW, Langage 10 MW. "
       "Kimberly-Clark also appears as ITM Power's Northfleet offtaker — the same "
       "offtaker behind two different electrolyser suppliers.")
E("plug-power", "Hy2gen", "framework_agreement", "supplier", "supplier_press",
  PF(2025), "2025-12-04", quantity=(5, "MW"), country="FR", sector="e-fuels",
  note="Letter of intent for the Sunrhyse project, Provence-Alpes-Côte d'Azur.")
E("plug-power", "Galp", "equipment_order", "supplier", "supplier_press",
  PF(2026), "2026-01-23", quantity=(100, "MW"), country="PT", sector="refining",
  note="INSTALLATION COMPLETE — all ten arrays at Sines. Same order as 2025-10-01, "
       "third document if the 2023-07-13 anonymous edge is the same project.")
E("plug-power", "Hynetwork", "co2_transport", "supplier", "supplier_press",
  PF(2026), "2026-02-04", quantity=(32, "tonnes of hydrogen"), country="NL",
  sector="hydrogen network",
  note="First fill of a 32 km hydrogen pipeline in Rotterdam. NOT CO2 and not "
       "equipment: the vocabulary has no hydrogen_transport value and this edge is "
       "filed under the nearest one, wrongly. Flagged in the docket.")
E("plug-power", "European Energy", "equipment_order", "supplier", "supplier_press",
  PF(2026), "2026-06-24", quantity=(5, "MW"), country="DK", sector="e-fuels",
  note="Commissioning complete at the Måde Power-to-X facility, Esbjerg. European "
       "Energy is also Siemens Energy's Kassø customer — one owner, two suppliers on "
       "this perimeter.")

# --- John Cockerill -----------------------------------------------------------
# The two news sitemaps list 1,060 items; 118 whose slug mentions hydrogen,
# electrolysis, green, steel or a register company were fetched and read. THE
# NEWSROOM PRINTS NO DATE a reader can see, but every page declares a schema.org
# datePublished, and that is what the dates below are — see dep_digest.meta_date.
#
# John Cockerill is UNLISTED. There is no annual report, no order book, and the
# only capacity-like figures it publishes are in its own year-in-review posts.
J = "https://johncockerill.com/en/press-and-news/news/"

C("john-cockerill", 200, "MW", "delivery_commitment", "supplier", "supplier_press",
  J + "green-hydrogen-john-cockerill-unveils-outstanding-track-record-in-2021-with-33-"
      "market-share-of-global-electrolysers-deliveries-100-takeover-of-cockerill-jingli-"
      "in-china-and-major-strategic-partners/", "2022-03-24",
  note="'exceptional sales in 2021, totaling close to 200 megawatts'. SALES IN A YEAR, "
       "which is neither nameplate nor backlog; delivery_commitment is the closest "
       "value in the vocabulary and it is not a good fit — flagged in the docket. The "
       "same release claims a 33% world market share of shipments, which is a share and "
       "not a capacity and is not recorded.")

E("john-cockerill", "Sibelga (H2GridLab, with Fluxys)", "framework_agreement",
  "supplier", "supplier_press",
  J + "green-hydrogen-injected-into-the-gas-grid-john-cockerill-develops-a-research-"
      "partnership-with-sibelga-on-a-fluxys-station/", "2021-03-25", quantity=None,
  country="BE", sector="gas network",
  note="A federally funded research partnership on a power-to-gas pilot, not a plant.")
E("john-cockerill", "UEM and Metz Métropole", "framework_agreement", "supplier",
  "supplier_press",
  J + "john-cockerill-uem-and-metz-metropole-are-partners-to-develop-a-hydrogen-"
      "production-chain-dedicated-to-ecomobility/", "2021-10-18", quantity=None,
  country="FR", sector="local authority / mobility")
E("john-cockerill", "RWE", "equipment_order", "supplier", "supplier_press",
  J + "rwe-and-john-cockerill-to-build-german-test-facility-for-dutch-circular-and-green-"
      "hydrogen-project-furec/", "2021-10-21", quantity=None, country="DE",
  sector="power / waste-to-hydrogen",
  note="A EUR 3m torrefaction PILOT at RWE's Niederaußem innovation centre for the "
       "Dutch FUREC project — not an electrolyser and not at scale. Recorded because "
       "the counterparty is a European owner and the ruling on pilots is not mine.")
E("john-cockerill", "Hyoffwind (Fluxys and Virya Energy) with BESIX",
  "framework_agreement", "supplier", "supplier_press",
  J + "hyoffwind-sassocie-a-john-cockerill-et-besix-pour-la-realisation-dune-"
      "installation-de-production-dhydrogene-vert-a-zeebruges/", "2022-02-15", quantity=None,
  country="BE", sector="gas network / renewables",
  note="Agreement to design and build a green hydrogen production unit at Zeebrugge. "
       "The capacity (25 MW) is stated in the later releases, not this one.")
E("john-cockerill", "Technip Energies", "framework_agreement", "supplier",
  "supplier_press",
  J + "john-cockerill-and-technip-energies-create-rely-integrated-green-hydrogen-"
      "solutions/", "2023-05-04", quantity=None, country="FR",
  sector="engineering",
  note="Formation of Rely, a joint venture. Technip Energies is a partner and route to "
       "market, not an offtaker.")
E("john-cockerill", "ArcelorMittal", "technology_licence", "supplier", "supplier_press",
  J + "arcelormittal-john-cockerill-announce-volteron/", "2023-06-14",
  quantity=(80000, "tonnes of iron plate per year"), country="LU", sector="steel",
  note="Volteron: an industrial-scale LOW-TEMPERATURE IRON ELECTROLYSIS plant, first "
       "phase 40,000–80,000 t/yr of iron plates, targeted 2027, with an intention to "
       "reach 300,000–1,000,000 t/yr. The upper bound of the stated first-phase range "
       "is recorded. This is a steel edge from an electrolyser OEM and it is not a DRI "
       "plant — the register's steel perimeter has no row for it. ArcelorMittal holds "
       "two rows and the release names neither site, so project_id is null.")
E("john-cockerill", "SSAB (via ArcelorMittal's JVD licence)", "technology_licence",
  "supplier", "supplier_press", J + "arcelormittal-jvd-technology-swedish-steelmaker-ssab/",
  "2024-06-19", quantity=None, country="SE", sector="steel",
  note="A preparation study to implement ArcelorMittal's JVD strip-coating process in "
       "SSAB's downstream production; John Cockerill is the exclusive commercialiser. "
       "Strip coating, not ironmaking — recorded because the counterparty is a European "
       "steelmaker and the exclusion would be a judgement about what counts.")
E("john-cockerill", "Virya Energy, HyoffGreen and Messer (Hyoffwind)", "equipment_order",
  "supplier", "supplier_press",
  J + "hyoffwind-25mw-green-hydrogen-production-plant-in-belgium-with-besix/", "2024-07-25", quantity=(25, "MW"), country="BE",
  sector="renewables / industrial gases",
  note="Financial close on Belgium's first renewable hydrogen production plant, "
       "Zeebrugge. Messer appears here as an owner and at Siemens Energy as a customer.")
E("john-cockerill", "Hyoffwind", "equipment_order", "supplier", "supplier_press",
  J + "john-cockerill-has-installed-four-electrolyzers-at-the-hyoffwind-site/",
  "2026-04-29", quantity=(25, "MW"), country="BE", sector="renewables",
  note="INSTALLATION: four electrolysers, 25 MW physically in place. Same plant, third "
       "document.")
E("john-cockerill", "an undisclosed customer (a green hydrogen project in the "
  "Netherlands)", "equipment_order", "supplier", "supplier_press",
  J + "hydrogen-electrolyseur-belfort-prod-aspach/", "2026-07-13", quantity=(40, "MW"),
  note="'a new 40 MW production phase is beginning for a green hydrogen project in the "
       "Netherlands'. Customer and site unnamed.")
E("john-cockerill", "Shell (with Rely)", "framework_agreement", "supplier",
  "supplier_press",
  J + "john-cockerill-rely-shell-evaluated-john-cockerills-alkaline-electrolyzer-"
      "technology/", "2026-05-11", quantity=None, country="GB", sector="oil and gas",
  note="A joint technology evaluation of safety, operability and maintainability. Not "
       "an order; recorded because Shell is a named European counterparty and the "
       "evaluation is a step towards one.")

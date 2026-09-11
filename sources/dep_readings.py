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

import dep_records as R_
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
       "No unmatched row — an undisclosed customer is not a customer nobody matched.",
  firmness="contract", firmness_basis=
  "(Oslo, 10 June 2020) Nel Hydrogen US, a subsidiary of Nel ASA (Nel, "
  "OSE:NEL), has received a purchase order for a containerized 2.5 megawatt "
  "Proton PEM® electrolyzer from a customer in Europe. “We’re proud that "
  "our customer decided to go for our Proton PEM® containerized "
  "electrolyser solution to produce green hydrogen for mobility "
  "applications in Europe, and look forward to support them in…")
E("nel", "Everfuel Europe A/S", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-h2station-from-everfuel/",
  "2020-10-05", quantity=(1, "H2Station fuelling station"), country="DK",
  sector="hydrogen refuelling",
  firmness="contract", firmness_basis=
  "(Oslo, 5 October 2020) Nel Hydrogen Fueling, a subsidiary of Nel ASA "
  "(Nel, OSE:NEL) has received a purchase order from Everfuel Europe A/S "
  "(Everfuel) for an H2Station™ hydrogen fueling station which will be used "
  "to fuel zero emission hydrogen buses in the Netherlands . \"We are "
  "delighted to get our second purchase order for an H2Station™ fueling "
  "solution from Everfuel.")
E("nel", "ZE PAK SA", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-first-h2station-order-in-poland/", "2020-10-14",
  quantity=None, country="PL", sector="power / hydrogen refuelling",
  note="'H2Station™ hydrogen fueling stations' — plural, no count stated.",
  firmness="contract", firmness_basis=
  "(Oslo, 14 October 2020) Nel Hydrogen Fueling, a subsidiary of Nel ASA "
  "(Nel, OSE:NEL) has received a purchase order from ZE PAK SA (ZE PAK) for "
  "H2Station™ hydrogen fueling stations which will be used to fuel "
  "passenger vehicles and buses in Poland. \"We’re excited to enter yet "
  "another country in Europe with our H2Station™ fueling solutions.")
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
  note="HySynergy, adjacent to the Fredericia refinery.",
  site="Fredericia HySynergy",
  firmness="contract", firmness_basis=
  "(Oslo, 30 December 2020) Nel ASA (OSE:NEL) has been awarded a 20 MW "
  "electrolyser contract with Everfuel A/S (Everfuel) for the green "
  "hydrogen production facility adjacent to the Fredericia refinery in "
  "Denmark. “Everfuel’s ambition is to commercialize the green hydrogen "
  "value chain to support Europe’s goal of becoming carbon neutral.")
E("nel", "Everfuel A/S", "equipment_order", "supplier", "supplier_press",
  N + "approval-of-everfuel-contract-nel-asa/", "2021-01-10", quantity=(20, "MW"),
  country="DK", sector="hydrogen",
  note="Board approval of the 2020-12-30 contract. Same order, second document.",
  site="Fredericia HySynergy",
  firmness="contract", firmness_basis=
  "The contract has today been approved by the Board of Directors of Nel "
  "ASA.")
E("nel", "Iberdrola", "equipment_order", "supplier", "supplier_press",
  N + "awarded-iberdrola-contract-for-20-mw-green-fertilizer-project-in-spain/",
  "2021-01-14", quantity=(20, "MW"), country="ES", sector="fertiliser",
  note="EUR 13.5 million contract; Puertollano.",
  firmness="contract", firmness_basis=
  "Thu, Jan 14, 2021 17:45 CET (Oslo, 14 January 2021) Nel Hydrogen "
  "Electrolyser, a division of Nel ASA (Nel, OSE:NEL), has been awarded a "
  "EUR 13.5 million contract by Iberdrola for a 20 MW PEM solution for a "
  "green fertilizer project in Spain.")
E("nel", "SGN", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-5mw-alkaline-electrolyser/", "2021-09-24",
  quantity=(5, "MW"), country="GB", sector="gas network",
  firmness="contract", firmness_basis=
  "(Oslo, 24 September 2021) Nel Hydrogen Electrolyser AS, a division of "
  "Nel ASA (Nel, OSE: NEL), has received a purchase order for a 5MW "
  "alkaline water electrolyser from SGN, for the world’s first 100% "
  "hydrogen-to-homes heating network on the east coast of Scotland. \"Nel is "
  "honored to be part of this new milestone achieved in the development of "
  "a commercial green hydrogen infrastructure, clearly…")
E("nel", "Communauté de communes Touraine Vallée de l'Indre (CCTVI)", "equipment_order",
  "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-the-community-of-cities-touraine-vallee-de-"
      "lindre-cctvi-for-a-hydrogen-fueling-station-h2station-to-be-located-in-the-regi/",
  "2021-09-28", quantity=(1, "H2Station fuelling station"), country="FR",
  sector="local authority / mobility",
  firmness="contract", firmness_basis=
  "(Oslo, September 28, 2021) Nel Hydrogen Fueling, a subsidiary of Nel ASA "
  "(Nel, OSE:NEL) has received a purchase order from the Community of "
  "cities “Touraine Vallée de l’Indre\" for one H2Station™ hydrogen fueling "
  "station to be used for light and heavy duty fuel cell electric vehicles "
  "in region of Tours, France. “We are delighted to announce that we have "
  "been chosen as supplier for a fueling…")
E("nel", "MaserFrakt AB", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-maserfrakt-ab-for-h2station-hydrogen-fueling-"
      "station-in-sweden/", "2021-09-30", quantity=(1, "H2Station fuelling station"),
  country="SE", sector="haulage",
  firmness="contract", firmness_basis=
  "( Oslo, September 30, 2021) Nel Hydrogen Fueling, a subsidiary of Nel "
  "ASA (Nel, OSE: NEL) has received a purchase order from MaserFrakt AB for "
  "one H2Station™ hydrogen fueling station to be used for a fleet of heavy-"
  "duty fuel cell electric vehicles in Borlänge, Sweden. “We are very happy "
  "to be chosen by MaserFrakt to be the supplier of their first hydrogen "
  "fueling station.")
E("nel", "Ovako", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-20mw-alkaline-electrolyser-from-ovako/",
  "2021-11-25", quantity=(20, "MW"), country="SE", sector="steel",
  note="Hofors, Sweden — hydrogen to replace propane in steel REHEATING furnaces, not "
       "iron reduction. A steel customer that the register's steel perimeter does not "
       "hold, which is the finding, not a miss.",
  site="Hofors",
  firmness="contract", firmness_basis=
  "(Oslo, 25 November 2021) Nel Hydrogen Electrolyser AS, a division of Nel "
  "ASA (Nel, OSE: NEL), has received a purchase order for a 20MW alkaline "
  "water electrolyser from Ovako, a leading European manufacturer of "
  "engineering steel.")
E("nel", "a new, European customer", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-alkaline-electrolyser-system/", "2021-12-24",
  quantity=None, note="Customer undisclosed.",
  firmness="contract", firmness_basis=
  "(Oslo, 24 December 2021) Nel Hydrogen Electrolyser AS, a division of Nel "
  "ASA (Nel, OSE: NEL), has received a purchase order for an alkaline "
  "electrolyser system from a new, European customer.")
E("nel", "Solar Foods", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-nel-to-supply-an-alkaline-electrolyser-system-for-solar-foods/",
  "2022-03-16", quantity=None, country="FI", sector="food / protein",
  note="Factory 01. No capacity stated in the release.",
  firmness="contract", firmness_basis=
  "The purchase orders have a value of approximately EUR 2 million, and "
  "delivery of the equipment is expected to be late-2022 / early-2023.")
E("nel", "HysetCo", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-several-h2station-modules-in-france/",
  "2022-03-21", quantity=None, country="FR", sector="hydrogen refuelling",
  note="'several H2Station modules', Paris. No count stated.",
  firmness="contract", firmness_basis=
  "(Oslo, 21 March 2022) Nel Hydrogen Fueling, a subsidiary of Nel ASA "
  "(Nel, OSE: NEL) has received a purchase order from HysetCo for several "
  "H2Station TM modules to be used for light-duty fuel cell electric "
  "vehicles in Paris, France. “We are delighted to announce that we have "
  "been chosen as supplier for hydrogen fueling station equipment by "
  "HysetCo and are looking forward to support HysetCo’s…")
E("nel", "an undisclosed European customer", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-in-europe/",
  "2022-03-28", quantity=None,
  note="Firm order following the 23 March 2022 commercial update.",
  firmness="contract", firmness_basis=
  "Nel Hydrogen Electrolyser AS, a subsidiary of Nel ASA, has now received "
  "a firm order for an alkaline electrolyser system from an undisclosed "
  "European customer to provide green hydrogen to the European market. Nel "
  "Hydrogen Electrolyser AS has received a contract for an alkaline "
  "electrolysis hydrogen production unit to be delivered to an innovative "
  "project that will distribute green hydrogen to…")
E("nel", "Biproraf (Grupa Technologiczna ASE)", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-from-biproraf-for-hydrogen-fueling-equipment-in-"
      "poland/", "2022-04-01", quantity=(1, "H2Station fuelling station"), country="PL",
  sector="engineering / hydrogen refuelling",
  firmness="contract", firmness_basis=
  "(Oslo, April 1, 2022) Nel Hydrogen Fueling, a subsidiary of Nel ASA "
  "(Nel, OSE:NEL) has received a purchase order from Biproraf, belonging to "
  "Grupa Technologiczna ASE, for one H2Station™ hydrogen fueling station.")
E("nel", "a European customer", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-two-purchase-orders-for-h2station-fueling-systems-from-a-european-"
      "client/", "2022-04-27", quantity=(2, "H2Station fuelling system"),
  note="Two firm purchase orders; customer undisclosed.",
  firmness="contract", firmness_basis=
  "Nel Hydrogen Fueling, a subsidiary of Nel ASA (Nel, OSE:NEL) has now "
  "received two firm purchase orders from a European client for H2Station™ "
  "modules. “We are very pleased to receive these orders from the client "
  "for the H2Station systems.")
E("nel", "Glencore Nikkelverk", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-system-from-glencore-"
      "nikkelverk/", "2022-06-02", quantity=None, country="NO",
  sector="non-ferrous metals", note="Kristiansand. No capacity stated.",
  firmness="contract", firmness_basis=
  "(Oslo, 2 June 2022) Nel Hydrogen Electrolyser AS, a subsidiary of Nel "
  "ASA (Nel, OSE:NEL), has been awarded a contract for an alkaline "
  "electrolyser system to Glencore Nikkelverk in Kristansand, Norway.")
E("nel", "Skovgaard Energy ApS", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-an-alkaline-electrolyser-system-from-skovgaard-"
      "energy/", "2022-07-08", quantity=None, country="DK", sector="hydrogen / ammonia",
  note="Lemvig, western Jutland.",
  firmness="contract", firmness_basis=
  "(Oslo, 8 July 2022) Nel Hydrogen Electrolyser AS, a subsidiary of Nel "
  "ASA (Nel, OSE:NEL), has received a purchase order for an alkaline "
  "electrolyser system from Skovgaard Energy Aps in Lemvig in Western "
  "Jutland, Denmark.")
E("nel", "an undisclosed European client", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-multiple-h2station-units-in-the-netherlands/",
  "2022-08-10", quantity=None,
  note="'several H2Station™ units' for light- and heavy-duty vehicles; the title places "
       "them in the Netherlands. UNSUPPORTED AND FLAGGED, NOT RULED ON: the page now "
       "cached at this URL is Nel's 17 December 2019 OrangeGas release — a named "
       "customer, and a date before this sweep's period. Either Nel reused the slug or "
       "the reading took its date from somewhere the document does not say it. The "
       "edge stands with this note rather than being deleted, because deleting a "
       "reading is George's call and not the re-run's.",
  firmness="contract", firmness_basis=
  "(Oslo, 17 December 2019) Nel Hydrogen A/S, a subsidiary of Nel ASA (Nel, "
  "OSE:NEL), has received a purchase order from OrangeGas for the delivery "
  "of multiple H2Station® units for fueling of predominately light duty "
  "fuel cell electric vehicles in the Netherlands. “We are delighted to be "
  "chosen as supplier for OrangeGas for their first fueling stations "
  "(H2Station®) which will predominately serve…")
E("nel", "a high quality North European energy company", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-40-mw-electrolyser-order-from-undisclosed-north-european-client/",
  "2022-11-14", quantity=(40, "MW"),
  note="NOK 120 million. Nel's 2025-04-30 cancellation release names this contract as "
       "Statkraft's — see the disagreement entry in the docket.",
  firmness="contract", firmness_basis=
  "(Oslo, 14 November 2022) Nel Hydrogen Electrolyser AS, a subsidiary of "
  "Nel ASA (Nel, OSE:NEL), has signed a NOK 120 million contract for "
  "alkaline electrolyser equipment with a high quality North European "
  "energy company.")
E("nel", "HH2E", "framework_agreement", "supplier", "supplier_press",
  N + "nel-asa-nel-signs-agreement-with-hh2e-for-potential-120-mw-capacity-in-germany/",
  "2023-01-06", quantity=(120, "MW"), country="DE", sector="hydrogen",
  note="FEED study and Letter of Intent for two 60 MW plants.")
E("nel", "HyCC", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-40-mw-electrolyser-equipment-from-hycc/",
  "2023-02-06", quantity=(40, "MW"), country="NL", sector="hydrogen",
  note="H2eron, Delfzijl. About EUR 12 million.",
  site="H2eron Delfzijl",
  firmness="contract", firmness_basis=
  "(February 6, 2023 - Oslo, Norway) Nel Hydrogen Electrolyser AS, a "
  "subsidiary of Nel ASA (Nel, OSE:NEL), has signed a contract for 40 MW of "
  "alkaline electrolyser equipment for about EUR 12 million with HyCC for "
  "its H2eron project in Delfzijl, Netherlands.")
E("nel", "HH2E", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-firm-purchase-order-from-hh2e-for-120-mw-of-electrolyser-equipment/",
  "2023-03-14", quantity=(120, "MW"), country="DE", sector="hydrogen",
  note="Firm contract following the January LoI.",
  firmness="contract", firmness_basis=
  "Nel Hydrogen Electrolyser AS, a subsidiary of Nel ASA (Nel, OSE:NEL), "
  "has now signed a firm contract with HH2E for 120 MW of alkaline "
  "electrolyser equipment.")
E("nel", "Hyd'Occ", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-20-mw-electrolyser-equipment-from-hydocc/",
  "2023-07-14", quantity=(20, "MW"), country="FR", sector="hydrogen",
  note="Port-la-Nouvelle. About EUR 9 million.",
  site="Port-la-Nouvelle",
  firmness="contract", firmness_basis=
  "(July 14, 2023 - Oslo, Norway) Nel Hydrogen Electrolyser AS, a "
  "subsidiary of Nel ASA (Nel, OSE:NEL), has signed a contract for 20 MW of "
  "alkaline electrolyser equipment for about EUR 9 million with Hyd’Occ for "
  "its project in Port-La-Nouvelle, France .")
E("nel", "Bondalti", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-40-mw-electrolyser-equipment-from-bondalti/",
  "2023-07-17", quantity=(40, "MW"), country="PT", sector="chemicals",
  note="H2 Enable phase one, Estarreja. About EUR 11 million.",
  site="Estarreja",
  firmness="contract", firmness_basis=
  "(July 17, 2023 - Oslo, Norway) Nel Hydrogen Electrolyser AS, a "
  "subsidiary of Nel ASA (Nel, OSE:NEL), has signed a contract for 40 MW of "
  "alkaline electrolyser equipment for about EUR 11 million with Bondalti "
  "for its first phase of the H2 Enable project in Estarreja, Portugal . "
  "\"We continue to experience good momentum for our electrolysers, and we "
  "are happy to partner with a quality company such…")
E("nel", "HyCC", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-hycc-has-cancelled-the-40-mw-purchase-order-due-to-market-conditions/",
  "2023-12-12", quantity=(40, "MW"), country="NL", sector="hydrogen",
  note="CANCELLATION of the 2023-02-06 order. Recorded as an edge so the backlog it "
       "left can be seen leaving.",
  site="H2eron Delfzijl",
  firmness="contract", firmness_basis=
  "The client has postponed its H 2 eron project to being realised in 2028 "
  "at the earliest and has therefore cancelled the purchase order. The "
  "cancellation is in accordance with the initial agreement for this "
  "project where production was communicated to start in Q4 2025.")
E("nel", "an undisclosed customer (a European project)", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-purchase-order-for-electrolyser-equipment/", "2024-07-01",
  quantity=None,
  note="'a follow-on equipment order of more than EUR 7 million for a European project'. "
       "Neither customer nor capacity stated.",
  firmness="contract", firmness_basis=
  "(July 1, 2024 - Oslo, Norway) A subsidiary of Nel ASA (Nel, OSE:NEL), "
  "has received a follow-on equipment order of more than EUR 7 million for "
  "a European project.")
E("nel", "Alperia Greenpower SRL", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-from-alperia-greenpower-srl-for-hydrogen-fueling-"
      "equipment-in-italy/", "2024-05-30", quantity=(1, "hydrogen fuelling site"),
  country="IT", sector="utility / hydrogen refuelling",
  note="Placed with a Cavendish Hydrogen ASA subsidiary, itself then a Nel subsidiary.",
  firmness="contract", firmness_basis=
  "(Oslo, 30 May 2024) A subsidiary of Cavendish Hydrogen ASA, itself a "
  "subsidiary of Nel ASA (Nel, OSE: NEL) has received a purchase order from "
  "Alperia Greenpower SRL for hydrogen fueling equipment for one site to be "
  "used for light- and heavy-duty fuel cell electric vehicles in Bruneck, "
  "South Tyrol, Italy. “We are pleased to be chosen by Alperia to be the "
  "supplier of their first hydrogen fueling…")
E("nel", "Aberdeen Hydrogen Hub", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-receives-purchase-order-for-one-mc500-containerized-pem-electrolyser/",
  "2025-03-20", quantity=(2.5, "MW"), country="GB", sector="hydrogen",
  note="One MC500 for the Aberdeen Hydrogen Hub, north-east Scotland. Announced by "
       "Nel Hydrogen US, which is where the order was booked and not where it lands.",
  site="Aberdeen Hydrogen Hub",
  firmness="contract", firmness_basis=
  "(March 20, 2025 - Oslo, Norway) Nel Hydrogen US, a subsidiary of Nel ASA "
  "(Nel, OSE:NEL), has received a purchase order for one 2.5 MW "
  "containerized PEM unit for the Aberdeen Hydrogen Hub project in the "
  "north-east of Scotland.")
E("nel", "Statkraft", "equipment_order", "supplier", "supplier_press",
  N + "nel-asa-statkraft-has-cancelled-the-40-mw-alkaline-electrolyser-contract/",
  "2025-04-30", quantity=(40, "MW"), country="NO", sector="hydrogen",
  note="CANCELLATION, and the document that names the 2022-11-14 'undisclosed North "
       "European client' as Statkraft.",
  firmness="contract", firmness_basis=
  "(April 30, 2025 - Oslo, Norway) Reference made to the announcements "
  "published November 14, 2022, and January 6, 2023, where Nel Hydrogen "
  "Electrolyser AS, a subsidiary of Nel ASA (Nel, OSE:NEL), signed a 40 MW "
  "contract with Statkraft.")
E("nel", "H2 Energy (for Verein für Abfallentsorgung, Buchs)", "equipment_order",
  "supplier", "supplier_press",
  N + "nel-asa-receives-its-third-purchase-order-for-a-containerized-pem-solution-from-"
      "h2-energy/", "2025-10-07", quantity=(2.5, "MW"), country="CH",
  sector="waste management / hydrogen refuelling",
  note="Ordered by H2 Energy, delivered to VfA Buchs, Switzerland. Two parties, one "
       "order; the customer as stated is the one that placed it.",
  firmness="contract", firmness_basis=
  "(October 7 , 2025 - Oslo, Norway) Nel Hydrogen US, a subsidiary of Nel "
  "ASA (Nel, OSE:NEL), has received a firm purchase order from H2 Energy "
  "for one MC500, a containerized 2.5 MW PEM electrolyser.")
E("nel", "Kaupanes Hydrogen AS and HyFuel AS", "equipment_order", "supplier",
  "supplier_press",
  N + "nel-asa-receives-pem-purchase-order-from-the-hyfuel-and-kaupanes-hydrogen-projects-"
      "valued-at-more-than-usd-50-million/", "2025-11-05", quantity=None, country="NO",
  sector="hydrogen", note="More than USD 50 million; developed by Hydrogen Solutions AS "
                          "(HYDS). No MW figure in the release.",
  site="Kaupanes HyFuel",
  firmness="contract", firmness_basis=
  "(November 5, 2025 - Oslo, Norway) Nel Hydrogen US, a subsidiary of Nel "
  "ASA (Nel, OSE:NEL), has received a firm purchase order from Kaupanes "
  "Hydrogen AS and HyFuel AS in Norway.")

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
                           "announced in due course'.",
  firmness="contract", firmness_basis=
  "ITM Power (AIM: ITM), the energy storage and clean fuel company, is "
  "pleased to announce it has signed an agreement to supply an 8MW "
  "electrolyser in the UK.")
E("itm-power", "BOC", "equipment_order", "supplier", "supplier_press",
  I + "first-project-to-deliver-a-10mw-electrolyser-to-glasgow-facility", "2020-09-16",
  quantity=(10, "MW"), country="GB", sector="industrial gases",
  note="Operated by BOC with power from ScottishPower Renewables; Glasgow.",
  firmness="intent", firmness_basis=
  "The project and the 10MW electrolyser is subject to an MoU at this stage "
  "and ITM Power will make a further announcement regarding the final "
  "details of deployment. “Green Hydrogen for Glasgow is an important step "
  "forward for the city’s net-zero targets and enables Scotland to "
  "demonstrate that its most densely populated urban areas can fully "
  "utilise its abundant local renewable energy resources…")
E("itm-power", "Linde", "equipment_order", "supplier", "supplier_press",
  I + "sale-to-linde-of-world-s-largest-pem-electrolyser", "2021-01-13",
  quantity=(24, "MW"), country="DE", sector="industrial gases",
  note="For the Leuna Chemical Complex, Germany. Linde is itself a node on this "
       "perimeter (capture_technology) and here is the buyer — the same firm appears "
       "on both sides of the sweep, which is the finding, not a clash.",
  site="Leuna Chemical Complex",
  firmness="contract", firmness_basis=
  "Andreas Rupieper, MD ILE GmbH said: “ITM Linde Electrolysis GmbH is "
  "delighted to have received this order for the world’s largest PEM "
  "electrolyser from Linde plc.")
E("itm-power", "an undisclosed customer", "equipment_order", "supplier",
  "supplier_press", I + "12mw-electrolyser-sale", "2021-11-15", quantity=(12, "MW"),
  note="'The customer and location remain confidential due to commercial sensitivities.'",
  firmness="contract", firmness_basis=
  "The customer and location remain confidential due to commercial "
  "sensitivities.")
E("itm-power", "Linde Engineering (for Yara Norge AS)", "equipment_order", "supplier",
  "supplier_press", I + "24mw-sale-to-yara", "2022-01-28", quantity=(24, "MW"),
  country="NO", sector="fertiliser",
  note="Sold to Linde Engineering, installed at Yara's Herøya site outside Porsgrunn. "
       "Two parties again; the buyer is Linde Engineering and the site is Yara's.",
  site="Herøya Porsgrunn",
  firmness="contract", firmness_basis=
  "**ITM Power PLC** (“ITM Power” or the “Company”) **24 MW Sale for "
  "Ammonia Production** ITM Power (AIM: ITM), the energy storage and clean "
  "fuel company, is pleased to provide details of the sale of a 24MW "
  "electrolyser to Linde Engineering contained in the Company’s Half Year "
  "Report issued yesterday.")
E("itm-power", "Linde Engineering (for RWE, Lingen)", "equipment_order", "supplier",
  "supplier_press", I + "two-100-mw-electrolyser-contracts-signed", "2023-01-31",
  quantity=(200, "MW"), country="DE", sector="power / hydrogen",
  note="TWO contracts of 100 MW each; recorded as one edge of 200 MW because the "
       "release states them as one signing. GET H2 Nukleus.",
  firmness="contract", firmness_basis=
  "ITM Power has signed two contracts, each for the sale of 100 MW of PEM "
  "electrolysers to Linde Engineering.")
E("itm-power", "an undisclosed customer (a 100MW project in Germany)", "equipment_order",
  "supplier", "supplier_press",
  I + "itm-power-contract-award-towards-100mw-project-in-germany", "2023-07-17",
  quantity=(100, "MW"),
  note="Long-lead materials and MEP30 skids only, not the whole plant. 'the third "
       "100MW project we are entrusted to execute'.",
  firmness="contract", firmness_basis=
  "ITM is delighted to announce the award of a contract for the procurement "
  "of long lead-time materials and components required for the "
  "manufacturing of our state-of-the-art MEP30 skids for a 100MW project in "
  "Germany. The Final Investment Decision (FID) is aimed to be taken by our "
  "customer in 2023. Dennis Schulz, CEO, said: “This order is an important "
  "endorsement of our technology and capability…")
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
  note="Following Shell's FID; Linde Engineering is the EPC integrator.",
  site="Shell Energy and Chemicals Park Rheinland Wesseling",
  firmness="contract", firmness_basis=
  "We are pleased to announce that we have signed a contract for the "
  "REFHYNE II project, following Shell's recent positive Final Investment "
  "Decision (FID).")
E("itm-power", "Guttroff GmbH", "equipment_order", "supplier", "supplier_press",
  I + "first-contract-signed-for-neptune-v", "2024-11-08", quantity=(5, "MW"),
  country="DE", sector="industrial gases", note="One NEPTUNE V unit, 5 MW.",
  firmness="contract", firmness_basis=
  "ITM Power is pleased to announce that we have signed our first contract "
  "to sell a NEPTUNE V unit to Guttroff GmbH, a private German company that "
  "provides solutions for technical and medical gases, welding supplies, "
  "and engineering and which celebrates its 100th company anniversary in "
  "2025. Launched in May this year and ideally suited for mid-sized "
  "projects, NEPTUNE V utilises ITM's leading and…")
E("itm-power", "an undisclosed green hydrogen plant developer", "framework_agreement",
  "supplier", "supplier_press", I + "50mw-feed-contract-signed", "2024-12-20",
  quantity=(50, "MW"), note="FEED for a 50MW site 'in the European Union'; ten NEPTUNE "
                            "V units; FID expected 2025.")
E("itm-power", "an undisclosed customer (three German refuelling projects)",
  "equipment_order", "supplier", "supplier_press", I + "contract-for-three-neptune-v",
  "2024-12-23", quantity=(15, "MW"),
  note="Three NEPTUNE V units at 5 MW, into three individual projects supplying "
       "refuelling stations in Germany.",
  firmness="contract", firmness_basis=
  "ITM have signed a contract to supply three NEPTUNE V units, totalling "
  "15MW, to a family-owned private German company. Launched in May this "
  "year, NEPTUNE V is ideally suited for mid-sized projects.")
E("itm-power", "a European energy company", "framework_agreement", "supplier",
  "supplier_press", I + "feed-contract-signed", "2025-01-24", quantity=(10, "MW"),
  note="A standard 10MW design the customer intends to deploy in several UK projects. "
       "One design, several sites, none named.")
E("itm-power", "La Française de l'Energie SA (FDE)", "equipment_order", "supplier",
  "supplier_press", I + "contract-for-four-neptune-v", "2025-02-13", quantity=(20, "MW"),
  country="FR", sector="energy", note="Four NEPTUNE V units totalling 20MW.",
  firmness="contract", firmness_basis=
  "ITM Power is pleased to announce that we have signed a contract to "
  "supply four NEPTUNE V units, totalling 20MW, to La Française de "
  "l’Energie SA (FDE), an independent multi-energy producer. NEPTUNE V is "
  "our full-scope 5MW containerised green hydrogen plant, which utilises "
  "ITM’s leading and proven TRIDENT stack technology.")
E("itm-power", "EDF Renewables UK and Hynamics", "equipment_order", "supplier",
  "supplier_press", I + "engineering-integration-package-for-hynamics", "2025-03-27",
  quantity=(8, "MW"), country="GB", sector="energy",
  note="Plant integration engineering package for Tees Green Hydrogen phase 1; four "
       "NEPTUNE II units, and the release names this as the 2024-07-16 reservation.",
  site="Tees Green Hydrogen",
  firmness="framework", firmness_basis=
  "Today’s announcement is related to the capacity reservation, and the "
  "engineering package will cover the integration of four NEPTUNE II units "
  "with the balance of plant. The project will boost local industry and "
  "transport by supplying green hydrogen to support decarbonisation efforts "
  "and significantly reduce industrial pollution, securing its long-term "
  "sustainability. Dennis Schulz, CEO, said:…")
E("itm-power", "Deutsche Bahn AG", "framework_agreement", "supplier", "supplier_press",
  I + "itm-and-deutsche-bahn-forge-partnership-for-sustainable-transportation-and-infrastructure", "2025-03-31",
  quantity=None, country="DE", sector="rail")
E("itm-power", "Westnetz GmbH", "equipment_order", "supplier", "supplier_press",
  I + "sale-of-neptune-v", "2025-05-06", quantity=(5, "MW"), country="DE",
  sector="gas and electricity distribution", note="Dortmund-based DSO. One NEPTUNE V.",
  firmness="contract", firmness_basis=
  "ITM Power is pleased to announce that we have signed a contract to "
  "supply a NEPTUNE V unit to Westnetz GmbH, a Dortmund-based German "
  "distribution system operator for electricity and gas. Westnetz will "
  "integrate the NEPTUNE V unit for their customer, a public transport "
  "operator and subsidiary of a German utility company.")
E("itm-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  I + "selected-by-uniper-for-120mw-green-hydrogen-project", "2025-05-08",
  quantity=(120, "MW"), country="GB", sector="power",
  note="Selection, not a contract: Humber H2ub (Green), six 20MW POSEIDON modules, "
       "shortlisted in HAR2.",
  site="Humber H2ub")
E("itm-power", "a leading Spanish cement producer", "equipment_order", "supplier",
  "supplier_press", I + "sale-of-neptune-ii", "2025-05-09", quantity=(2, "MW"),
  country="ES", sector="cement",
  note="ITM's FIRST system into the cement industry, hydrogen co-fired with natural gas "
       "in the kiln. The producer is not named, so it matches no row and cannot be "
       "made into one; a cement edge with an anonymous cement customer is exactly the "
       "shape the register cannot yet hold.",
  firmness="contract", firmness_basis=
  "ITM Power have signed a contract to supply a NEPTUNE II unit to a "
  "Spanish cement producer. ITM Power is pleased to announce that we have "
  "signed a contract to supply a NEPTUNE II unit to a leading Spanish "
  "cement producer. NEPTUNE II is our fully autonomous 2MW electrolyser "
  "system.")
E("itm-power", "an undisclosed customer (a UK HAR2 project and a smaller UK project)",
  "framework_agreement", "supplier", "supplier_press", I + "selected-for-two-uk-projects",
  "2025-06-17", quantity=None,
  note="Preferred supplier on two UK projects, both pre-FID. The 2025-08-13 MorGen "
       "release confirms one of the two is West Wales Hydrogen.")
E("itm-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  I + "feed-contract-for-uniper's-120mw-green-hydrogen-project", "2025-06-23",
  quantity=(120, "MW"), country="GB", sector="power",
  note="FEED contract following the 8 May selection. Still subject to FID.",
  site="Humber H2ub")
E("itm-power", "MorGen Energy", "equipment_order", "supplier", "supplier_press",
  I + "20mw-supply-agreement-signed", "2025-08-13", quantity=(20, "MW"), country="GB",
  sector="hydrogen", note="West Wales Hydrogen, Milford Haven; HAR1. Supply agreement "
                          "and binding heads of terms.",
  site="West Wales Hydrogen Milford Haven",
  firmness="contract", firmness_basis=
  "ITM Power have signed a supply agreement and binding heads of terms for "
  "a long-term services agreement with MorGen Energy for the 20MW West "
  "Wales Hydrogen project. ITM Power is delighted to announce the signing "
  "of a supply agreement and binding heads of terms for a long-term "
  "services agreement with MorGen Energy for the 20MW West Wales Hydrogen "
  "project in Milford Haven, UK.")
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
       "2028). 710 MW is the sum the release states, and 680 of it is a 2028 decision.",
  site="Netzbrücke 410 Rüstringen")
E("itm-power", "a project managed by Octopus Energy Generation (Kimberly-Clark "
  "Northfleet)", "equipment_order", "supplier", "supplier_press",
  I + "12.5-mw-contract-with-octopus-energy-generation", "2025-12-18",
  quantity=(12.5, "MW"), country="GB", sector="paper / consumer products",
  note="NEPTUNE V systems at Kimberly-Clark's Northfleet plant, Gravesend, Kent.",
  site="Kimberly-Clark Northfleet Gravesend",
  firmness="contract", firmness_basis=
  "ITM Power have signed a contract with a project managed by Octopus "
  "Energy Generation to deploy its NEPTUNE V systems at Kimberly-Clark’s "
  "Northfleet manufacturing plant in Gravesend. ITM Power is delighted to "
  "announce the signing of a contract with a project managed by Octopus "
  "Energy Generation to deploy its NEPTUNE V containerised green hydrogen "
  "systems at Kimberly-Clark’s Northfleet…")
E("itm-power", "MorGen Energy", "equipment_order", "supplier", "supplier_press",
  I + "morgen-energy-20-mw-project-fid-and-ltsa-signed", "2026-03-11",
  quantity=(20, "MW"), country="GB", sector="hydrogen",
  note="FID and long-term services agreement on the 2025-08-13 supply agreement.",
  site="West Wales Hydrogen Milford Haven",
  firmness="contract", firmness_basis=
  "We can now confirm that the 20 MW Notice to Proceed (NtP) announced in "
  "February relates to MorGen Energy’s West Wales Hydrogen project in "
  "Milford Haven, which has reached Final Investment Decision (FID).")
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
       "MW, third document.",
  firmness="contract", firmness_basis=
  "In total, ITM Power and Linde Engineering are delivering two 100 MW "
  "plants to RWE in Lingen. As part of the ongoing commissioning process, "
  "green hydrogen has been successfully produced and transported via "
  "approximately 120 km of hydrogen pipeline infrastructure for usage at "
  "Evonik’s chemical park in Marl.")

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
       "thyssenkrupp Uhde Chlorine Engineers, the node's former name.",
  site="Holland Hydrogen I Tweede Maasvlakte Rotterdam",
  firmness="contract", firmness_basis=
  "thyssenkrupp Uhde Chlorine Engineers has signed a supply contract with "
  "Shell for the large-scale project ‘Hydrogen Holland I’ in the port of "
  "Rotterdam, the Netherlands.")
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
       "the alias index matches on 'Boden'.",
  site="Boden",
  firmness="contract", firmness_basis=
  "In realizing this ambitious climate-friendly project, H2 Green Steel has "
  "chosen an industrial partner with a proven history in chlor-alkali and "
  "various other projects under contract with a similar or even larger "
  "production capacity in alkaline water electrolysis.")
E("tk-nucera", "Neste", "framework_agreement", "supplier", "supplier_press",
  K + "thyssenkrupp-nucera-and-neste-sign-agreement-to-reserve-production-capacities-for-"
      "120-mw-water-electrolyser-at-nestes-refinery-in-finland", "2023-10-10",
  quantity=(120, "MW"), country="FI", sector="refining",
  note="Six 20 MW scalum modules for the Porvoo refinery. A reservation agreement, not "
       "an order.",
  site="Porvoo")
E("tk-nucera", "Cepsa", "framework_agreement", "supplier", "supplier_press",
  K + "cepsa-selects-thyssenkrupp-nucera-as-preferred-supplier-of-a300-mw-electrolyzer-"
      "for-green-hydrogen-plant-in-spain", "2024-05-13", quantity=(300, "MW"),
  country="ES", sector="refining / energy",
  note="Preferred supplier plus a basic engineering design package through to FID; "
       "15 scalum units. Cepsa is now Moeve — see the 2026-03-18 edge.",
  site="Andalusian Green Hydrogen Valley Huelva")
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
       "two years and a company rename later.",
  site="Onuba La Rábida Huelva",
  firmness="contract", firmness_basis=
  "Madrid / Dortmund, March 18, 2026 – thyssenkrupp nucera and Moeve have "
  "signed an engineering, procurement, fabrication and supply contract for "
  "thyssenkrupp nucera to provide its equipment for 300 megawatts (MW) of "
  "its alkaline water electrolysis technology.")
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
                                         "and Circle K. Three full PEM arrays.",
  site="Kassø Aabenraa",
  firmness="contract", firmness_basis=
  "Siemens Energy will design, supply and commission the electrolysis "
  "system consisting of three full arrays of its latest and most powerful "
  "line of PEM (proton exchange membrane) electrolysis products including "
  "transformers, rectifiers, distributed control system (DCS) plus the "
  "equipment to produce demineralized water.")
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
       "same firm in three roles in one sweep.",
  firmness="contract", firmness_basis=
  "Siemens Energy is supplying 12 electrolyzers with a total capacity of "
  "200 megawatts to Normandy, France.")
E("siemens-energy", "EWE", "equipment_order", "supplier", "supplier_press",
  G + "siemens-energy-wins-contract-for-large-scale-hydrogen-project-fr.html",
  "2024-07-25", quantity=(280, "MW"), country="DE", sector="utility",
  note="Emden, part of Clean Hydrogen Coastline; operation expected 2027, up to 26,000 "
       "t/yr. A ten-year service contract was agreed alongside.",
  site="Emden Clean Hydrogen Coastline",
  firmness="contract", firmness_basis=
  "Siemens Energy has been awarded a contract to supply a 280-megawatt "
  "electrolysis system by German utility EWE.")

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
       "is not ambiguous to a reader. The 2021-07-14 release names SALCOS explicitly.",
  firmness="contract", firmness_basis=
  "August 25, 2020: GrInHy2.0: Sunfire delivers the world’s largest High-"
  "Temperatur Electrolyzer to Salzgitter Flachstahl:")
E("sunfire", "TotalEnergies", "equipment_order", "supplier", "supplier_press",
  F + "totalenergies-sunfire-and-fraunhofer-give-the-go-ahead-for-green-methanol-in-leuna/",
  "2021-06-15", quantity=(1, "MW"), country="FR", sector="refining",
  note="e-CO2Met at Leuna; 1 MW high-temperature electrolyser.",
  site="Leuna e-CO2Met",
  firmness="contract", firmness_basis=
  "A core piece of e-CO2Met is the 1 MW high-temperature electrolyser from "
  "the Dresden-based electrolysis company Sunfire.")
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
                             "2022-03-28 first-hydrogen release.",
  firmness="contract", firmness_basis=
  "The Demo4Grid project partners have reached one of the project’s most "
  "important milestones: This month, a 3.2 MW pressurized alkaline "
  "electrolyzer has been successfully installed at MPREIS’ food production "
  "center in Völs, Austria.")
E("sunfire", "P2X Solutions", "equipment_order", "supplier", "supplier_press",
  F + "finlands-first-green-hydrogen-production-plant-will-run-on-sunfires-electrolysis-"
      "technology/", "2022-03-22", quantity=(20, "MW"), country="FI", sector="hydrogen",
  note="Harjavalta; Finland's first industrial green hydrogen plant.",
  site="Harjavalta",
  firmness="contract", firmness_basis=
  "The electrolysis technology for producing the green hydrogen will be "
  "manufactured and delivered by Sunfire – one of the world’s leading "
  "electrolysis companies.")
E("sunfire", "RWE", "equipment_order", "supplier", "supplier_press",
  F + "rwe-realizes-electrolysis-project-with-sunfire/", "2022-05-03", quantity=(10, "MW"),
  country="DE", sector="power", note="Pressurized alkaline; the Lingen site.",
  site="Lingen",
  firmness="contract", firmness_basis=
  "As part of its hydrogen strategy, RWE has ordered a 10 MW pressurized "
  "alkaline electrolyzer from Sunfire.")
E("sunfire", "Neste", "equipment_order", "supplier", "supplier_press",
  F + "worlds-largest-high-temperature-electrolysis-module-deliveries-started/",
  "2022-07-05", quantity=(2.6, "MW"), country="NL", sector="refining",
  note="MultiPLHY, Neste's Rotterdam refinery. EU-funded under Clean Hydrogen "
       "Partnership grant 875123.",
  site="MultiPLHY Neste Rotterdam refinery",
  firmness="contract", firmness_basis=
  "As part of the MultiPLHY project, Sunfire is installing the world’s "
  "first multi-megawatt high-temperature electrolyzer to produce green "
  "hydrogen at Neste’s renewable products refinery in Rotterdam.")
E("sunfire", "Uniper", "equipment_order", "supplier", "supplier_press",
  F + "bad-lauchstaedt-uniper-orders-sunfire-electrolyzer/", "2022-08-04",
  quantity=(30, "MW"), country="DE", sector="utility",
  note="Bad Lauchstädt Energy Park, Central German Chemical Triangle.",
  site="Bad Lauchstädt Energy Park",
  firmness="contract", firmness_basis=
  "Uniper has ordered a 30 MW pressurized alkaline electrolyzer from the "
  "Dresden-based electrolysis company Sunfire.")
E("sunfire", "Vitesco Technologies", "framework_agreement", "supplier", "supplier_press",
  F + "sunfire-and-vitesco-technologies-become-strategic-partners/", "2023-01-12",
  quantity=None, country="DE", sector="automotive components",
  note="Strategic partnership on electrolyser component manufacture — Vitesco is a "
       "supplier INTO Sunfire here, not a customer. Recorded and flagged; the ruling on "
       "direction is the reader's, and this one plainly runs the other way.")
E("sunfire", "Uniper (Project Air)", "equipment_order", "supplier", "supplier_press",
  F + "project-air-in-sweden-uniper-commissions-sunfire-to-build-a-30-mw-electrolyzer/",
  "2023-01-31", quantity=(30, "MW"), country="SE", sector="chemicals",
  note="Stenungsund, Sweden; Project Air, with Perstorp as the site owner.",
  site="Stenungsund Project Air",
  firmness="contract", firmness_basis=
  "Uniper has commissioned the Dresden-based company Sunfire to build a 30 "
  "MW pressurized alkaline electrolysis plant which will generate green "
  "hydrogen using renewable electricity and purified wastewater.")
E("sunfire", "a leading refinery in Europe", "equipment_order", "supplier",
  "supplier_press",
  F + "sunfire-receives-purchase-order-for-100-mw-pressurized-alkaline-electrolyzer/",
  "2023-08-24", quantity=(100, "MW"),
  note="Ten 10 MW modules. Sunfire's first commercial 100 MW order; the customer is "
       "described only as 'a leading refinery in Europe'.",
  firmness="contract", firmness_basis=
  "Sunfire, a leading electrolysis manufacturer, has secured a contract to "
  "supply a 100 MW pressurized alkaline electrolyzer to a European "
  "refinery. Earlier this year, the company launched its scaling strategy "
  "with the official opening of its industrial serial electrolyzer "
  "production in Solingen, Germany. “Now we are ready to deliver on large "
  "scale projects,” said Sunfire CEO Nils Aldag.")
E("sunfire", "an undisclosed customer (a 500 MW European project)", "framework_agreement",
  "supplier", "supplier_press",
  F + "sunfire-conducts-feed-study-for-500-mw-green-hydrogen-project/", "2024-04-18",
  quantity=(500, "MW"),
  note="FEED study for a 500 MW pressurized alkaline plant, operation targeted 2028; "
       "hydrogen for refinery operations and ammonia.")
E("sunfire", "RWE", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-builds-100-megawatt-electrolyzer-for-rwe/", "2024-09-11",
  quantity=(100, "MW"), country="DE", sector="power", note="RWE's Lingen site.",
  site="Lingen",
  firmness="contract", firmness_basis=
  "Sunfire, a leading global electrolysis company, has been awarded a major "
  "contract for a 100 megawatt (MW) pressurized alkaline electrolyzer at "
  "RWE’s hydrogen site in Lingen.")
E("sunfire", "Ren-Gas", "equipment_order", "supplier", "supplier_press",
  F + "ren-gas-selects-sunfire-electrolyzer-for-its-tampere-e-methane-plant/",
  "2024-11-19", quantity=(50, "MW"), country="FI", sector="e-methane",
  site="Tampere",
  firmness="contract", firmness_basis=
  "Sunfire will deliver 50 megawatt (MW) electrolyzer capacity for Ren-"
  "Gas’s e-methane plant in Tampere, Finland.")
E("sunfire", "Basque Hydrogen (Petronor / Repsol, Enagás Renovable, Ente Vasco de la "
  "Energía)", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-enters-spanish-market-with-new-electrolysis-project/", "2025-04-09",
  quantity=(10, "MW"), country="ES", sector="refining",
  site="port of Bilbao",
  firmness="contract", firmness_basis=
  "Dresden / Bilbao, April 09, 2025 – Sunfire, a leading global "
  "electrolysis company, is delivering a 10 megawatt electrolyzer at the "
  "port of Bilbao to Basque Hydrogen, a consortium led by Petronor – a "
  "subsidiary of Repsol – in collaboration with Enagás Renovable, a "
  "pioneering company in the development of renewable gas production "
  "projects, and the Ente Vasco de la Energía, the energy agency of…")
E("sunfire", "Neste", "equipment_order", "supplier", "supplier_press",
  F + "worlds-largest-soec-electrolyzer-startet-up-at-nestes-rotterdam-refinery/",
  "2025-10-06", quantity=(2.6, "MW"), country="NL", sector="refining",
  note="START-UP of the 2022-07-05 delivery, twelve SOEC modules. Same plant, second "
       "document.",
  site="MultiPLHY Neste Rotterdam refinery",
  firmness="contract", firmness_basis=
  "It consists of twelve electrolysis modules, which together make up the "
  "world’s largest high-temperature electrolyzer (2.6 MW) installed in an "
  "industrial environment.")
E("sunfire", "P2X Solutions", "framework_agreement", "supplier", "supplier_press",
  F + "p2x-solutions-and-sunfire-expand-partnership-with-new-hydrogen-project/",
  "2025-10-08", quantity=(40, "MW"), country="FI", sector="hydrogen",
  note="FEED study for a 40 MW project at Joensuu.",
  site="Joensuu")
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
       "modules each, commissioning 2029, up to 15,000 t H2/yr each.",
  site="Cartagena Muskiz",
  firmness="contract", firmness_basis=
  "Dresden, January 27, 2026 – Sunfire, a leading global electrolysis "
  "company, will supply two 100 megawatt (MW) electrolyzers for renewable "
  "hydrogen projects in Spain.")
E("sunfire", "Nordic Ren-Gas", "framework_agreement", "supplier", "supplier_press",
  F + "nordic-ren-gas-announces-partnership-agreement-with-sunfire/", "2026-07-22",
  quantity=None, country="FI", sector="e-methane")
E("sunfire", "BASF", "equipment_order", "supplier", "supplier_press",
  F + "sunfire-to-build-electrolysis-test-facility-at-basf-site-in-schwarzheide/",
  "2026-05-11", quantity=None, country="DE", sector="chemicals",
  note="An SOEC TEST facility at BASF's Schwarzheide site under the H2Giga flagship. "
       "A test rig is not plant demand and is recorded with no quantity.",
  site="Schwarzheide",
  firmness="contract", firmness_basis=
  "Sunfire to Build Electrolysis Test Facility at BASF Site in Schwarzheide")

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
       "Denmark; up to 100,000 t/yr of hydrogen for northern European transport.",
  firmness="contract", firmness_basis=
  "In May 2022, Plug secured the world’s largest electrolyzer order to date "
  "with H2 Energy Europe . \\n")
E("plug-power", "Lhyfe", "equipment_order", "supplier", "supplier_press",
  PF(2022), "2022-09-08", quantity=(50, "MW"), country="FR", sector="hydrogen",
  note="Ten 5 MW European-manufactured PEM systems; 'Plug's largest multi-site "
       "electrolyzer order in Europe'.",
  firmness="intent", firmness_basis=
  "Lhyfe and Plug, having initiated a strategic relationship in October "
  "2021, have also executed an MoU to jointly develop 300 megawatts of "
  "green hydrogen plants across Europe by 2025.")
E("plug-power", "Uniper", "framework_agreement", "supplier", "supplier_press",
  PF(2023), "2023-03-07", quantity=(100, "MW"), country="NL", sector="utility",
  note="Selected to DESIGN the 100 MW electrolyser package for H2Maasvlakte at the Port "
       "of Rotterdam. A design selection, not a supply order.",
  site="H2Maasvlakte Maasvlakte Rotterdam")
E("plug-power", "Ardagh Glass Limmared AB", "equipment_order", "supplier",
  "supplier_press", PF(2023), "2023-05-22", quantity=(5, "MW"), country="SE",
  sector="glass packaging",
  note="One of three deals in one release. East of Gothenburg; 2.1 t/day of hydrogen "
       "replacing part of the natural gas at the works. First industrial-scale green "
       "hydrogen in glass manufacture.",
  site="Limmared",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a leading provider of turnkey hydrogen solutions for the "
  "global green hydrogen economy, landed three five megawatt (MW) "
  "electrolyzer projects with Ardagh Glass Limmared AB, Hydro Havrand, and "
  "the APEX Group for the first-ever use of industrial-scale green hydrogen "
  "in glass manufacturing, aluminum recycling, and steel manufacturing "
  "processes.")
E("plug-power", "Hydro Havrand", "equipment_order", "supplier", "supplier_press",
  PF(2023), "2023-05-22", quantity=(5, "MW"), country="NO", sector="aluminium recycling",
  note="A unit of Norsk Hydro ASA. Second of the three deals in the 22 May release.",
  firmness="contract", firmness_basis=
  "To build a close-loop circular economy for its aluminum recycling plant "
  "in Hoyanger, Norway, Hydro will employ a 5MW Plug electrolyzer module by "
  "June 2024.")
E("plug-power", "APEX Group", "equipment_order", "supplier", "supplier_press",
  PF(2023), "2023-05-22", quantity=(5, "MW"), country="DE", sector="steel",
  note="Third of the three. The release names steel manufacturing as the application. "
       "A STEEL customer of an electrolyser OEM that matches no row in the register's "
       "steel perimeter — the same shape as Nel/Ovako.",
  firmness="contract", firmness_basis=
  "Plug will deliver two 5MW electrolyzer modules with a capacity to "
  "produce 4.2 metric TPD of green hydrogen to SWB, the city’s public "
  "utility company, by the end of this year.")
E("plug-power", "an undisclosed customer (an oil refining project in Europe)",
  "equipment_order", "supplier", "supplier_press", PF(2023), "2023-07-13",
  quantity=(100, "MW"),
  note="'the largest announced project in the oil and gas sector in Europe'; ~43 t/day "
       "of hydrogen replacing grey hydrogen in refining. Delivery and installation 2024. "
       "Very likely the Galp Sines project named from 2025 onward, and the sweep does "
       "not assert that, because neither document says so.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the green hydrogen economy, secured an order for 100 megawatts (MW) of "
  "proton exchange membrane (PEM) electrolyzers.")
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
  note="Five 5 MW containerised PEM systems.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the green hydrogen economy, secured an order for 25 megawatts (MW) of "
  "proton exchange membrane (PEM) electrolyzer systems for a customer in "
  "Europe.")
E("plug-power", "Castellón Green Hydrogen S.L. (bp and Iberdrola joint venture)",
  "equipment_order", "supplier", "supplier_press", PF(2024), "2024-09-18",
  quantity=(25, "MW"), country="ES", sector="refining",
  note="Five 5 MW units to decarbonise bp's Castellón refinery, Valencia.",
  site="Castellón refinery",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the green hydrogen economy, has secured an order for 25 megawatts (MW) "
  "of proton exchange membrane (PEM) electrolyzer systems from bp and "
  "Iberdrola’s joint venture, Castellón Green Hydrogen S.L.")
E("plug-power", "Galp", "equipment_order", "supplier", "supplier_press",
  PF(2025), "2025-10-01", quantity=(100, "MW"), country="PT", sector="refining",
  note="First 10 MW module delivered of ten for the Sines refinery.",
  site="Sines refinery",
  firmness="contract", firmness_basis=
  "Major Delivery: Delivered the first 10 MW GenEco PEM electrolyzer to "
  "Galp Energia’s Sines project in Portugal, the first phase of a planned "
  "100 MW installation.")
E("plug-power", "Gasunie and STORAG ETZEL (H2CAST)", "equipment_order", "supplier",
  "supplier_press", PF(2025), "2025-10-21", quantity=(44.5, "tonnes of hydrogen"),
  country="DE", sector="gas storage",
  note="A MOLECULE supply, not equipment: 44.5 t of hydrogen delivered for cavern "
       "storage testing, with a new contract for 35 t more. edge_kind equipment_order "
       "is the closest the vocabulary comes and it is wrong in kind — flagged as new "
       "vocabulary pressure in the docket.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the hydrogen economy, today announced the completion of the first phase "
  "of its hydrogen supply delivery of 44.5 metric tons for H2CAST (Hydrogen "
  "Cavern Storage Transition), a joint project led by Gasunie and STORAG "
  "ETZEL in Germany.")
E("plug-power", "H2 Hollandia", "equipment_order", "supplier", "supplier_press",
  PF(2025), "2025-11-05", quantity=(5, "MW"), country="NL", sector="hydrogen",
  note="Plug's first commercial electrolyser deployment in the Netherlands.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the hydrogen economy, today announced it has started installation of its "
  "5 MW electrolyzer for the H2 Hollandia project, the first decentralized "
  "green hydrogen hub initiative currently under construction in the "
  "Netherlands.")
E("plug-power", "Carlton Power", "framework_agreement", "supplier", "supplier_press",
  PF(2025), "2025-11-17", quantity=(55, "MW"), country="GB", sector="hydrogen",
  note="Equipment supply and LTSA for three UK projects, SUBJECT TO FID: Barrow-in-"
       "Furness 30 MW (offtake to Kimberly-Clark), Trafford 15 MW, Langage 10 MW. "
       "Kimberly-Clark also appears as ITM Power's Northfleet offtaker — the same "
       "offtaker behind two different electrolyser suppliers.",
  site="Barrow-in-Furness Trafford Langage")
E("plug-power", "Hy2gen", "framework_agreement", "supplier", "supplier_press",
  PF(2025), "2025-12-04", quantity=(5, "MW"), country="FR", sector="e-fuels",
  note="Letter of intent for the Sunrhyse project, Provence-Alpes-Côte d'Azur.")
E("plug-power", "Galp", "equipment_order", "supplier", "supplier_press",
  PF(2026), "2026-01-23", quantity=(100, "MW"), country="PT", sector="refining",
  note="INSTALLATION COMPLETE — all ten arrays at Sines. Same order as 2025-10-01, "
       "third document if the 2023-07-13 anonymous edge is the same project.",
  site="Sines refinery",
  firmness="contract", firmness_basis=
  "All ten 10-megawatt arrays were delivered and installed, and "
  "commissioning is underway.")
E("plug-power", "Hynetwork", "co2_transport", "supplier", "supplier_press",
  PF(2026), "2026-02-04", quantity=(32, "tonnes of hydrogen"), country="NL",
  sector="hydrogen network",
  note="First fill of a 32 km hydrogen pipeline in Rotterdam. NOT CO2 and not "
       "equipment: the vocabulary has no hydrogen_transport value and this edge is "
       "filed under the nearest one, wrongly. Flagged in the docket.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the hydrogen economy, today announced it has completed the first "
  "hydrogen fill of Hynetwork’s 32-kilometer hydrogen pipeline in "
  "Rotterdam, Netherlands supplying 32 tons of RFNBO-certified renewable "
  "green hydrogen and the delivery of a custom unloading infrastructure "
  "required for this first pipeline-purging and filling…")
E("plug-power", "European Energy", "equipment_order", "supplier", "supplier_press",
  PF(2026), "2026-06-24", quantity=(5, "MW"), country="DK", sector="e-fuels",
  note="Commissioning complete at the Måde Power-to-X facility, Esbjerg. European "
       "Energy is also Siemens Energy's Kassø customer — one owner, two suppliers on "
       "this perimeter.",
  site="Måde Esbjerg",
  refuse_match="The site alias 'Måde' resolves to hoest-ptx-esbjerg, whose plant "
               "field is literally 'Måde, Esbjerg' — but that row's company is "
               "Copenhagen Infrastructure Partners and this release says the facility "
               "is 'developed and operated by European Energy'. One project whose "
               "ownership two speakers state differently, or two plants in one place; "
               "the sweep cannot tell and does not link. Logged as a speaker "
               "disagreement in the docket.",
  firmness="contract", firmness_basis=
  "(NASDAQ: PLUG), a global leader in comprehensive hydrogen solutions for "
  "the hydrogen economy, today announced the completion of a critical "
  "execution phase at the Måde Power-to-X (PtX) facility in Esbjerg, "
  "Denmark, developed and operated by European Energy .")

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
       "the counterparty is a European owner and the ruling on pilots is not mine.",
  firmness="contract", firmness_basis=
  "RWE and its partner John Cockerill are to jointly build a testing "
  "facility in Germany, which will enable to optimize a key stage in the "
  "process of turning household waste into hydrogen.")
E("john-cockerill", "Hyoffwind (Fluxys and Virya Energy) with BESIX",
  "framework_agreement", "supplier", "supplier_press",
  J + "hyoffwind-sassocie-a-john-cockerill-et-besix-pour-la-realisation-dune-"
      "installation-de-production-dhydrogene-vert-a-zeebruges/", "2022-02-15", quantity=None,
  country="BE", sector="gas network / renewables",
  note="Agreement to design and build a green hydrogen production unit at Zeebrugge. "
       "The capacity (25 MW) is stated in the later releases, not this one.",
  site="Zeebrugge")
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
       "two rows and the release names neither site, so project_id is null.",
  firmness="intent", firmness_basis=
  "ArcelorMittal, the world’s leading steel company , and John Cockerill, a "
  "group leading the development of steel processing facilities and "
  "electrolysers , today announce plans to construct the world’s first "
  "industrial-scale low temperature, iron electrolysis plant.")
E("john-cockerill", "SSAB (via ArcelorMittal's JVD licence)", "technology_licence",
  "supplier", "supplier_press", J + "arcelormittal-jvd-technology-swedish-steelmaker-ssab/",
  "2024-06-19", quantity=None, country="SE", sector="steel",
  note="A preparation study to implement ArcelorMittal's JVD strip-coating process in "
       "SSAB's downstream production; John Cockerill is the exclusive commercialiser. "
       "Strip coating, not ironmaking — recorded because the counterparty is a European "
       "steelmaker and the exclusion would be a judgement about what counts.",
  firmness="intent", firmness_basis=
  "With the intended implementation of ArcelorMittal’s novel JVD® (Jet "
  "Vapor Deposition) steel strip coating technology in Swedish steelmaker "
  "SSAB’s steel production, the collaboration between ArcelorMittal and "
  "John Cockerill makes a major leap forward in the deployment of this "
  "innovative technology providing a multitude of advantages. In a first "
  "step, John Cockerill will be conducting a…")
E("john-cockerill", "Virya Energy, HyoffGreen and Messer (Hyoffwind)", "equipment_order",
  "supplier", "supplier_press",
  J + "hyoffwind-25mw-green-hydrogen-production-plant-in-belgium-with-besix/", "2024-07-25", quantity=(25, "MW"), country="BE",
  sector="renewables / industrial gases",
  note="Financial close on Belgium's first renewable hydrogen production plant, "
       "Zeebrugge. Messer appears here as an owner and at Siemens Energy as a customer.",
  site="Zeebrugge",
  firmness="contract", firmness_basis=
  "Selected as technology partners for the design and the construction of "
  "the facility, John Cockerill Hydrogen, BESIX and BESIX Environment thus "
  "received the notice to proceed for the 25MW Hyoffwind project. This "
  "milestone agreement comes after the grant of the Environment and "
  "Construction permit, and the signature of the Engineering, Procurement, "
  "and Construction (EPC) contract earlier this…")
E("john-cockerill", "Hyoffwind", "equipment_order", "supplier", "supplier_press",
  J + "john-cockerill-has-installed-four-electrolyzers-at-the-hyoffwind-site/",
  "2026-04-29", quantity=(25, "MW"), country="BE", sector="renewables",
  note="INSTALLATION: four electrolysers, 25 MW physically in place. Same plant, third "
       "document.",
  site="Zeebrugge",
  firmness="contract", firmness_basis=
  "What a massive electrolyzer ! And four of them are now installed at "
  "HyOffWind, in the Port of Zeebrugge .")
E("john-cockerill", "an undisclosed customer (a green hydrogen project in the "
  "Netherlands)", "equipment_order", "supplier", "supplier_press",
  J + "hydrogen-electrolyseur-belfort-prod-aspach/", "2026-07-13", quantity=(40, "MW"),
  note="'a new 40 MW production phase is beginning for a green hydrogen project in the "
       "Netherlands'. Customer and site unnamed.",
  firmness="contract", firmness_basis=
  "After producing the cells for a 25 MW green hydrogen plant in Belgium , "
  "the plant is preparing to launch production this summer of eight new "
  "electrolyzers—totaling 40 MW—for a project in the Netherlands. These "
  "achievements illustrate the synergy developed between the Belfort, "
  "Aspach, and Seraing sites.")
E("john-cockerill", "Shell (with Rely)", "framework_agreement", "supplier",
  "supplier_press",
  J + "john-cockerill-rely-shell-evaluated-john-cockerills-alkaline-electrolyzer-"
      "technology/", "2026-05-11", quantity=None, country="GB", sector="oil and gas",
  note="A joint technology evaluation of safety, operability and maintainability. Not "
       "an order; recorded because Shell is a named European counterparty and the "
       "evaluation is a step towards one.")

# =============================================================================
# capture_technology
# =============================================================================

# --- Aker Carbon Capture ASA, and SLB Capturi after it -------------------------
# TWO NODES, AND THE McPHY RULING IS WHY. Fourteen edges below were signed by Aker
# Carbon Capture ASA, a listed Norwegian company; on 14 June 2024 that business
# closed into a joint venture with SLB and on 16 September 2024 the venture took
# the name SLB Capturi. Under DECISION D-11 an edge stays on the node that signed
# it and is INHERITED BY REFERENCE — `inherited_by` on each, with the date — so
# that the speaker survives and no sum counts the same order twice.
#
# WHAT THE TWO DEAD DOMAINS ACTUALLY DO, checked on 11 September 2026 because the
# earlier line here said both fail to resolve and only one of them does:
#   * slbcapturi.com  — NO ADDRESS RECORD AT ALL, and therefore nothing anywhere on
#     slb.com. It is not abandoned: its NS records are dns0/dns1.slb.com and
#     dns0/dns1.slb.net, so SLB holds the domain and publishes no host for it. The
#     live home is capturi.slb.com, which answers 200, and `home` now says so.
#   * akercarboncapture.com — RESOLVES, to 35.187.120.37, and serves nothing: nginx
#     answers 404 over http and the https certificate does not match the name.
#     "Resolves and serves nothing" is a different refusal from "does not resolve"
#     and the node records it as one.
# Releases from 2020 to 2022 — which include the Brevik award itself — are on
# neither and are read from the Internet Archive under DECISION D-7.
Q = "https://capturi.slb.com/resources/news/"
JV = Q + ("2024/slb-and-aker-carbon-capture-announce-closing-of-carbon-capture-"
          "joint-venture")
INTO_SLB = {"node_id": "slb-capturi", "since": "2024-06-14", "source_url": JV}

R_.status_event(
    "aker-carbon-capture", "2024-06-14", "Aker Carbon Capture ASA",
    "carbon capture business transferred into the SLB / Aker Carbon Capture joint "
    "venture", JV, "supplier_press",
    "THE TRANSFER. Aker Carbon Capture's carbon capture business closed into a "
    "joint venture with SLB — SLB 80%, Aker Carbon Capture 20% — and every edge "
    "this node signed is inherited from this date by slb-capturi. Stated by the "
    "acquirer's own newsroom, which is also the only host the seller's releases "
    "survive on.")
R_.status_event(
    "slb-capturi", "2024-06-14", "Aker Carbon Capture ASA", "SLB / Aker Carbon "
    "Capture joint venture", JV, "supplier_press",
    "Closing of the joint venture combining SLB's carbon capture business with Aker "
    "Carbon Capture. SLB 80%, Aker Carbon Capture 20%. The receiving side of the "
    "same event; the fourteen inherited edges stay on aker-carbon-capture.")
R_.status_event(
    "slb-capturi", "2024-09-16", "SLB / Aker Carbon Capture joint venture",
    "SLB Capturi", Q + "2024/introducing-slb-capturi-pioneering-industrial-"
                       "decarbonization", "supplier_press",
    "The joint venture takes the name SLB Capturi. Every release before this date is "
    "signed 'Aker Carbon Capture' and every one after is signed 'SLB Capturi'; they "
    "are one supplier and the edges below say so.")

C("slb-capturi", 7, "carbon capture plants", "backlog", "supplier", "supplier_press",
  Q + "2024/slb-capturi-completes-construction-of-the-worlds-first-industrial-scale-"
      "carbon-capture-plant", "2024-12-02",
  note="'currently delivering seven carbon capture plants to bioenergy, waste to "
       "energy, and cement facilities'. A COUNT OF PLANTS, not a rate and not a "
       "tonnage — this node's capacity cannot be compared with the tonnes on its "
       "edges, and the docket's arithmetic section says so rather than converting.")
C("slb-capturi", 8, "carbon capture plants", "backlog", "supplier", "supplier_press",
  Q + "2026/2026-0728-slb-capturi-uniper", "2026-07-28",
  note="'eight plants in operation or under delivery', nineteen months after seven.")

E("aker-carbon-capture", "Fortum Waste Solutions", "framework_agreement", "supplier",
  "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-test-campaign-and-study-for-fortum-waste-"
      "solutions-in-denmark", "2023-04-19",
  quantity=(170000, "tonnes CO2 per year"), country="DK", sector="waste-to-energy",
  site="Nyborg", note="Test campaign and feasibility study. 'around 170,000 tonnes'.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Ørsted", "equipment_order", "supplier", "supplier_press",
  Q + "2023/aker-carbon-capture-and-oersted-sign-contract-for-delivery-of-five-just-"
      "catch-units", "2023-06-15", quantity=(500000, "tonnes CO2 per year"),
  country="DK", sector="bioenergy", site="Kalundborg Asnæs Avedøre",
  note="Five Just Catch units plus liquefaction, temporary storage and loading; "
       "contract value above EUR 200 million. Asnæs (wood chip) and Avedøre (straw).",
  firmness="contract", firmness_basis=
  "Aker Carbon Capture and Ørsted, a global leader in renewable energy, "
  "have signed the contract to develop a large-scale carbon capture project "
  "for the Ørsted Kalundborg Hub in Denmark.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "a Swedish energy company", "framework_agreement", "supplier",
  "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-pre-feed-in-sweden-covering-more-than-"
      "200,000-tonnes-of-co2-per-year", "2023-10-16", quantity=None,
  note="Pre-FEED for a Just Catch application. Customer not named.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "a major European power company", "framework_agreement", "supplier",
  "supplier_press",
  Q + "2023/aker-carbon-capture-signed-pre-feed-contract-for-several-power-generation-"
      "facilities-in-europe", "2023-10-19", quantity=None,
  note="Pre-FEED across 'a portfolio of power plants in ma[ny countries]'. Neither "
       "the company nor any site is named — a multi-country framework with no "
       "geography at all.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "TES", "framework_agreement", "supplier", "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-study-by-tes-to-capture-400,000-tonnes-co2-"
      "per-year-in-germany", "2023-10-30",
  quantity=(400000, "tonnes CO2 per year"), country="DE", sector="waste-to-energy",
  note="Feasibility study; CO2 to be railed to TES's Wilhelmshaven e-NG plant.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "MAN Energy Solutions", "framework_agreement", "supplier",
  "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-feasibility-study-by-man-energy-solutions",
  "2023-11-15", quantity=None, country="DE", sector="engineering",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Hafslund Oslo Celsio", "framework_agreement", "supplier",
  "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-feed-for-hafslund-oslo-celsios-ccs-project",
  "2023-11-24", quantity=(400000, "tonnes CO2 per year"), country="NO",
  sector="waste-to-energy", site="Klemetsrud Oslo",
  note="Full FEED with Aker Solutions; Just Catch 400.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "an undisclosed customer (an e-fuel project in Finland)",
  "framework_agreement", "supplier", "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-feasibility-study-for-e-fuel-project-in-"
      "finland", "2023-11-29", quantity=None,
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Hafslund Oslo Celsio", "framework_agreement", "supplier",
  "supplier_press", Q + "2023/aker-carbon-capture-signs-feed-contract-with-hafslund-"
                        "oslo-celsio", "2023-12-04",
  quantity=(400000, "tonnes CO2 per year"), country="NO", sector="waste-to-energy",
  site="Klemetsrud Oslo", note="FEED contract signed. Same project, second document.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Uniper", "framework_agreement", "supplier", "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-process-design-package-for-unipers-grain-"
      "power-station-in-the-uk", "2023-12-13", quantity=None, country="GB",
  sector="power", site="Isle of Grain Kent",
  note="Process Design Package for a post-combustion plant on the existing CCGT units.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Limeco", "framework_agreement", "supplier", "supplier_press",
  Q + "2023/aker-carbon-capture-awarded-feasibility-study-by-waste-to-energy-player-"
      "in-switzerland", "2023-12-18", quantity=None, country="CH",
  sector="waste-to-energy", site="Dietikon",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "a European developer", "framework_agreement", "supplier",
  "supplier_press", Q + "2024/aker-carbon-capture-awarded-study-for-waste-to-energy-"
                        "plants-in-northern-europe", "2024-02-22", quantity=None,
  note="Feasibility of carbon capture at multiple biomass and waste-to-energy plants. "
       "Developer not named, sites not named.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "WACKER", "framework_agreement", "supplier", "supplier_press",
  Q + "2024/aker-carbon-capture-awarded-study-and-test-campaign-from-wacker",
  "2024-03-22", quantity=None, country="NO", sector="silicon / chemicals",
  site="Holla Kyrksæterøra",
  note="Feasibility study and an eight-month test campaign on metallurgical-grade "
       "silicon production. WACKER is German; the plant is Norwegian.",
  inherited_by=INTO_SLB)
E("aker-carbon-capture", "Statkraft", "framework_agreement", "supplier", "supplier_press",
  Q + "2024/aker-carbon-capture-awarded-pre-feed-from-statkraft-in-norway",
  "2024-04-01", quantity=(220000, "tonnes CO2 per year"), country="NO",
  sector="waste-to-energy", site="Heimdal Trondheim",
  inherited_by=INTO_SLB)
E("slb-capturi", "Twence", "equipment_order", "supplier", "supplier_press",
  Q + "2024/slb-capturi-completes-construction-of-the-worlds-first-industrial-scale-"
      "carbon-capture-plant", "2024-12-02",
  quantity=(100000, "tonnes CO2 per year"), country="NL", sector="waste-to-energy",
  site="Hengelo", note="Construction complete on the first modular Just Catch 100.",
  firmness="contract", firmness_basis=
  "SLB Capturi completes construction of the worlds first industrial scale "
  "carbon capture plant")
E("slb-capturi", "Twence", "equipment_order", "supplier", "supplier_press",
  Q + "2025/slb-capturi-powers-up-its-first-modular-carbon-capture-plant",
  "2025-01-23", quantity=(100000, "tonnes CO2 per year"), country="NL",
  sector="waste-to-energy", site="Hengelo",
  note="POWERED UP and handed over. Same plant, second document.",
  firmness="contract", firmness_basis=
  "OSLO, Norway, January 23, 2025 — Global energy technology company SLB "
  "(NYSE: SLB) announced today that SLB Capturi has completed commissioning "
  "and is handing over its modular carbon capture plant at Twence’s waste-"
  "to-energy facility in Hengelo, Netherlands. The new plant has the "
  "capacity to capture up to 100,000 metric tons of CO 2 per year, which "
  "will be used in applications for the…")
E("slb-capturi", "Hafslund Celsio AS", "equipment_order", "supplier", "supplier_press",
  Q + "2025/slb-capturi-and-aker-solutions-win-contract-to-deliver-carbon-capture-"
      "solution-for-hafslund-celsio", "2025-01-27",
  quantity=(350000, "tonnes CO2 per year"), country="NO", sector="waste-to-energy",
  site="Klemetsrud Oslo",
  note="EPCIC. THE DESIGN FIGURE MOVED: the 2023 FEED releases say 400,000 t/yr and "
       "this one says 350,000. Logged as a slip — one speaker, two figures — in the "
       "docket. CO2 goes to Northern Lights, which is a node on this perimeter.",
  firmness="contract", firmness_basis=
  "OSLO, Norway, January 27, 2025 — SLB Capturi, in collaboration with Aker "
  "Solutions, has been awarded an engineering, procurement, construction, "
  "installation and commissioning (EPCIC) contract from Hafslund Celsio AS "
  "to deliver a carbon capture solution at its waste-to-energy facility in "
  "Klemetsrud, Oslo.")
E("slb-capturi", "ACCIONA, Sener and SLB Capturi consortium (for AEB Amsterdam)",
  "framework_agreement", "supplier", "supplier_press",
  Q + "2025/slb-capturi-to-take-part-in-carbon-capture-feed-delivery-to-aeb-amsterdam",
  "2025-04-07", quantity=(550000, "tonnes CO2 per year"), country="NL",
  sector="waste processing", site="Westpoort Amsterdam",
  note="Project Aurora, two-phase design-and-implement contract won on a European "
       "tender. The 550,000 t is the fossil CO2 the two incinerators release, not a "
       "stated capture capacity — recorded with that said here.")
E("slb-capturi", "Heidelberg Materials", "equipment_order", "supplier", "supplier_press",
  Q + "2025/slb-capturi-achieves-first-1000-metric-tons-co2-captured-at-brevik-carbon-"
      "capture-plant", "2025-05-12", quantity=(400000, "tonnes CO2 per year"),
  country="NO", sector="cement", site="Brevik",
  note="Big Catch at Brevik, part of Longship; mechanical completion December 2024, "
       "first 1,000 t captured. THE SUPPLIER SIDE OF brevik-ccs, which the register "
       "holds from the owner's side at the same 400,000 t/yr.",
  firmness="contract", firmness_basis=
  "SLB Capturi achieves first 1,000 metric tons CO2 captured at Brevik "
  "carbon capture plant")
E("slb-capturi", "Uniper", "framework_agreement", "supplier", "supplier_press",
  Q + "2025/slb-capturi-partners-with-worley-and-siemens-energy-for-unipers-low-carbon-"
      "power-project", "2025-03-24", quantity=None, country="GB", sector="power",
  site="Connah's Quay Deeside",
  note="FEED partnership with Worley and Siemens Energy — Siemens Energy is a node on "
       "this perimeter, here as a partner rather than a competitor.")
E("slb-capturi", "Uniper", "technology_licence", "supplier", "supplier_press",
  Q + "2026/2026-0728-slb-capturi-uniper", "2026-07-28", quantity=None, country="GB",
  sector="power", site="Connah's Quay Deeside",
  note="Selected as preferred carbon capture technology licensor after a FEED that "
       "began in December 2024. Plant 'multi-million-tonnes-per-annum'; no figure.",
  firmness="intent", firmness_basis=
  "SLB Capturi™ has been selected as the preferred carbon capture "
  "technology licensor for Uniper’s proposed Connah’s Quay Low Carbon Power "
  "(CQLCP) project in Deeside, United Kingdom.")

# --- Mitsubishi Heavy Industries, Ltd. ----------------------------------------
# The corporate sitemap lists 6,334 /news/ URLs whose slugs are dates and carry no
# words, so no filter can be applied to them. The year index pages DO carry titles:
# mhi.com/news/{2020..2025,index}.html were fetched and parsed for 836 items across
# the period, 125 of which name CO2, capture, cement, steel or a European country
# and were fetched in full. THE REST OF MHI'S NEWSROOM IS NOT READ AND IS NOT
# CLAIMED TO BE — this node is on the perimeter as capture_technology, and MHI's
# gas turbines, ships, forklifts and air conditioners are a different company's
# worth of output that no reading of this file should be taken to cover.
M = "https://www.mhi.com/news/"

C("mhi", 13, "commercial facilities", "delivery_commitment", "supplier",
  "supplier_press", M + "22042501.html", "2022-04-25",
  note="'already been deployed at 13 commercial facilities around the world' — the KM "
       "CDR Process, cumulative and worldwide. A COUNT OF INSTALLATIONS, not a rate, "
       "not European, and not comparable with the tonnes on the edges below.")

E("mhi", "Drax", "framework_agreement", "supplier", "supplier_press",
  M + "200624.html", "2020-06-24", quantity=None, country="GB", sector="bioenergy",
  note="A BECCS pilot at the UK's largest renewable power generator.")
E("mhi", "Drax", "framework_agreement", "supplier", "supplier_press",
  M + "210610.html", "2021-06-10", quantity=None, country="GB", sector="bioenergy",
  note="Wider agreement; MHI also to open a CCUS centre of excellence in London and "
       "to look at producing its solvent in the UK.")
E("mhi", "Technology Centre Mongstad", "framework_agreement", "supplier",
  "supplier_press", M + "210304.html", "2021-03-04", quantity=None, country="NO",
  sector="test centre", site="Mongstad",
  note="Agreement to test the KS-21 solvent at TCM's amine plant. A test campaign at "
       "a public test centre, not plant demand.")
E("mhi", "Technology Centre Mongstad", "framework_agreement", "supplier",
  "supplier_press", M + "211019.html", "2021-10-19", quantity=None, country="NO",
  sector="test centre", site="Mongstad",
  note="Result of the campaign: 95–99% capture rate confirmed. Same engagement, "
       "second document.")
E("mhi", "Eni S.p.A. (through NextChem)", "technology_licence", "supplier",
  "supplier_press", M + "22042501.html", "2022-04-25",
  quantity=(25000, "tonnes CO2 per year"), country="IT", sector="oil and gas",
  site="Casalborsetti Ravenna",
  note="Licence and process design package for phase 1 of Italy's first CCUS project. "
       "The store is the Ravenna CCS node on this perimeter.",
  firmness="contract", firmness_basis=
  "(MHIENG), a Mitsubishi Heavy Industries (MHI) Group company based in "
  "Yokohama, has agreed to license its carbon capture technology and "
  "provide the process design package (PDP) for the foreseen phase 1 of "
  "Italy’s first CCUS (Carbon dioxide Capture, Utilization and Storage) "
  "project being developed by Eni S.p.A., the biggest integrated energy "
  "company in Italy.")
E("mhi", "an undisclosed customer (Peterhead Power Station)", "framework_agreement",
  "supplier", "supplier_press", M + "22083001.html", "2022-08-30", quantity=None,
  country="GB", sector="power", site="Peterhead Aberdeenshire",
  note="FEED for a GTCC power plant and CO2 capture plant. The release names the "
       "station and not the customer.",
  refuse_match="'Aberdeenshire' is a site alias of statera-kintore-hydrogen and it is "
               "a COUNTY. A gas-fired power station at Peterhead is not a hydrogen "
               "project at Kintore; they share a local authority and nothing else.")
E("mhi", "ArcelorMittal (with BHP and Mitsubishi Development)", "framework_agreement",
  "supplier", "supplier_press", M + "221027.html", "2022-10-27", quantity=None,
  country="BE", sector="steel", site="Gent",
  note="Multi-year trial of MHIENG carbon capture at ArcelorMittal's Gent steel plant "
       "and one North American site, plus a feasibility and design study. Gent is not "
       "a row in this register's steel perimeter, which holds ArcelorMittal at Bremen/"
       "Eisenhüttenstadt and Dunkirk.")
E("mhi", "Hanson UK", "framework_agreement", "supplier", "supplier_press",
  M + "22121502.html", "2022-12-15", quantity=(800000, "tonnes CO2 per year"),
  country="GB", sector="cement", site="Padeswood Flintshire",
  note="Pre-FEED. Hanson UK is Heidelberg Materials' UK arm and the later releases "
       "call the same works Heidelberg Materials' — one plant, two company names, "
       "three years apart.")
E("mhi", "Saipem S.p.A.", "technology_licence", "supplier", "supplier_press",
  M + "230427.html", "2023-04-27", quantity=None, country="IT", sector="engineering",
  note="General License Agreement. Saipem is a route to market, not an emitter.",
  firmness="contract", firmness_basis=
  "(MHI) has concluded a General License Agreement (GLA) with Saipem "
  "S.p.A., one of major engineering companies in Italy, under which MHI "
  "will provide Saipem with its proprietary “KM CDR Process™” and “Advanced "
  "KM CDR Process™” technologies for use in CO 2 capture plants.")
E("mhi", "Essar Oil UK Limited (EET Industrial Carbon Capture)", "technology_licence",
  "supplier", "supplier_press", M + "23110902.html", "2023-11-09", quantity=None,
  country="GB", sector="refining", site="Stanlow Cheshire",
  note="Selected as licensor; basic engineering design package, Advanced KM CDR.",
  firmness="intent", firmness_basis=
  "(MHI) has been selected as licensor of CO 2 capture technology for the "
  "project known as EET Industrial Carbon Capture which is underway at the "
  "Stanlow Refinery, owned and operated by Essar Oil UK Limited in Cheshire "
  "County in northwest England.")
E("mhi", "Evero Energy Group Limited", "framework_agreement", "supplier",
  "supplier_press", M + "23110903.html", "2023-11-09", quantity=None, country="GB",
  sector="waste-to-energy", site="Ince Protos",
  note="InBECCS at Ince Bio Power, on the Protos energy park beside HyNet's "
       "prospective CO2 pipeline.")
E("mhi", "Heidelberg Materials UK", "framework_agreement", "supplier", "supplier_press",
  M + "24020601.html", "2024-02-06", quantity=(800000, "tonnes CO2 per year"),
  country="GB", sector="cement", site="Padeswood Flintshire",
  note="FEED with Worley, following the 2022 pre-FEED. 'UK's first CO2 capture plant "
       "at a cement production facility'.")
E("mhi", "ArcelorMittal", "framework_agreement", "supplier", "supplier_press",
  M + "24052102.html", "2024-05-21", quantity=None, country="BE", sector="steel",
  site="Gent", note="Trial carbon capture unit begins operation at Gent. Same trial "
                    "as 2022-10-27, second document.")
E("mhi", "Eni and Snam (Ravenna CCS)", "technology_licence", "supplier",
  "supplier_press", M + "24091802.html", "2024-09-18",
  quantity=(25000, "tonnes CO2 per year"), country="IT", sector="oil and gas",
  site="Casalborsetti Ravenna",
  note="OPERATIONAL — 'Europe's first fully operational post-combustion carbon capture "
       "plant'. Same 25,000 t/yr as the 2022 licence, now running. CO2 injected into a "
       "depleted offshore Eni gas field.",
  firmness="contract", firmness_basis=
  "As well as being a significant development in the decarbonization of "
  "industry, this also represents a major milestone for \" Ravenna CCS \", "
  "the first project for the capture, transport and permanent storage of CO "
  "2 in Italy, developed for exclusively environmental purposes by Eni and "
  "Snam.")
E("mhi", "Heidelberg Materials UK", "equipment_order", "supplier", "supplier_press",
  M + "251208.html", "2025-12-08", quantity=(800000, "tonnes CO2 per year"),
  country="GB", sector="cement", site="Padeswood Flintshire",
  note="EXECUTION PHASE, after Heidelberg Materials' FID with the UK government. "
       "'the first in Europe to deploy MHI's Advanced KM CDR Process' at a cement "
       "works; CO2 to depleted gas fields under Liverpool Bay via HyNet North West. "
       "Padeswood is NOT a row in this register's cement perimeter, and Heidelberg "
       "Materials holds three rows that are — the largest single unmatched cement "
       "customer this sweep found.",
  firmness="contract", firmness_basis=
  "Project will deploy MHI's carbon capture technology following Heidelberg "
  "Materials' final investment decision with UK Government -- 2025-12-08 "
  "SHARE ・ First full-scale CCS project in the UK cement sector, to capture "
  "around 800,000 tonnes of CO 2 per year ・ Follows front-end engineering "
  "design (FEED) completed by MHI and Worley ・ Part of the first wave of "
  "projects under the UK's CCUS cluster…")

# --- Linde plc ----------------------------------------------------------------
# 278 items under linde.com/news-and-media in the sitemap; 31 in period whose slug
# names carbon, CO2, capture, CCS, hydrogen or electrolysis were fetched and read.
# ONLY THE CAPTURE EDGES ARE RECORDED (DECISION D-4): Linde is on this perimeter as
# capture_technology, and the great majority of what was read is industrial-gas
# supply — oxygen to steelworks, hydrogen to refineries, air separation units. That
# is a real and much larger European business and it is not this node's product.
#
# Linde also appears on this sweep as a BUYER: ITM Power's 24 MW Leuna electrolyser
# and both 100 MW Lingen units were sold to Linde Engineering. A node that is a
# customer of another node is not a contradiction; it is what a supply chain is.
L = "https://www.linde.com/news-and-media/"

E("linde", "Snam", "framework_agreement", "supplier", "supplier_press",
  L + "2020/linde-and-snam-sign-agreement-to-jointly-develop-clean-hydrogen-projects",
  "2020-12-07", quantity=None, country="IT", sector="gas infrastructure",
  note="MoU on clean hydrogen projects and infrastructure in Europe. No site.")
E("linde", "SLB", "framework_agreement", "supplier", "supplier_press",
  L + "2022/linde-and-slb-collaborate-on-carbon-capture-and-sequestration", "2022-10-31",
  quantity=None, note="Collaboration on CCUS in hydrogen, ammonia and natural gas "
                      "processing. SLB is half of the slb-capturi node on this "
                      "perimeter — two capture suppliers collaborating rather than "
                      "competing, with no customer and no site named.")
E("linde", "Heidelberg Materials", "equipment_order", "supplier", "supplier_press",
  L + "2023/linde-and-heidelberg-materials-announce-large-scale-carbon-capture-project",
  "2023-04-12", quantity=(70000, "tonnes CO2 per year"), country="DE", sector="cement",
  site="Lengfurt",
  note="Jointly build, own and operate a capture and liquefaction facility at the "
       "Lengfurt works; most of the liquid CO2 to be sold by Linde into the merchant "
       "market. A THIRD Heidelberg Materials cement site outside the register's "
       "perimeter, after Padeswood and Edmonton.",
  firmness="contract", firmness_basis=
  "Woking, UK, April 12, 2023 - Linde (NYSE: LIN) today announced it has "
  "signed an agreement with Heidelberg Materials, one of the world's "
  "largest building materials companies, to jointly build, own and operate "
  "a large-scale carbon capture and liquefaction facility. Carbon dioxide "
  "(CO 2 ) is a by-product of cement production and is estimated to be "
  "responsible for around 7% of global carbon…")

# --- Air Liquide S.A. ---------------------------------------------------------
# The two sitemap pages list 1,809 press items; 177 in period whose slug names
# carbon, CO2, capture, CCS, hydrogen, electrolysis, cement or steel were listed and
# the 74 English ones naming carbon, capture or a heavy industry were fetched. As
# with Linde, ONLY THE CAPTURE EDGES ARE RECORDED — Air Liquide's long-term oxygen
# and nitrogen contracts with steelmakers are the larger business and the wrong
# product for this node kind.
A = "https://www.airliquide.com/group/press-releases-news/"

E("air-liquide", "ArcelorMittal", "framework_agreement", "supplier", "supplier_press",
  A + "2021-03-17/air-liquide-and-arcelormittal-join-forces-accelerate-decarbonization-"
      "steel-production-basin-dunkirk", "2021-03-17", quantity=None, country="FR",
  sector="steel", site="Dunkirk",
  note="MoU on low-carbon steel in the Dunkirk basin. The register holds 3d-dunkirk "
       "— ArcelorMittal's DMX capture demonstration at the same works — and whether "
       "this MoU is that project or a second one beside it is not decidable from "
       "this release.")
E("air-liquide", "BASF", "framework_agreement", "supplier", "supplier_press",
  A + "2021-11-22/air-liquide-and-basf-welcome-support-european-innovation-fund-joint-"
      "ccs-project", "2021-11-22", quantity=None, country="BE", sector="chemicals",
  site="Antwerp", note="Kairos@C, selected for EU Innovation Fund support; 'the "
                       "world's largest cross-border CCS value chain', feeding the "
                       "Antwerp@C liquefaction and export terminal.")
E("air-liquide", "Eni", "framework_agreement", "supplier", "supplier_press",
  A + "2022-03-21/air-liquide-and-eni-cooperate-decarbonization-hard-abate-industries-"
      "europe", "2022-03-21", quantity=None, country="IT",
  sector="oil and gas")
E("air-liquide", "Sogestran", "co2_transport", "supplier", "supplier_press",
  A + "2022-04-05/air-liquide-and-sogestran-partner-develop-shipping-solutions-carbon-"
      "management", "2022-04-05", quantity=None, country="FR", sector="shipping",
  note="Joint venture for large-scale liquid CO2 shipping and barging.",
  firmness="contract", firmness_basis=
  "Air Liquide and Sogestran have signed an agreement to form a joint "
  "venture [1] .")
E("air-liquide", "Lhoist", "framework_agreement", "supplier", "supplier_press",
  A + "2022-05-09/air-liquide-and-lhoist-join-forces-launch-first-its-kind-"
      "decarbonization-project-lime-production", "2022-05-09", quantity=None,
  country="FR", sector="lime", site="Réty Hauts-de-France",
  note="MoU to put Cryocap on Lhoist's lime plant; co-application to the EU "
       "Innovation Fund. LIME, not cement — a heavy-industry customer class the "
       "register's perimeter does not hold at all.")
E("air-liquide", "Fluxys Belgium and Port of Antwerp-Bruges", "co2_transport",
  "supplier", "grant_award",
  A + "2022-12-12/air-liquide-fluxys-belgium-and-port-antwerp-bruges-awarded-eu-funding-"
      "building-antwerpc-co2-export", "2022-12-12", quantity=None, country="BE",
  sector="port / gas infrastructure",
  note="EUR 144.6 million under the Connecting Europe Facility. A GRANT AWARD, and "
       "the source_type says so: this is the Commission's money, described by one of "
       "the recipients.",
  firmness="intent", firmness_basis=
  "We are very pleased that the Antwerp@C CO2 Export Hub project, supported "
  "by innovative Air Liquide technologies, has been selected by the "
  "Connecting Europe Facility for Energy program.")
E("air-liquide", "Holcim", "framework_agreement", "supplier", "supplier_press",
  A + "2023-05-02/air-liquide-and-holcim-collaborate-project-decarbonize-cement-"
      "production-belgium", "2023-05-02", quantity=None, country="BE", sector="cement",
  note="MoU on 'Holcim's new cement production plant under development in Belgium', "
       "with a joint EU Innovation Fund application. The 2026 agreement names that "
       "plant as Obourg; this release does not, so it is not linked to a row.")
E("air-liquide", "Stockholm Exergi", "equipment_order", "supplier", "supplier_press",
  A + "2024-07-17/air-liquide-innovative-co2-liquefaction-technology-selected-stockholm-"
      "exergi-world-scale-carbon", "2024-07-17",
  quantity=(3500, "tonnes CO2 per day"), country="SE", sector="bioenergy",
  site="Stockholm",
  note="Cryocap LQ liquefaction unit, 'one of the largest in the world'. THE UNIT IS "
       "TONNES PER DAY while every other CO2 quantity in this file is tonnes per "
       "year; not converted, per the brief. The release separately says the BECCS "
       "facility aims to store around 8 Mt over its first ten years.",
  firmness="intent", firmness_basis=
  "Air Liquide's innovative large scale CO₂ liquefaction technology, "
  "Cryocap™ LQ, has been selected by Stockholm Exergi, Stockholm’s energy "
  "company, to contribute to its Bio-Energy Carbon Capture & Storage "
  "(BECCS) project.")
E("air-liquide", "Cementir Holding Group (Aalborg Portland)", "framework_agreement",
  "supplier", "grant_award",
  A + "2024-10-24/air-liquide-and-cementir-holding-group-receive-support-european-"
      "innovation-fund-carbon-capture-and", "2024-10-24",
  quantity=(1500000, "tonnes CO2 per year"), country="DK", sector="cement",
  site="Aalborg",
  note="ACCSION, EUR 220 million from the EU Innovation Fund; 'one of the first full "
       "onshore CCS value chains in Europe'. Pre-FID. Aalborg Portland is a cement "
       "works outside the register's perimeter and the largest single tonnage of any "
       "unmatched cement customer in this sweep.")
E("air-liquide", "Dunkerque LNG (D'Artagnan)", "co2_transport", "supplier",
  "supplier_press",
  A + "2024-06-18/decarbonization-dunkirk-basin-air-liquide-and-dunkerque-lng-co2-"
      "infrastructure-project-takes-major", "2024-06-18", quantity=None, country="FR",
  sector="CO2 infrastructure", site="Dunkirk",
  note="CO2 infrastructure; more than EUR 400m investment with more than EUR 160m of "
       "CEF-E grant. FID linked to signing 'CO2 management and capture as a service' "
       "contracts — the offtake does not exist yet.",
  refuse_match="'Dunkirk' is a site alias of 3d-dunkirk and it is a CITY. D'Artagnan "
               "is a CO2 export terminal with Dunkerque LNG; 3d-dunkirk is "
               "ArcelorMittal's DMX capture demonstration at the steelworks. Both "
               "stand in Dunkirk and they are not the same thing.",
  firmness="intent", firmness_basis=
  "Air Liquide and Dunkerque LNG welcome the decision of the European "
  "Commission to support the D'Artagnan project.")
E("air-liquide", "Holcim", "equipment_order", "supplier", "supplier_press",
  A + "2026-02-27/air-liquide-and-holcim-sign-agreement-decarbonize-cement-production-"
      "carbon-capture-project-belgium", "2026-02-27", quantity=None, country="BE",
  sector="cement", site="Obourg",
  note="Agreement to supply oxygen for the oxyfuel-ready clinker line and Cryocap OXY "
       "for capture at Obourg; CO2 to an export hub such as Antwerp@C for offshore "
       "storage. THE SUPPLIER SIDE OF go4zero-obourg. No tonnage is stated.",
  firmness="contract", firmness_basis=
  "Air Liquide and Holcim reach a new stage in their collaboration with the "
  "signing of an agreement to develop a state-of-the-art carbon capture "
  "solution for Holcim’s near-zero cement plant at Obourg in Belgium.")

# =============================================================================
# dri_plant
# =============================================================================

# --- Midrex Technologies, Inc. ------------------------------------------------
# 175 items across the press-release and news sitemaps, ALL fetched and read — the
# whole newsroom, which is small enough to take whole. Midrex is UNLISTED (a Kobe
# Steel subsidiary) and publishes no order book.
#
# NO stated_capacity IS RECORDED FOR THIS NODE, and that is a statement rather than
# a gap. Midrex licenses a process and engineers plants; it has no line with a rate.
# The tonnages below are the CUSTOMERS' plants, which is why they sit on edges and
# not on the node — and it is why the docket's arithmetic section cannot compare
# them with anything for this node kind.
X = "https://www.midrex.com/"

E("midrex", "H2 Green Steel", "equipment_order", "supplier", "supplier_press",
  X + "press-releases/midrex-and-paul-wurth-selected-by-h2-green-steel/", "2022-10-11",
  quantity=(2100000, "tonnes DRI per year"), country="SE", sector="steel", site="Boden",
  note="MIDREX H2 plant, with Paul Wurth (an SMS group company — SMS is also a node "
       "on this perimeter). 'the world's first commercial 100 percent hydrogen direct "
       "reduced iron plant'. Production expected 2025, ramp-up 2026.",
  firmness="contract", firmness_basis=
  "(Midrex) and Paul Wurth, an SMS Group company, announce a signed "
  "agreement with H2 Green Steel to supply the world’s first commercial 100 "
  "percent hydrogen direct reduced iron (DRI) plant.")
E("midrex", "thyssenkrupp Steel Europe AG", "equipment_order", "supplier",
  "supplier_press",
  X + "press-releases/thyssenkrupp-steel-selects-midrex-flex-for-immediate-co2-"
      "emissions-reduction/", "2023-03-13",
  quantity=(2500000, "tonnes DRI per year"), country="DE", sector="steel",
  site="Duisburg",
  note="MIDREX Flex with Paul Wurth, combined with SMS group melting technology. "
       "Starts on reformed natural gas at 50%+ hydrogen and transitions to up to 100%. "
       "Start-up planned end of 2026.",
  firmness="contract", firmness_basis=
  "thyssenkrupp Steel Selects MIDREX Flex™ for Immediate CO2 Emissions "
  "Reduction March 2023 Share")
E("midrex", "ArcelorMittal Germany", "equipment_order", "owner", "owner_press",
  X + "news/german-federal-government-to-provide-e55-million-for-arcelormittals-"
      "hydrogen-dri-plant/", "2021-09-07", quantity=None, country="DE", sector="steel",
  site="Hamburg",
  note="SPEAKER IS THE OWNER, not Midrex: the page says it is 'adapted from a 7 "
       "September 2021 ArcelorMittal news release'. A supplier's newsroom carrying "
       "somebody else's announcement does not make the supplier the speaker. EUR 55m "
       "of federal funding for Germany's first industrial-scale hydrogen DRI plant. "
       "Hamburg is not a row in the register's steel perimeter.",
  firmness="intent", firmness_basis=
  "German Federal Government to Provide €55 Million for ArcelorMittal’s "
  "Hydrogen DRI Plant September 2021 Share Editor’s note: This article is "
  "adapted from a 7 September 2021")
E("midrex", "Blastr Green Steel", "equipment_order", "supplier", "supplier_press",
  X + "press-releases/midrex-and-primetals-selected-by-blastr/", "2024-07-09",
  quantity=(2000000, "tonnes DRI per year"), country="FI", sector="steel", site="Inkoo",
  note="MIDREX H2 plant with Primetals — another node on this perimeter — inside a "
       "2.5 Mt/yr steelmaking facility. Blastr is not a row in this register.",
  firmness="contract", firmness_basis=
  "(Midrex) and Primetals have been selected to supply a hydrogen direct "
  "reduced iron (DRI) plant for Blastr Green Steel (Blastr), one of the "
  "largest industry start-ups in the Nordic region.")
E("midrex", "thyssenkrupp Steel Europe AG", "equipment_order", "supplier",
  "supplier_press",
  X + "news/thyssenkrupp-steel-receives-construction-approval-for-hydrogen-ready-dri-"
      "smelter-project/", "2026-01-01", no_dateline=True,
  quantity=(2500000, "tonnes DRI per year"), country="DE", sector="steel",
  site="Duisburg",
  note="CONSTRUCTION APPROVAL on the 2023 order — 'the largest single order in TKS "
       "history', about EUR 2bn of federal and state funding against just under EUR 1bn "
       "of TKS's own. THE ONE DOCUMENT IN THIS FILE WITH NO DATELINE AT ALL: no "
       "printed date and no metadata date. Under D-7 as ruled on 11 September 2026 it "
       "takes the date of the copy on file — this sweep's own fetch — and that date is "
       "an UPPER BOUND, not the date it was published. The first pass guessed the year "
       "from the text and the guess is withdrawn.",
  firmness="contract", firmness_basis=
  "thyssenkrupp Steel Europe AG (TKS) has received approval from the "
  "Düsseldorf district government for early start of construction of the "
  "first direct reduction plant for hydrogen-based steel production. The "
  "approval notice is an important milestone in the approval process.")

# --- McPhy Energy S.A. --------------------------------------------------------
# THE SUPPLIER'S WEBSITE NO LONGER EXISTS. mcphy.com does not resolve; www.mcphy.com
# serves a 107-byte redirect that ends at hydrogen.johncockerill.com. Every release
# below is read from an Internet Archive capture of mcphy.com under DECISION D-7 —
# the speaker's own document on the speaker's own domain, served by a third party.
# The Wayback capture timestamp is in each URL and dep_records appends it to the
# note as the archived copy's source date — DERIVED, never typed, because a
# hand-written capture date drifts the moment a better capture is substituted.
# `date` itself
# is the release's own dateline, because that is what the field means everywhere
# else in this file and what the sweep period is measured against.
#
# The CDX index returned 125 distinct captures of mcphy.com/en/press-releases/*;
# 23 were fetched and 21 carry a readable body. One capture — the 20 MW Netherlands
# project of 22 January 2020 — is a navigation-only snapshot with no article text,
# so no edge is recorded from it. There is no way to go back for a better one.
#
# EIGHT OF THE TWENTY-ONE ARE OUT OF PERIOD (2016–2018). They are in the cache
# because the archive indexed them together, and they are not edges.
W = "https://web.archive.org/web/"

R_.status_event(
    "mcphy", "2025-07-08", "listed (Euronext Paris: MCPHY)",
    "key assets acquired by John Cockerill Hydrogen",
    "https://johncockerill.com/en/press-and-news/news/hydrogen-electrolyseur-belfort-"
    "prod-aspach/", "supplier_press",
    "'On July 8, 2025, the Belfort Commercial Court accepted John Cockerill Hydrogen's "
    "bid to acquire McPhy's key assets, including the Belfort plant, innovative "
    "technologies, intellectual property, and approximately 80 employees in Europe.' "
    "Stated by the acquirer, a year later. McPhy's own domain was gone before this "
    "sweep ran, so there is no seller-side document to set beside it.")

C("mcphy", 1000, "MW/yr", "nameplate", "supplier", "supplier_press",
  W + "20221102091939id_/https://mcphy.com/en/press-releases/the-launch-of-the-mcphys-"
      "gigafactory-on-the-belfort-site/", "2022-11-02",
  note="Belfort gigafactory at full ramp-up. PLANNED: FID taken 26 October 2022, "
       "commissioning from the first half of 2024, EUR 114m of French state aid under "
       "IPCEI. The plant never reached this rate — the "
       "company's assets were sold by a commercial court two and a half years later.")
C("mcphy", 1300, "MW/yr", "nameplate", "supplier", "supplier_press",
  W + "20221102091939id_/https://mcphy.com/en/press-releases/the-launch-of-the-mcphys-"
      "gigafactory-on-the-belfort-site/", "2022-11-02",
  note="Group total including San Miniato, Italy. Same release, same day, a second "
       "figure on a wider boundary — both recorded because the brief says no value is "
       "superseded.")

_MCPHY_TO_JC = {"node_id": "john-cockerill", "since": "2025-07-08",
                "source_url": "https://johncockerill.com/en/press-and-news/news/"
                              "hydrogen-electrolyseur-belfort-prod-aspach/"}

E("mcphy", "Apex Energy", "equipment_order", "supplier", "supplier_press",
  W + "20200815135550id_/https://mcphy.com/en/press-releases/2-mw-of-electrolysis-in-"
      "germany/", "2020-06-30", quantity=(2, "MW"), country="DE", sector="hydrogen",
  site="Rostock-Laage", inherited_by=_MCPHY_TO_JC,
  note=" Construction completed 12 June 2020.",
  firmness="contract", firmness_basis=
  "Apex inaugurates a zero-carbon hydrogen production plant, equipped with "
  "McPhy electrolyzers • The German Rostock-based engineering and cleantech "
  "company Apex Energy inaugurated the 2 MW zero-carbon hydrogen production "
  "platform equipped by McPhy. • The McLyzer 400-30 electrolyzer (2 MW of "
  "high-power electrolysis) will produce more than 300 tons of zero-carbon "
  "hydrogen per year. La Motte-Fanjas,…")
E("mcphy", "DIAX", "equipment_order", "supplier", "supplier_press",
  W + "20200830195327id_/https://mcphy.com/en/press-releases/hydrogen-for-light-"
      "industry/", "2020-06-04", quantity=None, country="BA",
  sector="diamond tools / sintering", inherited_by=_MCPHY_TO_JC,
  note="Piel by McPhy hydrogen and nitrogen generators for a sintering line in Bosnia. "
       " A Western Balkans customer — inside this sweep's "
       "Europe and outside almost every other boundary anyone draws.",
  firmness="contract", firmness_basis=
  "Based in Bosnia, DIAX selected the complete line of Piel by McPhy "
  "hydrogen and nitrogen generators to equip its sintering diamond tools "
  "line.")
E("mcphy", "HYPORT (ENGIE Solutions and AREC Occitanie)", "equipment_order", "supplier",
  "supplier_press",
  W + "20210304065556id_/https://mcphy.com/en/press-releases/hyport/", "2021-03-04",
  quantity=(1, "MW"), country="FR", sector="airport / mobility",
  site="Toulouse-Francazal", inherited_by=_MCPHY_TO_JC,
  note="Two hydrogen stations and 1 MW of electrolysis (400 kg/day) at an airport. "
       "",
  firmness="intent", firmness_basis=
  "McPhy announced as a key partner by the company HYPORT to equip "
  "Toulouse-Blagnac airport with a complete zero-carbon hydrogen chain • "
  "Two hydrogen stations and 1 MW of electrolysis will equip Toulouse-"
  "Blagnac airport • The solution developed will satisfy mobility and "
  "logistics needs, and will supply hydrogen to industrial sites interested "
  "in decarbonizing their processes • This contract was…")
E("mcphy", "R-Hynoca (Strasbourg)", "equipment_order", "supplier", "supplier_press",
  W + "20210907053824id_/https://mcphy.com/en/press-releases/mcphy-will-equip-the-r-"
      "hynoca-project-in-strasbourg/", "2021-09-07", quantity=None, country="FR",
  sector="hydrogen", site="Strasbourg", inherited_by=_MCPHY_TO_JC,
  note="",
  firmness="contract", firmness_basis=
  "La Motte-Fanjas, September 07, 2021 – 07:30 am CEST – McPhy (Euronext "
  "Paris Compartment C: MCPHY, FR0011742329), specialized in zero-carbon "
  "hydrogen production and distribution equipment (electrolyzers and "
  "refueling stations), today announces that it has been selected by "
  "R-Hynoca, to set up the first hydrogen station in Strasbourg.")
E("mcphy", "Enel Green Power", "framework_agreement", "supplier", "supplier_press",
  W + "20211202001156id_/https://mcphy.com/en/press-releases/cooperation-agreement-with-"
      "enel-green-power/", "2021-11-30", quantity=(4, "MW"), country="IT",
  sector="renewables", site="Carlentini Sicily", inherited_by=_MCPHY_TO_JC,
  note="MoU for a 4 MW Augmented McLyzer on a renewable park.")
E("mcphy", "GreenH2Atlantic", "framework_agreement", "supplier", "supplier_press",
  W + "20211222191058id_/https://mcphy.com/en/press-releases/greenh2atlantic-project/",
  "2021-12-21", quantity=(100, "MW"), country="PT", sector="hydrogen", site="Sines",
  inherited_by=_MCPHY_TO_JC,
  note="Preferred supplier for a 100 MW plant on the Sines coal power station site; "
       "heads of terms, supply agreement expected in H1 2022; EUR 30m Horizon 2020 "
       "Green Deal grant. SINES IS AMBIGUOUS in this "
       "register — CALB's battery works and Galp's electrolyser both stand there.")
E("mcphy", "Hype", "equipment_order", "supplier", "supplier_press",
  W + "20220425160803id_/https://mcphy.com/en/press-releases/mcphy-signs-a-first-order-"
      "with-hype/", "2022-04-25", quantity=None, country="FR",
  sector="hydrogen mobility", inherited_by=_MCPHY_TO_JC,
  note="",
  firmness="contract", firmness_basis=
  "In this context, a first order was signed with Hype, for the supply of a "
  "2 MW alkaline electrolyzer and a Dual Pressure station with a capacity "
  "of 800 kg per day, which will be installed in the Paris region.")
E("mcphy", "Hype", "equipment_order", "supplier", "supplier_press",
  W + "20220704163153id_/https://mcphy.com/en/press-releases/mcphy-registers-a-new-order-"
      "for-hype-as-part-of-their-strategic-partnership/", "2022-07-04",
  quantity=(4, "MW"), country="FR", sector="hydrogen mobility",
  inherited_by=_MCPHY_TO_JC,
  note="'a second 2 to 4 MW electrolyzer and a second large capacity station'. The "
       "upper bound of the stated range is recorded.",
  firmness="contract", firmness_basis=
  "Grenoble, France, July 4, 2022 5:45 pm CEST – McPhy (Euronext Paris "
  "Compartment C: MCPHY, FR0011742329), specialized in zero-carbon hydrogen "
  "production and distribution equipment (electrolyzers and refueling "
  "stations), announces that it has secured a second order as part of its "
  "strategic partnership with Hype.")
E("mcphy", "Siemens Energy (for the CEOG project)", "framework_agreement", "supplier",
  "supplier_press",
  W + "20221025160231id_/https://mcphy.com/en/press-releases/mcphy-signs-an-8-year-"
      "maintenance-contract-with-siemens-energy-within-the-framework-of-the-ceog-"
      "project/", "2022-10-25", quantity=None, inherited_by=_MCPHY_TO_JC,
  note="An 8-year MAINTENANCE contract, with Siemens Energy — a node on this perimeter "
       "— as the manufacturer and operator. The plant is in French Guiana, which is an "
       "EU outermost region and is not in this sweep's Europe, so no country is "
       "recorded and no unmatched customer is created.")

# --- Primetals Technologies ---------------------------------------------------
# 327 news items whose slug names DRI, direct reduction, hydrogen, green, steel or
# a European steelmaker were fetched from the en sitemap and read; 59 of those name
# a European customer or country.
#
# MOST OF THEM ARE NOT EDGES, AND THAT IS THE PRODUCT RULE (DECISION D-4 extended
# here — DECISION D-8). Primetals is on this perimeter as dri_plant. Its European
# order book in this period is overwhelmingly conventional millwork: converters,
# casters, cold mills, drive systems, dedusting, gas cleaning, automation upgrades
# at voestalpine, thyssenkrupp, Salzgitter, ArcelorMittal, Liberty, Marcegaglia,
# Aperam and Tata. Every one of those is a real order from a European steelmaker
# and none is a direct reduction plant. What is recorded is the ironmaking route:
# direct reduction, smelters, and the electric arc furnaces that replace a blast
# furnace as part of a stated green-steel programme. The boundary is arguable — an
# EAF is not a DRI plant — and it is drawn where the OWNER's own release says the
# furnace is part of the hydrogen transition.
T_ = "https://www.primetals.com/en/news/"

E("primetals", "voestalpine", "equipment_order", "supplier", "supplier_press",
  T_ + "hyfor-pilot-plant-under-operation-the-next-step-for-carbon-free-hydrogen-based-"
       "direct-reduction-is-done/", "2021-06-24", quantity=None, country="AT",
  sector="steel", site="Donawitz",
  note="HYFOR hydrogen fine-ore reduction PILOT commissioned at voestalpine's Donawitz "
       "site. A pilot, not a plant; no capacity stated.",
  firmness="contract", firmness_basis=
  "In April, the Hydrogen-based fine-ore reduction (HYFOR) pilot plant "
  "developed by Primetals Technologies was commissioned at the voestalpine "
  "site in Donawitz, Austria.")
E("primetals", "GravitHy", "framework_agreement", "supplier", "supplier_press",
  T_ + "gravithy-imminent-market-leader-in-green-iron-and-steel-is-launched-today-by-"
       "world-class-industrial-consortium/", "2022-06-30", quantity=None, country="FR",
  sector="steel", note="Launch of the GravitHy consortium for DRI plus EAF in France. "
                       "Primetals is a consortium member; no order, no site named here.")
E("primetals", "Salzgitter", "equipment_order", "supplier", "supplier_press",
  T_ + "salzgitter-places-large-order-with-primetals-technologies-for-electric-arc-"
       "furnace-as-part-of-major-green-steel-transformation-program/", "2022-08-25",
  quantity=(1900000, "tonnes steel per year"), country="DE", sector="steel",
  site="Salzgitter SALCOS", project_id="salcos-salzgitter",
  note="A 220-tonne EAF Ultimate, 1.9 Mt/yr, start-up end of 2025, stated by Primetals "
       "as 'the first step' of SALCOS — which plans two direct reduction plants and "
       "three electric furnaces by 2033. project_id set by hand for the same reason as "
       "the Sunfire edge: the bare alias 'Salzgitter' is ambiguous with the PowerCo "
       "battery row and an EAF inside a steelworks is not.",
  firmness="contract", firmness_basis=
  "On August 23rd, German steel producer Salzgitter signed a contract with "
  "Primetals Technologies for an EAF Ultimate .")
E("primetals", "voestalpine (with Fortescue and Mitsubishi Corporation)",
  "framework_agreement", "supplier", "supplier_press",
  T_ + "primetals-technologies-fortescue-and-voestalpine-to-jointly-evaluate-"
       "groundbreaking-green-ironmaking-plant/", "2022-12-19", quantity=None,
  country="AT", sector="steel",
  note="MoU to evaluate a green ironmaking plant. No site and no capacity.")
E("primetals", "Hydnum Steel", "framework_agreement", "supplier", "supplier_press",
  T_ + "primetals-technologies-and-hydnum-steel-join-forces-for-new-green-steel-"
       "production-plant-in-spain/", "2023-06-15", quantity=None, country="ES",
  sector="steel", site="Puertollano",
  note="MoU for a greenfield green steel plant at Puertollano, with Russula, ABEI "
       "Energy and Siemens. Hydnum Steel is not a row in this register.")
E("primetals", "voestalpine", "equipment_order", "supplier", "supplier_press",
  T_ + "primetals-technologies-chosen-as-supplier-of-electric-arc-furnace-based-"
       "steelmaking-plant-in-austria/", "2024-01-12", quantity=None, country="AT",
  sector="steel", site="Linz",
  note="A 180-tonne EAF Ultimate for Linz, start-up 2027, stated as a first step of "
       "voestalpine's greentec steel programme — 'one electric arc furnace will be "
       "built at each of voestalpine's sites, in Linz and Donawitz'. No tonnage given "
       "for the furnace.",
  firmness="contract", firmness_basis=
  "voestalpine has placed an order with Primetals Technologies for a "
  "180-ton EAF Ultimate to be implemented at the Austrian steel producer’s "
  "site in Linz, Austria.")
E("primetals", "Blastr Green Steel", "equipment_order", "supplier", "supplier_press",
  T_ + "blastr-green-steel-chooses-primetals-technologies-as-"
       "technological-partner-for-low-carbon-emissions-plant/", "2024-07-09",
  quantity=(2500000, "tonnes steel per year"), country="FI", sector="steel",
  site="Inkoo",
  note="EAF-based meltshop with a 300-tonne EAF Ultimate for direct charging of hot "
       "DRI. The DRI plant beside it is Midrex's — the two suppliers announced the "
       "same project on the same day, and both edges are recorded.",
  firmness="contract", firmness_basis=
  "Recently, Blastr Green Steel has chosen Primetals Technologies as its "
  "technological partner for the development of a new 2.5 million tons-per-"
  "year steel production complex to be implemented in Inkoo, close to the "
  "city of Helsinki, Finland.")
E("primetals", "voestalpine (Hy4Smelt, with Rio Tinto and Mitsubishi Corporation)",
  "equipment_order", "supplier", "supplier_press",
  T_ + "construction-begins-on-hydrogen-based-ironmaking-plant-in-linz-austria/",
  "2025-09-25", quantity=(3, "tonnes per hour"), country="AT", sector="steel",
  site="Linz",
  note="Hy4Smelt industrial-scale DEMONSTRATION plant combining HYFOR direct reduction "
       "with a smelter; start-up end of 2027. THE UNIT IS TONNES PER HOUR, the only "
       "one in this file, and it is not converted.",
  firmness="contract", firmness_basis=
  "Seeing construction underway of the globally unique Hy4Smelt "
  "demonstration plant once again confirms our technological and innovation "
  "leadership in green steel production.\" Herbert Eibensteiner CEO of "
  "voestalpine AG Hydrogen-Based Direct Reduction and Smelting HYFOR is the "
  "world’s first direct reduction technology for iron ore fines that "
  "eliminates the need for agglomeration of the iron ore fines.")

# --- Tenova S.p.A. ------------------------------------------------------------
# 171 press and news items in the sitemap; 83 whose slug names DRI, hydrogen,
# green, EAF or a European steelmaker were fetched and read. The same product rule
# as Primetals (DECISION D-8) applies: reheating furnaces, rolling mills, digital
# systems and heat-treatment orders to European steelmakers are read and not
# recorded; direct reduction and the EAFs of a stated decarbonisation programme are.
V = "https://tenova.com/newsroom/press-releases/"

E("tenova", "Salzgitter Flachstahl GmbH", "equipment_order", "supplier",
  "supplier_press", V + "tenova-received-order-dri-plant-salzgitter-flachstahl-germany",
  "2020-12-17", quantity=None, country="DE", sector="steel",
  project_id="salcos-salzgitter", site="Salzgitter",
  note="An ENERGIRON direct reduction plant for Salzgitter Flachstahl. No capacity in "
       "the text this sweep could read; the 2022 MoU states 2.1 Mt/yr and the 2023 "
       "contract 'more than 2 million tons'.",
  firmness="contract", firmness_basis=
  "Castellanza, December 17, 2020 – Salzgitter Flachstahl GmbH , the "
  "largest steel subsidiary in the Salzgitter Group, has commissioned "
  "Tenova , a leading company specialized in innovative solutions for the "
  "metals and mining industries, for the construction of µDRAL , a "
  "demonstration plant for the production of Direct Reduced Iron (DRI) , "
  "using up to 100% hydrogen as reducing agent.")
E("tenova", "Salzgitter AG", "framework_agreement", "supplier", "supplier_press",
  V + "mou-salzgitter-and-tenova-salcosr", "2022-03-08",
  quantity=(2100000, "tonnes DRI per year"), country="DE", sector="steel",
  project_id="salcos-salzgitter", site="Salzgitter SALCOS",
  note="MoU. 'Conditional on the respective funding approvals, Salzgitter AG intends "
       "to order a DRI plant from Tenova with an annual capacity of 2.1 million tons'. "
       "ENERGIRON is jointly developed by Tenova and Danieli — two nodes on this "
       "perimeter behind one technology.")
E("tenova", "Salzgitter AG", "equipment_order", "supplier", "supplier_press",
  V + "energironr-direct-reduction-plant-contracted-salzgitter-ag-represents",
  "2023-05-24", quantity=(2000000, "tonnes DRI per year"), country="DE", sector="steel",
  project_id="salcos-salzgitter", site="Salzgitter Flachstahl SALCOS",
  note="CONTRACT, by a consortium of Tenova, Danieli and DSD Steel Group. 'more than 2 "
       "million tons of DRI per year' — a DIFFERENT FIGURE from the 2.1 Mt/yr of the "
       "2022 MoU, one speaker, fourteen months apart. Logged as a slip in the docket. "
       "The release also states SALCOS stage one as a DRI plant, an electric arc "
       "furnace and a 100 MW electrolyser, in operation from end-2025.",
  firmness="contract", firmness_basis=
  "Castellanza, Buttrio, May 24, 2023 - A consortium comprising Tenova , "
  "Danieli and DSD Steel Group has been contracted by Salzgitter AG to "
  "build a direct reduction plant (DRP) on the site of Salzgitter "
  "Flachstahl GmbH.")
E("tenova", "LKAB", "framework_agreement", "supplier", "supplier_press",
  V + "lkab-selects-energironr-its-demonstration-plant-northern-sweden", "2024-02-12",
  quantity=(1350000, "tonnes DRI per year"), country="SE", sector="iron ore / steel",
  site="Gällivare",
  note="BASIC ENGINEERING ONLY — 'future equipment supply and construction are pending "
       "waiting for prerequisites like environmental permits and Final Investment "
       "Decision'. Combines HYBRIT with ENERGIRON. The register holds hybrit-pilot-"
       "lulea, which is the pilot at Luleå and not this demonstration plant at "
       "Gällivare.")
E("tenova", "RINA (Hydra project)", "equipment_order", "supplier", "supplier_press",
  V + "tenova-joins-rinas-100-hydrogen-fueled-hydra-project-backed-european", "2024-03-20",
  quantity=(7, "tonnes per hour"), country="IT", sector="steel research",
  note="A 30 m hydrogen DRI tower and an EAF for a PILOT plant, EU-backed. Seven "
       "tonnes per hour at full capability within 2025.",
  firmness="intent", firmness_basis=
  "Castellanza, March 20, 2024 - Tenova , a leading developer and provider "
  "of sustainable solutions for the green transition of the metals "
  "industry, is partnering with RINA , a multinational engineering "
  "consultancy, inspection, and certification company, on the ambitious "
  "European Commission -backed Hydra project . The €88M project is funded "
  "by the European Commission’s NextGenerationEU and backed…")
E("tenova", "Hüttenwerke Krupp Mannesmann (HKM)", "equipment_order", "supplier",
  "supplier_press", V + "tenova-supply-germanys-largest-electric-arc-furnace-hkms-"
                        "transformation", "2026-08-03",
  quantity=(2500000, "tonnes steel per year"), country="DE", sector="steel",
  site="Duisburg",
  note="'the largest in Germany and one of the largest in Europe'. HKM's new owner is "
       "Salzgitter AG — the register holds Salzgitter's own SALCOS row and not HKM, so "
       "this is a second Duisburg steelworks outside the perimeter beside "
       "thyssenkrupp's. The site alias 'Duisburg' would have matched tkh2steel-"
       "duisburg, which is a different company's plant in the same city.",
  refuse_match="'Duisburg' is a site alias of tkh2steel-duisburg and it is a CITY. HKM "
               "and thyssenkrupp Steel are two different works in it.",
  firmness="contract", firmness_basis=
  "Castellanza, August 3, 2026 - Tenova , a leading developer and provider "
  "of sustainable solutions for the green transition of the metals "
  "industry, will supply the Electric Arc Furnace (EAF) for the "
  "transformation of Hüttenwerke Krupp Mannesmann (HKM) in Duisburg, "
  "Germany, into a low-emission steelmaking plant.")

# =============================================================================
# battery_equipment
# =============================================================================
#
# THE WHOLE KIND IS ALMOST EMPTY, AND THAT IS THE FINDING. Three suppliers were
# swept and they produced one European edge between them. The brief asked that a
# supplier publishing no English-language order announcements be written down
# rather than filled in from press; two of these three go further than that — one
# was liquidated and one refuses a reader at the door.

# --- Wuxi Lead Intelligent Equipment Co., Ltd. --------------------------------
# leadintelligent.com/en/news paginates to eight pages and lists 117 English items
# over the period, all listed and their titles read. THE ENGLISH NEWSROOM IS
# MARKETING, not an order book: product launches, trade-fair appearances, chairman
# interviews, technology explainers and awards. Seventeen mention Europe or a
# customer at all and exactly ONE names a European customer and a contract.
#
# Wuxi Lead is listed in Shenzhen and files in Chinese; this sweep reads English,
# and what it can say is about the English record and not about the company.
U = "https://www.leadintelligent.com/en/"

E("wuxi-lead", "FAAM – Energy Saving Battery (Seri Industrial S.p.A.)", "equipment_order",
  "supplier", "supplier_press",
  U + "lead-intelligent-equipment-signs-major-contract-with-faam-to-deliver-advanced-"
      "end-of-line-lithium-battery-production-solution-for-8-gwh-facility-in-italy/",
  "2025-04-28", quantity=(8, "GWh per year"), country="IT", sector="battery cells",
  site="Teverola 2 Naples",
  note="An end-of-line solution for the Teverola 2 plant near Naples. The 8 GWh is the "
       "FACILITY's capacity as the title states it, not the value of the equipment "
       "order — the release does not size the order. FAAM is not a row in the "
       "register's battery perimeter.",
  firmness="contract", firmness_basis=
  "Lead Intelligent Equipment is proud to announce the signing of a major "
  "contract with FAAM – Energy Saving Battery, a subsidiary of Seri "
  "Industrial S.p.A., to provide a state-of-the-art end-of-line (EOL) "
  "solution for FAAM’s new Teverola 2 facility near Naples, Italy. The "
  "Teverola 2 plant will feature multiple high-efficiency lithium iron "
  "phosphate (LFP) battery production lines and is expected…")

# --- Manz AG ------------------------------------------------------------------
# ZERO EDGES, AND NOT BECAUSE NOBODY LOOKED. manz.com's sitemap lists sixteen posts
# and all sixteen were fetched. Every one of them is an insolvency notice or a
# disposal: the December 2024 filing, the opening of proceedings, the sale of the
# core business to Tesla Automation, of Slovakia to Greatech, of Asia in a
# management buy-out and of the US business to ekvip automation. There is no
# customer announcement left on the site at all, because there is no longer a
# company to have made one. A search that returns nothing here is not a thin sweep.
Z = "https://www.manz.com/post/"

R_.status_event(
    "manz", "2025-01-10", "listed (Prime Standard)", "insolvent",
    Z + "manz-ag-provides-information-on-the-current-status-of-the-preliminary-"
        "insolvency-proceedings", "supplier_press",
    "'Manz AG's insolvency filing in December 2024 had become necessary because the "
    "company had built up expertise at an early stage and invested heavily in "
    "expanding capacities' — the company's own account of why. The filing itself is "
    "December 2024 and is not on the site; this is the earliest document that is.")
R_.status_event(
    "manz", "2025-01-23", "insolvent", "moved to General Standard",
    Z + "manz-ag-is-going-to-switch-from-the-prime-standard-to-the-general-standard",
    "supplier_press", "Listing segment change during the proceedings.")
R_.status_event(
    "manz", "2025-02-25", "moved to General Standard",
    "insolvency proceedings opened; core business sold to Tesla Automation GmbH",
    Z + "manz-ag-opening-of-insolvency-proceedings", "supplier_press",
    "Purchase agreement signed with Tesla Automation GmbH of Prüm, a subsidiary of "
    "Tesla, Inc. The battery-equipment supplier was bought by a battery-cell maker "
    "this register holds a row for — tesla-gruenheide-cells.")
R_.status_event(
    "manz", "2025-02-28", "insolvency proceedings opened; core business sold to Tesla "
    "Automation GmbH", "Slovak subsidiary sold to Greatech; Asian business sold in a "
    "management buy-out", Z + "manz-ag-sells-subsidiary-in-slovakia", "supplier_press",
    "Two disposals announced the same day; the Asia sale is in a separate release.")
R_.status_event(
    "manz", "2025-04-24", "Slovak subsidiary sold to Greatech; Asian business sold in a "
    "management buy-out", "sales to Tesla, Greatech and the Asia buy-out completed",
    Z + "manz-ag-completes-sales-to-tesla-greatech-and-asia-management-buy-out",
    "supplier_press", "Closing conditions all fulfilled.")
R_.status_event(
    "manz", "2025-07-11", "sales to Tesla, Greatech and the Asia buy-out completed",
    "US subsidiary sold to ekvip automation GmbH",
    Z + "manz-ag-sells-subsidiary-in-the-usa-to-ekvip-automation-gmbh", "supplier_press",
    "The last disposal on the site.")

# --- Hitachi, Ltd. ------------------------------------------------------------
# ZERO EDGES, AND THE SWEEP COULD NOT GET IN. The perimeter names "Hitachi", and the
# group unit that makes battery production equipment is Hitachi High-Tech, whose
# newsroom (hitachi-hightech.com/global/en/about/news/) and sitemap both answer 403
# to a declared reader carrying a full browser header set. The group's corporate
# press page at hitachi.com/en/press/ answers 200 and lists FIVE items — the most
# recent five — with no archive a reader can walk and no year index (the obvious
# /en/press/archive/<year>/ and /New/cnews/<year>/ paths are 404).
#
# So: no European battery-equipment order was found, and the reason is that the two
# places one would be announced are a 403 and a five-item page. That is a different
# fact from a supplier who announced nothing, and the docket says which this is.

# =============================================================================
# co2_storage_or_transport
# =============================================================================

# --- Northern Lights JV DA ----------------------------------------------------
# 86 news items in the WordPress sitemap, all fetched and read. Northern Lights
# sells transport and storage AS A SERVICE, so its edges run the other way from
# every other node here: the counterparty is an emitter buying storage, and the
# edge_kind is co2_storage. Quantities are tonnes of CO2 a year throughout, which
# makes this the one node kind whose edges CAN be summed against its own stated
# capacity — see the arithmetic section of the docket.
N_ = "https://norlights.com/news/"

# A STORE'S CAPACITY IS A DATED LIST AND THE DATES DECIDE THE ARITHMETIC. One
# release states both phases and the availability of each, so both are recorded
# with `phase` and `available_from`, and the four contracts below are summed
# against the phase whose availability date each one states. Done that way, the
# +890,000 t/yr overshoot the first pass reported is not there — it was four
# contracts summed against one phase, two of which do not start until the other
# phase opens. The workings are in the docket's arithmetic section.
C("northern-lights", 1500000, "tonnes CO2 per year", "nameplate", "supplier",
  "supplier_press", N_ + "northern-lights-is-expanding-capacity-through-commercial-"
                         "agreement/", "2025-03-27",
  phase="phase 1", available_from="2024",
  note="Phase 1 capacity, stated in the release that announces its expansion. 'Ready "
       "to receive CO2 from 2024, Northern Lights is the first company to offer "
       "commercial CCS services', and the same release says operations start in the "
       "summer of 2025 with Heidelberg Materials' Brevik cement works.")
C("northern-lights", 5000000, "tonnes CO2 per year", "nameplate", "supplier",
  "supplier_press", N_ + "northern-lights-is-expanding-capacity-through-commercial-"
                         "agreement/", "2025-03-27",
  phase="phase 2", available_from="2028",
  note="Phase 2, 'a minimum of 5 million tonnes'. 'The expansion is expected to be "
       "completed and ready for operation in the second half of 2028.' FID taken on "
       "the strength of the Stockholm Exergi agreement announced in the same release — "
       "the expansion and the contract that justified it are one document, and that "
       "contract runs from 2028, which is this phase and not the one before it.")

E("northern-lights", "Climeworks", "framework_agreement", "supplier", "supplier_press",
  N_ + "climeworks-and-northern-lights-to-jointly-explore-direct-air-capture-and-"
       "co2-storage-in-norway/", "2021-03-09", quantity=None, country="CH",
  sector="direct air capture")
E("northern-lights", "Borg CO2", "framework_agreement", "supplier", "supplier_press",
  N_ + "collaboration-with-borg-co2-on-carbon-capture-and-storage/", "2021-04-16",
  quantity=None, country="NO", sector="industrial cluster")
E("northern-lights", "Future Biogas", "framework_agreement", "supplier",
  "supplier_press", N_ + "northern-lights-signs-memorandum-of-understanding-mou-with-"
                         "future-biogas/", "2021-06-25", quantity=None, country="GB",
  sector="biogas")
E("northern-lights", "Aker Carbon Capture", "framework_agreement", "supplier",
  "supplier_press", N_ + "aker-carbon-capture-and-northern-lights-jv-to-collaborate-"
                         "on-accelerating-the-carbon-capture-and-storage-market-"
                         "through-full-value-chain-offerings/", "2022-02-17", quantity=None, country="NO",
  sector="capture technology",
  note="Non-exclusive MoU. Aker Carbon Capture is the slb-capturi node on this "
       "perimeter — a capture supplier and a storage supplier agreeing to sell "
       "together, which is a supply-chain edge and not demand on either.")
E("northern-lights", "CCB Energy Holding", "framework_agreement", "supplier",
  "supplier_press", N_ + "ccb-energy-and-northern-lights-collaboration-on-co2-"
                         "management-in-oygarden/", "2022-04-22", quantity=None,
  country="NO", sector="industrial services", site="Øygarden")
E("northern-lights", "Cory", "framework_agreement", "supplier", "supplier_press",
  N_ + "cory-and-northern-lights-announce-pioneering-international-carbon-partnership/",
  "2022-05-13", quantity=None, country="GB", sector="energy from waste",
  note="MoU to ship CO2 from Cory's energy-from-waste operations on the Thames.")
E("northern-lights", "Eramet Norway", "framework_agreement", "supplier",
  "supplier_press", N_ + "eramet-norway-and-northern-lights-announce-collaboration/",
  "2022-08-09", quantity=(260000, "tonnes CO2 per year"), country="NO",
  sector="manganese smelting", site="Sauda",
  note="MoU; capture of 70% of the smelter's emissions, an estimated 260,000 t/yr, "
       "full-scale from 2028. The capture technology named is Air Liquide's Cryocap — "
       "a third node on this perimeter inside one MoU.")
E("northern-lights", "Yara", "co2_storage", "supplier", "supplier_press",
  N_ + "major-milestone-for-decarbonising-europe/", "2022-08-29", quantity=None,
  country="NL", sector="ammonia and fertiliser", site="Sluiskil",
  note="Main commercial terms agreed — 'the world's first commercial agreement on "
       "cross border CO2 transport and storage'. No tonnage in this release; the "
       "binding agreement fifteen months later states 800,000 t/yr.",
  firmness="contract", firmness_basis=
  "Yara and Northern Lights have signed the world’s first commercial "
  "agreement on cross border CO 2 transport and storage.")
E("northern-lights", "Ørsted", "co2_storage", "supplier", "supplier_press",
  N_ + "northern-lights-enters-into-cross-border-transport-and-storage-agreement-with-"
       "orsted/", "2023-05-15", quantity=(430000, "tonnes CO2 per year"), country="DK",
  sector="bioenergy", site="Asnæs Avedøre",
  note="Transport and Services Agreement, effective 1 January 2026, for ten years. "
       "THE PAGE DATE WAS NEARLY WRONG: its own dateline is 'May 15, 2023' in a line "
       "the paragraph filter drops, and the body says 'The agreement is effective from "
       "1 January 2026' — which the date heuristic picked up as the page date. Read by "
       "hand, corrected by hand. The same Asnæs and Avedøre stations are SLB Capturi's "
       "2023-06-15 capture order: both halves of one chain are on this perimeter.",
  firmness="contract", firmness_basis=
  "Today May 15th, Northern Lights JV and Ørsted announce the signing of a "
  "CO 2 Transport and Services Agreement (TSA) to store 430,000 tonnes "
  "biogenic CO 2 emissions per year from two power plants in Denmark.")
E("northern-lights", "Yara International", "co2_storage", "supplier", "supplier_press",
  N_ + "northern-lights-and-yara-signs-binding-agreement-on-co2-transport-and-storage/",
  "2023-11-20", quantity=(800000, "tonnes CO2 per year"), country="NL",
  sector="ammonia and fertiliser", site="Sluiskil",
  note="BINDING agreement, from 2026. The commercial terms of August 2022 made firm.",
  firmness="contract", firmness_basis=
  "On the opening day of European Hydrogen Week, Northern Lights and Yara "
  "International signed a binding commercial transport and storage "
  "agreement with the ambition to capture and store 800 ,000 tonnes CO 2 "
  "from the ammonia production in Sluiskil from 2026.")
E("northern-lights", "Stockholm Exergi", "co2_storage", "supplier", "supplier_press",
  N_ + "northern-lights-is-expanding-capacity-through-commercial-agreement/",
  "2025-03-27", quantity=(900000, "tonnes CO2 per year"), country="SE",
  sector="bioenergy", site="Stockholm",
  note="Up to 900,000 t/yr of biogenic CO2 for 15 years from 2028. The same Stockholm "
       "BECCS plant whose liquefaction unit Air Liquide supplies — capture, "
       "liquefaction and storage each sold by a different node on this perimeter.",
  firmness="contract", firmness_basis=
  "In relation to the expansion investment decision, Northern Lights today "
  "announces the signing of a commercial cross-border transport and storage "
  "agreement with the Swedish district energy provider Stockholm Exergi to "
  "store up to 900,000 tonnes biogenic CO 2 emissions per year for 15 years "
  "starting from 2028 as part of the large-scale Bio-Energy Carbon Capture "
  "and Storage (BECCS) project.")
E("northern-lights", "Inherit", "co2_storage", "supplier", "supplier_press",
  N_ + "northern-lights-has-injected-first-co%e2%82%82-from-wastewater/", "2026-03-24",
  quantity=None, country="NO", sector="biogas / carbon removal",
  note="A pilot: first CO2 from Inherit injected.",
  firmness="contract", firmness_basis=
  "In addition, the Northern Lights JV has signed commercial agreements "
  "with Yara in the Netherlands, Ørsted in Denmark, Stockholm Exergi in "
  "Sweden, and Inherit in Norway.")

# --- Porthos CO2 Transport & Storage C.V. -------------------------------------
# 77 English items in the WordPress sitemap, all fetched and read. Porthos is a
# joint venture of EBN, Gasunie and the Port of Rotterdam Authority, and its
# newsroom is overwhelmingly construction progress: drilling under seawalls, pipe
# pulls, compressor stations, contractor profiles. THE CUSTOMER SIDE IS ONE
# DOCUMENT, and it contracts the whole store at once.
O = "https://www.porthosco2.nl/en/"

C("porthos", 2500000, "tonnes CO2 per year", "nameplate", "supplier", "supplier_press",
  O + "first-co2-storage-project-in-the-netherlands-is-launched/", "2023-10-18",
  note="'Porthos plans to store about 2.5 Mton per year for 15 years, totalling around "
       "37 Mton. With that, Porthos has contracted its full storage capacity.' A store "
       "that is SOLD OUT at FID — the clearest case on this perimeter of demand "
       "meeting a stated capacity exactly, and the reason the arithmetic section can "
       "say something about this node.")

E("porthos", "Air Liquide", "co2_storage", "supplier", "supplier_press",
  O + "rotterdam-companies-and-porthos-sign-contracts-for-transport-and-storage-of-co2/",
  "2021-12-20", quantity=None, country="NL", sector="industrial gases",
  site="Rotterdam",
  note="One of four final contracts signed the same day for a COMBINED 2.5 Mt/yr; the "
       "release does not split the tonnage between the four, so no quantity is "
       "recorded on any of them. Air Liquide is also a node on this perimeter.",
  firmness="contract", firmness_basis=
  "Air Liquide, Air Products, ExxonMobil and Shell signed the final "
  "contracts with Porthos for the transport and storage of CO 2 .")
E("porthos", "Air Products", "co2_storage", "supplier", "supplier_press",
  O + "rotterdam-companies-and-porthos-sign-contracts-for-transport-and-storage-of-co2/",
  "2021-12-20", quantity=None, country="NL", sector="industrial gases", site="Rotterdam",
  note="Second of the four. Combined 2.5 Mt/yr, unsplit.",
  firmness="contract", firmness_basis=
  "Air Liquide, Air Products, ExxonMobil and Shell signed the final "
  "contracts with Porthos for the transport and storage of CO 2 .")
E("porthos", "ExxonMobil", "co2_storage", "supplier", "supplier_press",
  O + "rotterdam-companies-and-porthos-sign-contracts-for-transport-and-storage-of-co2/",
  "2021-12-20", quantity=None, country="NL", sector="refining", site="Rotterdam",
  note="Third of the four. Combined 2.5 Mt/yr, unsplit.",
  firmness="contract", firmness_basis=
  "Air Liquide, Air Products, ExxonMobil and Shell signed the final "
  "contracts with Porthos for the transport and storage of CO 2 .")
E("porthos", "Shell", "co2_storage", "supplier", "supplier_press",
  O + "rotterdam-companies-and-porthos-sign-contracts-for-transport-and-storage-of-co2/",
  "2021-12-20", quantity=None, country="NL", sector="refining", site="Rotterdam",
  note="Fourth of the four. Combined 2.5 Mt/yr, unsplit. Shell's Pernis capture plant "
       "was welded to the Porthos main line in March 2026.",
  firmness="contract", firmness_basis=
  "Air Liquide, Air Products, ExxonMobil and Shell signed the final "
  "contracts with Porthos for the transport and storage of CO 2 .")

# --- Aramis CCS ---------------------------------------------------------------
# 65 news items fetched and read. ZERO CUSTOMER EDGES, and the reason is the stage:
# Aramis is pre-FID, and its entire newsroom is permitting, tendering, subsidy
# schemes, appeals and engineering explainers. No emitter has signed anything this
# sweep can read. The one counterparty document is a cross-border MoU.
Y = "https://www.aramis-ccs.com/news/"

E("aramis", "an unnamed group of European energy companies", "framework_agreement",
  "supplier", "supplier_press",
  Y + "european-energy-leaders-sign-mou-to-develop-major-cross-border-co2-infrastructure-"
      "between-germany-and-the-netherlands/", "2026-06-10", quantity=None,
  note="MoU on cross-border CO2 infrastructure between Germany and the Netherlands. "
       "The counterparties are not named in the headline text this sweep read.")

# --- Project Greensand / Greensand Future -------------------------------------
# projectgreensand.com now resolves to greensandfuture.com; 43 news items fetched
# from the live site and read. Much of the early record is in DANISH, which this
# sweep reads only as far as its slugs — the brief's instruction about a supplier
# publishing no English announcements applies in a milder form here: Greensand
# publishes in both, and the 2023 first-injection sequence is mostly Danish.
G_ = "https://greensandfuture.com/news/"

E("greensand", "Öresundskraft Kraft & Värme AB", "co2_storage", "supplier",
  "supplier_press",
  G_ + "oresundskraft-and-ineos-led-project-greensand-sign-agreement-to-store-210-000-ton",
  "2025-04-14", quantity=(210000, "tonnes CO2 per year"), country="SE",
  sector="energy from waste / district heating",
  note="An agreement to INVESTIGATE storing up to 210,000 t/yr from Sweden in Denmark "
       "from 2028; Öresundskraft's capture side has EUR 54m from the EU Innovation "
       "Fund. Cross-border, like Northern Lights' Yara and Stockholm Exergi deals.",
  firmness="intent", firmness_basis=
  "Öresundskraft Kraft & Värme AB and INEOS on behalf of Project Greensand "
  "have signed an agreement to investigate the opportunity to store up to "
  "210,000 tonnes of CO 2 annually from Sweden in Denmark.")

# --- Ravenna CCS (Eni / Snam) -------------------------------------------------
# eni.com's media index renders by script and its CCS pages moved; the launch
# release was located by search and fetched directly. The capture side of phase 1
# is MHI's, and both halves are on this perimeter.
C("ravenna-ccs", 25000, "tonnes CO2 per year", "nameplate", "supplier",
  "supplier_press",
  "https://www.eni.com/en-IT/media/press-release/2024/09/eni-snam-launch-ravenna-css-"
  "italy-s-first-carbon-capture-storage-project.html", "2024-09-03",
  phase="phase 1", available_from="2024",
  note="Phase 1, in operation: CO2 from Eni's Casalborsetti gas treatment plant, stored "
       "3,000 m down in the depleted Porto Corsini Mare Ovest field. Capture efficiency "
       "over 90%, peaks of 96%.")
C("ravenna-ccs", 4000000, "tonnes CO2 per year", "nameplate", "supplier",
  "supplier_press",
  "https://www.eni.com/en-IT/media/press-release/2024/09/eni-snam-launch-ravenna-css-"
  "italy-s-first-carbon-capture-storage-project.html", "2024-09-03",
  phase="phase 2", available_from="2030",
  note="Phase 2, 'up to 4 million tonnes of CO2 per year by 2030'. A 2030 target stated "
       "in 2024, 160 times phase 1, and recorded beside it rather than instead of it.")

E("ravenna-ccs", "Eni", "co2_storage", "supplier", "supplier_press",
  "https://www.eni.com/en-IT/media/press-release/2024/09/eni-snam-launch-ravenna-css-"
  "italy-s-first-carbon-capture-storage-project.html", "2024-09-03",
  quantity=(25000, "tonnes CO2 per year"), country="IT", sector="oil and gas",
  site="Casalborsetti Ravenna",
  note="THE STORE'S ONLY CUSTOMER IS ITS OWN PARENT. Phase 1 stores Eni's own emissions "
       "from its own gas plant, and Eni is half the joint venture that owns the store. "
       "Recorded as an edge because it is a stated storage relationship; whether an "
       "emitter storing with itself is demand is a ruling for the reader.",
  firmness="contract", firmness_basis=
  "Claudio Descalzi, CEO of Eni, commented: “A project of great "
  "significance for decarbonisation has now become an industrial reality.")

# --- Northern Endurance Partnership / Endurance store -------------------------
# 34 posts on netzeroteesside.co.uk fetched; 32 readable. NEP is a joint venture of
# bp, Equinor and TotalEnergies and shares a newsroom with NZT Power, the gas-fired
# power station that is its anchor customer. THE NEWSROOM IS ABOUT THE SUPPLY CHAIN,
# not about emitters: contractor awards, apprenticeships, quay upgrades, supplier
# spotlights. No emitter contract with a tonnage appears anywhere in it.
NZ = "https://www.netzeroteesside.co.uk/news/"

E("endurance-nep", "Net Zero Teesside Power", "co2_storage", "supplier",
  "supplier_press", NZ + "greenlight-for-net-zero-teesside-power/", "2024-12-10",
  quantity=None, country="GB", sector="power",
  note="Financial close and entry into execution for both NZT Power and NEP. NEP's "
       "infrastructure will 'serve three initial carbon capture projects on Teesside'; "
       "the other two are not named here and no tonnage is given for any of them.",
  firmness="contract", firmness_basis=
  "Net Zero Teesside Power (NZT Power) announces entry into execution "
  "phase, creating and supporting thousands of jobs. NZT Power aims to be "
  "the world’s first gas-fired power station with carbon capture and "
  "storage, providing flexible, low-carbon power to the UK grid. Start-up "
  "expected in 2028, supporting the UK Government’s Clean Power 2030 "
  "ambition. NZT Power today announced financial close and…")

# --- Danieli & C. Officine Meccaniche S.p.A. ----------------------------------
# danieli.com ANSWERS 403 TO EVERY PATH, with and without www, http and https, with
# a full browser header set. Its releases are therefore read from the Internet
# Archive under DECISION D-7 — and the archive is rate-limiting this sweep hard
# enough that only a fraction of the 107 captures identified were retrieved in the
# time available. THE SWEEP OF THIS NODE IS PARTIAL AND SAYS SO. Danieli also
# reaches this file from the other side: it co-developed ENERGIRON with Tenova and
# is named in the Salzgitter SALCOS consortium by Tenova's own release.
#
# BOTH CAPTURES CARRY A DATELINE AFTER ALL. The first pass dated them by year, and
# the D-7 re-read of 11 September 2026 found the day on each: danieli.com prints
# the category, then the date, then the headline, in one run of text that reads as
# navigation until you look for it. `captured_at` now holds the capture and `date`
# holds the release's own dateline, which is what D-7 asks of every archived copy.
D_ = "https://web.archive.org/web/"

E("danieli", "Acciaierie Venete", "equipment_order", "supplier", "supplier_press",
  D_ + "20250214112716id_/https://www.danieli.com/en/news-media/news/acciaierie-venete-"
       "contracts-danieli-eaf-green-steel-production_37_939.htm", "2025-02-03",
  quantity=None, country="IT", sector="steel", site="Padova",
  note="A 100-tonne EAF with fume treatment and material handling for Padova Works. "
       "Recorded on the D-8 boundary because the release's own headline calls it green "
       "steel production; it names no decarbonisation programme and no tonnage, and it "
       "is the weakest edge of its kind in this file. DATE CORRECTED in the D-7 "
       "re-read: the capture's own header reads 'new orders 2025, 3rd February', so "
       "this is a day and not the year the first pass gave it.",
  firmness="contract", firmness_basis=
  "Danieli will supply Acciaierie Venete with a new, 100-ton electric-arc "
  "furnace complete with new fume-treatment plant and material handling "
  "system, to be installed at Padova Works, in Italy. The new furnace will "
  "allow Acciaierie Venete to produce approx.")
E("danieli", "ABS Sisak", "equipment_order", "supplier", "supplier_press",
  D_ + "20220627234645id_/https://www.danieli.com/en/news-media/news/abs-sisak-secure-"
       "competitive-and-green-steel-production-croatia_37_723.htm", "2022-05-23",
  quantity=None, country="HR", sector="steel", site="Sisak",
  note="TWO CORRECTIONS FROM THE D-7 RE-READ. The capture's header reads 'corporate "
       "information 2022, 23rd May', which is a dateline and a day; and the body is "
       "readable after all, though it is a ministerial visit to Cargnacco and an "
       "expansion announcement rather than an order — which is why the firmness here "
       "is intent and not contract. Nothing is claimed about what was sold.",
  firmness="intent", firmness_basis=
  "ABS SISAK to secure competitive and green steel production in Croatia A "
  "significant technological breakthrough and expansion of the current "
  "plant Acciaierie Bertoli Safau is taking an important step to ensure a "
  "promising future of steel production in Croatia with its subsidiary ABS "
  "Sisak. Today, Cargnacco’s plant in Italy was the focus of a visit by two "
  "ministers of economics, the Italian…")

# --- SMS group GmbH -----------------------------------------------------------
# ZERO EDGES FROM THE SUPPLIER'S OWN VOICE. sms-group.com sits behind an AWS WAF
# that answers a declared reader with HTTP 202 and a 2 KB JavaScript challenge —
# not a refusal a reader can argue with and not a page. Its sitemap.xml is the same
# challenge. The Internet Archive holds 325 captures of /press-media/press-detail/
# in the period, and they are overwhelmingly 2020–2022 conventional millwork; none
# of SMS's large European decarbonisation orders is among them.
#
# SO THE COMPANY IS PRESENT IN THIS FILE ONLY THROUGH OTHER PEOPLE'S DOCUMENTS:
# Midrex names Paul Wurth, an SMS group company, in both the H2 Green Steel and the
# thyssenkrupp Duisburg contracts, and names 'the SMS group in consortium with
# Midrex' as holding the largest single order in thyssenkrupp Steel's history. Those
# are edges on the midrex node and they are not duplicated here, because the sweep
# records the speaker and Midrex is the speaker. What SMS itself said, this sweep
# could not read.

# --- Shell Cansolv ------------------------------------------------------------
# ZERO EDGES, AND THE REASON IS ALREADY IN THE REGISTER. shell.com answers a
# declared reader with HTTP 200 and an EMPTY BODY — sources/manual/MANIFEST.json
# records exactly this for two hydrogen rows and queues them for a person with a
# browser. Every Cansolv path tried here returns either 404 or 200-with-nothing:
# /what-we-do/oil-and-natural-gas/cansolv.html, the catalysts-and-technologies
# licensed-technologies pages, the newsroom index, and the resources-library page
# that a search engine still indexes by title.
#
# The one European owner-side source located — humberzero.co.uk's announcement that
# Shell Catalysts & Technologies would provide CANSOLV at VPI Immingham — is a dead
# domain: every path on it now answers 404. So the supplier cannot be read and the
# customer's own site is gone.
#
# This node is on the perimeter and it has been searched. It has no edges because
# nothing about it is readable, which is a different finding from a supplier with no
# European customers, and the report says which.


# =============================================================================
# How deep the sweep went, node by node
# =============================================================================
# `listed` is what the index or sitemap offered; `fetched` is what was retrieved in
# full; `read` is what a person put eyes on. A node whose `blocked` is not empty
# could not be swept as intended and the reason is stated, because "no edges" and
# "no access" are the two findings this sweep must never let a reader confuse.

def _s(node, listed, fetched, index, blocked=None, note=None):
    R_.searched(node, listed=listed, fetched=fetched, index=index,
                blocked=blocked, note=note)

_s("nel", 573, 166, "nelhydrogen.com/press-releases/ over 58 listing pages")
_s("itm-power", 133, 133, "itm-power.com/sitemap.xml",
   note="The sitemap lists 12 items for 2021 and 11 for 2022 against 20 for 2020; the "
        "RNS record on the investors/news page may hold items this sweep did not see.")
_s("tk-nucera", 93, 93, "thyssenkrupp-nucera.com TYPO3 sitemap",
   note="Article pages carry no date; every date comes from the listing page.")
_s("siemens-energy", 353, 353, "siemens-energy.com global/en sitemap, /press-releases/",
   note="22 of the 353 concern electrolysis; the rest are turbines, grids and wind and "
        "are counted, not read.")
_s("sunfire", 100, 100, "sunfire.de sitemap, /en/news/")
_s("plug-power", 317, 317, "ir.plugpower.com Q4 feed, one call per year, bodyType=1",
   blocked="plugpower.com answers 403 to every /press-releases/news-details/ URL; the "
           "feed the same site publishes answers 200 with the same text.")
_s("john-cockerill", 1060, 118, "two news sitemaps",
   note="118 fetched on slug keywords; the newsroom prints no date and every date "
        "comes from schema.org datePublished.")
_s("mcphy", 125, 23, "Internet Archive CDX of mcphy.com/en/press-releases/*",
   blocked="mcphy.com does not resolve; www.mcphy.com redirects to John Cockerill. The "
           "supplier's own site no longer exists (DECISION D-7).",
   note="21 of 23 captures carry a readable body; one is navigation only.")
_s("aker-carbon-capture", 14, 14, "capturi.slb.com sitemap, the successor's host",
   blocked="akercarboncapture.com RESOLVES (35.187.120.37) and serves nothing: nginx "
           "answers 404 over http and the https certificate does not match the name. "
           "That is a different refusal from a domain that has gone, and the earlier "
           "line saying it does not resolve was wrong. Every release this node signed "
           "is read from capturi.slb.com, the acquirer's host.",
   note="Fourteen edges, all signed 'Aker Carbon Capture' between April 2023 and April "
        "2024, all inherited by slb-capturi from 14 June 2024. The 2020–2022 releases, "
        "which include the Brevik award itself, are on neither host.")
_s("slb-capturi", 49, 49, "capturi.slb.com sitemap plus slb.com newsroom",
   blocked="slbcapturi.com HAS NO ADDRESS RECORD and therefore resolves nowhere on "
           "slb.com — checked 11 September 2026, and it is not abandoned: the domain's "
           "nameservers are dns0/dns1.slb.com and dns0/dns1.slb.net, so SLB holds it "
           "and publishes no host for it. capturi.slb.com answers 200 and is the home "
           "this file records.",
   note="The surviving archive starts in 2023; the 2020–2022 Aker Carbon Capture "
        "releases, which include the Brevik award itself, are on neither domain.")
_s("mhi", 836, 125, "mhi.com year index pages 2020–2026",
   note="The 6,334 /news/ URLs in the sitemap are date slugs carrying no words, so the "
        "year index pages were parsed for titles instead. 106 of 836 concern CO2.")
_s("shell-cansolv", 0, 0, "shell.com",
   blocked="shell.com answers 200 with an empty body to a declared reader — the failure "
           "sources/manual/MANIFEST.json already records for two hydrogen rows. Every "
           "Cansolv path returns 404 or nothing. humberzero.co.uk, the one European "
           "owner source located, now 404s on every path.")
_s("linde", 278, 31, "linde.com sitemap, /news-and-media/")
_s("air-liquide", 1809, 74, "airliquide.com sitemap pages 1 and 2")
_s("midrex", 175, 175, "midrex.com press-release and news sitemaps",
   note="The whole newsroom, taken whole.")
_s("primetals", 588, 327, "primetals.com/en sitemap")
_s("tenova", 171, 83, "tenova.com sitemap, /newsroom/press-releases and /news")
_s("danieli", 107, 9, "Internet Archive CDX of danieli.com news paths",
   blocked="danieli.com answers 403 on every path, http and https, with and without "
           "www, with a full browser header set. The archive is rate-limiting the "
           "sweep; 9 of 107 identified captures were retrieved.",
   note="PARTIAL. This node is the least swept on the perimeter.")
_s("sms-group", 325, 0, "Internet Archive CDX of sms-group.com press-detail paths",
   blocked="sms-group.com sits behind an AWS WAF answering 202 with a JavaScript "
           "challenge, sitemap included. The archive's 325 captures are 2020–2022 "
           "millwork and hold none of SMS's European decarbonisation orders.",
   note="Present in this file only through Midrex's releases, where Midrex is the "
        "speaker.")
_s("wuxi-lead", 117, 1, "leadintelligent.com/en/news, eight pages",
   note="All 117 titles read; the English newsroom is marketing, and one item names a "
        "European customer and a contract.")
_s("manz", 16, 16, "manz.com blog-posts sitemap",
   note="All sixteen are insolvency notices or disposals. There is no customer "
        "announcement left on the site.")
_s("hitachi", 5, 0, "hitachi.com/en/press/",
   blocked="hitachi-hightech.com — the group unit that makes battery production "
           "equipment — answers 403 on its newsroom and its sitemap. The corporate "
           "press page lists five items with no walkable archive; /en/press/archive/"
           "<year>/ and /New/cnews/<year>/ are 404.")
_s("northern-lights", 86, 86, "norlights.com WordPress sitemap")
_s("porthos", 77, 77, "porthosco2.nl post sitemap, /en/ items")
_s("aramis", 65, 65, "aramis-ccs.com/news",
   note="Pre-FID: permitting, tendering, subsidy and engineering. No emitter contract.")
_s("greensand", 43, 43, "greensandfuture.com/news",
   note="projectgreensand.com now resolves to greensandfuture.com. Much of the 2023 "
        "first-injection record is in Danish and was read only as far as its slugs.")
_s("ravenna-ccs", 2, 2, "eni.com press release located by search",
   blocked="eni.com's media index renders by script and the CCS pages have moved; the "
           "launch release was reached directly rather than by walking an index.")
_s("endurance-nep", 34, 32, "netzeroteesside.co.uk post sitemap",
   note="Shared newsroom with NZT Power. Contractor awards and supply-chain news; no "
        "emitter contract with a tonnage anywhere in it.")


# =============================================================================
# What the sweep can and cannot say about each node — the rulings of
# 11 September 2026
# =============================================================================
# Three records, all of them things a reader would otherwise have to take from
# prose: whether this node's capacity and its edges can be subtracted at all,
# where the supplier's own figure and this file's sum disagree, and whether the
# sweep of the node finished.

_nc = R_.not_comparable

# --- The units clash: the node states a capacity and it is in another unit ----
_nc("nel", "MW/yr", "MW", "A factory rate against a plant size, and then three more "
    "units besides: nel's edges carry MW, 'H2Station fuelling station', 'H2Station "
    "fuelling system' and 'hydrogen fuelling site', because four releases said four "
    "things and nothing is converted. Six years of orders minus an annual rate is not "
    "a number.")
_nc("itm-power", "MW/yr", "MW", "2,753.5 MW of edges against 1,500 MW/yr of factory. "
    "Six years of orders against an annual rate; subtracting one from the other would "
    "be meaningless. The single most common obstacle in this file.")
_nc("siemens-energy", "MW/yr", "MW", "A factory rate against plant sizes.")
_nc("mcphy", "MW/yr", "MW", "A gigafactory rate against plant sizes — and the rate was "
    "never reached: the company's assets were sold by a commercial court two and a "
    "half years after the figure was stated.")
_nc("john-cockerill", "MW", "MW", "THE UNITS MATCH AND THE BASES DO NOT. The node's one "
    "figure is 'close to 200 megawatts' SOLD IN 2021 — a year's sales, filed as "
    "delivery_commitment because the vocabulary has no value for it — and the edges "
    "are plant sizes across six years. Same unit, different question, and the docket "
    "flags the missing basis value rather than subtracting them.")
_nc("slb-capturi", "carbon capture plants", "tonnes CO2 per year",
    "A COUNT OF THINGS AGAINST A RATE. 'Seven carbon capture plants', then 'eight' "
    "nineteen months later, against edges in tonnes of CO2 a year. Plants cannot be "
    "divided into tonnes.")
_nc("mhi", "commercial facilities", "tonnes CO2 per year",
    "'13 commercial facilities' against 2,450,000 tonnes of CO2 a year. The same "
    "obstacle as slb-capturi and for the same reason.")
_nc("porthos", "tonnes CO2 per year", None,
    "THE UNITS WOULD MATCH IF THE EDGES CARRIED A QUANTITY. The store is contracted to "
    "exactly its nameplate and says so — 'Porthos has contracted its full storage "
    "capacity' — but the release gives one combined 2.5 Mt/yr for four customers and "
    "does not split it, so all four edges carry no quantity and the sum cannot be "
    "built from them. A store sold out with an unsplit customer list.")

# --- The node states no capacity at all, which is a different obstacle --------
for _nid, _eu, _why in [
    ("plug-power", "MW", "Publishes gigawatts of pipeline and no line rate."),
    ("aker-carbon-capture", "tonnes CO2 per year",
     "Stated no capacity for itself before the business transferred; the two 'carbon "
     "capture plants' counts are the successor's and stay on slb-capturi."),
    ("shell-cansolv", None, "Nothing readable at all — see this node's state record."),
    ("linde", "tonnes CO2 per year", "An industrial-gas major that states no capture "
     "capacity of its own."),
    ("air-liquide", "tonnes CO2 per year", "States no capture capacity of its own, and "
     "its edges are in tonnes per DAY (Stockholm Exergi) beside tonnes per YEAR "
     "(Cementir). Not converted."),
    ("midrex", "tonnes DRI per year", "A DRI supplier licenses a process and engineers "
     "a plant; it has no line with a rate, and the tonnages on its edges are its "
     "customers' plants."),
    ("primetals", "tonnes steel per year", "Same as midrex, and its edges mix tonnes of "
     "DRI a year, tonnes of steel a year and tonnes per hour."),
    ("tenova", "tonnes DRI per year", "Same as midrex, and the same mixed units."),
    ("danieli", None, "Same as midrex, and the sweep of it is incomplete besides."),
    ("sms-group", None, "Same as midrex, and no edge in its own voice at all."),
    ("wuxi-lead", "GWh per year", "Its one edge carries the CUSTOMER's facility "
     "capacity, 8 GWh, which is not the size of the equipment order — the release does "
     "not size it."),
    ("manz", None, "Sixteen items on the site, all insolvency notices or disposals."),
    ("hitachi", None, "The unit that makes the equipment refuses a reader."),
    ("aramis", None, "Pre-FID: permitting, tendering, subsidy and engineering, and no "
     "emitter contract."),
    ("greensand", "tonnes CO2 per year", "States no injection rate for itself."),
    ("endurance-nep", None, "Contractor awards and supply-chain news; no emitter "
     "contract with a tonnage anywhere in it."),
]:
    _nc(_nid, None, _eu, "NO STATED CAPACITY. " + _why)

# --- Where the supplier's own figure and this file's sum disagree -------------
# THE SHAPE IS projects.json's `disagreements`: the field, the values, who said
# which and when. NEITHER FIGURE IS CORRECTED. A backlog is a snapshot at a date
# and a sum of announcements is not, and the honest comparison is against the
# edges that existed when the snapshot was taken, split by how firm each one is.
R_.disagreement(
    "tk-nucera", "backlog_mw",
    [{"speaker": "supplier", "value": 1500, "unit": "MW", "date": "2025-08-28",
      "source_url": "https://www.thyssenkrupp-nucera.com/newsroom/news-press-releases/"
                    "thyssenkrupp-nucera-continues-stable-business-development-in-the-"
                    "third-quarter",
      "note": "'engineering orders totaling 1.5 gigawatts', stated in the Q3 report."},
     {"speaker": "eufabric sum of edges", "value": 900, "unit": "MW",
      "date": "2025-08-28",
      "note": "Edges of firmness `contract` dated on or before the backlog's own "
              "as-of date: Shell 200 MW (2022-01-13) and H2 Green Steel 700 MW "
              "(2023-05-22). BELOW the stated backlog, not above it."}],
    "THE +720 MW OVERSHOOT IS NOT THERE ONCE THE DATES AND THE FIRMNESS ARE KEPT. The "
    "first pass summed all six MW edges — 2,220 MW — against a backlog stated on "
    "28 August 2025. Of that, 1,020 MW is framework (Neste 120, Cepsa 300, the "
    "anonymous 600 MW FEED) and 300 MW is a contract signed in March 2026, seven "
    "months AFTER the snapshot. Contracted and already announced when the company "
    "spoke: 900 MW. The two numbers still are not the same number and never were, "
    "which is the finding; the direction of the gap is the opposite of the one "
    "reported.")
R_.disagreement(
    "sunfire", "backlog_mw",
    [{"speaker": "supplier", "value": 800, "unit": "MW", "date": "2024-12-19",
      "source_url": "https://sunfire.de/en/news/sunfire-year-in-review-2024/",
      "note": "'an order backlog exceeding 800 megawatts'."},
     {"speaker": "eufabric sum of edges", "value": 347.5, "unit": "MW",
      "date": "2024-12-19",
      "note": "Eleven edges of firmness `contract` dated on or before the backlog's "
              "own as-of date, from Salzgitter's 0.72 MW in August 2020 to Ren-Gas's "
              "50 MW in November 2024. Includes a 2.6 MW double count: Neste's "
              "MultiPLHY appears as a delivery in 2022 and a start-up in 2025, and "
              "this file records statements rather than a reconciled position."}],
    "THE +310.1 MW OVERSHOOT IS NOT THERE EITHER. Of the 1,110.1 MW the first pass "
    "summed, 550 MW is framework — including a single anonymous 500 MW agreement — and "
    "252.6 MW was announced after the backlog was stated. What Sunfire had announced "
    "as contracts by 19 December 2024 is 347.5 MW against a backlog it put above 800. "
    "A supplier's backlog is bigger than the orders it has named, which is ordinary "
    "and is the opposite of oversubscription.")

# --- Whether the sweep of the node finished, and what the door did ------------
_st = R_.node_state
_st("plug-power", refusal_class="403",
    note="plugpower.com answers 403 to every /press-releases/news-details/ URL. The "
         "same text is in the ir.plugpower.com Q4 feed, which answers 200, and every "
         "Plug edge cites the feed — DECISION D-6. The node is fully swept THROUGH A "
         "SUBSTITUTE, which is not the same as fully swept.")
_st("mcphy", refusal_class="domain_gone",
    note="mcphy.com does not resolve and www.mcphy.com redirects to John Cockerill. "
         "23 of 125 identified captures retrieved, 21 with a readable body.")
_st("aker-carbon-capture", refusal_class="domain_resolves_serves_nothing",
    note="akercarboncapture.com resolves to 35.187.120.37 and serves nothing: nginx "
         "404 over http, a certificate that does not match the name over https. "
         "Checked 11 September 2026. Every edge is read from the successor's host.")
_st("slb-capturi", refusal_class="domain_unaddressed",
    note="slbcapturi.com has NO address record and resolves nowhere on slb.com, but "
         "SLB holds the domain — its nameservers are dns0/dns1.slb.com and "
         "dns0/dns1.slb.net. Checked 11 September 2026. capturi.slb.com answers 200 "
         "and is swept in full; the 2020–2022 releases are on neither.")
_st("shell-cansolv", refusal_class="empty_body_200",
    manual_queue="sources/manual/MANIFEST.json",
    note="TWO REFUSALS, AND THEY ARE DIFFERENT ONES. shell.com answers a declared "
         "reader with HTTP 200 and a document that contains no text at all: the one "
         "Cansolv page this sweep located returns 10,475 bytes of markup and ZERO "
         "characters of readable text, because the article renders client-side. "
         "humberzero.co.uk, the one European owner source located, answers 404 on "
         "every path — a page that is gone rather than a page that will not speak. "
         "The node stands with no capacity and no edges, and joins the manual queue "
         "beside the two Shell hydrogen items already in it.")
_st("danieli", incomplete=True, refusal_class="403",
    note="INCOMPLETE, AND THE LEAST SWEPT NODE ON THE PERIMETER. danieli.com answers "
         "403 on every path, http and https, with and without www, with a full browser "
         "header set; the Internet Archive rate-limits hard enough that 9 of 107 "
         "identified captures were retrieved. Its two edges are a sample of unknown "
         "size and anybody summing this node is summing a sample. NEEDS ITS OWN "
         "THROTTLED RUN, which this batch did not start.")
_st("sms-group", incomplete=True, refusal_class="waf_challenge",
    note="sms-group.com sits behind an AWS WAF answering 202 with a JavaScript "
         "challenge, sitemap included. The archive's 325 captures are 2020–2022 "
         "millwork and hold none of SMS's European decarbonisation orders. ZERO edges "
         "in this supplier's own voice; it reaches this file only through Midrex's "
         "releases, where Midrex is the speaker.")
_st("hitachi", incomplete=True, refusal_class="403",
    note="hitachi-hightech.com — the group unit that makes battery production "
         "equipment — answers 403 on its newsroom and its sitemap. The corporate press "
         "page lists five items with no walkable archive.")
_st("ravenna-ccs", refusal_class="script_rendered_index",
    note="eni.com's media index renders by script and the CCS pages have moved. The "
         "launch release was reached directly rather than by walking an index, so the "
         "node rests on two pages located by search — there may be more and this sweep "
         "cannot say there are not.")

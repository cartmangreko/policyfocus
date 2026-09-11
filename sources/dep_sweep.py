"""The perimeter of the supplier-side dependency sweep, and the machinery that
reads a cached page against it (Brief 9).

The perimeter is FIXED. Node kinds, suppliers and admissible source types are the
brief's, copied here rather than inferred, so that a later re-run reads the same
boundary this run read. Extending it needs a DECISIONS entry in
sources/dependency_docket.md -- which is enforced socially and not by a gate,
because the brief says the ruling is the reader's.

WHY THE MATCHER IS DELIBERATELY DUMB. `matches()` looks for a customer name in a
page and nothing more: it does not decide that a mention is an order, does not
read a quantity, does not rule on whether a framework agreement is demand. Those
are the readings the brief reserves. What it produces is a shortlist for a person
to read, and the count of pages it looked at, which is the difference between a
row searched with nothing found and a row nobody searched.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECTS = ROOT / "data" / "transition" / "projects.json"

# The brief's period: 1 January 2020 to today. The end is the last day the sweep
# fetched anything, not a round number, so a reading dated after it is a reading
# from a page that did not exist when the sweep ran.
PERIOD = ("2020-01-01", "2026-09-11")

# --- the perimeter -----------------------------------------------------------
# node_id, kind, name, home page, listing. `listing` is the supplier's own equity
# status, which decides whether quarterly and annual reports are admissible for it
# at all: an unlisted supplier has no obligation to publish an order backlog, and
# several here do not.
NODES = [
    ("nel", "electrolyser_oem", "Nel ASA", "https://nelhydrogen.com", "listed"),
    ("itm-power", "electrolyser_oem", "ITM Power plc", "https://itm-power.com", "listed"),
    ("tk-nucera", "electrolyser_oem", "thyssenkrupp nucera AG & Co. KGaA",
     "https://thyssenkrupp-nucera.com", "listed"),
    ("siemens-energy", "electrolyser_oem", "Siemens Energy AG",
     "https://www.siemens-energy.com", "listed"),
    ("sunfire", "electrolyser_oem", "Sunfire GmbH", "https://www.sunfire.de", "unlisted"),
    ("plug-power", "electrolyser_oem", "Plug Power Inc.", "https://www.plugpower.com", "listed"),
    ("john-cockerill", "electrolyser_oem", "John Cockerill", "https://johncockerill.com", "unlisted"),
    ("mcphy", "electrolyser_oem", "McPhy Energy S.A.", "https://mcphy.com", "listed"),

    ("slb-capturi", "capture_technology", "SLB Capturi", "https://www.slbcapturi.com", "unlisted"),
    ("mhi", "capture_technology", "Mitsubishi Heavy Industries, Ltd.",
     "https://www.mhi.com", "listed"),
    ("shell-cansolv", "capture_technology", "Shell Cansolv", "https://www.shell.com", "listed"),
    ("linde", "capture_technology", "Linde plc", "https://www.linde.com", "listed"),
    ("air-liquide", "capture_technology", "Air Liquide S.A.", "https://www.airliquide.com", "listed"),

    ("midrex", "dri_plant", "Midrex Technologies, Inc.", "https://www.midrex.com", "unlisted"),
    ("primetals", "dri_plant", "Primetals Technologies", "https://www.primetals.com", "unlisted"),
    ("tenova", "dri_plant", "Tenova S.p.A.", "https://tenova.com", "unlisted"),
    ("danieli", "dri_plant", "Danieli & C. Officine Meccaniche S.p.A.",
     "https://www.danieli.com", "listed"),
    ("sms-group", "dri_plant", "SMS group GmbH", "https://www.sms-group.com", "unlisted"),

    ("wuxi-lead", "battery_equipment", "Wuxi Lead Intelligent Equipment Co., Ltd.",
     "https://www.leadintelligent.com", "listed"),
    ("manz", "battery_equipment", "Manz AG", "https://www.manz.com", "listed"),
    ("hitachi", "battery_equipment", "Hitachi, Ltd.", "https://www.hitachi.com", "listed"),

    ("northern-lights", "co2_storage_or_transport", "Northern Lights JV DA",
     "https://norlights.com", "unlisted"),
    ("porthos", "co2_storage_or_transport", "Porthos CO2 Transport & Storage C.V.",
     "https://www.porthosco2.nl", "unlisted"),
    ("aramis", "co2_storage_or_transport", "Aramis CCS", "https://www.aramis-ccs.com", "unlisted"),
    ("greensand", "co2_storage_or_transport", "Project Greensand / Greensand Future",
     "https://www.projectgreensand.com", "unlisted"),
    ("ravenna-ccs", "co2_storage_or_transport", "Ravenna CCS (Eni / Snam)",
     "https://www.eni.com", "listed"),
    ("endurance-nep", "co2_storage_or_transport",
     "Northern Endurance Partnership / Endurance store", "https://www.netzeroteesside.co.uk",
     "unlisted"),
]

KINDS = sorted({k for _, k, _, _, _ in NODES})
EDGE_KINDS = ["equipment_order", "technology_licence", "framework_agreement",
              "co2_storage", "co2_transport"]
SPEAKERS = ["owner", "supplier", "permit", "grant", "other"]
SOURCE_TYPES = ["supplier_press", "supplier_annual_report", "supplier_quarterly_report",
                "investor_presentation", "owner_press", "permit", "grant_award"]
BASES = ["nameplate", "backlog", "delivery_commitment"]

# Europe as the register already draws it (sources/batteries_docket.md, the
# perimeter prose): the 27, plus the UK, Norway, Switzerland, the Western Balkans
# and Ukraine. Türkiye is outside. Used only to label an unmatched customer.
EUROPE = {
    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV",
    "LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","GB","NO","CH","RS","BA",
    "ME","MK","AL","XK","UA","IS",
}

# Owner-side sectors read on this branch. Hydrogen ("clean") joined the register
# when #54 merged on 11 September 2026 and is in: all 66 rows, none held back.
#
# THE THREE "unreadable, queued" ITEMS ARE NOT ROWS. They are benchmark candidates
# whose duplicate match to a held row is unconfirmed, and the class lands on the
# candidate side in the follow-up to #54. Nothing on the row side is withheld from
# this sweep, and shell-holland-hydrogen-1 takes supplier edges like any other row.
OWNER_SECTORS = ("cement", "steel", "ccs", "batsol", "clean")


def strip(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", strip(s).lower()).strip()


def register_rows() -> list[dict]:
    P = json.loads(PROJECTS.read_text())["projects"]
    return [p for p in P if p["sector"] in OWNER_SECTORS]


def aliases(row: dict) -> dict[str, str]:
    """Every string a supplier might use for this row, and WHICH KIND it is.

    Two kinds, and the distinction is the whole of the matcher's honesty:

      site     the works, the project, the place — "Boden", "GET H2 Nukleus",
               "Tweede Maasvlakte". Naming one of these identifies a row.
      company  the owner — "Uniper", "Shell", "RWE". Naming one of these
               identifies a COMPANY, and a company is not a site.

    THE FIRST VERSION OF THIS DID NOT MAKE THE DISTINCTION AND IT WAS WRONG IN
    PUBLIC. It matched ITM Power's Uniper Humber H2ub contract — a project in the
    United Kingdom — onto `uniper-h2maasvlakte` in Rotterdam, because "Uniper"
    resolved to exactly one row and a one-candidate match looked unambiguous. It
    matched Sunfire's Bad Lauchstädt order onto the same Rotterdam row, and
    Sunfire's Ren-Gas order at Tampere onto Ren-Gas's Pori site. Ambiguity between
    two rows was caught; a confident match to the wrong single row was not, which
    is the worse failure, because it produces a link a reader would believe.

    It also read the shareholders out of a joint venture's name — "Northern Lights
    JV DA (Equinor, Shell, TotalEnergies)" made "Shell" an alias of the CO2 store,
    so every Shell electrolyser contract in Europe pointed at a reservoir under the
    North Sea. A parenthetical is kept only when it holds no comma, which is what
    an alternate name looks like and what a shareholder list does not.
    """
    out: dict[str, str] = {}

    def add(text: str, kind: str) -> None:
        a = norm(text)
        if len(a) > 3 and (a not in out or kind == "site"):
            out[a] = kind

    for field in ("plant", "name"):
        if row.get(field):
            add(row[field], "site")
            # "Tweede Maasvlakte, Rotterdam" is two site names, not one.
            for part in re.split(r"\s*[,/]\s*", row[field]):
                add(part, "site")

    add(row["company"], "company")
    m = re.search(r"\((.*?)\)", row["company"])
    if m and "," not in m.group(1):
        add(m.group(1), "company")
        add(re.sub(r"\s*\(.*?\)", "", row["company"]), "company")
    for owner in row.get("owners") or []:
        if isinstance(owner, dict) and owner.get("name"):
            add(owner["name"], "company")
    return out


def register_index() -> dict[str, tuple[list[str], str]]:
    """alias -> (the project ids it could mean, kind).

    A LIST AND NOT A WINNER. "Automotive Cells Company" names three rows in this
    register and "AESC" names three more; a matcher that resolved either to one id
    would be inventing the site the supplier did not name.
    """
    idx: dict[str, tuple[list[str], str]] = {}
    for row in register_rows():
        for a, kind in aliases(row).items():
            ids, k = idx.get(a, ([], kind))
            if row["id"] not in ids:
                ids = ids + [row["id"]]
            idx[a] = (ids, "site" if "site" in (k, kind) else "company")
    return idx


def matches(text: str, idx: dict[str, tuple[list[str], str]]
            ) -> list[tuple[str, list[str], str]]:
    """(alias, candidate project ids, kind) for every register alias in the text.

    Aliases contained in a longer matched alias are dropped: a page naming
    "Billy-Berclau/Douvrin" has also matched "Douvrin", and reporting both would
    count one mention twice.
    """
    t = f" {norm(text)} "
    hit = [(a, ids, kind) for a, (ids, kind) in idx.items() if f" {a} " in t]
    return sorted((a, ids, kind) for a, ids, kind in hit
                  if not any(a != b and f" {a} " in f" {b} " for b, _, _ in hit))


# --- the title filter --------------------------------------------------------
# Which of a newsroom's several hundred items are fetched in full. It is a filter
# on TITLES ONLY and it is generous: a title that might be about a customer is
# fetched, and the reading happens on the page.
#
# EVERY TERM IS ANCHORED WITH \b, AND THAT IS NOT COSMETIC. The first version of
# this regex dropped "Nel ASA: Receives purchase order for 40 MW electrolyser
# equipment from Bondalti" -- a 40 MW order to a Portuguese chemicals company --
# because the unanchored word `bond`, meant to skip debt announcements, matched
# the customer's name. A filter that silently removes a supplier's third-largest
# European order is worse than no filter, and the only reason it was caught is
# that the customer turned up again in a later listing page.
SIGNAL_TITLE = re.compile(
    r"\border|\bcontract|\baward|\bagreement|\bpurchase|\bdeliver|\bsuppl|"
    r"letter of intent|\bLoI\b|\bMoU\b|memorand|\blicen[cs]|\bselect|\bpartner|"
    r"\bframework|\bcustomer|\bclient|\bFID\b|final investment decision|"
    r"\d[\d.,]*\s?(MW|GW|GWh|kt|Mt|t/y|tpa|tonnes)\b", re.I)

# Corporate-housekeeping items. Anchored, and deliberately short: anything not
# named here is fetched.
NOISE_TITLE = re.compile(
    r"mandatory notification|primary insider|\bshare (buy|repurchas|issue)|"
    r"financial results|\bquarter\b|\binterim report\b|invitation to|"
    r"annual general meeting|\bAGM\b|extraordinary general|\bresign|"
    r"\bappoint|nomination committee|\bproxy\b|voting rights|\bwarrants?\b|"
    r"\bbonds?\b|\bprospectus\b|\bdividend\b|\bwebcast\b|\bIPO\b|"
    r"financial calendar|key information relating", re.I)


def is_candidate(title: str) -> bool:
    return bool(SIGNAL_TITLE.search(title)) and not NOISE_TITLE.search(title)

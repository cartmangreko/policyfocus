"""
Build the graph layer: data/graph/nodes.json + data/graph/edges.json.

This is an ADDITIVE build. It reads what is already in the repo and flattens it
into a graph. It invents no facts, holds no state of its own, and is safe to
re-run: given the same inputs it writes byte-identical output.

Inputs
------
  data/ets.json, data/iaa.json, data/omnibus.json,
  data/cbam.json                                    the measure register
  data/exposure/<slug>.json + _manifest.json        the FIGARO exposure layer
  sources/manifest.json                             the CELEX/act manifest

Outputs
-------
  data/graph/nodes.json
  data/graph/edges.json

Both are deterministically sorted. Nothing is written until every edge endpoint
resolves to a node that exists (see THE RESOLVE GATE below).


NODE KINDS  (exactly four, closed)
==================================
  act:<CELEX>                 a legal act. CELEX is the identifier; there is no
                              other. One placeholder is allowed, see below.
  measure:<file>:<id>         one row of the register. <file> is the register
                              file slug (ets|iaa|omnibus|cbam), <id> the row id
                              (SCP-01, LM-03a, ...).
  sector:<slug>               one of the 14 app sectors.
  country:<ISO2>              a country, plus the single non-country member
                              country:ROW for rest-of-world.

A NOTE ON MEASURE IDS.  The original spec said measure:<file>:<provision_id>.
provision_id cannot carry that role: it is set on only 25 of 146 rows, and it
is not unique -- it is a PROVISION GROUPING key, so two register rows drawn
from the same provision share one (ETS 'ets-10-3', IAA 'PRM-P1' each cover two
rows). Keying on it would both collide and leave 121 rows unaddressable. The
row `id` is unique within its file and present on every row, so it is the key.
provision_id is preserved as a node attribute, which is what makes the
"which rows came from one provision" query answerable without it being the id.


EDGE RELATIONS  (exactly eight, closed)
=======================================
  amends       act -> act         an act amends an earlier act
  repeals      act -> act         an act repeals an earlier act outright. Kept
                                  apart from `amends` because the two say
                                  opposite things about whether the target is
                                  still law, and a reader walking `amends`
                                  would otherwise see a repealed directive as
                                  a live act being modified. A repeal is rarely
                                  total, so the edge carries `survivals` and
                                  `correlation_table` and does not assert that
                                  nothing of the target remains.
  cites        measure -> act     a measure's text names another act
  depends_on   measure -> act     a measure cannot be applied until the target
                                  act exists (definitional dependency)
  contains     act -> measure     an act contains a register row
  applies_to   measure -> sector  a measure reaches a sector
  supplies     sector -> sector   the from-sector is an input to the to-sector
  imports_from sector -> country  the sector draws foreign inputs from there

The first five are legal edges: they come from the register and the manifest.
The last two are ECONOMIC edges: they come from FIGARO and carry view="EU",
so that country-level views can be added later without moving these.


EVERY EDGE CARRIES
==================
  since      when the relation started holding, as a string. Granularity is
             honest, not uniform: "2026" for a proposal known only by its CELEX
             year, "2025-10-20" for a consolidation with a date, "2024" for the
             FIGARO reference year. Never invented to look precise.
  evidence   a pointer back to the exact place the edge was read from --
             {source, path} and, where the edge rests on wording, {quote}.
             An edge you cannot trace is an edge you cannot defend.


THE RESOLVE GATE
================
Nothing is written until every from/to on every edge names a node that exists.
A dangling edge is not a warning here, it is a build failure: a half-written
graph is worse than no graph, because the walk succeeds and quietly omits.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "graph"

REGISTER_FILES = ["ets", "iaa", "omnibus", "cbam", "nzia", "crma", "ppwr"]

# The sector spine is NOT defined here. It lives in data/sectors.json, read by
# this builder and by web/lib/data.ts, so the two sides cannot drift -- the
# arrangement sources/register_files.json already uses. It is two levels deep:
# a sector is a parent, or a child of exactly one parent, and a child exists
# only where a measure applies to the child and not to the parent.
#
# A child does NOT inherit its parent's exposure file. FIGARO separates C22
# (rubber & plastics) from C20 (chemicals), so chem/plastics has its own
# economic profile; a child without a FIGARO code of its own carries no
# exposure at all rather than borrowing one that describes something else.
SECTOR_SPINE = json.loads((DATA / "sectors.json").read_text(encoding="utf-8"))["sectors"]
SECTORS = {slug: meta["name"] for slug, meta in SECTOR_SPINE.items()}
PARENT_OF = {slug: meta["parent"] for slug, meta in SECTOR_SPINE.items()}


def exposure_filename(slug: str) -> str:
    """
    Child slugs carry a slash ("chem/plastics") because that is their URL and
    their identity in the register. Directories do not: the exposure layer is
    one flat folder, so the separator is flattened to "__" for the filename and
    nowhere else. web/lib/exposure.ts does the same, deliberately.
    """
    return f"{slug.replace('/', '__')}.json"

# ---------------------------------------------------------------------------
# CELEX resolution.
#
# Citations in the register appear as human wording ("Directive 2003/87/EC"),
# not as CELEX. Turning wording into CELEX is NOT a safe regex: the sector
# letter (L directive / R regulation / D decision) is not recoverable from the
# number, and guessing it fabricates an identifier that looks authoritative.
# So the map is explicit. Wording that is not in this table produces NO EDGE
# and is reported at the end -- an unmapped citation is a gap to close by
# hand, never a silently invented node.
# ---------------------------------------------------------------------------
CITED_ACTS = {
    ("Directive", "2003/87"): ("32003L0087", "EU ETS Directive"),
    ("Decision", "2015/1814"): ("32015D1814", "Market Stability Reserve Decision"),
    ("Directive", "2009/31"): ("32009L0031", "CCS Directive"),
    ("Directive", "2013/34"): ("32013L0034", "Accounting Directive"),
    ("Directive", "2006/43"): ("32006L0043", "Statutory Audit Directive"),
    ("Directive", "2014/23"): ("32014L0023", "Concessions Directive"),
    ("Directive", "2024/1760"): ("32024L1760", "CSDDD"),
    ("Regulation", "952/2013"): ("32013R0952", "Union Customs Code"),
    ("Regulation", "2015/2446"): ("32015R2446", "Union Customs Code Delegated Regulation"),
    ("Regulation", "2018/858"): ("32018R0858", "Motor Vehicle Type-Approval Regulation"),
    ("Regulation", "2018/1724"): ("32018R1724", "Single Digital Gateway Regulation"),
    ("Regulation", "2019/1020"): ("32019R1020", "Market Surveillance Regulation"),
    ("Directive", "2019/904"): ("32019L0904", "Single-Use Plastics Directive"),
    ("Directive", "94/62"): ("31994L0062", "Packaging and Packaging Waste Directive"),
    ("Directive", "2008/98"): ("32008L0098", "Waste Framework Directive"),
    ("Regulation", "1907/2006"): ("32006R1907", "REACH"),
    ("Regulation", "1935/2004"): ("32004R1935", "Food Contact Materials Regulation"),
    ("Regulation", "2018/2067"): ("32018R2067", "ETS Verification and Accreditation Regulation"),
    ("Regulation", "2019/631"): ("32019R0631", "CO2 Standards for Cars and Vans"),
    ("Regulation", "2019/2088"): ("32019R2088", "SFDR"),
    ("Regulation", "2020/852"): ("32020R0852", "Taxonomy Regulation"),
    ("Regulation", "2020/2092"): ("32020R2092", "Rule of Law Conditionality Regulation"),
    ("Regulation", "2021/1119"): ("32021R1119", "European Climate Law"),
    ("Regulation", "2023/955"): ("32023R0955", "Social Climate Fund Regulation"),
    ("Regulation", "2023/956"): ("32023R0956", "CBAM Regulation"),
    # The environmental and procurement acts the two standing acts' permitting
    # and market-access articles run through. Added when NZIA and CRMA entered
    # the register: 13 citations were being reported unmapped, and every one of
    # them is a real dependency of a permitting or product row.
    ("Directive", "92/43"): ("31992L0043", "Habitats Directive"),
    ("Directive", "94/22"): ("31994L0022", "Hydrocarbons Licensing Directive"),
    ("Directive", "2000/60"): ("32000L0060", "Water Framework Directive"),
    ("Directive", "2001/42"): ("32001L0042", "Strategic Environmental Assessment Directive"),
    ("Directive", "2006/21"): ("32006L0021", "Extractive Waste Directive"),
    ("Directive", "2008/98"): ("32008L0098", "Waste Framework Directive"),
    ("Directive", "2009/147"): ("32009L0147", "Birds Directive"),
    ("Directive", "2010/75"): ("32010L0075", "Industrial Emissions Directive"),
    ("Directive", "2011/92"): ("32011L0092", "Environmental Impact Assessment Directive"),
    ("Directive", "2012/18"): ("32012L0018", "Seveso III Directive"),
    ("Directive", "2014/24"): ("32014L0024", "Public Procurement Directive"),
    ("Directive", "2014/25"): ("32014L0025", "Utilities Procurement Directive"),
    ("Regulation", "139/2004"): ("32004R0139", "EU Merger Regulation"),
    ("Regulation", "2024/1252"): ("32024R1252", "Critical Raw Materials Act"),
    ("Regulation", "2024/1735"): ("32024R1735", "Net-Zero Industry Act"),
    ("Regulation", "2024/1781"): ("32024R1781", "Ecodesign for Sustainable Products Regulation"),
    ("Regulation", "2024/2509"): ("32024R2509", "Financial Regulation (2024 recast)"),
    ("Regulation", "2024/3012"): ("32024R3012", "Carbon Removals Certification Framework"),
    ("Regulation", "2024/3110"): ("32024R3110", "Construction Products Regulation"),
}

# Matches "Directive 2003/87/EC", "Regulation (EU) 2024/1781",
# "Regulation (EU) No 952/2013", with the line breaks the PDF extraction leaves
# behind. Captures the instrument word and the number.
CITATION_RE = re.compile(
    r"\b(Directive|Regulation|Decision)\s*"
    r"(?:\((?:EU|EC|EEC|EU,\s*Euratom)\)\s*)?"
    r"(?:No\s*)?"
    r"(\d{1,4}\s*/\s*\d{2,4})",
    re.IGNORECASE,
)

# The definitional dependency. The IAA applies "low-carbon requirements" to
# procurement, support schemes and labelling, but the thresholds that decide
# what counts as low-carbon for steel, concrete and aluminium are left to
# delegated acts under the ESPR (Reg. 2024/1781) and the CPR (Reg. 2024/3110)
# that do not exist yet -- IAA recital 21 and Art. 24. Every register row that
# turns on the phrase therefore depends on an act that has not been adopted.
# That act gets a placeholder node, because the dependency is real and
# omitting it would make those rows look self-contained.
PENDING_LOWCARBON = "act:pending-ecodesign-lowcarbon"

# The dependency is an IAA construct and only an IAA construct, so the rule is
# scoped to that file. "low-carbon" as a bare phrase is NOT the test: it names
# two unrelated legal concepts across the register, and matching on it alone
# produced two false dependencies --
#
#   ETS MST-02  earmarks auction revenue for a list of purposes that happens to
#               include "lead markets for low-carbon products". A spending
#               purpose is not a threshold to be met.
#   ETS FRE-05  exempts "low-carbon installations" from a plan requirement.
#               That is the ETS's own category of INSTALLATION, set by ETS
#               benchmarks; the ESPR delegated acts define low-carbon PRODUCTS.
#
# What creates the dependency is a provision that makes something turn on
# whether a product qualifies as low-carbon. Those read one of four ways.
LOWCARBON_OPERATIVE = [
    # "low-carbon requirements", and the same thing with the noun qualified:
    # "low-carbon procurement requirements" (LM-04, LM-05).
    re.compile(r"low[\s­-]?carbon\s+(?:\w+\s+){0,2}requirement", re.IGNORECASE),
    re.compile(r"(?:shall|must)\s+be\s+low[\s­-]?carbon", re.IGNORECASE),
    re.compile(r"(?:classified|labelled|labeled)\s*/?\s*(?:or\s+)?(?:labelled\s+)?as\s+low[\s­-]?carbon", re.IGNORECASE),
    re.compile(r"low[\s­-]?carbon[^.]{0,120}Annex\s+I{2,3}", re.IGNORECASE),
]
LOWCARBON_FILES = {"iaa"}

# FIGARO vintage. data/flatfile_eu-ic-io_ind-by-ind_26ed_2024.zip -- 2024
# reference year, edition 26.
FIGARO_SINCE = "2024"
FIGARO_VINTAGE = "FIGARO ind-by-ind, 2024 reference year, ed. 26"

# Rows that close a share list to 100 but name no industry.
NON_INDUSTRY_CODES = {"OTHER"}
# FIGARO's rest-of-world aggregate, which is not a country.
ROW_CODE = "FIGW1"


class BuildError(Exception):
    pass


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def celex_year(celex: str) -> str:
    """Year from a CELEX. 52026PC0616 -> 2026; 02023R0956 -> 2023."""
    m = re.match(r"^[0-9](\d{4})[A-Z]", celex)
    if not m:
        raise BuildError(f"cannot read a year out of CELEX {celex!r}")
    return m.group(1)


CONSOLIDATED_RE = re.compile(r"^0(\d{4}[A-Z]\d{4})(?:-(\d{8}))?$")


def base_celex(celex: str) -> tuple[str, str | None]:
    """Collapse a consolidated CELEX onto the act it consolidates.

    CELEX sector 0 is a consolidated TEXT of an act whose own CELEX is sector 3:
    02023R0956 and 32023R0956 are one act, the CBAM Regulation, seen twice. If
    both become nodes the act has two identities, the amends edge lands on one
    and the manifest entry on the other, and the graph quietly says there are
    two CBAMs. Identity is the base act; the consolidation date is an attribute
    of the node, not a different node.

    Returns (base_celex, was_consolidated). The date is not returned separately
    because it is optional in the manifest ("latest" carries none) -- the
    caller keeps the original string, which is the thing worth recording.
    """
    m = CONSOLIDATED_RE.match(celex)
    if not m:
        return celex, False
    return "3" + m.group(1), True


def normalise_citation(number: str) -> str:
    return re.sub(r"\s+", "", number)


def text_of(row: dict) -> str:
    """The fields a citation or a defined term can legitimately appear in."""
    parts = [row.get("article") or "", row.get("duty") or "", row.get("source_text") or ""]
    return "\n".join(parts)


def sentence_around(text: str, match: re.Match) -> str:
    """The sentence a match sits in, for the evidence quote. Trimmed, single-line."""
    start = text.rfind(".", 0, match.start()) + 1
    end = text.find(".", match.end())
    end = len(text) if end == -1 else end + 1
    return re.sub(r"\s+", " ", text[start:end]).strip()


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


class Graph:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: list[dict] = []
        self.unmapped_citations: set[str] = set()

    def add_node(self, node_id: str, kind: str, label: str, **attrs) -> str:
        existing = self.nodes.get(node_id)
        if existing is None:
            self.nodes[node_id] = {
                "id": node_id,
                "kind": kind,
                "label": label,
                **({"attrs": attrs} if attrs else {}),
            }
        elif existing["kind"] != kind:
            raise BuildError(
                f"node {node_id} claimed by two kinds: {existing['kind']} and {kind}"
            )
        return node_id

    def add_edge(self, rel: str, src: str, dst: str, since: str, evidence: dict, **extra):
        edge = {"rel": rel, "from": src, "to": dst, "since": since, "evidence": evidence}
        edge.update(extra)
        self.edges.append(edge)


def act_name(celex: str) -> str | None:
    """The human name CITED_ACTS carries for a CELEX, if it carries one."""
    for cx, name in CITED_ACTS.values():
        if cx == celex:
            return name
    return None


def build() -> Graph:
    g = Graph()
    manifest = load(ROOT / "sources" / "manifest.json")

    # -- act nodes, from the manifest -------------------------------------
    # The manifest is the authority on the acts the pipeline tracks: their
    # CELEX, their status, and what they amend.
    for slug, entry in sorted(manifest.items()):
        celex, consolidated = base_celex(entry["celex"])
        # A proposal is known by its COM number; a standing act has none, and
        # falling straight through to the bare CELEX would have relabelled
        # act:32024R1735 from "Net-Zero Industry Act" to "32024R1735" the
        # moment NZIA entered the manifest -- add_node keeps the FIRST label it
        # is given, and the manifest pass runs before the citation pass that
        # used to supply the name. CITED_ACTS is consulted here for that reason.
        g.add_node(
            f"act:{celex}",
            "act",
            entry.get("com") or act_name(celex) or celex,
            celex=celex,
            kind_of_act=entry["kind"],
            status=entry["status"],
            procedure=entry.get("procedure"),
            manifest_slug=slug,
            consolidated_celex=(entry["celex"] if consolidated else None),
        )

    # -- act nodes, from acts the manifest amends or repeals ---------------
    # These are the prior rules. They are not tracked acts in their own right
    # (the pipeline does not fetch them as primary), but they are real
    # endpoints and the amends and repeals edges need them.
    #
    # `repeals` is spelled out in the manifest rather than derived, because the
    # facts it carries -- the date the repeal bites, which provisions survive
    # it and for how long -- are in the repealing article and nowhere else.
    for slug, entry in sorted(manifest.items()):
        celex, _ = base_celex(entry["celex"])
        for raw in sorted(entry.get("amends", [])):
            target, _c = base_celex(raw)
            known = next(
                (name for (_, _), (cx, name) in CITED_ACTS.items() if cx == target), target
            )
            g.add_node(f"act:{target}", "act", known, celex=target, status="adopted")
            g.add_edge(
                "amends",
                f"act:{celex}",
                f"act:{target}",
                celex_year(celex),
                {"source": "sources/manifest.json", "path": f"{slug}.amends"},
            )

        for target_raw, rec in sorted(entry.get("repeals", {}).items()):
            target, _c = base_celex(target_raw)
            known = next(
                (name for (_, _), (cx, name) in CITED_ACTS.items() if cx == target), target
            )
            # status "repealed" from the date, not "adopted": the node is the
            # one place a reader learns the target stops being law.
            g.add_node(f"act:{target}", "act", known, celex=target,
                       status="repealed", repealed_from=rec["since"])
            g.add_edge(
                "repeals",
                f"act:{celex}",
                f"act:{target}",
                rec["since"],
                {
                    "source": "sources/manifest.json",
                    "path": f"{slug}.repeals.{target_raw}",
                    "quote": rec["quote"],
                },
                survivals=rec.get("survivals", []),
                correlation_table=rec.get("correlation_table"),
            )

    # -- act node for the register files ----------------------------------
    # Every register row names its act by source_url. omnibus is in the
    # register but not in sources/manifest.json (it predates the fetcher), so
    # this is the only place its act node comes from.
    register: dict[str, list[dict]] = {}
    act_of_file: dict[str, str] = {}
    for file_slug in REGISTER_FILES:
        rows = load(DATA / f"{file_slug}.json")
        register[file_slug] = rows

        celexes = {
            m.group(1)
            for r in rows
            # The separator is a literal ":" or its percent-encoding "%3A" --
            # an ALTERNATION, not a character class. As a class, [:%3A] also
            # matches "3", so it swallowed the leading sector digit of any
            # CELEX beginning with 3 and turned "CELEX:32025R0040" into
            # "2025R0040". No act in the register started with 3 until PPWR,
            # which is why this survived six files.
            if (m := re.search(r"CELEX(?::|%3A)?([0-9A-Z]+)", r.get("source_url") or ""))
        }
        if len(celexes) != 1:
            raise BuildError(
                f"{file_slug}.json must name exactly one act by source_url, found {sorted(celexes)}"
            )
        celex, _ = base_celex(celexes.pop())
        act_of_file[file_slug] = celex
        g.add_node(
            f"act:{celex}",
            "act",
            manifest.get(file_slug, {}).get("com") or celex,
            celex=celex,
            status=manifest.get(file_slug, {}).get("status", "proposed"),
            register_file=file_slug,
        )

    # -- the pending-act placeholder --------------------------------------
    g.add_node(
        PENDING_LOWCARBON,
        "act",
        "Pending delegated acts defining low-carbon thresholds",
        celex=None,
        status="not_adopted",
        placeholder=True,
        note=(
            "The IAA applies low-carbon requirements but leaves the thresholds "
            "to delegated acts under Regulation (EU) 2024/1781 (ESPR) and "
            "Regulation (EU) 2024/3110 (CPR) that have not been adopted. This "
            "node stands in for them so the dependency is visible; it carries "
            "no CELEX because there is nothing yet to cite."
        ),
    )

    # -- sector nodes ------------------------------------------------------
    exposure_manifest = load(DATA / "exposure" / "_manifest.json")
    for slug, name in sorted(SECTORS.items()):
        entry = exposure_manifest.get(slug)
        # Parentage is a node ATTRIBUTE, not an edge. The edge set is a set of
        # claims about the world -- who amends whom, who supplies whom -- and
        # "plastics converting is filed under chemicals" is not a claim of that
        # kind, it is how this register files things. Making it an edge would
        # put a taxonomy decision on the same footing as a repeal clause.
        g.add_node(
            f"sector:{slug}",
            "sector",
            name,
            figaro_code=(entry or {}).get("code"),
            has_exposure=entry is not None,
            parent=PARENT_OF[slug],
        )

    # -- measure nodes and the contains edge ------------------------------
    for file_slug in REGISTER_FILES:
        celex = act_of_file[file_slug]
        since = celex_year(celex)
        seen_ids: set[str] = set()
        for row in register[file_slug]:
            rid = row["id"]
            if rid in seen_ids:
                raise BuildError(f"duplicate row id {rid} in {file_slug}.json")
            seen_ids.add(rid)

            node_id = f"measure:{file_slug}:{rid}"
            g.add_node(
                node_id,
                "measure",
                row.get("duty") or rid,
                register_id=rid,
                provision_id=row.get("provision_id"),
                measure_type=row.get("measure_type"),
                direction=row.get("direction"),
                article=row.get("article"),
                addressee_class=row.get("class"),
            )
            g.add_edge(
                "contains",
                f"act:{celex}",
                node_id,
                since,
                {"source": f"data/{file_slug}.json", "path": f"[id={rid}]"},
            )

    # -- applies_to --------------------------------------------------------
    # Two bases, kept apart: a sector the act NAMES is a different claim from
    # a sector the analysis says it REACHES. Collapsing them would let a
    # derived reach read as statutory text.
    for file_slug in REGISTER_FILES:
        for row in register[file_slug]:
            node_id = f"measure:{file_slug}:{row['id']}"
            since = celex_year(act_of_file[file_slug])
            named = set(row.get("sectors_named") or [])
            for slug in sorted(named):
                _require_sector(slug, file_slug, row["id"])
                g.add_edge(
                    "applies_to",
                    node_id,
                    f"sector:{slug}",
                    since,
                    {"source": f"data/{file_slug}.json", "path": f"[id={row['id']}].sectors_named"},
                    basis="named",
                )
            for slug in sorted(set(row.get("sectors_reached") or []) - named):
                _require_sector(slug, file_slug, row["id"])
                g.add_edge(
                    "applies_to",
                    node_id,
                    f"sector:{slug}",
                    since,
                    {
                        "source": f"data/{file_slug}.json",
                        "path": f"[id={row['id']}].sectors_reached",
                    },
                    basis="reached",
                )

    # -- cites -------------------------------------------------------------
    for file_slug in REGISTER_FILES:
        own_celex = act_of_file[file_slug]
        since = celex_year(own_celex)
        for row in register[file_slug]:
            node_id = f"measure:{file_slug}:{row['id']}"
            text = text_of(row)
            hits: dict[str, re.Match] = {}
            for m in CITATION_RE.finditer(text):
                key = (m.group(1).capitalize(), normalise_citation(m.group(2)))
                mapped = CITED_ACTS.get(key)
                if mapped is None:
                    g.unmapped_citations.add(f"{key[0]} {key[1]}")
                    continue
                target = mapped[0]
                if target == own_celex:
                    continue  # an act citing itself is not an edge
                hits.setdefault(target, m)
            for target, m in sorted(hits.items()):
                g.add_edge(
                    "cites",
                    node_id,
                    f"act:{target}",
                    since,
                    {
                        "source": f"data/{file_slug}.json",
                        "path": f"[id={row['id']}]",
                        "quote": sentence_around(text, m)[:400],
                    },
                )
                # A cited act may not otherwise be a node. It is a real act
                # with a real CELEX, so it becomes one.
                label = next(
                    (name for (_, _), (cx, name) in CITED_ACTS.items() if cx == target), target
                )
                g.add_node(f"act:{target}", "act", label, celex=target, status="adopted")

    # -- depends_on --------------------------------------------------------
    for file_slug in REGISTER_FILES:
        if file_slug not in LOWCARBON_FILES:
            continue
        since = celex_year(act_of_file[file_slug])
        for row in register[file_slug]:
            text = text_of(row)
            m = next(filter(None, (p.search(text) for p in LOWCARBON_OPERATIVE)), None)
            if m is None:
                continue
            g.add_edge(
                "depends_on",
                f"measure:{file_slug}:{row['id']}",
                PENDING_LOWCARBON,
                since,
                {
                    "source": f"data/{file_slug}.json",
                    "path": f"[id={row['id']}]",
                    "quote": sentence_around(text, m)[:400],
                },
                basis="low-carbon threshold not yet defined",
            )

    # -- economic edges ----------------------------------------------------
    _economic_edges(g, exposure_manifest)

    return g


def _require_sector(slug: str, file_slug: str, row_id: str):
    if slug not in SECTORS:
        raise BuildError(
            f"{file_slug}.json row {row_id} names sector {slug!r}, which is not one of "
            f"the {len(SECTORS)} app sectors -- add it to SECTORS or fix the register"
        )


def _economic_edges(g: Graph, exposure_manifest: dict):
    """supplies and imports_from, from the FIGARO exposure layer, EU view.

    Both directions of the supply relation are read. cement's supplier list and
    power's customer list are two views of one fact, so the same edge can be
    seen twice; it is emitted once, keeping whichever evidence pointer is
    lexically first so the output stays deterministic.
    """
    # FIGARO code -> app sectors. One-to-many, and that is not a defect to
    # paper over: FIGARO groups steel and aluminium under C24, cement and
    # glass under C23. An edge into C24 is an edge into both sectors, and
    # `shared_figaro_code` on the edge says so, so nobody reads a joint figure
    # as sector-specific.
    slugs_by_code: dict[str, list[str]] = {}
    for slug, entry in sorted(exposure_manifest.items()):
        slugs_by_code.setdefault(entry["code"], []).append(slug)

    supplies: dict[tuple[str, str], dict] = {}
    imports: dict[tuple[str, str], dict] = {}

    for slug in sorted(exposure_manifest):
        path = DATA / "exposure" / exposure_filename(slug)
        data = load(path)
        eu = data["eu"]
        src = f"data/exposure/{exposure_filename(slug)}"

        for i, r in enumerate(eu.get("suppliers", [])):
            if r["code"] in NON_INDUSTRY_CODES:
                continue
            for other in slugs_by_code.get(r["code"], []):
                _put_supply(supplies, other, slug, r, src, f"eu.suppliers[{i}]", slugs_by_code)

        for i, r in enumerate(eu.get("customers", [])):
            if r["code"] in NON_INDUSTRY_CODES:
                continue
            for other in slugs_by_code.get(r["code"], []):
                _put_supply(supplies, slug, other, r, src, f"eu.customers[{i}]", slugs_by_code)

        for i, r in enumerate(eu.get("foreign_input_origins", [])):
            code = r["code"]
            # OTHER closes the named-partner tail to 100. It is a remainder,
            # not a place, and it is NOT the same thing as FIGW1: FIGW1 is
            # FIGARO's own rest-of-world aggregate and does name a (compound)
            # origin, so it earns country:ROW. Turning OTHER into a node would
            # invent a country, and folding it into ROW would double-count
            # against FIGW1. It gets no edge; shares on imports_from therefore
            # do not sum to 100, which is correct -- an edge list is not a table.
            if code in NON_INDUSTRY_CODES:
                continue
            country = "ROW" if code == ROW_CODE else code
            key = (slug, country)
            if key not in imports:
                imports[key] = {
                    "share": r["share"],
                    "evidence": {"source": src, "path": f"eu.foreign_input_origins[{i}]"},
                    "label": r.get("label"),
                }

    # country nodes. Origins give the non-EU partners; by_country gives the 27
    # members. Both are read so a country never appears only as an edge end.
    # country nodes. Origins give the non-EU partners; by_country gives the 27
    # members. Both are read so a country never appears only as an edge end.
    #
    # The 27 members carry no edge yet, and that is by design rather than an
    # oversight: the economic edges here are the EU view, whose foreign origins
    # are extra-EU by construction. They are declared now so the country-view
    # build lands as pure edge addition against nodes that already exist.
    countries: dict[str, tuple[str, bool]] = {"ROW": ("Rest of world", False)}
    for slug in sorted(exposure_manifest):
        data = load(DATA / "exposure" / exposure_filename(slug))
        for r in data["eu"].get("foreign_input_origins", []):
            if r["code"] not in NON_INDUSTRY_CODES and r["code"] != ROW_CODE:
                countries.setdefault(r["code"], (r.get("label") or r["code"], False))
        for iso in data.get("by_country", {}):
            countries.setdefault(iso, (iso, True))
    for iso, (label, in_eu) in sorted(countries.items()):
        g.add_node(
            f"country:{iso}",
            "country",
            label,
            iso2=(None if iso == "ROW" else iso),
            aggregate=(iso == "ROW"),
            in_eu=in_eu,
        )

    for (src_slug, dst_slug), rec in sorted(supplies.items()):
        g.add_edge(
            "supplies",
            f"sector:{src_slug}",
            f"sector:{dst_slug}",
            FIGARO_SINCE,
            rec["evidence"],
            view="EU",
            share_pct=rec["share"],
            share_basis=rec["basis"],
            vintage=FIGARO_VINTAGE,
            **({"shared_figaro_code": rec["code"]} if rec["shared"] else {}),
        )

    for (slug, country), rec in sorted(imports.items()):
        g.add_edge(
            "imports_from",
            f"sector:{slug}",
            f"country:{country}",
            FIGARO_SINCE,
            rec["evidence"],
            view="EU",
            share_pct=rec["share"],
            share_basis="percent of the sector's foreign inputs",
            vintage=FIGARO_VINTAGE,
        )


def _put_supply(store, src_slug, dst_slug, row, source, path, slugs_by_code):
    if src_slug == dst_slug:
        return  # a sector supplying itself is a FIGARO diagonal, not a relation
    key = (src_slug, dst_slug)
    basis = (
        "percent of the receiving sector's total inputs"
        if path.startswith("eu.suppliers")
        else "percent of the supplying sector's total output"
    )
    candidate = {
        "share": row["share"],
        "basis": basis,
        "evidence": {"source": source, "path": path},
        "code": row["code"],
        "shared": len(slugs_by_code.get(row["code"], [])) > 1,
    }
    prev = store.get(key)
    if prev is None or (candidate["evidence"]["source"], path) < (
        prev["evidence"]["source"],
        prev["evidence"]["path"],
    ):
        store[key] = candidate


# ---------------------------------------------------------------------------
# gate + write
# ---------------------------------------------------------------------------


def gate(g: Graph):
    """Nothing is written until this passes."""
    problems: list[str] = []

    kinds = {"act", "measure", "sector", "country"}
    for node in g.nodes.values():
        if node["kind"] not in kinds:
            problems.append(f"node {node['id']} has kind {node['kind']!r}, outside the closed set")
        prefix = node["id"].split(":", 1)[0]
        if prefix != node["kind"]:
            problems.append(f"node {node['id']} is prefixed {prefix!r} but typed {node['kind']!r}")

    allowed = {
        "amends": ("act", "act"),
        "repeals": ("act", "act"),
        "cites": ("measure", "act"),
        "depends_on": ("measure", "act"),
        "contains": ("act", "measure"),
        "applies_to": ("measure", "sector"),
        "supplies": ("sector", "sector"),
        "imports_from": ("sector", "country"),
    }
    for e in g.edges:
        if e["rel"] not in allowed:
            problems.append(f"edge relation {e['rel']!r} is outside the closed set")
            continue
        want_src, want_dst = allowed[e["rel"]]
        for end, want in (("from", want_src), ("to", want_dst)):
            node = g.nodes.get(e[end])
            if node is None:
                problems.append(f"edge {e['rel']} {e['from']} -> {e['to']}: {end} {e[end]} does not resolve")
            elif node["kind"] != want:
                problems.append(
                    f"edge {e['rel']} {e['from']} -> {e['to']}: {end} is a {node['kind']}, expected {want}"
                )
        if not e.get("since"):
            problems.append(f"edge {e['rel']} {e['from']} -> {e['to']} carries no since")
        if not e.get("evidence", {}).get("source"):
            problems.append(f"edge {e['rel']} {e['from']} -> {e['to']} carries no evidence pointer")
        if e["rel"] in ("supplies", "imports_from") and e.get("view") != "EU":
            problems.append(f"economic edge {e['from']} -> {e['to']} carries no view")

    seen = set()
    for e in g.edges:
        key = (e["rel"], e["from"], e["to"], e.get("basis"))
        if key in seen:
            problems.append(f"duplicate edge {key}")
        seen.add(key)

    if problems:
        raise BuildError(
            "the resolve gate failed, nothing written:\n  " + "\n  ".join(problems[:40])
            + (f"\n  ... and {len(problems) - 40} more" if len(problems) > 40 else "")
        )


def write(g: Graph):
    OUT.mkdir(parents=True, exist_ok=True)
    nodes = sorted(g.nodes.values(), key=lambda n: (n["kind"], n["id"]))
    edges = sorted(g.edges, key=lambda e: (e["rel"], e["from"], e["to"], str(e.get("basis") or "")))
    for path, payload in ((OUT / "nodes.json", nodes), (OUT / "edges.json", edges)):
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False, sort_keys=False)
            fh.write("\n")
    return nodes, edges


def main() -> int:
    try:
        g = build()
        gate(g)
    except BuildError as exc:
        print(f"build_graph: {exc}", file=sys.stderr)
        return 1

    nodes, edges = write(g)

    by_kind: dict[str, int] = {}
    for n in nodes:
        by_kind[n["kind"]] = by_kind.get(n["kind"], 0) + 1
    by_rel: dict[str, int] = {}
    for e in edges:
        by_rel[e["rel"]] = by_rel.get(e["rel"], 0) + 1

    print(f"nodes {len(nodes)}: " + ", ".join(f"{k} {v}" for k, v in sorted(by_kind.items())))
    print(f"edges {len(edges)}: " + ", ".join(f"{k} {v}" for k, v in sorted(by_rel.items())))
    if g.unmapped_citations:
        print(
            "\nunmapped citations (no edge emitted; add to CITED_ACTS to resolve):\n  "
            + "\n  ".join(sorted(g.unmapped_citations))
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

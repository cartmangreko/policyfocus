"""Where the sweep's readings are written down, and the two files they become.

    python3 dep_records.py --check       # shape, vocabulary and cache checks
    python3 dep_records.py --build       # write nodes.json / edges.json / unmatched

A READING IS A HAND ENTRY AND IS MEANT TO LOOK LIKE ONE. Nothing in this module is
derived: every edge below is one sentence somebody read in one cached page, and the
url on it is the page. dep_digest.py put the sentence in front of the reader; this
file is what the reader concluded. Keeping the two apart is the point -- the digest
can be regenerated from the cache at any time and will not change what was ruled.

`add_edge` takes the brief's fields and no others, plus `note`, which is declared in
DECISION D-3: several readings are only honest with a sentence saying what was and
was not stated, and a null field cannot carry that.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import dep_sweep as S

HERE = Path(__file__).resolve().parent
EDGES: list[dict] = []
NODE_CAPACITY: dict[str, list[dict]] = {}
UNMATCHED: dict[str, dict] = {}
NODE_STATUS: dict[str, list[dict]] = {}

_IDX: dict[str, list[str]] | None = None


def _idx() -> dict[str, list[str]]:
    global _IDX
    if _IDX is None:
        _IDX = S.register_index()
    return _IDX


def resolve(customer: str, site: str = "") -> tuple[str | None, str | None]:
    """(project_id, note) for a customer and site as the supplier stated them.

    A ROW IS IDENTIFIED BY A SITE, AND A SITE NAME IS NOT ENOUGH ON ITS OWN. Both
    halves of that were learned the hard way:

      * Matching on the company alone linked ITM Power's Uniper contract for the
        Humber, in England, to Uniper's Maasvlakte row in Rotterdam — the only
        Uniper row in the register, and therefore an unambiguous-looking match to
        the wrong site.
      * Matching on the site alone linked Nel's HyCC order at DELFZIJL to
        `lhyfe-delfzijl`, because two different companies are building two
        different plants in the same Dutch town and the town is the site alias of
        one of them.

    So the site says which row and the company is asked to agree with it. Where
    they disagree, or where the site is ambiguous and the company cannot break the
    tie, the edge keeps project_id null and the note says what was seen. Nothing
    here creates a row and nothing here guesses — DECISION D-2.
    """
    hits = S.matches(f"{customer} {site}", _idx())
    sites = sorted({i for _, cand, k in hits if k == "site" for i in cand})
    firms = sorted({i for _, cand, k in hits if k == "company" for i in cand})
    both = [i for i in sites if i in firms]

    if len(both) == 1:
        return both[0], None
    if len(sites) == 1 and not firms:
        # A PLACE NAME ALONE. Right for "Boden", where the supplier used the site's
        # name and the register's company for it is a later rename; wrong for
        # "Dunkirk" and "Aberdeenshire", which are a city and a county and match
        # whichever row happens to stand in them. Every one of these is listed in
        # the docket as a weak match so a reader can see what the link rests on.
        return sites[0], "MATCHED ON A PLACE NAME ALONE: the source names " \
                         f"{sites[0]}'s site but not its company."
    if len(sites) == 1 and firms:
        return None, (f"the site named matches {sites[0]} while the company named "
                      f"matches {', '.join(firms)} — two different rows, so the "
                      "source has not identified one. DECISION D-2")
    if len(sites) > 1:
        named = ", ".join(a for a, _, k in hits if k == "site")
        return None, (f"names {named}, which in this register could be " +
                      " or ".join(sites) + "; the source does not say which — "
                      "DECISION D-2")
    if firms:
        named = ", ".join(a for a, _, k in hits if k == "company")
        return None, (f"names the company {named} but no site this register holds; "
                      "its rows are " + ", ".join(firms) +
                      ". A company is not a site — DECISION D-2")
    return None, None


FRAMEWORK_EN_BLOC = ("edge_kind framework_agreement. Ruled en bloc on 11 September "
                     "2026: a framework agreement is `framework` by its kind and no "
                     "source was re-read for it — DECISION D-14.")


def add_edge(node_id: str, customer: str, edge_kind: str, speaker: str,
             source_type: str, url: str, date: str, date_precision: str = "day",
             quantity: tuple[float, str] | None = None, project_id: str | None = None,
             site: str = "", note: str | None = None, country: str | None = None,
             sector: str | None = None, refuse_match: str | None = None,
             inherited_by: dict | None = None, firmness: str | None = None,
             firmness_basis: str | None = None, no_dateline: bool = False) -> dict:
    # `refuse_match` is the reader overruling the matcher, with the reason. It
    # exists because the matcher can be confidently wrong in a way no rule fixes:
    # Plug Power's release puts European Energy's Måde PtX plant at Måde, Esbjerg,
    # and the register's only Måde row is Copenhagen Infrastructure Partners'
    # HØST PtX. Either they are one project whose ownership two speakers state
    # differently, or they are two plants in one place. A matcher cannot tell, and
    # a link that might be either is worse than no link.
    if refuse_match:
        pid, amb, basis = None, refuse_match, "refused"
    elif project_id:
        pid, amb, basis = project_id, None, "explicit"
    else:
        pid, amb = resolve(customer, site)
        basis = ("site+company" if pid and not amb else
                 "site only" if pid else "unmatched")
    if amb:
        note = f"{note}. {amb}" if note else amb
    # FIRMNESS IS READ, EXCEPT WHERE THE KIND ALREADY SAYS IT. `framework_agreement`
    # is the firmness as well as the kind, so it maps rather than being recorded
    # twice -- DECISION D-14, and the reason the 98 of them needed no re-read.
    if edge_kind == "framework_agreement" and firmness is None:
        firmness, firmness_basis = "framework", FRAMEWORK_EN_BLOC

    captured = capture_date(url)
    if no_dateline:
        # DECISION D-7 as ruled on 11 September 2026: a document that carries no
        # dateline of its own is dated by the copy on file, and that date is an
        # UPPER BOUND -- the release exists at or before it and the file will not
        # say how much before.
        captured = captured or fetched_date(url)
        date, date_precision = captured or date, "capture_upper_bound"

    e = {"id": f"e{len(EDGES) + 1:04d}",
         "project_id": pid,
         "customer_name_as_stated": customer,
         "site_as_stated": site or None,
         "sector": sector,
         "node_id": node_id,
         "edge_kind": edge_kind,
         "firmness": firmness,
         "firmness_basis": firmness_basis,
         "quantity": None if quantity is None else {"value": quantity[0], "unit": quantity[1]},
         "speaker": speaker,
         "source_type": source_type,
         "url": url,
         "date": date,
         "date_precision": date_precision,
         "captured_at": captured,
         "verdict": None,
         "match_basis": basis,
         # THE SUPPLIER'S CUSTOMER THAT THIS REGISTER DOES NOT HOLD. A named site
         # that resolves to no admitted row is demand on the same capacity as a
         # matched one, and the supplier's totals count it -- DECISION D-15. A
         # company named without a site is NOT this: it may well be a row nobody
         # could identify, which is a different fact and stays false here.
         "outside_perimeter": bool(site) and pid is None and basis == "unmatched"
                              and country is not None,
         "inherited_by": inherited_by,
         "note": note}
    EDGES.append(e)
    if pid is None and country is not None:
        u = UNMATCHED.setdefault(customer, {
            "customer_name_as_stated": customer, "country": country,
            "sector_guess": sector, "sources": [], "edge_ids": []})
        if url not in u["sources"]:
            u["sources"].append(url)
        u["edge_ids"].append(e["id"])
    return e


ARCHIVE = re.compile(r"web\.archive\.org/web/(\d{4})(\d{2})(\d{2})\d{6}id_/")


def capture_date(url: str) -> str | None:
    """The date of the copy on file, from the Internet Archive URL itself.

    DECISION D-7, AS RULED ON 11 SEPTEMBER 2026. The capture timestamp is not the
    source date -- `date` keeps the release's own dateline, because that is what
    the sweep period is measured against and a 2020 release captured in 2024 would
    otherwise leave the period. It is a field of its own, `captured_at`, and it
    supersedes the earlier wording that made it the source date.

    IT IS DERIVED, NEVER TYPED. The timestamp is already in the URL, so writing it
    out by hand only creates a second copy that can disagree with the first -- and
    it did, twice, before this function existed. Derived here, it cannot.
    """
    m = ARCHIVE.search(url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def fetched_date(url: str) -> str | None:
    """The date this sweep fetched a live page, from the fetch cache index.

    The other half of D-7, and the narrower half. A document with no dateline is
    dated by the copy on file; where that copy is an archive capture the URL says
    when, and where it is this sweep's own fetch the cache index does. Both are
    upper bounds and both are recorded as `captured_at`, because "when somebody
    could last see this page" is one fact whoever took the copy.
    """
    import hashlib
    import dep_text as T
    e = T.index().get(hashlib.sha1(url.encode()).hexdigest()[:16]) or {}
    at = e.get("fetched_at")
    return at[:10] if at else None


def status_event(node_id: str, date: str, status_from: str | None, status_to: str,
                 source_url: str, source_type: str, note: str,
                 date_precision: str = "day", event_kind: str = "status",
                 evidence_mode: str = "retrospective") -> None:
    """A supplier's own history, in the shape data/transition/projects.json uses.

    SAME SHAPE ON PURPOSE. A supplier is an installation's other half and it has
    the same kind of history: it is founded, it is listed, it is acquired, it goes
    into administration. The register already decided what that record looks like —
    append-only, in date order, every entry carrying a source — and inventing a
    second shape for the same fact would mean two things to read and two gates to
    write. The vocabulary of `status` is the supplier's own and NOT the project
    vocabulary: `operating` says nothing useful about a company.

    It exists because of McPhy. A node whose entire published record vanished from
    the web between one sweep and the next cannot be described by a capacity figure
    and a list of orders; the fact that matters most about it is what happened to
    it, and there was nowhere to put that.
    """
    NODE_STATUS.setdefault(node_id, []).append(
        {"event_kind": event_kind, "date": date, "date_precision": date_precision,
         "status_from": status_from, "status_to": status_to, "status": status_to,
         "source_url": source_url, "source_type": source_type,
         "evidence_mode": evidence_mode, "note": note})


def add_capacity(node_id: str, value: float, unit: str, basis: str, speaker: str,
                 source_type: str, url: str, date: str, date_precision: str = "day",
                 note: str | None = None, phase: str | None = None,
                 available_from: str | None = None) -> None:
    """One figure a node states for itself, with the date it was stated.

    `phase` AND `available_from` ARE WHY A STORE'S CAPACITY IS A DATED LIST. A CO2
    store is not one number: Northern Lights phase 1 could take 1.5 Mt/yr from 2024
    and phase 2 a minimum of 5 Mt/yr from the second half of 2028, and a contract
    signed in 2025 for delivery from 2028 is demand on the second, not the first.
    Summing every contract against the phase 1 nameplate produced an overshoot of
    890,000 t/yr that the dates dissolve -- see the docket's arithmetic section.
    Both fields are null where the source states no phase and no availability date,
    which is most of the file.
    """
    NODE_CAPACITY.setdefault(node_id, []).append(
        {"value": value, "unit": unit, "basis": basis, "phase": phase,
         "available_from": available_from, "speaker": speaker,
         "source_type": source_type, "url": url, "date": date,
         "date_precision": date_precision, "captured_at": capture_date(url),
         "note": note})


NODE_DISAGREEMENT: dict[str, list[dict]] = {}
NODE_COMPARISON: dict[str, dict] = {}
NODE_STATE: dict[str, dict] = {}


def disagreement(node_id: str, field: str, values: list[dict], note: str) -> None:
    """Two speakers, one field, two numbers, and neither is corrected.

    SAME SHAPE AS `projects.json`'s `disagreements`, for the same reason
    status_history has the same shape as the register's: the fact is the same kind
    of fact. A supplier states an order backlog at a date; this file sums the edges
    that supplier announced; the two do not agree. Both values stand with the date
    each was stated on, because a backlog is a snapshot and a sum of announcements
    is not, and deciding which is right is not arithmetic.
    """
    NODE_DISAGREEMENT.setdefault(node_id, []).append(
        {"field": field, "values": values, "note": note})


def not_comparable(node_id: str, node_unit: str | None, edge_unit: str,
                   reason: str) -> None:
    """This node's stated capacity and its edges cannot be subtracted, and why.

    RECORDED RATHER THAN CONVERTED. An edge is a plant of n megawatts; a node
    capacity is a factory that builds n megawatts A YEAR, and six years of orders
    minus an annual rate is not a number. `node_unit` is null where the node states
    no capacity at all, which is a different obstacle from a unit clash and is told
    apart here rather than in prose. No derived figure is written anywhere, and no
    delivery window is assumed.
    """
    NODE_COMPARISON[node_id] = {"comparable": False, "node_unit": node_unit,
                                "edge_unit": edge_unit, "reason": reason}


def node_state(node_id: str, *, incomplete: bool = False,
               manual_queue: str | None = None, refusal_class: str | None = None,
               note: str = "") -> None:
    """What is true of the SWEEP of this node rather than of the node.

    `incomplete` says the sweep did not finish and the node's edges are a sample of
    unknown size -- Danieli, at nine of 107 captures. `manual_queue` names the file
    that will carry what a machine could not fetch, and `refusal_class` says what
    the door did: a 403, a WAF, an empty body, a domain that no longer resolves.
    A reader who sums this file without reading these is summing a sample.
    """
    NODE_STATE[node_id] = {"incomplete": incomplete, "manual_queue": manual_queue,
                           "refusal_class": refusal_class, "note": note or None}


# --- gates and output --------------------------------------------------------

def cites(sentence: str, url: str) -> bool:
    """Is this sentence on that page? Unknown counts as yes."""
    import dep_text as T
    body = T.body(url)
    if body is None:
        return True
    page = re.sub(r"\s+", " ", T.to_text(body))
    return re.sub(r"\s+", " ", sentence).rstrip("\u2026") in page


def check() -> list[str]:
    """Every way a reading can be wrong that a machine can see.

    THE URL CHECK IS THE ONE THAT EARNS ITS KEEP. Every url in dep_readings.py was
    typed by a person from a digest, and a mistyped slug on a supplier's newsroom
    does not 404 loudly in a file -- it sits there looking like a citation. If a url
    is not in the fetch cache with a 200 and a SHA-256, then the page behind this
    reading was never read at this address, and the reading is unsupported.
    """
    import dep_text as T
    idx, bad = T.index(), []
    ok = {e["url"] for e in idx.values() if e.get("sha256")}
    seen_ids = set()
    for e in EDGES:
        w = f"edge {e['id']} ({e['node_id']} / {e['customer_name_as_stated']})"
        if e["id"] in seen_ids:
            bad.append(f"{w}: duplicate id")
        seen_ids.add(e["id"])
        if e["url"] not in ok:
            bad.append(f"{w}: url not in the fetch cache as a 200 — {e['url']}")
        if e["edge_kind"] not in S.EDGE_KINDS:
            bad.append(f"{w}: edge_kind {e['edge_kind']!r} is not in the vocabulary")
        if e["speaker"] not in S.SPEAKERS:
            bad.append(f"{w}: speaker {e['speaker']!r} is not in the vocabulary")
        if e["source_type"] not in S.SOURCE_TYPES:
            bad.append(f"{w}: source_type {e['source_type']!r} is not in the vocabulary")
        if e["date_precision"] not in ("day", "month", "year", "capture_upper_bound"):
            bad.append(f"{w}: date_precision {e['date_precision']!r}")
        if e["date_precision"] == "capture_upper_bound" and e["date"] != e["captured_at"]:
            bad.append(f"{w}: dated as an upper bound but date {e['date']} is not "
                       f"captured_at {e['captured_at']}")
        if e["firmness"] not in S.FIRMNESS:
            bad.append(f"{w}: firmness {e['firmness']!r} is not in the vocabulary")
        if not e["firmness_basis"]:
            bad.append(f"{w}: firmness {e['firmness']!r} with nothing cited for it")
        elif e["firmness_basis"] != FRAMEWORK_EN_BLOC and not cites(e["firmness_basis"], e["url"]):
            # THE CITATION GATE. `firmness` decides whether rung 6 of the
            # confirmation ladder passes, so the sentence it rests on has to be a
            # sentence that is actually on the page. Checked against the cached
            # body, and skipped -- not failed -- where the body is not on this
            # machine, because the bodies are gitignored (D-9) and a clone must
            # still be able to run this.
            bad.append(f"{w}: firmness_basis is not in the cached page — "
                       f"{e['firmness_basis'][:60]!r}")
        if not (S.PERIOD[0] <= e["date"] <= S.PERIOD[1]):
            bad.append(f"{w}: date {e['date']} is outside the sweep period")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["date"]):
            bad.append(f"{w}: date {e['date']!r} is not YYYY-MM-DD")
        if e["node_id"] not in {n[0] for n in S.NODES}:
            bad.append(f"{w}: node_id {e['node_id']!r} is not on the perimeter")
        ib = e.get("inherited_by")
        if ib and ib["node_id"] not in {n[0] for n in S.NODES}:
            bad.append(f"{w}: inherited_by names {ib['node_id']!r}, not on the perimeter")
    for nid, events in NODE_STATUS.items():
        dates = [ev["date"] for ev in events]
        if dates != sorted(dates):
            bad.append(f"status_history on {nid} is not in date order")
        for ev in events:
            if ev["source_url"] not in ok:
                bad.append(f"status_history on {nid} ({ev['date']}): url not in the "
                           f"fetch cache as a 200 — {ev['source_url']}")
            if ev["source_type"] not in S.SOURCE_TYPES:
                bad.append(f"status_history on {nid} ({ev['date']}): source_type "
                           f"{ev['source_type']!r}")
    for nid, caps in NODE_CAPACITY.items():
        for c in caps:
            w = f"capacity on {nid} ({c['value']} {c['unit']})"
            if c["url"] not in ok:
                bad.append(f"{w}: url not in the fetch cache as a 200 — {c['url']}")
            if c["basis"] not in S.BASES:
                bad.append(f"{w}: basis {c['basis']!r} is not in the vocabulary")
            if c["source_type"] not in S.SOURCE_TYPES:
                bad.append(f"{w}: source_type {c['source_type']!r}")
            if c["available_from"] and not re.fullmatch(r"\d{4}(-\d{2}-\d{2})?",
                                                       c["available_from"]):
                bad.append(f"{w}: available_from {c['available_from']!r} is not a year "
                           "or a YYYY-MM-DD date")
    known = {n[0] for n in S.NODES}
    for nid in list(NODE_DISAGREEMENT) + list(NODE_COMPARISON) + list(NODE_STATE):
        if nid not in known:
            bad.append(f"a node record names {nid!r}, which is not on the perimeter")
    for nid, ds in NODE_DISAGREEMENT.items():
        for d in ds:
            if len(d["values"]) < 2:
                bad.append(f"disagreement on {nid} ({d['field']}): one value is not a "
                           "disagreement")
            for v in d["values"]:
                if not v.get("date") or not v.get("speaker"):
                    bad.append(f"disagreement on {nid} ({d['field']}): a value with no "
                               "speaker or no date")
    # A NODE THE SWEEP COULD NOT READ MAY NOT LOOK LIKE ONE IT COULD. `listed`
    # above `fetched` is ordinary -- the title filter does that on every newsroom.
    # A door that refused a reader is not ordinary, and the node has to say so
    # where somebody reading nodes.json will see it without reading prose.
    for nid, sw in SEARCHED.items():
        if sw.get("blocked") and nid not in NODE_STATE:
            bad.append(f"{nid}: swept behind a refusal and carries no node_state "
                       "saying which refusal")
    return bad


SEARCHED: dict[str, dict] = {}     # node_id -> what was swept for it
OWNER: dict[str, dict] = {}        # project id -> owner-side search result


def searched(node_id: str, **kw) -> None:
    SEARCHED[node_id] = kw


def owner(project_id: str, urls_read: int, found: list[str], note: str = "") -> None:
    OWNER[project_id] = {"project_id": project_id, "sources_read": urls_read,
                         "supplier_or_store_named": found, "note": note}


def owner_side() -> list[dict]:
    """The owner-side pass, run rather than transcribed.

    dep_owner scans the sources the register itself cites; calling it here means
    edges.json cannot drift from what that scan actually found, which a pasted list
    would do the first time a row gained a source.
    """
    import dep_owner
    scan = dep_owner.scan()
    out = []
    for pid, r in sorted(scan.items()):
        others = [n for n in r["named"] if n not in r["names_its_own_owner"]]
        out.append({"project_id": pid,
                    "sources_cited": r["cited"],
                    "sources_read": r["read"],
                    "unreadable": r["unreadable"],
                    "supplier_or_store_named": others,
                    "names_its_own_owner": r["names_its_own_owner"]})
    return out


def build() -> None:
    nodes = []
    for nid, kind, name, home, listing in S.NODES:
        nodes.append({"id": nid, "kind": kind, "name": name, "listing": listing,
                      "home": home,
                      "stated_capacity": NODE_CAPACITY.get(nid, []),
                      "status_history": sorted(NODE_STATUS.get(nid, []),
                                               key=lambda e: e["date"]),
                      "disagreements": NODE_DISAGREEMENT.get(nid, []),
                      "comparison": NODE_COMPARISON.get(nid),
                      "state": NODE_STATE.get(nid),
                      "sweep": SEARCHED.get(nid)})
    (HERE / "nodes.json").write_text(
        json.dumps({"_comment": NODES_COMMENT, "nodes": nodes},
                   indent=1, ensure_ascii=False) + "\n")
    (HERE / "edges.json").write_text(
        json.dumps({"_comment": EDGES_COMMENT, "edges": EDGES,
                    "owner_side": owner_side()},
                   indent=1, ensure_ascii=False) + "\n")
    (HERE / "dependency_unmatched.json").write_text(
        json.dumps({"_comment": UNMATCHED_COMMENT,
                    "customers": sorted(UNMATCHED.values(),
                                        key=lambda u: u["customer_name_as_stated"])},
                   indent=1, ensure_ascii=False) + "\n")


NODES_COMMENT = [
    "Suppliers and stores swept for Brief 9, and the capacity each STATES for itself.",
    "",
    "The perimeter is sources/dep_sweep.py:NODES and is fixed by the brief. `listing`",
    "is the node's own equity status, which decides whether an annual or quarterly",
    "report exists for it at all -- eleven of these twenty-seven are unlisted and",
    "publish no order backlog anywhere.",
    "",
    "`stated_capacity` IS A LIST AND IS NOT RECONCILED. A supplier states its capacity",
    "many times over six years and the figures do not agree, because they are answers",
    "to different questions: nameplate is what a line can build, backlog is what has",
    "been sold, delivery_commitment is what has been promised for a date. No value here",
    "is converted, averaged or superseded -- the 2022 Herxya nameplate and the 2025",
    "sentence saying those same lines are idling both stand, and the second is why the",
    "first cannot be read as output.",
    "",
    "`sweep` records what was actually read for this node: the index pages walked, how",
    "many items they listed, how many were fetched, and where the sweep could not go.",
    "A node with sweep null was not searched, which is a different fact from a node",
    "that was searched and yielded nothing.",
    "",
    "`comparison` SAYS WHETHER THE SUMS IN THIS FILE MAY BE SUBTRACTED AT ALL, and for",
    "24 of the 28 nodes the answer is no. Both units are named. `node_unit` null means",
    "the node states no capacity for itself, which is a different obstacle from a unit",
    "clash and is not the same finding. Nothing is converted and no delivery window is",
    "assumed anywhere in this file.",
    "",
    "`disagreements` has the shape projects.json uses: the field, the values, who said",
    "which and when. Two of them, both a supplier's own order backlog against this",
    "file's sum of the contracts it had announced by the date the backlog was stated.",
    "NEITHER FIGURE IS CORRECTED.",
    "",
    "`state` is about the SWEEP, not the node. `incomplete` means the node's edges are",
    "a sample of unknown size -- Danieli, at nine of 107 captures. `refusal_class` says",
    "what the door did, and the four kinds are not interchangeable: a 403, a WAF",
    "challenge, a 200 with no text in it, and a domain that has gone are four different",
    "facts about whether anybody can read this supplier at all.",
]
EDGES_COMMENT = [
    "One edge is one document stating one relationship between a supplier or store on",
    "the perimeter and a customer. Brief 9.",
    "",
    "AN EDGE IS A STATEMENT, NOT A STATE. The same order appears here two or three",
    "times -- as a letter of intent, as a firm contract, as a cancellation -- each with",
    "its own date and speaker, because the brief asks for what was said and not for a",
    "reconciled current position. Summing this file without reading `note` will",
    "double-count, and that is the correct behaviour for a file of statements.",
    "",
    "`quantity.unit` IS THE UNIT AS STATED, never converted. That is why some edges",
    "carry MW, some carry fuelling stations and some carry tonnes of CO2 a year, and",
    "why the docket's arithmetic section can only compare a subset of them.",
    "",
    "`project_id` is null when the customer matches no admitted row, AND when the",
    "customer names a company that holds several rows and the document does not say",
    "which site -- DECISION D-2. The two cases are told apart by `note`.",
    "",
    "`firmness` IS THE SECOND AXIS AND RUNG 6 OF THE LADDER READS IT, NOT `edge_kind`.",
    "contract is a firm order or a signed supply agreement; framework is an agreement",
    "with no named site or no quantity; intent is an MoU, a study, a pre-FEED or a",
    "selection the document itself calls conditional. `firmness_basis` is the sentence",
    "it was read off, quoted from the page at `url`, and a gate refuses any edge whose",
    "cited sentence is not in the cached body. The 98 framework_agreement edges are the",
    "one exception: their kind already says their firmness, so it is mapped rather than",
    "read twice, and the basis says so -- DECISION D-14.",
    "",
    "`captured_at` IS NOT THE SOURCE DATE. `date` is the release's own dateline, which",
    "is what the sweep period is measured against; `captured_at` is when the copy on",
    "file was taken, derived from the Internet Archive URL or from this sweep's own",
    "fetch. Where a document has no dateline at all, and only there, the two are the",
    "same and `date_precision` says `capture_upper_bound`: the release exists at or",
    "before that date and this file will not say how much before -- DECISION D-7.",
    "",
    "`outside_perimeter` is a named site that resolves to no admitted row. It is demand",
    "on the same supplier capacity as a matched edge and the supplier's totals count",
    "it -- DECISION D-15. A company named without a site is NOT this, because it may",
    "be a row nobody could identify, and that edge carries false.",
    "",
    "`verdict` is null on every edge in this file. It is the reader's field.",
    "",
    "`owner_side` is the other direction: every admitted row whose own cached sources",
    "were re-read for supplier and store names. `supplier_or_store_named` empty means",
    "searched and none found. A row absent from this list was not searched.",
]
UNMATCHED_COMMENT = [
    "Customers a supplier named that match no admitted row in data/transition/projects.json.",
    "",
    "NO ROWS WERE CREATED. The brief is explicit and the reason is the perimeter: a",
    "cement customer that this register does not hold may be out of scope, or may be a",
    "gap, and a sweep of suppliers is not the instrument that decides which. `country`",
    "and `sector_guess` are what the supplier's own release says or implies, so that a",
    "later pass can sort these without re-reading every page.",
    "",
    "An UNDISCLOSED customer is not here. 'an undisclosed European client' is a customer",
    "nobody named, not a customer nobody matched, and putting it in this file would",
    "turn the supplier's silence into a candidate.",
]


if __name__ == "__main__":
    # THE DOCSTRING PROMISED THESE TWO AND THE MODULE DID NOT HAVE THEM. Both
    # commands worked in the only way anybody had actually run them -- by importing
    # dep_readings and calling build() -- and `python3 dep_records.py --build`
    # exited 0 having done nothing at all, which is the worst way for a build to
    # fail. Here they are.
    import sys

    # RUN AGAINST THE IMPORTED MODULE, NOT AGAINST __main__. `python3
    # dep_records.py` makes this file the module `__main__`, and dep_readings
    # imports `dep_records` -- a second module object with a second, empty EDGES.
    # Calling check() here would check nothing and build() would write an empty
    # file, which is what the first version of this block did.
    import dep_records as M
    import dep_readings  # noqa: F401  -- importing it IS the reading pass

    argv = sys.argv[1:] or ["--check"]
    problems = M.check()
    for line in problems:
        print(line, file=sys.stderr)
    if problems:
        print(f"{len(problems)} problem(s).", file=sys.stderr)
        raise SystemExit(1)
    if "--build" in argv:
        M.build()
        print(f"{len(M.EDGES)} edges, {len(M.NODE_CAPACITY)} nodes with a stated capacity.")
    else:
        print(f"{len(M.EDGES)} edges check out.")

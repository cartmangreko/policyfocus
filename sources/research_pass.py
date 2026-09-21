#!/usr/bin/env python3
"""THE RE-SEARCH PASS OVER FOUR SECTORS, brief 14.

    python3 sources/research_pass.py --plan            # the 164 entries and their targets
    python3 sources/research_pass.py --search [--limit N] [--sector S]
    python3 sources/research_pass.py --report          # what was read, what it names
    python3 sources/research_pass.py --queue           # the browser queue, consolidated
    python3 sources/research_pass.py --queue-csv       # …as sources/manual/browser_queue.csv

WHAT THIS IS. The audit of 20 September re-searched thirty entries drawn at random from
the 164 classed `searched none found` or `named not admitted` in hydrogen, batteries,
cement and transport and storage, and four changed class — all of them found by starting
at the owner's own domain rather than at the list's citations. Four of thirty is above the
brief's threshold of two, so this is the full pass over all 164.
sources/ladder_research_audit.json is the audit; this is the pass it triggered.

THE SEARCH ORDER IS THE RULE, AND IT IS S3's. "Where a works has an owner with a newsroom,
that is where the search should start" — ruled 16 September after Tata Steel Port Talbot
was admitted on the first request having failed sixteen wiki citations. So for every entry
this pass asks the owner's own domain FIRST and the list's citations second, which is the
opposite of what the original censuses did.

EVERY SEARCH IS RECORDED, including the ones that find nothing. The fetch itself lands in
the sector's cache index with its URL, day, byte count and SHA-256; this file records
WHICH ENTRY each fetch was made for, in what order, and what the text contained. A search
nobody can reconstruct is a search nobody can check, and "searched, none found" is a claim
about a search.

NOTHING HERE WRITES A CLASS. The standing rule of 21 September: no rule changes until this
pass and the supplier sweep are in, and a case the rules do not settle goes to the
questions file with the entry held. What this pass produces is a record, a signal per
entry, and a browser queue. A person classes.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ladder_population as lp  # noqa: E402

ROOT = lp.ROOT
OUT = ROOT / "sources" / "research_pass_14.json"

READERS = {"hydrogen": "hydrogen_search", "batteries": "battery_search",
           "cement": "ccs_search", "transport and storage": "ccs_search"}
CACHE = {"hydrogen": "hydrogen", "batteries": "batteries", "cement": "ccs",
         "transport and storage": "ccs"}

# THE PATHS AN OWNER'S NEWSROOM LIVES AT, in the order S3 implies: the site itself,
# then where a company puts what it has announced. Hand-listed rather than guessed
# per host, so the same order is asked of every owner and the pass is comparable
# across 164 entries.
PATHS = ("", "/news", "/en/news", "/press", "/en/press", "/media", "/newsroom",
         "/en", "/about", "/projects")
MAX_PER_ENTRY = 4

# HOSTS THAT ARE NOT THE OWNER. A list's citation, an encyclopedia, a trade title or
# an aggregator is where the original censuses started and where S3 says not to.
NOT_THE_OWNER = re.compile(
    r"gem\.wiki|wikipedia|web\.archive\.org|iea\.org|globalenergymonitor|"
    r"industrytransition|linkedin|twitter|facebook|youtube|google|bing|"
    r"kallanish|steelorbis|gmk\.center|offshore-energy|battery-news|"
    r"hydrogeninsight|rechargenews|reuters|bloomberg|spglobal|argusmedia|"
    r"globenewswire|prnewswire|businesswire|yahoo|europa\.eu", re.I)


def load():
    if OUT.exists():
        return json.loads(OUT.read_text(encoding="utf-8"))
    return {"_comment": __doc__.strip().splitlines(), "started": "2026-09-21",
            "search_order": "S3 — the owner's own domain first, the list's citations second",
            "entries": {}}


def save(doc):
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def hydrogen_entries():
    """The hydrogen population's two re-searchable classes, from the gated CSV, with
    the admission search's own record for each."""
    gap = {str(e["ref"]): e for e in json.loads(
        (ROOT / "sources" / "hydrogen_gap_search.json").read_text(encoding="utf-8"))["entries"]}
    out = []
    with open(ROOT / "sources" / "ladder" / "all.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["sector"] != "hydrogen":
                continue
            if r["register_class"] not in ("none found", "named not admitted"):
                continue
            g = gap.get(r["list_key"], {})
            urls = [f.get("url") for f in (g.get("fetches") or []) if f.get("url")]
            out.append({"key": r["key"], "sector": "hydrogen", "name": r["name"],
                        "klass": r["register_class"], "country": r["country"],
                        "company": g.get("company") or "", "known_urls": urls})
    return out


def sector_entries(sector):
    pop, _ = lp.BUILDERS[sector]()
    S = json.loads((ROOT / "sources" / "steel_entries.json").read_text(encoding="utf-8"))
    out = []
    for e in pop:
        if e["register_class"] not in ("searched none found", "named not admitted"):
            continue
        a = e.get("admission") or {}
        urls = list(a.get("looked_in_order") or [])
        if a.get("source"):
            urls.append(a["source"])
        # THE BATTERY CENSUS RECORDED NO URLs AND NAMED THE DOMAINS IN PROSE.
        # "svolt-eu.com answers 200 with an empty body", "inobat.eu answers 200 and
        # does not name Valladolid", "bmz-group.com names Karlstein am Main exactly
        # once, in the imprint". Reading a host out of the census's own note is
        # reading the record; inventing one from a company name is not, and D-S4
        # forbids the second. So the note is parsed for a bare domain and nothing
        # else is.
        note = " ".join(str(a.get(k) or "") for k in ("failed_leg", "verbatim"))
        for c in e.get("list_claims") or []:
            note += " " + str(c.get("note") or "")
        for host in re.findall(r"\b([a-z0-9][a-z0-9-]{2,}(?:\.[a-z0-9-]{2,})*"
                               r"\.(?:com|eu|net|org|de|fr|es|it|nl|se|fi|no|dk|pl|be|uk))\b",
                               note.lower()):
            urls.append("https://" + host)
        out.append({"key": e["key"], "sector": sector, "name": e["name"],
                    "klass": e["register_class"], "country": e.get("country", ""),
                    "company": "", "known_urls": [u for u in urls if str(u).startswith("http")]})
    return out


def population():
    out = hydrogen_entries()
    for s in ("batteries", "cement", "transport and storage"):
        out += sector_entries(s)
    return out


def owner_hosts(e):
    """THE OWNER'S DOMAIN, from what the register already holds about the entry.

    A host the entry's own records point at, minus the ones S3 says not to start
    from. No guessing from a company name: a domain invented out of a name is a name
    match wearing a URL, which is the thing sources/steel_docket.md D-S4 forbids.
    """
    seen, out = set(), []
    for u in e["known_urls"]:
        try:
            h = urllib.parse.urlsplit(u).netloc.lower()
        except ValueError:
            continue
        if not h or h in seen or NOT_THE_OWNER.search(h):
            continue
        seen.add(h)
        out.append(h)
    return out


def targets(e):
    hosts = owner_hosts(e)
    if not hosts:
        return []
    h = hosts[0]
    return [f"https://{h}{p}" for p in PATHS][:MAX_PER_ENTRY]


def names_it(text, e):
    """A SIGNAL AND NOT A FINDING. Whether the owner's page contains the distinctive
    words of the entry's own name — which is where a person then looks."""
    words = [w for w in re.split(r"[^A-Za-zÀ-ÿ0-9]+", e["name"]) if len(w) > 4]
    words = [w for w in words if w.lower() not in
             ("plant", "steel", "green", "hydrogen", "project", "phase", "energy")][:3]
    if not words:
        return None
    return [w for w in words if re.search(re.escape(w), text, re.I)]


SUMMARY = ROOT / "sources" / "research_pass_14_summary.json"


def triage(E):
    """THE SIGNAL, SPLIT INTO WHAT IT IS WORTH.

    `owner_page_names_it` is a SUBSTRING MATCH on the entry's distinctive words and
    nothing more. Twenty-eight of the fifty-nine hits are the domain echoing the
    project's own name back — hyperionrenewables.com contains "Hyperion", inobat.eu
    contains "InoBat" — which says only that the register had the right company's
    website, not that the company says anything about this works. THAT IS THE
    NAME-FOLD FAILURE D-S4 FORBIDS, arriving through a different door, and it is
    split out here rather than counted.
    """
    weak, cand = [], []
    for k, v in sorted(E.items()):
        if not v["owner_page_names_it"]:
            continue
        g = next(x for x in v["searched"] if x["name_words_present"])
        host = urllib.parse.urlsplit(g["url"]).netloc.lower().replace("-", "")
        words = g["name_words_present"]
        (weak if all(w.lower().replace("-", "") in host for w in words)
         else cand).append((k, v, g, words))
    return weak, cand


def summarise(E):
    weak, cand = triage(E)
    return {
      "_comment": [
        "COMPUTED FROM sources/research_pass_14.json BY research_pass.py.",
        "Never edited by hand: --check recomputes it and refuses a mismatch.",
        "",
        "EVERY NUMBER A REPORT QUOTES ABOUT THIS PASS COMES FROM HERE, on the",
        "standing rule of 21 September: a figure that exists only in a session's",
        "narrative is not reported."],
      "entries_searched": len(E),
      "fetches": sum(len(v["searched"]) for v in E.values()),
      "by_sector": {s: {
        "searched": sum(1 for v in E.values() if v["sector"] == s),
        "owner_page_names_it": sum(1 for v in E.values()
                                   if v["sector"] == s and v["owner_page_names_it"]),
        "browser_queue": sum(1 for v in E.values()
                             if v["sector"] == s and v["browser_queue"])}
        for s in ("hydrogen", "batteries", "cement", "transport and storage")},
      "signal": {
        "hits": len(weak) + len(cand),
        "weak_the_domain_echoes_the_name": len(weak),
        "candidates_a_person_should_read": len(cand)},
      "browser_queue": sum(1 for v in E.values() if v["browser_queue"]),
      "the_admission_search_guessed_domains": guessed_domains(),
    }


def guessed_domains():
    """WHAT THE 10 SEPTEMBER ADMISSION SEARCH ACTUALLY FETCHED, counted.

    Every one of its 167 entries carries the same four EU press URLs and then, for
    most of them, `<projectname>.com` and `<projectname>.eu` — domains DERIVED FROM
    THE PROJECT'S OWN NAME rather than found in a document. `www.labskive.com` for
    Green Lab Skive, `www.castellon.com` for BP's Castellón refinery,
    `www.barseback.com` for the Barsebäck Hydrogen Hub — which is a golf resort.

    THE GUESS IS NOT ALWAYS WRONG and that is what made it survive: 28 of the 47
    entries whose hosts were ALL name-derived came back `owner or permit source
    names the site`, because a project often is at its own name. What cannot stand
    is the other column: fifteen entries are classed `searched, none found` where
    every domain tried was one this register invented. FOR THOSE, "NONE FOUND" IS A
    STATEMENT ABOUT A GUESS.
    """
    import re as _re
    gap = json.loads((ROOT / "sources" / "hydrogen_gap_search.json")
                     .read_text(encoding="utf-8"))["entries"]
    def norm(x):
        return _re.sub(r"[^a-z0-9]", "", (x or "").lower())
    BOILER = {"ec.europa.eu", "cinea.ec.europa.eu"}
    all_derived, none_found = 0, []
    for e in gap:
        hosts = []
        for f in e.get("fetches") or []:
            h = urllib.parse.urlsplit(f.get("url") or "").netloc.lower()
            if h and h not in BOILER:
                hosts.append(h)
        derived = [h for h in hosts
                   if norm(h.replace("www.", "").rsplit(".", 1)[0]) in norm(e.get("name"))]
        if hosts and len(hosts) == len(derived):
            all_derived += 1
            if (e.get("outcome") or "").startswith("searched, none found"):
                none_found.append(str(e["ref"]))
    return {
      "entries_in_the_admission_search": len(gap),
      "every_non_eu_host_derived_from_the_project_name": all_derived,
      "of_those_verdicted_searched_none_found": len(none_found),
      "refs": sorted(none_found, key=int),
      "reading": ("A guessed domain that answers is a lucky guess and a fact; a guessed "
                  "domain that 404s is not a search. These fifteen entries are classed "
                  "`searched, none found` on domains this register invented from the "
                  "project's name, which is the fold D-S4 forbids arriving through a "
                  "different door.")}


QUEUE_CSV = ROOT / "sources" / "manual" / "browser_queue.csv"
QUEUE_FIELDS = ["entry_id", "sector", "name", "country", "register_class", "reason",
                "urls_to_open", "folder"]


def name_derived(url: str, name: str) -> bool:
    """Is this host's stem inside the project's own name? Then nobody published it."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    if not host:
        return False
    stem = re.sub(r"[^a-z0-9]", "", host.replace("www.", "").rsplit(".", 1)[0])
    return bool(stem) and stem in re.sub(r"[^a-z0-9]", "", (name or "").lower())


def slug(key: str) -> str:
    """A folder name from an entry id, and it has to be reversible by eye.

    The ids are the censuses' own — `iea:1191`, `bn26:FAAM Terevola`,
    `ieaccus:1203` — and carry colons and spaces, which are a poor thing to type at
    a shell prompt and worse to quote in a script. Lower-cased, every run of
    anything else folded to one dash: `iea-1191`, `bn26-faam-terevola`. The CSV
    carries BOTH the id and the folder on every line, so nobody has to run this
    function in their head, and the writer refuses a collision rather than letting
    two entries share a folder.
    """
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", key.lower())).strip("-")


def queue_csv() -> int:
    """The browser queue as a file a person works down, one folder per entry.

    WHAT A ROW IS FOR. Each of these is an entry a declared reader could not read:
    either every URL its own records name answered nothing, or its records name no
    owner host at all. A browser can do what urllib cannot — run the script that
    draws the page, carry the cookie a WAF wants, be a person — so the queue is
    handed over with the reason stated, the URLs that refused, and the folder the
    saved page goes in.

    THE URLS ARE THE ONES ON FILE AND NONE ARE INVENTED. For an entry that was
    searched, they are the hosts this pass tried, in the order it tried them, with
    what each answered. For an entry with no owner host they are whatever its own
    records cite — a benchmark page, a grant register — and where there is nothing,
    the column is EMPTY and the reason says so. L9's rule holds here: a domain is
    never derived from a project's name, least of all in a queue that asks somebody
    to spend their morning on it.
    """
    doc = load()
    E = doc["entries"]
    known = {e["key"]: e.get("known_urls") or [] for e in population()}
    q = [(k, v) for k, v in sorted(E.items()) if v["browser_queue"]]
    seen, rows = {}, []
    for k, v in q:
        f = slug(k)
        if f in seen:
            raise SystemExit(f"research_pass --queue-csv: {k!r} and {seen[f]!r} both "
                             f"fold to the folder {f!r}; two entries cannot share one")
        seen[f] = k
        if v["searched"]:
            reason = "every URL in the entry's own records answered nothing: " + "; ".join(
                f"{g['url'].split('//')[-1]} {g['outcome']}" for g in v["searched"])
            urls = [g["url"] for g in v["searched"]]
        else:
            reason = ("no owner host in the entry's own records — nothing was fetched "
                      "for it, and nothing may be guessed (L9)")
            urls = []
        for u in known.get(k, []):
            if u not in urls:
                urls.append(u)
        # AND A DOMAIN THIS REGISTER INVENTED IS NOT A URL TO OPEN. L9's test, the
        # same one guessed_domains() uses: a host whose stem is inside the project's
        # own name was derived from that name rather than found in a document —
        # `www.europe.com` for "P2X Europe - Nordic Electrofuel", `www.crane.com` for
        # "Green Crane". They stay in the `reason` column, because what was tried and
        # what it answered is the record of the search; they are not handed to a
        # person as somewhere to go. D-A24 struck sixteen ladder queue items for
        # exactly this and the same rule applies to a queue that costs a morning.
        urls = [u for u in urls if not name_derived(u, v["name"])]
        rows.append({"entry_id": k, "sector": v["sector"], "name": v["name"],
                     "country": v.get("country", ""), "register_class": v["klass"],
                     "reason": reason, "urls_to_open": " | ".join(urls),
                     "folder": f"sources/manual/{f}/"})
    QUEUE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=QUEUE_FIELDS)
        w.writeheader()
        w.writerows(rows)
    no_url = sum(1 for r in rows if not r["urls_to_open"])
    print(f"browser_queue.csv — {len(rows)} entr(y/ies) for a browser, "
          f"{len(rows) - no_url} with a URL on file and {no_url} with none.")
    print(f"  by sector: {dict(Counter(r['sector'] for r in rows))}")
    print("\n  THE FOLDER LAYOUT, one per entry, created when you save into it:\n")
    print("    sources/manual/<entry-folder>/")
    print("      <anything>.html|.pdf|.png     the page as your browser saved it")
    print("      <anything>.html.url           OPTIONAL: the URL it came from, one line,")
    print("                                    needed only when the file does not carry")
    print("                                    it and the entry has more than one URL")
    print("\n  Then: python3 sources/ingest_manual.py")
    print("    — files each save in the sector's cache index with its hash, adds it to")
    print("      sources/manual/MANIFEST.json as a human-read copy, and re-runs the")
    print("      entry's search and its signal from your copy.")
    print("\n  Examples:")
    for r in rows[:3]:
        print(f"    {r['folder']:<36} {r['entry_id']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--queue-csv", action="store_true", dest="queue_csv")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--sector", default="")
    a = ap.parse_args()

    pop = population()
    if a.sector:
        pop = [e for e in pop if e["sector"] == a.sector]
    doc = load()

    if a.plan:
        withh = [e for e in pop if targets(e)]
        print(f"brief 14 re-search: {len(pop)} entries in the two re-searchable classes.")
        print(f"  {len(withh)} have an owner host in their own records; "
              f"{len(pop) - len(withh)} have none and go straight to the browser queue.")
        print(f"  {Counter(e['sector'] for e in pop)}")
        print(f"  no owner host, by sector: "
              f"{Counter(e['sector'] for e in pop if not targets(e))}")
        return 0

    if a.search:
        todo = [e for e in pop if e["key"] not in doc["entries"]][:a.limit]
        print(f"{len(todo)} to search ({len(doc['entries'])} already on file)")
        for i, e in enumerate(todo, 1):
            mod = __import__(READERS[e["sector"]])
            got, hits = [], []
            for u in targets(e):
                rec = mod.fetch(u, "company",
                                f"brief 14 re-search, S3 order: {e['key']} "
                                f"({e['klass']}) — the owner's own domain first")
                txt = mod.body_text(rec["sha256"]) if rec["sha256"] else ""
                n = names_it(txt, e) if txt else None
                got.append({"url": u, "outcome": rec["outcome"],
                            "text_chars": rec["text_chars"], "sha256": rec["sha256"],
                            "name_words_present": n})
                if n:
                    hits.append(u)
                if rec["text_chars"] >= 400 and n:
                    break
            doc["entries"][e["key"]] = {
                **{k: e[k] for k in ("sector", "name", "klass", "country")},
                "owner_hosts": owner_hosts(e), "searched": got,
                "owner_page_names_it": bool(hits),
                "browser_queue": not got or all(g["text_chars"] < 400 for g in got)}
            save(doc)
            if i % 10 == 0 or hits:
                print(f"  {i:>3}/{len(todo)} {e['key']:<22} {len(got)} read"
                      f"{'  NAMES IT' if hits else ''}")
        print("done")
        return 0

    E = doc["entries"]
    if a.check:
        want = summarise(E)
        if not SUMMARY.exists() or json.loads(SUMMARY.read_text(encoding="utf-8")) != want:
            SUMMARY.write_text(json.dumps(want, indent=1, ensure_ascii=False) + "\n",
                               encoding="utf-8")
            print("research_pass --check: the summary did not match its source and has "
                  "been rewritten; commit it.")
            return 1
        print(f"research_pass: --check, {want['entries_searched']} entries, "
              f"{want['fetches']} fetches, summary recomputed and equal.")
        return 0

    if a.report:
        print(f"brief 14 re-search: {len(E)} entries searched, "
              f"{sum(len(v['searched']) for v in E.values())} fetches.\n")
        print(f"  {'sector':<24}{'searched':>9}{'owner names it':>16}{'to the browser':>16}")
        for s in ("hydrogen", "batteries", "cement", "transport and storage"):
            v = [x for x in E.values() if x["sector"] == s]
            print(f"  {s:<24}{len(v):>9}{sum(1 for x in v if x['owner_page_names_it']):>16}"
                  f"{sum(1 for x in v if x['browser_queue']):>16}")
        print(f"\n  ENTRIES WHOSE OWNER'S OWN PAGE NAMES THEM — a signal, not a class:")
        for k, v in sorted(E.items()):
            if v["owner_page_names_it"]:
                u = next(g["url"] for g in v["searched"] if g["name_words_present"])
                print(f"    [{v['sector'][:12]:<12}] {k:<22} {v['name'][:34]:36} {u[:52]}")
        return 0

    if a.queue_csv:
        return queue_csv()

    if a.queue:
        q = [(k, v) for k, v in sorted(E.items()) if v["browser_queue"]]
        print(f"THE BROWSER QUEUE, brief 14 — {len(q)} entries a declared reader could "
              f"not read.\n  Each is a page that answered nothing, or an entry whose own "
              f"records name no owner host.\n")
        for k, v in q:
            why = ("no owner host in the entry's own records" if not v["searched"]
                   else "; ".join(f"{g['url'].split('//')[-1][:40]} {g['outcome']}"
                                  for g in v["searched"][:2]))
            print(f"  [{v['sector'][:12]:<12}] {k:<22} {v['name'][:32]:34} {why[:74]}")
        return 0

    print("nothing asked for; see --help")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

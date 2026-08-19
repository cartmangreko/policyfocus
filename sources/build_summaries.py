"""
The summary objects -- one small JSON per node, three cuts, identical shape
everywhere.

    python3 build_summaries.py           # regenerate data/summaries/, then verify
    python3 build_summaries.py --check   # verify what is on disk, write nothing

A node is a sector (parent or child), a register file (an act), or the site
as a whole. Every node gets the same three cuts, so a reader who has learned
to read one strip has learned to read them all:

  direction   burden / benefit counts, plus `unchanged` as its own small count
  status      adopted / proposed / mixed, from the legal standing of the file
              each row came from
  channel     direct versus reached, with per-channel counts for the reached
              cohort

THE DIRECTION RULE, for the extended valence matrix. Valence is derived per
row by benefit_axis.derive_valence (kept identical to the TypeScript
implementation by check_valence_parity.py). The nine labels fold into the
direction cut as follows:

  burden      Requirement, Prohibition, Support cut, Entitlement withdrawn.
              A Prohibition row counts as burden: it closes a route rather
              than conditioning one, but it is unambiguously duty-side.
  benefit     Simplification, Opportunity, Entitlement, Prohibition lifted.
  unchanged   Neutral rows (direction: "unchanged", e.g. the PPWR
              carry-overs). These are EXCLUDED from the burden/benefit counts
              and carried as their own small count. A carried-over rule has no
              direction of travel, and folding it into burden would recreate
              exactly the misreading `unchanged` was added to prevent.

WEIGHT IS DELIBERATELY EXCLUDED. weight / weight_intensity stay on the rows
that carry them; no summary surface aggregates them. Weight intensity exists
on a fraction of one file today, and a cut that silently describes 14 rows as
if it described 480 is worse than no cut.

THE CHANNEL RULE. For a sector node, `direct` counts measures that NAME the
sector (with the parent rollup web/lib/data.ts applies: a parent counts rows
naming any of its children) and `reached` counts measures that reach it
without naming it. For an act or the site, `direct` counts rows naming at
least one sector, `reached` counts rows naming none but reaching at least
one, and `no_sector` counts rows linked to no sector at all (the omnibus
rows, which apply by size rather than sector). The per-channel split of the
reached cohort uses the same inference as web/lib/reachChannel.ts, ported
verbatim below -- the channel is not stored on rows, so both sides infer it
from stored text, and the two regexes must be edited together.

THE GATE. `verify` recomputes every summary from the register and diffs it
against data/summaries/ on disk, field by field; any disagreement is a build
failure. `npm run build` runs this file with --check in its prebuild step, so
a register change that is not reflected in the committed summaries -- or a
hand-edited summary -- stops the site from building. Output is deterministic:
fixed key order, sorted node file names, indent 2, trailing newline; a rebuild
that changes no row produces no diff.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from benefit_axis import derive_valence
from build_graph import REGISTER_FILES, SECTOR_SPINE, SECTORS

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
OUT = DATA / "summaries"

BURDEN = {"Requirement", "Prohibition", "Support cut", "Entitlement withdrawn"}
BENEFIT = {"Simplification", "Opportunity", "Entitlement", "Prohibition lifted"}

# ---------------------------------------------------------------------------
# File basis -- the same rule as build_findings.STATUS_RULE and
# web/lib/files.ts getFileBasis: one status is that status, both is mixed.
# ---------------------------------------------------------------------------

_REGISTER_TABLE = json.loads((HERE / "register_files.json").read_text(encoding="utf-8"))["files"]
_MANIFEST = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))


def file_basis(file_slug: str) -> str:
    entry = _REGISTER_TABLE[file_slug]
    statuses = set()
    if entry.get("declared_status"):
        statuses.add(entry["declared_status"])
    for key in entry.get("manifest_keys") or ():
        s = (_MANIFEST.get(key) or {}).get("status")
        if s:
            statuses.add(s)
    if not statuses:
        raise SystemExit(f"build_summaries: no status resolvable for register file {file_slug!r}")
    return statuses.pop() if len(statuses) == 1 else "mixed"


# ---------------------------------------------------------------------------
# Reach channel -- ported from web/lib/reachChannel.ts. Same patterns, same
# order, same residual case. Edit both files together.
# ---------------------------------------------------------------------------

_PROCUREMENT = re.compile(r"procurement|contracting authorit|public buyer|tender|public support scheme")
_SUPPLY = re.compile(r"suppl(y|ier|ies)|input|feedstock|value chain|upstream|downstream|component")

CHANNELS = ("supply_chain", "procurement", "regulatory_dependency")


def infer_reach_channel(row: dict) -> str:
    text = f"{row.get('addressee', '')} {row.get('duty') or ''} {row.get('benefit') or ''}".lower()
    if _PROCUREMENT.search(text):
        return "procurement"
    if _SUPPLY.search(text):
        return "supply_chain"
    return "regulatory_dependency"


# ---------------------------------------------------------------------------
# Attribution
# ---------------------------------------------------------------------------

CHILDREN: dict[str, list[str]] = {}
for _slug, _meta in SECTOR_SPINE.items():
    if _meta.get("parent"):
        CHILDREN.setdefault(_meta["parent"], []).append(_slug)


def load_rows() -> list[dict]:
    rows = []
    for slug in REGISTER_FILES:
        for r in json.loads((DATA / f"{slug}.json").read_text(encoding="utf-8")):
            r["_file"] = slug
            rows.append(r)
    return rows


def sector_rows(rows: list[dict], slug: str) -> tuple[list[dict], list[dict]]:
    """(named, reached) for one sector, with the parent rollup web/lib/data.ts
    applies: a parent counts a row naming or reaching any of its children, in
    whichever list the row earned on the child. A child never rolls down."""
    own = {slug, *CHILDREN.get(slug, ())}
    named, reached = [], []
    for r in rows:
        if own & set(r.get("sectors_named") or ()):
            named.append(r)
        elif own & set(r.get("sectors_reached") or ()):
            reached.append(r)
    return named, reached


def cut(direct: list[dict], reached: list[dict], no_sector: list[dict]) -> dict:
    """The three cuts over one node's rows. Shape is identical for every node."""
    rows = direct + reached + no_sector
    direction = {"burden": 0, "benefit": 0, "unchanged": 0}
    status = {"adopted": 0, "proposed": 0, "mixed": 0}
    for r in rows:
        v = derive_valence(r.get("measure_type"), r["direction"])
        if v in BURDEN:
            direction["burden"] += 1
        elif v in BENEFIT:
            direction["benefit"] += 1
        else:
            direction["unchanged"] += 1
        status[file_basis(r["_file"])] += 1
    by_channel = {c: 0 for c in CHANNELS}
    for r in reached:
        by_channel[infer_reach_channel(r)] += 1
    return {
        "measures": len(rows),
        "direction": direction,
        "status": status,
        "channel": {
            "direct": len(direct),
            "reached": len(reached),
            "no_sector": len(no_sector),
            "reached_by_channel": by_channel,
        },
    }


def split_by_linkage(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """Act/site attribution: direct = names at least one sector; reached =
    names none but reaches at least one; no_sector = linked to none."""
    direct, reached, none = [], [], []
    for r in rows:
        if r.get("sectors_named"):
            direct.append(r)
        elif r.get("sectors_reached"):
            reached.append(r)
        else:
            none.append(r)
    return direct, reached, none


def distinct_sectors(rows: list[dict]) -> dict:
    named = set()
    total = set()
    for r in rows:
        named.update(r.get("sectors_named") or ())
        total.update(r.get("sectors_named") or ())
        total.update(r.get("sectors_reached") or ())
    return {"named": len(named), "total_reach": len(total)}


def compute() -> dict[str, dict]:
    """Every summary, keyed by its path relative to data/summaries/."""
    rows = load_rows()
    out: dict[str, dict] = {}

    for slug in sorted(SECTOR_SPINE):
        named, reached = sector_rows(rows, slug)
        out[f"sector/{slug.replace('/', '__')}.json"] = {
            "node": f"sector:{slug}",
            "label": SECTORS[slug],
            **cut(named, reached, []),
        }

    for file_slug in sorted(REGISTER_FILES):
        file_rows = [r for r in rows if r["_file"] == file_slug]
        direct, reached, none = split_by_linkage(file_rows)
        out[f"act/{file_slug}.json"] = {
            "node": f"act:{file_slug}",
            "sectors": distinct_sectors(file_rows),
            **cut(direct, reached, none),
        }

    direct, reached, none = split_by_linkage(rows)
    out["site.json"] = {
        "node": "site",
        "files": len(REGISTER_FILES),
        "sectors": distinct_sectors(rows),
        **cut(direct, reached, none),
    }
    return out


# ---------------------------------------------------------------------------

def write(summaries: dict[str, dict]) -> None:
    (OUT / "sector").mkdir(parents=True, exist_ok=True)
    (OUT / "act").mkdir(parents=True, exist_ok=True)
    for rel, doc in sorted(summaries.items()):
        (OUT / rel).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify(summaries: dict[str, dict]) -> list[str]:
    """Diff the computed summaries against what is on disk. Every difference
    is reported -- a summary disagreeing with the rows it summarizes, a stale
    file, a missing file, or a file nothing computes."""
    problems = []
    for rel, doc in sorted(summaries.items()):
        path = OUT / rel
        if not path.exists():
            problems.append(f"{rel}: missing (run build_summaries.py to regenerate)")
            continue
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        if on_disk != doc:
            problems.append(f"{rel}: disagrees with the register (stale or hand-edited; regenerate)")
    expected = set(summaries)
    for path in OUT.rglob("*.json"):
        rel = path.relative_to(OUT).as_posix()
        if rel not in expected:
            problems.append(f"{rel}: on disk but no node computes it")
    return problems


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    summaries = compute()

    # Internal consistency, before anything touches disk: the three cuts of one
    # node must describe the same row set.
    for rel, doc in summaries.items():
        n = doc["measures"]
        d, s, c = doc["direction"], doc["status"], doc["channel"]
        if sum(d.values()) != n or sum(s.values()) != n:
            raise SystemExit(f"build_summaries: cuts of {rel} disagree on the row count")
        if c["direct"] + c["reached"] + c["no_sector"] != n:
            raise SystemExit(f"build_summaries: channel cut of {rel} disagrees on the row count")
        if sum(c["reached_by_channel"].values()) != c["reached"]:
            raise SystemExit(f"build_summaries: per-channel counts of {rel} do not sum to reached")

    if not check_only:
        write(summaries)

    problems = verify(summaries)
    if problems:
        print(f"SUMMARIES INVALID — {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"build_summaries: {len(summaries)} summaries verified against the register "
          f"({len(SECTOR_SPINE)} sectors, {len(REGISTER_FILES)} acts, 1 site)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

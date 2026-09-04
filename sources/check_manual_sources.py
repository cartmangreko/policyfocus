"""
The gate on sources/manual/: pages a person retrieved because the fetcher cannot.

    python3 check_manual_sources.py          # non-zero on any mismatch

WHY A GATE ON A FOLDER SOMEBODY DROPS FILES INTO. Precisely because somebody
drops files into it. Every other source on this platform is a URL that
check_links.py fetches, so a source that has rotted announces itself. A file
sitting in a folder announces nothing: it does not say where it came from, when,
or whether the row citing it is citing this copy or a different one somebody
replaced it with.

So the pairing is checked in three directions and there is no fourth:

  RECORDED    every file in sources/manual/ has an entry in MANIFEST.json. A page
              with no provenance is a page somebody found.

  PRESENT     every entry in the manifest names a file that is there. An entry
              for a file nobody dropped is a claim that a page was read.

  CITED       every `retrieved_manually` path in the register names a file that
              is there and is in the manifest. This is the one that matters: it
              is what stops a row quoting a sentence from a copy that has been
              deleted, moved or never arrived.

WHAT THIS DOES NOT CHECK, and cannot. Whether the saved file is honestly what the
URL served. Nothing in this repository can check that, and pretending otherwise
would be worse than saying so: the manifest records who retrieved it and when,
and that is the whole of the assurance. It is the same assurance a verbatim quote
from any source carries, and it is why the row cites the publisher's live URL
rather than the local file -- a reader who doubts the quote can open the original.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import sector_map as sm

MANUAL = sm.ROOT / "sources" / "manual"
MANIFEST = MANUAL / "MANIFEST.json"

# Not sources. The folder documents itself and lists its own queue.
NOT_PAGES = {"README.md", "MANIFEST.json"}


def cited_paths() -> list[tuple[str, str]]:
    """Every `retrieved_manually` in the register, with where it was found.

    Walked generically rather than per field: the key may appear on a project's
    source list, on a location's source, on a parameter, on a funding row. A
    walker that had to be told where to look would miss the first one added
    somewhere new, which is exactly when a gate is needed.
    """
    out: list[tuple[str, str]] = []

    def walk(obj, where: str) -> None:
        if isinstance(obj, dict):
            path = obj.get("retrieved_manually")
            if isinstance(path, str):
                out.append((path, where))
            for k, v in obj.items():
                walk(v, f"{where}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{where}[{i}]")

    for kind in ("project", "parameter", "technology", "bottleneck", "funding",
                 "material"):
        walk(sm.load(kind), kind)
    return out


def main() -> int:
    if not MANIFEST.exists():
        print(f"check_manual_sources: no manifest at {MANIFEST}", file=sys.stderr)
        return 1
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    retrieved = doc.get("retrieved") or []
    wanted = doc.get("wanted") or []

    problems: list[str] = []

    on_disk = {p.name for p in MANUAL.iterdir()
               if p.is_file() and p.name not in NOT_PAGES}
    recorded = {}
    for i, entry in enumerate(retrieved):
        where = f"MANIFEST.retrieved[{i}]"
        for field in ("file", "url", "retrieved_date", "retrieved_by"):
            if not entry.get(field):
                problems.append(f"{where}: no {field}")
        name = entry.get("file")
        if not name:
            continue
        if name in recorded:
            problems.append(f"{where}: {name} is recorded twice")
        recorded[name] = entry
        if name not in on_disk:
            problems.append(f"{where}: names {name}, which is not in sources/manual/")

    for name in sorted(on_disk - set(recorded)):
        problems.append(f"sources/manual/{name} has no entry in MANIFEST.json — a page "
                        f"with no provenance is a page somebody found")

    for path, where in cited_paths():
        name = Path(path).name
        if not path.startswith("sources/manual/"):
            problems.append(f"{where}: retrieved_manually={path!r} is not in "
                            f"sources/manual/")
        elif name not in on_disk:
            problems.append(f"{where}: cites {path}, which is not on disk")
        elif name not in recorded:
            problems.append(f"{where}: cites {path}, which has no manifest entry")

    if problems:
        print(f"check_manual_sources: {len(problems)} problem(s)\n", file=sys.stderr)
        print("\n".join(f"  {p}" for p in problems), file=sys.stderr)
        return 1

    print(f"check_manual_sources: OK — {len(recorded)} page(s) retrieved by hand, "
          f"{len(cited_paths())} citation(s)")
    if wanted:
        # THE QUEUE IS PRINTED, ALWAYS, AND IT IS PARKED. These are things only a
        # person can do; the build retries none of them and no turn is spent on
        # them. Printing the exact URL and the path the file should take makes
        # filing a copy and a manifest line rather than a search — a queue that
        # has to be reconstructed before it can be worked is a queue nobody works.
        live = [w for w in wanted if w.get("priority") != "lowest"]
        low = [w for w in wanted if w.get("priority") == "lowest"]
        print(f"\nwanted ({len(wanted)}) — pages this pipeline cannot fetch, parked for "
              f"a browser:")
        for group, label in ((live, None), (low, "lowest priority — corroboration only, "
                                                "nothing waits on these")):
            if not group:
                continue
            if label:
                print(f"\n  {label}:")
            for w in group:
                print(f"  {w.get('candidate', '?')}")
                print(f"      url      {w.get('url', '?')}")
                print(f"      drop as  {w.get('drop_as', '?')}")
                if w.get("why"):
                    print(f"      {w['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

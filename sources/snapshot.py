"""
Release snapshots -- the register state and every fetched source version,
archived under a dated path that is never written twice.

    python3 snapshot.py                    # archive under snapshots/YYYY-MM-DD/
    python3 snapshot.py --label rc2        # snapshots/YYYY-MM-DD-rc2/, for a
                                           # second snapshot on one day
    python3 snapshot.py --list             # what has been archived

THE POLICY (also stated in scope.md, "Snapshots are append-only"). Each
release archives, under snapshots/<date>/:

  data/          the register as published -- the seven register files, the
                 sector spine, the findings, the summaries, the graph and the
                 exposure layer (everything the site build reads; the FIGARO
                 flatfile zip is an input, not register state, and is skipped)
  sources/       every fetched source version and its sidecar -- the .txt
                 corpora, the .fetch.json provenance records, the cache of
                 EUR-Lex manifestations, the manifest, and the pass/docket
                 artifacts the read-history is derived from

Ingestion and rebuilds NEVER overwrite a prior snapshot: this script refuses
to write into an existing directory, with no --force. A wrong snapshot is
deleted by a human with git, where the deletion is visible in history --
never replaced in place by a tool. That is the whole value of the archive: a
row can change classification, a source can be re-fetched, and the dated
copies stay exactly what was published when.

Copies are byte-for-byte; a MANIFEST.json in the snapshot root records what
was copied, from where, and the SHA-256 of every file, so a snapshot can be
verified without trusting the tree it sits in.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SNAPSHOTS = ROOT / "snapshots"

# What "register state" and "fetched source versions" mean, precisely.
DATA_GLOBS = [
    "*.json",
    "findings/*.json",
    "summaries/**/*.json",
    "graph/*.json",
    "exposure/*.json",
]
SOURCES_GLOBS = [
    "*.txt",
    "*.fetch.json",
    "manifest.json",
    "register_files.json",
    "queued.json",
    "seen.json",
    "watch_config.json",
    "*_pass_a.json",
    "*_pass_b.json",
    "*_disagreements.json",
    "*_reconciliation_docket.json",
    "cache/*",
]


def collect() -> list[tuple[Path, Path]]:
    """(absolute source, snapshot-relative destination) for every file."""
    pairs: list[tuple[Path, Path]] = []
    for base, globs in ((ROOT / "data", DATA_GLOBS), (HERE, SOURCES_GLOBS)):
        rel_base = base.relative_to(ROOT)
        for pattern in globs:
            for p in sorted(base.glob(pattern)):
                if p.is_file():
                    pairs.append((p, rel_base / p.relative_to(base)))
    return pairs


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = sys.argv[1:]
    if "--list" in args:
        if not SNAPSHOTS.exists():
            print("snapshot: none taken yet")
            return 0
        for d in sorted(SNAPSHOTS.iterdir()):
            manifest = d / "MANIFEST.json"
            n = len(json.loads(manifest.read_text())["files"]) if manifest.exists() else "?"
            print(f"  {d.name}  {n} files")
        return 0

    label = ""
    if "--label" in args:
        label = "-" + args[args.index("--label") + 1]

    dest = SNAPSHOTS / f"{date.today().isoformat()}{label}"
    if dest.exists():
        print(
            f"snapshot: {dest.relative_to(ROOT)} already exists and snapshots are never "
            "overwritten. Use --label to take a second snapshot today; delete a wrong one "
            "with git, where the deletion stays visible.",
            file=sys.stderr,
        )
        return 1

    pairs = collect()
    manifest = {"taken": date.today().isoformat(), "files": {}}
    for src, rel in pairs:
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        manifest["files"][rel.as_posix()] = sha256(src)

    (dest / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"snapshot: {len(pairs)} files archived under {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

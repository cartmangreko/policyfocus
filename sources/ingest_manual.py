#!/usr/bin/env python3
"""What a person saved in a browser, filed as a source and read back into the pass.

    python3 sources/ingest_manual.py            # what it sees, writing nothing
    python3 sources/ingest_manual.py --write    # file the copies and re-run the entries

THE QUEUE IS THE OTHER HALF OF A SEARCH THIS REGISTER COULD NOT FINISH.
`sources/manual/browser_queue.csv` lists the entries a declared reader could not
read — a 403, a WAF, a page that draws itself with a script, or an entry whose own
records name no owner host at all. A browser can do what urllib cannot. What it
cannot do is remember: a file dropped in a folder says nothing about where it came
from, when, or whether the row citing it is citing this copy. That is what this
script is for, and it is why sources/manual/ has a gate on it.

WHAT IT DOES TO ONE SAVED FILE, in order:

  1  finds the URL — from a `<file>.url` sidecar, or from what the browser wrote
     into the page itself (`saved from url=(…)`, `<link rel=canonical>`, `og:url`),
     or from the entry's single queued URL. WHERE THE ENTRY HAS SEVERAL AND THE
     FILE NAMES NONE IT STOPS AND ASKS, because attaching a page to the wrong URL
     is worse than not filing it.
  2  files it in the SECTOR'S cache index under its SHA-256, beside the fetches the
     machine made, with `http: null` because nothing here made a request. The hash
     is the whole of what makes the copy checkable later.
  3  adds it to sources/manual/MANIFEST.json as a human-read copy — the file, the
     url, the date, and the reader — which is what check_manual_sources.py gates.
  4  RE-RUNS THE ENTRY FROM THE COPY. The same reader that the machine pass used,
     the same signal: does the page contain the distinctive words of the entry's
     own name. The record in research_pass_14.json gains a search whose outcome is
     `retrieved by hand`, and the entry leaves the browser queue when a copy of it
     has text somebody can read.

THE DATE IS THE FILE'S OWN. `retrieved_date` is the day the file was written on
this disk, not today: a queue worked over a fortnight is a fortnight of different
days, and stamping them all with the day they were ingested would say the reader
did in an afternoon what they did in two weeks.

AND THE SIGNAL IS STILL A SIGNAL. `names_it` is a substring match on the entry's
distinctive words, which is where a person looks next and is not a class. NOTHING
HERE WRITES A CLASS, a verdict or a row — the same rule the machine pass runs
under.

A PDF IS FILED AND NOT READ. The sector readers extract text from HTML and return
nothing for a PDF, so a print-to-PDF save is recorded as a copy with its hash and
the entry STAYS in the queue, with this script saying so. Save the page as HTML
(or "Webpage, Complete") where the site lets you.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = HERE.parent
MANUAL = HERE / "manual"
MANIFEST = MANUAL / "MANIFEST.json"
QUEUE = MANUAL / "browser_queue.csv"
PASS = HERE / "research_pass_14.json"
READER = {"hydrogen": "hydrogen_search", "batteries": "battery_search",
          "cement": "ccs_search", "transport and storage": "ccs_search"}
BY = "George Christopoulos"
SKIP = {"MANIFEST.json", "README.md", "browser_queue.csv"}

SAVED_FROM = re.compile(rb"saved from url=\(\d+\)(\S+)")
CANONICAL = re.compile(rb"""<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']+)""", re.I)
OG_URL = re.compile(rb"""<meta[^>]+property=["']og:url["'][^>]+content=["']([^"']+)""", re.I)


def queue() -> dict:
    """folder slug -> the queue line. The CSV is the mapping and nothing re-derives it."""
    if not QUEUE.exists():
        raise SystemExit("ingest_manual: no sources/manual/browser_queue.csv — run "
                         "`python3 sources/research_pass.py --queue-csv`")
    out = {}
    with QUEUE.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[Path(r["folder"].rstrip("/")).name] = r
    return out


def url_for(path: Path, row: dict) -> tuple[str, str]:
    """(url, how it was established). Never guessed — see the docstring."""
    side = path.with_suffix(path.suffix + ".url")
    if side.exists():
        u = side.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        if u.startswith("http"):
            return u, "a .url sidecar beside the file"
    raw = path.read_bytes()[:400000]
    for pat, how in ((SAVED_FROM, "the browser's own `saved from url` comment"),
                     (CANONICAL, "the page's rel=canonical"),
                     (OG_URL, "the page's og:url")):
        m = pat.search(raw)
        if m:
            u = m.group(1).decode("utf-8", "replace").strip()
            if u.startswith("http"):
                return u, how
    urls = [u for u in (row.get("urls_to_open") or "").split(" | ") if u.strip()]
    if len(urls) == 1:
        return urls[0], "the entry's only queued URL"
    return "", ("the file carries no URL and the entry has "
                f"{len(urls)} queued — write it into {side.name}")


def index_of(mod):
    return json.loads(mod.INDEX.read_text(encoding="utf-8")) if mod.INDEX.exists() \
        else {"_comment": [], "fetches": []}


def main(argv: list[str]) -> int:
    write = "--write" in argv
    rows = queue()
    doc = json.loads(PASS.read_text(encoding="utf-8"))
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = {e["file"] for e in man.get("retrieved", [])}

    found, filed, unread, problems, touched = 0, 0, 0, [], {}
    for folder in sorted(p for p in MANUAL.iterdir() if p.is_dir()):
        row = rows.get(folder.name)
        if row is None:
            problems.append(f"sources/manual/{folder.name}/ is not a folder the browser "
                            f"queue names — nothing here knows which entry it is for")
            continue
        entry = doc["entries"].get(row["entry_id"])
        if entry is None:
            problems.append(f"{row['entry_id']}: not in research_pass_14.json")
            continue
        mod = __import__(READER[entry["sector"]])
        for f in sorted(folder.iterdir()):
            if not f.is_file() or f.name.startswith(".") or f.suffix == ".url":
                continue
            found += 1
            rel = str(f.relative_to(MANUAL))
            url, how = url_for(f, row)
            if not url:
                problems.append(f"{rel}: {how}")
                continue
            body = f.read_bytes()
            sha = hashlib.sha256(body).hexdigest()
            date = time.strftime("%Y-%m-%d", time.localtime(f.stat().st_mtime))
            text = mod.text_of(body, "pdf" if body[:4] == b"%PDF" else "")
            words = None
            if len(text) >= 400:
                import research_pass as R
                words = R.names_it(text, entry)
            else:
                unread += 1
            print(f"  {rel}")
            print(f"    {row['entry_id']}  ({entry['sector']})  {len(body):,} bytes, "
                  f"{len(text):,} chars of text, saved {date}")
            print(f"    url: {url}  — from {how}")
            if len(text) < 400:
                print("    NOT READABLE AS TEXT (a PDF, or a page that saved as a shell). "
                      "Filed as a copy; the entry stays in the queue.")
            elif words:
                print(f"    the copy names: {', '.join(words)}  — a signal, not a class")
            else:
                print("    the copy does not carry the entry's distinctive words")
            if not write:
                continue

            # 2 — the sector's cache index, beside the machine's own fetches.
            mod.CACHE.mkdir(parents=True, exist_ok=True)
            (mod.CACHE / sha).write_bytes(body)
            idx = index_of(mod)
            if not any(r.get("sha256") == sha and r.get("file") == f"sources/manual/{rel}"
                       for r in idx["fetches"]):
                idx["fetches"].append({
                    "url": url, "domain": urllib.parse.urlsplit(url).netloc,
                    "source_type": "company", "date": date, "http": None,
                    "bytes": len(body), "sha256": sha, "text_chars": len(text),
                    "outcome": "retrieved by hand",
                    "note": f"browser queue, {row['entry_id']}: {row['reason'][:160]}",
                    "file": f"sources/manual/{rel}"})
                mod.INDEX.write_text(
                    json.dumps(idx, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            # 3 — the manifest.
            if rel not in recorded:
                man["retrieved"].append({
                    "file": rel, "url": url, "retrieved_date": date,
                    "retrieved_by": BY,
                    "note": f"Browser queue, {row['entry_id']} ({entry['sector']}). "
                            f"URL from {how}. {len(text):,} chars of readable text."})
                recorded.add(rel)
            # 4 — the entry, re-run from the copy.
            got = {"url": url, "outcome": "retrieved by hand",
                   "text_chars": len(text), "sha256": sha,
                   "name_words_present": words, "file": f"sources/manual/{rel}"}
            entry["searched"] = [g for g in entry["searched"]
                                 if g.get("sha256") != sha] + [got]
            entry["owner_page_names_it"] = any(g.get("name_words_present")
                                               for g in entry["searched"])
            entry["browser_queue"] = all(g["text_chars"] < 400 for g in entry["searched"])
            touched[row["entry_id"]] = entry
            filed += 1

    print(f"\ningest_manual: {found} saved file(s) in {len(list(p for p in MANUAL.iterdir() if p.is_dir()))} "
          f"folder(s); {filed} filed, {unread} not readable as text, "
          f"{len(problems)} problem(s).")
    if problems:
        print("\n  PROBLEMS — nothing is filed for these:")
        for p in problems:
            print("    " + p)
    if not found:
        print("\n  Nothing saved yet. The queue and the folder layout are in "
              "sources/manual/browser_queue.csv; run "
              "`python3 sources/research_pass.py --queue-csv` to print the layout again.")
    if write and touched:
        left = sum(1 for v in doc["entries"].values() if v["browser_queue"])
        MANIFEST.write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        PASS.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        out = sum(1 for k in touched if not touched[k]["browser_queue"])
        print(f"\ningest_manual: {len(touched)} entr(y/ies) re-run from a copy, "
              f"{out} left the browser queue, {left} still in it.")
        print("  Then: python3 sources/research_pass.py --check   (rewrites the summary)")
        print("        python3 sources/check_manual_sources.py     (gates the folder)")
    elif not write and found:
        print("\ningest_manual: nothing written. Add --write to file these.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

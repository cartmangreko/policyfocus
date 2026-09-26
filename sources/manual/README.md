# Manually retrieved pages

A drop folder for pages this repository's fetcher cannot read and a person can.

## Why it exists

Some sources are live, correct, and unreachable from here. AESC answers `403` to a
datacentre IP on every URL tried; `eng.sk-on.com` serves a certificate for a
different host. Neither is a defect in the source and neither is a research
problem — the document is identified, it is the right document, and a browser
opens it in a second.

Without somewhere to put the result, that produces the worst outcome available: a
row that cites a URL nobody in the pipeline has read, carrying a verbatim quote
somebody took on trust. This folder is the alternative. A person opens the page,
saves it here, and the row then cites **the original URL** with the saved copy
recorded beside it — so the claim walks back to the publisher, and the text it
walks back to is one that was actually read.

## The protocol

1. Open the URL in a browser.
2. Save the page as HTML or as a PDF into this folder. Name it
   `<candidate-id>--<slug>.<ext>` — for example
   `envision-aesc-douai--start-of-production.html`.
3. Add an entry to `MANIFEST.json` with the file name, the URL it came from, the
   date it was retrieved, and who retrieved it.
4. Nothing else. The row that cites it is written from the file afterwards, in the
   ordinary way, quoting the sentence it actually says.

## What a row then looks like

The source block cites the publisher's own URL, exactly as any other company
source does, and adds `retrieved_manually` naming the file:

```json
{
  "url": "https://aesc-group.com/news/...",
  "publisher": "AESC",
  "date": "2025-06-03",
  "retrieved_manually": "sources/manual/envision-aesc-douai--start-of-production.html"
}
```

`sources/check_manual_sources.py` gates the pairing in both directions: a row
naming a file that is not here fails, an entry in the manifest naming a file that
is not here fails, and a file sitting here with no manifest entry fails. A page
whose provenance nobody wrote down is a page somebody found.

## What this is not

**Not an archive.** `archived: true` with a `snapshot` path already covers a
source that has gone off the web, and it is a different fact: the publisher's
copy is gone. Here the publisher's copy is fine and we could not reach it, so the
row goes on citing the live URL and `check_links.py` goes on checking it.

**Not a place to put anything a fetch failed on.** A 404 is a dead source and a
5xx is somebody's bad afternoon; neither belongs here. This is for a page that a
person has confirmed is live and readable and that the pipeline is being refused.

---

## The browser queue (21 September 2026)

`browser_queue.csv` is the 66 entries a declared reader could not read — a 403, a
WAF, a page that draws itself with a script, or an entry whose own records name no
owner host at all. It is generated, never typed:

    python3 sources/research_pass.py --queue-csv

Each line carries the entry id, its sector and class, **why the machine could not
read it**, the URLs on file that are worth opening, and the folder to save into.
**A domain this register derived from a project's name is not in the URL column** —
it stays in the reason, with what it answered, because handing somebody a browser
and a domain nobody published is not a queue item (L9, D-A24).

### One folder per entry

    sources/manual/<entry-folder>/
      <anything>.html|.pdf|.png     the page as your browser saved it
      <anything>.html.url           OPTIONAL: the URL it came from, one line

The folder name is on the queue line beside the entry id, so nothing has to be
derived by hand. The `.url` sidecar is needed **only** when the saved file carries
no URL of its own and the entry has more than one queued: a page saved as "Webpage,
Complete" carries `saved from url=(…)`, and most pages carry a `rel=canonical` or an
`og:url`, which is where the URL is taken from first.

### Before a browser is opened at all: the archive, and the missing URLs

Two passes run over the queue first, because both of them take entries OFF it without
anybody's morning.

    python3 sources/queue_archive_pass.py            # ask the Internet Archive
    python3 sources/queue_archive_pass.py --save     # …and submit the misses to SPN
    python3 sources/queue_archive_pass.py --write    # file what came back with a body

**The archive pass** asks the availability endpoint, and then the CDX index where that
answers empty, for the last capture of every URL the queue carries. A capture with a
readable body is filed through scope.md's archived-source rule — the document's own
dateline in `date`, the capture's day in `captured_at`, `archived` true, the
publisher's own URL in `url` and the Wayback URL in `read_url` — and the entry leaves
the queue. **An empty-shell capture is filed too, with `empty body` in its outcome, and
the entry stays in the queue**: a capture of a page that draws itself with a script is
a capture of the script, and letting one stand for a document would take an entry off
somebody's list on a copy nobody can read. `no capture` and `refused` are counted apart:
the archive holding nothing and the archive not answering are different facts.

Save Page Now needs credentials — an anonymous POST answers `401` — so `--save` reads
`IA_ACCESS_KEY` and `IA_SECRET_KEY` (archive.org/account/s3.php) and, with neither set,
records each miss as one it could not test rather than as one it tested.

**`url_candidates.csv` is the other half**, for the 26 entries whose own records name no
owner host at all and which L9 forbids deriving one for. A person searches owner,
project and site, writes down THE QUERY and one candidate URL per entry, and leaves
`verdict` empty. A reader then fills it in:

    accept    this is the document's home and the queue should open it
    reject    it is not
              (empty)  nobody has read this line yet, and it stays out of the queue

An accepted candidate is carried into `browser_queue.csv` by `--queue-csv` with the
host named in the `reason` column as a reader's find — never as something the census
cited, because it isn't.

### The browser itself, a domain at a time

    python3 sources/research_pass.py --browse              # what is left, by domain
    python3 sources/research_pass.py --browse --batch      # open one domain's tabs

`--batch` opens every URL of one domain at once (in bursts of `--tabs`, 12 by default),
waits while you run SingleFile's *save all tabs* into `~/Downloads/eufabric-queue/`, and
then matches each saved file to its entry **by the URL SingleFile wrote into the file's
own header** — filing it into the entry's folder with a `.url` sidecar carrying that URL.
A file whose header it cannot read is LISTED AND LEFT IN THE DROP FOLDER; a page filed
against the wrong entry is worse than a page nobody filed. A file with no readable body
is filed and named, so you can see which saves came out empty. One URL cited by several
entries is opened once and filed for all of them. The state is per URL in
`sources/queue_browse_state.json`, so stopping mid-domain loses nothing.

**The helper never fetches a page.** It calls the operating system's `open` and reads
files off this disk. These are the entries a declared reader was refused on, and a
script that quietly retried them would be re-asking a question already answered.

### Then

    python3 sources/ingest_manual.py            # what it sees, writing nothing
    python3 sources/ingest_manual.py --write    # file the copies and re-run the entries

It files each save in the SECTOR's cache index under its SHA-256 beside the machine's
own fetches, adds it here as a human-read copy with the date the file was written and
the reader's name, and re-runs the entry's search and its signal from the copy. **A
PDF is filed and not read** — the sector readers take text from HTML and nothing from
a PDF — so save as HTML where the site allows it, or the entry stays in the queue.

Nothing in that path writes a class, a verdict or a row. A person classes.

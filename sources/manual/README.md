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

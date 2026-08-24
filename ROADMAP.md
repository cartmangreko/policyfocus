# Roadmap

The backlog. Work that is agreed in principle, scoped enough to start, and not
yet started. An entry leaves this file when its PR opens.

Rules of the file. An entry says what the change is, why it exists, and what it
touches — the last one because the size of the blast radius is what decides
whether something can ride along with other work or needs its own stack. An
entry that cannot say what it touches is not ready to be an entry.

---

## Horizontal / economy-wide scope as a data-model attribute

**Its own stack.** Touches the schema, the gates, and every sector page.

The register can say which sectors an act names and which it reaches. It has
no way to say that an act's scope *is* horizontal — that it binds by company
size and activity rather than by industry, and so is economy-wide by design.

The consequence is that an act with no sectors and an act nobody has mapped
yet are the same object in the data. The omnibus is the live case: 0 of its 35
measures names a sector, which is a fact about how the act is written, not a
gap in the reading, and nothing in the model records the difference. It is
patched at one surface, on the ego-graph-views branch (#19): one reviewed
sentence per horizontal act, stored in `data/prose.json` under `ego_notes` and
rendered by `sources/build_ego_views.py`, which fails the build for any
sectorless file that has no such sentence. The docstring there records why it
is a patch. Nothing on `main` addresses it yet.

The fix is three pieces, in order:

1. **A scope attribute on the act**, alongside the fields the manifest already
   carries — horizontal or sector-specific — set at ingestion, checked by the
   gates, and required rather than defaulted, so a new act cannot be silently
   filed as neither.
2. **Display strings derived from it**, worded once and fed the attribute, the
   same discipline as every other computed sentence: no surface writes its own
   phrasing for "this act applies economy-wide". The stopgap notes retire into
   this as they are replaced.
3. **Economy-wide measures surfaced on sector pages as their own note**, not
   folded into the sector's counts. A horizontal act does bind the companies
   in a sector, so hiding it is wrong; counting it as a sector-specific measure
   is equally wrong and quietly corrupts every comparison between sectors that
   the summary strips and findings rest on. It is a third category, and it has
   to read as one.

Why it earns its place ahead of the next feature: the gap is not about the
omnibus. Any horizontal instrument hits it the same way — reporting
simplification, due-diligence style acts, anything binding by size or turnover
— so the attribute pays for itself on the next such act rather than on a
hypothetical one, and every act ingested before it exists is an act that will
need backfilling afterwards.

---

## Effect dates recorded at ingestion for every act a file amends

**Rides along with the next ingestion.** Touches `sources/manifest.json`,
`sources/fetch_eurlex.py`, and the date basis in `sources/build_records.py`.

The manifest records WHICH acts a file amends and, separately, WHEN a repeal
takes effect. `repeals.<celex>` carries `since`, the article and the quote —
PPWR's repeal of 94/62/EC is dated 12 August 2026 from Art. 70(1) — while
`amends` is a bare list of CELEX numbers with no date against any of them.

The consequence shows up on change records. A record's event date is the date
of the event it describes (`sources/scope.md`), so an `amendment` record has to
take its date from the law rather than from the day the file was read.
`build_records.py` can date a record against a REPEALED act, because the date
is there, and fails outright against an AMENDED one, because it is not — the
failure is deliberate, since falling back to the ingestion date would produce a
record that looks right and is wrong. PPWR is the only amendment record that
can exist today, and it exists only because PPWR repeals rather than amends.

The fix is to give each amended act the shape `repeals` already has: the date
the amendment takes effect, the article it comes from, and the verbatim span,
recorded at ingestion and required rather than defaulted, so an act cannot be
filed with an amendment nobody dated. `build_records.py` reads the new field
where it already reads `repeals.<celex>.since`, and the check that fails today
starts passing on its own.

Why it earns its place ahead of other backlog work: the next amending act to be
ingested cannot have a change record at all until this exists, and the feed is
the product. It is also cheapest at ingestion, when someone is already reading
the act's final articles — reconstructing effect dates for acts ingested
earlier is the same work done later with less context.

---

## Ecosystem as a node kind, with the six tiles rendered from its edges

**Its own stack, small.** Touches `sources/sector_map.py` (the schema),
`sources/build_graph.py`, `sources/check_sector_schema.py`, a new data file,
`web/lib/transition.ts` and the home page.

The homepage the specification describes opens on six ecosystem tiles — green
steel, low-carbon cement, batteries, hydrogen, carbon capture, circular
materials. Four of those six are not sectors and cannot become sectors.

`data/sectors.json` is keyed on FIGARO industries, and that keying is what the
Eurostat input-output joins run on. Hydrogen, carbon capture and circular
materials are not FIGARO industries. Adding pseudo-keys for them would give the
join three rows it cannot match, which is worse than not having the tiles: it
corrupts a table that other work depends on being clean, and it does so quietly.

So the ecosystem is a node kind above the spine, six instances, with two edge
types out of it — `ecosystem -> sector` and `ecosystem -> technology`. Where an
ecosystem maps 1:1 to a sector, the tile opens that sector page and no new
surface exists. Where it is cross-cutting, the sector template renders with the
query scoped by the ecosystem's edges rather than by a sector key: one template,
so a reader learns the page once and a maintainer keeps one of them.

Why it earns its place: it is the cheapest of the page prerequisites and the
only one the homepage cannot open without. It is also the point at which the
FIGARO keying either survives contact with the product taxonomy or is quietly
broken, and that decision is much more expensive to reverse after six pseudo-
keys are in the spine and someone has joined against them.

---

## The steel dataset, through the same gates as cement

**Rides with nothing; it is a dataset, not a change.** Touches
`data/transition/projects.json`, `bottlenecks.json`, `technologies.json`,
`funding.json`, `parameters.json`, and the built files under
`data/transition/importance/` and `data/transition/lead/`.

Cement is the only sector with a map. `hasMap()` asks for an importance file and
at least one bottleneck, and steel has neither; all eight rows of
`projects.json` are cement. Every worked example in the page specification is
green steel, which means the sector template cannot be rebuilt against a second
sector until a second sector exists.

That second sector is the point. A template with one instance is a page with
extra steps — cement's shape and the template's shape are indistinguishable
until something else has to fit in it, and the sections most likely to be
cement-shaped (Companies, Related sectors, the constraint column) are exactly
the ones the specification adds.

It goes through the gates cement went through, without exception:
`check_sector_schema.py` on the hand-written files, `check_importance.py` and
the rebuild-and-diff on the built ones, a source and a date on every readiness
value, an append-only status history with a link on every entry. A dataset
hurried past its gates is not a faster second sector, it is a first sector that
can no longer be trusted either.

---

## Downstream reach channel from the Eurostat input-output data

**Its own stack.** Touches `web/lib/reachChannel.ts`, the reach data behind
`data/exposure/`, `data/flatfile_eu-ic-io_ind-by-ind_26ed_2024.zip` as an
ingestion input, and the sector template.

Reach walks suppliers. A measure that lands on steel is recorded as reaching
steel's inputs, and nothing walks the other way: the automotive, machinery and
construction industries that buy the steel and carry the cost forward are absent
from the model, and `reachChannel.ts` infers a channel from stored fields
precisely because the channel was never stored.

The consequence is a section that cannot be built. Supply-chain exposure — what
a carbon price on cement does to the people who pour concrete — is the question
the sector pages are most often going to be asked, and answering it from a
supplier-side graph would produce a confident picture pointing the wrong way.

The fix is a second channel built from the input-output table, downstream rather
than upstream, with the same provenance discipline as the rest: the coefficient,
its year, and the table it came from, displayed wherever a propagated figure is.
Until it exists the supply-chain section does not appear on any sector page, and
no placeholder stands in for it — see `eufabric-page-specifications.md` §2.

Why it earns its place last: it is the largest of the outstanding channels and
the only one whose absence is currently honest. Everything above it is a surface
that cannot be drawn; this is a surface deliberately left undrawn, and it stays
that way until the data supports it.

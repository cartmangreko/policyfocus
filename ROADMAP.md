# Roadmap

**Eufabric launched on 24 August 2026.** `SITE_LAUNCHED` is set in Vercel
production; robots.txt serves `Allow: /` with the sitemap line, sitemap.xml
serves 12 URLs, and the domain is verified in Google Search Console with the
sitemap submitted. Everything below is post-launch work, and `web/lib/launch.ts`
is done: the switch it exists to hold has been thrown.

The backlog. Work that is agreed in principle, scoped enough to start, and not
yet started. An entry leaves this file when its PR opens.

Rules of the file. An entry says what the change is, why it exists, and what it
touches — the last one because the size of the blast radius is what decides
whether something can ride along with other work or needs its own stack. An
entry that cannot say what it touches is not ready to be an entry.

---

## ~~Deployment protection for the production custom domain~~ — closed by the launch

**Closed 24 August 2026, by the site launching rather than by anything being
changed.** The entry asked whether `https://www.eufabric.eu` should sit behind
the Vercel SSO wall while the site was closed to crawlers: deployment protection
covers `*.vercel.app` deployment URLs and Vercel exempts the production custom
domain, so the domain answered 200 to anybody with the address while noindex was
the only closure. That gap has no meaning now — the site is public on purpose,
and being reachable by a person who has the link is the point rather than the
risk.

Kept rather than deleted, because the fact behind it is still true and will
matter again the next time something is staged on this project: a Vercel
production custom domain is not covered by deployment protection by default, and
noindex is a closure against crawlers, not against people.

## The country hover layer on the geography

**Its own stack, small.** Touches `sources/build_maps.py` (a second geometry
output), `web/components/LocationMap.tsx` (which becomes a client component),
`web/app/globals.css`, and every page that draws a frame.

Split out of #47 deliberately. The permanent country names landed there — a crop
names every country in view, an overview only those holding a site — and 2 of
234 name slots were dropped because a site label had the paper. The hover layer
is the backstop for those two and for every country a frame shows without room
to name: point at any country and its name appears, in the same treatment the
permanent labels use rather than in the site tooltip's.

Why it is not in #47. It is the component's **first client-side behaviour**, and
that is a real change rather than a small one. Hover alone is a CSS pseudo-class
and would have ridden along; the ruling also asks for touch — a tap on country
area shows the name, the next tap dismisses it — and that is state. Holding
state makes `LocationMap` a client component, which puts hydration on all 21
frames and on every project and sector page that draws one, and that belongs in
a review of its own rather than at the end of a five-commit PR about geometry.

The second reason is data. Hit-testing a country needs **closed polygons**, and
the map files carry open polylines: coastlines are stroked, not filled, and are
clipped as lines precisely so that a frame edge does not read as a coast
(`build_maps.py`, module docstring). Hit targets are a second geometry output
with a different clipping rule, and they roughly double the land payload of
every map file. That is a size and a shape question worth its own diff.

What it needs, in order:

1. **Closed per-country paths**, clipped as polygons rather than as polylines,
   emitted alongside `land` and invisible — `fill: transparent`, no stroke, so
   nothing about the picture changes.
2. **The hit order**, which the ruling fixes: site marks always win. The country
   targets sit below the marks in paint order, which is where SVG hit-testing
   already resolves it, so no code decides this.
3. **The behaviour**: hover on pointer devices, tap-to-show and tap-to-dismiss on
   touch, the name rendered in the permanent-label treatment and not the tooltip
   one.

The names themselves are already done: `country_names` in `data/prose.json`, and
`build_maps.py` already bakes the string into every frame that shows the country.

## A drawn connection between a works and the store its tonne reaches

**Low priority. Its own stack, small.** Touches `sources/build_maps.py` (a
connection layer and the label placement that has to avoid it),
`web/components/LocationMap.tsx`, `web/app/globals.css`, and `web/lib/prose.ts`
for the key line that would explain it.

Split out of #47. The ruling there settled that the geography stays **marks
only**: a dot is a works, a triangle is a store, and the fact that Brevik's
captured tonne ends up in Northern Lights is carried by the crop drawing both
and by the standfirst saying so — "The store its captured CO₂ reaches is drawn
with it." That is a sentence, not a line on the paper, and a reader looking at
two marks four hundred kilometres apart is being asked to infer the relation
that put them in the same frame.

What a line would add, and what it would cost. It would make the dependency
visible rather than stated, which is the one relation on this picture that is
not geographic — every other reason two marks share a frame is that they are
near each other. The cost is a fifth ink layer on a picture whose whole
discipline is that it has four, and a stroke on a frame where a stroke already
means a coastline. Neither is fatal; both are why this is not a small edit.

**Scoped to include the shared store.** A store serving more than one works is
the case that makes the layer worth building and the case that makes it hard.
Northern Lights already takes Brevik's tonne and is named as the most advanced
candidate for Slite's; Galata takes Anrav's; Prinos takes Ifestos'. A store with
two or three lines running into it draws the thing the register actually knows
and the standfirst cannot say without listing — and it is also where the lines
start crossing each other, crossing coastlines, and crossing the site labels
that `label_marks` has already placed. Any design here has to answer the
many-to-one case before it answers the one-to-one one, or it will be rebuilt.

It also has to answer what a line means when only one of its ends is drawn.
`UNDRAWN_STATUSES` takes cancelled projects off every frame but their own, and
`store_report` in `build_maps.py` already watches for a store serving both a
drawn and an undrawn project — today it reports nothing, because no cancelled
project has a store. The day one does, this layer is what has to decide whether
a line runs to a mark that is not there.

What it needs, in order:

1. **The connection as data**, emitted per frame: a path from works to store in
   canvas units, computed where both ends are drawn, and a stated rule for where
   only one is.
2. **The label pass made to avoid it**, which is the real work. `label_marks`
   places against marks and against other labels; a connection layer is a third
   thing to place around, and the crowded/dropped counts the build prints are
   the measure of whether it can be done at the narrow breakpoint.
3. **A key line**, tier 1 in `geoKeyProse`, on the frames that draw one.

## Cell inputs — cathode, anode, separator, electrolyte — as material links or a widened batteries perimeter

**Queued behind the batteries dataset. Its own stack.** Touches
`data/transition/materials.json`, the batteries perimeter prose and its gate, and
`data/transition/projects.json` if the perimeter widens rather than linking.

The batteries perimeter admits **cell manufacturing only**, and refuses cathode,
anode, separator and electrolyte works by name. That refusal is deliberate and it
is not permanent: those four are the inputs a cell is made of, several of the
largest are being built in Europe right now — Umicore at Nysa, BASF at
Schwarzheide — and a batteries picture that cannot see them is missing the half of
the supply chain Europe is actually furthest behind on.

Two ways to close it, and they are not the same change:

- **Material links.** The works stay outside the batteries dataset and arrive as
  edges from the materials layer, the way a captured tonne reaches a store. The
  perimeter is unchanged and the batteries page gains a dependency it can draw.
- **A widened perimeter.** Cathode and the rest become admissible sites in their
  own right, which means new rows, new marks on the overview, and a scale rule
  that has to be restated: 1 GWh per year is a cell measure and means nothing for
  a tonne of cathode powder.

The first is cheaper and is probably right. The second is what a reader would
expect if the page ever calls itself a picture of European battery manufacturing,
so the naming and the perimeter have to move together.

CRMA Annex I materials are the obvious first links either way, and are already
queued as part of the batteries dataset's technology work.

## A reach-channel parity gate, on the transition-parity pattern

**Queued. Small, and its shape is already settled.** Touches
`sources/build_summaries.py`, `web/lib/reachChannel.ts` and one new file in
`sources/`.

`build_summaries.infer_reach_channel` and `reachChannel.ts` `inferReachChannel`
are one rule written twice — the same two regexes, the same order, the same
residual case — and what holds them together is a comment on each side saying
"ported verbatim … the two regexes must be edited together." That is exactly the
shape `sector_map.is_transition` and `transition.ts` `statusTransitions` were in
before `check_transition_parity.py`, and it is not a mechanism.

The failure is invisible in the product, which is what makes it worth a gate: the
channel is **not stored** on any row — both sides infer it from the same stored
text — so a drifting regex would have the built summary and the rendered page
sort the same measure into different channels, both confidently, with nothing in
either output saying which was right.

The pattern to copy is `check_transition_parity.py`: compile the TypeScript with
the project's own `tsc`, run it, and diff the two answers over a corpus rather
than reimplementing the rule a third time in Python. The corpus is the one real
difference. Transitions could be enumerated exhaustively because the rule is
local and the alphabet is seven statuses; a regex over free text cannot be, so
this one takes **every `addressee`/`duty`/`benefit` triple actually in the
register** — a few hundred, which is a real corpus and not a synthetic one — plus
a short list of hand-written strings sitting on the boundary between the two
patterns. Those hand-written cases are the part worth arguing about in review.

## Türkiye in the batteries perimeter — revisit the exclusion

**Queued behind the batteries dataset. Small: one clause in the perimeter prose,
one list in the gate, and whatever candidates it admits.**

The batteries perimeter defines Europe as a named country list — the twenty-seven
member states plus the United Kingdom, Norway, Switzerland, the Western Balkans
and Ukraine — and excludes Türkiye as a whole country at launch, with the
exclusion stated on the coverage page rather than left to be inferred from an
absence.

**Why a whole country rather than a line.** Strict geography would put the
question on which side of the Bosphorus a site stands, and Türkiye's cell
industry is largely in the Marmara region where that line runs: Siro, the
Togg/Farasis joint venture at Gemlik, is in Bursa province on the Asian shore and
would be refused by a few kilometres. A perimeter that turns on that will be
argued with every time it is applied, and the argument will be about cartography
rather than about industry. Excluding the country is at least a rule a reader can
predict.

**What would reopen it.** Türkiye is in the customs union, its cell industry
supplies European carmakers, and the argument for holding it is the same one that
holds the United Kingdom and Norway. If the perimeter's question is "what is
Europe building", the honest answer may include it. That is a scope decision
rather than a data one, and it should be made deliberately rather than by a
candidate arriving and forcing it.

**What it touches when it moves.** The perimeter prose on `/coverage`, the country
list in the gate, and the geography — `country_names` in `data/prose.json` would
need Türkiye, and `EUROPE_DEGREES` in `build_maps.py` currently stops at 31 E,
which holds Istanbul but not Bursa's eastern edge. Both are one-line changes and
both would fail the build loudly rather than quietly, which is the right order.

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

## A lead block for the material page, and its way into the index

**Rides along with any material work.** Touches
`sources/build_object_leads.py`, `data/lead/`, `web/app/materials/[id]/page.tsx`
and `web/lib/routes.ts`.

Brief 5 §2 gives the sector page a Materials section and brief 5 §6 makes
`/materials/{id}` its spoke — materials are cross-sector, so there is no
per-sector list page and the material's own page is where the whole of it is
read. The route is built (step 1) and carries `DEMOTED`, because §0.8 makes
indexability follow the lead block and this page renders none.

That is the rule working, not a hole in it: the page keeps `follow`, so a
crawler walks through it to the sectors and projects its edges name. The exit
is the one §0.8 gives every demoted route — it renders a lead block and becomes
indexable, and nobody re-opens the question to let it.

What the lead block needs is the mechanism measure and project pages already
have: a generator in `build_object_leads.py` writing `data/lead/materials.json`,
the same gate imported rather than reimplemented, and `web/lib/siteRoutes.ts`
reading that store for whether the URL is published — so the page's own robots
tag and the sitemap stay two readings of one file. Two materials today, which
is small enough that the shape of the sentence is the whole of the work: what a
material is, which sectors it moves between, and what anybody has published
about the volumes.

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

## The twenty-two `--acc-*` values were chosen, not ruled — revisit or ratify

**Low priority, and it may close by being ratified rather than changed.** Touches
one block in `web/app/globals.css` and nothing else. Every value is a one-line
edit; nothing computes from them and no gate encodes any particular hue.

**This was open question 3 of the original brief and was never answered.** The
brief asked which hues the sector accents should be; the instruction at the time
was to choose rather than to ask, so they were chosen. That decision has been
carried ever since as a fact about the stylesheet rather than as an open
question, and until now the only written record of its being open was a note in
the description of #26 — a PR that is closed, which is where questions go to be
forgotten. It is here so it is findable.

**What is already settled and is not being reopened.** The accents are wayfinding
rather than decoration: hairlines, chips and icon strokes only, never a
background, never a large fill. Grouped by material family, with a child sector a
lighter cut of its parent. And they have been **re-cut once by measurement** —
the first cut put all of them in one narrow band so none would shout, which
walked twelve into claret's and pine's neighbourhoods (`--acc-auto` was `#7c414a`,
nine deltaE from claret: a claret marker on the automotive page, beside figures
where claret means cost). Each is now the nearest colour to its original that
clears claret, pine, signal and ink by 33 deltaE, and `check_colour_layers.py`
fails the build on any that does not. So the values are constrained, checked, and
defensible.

**What is open is the only thing measurement cannot answer**: whether these are
the right twenty-two hues for these twenty-two sectors, as opposed to a
consistent set that clears the gate. A reader learns a sector's mark once and
then reads it everywhere — the feed card, the finding card, the directory card,
the diagram node, the sector header, the reach row — so the question is whether
the assignment means anything to somebody who does not already know the code, and
whether the family groupings read as families.

Closing it needs a look at the twenty-two in one place at the sizes they are
actually used, and then either a ruling that they stand or a re-cut inside the
same deltaE floor. Ratifying is a real outcome and should be recorded as one:
the entry exists so that the answer is written down, not so that the values
change.

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

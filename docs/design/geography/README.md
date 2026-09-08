# Geography

Two frames, one component, no colour.

`web/components/LocationMap.tsx` draws both: a regional crop on a project page
and a Europe-wide overview on a sector page. Every coordinate, every path and
the frame itself come from `sources/build_maps.py`, on the same rule the sector
diagram works under — a layout engine in the page makes the picture a function
of the reader's browser, and the basemap is a 5 MB shapefile nobody should be
parsing on a phone.

## Why it needed no colour ruling

The four layers each say what they are for. Signal is brand and chrome; claret
and pine are money direction; the diagram palette is for diagrams; the sector
accent is page identity and is explicitly never on a figure. A coastline is
none of those. So the ground is paper, the lines are ink, and the marks are
told apart by shape. No selector in the geography block emits a reserved token,
which is why `check_colour_layers.py` passes without the file being added to
any allowance and why §7 was never asked a question it does not answer.

## The picture draws what Europe is building

A **cancelled** project is **not drawn**: not on the sector overview, and not as
a context neighbour on another project's crop. Nothing is deleted — it keeps its
row in the register, its own page, and its place in every count and every number
built off the dataset. It loses ink on frames about what is being built, and
nothing else.

**The exception is its own page.** A project is always drawn on its own crop,
whatever its status, because a page whose picture omitted its subject would have
lost the plot. That crop is the one frame a cancelled project appears on, and
both the standfirst and the key say so — a hollow mark drawn nowhere else looks
exactly like a hollow mark drawn everywhere, and the reader cannot tell without
being told.

**The frame follows the ink.** An undrawn dependency does not widen a crop it is
then left off; the subject fixes the frame whatever its status, because the
subject is always drawn.

**Stores follow their project.** A triangle is drawn where the works whose tonne
it takes is drawn. That holds without a rule of its own: a store is only ever
pulled onto a crop as the *subject's* dependency, and the subject is always
drawn. A store serving one drawn and one undrawn project is the case nothing can
decide by default, so `build_maps.py` reports it rather than choosing. Today no
store serves a cancelled project and the report is empty.

**Not every entry in a status history is a status change**, and the split is what
forced that to be named. Slite was paused on 19 November 2025 when the Swedish
Energy Agency declined to co-fund it; on 1 January 2026 Heidelberg Materials
withdrew the permit application, and that source is now an entry in the history
with the status unchanged. It is the evidence that the register has read the
later news and still says paused — which is exactly what `ambiguity_report` was
asking for, and filing it clears the flag.

An entry is a **transition** if its status differs from the one before it; the
first always is. The rule is positional rather than a flag on the row, so it
cannot fall out of step with the data. Three sentence templates render an entry
as a transition — "{project} was paused on {date}" — and all three now read the
transitions only, or Slite would have been paused on 1 January 2026 on three
pages, which no source says: `fact_the_latest` in `build_lead.py`,
`project_lead` in `build_object_leads.py`, and the status rail on the project
page. `sector_map.transitions` / `entered` and `transition.ts`
`statusTransitions` are the two implementations of the one rule, and
`sources/check_transition_parity.py` is what holds them together: it compiles and
runs the TypeScript, walks both readings over every history up to four entries
long — 4,681 of them, over the seven statuses plus one neither side knows — and
fails the build on any disagreement. Four entries is past the point a longer case
could say anything new, because the rule only ever compares an entry with its
predecessor.

It is a gate rather than a comment because the failure is invisible in the
product: if the two sides disagreed about which entries qualify, the built lead
and the project page would each name a different date for the same event, both
confidently, and nothing in either output would say which was right. That is the
same reason `check_valence_parity.py` exists, and it runs in the prebuild beside
`check_number_format.py`, the site's other two-language rule.

Feeds are deliberately **not** built this way. The home feed, the sector change
strip, the "Last change" column and the `as of` date all want the latest thing on
file, which is a different question from when the project last moved — and the
withdrawal, rendered as a date, a status chip and its note, is true in all four.

**Two checks came with the split**, both in `build_maps.py`, both reported and
neither failing the build. `paused` and `cancelled` used to be one group
everywhere that mattered — both hollow, both drawn, both inside "paused or
cancelled" — so telling them apart was a question of wording. It now decides
whether a project is on the paper. `ambiguity_report` flags any project in that
group carrying a source dated *later* than the status_history entry that put it
there, which is the one mechanical signal that the sources have moved on and
nobody has read the status against them. `store_report` is the straddle check
above. Neither can be settled by a build: both want somebody to read two
paragraphs and decide, and a non-zero exit would claim otherwise.

## One rule for the marks

    dot        a works
    triangle   a store, pointing down, because that is where the tonne goes
    filled     it is running
    hollow     it is not — announced, funded, or paused
    ring       the one this page is about

A third mark for transport infrastructure is in the brief and is not drawn:
no such node exists. Every named hub in the register — Antwerp@C, Brunsbüttel,
the Dunkerque CO₂ terminal — is named without being sited. See `scope.md`,
"A node in the geo layer requires a source-stated position".

**The key names only the distinctions the picture draws.** Fill is always
explained, in both directions — "filled: operating or under construction" and
"hollow: announced, funded, or paused", so a reader who sees only filled marks
still learns what filled means. Shape is explained only on a frame that actually
carries a store; on one that does not, "a dot is a works" would put a second
identical filled dot in the key beside the one explaining fill, which reads as a
mistake. The wording is tier 1, in `geoKeyProse`, and divides on the same
statuses the picture and the standfirst above it divide on.

**Hollow is enumerated rather than negated.** It used to read "not running",
which quietly covered cancelled too. Cancelled is no longer drawn on an overview
or as context, so hollow there is exactly announced, funded, or paused, and the
key names the three. That is the point of the change: a reader told what hollow
contains can notice that a project they know of is absent from the picture; a
reader told only "not running" cannot.

**The ring is now named too**, on every crop, and it never was before — a reader
was left to work out that the circle around one mark meant "the one you are
looking at". An overview has no subject and draws no ring, so it gets no such
line.

    ringed: this project

**And on the one frame where hollow is not the whole truth, that line carries
it.** On a crop whose subject is cancelled, the mark is hollow and its status is
outside the three the hollow line names. Two other answers were considered and
dropped: a third fill state — a dashed or struck mark — adds a distinction to a
vocabulary that deliberately has two axes, and would have to be explained in the
key of every frame that does *not* draw it, which is all but one; and widening
the hollow line to include cancelled would be wrong for every other mark on that
same crop. So the ring's own line takes the clause:

    ringed: this project — cancelled, and drawn on no other frame

That states the status, and it states the thing a reader could not otherwise
know — that the mark's absence from every other frame is a rule and not an
oversight. On every other crop the line stops after "this project", because
there is nothing further to tell and a key that explains an exception on the
frames it does not apply to has taught a rule the reader cannot see.

**The ringed swatch takes the subject's own fill**, so a paused subject's key
shows a hollow ringed dot and an operating one shows a filled ringed dot. The
thing in the key is the thing on the paper, which is the rule every other swatch
already works under.

## Every mark is named on the paper

A tooltip is not a label. It needs a pointer, and a pointer is the one thing a
reader has not got on a phone, in print, or in the screenshot somebody puts in a
slide — three of the four ways this picture is looked at. So every mark carries
its project name and its company, permanently, on both frames.

`build_maps.py` places them, with the rest of the geometry, and the component
decides nothing. The ladder, in order:

1. **Beside the mark**, clear of every other mark, every placed label and the
   frame edge. Eight directions are tried, east and west first.
2. **Pushed out, with a leader line** drawn back to the mark. A hairline in this
   picture always means one thing: this name belongs to that mark and not to the
   nearer one.
3. **The name alone**, pushed out — the company falls back to the tooltip, which
   was already carrying it and is unchanged by any of this.
4. **The least-bad position, kept.** A label is never dropped. A picture that
   silently omits whichever name it found hardest to place lies worst exactly
   where it is most crowded, and the reader cannot know a name was ever there.
   The file records `crowded` on any label that lands here, and the build says so.

**Two layouts are computed, not one.** This is the only place in `build_maps.py`
that admits a viewport exists, and it has to: the canvas is 760 units wide and
scales to fit, so a label's size in units is fixed while its size in pixels is
not. Eleven units is 11px on the 760px canvas a desktop gets and 5.6px on the
390px one a 430-wide phone has room for, which is not reading, it is a smudge.
Holding the label legible at 430 means roughly doubling it in canvas units, and
a label at twice the size collides far more often — so the narrow frame needs
its own placements and, in a crowd, its own shorter wording. The stylesheet shows
one layout and hides the other with `display: none`, so a screen reader is not
given every name twice.

**Widths are estimated, not measured.** A true font metric would mean shipping a
font file and a parser for it, as a build input, to position nineteen names.
`text_width` uses per-class advances taken off the stack the stylesheet asks for,
rounded up, with a safety factor that errs wide on purpose: a box measured too
big costs a leader line, and a box measured too small puts one word on top of
another.

**`MARK_R` moved into the build** and is written into every map file as
`mark_geometry`. The label layout needs to know how much room a mark takes and
the component needs to draw one the same size; held in two places, the day a mark
grows, every label would still be placed against the old radius and nothing would
say so.

## A multi-site mark says which site it is

A one-site project's label is its name. A multi-site project's label is its name
and which site this is, because the alternative is two marks in one picture
carrying identical words: the ArcelorMittal row is one project standing on
Bremen and Eisenhüttenstadt, and a reader who sees the same label twice reads a
rendering fault rather than a two-site project. The suffix is added only where
it distinguishes something — on the other eighteen projects it would be noise.

**The site survives shortening; the company does not.** Rung three of the ladder
drops the company and never the name line, so the one thing that tells a mark
from its twin cannot be the thing that falls off. The company is in the tooltip
either way, and the tooltip is unchanged.

## The ground is named

Country names, in English, as the faintest layer of type on the paper.

**Which countries are named differs by frame, on one principle in two settings.**
A crop names **every country in view**: the reader has been handed a region
without being told which one, and at 800 km across these are not outlines anybody
recognises from memory. An overview names **only the countries holding a site**,
because Europe with forty-five names on it is an atlas, and the question an
overview answers is where this sector is — a name over an empty country answers
a question nobody asked and takes the room from one that was.

**The country layer is subordinate, and the ordering is what makes that true.**
Site labels are placed first, against nothing but each other. Country names are
placed afterwards, against the boxes the site labels have already taken. So a
country name can be nudged or dropped by a site name and never the reverse.
Where no clean position exists the country name is **dropped** — the opposite of
the rule for a site label, and the asymmetry is deliberate: a missing site is a
fact the reader cannot recover, and a missing country is a shape most readers
know. The build prints every drop and counts them.

**A name stays inside its country.** The label point is the cell of a 26×26 grid
furthest from anywhere the country is not — a discrete distance transform, not a
centroid, because the centroid of a concave shape is routinely outside the shape
and a country outline is nothing if not concave. Up to four such points are
offered, kept apart so they are genuinely different middles: Germany's roomiest
point on a crop of the Ruhr is exactly where the site labels are, and a country
with one candidate loses its name to a neighbour's works. Nudges from those
points are small, because a name that has walked any distance is no longer over
its country, and a name in the wrong country is worse than none.

**No border layer was added.** The ruling made one conditional on the base
geometry being coastline-only, and it is not: every country's ring carries its
land boundaries as well as its coast, and `land_paths` has drawn both from the
first commit — from both sides, in fact. Nothing was needed.

**The names are worded once, in `data/prose.json` under `country_names`**, keyed
on the same ISO codes `natural_earth.py` keys the polygons on. They are there
rather than in `web/lib/prose.ts` with the geography's sentences because the
layout runs in Python at build time and a name the placement cannot see is a name
it cannot fit: `build_maps.py` takes the string to measure it, and bakes it into
the map file, so the component draws a name it never chose. Required rather than
defaulted — a frame showing a country the block does not name fails the build,
rather than falling back to a two-letter code or to the basemap's own `NAME_EN`,
which is neither reviewed nor in house style.

## What the standfirsts count

**The overview heading is "Where Europe is building {sector}".** "Every {sector}
site on file, across Europe" stopped being true when cancelled projects came off
the frame. Rather than qualify it, the heading says what the picture is actually
of — and a cancelled conversion is on file and is not something Europe is
building, so its absence is the heading keeping its word rather than the heading
being narrowed to fit.

**The three status groups sum over drawn sites, and a final clause names the
remainder**: *"1 cancelled project, on 2 sites, is on file and not drawn."*
Without it the overview would quietly shrink — a reader counting steel's sites
here and in the projects table below would find two missing and nothing on the
page accounting for them. The third group is now `paused` alone, not "paused or
cancelled": cancelled is the one status this frame cannot show, and a group named
for a state the picture never draws is a group that teaches nothing. The country
count moved onto the drawn marks for the same reason — taken off the project
rows it would have gone on naming a country whose only site had been left off.

**On a crop, "nothing else on file falls inside this frame" became "nothing else
drawn".** It was a claim about the register and is now false where a cancelled
project sits in view: ArcelorMittal's two sites are inside SALCOS's crop and are
not drawn on it. And a cancelled subject's crop opens by saying so — *"It was
cancelled, and is drawn here and on no other frame."*

## Where a coordinate may come from

A coordinate must come from a citable source identifying **the works
specifically**, and three kinds do: `basemap` (an OpenStreetMap feature with its
tags quoted), `company` (the operator's own materials naming an address or parcel,
quoted alongside), `permit` (a state permitting, planning or zoning filing). The
type is recorded per site and required rather than defaulted — a coordinate whose
provenance is implied is one nobody can weigh. `sources/sector_map.py`,
`LOCATION_SOURCE_TYPES`, is where the rule lives.

**A geocoded town name is refused**, and so is a street: both are sources about a
place rather than about a works, and `precision: "town"` already fails by name. A
position read off a photograph in a news story is refused because nobody can check
it.

**And we do not draw the polygon ourselves.** Where the basemap has no feature,
the answer is a permit, a published address, or the row staying off file — never
an edit to OpenStreetMap made in order to cite it. That edit would be circular:
the coordinate's whole claim is that somebody independent put the works there, and
an edit made to be cited turns "we believe this is the site" into "the basemap
says so", which is a stronger claim than we hold and one no reader could unpick.
Nothing here argues against improving OpenStreetMap; it argues that a coordinate
we publish may not rest on an edit we made for the purpose.

**One named exception exists**, in the shape this repository already uses for
offshore points: a short list in `check_sector_schema.py`, each entry a sentence
somebody wrote, printed on every run, stale entries failing. Its single member is
Galata, a depleted offshore gas field with no address, no parcel and no polygon —
the three types describe how you identify a works, and it is not one.

## The projection

Lambert conformal conic, EPSG:3034's parameters — standard parallels 35 N and
65 N, origin 52 N, central meridian 10 E — on a sphere. That is the projection
the European statistical system draws the continent in, so the shape here is
the shape a reader has seen everywhere else. Spherical rather than ellipsoidal
because the difference is under a pixel at every size these render at, and the
spherical form is thirty lines somebody can check.

## The frames

**Overview: Europe, fixed, identical for every sector.** An extent that moved
with the data would make two sectors incomparable at the moment a reader is
comparing them, and the empty space is information — steel's absence from the
south is a fact about steel. `build_maps.py` fails the build if a project falls
outside it rather than letting it vanish.

**Crop: the subject and its dependencies, padded, minimum 800 km across.**
Neighbours are drawn where they fall inside that frame, technology before
sector, and they never move it.

Two parameters here were set by looking at the result rather than by argument,
and both are worth knowing before they are changed:

- **The other reading was built and rejected.** Letting neighbours grow the
  frame, nearest first, up to a cap gave Brevik a crop from Scotland to Estonia
  in order to reach Gotland — one small mark, two grey ones and a great deal of
  empty North Sea.
- **The minimum span was 500 km and is 800.** At 500, Salzgitter's crop was very
  nearly blank: inland Europe has no coast, and the nearest borders sat just
  outside the frame. At 800 the same crop is recognisably Germany. The cost is
  that a coastal crop carries more sea; the alternative was a plant floating in
  white space.

## Screenshots

`screenshots/`, at 1280 and at 430, taken from `next start` against the built
site — one element screenshot of `figure.geo` per page, at device scale 2, with
the sticky site header and section nav hidden so they do not paint over the
figure's own heading.

Brevik and SALCOS stage one for the crop; cement and steel for the overview; and
the ArcelorMittal conversion, which is the frame the exclusion is about — the one
crop that draws a cancelled project, and the only place the ring's third key line
carries its clause.

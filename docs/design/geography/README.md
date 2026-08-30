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

## One rule for the marks

    dot        a works
    triangle   a store, pointing down, because that is where the tonne goes
    filled     it is running
    hollow     it is not — paused, cancelled, or not yet built
    ring       the one this page is about

A third mark for transport infrastructure is in the brief and is not drawn:
no such node exists. Every named hub in the register — Antwerp@C, Brunsbüttel,
the Dunkerque CO₂ terminal — is named without being sited. See `scope.md`,
"A node in the geo layer requires a source-stated position".

**The key names only the distinctions the picture draws.** Fill is always
explained, in both directions — "filled: operating or under construction" and
"hollow: not running", so a reader who sees only filled marks still learns what
filled means. Shape is explained only on a frame that actually carries a store;
on one that does not, "a dot is a works" would put a second identical filled dot
in the key beside the one explaining fill, which reads as a mistake. The wording
is tier 1, in `geoKeyProse`, and divides on the same statuses the picture and
the standfirst above it divide on.

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
site. Brevik and SALCOS stage one for the crop; cement and steel for the
overview.

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

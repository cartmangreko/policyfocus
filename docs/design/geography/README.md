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

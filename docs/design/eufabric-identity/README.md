# Handoff: eufabric logo & identity

## Overview
eufabric is a publication that follows how Europe's industry is evolving — lab technologies, the projects that turn them into steel/cement/chemicals/batteries, and the rules and money that decide which get built. This package specifies its **logo (the mark + logotype)** and core identity tokens so they can be rebuilt as production code.

## About the Design Files
The files in this bundle are **design references created in HTML** — prototypes showing intended look and behavior, not production code to copy directly. The task is to **recreate these designs in your target codebase's existing environment** (React, Vue, SwiftUI, native, etc.) using its established patterns, or, if no environment exists, to pick the most appropriate framework and implement there. The mark is pure SVG geometry generated from a small algorithm (below) — reimplement that generator; do not hand-place lines.

## Fidelity
**High-fidelity.** Final colors, typography, geometry, and construction are specified. Recreate pixel-accurately. The mark should be reproduced as **resolution-independent SVG**, driven by the construction rules — not traced.

---

## The Mark

A plain-weave lattice: four warp (vertical) and four weft (horizontal) threads on a square module, one constant line weight, alternating over/under at every crossing, with each thread running past the grid so the weave reads as *being assembled* rather than finished. Reads as lattice, circuit, or loom depending on how long you look.

### Geometry (viewBox `0 0 120 120`, `overflow: visible`)
- **Thread positions** (both axes): `24, 48, 72, 96` — a 24-unit module pitch.
- **Thread extent**: each thread runs from `16` to `104` (8 units of overhang past the outermost crossings on each end).
- **Line weight**: `stroke-width: 4` (single weight throughout), `stroke-linecap: butt`.
- **Over/under rule**: at crossing `(i, j)` (column i, row j, both 0-indexed):
  - if `(i + j)` is **even** → the **weft (horizontal)** thread is on top, so the **warp (vertical)** thread is broken there.
  - if `(i + j)` is **odd** → the **warp (vertical)** thread is on top, so the **weft (horizontal)** thread is broken there.
- **The break**: the under-thread is not drawn through the crossing — it stops `5` units before the crossing center and resumes `5` units after (a gap of 10 units centered on the node). This is what creates the woven over/under illusion with a single flat line weight.

### Generator (reference pseudocode)
```
POS = [24, 48, 72, 96]; START = 16; END = 104; GAP = 5;
segments = [];

// weft — horizontal threads at each Y; broken where (i+j) even
for (j, Y) in POS:
  unders = [ POS[i] for i where (i+j) even ]      // x-positions where this weft passes UNDER
  cursor = START
  for ux in sort(unders):
     segments.push(line(cursor, Y, ux - GAP, Y)); cursor = ux + GAP
  segments.push(line(cursor, Y, END, Y))

// warp — vertical threads at each X; broken where (i+j) odd
for (i, X) in POS:
  unders = [ POS[j] for j where (i+j) odd ]        // y-positions where this warp passes UNDER
  cursor = START
  for uy in sort(unders):
     segments.push(line(X, cursor, X, uy - GAP)); cursor = uy + GAP
  segments.push(line(X, cursor, X, END))
```
Render each segment as an SVG `<line>` with the ink color and stroke-width 4.

### Variants
- **Lattice (default)**: lines only.
- **Circuit**: add small filled squares (`7×7`, centered) at the "over" crossings — i.e. every `(i,j)` where `(i+j)` is even — in the signal blue. This reads as nodes on a board.
- **Loom**: same as lattice; the overhang already reads as loose warp/weft ends.

### Sizing & scaling
- The mark is a pure ratio; scale by setting SVG width/height. It holds from favicon (24–32px) up to poster size.
- At small sizes (≤40px) bump stroke-width to ~6 (in viewBox units) for legibility — used on the business card, favicons, and masthead lockup.
- Clear space: keep at least one module (the equivalent of ~24 viewBox units) of empty space around the mark.

### Color pairings on backgrounds
- On **paper** (`#F4F2EA`): ink mark (`#211F1B`).
- On **ink** (`#211F1B`): paper mark (`#F4F2EA`).
- On **signal** (`#2B54D8`): paper mark (`#F4F2EA`).

---

## The Logotype

`eu|fabric` — set as one word, `eu` + `fabric`, joined by a single hairline "seam".

- **Case**: always lowercase.
- **Type**: Helvetica / Helvetica Neue, **Bold (700)** for the letters.
- **Tracking**: `letter-spacing: -0.05em` at display size (tighten less at small sizes, ~-0.02em to -0.03em).
- **The seam**: a single `|` character between `eu` and `fabric`, set in **regular weight (400)** and colored **signal blue** (`#2B54D8`). It is the *only* place the accent color touches the name. On dark backgrounds a lighter blue (`#7f9bff`) may be used for the seam for contrast.
- **Lockup**: when paired with the mark (e.g. masthead, card), place the mark to the left or right with the mark's height ≈ the cap height to ~1.4× the logotype height; gap ≈ 14px at a 20px logotype.

Example markup:
```html
<span style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
             font-weight:700; letter-spacing:-0.05em">eu<span
   style="color:#2B54D8; font-weight:400">|</span>fabric</span>
```

---

## Design Tokens

### Color
| Token  | Role                          | oklch                 | hex       |
|--------|-------------------------------|-----------------------|-----------|
| Ink    | Type, mark, rules             | `oklch(.22 .008 95)`  | `#211F1B` |
| Paper  | Ground (warm, never pure white)| `oklch(.975 .006 90)`| `#F4F2EA` |
| Signal | One accent thread only, never a fill | `oklch(.55 .13 250)` | `#2B54D8` |
| Signal-light | Seam/mark accent on dark    | —                     | `#7f9bff` |
| Rule / hairline (subtle) | Section dividers, card borders | — | `#DDD9CF` |
| Muted text | Labels, captions           | —                     | `#6E6A60` |
| Body text | Paragraph ink              | —                     | `#3a3833` |

Color rules: **no gradients**, ever. Signal blue is a *line*, not a fill — used for the seam, circuit nodes, and small accents only, never as a background block except in dedicated color/brand contexts.

### Typography
- **Family**: Helvetica Neue / Helvetica / Arial fallback throughout (Swiss, single family).
- **Display / logotype**: 700, letter-spacing -0.045em to -0.05em.
- **Section labels / eyebrows**: 11px, `letter-spacing: 0.2em`, `text-transform: uppercase`, muted (`#6E6A60`).
- **Body**: ~20px/1.5, `#3a3833`, `text-wrap: pretty`.
- **Specs / mono values**: `ui-monospace, monospace`, small, signal blue for the figure.

### Geometry / layout
- Single line weight discipline: `1px` hairline rules (`#DDD9CF`), and the mark's single 4u stroke. Avoid mixed weights.
- Grids use a 1px gap on a `#DDD9CF` background to produce clean hairline dividers between cells.
- Border radius: **0** everywhere except app-icon tiles (favicon) at `16px` and avatar at `50%`.
- No shadows.

---

## Assets
- **No raster assets required** for the logo — the mark is generated SVG; the logotype is live text (Helvetica). Photos shown in the masthead demo are placeholders only.
- **Favicon**: render the mark (stroke ~6 in viewBox units) in paper on an ink or signal `16px`-radius tile; export at 16/32/180px.
- **Fonts**: Helvetica Neue is a system font on Apple platforms; on web, use it if licensed, otherwise substitute a close neo-grotesque already in the codebase (e.g. an existing Helvetica/Arial stack, or a licensed alternative). Do not swap in Inter/Roboto if a true Helvetica/neo-grotesque is available.

## Screenshots (`/screenshots`)
Visual reference for the intended result:
- `mark-readings.png` — the logotype + mark (hero).
- `construction.png` — the plain-weave construction grid with the 24u/4u/8u specs.
- `in-use.png` — applications: masthead feed, business card, favicon tiles, avatar.

## Files (design references in this project)
- `Mark.dc.html` — the mark generator (SVG + the over/under algorithm). This is the source of truth for the geometry.
- `eufabric Identity.dc.html` — full identity showcase: construction, logotype, color, mark on backgrounds, and applications (masthead, business card, favicons, avatar).

Both are HTML prototypes — reference them for exact values, then rebuild the mark from the generator above in your own environment.

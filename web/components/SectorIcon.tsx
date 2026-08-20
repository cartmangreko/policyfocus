import type { SectorSlug } from "@/lib/types";

// One geometric line icon per sector, drawn to a single 24-unit grid at a
// single 1.5 stroke weight, round caps and joins throughout. They are hand-cut
// rather than pulled from an icon set: half the spine (plastics converting,
// carbon capture, clean tech, aluminium) has no entry in any general set, and
// a page mixing a library icon with a bespoke one shows the seam immediately.
// One hand is easier to keep honest than two.
//
// Every icon is a NOUN from the sector's own world — an I-beam, a mixer drum,
// a bottle — never an abstract mark. A reader who knows the industry should
// recognise it before reading the label; that is the whole job, and it is why
// none of these is a circle with a letter in it.
//
// Colour comes from the accent token, applied as `color` so the stroke follows
// currentColor. The tokens live in globals.css under one comment block, and
// the rule they obey is the brief's: hairlines, chips and icon strokes only,
// never a background, never a large fill.

const PATHS: Record<SectorSlug, React.ReactNode> = {
  // An I-beam, end on: the section every steel catalogue opens with.
  steel: (
    <>
      <path d="M5 4h14M5 20h14M12 4v16" />
      <path d="M8 4v1.5M16 4v1.5M8 20v-1.5M16 20v-1.5" />
    </>
  ),
  // A mixer drum on its axis.
  cement: (
    <>
      <path d="M4 8.5 20 6v12L4 15.5z" />
      <path d="M8 7.9v8.2M14 6.9v10.2" />
    </>
  ),
  // Two ingots, stacked and offset the way they leave the caster.
  alu: (
    <>
      <path d="M3 13.5h12l3-3.5H6z" />
      <path d="M6 19h12l3-3.5H9z" />
    </>
  ),
  // A round-bottomed flask.
  chem: (
    <>
      <path d="M10 3h4M11 3v6.2L5.6 18a2 2 0 0 0 1.7 3h9.4a2 2 0 0 0 1.7-3L13 9.2V3" />
      <path d="M8.2 14h7.6" />
    </>
  ),
  // A blow-moulded bottle: the same family as the flask, one step downstream.
  "chem/plastics": (
    <>
      <path d="M10 2h4v2.6c0 1 2.4 2 2.4 4.4V19a2 2 0 0 1-2 2h-4.8a2 2 0 0 1-2-2V9c0-2.4 2.4-3.4 2.4-4.4z" />
      <path d="M7.6 12h8.8" />
    </>
  ),
  // A pane with the light running across it.
  glass: (
    <>
      <path d="M4 3h16v18H4z" />
      <path d="M9 3 4 10M20 5l-9 12" />
    </>
  ),
  // A sheet with the corner turned.
  paper: (
    <>
      <path d="M6 2h8l5 5v15H6z" />
      <path d="M14 2v5h5" />
      <path d="M9 13h7M9 17h7" />
    </>
  ),
  // Log end grain: the rings are what makes it wood rather than a pipe.
  wood: (
    <>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="5" />
      <circle cx="12" cy="12" r="1.6" />
    </>
  ),
  // An ear of wheat.
  foodbev: (
    <>
      <path d="M12 21V8" />
      <path d="M12 8c0-2.6 1.8-4.6 4-5-.2 2.8-1.8 4.6-4 5z" />
      <path d="M12 8c0-2.6-1.8-4.6-4-5 .2 2.8 1.8 4.6 4 5z" />
      <path d="M12 14c0-2.2 1.6-3.8 3.6-4.2-.2 2.4-1.6 3.9-3.6 4.2z" />
      <path d="M12 14c0-2.2-1.6-3.8-3.6-4.2.2 2.4 1.6 3.9 3.6 4.2z" />
    </>
  ),
  // A carrier bag.
  retail: (
    <>
      <path d="M4 7h16l-1.4 14H5.4z" />
      <path d="M8.5 7V5.5a3.5 3.5 0 0 1 7 0V7" />
    </>
  ),
  // A cup on a saucer.
  horeca: (
    <>
      <path d="M4 5h13v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z" />
      <path d="M17 7h1.6a2.4 2.4 0 0 1 0 4.8H17" />
      <path d="M3 20h16" />
    </>
  ),
  // A pylon: the grid, not a light bulb.
  power: (
    <>
      <path d="M7 21 12 3l5 18" />
      <path d="M8.6 15h6.8M9.6 11h4.8" />
      <path d="M4 8h5.5M14.5 8H20" />
    </>
  ),
  // A bin with the lid on.
  waste: (
    <>
      <path d="M4 7h16" />
      <path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
      <path d="M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13" />
      <path d="M10 11v6M14 11v6" />
    </>
  ),
  // A hull on the water.
  ship: (
    <>
      <path d="M3 17h18l-2.4 4H5.4z" />
      <path d="M5 17V9h14v8" />
      <path d="M9 9V5h6v4" />
    </>
  ),
  air: (
    <>
      <path d="M12 2c1.4 0 2.2 2.2 2.2 5.4v2.2l7.3 4.3v2.3l-7.3-2.4v4l2.6 2v1.6L12 20.4l-4.8 1v-1.6l2.6-2v-4l-7.3 2.4v-2.3l7.3-4.3V7.4C9.8 4.2 10.6 2 12 2z" />
    </>
  ),
  auto: (
    <>
      <path d="M3 15v-2.2l2-4.4A2 2 0 0 1 6.8 7h10.4a2 2 0 0 1 1.8 1.4l2 4.4V15" />
      <path d="M3 15h18v3H3z" />
      <circle cx="7.5" cy="18" r="1.8" />
      <circle cx="16.5" cy="18" r="1.8" />
      <path d="M5.4 12.6h13.2" />
    </>
  ),
  // A tower crane over a footing.
  build: (
    <>
      <path d="M3 6h18" />
      <path d="M8 6v15M8 21H3M8 21h5" />
      <path d="M6 6 8 2l2 4" />
      <path d="M18 6v4" />
      <path d="M16.4 10h3.2v3h-3.2z" />
    </>
  ),
  // A cell, terminals out.
  batsol: (
    <>
      <path d="M2 8h16v8H2z" />
      <path d="M18 11h3v2h-3z" />
      <path d="M6.5 10.5v3M10.5 10.5v3M14.5 10.5v3" />
    </>
  ),
  // A three-blade turbine.
  clean: (
    <>
      <path d="M12 12V3M12 12l7.8 4.5M12 12 4.2 16.5" />
      <circle cx="12" cy="12" r="1.6" />
      <path d="M9.6 21h4.8l-1.2-6.9h-2.4z" />
    </>
  ),
  // Carbon going down into the strata.
  ccs: (
    <>
      <path d="M12 2v10" />
      <path d="M8.6 8.6 12 12l3.4-3.4" />
      <path d="M3 15.5h18M3 19h18" />
      <path d="M7 15.5V19M13 15.5V19M18 15.5V19" />
    </>
  ),
};

// A child sector's accent is a lighter cut of its parent's, so the two read as
// one family at a glance — chemicals and plastics converting sit next to each
// other on most pages, and a child with an unrelated hue reads as a separate
// industry. The token key drops the slash, since a CSS custom property cannot
// carry one.
export function accentVar(slug: string): string {
  return `--acc-${slug.replace("/", "-")}`;
}

export default function SectorIcon({
  slug,
  size = 16,
  className,
}: {
  slug: SectorSlug;
  size?: number;
  className?: string;
}) {
  const path = PATHS[slug];
  if (!path) return null;
  return (
    <svg
      className={`sector-icon${className ? ` ${className}` : ""}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ color: `var(${accentVar(slug)})` }}
      aria-hidden="true"
      focusable="false"
    >
      {path}
    </svg>
  );
}

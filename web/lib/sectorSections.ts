import { SECTORS } from "./data";
import { ecosystemForSector } from "./ecosystems";
import { hasMap } from "./transition";
import {
  getSectionSpecs,
  getSectorH1,
  getSectorNames,
  getSectorSlots,
  renderHeading,
} from "./sitetext";

// THE SECTION SEQUENCE, resolved for one sector — brief 5 §2.
//
// The sequence itself is data (data/prose.json → sector_sections) so the
// wording is reviewable in one place; this module is what turns it into the
// thing the page and the nav both render, and the reason both render from ONE
// list is §8's check_section_order: nav entries equal rendered sections, which
// is a property that holds by construction here rather than by two lists being
// kept in step.
//
// PRESENCE IS THE CALLER'S ANSWER, not this module's. Whether a sector has
// projects is a question for the project data, and this file has no business
// knowing which store answers which section. The page hands in a map of
// section id → has data, and gets back the sections that render, in order.
// A section absent from the map is absent from the page (brief 5 §2: omitted,
// not rendered empty), which makes the map exhaustive by default rather than
// by discipline.

export interface RenderedSection {
  id: string;
  /** The nav label. A fixed short form, the same on every sector. */
  nav: string;
  /** The H2, slots filled from this sector's name slots. */
  h2: string;
}

/** The sector's name slots, resolved through its ecosystem instance, and
 *  failing that through the slug's own entry in sector_names.sector_slots.
 *
 *  THE INSTANCE IS STILL THE FIRST QUESTION, because it is the right keying for
 *  the four slugs an instance claims: chemicals spans two and batteries covers
 *  part of one, so the wording is stored once per industry rather than once per
 *  FIGARO key.
 *
 *  AND IT IS NO LONGER THE ONLY QUESTION, which is the change of 12 October 2026
 *  (brief 17 §B.3). Two slugs render the hub and belong to no instance by a
 *  sector edge: `clean`, because the hydrogen instance deliberately carries none
 *  — hydrogen is not a FIGARO industry and a pseudo-key would corrupt the
 *  input-output join — and `ccs`, because CO2 transport and storage is an
 *  abatement route rather than an industry and is not one of the six tiles
 *  (eufabric-page-specifications.md §4.2). Neither is a data error, and neither
 *  should have to become a seventh ecosystem to be allowed a heading.
 *
 *  STILL THROWS FOR ANYTHING ELSE. A slug with no instance and no entry is a
 *  sector rendering the product template that nobody has named, and a heading
 *  reading "What is being built in European undefined" is a worse way to find
 *  that out than a build failure. */
export function sectorNames(slug: string): { short: string; phrase: string } {
  const eco = ecosystemForSector(slug);
  if (eco) return getSectorNames(eco.id);
  const own = getSectorSlots(slug);
  if (own) return own;
  throw new Error(
    `sector "${slug}" belongs to no ecosystem instance and has no entry in ` +
      `data/prose.json -> sector_names.sector_slots, so it has no name slots and ` +
      `cannot head its own page`
  );
}

/** WHAT TO CALL A SECTOR IN A BREADCRUMB, A FOOTER OR A LINK.
 *
 *  THE SPINE'S LABEL IS NOT ALWAYS THE PAGE'S NAME, and until 12 October 2026 it
 *  did not matter. data/sectors.json is keyed on FIGARO industries and labels
 *  them accordingly: `clean` is "Wind, heat pumps, hydrogen" and `ccs` is
 *  "Carbon capture and fuels", because those are the industries the
 *  input-output join covers. The moment those two slugs started rendering the
 *  hub, a project page's breadcrumb offered "Wind, heat pumps, hydrogen" and
 *  opened a page headed "Hydrogen in Europe's industrial transition" — the link
 *  and its destination calling the same thing two names.
 *
 *  SO A SECTOR THAT RENDERS THE HUB IS CALLED BY ITS NAME SLOT, capitalised, and
 *  every other sector keeps the spine's label — which is right, because a sector
 *  rendering the register directory IS the FIGARO industry and has no name slot
 *  of its own. One function, so a third caller cannot invent a third answer. */
export function sectorLabel(slug: string): string {
  if (!hasMap(slug)) return SECTORS[slug as keyof typeof SECTORS] ?? slug;
  const { short } = sectorNames(slug);
  return short.charAt(0).toUpperCase() + short.slice(1);
}

/** The page's H1: "{Short} in Europe's industrial transition". */
export function sectorH1(slug: string): string {
  return getSectorH1(sectorNames(slug));
}

/** The sections this sector renders, in the specified order.
 *
 *  `present` says which sections have data. An id the specification does not
 *  know is a build failure rather than an ignored key: the map is how a section
 *  gets onto the page, and a typo in it would silently drop one. */
export function renderedSections(
  slug: string,
  present: Record<string, boolean>,
): RenderedSection[] {
  const specs = getSectionSpecs();
  const known = new Set(specs.map((s) => s.id));
  for (const id of Object.keys(present)) {
    if (!known.has(id)) {
      throw new Error(
        `"${id}" is not a section in data/prose.json → sector_sections; the sequence ` +
          `is ${[...known].join(", ")}`
      );
    }
  }
  const names = sectorNames(slug);
  return specs
    .filter((s) => present[s.id])
    .map((s) => ({ id: s.id, nav: s.nav, h2: renderHeading(s.h2, names) }));
}

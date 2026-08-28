import fs from "node:fs";
import path from "node:path";
import { getSiteSummary } from "./summaries";

// Reviewed prose — tier 2 of the three-tier rule in sources/scope.md ("No
// free-generated text on the site"). The text lives in data/prose.json with a
// recorded review status — one review pass per text, then "approved" — and
// renders unchanged until deliberately edited; the only thing computed here is
// the slot substitution, and every slot resolves to a field of the
// gate-checked site summary object. An unknown slot is a build failure, never
// an approximation.

const PROSE_PATH = path.join(process.cwd(), "..", "data", "prose.json");

export type ProseStatus = "final" | "approved" | "draft" | "draft-pending-george-edit";

/** A block renders only once someone has read it. Everything else falls back
 *  to computed text, which is tier 1 and needs no review. */
export function isReviewed(status: ProseStatus): boolean {
  return status === "approved" || status === "final";
}

interface ProseDoc {
  masthead: { status: ProseStatus; descriptor: string; positioning: string };
  perimeter: { status: ProseStatus; template: string; reviewed?: string };
  /** The launch perimeter — which industries are covered and which are
   *  deliberately not. Rendered beside the perimeter paragraph on the coverage
   *  page THROUGH getLaunchPerimeter below, which returns null until the block
   *  is reviewed: an unread claim about scope is the one claim on this site
   *  that should not appear before somebody has read it. */
  launch_perimeter?: { status: ProseStatus; paragraph: string; reviewed?: string };
  coverage_declarations: {
    status: ProseStatus;
    files: Record<string, string>;
    reviewed?: string;
  };
  coverage_line: { status: ProseStatus; template: string; reviewed?: string };
  /** Read by sources/build_ego_views.py, not here: the note is rendered at
   *  build time into data/graph/ego/<file>.json, so the page reads a finished
   *  sentence. Declared so this interface stays the one description of the
   *  store's shape. */
  ego_notes: {
    status: ProseStatus;
    files: Record<string, string>;
    reviewed?: string;
  };
  /** One sentence per sector that has a transition map, naming the transitions
   *  it covers. Rendered by the sector page THROUGH getTransitionNote below,
   *  which returns null until the block is reviewed — an unreviewed sentence
   *  is a sentence nobody has read, and the page has a computed fallback. */
  transition_notes: {
    status: ProseStatus;
    reviewed?: string | null;
    sectors: Record<string, { transitions: string[]; sentence: string }>;
  };
  /** The standing orientation paragraph, one per mapped sector: what the sector
   *  is, why it is hard, the technology paths, how policy frames it, and the
   *  question the page then answers. Reviewed prose, four fixed beats, nearly
   *  number-free — see the _comment in data/prose.json. Returned by
   *  getSectorOrientation below, which is null until the block is reviewed. */
  /** The regenerated lead block, held for review — brief 4 §6. NOT READ BY THE
   *  SITE, and there is no getter below on purpose: the sector page renders the
   *  BUILT lead in data/transition/lead/<sector>.json, which is computed and
   *  gated (tier 1). This block is a copy of that text, put where prose is
   *  reviewed so the register can be read and edited as words; an approval
   *  moves the edited sentence into data/transition/overrides.json, which is
   *  where a reviewed lead has always gone. Declared here so this interface
   *  stays the one description of the store's shape. */
  sector_lead?: {
    status: ProseStatus;
    reviewed?: string | null;
    sectors: Record<
      string,
      {
        fingerprint: string;
        template_version: number;
        sentence: string;
        why_it_matters: string;
        facts: { id: string; text: string; as_of: string }[];
      }
    >;
  };
  /** One reviewed two-sentence description per ecosystem instance — what it
   *  contains and where its boundary runs (page specifications §4.2). Returned
   *  by getEcosystemDescription below, which is null until the block is
   *  reviewed AND the instance has text: the tile then has no hover text and
   *  the coverage page lists no description, which is the right thing for a
   *  boundary nobody has written down yet. */
  ecosystem_descriptions?: {
    status: ProseStatus;
    reviewed?: string | null;
    ecosystems: Record<string, { description: string }>;
  };
  /** The two name slots per ecosystem instance — brief 5 §2.1. Required for
   *  all six and gated by sources/check_h2_templates.py: unlike every other
   *  block here there is no null-until-reviewed path, because a heading with an
   *  unfilled slot is not a heading. Keyed on ecosystem id; see
   *  lib/ecosystems.ts for the slug → instance resolution. */
  sector_names: {
    status: ProseStatus;
    reviewed?: string | null;
    sectors: Record<string, { short: string; phrase: string }>;
  };
  /** The fixed section sequence and the H1/H2 templates that head it — brief 5
   *  §2. The array's order is the render order and the nav order both, and
   *  sources/check_section_order.py fails the build where the template
   *  disagrees with it. */
  sector_sections: {
    status: ProseStatus;
    reviewed?: string | null;
    h1: string;
    sections: { id: string; nav: string; h2: string }[];
    /** Headings that are not one of the numbered questions — Sources, and
     *  nothing else today. Stored here so the no-free-text rule has no
     *  exception to be widened later. */
    unnumbered: { id: string; h2: string; why?: string }[];
  };
  /** The Opportunity section's wording — brief 5 §4. Sub-headings, the lead
   *  sentence templates the Python builder fills, and the support-fact and
   *  window templates the section renders. Required, like the section
   *  sequence: none of it has a computed fallback. */
  opportunity: {
    status: ProseStatus;
    reviewed?: string | null;
    lead: Record<string, string>;
    headings: Record<string, string>;
    support_fact: Record<string, string>;
    support_window: Record<string, string>;
    signals: Record<string, string>;
  };
  sector_orientation?: {
    status: ProseStatus;
    reviewed?: string | null;
    sectors: Record<string, { paragraph: string }>;
  };
}

let cached: ProseDoc | null = null;

function readProse(): ProseDoc {
  if (cached) return cached;
  cached = JSON.parse(fs.readFileSync(PROSE_PATH, "utf-8")) as ProseDoc;
  return cached;
}

/** The two lines under the wordmark: the descriptor, then the positioning
 *  sentence. Locked text — George's wording, reviewed — so nothing here
 *  templates, truncates or recombines them. */
export function getMasthead(): { descriptor: string; positioning: string } {
  const { descriptor, positioning } = readProse().masthead;
  return { descriptor, positioning };
}

/**
 * The perimeter paragraph with its slots rendered from the site summary.
 * Slot mapping — measures_count: site.measures; acts_count: site.files;
 * sectors_count: site.sectors.total_reach (every sector the register names or
 * reaches, which is what "across N sectors" claims). A slot this map cannot
 * answer for throws, so a new slot in the prose without a summary counterpart
 * stops the build instead of shipping a guess.
 */
export function getPerimeterProse(): string {
  const site = getSiteSummary();
  const slots: Record<string, number> = {
    measures_count: site.measures,
    acts_count: site.files,
    sectors_count: site.sectors.total_reach,
  };
  return readProse().perimeter.template.replace(/\{([a-z_]+)\}/g, (_, name: string) => {
    const value = slots[name];
    if (value === undefined) {
      throw new Error(
        `perimeter prose slot {${name}} has no counterpart in the site summary object`
      );
    }
    return String(value);
  });
}

/** Which industries the platform covers at launch, and which it does not, or
 *  null while the block is unreviewed. The coverage page renders nothing extra
 *  in that case — it is a paragraph the page did not carry at all until
 *  brief 4 §1. */
export function getLaunchPerimeter(): string | null {
  const block = readProse().launch_perimeter;
  if (!block || !isReviewed(block.status)) return null;
  return block.paragraph;
}

/** What one ecosystem contains, or null. Null covers three states that are the
 *  same state to a reader — the block is unreviewed, the instance has no entry,
 *  or its entry is still empty — and every surface renders nothing in all
 *  three. Nothing falls back to `sector_scope` in the ecosystem data: that is a
 *  note to whoever maintains the edges, not a sentence written for a reader. */
export function getEcosystemDescription(id: string): string | null {
  const block = readProse().ecosystem_descriptions;
  if (!block || !isReviewed(block.status)) return null;
  return block.ecosystems[id]?.description?.trim() || null;
}

/** The stored single-pass declaration for one file, in audience terms, or
 *  null when the file carries none. */
export function getCoverageDeclaration(file: string): string | null {
  return readProse().coverage_declarations.files[file] ?? null;
}

/** THE ACTS-DECODED COUNTER IS NOT RENDERED ANYWHERE, and this getter is gone
 *  with it. The line ran at the foot of the front page — "N acts decoded so
 *  far" beside a link to /coverage — and it sold the register on a page about
 *  the industries.
 *
 *  The reviewed text stays in data/prose.json rather than being deleted: it is
 *  approved prose, it is still accurate, and an About or Method page is where
 *  it would come back. Deleting it would mean re-reviewing it to get it back.
 *  The block carries a note saying it renders nowhere, so it is not mistaken
 *  for prose that has quietly stopped appearing. */

/** The reviewed sentence for a sector's transition map, or null while the block
 *  is still a draft. Null is not an error: web/lib/prose.ts renders the
 *  computed sentence instead, and the draft sits in data/prose.json where
 *  sources/check_sector_schema.py prints it on every run. */
/** The sector's orientation paragraph, or null. Null covers both an unreviewed
 *  block and a sector nobody has written one for; the page renders nothing
 *  extra in either case and opens on the lead block, exactly as it did before
 *  this paragraph existed. Unlike the transition note there is no computed
 *  fallback, and there should not be: standing context is the one thing on this
 *  page that cannot be derived from the panels. */
export function getSectorOrientation(sector: string): string | null {
  const block = readProse().sector_orientation;
  if (!block || !isReviewed(block.status)) return null;
  return block.sectors[sector]?.paragraph ?? null;
}

export function getTransitionNote(sector: string): string | null {
  const block = readProse().transition_notes;
  if (!block || !isReviewed(block.status)) return null;
  return block.sectors[sector]?.sentence ?? null;
}

/** The sector's two name slots, by ecosystem id.
 *
 *  THIS ONE THROWS. Every other getter in this file returns null for an
 *  unreviewed or unwritten block, because every other block is prose a surface
 *  can do without. These slots are not: they are the subject of every heading
 *  on the page, and a page that fell back would head nine sections with a hole
 *  in them. A missing instance or an empty slot is a build failure, and
 *  sources/check_h2_templates.py catches it before the build gets here. */
export function getSectorNames(ecosystem: string): { short: string; phrase: string } {
  const block = readProse().sector_names;
  const row = block.sectors[ecosystem];
  if (!row || !row.short.trim() || !row.phrase.trim()) {
    throw new Error(
      `sector_names has no filled short and phrase for ecosystem "${ecosystem}"`
    );
  }
  return row;
}

/** The section sequence, in order. The array is the specification: a section
 *  renders where this says it renders, or the gate fails. */
export function getSectionSpecs(): { id: string; nav: string; h2: string }[] {
  return readProse().sector_sections.sections;
}

/** A heading with its slots filled.
 *
 *  Two slots, {short} and {phrase}, and the capitalisation rule from brief 5
 *  §2.1: `phrase` is stored lower case and is capitalised only where it OPENS
 *  the heading. No template does that today; the rule is implemented anyway,
 *  because the alternative is storing a second capitalised copy of the phrase
 *  and letting the two drift. An unknown slot throws rather than rendering the
 *  braces. */
export function renderHeading(template: string, names: { short: string; phrase: string }): string {
  return template.replace(/\{([A-Za-z_]+)\}/g, (_, slot: string, at: number) => {
    const key = slot.toLowerCase();
    if (key !== "short" && key !== "phrase") {
      throw new Error(
        `heading template "${template}" has slot {${slot}}, and the only slots a ` +
          `heading takes are {short} and {phrase}`
      );
    }
    const value = names[key];
    const capital = at === 0 || slot[0] === slot[0].toUpperCase();
    return capital ? value.charAt(0).toUpperCase() + value.slice(1) : value;
  });
}

/** The page's H1. One template for every sector, `short` capitalised into it. */
export function getSectorH1(names: { short: string; phrase: string }): string {
  return renderHeading(readProse().sector_sections.h1, names);
}

/** An unnumbered heading — Sources — by section id. Throws for an id the block
 *  does not carry, on the same reasoning as the name slots: a heading with no
 *  reviewed wording behind it is free text, and this page does not have any. */
export function getUnnumberedH2(id: string): string {
  const row = readProse().sector_sections.unnumbered.find((u) => u.id === id);
  if (!row) {
    throw new Error(
      `data/prose.json -> sector_sections.unnumbered has no heading for "${id}"`
    );
  }
  return row.h2;
}

/** The Opportunity section's wording. Throws for an unreviewed block, on the
 *  same reasoning as the name slots: the section is nine tenths computed and
 *  the tenth that is words has no computed form to fall back to. */
export function getOpportunityProse() {
  const block = readProse().opportunity;
  if (!isReviewed(block.status)) {
    throw new Error(
      `data/prose.json -> opportunity is ${block.status}; the Opportunity section has ` +
        `no computed fallback for its headings`
    );
  }
  return block;
}

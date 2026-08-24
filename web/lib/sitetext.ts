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

/** The stored single-pass declaration for one file, in audience terms, or
 *  null when the file carries none. */
export function getCoverageDeclaration(file: string): string | null {
  return readProse().coverage_declarations.files[file] ?? null;
}

/** The home page's one-line coverage statement, its act count rendered from
 *  the site summary — same slot discipline as the perimeter paragraph. */
export function getCoverageLine(): string {
  const site = getSiteSummary();
  return readProse().coverage_line.template.replace(/\{acts_count\}/g, String(site.files));
}

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

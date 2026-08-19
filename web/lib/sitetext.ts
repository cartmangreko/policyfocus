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

export type ProseStatus = "final" | "approved" | "draft-pending-george-edit";

interface ProseDoc {
  masthead: { status: ProseStatus; tagline: string; subline: string };
  perimeter: { status: ProseStatus; template: string; reviewed?: string };
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
}

let cached: ProseDoc | null = null;

function readProse(): ProseDoc {
  if (cached) return cached;
  cached = JSON.parse(fs.readFileSync(PROSE_PATH, "utf-8")) as ProseDoc;
  return cached;
}

export function getMasthead(): { tagline: string; subline: string } {
  const { tagline, subline } = readProse().masthead;
  return { tagline, subline };
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

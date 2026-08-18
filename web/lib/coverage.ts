import { FILES, getAllMeasures } from "./data";
import {
  getFileBasis,
  getFileSources,
  getLastUpdated,
  getReadHistory,
  getQueued,
} from "./files";
import type { BasisStatus, FileCelex, QueuedItem, ReadHistory } from "./files";

// What the site covers, stated as a table rather than as a sentence. Every
// column is derived at build time: the register answers "how many measures",
// the manifest answers "what document and what standing", the sources
// directory answers "how many times was it read".
//
// The reads column is the deliberately unflattering one. Two files have been
// read once; four have been read twice and reconciled. Publishing that is
// cheaper than being asked.

export interface CoverageFile {
  slug: string;
  title: string;
  /** Procedure or consolidation reference, as lib/data.ts states it. */
  code: string;
  celexes: FileCelex[];
  basis: BasisStatus | null;
  measures: number;
  reads: ReadHistory;
  lastUpdated: string | null;
}

export function getCoverage(): CoverageFile[] {
  const measures = getAllMeasures();
  return Object.entries(FILES)
    .map(([slug, meta]) => ({
      slug,
      title: meta.name,
      code: meta.code,
      celexes: getFileSources(slug),
      basis: getFileBasis(slug),
      measures: measures.filter((m) => m.file === slug).length,
      reads: getReadHistory(slug),
      lastUpdated: getLastUpdated(slug),
    }))
    // Most recently updated first; files with no fetch date (read from a local
    // text before the fetcher existed) sort last rather than pretending to a
    // date.
    .sort((a, b) => (b.lastUpdated ?? "").localeCompare(a.lastUpdated ?? "") || a.slug.localeCompare(b.slug));
}

/**
 * The home page's "recently added" list — the same rows, cut to the four most
 * recently fetched. A placeholder for a what-changed feed, and honest about
 * what it is: this is when the DOCUMENT was last fetched, not when anything
 * about it changed.
 */
export function getRecentlyAdded(limit = 4): CoverageFile[] {
  return getCoverage()
    .filter((f) => f.lastUpdated !== null)
    .slice(0, limit);
}

export function getQueuedItems(): QueuedItem[] {
  return getQueued();
}

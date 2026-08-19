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
// The read history stays in the object even though the page now states it as
// a two-value verification badge: the badge is derived from `reads`, and the
// dockets and pass artifacts behind it are unchanged in sources/.

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

/**
 * The weight-data situation, stated once and computed from the rows as built
 * — never asserted. The old hardcoded line claimed weight intensity exists
 * only on omnibus rows; that was true when written and is the kind of claim
 * that rots silently, so whatever this note says is derived from the register
 * at build time and moves when the data does.
 */
export function getWeightNote(): string {
  const all = getAllMeasures();
  const perFile = Object.entries(FILES).map(([slug, meta]) => {
    const rows = all.filter((m) => m.file === slug);
    return {
      title: meta.name.split(" — ")[0],
      rows: rows.length,
      weight: rows.filter((m) => m.weight).length,
      intensity: rows.filter((m) => m.weight_intensity).length,
      intensityNaming: rows.filter((m) => m.weight_intensity && (m.sectors_named?.length ?? 0) > 0)
        .length,
    };
  });

  const withIntensity = perFile.filter((f) => f.intensity > 0);
  const withWeight = perFile.filter((f) => f.weight > 0);
  const list = (fs: typeof perFile, count: (f: (typeof perFile)[number]) => number) =>
    fs.map((f) => `${f.title} (${count(f)} of ${f.rows} measures)`).join(", ");

  let intensityPart: string;
  if (withIntensity.length === 0) {
    intensityPart = "No act on the platform records weight intensity yet.";
  } else {
    const naming = withIntensity.reduce((n, f) => n + f.intensityNaming, 0);
    intensityPart =
      `Weight intensity is recorded on ${list(withIntensity, (f) => f.intensity)} only` +
      (naming === 0
        ? ", and none of those measures names a sector — so no sector-level view of weight is possible, and sector pages show the net position without one."
        : `, of which ${naming} name a sector.`);
  }

  const weightPart =
    withWeight.length > 0
      ? ` The coarser categorical weight field is present on ${list(withWeight, (f) => f.weight)}; it stays on the individual measures and is not aggregated on any summary surface.`
      : "";

  return intensityPart + weightPart;
}

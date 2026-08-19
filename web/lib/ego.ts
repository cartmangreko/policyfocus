import fs from "node:fs";
import path from "node:path";

// The ego views: one act's immediate graph neighbourhood, aggregated by
// sources/build_ego_views.py from data/graph/nodes.json + edges.json and
// written to data/graph/ego/<file>.json. Everything a spoke states — label,
// count, detail string — was composed by the builder from edges that exist;
// this module reads the file as-is and the renderer never writes a number.
// The prebuild step runs `build_ego_views.py --check`, so a stored view that
// has drifted from the graph fails the build instead of rendering.
const EGO_DIR = path.join(process.cwd(), "..", "data", "graph", "ego");

export type EgoGroupRel = "amends" | "repeals" | "depends_on" | "cites" | "sectors";

export interface EgoSpoke {
  id: string;
  kind: "act" | "sector";
  label: string;
  /** Register file slug when the act is one of the seven files, else null. */
  file: string | null;
  href: string | null;
  /** Composed by the builder, e.g. "named by 12 measures · reached by 3 measures". */
  detail: string;
  weight: number;
}

export interface EgoGroup {
  rel: EgoGroupRel;
  title: string;
  spokes: EgoSpoke[];
}

export interface EgoView {
  file: string;
  center: { id: string; label: string; file: string };
  measure_count: number;
  groups: EgoGroup[];
  /** Present only when the file's measures apply to no sector — the computed
   *  sentence that keeps absence from looking like omission. */
  note?: string;
}

const cache = new Map<string, EgoView | null>();

export function getEgoView(file: string): EgoView | null {
  const cached = cache.get(file);
  if (cached !== undefined) return cached;
  const filePath = path.join(EGO_DIR, `${file}.json`);
  const view = fs.existsSync(filePath)
    ? (JSON.parse(fs.readFileSync(filePath, "utf-8")) as EgoView)
    : null;
  cache.set(file, view);
  return view;
}

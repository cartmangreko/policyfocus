import fs from "node:fs";
import path from "node:path";
import { SECTORS, getAllMeasures, getChildren } from "./data";
import { REACH_CHANNEL_LABEL, inferReachChannel } from "./reachChannel";
import type { Measure, SectorSlug } from "./types";

// The act-page computations: what one register file does to the sector spine,
// and — inverted — which files arrive at one sector. Counts come from the
// register rows; the intermediating act behind an indirect reach comes from
// the graph's `cites` edges, because that is where the claim is evidenced
// (every edge carries a source pointer, see sources/scope.md).
const DATA_DIR = path.join(process.cwd(), "..", "data");

interface GraphEdge {
  rel: string;
  from: string;
  to: string;
}

interface GraphNode {
  id: string;
  label: string;
}

let cachedEdges: GraphEdge[] | null = null;
let cachedNodes: Map<string, GraphNode> | null = null;

function edges(): GraphEdge[] {
  cachedEdges ??= JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, "graph", "edges.json"), "utf-8")
  ) as GraphEdge[];
  return cachedEdges;
}

function nodes(): Map<string, GraphNode> {
  if (!cachedNodes) {
    const list = JSON.parse(
      fs.readFileSync(path.join(DATA_DIR, "graph", "nodes.json"), "utf-8")
    ) as GraphNode[];
    cachedNodes = new Map(list.map((n) => [n.id, n]));
  }
  return cachedNodes;
}

/** The act node(s) whose `contains` edges hold this file's measures, plus the
 *  acts those nodes amend. A reached row citing its own base act, or the act
 *  the file exists to amend, is self-reference, not an intermediating act. */
function selfActIds(file: string): Set<string> {
  const own = new Set<string>();
  const prefix = `measure:${file}:`;
  for (const e of edges()) {
    if (e.rel === "contains" && e.to.startsWith(prefix)) own.add(e.from);
  }
  const self = new Set(own);
  for (const e of edges()) {
    if (e.rel === "amends" && own.has(e.from)) self.add(e.to);
  }
  return self;
}

export interface ReachedSector {
  slug: SectorSlug;
  name: string;
  /** Rows of this file that reach the sector. */
  rows: Measure[];
  /** Distinct channel labels those rows arrive through. */
  channels: string[];
  /** Labels of the acts the reaching rows cite, own/amended acts excluded —
   *  the act that intermediates the reach, where the graph evidences one. */
  intermediatingActs: string[];
}

export interface ActReach {
  named: SectorSlug[];
  /** Total distinct sectors the file touches, named or reached. */
  totalReach: number;
  reachedOnly: ReachedSector[];
}

/** "Names N sectors, reaches M" plus the per-sector tags for the reached
 *  cohort. Reached-only means no row in the file names the sector. */
export function getActReach(file: string): ActReach {
  const rows = getAllMeasures().filter((m) => m.file === file);
  const named = new Set<SectorSlug>();
  const touched = new Set<SectorSlug>();
  for (const m of rows) {
    for (const s of m.sectors_named ?? []) {
      named.add(s);
      touched.add(s);
    }
    for (const s of m.sectors_reached ?? []) touched.add(s);
  }

  const self = selfActIds(file);
  const reachedOnly = [...touched]
    .filter((s) => !named.has(s))
    .sort()
    .map((slug) => {
      const reaching = rows.filter((m) => m.sectors_reached?.includes(slug));
      const channels = [
        ...new Set(reaching.map((m) => REACH_CHANNEL_LABEL[inferReachChannel(m)])),
      ].sort();
      const acts = new Set<string>();
      for (const m of reaching) {
        const from = `measure:${file}:${m.id}`;
        for (const e of edges()) {
          if (e.rel === "cites" && e.from === from && !self.has(e.to)) {
            const label = nodes().get(e.to)?.label;
            if (label) acts.add(label);
          }
        }
      }
      return {
        slug,
        name: SECTORS[slug],
        rows: reaching,
        channels,
        intermediatingActs: [...acts].sort(),
      };
    });

  return { named: [...named].sort(), totalReach: touched.size, reachedOnly };
}

/** This file's rows grouped for the act page: one group per sector, a row
 *  filed under the FIRST sector its named list carries (its full list is on
 *  the row and the measure page), rows naming no sector in a final group. */
export interface SectorGroup {
  slug: SectorSlug | null;
  name: string;
  rows: Measure[];
}

export function getActMeasuresBySector(file: string): SectorGroup[] {
  const rows = getAllMeasures().filter((m) => m.file === file);
  const groups = new Map<SectorSlug | null, Measure[]>();
  for (const m of rows) {
    const key = m.sectors_named?.[0] ?? null;
    (groups.get(key) ?? groups.set(key, []).get(key)!).push(m);
  }
  const named = [...groups.entries()]
    .filter((g): g is [SectorSlug, Measure[]] => g[0] !== null)
    .sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0]))
    .map(([slug, list]) => ({ slug, name: SECTORS[slug], rows: list }));
  const rest = groups.get(null);
  return rest
    ? [...named, { slug: null, name: "No sector named — applies by size or activity", rows: rest }]
    : named;
}

// ---------------------------------------------------------------------------
// The inverse: how pressure arrives at one sector, act by act. Uses the same
// parent rollup as getMeasuresForSector, so the panel and the lists above it
// describe the same row set.
// ---------------------------------------------------------------------------

export interface ArrivingAct {
  file: string;
  named: number;
  reached: number;
  /** Distinct channel labels for the reached rows. */
  channels: string[];
}

export interface Arrival {
  /** Files with at least one row naming the sector. */
  direct: ArrivingAct[];
  /** Files whose rows only ever reach the sector. */
  indirect: ArrivingAct[];
}

export function getArrival(slug: SectorSlug): Arrival {
  const own = new Set<SectorSlug>([slug, ...getChildren(slug)]);
  const byFile = new Map<string, { named: Measure[]; reached: Measure[] }>();
  for (const m of getAllMeasures()) {
    const names = m.sectors_named?.some((s) => own.has(s)) ?? false;
    const reaches = m.sectors_reached?.some((s) => own.has(s)) ?? false;
    if (!names && !reaches) continue;
    const entry = byFile.get(m.file) ?? { named: [], reached: [] };
    (names ? entry.named : entry.reached).push(m);
    byFile.set(m.file, entry);
  }
  const toAct = ([file, { named, reached }]: [string, { named: Measure[]; reached: Measure[] }]) => ({
    file,
    named: named.length,
    reached: reached.length,
    channels: [
      ...new Set(reached.map((m) => REACH_CHANNEL_LABEL[inferReachChannel(m)])),
    ].sort(),
  });
  const entries = [...byFile.entries()];
  return {
    direct: entries.filter(([, e]) => e.named.length > 0).map(toAct),
    indirect: entries.filter(([, e]) => e.named.length === 0).map(toAct),
  };
}

import fs from "node:fs";
import path from "node:path";
import type { IconKey } from "@/components/SectorIcon";
import { hasMap } from "./transition";

// THE SIX, read from the node kind — data/transition/ecosystems.json, specified
// in eufabric-page-specifications.md §4.2 and gated by
// sources/check_sector_schema.py.
//
// WHAT THIS REPLACED. A hard-coded array in components/EcosystemTiles.tsx with
// two placeholder ids in it, shipped deliberately as a placeholder while the
// node kind was queued. The array knew four things the data now knows properly:
// which sector a tile points at, that two tiles point at no sector at all, that
// chemicals means two slugs, and that batteries means part of one.
//
// THE ID IS NOT A SECTOR SLUG and cannot be. `chemicals` spans chem and
// chem/plastics; `batteries` covers the battery half of batsol and leaves solar
// in the register; `hydrogen` and `circular-materials` have no sector key at
// all, which is the reason the node kind exists.
export interface Ecosystem {
  id: string;
  name: string;
  /** Which drawing from the set in components/SectorIcon.tsx. Named in the data
   *  rather than derived from the id: the icons are keyed by the noun they
   *  draw, and four of the six borrow a sector's. */
  icon: IconKey;
  sectors: string[];
  /** A sentence, where the sector edge is wider than the instance — batteries
   *  is the case. Null where the edge is exact. */
  sector_scope: string | null;
  technology: string[];
  project: string[];
  measure: string[];
  material: string[];
}

const PATH = path.join(process.cwd(), "..", "data", "transition", "ecosystems.json");

let cached: Ecosystem[] | null = null;

export function getEcosystems(): Ecosystem[] {
  if (!cached) {
    cached = (JSON.parse(fs.readFileSync(PATH, "utf8")) as { ecosystems: Ecosystem[] })
      .ecosystems;
  }
  return cached;
}

/** Where a tile goes.
 *
 *  An instance that maps 1:1 onto a sector that has been BUILT opens that
 *  sector page. Everything else opens /coverage: a cross-cutting instance with
 *  no dataset behind it yet, and a 1:1 instance whose sector still renders the
 *  directory template. §4.2's rendering rule and brief 4 §3 meet here — a tile
 *  never opens a page with nothing on it, and an instance arrives at its own
 *  page by having data, not by an edit to this function. */
export function ecosystemHref(e: Ecosystem): string {
  const only = e.sectors.length === 1 ? e.sectors[0] : null;
  return only && hasMap(only) ? `/sectors/${only}` : "/coverage";
}

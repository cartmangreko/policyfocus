import Link from "next/link";
import SectorIcon, { type IconKey } from "./SectorIcon";
import { hasMap } from "@/lib/transition";

// THE SIX. Eufabric launches narrow: Europe's energy-intensive industries and
// the materials they make (brief 4 §1). These six are the whole front of the
// platform, on the front page and on /sectors, and the same component draws
// them in both places so the two cannot drift into two different lists.
//
// HARD-CODED, AND SAYING SO. Two of the six are not sectors and cannot become
// sector keys: hydrogen production and the recovery industry are not FIGARO
// sectors, so there is no key for them in data/sectors.json. The right home
// for all six is the ecosystem node kind — page specifications §5 step 4,
// moved to the front of the queue by brief 4 §6 — and this list is the
// placeholder until that lands: four tiles keyed to the sector slug they
// already have, two to an ecosystem id that exists nowhere else yet. When the
// node kind arrives, this array is what it replaces.
//
// NO COUNTS. Not a project count, not a measure count, not a status chip. The
// six are at six different depths of build and a number on each one would
// invite a comparison that is about the state of our data rather than about
// the industry.
export interface Tile {
  /** The sector slug where one exists, and the ecosystem id where it does not.
   *  `sector: false` is the second case, and it is what decides the link. */
  id: IconKey;
  name: string;
  /** What the tile contains, where the name does not settle it on its own —
   *  the perimeter in words, per brief 4 §2. */
  scope?: string;
  sector: boolean;
}

export const TILES: Tile[] = [
  { id: "cement", name: "Cement", sector: true },
  { id: "steel", name: "Steel", sector: true },
  {
    id: "chem",
    name: "Chemicals",
    scope: "Organic chemicals and plastics. Fertilisers are read under hydrogen.",
    sector: true,
  },
  { id: "batsol", name: "Batteries", sector: true },
  {
    id: "hydrogen",
    name: "Hydrogen",
    scope: "Production, including ammonia and the fertiliser line.",
    sector: false,
  },
  {
    id: "circular",
    name: "Circular materials",
    scope:
      "The recovery industry: battery recycling, plastics recycling, scrap processing, critical raw material recovery.",
    sector: false,
  },
];

/** Where a tile goes. A sector with a page of its own opens it; everything
 *  else opens the coverage page, which is where what is and is not on the
 *  platform is stated (brief 4 §3). A tile never opens a page that has nothing
 *  on it yet. */
export function tileHref(t: Tile): string {
  return t.sector && hasMap(t.id) ? `/sectors/${t.id}` : "/coverage";
}

export default function EcosystemTiles() {
  return (
    <div className="hairline-grid tile-grid">
      {TILES.map((t) => (
        <Link key={t.id} href={tileHref(t)} className="tile">
          <SectorIcon slug={t.id} size={26} />
          <span className="tile-name">{t.name}</span>
          {t.scope ? <span className="tile-scope">{t.scope}</span> : null}
        </Link>
      ))}
    </div>
  );
}

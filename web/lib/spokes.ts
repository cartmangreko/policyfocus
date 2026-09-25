import { SECTORS } from "./data";
import { sectorNames } from "./sectorSections";
import {
  sectorDependencies,
  sectorPolicyRows,
  sectorProjectRows,
  sectorSupportRows,
} from "./hub";
import { getRecordsForSector } from "./records";
import type { SectorSlug } from "./types";
import { getProjects } from "./transition";

// THE SPOKES. Brief 15 moves the complete lists off the hub, and this is the
// list of where they went.
//
// ONE COUNT, NOT TWO. Every spoke's population comes from the function the hub
// block is built from, so "All 34 projects" on the hub and the 34 rows on
// /sectors/cement/projects are the same call. The gate
// (sources/check_hub_list_duplication.py) checks the construction rather than
// the arithmetic, because arithmetic that has to be checked is arithmetic
// somebody will get wrong.
//
// EVERY SPOKE IS DEMOTED — noindex, follow. They are the evidence layer under
// the hub: a crawler walks through them, and the URL a stranger is offered in
// search is the hub. That is the same reading the demoted measure pages use.

export const SPOKE_IDS = [
  "projects",
  "technologies",
  "policies",
  "companies",
  "connections",
  "changes",
] as const;

export type SpokeId = (typeof SPOKE_IDS)[number];

export function isSpoke(segment: string): segment is SpokeId {
  return (SPOKE_IDS as readonly string[]).includes(segment);
}

/** The companies with a tracked project in this sector, each with its rows.
 *  Derived from the project register's `company` field and stored nowhere: a
 *  company is not a node kind on this platform yet (brief 5 §2), and a list
 *  computed off the rows is the honest version of one until it is. */
export function sectorCompanies(slug: string): { name: string; projects: string[] }[] {
  const byName = new Map<string, string[]>();
  for (const p of getProjects(slug)) {
    if (!byName.has(p.company)) byName.set(p.company, []);
    byName.get(p.company)!.push(p.id);
  }
  return [...byName.entries()]
    .map(([name, projects]) => ({ name, projects }))
    .sort((a, b) => b.projects.length - a.projects.length || a.name.localeCompare(b.name));
}

/** How many rows a spoke carries. The n in the hub's "All {n} …" link, read by
 *  the hub and by the gate from this one function. */
export function spokeCount(slug: string, spoke: SpokeId): number {
  switch (spoke) {
    case "projects":
      return sectorProjectRows(slug).length;
    case "technologies":
      return sectorDependencies(slug).length;
    case "policies":
      return sectorPolicyRows(slug).length;
    case "companies":
      return sectorCompanies(slug).length;
    case "changes":
      return getRecordsForSector(slug as SectorSlug).length;
    case "connections":
      return 0;
  }
}

/** The spoke's own title. The hub's H2s are questions; a spoke is a list, and
 *  a list is titled by what is in it. */
export function spokeTitle(slug: string, spoke: SpokeId): string {
  const names = sectorNames(slug);
  const name = SECTORS[slug as keyof typeof SECTORS] ?? slug;
  switch (spoke) {
    case "projects":
      return `Every tracked project in European ${names.short}`;
    case "technologies":
      return `What ${names.phrase} depends on`;
    case "policies":
      return `Every EU measure in the ${names.short} view`;
    case "companies":
      return `Companies in ${names.phrase}`;
    case "connections":
      return `How ${names.short} connects`;
    case "changes":
      return `What changed in ${name.toLowerCase()}`;
  }
}

/** The support-direction filter on the policies spoke — the destination of the
 *  hub's Opportunity link. Opportunity has no spoke of its own; the measures it
 *  lists are measures, and the page that carries every measure is the right
 *  place for all of them. */
export function sectorSupport(slug: string) {
  return sectorSupportRows(slug);
}

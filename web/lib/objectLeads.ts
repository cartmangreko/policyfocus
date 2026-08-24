import fs from "node:fs";
import path from "node:path";
import type { LeadView } from "@/components/LeadBlock";

// The lead blocks for the two object kinds that are not sectors — measures and
// projects. Built by sources/build_object_leads.py, gated by the same rules as
// the sector lead (it imports build_lead's gate rather than copying it), and
// drawn by the same component.
//
// ONE FILE PER KIND, not one per object. The sector leads are a file each
// because there are six of them and each is read beside its sector's other
// built artifacts; there are 480 measures, and 480 files whose combined size is
// under a megabyte would be a directory nobody can read and a build nobody can
// diff.
//
// AN ABSENT LEAD IS A DECISION. §0.8 makes indexability follow the lead block,
// so a measure with no entry here is a measure whose page is demoted and absent
// from the sitemap — see lib/siteRoutes.ts. Today that is the 35 omnibus
// measures, whose act was read from a local text before the fetcher existed and
// therefore carries no date on which anything about it was true.

interface LeadStore {
  leads: Record<string, LeadView>;
}

const DIR = path.join(process.cwd(), "..", "data", "lead");

const cache: Record<string, LeadStore> = {};

function store(kind: "measures" | "projects"): LeadStore {
  if (!cache[kind]) {
    const file = path.join(DIR, `${kind}.json`);
    cache[kind] = fs.existsSync(file)
      ? (JSON.parse(fs.readFileSync(file, "utf8")) as LeadStore)
      : { leads: {} };
  }
  return cache[kind];
}

/** Keyed by the register id, `<file>:<ID>` — the id in its stored case, not the
 *  lowercase form the URL carries. */
export function getMeasureLead(file: string, id: string): LeadView | null {
  const leads = store("measures").leads;
  const key = Object.keys(leads).find(
    (k) => k.toLowerCase() === `${file}:${id}`.toLowerCase(),
  );
  return key ? leads[key] : null;
}

export function getProjectLead(id: string): LeadView | null {
  return store("projects").leads[id] ?? null;
}

/** Every measure page that has a lead, as a URL path. The sitemap and the
 *  route classification read this; the page itself asks getMeasureLead, and
 *  both answer from the same file. */
export function measurePathsWithLead(): string[] {
  return Object.keys(store("measures").leads).map((key) => {
    const [file, id] = key.split(":");
    return `/measures/${file}/${id.toLowerCase()}`;
  });
}

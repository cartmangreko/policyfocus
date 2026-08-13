// Strategic priorities are an editorial lens over the register, not a stored
// field. Each one is a named predicate over the measures, so every count is
// computed from the data like the rest of the site — only the framing (title,
// description, standfirst, predicate) is authored here.
//
// The lens is deliberately cross-file: a priority collects provisions from
// Omnibus, the ETS revision and the Industrial Accelerator Act alike, which is
// the whole point of the page — it is where the agenda becomes visible across
// legislation rather than one file at a time. As more files land, they flow
// into these pages automatically.
import { FILES, getAllMeasures } from "./data";
import type { Measure } from "./types";

export interface Priority {
  slug: string;
  title: string;
  description: string;
  /** Page standfirst — what the lens is actually selecting for. */
  standfirst: string;
  /** How the predicate is drawn, stated plainly for the reader. */
  method: string;
  matches: (m: Measure) => boolean;
}

export const PRIORITIES: Priority[] = [
  {
    slug: "competitiveness-simplification",
    title: "Competitiveness & simplification",
    description: "Duties withdrawn, narrowed or merged to cut administrative load.",
    standfirst:
      "The withdrawal side of the agenda: every provision across the tracked corpus that removes, narrows or merges an existing duty rather than creating one.",
    method:
      "Obligations with direction 'removed'. Benefit-side measures are excluded — a grant is support, not simplification.",
    matches: (m) => m.direction === "rem" && (m.measure_type ?? "obligation") === "obligation",
  },
  {
    slug: "corporate-accountability",
    title: "Corporate accountability",
    description: "New reporting, due-diligence and disclosure duties on companies.",
    standfirst:
      "What the corpus asks companies to do that they did not have to do before — reporting, due diligence, verification and disclosure duties landing directly on business.",
    method: "Obligations with direction 'added' whose addressee class is Businesses.",
    matches: (m) =>
      m.direction === "add" &&
      m.class === "business" &&
      (m.measure_type ?? "obligation") === "obligation",
  },
  {
    slug: "industrial-support",
    title: "Industrial support & investment",
    description: "Benefit-side measures: allocations, funding routes and faster permitting.",
    standfirst:
      "The support side of the ledger: allocations, funding routes, permitting acceleration and other provisions that confer a benefit rather than impose a duty.",
    method:
      "Measures typed as 'incentive' in the register, in both directions — a support route granted and a support route withdrawn.",
    matches: (m) => m.measure_type === "incentive",
  },
  {
    slug: "implementation-capacity",
    title: "Implementation capacity",
    description: "What Member States and the Commission must build to make the files work.",
    standfirst:
      "The duties the agenda places on itself. Registries, delegated acts, national authorities and reporting lines that have to exist before any of the substantive rules bind.",
    method: "Provisions with direction 'added' addressed to Governments or the European Commission.",
    matches: (m) => (m.class === "state" || m.class === "commission") && m.direction === "add",
  },
];

export function getPriority(slug: string): Priority | undefined {
  return PRIORITIES.find((p) => p.slug === slug);
}

export function getPriorityMeasures(slug: string): Measure[] {
  const priority = getPriority(slug);
  if (!priority) return [];
  return getAllMeasures().filter(priority.matches);
}

export interface PriorityCount extends Omit<Priority, "matches"> {
  count: number;
}

export function getPriorityCounts(): PriorityCount[] {
  const all = getAllMeasures();
  return PRIORITIES.map(({ matches, ...rest }) => ({
    ...rest,
    count: all.filter(matches).length,
  })).sort((a, b) => b.count - a.count);
}

// How a priority is distributed across the legislative files it draws from.
// This is the cross-file summary the page is really for.
export interface FileBreakdown {
  file: string;
  name: string;
  code: string;
  count: number;
  share: number;
}

export function getPriorityByFile(slug: string): FileBreakdown[] {
  const measures = getPriorityMeasures(slug);
  const total = measures.length || 1;
  const counts = new Map<string, number>();
  for (const m of measures) counts.set(m.file, (counts.get(m.file) ?? 0) + 1);
  return [...counts.entries()]
    .map(([file, count]) => ({
      file,
      name: FILES[file]?.name.split(" — ")[0] ?? file,
      code: FILES[file]?.code ?? "",
      count,
      share: Math.round((count / total) * 100),
    }))
    .sort((a, b) => b.count - a.count);
}

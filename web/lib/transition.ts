import fs from "node:fs";
import path from "node:path";

// The sector transition map, read at build time from data/transition/.
//
// This is the product layer. The register answers "what does this act require";
// these four files answer "what transition is this sector under, which measures
// decide whether it pays, who is building what, and what is blocking it".
//
// READ-ONLY, AND GATED ELSEWHERE. Nothing here validates: sources/check_sector_
// schema.py and sources/check_importance.py run in the prebuild and fail it, so
// by the time Next reads these files every id resolves, every number has a
// quoted source, and the ranking reproduces from its inputs. A loader that
// re-checked would be a second, weaker implementation of the same rules.
//
// A SECTOR WITHOUT A MAP IS NORMAL. Cement is the pilot; the other nineteen
// sectors have no technologies, no projects and no ranking, and `hasMap` is how
// the sector route decides which template to render. It must never throw for
// them — an empty map is a state, not an error.

const DIR = path.join(process.cwd(), "..", "data", "transition");

export type Transition =
  | "decarbonisation"
  | "circularity"
  | "supply_security"
  | "digital"
  | "defence";

export type Readiness =
  | "research"
  | "pilot"
  | "demonstration"
  | "early-commercial"
  | "commercial";

export type BottleneckType =
  | "technical"
  | "financial"
  | "infrastructure"
  | "market"
  | "political";

export type ProjectStatus =
  | "announced"
  | "funded"
  | "fid"
  | "construction"
  | "operating"
  | "paused"
  | "cancelled";

export interface Source {
  url: string;
  title?: string;
  publisher: string;
  date?: string;
  verbatim?: string;
  snapshot?: string;
  archived?: boolean;
}

export interface Parameter {
  id: string;
  name: string;
  value: number | string;
  unit: string;
  scope: string;
  sector?: string;
  technology?: string;
  date_of_value: string;
  retrieved_date: string;
  stale_after?: number;
  confidence: "primary" | "secondary" | "estimate";
  verbatim_note?: string;
  note?: string;
  source: Source;
}

export interface Technology {
  id: string;
  transition: Transition;
  name: string;
  description: string;
  readiness: { level: Readiness; source: string; date: string; note?: string };
  abatement_share?: { low: number; high: number; unit: string; source: string; date: string; note?: string };
  cost?: { low: number; high: number; unit: string; source: string; date: string; parameter?: string; note?: string };
  dependency: string[];
  sectors: string[];
  sources: Source[];
}

export interface BottleneckMeasure {
  measure: string;
  rel: "worsens" | "relieves";
  weight: number;
  note: string;
  evidence: { source: string; path: string; quote: string; article?: string };
}

export interface Bottleneck {
  id: string;
  sector: string;
  transition: Transition;
  type: BottleneckType;
  name: string;
  description: string;
  quantified_by: string[];
  addressed_by: string[];
  measures: BottleneckMeasure[];
  sources: Source[];
}

export interface FundingLine {
  programme: string;
  amount_eur: number | null;
  source_url: string;
  measure?: string;
  measure_note?: string;
  parameter?: string;
  note?: string;
}

export interface StatusEvent {
  status: ProjectStatus;
  date: string;
  source_url: string;
  note?: string;
}

export interface Project {
  id: string;
  name: string;
  company: string;
  plant?: string;
  country: string;
  sector: string;
  transition: Transition;
  technology: string[];
  capacity?: { value: number; unit: string; parameter?: string };
  investment_total?: { value: number; unit: string; parameter?: string };
  status: ProjectStatus;
  status_history: StatusEvent[];
  public_funding: FundingLine[];
  sources: Source[];
}

export interface MoneyScore {
  value: number | null;
  scale: string | null;
  model: string | null;
  direction: "cost" | "support" | null;
  bearer: string | null;
  per_tonne: number | null;
  annual_total: number | null;
  computable: boolean;
  inputs: string[];
  formula: string | null;
  missing: string[];
  caveats: string[];
  context: { label: string; value: number; scale: string; detail?: string }[];
}

export interface RankedMeasure {
  measure: string;
  file: string;
  id: string;
  measure_type: string;
  reach: "register" | "funding";
  reached_via: string[];
  article: string | null;
  when: string | null;
  duty: string;
  money: MoneyScore;
  bottleneck_linkage: {
    count: number;
    weight: number;
    edges: {
      bottleneck: string;
      bottleneck_name: string;
      type: BottleneckType;
      rel: "worsens" | "relieves";
      weight: number;
      note: string;
      evidence: { source: string; path: string; quote: string; article?: string };
    }[];
  };
  attention: { available: boolean; count: number | null; window_months: number };
  rank: number;
  in_sector_view: boolean;
  override_rank?: number;
  override_reason?: string;
}

export interface NetBucket {
  scale: string;
  bearer: string;
  cost: number;
  support: number;
  net: number;
  measures: { measure: string; direction: string; amount: number }[];
}

export interface Importance {
  sector: string;
  priced_year: number;
  built_from: { parameters: string[]; attention_available: boolean };
  net: { _note: string; buckets: NetBucket[] };
  measures: RankedMeasure[];
}

function read<T>(file: string, key: string): T[] {
  const full = path.join(DIR, file);
  if (!fs.existsSync(full)) return [];
  return JSON.parse(fs.readFileSync(full, "utf8"))[key] as T[];
}

let cache: {
  technologies: Technology[];
  bottlenecks: Bottleneck[];
  parameters: Parameter[];
  projects: Project[];
} | null = null;

function all() {
  if (!cache) {
    cache = {
      technologies: read<Technology>("technologies.json", "technologies"),
      bottlenecks: read<Bottleneck>("bottlenecks.json", "bottlenecks"),
      parameters: read<Parameter>("parameters.json", "parameters"),
      projects: read<Project>("projects.json", "projects"),
    };
  }
  return cache;
}

export function getParameters(): Map<string, Parameter> {
  return new Map(all().parameters.map((p) => [p.id, p]));
}

export function getProjects(sector?: string): Project[] {
  const rows = all().projects;
  return sector ? rows.filter((p) => p.sector === sector) : rows;
}

export function getProject(id: string): Project | undefined {
  return all().projects.find((p) => p.id === id);
}

export function getBottlenecks(sector: string): Bottleneck[] {
  return all().bottlenecks.filter((b) => b.sector === sector);
}

/** Technologies deployed in a sector. Shared nodes: a technology lists its
 *  sectors, and the same row serves cement and steel. */
export function getTechnologies(sector: string): Technology[] {
  return all().technologies.filter((t) => t.sectors.includes(sector));
}

export function getTechnology(id: string): Technology | undefined {
  return all().technologies.find((t) => t.id === id);
}

export function getImportance(sector: string): Importance | null {
  const full = path.join(DIR, "importance", `${sector.replace("/", "__")}.json`);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf8")) as Importance;
}

/** Whether this sector has a transition map at all. The sector route reads it
 *  to choose a template, so it has to be cheap and total: no throw, no
 *  half-answer. A sector has a map when it has a ranking AND something for the
 *  ranking to point at. */
export function hasMap(sector: string): boolean {
  const imp = getImportance(sector);
  return Boolean(imp && getBottlenecks(sector).length > 0);
}

/** The transitions a sector is under, in the order the page shows them: by the
 *  money attached, which for a single-transition sector is a no-op and for
 *  chemicals will not be. */
export function getTransitions(sector: string): Transition[] {
  const seen = new Set<Transition>();
  for (const b of getBottlenecks(sector)) seen.add(b.transition);
  for (const p of getProjects(sector)) seen.add(p.transition);
  return [...seen];
}

export const TRANSITION_LABEL: Record<Transition, string> = {
  decarbonisation: "decarbonisation",
  circularity: "circularity",
  supply_security: "supply security",
  digital: "digital",
  defence: "defence",
};

export const STATUS_LABEL: Record<ProjectStatus, string> = {
  announced: "Announced",
  funded: "Funded",
  fid: "FID taken",
  construction: "In construction",
  operating: "Operating",
  paused: "Paused",
  cancelled: "Cancelled",
};

export const BEARER_LABEL: Record<string, string> = {
  eu_producer: "EU producer",
  importer: "Importer",
  project_developer: "Project developer",
};

/** Every project in a sector, newest status change first. Also the home page's
 *  feed, where it is not filtered by sector. */
export function byLastChange(rows: Project[]): Project[] {
  return [...rows].sort((a, b) => {
    const la = a.status_history[a.status_history.length - 1]?.date ?? "";
    const lb = b.status_history[b.status_history.length - 1]?.date ?? "";
    return lb.localeCompare(la);
  });
}

export function lastChange(p: Project): StatusEvent | undefined {
  return p.status_history[p.status_history.length - 1];
}

/** Every source URL used anywhere on a sector page, grouped by publisher.
 *  Section 7 of the sector page is not a nicety: the claim the whole layer
 *  makes is that each figure walks back to somebody's published sentence, and
 *  a reader who cannot see the list has to take that on trust. */
export function sourcesForSector(sector: string): { publisher: string; sources: Source[] }[] {
  const params = all().parameters.filter((p) => !p.sector || p.sector === sector);
  const rows: Source[] = [
    ...getTechnologies(sector).flatMap((t) => t.sources),
    ...getBottlenecks(sector).flatMap((b) => b.sources),
    ...getProjects(sector).flatMap((p) => p.sources),
    ...params.map((p) => p.source),
  ];
  const byUrl = new Map<string, Source>();
  for (const s of rows) if (!byUrl.has(s.url)) byUrl.set(s.url, s);
  const byPublisher = new Map<string, Source[]>();
  for (const s of byUrl.values()) {
    const key = s.publisher.split("—")[0].trim();
    if (!byPublisher.has(key)) byPublisher.set(key, []);
    byPublisher.get(key)!.push(s);
  }
  return [...byPublisher.entries()]
    .map(([publisher, sources]) => ({
      publisher,
      sources: sources.sort((a, b) => (a.title ?? a.url).localeCompare(b.title ?? b.url)),
    }))
    .sort((a, b) => a.publisher.localeCompare(b.publisher));
}

export function measureHref(measure: string): string {
  const [file, id] = measure.split(":");
  return `/measures/${file}/${id}`;
}

export function projectHref(id: string): string {
  return `/projects/${id}`;
}

export function eur(n: number): string {
  if (Math.abs(n) >= 1e9) return `€${(n / 1e9).toFixed(1)} bn`;
  if (Math.abs(n) >= 1e6) return `€${Math.round(n / 1e6).toLocaleString("en-US")} m`;
  return `€${n.toLocaleString("en-US", { maximumFractionDigits: 2 })}`;
}

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

/** @deprecated Replaced by the funding node. Kept only until nothing imports it. */
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
  sources: Source[];
}

// --- materials and funding ------------------------------------------------
//
// Two node kinds added in amendment brief 2 §2. Both are read the same way as
// everything else here: the file is curated, sources/check_sector_schema.py
// gates it, and nothing in this module validates or derives.

export type MaterialType =
  | "feedstock"
  | "intermediate"
  | "energy_carrier"
  | "by_product"
  | "waste_stream";

export interface MaterialEdge {
  node: string;
  since: string;
  volume: string | null;
  volume_note?: string;
  evidence: { source: string; path?: string; quote?: string; note?: string };
}

export interface Material {
  id: string;
  name: string;
  type: MaterialType;
  cn_code: string | null;
  prodcom_code: string | null;
  /** The Annex I entry of the Critical Raw Materials Act, where the material is
   *  a strategic raw material, and null where it is not. Explicit rather than
   *  optional: see the note in data/transition/materials.json. */
  crma_annex_i: { entry: string; source: Source } | null;
  sectors: string[];
  description: string;
  produced_by: MaterialEdge[];
  consumed_by: MaterialEdge[];
  substitutes: { material: string; since: string; evidence: MaterialEdge["evidence"] }[];
  required_by: MaterialEdge[];
  sources: Source[];
}

export type FundingInstrument =
  | "grant"
  | "state_aid"
  | "eib_financing"
  | "ipcei"
  | "auction_support"
  | "equity"
  | "project_finance"
  | "guarantee";

export type FundingStatus =
  | "announced"
  | "approved"
  | "signed"
  | "disbursed"
  | "withdrawn";

// WHICH STATUSES A TOTAL MAY ADD UP. The same three groups as
// sources/sector_map.py (FUNDING_COMMITTED / FUNDING_ANNOUNCED /
// FUNDING_EXCLUDED), which is the authority; check_sector_schema.py fails the
// build if these lists and that file disagree, because a total computed one way
// in Python and another way in TypeScript is two different numbers with one
// label.
export const FUNDING_COMMITTED: readonly FundingStatus[] = ["approved", "signed", "disbursed"];
export const FUNDING_ANNOUNCED: readonly FundingStatus[] = ["announced"];
export const FUNDING_EXCLUDED: readonly FundingStatus[] = ["withdrawn"];

export interface Funding {
  id: string;
  name: string;
  instrument: FundingInstrument;
  programme: string;
  under: string | null;
  under_note?: string;
  /** A parameter id, never a number: the amount exists in parameters.json with
   *  the sentence it was read from, or it does not exist. */
  amount: string | null;
  amount_note?: string | null;
  date: string;
  status: FundingStatus;
  finances: string[];
  supports: string[];
  country: string;
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
  /** What the measure requires or grants, said to somebody who has not read
   *  the act: an authored title and one sentence with its figures slotted in
   *  at build time. Written in data/transition/measure_labels.json, filled by
   *  sources/build_importance.py, gated by sources/check_sector_schema.py.
   *  Null for a measure nobody has written one for — which is every measure
   *  outside a sector view. */
  plain: { title: string; sentence: string } | null;
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
  materials: Material[];
  funding: Funding[];
} | null = null;

function all() {
  if (!cache) {
    cache = {
      technologies: read<Technology>("technologies.json", "technologies"),
      bottlenecks: read<Bottleneck>("bottlenecks.json", "bottlenecks"),
      parameters: read<Parameter>("parameters.json", "parameters"),
      projects: read<Project>("projects.json", "projects"),
      materials: read<Material>("materials.json", "materials"),
      funding: read<Funding>("funding.json", "funding"),
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

/** Materials a sector makes, consumes or throws off. Shared nodes, like
 *  technologies: slag leaving steel and arriving in cement is one row. */
export function getMaterials(sector: string): Material[] {
  return all().materials.filter((m) => m.sectors.includes(sector));
}

/** Every capital allocation that finances a project in this sector. */
export function getFunding(sector: string): Funding[] {
  const ids = new Set(getProjects(sector).map((p) => `project:${p.id}`));
  return all().funding.filter((f) => f.finances.some((n) => ids.has(n)));
}

/** One project's funding rows. THE ROLLUP IS DERIVED, always: the total is
 *  computed from these wherever it is shown and never stored back on the
 *  project, because a stored total is a second copy of a number and a second
 *  copy is a number that will eventually disagree with the first. */
export function fundingForProject(id: string): Funding[] {
  return all().funding.filter((f) => f.finances.includes(`project:${id}`));
}

/** A funding row's amount in euros, from its sourced parameter. `null` covers
 *  both "no amount recorded" and "recorded as unpublished" — the caller shows
 *  amount_note for the difference. */
export function fundingAmount(f: Funding, params: Map<string, Parameter>): number | null {
  if (!f.amount) return null;
  const p = params.get(f.amount);
  if (!p) return null;
  const scale =
    p.unit === "EUR" ? 1 : p.unit === "EUR million" ? 1e6 : p.unit === "EUR billion" ? 1e9 : null;
  return scale === null ? null : Number(p.value) * scale;
}

/** Funding split by what its status permits a total to say. Never one number:
 *  committed money, announced money and withdrawn lines are three different
 *  facts, and the Capital section shows them as three. `undisclosed` counts
 *  committed rows whose amount is not published, which is why `committed` is a
 *  floor rather than a total. */
export interface FundingTotals {
  committed: number;
  committedCount: number;
  announced: number;
  announcedCount: number;
  withdrawnCount: number;
  undisclosed: number;
}

export function fundingTotals(rows: Funding[], params: Map<string, Parameter>): FundingTotals {
  const t: FundingTotals = {
    committed: 0,
    committedCount: 0,
    announced: 0,
    announcedCount: 0,
    withdrawnCount: 0,
    undisclosed: 0,
  };
  for (const f of rows) {
    if (FUNDING_EXCLUDED.includes(f.status)) {
      t.withdrawnCount += 1;
      continue;
    }
    const amount = fundingAmount(f, params);
    if (FUNDING_ANNOUNCED.includes(f.status)) {
      t.announcedCount += 1;
      t.announced += amount ?? 0;
      continue;
    }
    t.committedCount += 1;
    if (amount === null) t.undisclosed += 1;
    else t.committed += amount;
  }
  return t;
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

/** The first screen: one sentence, why it matters, and the facts under both.
 *  Built and gated by sources/build_lead.py — see that file for the rules the
 *  sentences pass before they are written. Nothing is generated here. */
export interface LeadFact {
  id: string;
  label: string;
  text: string;
  as_of: string;
  numbers: string[];
  parts: Record<string, string>;
  sourced: string[];
  href: string | null;
  /** Whether the fact is drawn. Every fact is computed and kept; the binding
   *  constraint is deliberately not shown, because it is what the opening
   *  sentence is about — see sources/build_lead.py. A surfaced fact that fails
   *  its own gate is unsurfaced by the builder rather than dropped. */
  surface: boolean;
}

export interface LeadBlock {
  text: string;
  from: string[];
  /** `override` is a sentence a reviewer wrote; `generated` came from the
   *  templates. The page does not distinguish them — both are unsigned, per
   *  amendment brief 2 §4 — but the build report does. */
  source: "generated" | "override";
  reviewed?: string;
}

export interface Lead {
  sector: string;
  template_version: number;
  fingerprint: string;
  sentence: LeadBlock;
  why_it_matters: LeadBlock | null;
  facts: LeadFact[];
  override_stale: boolean;
  notes: string[];
}

export function getLead(sector: string): Lead | null {
  const full = path.join(DIR, "lead", `${sector.replace("/", "__")}.json`);
  if (!fs.existsSync(full)) return null;
  return JSON.parse(fs.readFileSync(full, "utf8")) as Lead;
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

/** The three lists the Materials section renders, brief 5 §2.
 *
 *  WHAT COUNTS AS THIS SECTOR'S EDGE. Not only `sector:cement`. A material
 *  edge's endpoint can be a sector, a project or a technology, and a captured
 *  CO2 stream produced by five cement plants is a cement output whether or not
 *  anybody also wrote the sector-level edge. So membership is the transitive
 *  one a reader means: the endpoint is this sector, or a project in it, or a
 *  technology in it. Reading it narrowly would have left the one waste stream
 *  on the platform in none of the three lists while sitting in the sector's
 *  own material set, which is the sort of quiet omission a section like this
 *  exists to prevent.
 *
 *  A material can appear in two lists — captured CO2 is produced by the plants
 *  and consumed by the transport-and-storage route — and that is a fact about
 *  the material rather than a double count. Nothing here is summed.
 *
 *  Each list is ordered by how many of this sector's edges the material carries,
 *  which is the only ordering available that is not a judgement. */
export interface MaterialFlow {
  material: Material;
  /** This sector's edges of that kind, and the ordering basis. */
  edges: number;
}

export interface MaterialFlows {
  inputs: MaterialFlow[];
  outputs: MaterialFlow[];
  substitutes: MaterialFlow[];
}

export function materialFlows(sector: string): MaterialFlows {
  const here = new Set<string>([
    `sector:${sector}`,
    ...getProjects(sector).map((p) => `project:${p.id}`),
    ...getTechnologies(sector).map((t) => `technology:${t.id}`),
  ]);
  const mine = (edges: MaterialEdge[]) => edges.filter((e) => here.has(e.node)).length;
  const rank = (rows: MaterialFlow[]) =>
    rows.filter((r) => r.edges > 0).sort((a, b) => b.edges - a.edges || a.material.name.localeCompare(b.material.name));

  const materials = getMaterials(sector);
  return {
    inputs: rank(materials.map((m) => ({ material: m, edges: mine(m.consumed_by) }))),
    outputs: rank(materials.map((m) => ({ material: m, edges: mine(m.produced_by) }))),
    // A substitution is a claim about one material standing in for another and
    // carries no sector endpoint of its own; a substitute is in this sector's
    // list because the material it substitutes for is.
    substitutes: rank(
      materials.map((m) => ({ material: m, edges: m.substitutes.length })),
    ),
  };
}

/** One material by id, for its own page. */
export function getMaterial(id: string): Material | undefined {
  return all().materials.find((m) => m.id === id);
}

/** Every material on the platform. Materials are cross-sector, so the spoke is
 *  /materials/{id} rather than a per-sector list (brief 5 §6). */
export function allMaterials(): Material[] {
  return all().materials;
}

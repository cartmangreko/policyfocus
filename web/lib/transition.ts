import fs from "node:fs";
import path from "node:path";
import { moneyShort } from "./money";

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
  /** What kind of thing is at the other end. Absent means a document, which is
   *  what almost everything is. `api` and `dataset` are cited from the query
   *  the call was made with rather than by a title they do not have — see
   *  lib/citation.ts. */
  kind?: "document" | "api" | "dataset";
  /** Required for an api or dataset source: what it is, so the citation has a
   *  subject. The id is the dataset's own, where it has one. */
  dataset?: { name: string; id?: string };
}

/** How the number or the point was come by. Same three values the Python
 *  vocabulary holds, named once so both sides cannot drift. */
export type Confidence = "primary" | "secondary" | "estimate";

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
  confidence: Confidence;
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

/** One event in a project's history.
 *
 *  `kind` is absent on an ordinary status change, which is almost all of them.
 *  An `ownership` event is the project changing hands: it names both owners, and
 *  it carries the status the project was ALREADY in, unchanged. That is what
 *  keeps the last entry's status equal to the project's, and it is why
 *  `statusTransitions` skips one without being told to — the status did not
 *  change, so the entry is not a transition. See sources/sector_map.py,
 *  PROJECT_EVENT_KINDS, which is where the rule is written and gated. */
export interface StatusEvent {
  kind?: "status" | "ownership";
  status: ProjectStatus;
  date: string;
  source_url: string;
  note?: string;
  /** Ownership events only: who it was, and who it is now. */
  from?: string;
  to?: string;
}

/** What kind of place a project row is, which is the only thing that decides
 *  how it is drawn. Absent means `plant`: a row that says nothing is a works. */
export type ProjectRole = "plant" | "storage";

/** One sited coordinate, with the source that puts it there.
 *
 *  `precision` is `plant` for a works and `site` for a store, a field or a
 *  receiving terminal. `town` exists in the Python vocabulary so that the gate
 *  can refuse it by name and never reaches this type in practice — a town
 *  centroid drawn as a works is a wrong fact rendered confidently. */
export interface Site {
  site: string;
  lat: number;
  lon: number;
  precision: "plant" | "site" | "town";
  retrieved_date: string;
  source: Source;
  confidence: Confidence;
  /** The plant address, where the company publishes one, beside the point that
   *  was read off it. */
  address?: { text: string; url: string; publisher: string; date: string };
  note?: string;
}

/** Where a captured tonne goes. Two shapes and no third: either the id of the
 *  storage project it reaches, or `unresolved` with a note saying how far the
 *  chain is actually specified. Unresolved is renderable information — a kiln
 *  with a capture unit and nowhere to send the CO2 is the thing worth showing —
 *  so nothing here treats it as an absence. */
export type ProjectStorage =
  | { project: string; since: string; source: Source; note?: string; unresolved?: never }
  | { unresolved: true; note: string; source: Source; project?: never };

export interface Project {
  id: string;
  name: string;
  company: string;
  plant?: string;
  country: string;
  /** One or more sites. A list because a project is not always at one place:
   *  the ArcelorMittal row covers Bremen and Eisenhüttenstadt, and one point
   *  for it would put a mark in the field between them. Never empty — the
   *  Python gate fails the build before this file is written. */
  location: Site[];
  sector: string;
  role?: ProjectRole;
  /** Only ever true, and only on a node several industries share — a CO2 store,
   *  a hydrogen pipeline. `shared_note` is where the judgement is defended. */
  shared?: true;
  shared_note?: string;
  transition: Transition;
  technology: string[];
  storage?: ProjectStorage;
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
 *  committed money, announced allocations and withdrawn lines are three
 *  different facts, and the Opportunity section shows them as three. `undisclosed` counts
 *  committed rows whose amount is not published, which is why `committed` is a
 *  floor rather than a total. */
export interface FundingTotals {
  committed: number;
  committedCount: number;
  /** ANNOUNCED IS COUNTED AND NOT SUMMED — brief 5 §4.1, ruled. There is no
   *  `announced` total here on purpose: a figure that is not computed cannot be
   *  rendered, which is a stronger guarantee than everybody remembering not to
   *  add one up. An announcement is a statement of intent, and a euro total of
   *  intentions reads as money that exists. The allocations are listed instead,
   *  each with its own amount, source and date. */
  announcedCount: number;
  withdrawnCount: number;
  undisclosed: number;
}

export function fundingTotals(rows: Funding[], params: Map<string, Parameter>): FundingTotals {
  const t: FundingTotals = {
    committed: 0,
    committedCount: 0,
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

/** The entries that CHANGED the status, which is not all of them.
 *
 *  A history is a list of events in date order, and most are transitions. Some
 *  are not: a later source reporting on a project whose status it does not
 *  change. Slite was paused on 19 November 2025 when the Swedish Energy Agency
 *  declined to co-fund it, and its permit application was withdrawn on 1
 *  January 2026 — a fact about a paused project, not a project becoming paused.
 *
 *  The distinction is positional rather than a flag on the row: an entry is a
 *  transition if its status differs from the one before it. That cannot fall out
 *  of step with the data the way a hand-set flag would. The same rule is written
 *  in sources/sector_map.py, which is where the two Python sentence templates
 *  with the same problem read it from — and the two are held together by
 *  sources/check_transition_parity.py, which runs both readings over every
 *  history up to four entries long and fails the build if they disagree. A
 *  comment saying "edit both" is what this rule had before that gate existed,
 *  and it is not a mechanism.
 *
 *  `lastChange` is deliberately NOT this. A feed, a "last change" column and an
 *  "as of" date all want the latest thing on file, which is a different
 *  question from when the project last moved. */
export function statusTransitions(p: Project): StatusEvent[] {
  return p.status_history.filter(
    (h, i) => i === 0 || h.status !== p.status_history[i - 1].status,
  );
}

/** Every source URL used anywhere on a sector page, grouped by publisher.
 *  Section 7 of the sector page is not a nicety: the claim the whole layer
 *  makes is that each figure walks back to somebody's published sentence, and
 *  a reader who cannot see the list has to take that on trust. */
export function sourcesForSector(sector: string): { publisher: string; sources: Source[] }[] {
  const params = all().parameters.filter((p) => !p.sector || p.sector === sector);
  // MATERIALS ARE ON THE PAGE AND WERE NOT IN THIS LIST. The section says
  // "every outbound URL on this page" and the Materials section had been
  // rendering material names and their edges since it was built, with the
  // material's own `sources` reachable from neither. It went unnoticed while
  // both materials happened to share their URLs with a project or a parameter;
  // steel's slag and scrap rows do not, and the ZKG citation appeared under a
  // publisher heading with nothing under it.
  const rows: Source[] = [
    ...getTechnologies(sector).flatMap((t) => t.sources),
    ...getBottlenecks(sector).flatMap((b) => b.sources),
    ...getProjects(sector).flatMap((p) => p.sources),
    ...getMaterials(sector).flatMap((m) => m.sources),
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

/** One euro amount, in the short form. Kept as a name because every surface on
 *  this side already calls it; the rule behind it is data/number_format.json,
 *  which sources/number_format.py reads too.
 *
 *  It used to be a tier ladder written here, beside a second one written in
 *  build_opportunity.py, and the two rounded a tie in opposite directions —
 *  steel's committed total printed as "€3.2 billion" and "€3.3 bn" four lines
 *  apart on the same page. */
export const eur = moneyShort;

/** The three lists the Materials section renders, brief 5 §2.
 *
 *  WHAT COUNTS AS THIS SECTOR'S EDGE: the sector itself, and the plants in it.
 *  Not the technologies deployed in it, and that distinction is the whole of
 *  this function.
 *
 *  It was written the other way first, and captured CO2 came out as a cement
 *  INPUT. Its one consumed_by edge is `technology:co2-transport-storage`,
 *  evidenced on NZIA Art. 21 — access to transport networks and storage sites
 *  for geological storage. That is where the CO2 GOES, not something a cement
 *  plant takes in, and reading a disposal route as a feedstock is the kind of
 *  error a page of computed views has no way to apologise for. A plant that
 *  really consumed CO2 — curing, mineralisation — would carry a `project:` edge
 *  and would show up here on the strength of it. None does.
 *
 *  So an endpoint counts when it is `sector:<slug>` or a project in the sector.
 *  A technology is a route rather than an actor, and it is read on the
 *  material's own page, where every edge is listed with its evidence.
 *
 *  THE BASIS IS DISPLAYED, brief 5 §2 as amended: each item shows the count
 *  behind it — "5 plants", or the sector-level edge where the claim is made
 *  about the industry as a whole — linking to the set of edges the count is of.
 *  An item may appear in more than one list only where DISTINCT edges support
 *  each appearance, which `assertDisjoint` below checks rather than assumes:
 *  produced_by and consumed_by are separate arrays, so the property holds by
 *  construction today, and a future list built off a shared array would break
 *  it silently.
 */
export interface MaterialFlow {
  material: Material;
  /** Plants in this sector carrying the edge. The ordering basis, and the
   *  displayed one. */
  plants: number;
  /** Whether the sector itself carries the edge — a claim about the industry
   *  rather than about a countable set of installations. */
  sectorWide: boolean;
  /** The edges this appearance rests on, so two appearances can be checked
   *  against each other rather than trusted. */
  edges: MaterialEdge[];
}

export interface MaterialFlows {
  inputs: MaterialFlow[];
  outputs: MaterialFlow[];
  substitutes: MaterialFlow[];
}

/** No two lists may rest on the same edge. The rule brief 5 §2 states, checked
 *  where it can actually be broken rather than left as a property of how the
 *  arrays happen to be named today. */
function assertDisjoint(flows: MaterialFlows): void {
  const seen = new Map<string, string>();
  for (const [list, rows] of Object.entries(flows)) {
    for (const row of rows as MaterialFlow[]) {
      for (const e of row.edges) {
        const key = `${row.material.id}|${e.node}|${e.since}`;
        const already = seen.get(key);
        if (already && already !== list) {
          throw new Error(
            `${row.material.id} appears in both ${already} and ${list} on the strength ` +
              `of the same edge (${e.node}). An item may appear in more than one list ` +
              `only where distinct edges support each appearance`,
          );
        }
        seen.set(key, list);
      }
    }
  }
}

export function materialFlows(sector: string): MaterialFlows {
  const plants = new Set(getProjects(sector).map((p) => `project:${p.id}`));
  const self = `sector:${sector}`;
  const mine = (edges: MaterialEdge[]) =>
    edges.filter((e) => e.node === self || plants.has(e.node));

  const flow = (m: Material, edges: MaterialEdge[]): MaterialFlow => ({
    material: m,
    plants: edges.filter((e) => plants.has(e.node)).length,
    sectorWide: edges.some((e) => e.node === self),
    edges,
  });
  const rank = (rows: MaterialFlow[]) =>
    rows
      .filter((r) => r.edges.length > 0)
      .sort(
        (a, b) =>
          b.edges.length - a.edges.length || a.material.name.localeCompare(b.material.name),
      );

  const materials = getMaterials(sector);
  const flows: MaterialFlows = {
    inputs: rank(materials.map((m) => flow(m, mine(m.consumed_by)))),
    outputs: rank(materials.map((m) => flow(m, mine(m.produced_by)))),
    // A substitution is a claim about one material standing in for another and
    // carries no endpoint of its own, so it has no plant count: a substitute is
    // in this sector's list because the material it substitutes for is, and the
    // basis a reader wants is what it stands in for, which the item says.
    substitutes: materials
      .filter((m) => m.substitutes.length > 0)
      .map((m) => ({ material: m, plants: 0, sectorWide: false, edges: [] }))
      .sort((a, b) => a.material.name.localeCompare(b.material.name)),
  };
  assertDisjoint(flows);
  return flows;
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

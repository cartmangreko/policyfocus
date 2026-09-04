import fs from "node:fs";
import path from "node:path";
import type {
  DDriver,
  FileMeta,
  Measure,
  MeasureClass,
  SectorMeta,
  SectorSlug,
} from "./types";
import { isPositiveValence, valenceLabel } from "./valence";

// data/ lives one level up from web/ at the repo root. Untouched, read-only.
const DATA_DIR = path.join(process.cwd(), "..", "data");
const DATA_FILES = ["omnibus.json", "ets.json", "iaa.json", "cbam.json", "nzia.json", "crma.json", "ppwr.json", "battery.json"];

export const FILES: Record<string, FileMeta> = {
  omnibus: {
    name: "Omnibus I — CSRD / CSDDD / Taxonomy simplification",
    code: "COM(2025) 81, 2025/0045 (COD)",
  },
  ets: {
    name: "EU ETS revision",
    code: "COM(2026) 616 final, 2026/0212 (COD)",
  },
  iaa: {
    name: "Industrial Accelerator Act",
    code: "COM(2026) 100 final, 2026/0068 (COD)",
  },
  cbam: {
    name: "CBAM extension — downstream goods and anti-circumvention",
    code: "COM(2025) 989 final, 2025/0419 (COD)",
  },
  // The two standing acts. `code` carries the dated consolidation the rows
  // were read from, not a procedure number: these are law in force, and which
  // consolidation was read is the fact a reader needs to place them.
  nzia: {
    name: "Net-Zero Industry Act",
    code: "Regulation (EU) 2024/1735, consolidated 17.08.2025",
  },
  crma: {
    name: "Critical Raw Materials Act",
    code: "Regulation (EU) 2024/1252, consolidated 03.05.2024",
  },
  // Read at the BASE act, not a consolidation: Cellar announces
  // 02025R0040-20250122 and then serves it in no format. Single-pass.
  battery: {
    name: "Batteries Regulation",
    code: "Regulation (EU) 2023/1542",
  },
  ppwr: {
    name: "Packaging and Packaging Waste Regulation",
    code: "Regulation (EU) 2025/40, base act",
  },
};

// The sector spine comes from data/sectors.json, the same file
// sources/build_graph.py reads, so the Python and TypeScript sides cannot
// drift — the arrangement sources/register_files.json already uses.
//
// It is two levels deep. A slug is a parent, or a child of exactly one parent,
// and a child's slug is "<parent>/<child>" — which is also its URL. A child
// exists only where a measure applies to the child and NOT to the parent; the
// `evidence` field on each child records which measures forced it.
//
// SectorSlug in types.ts has to restate these keys, because a union of string
// literals cannot be read out of a file the compiler never sees. So the union
// is restated once more here as a Record — which TypeScript checks for
// exhaustiveness — and the JSON is compared against it at build time. A slug
// added to one side and not the other fails the build instead of quietly
// producing a page nobody linked to, or a link to a page that 404s.
const EXPECTED_SLUGS: Record<SectorSlug, true> = {
  steel: true, cement: true, alu: true, chem: true, "chem/plastics": true,
  glass: true, paper: true, wood: true, foodbev: true, retail: true,
  horeca: true, power: true, waste: true, ship: true, air: true, auto: true,
  build: true, batsol: true, clean: true, ccs: true,
};

const SECTOR_SPINE: Record<SectorSlug, SectorMeta> = (() => {
  const raw = JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, "sectors.json"), "utf-8")
  ) as { sectors: Record<string, SectorMeta> };

  const fromJson = Object.keys(raw.sectors).sort();
  const fromUnion = Object.keys(EXPECTED_SLUGS).sort();
  const onlyJson = fromJson.filter((s) => !(s in EXPECTED_SLUGS));
  const onlyUnion = fromUnion.filter((s) => !fromJson.includes(s));
  if (onlyJson.length || onlyUnion.length) {
    throw new Error(
      "sector spine drift between data/sectors.json and SectorSlug: " +
        `only in JSON [${onlyJson}], only in the union [${onlyUnion}]`
    );
  }

  // Two levels, not three: a child's parent must itself be a parent.
  for (const [slug, meta] of Object.entries(raw.sectors)) {
    if (meta.parent && raw.sectors[meta.parent]?.parent) {
      throw new Error(`sector ${slug} nests under ${meta.parent}, which is itself a child`);
    }
    if (meta.parent && !raw.sectors[meta.parent]) {
      throw new Error(`sector ${slug} names a parent that does not exist: ${meta.parent}`);
    }
    if (meta.parent && slug !== `${meta.parent}/${slug.split("/").pop()}`) {
      throw new Error(`child slug ${slug} does not start with its parent ${meta.parent}`);
    }
  }

  return raw.sectors as Record<SectorSlug, SectorMeta>;
})();

export const SECTORS: Record<SectorSlug, string> = Object.fromEntries(
  Object.entries(SECTOR_SPINE).map(([slug, meta]) => [slug, meta.label])
) as Record<SectorSlug, string>;

// Every child slug, by parent. Empty for a leaf.
const CHILDREN: Record<string, SectorSlug[]> = {};
for (const [slug, meta] of Object.entries(SECTOR_SPINE)) {
  if (meta.parent) (CHILDREN[meta.parent] ??= []).push(slug as SectorSlug);
}

export function getSectorMeta(slug: SectorSlug): SectorMeta {
  return SECTOR_SPINE[slug];
}

export function getChildren(slug: SectorSlug): SectorSlug[] {
  return CHILDREN[slug] ?? [];
}

export function getParent(slug: SectorSlug): SectorSlug | null {
  return SECTOR_SPINE[slug]?.parent ?? null;
}

export function isChild(slug: SectorSlug): boolean {
  return getParent(slug) !== null;
}

export function getSectorSlugs(): SectorSlug[] {
  return Object.keys(SECTOR_SPINE) as SectorSlug[];
}

let cachedMeasures: Measure[] | null = null;

// Build-time only. No fetch, no client-side data loading.
export function getAllMeasures(): Measure[] {
  if (cachedMeasures) return cachedMeasures;
  const all: Measure[] = [];
  for (const fname of DATA_FILES) {
    const filePath = path.join(DATA_DIR, fname);
    if (!fs.existsSync(filePath)) continue;
    const raw = fs.readFileSync(filePath, "utf-8");
    const rows = JSON.parse(raw) as Measure[];
    all.push(...rows);
  }
  cachedMeasures = all;
  return all;
}

export interface SectorMeasures {
  named: Measure[];
  reached: Measure[];
}

// A parent rolls its children up: a measure on chem/plastics is a measure the
// chemicals page must show, or the parent under-reports itself. It rolls up
// into whichever list the measure earned on the child — a row that NAMES
// chem/plastics names it on the chemicals page too. A child does NOT roll
// down: it shows only what applies to the child, which is the whole reason it
// is a separate slug.
export function getMeasuresForSector(slug: SectorSlug): SectorMeasures {
  const all = getAllMeasures();
  const own = [slug, ...getChildren(slug)];
  const hits = (list: SectorSlug[] | undefined) =>
    list?.some((s) => own.includes(s)) ?? false;
  const named = all.filter((m) => hits(m.sectors_named));
  const reached = all.filter((m) => !hits(m.sectors_named) && hits(m.sectors_reached));
  return { named, reached };
}

// The named list, split for a parent with children: rows naming the parent
// itself apply to the sector as a whole; rows that arrive by rollup apply to
// one child and are listed under that child's name rather than blended in.
// A row naming both parent and child counts as whole-sector — the parent tag
// is the broader claim. For a childless sector `whole` is the entire named
// list and `byChild` is empty.
export interface NamedSplit {
  whole: Measure[];
  byChild: Array<{ child: SectorSlug; rows: Measure[] }>;
}

export function splitNamed(slug: SectorSlug): NamedSplit {
  const { named } = getMeasuresForSector(slug);
  const children = getChildren(slug);
  const whole = named.filter((m) => m.sectors_named?.includes(slug));
  const byChild = children
    .map((child) => ({
      child,
      rows: named.filter(
        (m) => !m.sectors_named?.includes(slug) && m.sectors_named?.includes(child)
      ),
    }))
    .filter((g) => g.rows.length > 0);
  return { whole, byChild };
}

export function getSectorCount(slug: SectorSlug): number {
  const { named, reached } = getMeasuresForSector(slug);
  return named.length + reached.length;
}

// ---------------------------------------------------------------------------
// Routing. Measure ids are unique per file but NOT across files (PRM-01 and
// GOV-01/02 each appear in two files), so the URL carries both.
// ---------------------------------------------------------------------------

export function measureHref(measure: Measure): string {
  return `/measures/${measure.file}/${measure.id.toLowerCase()}`;
}

export function getMeasure(file: string, id: string): Measure | undefined {
  return getAllMeasures().find(
    (m) => m.file === file && m.id.toLowerCase() === id.toLowerCase()
  );
}

// ---------------------------------------------------------------------------
// Aggregates. Every count the homepage shows is derived here from the register
// — nothing on the page is a typed-in number.
// ---------------------------------------------------------------------------

export const CLASS_LABELS: Record<MeasureClass, string> = {
  business: "Businesses",
  commission: "European Commission",
  state: "Governments",
  investor: "Foreign investors",
  household: "Households",
};

// Order the ledger reads in — widest constituency first.
const CLASS_ORDER: MeasureClass[] = ["business", "state", "commission", "investor", "household"];

export interface RegisterStats {
  measures: number;
  sectors: number;
  classes: number;
  sourceChecked: number; // percent of rows carrying verbatim source text
}

export function getRegisterStats(): RegisterStats {
  const all = getAllMeasures();
  const classes = new Set(all.map((m) => m.class));
  const withSource = all.filter((m) => m.source_text && m.source_text.trim().length > 0);
  return {
    measures: all.length,
    sectors: getSectorSlugs().length,
    classes: classes.size,
    sourceChecked: Math.round((withSource.length / all.length) * 100),
  };
}

export interface LedgerRow {
  cls: MeasureClass;
  label: string;
  added: number;
  removed: number;
}

export function getClassLedger(): LedgerRow[] {
  const all = getAllMeasures();
  return CLASS_ORDER.map((cls) => {
    const rows = all.filter((m) => m.class === cls);
    return {
      cls,
      label: CLASS_LABELS[cls],
      added: rows.filter((m) => m.direction === "add").length,
      removed: rows.filter((m) => m.direction === "rem").length,
    };
  }).filter((r) => r.added + r.removed > 0);
}

export const DRIVER_CODES: DDriver[] = ["D1", "D2", "D3", "D4", "D5", "D6", "D7"];

export function getDriverFrequency(): Record<DDriver, number> {
  const counts = Object.fromEntries(DRIVER_CODES.map((d) => [d, 0])) as Record<DDriver, number>;
  for (const m of getAllMeasures()) {
    for (const d of m.drivers ?? []) counts[d] += 1;
  }
  return counts;
}

// The signals feed. No row carries a date, so "latest" is file order — the
// register is appended to in the order provisions are extracted. Alternating
// the sign keeps the feed from reading as a single-direction package.
export function getSignals(limit = 6): Measure[] {
  const all = getAllMeasures().filter((m) => (m.duty ?? m.benefit ?? "").length > 0);
  const removed = all.filter((m) => m.direction === "rem");
  const added = all.filter((m) => m.direction === "add");
  const out: Measure[] = [];
  for (let i = 0; out.length < limit && (i < removed.length || i < added.length); i++) {
    if (removed[i]) out.push(removed[i]);
    if (out.length < limit && added[i]) out.push(added[i]);
  }
  return out;
}

export interface SectorCount {
  slug: SectorSlug;
  name: string;
  count: number;
}

export function getSectorCounts(): SectorCount[] {
  return getSectorSlugs()
    .map((slug) => ({ slug, name: SECTORS[slug], count: getSectorCount(slug) }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

export interface SectorStats {
  total: number;
  added: number;
  removed: number;
  named: number;
}

export function getSectorStats(slug: SectorSlug): SectorStats {
  const { named, reached } = getMeasuresForSector(slug);
  const all = [...named, ...reached];
  return {
    total: all.length,
    added: all.filter((m) => m.direction === "add").length,
    removed: all.filter((m) => m.direction === "rem").length,
    named: named.length,
  };
}

// Sectors that most often co-occur with this one in the same measure.
export function getRelatedSectors(slug: SectorSlug, limit = 4): SectorCount[] {
  const counts = new Map<SectorSlug, number>();
  for (const m of getAllMeasures()) {
    const touched = new Set([...(m.sectors_named ?? []), ...(m.sectors_reached ?? [])]);
    if (!touched.has(slug)) continue;
    for (const other of touched) {
      if (other === slug) continue;
      counts.set(other, (counts.get(other) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([s, count]) => ({ slug: s, name: SECTORS[s], count }));
}

// Other measures from the same file that share a sector or an id prefix.
export function getRelatedMeasures(measure: Measure, limit = 4): Measure[] {
  const prefix = measure.id.split("-")[0];
  const touched = new Set([...(measure.sectors_named ?? []), ...(measure.sectors_reached ?? [])]);
  return getAllMeasures()
    .filter((m) => !(m.file === measure.file && m.id === measure.id))
    .map((m) => {
      const shared = [...(m.sectors_named ?? []), ...(m.sectors_reached ?? [])].filter((s) =>
        touched.has(s)
      ).length;
      let score = shared;
      if (m.file === measure.file) score += 2;
      if (m.file === measure.file && m.id.startsWith(prefix)) score += 4;
      return { m, score };
    })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((x) => x.m);
}

// Ticker headlines. The flag uses the same valence vocabulary as the tags, so
// the page never calls the same provision two different things.
export interface TickerItem {
  label: string;
  positive: boolean;
  text: string;
}

export function getTickerItems(limit = 6): TickerItem[] {
  return getSignals(limit).map((m) => ({
    label: valenceLabel(m.measure_type, m.direction).toUpperCase(),
    positive: isPositiveValence(m.measure_type, m.direction),
    // Duty statements run to 200+ characters; the chrome has one line. Cut at
    // the last word boundary that fits rather than mid-word.
    text: clip(m.duty ?? m.benefit ?? "", 96),
  }));
}

function clip(text: string, max: number): string {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const boundary = cut.lastIndexOf(" ");
  return `${cut.slice(0, boundary > 0 ? boundary : max)}…`;
}

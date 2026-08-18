import fs from "node:fs";
import path from "node:path";
import type { DDriver, FileMeta, Measure, MeasureClass, SectorSlug } from "./types";
import { isPositiveValence, valenceLabel } from "./valence";

// data/ lives one level up from web/ at the repo root. Untouched, read-only.
const DATA_DIR = path.join(process.cwd(), "..", "data");
const DATA_FILES = ["omnibus.json", "ets.json", "iaa.json", "cbam.json", "nzia.json", "crma.json"];

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
};

export const SECTORS: Record<SectorSlug, string> = {
  steel: "Steel",
  cement: "Cement and concrete",
  alu: "Aluminium and metals",
  chem: "Chemicals and refining",
  glass: "Glass, ceramics, paper",
  power: "Power and heat",
  waste: "Waste and landfill",
  ship: "Shipping",
  air: "Aviation",
  auto: "Automotive",
  build: "Construction",
  batsol: "Batteries and solar",
  clean: "Wind, heat pumps, hydrogen",
  ccs: "Carbon capture and fuels",
};

export function getSectorSlugs(): SectorSlug[] {
  return Object.keys(SECTORS) as SectorSlug[];
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

export function getMeasuresForSector(slug: SectorSlug): SectorMeasures {
  const all = getAllMeasures();
  const named = all.filter((m) => m.sectors_named?.includes(slug));
  const reached = all.filter(
    (m) => !m.sectors_named?.includes(slug) && m.sectors_reached?.includes(slug)
  );
  return { named, reached };
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

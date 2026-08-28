import fs from "node:fs";
import path from "node:path";
import { getRecords, type ChangeRecord } from "./records";
import { isOpportunitySignal as isSignal } from "./signals";
import {
  FUNDING_COMMITTED,
  eur,
  fundingAmount,
  getImportance,
  type Funding,
  type Parameter,
  type RankedMeasure,
} from "./transition";
import { getOpportunityProse } from "./sitetext";

// THE OPPORTUNITY SECTION'S DATA, brief 5 §4.
//
// Four computed views, and this module reads what they stand on. Nothing here
// computes a euro or a ranking: the committed sum and the section's one
// sentence come out of data/transition/opportunity/<sector>.json, which
// sources/build_opportunity.py builds and gates, and the support measures come
// out of the importance store in the ranking's own order.
//
// WHAT IS NOT BUILT YET, and why it is named rather than stubbed. §4.3 (rules
// that create demand) needs the creates_demand_for edge type, which is step 3
// of brief 5 §9. §4.4 (open windows) needs watch channel three, which is step 4.
// Neither renders, and neither has a placeholder — a section that showed
// "no demand rules tracked" would be claiming the reading has been done.

export interface OpportunityFact {
  id: string;
  label: string;
  text: string;
  as_of: string;
  parts: Record<string, unknown>;
}

export interface OpportunityDoc {
  sector: string;
  fingerprint: string;
  sentence: { text: string; from: string[]; source?: string; reviewed?: string };
  facts: OpportunityFact[];
  override_stale: boolean;
  notes: string[];
}

const DIR = path.join(process.cwd(), "..", "data", "transition", "opportunity");
const cache = new Map<string, OpportunityDoc | null>();

/** The built block for a sector, or null where none has been built. Null is not
 *  an error: a sector arrives here by having a dataset, exactly as it arrives at
 *  the product template at all. */
export function getOpportunity(sector: string): OpportunityDoc | null {
  if (cache.has(sector)) return cache.get(sector)!;
  const file = path.join(DIR, `${sector.replace("/", "__")}.json`);
  const doc = fs.existsSync(file)
    ? (JSON.parse(fs.readFileSync(file, "utf8")) as OpportunityDoc)
    : null;
  cache.set(sector, doc);
  return doc;
}

/** §4.2. Measures reaching the sector whose money direction for the bearer is
 *  support, in the ranking's order.
 *
 *  The direction is the register's field, read and not re-derived. A measure
 *  that both costs and pays would be a measure with two money blocks, which the
 *  schema does not allow — one provision, one direction, and the netting the
 *  ranking does with them is not drawn on this page at all. */
export function supportMeasures(sector: string): RankedMeasure[] {
  const imp = getImportance(sector);
  if (!imp) return [];
  return imp.measures.filter((m) => m.money?.direction === "support");
}

/** An ISO date, which is what makes a window a dated one. Nothing on the
 *  platform carries one in `when` yet; the dated windows arrive with watch
 *  channel three (step 4). Matching the shape rather than inventing a field
 *  means the day one lands it renders, without a schema change here. */
const ISO_DATE = /\b(\d{4}-\d{2}-\d{2})\b/;

/** The eligibility window as a clause, or null.
 *
 *  Two forms and no third. A standing scheme has eligibility rather than an
 *  opening — "eligibility ongoing" — and a call has a date it closes on. A
 *  `when` that is neither renders no clause: it is the register's phrasing
 *  about when a provision BITES, which is not always a window and is never a
 *  promise about when somebody can apply. */
export function supportWindow(m: RankedMeasure): string | null {
  const prose = getOpportunityProse();
  const when = (m.when ?? "").trim();
  if (!when) return null;
  const dated = ISO_DATE.exec(when);
  if (dated) return prose.support_window.dated.replace("{date}", dated[1]);
  return prose.support_window[when] ?? null;
}

/** What a support measure PAYS, as a context-specific template — never the
 *  measure's standard one-liner, which is the Policies section's alone
 *  (brief 5 §5, gated by sources/check_one_liner_scope.py).
 *
 *  Keyed on the money model, because the model is what the figure MEANS: a
 *  grant that has landed and an auction floor that has not are different offers
 *  and cannot share a sentence. A model with no template throws rather than
 *  falling back to something generic.
 *
 *  THE AMOUNT IS THE SECTOR'S SHARE, NOT THE MEASURE'S TOTAL, and that is the
 *  whole reason this function takes the funding rows. The importance store's
 *  `money.value` is what the measure has paid EVERYWHERE; this section has just
 *  printed what is committed to THIS sector a few lines above, and the template
 *  says the second is part of the first. On cement the two coincide — every
 *  Innovation Fund row under ets:FND-03 finances a cement plant — and on the
 *  first measure that also pays another industry they would not. Summing the
 *  sector's own rows makes "X of the Y" true by construction rather than by
 *  luck, and a sentence claiming a share that is not one is the one thing this
 *  template must never say. */
export function supportFact(
  m: RankedMeasure,
  sectorFunding: Funding[],
  params: Map<string, Parameter>,
): string {
  const prose = getOpportunityProse();
  const money = m.money;
  if (!money || money.direction !== "support") {
    throw new Error(`${m.measure} is not a support-direction measure`);
  }
  const template = prose.support_fact[money.model ?? ""];
  if (!template) {
    throw new Error(
      `no support-fact template for the money model "${money.model}". Add one to ` +
        `data/prose.json → opportunity.support_fact deliberately: a template that covered ` +
        `every model would be saying nothing about any of them`,
    );
  }

  const committedRows = sectorFunding.filter((f) => FUNDING_COMMITTED.includes(f.status));
  const underThis = committedRows.filter((f) => f.under === m.measure);
  const awarded = underThis.reduce((sum, f) => sum + (fundingAmount(f, params) ?? 0), 0);
  const committed = committedRows.reduce((sum, f) => sum + (fundingAmount(f, params) ?? 0), 0);
  const projects = new Set(
    underThis.flatMap((f) => f.finances.filter((n) => n.startsWith("project:"))),
  );

  const text = template
    .replace("{amount}", awarded > 0 ? eur(awarded) : "no published amount")
    .replace("{committed}", eur(committed))
    .replace(
      "{recipients}",
      `${projects.size} tracked ${projects.size === 1 ? "project" : "projects"}`,
    );
  const window = supportWindow(m);
  return window ? `${text} ${window[0].toUpperCase()}${window.slice(1)}.` : text;
}

/** §4.6's predicate, re-exported. It lives in lib/signals.ts, which imports
 *  nothing at runtime so that it can be tested outside a bundler — this module
 *  reads the disk and cannot be. NOT A NEW DATA STRUCTURE, which §4.6 says
 *  twice: it is a filter over the records that already exist. */
export { isOpportunitySignal } from "./signals";

/** The sector's opportunity signals, newest first. */
export function opportunitySignals(sector: string, records: ChangeRecord[]): ChangeRecord[] {
  const support = new Set(supportMeasures(sector).map((m) => m.measure));
  return records.filter((r) => isSignal(r, support));
}

/** Every measure on the platform whose money direction is support, across every
 *  sector with a ranking. The change-record list is site-wide, so its filter
 *  cannot ask one sector's question. */
export function allSupportMeasureIds(sectors: string[]): Set<string> {
  const out = new Set<string>();
  for (const s of sectors) for (const m of supportMeasures(s)) out.add(m.measure);
  return out;
}

/** The site-wide filter the change-record list applies. */
export function signalIds(sectors: string[]): string[] {
  const support = allSupportMeasureIds(sectors);
  return getRecords()
    .filter((r) => isSignal(r, support))
    .map((r) => r.id);
}

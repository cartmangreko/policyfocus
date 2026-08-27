import fs from "node:fs";
import path from "node:path";
import { getRecords, type ChangeRecord } from "./records";
import { isOpportunitySignal as isSignal } from "./signals";
import {
  BEARER_LABEL,
  eur,
  getImportance,
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

/** What a support measure PAYS, as a context-specific template — never the
 *  measure's standard one-liner, which is the Policies section's alone
 *  (brief 5 §5, gated by sources/check_one_liner_scope.py).
 *
 *  Keyed on the money model, because the model is what the figure MEANS: a
 *  grant that has landed and an auction floor that has not are different offers
 *  and cannot share a sentence. A model with no template throws rather than
 *  falling back to something generic. */
export function supportFact(m: RankedMeasure): string {
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
  const recipients = m.reached_via?.length
    ? `${m.reached_via.length} tracked ${m.reached_via.length === 1 ? "project" : "projects"}`
    : (BEARER_LABEL[money.bearer ?? ""] ?? "the bearer").toLowerCase();
  const window = prose.support_window[m.when ?? ""] ?? null;
  const text = template
    .replace("{amount}", money.computable && money.value ? eur(money.value) : "an unpublished amount")
    .replace("{recipients}", recipients)
    .replace("{window}", window ?? "");
  // A window nobody has worded leaves no dangling clause behind it.
  return text.replace(/,\s*\./, ".").replace(/\s+/g, " ").trim();
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

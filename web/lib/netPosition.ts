import { getMeasuresForSector } from "./data";
import { getFileBasis } from "./files";
import { isPositiveValence, valenceLabel } from "./valence";
import type { ValenceLabel } from "./valence";
import type { Measure, SectorSlug } from "./types";

// The net-position strip: what the corpus, taken together, does to one sector.
// Computed at build time from the register — no new data, no stored totals.
//
// Three things are counted, and the strip prints all three because leaving any
// of them out would flatter the number:
//
//   the valence         what each measure does (the shared valence vocabulary,
//                       never a second naming of the same thing)
//   the legal standing  in force vs proposed, from the file the row came from.
//                       A sector facing eleven proposed duties and none in
//                       force is not in the same position as the reverse.
//   the weight          how heavy the rows are, where the register records it.
//
// Weight intensity is recorded on omnibus rows only, and omnibus rows name no
// sector, so for now every sector's intensity line reads "not recorded". That
// is left visible rather than hidden: the gap is a fact about the register's
// coverage, and it will fill in as weight is extracted for the other files.

export type Intensity = "High" | "Medium" | "Low";
const INTENSITIES: Intensity[] = ["High", "Medium", "Low"];

// The order the strip reads in: pressure first, then relief, then the
// benefit-side pair. Fixed so two sectors can be compared at a glance.
const VALENCE_ORDER: ValenceLabel[] = [
  "Requirement",
  "Simplification",
  "Opportunity",
  "Support cut",
  "Entitlement",
  "Entitlement withdrawn",
  "Neutral",
];

export interface NetPositionRow {
  valence: ValenceLabel;
  positive: boolean;
  total: number;
  /** Legal standing of the file each row came from. */
  inForce: number;
  proposed: number;
  mixed: number;
  intensity: Record<Intensity, number>;
  /** Rows carrying no weight_intensity at all. */
  intensityUnrecorded: number;
}

export interface NetPosition {
  rows: NetPositionRow[];
  total: number;
  /** Totals across the valences that read positive / negative. */
  positive: number;
  negative: number;
  anyIntensityRecorded: boolean;
}

function blank(valence: ValenceLabel, positive: boolean): NetPositionRow {
  return {
    valence,
    positive,
    total: 0,
    inForce: 0,
    proposed: 0,
    mixed: 0,
    intensity: { High: 0, Medium: 0, Low: 0 },
    intensityUnrecorded: 0,
  };
}

export function getNetPosition(slug: SectorSlug): NetPosition {
  const { named, reached } = getMeasuresForSector(slug);
  const all: Measure[] = [...named, ...reached];

  const rows = new Map<ValenceLabel, NetPositionRow>();
  for (const m of all) {
    const label = valenceLabel(m.measure_type, m.direction);
    const positive = isPositiveValence(m.measure_type, m.direction);
    const row = rows.get(label) ?? blank(label, positive);

    row.total += 1;

    const basis = getFileBasis(m.file);
    if (basis === "adopted") row.inForce += 1;
    else if (basis === "proposed") row.proposed += 1;
    else if (basis === "mixed") row.mixed += 1;

    const intensity = m.weight_intensity as Intensity | undefined;
    if (intensity && INTENSITIES.includes(intensity)) row.intensity[intensity] += 1;
    else row.intensityUnrecorded += 1;

    rows.set(label, row);
  }

  const ordered = VALENCE_ORDER.map((v) => rows.get(v)).filter(
    (r): r is NetPositionRow => r !== undefined
  );

  return {
    rows: ordered,
    total: all.length,
    positive: ordered.filter((r) => r.positive).reduce((n, r) => n + r.total, 0),
    negative: ordered.filter((r) => !r.positive).reduce((n, r) => n + r.total, 0),
    anyIntensityRecorded: ordered.some((r) => INTENSITIES.some((i) => r.intensity[i] > 0)),
  };
}

/** The secondary line under a valence: the weight distribution, or the honest
 *  statement that the register does not record one for these rows. */
export function intensityLine(row: NetPositionRow): string {
  const parts = INTENSITIES.filter((i) => row.intensity[i] > 0).map((i) => `${i} ${row.intensity[i]}`);
  if (!parts.length) return "weight not recorded";
  if (row.intensityUnrecorded) parts.push(`not recorded ${row.intensityUnrecorded}`);
  return parts.join(" · ");
}

import fs from "node:fs";
import path from "node:path";
import { FILES, SECTORS, getAllMeasures, getMeasure } from "./data";
import type { BasisStatus } from "./files";
import type { DiagramNode, DiagramEdge } from "./findings";
import { REACH_CHANNEL_LABEL, inferReachChannel } from "./reachChannel";
import type { Measure, SectorSlug } from "./types";

// The records layer: one permanent page per legislative event, built by
// sources/build_records.py.
//
// Three rules, all inherited from the gate rather than decided here:
//
//   1. The index is READ, never derived, and it carries the RENDERED prose.
//      data/records/index.json is written by the gate after every check
//      passes, with the headline and body already composed from the reviewed
//      templates in data/prose.json. Nothing on this side renders a template:
//      a reviewed text renders unchanged or not at all (sources/scope.md, "No
//      free-generated text on the site").
//   2. Nothing here recomputes a count. Every number a record prints was
//      recomputed from the register and matched exactly at build time; a
//      mismatch is a build failure, not a render-time correction.
//   3. A record whose prose is not APPROVED does not render. The gate builds
//      draft templates deliberately, so they can be read, and stamps the
//      status into every record — this module is the thing that stops a draft
//      reaching a reader.
const RECORDS_DIR = path.join(process.cwd(), "..", "data", "records");

// Mirrors build_records.FAMILIES. Each names an event shape and decides which
// counts the gate recomputes, so the two sides cannot drift into different
// vocabularies for the same event.
export type RecordTemplate =
  | "new_act_ingested"
  | "amendment"
  | "delegated_act"
  | "status_change";

export interface RecordMeasureRef {
  file: string;
  row_id: string;
}

export interface ChangeRecord {
  id: string;
  template: RecordTemplate;
  event_date: string;
  file: string;
  act_label: string;
  basis_status: BasisStatus;
  /** Composed by the gate from the reviewed template. Never composed here. */
  headline: string;
  body: string;
  prose_status: string;
  counts: {
    measures: number;
    sectors_named: number;
    /** Absent when this act's reach may not be stated — see `reach`. */
    sectors_reached?: number;
    top_sector_named: number;
  };
  top_sector: SectorSlug;
  sectors_named: SectorSlug[];
  /** Absent when reach is suppressed; the gate ships the record without it. */
  sectors_reached?: SectorSlug[];
  measures: RecordMeasureRef[];
  prior_act?: string;
  /** Why the reach clause is missing, when it is. sources/scope.md, "Reach is
   *  not stated on a record about an amending proposal". */
  reach: { suppressed: boolean; reason?: string };
}

export interface RecordDiagram {
  id: string;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

const APPROVED = "approved";

let cachedIndex: ChangeRecord[] | null = null;

/** Newest first — the order the gate wrote, not a re-sort.
 *
 *  Records whose prose is not approved are dropped here rather than rendered
 *  with a warning. A draft that reaches a reader has already failed; a feed
 *  that is short by one entry has not. */
export function getRecords(): ChangeRecord[] {
  if (cachedIndex) return cachedIndex;
  const indexPath = path.join(RECORDS_DIR, "index.json");
  const all: ChangeRecord[] = fs.existsSync(indexPath)
    ? (JSON.parse(fs.readFileSync(indexPath, "utf-8")) as ChangeRecord[])
    : [];
  cachedIndex = all.filter((r) => r.prose_status === APPROVED);
  return cachedIndex;
}

export function getRecord(id: string): ChangeRecord | null {
  return getRecords().find((r) => r.id === id) ?? null;
}

const diagramCache = new Map<string, RecordDiagram | null>();

export function getRecordDiagram(id: string): RecordDiagram | null {
  const cached = diagramCache.get(id);
  if (cached !== undefined) return cached;
  // Only ids the index carries reach the filesystem, so the id never arrives
  // as an arbitrary path segment.
  const known = getRecords().some((r) => r.id === id);
  const filePath = path.join(RECORDS_DIR, "diagrams", `${id}.json`);
  const diagram =
    known && fs.existsSync(filePath)
      ? (JSON.parse(fs.readFileSync(filePath, "utf-8")) as RecordDiagram)
      : null;
  diagramCache.set(id, diagram);
  return diagram;
}

export function getRecordsForSector(slug: SectorSlug): ChangeRecord[] {
  return getRecords().filter(
    (r) => r.sectors_named.includes(slug) || (r.sectors_reached ?? []).includes(slug)
  );
}

export function recordHref(id: string): string {
  return `/changes/${id}`;
}

export function actShortName(file: string): string {
  return FILES[file]?.name.split(" — ")[0] ?? file.toUpperCase();
}

export function sectorName(slug: string): string {
  return SECTORS[slug as SectorSlug] ?? slug;
}

// ---------------------------------------------------------------------------
// The measures a record is about. A record about particular measures names
// them; one about a whole act names none, because the measures involved are
// all of them and the act page holds the list. Both cases answer the same
// question here, so no page has to know which family it is looking at.
// ---------------------------------------------------------------------------

export function recordMeasures(record: ChangeRecord): Measure[] {
  if (record.measures.length > 0) {
    return record.measures
      .map((ref) => getMeasure(ref.file, ref.row_id))
      .filter((m): m is Measure => m !== undefined);
  }
  return getAllMeasures().filter((m) => m.file === record.file);
}

/** Whether the record names its measures, or stands for the whole act. */
export function isWholeAct(record: ChangeRecord): boolean {
  return record.measures.length === 0;
}

// ---------------------------------------------------------------------------
// Reach channels. The channel is not stored per entry — sectors_reached is a
// flat list — so it is inferred from fields that ARE stored, by the same
// module the act and sector pages use. Kept on this side deliberately: a
// second implementation in the builder would be a second thing to keep in
// step with reachChannel.ts, and the channel is a display fact, not a
// published number.
// ---------------------------------------------------------------------------

export interface ReachedSector {
  slug: SectorSlug;
  name: string;
  /** Every channel by which this record's measures arrive at the sector. */
  channels: string[];
}

export function reachedWithChannels(record: ChangeRecord): ReachedSector[] {
  const measures = recordMeasures(record);
  return (record.sectors_reached ?? []).map((slug) => {
    const reaching = measures.filter((m) => (m.sectors_reached ?? []).includes(slug));
    const channels = [
      ...new Set(reaching.map((m) => REACH_CHANNEL_LABEL[inferReachChannel(m)])),
    ].sort();
    return { slug, name: sectorName(slug), channels };
  });
}

// ---------------------------------------------------------------------------
// The evidence strip. One line under every headline, wherever a record
// appears: the same discipline the findings carry — a headline never stands
// alone without the line saying what it rests on.
// ---------------------------------------------------------------------------

export function evidenceStrip(record: ChangeRecord): string {
  const n = record.counts.measures;
  // The act is deliberately NOT in the strip. It is already the subject of the
  // headline and it is already the first tag on the card, and a card that says
  // the same act name three times reads as a template rather than as news.
  const parts = [
    `${n} ${n === 1 ? "measure" : "measures"}`,
    `${record.counts.sectors_named} ${record.counts.sectors_named === 1 ? "sector" : "sectors"} named`,
  ];
  if (record.counts.sectors_reached !== undefined) {
    parts.push(`${record.counts.sectors_reached} reached`);
  }
  return parts.join(" · ");
}

// The event, said in display vocabulary. The record's own prose says what
// happened; this is the label on the chip beside the date, and it has to be
// legible on its own in a feed.
export const TEMPLATE_LABEL: Record<RecordTemplate, string> = {
  new_act_ingested: "New act",
  amendment: "Amended",
  delegated_act: "Delegated act",
  status_change: "Status change",
};

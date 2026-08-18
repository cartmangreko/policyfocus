import fs from "node:fs";
import path from "node:path";
import { FILES, SECTORS, getMeasure } from "./data";
import { getExposure } from "./exposure";
import type { BasisStatus } from "./files";
import type { Measure, SectorSlug } from "./types";

// The findings layer: short claims of the form "this measure set means X for
// sector Y", hand-authored as data/findings/<id>.json.
//
// Two rules govern this module, and both come from the gate rather than from
// the front end:
//
//   1. The index is READ, never derived. data/findings/index.json is written by
//      sources/build_findings.py after every check passes, so a JSON file
//      dropped into the directory by hand publishes nothing. This module reads
//      the index and then reads only the files the index names.
//   2. Every number a finding prints has already been checked against the data
//      that holds it. Nothing here recomputes a share or re-resolves a row to
//      "fix" a mismatch — a mismatch is a build failure, not a render-time
//      decision.
const FINDINGS_DIR = path.join(process.cwd(), "..", "data", "findings");

// Mirrors build_findings.TEMPLATES. Every template names an arithmetic shape;
// there is deliberately no editorial value — findings are arithmetic-only
// (sources/scope.md, "A finding states arithmetic"), and the gate fails the
// build if an editorial template is ever added back.
export type FindingTemplate =
  | "reach"
  | "indirect_exposure"
  | "support_mismatch"
  | "net_position"
  | "country_concentration";

export type ExposureRelation = "supplier" | "customer" | "import_origin";

export interface MeasureRef {
  file: string;
  row_id: string;
}

export interface ExposureRef {
  sector: string;
  /** A sector slug for supplier/customer; a country code for import_origin. */
  partner_sector: string;
  relation: ExposureRelation;
  share_pct: number;
  /** "EU" or an EU member ISO 3166-1 alpha-2 code. */
  view: string;
}

export interface FindingIndexEntry {
  id: string;
  template: FindingTemplate;
  headline: string;
  sectors: SectorSlug[];
  files: string[];
  basis_status: BasisStatus;
  date: string;
}

export interface Finding extends FindingIndexEntry {
  schema_version: number;
  body: string;
  evidence: {
    measures: MeasureRef[];
    exposure?: ExposureRef[];
    notes?: string;
  };
  review?: { status: "open" | "resolved"; q?: string; since?: string };
}

let cachedIndex: FindingIndexEntry[] | null = null;

/** Newest first — the order the gate wrote, not a re-sort. */
export function getFindingsIndex(): FindingIndexEntry[] {
  if (cachedIndex) return cachedIndex;
  const indexPath = path.join(FINDINGS_DIR, "index.json");
  cachedIndex = fs.existsSync(indexPath)
    ? (JSON.parse(fs.readFileSync(indexPath, "utf-8")) as FindingIndexEntry[])
    : [];
  return cachedIndex;
}

const cache = new Map<string, Finding | null>();

export function getFinding(id: string): Finding | null {
  const cached = cache.get(id);
  if (cached !== undefined) return cached;

  // Only ids the index carries are read, so the id never reaches the
  // filesystem as an arbitrary path segment.
  const known = getFindingsIndex().some((f) => f.id === id);
  const filePath = path.join(FINDINGS_DIR, `${id}.json`);
  const finding =
    known && fs.existsSync(filePath)
      ? (JSON.parse(fs.readFileSync(filePath, "utf-8")) as Finding)
      : null;
  cache.set(id, finding);
  return finding;
}

export function getAllFindings(): Finding[] {
  return getFindingsIndex()
    .map((e) => getFinding(e.id))
    .filter((f): f is Finding => f !== null);
}

export function getRecentFindings(limit = 5): FindingIndexEntry[] {
  return getFindingsIndex().slice(0, limit);
}

export function getFindingsForSector(slug: SectorSlug): FindingIndexEntry[] {
  return getFindingsIndex().filter((f) => f.sectors.includes(slug));
}

export function findingHref(id: string): string {
  return `/findings/${id}`;
}

// ---------------------------------------------------------------------------
// Evidence resolution. Every reference here resolved at build time in
// build_findings.py; a null return means the index and the register have gone
// out of step, which the gate would have caught — so the pages treat it as
// nothing to render rather than as a fact to invent.
// ---------------------------------------------------------------------------

export function resolveMeasures(finding: Finding): Measure[] {
  return finding.evidence.measures
    .map((ref) => getMeasure(ref.file, ref.row_id))
    .filter((m): m is Measure => m !== undefined);
}

export interface ResolvedExposure extends ExposureRef {
  /** The sentence the page prints. Composed here so the card strip and the
   *  evidence section cannot describe the same reference differently. */
  sentence: string;
  href: string;
  /** Short form for the card strip: "power = 8.1% of cement inputs". */
  short: string;
}

function sectorName(slug: string): string {
  return SECTORS[slug as SectorSlug] ?? slug;
}

function viewLabel(view: string): string {
  return view === "EU" ? "EU view" : `${view} view`;
}

export function resolveExposure(finding: Finding): ResolvedExposure[] {
  const refs = finding.evidence.exposure ?? [];
  return refs.map((ref) => {
    const subject = sectorName(ref.sector).toLowerCase();
    // For supplier/customer the partner is an industry the register also
    // tracks as a sector; for import_origin it is a country code, printed as
    // the exposure file carries it.
    const partner =
      ref.relation === "import_origin" ? ref.partner_sector : sectorName(ref.partner_sector);

    let sentence: string;
    let short: string;
    if (ref.relation === "supplier") {
      sentence = `${partner} supplies ${ref.share_pct}% of ${subject}'s total inputs (${viewLabel(ref.view)}).`;
      short = `${partner.toLowerCase()} = ${ref.share_pct}% of ${subject} inputs`;
    } else if (ref.relation === "customer") {
      sentence = `${partner} takes ${ref.share_pct}% of ${subject}'s total output (${viewLabel(ref.view)}).`;
      short = `${partner.toLowerCase()} = ${ref.share_pct}% of ${subject} output`;
    } else {
      sentence = `${partner} accounts for ${ref.share_pct}% of ${subject}'s imported inputs (${viewLabel(ref.view)}).`;
      short = `${partner} = ${ref.share_pct}% of ${subject} imports`;
    }

    return {
      ...ref,
      sentence,
      short,
      href: `/sectors/${ref.sector}#exposure`,
    };
  });
}

/** Whether the sector page can show the panel a reference points at. */
export function hasExposurePanel(sector: string): boolean {
  return getExposure(sector) !== null;
}

// ---------------------------------------------------------------------------
// The evidence strip. One line, factual, composed from the finding itself:
// "{n} measures · {files} · {strongest exposure figure if any}". It is the
// reason a headline may never appear alone — see the note in globals.css.
// ---------------------------------------------------------------------------

export function fileShortName(file: string): string {
  return FILES[file]?.name.split(" — ")[0] ?? file.toUpperCase();
}

export function evidenceStrip(finding: Finding): string {
  const n = finding.evidence.measures.length;
  const parts = [
    `${n} ${n === 1 ? "measure" : "measures"}`,
    finding.files.map(fileShortName).join(", "),
  ];
  const exposure = resolveExposure(finding);
  if (exposure.length) {
    // The strongest figure, not the first — a strip that prints whichever
    // reference happened to be written first is not a summary of anything.
    const strongest = [...exposure].sort((a, b) => b.share_pct - a.share_pct)[0];
    parts.push(strongest.short);
  }
  return parts.join(" · ");
}

/** The index carries no evidence, so a card built from the index alone would
 *  have no strip. Cards therefore take the full finding; this is the loader
 *  the pages use. */
export function withEvidence(entries: FindingIndexEntry[]): Finding[] {
  return entries.map((e) => getFinding(e.id)).filter((f): f is Finding => f !== null);
}

export const BASIS_NOTE: Record<BasisStatus, string | null> = {
  adopted: null,
  // TODO-GEORGE: exact banner copy.
  proposed:
    "TODO-GEORGE — Based on proposed legislation. The provisions cited here are not in force and may change before adoption.",
  mixed:
    "TODO-GEORGE — Based in part on proposed legislation. Some provisions cited here are in force and some are not yet adopted and may change.",
};

export const BASIS_LABEL: Record<BasisStatus, string> = {
  adopted: "In force",
  proposed: "Proposed",
  mixed: "Mixed basis",
};

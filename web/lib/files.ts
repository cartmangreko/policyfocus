import fs from "node:fs";
import path from "node:path";

// Everything the site knows about the register FILES as documents: which
// EUR-Lex entries each was read from, whether it is law or a proposal, when it
// was fetched, and how many independent reads it has had.
//
// Build-time only, like lib/data.ts. Nothing here is a typed-in fact: the
// mapping comes from sources/register_files.json (shared with
// sources/build_findings.py so the two cannot drift), the legal status from
// sources/manifest.json, the dates from the .fetch.json sidecars, and the read
// count from which pass artifacts exist on disk.
const SOURCES_DIR = path.join(process.cwd(), "..", "sources");

export type BasisStatus = "adopted" | "proposed" | "mixed";

interface RegisterFileEntry {
  manifest_keys: string[];
  declared_status?: "adopted" | "proposed";
  declared_status_reason?: string;
}

interface ManifestEntry {
  celex?: string;
  kind?: string;
  com?: string;
  procedure?: string;
  status?: "adopted" | "proposed";
  consolidated_date?: string;
}

function readJson<T>(p: string): T | null {
  return fs.existsSync(p) ? (JSON.parse(fs.readFileSync(p, "utf-8")) as T) : null;
}

let cachedTable: Record<string, RegisterFileEntry> | null = null;

export function getRegisterFileTable(): Record<string, RegisterFileEntry> {
  if (cachedTable) return cachedTable;
  const doc = readJson<{ files: Record<string, RegisterFileEntry> }>(
    path.join(SOURCES_DIR, "register_files.json")
  );
  cachedTable = doc?.files ?? {};
  return cachedTable;
}

let cachedManifest: Record<string, ManifestEntry> | null = null;

export function getManifest(): Record<string, ManifestEntry> {
  if (cachedManifest) return cachedManifest;
  cachedManifest = readJson<Record<string, ManifestEntry>>(path.join(SOURCES_DIR, "manifest.json")) ?? {};
  return cachedManifest;
}

/** The statuses the manifest actually holds for one register file. */
export function getFileStatuses(file: string): Array<"adopted" | "proposed"> {
  const entry = getRegisterFileTable()[file];
  if (!entry) return [];
  const manifest = getManifest();
  const out = new Set<"adopted" | "proposed">();
  if (entry.declared_status) out.add(entry.declared_status);
  for (const key of entry.manifest_keys) {
    const status = manifest[key]?.status;
    if (status) out.add(status);
  }
  return [...out].sort();
}

// Same rule as STATUS_RULE in sources/build_findings.py: one status is that
// status, both is mixed. A file the table cannot answer for returns null and
// the page says so rather than picking a side.
export function getFileBasis(file: string): BasisStatus | null {
  const s = getFileStatuses(file);
  if (s.length === 0) return null;
  if (s.length === 1) return s[0];
  return "mixed";
}

export function basisOfFiles(files: string[]): BasisStatus | null {
  const all = new Set(files.flatMap(getFileStatuses));
  if (all.size === 0) return null;
  if (all.size === 1) return [...all][0];
  return "mixed";
}

export interface ReadHistory {
  /** How many independent extraction passes the file has had. */
  reads: number;
  /** True when the second read was compared against the first. */
  reconciled: boolean;
  /** True when the disagreements were frozen into a docket and ruled on. */
  docketed: boolean;
  label: string;
}

// Derived from what is on disk in sources/, not from a list that can drift:
//
//   <key>_pass_b.json               a second, independent read exists
//   <key>_disagreements.json        the two reads were compared
//   <key>_reconciliation_docket.json  the disagreements were frozen and ruled
//
// The register file itself is the first read. A file with no pass_b has had
// one read, and the coverage page says so — that is the point of the column.
export function getReadHistory(file: string): ReadHistory {
  const has = (suffix: string) => fs.existsSync(path.join(SOURCES_DIR, `${file}${suffix}`));
  const second = has("_pass_b.json");
  const reconciled = second && has("_disagreements.json");
  const docketed = reconciled && has("_reconciliation_docket.json");

  let label = "Single read";
  if (docketed) label = "Two independent reads, reconciled, rulings docketed";
  else if (reconciled) label = "Two independent reads, reconciled";
  else if (second) label = "Two independent reads, not yet reconciled";

  return { reads: second ? 2 : 1, reconciled, docketed, label };
}

export interface FileCelex {
  key: string;
  celex: string;
  status: "adopted" | "proposed";
  com?: string;
  procedure?: string;
  fetchedAt?: string;
}

/** The EUR-Lex documents behind one register file, with fetch dates. */
export function getFileSources(file: string): FileCelex[] {
  const entry = getRegisterFileTable()[file];
  if (!entry) return [];
  const manifest = getManifest();
  return entry.manifest_keys.flatMap((key) => {
    const m = manifest[key];
    if (!m?.celex) return [];
    const sidecar = readJson<{ fetched_at?: string }>(path.join(SOURCES_DIR, `${key}.fetch.json`));
    return [
      {
        key,
        celex: m.celex,
        status: m.status ?? "proposed",
        com: m.com,
        procedure: m.procedure,
        fetchedAt: sidecar?.fetched_at,
      },
    ];
  });
}

/** Most recent fetch across a file's sources, ISO date only. Null when the
 *  file predates the fetcher — omnibus, which was read from a local text. */
export function getLastUpdated(file: string): string | null {
  const dates = getFileSources(file)
    .map((s) => s.fetchedAt)
    .filter((d): d is string => Boolean(d))
    .sort();
  const latest = dates[dates.length - 1];
  return latest ? latest.slice(0, 10) : null;
}

export interface QueuedItem {
  title: string;
  note?: string;
  celex?: string | null;
}

/** sources/queued.json — what is known to be coming and not yet read. */
export function getQueued(): QueuedItem[] {
  return readJson<QueuedItem[]>(path.join(SOURCES_DIR, "queued.json")) ?? [];
}

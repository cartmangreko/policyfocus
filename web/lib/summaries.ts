import fs from "node:fs";
import path from "node:path";
import type { SectorSlug } from "./types";

// The summary objects — data/summaries/, one JSON per node, written and
// verified by sources/build_summaries.py. The build's prebuild step runs that
// script with --check, so a summary on disk that disagrees with the register
// rows it summarizes fails the build before anything here reads it.
//
// This module READS; it never derives. Nothing in the front end recomputes a
// burden count or a channel split — a page that needs one renders the checked
// object, which is how every surface stays consistent by construction.
// Weight is deliberately absent from these objects; it stays on the rows.
const SUMMARIES_DIR = path.join(process.cwd(), "..", "data", "summaries");

export interface SummaryCuts {
  measures: number;
  /** Prohibition rows count as burden; Neutral rows are the `unchanged`
   *  count, excluded from burden and benefit alike. */
  direction: { burden: number; benefit: number; unchanged: number };
  status: { adopted: number; proposed: number; mixed: number };
  channel: {
    direct: number;
    reached: number;
    /** Rows linked to no sector at all (omnibus). Zero on sector nodes. */
    no_sector: number;
    reached_by_channel: {
      supply_chain: number;
      procurement: number;
      regulatory_dependency: number;
    };
  };
}

export interface SectorSummary extends SummaryCuts {
  node: string;
  label: string;
}

export interface ActSummary extends SummaryCuts {
  node: string;
  sectors: { named: number; total_reach: number };
}

export interface SiteSummary extends SummaryCuts {
  node: "site";
  files: number;
  sectors: { named: number; total_reach: number };
}

const cache = new Map<string, unknown>();

function read<T>(rel: string): T {
  const hit = cache.get(rel);
  if (hit !== undefined) return hit as T;
  const doc = JSON.parse(
    fs.readFileSync(path.join(SUMMARIES_DIR, rel), "utf-8")
  ) as T;
  cache.set(rel, doc);
  return doc;
}

export function getSectorSummary(slug: SectorSlug): SectorSummary {
  return read<SectorSummary>(path.join("sector", `${slug.replace(/\//g, "__")}.json`));
}

export function getActSummary(file: string): ActSummary {
  return read<ActSummary>(path.join("act", `${file}.json`));
}

export function getSiteSummary(): SiteSummary {
  return read<SiteSummary>("site.json");
}

import fs from "node:fs";
import path from "node:path";
import type { Exposure, SectorSlug } from "./types";

// Supply-chain and country exposure, read from data/exposure/<slug>.json.
// Separate concern from the measures register: separate files, separate
// component, no shared logic. Shares arrive final — nothing here rescales,
// re-sorts or recomputes them.
//
// Server-only: the Exposure/ExposureView/ExposureRow shapes live in types.ts
// so the client panel can import them without dragging fs into the bundle.
const EXPOSURE_DIR = path.join(process.cwd(), "..", "data", "exposure");

export interface ExposureManifestEntry {
  code: string;
  eu_import_dependency_pct: number;
}

let cachedManifest: Record<string, ExposureManifestEntry> | null = null;

export function getExposureManifest(): Record<string, ExposureManifestEntry> {
  if (cachedManifest) return cachedManifest;
  const filePath = path.join(EXPOSURE_DIR, "_manifest.json");
  cachedManifest = fs.existsSync(filePath)
    ? (JSON.parse(fs.readFileSync(filePath, "utf-8")) as Record<string, ExposureManifestEntry>)
    : {};
  return cachedManifest;
}

const cache = new Map<string, Exposure | null>();

// Build-time only, like getAllMeasures. Sectors without a file (batsol, clean,
// ccs, and anything else outside the FIGARO mapping) return null and the panel
// is omitted — absence is expected, not an error.
export function getExposure(slug: SectorSlug | string): Exposure | null {
  const cached = cache.get(slug);
  if (cached !== undefined) return cached;

  // Only slugs the manifest knows about are read, so the slug never reaches
  // the filesystem as an arbitrary path segment.
  const known = slug in getExposureManifest();
  const filePath = path.join(EXPOSURE_DIR, `${slug}.json`);
  const exposure =
    known && fs.existsSync(filePath)
      ? (JSON.parse(fs.readFileSync(filePath, "utf-8")) as Exposure)
      : null;

  cache.set(slug, exposure);
  return exposure;
}

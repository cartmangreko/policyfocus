import fs from "node:fs";
import path from "node:path";
import type { MapDoc } from "@/components/LocationMap";

// The built geography, read the same way every other built file on this layer
// is read: from disk, at build time, with no derivation. sources/build_maps.py
// owns the projection, the frames and every coordinate in these files; this
// module finds one and hands it over.
//
// A MISSING FILE IS NOT AN EMPTY MAP. It returns undefined and the caller draws
// nothing, because the alternative — a frame with a coastline and no marks — is
// a picture asserting that a sector has no plants in Europe.

const DIR = path.join(process.cwd(), "..", "data", "transition", "maps");

function read(id: string): MapDoc | undefined {
  const file = path.join(DIR, `${id}.json`);
  if (!fs.existsSync(file)) return undefined;
  return JSON.parse(fs.readFileSync(file, "utf8")) as MapDoc;
}

/** The regional crop for one project. */
export function getProjectMap(id: string): MapDoc | undefined {
  return read(`project-${id}`);
}

/** The Europe-wide overview for one sector. The slug is flattened the same way
 *  the diagram files flatten it, so `chem/plastics` is one filename and not a
 *  directory nobody meant to create. */
export function getSectorMap(slug: string): MapDoc | undefined {
  return read(`sector-${slug.replace(/\//g, "__")}`);
}

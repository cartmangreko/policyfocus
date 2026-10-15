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

/** One country's frame within one sector — brief 16 §3. The slug is flattened
 *  the same way the overview's is, so the file name is a file name and not a
 *  directory nobody meant to create. Undefined where that country holds no
 *  drawn site, which is also how the route decides the page does not exist. */
export function getCountryMap(slug: string, iso: string): MapDoc | undefined {
  return read(`sector-${slug.replace(/\//g, "__")}-${iso}`);
}

/** Every (sector, country) pair that has a frame, read off the built files
 *  rather than recomputed from the rows.
 *
 *  THE BUILT FILES ARE THE AUTHORITY on which country views exist, and that is
 *  the same discipline every other route on this layer follows: the geometry is
 *  computed once in Python, and a second answer derived in TypeScript is a
 *  second answer. A page enumerated here with no frame behind it would be a
 *  route that renders nothing; a frame with no route would be a file nothing
 *  reads, and sources/check_map_clusters.py fails the build on either. */
export function countryFrames(): { sector: string; iso: string }[] {
  if (!fs.existsSync(DIR)) return [];
  const out: { sector: string; iso: string }[] = [];
  for (const name of fs.readdirSync(DIR).sort()) {
    const m = name.match(/^sector-(.+)-([A-Z]{2})\.json$/);
    if (!m) continue;
    out.push({ sector: m[1].replace(/__/g, "/"), iso: m[2] });
  }
  return out;
}

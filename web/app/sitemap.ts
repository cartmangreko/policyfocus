import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/routes";
import { siteRoutes } from "@/lib/siteRoutes";

// The indexable routes and nothing else — the positive half of the same
// classification robots.txt writes the negative half of (lib/routes.ts).
//
// SERVED IN BOTH STATES, on purpose. Pre-launch robots.txt disallows the whole
// site and no crawler asks for this file; what it is for then is that the list
// is inspectable before the switch is thrown, which is the only moment anybody
// can still find it wrong.
//
// NO lastModified, NO priority, NO changeFrequency. The first would be a date
// this build cannot source — a page changes when its data changes, and the data
// dates are on the figures themselves — and the other two are hints Google has
// said for years it ignores. A sitemap here is a list of what exists.
export default function sitemap(): MetadataRoute.Sitemap {
  return siteRoutes().indexable.map((path) => ({
    url: `${SITE_URL}${path === "/" ? "" : path}`,
  }));
}

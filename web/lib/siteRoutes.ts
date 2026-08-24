import { getSectorSlugs } from "./data";
import { getProjects, hasMap } from "./transition";
import { classify } from "./routes";

// The route policy in lib/routes.ts, applied to the data. Read by app/robots.ts
// and app/sitemap.ts, so the disallow list and the URL set are two renderings
// of one classification rather than two lists that have to be kept in step.
//
// A sector page is indexable when it renders the product template, which is
// `hasMap` — the same condition app/sectors/[...slug]/page.tsx branches on to
// decide which template to render. One condition, three consumers: the page
// chooses its template, the page states its own robots, and this decides
// whether the URL is published.
export function siteRoutes(): { indexable: string[]; demoted: string[] } {
  const slugs = getSectorSlugs();
  return classify({
    mappedSectors: slugs.filter((s) => hasMap(s)),
    unmappedSectors: slugs.filter((s) => !hasMap(s)),
    projectIds: getProjects().map((p) => p.id),
  });
}

/** Whether a sector's own page is indexable. The sector route reads this for
 *  its `robots` metadata, so the page and the sitemap answer from one
 *  function rather than from two readings of the same condition. */
export function sectorIsIndexable(slug: string): boolean {
  return hasMap(slug);
}

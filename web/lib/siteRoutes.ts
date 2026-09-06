import { getAllMeasures, getSectorSlugs } from "./data";
import { measurePathsWithLead } from "./objectLeads";
import { drawHold, getProjects, hasMap } from "./transition";
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
  const withLead = new Set(measurePathsWithLead());
  const allMeasures = getAllMeasures().map(
    (m) => `/measures/${m.file}/${m.id.toLowerCase()}`,
  );
  return classify({
    mappedSectors: slugs.filter((s) => sectorIsIndexable(s)),
    unmappedSectors: slugs.filter((s) => !sectorIsIndexable(s)),
    projectIds: getProjects().map((p) => p.id),
    measuresWithLead: allMeasures.filter((p) => withLead.has(p)),
    measuresWithoutLead: allMeasures.filter((p) => !withLead.has(p)),
  });
}

/** Whether a sector's own page is indexable. The sector route reads this for
 *  its `robots` metadata, so the page and the sitemap answer from one function
 *  rather than from two readings of the same condition.
 *
 *  TWO CONDITIONS, AND THEY ASK DIFFERENT THINGS. `hasMap` asks whether the
 *  product template has data to draw, which is what decides WHICH PAGE the
 *  route renders. A draw hold asks whether that page may be published, which is
 *  a judgement about whether the data is honest enough to put in front of a
 *  reader — and it is the only thing the hold does now. A held sector renders
 *  its product page, is built and gated like any other, carries `noindex` in
 *  its head and stays out of the sitemap until somebody lifts the hold. */
export function sectorIsIndexable(slug: string): boolean {
  return hasMap(slug) && !drawHold(slug);
}

import { getAllMeasures, getSectorSlugs } from "./data";
import { countryFrames } from "./maps";
import { getProjectLead, measurePathsWithLead } from "./objectLeads";
import { drawHold, getProjects, hasMap, projectPageHold } from "./transition";
import { classify } from "./routes";
import { SPOKE_IDS } from "./spokes";

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
    projectIds: getProjects().filter((p) => projectIsIndexable(p.id)).map((p) => p.id),
    heldProjectIds: getProjects().filter((p) => !projectIsIndexable(p.id)).map((p) => p.id),
    measuresWithLead: allMeasures.filter((p) => withLead.has(p)),
    measuresWithoutLead: allMeasures.filter((p) => !withLead.has(p)),
    // A sector serves its spokes when it renders the product template, which
    // is `hasMap` — the same condition the route branches on and the same one
    // generateStaticParams enumerates from. A held sector's spokes are demoted
    // for the same reason its hub is, and by the same list.
    spokeRoutes: slugs
      .filter((s) => hasMap(s))
      .flatMap((s) => SPOKE_IDS.map((spoke) => `/sectors/${s}/${spoke}`)),
    // THE COUNTRY VIEWS, from the built frames — the same enumeration the route
    // itself uses for generateStaticParams, so the sitemap cannot publish a URL
    // the build did not write and cannot miss one it did.
    countryRoutes: countryFrames()
      .filter(({ sector, iso }) => countryIsIndexable(sector, iso))
      .map(({ sector, iso }) => `/sectors/${sector}/projects/${iso}`),
    heldCountryRoutes: countryFrames()
      .filter(({ sector, iso }) => !countryIsIndexable(sector, iso))
      .map(({ sector, iso }) => `/sectors/${sector}/projects/${iso}`),
  });
}

/** Whether one country view is indexable.
 *
 *  IT FOLLOWS ITS SECTOR'S HUB AND NOTHING ELSE. A country view is a cut of the
 *  hub's picture — the same frame, fitted to one country — so publishing it
 *  while the hub is withheld would be offering a stranger through search exactly
 *  the picture a draw hold says is not honest enough to publish, one country at
 *  a time. CO2 transport and storage is the live case: its hub is held on 3 of
 *  44 rows drawn, and three country views drawn on one site each are the same
 *  judgement three times over.
 *
 *  IT DOES NOT ASK THE PROJECT-PAGE HOLD. That is a judgement about offering one
 *  indexable page per project, and a country view is one page per country: the
 *  two holds answer different questions and a country view is the hub's
 *  question. The ccs case happens to be held both ways, which is why the
 *  distinction is written down rather than discovered later. */
export function countryIsIndexable(sector: string, _iso: string): boolean {
  return sectorIsIndexable(sector);
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

/** Whether a project's own page is indexable. TWO CONDITIONS, and they ask
 *  different things.
 *
 *  1  ITS SECTOR'S PROJECT PAGES MUST HAVE BEEN RELEASED — the narrower of the
 *     two holds in draw_holds.json. A judgement about publication.
 *
 *  2  AND THE PAGE MUST RENDER A LEAD BLOCK, which is §0.8 itself and was
 *     missing from this function until 12 October 2026. The measure pages have
 *     applied it since they were built — 474 of 509 are indexable and the 35
 *     whose lead could not be built are demoted — and the project pages did not,
 *     so one row of 205 was published with no lead block in its head. HGHH
 *     Moorburg is that row: its lead fails the fact gate in
 *     sources/build_object_leads.py, which returns None precisely so that "a
 *     lead block that cannot be trusted takes the page down with it rather than
 *     rendering anyway", and then nothing took the page down.
 *
 *  THE RULE WAS ALREADY WRITTEN IN THE FILE THAT BUILDS THE LEADS. web/lib/
 *  objectLeads.ts says it in its own header: "An absent lead is a decision.
 *  §0.8 makes indexability follow the lead block, so a measure with no entry
 *  here is a measure whose page is demoted and absent from the sitemap". It said
 *  measure because measures were the kind that implemented it.
 *
 *  The route reads this for its robots metadata and siteRoutes reads it for the
 *  sitemap, so the page and the URL set answer from one function. */
export function projectIsIndexable(id: string): boolean {
  const p = getProjects().find((x) => x.id === id);
  return !!p && !projectPageHold(p.sector) && getProjectLead(id) !== null;
}

// WHICH ROUTES ARE THE PRODUCT — the policy, with no data in it.
//
// §0.8 of the page specifications says indexability follows the lead block, and
// names web/lib/launch.ts as the file that implements it. launch.ts owns the
// SWITCH — whether anything is indexable at all. This file owns the ROUTE
// CLASSES: which kinds of page are the product and which are the evidence
// behind it. lib/siteRoutes.ts applies it to the data, because whether a sector
// page is indexable is a question about whether that sector has been built, not
// a fact about its slug.
//
// It is split that way so this half can be run by `node --test` without a
// bundler — lib/launch.test.mts is the gate that the three noindex signals key
// off the switch alone, that a demoted page says `follow` and never `nofollow`
// once launched, and that no route is both indexed and disallowed.
//
// THE RULE, APPLIED
// -----------------
//   indexable  /                    the front page
//              /sectors             the six
//              /coverage            what is covered and what is not — the page
//                                   that states the perimeter (brief 4 §1),
//                                   which is why it is no longer a thin list
//              /sectors/<slug>      where the sector renders the product
//                                   template, i.e. where it has a lead block
//              /projects/<id>       object pages; lead blocks outstanding
//
//   demoted    /measures, /measures/<act>/<id>   until the measure lead blocks
//                                                land (§5, pre-launch item)
//              /sectors/<slug>      where the sector still renders the
//                                   directory template and has no lead block
//              /acts, /acts/<file>  near-duplicates of EUR-Lex
//              /changes, /changes/<id>            dated diffs
//              /findings, /findings/<id>          single computed statements
//
// A sector arrives in the index by having its data built. Nothing here is
// edited on the day steel lands.

/** The canonical origin. The sitemap's URLs and the Sitemap: line in robots.txt
 *  both have to be absolute, and neither is rendered from a request, so there
 *  is nothing to infer it from. */
export const SITE_URL = "https://www.eufabric.eu";

/** Route trees demoted whole. Prefixes rather than paths: every page under one
 *  of these is demoted for the reason its index page is, so the prefix is the
 *  honest statement and an enumeration would be 480 lines of the same fact. */
export const DEMOTED_PREFIXES = ["/acts", "/changes", "/findings", "/measures"];

/** The two lists, from the sector and project ids the caller has read. */
export function classify(input: {
  mappedSectors: string[];
  unmappedSectors: string[];
  projectIds: string[];
}): { indexable: string[]; demoted: string[] } {
  return {
    indexable: [
      "/",
      "/sectors",
      ...input.mappedSectors.map((s) => `/sectors/${s}`),
      ...input.projectIds.map((id) => `/projects/${id}`),
      "/coverage",
    ],
    demoted: [
      ...DEMOTED_PREFIXES,
      ...input.unmappedSectors.map((s) => `/sectors/${s}`),
    ],
  };
}

/** Whether a path falls under any demoted route. Prefix matching on segment
 *  boundaries: "/measures" covers "/measures/cbam/FIN-03" and must not cover a
 *  future "/measurements". */
export function isDemoted(path: string, demoted: string[]): boolean {
  return demoted.some((p) => path === p || path.startsWith(`${p}/`));
}

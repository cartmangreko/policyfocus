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
//              /measures/<act>/<id> where the measure renders a lead block
//              /sectors             the six
//              /coverage            what is covered and what is not — the page
//                                   that states the perimeter (brief 4 §1),
//                                   which is why it is no longer a thin list
//              /sectors/<slug>      where the sector renders the product
//                                   template, i.e. where it has a lead block
//              /projects/<id>       object pages; lead blocks outstanding
//
//   demoted    /measures            the browse surface, a thin list page
//              /measures/<act>/<id> where its lead block could not be built
//              /under-construction/<id>           the holding page a tile opens
//                                                where its industry is not built
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
 *  honest statement and an enumeration would be 480 lines of the same fact.
 *
 *  THIS LIST NO LONGER DRIVES robots.txt — see `robotsRules` below. It is the
 *  classification the pages themselves implement with `DEMOTED`, and what the
 *  sitemap is checked against. */
export const DEMOTED_PREFIXES = [
  "/acts",
  "/changes",
  "/findings",
  "/under-construction",
];

/** The measure browse page, demoted as a thin list — and NOT a prefix, which is
 *  the difference this constant exists to hold. Measure object pages under it
 *  are classified one at a time, by whether they render a lead block (§0.8),
 *  so "/measures" could not stay in the list above without taking 445 pages
 *  down with it. */
export const MEASURE_BROWSE = "/measures";

/** The two lists, from the sector and project ids the caller has read. */
export function classify(input: {
  mappedSectors: string[];
  unmappedSectors: string[];
  projectIds: string[];
  /** Measure pages that render a lead block, and those that do not. Both come
   *  from the same store — data/lead/measures.json — so a page's own robots tag
   *  and its presence in the sitemap are two readings of one file. */
  measuresWithLead?: string[];
  measuresWithoutLead?: string[];
}): { indexable: string[]; demoted: string[] } {
  return {
    indexable: [
      "/",
      "/sectors",
      ...input.mappedSectors.map((s) => `/sectors/${s}`),
      ...input.projectIds.map((id) => `/projects/${id}`),
      ...(input.measuresWithLead ?? []),
      "/coverage",
    ],
    demoted: [
      ...DEMOTED_PREFIXES,
      MEASURE_BROWSE,
      ...input.unmappedSectors.map((s) => `/sectors/${s}`),
      ...(input.measuresWithoutLead ?? []),
    ],
  };
}

/** robots.txt, as a rule object, in each of the two states.
 *
 *  LAUNCHED, IT ALLOWS EVERYTHING. The disallow list this used to carry —
 *  every demoted route — has been removed, and the reason is that the two
 *  mechanisms were working against each other. A disallowed page is never
 *  fetched, so the `noindex, follow` in its head is never read: robots.txt was
 *  keeping the crawler out of exactly the pages whose tag exists to let it walk
 *  through them. Now the tag is the only closure for a demoted route, which is
 *  what it was designed to be — noindex keeps the page out of the index, follow
 *  carries the crawler on to the indexable pages it links.
 *
 *  PRE-LAUNCH the switch dominates and nothing is allowed. */
export function robotsRules(indexable: boolean): {
  userAgent: string;
  allow?: string;
  disallow?: string;
} {
  return indexable
    ? { userAgent: "*", allow: "/" }
    : { userAgent: "*", disallow: "/" };
}

/** Routes that are demoted THEMSELVES and do not demote what is under them.
 *  One entry, and it is the whole reason this distinction exists: /measures is
 *  a thin list page, and the measure pages beneath it are classified one at a
 *  time by whether they render a lead block. Prefix-matching it would take 445
 *  indexable pages down with the list page above them. */
export const EXACT_ONLY = [MEASURE_BROWSE];

/** Whether a path falls under any demoted route. Prefix matching on segment
 *  boundaries — "/acts" covers "/acts/cbam" and must not cover a future
 *  "/actsomething" — except for the exact-only routes above. */
export function isDemoted(path: string, demoted: string[]): boolean {
  return demoted.some(
    (p) => path === p || (!EXACT_ONLY.includes(p) && path.startsWith(`${p}/`)),
  );
}

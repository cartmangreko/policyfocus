import type { MetadataRoute } from "next";
import { INDEXABLE } from "@/lib/launch";
import { SITE_URL } from "@/lib/routes";
import { siteRoutes } from "@/lib/siteRoutes";

// One of the three noindex signals, all keyed off SITE_LAUNCHED alone: this
// file, the X-Robots-Tag header in next.config.ts, and the robots metadata in
// app/layout.tsx. See lib/launch.ts for the switch and lib/routes.ts for which
// routes are the product.
//
// PRE-LAUNCH the switch dominates and nothing else is said: `Disallow: /` is
// the whole file, and adding a sitemap or a per-route rule underneath it would
// be describing a site that is closed.
//
// LAUNCHED it allows everything and disallows the demoted routes, per the
// index-opening brief.
//
// ONE CONSEQUENCE, STATED WHERE THE DECISION IS. A disallowed page is not
// fetched, so the crawler never reads the `noindex, follow` in its head: the
// disallow is what keeps it out, and the `follow` that was meant to carry a
// crawler through a demoted list page to the objects under it does not get the
// chance. Every path disallowed here is demoted anyway and every object under
// it is reachable from an indexable page, so nothing is orphaned — but the two
// mechanisms are not additive, and a reader of this file should not have to
// work that out.
export default function robots(): MetadataRoute.Robots {
  if (!INDEXABLE) {
    return { rules: { userAgent: "*", disallow: "/" } };
  }
  return {
    rules: { userAgent: "*", allow: "/", disallow: siteRoutes().demoted },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}

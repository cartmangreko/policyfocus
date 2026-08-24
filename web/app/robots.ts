import type { MetadataRoute } from "next";
import { INDEXABLE } from "@/lib/launch";
import { SITE_URL, robotsRules } from "@/lib/routes";

// One of the three noindex signals, all keyed off SITE_LAUNCHED alone: this
// file, the X-Robots-Tag header in next.config.ts, and the robots metadata in
// app/layout.tsx. See lib/launch.ts for the switch and lib/routes.ts for which
// routes are the product and for the rule this renders.
//
// PRE-LAUNCH the switch dominates and nothing else is said: `Disallow: /` is
// the whole file, and adding a sitemap or a per-route rule underneath it would
// be describing a site that is closed.
//
// LAUNCHED IT ALLOWS EVERYTHING, including the demoted routes. Their closure is
// the `noindex, follow` in their own heads, which is the only one that can be
// read by a crawler that is allowed to fetch them — and `follow` is the point:
// a demoted list page exists so the crawler can walk through it to the object
// pages it links. Disallowing it would have kept the crawler out of the page
// whose tag was inviting it through.
export default function robots(): MetadataRoute.Robots {
  return {
    rules: robotsRules(INDEXABLE),
    ...(INDEXABLE ? { sitemap: `${SITE_URL}/sitemap.xml` } : {}),
  };
}

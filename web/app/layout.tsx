import type { Metadata } from "next";
import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";
import { SITE_ROBOTS } from "@/lib/launch";
import { SITE_URL } from "@/lib/routes";
import { datasetJsonLd } from "@/lib/schema";
import { getMasthead } from "@/lib/sitetext";
import "./globals.css";

// NO WEBFONTS (brief 3). Archivo, Public Sans and IBM Plex Mono were three
// Google families — sixty-odd kilobytes and a flash of fallback text on every
// cold load — to say in a borrowed face what the identity is drawn in. The
// stack is Helvetica where it is installed, Arial and Liberation Sans behind
// it, and the hierarchy is carried by weight and tracking instead. See the
// type block in globals.css.

export const metadata: Metadata = {
  // THE ORIGIN EVERY ABSOLUTE URL IN THIS SITE'S METADATA RESOLVES ON, from the
  // one constant the sitemap and robots.txt are built from. Set 15 October 2026
  // with the move to www: Next resolves a relative metadata URL against this,
  // so without it an OpenGraph or canonical URL would be relative in the markup
  // and absolute-on-whatever-host wherever a consumer resolved it — which is
  // the one thing a canonical host is for.
  //
  // NO PER-PAGE CANONICAL TAG IS EMITTED TODAY, and this is not that. A
  // canonical tag is a claim that a page has one address, and the pages here
  // have exactly one each; what this fixes is which HOST the absolute URLs Next
  // does generate are built on. If canonicals are added later they resolve here
  // and need no second constant.
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Eufabric — Intelligence on what Europe builds next",
    template: "%s · Eufabric",
  },
  // The George-approved pair doubles as the default description, so the
  // fallback tag carries no claim the reviewed prose does not.
  description: `${getMasthead().descriptor} ${getMasthead().positioning}`,
  // The same launch switch as the X-Robots-Tag header and robots.txt, in the
  // head of every page: a saved or proxied copy of this HTML carries the
  // instruction even when the header does not travel with it.
  robots: SITE_ROBOTS,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        {/* schema.org Dataset markup, site-wide: the register described as
            the dataset it is. Computed from the site summary object — see
            lib/schema.ts for the documented type choices. */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: datasetJsonLd() }}
        />
        <div className="brand-rule" />
        {/* The register ticker is gone from the chrome. It scrolled measure
            text across the top of every page — the register advertising
            itself, above a product whose first job is to say what a sector is
            under. components/Ticker.tsx is kept: the strip is good, and it
            belongs to a register surface rather than to the site frame. */}
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}

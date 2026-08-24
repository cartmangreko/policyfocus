import type { Metadata } from "next";
import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";
import { SITE_ROBOTS } from "@/lib/launch";
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

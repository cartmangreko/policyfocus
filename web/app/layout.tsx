import type { Metadata } from "next";
import { Archivo, IBM_Plex_Mono, Public_Sans } from "next/font/google";
import SiteFooter from "@/components/SiteFooter";
import SiteHeader from "@/components/SiteHeader";
import { INDEXABLE } from "@/lib/launch";
import { datasetJsonLd } from "@/lib/schema";
import { getMasthead } from "@/lib/sitetext";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin"],
  weight: ["600", "700", "800", "900"],
  variable: "--font-display",
  display: "swap",
});
const publicSans = Public_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-sans",
  display: "swap",
});
const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "PolicyFocus — European policy, decoded into economic impact",
    template: "%s · PolicyFocus",
  },
  // The George-approved masthead pair doubles as the default description, so
  // the fallback tag carries no claim the reviewed prose does not.
  description: `${getMasthead().tagline} ${getMasthead().subline}`,
  // The same launch switch as the X-Robots-Tag header and robots.txt, in the
  // head of every page: a saved or proxied copy of this HTML carries the
  // instruction even when the header does not travel with it.
  robots: INDEXABLE ? undefined : { index: false, follow: false },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${archivo.variable} ${publicSans.variable} ${plexMono.variable}`}
    >
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

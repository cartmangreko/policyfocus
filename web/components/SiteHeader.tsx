import Link from "next/link";
import Wordmark from "./Wordmark";

import { PRIORITIES } from "@/lib/priorities";
import { ANALYSIS } from "@/lib/analysis";

// The home page leads with findings now, and the register sits behind the
// doors block, so the nav points at what exists rather than at the anchors the
// old home page carried.
const NAV = [
  { label: "Findings", href: "/findings" },
  { label: "Topics", href: `/priorities/${PRIORITIES[0].slug}` },
  { label: "Sectors", href: "/#doors" },
  { label: "Measures", href: "/#doors" },
  { label: "Analysis", href: `/analysis/${ANALYSIS[0].slug}` },
  { label: "Coverage", href: "/coverage" },
];

export default function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Wordmark />
        <nav className="site-nav">
          {NAV.map((n) => (
            <Link key={n.label} href={n.href}>
              {n.label}
            </Link>
          ))}
        </nav>
        <div className="site-header-actions">
          <Link href="/#search" className="header-search">
            <span className="header-search-glyph">⌕</span>
            <span>Search</span>
            <span className="keycap">/</span>
          </Link>
          <span className="signin">Sign in</span>
        </div>
      </div>
    </header>
  );
}

import Link from "next/link";
import Wordmark from "./Wordmark";

import { PRIORITIES } from "@/lib/priorities";
import { ANALYSIS } from "@/lib/analysis";

const NAV = [
  { label: "Topics", href: `/priorities/${PRIORITIES[0].slug}` },
  { label: "Measures", href: "/#signals" },
  { label: "Sectors", href: "/#sectors" },
  { label: "Companies", href: "/#sectors" },
  { label: "Analysis", href: `/analysis/${ANALYSIS[0].slug}` },
  { label: "Data", href: "/#stats" },
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

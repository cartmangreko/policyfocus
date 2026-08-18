import Link from "next/link";
import SearchBar from "./SearchBar";
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
  { label: "Measures", href: "/measures" },
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
          {/* The search field itself now sits in the row below, on every page,
              so the link that used to stand in for it here is gone rather than
              pointing at the thing next to it. */}
          <span className="signin">Sign in</span>
        </div>
      </div>
      <div className="site-header-search">
        <div className="site-header-inner">
          <SearchBar />
        </div>
      </div>
    </header>
  );
}

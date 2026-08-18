import Link from "next/link";
import SearchBar from "./SearchBar";
import Wordmark from "./Wordmark";

// Four doors, each a directory page of its own: the two spines (sectors and
// legislation), the conclusions layer, and the methods page. The flat measure
// browse is deliberately NOT here — it anchors /measures and is reachable
// from /coverage and from search, but a register-wide list is a working view,
// not a front door.
const NAV = [
  { label: "Sectors", href: "/sectors" },
  { label: "Legislation", href: "/acts" },
  { label: "Findings", href: "/findings" },
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

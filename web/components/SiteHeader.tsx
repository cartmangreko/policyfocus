import Link from "next/link";
import SearchBar from "./SearchBar";
import Wordmark from "./Wordmark";

// ONE DOOR. The product is the sector page, and the header should not offer a
// reader four other things to be instead.
//
// The five links this replaced — the change feed, legislation, findings,
// coverage — were the register presenting itself as the product. Those routes
// still exist and still work; they are reachable from a measure page, from
// search, and from any link already in the wild, and they carry a noindex tag
// (lib/launch.ts, DEMOTED). Removing a nav link is not deleting a page, and
// this is the difference between the two.
const NAV = [{ label: "Sectors", href: "/sectors" }];

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

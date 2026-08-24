import Link from "next/link";
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

// TWO THINGS LEFT THIS HEADER (brief 4 §3), and both for the same reason: they
// were promises the platform does not keep yet.
//
//   Sign in    there is nothing to sign in to. No replacement control — an
//              account door that opens on nothing is worse than no door.
//   Search     the field was presentational, with three example chips and no
//              index behind it. It returns with the index, page
//              specifications §5 step 6; components/SearchBar.tsx is kept for
//              that, unrendered, rather than rewritten from nothing later.
//
// The lockup is now the only place on the site where the name is set, which is
// why it is set larger here and no longer repeated on the home page.
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
      </div>
    </header>
  );
}

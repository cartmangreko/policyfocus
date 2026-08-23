import Link from "next/link";
import Wordmark from "./Wordmark";
import { getMasthead } from "@/lib/sitetext";

// The footer is chrome, and chrome advertises. So it carries the product and
// the method, and no longer carries the register's own directories: the flat
// measure browse, the act pages and the findings were three of four links
// under "Product" while being, since the transition map, the evidence layer
// beneath it. Their routes are unchanged and they are still reachable — from
// any measure a sector page links, from search, from an existing bookmark.
//
// Coverage stays, under Method, because "what is covered and what is not" is
// the one register surface a reader of a sector page has a right to be
// pointed at.
const COLUMNS: { heading: string; links: { label: string; href: string }[] }[] = [
  {
    heading: "Product",
    links: [{ label: "Sectors", href: "/sectors" }],
  },
  {
    heading: "Method",
    links: [
      { label: "Coverage & limits", href: "/coverage" },
      { label: "Sources", href: "/coverage" },
    ],
  },
];

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="site-footer-grid">
          <div>
            <Wordmark tone="dark" size="sm" />
            {/* The same reviewed descriptor the home head carries, read from
                data/prose.json rather than written twice. The footer used to
                have a statement of its own, which is how a product ends up
                with two descriptions of itself that drift apart. */}
            <p className="footer-statement">{getMasthead().descriptor}</p>
          </div>
          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <div className="footer-heading">{col.heading}</div>
              <div className="footer-links">
                {col.links.map((l) => (
                  <Link key={l.label} href={l.href}>
                    {l.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="footer-colophon">
          Prototype. Every count is computed from the source legislation, not entered by hand.
        </div>
      </div>
    </footer>
  );
}

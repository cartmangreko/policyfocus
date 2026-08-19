import Link from "next/link";
import Wordmark from "./Wordmark";

const COLUMNS: { heading: string; links: { label: string; href: string }[] }[] = [
  {
    heading: "Product",
    links: [
      { label: "Measures", href: "/measures" },
      { label: "Sectors", href: "/sectors" },
      { label: "Acts", href: "/acts" },
      { label: "Findings", href: "/findings" },
    ],
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
            <Wordmark tone="dark" />
            <p className="footer-statement">
              The intelligence layer between European policy and the real economy.
            </p>
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

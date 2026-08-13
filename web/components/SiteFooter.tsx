import Link from "next/link";
import Wordmark from "./Wordmark";
import { ANALYSIS } from "@/lib/analysis";
import { PRIORITIES } from "@/lib/priorities";

const COLUMNS: { heading: string; links: { label: string; href: string }[] }[] = [
  {
    heading: "Product",
    links: [
      { label: "Topics", href: `/priorities/${PRIORITIES[0].slug}` },
      { label: "Measures", href: "/#signals" },
      { label: "Sectors", href: "/#sectors" },
      { label: "Companies", href: "/#sectors" },
    ],
  },
  {
    heading: "Method",
    links: [
      { label: "How it works", href: "/#stats" },
      { label: "Sources", href: "/#signals" },
      { label: "Coverage & limits", href: "/#stats" },
    ],
  },
  {
    heading: "About",
    links: [
      { label: "Analysis", href: `/analysis/${ANALYSIS[0].slug}` },
      { label: "Data & API", href: "/#stats" },
      { label: "Contact", href: "/#stats" },
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
          Prototype. All counts computed from the register, not entered by hand.
        </div>
      </div>
    </footer>
  );
}

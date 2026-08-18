import type { Metadata } from "next";
import Link from "next/link";
import FindingCard from "@/components/FindingCard";
import { getAllFindings } from "@/lib/findings";

export const metadata: Metadata = {
  title: "Findings",
  description:
    "What the tracked measures mean, sector by sector. Every finding carries the measures it rests on.",
};

export default function FindingsIndexPage() {
  const findings = getAllFindings();

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/" className="backlink">
              ← Home
            </Link>
            <span className="crumb">Findings</span>
          </div>
          <h1 className="sector-title">Findings</h1>
          <p className="sector-intro">
            Short claims about what the tracked measures mean for a sector. Each one resolves
            against the register: the measures it cites, and any exposure figure it prints, are
            checked at build time before the finding can be published.
          </p>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          {findings.length === 0 ? (
            <p className="section-note">No findings published yet.</p>
          ) : (
            <div className="finding-grid">
              {findings.map((f) => (
                <FindingCard key={f.id} finding={f} />
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

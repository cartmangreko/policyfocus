import type { Metadata } from "next";
import Link from "next/link";
import FindingCard from "@/components/FindingCard";
import { getAllFindings } from "@/lib/findings";

export function generateMetadata(): Metadata {
  const findings = getAllFindings();
  return {
    title: "Findings",
    description: `${findings.length} findings — plain claims about the tracked measures, every number checked against the underlying data before publication.`,
  };
}

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
            Short claims about what the tracked measures mean for a sector. Every measure a
            finding cites, and every figure it prints, is checked against the underlying data
            before the finding can be published.
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

import type { Metadata } from "next";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import SummaryStrip from "@/components/SummaryStrip";
import { FILES } from "@/lib/data";
import { getActSummary, getSiteSummary } from "@/lib/summaries";

// The legislation directory — same grammar as /sectors: the site-wide summary
// strip, then each act as a sub-card carrying its own miniature strip. The
// act page below holds the reach strip and the grouped measures.
export const metadata: Metadata = {
  title: "Legislation",
  description:
    "The EU acts the platform decodes provision by provision, each with its burden/benefit, status and sector-reach summary.",
};

export default function ActsPage() {
  const site = getSiteSummary();

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <Crumbs trail={[{ label: "Home", href: "/" }, { label: "Legislation" }]} />
          <h1 className="sector-title">Legislation</h1>
          <p className="sector-intro">
            The platform decodes {site.files} EU acts provision by provision — {site.measures}{" "}
            measures in all, each one a requirement, a support measure or a right with its source
            sentence quoted verbatim. Every act below links to its own page: what it does, which
            sectors it names, and which it reaches without naming.
          </p>
          <SummaryStrip cuts={site} subject="the tracked corpus" />
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">Directory</p>
          <h2>Acts on the platform</h2>
          <div className="dir-cards">
            {Object.entries(FILES).map(([slug, meta]) => {
              const summary = getActSummary(slug);
              return (
                <div key={slug} className="dir-card">
                  <Link href={`/acts/${slug}`} className="dir-card-title">
                    {meta.name}
                  </Link>
                  <p className="dir-card-code">{meta.code}</p>
                  <SummaryStrip cuts={summary} variant="mini" />
                  <p className="summary-mini">
                    names {summary.sectors.named} sectors · reaches {summary.sectors.total_reach}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </main>
  );
}

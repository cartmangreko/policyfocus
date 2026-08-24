import type { Metadata } from "next";
import Crumbs from "@/components/Crumbs";
import SectorCard from "@/components/SectorCard";
import SummaryStrip from "@/components/SummaryStrip";
import { getSectorCounts, isChild } from "@/lib/data";
import { getPerimeterProse } from "@/lib/sitetext";
import { getSiteSummary } from "@/lib/summaries";

// The directory root — the same template as every level below it: summary
// strip, then children as sub-cards, each with a miniature strip of its own.
// At this depth the children are the parent sectors and there are no measure
// lists or panels; those belong to the sector the reader descends into.
export const metadata: Metadata = {
  title: "Sectors",
  description:
    "Every sector the platform covers, with the burden/benefit, status and channel summary for each — parents first, children nested under the parent that files them.",
};

export default function SectorsPage() {
  const site = getSiteSummary();
  const parents = getSectorCounts().filter((s) => !isChild(s.slug));

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <Crumbs trail={[{ label: "Home", href: "/" }, { label: "Sectors" }]} />
          <h1 className="sector-title">Sectors</h1>
          {/* The perimeter paragraph — reviewed prose from data/prose.json,
              its counts rendered from the gate-checked site summary. */}
          <p className="sector-intro">{getPerimeterProse()}</p>
          <p className="section-note">
            This is the full sector spine: {parents.length} parent sectors, with a child nested
            under a parent only where measures apply to the child and not to the parent.
          </p>
          <SummaryStrip cuts={site} subject="the tracked corpus" />
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">Directory</p>
          <h2>Every sector the corpus reaches</h2>
          <div className="dir-cards">
            {parents.map((s) => (
              <SectorCard key={s.slug} slug={s.slug} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

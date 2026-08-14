import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SectorExposure from "@/components/SectorExposure";
import SignalRow from "@/components/SignalRow";
import StatsStrip from "@/components/StatsStrip";
import {
  SECTORS,
  getMeasuresForSector,
  getRelatedSectors,
  getSectorSlugs,
  getSectorStats,
} from "@/lib/data";
import { getExposure } from "@/lib/exposure";
import { REACH_CHANNEL_LABEL, inferReachChannel } from "@/lib/reachChannel";
import type { Measure, SectorSlug } from "@/lib/types";

export function generateStaticParams() {
  return getSectorSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  if (!(slug in SECTORS)) return { title: "Sector not found" };
  const name = SECTORS[slug as SectorSlug];
  const stats = getSectorStats(slug as SectorSlug);
  return {
    title: `European ${name}`,
    description: `${stats.total} tracked EU measures reach ${name.toLowerCase()} — ${stats.added} adding a duty, ${stats.removed} removing one.`,
  };
}

// Pressure and support are read off the sector's own measures: pressure is the
// share of duties that add, support the share that remove or grant. Both are
// bounded 0-100 by construction, so the meters are honest, not decorative.
function meters(named: Measure[], reached: Measure[]) {
  const all = [...named, ...reached];
  if (!all.length) return { pressure: 0, support: 0 };
  const added = all.filter((m) => m.direction === "add").length;
  return {
    pressure: Math.round((added / all.length) * 100),
    support: Math.round(((all.length - added) / all.length) * 100),
  };
}

function band(pct: number): string {
  if (pct >= 70) return "Elevated";
  if (pct >= 40) return "Moderate";
  return "Low";
}

export default async function SectorPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (!(slug in SECTORS)) notFound();

  const sectorSlug = slug as SectorSlug;
  const name = SECTORS[sectorSlug];
  const { named, reached } = getMeasuresForSector(sectorSlug);
  const stats = getSectorStats(sectorSlug);
  const { pressure, support } = meters(named, reached);
  const relatedSectors = getRelatedSectors(sectorSlug);
  // Null for sectors outside the FIGARO mapping — the panel is then omitted.
  const exposure = getExposure(sectorSlug);

  // Channel mix for the reached-without-naming cohort.
  const channels = new Map<string, number>();
  for (const m of reached) {
    const c = REACH_CHANNEL_LABEL[inferReachChannel(m)];
    channels.set(c, (channels.get(c) ?? 0) + 1);
  }

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/" className="backlink">
              ← Home
            </Link>
            <span className="crumb">Sectors / {name}</span>
          </div>
          <h1 className="sector-title">European {name}</h1>
          <p className="sector-intro">
            How the tracked corpus reaches the sector — {stats.named} measures name it directly, and{" "}
            {reached.length} more reach it through supply-chain, procurement or
            regulatory-dependency channels.
          </p>
          <StatsStrip
            stats={[
              { value: String(stats.total), label: "Measures reaching sector" },
              { value: String(stats.added), label: "Added / burden", tone: "add" },
              { value: String(stats.removed), label: "Removed / relief", tone: "rem" },
              { value: String(stats.named), label: "Naming the sector" },
            ]}
          />
        </div>
      </section>

      <section className="detail-body">
        <div className="wrap meter-grid">
          <div className="card">
            <div className="meter-head">
              <span className="card-label">Regulatory pressure</span>
              <span className="meter-value is-neg">{band(pressure)}</span>
            </div>
            <div className="meter-track">
              <div className="meter-fill meter-fill-neg" style={{ width: `${pressure}%` }} />
            </div>
            <p className="card-note">
              {pressure}% of the measures reaching this sector add or widen a duty.
            </p>
          </div>
          <div className="card">
            <div className="meter-head">
              <span className="card-label">Policy support</span>
              <span className="meter-value is-pos">{band(support)}</span>
            </div>
            <div className="meter-track">
              <div className="meter-fill meter-fill-pos" style={{ width: `${support}%` }} />
            </div>
            <p className="card-note">
              {support}% remove, narrow or waive a duty, or grant a benefit.
            </p>
          </div>
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">Named in the text</p>
          <h2>Measures that address {name.toLowerCase()} directly</h2>
          {named.length === 0 ? (
            <p className="section-note">Nothing in the current corpus names this sector.</p>
          ) : (
            <div className="signals">
              {named.map((m, i) => (
                <SignalRow
                  key={`${m.file}-${m.id}`}
                  measure={m}
                  last={i === named.length - 1}
                />
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="band band-paper">
        <div className="wrap">
          <p className="eyebrow">Reaches you without naming you</p>
          <h2>Measures that land through a channel</h2>
          <p className="section-note">
            {[...channels.entries()].map(([c, n]) => `${c} ${n}`).join(" · ") ||
              "No indirect reach recorded."}
          </p>
          {reached.length > 0 && (
            <div className="signals">
              {reached.map((m, i) => (
                <SignalRow
                  key={`${m.file}-${m.id}`}
                  measure={m}
                  last={i === reached.length - 1}
                />
              ))}
            </div>
          )}
        </div>
      </section>

      {exposure && <SectorExposure exposure={exposure} sectorName={name} />}

      {relatedSectors.length > 0 && (
        <section className="band band-ruled">
          <div className="wrap">
            <p className="eyebrow">Related sectors</p>
            <h2>Most often caught by the same measure</h2>
            <div className="chips">
              {relatedSectors.map((s) => (
                <Link key={s.slug} href={`/sectors/${s.slug}`} className="chip">
                  {s.name}
                  <span className="chip-count">{s.count}</span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}

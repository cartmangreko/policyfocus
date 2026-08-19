import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Crumbs from "@/components/Crumbs";
import FindingCard from "@/components/FindingCard";
import NetPositionStrip from "@/components/NetPositionStrip";
import SectorCard from "@/components/SectorCard";
import SectorExposure from "@/components/SectorExposure";
import SignalRow from "@/components/SignalRow";
import SummaryStrip from "@/components/SummaryStrip";
import {
  SECTORS,
  getChildren,
  getMeasuresForSector,
  getParent,
  getRelatedSectors,
  getSectorSlugs,
  getSectorStats,
  splitNamed,
} from "@/lib/data";
import { getExposure } from "@/lib/exposure";
import { getSectorSummary } from "@/lib/summaries";
import { getFindingsForSector, withEvidence } from "@/lib/findings";
import { REACH_CHANNEL_LABEL, inferReachChannel } from "@/lib/reachChannel";
import type { Measure, SectorSlug } from "@/lib/types";

// A catch-all route, because a child sector's URL has two segments:
// /sectors/chem is the parent, /sectors/chem/plastics the child. The slug and
// the path are the same string — "chem/plastics" — so nothing has to translate
// between an id and a URL.
//
// Every depth renders the same directory template: summary strip, then
// children as sub-cards where they exist, then the measure lists, then the
// level-specific panels (net position, exposure) in their existing order.
// /sectors (the root) renders the same grammar one level up.

// Every path this route serves is enumerated below, so an unlisted one is a
// 404 rather than a render on demand. That is load-bearing on Vercel: the
// register JSON lives outside web/ and is read at build time only, so a
// function rendering an unknown slug would have nothing to read. See
// README.md, "Deploying".
export const dynamicParams = false;

export function generateStaticParams() {
  return getSectorSlugs().map((slug) => ({ slug: slug.split("/") }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<Metadata> {
  const slug = (await params).slug.join("/");
  if (!(slug in SECTORS)) return { title: "Sector not found" };
  const name = SECTORS[slug as SectorSlug];
  const stats = getSectorStats(slug as SectorSlug);
  return {
    title: `European ${name}`,
    description: `${stats.total} tracked EU measures reach ${name.toLowerCase()} — ${stats.added} adding a duty, ${stats.removed} removing one.`,
  };
}

function MeasureList({ rows }: { rows: Measure[] }) {
  return (
    <div className="signals">
      {rows.map((m, i) => (
        <SignalRow key={`${m.file}-${m.id}`} measure={m} last={i === rows.length - 1} />
      ))}
    </div>
  );
}

export default async function SectorPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const slug = (await params).slug.join("/");
  if (!(slug in SECTORS)) notFound();

  const sectorSlug = slug as SectorSlug;
  const name = SECTORS[sectorSlug];
  const parent = getParent(sectorSlug);
  const children = getChildren(sectorSlug);
  const { reached } = getMeasuresForSector(sectorSlug);
  const { whole, byChild } = splitNamed(sectorSlug);
  const stats = getSectorStats(sectorSlug);
  const relatedSectors = getRelatedSectors(sectorSlug);
  // Null for sectors outside the FIGARO mapping — the panel is then omitted.
  // A child never borrows its parent's panel; see lib/exposure.ts.
  const exposure = getExposure(sectorSlug);
  const findings = withEvidence(getFindingsForSector(sectorSlug));

  // Channel mix for the reached-without-naming cohort.
  const channels = new Map<string, number>();
  for (const m of reached) {
    const c = REACH_CHANNEL_LABEL[inferReachChannel(m)];
    channels.set(c, (channels.get(c) ?? 0) + 1);
  }

  const trail = [
    { label: "Home", href: "/" },
    { label: "Sectors", href: "/sectors" },
    ...(parent ? [{ label: SECTORS[parent], href: `/sectors/${parent}` }] : []),
    { label: name },
  ];

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <Crumbs trail={trail} />
          <h1 className="sector-title">European {name}</h1>
          <p className="sector-intro">
            How the tracked corpus reaches the sector — {stats.named} measures name it directly, and{" "}
            {reached.length} more reach it through supply-chain, procurement or
            regulatory-dependency channels.
          </p>
          {/* The gate-checked summary object for this node, rendered dumbly.
              Same three cuts as every other node on the site. */}
          <SummaryStrip cuts={getSectorSummary(sectorSlug)} />
        </div>
      </section>

      {children.length > 0 && (
        <section className="band band-tight" id="children">
          <div className="wrap">
            <p className="eyebrow">Within this sector</p>
            <h2>Child sectors with rules of their own</h2>
            <p className="section-note">
              A child exists only where measures apply to it and not to the parent; its rows roll up
              into this page, and this page&apos;s whole-sector measures do not roll down.
            </p>
            <div className="dir-cards">
              {children.map((c) => (
                <SectorCard key={c} slug={c} />
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="band band-ruled" id="measures">
        <div className="wrap">
          <p className="eyebrow">Named in the text</p>
          <h2>
            {children.length > 0
              ? "Measures applying to the sector as a whole"
              : `Measures that address ${name.toLowerCase()} directly`}
          </h2>
          {whole.length === 0 ? (
            <p className="section-note">Nothing in the current corpus names this sector.</p>
          ) : (
            <MeasureList rows={whole} />
          )}
          {byChild.map(({ child, rows }) => (
            <div key={child} className="named-child-group">
              <h3 className="named-child-head">
                Applying to <Link href={`/sectors/${child}`}>{SECTORS[child]}</Link> only —{" "}
                {rows.length} {rows.length === 1 ? "measure" : "measures"}, rolled up from the child
              </h3>
              <MeasureList rows={rows} />
            </div>
          ))}
        </div>
      </section>

      <section className="band band-paper" id="reached">
        <div className="wrap">
          <p className="eyebrow">Reaches you without naming you</p>
          <h2>Measures that land through a channel</h2>
          <p className="section-note">
            {[...channels.entries()].map(([c, n]) => `${c} ${n}`).join(" · ") ||
              "No indirect reach recorded."}
          </p>
          {reached.length > 0 && <MeasureList rows={reached} />}
        </div>
      </section>

      {findings.length > 0 && (
        <section className="band" id="findings">
          <div className="wrap">
            <div className="section-head">
              <div>
                <p className="eyebrow">Findings</p>
                <h2>What this means for {name.toLowerCase()}</h2>
              </div>
              <Link href="/findings" className="section-link">
                All findings →
              </Link>
            </div>
            <div className="finding-grid">
              {findings.map((f) => (
                <FindingCard key={f.id} finding={f} />
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="band band-tight" id="net-position">
        <div className="wrap">
          <p className="eyebrow">Net position</p>
          <h2>What the corpus does to this sector, in total</h2>
          {/* Computed from the register at build time: no stored totals, and
              the pressure/support meters this replaces are gone rather than
              kept alongside — two numbers for one fact is one too many. */}
          <NetPositionStrip slug={sectorSlug} />
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

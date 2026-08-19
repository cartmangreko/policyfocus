import type { Metadata } from "next";
import Link from "next/link";
import FindingCard from "@/components/FindingCard";
import SectorGrid from "@/components/SectorGrid";
import StatsStrip from "@/components/StatsStrip";
import Wordmark from "@/components/Wordmark";
import { FILES } from "@/lib/data";
import { getSiteSummary } from "@/lib/summaries";
import { getRecentlyAdded } from "@/lib/coverage";
import { BASIS_LABEL } from "@/lib/findings";
import { getRecentFindings, withEvidence } from "@/lib/findings";
import { getConnectionCount } from "@/lib/graphStats";
import { getCoverageLine, getMasthead } from "@/lib/sitetext";

// The home page leads with conclusions. Five blocks, in this order:
// wordmark, findings, recently added, doors, coverage line.
//
// Everything the old home page carried that is not one of those five was
// demoted, not deleted, and each piece now has an address: the signals feed
// and the burden ledger are /measures (reachable from /coverage and search),
// the driver chart is /coverage, and the search field is in the site header
// on every page. The priorities and analysis pages are gone: their editorial
// framing predated the arithmetic-only rule, and nothing else read their code.
//
// The masthead pair (tagline + subline) is George-approved final text, read
// from data/prose.json — reviewed prose stored as data, per sources/scope.md.


// The default title stays in the layout; the description is computed from
// the site summary so the tag moves with the register.
export function generateMetadata(): Metadata {
  const site = getSiteSummary();
  return {
    description: `${site.measures} measures decoded from ${site.files} EU acts, mapped to the ${site.sectors.total_reach} sectors they affect — every count computed from the source legislation.`,
  };
}

export default function Home() {
  const findings = withEvidence(getRecentFindings(5));
  const site = getSiteSummary();
  const latest = getRecentlyAdded(1)[0];
  const masthead = getMasthead();

  return (
    <main className="rise">
      <section className="home-head">
        <div className="wrap">
          <div className="home-wordmark">
            <Wordmark />
          </div>
          <p className="home-tagline">{masthead.tagline}</p>
          <p className="home-subline">{masthead.subline}</p>
          {/* The masthead statistic: exactly three figures. Measures and
              sectors come from the gate-checked site summary; connections is
              the graph's total edge count, guarded by build_graph.py --check
              in prebuild so it moves with every ingestion and can never go
              stale. Files-read and named/reached live on /coverage now. */}
          <Link href="/sectors" className="home-stats-link" aria-label="Browse sectors">
            <StatsStrip
              stats={[
                { value: site.measures.toLocaleString("en-US"), label: "Measures decoded" },
                {
                  value: getConnectionCount().toLocaleString("en-US"),
                  label: "Connections mapped",
                },
                { value: String(site.sectors.total_reach), label: "Sectors" },
              ]}
            />
          </Link>
        </div>
      </section>

      <section className="band" id="findings">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Findings</p>
              <h2>What the tracked measures mean</h2>
            </div>
            <Link href="/findings" className="section-link">
              All findings →
            </Link>
          </div>
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

      <section className="band band-paper" id="recent">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Recently added</p>
              <h2>Latest addition: {latest.title.split(" — ")[0]}</h2>
            </div>
            <Link href="/coverage" className="section-link">
              Full coverage →
            </Link>
          </div>
          {/* Derived from sources/manifest.json and the .fetch.json sidecars.
              This is when the DOCUMENT was fetched, not when anything in it
              changed — said plainly, because the two get confused. */}
          <p className="section-note">
            {latest.basis ? BASIS_LABEL[latest.basis] : "—"} · {latest.measures} measures · added{" "}
            {latest.lastUpdated}
          </p>
        </div>
      </section>

      <section className="band band-ruled" id="doors">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Evidence</p>
              <h2>Browse the measures</h2>
            </div>
          </div>
          <div className="doors">
            <div className="doors-col">
              <div className="doors-label">By legislation</div>
              <div className="chips">
                {Object.entries(FILES).map(([slug, meta]) => (
                  <Link key={slug} href={`/acts/${slug}`} className="chip">
                    {meta.name.split(" — ")[0]}
                  </Link>
                ))}
              </div>
            </div>
            <div className="doors-col">
              <div className="doors-label">By sector</div>
              <SectorGrid />
            </div>
          </div>
        </div>
      </section>

      <section className="band band-tight" id="coverage">
        <div className="wrap">
          <p className="coverage-line">
            {getCoverageLine()}{" "}
            <Link href="/coverage" className="section-link">
              What is covered →
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

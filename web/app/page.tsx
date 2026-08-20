import type { Metadata } from "next";
import Link from "next/link";
import FindingCard from "@/components/FindingCard";
import RecordCard from "@/components/RecordCard";
import SectorGrid from "@/components/SectorGrid";
import StatsStrip from "@/components/StatsStrip";
import Wordmark from "@/components/Wordmark";
import { FILES } from "@/lib/data";
import { getSiteSummary } from "@/lib/summaries";
import { getRecentlyAdded } from "@/lib/coverage";
import { getRecentFindings, withEvidence } from "@/lib/findings";
import { getConnectionCount } from "@/lib/graphStats";
import { getRecords } from "@/lib/records";
import { getCoverageLine, getMasthead } from "@/lib/sitetext";

// The home page is a front page, not a masthead. Five blocks, in this order:
// the slim head, the record feed, the findings, the doors, the coverage line.
//
// THE INVERSION, AND WHAT IT COST. The head used to be the page: wordmark,
// tagline, and three big figures above the fold, with the conclusions below
// them. It read as an identity rather than as something that had happened
// recently. So the head compresses — the masthead pair and the same three
// figures, now one slim strip — and the feed takes the lead. What was the
// "Recently added" band is gone rather than demoted: it said which act was
// added last, which is exactly what the first record in the feed says, at
// greater length and with a page behind it. Its one fact that the feed does
// not carry, the date the document was fetched, moved into the strip.
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

// The feed leads, so it shows enough to read as a feed rather than as a
// teaser, and stops before it becomes the /changes page.
const FEED_ON_HOME = 5;

export default function Home() {
  const records = getRecords().slice(0, FEED_ON_HOME);
  const findings = withEvidence(getRecentFindings(3));
  const site = getSiteSummary();
  const latest = getRecentlyAdded(1)[0];
  const masthead = getMasthead();

  // getRecentlyAdded only returns files that have a date, but the type does
  // not know that, and a strip reading "Latest addition — null" is worse than
  // a strip with three figures on it.
  const stats = [
    { value: site.measures.toLocaleString("en-US"), label: "Measures decoded" },
    { value: getConnectionCount().toLocaleString("en-US"), label: "Connections mapped" },
    { value: String(site.sectors.total_reach), label: "Sectors" },
    ...(latest?.lastUpdated ? [{ value: latest.lastUpdated, label: "Latest addition" }] : []),
  ];

  return (
    <main className="rise">
      <section className="home-head home-head-slim">
        <div className="wrap">
          <div className="home-wordmark">
            <Wordmark />
          </div>
          <p className="home-tagline">{masthead.tagline}</p>
          <p className="home-subline">{masthead.subline}</p>
          {/* Measures and sectors come from the gate-checked site summary;
              connections is the graph's total edge count, guarded by
              build_graph.py --check in prebuild so it moves with every
              ingestion and can never go stale. The fourth figure is when the
              most recent document was FETCHED, not when anything in it
              changed — said plainly on /coverage, because the two get
              confused. */}
          <Link href="/sectors" className="home-stats-link" aria-label="Browse sectors">
            <StatsStrip stats={stats} />
          </Link>
        </div>
      </section>

      <section className="band" id="latest">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Latest</p>
              <h2>What changed</h2>
            </div>
            <Link href="/changes" className="section-link">
              All records →
            </Link>
          </div>
          {records.length === 0 ? (
            <p className="section-note">No records published yet.</p>
          ) : (
            <div className="record-feed">
              {records.map((r) => (
                <RecordCard key={r.id} record={r} />
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="band band-paper" id="findings">
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

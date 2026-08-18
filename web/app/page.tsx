import Link from "next/link";
import FindingCard from "@/components/FindingCard";
import SectorGrid from "@/components/SectorGrid";
import Wordmark from "@/components/Wordmark";
import { FILES } from "@/lib/data";
import { getRecentlyAdded } from "@/lib/coverage";
import { BASIS_LABEL } from "@/lib/findings";
import { getRecentFindings, withEvidence } from "@/lib/findings";

// The home page leads with conclusions. Five blocks, in this order:
// wordmark, findings, recently added, doors, coverage line. Everything the old
// home page carried that is not one of those five — the signals feed, the
// burden ledger, the driver chart, the priorities, the analysis grid — still
// exists on its own page; it is demoted off the front, not deleted.

// TODO-GEORGE: tagline.
const TAGLINE = "TODO-GEORGE — one line saying what a reader gets here.";

// TODO-GEORGE: coverage line.
const COVERAGE_LINE =
  "TODO-GEORGE — one sentence stating the perimeter: what body of law this covers and what it does not.";

export default function Home() {
  const findings = withEvidence(getRecentFindings(5));
  const recent = getRecentlyAdded(4);

  return (
    <main className="rise">
      <section className="home-head">
        <div className="wrap">
          <div className="home-wordmark">
            <Wordmark />
          </div>
          <p className="home-tagline">{TAGLINE}</p>
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
              <h2>What the register last took in</h2>
            </div>
            <Link href="/coverage" className="section-link">
              Full coverage →
            </Link>
          </div>
          {/* Derived from sources/manifest.json and the .fetch.json sidecars.
              This is when the DOCUMENT was fetched, not when anything in it
              changed — said plainly, because the two get confused. */}
          <ul className="recent-list">
            {recent.map((f) => (
              <li key={f.slug} className="recent-item">
                <span className="recent-name">{f.title}</span>
                <span className="recent-meta">
                  {f.basis ? BASIS_LABEL[f.basis] : "—"} · {f.measures} measures · fetched{" "}
                  {f.lastUpdated}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="band band-ruled" id="doors">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Evidence</p>
              <h2>Browse the register</h2>
            </div>
          </div>
          <div className="doors">
            <div className="doors-col">
              <div className="doors-label">By legislation</div>
              <div className="chips">
                {Object.entries(FILES).map(([slug, meta]) => (
                  <Link key={slug} href={`/coverage#${slug}`} className="chip">
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
            {COVERAGE_LINE}{" "}
            <Link href="/coverage" className="section-link">
              What is covered →
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

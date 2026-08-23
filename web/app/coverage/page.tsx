import type { Metadata } from "next";
import Link from "next/link";
import DriverChart from "@/components/DriverChart";
import { getCoverage, getQueuedItems, getWeightNote } from "@/lib/coverage";
import type { CoverageFile } from "@/lib/coverage";
import { BASIS_LABEL } from "@/lib/findings";
import { getCoverageDeclaration, getPerimeterProse } from "@/lib/sitetext";
import { DEMOTED } from "@/lib/launch";

// The verification badge, in audience terms. The underlying dockets, gates
// and pass artifacts in sources/ are untouched; this is only how their result
// is stated to a reader — verified once a second, independent reading has
// been made and compared against the first, preliminary until then.
function isVerified(f: CoverageFile): boolean {
  return f.reads.reads > 1 && f.reads.reconciled;
}

const VERIFIED_LABEL = "Verified — confirmed by independent second reading";
const PRELIMINARY_LABEL = "Preliminary reading";

export function generateMetadata(): Metadata {
  const files = getCoverage();
  const total = files.reduce((n, f) => n + f.measures, 0);
  const verified = files.filter(isVerified).length;
  return {
    robots: DEMOTED,
    title: "Coverage",
    description: `${files.length} legislative acts on the platform, ${total} measures — ${verified} of ${files.length} acts verified by an independent second reading — plus what is queued and not yet read.`,
  };
}

export default function CoveragePage() {
  const files = getCoverage();
  const queued = getQueuedItems();
  const totalMeasures = files.reduce((n, f) => n + f.measures, 0);
  const verified = files.filter(isVerified).length;

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/" className="backlink">
              ← Home
            </Link>
            <span className="crumb">Coverage</span>
          </div>
          <h1 className="sector-title">Coverage</h1>
          {/* The perimeter paragraph — reviewed prose from data/prose.json,
              its counts rendered from the gate-checked site summary. Its last
              sentence states what is out of scope, so the page no longer
              carries a separate out-of-scope section. */}
          <p className="sector-intro">{getPerimeterProse()}</p>
          <p className="section-note">
            {files.length} acts · {totalMeasures} measures · {verified} of {files.length} verified.
          </p>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">What is read</p>
          <h2>Acts covered</h2>
          <div className="coverage-table">
            <div className="coverage-row coverage-head">
              <div>Act</div>
              <div>Source</div>
              <div>Standing</div>
              <div>Measures</div>
              <div>Verification</div>
              <div>Last fetched</div>
            </div>
            {files.map((f) => (
              <div className="coverage-row" key={f.slug} id={f.slug}>
                <div className="coverage-file">
                  <span className="coverage-file-name">{f.title}</span>
                  <span className="coverage-file-code">{f.code}</span>
                </div>
                <div className="coverage-celex">
                  {f.celexes.length === 0 ? (
                    // omnibus: read from a local text before the fetcher
                    // existed, so there is no CELEX on file to print.
                    <span className="coverage-muted">not fetched through EUR-Lex</span>
                  ) : (
                    f.celexes.map((c) => (
                      <span key={c.key}>
                        {c.celex}
                        {c.procedure ? ` · ${c.procedure}` : ""}
                      </span>
                    ))
                  )}
                </div>
                <div>{f.basis ? BASIS_LABEL[f.basis] : "—"}</div>
                <div className="coverage-num">{f.measures}</div>
                <div className="coverage-reads">
                  {isVerified(f) ? VERIFIED_LABEL : PRELIMINARY_LABEL}
                </div>
                <div className="coverage-num">{f.lastUpdated ?? "—"}</div>
              </div>
            ))}
          </div>
          {/* A file whose classifications stand on a preliminary reading says
              so here in one sentence — reviewed prose from data/prose.json.
              The dockets in sources/ that this condenses are unchanged. */}
          {files
            .filter((f) => f.reads.declaredSinglePass && getCoverageDeclaration(f.slug))
            .map((f) => (
              <p className="section-note" key={f.slug}>
                {getCoverageDeclaration(f.slug)}
              </p>
            ))}
          {/* The gap that the sector pages would otherwise each have to report
              for themselves. Stated once, here, because it is a fact about the
              register's coverage rather than about any one sector — and
              computed from the rows as built, because the previous hardcoded
              version of this sentence was already at risk of rotting. */}
          <p className="section-note">{getWeightNote()}</p>
          <p className="section-note">
            To read every measure across all acts, with the burden ledger above them —{" "}
            <Link href="/measures" className="section-link">
              open the measure browse →
            </Link>
          </p>
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">What the measures carry</p>
          <h2>Burden drivers across the corpus</h2>
          <p className="section-note section-note-wide">
            Seven yes-or-no marks are read off every measure on the platform. How often each one
            fires characterises what has actually been decoded — which is a statement about
            coverage, not about any one measure.
          </p>
          <div className="coverage-chart">
            <DriverChart />
          </div>
        </div>
      </section>

      <section className="band band-paper">
        <div className="wrap">
          <p className="eyebrow">Queued</p>
          <h2>Known, not yet read</h2>
          {queued.length === 0 ? (
            <p className="section-note">Nothing queued.</p>
          ) : (
            <ul className="queued-list">
              {queued.map((q, i) => (
                <li key={i}>
                  <span className="queued-title">{q.display_title ?? q.title}</span>
                  {q.celex && <span className="queued-celex">{q.celex}</span>}
                  {(q.display_note ?? q.note) && (
                    <span className="queued-note">{q.display_note ?? q.note}</span>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="band band-ruled" id="permanence">
        <div className="wrap">
          <p className="eyebrow">Permanence</p>
          <h2>Measure ids do not change</h2>
          <p className="section-note section-note-wide">
            A measure id, and the address built from it (/measures/&lt;act&gt;/&lt;id&gt;), is
            permanent. A measure whose classification changes keeps its id, and the change is
            recorded on the measure itself; any future change to an id or a URL shape ships with a
            redirect from the old address. Each release is archived in full — every measure and
            every fetched source version — under a dated snapshot that is never overwritten, so a
            citation made today stays checkable against exactly what was published today. Every
            measure page carries a &ldquo;cite this measure&rdquo; block with its permanent address.
          </p>
        </div>
      </section>
    </main>
  );
}

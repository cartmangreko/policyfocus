import type { Metadata } from "next";
import Link from "next/link";
import DriverChart from "@/components/DriverChart";
import { getCoverage, getQueuedItems, getWeightNote } from "@/lib/coverage";
import { BASIS_LABEL } from "@/lib/findings";

export const metadata: Metadata = {
  title: "Coverage",
  description:
    "What PolicyFocus reads, how many measures each file yields, how many times each was read, and what is queued.",
};

// TODO-GEORGE: perimeter statement.
const PERIMETER =
  "TODO-GEORGE — one paragraph stating the perimeter: what body of law the register covers, what it measures each provision against, and what a reader may conclude from a sector page as a result.";

// TODO-GEORGE: out-of-scope line.
const OUT_OF_SCOPE =
  "TODO-GEORGE — one line on what is deliberately out of scope, and where a reader should look instead.";

export default function CoveragePage() {
  const files = getCoverage();
  const queued = getQueuedItems();
  const totalMeasures = files.reduce((n, f) => n + f.measures, 0);
  const twice = files.filter((f) => f.reads.reads > 1).length;

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
          <p className="sector-intro">{PERIMETER}</p>
          <p className="section-note">
            {files.length} files · {totalMeasures} measures · {twice} of {files.length} read twice
            and reconciled.
          </p>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">What is read</p>
          <h2>Files in the register</h2>
          <div className="coverage-table">
            <div className="coverage-row coverage-head">
              <div>File</div>
              <div>Source</div>
              <div>Standing</div>
              <div>Measures</div>
              <div>Reads</div>
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
                <div className="coverage-reads">{f.reads.label}</div>
                <div className="coverage-num">{f.lastUpdated ?? "—"}</div>
              </div>
            ))}
          </div>
          <p className="section-note">
            The reads column is derived from what is on disk: a second extraction pass, a
            disagreement report comparing it with the first, and a docket. A docket is one of two
            documents. Three of them freeze the disagreements between two reads and record a ruling
            on each. The fourth declares the opposite — that no second read exists and that nothing
            in the file has been confirmed — and a file carrying one says so here rather than being
            left to look like a file nobody has got round to yet.
          </p>
          {/* The declaration itself, in the docket's own words, for every file
              that has one. A warning a reader has to go to sources/ to find is
              a warning the page is keeping to itself. */}
          {files
            .filter((f) => f.reads.note)
            .map((f) => (
              <p className="section-note" key={f.slug}>
                <strong>{f.title} — read once.</strong> {f.reads.note}
              </p>
            ))}
          {/* The gap that the sector pages would otherwise each have to report
              for themselves. Stated once, here, because it is a fact about the
              register's coverage rather than about any one sector — and
              computed from the rows as built, because the previous hardcoded
              version of this sentence was already at risk of rotting. */}
          <p className="section-note">{getWeightNote()}</p>
          <p className="section-note">
            To read the whole register flat — every row across all files, with the burden ledger
            above it —{" "}
            <Link href="/measures" className="section-link">
              open the measure browse →
            </Link>
          </p>
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">What the rows carry</p>
          <h2>Burden drivers across the corpus</h2>
          <p className="section-note section-note-wide">
            Seven yes-or-no marks are read off every provision in the register. How often each one
            fires characterises what has actually been extracted — which is a statement about
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
                  <span className="queued-title">{q.title}</span>
                  {q.celex && <span className="queued-celex">{q.celex}</span>}
                  {q.note && <span className="queued-note">{q.note}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">Out of scope</p>
          <p className="section-note section-note-wide">{OUT_OF_SCOPE}</p>
        </div>
      </section>
    </main>
  );
}

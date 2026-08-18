import type { Metadata } from "next";
import Link from "next/link";
import Ledger from "@/components/Ledger";
import SignalRow from "@/components/SignalRow";
import StatsStrip from "@/components/StatsStrip";
import { FILES, getAllMeasures, getRegisterStats } from "@/lib/data";
import type { Measure } from "@/lib/types";

export const metadata: Metadata = {
  title: "Measures",
  description:
    "The register, flat: every extracted provision across all six files, with who carries it and which direction it moves.",
};

// The cross-file browse view. /measures/<file>/<id> is the audit view of one
// provision; this is the whole register at once, which is a different question
// — "what is in here, and who does it land on" rather than "what exactly does
// this row say".
//
// The Ledger anchors it. It was built for the old home page and its logic is
// untouched: it answers the page's question directly, since a register-wide
// browse with no summary above it is a list, not a view.

function byFile(measures: Measure[]): [string, Measure[]][] {
  // Register order within a file, and FILES order across files — both are the
  // orders the data is maintained in, not a re-sort.
  return Object.keys(FILES)
    .map((slug): [string, Measure[]] => [slug, measures.filter((m) => m.file === slug)])
    .filter(([, rows]) => rows.length > 0);
}

export default function MeasuresPage() {
  const measures = getAllMeasures();
  const stats = getRegisterStats();
  const grouped = byFile(measures);
  const fileNames = Object.values(FILES)
    .map((f) => f.name.split(" — ")[0])
    .join(" · ");

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/" className="backlink">
              ← Home
            </Link>
            <span className="crumb">Measures</span>
          </div>
          <h1 className="sector-title">Measures</h1>
          <p className="sector-intro">
            Every provision extracted from the tracked corpus, in one list. Each row is one duty,
            one incentive or one entitlement, marked added or removed, with its seven-point burden
            strip. Open a row for the verbatim source text and the prior rule where there is one.
          </p>
          <StatsStrip
            stats={[
              { value: String(stats.measures), label: "Measures in the register" },
              { value: String(stats.sectors), label: "Sectors mapped" },
              { value: String(stats.classes), label: "Who-is-affected classes" },
              { value: String(stats.sourceChecked), suffix: "%", label: "Rows source-checked" },
            ]}
          />
        </div>
      </section>

      <section className="band band-paper" id="ledger">
        <div className="wrap">
          <p className="eyebrow">Who carries the burden</p>
          <h2>Duties added and removed, by who has to carry them</h2>
          <p className="section-note section-note-wide">
            A centred axis: relief runs left, new burden runs right. Read across the classes to see
            where a simplification package actually lands — and which duties it moves onto
            governments and the Commission rather than removing.
          </p>
          <div className="measures-ledger">
            <Ledger caption={fileNames} />
          </div>
        </div>
      </section>

      {grouped.map(([slug, rows]) => (
        <section className="band band-ruled" id={slug} key={slug}>
          <div className="wrap">
            <div className="section-head">
              <div>
                <p className="eyebrow">{FILES[slug].code}</p>
                <h2>{FILES[slug].name}</h2>
              </div>
              <Link href={`/coverage#${slug}`} className="section-link">
                How this file was read →
              </Link>
            </div>
            <p className="section-note">
              {rows.length} {rows.length === 1 ? "measure" : "measures"} ·{" "}
              {rows.filter((m) => m.direction === "add").length} added ·{" "}
              {rows.filter((m) => m.direction === "rem").length} removed
            </p>
            <div className="signals">
              {rows.map((m, i) => (
                <SignalRow key={`${m.file}-${m.id}`} measure={m} last={i === rows.length - 1} />
              ))}
            </div>
          </div>
        </section>
      ))}
    </main>
  );
}

import Link from "next/link";
import DriverChart from "@/components/DriverChart";
import Ledger from "@/components/Ledger";
import SearchBar from "@/components/SearchBar";
import SectorGrid from "@/components/SectorGrid";
import SignalRow from "@/components/SignalRow";
import StatsStrip from "@/components/StatsStrip";
import { ANALYSIS } from "@/lib/analysis";
import { FILES, getRegisterStats, getSignals } from "@/lib/data";
import { getPriorityCounts } from "@/lib/priorities";

export default function Home() {
  const stats = getRegisterStats();
  const signals = getSignals(6);
  const priorities = getPriorityCounts();
  const fileNames = Object.values(FILES)
    .map((f) => f.name.split(" — ")[0])
    .join(" · ");

  return (
    <main className="rise">
      <section className="hero">
        <div className="wrap">
          <p className="eyebrow">European policy intelligence · Economic impact</p>
          <h1 className="hero-title">European policy, decoded into economic impact.</h1>
          <p className="hero-standfirst">
            PolicyFocus turns complex European policy and regulation into structured intelligence on
            sectors, companies, markets, investment and strategic priorities.
          </p>
          <SearchBar />
        </div>
      </section>

      <section className="band band-tight" id="stats">
        <div className="wrap">
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

      <section className="band" id="signals">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Policy signals</p>
              <h2>What changed, and who now carries it</h2>
            </div>
            <Link href="#sectors" className="section-link">
              Open the full register →
            </Link>
          </div>
          <p className="section-note">
            Each item is a single measure, extracted from the source file and marked added or
            removed, with its seven-point burden strip. Every row traces to verbatim text.
          </p>
          <div className="signals">
            {signals.map((m, i) => (
              <SignalRow
                key={`${m.file}-${m.id}`}
                measure={m}
                last={i === signals.length - 1}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="band band-paper" id="burden">
        <div className="wrap">
          <p className="eyebrow">Who carries the burden</p>
          <h2>Duties added and removed, by who has to carry them</h2>
          <p className="section-note section-note-wide">
            A centred axis: relief runs left, new burden runs right. Read across the classes to see
            where a simplification package actually lands — and which duties it moves onto
            governments and the Commission rather than removing.
          </p>
          <div className="burden-grid">
            <Ledger caption={fileNames} />
            <DriverChart />
          </div>
        </div>
      </section>

      <section className="band" id="sectors">
        <div className="wrap">
          <p className="eyebrow">Explore by sector</p>
          <h2>Which industries the corpus touches</h2>
          <p className="section-note">
            Measures that name a sector, and those that reach it through its supply chain,
            procurement or regulatory dependencies. Counts across the tracked corpus.
          </p>
          <SectorGrid />
        </div>
      </section>

      <section className="band band-ruled" id="priorities">
        <div className="wrap">
          <p className="eyebrow">Strategic priorities</p>
          <h2>What the agenda is advancing</h2>
          <p className="section-note">
            Four lenses over the same register. Each count is the number of measures matching that
            lens, computed at build time.
          </p>
          <div className="priorities">
            {priorities.map((p) => (
              <Link key={p.slug} href={`/priorities/${p.slug}`} className="priority">
                <div>
                  <div className="priority-title">{p.title}</div>
                  <div className="priority-desc">{p.description}</div>
                </div>
                <div className="priority-count">{p.count} measures</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="band band-ruled" id="analysis">
        <div className="wrap">
          <div className="section-head section-head-spaced">
            <div>
              <p className="eyebrow">Analysis</p>
              <h2>Reading the change</h2>
            </div>
            <Link href={`/analysis/${ANALYSIS[0].slug}`} className="section-link">
              All analysis →
            </Link>
          </div>
          <div className="hairline-grid analysis-grid">
            {ANALYSIS.map((a) => (
              <Link key={a.slug} href={`/analysis/${a.slug}`} className="analysis-card">
                <div className="analysis-kicker">{a.kicker}</div>
                <h3 className="analysis-title">{a.title}</h3>
                <p className="analysis-dek">{a.dek}</p>
                <div className="analysis-meta">
                  {a.readingTime} · {a.date}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

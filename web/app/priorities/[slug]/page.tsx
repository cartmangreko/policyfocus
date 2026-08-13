import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SignalRow from "@/components/SignalRow";
import StatsStrip from "@/components/StatsStrip";
import { CLASS_LABELS, FILES, SECTORS } from "@/lib/data";
import {
  PRIORITIES,
  getPriority,
  getPriorityByFile,
  getPriorityMeasures,
} from "@/lib/priorities";
import type { Measure, MeasureClass, SectorSlug } from "@/lib/types";

export function generateStaticParams() {
  return PRIORITIES.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const priority = getPriority(slug);
  if (!priority) return { title: "Priority not found" };
  return { title: priority.title, description: priority.standfirst };
}

function countBy<K>(measures: Measure[], key: (m: Measure) => K[]): Map<K, number> {
  const out = new Map<K, number>();
  for (const m of measures) {
    for (const k of key(m)) out.set(k, (out.get(k) ?? 0) + 1);
  }
  return out;
}

export default async function PriorityPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const priority = getPriority(slug);
  if (!priority) notFound();

  const measures = getPriorityMeasures(slug);
  const byFile = getPriorityByFile(slug);
  const byClass = [...countBy(measures, (m) => [m.class]).entries()].sort((a, b) => b[1] - a[1]);
  const sectorCounts = countBy(measures, (m) => [
    ...new Set([...(m.sectors_named ?? []), ...(m.sectors_reached ?? [])]),
  ]);
  const bySector = [...sectorCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);

  const maxFile = Math.max(1, ...byFile.map((f) => f.count));
  const others = PRIORITIES.filter((p) => p.slug !== slug);

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/#priorities" className="backlink">
              ← All priorities
            </Link>
            <span className="crumb">Strategic priorities / {priority.title}</span>
          </div>
          <h1 className="sector-title">{priority.title}</h1>
          <p className="sector-intro">{priority.standfirst}</p>
          <StatsStrip
            stats={[
              { value: String(measures.length), label: "Measures in scope" },
              { value: String(byFile.length), label: "Legislative files" },
              { value: String(byClass.length), label: "Classes affected" },
              { value: String(sectorCounts.size), label: "Sectors touched" },
            ]}
          />
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">Across the corpus</p>
          <h2>Where this priority is being advanced</h2>
          <p className="section-note">
            The same lens applied to every tracked file. As more legislation is added to the
            register, it appears here without this page changing.
          </p>
          <div className="filebars">
            {byFile.map((f) => (
              <div key={f.file} className="filebar">
                <div className="filebar-name">
                  {f.name}
                  <span className="filebar-code">{f.code}</span>
                </div>
                <div className="filebar-track">
                  <div className="filebar-fill" style={{ width: `${(f.count / maxFile) * 100}%` }} />
                </div>
                <div className="filebar-count">
                  {f.count}
                  <span className="filebar-share">{f.share}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="band band-paper">
        <div className="wrap">
          <p className="eyebrow">How this lens is drawn</p>
          <h2>What counts as {priority.title.toLowerCase()}</h2>
          <p className="section-note section-note-wide">{priority.method}</p>
          <div className="split-grid">
            <div className="card">
              <div className="card-label">Who carries it</div>
              <div className="minibars">
                {byClass.map(([cls, n]) => (
                  <div key={cls} className="minibar">
                    <span className="minibar-name">{CLASS_LABELS[cls as MeasureClass]}</span>
                    <span
                      className="minibar-fill"
                      style={{ width: `${(n / (byClass[0]?.[1] ?? 1)) * 100}%` }}
                    />
                    <span className="minibar-count">{n}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="card">
              <div className="card-label">Sectors most touched</div>
              {bySector.length ? (
                <div className="minibars">
                  {bySector.map(([sector, n]) => (
                    <div key={sector} className="minibar">
                      <Link href={`/sectors/${sector}`} className="minibar-name">
                        {SECTORS[sector as SectorSlug]}
                      </Link>
                      <span
                        className="minibar-fill minibar-fill-alt"
                        style={{ width: `${(n / (bySector[0]?.[1] ?? 1)) * 100}%` }}
                      />
                      <span className="minibar-count">{n}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="card-note">
                  No measure under this priority names or reaches a sector — these provisions apply
                  by size, status or activity rather than by industry.
                </p>
              )}
            </div>
          </div>
        </div>
      </section>

      {byFile.map((f) => {
        const rows = measures.filter((m) => m.file === f.file);
        return (
          <section key={f.file} className="band band-ruled">
            <div className="wrap">
              <p className="eyebrow">{FILES[f.file]?.code ?? f.file}</p>
              <h2>{f.name}</h2>
              <p className="section-note">
                {rows.length} of the {measures.length} measures under this priority come from this
                file.
              </p>
              <div className="signals">
                {rows.map((m, i) => (
                  <SignalRow
                    key={`${m.file}-${m.id}`}
                    measure={m}
                    last={i === rows.length - 1}
                  />
                ))}
              </div>
            </div>
          </section>
        );
      })}

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">Other priorities</p>
          <h2>Read the same corpus another way</h2>
          <div className="priorities">
            {others.map((p) => (
              <Link key={p.slug} href={`/priorities/${p.slug}`} className="priority">
                <div>
                  <div className="priority-title">{p.title}</div>
                  <div className="priority-desc">{p.description}</div>
                </div>
                <div className="priority-count">→</div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

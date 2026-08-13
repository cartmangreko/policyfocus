import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SignalRow from "@/components/SignalRow";
import {
  ANALYSIS,
  getAnalysis,
  getAnalysisEvidence,
  getAnalysisEvidenceCount,
} from "@/lib/analysis";

export function generateStaticParams() {
  return ANALYSIS.map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const piece = getAnalysis(slug);
  if (!piece) return { title: "Analysis not found" };
  return { title: piece.title, description: piece.dek };
}

export default async function AnalysisPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const piece = getAnalysis(slug);
  if (!piece) notFound();

  const evidence = getAnalysisEvidence(slug);
  const total = getAnalysisEvidenceCount(slug);
  const others = ANALYSIS.filter((a) => a.slug !== slug);

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/#analysis" className="backlink">
              ← All analysis
            </Link>
            <span className="crumb">Analysis / {piece.kicker}</span>
          </div>
          <article className="article">
            <h1 className="article-title">{piece.title}</h1>
            <p className="article-standfirst">{piece.standfirst}</p>
            <div className="article-byline">
              {piece.readingTime} · {piece.date} · PolicyFocus analysis
            </div>
            {piece.body.map((para, i) => (
              <p key={i} className="article-para">
                {para}
              </p>
            ))}
          </article>
        </div>
      </section>

      <section className="band band-paper">
        <div className="wrap">
          <p className="eyebrow">Evidence</p>
          <h2>The measures this piece is reading</h2>
          <p className="section-note">
            {piece.evidenceNote} {total} in the register
            {evidence.length < total ? `; the first ${evidence.length} shown` : ""}.
          </p>
          <div className="signals">
            {evidence.map((m, i) => (
              <SignalRow
                key={`${m.file}-${m.id}`}
                measure={m}
                last={i === evidence.length - 1}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">More analysis</p>
          <h2>Reading the change</h2>
          <div className="hairline-grid analysis-grid analysis-grid-2">
            {others.map((a) => (
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

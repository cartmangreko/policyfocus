import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import FindingDiagram from "@/components/FindingDiagram";
import MeasureEvidence from "@/components/MeasureEvidence";
import { FILES, SECTORS } from "@/lib/data";
import {
  BASIS_LABEL,
  BASIS_NOTE,
  evidenceStrip,
  getFinding,
  getFindingDiagram,
  getFindingsIndex,
  hasExposurePanel,
  resolveExposure,
  resolveMeasures,
} from "@/lib/findings";
import { headlineStep } from "@/lib/text";
import type { SectorSlug } from "@/lib/types";

// Every path this route serves is enumerated below, so an unlisted one is a
// 404 rather than a render on demand. That is load-bearing on Vercel: the
// register JSON lives outside web/ and is read at build time only, so a
// function rendering an unknown slug would have nothing to read. See
// README.md, "Deploying".
export const dynamicParams = false;

export function generateStaticParams() {
  return getFindingsIndex().map((f) => ({ id: f.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const finding = getFinding(id);
  if (!finding) return { title: "Finding not found" };
  return { title: finding.headline, description: evidenceStrip(finding) };
}

// "4 measures, and 1 figure from Eurostat input-output data. Every one is
// checked against its source before this page is built."
function evidenceSentence(measures: number, exposure: number): string {
  const parts = [`${measures} ${measures === 1 ? "measure" : "measures"}`];
  if (exposure > 0) {
    parts.push(`${exposure} ${exposure === 1 ? "figure" : "figures"} from Eurostat input-output data`);
  }
  return `${parts.join(", and ")}. Every one is checked against its source before this page is built.`;
}

export default async function FindingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const finding = getFinding(id);
  if (!finding) notFound();

  const measures = resolveMeasures(finding);
  const exposure = resolveExposure(finding);
  const diagram = getFindingDiagram(finding.id);
  const banner = BASIS_NOTE[finding.basis_status];
  const paragraphs = finding.body.split("\n").filter((p) => p.trim().length > 0);

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/findings" className="backlink">
              ← All findings
            </Link>
            <span className="crumb">Findings</span>
          </div>
          <h1 className={`detail-title${headlineStep(finding.headline)}`}>{finding.headline}</h1>
          <div className="detail-meta">
            <span>
              <span className="detail-meta-label">Published</span> {finding.date}
            </span>
            <span>
              <span className="detail-meta-label">Basis</span> {BASIS_LABEL[finding.basis_status]}
            </span>
            <span>
              <span className="detail-meta-label">Evidence</span> {evidenceStrip(finding)}
            </span>
          </div>
          <div className="finding-sectors finding-sectors-lg">
            {finding.sectors.map((s) => (
              <Link key={s} href={`/sectors/${s}`} className="finding-sector">
                {SECTORS[s as SectorSlug] ?? s}
              </Link>
            ))}
          </div>
          {/* The banner appears on any basis that is not settled law, and it
              appears above the body rather than under it. */}
          {banner && <p className="basis-banner">{banner}</p>}
          {finding.review?.status === "open" && (
            <p className="basis-banner basis-banner-review">
              Under review. {finding.review.q ?? ""}
            </p>
          )}
        </div>
      </section>

      <section className="detail-body">
        <div className="wrap finding-body">
          {paragraphs.map((p, i) => (
            <p key={i} className="prose">
              {p}
            </p>
          ))}
          {diagram && <FindingDiagram diagram={diagram} />}
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">Evidence</p>
          <h2>What this rests on</h2>
          {/* Composed as one string: split across JSX expressions, the
              punctuation picks up stray spaces. */}
          <p className="section-note">{evidenceSentence(measures.length, exposure.length)}</p>

          <div className="evidence-list">
            {measures.map((m) => (
              <MeasureEvidence key={`${m.file}-${m.id}`} measure={m} />
            ))}
          </div>

          {exposure.length > 0 && (
            <div className="evidence-exposure">
              <h3 className="rule-head">Exposure</h3>
              <ul className="evidence-exposure-list">
                {exposure.map((e, i) => (
                  <li key={i}>
                    {e.sentence}{" "}
                    {hasExposurePanel(e.sector) && (
                      <Link href={e.href} className="source-link">
                        See the panel →
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {finding.evidence.notes && <p className="evidence-notes">{finding.evidence.notes}</p>}
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">Follow the evidence</p>
          <h2>Where this came from</h2>
          <div className="chips">
            {finding.files.map((f) => (
              <Link key={f} href={`/measures#${f}`} className="chip">
                {FILES[f]?.name.split(" — ")[0] ?? f}
                <span className="chip-count">file</span>
              </Link>
            ))}
            {finding.sectors.map((s) => (
              <Link key={s} href={`/sectors/${s}`} className="chip">
                {SECTORS[s as SectorSlug] ?? s}
                <span className="chip-count">sector</span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

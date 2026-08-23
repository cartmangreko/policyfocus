import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import FindingDiagram from "@/components/FindingDiagram";
import MeasureEvidence from "@/components/MeasureEvidence";
import SectorIcon from "@/components/SectorIcon";
import { BASIS_LABEL, BASIS_NOTE } from "@/lib/findings";
import {
  TEMPLATE_LABEL,
  actShortName,
  evidenceStrip,
  getRecord,
  getRecordDiagram,
  getRecords,
  isWholeAct,
  reachedWithChannels,
  recordMeasures,
  sectorName,
} from "@/lib/records";
import { headlineStep } from "@/lib/text";
import { DEMOTED } from "@/lib/launch";

// Every path this route serves is enumerated below, so an unlisted one is a
// 404 rather than a render on demand — the same reason the finding route does
// it: the register JSON lives outside web/ and is read at build time only.
export const dynamicParams = false;

export function generateStaticParams() {
  return getRecords().map((r) => ({ id: r.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const record = getRecord(id);
  if (!record) return { title: "Record not found" };
  return { title: record.headline, description: evidenceStrip(record), robots: DEMOTED };
}

// The measures a record about a whole act stands for are all of them, and a
// page cannot usefully list 89. It shows the ones the act names its leading
// sector on, and sends the reader to the act for the rest.
const WHOLE_ACT_SHOWN = 5;

export default async function RecordPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const record = getRecord(id);
  if (!record) notFound();

  const diagram = getRecordDiagram(record.id);
  const banner = BASIS_NOTE[record.basis_status];
  const wholeAct = isWholeAct(record);
  const all = recordMeasures(record);
  const measures = wholeAct
    ? all.filter((m) => m.sectors_named.includes(record.top_sector)).slice(0, WHOLE_ACT_SHOWN)
    : all;
  const reached = reachedWithChannels(record);
  const paragraphs = record.body.split("\n").filter((p) => p.trim().length > 0);

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/changes" className="backlink">
              ← Latest
            </Link>
            <span className="crumb">Latest</span>
          </div>
          <h1 className={`detail-title${headlineStep(record.headline)}`}>{record.headline}</h1>
          <div className="detail-meta">
            <span>
              <span className="detail-meta-label">Event</span> {record.event_date}
            </span>
            <span>
              <span className="detail-meta-label">Change</span> {TEMPLATE_LABEL[record.template]}
            </span>
            <span>
              <span className="detail-meta-label">Basis</span> {BASIS_LABEL[record.basis_status]}
            </span>
          </div>
          <div className="chips">
            <Link href={`/acts/${record.file}`} className="chip">
              {actShortName(record.file)}
              <span className="chip-count">act</span>
            </Link>
          </div>
          {banner && <p className="basis-banner">{banner}</p>}
        </div>
      </section>

      <section className="detail-body">
        <div className="wrap finding-body">
          {/* The diagram leads, for the reason it leads on a finding: the
              change is a shape — this act, these sectors, this many measures —
              and the picture carries the shape faster than the sentence. */}
          {diagram && (
            <FindingDiagram
              diagram={diagram}
              caption="Every figure on this diagram is counted from the act itself, and checked before the page is built."
            />
          )}
          {paragraphs.map((p, i) => (
            <p key={i} className="prose">
              {p}
            </p>
          ))}
        </div>
      </section>

      <section className="band band-ruled">
        <div className="wrap">
          <p className="eyebrow">Sectors</p>
          <h2>Who this lands on</h2>
          <p className="section-note">
            Sectors the act names in its own text, and — where the reach can be stated — the
            sectors its measures arrive at through a chain, with the channel each one travels.
          </p>

          <h3 className="rule-head">Named in the act</h3>
          <div className="chips">
            {record.sectors_named.map((s) => (
              <Link key={s} href={`/sectors/${s}`} className="chip">
                <SectorIcon slug={s} size={14} />
                {sectorName(s)}
              </Link>
            ))}
          </div>

          {record.reach.suppressed ? (
            /* Not an empty state. The reach exists and is not sayable yet, and
               saying which is the difference between a gap in the data and a
               limit in the method. sources/scope.md, "Reach is not stated on a
               record about an amending proposal". */
            <p className="section-note reach-note">
              Supply-chain reach is not stated on this record. The act is a proposal amending an
              act already in force, and reach is currently computed against the proposal rather
              than the act it amends — so the sectors it would list are the existing regime&rsquo;s,
              not the change&rsquo;s.
            </p>
          ) : (
            reached.length > 0 && (
              <>
                <h3 className="rule-head">Reached through a chain</h3>
                <ul className="reach-list">
                  {reached.map((r) => (
                    <li key={r.slug}>
                      <SectorIcon slug={r.slug} size={14} />
                      <Link href={`/sectors/${r.slug}`} className="reach-sector">
                        {r.name}
                      </Link>
                      {r.channels.map((c) => (
                        <span key={c} className="reach-channel">
                          {c}
                        </span>
                      ))}
                    </li>
                  ))}
                </ul>
              </>
            )
          )}
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <p className="eyebrow">Measures</p>
          <h2>{wholeAct ? "What the act requires" : "What changed"}</h2>
          <p className="section-note">
            {wholeAct
              ? `All ${record.counts.measures} measures of this act are on the platform. These are the ones it names ${sectorName(record.top_sector).toLowerCase()} on.`
              : `The ${record.counts.measures} measures this record is about. Where the earlier wording could be sourced, each shows what it said before.`}
          </p>

          <div className="evidence-list">
            {measures.map((m) => (
              <MeasureEvidence key={`${m.file}-${m.id}`} measure={m} />
            ))}
          </div>

          <div className="chips">
            <Link href={`/acts/${record.file}`} className="chip">
              {wholeAct ? `All ${record.counts.measures} measures` : "The whole act"}
              <span className="chip-count">→</span>
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}

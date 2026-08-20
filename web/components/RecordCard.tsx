import Link from "next/link";
import { BASIS_LABEL } from "@/lib/findings";
import {
  TEMPLATE_LABEL,
  actShortName,
  evidenceStrip,
  recordHref,
  sectorName,
} from "@/lib/records";
import type { ChangeRecord } from "@/lib/records";
import { firstSentence, headlineStep } from "@/lib/text";

// A record wherever it appears in short form: the home feed, the /changes
// index, and the sector pages. Like a finding card it carries its evidence
// strip — a headline is never rendered anywhere without the line saying what
// it rests on — and like a record page it leads with the event, because the
// date is the thing a feed is ordered by and the thing a reader is scanning
// for.
export default function RecordCard({ record }: { record: ChangeRecord }) {
  const sectors = record.sectors_named;
  return (
    <Link href={recordHref(record.id)} className="record-card">
      <div className="record-card-top">
        <span className="record-date">{record.event_date}</span>
        <span className="record-kind">{TEMPLATE_LABEL[record.template]}</span>
        {record.basis_status !== "adopted" && (
          <span className="record-basis">{BASIS_LABEL[record.basis_status]}</span>
        )}
      </div>
      <h3 className={`record-headline${headlineStep(record.headline)}`}>{record.headline}</h3>
      <p className="record-lede">{firstSentence(record.body)}</p>
      <div className="record-evidence">{evidenceStrip(record)}</div>
      <div className="record-sectors">
        <span className="record-act">{actShortName(record.file)}</span>
        {sectors.map((s) => (
          <span key={s} className="record-sector">
            {sectorName(s)}
          </span>
        ))}
      </div>
    </Link>
  );
}

import Link from "next/link";
import { SECTORS } from "@/lib/data";
import { BASIS_LABEL, evidenceStrip, findingHref } from "@/lib/findings";
import type { Finding } from "@/lib/findings";
import { firstSentence, headlineStep } from "@/lib/text";
import type { SectorSlug } from "@/lib/types";

// A finding, everywhere it appears in short form: the home page, the findings
// index, and the sector pages. It takes the whole finding rather than the
// index entry because the evidence strip is not optional — a headline is never
// rendered anywhere without the line saying what it rests on.
export default function FindingCard({ finding }: { finding: Finding }) {
  const basis = finding.basis_status;
  return (
    <Link href={findingHref(finding.id)} className="finding-card">
      <div className="finding-card-top">
        <span className="finding-date">{finding.date}</span>
        {basis !== "adopted" && (
          <span className="finding-basis">{BASIS_LABEL[basis]}</span>
        )}
      </div>
      <h3 className={`finding-headline${headlineStep(finding.headline)}`}>{finding.headline}</h3>
      <p className="finding-lede">{firstSentence(finding.body)}</p>
      <div className="finding-evidence">{evidenceStrip(finding)}</div>
      <div className="finding-sectors">
        {finding.sectors.map((s) => (
          <span key={s} className="finding-sector">
            {SECTORS[s as SectorSlug] ?? s}
          </span>
        ))}
      </div>
    </Link>
  );
}

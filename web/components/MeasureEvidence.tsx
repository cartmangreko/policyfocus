import Link from "next/link";
import RuleDiff from "./RuleDiff";
import ValenceTag from "./ValenceTag";
import { CLASS_LABELS, FILES, measureHref } from "@/lib/data";
import type { Measure } from "@/lib/types";

// One cited measure, rendered as evidence under a finding.
//
// Nothing here is a second implementation of anything: the valence chip is the
// ValenceTag component, the before/after states come from lib/ruleDiff (the
// same RuleDiff component the measure page renders, with the same rule that a
// prior pane appears only when prior_rule exists), and the source block reuses
// the .source styles the measure page already ships. If the rule for what a
// prior pane means changes, it changes in one place and both pages follow.
export default function MeasureEvidence({ measure }: { measure: Measure }) {
  const fileMeta = FILES[measure.file];

  return (
    <article className="evidence-measure">
      <div className="evidence-measure-head">
        <ValenceTag
          measureType={measure.measure_type}
          direction={measure.direction}
          suffix={measure.id}
        />
        <Link href={measureHref(measure)} className="evidence-measure-link">
          Open the measure →
        </Link>
      </div>

      <p className="evidence-statement">{measure.duty ?? measure.benefit}</p>

      <div className="evidence-meta">
        <span>{fileMeta ? fileMeta.name.split(" — ")[0] : measure.file}</span>
        <span>{measure.article}</span>
        <span>{measure.addressee}</span>
        <span>{CLASS_LABELS[measure.class]}</span>
      </div>

      {/* The delta, on the rows that carry one. The same component the measure
          page uses, so a row reads the same way in both places. */}
      <RuleDiff measure={measure} />

      <div className="source">
        <div className="source-label">Verbatim</div>
        <p className="source-quote">{measure.source_text}</p>
        <a href={measure.source_url} target="_blank" rel="noopener" className="source-link">
          View source →
        </a>
      </div>
    </article>
  );
}

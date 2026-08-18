import { getAfterState, getBeforeState } from "@/lib/ruleDiff";
import { isStated } from "@/lib/text";
import type { Measure } from "@/lib/types";

// The prior-rule / new-rule pair. Extracted from the measure page unchanged so
// that the finding pages can cite a measure without a second copy of the
// before/after rules drifting away from it: show a prior pane only when
// prior_rule exists, never print a "no prior rule" placeholder, and name the
// statement after the row's side.
function statementLabel(measure: Measure): string {
  if (measure.measure_type === "right") return "Entitlement";
  if (measure.measure_type === "incentive") return "Benefit";
  return "Obligation";
}

export default function RuleDiff({ measure }: { measure: Measure }) {
  const after = getAfterState(measure);
  const before = getBeforeState(measure);
  const label = statementLabel(measure);

  return (
    <div className={`diff ${before ? "" : "diff-single"}`}>
      {before && (
        <div className="diff-pane diff-prior">
          <div className="diff-label">Prior rule</div>
          {isStated(before.trigger) && (
            <>
              <div className="diff-field">Trigger</div>
              <p>{before.trigger}</p>
            </>
          )}
          <div className="diff-field">{label}</div>
          <p>{before.statement}</p>
          {before.status === "unresolved" && (
            <p className="diff-unresolved">Prior wording not available in the source file.</p>
          )}
        </div>
      )}
      <div className="diff-pane diff-new">
        <div className="diff-label">{before ? "New rule" : "New — no predecessor"}</div>
        {isStated(after.trigger) && (
          <>
            <div className="diff-field">Trigger</div>
            <p>{after.trigger}</p>
          </>
        )}
        <div className="diff-field">{label}</div>
        <p>{after.statement}</p>
      </div>
    </div>
  );
}

export function ruleDiffHeading(measure: Measure): string {
  return getBeforeState(measure) ? "Prior rule vs new rule" : "The rule";
}

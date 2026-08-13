// Before/after rendering rules (fixed, do not change without sign-off):
// - Show "Before" only when prior_rule exists (truthy). Never print a
//   "no prior rule" placeholder.
// - A measure with no prior_rule renders single-state and is tagged "New".
// - Rows that lack the diff-model fields entirely (ets.json/iaa.json, which
//   have no new_rule/prior_rule at all) fall back to their base
//   trigger/duty/benefit fields for the "after" state, so the page never
//   breaks on an older or differently-shaped row.
import type { Measure } from "./types";

export interface RuleStateView {
  trigger: string;
  statement: string;
  sourceText?: string | null;
  status?: string;
  note?: string;
}

export function getAfterState(measure: Measure): RuleStateView {
  if (measure.new_rule) {
    return { trigger: measure.new_rule.trigger, statement: measure.new_rule.obligation };
  }
  return {
    trigger: measure.trigger,
    statement: measure.duty ?? measure.benefit ?? "",
  };
}

export function getBeforeState(measure: Measure): RuleStateView | null {
  if (!measure.prior_rule) return null;
  const p = measure.prior_rule;
  return {
    trigger: p.trigger,
    statement: p.obligation,
    sourceText: p.source_text,
    status: p.status,
    note: p.note,
  };
}

export function isNewMeasure(measure: Measure): boolean {
  return !measure.prior_rule;
}

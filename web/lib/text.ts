// Several fields carry an explicit "not applicable" rather than being absent —
// a trigger of "n/a", or "n/a — Member States" where the duty binds by status
// rather than by any condition being met. Those are not facts to display, so
// the presentation layer omits the field entirely instead of printing "n/a".
export function isStated(value: string | null | undefined): value is string {
  if (!value) return false;
  const v = value.trim();
  if (!v) return false;
  return !/^n\/?a\b/i.test(v);
}

/**
 * Which display step a measure's headline should be set at.
 *
 * Hierarchy by type size only works when the thing at the top of it is short.
 * The design system was drawn against a headline-length title -- "Third-country
 * group reporting threshold raised to EUR 450 million", 61 characters -- but a
 * register row's headline is its duty statement, and those are written to be
 * precise rather than short: the median is 188 characters, 70% run past 150,
 * and the longest is 502. Set at the hero step, a median row runs seven lines
 * of 900-weight display type and the page reads as a wall rather than a
 * hierarchy; the meta line, the rule, and the source quote all fall below the
 * fold.
 *
 * So the step comes down as the statement gets longer. The headline stays the
 * largest thing on the page at every step -- the hierarchy is preserved, not
 * flattened -- but a long statement is set at a size a person can actually read
 * a paragraph in, which is the honest thing to do with a paragraph.
 *
 * Thresholds are in characters because that is what the constraint is about.
 * They sit near the distribution's own joints: 110 is roughly the short tail,
 * 210 is roughly the third quartile.
 */
export function headlineStep(text: string): "" | " is-long" | " is-xlong" {
  const n = text.trim().length;
  if (n > 210) return " is-xlong";
  if (n > 110) return " is-long";
  return "";
}

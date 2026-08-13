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

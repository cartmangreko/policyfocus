import { isPositiveValence, valenceLabel } from "@/lib/valence";
import type { Direction, MeasureType } from "@/lib/types";

export default function ValenceTag({
  measureType,
  direction,
  suffix,
}: {
  measureType?: MeasureType;
  direction: Direction;
  /** Appended after a separator, e.g. the measure id on a detail page. */
  suffix?: string;
}) {
  const positive = isPositiveValence(measureType, direction);
  const label = valenceLabel(measureType, direction);
  return (
    <span className={`tag ${positive ? "tag-pos" : "tag-neg"}`}>
      {suffix ? `${label} · ${suffix}` : label}
    </span>
  );
}

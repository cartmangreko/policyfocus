// Valence is derived at render time from measure_type + direction — it is
// never read as a stored string. The label mapping is the single place a
// future rename lives; nothing else in the presentation layer should
// hardcode "Requirement" / "Simplification" / etc.
import type { Direction, MeasureType } from "./types";

export type StoredValence = "Burden" | "Relief" | "Opportunity" | "Loss" | "Neutral";
export type ValenceLabel = "Requirement" | "Simplification" | "Opportunity" | "Support cut" | "Neutral";

// The stored valence names what the provision does to the register; the label
// names it to a reader. "Requirement" / "Simplification" is the product
// vocabulary — deliberately not the data's "Burden" / "Relief", which reads as
// a verdict. Changing the words is a one-line edit here; nothing else in the
// presentation layer names them.
const VALENCE_LABELS: Record<StoredValence, ValenceLabel> = {
  Burden: "Requirement",
  Relief: "Simplification",
  Opportunity: "Opportunity",
  Loss: "Support cut",
  Neutral: "Neutral",
};

export function deriveValence(measureType: MeasureType | undefined, direction: Direction): StoredValence {
  const type = measureType ?? "obligation";
  if (type === "obligation" && direction === "add") return "Burden";
  if (type === "obligation" && direction === "rem") return "Relief";
  if (type === "incentive" && direction === "add") return "Opportunity";
  if (type === "incentive" && direction === "rem") return "Loss";
  return "Neutral";
}

export function valenceLabel(measureType: MeasureType | undefined, direction: Direction): ValenceLabel {
  return VALENCE_LABELS[deriveValence(measureType, direction)];
}

// CSS class hook per valence, kept separate from the label text so a rename
// never touches styling either.
const VALENCE_CLASS: Record<StoredValence, string> = {
  Burden: "valence-burden",
  Relief: "valence-relief",
  Opportunity: "valence-opportunity",
  Loss: "valence-loss",
  Neutral: "valence-neutral",
};

export function valenceClassName(measureType: MeasureType | undefined, direction: Direction): string {
  return VALENCE_CLASS[deriveValence(measureType, direction)];
}

// Simplification and Opportunity read pine; Requirement and Support cut read
// claret.
export function isPositiveValence(
  measureType: MeasureType | undefined,
  direction: Direction
): boolean {
  const v = deriveValence(measureType, direction);
  return v === "Relief" || v === "Opportunity";
}

import Link from "next/link";
import BurdenStrip from "./BurdenStrip";
import ValenceTag from "./ValenceTag";
import { CLASS_LABELS, measureHref } from "@/lib/data";
import { isPositiveValence } from "@/lib/valence";
import { isStated } from "@/lib/text";
import type { Measure } from "@/lib/types";

// Nature is stored snake_case ("new_obligation"); the meta line wants prose.
const NATURE_LABELS: Record<string, string> = {
  exemption: "Exemption",
  new_obligation: "New obligation",
  reduction: "Reduction",
  extension: "Extension",
};

function natureLabel(nature?: string): string | null {
  if (!nature) return null;
  return NATURE_LABELS[nature] ?? nature.replace(/_/g, " ");
}

// `when` is a full sentence in the data. The meta line takes its first clause,
// and drops the field entirely when it is stored as "n/a".
function timing(when: string): string | null {
  if (!isStated(when)) return null;
  const head = when.split(/[(;]/)[0].trim();
  return head.length > 64 ? `${head.slice(0, 61)}…` : head;
}

export default function SignalRow({ measure, last }: { measure: Measure; last?: boolean }) {
  const positive = isPositiveValence(measure.measure_type, measure.direction);
  const meta = [natureLabel(measure.nature), timing(measure.when)].filter(Boolean);

  return (
    <Link href={measureHref(measure)} className={`signal ${last ? "signal-last" : ""}`}>
      <span className="signal-id">{measure.id}</span>
      <span className="signal-body">
        <span className="signal-statement">{measure.duty ?? measure.benefit}</span>
        <span className="signal-addressee">
          {/* The class is a coarser restatement of the addressee for some rows
              (addressee "European Commission", class "European Commission") —
              don't print it twice. */}
          {measure.addressee}
          {measure.addressee.trim().toLowerCase() !== CLASS_LABELS[measure.class].toLowerCase() &&
            ` · ${CLASS_LABELS[measure.class]}`}
        </span>
        <span className="signal-meta">
          {measure.article}
          {meta.length ? ` · ${meta.join(" · ")}` : ""}
        </span>
      </span>
      <span className="signal-marks">
        <ValenceTag measureType={measure.measure_type} direction={measure.direction} />
        <BurdenStrip drivers={measure.drivers} positive={positive} />
      </span>
    </Link>
  );
}

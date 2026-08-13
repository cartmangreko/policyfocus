import { DRIVER_CODES } from "@/lib/data";
import type { DDriver } from "@/lib/types";

// Seven yes-or-no marks, D1..D7 left to right. On-marks read ink on a burden
// row and pine on a relief row — the direction is carried by colour, not by
// which marks are lit.
export default function BurdenStrip({
  drivers,
  positive,
}: {
  drivers?: DDriver[];
  positive: boolean;
}) {
  const on = new Set(drivers ?? []);
  const label = on.size
    ? `Burden drivers: ${DRIVER_CODES.filter((d) => on.has(d)).join(", ")}`
    : "No burden drivers recorded";
  return (
    <span className={`strip ${positive ? "strip-pos" : ""}`} title={label} aria-label={label}>
      {DRIVER_CODES.map((d) => (
        <i key={d} className={on.has(d) ? "on" : undefined} />
      ))}
    </span>
  );
}

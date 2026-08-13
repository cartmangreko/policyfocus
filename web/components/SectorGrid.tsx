import Link from "next/link";
import { getSectorCounts } from "@/lib/data";

// gap:1px over a rule-soft ground so the cells read as a hairline grid.
export default function SectorGrid() {
  return (
    <div className="hairline-grid sector-grid">
      {getSectorCounts().map((s) => (
        <Link key={s.slug} href={`/sectors/${s.slug}`} className="sector-cell">
          <span className="sector-name">{s.name}</span>
          <span className="sector-count">{s.count}</span>
        </Link>
      ))}
    </div>
  );
}

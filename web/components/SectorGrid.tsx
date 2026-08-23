import Link from "next/link";
import { getSectorCounts } from "@/lib/data";
import { hasMap } from "@/lib/transition";

// gap:1px over a rule-soft ground so the cells read as a hairline grid.
//
// A SECTOR WITH A MAP LEADS, and says so. The grid used to be twenty cells
// ordered by measure count, which is a fact about how much of the register
// happens to point at a sector rather than about the sector. The ones with a
// transition map behind them are a different page and are marked as such; the
// rest keep the count, because it is what they have.
export default function SectorGrid() {
  const rows = getSectorCounts()
    .map((s) => ({ ...s, mapped: hasMap(s.slug) }))
    .sort((a, b) => Number(b.mapped) - Number(a.mapped) || b.count - a.count);
  return (
    <div className="hairline-grid sector-grid">
      {rows.map((s) => (
        <Link key={s.slug} href={`/sectors/${s.slug}`} className="sector-cell">
          <span className="sector-name">{s.name}</span>
          {s.mapped ? (
            <span className="sector-mapped">transition map</span>
          ) : (
            <span className="sector-count">{s.count}</span>
          )}
        </Link>
      ))}
    </div>
  );
}

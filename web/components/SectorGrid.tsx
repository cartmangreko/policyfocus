import Link from "next/link";
import { getSectorCounts } from "@/lib/data";
import { hasMap } from "@/lib/transition";

// gap:1px over a rule-soft ground so the cells read as a hairline grid.
//
// A SECTOR THAT IS LIVE LEADS, and says so. The grid used to be twenty cells
// ordered by measure count, which is a fact about how much of the register
// happens to point at a sector rather than about the sector.
//
// AND THE OTHER NINETEEN NOW SAY NOTHING BUT THEIR NAME. They used to keep the
// count, on the argument that it was what they had. It was not: a count of
// measures reaching a sector is the old product's headline figure, and putting
// it on nineteen of twenty tiles made the home page an inventory with one
// exception on it. What a sector without its own page actually has to say is
// that it is coming, so that is what it says. The ordering that used to be by
// count is now alphabetical within each group, because there is no longer a
// number to order by and inventing one would be the same mistake indoors.
export default function SectorGrid() {
  const rows = getSectorCounts()
    .map((s) => ({ ...s, live: hasMap(s.slug) }))
    .sort(
      (a, b) => Number(b.live) - Number(a.live) || a.name.localeCompare(b.name),
    );
  return (
    <div className="hairline-grid sector-grid">
      {rows.map((s) => (
        <Link key={s.slug} href={`/sectors/${s.slug}`} className="sector-cell">
          <span className="sector-name">{s.name}</span>
          {s.live ? (
            <span className="sector-live">Live</span>
          ) : (
            <span className="sector-pending">In preparation</span>
          )}
        </Link>
      ))}
    </div>
  );
}

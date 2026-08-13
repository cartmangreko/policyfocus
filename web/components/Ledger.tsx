import { getClassLedger } from "@/lib/data";

// Diverging bars on a centred axis: relief runs left (pine), new burden runs
// right (claret). Both halves share one scale — the widest single count sets
// 50% of the track — so a bar's length is comparable across rows and sides.
export default function Ledger({ caption }: { caption: string }) {
  const rows = getClassLedger();
  const max = Math.max(1, ...rows.flatMap((r) => [r.added, r.removed]));

  return (
    <div className="card ledger-card">
      <div className="card-label">{caption}</div>
      <div className="ledger">
        {rows.map((r) => (
          <div key={r.cls} className="led-row">
            <div className="led-name">{r.label}</div>
            <div className="led-track">
              <span className="led-axis" />
              {r.removed > 0 && (
                <span className="led-bar led-rem" style={{ width: `${(r.removed / max) * 50}%` }}>
                  <span className="led-count">{r.removed}</span>
                </span>
              )}
              {r.added > 0 && (
                <span className="led-bar led-add" style={{ width: `${(r.added / max) * 50}%` }}>
                  <span className="led-count">{r.added}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="legend">
        <span className="legend-item">
          <i className="swatch swatch-add" />
          Duties added or widened
        </span>
        <span className="legend-item">
          <i className="swatch swatch-rem" />
          Duties removed, merged or waived
        </span>
      </div>
    </div>
  );
}

import { DRIVER_CODES, getDriverFrequency } from "@/lib/data";

export default function DriverChart() {
  const counts = getDriverFrequency();
  const max = Math.max(1, ...DRIVER_CODES.map((d) => counts[d]));

  return (
    <div className="card">
      <div className="card-label">Burden drivers — frequency</div>
      <p className="card-note">
        Seven yes-or-no marks read off each provision. How often each one fires across the corpus.
      </p>
      <div className="dchart">
        {DRIVER_CODES.map((d) => (
          <div key={d} className="dchart-col">
            <span className="dchart-count">{counts[d]}</span>
            <div className="dchart-bar" style={{ height: `${(counts[d] / max) * 100}%` }} />
          </div>
        ))}
      </div>
      <div className="dchart-axis">
        {DRIVER_CODES.map((d) => (
          <span key={d}>{d}</span>
        ))}
      </div>
    </div>
  );
}

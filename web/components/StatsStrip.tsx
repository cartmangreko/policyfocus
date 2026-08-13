export interface Stat {
  value: string;
  suffix?: string;
  label: string;
  tone?: "add" | "rem";
}

export default function StatsStrip({ stats, id }: { stats: Stat[]; id?: string }) {
  return (
    <div className="stats" id={id}>
      {stats.map((s) => (
        <div key={s.label} className="stat">
          <div className={`stat-value ${s.tone ? `stat-${s.tone}` : ""}`}>
            {s.value}
            {s.suffix && <span className="stat-suffix">{s.suffix}</span>}
          </div>
          <div className="stat-label">{s.label}</div>
        </div>
      ))}
    </div>
  );
}

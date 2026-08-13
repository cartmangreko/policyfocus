import { FILES, getTickerItems } from "@/lib/data";

// The marquee duplicates its content once so translateX(-50%) loops seamlessly.
// The copy is aria-hidden; the first pass carries the accessible text.
function Run({ hidden }: { hidden?: boolean }) {
  const items = getTickerItems();
  return (
    <span className="ticker-run" aria-hidden={hidden || undefined}>
      <span className="ticker-item">
        {FILES.omnibus.name} — {FILES.omnibus.code}
      </span>
      {items.map((it, i) => (
        <span key={i}>
          <span className={`ticker-flag ${it.positive ? "is-pos" : "is-neg"}`}>▸ {it.label}</span>
          <span className="ticker-item">{it.text}</span>
        </span>
      ))}
    </span>
  );
}

export default function Ticker() {
  return (
    <div className="ticker">
      <div className="ticker-live">
        <span className="ticker-dot" />
        LIVE
      </div>
      <div className="ticker-track">
        <div className="ticker-scroll">
          <Run />
          <Run hidden />
        </div>
      </div>
    </div>
  );
}

import type { SummaryCuts } from "@/lib/summaries";

// Renders one summary object, dumbly. Every number here was computed and
// verified by sources/build_summaries.py; this component adds words, never
// arithmetic. The same three cuts render on every node — sector, act, site —
// so the strip reads the same wherever a reader meets it.
//
// Neutral rows print as their own small "unchanged" count and are never
// folded into burden or benefit; weight does not appear at all (it stays on
// the rows). Both rules belong to the generator — see its module docstring.

const CHANNEL_LABEL: Record<string, string> = {
  supply_chain: "supply chain",
  procurement: "procurement",
  regulatory_dependency: "regulatory dependency",
};

function join(parts: Array<string | null>): string {
  return parts.filter((p): p is string => p !== null).join(" · ");
}

export default function SummaryStrip({
  cuts,
  variant = "full",
}: {
  cuts: SummaryCuts;
  variant?: "full" | "mini";
}) {
  const { direction: d, status: s, channel: c } = cuts;

  const directionLine = join([
    `${d.burden} burden`,
    `${d.benefit} benefit`,
    d.unchanged > 0 ? `${d.unchanged} unchanged` : null,
  ]);
  const statusLine = join([
    s.adopted > 0 ? `${s.adopted} adopted` : null,
    s.proposed > 0 ? `${s.proposed} proposed` : null,
    s.mixed > 0 ? `${s.mixed} mixed` : null,
  ]);
  const channelLine = join([
    `${c.direct} direct`,
    `${c.reached} reached`,
    c.no_sector > 0 ? `${c.no_sector} no sector` : null,
  ]);
  const perChannel = join(
    Object.entries(c.reached_by_channel)
      .filter(([, n]) => n > 0)
      .map(([k, n]) => `${CHANNEL_LABEL[k] ?? k} ${n}`)
  );

  if (variant === "mini") {
    return (
      <p className="summary-mini">
        {directionLine} <span className="summary-mini-sep">|</span> {channelLine}
      </p>
    );
  }

  return (
    <div className="summary-strip">
      <div className="summary-cell">
        <div className="summary-cell-label">Direction</div>
        <div className="summary-cell-value">
          <span className="summary-neg">{d.burden}</span> burden ·{" "}
          <span className="summary-pos">{d.benefit}</span> benefit
        </div>
        {d.unchanged > 0 && (
          <div className="summary-cell-sub">{d.unchanged} unchanged — counted in neither</div>
        )}
      </div>
      <div className="summary-cell">
        <div className="summary-cell-label">Status</div>
        <div className="summary-cell-value">{statusLine || "—"}</div>
      </div>
      <div className="summary-cell">
        <div className="summary-cell-label">Channel</div>
        <div className="summary-cell-value">{channelLine}</div>
        {c.reached > 0 && perChannel && (
          <div className="summary-cell-sub">reached via {perChannel}</div>
        )}
      </div>
    </div>
  );
}

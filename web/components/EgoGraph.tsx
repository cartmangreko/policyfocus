"use client";

import { useState } from "react";
import type { EgoSpoke, EgoView } from "@/lib/ego";

// One act's neighbourhood, drawn radially: the act at the centre, every
// connection the builder aggregated as a spoke. The layout is a pure function
// of the view — spokes keep the builder's group order, angles are evenly
// spaced from twelve o'clock — so the same data always draws the same
// picture: no force simulation, no randomness, no layout drift between
// builds. Labels, counts and detail strings all come from
// data/graph/ego/<file>.json; this component draws and composes nothing.
//
// Above the cap, the picture shows the highest-weight connections and says
// so: the "Show all" control is the only state here, and hiding is never
// silent — the button carries the full count.

const CAP = 12;

interface Placed {
  spoke: EgoSpoke;
  rel: string;
  x: number;
  y: number;
  labelX: number;
  labelY: number;
  anchor: "start" | "middle" | "end";
}

function truncate(text: string, max = 26): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function layout(spokes: { spoke: EgoSpoke; rel: string }[], cx: number, cy: number, r: number): Placed[] {
  const n = spokes.length;
  return spokes.map(({ spoke, rel }, i) => {
    const angle = (-90 + (360 * i) / n) * (Math.PI / 180);
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    // Crowded rings stagger the label distance so neighbours at the top and
    // bottom do not overprint each other. Deterministic: parity of the index.
    const pad = 16 + (n > 14 ? (i % 2) * 30 : 0);
    return {
      spoke,
      rel,
      x: cx + r * cos,
      y: cy + r * sin,
      labelX: cx + (r + pad) * cos,
      labelY: cy + (r + pad) * sin,
      anchor: cos > 0.25 ? "start" : cos < -0.25 ? "end" : "middle",
    };
  });
}

export default function EgoGraph({ view, centerLabel }: { view: EgoView; centerLabel: string }) {
  const [showAll, setShowAll] = useState(false);

  const all = view.groups.flatMap((g) => g.spokes.map((spoke) => ({ spoke, rel: g.rel })));
  const capped = all.length > CAP && !showAll;
  let shown = all;
  if (capped) {
    const kept = new Set(
      [...all]
        .sort(
          (a, b) =>
            b.spoke.weight - a.spoke.weight ||
            a.spoke.label.localeCompare(b.spoke.label) ||
            a.spoke.id.localeCompare(b.spoke.id)
        )
        .slice(0, CAP)
        .map((s) => s.spoke.id)
    );
    shown = all.filter((s) => kept.has(s.spoke.id));
  }

  const cx = 340;
  const cy = 250;
  const placed = layout(shown, cx, cy, 145);

  return (
    <figure className="ego">
      <svg
        viewBox="0 0 680 500"
        className="ego-svg"
        role="img"
        aria-label={`${centerLabel}: ${all.length} connections in the graph`}
      >
        {placed.map((p) => (
          <line key={`l-${p.spoke.id}`} x1={cx} y1={cy} x2={p.x} y2={p.y} className={`ego-line ego-${p.rel}`} />
        ))}
        {placed.map((p) => {
          const detailLines = p.spoke.detail.split(" · ");
          const node = (
            <g key={`n-${p.spoke.id}`} className="ego-spoke">
              <circle cx={p.x} cy={p.y} r={4} className={`ego-dot ego-${p.rel}`} />
              <text x={p.labelX} y={p.labelY} textAnchor={p.anchor} className="ego-label">
                <title>{p.spoke.label}</title>
                {truncate(p.spoke.label)}
              </text>
              {detailLines.map((line, j) => (
                <text
                  key={j}
                  x={p.labelX}
                  y={p.labelY + 12 + j * 11}
                  textAnchor={p.anchor}
                  className="ego-detail"
                >
                  {line}
                </text>
              ))}
            </g>
          );
          return p.spoke.href ? (
            <a key={`a-${p.spoke.id}`} href={p.spoke.href} className="ego-link">
              {node}
            </a>
          ) : (
            node
          );
        })}
        <g>
          <circle cx={cx} cy={cy} r={7} className="ego-center-dot" />
          <text x={cx} y={cy + 26} textAnchor="middle" className="ego-center-label">
            {truncate(centerLabel, 34)}
          </text>
          <text x={cx} y={cy + 40} textAnchor="middle" className="ego-detail">
            {view.measure_count} measures
          </text>
        </g>
      </svg>

      <div className="ego-legend">
        {view.groups.map((g) => (
          <span key={g.rel} className="ego-legend-item">
            <span className={`ego-swatch ego-${g.rel}`} aria-hidden="true" />
            {g.title} ({g.spokes.length})
          </span>
        ))}
      </div>

      {all.length > CAP && (
        <button type="button" className="ego-toggle" onClick={() => setShowAll(!showAll)}>
          {showAll
            ? `Show the ${CAP} strongest connections`
            : `Show all ${all.length} connections`}
        </button>
      )}

      {view.note && <figcaption className="ego-note">{view.note}</figcaption>}
    </figure>
  );
}

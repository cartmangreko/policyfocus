"use client";

import { useMemo, useRef, useState } from "react";

// The sector diagram. It draws data/transition/diagrams/<sector>.json and adds
// exactly two things the data cannot carry: hover, and a way to take the
// picture away with you.
//
// NO LAYOUT HERE. Every coordinate comes from sources/build_sector_diagram.py,
// so the picture is identical for every reader, reviewable in a diff, and the
// same in the export as on the page. A component that laid out its own nodes
// would make the argument a function of the browser.
//
// ONE HUE PER NODE KIND, and they are the site's own accents rather than a
// palette invented here: claret for the law, ochre for what is blocking,
// pine for the route past it, blue for the thing actually being built. Edges
// take the hue of the relation, which is why worsens and relieves read apart
// at a glance even before the arrowhead is legible.

export interface DiagramNode {
  id: string;
  kind: "measure" | "bottleneck" | "technology" | "project";
  label: string;
  sub: string;
  href: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DiagramEdge {
  from: string;
  to: string;
  rel: "worsens" | "relieves" | "addresses" | "deploys";
  weight: number;
}

export interface Diagram {
  sector: string;
  width: number;
  height: number;
  columns: { kind: string; x: number; count: number }[];
  nodes: DiagramNode[];
  edges: DiagramEdge[];
}

export interface NodeSource {
  url: string;
  title?: string;
  publisher: string;
}

const KIND_HUE: Record<DiagramNode["kind"], string> = {
  measure: "var(--claret)",
  bottleneck: "var(--ochre)",
  technology: "var(--pine)",
  project: "var(--focus)",
};

const KIND_LABEL: Record<string, string> = {
  measure: "Measures",
  bottleneck: "Bottlenecks",
  technology: "Technologies",
  project: "Projects",
};

const REL_HUE: Record<DiagramEdge["rel"], string> = {
  worsens: "var(--claret)",
  relieves: "var(--pine)",
  addresses: "var(--ochre)",
  deploys: "var(--focus)",
};

// Entry motion: the columns arrive left to right, and the whole sequence is
// over inside 600ms. It exists to show the reading order once; anything longer
// would be the page performing rather than explaining.
const STAGGER_MS = 45;
const MAX_DELAY_MS = 320;

function edgePath(a: DiagramNode, b: DiagramNode) {
  const forward = a.x < b.x;
  const x1 = forward ? a.x + a.w : a.x;
  const x2 = forward ? b.x : b.x + b.w;
  const y1 = a.y + a.h / 2;
  const y2 = b.y + b.h / 2;
  const dx = Math.max(40, Math.abs(x2 - x1) * 0.45) * (forward ? 1 : -1);
  return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
}

export default function TransitionDiagram({
  diagram,
  sources,
  pageUrl,
}: {
  diagram: Diagram;
  sources: Record<string, NodeSource[]>;
  pageUrl: string;
}) {
  const [active, setActive] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const byId = useMemo(
    () => new Map(diagram.nodes.map((n) => [n.id, n])),
    [diagram.nodes],
  );
  const incident = useMemo(() => {
    const m = new Map<string, Set<string>>();
    for (const n of diagram.nodes) m.set(n.id, new Set([n.id]));
    for (const e of diagram.edges) {
      m.get(e.from)?.add(e.to);
      m.get(e.to)?.add(e.from);
    }
    return m;
  }, [diagram]);

  const lit = active ? incident.get(active) ?? new Set<string>() : null;
  const activeNode = active ? byId.get(active) : undefined;
  const activeSources = active ? sources[active] ?? [] : [];

  function download() {
    const svg = svgRef.current;
    if (!svg) return;
    const clone = svg.cloneNode(true) as SVGSVGElement;
    // The exported file has to stand on its own: the page's CSS variables do
    // not travel with it, and neither does the address it came from. So the
    // type rules are inlined as a real stylesheet inside the file, and the
    // hues, which are variables on the page, are resolved to literals.
    const style = document.createElementNS("http://www.w3.org/2000/svg", "style");
    style.textContent = EXPORT_CSS;
    clone.insertBefore(style, clone.firstChild);
    const computed = getComputedStyle(document.documentElement);
    clone.querySelectorAll<SVGElement>("[fill],[stroke]").forEach((el) => {
      for (const attr of ["fill", "stroke"] as const) {
        const v = el.getAttribute(attr);
        const m = v?.match(/^var\((--[\w-]+)\)$/);
        if (m) el.setAttribute(attr, computed.getPropertyValue(m[1]).trim() || "#14171c");
      }
    });
    const caption = document.createElementNS("http://www.w3.org/2000/svg", "text");
    caption.setAttribute("x", "12");
    caption.setAttribute("y", String(diagram.height + 26));
    caption.setAttribute("font-size", "13");
    caption.setAttribute("fill", "#5a5f68");
    caption.setAttribute("font-family", "IBM Plex Mono, monospace");
    caption.textContent = `PolicyFocus · ${diagram.sector} transition map · ${pageUrl}`;
    clone.appendChild(caption);
    clone.setAttribute("viewBox", `0 0 ${diagram.width} ${diagram.height + 40}`);
    const blob = new Blob([new XMLSerializer().serializeToString(clone)], {
      type: "image/svg+xml;charset=utf-8",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `policyfocus-${diagram.sector}-transition-map.svg`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return (
    <figure className="tdiagram" onMouseLeave={() => setActive(null)}>
      <div className="tdiagram-head">
        <ul className="tdiagram-key">
          {diagram.columns.map((c) => (
            <li key={c.kind}>
              <span className="swatch" style={{ background: KIND_HUE[c.kind as DiagramNode["kind"]] }} />
              {KIND_LABEL[c.kind]} <span className="count">{c.count}</span>
            </li>
          ))}
        </ul>
        <button type="button" className="tdiagram-export" onClick={download}>
          Save as SVG
        </button>
      </div>

      <div className="tdiagram-scroll">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${diagram.width} ${diagram.height}`}
          width={diagram.width}
          height={diagram.height}
          role="img"
          aria-label={`${diagram.sector}: measures, bottlenecks, technologies and projects, and how they connect`}
        >
          <defs>
            {Object.entries(REL_HUE).map(([rel, hue]) => (
              <marker
                key={rel}
                id={`arrow-${rel}`}
                viewBox="0 0 8 8"
                refX="7"
                refY="4"
                markerWidth="7"
                markerHeight="7"
                orient="auto-start-reverse"
              >
                <path d="M 0 1 L 7 4 L 0 7 z" fill={hue} />
              </marker>
            ))}
          </defs>

          <g className="tdiagram-edges">
            {diagram.edges.map((e, i) => {
              const a = byId.get(e.from);
              const b = byId.get(e.to);
              if (!a || !b) return null;
              const on = !lit || (lit.has(e.from) && lit.has(e.to));
              return (
                <path
                  key={`${e.from}->${e.to}-${e.rel}`}
                  d={edgePath(a, b)}
                  fill="none"
                  stroke={REL_HUE[e.rel]}
                  strokeWidth={e.weight >= 1 ? 1.6 : 1}
                  strokeDasharray={e.weight < 1 ? "4 3" : undefined}
                  markerEnd={`url(#arrow-${e.rel})`}
                  className="tedge"
                  opacity={on ? 0.85 : 0.08}
                  style={{ animationDelay: `${Math.min(i * 12, MAX_DELAY_MS)}ms` }}
                />
              );
            })}
          </g>

          <g className="tdiagram-nodes">
            {diagram.nodes.map((n, i) => {
              const on = !lit || lit.has(n.id);
              const hue = KIND_HUE[n.kind];
              return (
                <a
                  key={n.id}
                  href={n.href}
                  className="tnode"
                  onMouseEnter={() => setActive(n.id)}
                  onFocus={() => setActive(n.id)}
                  style={{
                    opacity: on ? 1 : 0.22,
                    animationDelay: `${Math.min(i * STAGGER_MS, MAX_DELAY_MS)}ms`,
                  }}
                >
                  <rect
                    x={n.x}
                    y={n.y}
                    width={n.w}
                    height={n.h}
                    rx="2"
                    fill="var(--card)"
                    stroke={active === n.id ? hue : "var(--rule)"}
                    strokeWidth={active === n.id ? 1.8 : 1}
                  />
                  <rect x={n.x} y={n.y} width="3" height={n.h} fill={hue} />
                  <text x={n.x + 12} y={n.y + 16} className="tnode-label">
                    {n.label.length > 30 ? `${n.label.slice(0, 29)}…` : n.label}
                  </text>
                  <text x={n.x + 12} y={n.y + 29} className="tnode-sub">
                    {n.sub}
                  </text>
                </a>
              );
            })}
          </g>
        </svg>
      </div>

      <figcaption className="tdiagram-caption">
        {activeNode ? (
          <div className="tdiagram-detail">
            <strong>{activeNode.label}</strong> <span className="kind">{activeNode.kind}</span>
            {activeSources.length > 0 ? (
              <ul>
                {activeSources.map((s) => (
                  <li key={s.url}>
                    <a href={s.url} target="_blank" rel="noreferrer">
                      {s.title ?? s.url}
                    </a>{" "}
                    <span className="pub">{s.publisher}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">Sources are on the node&rsquo;s own page.</p>
            )}
          </div>
        ) : (
          <p className="muted">
            Hover a node to light its edges and list its sources. Click one to open it.
            Solid lines carry full weight, dashed lines half.
          </p>
        )}
      </figcaption>
    </figure>
  );
}

// Inlined into the exported file only. The page itself is styled from
// globals.css; this exists because an SVG saved to disk has no stylesheet.
const EXPORT_CSS = [
  ".tnode-label{font:500 12px 'Public Sans',system-ui,sans-serif;fill:#14171c}",
  ".tnode-sub{font:11px 'IBM Plex Mono',monospace;fill:#5a5f68}",
  "a{text-decoration:none}",
].join("");

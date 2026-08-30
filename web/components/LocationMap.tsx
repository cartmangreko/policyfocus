import Link from "next/link";
import { geoKeyProse, geoMarkProse } from "@/lib/prose";

// THE SHARED GEOGRAPHY COMPONENT. One picture, two frames: a regional crop on a
// project page and a Europe-wide overview on a sector page. Both are the same
// component drawing the same file shape, because two components would drift and
// a reader would learn the picture twice.
//
// NO LAYOUT HERE, the same rule the sector diagram works under. Every
// coordinate, every path and the frame itself come from sources/build_maps.py,
// so the picture is identical for every reader, reviewable in a diff, and does
// not make a 5 MB shapefile the browser's problem. This file draws what it is
// given and adds a link.
//
// INK ONLY, AND NO FILL ON LAND. The four colour layers are: signal is chrome,
// claret and pine are money direction, the diagram palette is for diagrams and
// the sector accent is page identity and is explicitly never on a figure. None
// of those is what a coastline is. So the ground is paper, the lines are ink,
// and the marks are told apart by SHAPE rather than by hue — which also means
// this file names no reserved token and needs no entry in the colour gate's
// inline allowance.
//
// ONE RULE FOR THE MARKS, AND IT IS NOT COLOUR:
//
//     dot        a works
//     triangle   a store, pointing down, because that is where the tonne goes
//     filled     it is running
//     hollow     it is not — paused, cancelled, or not yet built
//     ring       the one this page is about
//
// AND THE GROUND IS NAMED UNDER ALL OF IT. A crop names every country in view,
// an overview only those holding a site. They are the faintest layer and the
// subordinate one: placed after the site labels, against boxes those have
// already taken, and DROPPED rather than moved on top of a name that matters
// more. Internal borders were already drawn — every country ring carries its
// land boundaries as well as its coast — so no border layer was added.
//
// EVERY MARK IS NAMED ON THE PAPER. The label is not a tooltip: a tooltip needs
// a pointer, and this picture is read on phones, in print and in screenshots.
// Where labels would collide they are offset and joined to their mark by a
// leader; where a crowd leaves no room at all the company drops to the tooltip
// and the name stays, because a label that is never drawn is a name the reader
// cannot know was there. All of that is decided in build_maps.py.
//
// A third mark for transport infrastructure is described in the brief and is
// not drawn, because no such node exists: every named hub in the register is
// named without being sited. See scope.md, "A node in the geo layer requires a
// source-stated position".

export interface MapLabelLine {
  text: string;
  role: "name" | "company";
  size: number;
  y: number;
}

export interface MapLabel {
  x: number;
  anchor: "start" | "middle" | "end";
  lines: MapLabelLine[];
  leader?: [number, number, number, number];
  shortened?: boolean;
  crowded?: boolean;
}

export interface MapMark {
  id: string;
  site: string;
  role: "plant" | "storage";
  relation: "subject" | "dependency" | "technology" | "sector";
  status: string;
  label: string;
  sub: string;
  href: string;
  lat: number;
  lon: number;
  as_of: string;
  x: number;
  y: number;
  labels: { wide: MapLabel; narrow: MapLabel };
}

export interface MapCountry {
  iso: string;
  text: string;
  labels: { wide?: MapLabel; narrow?: MapLabel };
}

export interface MapCoordinates {
  site: string;
  lat?: number;
  lon?: number;
  north?: number;
  south?: number;
  east?: number;
  west?: number;
  as_of: string;
}

export interface MapDoc {
  id: string;
  kind: "project" | "sector";
  subject: string;
  canvas: { width: number; height: number };
  mark_geometry: { r: number; store_scale: number; ring_scale: number };
  land: string[];
  marks: MapMark[];
  countries: MapCountry[];
  coordinates: MapCoordinates[];
  as_of: string;
}

/** Running, in the sense the mark uses: a filled mark is a thing that is doing
 *  something. `funded` and `fid` are decisions and not yet plant, so they are
 *  hollow — the same reading build_lead.py's ADVANCE ladder takes. */
const RUNNING = new Set(["construction", "operating"]);

type Geometry = MapDoc["mark_geometry"];

function shape(mark: MapMark, g: Geometry) {
  const filled = RUNNING.has(mark.status);
  const common = {
    className: `geo-mark geo-mark-${mark.role} ${filled ? "is-running" : "is-stopped"}`,
    vectorEffect: "non-scaling-stroke" as const,
  };
  if (mark.role === "storage") {
    const r = g.r * g.store_scale;
    const points = `${mark.x},${mark.y + r} ${mark.x - r},${mark.y - r * 0.72} ${
      mark.x + r
    },${mark.y - r * 0.72}`;
    return <polygon points={points} {...common} />;
  }
  return <circle cx={mark.x} cy={mark.y} r={g.r} {...common} />;
}

/** ONE MARK'S LABEL, AT ONE BREAKPOINT. Every number here was computed by
 *  sources/build_maps.py — the anchor, the baseline of each line, and the leader
 *  when the label had to be pushed clear of a neighbour. Both breakpoints are
 *  rendered and the stylesheet shows one, because the label that fits a 760px
 *  canvas is unreadable on a 390px one and the file carries a layout for each. */
function label(mark: MapMark, which: "wide" | "narrow") {
  const l = mark.labels[which];
  return (
    <g className={`geo-label geo-label-${which}`}>
      {l.leader ? (
        <line
          x1={l.leader[0]}
          y1={l.leader[1]}
          x2={l.leader[2]}
          y2={l.leader[3]}
          className="geo-leader"
          vectorEffect="non-scaling-stroke"
        />
      ) : null}
      {l.lines.map((line, i) => (
        <text
          key={i}
          x={l.x}
          y={line.y}
          fontSize={line.size}
          textAnchor={l.anchor}
          className={`geo-label-text geo-label-${line.role}`}
        >
          {line.text}
        </text>
      ))}
    </g>
  );
}

/** THE GROUND'S NAME, at one breakpoint, or nothing where the placement could
 *  not fit it. Drawn before the marks and before their labels, so it is under
 *  them on the paper as well as in the ordering: a country name never covers a
 *  site name, and build_maps.py has already dropped any that would have. */
function countryLabel(country: MapCountry, which: "wide" | "narrow") {
  const l = country.labels[which];
  if (!l) return null;
  return (
    <g className={`geo-country geo-label-${which}`}>
      {l.lines.map((line, i) => (
        <text
          key={i}
          x={l.x}
          y={line.y}
          fontSize={line.size}
          textAnchor={l.anchor}
          className="geo-label-text geo-country-text"
        >
          {line.text}
        </text>
      ))}
    </g>
  );
}

/** Degrees as a reader writes them, not as the file stores them: a hemisphere
 *  letter rather than a minus sign, because "-9.7" is a value and "9.7 W" is a
 *  place. Four decimals is roughly eleven metres, which is the precision the
 *  register actually claims. */
function degrees(value: number, axis: "lat" | "lon") {
  const hemisphere = axis === "lat" ? (value < 0 ? "S" : "N") : value < 0 ? "W" : "E";
  return `${Math.abs(value).toFixed(4)}° ${hemisphere}`;
}

function coordinateLine(c: MapCoordinates) {
  if (c.lat !== undefined && c.lon !== undefined) {
    return `${degrees(c.lat, "lat")}  ${degrees(c.lon, "lon")}`;
  }
  return (
    `${degrees(c.south ?? 0, "lat")}–${degrees(c.north ?? 0, "lat")}  ` +
    `${degrees(c.west ?? 0, "lon")}–${degrees(c.east ?? 0, "lon")}`
  );
}

/** The key's swatch, drawn at the same proportions the picture uses so that the
 *  thing in the key is the thing on the paper. */
function swatch(item: { role: "plant" | "storage"; running: boolean }) {
  const cls = `geo-mark geo-mark-${item.role} ${item.running ? "is-running" : "is-stopped"}`;
  return (
    <svg viewBox="0 0 12 12" aria-hidden="true">
      {item.role === "storage" ? (
        <polygon points="6,10.5 1.2,3.2 10.8,3.2" className={cls} />
      ) : (
        <circle cx="6" cy="6" r="4" className={cls} />
      )}
    </svg>
  );
}

export default function LocationMap({
  doc,
  heading,
  standfirst,
}: {
  doc: MapDoc;
  heading: string;
  standfirst: string;
}) {
  const { width, height } = doc.canvas;
  const g = doc.mark_geometry;
  const hasStore = doc.marks.some((m) => m.role === "storage");

  return (
    <figure className={`geo geo-${doc.kind}`} aria-labelledby={`${doc.id}-heading`}>
      <figcaption className="geo-caption">
        <h3 id={`${doc.id}-heading`}>{heading}</h3>
        <p className="geo-standfirst">{standfirst}</p>
      </figcaption>

      <svg
        className="geo-canvas"
        viewBox={`0 0 ${width} ${height}`}
        role="group"
        aria-label={standfirst}
      >
        <g className="geo-land-group">
          {doc.land.map((d, i) => (
            <path key={i} d={d} className="geo-land" vectorEffect="non-scaling-stroke" />
          ))}
        </g>
        <g className="geo-country-group">
          {doc.countries.map((country) => (
            <g key={country.iso}>
              {countryLabel(country, "wide")}
              {countryLabel(country, "narrow")}
            </g>
          ))}
        </g>
        {doc.marks.map((mark) => (
          <Link
            key={`${mark.id}::${mark.site}`}
            href={mark.href}
            className={`geo-link geo-rel-${mark.relation}`}
          >
            <title>
              {geoMarkProse({
                label: mark.label,
                sub: mark.sub,
                site: mark.site,
                coordinates: `${degrees(mark.lat, "lat")} ${degrees(mark.lon, "lon")}`,
              })}
            </title>
            {mark.relation === "subject" ? (
              <circle
                cx={mark.x}
                cy={mark.y}
                r={g.r * g.ring_scale}
                className="geo-here"
                vectorEffect="non-scaling-stroke"
              />
            ) : null}
            {shape(mark, g)}
            {label(mark, "wide")}
            {label(mark, "narrow")}
          </Link>
        ))}
      </svg>

      <div className="geo-key">
        {geoKeyProse({ hasStore }).map((item) => (
          <span className="geo-key-item" key={item.text}>
            {swatch(item)}
            {item.text}
          </span>
        ))}
      </div>

      <div className="geo-coords">
        {doc.coordinates.map((c) => (
          <p key={c.site}>
            <span className="geo-coord">{coordinateLine(c)}</span>
            <span className="geo-site">{c.site}</span>
          </p>
        ))}
        <p className="geo-asof">as of {doc.as_of}</p>
      </div>
    </figure>
  );
}

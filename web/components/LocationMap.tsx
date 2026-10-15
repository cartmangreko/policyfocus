import Link from "next/link";
import { SEPARATOR } from "@/lib/citation";
import { geoClusterProse, geoKeyProse, geoMarkProse, type UndrawnRow } from "@/lib/prose";

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
//     hollow     it is not — announced, funded, or paused
//     ring       the one this page is about
//
// AND WHAT IS NOT DRAWN AT ALL. A cancelled project is off the overview and is
// not a context mark on anybody else's crop, because the picture draws what
// Europe is building. It keeps its row, its page and its place in every count;
// it is drawn on its own crop and on no other frame. sources/build_maps.py
// decides that, in UNDRAWN_STATUSES, and this file is handed the result — but
// the KEY has to say it, because a hollow mark drawn nowhere else looks like
// every other hollow mark. See geoKeyProse.
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
  /** The ISO code of the country this site stands in. The overview's standfirst
   *  counts countries off this rather than off the project rows, so that the
   *  number is over sites the frame draws. */
  country: string;
  role: "plant" | "storage";
  relation: "subject" | "dependency" | "technology" | "sector";
  status: string;
  label: string;
  sub: string;
  href: string;
  lat: number;
  lon: number;
  /** The works this mark is actually on, where that is not the installation
   *  itself — an electrolyser inside a refinery is placed on the refinery. Null
   *  where the polygon is the installation's own. The standfirst counts these,
   *  because a dot looks the same either way. */
  host_works: string | null;
  as_of: string;
  x: number;
  y: number;
  labels: { wide: MapLabel; narrow: MapLabel };
  /** THE OTHER DESTINATION. `href` is the project's own page and is what a crop
   *  and a country view send a reader to. On the continental overview a marker
   *  opens the country view instead (brief 16 §2), because the overview's next
   *  question is "what is this country building" and the answer is a page rather
   *  than a dot. Both are on the file so the component chooses by the kind of
   *  picture it is drawing, and neither is composed here. */
  country_href?: string;
  /** Whether a cluster marker stands in for this mark on the overview. The mark
   *  stays in the file — it is what the counts, the legend and the gate are
   *  computed over — and is not drawn. */
  clustered?: boolean;
}

/** A GROUP OF DRAWN SITES WITHIN `radius_km` OF EACH OTHER, standing in for its
 *  members on the continental overview. Neutral ink and a count, by ruling: four
 *  sites at one place are rarely all in one status, and a marker taking the fill
 *  of whichever sorted first would assert a state for the other three. */
export interface MapCluster {
  key: string;
  country: string;
  x: number;
  y: number;
  count: number;
  projects: string[];
  sites: { id: string; site: string; status: string }[];
  href: string;
}

/** The legend under the overview: every country holding a drawn site, what it
 *  holds, and the link to its own view. */
export interface MapCountryTotal {
  iso: string;
  text: string;
  sites: number;
  projects: number;
  href: string;
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
  /** THREE KINDS OF PICTURE, one component. `project` is a regional crop,
   *  `sector` the fixed continental overview, and `country` — brief 16 §3 — one
   *  country's own frame with every one of its dots drawn unclustered. */
  kind: "project" | "sector" | "country";
  subject: string;
  canvas: { width: number; height: number };
  mark_geometry: { r: number; store_scale: number; ring_scale: number };
  land: string[];
  marks: MapMark[];
  countries: MapCountry[];
  coordinates: MapCoordinates[];
  as_of: string;
  /** Overview only: the register's remainder — what this sector has on file and
   *  this frame does not draw. The standfirst states it in a clause of its own. */
  undrawn?: { projects: number; sites: number; rows?: UndrawnRow[] };
  /** Crop only: the subject's status, so the key can name the one case the two
   *  fill lines do not cover. */
  subject_status?: string;
  /** Overview only: the clustering sources/build_maps.py applied, and the
   *  markers it produced. Absent on a crop and on a country view, neither of
   *  which clusters anything. */
  clusters?: { radius_km: number; groups: MapCluster[]; singles: number; clustered_sites: number };
  /** Overview only: the country legend. */
  country_totals?: MapCountryTotal[];
  /** Country view only. */
  country?: string;
  sector?: string;
  /** WHAT THE GROUND IS DRAWN FROM, and when the copy on file was taken. The
   *  second half of the as-of stamp: `as_of` dates the marks, this dates the
   *  land under them, and neither is the build's own date. Read from
   *  data/geo/SOURCE.json by build_maps.py — see basemap() there. */
  basemap?: {
    title: string;
    publisher: string;
    version: string;
    retrieved_date: string;
    licence: string;
    url: string;
  };
}

/** Running, in the sense the mark uses: a filled mark is a thing that is doing
 *  something. `funded` and `fid` are decisions and not yet plant, so they are
 *  hollow — the same reading build_lead.py's ADVANCE ladder takes. */
// `commissioning` is filled for the same reason `construction` is: something is
// happening on the ground. A works being started up is not a decision on paper.
const RUNNING = new Set(["construction", "commissioning", "operating"]);

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

/** A CLUSTER MARKER. One ring in neutral ink with the count inside it, drawn at
 *  the radius a mark would be drawn at plus the room the digits need.
 *
 *  NO STATUS, BY RULING (brief 16 §1). It is the one mark on this picture that
 *  is not told apart by shape and fill, and that is the honest reading: it
 *  stands for several sites whose statuses differ, so it takes none of them. A
 *  reader who wants the statuses presses it and gets them one row each.
 *
 *  THE COUNT IS IN THE MONOSPACE FACE, like every other count on this site; the
 *  class carries that and the stylesheet does the rest. */
function clusterMarker(cluster: MapCluster, g: Geometry) {
  const r = g.r * 1.9;
  return (
    <>
      <circle
        cx={cluster.x}
        cy={cluster.y}
        r={r}
        className="geo-cluster"
        vectorEffect="non-scaling-stroke"
      />
      <text x={cluster.x} y={cluster.y + r * 0.37} textAnchor="middle" className="geo-cluster-count">
        {cluster.count}
      </text>
    </>
  );
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
 *  thing in the key is the thing on the paper. The ring is drawn at the same
 *  ratio to the mark that `mark_geometry.ring_scale` sets on the canvas, so the
 *  ringed swatch is the ringed mark and not an approximation of it. */
function swatch(item: { role: "plant" | "storage"; running: boolean; ringed?: boolean }) {
  const cls = `geo-mark geo-mark-${item.role} ${item.running ? "is-running" : "is-stopped"}`;
  return (
    <svg viewBox="0 0 12 12" aria-hidden="true">
      {item.ringed ? <circle cx="6" cy="6" r="5.4" className="geo-here" /> : null}
      {item.role === "storage" ? (
        <polygon points="6,10.5 1.2,3.2 10.8,3.2" className={cls} />
      ) : (
        <circle cx="6" cy="6" r={item.ringed ? 2.6 : 4} className={cls} />
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
  /** Null where the picture's heading is the section's own H2 — which is what
   *  the sector hub does since brief 15 made the map a section rather than a
   *  figure inside the projects one. The wording is the same sentence; what
   *  changed is which element carries it, and two elements carrying it would be
   *  the heading said twice. */
  heading: string | null;
  standfirst: string;
}) {
  const { width, height } = doc.canvas;
  const g = doc.mark_geometry;
  const hasStore = doc.marks.some((m) => m.role === "storage");
  // THE RING IS EXPLAINED WHEREVER IT IS DRAWN, which is every crop and no
  // overview. Read off the built file's `subject_status` rather than off the
  // marks, so the key states the SUBJECT's state and not whichever mark
  // happened to be in frame — and so the swatch takes the subject's own fill
  // and is the mark on the paper rather than a filled stand-in for a hollow
  // one. The cancelled clause is appended to that same line: see geoKeyProse.
  const subject = doc.subject_status
    ? {
        running: RUNNING.has(doc.subject_status),
        cancelled: doc.subject_status === "cancelled",
      }
    : undefined;

  /** WHERE A MARK GOES. On the continental overview, the country view: the
   *  question the overview is asked next is "what is this country building",
   *  and brief 16 §2 answers it with a page rather than with one of the dots in
   *  it. On a crop and on a country view the mark is the project and opens it.
   *  Both links are on the file; nothing is composed here. */
  const target = (mark: MapMark) =>
    doc.kind === "sector" ? (mark.country_href ?? mark.href) : mark.href;

  /** A country's reviewed name, from the names already placed on this frame.
   *  Falls back to the code only where the frame draws no label for it, which
   *  on an overview cannot happen: it names every country holding a site. */
  const countryText = (iso: string) =>
    doc.countries.find((c) => c.iso === iso)?.text ??
    doc.country_totals?.find((t) => t.iso === iso)?.text ??
    iso;

  return (
    <figure
      className={`geo geo-${doc.kind}`}
      {...(heading ? { "aria-labelledby": `${doc.id}-heading` } : { "aria-label": standfirst })}
    >
      <figcaption className="geo-caption">
        {heading ? <h3 id={`${doc.id}-heading`}>{heading}</h3> : null}
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
            href={target(mark)}
            className={`geo-link geo-rel-${mark.relation}`}
            // A MARK A CLUSTER MARKER STANDS FOR IS NOT DRAWN TWICE. It stays in
            // the file because every count, the legend and the gate are computed
            // over the marks; what it loses is the ink, to the marker that is
            // already at its place.
            hidden={mark.clustered === true}
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
        {/* THE CLUSTERS, DRAWN LAST so a marker is never under a label it is
            standing beside. Each one opens the country view, which is where its
            members are listed; the title says what it is, because a numbered
            ring is the one mark on this picture a reader cannot read off the
            key. */}
        {(doc.clusters?.groups ?? []).map((cluster) => (
          <Link key={cluster.key} href={cluster.href} className="geo-link geo-cluster-link">
            <title>
              {geoClusterProse({
                count: cluster.count,
                projects: cluster.projects.length,
                country: countryText(cluster.country),
                radiusKm: doc.clusters?.radius_km ?? 0,
              })}
            </title>
            {clusterMarker(cluster, g)}
          </Link>
        ))}
      </svg>

      {/* THE COUNTRY LEGEND — brief 16 §2. Every country holding a drawn site,
          what it holds, and a link to its own view, which is the same
          destination the markers above have. On the overview only: a crop and a
          country view are already one place, and a legend of one row would be
          the heading said again in smaller type. */}
      {(doc.country_totals ?? []).length > 0 ? (
        <nav className="geo-countries" aria-label="By country">
          {(doc.country_totals ?? []).map((t) => (
            <Link key={t.iso} href={t.href} className="geo-country-row">
              <span className="geo-country-name">{t.text}</span>
              <span className="geo-country-count">{t.sites}</span>
            </Link>
          ))}
        </nav>
      ) : null}

      <div className="geo-key">
        {geoKeyProse({ hasStore, subject }).map((item) => (
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
        {/* THE STAMP, BOTH HALVES. `as_of` is the newest dateline over the rows
            this frame draws — the industry's currency, which moves every week —
            and the second clause is the basemap's, which is a release read on a
            stated day and does not move until somebody fetches another one. A
            picture has two ages and a reader is owed both; neither is the
            build's own date, which is what "every figure carries its as-of
            date" has always meant here. There is no staleness label and there
            is not going to be one: the ruling of 22 August 2026 is to show the
            date and let the reader judge it. */}
        <p className="geo-asof">
          as of {doc.as_of}
          {doc.basemap ? (
            <span className="geo-ground">
              {SEPARATOR}ground{" "}
              <a href={doc.basemap.url} target="_blank" rel="noreferrer">
                {doc.basemap.title}
              </a>
              {`, read ${doc.basemap.retrieved_date}`}
            </span>
          ) : null}
        </p>
      </div>
    </figure>
  );
}

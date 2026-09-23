import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import { SEPARATOR, citation } from "@/lib/citation";
import HubBlock from "@/components/HubBlock";
import LeadBlock from "@/components/LeadBlock";
import LocationMap from "@/components/LocationMap";
import SectionNav from "@/components/SectionNav";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import { SECTORS } from "@/lib/data";
import { hubBlocks } from "@/lib/hub";
import { sectorGeoProse, transitionProse } from "@/lib/prose";
import { renderedSections, sectorH1, sectorNames } from "@/lib/sectorSections";
import { getSectorMap } from "@/lib/maps";
import { getSectorOrientation, getTransitionNote, getUnnumberedH2 } from "@/lib/sitetext";
import {
  TRANSITION_LABEL,
  getBottlenecks,
  getImportance,
  getLead,
  getProjects,
  getTransitions,
  sourcesForSector,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";
import { atPrecision } from "@/lib/dates";

// THE SECTOR HUB: the product, and the only template that answers the whole
// question. Brief 15 reduces it.
//
// WHAT IT WAS. Nine numbered sections organised by node kind — projects,
// technologies, materials, opportunity, bottlenecks, policies, companies, feed,
// connections — each carrying its complete list. Ten equal-weight things, three
// of which were the hub doing a spoke page's job before the spoke pages
// existed. A visitor could not tell what the page was for, because the page did
// not say; it enumerated.
//
// WHAT IT IS. A short fixed sequence with the project register at its centre:
//
//   0  the epigraph and the reviewed sector_context prose, then the lead block.
//      Above the first H2, out of the nav: they answer "what am I looking at",
//      which is not one of the questions the sequence asks.
//   1  the map                      where Europe is building this
//   2  what is being built          the project register
//   3  what it depends on           technologies, materials and constraints
//   4  what policy does             the ranked measures
//   5  opportunity                  the money and the rules that pay
//      sources — §0.5's page-level register, unnumbered and outside the nav
//
// Sections 2 to 5 are BLOCKS and render through one component: a framing line,
// at most HUB_BLOCK_CAP rows, one link to the spoke that carries the complete
// list. See lib/hub.ts, which assembles them, and HubBlock.tsx, which draws
// them. This file decides what is shown and in what order, which is enough
// responsibility for one component.
//
// THE COMPLETE LISTS ARE ON THE SPOKES: /sectors/<slug>/projects,
// /technologies, /policies, /companies, /connections. Companies, Feed and
// Connections leave the hub entirely and are reached from the footer row.
//
// THE ORDER IS NOT WRITTEN HERE. It is data/prose.json → sector_sections, read
// through lib/sectorSections.ts, and sources/check_section_order.py fails the
// build if this file renders the sequence in any other order or under any other
// id. The headings are not written here either: they are templates in the same
// block with the sector's two name slots substituted in, so the wording is
// reviewed in one place and cannot drift between sectors.
//
// A BLOCK IS NEVER OMITTED. Brief 5 omitted a section with no data; brief 15
// does not, for these four, because "nothing on file, as of <date>" is one of
// the answers a reader is owed and an absent block reads as a page that forgot
// to ask. The map is the one conditional entry: a sector with no drawn frame
// has no picture to show.
//
// NOTHING HERE COMPUTES A RANKING OR A EURO. Both come from the gated Python
// artefacts, as they did before.

export default function SectorMap({ slug }: { slug: SectorSlug }) {
  const name = SECTORS[slug];
  const names = sectorNames(slug);
  const transitions = getTransitions(slug);
  const geoFrame = getSectorMap(slug);

  // EVERY COUNT IN THE MAP'S STANDFIRST IS OVER DRAWN SITES, because every mark
  // in the picture is one. Counting projects instead made steel read "9 sites …
  // 7 operating or under construction, 1 paused" — eight, because the
  // ArcelorMittal row is one project standing on two sites and the picture
  // draws both. What the frame does NOT draw is stated in its own clause, from
  // the count build_maps.py wrote into the file.
  const geoMarks = (status: string[]) =>
    geoFrame ? geoFrame.marks.filter((m) => status.includes(m.status)).length : 0;
  const geoProse = geoFrame
    ? sectorGeoProse({
        sector: name.toLowerCase(),
        sites: geoFrame.marks.length,
        countries: new Set(geoFrame.marks.map((m) => m.country)).size,
        running: geoMarks(["operating", "construction", "commissioning"]),
        pending: geoMarks(["announced", "funded", "fid"]),
        paused: geoMarks(["paused"]),
        undrawn: geoFrame.undrawn ?? { projects: 0, sites: 0 },
        hostWorks: geoFrame.marks.filter((m) => m.host_works).length,
      })
    : null;

  // WHICH SECTIONS EXIST ON THIS SECTOR'S PAGE. The four blocks are fixed; the
  // map is a question about the data. Listed in full rather than shortened to
  // the one variable entry, because this map is the sequence in the
  // specification, readable side by side with it, and because
  // check_section_order reads it to establish that no section renders outside
  // the one list the nav is built from.
  const present: Record<string, boolean> = {
    map: Boolean(geoFrame && geoProse),
    projects: true,
    depends: true,
    policies: true,
    opportunity: true,
  };
  const sections = renderedSections(slug, present);
  const headings = new Map(sections.map((s) => [s.id, s.h2]));
  /** The heading for a section that is being rendered. Throws for a section
   *  `present` says is absent, which is the one way this file could put a
   *  section on the page without the nav knowing about it. */
  const h2 = (id: string): string => {
    const text = headings.get(id);
    if (!text) {
      throw new Error(
        `section "${id}" is rendering but "present" says it has no data, so it has ` +
          `no heading and no nav entry — the two have to be one decision`,
      );
    }
    return text;
  };

  // THE FOUR BLOCKS, built in one call. A page that assembled them one at a
  // time could render three, and brief 15 makes a missing block a build
  // failure; the way to make that true is for there to be no way of building
  // three.
  const blocks = hubBlocks(slug);

  // The lead. A built artefact where one exists; otherwise the sentence this
  // page opened with before amendment brief 2 §4, which is still a correct
  // computed sentence and is the right thing to fall back to for a sector whose
  // lead has not been built yet.
  const orientation = getSectorOrientation(slug);
  const lead = getLead(slug);
  const imp = getImportance(slug);
  const projects = getProjects(slug);
  const bottlenecks = getBottlenecks(slug);
  const opening =
    getTransitionNote(slug) ??
    transitionProse({
      subject: name.toLowerCase(),
      transitions: transitions.map((t) => TRANSITION_LABEL[t]),
      measuresInView: imp ? imp.measures.filter((m) => m.in_sector_view).length : 0,
      measuresTotal: imp ? imp.measures.length : 0,
      bottlenecks: bottlenecks.length,
      projects: projects.length,
      operating: projects.filter((p) => p.status === "operating").length,
      paused: projects.filter((p) => p.status === "paused").length,
    });

  const grouped = sourcesForSector(slug);

  return (
    <main className="rise sector-map" style={{ ["--accent" as string]: `var(${accentVar(slug)})` }}>
      <SectionNav sections={sections} />
      <div className="wrap">
        <Crumbs trail={[{ label: "Sectors", href: "/sectors" }, { label: name }]} />

        <header className="tmap-head">
          <h1>
            <SectorIcon slug={slug} size={28} /> {sectorH1(slug)}
          </h1>
          <ul className="tmap-transitions">
            {transitions.map((t) => (
              <li key={t}>{TRANSITION_LABEL[t]}</li>
            ))}
          </ul>
          {/* Standing context first, then the computed lead. The paragraph is
              reviewed prose from data/prose.json and does not move when the data
              does; everything below it is computed and does. A reader who has
              never met this sector needs the first before the second means
              anything, and a reader who has can skip it — which is why it is one
              paragraph and not a page. Absent (unreviewed, or unwritten for this
              sector) the header renders exactly as it did before.

              ONE BLOCK, RENDERED AS ITS BEATS. The paragraph is written in
              several beats separated by blank lines, and a single <p> would run
              them together into a wall. */}
          {orientation
            ? orientation.split(/\n\s*\n/).map((beat, i) => (
                <p key={i} className="tmap-orientation">
                  {beat}
                </p>
              ))
            : null}
          {lead ? <LeadBlock lead={lead} /> : <p className="tmap-lede">{opening}</p>}
        </header>

        {/* THE MAP, now a section of its own and the first entry in the nav. It
            used to render inside the projects section behind an H3, which made
            geography an attribute of the project table rather than the first
            answer to where this is happening. The heading and the standfirst are
            the same sentences; the heading is now the section's H2, read from
            the reviewed sequence, so LocationMap draws the picture and heads
            nothing. */}
        {present.map && geoFrame && geoProse ? (
          <section className="tmap-section" id="map">
            <h2 className="sectionhead">{h2("map")}</h2>
            <LocationMap doc={geoFrame} heading={null} standfirst={geoProse.standfirst} />
            {/* THE FULL UNDRAWN LIST, UNDER THE PICTURE. The standfirst names
                five and counts the rest, because a sentence that names fifty
                projects is a list wearing a sentence's clothes. Every row links
                to its own page: a project the picture cannot draw is still a
                project a reader can open. */}
            {(geoFrame.undrawn?.rows ?? []).length > 0 ? (
              <details className="tmap-undrawn">
                <summary>{`On file and not drawn: ${(geoFrame.undrawn?.rows ?? []).length}`}</summary>
                <ul>
                  {(geoFrame.undrawn?.rows ?? []).map((r) => (
                    <li key={r.id}>
                      <Link href={`/projects/${r.id}`}>{r.name}</Link>
                      {` — ${r.status}, `}
                      {r.sited
                        ? "cancelled and drawn on its own crop only"
                        : r.stopped
                          ? "location not sought"
                          : "no citable source places the works"}
                    </li>
                  ))}
                </ul>
              </details>
            ) : null}
          </section>
        ) : null}

        {/* THE FOUR BLOCKS, in the sequence's order. `present` says all four
            render; the guard is what makes that a decision this file states
            rather than one HubBlock assumes. */}
        {blocks.map((block) =>
          present[block.id] ? (
            <HubBlock key={block.id} block={block} heading={h2(block.id)} />
          ) : null,
        )}

        {/* THE FOOTER ROW. Where the three demoted spokes are reached from, and
            the whole of what is left of Companies, Feed and Connections on this
            page. They are a click away rather than a scroll away, which is the
            right weight for three things a reader on a hub is not asking for. */}
        <nav className="tmap-footer" aria-label="More on this sector">
          <Link href={`/sectors/${slug}/companies`}>Companies in {names.phrase}</Link>
          <Link href={`/sectors/${slug}/changes`}>What changed in {names.short}</Link>
          <Link href={`/sectors/${slug}/connections`}>How {names.short} connects</Link>
        </nav>

        {/* SOURCES IS NOT ONE OF THE NUMBERED SECTIONS and is not in the nav.
            Page specifications §0.5 makes it the final section of every sector
            page; it answers "what does this page stand on", which is a question
            about the page rather than about the industry. So it renders last on
            the same footing as the lead block renders first. */}
        <section className="tmap-section" id="sources">
          <h2 className="sectionhead">{getUnnumberedH2("sources")}</h2>
          <p className="tmap-sub">
            Every outbound URL on this page and on its spokes, grouped by publisher. The build
            fails on a dead one.
          </p>
          <div className="tsources">
            {grouped.map((g) => (
              <div key={g.publisher}>
                <h3>{g.publisher}</h3>
                <ul>
                  {g.sources.map((s) => (
                    <li key={s.url}>
                      {/* THE URL IS IN href AND NOWHERE ELSE. The anchor text is
                          a citation — a title for a document, what was asked of
                          a dataset for an api — and never the address it was
                          asked at. See lib/citation.ts. */}
                      <a href={s.url} target="_blank" rel="noreferrer">
                        {citation(s)}
                      </a>
                      {s.date ? (
                        <span className="tscore-note">{`${SEPARATOR}${atPrecision(s.date!, s.date_precision)}`}</span>
                      ) : null}
                      {s.retrieved_date ? (
                        <span className="tscore-note">{`${SEPARATOR}read ${s.retrieved_date}`}</span>
                      ) : null}
                      {s.licence ? (
                        <span className="tscore-note">{`${SEPARATOR}${s.licence}`}</span>
                      ) : null}
                      {s.archived ? <span className="tarchived">archived</span> : null}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

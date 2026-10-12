import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import LocationMap from "@/components/LocationMap";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import { capacityFigures } from "@/components/SectorMap";
import { ProjectTable } from "@/components/SectorSpoke";
import { SECTORS } from "@/lib/data";
import { getCountryMap } from "@/lib/maps";
import { countryGeoProse } from "@/lib/prose";
import { sectorLabel, sectorNames } from "@/lib/sectorSections";
import { getCountryH1 } from "@/lib/sitetext";
import { byLastChange, getProjects, isDrawable } from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// ONE COUNTRY, INSIDE ONE SECTOR — brief 16 §3. Where every marker on the
// continental overview and every row of its country legend goes.
//
// WHY THE PAGE EXISTS. The sector overview is a fixed continental frame,
// identical for every sector, which is what makes two sectors' pictures
// comparable — and which means it cannot separate two works eight kilometres
// apart. Brief 16 clusters those into one numbered marker, and a marker that
// stands for four sites owes the reader the four. This is where they are: the
// same component, a frame fitted to the country, nothing grouped.
//
// FOUR THINGS AND NOTHING ELSE:
//
//   1  the heading, from the reviewed template in data/prose.json →
//      country_pages, filled with the sector's name slots and the country's
//      reviewed name — the same string build_maps.py measured to place the
//      label on the paper, so the heading and the map agree.
//   2  the count line, computed, linking back to the sector's own overview.
//   3  the picture, drawn one for one.
//   4  the project register's table over this country's rows — the same eight
//      columns the projects spoke renders, because this is a filter on that
//      list and not a different list.
//
// AND THE UNDRAWN ROWS ARE NAMED. A reader counting four Spanish dots against a
// register holding nine Spanish rows is owed the difference, by name and with
// the reason: cancelled, or no position on file. The standfirst over the picture
// says it and the list under the table repeats it with a link to each row —
// exactly the arrangement the overview uses, for the same reason.
//
// NO LAYOUT HERE. Every coordinate comes from sources/build_maps.py, like every
// other picture on this site. There is no client-side zoom and no filtering:
// this page IS the zoom, computed once, identical for every reader and
// reviewable in a diff.

export default function SectorCountry({
  slug,
  iso,
}: {
  slug: SectorSlug;
  iso: string;
}) {
  const frame = getCountryMap(slug, iso);
  // The route enumerates only the pairs that have a frame, so this is
  // unreachable — and it is a type guard rather than an empty state, because an
  // empty state here would be a picture of a country asserting it builds
  // nothing.
  if (!frame) return null;

  const name = SECTORS[slug];
  const names = sectorNames(slug);
  const country = frame.countries.find((c) => c.iso === iso)?.text ?? iso;
  const heading = getCountryH1(names, country);

  const marks = (status: string[]) => frame.marks.filter((m) => status.includes(m.status)).length;
  const countryRows = getProjects(slug).filter((p) => p.country === iso);
  const geo = countryGeoProse({
    sector: names.short,
    country,
    sites: frame.marks.length,
    projects: new Set(frame.marks.map((m) => m.id)).size,
    running: marks(["operating", "construction", "commissioning"]),
    pending: marks(["announced", "funded", "fid"]),
    paused: marks(["paused"]),
    undrawn: frame.undrawn ?? { projects: 0, sites: 0 },
    hostWorks: frame.marks.filter((m) => m.host_works).length,
    // The capacity on the ground IN THIS COUNTRY, with the denominator over
    // this country's drawn rows. The undrawn figure is not repeated here: the
    // sector's overview states it over the sector, and a per-country split of
    // rows nobody has placed would be a figure about a place the register does
    // not claim the project is in.
    drawnCapacity: capacityFigures(countryRows.filter(isDrawable)),
  });

  // THE ROWS THIS PAGE IS ABOUT: every row in the sector filed to this country,
  // drawn or not. The table is the register's answer and the register does not
  // stop at what could be placed — a cancelled Spanish plant is a Spanish row.
  // Ordered by last status change, which is the order the hub's block and the
  // projects spoke both use, so a reader moving between them is not re-sorted.
  const rows = byLastChange(countryRows);
  const drawnRows = rows.filter(isDrawable).length;

  return (
    <main className="rise sector-map" style={{ ["--accent" as string]: `var(${accentVar(slug)})` }}>
      <div className="wrap">
        <Crumbs
          trail={[
            { label: "Sectors", href: "/sectors" },
            { label: sectorLabel(slug), href: `/sectors/${slug}` },
            { label: `Every tracked project in European ${names.short}`, href: `/sectors/${slug}/projects` },
            { label: country },
          ]}
        />

        <header className="tmap-head">
          <h1>
            <SectorIcon slug={slug} size={28} /> {heading}
          </h1>
          {/* THE COUNT LINE. Computed, and every number in it is a count of
              rows this page lists: the register's rows for this country, how
              many of them the picture draws, and the link back to the frame
              those dots were grouped on. */}
          <p className="tmap-lede">
            {`${rows.length} tracked ${rows.length === 1 ? "project" : "projects"} in `}
            {country}
            {`, ${drawnRows} of them drawn. `}
            <Link href={`/sectors/${slug}`}>{`Back to where Europe is building ${names.short}`}</Link>
          </p>
        </header>

        <section className="tmap-section" id="map">
          <LocationMap doc={frame} heading={geo.heading} standfirst={geo.standfirst} />
        </section>

        <section className="tmap-section" id="projects">
          <h2 className="sectionhead">{`Every tracked ${names.short} project in ${country}`}</h2>
          <ProjectTable rows={rows} />
          {/* THE ROWS THE PICTURE COULD NOT DRAW, by name and with the reason.
              The table above holds them — they are rows — so this list is not
              a second enumeration of the sector; it is the answer to "why are
              there fewer dots than lines". */}
          {(frame.undrawn?.rows ?? []).length > 0 ? (
            <details className="tmap-undrawn">
              <summary>{`On file in ${country} and not drawn: ${(frame.undrawn?.rows ?? []).length}`}</summary>
              <ul>
                {(frame.undrawn?.rows ?? []).map((r) => (
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

        <nav className="tmap-footer" aria-label="Back to the sector">
          <Link href={`/sectors/${slug}`}>← {sectorLabel(slug)}</Link>
          <Link href={`/sectors/${slug}/projects`}>{`All ${names.short} projects`}</Link>
        </nav>
      </div>
    </main>
  );
}

import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import { SEPARATOR, citation } from "@/lib/citation";
import { getOpportunity, opportunitySignals, supportFact, supportMeasures } from "@/lib/opportunity";
import LeadBlock from "@/components/LeadBlock";
import LocationMap from "@/components/LocationMap";
import SectionNav from "@/components/SectionNav";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import TransitionDiagram, { type Diagram, type NodeSource } from "@/components/TransitionDiagram";
import { FILES, SECTORS, getRelatedSectors } from "@/lib/data";
import { sectorGeoProse, transitionProse } from "@/lib/prose";
import { renderedSections, sectorH1 } from "@/lib/sectorSections";
import { getSectorMap } from "@/lib/maps";
import { getRecordsForSector } from "@/lib/records";
import { getOpportunityProse, getSectorOrientation, getTransitionNote, getUnnumberedH2 } from "@/lib/sitetext";
import {
  STATUS_LABEL,
  TRANSITION_LABEL,
  byLastChange,
  eur,
  fundingAmount,
  fundingTotals,
  fundingForProject,
  FUNDING_ANNOUNCED,
  FUNDING_COMMITTED,
  getBottlenecks,
  getFunding,
  getImportance,
  getLead,
  getMaterial,
  getParameters,
  getProjects,
  getProject,
  getTechnologies,
  getTechnology,
  getTransitions,
  lastChange,
  materialFlows,
  measureHref,
  projectHref,
  sourcesForSector,
  type Funding,
  type MaterialFlow,
  type Parameter,
  type StatusEvent,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// THE SECTOR PAGE: the product, and the only template that answers the whole
// question. Brief 5 restructures it around a fixed sequence of QUESTIONS —
// every section heading is one, every sector asks them in the same order, so
// the interface is learned once and never re-learned on the second sector.
//
//   0  the lead block — the sentence, why it matters, the facts. No H2, not in
//      the nav: it is the answer to "what am I looking at", which is not one of
//      the questions the sequence asks.
//   1  what is being built            projects
//   2  which technologies could change it
//   3  which materials flow through it
//   4  what rules and money support it   opportunity
//   5  what constrains it              bottlenecks
//   6  which rules matter              policies
//   7  who the companies are           (omitted everywhere: no company node kind yet)
//   8  what changed                    feed
//   9  how it connects                 the diagram and the related sectors
//      sources — §0.5's page-level register, unnumbered and outside the nav
//
// THE ORDER IS NOT WRITTEN HERE. It is data/prose.json → sector_sections, read
// through lib/sectorSections.ts, and sources/check_section_order.py fails the
// build if this file renders the sections in any other order or under any other
// id. The headings are not written here either: they are templates in the same
// block with the sector's two name slots substituted in, so the wording is
// reviewed in one place and cannot drift between sectors.
//
// AN EMPTY SECTION IS OMITTED, from the page and from the nav both (brief 5 §2)
// — which amends the fixed-presence rule at page specifications §0.5 for this
// page type. `present` below is the whole of that decision, one boolean per
// section, and it is the only place a section's existence is decided.
//
// NOTHING HERE COMPUTES A RANKING OR A EURO. Both come from
// data/transition/importance/<sector>.json, built and gated in Python. This
// file decides what is shown and in what order, which is enough responsibility
// for one component.

// THE SCORE PANEL IS GONE FROM THIS PAGE, and it is worth saying where it
// went. `ScoreComponents` drew three columns under every measure: the money
// model with its formula and caveats, every bottleneck edge with its weight
// and quote, and the attention count. Brief 4 §5 rules the key-measures list
// down to a title and a sentence, and a panel of weights under each one is
// exactly the schema-facing surface it rules off.
//
// Nothing about the ranking has changed. It is still computed and gated in
// Python, and all of it — formula, caveats, edges, weights, attention — is in
// data/transition/importance/<sector>.json and printed by
// `python3 sources/build_importance.py` on every run. What has changed is that
// the reader is no longer shown the working before the conclusion.

// Five is the top of the three-to-five brief 4 §5 allows, and it is the number
// at which the list stops being a list a reader finishes. It caps what is
// DRAWN and nothing else: the ranking is built over every measure in the sector
// view, and the ones below the cut are on their own pages with their scores.
const KEY_MEASURES = 5;

// Thirty days, per amendment brief 2 §5. Long enough that a quiet fortnight
// does not empty the strip, short enough that "moved" still means recently.
const MOVED_WINDOW_DAYS = 30;

// Evaluated once when this module loads, which for a statically generated page
// is build time. The window is therefore the thirty days before THIS BUILD, not
// before the reader's clock — the right basis for a page whose every other
// figure carries an as-of date from the same build, and the only one that does
// not quietly change what a cached page claims as it ages.
const MOVED_CUTOFF = new Date(Date.now() - MOVED_WINDOW_DAYS * 86_400_000)
  .toISOString()
  .slice(0, 10);

function ParameterChip({ p }: { p: Parameter }) {
  return (
    <li className="tparam">
      <span className="tparam-value">
        {p.value} <span className="tparam-unit">{p.unit}</span>
      </span>
      <span className="tparam-name">{p.name}</span>
      <a className="tparam-src" href={p.source.url} target="_blank" rel="noreferrer">
        {p.source.publisher}
      </a>
      <span className={`tconf ${p.confidence}`}>{p.confidence}</span>
    </li>
  );
}

/** A material edge's endpoint, said in the reader's words rather than the
 *  graph's. `project:brevik-ccs` is an id; "Brevik CCS" is what it is called. */
function nodeLabel(node: string): string {
  const [kind, id] = node.split(":");
  if (kind === "sector") return SECTORS[id as SectorSlug] ?? id;
  if (kind === "project") return getProject(id)?.name ?? id;
  if (kind === "technology") return getTechnology(id)?.name ?? id;
  return id;
}

/** One of the three material lists.
 *
 *  EVERY ITEM SHOWS ITS BASIS (brief 5 §2 as amended): the count of plants
 *  behind the edge, or the sector-level edge where the claim is about the
 *  industry as a whole, linking to the set that count is of.
 *
 *  The link goes to the material's own page rather than to this page's project
 *  table, and the difference matters: the table lists all eight cement plants,
 *  and a reader who clicks "5 plants" has to land on the five, each with the
 *  edge evidence that put it there. That is §0.1's rule for a computed figure —
 *  it links to the set of records behind it — and the plant list it asks for is
 *  the one on /materials/{id}, not the one here.
 *
 *  Ordering is by edge count and is not itself displayed: a count of edges is a
 *  fact about the graph, where a count of plants is a fact about the industry. */
function MaterialList({
  title,
  rows,
  anchor,
}: {
  title: string;
  rows: MaterialFlow[];
  /** Which block on the material page the basis link opens. Null for
   *  substitutes, which rest on no endpoint and carry no count. */
  anchor: string | null;
}) {
  if (rows.length === 0) return null;
  return (
    <div className="tmatlist">
      <h3>{title}</h3>
      <ul>
        {rows.map((row) => {
          const m = row.material;
          const basis: string[] = [];
          if (row.plants > 0) basis.push(`${row.plants} ${row.plants === 1 ? "plant" : "plants"}`);
          if (row.sectorWide) basis.push("sector-wide");
          return (
            <li key={m.id}>
              <Link href={`/materials/${m.id}`}>{m.name}</Link>
              <span className={`tmat-type ${m.type}`}>{m.type.replace("_", " ")}</span>
              {basis.length > 0 && anchor ? (
                <Link className="tmat-basis" href={`/materials/${m.id}#${anchor}`}>
                  {basis.join(" · ")}
                </Link>
              ) : null}
              {/* A substitution names what it stands in for, which is the basis
                  a reader wants where there is no count to give them. */}
              {anchor === null ? (
                <span className="tmat-basis">
                  for{" "}
                  {m.substitutes
                    .map((sub) => getMaterial(sub.material)?.name ?? sub.material)
                    .join(", ")}
                </span>
              ) : null}
              {/* A fact about the material, read off Annex I of the CRMA, never a
                  judgement about the sector that handles it. */}
              {m.crma_annex_i ? (
                <a
                  className="tmat-crma"
                  href={m.crma_annex_i.source.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  CRMA Annex I
                </a>
              ) : null}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/** One allocation, said the same way in every status group. It is one component
 *  rather than three copies because the ROW is identical across the groups —
 *  what differs is whether the group above it carries a total, and that is a
 *  decision about the group, not about the line. */
function FundingRow({ f, params }: { f: Funding; params: Map<string, Parameter> }) {
  const amount = fundingAmount(f, params);
  return (
    <li id={`funding-${f.id}`}>
      <span className="amount">{amount ? eur(amount) : "undisclosed"}</span>
      <span className="programme">{f.programme}</span>
      <span className={`tstatus ${f.status}`}>{f.status}</span>
      <span className="tfunding-to">
        {f.finances.map((n, i) => (
          <span key={n}>
            {i > 0 ? ", " : ""}
            <Link href={projectHref(n.split(":")[1])}>{nodeLabel(n)}</Link>
          </span>
        ))}
      </span>
      {f.under ? (
        <Link href={measureHref(f.under)} className="measure">
          {f.under}
        </Link>
      ) : null}
      <span className="tfunding-date">{f.date}</span>
    </li>
  );
}

export default function SectorMap({ slug }: { slug: SectorSlug }) {
  const name = SECTORS[slug];
  const imp = getImportance(slug)!;
  const bottlenecks = getBottlenecks(slug);
  const technologies = getTechnologies(slug);
  const projects = byLastChange(getProjects(slug));
  const params = getParameters();
  const flows = materialFlows(slug);
  const funding = getFunding(slug);
  const related = getRelatedSectors(slug);
  // §4.1's three status groups, split once and read three times.
  const committedFunding = funding.filter((f) => FUNDING_COMMITTED.includes(f.status));
  const announcedFunding = funding.filter((f) => FUNDING_ANNOUNCED.includes(f.status));
  // The date the committed sum is complete THROUGH, not the date of the build:
  // the build ran today and that says nothing about when the money last moved.
  const committedAsOf = committedFunding.reduce((a, f) => (f.date > a ? f.date : a), "");
  const opportunity = getOpportunity(slug);
  const opp = getOpportunityProse();
  const support = supportMeasures(slug);
  // §4.6. A filter over the records that already exist, never a second feed.
  const signals = opportunitySignals(slug, getRecordsForSector(slug));
  // The rollup, derived here and stored nowhere. `undisclosed` is counted
  // separately rather than folded in as zero: a grant nobody published is not
  // a grant of nothing, and a total that pretended otherwise would read as
  // complete.
  // Three figures, never one: committed money, announced money and withdrawn
  // lines. See lib/transition.ts:fundingTotals and sources/sector_map.py.
  const totals = fundingTotals(funding, params);
  const undisclosed = totals.undisclosed;
  const transitions = getTransitions(slug);

  // Status changes in this sector inside the window, most recent first, and
  // the most recent change of any age for the empty state. `lastChange` is the
  // same helper the home feed uses, so the two strips cannot disagree about
  // what the latest event is.
  // EVERY COUNT IN THIS SENTENCE IS OVER SITES, because every mark in the
  // picture is one. Counting projects instead made steel read "9 sites … 7
  // operating or under construction, 1 paused" — eight, because the
  // ArcelorMittal row is one project standing on two sites and the picture
  // draws both.
  const geoFrame = getSectorMap(slug);
  const geoMarks = (status: string[]) =>
    geoFrame ? geoFrame.marks.filter((m) => status.includes(m.status)).length : 0;
  const geoProse = geoFrame
    ? sectorGeoProse({
        sector: SECTORS[slug].toLowerCase(),
        sites: geoFrame.marks.length,
        countries: new Set(projects.map((p) => p.country)).size,
        running: geoMarks(["operating", "construction"]),
        pending: geoMarks(["announced", "funded", "fid"]),
        stopped: geoMarks(["paused", "cancelled"]),
      })
    : null;

  const changes = projects
    .map((p) => ({ project: p, event: lastChange(p) }))
    .filter((r): r is { project: (typeof projects)[number]; event: StatusEvent } =>
      Boolean(r.event),
    )
    .sort((a, b) => b.event.date.localeCompare(a.event.date));
  const moved = changes.filter((r) => r.event.date >= MOVED_CUTOFF);
  const latestMove = changes[0] ?? null;
  const inView = imp.measures.filter((m) => m.in_sector_view);

  // The lead. A built artifact where one exists; otherwise the sentence this
  // page opened with before amendment brief 2 §4, which is still a correct
  // computed sentence and is the right thing to fall back to for a sector whose
  // lead has not been built yet.
  const orientation = getSectorOrientation(slug);
  const lead = getLead(slug);
  const opening =
    getTransitionNote(slug) ??
    transitionProse({
      subject: name.toLowerCase(),
      transitions: transitions.map((t) => TRANSITION_LABEL[t]),
      measuresInView: inView.length,
      measuresTotal: imp.measures.length,
      bottlenecks: bottlenecks.length,
      projects: projects.length,
      operating: projects.filter((p) => p.status === "operating").length,
      paused: projects.filter((p) => p.status === "paused").length,
    });

  const diagramPath = path.join(
    process.cwd(),
    "..",
    "data",
    "transition",
    "diagrams",
    `${slug.replace("/", "__")}.json`,
  );
  const diagram: Diagram | null = fs.existsSync(diagramPath)
    ? (JSON.parse(fs.readFileSync(diagramPath, "utf8")) as Diagram)
    : null;

  // The diagram's hover panel needs each node's sources. They are assembled
  // here rather than in the layout script because they are page data, not
  // geometry — the picture would be identical without them.
  const nodeSources: Record<string, NodeSource[]> = {};
  // The panel is drawn in the browser and lib/citation.ts reads the register off
  // disk, so the wording happens here and the component is handed finished text.
  const cited = (rows: typeof bottlenecks[number]["sources"]): NodeSource[] =>
    rows.map((s) => ({ ...s, title: citation(s) }));
  for (const b of bottlenecks) nodeSources[`bottleneck:${b.id}`] = cited(b.sources);
  for (const t of technologies) nodeSources[`technology:${t.id}`] = cited(t.sources);
  for (const p of projects) nodeSources[`project:${p.id}`] = cited(p.sources);
  for (const m of inView) {
    const q = m.bottleneck_linkage.edges[0]?.evidence;
    nodeSources[`measure:${m.measure}`] = q
      ? [{ url: measureHref(m.measure), title: m.article ?? m.measure, publisher: q.source }]
      : [{ url: measureHref(m.measure), title: m.article ?? m.measure, publisher: `data/${m.file}.json` }];
  }

  const grouped = sourcesForSector(slug);
  const projectsByTech = new Map<string, typeof projects>();
  for (const p of projects)
    for (const t of p.technology) {
      if (!projectsByTech.has(t)) projectsByTech.set(t, []);
      projectsByTech.get(t)!.push(p);
    }

  // WHICH SECTIONS EXIST ON THIS SECTOR'S PAGE. One boolean each, and every one
  // of them is a question about the data rather than about the sector: steel
  // gets its sections by having rows, not by an edit here.
  //
  // `companies` is false on every sector and will be until the company node
  // kind is built (brief 5 §2). It is listed rather than omitted so the day it
  // arrives is a one-word change and so the sequence in this map is the
  // sequence in the specification, readable side by side.
  const present: Record<string, boolean> = {
    projects: projects.length > 0,
    technologies: technologies.length > 0,
    materials:
      flows.inputs.length + flows.outputs.length + flows.substitutes.length > 0,
    opportunity: funding.length > 0,
    bottlenecks: bottlenecks.length > 0,
    policies: inView.length > 0,
    companies: false,
    feed: changes.length > 0,
    connections: Boolean(diagram) || related.length > 0,
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
            sector) the header renders exactly as it did before. */}
        {orientation ? <p className="tmap-orientation">{orientation}</p> : null}
        {lead ? <LeadBlock lead={lead} /> : <p className="tmap-lede">{opening}</p>}
      </header>

      {present.projects ? (
        <section className="tmap-section" id="projects">
          <h2 className="sectionhead">{h2("projects")}</h2>
          {/* THE OVERVIEW COMES BEFORE THE TABLE, and inside this section rather
              than as one of its own. It answers the section's question — what is
              being built — in the one dimension the table cannot show, and a
              tenth numbered section would have made geography a subject rather
              than an attribute of the projects already here. */}
          {geoFrame && geoProse ? (
            <LocationMap
              doc={geoFrame}
              heading={geoProse.heading}
              standfirst={geoProse.standfirst}
            />
          ) : null}
          <p className="tmap-sub">Sorted by last status change. Every change carries its source.</p>
          <div className="tprojects-scroll">
            <table className="tprojects">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Company</th>
                  <th>Site</th>
                  <th>Country</th>
                  <th>Technology</th>
                  <th>Status</th>
                  <th>Public funding</th>
                  <th>Last change</th>
                </tr>
              </thead>
              <tbody>
                {projects.map((p) => {
                  const last = lastChange(p);
                  const rows = fundingForProject(p.id);
                  // The same rule as the money section: this cell says committed
                  // money only, so a column of awards never quietly includes an
                  // announcement. The announced figure has one home, above.
                  const pt = fundingTotals(rows, params);
                  const funded = pt.committed;
                  return (
                    <tr key={p.id}>
                      <td>
                        <Link href={projectHref(p.id)}>{p.name}</Link>
                      </td>
                      <td>{p.company}</td>
                      <td>{p.plant ?? "—"}</td>
                      <td>{p.country}</td>
                      <td className="ttech-cell">{p.technology.join(", ")}</td>
                      <td>
                        <span className={`tstatus ${p.status}`}>{STATUS_LABEL[p.status]}</span>
                      </td>
                      <td className="num">
                        {funded ? eur(funded) : pt.committedCount ? "undisclosed" : "—"}
                      </td>
                      <td className="num">{last?.date ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      {present.technologies ? (
        <section className="tmap-section" id="technologies">
          <h2 className="sectionhead">{h2("technologies")}</h2>
          <div className="ttechs">
            {technologies.map((t) => (
              <article key={t.id} id={`technology-${t.id}`} className="ttech">
                <h3>
                  {t.name} <span className={`tready ${t.readiness.level}`}>{t.readiness.level}</span>
                </h3>
                <p>{t.description}</p>
                <dl>
                  <dt>Readiness</dt>
                  <dd>
                    {t.readiness.level} — {t.readiness.note}{" "}
                    <a href={t.readiness.source} target="_blank" rel="noreferrer">
                      source
                    </a>{" "}
                    ({t.readiness.date})
                  </dd>
                  {t.abatement_share ? (
                    <>
                      <dt>Abatement</dt>
                      <dd>
                        {t.abatement_share.low === t.abatement_share.high
                          ? t.abatement_share.low
                          : `${t.abatement_share.low}–${t.abatement_share.high}`}{" "}
                        {t.abatement_share.unit}
                        {t.abatement_share.note ? ` — ${t.abatement_share.note}` : ""}
                      </dd>
                    </>
                  ) : null}
                  {t.cost ? (
                    <>
                      <dt>Cost</dt>
                      <dd>
                        {t.cost.low}–{t.cost.high} {t.cost.unit}
                        {t.cost.note ? ` — ${t.cost.note}` : ""}
                      </dd>
                    </>
                  ) : null}
                  {t.dependency.length > 0 ? (
                    <>
                      <dt>Depends on</dt>
                      <dd>
                        {t.dependency.map((d, i) => (
                          <span key={d}>
                            {i > 0 ? ", " : ""}
                            <a href={`#technology-${d}`}>{d}</a>
                          </span>
                        ))}
                      </dd>
                    </>
                  ) : null}
                  <dt>Deployed by</dt>
                  <dd>
                    {(projectsByTech.get(t.id) ?? []).length > 0
                      ? (projectsByTech.get(t.id) ?? []).map((p, i) => (
                          <span key={p.id}>
                            {i > 0 ? ", " : ""}
                            <Link href={projectHref(p.id)}>{p.name}</Link>
                          </span>
                        ))
                      : "no tracked project in this sector"}
                  </dd>
                </dl>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {present.materials ? (
        <section className="tmap-section" id="materials">
          <h2 className="sectionhead">{h2("materials")}</h2>
          <p className="tmap-sub">
            What arrives, what leaves, and what could stand in for it. Every material is a
            cross-sector node — clinker leaves cement, captured CO2 leaves it and arrives at
            a storage route — so each one opens its own page rather than a list of this
            sector&apos;s copy of it.
          </p>
          <div className="tmatlists">
            <MaterialList title="Inputs" rows={flows.inputs} anchor="consumed-by" />
            <MaterialList title="Outputs and by-products" rows={flows.outputs} anchor="produced-by" />
            <MaterialList title="Substitutes" rows={flows.substitutes} anchor={null} />
          </div>
        </section>
      ) : null}

      {present.opportunity ? (
        <section className="tmap-section" id="opportunity">
          <h2 className="sectionhead">{h2("opportunity")}</h2>
          {/* THE SECTION'S OWN GENERATED SENTENCE (§4.5). Built by
              sources/build_opportunity.py from the two facts below it and
              nothing else, gated by the same rules as the sector lead, with an
              override slot in overrides.json and a re-review flag when the
              facts move. Absent where the sentence failed its gate — this
              section has a heading that already asks the question, so a
              sentence nobody checked is better not there. */}
          {opportunity?.sentence.text ? (
            <p className="topp-lead">{opportunity.sentence.text}</p>
          ) : null}

          {/* §4.1 MONEY FLOWING IN. Three status groups, three different
              statements, and the difference between them is the point:
              committed money is summed, announcements are listed and never
              summed (ruled), withdrawals are a named count. */}
          <div className="topp-block">
            <h3>{opp.headings.money_in}</h3>
            {committedFunding.length > 0 ? (
              <>
                <p className="tfunding-total">
                  {eur(totals.committed)} {opp.headings.committed.toLowerCase()} across{" "}
                  {totals.committedCount}{" "}
                  {totals.committedCount === 1 ? "allocation" : "allocations"}
                  {undisclosed > 0
                    ? `, ${undisclosed} of them carrying no published figure`
                    : ""}
                  <span className="tscore-note">{`${SEPARATOR}as of ${committedAsOf}`}</span>
                </p>
                <ul className="tfundings">
                  {committedFunding.map((f) => (
                    <FundingRow key={f.id} f={f} params={params} />
                  ))}
                </ul>
              </>
            ) : null}

            {announcedFunding.length > 0 ? (
              <>
                <h4 className="topp-sub">{opp.headings.announced}</h4>
                {/* NOT SUMMED, and there is no total to render: lib/transition.ts
                    does not compute one. An announcement is a statement of
                    intent, and a euro figure made of intentions reads as money
                    that exists. */}
                <ul className="tfundings">
                  {announcedFunding.map((f) => (
                    <FundingRow key={f.id} f={f} params={params} />
                  ))}
                </ul>
              </>
            ) : null}

            {totals.withdrawnCount > 0 ? (
              <p className="tfunding-total tfunding-withdrawn">
                {totals.withdrawnCount} {opp.headings.withdrawn.toLowerCase()} allocation
                {totals.withdrawnCount === 1 ? "" : "s"}, in no total.
              </p>
            ) : null}
          </div>

          {/* §4.2 RULES THAT PAY. Support-direction measures in the ranking's
              order, each saying what it PAYS in a context-specific template.
              Never the standard one-liner — that sentence belongs to the
              Policies section and to no other, and
              sources/check_one_liner_scope.py fails the build if it appears
              here (brief 5 §5). */}
          {support.length > 0 ? (
            <div className="topp-block">
              <h3>{opp.headings.rules_that_pay}</h3>
              <ul className="topp-pays">
                {support.map((m) => (
                  <li key={m.measure}>
                    <Link href={measureHref(m.measure)}>
                      {m.plain ? m.plain.title : m.measure}
                    </Link>
                    <span className="topp-fact">{supportFact(m, funding, params)}</span>
                    <span className="tmeasure-cite">
                      {FILES[m.file]?.name ?? m.file}
                      {m.article ? ` · ${m.article}` : ""}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      ) : null}

      {present.bottlenecks ? (
        <section className="tmap-section" id="bottlenecks">
          <h2 className="sectionhead">{h2("bottlenecks")}</h2>
          <div className="tbottlenecks">
            {bottlenecks.map((b) => (
              <article key={b.id} id={`bottleneck-${b.id}`} className="tbottleneck">
                <h3>
                  <span className={`ttype ${b.type}`}>{b.type}</span> {b.name}
                </h3>
                <p>{b.description}</p>
                {b.quantified_by.length > 0 ? (
                  <ul className="tparams">
                    {b.quantified_by.map((id) => {
                      const p = params.get(id);
                      return p ? <ParameterChip key={id} p={p} /> : null;
                    })}
                  </ul>
                ) : (
                  <p className="tscore-note">Not quantified yet.</p>
                )}
                {b.addressed_by.length > 0 ? (
                  <p className="taddressed">
                    Addressed by{" "}
                    {b.addressed_by.map((id, i) => (
                      <span key={id}>
                        {i > 0 ? ", " : ""}
                        <a href={`#technology-${id}`}>{id}</a>
                      </span>
                    ))}
                  </p>
                ) : null}
                {/* A measure appears here as a clause under the constraint it
                    bears on and never as an entry of its own — brief 5 §5, the
                    overlap rule. Its standard one-liner is the Policies
                    section's alone. */}
                {b.measures.length > 0 ? (
                  <ul className="tbmeasures">
                    {b.measures.map((m) => (
                      <li key={m.measure}>
                        <span className={`trel ${m.rel}`}>{m.rel}</span>{" "}
                        <Link href={measureHref(m.measure)}>{m.measure}</Link>
                        <span className="tweight">×{m.weight}</span>
                        <span className="tscore-note">{m.note}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="tscore-note">Nothing on the platform moves this one.</p>
                )}
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {present.policies ? (
        <section className="tmap-section" id="policies">
          <h2 className="sectionhead">{h2("policies")}</h2>
          {/* THE TOP FIVE, AND WHAT THEY SAY (brief 4 §5).

              This list used to be every measure in the sector view — eight for
              cement — each with its register id as the heading, the decoded
              provision under it, and a three-column panel showing the money
              model, every bottleneck edge with its weight, and the attention
              count. That is the ranking showing its working, and it is the right
              thing to be able to see; it is the wrong thing to open with. A
              reader who has not read the act cannot tell from `cbam:FIN-03` and
              'satisfy the quarterly certificate-holding requirement' what the
              measure would do to them.

              So: five entries at most, in the ranking's own order, and each one
              says what it requires or grants in a title and one sentence. The
              words are authored and reviewed in
              data/transition/measure_labels.json; the figures inside them are
              computed at build time from the same money block the ranking sorts
              on, so the sentence and the score cannot disagree. The working has
              not been deleted — every measure keeps its own page, linked from
              its title, and the score components are on it.

              THIS IS THE ONLY SECTION THAT RENDERS THE STANDARD ONE-LINER
              (brief 5 §5, gated by sources/check_one_liner_scope.py in step 2).
              Opportunity says what a measure pays with a support template;
              Bottlenecks says what it bears on in a clause. The same measure may
              appear in all three; the same sentence may not appear twice. */}
          <ol className="tmeasures">
            {inView.slice(0, KEY_MEASURES).map((m) => (
              <li key={m.measure} id={`measure-${m.file}-${m.id}`}>
                <h3 className="tmeasure-title">
                  <Link href={measureHref(m.measure)}>{m.plain ? m.plain.title : m.measure}</Link>
                </h3>
                {m.plain ? <p className="tmeasure-plain">{m.plain.sentence}</p> : null}
                <p className="tmeasure-cite">
                  {FILES[m.file]?.name ?? m.file}
                  {m.article ? ` · ${m.article}` : ""}
                  {m.when ? ` · ${m.when}` : ""}
                </p>
              </li>
            ))}
          </ol>
          {/* NET POSITION IS BUILT AND NOT DRAWN (brief 4 §5, and it stays
              hidden under brief 5 §2). The table lived here: cost, support and
              net per bearer and per scale, out of imp.net. It is still computed
              by sources/build_importance.py, still gated by
              sources/check_importance.py, and still in
              data/transition/importance/<sector>.json — this page does not
              render it. What it showed was a netting a reader cannot check
              without the schema in front of them, at the top of the page,
              immediately after four sentences written so they would not need
              it. */}
        </section>
      ) : null}

      {present.feed ? (
        <section className="tmap-section" id="feed">
          <h2 className="sectionhead">{h2("feed")}</h2>
          {/* §4.6 OPPORTUNITY SIGNALS. Not a feed of its own and not a new data
              structure: a filter over the change records, for the ones whose
              object is a funding node, a support-direction measure or (from
              step 3) a measure that creates demand. It renders only where this
              sector HAS one — a filter chip that filters to nothing is a
              promise the data does not keep — and it opens the change-record
              list with the same filter as a query parameter. */}
          {signals.length > 0 ? (
            <p className="topp-signals">
              <Link href={`/changes?opportunity=1`} className="chip">
                {opp.signals.chip}
                <span className="chip-count">{signals.length}</span>
              </Link>
            </p>
          ) : null}
          {/* WHAT MOVED HERE, last 30 days. The home strip says what moved
              anywhere; this says what moved in this sector, which is the
              question somebody on this page is actually asking.

              AN EMPTY WINDOW IS A FACT AND IT IS PRINTED — and note what that
              is not. Brief 5 §2 omits a section with NO DATA; a sector with a
              status history and a quiet month has data, and the fact that
              nothing has happened in thirty days is one of the more useful
              things this page can tell a reader. So the section renders
              whenever the sector has ever moved, and says when it last did. */}
          {moved.length > 0 ? (
            <ul className="tmoved-list">
              {moved.map(({ project, event }) => (
                <li key={project.id}>
                  <span className="tmoved-date">{event.date}</span>
                  <Link href={projectHref(project.id)}>{project.name}</Link>
                  <span className="tmoved-to">{STATUS_LABEL[event.status]}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="tmoved-quiet">
              Nothing in the last {MOVED_WINDOW_DAYS} days.
              {latestMove ? (
                <>
                  {" "}
                  The last change was{" "}
                  <Link href={projectHref(latestMove.project.id)}>{latestMove.project.name}</Link>{" "}
                  to {STATUS_LABEL[latestMove.event.status]} on{" "}
                  <span className="tmoved-date">{latestMove.event.date}</span>.
                </>
              ) : null}
            </p>
          )}
        </section>
      ) : null}

      {present.connections ? (
        <section className="tmap-section" id="connections">
          <h2 className="sectionhead">{h2("connections")}</h2>
          {diagram ? (
            <>
              {/* TWO DIAGRAMS, ONE PICTURE. Above the breakpoint the interactive
                  component; below it the flat SVG the same builder writes, linked
                  so a tap opens it full size. A phone gets no hover, cannot fit
                  four columns, and would be pinching at a 1160-unit canvas inside a
                  375-point viewport — so it gets the file instead of the widget,
                  and the widget is not rendered there at all. */}
              <div className="tdiagram-interactive">
                <TransitionDiagram
                  diagram={diagram}
                  sources={nodeSources}
                  pageUrl={`eufabric.eu/sectors/${slug}`}
                />
              </div>
              <figure className="tdiagram-static">
                <a href={`/diagrams/${slug.replace("/", "__")}.svg`}>
                  {/* eslint-disable-next-line @next/next/no-img-element -- a built
                      SVG of known size; the optimiser has nothing to add and would
                      rasterise it. */}
                  <img
                    src={`/diagrams/${slug.replace("/", "__")}.svg`}
                    width={diagram.width}
                    height={diagram.height + 34}
                    alt={`${name}: the measures, bottlenecks, technologies and projects on this page, and how they connect`}
                  />
                </a>
                <figcaption>Tap to open full size. The hover detail is on the desktop view.</figcaption>
              </figure>
            </>
          ) : null}
          {related.length > 0 ? (
            <div className="trelated">
              <h3>Most often caught by the same measure</h3>
              {/* Computed from the register, not curated: two sectors are
                  related here because the corpus keeps naming them together. */}
              <div className="chips">
                {related.map((s) => (
                  <Link key={s.slug} href={`/sectors/${s.slug}`} className="chip">
                    {s.name}
                    <span className="chip-count">{s.count}</span>
                  </Link>
                ))}
              </div>
            </div>
          ) : null}
        </section>
      ) : null}

      {/* SOURCES IS NOT ONE OF THE NUMBERED SECTIONS and is not in the nav.
          Page specifications §0.5 makes it the final section of every sector
          page; brief 5 §2 numbers nine questions and this is not one of them —
          it answers "what does this page stand on", which is a question about
          the page rather than about the industry. So it renders last on the
          same footing as the lead block renders first, and §2 is amended to say
          so in step 6 of the order of work. */}
      <section className="tmap-section" id="sources">
        <h2 className="sectionhead">{getUnnumberedH2("sources")}</h2>
        <p className="tmap-sub">
          Every outbound URL on this page, grouped by publisher. The build fails on a dead one.
        </p>
        <div className="tsources">
          {grouped.map((g) => (
            <div key={g.publisher}>
              <h3>{g.publisher}</h3>
              <ul>
                {g.sources.map((s) => (
                  <li key={s.url}>
                    {/* THE URL IS IN href AND NOWHERE ELSE. The anchor text is a
                        citation — a title for a document, what was asked of a
                        dataset for an api — and never the address it was asked
                        at. See lib/citation.ts. */}
                    <a href={s.url} target="_blank" rel="noreferrer">
                      {citation(s)}
                    </a>
                    {/* A separator a reader can see and a copy keeps, rather
                        than two strings run together. */}
                    {s.date ? (
                      <span className="tscore-note">{`${SEPARATOR}${s.date}`}</span>
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

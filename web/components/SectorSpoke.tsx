import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import TransitionDiagram, { type Diagram, type NodeSource } from "@/components/TransitionDiagram";
import { citation } from "@/lib/citation";
import { FILES, SECTORS, getRelatedSectors } from "@/lib/data";
import { atPrecision } from "@/lib/dates";
import { sectorDependencies, sectorPolicyRows, sectorProjectRows, sectorSupportRows } from "@/lib/hub";
import { supportFact } from "@/lib/opportunity";
import { getRecordsForSector, recordHref } from "@/lib/records";
import { sectorCompanies, spokeTitle, type SpokeId } from "@/lib/spokes";
import {
  STATUS_LABEL,
  eur,
  fundingForProject,
  fundingTotals,
  getBottlenecks,
  getFunding,
  getParameters,
  getTechnologies,
  getTechnology,
  lastChange,
  materialFlows,
  measureHref,
  projectHref,
  type MaterialFlow,
  type Parameter,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// THE SPOKE PAGES. One template, six lists — brief 15.
//
// WHAT THEY ARE FOR. The hub used to carry every project, every technology,
// every material and every constraint, and linked to nothing, because there was
// nowhere to link to. A complete list is a good thing to be able to read and a
// bad thing to open a page with. So the complete lists are here, one per
// question, and the hub carries the top of each and a link.
//
// THE COUNT IS NOT COMPUTED TWICE. Every list below comes from the same
// function the hub's block is built from (lib/hub.ts), which is what makes
// "All 34 projects" on the hub and 34 rows here one fact rather than two that
// agree today.
//
// DEMOTED, ALL SIX. noindex, follow: the crawler walks through, and the URL a
// stranger meets in search is the hub. See app/sectors/[...slug]/page.tsx for
// the robots tag and lib/routes.ts for why they stay out of the sitemap.

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

/** One of the three material lists, unchanged from the section it moved off.
 *
 *  EVERY ITEM SHOWS ITS BASIS: the count of plants behind the edge, or the
 *  sector-level edge where the claim is about the industry as a whole, linking
 *  to the set that count is of. */
function MaterialList({
  title,
  rows,
  anchor,
}: {
  title: string;
  rows: MaterialFlow[];
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
              {anchor === null ? (
                <span className="tmat-basis">
                  for {m.substitutes.map((sub) => sub.material).join(", ")}
                </span>
              ) : null}
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

function ProjectsSpoke({ slug }: { slug: SectorSlug }) {
  const rows = sectorProjectRows(slug);
  const params = getParameters();
  return (
    <>
      <p className="tmap-sub">
        Sorted by last status change, the same order the hub&apos;s block is the top of. Every
        change carries its source.
      </p>
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
            {rows.map((p) => {
              const last = lastChange(p);
              const money = fundingTotals(fundingForProject(p.id), params);
              return (
                <tr key={p.id}>
                  <td>
                    <Link href={projectHref(p.id)}>{p.name}</Link>
                  </td>
                  <td>{p.company}</td>
                  <td>{p.plant ?? "—"}</td>
                  <td>{p.country}</td>
                  {/* THE NODE'S LABEL, NOT ITS ID. This cell printed the raw
                      technology ids off the row — including
                      `ccs-capture-unspecified`, which is a placeholder and has
                      no business being displayed at all. It now prints what the
                      technology is called, and drops a placeholder rather than
                      naming it. */}
                  <td className="ttech-cell">{technologyLabels(p.technology).join(", ") || "—"}</td>
                  <td>
                    <span className={`tstatus ${p.status}`}>{STATUS_LABEL[p.status]}</span>
                  </td>
                  <td className="num">
                    {money.committed
                      ? eur(money.committed)
                      : money.committedCount
                        ? "undisclosed"
                        : "—"}
                  </td>
                  {/* AT THE PRECISION THE REGISTER KNOWS IT: a year-precision
                      event renders as its year, never as a padded 01-01. */}
                  <td className="num">
                    {last ? atPrecision(last.date, last.date_precision) : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

/** A technology id said in the reader's words. A placeholder has no label
 *  worth printing and is dropped: `ccs-capture-unspecified` is the register
 *  saying it does not yet know which capture route, and a reader shown the id
 *  learns nothing but that the site prints ids. */
function technologyLabels(ids: string[]): string[] {
  const out: string[] = [];
  for (const id of ids) {
    const t = technologyById(id);
    if (!t || t.placeholder) continue;
    out.push(t.name);
  }
  return out;
}

/** Any technology by id, not only this sector's: a cement row may carry a
 *  technology whose own sector edge is elsewhere, and it still has a name. */
function technologyById(id: string) {
  return getTechnology(id);
}

function DependenciesSpoke({ slug }: { slug: SectorSlug }) {
  const technologies = getTechnologies(slug);
  const flows = materialFlows(slug);
  const bottlenecks = getBottlenecks(slug);
  const dependencyCount = sectorDependencies(slug).length;
  const materialLists = [...flows.inputs, ...flows.outputs, ...flows.substitutes];
  const materialRows = materialLists.length;
  const materialNodes = new Set(materialLists.map((r) => r.material.id)).size;
  const params = getParameters();
  const projectsByTech = new Map<string, { id: string; name: string }[]>();
  for (const p of sectorProjectRows(slug))
    for (const t of p.technology) {
      if (!projectsByTech.has(t)) projectsByTech.set(t, []);
      projectsByTech.get(t)!.push({ id: p.id, name: p.name });
    }

  return (
    <>
      {/* THE TWO NUMBERS, BOTH STATED, because they differ and a reader can see
          that they do. A DEPENDENCY IS A NODE and is counted once — which is
          what the hub's "All {n} dependencies" promises and what
          `sectorDependencies` returns. The material section below is the
          sector's FLOW, and a material that both arrives and leaves appears in
          two of its lists on the strength of two distinct edges: steel's
          directly reduced iron is made here and consumed here, and its
          granulated blast furnace slag leaves as a by-product and stands in for
          clinker. materialFlows() refuses to list one twice on the SAME edge
          (assertDisjoint); listing it twice on different ones is the fact, not
          a fault, and the sentence says so rather than leaving a reader to count
          six rows under a link that promised four materials. */}
      <p className="tmap-sub">
        Technologies, materials and constraints in one list, because a reader asking what a
        sector depends on is asking one question. {dependencyCount} in total
        {materialRows > materialNodes
          ? `, of which ${materialNodes} are materials — shown on ${materialRows} rows, because ${
              materialRows - materialNodes === 1 ? "one of them appears" : `${materialRows - materialNodes} of them appear`
            } in two lists on separate edges`
          : ""}
        .
      </p>

      {technologies.length > 0 ? (
        <div className="ttechs">
          <h2 className="sectionhead">Technologies</h2>
          {technologies.map((t) => (
            <article key={t.id} id={`technology-${t.id}`} className="ttech">
              <h3>
                {t.name}{" "}
                {t.readiness ? (
                  <span className={`tready ${t.readiness.level}`}>{t.readiness.level}</span>
                ) : null}
              </h3>
              <p>{t.description}</p>
              <dl>
                {t.readiness ? (
                  <>
                    <dt>Readiness</dt>
                    <dd>
                      {t.readiness.level}
                      {t.readiness.note ? ` — ${t.readiness.note}` : ""}{" "}
                      <a href={t.readiness.source} target="_blank" rel="noreferrer">
                        source
                      </a>{" "}
                      ({t.readiness.date})
                    </dd>
                  </>
                ) : null}
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
                {(t.dependency ?? []).length > 0 ? (
                  <>
                    <dt>Depends on</dt>
                    <dd>
                      {technologyLabels(t.dependency ?? []).map((label, i) => (
                        <span key={label}>
                          {i > 0 ? ", " : ""}
                          {label}
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
      ) : null}

      {flows.inputs.length + flows.outputs.length + flows.substitutes.length > 0 ? (
        <div className="tmatlists">
          <h2 className="sectionhead">Materials</h2>
          <p className="tmap-sub">
            What arrives, what leaves, and what could stand in for it. Every material is a
            cross-sector node, so each one opens its own page rather than a list of this
            sector&apos;s copy of it.
          </p>
          <MaterialList title="Inputs" rows={flows.inputs} anchor="consumed-by" />
          <MaterialList title="Outputs and by-products" rows={flows.outputs} anchor="produced-by" />
          <MaterialList title="Substitutes" rows={flows.substitutes} anchor={null} />
        </div>
      ) : null}

      {bottlenecks.length > 0 ? (
        <div className="tbottlenecks">
          <h2 className="sectionhead">Constraints</h2>
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
                      <a href={`#technology-${id}`}>{technologyById(id)?.name ?? id}</a>
                    </span>
                  ))}
                </p>
              ) : null}
              {/* A measure appears here as a clause under the constraint it
                  bears on and never as an entry of its own — the overlap rule
                  from brief 5 §5, unchanged. Its standard one-liner belongs to
                  the policies list and to nothing else. */}
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
      ) : null}
    </>
  );
}

function PoliciesSpoke({ slug }: { slug: SectorSlug }) {
  const rows = sectorPolicyRows(slug);
  const support = sectorSupportRows(slug);
  const funding = getFunding(slug);
  const params = getParameters();
  return (
    <>
      <p className="tmap-sub">
        Every measure in this sector&apos;s view, in the ranking&apos;s order. The score
        components behind the order are on each measure&apos;s own page.
      </p>
      <ol className="tmeasures">
        {rows.map((m) => (
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

      {/* THE SUPPORT-DIRECTION FILTER, and the destination of the hub's
          Opportunity link. Opportunity has no spoke of its own; what it lists
          are measures, and every measure is here. Each says what it PAYS in a
          context-specific template and never the standard one-liner — that
          sentence belongs to the list above and to nothing else, and
          sources/check_one_liner_scope.py fails the build if it appears
          twice. */}
      {support.length > 0 ? (
        <div className="topp-block" id="support">
          <h2 className="sectionhead">Measures that pay</h2>
          <ul className="topp-pays">
            {support.map((m) => (
              <li key={m.measure}>
                <Link href={measureHref(m.measure)}>{m.plain ? m.plain.title : m.measure}</Link>
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
    </>
  );
}

function CompaniesSpoke({ slug }: { slug: SectorSlug }) {
  const rows = sectorCompanies(slug);
  const byId = new Map(sectorProjectRows(slug).map((p) => [p.id, p]));
  return (
    <>
      <p className="tmap-sub">
        Computed from the project register, not curated: a company is here because it holds a
        tracked project, and the count beside it is that project list. A company is not a node
        kind on this platform yet, so this page is a list of rows rather than a set of pages.
      </p>
      <ul className="tcompanies">
        {rows.map((c) => (
          <li key={c.name}>
            <span className="tcompany-name">{c.name}</span>
            <span className="tcompany-projects">
              {c.projects.map((id, i) => (
                <span key={id}>
                  {i > 0 ? ", " : ""}
                  <Link href={projectHref(id)}>{byId.get(id)?.name ?? id}</Link>
                </span>
              ))}
            </span>
          </li>
        ))}
      </ul>
    </>
  );
}

function ConnectionsSpoke({ slug }: { slug: SectorSlug }) {
  const name = SECTORS[slug];
  const related = getRelatedSectors(slug);
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
  const cited = (rows: { url: string; publisher: string; date?: string }[]): NodeSource[] =>
    rows.map((s) => ({ ...s, title: citation(s) }));
  for (const b of getBottlenecks(slug)) nodeSources[`bottleneck:${b.id}`] = cited(b.sources);
  for (const t of getTechnologies(slug)) nodeSources[`technology:${t.id}`] = cited(t.sources);
  for (const p of sectorProjectRows(slug)) nodeSources[`project:${p.id}`] = cited(p.sources);
  for (const m of sectorPolicyRows(slug)) {
    const q = m.bottleneck_linkage.edges[0]?.evidence;
    nodeSources[`measure:${m.measure}`] = [
      {
        url: measureHref(m.measure),
        title: m.article ?? m.measure,
        publisher: q ? q.source : `data/${m.file}.json`,
      },
    ];
  }

  return (
    <>
      {diagram ? (
        <>
          {/* TWO DIAGRAMS, ONE PICTURE. Above the breakpoint the interactive
              component; below it the flat SVG the same builder writes, linked
              so a tap opens it full size. */}
          <div className="tdiagram-interactive">
            <TransitionDiagram
              diagram={diagram}
              sources={nodeSources}
              pageUrl={`eufabric.eu/sectors/${slug}/connections`}
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
                alt={`${name}: the measures, constraints, technologies and projects on this sector's pages, and how they connect`}
              />
            </a>
            <figcaption>Tap to open full size. The hover detail is on the desktop view.</figcaption>
          </figure>
        </>
      ) : (
        <p className="tmap-sub">No diagram is built for this sector.</p>
      )}
      {related.length > 0 ? (
        <div className="trelated">
          <h2 className="sectionhead">Most often caught by the same measure</h2>
          {/* Computed from the register, not curated: two sectors are related
              here because the corpus keeps naming them together. */}
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
    </>
  );
}

function ChangesSpoke({ slug }: { slug: SectorSlug }) {
  const records = getRecordsForSector(slug);
  return (
    <>
      <p className="tmap-sub">
        One record per legislative event reaching this sector, most recent first. A record is
        written when the change enters the platform and is not revised afterwards.
      </p>
      {records.length > 0 ? (
        <ul className="tmoved-list">
          {records.map((r) => (
            <li key={r.id}>
              <span className="tmoved-date">{r.event_date}</span>
              <Link href={recordHref(r.id)}>{r.headline}</Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="tmoved-quiet">No change record names this sector yet.</p>
      )}
    </>
  );
}

const BODIES: Record<SpokeId, (props: { slug: SectorSlug }) => React.ReactNode> = {
  projects: ProjectsSpoke,
  technologies: DependenciesSpoke,
  policies: PoliciesSpoke,
  companies: CompaniesSpoke,
  connections: ConnectionsSpoke,
  changes: ChangesSpoke,
};

export default function SectorSpoke({ slug, spoke }: { slug: SectorSlug; spoke: SpokeId }) {
  const name = SECTORS[slug];
  const Body = BODIES[spoke];
  return (
    <main className="rise sector-map" style={{ ["--accent" as string]: `var(${accentVar(slug)})` }}>
      <div className="wrap">
        <Crumbs
          trail={[
            { label: "Sectors", href: "/sectors" },
            { label: name, href: `/sectors/${slug}` },
            { label: spokeTitle(slug, spoke) },
          ]}
        />
        <header className="tmap-head">
          <h1>
            <SectorIcon slug={slug} size={28} /> {spokeTitle(slug, spoke)}
          </h1>
        </header>
        <section className="tmap-section">
          <Body slug={slug} />
        </section>
        <nav className="tmap-footer" aria-label="Back to the sector">
          <Link href={`/sectors/${slug}`}>← {name}</Link>
        </nav>
      </div>
    </main>
  );
}

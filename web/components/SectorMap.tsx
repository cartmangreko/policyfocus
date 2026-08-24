import fs from "node:fs";
import path from "node:path";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import LeadBlock from "@/components/LeadBlock";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import TransitionDiagram, { type Diagram, type NodeSource } from "@/components/TransitionDiagram";
import { SECTORS } from "@/lib/data";
import { transitionProse } from "@/lib/prose";
import { getSectorOrientation, getTransitionNote } from "@/lib/sitetext";
import {
  BEARER_LABEL,
  STATUS_LABEL,
  TRANSITION_LABEL,
  byLastChange,
  eur,
  fundingAmount,
  fundingForProject,
  getBottlenecks,
  getFunding,
  getMaterials,
  getImportance,
  getLead,
  getParameters,
  getProjects,
  getProject,
  getTechnologies,
  getTechnology,
  getTransitions,
  lastChange,
  measureHref,
  projectHref,
  sourcesForSector,
  type Material,
  type Parameter,
  type StatusEvent,
  type RankedMeasure,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// The sector page: the product, and the only template that answers the whole
// question. Seven sections, in this order and no other:
//
//   1  the lead block — the sentence, why it matters, and the five facts
//   2  the diagram — the same seven sections as a picture
//   3  key measures, ranked, with the score components visible
//   4  bottlenecks, typed, with their parameters and the technologies that address them
//   5  technologies, with readiness, cost and who is deploying them
//   6  materials — what the sector makes, consumes and throws off
//   7  projects, sorted by last status change, with the funding rollup
//   8  every source used on the page, grouped by publisher
//
// The order is the argument: law, then what the law is up against, then what
// gets past it, then who is actually building. Sections 3-6 repeat per
// transition where a sector carries more than one; cement carries one, so the
// loop runs once and the heading says so rather than the layout implying it.
//
// NOTHING HERE COMPUTES A RANKING OR A EURO. Both come from
// data/transition/importance/<sector>.json, built and gated in Python. This
// file decides what is shown and in what order, which is enough
// responsibility for one component.

function ScoreComponents({ m }: { m: RankedMeasure }) {
  const money = m.money;
  return (
    <div className="tscore">
      <div className="tscore-cell">
        <span className="tscore-label">Money</span>
        {money.computable ? (
          <>
            <span className={`tdir ${money.direction}`}>
              {money.direction} → {BEARER_LABEL[money.bearer ?? ""] ?? money.bearer}
            </span>
            <span className="tscore-figure">
              {money.per_tonne !== null ? `${eur(money.per_tonne)} / t` : eur(money.value ?? 0)}
            </span>
            {money.annual_total ? (
              <span className="tscore-note">{eur(money.annual_total)} a year</span>
            ) : null}
            {money.context.map((c) => (
              <span key={c.label} className="tscore-note">
                {c.label}: {eur(c.value)}
                {c.detail ? ` — ${c.detail}` : ""}
              </span>
            ))}
            <span className="tscore-formula">{money.formula}</span>
            {money.caveats.map((c) => (
              <span key={c} className="tscore-caveat">
                {c}
              </span>
            ))}
          </>
        ) : (
          <>
            <span className="tscore-figure none">—</span>
            <span className="tscore-note">
              {money.model
                ? `${money.model}: needs ${money.missing.join(", ")}`
                : "no money model applies"}
            </span>
          </>
        )}
      </div>

      <div className="tscore-cell">
        <span className="tscore-label">Bottleneck linkage</span>
        <span className="tscore-figure">{m.bottleneck_linkage.weight}</span>
        <ul className="tscore-edges">
          {m.bottleneck_linkage.edges.map((e) => (
            <li key={e.bottleneck}>
              <span className={`trel ${e.rel}`}>{e.rel}</span>{" "}
              <a href={`#bottleneck-${e.bottleneck}`}>{e.bottleneck_name}</a>
              <span className="tweight">×{e.weight}</span>
              <span className="tscore-note">{e.note}</span>
            </li>
          ))}
          {m.bottleneck_linkage.edges.length === 0 ? (
            <li className="tscore-note">No bottleneck edge.</li>
          ) : null}
        </ul>
      </div>

      <div className="tscore-cell">
        <span className="tscore-label">Attention</span>
        <span className="tscore-figure none">{m.attention.available ? m.attention.count : "—"}</span>
        <span className="tscore-note">
          {m.attention.available
            ? `mentions in ${m.attention.window_months} months`
            : "the watch agent's project channel has not run, so this ranking has no cross-check"}
        </span>
      </div>
    </div>
  );
}

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

/** Every sourced volume attached to a material's edges, deduplicated. The
 *  material states no number of its own — each one is a parameter id, and the
 *  chip renders the parameter with its quote and its source. */
function volumes(m: Material): string[] {
  const ids = [...m.produced_by, ...m.consumed_by, ...m.required_by]
    .map((e) => e.volume)
    .filter((v): v is string => Boolean(v));
  return [...new Set(ids)];
}

export default function SectorMap({ slug }: { slug: SectorSlug }) {
  const name = SECTORS[slug];
  const imp = getImportance(slug)!;
  const bottlenecks = getBottlenecks(slug);
  const technologies = getTechnologies(slug);
  const projects = byLastChange(getProjects(slug));
  const params = getParameters();
  const materials = getMaterials(slug);
  const funding = getFunding(slug);
  // The rollup, derived here and stored nowhere. `undisclosed` is counted
  // separately rather than folded in as zero: a grant nobody published is not
  // a grant of nothing, and a total that pretended otherwise would read as
  // complete.
  const fundingTotal = funding.reduce((a, f) => a + (fundingAmount(f, params) ?? 0), 0);
  const undisclosed = funding.filter((f) => fundingAmount(f, params) === null).length;
  const transitions = getTransitions(slug);

  // Status changes in this sector inside the window, most recent first, and
  // the most recent change of any age for the empty state. `lastChange` is the
  // same helper the home feed uses, so the two strips cannot disagree about
  // what the latest event is.
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
  for (const b of bottlenecks) nodeSources[`bottleneck:${b.id}`] = b.sources;
  for (const t of technologies) nodeSources[`technology:${t.id}`] = t.sources;
  for (const p of projects) nodeSources[`project:${p.id}`] = p.sources;
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

  return (
    <main className="rise sector-map" style={{ ["--accent" as string]: `var(${accentVar(slug)})` }}>
      <div className="wrap">
      <Crumbs trail={[{ label: "Sectors", href: "/sectors" }, { label: name }]} />

      <header className="tmap-head">
        <h1>
          <SectorIcon slug={slug} size={28} /> {name}
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

      {/* WHAT MOVED HERE, last 30 days. The home strip says what moved anywhere;
          this says what moved in this sector, which is the question somebody on
          this page is actually asking.

          AN EMPTY WINDOW IS A FACT AND IT IS PRINTED. Most sectors will have
          nothing in thirty days most of the time, and a strip that vanished
          when empty would leave a reader unable to tell "nothing happened" from
          "we stopped looking". So the empty state names the last thing that did
          happen, and dates it. */}
      <section className="tmoved" aria-label="What moved in this sector">
        <h2>What moved</h2>
        {moved.length > 0 ? (
          <ul>
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
                <Link href={projectHref(latestMove.project.id)}>
                  {latestMove.project.name}
                </Link>{" "}
                to {STATUS_LABEL[latestMove.event.status]} on{" "}
                <span className="tmoved-date">{latestMove.event.date}</span>.
              </>
            ) : null}
          </p>
        )}
      </section>

      {diagram ? (
        <section className="tmap-section" id="map">
          <h2>How it connects</h2>
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
        </section>
      ) : null}

      <section className="tmap-section" id="measures">
        <h2>Key measures</h2>
        <p className="tmap-sub">
          {inView.length} of {imp.measures.length} measures reaching the sector carry money or a
          named constraint. Ranked on money first, then linkage; priced at {imp.priced_year}.
        </p>
        <ol className="tmeasures">
          {inView.map((m) => (
            <li key={m.measure} id={`measure-${m.file}-${m.id}`}>
              <div className="tmeasure-head">
                <span className="trank">{m.override_rank ?? m.rank}</span>
                <Link href={measureHref(m.measure)} className="tmeasure-id">
                  {m.measure}
                </Link>
                <span className="tmtype">{m.measure_type}</span>
                {m.reach === "funding" ? (
                  <span className="treach">
                    reaches the sector through funding: {m.reached_via.join(", ")}
                  </span>
                ) : null}
              </div>
              <p className="tmeasure-duty">{m.duty}</p>
              <p className="tmeasure-cite">
                {m.article}
                {m.when ? ` · ${m.when}` : ""}
              </p>
              {m.override_reason ? (
                <p className="toverride">
                  Ranked by hand at {m.override_rank}: {m.override_reason}
                </p>
              ) : null}
              <ScoreComponents m={m} />
            </li>
          ))}
        </ol>
        {imp.net.buckets.length > 0 ? (
          <div className="tnet">
            <h3>Net position</h3>
            <table>
              <thead>
                <tr>
                  <th>Bearer</th>
                  <th>Cost</th>
                  <th>Support</th>
                  <th>Net</th>
                </tr>
              </thead>
              <tbody>
                {imp.net.buckets.map((b) => (
                  <tr key={`${b.scale}-${b.bearer}`}>
                    <td>
                      {BEARER_LABEL[b.bearer] ?? b.bearer}
                      <span className="tscore-note">
                        {b.scale === "eur_per_tonne" ? "per tonne" : "awarded, cumulative"}
                      </span>
                    </td>
                    <td className="num">{b.cost ? eur(b.cost) : "—"}</td>
                    <td className="num">{b.support ? eur(b.support) : "—"}</td>
                    <td className={`num ${b.net < 0 ? "neg" : "pos"}`}>
                      {eur(Math.abs(b.net))} {b.net < 0 ? "out" : "in"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="tscore-note">{imp.net._note}</p>
          </div>
        ) : null}
      </section>

      <section className="tmap-section" id="bottlenecks">
        <h2>Bottlenecks</h2>
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
                <p className="tscore-note">
                  Not quantified yet.
                </p>
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

      <section className="tmap-section" id="technologies">
        <h2>Technologies</h2>
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

      <section className="tmap-section" id="materials">
        <h2>Materials</h2>
        <p className="tmap-sub">
          What the sector makes, consumes and throws off, and the volumes anybody has
          published. Every edge names the document it was read from.
        </p>
        {materials.length === 0 ? (
          <p className="tscore-note">No material recorded for this sector yet.</p>
        ) : (
          <div className="tmaterials">
            {materials.map((m) => (
              <article key={m.id} id={`material-${m.id}`} className="tmaterial">
                <h3>
                  {m.name} <span className={`tmat-type ${m.type}`}>{m.type.replace("_", " ")}</span>
                </h3>
                <p>{m.description}</p>
                <dl>
                  {m.cn_code ? (
                    <>
                      <dt>CN code</dt>
                      <dd className="mono">{m.cn_code}</dd>
                    </>
                  ) : null}
                  {m.produced_by.length > 0 ? (
                    <>
                      <dt>Produced by</dt>
                      <dd>{m.produced_by.map((e) => nodeLabel(e.node)).join(", ")}</dd>
                    </>
                  ) : null}
                  {m.consumed_by.length > 0 ? (
                    <>
                      <dt>Consumed by</dt>
                      <dd>{m.consumed_by.map((e) => nodeLabel(e.node)).join(", ")}</dd>
                    </>
                  ) : null}
                  {volumes(m).length > 0 ? (
                    <>
                      <dt>Volumes</dt>
                      <dd>
                        <ul className="tparams">
                          {volumes(m).map((id) => {
                            const q = params.get(id);
                            return q ? <ParameterChip key={id} p={q} /> : null;
                          })}
                        </ul>
                      </dd>
                    </>
                  ) : null}
                </dl>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="tmap-section" id="funding">
        <h2>Capital</h2>
        <p className="tmap-sub">
          Every allocation that finances a project here, with the basis it was made under
          and how far it has got. Amounts are the published ones; an undisclosed amount is
          shown as undisclosed rather than as nothing.
        </p>
        {funding.length === 0 ? (
          <p className="tscore-note">No public capital recorded for this sector yet.</p>
        ) : (
          <>
            <p className="tfunding-total">
              {eur(fundingTotal)} recorded across {funding.length} allocations
              {undisclosed > 0 ? `, ${undisclosed} of them undisclosed` : ""}.
            </p>
            <ul className="tfundings">
              {funding.map((f) => {
                const amount = fundingAmount(f, params);
                return (
                  <li key={f.id} id={`funding-${f.id}`}>
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
              })}
            </ul>
          </>
        )}
      </section>

      <section className="tmap-section" id="projects">
        <h2>Projects</h2>
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
                const funded = rows.reduce((a, f) => a + (fundingAmount(f, params) ?? 0), 0);
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
                      {funded ? eur(funded) : rows.length ? "undisclosed" : "—"}
                    </td>
                    <td className="num">{last?.date ?? "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="tmap-section" id="sources">
        <h2>Sources</h2>
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
                    <a href={s.url} target="_blank" rel="noreferrer">
                      {s.title ?? s.url}
                    </a>
                    {s.date ? <span className="tscore-note">{s.date}</span> : null}
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

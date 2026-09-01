import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Crumbs from "@/components/Crumbs";
import { citation } from "@/lib/citation";
import LeadBlock from "@/components/LeadBlock";
import LocationMap from "@/components/LocationMap";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import { SECTORS } from "@/lib/data";
import { getProjectLead } from "@/lib/objectLeads";
import { getProjectMap } from "@/lib/maps";
import { projectGeoProse } from "@/lib/prose";
import {
  STATUS_LABEL,
  TRANSITION_LABEL,
  eur,
  fundingAmount,
  fundingForProject,
  getParameters,
  getProject,
  getProjects,
  getTechnology,
  measureHref,
  statusTransitions,
  type ProjectStatus,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// One installation, and what has happened to it. Five blocks and nothing else:
// header, status timeline, technology and measures, funding, sources.
//
// THE TIMELINE IS THE PAGE. Everything else here is also on the sector page in
// some form; the status history is not, and it is the thing that changes. It
// is append-only in the data and drawn in order, with every entry carrying the
// link that evidences it — a status somebody cannot check is a status this
// project has no business asserting about a real company's plant.
//
// A ONE-ENTRY TIMELINE IS NOT A BUG. Several projects begin at the grant or
// the groundbreaking because no primary source for anything earlier has been
// read. The strip says what was verified rather than implying a project sprang
// into being fully funded.

export const dynamicParams = false;

export function generateStaticParams() {
  return getProjects().map((p) => ({ id: p.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const p = getProject((await params).id);
  if (!p) return { title: "Project not found" };
  return {
    title: `${p.name} — ${p.company}`,
    description:
      `${p.name}, ${p.company}'s ${p.plant ?? p.country} project: ` +
      `${STATUS_LABEL[p.status].toLowerCase()} as of ` +
      `${p.status_history[p.status_history.length - 1]?.date}, deploying ` +
      `${p.technology.join(", ")}.`,
  };
}

const FLOW: ProjectStatus[] = ["announced", "funded", "fid", "construction", "operating"];

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const project = getProject((await params).id);
  if (!project) notFound();

  const lead = getProjectLead(project.id);
  // The regional crop. Absent only if the build has not run — which the
  // prebuild gate makes impossible — so there is no empty state to design.
  const frame = getProjectMap(project.id);
  const geo = frame
    ? projectGeoProse({
        label: project.name,
        place: project.location.map((s) => s.site).join(" and "),
        sites: project.location.length,
        dependency: frame.marks.filter((m) => m.relation === "dependency").length,
        technology: frame.marks.filter((m) => m.relation === "technology").length,
        sector: frame.marks.filter((m) => m.relation === "sector").length,
        // A cancelled subject is drawn on this crop and on no other frame. The
        // standfirst says so and the key repeats it against the ring, because
        // nothing about the mark itself distinguishes it from a hollow
        // neighbour that IS drawn elsewhere.
        subjectCancelled: project.status === "cancelled",
      })
    : null;

  const sector = project.sector as SectorSlug;
  const allParams = getParameters();
  const funding = fundingForProject(project.id);
  const reached = new Set(project.status_history.map((h) => h.status));
  // The rail shows the ordinary forward path, with anything off it — paused,
  // cancelled — appended, so a stopped project reads as stopped rather than as
  // a project that never got going.
  const offFlow = project.status_history
    .map((h) => h.status)
    .filter((s) => !FLOW.includes(s));
  const rail = [...FLOW, ...new Set(offFlow)];
  // THE RAIL DATES A STATUS FROM WHEN IT WAS ENTERED. Built off the whole
  // history, a repeated status would take the date of the LAST entry carrying
  // it — so Slite's "Paused" rung would read 1 January 2026, the date its permit
  // application was withdrawn, rather than 19 November 2025, the date it was
  // paused. The full history is still drawn underneath, both entries and both
  // sources; it is only the rung that has to name the moment.
  const dateOf = new Map(statusTransitions(project).map((h) => [h.status, h.date]));

  return (
    <main className="rise project-page" style={{ ["--accent" as string]: `var(${accentVar(sector)})` }}>
      <div className="wrap">
        <Crumbs
          trail={[
            { label: "Sectors", href: "/sectors" },
            { label: SECTORS[sector], href: `/sectors/${sector}` },
            { label: project.name },
          ]}
        />

        <header className="proj-head">
          <h1>{project.name}</h1>
          <p className="proj-who">
            {project.company} · {project.plant ?? "—"} · {project.country} ·{" "}
            <Link href={`/sectors/${sector}`}>
              <SectorIcon slug={sector} size={14} /> {SECTORS[sector]}
            </Link>{" "}
            · {TRANSITION_LABEL[project.transition]}
          </p>
          <div className="proj-figures">
            <span className={`tstatus ${project.status}`}>{STATUS_LABEL[project.status]}</span>
            {project.capacity ? (
              <span className="proj-figure">
                {project.capacity.value.toLocaleString("en-US")}{" "}
                <span>{project.capacity.unit}</span>
              </span>
            ) : null}
            {project.investment_total ? (
              <span className="proj-figure">
                {eur(project.investment_total.value)} <span>total investment</span>
              </span>
            ) : null}
          </div>
          {/* THE LEAD BLOCK (§0.2). The strip above is the figures; this is the
              sentence they add up to, plus the four or five facts underneath it
              with the date each was true on. Built and gated in Python by
              sources/build_object_leads.py — the same gate the sector lead
              passes, imported rather than copied — and drawn by the same
              component. Absent only where the build could not answer, which for
              a project means it has no status history at all. */}
          {lead ? <LeadBlock lead={lead} /> : null}
        </header>

        {frame && geo ? (
          <section className="proj-section">
            <LocationMap doc={frame} heading={geo.heading} standfirst={geo.standfirst} />
          </section>
        ) : null}

        <section className="proj-section">
          <h2>Status</h2>
          <ol className="proj-rail">
            {rail.map((s) => {
              const on = reached.has(s);
              return (
                <li key={s} className={`${on ? "on" : "off"} ${s}`}>
                  <span className="dot" aria-hidden="true" />
                  <span className="label">{STATUS_LABEL[s]}</span>
                  <span className="date">{dateOf.get(s) ?? ""}</span>
                </li>
              );
            })}
          </ol>
          <ul className="proj-history">
            {project.status_history.map((h) => (
              <li key={`${h.status}-${h.date}`}>
                <span className="date">{h.date}</span>
                <span className={`tstatus ${h.status}`}>{STATUS_LABEL[h.status]}</span>
                {h.note ? <span className="note">{h.note}</span> : null}
                <a href={h.source_url} target="_blank" rel="noreferrer">
                  source
                </a>
              </li>
            ))}
          </ul>
        </section>

        <section className="proj-section">
          <h2>Technology and measures</h2>
          <ul className="proj-tech">
            {project.technology.map((id) => {
              const t = getTechnology(id);
              return (
                <li key={id}>
                  <Link href={`/sectors/${sector}#technology-${id}`}>{t?.name ?? id}</Link>
                  {t ? <span className={`tready ${t.readiness.level}`}>{t.readiness.level}</span> : null}
                  {t ? <span className="note">{t.description}</span> : null}
                </li>
              );
            })}
          </ul>
        </section>

        <section className="proj-section">
          <h2>Funding</h2>
          {/* Derived from data/transition/funding.json, never stored here: the
              same award can finance several projects, so it is a node with an
              edge to each of them rather than a line copied onto each one. */}
          {funding.length === 0 ? (
            <p className="tscore-note">No public capital recorded for this project.</p>
          ) : (
            <ul className="proj-funding">
              {funding.map((f) => {
                const amount = fundingAmount(f, allParams);
                const quote = f.amount ? allParams.get(f.amount)?.source.verbatim : undefined;
                return (
                  <li key={f.id}>
                    <span className="amount">{amount ? eur(amount) : "undisclosed"}</span>
                    <span className="programme">{f.programme}</span>
                    <span className={`tstatus ${f.status}`}>{f.status}</span>
                    {f.under ? (
                      <Link href={measureHref(f.under)} className="measure">
                        {f.under}
                      </Link>
                    ) : null}
                    {f.under_note ? <span className="note">{f.under_note}</span> : null}
                    {f.amount_note ? <span className="note">{f.amount_note}</span> : null}
                    {quote ? <span className="quote">&ldquo;{quote}&rdquo;</span> : null}
                    {f.sources.map((src) => (
                      <a key={src.url} href={src.url} target="_blank" rel="noreferrer">
                        source
                      </a>
                    ))}
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <section className="proj-section">
          <h2>Sources</h2>
          <ul className="proj-sources">
            {project.sources.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {citation(s)}
                </a>
                <span className="note">
                  {s.publisher}
                  {s.date ? ` · ${s.date}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}

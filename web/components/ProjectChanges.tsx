import Link from "next/link";
import { SECTORS } from "@/lib/data";
import {
  STATUS_LABEL,
  byLastChange,
  eur,
  fundingAmount,
  fundingForProject,
  getParameters,
  getProjects,
  lastChange,
  projectHref,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// The home page's feed: what moved, most recent first.
//
// WHY THIS AND NOT THE LEGISLATIVE FEED. Both are real, and only one of them
// is evidence that the law is doing anything. A proposal moving through
// Parliament is an input; a kiln reaching mechanical completion, or a project
// pausing because a national agency declined to co-fund it, is the outcome the
// whole register is a means to. The legislative records still exist at
// /changes; they are no longer the first thing a reader meets.
//
// Every row is one status_history entry with its source link — the same
// append-only data the project page draws as a timeline.

export default function ProjectChanges({ limit = 6 }: { limit?: number }) {
  const params = getParameters();
  const rows = byLastChange(getProjects())
    .map((p) => ({ project: p, event: lastChange(p) }))
    .filter((r) => r.event)
    .slice(0, limit);

  if (rows.length === 0) return <p className="section-note">No project changes recorded yet.</p>;

  return (
    <ol className="pchanges">
      {rows.map(({ project: p, event }) => {
        // Derived, never stored: the project's funding rollup is summed from
        // the funding rows that name it, every time it is shown.
        const funded = fundingForProject(p.id).reduce(
          (a, f) => a + (fundingAmount(f, params) ?? 0),
          0,
        );
        return (
          <li key={p.id} className={`pchange ${event!.status}`}>
            <span className="pchange-date">{event!.date}</span>
            <span className={`tstatus ${event!.status}`}>{STATUS_LABEL[event!.status]}</span>
            <span className="pchange-body">
              <Link href={projectHref(p.id)} className="pchange-name">
                {p.name}
              </Link>
              <span className="pchange-who">
                {p.company} · {p.plant ?? p.country} ·{" "}
                <Link href={`/sectors/${p.sector}`}>{SECTORS[p.sector as SectorSlug]}</Link>
              </span>
              {event!.note ? <span className="pchange-note">{event!.note}</span> : null}
            </span>
            <span className="pchange-figures">
              {p.capacity ? (
                <span>
                  {p.capacity.value.toLocaleString("en-US")} <em>{p.capacity.unit}</em>
                </span>
              ) : null}
              {funded ? (
                <span>
                  {eur(funded)} <em>public funding</em>
                </span>
              ) : null}
            </span>
            <a className="pchange-src" href={event!.source_url} target="_blank" rel="noreferrer">
              source
            </a>
          </li>
        );
      })}
    </ol>
  );
}

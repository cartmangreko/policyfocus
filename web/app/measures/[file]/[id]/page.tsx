import { Fragment } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import BurdenStrip from "@/components/BurdenStrip";
import RuleDiff, { ruleDiffHeading } from "@/components/RuleDiff";
import ValenceTag from "@/components/ValenceTag";
import LeadBlock from "@/components/LeadBlock";
import { DEMOTED, SITE_ROBOTS } from "@/lib/launch";
import { getMeasureLead } from "@/lib/objectLeads";
import {
  CLASS_LABELS,
  FILES,
  SECTORS,
  getAllMeasures,
  getMeasure,
  getRelatedMeasures,
  measureHref,
} from "@/lib/data";
import { measureJsonLd } from "@/lib/schema";
import { headlineStep, isStated } from "@/lib/text";
import { isPositiveValence, valenceLabel } from "@/lib/valence";
import type { Measure } from "@/lib/types";

// Every path this route serves is enumerated below, so an unlisted one is a
// 404 rather than a render on demand. That is load-bearing on Vercel: the
// register JSON lives outside web/ and is read at build time only, so a
// function rendering an unknown slug would have nothing to read. See
// README.md, "Deploying".
export const dynamicParams = false;

export function generateStaticParams() {
  return getAllMeasures().map((m) => ({ file: m.file, id: m.id.toLowerCase() }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ file: string; id: string }>;
}): Promise<Metadata> {
  const { file, id } = await params;
  const measure = getMeasure(file, id);
  if (!measure) return { title: "Measure not found" };
  const title = measure.duty ?? measure.benefit ?? measure.id;
  return {
    title: `${measure.id} — ${title}`,
    description: measure.affected_delta ?? measure.trigger,
    // INDEXABLE ONCE IT RENDERS A LEAD BLOCK, and not before — §0.8, and the
    // exit the index opening left open for this route class. The condition is
    // the lead itself rather than a date or a list of ids: a measure whose lead
    // could not be built (its act carries no date on which anything about it
    // was true) stays demoted, and arrives in the index on the day the build
    // can answer for it. lib/siteRoutes.ts reads the same store to decide
    // whether to publish the URL, so the tag and the sitemap cannot disagree.
    // SITE_ROBOTS, not undefined: page metadata replaces the layout's rather
    // than merging with it, so `undefined` would clear the site-wide tag rather
    // than inherit it. See the same note on the sector route.
    robots: getMeasureLead(file, id) ? SITE_ROBOTS : DEMOTED,
  };
}

const NATURE_LABELS: Record<string, string> = {
  exemption: "Exemption",
  new_obligation: "New obligation",
  reduction: "Reduction",
  extension: "Extension",
};

function sectorList(measure: Measure): string {
  const named = measure.sectors_named ?? [];
  const reached = measure.sectors_reached ?? [];
  if (!named.length && !reached.length) return "No sector named — applies by size or activity";
  const parts: string[] = [];
  if (named.length) parts.push(`Names ${named.map((s) => SECTORS[s]).join(", ")}`);
  if (reached.length) parts.push(`Reaches ${reached.map((s) => SECTORS[s]).join(", ")}`);
  return parts.join(" · ");
}

export default async function MeasurePage({
  params,
}: {
  params: Promise<{ file: string; id: string }>;
}) {
  const { file, id } = await params;
  const measure = getMeasure(file, id);
  if (!measure) notFound();

  const lead = getMeasureLead(file, id);
  const fileMeta = FILES[measure.file];
  const positive = isPositiveValence(measure.measure_type, measure.direction);
  const related = getRelatedMeasures(measure);
  const drivers = measure.drivers ?? [];

  // The headline is the provision's own statement: the duty for an obligation
  // row, the benefit for an incentive one. It sets the display step, since a
  // statement is often a paragraph rather than a title — see headlineStep.
  const statement = measure.duty ?? measure.benefit ?? "";

  // Fields stored as "n/a" are omitted rather than printed — a row that says
  // "Frequency: n/a" tells the reader nothing the missing row doesn't.
  const keyFacts: [string, string][] = [
    ["Nature", measure.nature ? NATURE_LABELS[measure.nature] ?? measure.nature : ""],
    ["Direction", measure.direction === "add" ? "Added" : "Removed"],
    ["Frequency", measure.frequency],
    ["Verification", measure.verification],
    ["Drivers", drivers.length ? drivers.join(", ") : "None recorded"],
  ].filter((pair): pair is [string, string] => isStated(pair[1]));

  return (
    <main className="rise">
      {/* schema.org Legislation markup for this provision, nested in the act
          it was read from — see lib/schema.ts for the documented choice. */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: measureJsonLd(measure) }}
      />
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/#doors" className="backlink">
              ← All measures
            </Link>
            <span className="crumb">
              Measures / {fileMeta ? fileMeta.name.split(" — ")[0] : measure.file}
            </span>
          </div>
          <ValenceTag
            measureType={measure.measure_type}
            direction={measure.direction}
            suffix={measure.id}
          />
          <h1 className={`detail-title${headlineStep(statement)}`}>{statement}</h1>
          {/* THE LEAD BLOCK (§0.2), and what it deliberately does not repeat.
              The heading above is the decoded provision — this page's whole
              subject — so the lead says the five things the provision itself
              does not: who it lands on, whether it is law yet, when it bites,
              which industries it names, and what it costs wherever somebody has
              priced it. Built and gated in Python; this draws it. */}
          {lead ? <LeadBlock lead={lead} /> : null}
          <div className="detail-meta">
            <span>
              <span className="detail-meta-label">Addressee</span> {measure.addressee}
            </span>
            <span>
              <span className="detail-meta-label">Act</span>{" "}
              {fileMeta ? fileMeta.code : measure.file}
            </span>
            <span>
              <span className="detail-meta-label">Article</span> {measure.article}
            </span>
            <span>
              <span className="detail-meta-label">Class</span> {CLASS_LABELS[measure.class]}
            </span>
          </div>
        </div>
      </section>

      <section className="detail-body">
        <div className="wrap detail-grid">
          <div>
            {measure.affected_delta && (
              <>
                <h2 className="rule-head">What changes</h2>
                <p className="prose">{measure.affected_delta}</p>
              </>
            )}

            <h2 className="rule-head">{ruleDiffHeading(measure)}</h2>
            <RuleDiff measure={measure} />

            <h2 className="rule-head">Who is affected</h2>
            <div className="factgrid">
              <div>
                <div className="fact-label">Addressee</div>
                <div className="fact-value">{measure.addressee}</div>
              </div>
              <div>
                <div className="fact-label">Class</div>
                <div className="fact-value">{CLASS_LABELS[measure.class]}</div>
              </div>
              <div>
                <div className="fact-label">Sectors</div>
                <div className="fact-value">{sectorList(measure)}</div>
              </div>
              <div>
                <div className="fact-label">Applies</div>
                <div className="fact-value">{measure.when}</div>
              </div>
            </div>

            <h2 className="rule-head">Burden drivers</h2>
            <div className="drivers-block">
              <BurdenStrip drivers={measure.drivers} positive={positive} />
              <span className="drivers-text">
                {drivers.length
                  ? `${drivers.join(" · ")} — ${drivers.length} of 7 marks fire on this provision.`
                  : "No burden drivers recorded on this provision."}
              </span>
            </div>

            {measure.size_scope_note && <p className="prose prose-sm">{measure.size_scope_note}</p>}

            <h2 className="rule-head">Source text</h2>
            <div className="source">
              <div className="source-label">Verbatim</div>
              <p className="source-quote">{measure.source_text}</p>
              <a href={measure.source_url} target="_blank" rel="noopener" className="source-link">
                View source →
              </a>
            </div>

            {measure.pending && (
              <p className="pending">Settled later in secondary legislation. {measure.pending}</p>
            )}
          </div>

          <aside className="rail">
            <div className="rail-head">
              <div className="rail-head-label">Weight</div>
              <div className={`rail-head-value ${positive ? "is-pos" : "is-neg"}`}>
                {valenceLabel(measure.measure_type, measure.direction)}
              </div>
            </div>
            <div className="rail-body">
              <div className="rail-label">Key facts</div>
              <dl className="keyfacts">
                {keyFacts.map(([term, value]) => (
                  <Fragment key={term}>
                    <dt>{term}</dt>
                    <dd>{value}</dd>
                  </Fragment>
                ))}
              </dl>

              {/* The citation affordance. Ids are permanent policy — stated
                  on /coverage and in sources/scope.md — so the path is the
                  durable half of the citation; the site's domain prefixes it
                  at launch. Everything here is composed from row fields. */}
              <div className="rail-label rail-label-divided">Cite this measure</div>
              <div className="cite-block">
                <code className="cite-url">{measureHref(measure)}</code>
                <p className="cite-string">
                  {measure.id}, {fileMeta ? fileMeta.name.split(" — ")[0] : measure.file} (
                  {fileMeta ? fileMeta.code : measure.file}), {measure.article} — Eufabric,
                  permanent id.
                </p>
              </div>

              {related.length > 0 && (
                <>
                  <div className="rail-label rail-label-divided">Related measures</div>
                  <div className="rail-related">
                    {related.map((r) => (
                      <Link key={`${r.file}-${r.id}`} href={measureHref(r)}>
                        <span className="rail-related-id">{r.id} · </span>
                        {r.duty ?? r.benefit}
                      </Link>
                    ))}
                  </div>
                </>
              )}
            </div>
          </aside>
        </div>
      </section>
    </main>
  );
}

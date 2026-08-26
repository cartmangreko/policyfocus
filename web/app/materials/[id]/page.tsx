import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Crumbs from "@/components/Crumbs";
import { citation } from "@/lib/citation";
import { SECTORS } from "@/lib/data";
import { DEMOTED } from "@/lib/launch";
import {
  allMaterials,
  getMaterial,
  getParameters,
  getProject,
  getTechnology,
  projectHref,
  type Material,
  type MaterialEdge,
} from "@/lib/transition";
import type { SectorSlug } from "@/lib/types";

// One material, and every edge that touches it. The spoke the Materials
// section on a sector page points at — brief 5 §6, which is also why there is
// no per-sector materials list page: a material is cross-sector by nature.
// Clinker leaves cement; captured CO2 leaves cement and arrives at a storage
// route; slag will leave steel and arrive in cement. A list of "cement's
// materials" would be a slice of this page repeated once per sector.
//
// DEMOTED, and it says why in one place rather than two: §0.8 makes
// indexability follow the lead block, this page renders none yet, so it carries
// `noindex, follow` and the crawler walks through it to the projects and
// sectors it links. It arrives in the index by being given a lead block, which
// is a build gap on the ROADMAP and not a decision anybody re-opens here.

export const dynamicParams = false;

export function generateStaticParams() {
  return allMaterials().map((m) => ({ id: m.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const m = getMaterial((await params).id);
  if (!m) return { title: "Material not found" };
  return {
    robots: DEMOTED,
    title: `${m.name} — ${m.type.replace("_", " ")}`,
    description: m.description,
  };
}

/** An edge endpoint in the reader's words, linked where the endpoint has a page
 *  of its own. A technology does not, yet: it is a section on the sector page,
 *  so the label stands as text rather than pointing at an anchor that a
 *  different sector's page may not carry. */
function Endpoint({ node }: { node: string }) {
  const [kind, id] = node.split(":");
  if (kind === "sector") {
    const name = SECTORS[id as SectorSlug];
    return name ? <Link href={`/sectors/${id}`}>{name}</Link> : <>{id}</>;
  }
  if (kind === "project") {
    const p = getProject(id);
    return p ? <Link href={projectHref(p.id)}>{p.name}</Link> : <>{id}</>;
  }
  if (kind === "technology") return <>{getTechnology(id)?.name ?? id}</>;
  return <>{id}</>;
}

/** `id` is what a sector page's basis count links to — "5 plants" opens the
 *  five, each with the edge evidence that put it there. §0.1: a computed figure
 *  links to the set of records behind it. */
function Edges({ id, title, edges }: { id: string; title: string; edges: MaterialEdge[] }) {
  if (edges.length === 0) return null;
  const params = getParameters();
  return (
    <div className="mat-edges" id={id}>
      <h3>{title}</h3>
      <ul>
        {edges.map((e) => {
          const volume = e.volume ? params.get(e.volume) : null;
          return (
            <li key={`${e.node}-${e.since}`}>
              <Endpoint node={e.node} />
              <span className="mat-since">since {e.since}</span>
              {volume ? (
                <span className="mat-volume">
                  {volume.value} {volume.unit}{" "}
                  <a href={volume.source.url} target="_blank" rel="noreferrer">
                    {volume.source.publisher}
                  </a>
                </span>
              ) : e.volume_note ? (
                <span className="mat-volume-gap">{e.volume_note}</span>
              ) : null}
              {/* The quote is the edge. An edge whose evidence is a filename
                  and nothing else still says which file, which is the least a
                  reader needs to go and check it. */}
              <span className="mat-evidence">
                {e.evidence.quote ? `“${e.evidence.quote}” — ` : ""}
                {e.evidence.source}
                {e.evidence.note ? ` · ${e.evidence.note}` : ""}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default async function MaterialPage({ params }: { params: Promise<{ id: string }> }) {
  const material: Material | undefined = getMaterial((await params).id);
  if (!material) notFound();

  return (
    <main className="rise">
      <div className="wrap">
        <Crumbs trail={[{ label: "Sectors", href: "/sectors" }, { label: material.name }]} />

        <header className="mat-head">
          <h1>{material.name}</h1>
          <p className="mat-kind">
            <span className={`tmat-type ${material.type}`}>{material.type.replace("_", " ")}</span>
            {material.cn_code ? <span className="mono">CN {material.cn_code}</span> : null}
            {material.prodcom_code ? (
              <span className="mono">PRODCOM {material.prodcom_code}</span>
            ) : null}
            {material.crma_annex_i ? (
              <a
                className="mat-crma"
                href={material.crma_annex_i.source.url}
                target="_blank"
                rel="noreferrer"
              >
                CRMA Annex I — {material.crma_annex_i.entry}
              </a>
            ) : null}
          </p>
          <p className="mat-description">{material.description}</p>
          <p className="mat-sectors">
            Read in{" "}
            {material.sectors.map((s, i) => (
              <span key={s}>
                {i > 0 ? ", " : ""}
                <Link href={`/sectors/${s}`}>{SECTORS[s as SectorSlug] ?? s}</Link>
              </span>
            ))}
            .
          </p>
        </header>

        <Edges id="produced-by" title="Produced by" edges={material.produced_by} />
        <Edges id="consumed-by" title="Consumed by" edges={material.consumed_by} />
        <Edges id="required-by" title="Required by" edges={material.required_by} />

        {material.substitutes.length > 0 ? (
          <div className="mat-edges" id="substitutes">
            <h3>Substitutes for</h3>
            <ul>
              {material.substitutes.map((s) => (
                <li key={s.material}>
                  <Link href={`/materials/${s.material}`}>
                    {getMaterial(s.material)?.name ?? s.material}
                  </Link>
                  <span className="mat-since">since {s.since}</span>
                  <span className="mat-evidence">
                    {s.evidence.quote ? `“${s.evidence.quote}” — ` : ""}
                    {s.evidence.source}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="mat-edges">
          <h3>Sources</h3>
          <ul>
            {material.sources.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {citation(s)}
                </a>
                <span className="mat-since">{s.publisher}</span>
                {s.date ? <span className="mat-since">{`· ${s.date}`}</span> : null}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </main>
  );
}

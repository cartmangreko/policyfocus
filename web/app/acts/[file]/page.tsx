import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Crumbs from "@/components/Crumbs";
import SignalRow from "@/components/SignalRow";
import SummaryStrip from "@/components/SummaryStrip";
import { getActMeasuresBySector, getActReach } from "@/lib/acts";
import { FILES, SECTORS } from "@/lib/data";
import { getActSummary } from "@/lib/summaries";

// One act, in the same grammar as a sector page: summary strip, then the
// reach strip (which sectors the file names, which it reaches and through
// what), then the measures grouped by sector. The article-order audit view —
// every row in register order — lives on /measures and is linked, not
// duplicated: it answers "what exactly does this file say, row by row",
// which is a different question from this page's "who does it land on".

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.keys(FILES).map((file) => ({ file }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ file: string }>;
}): Promise<Metadata> {
  const { file } = await params;
  const meta = FILES[file];
  if (!meta) return { title: "File not found" };
  const reach = getActReach(file);
  return {
    title: meta.name,
    description: `${meta.code} — names ${reach.named.length} sectors, reaches ${reach.totalReach}, read provision by provision.`,
  };
}

export default async function ActPage({ params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  const meta = FILES[file];
  if (!meta) notFound();

  const summary = getActSummary(file);
  const reach = getActReach(file);
  const groups = getActMeasuresBySector(file);

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <Crumbs
            trail={[
              { label: "Home", href: "/" },
              { label: "Legislation", href: "/acts" },
              { label: meta.name.split(" — ")[0] },
            ]}
          />
          <h1 className="sector-title">{meta.name}</h1>
          <p className="sector-intro">{meta.code}</p>
          <SummaryStrip cuts={summary} />
        </div>
      </section>

      <section className="band band-tight" id="reach">
        <div className="wrap">
          <p className="eyebrow">Reach</p>
          <h2>
            Names {reach.named.length} {reach.named.length === 1 ? "sector" : "sectors"}, reaches{" "}
            {reach.totalReach}
          </h2>
          <div className="chips">
            {reach.named.map((s) => (
              <Link key={s} href={`/sectors/${s}`} className="chip">
                {SECTORS[s]}
              </Link>
            ))}
          </div>
          {reach.reachedOnly.length > 0 && (
            <div className="reach-list">
              {/* The sectors this file covers without naming once — each
                  tagged with how it arrives, and with the act that
                  intermediates the reach where the graph evidences one. */}
              {reach.reachedOnly.map((r) => (
                <p key={r.slug} className="reach-row">
                  <Link href={`/sectors/${r.slug}`} className="reach-row-name">
                    {r.name}
                  </Link>{" "}
                  — reached by {r.rows.length} {r.rows.length === 1 ? "row" : "rows"}, via{" "}
                  {r.channels.join(" and ").toLowerCase()}
                  {r.intermediatingActs.length > 0 && (
                    <> · through {r.intermediatingActs.join(", ")}</>
                  )}
                </p>
              ))}
            </div>
          )}
        </div>
      </section>

      {groups.map((g) => (
        <section className="band band-ruled" id={g.slug ?? "no-sector"} key={g.slug ?? "none"}>
          <div className="wrap">
            <div className="section-head">
              <div>
                <p className="eyebrow">
                  {g.rows.length} {g.rows.length === 1 ? "measure" : "measures"}
                </p>
                <h2>
                  {g.slug ? <Link href={`/sectors/${g.slug}`}>{g.name}</Link> : g.name}
                </h2>
              </div>
            </div>
            <div className="signals">
              {g.rows.map((m, i) => (
                <SignalRow key={`${m.file}-${m.id}`} measure={m} last={i === g.rows.length - 1} />
              ))}
            </div>
          </div>
        </section>
      ))}

      <section className="band band-paper">
        <div className="wrap">
          <p className="eyebrow">Audit view</p>
          <p className="section-note section-note-wide">
            A row naming several sectors is filed above under the first sector its named list
            carries; the full list is on each measure page. To read the file in register order
            instead — every row, article by article —{" "}
            <Link href={`/measures#${file}`} className="section-link">
              open the audit view →
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

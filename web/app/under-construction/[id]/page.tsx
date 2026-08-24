import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import SectorIcon, { accentVar } from "@/components/SectorIcon";
import { getEcosystems, isUnderConstruction } from "@/lib/ecosystems";
import { DEMOTED } from "@/lib/launch";

// WHERE A TILE GOES WHEN ITS INDUSTRY IS NOT BUILT YET.
//
// It used to go to /coverage, which is a page about the platform — how an act
// becomes measures, which acts have been read twice, what is queued. A reader
// who clicked Hydrogen asked about hydrogen and was handed the methodology.
//
// This says the one true thing instead, and stops. No date, because we do not
// have one and a date nobody can keep is worse than silence. No progress
// claim — no "coming soon", no percentage, no list of what is nearly ready —
// because a holding page that boasts is a holding page nobody believes the
// second time.
//
// ONE TEMPLATE, FIVE ADDRESSES. The route is one file and one layout; the
// segment is what lets the page name the industry the reader asked about,
// which is the only thing on it that changes. A single address with the
// industry in a query string would have to render at request time, and the
// data it needs — data/transition/ecosystems.json — lives outside web/ and is
// read at build time, which is the same constraint that makes the sector route
// enumerate its params. See README, "Deploying".
//
// THE WORDMARK IS THE HEADER'S. Brief 4 §3 left exactly one on the site and
// this page is inside the same chrome as every other; a second lockup in the
// body would be the duplication that brief removed, on the one page with least
// reason to carry it.

export const dynamicParams = false;

export function generateStaticParams() {
  return getEcosystems()
    .filter(isUnderConstruction)
    .map((e) => ({ id: e.id }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const eco = getEcosystems().find((e) => e.id === id);
  if (!eco) return { title: "Not found" };
  return {
    title: eco.name,
    description: `${eco.name} is being built on Eufabric.`,
    // Demoted, and it will stay demoted: a page whose content is one sentence
    // saying there is no content is the clearest case there is of a page that
    // should not be offered to a stranger as an answer. It keeps `follow`, so
    // the link home is walked.
    robots: DEMOTED,
  };
}

export default async function UnderConstruction({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const eco = getEcosystems().find((e) => e.id === id);
  if (!eco || !isUnderConstruction(eco)) notFound();

  return (
    <main className="rise building" style={{ ["--accent" as string]: `var(${accentVar(eco.icon)})` }}>
      <div className="wrap">
        <div className="building-inner">
          <SectorIcon slug={eco.icon} size={44} />
          <h1>{eco.name}</h1>
          <p className="building-line">This sector is being built.</p>
          <Link href="/" className="section-link">
            &larr; Back to the front page
          </Link>
        </div>
      </div>
    </main>
  );
}

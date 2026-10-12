import type { Metadata } from "next";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import EcosystemTiles from "@/components/EcosystemTiles";
import { getProjects, hasMap, isDrawable } from "@/lib/transition";
import { sectorNames } from "@/lib/sectorSections";

// The six, and nothing else (brief 4 §4).
//
// WHAT THIS REPLACED. A directory of twenty parent sectors, each a card with a
// miniature burden/relief strip, children nested under it, and the whole
// corpus summarised at the top. Every figure on it was correct and every one
// of them was the old product: a reader arriving here wanted to know which
// industries this platform covers, and was given a measure inventory instead.
//
// The rest of the spine has not gone anywhere. Every sector the corpus reaches
// still has its page, still renders its own directory template, and is reached
// from the coverage page — which is the page whose job is to say what is on
// the platform and what is not. This one says what the platform is FOR.
//
// It draws the same component as the front page, deliberately: two lists of
// six maintained in two places is two lists of six that will disagree.
export const metadata: Metadata = {
  title: "Sectors",
  description:
    "The six industries Eufabric covers: cement, steel, chemicals, batteries, hydrogen and circular materials.",
};

export default function SectorsPage() {
  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <Crumbs trail={[{ label: "Home", href: "/" }, { label: "Sectors" }]} />
          <h1 className="sector-title">Sectors</h1>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          <EcosystemTiles />
          {/* The sentence stays and its link does not: what this page covers
              is worth saying here, and the page that qualifies it is no longer
              linked from anywhere on the site. */}
          <p className="section-note">
            Eufabric covers Europe&rsquo;s energy-intensive industries and the materials they
            make.
          </p>
        </div>
      </section>

      {/* THE SHARED LAYER, BELOW THE SIX AND NOT ONE OF THEM. Brief 17 §B.3.
          eufabric-page-specifications.md §4.2 settles that carbon capture is
          not an ecosystem — it is an abatement route several industries take —
          so it gets no tile, and a seventh tile would be the perimeter argument
          being lost by addition. What it does get is a dataset of its own and
          a hub that draws it, and until now there was no way to reach that hub
          from anywhere a reader would look.

          THE ENTRY IS A LINK AND NOT A TILE, which is the distinction doing the
          work: a tile is one of the industries this platform is for, and this
          is something they all depend on. It is reached from here and from the
          dependency row on the cement and steel hubs, which is where a reader
          meets the question it answers. */}
      {hasMap("ccs") ? <SharedLayer /> : null}
    </main>
  );
}

/** CO2 transport and storage, named below the tiles.
 *
 *  THE TWO NUMBERS ARE COMPUTED, and they are the two a reader needs before
 *  deciding whether to follow the link: how much is tracked, and how much of it
 *  has been placed on the ground. The second is much the smaller, which is why
 *  it is said here rather than left to be discovered — the hub is withheld from
 *  search for exactly that reason (data/transition/draw_holds.json), and a page
 *  that linked to it without saying so would be routing readers at a picture
 *  somebody has judged incomplete. */
function SharedLayer() {
  const rows = getProjects("ccs");
  const drawn = rows.filter(isDrawable).length;
  const names = sectorNames("ccs");
  return (
    <section className="band band-ruled">
      <div className="wrap">
        <p className="eyebrow">Not an industry</p>
        <h2>What several of them depend on</h2>
        <p className="section-note">
          {`${names.short} is an abatement route rather than an industry, so it is not one ` +
            `of the six above. It is tracked as a layer of its own: ${rows.length} ` +
            `projects, ${drawn} of them placed on the ground.`}
        </p>
        <p>
          <Link href="/sectors/ccs" className="section-link">
            {`Where Europe is building ${names.short} →`}
          </Link>
        </p>
      </div>
    </section>
  );
}

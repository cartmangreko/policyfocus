import type { Metadata } from "next";
import Link from "next/link";
import EcosystemTiles from "@/components/EcosystemTiles";
import ProjectChanges from "@/components/ProjectChanges";
import { getCoverageLine, getMasthead } from "@/lib/sitetext";

// The front page, cut back to what it can stand behind (brief 4 §3): the name,
// what the platform is, the six industries it covers, what moved, and one line
// saying where the material comes from.
//
// WHAT LEFT, AND WHY EACH ONE LEFT
// --------------------------------
// The wordmark. It was here AND in the header, which on a phone drew the logo
// twice on the first screen. One instance survives, in the header, set larger
// — see components/SiteHeader.tsx.
//
// The twenty-sector grid. Eufabric launches narrow (brief 4 §1), and a grid of
// twenty tiles with one live sector in it advertises the nineteen that are
// not. The six tiles are the perimeter; every other sector the corpus reaches
// is reachable from the coverage page, which is where a claim about what is
// covered belongs.
//
// The sector count sentence ("1 of 20 sectors is live"). Same reason. It was a
// computed sentence about our own build progress standing where a statement
// about the industries should be.
//
// Sign in, and the search field. See components/SiteHeader.tsx.
//
// WHAT STAYED. The project feed. Both feeds on this platform are real, and only
// one of them is evidence that any of this law is doing something: a kiln
// reaching mechanical completion, or a project pausing because a national
// agency declined to co-fund it. The legislative change records keep their
// pages at /changes, unlinked from here.
//
// The descriptor and the positioning sentence are George-approved final text,
// read from data/prose.json — reviewed prose stored as data, per
// sources/scope.md. Nothing on this page composes a sentence of its own.

export function generateMetadata(): Metadata {
  const masthead = getMasthead();
  // The two reviewed lines, in the order they render on the page. It used to
  // be a computed inventory — measures, acts, sectors reached — which is the
  // old product describing itself, and which now disagrees with the page it
  // tags.
  return { description: `${masthead.descriptor} ${masthead.positioning}` };
}

// Enough to read as a feed rather than as a teaser, and few enough that the
// page stays one screen of tiles and one of movement.
const FEED_ON_HOME = 6;

export default function Home() {
  const masthead = getMasthead();

  return (
    <main className="rise">
      <section className="home-head home-head-slim">
        <div className="wrap">
          <p className="home-tagline">{masthead.descriptor}</p>
          <p className="home-subline">{masthead.positioning}</p>
        </div>
      </section>

      <section className="band band-paper" id="sectors">
        <div className="wrap">
          <EcosystemTiles />
        </div>
      </section>

      <section className="band" id="latest">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Latest</p>
              <h2>What moved</h2>
            </div>
          </div>
          <ProjectChanges limit={FEED_ON_HOME} />
        </div>
      </section>

      {/* The one line about the material, and the one link out of this page.
          The sentence is reviewed prose with its act count computed, so it
          moves when the coverage does. */}
      <section className="band band-tight" id="sources">
        <div className="wrap">
          <p className="home-sources">
            {getCoverageLine()}{" "}
            <Link href="/coverage" className="section-link">
              What is covered, and what is not &rarr;
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

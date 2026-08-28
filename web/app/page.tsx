import type { Metadata } from "next";
import EcosystemTiles from "@/components/EcosystemTiles";
import { getMasthead } from "@/lib/sitetext";

// The front page, cut back to what it can stand behind (brief 4 §3): the name,
// what the platform is, the six industries it covers, and one line saying where
// the material comes from.
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
// The project feed. It was the one thing on this page that was evidence rather
// than description — a kiln reaching mechanical completion, a project pausing
// because a national agency declined to co-fund it — and it went last, on
// George's call. What it left behind is the reason it went: six industries and
// one feed, on a platform where five of the six have no projects yet, is a feed
// about cement standing under a page that claims six. It belongs here when the
// other five have something to put in it, and until then the movement is on the
// sector page, where a reader knows what it is movement IN. components/
// ProjectChanges.tsx is kept for that, unrendered; the change records keep
// their pages at /changes.
//
// WHAT STAYED is what the page can stand behind on the day it ships: the name,
// the claim, the perimeter, and where the material comes from.
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

      {/* THE ACTS-DECODED COUNTER IS GONE, and it is not in the footer either.
          It was the last thing on the front page and what it sold was the
          register: a count of acts read is a fact about the pipeline, and this
          page is about the industries. /coverage still exists and is still
          indexable — it is simply linked from nowhere on the site now, which is
          a decision rather than an oversight. See components/SiteFooter.tsx. */}
    </main>
  );
}

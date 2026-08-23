import type { Metadata } from "next";
import Link from "next/link";
import ProjectChanges from "@/components/ProjectChanges";
import SectorGrid from "@/components/SectorGrid";
import Wordmark from "@/components/Wordmark";
import { getSiteSummary } from "@/lib/summaries";
import { getSectorCounts } from "@/lib/data";
import { getMasthead } from "@/lib/sitetext";
import { hasMap } from "@/lib/transition";

// The home page is a front page, not a masthead. Three blocks: the slim head,
// what moved at a plant, and the sectors.
//
// THE SECOND INVERSION. The feed used to be the legislative record — an act
// proposed, an act amended. Both feeds are real, and only one of them is
// evidence that any of this law is doing something: a kiln reaching mechanical
// completion, or a project pausing because a national agency declined to
// co-fund it. So the project feed leads and the legislative records keep their
// pages at /changes, unlinked from here.
//
// What went with it: the three-figure stats strip, the findings band, the
// legislation chips and the coverage line. They were the register presenting
// itself as the product. The register is now the candidate pool behind the
// sector pages, and its surfaces are reachable rather than advertised.
//
// THE INVERSION, AND WHAT IT COST. The head used to be the page: wordmark,
// tagline, and three big figures above the fold, with the conclusions below
// them. It read as an identity rather than as something that had happened
// recently. So the head compresses — the masthead pair and the same three
// figures, now one slim strip — and the feed takes the lead. What was the
// "Recently added" band is gone rather than demoted: it said which act was
// added last, which is exactly what the first record in the feed says, at
// greater length and with a page behind it. Its one fact that the feed does
// not carry, the date the document was fetched, moved into the strip.
//
// The masthead pair (tagline + subline) is George-approved final text, read
// from data/prose.json — reviewed prose stored as data, per sources/scope.md.

// The default title stays in the layout; the description is computed from
// the site summary so the tag moves with the register.
export function generateMetadata(): Metadata {
  const site = getSiteSummary();
  return {
    description: `${site.measures} measures decoded from ${site.files} EU acts, mapped to the ${site.sectors.total_reach} sectors they affect — every count computed from the source legislation.`,
  };
}

// Enough to read as a feed rather than as a teaser, and few enough that the
// sectors stay above the fold on a laptop.
const FEED_ON_HOME = 6;

export default function Home() {
  const masthead = getMasthead();
  // Computed, not written: how many sectors have a map and what the rest show
  // instead. The sentence changes on the day steel lands, with nobody editing
  // a page.
  const counts = getSectorCounts();
  const mapped = counts.filter((s) => hasMap(s.slug)).length;
  const sectorLine =
    `${mapped} of ${counts.length} sectors has a transition map; the rest carry the ` +
    `number of tracked measures reaching them until they do.`;

  return (
    <main className="rise">
      <section className="home-head home-head-slim">
        <div className="wrap">
          <div className="home-wordmark">
            <Wordmark />
          </div>
          <p className="home-tagline">{masthead.tagline}</p>
          <p className="home-subline">{masthead.subline}</p>
        </div>
      </section>

      <section className="band" id="latest">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Latest</p>
              <h2>What moved at a plant</h2>
            </div>
          </div>
          <ProjectChanges limit={FEED_ON_HOME} />
        </div>
      </section>

      <section className="band band-paper" id="sectors">
        <div className="wrap">
          <div className="section-head">
            <div>
              <p className="eyebrow">Sectors</p>
              <h2>What each sector is under</h2>
              <p className="section-note">{sectorLine}</p>
            </div>
            <Link href="/sectors" className="section-link">
              All sectors &rarr;
            </Link>
          </div>
          <SectorGrid />
        </div>
      </section>
    </main>
  );
}

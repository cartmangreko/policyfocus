import type { Metadata } from "next";
import Link from "next/link";
import Crumbs from "@/components/Crumbs";
import EcosystemTiles from "@/components/EcosystemTiles";

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
          <p className="section-note">
            Eufabric covers Europe&rsquo;s energy-intensive industries and the materials they
            make.{" "}
            <Link href="/coverage" className="section-link">
              What is covered, and what is not &rarr;
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}

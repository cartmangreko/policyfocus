import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import RecordCard from "@/components/RecordCard";
import RecordFeed from "@/components/RecordFeed";
import { getRecords } from "@/lib/records";
import { signalIds } from "@/lib/opportunity";
import { getSectorSlugs } from "@/lib/data";
import { hasMap } from "@/lib/transition";
import { DEMOTED } from "@/lib/launch";

// The full record feed, reverse chronological. The home page leads with the
// same records; this is where they all live, and where the feed keeps going
// once the home page has shown the most recent few.
export function generateMetadata(): Metadata {
  const records = getRecords();
  return {
    robots: DEMOTED,
    title: "Latest",
    description:
      `${records.length} change ${records.length === 1 ? "record" : "records"} — one per legislative event, ` +
      "stating what changed, in which act, and which sectors it names, every count computed from the act itself.",
  };
}

export default function ChangesIndexPage() {
  const records = getRecords();
  // §4.6, site-wide: the list is not one sector's page, so its filter cannot
  // ask one sector's question. Computed at build time; the client component
  // only hides what it is told to hide.
  const signals = signalIds(getSectorSlugs().filter((s) => hasMap(s)));

  return (
    <main className="rise">
      <section className="detail-head">
        <div className="wrap">
          <div className="crumbs">
            <Link href="/" className="backlink">
              ← Home
            </Link>
            <span className="crumb">Latest</span>
          </div>
          <h1 className="sector-title">Latest</h1>
          <p className="sector-intro">
            One record per legislative event: what changed, in which act, and which sectors the
            act names. A record is written when the change enters the platform and is not revised
            afterwards, so it stays a record of what happened rather than of what is current.
            Every count on it is computed from the act itself.
          </p>
        </div>
      </section>

      <section className="band">
        <div className="wrap">
          {records.length === 0 ? (
            <p className="section-note">No records published yet.</p>
          ) : (
            // Suspense because the filter reads the query string, and a
            // statically rendered page has no query string until the browser
            // has one. The fallback is the unfiltered feed, which is what this
            // page was before the filter and what a crawler gets.
            <Suspense
              fallback={
                <div className="record-feed">
                  {records.map((r) => (
                    <RecordCard key={r.id} record={r} />
                  ))}
                </div>
              }
            >
              <RecordFeed
                cards={records.map((r) => ({
                  id: r.id,
                  card: <RecordCard key={r.id} record={r} />,
                }))}
                signalIds={signals}
              />
            </Suspense>
          )}
        </div>
      </section>
    </main>
  );
}

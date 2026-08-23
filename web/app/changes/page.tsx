import type { Metadata } from "next";
import Link from "next/link";
import RecordCard from "@/components/RecordCard";
import { getRecords } from "@/lib/records";
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
            <div className="record-feed">
              {records.map((r) => (
                <RecordCard key={r.id} record={r} />
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

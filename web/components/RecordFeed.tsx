"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import type { ReactNode } from "react";

// THE CHANGE-RECORD LIST, WITH §4.6'S FILTER ON IT.
//
// `?opportunity=1` narrows the list to the records whose object is a funding
// node, a support-direction measure or a measure that creates demand. The chip
// on a sector page's Feed section opens this route with that parameter.
//
// FILTERED IN THE BROWSER, ON PURPOSE. Reading the parameter on the server
// would make this page render per request, and the register JSON lives outside
// web/ and is read at build time only — a request-rendered page would have
// nothing to read (see README, "Deploying"). So the page is built once with
// every record in it, each card carrying whether it is a signal, and this hides
// what the filter excludes. Every record is in the HTML either way, which is
// also the right answer for a crawler: the filter is a convenience, not a
// separate document.

export default function RecordFeed({
  cards,
  signalIds,
}: {
  cards: { id: string; card: ReactNode }[];
  /** Which records are opportunity signals, decided at build time by
   *  lib/opportunity.ts. This component holds no opinion about what one is. */
  signalIds: string[];
}) {
  const params = useSearchParams();
  const filtered = params.get("opportunity") === "1";
  const signals = new Set(signalIds);
  const shown = filtered ? cards.filter((c) => signals.has(c.id)) : cards;

  return (
    <>
      {signalIds.length > 0 ? (
        <p className="record-filter">
          <Link href="/changes" className={`chip${filtered ? "" : " is-here"}`}>
            All
            <span className="chip-count">{cards.length}</span>
          </Link>
          <Link href="/changes?opportunity=1" className={`chip${filtered ? " is-here" : ""}`}>
            Opportunity signals
            <span className="chip-count">{signalIds.length}</span>
          </Link>
        </p>
      ) : null}
      {shown.length === 0 ? (
        <p className="section-note">
          Nothing on the platform is an opportunity signal yet.{" "}
          <Link href="/changes">Show all</Link>.
        </p>
      ) : (
        <div className="record-feed">{shown.map((c) => c.card)}</div>
      )}
    </>
  );
}

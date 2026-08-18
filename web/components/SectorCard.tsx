import Link from "next/link";
import SummaryStrip from "./SummaryStrip";
import { SECTORS, getChildren } from "@/lib/data";
import { getSectorSummary } from "@/lib/summaries";
import type { SectorSlug } from "@/lib/types";

// One sector as a directory sub-card: the name, its gate-checked summary in
// miniature, and — where the sector has children — each child nested with a
// miniature strip of its own. Used by the /sectors directory and by parent
// pages listing their children; the numbers come from the summary objects,
// never from a recount here.
export default function SectorCard({ slug }: { slug: SectorSlug }) {
  const children = getChildren(slug);
  return (
    <div className="dir-card">
      <Link href={`/sectors/${slug}`} className="dir-card-title">
        {SECTORS[slug]}
      </Link>
      <SummaryStrip cuts={getSectorSummary(slug)} variant="mini" />
      {children.length > 0 && (
        <div className="dir-card-children">
          {children.map((child) => (
            <div key={child} className="dir-card-child">
              <Link href={`/sectors/${child}`} className="dir-card-child-title">
                {SECTORS[child]}
              </Link>
              <SummaryStrip cuts={getSectorSummary(child)} variant="mini" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { getNetPosition } from "@/lib/netPosition";
import type { SectorSlug } from "@/lib/types";

// One compact horizontal strip: what the corpus does to this sector, by
// valence, split by legal standing. Numbers and hairline rules only — the
// valence accents are the ones the register already uses, and nothing here is
// charted.
//
// A sector with nothing on one side shows the zero. A true zero is information:
// "no simplification at all" is a finding, and hiding the row would turn it
// into an absence the reader has to notice for themselves.
//
// A weight line was here and is now SUPPRESSED, not deleted. weight_intensity
// is recorded on omnibus rows only, and omnibus rows name no sector, so the
// line read "weight not recorded" on all fourteen sectors — fourteen copies of
// one fact about the register, printed where a reader is looking for a fact
// about their sector. The fact itself is now stated once, on /coverage, where
// it belongs. lib/netPosition.ts still computes the distribution and
// intensityLine() still formats it, so restoring the line when weight is
// extracted for the other files is uncommenting one element.
export default function NetPositionStrip({ slug }: { slug: SectorSlug }) {
  const net = getNetPosition(slug);
  if (!net.total) {
    return <p className="section-note">No measure in the corpus reaches this sector.</p>;
  }

  return (
    <div className="netpos">
      <div className="netpos-total">
        <span className="netpos-total-value">{net.total}</span>
        <span className="netpos-total-label">
          measures reach this sector · {net.negative} press, {net.positive} relieve or grant
        </span>
      </div>
      <div className="netpos-rows">
        {net.rows.map((row) => (
          <div key={row.valence} className={`netpos-row ${row.positive ? "is-pos" : "is-neg"}`}>
            <div className="netpos-valence">{row.valence}</div>
            <div className="netpos-count">{row.total}</div>
            <div className="netpos-split">
              {/* Both sides always printed, zero included. */}
              <span>In force {row.inForce}</span>
              <span>Proposed {row.proposed}</span>
              {row.mixed > 0 && <span>Mixed basis {row.mixed}</span>}
            </div>
            {/* Suppressed until weight_intensity exists on rows that name a
                sector — see the note at the top of this file.
                <div className="netpos-intensity">{intensityLine(row)}</div> */}
          </div>
        ))}
      </div>
    </div>
  );
}

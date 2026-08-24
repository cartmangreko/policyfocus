import { getNetPosition } from "@/lib/netPosition";
import type { SectorSlug } from "@/lib/types";

// What the corpus, taken together, does to one sector — drawn rather than
// listed. Same computed inputs as before, no new data: one bar per valence,
// width set from that valence's share of the sector's total, so the shape
// answers "what does this sector actually carry" before a number is read.
//
// THE HATCH IS LOAD-BEARING. The in-force portion of each bar is solid and the
// proposed portion hatched. A bar that drew them alike would tell a reader
// this sector already carries something it does not yet carry, which is the
// single most consequential thing this panel could get wrong — the same
// distinction the basis banners exist to hold everywhere else on the site.
//
// A sector with nothing on one side keeps its row and shows the zero. A true
// zero is information: "no simplification at all" is a finding, and a missing
// row would turn it into an absence the reader has to notice for themselves.
//
// There is deliberately no weight line. Weight stays on the rows that carry
// it, and the state of weight data across files is stated once, on /coverage.
export default function NetPositionStrip({ slug }: { slug: SectorSlug }) {
  const net = getNetPosition(slug);
  if (!net.total) {
    return <p className="section-note">No measure in the corpus reaches this sector.</p>;
  }

  // Widths are shares of the largest row, not of the total: scaled against the
  // total, a sector whose measures are spread across six valences would draw
  // six bars too short to compare with each other, and comparing them is what
  // the panel is for. The count is printed beside every bar, so the scale
  // cannot mislead about magnitude.
  const widest = Math.max(...net.rows.map((r) => r.total), 1);

  return (
    <div className="netpos">
      <div className="netpos-total">
        <span className="netpos-total-value">{net.total}</span>
        <span className="netpos-total-label">
          measures reach this sector · {net.negative} press, {net.positive} relieve or grant
        </span>
      </div>

      <div className="netpos-bars">
        {net.rows.map((row) => {
          const width = (row.total / widest) * 100;
          // Mixed-basis rows sit with the proposed portion: their standing is
          // not settled either, and rounding them up to "in force" is the
          // error the hatch exists to prevent.
          const unsettled = row.proposed + row.mixed;
          const settledWidth = row.total ? (row.inForce / row.total) * width : 0;
          const unsettledWidth = row.total ? (unsettled / row.total) * width : 0;
          return (
            <div
              key={row.valence}
              className={`netpos-bar-row ${row.positive ? "is-pos" : "is-neg"}`}
            >
              <div className="netpos-bar-label">{row.valence}</div>
              <div className="netpos-bar-track">
                <div className="netpos-bar-fill" style={{ width: `${settledWidth}%` }} />
                <div
                  className="netpos-bar-proposed"
                  style={{ left: `${settledWidth}%`, width: `${unsettledWidth}%` }}
                />
              </div>
              <div className="netpos-bar-count">{row.total}</div>
            </div>
          );
        })}
      </div>

      <div className="netpos-key">
        <span>
          <i className="solid" aria-hidden="true" /> In force
        </span>
        <span>
          <i className="hatched" aria-hidden="true" /> Proposed or mixed basis
        </span>
      </div>
    </div>
  );
}

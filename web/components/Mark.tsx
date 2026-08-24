import { markNodes, markSegments, strokeFor, VIEWBOX } from "@/lib/mark";

// The eufabric mark. Geometry from lib/mark.ts and none of its own — see that
// file for why the weave is generated rather than traced.
//
// THREE VARIANTS, ONE GEOMETRY. `lattice` is the default and is lines only.
// `circuit` adds a filled square at every crossing the weft passes over, in
// signal blue, and reads as nodes on a board. `loom` is the lattice: the
// overhanging thread ends already read as loose warp and weft, and a separate
// drawing for it would be the same drawing.
//
// `tone` picks the pairing rather than the colour: the mark is ink on paper,
// paper on ink, paper on signal, and nothing else. Passing a colour would let a
// caller invent a fourth pairing, which is the thing the identity is specific
// about.
export type MarkVariant = "lattice" | "circuit" | "loom";
export type MarkTone = "ink" | "paper";

const INK: Record<MarkTone, string> = {
  ink: "var(--ink)",
  paper: "var(--paper)",
};

export default function Mark({
  size = 40,
  tone = "ink",
  variant = "lattice",
  title,
}: {
  size?: number;
  tone?: MarkTone;
  variant?: MarkVariant;
  /** Set only where the mark stands alone. In the lockup the logotype is the
   *  accessible name and a second one would be read out twice. */
  title?: string;
}) {
  const stroke = strokeFor(size);
  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${VIEWBOX} ${VIEWBOX}`}
      fill="none"
      className="mark"
      style={{ display: "block", overflow: "visible" }}
      role={title ? "img" : "presentation"}
      aria-hidden={title ? undefined : true}
      aria-label={title}
    >
      <g stroke={INK[tone]} strokeWidth={stroke} strokeLinecap="butt">
        {markSegments().map((s, i) => (
          <line key={i} x1={s.x1} y1={s.y1} x2={s.x2} y2={s.y2} />
        ))}
      </g>
      {variant === "circuit" &&
        markNodes().map((n, i) => (
          <rect
            key={i}
            x={n.x}
            y={n.y}
            width={n.size}
            height={n.size}
            fill="var(--signal)"
          />
        ))}
    </svg>
  );
}

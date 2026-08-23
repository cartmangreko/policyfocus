/**
 * The eufabric mark: a plain-weave lattice, generated rather than drawn.
 *
 * Four warp (vertical) and four weft (horizontal) threads on a 24-unit module,
 * one constant line weight, alternating over/under at every crossing, each
 * thread running eight units past the outermost crossing so the weave reads as
 * being assembled rather than finished.
 *
 * WHY A GENERATOR AND NOT A TRACED PATH. The handoff is explicit — reimplement
 * the algorithm, do not hand-place the lines — and the reason survives contact
 * with the codebase: the over/under rule is what makes a single flat stroke
 * read as woven, and a traced copy of it is 32 line segments nobody can check.
 * Generated, the rule is one function, the geometry is a snapshot test, and a
 * change to the weave is a change to four constants.
 *
 * No React here. The component draws it, the favicon writer emits it as a file,
 * and the test asserts on it, so the geometry cannot end up living in whichever
 * of the three somebody edited last.
 */

/** Thread positions on both axes. A 24-unit pitch inside a 120-unit box. */
export const POS = [24, 48, 72, 96] as const;
/** Each thread runs from START to END — eight units of overhang each side. */
export const START = 16;
export const END = 104;
/** Half the gap punched in the thread that passes underneath. */
export const GAP = 5;
export const VIEWBOX = 120;
export const STROKE = 4;
/** Below this rendered size the weave closes up, so the stroke is bumped. */
export const SMALL_PX = 40;
export const STROKE_SMALL = 6;
/** The circuit variant's node, centred on each "over" crossing. */
export const NODE = 7;

export interface Segment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Node {
  x: number;
  y: number;
  size: number;
}

/**
 * The over/under rule, in one place: at crossing (i, j) the weft is on top when
 * (i + j) is even, so the warp is the thread that breaks there — and the other
 * way round when it is odd. Everything else in this file is bookkeeping.
 */
export function weftIsOver(i: number, j: number): boolean {
  return (i + j) % 2 === 0;
}

/** Split one thread into the segments left after its breaks are punched out. */
function thread(unders: number[], at: (from: number, to: number) => Segment): Segment[] {
  const segments: Segment[] = [];
  let cursor = START;
  for (const u of [...unders].sort((a, b) => a - b)) {
    segments.push(at(cursor, u - GAP));
    cursor = u + GAP;
  }
  segments.push(at(cursor, END));
  return segments;
}

export function markSegments(): Segment[] {
  const segments: Segment[] = [];
  // weft — horizontal threads, broken where they pass under
  POS.forEach((y, j) => {
    const unders = POS.filter((_, i) => !weftIsOver(i, j));
    segments.push(...thread([...unders], (from, to) => ({ x1: from, y1: y, x2: to, y2: y })));
  });
  // warp — vertical threads, broken where they pass under
  POS.forEach((x, i) => {
    const unders = POS.filter((_, j) => weftIsOver(i, j));
    segments.push(...thread([...unders], (from, to) => ({ x1: x, y1: from, x2: x, y2: to })));
  });
  return segments;
}

/** The circuit variant: a filled square at every crossing the weft passes over. */
export function markNodes(size: number = NODE): Node[] {
  const nodes: Node[] = [];
  POS.forEach((x, i) =>
    POS.forEach((y, j) => {
      if (weftIsOver(i, j)) nodes.push({ x: x - size / 2, y: y - size / 2, size });
    }),
  );
  return nodes;
}

export function strokeFor(px: number): number {
  return px <= SMALL_PX ? STROKE_SMALL : STROKE;
}

/**
 * The mark as a standalone SVG document. Used by the favicon writer, where
 * there is no React to render through, and by nothing on a page — the
 * component builds its own JSX from the same segments.
 */
export function markSvg(opts: {
  size: number;
  ink: string;
  ground?: string;
  radius?: number;
  nodes?: string;
}): string {
  const { size, ink, ground, radius = 0, nodes } = opts;
  const stroke = strokeFor(size);
  const lines = markSegments()
    .map((s) => `<line x1="${s.x1}" y1="${s.y1}" x2="${s.x2}" y2="${s.y2}"/>`)
    .join("");
  const squares = nodes
    ? markNodes()
        .map((n) => `<rect x="${n.x}" y="${n.y}" width="${n.size}" height="${n.size}" fill="${nodes}"/>`)
        .join("")
    : "";
  // The tile is drawn a module wider than the weave on each side, which is the
  // clear space the handoff asks for, and is why the favicon does not look
  // cropped at 16px.
  const pad = 16;
  const box = VIEWBOX + pad * 2;
  const tile = ground
    ? `<rect width="${box}" height="${box}" rx="${radius}" fill="${ground}"/>`
    : "";
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" ` +
    `viewBox="0 0 ${box} ${box}" fill="none">` +
    tile +
    `<g transform="translate(${pad} ${pad})" stroke="${ink}" ` +
    `stroke-width="${stroke}" stroke-linecap="butt">${lines}</g>` +
    (squares ? `<g transform="translate(${pad} ${pad})">${squares}</g>` : "") +
    `</svg>`
  );
}

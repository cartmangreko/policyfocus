/**
 * Write the favicon set from the mark generator.
 *
 *     node scripts/build-mark-assets.mjs            # writes app/icon.svg, app/apple-icon.svg
 *     node scripts/build-mark-assets.mjs --check    # non-zero if either is stale
 *
 * Next serves app/icon.svg and app/apple-icon.svg as the tab and home-screen
 * icons by convention. They are committed rather than generated at request
 * time, and checked rather than trusted, for the same reason every other built
 * artifact in this repository is: a favicon that has quietly drifted from the
 * mark is a second logo nobody decided to have.
 *
 * The colours are literals here and only here. Everywhere else the mark takes
 * CSS variables, but an icon file is served without a stylesheet, so it carries
 * the two identity hexes itself.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { markSvg } from "../lib/mark.ts";

const INK = "#211f1b";
const PAPER = "#f4f2ea";

const ASSETS = [
  // The tab icon: paper weave on ink, square. At 32px the stroke bumps to 6 so
  // the weave does not close up.
  ["app/icon.svg", { size: 32, ink: PAPER, ground: INK, radius: 0 }],
  // The home-screen tile: the same mark on the 16px-radius tile the identity
  // specifies for app icons, at the size iOS asks for.
  ["app/apple-icon.svg", { size: 180, ink: PAPER, ground: INK, radius: 16 }],
];

const root = join(import.meta.dirname, "..");
let stale = false;

for (const [rel, opts] of ASSETS) {
  const path = join(root, rel);
  const svg = markSvg(opts) + "\n";
  if (process.argv.includes("--check")) {
    let current = null;
    try {
      current = readFileSync(path, "utf8");
    } catch {
      /* missing counts as stale */
    }
    if (current !== svg) {
      console.error(`build-mark-assets: ${rel} is stale or missing — rebuild it`);
      stale = true;
    } else {
      console.log(`build-mark-assets: --check, ${rel} matches`);
    }
  } else {
    writeFileSync(path, svg);
    console.log(`build-mark-assets: wrote ${rel}`);
  }
}

process.exit(stale ? 1 : 0);

/**
 * Snapshot tests for the mark generator.
 *
 *     node --test web/lib/mark.test.ts        (from the repo root)
 *     npm test                                (from web/)
 *
 * WHY A SNAPSHOT AND NOT ASSERTIONS ABOUT LINES. The thing worth protecting is
 * not that there are 32 segments — it is that the weave alternates correctly,
 * and a reader checking that by reading assertions is doing the algorithm's job
 * by hand. So the geometry is committed as data, the test diffs against it, and
 * a change to the weave shows up in review as the coordinates that moved.
 *
 * The structural properties the snapshot cannot express — that every thread is
 * continuous, that no two adjacent crossings resolve the same way — are
 * asserted separately below, because those are the rules, and a snapshot that
 * captured a broken weave would happily keep capturing it.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  END,
  GAP,
  POS,
  START,
  markNodes,
  markSegments,
  markSvg,
  strokeFor,
  weftIsOver,
} from "./mark.ts";

const SNAPSHOT = join(import.meta.dirname, "mark.snapshot.json");

test("the geometry matches the committed snapshot", () => {
  const actual = { segments: markSegments(), nodes: markNodes() };
  if (process.env.UPDATE_SNAPSHOT) {
    writeFileSync(SNAPSHOT, JSON.stringify(actual, null, 2) + "\n");
    return;
  }
  const expected = JSON.parse(readFileSync(SNAPSHOT, "utf8"));
  assert.deepEqual(actual, expected);
});

test("every crossing alternates with both its neighbours", () => {
  for (let i = 0; i < POS.length; i++) {
    for (let j = 0; j < POS.length; j++) {
      if (i + 1 < POS.length) assert.notEqual(weftIsOver(i, j), weftIsOver(i + 1, j));
      if (j + 1 < POS.length) assert.notEqual(weftIsOver(i, j), weftIsOver(i, j + 1));
    }
  }
});

test("each thread runs the full extent, broken only at its unders", () => {
  const segments = markSegments();
  // Sixteen threads, each broken into (breaks + 1) pieces. Two of every four
  // crossings on a thread are unders, so every thread is three pieces.
  assert.equal(segments.length, 2 * POS.length * (POS.length / 2 + 1));

  const horizontal = segments.filter((s) => s.y1 === s.y2);
  const vertical = segments.filter((s) => s.x1 === s.x2);
  assert.equal(horizontal.length, vertical.length);

  for (const y of POS) {
    const row = horizontal.filter((s) => s.y1 === y).sort((a, b) => a.x1 - b.x1);
    assert.equal(row[0].x1, START, `weft at ${y} starts at START`);
    assert.equal(row[row.length - 1].x2, END, `weft at ${y} ends at END`);
    for (let k = 1; k < row.length; k++) {
      assert.equal(row[k].x1 - row[k - 1].x2, GAP * 2, "the break is one full gap");
    }
  }
});

test("no segment has zero or negative length", () => {
  for (const s of markSegments()) {
    assert.ok(s.x2 - s.x1 > 0 || s.y2 - s.y1 > 0, `degenerate segment ${JSON.stringify(s)}`);
  }
});

test("the circuit variant marks exactly the over-crossings", () => {
  assert.equal(markNodes().length, (POS.length * POS.length) / 2);
});

test("the stroke thickens below the small-size threshold", () => {
  assert.equal(strokeFor(200), 4);
  assert.equal(strokeFor(32), 6);
});

test("the standalone SVG carries the tile, the weave and nothing else", () => {
  const svg = markSvg({ size: 32, ink: "#F4F2EA", ground: "#211F1B", radius: 16 });
  assert.match(svg, /^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);
  assert.match(svg, /rx="16"/);
  assert.equal((svg.match(/<line /g) ?? []).length, markSegments().length);
  assert.ok(!svg.includes("undefined"));
});

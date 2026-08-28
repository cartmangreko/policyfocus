import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import path from "path";

import { money, roundDecimal, contract } from "./money.ts";

// THE TYPESCRIPT HALF OF THE PARITY GATE.
//
// data/number_format.json states how this site writes a euro amount and both
// languages implement it. A declaration that both round half away from zero
// proves nothing about whether both DO, so the contract carries vectors and
// each implementation is held against them: this file on the TypeScript side,
// sources/check_number_format.py on the Python side.
//
// The vectors are written by the Python implementation. That is deliberate and
// is not the Python side marking its own homework — check_number_format.py
// regenerates and diffs them, so a Python change that moved a figure would
// fail there, and this file would then fail too unless TypeScript moved with
// it. Neither language can change the shared behaviour alone.

test("every vector in the contract renders identically here", () => {
  for (const c of contract().cases) {
    assert.equal(money(c.value, "long"), c.long, `long form of ${c.value}`);
    assert.equal(money(c.value, "short"), c.short, `short form of ${c.value}`);
    assert.equal(money(c.value, "compact"), c.compact, `compact form of ${c.value}`);
  }
});

test("the tie case that put this contract here", () => {
  // Steel committed exactly €3,250,000,000 and the page printed "€3.2 billion"
  // and "€3.3 bn" four lines apart.
  assert.equal(money(3_250_000_000, "long"), "€3.3 billion");
  assert.equal(money(3_250_000_000, "short"), "€3.3 bn");
});

test("rounding is half away from zero, in both directions", () => {
  assert.equal(roundDecimal(3.25, 1), 3.3);
  assert.equal(roundDecimal(-3.25, 1), -3.3);
  assert.equal(roundDecimal(2.5, 0), 3);
  assert.equal(roundDecimal(-2.5, 0), -3);
  // Not Math.round, which takes -2.5 to -2, and not the format spec's half to
  // even, which takes 2.5 to 2.
});

test("rounding works on digits, not on a binary scaling", () => {
  // 1.005 * 100 is 100.49999999999999 in binary, so scale-then-round gives
  // 1.00 while the decimal digits give 1.01. Python's Decimal(repr(x)) takes
  // the second reading and so does roundDecimal.
  assert.equal(roundDecimal(1.005, 2), 1.01);
  assert.equal(roundDecimal(8.475, 2), 8.48);
});

test("the contract is read, not restated", () => {
  // A hardcoded tier table here would pass every test above and still be a
  // second source of truth, so the module is checked for reading the file.
  const src = fs.readFileSync(path.join(process.cwd(), "lib", "money.ts"), "utf8");
  assert.match(src, /number_format\.json/, "money.ts must read data/number_format.json");
  assert.doesNotMatch(
    src.replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, ""),
    /\b1e9\b|\b1e6\b|1_000_000/,
    "money.ts must take its thresholds from the contract, not restate them",
  );
});

/**
 * The opportunity-signal filter, brief 5 §4.6.
 *
 *     npm test                       (from web/; also runs in prebuild)
 *
 * WHY THIS FILE EXISTS. No record on the platform is an opportunity signal
 * today: the two records that reach cement are whole-act ingestions and name no
 * measures, and the only support-direction measure on the platform —
 * ets:FND-03 — is named by none of them. So the filter renders nothing, the
 * chip does not appear, and the change-record list shows what it always showed.
 *
 * That is the correct output and it is also indistinguishable, from the page,
 * from a filter that does not work. These assertions are the difference. They
 * run the predicate over records built here rather than over the store, so they
 * say what the filter WILL do on the day a record names a support measure,
 * which is the day nobody will be looking at this code.
 *
 * The third clause of §4.6 — a measure that creates demand — is not asserted,
 * because creates_demand_for does not exist until step 3. It is named in
 * lib/opportunity.ts so the day it lands is a one-line change here too.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { isOpportunitySignal } from "./signals.ts";
import type { ChangeRecord } from "./records.ts";

/** Only the fields the predicate reads. Casting the rest away is deliberate:
 *  a fixture that filled in twenty fields would suggest the predicate looks at
 *  them. */
function record(measures: { file: string; row_id: string }[]): Pick<ChangeRecord, "measures"> {
  return { measures };
}

const SUPPORT = new Set(["ets:FND-03"]);

test("a record naming a support-direction measure is a signal", () => {
  assert.equal(isOpportunitySignal(record([{ file: "ets", row_id: "FND-03" }]), SUPPORT), true);
});

test("a record naming only cost-direction measures is not", () => {
  assert.equal(isOpportunitySignal(record([{ file: "cbam", row_id: "FIN-03" }]), SUPPORT), false);
});

test("one support measure among several is enough", () => {
  const r = record([
    { file: "cbam", row_id: "FIN-03" },
    { file: "ets", row_id: "FND-03" },
  ]);
  assert.equal(isOpportunitySignal(r, SUPPORT), true);
});

test("a whole-act record, which names no measure, is not a signal", () => {
  // The two records that reach cement are exactly this shape. A record's object
  // is the act, and an act containing a support measure is not the same claim
  // as a record about that measure.
  assert.equal(isOpportunitySignal(record([]), SUPPORT), false);
});

test("the measure id is composed file-first, and the halves are not interchangeable", () => {
  // `${file}:${row_id}` is the register's id form everywhere. A predicate that
  // built it the other way round would match nothing and would look like a
  // filter with no data behind it, which is exactly what this platform looks
  // like today — hence the assertion.
  assert.equal(isOpportunitySignal(record([{ file: "FND-03", row_id: "ets" }]), SUPPORT), false);
});

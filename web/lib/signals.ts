import type { ChangeRecord } from "./records";

// THE OPPORTUNITY-SIGNAL PREDICATE, brief 5 §4.6, on its own.
//
// It lives in a leaf module — one type import, no value imports, nothing that
// reads the disk — for one reason: so it can be tested. lib/opportunity.ts
// reads the register and the built blocks, which makes it a module that cannot
// load outside a bundler, and a predicate nobody can run in a test is a
// predicate nobody can check. See lib/opportunity.test.mts, and the note there
// about why the check matters more than usual here: no record on the platform
// is a signal today, so a filter that silently did nothing would look exactly
// like the correct output.

/** A change record is an opportunity signal when its object is a funding node,
 *  a support-direction measure, or a measure that creates demand.
 *
 *  Two of the three clauses are live. A record's object is a funding node only
 *  once a record template exists for one, and `creates_demand_for` arrives in
 *  step 3 of brief 5 §9 — both are named here rather than in a comment
 *  elsewhere, so the day either lands the change is in the function it belongs
 *  to.
 *
 *  `support` is the set of measure ids whose money direction for the bearer is
 *  support, decided by the caller from the importance store. This function
 *  holds no opinion about what a support measure is; it is a set membership
 *  test, and keeping it one is what makes it testable. */
export function isOpportunitySignal(
  record: Pick<ChangeRecord, "measures">,
  support: ReadonlySet<string>,
): boolean {
  return record.measures.some((ref) => support.has(`${ref.file}:${ref.row_id}`));
}

/** A stored date, shown at the precision its source gave it.
 *
 *  EVERY DATE ON THE TRANSITION LAYER THAT SAYS WHEN SOMETHING WAS IS STORED
 *  PADDED to the day — a month-precision figure on the first of its month, a
 *  year-precision one on 1 January — with a `..._precision` field beside it
 *  saying what the source actually said. That is right for storage and for
 *  arithmetic, and it is wrong on a page: "as of 2025-01-01" under a figure the
 *  publisher dates to 2025 is a day nobody published, rendered confidently.
 *
 *  So the padding is undone HERE, in one function, and every surface that prints
 *  one of those dates calls it. sources/check_date_precision.py reads the built
 *  pages and fails any that print a padded date in full, so a new surface that
 *  forgets this is caught by the build rather than by a reader.
 *
 *  A DATE WITH NO PRECISION IS PRINTED AS STORED, and that is not a gap. A
 *  funding row's `date`, a technology's readiness date and a source's
 *  `retrieved_date` carry no precision field, because each is a day by
 *  construction: a decision was taken on a day, a reading was made on a day.
 *  `undefined` therefore means "as exact as it looks" rather than "unknown". */
export function atPrecision(date: string, precision?: "day" | "month" | "year"): string {
  if (precision === "year") return date.slice(0, 4);
  if (precision === "month") return date.slice(0, 7);
  return date;
}

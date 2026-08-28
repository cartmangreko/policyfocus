import fs from "fs";
import path from "path";

// How this site writes a euro amount, on the TypeScript side.
//
// THE RULES ARE NOT IN THIS FILE. They are in data/number_format.json, which
// sources/number_format.py reads too. This module is one of two
// implementations of that contract, and the reason the contract is a file
// rather than a constant in each language is that the two used to be written
// separately: build_opportunity.py rendered a total with Python's format spec
// and transition.ts rendered the same total with toFixed, which round a tie in
// opposite directions. Steel committed exactly €3,250,000,000 and the sector
// page printed "€3.2 billion" and "€3.3 bn" four lines apart.
//
// NEITHER LANGUAGE'S BUILT-IN ROUNDING IS USED. `toFixed` rounds half away
// from zero, Python's format spec rounds half to even, and `Math.round` rounds
// half toward positive infinity, so negatives disagree with all of them. Both
// implementations round the number's shortest round-trip decimal
// representation instead — the string `String()` gives here and `repr()` gives
// there, which is the same string.

interface Tier {
  at: number;
  divide_by: number;
  decimals: number;
  long: string;
  short: string;
  compact: string;
}

interface Contract {
  prefix: string;
  group_separator: string;
  decimal_separator: string;
  tiers: Tier[];
  form_separator: Record<string, string>;
  cases: { value: number; long: string; short: string; compact: string }[];
}

let cached: Contract | null = null;

/** The contract, read from the same file the Python side reads. */
export function contract(): Contract {
  if (!cached) {
    const full = path.join(process.cwd(), "..", "data", "number_format.json");
    cached = JSON.parse(fs.readFileSync(full, "utf8")) as Contract;
  }
  return cached;
}

/** Round half away from zero, on the number's decimal digits.
 *
 *  Mirrored character for character by round_decimal in
 *  sources/number_format.py. Any edit here is an edit there, and the contract's
 *  `cases` is what notices if it is not.
 *
 *  Scaling by a power of ten first would reintroduce the divergence somewhere
 *  subtler: 1.005 * 100 is 100.49999999999999 in binary, so a scale-then-round
 *  implementation rounds it down while a digit implementation rounds it up. */
export function roundDecimal(value: number, decimals: number): number {
  const negative = value < 0;
  let text = Math.abs(value).toString();
  if (text.includes("e") || text.includes("E")) text = Math.abs(value).toFixed(20);
  if (!text.includes(".")) return value;
  const [whole, frac] = text.split(".");
  if (frac.length <= decimals) return value;
  const keep = whole + frac.slice(0, decimals);
  const carry = Number(frac[decimals]) >= 5 ? 1 : 0;
  const out = (Number(keep) + carry) / 10 ** decimals;
  return negative ? -out : out;
}

/** The tier the figure belongs in, after rounding is taken into account.
 *
 *  The tier is chosen by the raw value and then PROMOTED once if rounding at
 *  that tier carries the figure up to the next threshold. Each half alone is
 *  wrong: by raw value only, €999,999,999 renders "€1,000 million"; by rounded
 *  value only, €750,000 renders "€1 million". */
function tierFor(value: number): Tier {
  const { tiers } = contract();
  let index = tiers.findIndex((t) => Math.abs(value) >= t.at);
  if (index === -1) index = tiers.length - 1;
  const tier = tiers[index];
  if (index > 0) {
    const above = tiers[index - 1];
    const rounded = roundDecimal(Math.abs(value) / tier.divide_by, tier.decimals);
    if (rounded * tier.divide_by >= above.at) return above;
  }
  return tier;
}

function digits(value: number, tier: Tier): string {
  const c = contract();
  const scaled = roundDecimal(value / tier.divide_by, tier.decimals);
  const fixed = scaled.toFixed(tier.decimals);
  const [whole, frac] = fixed.split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, c.group_separator);
  return frac ? grouped + c.decimal_separator + frac : grouped;
}

/** One euro amount. `form` is "long" for prose and "short" where the unit has
 *  to fit in a column.
 *
 *  THE SIGN GOES OUTSIDE THE SYMBOL — "-€3.3 billion", never "€-3.3 billion".
 *  The minus is about the amount, not about the currency. */
export function money(value: number, form: "long" | "short" | "compact"): string {
  const tier = tierFor(value);
  const word = tier[form];
  const joint = contract().form_separator[form];
  const sign = value < 0 ? "-" : "";
  return (
    `${sign}${contract().prefix}${digits(Math.abs(value), tier)}` + (word ? `${joint}${word}` : "")
  );
}

export const moneyLong = (value: number): string => money(value, "long");
export const moneyShort = (value: number): string => money(value, "short");
export const moneyCompact = (value: number): string => money(value, "compact");

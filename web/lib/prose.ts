import type { ActReach, Arrival } from "./acts";
import { FILES } from "./data";
import type { SummaryCuts } from "./summaries";

// The computed prose layer. Every sentence here is template-rendered from the
// gate-checked objects the strips already display — the same numbers in
// running text, emitted as crawlable copy on the page and reused by the
// meta-description templates. Unique per page because the numbers are;
// consistent by construction because nothing here recomputes anything.
//
// This module is the ONLY place these sentences are worded, and it takes data
// objects, never re-derives them. The scope rule it serves: no free-generated
// text anywhere on the site — every readable sentence is template-rendered
// from the register or George-reviewed content stored as data.

function n(count: number, singular: string, plural?: string): string {
  return `${count} ${count === 1 ? singular : plural ?? `${singular}s`}`;
}

function list(parts: Array<string | null>): string {
  return parts.filter((p): p is string => p !== null).join(", ");
}

/** The three cuts of one summary object, as two sentences. `subject` is the
 *  node's name in running text ("European steel", "the ETS revision",
 *  "the tracked corpus"). */
export function summaryProse(subject: string, cuts: SummaryCuts): string {
  const { direction: d, status: s, channel: c } = cuts;
  const first =
    `The platform holds ${n(cuts.measures, "measure")} for ${subject}: ` +
    list([
      `${d.burden} imposing a burden`,
      `${d.benefit} conferring a benefit`,
      d.unchanged > 0 ? `${d.unchanged} carried over unchanged` : null,
    ]) +
    ".";

  const statusParts = list([
    s.adopted > 0 ? `${s.adopted} from law in force` : null,
    s.proposed > 0 ? `${s.proposed} from proposals` : null,
    s.mixed > 0 ? `${s.mixed} from a file spanning both` : null,
  ]);

  const channelParts = list([
    `${c.direct} arrive directly`,
    `${c.reached} through a channel`,
    c.no_sector > 0 ? `${c.no_sector} apply by size or activity rather than by sector` : null,
  ]);

  return `${first} ${statusParts ? `Of these, ${statusParts}; ` : ""}${channelParts}.`;
}

/** The reach strip as a sentence: names N sectors; M more — including X —
 *  are reached through the intermediating act(s) or channel. */
export function reachProse(actName: string, reach: ActReach): string {
  const base = `${actName} names ${n(reach.named.length, "sector")} and reaches ${reach.totalReach}.`;
  if (reach.reachedOnly.length === 0) return base;

  const names = reach.reachedOnly.map((r) => r.name.toLowerCase());
  const through = [
    ...new Set(reach.reachedOnly.flatMap((r) => r.intermediatingActs)),
  ];
  const channels = [...new Set(reach.reachedOnly.flatMap((r) => r.channels))].map((c) =>
    c.toLowerCase()
  );
  const via =
    through.length > 0 ? `through ${through.join(" and ")}` : `by ${channels.join(" and ")}`;

  return (
    `${actName} names ${n(reach.named.length, "sector")}; ` +
    `${n(reach.reachedOnly.length, "more is", "more are")} — ${names.join(", ")} — reached without being named, ${via}.`
  );
}

/** The arrival panel as a sentence. */
export function arrivalProse(sectorName: string, arrival: Arrival): string {
  const direct = `Pressure arrives at ${sectorName} from ${n(arrival.direct.length, "act")} that ${
    arrival.direct.length === 1 ? "names" : "name"
  } it directly`;
  if (arrival.indirect.length === 0) return `${direct}.`;
  const files = arrival.indirect.map((a) => FILES[a.file].name.split(" — ")[0]);
  return `${direct}, and from ${n(arrival.indirect.length, "more that never does", "more that never do")}: ${files.join(", ")}.`;
}

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

/** The sector transition map's opening sentence, computed. Used until the
 *  reviewed sentence in data/prose.json is approved — see
 *  lib/sitetext.ts:getTransitionNote. Every number is read from the built
 *  ranking and the transition files, so this sentence cannot disagree with the
 *  sections below it. */
export function transitionProse(cuts: {
  subject: string;
  transitions: string[];
  measuresInView: number;
  measuresTotal: number;
  bottlenecks: number;
  projects: number;
  operating: number;
  paused: number;
}): string {
  const t =
    cuts.transitions.length === 1
      ? `one transition, ${cuts.transitions[0]}`
      : `${n(cuts.transitions.length, "transition")} — ${list(cuts.transitions)}`;
  const built = list([
    cuts.operating > 0 ? `${cuts.operating} operating` : null,
    cuts.paused > 0 ? `${cuts.paused} paused` : null,
  ]);
  return (
    `European ${cuts.subject} is under ${t}. ` +
    `Of ${n(cuts.measuresTotal, "tracked measure")} reaching the sector, ` +
    `${cuts.measuresInView} carry money or a named constraint; ` +
    `${n(cuts.bottlenecks, "bottleneck")} stand in the way, and ` +
    `${n(cuts.projects, "project")} ${cuts.projects === 1 ? "is" : "are"} building past them` +
    `${built ? ` (${built})` : ""}.`
  );
}

// ---------------------------------------------------------------------------
// The geography. Three templates: the heading and standfirst over a regional
// crop, the same pair over a Europe-wide overview, and the text a mark carries.
//
// THESE ARE TIER 1. Every one is rendered from the built map object, which
// sources/build_maps.py wrote and sources/check_coordinates.py placed, so every
// noun and every number in them points at gate-checked data. Worded here, once,
// like every other computed sentence on the site.
//
// TWO WORDS THAT DO NOT APPEAR, and their absence is the rule rather than an
// oversight. The picture is never called a map: "map" is on the framing list in
// display_vocabulary.py, and a page that calls itself one has told the reader it
// is a place things are drawn rather than a place they are worked out. "Plant"
// is on the same list, so a mark is a SITE or a WORKS in running text, and
// "plant" survives only inside an installation's own name.

export interface GeoCounts {
  label: string;
  place: string;
  sites: number;
  dependency: number;
  technology: number;
  sector: number;
}

/** The regional crop on a project page. */
export function projectGeoProse(c: GeoCounts): { heading: string; standfirst: string } {
  const near = c.technology + c.sector;
  const parts: string[] = [
    c.sites > 1
      ? `${c.label} runs across ${n(c.sites, "site")}, at ${c.place}.`
      : `${c.label} is at ${c.place}.`,
  ];
  if (c.dependency === 1) {
    parts.push("The store its captured CO₂ reaches is drawn with it.");
  } else if (c.dependency > 1) {
    parts.push(`The ${c.dependency} stores its captured CO₂ reaches are drawn with it.`);
  }
  parts.push(
    near > 0
      ? "Also in frame: " +
        list([
          c.technology > 0 ? `${n(c.technology, "site")} using the same technology` : null,
          c.sector > 0 ? `${n(c.sector, "site")} in the same sector` : null,
        ]) +
        "."
      : "Nothing else on file falls inside this frame.",
  );
  return { heading: `Where ${c.label} is`, standfirst: parts.join(" ") };
}

/** The Europe-wide overview on a sector page.
 *
 *  THE THREE GROUPS PARTITION THE STATUSES and the sentence says so by adding
 *  up. An earlier wording gave only the running and the stopped, so a sector
 *  with eight sites announced "4 operating or under construction, 1 paused" and
 *  left three of them unaccounted for — a reader can subtract, and a sentence
 *  that invites the subtraction and then fails it is worse than one that says
 *  less. `pending` is everything between a decision and a building site. */
export function sectorGeoProse(c: {
  sector: string;
  sites: number;
  countries: number;
  running: number;
  pending: number;
  stopped: number;
}): { heading: string; standfirst: string } {
  const state = list([
    c.running > 0 ? `${c.running} operating or under construction` : null,
    c.pending > 0 ? `${c.pending} announced or funded and not yet built` : null,
    c.stopped > 0 ? `${c.stopped} paused or cancelled` : null,
  ]);
  return {
    heading: `Every ${c.sector} site on file, across Europe`,
    standfirst:
      `${n(c.sites, "site")} in ${n(c.countries, "country", "countries")}` +
      (state ? `: ${state}.` : ".") +
      " Each one opens its own page.",
  };
}

/** What a mark says when a reader points at it. One line, because it is a
 *  tooltip: the name, whose it is, and the coordinate the register claims. */
export function geoMarkProse(m: {
  label: string;
  sub: string;
  site: string;
  coordinates: string;
}): string {
  return `${m.label} — ${m.sub}. ${m.site}, ${m.coordinates}.`;
}

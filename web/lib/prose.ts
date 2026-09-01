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
  /** The subject is cancelled, so this crop is the one frame it appears on. */
  subjectCancelled: boolean;
}

/** The regional crop on a project page.
 *
 *  EVERY CLAUSE HERE COUNTS WHAT IS DRAWN, and since the ruling that took
 *  cancelled projects off every frame but their own, that is no longer the same
 *  as what is on file. Two clauses moved:
 *
 *  THE EMPTY-FRAME CLAUSE. "Nothing else on file falls inside this frame" was a
 *  claim about the register and is now false where a cancelled project sits in
 *  view — ArcelorMittal's two sites are inside SALCOS's crop and are not drawn
 *  on it. The sentence now says what it can still see: nothing else DRAWN.
 *
 *  THE SUBJECT'S OWN STATE. A cancelled subject is drawn here and nowhere else,
 *  which no reader can infer from a mark that looks like every other hollow one,
 *  so the standfirst says it and the key repeats it against the ring. */
export function projectGeoProse(c: GeoCounts): { heading: string; standfirst: string } {
  const near = c.technology + c.sector;
  const parts: string[] = [
    c.sites > 1
      ? `${c.label} runs across ${n(c.sites, "site")}, at ${c.place}.`
      : `${c.label} is at ${c.place}.`,
  ];
  if (c.subjectCancelled) {
    parts.push("It was cancelled, and is drawn here and on no other frame.");
  }
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
      : "Nothing else drawn falls inside this frame.",
  );
  return { heading: `Where ${c.label} is`, standfirst: parts.join(" ") };
}

/** The Europe-wide overview on a sector page.
 *
 *  THE HEADING IS THE QUESTION THE PICTURE ANSWERS. "Every {sector} site on
 *  file, across Europe" stopped being true when cancelled projects came off the
 *  frame, and rather than qualify it the heading now says what the picture is
 *  actually of: where Europe is building. A cancelled conversion is on file and
 *  is not something Europe is building, so its absence is the heading keeping
 *  its word rather than the heading being narrowed to fit.
 *
 *  THE THREE GROUPS PARTITION THE DRAWN STATUSES and the sentence says so by
 *  adding up. An earlier wording gave only the running and the stopped, so a
 *  sector with eight sites announced "4 operating or under construction, 1
 *  paused" and left three of them unaccounted for — a reader can subtract, and a
 *  sentence that invites the subtraction and then fails it is worse than one
 *  that says less. `pending` is everything between a decision and a building
 *  site. `paused` is the whole of the third group now: cancelled is the one
 *  status that is not on this frame, so a group called "paused or cancelled"
 *  would be naming a state the picture cannot show.
 *
 *  AND THE SUM IS OVER DRAWN SITES, SO THE SENTENCE SAYS WHAT IT LEFT OFF. The
 *  three groups add to the sites in the picture; the clause after them names the
 *  register's remainder. Without it an overview would quietly shrink — a reader
 *  counting steel's sites here and on the projects table below would find two
 *  missing and nothing on the page accounting for them. */
export function sectorGeoProse(c: {
  sector: string;
  sites: number;
  countries: number;
  running: number;
  pending: number;
  paused: number;
  undrawn: { projects: number; sites: number };
}): { heading: string; standfirst: string } {
  const state = list([
    c.running > 0 ? `${c.running} operating or under construction` : null,
    c.pending > 0 ? `${c.pending} announced or funded and not yet built` : null,
    c.paused > 0 ? `${c.paused} paused` : null,
  ]);
  const { projects, sites } = c.undrawn;
  const left =
    projects > 0
      ? ` ${n(projects, "cancelled project")}, on ${n(sites, "site")}, ` +
        `${projects === 1 ? "is" : "are"} on file and not drawn.`
      : "";
  return {
    heading: `Where Europe is building ${c.sector}`,
    standfirst:
      `${n(c.sites, "site")} in ${n(c.countries, "country", "countries")}` +
      (state ? `: ${state}.` : ".") +
      " Each one opens its own page." +
      left,
  };
}

/** THE KEY, SPELLED OUT. Two axes, and the reader is told both rather than
 *  being left to infer either: SHAPE says what kind of thing a mark is, and FILL
 *  says whether it is doing anything.
 *
 *  The fill wording is the part that had to be written down. "not running" on
 *  its own describes the hollow mark without saying what the filled one means,
 *  so a reader who saw only filled marks learned nothing from the key at all —
 *  and "running" is not the word the register uses, which grades a project
 *  through announced, funded, construction and operating. The two lines here
 *  name the statuses on each side of that line, and they are the same statuses
 *  LocationMap's RUNNING set divides on and the same ones sectorGeoProse counts
 *  in its standfirst, so the key, the picture and the sentence above it cannot
 *  drift apart without one of the three being edited alone.
 *
 *  HOLLOW IS NOW ENUMERATED. It used to mean "not running", which quietly
 *  covered cancelled as well; cancelled is no longer drawn on an overview or as
 *  context, so hollow there means announced, funded, or paused and the key says
 *  the three. Naming them rather than keeping the safe negative is the point of
 *  the change: a reader who is told what hollow contains can see that a project
 *  they know of is not in the picture, and a reader told only "not running"
 *  cannot.
 *
 *  THE RING IS NAMED ON EVERY CROP, and it is the third line. It has always
 *  been drawn and never explained — a reader was left to work out that the
 *  circle around one mark meant "the one you are looking at". On an ordinary
 *  crop it reads "ringed: this project" and nothing more.
 *
 *  AND ON THE ONE FRAME WHERE HOLLOW IS NOT THE WHOLE TRUTH, THAT LINE CARRIES
 *  IT. A cancelled project is drawn on its own page's crop and on nothing else,
 *  so its mark is hollow and its status is outside the three the hollow line
 *  names. The clause is appended to the ring's own line, taken over two rejected
 *  answers:
 *
 *    THE MARK DOES NOT CHANGE. It stays a hollow dot inside the ring. A third
 *    fill state — a dashed outline, a struck mark — would add a distinction to a
 *    vocabulary that deliberately has two axes, and it would have to be
 *    explained in the key of every frame that does not draw it, which is all but
 *    one of them. The picture is not the place to carry a fact that appears
 *    once.
 *
 *    THE RING CARRIES IT INSTEAD. The ring already means "the one this page is
 *    about" and is present on exactly the frames where the exception applies, so
 *    on a crop whose subject is cancelled its line reads "ringed: this project —
 *    cancelled, and drawn on no other frame". That says the status, and it says
 *    the thing a reader could not otherwise know: that this mark's absence
 *    everywhere else is a rule and not an oversight. On every other crop the
 *    same line stops after "this project", because there is nothing further to
 *    tell and a key that explains an exception on the frames it does not apply
 *    to has taught the reader a rule they cannot see.
 *
 *  The hollow line is left alone on that frame rather than widened to include
 *  cancelled, because it is still exactly right for every OTHER mark there, and
 *  the ringed line directly under it is what covers the subject. */
export function geoKeyProse(o: {
  hasStore: boolean;
  /** A crop's subject, which is the mark wearing the ring. Absent on an
   *  overview, which has no subject and draws no ring. `running` is the
   *  subject's own fill, so the swatch in the key is the mark on the paper and
   *  not a filled stand-in for a hollow one. */
  subject?: { running: boolean; cancelled: boolean };
}): {
  role: "plant" | "storage";
  running: boolean;
  ringed?: boolean;
  text: string;
}[] {
  return [
    // THE SHAPE AXIS IS NAMED ONLY WHERE THE PICTURE DRAWS IT. A frame with no
    // store on it has one shape, so "a dot is a works" would put a second
    // identical filled dot in the key beside the one explaining fill — which
    // reads as a mistake and teaches a distinction the reader cannot see.
    ...(o.hasStore
      ? ([
          { role: "plant" as const, running: true, text: "a dot is a works" },
          { role: "storage" as const, running: true, text: "a triangle is a store" },
        ])
      : []),
    { role: "plant", running: true, text: "filled: operating or under construction" },
    { role: "plant", running: false, text: "hollow: announced, funded, or paused" },
    ...(o.subject
      ? [
          {
            role: "plant" as const,
            running: o.subject.running,
            ringed: true,
            text: o.subject.cancelled
              ? "ringed: this project — cancelled, and drawn on no other frame"
              : "ringed: this project",
          },
        ]
      : []),
  ];
}

/** What a mark says when a reader points at it. One line, because it is a
 *  tooltip: the name, whose it is, and the coordinate the register claims.
 *
 *  UNCHANGED BY THE LABELS. The label on the paper carries the name and, where
 *  there is room, the company; this is where the site and the coordinate still
 *  live, and it is the whole of the label for a mark whose company had to be
 *  dropped to fit. */
export function geoMarkProse(m: {
  label: string;
  sub: string;
  site: string;
  coordinates: string;
}): string {
  return `${m.label} — ${m.sub}. ${m.site}, ${m.coordinates}.`;
}

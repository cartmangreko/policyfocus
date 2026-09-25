import { SECTORS } from "./data";
import { atPrecision } from "./dates";
import { supportFact, supportMeasures } from "./opportunity";
import {
  FUNDING_ANNOUNCED,
  FUNDING_COMMITTED,
  byLastChange,
  eur,
  fundingForProject,
  fundingTotals,
  getBottlenecks,
  getFunding,
  getImportance,
  getParameters,
  getProjects,
  getTechnologies,
  lastChange,
  materialFlows,
  measureHref,
  projectHref,
  type Bottleneck,
  type Parameter,
  type Project,
} from "./transition";

// THE HUB'S FOUR BLOCKS, assembled — brief 15.
//
// WHAT A BLOCK IS, and it is the same three parts in all four cases and nothing
// else:
//
//   1  one FRAMING LINE, computed from the block's own gated source, carrying
//      the as-of date. Its counts sum against the spoke page, which is what
//      makes the line checkable rather than decorative.
//   2  a SHORT LIST, capped at HUB_BLOCK_CAP. Each item is one row — a name,
//      one computed fact, a date. No paragraph per item.
//   3  one LINK to the spoke that carries the complete list, in the fixed form
//      "All {n} …" where n is the spoke's count.
//
// A BLOCK WITH NOTHING ON FILE renders the framing line saying so, with the
// date, and no list. Not a placeholder, not an empty-state graphic, not an
// invented item: the fact that a sector has no constraints on file is a fact
// about the sector and is one of the four answers this page owes a reader.
//
// THE HUB HOLDS NO COMPLETE LIST. That is the whole of the reduction: before
// this, the hub rendered every project, every technology, every material and
// every constraint, and the spoke pages it linked to did not exist. Now the
// complete list lives on the spoke and the hub carries the top of it. The
// property is gated — sources/check_hub_list_duplication.py fails the build on
// any list here longer than the cap, and on any block link whose n disagrees
// with the spoke it points at.
//
// NOTHING HERE COMPUTES A RANKING OR A EURO. Both come from the gated Python
// artefacts — data/transition/importance/<sector>.json and the parameter store
// — exactly as they did when the sections this replaces rendered them.

/** The cap on every block, in ONE place so it is one change.
 *
 *  Five is George's ruling (brief 15, 23 Sep). It caps what is DRAWN and
 *  nothing else: every block's framing line counts the whole population and its
 *  link goes to all of it. */
export const HUB_BLOCK_CAP = 5;

/** One row of a block. A name, one computed fact, a date — and the two labels
 *  the design already has, where the row carries one. */
export interface HubItem {
  key: string;
  name: string;
  /** Where the name goes. Null for an item with no page of its own, which
   *  expands in place on the spoke rather than opening anything here. */
  href: string | null;
  /** The display-vocabulary kind, on the one block that mixes kinds. */
  kind?: "technology" | "material" | "constraint";
  /** The existing status badge, on the one block whose rows have a status. */
  status?: { label: string; cls: string };
  /** THE one computed fact for this row. One clause, never a paragraph. */
  fact: string;
  /** Rendered at the precision the register knows it, or null where the row
   *  carries no date. Never today's date standing in for a missing one. */
  date: string | null;
}

export interface HubBlock {
  /** The section id. The same string the nav, the anchor and the gate use. */
  id: string;
  framing: string;
  items: HubItem[];
  /** The complete list's length — the n in "All {n} …", and the number the
   *  spoke has to agree with. */
  total: number;
  link: { href: string; label: string } | null;
}

/** The four project status groups. The hub says the group; the spoke's table
 *  says the exact status. A hub row that named all eight statuses would be
 *  asking a reader to hold a vocabulary in their head to read five lines. */
const PROJECT_GROUP = {
  operating: "running",
  commissioning: "running",
  construction: "running",
  announced: "pending",
  funded: "pending",
  fid: "pending",
  paused: "paused",
  cancelled: "cancelled",
} as const;

const GROUP_LABEL: Record<string, string> = {
  running: "Running",
  pending: "Pending",
  paused: "Paused",
  cancelled: "Cancelled",
};

/** The latest date on a set of rows, or null where none of them carries one.
 *  An as-of date is a fact about the DATA, never about the build: a block whose
 *  newest row is from March says March, on a page built today. */
function asOf(dates: (string | null | undefined)[]): string | null {
  const real = dates.filter((d): d is string => Boolean(d));
  return real.length > 0 ? real.reduce((a, b) => (b > a ? b : a)) : null;
}

/** " — as of {date}", or nothing at all. A framing line with no date is a
 *  framing line over rows that carry none, and inventing one would be the page
 *  asserting a currency nobody checked. */
function stamp(date: string | null): string {
  return date ? ` — as of ${date}` : "";
}

/** The ISO date inside a measure's `when`, or null.
 *
 *  A MEASURE'S `when` IS A CLAUSE, NOT A DATE. "From 1 January 2029 (Annex II)"
 *  is the right thing to print in a citation line and the wrong thing to put in
 *  a column of dates: it is prose, it is long, and a row that tried to hold it
 *  unwrapped pushed the hub sideways off a phone. So the column takes the date
 *  the clause contains where it contains one, and nothing where it does not —
 *  and the clause itself stays on the policies spoke, in the cite line it has
 *  always been part of. */
function isoIn(when: string | null): string | null {
  if (!when) return null;
  const m = when.match(/\d{4}-\d{2}-\d{2}/);
  return m ? m[0] : null;
}

function plural(n: number, one: string, many = `${one}s`): string {
  return `${n} ${n === 1 ? one : many}`;
}

// ---------------------------------------------------------------- projects --

/** WHAT IS BEING BUILT.
 *
 *  ORDERING BASIS: last status change, most recent first — `byLastChange`, the
 *  same ordering the section this replaces used for its table, so the top five
 *  here are the top five rows of the spoke's table and a reader moving between
 *  them is not re-sorted.
 *
 *  THE FIGURE ON THE ROW is the one the hub already showed: public funding,
 *  said with the status group the funding node carries. It used to be summed
 *  as committed money only, so a project whose money is announced showed a dash
 *  — which is how IFESTOS came to look unfunded beside GeZero and ANRAV when
 *  what differs between them is the status of the allocation, not its
 *  existence. The group is now printed with the figure, in both cases. */
export function sectorProjectRows(slug: string): Project[] {
  return byLastChange(getProjects(slug));
}

export function projectsBlock(slug: string): HubBlock {
  const rows = sectorProjectRows(slug);
  const params = getParameters();
  const group = (p: Project) => PROJECT_GROUP[p.status];
  const counts = { running: 0, pending: 0, paused: 0, cancelled: 0 };
  for (const p of rows) counts[group(p)] += 1;
  const dates = rows.map((p) => lastChange(p)?.date ?? null);
  const date = asOf(dates);

  const parts = [
    counts.running > 0 ? `${counts.running} running` : null,
    counts.pending > 0 ? `${counts.pending} announced or funded` : null,
    counts.paused > 0 ? `${counts.paused} paused` : null,
    counts.cancelled > 0 ? `${counts.cancelled} cancelled` : null,
  ].filter(Boolean);

  const framing =
    rows.length === 0
      ? `No project on file in European ${SECTORS[slug as keyof typeof SECTORS]?.toLowerCase() ?? slug}${stamp(date)}`
      : `${plural(rows.length, "project")} on file — ${parts.join(", ")}${stamp(date)}`;

  return {
    id: "projects",
    framing,
    total: rows.length,
    link: rows.length > 0 ? { href: `/sectors/${slug}/projects`, label: `All ${plural(rows.length, "project")}` } : null,
    items: rows.slice(0, HUB_BLOCK_CAP).map((p) => {
      const last = lastChange(p);
      const money = fundingTotals(fundingForProject(p.id), params);
      const announced = fundingForProject(p.id).filter((f) => FUNDING_ANNOUNCED.includes(f.status));
      // The committed figure where there is one, the announced count where
      // there is not, and the group said out loud in both cases.
      const fact = money.committed
        ? `${eur(money.committed)} committed`
        : money.committedCount
          ? "committed funding, amount undisclosed"
          : announced.length > 0
            ? `${plural(announced.length, "allocation")} announced`
            : "no public funding on file";
      const site = [p.plant, p.country].filter(Boolean).join(", ");
      return {
        key: p.id,
        name: p.name,
        href: projectHref(p.id),
        status: { label: GROUP_LABEL[group(p)], cls: group(p) },
        fact: site ? `${site} — ${fact}` : fact,
        date: last ? atPrecision(last.date, last.date_precision) : null,
      };
    }),
  };
}

// ----------------------------------------------------------------- depends --

/** One quantified fact about a constraint, or the line naming what it rests
 *  on. A constraint that is not quantified says so — see the section this
 *  replaces, which printed "Not quantified yet." under the same rows. */
function bottleneckFact(b: Bottleneck, params: Map<string, Parameter>): string {
  for (const id of b.quantified_by) {
    const p = params.get(id);
    if (p) return `${p.value} ${p.unit} — ${p.name}`;
  }
  const src = b.sources[0];
  return src ? `not quantified — ${src.publisher}` : "not quantified";
}

/** WHAT IT DEPENDS ON: technologies, materials and constraints in one list.
 *
 *  ONE QUESTION, THREE NODE KINDS. They were three sections, and a reader
 *  asking what a sector depends on does not care which store the answer comes
 *  out of. Each row carries its kind label so the fold is visible rather than
 *  silent, and the order inside the block is technologies, then materials, then
 *  constraints, each in the internal order its own section used. The cap
 *  applies to the WHOLE block, not to each kind: five rows, whatever they are.
 *
 *  A NODE APPEARS ONCE. materialFlows() already refuses to put one material in
 *  two lists on the strength of the same edge (assertDisjoint), and the fold
 *  here dedupes across the three kinds by node id, so a material that is both
 *  an input and an output is one row. */
export function sectorDependencies(slug: string): HubItem[] {
  const params = getParameters();
  const technologies = getTechnologies(slug);
  const flows = materialFlows(slug);
  const bottlenecks = getBottlenecks(slug);

  const items: HubItem[] = [];
  const seen = new Set<string>();
  const push = (item: HubItem) => {
    if (seen.has(item.key)) return;
    seen.add(item.key);
    items.push(item);
  };

  for (const t of technologies) {
    const deps = t.dependency ?? [];
    const fact = t.readiness
      ? `${t.readiness.level}${t.readiness.note ? ` — ${t.readiness.note}` : ""}`
      : deps.length > 0
        ? `depends on ${deps.join(", ")}`
        : t.description.split(". ")[0];
    push({
      key: `technology:${t.id}`,
      name: t.name,
      href: `/sectors/${slug}/technologies#technology-${t.id}`,
      kind: "technology",
      fact,
      date: t.readiness?.date ?? null,
    });
  }

  for (const row of [...flows.inputs, ...flows.outputs, ...flows.substitutes]) {
    const m = row.material;
    const basis = row.plants > 0 ? plural(row.plants, "plant") : row.sectorWide ? "sector-wide" : null;
    push({
      key: `material:${m.id}`,
      name: m.name,
      // A material node has a page; the edge basis is read there, which is
      // where §0.1 puts the set behind a computed figure.
      href: `/materials/${m.id}`,
      kind: "material",
      fact: basis ? `${m.type.replace("_", " ")} — ${basis}` : m.type.replace("_", " "),
      date: asOf(row.edges.map((e) => e.since)),
    });
  }

  for (const b of bottlenecks) {
    push({
      key: `bottleneck:${b.id}`,
      name: b.name,
      href: `/sectors/${slug}/technologies#bottleneck-${b.id}`,
      kind: "constraint",
      fact: bottleneckFact(b, params),
      date: asOf(b.sources.map((s) => s.date ?? null)),
    });
  }

  return items;
}

/** The framing line's three clauses, over the same populations the list above
 *  is built from. The list is one row per node and the line is one clause per
 *  KIND, which is why they are counted separately rather than one being derived
 *  from the other. */
function dependsClauses(slug: string): string[] {
  const technologies = getTechnologies(slug);
  const flows = materialFlows(slug);
  const bottlenecks = getBottlenecks(slug);
  const parts = [
    technologies.length > 0 ? plural(technologies.length, "technology", "technologies") : null,
    flows.inputs.length + flows.outputs.length + flows.substitutes.length > 0
      ? plural(new Set([...flows.inputs, ...flows.outputs, ...flows.substitutes].map((r) => r.material.id)).size, "material")
      : null,
    bottlenecks.length > 0 ? plural(bottlenecks.length, "constraint") : null,
  ].filter((c): c is string => Boolean(c));
  return parts;
}

export function dependsBlock(slug: string): HubBlock {
  const items = sectorDependencies(slug);
  const parts = dependsClauses(slug);
  const date = asOf(items.map((i) => i.date));

  const framing =
    items.length === 0 ? `Nothing on file${stamp(date)}` : `${parts.join(", ")}${stamp(date)}`;

  return {
    id: "depends",
    framing,
    total: items.length,
    link:
      items.length > 0
        ? {
            href: `/sectors/${slug}/technologies`,
            label: `All ${plural(items.length, "dependency", "dependencies")}`,
          }
        : null,
    items: items.slice(0, HUB_BLOCK_CAP),
  };
}

// ---------------------------------------------------------------- policies --

/** WHAT POLICY DOES. The ranked list, capped, with a plain title and one
 *  sentence per measure.
 *
 *  THE RANK IS THE ORDER AND IS NOT DISPLAYED. It was not displayed before
 *  either; what has gone is the numbered <ol>, because a number beside a
 *  measure reads as a score a reader can argue with and the score is on the
 *  measure's own page.
 *
 *  THE OVERLAP RULE IS UNCHANGED (brief 5 §5): this is the only place on the
 *  hub that renders a measure's standard one-liner, and
 *  sources/check_one_liner_scope.py still fails the build if it appears
 *  anywhere else. */
export function sectorPolicyRows(slug: string) {
  const imp = getImportance(slug);
  // No importance file for this sector: the register's own order, and the
  // framing line says there is no importance basis rather than implying one.
  return (imp?.measures ?? []).filter((m) => m.in_sector_view);
}

export function policiesBlock(slug: string): HubBlock {
  const imp = getImportance(slug);
  const all = imp?.measures ?? [];
  const inView = all.filter((m) => m.in_sector_view);
  const ranked = sectorPolicyRows(slug);
  // THE RANKING'S AS-OF IS ITS INPUTS', and it has to be: the importance file
  // carries no date of its own, and a measure's `when` is a clause about when a
  // provision BITES rather than a statement of how current the ordering is.
  // build_from.parameters names every parameter the ranking was priced on, and
  // each of those carries the date its value is current to.
  const params = getParameters();
  const date = asOf(
    (imp?.built_from.parameters ?? []).map((id) => params.get(id)?.date_of_value ?? null),
  );

  const framing = imp
    ? inView.length === 0
      ? `No EU measure in this sector's view${stamp(date)}`
      : `${inView.length} of ${plural(all.length, "tracked measure")} are in this sector's view, ordered by what they cost or grant it${stamp(date)}`
    : `${plural(all.length, "tracked measure")}, in register order: no importance basis is computed for this sector${stamp(date)}`;

  return {
    id: "policies",
    framing,
    total: ranked.length,
    link:
      ranked.length > 0
        ? { href: `/sectors/${slug}/policies`, label: `All ${plural(ranked.length, "measure")}` }
        : null,
    items: ranked.slice(0, HUB_BLOCK_CAP).map((m) => ({
      key: m.measure,
      name: m.plain ? m.plain.title : m.measure,
      href: measureHref(m.measure),
      fact: m.plain ? m.plain.sentence : m.duty,
      date: isoIn(m.when),
    })),
  };
}

// ------------------------------------------------------------- opportunity --

/** OPPORTUNITY, unchanged in definition: the four computed sources and nothing
 *  else. Two of the four exist today — funding by status group, and the
 *  support-direction measures — because `creates_demand_for` edges and dated
 *  open windows are steps 3 and 4 of brief 5 §9 and are not built. The block
 *  renders what is computed; it does not stand in for what is not.
 *
 *  THE FRAMING LINE IS THE COMMITTED-FUNDING SUM the section already computed,
 *  with the date the sum is complete THROUGH — never the build's date.
 *  Announcements are counted and never summed: a euro figure made of
 *  intentions reads as money that exists.
 *
 *  AND IT IS THE ONE BLOCK WITH NO LINK. Brief 15 allowed either: the
 *  support-direction filter on the policies spoke if one existed, or no link at
 *  all with the PR saying so. It was first built with the filter — the policies
 *  spoke was being written anyway, so the filter was cheap — and George ruled
 *  against it on the cement read (24 September 2026): opportunity gets no spoke,
 *  and the block renders without a link.
 *
 *  THE RULING IS NOT ABOUT THE ANCHOR, which is why it is worth writing down. A
 *  block's link means "the complete list of what this block is showing you the
 *  top of", and the support-direction measures are not that: the block's framing
 *  line counts ALLOCATIONS and its rows are MEASURES, so a link to the measures
 *  would have promised the rest of a list the line does not count. Opportunity is
 *  the one question on this page whose complete answer has no page yet, and the
 *  missing link says so more honestly than a link to the nearest thing would.
 *  The support list is still on the policies spoke, under #support, reached by
 *  reading that page rather than by being sent to an anchor from here. */
export function sectorSupportRows(slug: string) {
  return supportMeasures(slug);
}

export function opportunityBlock(slug: string): HubBlock {
  const params = getParameters();
  const funding = getFunding(slug);
  const totals = fundingTotals(funding, params);
  const committed = funding.filter((f) => FUNDING_COMMITTED.includes(f.status));
  const announced = funding.filter((f) => FUNDING_ANNOUNCED.includes(f.status));
  const committedAsOf = asOf(committed.map((f) => f.date));
  const support = sectorSupportRows(slug);

  const clauses = [
    totals.committedCount > 0
      ? `${eur(totals.committed)} committed across ${plural(totals.committedCount, "allocation")}${
          totals.undisclosed > 0 ? `, ${totals.undisclosed} of them carrying no published figure` : ""
        }`
      : null,
    announced.length > 0 ? `${plural(announced.length, "allocation")} announced and in no total` : null,
    totals.withdrawnCount > 0 ? `${plural(totals.withdrawnCount, "allocation")} withdrawn` : null,
  ].filter(Boolean);

  const framing =
    clauses.length === 0
      ? `No public money on file for this sector${stamp(committedAsOf)}`
      : `${clauses.join("; ")}${stamp(committedAsOf)}`;

  return {
    id: "opportunity",
    framing,
    total: support.length,
    // No link, by ruling. Not `support.length > 0 ? … : null` with the true
    // branch removed either: the absence is unconditional, so it is written as
    // one rather than left looking like a case nobody filled in.
    link: null,
    items: support.slice(0, HUB_BLOCK_CAP).map((m) => ({
      key: m.measure,
      name: m.plain ? m.plain.title : m.measure,
      href: measureHref(m.measure),
      fact: supportFact(m, funding, params),
      date: isoIn(m.when),
    })),
  };
}

/** The four blocks, in the sequence's order. One function, so the page cannot
 *  render three of them and a sector cannot quietly lack one: a block missing
 *  from a sector's build is a build failure, and the way to make that true is
 *  for there to be no way of building three. */
export function hubBlocks(slug: string): HubBlock[] {
  return [projectsBlock(slug), dependsBlock(slug), policiesBlock(slug), opportunityBlock(slug)];
}

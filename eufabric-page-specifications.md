# Eufabric page specifications: home, sector, company

24 Aug 2026. Supersedes the page-structure sections of earlier briefs where
they conflict — `policyfocus-claude-code-brief.md` describes the register
pipeline and remains authoritative for it; where it describes page structure,
this file wins. Data model, gates, colour layers, prose tiers and display
vocabulary are unchanged and bind everything below.

## 0. Rules that apply to all three pages

1. **Every number links to its source.** A figure taken from one record links
   to that record's source_url. A computed figure (a count, a sum) links to the
   set of records behind it, shown as an expandable list with each record's
   source. No number appears on a surface without a link and an as-of date.
2. **Axios lead block on every page type.** One generated sentence stating the
   situation, built at build time from the page's computed facts; a "Why it
   matters" line; then four or five computed fact lines with as-of dates.
   Generation is gated to the panel facts. `summary_override` in
   `data/transition/overrides.json`, marked reviewed, with a re-review flag when
   the underlying facts change. This is the existing sector-page mechanism
   (`sources/build_lead.py` → `data/transition/lead/<sector>.json` →
   `web/components/LeadBlock.tsx`) extended to home and company pages.
3. **No written judgements on surfaces.** No adjectives (High, Early mover,
   Mature), no composite scores, no /100 anywhere. Where the current data
   carries a qualitative attribute (technology readiness), display the attribute
   value with its source; do not editorialize on it.
4. **Ranking without displayed scores.** The measure importance ranking survives
   as an ordering. The number is not shown. What is shown per measure is the
   computed basis: money attached (with source), the constraint it bears on
   (linked node, with source), attention count since a stated date. George's
   override, where used, appears as a reviewed note with its reason.

   **The basis line is conditional, clause by clause.** It renders the clauses
   whose data exists and omits the rest. The attention clause appears only once
   the watch channel has written `data/transition/attention.json`; cement's
   `attention_available: false` in its importance file is already the right
   switch and the line reads correctly without it. No placeholder text, no
   "attention not yet tracked" filler — an absent clause is absent.
5. **Fixed section order and fixed section presence.** Every page of a type
   renders every section in the same order. An empty section renders with a
   computed "none tracked as of [date]" line, not omitted.

   **Sources appears on every page type.** On sector and company pages it is the
   final section, in the form defined at §2.11: the datasets and registers the
   page stands on, each with its retrieval date and a link. The homepage takes a
   variant rather than an exception — a full register section there would be the
   union of every register on the site, which is noise — so it renders as a
   one-line footer register pointing to the coverage page, which is already the
   site-level statement of what stands on what. The rule is uniform; only the
   form differs, and the reason it differs is stated here rather than left as a
   gap.
6. **Absolute dates only.** As-of dates on figures, event dates on feed entries.
   No relative timestamps.
7. **Prose tiers hold.** Computed template sentences (unique per template
   family, gate-checked), reviewed prose in `data/prose.json`, no free per-page
   text. Display vocabulary rules hold ("Eurostat input-output data", never
   register/row/reached) — `sources/display_vocabulary.py`.

8. **Indexability follows the lead block.** A page is indexable when it renders
   a lead block (§0.2). An evidence page without one carries `DEMOTED` —
   `index: false, follow: true` — which is unlinking plus noindex, never
   deletion: the page keeps its route and its content, and a crawler still walks
   through it to the object pages it links.

   The point of stating it this way is that indexability then tracks this
   specification's own definition of a first-class object page, rather than a
   route list that has to be re-decided every time a route is added.

   **Qualifying today:** measures, sectors, projects. **Qualifying as they are
   built:** companies (§3), technologies, ecosystems (§4.2).

   **Demoted today,** each for its own reason rather than by category: act file
   pages, because they substantially mirror EUR-Lex and indexing near-duplicates
   of official texts helps nobody; change records, because they are dated diffs;
   findings, because as currently built they are single computed statements. The
   browse surfaces — `/acts`, `/measures`, `/findings`, `/changes` — and
   `/coverage` are demoted as thin list pages, with `follow: true` carrying the
   crawler through to the objects beneath them.

   **Every demoted route has its exit, stated by the rule rather than reserved
   to a future decision.** If findings grow into analytical objects that render
   a lead block, they become indexable because the rule says so, not because
   somebody re-opens the question.

   **An owed lead block is a build gap, never grounds to demote.** Today only
   the sector page renders one; measure and project pages qualify by kind and
   their lead blocks are outstanding (§0.2 extends the mechanism to the page
   types §1 and §3 define). A page that qualifies and has not yet been given its
   lead block is indexable and owes one. Reading the test the other way would
   remove the largest class of object pages on the site from the index, which is
   the opposite of what this rule exists to protect.

   **This section is the authority for the route list.** The list in
   `web/lib/launch.ts` predates it and is reviewed against this section; where
   they disagree, this section is what the implementation is wrong about.

   **One source of truth per state.** The global switch (`web/lib/launch.ts`,
   closed by default) decides whether anything is indexable at all; this rule
   decides which pages are, once it is open. Where both speak — a demoted page
   before launch — the robots output must state one `follow` value, not two
   overlapping ones from two sources. Nothing in this section opens any page:
   pre-launch, the switch dominates and everything stays out.

## 1. Homepage

Order above the fold: descriptor, search, six ecosystem tiles, what-changed
feed. Nothing else.

**Masthead.** eu|fabric wordmark, descriptor "Intelligence on what Europe builds
next." Positioning line as reviewed prose below or in the footer, per the design
pass.

**Lead sentence.** One computed sentence over the change records, e.g. "Since
[date], [N] projects changed status and [M] measures moved across [K] sectors."
Each count links to the records behind it.

**Search.** One field across four node kinds: project, company, technology,
measure. Extends the existing `SearchBar` component (currently unrendered and
presentational — three hardcoded example chips, no index of any kind behind it).
Result rows state the node kind. Empty state: a computed "nothing tracked
matches [query]" line plus the six ecosystem links, never a dead end.

**Ecosystem tiles.** Six tiles: green steel, low-carbon cement, batteries,
hydrogen, carbon capture, circular materials. Each tile carries the ecosystem
name and one computed count line ([N] projects, [M] measures, as-of date). The
counts make uneven depth visible on the first screen; the coverage page states
what each ecosystem contains at its current tier.

Ecosystems are their own node kind, not sector keys — see §4.2 for why, and for
what a tile opens.

**What-changed feed.** Reverse-chronological entries generated from watch PRs
and change records. Each entry: event date, one template sentence ("[N] projects
updated across [sectors]", "[Measure] milestone: [computed clause]"), links to
every node touched, link to the source of the change. No hand-written entries.

## 2. Sector page

Example used throughout the build: green steel. Section order, identical on
every sector — eleven sections:

1. Lead block
2. Industrial map
3. What changed
4. Projects
5. Measures
6. Capital
7. Companies
8. Technologies
9. Timeline
10. Related sectors
11. Sources

**Lead block.** Generated sentence plus "Why it matters" line, then fact lines,
each dated and linked:
- Projects tracked: [N] (links to the project table)
- Public funding awarded: [€X] (links to the capital section; sum definition
  displayed on hover or expand: which sources, awarded amounts only)
- Measures: [N] in force, [M] proposed (links to the measures section)
- Latest change: [date], [template sentence] (links to the change record)

**Industrial map.** The sector's technology and material nodes with their edges,
every node clickable to its page. Colour layers, save-as-SVG and the mobile
static variant as already built. Under the diagram, each edge rendered as a
computed sentence in HTML (the standing SEO rule).

Materials no longer stand as their own section. They are nodes on this map and
are read there.

**What changed.** The per-sector strip, absolute dates, entries as on the
homepage but filtered to the sector.

**Projects.** Table: project, country, technology, status, funding source.
Status comes from the status history with its date. Each row opens the project
page. Each funding cell links to the funding record.

**Measures.** The ranked list. Per measure one computed basis line replaces any
"why it matters" prose: "[€X] attached (source) · bears on [constraint] (source)
· [N] press items since [date]", clause by clause as available (§0.4).
Override notes as in §0.4. Clicking opens the measure page.

**Capital.** Funding records grouped by source (Innovation Fund, IPCEI, EIB,
state aid, project finance). Each sum expands to the individual awards, each
with recipient, date, amount, source link. The awarded/announced distinction is
a record attribute and is displayed, never merged into one figure.

**Companies.** One computed line per company: [N] projects in this sector · most
advanced status: [status] · funding received: [€X] · technologies: [list from
project edges]. No position labels. Each opens the company page.

**Technologies.** Table from node attributes: technology, readiness (attribute
value, sourced), cost level (attribute value, sourced), binding constraint
(linked constraint node). No free-text bottleneck column.

Bottlenecks no longer stand as their own section. A constraint is read here, as
the column that says which technology bears it, and on its own node page.

**Timeline.** Chronological merge of measure dates and project status changes,
each entry dated and sourced.

**Related sectors.** Computed from shared technology and material edges, not
curated. Each link states the shared node ("shares: carbon capture, hydrogen").

**Sources, redefined.** With §0.1 every figure cites inline, so this section
stops being the citation mechanism and becomes the page-level register: the
datasets and registers behind the page, each with its retrieval date and a link.
It is cheap, it keeps the credibility function that the old section carried, and
fixed presence (§0.5) applies to it like everything else.

**Excluded for now: supply-chain exposure.** The downstream view (steel costs
propagating into automotive, machinery, construction) cannot be computed
honestly while reach walks suppliers only. The section does not appear on any
sector page until the downstream channel is built from the Eurostat
input-output data. Listed in `ROADMAP.md`; do not ship a placeholder.

## 3. Company page

Example used throughout the build: Heidelberg Materials. Section order,
identical on every company:

1. Lead block
2. Industrial profile
3. Projects
4. Policy exposure
5. Technology map
6. Timeline
7. Related companies
8. Sources

**Lead block.** Generated sentence answering the page's question (the company's
role in the transition), built from computed slots: primary sector, flagship
project (largest or most advanced), funding received. "Why it matters" line.
Fact lines, each dated and linked:
- Installations: [N] European plants (ETS registry, source link)
- Key technology: [from project nodes] (links to the technology page)
- Funding: [€X] across [N] awards (links to the records)
- Carbon pricing: [N] installations covered, free allocation phase-out [year]
  (links to the measure)

No "High/Medium" exposure labels anywhere.

**Industrial profile.** Four fact rows, all links: technologies (from project
edges), materials (produces/consumes edges), constraints (linked constraint
nodes), applicable measures (applies_to edges).

**Projects.** Table as on the sector page, filtered to the company. Each row
opens the project page.

**Policy exposure.** Per applicable measure, one computed clause from the graph
in place of any written effect line. Pattern: "[Measure]: applies to [the
company's covered products/installations from the graph], [provision link]".
Example: "CBAM: covers cement and clinker, which this company produces
([provision])". Clicking opens the provision-level page. Where the graph cannot
yet compute a clause for a measure, the measure is listed with the link only, no
invented effect text.

**Technology map.** The sector's industrial map filtered to nodes the company's
projects touch.

**Timeline.** Funding awards, project status changes, and measure events on the
company's applicable measures, merged chronologically, dated, sourced.

**Related companies.** Computed: same sector plus a shared technology or a
shared applicable measure. Each link states the basis.

**Sources.** As defined at §2.11: the datasets and registers behind the page,
each with its retrieval date and a link. The gap bites hardest here — the lead
block above stands almost entirely on the ETS Union Registry and the award
lists, and a reader who wants to know what those are and when they were read has
nowhere else on the page to look.

## 4. Prerequisites before build

1. **Company node kind.** Not yet in the schema — `company` is today a plain
   string field on each row of `data/transition/projects.json`
   ("Heidelberg Materials"), with nothing behind it. Definition: an entity that
   owns at least one project or operates at least one installation in the graph.
   Sources for population: ETS Union Registry operator field, Innovation Fund
   award recipients, NZIA project owners. Needs: slug rule, edges (owns →
   project, operates → installation, plus the applies_to inverse), and a dedup
   rule for name variants across the three registries.

   **None of those three registries is ingested.** The ETS Union Registry, the
   Innovation Fund award list and the NZIA project owners are all outside the
   repository today, so the dedup rule currently has nothing to dedup. Ingestion
   of at least one of them is inside this prerequisite, not before it.

2. **Ecosystem node kind.** Six instances: green steel, low-carbon cement,
   batteries, hydrogen, carbon capture, circular materials. Edges: ecosystem →
   sector, ecosystem → technology.

   Why a node kind and not six sector keys. The sector spine in
   `data/sectors.json` is keyed on FIGARO industries because the input-output
   joins depend on that keying. Hydrogen, carbon capture and circular materials
   are not FIGARO industries; adding pseudo-keys for them would corrupt the
   join. So the ecosystem sits above the spine and points into it.

   Rendering rule. Where an ecosystem maps 1:1 to a sector (low-carbon cement,
   green steel), the tile opens the sector page directly. Where it is
   cross-cutting (hydrogen, carbon capture, circular materials), the same
   eleven-section template of §2 renders with the query scoped by the
   ecosystem's edges instead of by a sector key. One template, learned once,
   either way.

   Sequenced before the homepage tiles. Does not block the steel dataset.

3. **Steel dataset.** Green steel is the running example of §2, and no steel
   data exists: `hasMap()` requires an importance file plus bottlenecks, and
   cement is the only sector with both. `data/transition/projects.json` holds
   eight projects, all `sector: "cement"`. The sector build needs steel
   projects, bottlenecks, technologies, funding and parameters.

   It goes through the same gates cement went through —
   `sources/check_sector_schema.py`, `sources/check_importance.py`, the
   rebuild-and-diff on every built file. No exceptions for speed.

4. **Search index** across the four node kinds; `SearchBar` extended and
   rendered. Needs the company node kind to exist first.

5. **Change-record template family** feeding the homepage and sector feeds from
   watch channel two output.

6. **Funding record attribute** `awarded | announced`, carried on every funding
   node and displayed wherever sums appear.

7. **Downstream reach channel** from the Eurostat input-output data, required
   before the supply-chain section exists (§2, excluded item).

## 5. Build order

1. Funding `awarded | announced` attribute (§4.6). Smallest, gates every sum on
   all three page types, rides along with anything.
2. Change-record template family (§4.5). The homepage and sector feeds are dead
   without it.
3. Steel dataset (§4.3). Unblocks the §2 rebuild and makes the tile counts
   uneven in the way §1 wants them to be.
4. Ecosystem node kind (§4.2). The tiles need it; the steel work does not.
5. Sector page re-cut to the eleven sections.
6. Company node kind, ingestion and dedup (§4.1), then the company page.
7. Search index across the four node kinds (§4.4).
8. Downstream reach channel (§4.7) → supply-chain section. `ROADMAP.md` only.

**Before `SITE_LAUNCHED` is set:** measure and project lead blocks, so that
§0.8's literal test and the practice coincide at launch and the build-gap clause
there becomes vestigial rather than a standing exemption. Sequenced against the
flag, not against any merge — the global noindex means the clause does no work
until then, and nothing in the eight steps above waits on it.

The launch gate is unchanged. `web/lib/launch.ts` stays closed by default and
nothing in this specification touches it; every surface here ships noindex until
`SITE_LAUNCHED` is set out loud.

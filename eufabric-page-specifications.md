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

   **Superseded for two route classes at the index opening.** The build-gap
   clause above is what would have carried measure pages and unbuilt sector
   pages into the index on the day the switch is thrown. It does not:

   - **Measure pages carry `DEMOTED` until their lead blocks land.** They
     qualify by kind and they keep the exit the rule gives them — they return to
     indexable by rendering a lead block, which is the pre-launch item in §5,
     and nobody re-opens the question to let them. What the clause did not
     anticipate is the size of the class: 480-odd pages, each a decoded
     provision beside its verbatim source, opening the index with the evidence
     under the product rather than the product.
   - **A sector page without its dataset carries `DEMOTED` too.** Indexability
     follows the lead block, and a sector that has no transition data renders
     the directory template, which has none. It arrives in the index by having
     its data built — `web/lib/siteRoutes.ts` reads the same condition the
     sector route branches on — so steel needs no edit here, only a dataset.

   Project pages are untouched by this and stay indexable on the build-gap
   clause: eight substantive object pages is the case the clause was written
   for.

   **`/coverage` is not demoted.** §0.8 listed it with the browse surfaces as a
   thin list page. Brief 4 §1 made it the page that states the perimeter — what
   Eufabric covers, what it does not, and why — and the front-page tiles for the
   five industries without a page of their own open it. It is a destination.

   **A published route list, and a disallowed one.** `sitemap.xml` carries the
   indexable routes and nothing else; `robots.txt`, once launched, allows
   everything and disallows the demoted routes. The two are one classification
   in `web/lib/routes.ts` rendered twice, and `web/lib/launch.test.mts` fails
   the build if a route appears in both. Note what disallowing a demoted route
   costs: a page that is not fetched is a page whose `follow: true` is never
   read, so the crawl-through this rule describes is carried by the links on
   indexable pages rather than by the demoted pages themselves.

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

**Ecosystem tiles.** Six tiles. **Superseded twice since this was written:**
§4.2 settles the instances — cement, steel, chemicals, batteries, hydrogen,
circular-materials, with carbon capture a technology rather than an ecosystem —
and brief 4 §3 rules the count line off the tile face. No tile carries a number
of any kind: the six are at six different depths of build, and a count on each
would invite a comparison about the state of our data rather than about the
industries. What each ecosystem contains is stated on the coverage page and in
the tile's hover text, in its reviewed description (§4.2).

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

2. **Ecosystem node kind.** **This section supersedes its own first statement
   of the six instances and of carbon capture's place among them; where an
   earlier reading of §1 or §4.2 disagrees with what follows, what follows is
   the ruling.**

   Six instances: `cement`, `steel`, `chemicals`, `batteries`, `hydrogen`,
   `circular-materials`. They are the front of the platform — the front page
   and `/sectors` render these and nothing else (brief 4 §§1, 3, 4).

   **Carbon capture is not an instance.** It is a technology node, with edges
   from cement, steel and chemicals — the industries that deploy it — and the
   CO2 transport and storage projects that serve them (Northern Lights,
   Porthos, Greensand) are shared project nodes reachable from each. It was
   listed as an ecosystem when the six were first written down, and it is the
   one entry on that list that is not an industry: it is an abatement route
   several industries take, and an ecosystem tile for it would have put a
   technology beside five sectors and invited the reader to compare them.

   Why a node kind and not six sector keys. The sector spine in
   `data/sectors.json` is keyed on FIGARO industries because the input-output
   joins depend on that keying. Hydrogen and circular materials are not FIGARO
   industries; adding pseudo-keys for them would corrupt the join. So the
   ecosystem sits above the spine and points into it.

   **Sector edges, instance by instance.** The mapping is not one-to-one for
   half of them, which is the whole reason the node kind exists:

   | Instance | Sector edges |
   |---|---|
   | `cement` | `cement` |
   | `steel` | `steel` |
   | `chemicals` | `chem` and `chem/plastics` (FIGARO C20 and C22). Fertilisers are excluded; ammonia is read under `hydrogen` |
   | `batteries` | `batsol`, **scoped to batteries only**. Solar stays in the register and carries no ecosystem edge |
   | `hydrogen` | none. Production, including ammonia and the fertiliser line |
   | `circular-materials` | none. The recovery industry: battery recycling, chemical and mechanical plastics recycling, scrap processing, critical raw material recovery |

   The two without a sector key are defined by their edges to technologies,
   projects, measures and materials. That is not a lesser definition — it is the
   definition the node kind was introduced for, and the reason a sector key
   could not have carried them.

   `batsol` is the sharp case. The slug covers batteries *and* solar because
   FIGARO does; the ecosystem instance covers batteries. A scoped edge says so
   in the data rather than leaving a reader of the tile to assume the sector
   page behind it is about the same thing.

   **The boundary rule, as a gate.** A project belongs to the ecosystem whose
   product it makes. A recycling plant is `circular-materials`. A
   recycled-content obligation on a producing sector stays in that sector, with
   an edge to `circular-materials`. Two ecosystem edges on one project fail the
   build unless the project is flagged shared — which is what a CO2 store or a
   hydrogen pipeline serving three industries is, and what a plant making one
   product is not.

   **Rendering rule.** Where an ecosystem maps 1:1 to a sector that has been
   built, the tile opens that sector page directly. Where it is cross-cutting
   (`hydrogen`, `circular-materials`), the same sector template renders with the
   query scoped by the ecosystem's edges instead of by a sector key, with the
   lead block and the `sector_context` slot empty until there is data to fill
   them. One template, learned once, either way.

   Until an instance has data behind it — a cross-cutting one with no edges, or
   a 1:1 one whose sector still renders the directory template — **the tile
   opens `/coverage`**, which states what is covered and what is not. This
   reconciles the rule above with brief 4 §3: a tile never opens a page with
   nothing on it, and an instance arrives at its own page by having a dataset,
   not by an edit here.

   **Each instance carries a reviewed two-sentence description** in
   `data/prose.json` — what the ecosystem contains and where its boundary runs.
   It renders on the coverage page and as the tile's hover text. **Never on the
   tile face:** the tile carries the name and the icon, and a paragraph on it
   would be the perimeter argument competing with the six names it exists to
   present.

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

6. **Funding status groups honoured by every sum.** The attribute exists and is
   richer than an earlier draft of this section assumed: `status` on every
   funding node, required by the gate, from the vocabulary `announced |
   approved | signed | disbursed | withdrawn` (`sources/sector_map.py`).

   What the totals must do with it, stated once and read by both the Python and
   the app:

   - **Committed** — `approved`, `signed`, `disbursed`. This and nothing else is
     what a figure labelled awarded may contain.
   - **Announced** — `announced`, alone. Its own figure, never folded into the
     committed one.
   - **Withdrawn** — `withdrawn`. In no total, and named where it is left out
     rather than dropped silently.

   This supersedes `awarded | announced` as this section first stated it. The
   schema already carried the finer distinction, and adding a two-value
   attribute beside it would have created a second source of truth for the same
   fact — so the specification defers to the repository on what exists. Recorded
   here so the next reader sees a decision rather than suspects drift.

7. **Downstream reach channel** from the Eurostat input-output data, required
   before the supply-chain section exists (§2, excluded item).

## 5. Build order

0. **The `sector-map` merge.** Not a build step, but everything below waits on
   it: the transition layer — `data/transition/`, the funding node, the sector
   template — exists only on that branch. `main` has no transition layer at all,
   so step 1 has nothing to act on until it lands. That puts the `sector-map`
   review at the front of this queue.
1. Funding status groups honoured by every sum (§4.6). Smallest, gates every sum
   on all three page types. Depends on step 0.
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
there becomes vestigial rather than a standing exemption. Since the index
opening this item has a second consequence, stated in §0.8: the measure lead
block is what returns measure pages to the index. They are demoted until it
lands, and they return by rendering it. Sequenced against the
flag, not against any merge — the global noindex means the clause does no work
until then, and nothing in the eight steps above waits on it.

The launch gate is unchanged. `web/lib/launch.ts` stays closed by default and
nothing in this specification touches it; every surface here ships noindex until
`SITE_LAUNCHED` is set out loud.

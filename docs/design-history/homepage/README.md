> **Superseded.** This is the 13 August 2026 handoff for the pre-Next.js static
> site, kept for its component and token specifications. Amendment brief 2 §6
> (photography, and the turned-up Swiss direction) and brief 3 (the eufabric
> logo and identity) overrule it wherever they disagree — most of all on assets,
> where this document bans images outright. Nothing structural is taken from it.

# Handoff: PolicyFocus Homepage

## Overview
The public homepage / "intelligence terminal" front page for **PolicyFocus** — a European policy-intelligence platform that translates EU legislation into structured intelligence on who is affected, whether a file adds or removes a duty, and the economic incidence. The homepage sits on top of the existing Obligation Register instrument (`index.html` + `styles.css` in the repo) and links into it. It demonstrates the product rather than marketing it: a live signals stream, the "who carries the burden" ledger, a sector index, strategic priorities, and analysis.

Repo: `cartmangreko/policyfocus` (branch `main`). This homepage is **new** — it does not exist in the repo yet. It was built to match the repo's established design system verbatim.

## About the Design Files
The file in this bundle (`PolicyFocus Homepage.dc.html`) is a **design reference created in HTML** — a prototype showing intended look and behavior, not production code to copy directly. It was authored as a streaming "Design Component" so it carries some non-standard tags (`<sc-if>`, `{{ }}` holes, an `x-dc` runtime); **ignore those** and read it for layout, structure, copy, and exact style values.

The task is to **recreate this homepage in the repo's existing environment**: static HTML pages styled by the shared `styles.css`, with vanilla JS for interaction — exactly how `index.html` is built. Reuse the existing CSS tokens and component classes in `styles.css` rather than the inline styles in the prototype (the prototype inlines everything only because of its authoring constraints). Where a class already exists (`.masthead`, `.sec`, `.ledger`/`.led-*`, `.strip`, `.item`, `.eyebrow`, `.mono`), use it.

## Fidelity
**High-fidelity.** Final colors, typography, spacing, and interactions. Recreate pixel-accurately using the repo's `styles.css` tokens. The one deliberate departure from `styles.css`: the homepage background is pure white (`#ffffff`), not the register's `--paper` (`#f4f4f1`); `--paper` is retained only for inset panels (the ledger card wells, the source block, the diff panes, and the "who carries the burden" section band).

## Screens / Views

The prototype is a single page with an internal router (`state.route`) covering three views. In the real site these should be **separate, indexable, SEO-friendly pages/routes** (see SEO note): `/` (home), `/measures/<id>` (measure detail), `/sectors/<slug>` (sector detail). The header and footer are shared chrome across all three.

### 1. Shared chrome — Top bar, ticker, header, footer
- **Claret rule**: a 3px `#7a2e3f` bar spanning the very top of the page (the brand signature, mirrors `.masthead` `border-top`).
- **Ticker** (optional; toggle default on): 34px tall, `#fbfbf9` ground, `border-bottom:1px #e0e2dc`. Left cell: white, right border `#e0e2dc`, a 7px claret dot + `LIVE` in mono uppercase 10.5px. Right of it: a horizontally scrolling marquee of headlines in IBM Plex Mono 11px `#5a5f68`, with `▸ RELIEF` in pine and `▸ BURDEN` in claret. Animation: `translateX(0 → -50%)` over 46s linear infinite; content is duplicated once for a seamless loop.
- **Header**: sticky, `top:0`, `z-index:50`, background `rgba(255,255,255,.94)` + `backdrop-filter: saturate(180%) blur(8px)`, `border-bottom:1px #cdd0ca`, height 62px, inner max-width 1200px, padding `0 32px`, flex space-between.
  - **Logomark**: four thin vertical bars, 3px wide, `gap:2px`, bottom-aligned, heights `10/17/13/17`px, colors `#1f5c55` (pine), `#14171c`, `#14171c`, `#7a2e3f` (claret). Echoes the burden strip + ledger. On the dark footer the two ink bars become `#f4f4f1` and `#868b93`, and claret lightens to `#a5495e`.
  - **Wordmark**: `PolicyFocus` in **IBM Plex Mono**, 15px, `letter-spacing:.02em`, uppercase. "Policy" weight 500 `#868b93`; "Focus" weight 600 `#14171c` (white in footer). Clicking it → home.
  - **Nav** (13.5px, weight 500, `#5a5f68`, gap 26px, hover `#14171c`): Topics · Measures · Sectors · Companies · Analysis · Data. Measures → measure route; Sectors → sector route.
  - **Right**: a search affordance (bordered 6px-radius box, `#cdd0ca` border, mono placeholder "⌕ Search" + a `/` keycap in a `#e0e2dc` bordered chip) and a "Sign in" text button.
- **Footer**: `#14171c` ground, text `#b6bab4`, padding `56px 0 40px`, inner max-width 1200px. 4-col grid `2fr 1fr 1fr 1fr`, divider `1px #2b2f36`. Col 1: logomark + wordmark, then the statement **"The intelligence layer between European policy and the real economy."** in Archivo 600, 1.2rem, `#fff`, max-width 24ch. Cols 2–4: Product / Method / About link lists (mono uppercase 10.5px `#5a5f68` headers; 13px items, hover `#fff`). Bottom line, mono 11px `#5a5f68`: "Prototype. All counts computed from the register, not entered by hand."

### 2. Home view
Sections top to bottom, each a full-width band; inner content max-width 1200px, padding `0 32px`; section vertical padding 56px unless noted; dividers `1px #cdd0ca`.

- **Hero** (padding `64px 0 44px`):
  - Eyebrow (mono 11px, `letter-spacing:.16em`, uppercase, `#868b93`): "European policy intelligence · Economic impact".
  - H1: Archivo 900, `letter-spacing:-.035em`, `line-height:1.02`, `font-size:clamp(2.6rem,6vw,4.5rem)`, max-width 17ch, `text-wrap:balance` — **"European policy, decoded into economic impact."**
  - Standfirst: Archivo 600, `#3f444c`, `clamp(1.05rem,1.7vw,1.35rem)`, `line-height:1.32`, max-width 54ch — **"PolicyFocus turns complex European policy and regulation into structured intelligence on sectors, companies, markets, investment and strategic priorities."**
  - **Search bar**: max-width 820px, `border:1.5px solid #14171c`, radius 8px, white. A `⌕` glyph (`#868b93`, 19px), a borderless text input (Public Sans 16px, placeholder "Search European policy, sectors, companies or measures", padding `18px 8px 18px 0`), and a submit button: full-height, `border-left:1.5px #14171c`, `#14171c` ground, white mono 12px uppercase `letter-spacing:.08em` "Search ⏎", hover ground → `#7a2e3f`.
  - **Example queries** (optional; toggle default on): three chips, `border:1px #e0e2dc`, radius 5px, padding `8px 12px`, 13px `#3f444c`, each led by a claret mono "→". Hover: border `#868b93`, text `#14171c`. Copy: "What EU policies affect battery manufacturers?", "Where is Europe reducing the reporting burden?", "Which sectors face the greatest regulatory pressure?"
  - Entering animation: `rise` (opacity 0→1, translateY 8px→0) 0.4s `cubic-bezier(.2,.7,.3,1)`.
- **Stats strip** (bordered top+bottom `#cdd0ca`): 4-col grid, inner column dividers `1px #e0e2dc`, each cell padding 28px. Number: Archivo 900, 2.4rem, `letter-spacing:-.03em`, tabular-nums. Label: mono 11px `letter-spacing:.1em` uppercase `#868b93`. Values: **40** Duties in the register · **14** Sectors mapped · **4** Who-is-affected classes · **100%** Rows source-checked.
- **Policy Signals**: header row = eyebrow "Policy signals" + H2 (Archivo 800, 1.65rem, `-.02em`) "What changed, and who now carries it" + a right-aligned mono claret link "Open the full register →". Intro note (13.5px `#5a5f68`, max 64ch). Then a list of **signal rows** — this is the register-row component (`.item`/`.item-btn` in `styles.css`):
  - Grid `64px 1fr 208px`, gap 20px, align-items start, padding `20px 12px`, `border-top:1px #e0e2dc` (last row also bottom border). Cursor pointer; hover background `#f7f8f5`. Whole row → measure route.
  - Col 1: duty id, mono 11.5px `#868b93`.
  - Col 2: duty statement (Public Sans 15.5px, weight 450, `line-height:1.45`); addressee + class (12px `#5a5f68`, 6px top margin); meta line (mono 10.5px, `letter-spacing:.03em`, uppercase, `#868b93`, 8px top): article · directive · nature · timing.
  - Col 3 (right-aligned, gap 11px): a weight tag then the 7-mark strip. Tag: mono 10px uppercase, radius 2px, padding `4px 7px`. Relief/removed → background `#d4e2df`, text `#1f5c55`. Burden/added → background `#ecdadd`, text `#7a2e3f`. **Strip** (the `.strip` signature): 7 bars, each 7px×14px, `gap:2px`, radius .5px; off = `#e0e2dc`; on = `#14171c` for added rows, `#1f5c55` for removed rows. On-marks correspond to the row's burden drivers (D1–D7, left to right).
  - The six seeded rows (all from `data/omnibus.json`): **RPT-01** Relief, driver D5; **DD-05** Burden, D1; **RPT-09** Relief, none; **TAX-01** Relief, none; **DD-02** Burden, none; **STD-01** Burden, D1. (Copy verbatim in the HTML.) In production these should render from the register data, not be hardcoded.
- **Who carries the burden** (section band background `#f4f4f1`, bordered top+bottom): eyebrow + H2 "Duties added and removed, by who has to carry them" + note. Two-column grid `1.7fr 1fr`, gap 40px:
  - **Ledger card** (white, `border:1px #e0e2dc`, radius 8px, padding `26px 24px`): the diverging-bar chart (`.ledger`/`.led-*`). Each class row: grid `11rem 1fr`; a centered vertical axis (`1px #cdd0ca`); pine bar grows **left** from center (removed), claret bar grows **right** (added); bar height 16px, count label in mono 11px white inside the bar. Widths are `count / max * 50%` of the track (max = 12). Rows: Businesses 12 removed / 6 added; European Commission 3 / 2; Governments 0 / 2; Foreign investors 2 / 0. Legend below: 10px squares, claret "Duties added or widened", pine "Duties removed, merged or waived".
  - **Burden-driver frequency** (optional; toggle default on) card: a 7-bar column chart, bars `#14171c`, area height 120px, `border-bottom:1px #cdd0ca`, count above each bar (mono 10px `#868b93`), D1–D7 labels below. Heights are `count/9`: D1 9, D2 4, D3 2, D4 1, D5 7, D6 3, D7 2.
- **Explore by sector**: eyebrow + H2 "Which industries the corpus touches" + note. Grid `repeat(auto-fill,minmax(210px,1fr))`, `gap:1px`, on a `#e0e2dc` background with `1px #e0e2dc` outer border so cells read as a hairline grid (Swiss). Each cell: white, padding 18px, flex space-between baseline; sector name (14px weight 500) + count (mono 11px `#868b93`); hover background `#f4f4f1`; → sector route. 14 sectors with counts (Automotive 10, Chemicals & refining 12, Power & heat 11, Steel 9, Construction 9, Aluminium & metals 8, Batteries & solar 8, Cement & concrete 7, Wind/heat pumps & H₂ 7, Glass/ceramics & paper 6, Shipping 6, Waste & landfill 5, Aviation 5, Carbon capture & fuels 4). Sector slugs live in `index.html`'s `SECTORS` map — reuse them.
- **Strategic priorities**: eyebrow + H2 "What the agenda is advancing". A bordered list, rows grid `1fr auto`, padding `20px 8px`, `border-bottom:1px #e0e2dc`, hover `#f7f8f5`. Each: title (Archivo 700, 1.15rem) + one-line description (13px `#5a5f68`) and a right mono count (12px `#868b93`). Items: Competitiveness & simplification (21), Corporate accountability (11), Sustainable finance (8), Strategic autonomy (6).
- **Analysis**: header row (eyebrow + H2 "Reading the change" + "All analysis →"). 3-col card grid, `gap:1px` on `#e0e2dc` hairline background. Each card: white, padding `26px 22px 30px`, hover `#f7f8f5`; kicker (mono 10.5px uppercase claret), H3 (Archivo 700, 1.15rem, `line-height:1.22`), dek (13.5px `#5a5f68`), meta (mono 11px `#868b93`, "6 min · Aug 2026"). Titles are in the HTML.

### 3. Measure detail view (route: measure; seeded with duty **RPT-09**)
- Back link "← Back to signals" (mono claret) + breadcrumb "Measures / Reporting & Taxonomy".
- A weight tag ("Relief · removed · RPT-09"), then H1 (Archivo 900, `clamp(1.9rem,3.8vw,2.7rem)`, max 22ch): "Third-country group reporting threshold raised to €450 million".
- Meta row (mono 11.5px): Institution / File / Article / Status, labels in `#868b93`, values `#5a5f68`.
- Two-column body grid `1fr 320px`, gap 48px:
  - **Main**: sections each led by a mono uppercase label with a `1px #cdd0ca` underline. *What changes* (two paragraphs, 15.5px `#3f444c`, `line-height:1.6`). *Prior rule vs new rule* — two panes side by side: prior on `#f4f4f1` `1px #e0e2dc`, new on white `1px #cdd0ca` (mirrors `.diff`/`.diff-pane` in `styles.css`). *Who is affected* — 2×2 grid of label/value pairs. *Economic incidence* — two columns, Benefits (pine dot + bulleted list) and Costs (claret dot + list). *Source text* — the provenance block: `#f4f4f1`, `border-left:2px #b6bab4`, mono 12.5px verbatim quote + a "View source →" link (`#1f4f8f`) to the EUR-Lex URL (mirrors `.source`). *Timeline* — 4 nodes on a horizontal `1px #cdd0ca` line: Proposal (FEB 2025, pine dot) → Adopted (FEB 2026, pine) → Transposition (+12 months, hollow claret ring = current) → Application (hollow grey ring).
  - **Rail** (sticky, `top:88px`, `border:1px #e0e2dc`, radius 8px): a Weight header well (`#f4f4f1`) with "Relief" in Archivo 800 1.4rem pine; a "Key facts" definition grid (Nature Exemption / Direction Removed / Frequency Annual (removed) / Verification None / Drivers None recorded); a "Related measures" list linking RPT-01 and TAX-01.
- All values from `data/omnibus.json` row `RPT-09`.

### 4. Sector detail view (route: sector; seeded with **Automotive**)
- Back link "← Home" + breadcrumb "Sectors / Automotive". H1 "European Automotive" (Archivo 900, `clamp(2.2rem,4.5vw,3.2rem)`). Intro (15px `#3f444c`, max 62ch) with an explicit "Figures are illustrative across the corpus" caveat.
- Stats strip (4 cols, bordered): Duties reaching sector 10 / Added·burden 4 (claret) / Removed·relief 6 (pine) / Companies tracked 31.
- Pressure vs support: two cards (`1px #e0e2dc`, radius 8px). Regulatory pressure "Moderate" (claret), a `#f4f4f1` track with a 64% claret fill. Policy support "Elevated" (pine), 78% pine fill.
- Key measures: 3 register rows (grid `64px 1fr auto`), each → measure route, with a Burden/Relief tag.
- Bottom grid `1.4fr 1fr`: **Policy trajectory** inline SVG (viewBox `0 0 640 220`) — two 2px polylines, claret = duties added, pine = duties removed, over 2023–2026, thin `#e0e2dc` gridlines + a `#cdd0ca` baseline, end-point dots. **Companies · exposure** table (Company A–D with N direct / N indirect in mono) and a **Related sectors** chip row (Batteries & solar, Steel, Aluminium & metals, Chemicals & refining).

## Interactions & Behavior
- **Navigation**: prototype uses a JS router (`state.route ∈ {home, measure, sector}`); nav clicks and card/row clicks call `go(route)` which sets state and scrolls to top. In production, make these real routed pages (see SEO). Every signal row, sector cell, strategic-priority row, analysis card, and related-measure link is a navigation target.
- **Ticker**: CSS marquee, `translateX(0 → -50%)`, 46s linear infinite; duplicate the content once for a seamless loop. Respect `prefers-reduced-motion` (the existing `styles.css` already disables animations under that query — keep it).
- **View entrance**: `@keyframes rise` (opacity + 8px translateY), ~0.35–0.4s `cubic-bezier(.2,.7,.3,1)`.
- **Hover states**: rows/cards → background `#f7f8f5` or `#f4f4f1`; nav/links → darken to `#14171c` or `#fff` (footer); search submit → ground `#7a2e3f`; example/related chips → border `#868b93`. The burden strip's on-marks shift to claret on row hover in `styles.css` (`.item-btn:hover .strip i.on`) — preserve that.
- **Header**: sticky with translucent blur; stays above the ticker (which scrolls away).
- **Search**: non-functional in the prototype. Intended behavior per brief: fast, full-text + AI-assisted natural-language search across measures, sectors, companies, topics, strategic priorities — but presented as a search instrument, **not** a chatbot.

## State Management
- `route` — which view is shown (home | measure | sector). In production, this is the URL/router.
- Three homepage display toggles exposed as props in the prototype (defaults in parens): `tickerEnabled` (true), `showExampleQueries` (true), `showLedgerDrivers` (true). These are presentation flags, optional to carry over.
- **Data**: signals, ledger counts, driver frequencies, sector counts, measure detail, and sector detail should all be **computed from the register data at load** (per the repo brief: "Counts on the page must be computed from the register, never hardcoded"). The prototype hardcodes them for illustration; wire them to `data/omnibus.json` (and future `data/<file>.json`) in the real build.

## Design Tokens
All tokens already exist in the repo's `styles.css` `:root` — use those variables, do not re-declare. Key values:
- **Ink**: `--ink #14171c`, `--ink-70 #3f444c`, `--ink-55 #5a5f68`, `--ink-40 #868b93`, `--ink-25 #b6bab4`.
- **Grounds**: white `#ffffff` (homepage default), `--paper #f4f4f1` (inset wells/bands), `--paper-2 #e6e8e2`, `--card #ffffff`, `--card-hover #f7f8f5`.
- **Rules**: `--rule #cdd0ca`, `--rule-soft #e0e2dc`; footer divider `#2b2f36` (not a token — add or inline).
- **Signal / semantic**: `--claret #7a2e3f` (added / burden / accent), `--claret-soft #ecdadd`; `--pine #1f5c55` (removed / relief), `--pine-soft #d4e2df`; `--ochre #a8781a` (settled-later flag); `--focus #1f4f8f` (source links / focus ring). Footer logomark claret variant `#a5495e`.
- **Type families**: `--display 'Archivo'` (headings/wordmark-alt), `--sans 'Public Sans'` (body), `--mono 'IBM Plex Mono'` (eyebrows, metadata, ids, counts, wordmark). Loaded from Google Fonts (weights: Archivo 600–900, Public Sans 400–600, IBM Plex Mono 400–600).
- **Type scale (as used)**: H1 hero `clamp(2.6rem,6vw,4.5rem)`/900/`-.035em`; section H2 1.65rem/800/`-.02em`; card/priority title 1.15rem/700; body 15–15.5px/1.55–1.6; eyebrow mono 11px/`.16em`/uppercase; metadata mono 10.5–11.5px; stat numbers 2–2.4rem/900/`-.03em`, tabular-nums.
- **Radii**: 8px (cards, search bar), 6px (search chip, diff panes), 5px (query/sector chips), 2px (tags, source block), .5px (strip bars), 3px (keycap). The wordmark logomark bars are square (no radius).
- **Shadows**: minimal, per `styles.css` (`.led-file`, `.reg`, `.sec:hover` use subtle `box-shadow` — reuse those; the homepage otherwise relies on hairlines, not shadows).
- **Motion**: `--dur .45s`, `--ease cubic-bezier(.2,.7,.3,1)`; ticker 46s linear.

## SEO (from the product brief — important)
Every object gets its own indexable, server-renderable page: policy, measure, sector, company, topic, strategic priority, analysis. The homepage's routed views (measure, sector) must become real URLs with proper `<title>`/meta, not client-only state. Architecture must scale to thousands+ of pages on the same design language.

## Assets
No image or icon assets. Everything is type, CSS, and one inline SVG (the sector trajectory line chart). The `⌕`, `→`, `⏎`, `▸` are Unicode glyphs. The logomark is CSS boxes. Fonts are Google Fonts (already imported in `styles.css`).

## Files
- `design_handoff_homepage/PolicyFocus Homepage.dc.html` — the homepage design reference (this bundle). Contains the home, measure, and sector views. Read for structure/values; do not ship as-is.
- In the repo (reference these directly):
  - `styles.css` — **the design system. Reuse its tokens and component classes.** Do not restyle.
  - `index.html` — the existing Obligation Register; the markup contract, sector/class/driver vocabularies (`SECTORS`, `CLASSES`, `D`), and the pattern the homepage should follow.
  - `data/omnibus.json` — the real register data all counts and detail content should derive from.
  - `policyfocus-claude-code-brief.md` — the data-model brief (schema, drivers, named-vs-reached rule).

# PolicyFocus: wiring the supply-chain / country-exposure panel into sector pages

## Purpose

Each sector page currently renders measures from `data/<slug>.json`. This brief adds a second, separate panel on the same page: the sector's supply-chain and country exposure, read from a new file `data/exposure/<slug>.json`. The panel answers three questions for a sector: what it buys, what it sells, and how import-dependent it is and on which countries.

This is a read-only, statically generated addition. It does not touch the measures data, the valence logic, or the extraction pipeline. Keep it a separate concern: a new data file, a new component, one import on the existing sector page.

## Scope

- Do NOT compute or display any euro figures. The data is structural (shares and dependency percentages) by design.
- Do NOT merge the exposure JSON into the measures JSON. Separate files, separate component.
- Do NOT rescale or recompute shares. They are already final; render them as given.
- Do NOT fetch at runtime. Import the JSON at build time like the measures data.

## The data

### Location and coverage

One file per sector at `data/exposure/<slug>.json`, plus `data/exposure/_manifest.json` (a slug index with EU import-dependency, for listings). Eleven sectors have a file:

`steel, alu, cement, glass, chem, power, waste, ship, air, auto, build`

Slugs not in this list (for example `omnibus`) have no exposure file. The panel must be hidden when the file is absent, not error.

### Source line to display

Source: Eurostat FIGARO 2026 edition, 2024 reference year (EU inter-country input-output tables, industry by industry). Show this once, near the panel, as the provenance line.

### Schema

```
{
  "slug": "cement",
  "figaro_code": "C23",
  "figaro_label": "cement, glass & ceramics",
  "shares_basis": "percent of sector's total inputs (suppliers) / total output (customers); OTHER row carries the remainder to 100",
  "note": "FIGARO groups cement & glass under one code (C23); these share a profile in this data source.",  // or null
  "eu": <VIEW>,
  "by_country": { "AT": <VIEW>, "BE": <VIEW>, ... 27 EU members ... }
}
```

A `<VIEW>` is:

```
{
  "import_dependency_pct": 12.8,          // share of this sector's inputs bought from outside the home area
  "suppliers":  [ <ROW>, ... , OTHER ],   // industries this sector buys from
  "customers":  [ <ROW>, ... , OTHER ],   // industries that buy from this sector
  "foreign_input_origins": [ <ROW>, ... ] // countries the imported inputs come from
}
```

A `<ROW>` is `{ "code": "G46", "label": "wholesale trade", "share": 10.5 }`.

Rules the renderer must respect:

- `share` is a percentage of the sector's true total (total inputs for `suppliers`, total output for `customers`, total foreign inputs for `foreign_input_origins`). Lists do not need summing logic; the numbers are final.
- `suppliers` and `customers` end with a row whose `code` is `OTHER` and `label` is `everything else`. It carries the remainder to 100. Render it as the last row, visually lighter than the named rows. Do not drop it and do not treat it as a real industry link.
- `foreign_input_origins` may include a row labelled `rest of world` (this is an aggregate of countries outside the FIGARO set, code `FIGW1` or `W2`). Keep it. It is often the largest single origin; that is expected and correct.
- `import_dependency_pct` can be higher in a single-country view than in the EU view, because other EU countries count as foreign to one member but as home to the EU as a whole. This is the intended behaviour, not a bug.

## Rendering

### Default and country switch

- Default the panel to the `eu` view. This matches the EU-default, country-as-filter decision.
- Provide a country selector (the 27 keys of `by_country`, plus an "EU" option that returns to `eu`). Selecting a country swaps the active view to `by_country[CC]`.
- Because step one is static and read-only, the selector can be a client component that holds only the selected-country string in state and reads from the already-imported JSON. No data fetching. If you prefer to keep the page fully server-rendered for now, ship the `eu` view only and add the selector in a later step; either is acceptable, but wire the data so the country views are present in the payload.

### Layout

Three blocks, in this order, each a simple labelled list:

1. Inputs come from (`suppliers`) with a heading like "What this sector buys".
2. Goods go to (`customers`) with a heading like "Who buys from this sector".
3. Import exposure: show `import_dependency_pct` as the headline number ("X% of inputs come from abroad"), then `foreign_input_origins` as the list beneath it.

Each list row shows the `label` and the `share` as a percent. The `OTHER` row renders as "everything else" at the foot of the suppliers and customers lists.

### The shared-code note

When `note` is non-null, display it near the panel heading (for example under the sector title as a small caption). It applies to the two shared pairs: cement and glass both map to `C23`, steel and aluminium both map to `C24`. The two members of each pair carry identical figures. Surfacing the note keeps that honest rather than looking like two independent findings.

### Absent file

If `data/exposure/<slug>.json` does not exist, render the rest of the sector page normally and omit the panel. No placeholder, no error.

## Suggested placement (adapt to the actual tree)

- Data: `data/exposure/*.json` (delivered).
- A small loader in `web/lib/` (for example `exposure.ts`) exporting a typed `getExposure(slug)` that returns the parsed object or `null`, plus the `Exposure`, `ExposureView`, and `ExposureRow` types mirroring the schema above.
- A component in the web app's components directory (for example `SectorExposure`) that takes the `Exposure` object and renders the three blocks and the selector.
- Import and render it on the existing sector page alongside the measures, guarded by a null check.

## Acceptance checks

- Cement page, EU view: suppliers led by wholesale trade (~10.5%) and mining (~8.7%); customers led by construction (~55%); import dependency ~12.8%; an "everything else" row closes each of the first two lists.
- Cement page, switch to Greece: import dependency jumps to ~36%; Russia appears among foreign origins. Switch to Germany: dependency ~15%; origins are mostly EU neighbours.
- Glass page matches cement exactly, and the shared-code note is visible on both. Same for steel and aluminium.
- A slug with no exposure file renders with no panel and no error.
- No euro values anywhere. Shares render as given, with no client-side recomputation.

## What this is not (deferred, do not build now)

- No euro-denominated impact or multiplier maths.
- No named-company data.
- No writing back into the measures files or the valence layer.

# PolicyFocus — build brief for Claude Code

## What this is
PolicyFocus is an open-access site that tracks EU legislative and policy proposals
affecting **industry, trade and markets**, and translates each one into **who is
affected and how** — which sectors, companies and countries, through what
mechanism, and whether the file adds a duty or removes one. It is a reference
instrument, not a news tracker. Its credibility rests on provenance: every claim
is checkable against the source text.

This brief covers ONE job: run a single legislative file through an
extract-and-validate pipeline, produce the register rows in the schema below,
and surface how much manual correction it needs. This is a measurement. Do not
build hosting, auth, or a database. Local files only.

## The measurement that matters
At the end, report two numbers:
1. How many rows came out wrong or missing (against my judgement of the file).
2. How much of the output I had to fix by hand, including assigning indirect sectors.
Everything else in the pipeline should be automatic. The point is to learn the
per-file human cost, because that decides whether this scales.

---

## Pipeline stages
1. **Fetch** the file's full text (I will provide it as a local file — do not
   assume network access to EUR-Lex works; if a URL fetch fails, use the local copy).
2. **Extract** every distinct reporting/compliance duty into the schema below,
   one record per duty. One article can yield several duties; one duty can span
   several articles.
3. **Validate** mechanically (see checks below). Reject/flag any row that fails.
4. **Write** the rows to `data/<fileslug>.json`.
5. **Render** into the existing page template using `styles.css` (already designed —
   do not restyle).

Run extraction **twice** with slightly different prompts and flag any row where
the two runs disagree on addressee, direction, or threshold. Disagreements are
the rows I need to look at.

---

## Schema — one record per duty
```json
{
  "id": "S-01",                        // file-letter + sequence
  "file": "cbam",                      // slug of the source file
  "duty": "Plain-language statement of what must be done, from the reader's side.",
  "addressee": "Who must act, in plain words (e.g. 'Importers of covered goods').",
  "class": "business",                 // business | state | investor | commission
  "trigger": "Threshold or condition that brings someone into scope.",
  "frequency": "annual | quarterly | one-off | per-transaction | event-driven | n/a",
  "verification": "none | self-declaration | accredited third party | competent authority",
  "direction": "add",                  // add (new/expanded duty) | rem (removed/merged/waived/relieved)
  "article": "Art. 35(1)",             // the provision reference
  "when": "Applies from 1 January 2027",// the operative date/phase, in plain words
  "source_text": "Verbatim sentence(s) from the file — the operative provision, tight.",
  "source_url": "https://eur-lex.europa.eu/...#...",  // deep link to the article if available, else file-level
  "drivers": ["D1","D2","D5"],         // burden drivers present (see below)
  "burden": "High",                    // High | Medium | Low | Relief
  "sectors_named": ["steel","cement"], // sectors the TEXT names directly
  "sectors_reached": ["build"],        // sectors reached WITHOUT being named (see rule below)
  "pending": "One line, only if the real substance sits in a delegated/implementing act not yet drafted. Else omit."
}
```

### The seven burden drivers (read off the text, do not infer)
- **D1** a new document must be produced that does not exist today
- **D2** accredited third-party verification required
- **D3** approval by an authority needed *before* proceeding
- **D4** new measurement, metering or data infrastructure required
- **D5** recurring rather than one-off
- **D6** a financial consequence is directly attached (allowances returned, bond forfeited, penalty, funding withheld)
- **D7** the entity is newly in scope of the regime *as a whole*, not just of this duty

**Burden rating** derives from drivers: High if D7, or D3+D6, or three or more
drivers. Relief for any `direction: rem` row. Medium/Low otherwise by weight.

### direction
- `add` — a new duty, an expanded one, or a newly-scoped entity.
- `rem` — a duty removed, two merged into one, a verification waived, an exemption
  created, or a relief granted. Removals matter as much as additions — capture them.

### sectors_named vs sectors_reached — the key distinction
- **sectors_named**: the file's text addresses this sector directly (names it, or
  names an activity that is unambiguously that sector).
- **sectors_reached**: the duty lands on the sector *without naming it*, through one
  of three channels only:
  - **supply chain** — the named sector supplies this one (cement → construction)
  - **procurement** — the duty falls on a public buyer, so suppliers into that
    category are reached
  - **regulatory dependency** — the file's definitions/data sit in another act this
    sector is already subject to
  Do NOT invent indirect links beyond these three channels. When unsure, leave
  `sectors_reached` empty rather than guess. (Later this becomes a shared
  sector-to-sector lookup table, built once from input-output + procurement codes,
  not judged per file. For this run, populate it directly but conservatively.)

Sector vocabulary (use these slugs): steel, cement, alu, chem, glass, power,
waste, ship, air, auto, build, batsol, clean, ccs. Add a slug only if the file
clearly needs one.

---

## Validation checks (mechanical — run these, report failures)
1. **Verbatim check**: `source_text` MUST be a literal substring of the file text.
   If it is not an exact match, the row is rejected. This is the most important
   check — it catches invented provisions.
2. **Article resolves**: the `article` reference must correspond to a provision
   that exists in the file.
3. **Date parses / phrase present**: `when` must trace to language in the text,
   not be inferred.
4. **Driver sanity**: every `rem` row is `burden: "Relief"`; every row with D7 is
   `burden: "High"`.
5. **Cross-run agreement**: flag rows where the two extraction passes disagree.

Output a short report: total duties, count by direction, count by class, and the
list of flagged rows (failed a check or disagreed across runs). Those flagged
rows are the only ones I need to review.

---

## Output format
- `data/<fileslug>.json` — the array of records.
- One page that renders them, linking `styles.css` via `<link rel="stylesheet" href="/styles.css">`.
  Do not inline styles. Match the existing markup contract:
  - wordmark: `<h1><span class="lo">Policy</span>Focus</h1>`
  - each duty row expands to show, in this order: the plain-language `duty` and
    `addressee`; a `.dl` block (file, article, when, frequency, verification, burden);
    the **`.source` block** containing `.source-label` "Source text", the verbatim
    `.source-text`, and the `.source-link` to `source_url`; the `.drv` drivers line;
    and the `.pending` flag if present.
  - the added/removed `.tag` and the seven-mark `.strip` on each row.
- Keep the three sections from the reference build: sector picker (named vs
  reached), the ledger (added/removed by class), the full register with filters.

## Rules
- No euro figures unless they are operative text in the file (a threshold, a
  penalty rate). Never an estimate.
- `source_text` verbatim and tight — the operative sentence, not the whole article.
- Interpretation (`duty`, `sectors_reached`, `burden`) is generated but is the part
  I may correct. Extraction (`article`, `source_text`, `when`, `addressee`) should
  be right off the text.
- Counts on the page must be computed from the data at load, never hardcoded.

## The file for this run
I will provide one file I know well (CBAM or the Omnibus). Extract it fully,
run the validation, render the page, and give me the report plus the flagged rows.
Then tell me: of the total duties, how many needed correction, and roughly how
long the whole review took.

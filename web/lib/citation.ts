import { allMaterials, type Source } from "./transition";

// HOW A SOURCE SAYS WHAT IT IS.
//
// A QUERY ADDRESS IS NOT A CITATION. The Sources block used to render
// `title ?? url`, and for every source that carried no title — which is every
// source attached to a parameter — that fell through to the URL. A reader got
// a 214-character Comext call with eight query parameters in it where a
// citation belongs, and no way to tell from it what had been asked of the
// dataset. The URL is the address of the evidence; it belongs in href, and only
// there.
//
// So every source renders a citation, and this module is the one place one is
// worded:
//
//   document   the title, or the descriptor the publisher field carries after
//              its em dash — "EUR-Lex — Commission Implementing Regulation (EU)
//              2026/1412, Annex" is a publisher and a citation glued together,
//              and the Sources block already splits it to make its group
//              headings. Same split, other half.
//
//   api        the dataset, and what was asked of it, read out of the query
//   dataset    string in words: flow, product, reporter, year. The fields are
//              named in the URL the call was made with, so the citation cannot
//              drift from the request that produced the figure.
//
// NOTHING FALLS BACK TO THE URL. A source that can produce no citation is a
// data error, and it fails the build (sources/check_anchor_text.py reads the
// rendered pages and fails on any anchor whose text starts with http or carries
// a query string) rather than rendering a row a reader cannot read.
//
// THE SEPARATOR IS A COMMA OR A MIDDLE DOT, NEVER AN EM DASH. The standing rule
// is in sources/scope.md under "A citation separates with a comma or a middle
// dot"; SEPARATOR below is the only place this module emits one, so the rule is
// enforced by there being one of it rather than by everybody remembering.
//
// The rule is about the separator a citation EMITS. An em dash inside a title —
// "Cement — Energy System", "Carbon sequestration and reuse — capital and
// operating cost estimates" — is how the publisher wrote it, and a citation
// quotes a title rather than editing it. Only the joins this file makes are
// this file's business.

/** Every join this module makes. A middle dot rather than an em dash: an em
 *  dash reads as a publisher's own punctuation — half the titles on the cement
 *  page contain one — so a citation that also joined with it gave a reader no
 *  way to see where the title stopped and the citation's own structure began.
 *  Clauses inside a single fact are separated with a comma; facts are separated
 *  with this. */
export const SEPARATOR = " · ";

/** Comext flow codes. 1 and 2 are the whole vocabulary. */
const FLOW: Record<string, string> = { "1": "imports", "2": "exports" };

/** The half of the publisher field after its em dash, where it carries one.
 *  "EUR-Lex — Directive 2003/87/EC, consolidated 1 March 2024, Art. 10a(1a)"
 *  is a group heading and a citation in one string; the Sources block takes the
 *  first half for its heading, and this is the second. */
function descriptor(publisher: string): string | null {
  const [, ...rest] = publisher.split("—");
  const tail = rest.join("—").trim();
  return tail || null;
}

/** A CN code as the register writes it, without its spaces: "2523 10 00" and
 *  "252310" are the same code asked for two ways, and Comext asks the second
 *  way. Compared on the first six digits, which is the subheading Comext
 *  queries at. */
function materialForCn(code: string): string | null {
  const want = code.replace(/\D/g, "").slice(0, 6);
  if (!want) return null;
  for (const m of allMaterials()) {
    const have = (m.cn_code ?? "").replace(/\D/g, "").slice(0, 6);
    if (have && have === want) return m.name.toLowerCase();
  }
  return null;
}

/** What was asked of a dataset, in words, from the query the call was made
 *  with. Every clause is conditional on its field being present: a dataset
 *  fetched without a product code says nothing about a product. */
function askedFor(url: string): string[] {
  let query: URLSearchParams;
  try {
    query = new URL(url).searchParams;
  } catch {
    return [];
  }
  const clauses: string[] = [];

  const flow = FLOW[query.get("flow") ?? ""];
  if (flow) {
    // `partner` is who the trade is with. EXT_* is the rest of the world, which
    // is what makes the flow extra-EU rather than intra.
    const partner = query.get("partner") ?? "";
    clauses.push(partner.startsWith("EXT_") ? `extra-EU ${flow}` : flow);
  }

  const product = query.get("product");
  if (product) {
    const name = materialForCn(product);
    clauses.push(`CN ${product}${name ? ` (${name})` : ""}`);
  }

  const reporter = query.get("reporter");
  // EU27_2020 is the reporter code for the Union in its post-2020 composition;
  // a reader wants the country, not the vintage of the definition.
  if (reporter) clauses.push(reporter.replace(/_\d{4}$/, ""));

  const time = query.get("time");
  if (time) clauses.push(time);

  return clauses;
}

/** The one citation for one source. Never a URL, and never empty. */
export function citation(s: Source): string {
  if (s.kind === "api" || s.kind === "dataset") {
    if (!s.dataset) {
      throw new Error(
        `${s.url} is a ${s.kind} source with no dataset block, so there is nothing to ` +
          `cite it by. A query address is not a citation`,
      );
    }
    const named = s.dataset.id ? `${s.dataset.name} ${s.dataset.id}` : s.dataset.name;
    const asked = askedFor(s.url);
    return asked.length > 0 ? `${named}${SEPARATOR}${asked.join(", ")}` : named;
  }
  const text = s.title?.trim() || descriptor(s.publisher) || s.publisher.trim();
  if (!text) {
    throw new Error(`source ${s.url} has no title, no publisher descriptor and no publisher`);
  }
  return text;
}

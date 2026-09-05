/**
 * The sitemap's origin and the route file that builds it.
 *
 *     npm test                       (from web/; also runs in prebuild)
 *
 * TWO GATES, AND THIS IS THE CHEAP HALF. What the sitemap PUBLISHES is checked
 * after the build by sources/check_sitemap.py, which reads the file the build
 * wrote and holds every URL in it against the robots tag of the page it names.
 * That is the check that matters and it needs a build to run.
 *
 * This half needs neither a build nor a bundler, and it holds the two things a
 * build would find out too late: the canonical origin, and the shape of the
 * route file that maps it over the classification. lib/siteRoutes.ts cannot be
 * imported here — it reads the register through modules with extensionless
 * specifiers, which is what the routes/siteRoutes split exists to keep out of
 * `node --test` — so the data-facing assertions live in the python gate.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { SITE_URL, classify, isDemoted } from "./routes.ts";

const HERE = new URL(".", import.meta.url).pathname;

test("the canonical origin is the apex, with no trailing slash", () => {
  // A sitemap is a list of the URLs this site asks to have indexed, and asking
  // for a URL that answers with a redirect is asking for the wrong one: the
  // crawler follows it and indexes what it lands on. One canonical host.
  assert.equal(SITE_URL, "https://eufabric.eu");
  assert.doesNotMatch(SITE_URL, /\/\/www\./, "the sitemap must not be built on www");
  assert.doesNotMatch(SITE_URL, /\/$/, "the origin must not carry a trailing slash");
});

test("a URL is the origin plus the path, and the front page is the bare origin", () => {
  const url = (path: string) => `${SITE_URL}${path === "/" ? "" : path}`;
  assert.equal(url("/"), "https://eufabric.eu");
  assert.equal(url("/coverage"), "https://eufabric.eu/coverage");
  assert.equal(url("/measures/cbam/fin-03"), "https://eufabric.eu/measures/cbam/fin-03");
});

test("the sitemap route builds from the classification and adds nothing", () => {
  // A shape assertion because the module resolves `@/lib/...` and cannot be
  // imported without the bundler. What it protects: a second source of URLs —
  // a hardcoded entry, a second origin constant, a list that forgot to ask
  // siteRoutes, or a sitemap that reached for the demoted list.
  const src = readFileSync(join(HERE, "../app/sitemap.ts"), "utf8");
  assert.match(src, /siteRoutes\(\)\.indexable/, "the sitemap must map the indexable list");
  assert.match(src, /from "@\/lib\/routes"/, "the origin must come from lib/routes");
  assert.doesNotMatch(src, /https:\/\//, "no URL may be written into the route file");
  assert.doesNotMatch(src, /\.demoted\b/, "the sitemap must never read the demoted list");
});

test("no route can be published and demoted at once, on a list of every kind", () => {
  // launch.test.mts asserts this on the two measure classes; here it is over
  // one of every route kind the classification knows, so that a new kind added
  // to `classify` without a thought about the sitemap fails here.
  const routes = classify({
    mappedSectors: ["cement", "steel"],
    unmappedSectors: ["chem/plastics", "auto"],
    projectIds: ["brevik-ccs", "stegra-boden"],
    measuresWithLead: ["/measures/cbam/fin-03", "/measures/ets/cbam-01"],
    measuresWithoutLead: ["/measures/omnibus/rpt-01"],
  });
  for (const path of routes.indexable) {
    assert.equal(isDemoted(path, routes.demoted), false, `${path} is in both lists`);
  }
  const dupes = routes.indexable.filter((p, i) => routes.indexable.indexOf(p) !== i);
  assert.deepEqual(dupes, [], `the indexable list repeats: ${dupes.join(", ")}`);
});

/**
 * The launch switch, and the route classes it opens onto.
 *
 *     npm test                       (from web/; also runs in prebuild)
 *
 * WHAT THIS PROTECTS. Three signals tell a crawler whether this site is open —
 * the X-Robots-Tag header in next.config.ts, robots.txt in app/robots.ts, and
 * the robots metadata in app/layout.tsx. The failure this file exists to
 * prevent is not any one of them being wrong; it is the three disagreeing, so
 * that a page says noindex in its head while robots.txt invites the crawler in,
 * or the site opens on a platform variable nobody meant to set.
 *
 * So the assertions are about the SHAPE of the mechanism rather than about its
 * current value: one env var decides, one module reads it, and every consumer
 * imports the answer instead of computing its own.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { classify, isDemoted, DEMOTED_PREFIXES } from "./routes.ts";

const HERE = new URL(".", import.meta.url).pathname;

/** launch.ts reads the environment when it loads, so each state needs its own
 *  module instance. The query string defeats the module cache; nothing else in
 *  the repository imports it this way, and nothing should. */
async function launchWith(env: Record<string, string | undefined>, tag: string) {
  const saved = { ...process.env };
  for (const [k, v] of Object.entries(env)) {
    if (v === undefined) delete process.env[k];
    else process.env[k] = v;
  }
  try {
    return await import(`./launch.ts?${tag}`);
  } finally {
    process.env = saved;
  }
}

const CLOSED = { SITE_LAUNCHED: undefined, VERCEL_ENV: undefined };

test("closed by default: nothing is indexable without SITE_LAUNCHED", async () => {
  const m = await launchWith(CLOSED, "closed");
  assert.equal(m.INDEXABLE, false);
  assert.deepEqual(m.SITE_ROBOTS, { index: false, follow: false });
});

test("production alone does not open the site — the variable does", async () => {
  const m = await launchWith(
    { SITE_LAUNCHED: undefined, VERCEL_ENV: "production" },
    "prod-only",
  );
  assert.equal(m.INDEXABLE, false);
});

test("SITE_LAUNCHED opens production, and only production", async () => {
  const open = await launchWith(
    { SITE_LAUNCHED: "1", VERCEL_ENV: "production" },
    "open",
  );
  assert.equal(open.INDEXABLE, true);
  assert.equal(open.SITE_ROBOTS, undefined);

  for (const env of ["preview", "development"]) {
    const m = await launchWith({ SITE_LAUNCHED: "1", VERCEL_ENV: env }, `open-${env}`);
    assert.equal(m.INDEXABLE, false, `${env} must never be indexable`);
  }
});

test("one value per state: pre-launch, a demoted page says what every page says", async () => {
  const m = await launchWith(CLOSED, "demoted-closed");
  assert.deepEqual(m.DEMOTED, m.SITE_ROBOTS);
});

test("launched, a demoted page is noindex FOLLOW and never nofollow", async () => {
  const m = await launchWith(
    { SITE_LAUNCHED: "1", VERCEL_ENV: "production" },
    "demoted-open",
  );
  assert.deepEqual(m.DEMOTED, { index: false, follow: true });
  // Said twice on purpose: `follow: false` on a demoted page would cut the
  // crawler off from the object pages the demoted list surfaces link to, which
  // is the one thing demotion is not supposed to do.
  assert.equal(m.DEMOTED.follow, true);
});

test("the switch is read in exactly one module", () => {
  // Every other file asks lib/launch.ts. A second reader of process.env is how
  // the three signals come to disagree.
  for (const file of ["../next.config.ts", "../app/robots.ts", "../app/layout.tsx"]) {
    const src = readFileSync(join(HERE, file), "utf8");
    assert.match(src, /from "(@\/lib\/launch|\.\/lib\/launch)"/, `${file} must import the switch`);
    assert.doesNotMatch(src, /process\.env/, `${file} must not read the environment itself`);
  }
});

test("no route is both published and disallowed", () => {
  const routes = classify({
    mappedSectors: ["cement"],
    unmappedSectors: ["steel", "chem/plastics"],
    projectIds: ["brevik-ccs"],
  });
  for (const path of routes.indexable) {
    assert.equal(isDemoted(path, routes.demoted), false, `${path} is in both lists`);
  }
  // The sitemap is the positive list and robots.txt the negative one; a URL in
  // both would be a site asking to be indexed and refusing to be read.
  assert.deepEqual(
    routes.indexable.filter((p) => routes.demoted.includes(p)),
    [],
  );
});

test("demotion matches on segment boundaries", () => {
  assert.equal(isDemoted("/measures", DEMOTED_PREFIXES), true);
  assert.equal(isDemoted("/measures/cbam/FIN-03", DEMOTED_PREFIXES), true);
  assert.equal(isDemoted("/measurements", DEMOTED_PREFIXES), false);
  assert.equal(isDemoted("/", DEMOTED_PREFIXES), false);
});

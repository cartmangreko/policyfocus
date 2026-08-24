// The launch switch. One boolean, read in three places: the X-Robots-Tag
// header (next.config.ts), robots.txt (app/robots.ts) and the per-page robots
// metadata (app/layout.tsx, via SITE_ROBOTS below). All three derive from here
// so the site cannot end up half-hidden — a page that says noindex in its head
// while robots.txt invites the crawler is the failure this file exists to
// prevent. The per-page override for demoted surfaces derives from it too, for
// the same reason: see DEMOTED at the foot of this file.
//
// CLOSED BY DEFAULT. The register is a work in progress with unreconciled
// files in it; being indexed before it is ready is not recoverable on the
// crawler's timetable. So indexing requires someone to say so out loud:
//
//   SITE_LAUNCHED=1   in Vercel → Settings → Environment Variables, Production
//
// It is read at build time, not at request time, because every page here is
// prerendered — flipping the switch means redeploying, which is the right
// amount of ceremony for the decision.
//
// Preview and development deployments are never indexable, whatever the
// variable says: VERCEL_ENV is set by the platform and cannot be spoofed by an
// environment variable being scoped to the wrong place, which is the most
// likely way this gets set wrong.
const LAUNCHED = ["1", "true", "yes"].includes((process.env.SITE_LAUNCHED ?? "").toLowerCase());
const ENV = process.env.VERCEL_ENV; // "production" | "preview" | "development" | undefined

export const INDEXABLE: boolean = LAUNCHED && (ENV === undefined || ENV === "production");

// THE DEMOTED SURFACES. The register is no longer the product: it is the
// candidate pool behind the sector pages. Its own surfaces — the act pages,
// the flat measure browse, the findings, the coverage page and the legislative
// change feed — keep their routes and their content, lose their links from the
// header and the home page, and carry this tag.
//
// Kept rather than deleted, deliberately. Every one of them is the evidence a
// sector page's ranking rests on, and a reader who follows a measure link into
// the register should land on something finished. What they should not be is
// the thing a search engine offers a stranger as the product.
//
// `follow: true` on purpose: the crawler should still walk through to the
// measure pages, which ARE product surfaces — the sector page links them by
// name and they carry the register's own evidence.
//
// ONE VALUE PER STATE, WHICH IS WHY THIS IS DERIVED RATHER THAN WRITTEN. Page
// metadata overrides the layout default, so a `DEMOTED` written as a flat
// constant made a demoted page emit `noindex, follow` in its head while the
// X-Robots-Tag header from next.config.ts said `noindex, nofollow` for every
// path. `noindex` held either way, so nothing was ever exposed — but the file's
// own guarantee at the top is that all three signals say the same thing from
// one source, and on `follow` they said two things from two.
//
// Pre-launch the site is closed and demotion has nothing to add: `SITE_ROBOTS`
// is what every page says, this included. Demotion is a ranking decision about
// a launched site, so it only means anything once the switch is open, and only
// then does `follow: true` differ from the default.
export const SITE_ROBOTS = INDEXABLE ? undefined : ({ index: false, follow: false } as const);

export const DEMOTED = INDEXABLE
  ? ({ index: false, follow: true } as const)
  : ({ index: false, follow: false } as const);

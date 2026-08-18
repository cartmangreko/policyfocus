// The launch switch. One boolean, read in three places: the X-Robots-Tag
// header (next.config.ts), robots.txt (app/robots.ts) and the per-page robots
// metadata (app/layout.tsx). All three derive from here so the site cannot end
// up half-hidden — a page that says noindex in its head while robots.txt
// invites the crawler is the failure this file exists to prevent.
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

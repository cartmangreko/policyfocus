# eufabric — web

The front end. A Next.js App Router site that renders the measure register,
the sector spine, the exposure layer and the findings — all of it read from
`../data` and `../sources` at build time, none of it fetched at request time.

## Running it locally

```bash
npm install
npm run dev     # http://localhost:3000
npm run build   # runs the findings gate first, then a full static build
```

`npm run build` has a `prebuild` step: `python3 ../sources/build_findings.py`.
That gate validates every hand-authored finding against the register and
rewrites `data/findings/index.json`, which is the only list of findings the
site reads. A finding that fails the gate fails the build. It needs `python3`
and nothing else — the gate is standard library only, so no pip install is
required to build the site (`sources/requirements.txt` is for the fetcher and
the watch agent, neither of which runs here).

## Deploying

The site is deployed on Vercel from this directory. Four things about that
arrangement are load-bearing, and all four are easy to break silently:

**Root Directory is `web`, and files outside it must be included.** The data
this site renders lives at the repo root — `../data`, `../sources` — and is
read with `fs` at build time (`lib/data.ts`, `lib/exposure.ts`, `lib/files.ts`,
`lib/findings.ts`). Setting a Root Directory alone does not give the build
access to its parent, so in Vercel → Settings → Build and Deployment, **Include
files outside the Root Directory in the Build Step** has to be on. With it off,
the build fails in `prebuild` on a missing `../sources/build_findings.py`.

**Every page is prerendered, and every dynamic route sets
`dynamicParams = false`.** The data is present during the build and absent from
anything Vercel runs afterwards: a deployed function has no `../data` to read.
So no route may render on demand. Each of the five dynamic routes enumerates
its paths in `generateStaticParams` and refuses the rest, which makes an
unknown slug a 404 instead of a function that crashes on a missing file. If a
route ever needs request-time data, that read has to move inside `web/` (or the
files have to be traced into the function) before the route is allowed to be
dynamic.

**The site is closed to crawlers until someone opens it.** `lib/launch.ts`
holds one boolean, and `next.config.ts` (the `X-Robots-Tag: noindex, nofollow`
header), `app/robots.ts` (robots.txt) and `app/layout.tsx` (the `robots` meta
tag) all read it, so the site cannot end up half-hidden. It is closed unless
`SITE_LAUNCHED=1` is set in Vercel → Settings → Environment Variables for
Production, and preview deployments stay closed whatever that variable says.
The switch is read at build time — every page is prerendered, so opening the
site means redeploying it.

**The build reads committed JSON, not the FIGARO flatfile.** The 65 MB
`data/flatfile_eu-ic-io_ind-by-ind_26ed_2024.zip` is an input to
`sources/build_exposure.py`, which is run by hand; the site reads only the
`data/exposure/*.json` that script commits. Nothing the site build needs is
gitignored, and a clean checkout plus `npm ci && npm run build` reproduces the
deployment.

There is no `vercel.json`: the framework preset detects Next.js, install, build
and output settings are all defaults, and the one header the site sets is set in
`next.config.ts`, where the launch switch that decides it already lives. Add one
only when a setting genuinely cannot be expressed in the project itself.

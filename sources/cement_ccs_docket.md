# Cement and CCS — the census, and where it stopped

**Brief 8, sector 2.** The procedure is hydrogen's and batteries': a recognised external
list, every entry worked to a class, a gap table that sums to the list's own entry count,
and drift measured against a second list.

**NOTHING IS CENSUSED YET.** This file exists because the pass reached the first step and
could not pass it, and a stop that leaves no record behind is a stop somebody repeats.

---

## 1. The perimeter is already written

`sources/scope.md`, "Sector perimeters", landed in pull request #59. Unchanged by this file
and restated here only so a reader of the docket is not sent looking:

- **Cement** — a capture project at a cement works, any capture technology including
  oxyfuel with capture, company-confirmed. Any other investment at a cement works is
  refused with the clause **"cement, no capture"**.
- **CCS** — CO₂ transport and storage infrastructure: stores, pipelines, shipping
  terminals, hubs. Capture at works in industries outside the four sectors is refused with
  **the industry named in the clause** — "capture, refinery", "capture, waste-to-energy" —
  rather than one clause covering all of them, because those entries are read later for the
  supplier nodes and a refusal recording only "out of perimeter" throws away the one fact
  that makes the later read possible.

## 2. What this register already holds

Eleven rows, and they are the population the gap will be measured against when a list
exists. Eight cement, three CCS:

| sector | rows |
|---|---|
| cement | brevik-ccs, gezero-geseke, anrav-devnya, go4zero-obourg, carbon2business-lagerdorf, slite-ccs, ifestos-kamari, k6-lumbres |
| ccs | northern-lights, galata-co2-storage, prinos-co2-storage |

**Four of the eight cement rows carry a stated capacity and four do not**, which is the
count `check_capacity_clause` prints beside any capacity-weighted figure. **None of the
three CCS rows carries one.**

## 3. Where it stopped, and why that is not the brief's stop clause

Both lists are behind an **affirmative acceptance**: a step where a person agrees to
something. Neither is behind a term that forbids the snapshot.

| list | role | barrier |
|---|---|---|
| IEA CCUS Projects Database | first list | **account login** — `IEA CCUS Projects Database 2026.xlsx`, updated 27/03/2026 |
| Global CCS Institute / CO2RE | second list | **click-through acceptance**, then an `app.powerbi.com` embed with no data behind it |

**The brief's stop clause is "terms that forbid the snapshot", and these terms do not.**
A hash-referenced snapshot holds an identity rather than a copy: it redistributes nothing
and needs no grant of rights, so it is permitted under the strictest reading of either
publisher's terms. What stops the pass is that passing a login or ticking an agreement
**binds the account holder**, and that is not a signature this pipeline may write.

### The routes that were tried before concluding

Recorded so nobody repeats them:

- `api.iea.org/ccus` answers **200 with 333,510 bytes** — and it is the **CCUS legal and
  regulatory database**, 89 rows keyed `Base legislation`, `Description`, `Issue`, `Link`,
  `Region`, `Regulation or law`. It is not the projects database. **A 200 is not the file
  you wanted**, and this is the second time that lesson has cost a pass an hour.
- `api.iea.org/ccus/projects`, `/ccus/project`, `/ccusprojects`, `/ccus/projects-database`
  and `/ccus-projects-database/ccus` — **404**.
- `api.iea.org/sdmx/dataflow` — **404**. `sdmx.iea.org` and `data.iea.org` — do not resolve.
- The CCUS Projects Explorer page exposes only `A17.PUBLIC_API_ENDPOINT='https://api.iea.org'`
  and no dataset path.
- `co2re.co/FacilityData` carries **no `.json`, `.csv` or `.xlsx` URL and no `/api` path**.
  Its "Terms" and "Data Use Policy" links both point at the same Terms of Use page, which
  **was** read.

## 4. The IEA describes this file two ways, and both are recorded

**A disagreement inside one publisher**, held rather than resolved, in
`sources/benchmark_snapshots.json`:

- **The product page for this very file** states `Licence CC BY 4.0`, and prints a CC BY
  citation string for it.
- **The general Terms and Conditions** exclude "Standalone datasets, data explorers and
  databases" from the CC BY 4.0 Open Use Terms.

**This register does not decide between two statements by one speaker**, and it does not
have to: a hash-referenced snapshot is permitted on either reading, and the stricter
reading is what the pass works to. The bytes stay out of the repository,
`sources/cache/ccs/` is gitignored except its index, and entries will be cited by the
publisher's own identifier.

## 5. What unblocks it

`sources/manual/MANIFEST.json`, `wanted`, three entries at `priority: blocking`, each with
the exact URL and the path the file should take. `check_manual_sources.py` prints them on
every run. Two of the three are this sector's:

| file | drop at |
|---|---|
| IEA CCUS Projects Database 2026.xlsx | `sources/cache/ccs/iea_ccus_projects_2026.xlsx` |
| CO2RE facilities export | `sources/cache/ccs/co2re_facilities.xlsx` |

**The census runs the moment they land.** Nothing else is outstanding: the perimeter is
written, the reader and its cache index exist from the batteries pass, and the class
vocabulary and the summing gate are already built and proved against three lists.

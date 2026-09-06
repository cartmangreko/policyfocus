#!/usr/bin/env python3
"""Hidden share of the two reconciled adopted-law registers (ets, cbam).

Exploratory, one-off. Reads only from data/, writes scratch/hidden_share.csv and
scratch/hidden_share.md. Nothing here feeds the site or any gate.

Hidden share of a measure: of all the exposure the measure puts on the economy
through its named sectors' input-output neighbours, how much of it lands on
sectors the measure never names.
"""

import csv
import json
import os
import statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "scratch")

FILES = ["ets", "cbam"]  # iaa is a proposal, left out
CUSTOMER_TYPES = {"obligation", "prohibition"}
SUPPLIER_TYPES = {"incentive", "right"}
REACHED_CUTOFF = 0.05

DECISIONS = []


def load(path):
    with open(os.path.join(DATA, path), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    os.makedirs(OUT, exist_ok=True)
    sectors = load("sectors.json")["sectors"]
    manifest = load("exposure/_manifest.json")

    # --- resolve each sector slug to an exposure file, per the child/parent rule
    exposure = {}          # slug -> parsed exposure json
    code_of = {}           # slug -> FIGARO code the slug occupies in exposure space
    no_exposure = []       # slugs with neither own nor parent file
    for slug, meta in sectors.items():
        own = os.path.join(DATA, "exposure", slug.replace("/", "__") + ".json")
        parent = meta.get("parent")
        par = (
            os.path.join(DATA, "exposure", parent.replace("/", "__") + ".json")
            if parent
            else None
        )
        used = own if os.path.exists(own) else (par if par and os.path.exists(par) else None)
        if used is None:
            no_exposure.append(slug)
            continue
        with open(used, encoding="utf-8") as fh:
            exposure[slug] = json.load(fh)
        code = manifest.get(slug, {}).get("code") or exposure[slug].get("figaro_code")
        code_of[slug] = code
        if used != own:
            DECISIONS.append(
                "%s has no exposure file of its own; used the parent %s file." % (slug, parent)
            )

    DECISIONS.append(
        "Named sectors with no exposure file (own or parent), skipped wherever named: "
        + (", ".join(sorted(no_exposure)) if no_exposure else "none")
        + "."
    )

    # --- schema mapping
    DECISIONS.append(
        "Exposure schema: each data/exposure/<slug>.json holds eu.customers and "
        "eu.suppliers, lists of {code, label, share} where share is a percent of the "
        "sector's total output (customers) or total inputs (suppliers) and the OTHER "
        "row carries the remainder to 100. Those are the customer and supplier shares "
        "the task describes. Shares divided by 100, so every exposure and cutoff below "
        "is on a 0-1 scale."
    )
    DECISIONS.append(
        "Counterparty rows are keyed by FIGARO code, not by register sector slug, so "
        "all arithmetic runs in FIGARO code space. A named slug is mapped to its code "
        "via data/exposure/_manifest.json; a code is 'named' for a measure if any of "
        "that measure's named slugs maps to it. See the DEVIATION note below for how the "
        "named set is handled in the ratio."
    )
    DECISIONS.append(
        "FIGARO collapses some slugs onto one code: steel and alu are both C24, cement "
        "and glass are both C23. Naming either member of a pair therefore marks the "
        "shared code as named, so the other member cannot be counted as hidden."
    )
    DECISIONS.append(
        "Side: customers for measure_type obligation or prohibition, suppliers for "
        "incentive or right. Rows with several named sectors sum the shares without "
        "normalising, so a multi-sector measure can total more than 1. Measures are "
        "weighted equally and the weight field is ignored. Direct shares only, no "
        "Leontief inverse. OTHER is treated as one unnamed sector and always counts "
        "toward the hidden numerator."
    )
    DECISIONS.append(
        "Rows with an empty sectors_named are excluded from the shares and counted as "
        "horizontal rows. A row whose named sectors all lack an exposure file is "
        "counted as used but yields zero total exposure and no hidden share."
    )
    DECISIONS.append(
        "'Reached' in Table C means exposure above %s for that measure, counted only "
        "for measures that do not name the code." % REACHED_CUTOFF
    )
    DECISIONS.append(
        "DEVIATION, forced by the arithmetic: applying 'sectors in the named set get "
        "exposure zero' to both halves of the ratio makes the denominator equal the "
        "numerator, so hidden share is identically 1.000 for every row and the "
        "statistic carries no information. The zeroing is therefore applied to the "
        "numerator only: named sectors are excluded from the hidden sum but keep their "
        "exposure in the denominator, so hidden share is the fraction of a measure's "
        "total direct exposure that lands outside its own named set. The retained "
        "named exposure is reported as named_exposure in the CSV; where a measure names "
        "one sector whose FIGARO code no other named sector shares, that column is the "
        "share the named sectors trade with each other."
    )
    DECISIONS.append("iaa is excluded throughout: it is a proposal, not adopted law.")

    labels = {}
    for slug, meta in sectors.items():
        code = code_of.get(slug)
        if code:
            labels.setdefault(code, meta.get("label", slug))
    per_file_rows = defaultdict(list)
    horizontal = Counter()
    total_rows = Counter()
    named_count = Counter()
    reached_count = Counter()
    csv_rows = []
    skipped_named = Counter()

    for fname in FILES:
        register = load(fname + ".json")
        total_rows[fname] = len(register)
        for row in register:
            named = row.get("sectors_named") or []
            if not named:
                horizontal[fname] += 1
                continue

            mtype = row.get("measure_type")
            side = "customers" if mtype in CUSTOMER_TYPES else "suppliers"
            if mtype not in CUSTOMER_TYPES and mtype not in SUPPLIER_TYPES:
                side = "customers"
                DECISIONS.append(
                    "measure_type %r is neither obligation/prohibition nor "
                    "incentive/right; used the customer side." % mtype
                )

            named_codes = set()
            used_named = []
            for slug in named:
                if slug not in exposure:
                    skipped_named[slug] += 1
                    continue
                used_named.append(slug)
                if code_of.get(slug):
                    named_codes.add(code_of[slug])

            expo = defaultdict(float)
            for slug in used_named:
                for entry in exposure[slug]["eu"].get(side, []):
                    labels[entry["code"]] = entry.get("label", entry["code"])
                    expo[entry["code"]] += entry["share"] / 100.0
            total = sum(expo.values())
            named_expo = sum(v for k, v in expo.items() if k in named_codes)
            hidden = total - named_expo
            share = hidden / total if total else None
            other = (expo.get("OTHER", 0.0) / total) if total else None

            for code in named_codes:
                named_count[code] += 1
            for code, v in expo.items():
                if v > REACHED_CUTOFF and code not in named_codes:
                    reached_count[code] += 1

            rec = {
                "file": fname,
                "id": row.get("id"),
                "provision_id": row.get("provision_id") or "",
                "measure_type": mtype,
                "class": row.get("class"),
                "sectors_named": " ".join(named),
                "side": side,
                "total_exposure": total,
                "named_exposure": named_expo,
                "hidden_exposure": hidden,
                "hidden_share": share,
                "other_share": other,
            }
            per_file_rows[fname].append(rec)
            csv_rows.append(rec)

    for slug, n in sorted(skipped_named.items()):
        DECISIONS.append(
            "Named sector %s has no exposure file; skipped in the %d measure(s) naming it."
            % (slug, n)
        )

    # ---------------- CSV ----------------
    csv_path = os.path.join(OUT, "hidden_share.csv")
    cols = [
        "file", "id", "provision_id", "measure_type", "class", "sectors_named",
        "side", "total_exposure", "named_exposure", "hidden_exposure", "hidden_share",
        "other_share",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in csv_rows:
            w.writerow({
                k: ("" if r[k] is None else (round(r[k], 6) if isinstance(r[k], float) else r[k]))
                for k in cols
            })

    # ---------------- Markdown ----------------
    def fmt(x, nd=3):
        return "-" if x is None else ("%.*f" % (nd, x))

    def mean(vals):
        return statistics.fmean(vals) if vals else None

    def median(vals):
        return statistics.median(vals) if vals else None

    def table(headers, rows):
        out = ["| " + " | ".join(headers) + " |",
               "|" + "|".join(["---"] * len(headers)) + "|"]
        for r in rows:
            out.append("| " + " | ".join(str(c) for c in r) + " |")
        return "\n".join(out)

    md = ["# Hidden share — ets and cbam", "", "## DECISIONS", ""]
    md += ["- " + d for d in DECISIONS]

    # Table A
    md += ["", "## Table A — per file", ""]
    a = []
    for f in FILES:
        rows = per_file_rows[f]
        hs = [r["hidden_share"] for r in rows if r["hidden_share"] is not None]
        os_ = [r["other_share"] for r in rows if r["other_share"] is not None]
        a.append([f, total_rows[f], horizontal[f], len(rows), len(hs),
                  fmt(mean(hs)), fmt(median(hs)), fmt(mean(os_))])
    md += [table(["file", "rows", "horizontal rows", "rows used", "rows with a share",
                  "mean hidden share", "median hidden share", "mean OTHER share"], a)]
    md += ["", "Rows used minus rows with a share are rows whose every named sector "
           "lacks an exposure file, so they carry no exposure at all.", ""]

    # Table B
    md += ["", "## Table B — mean hidden share by measure_type, then by class", ""]
    b = []
    for f in FILES:
        rows = per_file_rows[f]
        for key in ("measure_type", "class"):
            for val in sorted({r[key] for r in rows}):
                hs = [r["hidden_share"] for r in rows
                      if r[key] == val and r["hidden_share"] is not None]
                n = sum(1 for r in rows if r[key] == val)
                b.append([f, key, val, n, len(hs), fmt(mean(hs))])
    md += [table(["file", "split", "value", "rows used", "rows with a share",
                  "mean hidden share"], b)]

    # Table C
    md += ["", "## Table C — sectors named vs reached (exposure > %s)" % REACHED_CUTOFF, ""]
    all_codes = set(named_count) | set(reached_count)
    c = []
    for code in sorted(all_codes, key=lambda k: (-reached_count[k], -named_count[k], k)):
        c.append([code, labels.get(code, code), named_count[code], reached_count[code],
                  "NEVER NAMED" if named_count[code] == 0 else ""])
    md += [table(["code", "label", "named in", "reached in", "flag"], c)]

    # Table D
    md += ["", "## Table D — ten highest and ten lowest hidden share", ""]
    ranked = sorted((r for r in csv_rows if r["hidden_share"] is not None),
                    key=lambda r: r["hidden_share"])
    d = []
    for band, sel in (("highest", list(reversed(ranked[-10:]))), ("lowest", ranked[:10])):
        for r in sel:
            d.append([band, r["file"], r["id"], r["measure_type"], r["sectors_named"],
                      r["side"], fmt(r["hidden_share"]), fmt(r["other_share"])])
    md += [table(["band", "file", "id", "measure_type", "named sectors", "side",
                  "hidden share", "OTHER share"], d)]

    # Paragraph
    md += ["", "## Observations", ""]
    stats = {}
    for f in FILES:
        rows = per_file_rows[f]
        hs = [r["hidden_share"] for r in rows if r["hidden_share"] is not None]
        os_ = [r["other_share"] for r in rows if r["other_share"] is not None]
        stats[f] = (mean(hs), median(hs), mean(os_), len(hs))

    def by_type(f, t):
        v = [r["hidden_share"] for r in per_file_rows[f]
             if r["measure_type"] == t and r["hidden_share"] is not None]
        return mean(v), len(v)

    ets_ob, ets_ob_n = by_type("ets", "obligation")
    ets_in, ets_in_n = by_type("ets", "incentive")
    never = [(code, reached_count[code]) for code in all_codes if named_count[code] == 0]
    never.sort(key=lambda x: -x[1])
    never_txt = ", ".join(
        "%s (%s) reached in %d" % (c0, labels.get(c0, c0), n) for c0, n in never[:6]
    ) or "none"

    md += [
        "Hidden share averages %s in ets (median %s, %d rows carrying a share) and %s in cbam "
        "(median %s, %d rows carrying a share). Within ets, obligations average %s over %d rows "
        "against %s over %d rows for incentives, a gap of %s; cbam carries no "
        "incentive rows, so no comparison there. %d counterparty codes clear the %s "
        "exposure cutoff without ever being named across the two files, the most "
        "reached being %s. OTHER alone accounts for a mean %s of exposure in ets and "
        "%s in cbam, against mean hidden shares of %s and %s." % (
            fmt(stats["ets"][0]), fmt(stats["ets"][1]), stats["ets"][3],
            fmt(stats["cbam"][0]), fmt(stats["cbam"][1]), stats["cbam"][3],
            fmt(ets_ob), ets_ob_n, fmt(ets_in), ets_in_n,
            fmt(ets_ob - ets_in) if ets_ob is not None and ets_in is not None else "-",
            len(never), REACHED_CUTOFF, never_txt,
            fmt(stats["ets"][2]), fmt(stats["cbam"][2]),
            fmt(stats["ets"][0]), fmt(stats["cbam"][0]),
        )
    ]

    md_path = os.path.join(OUT, "hidden_share.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")

    print(csv_path)
    print(md_path)


if __name__ == "__main__":
    main()

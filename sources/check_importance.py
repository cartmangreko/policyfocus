"""
The gate on the importance ranking: data/transition/importance/*.json.

    python3 check_importance.py             # exits non-zero on any failure

Three things are checked, and they are the three ways a computed ranking stops
being a computed ranking:

  REPRODUCTION   the committed file is byte-identical to what build_importance.py
                 produces from today's inputs. A ranking that has drifted from
                 its inputs is a hand-edited ranking whether or not anyone edited
                 it by hand.

  OVERRIDES      every override_rank carries an override_reason. The override
                 exists because a reviewer sometimes knows something the model
                 does not, and it is legitimate exactly as long as it is stated:
                 both fields render on the measure page. An override without a
                 reason is the model being quietly overruled, which is the thing
                 this whole layer is built to avoid.

  SECTOR VIEW    every measure marked in_sector_view has money > 0 or
                 bottleneck_linkage > 0, and no measure outside the view has
                 either. Attention alone never admits a measure -- it is a
                 cross-check on the ranking, not an input to it, and a gate is
                 the only place that distinction survives contact with a busy
                 news cycle.
"""

from __future__ import annotations

import json
import sys

import build_importance as bi
import sector_map as sm


def main() -> int:
    failures: list[str] = []
    sectors = sorted(p.stem for p in bi.OUT_DIR.glob("*.json")) if bi.OUT_DIR.exists() else []
    if not sectors:
        print("check_importance: no built rankings found; run build_importance.py")
        return 1

    params = sm.index(sm.load("parameter"))

    for sector in sectors:
        path = bi.OUT_DIR / f"{sector}.json"
        committed = json.loads(path.read_text(encoding="utf-8"))
        rebuilt = bi.build(sector, committed["priced_year"])
        if json.dumps(rebuilt, sort_keys=True) != json.dumps(committed, sort_keys=True):
            failures.append(f"{sector}: the committed ranking does not reproduce from "
                            f"its inputs — run build_importance.py")

        for m in committed["measures"]:
            where = f"{sector} {m['measure']}"
            if m.get("override_rank") is not None and not m.get("override_reason"):
                failures.append(f"{where}: override_rank without override_reason")

            money = (m["money"]["value"] or 0) > 0
            linkage = m["bottleneck_linkage"]["weight"] > 0
            if m["in_sector_view"] != (money or linkage):
                failures.append(
                    f"{where}: in_sector_view={m['in_sector_view']} but money={money} "
                    f"linkage={linkage} — the sector-view gate is money or linkage, "
                    f"never attention")

            for pid in m["money"]["inputs"]:
                if pid not in params and not pid.startswith(("cement-", "cbam-cement-")):
                    # Project ids appear as inputs on the grant model; parameter ids
                    # on the others. Anything else is a typo that would otherwise
                    # show as a missing figure rather than as an error.
                    if pid not in {p["id"] for p in sm.load("project")}:
                        failures.append(f"{where}: money input {pid!r} is neither a "
                                        f"parameter nor a project")

    if failures:
        print(f"check_importance: {len(failures)} failures\n")
        for f in failures:
            print(f"  {f}")
        return 1

    total = sum(len(json.loads((bi.OUT_DIR / f"{s}.json").read_text())["measures"])
                for s in sectors)
    print(f"check_importance: OK — {len(sectors)} sector(s), {total} measures ranked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

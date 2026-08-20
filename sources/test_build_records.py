"""
Negative tests for the records gate. A gate is only worth the failures it
catches, so each case here breaks one thing on purpose and asserts that
build_records.py exits non-zero AND says which check caught it.

    python3 test_build_records.py

Every case runs against a COPY of data/records (PF_RECORDS_DIR) and, where the
template is what is broken, a copy of data/prose.json (PF_PROSE_PATH). The real
files are never written. The positive case runs last: the repo as it stands
must still pass, so a test run cannot leave a false green behind.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
RECORDS = DATA / "records"
PPWR = "2026-08-ppwr-ingested"
AMEND = "2026-08-ppwr-replaces-packaging-directive"
ETS = "2026-08-ets-revision-proposed"


def run(records_dir: Path, prose_path: Path | None = None) -> tuple[int, str]:
    env = {**os.environ, "PF_RECORDS_DIR": str(records_dir)}
    if prose_path:
        env["PF_PROSE_PATH"] = str(prose_path)
    p = subprocess.run([sys.executable, str(HERE / "build_records.py"), "--check"],
                       capture_output=True, text=True, cwd=HERE, env=env)
    return p.returncode, p.stdout + p.stderr


def case(name: str, expect: str, mutate_record=None, mutate_prose=None,
         target: str = PPWR) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "records"
        shutil.copytree(RECORDS, d)
        prose_path = None
        if mutate_record:
            path = d / f"{target}.json"
            doc = json.loads(path.read_text(encoding="utf-8"))
            mutate_record(doc)
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if mutate_prose:
            prose_path = Path(tmp) / "prose.json"
            prose = json.loads((DATA / "prose.json").read_text(encoding="utf-8"))
            mutate_prose(prose)
            prose_path.write_text(json.dumps(prose, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8")
        rc, out = run(d, prose_path)
    ok = rc != 0 and expect in out
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        print(f"        expected exit!=0 and {expect!r}; got rc={rc}")
        for line in out.strip().splitlines()[:8]:
            print(f"        | {line}")
    return ok


def to_amendment(doc: dict, row_id: str) -> None:
    """An amendment is the family that names particular measures, so it is the
    one that can carry a bad measure reference at all."""
    doc["template"] = "amendment"
    doc["measures"] = [{"file": "ppwr", "row_id": row_id}]


def main() -> int:
    print("negative cases (each must fail the build):")
    results = [
        case("a measure reference that is not in the register",
             "NOPE-99' is not in data/ppwr.json",
             lambda d: to_amendment(d, "NOPE-99")),
        case("a count that disagrees with the register",
             "[counts]",
             lambda d: d["counts"].__setitem__("measures", 88)),
        case("a sector list that disagrees with the register",
             "[counts]",
             lambda d: d["sectors_named"].append("power")),
        case("a top sector that is not the most-named one",
             "[counts]",
             lambda d: d.__setitem__("top_sector", "wood")),
        case("an event shape that fits no template family",
             "fits no template family",
             lambda d: d.__setitem__("template", "editorial")),
        case("an id whose date prefix disagrees with the event date",
             "[id]",
             lambda d: d.__setitem__("event_date", "2026-07-18")),
        case("an act label that is not the act's display name",
             "[references]",
             lambda d: d.__setitem__("act_label", "The Packaging Rules")),
        case("a diagram that leads on a sector the prose does not",
             "[diagram]",
             lambda d: d["diagram"]["edges"][0].__setitem__("to", "sector:wood")),
        case("a template slot the gate cannot compute",
             "this gate does not compute",
             None,
             lambda p: p["record_templates"]["families"]["new_act_ingested"].__setitem__(
                 "body", "{act_name} affects {profit_impact} of turnover.")),
        case("a template family with no reviewed text",
             "has no headline+body template",
             None,
             lambda p: p["record_templates"]["families"].pop("new_act_ingested")),
        # THE REACH SUPPRESSION (sources/scope.md, "Reach is not stated on a
        # record about an amending proposal"). Three ways it could be lost: the
        # template regaining a reach slot, the no-reach variant going missing,
        # and the suppressed record's sectors surviving into the index.
        case("a reach clause rendering for an amending proposal",
             "this gate does not compute",
             None,
             lambda p: p["record_templates"]["families"]["new_act_ingested"].__setitem__(
                 "body_no_reach",
                 "{act_name} names {named_count} sectors and reaches {reached_count} more."),
             target=ETS),
        case("an amending proposal whose family has no suppressed variant",
             "reach may not be stated",
             None,
             lambda p: p["record_templates"]["families"]["new_act_ingested"].pop("body_no_reach"),
             target=ETS),
        case("an amendment record naming an act the manifest does not link to",
             "is not recorded in sources/manifest.json",
             lambda d: d.__setitem__("prior_act", "32003L0087"),
             target=AMEND),
        case("an amendment record with no act it changes",
             "must name the act it changes",
             lambda d: d.pop("prior_act"),
             target=AMEND),
        case("an amendment record whose measures have no earlier wording on file",
             "no before to show against the after",
             lambda d: d.__setitem__("measures", [{"file": "ppwr", "row_id": "FREE-01"}]),
             target=AMEND),
        case("a diagram scoped to a different measure set than the prose",
             "[diagram]",
             lambda d: d["diagram"]["edges"][0]["quantity"].pop("scope"),
             target=AMEND),
        case("a status note missing for the record's legal standing",
             "no status note for basis_status",
             None,
             lambda p: p["record_templates"]["status_notes"].pop("adopted")),
    ]

    print("positive case (the repo as it stands must pass):")
    rc, out = run(RECORDS)
    ok = rc == 0
    print(f"  {'PASS' if ok else 'FAIL'}  every published record builds")
    if not ok:
        print(out)
    results.append(ok)

    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

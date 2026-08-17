"""
Reconcile two independent extraction passes for one file.

Matches records by overlapping article reference (normalised), then flags
disagreements on direction/measure_type and lists Pass-B-only finds. Writes
`<prefix>_disagreements.json` for human review.

WHAT THIS DOES NOT DO
=====================
It does not write data/. The docstring here used to promise "a canonical merged
set (Pass A as base)", and no such set was ever produced -- the only file this
script has ever written is the disagreements report. Nothing in the repo builds
data/ets.json or data/iaa.json from these passes; those files are written in
place by build_benefit_axis.py, and data/omnibus.json by build_data_v2.py from
extracted.json. Said plainly here because the missing sentence is what made the
passes look like a live input that could overwrite corrected data.

THE INPUT GUARD
===============
Everything this script reports is only as good as its inputs. Comparing two
passes whose spans no longer appear in the current sources produces a
disagreement count that means nothing: rows fail to match on stale article
references, Pass-B-only lists fill with rows that are not really B-only, and the
output reads like a real reconciliation. So every input is put through
verify_pass.py first, and a failing input stops the run before anything is
written.

Usage: python3 reconcile.py <pass_a.json> <pass_b.json> <prefix>
       prefix is the file key (ets | iaa) and selects the sources to verify
       against, via benefit_axis.FILE_SOURCES.
"""
import json, os, re, subprocess, sys

from benefit_axis import FILE_SOURCES

_HERE = os.path.dirname(os.path.abspath(__file__))


def verify_inputs(paths, file_key):
    """Run verify_pass.py over each input. Returns the list that failed.

    Shelling out rather than importing: verify_pass is the gate, and running it
    the same way a person would means this guard cannot drift from the check it
    claims to be applying.
    """
    sources = FILE_SOURCES.get(file_key)
    if sources is None:
        sys.exit(
            f"reconcile: unknown file key {file_key!r}; expected one of "
            f"{sorted(FILE_SOURCES)}. The prefix selects which sources the "
            "inputs are verified against, so it cannot be arbitrary."
        )

    failed = []
    for p in paths:
        result = subprocess.run(
            [sys.executable, os.path.join(_HERE, "verify_pass.py"), p,
             *[os.path.join(_HERE, s) for s in sources]],
            capture_output=True, text=True,
        )
        print(result.stdout.rstrip())
        if result.returncode != 0:
            failed.append(p)
    return failed

def norm_article(a):
    # pull out compound article-paragraph identifiers like "10a", "12b", "3gaa", "28a(1)"
    # require at least 2 chars incl. a letter, or a paren-qualified number, to avoid bare-digit false matches
    tokens = re.findall(r'\d+[a-z]{1,3}(?:\(\d+[a-z]?\))?|\d+\(\d+[a-z]?\)', a.lower())
    return set(tokens)

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def main():
    if len(sys.argv) != 4:
        sys.exit("usage: reconcile.py <pass_a.json> <pass_b.json> <prefix>")
    file_a, file_b, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3]

    # THE GUARD. Before anything is read for comparison or written anywhere.
    failed = verify_inputs([file_a, file_b], out_prefix)
    if failed:
        sys.exit(
            "\nreconcile: refusing to run — these inputs do not verify against "
            f"the current sources:\n  " + "\n  ".join(failed) +
            "\n\nA reconciliation of stale passes is not a reconciliation: rows "
            "fail to match on spans the sources no longer contain, and the "
            "disagreement count that comes out looks authoritative and is not. "
            "Re-anchor the passes against data/ first. Nothing was written."
        )

    a_rows = load(file_a)
    b_rows = load(file_b)

    b_matched = set()
    disagreements = []
    b_only = []

    for ra in a_rows:
        na = norm_article(ra.get('article', ''))
        best = None
        best_overlap = 0
        for j, rb in enumerate(b_rows):
            if j in b_matched:
                continue
            nb = norm_article(rb.get('article', ''))
            overlap = len(na & nb)
            if overlap > best_overlap:
                best_overlap = overlap
                best = j
        if best is not None and best_overlap > 0:
            rb = b_rows[best]
            b_matched.add(best)
            if ra['measure_type'] != rb['measure_type'] or ra['direction'] != rb['direction']:
                disagreements.append({
                    'a_id': ra['id'], 'b_id': rb['id'], 'article': ra['article'],
                    'a': {'measure_type': ra['measure_type'], 'direction': ra['direction'], 'addressee': ra['addressee']},
                    'b': {'measure_type': rb['measure_type'], 'direction': rb['direction'], 'addressee': rb['addressee']},
                })
    for j, rb in enumerate(b_rows):
        if j not in b_matched:
            b_only.append({'id': rb['id'], 'article': rb['article'], 'measure_type': rb['measure_type'],
                            'direction': rb['direction'], 'addressee': rb['addressee'],
                            'benefit_or_duty': rb.get('benefit') or rb.get('duty')})

    print(f"Pass A: {len(a_rows)} rows, Pass B: {len(b_rows)} rows")
    print(f"Matched (by article overlap): {len(b_matched)}")
    print(f"Disagreements (measure_type/direction): {len(disagreements)}")
    for d in disagreements:
        print(f"  {d['a_id']} vs {d['b_id']} [{d['article']}]: A={d['a']} B={d['b']}")
    print(f"\nPass-B-only finds (no article-overlap match in A): {len(b_only)}")
    for o in b_only:
        print(f"  {o['id']} [{o['article']}] {o['measure_type']}/{o['direction']}: {o['benefit_or_duty'][:80]}")

    with open(f'{out_prefix}_disagreements.json', 'w', encoding='utf-8') as f:
        json.dump({'disagreements': disagreements, 'b_only': b_only}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

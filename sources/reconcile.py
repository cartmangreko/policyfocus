"""
Reconcile two independent extraction passes for one file.

Matches records by the Pass B crosswalk first and by overlapping article
reference second, then flags disagreements on direction/measure_type and lists
Pass-B-only finds. Writes `<prefix>_disagreements.json` for human review.

WHY THE CROSSWALK COMES FIRST
=============================
Article overlap alone cannot identify a provision. Four ETS register rows share
"Art. 1(15)(d)", so the matcher paired whatever it reached first and produced
confident nonsense -- it reported AVI-02 against AVI-03, and LM-15b against
NZT-04, as measure_type disagreements between rows that are not the same
provision. Worse, every B row it failed to pair was filed under "Pass-B-only
finds", which reads as "the register is missing this". It was not: 22 of the 27
so listed were provisions the register already carried under a Pass A id, and
that list was acted on as if it were a coverage gap.

reanchor_passes.PASS_B_CROSSWALK states which Pass B id and which register id
name one provision. Pass A's ids are the register's, so the same map resolves
A-to-B pairing exactly, and only the genuinely unmapped rows fall through to
article overlap. Pass-B-only is now split in two: rows ruled into the register
with no Pass A counterpart (already handled, listed so the count stays legible)
and rows nobody has ruled on yet. The second list is a CANDIDATE list -- the
crosswalk is not exhaustive, so a row on it may still turn out to be registered.
Confirming one means comparing spans against data/, not trusting the id.

THE DATE CHECK, AND HOW FAR TO TRUST IT
=======================================
Two passes can agree on measure_type and direction and still disagree about
when the provision bites, and until now nothing looked. That is not a small
field: for an amending act the application date is set by a separate article
that lists amending points by number, so it is read off a different sentence
from everything else on the row and gets its own chance to be wrong. The CBAM
pass found ten such rows, seven of them a plain misreading of Art. 2's three
application dates.

`when` is prose, so the comparison is on the SET OF DATES a row commits to --
calendar dates, bare years, and whether it falls back on entry into force --
not on the wording. Rows where either side commits to no date at all are
skipped rather than reported as disagreeing with the one that does.

It is a candidate list, and a noisier one than the classification list, for a
reason that is not about dates: a pair matched by ARTICLE OVERLAP may not be
the same provision at all, and then its dates differ because the rows differ.
Every crosswalk-matched date disagreement is real; an article-matched one has
to be read against the two rows before it means anything.

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
       prefix is the file key. It does two things: it selects the sources both
       passes are verified against, via benefit_axis.FILE_SOURCES, and it names
       the report written as <prefix>_disagreements.json.

       Any key in FILE_SOURCES is accepted -- currently ets, iaa, omnibus,
       cbam, nzia and crma -- but a run is only meaningful for a file that
       HAS a second pass. Those are:

           ets    ets_pass_a.json    ets_pass_b.json     (frozen snapshots)
           iaa    iaa_pass_a.json    iaa_pass_b.json     (frozen snapshots)
           cbam   ../data/cbam.json  cbam_pass_b.json    (B regenerated live)
           nzia   ../data/nzia.json  nzia_pass_b.json    (B regenerated live)

       omnibus has no second pass and never had one. The line above used to say
       "(ets | iaa)", which was true when it was written and stopped being true
       when CBAM got a second read, was wired into PASS_B_CROSSWALK and
       FILE_SOURCES, and became the file reconciliation_gate.py certifies.

       Pass A is the REGISTER file for cbam and nzia, and a frozen pass_a
       snapshot for ets and iaa. Either way Pass A's ids are the register's,
       which is what makes the crosswalk resolve A-to-B pairing exactly.
"""
import json, os, re, subprocess, sys

from benefit_axis import FILE_SOURCES
from reanchor_passes import PASS_B_CROSSWALK

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

_MONTH = ("january|february|march|april|may|june|july|august|september|"
          "october|november|december")
_DATE_RE = re.compile(r"\b\d{1,2}\s+(?:" + _MONTH + r")\s+(?:19|20)\d{2}", re.I)
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_EIF_RE = re.compile(r"entry into force|entering into force|on adoption", re.I)


def when_signature(when):
    """The dates a `when` string commits to, as a comparable set.

    `when` is prose and the two passes never phrase it alike, so a string
    compare would flag every row and mean nothing. What is comparable is the
    set of dates the row asserts: full calendar dates, bare years, and whether
    it falls back on entry into force. Two rows reading the same provision
    should commit to the same set however they word it.
    """
    text = when or ""
    sig = {m.group(0).lower() for m in _DATE_RE.finditer(text)}
    sig |= {"y" + y for y in _YEAR_RE.findall(text)}
    if _EIF_RE.search(text):
        sig.add("entry-into-force")
    return sig


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

    # Pass A's ids ARE the register's, so a crosswalk entry pointing at a Pass A
    # id identifies the two rows that read the same provision. Matching on that
    # first is strictly better than article overlap, which cannot tell four rows
    # sharing "Art. 1(15)(d)" apart and pairs whatever it reaches first.
    crosswalk = PASS_B_CROSSWALK.get(os.path.basename(file_b), {})
    a_by_id = {ra['id']: i for i, ra in enumerate(a_rows)}

    b_matched = {}          # b index -> a index
    matched_by = {}         # b index -> "crosswalk" | "article"
    for j, rb in enumerate(b_rows):
        target = crosswalk.get(rb['id'])
        if target is not None and target in a_by_id:
            b_matched[j] = a_by_id[target]
            matched_by[j] = 'crosswalk'

    a_taken = set(b_matched.values())
    for i, ra in enumerate(a_rows):
        if i in a_taken:
            continue
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
            b_matched[best] = i
            matched_by[best] = 'article'

    disagreements = []
    # Kept separate from the classification disagreements above rather than
    # folded into them. `when` is not a classification: a row can be correctly
    # typed and still cite the wrong application date, and the two failures are
    # found and fixed by different means. Merging them would also move the
    # headline disagreement count for reasons that have nothing to do with the
    # benefit axis.
    date_disagreements = []
    for j, i in sorted(b_matched.items()):
        ra, rb = a_rows[i], b_rows[j]
        sa, sb = when_signature(ra.get('when')), when_signature(rb.get('when'))
        # Both sides must actually commit to a date. A row that says only
        # "annually" or "n/a" has nothing to disagree with, and reporting it
        # against one that does would fill the list with absences.
        if sa and sb and sa != sb:
            date_disagreements.append({
                'a_id': ra['id'], 'b_id': rb['id'], 'article': ra['article'],
                'matched_by': matched_by[j],
                'a_when': ra.get('when'), 'b_when': rb.get('when'),
            })
        if ra['measure_type'] != rb['measure_type'] or ra['direction'] != rb['direction']:
            disagreements.append({
                'a_id': ra['id'], 'b_id': rb['id'], 'article': ra['article'],
                'matched_by': matched_by[j],
                'a': {'measure_type': ra['measure_type'], 'direction': ra['direction'], 'addressee': ra['addressee']},
                'b': {'measure_type': rb['measure_type'], 'direction': rb['direction'], 'addressee': rb['addressee']},
            })

    # A B-row with no Pass A partner is not automatically a gap in the register.
    # It is a gap only if no register row rules on its provision at all -- and
    # the crosswalk is what knows the difference. Reporting the two together as
    # "Pass-B-only finds" is what made 22 already-registered provisions read as
    # missing, so they are split and counted separately.
    #
    # THE REMAINING LIST IS A CANDIDATE LIST, NOT A GAP LIST. The crosswalk
    # covers the 27 rows that were blocked plus ETSB-MRV-02, and no more, so a
    # row can land below simply because nobody has ruled on it yet. Id identity
    # deliberately does NOT count as a ruling: Pass B reused ids for different
    # provisions (its LM-13, LM-14, LM-15b and AVI-04 each name a provision the
    # register files under that id or another), and matching on the coincidence
    # would manufacture exactly the false certainty this split exists to end.
    # Each row below needs the same span-level check the crosswalk entries got.
    b_only, b_registered = [], []
    for j, rb in enumerate(b_rows):
        if j in b_matched:
            continue
        entry = {'id': rb['id'], 'article': rb['article'], 'measure_type': rb['measure_type'],
                 'direction': rb['direction'], 'addressee': rb['addressee'],
                 'benefit_or_duty': rb.get('benefit') or rb.get('duty')}
        target = crosswalk.get(rb['id'])
        if target is None:
            b_only.append(entry)
        else:
            # Ruled on, but the register row has no Pass A counterpart -- these
            # are the promotions (ETSB-/IAAB-) and rows only one pass caught.
            b_registered.append({**entry, 'register_id': target})

    n_cross = sum(1 for v in matched_by.values() if v == 'crosswalk')
    print(f"Pass A: {len(a_rows)} rows, Pass B: {len(b_rows)} rows")
    print(f"Matched: {len(b_matched)} ({n_cross} by crosswalk, "
          f"{len(b_matched) - n_cross} by article overlap)")
    print(f"Disagreements (measure_type/direction): {len(disagreements)}")
    for d in disagreements:
        print(f"  [{d['matched_by']}] {d['a_id']} vs {d['b_id']} [{d['article']}]: A={d['a']} B={d['b']}")
    print(f"\nApplication-date disagreements (`when`): {len(date_disagreements)}")
    for d in date_disagreements:
        print(f"  [{d['matched_by']}] {d['a_id']} vs {d['b_id']} [{d['article']}]")
        print(f"      A: {d['a_when']}")
        print(f"      B: {d['b_when']}")

    print(f"\nPass-B rows ruled into the register, no Pass A counterpart: {len(b_registered)}")
    for o in b_registered:
        print(f"  {o['id']} -> {o['register_id']} [{o['article']}]")
    print(f"\nPass-B rows not yet ruled on (candidates, not confirmed gaps): {len(b_only)}")
    for o in b_only:
        print(f"  {o['id']} [{o['article']}] {o['measure_type']}/{o['direction']}: {o['benefit_or_duty'][:80]}")

    with open(f'{out_prefix}_disagreements.json', 'w', encoding='utf-8') as f:
        json.dump({'disagreements': disagreements,
                   'date_disagreements': date_disagreements,
                   'b_only': b_only,
                   'b_registered': b_registered}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()

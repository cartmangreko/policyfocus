"""
Reconcile two independent extraction passes for one file.
Matches records by overlapping article reference (normalized), then flags
disagreements on direction/measure_type. Produces a canonical merged set
(Pass A as base) plus a list of flagged rows for human review.
"""
import json, re, sys

def norm_article(a):
    # pull out compound article-paragraph identifiers like "10a", "12b", "3gaa", "28a(1)"
    # require at least 2 chars incl. a letter, or a paren-qualified number, to avoid bare-digit false matches
    tokens = re.findall(r'\d+[a-z]{1,3}(?:\(\d+[a-z]?\))?|\d+\(\d+[a-z]?\)', a.lower())
    return set(tokens)

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def main():
    file_a, file_b, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3]
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

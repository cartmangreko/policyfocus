"""
The measure's standard one-liner renders in Policies and nowhere else.

    python3 check_one_liner_scope.py        # exits non-zero on any violation

WHAT THE RULE IS FOR
====================
Brief 5 §5. The same measure may legitimately appear in three sections of a
sector page: ranked in Policies, paying in Opportunity, and as a clause under a
Bottleneck it bears on. The same SENTENCE may not appear in two of them.

The sentence in question is the authored one-liner in
data/transition/measure_labels.json -- `plain.sentence` -- which says what a
measure requires or grants to somebody who has not read the act. Its `plain.title`
is the measure's NAME and is not restricted: Opportunity links a support measure
by the name a reader met in Policies, which is how they know it is the same
measure. It is the right sentence for a ranked list and the wrong one everywhere
else, because a reader who meets it twice on one page learns nothing the second
time and starts to distrust the first.

So Policies renders it. Opportunity renders a support fact instead, keyed on the
money model that produced the figure (data/prose.json -> opportunity.
support_fact). Bottlenecks renders a short clause about the constraint the
measure bears on, and no title of its own.

HOW IT IS CHECKED
=================
By where `plain.sentence` is READ in the template, not by comparing rendered
strings. A string comparison would pass the day two sections rendered the same
sentence from two different expressions, and would fail the day a title happened
to repeat a phrase. What the rule is actually about is which section is allowed
to reach for that field.

The parse is small and deliberately brittle: it finds the sections in
components/SectorMap.tsx and asks which of them mention `plain`. A rewrite that
changes the shape fails loudly rather than passing vacuously, which is the right
way round for a gate.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "web" / "components" / "SectorMap.tsx"

# The section allowed to render the one-liner, and it is one.
ALLOWED = "policies"

SECTION = re.compile(r'<section className="tmap-section" id="([a-z-]+)">')

# `plain.sentence`, however it is reached — `m.plain.sentence`,
# `m.plain?.sentence`, `plain!.sentence`.
#
# THE SENTENCE, NOT THE TITLE. Brief 5 §5 lists "plain title" and "the measure's
# standard one-liner" as two things, and what it forbids is a repeated SENTENCE.
# A title is the measure's name: Opportunity links a support measure by the name
# a reader met in Policies, which is how they know it is the same measure, and
# banning that would leave the link reading `ets:FND-03`. The rule is about the
# sentence under the name, and this matches exactly that.
READ = re.compile(r"\bplain\s*[?!]?\s*\.\s*sentence\b")


def main() -> int:
    tsx = TEMPLATE.read_text(encoding="utf-8")
    bounds = [(m.group(1), m.start()) for m in SECTION.finditer(tsx)]
    if not bounds:
        print("check_one_liner_scope: no sections found in SectorMap.tsx — this gate "
              "matches the template's exact section shape and is now matching nothing")
        return 1

    problems: list[str] = []
    for i, (section_id, start) in enumerate(bounds):
        end = bounds[i + 1][1] if i + 1 < len(bounds) else len(tsx)
        body = tsx[start:end]
        # Comments explain the rule and name the field; they are not renders.
        body = re.sub(r"\{/\*.*?\*/\}", " ", body, flags=re.S)
        body = re.sub(r"//[^\n]*", " ", body)
        hits = READ.findall(body)
        if hits and section_id != ALLOWED:
            problems.append(
                f'the "{section_id}" section reads the measure one-liner '
                f"({len(hits)} time(s)). Brief 5 §5 gives that sentence to Policies and "
                f"to no other section: Opportunity says what a measure PAYS in a "
                f"support-fact template, and Bottlenecks says what it bears on in a "
                f"clause")

    allowed_body = ""
    for i, (section_id, start) in enumerate(bounds):
        if section_id != ALLOWED:
            continue
        end = bounds[i + 1][1] if i + 1 < len(bounds) else len(tsx)
        allowed_body = tsx[start:end]
    if allowed_body and not READ.search(re.sub(r"\{/\*.*?\*/\}", " ", allowed_body, flags=re.S)):
        problems.append(
            f'the "{ALLOWED}" section renders no one-liner. It is the only section '
            f"allowed to, and a ranked list of titles with no sentence under them is "
            f"the list brief 4 §5 replaced")

    if problems:
        print(f"check_one_liner_scope: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    print(f"check_one_liner_scope: OK — the measure one-liner renders in "
          f"\"{ALLOWED}\" and in none of the other {len(bounds) - 1} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())

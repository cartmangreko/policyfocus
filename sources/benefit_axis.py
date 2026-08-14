"""
The benefit axis: how measure_type is decided, and the guardrail that keeps it honest.

================================================================================
THE CLASSIFICATION RULE  (this is the point at which measure_type is decided)
================================================================================

Set measure_type by THE OBJECT THE PROVISION ACTS ON, not by the instrument the
text happens to name.

One test:

    Does the provision change the support itself -- its amount, its rate,
    its eligibility, or its existence?

    YES -> incentive side.
           direction "add" -> Opportunity.  direction "rem" -> Support cut.

    NO -- it changes a verification step, an audit, a plan requirement, a
          condition, a procedure, a deadline, or the scope of a duty
       -> obligation side.
           direction "add" -> Requirement.  direction "rem" -> Simplification.
           This holds EVEN WHEN the duty is attached to free allocation.

The presence of "free allocation" -- or any other support word -- in the source
text is NOT evidence of measure_type == "incentive". Two provisions that were
mislabelled this way, and what they actually are:

  * "Installations receive 80% of free allocation without additional
    verification."  A VERIFICATION DUTY is removed. Obligation side,
    favourable: Simplification.  (ETS FRE-04)

  * "Top-10% efficient, low-carbon and voluntary-stayer installations are
    exempt from the decarbonisation-plan requirement and the 80/20 tranching
    conditionality."  A CONDITION ATTACHED TO the support is removed, not the
    support. Obligation side, favourable: Simplification -- it protects
    allocation the conditionality could have docked.  (ETS FRE-05)

"Eligibility" in the test above means WHO OR WHAT QUALIFIES for the support --
which actors, which products, which activities. A behavioural or procedural
condition a qualifying recipient must then keep satisfying (draw up a plan, pass
a verification, hit a milestone) is a DUTY, and stays on the obligation side
even though failing it costs money.

================================================================================
THE GUARDRAIL
================================================================================

A row may only sit on the benefit axis if it can point at the quantum it moved.
Mirroring the `source_text in FULLTEXT` discipline the builds already run:

  * valence "Support cut" requires support_cut_basis
  * valence "Opportunity"  requires opportunity_basis

Each is {"text": <verbatim span>, "kind": "amount"|"rate"|"eligibility"|"existence"}
and the text must appear verbatim in the row's own source file. No basis, no
benefit label -- the build fails and names the offending ids.
"""
import json
import os

from textnorm import canonical

BASIS_KINDS = ("amount", "rate", "eligibility", "existence")

BASIS_FIELD = {
    "Support cut": "support_cut_basis",
    "Opportunity": "opportunity_basis",
}

# Every source file a given data file's rows may be quoted from. Matching the
# verify_pass.py convention: a span counts as verbatim if it is an exact
# substring of ANY of them.
#
# These must be the live fetched sources and nothing else. This list previously
# also carried iaa_norm.txt and iaa_annexes_norm.txt -- pre-baked normalised
# copies -- which was a correctness bug rather than redundancy: because a span
# counts if it matches ANY listed file, a quote that no longer appeared in the
# real source could still pass against a stale copy of it. They were 1,439
# canonical characters longer than the live text, the difference being PDF page
# furniture the fetcher now strips, so they were live evidence for text that is
# not in the act. Normalisation happens at compare time via textnorm.canonical,
# which is why no pre-baked variant is needed to begin with.
_HERE = os.path.dirname(os.path.abspath(__file__))
FILE_SOURCES = {
    "ets": ["ets.txt", "ets_annexes.txt"],
    "iaa": ["iaa.txt", "iaa_annexes.txt"],
    "omnibus": ["COM2025_81.txt", "COM2025_80.txt"],
}


def load_fulltext(file_key):
    """Concatenated source text for one data file, for substring checks."""
    parts = []
    for name in FILE_SOURCES[file_key]:
        with open(os.path.join(_HERE, name), encoding="utf-8") as f:
            parts.append(f.read())
    return "\n".join(parts)


def derive_valence(measure_type, direction):
    """Mirrors web/lib/valence.ts deriveValence + VALENCE_LABELS. Kept in sync by
    hand: the build is the authority on the data, the TS is the authority on
    rendering, and they must agree on the same four labels."""
    t = measure_type or "obligation"
    if t == "obligation" and direction == "add":
        return "Requirement"
    if t == "obligation" and direction == "rem":
        return "Simplification"
    if t == "incentive" and direction == "add":
        return "Opportunity"
    if t == "incentive" and direction == "rem":
        return "Support cut"
    return "Neutral"


def benefit_basis_ok(row, fulltext):
    """True unless the row claims a benefit-axis label it cannot substantiate."""
    label = derive_valence(row.get("measure_type"), row.get("direction"))
    field = BASIS_FIELD.get(label)
    if field is None:
        return True
    b = row.get(field)
    return bool(
        b
        and b.get("text")
        and b.get("kind") in BASIS_KINDS
        # Typography-insensitive: the same span is legally identical whether it
        # arrived via XHTML or a PDF conversion. See textnorm.canonical.
        and canonical(b["text"]) in canonical(fulltext)
    )


def assert_benefit_basis(rows, fulltext, where=""):
    """Build-time assertion, in the existing assert style."""
    bad = [r["id"] for r in rows if not benefit_basis_ok(r, fulltext)]
    assert not bad, f"benefit label without a verbatim quantum basis{where}: {bad}"


def check_data_file(path, file_key):
    """Convenience for callers holding a data/*.json path. Returns offending ids."""
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    fulltext = load_fulltext(file_key)
    return [r["id"] for r in rows if not benefit_basis_ok(r, fulltext)]

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
THE THIRD SIDE: `right`
================================================================================

The two-sided test above sends everything that is not a support movement to the
obligation side, which mislabels a whole class of provision: the one that hands
the addressee a FACULTY THEY DID NOT HAVE. Priority permitting for a strategic
project is not a duty being eased -- no duty shrinks -- it is a privilege being
conferred. Filed as Simplification it reads as "less to do", when what actually
happened is "something new you may do".

So a third measure_type, with the same discipline as the support types:

    Does the provision grant the addressee a faculty, status, or entitlement
    they did not previously hold?

    YES -> right.  direction "add" -> Entitlement.
                   direction "rem" -> Entitlement withdrawn.

The operative verb is the test. "may request", "shall provide for the
possibility for operators to", "shall be considered strategic projects" all
CONFER. A bare narrowing or postponement of a duty does not, however welcome it
is -- ETS SHIP-04 replaces the date "31 December 2030" with "31 December 2038"
and confers nothing on anybody, so it stays Simplification. The distinction is
not whether the addressee is better off; it is whether they hold something new.

`right` is a benefit-side type. Right rows carry `benefit`, never `duty`,
symmetric with `incentive`.

================================================================================
THE GUARDRAIL, EXTENDED
================================================================================

Support cut, Opportunity, and both Entitlement labels each require a verbatim
basis. `right_basis` takes its own kinds -- conferral | scope | procedure --
because the quantum a right moves is not an amount but the faculty itself, its
extent, or the process it runs through.

BASIS STATUS. Some quanta genuinely do not live in the fetched text. Rather than
paraphrasing one into existence, a basis may declare where it lives:

  * verbatim  (default) -- the span is in this act. The requirement for
                           everything that can meet it.
  * external  -- the quantum lives in another instrument; `pointer` must name
                 it (CELEX). The span here is the hook, not the number.
  * announced -- the act states an intent with no instrument yet; `pointer`
                 says what was announced.

external and announced are accepted ONLY with a pointer. The escape hatch is
narrow on purpose: it exists so the register can say "the number is over there"
instead of inventing one, and it mirrors the prior_rule "unresolved" convention
already in use.

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
RIGHT_BASIS_KINDS = ("conferral", "scope", "procedure")

BASIS_FIELD = {
    "Support cut": "support_cut_basis",
    "Opportunity": "opportunity_basis",
    "Entitlement": "right_basis",
    "Entitlement withdrawn": "right_basis",
}

# Which kinds each basis field accepts. A support basis names a quantum; a right
# basis names the faculty, its extent, or its process. Keeping them apart stops
# a right row from claiming an "amount" it never moved.
BASIS_KINDS_FOR = {
    "support_cut_basis": BASIS_KINDS,
    "opportunity_basis": BASIS_KINDS,
    "right_basis": RIGHT_BASIS_KINDS,
}

BASIS_STATUSES = ("verbatim", "external", "announced")

# The measure_type vocabulary. `right` is benefit-side: right rows carry
# `benefit`, never `duty`.
MEASURE_TYPES = ("obligation", "incentive", "right")
BENEFIT_SIDE_TYPES = ("incentive", "right")

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
    # The CBAM extension proposal. cbam_base.txt / the prior consolidation are
    # deliberately NOT listed: they are the rule this act amends, not the act
    # itself, and a span counts if it matches ANY listed file -- so including
    # them would let a quote from the existing CBAM Regulation pass as evidence
    # for something this proposal says. Same reasoning that removed the
    # pre-baked iaa_norm copies above.
    "cbam": ["cbam_ext.txt", "cbam_ext_annexes.txt"],
}


def load_fulltext(file_key):
    """Concatenated source text for one data file, for substring checks."""
    parts = []
    for name in FILE_SOURCES[file_key]:
        with open(os.path.join(_HERE, name), encoding="utf-8") as f:
            parts.append(f.read())
    return "\n".join(parts)


def derive_valence(measure_type, direction):
    """Mirrors web/lib/valence.ts deriveValence + VALENCE_LABELS.

    The two are kept identical by check_valence_parity.py, which walks every
    measure_type x direction combination through both and diffs the labels. It
    runs in the build gate, so the pair cannot drift silently the way a
    hand-sync comment invites."""
    # Only an ABSENT measure_type defaults to obligation, matching the TS `??`.
    # `or` would also swallow "", turning a malformed value into a confident
    # "Requirement"; the parity check caught exactly that. A present-but-invalid
    # type falls through to Neutral, where it is visible instead of disguised.
    t = "obligation" if measure_type is None else measure_type
    if t == "obligation" and direction == "add":
        return "Requirement"
    if t == "obligation" and direction == "rem":
        return "Simplification"
    if t == "incentive" and direction == "add":
        return "Opportunity"
    if t == "incentive" and direction == "rem":
        return "Support cut"
    # Scoped to the right side only, so no label floats across types -- the flaw
    # that sank the earlier Cost/Saving and Loss/Withdrawal pairs, where one word
    # had to mean two different movements depending on which type it landed on.
    if t == "right" and direction == "add":
        return "Entitlement"
    if t == "right" and direction == "rem":
        return "Entitlement withdrawn"
    return "Neutral"


def basis_ok(basis, field, fulltext):
    """Whether one basis object substantiates the label that requires it.

    A basis must name its kind from the set its field allows, and then either
    quote the act verbatim or say where the quantum actually lives.
    """
    if not basis or not basis.get("text"):
        return False
    if basis.get("kind") not in BASIS_KINDS_FOR[field]:
        return False

    status = basis.get("basis_status", "verbatim")
    if status not in BASIS_STATUSES:
        return False
    if status in ("external", "announced"):
        # The escape hatch costs a pointer. Without one it is just a paraphrase
        # with a label on it, which is the thing the guardrail exists to stop.
        return bool(basis.get("pointer"))

    # Typography-insensitive: the same span is legally identical whether it
    # arrived via XHTML or a PDF conversion. See textnorm.canonical.
    return canonical(basis["text"]) in canonical(fulltext)


def benefit_basis_ok(row, fulltext):
    """True unless the row claims a benefit-axis label it cannot substantiate."""
    label = derive_valence(row.get("measure_type"), row.get("direction"))
    field = BASIS_FIELD.get(label)
    if field is None:
        return True
    return basis_ok(row.get(field), field, fulltext)


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

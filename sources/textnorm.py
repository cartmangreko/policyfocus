"""
The canonical form used when checking that a quoted span really is verbatim.

Why this exists
---------------
The same provision reaches us in different formats depending on what EUR-Lex
publishes for a given act: XHTML for most regulations, PDF for Commission
proposals that have no other manifestation. Those formats disagree about
characters that carry no legal meaning:

  * line wrapping -- PDF hard-wraps at ~63 characters, XHTML does not, so the
    same sentence has newlines in different places;
  * NBSP -- XHTML writes "EUR 450\xa0000\xa0000", PDF often writes plain
    spaces;
  * hyphenation -- PDF breaks words across lines ("prio-\nrity"), and whether
    that hyphen survives depends on the extractor.

A quoted source_text is legally identical across all of those; only the
typography differs. Comparing raw strings therefore produces false negatives
that have nothing to do with whether the quote is real -- 30 of 61 IAA rows
failed that way when the source moved from a hand-made PDF conversion to a
fetched one, with every word present and in order.

What is deliberately NOT folded
-------------------------------
Case, punctuation, digits, quote marks and dashes are all left alone. They can
carry meaning in legal text, and the guardrail is only worth having if it still
fails on a quote that was actually altered. Folding stops at whitespace and the
hyphenation artefact.
"""
import re

# Invisible characters that no quote can meaningfully contain.
INVISIBLE = ("­", "​", "﻿", "‌", "‍")

_WHITESPACE = re.compile(r"\s+")
# A hyphen followed by a space is a line-break artefact once the text is
# flattened; a real compound hyphen ("carbon-based") has no space after it.
# Applied to both sides of the comparison, so the rare genuine case ("pre- and
# post-award") folds identically on both and still matches.
_BREAK_HYPHEN = re.compile(r"-\s")


def canonical(text):
    """Fold a string to the form used for verbatim comparison."""
    if not text:
        return ""
    for ch in INVISIBLE:
        text = text.replace(ch, "")
    text = text.replace(" ", " ")
    text = _WHITESPACE.sub(" ", text)
    text = _BREAK_HYPHEN.sub("", text)
    return text.strip()


def contains_verbatim(needle, haystack):
    """
    True when needle appears in haystack, ignoring typography only.

    Pre-canonicalise the haystack with canonical() and use `in` directly when
    checking many needles against one text -- this helper re-folds both sides
    on every call.
    """
    return bool(needle) and canonical(needle) in canonical(haystack)

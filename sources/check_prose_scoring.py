#!/usr/bin/env python3
"""A SCORER READS TYPED FIELDS. FREE TEXT IS NEVER PARSED FOR A VERDICT.

    python3 sources/check_prose_scoring.py        # exits non-zero on any violation

WHY THIS EXISTS
===============
Three times in three days a verdict was decided by looking for a word inside a
sentence, and all three were wrong in the same way:

  * D-A5, the Sines screen: a project was excluded because "Sines" appeared inside
    the word `business`.
  * L9, the name-derived hosts: `endesa.com` counted as derived from the project
    name because "Endesa" is a substring of "Huelva - Endesa" — the owner's real
    domain, found in a document, filed as a machine's guess.
  * D-A11, rung 1: the scorer asked whether `site` appeared anywhere in the failed
    leg, and a leg recorded as "CAPACITY — the owner names the site and states no
    GWh" contains the word while failing on capacity.

The shape is identical every time. A sentence is written for a reader and mentions
whatever it needs to mention; a field is written for a machine and means one thing.
A scorer that reads the paragraph is not reading the record, it is guessing at it,
and the guess is wrong in the direction nobody checks — quietly, on the entries
where the prose happens to be fullest.

SO THE RULE IS: a scorer or a classifier reads TYPED FIELDS ONLY. A leg
description, a note, a verbatim, a reason, a clause — none of them may be
substring-matched, regex-matched or split for a verdict. If a verdict needs a fact
that today lives only in prose, the fix is to give the record a field, not to parse
the sentence more cleverly. See sources/scope.md, "A scorer reads typed fields, and
never the prose".

WHAT COUNTS AS A SCORER, and the parse is deliberately brittle
==============================================================
Two tests, because scorers have two shapes here:

  by name    `score_*`, `classify*`, and the `*_of` / `*_cell` / `*_class` /
             `*_outcome` / `*_verdict` / `*_rung` endings this codebase uses —
             score_entry, medium_of, funding_cell, outcome_of.
  by return  every `return` in the function is a bare string constant and there
             are two or more distinct ones. That is a closed vocabulary, which is
             what a classifier is, whatever it is called.

WHAT COUNTS AS A PROSE FIELD, and it is derived and never typed
================================================================
A hand-kept list would have to be remembered, and not remembering is the failure
being prevented. So the vocabulary is MEASURED from the tracked data: every JSON
key in `sources/` and `data/` whose string values are mostly sentence-shaped — six
words or more, or an em-dash clause — over at least three observations. `note`,
`verbatim`, `failed_leg` and `why` are prose because the data says they are; a
field that stops being prose stops being checked, and a field that becomes prose is
covered the day it does.

WHAT IS FLAGGED, and what is deliberately not
==============================================
Flagged: `in` / `not in` against a prose value, `.startswith` / `.endswith` /
`.find` / `.index` / `.count` / `.split`, and any `re` call or compiled-pattern
method applied to one. Taint follows assignment, f-strings, concatenation and
normalisation, because `blob = f"{speaker} {note}"` is still the note.

Not flagged: `==` and `x in (a, b, c)` against the WHOLE value. Comparing a field to
a closed set of literals is reading the field, not parsing the paragraph — it is
what this rule asks for, and it is what a prose field looks like the day somebody
tightens it into an enum.

THE EXEMPTIONS ARE NAMED, DATED AND CAN ONLY SHRINK. `sources/prose_scoring_exemptions.json`
holds what was already in the tree when the rule was written, each with the queue item
that will remove it. A stale exemption — one whose code no longer violates the rule —
fails this gate too, so the list cannot quietly outlive the thing it excused.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXEMPTIONS = ROOT / "sources" / "prose_scoring_exemptions.json"

# The two scorer tests. See the docstring: by name, and by closed-vocabulary return.
SCORER_NAME = re.compile(
    r"^(score|classify|rank|grade|judge|assess|verdict|decide|rate)"
    r"|(_of|_cell|_class|_outcome|_verdict|_rung|_score)$")

# Reading a value: `e["note"]`, `e.get("note")`, `e.get("note") or ""`.
GETTERS = {"get", "setdefault", "pop"}
# Normalisation, which keeps the prose prose rather than turning it into a field.
KEEPS_TAINT = {"lower", "upper", "casefold", "strip", "lstrip", "rstrip", "replace",
               "join", "format", "title", "removeprefix", "removesuffix"}
# Matching. Every one of these asks a question of the *inside* of a string.
MATCHES = {"startswith", "endswith", "find", "rfind", "index", "rindex", "count",
           "split", "rsplit", "partition", "rpartition", "search", "match",
           "fullmatch", "findall", "finditer", "sub", "subn"}
RE_FUNCS = {"search", "match", "fullmatch", "findall", "finditer", "split", "sub",
            "subn"}


# --------------------------------------------------------------------------
# THE PROSE VOCABULARY, measured from the tracked data rather than typed.

def looks_like_prose(v: str) -> bool:
    return len(v.split()) >= 6 or " — " in v or " -- " in v


def walk_json(node, seen):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and v.strip():
                tot, pro = seen[k]
                seen[k] = (tot + 1, pro + (1 if looks_like_prose(v) else 0))
            else:
                walk_json(v, seen)
    elif isinstance(node, list):
        for v in node:
            walk_json(v, seen)


def prose_fields() -> set[str]:
    seen: dict[str, tuple[int, int]] = defaultdict(lambda: (0, 0))
    for d in ("sources", "data"):
        for p in sorted((ROOT / d).rglob("*.json")):
            if "node_modules" in p.parts or p == EXEMPTIONS:
                continue  # the register of exceptions is not evidence about the data
            try:
                walk_json(json.loads(p.read_text(encoding="utf-8")), seen)
            except (ValueError, OSError):
                continue  # a gate that reads the data is not a gate on the data
    return {k for k, (tot, pro) in seen.items() if tot >= 3 and pro / tot > 0.5}


# --------------------------------------------------------------------------
# THE TAINT WALK.

class Scan(ast.NodeVisitor):
    """One function. Which expressions are prose, and where prose is matched."""

    def __init__(self, prose: set[str], path: Path, func: str):
        self.prose, self.path, self.func = prose, path, func
        self.tainted: dict[str, str] = {}   # variable -> the field it came from
        self.hits: list[tuple[int, str, str]] = []

    # -- is this expression prose, and from which field --------------------
    def field_of(self, n) -> str | None:
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str) and n.slice.value in self.prose:
            return n.slice.value
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in GETTERS and n.args \
                and isinstance(n.args[0], ast.Constant) \
                and n.args[0].value in self.prose:
            return n.args[0].value
        if isinstance(n, ast.Attribute) and n.attr in self.prose:
            return n.attr
        if isinstance(n, ast.Name):
            return self.tainted.get(n.id)
        return None

    def source_of(self, n) -> str | None:
        """The field name if any part of the expression is prose. Taint through
        f-strings, concatenation, slices and normalising calls, because
        `f"{speaker} {note}"` is still the note and `note[:160].lower()` is too."""
        direct = self.field_of(n)
        if direct:
            return direct
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in MATCHES:
            return None          # the match itself is reported where it happens
        for c in ast.iter_child_nodes(n):
            if isinstance(c, ast.expr):
                f = self.source_of(c)
                if f:
                    return f
        return None

    # -- assignment ---------------------------------------------------------
    def visit_Assign(self, n):
        self.generic_visit(n)
        for t in n.targets:
            self._bind(t, n.value)

    def visit_AnnAssign(self, n):
        self.generic_visit(n)
        if n.value is not None:
            self._bind(n.target, n.value)

    def _bind(self, target, value):
        if isinstance(target, ast.Name):
            f = self.source_of(value)
            if f:
                self.tainted[target.id] = f
        elif isinstance(target, (ast.Tuple, ast.List)) \
                and isinstance(value, (ast.Tuple, ast.List)) \
                and len(target.elts) == len(value.elts):
            for t, v in zip(target.elts, value.elts):
                self._bind(t, v)
        elif isinstance(target, (ast.Tuple, ast.List)):
            f = self.source_of(value)
            if f:
                for t in target.elts:
                    if isinstance(t, ast.Name):
                        self.tainted[t.id] = f

    # -- the two ways prose gets matched ------------------------------------
    def visit_Compare(self, n):
        self.generic_visit(n)
        for op, right in zip(n.ops, n.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                # `"site" in leg` asks what is INSIDE the sentence.
                # `leg in ("site", "capacity")` compares the whole field: allowed.
                f = self.source_of(right)
                if f and not isinstance(right, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
                    self.hits.append((n.lineno, f, "`in` against the prose value"))

    def visit_Call(self, n):
        self.generic_visit(n)
        fn = n.func
        if isinstance(fn, ast.Attribute):
            # `<prose>.startswith(...)`, `<prose>.split(...)`
            if fn.attr in MATCHES:
                f = self.source_of(fn.value)
                if f:
                    self.hits.append((n.lineno, f, f"`.{fn.attr}()` on the prose value"))
            # `re.search(p, <prose>)`, `PATTERN.search(<prose>)`
            if fn.attr in RE_FUNCS:
                for a in n.args:
                    f = self.source_of(a)
                    if f:
                        self.hits.append(
                            (n.lineno, f, f"a pattern `.{fn.attr}()` over the prose value"))


def is_scorer(fn: ast.FunctionDef) -> str | None:
    if SCORER_NAME.search(fn.name):
        return "name"
    rets = [n.value for n in ast.walk(fn) if isinstance(n, ast.Return)]
    lits = {r.value for r in rets
            if isinstance(r, ast.Constant) and isinstance(r.value, str)}
    if rets and len(lits) >= 2 and all(
            isinstance(r, ast.Constant) and isinstance(r.value, str) for r in rets):
        return "closed vocabulary"
    return None


def scan_file(path: Path, prose: set[str]):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [(path, 0, "-", exc.lineno or 0, "-", f"does not parse: {exc.msg}")]
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        why = is_scorer(fn)
        if not why:
            continue
        s = Scan(prose, path, fn.name)
        for st in fn.body:
            s.visit(st)
        for line, field, what in s.hits:
            out.append((path, fn.lineno, fn.name, line, field, f"{what} ({why})"))
    return out


def main() -> int:
    prose = prose_fields()
    hits = []
    for p in sorted((ROOT / "sources").glob("*.py")):
        if p.name == Path(__file__).name:
            continue
        hits.extend(scan_file(p, prose))

    allowed = {}
    if EXEMPTIONS.exists():
        for e in json.loads(EXEMPTIONS.read_text(encoding="utf-8"))["exemptions"]:
            allowed[(e["file"], e["function"], e["field"])] = e

    live, used = [], set()
    for path, _fl, func, line, field, what in hits:
        key = (str(path.relative_to(ROOT)), func, field)
        if key in allowed:
            used.add(key)
            continue
        live.append((key[0], func, line, field, what))

    stale = [k for k in allowed if k not in used]

    print(f"check_prose_scoring: {len(prose)} prose fields measured from the tracked "
          f"data; {len(hits)} match(es) on one inside a scorer, {len(allowed)} exempt.")
    if live:
        print(f"\n{len(live)} scorer(s) read the paragraph rather than the field:")
        for f, func, line, field, what in live:
            print(f"  {f}:{line}  {func}()  —  {what}, field `{field}`")
        print("\nA verdict is decided on a typed field. If the fact lives only in "
              "prose, give the record a field. See sources/scope.md, \"A scorer reads "
              "typed fields, and never the prose\".")
    if stale:
        print(f"\n{len(stale)} exemption(s) no longer describe anything:")
        for f, func, field in stale:
            print(f"  {f}  {func}()  field `{field}` — remove it from "
                  f"prose_scoring_exemptions.json")
    if live or stale:
        return 1
    print("check_prose_scoring: OK — no scorer decides a verdict by reading a sentence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

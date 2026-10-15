"""
Every heading on a sector page is a reviewed template, and every sector can
fill it.

    python3 check_h2_templates.py           # exits non-zero on any violation

THREE THINGS, ONE FILE
======================
1  Every H2 in the sector template resolves to a template in data/prose.json.
   No free text, including the unnumbered one: an exception carved for a single
   heading is an exception somebody widens.
2  Every one of the six ecosystem instances has both name slots -- `short` and
   `phrase` -- filled. These are not optional prose. Unlike an ecosystem
   description, which a surface can render nothing for, a name slot is the
   SUBJECT of nine headings, and a page cannot be missing its subject.
3  Every template, filled with every sector's slots, comes out as a sentence:
   no slot left unsubstituted, no slot the renderer does not know.

WHY 2 IS CHECKED AGAINST THE ECOSYSTEMS FILE and not against the sector spine:
the slots are keyed on instance because chemicals spans two FIGARO slugs and
batteries covers part of one (see the note in data/prose.json). The set that
has to be complete is therefore the six, and a seventh instance arriving with
no name slots should fail here on the day it is added rather than on the day
somebody builds its page.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROSE = ROOT / "data" / "prose.json"
ECOSYSTEMS = ROOT / "data" / "transition" / "ecosystems.json"
TEMPLATE = ROOT / "web" / "components" / "SectorMap.tsx"
# The four block headings do not appear in the template: the blocks render
# through one component, which is handed the heading the template looked up. So
# the chain has two more links and both are checked here -- that the template
# passes h2(block.id), and that the component renders that prop and no wording
# of its own. Without these two, brief 15 would have quietly taken four of the
# five headings out of this gate's sight.
BLOCK_COMPONENT = ROOT / "web" / "components" / "HubBlock.tsx"

# The two slots a heading may take, and nothing else. Kept here rather than
# inferred from the templates, because the renderer in web/lib/sitetext.ts
# knows exactly these two and a third one would throw at build time.
SLOTS = ("short", "phrase")

H2 = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.S)
# The two shapes a heading may take in the template: a numbered section's
# question, and the one unnumbered heading.
CALL = re.compile(r'^\{(?:h2|getUnnumberedH2)\("([a-z-]+)"\)\}$')


def fill(template: str, names: dict) -> tuple[str, list[str]]:
    """The heading with its slots filled, and any slot the renderer would
    reject. Mirrors renderHeading() in web/lib/sitetext.ts, including the rule
    that `phrase` is capitalised only where it opens the heading."""
    unknown: list[str] = []

    def sub(m: re.Match[str]) -> str:
        slot = m.group(1)
        key = slot.lower()
        if key not in SLOTS:
            unknown.append(slot)
            return m.group(0)
        value = names[key]
        if m.start() == 0 or slot[0].isupper():
            return value[:1].upper() + value[1:]
        return value

    return re.sub(r"\{([A-Za-z_]+)\}", sub, template), unknown


def main() -> int:
    prose = json.loads(PROSE.read_text(encoding="utf-8"))
    problems: list[str] = []

    block = prose.get("sector_sections")
    names_block = prose.get("sector_names")
    if not block or not names_block:
        print("check_h2_templates: data/prose.json is missing sector_sections or "
              "sector_names")
        return 1

    for label, b in (("sector_sections", block), ("sector_names", names_block)):
        if b.get("status") not in ("approved", "final"):
            problems.append(
                f"{label} is {b.get('status')!r}. Every other prose block on this site "
                f"falls back to computed text while it is a draft; these two have no "
                f"fallback, because there is no computed form of a sector's own name")

    sections = block.get("sections") or []
    unnumbered = block.get("unnumbered") or []
    by_id = {s["id"]: s for s in sections}
    unnumbered_by_id = {u["id"]: u for u in unnumbered}

    for s in sections:
        for field in ("id", "nav", "h2"):
            if not (s.get(field) or "").strip():
                problems.append(f"section {s.get('id', '?')!r} has an empty {field}")
    for u in unnumbered:
        if not (u.get("h2") or "").strip():
            problems.append(f"unnumbered heading {u.get('id', '?')!r} has no h2")

    # ---- the six have their slots -----------------------------------------
    instances = [e["id"] for e in
                 json.loads(ECOSYSTEMS.read_text(encoding="utf-8"))["ecosystems"]]
    slots = names_block.get("sectors") or {}
    for eco in instances:
        row = slots.get(eco)
        if not row:
            problems.append(f"ecosystem {eco!r} has no entry in sector_names, so no "
                            f"heading on its page has a subject")
            continue
        for slot in SLOTS:
            if not (row.get(slot) or "").strip():
                problems.append(f"ecosystem {eco!r} has an empty {slot!r} name slot")
    for extra in sorted(set(slots) - set(instances)):
        problems.append(
            f"sector_names carries {extra!r}, which is not an ecosystem instance in "
            f"data/transition/ecosystems.json")

    # ---- the slugs no instance claims -------------------------------------
    # `sector_slots` answers for a sector that renders the hub and that no
    # ecosystem reaches by a sector edge: `clean`, because the hydrogen instance
    # deliberately carries none, and `ccs`, because CO2 transport and storage is
    # not an ecosystem. TWO SHAPES AND ONLY TWO -- an entry borrows an
    # instance's slots or carries its own. Both is a name with two sources of
    # truth, which is a name that drifts; neither is a sector with no subject.
    sector_slots = names_block.get("sector_slots") or {}
    resolved: dict[str, dict] = {}
    drafted: set[str] = set()
    for slug, row in sorted(sector_slots.items()):
        if slug == "_comment":
            continue
        instance = (row.get("instance") or "").strip()
        own = {s: (row.get(s) or "").strip() for s in SLOTS}
        if instance and any(own.values()):
            problems.append(
                f"sector_slots[{slug!r}] names the instance {instance!r} AND carries "
                f"slots of its own. One or the other: two sources of truth for one "
                f"name is a name that drifts")
            continue
        if instance:
            if instance not in slots:
                problems.append(
                    f"sector_slots[{slug!r}] names the instance {instance!r}, which has "
                    f"no entry in sector_names.sectors")
                continue
            resolved[slug] = slots[instance]
            continue
        if not all(own.values()):
            problems.append(
                f"sector_slots[{slug!r}] names no instance and has an empty "
                f"{', '.join(s for s in SLOTS if not own[s])!r} slot, so no heading on "
                f"its page has a subject")
            continue
        resolved[slug] = own
        # WHICH OF THESE ACTUALLY RENDERS. Since George's ruling of 15 October
        # 2026 a draft slot renders nothing and web/lib/sectorSections.ts
        # computedSectorNames supplies the heading instead, so an entry checked
        # here may be wording no reader is seeing yet. The templates are filled
        # for it either way — a draft has to be ready on the day it is approved —
        # and the print below says which state each one is in, so this gate's own
        # output cannot imply that a draft is on the page.
        if row.get("status") is not None and row["status"] not in ("approved", "final"):
            drafted.add(slug)

    # ---- every template fills for those too -------------------------------
    for slug, row in sorted(resolved.items()):
        for template in [block["h1"]] + [s["h2"] for s in sections]:
            filled, unknown = fill(template, row)
            for slot in unknown:
                problems.append(
                    f"heading {template!r} takes a slot {{{slot}}}, and the only slots "
                    f"a heading takes are {{short}} and {{phrase}}")
            if "{" in filled or "}" in filled:
                problems.append(f"{slug}: {template!r} still has a brace in it after "
                                f"filling: {filled!r}")

    # ---- every template fills, for every sector ---------------------------
    for eco in instances:
        row = slots.get(eco) or {}
        if not all((row.get(s) or "").strip() for s in SLOTS):
            continue  # already reported
        for template in [block["h1"]] + [s["h2"] for s in sections]:
            filled, unknown = fill(template, row)
            for slot in unknown:
                problems.append(
                    f"heading {template!r} takes a slot {{{slot}}}, and the only slots "
                    f"a heading takes are {{short}} and {{phrase}}")
            if "{" in filled or "}" in filled:
                problems.append(f"{eco}: {template!r} still has a brace in it after "
                                f"filling: {filled!r}")

    # ---- no free text in the template -------------------------------------
    tsx = TEMPLATE.read_text(encoding="utf-8")
    for raw in H2.findall(tsx):
        text = " ".join(raw.split())
        m = CALL.match(text)
        if not m:
            problems.append(
                f"<h2>{text}</h2> in {TEMPLATE.name} is not a template lookup. Every "
                f"heading on this page is reviewed wording in data/prose.json, "
                f'rendered as {{h2("id")}} or {{getUnnumberedH2("id")}}')
            continue
        section_id = m.group(1)
        if section_id not in by_id and section_id not in unnumbered_by_id:
            problems.append(
                f'the template asks for the heading of "{section_id}", which is not a '
                f"section in data/prose.json")

    # ---- the block headings, through the component ------------------------
    if not re.search(r"heading=\{h2\(block\.id\)\}", tsx):
        problems.append(
            f"{TEMPLATE.name} does not hand each block h2(block.id). A block heading "
            f"that came from anywhere else is free text with a lookup standing beside "
            f"it")
    hubtsx = BLOCK_COMPONENT.read_text(encoding="utf-8")
    hub_h2 = [" ".join(raw.split()) for raw in H2.findall(hubtsx)]
    if hub_h2 != ["{heading}"]:
        problems.append(
            f"{BLOCK_COMPONENT.name} renders {hub_h2!r} as its heading(s). It renders "
            f"exactly one, and it is the `heading` prop: a block that wrote its own "
            f"wording would be four headings this gate cannot see")

    # ---- the country view's heading, filled for every sector and country ----
    # Added 15 October 2026. The template lives in its own block because it takes
    # a third slot, and nothing was holding it to the same standard as the five
    # above: a brace left in it would have reached 29 pages.
    country = prose.get("country_pages") or {}
    country_h1 = (country.get("h1") or "").strip()
    if not country_h1:
        problems.append("country_pages has no h1, so a country view has no heading")
    else:
        names = {s: "x" for s in SLOTS}
        names["country"] = "Germany"
        filled = re.sub(r"\{([A-Za-z_]+)\}",
                        lambda m: names.get(m.group(1).lower(), m.group(0)), country_h1)
        if "{" in filled or "}" in filled:
            problems.append(
                f"country_pages.h1 {country_h1!r} still has a brace in it after "
                f"filling; the only slots it takes are {{short}}, {{phrase}} and "
                f"{{country}}")

    if problems:
        print(f"check_h2_templates: {len(problems)} violations\n")
        for p in problems:
            print(f"  {p}")
        return 1

    example = slots[instances[0]]
    print(f"check_h2_templates: OK — {len(sections)} questions and "
          f"{len(unnumbered)} unnumbered heading(s), all templated; "
          f"{len(instances)} ecosystems with both name slots, "
          f"{len(resolved)} sector slug(s) named outside an instance. "
          f"{instances[0]}: {fill(block['h1'], example)[0]!r}")
    for slug, row in sorted(resolved.items()):
        state = ("DRAFT, not rendering — the page heads itself from the computed "
                 "fallback" if slug in drafted else "approved and rendering")
        print(f"  {slug}: {fill(block['h1'], row)[0]!r}  [{state}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

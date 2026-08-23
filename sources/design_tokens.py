"""
The design tokens, read from the stylesheet that defines them.

    import design_tokens as dt
    dt.tokens()["--dg-measure"]   -> "#a1662f"

WHY PYTHON READS THE CSS
========================
Two build-side jobs need the palette: the colour gate, which measures it, and
the static diagram writer, which bakes it into standalone SVG files that ship
without a stylesheet. Both could carry their own copy of the hexes. Neither
should: a second copy of a colour is a colour that will disagree with the first
one, and the whole point of the gate is that a hue cannot quietly drift.

So globals.css stays the single definition and this reads it. The parse is
deliberately small -- :root, custom properties, hex values, one level of alias
following -- because anything cleverer would be a CSS parser, and a CSS parser
is a dependency this repository does not need to have an opinion about.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "web" / "app" / "globals.css"

_cache: dict[str, str] | None = None


def tokens(path: Path | None = None) -> dict[str, str]:
    """Every :root custom property that resolves to a literal hex colour.

    An alias (`--focus: var(--signal)`) is followed to its value. A token whose
    value is not a colour -- the type stacks, the metrics -- is simply absent,
    which is what every caller here wants.
    """
    global _cache
    if path is None and _cache is not None:
        return _cache
    css = (path or CSS).read_text(encoding="utf-8")
    block = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not block:
        raise SystemExit(f"design_tokens: no :root block in {path or CSS}")
    raw = {name: value.strip() for name, value in
           re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block.group(1))}
    out: dict[str, str] = {}
    for name, value in raw.items():
        hops = 0
        while value.startswith("var(") and hops < 4:
            value = raw.get(value[4:].split(",")[0].strip().rstrip(")"), "").strip()
            hops += 1
        if re.fullmatch(r"#[0-9a-fA-F]{3,8}", value):
            out[name] = value
    if path is None:
        _cache = out
    return out


def require(*names: str) -> dict[str, str]:
    """Tokens a caller cannot run without, with a failure that names the gap."""
    have = tokens()
    missing = [n for n in names if n not in have]
    if missing:
        raise SystemExit(
            f"design_tokens: {missing} not defined in {CSS.relative_to(ROOT)} — a build "
            f"step needs them as literals and will not invent them")
    return {n: have[n] for n in names}

#!/usr/bin/env python3
"""Export the diagrams in skills/automation/workflow.html as standalone SVG files.

Each SVG carries its own styles (light and dark colours), so GitHub shows it
correctly in the README in either theme. Run after editing workflow.html:

    python tools/export_workflow_svgs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills" / "automation" / "workflow.html"
OUT_DIR = ROOT / "docs" / "images"
NAMES = ["workflow.svg", "daily-update.svg"]
FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'


def main() -> int:
    html = SOURCE.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    # Keep the colour tokens and the diagram rules; drop page-only rules.
    css = "\n".join(
        line for line in css.splitlines()
        if not re.match(r"\s*(body|main|h1|h2|p|svg|svg text)\s*\{", line)
    )
    css += f"\nsvg {{ font-family: {FONT}; }}\n.bg {{ fill: var(--bg); }}\n"
    svgs = re.findall(r"<svg\b.*?</svg>", html, re.S)
    if len(svgs) != len(NAMES):
        print(f"expected {len(NAMES)} diagrams in {SOURCE}, found {len(svgs)}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in zip(NAMES, svgs):
        _, _, w, h = re.search(r'viewBox="([^"]+)"', svg).group(1).split()
        svg = svg.replace(
            "<svg ",
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" ',
            1,
        )
        # Styles first, then a full-size background so text stays readable on any page colour.
        svg = re.sub(
            r"(<svg\b[^>]*>)",
            lambda m: f'{m.group(1)}<style>{css}</style><rect class="bg" width="100%" height="100%"/>',
            svg,
            count=1,
        )
        (OUT_DIR / name).write_text(svg + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {(OUT_DIR / name).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

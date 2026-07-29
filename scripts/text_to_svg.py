"""
Convert raw ASCII art text into an animated SVG with typewriter effect.
Reads from ascii_art.txt and outputs pranav-ascii.svg.
"""
from pathlib import Path
import sys

# SVG parameters
FONT_SIZE = 4.0
LINE_HEIGHT = 4.6
CHAR_WIDTH = 2.4
BG_COLOR = "#000"
TEXT_COLOR = "#b0b0b0"
FONT_FAMILY = "'Courier New', monospace"


def generate_svg(ascii_lines: list[str], output_path: str):
    num_lines = len(ascii_lines)
    max_chars = max(len(line) for line in ascii_lines)

    svg_width = int(max_chars * CHAR_WIDTH + 20)
    svg_height = int(num_lines * LINE_HEIGHT + 20)

    line_delay = 0.04
    type_duration = 0.3

    css = ["    <style>"]
    css.append("      @keyframes typeIn { from { width: 0; } to { width: 100%; } }")
    for i in range(num_lines):
        d = i * line_delay
        css.append(f"      .l{i} {{ animation: typeIn {type_duration}s steps({max_chars}) {d:.2f}s forwards; overflow: hidden; white-space: nowrap; width: 0; }}")
    css.append("    </style>")

    body = []
    for i, line in enumerate(ascii_lines):
        y = 10 + (i * LINE_HEIGHT)
        esc = (line.replace("&", "&amp;").replace("<", "&lt;")
               .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;"))
        body.append(f'    <clipPath id="c{i}"><rect class="l{i}" x="0" y="{y - FONT_SIZE:.1f}" width="{svg_width}" height="{LINE_HEIGHT + 2:.1f}"/></clipPath>')
        body.append(f'    <text x="10" y="{y:.1f}" clip-path="url(#c{i})">{esc}</text>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <rect width="100%" height="100%" fill="{BG_COLOR}"/>
{chr(10).join(css)}
  <g font-family="{FONT_FAMILY}" font-size="{FONT_SIZE}px" fill="{TEXT_COLOR}">
{chr(10).join(body)}
  </g>
</svg>"""

    Path(output_path).write_text(svg, encoding="utf-8")
    print(f"[OK] {output_path} ({svg_width}x{svg_height}, {num_lines} lines, {max_chars} cols)")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "ascii_art.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "pranav-ascii.svg"
    
    text = Path(input_file).read_text(encoding="utf-8")
    lines = text.rstrip("\n").split("\n")
    # Remove empty trailing lines
    while lines and not lines[-1].strip():
        lines.pop()
    generate_svg(lines, output_file)

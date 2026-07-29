"""
Generate a large 3D extruded ASCII wordmark SVG with wipe-in and rocking animation.
This version creates a much bigger, more impressive wordmark matching the AVIVASHISHTA29 style.
"""

import sys
from pathlib import Path

# Large FIGlet-style block letters - each is 12 lines tall
BIG_LETTERS = {
    "P": [
        "PPPPPPPPPPPP   ",
        "PP         PP  ",
        "PP         PP  ",
        "PP         PP  ",
        "PPPPPPPPPPPP   ",
        "PP             ",
        "PP             ",
        "PP             ",
        "PP             ",
        "PP             ",
        "PP             ",
        "               ",
    ],
    "R": [
        "RRRRRRRRRRRR   ",
        "RR         RR  ",
        "RR         RR  ",
        "RR         RR  ",
        "RRRRRRRRRRRR   ",
        "RR    RR       ",
        "RR     RR      ",
        "RR      RR     ",
        "RR       RR    ",
        "RR        RR   ",
        "RR         RR  ",
        "               ",
    ],
    "A": [
        "      AA       ",
        "     AAAA      ",
        "    AA  AA     ",
        "   AA    AA    ",
        "  AA      AA   ",
        " AAAAAAAAAAAA  ",
        " AA          AA",
        "AA            AA",
        "AA            AA",
        "AA            AA",
        "AA            AA",
        "               ",
    ],
    "N": [
        "NN          NN ",
        "NNN         NN ",
        "NNNN        NN ",
        "NN NN       NN ",
        "NN  NN      NN ",
        "NN   NN     NN ",
        "NN    NN    NN ",
        "NN     NN   NN ",
        "NN      NN  NN ",
        "NN       NN NN ",
        "NN        NNNN ",
        "               ",
    ],
    "V": [
        "VV            VV",
        "VV            VV",
        " VV          VV ",
        " VV          VV ",
        "  VV        VV  ",
        "  VV        VV  ",
        "   VV      VV   ",
        "   VV      VV   ",
        "    VV    VV    ",
        "     VV  VV     ",
        "      VVVV      ",
        "                ",
    ],
}


def make_block_text(name: str) -> list[str]:
    """Combine block letters into multi-line text for a name."""
    height = 12
    lines = []
    for row in range(height):
        line = ""
        for char in name.upper():
            if char in BIG_LETTERS:
                letter_row = BIG_LETTERS[char][row]
                line += letter_row + "   "
            elif char == " ":
                line += "               "
        lines.append(line.rstrip())
    return lines


def generate_wordmark_svg(name: str, output_path: str):
    """Generate a 3D extruded wordmark SVG with animations."""
    block_lines = make_block_text(name)
    num_lines = len(block_lines)
    max_chars = max(len(line) for line in block_lines)

    # SVG parameters - much larger font for impressive look
    font_size = 6.0
    line_height = 7.0
    char_width = 3.6

    # 3D offset
    shadow_dx = 3
    shadow_dy = 3

    # Colors
    front_color = "#d0d0d0"
    shadow_color = "#555555"
    bg_color = "#000"

    svg_width = int(max_chars * char_width + 60 + shadow_dx)
    svg_height = int(num_lines * line_height + 60 + shadow_dy)

    # Wipe-in animation timing
    wipe_start = 0.4
    wipe_end = 1.4
    wipe_duration = wipe_end - wipe_start

    css = f"""
    <style>
      @keyframes wipeIn {{
        from {{ clip-path: inset(0 100% 0 0); }}
        to {{ clip-path: inset(0 0% 0 0); }}
      }}
      @keyframes rockY {{
        0% {{ transform: skewY(0deg); }}
        25% {{ transform: skewY(1.5deg); }}
        50% {{ transform: skewY(0deg); }}
        75% {{ transform: skewY(-1.5deg); }}
        100% {{ transform: skewY(0deg); }}
      }}
      .wordmark {{
        animation: wipeIn {wipe_duration}s ease {wipe_start}s forwards,
                   rockY 4s ease-in-out {wipe_end}s infinite;
        clip-path: inset(0 100% 0 0);
        transform-origin: center center;
      }}
    </style>"""

    # Build text elements
    shadow_texts = []
    front_texts = []

    for i, line in enumerate(block_lines):
        y = 30 + (i * line_height)
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        shadow_texts.append(
            f'    <text x="{30 + shadow_dx}" y="{y + shadow_dy}">{escaped}</text>'
        )
        front_texts.append(
            f'    <text x="30" y="{y}">{escaped}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <rect width="100%" height="100%" fill="{bg_color}" />
  {css}
  <g class="wordmark" font-family="'Courier New', monospace" font-size="{font_size}px" letter-spacing="0px">
    <g class="shadow" fill="{shadow_color}">
{chr(10).join(shadow_texts)}
    </g>
    <g class="front" fill="{front_color}">
{chr(10).join(front_texts)}
    </g>
  </g>
</svg>"""

    Path(output_path).write_text(svg, encoding="utf-8")
    print(f"[OK] Wordmark SVG written to {output_path} ({svg_width}x{svg_height})")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "PRANAV"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "wordmark.svg"
    generate_wordmark_svg(name, output_path)

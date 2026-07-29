"""
Convert a photo into a high-detail monochrome ASCII-art SVG with typewriter animation.

Full-scene version: minimal cropping, high resolution for maximum detail.

Usage:
    python make_ascii_svg.py <input_image> [output.svg]
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    print("Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

import numpy as np

# 15-char ramp: space (dark/invisible on black bg) → @ (bright/dense)
RAMP = " .,:;i1tfLCG08@"

# SVG parameters — smaller font = more detail
FONT_SIZE = 4.2
LINE_HEIGHT = 4.8
CHAR_WIDTH = 2.52
BG_COLOR = "#000"
TEXT_COLOR = "#b0b0b0"
FONT_FAMILY = "'Courier New', monospace"

# High resolution for maximum detail
TARGET_WIDTH = 150   # characters per line
TARGET_LINES = 120   # max lines


def image_to_ascii(image_path: str, width: int = TARGET_WIDTH, max_height: int = TARGET_LINES) -> list[str]:
    """Convert full image to detailed ASCII art."""
    img = Image.open(image_path)

    # Minimal crop — just trim tiny margins, keep full scene
    w, h = img.size
    crop_left = int(w * 0.02)
    crop_top = int(h * 0.01)
    crop_right = int(w * 0.98)
    crop_bottom = int(h * 0.99)
    img = img.crop((crop_left, crop_top, crop_right, crop_bottom))

    # Grayscale
    img = img.convert("L")

    # Auto-contrast: full range stretch
    img = ImageOps.autocontrast(img, cutoff=0.5)

    # Strong contrast boost — crucial for dark photos
    img = ImageEnhance.Contrast(img).enhance(1.6)

    # Brightness boost
    img = ImageEnhance.Brightness(img).enhance(1.3)

    # Sharpen twice — brings out edges of glasses, cans, laptop, shirt stripes
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.DETAIL)

    # Resize preserving aspect ratio for monospace chars
    aspect = img.height / img.width
    char_aspect = LINE_HEIGHT / CHAR_WIDTH
    height = int(width * aspect / char_aspect)
    height = min(height, max_height)

    img = img.resize((width, height), Image.Resampling.LANCZOS)

    pixels = np.array(img, dtype=np.float64) / 255.0

    # Gentle gamma to lift midtones
    pixels = np.power(np.clip(pixels, 0, 1), 0.85)

    ramp = RAMP
    ramp_len = len(ramp)

    lines = []
    for row in pixels:
        chars = []
        for val in row:
            idx = int(val * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            chars.append(ramp[idx])
        lines.append("".join(chars))

    return lines


def generate_svg(ascii_lines: list[str], output_path: str):
    """Generate SVG with typewriter animation."""
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
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_image> [output.svg]")
        sys.exit(1)
    lines = image_to_ascii(sys.argv[1])
    generate_svg(lines, sys.argv[2] if len(sys.argv) > 2 else "pranav-ascii.svg")

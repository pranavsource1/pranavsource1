"""
Generate an animated GitHub contribution heatmap SVG using REAL contribution data.

Fetches actual contribution data from GitHub's public contributions endpoint.

Usage:
    python make_contrib_heatmap_svg.py <username> [output.svg]
"""

import sys
import re
from pathlib import Path
from datetime import datetime

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass


def fetch_real_contributions(username: str) -> list[dict]:
    """
    Fetch real contribution data from GitHub's public contributions page.
    Returns list of {date, count, level} dicts.
    """
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; contrib-heatmap/1.0)"}

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"[ERROR] Could not fetch contributions for {username}: {e}")
        sys.exit(1)

    # Parse contribution cells from the HTML
    # GitHub returns <td> elements with data-date and data-level attributes
    # Pattern: data-date="2024-01-15" data-level="2"
    # Also look for: <tool-tip ...>N contributions on ...
    cells = []

    # Match table cells with contribution data
    td_pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"',
        re.DOTALL
    )

    # Also try to get contribution counts from tooltips
    count_pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})".*?'
        r'(?:(\d+)\s+contribution|No\s+contribution)',
        re.DOTALL
    )

    # First pass: get dates and levels
    date_levels = {}
    for match in td_pattern.finditer(html):
        date_str = match.group(1)
        level = int(match.group(2))
        date_levels[date_str] = {"date": date_str, "level": level, "count": 0}

    # Second pass: try to get actual counts
    # Look for tooltip text patterns
    tooltip_pattern = re.compile(
        r'(\d+)\s+contributions?\s+on\s+\w+,\s+(\w+\s+\d+,\s+\d{4})'
    )
    no_contrib_pattern = re.compile(
        r'No\s+contributions?\s+on\s+\w+,\s+(\w+\s+\d+,\s+\d{4})'
    )

    # If we got date_levels, use them
    if date_levels:
        # Sort by date
        cells = sorted(date_levels.values(), key=lambda x: x["date"])
        print(f"[OK] Fetched {len(cells)} days of real contribution data for {username}")
    else:
        print(f"[WARN] Could not parse contribution data, trying alternate format...")
        # Try alternate parsing for newer GitHub HTML format
        rect_pattern = re.compile(
            r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"'
        )
        for match in rect_pattern.finditer(html):
            date_str = match.group(1)
            level = int(match.group(2))
            cells.append({"date": date_str, "level": level, "count": 0})

        if cells:
            cells.sort(key=lambda x: x["date"])
            print(f"[OK] Fetched {len(cells)} days (alternate parse) for {username}")
        else:
            print(f"[ERROR] Could not parse any contribution data from GitHub")
            print(f"[DEBUG] First 2000 chars of response:\n{html[:2000]}")
            sys.exit(1)

    return cells


def organize_into_weeks(cells: list[dict]) -> list[list[dict]]:
    """Organize contribution cells into weeks (columns) for the heatmap grid."""
    if not cells:
        return []

    weeks = []
    current_week = []

    for cell in cells:
        dt = datetime.strptime(cell["date"], "%Y-%m-%d")
        weekday = dt.weekday()  # 0=Mon, 6=Sun

        # GitHub calendar: Sunday=0, so convert
        gh_weekday = (weekday + 1) % 7  # Sun=0, Mon=1, ..., Sat=6

        if gh_weekday == 0 and current_week:
            weeks.append(current_week)
            current_week = []

        current_week.append({"day": gh_weekday, "level": cell["level"], "date": cell["date"]})

    if current_week:
        weeks.append(current_week)

    return weeks


def generate_heatmap_svg(username: str, output_path: str):
    """Generate the real contribution heatmap SVG."""
    cells = fetch_real_contributions(username)
    weeks = organize_into_weeks(cells)

    # Colors (GitHub's green scale on dark theme)
    LEVEL_COLORS = {
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353",
    }
    BG_COLOR = "#0d1117"

    # Grid parameters
    cell_size = 13
    cell_gap = 3
    cell_total = cell_size + cell_gap
    margin_left = 40
    margin_top = 30
    margin_right = 20
    margin_bottom = 30

    num_weeks = len(weeks)
    days = 7

    svg_width = margin_left + num_weeks * cell_total + margin_right
    svg_height = margin_top + days * cell_total + margin_bottom

    elements = []

    # Month labels
    current_month = -1
    for w, week in enumerate(weeks):
        if week:
            dt = datetime.strptime(week[0]["date"], "%Y-%m-%d")
            if dt.month != current_month:
                current_month = dt.month
                x = margin_left + w * cell_total
                elements.append(
                    f'  <text x="{x}" y="{margin_top - 8}" '
                    f'font-family="\'Segoe UI\', sans-serif" font-size="11" fill="#848d97">{dt.strftime("%b")}</text>'
                )

    # Day labels
    day_names = {1: "Mon", 3: "Wed", 5: "Fri"}
    for d, label in day_names.items():
        y = margin_top + d * cell_total + cell_size - 2
        elements.append(
            f'  <text x="{margin_left - 8}" y="{y}" '
            f'font-family="\'Segoe UI\', sans-serif" font-size="10" fill="#848d97" '
            f'text-anchor="end">{label}</text>'
        )

    # Contribution cells with staggered pop-in animation
    cell_index = 0
    for w, week in enumerate(weeks):
        for cell in week:
            d = cell["day"]
            level = cell["level"]
            color = LEVEL_COLORS.get(level, LEVEL_COLORS[0])
            x = margin_left + w * cell_total
            y = margin_top + d * cell_total
            delay = cell_index * 0.003

            elements.append(
                f'  <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                f'rx="2" ry="2" fill="{color}" '
                f'style="animation: popIn 0.25s ease {delay:.3f}s both;" />'
            )
            cell_index += 1

    # Legend
    legend_x = svg_width - margin_right - 120
    legend_y = svg_height - 15
    elements.append(
        f'  <text x="{legend_x}" y="{legend_y}" '
        f'font-family="\'Segoe UI\', sans-serif" font-size="10" fill="#848d97">Less</text>'
    )
    for i in range(5):
        lx = legend_x + 30 + i * (cell_size + 2)
        elements.append(
            f'  <rect x="{lx}" y="{legend_y - 10}" width="{cell_size}" height="{cell_size}" '
            f'rx="2" ry="2" fill="{LEVEL_COLORS[i]}" />'
        )
    elements.append(
        f'  <text x="{legend_x + 30 + 5 * (cell_size + 2) + 5}" y="{legend_y}" '
        f'font-family="\'Segoe UI\', sans-serif" font-size="10" fill="#848d97">More</text>'
    )

    css = """
    <style>
      @keyframes popIn {
        from { transform: scale(0); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
      rect { transform-box: fill-box; transform-origin: center; }
    </style>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="6" />
  {css}
{chr(10).join(elements)}
</svg>"""

    Path(output_path).write_text(svg, encoding="utf-8")
    print(f"[OK] Heatmap written to {output_path} ({svg_width}x{svg_height}, {cell_index} cells)")


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "pranavsource1"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
    generate_heatmap_svg(username, output_path)

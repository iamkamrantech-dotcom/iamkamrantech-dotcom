#!/usr/bin/env python3
"""
render_heatmap_svg.py
---------------------
data/contributions.json ko parh kar animated SVG heatmap banata hai
(53 hafte x 7 din, rounded boxes, diagonal reveal animation).

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
import os
from datetime import datetime

IN_PATH = os.path.join("data", "contributions.json")
OUT_PATH = "contrib-heatmap.svg"

# --- look & feel ------------------------------------------------------------
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
BORDER = "#21262d"
TEXT = "#8b949e"
TEXT_BRIGHT = "#c9d1d9"
ACCENT = "#39d353"

CELL = 12          # box ka size
GAP = 3            # boxes ke darmiyan gap
RADIUS = 2.5
PAD_L = 34         # left me Mon/Wed/Fri labels ki jagah
PAD_T = 46         # upar title + month labels
PAD_R = 18
PAD_B = 46         # neeche legend + stats
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build(data):
    days = data["days"]

    # har din ko (week, weekday) grid position do
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    first_col_offset = (first.weekday() + 1) % 7  # GitHub: Sunday = row 0

    cells = []
    for i, d in enumerate(days):
        idx = i + first_col_offset
        cells.append((idx // 7, idx % 7, d))  # (week, weekday, day)

    weeks = max(c[0] for c in cells) + 1
    grid_w = weeks * (CELL + GAP) - GAP
    grid_h = 7 * (CELL + GAP) - GAP
    W = PAD_L + grid_w + PAD_R
    H = PAD_T + grid_h + PAD_B

    # ---- animation: har box ka apna delay (diagonal wave) -------------------
    max_delay = 0.0
    parts = []
    for week, wd, d in cells:
        x = PAD_L + week * (CELL + GAP)
        y = PAD_T + wd * (CELL + GAP)
        lvl = min(d["level"], len(PALETTE) - 1)
        if d["count"] >= 25 and lvl >= 4:
            lvl = 5  # neon top-end
        delay = (week * 0.018) + (wd * 0.035)
        max_delay = max(max_delay, delay)
        title = f'{d["count"]} contributions on {d["date"]}'
        parts.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="{RADIUS}" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{esc(title)}</title></rect>'
        )

    # ---- month labels ------------------------------------------------------
    month_labels = []
    seen = set()
    for week, wd, d in cells:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        key = (dt.year, dt.month)
        if key in seen or dt.day > 7:
            continue
        seen.add(key)
        x = PAD_L + week * (CELL + GAP)
        month_labels.append(
            f'<text x="{x}" y="{PAD_T - 8}" class="lbl">{MONTHS[dt.month - 1]}</text>'
        )

    # ---- weekday labels ----------------------------------------------------
    wd_labels = []
    for wd, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = PAD_T + wd * (CELL + GAP) + CELL - 2
        wd_labels.append(f'<text x="4" y="{y}" class="lbl">{name}</text>')

    # ---- legend ------------------------------------------------------------
    legend_y = PAD_T + grid_h + 20
    lx = W - PAD_R - (len(PALETTE) * (CELL + GAP)) - 62
    legend = [f'<text x="{lx - 6}" y="{legend_y + 10}" class="lbl" text-anchor="end">Less</text>']
    for i, col in enumerate(PALETTE):
        legend.append(
            f'<rect x="{lx + i * (CELL + GAP)}" y="{legend_y}" width="{CELL}" '
            f'height="{CELL}" rx="{RADIUS}" fill="{col}"/>'
        )
    legend.append(
        f'<text x="{lx + len(PALETTE) * (CELL + GAP) + 6}" y="{legend_y + 10}" class="lbl">More</text>'
    )

    # ---- footer stats ------------------------------------------------------
    st = data["stats"]
    footer = (
        f'<text x="{PAD_L}" y="{legend_y + 10}" class="stat">'
        f'<tspan class="hi">{data["total"]:,}</tspan> contributions'
        f'<tspan dx="14" class="dim">·</tspan>'
        f'<tspan dx="14">streak </tspan><tspan class="hi">{st["current_streak"]}d</tspan>'
        f'<tspan dx="14" class="dim">·</tspan>'
        f'<tspan dx="14">best </tspan><tspan class="hi">{st["longest_streak"]}d</tspan>'
        f'</text>'
    )

    title = (
        f'<text x="{PAD_L}" y="26" class="title">'
        f'<tspan class="prompt">@{esc(data["username"])}</tspan>'
        f'<tspan dx="10" class="dim">~ contribution graph</tspan></text>'
    )

    reveal = max_delay + 0.6

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"
     viewBox="0 0 {W} {H}" font-family="{FONT}" role="img"
     aria-label="GitHub contribution graph for {esc(data['username'])}">
  <style>
    .c {{ opacity:0; transform-box:fill-box; transform-origin:center;
          animation: pop .45s cubic-bezier(.2,.8,.3,1) both; }}
    @keyframes pop {{
      0%   {{ opacity:0; transform: translateY(-6px) scale(.4); }}
      100% {{ opacity:1; transform: translateY(0)    scale(1);  }}
    }}
    .lbl   {{ fill:{TEXT}; font-size:9px; }}
    .title {{ fill:{TEXT_BRIGHT}; font-size:12px; font-weight:600;
              opacity:0; animation: fade .5s ease-out .1s both; }}
    .stat  {{ fill:{TEXT}; font-size:10px;
              opacity:0; animation: fade .6s ease-out {reveal:.2f}s both; }}
    .hi    {{ fill:{ACCENT}; font-weight:600; }}
    .prompt{{ fill:{ACCENT}; }}
    .dim   {{ fill:#484f58; }}
    @keyframes fade {{ from {{opacity:0}} to {{opacity:1}} }}
    @media (prefers-reduced-motion: reduce) {{
      .c, .title, .stat {{ animation:none; opacity:1; transform:none; }}
    }}
  </style>
  <rect width="{W}" height="{H}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  {title}
  {"".join(month_labels)}
  {"".join(wd_labels)}
  {"".join(parts)}
  {"".join(legend)}
  {footer}
</svg>
'''


def main():
    if not os.path.exists(IN_PATH):
        raise SystemExit(f"[x] {IN_PATH} nahi mila. Pehle fetch_contributions.py chalao.")
    with open(IN_PATH, encoding="utf-8") as f:
        data = json.load(f)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(build(data))
    print(f"[+] {OUT_PATH} ban gaya")


if __name__ == "__main__":
    main()

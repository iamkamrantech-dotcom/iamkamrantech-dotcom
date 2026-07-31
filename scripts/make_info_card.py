#!/usr/bin/env python3
"""
make_info_card.py
-----------------
Neofetch-jaisa info card SVG banata hai jo line-by-line fade-in hota hai.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py     # bina animation (preview ke liye)

=> Sirf neeche wali CONFIG edit karo, baaki kuch chhoone ki zaroorat nahi.
"""

import os

OUT_PATH = "info-card.svg"

# ============================================================================
# CONFIG — yahan apni details bharo
# ============================================================================
USERNAME = "Kamran Shahid"
HOST = "github"

ROWS = [
    ("Now",        "Ai Engineer @ Contech International Health consultants"),
    ("Focus",      "Backend systems, Ai Models, Automation"),
    ("Stack",      "Python · TypeScript · React · Docker"),
    ("Tools",      "Linux · Git · Postgres · AWS"),
    ("Learning",   "Rust, distributed systems"),
    ("Highlight",  ""),
    ("Highlight",  "Open-source contributor"),
    ("Reach me",   "iamkamran.tech@gmail.com"),
]

# =============================== look & feel ================================
BG = "#0d1117"
BORDER = "#21262d"
KEY = "#39d353"        # left column (keys)
VAL = "#c9d1d9"        # right column (values)
DIM = "#8b949e"
ACCENT = "#58a6ff"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

WIDTH = 490
PAD = 20
FS = 11.5              # font size
LINE_H = 22
KEY_W = 88             # key column ki chaurai
STAGGER = 0.09         # har line ka delay

PALETTE = ["#161b22", "#f85149", "#39d353", "#d29922",
           "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]

STATIC = os.environ.get("STATIC") == "1"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim(i):
    """Har line ke liye animation class + delay."""
    if STATIC:
        return ""
    return f' class="in" style="animation-delay:{i * STAGGER:.2f}s"'


def build():
    y = PAD + 24
    parts = []
    i = 0

    # --- title: user@host ---
    parts.append(
        f'<text x="{PAD}" y="{y}"{anim(i)} font-size="{FS + 1.5}" font-weight="700">'
        f'<tspan fill="{KEY}">{esc(USERNAME)}</tspan>'
        f'<tspan fill="{DIM}">@</tspan>'
        f'<tspan fill="{ACCENT}">{esc(HOST)}</tspan></text>'
    )
    i += 1
    y += 10

    # --- separator line ---
    parts.append(
        f'<line x1="{PAD}" y1="{y}" x2="{WIDTH - PAD}" y2="{y}" '
        f'stroke="{BORDER}" stroke-width="1"{anim(i)}/>'
    )
    i += 1
    y += LINE_H

    # --- key/value rows ---
    for k, v in ROWS:
        parts.append(
            f'<text x="{PAD}" y="{y}"{anim(i)} font-size="{FS}">'
            f'<tspan fill="{KEY}" font-weight="600">{esc(k)}</tspan>'
            f'<tspan fill="{DIM}">:</tspan>'
            f'<tspan x="{PAD + KEY_W}" fill="{VAL}">{esc(v)}</tspan></text>'
        )
        i += 1
        y += LINE_H

    # --- neofetch color blocks ---
    y += 6
    bw, bh = 20, 11
    for j, col in enumerate(PALETTE):
        parts.append(
            f'<rect x="{PAD + j * (bw + 4)}" y="{y}" width="{bw}" height="{bh}" '
            f'rx="2" fill="{col}"{anim(i)}/>'
        )
    i += 1
    y += bh + PAD

    H = int(y)

    style = "" if STATIC else f'''
    .in {{ opacity:0; animation: slidein .5s ease-out both; }}
    @keyframes slidein {{
      from {{ opacity:0; transform: translateX(-10px); }}
      to   {{ opacity:1; transform: translateX(0);     }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .in {{ animation:none; opacity:1; transform:none; }}
    }}'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{H}"
     viewBox="0 0 {WIDTH} {H}" font-family="{FONT}" role="img" aria-label="Profile info card">
  <style>{style}</style>
  <rect width="{WIDTH}" height="{H}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  {"".join(parts)}
</svg>
'''


if __name__ == "__main__":
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"[+] {OUT_PATH} ban gaya{' (static)' if STATIC else ''}")

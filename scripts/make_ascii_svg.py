#!/usr/bin/env python3
"""
make_ascii_svg.py
-----------------
Ek photo ko monochrome ASCII portrait SVG me badalta hai jo row-by-row
"type" hoti hai (SMIL animation, GitHub README me chal jaati hai).

Usage:
    python scripts/make_ascii_svg.py source-photo.jpg
    python scripts/make_ascii_svg.py source-prepped.png --cols 100 --rows 53

Sirf Pillow + numpy zaroori hain. Agar rembg install ho to background
khud-ba-khud hata dega (behtar result), warna bhi kaam karega.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

OUT_PATH = "avi-ascii.svg"

# bright (sparse) -> dark (dense). Pehla space background ko khali karta hai.
RAMP = " .`:-=+*cs#%@"

INK = "#c9d1d9"       # ASCII text ka rang (monochrome — yahi saaf lagta hai)
CURSOR = "#39d353"    # typing cursor
BG = "#0d1117"
BORDER = "#21262d"
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

FONT_SIZE = 8.0
CHAR_W = FONT_SIZE * 0.60   # monospace advance width
LINE_H = FONT_SIZE * 1.00
PAD = 14.0


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def prepare(path, cols, rows, invert, no_bg_removal):
    img = Image.open(path)

    # 1) background hatao (optional, agar rembg mojood ho)
    if not no_bg_removal:
        try:
            from rembg import remove
            img = remove(img)
            print("[*] rembg: background hata diya")
        except Exception:
            print("[i] rembg nahi mila — background waise hi rahega "
                  "(saaf background wali photo use karo)")

    # 2) safed background par composite (transparent -> white)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        white = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(white, img)

    img = img.convert("L")

    # 3) contrast boost — flat chehra warna kaali dhabba ban jaata hai
    try:
        import cv2  # CLAHE = sab se behtar
        arr = np.array(img)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        img = Image.fromarray(clahe.apply(arr))
        print("[*] OpenCV CLAHE contrast lagaya")
    except Exception:
        img = ImageOps.autocontrast(img, cutoff=2)
        img = ImageEnhance.Contrast(img).enhance(1.45)
        print("[i] OpenCV nahi mila — Pillow autocontrast use kiya")

    # 4) character grid par resize (characters chaure se lambe hote hain)
    img = img.resize((cols, rows), Image.LANCZOS)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    if invert:
        arr = 1.0 - arr
    return arr


def to_rows(arr):
    n = len(RAMP)
    idx = np.clip(((1.0 - arr) * (n - 1)).round().astype(int), 0, n - 1)
    return ["".join(RAMP[i] for i in row) for row in idx]


def build_svg(text_rows, stagger, row_dur):
    cols = max(len(r) for r in text_rows)
    rows = len(text_rows)
    grid_w = cols * CHAR_W
    grid_h = rows * LINE_H
    W = grid_w + PAD * 2
    H = grid_h + PAD * 2 + 6

    clips, lines, cursors = [], [], []
    for i, row in enumerate(text_rows):
        if not row.strip():
            continue
        begin = i * stagger
        y = PAD + (i + 1) * LINE_H
        cid = f"w{i}"

        clips.append(
            f'<clipPath id="{cid}"><rect x="{PAD:.1f}" y="{y - LINE_H:.1f}" '
            f'width="0" height="{LINE_H + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{grid_w:.1f}" '
            f'dur="{row_dur}s" begin="{begin:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        lines.append(
            f'<text clip-path="url(#{cid})" x="{PAD:.1f}" y="{y:.1f}" '
            f'xml:space="preserve">{esc(row)}</text>'
        )
        cursors.append(
            f'<rect class="cur" x="{PAD:.1f}" y="{y - LINE_H + 1:.1f}" '
            f'width="{CHAR_W:.2f}" height="{LINE_H:.1f}" opacity="0">'
            f'<animate attributeName="x" from="{PAD:.1f}" to="{PAD + grid_w:.1f}" '
            f'dur="{row_dur}s" begin="{begin:.2f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.02;0.98;1" '
            f'dur="{row_dur}s" begin="{begin:.2f}s" fill="freeze"/></rect>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"
     viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="ASCII portrait">
  <defs>{"".join(clips)}</defs>
  <rect width="{W:.0f}" height="{H:.0f}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <g font-family="{FONT}" font-size="{FONT_SIZE}" fill="{INK}">
    {"".join(lines)}
  </g>
  <g fill="{CURSOR}">{"".join(cursors)}</g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="apni photo ka path (jpg/png)")
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument("--rows", type=int, default=53)
    ap.add_argument("--out", default=OUT_PATH)
    ap.add_argument("--invert", action="store_true", help="dark background wali photo ke liye")
    ap.add_argument("--no-bg-removal", action="store_true")
    ap.add_argument("--stagger", type=float, default=0.045, help="har row ka delay (sec)")
    ap.add_argument("--row-dur", type=float, default=0.35, help="ek row type hone ka time")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        sys.exit(f"[x] File nahi mili: {args.image}")

    arr = prepare(args.image, args.cols, args.rows, args.invert, args.no_bg_removal)
    svg = build_svg(to_rows(arr), args.stagger, args.row_dur)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[+] {args.out} ban gaya ({args.cols}x{args.rows})")


if __name__ == "__main__":
    main()

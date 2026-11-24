"""P12d: two diagrams redrawn at insertion size (text >= 9.3 pt after insertion).

  3-4-1_pipeline          one command, eight steps (extract -> ODS -> dim -> fact -> mart -> tests -> snapshot -> export), etl_log below
  3-2_kien_truc_cac_lop   six layers from source to Power BI (names and numbers as on the slide "Kiến trúc: vai trò từng lớp")

Run: python scripts/p12d_diagrams.py   -> figures/slide/*.png (+ manifest). The report keeps its own figures.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matplotlib.patches import FancyBboxPatch  # noqa: E402

import slide_fig as sf  # noqa: E402

INK = "#0b0b0b"
FILL = {"src": "#e6e8ee", "stg": "#f3d9b8", "ods": "#dde1ea", "dw": "#fde08a", "mart": "#cfe8d6", "bi": "#e1d4ee", "log": "#fdf8e4"}
EDGE = "#33415c"


def box(ax, x, y, w, h, text, fc, fs=9.6, bold=True, dashed=False, align="center"):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.06", fc=fc, ec=EDGE, lw=1.4, ls="--" if dashed else "-")
    ax.add_patch(p)
    ax.text(x + (w / 2 if align == "center" else 0.08), y + h / 2, text, ha=align, va="center", fontsize=fs, fontweight="bold" if bold else "normal", color=INK, linespacing=1.05)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=EDGE, lw=1.6, shrinkA=0, shrinkB=0))


def pipeline():
    fig, ax = sf.new_figure("full_ket")
    ax.set_xlim(0, 4.6)
    ax.set_ylim(-0.12, 2.0)
    ax.axis("off")
    steps = [("extract", "src"), ("ODS", "ods"), ("dim", "dw"), ("fact", "dw"), ("mart", "mart"), ("tests", "ods"), ("snapshot", "stg"), ("export", "bi")]
    sub = ["lấy dòng\nchưa có", "làm sạch\n18 bảng", "10 chiều", "6 fact", "17 view", "136 phép\nkiểm thử", "chụp lại\nsố dòng", "CSV cho\nPower BI"]
    w, h, gap = 1.0, 0.62, 0.2
    for i, ((name, k), s) in enumerate(zip(steps, sub)):
        row, col = divmod(i, 4)
        x = col * (w + gap) - 0.0 + 0.0
        y = 1.2 - row * 0.85
        box(ax, x, y, w, h, f"{name}\n{s}", FILL[k], fs=9.6)
        if col < 3:
            arrow(ax, x + w, y + h / 2, x + w + gap, y + h / 2)
    # wrap arrow from end of row 1 to start of row 2
    ax.annotate("", xy=(0.5, 1.2 - 0.85 + h), xytext=(3 * (w + gap) + w / 2, 1.2), arrowprops=dict(arrowstyle="-|>", color=EDGE, lw=1.6, connectionstyle="angle,angleA=-90,angleB=180,rad=0", shrinkA=0, shrinkB=2), annotation_clip=False)
    box(ax, 0.0, -0.08, 4.6 * 0.0 + 4 * (w + gap) - gap, 0.38, "etl_log: mỗi lần chạy, dòng bị loại, kết quả kiểm thử", FILL["log"], fs=9.6, bold=False, dashed=True)
    sf.finish(fig, "3-4-1_pipeline", "full_ket", script="scripts/p12d_diagrams.py")


def layers():
    fig, ax = sf.new_figure("left60")
    ax.set_xlim(0, 3.6)
    ax.set_ylim(0, 2.45)
    ax.axis("off")
    rows = [("Nguồn", "oltp 9 bảng, crm 2 bảng", "src"), ("Staging", "chép nguyên dữ liệu", "stg"), ("ODS", "làm sạch, gắn cờ lỗi", "ods"),
            ("Kho dw", "10 dimension, 6 fact", "dw"), ("Data mart", "4 mart, 17 view", "mart"), ("Power BI", "4 dashboard", "bi")]
    h, gap = 0.32, 0.07
    for i, (name, txt, k) in enumerate(rows):
        y = 2.45 - (i + 1) * (h + gap) + gap
        box(ax, 0.0, y, 0.95, h, name, FILL[k], fs=9.6)
        box(ax, 1.0, y, 2.6, h, txt, "white", fs=9.4, bold=False, align="left")
        if i < len(rows) - 1:
            arrow(ax, 0.475, y, 0.475, y - gap)
    sf.finish(fig, "3-2_kien_truc_cac_lop", "left60", script="scripts/p12d_diagrams.py")


if __name__ == "__main__":
    pipeline()
    layers()

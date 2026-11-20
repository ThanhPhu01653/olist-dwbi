"""P11: figures redrawn for the projector (16:9 slides). The report keeps the old versions; the slides use the *_sl.png files written here.

    python scripts/p11_figures.py          # architecture diagrams (Lakehouse, API) and the latency chart
Latency chart: replotted from handoff/2026-11-19-P10-latency.md (the six probes are listed there); no new measurement is made.
Rules: slides/QUY-TAC-TRINH-BAY.md section 6 (at most about 12 blocks, large text, no title inside the figure).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
EDGE = "#374151"
GREY, BLUE, ORANGE, GREEN, GOLD, SILVER, BRONZE, RED, PURPLE = "#E5E7EB", "#8ECAE6", "#F4A261", "#CDE8D6", "#FFE08A", "#D9DDE3", "#F1CDA8", "#C8102E", "#E2D4F0"


def block(ax, x, y, w, h, text, fill, fs=16, dashed=False, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.09", fc=fill, ec=EDGE, lw=1.6, ls="--" if dashed else "-"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.15)


def arrow(ax, p, q, label="", fs=16, color=EDGE, rad=0.0, ls="-", dy=0.12):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=22, lw=2.2, color=color, connectionstyle=f"arc3,rad={rad}", ls=ls, shrinkA=2, shrinkB=2))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", va="bottom", fontsize=fs, color=color)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    out = FIG / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    for sub in ("report/figures", "slides/figures"):
        if (ROOT / sub).exists():
            shutil.copy2(out, ROOT / sub / name)
    print("written", name)


# ------------------------------------------------------------------ Lakehouse architecture (8 blocks)
W, H = 12.2, 4.5
fig, ax = canvas(W, H)
bw, bh, gap, y0 = 1.72, 1.25, 0.36, 2.95
xs = [0.05 + i * (bw + gap) for i in range(6)]
names = [("PostgreSQL\nnguồn", GREY), ("Debezium\n+ Kafka", BLUE), ("Bronze\nSpark", BRONZE), ("Silver\nSpark", SILVER), ("Gold\ndbt", GOLD), ("Trino +\nSuperset", GREEN)]
for x, (t, c) in zip(xs, names):
    block(ax, x, y0, bw, bh, t, c)
for i in range(5):
    arrow(ax, (xs[i] + bw, y0 + bh / 2), (xs[i + 1], y0 + bh / 2))
# storage band under Bronze..Gold
bx0, bx1 = xs[2], xs[4] + bw
block(ax, bx0, 1.45, bx1 - bx0, 0.85, "MinIO + Iceberg (Parquet)", "#FFFFFF", fs=17, dashed=True)
for k in (2, 3, 4):
    ax.plot([xs[k] + bw / 2] * 2, [y0, 2.3], color=EDGE, lw=1.6, ls=":")
# chapter 3 warehouse + reconciliation
block(ax, xs[5] - 0.05, 0.25, bw + 0.1, 1.0, "Kho\nchương 3", GREY, fs=18, dashed=True)
arrow(ax, (xs[4] + bw / 2 + 0.2, 1.45), (xs[5] - 0.02, 0.8), "", color=RED, rad=0.25)
ax.text(xs[4] + 0.2, 0.62, "đối soát\n16/16 bảng", fontsize=16, color=RED, fontweight="bold", ha="center", va="center")
save(fig, "5-1_kien_truc_lakehouse_sl.png")

# ------------------------------------------------------------------ API architecture (7 blocks)
W, H = 12.7, 3.5
fig, ax = canvas(W, H)
bw, bh, gap, y0 = 1.58, 1.25, 0.25, 1.75
xs = [0.05 + i * (bw + gap) for i in range(7)]
names = [("API\ncông khai", BLUE), ("Collector\nPython", GREY), ("Landing\nzone", GREY), ("Staging", BRONZE), ("ODS", SILVER), ("Kho\n(dw)", GOLD), ("Mart\nvà BI", GREEN)]
for x, (t, c) in zip(xs, names):
    block(ax, x, y0, bw, bh, t, c)
for i in range(6):
    arrow(ax, (xs[i] + bw, y0 + bh / 2), (xs[i + 1], y0 + bh / 2))
block(ax, xs[0], 0.2, xs[6] + bw - xs[0], 0.95, "etl_log ghi mọi lời gọi; lỗi API không chặn pipeline chính", "#FFFBEA", fs=17, dashed=True, bold=False)
save(fig, "5-2_kien_truc_api_sl.png")

# ------------------------------------------------------------------ latency chart (12 x 6, no title)
md = (ROOT / "handoff" / "2026-11-19-P10-latency.md").read_text(encoding="utf-8")
probes = []
for m in re.finditer(r"- probe (\d+): PostgreSQL → Kafka ([\d.]+) s; Kafka → Bronze ([\d.]+) s; Bronze → Silver ([\d.]+) s", md):
    probes.append((int(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))))
assert len(probes) == 6, probes
fig, ax = plt.subplots(figsize=(12, 6))
labels = [f"lần {p[0]}" for p in probes]
left = [0.0] * len(probes)
for k, name, col in ((1, "PostgreSQL → Kafka", "#8ECAE6"), (2, "Kafka → Bronze", ORANGE), (3, "Bronze → Silver", "#2A9D8F")):
    vals = [p[k] for p in probes]
    ax.barh(labels, vals, left=left, label=name, color=col, edgecolor="white")
    left = [a + b for a, b in zip(left, vals)]
for y, v in enumerate(left):
    ax.text(v + 0.5, y, f"{v:.1f} s", va="center", fontsize=15)
ax.set_xlabel("giây từ lúc COMMIT ở nguồn đến khi Silver ghi xong", fontsize=15)
ax.invert_yaxis()
ax.tick_params(labelsize=15)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=15, frameon=False)
ax.set_xlim(0, 45)
save(fig, "5-1_latency_sl.png")

"""P12d: analysis trees DB1-DB4 (goal -> questions / measures / dimensions) drawn left-to-right at insertion size.

Source text: the mermaid blocks of huong-dan/05-nghiep-vu-nhap.md section 6 (not edited).  Output: figures/slide/2-3_cay_phan_tich_DB<k>.png
Run: python scripts/p12d_trees.py
"""
from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matplotlib.patches import FancyBboxPatch  # noqa: E402

import slide_fig as sf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "huong-dan" / "05-nghiep-vu-nhap.md"
COL = {"Câu hỏi": ("#fff3a8", "#b59f00"), "Chỉ số": ("#d3efc2", "#5c9a3c"), "Chiều": ("#e3d3f7", "#8458b6")}
ROOT_FILL = ("#1f3fbf", "white")


def parse() -> dict[str, tuple[str, dict[str, list[str]]]]:
    txt = SRC.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"<!-- png: 2-3_cay_phan_tich_(DB\d)\.png -->\s*```mermaid\s*mindmap\s*(.*?)```", txt, re.S):
        key, body = m.group(1), m.group(2).splitlines()
        root = re.search(r"root\(\((.*?)\)\)", body[0]).group(1)
        branches: dict[str, list[str]] = {}
        cur = None
        for ln in body[1:]:
            if not ln.strip():
                continue
            ind = len(ln) - len(ln.lstrip())
            if ind == 4:
                cur = ln.strip()
                branches[cur] = []
            else:
                branches[cur].append(ln.strip())
        out[key] = (root, branches)
    return out


def draw(key: str, root: str, branches: dict[str, list[str]]) -> None:
    fig, ax = sf.new_figure("full_ket")
    W, H = sf.BOX_PT["full_ket"]
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    n_leaf = sum(len(v) for v in branches.values())
    gaps = (len(branches) - 1) * 5
    row = (H - gaps) / n_leaf
    x_root, w_root = 0, 88
    x_br, w_br = 106, 54
    x_leaf = 176
    y = H
    centers = []
    for name, leaves in branches.items():
        fc, ec = COL.get(name, ("#eee", "#888"))
        top = y
        for leaf in leaves:
            y -= row
            ax.add_patch(FancyBboxPatch((x_leaf, y + 0.8), W - x_leaf, row - 1.6, boxstyle="round,pad=0,rounding_size=2.5", fc=fc, ec=ec, lw=0.9))
            ax.text(x_leaf + 4, y + row / 2, leaf, ha="left", va="center", fontsize=9.4, color="#0b0b0b")
        mid = (top + y) / 2
        centers.append(mid)
        ax.add_patch(FancyBboxPatch((x_br, mid - 9), w_br, 18, boxstyle="round,pad=0,rounding_size=3", fc=fc, ec=ec, lw=1.4))
        ax.text(x_br + w_br / 2, mid, name, ha="center", va="center", fontsize=9.6, fontweight="bold", color="#0b0b0b")
        ax.plot([x_br + w_br, x_leaf], [mid, mid], color=ec, lw=1.2)
        for k in range(len(leaves)):
            yy = top - row * (k + 0.5)
            ax.plot([x_br + w_br + 8, x_leaf], [mid, yy], color=ec, lw=0.9)
        y -= 5
    cy = sum(centers) / len(centers)
    ax.add_patch(FancyBboxPatch((x_root, cy - 34), w_root, 68, boxstyle="round,pad=0,rounding_size=6", fc=ROOT_FILL[0], ec="#14287f", lw=1.4))
    ax.text(x_root + w_root / 2, cy, textwrap.fill(root, 12), ha="center", va="center", fontsize=9.6, fontweight="bold", color=ROOT_FILL[1], linespacing=1.1)
    for mid in centers:
        ax.plot([x_root + w_root, x_br], [cy, mid], color="#6a6a6a", lw=1.4)
    sf.finish(fig, f"2-3_cay_phan_tich_{key}", "full_ket", drop_title=False, script="scripts/p12d_trees.py")


if __name__ == "__main__":
    for key, (root, br) in parse().items():
        draw(key, root, br)

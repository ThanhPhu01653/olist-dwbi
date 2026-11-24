"""P12e: small drawing kit for slide diagrams, in 'canvas pixels' of the draw.io rule (full frame 860 x 350 px, figure next to text 550 x 350 px).

The figure is created at the insertion size, so 20 px text = about 10 pt on the slide.  Boxes wrap their text; arrows are plain lines.
    c = Canvas("full_ket"); c.box(10, 10, 200, 60, "Tên khối", fill=BLUE, bold=True); c.arrow((210, 40), (260, 40)); c.save("ten-hinh")
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

import slide_fig as sf  # noqa: E402

ORANGE, BLUE, GREEN, GREY, YELLOW, PURPLE, PINK, TEAL, WHITE = "#F4A261", "#8ECAE6", "#CDE8D6", "#E5E7EB", "#FFF3C4", "#E2D4F0", "#F8C8DC", "#B7E4DA", "#FFFFFF"
INK, EDGE = "#0b0b0b", "#33415c"
SIZE_PX = {"full_ket": (860, 350), "full": (860, 390), "left60": (550, 350), "full_ket_ca": (860, 323)}


class Canvas:
    def __init__(self, kind: str = "full_ket"):
        self.kind = kind
        self.fig, self.ax = sf.new_figure(kind)
        self.W, self.H = SIZE_PX[kind]
        self.pt = sf.BOX_PT[kind][0] / self.W          # points per canvas pixel
        self.ax.set_position([0, 0, 1, 1])
        self.ax.set_xlim(0, self.W)
        self.ax.set_ylim(self.H, 0)
        self.ax.axis("off")
        self.fig._slide_no_layout = True
        self.fig._slide_no_rotate = True
        self.fig._slide_max_pt = 12

    def fs(self, px: float) -> float:
        return px * self.pt

    def text(self, x, y, s, px=20, bold=False, ha="center", va="center", color=INK, family=None, z=5):
        return self.ax.text(x, y, s, fontsize=self.fs(px), fontweight="bold" if bold else "normal", ha=ha, va=va, color=color, linespacing=1.15, zorder=z,
                            **({"family": family} if family else {}))

    def wrap(self, s: str, w: float, px: float) -> str:
        chars = max(4, int((w - 10) / (0.54 * px)))
        out = []
        for ln in s.split("\n"):
            out.extend(textwrap.wrap(ln, chars, break_long_words=False, break_on_hyphens=False) or [""])
        return "\n".join(out)

    def box(self, x, y, w, h, s="", fill=GREY, px=20, bold=False, ec=EDGE, lw=1.4, dashed=False, ha="center", wrap=True, tc=INK, z=2, r=6):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fill, ec=ec, lw=lw * self.pt / 0.5, ls="--" if dashed else "-", zorder=z))
        if s:
            txt = self.wrap(s, w, px) if wrap else s
            tx = x + w / 2 if ha == "center" else x + 8
            self.text(tx, y + h / 2, txt, px=px, bold=bold, ha=ha, color=tc)
        return (x, y, w, h)

    def arrow(self, p0, p1, color=EDGE, lw=1.6, dashed=False, head=True, z=1):
        self.ax.annotate("", xy=p1, xytext=p0, zorder=z,
                         arrowprops=dict(arrowstyle="-|>" if head else "-", color=color, lw=lw * self.pt / 0.5, ls="--" if dashed else "-", shrinkA=0, shrinkB=0))

    def line(self, p0, p1, color="#6b7280", lw=1.2, z=0):
        self.ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=color, lw=lw * self.pt / 0.5, zorder=z, solid_capstyle="round")

    def rect(self, x, y, w, h, fill, ec="none", z=0):
        self.ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec=ec, zorder=z))

    def save(self, name: str, script: str = "scripts/p12e_*.py"):
        return sf.finish(self.fig, name, self.kind, drop_title=False, script=script)


def top(b):
    return (b[0] + b[2] / 2, b[1])


def bottom(b):
    return (b[0] + b[2] / 2, b[1] + b[3])


def left(b):
    return (b[0], b[1] + b[3] / 2)


def right(b):
    return (b[0] + b[2], b[1] + b[3] / 2)

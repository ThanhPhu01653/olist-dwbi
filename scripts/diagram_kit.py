"""Tiny diagram kit: describe boxes and arrows once, get an editable draw.io file AND a draft PNG (watermarked BẢN NHÁP).

Used by scripts/gen_drawio.py. Coordinates are draw.io pixels (origin top-left). The PNG is a draft that the group redraws in draw.io
(figure file names stay the same so the report and slides pick up the redrawn version).
"""
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

ROOT = Path(__file__).resolve().parent.parent
DRAWIO_DIR = ROOT / "docs" / "diagrams"
FIG_DIRS = [ROOT / "figures", ROOT / "report" / "figures", ROOT / "slides" / "figures"]

ORANGE, BLUE, GREY, GREEN, YELLOW, PURPLE, WHITE = "#F4A261", "#8ECAE6", "#E5E7EB", "#CDE8D6", "#FFF3C4", "#E2D4F0", "#FFFFFF"
PINK, TEAL = "#F8C8DC", "#B7E4DA"

_names = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ("Segoe UI", "Arial", "Calibri") if f in _names), "DejaVu Sans")


class Diagram:
    def __init__(self, name: str, width: int = 1500, height: int = 900, draft: bool = True):
        self.name, self.W, self.H, self.draft = name, width, height, draft
        self.items: list[dict] = []  # insertion order = z-order
        self.n = 1

    # ---- primitives
    def box(self, x, y, w, h, text, fill=GREY, bold=False, font=12, stroke="#4B5563", shape="rounded", color="#111111", underline=False, align="center", dashed=False) -> int:
        self.n += 1
        self.items.append(dict(kind="box", id=self.n, x=x, y=y, w=w, h=h, text=text, fill=fill, bold=bold, font=font, stroke=stroke,
                               shape=shape, color=color, align=align, dashed=dashed))
        return self.n

    def entity(self, x, y, w, title, cols, fill=GREY, font=11, header=None) -> int:
        """ER-style table box. cols = [(text, underlined, bold), ...]; height follows the number of columns."""
        h = 30 + 17 * len(cols) + 6
        i = self.box(x, y, w, h, title, fill=fill, font=font, shape="entity")
        it = self._box(i)
        it["cols"], it["header"] = cols, header or fill
        return i

    def frame(self, x, y, w, h, title, fill="#FFFBEA", font=13) -> int:
        return self.box(x, y, w, h, title, fill=fill, bold=True, font=font, shape="frame", align="top-left", dashed=True)

    def label(self, x, y, w, h, text, font=14, bold=True, color="#111111", align="left") -> int:
        return self.box(x, y, w, h, text, fill="none", bold=bold, font=font, stroke="none", shape="text", color=color, align=align)

    def arrow(self, a, b, label="", dashed=False, color="#374151", both=False, width=1.6) -> None:
        self.n += 1
        self.items.append(dict(kind="arrow", id=self.n, a=a, b=b, label=label, dashed=dashed, color=color, both=both, width=width))

    # ---- helpers
    def _box(self, i):
        return next(it for it in self.items if it["kind"] == "box" and it["id"] == i)

    # ---- draw.io
    def drawio(self) -> str:
        cells = []
        for it in self.items:
            if it["kind"] == "box":
                if it["shape"] == "entity":
                    rows = "<br/>".join(("<b>%s</b>" if b else "%s") % (("<u>%s</u>" if u else "%s") % escape(t)) for t, u, b in it["cols"])
                    val = escape("<b>%s</b><hr size=\"1\"/>" % escape(it["text"]) + rows)
                    st = f"rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=6;fillColor={it['fill']};strokeColor={it['stroke']};fontSize={it['font']};"
                    cells.append(f'<mxCell id="c{it["id"]}" value="{val}" style="{st}" vertex="1" parent="1"><mxGeometry x="{it["x"]}" y="{it["y"]}" width="{it["w"]}" height="{it["h"]}" as="geometry"/></mxCell>')
                    continue
                if it["shape"] == "text":
                    st = "text;html=1;whiteSpace=wrap;verticalAlign=middle;align=left;"
                elif it["shape"] == "frame":
                    st = "rounded=0;verticalAlign=top;align=left;spacingLeft=8;dashed=1;whiteSpace=wrap;html=1;"
                else:
                    st = ("rounded=1;" if it["shape"] == "rounded" else "rounded=0;") + "whiteSpace=wrap;html=1;" + ("dashed=1;" if it["dashed"] else "")
                if it["fill"] != "none":
                    st += f"fillColor={it['fill']};strokeColor={it['stroke']};"
                st += f"fontSize={it['font']};fontColor={it['color']};" + ("fontStyle=%d;" % (1 + (4 if it['kind'] == 'x' else 0)) if it["bold"] else "")
                val = escape(it["text"], {"\n": "&#10;"})
                cells.append(f'<mxCell id="c{it["id"]}" value="{val}" style="{st}" vertex="1" parent="1"><mxGeometry x="{it["x"]}" y="{it["y"]}" width="{it["w"]}" height="{it["h"]}" as="geometry"/></mxCell>')
            else:
                st = "endArrow=classic;html=1;rounded=0;strokeColor=%s;strokeWidth=%s;" % (it["color"], it["width"]) + ("dashed=1;" if it["dashed"] else "") + ("startArrow=classic;" if it["both"] else "")
                cells.append(f'<mxCell id="e{it["id"]}" value="{escape(it["label"])}" style="{st}" edge="1" parent="1" source="c{it["a"]}" target="c{it["b"]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
        return (f'<mxfile host="app.diagrams.net"><diagram name="{escape(self.name)}" id="d1"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" page="1" pageScale="1" '
                f'pageWidth="{self.W}" pageHeight="{self.H}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(cells)}</root></mxGraphModel></diagram></mxfile>')

    # ---- PNG draft
    def png(self, path: Path) -> None:
        fig = plt.figure(figsize=(self.W / 100, self.H / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.W); ax.set_ylim(self.H, 0); ax.axis("off")
        fig.patch.set_facecolor("white")

        def clip(b, tx, ty):
            cx, cy = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
            dx, dy = tx - cx, ty - cy
            if dx == 0 and dy == 0:
                return cx, cy
            sx = (b["w"] / 2) / abs(dx) if dx else 1e9
            sy = (b["h"] / 2) / abs(dy) if dy else 1e9
            t = min(sx, sy)
            return cx + dx * t, cy + dy * t

        for it in self.items:
            if it["kind"] != "box":
                continue
            x, y, w, h = it["x"], it["y"], it["w"], it["h"]
            if it["shape"] == "entity":
                ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=it["stroke"], lw=1.2))
                ax.add_patch(Rectangle((x, y), w, 28, fc=it["header"], ec=it["stroke"], lw=1.2))
                ax.text(x + w / 2, y + 14, it["text"], ha="center", va="center", fontsize=it["font"] * 0.72 * 1.1, fontweight="bold", family=FONT)
                rend = fig.canvas.get_renderer()
                for k, (t, u, b) in enumerate(it["cols"]):
                    ty = y + 28 + 17 * k + 12
                    tx = ax.text(x + 8, ty, t, ha="left", va="center", fontsize=it["font"] * 0.72, fontweight="bold" if b else "normal", family=FONT)
                    if u:
                        bb = tx.get_window_extent(rend).transformed(ax.transData.inverted())
                        yy = max(bb.y0, bb.y1)
                        ax.plot([bb.x0, bb.x1], [yy + 0.5, yy + 0.5], color="black", lw=0.9)
                continue
            if it["shape"] == "frame":
                ax.add_patch(Rectangle((x, y), w, h, fc=it["fill"], ec="#9CA3AF", lw=1.2, ls="--"))
            elif it["shape"] == "text":
                pass
            else:
                ax.add_patch(FancyBboxPatch((x + 4, y + 4), w - 8, h - 8, boxstyle="round,pad=4,rounding_size=7" if it["shape"] == "rounded" else "square,pad=4",
                                            fc=it["fill"], ec=it["stroke"], lw=1.2, ls="--" if it["dashed"] else "-"))
            fs = it["font"]
            chars = max(6, int((w - 14) / (0.52 * fs)))
            lines = []
            for ln in it["text"].split("\n"):
                lines.extend(textwrap.wrap(ln, chars) or [""])
            txt = "\n".join(lines)
            if it["shape"] == "frame":
                ax.text(x + 8, y + 6, txt, ha="left", va="top", fontsize=fs * 0.72, fontweight="bold" if it["bold"] else "normal", family=FONT, color=it["color"])
            elif it["shape"] == "text":
                ha = {"left": "left", "center": "center", "right": "right"}[it["align"]]
                tx = x if ha == "left" else (x + w / 2 if ha == "center" else x + w)
                ax.text(tx, y + h / 2, txt, ha=ha, va="center", fontsize=fs * 0.72, fontweight="bold" if it["bold"] else "normal", family=FONT, color=it["color"])
            else:
                ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs * 0.72, fontweight="bold" if it["bold"] else "normal", family=FONT, color=it["color"], linespacing=1.25)
        for it in self.items:
            if it["kind"] != "arrow":
                continue
            a, b = self._box(it["a"]), self._box(it["b"])
            acx, acy, bcx, bcy = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2, b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
            p0, p1 = clip(a, bcx, bcy), clip(b, acx, acy)
            ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="<|-|>" if it["both"] else "-|>", color=it["color"], lw=it["width"], ls="--" if it["dashed"] else "-", shrinkA=0, shrinkB=0))
            if it["label"]:
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                lab = "\n".join(textwrap.fill(it["label"], 26).split("\n"))
                ax.text(mx, my, lab, ha="center", va="center", fontsize=8, family=FONT, color="#111111", bbox=dict(fc="white", ec="none", pad=1.5, alpha=0.92))
        if self.draft:
            ax.text(self.W - 12, self.H - 10, "BẢN NHÁP – nhóm vẽ lại bằng draw.io (docs/diagrams/)", ha="right", va="bottom", fontsize=9, color="#B91C1C", family=FONT, fontweight="bold")
        path.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(path, dpi=150)
        plt.close(fig)

    def save(self, drawio_name: str | None, png_name: str | None) -> None:
        if drawio_name:
            DRAWIO_DIR.mkdir(parents=True, exist_ok=True)
            (DRAWIO_DIR / drawio_name).write_text(self.drawio(), encoding="utf-8")
            print("written docs/diagrams/" + drawio_name)
        if png_name:
            self.png(FIG_DIRS[0] / png_name)
            for d in FIG_DIRS[1:]:
                if d.exists():
                    shutil.copy2(FIG_DIRS[0] / png_name, d / png_name)
            print("written figures/" + png_name)

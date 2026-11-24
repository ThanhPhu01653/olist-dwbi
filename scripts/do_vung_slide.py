"""P12d: measure the usable area of the slides on the rendered PDF (no guessing).

For every page of slides/main.pdf (PyMuPDF) report, in pt (page = 453.5 x 255.1):
  - bottom of the title bar (incl. the red rule), the \\muc label box, the footer rule (top of the footer area)
  - boxes of all figures (images wider than 40 pt below the title bar) and of the \\KetLuan bar (light-blue rounded box)
  - gap from the figure / KetLuan to the title bar and to the footer rule

Usage:  python scripts/do_vung_slide.py [slides/main.pdf] [--json out.json] [--pages 53-60]
Imported by scripts/kiem_tra_slide.py (--pdf mode): measure(pdf) -> list of page dicts.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
NAVY = (0.0, 0.2, 0.4)
KET_FILL = (0.9, 0.92, 0.94)


def _close(a, b, tol=0.02):
    return a is not None and all(abs(x - y) < tol for x, y in zip(a, b))


def measure_page(page: "pymupdf.Page") -> dict:
    W, H = page.rect.width, page.rect.height
    res = {"w": W, "h": H, "bar_bottom": None, "footer_top": None, "muc": None, "ket": None, "figs": []}
    for dr in page.get_drawings():
        r = dr["rect"]
        fill = dr.get("fill")
        if _close(fill, NAVY) and r.y0 < 5 and r.width > W * 0.9 and r.y1 > 20:
            res["bar_bottom"] = max(res["bar_bottom"] or 0, r.y1)  # title bar
        elif fill is not None and abs(fill[0] - 0.808) < 0.02 and r.y0 < 40 and r.width > W * 0.9:
            res["bar_bottom"] = max(res["bar_bottom"] or 0, r.y1)  # red rule under the bar
        elif _close(fill, KET_FILL, 0.01) and r.width > W * 0.5:
            res["ket"] = [r.x0, r.y0, r.x1, r.y1]
        elif dr.get("fill") is None and dr.get("color") is not None and abs(r.y0 - r.y1) < 0.5 and r.y0 > H * 0.85 and r.width > W * 0.5:
            res["footer_top"] = r.y0  # footer rule
    for im in page.get_image_info():
        x0, y0, x1, y1 = im["bbox"]
        if y0 > (res["bar_bottom"] or 35) - 1 and y1 < H * 0.96 and (x1 - x0) > 40 and (y1 - y0) > 20:
            res["figs"].append({"bbox": [x0, y0, x1, y1], "px": [im["width"], im["height"]]})
    return res


def measure(pdf: str | Path) -> list[dict]:
    doc = pymupdf.open(str(pdf))
    out = []
    for i, p in enumerate(doc):
        m = measure_page(p)
        m["page"] = i + 1
        txt = p.get_text("blocks")
        m["muc"] = None
        for b in txt:
            if b[0] > 200 and b[1] < 50 and b[3] < 50 and "·" in b[4] or (b[1] < 50 and b[0] > 200 and b[4].strip()[:1].isdigit() and "·" in b[4]):
                m["muc"] = [b[0], b[1], b[2], b[3]]
                break
        out.append(m)
    return out


def summary(ms: list[dict]) -> dict:
    """Median figure geometry on pages with a figure: top, height with / without a KetLuan bar below."""
    top = [m["figs"][0]["bbox"][1] for m in ms if m["figs"] and m["bar_bottom"]]
    with_ket = [m for m in ms if m["figs"] and m["ket"]]
    no_ket = [m for m in ms if m["figs"] and not m["ket"]]
    h_ket = [max(f["bbox"][3] - f["bbox"][1] for f in m["figs"]) for m in with_ket]
    h_no = [max(f["bbox"][3] - f["bbox"][1] for f in m["figs"]) for m in no_ket]
    ket_top = [m["ket"][1] for m in with_ket]
    ket_bottom = [m["ket"][3] for m in with_ket]
    foot = [m["footer_top"] for m in ms if m["footer_top"]]
    bar = [m["bar_bottom"] for m in ms if m["bar_bottom"]]
    med = lambda x: round(statistics.median(x), 1) if x else None
    mx = lambda x: round(max(x), 1) if x else None
    return {
        "bar_bottom": med(bar), "footer_top": med(foot),
        "fig_top_median": med(top), "fig_top_min": round(min(top), 1) if top else None,
        "fig_height_with_ketluan_max": mx(h_ket), "fig_height_with_ketluan_median": med(h_ket),
        "fig_height_no_ketluan_max": mx(h_no),
        "ketluan_top_median": med(ket_top), "ketluan_bottom_max": mx(ket_bottom),
        "gap_ketluan_to_footer_min": round(min(foot[0] - b for b in ket_bottom), 1) if ket_bottom and foot else None,
        "pages": len(ms),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?", default=str(ROOT / "slides" / "main.pdf"))
    ap.add_argument("--json")
    ap.add_argument("--pages", help="e.g. 53-60")
    a = ap.parse_args()
    ms = measure(a.pdf)
    sel = ms
    if a.pages:
        lo, hi = (int(x) for x in a.pages.split("-"))
        sel = [m for m in ms if lo <= m["page"] <= hi]
        for m in sel:
            f = [[round(v, 1) for v in x["bbox"]] for x in m["figs"]]
            print(f"p{m['page']}: bar_bottom={m['bar_bottom']} muc={m['muc']} footer={m['footer_top']} ket={[round(v, 1) for v in m['ket']] if m['ket'] else None} figs={f}")
    s = summary(ms)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps({"summary": s, "pages": ms}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()

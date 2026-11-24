"""P12d: figures for the slides are always drawn through this module (size = insertion size, text >= 9 pt after insertion).

Why: a figure drawn at 9.5 inch and shrunk to 25% makes 12 pt text about 3 pt on the slide. Here the figure is created at the size it
will have on the slide (scale about 1), so the point size in matplotlib is the point size on the slide.

Boxes (pt, measured on the PDF by scripts/do_vung_slide.py; keep in sync with slides/bocuc.sty):
  full_ket : \\HinhLon / \\AnhChup with a \\KetLuan bar below   (\\linewidth x \\HinhCao)
  full     : figure without \\KetLuan                          (\\linewidth x \\VungCao)
  left60   : \\HinhChu (figure 60 % of the width, text right)   (0.60 \\linewidth x \\HinhCao)

Use in a new script:
    from slide_fig import new_figure, finish
    fig, ax = new_figure("full_ket")       # figsize = insertion size
    ...draw...
    finish(fig, "3-1_my_chart")             # -> figures/slide/3-1_my_chart.png + manifest

Redraw every chart of the main deck:  python scripts/slide_fig.py --all   (then python scripts/sync_figures.py)
Use for an existing script without editing it (hooks Figure.savefig; only figures that appear in slides/sections are redrawn,
into figures/slide/; the files used by the report are NOT overwritten):
    python scripts/slide_fig.py --run scripts/eda/distributions.py
The kind of each figure is read from slides/sections/*.tex (macro and whether the frame has \\KetLuan).
"""
from __future__ import annotations

import json
import re
import runpy
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.text import Text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "slide"
MANIFEST = OUT / "_manifest.json"
SECTIONS = ROOT / "slides" / "sections"

LINEWIDTH_PT = 428.0     # \linewidth (text width of the 16:9 page)
HINH_CAO_PT = 175.0      # \HinhCao
VUNG_CAO_PT = 195.0      # \VungCao
MIN_PT = 9.3             # smallest text in the drawing (>= 9 pt after insertion even at display scale 0.97)
MAIN_PT = 10.0           # main text (axis labels, annotations)

BOX_PT = {"full_ket": (LINEWIDTH_PT, HINH_CAO_PT), "full": (LINEWIDTH_PT, VUNG_CAO_PT), "left60": (0.64 * LINEWIDTH_PT, HINH_CAO_PT)}
BOX_IN = {k: (w / 72.0, h / 72.0) for k, (w, h) in BOX_PT.items()}

_PAT = re.compile(r"\\(HinhLon|AnhChup|HinhChu|anh|begin\{AnhKhoanh\})(?:\[[^\]]*\])?\{([^}]+\.(?:png|jpg|jpeg))\}")


def figure_kinds(include_backup: bool = False) -> dict[str, str]:
    """name (stem) -> kind, from the macro that inserts it and whether the frame has a \\KetLuan bar."""
    kinds: dict[str, str] = {}
    rank = {"left60": 0, "full_ket": 1, "full": 2}
    for f in sorted(SECTIONS.glob("*.tex")):
        if f.name.startswith("99-") and not include_backup:
            continue
        t = f.read_text(encoding="utf-8")
        for fr in re.findall(r"\\begin\{frame\}.*?\\end\{frame\}", t, flags=re.S):
            has_ket = "\\KetLuan" in fr
            for m in _PAT.finditer(fr):
                kind = "left60" if m.group(1) == "HinhChu" else "full_ket" if has_ket else "full"
                stem = Path(m.group(2)).stem
                if stem not in kinds or rank[kind] < rank[kinds[stem]]:
                    kinds[stem] = kind
    return kinds


def apply_style() -> None:
    plt.rcParams.update({
        "font.size": MAIN_PT, "axes.labelsize": MAIN_PT, "axes.titlesize": MAIN_PT, "xtick.labelsize": MIN_PT + 0.5,
        "ytick.labelsize": MIN_PT + 0.5, "legend.fontsize": MIN_PT + 0.5, "figure.titlesize": MAIN_PT + 1,
        "axes.linewidth": 0.9, "lines.linewidth": 1.8, "patch.linewidth": 0.8, "grid.linewidth": 0.6,
        "figure.dpi": 100, "savefig.dpi": 300,
    })


def new_figure(kind: str = "full_ket", **kw):
    """Figure whose size equals the insertion size (inch)."""
    apply_style()
    w, h = BOX_IN[kind]
    return plt.subplots(figsize=(w, h), **kw)


def _texts(fig: Figure):
    for t in fig.findobj(Text):
        if t.get_text().strip() and t.get_visible():
            yield t


def enforce_text(fig: Figure, min_pt: float = MIN_PT, scale: float = 1.0, max_pt: float = 11.0) -> float:
    """Scale every visible text by `scale` (new size / old size of the figure), clamp it to [min_pt, max_pt], return the smallest size."""
    smallest = 99.0
    for t in _texts(fig):
        fs = min(max(t.get_fontsize() * scale, min_pt), max_pt)
        t.set_fontsize(fs)
        smallest = min(smallest, fs)
    return smallest


TWEAKS: dict = {}   # name -> function(fig) run after the figure is resized and before the text rule is enforced


def tweak(name: str):
    def deco(fn):
        TWEAKS[name] = fn
        return fn
    return deco


def fix_tick_overlap(fig: Figure) -> None:
    """Rotate x tick labels by 30 degrees on axes whose labels overlap each other."""
    if getattr(fig, "_slide_no_rotate", False):
        return
    try:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
    except Exception:
        return
    for ax in fig.axes:
        labs = [l for l in ax.get_xticklabels() if l.get_text().strip() and l.get_visible()]
        if len(labs) < 2:
            continue
        boxes = [l.get_window_extent(r) for l in labs]
        if any(boxes[i].x1 > boxes[i + 1].x0 - 1 for i in range(len(boxes) - 1)) and not any(abs(l.get_rotation()) > 5 for l in labs):
            for l in labs:
                l.set_rotation(30)
                l.set_ha("right")
                l.set_rotation_mode("anchor")


def finish(fig: Figure, name: str, kind: str | None = None, script: str | None = None, drop_title: bool = True, pad: float = 0.04) -> Path:
    """Resize to the insertion box, enforce text >= 9 pt, trim white margins, save at 300 dpi, write the manifest."""
    kinds = figure_kinds()
    kind = kind or kinds.get(name, "full_ket")
    w, h = BOX_IN[kind]
    old_w = fig.get_size_inches()[0]
    fig.set_size_inches(w, h)
    scale = min(1.0, w / old_w) if old_w else 1.0
    axes = [a for a in fig.axes if a.get_label() != "<colorbar>"]
    for a in axes:
        for ln in a.get_lines():
            if ln.get_linewidth() < 1.4:
                ln.set_linewidth(1.4)
    if drop_title and len(axes) <= 1:
        for a in axes:
            a.set_title("")
        if fig._suptitle is not None:
            fig._suptitle.set_text("")
    if __import__("os").environ.get("SLIDE_DEBUG"):
        for i, a_ in enumerate(fig.axes):
            ps = a_.get_position()
            print("  AX", name, i, a_.get_label() or "", [round(x, 2) for x in (ps.x0, ps.y0, ps.width, ps.height)], repr(a_.get_title())[:50], repr(a_.get_xlabel())[:30], repr(a_.get_ylabel())[:30], "texts", len(a_.texts), "patches", len(a_.patches), "lines", len(a_.lines))
    if name in TWEAKS:
        TWEAKS[name](fig)
    smallest = enforce_text(fig, scale=scale, max_pt=getattr(fig, "_slide_max_pt", 11.0))
    for a_ in fig.axes:   # tick label sizes must live in tick_params, otherwise they are rebuilt at the default size when the figure is redrawn
        for axis in ("x", "y"):
            labs = [l for l in (a_.get_xticklabels() if axis == "x" else a_.get_yticklabels()) if l.get_text().strip()]
            if labs:
                a_.tick_params(axis=axis, labelsize=max(MIN_PT, min(labs[0].get_fontsize(), getattr(fig, "_slide_max_pt", 11.0))))
    if not getattr(fig, "_slide_no_layout", False):
        try:
            fig.tight_layout(pad=0.25)
        except Exception:
            pass
    fix_tick_overlap(fig)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    from PIL import Image
    save = getattr(Figure, "_slide_original_savefig", Figure.savefig)
    cur_w, cur_h = w, h
    for _ in range(8):
        save(fig, path, dpi=300, bbox_inches="tight", pad_inches=pad)
        px = Image.open(path).size
        s = min(w / (px[0] / 300.0), h / (px[1] / 300.0))   # display scale when the box limits the picture
        if s >= 0.995 or s < 0.75:   # below 0.75 the content does not fit the box: needs a tweak, do not shrink further
            break
        cur_w, cur_h = cur_w * s * 0.985, cur_h * s * 0.985     # text is kept at >= 9 pt, so shrink the drawing area instead
        fig.set_size_inches(cur_w, cur_h)
        if not getattr(fig, "_slide_no_layout", False):
            try:
                fig.tight_layout(pad=0.25)
            except Exception:
                pass
    smallest = min((t.get_fontsize() for t in _texts(fig)), default=MIN_PT)  # sizes unchanged by saving
    man = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    man[f"{name}.png"] = {"kind": kind, "min_pt": round(smallest, 2), "w_in": round(px[0] / 300.0, 3), "h_in": round(px[1] / 300.0, 3), "dpi": 300, "px": list(px),
                          "script": script or ""}
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    plt.close(fig)
    print("slide figure:", path.relative_to(ROOT), kind, f"min {smallest:.1f} pt")
    return path


def install(script: str = "") -> None:
    """Hook Figure.savefig: figures named in the slides are redrawn into figures/slide/; every other figure is not written."""
    kinds = figure_kinds()
    original = Figure.savefig

    def patched(self, fname, *a, **k):
        stem = Path(str(fname)).stem
        if stem in kinds and stem not in NOT_REDRAWN:
            finish(self, stem, kinds[stem], script=script)
            return None
        return None  # not used by the main deck: skip (the report keeps its own file)

    Figure.savefig = patched  # type: ignore[assignment]
    Figure._slide_original_savefig = original  # type: ignore[attr-defined]


# diagrams / tables that do not survive being shrunk (text overflows the boxes): they need a hand redraw, not a resize
NOT_REDRAWN = {"2-4_data_taxonomy", "3-3-4_constellation_sl", "3-4-1_pipeline_sl", "5-1_kien_truc_lakehouse_sl", "3-4-3_before_after_orders", "3-4-3_before_after_geolocation"}

ALL_SCRIPTS = [
    ("scripts/eda/distributions.py", []), ("scripts/eda/data_quality.py", []), ("scripts/eda/correlations.py", []), ("scripts/eda/funnel.py", []),
    ("scripts/eda/source_profile.py", []), ("scripts/eda/p8_outliers.py", []), ("scripts/eda/p8_seasonality.py", []),
    ("scripts/eda/p12c_categorical.py", []), ("scripts/geo_analysis.py", []), ("scripts/p9_results.py", ["--slide"]),
]


def run(script: str, args: list[str]) -> None:
    p = (ROOT / script).resolve() if not Path(script).is_absolute() else Path(script)
    sys.path.insert(0, str(p.parent))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.argv = [str(p)] + args
    install(str(p.relative_to(ROOT)).replace("\\", "/"))
    apply_style()
    runpy.run_path(str(p), run_name="__main__")


sys.modules.setdefault("slide_fig", sys.modules[__name__])  # when run as a script, tweaks must register in this module
sys.path.insert(0, str(Path(__file__).resolve().parent))
import slide_tweaks  # noqa: E402,F401  (registers TWEAKS)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--run":
        run(sys.argv[2], sys.argv[3:])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--all":
        import subprocess
        for s, extra in ALL_SCRIPTS:
            print("==", s)
            subprocess.run([sys.executable, str(Path(__file__).resolve()), "--run", s, *extra], cwd=ROOT, check=False)
    elif len(sys.argv) >= 2 and sys.argv[1] == "--kinds":
        for k, v in sorted(figure_kinds().items()):
            print(f"{k}\t{v}")
    else:
        print(__doc__)

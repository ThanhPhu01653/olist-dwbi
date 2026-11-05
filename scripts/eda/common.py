"""Shared helpers for the EDA scripts (P1): DB access on olist_full, chart style, number formatting, markdown output.

Run any script from the repo root, e.g.  python scripts/eda/profile.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from sqlalchemy import text

from etl import config
from etl.db import get_engine

FIG_DIR = ROOT / "figures"
HANDOFF_DIR = ROOT / "handoff"
DATABASE = config.DB_NAME_FULL  # all EDA runs on the full data set

# ---- palette (reference categorical palette, light mode; see dataviz skill) ----
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
CATEGORICAL = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
MUTED = "#898781"        # axis labels / de-emphasised marks
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
SEQ_BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# DW_DESIGN 6.2: state -> region (becomes seeds/state_region.csv in P2)
STATE_REGION = {
    **dict.fromkeys(["AC", "AP", "AM", "PA", "RO", "RR", "TO"], "Norte"),
    **dict.fromkeys(["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "Nordeste"),
    **dict.fromkeys(["DF", "GO", "MT", "MS"], "Centro-Oeste"),
    **dict.fromkeys(["ES", "MG", "RJ", "SP"], "Sudeste"),
    **dict.fromkeys(["PR", "RS", "SC"], "Sul"),
}
# GMV definition (DW_DESIGN section 9): price of orders that are not in the "Failed" status group
FAILED_STATUSES = ("canceled", "unavailable")
OK_ORDER = "o.order_status NOT IN ('canceled', 'unavailable')"

_engine = None


def engine():
    global _engine
    if _engine is None:
        _engine = get_engine(DATABASE)
    return _engine


def q(sql: str, **params) -> pd.DataFrame:
    with engine().connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or None)


def scalar(sql: str, **params):
    with engine().connect() as conn:
        return conn.execute(text(sql), params).scalar_one()


# ---- number formatting, Vietnamese style: 99.441 and 12,3% ----
def n(x, digits: int = 0) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    s = f"{x:,.{digits}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, digits: int = 1) -> str:
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else n(x, digits) + "%"


def setup_style() -> None:
    names = {f.name for f in font_manager.fontManager.ttflist}
    family = next((f for f in ("Segoe UI", "Arial", "Calibri") if f in names), "DejaVu Sans")
    plt.rcParams.update({
        "font.family": family, "font.size": 10, "figure.dpi": 100, "savefig.dpi": 200,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "axes.titlecolor": INK,
        "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
        "legend.frameon": False, "axes.unicode_minus": False,
    })


setup_style()


def vn_axis(ax, axis: str = "y", digits: int = 0) -> None:
    fmt = FuncFormatter(lambda v, _: n(v, digits))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def save(fig, name: str) -> str:
    FIG_DIR.mkdir(exist_ok=True)
    path = FIG_DIR / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("figure:", path.relative_to(ROOT))
    return f"figures/{name}.png"


def md_table(df: pd.DataFrame, align_right: list[str] | None = None) -> str:
    """Pandas frame -> GitHub markdown table. Values should already be formatted strings."""
    align_right = set(align_right or [])
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "| " + " | ".join("---:" if c in align_right else "---" for c in df.columns) + " |"
    rows = ["| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def write_md(name: str, lines: list[str]) -> None:
    HANDOFF_DIR.mkdir(exist_ok=True)
    path = HANDOFF_DIR / name
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("written:", path.relative_to(ROOT))


def source_note(script: str) -> str:
    return f"*Sinh tự động bởi `scripts/eda/{script}` trên database `{DATABASE}`; chạy lại script để cập nhật số liệu.*"


def direct_label_bars(ax, bars, fmt=lambda v: n(v), horizontal=False, pad=3) -> None:
    for b in bars:
        v = b.get_width() if horizontal else b.get_height()
        if horizontal:
            ax.annotate(fmt(v), (v, b.get_y() + b.get_height() / 2), xytext=(pad, 0), textcoords="offset points",
                        va="center", fontsize=8, color=INK2)
        else:
            ax.annotate(fmt(v), (b.get_x() + b.get_width() / 2, v), xytext=(0, pad), textcoords="offset points",
                        ha="center", fontsize=8, color=INK2)

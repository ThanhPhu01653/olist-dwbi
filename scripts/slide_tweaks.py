"""P12d: per-figure adjustments applied by scripts/slide_fig.py after the figure is resized to its insertion box.

Only the layout changes (labels shortened, panels re-arranged, minor text removed); data, colours and chart type stay.
A tweak receives the matplotlib figure; set `fig._slide_no_layout = True` when it positions the axes itself.
"""
from __future__ import annotations

import re

from slide_fig import tweak


def clear_titles(ax) -> None:
    for loc in ("left", "center", "right"):
        ax.set_title("", loc=loc)


def _title(ax) -> str:
    return ax.get_title("left") or ax.get_title("center") or ax.get_title("right")


@tweak("3-3-1_distributions_numeric")
def _distributions(fig):
    """Five histograms in one row; the boxplot row is dropped, the median label moves under the panel title."""
    axes = list(fig.axes)
    hist, box = axes[0::2], axes[1::2]
    for a in box:
        fig.delaxes(a)
    names = ["Giá", "Phí vận chuyển", "Thanh toán", "Lead time", "Ngày trễ"]
    units = ["BRL", "BRL", "BRL", "ngày", "ngày"]
    for i, a in enumerate(hist):
        med = ""
        for t in list(a.texts):
            med = t.get_text()
            t.set_visible(False)
        m = re.search(r"(-?[\d.,]+)\s*$", med.strip())
        a.set_title(f"{names[i]}\n(trung vị {m.group(1)})" if m else names[i], loc="center", fontsize=9.5)
        a.set_xlabel(units[i] + (", thang log" if i < 3 else ""), fontsize=9)
        if i:
            a.set_ylabel("")
        a.set_position([0.075 + i * 0.19, 0.17, 0.155, 0.56])
    fig._slide_no_layout = True


@tweak("3-3-1_delay_vs_review")
def _delay(fig):
    left, right = fig.axes[0], fig.axes[1]
    left.set_ylabel("Điểm review")
    left.set_xlabel("ngày giao − ngày dự kiến (âm = sớm)")
    clear_titles(left)
    clear_titles(right)
    left.set_title("Điểm theo ngày trễ", loc="center")
    for t in list(left.texts):
        t.set_visible(False)
    for t in list(right.texts):
        if t.get_text().startswith("n ="):
            t.set_visible(False)
    right.set_xticks(range(5))
    right.set_xticklabels(["Sớm", "Đúng hạn", "Trễ 1–3", "Trễ 4–7", "Trễ >7"])
    right.set_ylabel("Điểm TB")
    right.set_title("Điểm TB theo nhóm trễ", loc="center")


@tweak("3-3-1_late_rate_by_state")
def _late_state(fig):
    """27 horizontal bars do not fit at 9 pt: keep the 14 rows around the highest bar."""
    ax = fig.axes[0]
    bars = [p for p in ax.patches if p.get_width() > 0]
    n = len(bars)
    top = max(bars, key=lambda p: p.get_width())
    y_top = top.get_y() + top.get_height() / 2
    if y_top < n / 2:
        ax.set_ylim(13.5, -0.5)
    else:
        ax.set_ylim(n - 14.5, n - 0.5)


@tweak("3-3-1_pareto_category")
def _pareto(fig):
    a, b = fig.axes[0], fig.axes[1]
    clear_titles(a)
    clear_titles(b)
    a.set_title("Top 12 danh mục theo GMV", loc="center")
    b.set_title("Đường tích luỹ GMV", loc="center")
    b.set_xlabel("% số danh mục")
    for t in list(b.texts):
        t.set_text("18 danh mục\n(24,3%) tạo 80% GMV") if "18" in t.get_text() else None


def _strip_n(fig):
    for a in fig.axes:
        labs = [re.sub(r"\n?\(n=[^)]*\)", "", l.get_text()) for l in a.get_xticklabels()]
        if any(labs):
            a.set_xticks(a.get_xticks())
            a.set_xticklabels(labs)


@tweak("3-5-2_distance_vs_freight")
def _dist_freight(fig):
    _strip_n(fig)
    ax = fig.axes
    for a in ax:
        clear_titles(a)
    if len(ax) >= 2:
        ax[0].set_title("Phí theo khoảng cách", loc="center")
        ax[0].set_ylabel("Phí vận chuyển (BRL)")
        ax[0].set_xlabel("Khoảng cách (km)")
        ax[1].set_title("Phí TB theo nhóm", loc="center")
        ax[1].set_ylabel("Phí TB (BRL)")


@tweak("3-5-2_distance_vs_leadtime")
def _dist_lead(fig):
    _strip_n(fig)
    for a, ttl in zip(fig.axes, ["Lead time TB", "Tỷ lệ giao trễ"]):
        clear_titles(a)
        a.set_title(ttl, loc="center")


@tweak("3-1_cramer_v_heatmap_p")
def _cramer(fig):
    fig._slide_max_pt = 9.5
    for a in list(fig.axes):
        if a.get_position().width < 0.1:
            fig.delaxes(a)
            continue
        clear_titles(a)
        a.set_xlabel("")
        a.set_ylabel("")
        for l in a.get_xticklabels():
            l.set_rotation(30)
            l.set_ha("right")
            l.set_rotation_mode("anchor")


@tweak("3-1_theils_u_heatmap")
def _theil(fig):
    _cramer(fig)


from matplotlib.ticker import MaxNLocator  # noqa: E402


def _kill_fig_text(fig):
    if fig._suptitle is not None:
        fig._suptitle.set_text("")
    for t in list(fig.texts):
        t.set_visible(False)


@tweak("3-3-1_distributions_numeric")
def _distributions2(fig):
    _kill_fig_text(fig)
    axes = list(fig.axes)
    hist, box = axes[0::2], axes[1::2]
    for a in box:
        fig.delaxes(a)
    names = ["Giá", "Phí vận chuyển", "Thanh toán", "Lead time", "Ngày trễ"]
    units = ["BRL", "BRL", "BRL", "ngày", "ngày"]
    for i, a in enumerate(hist):
        med = ""
        for t in list(a.texts):
            med = t.get_text()
            t.set_visible(False)
        m = re.search(r"(-?[\d.,]+)\s*$", med.strip())
        clear_titles(a)
        a.set_title(f"{names[i]}\n(trung vị {m.group(1)})" if m else names[i], loc="center", fontsize=9.5)
        a.set_xlabel(units[i] + (", log" if i < 3 else ""), fontsize=9)
        a.yaxis.set_major_locator(MaxNLocator(3))
        a.xaxis.set_major_locator(MaxNLocator(3))
        if i:
            a.set_ylabel("")
        a.set_position([0.09 + i * 0.19, 0.2, 0.12, 0.56])
    fig._slide_no_layout = True


@tweak("3-3-1_data_quality")
def _quality(fig):
    ax = fig.axes[0]
    ax.set_ylim(9.5, -0.5) if ax.yaxis_inverted() or True else None
    labs = [l.get_text() for l in ax.get_yticklabels()]
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([x if len(x) <= 44 else x[:43] + "…" for x in labs])
    for t in list(ax.texts):
        t.set_fontsize(9)
    ax.set_xlabel("% số dòng của bảng bị ảnh hưởng (trục log)")


@tweak("2-4_tan_suat_cap_nhat")
def _tansuat(fig):
    _kill_fig_text(fig)
    axes = list(fig.axes)
    for i, a in enumerate(axes):
        a.yaxis.set_major_locator(MaxNLocator(2))
        a.xaxis.set_major_locator(MaxNLocator(4))
        a.set_title(_title(a) or "", fontsize=9)
        for tt in list(a.texts):
            tt.set_fontsize(9)
    for a in axes[:-2]:
        a.tick_params(axis="x", labelbottom=False)


@tweak("3-1_outliers_boxplot")
def _outliers(fig):
    _kill_fig_text(fig)
    names = ["Giá", "Phí VC", "Cân nặng", "Lead time", "Ngày trễ"]
    for k, a in enumerate(fig.axes):
        clear_titles(a)
        a.yaxis.set_major_locator(MaxNLocator(3))
        lab = a.get_xlabel().split("\n")
        a.set_xlabel(names[k] + "\n" + (lab[0] if lab else ""))


def crop_rows(ax, k: int) -> None:
    """Show the k horizontal bars around the longest bar (rows that do not fit at 9 pt are cropped, still in the data)."""
    bars = [p for p in ax.patches if p.get_width() > 0]
    n = len(bars)
    top = max(bars, key=lambda p: p.get_width())
    y_top = top.get_y() + top.get_height() / 2
    if y_top < n / 2:
        ax.set_ylim(k - 0.5, -0.5)
    else:
        ax.set_ylim(n - k - 0.5, n - 0.5)


@tweak("3-3-1_data_quality")
def _quality2(fig):
    ax = fig.axes[0]
    labs = [l.get_text() for l in ax.get_yticklabels()]
    ax.set_yticks(ax.get_yticks())
    ax.set_yticklabels([x if len(x) <= 46 else x[:45] + "…" for x in labs])
    crop_rows(ax, 10)
    ax.set_xlabel("% số dòng của bảng bị ảnh hưởng (trục log)")


def _wrap_heat_labels(fig):
    wrap = {"Thanh toán": "Thanh\ntoán", "Ngành hàng": "Ngành\nhàng", "Vùng khách": "Vùng\nkhách", "Vùng seller": "Vùng\nseller", "Trạng thái": "Trạng\nthái", "Cờ trễ": "Cờ\ntrễ"}
    fig._slide_max_pt = 9.5
    fig._slide_no_rotate = True
    for a in list(fig.axes):
        if a.get_position().width < 0.1:
            fig.delaxes(a)
            continue
        clear_titles(a)
        a.set_xlabel("")
        a.set_ylabel("")
        a.set_xticklabels([wrap.get(l.get_text(), l.get_text()) for l in a.get_xticklabels()], rotation=0, ha="center")
        a.tick_params(axis="x", length=0, pad=2)
        a.tick_params(axis="y", length=0, pad=2)
        a.set_aspect("auto")


@tweak("3-1_cramer_v_heatmap_p")
def _cramer3(fig):
    _wrap_heat_labels(fig)


@tweak("3-1_theils_u_heatmap")
def _theil3(fig):
    _wrap_heat_labels(fig)


@tweak("3-1_stl_daily")
def _stl(fig):
    _kill_fig_text(fig)
    names = ["Quan sát", "Xu hướng", "Mùa vụ", "Phần dư"]
    for i, a in enumerate(fig.axes):
        clear_titles(a)
        a.set_ylabel(names[i], rotation=0, ha="right", va="center", fontsize=9, labelpad=4)
        a.yaxis.set_major_locator(MaxNLocator(2))
        a.xaxis.set_major_locator(MaxNLocator(4))
        if i < len(fig.axes) - 1:
            a.tick_params(axis="x", labelbottom=False)


def _shrink_legend(leg, fs=9.0):
    if leg is None:
        return
    for t in leg.get_texts():
        t.set_fontsize(fs)
    leg._legend_box.sep = 2
    try:
        leg.handlelength = 1.2
        leg.columnspacing = 0.8
        leg.handletextpad = 0.4
    except Exception:
        pass


def _move_fig_legend(fig, ax, loc, ncol=1, anchor=None):
    leg = (fig.legends or [None])[0] or ax.get_legend()
    if leg is None:
        return
    handles = list(getattr(leg, "legend_handles", getattr(leg, "legendHandles", [])))
    labels = [t.get_text() for t in leg.get_texts()]
    for l in list(fig.legends):
        l.remove()
    if ax.get_legend() is not None:
        ax.get_legend().remove()
    kw = dict(loc=loc, ncol=ncol, fontsize=9, frameon=False, handlelength=1.2, columnspacing=0.8, handletextpad=0.4)
    if anchor:
        kw["bbox_to_anchor"] = anchor
    ax.legend(handles, labels, **kw)


@tweak("3-3-1_funnel_seller_overlap")
def _funnel(fig):
    ax = fig.axes[0]
    fig._slide_max_pt = 10
    _move_fig_legend(fig, ax, "upper center", 1, (0.5, 0.0))
    for t in ax.texts:
        t.set_fontsize(10)


@tweak("5-2_gmv_dau_nguoi_theo_bang_sl")
def _gmv(fig):
    ax = fig.axes[0]
    fig._slide_max_pt = 10
    _move_fig_legend(fig, ax, "upper right", 2)
    ax.set_xlabel("")
    labs = [l.get_text().split("\n")[0] for l in ax.get_xticklabels()]
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(labs)
    fig._slide_no_rotate = True
    for t in list(ax.texts):
        if "bang khác" in t.get_text() or "bảng khác" in t.get_text():
            t.set_visible(False)
        else:
            t.set_fontsize(9)


def _short_km(ax):
    n = len(ax.get_xticks())
    if n == 4:
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(["<100", "100–500", "500–1000", ">1000"], rotation=0, ha="center")
        ax.set_xlabel("Khoảng cách (km)")


@tweak("3-5-2_distance_vs_leadtime")
def _dist_lead2(fig):
    _strip_n(fig)
    fig._slide_no_rotate = True
    for a, ttl in zip(fig.axes, ["Lead time TB (ngày)", "Tỷ lệ giao trễ (%)"]):
        clear_titles(a)
        a.set_title(ttl, loc="center")
        a.set_ylabel("")
        _short_km(a)


@tweak("3-5-2_distance_vs_freight")
def _dist_freight2(fig):
    _strip_n(fig)
    fig._slide_no_rotate = True
    ax = fig.axes
    for a in ax:
        clear_titles(a)
    ax[0].set_title("Phí theo khoảng cách", loc="center")
    ax[0].set_ylabel("Phí (BRL)")
    ax[0].set_xlabel("Khoảng cách (km)")
    ax[1].set_title("Phí TB theo nhóm (BRL)", loc="center")
    ax[1].set_ylabel("")
    _short_km(ax[1])

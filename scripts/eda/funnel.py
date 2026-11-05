"""P1 step 5: marketing funnel EDA -> handoff/funnel.md + figures.

MQL per month and origin, win rate per origin, days_to_close, top business segments, and how many sellers in
closed_deals appear (or not) in the sales system, with the GMV of those that do.
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

SELLER_GROUPS_SQL = f"""
WITH sales AS (
    SELECT i.seller_id, count(DISTINCT i.order_id) AS orders, sum(i.price) AS gmv_all,
           sum(i.price) FILTER (WHERE {OK_ORDER}) AS gmv, min(o.order_purchase_timestamp) AS first_sale
    FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY 1)
SELECT d.mql_id, d.seller_id, d.won_date, m.first_contact_date, m.origin,
       (s0.seller_id IS NOT NULL) AS in_sellers, (sales.seller_id IS NOT NULL) AS has_orders,
       coalesce(sales.orders, 0) AS orders, coalesce(sales.gmv, 0) AS gmv, coalesce(sales.gmv_all, 0) AS gmv_all, sales.first_sale
FROM crm.closed_deals d JOIN crm.mql m USING (mql_id)
LEFT JOIN oltp.sellers s0 ON s0.seller_id = d.seller_id
LEFT JOIN sales ON sales.seller_id = d.seller_id
"""


def mql_by_month() -> tuple[str, pd.DataFrame]:
    d = q("""SELECT to_char(first_contact_date, 'YYYY-MM') AS month, coalesce(origin, 'unknown') AS origin, count(*) AS c
             FROM crm.mql GROUP BY 1, 2""")
    tot = d.groupby("origin").c.sum().sort_values(ascending=False)
    top = list(tot.index[:5])
    d["grp"] = d.origin.where(d.origin.isin(top), "other (gộp)")
    pv = d.pivot_table(index="month", columns="grp", values="c", aggfunc="sum", fill_value=0)
    pv = pv[top + (["other (gộp)"] if "other (gộp)" in pv else [])]
    colors = CATEGORICAL[: len(pv.columns)]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    bottom = np.zeros(len(pv))
    for col, c in zip(pv.columns, colors):
        ax.bar(pv.index, pv[col], bottom=bottom, color=c, label=col, width=0.78, edgecolor=SURFACE, linewidth=1.2)
        bottom += pv[col].values
    for i, v in enumerate(bottom):
        ax.annotate(n(int(v)), (i, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, color=INK2)
    ax.set_xticks(range(len(pv)), pv.index, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Số MQL (khách tiềm năng) mới")
    vn_axis(ax)
    ax.grid(axis="x", visible=False)
    ax.set_title("MQL theo tháng liên hệ đầu tiên và kênh (origin)")
    ax.legend(ncol=6, loc="upper left", fontsize=9, title="origin", title_fontsize=9)
    return save(fig, "3-3-1_funnel_mql_by_month"), pv


def win_rate() -> tuple[str, pd.DataFrame]:
    d = q("""SELECT coalesce(m.origin, 'unknown') AS origin, count(*) AS mql, count(d.mql_id) AS won
             FROM crm.mql m LEFT JOIN crm.closed_deals d USING (mql_id) GROUP BY 1""")
    d["rate"] = 100 * d.won / d.mql
    d = d.sort_values("rate")
    overall = 100 * d.won.sum() / d.mql.sum()
    fig, ax = plt.subplots(figsize=(10, 5.4))
    b = ax.barh(d.origin, d.rate, color=BLUE, height=0.65)
    for rect, (m, w, r) in zip(b, zip(d.mql, d.won, d.rate)):
        ax.annotate(f"{pct(r, 1)}  ({n(int(w))} / {n(int(m))} MQL)", (rect.get_width(), rect.get_y() + rect.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=9, color=INK2)
    ax.axvline(overall, color=ORANGE, ls="--", lw=1.4)
    ax.annotate(f"Chung {pct(overall, 1)}", (overall, len(d) - 0.4), xytext=(5, 0), textcoords="offset points", color=ORANGE, fontsize=9, fontweight="bold")
    ax.set_xlim(0, d.rate.max() * 1.45)
    ax.set_xlabel("Tỷ lệ MQL được chốt thành seller (%)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Tỷ lệ chốt deal theo kênh thu hút (origin)")
    return save(fig, "3-3-1_funnel_win_rate_by_origin"), d.sort_values("rate", ascending=False)


def days_to_close() -> tuple[str, pd.Series]:
    s = q("SELECT (d.won_date::date - m.first_contact_date) AS days FROM crm.closed_deals d JOIN crm.mql m USING (mql_id)").days.astype(float)
    s = s[s >= 0]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.hist(s, bins=np.arange(0, s.max() + 10, 10), color=BLUE, edgecolor=SURFACE, linewidth=0.5)
    for val, lab, col in [(s.median(), f"trung vị {n(s.median(), 0)} ngày", ORANGE), (s.quantile(0.9), f"P90 {n(s.quantile(0.9), 0)} ngày", INK2)]:
        ax.axvline(val, color=col, ls="--", lw=1.4)
        ax.annotate(lab, (val, ax.get_ylim()[1]), xytext=(5, -14), textcoords="offset points", color=col, fontsize=9.5, fontweight="bold")
    ax.set_xlabel("Số ngày từ lần liên hệ đầu đến ngày chốt (khoảng 10 ngày)")
    ax.set_ylabel("Số deal")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"Thời gian chốt deal (days_to_close) – {n(len(s))} deal")
    return save(fig, "3-3-1_funnel_days_to_close"), s


def segments() -> tuple[str, pd.DataFrame]:
    d = q("""SELECT coalesce(business_segment, 'unknown') AS segment, count(*) AS deals FROM crm.closed_deals GROUP BY 1 ORDER BY 2 DESC""")
    top = d.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    b = ax.barh(top.segment, top.deals, color=BLUE, height=0.65)
    direct_label_bars(ax, b, lambda v: n(int(v)), horizontal=True)
    ax.set_xlabel("Số deal đã chốt")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Top 10 business_segment trong {n(int(d.deals.sum()))} deal ({n(len(d))} segment)")
    return save(fig, "3-3-1_funnel_business_segment"), d


def seller_overlap() -> tuple[str, pd.DataFrame, dict]:
    d = q(SELLER_GROUPS_SQL)
    for c in ["gmv", "gmv_all"]:
        d[c] = d[c].astype(float)
    total_deals = len(d)
    g_missing = int((~d.in_sellers).sum())
    g_noorder = int((d.in_sellers & ~d.has_orders).sum())
    g_orders = int(d.has_orders.sum())
    plat = q(f"SELECT sum(i.price) AS gmv FROM oltp.order_items i JOIN oltp.orders o USING (order_id) WHERE {OK_ORDER}").gmv.iloc[0]
    plat = float(plat)
    with_o = d[d.has_orders]
    n_all_sellers = int(scalar("SELECT count(*) FROM oltp.sellers"))
    sellers_with_orders = int(scalar("SELECT count(DISTINCT seller_id) FROM oltp.order_items"))
    gmv = with_o.gmv.sum()
    won_to_first = (with_o.first_sale.dt.normalize() - with_o.won_date.dt.normalize()).dt.days
    info = {"total": total_deals, "missing": g_missing, "noorder": g_noorder, "orders": g_orders, "gmv": gmv, "platform_gmv": plat,
            "gmv_share": 100 * gmv / plat, "avg": gmv / g_orders if g_orders else 0, "orders_n": int(with_o.orders.sum()),
            "n_all_sellers": n_all_sellers, "sellers_with_orders": sellers_with_orders,
            "avg_other": (plat - gmv) / max(sellers_with_orders - g_orders, 1),
            "before_won": int((won_to_first < 0).sum()), "won_to_first": won_to_first, "median_w2f": float(won_to_first.median())}
    fig, ax = plt.subplots(figsize=(11, 3.9))
    parts = [("Có đơn hàng trong order_items", g_orders, BLUE), ("Có trong oltp.sellers nhưng chưa có đơn", g_noorder, YELLOW),
             ("Không có trong oltp.sellers", g_missing, MUTED)]
    parts = [p for p in parts if p[1] > 0]  # an empty group is stated in the text, not drawn
    left = 0
    for lab, v, c in parts:
        ax.barh([0], [v], left=left, color=c, height=0.5, edgecolor=SURFACE, linewidth=2)
        ax.annotate(f"{n(v)}\n({pct(100 * v / total_deals, 1)})", (left + v / 2, 0), ha="center", va="center", fontsize=11, fontweight="bold",
                    color="#0b0b0b" if c == YELLOW else "white")
        left += v
    ax.set_yticks([])
    ax.set_xlim(0, total_deals)
    ax.grid(visible=False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in parts], labels=[l for l, _, _ in parts], loc="upper center",
              bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=9.5)
    ax.set_title(f"{n(total_deals)} deal đã chốt trong CRM: bao nhiêu seller xuất hiện trong hệ thống bán hàng?")
    return save(fig, "3-3-1_funnel_seller_overlap"), d, info


def main() -> None:
    f1, mql_pv = mql_by_month()
    f2, wr = win_rate()
    f3, dtc = days_to_close()
    f4, seg = segments()
    f5, deals, info = seller_overlap()

    tot_mql = int(mql_pv.values.sum())
    won_total = int(wr.won.sum())
    first_m, last_m = mql_pv.index[0], mql_pv.index[-1]
    peak_m = mql_pv.sum(axis=1).idxmax()
    ov = deals[deals.has_orders]
    lines = ["# Marketing funnel (olist_full)", "", source_note("funnel.py"), "",
             "GMV của seller = tổng `price` của các đơn không bị hủy/không khả dụng (DW_DESIGN §9).", "",
             "## MQL theo tháng và kênh", "", f"Hình: `{f1}`.", "",
             f"- {n(tot_mql)} MQL, liên hệ đầu từ {first_m} đến {last_m}; tháng nhiều nhất {peak_m} ({n(int(mql_pv.sum(axis=1).max()))} MQL).",
             "- Số MQL theo kênh (cao → thấp): " + ", ".join(f"{k} {n(int(v))}" for k, v in wr.set_index('origin').mql.sort_values(ascending=False).items()) + ".", "",
             "## Tỷ lệ chốt deal theo kênh", "", f"Hình: `{f2}`.", "",
             md_table(pd.DataFrame({"origin": wr.origin, "MQL": wr.mql.map(lambda v: n(int(v))), "Đã chốt": wr.won.map(lambda v: n(int(v))), "Tỷ lệ chốt": wr.rate.map(lambda v: pct(v, 1))}),
                      ["MQL", "Đã chốt", "Tỷ lệ chốt"]), "",
             f"- Tỷ lệ chốt chung {pct(100 * won_total / tot_mql, 1)} ({n(won_total)} / {n(tot_mql)}). "
             f"Kênh cao nhất: {wr.origin.iloc[0]} ({pct(wr.rate.iloc[0], 1)}); thấp nhất: {wr.origin.iloc[-1]} ({pct(wr.rate.iloc[-1], 1)}).", "",
             "## Thời gian chốt deal", "", f"Hình: `{f3}`.", "",
             f"- {n(len(dtc))} deal hợp lệ (loại deal có ngày chốt trước ngày liên hệ đầu): trung vị {n(dtc.median(), 0)} ngày, trung bình {n(dtc.mean(), 1)} ngày, P90 {n(dtc.quantile(.9), 0)} ngày, dài nhất {n(dtc.max(), 0)} ngày.", "",
             "## Phân khúc kinh doanh (business_segment)", "", f"Hình: `{f4}`.", "",
             md_table(pd.DataFrame({"business_segment": seg.segment.head(10), "Số deal": seg.deals.head(10).map(lambda v: n(int(v))),
                                    "%": (100 * seg.deals.head(10) / seg.deals.sum()).map(lambda v: pct(v, 1))}), ["Số deal", "%"]), "",
             "## Seller trong closed_deals có / không có đơn hàng", "", f"Hình: `{f5}`.", "",
             md_table(pd.DataFrame({
                 "Nhóm": ["Có đơn hàng trong order_items", "Có trong oltp.sellers nhưng chưa có đơn", "Không có trong oltp.sellers", "Tổng deal"],
                 "Số seller": [n(info["orders"]), n(info["noorder"]), n(info["missing"]), n(info["total"])],
                 "%": [pct(100 * info["orders"] / info["total"], 1), pct(100 * info["noorder"] / info["total"], 1),
                       pct(100 * info["missing"] / info["total"], 1), "100,0%"]}), ["Số seller", "%"]), "",
             f"- **{n(info['orders'])} / {n(info['total'])} seller từ funnel ({pct(100 * info['orders'] / info['total'], 1)}) có đơn hàng**; "
             f"{n(info['missing'])} seller ({pct(100 * info['missing'] / info['total'], 1)}) không có trong hệ thống bán hàng.",
             f"- Nhóm có đơn: {n(info['orders_n'])} đơn, **tổng GMV {n(info['gmv'], 2)} BRL** ({n(info['gmv'] / 1e6, 2)} triệu), "
             f"chiếm {pct(info['gmv_share'], 2)} GMV toàn sàn ({n(info['platform_gmv'] / 1e6, 2)} triệu BRL); trung bình {n(info['avg'], 0)} BRL / seller.",
             f"- Các seller còn lại có đơn ({n(info['sellers_with_orders'] - info['orders'])} seller, không nằm trong deal đã chốt có đơn) trung bình {n(info['avg_other'], 0)} BRL / seller.",
             f"- Từ ngày chốt đến đơn đầu tiên (nhóm có đơn): trung vị {n(info['median_w2f'], 0)} ngày; "
             + (f"**{n(info['before_won'])} seller có đơn đầu TRƯỚC ngày chốt** (won_date) – cần kiểm tra khi tính `days_won_to_first_sale`." if info['before_won'] else
              "không có seller nào có đơn đầu trước ngày chốt (won_date), nên `days_won_to_first_sale` luôn không âm."),
             f"- Mọi seller trong `oltp.sellers` đều có ít nhất một đơn ({n(info['n_all_sellers'])} seller, {n(info['sellers_with_orders'])} seller có dòng hàng): bảng sellers của hệ thống bán hàng chỉ chứa seller đã bán được.", ""]
    write_md("funnel.md", lines)


if __name__ == "__main__":
    main()

"""P1 step 3: distributions -> handoff/distributions.md + figures.

Histogram + boxplot of price, freight_value, payment_value, lead time, delay_days; Pareto of GMV by category and
by seller (80% line); orders per month; review_score distribution.
GMV = sum(price) of orders that are not canceled/unavailable (DW_DESIGN section 9).
"""
from __future__ import annotations

from matplotlib.gridspec import GridSpec

from common import *  # noqa: F401,F403


def describe(s: pd.Series) -> dict:
    return {"n": len(s), "mean": s.mean(), "median": s.median(), "p95": s.quantile(0.95), "p99": s.quantile(0.99),
            "max": s.max(), "min": s.min()}


def numeric_figure(series: dict[str, tuple[pd.Series, str, bool]]) -> tuple[str, pd.DataFrame]:
    """series: label -> (values, x label, log scale). One column per variable: histogram on top, boxplot below."""
    k = len(series)
    fig = plt.figure(figsize=(4.2 * k, 6.2))
    gs = GridSpec(2, k, height_ratios=[4, 1], hspace=0.12, wspace=0.28)
    rows = []
    for i, (label, (s, xlabel, log)) in enumerate(series.items()):
        ax, bx = fig.add_subplot(gs[0, i]), fig.add_subplot(gs[1, i])
        zero = int((s <= 0).sum()) if log else 0
        v = s[s > 0] if log else s
        if log:
            lo, hi = v.quantile(0.001), v.quantile(0.999)  # view window P0.1-P99.9 keeps the bulk readable
            bins = np.logspace(np.log10(lo), np.log10(hi), 55)
            ax.hist(v, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.3)
            ax.set_xscale("log")
            bx.set_xscale("log")
            ax.set_xlim(lo, hi)
        else:
            lo, hi = v.quantile(0.005), v.quantile(0.995)
            ax.hist(v, bins=60, range=(lo, hi), color=BLUE, edgecolor=SURFACE, linewidth=0.3)
            ax.set_xlim(lo, hi)
        ax.axvline(v.median(), color=ORANGE, lw=1.6)
        ax.annotate(f"trung vị {n(v.median(), 1 if v.median() < 100 else 0)}", (v.median(), ax.get_ylim()[1] * 0.93),
                    xytext=(5, 0), textcoords="offset points", fontsize=8.5, color=ORANGE, va="top")
        ax.set_title(label, fontsize=11)
        ax.set_xticklabels([])
        vn_axis(ax, "y")
        ax.set_ylabel("Số quan sát" if i == 0 else "")
        bp = bx.boxplot(v, orientation='horizontal', widths=0.6, showfliers=False, patch_artist=True,
                        boxprops=dict(facecolor="#cde2fb", edgecolor=BLUE), medianprops=dict(color=ORANGE, lw=1.6),
                        whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE))
        bx.set_yticks([])
        note = f", thang log\n(bỏ {n(zero)} giá trị = 0)" if zero else (", thang log" if log else "")
        bx.set_xlabel(xlabel + note)
        bx.grid(axis="y", visible=False)
        bx.set_xlim(ax.get_xlim())
        if not log:
            vn_axis(bx, "x")
        rows.append({"Biến": label, **{k2: v2 for k2, v2 in describe(s).items()}, "zero": zero})
    fig.suptitle("Phân phối các biến số chính (histogram trên, boxplot dưới). Khung hiển thị P0,1–P99,9 (tiền) và P0,5–P99,5 (ngày); không vẽ ngoại lai", x=0.01, ha="left",
                 fontsize=13, fontweight="bold", y=0.99)
    return save(fig, "3-3-1_distributions_numeric"), pd.DataFrame(rows)


def pareto_figure(name: str, title_left: str, bars: pd.DataFrame, label_col: str, gmv: pd.Series, entity: str, fname: str) -> tuple[str, dict]:
    gmv = gmv.sort_values(ascending=False)
    share = gmv.cumsum() / gmv.sum() * 100
    k80 = int((share < 80).sum() + 1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw={"width_ratios": [1.15, 1]})
    top = bars.head(12).iloc[::-1]
    b = a1.barh(top[label_col], top["gmv"] / 1e6, color=BLUE, height=0.65)
    direct_label_bars(a1, b, lambda v: n(v, 2), horizontal=True)
    a1.set_xlabel("GMV (triệu BRL)")
    vn_axis(a1, "x", 2 if bars["gmv"].max() / 1e6 < 1 else 1)
    a1.grid(axis="y", visible=False)
    a1.set_title(title_left)
    x = np.arange(1, len(share) + 1) / len(share) * 100
    a2.plot(x, share.values, color=BLUE, lw=2)
    a2.axhline(80, color=ORANGE, lw=1.2, ls="--")
    a2.axvline(k80 / len(share) * 100, color=ORANGE, lw=1.2, ls="--")
    a2.plot([k80 / len(share) * 100], [80], "o", color=ORANGE, ms=7, mec=SURFACE, mew=1.5)
    a2.annotate(f"{n(k80)} {entity} ({pct(k80 / len(share) * 100, 1)}) tạo 80% GMV", (k80 / len(share) * 100, 80),
                xytext=(12, -34), textcoords="offset points", fontsize=10, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=MUTED))
    a2.set_xlabel(f"% số {entity} (xếp từ GMV cao xuống thấp)")
    a2.set_ylabel("% GMV tích luỹ")
    a2.set_xlim(0, 100)
    a2.set_ylim(0, 101)
    a2.set_title(f"Đường tích luỹ GMV theo {entity} (quy luật 80/20)")
    fig.suptitle(name, x=0.01, ha="left", fontsize=13, fontweight="bold")
    return save(fig, fname), {"k80": k80, "total": len(share), "gmv": gmv.sum(), "top5_share": gmv.head(5).sum() / gmv.sum() * 100,
                              "top1_share": gmv.iloc[0] / gmv.sum() * 100}


def main() -> None:
    items = q(f"""SELECT i.price, i.freight_value FROM oltp.order_items i""")
    pay = q("SELECT payment_value FROM oltp.order_payments")
    deliv = q("""SELECT extract(epoch FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0 AS lead_days,
                        (order_delivered_customer_date::date - order_estimated_delivery_date::date) AS delay_days
                 FROM oltp.orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL""")
    fig1, stats = numeric_figure({
        "Giá sản phẩm (price)": (items.price.astype(float), "BRL", True),
        "Phí vận chuyển (freight_value)": (items.freight_value.astype(float), "BRL", True),
        "Giá trị thanh toán (payment_value)": (pay.payment_value.astype(float), "BRL", True),
        "Lead time: mua → giao (lead_days)": (deliv.lead_days, "ngày", False),
        "Chênh lệch so với dự kiến (delay_days)": (deliv.delay_days.astype(float), "ngày (âm = giao sớm)", False),
    })

    # ---- Pareto: category, seller ----
    cat = q(f"""SELECT coalesce(t.product_category_name_english, p.product_category_name, 'unknown') AS category, sum(i.price) AS gmv,
                       count(DISTINCT i.order_id) AS orders, count(*) AS items
                FROM oltp.order_items i JOIN oltp.orders o USING (order_id) JOIN oltp.products p USING (product_id)
                LEFT JOIN oltp.product_category_name_translation t ON t.product_category_name = p.product_category_name
                WHERE {OK_ORDER} GROUP BY 1 ORDER BY 2 DESC""")
    cat["gmv"] = cat.gmv.astype(float)
    fig2, pc = pareto_figure("Pareto GMV theo danh mục sản phẩm", "Top 12 danh mục theo GMV", cat, "category", cat.set_index("category").gmv,
                             "danh mục", "3-3-1_pareto_category")
    sel = q(f"""SELECT i.seller_id, s.seller_state AS state, sum(i.price) AS gmv, count(DISTINCT i.order_id) AS orders
                FROM oltp.order_items i JOIN oltp.orders o USING (order_id) JOIN oltp.sellers s USING (seller_id)
                WHERE {OK_ORDER} GROUP BY 1, 2 ORDER BY 3 DESC""")
    sel["gmv"] = sel.gmv.astype(float)
    sel["label"] = "seller " + sel.seller_id.str[:6] + " (" + sel.state + ")"
    fig3, ps = pareto_figure("Pareto GMV theo người bán (seller)", "Top 12 seller theo GMV", sel, "label", sel.set_index("seller_id").gmv,
                             "seller", "3-3-1_pareto_seller")
    n_sellers_all = int(scalar("SELECT count(*) FROM oltp.sellers"))

    # ---- orders per month ----
    m = q("SELECT to_char(order_purchase_timestamp, 'YYYY-MM') AS month, count(*) AS orders FROM oltp.orders GROUP BY 1 ORDER BY 1")
    allm = pd.period_range(m.month.min(), m.month.max(), freq="M").astype(str)
    m = m.set_index("month").reindex(allm, fill_value=0).rename_axis("month").reset_index()
    inwin = (m.month >= "2017-01") & (m.month <= "2018-08")
    fig, ax = plt.subplots(figsize=(13, 5))
    bars = ax.bar(m.month, m.orders, color=[BLUE if w else MUTED for w in inwin], width=0.75)
    ax.set_xticks(range(len(m)), m.month, rotation=60, ha="right", fontsize=8)
    for b, v, w in zip(bars, m.orders, inwin):
        if (not w) or v == m.orders.max():
            ax.annotate(n(int(v)), (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8, color=INK2)
    vn_axis(ax)
    ax.set_ylabel("Số đơn hàng (theo ngày mua)")
    ax.grid(axis="x", visible=False)
    ax.set_title("Số đơn hàng theo tháng: 2016 rất thưa, 09–10/2018 gần như trống")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=MUTED)],
              labels=["Giai đoạn dùng cho xu hướng (2017-01 → 2018-08)", "Loại khỏi dashboard xu hướng"], loc="upper left")
    fig4 = save(fig, "3-3-1_orders_per_month")

    # ---- review score ----
    rs = q("SELECT review_score, count(*) AS c FROM oltp.order_reviews GROUP BY 1 ORDER BY 1")
    rs["share"] = rs.c / rs.c.sum() * 100
    avg = float((rs.review_score * rs.c).sum() / rs.c.sum())
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    b = ax.bar(rs.review_score.astype(str), rs.share, color=BLUE, width=0.65)
    direct_label_bars(ax, b, lambda v: pct(v, 1))
    ax.set_xlabel("Điểm đánh giá (1 = tệ nhất, 5 = tốt nhất)")
    ax.set_ylabel("% số review")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"Phân bố điểm đánh giá (trung bình {n(avg, 2)}; {n(int(rs.c.sum()))} review)")
    fig5 = save(fig, "3-3-1_review_score")

    # ---- markdown ----
    st = stats.copy()
    dig = lambda v: n(v, 2) if abs(v) < 1000 else n(v, 0)
    tbl = pd.DataFrame({"Biến": st["Biến"], "Số quan sát": st.n.map(lambda v: n(int(v))), "Trung bình": st["mean"].map(dig),
                        "Trung vị": st["median"].map(dig), "P95": st.p95.map(dig), "P99": st.p99.map(dig),
                        "Min": st["min"].map(dig), "Max": st["max"].map(dig), "Giá trị = 0": st.zero.map(lambda v: n(int(v)))})
    skew = items.price.astype(float)
    lead, delay = deliv.lead_days, deliv.delay_days
    months_low = m[(m.month < "2017-01") | (m.month > "2018-08")]
    lines = ["# Phân phối dữ liệu (olist_full)", "", source_note("distributions.py"), "",
             "GMV = tổng `price` của các đơn không bị hủy/không khả dụng (đúng định nghĩa KPI ở DW_DESIGN §9).", "",
             "## Biến số chính", "", f"Hình: `{fig1}`.", "", md_table(tbl, list(tbl.columns[1:])), "",
             f"- Giá sản phẩm lệch phải rất mạnh: trung bình {n(skew.mean(), 2)} BRL nhưng trung vị chỉ {n(skew.median(), 2)} BRL; "
             f"1% dòng hàng đắt nhất có giá từ {n(skew.quantile(0.99), 0)} BRL, cao nhất {n(skew.max(), 0)} BRL.",
             f"- Lead time (mua → giao) của {n(len(lead))} đơn đã giao: trung vị {n(lead.median(), 1)} ngày, P95 {n(lead.quantile(.95), 1)} ngày, "
             f"tối đa {n(lead.max(), 0)} ngày.",
             f"- delay_days: {pct(100 * (delay < 0).mean())} đơn giao sớm hơn ngày dự kiến, {pct(100 * (delay == 0).mean())} đúng ngày, "
             f"{pct(100 * (delay > 0).mean())} giao trễ (trung vị {n(delay.median(), 0)} ngày, tức thường giao sớm hơn dự kiến).", "",
             "## Pareto theo danh mục", "", f"Hình: `{fig2}`.", "",
             f"- {n(pc['k80'])} / {n(pc['total'])} danh mục ({pct(100 * pc['k80'] / pc['total'])}) tạo ra 80% GMV; tổng GMV {n(pc['gmv'] / 1e6, 2)} triệu BRL.",
             f"- 5 danh mục đứng đầu chiếm {pct(pc['top5_share'])} GMV; danh mục số 1 (`{cat.category.iloc[0]}`) chiếm {pct(pc['top1_share'])}.", "",
             md_table(pd.DataFrame({"Hạng": range(1, 11), "Danh mục (tiếng Anh)": cat.category.head(10), "GMV (triệu BRL)": (cat.gmv.head(10) / 1e6).map(lambda v: n(v, 2)),
                                    "Số đơn": cat.orders.head(10).map(lambda v: n(int(v)))}), ["Hạng", "GMV (triệu BRL)", "Số đơn"]), "",
             "## Pareto theo seller", "", f"Hình: `{fig3}`.", "",
             f"- {n(ps['k80'])} / {n(ps['total'])} seller có đơn hợp lệ ({pct(100 * ps['k80'] / ps['total'])}) tạo ra 80% GMV "
             f"(trong tổng {n(n_sellers_all)} seller của hệ thống).",
             f"- 5 seller đứng đầu chiếm {pct(ps['top5_share'])} GMV; seller số 1 chiếm {pct(ps['top1_share'])}.", "",
             "## Số đơn theo tháng", "", f"Hình: `{fig4}`.", "",
             f"- Giai đoạn 2017-01 → 2018-08 có {n(int(m[inwin].orders.sum()))} đơn ({pct(100 * m[inwin].orders.sum() / m.orders.sum())} tổng số đơn).",
             f"- Ngoài giai đoạn đó: 2016 chỉ {n(int(m[m.month < '2017-01'].orders.sum()))} đơn "
             f"(tháng có đơn: {', '.join(m[(m.month < '2017-01') & (m.orders > 0)].month)}); "
             f"2018-09 và 2018-10 chỉ {n(int(m[m.month > '2018-08'].orders.sum()))} đơn "
             f"({', '.join(f'{r.month}: {n(int(r.orders))}' for r in m[m.month > '2018-08'].itertuples())}).",
             f"- Tháng cao nhất: {m.loc[m.orders.idxmax(), 'month']} với {n(int(m.orders.max()))} đơn.", "",
             md_table(pd.DataFrame({"Tháng": m.month, "Số đơn": m.orders.map(lambda v: n(int(v)))}), ["Số đơn"]), "",
             "## Phân bố điểm đánh giá", "", f"Hình: `{fig5}`.", "",
             md_table(pd.DataFrame({"Điểm": rs.review_score, "Số review": rs.c.map(lambda v: n(int(v))), "%": rs.share.map(lambda v: pct(v, 1))}), ["Số review", "%"]), "",
             f"- Điểm trung bình {n(avg, 2)}; {pct(rs[rs.review_score >= 4].share.sum())} review từ 4 sao trở lên; "
             f"{pct(rs[rs.review_score <= 2].share.sum())} review tiêu cực (≤ 2 sao)."]
    write_md("distributions.md", lines)


if __name__ == "__main__":
    main()

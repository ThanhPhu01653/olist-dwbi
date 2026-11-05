"""P1 step 4: correlations -> handoff/correlations.md + figures.

Correlation matrix (Spearman), delay_days vs review_score (with mean score per delay group),
freight_value vs product_weight_g, lead time by region, late rate by state.
Population: delivered orders with a delivery date. delay_days = delivered date - estimated date (days, negative = early).
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

ORDERS_SQL = """
WITH it AS (SELECT i.order_id, count(*) AS items, sum(i.price) AS price_total, sum(i.freight_value) AS freight_total,
                   count(DISTINCT i.seller_id) AS sellers, sum(p.product_weight_g) AS weight_g
            FROM oltp.order_items i JOIN oltp.products p USING (product_id) GROUP BY 1),
     pa AS (SELECT order_id, sum(payment_value) AS payment_total, max(payment_installments) AS installments
            FROM oltp.order_payments GROUP BY 1),
     rv AS (SELECT order_id, avg(review_score) AS review_score FROM oltp.order_reviews GROUP BY 1)
SELECT o.order_id, c.customer_state AS state,
       it.items, it.price_total, it.freight_total, it.weight_g, pa.payment_total, pa.installments, rv.review_score,
       extract(epoch FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS lead_days,
       CASE WHEN o.order_approved_at >= o.order_purchase_timestamp
            THEN extract(epoch FROM (o.order_approved_at - o.order_purchase_timestamp)) / 3600.0 END AS approval_hours,
       CASE WHEN o.order_delivered_carrier_date >= o.order_approved_at
            THEN extract(epoch FROM (o.order_delivered_carrier_date - o.order_approved_at)) / 86400.0 END AS handling_days,
       CASE WHEN o.order_delivered_customer_date >= o.order_delivered_carrier_date
            THEN extract(epoch FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date)) / 86400.0 END AS transit_days,
       (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date) AS delay_days
FROM oltp.orders o JOIN oltp.customers c USING (customer_id)
LEFT JOIN it USING (order_id) LEFT JOIN pa USING (order_id) LEFT JOIN rv USING (order_id)
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
"""

LABELS = {
    "items": "Số dòng hàng", "price_total": "Tiền hàng (price)", "freight_total": "Phí vận chuyển", "weight_g": "Tổng cân nặng (g)",
    "payment_total": "Tổng thanh toán", "installments": "Số kỳ trả góp", "approval_hours": "Giờ chờ duyệt",
    "handling_days": "Ngày xử lý (duyệt → bàn giao)", "transit_days": "Ngày vận chuyển", "lead_days": "Lead time (mua → giao)",
    "delay_days": "Trễ so với dự kiến (ngày)", "review_score": "Điểm review",
}
GROUPS = ["Sớm (< 0 ngày)", "Đúng hạn (0 ngày)", "Trễ 1–3 ngày", "Trễ 4–7 ngày", "Trễ > 7 ngày"]


def delay_group(d: pd.Series) -> pd.Categorical:
    g = np.select([d < 0, d == 0, d <= 3, d <= 7], GROUPS[:4], default=GROUPS[4])
    return pd.Categorical(g, categories=GROUPS, ordered=True)


def corr_figure(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    cols = list(LABELS)
    corr = df[cols].astype(float).corr(method="spearman")
    labels = [LABELS[c] for c in cols]
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("div", [RED, "#f0efec", BLUE])  # diverging: red (-) <-> grey 0 <-> blue (+)
    fig, ax = plt.subplots(figsize=(10.5, 8.4))
    ax.grid(False)
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = corr.values[i, j]
            ax.text(j, i, n(v, 2), ha="center", va="center", fontsize=8, color="white" if abs(v) > 0.6 else INK)
    ax.set_xticks(range(len(cols)), labels, rotation=40, ha="right", fontsize=9, color=INK2)
    ax.set_yticks(range(len(cols)), labels, fontsize=9, color=INK2)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Ma trận tương quan Spearman giữa các biến số của đơn hàng đã giao", pad=12)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.outline.set_visible(False)
    cb.set_label("Hệ số tương quan Spearman")
    return save(fig, "3-3-1_correlation_matrix"), corr


def delay_review(df: pd.DataFrame) -> tuple[str, pd.DataFrame, float]:
    d = df.dropna(subset=["review_score", "delay_days"]).copy()
    d["group"] = delay_group(d.delay_days)
    grp = d.groupby("group", observed=True).agg(orders=("review_score", "size"), mean=("review_score", "mean"),
                                                 neg=("review_score", lambda s: 100 * (s <= 2).mean()),
                                                 five=("review_score", lambda s: 100 * (s >= 5).mean())).reset_index()
    rho = float(d.delay_days.corr(d.review_score, method="spearman"))
    samp = d.sample(min(25000, len(d)), random_state=42)
    rng = np.random.default_rng(42)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.25, 1]})
    x = samp.delay_days.clip(-40, 40)
    y = samp.review_score.round() + rng.uniform(-0.28, 0.28, len(samp))
    a1.scatter(x, y, s=5, color=BLUE, alpha=0.10, linewidths=0)
    bins = np.arange(-40, 41, 4)
    cut = pd.cut(d.delay_days.clip(-40, 40), bins, include_lowest=True)
    g = d.groupby(cut, observed=True).review_score
    m = g.mean()[g.size() >= 50]  # skip sparse bins at the extremes
    a1.plot([iv.mid for iv in m.index], m.values, color=ORANGE, lw=2.4, marker="o", ms=4)
    a1.annotate("điểm TB theo khoảng 4 ngày\n(chỉ khoảng có ≥ 50 đơn)",(m.index[-3].mid, m.values[-3]), xytext=(-70, 30), textcoords="offset points", color=ORANGE,
                fontsize=9, fontweight="bold", arrowprops=dict(arrowstyle="-", color=ORANGE))
    a1.set_xlabel("delay_days = ngày giao − ngày dự kiến (âm = giao sớm; cắt ở ±40 ngày)")
    a1.set_ylabel("Điểm review (có nhiễu nhẹ để thấy mật độ)")
    a1.set_yticks([1, 2, 3, 4, 5])
    a1.axvline(0, color=MUTED, lw=1, ls="--")
    a1.set_title(f"Trễ giao hàng và điểm review (Spearman ρ = {n(rho, 2)})")
    cols = [BLUE, BLUE, ORANGE, ORANGE, ORANGE]
    b = a2.bar([g.replace(" (", "\n(") for g in grp.group.astype(str)], grp["mean"], color=cols, width=0.65)
    direct_label_bars(a2, b, lambda v: n(v, 2))
    for rect, cnt in zip(b, grp.orders):
        a2.annotate(f"n = {n(int(cnt))}", (rect.get_x() + rect.get_width() / 2, 0.08), ha="center", fontsize=8, color="white")
    a2.set_ylim(0, 5)
    a2.set_ylabel("Điểm review trung bình")
    a2.grid(axis="x", visible=False)
    a2.tick_params(axis="x", labelsize=8.5)
    a2.set_title("Điểm trung bình theo nhóm trễ")
    return save(fig, "3-3-1_delay_vs_review"), grp, rho


def freight_weight() -> tuple[str, float, int]:
    d = q("""SELECT i.freight_value::float AS freight, p.product_weight_g::float AS weight, i.price::float AS price
             FROM oltp.order_items i JOIN oltp.products p USING (product_id)
             WHERE p.product_weight_g > 0 AND i.freight_value > 0""")
    rho = float(d.freight.corr(d.weight, method="spearman"))
    pear_log = float(np.log(d.freight).corr(np.log(d.weight)))
    s = d.sample(25000, random_state=1)
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    ax.scatter(s.weight, s.freight, s=5, color=BLUE, alpha=0.18, linewidths=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cân nặng sản phẩm (g, thang log)")
    ax.set_ylabel("Phí vận chuyển (BRL, thang log)")
    ax.set_title(f"Phí vận chuyển tăng theo cân nặng (Spearman ρ = {n(rho, 2)}; Pearson trên log = {n(pear_log, 2)})")
    return save(fig, "3-3-1_freight_vs_weight"), rho, len(d)


def region_lead(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    d = df.dropna(subset=["lead_days"]).copy()
    d["region"] = d.state.map(STATE_REGION)
    order = d.groupby("region").lead_days.median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    data = [d[d.region == r].lead_days for r in order]
    ax.boxplot(data, orientation="vertical", widths=0.55, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="#cde2fb", edgecolor=BLUE), medianprops=dict(color=ORANGE, lw=2),
               whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE))
    ax.set_xticks(range(1, len(order) + 1), [f"{r}\n(n = {n(len(x))})" for r, x in zip(order, data)])
    for i, x in enumerate(data, 1):
        ax.text(i + 0.33, x.median(), n(x.median(), 1), va="center", fontsize=9.5, color=ORANGE, fontweight="bold")
    ax.set_ylabel("Lead time mua → giao (ngày)")
    ax.grid(axis="x", visible=False)
    ax.set_title("Lead time theo vùng của khách (số trên hộp = trung vị; không vẽ ngoại lai)")
    stats = d.groupby("region").lead_days.agg(["size", "mean", "median", lambda s: s.quantile(0.95)]).loc[order]
    stats.columns = ["orders", "mean", "median", "p95"]
    return save(fig, "3-3-1_lead_time_by_region"), stats


def late_by_state(df: pd.DataFrame) -> tuple[str, pd.DataFrame, float]:
    d = df.dropna(subset=["delay_days"]).copy()
    d["late"] = d.delay_days > 0
    s = d.groupby("state").agg(orders=("late", "size"), late=("late", "mean")).reset_index()
    s["late"] *= 100
    s["region"] = s.state.map(STATE_REGION)
    overall = 100 * d.late.mean()
    s = s.sort_values("late")
    fig, ax = plt.subplots(figsize=(9, 8.2))
    colors = [ORANGE if v > overall else BLUE for v in s.late]
    b = ax.barh(s.state, s.late, color=colors, height=0.68)
    direct_label_bars(ax, b, lambda v: pct(v, 1), horizontal=True)
    ax.axvline(overall, color=MUTED, ls="--", lw=1.2)
    ax.annotate(f"Toàn quốc {pct(overall, 1)}", (overall, 0), xytext=(6, 4), textcoords="offset points", color=INK2, fontsize=9, fontweight="bold")
    ax.set_xlabel("Tỷ lệ đơn giao trễ so với ngày dự kiến (% số đơn đã giao)")
    vn_axis(ax, "x", 1)
    ax.grid(axis="y", visible=False)
    ax.set_title("Tỷ lệ giao trễ theo bang của khách (cam = cao hơn mức toàn quốc)")
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=ORANGE), plt.Rectangle((0, 0), 1, 1, color=BLUE)],
              labels=["Cao hơn toàn quốc", "Bằng hoặc thấp hơn"], loc="lower right")
    return save(fig, "3-3-1_late_rate_by_state"), s.sort_values("late", ascending=False), overall


def main() -> None:
    df = q(ORDERS_SQL)
    for c in df.columns.difference(["order_id", "state"]):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    f1, corr = corr_figure(df)
    f2, grp, rho = delay_review(df)
    f3, rho_fw, n_fw = freight_weight()
    f4, rstats = region_lead(df)
    f5, late, overall = late_by_state(df)

    pairs = corr.where(np.triu(np.ones(corr.shape), 1).astype(bool)).stack().rename("rho").reset_index()
    pairs.columns = ["a", "b", "rho"]
    top = pairs.reindex(pairs.rho.abs().sort_values(ascending=False).index).head(8)
    rv = corr["review_score"].drop("review_score").sort_values(key=abs, ascending=False)

    lines = ["# Tương quan và các mối quan hệ chính (olist_full)", "", source_note("correlations.py"), "",
             f"Tập dữ liệu: {n(len(df))} đơn đã giao (status = delivered, có ngày giao khách). Các khoảng thời gian âm (lỗi nguồn) được đặt NULL trước khi tính. "
             "Dùng hệ số **Spearman** (theo thứ hạng) vì hầu hết biến lệch phải mạnh.", "",
             "## Ma trận tương quan", "", f"Hình: `{f1}`.", "",
             md_table(pd.DataFrame({"Cặp biến": [f"{LABELS[a]} – {LABELS[b]}" for a, b in zip(top.a, top.b)], "Spearman ρ": top.rho.map(lambda v: n(v, 2))}), ["Spearman ρ"]), "",
             "Tương quan của điểm review với các biến khác (mạnh nhất trước): " + "; ".join(f"{LABELS[k]} {n(v, 2)}" for k, v in rv.head(4).items()) + ".", "",
             "## Trễ giao hàng và điểm review", "", f"Hình: `{f2}`.", "",
             md_table(pd.DataFrame({"Nhóm": grp.group.astype(str), "Số đơn có review": grp.orders.map(lambda v: n(int(v))),
                                    "Điểm TB": grp["mean"].map(lambda v: n(v, 2)), "% review tiêu cực (≤ 2)": grp.neg.map(lambda v: pct(v, 1)),
                                    "% review 5 sao": grp.five.map(lambda v: pct(v, 1))}),
                      ["Số đơn có review", "Điểm TB", "% review tiêu cực (≤ 2)", "% review 5 sao"]), "",
             f"- Spearman giữa delay_days và điểm review: ρ = {n(rho, 2)}.",
             f"- Đơn giao đúng/sớm có điểm TB {n((grp['mean'].iloc[:2] * grp.orders.iloc[:2]).sum() / grp.orders.iloc[:2].sum(), 2)}, còn đơn trễ > 7 ngày chỉ {n(grp['mean'].iloc[4], 2)} "
             f"(chênh {n(grp['mean'].iloc[0] - grp['mean'].iloc[4], 2)} điểm); tỷ lệ review tiêu cực tăng từ {pct(grp.neg.iloc[0], 1)} (giao sớm) lên {pct(grp.neg.iloc[4], 1)} (trễ > 7 ngày).", "",
             "## Phí vận chuyển và cân nặng", "", f"Hình: `{f3}`.", "",
             f"- {n(n_fw)} dòng hàng có cân nặng và phí > 0: Spearman ρ = {n(rho_fw, 2)}. Phí tăng theo cân nặng nhưng độ phân tán lớn "
             "(phí còn phụ thuộc quãng đường và kích thước), nên không thể thay thế bằng công thức theo cân nặng.", "",
             "## Lead time theo vùng", "", f"Hình: `{f4}`.", "",
             md_table(pd.DataFrame({"Vùng": rstats.index, "Số đơn đã giao": rstats.orders.map(lambda v: n(int(v))), "Trung bình (ngày)": rstats["mean"].map(lambda v: n(v, 1)),
                                    "Trung vị (ngày)": rstats["median"].map(lambda v: n(v, 1)), "P95 (ngày)": rstats.p95.map(lambda v: n(v, 1))}),
                      ["Số đơn đã giao", "Trung bình (ngày)", "Trung vị (ngày)", "P95 (ngày)"]), "",
             f"- Vùng nhanh nhất: {rstats.index[0]} (trung vị {n(rstats['median'].iloc[0], 1)} ngày); chậm nhất: {rstats.index[-1]} (trung vị {n(rstats['median'].iloc[-1], 1)} ngày).", "",
             "## Tỷ lệ giao trễ theo bang", "", f"Hình: `{f5}`.", "",
             f"- Tỷ lệ giao trễ toàn quốc: {pct(overall, 1)} số đơn đã giao.",
             "- Bang trễ nhiều nhất: " + ", ".join(f"{r.state} {pct(r.late, 1)} (n = {n(int(r.orders))})" for r in late.head(5).itertuples()) + ".",
             "- Bang trễ ít nhất: " + ", ".join(f"{r.state} {pct(r.late, 1)} (n = {n(int(r.orders))})" for r in late.tail(3).itertuples()) + ".",
             "- Lưu ý: các bang có rất ít đơn (n nhỏ) thì tỷ lệ kém ổn định.", "",
             md_table(pd.DataFrame({"Bang": late.state, "Vùng": late.region, "Số đơn đã giao": late.orders.map(lambda v: n(int(v))), "% trễ": late.late.map(lambda v: pct(v, 1))}),
                      ["Số đơn đã giao", "% trễ"])]
    write_md("correlations.md", lines)


if __name__ == "__main__":
    main()

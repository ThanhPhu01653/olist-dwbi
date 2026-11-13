"""P8-D1: outliers by two methods (IQR 1.5x and Isolation Forest) for price, freight_value, product_weight_g, lead time and delay.
-> handoff/2026-11-14-P8-eda.md (section outliers), figures/3-1_outliers_*.png, report/tables/p8_outliers.tex

IQR: x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR.  Isolation Forest: one-dimensional model per variable, contamination = 0.05, random_state = 42.
Lead time and delay use delivered orders with a delivery date (one value per order); price, freight and weight use order lines.
"""
from __future__ import annotations

from p8_common import *  # noqa: F401,F403

from sklearn.ensemble import IsolationForest

CONTAM, SEED = 0.05, 42
items = items_df()
deliv = orders_df()
deliv = deliv[deliv["lead_days"].notna()]

VARS = [
    ("price", "Giá (price, BRL)", items["price"], items, "price"),
    ("freight_value", "Phí vận chuyển (BRL)", items["freight_value"], items, "freight_value"),
    ("product_weight_g", "Cân nặng sản phẩm (g)", items["product_weight_g"], items, "product_weight_g"),
    ("lead_days", "Lead time (ngày)", deliv["lead_days"], deliv, "lead_days"),
    ("delay_days", "Số ngày trễ so với dự kiến", deliv["delay_days"].astype(float), deliv, "delay_days"),
]

rows, flags, examples = [], {}, []
for key, label, s, frame, col in VARS:
    v = s.dropna()
    q1, q3 = v.quantile(0.25), v.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    f_iqr = (v < lo) | (v > hi)
    model = IsolationForest(n_estimators=200, contamination=CONTAM, random_state=SEED)
    f_if = pd.Series(model.fit_predict(v.to_frame()) == -1, index=v.index)
    both = f_iqr & f_if
    flags[key] = (v, f_iqr, f_if, lo, hi)
    rows.append({"Biến": label, "n": len(v), "Q1": q1, "Q3": q3, "Ngưỡng dưới": lo, "Ngưỡng trên": hi, "IQR": int(f_iqr.sum()), "iForest": int(f_if.sum()),
                 "Giao nhau": int(both.sum()), "Chỉ IQR": int((f_iqr & ~f_if).sum()), "Chỉ iForest": int((f_if & ~f_iqr).sum()), "max": v.max(), "min": v.min()})
    top = frame.loc[v[both].sort_values(ascending=False).head(3).index]
    for _, r in top.iterrows():
        examples.append((label, r))

res = pd.DataFrame(rows)

# ---- evidence for "keep or drop": are the extremes explained by other variables, or are they data errors?
ev = []
fr_v, fr_iqr, *_ = flags["freight_value"]
heavy = items.loc[fr_v[fr_iqr].index, "product_weight_g"]
ev.append(f"{n(int(fr_iqr.sum()))} dòng có phí vận chuyển ngoại lai: cân nặng trung vị {n(heavy.median())} g, so với trung vị toàn bộ {n(items['product_weight_g'].median())} g; phần lớn là hàng nặng hoặc giao xa.")
pr_v, pr_iqr, *_ = flags["price"]
top_cat = items.loc[pr_v[pr_iqr].index, "product_category_name"].value_counts().head(3)
ev.append("Giá ngoại lai tập trung ở các danh mục " + ", ".join(f"{c} ({n(int(k))} dòng)" for c, k in top_cat.items()) + f"; giá lớn nhất {n(items['price'].max(), 2)} BRL, nhỏ nhất {n(items['price'].min(), 2)} BRL (không có giá bằng 0 hoặc âm).")
w0 = int((items["product_weight_g"] == 0).sum())
ev.append(f"Có {n(w0)} dòng hàng có cân nặng bằng 0 g (vô lý về vật lý, đây là lỗi dữ liệu nguồn chứ không phải ngoại lai thống kê); cân nặng lớn nhất {n(items['product_weight_g'].max())} g.")
ld_v, ld_iqr, *_ = flags["lead_days"]
ev.append(f"{n(int(ld_iqr.sum()))} đơn có lead time ngoại lai (trên {n(flags['lead_days'][4], 1)} ngày), lớn nhất {n(ld_v.max(), 0)} ngày; các đơn này phần lớn trễ so với ngày dự kiến ({pct(float((deliv.loc[ld_v[ld_iqr].index, 'delay_days'] > 0).mean() * 100))} đơn trễ), tức là chậm thật chứ không phải nhập sai.")
neg = int((deliv["lead_days"] < 0).sum())
ev.append(f"Không có lead time âm trong tập đơn đã giao ({n(neg)} đơn); ngày trễ âm lớn (giao sớm hơn dự kiến) chiếm phần lớn ngoại lai của biến trễ vì ngày dự kiến rất rộng rãi.")

# ---- figures
fig, axes = plt.subplots(1, 5, figsize=(14, 4.6))
for ax, (key, label, *_r) in zip(axes, VARS):
    v, f_iqr, f_if, lo, hi = flags[key]
    bp = ax.boxplot(v, widths=0.55, showfliers=True, patch_artist=True, flierprops=dict(marker=".", markersize=2, markerfacecolor=MUTED, markeredgecolor=MUTED, alpha=0.35),
                    boxprops=dict(facecolor="#cde2fb", edgecolor=BLUE), medianprops=dict(color=ORANGE, lw=1.6), whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE))
    if key in ("price", "freight_value", "product_weight_g"):
        ax.set_yscale("symlog", linthresh=10)
    ax.set_title(label, fontsize=9.5)
    ax.set_xticks([])
    ax.grid(axis="x", visible=False)
    ax.set_xlabel(f"IQR {n(int(f_iqr.sum()))}\niForest {n(int(f_if.sum()))}\ngiao nhau {n(int((f_iqr & f_if).sum()))}", fontsize=8.5, color=INK2)
fig.suptitle("Boxplot năm biến số (thang symlog cho tiền và cân nặng): chấm xám là ngoại lai theo IQR", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
f1 = save(fig, "3-1_outliers_boxplot")

# hexbin price vs freight with IQR fences
fig, ax = plt.subplots(figsize=(7.4, 5.6))
d = items[(items["price"] > 0) & (items["freight_value"] > 0)]
hb = ax.hexbin(np.log10(d["price"]), np.log10(d["freight_value"]), gridsize=55, bins="log", cmap="Blues", mincnt=1)
cb = fig.colorbar(hb, ax=ax, pad=0.01); cb.set_label("Số dòng hàng (thang log)")
ax.axvline(np.log10(flags["price"][4]), color=ORANGE, ls="--", lw=1.2)
ax.axhline(np.log10(flags["freight_value"][4]), color=ORANGE, ls="--", lw=1.2)
ax.set_xlabel("log10 giá (BRL)"); ax.set_ylabel("log10 phí vận chuyển (BRL)")
ax.set_title("Giá và phí vận chuyển (hexbin); đường cam là ngưỡng IQR", fontsize=11)
f2 = save(fig, "3-1_outliers_hexbin")

# histogram of lead time with fences
fig, ax = plt.subplots(figsize=(7.4, 4.6))
v, f_iqr, f_if, lo, hi = flags["lead_days"]
ax.hist(v.clip(upper=v.quantile(0.999)), bins=70, color=BLUE)
ax.axvline(hi, color=ORANGE, lw=1.6, ls="--")
ax.annotate(f"ngưỡng IQR {n(hi, 1)} ngày", (hi, ax.get_ylim()[1] * 0.9), xytext=(6, 0), textcoords="offset points", color=ORANGE, fontsize=9)
ax.set_xlabel("Lead time (ngày, cắt ở P99,9)"); ax.set_ylabel("Số đơn"); vn_axis(ax)
ax.set_title("Phân bố lead time và ngưỡng ngoại lai", fontsize=11)
f3 = save(fig, "3-1_outliers_hist_lead")

# ---- LaTeX table
def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


tex_rows = "\n".join(
    f"{esc(r['Biến'])} & {n(r['n'])} & {n(r['Ngưỡng dưới'], 1)} / {n(r['Ngưỡng trên'], 1)} & {n(r['IQR'])} & {n(r['iForest'])} & {n(r['Giao nhau'])}\\\\" for _, r in res.iterrows())
(ROOT / "report" / "tables" / "p8_outliers.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Số ngoại lai theo hai phương pháp (iForest: contamination 0,05, random\\_state 42)}\\label{tab:outliers}\n"
    "\\begin{tabular}{p{4.2cm}rrrrr}\\toprule\n\\textbf{Biến} & \\textbf{n} & \\textbf{Ngưỡng IQR dưới / trên} & \\textbf{IQR} & \\textbf{iForest} & \\textbf{Giao nhau}\\\\\\midrule\n"
    + tex_rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

# ---- handoff section
view = res.copy()
for c in ["n", "IQR", "iForest", "Giao nhau", "Chỉ IQR", "Chỉ iForest"]:
    view[c] = view[c].map(n)
for c in ["Q1", "Q3", "Ngưỡng dưới", "Ngưỡng trên", "min", "max"]:
    view[c] = view[c].map(lambda x: n(x, 2))
md = [f"Hai phương pháp: **IQR** (ngoại lai nếu ngoài [Q1 − 1,5·IQR, Q3 + 1,5·IQR]) và **Isolation Forest** (scikit-learn, `n_estimators = 200`, **`contamination = 0,05`**, **`random_state = 42`**; mô hình một chiều cho từng biến). Giá, phí vận chuyển và cân nặng tính trên {n(len(items))} dòng hàng; lead time và số ngày trễ tính trên {n(len(deliv))} đơn đã giao.", "",
      md_table(view[["Biến", "n", "Ngưỡng dưới", "Ngưỡng trên", "IQR", "iForest", "Giao nhau", "Chỉ IQR", "Chỉ iForest"]], ["n", "IQR", "iForest", "Giao nhau", "Chỉ IQR", "Chỉ iForest"]), "",
      f"Tổng ngoại lai theo từng biến (cộng các biến, có thể trùng dòng): IQR {n(int(res['IQR'].sum()))}, iForest {n(int(res['iForest'].sum()))}, giao nhau {n(int(res['Giao nhau'].sum()))}.", "",
      "### Ví dụ dòng ngoại lai (cả hai phương pháp cùng đánh dấu)", ""]
ex_rows = []
for label, r in examples:
    if label.startswith("Giá") or label.startswith("Phí") or label.startswith("Cân"):
        ex_rows.append({"Biến": label, "order_id": r["order_id"][:8] + "…", "price": n(r["price"], 2), "freight": n(r["freight_value"], 2), "weight_g": n(r["product_weight_g"]), "danh mục": r["product_category_name"], "bang khách": r["customer_state"]})
    else:
        ex_rows.append({"Biến": label, "order_id": r["order_id"][:8] + "…", "price": n(r["main_price"], 2), "freight": "–", "weight_g": "–", "danh mục": r["product_category_name"], "bang khách": r["customer_state"]})
md += [md_table(pd.DataFrame(ex_rows)), "", "### Giữ hay loại?", ""] + [f"- {e}" for e in ev] + [
    "",
    "**Kết luận:** giữ toàn bộ ngoại lai về giá, phí vận chuyển, lead time và số ngày trễ, vì đó là ngoại lai hợp lệ (hàng đắt, hàng nặng, giao xa, giao chậm thật) và chính là đối tượng phân tích (giao trễ, phí vận chuyển cao); loại chúng sẽ làm sai GMV và che mất vấn đề giao hàng. Riêng các dòng có cân nặng bằng 0 g là lỗi dữ liệu nguồn: không loại dòng hàng (vẫn có doanh thu), chỉ không dùng cân nặng của chúng khi phân tích phí theo cân nặng. Để giảm ảnh hưởng của ngoại lai lên thống kê mô tả, báo cáo dùng trung vị thay cho trung bình.", "",
    "### Hình", "",
    f"![Boxplot]({f1.replace('figures/', '../figures/')})", "",
    f"- Giá, phí vận chuyển và cân nặng có đuôi phải rất dài (hộp hẹp, nhiều chấm ngoại lai) nên phải vẽ bằng thang symlog; ở ba biến này IQR đánh dấu nhiều hơn iForest ({n(int(res.loc[0, 'IQR']))} so với {n(int(res.loc[0, 'iForest']))} ở giá; {n(int(res.loc[1, 'IQR']))} so với {n(int(res.loc[1, 'iForest']))} ở phí; {n(int(res.loc[2, 'IQR']))} so với {n(int(res.loc[2, 'iForest']))} ở cân nặng), còn ở lead time và số ngày trễ hai phương pháp gần nhau ({n(int(res.loc[3, 'IQR']))} so với {n(int(res.loc[3, 'iForest']))}; {n(int(res.loc[4, 'IQR']))} so với {n(int(res.loc[4, 'iForest']))}).", "",
    f"![Hexbin]({f2.replace('figures/', '../figures/')})", "",
    f"- Tương quan Spearman giữa giá và phí vận chuyển là {n(items['price'].corr(items['freight_value'], method='spearman'), 2)} (mức vừa); phần lớn dòng hàng nằm ở vùng giá và phí thấp. {n(int(((items['price'] > flags['price'][4]) & (items['freight_value'] > flags['freight_value'][4])).sum()))} dòng vượt cả hai ngưỡng IQR, bằng {pct(float(((items['price'] > flags['price'][4]) & (items['freight_value'] > flags['freight_value'][4])).sum() / (items['price'] > flags['price'][4]).sum() * 100))} số dòng có giá ngoại lai: ngoại lai về giá và về phí phần lớn là hai nhóm khác nhau.", "",
    f"![Lead time]({f3.replace('figures/', '../figures/')})", "",
    f"- Lead time có trung vị {n(ld_v.median(), 1)} ngày, P95 {n(ld_v.quantile(0.95), 1)} ngày và đuôi phải kéo dài đến {n(ld_v.max(), 0)} ngày; ngưỡng IQR là {n(hi, 1)} ngày, tức {pct(float(f_iqr.mean() * 100))} số đơn đã giao.", ""]
section("outliers", md)
print(res[["Biến", "IQR", "iForest", "Giao nhau"]].to_string(index=False))

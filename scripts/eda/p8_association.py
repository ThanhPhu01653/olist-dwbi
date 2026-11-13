"""P8-D2: association between discrete variables: Cramer's V (Bergsma bias correction) for categorical pairs and the correlation ratio eta
for categorical -> numeric pairs; compared with the Spearman coefficients of P1.
-> handoff/2026-11-14-P8-eda.md (section association), figures/3-1_cramer_v_heatmap.png, 3-1_eta_heatmap.png, report/tables/p8_association*.tex
"""
from __future__ import annotations

from p8_common import *  # noqa: F401,F403

from scipy.stats import chi2_contingency

df = orders_df()
df["review_group"] = df["review_group"].astype("object")
CAT = {
    "payment_type": "Hình thức thanh toán",
    "category_group": "Nhóm ngành hàng",
    "customer_region": "Vùng khách",
    "seller_region": "Vùng seller",
    "order_status": "Trạng thái đơn",
    "is_late": "Cờ giao trễ",
    "review_group": "Nhóm review",
}
df["is_late"] = df["is_late"].map({0.0: "đúng hạn/sớm", 1.0: "trễ"})


def cramers_v(a: pd.Series, b: pd.Series) -> tuple[float, int, float, tuple[int, int]]:
    """Bias-corrected Cramer's V (Bergsma 2013). Returns (V, n, raw V, table shape)."""
    t = pd.crosstab(a, b)
    r, k = t.shape
    n_ = int(t.values.sum())
    if r < 2 or k < 2 or n_ < 2:
        return np.nan, n_, np.nan, (r, k)
    chi2 = chi2_contingency(t, correction=False)[0]
    phi2 = chi2 / n_
    raw = np.sqrt(phi2 / min(r - 1, k - 1))
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n_ - 1))
    rc = r - (r - 1) ** 2 / (n_ - 1)
    kc = k - (k - 1) ** 2 / (n_ - 1)
    return float(np.sqrt(phi2c / min(kc - 1, rc - 1))), n_, float(raw), (r, k)


cols = list(CAT)
V = pd.DataFrame(np.nan, index=cols, columns=cols)
N = pd.DataFrame(0, index=cols, columns=cols)
pairs = []
for i, a in enumerate(cols):
    for j, b in enumerate(cols):
        if i == j:
            V.loc[a, b] = 1.0
            continue
        sub = df[[a, b]].dropna()
        v, n_, raw, shape = cramers_v(sub[a], sub[b])
        V.loc[a, b] = v
        N.loc[a, b] = n_
        if i < j:
            pairs.append({"a": a, "b": b, "V": v, "raw": raw, "n": n_, "shape": shape})
pairs_df = pd.DataFrame(pairs).sort_values("V", ascending=False)


def eta(cat: pd.Series, num: pd.Series) -> tuple[float, int]:
    d = pd.DataFrame({"c": cat, "x": num}).dropna()
    if d["c"].nunique() < 2 or len(d) < 3:
        return np.nan, len(d)
    grand = d["x"].mean()
    ssb = d.groupby("c")["x"].agg(lambda s: len(s) * (s.mean() - grand) ** 2).sum()
    sst = ((d["x"] - grand) ** 2).sum()
    return float(np.sqrt(ssb / sst)) if sst > 0 else np.nan, len(d)


NUM = {"delay_days": "Ngày trễ so với dự kiến", "lead_days": "Lead time (ngày)", "review_score": "Điểm review", "main_price": "Giá dòng hàng chính (BRL)"}
CATE = ["customer_region", "seller_region", "category_group", "payment_type", "is_late", "order_status"]
E = pd.DataFrame(np.nan, index=list(NUM), columns=CATE)
for nk in NUM:
    for ck in CATE:
        E.loc[nk, ck], _ = eta(df[ck], df[nk])

# Spearman for comparison (numeric pairs, delivered orders)
dl = df[df["lead_days"].notna()]
sp = {
    "delay_days ~ review_score": dl[["delay_days", "review_score"]].astype(float).corr(method="spearman").iloc[0, 1],
    "lead_days ~ review_score": dl[["lead_days", "review_score"]].astype(float).corr(method="spearman").iloc[0, 1],
}
eta_review_late = E.loc["review_score", "is_late"]
eta_delay_region = E.loc["delay_days", "customer_region"]
eta_review_cat = E.loc["review_score", "category_group"]
V_late_review = V.loc["is_late", "review_group"]
V_best = pairs_df.iloc[0]


_rv = df.dropna(subset=['review_score'])
neg_rate = (_rv['review_score'] <= 2.5).groupby(_rv['order_status']).mean()


def scale_v(x: float) -> str:
    return "không đáng kể" if x < 0.1 else "yếu" if x < 0.3 else "vừa" if x < 0.5 else "mạnh"


def heat(mat: pd.DataFrame, labels_r: dict, labels_c: dict, title: str, name: str, fmt_max=1.0, figsize=(8.2, 6.4)) -> str:
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(mat.values.astype(float), cmap="Blues", vmin=0, vmax=fmt_max)
    ax.set_xticks(range(mat.shape[1])); ax.set_xticklabels([labels_c[c] for c in mat.columns], rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(mat.shape[0])); ax.set_yticklabels([labels_r[r] for r in mat.index], fontsize=9)
    ax.grid(False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, n(v, 2), ha="center", va="center", fontsize=8.5, color="white" if v > 0.55 * fmt_max else INK)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    ax.set_title(title, fontsize=11)
    return save(fig, name)


f_v = heat(V.where(~np.eye(len(cols), dtype=bool), np.nan), CAT, CAT, "Cramér's V (hiệu chỉnh Bergsma) giữa các biến phân loại", "3-1_cramer_v_heatmap", fmt_max=max(0.5, float(np.nanmax(V.where(~np.eye(len(cols), dtype=bool)).values))))
f_e = heat(E, NUM, CAT, "Tỉ số tương quan η: biến phân loại (cột) giải thích biến số (hàng)", "3-1_eta_heatmap", fmt_max=max(0.5, float(np.nanmax(E.values))), figsize=(8.8, 4.2))

# ---- LaTeX tables
def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


top = pairs_df.head(8)
rows = "\n".join(f"{esc(CAT[r.a])} -- {esc(CAT[r.b])} & {n(r.V, 3)} & {n(r.raw, 3)} & {n(r.n)} & {scale_v(r.V)}\\\\" for r in top.itertuples())
(ROOT / "report" / "tables" / "p8_association_v.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Tám cặp biến phân loại có Cramér's V lớn nhất}\\label{tab:cramer-v}\n\\begin{tabular}{p{6.2cm}rrrl}\\toprule\n"
    "\\textbf{Cặp biến} & \\textbf{V hiệu chỉnh} & \\textbf{V gốc} & \\textbf{n} & \\textbf{Mức}\\\\\\midrule\n" + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")
erows = []
for nk, lab in NUM.items():
    for ck in CATE:
        pass
etop = sorted(((E.loc[nk, ck], nk, ck) for nk in NUM for ck in CATE if not np.isnan(E.loc[nk, ck]) and not (nk == 'delay_days' and ck == 'is_late')), reverse=True)[:8]
rows = "\n".join(f"{esc(NUM[nk])} theo {esc(CAT[ck])} & {n(e, 3)} & {n(e ** 2, 3)} & {scale_v(e)}\\\\" for e, nk, ck in etop)
(ROOT / "report" / "tables" / "p8_association_eta.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Tám cặp (biến phân loại, biến số) có tỉ số tương quan $\\eta$ lớn nhất}\\label{tab:eta}\n\\begin{tabular}{p{7.2cm}rrl}\\toprule\n"
    "\\textbf{Cặp biến} & $\\eta$ & $\\eta^2$ & \\textbf{Mức}\\\\\\midrule\n" + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

# ---- handoff section
vt = pairs_df.head(10).copy()
vt["Cặp biến"] = vt.apply(lambda r: f"{CAT[r.a]} – {CAT[r.b]}", axis=1)
vt_md = pd.DataFrame({"Cặp biến": vt["Cặp biến"], "V hiệu chỉnh": vt["V"].map(lambda x: n(x, 3)), "V gốc": vt["raw"].map(lambda x: n(x, 3)), "n": vt["n"].map(n), "Mức": vt["V"].map(scale_v)})
et_md = pd.DataFrame([{"Biến số": NUM[nk], "Biến phân loại": CAT[ck], "η": n(e, 3), "η²": n(e ** 2, 3), "Mức": scale_v(e)} for e, nk, ck in etop])
ewide = E.copy()
ewide.index = [NUM[i] for i in ewide.index]
ewide.columns = [CAT[c] for c in ewide.columns]
ewide = ewide.map(lambda x: n(x, 3)).reset_index().rename(columns={"index": "Biến số"})
md = [
    "### Công thức",
    "",
    "Với bảng chéo $r \\times k$ của hai biến phân loại, $n$ quan sát, thống kê $\\chi^2$ (không hiệu chỉnh liên tục), $\\varphi^2 = \\chi^2 / n$:",
    "",
    "$$V = \\sqrt{\\frac{\\varphi^2}{\\min(r-1,\\; k-1)}} \\qquad \\text{(Cramér)}$$",
    "",
    "Hiệu chỉnh Bergsma (bỏ độ chệch dương của $V$ khi bảng lớn hoặc $n$ nhỏ):",
    "",
    "$$\\tilde\\varphi^2 = \\max\\!\\Bigl(0,\\; \\varphi^2 - \\frac{(k-1)(r-1)}{n-1}\\Bigr),\\quad \\tilde r = r - \\frac{(r-1)^2}{n-1},\\quad \\tilde k = k - \\frac{(k-1)^2}{n-1},\\quad \\tilde V = \\sqrt{\\frac{\\tilde\\varphi^2}{\\min(\\tilde k-1,\\; \\tilde r-1)}}$$",
    "",
    "Tỉ số tương quan giữa biến phân loại $c$ (nhóm $g$ có $n_g$ quan sát, trung bình $\\bar x_g$) và biến số $x$ (trung bình chung $\\bar x$):",
    "",
    "$$\\eta = \\sqrt{\\frac{\\sum_g n_g(\\bar x_g - \\bar x)^2}{\\sum_i (x_i - \\bar x)^2}} \\in [0,1], \\qquad \\eta^2 = \\text{tỉ lệ phương sai của } x \\text{ do nhóm giải thích}$$",
    "",
    "**Thang đọc** (quy ước, giống thang của hệ số tương quan): < 0,1 không đáng kể; 0,1–0,3 yếu; 0,3–0,5 vừa; > 0,5 mạnh. Cả hai hệ số đều không có dấu (chỉ cho biết có liên hệ, không cho biết chiều).",
    "",
    "### Dùng hệ số nào khi nào",
    "",
    "| Cặp biến | Hệ số | Giả định / ghi chú |",
    "| --- | --- | --- |",
    "| số – số, quan hệ tuyến tính, ít ngoại lai | Pearson | nhạy với ngoại lai; dữ liệu này lệch phải mạnh nên ít dùng |",
    "| số – số (hoặc thứ bậc), quan hệ đơn điệu | Spearman | dựa trên hạng nên bền với ngoại lai; dùng trong ma trận tương quan của P1 |",
    "| phân loại – phân loại | Cramér's V (hiệu chỉnh Bergsma) | từ 0 đến 1, không có dấu; hiệu chỉnh để không phóng đại khi bảng chéo nhiều ô |",
    "| phân loại – số | tỉ số tương quan η | từ 0 đến 1; η² là tỉ lệ phương sai giải thích; không có dấu |",
    "",
    f"### Cramér's V giữa bảy biến phân loại (hình)", "",
    f"![Cramér's V]({f_v.replace('figures/', '../figures/')})", "",
    md_table(vt_md, ["V hiệu chỉnh", "V gốc", "n"]), "",
    f"- Cặp liên hệ mạnh nhất là **{CAT[V_best['a']]} – {CAT[V_best['b']]}** với V = {n(V_best['V'], 3)} (mức {scale_v(V_best['V'])}). " + ("Đơn trễ có xác suất bị review tiêu cực cao hơn rõ rệt, khớp với điểm review giảm từ 4,29 xuống 1,70 ở P1." if {V_best['a'], V_best['b']} == {"is_late", "review_group"} else ""),
    f"- Trạng thái đơn và nhóm review có V = {n(V.loc['order_status', 'review_group'], 3)} (mức {scale_v(V.loc['order_status', 'review_group'])}): tỷ lệ review tiêu cực là {pct(neg_rate['delivered'] * 100)} ở đơn đã giao so với {pct(neg_rate['canceled'] * 100)} ở đơn hủy và {pct(neg_rate['shipped'] * 100)} ở đơn đang vận chuyển.",
    f"- Vùng khách và vùng seller có V = {n(V.loc['customer_region', 'seller_region'], 3)} (mức {scale_v(V.loc['customer_region', 'seller_region'])}); hình thức thanh toán và trạng thái đơn có V = {n(V.loc['payment_type', 'order_status'], 3)} (mức {scale_v(V.loc['payment_type', 'order_status'])}). Hầu hết cặp còn lại có liên hệ yếu hoặc không đáng kể, nên các biến này gần như độc lập và có thể dùng làm chiều phân tích riêng rẽ.",
    "",
    "### Tỉ số tương quan η (hình)", "",
    f"![Tỉ số tương quan η]({f_e.replace('figures/', '../figures/')})", "",
    md_table(et_md, ["η", "η²"]), "",
    "Toàn bộ ma trận η (hàng: biến số, cột: biến phân loại):", "", md_table(ewide), "",
    f"- Điểm review theo cờ giao trễ: η = {n(eta_review_late, 3)} (η² = {n(eta_review_late ** 2, 3)}), tức khoảng {n(100 * eta_review_late ** 2, 1)}% phương sai điểm review gắn với việc đơn giao trễ hay không.",
    "- Cặp (ngày trễ, cờ giao trễ) bị bỏ khỏi bảng xếp hạng vì cờ trễ được định nghĩa từ chính ngày trễ (η = " + n(E.loc['delay_days', 'is_late'], 3) + " là hiển nhiên). Lead time theo cờ trễ (" + n(E.loc['lead_days', 'is_late'], 3) + ") cũng cao vì đơn trễ có lead time dài.",
    f"- Ngày trễ theo vùng khách: η = {n(eta_delay_region, 3)}; điểm review theo nhóm ngành: η = {n(eta_review_cat, 3)} (nhóm ngành giải thích điểm review ít hơn nhiều so với việc giao trễ).",
    "",
    "### Đối chiếu với Spearman đã có (P1)", "",
    f"- Spearman(ngày trễ, điểm review) = {n(sp['delay_days ~ review_score'], 3)} và Spearman(lead time, điểm review) = {n(sp['lead_days ~ review_score'], 3)} (đơn đã giao): cùng hướng kết luận với η và V ở trên, tức giao chậm làm điểm review giảm. Spearman chỉ −0,18 trong khi η theo cờ trễ là " + n(eta_review_late, 3) + ": ảnh hưởng của giao trễ lên review mang tính ngưỡng (đơn trễ mới tụt điểm mạnh) hơn là tuyến tính theo số ngày.",
    "- Spearman chỉ áp dụng cho hai biến số hoặc thứ bậc; V và η mở rộng việc đo liên hệ sang biến phân loại (vùng, ngành hàng, hình thức thanh toán, trạng thái) mà Spearman không đo được.", "",
]
section("association", md)
print(pairs_df.head(6).to_string(index=False))
print("eta review~late", eta_review_late, "eta delay~region", eta_delay_region)

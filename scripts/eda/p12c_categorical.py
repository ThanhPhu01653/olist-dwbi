"""P12c: how to read association between categorical variables, and a readable correlation matrix for the slides.

a. chi-square test of independence for the 21 pairs of 7 categorical variables (chi2, dof, p, share of expected cells < 5;
   Monte Carlo permutation p-value when more than 20% of expected cells are < 5)
b. Cramer's V heatmap with * where p < 0.05, and Theil's U (asymmetric) heatmap
c. Spearman matrix for slides (8 variables, lower triangle, definitional pairs marked)
d. Odds ratio late -> negative review: raw 2x2 and logistic regression controlled for customer region and category group
e. MCA on four variables (SVD of the indicator matrix, no extra package)
-> handoff/2026-11-25-P12c-tuong-quan.md, figures/3-1_*.png, report/tables/p12c_*.tex
Run: python scripts/eda/p12c_categorical.py   (database olist_full; fixed random seed, same numbers each run)
"""
from __future__ import annotations

from itertools import combinations

from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import chi2_contingency

from correlations import LABELS, ORDERS_SQL
from p8_common import *  # noqa: F401,F403

SEED = 20261125
MC_ROUNDS = 2000
rng = np.random.default_rng(SEED)

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
cols = list(CAT)
SHORT = {"payment_type": "Thanh toán", "category_group": "Ngành hàng", "customer_region": "Vùng khách", "seller_region": "Vùng seller",
         "order_status": "Trạng thái", "is_late": "Cờ trễ", "review_group": "Review"}


def pair_table(a: str, b: str) -> pd.DataFrame:
    sub = df[[a, b]].dropna()
    return pd.crosstab(sub[a], sub[b])


def chi2_row(t: pd.DataFrame) -> dict:
    r, k = t.shape
    n_ = int(t.values.sum())
    chi2, p, dof, exp = chi2_contingency(t, correction=False)
    low = float((exp < 5).mean())
    method = "chi2"
    if low > 0.20:
        # Monte Carlo: permute one variable, recompute chi2 on the same margins
        x = np.repeat(np.arange(r), t.sum(axis=1).values)
        y = np.concatenate([np.repeat(np.arange(k), t.values[i]) for i in range(r)])
        hits = 0
        for _ in range(MC_ROUNDS):
            yy = rng.permutation(y)
            tt = np.bincount(x * k + yy, minlength=r * k).reshape(r, k)
            e = np.outer(tt.sum(1), tt.sum(0)) / n_
            c = np.where(e > 0, (tt - e) ** 2 / np.where(e > 0, e, 1), 0).sum()
            hits += c >= chi2 - 1e-9
        p = (hits + 1) / (MC_ROUNDS + 1)
        method = f"Monte Carlo ({MC_ROUNDS})"
    phi2 = chi2 / n_
    raw = float(np.sqrt(phi2 / min(r - 1, k - 1)))
    phi2c = max(0.0, phi2 - (k - 1) * (r - 1) / (n_ - 1))
    rc = r - (r - 1) ** 2 / (n_ - 1)
    kc = k - (k - 1) ** 2 / (n_ - 1)
    v = float(np.sqrt(phi2c / min(kc - 1, rc - 1)))
    return {"n": n_, "r": r, "k": k, "chi2": float(chi2), "dof": int(dof), "p": float(p), "low": low, "method": method, "V": v, "raw": raw}


def entropy(counts: np.ndarray) -> float:
    p = counts[counts > 0] / counts.sum()
    return float(-(p * np.log(p)).sum())


def theil_u(t: pd.DataFrame) -> tuple[float, float]:
    """(U(row | col), U(col | row)) from a contingency table: share of the uncertainty of one variable removed by knowing the other."""
    v = t.values.astype(float)
    n_ = v.sum()
    hr, hc = entropy(v.sum(1)), entropy(v.sum(0))
    h_joint = entropy(v.ravel())
    h_r_given_c = h_joint - hc
    h_c_given_r = h_joint - hr
    return (hr - h_r_given_c) / hr if hr > 0 else np.nan, (hc - h_c_given_r) / hc if hc > 0 else np.nan


rows = []
U = pd.DataFrame(np.nan, index=cols, columns=cols)  # U.loc[x, y] = U(X | Y): row = variable to guess, column = variable known
V = pd.DataFrame(np.nan, index=cols, columns=cols)
P = pd.DataFrame(np.nan, index=cols, columns=cols)
for a, b in combinations(cols, 2):
    t = pair_table(a, b)
    row = chi2_row(t)
    u_ab, u_ba = theil_u(t)  # U(a|b), U(b|a)
    row.update({"a": a, "b": b, "U_a_given_b": u_ab, "U_b_given_a": u_ba})
    rows.append(row)
    U.loc[a, b], U.loc[b, a] = u_ab, u_ba
    V.loc[a, b] = V.loc[b, a] = row["V"]
    P.loc[a, b] = P.loc[b, a] = row["p"]
res = pd.DataFrame(rows).sort_values("V", ascending=False).reset_index(drop=True)
for c in cols:
    V.loc[c, c] = np.nan
    U.loc[c, c] = np.nan


# ---------------------------------------------------------------- heatmaps (same style as 3-1_cramer_v_heatmap)
def heat(mat: pd.DataFrame, title: str, name: str, vmax: float, stars: pd.DataFrame | None = None, xlabel: str | None = None,
         ylabel: str | None = None) -> str:
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    im = ax.imshow(mat.values.astype(float), cmap="Blues", vmin=0, vmax=vmax)
    ax.set_xticks(range(mat.shape[1]))
    ax.set_xticklabels([SHORT[c] for c in mat.columns], rotation=30, ha="right", fontsize=12)
    ax.set_yticks(range(mat.shape[0]))
    ax.set_yticklabels([SHORT[r] for r in mat.index], fontsize=12)
    ax.grid(False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat.values[i, j]
            if np.isnan(v):
                continue
            s = n(v, 2) + ("*" if stars is not None and stars.values[i, j] < 0.05 else "")
            ax.text(j, i, s, ha="center", va="center", fontsize=12, color="white" if v > 0.55 * vmax else INK)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    ax.set_title(title, fontsize=13)
    return save(fig, name)


vmax_v = max(0.5, float(np.nanmax(V.values)))
f_v = heat(V, "Cramér's V (hiệu chỉnh Bergsma); * là p < 0,05 (kiểm định χ²)", "3-1_cramer_v_heatmap_p", vmax_v, stars=P)
vmax_u = max(0.5, float(np.nanmax(U.values)))
f_u = heat(U, "Theil's U: biết cột thì giảm bấy nhiêu bất định của hàng", "3-1_theils_u_heatmap", vmax_u,
           xlabel="biến đã biết (cột)", ylabel="biến cần đoán (hàng)")
n_pairs = len(res)
n_sig = int((res["p"] < 0.05).sum())
n_mc = int((res["method"] != "chi2").sum())

# ---------------------------------------------------------------- spearman matrix for slides
od = q(ORDERS_SQL)
full_corr = od[list(LABELS)].astype(float).corr(method="spearman")
SL = ["price_total", "freight_total", "weight_g", "installments", "transit_days", "lead_days", "delay_days", "review_score"]
SLL = dict(LABELS)
SLL["price_total"] = "Tiền hàng"
SLL["lead_days"] = "Lead time"
SLL["transit_days"] = "Ngày vận chuyển"
SLL["delay_days"] = "Trễ so với dự kiến"
SLL["installments"] = "Số kỳ trả góp"
SLL["weight_g"] = "Cân nặng"
SLL["freight_total"] = "Phí vận chuyển"
sc = full_corr.loc[SL, SL]
DEFN = {frozenset(("transit_days", "lead_days"))}  # transit time is a component of lead time
cmap = LinearSegmentedColormap.from_list("div", [RED, "#f0efec", BLUE])
fig, ax = plt.subplots(figsize=(9.6, 6.0))
mask = np.tril(np.ones(sc.shape, dtype=bool), k=-1)
shown = np.where(mask, sc.values, np.nan)[1:, :-1]
im = ax.imshow(shown, cmap=cmap, vmin=-1, vmax=1)
ax.grid(False)
for i in range(1, len(SL)):
    for j in range(len(SL) - 1):
        if not mask[i, j]:
            continue
        v = sc.values[i, j]
        mark = "†" if frozenset((SL[i], SL[j])) in DEFN else ""
        ax.text(j, i - 1, n(v, 2) + mark, ha="center", va="center", fontsize=11, color="white" if abs(v) > 0.6 else INK)
ax.set_xticks(range(len(SL) - 1), [SLL[c] for c in SL[:-1]], rotation=40, ha="right", fontsize=11)
ax.set_yticks(range(len(SL) - 1), [SLL[c] for c in SL[1:]], fontsize=11)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("Spearman giữa các biến số của đơn đã giao", fontsize=12, pad=10)
fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
ax.set_xlabel("† tương quan do định nghĩa: ngày vận chuyển là một phần của lead time", fontsize=10.5, labelpad=40, loc="left")
f_s = save(fig, "3-1_spearman_slide")
sp_pt = float(full_corr.loc["price_total", "payment_total"])
sp_tl = float(full_corr.loc["transit_days", "lead_days"])
sp_fr_w = float(full_corr.loc["freight_total", "weight_g"])
sp_dl_rv = float(full_corr.loc["delay_days", "review_score"])
sp_ld_rv = float(full_corr.loc["lead_days", "review_score"])
sp_hl_ld = float(full_corr.loc["handling_days", "lead_days"])
sp_dl_ld = float(full_corr.loc["delay_days", "lead_days"])
defn_pairs = [(LABELS[a], LABELS[b], float(full_corr.loc[a, b])) for a, b in combinations(list(LABELS), 2) if abs(full_corr.loc[a, b]) >= 0.8]

# distance - freight Spearman (items with both coordinates) is produced by P8/P9 geo scripts; here only report what is in the matrix
skew = od[["price_total", "freight_total", "lead_days"]].skew()

# ---------------------------------------------------------------- odds ratio
d = df.dropna(subset=["is_late", "review_group"]).copy()
d["neg"] = (d["review_group"] == "tiêu cực (1-2)").astype(int)
d["late"] = (d["is_late"] == "trễ").astype(int)
a_ = int(((d.late == 1) & (d.neg == 1)).sum())
b_ = int(((d.late == 1) & (d.neg == 0)).sum())
c_ = int(((d.late == 0) & (d.neg == 1)).sum())
d_ = int(((d.late == 0) & (d.neg == 0)).sum())
or_raw = (a_ * d_) / (b_ * c_)
se = float(np.sqrt(1 / a_ + 1 / b_ + 1 / c_ + 1 / d_))
or_lo, or_hi = float(np.exp(np.log(or_raw) - 1.96 * se)), float(np.exp(np.log(or_raw) + 1.96 * se))
rate_late = a_ / (a_ + b_)
rate_ok = c_ / (c_ + d_)

import statsmodels.formula.api as smf  # noqa: E402

dd = d[d["category_group"].notna()].copy()
dd["category_group"] = dd["category_group"].astype(str)
m1 = smf.logit("neg ~ late", data=dd).fit(disp=0)
m2 = smf.logit("neg ~ late + C(customer_region) + C(category_group)", data=dd).fit(disp=0)
or1 = float(np.exp(m1.params["late"]))
or2 = float(np.exp(m2.params["late"]))
ci2 = np.exp(m2.conf_int().loc["late"].values)
n_logit = int(m2.nobs)

# ---------------------------------------------------------------- MCA on 4 variables (SVD of the indicator matrix)
mc = df[["is_late", "review_group", "customer_region", "order_status"]].copy()
mc["is_late"] = mc["is_late"].fillna("chưa giao")
mc["review_group"] = mc["review_group"].fillna("chưa có review")
mc["order_status"] = mc["order_status"].map(lambda s: "đã giao" if s == "delivered" else "hủy/không khả dụng" if s in ("canceled", "unavailable") else "đang xử lý/vận chuyển")
MC_LAB = {"is_late": "Giao", "review_group": "Review", "customer_region": "Vùng", "order_status": "Trạng thái"}
Z = pd.concat([pd.get_dummies(mc[c], prefix=MC_LAB[c], prefix_sep=": ") for c in mc.columns], axis=1).astype(float)
Zv = Z.values
Q = mc.shape[1]
J = Zv.shape[1]
Pm = Zv / Zv.sum()
rm, cm = Pm.sum(1), Pm.sum(0)
S = (Pm - np.outer(rm, cm)) / np.sqrt(np.outer(rm, cm))
_, sv, Vt = np.linalg.svd(S, full_matrices=False)
eig = sv ** 2
total_inertia = (J - Q) / Q
share = eig / total_inertia
keep = eig > 1 / Q  # Benzecri: only axes above 1/Q
bz = np.where(keep, (Q / (Q - 1)) ** 2 * (eig - 1 / Q) ** 2, 0.0)
bz_share = bz / bz.sum() if bz.sum() > 0 else bz
coords = (Vt.T * sv) / np.sqrt(cm)[:, None]  # principal coordinates of the categories
cats = list(Z.columns)
fig, ax = plt.subplots(figsize=(8.8, 6.6))
palette = {"Giao": ORANGE, "Review": BLUE, "Vùng": GREEN, "Trạng thái": MAGENTA}
cluster = [i for i in range(len(cats)) if coords[i, 0] < 0.6 and -0.7 < coords[i, 1] < 0.5]
cluster.sort(key=lambda i: coords[i, 1])
slot = {i: (1.9, -1.0 + 0.17 * k) for k, i in enumerate(cluster)}
nright = 0
for i, c in enumerate(cats):
    grp = c.split(":")[0]
    ax.scatter(coords[i, 0], coords[i, 1], s=70, color=palette[grp], zorder=3)
    if i in slot:
        ax.annotate(c, (coords[i, 0], coords[i, 1]), xytext=slot[i], textcoords="data", fontsize=10, color=INK, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    elif coords[i, 0] > 4:
        ax.annotate(c, (coords[i, 0], coords[i, 1]), xytext=(-7, [6, -14, 18][nright % 3]), textcoords="offset points", fontsize=10, color=INK, ha="right")
        nright += 1
    else:
        ax.annotate(c, (coords[i, 0], coords[i, 1]), xytext=(7, 6), textcoords="offset points", fontsize=10, color=INK)
ax.axhline(0, color=MUTED, lw=0.8)
ax.axvline(0, color=MUTED, lw=0.8)
ax.set_xlabel(f"Trục 1 ({n(100 * share[0], 1)}% quán tính)", fontsize=11)
ax.set_ylabel(f"Trục 2 ({n(100 * share[1], 1)}% quán tính)", fontsize=11)
ax.set_title(f"MCA bốn biến: hai trục giải thích {n(100 * (share[0] + share[1]), 1)}% quán tính", fontsize=12)
ax.set_xlim(-1.0, 6.2)
ax.text(5.9, -0.2, "đơn chưa giao,\nhủy, đang xử lý", ha="right", fontsize=9.5, color=INK2)
f_m = save(fig, "3-1_mca")
mca_top = pd.DataFrame({"cat": cats, "ax1": coords[:, 0], "ax2": coords[:, 1], "n": Zv.sum(0)})


# ---------------------------------------------------------------- tables for the report
def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")


def pfmt(p):
    return "< 0,001" if p < 0.001 else n(p, 3)


top5 = res.head(5)
tex = ["\\begin{table}[htbp]\\centering\\scriptsize\\caption{Kiểm định $\\chi^2$, Cramér's V và Theil's U của năm cặp biến phân loại mạnh nhất}\\label{tab:p12c-chi2}",
       "\\begin{tabular}{p{4.6cm}rrrrrr}\\toprule",
       "\\textbf{Cặp biến} & $\\chi^2$ & \\textbf{bậc tự do} & \\textbf{p} & \\textbf{V} & \\textbf{U (hàng | cột)} & \\textbf{U (cột | hàng)}\\\\\\midrule"]
for r in top5.itertuples():
    tex.append(f"{esc(CAT[r.a])} -- {esc(CAT[r.b])} & {n(r.chi2)} & {r.dof} & {pfmt(r.p)} & {n(r.V, 3)} & {n(r.U_a_given_b, 3)} & {n(r.U_b_given_a, 3)}\\\\")
tex += ["\\bottomrule\\end{tabular}\\end{table}", ""]
(ROOT / "report" / "tables" / "p12c_chi2.tex").write_text("\n".join(tex), encoding="utf-8")
(ROOT / "report" / "tables" / "p12c_or.tex").write_text("\n".join([
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Odds ratio của review tiêu cực (1--2 sao) theo cờ giao trễ}\\label{tab:p12c-or}",
    "\\begin{tabular}{p{6.2cm}rr}\\toprule",
    "\\textbf{Mô hình} & \\textbf{OR} & \\textbf{Khoảng tin cậy 95\\%}\\\\\\midrule",
    f"Bảng 2$\\times$2 (thô, n = {n(a_ + b_ + c_ + d_)}) & {n(or_raw, 1)} & {n(or_lo, 1)} -- {n(or_hi, 1)}\\\\",
    f"Logistic chỉ có cờ trễ & {n(or1, 1)} & --\\\\",
    f"Logistic kiểm soát vùng khách và nhóm ngành (n = {n(n_logit)}) & {n(or2, 1)} & {n(ci2[0], 1)} -- {n(ci2[1], 1)}\\\\",
    "\\bottomrule\\end{tabular}\\end{table}", ""]), encoding="utf-8")

# ---------------------------------------------------------------- handoff
best = res.iloc[0]
v_lr = float(V.loc["is_late", "review_group"])
u_r_l = float(U.loc["review_group", "is_late"])  # guess review group knowing late
u_l_r = float(U.loc["is_late", "review_group"])  # guess late knowing review group
p_lr = float(P.loc["is_late", "review_group"])
eta_rl = None
dl = df.dropna(subset=["review_score", "is_late"])
grand = dl["review_score"].mean()
ssb = dl.groupby("is_late")["review_score"].agg(lambda s: len(s) * (s.mean() - grand) ** 2).sum()
eta_rl = float(np.sqrt(ssb / ((dl["review_score"] - grand) ** 2).sum()))
t_main = res.head(8).copy()
t_md = pd.DataFrame({
    "Cặp biến": [f"{CAT[r.a]} – {CAT[r.b]}" for r in t_main.itertuples()],
    "n": t_main["n"].map(n), "χ²": t_main["chi2"].map(lambda x: n(x)), "bậc tự do": t_main["dof"],
    "p": t_main["p"].map(pfmt), "ô kỳ vọng < 5": t_main["low"].map(lambda x: pct(100 * x, 0)),
    "V": t_main["V"].map(lambda x: n(x, 3)),
    "U (hàng | cột)": t_main["U_a_given_b"].map(lambda x: n(x, 3)), "U (cột | hàng)": t_main["U_b_given_a"].map(lambda x: n(x, 3)),
})
t_all = pd.DataFrame({
    "Cặp biến (a – b)": [f"{CAT[r.a]} – {CAT[r.b]}" for r in res.itertuples()],
    "n": res["n"].map(n), "χ²": res["chi2"].map(n), "bậc tự do": res["dof"], "p": res["p"].map(pfmt),
    "ô < 5": res["low"].map(lambda x: pct(100 * x, 0)), "cách tính p": res["method"],
    "V": res["V"].map(lambda x: n(x, 3)), "U(a|b)": res["U_a_given_b"].map(lambda x: n(x, 3)), "U(b|a)": res["U_b_given_a"].map(lambda x: n(x, 3)),
})
md = [
    "# P12c – Tương quan: chọn phương pháp, kiểm định χ², Theil's U, odds ratio, MCA – 2026-11-25", "",
    "## Đã làm", "",
    "- Script `scripts/eda/p12c_categorical.py` (database `olist_full`, hạt giống ngẫu nhiên cố định nên số giống nhau mỗi lần chạy). Chạy: `python scripts/eda/p12c_categorical.py` (PowerShell và bash giống nhau).",
    "- Dùng cùng dữ liệu và cùng bảy biến phân loại của P8 (hình thức thanh toán, nhóm ngành, vùng khách, vùng seller, trạng thái đơn, cờ giao trễ, nhóm review), 21 cặp.",
    f"- **Kiểm định χ²:** {n_sig}/{n_pairs} cặp có p < 0,05. Với n khoảng 100.000, p gần như luôn nhỏ nên p không phân biệt được cặp mạnh với cặp yếu; phải đọc độ mạnh (V) chứ không đọc p.",
    f"- **Ô kỳ vọng < 5:** {n_mc} cặp có hơn 20% ô kỳ vọng nhỏ hơn 5, p của các cặp này tính bằng Monte Carlo ({MC_ROUNDS} lần hoán vị, p nhỏ nhất có thể là 1/{MC_ROUNDS + 1} ≈ 0,0005); cột \"cách tính p\" ghi rõ.",
    "- **Theil's U:** U(X | Y) = (H(X) − H(X | Y)) / H(X), entropy tự nhiên; hàng là biến cần đoán, cột là biến đã biết (không đối xứng).",
    "", "## Số liệu", "",
    "### Năm cặp mạnh nhất (xếp theo V hiệu chỉnh) và ba cặp tiếp theo", "", md_table(t_md, ["n", "χ²", "bậc tự do", "p", "V", "U (hàng | cột)", "U (cột | hàng)"]), "",
    "`U (hàng | cột)`: biến đầu của cặp là biến cần đoán, biến sau là biến đã biết; cột còn lại là chiều ngược.", "",
    "### Cặp cờ giao trễ – nhóm review (cặp trung tâm)", "",
    f"- χ² p {pfmt(p_lr)}; V = {n(v_lr, 3)}; η (điểm review theo cờ trễ) = {n(eta_rl, 3)}.",
    f"- Biết đơn trễ thì độ bất định về nhóm review giảm **{n(100 * u_r_l, 1)}%** (U(review | trễ) = {n(u_r_l, 3)}); biết nhóm review thì độ bất định về cờ trễ giảm **{n(100 * u_l_r, 1)}%** (U(trễ | review) = {n(u_l_r, 3)}).", "",
    "### Toàn bộ 21 cặp", "", md_table(t_all, ["n", "χ²", "bậc tự do", "p", "V", "U(a|b)", "U(b|a)"]), "",
    "### Odds ratio: giao trễ → review tiêu cực (1–2 sao)", "",
    f"| | Review tiêu cực | Không tiêu cực | Tỷ lệ tiêu cực |", "| --- | ---: | ---: | ---: |",
    f"| Đơn trễ | {n(a_)} | {n(b_)} | {pct(100 * rate_late)} |", f"| Đơn đúng hạn hoặc sớm | {n(c_)} | {n(d_)} | {pct(100 * rate_ok)} |", "",
    f"- OR thô = {n(or_raw, 2)} (khoảng tin cậy 95%: {n(or_lo, 2)} – {n(or_hi, 2)}), tính trên {n(a_ + b_ + c_ + d_)} đơn đã giao có review.",
    f"- Hồi quy logistic chỉ có cờ trễ: OR = {n(or1, 2)} (trùng OR thô, đúng như dự kiến).",
    f"- Hồi quy logistic kiểm soát vùng khách và nhóm ngành ({n(n_logit)} đơn): **OR = {n(or2, 2)}** (khoảng tin cậy 95%: {n(ci2[0], 2)} – {n(ci2[1], 2)}).",
    f"- Chênh lệch OR thô và OR có kiểm soát: {n(or_raw, 2)} → {n(or2, 2)} ({n(100 * (or2 / or_raw - 1), 1)}%). " + ("Nhỏ: vùng khách và nhóm ngành hầu như không làm đổi tác động của giao trễ." if abs(or2 / or_raw - 1) < 0.15 else "Đáng kể: vùng khách và nhóm ngành giải thích một phần ảnh hưởng của cờ trễ."),
    "- Câu cho slide: đơn trễ có odds review tiêu cực gấp khoảng " + n(or2, 0) + " lần (đã kiểm soát vùng khách và nhóm ngành).", "",
    "### Ma trận Spearman cho slide", "",
    f"- Hai cặp do định nghĩa trong ma trận 12 biến cũ: tiền hàng – tổng thanh toán = {n(sp_pt, 2)} (thanh toán = tiền hàng + phí vận chuyển) và ngày vận chuyển – lead time = {n(sp_tl, 2)} (ngày vận chuyển là một phần của lead time). Mọi cặp có |ρ| ≥ 0,8: " + "; ".join(f"{a} – {b} = {n(v, 2)}" for a, b, v in defn_pairs) + ".",
    f"- Hình slide giữ 8 biến (tiền hàng, phí vận chuyển, cân nặng, số kỳ trả góp, ngày vận chuyển, lead time, trễ so với dự kiến, điểm review); bỏ tổng thanh toán (trùng định nghĩa với tiền hàng), giờ chờ duyệt, ngày xử lý, số dòng hàng; chỉ nửa dưới tam giác; ô ngày vận chuyển – lead time đánh dấu † \"tương quan do định nghĩa\".",
    f"- Phí vận chuyển – cân nặng ρ = {n(sp_fr_w, 2)}; trễ – điểm review ρ = {n(sp_dl_rv, 2)}; lead time – điểm review ρ = {n(sp_ld_rv, 2)}.",
    f"- Độ lệch (skewness) của các biến số: tiền hàng {n(skew['price_total'], 2)}, phí vận chuyển {n(skew['freight_total'], 2)}, lead time {n(skew['lead_days'], 2)} (lệch phải; cơ sở để dùng Spearman thay Pearson).", "",
    "### MCA (bốn biến: giao, review, vùng khách, trạng thái đơn)", "",
    "- Cách làm: phân tích tương ứng (SVD) trên ma trận chỉ báo của bốn biến (không có gói `prince`), toàn bộ 99.441 đơn. Giá trị thiếu giữ thành nhóm riêng: giao = \"chưa giao\", review = \"chưa có review\"; trạng thái đơn gộp thành ba nhóm (đã giao; hủy hoặc không khả dụng; đang xử lý hoặc vận chuyển).",
    f"- Tổng quán tính (J − Q)/Q = {n(total_inertia, 3)} với J = {J} nhóm, Q = {Q} biến. Trục 1 giải thích **{n(100 * share[0], 1)}%**, trục 2 **{n(100 * share[1], 1)}%**, cả hai **{n(100 * (share[0] + share[1]), 1)}%** quán tính.",
    f"- Hiệu chỉnh Benzécri (chỉ tính trục có trị riêng > 1/Q): trục 1 {n(100 * bz_share[0], 1)}%, trục 2 {n(100 * bz_share[1], 1)}% (trong các trục được giữ).",
    "- Quán tính thô của MCA thấp là bình thường vì ma trận chỉ báo có nhiều chiều; vì vậy chỉ đọc vị trí tương đối các nhóm, không kết luận hơn.",
    "", md_table(mca_top.assign(ax1=mca_top.ax1.map(lambda x: n(x, 2)), ax2=mca_top.ax2.map(lambda x: n(x, 2)), n=mca_top.n.map(lambda x: n(int(x)))).rename(columns={"cat": "Nhóm", "ax1": "Trục 1", "ax2": "Trục 2", "n": "Số đơn"}), ["Trục 1", "Trục 2", "Số đơn"]), "",
    "## Slide và báo cáo", "",
    "- `slides/sections/02a-kham-pha.tex`, khối Tương quan, bộ chính (+1 frame, không thêm frame khác): **mới** \"Tương quan: chọn phương pháp theo loại biến\" (bảng 3 dòng, `\\note` có 5 câu trả lời); **sửa** \"Tương quan dim–dim: Cramér's V 0,40, Theil's U có chiều\" (hai lớp bấm: V có dấu *, Theil's U); **sửa** \"Tương quan dim–fact: giao trễ và điểm review\" (odds ratio 16 lần ở `\KetLuan`, số cũ chuyển vào `\\note`).",
    "- `slides/sections/99-du-phong.tex` (+3 frame): ma trận Spearman đã đánh dấu tương quan do định nghĩa; bảng χ², V, U bảy cặp mạnh nhất; bản đồ MCA.",
    "- `report/chapters/3-1-kham-pha.tex`: thay ma trận Spearman cũ bằng bản tám biến đã đánh dấu †; thêm đoạn kiểm định χ², Theil's U, odds ratio, MCA và hai bảng `p12c_chi2.tex`, `p12c_or.tex`, hình Theil's U.",
    "- Số trong bảng \"chọn phương pháp\": Spearman khoảng cách – phí 0,63 lấy từ `handoff/geo-distance.md`; η review theo cờ trễ 0,392 và V cờ trễ – review 0,403 khớp P8; skewness 3,8 đến 12,3 là số mới tính trên đơn đã giao (giá 9,89, phí 12,28, lead time 3,83), khác \"4–7\" ghi trong đề bài và khác số mẫu 5.000 đơn ở slide Thống kê đặc trưng.",
    "",
    "## Câu trả lời trong `\\note` của slide \"chọn phương pháp\" (để gửi người trình bày)", "",
    "1. **Vì sao không dùng Pearson?** Giá, phí và lead time lệch phải mạnh, nhiều ngoại lai hợp lệ; Pearson chỉ đo quan hệ tuyến tính và bị vài đơn lớn kéo đi, Spearman dựa trên hạng nên bền hơn.",
    f"2. **Vì sao không đọc p-value?** Với khoảng 100.000 đơn, {n_sig}/21 cặp có p < 0,05, kể cả cặp có V chỉ 0,01; p chỉ nói có liên hệ hay không, không nói mạnh hay yếu, nên đọc V (chỉ 3 cặp có V từ 0,1).",
    f"3. **V khác U thế nào?** V đối xứng, một con số độ mạnh; U có chiều: biết nhóm review giảm {n(100 * u_l_r, 1)}% bất định về cờ trễ, biết cờ trễ giảm {n(100 * u_r_l, 1)}% bất định về nhóm review.",
    "4. **Tương quan có phải nhân quả không?** Không: đơn trễ đi kèm review xấu (odds gấp khoảng 16 lần, đã kiểm soát vùng và ngành) nhưng nhóm không kết luận trễ gây ra điểm thấp.",
    "5. **Vì sao bỏ cặp tiền hàng – thanh toán?** Tổng thanh toán = tiền hàng + phí vận chuyển nên ρ = 0,99 do định nghĩa; tương tự ngày vận chuyển – lead time (0,89, đánh dấu †).",
    "",
    "## Hình / file xuất", "",
    "- `figures/3-1_cramer_v_heatmap_p.png` – Cramér's V kèm dấu * cho p < 0,05.",
    "- `figures/3-1_theils_u_heatmap.png` – Theil's U không đối xứng (hàng = biến cần đoán, cột = biến đã biết).",
    "- `figures/3-1_spearman_slide.png` – Spearman 8 biến, nửa dưới tam giác, † cặp do định nghĩa.",
    "- `figures/3-1_mca.png` – bản đồ MCA hai trục.",
    "- `report/tables/p12c_chi2.tex`, `report/tables/p12c_or.tex` – bảng cho báo cáo.", "",
]
out = HANDOFF_DIR / "2026-11-25-P12c-tuong-quan.md"
out.write_text("\n".join(md), encoding="utf-8")
print("written", out)
print(res[["a", "b", "chi2", "dof", "p", "low", "method", "V", "U_a_given_b", "U_b_given_a"]].head(8).to_string())
print("OR raw", or_raw, or_lo, or_hi, "logit", or1, or2, ci2, "rates", rate_late, rate_ok)
print("late-review U", u_r_l, u_l_r, "V", v_lr, "eta", eta_rl)
print("sig", n_sig, "mc", n_mc, "MCA share", share[:3], "benz", bz_share[:3], "J", J)
print("defn", defn_pairs, "sp", sp_pt, sp_tl, sp_fr_w, sp_dl_rv, sp_ld_rv, sp_dl_ld)
print("skew", skew.to_dict())

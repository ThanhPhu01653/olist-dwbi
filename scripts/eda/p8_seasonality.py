"""P8-D3: trend and seasonality. Weekly and monthly orders and GMV, STL decomposition (statsmodels) on 2017-01 .. 2018-08,
trend/seasonal strength 1 - Var(R)/Var(S+R), day-of-week x hour heatmap, Black Friday 2017.
-> handoff/2026-11-14-P8-eda.md (section seasonality), figures/3-1_*.png, report/tables/p8_stl.tex
Limit stated in the output: less than two years of usable data, so yearly seasonality (period 12 months) is weakly identified.
"""
from __future__ import annotations

from p8_common import *  # noqa: F401,F403

from statsmodels.tsa.seasonal import STL

W0, W1 = "2017-01-01", "2018-08-31"
ord_day = q("""SELECT o.order_purchase_timestamp::date AS d, count(DISTINCT o.order_id) AS orders,
                      coalesce(sum(i.price) FILTER (WHERE o.order_status NOT IN ('canceled','unavailable')), 0) AS gmv
               FROM oltp.orders o LEFT JOIN oltp.order_items i USING (order_id) GROUP BY 1 ORDER BY 1""")
ord_day["d"] = pd.to_datetime(ord_day["d"])
day = ord_day.set_index("d").asfreq("D", fill_value=0)
win = day.loc[W0:W1]
weekly = win.resample("W-SUN").sum()
monthly = win.resample("MS").sum()
# drop partial first/last weeks for the weekly chart
weekly = weekly.iloc[1:-1]


def strengths(res) -> tuple[float, float]:
    r, s, t = res.resid, res.seasonal, res.trend
    ft = max(0.0, 1 - np.var(r) / np.var(t + r))
    fs = max(0.0, 1 - np.var(r) / np.var(s + r))
    return float(ft), float(fs)


results = {}
# daily STL, weekly cycle (period 7), robust to the Black Friday spike
for key, col in [("orders_daily", "orders"), ("gmv_daily", "gmv")]:
    res = STL(win[col].astype(float), period=7, robust=True).fit()
    results[key] = (res, *strengths(res))
# monthly STL, yearly cycle (period 12) on only 20 months: reported with a warning
for key, col in [("orders_monthly", "orders"), ("gmv_monthly", "gmv")]:
    res = STL(monthly[col].astype(float), period=12, robust=True).fit()
    results[key] = (res, *strengths(res))

# ---- figure 1: weekly + monthly series
fig, axes = plt.subplots(2, 2, figsize=(12, 6.8))
for ax, (ser, lab, color) in zip(axes[0], [(weekly["orders"], "Số đơn mỗi tuần", BLUE), (weekly["gmv"] / 1e3, "GMV mỗi tuần (nghìn BRL)", ORANGE)]):
    ax.plot(ser.index, ser.values, color=color, lw=1.8)
    ax.set_title(lab); vn_axis(ax)
    pk = ser.idxmax()
    ax.annotate(f"đỉnh tuần {pk:%d/%m/%Y}: {n(ser.max())}", (pk, ser.max()), xytext=(-110, -6), textcoords="offset points", fontsize=8.5, color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
for ax, (ser, lab, color) in zip(axes[1], [(monthly["orders"], "Số đơn mỗi tháng", BLUE), (monthly["gmv"] / 1e3, "GMV mỗi tháng (nghìn BRL)", ORANGE)]):
    ax.bar(ser.index, ser.values, width=22, color=color)
    ax.set_title(lab); vn_axis(ax)
for ax in axes.ravel():
    ax.tick_params(axis="x", labelrotation=30, labelsize=8.5)
fig.suptitle("Số đơn và GMV theo tuần và theo tháng, giai đoạn 2017-01 → 2018-08", x=0.01, ha="left", fontsize=12.5, fontweight="bold")
fig.tight_layout()
f_series = save(fig, "3-1_seasonality_series")

# ---- figure 2: STL daily (orders)
res = results["orders_daily"][0]
fig, axs = plt.subplots(4, 1, figsize=(11, 8.2), sharex=True)
for ax, (ser, lab, col) in zip(axs, [(win["orders"], "Quan sát (số đơn mỗi ngày)", BLUE), (res.trend, "Xu hướng (trend)", ORANGE), (res.seasonal, "Mùa vụ theo tuần (chu kỳ 7 ngày)", AQUA), (res.resid, "Phần dư (residual)", MUTED)]):
    ax.plot(ser.index, ser.values, color=col, lw=1.2)
    ax.set_title(lab, fontsize=10); vn_axis(ax)
fig.suptitle(f"Phân rã STL số đơn theo ngày (chu kỳ 7, robust): độ mạnh xu hướng {n(results['orders_daily'][1], 2)}, mùa vụ tuần {n(results['orders_daily'][2], 2)}", x=0.01, ha="left", fontsize=12, fontweight="bold")
fig.tight_layout()
f_stl = save(fig, "3-1_stl_daily")

# ---- figure 3: STL monthly
res_m = results["orders_monthly"][0]
fig, axs = plt.subplots(4, 1, figsize=(9, 7.2), sharex=True)
for ax, (ser, lab, col) in zip(axs, [(monthly["orders"], "Quan sát (số đơn mỗi tháng)", BLUE), (res_m.trend, "Xu hướng", ORANGE), (res_m.seasonal, "Mùa vụ theo năm (chu kỳ 12 tháng)", AQUA), (res_m.resid, "Phần dư", MUTED)]):
    ax.plot(ser.index, ser.values, color=col, lw=1.6, marker="o", ms=3)
    ax.set_title(lab, fontsize=10); vn_axis(ax)
fig.suptitle(f"STL theo tháng (chu kỳ 12, chỉ {len(monthly)} tháng): độ mạnh xu hướng {n(results['orders_monthly'][1], 2)}, mùa vụ năm {n(results['orders_monthly'][2], 2)}", x=0.01, ha="left", fontsize=11.5, fontweight="bold")
fig.tight_layout()
f_stlm = save(fig, "3-1_stl_monthly")

# ---- figure 4: heatmap day of week x hour
hh = q("""SELECT extract(isodow FROM order_purchase_timestamp)::int AS dow, extract(hour FROM order_purchase_timestamp)::int AS h, count(*) AS n
          FROM oltp.orders WHERE order_purchase_timestamp >= :a AND order_purchase_timestamp < :b GROUP BY 1,2""", a=W0, b="2018-09-01")
piv = hh.pivot(index="dow", columns="h", values="n").reindex(index=range(1, 8), columns=range(24)).fillna(0)
fig, ax = plt.subplots(figsize=(11, 3.9))
im = ax.imshow(piv.values, aspect="auto", cmap="Blues")
ax.set_yticks(range(7)); ax.set_yticklabels(["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"])
ax.set_xticks(range(24)); ax.set_xlabel("Giờ trong ngày (giờ mua hàng)")
ax.grid(False)
fig.colorbar(im, ax=ax, pad=0.01).set_label("Số đơn")
ax.set_title("Số đơn theo thứ trong tuần và giờ (2017-01 → 2018-08)", fontsize=11.5)
f_heat = save(fig, "3-1_heatmap_dow_hour")
dow_tot = piv.sum(axis=1)
hour_tot = piv.sum(axis=0)
peak_dow = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"][int(dow_tot.values.argmax())]
low_dow = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"][int(dow_tot.values.argmin())]
peak_hour = int(hour_tot.values.argmax())
night = float(hour_tot.loc[0:5].sum() / hour_tot.sum() * 100)

# ---- figure 5: Black Friday zoom
nov = day.loc["2017-11-01":"2017-12-10"]
bf = pd.Timestamp("2017-11-24")
base = day.loc["2017-11-01":"2017-11-23", "orders"].mean()
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(nov.index, nov["orders"], color=BLUE, lw=1.8, marker="o", ms=3)
ax.axvline(bf, color=ORANGE, ls="--", lw=1.2)
ax.annotate(f"Black Friday 24/11/2017\n{n(day.loc[bf, 'orders'])} đơn, {n(day.loc[bf, 'gmv'])} BRL", (bf, day.loc[bf, "orders"]), xytext=(18, -4), textcoords="offset points", fontsize=9, color=INK)
ax.set_title("Số đơn mỗi ngày quanh Black Friday 2017", fontsize=11.5); vn_axis(ax)
ax.tick_params(axis="x", labelrotation=30, labelsize=8.5)
f_bf = save(fig, "3-1_black_friday")
after = day.loc["2017-11-25":"2017-12-10", "orders"].mean()
yoy_nov = float(day.loc["2017-11-01":"2017-11-30", "gmv"].sum() / day.loc["2017-10-01":"2017-10-31", "gmv"].sum() - 1)

# ---- LaTeX table + handoff
def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


LABEL = {"orders_daily": "Số đơn theo ngày (chu kỳ 7 ngày)", "gmv_daily": "GMV theo ngày (chu kỳ 7 ngày)", "orders_monthly": "Số đơn theo tháng (chu kỳ 12 tháng)", "gmv_monthly": "GMV theo tháng (chu kỳ 12 tháng)"}
rows = "\n".join(f"{esc(LABEL[k])} & {n(len(v[0].trend))} & {n(v[1], 2)} & {n(v[2], 2)}\\\\" for k, v in results.items())
(ROOT / "report" / "tables" / "p8_stl.tex").write_text(
    "\\begin{table}[htbp]\\centering\\scriptsize\\caption{Độ mạnh xu hướng và mùa vụ của phân rã STL (2017-01 đến 2018-08)}\\label{tab:stl}\n\\begin{tabular}{p{7.5cm}rrr}\\toprule\n"
    "\\textbf{Chuỗi} & \\textbf{Số điểm} & \\textbf{Xu hướng $F_T$} & \\textbf{Mùa vụ $F_S$}\\\\\\midrule\n" + rows + "\n\\bottomrule\\end{tabular}\\end{table}\n", encoding="utf-8")

tbl = pd.DataFrame([{"Chuỗi": LABEL[k], "Số điểm": n(len(v[0].trend)), "Độ mạnh xu hướng": n(v[1], 3), "Độ mạnh mùa vụ": n(v[2], 3)} for k, v in results.items()])
sd = results["orders_daily"][0].seasonal
dow_amp = float((sd.groupby(sd.index.day_of_week).mean().max() - sd.groupby(sd.index.day_of_week).mean().min()))
md = [
    f"Phạm vi: **{W0} → {W1}** ({n(len(win))} ngày), đoạn có đủ dữ liệu (2016 chỉ 329 đơn, tháng 2018-09 và 2018-10 chỉ 20 đơn). GMV = tổng giá hàng của đơn không thuộc nhóm Failed. Nguồn: `olist_full`.", "",
    "### Công thức độ mạnh (Hyndman)", "",
    "Phân rã STL: $y_t = T_t + S_t + R_t$ (xu hướng, mùa vụ, phần dư). Độ mạnh:", "",
    "$$F_T = \\max\\Bigl(0,\\; 1 - \\frac{\\operatorname{Var}(R_t)}{\\operatorname{Var}(T_t + R_t)}\\Bigr), \\qquad F_S = \\max\\Bigl(0,\\; 1 - \\frac{\\operatorname{Var}(R_t)}{\\operatorname{Var}(S_t + R_t)}\\Bigr)$$", "",
    "Giá trị gần 1 nghĩa là thành phần đó chi phối chuỗi, gần 0 nghĩa là gần như không có. STL chạy với `robust=True` để đỉnh Black Friday không làm lệch xu hướng và mùa vụ.", "",
    "### Kết quả STL", "", md_table(tbl, ["Số điểm", "Độ mạnh xu hướng", "Độ mạnh mùa vụ"]), "",
    f"- **Xu hướng**: số đơn theo ngày có độ mạnh xu hướng {n(results['orders_daily'][1], 3)}, theo tháng {n(results['orders_monthly'][1], 3)}; xu hướng tăng rõ từ 2017-01 và đi ngang từ khoảng 2018-01.",
    f"- **Mùa vụ tuần** (chu kỳ 7 ngày): độ mạnh {n(results['orders_daily'][2], 3)}; số đơn nhiều nhất vào {peak_dow} và ít nhất vào {low_dow}; chênh giữa ngày cao nhất và thấp nhất của thành phần mùa vụ là {n(dow_amp, 1)} đơn.",
    f"- **Mùa vụ năm** (chu kỳ 12 tháng): độ mạnh {n(results['orders_monthly'][2], 3)} trên chỉ {len(monthly)} tháng. **Giới hạn**: dữ liệu dưới 2 năm, mỗi tháng trong năm chỉ xuất hiện một hoặc hai lần nên STL không tách được mùa vụ theo năm khỏi xu hướng tăng; con số này không đủ cơ sở để kết luận có mùa vụ theo năm.", "",
    f"![Chuỗi theo tuần và tháng]({f_series.replace('figures/', '../figures/')})", "",
    f"- Đơn và GMV tăng gần như liên tục từ 2017-01, đạt đỉnh tuần ở Black Friday (tuần chứa 24/11/2017) rồi giữ mặt bằng mới cao hơn trước đó; tháng 11/2017 có GMV cao hơn tháng 10/2017 {pct(yoy_nov * 100)}.", "",
    f"![STL theo ngày]({f_stl.replace('figures/', '../figures/')})", "",
    f"- Thành phần xu hướng tách được bước nhảy sau Black Friday; phần dư lớn nhất tập trung quanh 24/11/2017.", "",
    f"![STL theo tháng]({f_stlm.replace('figures/', '../figures/')})", "",
    f"![Heatmap thứ x giờ]({f_heat.replace('figures/', '../figures/')})", "",
    f"- Giờ cao điểm là {peak_hour}h; chỉ {pct(night)} số đơn được đặt từ 0h đến 5h sáng. {peak_dow} có nhiều đơn nhất, {low_dow} ít nhất.", "",
    f"![Black Friday]({f_bf.replace('figures/', '../figures/')})", "",
    f"- Black Friday 24/11/2017 có {n(day.loc[bf, 'orders'])} đơn, gấp {n(day.loc[bf, 'orders'] / base, 1)} lần trung bình 23 ngày đầu tháng 11 ({n(base, 0)} đơn/ngày); sau đó số đơn trung bình {n(after, 0)} đơn/ngày (25/11–10/12). GMV ngày này là {n(day.loc[bf, 'gmv'], 2)} BRL.", "",
]
section("seasonality", md)
for k, v in results.items():
    print(k, "FT", round(v[1], 3), "FS", round(v[2], 3))

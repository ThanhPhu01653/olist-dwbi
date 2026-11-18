"""P9 results: numbers, tables and figures for chapter 5.2 from the warehouse (olist_dw) and the landing zone manifests.

    python scripts/p9_results.py
Writes:  handoff/2026-11-18-P9-results.md (all numbers, generated; do not edit by hand)
         report/tables/p9_*.tex   figures/5-2_*.png   docs/diagrams/api-kien-truc.drawio + figures/5-2_kien_truc_api.png (draft)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text

from diagram_kit import BLUE, GREEN, GREY, ORANGE, PURPLE, YELLOW, Diagram
from etl import config
from etl.db import get_engine

FIG, TAB, HAND = ROOT / "figures", ROOT / "report" / "tables", ROOT / "handoff"
LAND = ROOT / "data" / "raw" / "api"
eng = get_engine(config.DB_NAME)
BLUE_D, ORANGE_D, GREY_D, GREEN_D = "#1F6FB2", "#F28E2B", "#8A94A6", "#2E9E6B"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 100})


def q(sql, **p) -> pd.DataFrame:
    with eng.connect() as c:
        return pd.read_sql_query(text(sql), c, params=p or None)


def n(x) -> str:
    return f"{int(round(float(x))):,}".replace(",", ".")


def f1(x, d=1) -> str:
    return f"{float(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def esc(s) -> str:
    return str(s).replace("_", "\\_").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")


def save(fig, name):
    fig.savefig(FIG / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def table_tex(name, caption, label, header, rows, spec, note=""):
    body = "\n".join(" & ".join(esc(c) for c in r) + " \\\\" for r in rows)
    (TAB / name).write_text(
        f"\\begin{{table}}[htbp]\\centering\\scriptsize\\caption{{{caption}}}\\label{{{label}}}\n\\begin{{tabular}}{{{spec}}}\\toprule\n"
        + " & ".join(f"\\textbf{{{esc(h)}}}" for h in header) + " \\\\\\midrule\n" + body + "\n\\bottomrule\\end{tabular}"
        + (f"\\\\[2pt]{{\\footnotesize {note}}}" if note else "") + "\n\\end{table}\n", encoding="utf-8")


md: list[str] = ["# P9 – Kết quả thu thập API (sinh tự động)", "",
                 "*Sinh bởi `python scripts/p9_results.py` từ database `olist_dw` và các manifest trong `data/raw/api/`; chạy lại script để cập nhật. Mọi số liệu lấy từ truy vấn thật.*", ""]

# ------------------------------------------------------------------ 1. collector: calls, records, bytes, seconds (from the landing zone manifests)
rows = []
for mf in sorted(LAND.glob("*/*/manifest.json")):
    for e in json.loads(mf.read_text(encoding="utf-8")):
        rows.append({**e, "run_date": mf.parent.name})
calls = pd.DataFrame(rows)
calls = calls.sort_values("called_at").drop_duplicates(["source", "name"], keep="last")
src = calls.groupby("source").agg(calls=("name", "count"), records=("records", "sum"), bytes=("bytes", "sum"), seconds=("seconds", "sum"),
                                  failed=("error", lambda s: int(s.notna().sum())))
desc = {"ibge": ("IBGE (Localidades, SIDRA)", "estados, 5.571 đô thị, dân số, PIB, IPCA; metadata"), "bcb": ("Banco Central (SGS)", "USD/BRL ngày, IPCA tháng"),
        "holidays": ("BrasilAPI", "ngày lễ quốc gia 2016–2020"), "weather": ("Open-Meteo", "27 thủ phủ: định vị và mưa ngày 2016–2018")}
call_rows = []
for s in ["ibge", "bcb", "holidays", "weather"]:
    if s in src.index:
        r = src.loc[s]
        call_rows.append((desc[s][0], n(r.calls), n(r.records), f1(r.bytes / 1024 / 1024, 2), f1(r.seconds, 1), n(r.failed)))
tot = src.sum()
call_rows.append(("Tổng", n(tot.calls), n(tot.records), f1(tot.bytes / 1024 / 1024, 2), f1(tot.seconds, 1), n(tot.failed)))
table_tex("p9_api_calls.tex", "Thu thập API: số lời gọi, bản ghi, dung lượng JSON và thời gian", "tab:api-calls",
          ["Nguồn", "Lời gọi", "Bản ghi", "JSON (MB)", "Thời gian gọi (giây)", "Lỗi"], call_rows, "lrrrrr",
          "Lấy từ các file \\code{manifest.json} trong landing zone; thời gian là tổng thời gian chờ phản hồi (đã gồm thử lại); bản ghi là số dòng hoặc số điểm dữ liệu trong JSON.")
md += ["## 1. Bảng thu thập (từ manifest của landing zone)", "", "| Nguồn | Lời gọi | Bản ghi | JSON (MB) | Giây | Lỗi |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
md += [f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in call_rows]
detail = calls[calls.source.isin(["ibge", "bcb", "holidays"])][["source", "name", "http_status", "records", "bytes", "seconds"]]
md += ["", "Chi tiết từng lời gọi (không gồm 54 lời gọi của Open-Meteo):", "", "| Nguồn | Lời gọi | HTTP | Bản ghi | Byte | Giây |", "| --- | --- | ---: | ---: | ---: | ---: |"]
md += [f"| {r.source} | {r['name']} | {r.http_status} | {n(r.records)} | {n(r.bytes)} | {f1(r.seconds, 2)} |" for _, r in detail.iterrows()]

# ------------------------------------------------------------------ 2. staging / ODS rows
stg = q("""SELECT 'ibge_municipio' t, count(*) c FROM api.stg_api_ibge_municipio UNION ALL SELECT 'ibge_populacao', count(*) FROM api.stg_api_ibge_populacao
           UNION ALL SELECT 'ibge_pib', count(*) FROM api.stg_api_ibge_pib UNION ALL SELECT 'bcb_serie', count(*) FROM api.stg_api_bcb_serie
           UNION ALL SELECT 'holiday', count(*) FROM api.stg_api_holiday UNION ALL SELECT 'weather_daily', count(*) FROM api.stg_api_weather_daily""")
md += ["", "## 2. Số dòng ở staging (schema api)", "", "| Bảng | Dòng |", "| --- | ---: |"] + [f"| stg_api_{r.t} | {n(r.c)} |" for _, r in stg.iterrows()]
rej = q("SELECT job_name, source_table, reason, count(*) c FROM etl_log.rejected_rows WHERE job_name LIKE 'ods.load_api%' OR job_name LIKE 'api.match%' "
        "AND batch_id = (SELECT max(batch_id) FROM etl_log.rejected_rows WHERE job_name LIKE 'api.match%') GROUP BY 1, 2, 3")

# ------------------------------------------------------------------ 3. city match by tier
st = q("""SELECT method, city_pairs, zips FROM etl_log.api_match_stat WHERE batch_id = (SELECT max(batch_id) FROM etl_log.api_match_stat)""").set_index("method")
order = ["exact", "normalized", "fuzzy", "override", "unmatched"]
st = st.reindex(order).fillna(0)
tp, tz = int(st.city_pairs.sum()), int(st.zips.sum())
orders_by = q("""SELECT coalesce(g.match_method, 'none') AS method, count(DISTINCT f.order_id) AS orders, sum(f.price) AS gmv
                 FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
                 JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key GROUP BY 1""").set_index("method").reindex(order).fillna(0)
tg = float(orders_by.gmv.sum())
label = {"exact": "1. Khớp đúng", "normalized": "2. Sau unaccent và chuẩn hoá", "fuzzy": "3. Fuzzy (rapidfuzz)", "override": "4. Bảng ghép tay", "unmatched": "Không khớp"}
cum_p = cum_z = cum_g = 0
match_rows = []
for m in order:
    p, z, g = int(st.loc[m, "city_pairs"]), int(st.loc[m, "zips"]), float(orders_by.loc[m, "gmv"])
    if m != "unmatched":
        cum_p, cum_z, cum_g = cum_p + p, cum_z + z, cum_g + g
        match_rows.append((label[m], n(p), n(z), n(orders_by.loc[m, "orders"]), f1(cum_p / tp * 100), f1(cum_z / tz * 100), f1(cum_g / tg * 100)))
    else:
        match_rows.append((label[m], n(p), n(z), n(orders_by.loc[m, "orders"]), "–", "–", f1(g / tg * 100) + " (chưa khớp)"))
table_tex("p9_match_tiers.tex", "Ghép thành phố Olist với đô thị IBGE: số cặp (bang, thành phố), zip và GMV sau từng tầng", "tab:api-match",
          ["Tầng", "Cặp (bang, thành phố)", "Zip", "Đơn", "Luỹ kế cặp (%)", "Luỹ kế zip (%)", "Luỹ kế GMV (%)"], match_rows, "lrrrrrr",
          f"Tổng {n(tp)} cặp (bang, thành phố), {n(tz)} zip. Luỹ kế GMV tính theo bang của khách; cột Đơn là đơn có doanh thu.")
md += ["", "## 3. Ghép (bang, thành phố) với đô thị IBGE theo tầng", "", f"Tổng {n(tp)} cặp, {n(tz)} zip, GMV {f1(tg, 2)} BRL.", "",
       "| Tầng | Cặp | Zip | Đơn | Luỹ kế cặp % | Luỹ kế zip % | Luỹ kế GMV % |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
md += [f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} |" for a, b, c, d, e, f, g in match_rows]
ex = q("""SELECT m.method, m.state_code, m.city AS olist_city, i.name AS ibge_name, m.score
          FROM ods.city_ibge_match m JOIN ods.ibge_municipio i USING (ibge_code) WHERE m.method <> 'exact'
          ORDER BY CASE m.method WHEN 'fuzzy' THEN 1 WHEN 'override' THEN 2 ELSE 3 END, m.score DESC, m.state_code, m.city""")
ex_n = ex[ex.method == "normalized"].head(6)
ex_rows = [(r.method, r.state_code, r.olist_city, r.ibge_name, f1(r.score)) for _, r in pd.concat([ex_n, ex[ex.method == "fuzzy"].head(5), ex[ex.method == "override"].head(4)]).iterrows()]
table_tex("p9_match_examples.tex", "Ví dụ tên thành phố lệch đã ghép được", "tab:api-match-ex", ["Tầng", "Bang", "Tên trong Olist", "Tên IBGE", "Điểm"], ex_rows, "llllr")
md += ["", "Ví dụ tên lệch đã sửa được:", "", "| Tầng | Bang | Olist | IBGE | Điểm |", "| --- | --- | --- | --- | ---: |"] + [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in ex_rows]
bigun = q("""SELECT p.state_code, p.city, p.zips, (SELECT sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
                   JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key WHERE g.state_code = p.state_code AND g.city = p.city) AS gmv
            FROM ods.v_geo_city_pair p LEFT JOIN ods.city_ibge_match m USING (state_code, city) WHERE m.city IS NULL ORDER BY gmv DESC NULLS LAST LIMIT 8""")
md += ["", "Cặp không khớp có GMV lớn nhất (đa số là quận, huyện hoặc khu dân cư không phải đô thị):", "", "| Bang | Thành phố (Olist) | Zip | GMV |", "| --- | --- | ---: | ---: |"]
md += [f"| {r.state_code} | {r.city} | {r.zips} | {f1(r.gmv or 0, 2)} |" for _, r in bigun.iterrows()]
munc = q("SELECT count(*) c, count(DISTINCT mesorregiao) me, count(DISTINCT microrregiao) mi FROM (SELECT DISTINCT ibge_municipio_code, mesorregiao, microrregiao FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL) x").iloc[0]
geo = q("SELECT count(*) FILTER (WHERE ibge_municipio_code IS NOT NULL) matched, count(*) total, count(DISTINCT ibge_municipio_code) munis FROM dw.dim_geography WHERE geography_key <> -1").iloc[0]
md += ["", f"Zip gán mã IBGE: {n(geo.matched)} / {n(geo.total)} ({f1(geo.matched / geo.total * 100)}%), thuộc {n(geo.munis)} đô thị khác nhau ({n(munc.me)} mesorregião, {n(munc.mi)} microrregião).",
       f"IBGE có {n(q('select count(*) c from ods.ibge_municipio').iloc[0, 0])} đô thị; dân số 2016–2018 có cho {n(q('select count(distinct ibge_code) c from ods.ibge_population').iloc[0, 0])} đô thị "
       "(1 đô thị mới lập không có số liệu những năm này, 3 dòng ghi ở etl_log.rejected_rows)."]

# figure: match rate by tier
fig, ax = plt.subplots(figsize=(8.2, 3.9))
tiers = [label[m] for m in order[:4]]
cz = [sum(st.loc[order[:i + 1], "zips"]) / tz * 100 for i in range(4)]
cp = [sum(st.loc[order[:i + 1], "city_pairs"]) / tp * 100 for i in range(4)]
cg = [sum(orders_by.loc[order[:i + 1], "gmv"]) / tg * 100 for i in range(4)]
x = range(4)
ax.bar([i - 0.27 for i in x], cp, 0.27, color=GREY_D, label="cặp (bang, thành phố)")
ax.bar(x, cz, 0.27, color=BLUE_D, label="zip")
ax.bar([i + 0.27 for i in x], cg, 0.27, color=ORANGE_D, label="GMV")
for i in x:
    for off, v in ((-0.27, cp[i]), (0, cz[i]), (0.27, cg[i])):
        ax.text(i + off, v + 0.6, f"{v:.1f}", ha="center", fontsize=7)
ax.set_xticks(list(x))
ax.set_xticklabels(tiers, fontsize=8)
ax.set_ylim(80, 102)
ax.set_ylabel("% luỹ kế đã gán mã IBGE")
ax.set_title("Tỉ lệ khớp luỹ kế sau từng tầng ghép đô thị", fontsize=11)
ax.legend(fontsize=8, loc="lower right")
save(fig, "5-2_ty_le_khop_theo_tang.png")

# ------------------------------------------------------------------ 4. findings: GMV per 1,000 inhabitants
pc = q("SELECT * FROM mart_market.v_gmv_per_capita_state")
for y in (2017, 2018):
    d = pc[pc.year == y].sort_values("gmv_per_1000_pop", ascending=False)
    md += ["", f"## 4.{y - 2016}. GMV trên 1.000 dân theo bang, {y}", "", "| Hạng đầu người | Bang | Dân số | GMV (BRL) | GMV / 1.000 dân | Hạng GMV |", "| ---: | --- | ---: | ---: | ---: | ---: |"]
    md += [f"| {r.rank_per_capita} | {r.state_code} | {n(r.population)} | {n(r.gmv)} | {f1(r.gmv_per_1000_pop, 2)} | {r.rank_gmv} |" for _, r in d.iterrows()]
d17 = pc[pc.year == 2017].sort_values("gmv_per_1000_pop")
top5, bot5 = d17.tail(5)[::-1], d17.head(5)
table_tex("p9_state_per_capita.tex", "GMV trên 1.000 dân theo bang năm 2017 (5 bang cao nhất và 5 bang thấp nhất) so với hạng theo GMV tuyệt đối", "tab:api-percapita",
          ["Bang", "Dân số", "GMV (BRL)", "GMV / 1.000 dân", "Hạng đầu người", "Hạng GMV"],
          [(r.state_code, n(r.population), n(r.gmv), f1(r.gmv_per_1000_pop, 2), r.rank_per_capita, r.rank_gmv) for _, r in pd.concat([top5, bot5]).iterrows()], "lrrrrr",
          "GMV tính theo bang của khách, đơn không thuộc nhóm Failed; dân số là ước tính IBGE 2017.")
corr = d17[["gmv_per_1000_pop", "gmv"]].corr(method="spearman").iloc[0, 1]
big_move = d17.assign(delta=d17.rank_gmv - d17.rank_per_capita).sort_values("delta")
md += ["", f"Spearman giữa GMV/1.000 dân và GMV tuyệt đối (27 bang, 2017): {f1(corr, 2)}.",
       "Bang tụt nhiều hạng nhất khi tính theo đầu người: " + ", ".join(f"{r.state_code} ({r.rank_gmv} → {r.rank_per_capita})" for _, r in big_move.head(3).iterrows()) + ".",
       "Bang lên nhiều hạng nhất: " + ", ".join(f"{r.state_code} ({r.rank_gmv} → {r.rank_per_capita})" for _, r in big_move.tail(3)[::-1].iterrows()) + "."]

fig, ax = plt.subplots(figsize=(7.6, 7.2))
dd = d17.sort_values("gmv_per_1000_pop")
colors = [{"Sudeste": BLUE_D, "Sul": GREEN_D, "Nordeste": ORANGE_D, "Norte": "#9B5DE5", "Centro-Oeste": "#00A6A6"}[r] for r in dd.region]
ax.barh(dd.state_code, dd.gmv_per_1000_pop, color=colors)
for yi, (v, rg, ra) in enumerate(zip(dd.gmv_per_1000_pop, dd.rank_gmv, dd.rank_per_capita)):
    ax.text(v + 0.6, yi, f"{v:.1f}  (hạng GMV {rg})", va="center", fontsize=7)
ax.set_xlabel("BRL GMV trên 1.000 dân (2017)")
ax.set_title("Bang nào mua nhiều nhất theo đầu người?", fontsize=11)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=l) for l, c in (("Sudeste", BLUE_D), ("Sul", GREEN_D), ("Nordeste", ORANGE_D), ("Norte", "#9B5DE5"), ("Centro-Oeste", "#00A6A6"))], fontsize=8, loc="lower right")
save(fig, "5-2_gmv_dau_nguoi_theo_bang.png")

city = q("SELECT * FROM mart_market.v_gmv_per_capita_city WHERE year = 2017 AND population >= 100000 ORDER BY gmv_per_1000_pop DESC")
md += ["", "### Đô thị từ 100 nghìn dân, 2017: 8 đô thị cao nhất theo GMV/1.000 dân", "", "| Đô thị | Bang | Dân số | GMV | GMV / 1.000 dân | Hạng GMV |", "| --- | --- | ---: | ---: | ---: | ---: |"]
md += [f"| {r.city} | {r.state_code} | {n(r.population)} | {n(r.gmv)} | {f1(r.gmv_per_1000_pop, 2)} | {r.rank_gmv} |" for _, r in city.head(8).iterrows()]
md += ["", f"Số đô thị từ 100 nghìn dân có đơn năm 2017: {len(city)}."]

# ------------------------------------------------------------------ 5. nominal vs real growth and USD
real = q("SELECT * FROM mart_market.v_gmv_real_month WHERE in_window ORDER BY year_month")
g17 = real[(real.year_month >= "2017-01") & (real.year_month <= "2017-08")]
g18 = real[(real.year_month >= "2018-01") & (real.year_month <= "2018-08")]
nom17, nom18, re17, re18 = float(g17.gmv_nominal.sum()), float(g18.gmv_nominal.sum()), float(g17.gmv_real.sum()), float(g18.gmv_real.sum())
gn, gr = (nom18 / nom17 - 1) * 100, (re18 / re17 - 1) * 100
usd = q("SELECT * FROM mart_market.v_gmv_usd_month WHERE in_window ORDER BY year_month")
u17, u18 = float(usd[(usd.year_month >= "2017-01") & (usd.year_month <= "2017-08")].gmv_usd.sum()), float(usd[(usd.year_month >= "2018-01") & (usd.year_month <= "2018-08")].gmv_usd.sum())
gu = (u18 / u17 - 1) * 100
rate = q("SELECT min(usd_brl) lo, max(usd_brl) hi FROM dw.dim_date WHERE full_date BETWEEN DATE '2017-01-01' AND DATE '2018-08-31'").iloc[0]
rate_m = q("SELECT year_month, avg_usd_brl FROM mart_market.v_gmv_usd_month WHERE year_month IN ('2017-01','2018-08')").set_index("year_month").avg_usd_brl
ipca = q("SELECT (SELECT ipca_index FROM ods.ipca_month WHERE month_date = DATE '2017-08-01') a, (SELECT ipca_index FROM ods.ipca_month WHERE month_date = DATE '2018-08-01') b").iloc[0]
infl = (float(ipca.b) / float(ipca.a) - 1) * 100
md += ["", "## 5. GMV danh nghĩa, GMV thực và GMV quy USD", "",
       f"Cùng kỳ tháng 1–8: GMV 2017 = {f1(nom17, 2)} BRL, 2018 = {f1(nom18, 2)} BRL: **tăng danh nghĩa {f1(gn)}%**. Chia chỉ số IPCA (giá 01/2016): 2017 = {f1(re17, 2)}, 2018 = {f1(re18, 2)}: **tăng thực {f1(gr)}%**.",
       f"Lạm phát IPCA 08/2017 → 08/2018: {f1(infl)}% (chỉ số {f1(ipca.a, 3)} → {f1(ipca.b, 3)}).",
       f"GMV quy USD (mỗi dòng hàng theo tỷ giá ngày mua), tháng 1–8: 2017 = {f1(u17, 2)} USD, 2018 = {f1(u18, 2)} USD: **tăng {f1(gu)}%** (so với {f1(gn)}% bằng BRL); tỷ giá bình quân gia quyền theo GMV: {f1(rate_m.get('2017-01', 0), 3)} (01/2017) → {f1(rate_m.get('2018-08', 0), 3)} (08/2018); "
       f"khoảng {f1(rate.lo, 3)} – {f1(rate.hi, 3)} BRL/USD trong 2017-01 → 2018-08.", ""]
table_tex("p9_growth.tex", "Tăng trưởng GMV tháng 1–8 năm 2018 so với cùng kỳ 2017: danh nghĩa, thực và quy USD", "tab:api-growth",
          ["Thước đo", "2017 (1–8)", "2018 (1–8)", "Tăng (%)"],
          [("GMV danh nghĩa (BRL)", n(nom17), n(nom18), f1(gn)), ("GMV thực (BRL, giá 01/2016)", n(re17), n(re18), f1(gr)), ("GMV quy USD", n(u17), n(u18), f1(gu))], "lrrr",
          f"Lạm phát IPCA từ 08/2017 đến 08/2018: {f1(infl)}\\%.")
fig, ax = plt.subplots(figsize=(8.4, 3.9))
xs = range(len(real))
ax.plot(xs, real.gmv_nominal / 1e6, color=BLUE_D, lw=2, label="GMV danh nghĩa")
ax.plot(xs, real.gmv_real / 1e6, color=ORANGE_D, lw=2, label="GMV thực (giá 01/2016)")
ax.set_xticks(list(xs)[::3])
ax.set_xticklabels(real.year_month.iloc[::3], fontsize=8, rotation=0)
ax.set_ylabel("triệu BRL")
ax.set_title("GMV danh nghĩa và GMV thực theo tháng", fontsize=11)
ax.legend(fontsize=8)
save(fig, "5-2_danh_nghia_so_voi_thuc.png")
fig, ax = plt.subplots(figsize=(8.4, 3.9))
ax.bar(range(len(usd)), usd.gmv_usd / 1e3, color=GREEN_D)
ax.set_ylabel("nghìn USD")
ax.set_xticks(list(range(len(usd)))[::3])
ax.set_xticklabels(usd.year_month.iloc[::3], fontsize=8)
ax2 = ax.twinx()
ax2.plot(range(len(usd)), usd.avg_usd_brl, color=ORANGE_D, lw=2)
ax2.set_ylabel("BRL / USD (tỷ giá bình quân gia quyền theo GMV)")
ax2.set_ylim(2.5, 4.5)
ax2.spines["top"].set_visible(False)
ax.set_title("GMV quy USD theo tháng và tỷ giá", fontsize=11)
save(fig, "5-2_gmv_usd_theo_thang.png")

# ------------------------------------------------------------------ 6. holidays
he = q("SELECT * FROM mart_market.v_holiday_effect ORDER BY day_type, is_holiday_official")
diff = q("SELECT agreement, count(*) c FROM mart_market.v_holiday_diff GROUP BY 1").set_index("agreement").c
only = q("SELECT full_date, holiday_name_official FROM mart_market.v_holiday_diff WHERE agreement = 'only BrasilAPI' ORDER BY full_date")
wd = he[he.day_type == "weekday"].set_index("is_holiday_official")
eff = (float(wd.loc[True, "avg_orders_per_day"]) / float(wd.loc[False, "avg_orders_per_day"]) - 1) * 100
md += ["", "## 6. Ngày lễ", "", f"BrasilAPI có {int(q('select count(distinct holiday_date) c from ods.holiday_official').iloc[0, 0])} ngày lễ quốc gia 2016–2020; thư viện `holidays` đánh dấu {int(q('select count(*) c from dw.dim_date where is_holiday_br').iloc[0, 0])} ngày (cờ `is_holiday_br`). "
       f"Cả hai cùng có {int(diff.get('both', 0))} ngày; chỉ BrasilAPI có {int(diff.get('only BrasilAPI', 0))} ngày; chỉ thư viện có {int(diff.get('only holidays library', 0))} ngày.",
       "Ngày chỉ có ở BrasilAPI (mẫu): " + "; ".join(f"{r.full_date:%d/%m/%Y} {r.holiday_name_official}" for _, r in only.head(8).iterrows()) + ".", "",
       "| Loại ngày | Lễ quốc gia | Số ngày | Đơn TB / ngày | GMV TB / ngày |", "| --- | --- | ---: | ---: | ---: |"]
md += [f"| {r.day_type} | {'có' if r.is_holiday_official else 'không'} | {r.days} | {r.avg_orders_per_day} | {f1(r.avg_gmv_per_day, 2)} |" for _, r in he.iterrows()]
md += ["", f"Ngày lễ rơi vào ngày thường (2017-01 → 2018-08, bỏ Black Friday): đơn trung bình thấp hơn ngày thường không lễ {f1(abs(eff))}%."]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
labels = ["Thường\n(không lễ)", "Thường\n(lễ quốc gia)", "Cuối tuần\n(không lễ)"]
vals = [float(wd.loc[False, "avg_orders_per_day"]), float(wd.loc[True, "avg_orders_per_day"]),
        float(he[(he.day_type == "weekend") & (~he.is_holiday_official)].avg_orders_per_day.iloc[0])]
ax.bar(labels, vals, color=[BLUE_D, ORANGE_D, GREY_D])
for i, v in enumerate(vals):
    ax.text(i, v + 2, f"{v:.1f}", ha="center", fontsize=9)
ax.set_ylabel("đơn trung bình mỗi ngày")
ax.set_title("Ngày lễ quốc gia và số đơn (01/2017–08/2018)", fontsize=11)
save(fig, "5-2_ngay_le_va_don.png")
table_tex("p9_holidays.tex", "Ngày lễ quốc gia và số đơn trung bình mỗi ngày (2017-01 đến 2018-08, không tính Black Friday)", "tab:api-holiday",
          ["Loại ngày", "Lễ quốc gia (BrasilAPI)", "Số ngày", "Đơn TB / ngày", "GMV TB / ngày (BRL)"],
          [(r.day_type, "có" if r.is_holiday_official else "không", r.days, r.avg_orders_per_day, f1(r.avg_gmv_per_day, 2)) for _, r in he.iterrows()], "llrrr")

# ------------------------------------------------------------------ 7. rain (optional source)
rain = q("SELECT * FROM mart_market.v_late_by_rain ORDER BY rain_bucket_no")
md += ["", "## 7. (Tuỳ chọn) Tỷ lệ giao trễ theo lượng mưa ngày giao tại thủ phủ bang của khách", "", "| Mưa ngày giao | Đơn đã giao | Đơn trễ | Tỷ lệ trễ % |", "| --- | ---: | ---: | ---: |"]
md += [f"| {r.rain_bucket} | {n(r.delivered_orders)} | {n(r.late_orders)} | {r.late_rate_pct} |" for _, r in rain.iterrows()]
md += ["", "Giới hạn: mưa đo tại thủ phủ của bang, không phải tại nơi khách ở; đây là liên hệ thống kê."]
fig, ax = plt.subplots(figsize=(6.2, 3.6))
ax.bar(rain.rain_bucket, rain.late_rate_pct.astype(float), color=[BLUE_D, BLUE_D, ORANGE_D, ORANGE_D])
for i, v in enumerate(rain.late_rate_pct.astype(float)):
    ax.text(i, v + 0.1, f"{v:.2f}%", ha="center", fontsize=9)
ax.set_ylabel("tỷ lệ giao trễ (%)")
ax.set_title("Mưa ngày giao và tỷ lệ giao trễ", fontsize=11)
save(fig, "5-2_mua_va_giao_tre.png")

# ------------------------------------------------------------------ 8. new columns, tests
newcols = q("""SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'dw' AND table_name IN ('dim_geography', 'dim_date')
               AND column_name IN ('ibge_municipio_code','microrregiao','mesorregiao','populacao_2016','populacao_2017','populacao_2018','match_method','usd_brl','ipca_index','is_holiday_official','holiday_name_official')
               ORDER BY table_name, ordinal_position""")
tests = q("""SELECT count(*) FILTER (WHERE check_name LIKE 'API:%' OR check_name LIKE 'fact_state_year:%' OR check_name LIKE 'mart_market.%') AS p9, count(*) FILTER (WHERE passed AND (check_name LIKE 'API:%' OR check_name LIKE 'fact_state_year:%' OR check_name LIKE 'mart_market.%')) AS p9_ok,
                    count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check WHERE batch_id = (SELECT max(batch_id) FROM etl_log.dq_check WHERE check_name LIKE 'API:%') AND check_name NOT LIKE 'EDA:%'""").iloc[0]
md += ["", "## 8. Kiểm thử", "", f"Lô kiểm thử cuối: {int(tests.ok)}/{int(tests.total)} phép đạt (không tính 6 phép đối chiếu EDA); trong đó test của P9: {int(tests.p9_ok)}/{int(tests.p9)} đạt."]
rows_dw = q("""SELECT (SELECT count(*) FROM dw.dim_geography) geo, (SELECT count(*) FROM dw.dim_date) dtc, (SELECT count(*) FROM dw.fact_state_year) fsy""").iloc[0]
md += ["", f"Số dòng: dim_geography {n(rows_dw.geo)}, dim_date {n(rows_dw.dtc)}, fact_state_year {n(rows_dw.fsy)}.", "",
       "Cột mới: " + ", ".join(f"`{r.table_name}.{r.column_name}`" for _, r in newcols.iterrows()) + "."]

# ------------------------------------------------------------------ 9. architecture diagram (draft; the group redraws it in draw.io)
d = Diagram("5-2_kien_truc_api", 1500, 420)
d.label(20, 8, 700, 28, "Kiến trúc thu thập dữ liệu API (P9): nguồn → collector → landing zone → staging → ODS → kho → mart → BI", 15)
xs0, w, h, y0 = 20, 170, 110, 80
cols = [("API công khai", "IBGE Localidades và SIDRA\nBanco Central (SGS)\nBrasilAPI (ngày lễ)\nOpen-Meteo (mưa)", BLUE), ("Collector", "api_ingest (Python)\nrequests + thử lại, backoff\ntimeout, giới hạn tốc độ\nwatermark BCB", YELLOW),
        ("Landing zone", "data/raw/api/<nguồn>/<ngày>/\nJSON thô nguyên văn\nmanifest.json: URL, status,\nbản ghi, byte, sha256", GREY), ("Staging (api)", "stg_api_ibge_*\nstg_api_bcb_serie\nstg_api_holiday\nstg_api_weather_*", GREY),
        ("ODS", "ibge_municipio, population\nfx_usd_brl (điền ngày nghỉ)\nipca_month (chỉ số)\ncity_ibge_match (4 tầng)", GREEN), ("Kho (dw)", "dim_geography + mã IBGE\ndim_date + tỷ giá, IPCA\nfact_state_year (bang x năm)", ORANGE),
        ("Mart và BI", "mart_market (7 view)\nCSV Power BI\nDashboard D8", PURPLE)]
ids = []
for i, (t, body, col) in enumerate(cols):
    x = xs0 + i * (w + 38)
    d.box(x, y0, w, 32, t, fill=col, bold=True, font=13)
    ids.append(d.box(x, y0 + 36, w, h + 30, body, fill=col, font=11, align="center"))
for a, b in zip(ids, ids[1:]):
    d.arrow(a, b)
d.box(20, 290, 1440, 40, "etl_log: api_call (mỗi lời gọi), job_run, rejected_rows (thành phố không khớp), api_match_stat (tỉ lệ khớp theo tầng), watermark", fill="#FFFBEA", font=12, shape="frame", align="center", dashed=True)
d.box(20, 350, 700, 40, "Lỗi API: ghi vào etl_log, không chặn nguồn khác, không làm hỏng pipeline chính (cột mới giữ NULL)", fill="#FDE2E2", font=11)
d.box(760, 350, 700, 40, "Dựng lại từ đầu (rebuild_all) dùng landing zone, không cần mạng", fill=GREEN, font=11)
d.save("api-kien-truc.drawio", "5-2_kien_truc_api.png")

(HAND / "2026-11-18-P9-results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("written handoff/2026-11-18-P9-results.md, report/tables/p9_*.tex, figures/5-2_*.png")


# ------------------------------------------------------------------ D8 expected values (measures of powerbi/measures.md section 8), written into huong-dan/dashboards/D8.md
def d8_expected() -> None:
    scopes = [("Toàn bộ dữ liệu", "TRUE", None), ("Cửa sổ 2017-01 → 2018-08", "d.year_month BETWEEN '2017-01' AND '2018-08'", None),
              ("Năm 2017", "d.year = 2017", None), ("Năm 2018", "d.year = 2018", None)]
    vals = {}
    for name, cond, _ in scopes:
        r = q(f"""SELECT sum(f.price) AS gmv, sum(f.price / d.usd_brl) AS gmv_usd, sum(f.price * 100 / d.ipca_index) AS gmv_real,
                         count(DISTINCT f.order_id) FILTER (WHERE d.is_holiday_official) AS orders_hol
                  FROM dw.fact_order_item f JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
                  JOIN dw.dim_date d ON d.date_key = f.purchase_date_key WHERE {cond}""").iloc[0]
        vals[name] = r
    md_rows = ["| Measure | " + " | ".join(s[0] for s in scopes) + " |", "| --- | " + " | ".join("---:" for _ in scopes) + " |"]
    md_rows.append("| GMV (BRL) | " + " | ".join(f1(vals[s[0]].gmv, 2) for s in scopes) + " |")
    md_rows.append("| GMV USD | " + " | ".join(f1(vals[s[0]].gmv_usd, 2) for s in scopes) + " |")
    md_rows.append("| Avg USD/BRL | " + " | ".join(f1(vals[s[0]].gmv / vals[s[0]].gmv_usd, 4) for s in scopes) + " |")
    md_rows.append("| GMV real (giá 01/2016) | " + " | ".join(f1(vals[s[0]].gmv_real, 2) for s in scopes) + " |")
    md_rows.append("| Orders on official holidays | " + " | ".join(n(vals[s[0]].orders_hol) for s in scopes) + " |")
    pop = q("SELECT year, sum(population) p, sum(gmv) g FROM mart_market.v_gmv_per_capita_state GROUP BY year ORDER BY year").set_index("year")
    md_rows += ["", "| Năm | Population (Brazil) | GMV | GMV per 1000 pop (Brazil) |", "| ---: | ---: | ---: | ---: |"]
    md_rows += [f"| {y} | {n(r.p)} | {f1(r.g, 2)} | {f1(r.g / r.p * 1000, 2)} |" for y, r in pop.iterrows()]
    md_rows += ["", "GMV per 1000 pop theo bang (năm 2017): " + ", ".join(f"{r.state_code} {f1(r.gmv_per_1000_pop, 2)}" for _, r in d17.sort_values("gmv_per_1000_pop", ascending=False).head(5).iterrows()) + " (5 bang đầu; đủ 27 bang ở `handoff/2026-11-18-P9-results.md` mục 4.1)."]
    yo = real[real.year_month.isin(["2018-05", "2018-08"])].set_index("year_month")
    md_rows += ["", "| Tháng | GMV | GMV real | GMV YoY % (danh nghĩa) | GMV real YoY % |", "| --- | ---: | ---: | ---: | ---: |"]
    md_rows += [f"| {m} | {f1(r.gmv_nominal, 2)} | {f1(r.gmv_real, 2)} | {r.nominal_yoy_pct} | {r.real_yoy_pct} |" for m, r in yo.iterrows()]
    md_rows += ["", f"Cùng kỳ tháng 1–8 (2018 so với 2017): GMV danh nghĩa +{f1(gn)}%, GMV real +{f1(gr)}%, GMV USD +{f1(gu)}%."]
    p = ROOT / "huong-dan" / "dashboards" / "D8.md"
    t = p.read_text(encoding="utf-8")
    a, b = t.index("<!-- D8:EXPECTED:START -->"), t.index("<!-- D8:EXPECTED:END -->")
    p.write_text(t[:a] + "<!-- D8:EXPECTED:START -->\n*Sinh bởi `python scripts/p9_results.py`; số của DB1–DB4 không đổi (xem `powerbi/measures.md` mục 7).*\n\n" + "\n".join(md_rows) + "\n" + t[b:], encoding="utf-8", newline="\n")


d8_expected()
print("D8 expected values written")

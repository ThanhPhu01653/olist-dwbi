"""P8-E2: ETL summary from etl_log.job_run (olist_dw):
  (1) stage table: stage -> content -> tool -> result (rows from etl_log, first full batch and total after all batches)
  (2) job diagram of run_pipeline (job name, order, table out and rows) generated from job_run of the first full batch -> docs/diagrams/etl-jobs.drawio + figures/3-3_etl_jobs.png
  (3) warehouse load result table: table, type, columns, rows, reconciliation against the source (olist_full) and dq_check results
-> report/tables/p8_etl_stages.tex, p8_etl_results.tex, handoff/2026-11-14-P8-etl.md.   python scripts/p8_etl.py

Chapter 3 describes the CORE pipeline only. Since P9 the same batches also contain the API step (chapter 5); every figure written to report/tables/ is
therefore computed WITHOUT it: jobs of layers api / api_ods, the three enrichment jobs and the 20 API tests are left out and their time is subtracted.
The split (core / API) of every batch is written separately to handoff/2026-11-14-P8-etl.md (section "Tách thời gian").
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pandas as pd
from sqlalchemy import text

from diagram_kit import BLUE, GREEN, GREY, ORANGE, PURPLE, YELLOW, Diagram
from etl import config
from etl.db import get_engine

dw = get_engine(config.DB_NAME)
full = get_engine(config.DB_NAME_FULL)


# P9 objects that belong to chapter 5, not to the core pipeline
API_JOBS = ("dw.enrich_dim_geography", "dw.enrich_dim_date", "dw.load_fact_state_year")
CORE_JOB = "layer NOT IN ('api', 'api_ods') AND job_name NOT IN ('dw.enrich_dim_geography', 'dw.enrich_dim_date', 'dw.load_fact_state_year')"
API_TEST = r"check_name ~ '^(API|fact_state_year|mart_market)'"       # the 20 checks of sql/90_tests/050_api_tests.sql
CORE_TEST = r"check_name !~ '^(API|fact_state_year|mart_market)' AND check_name NOT LIKE 'EDA:%'"      # 136 checks of the warehouse
CORE_TEST_EDA = r"check_name !~ '^(API|fact_state_year|mart_market)'"                                      # the same + 6 report-only EDA cross-checks = 142
API_COLS = ("ibge_municipio_code", "microrregiao", "mesorregiao", "populacao_2016", "populacao_2017", "populacao_2018", "match_method",
            "usd_brl", "ipca_index", "is_holiday_official", "holiday_name_official")                      # columns added by P9 to dim_geography and dim_date


def q(eng, sql, **p):
    with eng.connect() as c:
        return pd.read_sql_query(text(sql), c, params=p or None)


def n(x) -> str:
    return f"{int(x):,}".replace(",", ".")


def esc(s) -> str:
    return str(s).replace("_", "\\_").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#").replace("→", "$\\rightarrow$")


first = int(q(dw, "SELECT min(batch_id) b FROM etl_log.batch_metrics WHERE mode='full'").iloc[0, 0])
nb = int(q(dw, "SELECT count(*) c FROM etl_log.batch_metrics").iloc[0, 0])
jobs = q(dw, """SELECT run_id, job_name, layer, target_table, round(extract(epoch FROM finished_at - started_at)::numeric, 2) AS sec, rows_read, rows_inserted, rows_updated, rows_rejected
                FROM etl_log.job_run WHERE batch_id = :b AND job_name <> 'pipeline.full' AND """ + CORE_JOB + """ ORDER BY run_id""", b=first)
# tests.run counts every check of the batch; the API ones belong to chapter 5
_api_n = int(q(dw, "SELECT count(*) AS c FROM etl_log.dq_check WHERE batch_id = :b AND " + API_TEST, b=first).iloc[0, 0])
jobs.loc[jobs.layer == "test", "rows_read"] -= _api_n
tot = q(dw, """SELECT layer, count(*) AS runs, sum(rows_read) AS rd, sum(rows_inserted) AS ins, sum(rows_updated) AS upd, sum(rows_rejected) AS rej
               FROM etl_log.job_run WHERE job_name NOT LIKE 'pipeline.%' AND """ + CORE_JOB + """ GROUP BY 1""").set_index("layer")
first_l = jobs.groupby("layer").agg(runs=("run_id", "count"), rd=("rows_read", "sum"), ins=("rows_inserted", "sum"), rej=("rows_rejected", "sum"), sec=("sec", "sum"))
dq = q(dw, "SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check WHERE " + CORE_TEST_EDA + " AND batch_id = (SELECT max(batch_id) FROM etl_log.dq_check)").iloc[0]
dq_first = q(dw, "SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check WHERE " + CORE_TEST_EDA + " AND batch_id = :b", b=first).iloc[0]

# ------------------------------------------------------------------ (1) stage table
S = []
st = first_l.loc["staging"]
S.append(("Extract", "Chép nguyên trạng 11 bảng nguồn vào staging, gắn mã lô và thời điểm nạp; full hoặc tăng dần (watermark theo ngày mua của đơn, các bảng khác theo khoá)", "Python + SQL (SQLAlchemy)",
          f"lô đầu: {int(st.runs)} job, {n(st.ins)} dòng vào staging; tổng {nb} lô: {n(tot.loc['staging', 'ins'])} dòng"))
od = first_l.loc["ods"]
S.append(("Seed và ODS", "Nạp 6 bảng tham chiếu từ file seed; làm sạch, chuẩn hoá, gắn cờ lỗi; dòng không nạp được ghi rejected_rows kèm lý do", "SQL procedure (PL/pgSQL), Python đọc seed",
          f"lô đầu: {int(od.runs)} job, {n(od.ins)} dòng vào ODS, {n(od.rej)} dòng bị loại; tổng {nb} lô: {n(tot.loc['ods', 'ins'])} dòng vào, {n(tot.loc['ods', 'rej'])} bị loại"))
dwl = first_l.loc["dw"]
S.append(("Dimension và fact", "Nạp 10 dimension (khoá thay thế, SCD1 và SCD2) rồi 6 fact (tra khoá theo phiên bản hiệu lực, tính thời gian từng chặng)", "SQL procedure (PL/pgSQL)",
          f"lô đầu: {int(dwl.runs)} job, {n(dwl.ins)} dòng chèn; tổng {nb} lô: {n(tot.loc['dw', 'ins'])} dòng chèn, {n(tot.loc['dw', 'upd'])} dòng cập nhật"))
mk = jobs[jobs.layer == "mart"].iloc[0]
S.append(("Data mart", "Làm mới các materialized view của bốn mart", "SQL (REFRESH MATERIALIZED VIEW)", f"lô đầu: {n(mk.rows_read)} dòng đọc, {mk.sec:.1f} giây"))
S.append(("Kiểm thử", "Chạy các truy vấn kiểm thử số dòng, tổng tiền, grain, khoá ngoại, logic nghiệp vụ; ghi dq_check", "Python + SQL (sql/90_tests)", f"lô đầu: {int(dq_first.ok)}/{int(dq_first.total)} phép đạt; lô cuối: {int(dq.ok)}/{int(dq.total)} đạt"))
S.append(("Xuất cho Power BI", "Xuất bảng dw, mart và etl_log ra 37 file CSV (UTF-8 có BOM)", "Python (pandas)", "37 file CSV trong exports/powerbi/"))
stage_df = pd.DataFrame(S, columns=["Giai đoạn", "Nội dung", "Công cụ", "Kết quả (từ etl_log)"])

# ------------------------------------------------------------------ (2) job diagram
d = Diagram("ETL jobs", 1900, 760)
d.label(20, 8, 1850, 34, f"Các job của python -m etl.run_pipeline (lô full đầu tiên, batch {first}); mỗi ô: tên job, bảng đích, số dòng chèn", font=16)
groups = [("1. Extract (staging)", GREY, jobs[jobs.layer == "staging"]), ("2. Seed + ODS", GREY, jobs[jobs.layer == "ods"]), ("3. Dimension", BLUE, jobs[(jobs.layer == "dw") & jobs.job_name.str.contains("dim")]),
          ("4. Fact", ORANGE, jobs[(jobs.layer == "dw") & ~jobs.job_name.str.contains("dim")]), ("5. Mart + kiểm thử", YELLOW, jobs[jobs.layer.isin(["mart", "test"])])]
maxh = max(60 + len(g) * 40 for _t, _c, g in groups)
d.H = 60 + maxh + 130
x = 20
frames = []
for title, color, g in groups:
    w = 345 if len(g) > 8 else 330
    h = 60 + len(g) * 40
    f = d.frame(x, 60, w, max(h, 120), f"{title} ({len(g)} job)")
    for i, r in enumerate(g.itertuples()):
        tgt = (r.target_table if isinstance(r.target_table, str) else "").split(".")[-1]
        if r.layer == "test":
            label = f"{r.job_name}\n{n(r.rows_read)} phép kiểm thử"
        elif r.layer == "mart":
            label = f"{r.job_name}\nmaterialized view: {n(r.rows_read)} dòng đọc"
        else:
            label = f"{r.job_name}\n{tgt}: " + (f"{n(r.rows_inserted)} chèn" if r.rows_inserted else f"{n(r.rows_updated)} cập nhật")
        d.box(x + 10, 96 + i * 40, w - 20, 34, label, fill=color if color != GREY else "#F3F4F6", font=9)
    frames.append(f)
    x += w + 10
for a, b in zip(frames, frames[1:]):
    d.arrow(a, b)
d.box(20, 60 + maxh + 20, 1850, 90, f"Chạy một lệnh, ghi etl_log.job_run cho từng job ({len(jobs)} job + 1 dòng tổng pipeline.full ở lô đầu); lỗi ở bất kỳ job nào thì dừng pipeline và ghi status failed. Lô đầu mất {jobs.sec.sum():.0f} giây (không tính export CSV); sau đó {nb - 1} lô tăng dần chạy cùng các job, chỉ lấy dòng mới.", fill="#FFFFFF", shape="rect", font=11, dashed=True)
d.save("etl-jobs.drawio", "3-3_etl_jobs.png")

# ------------------------------------------------------------------ (3) warehouse load results
TYPE = {"dim_date": "dimension (role-playing)", "dim_geography": "dimension (SCD1)", "dim_customer": "dimension (SCD2)", "dim_seller": "dimension (SCD1, conformed)", "dim_product": "dimension (SCD1)",
        "dim_order_status": "dimension (lookup)", "dim_payment_type": "dimension (lookup)", "dim_lead_origin": "dimension (lookup)", "dim_lead_profile": "dimension (junk)", "dim_sales_rep": "dimension (role-playing)",
        "fact_order_item": "fact giao dịch", "fact_order_fulfillment": "fact snapshot tích luỹ", "fact_payment": "fact giao dịch", "fact_review": "fact giao dịch", "fact_lead_funnel": "fact snapshot tích luỹ", "fact_seller_monthly": "fact snapshot định kỳ"}
cols = q(dw, "SELECT table_name, count(*) AS c FROM information_schema.columns WHERE table_schema='dw' AND column_name NOT IN (" + ", ".join("'%s'" % c for c in API_COLS) + ") AND table_name IN (SELECT table_name FROM information_schema.tables WHERE table_schema='dw' AND table_type='BASE TABLE') GROUP BY 1").set_index("table_name")["c"]
ctab = {t: int(q(dw, f"SELECT count(*) AS c FROM dw.{t}").iloc[0, 0]) for t in TYPE}
dqt = q(dw, """SELECT split_part(target_table, '.', 2) AS t, count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check
               WHERE """ + CORE_TEST_EDA + """ AND batch_id = (SELECT max(batch_id) FROM etl_log.dq_check) GROUP BY 1""").set_index("t")
src = lambda sql: int(q(full, sql).iloc[0, 0])
EXPECT = {  # table -> (description, expected row count from the full source, offset for Unknown row)
    "dim_date": ("1.827 ngày 2016-01-01 → 2020-12-31", 1827, 1),
    "dim_geography": ("số mã bưu chính trong geolocation ∪ customers ∪ sellers", src("""SELECT count(*) FROM (SELECT lpad(regexp_replace(geolocation_zip_code_prefix, '[^0-9]', '', 'g'), 5, '0') FROM oltp.geolocation
                                                                       UNION SELECT lpad(regexp_replace(customer_zip_code_prefix, '[^0-9]', '', 'g'), 5, '0') FROM oltp.customers
                                                                       UNION SELECT lpad(regexp_replace(seller_zip_code_prefix, '[^0-9]', '', 'g'), 5, '0') FROM oltp.sellers) t"""), 1),
    "dim_customer": ("96.096 khách thật + phiên bản khi đổi mã bưu chính", None, 1),
    "dim_seller": ("seller trong oltp ∪ crm", src("SELECT count(*) FROM (SELECT seller_id FROM oltp.sellers UNION SELECT seller_id FROM crm.closed_deals) t"), 1),
    "dim_product": ("oltp.products", src("SELECT count(*) FROM oltp.products"), 1),
    "dim_order_status": ("seed order_status", None, 1), "dim_payment_type": ("seed payment_type", None, 1), "dim_lead_origin": ("seed lead_origin_group + unknown", None, 1),
    "dim_lead_profile": ("tổ hợp 7 thuộc tính của deal", None, 1), "dim_sales_rep": ("SDR và SR trong closed_deals", None, 1),
    "fact_order_item": ("oltp.order_items", src("SELECT count(*) FROM oltp.order_items"), 0), "fact_order_fulfillment": ("oltp.orders", src("SELECT count(*) FROM oltp.orders"), 0),
    "fact_payment": ("oltp.order_payments", src("SELECT count(*) FROM oltp.order_payments"), 0), "fact_review": ("oltp.order_reviews", src("SELECT count(*) FROM oltp.order_reviews"), 0),
    "fact_lead_funnel": ("crm.mql", src("SELECT count(*) FROM crm.mql"), 0), "fact_seller_monthly": ("seller × tháng, lưới dày đặc", None, 0),
}
gmv_dw = float(q(dw, "SELECT sum(price) AS s FROM dw.fact_order_item").iloc[0, 0])
gmv_src = float(q(full, "SELECT sum(price) AS s FROM oltp.order_items").iloc[0, 0])
R = []
for t, typ in TYPE.items():
    desc, exp, off = EXPECT[t]
    rows = ctab[t]
    if exp is not None:
        ok = (rows - off) == exp
        rec = f"{desc}: {n(exp)}" + (f" (+{off} dòng Unknown)" if off else "") + (" khớp" if ok else f" LỆCH ({n(rows - off)})")
    else:
        rec = desc
    tests = f"{int(dqt.loc[t, 'ok'])}/{int(dqt.loc[t, 'total'])}" if t in dqt.index else "–"
    R.append((t, typ, int(cols[t]), n(rows), rec, tests))
res_df = pd.DataFrame(R, columns=["Bảng", "Loại", "Số cột", "Số dòng", "Đối chiếu với nguồn", "Test đạt"])
fact_note = f"Tổng price của fact_order_item: {gmv_dw:,.2f} BRL; tổng price nguồn: {gmv_src:,.2f} BRL ({'khớp từng đồng' if abs(gmv_dw - gmv_src) < 0.005 else 'LỆCH'})."

# ------------------------------------------------------------------ LaTeX
def fit(widths):
    k = (15.7 - 0.42 * len(widths)) / sum(widths)
    return "".join("p{%.2fcm}" % (w * k) for w in widths)


def tex(df, caption, label, widths, code_first=False, right=()):
    head = " & ".join("\\textbf{%s}" % esc(c) for c in df.columns) + "\\\\\\midrule"
    body = "\n".join(" & ".join(("\\code{%s}" % esc(v)) if (i == 0 and code_first) else esc(v) for i, v in enumerate(r)) + "\\\\" for r in df.itertuples(index=False))
    return f"\\begin{{table}}[htbp]\\centering\\scriptsize\\caption{{{caption}}}\\label{{{label}}}\n\\begin{{tabular}}{{{fit(widths)}}}\\toprule\n{head}\n{body}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n"


T = ROOT / "report" / "tables"
(T / "p8_etl_stages.tex").write_text(tex(stage_df, "Tóm tắt các giai đoạn ETL và kết quả (số dòng lấy từ etl\\_log)", "tab:etl-stages", [2.2, 6.0, 3.0, 5.2]), encoding="utf-8")
(T / "p8_etl_results.tex").write_text(tex(res_df, "Kết quả nạp kho dữ liệu: loại bảng, số cột, số dòng và đối chiếu với nguồn", "tab:etl-results", [3.2, 3.0, 1.0, 1.4, 5.8, 1.2], code_first=True), encoding="utf-8")

md = ["# P8-E2 – ETL: tóm tắt, job và kết quả nạp kho (số liệu từ etl_log của olist_dw)", "", "*Sinh tự động bởi `scripts/p8_etl.py`.*", "",
      "## Tóm tắt các giai đoạn", "", "| " + " | ".join(stage_df.columns) + " |", "| --- | --- | --- | --- |"]
md += ["| " + " | ".join(str(v).replace("|", "/") for v in r) + " |" for r in stage_df.itertuples(index=False)]
md += ["", f"## Job của lô full đầu tiên (batch {first})", "", "| run_id | job | lớp | bảng đích | giây | đọc | chèn | cập nhật | loại |", "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
md += [f"| {r.run_id} | {r.job_name} | {r.layer} | {r.target_table if isinstance(r.target_table, str) else ''} | {r.sec} | {n(r.rows_read)} | {n(r.rows_inserted)} | {n(r.rows_updated)} | {n(r.rows_rejected)} |" for r in jobs.itertuples()]
md += ["", "![ETL jobs](../figures/3-3_etl_jobs.png)", "", "## Kết quả nạp kho dữ liệu (trạng thái cuối)", "", "| " + " | ".join(res_df.columns) + " |", "| --- | --- | ---: | ---: | --- | --- |"]
md += ["| " + " | ".join(str(v) for v in r) + " |" for r in res_df.itertuples(index=False)]
md += ["", fact_note, ""]
(ROOT / "handoff" / "2026-11-14-P8-etl.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(stage_df[["Giai đoạn", "Kết quả (từ etl_log)"]].to_string(index=False))
print(res_df[["Bảng", "Số dòng", "Đối chiếu với nguồn", "Test đạt"]].to_string(index=False))
print(fact_note)


# ------------------------------------------------------------------ (4) P8b: ETL monitoring tables (former dashboard D7), report section 3.3
# P9: etl_log.v_run_summary mixes the core pipeline and the API step, so the per-batch figures are rebuilt from job_run.
api_jobs_sql = ", ".join("'%s'" % j for j in API_JOBS)
rs = q(dw, f"""
SELECT j.batch_id,
       coalesce(max(replace(j.job_name, 'pipeline.', '')) FILTER (WHERE j.layer = 'pipeline'), max(split_part(j.job_name, '.', 1))) AS mode,
       round(extract(epoch FROM max(j.finished_at) - min(j.started_at))::numeric, 1) AS total_sec,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'source'), 0) AS source_rows,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'staging'), 0) AS staging_rows,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'ods' AND j.job_name NOT LIKE 'seeds.%'), 0) AS ods_inserted,
       coalesce(sum(j.rows_rejected) FILTER (WHERE j.layer = 'ods'), 0) AS ods_rejected,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'dw' AND j.job_name NOT IN ({api_jobs_sql})), 0) AS dw_inserted,
       coalesce(sum(j.rows_updated) FILTER (WHERE j.layer = 'dw' AND j.job_name NOT IN ({api_jobs_sql})), 0) AS dw_updated,
       round(extract(epoch FROM max(j.finished_at) FILTER (WHERE j.layer IN ('api', 'api_ods')) - min(j.started_at) FILTER (WHERE j.layer IN ('api', 'api_ods')))::numeric, 1) AS api_stage_sec,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.job_name IN ({api_jobs_sql})), 0)::numeric, 1) AS api_enrich_sec
FROM etl_log.job_run j GROUP BY j.batch_id ORDER BY j.batch_id""")
dqs = q(dw, f"""
SELECT batch_id, count(*) FILTER (WHERE {CORE_TEST}) AS checks, count(*) FILTER (WHERE {CORE_TEST} AND passed) AS passed,
       round(100.0 * avg(passed::int) FILTER (WHERE {CORE_TEST}), 1) AS pass_pct,
       count(*) FILTER (WHERE check_name LIKE 'EDA:%') AS eda_checks, count(*) FILTER (WHERE check_name LIKE 'EDA:%' AND passed) AS eda_match,
       count(*) FILTER (WHERE {API_TEST}) AS api_checks, count(*) FILTER (WHERE {API_TEST} AND passed) AS api_passed
FROM etl_log.dq_check GROUP BY batch_id ORDER BY batch_id""")

# time of the 20 API checks: run sql/90_tests/050_api_tests.sql alone (read-only SELECT) five times on the final state, take the median
api_test_sql = (ROOT / "sql" / "90_tests" / "050_api_tests.sql").read_text(encoding="utf-8")
_t = []
for _ in range(5):
    _raw = dw.raw_connection()
    try:
        _cur = _raw.cursor()
        _t0 = time.perf_counter()
        _cur.execute(api_test_sql)
        _cur.fetchall()
        _t.append(time.perf_counter() - _t0)
    finally:
        _raw.close()
api_test_sec = sorted(_t)[len(_t) // 2]
rs = rs.merge(dqs[["batch_id", "api_checks"]], on="batch_id", how="left").fillna({"api_checks": 0})
rs["api_test_sec"] = rs["api_checks"].map(lambda c: round(api_test_sec, 1) if c > 0 else 0.0)
rs["api_stage_sec"] = rs["api_stage_sec"].fillna(0.0).astype(float)
rs["api_sec"] = (rs["api_stage_sec"] + rs["api_enrich_sec"].astype(float) + rs["api_test_sec"]).round(1)
rs["duration_sec"] = (rs["total_sec"].astype(float) - rs["api_sec"]).round(1)           # core pipeline only
bm = q(dw, "SELECT * FROM etl_log.batch_metrics ORDER BY batch_id").set_index("batch_id")
rej = q(dw, "SELECT job_name, source_table, reason, sum(row_count) AS n FROM etl_log.v_rejected_summary WHERE job_name NOT LIKE 'api.%' AND job_name NOT LIKE 'ods.load_api%' GROUP BY 1, 2, 3 ORDER BY n DESC")
iss = q(dw, "SELECT fact_table, detail, CASE WHEN fact_table = 'fact_lead_funnel' THEN max(row_count) ELSE sum(row_count) END AS n FROM etl_log.fact_load_issue GROUP BY fact_table, detail ORDER BY n DESC")
orph = q(dw, "SELECT count(*) AS c FROM etl_log.rejected_rows WHERE reason LIKE 'orphan%'").iloc[0, 0]

# (a) rows through each layer, all batches
src_rows = rs.loc[rs["mode"].isin(["load_source", "simulate_increment"]), "source_rows"].sum()
tot_stg, tot_ods, tot_rej, tot_dwi, tot_dwu = (rs[c].sum() for c in ["staging_rows", "ods_inserted", "ods_rejected", "dw_inserted", "dw_updated"])
layer_df = pd.DataFrame([
    ("Nguồn (oltp, crm)", n(src_rows), "dòng đã nạp hoặc mô phỏng vào hai hệ thống nguồn qua mọi đợt"),
    ("Staging", n(tot_stg), "dòng chép vào staging (extract); bằng số dòng nguồn"),
    ("ODS", n(tot_ods), f"dòng vào ODS (không tính các bảng seed nạp lại mỗi lô; bảng toạ độ đã gom về mã bưu chính); {n(tot_rej)} dòng bị loại"),
    ("Kho dw", n(tot_dwi), f"dòng chèn vào dimension và fact; {n(tot_dwu)} dòng cập nhật (snapshot tích luỹ, ngày bán đầu tiên của seller)"),
], columns=["Lớp", "Số dòng", "Ghi chú"])

# (b) rejected rows by reason
rej_rows = [(r.job_name, r.source_table, r.reason, n(r.n)) for r in rej.itertuples()] or [("–", "–", "không có dòng bị loại", "0")]
rej_df = pd.DataFrame(rej_rows, columns=["Job", "Bảng nguồn", "Lý do", "Số dòng"])
iss_df = pd.DataFrame([(r.fact_table, r.detail, n(r.n)) for r in iss.itertuples()], columns=["Fact", "Vấn đề ghi nhận", "Số dòng"])

# (c) batch table: full + incremental batches that carried data
bt = rs[rs["mode"].isin(["full", "incremental"]) & (rs["staging_rows"] > 0)].copy()
bt = bt.merge(dqs[["batch_id", "checks", "passed"]], on="batch_id", how="left")
bt["tests"] = bt.apply(lambda r: f"{int(r.passed)}/{int(r.checks)}" if pd.notna(r.checks) else "–", axis=1)
bt = bt.reset_index(drop=True)
bt["stt"] = ["đầu" if m == "full" else str(i) for i, m in enumerate(bt["mode"], 0)]
batch_df = pd.DataFrame({
    "Đợt": bt["stt"], "Lô": bt["batch_id"].astype(int), "Dòng mới vào staging": bt["staging_rows"].map(n), "Dòng bị loại": bt["ods_rejected"].map(n),
    "Dòng chèn vào kho": bt["dw_inserted"].map(n), "Thời gian (giây)": bt["duration_sec"].map(lambda x: f"{x:.1f}".replace(".", ",")), "Test đạt": bt["tests"],
    "MQL": bt["batch_id"].map(lambda b: n(bm.loc[b, "mql"]) if b in bm.index else "–"), "Deal": bt["batch_id"].map(lambda b: n(bm.loc[b, "deals_won"]) if b in bm.index else "–"),
    "Seller có đơn": bt["batch_id"].map(lambda b: n(bm.loc[b, "sellers_with_sale"]) if b in bm.index else "–"),
})
inc = bt[bt["mode"] == "incremental"]
n_inc = len(inc)
t_min, t_avg, t_max = inc["duration_sec"].min(), inc["duration_sec"].mean(), inc["duration_sec"].max()
last = dqs.iloc[-1]
split = rs[rs["mode"].isin(["full", "incremental"]) & (rs["staging_rows"] > 0)]


def tex_simple(df, caption, label, widths, size="scriptsize"):
    head = " & ".join("\\textbf{%s}" % esc(c) for c in df.columns) + "\\\\\\midrule"
    body = "\n".join(" & ".join(esc(v) for v in r) + "\\\\" for r in df.itertuples(index=False))
    return f"\\begin{{table}}[htbp]\\centering\\{size}\\caption{{{caption}}}\\label{{{label}}}\n\\begin{{tabular}}{{{fit(widths)}}}\\toprule\n{head}\n{body}\n\\bottomrule\\end{{tabular}}\\end{{table}}\n"


(T / "p8b_etl_layers.tex").write_text(tex_simple(layer_df, "Số dòng đi qua từng lớp trong mọi đợt nạp (từ etl\\_log)", "tab:etl-layers", [3.0, 2.4, 10.0]), encoding="utf-8")
(T / "p8b_etl_rejected.tex").write_text(tex_simple(rej_df, "Dòng bị loại theo lý do (etl\\_log.rejected\\_rows)", "tab:etl-rejected", [4.0, 4.0, 5.5, 1.8]) + "\n" +
                                       tex_simple(iss_df, "Vấn đề ghi nhận khi nạp fact (etl\\_log.fact\\_load\\_issue; dòng không bị xoá)", "tab:etl-issues", [3.5, 8.8, 2.0]), encoding="utf-8")
(T / "p8b_etl_batches.tex").write_text(tex_simple(batch_df, "Các đợt nạp: lô đầu (đến 31/12/2017) và %d đợt tăng dần hằng tháng" % n_inc, "tab:etl-batches", [0.9, 0.9, 1.6, 1.1, 1.5, 1.4, 1.2, 1.0, 0.9, 1.3], size="tiny"), encoding="utf-8")

mon = {"layer": layer_df, "rej": rej_df, "iss": iss_df, "batch": batch_df}
md2 = ["", "## Giám sát ETL (trước đây là dashboard D7; P8b chuyển thành bảng ở mục 3.3 của báo cáo)", "", "### Số dòng qua từng lớp", "", md_tbl := "\n".join(["| " + " | ".join(layer_df.columns) + " |", "| --- | ---: | --- |"] + ["| " + " | ".join(r) + " |" for r in layer_df.itertuples(index=False)]),
       "", "### Dòng bị loại theo lý do", "", "\n".join(["| " + " | ".join(rej_df.columns) + " |", "| --- | --- | --- | ---: |"] + ["| " + " | ".join(r) + " |" for r in rej_df.itertuples(index=False)]),
       "", f"Dòng mồ côi (`orphan:`) trong `rejected_rows`: {orph}.", "", "\n".join(["| " + " | ".join(iss_df.columns) + " |", "| --- | --- | ---: |"] + ["| " + " | ".join(r) + " |" for r in iss_df.itertuples(index=False)]),
       "", "### Các đợt nạp", "", "\n".join(["| " + " | ".join(batch_df.columns) + " |", "| " + " | ".join("---" for _ in batch_df.columns) + " |"] + ["| " + " | ".join(map(str, r)) + " |" for r in batch_df.itertuples(index=False)]),
       "", f"- {n_inc} đợt tăng dần: thời gian nhỏ nhất {t_min:.1f}, trung bình {t_avg:.1f}, lớn nhất {t_max:.1f} giây; lô kiểm thử cuối: {int(last.passed)}/{int(last.checks)} phép đạt ({last.pass_pct}%), đối chiếu EDA {int(last.eda_match)}/{int(last.eda_checks)}."]
with open(ROOT / "handoff" / "2026-11-14-P8-etl.md", "a", encoding="utf-8") as fh:
    fh.write("\n".join(md2) + "\n")
# ------------------------------------------------------------------ core / API split (handoff only; the report tables above are core only)
sp = split.copy().reset_index(drop=True)
sp["stt"] = ["đầu" if m == "full" else str(i) for i, m in enumerate(sp["mode"], 0)]
fmt = lambda x: f"{float(x):.1f}".replace(".", ",")
inc_sp = sp[sp["mode"] == "incremental"]
core_tests = int(dqs.iloc[-1].checks)
api_tests = int(dqs.iloc[-1].api_checks)
md3 = ["", "## Tách thời gian: pipeline lõi và bước API (P9)", "",
       "Từ P9 mỗi lô còn chạy thêm bước API (mục 5.2 của báo cáo). Bảng ở mục 3.3 chỉ tính phần lõi; phần API tách riêng như sau (giây, từ `etl_log.job_run`).", "",
       "- **Bước API** = cửa sổ thời gian của các job lớp `api` và `api_ods` (thu nhận, staging, ODS, ghép đô thị) + ba job làm giàu `dw.enrich_dim_geography`, `dw.enrich_dim_date`, `dw.load_fact_state_year` + thời gian chạy 20 phép kiểm thử API.",
       f"- 20 phép kiểm thử API (`sql/90_tests/050_api_tests.sql`) không ghi thời gian riêng; thời gian chạy riêng tệp này (trung vị 5 lần, trạng thái cuối) là {api_test_sec:.1f} giây, dùng chung cho mọi lô.",
       "- **Lõi** = tổng thời gian lô − bước API. Số dòng chèn vào kho ở cột \"Dòng chèn vào kho\" của bảng trên không tính 81 dòng `fact_state_year` và các dòng làm giàu.", "",
       "| Đợt | Lô | Tổng (giây) | API: thu nhận + ODS + ghép | API: làm giàu dim/fact | API: test | Bước API (giây) | Lõi (giây) |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
md3 += [f"| {r.stt} | {int(r.batch_id)} | {fmt(r.total_sec)} | {fmt(r.api_stage_sec)} | {fmt(r.api_enrich_sec)} | {fmt(r.api_test_sec)} | {fmt(r.api_sec)} | {fmt(r.duration_sec)} |" for r in sp.itertuples()]
md3 += ["", f"- {len(inc_sp)} đợt tăng dần, tổng thời gian có API: {inc_sp.total_sec.astype(float).min():.1f} / {inc_sp.total_sec.astype(float).mean():.1f} / {inc_sp.total_sec.astype(float).max():.1f} giây (nhỏ nhất / trung bình / lớn nhất).",
        f"- Chỉ phần lõi: {inc_sp.duration_sec.min():.1f} / {inc_sp.duration_sec.mean():.1f} / {inc_sp.duration_sec.max():.1f} giây; bước API: {inc_sp.api_sec.min():.1f} / {inc_sp.api_sec.mean():.1f} / {inc_sp.api_sec.max():.1f} giây.",
        f"- Lô đầu (full): có API {fmt(sp.iloc[0].total_sec)} giây, lõi {fmt(sp.iloc[0].duration_sec)} giây.",
        f"- Kiểm thử ở lô cuối: {core_tests} phép của kho (đạt {int(dqs.iloc[-1].passed)}) + {api_tests} phép của API (đạt {int(dqs.iloc[-1].api_passed)}) = {core_tests + api_tests}; chưa tính {int(dqs.iloc[-1].eda_checks)} phép đối chiếu EDA."]
with open(ROOT / "handoff" / "2026-11-14-P8-etl.md", "a", encoding="utf-8") as fh:
    fh.write(chr(10).join(md3) + chr(10))
print("monitor tables written;", n_inc, "incremental batches; time min/avg/max", round(t_min, 1), round(t_avg, 1), round(t_max, 1))
print(layer_df.to_string(index=False)); print(rej_df.to_string(index=False)); print(iss_df.to_string(index=False)); print(batch_df.to_string(index=False))

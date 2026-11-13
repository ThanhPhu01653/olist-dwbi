"""P8-E2: ETL summary from etl_log.job_run (olist_dw):
  (1) stage table: stage -> content -> tool -> result (rows from etl_log, first full batch and total after all batches)
  (2) job diagram of run_pipeline (job name, order, table out and rows) generated from job_run of the first full batch -> docs/diagrams/etl-jobs.drawio + figures/3-3_etl_jobs.png
  (3) warehouse load result table: table, type, columns, rows, reconciliation against the source (olist_full) and dq_check results
-> report/tables/p8_etl_stages.tex, p8_etl_results.tex, handoff/2026-11-14-P8-etl.md.   python scripts/p8_etl.py
"""
from __future__ import annotations

import sys
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
                FROM etl_log.job_run WHERE batch_id = :b AND job_name <> 'pipeline.full' ORDER BY run_id""", b=first)
tot = q(dw, """SELECT layer, count(*) AS runs, sum(rows_read) AS rd, sum(rows_inserted) AS ins, sum(rows_updated) AS upd, sum(rows_rejected) AS rej
               FROM etl_log.job_run WHERE job_name NOT LIKE 'pipeline.%' GROUP BY 1""").set_index("layer")
first_l = jobs.groupby("layer").agg(runs=("run_id", "count"), rd=("rows_read", "sum"), ins=("rows_inserted", "sum"), rej=("rows_rejected", "sum"), sec=("sec", "sum"))
dq = q(dw, "SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check WHERE batch_id = (SELECT max(batch_id) FROM etl_log.dq_check)").iloc[0]
dq_first = q(dw, "SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check WHERE batch_id = :b", b=first).iloc[0]

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
cols = q(dw, "SELECT table_name, count(*) AS c FROM information_schema.columns WHERE table_schema='dw' AND table_name IN (SELECT table_name FROM information_schema.tables WHERE table_schema='dw' AND table_type='BASE TABLE') GROUP BY 1").set_index("table_name")["c"]
ctab = {t: int(q(dw, f"SELECT count(*) AS c FROM dw.{t}").iloc[0, 0]) for t in TYPE}
dqt = q(dw, """SELECT split_part(target_table, '.', 2) AS t, count(*) AS total, count(*) FILTER (WHERE passed) AS ok FROM etl_log.dq_check
               WHERE batch_id = (SELECT max(batch_id) FROM etl_log.dq_check) GROUP BY 1""").set_index("t")
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
rs = q(dw, "SELECT * FROM etl_log.v_run_summary ORDER BY batch_id")
dqs = q(dw, "SELECT * FROM etl_log.v_dq_summary ORDER BY batch_id")
bm = q(dw, "SELECT * FROM etl_log.batch_metrics ORDER BY batch_id").set_index("batch_id")
rej = q(dw, "SELECT job_name, source_table, reason, sum(row_count) AS n FROM etl_log.v_rejected_summary GROUP BY 1, 2, 3 ORDER BY n DESC")
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
print("monitor tables written;", n_inc, "incremental batches; time min/avg/max", round(t_min, 1), round(t_avg, 1), round(t_max, 1))
print(layer_df.to_string(index=False)); print(rej_df.to_string(index=False)); print(iss_df.to_string(index=False)); print(batch_df.to_string(index=False))

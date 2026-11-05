"""Generate the data-driven parts of the LaTeX report from olist_dw:   python scripts/export_latex.py

  report/tables/*.tex   complete table floats (caption + label) with the real numbers -> \\input{tables/<name>} in the chapters
  report/code/*.sql     SQL snippets cut from sql/ (ODS, SCD2, accumulating snapshot, OLAP) for the appendix
  report/tables/dax.tex the DAX library from powerbi/measures.md
Safe to re-run whenever the data change; it never touches report/chapters/ (the text written by the team).
"""
from __future__ import annotations

import csv
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine
from etl.load_source import SPECS

TAB = ROOT / "report" / "tables"
CODE = ROOT / "report" / "code"


def esc(s) -> str:
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def num(v, d: int = 0) -> str:
    """Vietnamese number format: 1.234.567,89"""
    if v is None:
        return "--"
    v = float(v)
    s = f"{v:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def table(name: str, caption: str, label: str, header: list[str], rows: list[list], colspec: str, note: str = "", small: bool = True) -> None:
    lines = ["\\begin{table}[htbp]", "\\centering" + ("\\small" if small else ""), f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule",
             " & ".join(f"\\textbf{{{esc(h)}}}" for h in header) + " \\\\", "\\midrule"]
    lines += [" & ".join(c if isinstance(c, str) and c.startswith("\\raw:") is False and False else esc(c) for c in r) + " \\\\" for r in rows]
    lines += ["\\bottomrule", "\\end{tabular}"]
    if note:
        lines += ["\\\\[2pt]{\\footnotesize " + note + "}"]
    lines += ["\\end{table}", ""]
    (TAB / f"{name}.tex").write_text("\n".join(lines), encoding="utf-8")
    print("  tables/" + name + ".tex")


def longtable(name: str, caption: str, label: str, header: list[str], rows: list[list], colspec: str) -> None:
    head = " & ".join(f"\\textbf{{{esc(h)}}}" for h in header) + " \\\\"
    lines = [f"{{\\small\\begin{{longtable}}{{{colspec}}}", f"\\caption{{{caption}}}\\label{{{label}}}\\\\", "\\toprule", head, "\\midrule", "\\endfirsthead",
             "\\toprule", head, "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    lines += [" & ".join(esc(c) for c in r) + " \\\\" for r in rows]
    lines += ["\\end{longtable}}", ""]
    (TAB / f"{name}.tex").write_text("\n".join(lines), encoding="utf-8")
    print("  tables/" + name + ".tex")


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def q(conn, sql, **p):
    return conn.execute(text(sql), p).fetchall()


GRAIN = {
    "dim_date": ("1 ngày (2016-01-01 → 2020-12-31)", "--"), "dim_geography": ("1 mã bưu chính (zip)", "1"), "dim_customer": ("1 phiên bản địa chỉ của 1 khách thật", "2"),
    "dim_seller": ("1 seller (chiều dùng chung)", "1"), "dim_product": ("1 sản phẩm", "1"), "dim_order_status": ("1 trạng thái đơn", "1"), "dim_payment_type": ("1 hình thức thanh toán", "1"),
    "dim_lead_origin": ("1 giá trị origin của MQL", "1"), "dim_lead_profile": ("1 tổ hợp thuộc tính deal (junk dimension)", "--"), "dim_sales_rep": ("1 nhân viên và vai trò (SDR/SR)", "--"),
}
FACTS = {
    "fact_order_item": ("Transaction", "1 dòng hàng của 1 đơn", "price, freight\\_value, item\\_total"), "fact_order_fulfillment": ("Accumulating snapshot", "1 đơn (5 mốc thời gian)", "approval\\_hours, handling\\_days, transit\\_days, lead\\_days, delay\\_days, promised\\_days"),
    "fact_payment": ("Transaction", "1 lần thanh toán", "payment\\_value, payment\\_installments"), "fact_review": ("Transaction", "1 review của 1 đơn", "review\\_score, is\\_negative, response\\_hours"),
    "fact_lead_funnel": ("Accumulating snapshot", "1 MQL", "is\\_won, days\\_to\\_close, seller\\_gmv\\_first\\_90d"), "fact_seller_monthly": ("Periodic snapshot (dày đặc)", "1 seller × 1 tháng", "orders, gmv, late\\_rate, avg\\_review\\_score"),
}
FLAG_TXT = {
    "carrier_before_approved": "Bàn giao vận chuyển trước khi duyệt thanh toán", "carrier_before_purchase": "Bàn giao vận chuyển trước ngày mua", "delivered_before_carrier": "Giao khách trước khi bàn giao vận chuyển",
    "delivered_without_approval": "Đơn đã giao nhưng không có ngày duyệt", "delivered_without_date": "Trạng thái delivered nhưng không có ngày giao", "delivery_date_but_not_delivered": "Có ngày giao nhưng trạng thái chưa là delivered",
    "approved_before_purchase": "Duyệt trước ngày mua", "delivered_before_purchase": "Giao trước ngày mua", "estimated_before_purchase": "Ngày dự kiến trước ngày mua", "delivered_without_carrier_date": "Đã giao nhưng không có ngày bàn giao",
    "installments_zero_set_to_1": "Số kỳ trả góp = 0 (đặt thành 1)", "payment_type_not_defined": "Hình thức thanh toán not\\_defined", "payment_value_zero": "Giá trị thanh toán = 0",
    "declared_revenue_zero": "Doanh thu tháng khai báo = 0", "declared_catalog_zero": "Số sản phẩm khai báo = 0", "won_before_first_contact": "Chốt deal trước ngày liên hệ đầu",
}


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    CODE.mkdir(parents=True, exist_ok=True)
    gp = load("scripts/gen_powerbi_docs.py", "gen_powerbi_docs")
    with get_engine(config.DB_NAME).connect() as c:
        # 1. source tables
        rows = []
        for s in SPECS:
            sch, name = s.table.split(".")
            n = q(c, f"SELECT count(*) FROM {s.table}")[0][0]
            cols = q(c, "SELECT count(*) FROM information_schema.columns WHERE table_schema = :s AND table_name = :t", s=sch, t=name)[0][0]
            rows.append([f"{s.table}", s.path.name, num(n), str(cols), num(s.path.stat().st_size / 1024 / 1024, 2)])
        tot = sum(int(r[2].replace(".", "")) for r in rows)
        rows.append(["Tổng (11 bảng)", "", num(tot), "", num(sum(float(r[4].replace(",", ".")) for r in rows), 2)])
        table("src_tables", "Hai hệ thống nguồn: số bảng ghi, số cột và dung lượng file CSV", "tab:src-tables", ["Bảng nguồn", "File CSV", "Số dòng", "Số cột", "MB"], rows, "llrrr")

        # 2. layers
        lay = []
        for sch, desc in [("oltp", "Nguồn bán hàng"), ("crm", "Nguồn marketing"), ("staging", "Staging"), ("ods", "ODS"), ("dw", "Kho (dimension + fact)"), ("etl_log", "Giám sát ETL")]:
            tabs = q(c, "SELECT table_name FROM information_schema.tables WHERE table_schema = :s AND table_type = 'BASE TABLE'", s=sch)
            n = sum(q(c, f'SELECT count(*) FROM {sch}."{t[0]}"')[0][0] for t in tabs)
            lay.append([desc, sch, str(len(tabs)), num(n)])
        nv = q(c, "SELECT (SELECT count(*) FROM pg_views WHERE schemaname LIKE 'mart\\_%'), (SELECT count(*) FROM pg_matviews WHERE schemaname LIKE 'mart\\_%')")[0]
        lay.append(["Data mart (view và materialized view)", "mart\\_*".replace("\\", ""), f"{nv[0] + nv[1]} view", "--"])
        table("layers", "Số bảng và số dòng của từng lớp trong kho dữ liệu (trạng thái cuối)", "tab:layers", ["Lớp", "Schema", "Số bảng", "Số dòng"], lay, "llrr")

        # 3. dims and facts
        rows = []
        for d, (grain, scd) in GRAIN.items():
            rows.append([d, grain, num(q(c, f"SELECT count(*) FROM dw.{d}")[0][0]), scd])
        table("dims", "Các bảng chiều: grain, số dòng (gồm dòng Unknown $-1$) và loại SCD", "tab:dims", ["Chiều", "Grain", "Số dòng", "SCD"], rows, "llrc")
        rows = []
        for f, (kind, grain, meas) in FACTS.items():
            rows.append([f, kind, grain, num(q(c, f"SELECT count(*) FROM dw.{f}")[0][0])])
        table("facts", "Các bảng fact: loại, grain và số dòng", "tab:facts", ["Fact", "Loại", "Grain", "Số dòng"], rows, "lllr")

        # 4. data quality
        rows = []
        for fl, n in q(c, "SELECT f, count(*) FROM ods.orders, unnest(dq_flags) f GROUP BY 1 ORDER BY 2 DESC"):
            rows.append([FLAG_TXT.get(fl, fl).replace("\\_", "_"), num(n), "Gắn cờ dq_flags, giữ đơn; khoảng thời gian âm đặt NULL"])
        for fl, n in q(c, "SELECT f, count(*) FROM ods.order_payments, unnest(dq_flags) f GROUP BY 1 ORDER BY 2 DESC"):
            rows.append([FLAG_TXT.get(fl, fl).replace("\\_", "_"), num(n), "Gắn cờ, chuẩn hoá (số kỳ 0 → 1)"])
        for fl, n in q(c, "SELECT f, count(*) FROM ods.closed_deals, unnest(dq_flags) f GROUP BY 1 ORDER BY 2 DESC"):
            rows.append([FLAG_TXT.get(fl, fl).replace("\\_", "_"), num(n), "Gắn cờ, giữ nguyên giá trị"])
        for reason, n in q(c, "SELECT reason, sum(row_count) FROM etl_log.v_rejected_summary GROUP BY 1 ORDER BY 2 DESC"):
            rows.append([reason, num(n), "Loại khỏi ODS, ghi etl_log.rejected_rows"])
        table("dq_errors", "Lỗi dữ liệu nguồn được phát hiện khi làm sạch và cách xử lý (số dòng ở trạng thái cuối)", "tab:dq-errors", ["Lỗi", "Số dòng", "Xử lý"], rows, "p{6.2cm}rp{5.5cm}",
              note="Cờ chất lượng gắn trên đơn, thanh toán và deal; mỗi dòng có thể có nhiều cờ.")

        # 5. KPI
        k0, k1 = gp.kpis(c, None, None), gp.kpis(c, "2017-01", "2018-08")
        show = ["GMV", "Orders", "AOV", "Freight ratio", "Orders placed", "Cancel rate", "On-time rate", "Avg lead days", "Avg promised days", "Promised vs actual (days)", "Avg review", "% negative",
                "Repeat customer rate", "MQLs (theo tháng liên hệ đầu)", "Won deals", "MQL to won rate", "Avg days to close", "Sellers with first sale", "Won to first sale rate"]
        rows = []
        for k in show:
            (v0, kind), (v1, _) = k0[k], k1[k]
            f = lambda v: "--" if v is None else (num(v, 2) if kind in ("money", "d1", "d2") else num(v, 0) if kind == "int" else num(100 * float(v), 1 if kind == "pct1" else 2) + "\\%")
            rows.append([k, f(v0).replace("\\%", "%"), f(v1).replace("\\%", "%")])
        table("kpi", "Các chỉ số KPI chính (tính bằng SQL trên kho; đối chiếu với Power BI)", "tab:kpi", ["KPI", "Toàn bộ dữ liệu", "Cửa sổ 2017-01 → 2018-08"], rows, "lrr",
              note="GMV chỉ tính đơn không thuộc nhóm Failed (hủy / không khả dụng); tổng giá hàng mọi đơn là 13.591.643,70 BRL.")

        # 6. increments
        inc = q(c, """
            WITH sim AS (SELECT batch_id sb, sum(rows_inserted) src_rows FROM etl_log.job_run WHERE job_name LIKE 'simulate_increment.%' GROUP BY batch_id),
            pb AS (SELECT s.sb, s.src_rows, (SELECT min(batch_id) FROM etl_log.v_run_summary r WHERE r.mode = 'incremental' AND r.batch_id > s.sb AND r.staging_rows > 0) AS pbid FROM sim s)
            SELECT row_number() OVER (ORDER BY pb.sb), pb.src_rows, r.ods_inserted, r.ods_rejected, r.dw_inserted, r.dw_updated, r.duration_sec, m.mql, m.deals_won, m.sellers_with_sale, m.orders
            FROM pb JOIN etl_log.v_run_summary r ON r.batch_id = pb.pbid JOIN etl_log.batch_metrics m ON m.batch_id = pb.pbid ORDER BY pb.sb""")
        months = ["2018-01", "2018-02", "2018-03", "2018-04", "2018-05", "2018-06", "2018-07", "2018-08", "2018-09", "2018-10", "2018-11"]
        rows = [[str(r[0]), months[r[0] - 1] if r[0] <= 11 else "", num(r[1]), num(r[2]), num(r[3]), num(r[4]) + " / " + num(r[5]), num(r[6], 1), num(r[7]), num(r[8]), num(r[9]), num(r[10])] for r in inc]
        table("increments", "Các đợt nạp tăng dần: bản ghi mới, thời gian chạy (gồm kiểm thử) và funnel “lấp đầy dần”", "tab:increments",
              ["Đợt", "Đến tháng", "Bản ghi mới ở nguồn", "ODS chèn", "ODS loại", "DW chèn / cập nhật", "Giây", "MQL", "Deal", "Seller có đơn", "Đơn"], rows, "clrrrrrrrrr")

        # 7. distance bands and review vs delay
        rows = []
        for r in q(c, """SELECT distance_band, count(*), avg(freight_value), avg(freight_ratio), avg(lead_days) FILTER (WHERE is_delivered = 1), 100.0 * avg(is_late) FILTER (WHERE is_delivered = 1)
                         FROM mart_fulfillment.v_shipping_distance WHERE has_distance AND status_group <> 'Failed' GROUP BY distance_band, distance_band_no ORDER BY distance_band_no"""):
            rows.append([r[0], num(r[1]), num(r[2], 2), num(100 * r[3], 1) + "%", num(r[4], 1), num(r[5], 1) + "%"])
        table("distance", "Khoảng cách seller → khách (haversine) với phí vận chuyển, lead time và tỷ lệ trễ", "tab:distance", ["Nhóm khoảng cách", "Dòng hàng", "Freight TB (BRL)", "Freight / giá", "Lead time TB (ngày)", "Tỷ lệ trễ"], rows, "lrrrrr")
        rows = [[r[0], num(r[1]), num(r[2], 2), num(r[3], 1) + "%"] for r in q(c, """SELECT delay_bucket, sum(reviews), sum(score_sum)::numeric / sum(reviews), 100.0 * sum(negative_reviews) / sum(reviews)
                                                                                     FROM mart_cx.v_review_vs_delay GROUP BY delay_bucket, delay_bucket_no ORDER BY delay_bucket_no""")]
        table("review_delay", "Điểm review theo mức trễ giao hàng (chỉ đơn đã giao)", "tab:review-delay", ["Nhóm trễ", "Số review", "Điểm TB", "% tiêu cực"], rows, "lrrr")

        # 8. funnel by channel
        rows = [[r[0], num(r[1]), num(r[2]), num(r[3], 1) + "%", num(r[4], 1)] for r in q(c, """SELECT lo.channel_group, count(*), sum(is_won), 100.0 * sum(is_won) / count(*), avg(days_to_close)
                                                                                                   FROM dw.fact_lead_funnel f JOIN dw.dim_lead_origin lo USING (lead_origin_key) GROUP BY 1 ORDER BY 2 DESC""")]
        table("funnel_channel", "Funnel MQL → deal đã chốt theo nhóm kênh thu hút", "tab:funnel-channel", ["Nhóm kênh", "MQL", "Đã chốt", "Tỷ lệ chốt", "Ngày chốt TB"], rows, "lrrrr")
        rows = [[r[0], num(r[1]), num(r[2]), num(r[3]), num(r[4], 2) if r[4] is not None else "--", ("mẫu nhỏ" if r[5] else "")]
                for r in q(c, "SELECT acquisition_channel, sellers, selling_sellers, gmv, gmv_per_selling_seller, small_sample FROM mart_acquisition.v_seller_by_channel ORDER BY gmv DESC")]
        table("seller_channel", "Seller và GMV theo kênh thu hút (kênh có dưới 30 seller có đơn được đánh dấu mẫu nhỏ)", "tab:seller-channel", ["Kênh", "Seller", "Seller có đơn", "GMV (BRL)", "GMV / seller có đơn", "Cỡ mẫu"], rows, "lrrrrl")

        # 9. marts
        rows = []
        for sch, nm, kind in q(c, "SELECT schemaname, viewname, 'view' FROM pg_views WHERE schemaname LIKE 'mart\\_%' UNION ALL SELECT schemaname, matviewname, 'materialized' FROM pg_matviews WHERE schemaname LIKE 'mart\\_%' ORDER BY 1, 2"):
            n = q(c, f"SELECT count(*) FROM {sch}.{nm}")[0][0]
            cm = q(c, "SELECT obj_description(CAST(:r AS regclass), 'pg_class')", r=f"{sch}.{nm}")[0][0] or ""
            rows.append([sch, nm, kind, num(n), cm])
        longtable("marts", "Các data mart: view, loại, số dòng và mô tả", "tab:marts", ["Mart", "View", "Loại", "Dòng", "Mô tả"], rows, "llllp{6.3cm}")

        # 10. OLAP samples
        rows = [[a, b, num(o), num(g, 2)] for a, b, o, g in q(c, """SELECT CASE WHEN GROUPING(d.year) = 1 THEN 'Tổng' ELSE d.year::text END, CASE WHEN GROUPING(d.year_quarter) = 1 THEN '(cả năm)' ELSE d.year_quarter END,
                                                                   count(DISTINCT f.order_id), sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
                                                                   JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed' WHERE d.year IN (2017, 2018)
                                                                   GROUP BY ROLLUP (d.year, d.year_quarter) ORDER BY GROUPING(d.year), d.year, GROUPING(d.year_quarter), d.year_quarter""")]
        table("olap_rollup", "Roll-up bằng ROLLUP: GMV theo quý, năm và tổng", "tab:olap-rollup", ["Năm", "Quý", "Số đơn", "GMV (BRL)"], rows, "llrr")
        rows = [[r[0]] + [num(x, 0) for x in r[1:]] for r in q(c, """SELECT g.region, coalesce(sum(f.price) FILTER (WHERE d.year = 2016), 0), coalesce(sum(f.price) FILTER (WHERE d.year = 2017), 0),
                                                                 coalesce(sum(f.price) FILTER (WHERE d.year = 2018), 0), sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
                                                                 JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
                                                                 GROUP BY g.region ORDER BY 5 DESC""")]
        table("olap_pivot", "Pivot bằng FILTER: GMV (BRL) theo vùng × năm", "tab:olap-pivot", ["Vùng", "2016", "2017", "2018", "Tổng"], rows, "lrrrr")

    # 11. benchmark (parse handoff/benchmark.md)
    md = (ROOT / "handoff" / "benchmark.md").read_text(encoding="utf-8")
    t = [[c.strip() for c in l.strip("|").split("|")] for l in md.splitlines() if re.match(r"\| Q\d", l)]
    by = {}
    for i, r in enumerate(t):
        by.setdefault(r[0], {})[i // 4] = r      # three tables x 4 queries (the third has 3 rows)
    keys = list(dict.fromkeys(r[0] for r in t))
    rows = []
    for k in keys:
        d = by[k]
        rows.append([k, d[0][1], d[0][2], d[1][2], d[2][1] if 2 in d else "--", d[2][2] if 2 in d else "--"])
    table("benchmark", "Thời gian thực thi trung bình của 4 truy vấn (mili giây, trung bình 5 lần EXPLAIN ANALYZE)", "tab:benchmark",
          ["Truy vấn", "oltp (chuẩn hoá)", "dw (star, có index FK)", "dw không index FK", "View thường", "Materialized view"], rows, "p{4.6cm}rrrrr")

    # 12. rebuild report
    md = (ROOT / "handoff" / "rebuild-report.md").read_text(encoding="utf-8")
    rows = [[x.strip() for x in l.strip("|").split("|")][:2] + [[x.strip() for x in l.strip("|").split("|")][2][:90]] for l in md.splitlines() if l.startswith("| ") and not l.startswith("| Bước") and not l.startswith("| ---")]
    table("rebuild", "Dựng lại toàn bộ dự án từ đầu bằng một lệnh (kiểm chứng tái lập)", "tab:rebuild", ["Bước", "Giây", "Kết quả"], rows, "p{6cm}rp{6cm}")

    # 13. mapping (ods -> dw)
    with open(ROOT / "docs" / "mapping.csv", encoding="utf-8-sig") as f:
        rd = [r for r in csv.DictReader(f) if r["layer"] == "ods → dw"]
    longtable("mapping", "Ánh xạ ODS → kho (cột đích, nguồn, phép biến đổi)", "tab:mapping", ["Bảng đích", "Cột đích", "Nguồn", "Phép biến đổi"],
              [[r["target_table"].replace("dw.", ""), r["target_column"], r["source_table"] + ": " + r["source_column"], r["transformation"]] for r in rd], "p{2.4cm}p{3.1cm}p{3.6cm}p{5.4cm}")

    # 14. DAX library
    txt = (ROOT / "powerbi" / "measures.md").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"### (.+?)\n```dax\n(.*?)```\n(.*?)\n", txt, re.S):
        title, code, desc = m.group(1).strip(), m.group(2).rstrip(), m.group(3).strip()
        out += [f"\\subsection*{{{esc(title)}}}", "\\begin{lstlisting}[language={}]", code, "\\end{lstlisting}", esc(re.sub(r"[`*]", "", desc)) if desc and not desc.startswith("```") else "", ""]
    (TAB / "dax.tex").write_text("\n".join(out), encoding="utf-8")
    print("  tables/dax.tex:", len(re.findall(r"\\subsection\*", "\n".join(out))), "measures")

    # 15. SQL snippets
    def cut(path: str, start: str, name: str, max_lines: int = 0) -> None:
        s = (ROOT / path).read_text(encoding="utf-8")
        i = s.index(start)
        j = s.index("END $$;", i) + len("END $$;")
        lines = s[i:j].splitlines()
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines] + ["    -- ... (rút gọn, xem file nguồn)", "END $$;"]
        (CODE / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("  code/" + name)

    cut("sql/30_ods/020_ods_procs.sql", "CREATE OR REPLACE PROCEDURE ods.load_closed_deals(", "ods_load_closed_deals.sql")
    cut("sql/30_ods/020_ods_procs.sql", "CREATE OR REPLACE PROCEDURE ods.take_orphans(", "ods_take_orphans.sql")
    cut("sql/40_dw/030_dim_procs.sql", "CREATE OR REPLACE PROCEDURE dw.load_dim_customer(", "scd2_dim_customer.sql")
    cut("sql/40_dw/040_fact_procs.sql", "CREATE OR REPLACE PROCEDURE dw.load_fact_order_fulfillment(", "fact_order_fulfillment.sql", 95)
    olap = (ROOT / "sql" / "60_olap_examples" / "010_rollup.sql").read_text(encoding="utf-8")
    (CODE / "olap_rollup.sql").write_text(olap.split("-- QUERY:")[1].split("\n", 1)[1].split("-- QUERY:")[0].strip() + "\n", encoding="utf-8")
    piv = (ROOT / "sql" / "60_olap_examples" / "050_pivot.sql").read_text(encoding="utf-8")
    (CODE / "olap_pivot.sql").write_text(piv.split("-- QUERY:")[1].split("\n", 1)[1].split("-- QUERY:")[0].strip() + "\n", encoding="utf-8")
    hv = (ROOT / "sql" / "70_geo" / "010_geo.sql").read_text(encoding="utf-8")
    (CODE / "haversine.sql").write_text(hv[hv.index("CREATE OR REPLACE FUNCTION dw.haversine_km"):hv.index("COMMENT ON FUNCTION")].strip() + "\n", encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()

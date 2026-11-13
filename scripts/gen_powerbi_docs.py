"""Fill the generated parts of the Power BI documents from the database.

    python scripts/gen_powerbi_docs.py

  powerbi/measures.md  between  <!-- EXPECTED:START --> ... <!-- EXPECTED:END -->  : expected KPI values per dashboard DB1-DB4 (SQL on the final state of olist_dw)
  powerbi/measures.md  between  <!-- ETL:START --> ... <!-- ETL:END -->  : ETL monitoring numbers (appendix; used by report section 3.3)
  powerbi/model.md     between  <!-- APPENDIX:START --> ... <!-- APPENDIX:END -->  : one Power Query (M) snippet per CSV table with the data type of every column
Nothing is typed by hand: columns and types come from the database, tables and file names from scripts/export_powerbi.py.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

spec = importlib.util.spec_from_file_location("export_powerbi", ROOT / "scripts" / "export_powerbi.py")
export_powerbi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_powerbi)

SCOPES = [("Toàn bộ dữ liệu", None, None), ("Cửa sổ 2017-01 → 2018-08", "2017-01", "2018-08"), ("Năm 2017", "2017-01", "2017-12"), ("Tháng 2017-11", "2017-11", "2017-11")]


def scope(key_col: str, a: str | None, b: str | None) -> tuple[str, str]:
    if a is None:
        return "", ""
    return f"JOIN dw.dim_date sd ON sd.date_key = {key_col}", f"WHERE sd.year_month BETWEEN '{a}' AND '{b}'"


def kpis(conn, a, b) -> dict:
    one = lambda sql: conn.execute(text(sql)).one()
    j, w = scope("f.purchase_date_key", a, b)
    gmv, orders, items, freight = one(f"SELECT sum(f.price), count(DISTINCT f.order_id), count(*), sum(f.freight_value) FROM dw.fact_order_item f "
                                      f"JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed' {j} {w}")
    j, w = scope("o.purchase_date_key", a, b)
    (placed, failed, delivered, late, lead, appr, hand, trans, prom, delay, pva, early) = one(
        "SELECT count(*), count(*) FILTER (WHERE s.status_group = 'Failed'), sum(o.is_delivered), sum(o.is_late), "
        "avg(o.lead_days) FILTER (WHERE o.is_delivered = 1), avg(o.approval_hours) FILTER (WHERE o.is_delivered = 1), "
        "avg(o.handling_days) FILTER (WHERE o.is_delivered = 1), avg(o.transit_days) FILTER (WHERE o.is_delivered = 1), "
        "avg(o.promised_days) FILTER (WHERE o.is_delivered = 1), avg(o.delay_days) FILTER (WHERE o.is_delivered = 1), "
        "avg(o.promised_days - o.lead_days) FILTER (WHERE o.is_delivered = 1 AND o.lead_days IS NOT NULL AND o.promised_days IS NOT NULL), "
        f"count(*) FILTER (WHERE o.is_delivered = 1 AND o.delay_days < 0) FROM dw.fact_order_fulfillment o JOIN dw.dim_order_status s ON s.order_status_key = o.order_status_key {j} {w}")
    cust, rep = one(f"WITH c AS (SELECT dc.customer_unique_id, count(*) AS n FROM dw.fact_order_fulfillment o JOIN dw.dim_customer dc ON dc.customer_key = o.customer_key {j} {w} "
                    "GROUP BY 1) SELECT count(*), count(*) FILTER (WHERE n >= 2) FROM c")
    j, w = scope("f.review_creation_date_key", a, b)
    revs, avg_rev, neg, rev_late, rev_ok = one("SELECT count(*), avg(f.review_score), sum(f.is_negative), avg(f.review_score) FILTER (WHERE f.is_delivered = 1 AND f.delivered_late = 1), "
                                               f"avg(f.review_score) FILTER (WHERE f.is_delivered = 1 AND f.delivered_late = 0) FROM dw.fact_review f {j} {w}")
    j, w = scope("f.purchase_date_key", a, b)
    pay, npay, inst = one(f"SELECT sum(f.payment_value), count(*), avg(f.payment_installments) FROM dw.fact_payment f {j} {w}")
    j, w = scope("f.first_contact_date_key", a, b)
    mql, won, sale, dclose, dsale, g90 = one("SELECT count(*), sum(f.is_won), sum(f.has_first_sale), avg(f.days_to_close), avg(f.days_won_to_first_sale), "
                                             f"sum(f.seller_gmv_first_90d) FROM dw.fact_lead_funnel f {j} {w}")
    j, w = scope("f.month_date_key", a, b)
    act, sm_late, sm_del, sm_gmv = one("SELECT count(DISTINCT f.seller_key) FILTER (WHERE f.is_active = 1), sum(f.late_orders), sum(f.delivered_orders), sum(f.gmv) "
                                       f"FROM dw.fact_seller_monthly f {j} {w}")
    d = lambda x, y: (float(x) / float(y)) if y else None
    return {
        "GMV": (gmv, "money"), "Orders": (orders, "int"), "Items": (items, "int"), "AOV": (d(gmv, orders), "money"), "Freight": (freight, "money"),
        "Freight ratio": (d(freight, gmv), "pct1"), "Orders placed": (placed, "int"), "Failed orders": (failed, "int"), "Cancel rate": (d(failed, placed), "pct2"),
        "Delivered orders": (delivered, "int"), "Late orders": (late, "int"), "Late rate": (d(late, delivered), "pct1"), "On-time rate": (d((delivered or 0) - (late or 0), delivered), "pct1"),
        "Early delivery rate": (d(early, delivered), "pct1"),
        "Avg lead days": (lead, "d1"), "Avg approval hours": (appr, "d1"), "Avg handling days": (hand, "d1"), "Avg transit days": (trans, "d1"),
        "Avg promised days": (prom, "d1"), "Avg delay days": (delay, "d1"), "Promised vs actual (days)": (pva, "d1"),
        "Payment value": (pay, "money"), "Payments": (npay, "int"), "Avg installments": (inst, "d2"),
        "Reviews": (revs, "int"), "Avg review": (avg_rev, "d2"), "% negative": (d(neg, revs), "pct1"),
        "Avg review - late delivery": (rev_late, "d2"), "Avg review - on time": (rev_ok, "d2"),
        "Customers": (cust, "int"), "Repeat customers": (rep, "int"), "Repeat customer rate": (d(rep, cust), "pct2"),
        "MQLs (theo tháng liên hệ đầu)": (mql, "int"), "Won deals": (won, "int"), "MQL to won rate": (d(won, mql), "pct1"),
        "Avg days to close": (dclose, "d1"), "Sellers with first sale": (sale, "int"), "Won to first sale rate": (d(sale, won), "pct1"),
        "Avg days won to first sale": (dsale, "d1"), "Seller GMV first 90d": (g90, "money"),
        "Active sellers (fact_seller_monthly)": (act, "int"), "Seller GMV (monthly)": (sm_gmv, "money"), "Seller late rate": (d(sm_late, sm_del), "pct1"),
    }


def fmt(v, kind: str) -> str:
    if v is None:
        return "(trống)"
    v = float(v)
    return {"money": f"{v:,.2f}", "int": f"{v:,.0f}", "pct1": f"{100 * v:.1f}%", "pct2": f"{100 * v:.2f}%", "d1": f"{v:.1f}", "d2": f"{v:.2f}"}[kind]


def gmv_month(conn, ym: str) -> float:
    return float(conn.execute(text("SELECT coalesce(sum(f.price), 0) FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key "
                                   "JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed' WHERE d.year_month = :m"), {"m": ym}).scalar_one())


DB_MEASURES = {
    "DB1 – Tổng quan và doanh thu": ["GMV", "Orders", "Items", "AOV", "Freight", "Freight ratio", "Orders placed", "Cancel rate", "On-time rate", "Avg review"],
    "DB2 – Giao hàng và trải nghiệm khách": ["Orders placed", "Failed orders", "Cancel rate", "Delivered orders", "Late orders", "Late rate", "On-time rate", "Early delivery rate", "Avg lead days",
                                           "Avg approval hours", "Avg handling days", "Avg transit days", "Avg promised days", "Avg delay days", "Promised vs actual (days)",
                                           "Reviews", "Avg review", "% negative", "Avg review - late delivery", "Avg review - on time", "Payment value", "Payments", "Avg installments",
                                           "Customers", "Repeat customers", "Repeat customer rate"],
    "DB3 – Địa lý và phí vận chuyển": ["GMV", "Orders", "Freight", "Freight ratio", "Avg lead days", "Late rate"],
    "DB4 – Thu hút và hiệu quả seller": ["MQLs (theo tháng liên hệ đầu)", "Won deals", "MQL to won rate", "Avg days to close", "Sellers with first sale", "Won to first sale rate",
                                       "Avg days won to first sale", "Seller GMV first 90d", "Active sellers (fact_seller_monthly)", "Seller GMV (monthly)", "Seller late rate"],
}


def expected_block(conn) -> str:
    res = [kpis(conn, a, b) for _, a, b in SCOPES]
    out = []
    for db, names in DB_MEASURES.items():
        lines = [f"### {db}", "", "| Measure | " + " | ".join(s[0] for s in SCOPES) + " |", "| --- | " + " | ".join("---:" for _ in SCOPES) + " |"]
        for name in names:
            lines.append(f"| {name} | " + " | ".join(fmt(r[name][0], r[name][1]) for r in res) + " |")
        if db.startswith("DB1"):
            lines += ["", "**So sánh theo thời gian (GMV)**", "", "| Tháng đang chọn | GMV | GMV last month | GMV MoM % | GMV last year | GMV YoY % |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
            for ym, lm, ly in [("2017-11", "2017-10", "2016-11"), ("2018-05", "2018-04", "2017-05"), ("2018-08", "2018-07", "2017-08")]:
                g, m, y = gmv_month(conn, ym), gmv_month(conn, lm), gmv_month(conn, ly)
                mom = f"{100 * (g - m) / m:+.1f}%" if m else "(trống)"
                yoy = f"{100 * (g - y) / y:+.1f}%" if y else "(trống)"
                lines.append(f"| {ym} | {g:,.2f} | {m:,.2f} | {mom} | {y:,.2f} | {yoy} |")
        out += lines + [""]
    out += ["Ghi chú: dòng *Tháng 2017-11* và các cột có lọc thời gian áp dụng cho ngày mua (đơn, thanh toán), ngày tạo review (review), tháng liên hệ đầu (funnel) và tháng của snapshot (seller theo tháng). "
            "Bộ lọc tương ứng trên Power BI: slicer `dim_date[year_month]` hoặc bộ lọc trang `InWindow = TRUE`. Measure dùng ở nhiều dashboard (ví dụ GMV ở DB1 và DB3) có cùng giá trị."]
    return "\n".join(out)


def etl_block(conn) -> str:
    q = conn.execute(text("SELECT checks, passed, failed, pass_pct, eda_checks, eda_match FROM etl_log.v_dq_summary ORDER BY batch_id DESC LIMIT 1")).one()
    runs = conn.execute(text("SELECT count(*), min(duration_sec), round(avg(duration_sec), 1), max(duration_sec) FROM etl_log.v_run_summary WHERE mode = 'incremental' AND staging_rows > 0")).one()
    rej = conn.execute(text("SELECT coalesce(sum(row_count), 0) FROM etl_log.v_rejected_summary")).scalar_one()
    bm = conn.execute(text("SELECT min(mql), max(mql), min(deals_won), max(deals_won), min(sellers_with_sale), max(sellers_with_sale), max(gmv) FROM etl_log.batch_metrics")).one()
    iss = conn.execute(text("SELECT detail, CASE WHEN fact_table = 'fact_lead_funnel' THEN max(row_count) ELSE sum(row_count) END AS n FROM etl_log.fact_load_issue GROUP BY fact_table, detail ORDER BY 2 DESC")).fetchall()
    rows = [("Số phép kiểm thử ở lô mới nhất (checks / đạt / lỗi)", f"{q[0]} / {q[1]} / {q[2]}"), ("`pass_pct` lô mới nhất", f"{q[3]}"), ("Đối chiếu EDA (khớp / tổng)", f"{q[5]} / {q[4]}"),
            ("Số lô tăng dần (`mode = incremental`, có dữ liệu mới)", f"{runs[0]}"), ("Thời gian mỗi lô: nhỏ nhất / TB / lớn nhất (giây)", f"{runs[1]} / {runs[2]} / {runs[3]}"),
            ("Tổng `row_count` ở `v_rejected_summary`", f"{int(rej):,}"), ("`batch_metrics`: MQL nhỏ nhất → lớn nhất", f"{bm[0]:,} → {bm[1]:,}"),
            ("`batch_metrics`: deal chốt nhỏ nhất → lớn nhất", f"{bm[2]:,} → {bm[3]:,}"), ("`batch_metrics`: seller có đơn nhỏ nhất → lớn nhất", f"{bm[4]:,} → {bm[5]:,}"),
            ("`batch_metrics`: GMV lớn nhất (BRL)", f"{float(bm[6]):,.2f}")] + [(f"`fact_load_issue`: {d}", f"{n:,}") for d, n in iss]
    return "| Chỉ số | Giá trị |\n| --- | ---: |\n" + "\n".join(f"| {a} | {b} |" for a, b in rows) + "\n\n*Số theo lần chạy cuối; số lô và thời gian có thể thay đổi nếu chạy pipeline thêm lần nữa.*"


M_TYPE = {"int2": "Int64.Type", "int4": "Int64.Type", "int8": "Int64.Type", "numeric": "type number", "float8": "type number", "float4": "type number",
          "text": "type text", "bpchar": "type text", "varchar": "type text", "date": "type date", "timestamp": "type datetime", "timestamptz": "type datetimezone",
          "bool": "type logical"}


def appendix_block(conn) -> str:
    out = []
    for table, desc, drop in export_powerbi.TABLES:
        name = table.split(".")[1]
        cols = [(c, t) for c, t in export_powerbi.columns_of(conn, table) if c not in ("dw_created_at", "dw_updated_at")]
        items = [f'{{"{c}", {M_TYPE[t]}}}' for c, t in cols]
        rows, line = [], "    "
        for it in items:                        # wrap at ~110 characters
            if len(line) + len(it) > 110:
                rows.append(line.rstrip())
                line = "    "
            line += it + ", "
        rows.append(line.rstrip().rstrip(","))
        extra = "\n// dim_date: thêm bước loại dòng Unknown (date_key = -1) và cột InWindow - xem mục 3.3 của model.md" if name == "dim_date" else ""
        out += [f"**{name}** – {desc}", "", "```m", "let", f'    Source = fnCsv("{name}.csv", {{', *["    " + r for r in rows], "    })", "in", "    Source" + extra, "```", ""]
    return "\n".join(out)


def inject(path: Path, start: str, end: str, body: str) -> None:
    s = path.read_text(encoding="utf-8")
    a, b = s.index(start) + len(start), s.index(end)
    path.write_text(s[:a] + "\n" + body + "\n" + s[b:], encoding="utf-8")


def main() -> None:
    engine = get_engine(config.DB_NAME)
    with engine.connect() as conn:
        inject(ROOT / "powerbi" / "measures.md", "<!-- EXPECTED:START -->", "<!-- EXPECTED:END -->", expected_block(conn))
        inject(ROOT / "powerbi" / "measures.md", "<!-- ETL:START -->", "<!-- ETL:END -->", etl_block(conn))
        print("measures.md: expected values per dashboard and ETL appendix written")
        model = ROOT / "powerbi" / "model.md"
        if model.exists():
            inject(model, "<!-- APPENDIX:START -->", "<!-- APPENDIX:END -->", appendix_block(conn))
            print("model.md: appendix written")


if __name__ == "__main__":
    main()

"""Generate handoff/stats.md: CSV sizes + row/column/size counts of the source tables in each database.

    python scripts/report_stats.py                      # olist_dw and olist_full
    python scripts/report_stats.py --database olist_dw

The warehouse part lists every table, the dimensions (hierarchies, samples) and the facts (grain, measures, totals).
All numbers come from the files and the databases.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine
from etl.load_source import SPECS, TABLE_NAMES


def fmt_bytes(n: int) -> str:
    return f"{n / 1024 / 1024:,.2f} MB" if n >= 1024 * 1024 else f"{n / 1024:,.1f} KB"


def csv_table() -> str:
    lines = ["| File | Thư mục | Dung lượng | Số dòng dữ liệu | Số cột |", "| --- | --- | ---: | ---: | ---: |"]
    tot_b = tot_r = 0
    for s in SPECS:
        df = pd.read_csv(s.path, dtype=str, keep_default_na=False)
        size = s.path.stat().st_size
        tot_b, tot_r = tot_b + size, tot_r + len(df)
        lines.append(f"| {s.path.name} | {s.path.parent.name} | {fmt_bytes(size)} | {len(df):,} | {len(df.columns)} |")
    lines.append(f"| **Tổng ({len(SPECS)} file)** | | **{fmt_bytes(tot_b)}** | **{tot_r:,}** | |")
    return "\n".join(lines)


def db_section(database: str) -> str:
    engine = get_engine(database)
    lines = [f"### Database `{database}`", "", "| Bảng | Số dòng | Số cột | Dung lượng (gồm index) |", "| --- | ---: | ---: | ---: |"]
    tot_rows = tot_cols = 0
    with engine.connect() as conn:
        for t in TABLE_NAMES:
            schema, name = t.split(".")
            n = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar_one()
            c = conn.execute(text("SELECT count(*) FROM information_schema.columns WHERE table_schema=:s AND table_name=:t"),
                             {"s": schema, "t": name}).scalar_one()
            size = conn.execute(text("SELECT pg_total_relation_size(:t)"), {"t": t}).scalar_one()
            tot_rows, tot_cols = tot_rows + n, tot_cols + c
            lines.append(f"| {t} | {n:,} | {c} | {fmt_bytes(size)} |")
        db_size = conn.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
        rej = conn.execute(text("SELECT count(*) FROM etl_log.rejected_rows")).scalar_one()
    lines.append(f"| **Tổng ({len(TABLE_NAMES)} bảng)** | **{tot_rows:,}** | **{tot_cols}** | |")
    lines += ["", f"- Dung lượng cả database: **{fmt_bytes(db_size)}**", f"- Số dòng trong etl_log.rejected_rows: **{rej:,}**"]
    return "\n".join(lines)


HIERARCHIES = {
    "dim_date": [("Năm", "count(DISTINCT year)"), ("Quý", "count(DISTINCT year_quarter)"), ("Tháng", "count(DISTINCT year_month)"), ("Ngày", "count(*)")],
    "dim_geography": [("Vùng", "count(DISTINCT region)"), ("Bang", "count(DISTINCT state_code)"), ("Thành phố", "count(DISTINCT (state_code, city))"),
                      ("Zip", "count(DISTINCT zip_code_prefix)")],
    "dim_customer": [("Bang", "count(DISTINCT state_code)"), ("Thành phố", "count(DISTINCT (state_code, city))"),
                     ("Khách thật", "count(DISTINCT customer_unique_id)"), ("Phiên bản (SCD2)", "count(*)")],
    "dim_seller": [("Bang", "count(DISTINCT state_code)"), ("Thành phố", "count(DISTINCT (state_code, city))"),
                   ("Nhóm kênh", "count(DISTINCT acquisition_channel)"), ("Origin", "count(DISTINCT acquisition_origin)"), ("Seller", "count(*)")],
    "dim_product": [("Nhóm ngành hàng", "count(DISTINCT category_group)"), ("Danh mục", "count(DISTINCT category_name_pt)"), ("Sản phẩm", "count(*)")],
    "dim_order_status": [("Nhóm trạng thái", "count(DISTINCT status_group)"), ("Trạng thái", "count(*)")],
    "dim_payment_type": [("Nhóm", "count(DISTINCT payment_group)"), ("Loại", "count(*)")],
    "dim_lead_origin": [("Nhóm kênh", "count(DISTINCT channel_group)"), ("Origin", "count(*)")],
    "dim_lead_profile": [("Phân khúc", "count(DISTINCT business_segment)"), ("Tổ hợp hồ sơ", "count(*)")],
    "dim_sales_rep": [("Vai trò", "count(DISTINCT rep_role)"), ("Nhân viên-vai trò", "count(*)")],
}
DIM_ORDER = list(HIERARCHIES)


def warehouse_section(database: str) -> str:
    engine = get_engine(database)
    lines = [f"## Số dòng mọi bảng của `{database}` (staging, ods, dw, etl_log)", "", "| Schema | Bảng | Số dòng |", "| --- | --- | ---: |"]
    with engine.connect() as conn:
        tabs = conn.execute(text("SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' "
                                 "AND table_schema IN ('oltp','crm','staging','ods','dw','etl_log') ORDER BY 1, 2")).fetchall()
        for sch, tbl in tabs:
            n = conn.execute(text(f'SELECT count(*) FROM {sch}."{tbl}"')).scalar_one()
            lines.append(f"| {sch} | {tbl} | {n:,} |")
        lines += ["", "## Các dimension: số bản ghi, 5 dòng mẫu, phân cấp", ""]
        for dim in DIM_ORDER:
            n = conn.execute(text(f"SELECT count(*) FROM dw.{dim}")).scalar_one()
            hier = conn.execute(text("SELECT " + ", ".join(expr for _, expr in HIERARCHIES[dim]) + f" FROM dw.{dim} WHERE {DIM_ORDER_KEY[dim]} <> -1")).one()
            chain = " → ".join(f"{name} ({int(v):,})" for (name, _), v in zip(HIERARCHIES[dim], hier))
            sample = pd.read_sql_query(text(f"SELECT * FROM dw.{dim} WHERE {DIM_ORDER_KEY[dim]} <> -1 ORDER BY {DIM_ORDER_KEY[dim]} LIMIT 5"), conn)
            sample = sample.drop(columns=[c for c in ("dw_created_at", "dw_updated_at") if c in sample.columns]).astype(str).fillna("NULL")
            sample = sample.apply(lambda col: col.str.slice(0, 22))
            lines += [f"### dw.{dim} – {n:,} dòng (gồm dòng Unknown key −1)", "", f"Phân cấp / số phần tử: {chain}", "",
                      "| " + " | ".join(sample.columns) + " |", "| " + " | ".join("---" for _ in sample.columns) + " |",
                      *["| " + " | ".join(r) + " |" for r in sample.itertuples(index=False)], ""]
        lines.append(fact_section(conn))
    return "\n".join(lines)


FACTS = [
    ("fact_order_item", "Transaction", "1 dòng sản phẩm trong 1 đơn", "price, freight_value, item_total"),
    ("fact_order_fulfillment", "Accumulating snapshot", "1 đơn hàng", "approval_hours, handling_days, transit_days, lead_days, delay_days, promised_days, is_late, order_value"),
    ("fact_payment", "Transaction", "1 lần thanh toán", "payment_value, payment_installments"),
    ("fact_review", "Transaction", "1 review của 1 đơn", "review_score, is_negative, response_hours"),
    ("fact_lead_funnel", "Accumulating snapshot", "1 MQL", "is_won, has_first_sale, days_to_close, days_won_to_first_sale, seller_gmv_first_90d"),
    ("fact_seller_monthly", "Periodic snapshot", "1 seller × 1 tháng (dày đặc)", "orders, items, gmv, freight, late_rate, avg_review_score"),
]
FACT_TOTALS = [
    ("Số đơn (fact_order_fulfillment)", "SELECT count(*) FROM dw.fact_order_fulfillment"),
    ("Số dòng hàng (fact_order_item)", "SELECT count(*) FROM dw.fact_order_item"),
    ("Tổng price, mọi đơn (BRL)", "SELECT sum(price) FROM dw.fact_order_item"),
    ("GMV = Σ price của đơn không thuộc nhóm Failed (BRL)",
     "SELECT sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_order_status s USING (order_status_key) WHERE s.status_group <> 'Failed'"),
    ("Tổng freight_value (BRL)", "SELECT sum(freight_value) FROM dw.fact_order_item"),
    ("Tổng payment_value (BRL)", "SELECT sum(payment_value) FROM dw.fact_payment"),
    ("Số đơn đã giao / giao trễ", "SELECT sum(is_delivered) || ' / ' || sum(is_late) FROM dw.fact_order_fulfillment"),
    ("Số đơn bị hủy", "SELECT sum(is_canceled) FROM dw.fact_order_fulfillment"),
    ("Điểm review trung bình / % review tiêu cực", "SELECT round(avg(review_score), 2) || ' / ' || round(100.0 * avg(is_negative), 1) || '%' FROM dw.fact_review"),
    ("MQL / đã chốt (won) / seller đã có đơn", "SELECT count(*) || ' / ' || sum(is_won) || ' / ' || sum(has_first_sale) FROM dw.fact_lead_funnel"),
    ("Số seller trong fact_seller_monthly / số tháng", "SELECT count(DISTINCT seller_key) || ' / ' || count(DISTINCT month_date_key) FROM dw.fact_seller_monthly"),
    ("Σ gmv của fact_seller_monthly (phải bằng GMV ở trên, giai đoạn có đơn)", "SELECT sum(gmv) FROM dw.fact_seller_monthly"),
]


def fact_section(conn) -> str:
    lines = ["## Các fact: grain, số dòng, measure, tổng", "", "| Fact | Loại | Grain | Số dòng | Measure chính |", "| --- | --- | --- | ---: | --- |"]
    for name, kind, grain, measures in FACTS:
        n = conn.execute(text(f"SELECT count(*) FROM dw.{name}")).scalar_one()
        lines.append(f"| dw.{name} | {kind} | {grain} | {n:,} | {measures} |")
    lines += ["", "| Chỉ số | Giá trị |", "| --- | ---: |"]
    for label, sql in FACT_TOTALS:
        v = conn.execute(text(sql)).scalar_one()
        shown = f"{v:,.2f}" if hasattr(v, "quantize") else f"{v:,}" if isinstance(v, int) else str(v)
        lines.append(f"| {label} | {shown} |")
    issues = conn.execute(text("SELECT fact_table, issue_type, detail, sum(row_count) FROM etl_log.fact_load_issue "
                               "WHERE batch_id = (SELECT max(batch_id) FROM etl_log.fact_load_issue) GROUP BY 1, 2, 3 ORDER BY 1, 2, 3")).fetchall()
    lines += ["", "### Vấn đề ghi nhận khi nạp fact (lô gần nhất, `etl_log.fact_load_issue`)", ""]
    if issues:
        lines += ["| Fact | Loại | Chi tiết | Số dòng |", "| --- | --- | --- | ---: |"] + [f"| {a} | {b} | {c} | {d:,} |" for a, b, c, d in issues]
    else:
        lines.append("Không có.")
    # 5 sample rows per fact
    for name, *_ in FACTS:
        sample = pd.read_sql_query(text(f"SELECT * FROM dw.{name} ORDER BY 1, 2 LIMIT 5"), conn)
        sample = sample.drop(columns=[c for c in ("etl_batch_id",) if c in sample.columns]).astype(str).fillna("NULL").apply(lambda col: col.str.slice(0, 22))
        lines += ["", f"### dw.{name} – 5 dòng mẫu", "", "| " + " | ".join(sample.columns) + " |", "| " + " | ".join("---" for _ in sample.columns) + " |",
                  *["| " + " | ".join(r) + " |" for r in sample.itertuples(index=False)]]
    return "\n".join(lines) + "\n"


DIM_ORDER_KEY = {"dim_date": "date_key", "dim_geography": "geography_key", "dim_customer": "customer_key", "dim_seller": "seller_key",
                 "dim_product": "product_key", "dim_order_status": "order_status_key", "dim_payment_type": "payment_type_key",
                 "dim_lead_origin": "lead_origin_key", "dim_lead_profile": "lead_profile_key", "dim_sales_rep": "sales_rep_key"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", action="append", help="database(s) to report (default: DB_NAME and DB_NAME_FULL)")
    args = parser.parse_args()
    parts = [f"# Thống kê dữ liệu (sinh tự động {datetime.now():%Y-%m-%d %H:%M})", "", "## File CSV nguồn", "", csv_table(), "",
             "## Bảng nguồn (oltp + crm)", ""]
    parts += [db_section(d) + "\n" for d in (args.database or [config.DB_NAME, config.DB_NAME_FULL])]
    parts += ["", warehouse_section(config.DB_NAME)]
    out = config.ROOT / "handoff" / "stats.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Written {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()

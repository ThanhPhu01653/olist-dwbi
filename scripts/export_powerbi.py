"""Export the warehouse for Power BI: every dimension, every fact and etl_log.job_run -> exports/powerbi/<table>.csv
(+ exports/powerbi/README.md listing files, row counts, columns and the join keys).

    python scripts/export_powerbi.py [--database olist_dw]

CSV rules (CLAUDE.md): UTF-8 with BOM, ',' separator, '.' decimal point, dates as YYYY-MM-DD, file name = table name.
Everything comes straight from the database (COPY ... TO STDOUT); nothing is typed by hand.
"""
from __future__ import annotations

import argparse
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

OUT_DIR = config.ROOT / "exports" / "powerbi"
SIZE_LIMIT_MB = 50

# table -> (description, columns to leave out)
TABLES: list[tuple[str, str, tuple[str, ...]]] = [
    ("dw.dim_date", "Chiều thời gian (1 dòng / ngày 2016–2020 + Unknown -1)", ()),
    ("dw.dim_geography", "Chiều địa lý (1 dòng / zip)", ()),
    ("dw.dim_customer", "Chiều khách hàng, SCD2 (1 dòng / phiên bản địa chỉ)", ()),
    ("dw.dim_seller", "Chiều seller, dùng chung bán hàng và funnel", ()),
    ("dw.dim_product", "Chiều sản phẩm", ()),
    ("dw.dim_order_status", "Chiều trạng thái đơn", ()),
    ("dw.dim_payment_type", "Chiều hình thức thanh toán", ()),
    ("dw.dim_lead_origin", "Chiều kênh thu hút MQL", ()),
    ("dw.dim_lead_profile", "Chiều hồ sơ deal (junk dimension)", ()),
    ("dw.dim_sales_rep", "Chiều nhân viên sales (SDR / SR)", ()),
    ("dw.fact_order_item", "Fact giao dịch: 1 dòng hàng của 1 đơn", ()),
    ("dw.fact_order_fulfillment", "Fact accumulating snapshot: 1 đơn", ()),
    ("dw.fact_payment", "Fact giao dịch: 1 lần thanh toán", ()),
    ("dw.fact_review", "Fact giao dịch: 1 review", ()),
    ("dw.fact_lead_funnel", "Fact accumulating snapshot: 1 MQL", ()),
    ("dw.fact_seller_monthly", "Fact periodic snapshot: 1 seller × 1 tháng", ()),
    ("etl_log.job_run", "Nhật ký chạy ETL từng job (số liệu cho mục 3.3 ETL)", ()),
    ("etl_log.v_run_summary", "Tóm tắt mỗi lô ETL: chế độ, thời gian, số dòng từng tầng (mục 3.3 ETL)", ()),
    ("etl_log.v_dq_summary", "Kết quả kiểm thử chất lượng theo lô (mục 3.3 ETL)", ()),
    ("etl_log.v_rejected_summary", "Số dòng bị loại theo lô, job, lý do (mục 3.3 ETL)", ()),
    ("etl_log.batch_metrics", "Chỉ số chính của kho sau mỗi lô: đơn, GMV, MQL, deal… (mục 3.3 ETL, minh hoạ funnel lấp đầy dần)", ()),
    ("etl_log.fact_load_issue", "Khoá rơi về Unknown và khoảng thời gian âm khi nạp fact (mục 3.3 ETL)", ()),
    ("mart_sales.v_sales_daily", "Mart: GMV, đơn, AOV theo ngày (chỉ đơn không Failed)", ()),
    ("mart_sales.v_sales_category_month", "Mart: GMV theo tháng x nhóm ngành x danh mục", ()),
    ("mart_sales.v_sales_state_month", "Mart: GMV, freight ratio theo tháng x bang của khách", ()),
    ("mart_sales.v_geo_state", "Mart địa lý: dữ liệu bản đồ theo bang (toạ độ tâm, khách, GMV, lead time, trễ)", ()),
    ("mart_sales.v_geo_zip", "Mart địa lý: dữ liệu bản đồ theo zip có toạ độ (đơn, GMV, seller)", ()),
    ("mart_sales.v_category_pareto", "Mart: Pareto 80/20 GMV theo danh mục (hạng A/B/C)", ()),
    ("mart_fulfillment.v_fulfillment_state_month", "Mart: tỷ lệ đúng hạn / hủy, thời gian từng chặng theo tháng x bang", ()),
    ("mart_fulfillment.v_status_funnel", "Mart: số đơn đi qua từng chặng theo tháng (dạng dài)", ()),
    ("mart_cx.v_review_vs_delay", "Mart: điểm review theo nhóm trễ giao x tháng", ()),
    ("mart_cx.v_payment_mix_month", "Mart: cơ cấu thanh toán theo tháng x hình thức", ()),
    ("mart_cx.v_customer_rfm", "Mart: RFM từng khách thật và phân khúc", ()),
    ("mart_cx.v_customer_cohort", "Mart: cohort khách quay lại theo tháng mua đầu", ()),
    ("mart_acquisition.v_funnel_by_origin_month", "Mart: funnel MQL -> won -> có đơn theo tháng liên hệ x origin", ()),
    ("mart_acquisition.v_seller_scorecard", "Mart: scorecard từng seller có đơn (Pareto, cờ mẫu nhỏ)", ()),
    ("mart_acquisition.v_seller_by_channel", "Mart: seller và GMV theo kênh thu hút", ()),
]

# join keys shown in the README: fact column -> dimension (role)
JOINS = [
    ("fact_order_item", "purchase_date_key, shipping_limit_date_key → dim_date.date_key; customer_key → dim_customer; customer_geography_key, seller_geography_key → dim_geography.geography_key; seller_key → dim_seller; product_key → dim_product; order_status_key → dim_order_status"),
    ("fact_order_fulfillment", "purchase_date_key, approved_date_key, carrier_date_key, delivered_date_key, estimated_date_key → dim_date.date_key; customer_key → dim_customer; customer_geography_key → dim_geography.geography_key; order_status_key → dim_order_status"),
    ("fact_payment", "purchase_date_key → dim_date.date_key; customer_key → dim_customer; payment_type_key → dim_payment_type"),
    ("fact_review", "review_creation_date_key, review_answer_date_key → dim_date.date_key; customer_key → dim_customer; (order_id nối được với fact_order_fulfillment)"),
    ("fact_lead_funnel", "first_contact_date_key, won_date_key, first_sale_date_key → dim_date.date_key; lead_origin_key → dim_lead_origin; lead_profile_key → dim_lead_profile; seller_key → dim_seller; sdr_key, sr_key → dim_sales_rep.sales_rep_key"),
    ("fact_seller_monthly", "month_date_key → dim_date.date_key; seller_key → dim_seller"),
    ("dim_customer", "geography_key → dim_geography"),
    ("dim_seller", "geography_key → dim_geography"),
]


def columns_of(conn, table: str) -> list[tuple[str, str]]:
    """[(column, udt_name)] in table order; works for tables, views and materialized views (information_schema does not list the latter)."""
    return [tuple(r) for r in conn.execute(text(
        "SELECT a.attname, t.typname FROM pg_attribute a JOIN pg_type t ON t.oid = a.atttypid WHERE a.attrelid = CAST(:r AS regclass) "
        "AND a.attnum > 0 AND NOT a.attisdropped ORDER BY a.attnum"), {"r": table})]


def export_table(conn, table: str, drop: tuple[str, ...]) -> tuple[int, list[str], int]:
    """Write exports/powerbi/<table>.csv; return (rows, columns, bytes)."""
    schema, name = table.split(".")
    info = columns_of(conn, table)
    technical = ("dw_created_at", "dw_updated_at")      # warehouse bookkeeping, useless in reports
    info = [(c, u) for c, u in info if c not in drop and c not in technical]
    cols = [c for c, _ in info]
    # booleans as true/false (COPY would write t/f), char(n) without trailing blanks
    select_list = ", ".join(f"{c}::text AS {c}" if u == "bool" else f"rtrim({c}) AS {c}" if u == "bpchar" else c for c, u in info)
    order = {"fact_order_item": "order_id, order_item_id", "fact_payment": "order_id, payment_sequential", "fact_review": "review_id, order_id",
             "fact_seller_monthly": "month_date_key, seller_key", "job_run": "run_id", "v_run_summary": "batch_id", "batch_metrics": "batch_id"}.get(name, cols[0])
    # session settings give ISO dates and '.' decimals regardless of the server defaults
    conn.exec_driver_sql("SET datestyle = 'ISO, YMD'")
    raw = conn.connection.dbapi_connection if hasattr(conn.connection, "dbapi_connection") else conn.connection.connection
    buf = io.BytesIO()
    with raw.cursor() as cur:
        cur.copy_expert(f"COPY (SELECT {select_list} FROM {table} ORDER BY {order}) TO STDOUT WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')", buf)
    data = buf.getvalue()
    (OUT_DIR / f"{name}.csv").write_bytes(b"\xef\xbb\xbf" + data)
    rows = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()
    return rows, cols, len(data) + 3


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", default=config.DB_NAME)
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = get_engine(args.database)
    results = []
    with engine.connect() as conn:
        for table, desc, drop in TABLES:
            rows, cols, size = export_table(conn, table, drop)
            results.append((table, desc, rows, cols, size))
            print(f"  {table.split('.')[1]}.csv: {rows:,} rows, {size / 1024 / 1024:.2f} MB")
        max_batch = conn.execute(text("SELECT max(batch_id) FROM etl_log.job_run")).scalar_one()
        cutoff = conn.execute(text("SELECT max(full_date) FROM dw.fact_order_fulfillment f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key")).scalar_one()
    total_mb = sum(r[4] for r in results) / 1024 / 1024
    lines = [
        "# Dữ liệu xuất cho Power BI", "",
        f"> Sinh tự động bằng `python scripts/export_powerbi.py` lúc {datetime.now():%Y-%m-%d %H:%M} từ database `{args.database}` "
        f"(lô ETL mới nhất: {max_batch}; đơn mua muộn nhất trong dữ liệu: {cutoff}). Đừng sửa tay.", "",
        "**Định dạng**: UTF-8 có BOM, phân cách `,`, số thập phân `.`, ngày `YYYY-MM-DD`, cột đúng/sai ghi `true`/`false`, ô trống = NULL, tên file = tên bảng. "
        "Trong Power BI chọn *Get data → Text/CSV*, đặt *File origin* = UTF-8, rồi **Transform Data** để đặt kiểu cột (xem hướng dẫn trong `handoff/`).", "",
        f"**Dung lượng**: {total_mb:.1f} MB tổng cộng. " + (
            f"Dưới {SIZE_LIMIT_MB} MB nên các file được commit cùng repo." if total_mb < SIZE_LIMIT_MB else
            f"**Trên {SIZE_LIMIT_MB} MB nên các file `*.csv` không được commit** (đã có trong `.gitignore`); cả thư mục được chia sẻ qua Google Drive, link ở `exports/README.md`. Tên file giữ nguyên giữa các lần xuất nên Power BI chỉ cần *Refresh*."), "",
        "## Danh sách file", "", "| File | Mô tả | Số dòng | Dung lượng | Số cột |", "| --- | --- | ---: | ---: | ---: |"]
    for table, desc, rows, cols, size in results:
        lines.append(f"| {table.split('.')[1]}.csv | {desc} | {rows:,} | {size / 1024 / 1024:.2f} MB | {len(cols)} |")
    lines += ["", "## Khoá nối (fact → dimension)", "",
              "Mọi khoá `*_key` là số nguyên; `-1` là dòng Unknown của chiều (ví dụ mốc chưa xảy ra, MQL chưa chốt). "
              "`dim_date` dùng nhiều lần (role-playing): tạo **một quan hệ đang hoạt động** và các quan hệ còn lại để *không hoạt động* "
              "(dùng `USERELATIONSHIP` trong DAX) hoặc nhân bản bảng ngày.", "", "| Bảng | Khoá nối |", "| --- | --- |"]
    lines += [f"| {t} | {j} |" for t, j in JOINS]
    lines += ["", "## Cột của từng file", ""]
    for table, desc, rows, cols, size in results:
        lines += [f"**{table.split('.')[1]}** – " + ", ".join(f"`{c}`" for c in cols), ""]
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Written exports/powerbi/README.md ({total_mb:.1f} MB in {len(results)} files)")


if __name__ == "__main__":
    main()

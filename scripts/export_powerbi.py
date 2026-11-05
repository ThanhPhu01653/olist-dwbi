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
    ("dw.dim_date", "Chiều thời gian (1 dòng / ngày 2016–2019 + Unknown -1)", ()),
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
    ("etl_log.job_run", "Nhật ký chạy ETL (cho dashboard D7)", ()),
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


def export_table(conn, table: str, drop: tuple[str, ...]) -> tuple[int, list[str], int]:
    """Write exports/powerbi/<table>.csv; return (rows, columns, bytes)."""
    schema, name = table.split(".")
    info = conn.execute(
        text("SELECT column_name, udt_name FROM information_schema.columns WHERE table_schema = :s AND table_name = :t ORDER BY ordinal_position"),
        {"s": schema, "t": name}).fetchall()
    technical = ("dw_created_at", "dw_updated_at")      # warehouse bookkeeping, useless in reports
    info = [(c, u) for c, u in info if c not in drop and c not in technical]
    cols = [c for c, _ in info]
    # booleans as true/false (COPY would write t/f), char(n) without trailing blanks
    select_list = ", ".join(f"{c}::text AS {c}" if u == "bool" else f"rtrim({c}) AS {c}" if u == "bpchar" else c for c, u in info)
    order = {"fact_order_item": "order_id, order_item_id", "fact_payment": "order_id, payment_sequential", "fact_review": "review_id, order_id",
             "fact_seller_monthly": "month_date_key, seller_key", "job_run": "run_id"}.get(name, cols[0])
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
            f"**Trên {SIZE_LIMIT_MB} MB: không commit; KT1 tải lên Google Drive và ghi link vào đây.**"), "",
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

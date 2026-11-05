"""Generate docs/mapping.csv: source-to-target mapping (source column -> target column -> transformation).

Layers: 'oltp/crm -> ods' (generated from the real table structures, same-name columns are copies unless overridden)
and 'ods -> dw' (dimension sections, defined below; fact sections are added in P4).
    python scripts/gen_mapping.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

# (source schema.table, ods table, ods column) -> (source column, transformation)
ODS_OVERRIDES: dict[tuple[str, str], tuple[str, str]] = {
    ("products", "name_length"): ("product_name_lenght", "Đổi tên cột (sửa chính tả *_lenght → *_length)"),
    ("products", "description_length"): ("product_description_lenght", "Đổi tên cột (sửa chính tả *_lenght → *_length)"),
    ("products", "photos_qty"): ("product_photos_qty", "Đổi tên cột (bỏ tiền tố product_)"),
    ("products", "weight_g"): ("product_weight_g", "Đổi tên cột (bỏ tiền tố product_)"),
    ("products", "length_cm"): ("product_length_cm", "Đổi tên cột (bỏ tiền tố product_)"),
    ("products", "height_cm"): ("product_height_cm", "Đổi tên cột (bỏ tiền tố product_)"),
    ("products", "width_cm"): ("product_width_cm", "Đổi tên cột (bỏ tiền tố product_)"),
    ("products", "product_category_name"): ("product_category_name", "trim; rỗng/NULL → 'unknown'"),
    ("products", "dq_missing_dimensions"): ("product_weight_g, product_length_cm, product_height_cm, product_width_cm",
                                            "true nếu thiếu (NULL) bất kỳ số đo nào hoặc cân nặng = 0; giữ nguyên giá trị gốc"),
    ("sellers", "zip_code_prefix"): ("seller_zip_code_prefix", "Chuẩn hoá char(5): bỏ ký tự không phải số, lpad(…,5,'0')"),
    ("sellers", "city"): ("seller_city", "lower(unaccent(trim())); rỗng → NULL"),
    ("sellers", "state_code"): ("seller_state", "upper(trim()), 2 ký tự"),
    ("customers", "zip_code_prefix"): ("customer_zip_code_prefix", "Chuẩn hoá char(5): bỏ ký tự không phải số, lpad(…,5,'0')"),
    ("customers", "city"): ("customer_city", "lower(unaccent(trim())); rỗng → NULL"),
    ("customers", "state_code"): ("customer_state", "upper(trim()), 2 ký tự"),
    ("orders", "order_status"): ("order_status", "lower(trim())"),
    ("orders", "dq_flags"): ("các cột mốc thời gian + order_status", "Mảng cờ lỗi: approved_before_purchase, carrier_before_purchase, carrier_before_approved, "
                              "delivered_before_carrier, delivered_before_purchase, estimated_before_purchase, delivered_without_date, "
                              "delivered_without_carrier_date, delivered_without_approval, delivery_date_but_not_delivered"),
    ("orders", "dq_flag_count"): ("dq_flags", "cardinality(dq_flags)"),
    ("order_payments", "payment_type"): ("payment_type", "lower(trim())"),
    ("order_payments", "payment_installments"): ("payment_installments", "NULL hoặc 0 → 1 (greatest(...,1))"),
    ("order_payments", "dq_flags"): ("payment_installments, payment_type, payment_value",
                                     "Cờ: installments_zero_set_to_1, payment_type_not_defined, payment_value_zero"),
    ("mql", "origin"): ("origin", "lower(trim()); NULL/rỗng → 'unknown'"),
    ("closed_deals", "has_company"): ("has_company", "boolean → text 'true'/'false'; NULL → 'unknown'"),
    ("closed_deals", "has_gtin"): ("has_gtin", "boolean → text 'true'/'false'; NULL → 'unknown'"),
    ("closed_deals", "dq_flags"): ("declared_monthly_revenue, declared_product_catalog_size, won_date",
                                   "Cờ: declared_revenue_zero, declared_catalog_zero, won_before_first_contact (so với mql.first_contact_date)"),
}
for col in ["business_segment", "lead_type", "lead_behaviour_profile", "business_type", "average_stock"]:
    ODS_OVERRIDES[("closed_deals", col)] = (col, "trim; NULL/rỗng → 'unknown'")

SRC_OF = {"orders": "oltp.orders", "customers": "oltp.customers", "order_items": "oltp.order_items", "order_payments": "oltp.order_payments",
          "order_reviews": "oltp.order_reviews", "sellers": "oltp.sellers", "products": "oltp.products",
          "category_translation": "oltp.product_category_name_translation", "mql": "crm.mql", "closed_deals": "crm.closed_deals"}
TABLE_RULES = {
    "order_reviews": "Khử trùng trên cặp (review_id, order_id): giữ bản có review_answer_timestamp mới nhất, dòng còn lại ghi etl_log.rejected_rows",
    "order_items": "Dòng mồ côi (order/product/seller không có trong ODS) → etl_log.rejected_rows",
    "order_payments": "Dòng mồ côi (order không có trong ODS) → etl_log.rejected_rows",
    "orders": "Dòng mồ côi (customer không có trong ODS) → etl_log.rejected_rows",
    "closed_deals": "Dòng mồ côi (mql không có trong ODS) → etl_log.rejected_rows",
}

# ods -> dw dimensions
DW_ROWS: list[tuple[str, str, str, str, str]] = []   # (dw table, dw column, source table, source column, transformation)


def build() -> list[dict]:
    eng = get_engine(config.DB_NAME)
    rows: list[dict] = []
    with eng.connect() as c:
        cols = c.execute(text("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema='ods' "
                              "AND table_name = ANY(:t) AND column_name <> 'etl_batch_id' ORDER BY table_name, ordinal_position"),
                         {"t": list(SRC_OF)}).fetchall()
    for tbl, col in cols:
        src_col, rule = ODS_OVERRIDES.get((tbl, col), (col, "Giữ nguyên giá trị"))
        if tbl == "order_reviews" and col == "review_id":
            rule = TABLE_RULES["order_reviews"]
        rows.append({"layer": "nguồn → ods", "source_table": SRC_OF[tbl], "source_column": src_col, "target_table": f"ods.{tbl}",
                     "target_column": col, "transformation": rule})
    # geolocation (many rows -> one row per zip) and customer_map
    for col, src, rule in [
        ("zip_code_prefix", "geolocation_zip_code_prefix", "Chuẩn hoá char(5) rồi GROUP BY zip"),
        ("latitude", "geolocation_lat", "Median (percentile_cont 0.5) sau khi lọc bbox Brazil lat −33.75…5.27"),
        ("longitude", "geolocation_lng", "Median (percentile_cont 0.5) sau khi lọc bbox Brazil lng −73.99…−34.79"),
        ("city", "geolocation_city", "lower(unaccent(trim())) rồi lấy mode theo zip"),
        ("state_code", "geolocation_state", "upper(trim()) rồi lấy mode theo zip"),
        ("n_points", "(số dòng)", "count(*) điểm hợp lệ của zip"),
    ]:
        rows.append({"layer": "nguồn → ods", "source_table": "oltp.geolocation", "source_column": src, "target_table": "ods.geolocation_zip",
                     "target_column": col, "transformation": rule})
    rows.append({"layer": "nguồn → ods", "source_table": "oltp.geolocation", "source_column": "(mọi cột)", "target_table": "etl_log.rejected_rows",
                 "target_column": "record", "transformation": "Điểm ngoài bbox Brazil bị loại khỏi phép gom và ghi etl_log.rejected_rows"})
    for col in ["customer_id", "customer_unique_id"]:
        rows.append({"layer": "nguồn → ods", "source_table": "oltp.customers", "source_column": col, "target_table": "ods.customer_map",
                     "target_column": col, "transformation": "Giữ nguyên; bảng ánh xạ customer_id → customer_unique_id"})
    for tbl, col, src_t, src_c, rule in DW_ROWS:
        rows.append({"layer": "ods → dw", "source_table": src_t, "source_column": src_c, "target_table": f"dw.{tbl}",
                     "target_column": col, "transformation": rule})
    return rows


def main() -> None:
    rows = build()
    out = config.ROOT / "docs" / "mapping.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["layer", "source_table", "source_column", "target_table", "target_column", "transformation"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"written {out.relative_to(config.ROOT)}: {len(rows)} rows")


if __name__ == "__main__":
    main()

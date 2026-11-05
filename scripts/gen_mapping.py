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


def _dim(table: str, rows: list[tuple[str, str, str, str]]) -> None:
    DW_ROWS.extend((table, c, st, sc, rule) for c, st, sc, rule in rows)


KEY = "Khoá thay thế tự sinh (identity); dòng Unknown có key -1"
_dim("dim_date", [("date_key", "(lịch)", "full_date", "Số yyyymmdd; -1 = Unknown"), ("full_date", "(lịch)", "-", "Mỗi ngày 2016-01-01 … 2019-12-31"),
    ("day_of_week", "(lịch)", "full_date", "isoweekday: 1 = Thứ Hai"), ("week_of_year", "(lịch)", "full_date", "Tuần ISO"),
    ("year_month / year_quarter", "(lịch)", "full_date", "'YYYY-MM' / 'YYYY-Qn'"), ("is_weekend", "(lịch)", "full_date", "Thứ Bảy, Chủ Nhật"),
    ("is_holiday_br / holiday_name", "(package holidays)", "holidays.Brazil", "Ngày lễ quốc gia Brazil"),
    ("is_black_friday", "(lịch)", "full_date", "Thứ Sáu sau thứ Năm thứ 4 của tháng 11")])
_dim("dim_geography", [("geography_key", "-", "-", KEY),
    ("zip_code_prefix", "ods.geolocation_zip ∪ ods.customers ∪ ods.sellers", "zip_code_prefix", "Hợp nhất mọi zip (khoá tự nhiên, UNIQUE)"),
    ("city / state_code", "ods.geolocation_zip (ưu tiên) hoặc ods.customers/sellers", "city, state_code", "Lấy từ geolocation_zip; zip chỉ có ở customers/sellers thì lấy mode"),
    ("state_name / region", "ods.ref_state_region", "state_name, region", "Tra theo state_code; không có → 'Unknown'"),
    ("latitude / longitude", "ods.geolocation_zip", "latitude, longitude", "Giữ median; NULL nếu zip không có toạ độ"),
    ("country", "-", "-", "Hằng 'Brazil'")])
_dim("dim_customer", [("customer_key", "-", "-", KEY + " (mỗi phiên bản một key)"),
    ("customer_unique_id", "ods.customers", "customer_unique_id", "Khoá tự nhiên của khách thật"),
    ("zip_code_prefix / city / state_code", "ods.customers", "zip_code_prefix, city, state_code", "Thuộc tính của phiên bản (từ đơn mở phiên bản)"),
    ("geography_key", "dw.dim_geography", "geography_key", "Tra theo zip; không có → -1"),
    ("effective_from / effective_to / is_current / version_no", "ods.orders + ods.customers", "order_purchase_timestamp, zip",
     "SCD2: mỗi lần zip đổi so với đơn trước mở phiên bản mới (effective_from = ngày mua; phiên bản đầu 1900-01-01; hiện hành 9999-12-31)")])
_dim("dim_seller", [("seller_key", "-", "-", KEY), ("seller_id", "ods.sellers ∪ ods.closed_deals", "seller_id", "Khoá tự nhiên; seller chỉ có trong CRM vẫn có dòng"),
    ("zip_code_prefix / city / state_code", "ods.sellers", "zip_code_prefix, city, state_code", "NULL / 'unknown' nếu seller chỉ có trong CRM"),
    ("geography_key", "dw.dim_geography", "geography_key", "Tra theo zip; không có → -1"),
    ("is_from_funnel / mql_id", "ods.closed_deals", "mql_id", "true nếu seller có trong closed_deals"),
    ("acquisition_origin", "ods.mql", "origin", "origin của MQL; 'not_from_funnel' nếu không từ funnel"),
    ("acquisition_channel", "ods.ref_lead_origin_group", "channel_group", "Nhóm kênh; 'Not from funnel' nếu không từ funnel"),
    ("business_segment / lead_type / business_type", "ods.closed_deals", "business_segment, lead_type, business_type", "Giữ nguyên"),
    ("won_date", "ods.closed_deals", "won_date", "cast date"), ("first_sale_date", "dw.fact_order_item", "purchase_date_key", "Ngày mua đầu tiên (cập nhật ở P4)")])
_dim("dim_product", [("product_key", "-", "-", KEY), ("product_id", "ods.products", "product_id", "Khoá tự nhiên"),
    ("category_name_pt", "ods.products", "product_category_name", "Giữ nguyên ('unknown' nếu rỗng)"),
    ("category_name_en", "ods.category_translation / ods.ref_category_translation_extra", "product_category_name_english", "Bản dịch gốc, thiếu thì lấy seed bổ sung"),
    ("category_group", "ods.ref_category_group", "category_group", "Tra theo category_name_pt; không có → 'Unknown'"),
    ("weight_g / length_cm / height_cm / width_cm / photos_qty / name_length / description_length", "ods.products", "cùng tên", "Giữ nguyên"),
    ("volume_cm3", "ods.products", "length_cm, height_cm, width_cm", "dài × cao × rộng; NULL nếu thiếu"),
    ("size_class", "ods.products", "weight_g", "S < 500 g; M < 2 kg; L < 10 kg; XL ≥ 10 kg; Unknown nếu thiếu hoặc 0")])
_dim("dim_order_status", [("order_status / status_group / is_final", "ods.ref_order_status", "cùng tên", "Giữ nguyên từ seed order_status.csv")])
_dim("dim_payment_type", [("payment_type / payment_group / display_name", "ods.ref_payment_type", "cùng tên", "Giữ nguyên từ seed payment_type.csv")])
_dim("dim_lead_origin", [("origin / channel_group", "ods.ref_lead_origin_group", "cùng tên", "Giữ nguyên từ seed; 'unknown' là nhóm kênh Unknown riêng, không gộp với 'other'")])
_dim("dim_lead_profile", [("business_segment … average_stock (7 cột)", "ods.closed_deals", "cùng tên",
                           "Junk dimension: mỗi tổ hợp khác nhau của 7 thuộc tính một dòng; dòng -1 cho MQL chưa chốt")])
_dim("dim_sales_rep", [("rep_id / rep_role", "ods.closed_deals", "sdr_id → 'SDR'; sr_id → 'SR'", "Tách hai vai trò thành các dòng (rep_id, rep_role)")])


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

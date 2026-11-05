"""Generate docs/mapping.csv: source-to-target mapping (source column -> target column -> transformation).

Layers: 'oltp/crm -> ods' (generated from the real table structures, same-name columns are copies unless overridden)
and 'ods -> dw' (dimension and fact sections, defined below).
Also writes docs/mapping_oltp_olap.md (the ods -> dw part as readable tables, one per dimension / fact).
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
_dim("dim_date", [("date_key", "(lịch)", "full_date", "Số yyyymmdd; -1 = Unknown"), ("full_date", "(lịch)", "-", "Mỗi ngày 2016-01-01 … 2020-12-31"),
    ("day_of_week", "(lịch)", "full_date", "isoweekday: 1 = Thứ Hai"), ("week_of_year", "(lịch)", "full_date", "Tuần ISO"),
    ("year_month / year_quarter", "(lịch)", "full_date", "'YYYY-MM' / 'YYYY-Qn'"), ("is_weekend", "(lịch)", "full_date", "Thứ Bảy, Chủ Nhật"),
    ("is_holiday_br / holiday_name", "(package holidays)", "holidays.Brazil", "Ngày lễ quốc gia Brazil"),
    ("is_black_friday", "(lịch)", "full_date", "Thứ Sáu sau thứ Năm thứ 4 của tháng 11")])
_dim("dim_geography", [("geography_key", "-", "-", KEY),
    ("zip_code_prefix", "ods.geolocation_zip ∪ ods.customers ∪ ods.sellers", "zip_code_prefix", "Hợp nhất mọi zip (khoá tự nhiên, UNIQUE)"),
    ("city / state_code", "ods.geolocation_zip (ưu tiên) hoặc ods.customers/sellers", "city, state_code", "Lấy từ geolocation_zip; zip chỉ có ở customers/sellers thì lấy mode"),
    ("state_name / region", "ods.ref_state_region", "state_name, region", "Tra theo state_code; không có → 'Unknown'"),
    ("latitude / longitude", "ods.geolocation_zip", "latitude, longitude", "Giữ median; NULL nếu zip không có toạ độ hợp lệ (không có trong geolocation hoặc mọi điểm nằm ngoài bbox)"),
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
    ("won_date", "ods.closed_deals", "won_date", "cast date"), ("first_sale_date", "dw.fact_order_item", "purchase_date_key", "min(ngày mua) của các dòng fact_order_item có seller này (cập nhật sau khi nạp fact)")])
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

# ods -> dw facts
DK = "Ngày → yyyymmdd (dim_date); NULL hoặc ngoài 2016–2020 → -1"
CUST = "ods.orders.customer_id → ods.customers.customer_unique_id → dw.dim_customer: phiên bản SCD2 có hiệu lực tại ngày mua; không có → -1"
_dim("fact_order_item", [
    ("order_id / order_item_id", "ods.order_items", "order_id, order_item_id", "Giữ nguyên (degenerate dimension, khoá chính)"),
    ("purchase_date_key", "ods.orders", "order_purchase_timestamp", DK),
    ("shipping_limit_date_key", "ods.order_items", "shipping_limit_date", DK),
    ("customer_key", "ods.orders, ods.customers, dw.dim_customer", "customer_id", CUST),
    ("customer_geography_key", "dw.dim_customer", "geography_key", "geography_key của phiên bản khách tìm được ở trên"),
    ("seller_geography_key", "dw.dim_seller", "geography_key", "Tra theo seller_id"),
    ("seller_key / product_key", "dw.dim_seller, dw.dim_product", "seller_id, product_id", "Tra khoá thay thế theo khoá tự nhiên; không có → -1"),
    ("order_status_key", "ods.orders, dw.dim_order_status", "order_status", "Tra theo trạng thái đơn; không có → -1"),
    ("price / freight_value", "ods.order_items", "price, freight_value", "Giữ nguyên (additive)"),
    ("item_total", "ods.order_items", "price, freight_value", "price + freight_value"),
    ("etl_batch_id", "-", "-", "Lô ETL đã nạp (UPSERT: ghi đè nếu có cột khác đổi)")])
_dim("fact_order_fulfillment", [
    ("order_id", "ods.orders", "order_id", "Giữ nguyên (khoá chính; UPSERT theo order_id)"),
    ("customer_key / customer_geography_key", "ods.orders, ods.customers, dw.dim_customer", "customer_id", CUST + "; geography_key lấy từ phiên bản đó"),
    ("order_status_key", "ods.orders, dw.dim_order_status", "order_status", "Tra theo trạng thái đơn; không có → -1"),
    ("purchase_date_key / approved_date_key / carrier_date_key / delivered_date_key / estimated_date_key", "ods.orders",
     "order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date",
     DK + " (mốc chưa xảy ra = NULL → -1)"),
    ("purchase_ts … estimated_ts (5 cột)", "ods.orders", "5 cột mốc thời gian", "Giữ nguyên timestamp gốc"),
    ("approval_hours", "ods.orders", "order_approved_at − order_purchase_timestamp", "Số giờ; NULL nếu thiếu mốc hoặc âm (lỗi nguồn, ghi etl_log.fact_load_issue)"),
    ("handling_days", "ods.orders", "order_delivered_carrier_date − order_approved_at", "Số ngày (2 chữ số thập phân); NULL nếu thiếu mốc hoặc âm"),
    ("transit_days", "ods.orders", "order_delivered_customer_date − order_delivered_carrier_date", "Số ngày; NULL nếu thiếu mốc hoặc âm"),
    ("lead_days", "ods.orders", "order_delivered_customer_date − order_purchase_timestamp", "Số ngày; NULL nếu thiếu mốc hoặc âm"),
    ("delay_days", "ods.orders", "order_delivered_customer_date, order_estimated_delivery_date", "delivered::date − estimated::date (âm = giao sớm); NULL nếu chưa giao"),
    ("promised_days", "ods.orders", "order_estimated_delivery_date, order_purchase_timestamp", "estimated::date − purchase::date; NULL nếu âm"),
    ("is_delivered", "ods.orders", "order_status, order_delivered_customer_date", "1 nếu status = 'delivered' và có ngày giao"),
    ("is_late", "(tính từ delay_days)", "is_delivered, delay_days", "1 nếu is_delivered = 1 và delay_days > 0"),
    ("is_canceled", "ods.orders", "order_status", "1 nếu status = 'canceled'"),
    ("item_count / seller_count", "ods.order_items", "order_item_id, seller_id", "count(*) và count(distinct seller_id) theo đơn"),
    ("order_value / freight_total", "ods.order_items", "price, freight_value", "Σ theo đơn (0 nếu đơn không có dòng hàng)"),
    ("payment_total", "ods.order_payments", "payment_value", "Σ theo đơn"),
    ("dq_flag_count", "ods.orders", "dq_flag_count", "Số cờ lỗi ODS của đơn + số khoảng thời gian bị đặt NULL vì âm"),
    ("etl_batch_id", "-", "-", "Lô ETL cuối cùng ghi dòng")])
_dim("fact_payment", [
    ("order_id / payment_sequential", "ods.order_payments", "order_id, payment_sequential", "Giữ nguyên (khoá chính)"),
    ("purchase_date_key", "ods.orders", "order_purchase_timestamp", DK),
    ("customer_key", "ods.orders, ods.customers, dw.dim_customer", "customer_id", CUST),
    ("payment_type_key", "ods.order_payments, dw.dim_payment_type", "payment_type", "Tra theo loại thanh toán; không có → -1"),
    ("payment_installments / payment_value", "ods.order_payments", "payment_installments, payment_value", "Giữ nguyên (installments đã chuẩn hoá ≥ 1 ở ODS)")])
_dim("fact_review", [
    ("review_id / order_id", "ods.order_reviews", "review_id, order_id", "Giữ nguyên (khoá chính; đã khử trùng ở ODS)"),
    ("review_creation_date_key / review_answer_date_key", "ods.order_reviews", "review_creation_date, review_answer_timestamp", DK),
    ("customer_key", "ods.orders, ods.customers, dw.dim_customer", "customer_id", CUST),
    ("review_score", "ods.order_reviews", "review_score", "Giữ nguyên (CHECK 1–5)"),
    ("is_negative", "ods.order_reviews", "review_score", "1 nếu điểm ≤ 2"),
    ("has_comment_title / has_comment_message", "ods.order_reviews", "review_comment_title, review_comment_message", "1 nếu khác rỗng sau trim"),
    ("comment_length", "ods.order_reviews", "review_comment_message", "Số ký tự sau trim (0 nếu không có)"),
    ("response_hours", "ods.order_reviews", "review_answer_timestamp − review_creation_date", "Số giờ; NULL nếu thiếu hoặc âm"),
    ("delivered_late", "dw.fact_order_fulfillment", "is_late", "Lấy từ fulfillment của cùng đơn; không có → 0")])
_dim("fact_lead_funnel", [
    ("mql_id / landing_page_id", "ods.mql", "mql_id, landing_page_id", "Giữ nguyên (mỗi MQL một dòng)"),
    ("first_contact_date_key", "ods.mql", "first_contact_date", DK),
    ("won_date_key", "ods.closed_deals", "won_date", DK + "; MQL chưa chốt → -1"),
    ("first_sale_date_key", "dw.dim_seller", "first_sale_date", DK + "; seller chưa có đơn → -1"),
    ("lead_origin_key", "ods.mql, dw.dim_lead_origin", "origin", "Tra theo origin; không có → -1"),
    ("lead_profile_key", "ods.closed_deals, dw.dim_lead_profile", "7 thuộc tính của deal", "Tra theo tổ hợp 7 thuộc tính; MQL chưa chốt → -1"),
    ("seller_key", "ods.closed_deals, dw.dim_seller", "seller_id", "Tra theo seller_id; MQL chưa chốt → -1"),
    ("sdr_key / sr_key", "ods.closed_deals, dw.dim_sales_rep", "sdr_id, sr_id", "Tra theo (rep_id, vai trò); không có → -1"),
    ("is_won / has_first_sale", "ods.closed_deals, dw.dim_seller", "mql_id, first_sale_date", "1 nếu có deal / nếu seller đã có đơn"),
    ("days_to_close", "ods.closed_deals, ods.mql", "won_date, first_contact_date", "won::date − first_contact_date; NULL nếu chưa chốt hoặc âm"),
    ("days_won_to_first_sale", "dw.dim_seller, ods.closed_deals", "first_sale_date, won_date", "first_sale_date − won::date; NULL nếu chưa có hoặc âm"),
    ("declared_product_catalog_size / declared_monthly_revenue", "ods.closed_deals", "cùng tên", "Giữ nguyên (non-additive)"),
    ("seller_gmv_first_90d", "dw.fact_order_item", "price", "Σ price của đơn không Failed của seller trong 90 ngày kể từ ngày đơn đầu; NULL nếu chưa có đơn")])
_dim("fact_seller_monthly", [
    ("month_date_key", "dw.fact_order_item", "purchase_date_key", "Ngày 1 của tháng mua; dày đặc từ tháng đơn đầu của seller đến tháng cuối có đơn"),
    ("seller_key", "dw.fact_order_item", "seller_key", "Giữ nguyên"),
    ("orders / items", "dw.fact_order_item", "order_id", "count(distinct order_id) / count(*) trong tháng, mọi trạng thái; 0 nếu tháng không có đơn"),
    ("gmv / freight", "dw.fact_order_item", "price, freight_value", "Σ của đơn không thuộc nhóm Failed"),
    ("delivered_orders / late_orders / canceled_orders", "dw.fact_order_fulfillment", "is_delivered, is_late, is_canceled", "Σ theo đơn của seller trong tháng"),
    ("late_rate", "(tính)", "late_orders, delivered_orders", "late_orders ÷ delivered_orders; NULL nếu chưa có đơn giao"),
    ("avg_review_score", "dw.fact_review", "review_score", "avg theo review của các đơn trong tháng; NULL nếu không có"),
    ("is_active", "(tính)", "orders", "1 nếu orders > 0"),
    ("months_since_first_sale", "(tính)", "month_date_key", "Số tháng kể từ tháng có đơn đầu của seller (0 = tháng đầu)")])


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
        ("latitude", "geolocation_lat", "Median (percentile_cont 0.5) sau khi lọc bbox Brazil lat −33.75…5.27; NULL nếu zip không còn điểm hợp lệ"),
        ("longitude", "geolocation_lng", "Median (percentile_cont 0.5) sau khi lọc bbox Brazil lng −73.99…−34.79; NULL nếu zip không còn điểm hợp lệ"),
        ("city", "geolocation_city", "lower(unaccent(trim())) rồi lấy mode theo zip"),
        ("state_code", "geolocation_state", "upper(trim()) rồi lấy mode theo zip"),
        ("n_points", "(số dòng)", "count(*) điểm hợp lệ của zip (0 nếu mọi điểm của zip nằm ngoài bbox)"),
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
    write_markdown(rows)

def write_markdown(rows: list[dict]) -> None:
    """docs/mapping_oltp_olap.md: ods -> dw mapping, one table per dimension / fact (readable on GitHub)."""
    out = config.ROOT / "docs" / "mapping_oltp_olap.md"

    def esc(t: str) -> str:
        return str(t).replace("|", "\\|")

    lines = ["# Mapping OLTP → OLAP (nguồn → ODS → DW)", "",
             "> Sinh tự động bằng `python scripts/gen_mapping.py` từ cấu trúc bảng thật. Đừng sửa tay. "
             "Bản đầy đủ gồm cả bước nguồn → ODS: `docs/mapping.csv`.", "",
             "Cách đọc: *Bảng nguồn* là bảng ODS (đã làm sạch từ `oltp`/`crm`) hoặc bảng DW dùng để tra khoá; "
             "*Phép biến đổi* nói cách tính cột đích. Khoá `-1` là dòng Unknown của chiều.", ""]
    for tbl in dict.fromkeys(r["target_table"] for r in rows if r["layer"] == "ods → dw"):
        kind = "Fact" if tbl.startswith("dw.fact_") else "Dimension"
        lines += [f"## {kind} `{tbl}`", "", "| Cột đích | Bảng nguồn | Cột nguồn | Phép biến đổi |", "| --- | --- | --- | --- |"]
        lines += [f"| {esc(r['target_column'])} | {esc(r['source_table'])} | {esc(r['source_column'])} | {esc(r['transformation'])} |"
                  for r in rows if r["layer"] == "ods → dw" and r["target_table"] == tbl]
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {out.relative_to(config.ROOT)}")



if __name__ == "__main__":
    main()

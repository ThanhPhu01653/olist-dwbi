# P8-C3 – Tổng hợp mapping OLTP → OLAP

*Sinh tự động bởi `scripts/p8_mapping_summary.py` từ `docs/mapping.csv`.*

| Bảng nguồn | Số cột | Cột dùng sang OLAP | Bảng đích (dim, fact) | Ví dụ phép biến đổi |
| --- | ---: | ---: | --- | --- |
| oltp.customers | 5 | 5 | dim_customer, dim_geography, fact_order_fulfillment, fact_order_item, fact_payment, fact_review | customer_zip_code_prefix → zip_code_prefix: Chuẩn hoá char(5): bỏ ký tự không phải số, lpad(…,5,'0') |
| oltp.geolocation | 6 | 5 | dim_geography | geolocation_zip_code_prefix → zip_code_prefix: Chuẩn hoá char(5) rồi GROUP BY zip |
| oltp.order_items | 7 | 7 | fact_order_fulfillment, fact_order_item | giữ nguyên giá trị |
| oltp.order_payments | 5 | 5 | fact_order_fulfillment, fact_payment | payment_type → payment_type: lower(trim()) |
| oltp.order_reviews | 7 | 7 | fact_review | review_id → review_id: Khử trùng trên cặp (review_id, order_id): giữ bản có review_answer_timestamp mới nhất, dòng còn lại ghi etl_log.rejected_rows |
| oltp.orders | 8 | 8 | dim_customer, fact_order_fulfillment, fact_order_item, fact_payment, fact_review | order_status → order_status: lower(trim()) |
| oltp.product_category_name_translation | 2 | 2 | dim_product | giữ nguyên giá trị |
| oltp.products | 9 | 6 | dim_product | product_category_name → product_category_name: trim; rỗng/NULL → 'unknown' |
| oltp.sellers | 4 | 4 | dim_geography, dim_seller | seller_zip_code_prefix → zip_code_prefix: Chuẩn hoá char(5): bỏ ký tự không phải số, lpad(…,5,'0') |
| crm.closed_deals | 14 | 8 | dim_lead_profile, dim_sales_rep, dim_seller, fact_lead_funnel | business_segment → business_segment: trim; NULL/rỗng → 'unknown' |
| crm.mql | 4 | 4 | dim_seller, fact_lead_funnel | origin → origin: lower(trim()); NULL/rỗng → 'unknown' |
| **Tổng** | 71 | 61 | | |

Cột dùng sang OLAP: 61 / 71 cột nguồn (85.9%). Các cột không dùng sang OLAP: crm.closed_deals.average_stock, crm.closed_deals.declared_monthly_revenue, crm.closed_deals.declared_product_catalog_size, crm.closed_deals.has_company, crm.closed_deals.has_gtin, crm.closed_deals.lead_behaviour_profile, oltp.geolocation.id, oltp.products.product_description_lenght, oltp.products.product_name_lenght, oltp.products.product_photos_qty.

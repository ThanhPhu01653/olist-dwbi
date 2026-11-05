# Dữ liệu xuất cho Power BI

> Sinh tự động bằng `python scripts/export_powerbi.py` lúc 2026-11-05 19:28 từ database `olist_dw` (lô ETL mới nhất: 96; đơn mua muộn nhất trong dữ liệu: 2018-10-17). Đừng sửa tay.

**Định dạng**: UTF-8 có BOM, phân cách `,`, số thập phân `.`, ngày `YYYY-MM-DD`, cột đúng/sai ghi `true`/`false`, ô trống = NULL, tên file = tên bảng. Trong Power BI chọn *Get data → Text/CSV*, đặt *File origin* = UTF-8, rồi **Transform Data** để đặt kiểu cột (xem hướng dẫn trong `handoff/`).

**Dung lượng**: 69.0 MB tổng cộng. **Trên 50 MB nên các file `*.csv` không được commit** (đã có trong `.gitignore`); cả thư mục được chia sẻ qua Google Drive, link ở `exports/README.md`. Tên file giữ nguyên giữa các lần xuất nên Power BI chỉ cần *Refresh*.

## Danh sách file

| File | Mô tả | Số dòng | Dung lượng | Số cột |
| --- | --- | ---: | ---: | ---: |
| dim_date.csv | Chiều thời gian (1 dòng / ngày 2016–2020 + Unknown -1) | 1,828 | 0.15 MB | 16 |
| dim_geography.csv | Chiều địa lý (1 dòng / zip) | 19,178 | 1.66 MB | 9 |
| dim_customer.csv | Chiều khách hàng, SCD2 (1 dòng / phiên bản địa chỉ) | 96,339 | 8.59 MB | 10 |
| dim_seller.csv | Chiều seller, dùng chung bán hàng và funnel | 3,558 | 0.44 MB | 15 |
| dim_product.csv | Chiều sản phẩm | 32,952 | 3.66 MB | 14 |
| dim_order_status.csv | Chiều trạng thái đơn | 9 | 0.00 MB | 4 |
| dim_payment_type.csv | Chiều hình thức thanh toán | 6 | 0.00 MB | 4 |
| dim_lead_origin.csv | Chiều kênh thu hút MQL | 11 | 0.00 MB | 3 |
| dim_lead_profile.csv | Chiều hồ sơ deal (junk dimension) | 503 | 0.03 MB | 8 |
| dim_sales_rep.csv | Chiều nhân viên sales (SDR / SR) | 55 | 0.00 MB | 3 |
| fact_order_item.csv | Fact giao dịch: 1 dòng hàng của 1 đơn | 112,650 | 11.09 MB | 14 |
| fact_order_fulfillment.csv | Fact accumulating snapshot: 1 đơn | 99,441 | 23.80 MB | 30 |
| fact_payment.csv | Fact giao dịch: 1 lần thanh toán | 103,886 | 6.29 MB | 8 |
| fact_review.csv | Fact giao dịch: 1 review | 99,224 | 10.55 MB | 13 |
| fact_lead_funnel.csv | Fact accumulating snapshot: 1 MQL | 8,000 | 0.84 MB | 18 |
| fact_seller_monthly.csv | Fact periodic snapshot: 1 seller × 1 tháng | 36,583 | 1.71 MB | 14 |
| job_run.csv | Nhật ký chạy ETL từng job (cho dashboard D7) | 1,525 | 0.20 MB | 13 |
| v_run_summary.csv | Tóm tắt mỗi lô ETL: chế độ, thời gian, số dòng từng tầng (D7) | 51 | 0.01 MB | 16 |
| v_dq_summary.csv | Kết quả kiểm thử chất lượng theo lô (D7) | 34 | 0.00 MB | 8 |
| v_rejected_summary.csv | Số dòng bị loại theo lô, job, lý do (D7) | 15 | 0.00 MB | 6 |
| batch_metrics.csv | Chỉ số chính của kho sau mỗi lô: đơn, GMV, MQL, deal… (D7, minh hoạ funnel lấp đầy dần) | 14 | 0.00 MB | 12 |
| fact_load_issue.csv | Khoá rơi về Unknown và khoảng thời gian âm khi nạp fact (D7) | 33 | 0.00 MB | 6 |

## Khoá nối (fact → dimension)

Mọi khoá `*_key` là số nguyên; `-1` là dòng Unknown của chiều (ví dụ mốc chưa xảy ra, MQL chưa chốt). `dim_date` dùng nhiều lần (role-playing): tạo **một quan hệ đang hoạt động** và các quan hệ còn lại để *không hoạt động* (dùng `USERELATIONSHIP` trong DAX) hoặc nhân bản bảng ngày.

| Bảng | Khoá nối |
| --- | --- |
| fact_order_item | purchase_date_key, shipping_limit_date_key → dim_date.date_key; customer_key → dim_customer; customer_geography_key, seller_geography_key → dim_geography.geography_key; seller_key → dim_seller; product_key → dim_product; order_status_key → dim_order_status |
| fact_order_fulfillment | purchase_date_key, approved_date_key, carrier_date_key, delivered_date_key, estimated_date_key → dim_date.date_key; customer_key → dim_customer; customer_geography_key → dim_geography.geography_key; order_status_key → dim_order_status |
| fact_payment | purchase_date_key → dim_date.date_key; customer_key → dim_customer; payment_type_key → dim_payment_type |
| fact_review | review_creation_date_key, review_answer_date_key → dim_date.date_key; customer_key → dim_customer; (order_id nối được với fact_order_fulfillment) |
| fact_lead_funnel | first_contact_date_key, won_date_key, first_sale_date_key → dim_date.date_key; lead_origin_key → dim_lead_origin; lead_profile_key → dim_lead_profile; seller_key → dim_seller; sdr_key, sr_key → dim_sales_rep.sales_rep_key |
| fact_seller_monthly | month_date_key → dim_date.date_key; seller_key → dim_seller |
| dim_customer | geography_key → dim_geography |
| dim_seller | geography_key → dim_geography |

## Cột của từng file

**dim_date** – `date_key`, `full_date`, `day_of_month`, `day_of_week`, `day_name`, `week_of_year`, `month`, `month_name`, `quarter`, `year`, `year_month`, `year_quarter`, `is_weekend`, `is_holiday_br`, `holiday_name`, `is_black_friday`

**dim_geography** – `geography_key`, `zip_code_prefix`, `city`, `state_code`, `state_name`, `region`, `country`, `latitude`, `longitude`

**dim_customer** – `customer_key`, `customer_unique_id`, `zip_code_prefix`, `city`, `state_code`, `geography_key`, `effective_from`, `effective_to`, `is_current`, `version_no`

**dim_seller** – `seller_key`, `seller_id`, `zip_code_prefix`, `city`, `state_code`, `geography_key`, `is_from_funnel`, `mql_id`, `acquisition_origin`, `acquisition_channel`, `business_segment`, `lead_type`, `business_type`, `won_date`, `first_sale_date`

**dim_product** – `product_key`, `product_id`, `category_name_pt`, `category_name_en`, `category_group`, `weight_g`, `length_cm`, `height_cm`, `width_cm`, `volume_cm3`, `size_class`, `photos_qty`, `name_length`, `description_length`

**dim_order_status** – `order_status_key`, `order_status`, `status_group`, `is_final`

**dim_payment_type** – `payment_type_key`, `payment_type`, `payment_group`, `display_name`

**dim_lead_origin** – `lead_origin_key`, `origin`, `channel_group`

**dim_lead_profile** – `lead_profile_key`, `business_segment`, `lead_type`, `lead_behaviour_profile`, `business_type`, `has_company`, `has_gtin`, `average_stock`

**dim_sales_rep** – `sales_rep_key`, `rep_id`, `rep_role`

**fact_order_item** – `order_id`, `order_item_id`, `purchase_date_key`, `shipping_limit_date_key`, `customer_key`, `customer_geography_key`, `seller_geography_key`, `seller_key`, `product_key`, `order_status_key`, `price`, `freight_value`, `item_total`, `etl_batch_id`

**fact_order_fulfillment** – `order_id`, `customer_key`, `customer_geography_key`, `order_status_key`, `purchase_date_key`, `approved_date_key`, `carrier_date_key`, `delivered_date_key`, `estimated_date_key`, `purchase_ts`, `approved_ts`, `carrier_ts`, `delivered_ts`, `estimated_ts`, `approval_hours`, `handling_days`, `transit_days`, `lead_days`, `delay_days`, `promised_days`, `is_delivered`, `is_late`, `is_canceled`, `item_count`, `seller_count`, `order_value`, `freight_total`, `payment_total`, `dq_flag_count`, `etl_batch_id`

**fact_payment** – `order_id`, `payment_sequential`, `purchase_date_key`, `customer_key`, `payment_type_key`, `payment_installments`, `payment_value`, `etl_batch_id`

**fact_review** – `review_id`, `order_id`, `review_creation_date_key`, `review_answer_date_key`, `customer_key`, `review_score`, `is_negative`, `has_comment_title`, `has_comment_message`, `comment_length`, `response_hours`, `delivered_late`, `etl_batch_id`

**fact_lead_funnel** – `mql_id`, `landing_page_id`, `first_contact_date_key`, `won_date_key`, `first_sale_date_key`, `lead_origin_key`, `lead_profile_key`, `seller_key`, `sdr_key`, `sr_key`, `is_won`, `has_first_sale`, `days_to_close`, `days_won_to_first_sale`, `declared_product_catalog_size`, `declared_monthly_revenue`, `seller_gmv_first_90d`, `etl_batch_id`

**fact_seller_monthly** – `month_date_key`, `seller_key`, `orders`, `items`, `gmv`, `freight`, `delivered_orders`, `late_orders`, `late_rate`, `canceled_orders`, `avg_review_score`, `is_active`, `months_since_first_sale`, `etl_batch_id`

**job_run** – `run_id`, `batch_id`, `job_name`, `layer`, `target_table`, `started_at`, `finished_at`, `status`, `rows_read`, `rows_inserted`, `rows_updated`, `rows_rejected`, `message`

**v_run_summary** – `batch_id`, `mode`, `started_at`, `finished_at`, `duration_sec`, `status`, `source_rows`, `staging_rows`, `ods_inserted`, `ods_rejected`, `dw_inserted`, `dw_updated`, `staging_sec`, `ods_sec`, `dw_sec`, `test_sec`

**v_dq_summary** – `batch_id`, `checks`, `passed`, `failed`, `pass_pct`, `eda_checks`, `eda_match`, `checked_at`

**v_rejected_summary** – `batch_id`, `job_name`, `source_table`, `reason`, `row_count`, `last_logged_at`

**batch_metrics** – `batch_id`, `taken_at`, `mode`, `orders`, `order_items`, `gmv`, `mql`, `deals_won`, `sellers_with_sale`, `customers`, `customer_versions`, `sellers`

**fact_load_issue** – `batch_id`, `fact_table`, `issue_type`, `detail`, `row_count`, `logged_at`

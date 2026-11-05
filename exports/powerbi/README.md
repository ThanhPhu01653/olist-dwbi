# Dữ liệu xuất cho Power BI

> Sinh tự động bằng `python scripts/export_powerbi.py` lúc 2026-11-05 18:57 từ database `olist_dw` (lô ETL mới nhất: 25; đơn mua muộn nhất trong dữ liệu: 2017-12-31). Đừng sửa tay.

**Định dạng**: UTF-8 có BOM, phân cách `,`, số thập phân `.`, ngày `YYYY-MM-DD`, cột đúng/sai ghi `true`/`false`, ô trống = NULL, tên file = tên bảng. Trong Power BI chọn *Get data → Text/CSV*, đặt *File origin* = UTF-8, rồi **Transform Data** để đặt kiểu cột (xem hướng dẫn trong `handoff/`).

**Dung lượng**: 34.3 MB tổng cộng. Dưới 50 MB nên các file được commit cùng repo.

## Danh sách file

| File | Mô tả | Số dòng | Dung lượng | Số cột |
| --- | --- | ---: | ---: | ---: |
| dim_date.csv | Chiều thời gian (1 dòng / ngày 2016–2019 + Unknown -1) | 1,462 | 0.12 MB | 16 |
| dim_geography.csv | Chiều địa lý (1 dòng / zip) | 19,108 | 1.66 MB | 9 |
| dim_customer.csv | Chiều khách hàng, SCD2 (1 dòng / phiên bản địa chỉ) | 44,118 | 3.93 MB | 10 |
| dim_seller.csv | Chiều seller, dùng chung bán hàng và funnel | 3,098 | 0.33 MB | 15 |
| dim_product.csv | Chiều sản phẩm | 32,952 | 3.66 MB | 14 |
| dim_order_status.csv | Chiều trạng thái đơn | 9 | 0.00 MB | 4 |
| dim_payment_type.csv | Chiều hình thức thanh toán | 6 | 0.00 MB | 4 |
| dim_lead_origin.csv | Chiều kênh thu hút MQL | 11 | 0.00 MB | 3 |
| dim_lead_profile.csv | Chiều hồ sơ deal (junk dimension) | 4 | 0.00 MB | 8 |
| dim_sales_rep.csv | Chiều nhân viên sales (SDR / SR) | 7 | 0.00 MB | 3 |
| fact_order_item.csv | Fact giao dịch: 1 dòng hàng của 1 đơn | 51,234 | 5.04 MB | 14 |
| fact_order_fulfillment.csv | Fact accumulating snapshot: 1 đơn | 45,430 | 10.85 MB | 30 |
| fact_payment.csv | Fact giao dịch: 1 lần thanh toán | 47,871 | 2.89 MB | 8 |
| fact_review.csv | Fact giao dịch: 1 review | 45,370 | 4.82 MB | 13 |
| fact_lead_funnel.csv | Fact accumulating snapshot: 1 MQL | 2,002 | 0.20 MB | 18 |
| fact_seller_monthly.csv | Fact periodic snapshot: 1 seller × 1 tháng | 13,548 | 0.65 MB | 14 |
| job_run.csv | Nhật ký chạy ETL (cho dashboard D7) | 779 | 0.11 MB | 13 |

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

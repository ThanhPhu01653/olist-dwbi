# Dữ liệu xuất cho Power BI

> Sinh tự động bằng `python scripts/export_powerbi.py` lúc 2026-11-08 13:51 từ database `olist_dw` (lô ETL mới nhất: 61; đơn mua muộn nhất trong dữ liệu: 2018-10-17). Đừng sửa tay.

**Định dạng**: UTF-8 có BOM, phân cách `,`, số thập phân `.`, ngày `YYYY-MM-DD`, cột đúng/sai ghi `true`/`false`, ô trống = NULL, tên file = tên bảng. Trong Power BI chọn *Get data → Text/CSV*, đặt *File origin* = UTF-8, rồi **Transform Data** để đặt kiểu cột (xem hướng dẫn trong `handoff/`).

**Dung lượng**: 79.7 MB tổng cộng. **Trên 50 MB nên các file `*.csv` không được commit** (đã có trong `.gitignore`); cả thư mục được chia sẻ qua Google Drive, link ở `exports/README.md`. Tên file giữ nguyên giữa các lần xuất nên Power BI chỉ cần *Refresh*.

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
| fact_order_item.csv | Fact giao dịch: 1 dòng hàng của 1 đơn | 112,650 | 11.03 MB | 14 |
| fact_order_fulfillment.csv | Fact accumulating snapshot: 1 đơn | 99,441 | 23.75 MB | 30 |
| fact_payment.csv | Fact giao dịch: 1 lần thanh toán | 103,886 | 6.23 MB | 8 |
| fact_review.csv | Fact giao dịch: 1 review | 99,224 | 10.69 MB | 14 |
| fact_lead_funnel.csv | Fact accumulating snapshot: 1 MQL | 8,000 | 0.83 MB | 18 |
| fact_seller_monthly.csv | Fact periodic snapshot: 1 seller × 1 tháng | 36,583 | 1.70 MB | 14 |
| job_run.csv | Nhật ký chạy ETL từng job (số liệu cho mục 3.3 ETL) | 712 | 0.09 MB | 13 |
| v_run_summary.csv | Tóm tắt mỗi lô ETL: chế độ, thời gian, số dòng từng tầng (mục 3.3 ETL) | 25 | 0.00 MB | 17 |
| v_dq_summary.csv | Kết quả kiểm thử chất lượng theo lô (mục 3.3 ETL) | 13 | 0.00 MB | 8 |
| v_rejected_summary.csv | Số dòng bị loại theo lô, job, lý do (mục 3.3 ETL) | 1 | 0.00 MB | 6 |
| batch_metrics.csv | Chỉ số chính của kho sau mỗi lô: đơn, GMV, MQL, deal… (mục 3.3 ETL, minh hoạ funnel lấp đầy dần) | 13 | 0.00 MB | 12 |
| fact_load_issue.csv | Khoá rơi về Unknown và khoảng thời gian âm khi nạp fact (mục 3.3 ETL) | 20 | 0.00 MB | 6 |
| v_sales_daily.csv | Mart: GMV, đơn, AOV theo ngày (chỉ đơn không Failed) | 614 | 0.05 MB | 14 |
| v_sales_category_month.csv | Mart: GMV theo tháng x nhóm ngành x danh mục | 1,282 | 0.10 MB | 11 |
| v_sales_state_month.csv | Mart: GMV, freight ratio theo tháng x bang của khách | 558 | 0.04 MB | 12 |
| v_geo_state.csv | Mart địa lý: dữ liệu bản đồ theo bang (toạ độ tâm, khách, GMV, lead time, trễ) | 27 | 0.00 MB | 13 |
| v_geo_zip.csv | Mart địa lý: dữ liệu bản đồ theo zip có toạ độ (đơn, GMV, seller) | 14,889 | 1.11 MB | 9 |
| v_category_pareto.csv | Mart: Pareto 80/20 GMV theo danh mục (hạng A/B/C) | 74 | 0.01 MB | 9 |
| v_fulfillment_state_month.csv | Mart: tỷ lệ đúng hạn / hủy, thời gian từng chặng theo tháng x bang | 565 | 0.04 MB | 15 |
| v_status_funnel.csv | Mart: số đơn đi qua từng chặng theo tháng (dạng dài) | 125 | 0.01 MB | 6 |
| v_review_vs_delay.csv | Mart: điểm review theo nhóm trễ giao x tháng | 105 | 0.01 MB | 10 |
| v_payment_mix_month.csv | Mart: cơ cấu thanh toán theo tháng x hình thức | 90 | 0.01 MB | 10 |
| v_customer_rfm.csv | Mart: RFM từng khách thật và phân khúc | 94,983 | 8.91 MB | 12 |
| v_customer_cohort.csv | Mart: cohort khách quay lại theo tháng mua đầu | 220 | 0.01 MB | 6 |
| v_funnel_by_origin_month.csv | Mart: funnel MQL -> won -> có đơn theo tháng liên hệ x origin | 113 | 0.01 MB | 11 |
| v_seller_scorecard.csv | Mart: scorecard từng seller có đơn (Pareto, cờ mẫu nhỏ) | 3,095 | 0.56 MB | 28 |
| v_seller_by_channel.csv | Mart: seller và GMV theo kênh thu hút | 7 | 0.00 MB | 10 |

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

**fact_review** – `review_id`, `order_id`, `review_creation_date_key`, `review_answer_date_key`, `customer_key`, `review_score`, `is_negative`, `has_comment_title`, `has_comment_message`, `comment_length`, `response_hours`, `delivered_late`, `is_delivered`, `etl_batch_id`

**fact_lead_funnel** – `mql_id`, `landing_page_id`, `first_contact_date_key`, `won_date_key`, `first_sale_date_key`, `lead_origin_key`, `lead_profile_key`, `seller_key`, `sdr_key`, `sr_key`, `is_won`, `has_first_sale`, `days_to_close`, `days_won_to_first_sale`, `declared_product_catalog_size`, `declared_monthly_revenue`, `seller_gmv_first_90d`, `etl_batch_id`

**fact_seller_monthly** – `month_date_key`, `seller_key`, `orders`, `items`, `gmv`, `freight`, `delivered_orders`, `late_orders`, `late_rate`, `canceled_orders`, `avg_review_score`, `is_active`, `months_since_first_sale`, `etl_batch_id`

**job_run** – `run_id`, `batch_id`, `job_name`, `layer`, `target_table`, `started_at`, `finished_at`, `status`, `rows_read`, `rows_inserted`, `rows_updated`, `rows_rejected`, `message`

**v_run_summary** – `batch_id`, `mode`, `started_at`, `finished_at`, `duration_sec`, `status`, `source_rows`, `staging_rows`, `ods_inserted`, `ods_rejected`, `dw_inserted`, `dw_updated`, `staging_sec`, `ods_sec`, `dw_sec`, `test_sec`, `mart_sec`

**v_dq_summary** – `batch_id`, `checks`, `passed`, `failed`, `pass_pct`, `eda_checks`, `eda_match`, `checked_at`

**v_rejected_summary** – `batch_id`, `job_name`, `source_table`, `reason`, `row_count`, `last_logged_at`

**batch_metrics** – `batch_id`, `taken_at`, `mode`, `orders`, `order_items`, `gmv`, `mql`, `deals_won`, `sellers_with_sale`, `customers`, `customer_versions`, `sellers`

**fact_load_issue** – `batch_id`, `fact_table`, `issue_type`, `detail`, `row_count`, `logged_at`

**v_sales_daily** – `date_key`, `full_date`, `year`, `quarter`, `year_month`, `is_weekend`, `is_holiday_br`, `is_black_friday`, `in_window`, `orders`, `items`, `gmv`, `freight`, `aov`

**v_sales_category_month** – `year_month`, `year`, `quarter`, `in_window`, `category_group`, `category_name_en`, `orders`, `items`, `gmv`, `freight`, `avg_item_price`

**v_sales_state_month** – `year_month`, `year`, `quarter`, `in_window`, `region`, `state_code`, `state_name`, `orders`, `items`, `gmv`, `freight`, `freight_ratio`

**v_geo_state** – `state_code`, `state_name`, `region`, `latitude`, `longitude`, `zips_with_coordinates`, `customers`, `orders`, `gmv`, `freight_ratio`, `sellers`, `avg_lead_days`, `late_rate_pct`

**v_geo_zip** – `zip_code_prefix`, `city`, `state_code`, `region`, `latitude`, `longitude`, `customer_orders`, `customer_gmv`, `sellers`

**v_category_pareto** – `gmv_rank`, `category_group`, `category_name_en`, `orders`, `items`, `gmv`, `share_pct`, `cum_share_pct`, `abc_class`

**v_fulfillment_state_month** – `year_month`, `in_window`, `region`, `state_code`, `orders`, `delivered_orders`, `late_orders`, `canceled_orders`, `on_time_rate_pct`, `cancel_rate_pct`, `avg_lead_days`, `avg_approval_hours`, `avg_handling_days`, `avg_transit_days`, `avg_promised_days`

**v_status_funnel** – `year_month`, `in_window`, `stage_no`, `stage`, `orders`, `pct_of_placed`

**v_review_vs_delay** – `year_month`, `in_window`, `delay_bucket_no`, `delay_bucket`, `reviews`, `score_sum`, `negative_reviews`, `avg_score`, `pct_negative`, `avg_response_hours`

**v_payment_mix_month** – `year_month`, `in_window`, `payment_type`, `payment_group`, `display_name`, `payments`, `orders`, `payment_value`, `avg_installments`, `value_share_pct`

**v_customer_rfm** – `customer_unique_id`, `region`, `state_code`, `first_purchase`, `last_purchase`, `recency_days`, `frequency`, `monetary`, `r_score`, `f_score`, `m_score`, `segment`

**v_customer_cohort** – `cohort_month`, `in_window`, `months_since`, `cohort_size`, `customers_active`, `retention_pct`

**v_funnel_by_origin_month** – `first_contact_month`, `origin`, `channel_group`, `mqls`, `won`, `won_with_sale`, `win_rate_pct`, `won_to_sale_rate_pct`, `avg_days_to_close`, `avg_days_won_to_first_sale`, `seller_gmv_first_90d`

**v_seller_scorecard** – `seller_key`, `seller_id`, `city`, `state_code`, `region`, `is_from_funnel`, `acquisition_channel`, `acquisition_origin`, `business_segment`, `first_sale_date`, `last_active_month`, `active_months`, `orders`, `items`, `gmv`, `freight`, `delivered_orders`, `late_orders`, `late_rate_pct`, `canceled_orders`, `reviews`, `avg_review_score`, `pct_negative`, `gmv_rank`, `gmv_share_pct`, `cum_share_pct`, `abc_class`, `small_sample`

**v_seller_by_channel** – `acquisition_channel`, `sellers`, `selling_sellers`, `pct_selling`, `orders`, `gmv`, `gmv_per_selling_seller`, `late_rate_pct`, `avg_review_score`, `small_sample`

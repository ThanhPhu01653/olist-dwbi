# Thống kê dữ liệu (sinh tự động 2026-11-05 19:50)

## File CSV nguồn

| File | Thư mục | Dung lượng | Số dòng dữ liệu | Số cột |
| --- | --- | ---: | ---: | ---: |
| product_category_name_translation.csv | ecommerce | 2.6 KB | 71 | 2 |
| olist_products_dataset.csv | ecommerce | 2.27 MB | 32,951 | 9 |
| olist_sellers_dataset.csv | ecommerce | 170.6 KB | 3,095 | 4 |
| olist_geolocation_dataset.csv | ecommerce | 58.44 MB | 1,000,163 | 5 |
| olist_customers_dataset.csv | ecommerce | 8.62 MB | 99,441 | 5 |
| olist_orders_dataset.csv | ecommerce | 16.84 MB | 99,441 | 8 |
| olist_order_items_dataset.csv | ecommerce | 14.72 MB | 112,650 | 7 |
| olist_order_payments_dataset.csv | ecommerce | 5.51 MB | 103,886 | 5 |
| olist_order_reviews_dataset.csv | ecommerce | 13.78 MB | 99,224 | 7 |
| olist_marketing_qualified_leads_dataset.csv | marketing | 687.3 KB | 8,000 | 4 |
| olist_closed_deals_dataset.csv | marketing | 167.3 KB | 842 | 14 |
| **Tổng (11 file)** | | **121.18 MB** | **1,559,764** | |

## Bảng nguồn (oltp + crm)

### Database `olist_dw`

| Bảng | Số dòng | Số cột | Dung lượng (gồm index) |
| --- | ---: | ---: | ---: |
| oltp.product_category_name_translation | 71 | 2 | 32.0 KB |
| oltp.products | 32,951 | 9 | 5.94 MB |
| oltp.sellers | 3,095 | 4 | 560.0 KB |
| oltp.geolocation | 1,000,163 | 6 | 106.29 MB |
| oltp.customers | 99,441 | 5 | 26.30 MB |
| oltp.orders | 99,441 | 8 | 31.83 MB |
| oltp.order_items | 112,650 | 7 | 30.96 MB |
| oltp.order_payments | 103,886 | 5 | 17.06 MB |
| oltp.order_reviews | 99,224 | 7 | 32.99 MB |
| crm.mql | 8,000 | 4 | 1.50 MB |
| crm.closed_deals | 842 | 14 | 400.0 KB |
| **Tổng (11 bảng)** | **1,559,764** | **71** | |

- Dung lượng cả database: **862.14 MB**
- Số dòng trong etl_log.rejected_rows: **630**

### Database `olist_full`

| Bảng | Số dòng | Số cột | Dung lượng (gồm index) |
| --- | ---: | ---: | ---: |
| oltp.product_category_name_translation | 71 | 2 | 32.0 KB |
| oltp.products | 32,951 | 9 | 5.94 MB |
| oltp.sellers | 3,095 | 4 | 560.0 KB |
| oltp.geolocation | 1,000,163 | 6 | 106.29 MB |
| oltp.customers | 99,441 | 5 | 26.52 MB |
| oltp.orders | 99,441 | 8 | 31.98 MB |
| oltp.order_items | 112,650 | 7 | 29.19 MB |
| oltp.order_payments | 103,886 | 5 | 17.01 MB |
| oltp.order_reviews | 99,224 | 7 | 33.84 MB |
| crm.mql | 8,000 | 4 | 1.52 MB |
| crm.closed_deals | 842 | 14 | 504.0 KB |
| **Tổng (11 bảng)** | **1,559,764** | **71** | |

- Dung lượng cả database: **261.67 MB**
- Số dòng trong etl_log.rejected_rows: **0**


## Số dòng mọi bảng của `olist_dw` (staging, ods, dw, etl_log)

| Schema | Bảng | Số dòng |
| --- | --- | ---: |
| crm | closed_deals | 842 |
| crm | mql | 8,000 |
| dw | dim_customer | 96,339 |
| dw | dim_date | 1,828 |
| dw | dim_geography | 19,178 |
| dw | dim_lead_origin | 11 |
| dw | dim_lead_profile | 503 |
| dw | dim_order_status | 9 |
| dw | dim_payment_type | 6 |
| dw | dim_product | 32,952 |
| dw | dim_sales_rep | 55 |
| dw | dim_seller | 3,558 |
| dw | fact_lead_funnel | 8,000 |
| dw | fact_order_fulfillment | 99,441 |
| dw | fact_order_item | 112,650 |
| dw | fact_payment | 103,886 |
| dw | fact_review | 99,224 |
| dw | fact_seller_monthly | 36,583 |
| etl_log | batch_metrics | 16 |
| etl_log | dq_check | 3,142 |
| etl_log | fact_load_issue | 35 |
| etl_log | job_run | 1,621 |
| etl_log | rejected_rows | 630 |
| etl_log | watermark | 4 |
| ods | category_translation | 71 |
| ods | closed_deals | 842 |
| ods | customer_map | 99,441 |
| ods | customers | 99,441 |
| ods | geolocation_zip | 19,015 |
| ods | mql | 8,000 |
| ods | order_items | 112,650 |
| ods | order_payments | 103,886 |
| ods | order_reviews | 99,224 |
| ods | orders | 99,441 |
| ods | products | 32,951 |
| ods | ref_category_group | 74 |
| ods | ref_category_translation_extra | 2 |
| ods | ref_lead_origin_group | 10 |
| ods | ref_order_status | 8 |
| ods | ref_payment_type | 5 |
| ods | ref_state_region | 27 |
| ods | sellers | 3,095 |
| oltp | customers | 99,441 |
| oltp | geolocation | 1,000,163 |
| oltp | order_items | 112,650 |
| oltp | order_payments | 103,886 |
| oltp | order_reviews | 99,224 |
| oltp | orders | 99,441 |
| oltp | product_category_name_translation | 71 |
| oltp | products | 32,951 |
| oltp | sellers | 3,095 |
| staging | stg_closed_deals | 842 |
| staging | stg_customers | 99,441 |
| staging | stg_geolocation | 1,000,163 |
| staging | stg_mql | 8,000 |
| staging | stg_order_items | 112,650 |
| staging | stg_order_payments | 103,886 |
| staging | stg_order_reviews | 99,224 |
| staging | stg_orders | 99,441 |
| staging | stg_product_category_name_translation | 71 |
| staging | stg_products | 32,951 |
| staging | stg_sellers | 3,095 |

## Các dimension: số bản ghi, 5 dòng mẫu, phân cấp

### dw.dim_date – 1,828 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Năm (5) → Quý (20) → Tháng (60) → Ngày (1,827)

| date_key | full_date | day_of_month | day_of_week | day_name | week_of_year | month | month_name | quarter | year | year_month | year_quarter | is_weekend | is_holiday_br | holiday_name | is_black_friday |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20160101 | 2016-01-01 | 1 | 5 | Friday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | True | Confraternização Unive | False |
| 20160102 | 2016-01-02 | 2 | 6 | Saturday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | True | False | NULL | False |
| 20160103 | 2016-01-03 | 3 | 7 | Sunday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | True | False | NULL | False |
| 20160104 | 2016-01-04 | 4 | 1 | Monday | 1 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | False | NULL | False |
| 20160105 | 2016-01-05 | 5 | 2 | Tuesday | 1 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | False | NULL | False |

### dw.dim_geography – 19,178 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Vùng (5) → Bang (27) → Thành phố (6,190) → Zip (19,177)

| geography_key | zip_code_prefix | city | state_code | state_name | region | country | latitude | longitude |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 01001 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.550380539269455 | -46.63402699777831 |
| 2 | 01002 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.548551065785627 | -46.63507239078997 |
| 3 | 01003 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.54897652899767 | -46.63531311226845 |
| 4 | 01004 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.549534948092827 | -46.634770582289825 |
| 5 | 01005 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.54961248124544 | -46.63653202553522 |

### dw.dim_customer – 96,339 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Bang (27) → Thành phố (4,310) → Khách thật (96,096) → Phiên bản (SCD2) (96,338)

| customer_key | customer_unique_id | zip_code_prefix | city | state_code | geography_key | effective_from | effective_to | is_current | version_no |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0000f46a3911fa3c080544 | 88115 | sao jose | SC | 17310 | 1900-01-01 | 9999-12-31 | True | 1 |
| 2 | 0000f6ccb0745a6a4b8866 | 66812 | belem | PA | 13649 | 1900-01-01 | 9999-12-31 | True | 1 |
| 3 | 0004aac84e0df4da2b147f | 18040 | sorocaba | SP | 5983 | 1900-01-01 | 9999-12-31 | True | 1 |
| 4 | 0005e1862207bf6ccc02e4 | 25966 | teresopolis | RJ | 7187 | 1900-01-01 | 9999-12-31 | True | 1 |
| 5 | 0006fdc98a402fceb4eb0e | 29400 | mimoso do sul | ES | 7937 | 1900-01-01 | 9999-12-31 | True | 1 |

### dw.dim_seller – 3,558 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Bang (23) → Thành phố (636) → Nhóm kênh (7) → Origin (11) → Seller (3,557)

| seller_key | seller_id | zip_code_prefix | city | state_code | geography_key | is_from_funnel | mql_id | acquisition_origin | acquisition_channel | business_segment | lead_type | business_type | won_date | first_sale_date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3442f8959a84dea7ee197c | 13023 | campinas | SP | 4811 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2017-05-05 |
| 2 | d1b65fc7debc3361ea86b5 | 13844 | mogi guacu | SP | 5210 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2017-03-28 |
| 3 | ce3ad9de960102d0677a81 | 20031 | rio de janeiro | RJ | 6354 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2018-07-30 |
| 4 | c0f3eea2e14555b6faeea3 | 04195 | sao paulo | SP | 1834 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2018-08-03 |
| 5 | 51a04a8a6bdcb23deccc82 | 12914 | braganca paulista | SP | 4773 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2017-11-14 |

### dw.dim_product – 32,952 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Nhóm ngành hàng (13) → Danh mục (74) → Sản phẩm (32,951)

| product_key | product_id | category_name_pt | category_name_en | category_group | weight_g | length_cm | height_cm | width_cm | volume_cm3 | size_class | photos_qty | name_length | description_length |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1e9e8ef04dbcff4541ed26 | perfumaria | perfumery | Health & Beauty | 225 | 16 | 10 | 14 | 2240 | S | 1 | 40 | 287 |
| 2 | 3aa071139cb16b67ca9e5d | artes | art | Gifts & Others | 1000 | 30 | 18 | 20 | 10800 | M | 1 | 44 | 276 |
| 3 | 96bd76ec8810374ed1b65e | esporte_lazer | sports_leisure | Sports & Leisure | 154 | 18 | 9 | 15 | 2430 | S | 1 | 46 | 250 |
| 4 | cef67bcfe19066a932b767 | bebes | baby | Toys & Baby | 371 | 26 | 4 | 26 | 2704 | S | 1 | 27 | 261 |
| 5 | 9dc1a7de274444849c219c | utilidades_domesticas | housewares | Home & Furniture | 625 | 20 | 17 | 13 | 4420 | M | 4 | 37 | 402 |

### dw.dim_order_status – 9 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Nhóm trạng thái (3) → Trạng thái (8)

| order_status_key | order_status | status_group | is_final |
| --- | --- | --- | --- |
| 1 | delivered | Completed | True |
| 2 | shipped | In progress | False |
| 3 | invoiced | In progress | False |
| 4 | processing | In progress | False |
| 5 | approved | In progress | False |

### dw.dim_payment_type – 6 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Nhóm (4) → Loại (5)

| payment_type_key | payment_type | payment_group | display_name |
| --- | --- | --- | --- |
| 1 | credit_card | Card | Credit card |
| 2 | debit_card | Card | Debit card |
| 3 | boleto | Bank slip | Boleto |
| 4 | voucher | Voucher | Voucher |
| 5 | not_defined | Unknown | Not defined |

### dw.dim_lead_origin – 11 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Nhóm kênh (6) → Origin (10)

| lead_origin_key | origin | channel_group |
| --- | --- | --- |
| 1 | organic_search | Organic |
| 2 | direct_traffic | Organic |
| 3 | referral | Organic |
| 4 | paid_search | Paid |
| 5 | display | Paid |

### dw.dim_lead_profile – 503 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Phân khúc (34) → Tổ hợp hồ sơ (502)

| lead_profile_key | business_segment | lead_type | lead_behaviour_profile | business_type | has_company | has_gtin | average_stock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | computers | offline | unknown | reseller | unknown | unknown | unknown |
| 2 | health_beauty | online_small | unknown | manufacturer | unknown | unknown | unknown |
| 3 | food_supplement | industry | unknown | manufacturer | unknown | unknown | unknown |
| 4 | fashion_accessories | online_medium | unknown | reseller | unknown | unknown | unknown |
| 5 | computers | online_big | unknown | reseller | unknown | unknown | unknown |

### dw.dim_sales_rep – 55 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Vai trò (2) → Nhân viên-vai trò (54)

| sales_rep_key | rep_id | rep_role |
| --- | --- | --- |
| 1 | c638112b43f1d1b86dcabb | SR |
| 2 | 060c0a26f19f4d66b42e0d | SR |
| 3 | 495d4e95a8cf8bbf8b432b | SR |
| 4 | 56bf83c4bb35763a51c2ba | SDR |
| 5 | 9ae085775a198122c5586f | SDR |

## Các fact: grain, số dòng, measure, tổng

| Fact | Loại | Grain | Số dòng | Measure chính |
| --- | --- | --- | ---: | --- |
| dw.fact_order_item | Transaction | 1 dòng sản phẩm trong 1 đơn | 112,650 | price, freight_value, item_total |
| dw.fact_order_fulfillment | Accumulating snapshot | 1 đơn hàng | 99,441 | approval_hours, handling_days, transit_days, lead_days, delay_days, promised_days, is_late, order_value |
| dw.fact_payment | Transaction | 1 lần thanh toán | 103,886 | payment_value, payment_installments |
| dw.fact_review | Transaction | 1 review của 1 đơn | 99,224 | review_score, is_negative, response_hours |
| dw.fact_lead_funnel | Accumulating snapshot | 1 MQL | 8,000 | is_won, has_first_sale, days_to_close, days_won_to_first_sale, seller_gmv_first_90d |
| dw.fact_seller_monthly | Periodic snapshot | 1 seller × 1 tháng (dày đặc) | 36,583 | orders, items, gmv, freight, late_rate, avg_review_score |

| Chỉ số | Giá trị |
| --- | ---: |
| Số đơn (fact_order_fulfillment) | 99,441 |
| Số dòng hàng (fact_order_item) | 112,650 |
| Tổng price, mọi đơn (BRL) | 13,591,643.70 |
| GMV = Σ price của đơn không thuộc nhóm Failed (BRL) | 13,494,400.74 |
| Tổng freight_value (BRL) | 2,251,909.54 |
| Tổng payment_value (BRL) | 16,008,872.12 |
| Số đơn đã giao / giao trễ | 96470 / 6534 |
| Số đơn bị hủy | 625 |
| Điểm review trung bình / % review tiêu cực | 4.09 / 14.7% |
| MQL / đã chốt (won) / seller đã có đơn | 8000 / 842 / 380 |
| Số seller trong fact_seller_monthly / số tháng | 3095 / 25 |
| Σ gmv của fact_seller_monthly (phải bằng GMV ở trên, giai đoạn có đơn) | 13,494,400.74 |

### Vấn đề ghi nhận khi nạp fact (từ lần nạp full gần nhất đến nay, cộng dồn các đợt, riêng fact_lead_funnel được tính lại mỗi đợt nên lấy giá trị lớn nhất; `etl_log.fact_load_issue`)

| Fact | Loại | Chi tiết | Số dòng |
| --- | --- | --- | ---: |
| fact_lead_funnel | negative_interval | days_to_close (won before first contact) | 1 |
| fact_order_fulfillment | negative_interval | handling_days | 1,359 |
| fact_order_fulfillment | negative_interval | transit_days | 23 |

### dw.fact_order_item – 5 dòng mẫu

| order_id | order_item_id | purchase_date_key | shipping_limit_date_key | customer_key | customer_geography_key | seller_geography_key | seller_key | product_key | order_status_key | price | freight_value | item_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 1 | 20170913 | 20170919 | 23284 | 7570 | 7453 | 514 | 25866 | 1 | 58.9 | 13.29 | 72.19 |
| 00018f77f2f0320c557190 | 1 | 20170426 | 20170503 | 40549 | 5642 | 1307 | 472 | 27231 | 1 | 239.9 | 19.93 | 259.83 |
| 000229ec398224ef6ca065 | 1 | 20180114 | 20180118 | 45642 | 8798 | 9349 | 1825 | 22625 | 1 | 199.0 | 17.87 | 216.87 |
| 00024acbcdf0a6daa1e931 | 1 | 20180808 | 20180815 | 94349 | 4797 | 5353 | 2024 | 15404 | 1 | 12.99 | 12.79 | 25.78 |
| 00042b26cf59d7ce69dfab | 1 | 20170204 | 20170213 | 17414 | 4934 | 17249 | 1598 | 8863 | 1 | 199.9 | 18.14 | 218.04 |

### dw.fact_order_fulfillment – 5 dòng mẫu

| order_id | customer_key | customer_geography_key | order_status_key | purchase_date_key | approved_date_key | carrier_date_key | delivered_date_key | estimated_date_key | purchase_ts | approved_ts | carrier_ts | delivered_ts | estimated_ts | approval_hours | handling_days | transit_days | lead_days | delay_days | promised_days | is_delivered | is_late | is_canceled | item_count | seller_count | order_value | freight_total | payment_total | dq_flag_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 23284 | 7570 | 1 | 20170913 | 20170913 | 20170919 | 20170920 | 20170929 | 2017-09-13 08:59:02 | 2017-09-13 09:45:35 | 2017-09-19 18:34:16 | 2017-09-20 23:43:48 | 2017-09-29 | 0.78 | 6.37 | 1.21 | 7.61 | -9 | 16 | 1 | 0 | 0 | 1 | 1 | 58.9 | 13.29 | 72.19 | 0 |
| 00018f77f2f0320c557190 | 40549 | 5642 | 1 | 20170426 | 20170426 | 20170504 | 20170512 | 20170515 | 2017-04-26 10:53:06 | 2017-04-26 11:05:13 | 2017-05-04 14:35:00 | 2017-05-12 16:04:24 | 2017-05-15 | 0.2 | 8.15 | 8.06 | 16.22 | -3 | 19 | 1 | 0 | 0 | 1 | 1 | 239.9 | 19.93 | 259.83 | 0 |
| 000229ec398224ef6ca065 | 45642 | 8798 | 1 | 20180114 | 20180114 | 20180116 | 20180122 | 20180205 | 2018-01-14 14:33:31 | 2018-01-14 14:48:30 | 2018-01-16 12:36:48 | 2018-01-22 13:19:16 | 2018-02-05 | 0.25 | 1.91 | 6.03 | 7.95 | -14 | 22 | 1 | 0 | 0 | 1 | 1 | 199.0 | 17.87 | 216.87 | 0 |
| 00024acbcdf0a6daa1e931 | 94349 | 4797 | 1 | 20180808 | 20180808 | 20180810 | 20180814 | 20180820 | 2018-08-08 10:00:35 | 2018-08-08 10:10:18 | 2018-08-10 13:28:00 | 2018-08-14 13:32:39 | 2018-08-20 | 0.16 | 2.14 | 4.0 | 6.15 | -6 | 12 | 1 | 0 | 0 | 1 | 1 | 12.99 | 12.79 | 25.78 | 0 |
| 00042b26cf59d7ce69dfab | 17414 | 4934 | 1 | 20170204 | 20170204 | 20170216 | 20170301 | 20170317 | 2017-02-04 13:57:51 | 2017-02-04 14:10:13 | 2017-02-16 09:46:09 | 2017-03-01 16:42:31 | 2017-03-17 | 0.21 | 11.82 | 13.29 | 25.11 | -16 | 41 | 1 | 0 | 0 | 1 | 1 | 199.9 | 18.14 | 218.04 | 0 |

### dw.fact_payment – 5 dòng mẫu

| order_id | payment_sequential | purchase_date_key | customer_key | payment_type_key | payment_installments | payment_value |
| --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 1 | 20170913 | 23284 | 1 | 2 | 72.19 |
| 00018f77f2f0320c557190 | 1 | 20170426 | 40549 | 1 | 3 | 259.83 |
| 000229ec398224ef6ca065 | 1 | 20180114 | 45642 | 1 | 5 | 216.87 |
| 00024acbcdf0a6daa1e931 | 1 | 20180808 | 94349 | 1 | 2 | 25.78 |
| 00042b26cf59d7ce69dfab | 1 | 20170204 | 17414 | 1 | 3 | 218.04 |

### dw.fact_review – 5 dòng mẫu

| review_id | order_id | review_creation_date_key | review_answer_date_key | customer_key | review_score | is_negative | has_comment_title | has_comment_message | comment_length | response_hours | delivered_late |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0001239bc1de2e33cb5839 | fc046d7776171871436844 | 20180320 | 20180320 | 53172 | 5 | 0 | 0 | 0 | 0 | 18.6 | 0 |
| 0001cc6860aeaf5b9017fe | d4665434b01caa9dc3e3e7 | 20180622 | 20180626 | 79393 | 5 | 0 | 0 | 0 | 0 | 109.86 | 0 |
| 00020c7512a52e92212f12 | e28abf2eb2f1fbcbdc2dd0 | 20180425 | 20180426 | 71129 | 5 | 0 | 1 | 1 | 68 | 38.93 | 0 |
| 00032b0141443497c898b3 | 04fb47576993a3cb0c12d4 | 20170530 | 20170601 | 38566 | 5 | 0 | 0 | 0 | 0 | 71.48 | 0 |
| 00034d88989f9a4c393bdc | 5f358d797a49fe2f24352f | 20170812 | 20170813 | 3831 | 5 | 0 | 0 | 0 | 0 | 43.95 | 0 |

### dw.fact_lead_funnel – 5 dòng mẫu

| mql_id | landing_page_id | first_contact_date_key | won_date_key | first_sale_date_key | lead_origin_key | lead_profile_key | seller_key | sdr_key | sr_key | is_won | has_first_sale | days_to_close | days_won_to_first_sale | declared_product_catalog_size | declared_monthly_revenue | seller_gmv_first_90d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0002ac0d783338cfeab0b2 | b76ef37428e6799c421989 | 20171114 | -1 | -1 | 10 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 000dd3543ac84d906eae52 | b48ec5f3b04e9068441002 | 20180405 | 20180424 | -1 | 1 | 607 | 15943 | 24 | 87 | 1 | 0 | 19.0 | NULL | NULL | 0.0 | NULL |
| 001d3439223b7bb23ed89b | 35c9b150ab36fe584c1f24 | 20180414 | -1 | -1 | 4 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 00275937100699204a3d5a | a7982125ff7aa3b2054c6e | 20180111 | -1 | -1 | 1 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 003d859bbd84a526b9e063 | 22c29808c4f815213303f8 | 20180402 | -1 | -1 | 2 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |

### dw.fact_seller_monthly – 5 dòng mẫu

| month_date_key | seller_key | orders | items | gmv | freight | delivered_orders | late_orders | late_rate | canceled_orders | avg_review_score | is_active | months_since_first_sale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20160901 | 524 | 1 | 2 | 72.89 | 63.34 | 0 | 0 | NULL | 0 | 1.0 | 1 | 0 |
| 20160901 | 1717 | 1 | 3 | 134.97 | 8.49 | 1 | 1 | 1.0 | 0 | 1.0 | 1 | 0 |
| 20160901 | 2041 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | NULL | 1 | 1.0 | 1 | 0 |
| 20161001 | 23 | 1 | 1 | 119.99 | 29.4 | 1 | 0 | 0.0 | 0 | 5.0 | 1 | 0 |
| 20161001 | 56 | 2 | 2 | 72.8 | 30.57 | 2 | 0 | 0.0 | 0 | 4.5 | 1 | 0 |

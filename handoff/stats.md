# Thống kê dữ liệu (sinh tự động 2026-11-05 18:57)

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
| oltp.customers | 45,430 | 5 | 12.10 MB |
| oltp.orders | 45,430 | 8 | 14.84 MB |
| oltp.order_items | 51,234 | 7 | 13.41 MB |
| oltp.order_payments | 47,871 | 5 | 7.84 MB |
| oltp.order_reviews | 45,370 | 7 | 15.20 MB |
| crm.mql | 2,002 | 4 | 440.0 KB |
| crm.closed_deals | 3 | 14 | 48.0 KB |
| **Tổng (11 bảng)** | **1,273,620** | **71** | |

- Dung lượng cả database: **517.11 MB**
- Số dòng trong etl_log.rejected_rows: **588**

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
| crm | closed_deals | 3 |
| crm | mql | 2,002 |
| dw | dim_customer | 44,118 |
| dw | dim_date | 1,462 |
| dw | dim_geography | 19,108 |
| dw | dim_lead_origin | 11 |
| dw | dim_lead_profile | 4 |
| dw | dim_order_status | 9 |
| dw | dim_payment_type | 6 |
| dw | dim_product | 32,952 |
| dw | dim_sales_rep | 7 |
| dw | dim_seller | 3,098 |
| dw | fact_lead_funnel | 2,002 |
| dw | fact_order_fulfillment | 45,430 |
| dw | fact_order_item | 51,234 |
| dw | fact_payment | 47,871 |
| dw | fact_review | 45,370 |
| dw | fact_seller_monthly | 13,548 |
| etl_log | dq_check | 945 |
| etl_log | fact_load_issue | 12 |
| etl_log | job_run | 779 |
| etl_log | rejected_rows | 588 |
| etl_log | watermark | 3 |
| ods | category_translation | 71 |
| ods | closed_deals | 3 |
| ods | customer_map | 45,430 |
| ods | customers | 45,430 |
| ods | geolocation_zip | 19,015 |
| ods | mql | 2,002 |
| ods | order_items | 51,234 |
| ods | order_payments | 47,871 |
| ods | order_reviews | 45,370 |
| ods | orders | 45,430 |
| ods | products | 32,951 |
| ods | ref_category_group | 74 |
| ods | ref_category_translation_extra | 2 |
| ods | ref_lead_origin_group | 10 |
| ods | ref_order_status | 8 |
| ods | ref_payment_type | 5 |
| ods | ref_state_region | 27 |
| ods | sellers | 3,095 |
| oltp | customers | 45,430 |
| oltp | geolocation | 1,000,163 |
| oltp | order_items | 51,234 |
| oltp | order_payments | 47,871 |
| oltp | order_reviews | 45,370 |
| oltp | orders | 45,430 |
| oltp | product_category_name_translation | 71 |
| oltp | products | 32,951 |
| oltp | sellers | 3,095 |
| staging | stg_closed_deals | 3 |
| staging | stg_customers | 45,430 |
| staging | stg_geolocation | 1,000,163 |
| staging | stg_mql | 2,002 |
| staging | stg_order_items | 51,234 |
| staging | stg_order_payments | 47,871 |
| staging | stg_order_reviews | 45,370 |
| staging | stg_orders | 45,430 |
| staging | stg_product_category_name_translation | 71 |
| staging | stg_products | 32,951 |
| staging | stg_sellers | 3,095 |

## Các dimension: số bản ghi, 5 dòng mẫu, phân cấp

### dw.dim_date – 1,462 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Năm (4) → Quý (16) → Tháng (48) → Ngày (1,461)

| date_key | full_date | day_of_month | day_of_week | day_name | week_of_year | month | month_name | quarter | year | year_month | year_quarter | is_weekend | is_holiday_br | holiday_name | is_black_friday |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20160101 | 2016-01-01 | 1 | 5 | Friday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | True | Confraternização Unive | False |
| 20160102 | 2016-01-02 | 2 | 6 | Saturday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | True | False | NULL | False |
| 20160103 | 2016-01-03 | 3 | 7 | Sunday | 53 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | True | False | NULL | False |
| 20160104 | 2016-01-04 | 4 | 1 | Monday | 1 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | False | NULL | False |
| 20160105 | 2016-01-05 | 5 | 2 | Tuesday | 1 | 1 | January | 1 | 2016 | 2016-01 | 2016-Q1 | False | False | NULL | False |

### dw.dim_geography – 19,108 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Vùng (5) → Bang (27) → Thành phố (6,165) → Zip (19,107)

| geography_key | zip_code_prefix | city | state_code | state_name | region | country | latitude | longitude |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 01001 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.550380539269455 | -46.63402699777831 |
| 2 | 01002 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.548551065785627 | -46.63507239078997 |
| 3 | 01003 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.54897652899767 | -46.63531311226845 |
| 4 | 01004 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.549534948092827 | -46.634770582289825 |
| 5 | 01005 | sao paulo | SP | São Paulo | Sudeste | Brazil | -23.54961248124544 | -46.63653202553522 |

### dw.dim_customer – 44,118 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Bang (27) → Thành phố (3,414) → Khách thật (44,034) → Phiên bản (SCD2) (44,117)

| customer_key | customer_unique_id | zip_code_prefix | city | state_code | geography_key | effective_from | effective_to | is_current | version_no |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0000f46a3911fa3c080544 | 88115 | sao jose | SC | 17310 | 1900-01-01 | 9999-12-31 | True | 1 |
| 2 | 0000f6ccb0745a6a4b8866 | 66812 | belem | PA | 13649 | 1900-01-01 | 9999-12-31 | True | 1 |
| 3 | 0004aac84e0df4da2b147f | 18040 | sorocaba | SP | 5983 | 1900-01-01 | 9999-12-31 | True | 1 |
| 4 | 0005e1862207bf6ccc02e4 | 25966 | teresopolis | RJ | 7187 | 1900-01-01 | 9999-12-31 | True | 1 |
| 5 | 0006fdc98a402fceb4eb0e | 29400 | mimoso do sul | ES | 7937 | 1900-01-01 | 9999-12-31 | True | 1 |

### dw.dim_seller – 3,098 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Bang (23) → Thành phố (636) → Nhóm kênh (2) → Origin (3) → Seller (3,097)

| seller_key | seller_id | zip_code_prefix | city | state_code | geography_key | is_from_funnel | mql_id | acquisition_origin | acquisition_channel | business_segment | lead_type | business_type | won_date | first_sale_date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3442f8959a84dea7ee197c | 13023 | campinas | SP | 4811 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2017-05-05 |
| 2 | d1b65fc7debc3361ea86b5 | 13844 | mogi guacu | SP | 5210 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | 2017-03-28 |
| 3 | ce3ad9de960102d0677a81 | 20031 | rio de janeiro | RJ | 6354 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
| 4 | c0f3eea2e14555b6faeea3 | 04195 | sao paulo | SP | 1834 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
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

### dw.dim_lead_profile – 4 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Phân khúc (3) → Tổ hợp hồ sơ (3)

| lead_profile_key | business_segment | lead_type | lead_behaviour_profile | business_type | has_company | has_gtin | average_stock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | computers | offline | unknown | reseller | unknown | unknown | unknown |
| 2 | health_beauty | online_small | unknown | manufacturer | unknown | unknown | unknown |
| 3 | food_supplement | industry | unknown | manufacturer | unknown | unknown | unknown |

### dw.dim_sales_rep – 7 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Vai trò (2) → Nhân viên-vai trò (6)

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
| dw.fact_order_item | Transaction | 1 dòng sản phẩm trong 1 đơn | 51,234 | price, freight_value, item_total |
| dw.fact_order_fulfillment | Accumulating snapshot | 1 đơn hàng | 45,430 | approval_hours, handling_days, transit_days, lead_days, delay_days, promised_days, is_late, order_value |
| dw.fact_payment | Transaction | 1 lần thanh toán | 47,871 | payment_value, payment_installments |
| dw.fact_review | Transaction | 1 review của 1 đơn | 45,370 | review_score, is_negative, response_hours |
| dw.fact_lead_funnel | Accumulating snapshot | 1 MQL | 2,002 | is_won, has_first_sale, days_to_close, days_won_to_first_sale, seller_gmv_first_90d |
| dw.fact_seller_monthly | Periodic snapshot | 1 seller × 1 tháng (dày đặc) | 13,548 | orders, items, gmv, freight, late_rate, avg_review_score |

| Chỉ số | Giá trị |
| --- | ---: |
| Số đơn (fact_order_fulfillment) | 45,430 |
| Số dòng hàng (fact_order_item) | 51,234 |
| Tổng price, mọi đơn (BRL) | 6,205,592.90 |
| GMV = Σ price của đơn không thuộc nhóm Failed (BRL) | 6,153,218.33 |
| Tổng freight_value (BRL) | 994,262.74 |
| Tổng payment_value (BRL) | 7,309,109.07 |
| Số đơn đã giao / giao trễ | 43693 / 2456 |
| Số đơn bị hủy | 291 |
| Điểm review trung bình / % review tiêu cực | 4.08 / 14.6% |
| MQL / đã chốt (won) / seller đã có đơn | 2002 / 3 / 0 |
| Số seller trong fact_seller_monthly / số tháng | 1811 / 16 |
| Σ gmv của fact_seller_monthly (phải bằng GMV ở trên, giai đoạn có đơn) | 6,153,218.33 |

### Vấn đề ghi nhận khi nạp fact (lô gần nhất, `etl_log.fact_load_issue`)

| Fact | Loại | Chi tiết | Số dòng |
| --- | --- | --- | ---: |
| fact_order_fulfillment | negative_interval | handling_days | 84 |
| fact_order_fulfillment | negative_interval | transit_days | 23 |
| fact_order_item | unknown_member | shipping_limit_date_key | 4 |

### dw.fact_order_item – 5 dòng mẫu

| order_id | order_item_id | purchase_date_key | shipping_limit_date_key | customer_key | customer_geography_key | seller_geography_key | seller_key | product_key | order_status_key | price | freight_value | item_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 1 | 20170913 | 20170919 | 23284 | 7570 | 7453 | 514 | 25866 | 1 | 58.9 | 13.29 | 72.19 |
| 00018f77f2f0320c557190 | 1 | 20170426 | 20170503 | 40549 | 5642 | 1307 | 472 | 27231 | 1 | 239.9 | 19.93 | 259.83 |
| 00042b26cf59d7ce69dfab | 1 | 20170204 | 20170213 | 17414 | 4934 | 17249 | 1598 | 8863 | 1 | 199.9 | 18.14 | 218.04 |
| 00048cc3ae777c65dbb7d2 | 1 | 20170515 | 20170523 | 23072 | 9448 | 5303 | 660 | 3940 | 1 | 21.9 | 12.69 | 34.59 |
| 00054e8431b9d7675808bc | 1 | 20171210 | 20171214 | 17189 | 5780 | 26 | 2974 | 22293 | 1 | 19.9 | 11.85 | 31.75 |

### dw.fact_order_fulfillment – 5 dòng mẫu

| order_id | customer_key | customer_geography_key | order_status_key | purchase_date_key | approved_date_key | carrier_date_key | delivered_date_key | estimated_date_key | purchase_ts | approved_ts | carrier_ts | delivered_ts | estimated_ts | approval_hours | handling_days | transit_days | lead_days | delay_days | promised_days | is_delivered | is_late | is_canceled | item_count | seller_count | order_value | freight_total | payment_total | dq_flag_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 23284 | 7570 | 1 | 20170913 | 20170913 | 20170919 | 20170920 | 20170929 | 2017-09-13 08:59:02 | 2017-09-13 09:45:35 | 2017-09-19 18:34:16 | 2017-09-20 23:43:48 | 2017-09-29 | 0.78 | 6.37 | 1.21 | 7.61 | -9 | 16 | 1 | 0 | 0 | 1 | 1 | 58.9 | 13.29 | 72.19 | 0 |
| 00018f77f2f0320c557190 | 40549 | 5642 | 1 | 20170426 | 20170426 | 20170504 | 20170512 | 20170515 | 2017-04-26 10:53:06 | 2017-04-26 11:05:13 | 2017-05-04 14:35:00 | 2017-05-12 16:04:24 | 2017-05-15 | 0.2 | 8.15 | 8.06 | 16.22 | -3 | 19 | 1 | 0 | 0 | 1 | 1 | 239.9 | 19.93 | 259.83 | 0 |
| 00042b26cf59d7ce69dfab | 17414 | 4934 | 1 | 20170204 | 20170204 | 20170216 | 20170301 | 20170317 | 2017-02-04 13:57:51 | 2017-02-04 14:10:13 | 2017-02-16 09:46:09 | 2017-03-01 16:42:31 | 2017-03-17 | 0.21 | 11.82 | 13.29 | 25.11 | -16 | 41 | 1 | 0 | 0 | 1 | 1 | 199.9 | 18.14 | 218.04 | 0 |
| 00048cc3ae777c65dbb7d2 | 23072 | 9448 | 1 | 20170515 | 20170517 | 20170517 | 20170522 | 20170606 | 2017-05-15 21:42:34 | 2017-05-17 03:55:27 | 2017-05-17 11:05:55 | 2017-05-22 13:44:35 | 2017-06-06 | 30.21 | 0.3 | 5.11 | 6.67 | -15 | 22 | 1 | 0 | 0 | 1 | 1 | 21.9 | 12.69 | 34.59 | 0 |
| 00054e8431b9d7675808bc | 17189 | 5780 | 1 | 20171210 | 20171210 | 20171212 | 20171218 | 20180104 | 2017-12-10 11:53:48 | 2017-12-10 12:10:31 | 2017-12-12 01:07:48 | 2017-12-18 22:03:38 | 2018-01-04 | 0.28 | 1.54 | 6.87 | 8.42 | -17 | 25 | 1 | 0 | 0 | 1 | 1 | 19.9 | 11.85 | 31.75 | 0 |

### dw.fact_payment – 5 dòng mẫu

| order_id | payment_sequential | purchase_date_key | customer_key | payment_type_key | payment_installments | payment_value |
| --- | --- | --- | --- | --- | --- | --- |
| 00010242fe8c5a6d1ba2dd | 1 | 20170913 | 23284 | 1 | 2 | 72.19 |
| 00018f77f2f0320c557190 | 1 | 20170426 | 40549 | 1 | 3 | 259.83 |
| 00042b26cf59d7ce69dfab | 1 | 20170204 | 17414 | 1 | 3 | 218.04 |
| 00048cc3ae777c65dbb7d2 | 1 | 20170515 | 23072 | 3 | 1 | 34.59 |
| 00054e8431b9d7675808bc | 1 | 20171210 | 17189 | 1 | 1 | 31.75 |

### dw.fact_review – 5 dòng mẫu

| review_id | order_id | review_creation_date_key | review_answer_date_key | customer_key | review_score | is_negative | has_comment_title | has_comment_message | comment_length | response_hours | delivered_late |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00032b0141443497c898b3 | 04fb47576993a3cb0c12d4 | 20170530 | 20170601 | 38566 | 5 | 0 | 0 | 0 | 0 | 71.48 | 0 |
| 00034d88989f9a4c393bdc | 5f358d797a49fe2f24352f | 20170812 | 20170813 | 3831 | 5 | 0 | 0 | 0 | 0 | 43.95 | 0 |
| 0005534973388c830bb858 | a589caa6892ceacc6bbf2f | 20170901 | 20170902 | 15438 | 5 | 0 | 0 | 1 | 54 | 37.07 | 0 |
| 00055e36e9608fe969231e | f5fea26ab547eec920e6f8 | 20171125 | 20171127 | 12734 | 5 | 0 | 0 | 1 | 64 | 59.62 | 0 |
| 0005949d4c047d64863a68 | 640883769bc5da4a077725 | 20170620 | 20170622 | 42143 | 5 | 0 | 0 | 1 | 53 | 71.33 | 0 |

### dw.fact_lead_funnel – 5 dòng mẫu

| mql_id | landing_page_id | first_contact_date_key | won_date_key | first_sale_date_key | lead_origin_key | lead_profile_key | seller_key | sdr_key | sr_key | is_won | has_first_sale | days_to_close | days_won_to_first_sale | declared_product_catalog_size | declared_monthly_revenue | seller_gmv_first_90d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0002ac0d783338cfeab0b2 | b76ef37428e6799c421989 | 20171114 | -1 | -1 | 10 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 005b0c27e7224dabb8c1c7 | 298895230612f85f074243 | 20170914 | -1 | -1 | 8 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 007491783420080b256392 | 0f25be78376bbbaba85530 | 20170829 | -1 | -1 | 1 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 00c37b7a1f13daf967813d | 007f9098284a86ee80ddeb | 20171006 | -1 | -1 | 4 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |
| 00f42382da08bb47df2585 | 128d8c3f32b8aa66b5bcbe | 20170817 | -1 | -1 | 1 | -1 | -1 | -1 | -1 | 0 | 0 | NULL | NULL | NULL | NULL | NULL |

### dw.fact_seller_monthly – 5 dòng mẫu

| month_date_key | seller_key | orders | items | gmv | freight | delivered_orders | late_orders | late_rate | canceled_orders | avg_review_score | is_active | months_since_first_sale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20160901 | 524 | 1 | 2 | 72.89 | 63.34 | 0 | 0 | NULL | 0 | 1.0 | 1 | 0 |
| 20160901 | 1717 | 1 | 3 | 134.97 | 8.49 | 1 | 1 | 1.0 | 0 | 1.0 | 1 | 0 |
| 20160901 | 2041 | 1 | 1 | 0.0 | 0.0 | 0 | 0 | NULL | 1 | 1.0 | 1 | 0 |
| 20161001 | 23 | 1 | 1 | 119.99 | 29.4 | 1 | 0 | 0.0 | 0 | 5.0 | 1 | 0 |
| 20161001 | 56 | 2 | 2 | 72.8 | 30.57 | 2 | 0 | 0.0 | 0 | 4.5 | 1 | 0 |

# Thống kê dữ liệu (sinh tự động 2026-11-05 15:38)

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

- Dung lượng cả database: **454.81 MB**
- Số dòng trong etl_log.rejected_rows: **378**

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
| dw | dim_geography | 19,103 |
| dw | dim_lead_origin | 11 |
| dw | dim_lead_profile | 4 |
| dw | dim_order_status | 9 |
| dw | dim_payment_type | 6 |
| dw | dim_product | 32,952 |
| dw | dim_sales_rep | 7 |
| dw | dim_seller | 3,098 |
| etl_log | dq_check | 546 |
| etl_log | job_run | 510 |
| etl_log | rejected_rows | 378 |
| etl_log | watermark | 3 |
| ods | category_translation | 71 |
| ods | closed_deals | 3 |
| ods | customer_map | 45,430 |
| ods | customers | 45,430 |
| ods | geolocation_zip | 19,010 |
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

### dw.dim_geography – 19,103 dòng (gồm dòng Unknown key −1)

Phân cấp / số phần tử: Vùng (5) → Bang (27) → Thành phố (6,161) → Zip (19,102)

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
| 1 | 3442f8959a84dea7ee197c | 13023 | campinas | SP | 4811 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
| 2 | d1b65fc7debc3361ea86b5 | 13844 | mogi guacu | SP | 5210 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
| 3 | ce3ad9de960102d0677a81 | 20031 | rio de janeiro | RJ | 6354 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
| 4 | c0f3eea2e14555b6faeea3 | 04195 | sao paulo | SP | 1834 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |
| 5 | 51a04a8a6bdcb23deccc82 | 12914 | braganca paulista | SP | 4773 | False | NULL | not_from_funnel | Not from funnel | NULL | NULL | NULL | NULL | NULL |

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

# Thống kê dữ liệu (sinh tự động 2026-11-05 14:34)

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
| oltp.products | 32,951 | 9 | 6.30 MB |
| oltp.sellers | 3,095 | 4 | 616.0 KB |
| oltp.geolocation | 1,000,163 | 6 | 106.24 MB |
| oltp.customers | 45,430 | 5 | 12.07 MB |
| oltp.orders | 45,430 | 8 | 14.81 MB |
| oltp.order_items | 51,234 | 7 | 13.38 MB |
| oltp.order_payments | 47,871 | 5 | 7.81 MB |
| oltp.order_reviews | 45,370 | 7 | 15.16 MB |
| crm.mql | 2,002 | 4 | 528.0 KB |
| crm.closed_deals | 3 | 14 | 48.0 KB |
| **Tổng (11 bảng)** | **1,273,620** | **71** | |

- Dung lượng cả database: **185.14 MB**
- Số dòng trong etl_log.rejected_rows: **0**

### Database `olist_full`

| Bảng | Số dòng | Số cột | Dung lượng (gồm index) |
| --- | ---: | ---: | ---: |
| oltp.product_category_name_translation | 71 | 2 | 32.0 KB |
| oltp.products | 32,951 | 9 | 6.30 MB |
| oltp.sellers | 3,095 | 4 | 616.0 KB |
| oltp.geolocation | 1,000,163 | 6 | 106.24 MB |
| oltp.customers | 99,441 | 5 | 26.49 MB |
| oltp.orders | 99,441 | 8 | 31.95 MB |
| oltp.order_items | 112,650 | 7 | 29.16 MB |
| oltp.order_payments | 103,886 | 5 | 16.98 MB |
| oltp.order_reviews | 99,224 | 7 | 33.81 MB |
| crm.mql | 8,000 | 4 | 1.80 MB |
| crm.closed_deals | 842 | 14 | 504.0 KB |
| **Tổng (11 bảng)** | **1,559,764** | **71** | |

- Dung lượng cả database: **262.01 MB**
- Số dòng trong etl_log.rejected_rows: **0**

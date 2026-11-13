# 06 – Từ điển dữ liệu nguồn (11 bảng oltp và crm)

> Sinh tự động bởi `python scripts/eda/p8_dictionary.py` trên database `olist_full`; mapping lấy từ `docs/mapping.csv`. Từ điển các bảng của kho (`dw`, `mart_*`) nằm ở [`03-tu-dien-du-lieu.md`](03-tu-dien-du-lieu.md).

Cột *Miền giá trị*: khoảng min–max với cột số và ngày; với cột chữ là số giá trị phân biệt và, nếu ít, danh sách giá trị. *% rỗng* là tỷ lệ NULL hoặc chuỗi rỗng. *Vai trò trong DW* là cột đích của dimension hoặc fact; "không dùng" nghĩa là cột không đi sang kho.

## `crm.closed_deals` (842 dòng, 14 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `mql_id` | char | 842 giá trị phân biệt (ví dụ 5420aad7fec354…) | 0,0% | dim_seller.is_from_funnel, fact_lead_funnel.is_won |
| `seller_id` | char | 842 giá trị phân biệt (ví dụ 2c43fb513632d2…) | 0,0% | dim_seller.seller_id, fact_lead_funnel.seller_key |
| `sdr_id` | char | 32 giá trị phân biệt (ví dụ a8387c01a09e99…) | 0,0% | fact_lead_funnel.sdr_key |
| `sr_id` | char | 22 giá trị phân biệt (ví dụ 4ef15afb4b2723…) | 0,0% | fact_lead_funnel.sdr_key |
| `won_date` | timestamp | 2017-12-05 … 2018-11-14 | 0,0% | dim_seller.won_date, fact_lead_funnel.days_to_close, fact_lead_funnel.days_won_to_first_sale, fact_lead_funnel.won_date_key |
| `business_segment` | text | 33 giá trị phân biệt (ví dụ pet) | 0,1% | dim_seller.business_segment, dim_lead_profile (junk dimension, 7 thuộc tính) |
| `lead_type` | text | 8 giá trị: online_medium; online_big; industry; offline; online_small; online_beginner; online_top; nan; other | 0,7% | dim_seller.business_segment, dim_lead_profile (junk dimension, 7 thuộc tính) |
| `lead_behaviour_profile` | text | 9 giá trị: cat; nan; eagle; wolf; shark; cat, wolf; eagle, wolf; eagle, cat; shark, wolf; shark, cat | 21,0% | dim_lead_profile (junk dimension, 7 thuộc tính) |
| `has_company` | boolean | 2 giá trị: nan; true; false | 92,5% | dim_lead_profile (junk dimension, 7 thuộc tính) |
| `has_gtin` | boolean | 2 giá trị: nan; true; false | 92,4% | dim_lead_profile (junk dimension, 7 thuộc tính) |
| `average_stock` | text | 6 giá trị: nan; 5-20; 50-200; 1-5; 20-50; 200+; unknown | 92,2% | dim_lead_profile (junk dimension, 7 thuộc tính) |
| `business_type` | text | 3 giá trị: reseller; manufacturer; nan; other | 1,2% | dim_seller.business_segment, dim_lead_profile (junk dimension, 7 thuộc tính) |
| `declared_product_catalog_size` | numeric | 1 … 2000 | 91,8% | không dùng |
| `declared_monthly_revenue` | numeric | 0 … 5e+07 | 0,0% | không dùng |

## `crm.mql` (8.000 dòng, 4 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `mql_id` | char | 8.000 giá trị phân biệt (ví dụ dac32acd4db4c2…) | 0,0% | fact_lead_funnel.mql_id |
| `first_contact_date` | date | 2017-06-14 … 2018-05-31 | 0,0% | fact_lead_funnel.days_to_close, fact_lead_funnel.first_contact_date_key |
| `landing_page_id` | char | 495 giá trị phân biệt (ví dụ 88740e65d5d6b0…) | 0,0% | fact_lead_funnel.mql_id |
| `origin` | text | 10 giá trị: organic_search; paid_search; social; unknown; direct_traffic; email; referral; other; display; other_publicities; nan | 0,8% | dim_seller.acquisition_origin, fact_lead_funnel.lead_origin_key |

## `oltp.customers` (99.441 dòng, 5 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `customer_id` | char | 99.441 giá trị phân biệt (ví dụ 06b8999e2fba1a…) | 0,0% | không dùng |
| `customer_unique_id` | char | 96.096 giá trị phân biệt (ví dụ 861eff4711a542…) | 0,0% | không dùng |
| `customer_zip_code_prefix` | text | 14.994 giá trị phân biệt (ví dụ 14409) | 0,0% | dim_customer.zip_code_prefix, dim_geography.zip_code_prefix |
| `customer_city` | text | 4.119 giá trị phân biệt (ví dụ franca) | 0,0% | dim_customer.zip_code_prefix, dim_geography.city |
| `customer_state` | text | 27 giá trị phân biệt (ví dụ SP) | 0,0% | dim_customer.zip_code_prefix, dim_geography.city |

## `oltp.geolocation` (1.000.163 dòng, 6 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `id` | bigint | 1 … 1000163 | 0,0% | không dùng |
| `geolocation_zip_code_prefix` | text | 19.015 giá trị phân biệt (ví dụ 01037) | 0,0% | dim_geography.zip_code_prefix |
| `geolocation_lat` | double | -36.61 … 45.0659 | 0,0% | dim_geography.latitude |
| `geolocation_lng` | double | -101.5 … 121.105 | 0,0% | dim_geography.latitude |
| `geolocation_city` | text | 8.011 giá trị phân biệt (ví dụ sao paulo) | 0,0% | dim_geography.city |
| `geolocation_state` | text | 27 giá trị phân biệt (ví dụ SP) | 0,0% | dim_geography.city |

## `oltp.order_items` (112.650 dòng, 7 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `order_id` | char | 98.666 giá trị phân biệt (ví dụ 00010242fe8c5a…) | 0,0% | fact_order_item.order_id |
| `order_item_id` | int | 1 … 21 | 0,0% | fact_order_fulfillment.item_count, fact_order_item.order_id |
| `product_id` | char | 32.951 giá trị phân biệt (ví dụ 4244733e06e7ec…) | 0,0% | khoá tra cứu dim_product |
| `seller_id` | char | 3.095 giá trị phân biệt (ví dụ 48436dade18ac8…) | 0,0% | fact_order_fulfillment.item_count |
| `shipping_limit_date` | timestamp | 2016-09-19 … 2020-04-09 | 0,0% | fact_order_item.shipping_limit_date_key |
| `price` | numeric | 0.85 … 6735 | 0,0% | fact_order_fulfillment.order_value, fact_order_item.item_total, fact_order_item.price |
| `freight_value` | numeric | 0 … 409.68 | 0,0% | fact_order_fulfillment.order_value, fact_order_item.item_total, fact_order_item.price |

## `oltp.order_payments` (103.886 dòng, 5 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `order_id` | char | 99.440 giá trị phân biệt (ví dụ b81ef226f3fe17…) | 0,0% | fact_payment.order_id |
| `payment_sequential` | int | 1 … 29 | 0,0% | fact_payment.order_id |
| `payment_type` | text | 5 giá trị: credit_card; boleto; voucher; debit_card; not_defined | 0,0% | fact_payment.payment_type_key |
| `payment_installments` | int | 0 … 24 | 0,0% | fact_payment.payment_installments |
| `payment_value` | numeric | 0 … 13664.1 | 0,0% | fact_order_fulfillment.payment_total, fact_payment.payment_installments |

## `oltp.order_reviews` (99.224 dòng, 7 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `review_id` | char | 98.410 giá trị phân biệt (ví dụ 7bc2406110b926…) | 0,0% | fact_review.review_id |
| `order_id` | char | 98.673 giá trị phân biệt (ví dụ 73fc7af87114b3…) | 0,0% | fact_review.review_id |
| `review_score` | smallint | 1 … 5 | 0,0% | fact_review.is_negative, fact_review.review_score |
| `review_comment_title` | text | 4.527 giá trị phân biệt (ví dụ recomendo) | 88,3% | fact_review.has_comment_title |
| `review_comment_message` | text | 36.159 giá trị phân biệt (ví dụ Recebi bem ant…) | 58,7% | fact_review.comment_length, fact_review.has_comment_title |
| `review_creation_date` | timestamp | 2016-10-02 … 2018-08-31 | 0,0% | fact_review.review_creation_date_key |
| `review_answer_timestamp` | timestamp | 2016-10-07 … 2018-10-29 | 0,0% | fact_review.review_creation_date_key |

## `oltp.orders` (99.441 dòng, 8 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `order_id` | char | 99.441 giá trị phân biệt (ví dụ e481f51cbdc546…) | 0,0% | fact_order_fulfillment.order_id |
| `customer_id` | char | 99.441 giá trị phân biệt (ví dụ 9ef432eb625129…) | 0,0% | fact_order_fulfillment.customer_key, fact_order_item.customer_key, fact_payment.customer_key, fact_review.customer_key |
| `order_status` | text | 8 giá trị: delivered; shipped; canceled; unavailable; invoiced; processing; created; approved | 0,0% | fact_order_fulfillment.is_canceled, fact_order_fulfillment.is_delivered, fact_order_fulfillment.order_status_key, fact_order_item.order_status_key |
| `order_purchase_timestamp` | timestamp | 2016-09-04 … 2018-10-17 | 0,0% | dim_customer.effective_from, fact_order_fulfillment.promised_days, fact_order_fulfillment.purchase_date_key, fact_order_item.purchase_date_key, fact_payment.purchase_date_key |
| `order_approved_at` | timestamp | 2016-09-15 … 2018-09-03 | 0,2% | fact_order_fulfillment.purchase_date_key |
| `order_delivered_carrier_date` | timestamp | 2016-10-08 … 2018-09-11 | 1,8% | fact_order_fulfillment.purchase_date_key |
| `order_delivered_customer_date` | timestamp | 2016-10-11 … 2018-10-17 | 3,0% | fact_order_fulfillment.delay_days, fact_order_fulfillment.is_delivered, fact_order_fulfillment.purchase_date_key |
| `order_estimated_delivery_date` | timestamp | 2016-09-30 … 2018-11-12 | 0,0% | fact_order_fulfillment.delay_days, fact_order_fulfillment.promised_days, fact_order_fulfillment.purchase_date_key |

## `oltp.product_category_name_translation` (71 dòng, 2 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `product_category_name` | text | 71 giá trị phân biệt (ví dụ beleza_saude) | 0,0% | khoá tra bản dịch danh mục (dim_product) |
| `product_category_name_english` | text | 71 giá trị phân biệt (ví dụ health_beauty) | 0,0% | dim_product.category_name_en |

## `oltp.products` (32.951 dòng, 9 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `product_id` | char | 32.951 giá trị phân biệt (ví dụ 1e9e8ef04dbcff…) | 0,0% | dim_product.product_id |
| `product_category_name` | text | 73 giá trị phân biệt (ví dụ perfumaria) | 1,9% | dim_product.category_name_pt |
| `product_name_lenght` | int | 5 … 76 | 1,9% | không dùng |
| `product_description_lenght` | int | 4 … 3992 | 1,9% | không dùng |
| `product_photos_qty` | int | 1 … 20 | 1,9% | không dùng |
| `product_weight_g` | int | 0 … 40425 | 0,0% | dim_product.size_class |
| `product_length_cm` | int | 7 … 105 | 0,0% | dim_product.volume_cm3 |
| `product_height_cm` | int | 2 … 105 | 0,0% | dim_product.volume_cm3 |
| `product_width_cm` | int | 6 … 118 | 0,0% | dim_product.volume_cm3 |

## `oltp.sellers` (3.095 dòng, 4 cột)

| Cột | Kiểu | Miền giá trị | % rỗng | Vai trò trong DW |
| --- | --- | --- | ---: | --- |
| `seller_id` | char | 3.095 giá trị phân biệt (ví dụ 3442f8959a84de…) | 0,0% | dim_seller.seller_id |
| `seller_zip_code_prefix` | text | 2.246 giá trị phân biệt (ví dụ 13023) | 0,0% | dim_geography.zip_code_prefix, dim_seller.zip_code_prefix |
| `seller_city` | text | 611 giá trị phân biệt (ví dụ campinas) | 0,0% | dim_seller.zip_code_prefix |
| `seller_state` | text | 23 giá trị phân biệt (ví dụ SP) | 0,0% | dim_seller.zip_code_prefix |


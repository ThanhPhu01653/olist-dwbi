# Profiling dữ liệu nguồn (olist_full)

*Sinh tự động bởi `scripts/eda/profile.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

Mỗi bảng: số dòng, số cột, và với từng cột: kiểu dữ liệu, % giá trị rỗng (NULL), số giá trị khác nhau, giá trị nhỏ nhất/lớn nhất (cột số, ngày) hoặc độ dài chuỗi (cột văn bản), 3 giá trị phổ biến nhất (chỉ hiển thị với cột có ít giá trị khác nhau).

## Tóm tắt

| Bảng | Số dòng | Số cột | Cột có NULL |
| --- | ---: | ---: | --- |
| oltp.orders | 99.441 | 8 | order_approved_at (0,16%), order_delivered_carrier_date (1,79%), order_delivered_customer_date (2,98%) |
| oltp.order_items | 112.650 | 7 | không có |
| oltp.order_payments | 103.886 | 5 | không có |
| oltp.order_reviews | 99.224 | 7 | review_comment_title (88,34%), review_comment_message (58,70%) |
| oltp.customers | 99.441 | 5 | không có |
| oltp.sellers | 3.095 | 4 | không có |
| oltp.products | 32.951 | 9 | product_category_name (1,85%), product_name_lenght (1,85%), product_description_lenght (1,85%), product_photos_qty (1,85%), product_weight_g (0,01%), product_length_cm (0,01%), product_height_cm (0,01%), product_width_cm (0,01%) |
| oltp.geolocation | 1.000.163 | 6 | không có |
| oltp.product_category_name_translation | 71 | 2 | không có |
| crm.mql | 8.000 | 4 | origin (0,75%) |
| crm.closed_deals | 842 | 14 | business_segment (0,12%), lead_type (0,71%), lead_behaviour_profile (21,02%), has_company (92,52%), has_gtin (92,40%), average_stock (92,16%), business_type (1,19%), declared_product_catalog_size (91,81%) |

Hình: `figures/3-3-1_null_heatmap.png` – bản đồ nhiệt tỷ lệ NULL của mọi cột (ô trống = bảng không có cột đó).

## oltp.orders

99.441 dòng × 8 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| order_id | char(32) | 0,00% | 99.441 | – | – |
| customer_id | char(32) | 0,00% | 99.441 | – | – |
| order_status | text | 0,00% | 8 | độ dài 7–11 | delivered (96.478); shipped (1.107); canceled (625) |
| order_purchase_timestamp | timestamp | 0,00% | 98.875 | 2016-09-04 21:15:19 … 2018-10-17 17:30:18 | – |
| order_approved_at | timestamp | 0,16% | 90.733 | 2016-09-15 12:16:38 … 2018-09-03 17:40:06 | – |
| order_delivered_carrier_date | timestamp | 1,79% | 81.018 | 2016-10-08 10:34:01 … 2018-09-11 19:48:28 | – |
| order_delivered_customer_date | timestamp | 2,98% | 95.664 | 2016-10-11 13:46:32 … 2018-10-17 13:22:46 | – |
| order_estimated_delivery_date | timestamp | 0,00% | 459 | 2016-09-30 00:00:00 … 2018-11-12 00:00:00 | 2017-12-20 00:00:00 (522); 2018-03-12 00:00:00 (516); 2018-03-13 00:00:00 (513) |

## oltp.order_items

112.650 dòng × 7 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| order_id | char(32) | 0,00% | 98.666 | – | – |
| order_item_id | integer | 0,00% | 21 | 1 … 21 | 1 (98.666); 2 (9.803); 3 (2.287) |
| product_id | char(32) | 0,00% | 32.951 | – | – |
| seller_id | char(32) | 0,00% | 3.095 | – | – |
| shipping_limit_date | timestamp | 0,00% | 93.318 | 2016-09-19 00:15:34 … 2020-04-09 22:35:08 | – |
| price | numeric(12,2) | 0,00% | 5.968 | 0.85 … 6735.00 | – |
| freight_value | numeric(12,2) | 0,00% | 6.999 | 0.00 … 409.68 | – |

## oltp.order_payments

103.886 dòng × 5 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| order_id | char(32) | 0,00% | 99.440 | – | – |
| payment_sequential | integer | 0,00% | 29 | 1 … 29 | 1 (99.360); 2 (3.039); 3 (581) |
| payment_type | text | 0,00% | 5 | độ dài 6–11 | credit_card (76.795); boleto (19.784); voucher (5.775) |
| payment_installments | integer | 0,00% | 24 | 0 … 24 | 1 (52.546); 2 (12.413); 3 (10.461) |
| payment_value | numeric(12,2) | 0,00% | 29.077 | 0.00 … 13664.08 | – |

## oltp.order_reviews

99.224 dòng × 7 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| review_id | char(32) | 0,00% | 98.410 | – | – |
| order_id | char(32) | 0,00% | 98.673 | – | – |
| review_score | smallint | 0,00% | 5 | 1 … 5 | 5 (57.328); 4 (19.142); 1 (11.424) |
| review_comment_title | text | 88,34% | 4.527 | độ dài 1–26 | – |
| review_comment_message | text | 58,70% | 36.159 | độ dài 1–208 | – |
| review_creation_date | timestamp | 0,00% | 636 | 2016-10-02 00:00:00 … 2018-08-31 00:00:00 | 2017-12-19 00:00:00 (463); 2018-08-28 00:00:00 (452); 2017-12-20 00:00:00 (440) |
| review_answer_timestamp | timestamp | 0,00% | 98.248 | 2016-10-07 18:32:28 … 2018-10-29 12:27:35 | – |

## oltp.customers

99.441 dòng × 5 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| customer_id | char(32) | 0,00% | 99.441 | – | – |
| customer_unique_id | char(32) | 0,00% | 96.096 | – | – |
| customer_zip_code_prefix | text | 0,00% | 14.994 | độ dài 5–5 | – |
| customer_city | text | 0,00% | 4.119 | độ dài 3–32 | – |
| customer_state | text | 0,00% | 27 | độ dài 2–2 | SP (41.746); RJ (12.852); MG (11.635) |

## oltp.sellers

3.095 dòng × 4 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| seller_id | char(32) | 0,00% | 3.095 | – | – |
| seller_zip_code_prefix | text | 0,00% | 2.246 | độ dài 5–5 | – |
| seller_city | text | 0,00% | 611 | độ dài 2–40 | sao paulo (694); curitiba (127); rio de janeiro (96) |
| seller_state | text | 0,00% | 23 | độ dài 2–2 | SP (1.849); PR (349); MG (244) |

## oltp.products

32.951 dòng × 9 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| product_id | char(32) | 0,00% | 32.951 | – | – |
| product_category_name | text | 1,85% | 73 | độ dài 3–46 | cama_mesa_banho (3.029); esporte_lazer (2.867); moveis_decoracao (2.657) |
| product_name_lenght | integer | 1,85% | 66 | 5 … 76 | 60 (2.182); 59 (2.025); 58 (1.887) |
| product_description_lenght | integer | 1,85% | 2.960 | 4 … 3992 | – |
| product_photos_qty | integer | 1,85% | 19 | 1 … 20 | 1 (16.489); 2 (6.263); 3 (3.860) |
| product_weight_g | integer | 0,01% | 2.204 | 0 … 40425 | – |
| product_length_cm | integer | 0,01% | 99 | 7 … 105 | 16 (5.520); 20 (2.816); 30 (2.029) |
| product_height_cm | integer | 0,01% | 102 | 2 … 105 | 10 (2.548); 15 (2.022); 20 (1.991) |
| product_width_cm | integer | 0,01% | 95 | 6 … 118 | 11 (3.718); 20 (3.053); 16 (2.808) |

## oltp.geolocation

1.000.163 dòng × 6 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| id | bigint | 0,00% | 1.000.163 | 1 … 1000163 | – |
| geolocation_zip_code_prefix | text | 0,00% | 19.015 | độ dài 5–5 | – |
| geolocation_lat | double | 0,00% | 717.372 | -36.6053744107061 … 45.06593318269697 | – |
| geolocation_lng | double | 0,00% | 717.615 | -101.46676644931476 … 121.10539381057764 | – |
| geolocation_city | text | 0,00% | 8.011 | độ dài 2–38 | – |
| geolocation_state | text | 0,00% | 27 | độ dài 2–2 | SP (404.268); MG (126.336); RJ (121.169) |

## oltp.product_category_name_translation

71 dòng × 2 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| product_category_name | text | 0,00% | 71 | độ dài 3–46 | – |
| product_category_name_english | text | 0,00% | 71 | độ dài 3–39 | – |

## crm.mql

8.000 dòng × 4 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| mql_id | char(32) | 0,00% | 8.000 | – | – |
| first_contact_date | date | 0,00% | 336 | 2017-06-14 … 2018-05-31 | 2018-05-02 (93); 2018-05-15 (76); 2018-01-22 (75) |
| landing_page_id | char(32) | 0,00% | 495 | – | b76ef37428e6799c421989521c0e (912); 22c29808c4f815213303f8933030 (883); 58326e62183c14b0c03085c33b9f (495) |
| origin | text | 0,75% | 10 | độ dài 5–17 | organic_search (2.296); paid_search (1.586); social (1.350) |

## crm.closed_deals

842 dòng × 14 cột.

| Cột | Kiểu | % null | Số giá trị khác nhau | Min … Max | Top giá trị (số lần) |
| --- | --- | ---: | ---: | --- | --- |
| mql_id | char(32) | 0,00% | 842 | – | – |
| seller_id | char(32) | 0,00% | 842 | – | – |
| sdr_id | char(32) | 0,00% | 32 | – | 4b339f9567d060bcea4f5136b9f5 (140); 068066e24f0c643eb1d089c7dd20 (81); 56bf83c4bb35763a51c2baab501b (74) |
| sr_id | char(32) | 0,00% | 22 | – | 4ef15afb4b2723d8f3d81e51ec7a (133); d3d1e91a157ea7f90548eef82f19 (82); 6565aa9ce3178a5caf6171827af3 (74) |
| won_date | timestamp | 0,00% | 824 | 2017-12-05 02:00:00 … 2018-11-14 18:04:19 | – |
| business_segment | text | 0,12% | 33 | độ dài 3–31 | home_decor (105); health_beauty (93); car_accessories (77) |
| lead_type | text | 0,71% | 8 | độ dài 5–15 | online_medium (332); online_big (126); industry (123) |
| lead_behaviour_profile | text | 21,02% | 9 | độ dài 3–11 | cat (407); eagle (123); wolf (95) |
| has_company | boolean | 92,52% | 2 | – | true (58); false (5) |
| has_gtin | boolean | 92,40% | 2 | – | true (54); false (10) |
| average_stock | text | 92,16% | 6 | độ dài 3–7 | 5-20 (22); 50-200 (15); 1-5 (10) |
| business_type | text | 1,19% | 3 | độ dài 5–12 | reseller (587); manufacturer (242); other (3) |
| declared_product_catalog_size | numeric(12,1) | 91,81% | 33 | 1.0 … 2000.0 | 100.0 (9); 50.0 (7); 300.0 (5) |
| declared_monthly_revenue | numeric(14,2) | 0,00% | 27 | 0.00 … 50000000.00 | 0.00 (797); 100000.00 (5); 10000.00 (3) |

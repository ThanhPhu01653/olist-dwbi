# Mẫu trước / sau khi làm sạch (staging → ods)

*Sinh tự động bởi `scripts/export_samples.py` trên `olist_dw`. Mỗi bảng: 5 bản ghi của cùng một đối tượng ở staging và ods; ô thay đổi được tô vàng trong ảnh.*

## products – danh mục rỗng → 'unknown'; *_lenght → *_length; cờ dq_missing_dimensions

Ảnh: `figures/3-4-3_before_after_products.png`

**Trước (staging)**

| product_id | product_category_name | product_name_lenght | product_description_lenght | product_weight_g |
| --- | --- | --- | --- | --- |
| 0082684bb4a60a862baaf7a60a5845ed | NULL | NULL | NULL | 500.0 |
| 00ab8a8b9fe219511dc3f178c6d79698 | NULL | NULL | NULL | 2100.0 |
| 00d62b338366db4c4aec8547ea8f928e | NULL | NULL | NULL | 400.0 |
| 09ff539a621711667c43eba6a3bd8466 | bebes | 60.0 | 865.0 | NULL |
| 36ba42dd187055e1fbe943b2d11430ca | cama_mesa_banho | 53.0 | 528.0 | 0.0 |

**Sau (ods)**

| product_id | product_category_name | name_length | description_length | weight_g | dq_missing_dimensions |
| --- | --- | --- | --- | --- | --- |
| 0082684bb4a60a862baaf7a60a5845ed | unknown | NULL | NULL | 500.0 | False |
| 00ab8a8b9fe219511dc3f178c6d79698 | unknown | NULL | NULL | 2100.0 | False |
| 00d62b338366db4c4aec8547ea8f928e | unknown | NULL | NULL | 400.0 | False |
| 09ff539a621711667c43eba6a3bd8466 | bebes | 60.0 | 865.0 | NULL | True |
| 36ba42dd187055e1fbe943b2d11430ca | cama_mesa_banho | 53.0 | 528.0 | 0.0 | True |

## orders – giữ nguyên đơn, thêm cờ lỗi dq_flags

Ảnh: `figures/3-4-3_before_after_orders.png`

**Trước (staging)**

| order_id | order_status | order_purchase_timestamp | order_approved_at | order_delivered_carrier_date | order_delivered_customer_date |
| --- | --- | --- | --- | --- | --- |
| 0184d4ddb259e1a4cfc2871888cf97b8 | delivered | 2017-09-01 20:04:28 | 2017-09-13 22:17:15 | 2017-09-04 14:05:50 | 2017-09-09 15:12:44 |
| 0922ee1619de7b995648e5a8407afb91 | delivered | 2017-07-11 10:45:44 | 2017-07-11 10:55:15 | 2017-07-14 12:41:34 | 2017-07-12 20:49:42 |
| 12a95a3c06dbaec84bcfb0e2da5d228a | delivered | 2017-02-17 13:05:55 | NULL | 2017-02-22 11:23:11 | 2017-03-02 11:09:19 |
| 2aa91108853cecb43c84a5dc5b277475 | delivered | 2017-09-29 08:52:58 | 2017-09-29 09:07:16 | NULL | 2017-11-20 19:44:47 |
| 2d1e2d5bf4dc7227b3bfebb81328c15f | delivered | 2017-11-28 17:44:07 | 2017-11-28 17:56:40 | 2017-11-30 18:12:23 | NULL |

**Sau (ods)**

| order_id | order_status | order_purchase_timestamp | order_approved_at | order_delivered_carrier_date | order_delivered_customer_date | dq_flags |
| --- | --- | --- | --- | --- | --- | --- |
| 0184d4ddb259e1a4cfc2871888cf97b8 | delivered | 2017-09-01 20:04:28 | 2017-09-13 22:17:15 | 2017-09-04 14:05:50 | 2017-09-09 15:12:44 | {'carrier_before_approved'} |
| 0922ee1619de7b995648e5a8407afb91 | delivered | 2017-07-11 10:45:44 | 2017-07-11 10:55:15 | 2017-07-14 12:41:34 | 2017-07-12 20:49:42 | {'delivered_before_carrier'} |
| 12a95a3c06dbaec84bcfb0e2da5d228a | delivered | 2017-02-17 13:05:55 | NULL | 2017-02-22 11:23:11 | 2017-03-02 11:09:19 | {'delivered_without_approval'} |
| 2aa91108853cecb43c84a5dc5b277475 | delivered | 2017-09-29 08:52:58 | 2017-09-29 09:07:16 | NULL | 2017-11-20 19:44:47 | {'delivered_without_carrier_date'} |
| 2d1e2d5bf4dc7227b3bfebb81328c15f | delivered | 2017-11-28 17:44:07 | 2017-11-28 17:56:40 | 2017-11-30 18:12:23 | NULL | {'delivered_without_date'} |

## order_payments – installments 0 → 1; cờ cho not_defined / giá trị 0

Không có bản ghi cần làm sạch theo quy tắc này trong dữ liệu nạp ban đầu (đến 2017-12-31); chạy lại sau các đợt incremental.

## mql – origin NULL → 'unknown'

Ảnh: `figures/3-4-3_before_after_mql.png`

**Trước (staging)**

| mql_id | first_contact_date | landing_page_id | origin |
| --- | --- | --- | --- |
| 0138fa79ed7cc7113e031e4ac11bd26a | 2017-07-07 | 22c29808c4f815213303f8933030604c | NULL |
| 0b99dab71519032b917dc641cdd7ac5b | 2017-06-14 | d41d8cd98f00b204e9800998ecf8427e | NULL |
| 33ce1e734d9d50629fa2c36769285d53 | 2017-07-11 | d41d8cd98f00b204e9800998ecf8427e | NULL |
| 4b98e90ba839623e88d5b3d6dce56562 | 2017-12-14 | 99b00c6e27db383d844d1763dbcbfe06 | NULL |
| 4bc2d171e7cff7fa3c2c4bd0bf5dabc4 | 2017-07-27 | 6404292b0f9a5594edf14be71ce4c221 | NULL |

**Sau (ods)**

| mql_id | first_contact_date | landing_page_id | origin |
| --- | --- | --- | --- |
| 0138fa79ed7cc7113e031e4ac11bd26a | 2017-07-07 | 22c29808c4f815213303f8933030604c | unknown |
| 0b99dab71519032b917dc641cdd7ac5b | 2017-06-14 | d41d8cd98f00b204e9800998ecf8427e | unknown |
| 33ce1e734d9d50629fa2c36769285d53 | 2017-07-11 | d41d8cd98f00b204e9800998ecf8427e | unknown |
| 4b98e90ba839623e88d5b3d6dce56562 | 2017-12-14 | 99b00c6e27db383d844d1763dbcbfe06 | unknown |
| 4bc2d171e7cff7fa3c2c4bd0bf5dabc4 | 2017-07-27 | 6404292b0f9a5594edf14be71ce4c221 | unknown |

## closed_deals – NULL → 'unknown' cho cột phân loại; cờ declared = 0

Ảnh: `figures/3-4-3_before_after_closed_deals.png`

**Trước (staging)**

| mql_id | business_segment | lead_type | lead_behaviour_profile | has_company | average_stock | declared_monthly_revenue |
| --- | --- | --- | --- | --- | --- | --- |
| 512f3a7ea5520eae3b54a77c0497489e | computers | offline | NULL | NULL | NULL | 0.0 |
| 51b030d05fdce1d571c4f55eed93d323 | health_beauty | online_small | NULL | NULL | NULL | 0.0 |
| dedd5db8f760f36dd41fba0d5e94308b | food_supplement | industry | NULL | NULL | NULL | 0.0 |

**Sau (ods)**

| mql_id | business_segment | lead_type | lead_behaviour_profile | has_company | average_stock | declared_monthly_revenue | dq_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 512f3a7ea5520eae3b54a77c0497489e | computers | offline | unknown | unknown | unknown | 0.0 | {'declared_revenue_zero'} |
| 51b030d05fdce1d571c4f55eed93d323 | health_beauty | online_small | unknown | unknown | unknown | 0.0 | {'declared_revenue_zero'} |
| dedd5db8f760f36dd41fba0d5e94308b | food_supplement | industry | unknown | unknown | unknown | 0.0 | {'declared_revenue_zero'} |

## sellers – city = lower(unaccent(trim())); zip = char(5)

Ảnh: `figures/3-4-3_before_after_sellers.png`

**Trước (staging)**

| seller_id | seller_zip_code_prefix | seller_city | seller_state |
| --- | --- | --- | --- |
| 0015a82c2db000af6aaaf3ae2ecb0532 | 09080 | santo andre | SP |
| 001cca7ae9ae17fb1caed9dfb1094831 | 29156 | cariacica | ES |
| 001e6ad469a905060d959994f1b41e4f | 24754 | sao goncalo | RJ |
| 002100f778ceb8431b7a1020ff7ab48f | 14405 | franca | SP |
| a3fa18b3f688ec0fca3eb8bfcbd2d5b3 | 04557 | são paulo | SP |

**Sau (ods)**

| seller_id | zip_code_prefix | city | state_code |
| --- | --- | --- | --- |
| 0015a82c2db000af6aaaf3ae2ecb0532 | 09080 | santo andre | SP |
| 001cca7ae9ae17fb1caed9dfb1094831 | 29156 | cariacica | ES |
| 001e6ad469a905060d959994f1b41e4f | 24754 | sao goncalo | RJ |
| 002100f778ceb8431b7a1020ff7ab48f | 14405 | franca | SP |
| a3fa18b3f688ec0fca3eb8bfcbd2d5b3 | 04557 | sao paulo | SP |

## geolocation → geolocation_zip – nhiều điểm / zip → 1 dòng (median lat/lng, mode city/state, city chuẩn hoá)

Ảnh: `figures/3-4-3_before_after_geolocation.png`

**Trước (staging)**: 5 trong số các điểm của zip 01006

| geolocation_zip_code_prefix | geolocation_lat | geolocation_lng | geolocation_city | geolocation_state |
| --- | --- | --- | --- | --- |
| 01006 | -23.55069564418031 | -46.63488479003406 | sao paulo | SP |
| 01006 | -23.55052430835593 | -46.63669363835193 | sao paulo | SP |
| 01006 | -23.55052430835593 | -46.63669363835193 | sao paulo | SP |
| 01006 | -23.5504842536788 | -46.63570293588782 | sao paulo | SP |
| 01006 | -23.5502592536788 | -46.63635993588781 | sao paulo | SP |

**Sau (ods.geolocation_zip)**

| zip_code_prefix | latitude | longitude | city | state_code | n_points |
| --- | --- | --- | --- | --- | --- |
| 01006 | -23.550317224536894 | -46.63622549584506 | sao paulo | SP | 9 |

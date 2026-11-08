# 03 – Từ điển dữ liệu (sinh tự động 2026-11-08 13:51)

Mọi bảng trong schema `dw` (kho) và `mart_*` (data mart). Ý nghĩa lấy từ `COMMENT ON` trong database (tiếng Việt), kiểu và khoá từ `information_schema` / `pg_catalog`, số dòng và **ví dụ giá trị** lấy từ `olist_dw` ở trạng thái cuối. Chạy lại: `python scripts/gen_data_dictionary.py`. Quy ước: khoá thay thế `<tên>_key`; `-1` = dòng Unknown; cột kỹ thuật `etl_batch_id`, `dw_created_at`, `dw_updated_at` cho biết lô nạp. Cột mart không có COMMENT riêng lấy nghĩa từ cột cùng tên ở `dw` hoặc từ bảng chú thích của script.

## Mục lục

- [`dw.dim_customer`](#dwdim_customer) – bảng, 96,339 dòng
- [`dw.dim_date`](#dwdim_date) – bảng, 1,828 dòng
- [`dw.dim_geography`](#dwdim_geography) – bảng, 19,178 dòng
- [`dw.dim_lead_origin`](#dwdim_lead_origin) – bảng, 11 dòng
- [`dw.dim_lead_profile`](#dwdim_lead_profile) – bảng, 503 dòng
- [`dw.dim_order_status`](#dwdim_order_status) – bảng, 9 dòng
- [`dw.dim_payment_type`](#dwdim_payment_type) – bảng, 6 dòng
- [`dw.dim_product`](#dwdim_product) – bảng, 32,952 dòng
- [`dw.dim_sales_rep`](#dwdim_sales_rep) – bảng, 55 dòng
- [`dw.dim_seller`](#dwdim_seller) – bảng, 3,558 dòng
- [`dw.fact_lead_funnel`](#dwfact_lead_funnel) – bảng, 8,000 dòng
- [`dw.fact_order_fulfillment`](#dwfact_order_fulfillment) – bảng, 99,441 dòng
- [`dw.fact_order_item`](#dwfact_order_item) – bảng, 112,650 dòng
- [`dw.fact_payment`](#dwfact_payment) – bảng, 103,886 dòng
- [`dw.fact_review`](#dwfact_review) – bảng, 99,224 dòng
- [`dw.fact_seller_monthly`](#dwfact_seller_monthly) – bảng, 36,583 dòng
- [`dw.v_dim_approved_date`](#dwv_dim_approved_date) – view, 1,828 dòng
- [`dw.v_dim_carrier_date`](#dwv_dim_carrier_date) – view, 1,828 dòng
- [`dw.v_dim_delivered_date`](#dwv_dim_delivered_date) – view, 1,828 dòng
- [`dw.v_dim_estimated_date`](#dwv_dim_estimated_date) – view, 1,828 dòng
- [`dw.v_dim_first_contact_date`](#dwv_dim_first_contact_date) – view, 1,828 dòng
- [`dw.v_dim_first_sale_date`](#dwv_dim_first_sale_date) – view, 1,828 dòng
- [`dw.v_dim_purchase_date`](#dwv_dim_purchase_date) – view, 1,828 dòng
- [`dw.v_dim_review_answer_date`](#dwv_dim_review_answer_date) – view, 1,828 dòng
- [`dw.v_dim_review_creation_date`](#dwv_dim_review_creation_date) – view, 1,828 dòng
- [`dw.v_dim_shipping_limit_date`](#dwv_dim_shipping_limit_date) – view, 1,828 dòng
- [`dw.v_dim_won_date`](#dwv_dim_won_date) – view, 1,828 dòng
- [`mart_acquisition.v_funnel_by_origin_month`](#mart_acquisitionv_funnel_by_origin_month) – view, 113 dòng
- [`mart_acquisition.v_seller_by_channel`](#mart_acquisitionv_seller_by_channel) – materialized view, 7 dòng
- [`mart_acquisition.v_seller_scorecard`](#mart_acquisitionv_seller_scorecard) – materialized view, 3,095 dòng
- [`mart_cx.v_customer_cohort`](#mart_cxv_customer_cohort) – materialized view, 220 dòng
- [`mart_cx.v_customer_rfm`](#mart_cxv_customer_rfm) – materialized view, 94,983 dòng
- [`mart_cx.v_payment_mix_month`](#mart_cxv_payment_mix_month) – view, 90 dòng
- [`mart_cx.v_review_vs_delay`](#mart_cxv_review_vs_delay) – view, 105 dòng
- [`mart_fulfillment.v_fulfillment_order`](#mart_fulfillmentv_fulfillment_order) – view, 99,441 dòng
- [`mart_fulfillment.v_fulfillment_state_month`](#mart_fulfillmentv_fulfillment_state_month) – view, 565 dòng
- [`mart_fulfillment.v_shipping_distance`](#mart_fulfillmentv_shipping_distance) – view, 112,650 dòng
- [`mart_fulfillment.v_status_funnel`](#mart_fulfillmentv_status_funnel) – view, 125 dòng
- [`mart_sales.v_category_pareto`](#mart_salesv_category_pareto) – view, 74 dòng
- [`mart_sales.v_geo_state`](#mart_salesv_geo_state) – view, 27 dòng
- [`mart_sales.v_geo_zip`](#mart_salesv_geo_zip) – view, 14,889 dòng
- [`mart_sales.v_sales_category_month`](#mart_salesv_sales_category_month) – view, 1,282 dòng
- [`mart_sales.v_sales_daily`](#mart_salesv_sales_daily) – view, 614 dòng
- [`mart_sales.v_sales_state_month`](#mart_salesv_sales_state_month) – view, 558 dòng

### dw.dim_customer

*bảng · **96,339 dòng***

**Grain**: 1 phiên bản địa chỉ của 1 khách thật (SCD2).

**Mô tả**: Chiều khách hàng, SCD loại 2: 1 dòng / phiên bản địa chỉ của 1 khách thật (customer_unique_id)

**Khoá chính**: `customer_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `customer_key` | integer | không | Khoá thay thế (mỗi phiên bản một khoá) | 3 |
| `customer_unique_id` | character(32) | không | Mã khách thật (khoá tự nhiên) | 0004aac84e0df4da2b147fca70cf8255 |
| `zip_code_prefix` | character(5) | có | Zip của phiên bản (thuộc tính theo dõi SCD2) | 18040 |
| `city` | text | có | Thành phố của phiên bản | sorocaba |
| `state_code` | character(2) | có | Bang của phiên bản | SP |
| `geography_key` | integer | không | Khoá sang dim_geography → `dim_geography` | 5991 |
| `effective_from` | date | không | Ngày bắt đầu hiệu lực (phiên bản đầu = 1900-01-01) | 1900-01-01 |
| `effective_to` | date | không | Ngày kết thúc hiệu lực (phiên bản hiện hành = 9999-12-31) | 9999-12-31 |
| `is_current` | boolean | không | Phiên bản hiện hành | True |
| `version_no` | integer | không | Số thứ tự phiên bản của khách (1, 2, ...) | 1 |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_date

*bảng · **1,828 dòng***

**Grain**: 1 ngày.

**Mô tả**: Chiều thời gian: 1 dòng / ngày từ 2016-01-01 đến 2020-12-31 (+ dòng Unknown key -1). Dùng chung cho nhiều vai trò (ngày mua, duyệt, giao...)

**Khoá chính**: `date_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | không | Khoá ngày dạng số yyyymmdd (vd 20171124); -1 = Unknown | 20160103 |
| `full_date` | date | có | Ngày dạng date | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_geography

*bảng · **19,178 dòng***

**Grain**: 1 mã bưu chính (zip).

**Mô tả**: Chiều địa lý: 1 dòng / mã bưu chính (zip prefix); phân cấp Zip - Thành phố - Bang - Vùng - Quốc gia

**Khoá chính**: `geography_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `geography_key` | integer | không | Khoá thay thế | 3 |
| `zip_code_prefix` | character(5) | có | Mã bưu chính 5 số (khoá tự nhiên) | 01003 |
| `city` | text | có | Tên thành phố đã chuẩn hoá (chữ thường, không dấu) | sao paulo |
| `state_code` | character(2) | có | Mã bang 2 ký tự | SP |
| `state_name` | text | có | Tên bang | São Paulo |
| `region` | text | có | Vùng: Norte, Nordeste, Centro-Oeste, Sudeste, Sul | Sudeste |
| `country` | text | không | Quốc gia | Brazil |
| `latitude` | double precision | có | Vĩ độ (median của zip); NULL nếu zip không có trong bảng toạ độ | -23.54897652899767 |
| `longitude` | double precision | có | Kinh độ (median của zip); NULL nếu zip không có trong bảng toạ độ | -46.63531311226845 |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_lead_origin

*bảng · **11 dòng***

**Grain**: 1 giá trị origin của MQL.

**Mô tả**: Chiều kênh thu hút của MQL

**Khoá chính**: `lead_origin_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `lead_origin_key` | integer | không | -> dim_lead_origin | 3 |
| `origin` | text | không | Kênh gốc (organic_search, paid_search, ...) | email |
| `channel_group` | text | không | Nhóm kênh: Organic, Paid, Social, Email, Other, Unknown | Email |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_lead_profile

*bảng · **503 dòng***

**Grain**: 1 tổ hợp thuộc tính deal.

**Mô tả**: Chiều hồ sơ deal (junk dimension): mỗi tổ hợp thuộc tính deal một dòng; dòng -1 cho MQL chưa chốt

**Khoá chính**: `lead_profile_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `lead_profile_key` | integer | không | -> dim_lead_profile (-1 nếu chưa chốt) | 3 |
| `business_segment` | text | không | Phân khúc kinh doanh | health_beauty |
| `lead_type` | text | không | Loại lead | online_small |
| `lead_behaviour_profile` | text | không | Hồ sơ hành vi | wolf |
| `business_type` | text | không | Loại hình kinh doanh | manufacturer |
| `has_company` | text | không | Có công ty (true/false/unknown) | unknown |
| `has_gtin` | text | không | Có mã GTIN (true/false/unknown) | unknown |
| `average_stock` | text | không | Tồn kho trung bình khai báo | unknown |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_order_status

*bảng · **9 dòng***

**Grain**: 1 trạng thái đơn.

**Mô tả**: Chiều trạng thái đơn: 8 trạng thái + Unknown

**Khoá chính**: `order_status_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_status_key` | integer | không | Trạng thái đơn -> dim_order_status | 3 |
| `order_status` | text | không | Trạng thái gốc | created |
| `status_group` | text | không | Nhóm: Completed, In progress, Failed | In progress |
| `is_final` | boolean | không | Trạng thái cuối (không đổi nữa) | False |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_payment_type

*bảng · **6 dòng***

**Grain**: 1 hình thức thanh toán.

**Mô tả**: Chiều hình thức thanh toán

**Khoá chính**: `payment_type_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `payment_type_key` | integer | không | -> dim_payment_type | -1 |
| `payment_type` | text | không | Loại gốc (credit_card, boleto, ...) | boleto |
| `payment_group` | text | không | Nhóm (Card, Bank slip, Voucher, Unknown) | Unknown |
| `display_name` | text | không | Tên hiển thị | Unknown |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.200850+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_product

*bảng · **32,952 dòng***

**Grain**: 1 sản phẩm.

**Mô tả**: Chiều sản phẩm: 1 dòng / sản phẩm; phân cấp Sản phẩm - Danh mục - Nhóm ngành hàng

**Khoá chính**: `product_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `product_key` | integer | không | Khoá thay thế | 3 |
| `product_id` | character(32) | không | Mã sản phẩm (khoá tự nhiên) | 0009406fd7479715e4bef61dd91f2462 |
| `category_name_pt` | text | có | Tên danh mục tiếng Bồ Đào Nha (unknown nếu rỗng) | cama_mesa_banho |
| `category_name_en` | text | có | Tên danh mục tiếng Anh | bed_bath_table |
| `category_group` | text | có | Nhóm ngành hàng (13 nhóm, từ seeds/category_group.csv) | Home & Furniture |
| `weight_g` | integer | có | Cân nặng (gram) | 300 |
| `length_cm` | integer | có | Chiều dài (cm) | 45 |
| `height_cm` | integer | có | Chiều cao (cm) | 15 |
| `width_cm` | integer | có | Chiều rộng (cm) | 35 |
| `volume_cm3` | bigint | có | Thể tích = dài x cao x rộng (cm3) | 23625 |
| `size_class` | text | có | Cỡ hàng: S (<500 g), M (<2 kg), L (<10 kg), XL (>=10 kg), Unknown | S |
| `photos_qty` | integer | có | Số ảnh | 2 |
| `name_length` | integer | có | Độ dài tên sản phẩm (ký tự) | 50 |
| `description_length` | integer | có | Độ dài mô tả (ký tự) | 266 |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_sales_rep

*bảng · **55 dòng***

**Grain**: 1 nhân viên + vai trò (SDR/SR).

**Mô tả**: Chiều nhân viên sales, đóng 2 vai trò: SDR (tìm khách) và SR (chốt deal)

**Khoá chính**: `sales_rep_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `sales_rep_key` | integer | không | (xem mô tả bảng) | 3 |
| `rep_id` | character(32) | không | Mã nhân viên | f6c6ab65a1c732f154b371401448be6d |
| `rep_role` | text | không | Vai trò: SDR hoặc SR | SDR |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.588018+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.dim_seller

*bảng · **3,558 dòng***

**Grain**: 1 seller.

**Mô tả**: Chiều người bán, SCD loại 1, chiều dùng chung (conformed) cho bán hàng và thu hút seller

**Khoá chính**: `seller_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `seller_key` | integer | không | Khoá thay thế | 9593 |
| `seller_id` | character(32) | không | Mã seller (khoá tự nhiên) | 0f5f7caa3e6a2b466fabe6bfaf25b06b |
| `zip_code_prefix` | character(5) | có | Zip của seller (NULL nếu seller chỉ có trong CRM) | 30170 |
| `city` | text | có | Thành phố của seller | belo horizonte |
| `state_code` | character(2) | có | Bang của seller | MG |
| `geography_key` | integer | không | Khoá sang dim_geography (-1 nếu chưa biết) → `dim_geography` | -1 |
| `is_from_funnel` | boolean | không | Seller có trong closed_deals của CRM | True |
| `mql_id` | character(32) | có | MQL đã dẫn tới seller; NULL nếu không từ funnel | d54be8a176d25fedda751546f6276fb6 |
| `acquisition_origin` | text | không | Kênh gốc của MQL; not_from_funnel nếu seller không từ funnel | paid_search |
| `acquisition_channel` | text | không | Nhóm kênh thu hút (Organic, Paid, Social, Email, Other, Unknown, Not from funnel) | Paid |
| `business_segment` | text | có | Phân khúc kinh doanh khai báo khi chốt deal | audio_video_electronics |
| `lead_type` | text | có | Loại lead | online_medium |
| `business_type` | text | có | Loại hình kinh doanh | reseller |
| `won_date` | date | có | Ngày chốt deal | 2018-03-26 |
| `first_sale_date` | date | có | Ngày mua của đơn đầu tiên không thuộc nhóm Failed của seller (cập nhật sau khi nạp fact_order_item); NULL nếu mọi đơn đều Failed | 2018-03-21 |
| `dw_created_at` | timestamp with time zone | không | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:46:05.660713+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) | 2026-11-08 13:46:06.790247+07:00 |

### dw.fact_lead_funnel

*bảng · **8,000 dòng***

**Grain**: 1 MQL.

**Mô tả**: Fact accumulating snapshot: 1 dòng / MQL; cập nhật khi MQL được chốt (won) và khi seller có đơn đầu

**Khoá chính**: `mql_id`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `mql_id` | character(32) | không | Mã MQL (khoá chính) | a5448d7164426cc7f3260a7b2001e3e6 |
| `landing_page_id` | character(32) | có | Trang đích (degenerate) | bdaeb752e5c3caa215ebe04c61e22325 |
| `first_contact_date_key` | integer | không | Mốc 1: ngày liên hệ đầu → `dim_date` | 20171208 |
| `won_date_key` | integer | không | Mốc 2: ngày chốt deal (-1 nếu chưa chốt) → `dim_date` | -1 |
| `first_sale_date_key` | integer | không | Mốc 3: ngày mua của đơn đầu tiên không thuộc nhóm Failed của seller (-1 nếu chưa) → `dim_date` | -1 |
| `lead_origin_key` | integer | không | -> dim_lead_origin → `dim_lead_origin` | 7 |
| `lead_profile_key` | integer | không | -> dim_lead_profile (-1 nếu chưa chốt) → `dim_lead_profile` | -1 |
| `seller_key` | integer | không | -> dim_seller (-1 nếu chưa chốt) → `dim_seller` | -1 |
| `sdr_key` | integer | không | Nhân viên SDR -> dim_sales_rep → `dim_sales_rep` | -1 |
| `sr_key` | integer | không | Nhân viên SR -> dim_sales_rep → `dim_sales_rep` | -1 |
| `is_won` | integer | không | 1 nếu đã chốt deal | 0 |
| `has_first_sale` | integer | không | 1 nếu seller đã có đơn | 0 |
| `days_to_close` | integer | có | Ngày từ liên hệ đầu đến chốt; NULL nếu chưa chốt hoặc âm (lỗi nguồn) | 267 |
| `days_won_to_first_sale` | integer | có | Ngày từ chốt đến đơn đầu; NULL nếu chưa có hoặc âm (seller bán trước khi chốt) | 16 |
| `declared_product_catalog_size` | numeric(12,1) | có | Số sản phẩm khai báo (non-additive, dùng AVG/median) |  |
| `declared_monthly_revenue` | numeric(14,2) | có | Doanh thu tháng khai báo (non-additive) | 0.00 |
| `seller_gmv_first_90d` | numeric(12,2) | có | GMV (đơn không bị Failed) của seller trong 90 ngày kể từ ngày đơn đầu tiên; NULL nếu chưa có đơn | 573.50 |
| `etl_batch_id` | bigint | không | Lô ETL cuối cùng ghi dòng này | 2 |

### dw.fact_order_fulfillment

*bảng · **99,441 dòng***

**Grain**: 1 đơn hàng.

**Mô tả**: Fact accumulating snapshot: 1 dòng / đơn hàng, cập nhật (UPSERT) khi đơn đi qua mốc mới; dùng cho thời gian xử lý, giao trễ, hủy

**Khoá chính**: `order_id`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_id` | character(32) | không | Mã đơn (khoá chính, degenerate dimension) | 00048cc3ae777c65dbb7d2a0634bc1ea |
| `customer_key` | integer | không | Phiên bản SCD2 của khách tại ngày mua → `dim_customer` | 23072 |
| `customer_geography_key` | integer | không | Địa lý khách -> dim_geography → `dim_geography` | 9470 |
| `order_status_key` | integer | không | -> dim_order_status → `dim_order_status` | 4 |
| `purchase_date_key` | integer | không | Mốc 1: ngày mua → `dim_date` | 20170515 |
| `approved_date_key` | integer | không | Mốc 2: ngày duyệt thanh toán (-1 nếu chưa xảy ra) → `dim_date` | 20170517 |
| `carrier_date_key` | integer | không | Mốc 3: ngày bàn giao cho vận chuyển (-1 nếu chưa) → `dim_date` | 20170517 |
| `delivered_date_key` | integer | không | Mốc 4: ngày giao khách (-1 nếu chưa) → `dim_date` | 20170522 |
| `estimated_date_key` | integer | không | Mốc 5: ngày giao dự kiến → `dim_date` | 20170606 |
| `purchase_ts` | timestamp without time zone | có | Thời điểm mua (gốc) | 2017-05-15 21:42:34 |
| `approved_ts` | timestamp without time zone | có | Thời điểm duyệt (gốc) | 2017-05-17 03:55:27 |
| `carrier_ts` | timestamp without time zone | có | Thời điểm bàn giao vận chuyển (gốc) | 2017-05-17 11:05:55 |
| `delivered_ts` | timestamp without time zone | có | Thời điểm giao khách (gốc) | 2017-05-22 13:44:35 |
| `estimated_ts` | timestamp without time zone | có | Thời điểm giao dự kiến (gốc) | 2017-06-06 00:00:00 |
| `approval_hours` | numeric(10,2) | có | Giờ từ mua đến duyệt; NULL nếu thiếu mốc hoặc âm (lỗi nguồn) | 30.21 |
| `handling_days` | numeric(10,2) | có | Ngày từ duyệt đến bàn giao vận chuyển; NULL nếu thiếu mốc hoặc âm | 0.30 |
| `transit_days` | numeric(10,2) | có | Ngày từ bàn giao đến giao khách; NULL nếu thiếu mốc hoặc âm | 5.11 |
| `lead_days` | numeric(10,2) | có | Ngày từ mua đến giao khách; NULL nếu thiếu mốc hoặc âm | 6.67 |
| `delay_days` | integer | có | Ngày giao thực tế - ngày dự kiến (theo ngày; âm = giao sớm) | -15 |
| `promised_days` | integer | có | Ngày dự kiến - ngày mua = số ngày Olist hứa giao; NULL nếu âm | 22 |
| `is_delivered` | integer | không | 1 nếu trạng thái delivered và có ngày giao | 1 |
| `is_late` | integer | không | 1 nếu đã giao và delay_days > 0 | 0 |
| `is_canceled` | integer | không | 1 nếu trạng thái canceled | 0 |
| `item_count` | integer | không | Số dòng sản phẩm của đơn | 1 |
| `seller_count` | integer | không | Số seller khác nhau trong đơn | 1 |
| `order_value` | numeric(12,2) | không | Σ price của đơn | 21.90 |
| `freight_total` | numeric(12,2) | không | Σ freight_value của đơn | 12.69 |
| `payment_total` | numeric(12,2) | không | Σ payment_value của đơn | 34.59 |
| `dq_flag_count` | integer | không | Số cờ lỗi dữ liệu của đơn ở ODS + số khoảng thời gian bị đặt NULL vì âm | 0 |
| `etl_batch_id` | bigint | không | Lô ETL cuối cùng ghi dòng này | 2 |

### dw.fact_order_item

*bảng · **112,650 dòng***

**Grain**: 1 dòng sản phẩm trong 1 đơn.

**Mô tả**: Fact giao dịch: 1 dòng / sản phẩm trong 1 đơn (order_id, order_item_id). Dùng cho GMV, doanh thu theo danh mục / seller / vùng

**Khoá chính**: `order_id`, `order_item_id`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_id` | character(32) | không | Mã đơn (degenerate dimension) | 00048cc3ae777c65dbb7d2a0634bc1ea |
| `order_item_id` | integer | không | Số thứ tự dòng trong đơn (degenerate dimension) | 1 |
| `purchase_date_key` | integer | không | Ngày mua -> dim_date → `dim_date` | 20170515 |
| `shipping_limit_date_key` | integer | không | Hạn seller bàn giao cho vận chuyển -> dim_date → `dim_date` | 20170523 |
| `customer_key` | integer | không | Phiên bản SCD2 của khách có hiệu lực tại ngày mua -> dim_customer → `dim_customer` | 23072 |
| `customer_geography_key` | integer | không | Địa lý khách (vai trò 1) -> dim_geography → `dim_geography` | 9470 |
| `seller_geography_key` | integer | không | Địa lý seller (vai trò 2) -> dim_geography → `dim_geography` | 5310 |
| `seller_key` | integer | không | -> dim_seller → `dim_seller` | 1225 |
| `product_key` | integer | không | -> dim_product → `dim_product` | 30848 |
| `order_status_key` | integer | không | Trạng thái đơn -> dim_order_status → `dim_order_status` | 4 |
| `price` | numeric(12,2) | không | Giá bán (BRL), additive | 21.90 |
| `freight_value` | numeric(12,2) | không | Phí vận chuyển phân bổ cho dòng (BRL), additive | 12.69 |
| `item_total` | numeric(12,2) | không | price + freight_value | 34.59 |
| `etl_batch_id` | bigint | không | Lô ETL đã nạp dòng này | 2 |

### dw.fact_payment

*bảng · **103,886 dòng***

**Grain**: 1 lần thanh toán.

**Mô tả**: Fact giao dịch: 1 lần thanh toán (order_id, payment_sequential)

**Khoá chính**: `order_id`, `payment_sequential`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_id` | character(32) | không | Mã đơn | 3d7239c394a212faae122962df514ac7 |
| `payment_sequential` | integer | không | Lần thanh toán thứ mấy của đơn | 1 |
| `purchase_date_key` | integer | không | Ngày mua của đơn -> dim_date → `dim_date` | 20170605 |
| `customer_key` | integer | không | -> dim_customer → `dim_customer` | 27147 |
| `payment_type_key` | integer | không | -> dim_payment_type → `dim_payment_type` | 2 |
| `payment_installments` | integer | không | Số kỳ trả góp (>= 1) | 3 |
| `payment_value` | numeric(12,2) | không | Giá trị thanh toán (BRL) | 51.84 |
| `etl_batch_id` | bigint | không | Lô ETL đã nạp | 2 |

### dw.fact_review

*bảng · **99,224 dòng***

**Grain**: 1 review của 1 đơn.

**Mô tả**: Fact giao dịch: 1 review gắn với 1 đơn (review_id, order_id)

**Khoá chính**: `review_id`, `order_id`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `review_id` | character(32) | không | Mã review | 00055e36e9608fe969231e551983a69c |
| `order_id` | character(32) | không | Mã đơn | f5fea26ab547eec920e6f8ecdc5c37e4 |
| `review_creation_date_key` | integer | không | Ngày tạo review -> dim_date → `dim_date` | 20171125 |
| `review_answer_date_key` | integer | không | Ngày trả lời review -> dim_date (-1 nếu không có) → `dim_date` | 20171127 |
| `customer_key` | integer | không | -> dim_customer → `dim_customer` | 12734 |
| `review_score` | integer | không | Điểm 1-5 | 5 |
| `is_negative` | integer | không | 1 nếu điểm <= 2 | 0 |
| `has_comment_title` | integer | không | 1 nếu có tiêu đề | 0 |
| `has_comment_message` | integer | không | 1 nếu có nội dung | 1 |
| `comment_length` | integer | không | Số ký tự nội dung (0 nếu không có) | 64 |
| `response_hours` | numeric(10,2) | có | Giờ từ tạo đến trả lời; NULL nếu thiếu hoặc âm | 59.62 |
| `delivered_late` | integer | không | 1 nếu đơn được giao trễ (lấy từ fact_order_fulfillment) | 0 |
| `is_delivered` | smallint | không | 1 nếu đơn đã giao (có order_delivered_customer_date; lấy từ fact_order_fulfillment), 0 nếu chưa giao | 1 |
| `etl_batch_id` | bigint | không | Lô ETL đã nạp | 2 |

### dw.fact_seller_monthly

*bảng · **36,583 dòng***

**Grain**: 1 seller × 1 tháng.

**Mô tả**: Fact periodic snapshot: 1 seller x 1 tháng, dày đặc từ tháng có đơn đầu đến tháng cuối có đơn trong dữ liệu

**Khoá chính**: `month_date_key`, `seller_key`

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `month_date_key` | integer | không | Ngày 1 của tháng -> dim_date → `dim_date` | 20170601 |
| `seller_key` | integer | không | -> dim_seller → `dim_seller` | 377 |
| `orders` | integer | không | Số đơn (distinct) có seller này trong tháng, mọi trạng thái | 0 |
| `items` | integer | không | Số dòng sản phẩm | 0 |
| `gmv` | numeric(12,2) | không | Σ price của đơn không bị Failed (khớp định nghĩa GMV) | 0.00 |
| `freight` | numeric(12,2) | không | Σ freight_value của đơn không bị Failed | 0.00 |
| `delivered_orders` | integer | không | Số đơn đã giao | 0 |
| `late_orders` | integer | không | Số đơn giao trễ | 0 |
| `late_rate` | numeric(7,4) | có | late_orders / delivered_orders; NULL nếu chưa có đơn giao | 0.0000 |
| `canceled_orders` | integer | không | Số đơn bị hủy | 0 |
| `avg_review_score` | numeric(4,2) | có | Điểm review trung bình; NULL nếu không có review | 2.00 |
| `is_active` | integer | không | 1 nếu orders > 0 | 0 |
| `months_since_first_sale` | integer | có | Số tháng kể từ tháng của first_sale_date (đơn đầu không thuộc nhóm Failed); 0 = tháng đó, âm = tháng trước đó chỉ có đơn Failed, NULL nếu seller chưa có đơn bán được | 0 |
| `etl_batch_id` | bigint | không | Lô ETL đã ghi | 2 |

### dw.v_dim_approved_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày approved

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_carrier_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày carrier

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_delivered_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày delivered

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_estimated_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày estimated

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_first_contact_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày first_contact

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_first_sale_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày first_sale

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_purchase_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày purchase

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_review_answer_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày review_answer

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_review_creation_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày review_creation

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_shipping_limit_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày shipping_limit

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### dw.v_dim_won_date

*view · **1,828 dòng***

**Mô tả**: Bản đóng vai (role-playing) của dim_date: ngày won

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20160103 |
| `full_date` | date | có | Ngày | 2016-01-03 |
| `day_of_month` | integer | có | Ngày trong tháng (1-31) | 3 |
| `day_of_week` | integer | có | Thứ trong tuần, 1 = Thứ Hai ... 7 = Chủ Nhật | 7 |
| `day_name` | text | có | Tên thứ (tiếng Anh) | Sunday |
| `week_of_year` | integer | có | Số tuần theo chuẩn ISO | 53 |
| `month` | integer | có | Tháng (1-12) | 1 |
| `month_name` | text | có | Tên tháng | January |
| `quarter` | integer | có | Quý (1-4) | 1 |
| `year` | integer | có | Năm | 2016 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-01 |
| `year_quarter` | character(7) | có | Năm-quý, vd 2017-Q4 | 2016-Q1 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | True |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `holiday_name` | text | có | Tên ngày lễ | Sexta-feira Santa |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `dw_created_at` | timestamp with time zone | có | Thời điểm tạo dòng trong kho (cột kỹ thuật) | 2026-11-08 13:44:34.543946+07:00 |
| `dw_updated_at` | timestamp with time zone | có | Thời điểm cập nhật dòng gần nhất (cột kỹ thuật; trống nếu chưa từng cập nhật) |  |

### mart_acquisition.v_funnel_by_origin_month

*view · **113 dòng***

**Mô tả**: Funnel theo tháng liên hệ đầu x origin: MQL, đã chốt, đã có đơn, tỷ lệ, số ngày TB, GMV 90 ngày đầu

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `first_contact_month` | character(7) | có | Tháng liên hệ đầu của MQL | 2017-07 |
| `origin` | text | có | Kênh gốc (organic_search, paid_search, ...) | direct_traffic |
| `channel_group` | text | có | Nhóm kênh: Organic, Paid, Social, Email, Other, Unknown | Organic |
| `mqls` | bigint | có | Số MQL | 16 |
| `won` | bigint | có | Số MQL đã chốt | 0 |
| `won_with_sale` | bigint | có | Số MQL đã chốt và seller có đơn | 0 |
| `win_rate_pct` | numeric | có | Tỷ lệ chốt (%) = won / mqls | 0.00 |
| `won_to_sale_rate_pct` | numeric | có | Tỷ lệ seller đã chốt có đơn (%) | 56.76 |
| `avg_days_to_close` | numeric | có | Số ngày TB từ liên hệ đến chốt | 14.8 |
| `avg_days_won_to_first_sale` | numeric | có | Số ngày TB từ chốt đến đơn đầu | 55.2 |
| `seller_gmv_first_90d` | numeric | có | GMV của seller trong 90 ngày đầu kể từ đơn đầu tiên | 0 |

### mart_acquisition.v_seller_by_channel

*materialized view · **7 dòng***

**Mô tả**: Theo kênh thu hút seller: số seller, số seller có đơn, GMV, GMV / seller, trễ, review; cờ mẫu nhỏ (< 30 seller có đơn)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `acquisition_channel` | text | có | Nhóm kênh thu hút (Organic, Paid, Social, Email, Other, Unknown, Not from funnel) | Social |
| `sellers` | bigint | có | Số seller | 75 |
| `selling_sellers` | bigint | có | Số seller có đơn | 31 |
| `pct_selling` | numeric | có | % seller có đơn | 41.33 |
| `orders` | numeric | có | Số đơn (distinct order_id) trong nhóm | 392 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 43418.00 |
| `gmv_per_selling_seller` | numeric | có | GMV TB mỗi seller có đơn | 1400.58 |
| `late_rate_pct` | numeric | có | Tỷ lệ giao trễ (%) | 5.14 |
| `avg_review_score` | numeric | có | Điểm review TB | 4.27 |
| `small_sample` | boolean | có | TRUE nếu mẫu nhỏ (seller < 10 đơn; kênh < 30 seller có đơn) | False |

### mart_acquisition.v_seller_scorecard

*materialized view · **3,095 dòng***

**Mô tả**: 1 dòng / seller có đơn: GMV, đơn, trễ, hủy, review, hạng và tỷ trọng luỹ kế (Pareto), cờ mẫu nhỏ (< 10 đơn)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `seller_key` | integer | có | Khoá thay thế | 3027 |
| `seller_id` | character(32) | có | Mã seller (khoá tự nhiên) | fa1c13f2614d7b5c4749cbc52fecda94 |
| `city` | text | có | Tên thành phố đã chuẩn hoá (chữ thường, không dấu) | sumare |
| `state_code` | character(2) | có | Mã bang 2 ký tự | SP |
| `region` | text | có | Vùng của Brazil | Sudeste |
| `is_from_funnel` | boolean | có | Seller có trong closed_deals của CRM | False |
| `acquisition_channel` | text | có | Nhóm kênh thu hút (Organic, Paid, Social, Email, Other, Unknown, Not from funnel) | Not from funnel |
| `acquisition_origin` | text | có | Kênh gốc của MQL; not_from_funnel nếu seller không từ funnel | not_from_funnel |
| `business_segment` | text | có | Phân khúc kinh doanh khai báo khi chốt deal | watches |
| `first_sale_date` | date | có | Ngày mua của đơn đầu tiên không thuộc nhóm Failed của seller (cập nhật sau khi nạp fact_order_item); NULL nếu mọi đơn đều Failed | 2017-01-07 |
| `last_active_month` | date | có | Tháng gần nhất seller có đơn | 2018-08-01 |
| `active_months` | bigint | có | Số tháng seller có đơn | 20 |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 585 |
| `items` | bigint | có | Số dòng sản phẩm | 586 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 192842.13 |
| `freight` | numeric | có | Tổng phí vận chuyển (BRL) | 10019.54 |
| `delivered_orders` | bigint | có | Số đơn đã giao | 578 |
| `late_orders` | bigint | có | Số đơn giao trễ | 53 |
| `late_rate_pct` | numeric | có | Tỷ lệ giao trễ (%) | 9.17 |
| `canceled_orders` | bigint | có | Số đơn bị hủy | 1 |
| `reviews` | bigint | có | Số review | 581 |
| `avg_review_score` | numeric | có | Điểm review TB | 4.34 |
| `pct_negative` | numeric | có | % review tiêu cực | 10.50 |
| `gmv_rank` | bigint | có | Hạng theo GMV (1 = cao nhất) | 4 |
| `gmv_share_pct` | numeric | có | (xem mô tả bảng) | 1.429 |
| `cum_share_pct` | numeric | có | Tỷ trọng luỹ kế (%) khi xếp giảm dần | 6.26 |
| `abc_class` | text | có | Hạng Pareto: A = 80% GMV đầu, B = đến 95%, C = phần còn lại | A |
| `small_sample` | boolean | có | TRUE nếu mẫu nhỏ (seller < 10 đơn; kênh < 30 seller có đơn) | False |

### mart_cx.v_customer_cohort

*materialized view · **220 dòng***

**Mô tả**: Cohort theo tháng mua đầu tiên: số khách còn mua lại sau 0,1,2... tháng và tỷ lệ quay lại

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `cohort_month` | text | có | Tháng mua đầu tiên của nhóm khách (cohort) | 2018-03 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | True |
| `months_since` | integer | có | Số tháng kể từ tháng cohort | 0 |
| `cohort_size` | bigint | có | Số khách của cohort | 6931 |
| `customers_active` | bigint | có | Số khách của cohort còn mua trong tháng đó | 6931 |
| `retention_pct` | numeric | có | Tỷ lệ khách còn mua (%) | 100.00 |

### mart_cx.v_customer_rfm

*materialized view · **94,983 dòng***

**Mô tả**: 1 dòng / khách thật (customer_unique_id): recency, frequency, monetary, điểm R-F-M 1-5 và phân khúc; đơn không thuộc nhóm Failed

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `customer_unique_id` | character(32) | có | Mã khách thật | 7390ed59fa1febbfda31a80b4318c8cb |
| `region` | text | có | Vùng của Brazil | Centro-Oeste |
| `state_code` | character(2) | có | Mã bang 2 ký tự | GO |
| `first_purchase` | date | có | Ngày mua đầu tiên | 2016-10-03 |
| `last_purchase` | date | có | Ngày mua gần nhất | 2016-10-03 |
| `recency_days` | integer | có | Số ngày từ lần mua gần nhất đến ngày chốt dữ liệu (R) | 701 |
| `frequency` | bigint | có | Số đơn (F) | 1 |
| `monetary` | numeric | có | Tổng tiền đã mua gồm phí vận chuyển (M) | 154.57 |
| `r_score` | integer | có | Điểm R 1-5 (5 = mới nhất) | 1 |
| `f_score` | integer | có | Điểm F: 1 = một đơn, 3 = hai đơn, 5 = từ ba đơn | 1 |
| `m_score` | integer | có | Điểm M 1-5 | 4 |
| `segment` | text | có | Phân khúc RFM | Ngủ đông |

### mart_cx.v_payment_mix_month

*view · **90 dòng***

**Mô tả**: Cơ cấu thanh toán theo tháng mua x hình thức: số lần, giá trị, trả góp TB, tỷ trọng giá trị

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `payment_type` | text | có | Loại gốc (credit_card, boleto, ...) | debit_card |
| `payment_group` | text | có | Nhóm (Card, Bank slip, Voucher, Unknown) | Card |
| `display_name` | text | có | Tên hiển thị | Debit card |
| `payments` | bigint | có | Số lần thanh toán | 2 |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 2 |
| `payment_value` | numeric | có | Tổng giá trị thanh toán (BRL) | 241.73 |
| `avg_installments` | numeric | có | Số kỳ trả góp TB | 1.00 |
| `value_share_pct` | numeric | có | Tỷ trọng giá trị trong tháng (%) | 0.41 |

### mart_cx.v_review_vs_delay

*view · **105 dòng***

**Mô tả**: Điểm review và % tiêu cực theo nhóm trễ giao (giao sớm ... trễ trên 7 ngày) x tháng mua; chỉ đơn đã giao

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `delay_bucket_no` | integer | có | Thứ tự nhóm trễ (để sắp xếp) | 5 |
| `delay_bucket` | text | có | Nhóm trễ giao (Giao sớm … Trễ trên 7 ngày, Chưa giao) | Trễ trên 7 ngày |
| `reviews` | bigint | có | Số review | 1 |
| `score_sum` | bigint | có | Tổng điểm review | 1 |
| `negative_reviews` | bigint | có | Số review tiêu cực (điểm ≤ 2) | 1 |
| `avg_score` | numeric | có | Điểm review TB | 1.000 |
| `pct_negative` | numeric | có | % review tiêu cực | 100.00 |
| `avg_response_hours` | numeric | có | Số giờ TB từ tạo đến trả lời review | 70.0 |

### mart_fulfillment.v_fulfillment_order

*view · **99,441 dòng***

**Mô tả**: 1 dòng / đơn: mốc ngày, thời gian từng chặng, số ngày hứa và trễ, nhóm trễ (delay_bucket), bang và vùng của khách

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_id` | character(32) | có | Mã đơn (degenerate dimension) | 00048cc3ae777c65dbb7d2a0634bc1ea |
| `purchase_date` | date | có | Ngày mua | 2017-05-15 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2017-05 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | True |
| `order_status` | text | có | Trạng thái gốc | delivered |
| `status_group` | text | có | Nhóm trạng thái đơn | Completed |
| `customer_region` | text | có | Vùng của khách | Sudeste |
| `customer_state` | character(2) | có | Bang của khách | MG |
| `customer_city` | text | có | Thành phố của khách | uberaba |
| `approved_date` | date | có | Ngày duyệt thanh toán | 2017-05-17 |
| `carrier_date` | date | có | Ngày bàn giao vận chuyển | 2017-05-17 |
| `delivered_date` | date | có | Ngày giao khách | 2017-05-22 |
| `estimated_date` | date | có | Ngày giao dự kiến | 2017-06-06 |
| `approval_hours` | numeric(10,2) | có | Giờ từ mua đến duyệt; NULL nếu thiếu mốc hoặc âm (lỗi nguồn) | 30.21 |
| `handling_days` | numeric(10,2) | có | Ngày từ duyệt đến bàn giao vận chuyển; NULL nếu thiếu mốc hoặc âm | 0.30 |
| `transit_days` | numeric(10,2) | có | Ngày từ bàn giao đến giao khách; NULL nếu thiếu mốc hoặc âm | 5.11 |
| `lead_days` | numeric(10,2) | có | Ngày từ mua đến giao khách; NULL nếu thiếu mốc hoặc âm | 6.67 |
| `promised_days` | integer | có | Ngày dự kiến - ngày mua = số ngày Olist hứa giao; NULL nếu âm | 22 |
| `delay_days` | integer | có | Ngày giao thực tế - ngày dự kiến (theo ngày; âm = giao sớm) | -15 |
| `is_delivered` | integer | có | 1 nếu trạng thái delivered và có ngày giao | 1 |
| `is_late` | integer | có | 1 nếu đã giao và delay_days > 0 | 0 |
| `is_canceled` | integer | có | 1 nếu trạng thái canceled | 0 |
| `item_count` | integer | có | Số dòng sản phẩm của đơn | 1 |
| `seller_count` | integer | có | Số seller khác nhau trong đơn | 1 |
| `order_value` | numeric(12,2) | có | Σ price của đơn | 21.90 |
| `freight_total` | numeric(12,2) | có | Σ freight_value của đơn | 12.69 |
| `payment_total` | numeric(12,2) | có | Σ payment_value của đơn | 34.59 |
| `dq_flag_count` | integer | có | Số cờ lỗi dữ liệu của đơn ở ODS + số khoảng thời gian bị đặt NULL vì âm | 0 |
| `delay_bucket` | text | có | Nhóm trễ giao (Giao sớm … Trễ trên 7 ngày, Chưa giao) | Giao sớm |
| `delay_bucket_no` | integer | có | Thứ tự nhóm trễ (để sắp xếp) | 1 |

### mart_fulfillment.v_fulfillment_state_month

*view · **565 dòng***

**Mô tả**: Theo tháng mua x bang: số đơn, tỷ lệ đúng hạn / hủy, thời gian trung bình từng chặng (chỉ đơn đã giao)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `region` | text | có | Vùng của Brazil | Centro-Oeste |
| `state_code` | character(2) | có | Mã bang 2 ký tự | DF |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 6 |
| `delivered_orders` | bigint | có | Số đơn đã giao | 6 |
| `late_orders` | bigint | có | Số đơn giao trễ | 0 |
| `canceled_orders` | bigint | có | Số đơn bị hủy | 0 |
| `on_time_rate_pct` | numeric | có | Tỷ lệ đơn giao đúng hạn (%) | 100.00 |
| `cancel_rate_pct` | numeric | có | Tỷ lệ hủy (%) | 0.00 |
| `avg_lead_days` | numeric | có | Số ngày TB từ mua đến giao | 22.99 |
| `avg_approval_hours` | numeric | có | Số giờ TB từ mua đến duyệt | 7.40 |
| `avg_handling_days` | numeric | có | Số ngày TB từ duyệt đến bàn giao vận chuyển | 15.78 |
| `avg_transit_days` | numeric | có | Số ngày TB vận chuyển | 6.91 |
| `avg_promised_days` | numeric | có | Số ngày hứa giao TB | 58.67 |

### mart_fulfillment.v_shipping_distance

*view · **112,650 dòng***

**Mô tả**: Khoảng cách seller -> khách (km, haversine) cho từng dòng hàng, nhóm 0-100 / 100-500 / 500-1000 / trên 1000 km; distance_km NULL nếu thiếu toạ độ (has_distance = false)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `order_id` | character(32) | có | Mã đơn (degenerate dimension) | 00024acbcdf0a6daa1e931b038114c75 |
| `order_item_id` | integer | có | Số thứ tự dòng trong đơn (degenerate dimension) | 1 |
| `seller_key` | integer | có | Khoá thay thế | 1921 |
| `seller_state` | character(2) | có | Bang của seller | SP |
| `customer_state` | character(2) | có | Bang của khách | SP |
| `customer_region` | text | có | Vùng của khách | Sudeste |
| `distance_km` | double precision | có | Khoảng cách seller → khách (km, haversine); trống nếu thiếu toạ độ | 295.03288775681654 |
| `has_distance` | boolean | có | TRUE nếu tính được khoảng cách | True |
| `distance_band` | text | có | Nhóm khoảng cách | 100-500 km |
| `distance_band_no` | integer | có | Thứ tự nhóm khoảng cách | 2 |
| `price` | numeric(12,2) | có | Giá bán (BRL), additive | 12.99 |
| `freight_value` | numeric(12,2) | có | Phí vận chuyển phân bổ cho dòng (BRL), additive | 12.79 |
| `freight_ratio` | numeric | có | Phí vận chuyển / giá hàng | 0.9846 |
| `lead_days` | numeric(10,2) | có | Ngày từ mua đến giao khách; NULL nếu thiếu mốc hoặc âm | 6.15 |
| `delay_days` | integer | có | Ngày giao thực tế - ngày dự kiến (theo ngày; âm = giao sớm) | -6 |
| `is_delivered` | integer | có | 1 nếu trạng thái delivered và có ngày giao | 1 |
| `is_late` | integer | có | 1 nếu đã giao và delay_days > 0 | 0 |
| `status_group` | text | có | Nhóm trạng thái đơn | Completed |

### mart_fulfillment.v_status_funnel

*view · **125 dòng***

**Mô tả**: Số đơn đi qua từng chặng (đặt, duyệt, bàn giao, giao, hủy) theo tháng mua, dạng dài

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-09 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `stage_no` | integer | có | Thứ tự chặng | 4 |
| `stage` | text | có | Tên chặng của đơn | Đã giao khách |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 1 |
| `pct_of_placed` | numeric | có | % so với số đơn đã đặt | 25.00 |

### mart_sales.v_category_pareto

*view · **74 dòng***

**Mô tả**: Pareto 80/20 của GMV theo danh mục: xếp hạng, tỷ trọng, tỷ trọng luỹ kế, hạng A/B/C

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `gmv_rank` | bigint | có | Hạng theo GMV (1 = cao nhất) | 4 |
| `category_group` | text | có | Nhóm ngành hàng (13 nhóm, từ seeds/category_group.csv) | Sports & Leisure |
| `category_name_en` | text | có | Tên danh mục tiếng Anh | sports_leisure |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 7673 |
| `items` | bigint | có | Số dòng sản phẩm | 8590 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 979740.92 |
| `share_pct` | numeric | có | Tỷ trọng (%) trong tổng | 7.26 |
| `cum_share_pct` | numeric | có | Tỷ trọng luỹ kế (%) khi xếp giảm dần | 33.12 |
| `abc_class` | text | có | Hạng Pareto: A = 80% GMV đầu, B = đến 95%, C = phần còn lại | A |

### mart_sales.v_geo_state

*view · **27 dòng***

**Mô tả**: Dữ liệu bản đồ theo bang: toạ độ tâm (trung bình các zip có toạ độ), số khách, đơn, GMV, freight ratio, số seller, lead time, tỷ lệ trễ

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `state_code` | character(2) | có | Mã bang 2 ký tự | AP |
| `state_name` | text | có | Tên bang | Amapá |
| `region` | text | có | Vùng của Brazil | Norte |
| `latitude` | numeric | có | Vĩ độ | -0.63310 |
| `longitude` | numeric | có | Kinh độ | -51.35236 |
| `zips_with_coordinates` | bigint | có | Số zip của bang có toạ độ | 26 |
| `customers` | bigint | có | Số khách thật | 67 |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 68 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 13474.30 |
| `freight_ratio` | numeric | có | Phí vận chuyển / giá hàng | 0.2069 |
| `sellers` | bigint | có | Số seller | 0 |
| `avg_lead_days` | numeric | có | Số ngày TB từ mua đến giao | 27.19 |
| `late_rate_pct` | numeric | có | Tỷ lệ giao trễ (%) | 2.99 |

### mart_sales.v_geo_zip

*view · **14,889 dòng***

**Mô tả**: Dữ liệu bản đồ theo zip có toạ độ và có khách hoặc seller: toạ độ, thành phố, số đơn và GMV phía khách, số seller

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `zip_code_prefix` | character(5) | có | Mã bưu chính 5 số (khoá tự nhiên) | 01005 |
| `city` | text | có | Tên thành phố đã chuẩn hoá (chữ thường, không dấu) | sao paulo |
| `state_code` | character(2) | có | Mã bang 2 ký tự | SP |
| `region` | text | có | Vùng của Brazil | Sudeste |
| `latitude` | double precision | có | Vĩ độ | -23.54961248124544 |
| `longitude` | double precision | có | Kinh độ | -46.63653202553522 |
| `customer_orders` | bigint | có | Số đơn phía khách | 6 |
| `customer_gmv` | numeric | có | GMV phía khách | 490.59 |
| `sellers` | bigint | có | Số seller | 0 |

### mart_sales.v_sales_category_month

*view · **1,282 dòng***

**Mô tả**: GMV, đơn, dòng hàng theo tháng x nhóm ngành hàng x danh mục (số đơn không cộng được giữa các danh mục)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `year` | integer | có | Năm | 2016 |
| `quarter` | integer | có | Quý (1-4) | 4 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `category_group` | text | có | Nhóm ngành hàng (13 nhóm, từ seeds/category_group.csv) | Auto, Tools & Construction |
| `category_name_en` | text | có | Tên danh mục tiếng Anh | garden_tools |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 5 |
| `items` | bigint | có | Số dòng sản phẩm | 5 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 1359.88 |
| `freight` | numeric | có | Tổng phí vận chuyển (BRL) | 105.31 |
| `avg_item_price` | numeric | có | Giá TB một dòng hàng | 271.98 |

### mart_sales.v_sales_daily

*view · **614 dòng***

**Mô tả**: GMV, số đơn, số dòng hàng, phí vận chuyển, AOV theo ngày mua (chỉ đơn không thuộc nhóm Failed)

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `date_key` | integer | có | Khoá ngày yyyymmdd | 20161004 |
| `full_date` | date | có | Ngày | 2016-10-04 |
| `year` | integer | có | Năm | 2016 |
| `quarter` | integer | có | Quý (1-4) | 4 |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `is_weekend` | boolean | có | Cuối tuần (Thứ Bảy, Chủ Nhật) | False |
| `is_holiday_br` | boolean | có | Ngày lễ quốc gia của Brazil | False |
| `is_black_friday` | boolean | có | Black Friday (thứ Sáu sau thứ Năm thứ 4 của tháng 11) | False |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 58 |
| `items` | bigint | có | Số dòng sản phẩm | 67 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 9571.16 |
| `freight` | numeric | có | Tổng phí vận chuyển (BRL) | 1329.79 |
| `aov` | numeric | có | Giá trị TB mỗi đơn = gmv / orders | 165.02 |

### mart_sales.v_sales_state_month

*view · **558 dòng***

**Mô tả**: GMV, đơn, phí vận chuyển, tỷ lệ freight/price theo tháng x bang của khách

| Cột | Kiểu | Null? | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- | --- |
| `year_month` | character(7) | có | Năm-tháng, vd 2017-11 | 2016-10 |
| `year` | integer | có | Năm | 2016 |
| `quarter` | integer | có | Quý (1-4) | 4 |
| `in_window` | boolean | có | TRUE nếu tháng thuộc 2017-01 → 2018-08 (giai đoạn dashboard dùng) | False |
| `region` | text | có | Vùng của Brazil | Centro-Oeste |
| `state_code` | character(2) | có | Mã bang 2 ký tự | GO |
| `state_name` | text | có | Tên bang | Goiás |
| `orders` | bigint | có | Số đơn (distinct order_id) trong nhóm | 8 |
| `items` | bigint | có | Số dòng sản phẩm | 8 |
| `gmv` | numeric | có | GMV (BRL): Σ giá hàng của đơn không thuộc nhóm Failed | 984.39 |
| `freight` | numeric | có | Tổng phí vận chuyển (BRL) | 170.28 |
| `freight_ratio` | numeric | có | Phí vận chuyển / giá hàng | 0.1730 |

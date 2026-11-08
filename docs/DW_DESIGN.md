# Thiết kế Kho dữ liệu – Olist Order Management (+ Marketing Funnel)

> Tài liệu đặc tả cho nhóm và cho Claude Code. Đây là nguồn sự thật duy nhất (single source of truth) về schema.
> Mọi thay đổi sau mốc chốt thiết kế (12/11) phải cập nhật file này trước rồi mới sửa code.
> Phiên bản: v1.1 – 07/11/2026 (v1.0 ngày 05/11/2026; thay đổi sau đó nằm trong nhật ký quyết định).

**Nhật ký quyết định**

| Ngày | Quyết định | Hệ quả |
| --- | --- | --- |
| 05/11 | Ghép thêm bộ Olist Marketing Funnel | Thêm schema `crm`, `fact_lead_funnel`, `fact_seller_monthly`, mart `mart_acquisition` |
| 05/11 | Dùng **PostgreSQL** cho toàn bộ hệ thống, không dùng SQL Server/SSAS | OLAP theo mô hình **ROLAP**: thao tác OLAP minh hoạ bằng SQL (ROLLUP, CUBE, GROUPING SETS) trên star schema và bằng Power BI; báo cáo giải thích lý do chọn ROLAP thay vì MOLAP |
| 05/11 | Không dùng Docker; chỉ Phú viết và chạy code (cùng Claude Code); cả nhóm cùng làm dashboard Power BI, báo cáo và slide | PostgreSQL cài trực tiếp; dữ liệu cho Power BI đi qua CSV xuất từ `scripts/export_powerbi.py` |
| 05/11 | Không cài PostGIS | Khoảng cách seller → khách tính bằng hàm haversine SQL thuần; dim_geography không có cột geometry |
| 05/11 | Zip: bản CSV hiện tại đã giữ số 0 đầu → `oltp` lưu zip kiểu `text`; ODS vẫn chuẩn hoá về `char(5)` (`lpad`) để phòng thủ | Lỗi "mất số 0 đầu" ở §2.3 không xảy ra với bản CSV này (số liệu kiểm chứng ghi ở §2.3) |
| 05/11 | `oltp.customers` chỉ nạp khách có đơn trong khoảng thời gian nạp (`customer_id` sinh theo từng đơn, hệ thống OLTP thật cũng vậy) | `simulate_increment` phải chèn customer cùng với đơn mới (§12) |
| 05/11 | Chấp nhận chỉ 3 deal có `won_date` ≤ 2017-12-31 sau nạp ban đầu; dashboard dựng trên trạng thái cuối sau khi chạy hết các đợt incremental | Funnel "lấp đầy dần" qua các đợt incremental là điểm để trình bày |
| 05/11 | `oltp.order_reviews` dùng khoá chính ghép (`review_id`, `order_id`) | `review_id` lặp giữa các đơn nên không làm PK riêng được |
| 05/11 | Máy của Phú dùng **PostgreSQL 18.6**, giữ nguyên, không cài lại bản 16 | Tài liệu ghi "PostgreSQL 18 (16+ đều chạy được)"; code không dùng tính năng riêng của một bản; đã chạy thật P0 trên 18.6 |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** `dim_customer` dùng **SCD2** | Chỉ 250 / 96.096 khách đổi zip (0,26%) nên SCD2 thêm 256 dòng (+0,27%); là ví dụ SCD thật để trình bày (EDA câu a) |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** D6 gồm **2 trang**: (1) funnel theo kênh, (2) seller từ funnel có cảnh báo cỡ mẫu. 462 deal "chốt nhưng chưa bán" vẫn có dòng trong `dim_seller` (địa chỉ Unknown, `is_from_funnel = true`) và được hiển thị như một kết quả, không phải lỗi | Chỉ 380 / 842 deal (45,1%) có đơn, GMV 4,99% GMV sàn (EDA câu b) |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** `fact_seller_monthly` lưu **dày đặc** đến tháng cuối có đơn; dashboard lọc 2017-01 → 2018-08 | 36.583 dòng dày đặc so với 16.441 dòng thưa; đo được seller ngừng bán (EDA câu c) |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** nhóm ngành hàng dùng `docs/category_group_draft.csv` với 2 chỗ sửa: tách `pet_shop` thành nhóm **Pet**; đổi tên "Auto & Tools" thành **"Auto, Tools & Construction"** → 13 nhóm kể cả Unknown | Bản chốt nằm ở `seeds/category_group.csv` (EDA câu d) |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** zip của customers/sellers thiếu trong geolocation → vẫn tạo dòng `dim_geography` từ city/state, `latitude`/`longitude` = NULL | 157 zip khách + 7 zip seller; 0,28% số đơn (EDA câu e) |
| 05/11 | **Chốt 05/11 (Phú); nhóm có thể xem lại trước mốc chốt thiết kế 12/11:** giữ mốc nạp ban đầu **2017-12-31** | 45.430 đơn, 2.002 MQL, 3 deal; còn 8 đợt incremental hằng tháng đến 2018-08 (EDA câu f) |
| 05/11 | Điều chỉnh đặc tả: `fact_order_fulfillment` thêm `promised_days` (= ngày dự kiến − ngày mua); thêm KPI "ngày hứa giao TB so với ngày giao thực tế" | Ngày dự kiến quá rộng rãi (91,9% đơn giao sớm hơn dự kiến, trung vị sớm 12 ngày) nên cần so sánh số ngày hứa với số ngày thực tế (dùng cho D3) |
| 05/11 | Điều chỉnh đặc tả: `dim_lead_origin` tách `unknown` thành nhóm kênh riêng **Unknown** (không gộp với `other`) | `origin = unknown` có tỷ lệ chốt cao nhất (16,7%), gộp với `other` (2,7%) sẽ che mất sự khác biệt |
| 05/11 | Làm rõ `dim_geography` (P4): zip chỉ có toạ độ ngoài bbox vẫn có dòng (lat/lng NULL, city/state theo mode của các điểm đó). Trước đó 4 zip như vậy bị bỏ sót (dim 19.174 thay vì 19.178 dòng khi nạp đủ dữ liệu) | ODS giữ zip với `n_points = 0`; thêm test đối soát số zip dim = số zip trong staging ∪ customers ∪ sellers |
| 05/11 | Làm rõ cách tính fact (P4): `is_delivered` = status `delivered` và có ngày giao; `is_canceled` = status `canceled`; `dq_flag_count` = cờ ODS + số khoảng thời gian bị đặt NULL; `fact_seller_monthly.gmv/freight` chỉ tính đơn không thuộc nhóm Failed (khớp KPI GMV), `orders/items` tính mọi đơn; `seller_gmv_first_90d` = GMV (không Failed) trong 90 ngày kể từ ngày đơn đầu; thêm bảng `etl_log.fact_load_issue` | Chỉ làm rõ định nghĩa, không đổi tên bảng/cột của đặc tả |
| 05/11 | Mở rộng `dim_date` đến **2020-12-31** (1.827 ngày + Unknown) | 4 dòng hàng (3 đơn) có `shipping_limit_date` năm 2020 không còn nhận khoá −1 |
| 05/11 | Làm rõ nạp tăng dần (P5): (1) `simulate_increment` nạp mọi bản ghi nguồn có mốc thời gian ≤ ngày `--until` mà nguồn chưa có (nạp cả MQL cha của deal nếu `first_contact_date` muộn hơn `won_date`); cần **11 đợt hằng tháng (01/2018 → 11/2018)** để hết dữ liệu nguồn vì deal kéo dài tới 11/2018 (8 đợt đầu mới tới 08/2018); (2) `mql` và `closed_deals` được extract theo "chưa có trong staging" thay vì watermark ngày (tránh bỏ sót MQL khi deal đăng ký trước ngày liên hệ); watermark chỉ còn dùng cho `orders`; (3) dòng bị loại vì mồ côi (`orphan:`) được **thử lại** ở các đợt sau khi cha đã tới, và biến mất khỏi `etl_log.rejected_rows` khi đã nạp; (4) thêm `etl_log.batch_metrics`, `v_run_summary`, `v_dq_summary`, `v_rejected_summary` cho D7 | Kết quả incremental phải bằng full (so sánh số dòng, tổng tiền và checksum nội dung trên khoá tự nhiên) |
| 05/11 | Làm rõ KPI và data mart (P6): `Orders` = số đơn **có doanh thu** (distinct `order_id` của các đơn không thuộc nhóm Failed, cùng phạm vi với GMV) để `AOV = GMV ÷ Orders` nhất quán; `Orders placed` = mọi đơn đã đặt (`fact_order_fulfillment`); mart đặt tên `v_*`, các view nặng (RFM, cohort, scorecard seller, seller theo kênh) là MATERIALIZED VIEW làm mới bằng `dw.refresh_marts` giữa bước fact và test; trong Power BI bỏ dòng `date_key = -1` của `dim_date` và thêm cột `InWindow` (2017-01 → 2018-08) làm bộ lọc trang | Không đổi schema `dw`; thêm 13 file CSV mart vào `exports/powerbi/` |
| 05/11 | P7: hàm `dw.haversine_km` và `mart_fulfillment.v_shipping_distance` (khoảng cách seller → khách cho từng dòng hàng; dòng thiếu toạ độ giữ `distance_km` NULL); thêm `mart_sales.v_geo_state`, `v_geo_zip` cho bản đồ; `scripts/rebuild_all.py` dựng lại toàn bộ bằng một lệnh | Không đổi schema `dw`; `sql/70_geo` chạy trong `setup_db`; xuất thêm 2 file CSV (37 file) |
| 07/11 | Thêm cột `is_delivered smallint` vào `dw.fact_review` (lấy từ `fact_order_fulfillment.is_delivered`; không có fulfillment → 0) | Measure `Avg review - on time` và `Avg review - late delivery` chỉ tính đơn đã giao; trước đó đơn chưa giao (2.871 review) bị tính vào nhóm "đúng hạn" nên điểm là 4,21 thay vì 4,29. Thêm test đối soát `is_delivered` với `fact_order_fulfillment` và test EDA điểm đúng hạn 4,29 |
| 07/11 | Làm rõ §9: tách `Orders` (đơn có doanh thu, không Failed) và `Orders placed` (mọi đơn); `Late rate` = đơn giao trễ ÷ đơn đã giao, viết `DIVIDE([Late orders], [Delivered orders])` thay cho `1 - [On-time rate]` | Giá trị không đổi, định nghĩa không còn phụ thuộc measure khác |
| 07/11 | `dim_seller.first_sale_date` chỉ lấy đơn **không thuộc nhóm Failed** (join `dim_order_status`); lý do: đơn bị huỷ / không có sẵn không phải là bán được hàng, khớp định nghĩa GMV. Sửa theo: `fact_lead_funnel.first_sale_date_key`, `has_first_sale`, `days_won_to_first_sale`, `seller_gmv_first_90d` (cửa sổ 90 ngày bắt đầu từ ngày đơn đầu không Failed); `fact_seller_monthly.months_since_first_sale` tính từ tháng của `first_sale_date` (âm ở tháng trước đó chỉ có đơn Failed, NULL nếu seller chưa bán được; cột cho phép NULL), lưới tháng vẫn bắt đầu từ tháng có đơn đầu ở mọi trạng thái để không bỏ sót đơn Failed | Toàn kho: 62 trong 3.095 seller có đơn đổi `first_sale_date` (42 seller chỉ có đơn Failed chuyển thành NULL, 20 seller dời sang ngày muộn hơn); còn 3.053 seller có `first_sale_date`. Seller của funnel: 2 seller đổi (1 seller chỉ có đơn Failed mất `first_sale`; 1 seller dời từ 2018-08-06 sang 2018-08-10). `Sellers with first sale` 380 → 379, `Won to first sale rate` 45,1% → 45,0%, `Avg days won to first sale` 51,8 → 51,9, `Σ seller_gmv_first_90d` 538.271,72 không đổi. Con số 380 / 842 (45,1%) trong EDA vẫn đúng vì EDA đếm seller có đơn ở mọi trạng thái. Sửa test `dim_seller.first_sale_date` và test tháng đầu của `fact_seller_monthly`; test EDA đổi thành "seller của funnel có ít nhất một đơn (mọi trạng thái) = 380" |
| 08/11 | Mọi procedure nạp dimension (`sql/40_dw/030_dim_procs.sql`) chèn theo `ORDER BY` khoá tự nhiên (geography: zip; customer: `customer_unique_id`, `effective_from`; seller: `seller_id`; product: `product_id`; order_status, payment_type, lead_origin: giá trị tự nhiên; lead_profile: 7 cột thuộc tính; sales_rep: `rep_role`, `rep_id`); lý do: trước đó thứ tự chèn (và vì vậy giá trị khoá thay thế) phụ thuộc kế hoạch truy vấn, riêng `dim_sales_rep` đổi khoá giữa hai lần dựng | Hai lần `rebuild_all.py --drop` liên tiếp cho cùng giá trị khoá ở cả 10 dimension và 6 fact; `compare_databases.py --keys` so cả giá trị khoá (không dùng khi so nạp tăng dần với nạp full vì hai cách nạp cấp khoá theo thứ tự khác nhau) |
| 12/11 | Mốc chốt thiết kế: xem lại các dòng "Chốt 05/11" ở trên; mọi thay đổi sau đó phải cập nhật file này trước rồi mới sửa code | |

---

## 1. Bối cảnh và mục tiêu

**Doanh nghiệp:** Olist – sàn kết nối người bán nhỏ (seller) với các sàn TMĐT lớn ở Brazil.
**Chủ đề:** Order Management (Quản lý đơn hàng), theo khung Kimball – *The Data Warehouse Toolkit*, chương Order Management:
giao dịch đơn hàng mức dòng, chu trình xử lý đơn (order fulfillment pipeline), thanh toán, mức hài lòng sau giao.

**Mở rộng với Marketing Funnel:** Olist không chỉ bán hàng mà còn phải *thu hút seller* về sàn. Bộ Marketing Funnel
ghi lại quá trình một doanh nghiệp đăng ký quan tâm (MQL – Marketing Qualified Lead) → được đội sales chốt thành seller
(closed deal) → bắt đầu bán hàng. Nối qua `seller_id`, kho dữ liệu trả lời được câu hỏi xuyên quy trình:
*"Seller đến từ kênh marketing nào thì sau này bán được nhiều và giao đúng hạn hơn?"*

**Câu hỏi phân tích chính**

| Nhóm | Câu hỏi |
| --- | --- |
| Bán hàng | Doanh thu (GMV), số đơn, AOV theo thời gian / danh mục / vùng; tăng trưởng MoM, YoY; quy luật 80/20 |
| Xử lý đơn | Đơn mất bao lâu ở từng chặng (duyệt → bàn giao vận chuyển → giao khách)? Tỷ lệ trễ hạn, hủy? Vùng nào chậm? |
| Thanh toán | Cơ cấu hình thức thanh toán, số kỳ trả góp |
| Trải nghiệm khách | Giao trễ ảnh hưởng điểm review thế nào? Khách có quay lại không? |
| Seller | Seller nào doanh thu cao nhưng hay trễ? |
| Thu hút seller | Tỷ lệ chuyển đổi MQL → seller theo kênh, thời gian chốt deal, seller mới mất bao lâu để có đơn đầu tiên, GMV của seller theo kênh thu hút |

---

## 2. Nguồn dữ liệu

Hai hệ thống nguồn được mô phỏng như hai hệ thống CNTT riêng biệt:

| Hệ thống nguồn | Schema mô phỏng | Bộ Kaggle | Ghi chú |
| --- | --- | --- | --- |
| Hệ thống bán hàng (OLTP) | `oltp` | `olistbr/brazilian-ecommerce` (9 file) | ~99k đơn, 09/2016 – 10/2018 |
| Hệ thống CRM / Marketing | `crm` | `olistbr/marketing-funnel-olist` (2 file) | ~8.000 MQL, ~840 deal |

### 2.1 Bộ Brazilian E-Commerce (số dòng gần đúng, đo lại khi nạp)

| File | Dòng | Cột |
| --- | --- | --- |
| olist_orders_dataset.csv | 99.441 | order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date |
| olist_order_items_dataset.csv | 112.650 | order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value |
| olist_order_payments_dataset.csv | 103.886 | order_id, payment_sequential, payment_type, payment_installments, payment_value |
| olist_order_reviews_dataset.csv | 99.224 | review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp |
| olist_customers_dataset.csv | 99.441 | customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state |
| olist_sellers_dataset.csv | 3.095 | seller_id, seller_zip_code_prefix, seller_city, seller_state |
| olist_products_dataset.csv | 32.951 | product_id, product_category_name, product_name_lenght, product_description_lenght, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm |
| olist_geolocation_dataset.csv | 1.000.163 | geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state |
| product_category_name_translation.csv | 71 | product_category_name, product_category_name_english |

### 2.2 Bộ Marketing Funnel

| File | Dòng | Cột |
| --- | --- | --- |
| olist_marketing_qualified_leads_dataset.csv | ~8.000 | mql_id, first_contact_date, landing_page_id, origin |
| olist_closed_deals_dataset.csv | ~842 | mql_id, seller_id, sdr_id, sr_id, won_date, business_segment, lead_type, lead_behaviour_profile, has_company, has_gtin, average_stock, business_type, declared_product_catalog_size, declared_monthly_revenue |

**Quan hệ:** `closed_deals.mql_id → mql.mql_id` (1–0..1); `closed_deals.seller_id → sellers.seller_id`.
Chỉ một phần seller trong closed deals có đơn hàng trong bộ e-commerce (đo con số chính xác ở bước EDA – đây là một phát hiện đáng trình bày).

> Lưu ý dung lượng: bộ Marketing Funnel chỉ vài MB, nên tổng dữ liệu vẫn ~120 MB. Giá trị của nó là **thêm một quy trình nghiệp vụ và một hệ thống nguồn thứ hai** (tích hợp đa nguồn), không phải tăng dung lượng.

### 2.3 Lỗi dữ liệu đã biết (đầu vào cho tầng ODS)

| Bảng | Vấn đề | Xử lý ở ODS |
| --- | --- | --- |
| Mọi bảng có zip | Kiểm tra zip có bị mất số 0 đầu không. **Với bản CSV hiện tại không có lỗi**: kiểm bằng SQL trên `olist_full`, cả 99.441 zip của customers, 3.095 của sellers và 1.000.163 của geolocation đều đúng 5 chữ số (không có giá trị ngắn hơn hay chứa ký tự khác); lần lượt 23.995, 1.027 và 245.733 giá trị bắt đầu bằng `0` | `oltp` lưu `text`; ODS vẫn chuẩn hóa `char(5)`, `lpad(...,5,'0')` để phòng thủ |
| geolocation | Nhiều tọa độ cho một zip; tọa độ ngoài Brazil; tên thành phố lệch dấu / hoa thường | Lọc bbox Brazil (lat −33.75…5.27, lng −73.99…−34.79); gom theo zip lấy **median** lat/lng, **mode** city/state; city chuẩn hóa `lower(unaccent(trim()))` |
| customers / sellers | Tên thành phố lệch dấu | Chuẩn hóa như trên |
| products | Cột sai chính tả `*_lenght`; `product_category_name` rỗng; thiếu kích thước/cân nặng | Đổi tên cột `*_length`; danh mục rỗng → `'unknown'`; số đo thiếu giữ NULL + cờ `dq_missing_dimensions` |
| translation | Thiếu bản dịch `pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos` | Bổ sung thủ công qua seed |
| orders | Thiếu `approved_at` / `delivered_*`; status `delivered` nhưng không có ngày giao; thứ tự mốc thời gian sai (vd carrier < approved) | Không xóa đơn. Gắn cờ `dq_flags` (text[]); các khoảng thời gian âm → NULL ở fact |
| payments | `payment_type = 'not_defined'`; `payment_installments = 0` | Giữ loại `not_defined`; installments 0 → 1 + cờ |
| reviews | `review_id` lặp (một review gắn nhiều đơn, hoặc trùng dòng) | Khử trùng trên cặp (`review_id`, `order_id`), giữ bản có `review_answer_timestamp` mới nhất |
| customers | `customer_id` sinh mới theo từng đơn | Dùng `customer_unique_id` làm natural key của khách |
| mql | `origin` NULL | → `'unknown'` |
| closed_deals | Nhiều cột phân loại NULL; `declared_*` = 0 | NULL → `'unknown'` cho cột phân loại; giữ số 0 nhưng thêm cờ |
| Mọi bảng | Dòng mồ côi (FK không tồn tại) | Ghi vào `etl_log.rejected_rows`, không nạp |

---

## 3. Kiến trúc các lớp

```
CSV (Kaggle) ──setup──► oltp (bán hàng) ┐
CSV (Kaggle) ──setup──► crm  (marketing) ┘
        │ extract (Python, full + incremental theo watermark)
        ▼
staging  (stg_*: bản sao thô, thêm cột load_batch_id, loaded_at)
        │ transform (SQL procedure)
        ▼
ods      (đã làm sạch, chuẩn hóa, có dq_flags)        ← "Operational Data Store"
        │ load (SQL procedure, SCD, surrogate key)
        ▼
dw       (star schema / constellation: dim_* + fact_*)
        │ view tổng hợp theo chủ đề
        ▼
mart_sales · mart_fulfillment · mart_cx · mart_acquisition
        │
        ▼
Power BI (semantic model + DAX) → 7 dashboard → Publish to web

etl_log: job_run, rejected_rows, watermark  (giám sát → dashboard D7)
```

**Công nghệ:** PostgreSQL 18 (16+ đều chạy được) cài trực tiếp trên máy (không dùng Docker, không PostGIS), extension `unaccent`;
Python 3.11 (pandas, SQLAlchemy, psycopg2); SQL stored procedure (PL/pgSQL); Git/GitHub; Power BI Desktop/Service.

**Cầu nối sang Power BI:** chỉ Phú chạy database, nên `dw`, `mart_*` và `etl_log` được xuất ra CSV (`exports/powerbi/`)
sau mỗi lần chạy pipeline; cả nhóm dựng Power BI ở chế độ Import từ các file này. Publish to web cũng cần chế độ Import.

---

## 4. Bus matrix

| Quy trình nghiệp vụ → Bảng fact | Loại fact | Date | Customer | Seller | Product | Geography | Order status | Payment type | Lead origin | Lead profile | Sales rep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Giao dịch đơn hàng → `fact_order_item` | Transaction | ✓ ×2 | ✓ | ✓ | ✓ | ✓ ×2 (khách, seller) | ✓ | | | | |
| Xử lý đơn → `fact_order_fulfillment` | Accumulating snapshot | ✓ ×5 | ✓ | | | ✓ | ✓ | | | | |
| Thanh toán → `fact_payment` | Transaction | ✓ | ✓ | | | | | ✓ | | | |
| Đánh giá → `fact_review` | Transaction | ✓ ×2 | ✓ | | | | | | | | |
| Thu hút seller → `fact_lead_funnel` | Accumulating snapshot | ✓ ×3 | | ✓ | | | | | ✓ | ✓ | ✓ ×2 (SDR, SR) |
| Hiệu suất seller → `fact_seller_monthly` | Periodic snapshot | ✓ (tháng) | | ✓ | | | | | | | |

`dim_seller` là **conformed dimension** nối hai quy trình bán hàng và thu hút seller. Kho có đủ 3 loại fact của Kimball.

---

## 5. Quy ước chung cho dimension

- Surrogate key: `<tên>_key INTEGER GENERATED ALWAYS AS IDENTITY` (riêng `dim_date.date_key` là số `yyyymmdd`). Mỗi câu `INSERT` của procedure nạp dim có `ORDER BY` khoá tự nhiên để khoá thay thế giống nhau giữa các lần dựng.
- Mỗi dim có **dòng Unknown** với key `-1` (chèn bằng `OVERRIDING SYSTEM VALUE`); fact không bao giờ có FK NULL.
- Cột kỹ thuật: `dw_created_at timestamptz default now()`, `dw_updated_at timestamptz`.
- Natural key có ràng buộc UNIQUE (với SCD2: UNIQUE trên (natural key, effective_from)).

## 6. Dimension

### 6.1 `dw.dim_date` (role-playing)
Phạm vi 2016-01-01 → 2020-12-31 (1.827 dòng) + dòng `-1`.

| Cột | Kiểu | Ghi chú |
| --- | --- | --- |
| date_key | int PK | yyyymmdd |
| full_date | date | |
| day_of_month, day_of_week (1=Thứ Hai), day_name | | |
| week_of_year (ISO), month, month_name, quarter, year | | |
| year_month | char(7) | `2017-11` |
| year_quarter | char(7) | `2017-Q4` |
| is_weekend | bool | |
| is_holiday_br, holiday_name | bool, text | Dùng package Python `holidays` (Brazil) |
| is_black_friday | bool | Thứ Sáu sau thứ Năm thứ 4 của tháng 11 (2016-11-25, 2017-11-24, 2018-11-23) |

Phân cấp: Ngày → Tuần; Ngày → Tháng → Quý → Năm.
Role-playing qua view: `dw.v_dim_purchase_date`, `v_dim_approved_date`, `v_dim_carrier_date`, `v_dim_delivered_date`, `v_dim_estimated_date`, `v_dim_first_contact_date`, `v_dim_won_date`… (hoặc dùng role-playing trực tiếp trong Power BI).

### 6.2 `dw.dim_geography`
Grain: 1 zip code prefix. ~19.000 dòng.

| Cột | Ghi chú |
| --- | --- |
| geography_key | PK |
| zip_code_prefix | char(5), UNIQUE |
| city | đã chuẩn hóa |
| state_code | 2 ký tự (SP, RJ…) |
| state_name | từ seed |
| region | Norte / Nordeste / Centro-Oeste / Sudeste / Sul |
| country | 'Brazil' |
| latitude, longitude | median sau khi lọc bbox; NULL nếu zip không có trong geolocation hoặc mọi điểm của zip nằm ngoài bbox |
| *(không có cột geom – không dùng PostGIS; khoảng cách tính bằng haversine trên latitude/longitude)* | |

Phân cấp: Zip → Thành phố → Bang → Vùng → Quốc gia.
Nguồn: hợp nhất zip từ geolocation + customers + sellers (zip có ở customers/sellers mà không có ở geolocation vẫn phải có dòng, lấy city/state từ bảng đó).

Seed `state_region.csv` (27 bang):
- Norte: AC Acre, AP Amapá, AM Amazonas, PA Pará, RO Rondônia, RR Roraima, TO Tocantins
- Nordeste: AL Alagoas, BA Bahia, CE Ceará, MA Maranhão, PB Paraíba, PE Pernambuco, PI Piauí, RN Rio Grande do Norte, SE Sergipe
- Centro-Oeste: DF Distrito Federal, GO Goiás, MT Mato Grosso, MS Mato Grosso do Sul
- Sudeste: ES Espírito Santo, MG Minas Gerais, RJ Rio de Janeiro, SP São Paulo
- Sul: PR Paraná, RS Rio Grande do Sul, SC Santa Catarina

### 6.3 `dw.dim_customer` (SCD loại 2)
Grain: 1 phiên bản địa chỉ của 1 khách (`customer_unique_id`). ~96.000 khách, vài nghìn dòng có nhiều phiên bản.

| Cột | Ghi chú |
| --- | --- |
| customer_key | PK |
| customer_unique_id | natural key |
| zip_code_prefix, city, state_code | thuộc tính theo dõi SCD2 |
| geography_key | FK → dim_geography |
| effective_from, effective_to | date; bản hiện hành `effective_to = '9999-12-31'` |
| is_current | bool |
| version_no | int |

Cách dựng SCD2 từ dữ liệu tĩnh: với mỗi `customer_unique_id`, sắp các đơn theo `order_purchase_timestamp`; mỗi lần zip đổi so với đơn trước → mở phiên bản mới, `effective_from` = ngày mua của đơn đó. Phiên bản đầu `effective_from = '1900-01-01'`.
Fact tra `customer_key` theo phiên bản có hiệu lực tại ngày mua.
Bảng ánh xạ ở ODS: `ods.customer_map(customer_id, customer_unique_id)`.

### 6.4 `dw.dim_seller` (SCD loại 1, conformed)
Grain: 1 seller. 3.095 dòng (+ seller chỉ có trong closed_deals nếu có – đo ở EDA; nếu có thì vẫn tạo dòng với địa chỉ Unknown).

| Cột | Ghi chú |
| --- | --- |
| seller_key | PK |
| seller_id | natural key |
| zip_code_prefix, city, state_code, geography_key | |
| is_from_funnel | bool – seller có trong closed_deals |
| mql_id | NULL nếu không từ funnel |
| acquisition_origin | origin của MQL, `'not_from_funnel'` nếu không |
| acquisition_channel | nhóm kênh (xem 6.9) |
| business_segment, lead_type, business_type | từ closed_deals |
| won_date | date |
| first_sale_date | ngày mua của đơn đầu tiên **không thuộc nhóm Failed** có seller này (tính sau khi nạp fact_order_item, cập nhật lại); NULL nếu mọi đơn của seller đều Failed |

Phân cấp: Seller → Thành phố → Bang → Vùng; Seller → Kênh thu hút → Origin.

### 6.5 `dw.dim_product`
Grain: 1 sản phẩm. 32.951 dòng.

| Cột | Ghi chú |
| --- | --- |
| product_key | PK |
| product_id | natural key |
| category_name_pt | `'unknown'` nếu rỗng |
| category_name_en | từ translation + seed bổ sung |
| category_group | ~10 nhóm, từ seed `category_group.csv` |
| weight_g, length_cm, height_cm, width_cm | |
| volume_cm3 | length × height × width |
| size_class | S (<500 g), M (<2 kg), L (<10 kg), XL (≥10 kg), Unknown |
| photos_qty, name_length, description_length | |

Phân cấp: Sản phẩm → Danh mục → Nhóm ngành hàng.
Nhóm ngành hàng (13 nhóm, chốt 05/11, nguồn `seeds/category_group.csv`): Home & Furniture; Health & Beauty; Electronics & Computers; Fashion & Accessories; Sports & Leisure; Toys & Baby; Books, Media & Music; Food & Drinks; Auto, Tools & Construction; Office & Stationery; Gifts & Others; Pet; Unknown.

### 6.6 `dw.dim_order_status`
8 trạng thái + Unknown.

| order_status | status_group | is_final |
| --- | --- | --- |
| delivered | Completed | true |
| shipped | In progress | false |
| invoiced, processing, approved, created | In progress | false |
| canceled, unavailable | Failed | true |

### 6.7 `dw.dim_payment_type`
credit_card (Card), debit_card (Card), boleto (Bank slip), voucher (Voucher), not_defined (Unknown).
Cột: payment_type_key, payment_type, payment_group, display_name.

### 6.8 `dw.dim_lead_origin`
Grain: 1 giá trị `origin` của MQL.

| origin | channel_group |
| --- | --- |
| organic_search, direct_traffic, referral | Organic |
| paid_search, display, other_publicities | Paid |
| social | Social |
| email | Email |
| other | Other |
| unknown | Unknown |

### 6.9 `dw.dim_lead_profile` (junk dimension)
Grain: 1 tổ hợp khác nhau của các thuộc tính deal: business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock. NULL → `'unknown'`. Dòng `-1` cho MQL chưa chốt.

### 6.10 `dw.dim_sales_rep` (role-playing: SDR và SR)
Grain: 1 mã nhân viên + vai trò. Cột: sales_rep_key, rep_id, rep_role (`SDR` / `SR`). Vài chục dòng.

---

## 7. Fact

Quy ước: measure kiểu `numeric(12,2)` cho tiền (BRL), `numeric(10,2)` cho số ngày/giờ; mọi FK NOT NULL (dùng `-1`);
cột `etl_batch_id`; khoảng thời gian tính ra âm (do lỗi nguồn) → NULL và tăng bộ đếm DQ.

### 7.1 `dw.fact_order_item` – Transaction
**Grain:** 1 dòng sản phẩm trong 1 đơn (`order_id`, `order_item_id`). ~112.650 dòng.

| Cột | Ghi chú |
| --- | --- |
| order_id, order_item_id | degenerate dimension; PK (order_id, order_item_id) |
| purchase_date_key | FK dim_date |
| shipping_limit_date_key | FK dim_date |
| customer_key | phiên bản SCD2 tại ngày mua |
| customer_geography_key, seller_geography_key | FK dim_geography (role-playing) |
| seller_key, product_key, order_status_key | |
| price, freight_value | additive |
| item_total | price + freight_value |

### 7.2 `dw.fact_order_fulfillment` – Accumulating snapshot
**Grain:** 1 đơn hàng. ~99.441 dòng. Cập nhật (UPSERT theo `order_id`) mỗi khi đơn đi qua mốc mới.

| Cột | Ghi chú |
| --- | --- |
| order_id | PK, degenerate |
| customer_key, customer_geography_key, order_status_key | |
| purchase_date_key, approved_date_key, carrier_date_key, delivered_date_key, estimated_date_key | 5 role-playing date; mốc chưa xảy ra = −1 |
| purchase_ts, approved_ts, carrier_ts, delivered_ts, estimated_ts | timestamp gốc để tính lag |
| approval_hours | approved − purchase (giờ) |
| handling_days | carrier − approved (ngày) |
| transit_days | delivered − carrier (ngày) |
| lead_days | delivered − purchase (ngày) |
| delay_days | delivered::date − estimated::date (âm = sớm) |
| promised_days | estimated::date − purchase::date (ngày; số ngày Olist hứa giao) |
| is_delivered, is_late, is_canceled | 0/1 (int để cộng được). `is_delivered` = status `delivered` và có ngày giao; `is_late` = đã giao và `delay_days > 0`; `is_canceled` = status `canceled` |
| item_count, seller_count | |
| order_value, freight_total | Σ từ order items |
| payment_total | Σ từ payments |
| dq_flag_count | số cờ lỗi của đơn ở ODS + số khoảng thời gian bị đặt NULL vì âm |

### 7.3 `dw.fact_payment` – Transaction
**Grain:** 1 lần thanh toán (`order_id`, `payment_sequential`). ~103.886 dòng.
Cột: order_id, payment_sequential (DD), purchase_date_key, customer_key, payment_type_key, payment_installments, payment_value.

### 7.4 `dw.fact_review` – Transaction
**Grain:** 1 review gắn với 1 đơn (`review_id`, `order_id`). ~99k dòng.
Cột: review_id, order_id (DD), review_creation_date_key, review_answer_date_key, customer_key, review_score (1–5),
is_negative (score ≤ 2), has_comment_title, has_comment_message, comment_length, response_hours, delivered_late (0/1, lấy từ fact_order_fulfillment – thuận tiện phân tích trễ → điểm), is_delivered (0/1, lấy từ fact_order_fulfillment: 1 nếu đơn đã giao, tức có `order_delivered_customer_date`). Khi so sánh điểm review của đơn đúng hạn với đơn trễ phải lọc `is_delivered = 1`, vì đơn chưa giao cũng có `delivered_late = 0` nhưng chưa thể gọi là đúng hạn.

### 7.5 `dw.fact_lead_funnel` – Accumulating snapshot
**Grain:** 1 MQL. ~8.000 dòng.

| Cột | Ghi chú |
| --- | --- |
| mql_id | PK, degenerate |
| landing_page_id | degenerate |
| first_contact_date_key, won_date_key, first_sale_date_key | role-playing; −1 nếu chưa xảy ra. `first_sale_date_key` lấy từ `dim_seller.first_sale_date` (đơn đầu không Failed) |
| lead_origin_key, lead_profile_key | |
| seller_key | −1 nếu chưa chốt |
| sdr_key, sr_key | FK dim_sales_rep; −1 nếu chưa chốt |
| is_won | 0/1 |
| has_first_sale | 0/1 |
| days_to_close | won_date − first_contact_date |
| days_won_to_first_sale | first_sale_date − won_date |
| declared_product_catalog_size, declared_monthly_revenue | non-additive, dùng AVG/median |
| seller_gmv_first_90d | GMV (đơn không thuộc nhóm Failed) của seller trong 90 ngày kể từ `first_sale_date` (ngày 0…89), nối với fact_order_item; NULL nếu seller chưa có đơn |

### 7.6 `dw.fact_seller_monthly` – Periodic snapshot
**Grain:** 1 seller × 1 tháng, **dày đặc** từ tháng có đơn đầu tiên của seller (mọi trạng thái, để không bỏ sót đơn Failed) đến tháng cuối cùng có đơn hàng trong dữ liệu (để tổng GMV khớp fact_order_item; dashboard tự lọc giai đoạn hiển thị).
`month_date_key` = date_key của ngày 1 trong tháng.

| Cột | Ghi chú |
| --- | --- |
| month_date_key, seller_key | PK |
| orders, items | 0 nếu tháng không có đơn |
| gmv, freight | chỉ tính đơn không thuộc nhóm Failed (khớp KPI GMV); `orders`, `items`, `canceled_orders` tính mọi đơn |
| delivered_orders, late_orders, late_rate | |
| canceled_orders | |
| avg_review_score | NULL nếu không có review |
| is_active | orders > 0 |
| months_since_first_sale | số tháng kể từ tháng của `dim_seller.first_sale_date` (0 = tháng có đơn bán được đầu tiên); âm nếu là tháng trước đó chỉ có đơn Failed; NULL nếu seller chưa có đơn bán được (cột cho phép NULL) |

---

## 8. Data mart (schema riêng, dạng view; view nặng có thể là materialized view)

| Mart | Đối tượng | Nội dung |
| --- | --- | --- |
| `mart_sales` | `v_sales_daily`, `v_sales_category_month`, `v_sales_state_month`, `v_category_pareto` | GMV, đơn, AOV, theo ngày / danh mục / bang; Pareto danh mục |
| `mart_fulfillment` | `v_fulfillment_order`, `v_fulfillment_state_month`, `v_status_funnel` | lead time từng chặng, tỷ lệ trễ, hủy theo bang/tháng |
| `mart_cx` | `v_review_vs_delay`, `v_payment_mix_month`, `v_customer_rfm`, `v_customer_cohort` | review vs trễ, cơ cấu thanh toán, RFM, cohort khách quay lại |
| `mart_acquisition` | `v_funnel_by_origin_month`, `v_seller_scorecard`, `v_seller_by_channel` | MQL → won → first sale theo kênh; scorecard seller; GMV theo kênh thu hút |

Lưu ý giai đoạn dữ liệu: đơn 2016 rất thưa và 09–10/2018 gần như trống → dashboard xu hướng lọc 2017-01 → 2018-08.

## 9. KPI chính (tính trong Power BI bằng DAX, đối chiếu bằng SQL ở mart)

| KPI | Định nghĩa |
| --- | --- |
| GMV | Σ price của đơn không ở nhóm Failed |
| Orders | COUNT DISTINCT order_id của các đơn **có doanh thu** (không thuộc nhóm Failed, cùng phạm vi với GMV) |
| AOV | GMV ÷ Orders |
| Orders placed | COUNT DISTINCT order_id của **mọi đơn đã đặt** (`fact_order_fulfillment`), kể cả đơn Failed; là mẫu số của Cancel rate |
| MoM %, YoY % | Time intelligence trên dim_date |
| Freight ratio | Σ freight_value ÷ Σ price |
| Cancel rate | Đơn status_group = Failed ÷ Orders placed |
| On-time rate | Đơn giao có delay_days ≤ 0 ÷ đơn đã giao |
| Late rate | Đơn giao trễ (`is_late = 1`) ÷ đơn đã giao (`is_delivered = 1`) = `DIVIDE([Late orders], [Delivered orders])` |
| Avg lead time / từng chặng | AVG lead_days, approval_hours, handling_days, transit_days |
| Ngày hứa giao TB so với ngày giao thực tế | AVG promised_days và AVG lead_days trên đơn đã giao; chênh lệch = AVG(promised_days − lead_days) (dương = giao sớm hơn hứa); dùng cho D3 |
| Avg review, % negative | AVG review_score; Σ is_negative ÷ số review. Điểm review theo đúng hạn / trễ chỉ tính đơn đã giao (`fact_review.is_delivered = 1`) |
| Repeat customer rate | Khách có ≥ 2 đơn ÷ tổng khách (theo customer_unique_id) |
| MQL → Won conversion | Σ is_won ÷ số MQL |
| Avg days to close | AVG days_to_close (won) |
| Won → first sale rate | Σ has_first_sale ÷ Σ is_won |

## 10. Dashboard (7)

| # | Dashboard | Loại | Nguồn chính |
| --- | --- | --- | --- |
| D1 | Executive Overview | Theo thời gian | mart_sales, fact_order_fulfillment |
| D2 | Sales & Product | Theo thời gian, OLAP | fact_order_item |
| D3 | Order Fulfillment | Vận hành | fact_order_fulfillment |
| D4 | Geography & Freight | OLAP | fact_order_item, dim_geography |
| D5 | Customer Experience | Thống kê | fact_review, fact_payment, mart_cx |
| D6 | Seller Acquisition & Performance | Vận hành | fact_lead_funnel, fact_seller_monthly |
| D7 | Data Quality & ETL Monitor | Vận hành hệ thống | etl_log |

Cả nhóm dựng một semantic model chung trong một file .pbix và chia nhau các dashboard (phân công làm sau). Phú cung cấp dữ liệu, `powerbi/measures.md` và `powerbi/model.md`.

## 11. Giám sát ETL (`etl_log`)

- `etl_log.job_run(run_id, batch_id, job_name, layer, target_table, started_at, finished_at, status, rows_read, rows_inserted, rows_updated, rows_rejected, message)`
- `etl_log.rejected_rows(id, batch_id, job_name, source_table, reason, record jsonb, logged_at)`
- `etl_log.watermark(source_table, last_value timestamptz, updated_at)` – cho incremental load
- `etl_log.dq_check(batch_id, check_name, target_table, expected, actual, passed, checked_at)` – kết quả kiểm thử sau mỗi lần chạy
- `etl_log.fact_load_issue(batch_id, fact_table, issue_type, detail, row_count, logged_at)` – khoá rơi về Unknown (`unknown_member`) và khoảng thời gian âm bị đặt NULL (`negative_interval`) khi nạp fact

## 12. Mô phỏng cập nhật (incremental)

Dữ liệu Kaggle là ảnh chụp tĩnh. Để có nội dung "tần suất cập nhật" và incremental load:
1. Nạp ban đầu vào `oltp`/`crm` mọi bản ghi có mốc thời gian ≤ **2017-12-31** (đơn theo `order_purchase_timestamp`, MQL theo `first_contact_date`; bảng tham chiếu nạp đủ). Bảng tham chiếu gồm `products`, `sellers`, `geolocation`, bảng dịch danh mục; **`customers` không phải bảng tham chiếu** – chỉ nạp khách có đơn trong khoảng thời gian, vì `customer_id` sinh theo từng đơn.
2. Script `simulate_increment --until YYYY-MM-DD` chèn thêm bản ghi của khoảng tiếp theo (mặc định 1 tháng) từ CSV vào `oltp`/`crm`. **Phải chèn `customers` cùng với đơn mới** (khách của các đơn đó), nếu không đơn mới vi phạm FK `orders.customer_id`.
3. ETL đọc theo watermark → chỉ lấy bản ghi mới; dim cập nhật SCD; fact transaction INSERT, accumulating snapshot UPSERT, periodic snapshot tính lại các tháng bị ảnh hưởng.
4. Mỗi lần chạy ghi `etl_log` → dashboard D7 hiển thị số bản ghi mới mỗi đợt.

Giới hạn cần nói rõ khi trình bày: bản ghi đơn được chèn với trạng thái cuối cùng trong CSV (không mô phỏng được trạng thái trung gian).

## 13. Kiểm thử chất lượng (chạy sau mỗi pipeline)

- Đối soát số dòng: oltp → staging → ods → dw (chênh lệch phải bằng số dòng bị reject).
- Đối soát tổng tiền: Σ price ở `oltp.order_items` = Σ price ở `fact_order_item` (+ phần bị reject).
- Unique grain của mọi fact; không có FK NULL; không có FK trỏ tới key không tồn tại.
- Mỗi dim có đúng 1 dòng `-1`; SCD2: mỗi `customer_unique_id` có đúng 1 dòng `is_current`, không chồng khoảng hiệu lực.
- fact_lead_funnel: `is_won = 1` ⇔ `won_date_key <> -1` ⇔ `seller_key <> -1`.

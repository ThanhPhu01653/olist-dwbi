# Người 3 – Kiến trúc, ETL, chiều khái niệm, data model và dashboard DB3

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io, cách hỏi Phú): [`README.md`](README.md). File này chỉ nói phần của Người 3.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | **3.2 Kiến trúc** · **3.3 ETL** · **3.4 Chiều khái niệm** · **3.5 Data model OLAP** |
| File slide | `slides/sections/02b-kien-truc-etl-model.tex` (3.2–3.5; 49 frame, file dài nhất) |
| Sơ đồ draw.io | `3-2_kien_truc_cac_lop` (có logo), `3-3_etl_jobs`, `3-5_data_model_logic`, `3-5_data_model_vat_ly`, `3-5_data_mart` |
| Dashboard | **DB3 Địa lý và phí vận chuyển** (OLAP: drill-down Vùng → Bang → Thành phố, drill-through, tooltip) |
| Việc riêng | chạy mã M trong `powerbi/power-query-vi-du.md`, chụp ảnh before/after |
| Thuyết trình | kiến trúc, ETL, chiều khái niệm, data model; giả định **khoảng 11 phút, 9 slide nói** (thời lượng chính thức chưa có, xem `README.md` mục 2) |
| Báo cáo (giai đoạn 2) | `3-2-kien-truc.tex`, `3-3-etl.tex`, `3-4-chieu-khai-niem.tex`, `3-5-data-model.tex` |

## 2. Barem chấm gì ở phần này

Các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu của thầy; dòng đỏ là chỗ nhóm khác bị trừ điểm):

**Kiến trúc khai thác**
- Phân tích chi tiết kiến trúc.
- Sử dụng logo minh hoạ.
- **Trình bày cho rõ kiến trúc hơn: hình vẽ giống luồng hơn là kiến trúc** (bị trừ).

**ETL / tiền xử lý**
- Tóm tắt các hoạt động ETL.
- Có data pipeline mô hình ETL job.
- Trình bày before/after của hoạt động ETL.
- Mô tả quá trình chuyển từ OLTP → OLAP.
- Sử dụng đa dạng công cụ ETL: Power Query + Python + SQL.
- Cách trình bày khiến người xem khó theo dõi và nắm bắt vấn đề; data pipeline chưa đủ chi tiết: **bổ sung ví dụ minh hoạ cho ETL** (bị trừ).

**Dimension / hệ thống chiều khái niệm**
- Thống kê số lượng dòng ở mỗi dimension.
- Phân dimension thành các nhóm cho dễ theo dõi.
- Trình bày; **hệ thống chiều khái niệm chưa đúng** (bị trừ).

**Data model OLAP (logic, vật lý)**
- Bố cục hài hoà.
- Phù hợp với logic dim, fact.
- Sử dụng màu sắc để phân tích trình bày rõ hơn.
- **Thiếu mô hình tổng thể vật lý** (bị trừ).

**Dashboard (liên quan DB3):** phân tích OLAP (slicer, drill-down); drill-through và tooltip để phân tích chi tiết; đơn vị tính và định dạng số.

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Kiến trúc DWH (slide 106–107) | 4 | một hình kiến trúc theo lớp, mỗi lớp liệt kê thành phần | đã có hình theo lớp (nháp), bảng các lớp. **Hơn nhóm 6:** một trang giải thích từng lớp và lý do chọn công nghệ; logo công nghệ; không vẽ thành luồng |
| ETL (slide 108–128) | 5 | bảng tóm tắt các giai đoạn (công cụ, kết quả); ETL từng bảng nguồn → staging; pipeline các job; OLTP → OLAP cho từng dimension và từng fact mỗi bảng một trang; ví dụ một bản ghi đi vào kho; kết quả nạp đối chiếu số dòng | đã có tóm tắt, sơ đồ job, before–after 6 bảng, một đơn thật đi qua các lớp, giám sát ETL, Power Query mẫu. **Cần làm:** mỗi dimension và mỗi fact một trang (nguồn, quy tắc, số dòng vào/ra); chạy mã M trong Power BI và chụp ảnh before/after |
| Dimension (slide 129–131) | 4 | bảng giá trị phân biệt theo từng cấp của mọi dimension | đã có bảng cấp và số giá trị; 303 tên thành phố trùng giữa các bang. **Hơn nhóm 6:** sơ đồ phân cấp; giải thích cấp nào hợp lệ; nhóm dimension (dùng chung, role-playing, SCD2, junk) |
| Data model OLAP (slide 132–134) | 5 | mô hình logic; mô hình vật lý; data marts kèm câu hỏi phân tích | đã có 3 hình nháp tương ứng và hiệu năng. **Cần làm:** vẽ lại bằng draw.io; fact và dimension khác màu |

Không được chép câu chữ, số liệu hay hình của nhóm 6.

## 3. Kiến thức cần nắm

**Kiến trúc theo lớp.** Kiến trúc trả lời "hệ thống gồm những thành phần nào, công nghệ nào, bao nhiêu bảng", nên vẽ các khối xếp tầng chứ không vẽ thành luồng. Sáu lớp của dự án (số trạng thái cuối):

| Lớp | Vai trò | Số bảng | Số dòng |
| --- | --- | ---: | ---: |
| Nguồn `oltp` + `crm` | hai hệ thống nguồn mô phỏng từ 11 file CSV | 9 + 2 | 1.559.764 |
| Staging `staging` | bản sao thô của nguồn, có mã lô nạp | 11 | 1.559.764 |
| ODS `ods` | dữ liệu đã làm sạch, có cờ chất lượng; dòng lỗi ghi vào `rejected_rows` | 18 | 678.183 |
| Kho `dw` | 10 chiều + 6 fact | 16 | 614.223 |
| Data mart `mart_*` | 4 mart, 17 view (4 là materialized view) | 17 view | – |
| Giám sát `etl_log` | nhật ký chạy, dòng bị loại, kiểm thử | 6 + 3 view | 2.546 |

Tách lớp giúp **đối soát**: nguồn = staging = ODS + dòng bị loại, với mọi bảng. Công nghệ: PostgreSQL 18, Python 3.11, SQL procedure (PL/pgSQL), Power BI, Git/GitHub. Lý do chọn: dữ liệu 1,56 triệu dòng chạy được trên laptop; biến đổi bằng SQL để nằm cạnh dữ liệu; Python để điều phối. Nhật ký chi tiết: `huong-dan/01-pipeline-bang-loi.md`.

**Staging và ODS.** *Staging* là bản sao thô của nguồn, giữ nguyên để đối chiếu. *ODS* (Operational Data Store) là lớp trung gian làm sạch: chuẩn hoá (cắt khoảng trắng, chữ thường, bỏ dấu), gắn cờ lỗi, hoặc loại có lý do. Ví dụ: 1.000.163 dòng toạ độ gom thành 19.178 mã bưu chính; 42 dòng toạ độ ngoài Brazil bị loại và ghi vào `etl_log.rejected_rows`; **không bao giờ xoá âm thầm**.

**Surrogate key (khoá thay thế).** Số nguyên tự sinh (`customer_key`, `seller_key`…) thay cho mã nguồn (`customer_id`, `seller_id`), vì mã nguồn có thể đổi, trùng giữa hai hệ thống, hoặc cần nhiều phiên bản cho cùng một thực thể (SCD2). Dòng **Unknown có khoá −1** bảo đảm fact không bao giờ có khoá rỗng. Ngày dùng `date_key` = số nguyên `yyyymmdd` (ví dụ `20171124`).

**SCD2 (Slowly Changing Dimension loại 2).** Khi thuộc tính đổi, đóng phiên bản cũ và mở phiên bản mới thay vì ghi đè, để đơn hàng gắn với địa chỉ **tại ngày mua**. Ở dự án: `dim_customer` giữ lịch sử mã bưu chính: 96.096 khách thật thành 96.339 dòng (236 khách đổi mã bưu chính, tức khoảng 0,26%); nạp bằng window function; fact tra khoá theo phiên bản có hiệu lực. `dim_seller` dùng SCD1 (ghi đè).

**Role-playing dimension (chiều đóng vai).** Một bảng chiều dùng nhiều vai trò trong cùng fact. `dim_date` đóng 11 vai: mua, duyệt, bàn giao, giao, dự kiến, liên hệ đầu, chốt, đơn đầu tiên…; `fact_order_fulfillment` có 5 khoá ngày. `dim_sales_rep` là một bảng cho hai vai trò SDR và SR. Trong Power BI: một quan hệ ngày active, các quan hệ khác inactive và bật bằng `USERELATIONSHIP`.

**Junk dimension (chiều rác).** Gom nhiều thuộc tính nhỏ, ít giá trị thành một chiều để fact gọn: `dim_lead_profile` gom 7 thuộc tính của deal (phân khúc, loại lead, hành vi, loại hình, có công ty, có GTIN, tồn kho) thành 503 dòng.

**Conformed dimension (chiều dùng chung).** Một chiều dùng được bởi nhiều fact với cùng nghĩa: `dim_date` (6 fact), `dim_seller` (3 fact, nối bán hàng với thu hút seller qua `seller_id`), `dim_customer` (4), `dim_geography` (2), `dim_order_status` (2). Đây là chỗ hai quy trình gặp nhau.

**Ba loại fact và grain.** *Grain* là "một dòng fact là gì". Transaction: `fact_order_item` (1 dòng hàng của 1 đơn, 112.650), `fact_payment` (1 lần thanh toán, 103.886), `fact_review` (1 review, 99.224). **Accumulating snapshot** (một dòng cập nhật dần theo các mốc): `fact_order_fulfillment` (1 đơn, 99.441, 5 mốc thời gian và các khoảng thời gian giữa chúng), `fact_lead_funnel` (1 MQL, 8.000, 3 mốc ngày). **Periodic snapshot** (chụp định kỳ): `fact_seller_monthly` (1 seller × 1 tháng, 36.583 dòng, lưu dày đặc để thấy seller ngừng bán).

**Chiều khái niệm (hệ thống chiều khái niệm).** Với mỗi chiều: các cấp phân cấp và số giá trị phân biệt của từng cấp, rồi kiểm tra phân cấp đúng. Ví dụ thời gian: 5 năm → 20 quý → 60 tháng → 1.827 ngày; địa lý: 5 vùng → 27 bang → 6.190 (bang, thành phố) → 19.177 mã bưu chính. **Kiểm tra hợp lệ:** *tháng phải đi kèm năm* (chỉ có 12 số tháng nhưng 60 cặp năm–tháng, nên dùng `year_month`); *thành phố phải đi kèm bang* (303 tên thành phố xuất hiện ở từ 2 bang trở lên, ví dụ `bom jesus` ở 6 bang); mã bưu chính xác định đúng một thành phố và một bang (0 ngoại lệ). Số liệu từng chiều: `handoff/2026-11-14-P8-dimensions.md`.

**Phân nhóm dimension.** Dùng chung (conformed), đóng vai (role-playing), SCD2, chiều rác (junk), danh mục nhỏ (lookup: `dim_order_status` 9 dòng, `dim_payment_type` 6, `dim_lead_origin` 11). Thầy yêu cầu **thống kê số dòng của từng dimension**: 10 bảng từ 6 đến 96.339 dòng (dim_date 1.828; dim_geography 19.178; dim_customer 96.339; dim_seller 3.558; dim_product 32.952; dim_order_status 9; dim_payment_type 6; dim_lead_origin 11; dim_lead_profile 503; dim_sales_rep 55).

**ETL và nạp tăng dần.** Một lệnh `python -m etl.run_pipeline` chạy sáu bước và ghi nhật ký từng bước. *Extract* chỉ lấy dòng chưa có (đơn theo **watermark**, bảng nhỏ theo khoá). *Nạp ban đầu* đến 31/12/2017 (45.430 đơn) rồi **11 đợt hằng tháng** mô phỏng cập nhật, tổng 286.144 bản ghi mới; mỗi đợt 21–28 giây, kết quả trùng đúng nạp full (16/16 bảng khớp số dòng, tổng tiền và nội dung). **Dòng mồ côi** (dòng con đến trước dòng cha) được thử lại ở đợt sau; cơ chế được chứng minh bằng kịch bản kiểm thử. Kiểm thử: 136 phép đạt 100%, cộng 6 phép đối chiếu với khám phá dữ liệu. Dựng lại toàn bộ từ đầu mất 443 giây và cho kết quả giống hệt. Lô đầu nạp 1.273.620 dòng vào staging, loại 42 dòng.

**Đa dạng công cụ ETL.** SQL (procedure PostgreSQL) làm biến đổi chính; Python điều phối, nạp, xuất; Power Query (M) làm lại cùng một quy tắc làm sạch tên thành phố. Ba công cụ cho cùng kết quả: **8.011 tên thành phố → 5.968**; SQL đổi 73.440 dòng, Python 73.438 (chênh 2 dòng do ký tự `º` trong `4º centenario`).

**Data model logic và vật lý.** *Logic*: mỗi fact nối đúng các chiều theo **bus matrix** (hàng = quy trình/fact, cột = chiều dùng chung). *Vật lý*: toàn bộ bảng schema `dw` với cột, kiểu dữ liệu, khoá chính theo grain, khoá ngoại có chỉ mục. Cả hai hình đều **fact màu cam, dimension màu xanh**. **Data mart**: 4 mart, 17 view, mỗi mart gồm fact, dimension và 3–4 câu hỏi phân tích.

**OLAP.** Năm thao tác (roll-up, drill-down, slice, dice, pivot) đều quy về SQL trên lược đồ sao (ROLAP). Ví dụ: roll-up GMV theo năm: 2017 là 6,11 triệu BRL, 2018 là 7,34 triệu; drill-down xuống ngày: Black Friday cao gấp 5,2 lần ngày thường; slice/dice: vùng Sudeste chiếm 64,3% GMV năm 2017. **Chọn ROLAP** vì dữ liệu nhỏ, kho luôn tươi và Power BI làm lớp ngữ nghĩa. **Hiệu năng:** star schema chỉ nhanh hơn OLTP 1,0–1,6 lần; tốc độ lớn đến từ materialized view (làm mới trong khoảng 2 giây) và chỉ mục khoá ngoại (`handoff/benchmark.md`).

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn | Dùng ở |
| --- | --- | --- | --- |
| Các lớp | 6 lớp, số bảng và dòng như mục 3 | `handoff/00-TONG-QUAN.md` mục 2; `2026-11-14-P8-layers.md` | S49, S50, S136 |
| ODS | 18 bảng, 678.183 dòng | `2026-11-05-P2.md` | S52 |
| Before/after | 6 bảng nguồn; geolocation 1.000.163 → 19.178 | `handoff/before-after-samples.md` | S70–S73 |
| Đối soát | nguồn = staging = ODS + loại; tổng tiền khớp từng đồng | `2026-11-05-P5.md`; `rebuild-report.md` | S74 |
| Nạp tăng dần | 11 đợt; 286.144 bản ghi; 21–28 giây; 16/16 bảng khớp | `handoff/2026-11-14-P8-etl.md`; `2026-11-14-P8b.md` | S77–S80 |
| Kiểm thử | 136 phép đạt 100%, 6/6 đối chiếu EDA | `handoff/2026-11-14-P8-etl.md` | S82 |
| Dựng lại | 443 giây | `handoff/rebuild-report.md` | S110 |
| Ba công cụ ETL | 8.011 → 5.968 thành phố | `powerbi/power-query-vi-du.md` | S138 |
| Chiều | 10 bảng; số giá trị từng cấp | `handoff/2026-11-14-P8-dimensions.md` | S57, S58, S139 |
| Fact | 6 bảng, 3 loại | `handoff/stats.md` mục fact | S62–S65 |
| Mart và OLAP | 17 view; 4 materialized view; roll-up, drill-down, slice, dice, pivot | `handoff/olap-examples.md`; `2026-11-05-P6.md` | S84–S87 |
| Hiệu năng | 1,0–1,6 lần; materialized view | `handoff/benchmark.md` | S88 |
| Mapping từng bảng | nguồn → đích → phép biến đổi | `docs/mapping.csv`; `docs/mapping_oltp_olap.md` | trang OLTP → OLAP |

Hình có sẵn (bản nháp): `figures/3-2_kien_truc_cac_lop.png`, `3-3_etl_jobs.png`, `3-4-1_pipeline.png`, `3-4-3_before_after_*.png` (6), `3-3-4_erd_dw.png`, `3-3-4_constellation.png`, `3-5_data_model_logic.png`, `3-5_data_model_vat_ly.png`, `3-5_data_mart.png`, `3-5-1_benchmark.png`.

## 5. Danh sách slide đề xuất

**Các slide đang có** (bảng do script đọc từ file `.tex`):

<!-- SLIDES:02b-kien-truc-etl-model.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 49 | Kiến trúc sáu lớp từ hai hệ thống nguồn đến bốn dashboard | oltp/crm → staging → ODS → kho → data mart → Power BI; etl_log giám sát | `3-4-1_pipeline.png` | đã có |
| 2 | 50 | Tách lớp giúp đối soát: staging = ODS + dòng bị loại cho mọi bảng | Chỗ nào hỏng biết ngay lớp nào | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng đối soát (handoff P2) |
| 3 | 51 | Công nghệ: PostgreSQL 18, Python 3.11, SQL procedure, Power BI, Git | Không Docker, không PostGIS; điều phối bằng một lệnh | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: logo công nghệ (chèn) |
| 4 | 136 | Kiến trúc theo lớp: sáu tầng từ nguồn đến BI, mỗi tầng có thành phần, công nghệ, số dòng | PostgreSQL, Python, Power BI, GitHub; số bảng và số dòng từng lớp; Giám sát etl_log 6 bảng; điều phối bằng một lệnh Python | `3-2_kien_truc_cac_lop.png` | đã có |
| 5 | 52 | ODS là lớp làm sạch trung gian: 18 bảng, 678.183 dòng, mọi lỗi có cờ hoặc lý do | Zip thành 5 chữ số, thành phố bỏ dấu, NULL thành unknown, khử trùng review | bảng | đã có |
| 6 | 67 | Một lệnh chạy sáu bước ETL và ghi lại từng bước | extract → ODS → dim → fact → mart → tests → snapshot → export | `3-4-1_pipeline.png` | đã có |
| 7 | 68 | Extract chỉ lấy dòng chưa có: đơn theo watermark, bảng nhỏ theo khoá | Chế độ full 52 giây; incremental khoảng 22 giây | `3-4-1_pipeline.png` | đã có |
| 8 | 69 | ODS xử lý lỗi theo ba cách: chuẩn hóa, gắn cờ hoặc loại có lý do | 1.359 đơn bàn giao trước khi duyệt được gắn cờ, không xóa | bảng | đã có |
| 9 | 70 | Trước và sau ETL: bảng đơn hàng có thêm cờ lỗi và kiểu dữ liệu chuẩn | Ví dụ trước/sau | `3-4-3_before_after_orders.png` | đã có |
| 10 | 71 | Trước và sau ETL: sản phẩm và seller được chuẩn hóa tên cột và thành phố | *_lenght → *_length; thành phố bỏ dấu, chữ thường | `3-4-3_before_after_products.png`, `3-4-3_before_after_sellers.png` | đã có |
| 11 | 72 | Trước và sau ETL: 1.000.163 dòng toạ độ gom thành 19.178 mã bưu chính | Trung vị toạ độ, mode thành phố | `3-4-3_before_after_geolocation.png` | đã có |
| 12 | 73 | Trước và sau ETL: MQL và deal có giá trị trống thành unknown | origin rỗng → unknown; doanh thu khai báo 0 gắn cờ | `3-4-3_before_after_mql.png`, `3-4-3_before_after_closed_deals.png` | đã có |
| 13 | 74 | Đối soát số dòng: nguồn = staging = ODS + loại, và tổng tiền khớp từng đồng | price 13.591.643,70 BRL = file CSV | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng đối soát (handoff P4) |
| 14 | 75 | SCD2 được nạp bằng window function: mỗi lần zip đổi mở một phiên bản mới | lag(zip) so với đơn trước; effective_from = ngày mua | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: đoạn SQL (Phụ lục B, code/scd2_ |
| 15 | 76 | Nạp fact: tra khoá theo phiên bản có hiệu lực, khoảng thời gian âm thành NULL | 1.359 đơn có handling_days âm (bàn giao trước khi duyệt) được đặt NULL và đếm | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng fact_ |
| 16 | 77 | Nạp tăng dần mô phỏng: 11 đợt hằng tháng, tổng 286.144 bản ghi mới | simulate_increment rồi run_pipeline –mode incremental | `3-4-1_pipeline.png` | đã có |
| 17 | 78 | Mỗi đợt chạy 20–26 giây, trong đó kiểm thử chiếm hơn một nửa | Bảng 11 đợt: bản ghi mới, thời gian | bảng | đã có |
| 18 | 79 | Funnel lấp đầy dần: MQL 2.002 → 8.000, deal 3 → 842, seller có đơn 0 → 379 | Số liệu mỗi đợt từ batch_metrics | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: biểu đồ đường từ batch_ |
| 19 | 80 | Kết quả incremental trùng nạp full: 16/16 bảng khớp số dòng, tổng tiền và nội dung | So sánh bằng checksum trên khoá tự nhiên | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng so sánh (handoff/2026-11-05-P5.md |
| 20 | 81 | Dòng mồ côi được thử lại ở đợt sau, nhưng cơ chế mới được chứng minh bằng kiểm thử | Kịch bản deal b91cf88… trên bản sao trong giao dịch rồi hoàn tác | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: sơ đồ 3 bước (loại → cha đến → nạp lại) |
| 21 | 82 | 136 phép kiểm thử đạt 100%, cộng 6 phép đối chiếu với khám phá dữ liệu | Số dòng, tổng tiền, grain, khoá ngoại, SCD2, mart khớp fact | bảng | đã có |
| 22 | 83 | Nhật ký etl_log cho biết mỗi lô chạy gì, mất bao lâu, loại bao nhiêu dòng | job_run, rejected_rows, dq_check, batch_metrics | khung chờ | cần ảnh: CHÈN BẢNG: giám sát ETL (báo cáo mục 3.3) |
| 23 | 110 | Dựng lại toàn bộ dự án từ đầu mất 443 giây và cho kết quả giống hệt | Xóa hai database, chạy một lệnh, 16/16 bảng khớp | bảng | đã có |
| 24 | 137 | Sáu giai đoạn ETL: lô đầu nạp 1.273.620 dòng vào staging, 42 dòng loại, 142 test đạt | Extract, seed và ODS, dimension và fact, mart, kiểm thử, xuất CSV; Số dòng lấy từ etl_log.job_run (lô đầu và tổng các lô) | `3-3_etl_jobs.png` | đã có |
| 25 | 138 | SQL, Python và Power Query cho cùng kết quả làm sạch: 8.011 thành 5.968 thành phố | Chữ thường, bỏ dấu, zip đủ 5 ký tự; 73.440 dòng đổi; Python chênh 2 dòng do ký tự ordinal; mã M thêm bảng thay thế để khớp SQL | – | đã có |
| 26 | 105 | Giám sát ETL: 11 đợt tăng dần 21–28 giây, 136 test đạt 100%, chỉ 42 dòng bị loại | Dòng bị loại duy nhất là 42 điểm toạ độ ngoài Brazil; không có dòng mồ côi; Funnel lấp đầy dần: MQL 2.002 → 8.000, deal 3 → 842, seller có đơn 0 → 379 | khung chờ | cần ảnh: CHÈN BẢNG: các đợt nạp (tables/p8b_etl_batches) |
| 27 | 57 | Mười bảng chiều với số dòng từ 6 đến 96.339 | dim_date 1.828; geography 19.178; customer 96.339; seller 3.558; product 32.952; ... | bảng | đã có |
| 28 | 58 | Hệ thống chiều khái niệm: phân cấp ngày, địa lý, sản phẩm, seller, khách | Ngày → tháng → quý → năm; zip → thành phố → bang → vùng | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: sơ đồ phân cấp (vẽ) |
| 29 | 59 | SCD2 giữ lịch sử địa chỉ: 96.096 khách thành 96.339 dòng, 236 khách đổi zip | Đơn cũ vẫn trỏ về địa chỉ lúc mua | bảng | đã có |
| 30 | 60 | dim_seller là chiều dùng chung: nối bán hàng với funnel qua seller_id | 462 seller chỉ có trong CRM vẫn có dòng, địa chỉ Unknown | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng ví dụ seller (huong-dan/01-pipeline-b |
| 31 | 61 | Chiều rác và role-playing giúp fact gọn mà vẫn đủ thông tin | dim_lead_profile gom 7 thuộc tính thành 503 tổ hợp; dim_date đóng 5 vai ở fulfillment | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng ví dụ hai kỹ thuật |
| 32 | 66 | Dòng Unknown -1 và khoá thay thế bảo đảm fact không bao giờ có khoá rỗng | Mọi lỗi tra khoá được ghi fact_load_issue | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng dim_ |
| 33 | 139 | Phân cấp đúng khi tháng kèm năm, thành phố kèm bang: 303 tên thành phố trùng giữa các bang | 12 số tháng nhưng 60 cặp (năm, tháng); 5.814 tên thành phố nhưng 6.190 cặp (bang, thành phố); Mỗi danh mục một nhóm ngành, mỗi origin một nhóm kênh (0 | – | đã có |
| 34 | 53 | Bus matrix: sáu fact dùng chung các chiều ngày, seller, khách, địa lý | Seller là chiều dùng chung của hai quy trình | bảng | đã có |
| 35 | 54 | Mô hình constellation: bốn mart, sáu fact (cam), mười chiều (xanh) | Khung = data mart | `3-3-4_constellation.png` | đã có |
| 36 | 55 | Data model logic: mỗi fact nối đúng các chiều theo bus matrix | Ví dụ fact_order_item nối 6 chiều với 2 vai địa lý | `3-3-4_erd_dw.png` | đã có |
| 37 | 56 | Data model vật lý: khoá chính theo grain, khoá ngoại có index, 112.650 dòng hàng | Mọi khoá ngoại NOT NULL, dòng Unknown -1 | `3-3-4_erd_dw.png` | đã có |
| 38 | 62 | Sáu fact thuộc đủ ba loại của Kimball | Transaction 3, accumulating 2, periodic 1 | bảng | đã có |
| 39 | 63 | fact_order_fulfillment là accumulating snapshot: một đơn một dòng, cập nhật theo mốc | Mốc chưa xảy ra có khoá -1; thời gian từng chặng tính sẵn | bảng | đã có |
| 40 | 64 | fact_lead_funnel ghi lại hành trình MQL: ba mốc ngày và hai khoảng thời gian | days_to_close TB 48,5; days_won_to_first_sale TB 51,9 | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: dòng ví dụ MQL |
| 41 | 65 | fact_seller_monthly lưu dày đặc 36.583 dòng để thấy seller ngừng bán | Dày đặc so với thưa: 36.583 và 16.441 dòng | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng 4 tháng đầu của một seller |
| 42 | 84 | Bốn data mart gồm 17 view, trong đó 4 là materialized view làm mới trong 2 giây | Sales, fulfillment, cx, acquisition | bảng | đã có |
| 43 | 85 | Roll-up và drill-down: GMV 2017 là 6,11 triệu, 2018 là 7,34 triệu; ngày Black Friday cao gấp 5,2 lần | Quý 4/2017: 2,41 triệu BRL; 24/11/2017: 152.654 BRL | bảng | đã có |
| 44 | 86 | Slice, dice và pivot: vùng Sudeste chiếm 64,3% GMV năm 2017 | Dice Sudeste Home & Furniture quý 4: SP 199.179 BRL | bảng | đã có |
| 45 | 87 | Chọn ROLAP vì dữ liệu nhỏ, kho luôn tươi và Power BI làm lớp ngữ nghĩa | Khác MOLAP: không phải xử lý lại khối khi nạp dữ liệu | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng ROLAP vs MOLAP (handoff/olap-examples |
| 46 | 88 | Star schema chỉ nhanh hơn OLTP 1,0–1,6 lần; tốc độ lớn đến từ materialized view và index | Chọn lọc một seller nhanh gấp 9 lần nhờ index; materialized view dưới 1 ms so với 150–750 ms | `3-5-1_benchmark.png` | đã có |
| 47 | 140 | Data model logic: sáu quy trình nối với mười dimension và các cấp phân cấp | Fact cam, dimension xanh; không ghi kiểu dữ liệu | `3-5_data_model_logic.png` | đã có |
| 48 | 141 | Data model vật lý sinh từ cơ sở dữ liệu: mọi bảng dw với cột, kiểu, PK và FK | 16 bảng, fact và dimension khác màu | `3-5_data_model_vat_ly.png` | đã có |
| 49 | 142 | Bốn data mart, mỗi mart gồm fact, dimension và 3–4 câu hỏi phân tích | mart_sales, mart_fulfillment, mart_cx, mart_acquisition | `3-5_data_mart.png` | đã có |

*49 frame trong `02b-kien-truc-etl-model.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm hoặc sửa** (theo `docs/doi-chieu-nhom6.md`). Số dòng của từng bảng lấy từ `handoff/stats.md`:

| STT mới | Tiêu đề đề xuất (câu kết luận có số) | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| K1 | Mỗi lớp kiến trúc có một vai trò và một lý do chọn công nghệ | giải thích từng lớp (nguồn, staging, ODS, kho, mart, BI): làm gì, vì sao chọn PostgreSQL / Python / Power BI | bảng vai trò + hình có logo | mục 3 của file này | cần làm (thay S50, S51 đang là khung chờ) |
| K2 | `dim_date`: 1.828 dòng, đóng 11 vai trò, nuôi cả 6 fact | OLTP → OLAP: nguồn, quy tắc, số dòng vào/ra | bảng mapping | `docs/mapping.csv`; `stats.md` | cần làm |
| K3–K11 | các chiều còn lại, mỗi chiều một trang: `dim_geography` 19.178; `dim_customer` 96.339 (SCD2); `dim_seller` 3.558; `dim_product` 32.952; `dim_order_status` 9; `dim_payment_type` 6; `dim_lead_origin` 11; `dim_lead_profile` 503 (junk); `dim_sales_rep` 55 | nguồn, phép biến đổi, số dòng, ví dụ | bảng mapping | `docs/mapping.csv`; `stats.md`; `P3.md` | cần làm |
| K12–K17 | mỗi fact một trang: `fact_order_item` 112.650; `fact_order_fulfillment` 99.441; `fact_payment` 103.886; `fact_review` 99.224; `fact_lead_funnel` 8.000; `fact_seller_monthly` 36.583 | grain, nguồn, tra khoá, số dòng vào/ra | bảng mapping | `docs/mapping.csv`; `P4.md` | cần làm |
| K18 | Sơ đồ phân cấp: 5 năm → 20 quý → 60 tháng → 1.827 ngày; 5 vùng → 27 bang → 6.190 thành phố | sơ đồ cây các cấp của từng chiều kèm số giá trị | sơ đồ vẽ draw.io | `handoff/2026-11-14-P8-dimensions.md` | cần làm |
| K19 | Một đơn thật đi qua các lớp: nguồn → staging → ODS → kho | ví dụ minh hoạ ETL ("bổ sung ví dụ") | bảng một đơn qua từng lớp | `huong-dan/01-pipeline-bang-loi.md` | kiểm tra đã có chưa |
| K20 | Power Query cho cùng kết quả làm sạch: 8.011 → 5.968 thành phố (S138) | ảnh before/after chụp từ Power BI | `3-3_power_query_before_after.png` | `powerbi/power-query-vi-du.md` | cần ảnh (việc riêng) |
| K21 | Sửa S78 "Mỗi đợt chạy 20–26 giây": số thật là 21,3–27,6 giây (S105 đã ghi 21–28) | đồng bộ số | – | `handoff/2026-11-14-P8b.md` | sửa tiêu đề |

Khối lượng: 49 slide đang có + K1–K21 (K3–K11 là 9 trang, K12–K17 là 6 trang) ≈ 19 slide mới = **khoảng 68 slide** trong file của bạn; mỗi chiều và mỗi fact một trang là slide chi tiết (không nói hết trên lớp). **Chọn 9 slide để nói** (khoảng 11 phút):

| Thứ tự nói | Slide (cột S) | Ý chính |
| ---: | --- | --- |
| 1 | S136 và K1 | Kiến trúc theo lớp có logo và lý do chọn công nghệ |
| 2 | S137, S67 | Sáu giai đoạn ETL và pipeline các job |
| 3 | S70, S72 | Before/after: bảng đơn hàng và 1.000.163 dòng toạ độ → 19.178 mã |
| 4 | S138 và K20 | Ba công cụ (SQL, Python, Power Query), cùng 5.968 thành phố |
| 5 | S77, S80 | Nạp tăng dần 11 đợt và kết quả trùng nạp full |
| 6 | S57, S58, K18 | 10 chiều: số dòng, nhóm, phân cấp |
| 7 | S139 | Phân cấp đúng: tháng kèm năm, thành phố kèm bang (303 tên trùng) |
| 8 | S140, S141 | Data model logic và vật lý (fact cam, dimension xanh) |
| 9 | S85, S88 | Roll-up, drill-down và hiệu năng |

## 6. Sơ đồ draw.io

Quy ước chung (màu, font, xuất PNG): `README.md` mục 6. Nộp `.drawio` và PNG vào `03_drawio`.

| Hình | Phải thể hiện | Bản nháp | Lỗi thầy hay bắt |
| --- | --- | --- | --- |
| `3-2_kien_truc_cac_lop.png` | các lớp xếp tầng (nguồn, staging, ODS, kho, mart, BI, giám sát); **mỗi lớp liệt kê thành phần, logo công nghệ (PostgreSQL, Python, Power BI, GitHub), số bảng, số dòng**; **không vẽ thành luồng** | `docs/diagrams/kien-truc-cac-lop.drawio` | vẽ giống luồng hơn kiến trúc; thiếu logo; thiếu phân tích chi tiết |
| `3-3_etl_jobs.png` | pipeline mô hình ETL job: các job, thứ tự, đầu vào và đầu ra từng job, công cụ (SQL, Python, Power Query) | `docs/diagrams/etl-jobs.drawio` (kèm `pipeline-etl.drawio`) | pipeline chưa đủ chi tiết, người xem khó theo dõi: kèm ví dụ minh hoạ |
| `3-5_data_model_logic.png` | sáu fact nối đúng các chiều theo bus matrix, các cấp phân cấp | `docs/diagrams/data-model-logic.drawio` | bố cục không hài hoà; không phân màu |
| `3-5_data_model_vat_ly.png` | mọi bảng schema `dw`: cột, kiểu, khoá chính, khoá ngoại | `docs/diagrams/data-model-vat-ly.drawio` | **thiếu mô hình tổng thể vật lý** |
| `3-5_data_mart.png` | bốn data mart, mỗi mart gồm fact, dimension và 3–4 câu hỏi phân tích | `docs/diagrams/data-model-theo-mart.drawio` | fact và dimension cùng màu |

Logo công nghệ: tải logo chính thức của PostgreSQL, Python, Power BI, GitHub, kiểm tra điều khoản dùng; đặt ở góc từng khối. Cần thêm một **sơ đồ phân cấp** cho slide K18 (chưa có bản nháp, vẽ mới từ bảng ở `handoff/2026-11-14-P8-dimensions.md`).

## 7. Dashboard DB3 – Địa lý và phí vận chuyển

Hướng dẫn đầy đủ: [`../dashboards/DB3.md`](../dashboards/DB3.md). Cách mở file, lưu, Refresh, đối chiếu số, chụp ảnh: `README.md` mục 4. DB3 là dashboard **OLAP chính** của bộ.

**Câu hỏi trả lời:** GMV tập trung ở vùng/bang nào; phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng; seller và khách xa nhau bao nhiêu và điều đó ảnh hưởng phí vận chuyển và lead time ra sao.

**Các trang:** trang 1 *Địa lý và phí vận chuyển* (bản đồ bong bóng, ma trận phân cấp Geography, cột Freight ratio theo bang, so sánh GMV theo địa lý khách và theo địa lý seller); trang 2 *Chi tiết bang* (trang drill-through); trang tooltip `Tooltip_Bang`.

**Measure chính** (thư mục `DB3 Địa lý và phí vận chuyển` và dùng lại từ DB1, DB2): GMV by seller state; GMV, Orders, Freight, Freight ratio; Avg lead days, Late rate; màu `Color Freight ratio`.

**Checklist phải đạt:** ≥ 4 loại biểu đồ; định dạng số; tiêu đề dạng câu hỏi; màu đỏ chỉ để cảnh báo (Freight ratio cao); định dạng có điều kiện (data bars, màu bong bóng); slicer phân cấp Vùng → Bang; **OLAP drill-down/roll-up: Vùng → Bang → Thành phố → Zip trên bản đồ và ma trận (DB3 là dashboard chính của mục này)**; **drill-through trang Chi tiết bang** (trường `state_code`); tooltip `Tooltip_Bang`; publish và QR (Phú).

**Các bước dựng:**
1. Mở `olist_base.pbix`, *Save as* `DB3_dia-ly.pbix`; Refresh.
2. Trang 1: bộ lọc trang `InWindow = TRUE`; bản đồ bong bóng dùng `dim_geography[latitude]`/`[longitude]` (hoặc bảng rời `v_geo_state` theo bang, `v_geo_zip` theo zip), kích thước GMV, màu Freight ratio; một số zip chưa có toạ độ sẽ không hiện (ghi chú trên trang).
3. Ma trận với hierarchy **Geography** (Vùng → Bang → Thành phố → Zip) và các giá trị GMV, Freight, Freight ratio, Avg lead days; bật drill-down và *Expand all down one level*.
4. Cột Freight ratio theo `state_code` (màu `Color Freight ratio`); so sánh GMV (địa lý khách) với `GMV by seller state` (địa lý seller) theo `region`.
5. Slicer `year`, `category_group`, `size_class`; slicer phân cấp Vùng → Bang.
6. **Trang 2 Chi tiết bang:** *Format page → Page type = Drillthrough*, *Drill through → Add drill-through fields here* = `dim_geography[state_code]` (giữ *Keep all filters*); thẻ GMV, Orders, Freight ratio, Avg lead days, Late rate; bảng thành phố của bang; cột GMV và đường Avg lead days theo `year_month`; nút quay lại (*Insert → Buttons → Back*). Kiểm tra: chuột phải một bang ở trang 1 → *Drill through* → *Chi tiết bang*.
7. Trang tooltip `Tooltip_Bang` (*Page size = Tooltip*, *Allow use as tooltip = On*), 4 thẻ GMV, Freight ratio, Avg lead days, Late rate; gán cho bản đồ và thanh bang.
8. Đối chiếu mục 9 của `DB3.md`; đánh dấu checklist mục 10.
(Trang drill-through `DB3 Chi tiết bang` đã có sẵn trống trong `olist_base.pbix`; nếu mở file thấy chưa gán trường `state_code`, tự đặt ở bước 6.)

**Giá trị kỳ vọng để tự kiểm** (cửa sổ 2017-01 → 2018-08): GMV 13,449,529.68; Orders 97,905; Freight 2,234,177.06; Freight ratio 16.6%; Avg lead days 12.5; Late rate 6.8%.

**Câu chuyện khi demo (3 điểm, có số):**
1. Sudeste chiếm 65,4% GMV, Sul 14,4%, Nordeste 11,4%, Norte chỉ 2,5%: thị trường tập trung.
2. Phí vận chuyển nặng ở vùng xa: Norte 22,7% và Nordeste 21,7% giá hàng so với 15,2% ở Sudeste.
3. Khoảng cách tăng từ dưới 100 km lên trên 1.000 km làm phí vận chuyển TB tăng 11,75 → 31,65 BRL và lead time 6,5 → 19,0 ngày (`handoff/geo-distance.md`). Ghi chú: 555 dòng hàng (0,49%) thiếu toạ độ nên không tính được khoảng cách.

**Ảnh cần chụp:** `4_DB3_trang1_dia_ly.png`, `4_DB3_drill_down.png` (chuỗi thao tác vùng → bang → thành phố), `4_DB3_chi_tiet_bang.png`, `4_DB3_tooltip.png`; kèm 3–5 câu nhận xét có số cho mỗi ảnh gửi Người 4 (hạn 25/11).

## 8. Việc riêng: Power Query (mã M) và ảnh before/after

Hướng dẫn: `powerbi/power-query-vi-du.md`. Quy tắc làm sạch tên thành phố và mã bưu chính của bảng toạ độ viết bằng M. Các bước:
1. Lấy file nguồn `olist_geolocation_dataset.csv` từ Phú (không nằm trong 37 file CSV của Power BI; nằm ở `data/raw/ecommerce/`) và đặt vào thư mục `DataFolder`.
2. *Home → Transform data*; dán mã M vào truy vấn trống (bước `Nguon` đến `KieuText` cho `geolocation_raw`, rồi bước làm sạch cho `geolocation_clean`).
3. Bật *View → Column quality, Column distribution, Column profile*; chụp trước (8.011 tên thành phố khác nhau, mã bưu chính bắt đầu bằng 0) và sau (5.968 tên; mã đủ 5 ký tự).
4. Ghép ảnh trước/sau, đặt tên `3-3_power_query_before_after.png`, đưa vào `04_Docs/tex-nop/figures/` và dùng ở K20/S138.
5. **Không bấm Close & Apply** nếu chỉ minh hoạ (truy vấn này không thuộc mô hình chính).
Kết quả mong đợi (SQL đã chạy thật; Power Query chưa chạy thật): 8.011 → 5.968 tên thành phố; 73.440 dòng đổi. Nếu số khác, ghi lại và báo Phú.

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này (chọn các câu chính; còn lại xem file gốc: Q2, Q4, Q12, Q14, Q16–Q18, Q26–Q28, Q31, Q32):

<!-- QA:3,5,6,7,8,9,10,11,13,15,22,25,30,44,47 -->
**Q3. Vì sao `fact_order_fulfillment` là accumulating snapshot?**
Một đơn đi qua nhiều mốc (mua → duyệt → bàn giao → giao, kèm ngày dự kiến) và ta muốn đo thời gian giữa các mốc trên **một dòng** (`approval_hours` 10,3 giờ, `handling_days` 2,9 ngày, `transit_days` 9,3 ngày). Dòng được cập nhật (upsert theo `order_id`) khi đơn sang mốc mới; mốc chưa xảy ra có khoá ngày −1. Nếu dùng transaction fact thì phải tự ghép nhiều dòng để tính khoảng thời gian.

**Q5. `dim_seller` là conformed dimension nghĩa là gì?**
Cùng một bảng chiều được cả hai quy trình dùng: `fact_order_item` (bán hàng) và `fact_lead_funnel`/`fact_seller_monthly` (thu hút seller). Nhờ đó nối được "kênh thu hút → GMV": kênh Paid có 204 seller, 103 seller có đơn, GMV 153.720 BRL. Seller chỉ có trong CRM (462 deal chưa bán) vẫn có dòng với địa chỉ Unknown.

**Q6. SCD2 hoạt động thế nào trên dữ liệu này?**
Mỗi `customer_id` trong nguồn sinh ra cho từng đơn, nên khách thật (`customer_unique_id`) có thể đổi mã bưu chính qua các đơn. Kho sắp đơn theo thời gian; mỗi lần zip đổi thì mở **phiên bản mới** (`effective_from` = ngày mua, bản cũ `effective_to` = ngày trước). Kết quả: 96.096 khách → 96.338 phiên bản (96.339 dòng kể cả dòng Unknown `-1`); 236 khách có ≥ 2 phiên bản (nhiều nhất 4). Fact tra `customer_key` theo phiên bản có hiệu lực **tại ngày mua** nên báo cáo địa lý theo lịch sử vẫn đúng. *Xem thêm: `01-pipeline-bang-loi.md` mục 2.*

**Q7. Vì sao chọn SCD2 cho khách khi chỉ 0,26% khách đổi zip?**
Vì chi phí thấp (thêm 242 dòng so với 96.096 khách, +0,25%) mà có ví dụ SCD2 thật trên dữ liệu thật để minh hoạ cho báo cáo. Quyết định ghi trong nhật ký của `DW_DESIGN.md`.

**Q8. Role-playing dimension là gì, dự án dùng ở đâu?**
Một bảng chiều đóng nhiều vai. `dim_date` có 5 vai trong `fact_order_fulfillment` (mua, duyệt, bàn giao, giao, dự kiến) và 3 vai trong `fact_lead_funnel`; `dim_geography` có vai khách và vai seller; `dim_sales_rep` có vai SDR/SR. Trong SQL: join nhiều lần; trong Power BI: một quan hệ Active + các quan hệ Inactive gọi bằng `USERELATIONSHIP`.

**Q9. Junk dimension dùng để làm gì ở đây?**
Deal có 7 thuộc tính nhỏ (phân khúc, loại lead, hồ sơ hành vi, loại hình, có công ty, có GTIN, tồn kho). Gom thành `dim_lead_profile` (503 tổ hợp) thay vì rải 7 cột vào fact giúp fact gọn, và nhóm/lọc bằng một khoá.

**Q10. Vì sao dùng khoá thay thế thay vì dùng mã nguồn?**
Mã nguồn là chuỗi 32 ký tự và có thể thay đổi/không duy nhất giữa hệ thống; khoá số nguyên nhỏ, join nhanh, và **bắt buộc** cho SCD2 (một khách nhiều dòng). Mỗi chiều có dòng Unknown `-1` để fact không bao giờ có khoá rỗng.

**Q11. Kiến trúc các lớp và vai trò từng lớp?**
Nguồn (`oltp`, `crm`) → staging (bản sao thô + mã lô) → ODS (làm sạch, cờ lỗi) → dw (hình sao) → mart (tổng hợp) → Power BI. Tách lớp để chỗ nào hỏng biết ngay, có thể đối soát số dòng từng lớp: staging 1.559.764 = ODS + dòng bị loại. *Xem thêm: `01-pipeline-bang-loi.md`.*

**Q13. Làm sao biết kết quả nạp tăng dần đúng?**
Nạp full toàn bộ nguồn vào một database riêng rồi so với database sau 11 đợt bằng checksum nội dung trên khoá tự nhiên: **16/16 bảng dim/fact khớp** số dòng, tổng tiền và nội dung. Ngoài ra chạy lại một đợt đã chạy cho 0 dòng chèn, 0 cập nhật (idempotent).

**Q15. Dòng mồ côi (orphan) được xử lý ra sao?**
Dòng con thiếu dòng cha bị loại kèm lý do `orphan:…` ở `rejected_rows`, nhưng **được thử lại** ở các đợt sau khi cha đã tới và biến mất khỏi danh sách loại. Thành thật: cơ chế này **mới được chứng minh bằng kịch bản test** (`etl.test_orphan_retry`, 3/3 đạt); trong 11 đợt thật không có dòng mồ côi nào vì nguồn luôn nạp cha trước.

**Q22. Bạn kiểm tra chất lượng kho bằng cách nào?**
136 phép kiểm thử chạy sau mỗi lần pipeline và lưu ở `etl_log.dq_check`: đối soát số dòng nguồn → ODS → kho (chênh = dòng bị loại), tổng tiền (Σ price kho = 13.591.643,70 = file CSV), khoá ngoại hợp lệ, grain không trùng, SCD2 không chồng thời gian, mart khớp fact. Thêm 6 phép đối chiếu với EDA (chỉ báo cáo) như 380 seller có đơn và GMV 13,49 triệu.

**Q25. Vì sao chọn ROLAP mà không dùng MOLAP?**
Dùng PostgreSQL (không có SSAS); dữ liệu vài trăm nghìn dòng fact nên SQL trả lời dưới 1 giây; kho luôn "tươi" sau mỗi lần nạp tăng dần mà không phải xử lý lại khối đa chiều; Power BI (Import + DAX) làm lớp ngữ nghĩa. MOLAP đổi lại tính sẵn tổng hợp (nhanh hơn) nhưng cần bước process và tốn dung lượng. *Xem: `handoff/olap-examples.md`.*

**Q30. Vì sao star schema chỉ nhanh hơn OLTP 1,0–1,6 lần mà vẫn đáng dùng?**
Dữ liệu còn nhỏ (112 nghìn dòng hàng) và các truy vấn quét gần hết bảng nên chi phí chủ yếu là gom nhóm, không phải join (GMV theo bang × tháng: 657 ms → 506 ms). Giá trị của star schema là **truy vấn đơn giản, nhất quán** (một định nghĩa KPI), tính sẵn (`lead_days`, `delay_days`) và tạo nền cho snapshot/mart; khi dữ liệu lớn hơn nhiều, khoảng cách mới rõ.

**Q44. Hệ thống chiều khái niệm của nhóm gồm những gì và kiểm tra phân cấp đúng thế nào?**
Mỗi chiều có phân cấp: ngày (năm → quý → tháng → ngày), địa lý (vùng → bang → thành phố → zip), sản phẩm (nhóm ngành → danh mục → sản phẩm), seller, khách (SCD2), kênh (nhóm kênh → origin)… Đã kiểm tra bằng đếm trên kho: **tháng phải đi kèm năm** (12 số tháng nhưng 60 cặp năm-tháng), **thành phố phải đi kèm bang** (5.814 tên thành phố nhưng 6.190 cặp bang-thành phố; 303 tên xuất hiện ở từ 2 bang trở lên, nhiều nhất `bom jesus` và `sao domingos` ở 6 bang), mỗi danh mục thuộc đúng một nhóm ngành và mỗi origin thuộc đúng một nhóm kênh. Mười chiều chia thành chiều dùng chung (`dim_date`, `dim_customer`, `dim_seller`, `dim_geography`, `dim_order_status`), đóng vai (`dim_date`, `dim_sales_rep`), SCD2 (`dim_customer`), rác (`dim_lead_profile`) và danh mục nhỏ. Xem thêm: `DW_DESIGN.md` §5a.

**Q47. Vì sao hình kiến trúc vẽ theo lớp mà không vẽ thành luồng?**
Kiến trúc trả lời "hệ thống gồm những thành phần nào, công nghệ nào, bao nhiêu bảng" nên các khối xếp tầng (nguồn, staging, ODS, kho, mart, BI) và mỗi lớp liệt kê thành phần, logo công nghệ (PostgreSQL, Python, Power BI, GitHub), số bảng, số dòng và tần suất. Còn "dữ liệu đi từ đâu đến đâu" thể hiện ở hai hình khác: sơ đồ data flow và sơ đồ các job của pipeline (sinh từ `etl_log.job_run`). Tách hai hình giúp người xem nắm được từng thông tin mà không phải đọc một sơ đồ vừa có cấu trúc vừa có luồng.
<!-- /QA -->

Câu mới:

**Q-K1. Vì sao biến đổi bằng SQL procedure mà còn viết Power Query?**
SQL làm biến đổi chính vì nằm cạnh dữ liệu và chạy trong lô hằng ngày; Python điều phối; Power Query viết lại cùng quy tắc làm sạch tên thành phố để chứng minh ba công cụ cho cùng kết quả (8.011 → 5.968 thành phố). Barem yêu cầu ETL đa dạng công cụ.

**Q-K2. Staging và ODS khác nhau ở đâu?**
Staging là bản sao thô của nguồn (1.559.764 dòng, có mã lô nạp) để đối chiếu; ODS là lớp làm sạch (chuẩn hoá, gắn cờ, loại có lý do; 18 bảng, 678.183 dòng). Đối soát: nguồn = staging = ODS + dòng bị loại.

**Q-K3. Một dòng đi vào kho thế nào? Cho ví dụ.**
Ví dụ một đơn: bảng `orders` ở nguồn → bản sao ở staging → ODS (chuẩn hoá trạng thái, gắn cờ lỗi, kiểu dữ liệu chuẩn) → `fact_order_fulfillment` (tra khoá khách theo phiên bản SCD2 có hiệu lực, năm mốc ngày thành 5 khoá `date_key`, tính lead time, trễ). Xem `huong-dan/01-pipeline-bang-loi.md` để lấy ví dụ đơn thật.

**Q-K4. Vì sao thành phố phải đi kèm bang trong phân cấp?**
Có 303 tên thành phố xuất hiện ở từ 2 bang trở lên (ví dụ `bom jesus` ở 6 bang); chỉ dùng tên thành phố sẽ gộp nhầm các nơi khác nhau. Tương tự tháng phải đi kèm năm: 12 số tháng nhưng 60 cặp năm–tháng.

**Q-K5. DB3 đáp ứng OLAP thế nào?**
Hierarchy Geography Vùng → Bang → Thành phố → Zip trên bản đồ và ma trận, drill-down và roll-up trực tiếp trong Power BI; phía SQL tương ứng là 5 thao tác ở `sql/60_olap_examples/`.

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Viết dựa trên slide của mình. Số trang hiện tại: <!-- PAGES:3.2,3.3,3.4,3.5 -->mục 3.2: trang 40–41 (2 trang); mục 3.3: trang 42–52 (11 trang); mục 3.4: trang 53–56 (4 trang); mục 3.5: trang 57–66 (10 trang); tổng 27 trang<!-- /PAGES -->.

Các `\todo` hiện có (đếm từ mã nguồn):

<!-- TODOS:3-2-kien-truc.tex,3-3-etl.tex,3-4-chieu-khai-niem.tex,3-5-data-model.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/3-2-kien-truc.tex` | 2 | 1. Yêu cầu của môn: sơ đồ kiến trúc có logo công nghệ ở mỗi phần (PostgreSQL, Python, Power BI, GitHub...), nêu các hoạt động ETL, dimension, fact và tên các dashboard. Vẽ lại bằng draw.io từ các file docs/diagram…<br>2. Thay các ô chữ công nghệ trong Hình fig:kien-truc-lop bằng logo chính thức (PostgreSQL, Python, Power BI, GitHub) khi vẽ lại bằng draw.io từ docs/diagrams/kien-truc-cac-lop.drawio; giữ nguyên tên file hình 3-2_… |
| `report/chapters/3-3-etl.tex` | 6 | 1. Nhóm bổ sung phần ``Giới thiệu về ODS'' theo giáo trình (khái niệm, vị trí giữa nguồn và kho, khác biệt với kho) và liên hệ với Chương 1.<br>2. Thêm bảng công nghệ (logo, phiên bản, vai trò), hình cấu trúc thư mục repo, và hướng dẫn cài đặt rút gọn (README.md). Nêu quy ước đặt tên và quy trình làm việc nhóm với Git.<br>3. Thêm sơ đồ luồng staging → ODS (các job ETL) và bảng ``nguồn → đích → phép biến đổi'' (Phụ lục C).<br>4. Thêm sơ đồ data pipeline hoặc ETL jobs (có logo công nghệ); ví dụ trước/sau cho thêm bảng nếu giảng viên yêu cầu; kết quả so sánh incremental với full: 16/16 bảng khớp (handoff/2026-11-05-P5.md).<br>5. Nhóm kiểm tra các nhận xét giám sát ETL trên số liệu thật và viết lại bằng lời của nhóm; vẽ biểu đồ thời gian mỗi đợt và đường funnel lấp đầy dần từ handoff/2026-11-14-P8-etl.md nếu cần.<br>6. Nhóm chạy mã M trong Power BI Desktop để xác nhận 5.968 thành phố và 73.440 dòng đổi, chụp ảnh before/after (cột geolocation_city, Column distribution) theo powerbi/power-query-vi-du.md mục 4 và đặt vào figures… |
| `report/chapters/3-4-chieu-khai-niem.tex` | 1 | 1. Nhóm vẽ lại hệ thống chiều khái niệm (cây phân cấp từng chiều) bằng draw.io từ các bảng trên; bus matrix ở docs/DW_DESIGN.md mục 4. |
| `report/chapters/3-5-data-model.tex` | 5 | 1. Nhóm vẽ lại ba hình bằng draw.io từ docs/diagrams/data-model-logic.drawio, data-model-vat-ly.drawio và data-model-theo-mart.drawio (giữ tên file hình 3-5_data_model_logic.png, 3-5_data_model_vat_ly.png, 3-5_dat…<br>2. Yêu cầu của môn: data model logic và vật lý của staging / data mart / kho, dùng màu phân biệt fact (cam) và dimension (xanh), nhóm các vùng liên quan bằng khung. Vẽ lại bằng draw.io từ docs/diagrams/data-model-…<br>3. Thêm bus matrix (docs/DW_DESIGN.md mục 4) và sơ đồ phân cấp: ngày, địa lý, sản phẩm, seller, khách (SCD2).<br>4. Chọn thêm các truy vấn drill-down, slice, dice từ handoff/olap-examples.md; viết đoạn so sánh ROLAP và MOLAP trong bối cảnh bài toán (liên hệ mục 1.6).<br>5. Nhóm xác nhận số đo trên máy của mình nếu chạy lại (python scripts/benchmark.py); thêm giải thích kế hoạch thực thi (EXPLAIN) cho một truy vấn nếu muốn. |
| **Tổng** | **14** | |
<!-- /TODOS -->

## 11. Checklist trước khi nộp và mốc hạn

| Hạn | Việc | Xong |
| --- | --- | --- |
| 23/11 | 5 sơ đồ draw.io vẽ lại (kiến trúc có logo; ETL job; data model logic, vật lý, mart), xuất PNG đúng tên, nộp `03_drawio` | ☐ |
| 23/11 | Bản nháp `02b-kien-truc-etl-model.tex` (K1, K2–K17, K18–K21) | ☐ |
| 23/11 | Ảnh Power Query before/after (việc riêng) | ☐ |
| 25/11 | Bản đầu DB3; ảnh `4_DB3_*.png` và 3–5 câu nhận xét gửi Người 4 | ☐ |
| 26/11 | 3–5 câu bài học gửi Người 4 (về ETL: không xoá âm thầm, chọn grain trước; về dữ liệu: 303 tên thành phố trùng) | ☐ |
| 27/11 | Slide và DB3 xong; nộp `.tex` và hình mới vào `04_Docs/tex-nop/` | ☐ |
| 28–29/11 | Tập 11 phút, bấm giờ, tổng duyệt | ☐ |

Trước khi nộp slide: không còn khung đỏ `CHÈN HÌNH` (tìm `khungchen`; các slide còn khung chờ có trạng thái "cần ảnh" trong bảng mục 5); tiêu đề là câu kết luận có số; mỗi slide có `\muc{...}`; số trong tiêu đề khớp số liệu mới nhất; biên dịch bằng `thu-mot-phan.tex` không lỗi.
Trước khi nộp dashboard: mọi mục checklist DB3 (mục 10 của `DB3.md`) đã đánh dấu; drill-through hoạt động; số khớp mục 9.

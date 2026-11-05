# Prompt cho Claude Code – theo từng phase

Chỉ **KT1 (Phú)** chạy các prompt này. Các thành viên khác không code; họ nhận output qua `handoff/`, `figures/`,
`exports/powerbi/` trên GitHub và làm phần thiết kế, Power BI, báo cáo, slide.

Chuẩn bị một lần:
1. Cài PostgreSQL 16 trực tiếp trên máy (installer EnterpriseDB; ở Stack Builder không cần tick gì – nhóm không dùng PostGIS). Ghi lại user/mật khẩu.
2. Cài Python 3.11 và Git. Tạo repo private trên GitHub, clone về máy.
3. Copy `CLAUDE.md` vào gốc repo, `DW_DESIGN.md` vào `docs/`.
4. Tải 2 bộ dữ liệu Kaggle, giải nén vào `data/raw/ecommerce/` và `data/raw/marketing/`
   (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce và https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist).
5. Mở Claude Code ở gốc repo, dán **một prompt mỗi lần**, kiểm tra kết quả rồi mới sang prompt sau.

| Phase | Hạn | Phụ thuộc | Ai dùng output |
| --- | --- | --- | --- |
| P0 Khởi tạo & nạp nguồn | 8/11 | – | KT2 (ERD OLTP), VB1 (3.2.3, 3.2.4) |
| P1 Profiling & EDA | 10/11 | P0 | Cả nhóm trước buổi chốt thiết kế 12/11; VB1 (3.3.1); KT3 (Excel ToolPak) |
| P2 Staging & ODS | 14/11 | Chốt thiết kế 12/11, mapping của KT2 | KT2 (kiểm tra), VB1 (3.3.3, 3.4) |
| P3 Dimension | 16/11 | P2 | KT2 (data model), KT3 (phân cấp) |
| P4 Fact, kiểm thử, **xuất bản đầu cho Power BI** | 18/11 | P3 | KT3 bắt đầu dựng dashboard |
| P5 Incremental & điều phối | 20/11 | P4 | KT2 (pipeline), D7 |
| P6 Data mart, OLAP, đặc tả Power BI, xuất bản cuối | 21/11 | P4 | KT3, KT2, VB1 (3.4.4) |
| P7 Mở rộng: hiệu năng + địa lý | 25/11 | P4 | VB1 (3.5), KT3 (bản đồ) |

---

## P0 – Khởi tạo repo và nạp hệ thống nguồn

```
Đọc CLAUDE.md và docs/DW_DESIGN.md (mục 2, 3, 12) trước khi làm.

Nhiệm vụ phase P0: dựng môi trường (KHÔNG dùng Docker – PostgreSQL đã cài sẵn trên máy) và mô phỏng 2 hệ thống nguồn.

1. Tạo cấu trúc thư mục đúng như CLAUDE.md, cùng .gitignore (data/raw, .env, .venv, __pycache__), .env.example, requirements.txt, README.md tiếng Việt (cài PostgreSQL trên Windows và macOS, tạo venv, chạy pipeline).
2. Kiểm tra kết nối PostgreSQL bằng thông tin trong .env; kiểm tra có extension unaccent. Không dùng PostGIS.
3. etl/setup_db.py: tạo database chính (olist_dw) và database phụ (olist_full) nếu chưa có; chạy theo thứ tự các file trong sql/00_init và sql/10_source. Idempotent.
4. sql/00_init: extension unaccent; toàn bộ schema theo CLAUDE.md; các bảng etl_log (job_run, rejected_rows, watermark, dq_check) theo mục 11 DW_DESIGN.
5. sql/10_source: DDL cho schema oltp (9 bảng e-commerce) và crm (2 bảng marketing) giữ nguyên tên cột gốc của CSV (kể cả cột sai chính tả *_lenght – đó là đặc điểm của hệ thống nguồn), có PRIMARY KEY và FOREIGN KEY hợp lý. Chú ý: order_reviews không dùng review_id làm PK được vì bị lặp; geolocation không có PK tự nhiên (thêm cột id); KHÔNG đặt FK closed_deals.seller_id sang oltp.sellers (hai hệ thống khác nhau) – ghi chú điều này.
6. etl/: config.py (đọc .env), db.py (engine SQLAlchemy), log.py (ghi etl_log.job_run), load_source.py:
   - kiểm tra đủ 11 file CSV, báo rõ file nào thiếu;
   - `--initial`: nạp bảng tham chiếu đầy đủ; nạp orders (và các bảng con theo order_id) có order_purchase_timestamp <= 2017-12-31; MQL có first_contact_date <= 2017-12-31 và closed_deals có won_date <= 2017-12-31;
   - `--full --database olist_full`: nạp toàn bộ (dùng cho EDA);
   - dùng COPY (psycopg2 copy_expert); geolocation 1 triệu dòng phải nạp dưới 1 phút;
   - không làm sạch ở bước này (nguồn phải "bẩn" như thật); dòng vi phạm FK ghi vào etl_log.rejected_rows.
7. docs/erd_oltp.mmd: sơ đồ Mermaid erDiagram cho oltp + crm (cột, PK, FK; quan hệ qua seller_id vẽ riêng kèm chú thích). Render thêm ra figures/3-2-4_erd_oltp.png (dùng mermaid-cli nếu có, nếu không thì hướng dẫn KT2 dán vào mermaid.live).
8. Chạy thật: setup_db, nạp --full vào olist_full và --initial vào olist_dw. In bảng số dòng từng bảng cho cả hai.
9. Viết handoff/<ngày>-P0.md theo mẫu trong CLAUDE.md: số bảng, số dòng, số cột, dung lượng từng file CSV, dung lượng database; phần "Việc cho thành viên khác" giao KT2 vẽ lại ERD OLTP bằng draw.io (gạch chân các cột sẽ dùng sang OLAP); đoạn nháp cho 3.2.3 và 3.2.4; gợi ý slide. Commit.

Tiêu chí xong: chạy lại toàn bộ trên database trống không lỗi; số dòng olist_full khớp số dòng CSV (trừ dòng bị reject có log).
```

---

## P1 – Profiling và khám phá dữ liệu (EDA)

```
Đọc CLAUDE.md và docs/DW_DESIGN.md mục 2.3. Làm việc trên database olist_full.

Nhiệm vụ phase P1: khám phá dữ liệu cho mục 3.2.3 và 3.3.1 của báo cáo, và trả lời các câu hỏi cần có trước buổi chốt thiết kế 12/11.
Script trong scripts/eda/, hình vào figures/ (png, 200 dpi, tiêu đề và trục tiếng Việt, font có dấu tiếng Việt).

1. profile.py: với mỗi bảng nguồn – số dòng, số cột, kiểu, % null, số giá trị khác nhau, min/max, top giá trị. Xuất handoff/profiling.md và figures/3-3-1_null_heatmap.png.
2. data_quality.py: đếm cụ thể từng lỗi trong DW_DESIGN mục 2.3 (zip mất số 0, tọa độ ngoài Brazil, số tọa độ/zip, city lệch dấu – kèm ví dụ, đơn delivered thiếu ngày giao, mốc thời gian sai thứ tự, payment not_defined, installments 0, review trùng, danh mục thiếu bản dịch, MQL thiếu origin…). Bảng "Lỗi – số dòng – % – cách xử lý".
3. distributions.py: histogram + boxplot price, freight_value, payment_value, lead time, delay_days; Pareto GMV theo danh mục và theo seller (đường tích lũy 80%); số đơn theo tháng (chỉ rõ 2016 thưa, 09–10/2018 trống); phân bố review_score.
4. correlations.py: ma trận tương quan biến số; scatter delay_days – review_score (kèm điểm TB theo nhóm trễ); freight_value – product_weight_g; boxplot lead time theo vùng; tỷ lệ trễ theo bang.
5. funnel.py: MQL theo tháng và origin; tỷ lệ won theo origin; phân bố days_to_close; business_segment top 10; **số seller trong closed_deals có / không có đơn hàng**.
6. design_questions.py – trả lời bằng số cho buổi chốt thiết kế:
   a) bao nhiêu customer_unique_id có >1 zip qua các đơn (quyết định SCD2 hay SCD1 cho dim_customer);
   b) bao nhiêu seller từ funnel có đơn, tổng GMV của họ (quyết định độ sâu dashboard D6);
   c) nếu fact_seller_monthly dày đặc thì bao nhiêu dòng, nếu thưa thì bao nhiêu;
   d) liệt kê toàn bộ danh mục sản phẩm kèm số đơn để nhóm duyệt bảng nhóm ngành hàng.
   Xuất handoff/design-questions.md, mỗi câu kèm khuyến nghị.
7. scripts/eda/excel_export.py: xuất exports/eda_sample.xlsx (5.000 dòng đơn đã join, cột số đã sạch) để KT3 chạy Excel Data Analysis ToolPak (Descriptive Statistics, Correlation, Histogram) – môn học yêu cầu đa dạng công cụ. Kèm hướng dẫn từng bước trong handoff.
8. handoff/<ngày>-P1.md: mỗi hình một dòng mô tả + 1–2 câu kết luận có số cụ thể; đoạn nháp cho 3.3.1 (~1 trang); gợi ý 8–10 slide. Commit.

Tiêu chí xong: mọi hình mở được; mọi con số trong handoff truy ngược được về script.
```

---

## P2 – Staging và ODS

```
Đọc CLAUDE.md, docs/DW_DESIGN.md mục 2.3, 3, 11 và docs/mapping.csv (source-to-target mapping do KT2 lập; nếu chưa có thì tạo bản nháp từ DW_DESIGN để KT2 duyệt).

Nhiệm vụ phase P2: xây tầng staging và ODS trên database olist_dw.

1. sql/20_staging: bảng staging.stg_<bảng nguồn> cho 11 bảng, cấu trúc giống nguồn + batch_id, loaded_at.
2. etl/extract.py: oltp/crm → staging. Hai chế độ: full (truncate + load) và incremental (etl_log.watermark: orders theo order_purchase_timestamp, bảng con theo order_id của đơn mới, mql theo first_contact_date, closed_deals theo won_date; customers/sellers/products/geolocation lấy dòng chưa có). Ghi etl_log.job_run.
3. seeds/: state_region.csv (DW_DESIGN 6.2), category_translation_extra.csv, category_group.csv (dùng kết quả nhóm đã duyệt ngày 12/11 nếu có trong docs/, nếu chưa thì tự map và liệt kê để duyệt), lead_origin_group.csv, payment_type.csv, order_status.csv. Nạp vào ods.ref_*.
4. sql/30_ods: bảng ods.* đã làm sạch + procedure ods.load_<bảng>(batch_id) theo bảng "Lỗi dữ liệu đã biết" mục 2.3:
   - zip char(5), city lower(unaccent(trim())), đổi *_lenght → *_length;
   - ods.geolocation_zip: 1 dòng/zip, median lat/lng sau lọc bbox, mode city/state;
   - ods.customer_map(customer_id, customer_unique_id);
   - orders có cột dq_flags text[] ('approved_before_purchase', 'delivered_without_date', 'carrier_before_approved', 'delivered_before_carrier'…);
   - reviews khử trùng theo (review_id, order_id);
   - dòng mồ côi → etl_log.rejected_rows kèm reason.
5. scripts/export_samples.py: với mỗi bảng có biến đổi, xuất 5 dòng TRƯỚC (staging) và SAU (ods) của cùng bản ghi ra bảng markdown, và render ảnh figures/3-4-3_before_after_<bảng>.png có tô màu ô bị thay đổi (báo cáo yêu cầu "before–after có tô phần tiền xử lý").
6. Chạy thật, in số dòng staging / ods / rejected từng bảng.
7. handoff/<ngày>-P2.md: bảng đối soát số dòng; bảng quy tắc làm sạch (quy tắc – số dòng bị ảnh hưởng); việc cho KT2 (đối chiếu với mapping, vẽ sơ đồ luồng staging → ods); đoạn nháp cho 3.3.3 và 3.4.2–3.4.3; gợi ý slide. Commit.

Tiêu chí xong: chạy lại 2 lần không lỗi, không trùng; staging = ods + rejected cho mọi bảng.
```

---

## P3 – Dimension

```
Đọc CLAUDE.md và docs/DW_DESIGN.md mục 5, 6 (kể cả nhật ký quyết định ở đầu file).

Nhiệm vụ phase P3: tạo và nạp toàn bộ dimension trong schema dw.

1. sql/40_dw/010_dim_ddl.sql: DDL 10 dim đúng đặc tả, PK, UNIQUE natural key, dòng Unknown -1, COMMENT ON bảng và cột bằng tiếng Việt (làm metadata).
2. etl/build_dim_date.py: dim_date 2016-01-01 → 2019-12-31, ngày lễ Brazil (package holidays), Black Friday. Tạo các view role-playing mục 6.1.
3. Procedure dw.load_dim_<tên>(batch_id) cho các dim còn lại, idempotent:
   - dim_geography hợp nhất zip từ ods.geolocation_zip + customers + sellers; giữ latitude/longitude (không có cột geom vì không dùng PostGIS);
   - dim_customer theo quyết định 12/11 (SCD2 theo mục 6.3, hoặc SCD1 nếu nhóm đã hạ cấp); nếu SCD2 thì chạy incremental phải đóng phiên bản cũ, mở phiên bản mới đúng;
   - dim_seller SCD1, gộp thông tin closed_deals + mql; first_sale_date để NULL (P4 cập nhật);
   - dim_product có category_group, size_class;
   - dim_lead_profile là junk dimension; dim_sales_rep tách SDR/SR.
4. sql/90_tests/dim_tests.sql (mục 13 phần dim) + etl/run_tests.py chạy và ghi etl_log.dq_check.
5. scripts/report_stats.py: sinh handoff/stats.md gồm số dòng mọi bảng mọi schema; với mỗi dim: số bản ghi, 5 dòng mẫu, các phân cấp và số phần tử mỗi cấp (vd 5 vùng → 27 bang → N thành phố → M zip).
6. handoff/<ngày>-P3.md: bảng dim (tên – grain – số dòng – phân cấp – SCD); việc cho KT2 (vẽ hệ thống chiều khái niệm / phân cấp dim bằng draw.io) và KT3 (các phân cấp cần tạo trong Power BI); đoạn nháp cho 3.3.4 phần dimension; gợi ý slide. Commit.

Tiêu chí xong: test dim pass; mỗi dim đúng 1 dòng -1; (nếu SCD2) không chồng khoảng hiệu lực.
```

---

## P4 – Fact, kiểm thử và xuất bản đầu cho Power BI

```
Đọc CLAUDE.md và docs/DW_DESIGN.md mục 4, 7, 13.

Nhiệm vụ phase P4: tạo và nạp 6 bảng fact, kiểm thử, rồi xuất dữ liệu để KT3 bắt đầu dựng Power BI.

1. sql/40_dw/020_fact_ddl.sql: DDL fact_order_item, fact_order_fulfillment, fact_payment, fact_review, fact_lead_funnel, fact_seller_monthly đúng đặc tả; PK theo grain; FOREIGN KEY sang dim; index B-tree trên mọi FK; COMMENT ON tiếng Việt.
2. Procedure nạp theo thứ tự: fact_order_item → fact_payment → fact_order_fulfillment (UPSERT theo order_id) → fact_review (delivered_late lấy từ fulfillment) → cập nhật dim_seller.first_sale_date → fact_lead_funnel (UPSERT theo mql_id) → fact_seller_monthly (theo quyết định dày đặc/thưa ngày 12/11).
   - customer_key theo phiên bản có hiệu lực tại ngày mua (nếu SCD2);
   - không có FK NULL: không tìm thấy → -1 và đếm vào etl_log;
   - khoảng thời gian âm → NULL + cộng dq_flag_count.
3. sql/90_tests/fact_tests.sql: toàn bộ kiểm thử mục 13; chạy qua etl/run_tests.py, in bảng pass/fail.
4. docs/erd_dw.mmd: Mermaid erDiagram của dw (ghi chú loại fact); thêm bản tách theo data mart (constellation). Render ra figures/3-3-4_*.png nếu được.
5. docs/mapping_oltp_olap.md: bảng mapping cột nguồn → cột đích → phép biến đổi cho mọi cột của dim và fact (mục 3.2.4 báo cáo cần "ghi chú mapping OLTP → OLAP").
6. scripts/export_powerbi.py: xuất toàn bộ dim + fact + etl_log.job_run ra exports/powerbi/*.csv theo quy ước CSV trong CLAUDE.md, kèm exports/powerbi/README.md liệt kê file, số dòng, cột, và cột nào là khóa nối. Nếu tổng > 50 MB thì không commit, ghi rõ để KT1 tải lên Google Drive.
7. Cập nhật report_stats.py thêm phần fact (grain, số dòng, measure, tổng GMV, số đơn).
8. handoff/<ngày>-P4.md: bảng fact (tên – loại – grain – số dòng – measure); kết quả test; việc cho KT2 (vẽ data model logic và vật lý bằng draw.io, fact màu cam, dim màu xanh, nhóm theo data mart) và KT3 (nạp CSV vào Power BI, tạo quan hệ – hướng dẫn từng bước, không cần biết SQL); đoạn nháp cho 3.3.4 phần fact và model vật lý; gợi ý slide. Commit.

Tiêu chí xong: tất cả test pass; tổng price ở fact khớp nguồn (chênh lệch giải thích được bằng rejected_rows); KT3 mở được CSV trong Power BI.
```

---

## P5 – Incremental load và điều phối

```
Đọc CLAUDE.md và docs/DW_DESIGN.md mục 11, 12.

Nhiệm vụ phase P5:
1. etl/simulate_increment.py `--until YYYY-MM-DD` (mặc định +1 tháng so với watermark nguồn): chèn vào oltp/crm bản ghi mới từ CSV theo mục 12 (đơn + item + payment + review của đơn đó, khách/seller/product mới; MQL và closed_deals mới).
2. etl/run_pipeline.py `--mode full|incremental`: extract → ods → dim → fact → mart refresh → tests → export_powerbi; mỗi lần chạy một batch_id; ghi etl_log.job_run (thời gian, số dòng đọc/chèn/cập nhật/loại); lỗi thì dừng, ghi status 'failed' và message.
3. Kịch bản demo: initial (đến 2017-12) → full → lặp simulate +1 tháng và incremental cho tới khi hết dữ liệu nguồn (khoảng 11 đợt, tới 2018-11 vì won_date của closed_deals kéo dài hơn đơn hàng) → so sánh với một lần full trên dữ liệu đầy đủ (số dòng và tổng GMV phải khớp). Bảng thời gian chạy mỗi đợt.
4. View etl_log.v_run_summary và etl_log.v_dq_summary cho dashboard D7; thêm vào export_powerbi.
5. Mermaid flowchart của pipeline: docs/pipeline.mmd (+ png nếu render được).
6. handoff/<ngày>-P5.md: sơ đồ pipeline, bảng các đợt incremental (đợt – số bản ghi mới – thời gian chạy), giới hạn của mô phỏng; việc cho KT2 (vẽ lại sơ đồ pipeline / ETL jobs có logo công nghệ) và KT2/D7 (dữ liệu monitor); đoạn nháp về tần suất cập nhật và incremental load; gợi ý slide. Commit.

Tiêu chí xong: kết quả incremental = kết quả full; chạy lại một đợt đã chạy không sinh trùng.
```

---

## P6 – Data mart, minh hoạ OLAP, đặc tả Power BI, xuất bản cuối

```
Đọc CLAUDE.md và docs/DW_DESIGN.md mục 8, 9, 10 và nhật ký quyết định (OLAP theo mô hình ROLAP).

Nhiệm vụ phase P6:
1. sql/50_mart: view trong 4 schema mart theo mục 8 (view nặng dùng MATERIALIZED VIEW + procedure refresh), mỗi view có COMMENT tiếng Việt.
2. sql/60_olap_examples: 5 file, mỗi file một thao tác OLAP trên dw, có comment giải thích: roll-up (ngày → tháng → quý → năm; zip → bang → vùng), drill-down, slice (năm 2017), dice (Sudeste × Home & Furniture × quý 4), pivot (vùng × năm bằng FILTER hoặc crosstab); thêm ví dụ GROUPING SETS / ROLLUP / CUBE. Xuất kết quả mỗi truy vấn ra handoff dạng bảng. Thêm một đoạn giải thích vì sao đây là ROLAP và khác MOLAP ở đâu.
3. powerbi/measures.md: thư viện measure DAX cho KPI mục 9 (GMV, Orders, AOV, MoM %, YoY %, Freight ratio, Cancel rate, On-time rate, lead time từng chặng, Avg review, % negative, Repeat rate, MQL→Won, Avg days to close, Won→first sale), mỗi measure: code DAX, giải thích 1 dòng, định dạng hiển thị; measure cảnh báo cho conditional formatting (vd On-time rate < 90% → đỏ). Viết để người không biết DAX copy-paste được.
4. powerbi/model.md: hướng dẫn từng bước cho KT3 – nạp file CSV nào, kiểu dữ liệu từng cột, quan hệ (bảng – cột – cardinality – active/inactive, role-playing date dùng USERELATIONSHIP), phân cấp cần tạo, slicer và visual gợi ý cho D1–D7, cách Publish to web.
5. powerbi/theme.json: theme màu thống nhất (fact / cảnh báo / tăng trưởng), font Segoe UI.
6. Cập nhật export_powerbi.py xuất thêm các view mart cần cho dashboard; chạy xuất bản cuối.
7. handoff/<ngày>-P6.md: danh sách mart (view – mô tả – số dòng); kết quả 5 thao tác OLAP; bảng KPI với giá trị tính bằng SQL để KT3 đối chiếu số trên Power BI; đoạn nháp cho 3.4.4; gợi ý slide. Commit.

Tiêu chí xong: mọi view chạy dưới 3 giây (hoặc là materialized view); giá trị KPI trong handoff khớp với Power BI khi KT3 đối chiếu.
```

---

## P7 – Mở rộng (bản gọn): hiệu năng và CSDL địa lý

```
Đọc CLAUDE.md và docs/DW_DESIGN.md.

Nhiệm vụ phase P7 – hai phần độc lập, mỗi phần một handoff.

A. Hiệu năng: scripts/benchmark.py
 - 5 truy vấn phân tích tiêu biểu (GMV theo vùng × tháng, lead time theo bang, scorecard seller…);
 - đo thời gian (EXPLAIN ANALYZE, trung bình 5 lần): trên oltp (join chuẩn hóa) vs trên dw (star schema); có/không index FK; bảng thường vs materialized view; fact_order_item phân vùng theo năm vs không phân vùng;
 - bảng kết quả + figures/3-5-1_benchmark.png; giải thích ngắn vì sao nhanh/chậm.

B. CSDL địa lý: sql/70_geo/ (KHÔNG dùng PostGIS)
 - hàm SQL dw.haversine_km(lat1, lng1, lat2, lng2) bằng PL/pgSQL/SQL thuần; khoảng cách seller → khách (km) cho từng order item, view mart_fulfillment.v_shipping_distance;
 - so sánh ngắn trong handoff: haversine thuần SQL vs PostGIS (kiểu geometry/geography, chỉ mục không gian GiST) – nêu ưu nhược để báo cáo phần "Cơ sở dữ liệu địa lý" vẫn có nội dung lý thuyết;
 - quan hệ khoảng cách với freight_value và lead_days theo nhóm 0–100, 100–500, 500–1000, >1000 km, kèm tương quan;
 - xuất exports/powerbi/geo_state.csv và geo_zip.csv có tọa độ để KT3 vẽ bản đồ; hình figures/3-5-2_*.png.

handoff/<ngày>-P7-perf.md và handoff/<ngày>-P7-geo.md: bảng kết quả, hình, đoạn nháp cho 3.5.1 / 3.5.2, gợi ý slide. Commit.
```

---

## Prompt dùng nhanh khi cần đổi thiết kế

```
Đọc CLAUDE.md và docs/DW_DESIGN.md. Tôi muốn thay đổi: <mô tả>.
Trước khi sửa code: liệt kê mọi bảng, procedure, view, test, file xuất Power BI, measure DAX và handoff bị ảnh hưởng; đề xuất chỉnh docs/DW_DESIGN.md (thêm dòng vào nhật ký quyết định); chờ tôi đồng ý rồi mới làm.
```

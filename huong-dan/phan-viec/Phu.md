# Phú – Mở đầu, mở rộng, kết luận, file gốc và ghép file tổng

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io): [`README.md`](README.md). File này viết dạng checklist cho Phú; các mục 1–3 và 5–6 giống khung của `Nguoi-1.md` … `Nguoi-4.md`.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | **Mở đầu** · **Ch.5 Mở rộng** (5.1 Lakehouse, 5.2 thu thập API, D8, DB1 trên Superset) · **Ch.6 Kết luận** |
| File slide | `slides/sections/00-mo-dau.tex` (3 frame), `04-mo-rong.tex`, `05-tong-ket.tex`, `99-du-phong.tex` |
| Sơ đồ draw.io | **Kiến trúc Lakehouse** (`5-1_kien_truc_lakehouse.png`); sơ đồ API `5-2_kien_truc_api.png` |
| Dashboard | file gốc `olist_base.pbix`, **D8 Thị trường Brazil**, ghép file tổng, publish, QR |
| Thuyết trình | mở đầu (khoảng 3 phút, 3 slide) và mở rộng + kết luận (khoảng 5–6 phút); thứ tự: Phú → Người 1 → Người 2 → Người 3 → Người 4 → Phú |
| Báo cáo (giai đoạn 2) | `00-*` (bìa, lời mở đầu, đánh giá, viết tắt), `5-1-lakehouse.tex`, `5-2-thu-thap-api.tex`, `06-ket-luan.tex`, phụ lục |

## 2. Barem chấm gì ở phần này

**Hướng mở rộng (tập trung 1–2 hướng)** — các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu; dòng đỏ là chỗ nhóm khác bị trừ điểm):
- Tổ chức hoạt động tiền xử lý dữ liệu trong CSDL/công cụ lập trình.
- **Data lake.**
- Ứng dụng AI/Copilot.
- Sử dụng các ETL tools/Data pipeline.
- **Thu thập dữ liệu thực tế sử dụng API.**
- Tính năng mới của các công cụ (Power BI, …).
- Khai phá dữ liệu (phân lớp, phân cụm, luật kết hợp).
- Sử dụng công cụ trực quan mới (ví dụ Tableau).
- Ngoài ra thầy chê một nhóm dùng **SQLite làm lakehouse: "chưa hợp lý về công nghệ"** và "trình bày lakehouse triển khai chưa rõ".

Ngoài 11 mục: *mức độ thu hút* (số người đặt câu hỏi) và *điểm bổ sung* (hướng mở rộng).

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Mở rộng (slide 151–233) | điểm bổ sung 2 | Lakehouse: kiến trúc → các bước triển khai, mỗi bước kèm một slide minh chứng → kết quả; trợ lý hỏi đáp Text-to-SQL | đã có khung chương 5. **Cần làm:** P9 (thu thập API, D8) và P10 (Lakehouse, DB1 trên Superset); xen kẽ slide triển khai và slide minh chứng |
| Bài học (slide 148–150, 235–237) | 4 | bài học về chỉ số và quy trình; tổng kết quy trình, kiến thức, công cụ | phần này do Người 4 gom; Phú dùng ở chương kết luận |

Không được chép câu chữ, số liệu hay hình của nhóm 6.

## 3. Kiến thức cần nắm

**Data lake và lakehouse.** *Data warehouse* lưu dữ liệu đã làm sạch theo lược đồ cố định; *data lake* lưu dữ liệu thô mọi định dạng trên object storage; *lakehouse* thêm lớp **table format có ACID** (Apache Iceberg: giao dịch, time travel) lên object storage để có cả hai. Kho chương 3 (PostgreSQL) có giới hạn mà lakehouse giải quyết: nạp theo lô so với CDC (bắt thay đổi liên tục); `fact_order_fulfillment` ghi đè trạng thái nên mất lịch sử sự kiện; không giữ dữ liệu thô; lưu trữ và tính toán gắn trên một máy; Power BI Import phải refresh. Thầy đã chê SQLite làm lakehouse, nên lưu trữ phải là object storage + table format có ACID. Thiết kế: `docs/prompts/P10-lakehouse.md` (bước 1), kết quả sẽ ở `docs/LAKEHOUSE.md`.

**Medallion Bronze – Silver – Gold.** Bronze: dữ liệu thô nguyên văn; Silver: làm sạch và ghép; Gold: star schema giống kho chương 3, đối soát được từng con số với kho cũ.

**Thu thập dữ liệu qua API (P9).** Olist chỉ có dữ liệu nội bộ, tĩnh. Làm giàu bằng dữ liệu công khai của Brazil: IBGE (bang, đô thị, dân số), Banco Central do Brasil SGS (tỷ giá USD/BRL, lạm phát IPCA), BrasilAPI (ngày lễ). Trả lời câu hỏi Olist không tự trả lời được: doanh thu trên đầu người theo bang, tăng trưởng thực sau lạm phát, GMV quy đổi USD, ngày lễ chính thức. Cách trình bày theo ý thầy: **kiến trúc → triển khai → kết quả**, mọi số liệu từ lần chạy thật. Chi tiết: `docs/prompts/P9-thu-thap-api.md`.

**Superset.** Apache Superset là công cụ BI nguồn mở; dựng lại **DB1 trên Superset** đọc từ tầng Gold của lakehouse (qua Trino), để so sánh với DB1 trên Power BI (cùng số liệu): đáp ứng "sử dụng công cụ trực quan mới".

**Bài học và kết luận.** Kết quả: một kho dữ liệu chạy được từ đầu đến cuối (10 chiều, 6 fact, 17 view mart; 99.441 đơn; GMV 13,49 triệu BRL; 136 kiểm thử đạt 100%; dựng lại 443 giây) và bốn dashboard. Hạn chế nói thẳng: mô phỏng cập nhật chỉ thêm bản ghi mới, chưa có đơn đổi trạng thái giữa chừng; chưa dùng PostGIS (khoảng cách là haversine đường chim bay); điều phối bằng lệnh Python, chưa có lịch tự chạy (`handoff/00-TONG-QUAN.md` mục 9).

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn |
| --- | --- | --- |
| Tổng quan dự án | 1,56 triệu dòng nguồn → 6 fact, 17 view mart, 4 dashboard | `handoff/00-TONG-QUAN.md` |
| Kết quả kiểm thử | 136 phép đạt 100%, 6/6 đối chiếu EDA | `handoff/2026-11-14-P8-etl.md` |
| Dựng lại toàn bộ | 443 giây, kết quả giống hệt | `handoff/rebuild-report.md` |
| Mô hình Power BI | 46 bảng, 33 quan hệ, 76 measure (sau P9) | `powerbi/olist_base/README.md`; `handoff/2026-11-14-P8c.md` |
| Hạn chế | danh sách | `handoff/00-TONG-QUAN.md` mục 9 |
| Mở rộng (P9, P10) | chưa chạy; điền sau khi làm | `docs/prompts/P9-thu-thap-api.md`; `P10-lakehouse.md` |

## 5. Danh sách slide đề xuất

**Các slide đang có trong `00-mo-dau.tex`** (bảng do script đọc từ file `.tex`):

<!-- SLIDES:00-mo-dau.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 1 | Xây kho dữ liệu và BI cho 99.441 đơn hàng thương mại điện tử Olist | Học phần MI4214 – Kho dữ liệu và Kinh doanh thông minh; nhóm ...; giảng viên ... | `3-3-4_constellation.png` | đã có |
| 2 | 2 | Bài trình bày gồm năm phần theo thứ tự khảo sát, phân tích thiết kế, dashboard, mở rộng và tổng kết | 2 Khảo sát (nghiệp vụ, yêu cầu, KPI, dữ liệu nguồn, ERD) 3 Phân tích và thiết kế (khám phá dữ liệu, kiến trúc, ETL, chiều khái niệm, data model) 4 Das | – | đã có |
| 3 | 3 | Dự án trong một trang: 1,56 triệu dòng nguồn thành 6 fact, 17 view mart và 4 dashboard | 2 hệ thống nguồn → staging → ODS → kho (10 chiều + 6 fact) → 4 data mart → Power BI | `3-4-1_pipeline.png` | đã có |

*3 frame trong `00-mo-dau.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Các slide đang có trong `04-mo-rong.tex` và `05-tong-ket.tex`** (khung chờ P9, P10):

<!-- SLIDES:04-mo-rong.tex,05-tong-ket.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | – | Lakehouse thêm đường thứ hai cho cùng dữ liệu: Debezium, Kafka, Iceberg, dbt | Mỗi thay đổi ở PostgreSQL được bắt từ log (CDC), qua Bronze, Silver, Gold; Gold có đúng mô hình hình sao của chương 3; Bảng Iceberg nằm trên object st | `5-1_kien_truc_lakehouse.png` | đã có |
| 2 | – | Bảy dịch vụ chạy trong 4 GB RAM của WSL, vận hành bằng script, không cần Airflow | Máy 13,9 GB; WSL giới hạn 4 GB để Windows và PostgreSQL của chương 3 còn 9,9 GB; Tổng đỉnh đo được khoảng 3,6 GB, dưới trần | bảng | đã có |
| 3 | – | Bước 1 hạ tầng: bảy container có healthcheck, image Iceberg REST tự dựng | docker compose –profile lite up -d: mỗi dịch vụ có healthcheck và giới hạn bộ nhớ riêng; Catalog Iceberg dùng REST (apache/iceberg-rest-fixture) lưu m | – | đã có |
| 4 | – | Minh chứng hạ tầng: kiểm tra bằng truy vấn thật, cả bảy dịch vụ khoẻ | Bên phải: MinIO console, bucket lakehouse có bốn thư mục bronze, silver, gold, ops | `5-1_minio_console.png` | đã có |
| 5 | – | Bước 2 nguồn và CDC: Debezium chụp snapshot rồi bắt từng thay đổi từ log | Nguồn: mã nạp của chương 3 (etl.load_source –initial) nạp 1.273.620 dòng vào oltp và crm trong 11,1 giây; kho PostgreSQL của chương 3 không bị đụng tớ | – | đã có |
| 6 | – | Minh chứng CDC: topic bằng đúng số dòng nguồn, và đủ 1.720.555 sau phát lại | orders sau phát lại: 99.441 INSERT cộng 160.791 UPDATE trạng thái đơn = 260.232 sự kiện | bảng | đã có |
| 7 | – | Phát lại 11 tháng: hai lần áp dụng, tách rõ để khớp 1.720.555 sự kiện | Nhịp phát 468,5 sự kiện/giây (443.935 trong 947,5 giây): do script phát quyết định; Năng lực xử lý đo ở lần nạp bù: khoảng 2.100 sự kiện/giây, cao gấp | bảng | đã có |
| 8 | – | Bước 3 Bronze: Spark ghi nguyên văn từng sự kiện vào bảng Iceberg chỉ-thêm | Một ứng dụng Spark đọc 11 topic, micro-batch 30 giây, tối đa 100.000 sự kiện mỗi lô để giữ bộ nhớ; Bronze bronze.<schema>_<bảng>: khoá, payload (JSON  | – | đã có |
| 9 | – | Minh chứng Bronze và Silver: bảng Iceberg là Parquet cộng metadata trên MinIO | Ví dụ silver/customers: thư mục data (Parquet) và metadata (mỗi lần ghi là một tệp *.metadata.json, nền tảng của time travel) | `5-1_minio_iceberg.png` | đã có |
| 10 | – | Bước 4 Silver: MERGE theo khoá, giữ dòng mồ côi để thử lại, SCD2 địa chỉ khách | Silver ghi bằng MERGE theo khoá chính; một sự kiện chỉ thay dòng có sẵn khi ts_ms không cũ hơn, nên giao trùng và sai thứ tự đều an toàn; Dòng mồ côi  | – | đã có |
| 11 | – | Minh chứng Silver: 10 bảng bằng nguồn về số dòng và checksum khoá | Kiểm tra: số dòng và md5 của khoá chính đã sắp xếp, ở PostgreSQL nguồn và ở Trino; 10/10 bảng khớp; sáu bảng *_rejected đều rỗng | bảng | đã có |
| 12 | – | Bước 5 Gold: dbt dựng 20 model từ Silver, giữ nguyên tên bảng, cột của đặc tả | dbt-trino: 10 dimension, 6 fact và 4 bảng mart (mart_sales_*) cho Superset; dòng Unknown khoá -1 như kho; lịch dim_date sinh từ chính hàm của chương 3 | – | đã có |
| 13 | – | Minh chứng Gold: lineage bốn tầng Silver, dimension, fact, mart | 18 nguồn Silver → 10 dimension → 6 fact → 4 mart, 77 cạnh phụ thuộc | `5-1_dbt_lineage.png` | đã có |
| 14 | – | Minh chứng Gold: 71 phép kiểm thử dbt đều đạt | dbt test: PASS=71, ERROR=0; chạy lại trong bộ pytest bằng tham số –run-slow | `5-1_dbt_test_1.png`, `5-1_dbt_test_2.png` | đã có |
| 15 | – | Đối soát Gold với kho: 16/16 bảng khớp, hai zip lệch tên thành phố (có giải thích) | Cùng một câu SQL chạy trên PostgreSQL (dw.*) và Trino (gold.*); mỗi bảng so số dòng, tổng các số đo, md5 khoá tự nhiên, md5 nội dung từng dòng; GMV 13 | `5-1_reconcile.png` | đã có |
| 16 | – | Dung sai và ngoại lệ duy nhất: hai zip hoà điểm tên thành phố | late_rate, avg_review_score: làm tròn 4 chữ số thập phân ở cả hai phía; Toạ độ: cắt floor(x 10^6), tức dưới 1e-6 độ (khoảng 0,11 m) | – | đã có |
| 17 | – | Lỗi 1: Silver chỉ có 24.765 trên 45.971 đơn, log không báo, đối soát mới thấy | Hiện tượng: luồng chạy xong, không lỗi, Bronze đủ (1.276.620 sự kiện = tổng offset Kafka), nhưng Silver chỉ có 24.765 đơn; Nguyên nhân: đơn có thể đến | bảng | đã có |
| 18 | – | Lỗi 2: trim() của Trino khác PostgreSQL, 18 review bị tính là không có bình luận | Hiện tượng: fact_review lệch ở hai cột, dù các bảng khác khớp; Nguyên nhân: trim() của Trino bỏ cả xuống dòng và tab, còn của PostgreSQL chỉ bỏ dấu cá | bảng | đã có |
| 19 | – | Độ trễ nguồn đến Silver trung bình 22,6 giây, chủ yếu là chờ micro-batch 30 giây | 6 lần thử ở pha ngẫu nhiên so với trigger; đổi một cột của một đơn rồi hoàn nguyên, Silver trở lại bằng nguồn | `5-1_latency.png` | đã có |
| 20 | – | Minh chứng luồng chạy liên tục: Spark UI ghi lại 41 lô, lô dồn việc hơn một phút | Trái: thống kê của query; phải: dòng thời gian các job Spark | `5-1_spark_ui_streaming_crop.png`, `5-1_spark_ui_jobs.png` | đã có |
| 21 | – | Thông lượng: nạp bù 2.100 sự kiện/giây, UPDATE qua MERGE 241, RAM đỉnh 3,6 GB | Nạp bù nhanh vì phần lớn là geolocation chỉ ghi Bronze; MERGE ghi lại tệp Iceberg nên chậm hơn; Spark chạm giới hạn nhưng không bị kill | bảng | đã có |
| 22 | – | Time travel: đọc phiên bản cũ dưới 0,2 giây, rollback sửa nhầm trong 0,09 giây | FOR VERSION AS OF và FOR TIMESTAMP AS OF đọc đúng phiên bản, không đụng dữ liệu hiện tại; UPDATE nhầm 97.103 đơn thành canceled; bản cũ vẫn đọc được ( | bảng | đã có |
| 23 | – | DB1 trên Superset: dashboard đọc từ tầng Gold của lakehouse qua Trino |  | khung chờ | cần ảnh: Chờ ảnh chụp DB1 trên Superset (Bước 10) |
| 24 | – | Kiểm thử ba lớp: 18 phép pytest, 71 phép dbt và đối soát 16 bảng | pytest nhanh (18 phép): Silver = nguồn cho 10 bảng (số dòng và md5 khoá), 6 bảng loại rỗng, Bronze = offset Kafka của 11 topic, Silver địa lý = ODS củ | – | đã có |
| 25 | – | Tổng kết 5.1: cùng số liệu với kho chương 3, thêm sự kiện và time travel | 1.720.555 sự kiện đi qua Kafka vào Bronze không mất, không trùng; Silver bằng nguồn ở 10 bảng; Gold bằng kho ở 16/16 bảng | – | đã có |
| 26 | 118 | Olist là ảnh chụp tĩnh nên cần dữ liệu công khai của Brazil để trả lời năm câu hỏi mà bán hàng một mình không trả lời được | bảng | bảng | đã có |
| 27 | 119 | Kiến trúc: collector, landing zone, staging, ODS, kho và mart; lỗi API không làm hỏng pipeline chính | Dựng lại toàn bộ (rebuild) dùng landing zone, không cần mạng | `5-2_kien_truc_api.png` | đã có |
| 28 | 150 | Bốn nguồn API công khai, mã bảng và mã chuỗi đều được đối chiếu với metadata của chính API | bảng | bảng | đã có |
| 29 | 151 | Collector thử lại tối đa 5 lần với chờ tăng dần, có timeout, giữ khoảng cách giữa các lời gọi và dùng User-Agent chung | Lỗi mạng, HTTP 429 và 5xx: chờ 1,5 → 3 → 6 → 12 giây giữa các lần thử; Banco Central chỉ xin phần sau watermark; cửa sổ ngày 10 năm theo quy định mới  | – | đã có |
| 30 | 120 | Landing zone giữ JSON nguyên văn kèm manifest: 69 lời gọi, 4,66 MB, 48.016 bản ghi, không lỗi | bảng | bảng | đã có |
| 31 | 152 | Staging giữ nguyên giá trị API; ODS ép kiểu, điền tỷ giá cho ngày nghỉ và nối chỉ số IPCA | bảng | bảng | đã có |
| 32 | 153 | Ghép thành phố Olist với đô thị IBGE qua bốn tầng: hai tầng đầu gán 96,1% số zip, bốn tầng gán 96,3% zip và 99,5% GMV | bảng | bảng | đã có |
| 33 | 154 | Ngưỡng fuzzy 95 vì từ 95 trở lên mọi cặp đúng, còn 90–94 đã có ghép sai như boa vista de minas → Bela Vista de Minas | sao thome das letras → São Tomé das Letras (97,4); santana do livramento → Sant'Ana do Livramento (97,7) | `5-2_ty_le_khop_theo_tang.png` | đã có |
| 34 | 155 | Kho được làm giàu không đổi khoá: 7 cột mới ở chiều địa lý, 4 cột ở chiều ngày và một fact bang theo năm với 81 dòng | dim_geography: mã IBGE, microrregião, mesorregião, dân số 2016–2018, tầng ghép (5.473 đô thị); dim_date: usd_brl, ipca_index, is_holiday_official, tên | – | đã có |
| 35 | 156 | 20 phép kiểm thử SQL mới và bộ pytest đều đạt: tổng số phép của pipeline tăng từ 136 lên 156 | Tỷ giá có đủ 1.827 ngày và không thiếu ngày làm việc nào; IPCA đủ 60 tháng, trùng chỉ số IBGE (chênh 0,000); Mã IBGE hợp lệ, cùng bang; không zip nào  | – | đã có |
| 36 | 121 | Theo đầu người, Rio de Janeiro dẫn đầu với 53,90 BRL trên 1.000 dân; Distrito Federal từ hạng 9 theo GMV lên hạng 3 | 2017: RJ 53,90; SP 48,58; DF 43,95; thấp nhất AM 2,58; Spearman giữa hai thứ hạng là 0,78 | `5-2_gmv_dau_nguoi_theo_bang.png` | đã có |
| 37 | 157 | GMV tháng 1–8 tăng 138,3% danh nghĩa nhưng chỉ 130,9% theo giá thực và 116,7% khi quy USD | Lạm phát IPCA 08/2017 → 08/2018: 4,2%; Tỷ giá bình quân gia quyền theo GMV: 3,17 (01/2017) → 3,84 (08/2018) | `5-2_danh_nghia_so_voi_thuc.png` | đã có |
| 38 | 158 | Thư viện ngày lễ thiếu 19 ngày so với BrasilAPI; ngày thường có lễ quốc gia ít hơn 27,9% số đơn | BrasilAPI 64 ngày lễ; holidays 45 ngày; 19 ngày chỉ có ở BrasilAPI (Carnaval, Phục sinh, Corpus Christi); Ngày thường có lễ: 124,7 đơn; không lễ: 172, | `5-2_ngay_le_va_don.png` | đã có |
| 39 | 159 | (Tuỳ chọn) Mưa càng nhiều thì giao trễ càng nhiều: từ 5,45% lúc không mưa lên 9,55% khi mưa từ 20 mm | Mưa ngày giao tại thủ phủ bang của khách; Liên hệ thống kê; mưa đo ở thủ phủ, không ở nơi khách ở | `5-2_mua_va_giao_tre.png` | đã có |
| 40 | 149 | [P9] Dashboard D8 Thị trường Brazil dựng từ dữ liệu API thu thập thực tế |  | khung chờ | cần ảnh: P9 điền: ảnh chụp D8 |
| 41 | 111 | Kết quả: một kho dữ liệu chạy được từ đầu đến cuối với 136 kiểm thử đạt và bốn dashboard | 10 chiều, 6 fact, 17 view mart; 99.441 đơn; GMV 13,49 triệu BRL | `3-3-4_constellation.png` | đã có |
| 42 | 113 | Hạn chế và hướng phát triển: trạng thái trung gian của đơn, PostGIS, lịch chạy tự động | Mô phỏng cập nhật chỉ thêm bản ghi mới; cơ chế thử lại mồ côi mới được chứng minh bằng test | – | đã có |

*42 frame trong `04-mo-rong.tex`, `05-tong-ket.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm** (theo `docs/doi-chieu-nhom6.md`: xen kẽ slide triển khai và slide minh chứng):

| STT mới | Tiêu đề đề xuất | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| P1 | Lakehouse: kiến trúc (thay khung S đầu mục 5.1) | tầng, công cụ, vai trò, vì sao chọn | `5-1_kien_truc_lakehouse.png` | `docs/LAKEHOUSE.md` (sau P10) | chờ P10 |
| P2–P5 | Triển khai lakehouse từng bước, mỗi bước một slide minh chứng (ảnh chụp, lệnh, kết quả) | nạp CDC, Bronze/Silver/Gold, truy vấn mẫu | ảnh chụp | handoff P10 | chờ P10 |
| P6 | Kết quả lakehouse: số liệu đo được, đối soát với kho PostgreSQL | số bảng, số dòng, thời gian truy vấn | bảng | handoff P10 | chờ P10 |
| P7 | DB1 trên Superset cùng số liệu với Power BI | so sánh hai công cụ | ảnh chụp | handoff P10 | chờ P10 |
| P8 | Thu thập API: bài toán, kiến trúc, triển khai, kết quả (4 slide) | IBGE, BCB, BrasilAPI | `5-2_kien_truc_api.png` | `docs/THU_THAP_API.md` (sau P9) | chờ P9 |
| P9 | D8 Thị trường Brazil dựng từ dữ liệu API | dashboard D8 | ảnh chụp D8 | `huong-dan/dashboards/D8.md` (sau P9) | chờ P9 |
| P10 | Kết luận: số kết quả, 3 bài học chính, hạn chế (sửa S đầu `05-tong-ket.tex`) | từ bài học Người 4 gom | bảng | Người 4 (26/11) | cần làm |

Khối lượng: mở đầu 3 frame (cộng 2 frame lý thuyết của Người 1 ở `00b-ly-thuyet-rut-gon.tex`), mở rộng 9 frame khung (cộng khoảng 6–8 slide minh chứng khi có P9, P10), kết luận 2 frame, dự phòng 17 frame. **Chọn slide để nói:** mở đầu S1–S3 (khoảng 3 phút); cuối bài: kiến trúc lakehouse (P1), một slide minh chứng triển khai, kết quả (P6), DB1 Superset (P7), thu thập API và D8 (P8, P9), kết luận (P10): khoảng 7 slide trong 5–6 phút.

Trước khi nộp slide: số liệu trong slide mở đầu khớp `handoff/00-TONG-QUAN.md`; mọi slide có `\muc{...}`.

## 6. Sơ đồ draw.io

- `5-1_kien_truc_lakehouse.png`: tầng lưu trữ (object storage), định dạng bảng (Iceberg), engine truy vấn, nguồn (CDC, JSON từ API), Bronze/Silver/Gold, quan hệ với kho PostgreSQL hiện có, BI (Power BI, Superset). **Vẽ theo lớp, không vẽ thành luồng**, có logo công nghệ (như lỗi thầy hay bắt ở `Nguoi-3.md`). Sẽ có file `.drawio` và bản nháp sau P10.
- `5-2_kien_truc_api.png`: collector → landing zone JSON thô → staging → ODS → kho → mart → Power BI. Sẽ có bản nháp sau P9.

## 7. Checklist việc của Phú

### 7.1 Power BI: file gốc, D8, ghép file tổng, publish, QR
- [ ] **File gốc:** mở `powerbi/olist_base/olist_base.pbip` bằng Power BI Desktop, Refresh, đối chiếu số với bảng ở `powerbi/olist_base/README.md` mục 4, rồi lưu `olist_base.pbix`. *Thư mục `powerbi/olist_base/` hiện có thay đổi chưa commit do Power BI Desktop lưu lại (gồm tham số `DataFolder` trỏ vào đường dẫn máy của bạn): trước khi commit, đặt lại `DataFolder` về giá trị mặc định hoặc không commit `expressions.tmdl`.*
- [ ] **Đóng gói:** `olist_base.pbix` lên `02_Dashboard`; 45 file CSV và `olist_geolocation_dataset.csv` lên `01_pBI_data`. Quy tắc: mọi người lưu thành `DBx_<tên>.pbix` trước khi dựng, **không sửa file gốc**.
- [ ] **Measure mới:** nếu ai cần measure chưa có, thêm vào `powerbi/measures.md` và `olist_base`, rồi chạy `python scripts/gen_pbip.py` (ghi đè `powerbi/olist_base/` nên chỉ chạy khi chưa ai dựng trên bản mới) hoặc thêm tay trong file gốc. Không để mỗi người tạo measure riêng trong file riêng, vì khi ghép sẽ mất.
- [ ] **D8 Thị trường Brazil:** sau P9, dựng bằng Power BI từ dữ liệu API; hướng dẫn `huong-dan/dashboards/D8.md` (do P9 viết). Không sửa DB1–DB4 của nhóm.
- [ ] **Ghép file tổng** (4 file `DBx_<tên>.pbix` → `Olist_DW_BI.pbix`), cách làm gợi ý (chưa thử):
  1. Dựng file tổng từ `olist_base.pbix` (cùng mô hình) rồi thêm các trang.
  2. Mỗi trang của một dashboard: mở file của người đó, chọn trang → chọn tất cả visual (Ctrl+A) → Ctrl+C → dán vào trang mới ở file tổng. Dán xong kiểm tra lại định dạng có điều kiện, bộ lọc trang `InWindow` và các tooltip.
  3. **Trang drill-through và tooltip:** cài đặt trang (Page type = Drillthrough, Tooltip, trường drill-through) **không đi theo** thao tác dán visual: đặt lại ở file tổng, hoặc dùng định dạng PBIR (mỗi trang là một thư mục trong `.Report/definition/pages/` của một dự án `.pbip`: sao chép thư mục trang và thêm tên trang vào `pages.json`) nếu mọi người lưu thêm bản `.pbip`.
  4. Sau khi ghép: đối chiếu từng thẻ với `powerbi/measures.md` mục 7; mở từng drill-through và tooltip.
- [ ] **Publish:** *Home → Publish* → *My workspace*; *File → Embed report → Publish to web (public)* → *Create embed code* → sao chép link (`powerbi/model.md` mục 9). Dữ liệu Olist là dữ liệu công khai nên chấp nhận; **không đưa dữ liệu thật của người khác lên**. Nếu tài khoản trường tắt *Publish to web*: dùng tài khoản cá nhân, hoặc xuất PDF/PowerPoint và chụp ảnh.
- [ ] **QR:** mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc công cụ tạo QR bất kỳ); lưu `figures/4_qr_dashboard.png`; chạy `python scripts/sync_figures.py` để chép sang `report/figures` và `slides/figures`; đặt QR ở slide cuối phần dashboard (do Người 4, slide D8 trong `Nguoi-4.md`) và báo cáo 4.
- [ ] **Thống kê bộ dashboard:** nhận số thật từ Người 4 và cập nhật bảng ở báo cáo 4.1.5 (`report/tables/p8b_dashboard_stats.tex` đang là số thiết kế).

### 7.2 Mở rộng
- [ ] **P9 – thu thập API** (`docs/prompts/P9-thu-thap-api.md`): chạy; lấy `docs/THU_THAP_API.md`, `figures/5-2_*.png`, handoff; điền `5-2-thu-thap-api.tex` (5 `\todo`) và slide mục 5.2 (khung `[P9]` trong `04-mo-rong.tex`).
- [ ] **P10 – Lakehouse** (`docs/prompts/P10-lakehouse.md`): cần Docker Desktop (WSL2) trên máy Windows; lấy `docs/LAKEHOUSE.md`, `figures/5-1_*.png`, handoff; điền `5-1-lakehouse.tex` (4 `\todo`) và slide mục 5.1 (khung `[P10]`). Cấu trúc trình bày: **kiến trúc → triển khai (mỗi bước một slide minh chứng) → kết quả**.
- [ ] **Superset – DB1:** dựng DB1 trên Superset đọc tầng Gold qua Trino; so sánh số với DB1 Power BI; ảnh chụp và slide P7.
- [ ] **Kiến trúc Lakehouse bằng draw.io** (mục 6), có logo công nghệ, vẽ theo lớp.

### 7.3 Slide
- [ ] **Mở đầu** (`00-mo-dau.tex`): bìa, mục lục, "Dự án trong một trang" (số liệu từ `handoff/00-TONG-QUAN.md`); điền tên nhóm, thành viên, giảng viên trong `main.tex` (khối THÔNG TIN CẦN SỬA); hai frame lý thuyết rút gọn do Người 1 viết ở `00b-ly-thuyet-rut-gon.tex`.
- [ ] **Chương 5** theo kiến trúc → triển khai → minh chứng → kết quả (mục 5).
- [ ] **Kết luận** (`05-tong-ket.tex`): số kết quả, 3 bài học chính từ Người 4, hạn chế.
- [ ] **Ghép slide:** nhận `.tex` và hình từ `04_Docs/tex-nop/` (hạn 27/11); chép vào `slides/sections/` và `slides/figures/` (đúng tên file); biên dịch `latexmk -lualatex main.tex`; kiểm tra số trang (hiện 167), không còn khung đỏ (`khungchen`), không còn `[nhóm xác nhận]`; chạy `python scripts/make_slides_zip.py`.
- [ ] **Số liệu cần đồng bộ trước khi ghép:** S78 ghi "20–26 giây", số thật 21,3–27,6 giây (S105 đã ghi 21–28); S90 ghi "16 bảng", mô hình hiện có 46 bảng; S47 "380/842" và các slide dashboard "379" cùng tồn tại (khác phạm vi đơn, có ghi chú); kiểm tra các số khác khi slide đã sửa.

### 7.4 Tổng duyệt (28–29/11)
- [ ] Chạy thử toàn bộ theo thứ tự: Phú → Người 1 → Người 2 → Người 3 → Người 4 → Phú; bấm giờ từng người (giả định ở các file `Nguoi-x.md`); điều chỉnh số slide nói khi có thời lượng chính thức.
- [ ] Chuẩn bị phương án dự phòng: ảnh chụp dashboard nếu mất mạng; slide dự phòng B01–B10 trong `99-du-phong.tex` cho 10 câu vấn đáp dễ gặp.
- [ ] Mỗi người đọc phần câu hỏi trong file của mình (mục 9); Phú đọc mục 9 của file này.

### 7.5 Giai đoạn 2 (sau thuyết trình): báo cáo
- [ ] Nhận file `.tex` báo cáo từ từng người vào `04_Docs/tex-nop/`; chép vào `report/chapters/`; `python scripts/export_latex.py` cập nhật bảng và mã sinh từ database; biên dịch `cd report && latexmk -xelatex main.tex`; đảm bảo > 100 trang (hiện 128 trang); chạy `python scripts/make_overleaf_zip.py`.
- [ ] Viết phần của mình (số trang và `\todo` ở mục 10).

## 8. Việc riêng
Phú không có việc riêng ngoài mục 7; việc dài nhất là P9, P10 và ghép file tổng.

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này:

<!-- QA:17,18,38,40 -->
**Q17. Vì sao biến đổi bằng SQL procedure thay vì pandas?**
Dữ liệu nằm sẵn trong PostgreSQL, xử lý theo tập hợp (window function, upsert) nhanh và ngắn hơn; Python chỉ điều phối và COPY. Nạp full toàn bộ 1,56 triệu dòng nguồn vào kho mất khoảng 1,5 phút.

**Q18. Dựng lại toàn bộ dự án mất bao lâu và có tái lập không?**
Một lệnh `python scripts/rebuild_all.py --drop` xoá hai database và dựng lại từ CSV: **443 giây (7,4 phút)**; kết quả giống hệt trước khi xoá (16/16 bảng khớp checksum), 130/130 test đạt khi dựng (133 sau khi thêm test địa lý).

**Q38. Những giới hạn của dự án?**
(1) Nạp tăng dần chỉ mô phỏng bản ghi mới với trạng thái cuối, không có đơn đổi trạng thái giữa chừng; (2) cơ chế thử lại mồ côi mới chứng minh bằng test; (3) toạ độ theo mã bưu chính (không phải địa chỉ), haversine là đường chim bay (sai số ≤ 0,5%); (4) dữ liệu 2016 và cuối 2018 thưa; (5) chỉ 45,1% deal có đơn nên so sánh theo kênh nhỏ (kênh Email chỉ 6 seller có đơn, đánh dấu mẫu nhỏ); (6) benchmark gọn trên một laptop.

**Q40. Nếu mở rộng, bạn sẽ làm gì tiếp?**
Thêm trạng thái trung gian của đơn (CDC thật) và lịch chạy tự động; chuyển toạ độ sang PostGIS khi cần truy vấn không gian; phân vùng `fact_order_item` theo năm khi dữ liệu lớn; thêm chiều khuyến mãi/sản phẩm theo thời gian (SCD cho giá); và đo hiệu năng nhiều người dùng đồng thời.
<!-- /QA -->

Câu mới:

**Q-P1. Vì sao lakehouse mà không dùng SQLite hay DuckDB?**
Lakehouse cần lưu trữ dạng object storage cộng table format có ACID (Apache Iceberg: giao dịch, time travel); SQLite hay DuckDB file chỉ là một CSDL trên một máy, không có các đặc tính đó nên không đúng nghĩa lakehouse.

**Q-P2. Lakehouse khác kho PostgreSQL ở đâu và bạn giải quyết giới hạn nào?**
Kho chương 3 nạp theo lô, ghi đè trạng thái của đơn và không giữ dữ liệu thô; lakehouse nhận dữ liệu liên tục qua CDC, giữ lịch sử sự kiện và dữ liệu thô ở Bronze, và tách lưu trữ khỏi tính toán. Gold có cùng star schema nên đối soát được từng con số với kho cũ. Số liệu thật: điền sau P10.

**Q-P3. Dữ liệu API đem lại gì cho kho?**
Dữ liệu Olist là ảnh chụp tĩnh nội bộ; API công khai của Brazil (IBGE, Banco Central, BrasilAPI) bổ sung dân số theo bang, tỷ giá và lạm phát, ngày lễ, để trả lời doanh thu trên đầu người, tăng trưởng thực, GMV quy đổi USD. Số liệu thật: điền sau P9.

**Q-P4. Vì sao thêm Superset khi đã có Power BI?**
Barem khuyến khích công cụ trực quan mới; DB1 dựng lại trên Superset đọc từ tầng Gold của lakehouse cho cùng số liệu với Power BI, chứng minh lớp Gold dùng được cho nhiều công cụ BI.

**Q-P5. Nếu có thêm thời gian, nhóm làm gì tiếp?**
Xem Q40 ở trên: đơn đổi trạng thái giữa chừng, PostGIS cho truy vấn bán kính, lịch chạy tự động, khai phá dữ liệu (phân lớp, phân cụm, luật kết hợp).

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Số trang hiện tại: <!-- PAGES:5.1,5.2,6.1,6.2,6.3 -->mục 5.1: trang 80 (1 trang); mục 5.2: trang 81–87 (7 trang); mục 6.1: trang 88 (1 trang); mục 6.2: trang 88 (1 trang); mục 6.3: trang 89 (1 trang); tổng 11 trang<!-- /PAGES -->. Phần `00-*` (bìa, lời mở đầu, đánh giá, từ viết tắt) và phụ lục nằm ngoài mục lục theo số chương.

Các `\todo` hiện có (đếm từ mã nguồn):

<!-- TODOS:00-bia.tex,00-loi-mo-dau.tex,00-danh-gia-thanh-vien.tex,00-tu-danh-gia.tex,00-viet-tat.tex,5-1-lakehouse.tex,5-2-thu-thap-api.tex,06-ket-luan.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/00-bia.tex` | 1 | 1. Điền tên giảng viên, lớp, nhóm, thành viên và MSSV ở bìa. |
| `report/chapters/00-loi-mo-dau.tex` | 1 | 1. Viết lời mở đầu (nửa trang đến một trang): bối cảnh (thương mại điện tử, nhu cầu phân tích dữ liệu), mục tiêu của bài tập lớn, phạm vi (hai bộ dữ liệu Olist, PostgreSQL, Power BI), bố cục báo cáo sáu chương, lờ… |
| `report/chapters/00-danh-gia-thanh-vien.tex` | 1 | 1. Trưởng nhóm điền điểm sau khi cả nhóm thống nhất; in ra và ký. Mẫu theo bảng đánh giá thành viên của môn học (5 tiêu chí). |
| `report/chapters/00-tu-danh-gia.tex` | 1 | 1. Nhóm điền cột "Đạt" và ghi chú khi hoàn thiện báo cáo. |
| `report/chapters/00-viet-tat.tex` | 1 | 1. Bổ sung các từ viết tắt khác xuất hiện trong báo cáo. |
| `report/chapters/5-1-lakehouse.tex` | 4 | 1. P10 điền: kiến trúc lakehouse (lớp lưu trữ, định dạng bảng, engine truy vấn, quan hệ với kho PostgreSQL hiện có); nêu lý do chọn công nghệ và so sánh với kho quan hệ.<br>2. P10 điền: các bước dựng lakehouse (nạp dữ liệu nguồn, phân lớp dữ liệu, truy vấn mẫu), kèm mã và lệnh chạy.<br>3. P10 điền: số liệu đo được (số bảng, số dòng, thời gian truy vấn so với PostgreSQL), hình minh hoạ, hạn chế.<br>4. P10 điền: dựng lại dashboard DB1 (tổng quan và doanh thu) trên Apache Superset, đọc tầng Gold của lakehouse qua Trino; so sánh với DB1 trên Power BI (cùng số liệu, khác công cụ); ảnh chụp figures/5-1_superset_d… |
| `report/chapters/5-2-thu-thap-api.tex` | 1 | 1. Phú dựng D8 trên Power BI, chụp ảnh đặt tên 4_D8_….png vào figures/ và chèn vào đây; đối chiếu số với bảng giá trị kỳ vọng của D8.md. |
| `report/chapters/06-ket-luan.tex` | 3 | 1. Viết lại bằng lời của nhóm. Gợi ý các ý đã có số liệu: kho dữ liệu hình sao với 10 bảng chiều và 6 bảng fact thuộc cả ba loại; hai hệ thống nguồn và 1,56 triệu dòng; pipeline chạy lại từ đầu bằng một lệnh trong…<br>2. Nhóm bổ sung bài học về làm việc nhóm, phân công, công cụ (Git, Power BI) và khó khăn thực tế.<br>3. Chỉnh danh sách hạn chế theo thực tế sau khi dựng dashboard. |
| **Tổng** | **13** | |
<!-- /TODOS -->

## 11. Mốc hạn

| Hạn | Việc | Xong |
| --- | --- | --- |
| 23/11 | Kiến trúc Lakehouse (draw.io, nếu đã có thiết kế P10); slide mở đầu | ☐ |
| 25/11 | File gốc `olist_base.pbix` và zip đã lên Drive từ trước; nhận bản đầu dashboard của mọi người | ☐ |
| 26/11 | Nhận bài học từ Người 4 (đã gom) | ☐ |
| 27/11 | Slide và dashboard xong: ghép slide và file tổng; publish, QR | ☐ |
| 28–29/11 | Tập, bấm giờ, tổng duyệt | ☐ |
| Tuần 12 | Thuyết trình | ☐ |

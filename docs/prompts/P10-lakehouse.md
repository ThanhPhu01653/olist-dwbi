# P10 – Mở rộng 1: Data Lakehouse cho Order Management

## Trước khi bắt đầu
- Đọc `CLAUDE.md`, `docs/DW_DESIGN.md`, `handoff/2026-11-14-P8.md`, handoff P9 và `docs/THU_THAP_API.md` (mở rộng 2, đã làm ở P9).
- Làm trên nhánh `phase/P10-lakehouse`. Commit sau mỗi bước. Xong thì merge vào `main` và push.
- Nếu hết lượt giữa chừng: dừng sau bước đang làm, ghi tiến độ vào `handoff/2026-11-xx-P10-lakehouse.md`, rồi commit.

## Mục tiêu
Đưa kho ở chương 3 lên một Lakehouse đúng nghĩa:
- dữ liệu vào liên tục qua CDC;
- lưu trên object storage với định dạng bảng mở Apache Iceberg (có ACID, time travel);
- Gold có cùng star schema với kho chương 3;
- đối soát được từng con số với kho cũ.

Trình bày theo ý thầy: **kiến trúc → triển khai → kết quả**. Mọi số liệu lấy từ lần chạy thật.

Thầy đã chê một nhóm khác dùng SQLite làm lakehouse vì "chưa hợp lý về công nghệ". Vì vậy:
- KHÔNG dùng SQLite hay DuckDB file để thay thế Lakehouse;
- lưu trữ phải là object storage cộng table format có ACID.

## Bước 0 – Kiểm tra máy, chọn cấu hình
Kiểm tra trên Windows của Phú: RAM, số nhân CPU, ổ trống, Docker Desktop + WSL2 (`docker version`, `docker compose version`), giới hạn bộ nhớ WSL (`.wslconfig`).

- **Chưa có Docker:** dừng lại. Hướng dẫn Phú cài Docker Desktop (bật WSL2) và đặt `.wslconfig` cho đủ bộ nhớ, rồi chờ.
- **RAM ≥ 16 GB:** chọn profile `full`.
- **RAM < 16 GB:** chọn profile `lite`:
  - bỏ Airflow, thay bằng script điều phối Python;
  - Superset chỉ bật khi demo;
  - Spark một worker.

Ghi kết quả kiểm tra vào handoff.

## Bước 1 – Thiết kế (viết trước khi code)
Tạo `docs/LAKEHOUSE.md` gồm:
- So sánh Data Warehouse / Data Lake / Lakehouse.
- Giới hạn của kho chương 3 và cách Lakehouse giải quyết:
  - nạp lô so với CDC;
  - `fact_order_fulfillment` ghi đè trạng thái so với lịch sử sự kiện;
  - không giữ dữ liệu thô;
  - lưu trữ và tính toán gắn trên một máy;
  - Power BI Import phải refresh.
- Bảng kiến trúc: tầng | công cụ | vai trò | vì sao chọn | phiên bản.
- Sơ đồ Mermaid (xuất PNG `figures/5-1_kien_truc_lakehouse.png`) và file `.drawio` để nhóm chỉnh.
- Danh sách bảng Bronze / Silver / Gold kèm grain và cách ghi (append, MERGE, thay bảng).
- Luồng sự kiện của một đơn hàng.

Ghi thêm một dòng nhật ký quyết định vào `DW_DESIGN.md`.

Stack:
- **Nguồn:** JSON từ API (P9) đi vào landing zone; dữ liệu nghiệp vụ lấy từ một PostgreSQL riêng trong Compose. Bật `wal_level=logical`, cổng khác cổng 5432 của PostgreSQL trên Windows. Nạp `oltp` + `crm` bằng chính `etl.load_source` (trỏ biến môi trường sang container). KHÔNG đụng database `olist_dw` đang dùng.
- **Thu nhận:** Debezium (Kafka Connect) + Kafka chế độ KRaft. Mỗi bảng một topic.
- **Lưu trữ:** MinIO + Apache Iceberg, catalog REST có backend bền. Ba namespace `bronze`, `silver`, `gold`, thêm `ops` cho kết quả kiểm tra.
- **Xử lý:** Spark Structured Streaming (Kafka → Bronze → Silver) và Spark batch (SCD2).
- **Mô hình hoá:** dbt với adapter dbt-trino, cho Silver → Gold.
- **Truy vấn:** Trino, connector Iceberg trỏ cùng catalog. User `bi_viewer` chỉ đọc `gold`.
- **Trực quan:** Apache Superset kết nối Trino.
- **Điều phối:** Airflow (chỉ profile `full`).
- **Phiên bản:** ghi rõ tag cho mọi image, KHÔNG dùng `latest`. Chọn bộ phiên bản Spark – Iceberg runtime – Trino – catalog tương thích nhau và ghi lý do vào `docs/LAKEHOUSE.md`.

Cấu trúc thư mục:
- `lakehouse/` gồm `docker-compose.yml`, `.env.example`, `connectors/`, `spark/`, `dbt/`, `airflow/`, `superset/`, `scripts/`, `tests/`, `README.md`.
- Dữ liệu volume không commit; thêm vào `.gitignore`.
- `.env` chứa mật khẩu, KHÔNG commit.

## Bước 2 – Hạ tầng
- `docker compose --profile full|lite up -d`; mọi dịch vụ có healthcheck.
- Script `lakehouse/scripts/check_health.py` in trạng thái từng dịch vụ.
- Lưu output `docker ps` và `docker stats --no-stream` vào handoff để làm minh chứng.

## Bước 3 – Thu nhận
- Nạp nguồn ban đầu (đến 2017-12-31) vào PostgreSQL nguồn. Đăng ký connector Debezium; snapshot ban đầu vào Kafka.
- Viết `lakehouse/scripts/replay_events.py` phát lại 11 tháng còn lại thành sự kiện theo thời gian (đồng hồ tăng tốc, tham số `--speed`):
  - đơn mới được INSERT ở thời điểm mua với trạng thái ban đầu;
  - sau đó UPDATE theo mốc duyệt → giao vận chuyển → giao khách;
  - review, payment, MQL, deal được INSERT đúng thời điểm của chúng.
  - Nhờ vậy Bronze có vòng đời thật của đơn.
- Nguồn API của P9 vào Lakehouse:
  - dùng lại collector trong `api_ingest/`, KHÔNG viết lại;
  - collector ghi JSON thô vào landing zone trên MinIO (`s3://lakehouse/landing/api/<nguồn>/<ngày>/…`);
  - Spark đọc landing zone thành các bảng `bronze.api_*` theo kiểu schema-on-read, giữ nguyên JSON;
  - Silver chuẩn hoá theo đúng quy tắc của P9;
  - Gold làm giàu `dim_geography` và `dim_date` bằng dbt, giống kho chương 3.
  - Mục đích: cho thấy Lakehouse giữ được cả dữ liệu bán cấu trúc lẫn bảng sạch trên cùng một bản dữ liệu.

## Bước 4 – Bronze → Silver (streaming)
Một ứng dụng Spark Structured Streaming, micro-batch có tham số (mặc định 30 giây).

**Bronze:**
- Append nguyên sự kiện, gồm: key, payload JSON, `op` (c/u/d/r), `ts_ms`, bảng nguồn, partition/offset Kafka, thời điểm ghi.

**Silver:**
- Áp lại quy tắc làm sạch của ODS (đọc `sql/30_ods/020_ods_procs.sql`, dịch sang Spark và giữ đúng logic):
  - khử trùng;
  - chuẩn hoá zip, thành phố;
  - loại toạ độ ngoài khung Brazil;
  - khoảng thời gian âm thành NULL;
  - review trùng giữ bản mới nhất.
- Bản ghi lỗi đưa vào bảng `*_rejected` kèm mã lỗi. Không bỏ âm thầm.
- MERGE theo khoá chính, giữ bản `ts_ms` mới nhất, để sự kiện phát lại (Debezium giao ít nhất một lần) không bị nhân đôi.
- `silver.order_status_history`: mỗi lần đơn đổi trạng thái thêm một dòng (order_id, status, valid_from, valid_to, is_current).
- SCD2 địa chỉ khách theo `customer_unique_id`, dùng MERGE của Iceberg. Logic phải khớp `dim_customer` của kho chương 3.

## Bước 5 – Silver → Gold bằng dbt
- Dựng lại 10 dimension + 6 fact đúng tên bảng và tên cột trong `DW_DESIGN.md`, cùng quy tắc (dòng Unknown key −1, GMV không tính đơn Failed…).
- Dùng lại seeds trong `seeds/`.
- dbt test: unique, not_null, relationships, accepted_values, cùng vài test tuỳ chỉnh (ví dụ tổng price khớp Silver).
- Chạy `dbt docs generate`; chụp ảnh lineage, lưu `figures/5-1_dbt_lineage.png`.
- Thêm một mart cho Superset tương đương `mart_sales` (dùng cho dashboard DB1).

## Bước 6 – Đối soát với kho chương 3 (bắt buộc, là bằng chứng chính)
`lakehouse/scripts/reconcile.py` so `gold.*` (đọc qua Trino) với `olist_dw.dw.*` (PostgreSQL):
- số dòng;
- tổng tiền;
- checksum theo khoá tự nhiên của 16 bảng;
- GMV = 13.494.400,74 BRL.

Trạng thái so sánh: kho chương 3 sau 11 đợt; Lakehouse sau khi phát lại xong. Kết quả ghi bảng vào handoff. Bảng nào lệch thì giải thích và sửa đến khi khớp, hoặc nêu rõ lý do.

## Bước 7 – Tính năng Lakehouse (minh chứng)
- **Time travel và rollback:** liệt kê snapshot của một bảng Silver; truy vấn `FOR VERSION/TIMESTAMP AS OF`. Xoá nhầm có kiểm soát trên bảng thử rồi `rollback_to_snapshot`; ghi số dòng trước / sau / khôi phục.
- **Lịch sử đơn:** một `order_id` thật đi qua các trạng thái. Câu SQL "đơn này ở trạng thái nào lúc T".
- **Đổi schema:** thêm một cột vào bảng Silver mà không viết lại dữ liệu.
- **Thống kê bảng Iceberg:** số snapshot, số file metadata/manifest/data của một bảng lớn.

## Bước 8 – Vận hành
- **Airflow** (profile `full`):
  - DAG hằng ngày: dbt run + dbt test + kiểm tra chất lượng ghi `ops.dq_results`;
  - DAG bảo trì hằng tuần: `rewrite_data_files`, `expire_snapshots` (giữ 7 ngày), `remove_orphan_files`;
  - DAG kiểm tra streaming định kỳ.
- **Profile `lite`:** script `lakehouse/scripts/run_daily.py` làm các việc tương đương.
- **Ghi lại vấn đề file nhỏ do streaming:** số file trước / sau khi gộp.

## Bước 9 – Kết quả đo
- Độ trễ từ lúc sự kiện vào Kafka tới lúc đọc được ở Bronze và Silver. Đo ít nhất 5 lần; lấy min / trung bình / max.
- Thông lượng phát (sự kiện/giây). Thời gian nạp toàn bộ.
- RAM từng dịch vụ (`docker stats`).
- Vẽ biểu đồ vào `figures/5-1_*.png`.

## Bước 10 – Superset
- Dựng lại dashboard DB1 trên Superset, đọc Gold qua Trino bằng user `bi_viewer`.
- Export dashboard ra file JSON trong repo; chụp ảnh `figures/5-1_superset_db1.png`.
- Ghi rõ visual nào thay bằng loại tương đương.

## Bước 11 – Tuỳ chọn (làm nếu còn thời gian, theo thứ tự)
1. **Cảnh báo trên luồng → `gold.order_alerts`:**
   - đơn quá ngày hứa giao mà chưa giao;
   - seller có tỉ lệ huỷ trong 7 ngày cao bất thường.
2. **Mô hình dự báo đơn giao trễ, chấm tại lúc duyệt đơn:**
   - **Đặc trưng:**
     - khoảng cách seller → khách bằng haversine;
     - phí vận chuyển, giá, cân nặng, nhóm ngành;
     - vùng khách và vùng seller;
     - số ngày hứa giao;
     - tỉ lệ giao trễ quá khứ của seller (chỉ dùng dữ liệu trước đơn đó, tránh rò rỉ).
   - **Cách chia dữ liệu và mô hình:**
     - chia theo thời gian: train đến 2017-12, test 2018;
     - Logistic Regression và một mô hình cây.
   - **Báo kết quả:** ROC-AUC, PR-AUC, recall, ma trận nhầm lẫn; ghi điểm vào `gold.order_late_scores`.

## Bước 12 – Kiểm thử
`pytest` trong `lakehouse/tests/`, gồm:
- hạ tầng sống;
- Bronze = số sự kiện nguồn;
- Silver hợp lệ + rejected = Bronze (sau khử trùng);
- SCD2 đúng;
- dbt test đạt;
- đối soát khớp;
- `bi_viewer` không đọc được `bronze`/`silver`.

## Bước 13 – Tài liệu và bàn giao
- **Handoff:** `handoff/2026-11-xx-P10-lakehouse.md` theo mẫu, gồm:
  - số liệu thật;
  - đoạn nháp cho mục 5.1;
  - danh sách ảnh minh chứng cần chụp và cách chụp (docker ps, Spark UI, Kafka/Connect, MinIO console, dbt lineage, Superset, output đối soát).
- **Báo cáo:** điền `report/chapters/5-1-lakehouse.tex` theo kiến trúc → triển khai → kết quả, có số thật.
- **Slide:** điền phần Lakehouse trong `slides/sections/04-mo-rong.tex`:
  - khoảng 15–20 slide;
  - tiêu đề là câu kết luận có số;
  - mỗi bước triển khai có một slide minh chứng.
- **Vấn đáp:** thêm câu hỏi về Lakehouse vào `huong-dan/04-cau-hoi-van-dap.md`:
  - Iceberg đạt ACID thế nào;
  - vì sao MERGE;
  - Debezium at-least-once;
  - SCD2 khác snapshot Iceberg;
  - vì sao không dùng SQLite.
- **README:** `lakehouse/README.md` hướng dẫn chạy lại từ đầu bằng vài lệnh, có bản PowerShell.

## Báo lại cho Phú
- Profile đã chọn.
- Bảng đối soát.
- Độ trễ, thông lượng, RAM.
- Kết quả time travel và rollback.
- Số test đạt.
- Phần tuỳ chọn đã làm được.
- Ảnh cần Phú tự chụp.

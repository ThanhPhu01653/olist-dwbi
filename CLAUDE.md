# CLAUDE.md – Olist DW & BI (bài tập lớn môn Kho dữ liệu & Kinh doanh thông minh, HUST)

## Dự án là gì
Xây kho dữ liệu chủ đề **Order Management** trên bộ Olist Brazilian E-Commerce, tích hợp thêm bộ **Olist Marketing Funnel**
(nối qua `seller_id`). Sản phẩm cuối: PostgreSQL DW chạy được end-to-end, 7 dashboard Power BI, báo cáo LaTeX > 100 trang
và slide > 100 trang. Báo cáo trước lớp vào **tuần 12 (30/11–6/12/2026)**; phần code phải xong trước **21/11**,
dữ liệu xuất cho Power BI phải có bản đầu tiên trước **18/11**.

**Đặc tả schema đầy đủ nằm ở `docs/DW_DESIGN.md` – đọc file đó trước khi viết bất kỳ DDL/ETL nào.**
Không tự ý đổi tên bảng/cột so với đặc tả. Nếu thấy đặc tả sai hoặc thiếu, dừng lại, nêu rõ vấn đề và đề xuất sửa `docs/DW_DESIGN.md` trước.

## Ai làm gì (để hiểu ai đọc output)
- **KT1 (Phú) là người duy nhất viết và chạy code**, làm việc cùng Claude Code. Mọi code trong repo do KT1 + Claude Code viết.
- Cả nhóm cùng làm dashboard Power BI, báo cáo LaTeX và slide **từ các file trong `handoff/`**; phân công cụ thể sẽ làm sau.

Hệ quả: những người còn lại **không thể tự chạy truy vấn**. Mọi thứ họ cần (số liệu, bảng mẫu, hình, dữ liệu cho Power BI)
phải được xuất sẵn ra file trong repo hoặc thư mục chia sẻ. Handoff phải tự giải thích được, không giả định người đọc biết SQL.

## Môi trường (không dùng Docker)
- PostgreSQL 18 (16+ đều chạy được) **cài trực tiếp** trên máy của KT1 (installer EnterpriseDB). Extension bắt buộc: `unaccent` (có sẵn).
- **PostGIS không cài** (quyết định 05/11). Mọi tính toán địa lý (khoảng cách seller → khách) dùng công thức haversine bằng SQL thuần trên cột latitude/longitude; không tạo cột `geometry`. Nếu sau này cài PostGIS thì mới thêm.
- Python 3.11 trong virtualenv (`.venv`): pandas, SQLAlchemy 2, psycopg2-binary, python-dotenv, holidays, matplotlib, seaborn, openpyxl
- Biến đổi chính viết bằng **SQL (PL/pgSQL procedure)**; Python dùng để tạo database, nạp nguồn, extract, điều phối, sinh thống kê, xuất file
- Không dùng Airflow/dbt. Điều phối bằng `python -m etl.run_pipeline`
- Viết code chạy được cả Windows lẫn macOS: dùng `pathlib`, không phụ thuộc lệnh bash; khi đưa lệnh terminal thì đưa cả bản PowerShell
- Kết nối đọc từ `.env`: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (database chính `olist_dw`), `DB_NAME_FULL` (database `olist_full` cho EDA); không hardcode mật khẩu

## Git / GitHub
- Repo GitHub (private), nhánh `main` luôn chạy được; làm mỗi phase trên nhánh `phase/Px-...` rồi merge
- Không commit `data/raw/`, `.env`, `.venv/`; `exports/powerbi/` chỉ commit nếu tổng < 50 MB, nếu lớn hơn thì chia sẻ qua Google Drive và ghi link trong `exports/README.md`
- `handoff/`, `figures/`, `docs/` luôn được commit – cả nhóm đọc trên giao diện web GitHub

## Cấu trúc repo
```
.env.example  requirements.txt  README.md  CLAUDE.md
docs/DW_DESIGN.md   docs/erd_oltp.mmd   docs/erd_dw.mmd   docs/mapping.csv
data/raw/ecommerce/*.csv        # 9 file Kaggle, KHÔNG commit
data/raw/marketing/*.csv        # 2 file Kaggle, KHÔNG commit
seeds/*.csv                     # state_region, category_group, category_translation_extra, lead_origin_group, payment_type, order_status
sql/00_init/                    # schemas, extensions, etl_log
sql/10_source/                  # DDL oltp + crm (có PK/FK)
sql/20_staging/                 # DDL stg_*
sql/30_ods/                     # DDL + procedure làm sạch
sql/40_dw/                      # DDL dim/fact + procedure nạp
sql/50_mart/                    # view mart_*
sql/60_olap_examples/           # truy vấn minh hoạ roll-up, drill-down, slice, dice, pivot (ROLAP)
sql/70_geo/                     # phần mở rộng địa lý: haversine SQL (khoảng cách seller → khách)
sql/90_tests/                   # truy vấn kiểm thử chất lượng
etl/                            # package Python: config, db, setup_db, log, load_source, simulate_increment, extract, run_pipeline, run_tests
scripts/                        # report_stats.py, export_samples.py, export_powerbi.py, eda/*.py, benchmark.py
powerbi/                        # measures.md (DAX), model.md (quan hệ, phân cấp), theme.json – nhóm dùng để dựng trong Power BI
exports/powerbi/                # CSV xuất từ dw/mart/etl_log cho Power BI
handoff/                        # bàn giao cho cả nhóm (markdown)
figures/                        # hình xuất ra cho báo cáo (png, 200 dpi)
```

## Quy ước
- Schema theo lớp: `oltp`, `crm`, `staging`, `ods`, `dw`, `mart_sales`, `mart_fulfillment`, `mart_cx`, `mart_acquisition`, `etl_log`
- snake_case; tiền tố `stg_`, `dim_`, `fact_`, `v_`; surrogate key `<tên>_key`; `date_key` = int `yyyymmdd`; dòng Unknown key `-1`
- Tiền: `numeric(12,2)`; zip: `char(5)` zero-padded
- File SQL đánh số thứ tự chạy (`010_...sql`), idempotent (`CREATE ... IF NOT EXISTS`, `CREATE OR REPLACE`), chạy lại không lỗi
- Mỗi job ETL ghi `etl_log.job_run`; dòng bị loại ghi `etl_log.rejected_rows` kèm lý do — **không bao giờ âm thầm bỏ dữ liệu**
- Comment SQL/Python bằng tiếng Anh ngắn gọn; `handoff/`, `README.md`, `powerbi/*.md` viết bằng **tiếng Việt**
- CSV xuất cho Power BI: UTF-8 có BOM, dấu phân cách `,`, số thập phân dấu `.`, ngày dạng `YYYY-MM-DD`, tên file = tên bảng

## Cách làm việc
- Làm theo từng phase trong prompt được giao; cuối phase **chạy thật** và kiểm tra kết quả (số dòng, test), không chỉ viết code
- Không đoán số liệu: mọi con số đưa vào handoff phải lấy từ truy vấn thật
- Sau mỗi phase viết `handoff/<yyyy-mm-dd>-<phase>.md` theo mẫu dưới đây và commit
- Ưu tiên đơn giản, chạy được trên laptop sinh viên (8 GB RAM); bảng lớn nhất là geolocation ~1 triệu dòng

## Mẫu handoff (người không biết code đọc để viết báo cáo, vẽ sơ đồ, dựng dashboard)
```markdown
# <Phase> – <ngày>
## Đã làm (giải thích bằng lời, không giả định người đọc biết SQL)
- ...
## Số liệu (lấy từ truy vấn thật)
| Bảng | Số dòng | Ghi chú |
## Hình / file xuất
- figures/<mục báo cáo>_<tên>.png – mô tả 1 câu
- exports/... – dùng để làm gì
## Việc cho nhóm
- (liệt kê việc cần làm: vẽ sơ đồ, kiểm tra số liệu, dựng/cập nhật Power BI, viết mục báo cáo...; chưa gán người)
## Đoạn nháp cho báo cáo (mục 3.x.x)
5–10 câu tiếng Việt giải thích làm gì, vì sao, kết quả.
## Gợi ý slide (2–4 slide)
- Slide: tiêu đề – nội dung chính – hình dùng
## SQL / code tiêu biểu
(1–2 đoạn ngắn, đáng đưa vào báo cáo)
## Vấn đề còn mở
```

## Lệnh thường dùng (cập nhật khi thêm)
- `python -m etl.setup_db` – tạo database, extension, schema, etl_log (chạy các file trong sql/00_init, sql/10_source)
- `python -m etl.load_source --initial` – nạp nguồn ban đầu (đến 2017-12-31) vào oltp/crm
- `python -m etl.run_pipeline` – chạy staging → ods → dw → mart → tests
- `python -m etl.simulate_increment --until 2018-01-31` – chèn thêm dữ liệu mới vào nguồn
- `python scripts/export_powerbi.py` – xuất CSV cho Power BI vào `exports/powerbi/`
- `python scripts/report_stats.py` – sinh `handoff/stats.md` (số dòng mọi bảng, số bản ghi từng dim)
- `python -m etl.run_tests [--only ods|dim|fact]` – chạy kiểm thử `sql/90_tests/*.sql`, ghi `etl_log.dq_check`
- `python scripts/export_samples.py` – sinh `handoff/before-after-samples.md` + `figures/3-4-3_before_after_*.png`
- `python scripts/gen_mapping.py` – sinh `docs/mapping.csv` (nguồn → đích → phép biến đổi)
- `python scripts/eda/run_all.py` – chạy toàn bộ EDA (P1) trên `olist_full`: sinh `handoff/{profiling,data-quality,distributions,correlations,funnel,design-questions,excel-toolpak-guide}.md`, `figures/3-3-1_*.png`, `exports/eda_sample.xlsx`

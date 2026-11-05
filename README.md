# Olist DW & BI – Kho dữ liệu Order Management

Bài tập lớn môn Kho dữ liệu & Kinh doanh thông minh (HUST). Xây kho dữ liệu chủ đề **Order Management** trên bộ
Olist Brazilian E-Commerce, tích hợp bộ Olist Marketing Funnel (nối qua `seller_id`).
📘 **Hướng dẫn cho cả nhóm (lộ trình theo việc, thuật ngữ, từ điển dữ liệu, hỏi đáp, dashboard): [huong-dan/00-BAT-DAU-TU-DAY.md](huong-dan/00-BAT-DAU-TU-DAY.md)**

**Cả nhóm bắt đầu từ [handoff/00-TONG-QUAN.md](handoff/00-TONG-QUAN.md)** (tổng quan, số liệu, phát hiện, việc cần làm; không cần biết lập trình).
Đặc tả schema: [docs/DW_DESIGN.md](docs/DW_DESIGN.md). Quy ước làm việc: [CLAUDE.md](CLAUDE.md). Hướng dẫn dựng Power BI: [powerbi/model.md](powerbi/model.md).

Dự án **không dùng Docker**: PostgreSQL được cài trực tiếp trên máy.

## 1. Cài đặt PostgreSQL

### Windows
1. Tải bộ cài PostgreSQL (dự án chạy trên bản 18; bản 16 trở lên đều chạy được) từ <https://www.enterprisedb.com/downloads/postgres-postgresql-downloads>, chạy với thành phần mặc định
   (PostgreSQL Server, pgAdmin 4, Command Line Tools). Đặt mật khẩu cho user `postgres` và nhớ nó; giữ cổng `5432`.
   Ở Stack Builder không cần chọn gì: dự án **không dùng PostGIS** (khoảng cách địa lý tính bằng haversine SQL thuần).
2. Kiểm tra dịch vụ đang chạy: PowerShell `Get-Service postgresql*` phải báo `Running`.

### macOS
```bash
brew install postgresql@18          # hoặc postgresql@16
brew services start postgresql@18
createuser -s postgres        # nếu chưa có user postgres (siêu quản trị)
```

`unaccent` đi kèm PostgreSQL, không cần cài thêm.

## 2. Cài môi trường Python (khuyến nghị Python 3.11; đã thử với 3.13)

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # nếu bị chặn: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
```
macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Cấu hình và dữ liệu

1. Sao chép `.env.example` thành `.env` rồi điền mật khẩu PostgreSQL (`.env` không bao giờ được commit):
   - Windows: `Copy-Item .env.example .env`
   - macOS: `cp .env.example .env`
2. Tải 2 bộ dữ liệu Kaggle và giải nén **đúng thư mục** (thư mục `data/raw/` không được commit):
   - `olistbr/brazilian-ecommerce` → `data/raw/ecommerce/` (9 file CSV)
   - `olistbr/marketing-funnel-olist` → `data/raw/marketing/` (2 file CSV)

## 4. Chạy

### 4.1 Cả dự án bằng một lệnh (khoảng 7 phút)
```powershell
python scripts/rebuild_all.py --drop      # xoá và dựng lại từ đầu: setup -> nạp nguồn -> pipeline full -> 11 đợt tăng dần -> test -> xuất CSV
python scripts/rebuild_all.py             # như trên nhưng giữ database cũ (mọi bước chạy lại được)
```
Kết quả (thời gian từng bước, số test, so sánh với trạng thái trước) ghi ở `handoff/rebuild-report.md`. Cuối cùng `olist_dw` ở **trạng thái đủ dữ liệu** (99.441 đơn, GMV 13,49 triệu BRL) và `exports/powerbi/` có 37 file CSV cho Power BI.

### 4.2 Từng bước
```powershell
python -m etl.setup_db --check                    # kiểm tra kết nối và extension unaccent
python -m etl.setup_db                            # tạo olist_dw + olist_full, chạy toàn bộ DDL, procedure, view (sql/00_init ... 70_geo)
python -m etl.load_source --initial               # nạp nguồn đến 2017-12-31 vào olist_dw
python -m etl.load_source --full --database olist_full   # nạp toàn bộ vào olist_full (dùng cho EDA)
python -m etl.run_pipeline --mode full --no-export       # staging -> ODS -> dim -> fact -> mart -> test (trạng thái ban đầu)
python scripts/replay_increments.py               # 11 đợt hằng tháng: simulate_increment + run_pipeline --mode incremental
python -m etl.run_pipeline --mode incremental     # chạy lại một đợt: 0 dòng mới; test + xuất CSV Power BI
python -m etl.run_tests                           # chỉ chạy kiểm thử (sql/90_tests), ghi etl_log.dq_check
```
Các báo cáo và bản xuất phụ: `python scripts/report_stats.py` (handoff/stats.md), `python scripts/eda/run_all.py` (EDA trên olist_full),
`python scripts/run_olap_examples.py` (handoff/olap-examples.md), `python scripts/benchmark.py` (hiệu năng), `python scripts/geo_analysis.py` (khoảng cách địa lý),
`python scripts/gen_powerbi_docs.py` (giá trị kỳ vọng trong powerbi/measures.md), `python scripts/export_powerbi.py` (CSV cho Power BI).
Tất cả chạy lại được nhiều lần (`IF NOT EXISTS`, `CREATE OR REPLACE`, upsert). `load_source --initial` đưa nguồn về trạng thái ban đầu.
Dòng bị loại luôn được ghi vào `etl_log.rejected_rows` kèm lý do; không có dòng nào bị bỏ âm thầm.

### 4.3 Cấu trúc thư mục
```
huong-dan/      hướng dẫn cho cả nhóm: lộ trình đọc, pipeline bằng lời, thuật ngữ, từ điển dữ liệu, 40 câu hỏi đáp, nghiệp vụ (nháp), D1-D7
handoff/        bàn giao cho cả nhóm: 00-TONG-QUAN.md (đọc trước), một file cho mỗi phase P0-P7, các bảng số liệu sinh tự động
docs/           DW_DESIGN.md (đặc tả + nhật ký quyết định), sơ đồ Mermaid (*.mmd), diagrams/*.drawio (mở bằng draw.io), mapping nguồn -> đích
figures/        hình cho báo cáo (png)
powerbi/        model.md (dựng Power BI từng bước), measures.md (DAX + giá trị kỳ vọng), theme.json
exports/        powerbi/ = CSV cho Power BI (không commit nếu > 50 MB, xem exports/README.md), eda_sample.xlsx
sql/            00_init, 10_source, 20_staging, 30_ods, 40_dw, 50_mart, 60_olap_examples, 70_geo, 90_tests
etl/            setup_db, load_source, simulate_increment, extract, run_pipeline, run_tests, load_dw, procs, log ...
scripts/        rebuild_all, replay_increments, export_powerbi, report_stats, benchmark, geo_analysis, eda/ ...
seeds/          bảng tham chiếu (bang -> vùng, nhóm ngành hàng, nhóm kênh...)
data/raw/       CSV Kaggle (không commit)
```

## 5. Xử lý sự cố

| Triệu chứng | Cách xử lý |
| --- | --- |
| `Cannot connect to PostgreSQL ...` | Dịch vụ chưa chạy hoặc sai `DB_PORT`/`DB_PASSWORD` trong `.env` |
| `Missing ... CSV files` | Kiểm tra đã giải nén đúng vào `data/raw/ecommerce` và `data/raw/marketing` |
| `This role cannot create databases` | Dùng user `postgres` (siêu quản trị) trong `.env` |
| `rebuild_all.py --drop` báo không xoá được database | Đóng pgAdmin / DBeaver / Power BI đang kết nối, rồi chạy lại |
| Pipeline dừng với `PIPELINE FAILED` | Xem `etl_log.job_run` (cột `status`, `message`); sửa nguyên nhân rồi chạy lại cùng lệnh |

# Olist DW & BI – Kho dữ liệu Order Management

Bài tập lớn môn Kho dữ liệu & Kinh doanh thông minh (HUST). Xây kho dữ liệu chủ đề **Order Management** trên bộ
Olist Brazilian E-Commerce, tích hợp bộ Olist Marketing Funnel (nối qua `seller_id`).
Đặc tả schema: [docs/DW_DESIGN.md](docs/DW_DESIGN.md). Quy ước làm việc: [CLAUDE.md](CLAUDE.md).

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

```powershell
python -m etl.setup_db --check                    # kiểm tra kết nối và extension unaccent
python -m etl.setup_db                            # tạo olist_dw + olist_full, chạy sql/00_init và sql/10_source
python -m etl.load_source --initial               # nạp nguồn đến 2017-12-31 vào olist_dw
python -m etl.load_source --full --database olist_full   # nạp toàn bộ vào olist_full (dùng cho EDA)
python scripts/report_stats.py                    # sinh handoff/stats.md (số dòng, số cột, dung lượng)
python scripts/eda/run_all.py                     # khám phá dữ liệu (EDA) trên olist_full: handoff/*.md, figures/3-3-1_*.png, exports/eda_sample.xlsx
```
Tất cả lệnh chạy lại được nhiều lần: `setup_db` dùng `IF NOT EXISTS`, `load_source` xoá rồi nạp lại 11 bảng nguồn
(chạy lại `--initial` sẽ đưa nguồn về trạng thái ban đầu).
Dòng vi phạm khoá chính / khoá ngoại / NOT NULL không được nạp mà ghi vào `etl_log.rejected_rows`.

Các lệnh `etl.run_pipeline` và `etl.simulate_increment` trong CLAUDE.md sẽ có ở các phase sau.

## 5. Xử lý sự cố

| Triệu chứng | Cách xử lý |
| --- | --- |
| `Cannot connect to PostgreSQL ...` | Dịch vụ chưa chạy hoặc sai `DB_PORT`/`DB_PASSWORD` trong `.env` |
| `Missing ... CSV files` | Kiểm tra đã giải nén đúng vào `data/raw/ecommerce` và `data/raw/marketing` |
| `This role cannot create databases` | Dùng user `postgres` (siêu quản trị) trong `.env` |

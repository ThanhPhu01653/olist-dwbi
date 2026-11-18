# api_ingest – thu thập dữ liệu công khai của Brazil qua API

Bộ Olist chỉ có dữ liệu nội bộ của sàn và là ảnh chụp tĩnh. Package này lấy dữ liệu công khai, có thật, qua API để làm giàu kho: dân số và PIB theo đô thị (IBGE), tỷ giá USD/BRL và lạm phát IPCA (Banco Central do Brasil), ngày lễ quốc gia (BrasilAPI), lượng mưa (Open-Meteo, tuỳ chọn). Thiết kế đầy đủ, bảng nguồn và kết quả: [`docs/THU_THAP_API.md`](../docs/THU_THAP_API.md).

```
API  →  collector  →  landing zone (JSON thô)  →  staging api.stg_api_*  →  ODS  →  kho (dim_geography, dim_date, fact_state_year)  →  mart_market  →  Power BI (D8)
```

## Chạy bằng vài lệnh

Cần PostgreSQL đang chạy, `.env` đã điền và `pip install -r requirements.txt` (thêm `requests`, `rapidfuzz`, `pytest`).

**PowerShell (Windows)**
```powershell
.\.venv\Scripts\Activate.ps1
python -m etl.setup_db                                  # tạo schema api, bảng stg_api_*, ODS, bảng mới của kho (chạy lại không lỗi)
python -m api_ingest.run --source all                   # gọi API -> data\raw\api\<nguồn>\<ngày>\*.json -> staging -> ODS -> ghép đô thị
python -m etl.run_pipeline --mode incremental --with-api --api-offline   # đưa vào kho: dim_geography, dim_date, fact_state_year, mart, kiểm thử
python scripts\export_powerbi.py                        # xuất CSV cho D8
```

**macOS / Linux**
```bash
source .venv/bin/activate
python -m etl.setup_db
python -m api_ingest.run --source all
python -m etl.run_pipeline --mode incremental --with-api --api-offline
python scripts/export_powerbi.py
```

Các tuỳ chọn:

| Lệnh | Tác dụng |
| --- | --- |
| `python -m api_ingest.run --source ibge` (hoặc `bcb`, `holidays`, `weather`) | chỉ một nguồn |
| `python -m api_ingest.run --offline` | không gọi API: nạp lại những gì đã có trong `data/raw/api/` vào staging và ODS |
| `python -m api_ingest.run --fetch-only` | chỉ gọi API và ghi landing zone |
| `python -m etl.run_pipeline --with-api` | pipeline gọi API trước khi nạp chiều (lỗi API được ghi log, không làm hỏng pipeline) |
| `python -m etl.run_pipeline --with-api --api-offline` | dùng dữ liệu đã có trong landing zone, không dùng mạng |
| `python scripts/rebuild_all.py --drop` | dựng lại toàn bộ từ đầu; bước API dùng landing zone, không cần mạng |
| `python -m pytest tests -q` | kiểm thử collector (không gọi API thật) |

## Thư mục và bảng

| Thành phần | Ở đâu |
| --- | --- |
| Landing zone (JSON nguyên văn, không commit) | `data/raw/api/<nguồn>/<ngày chạy>/<tên>.json` và `manifest.json` (URL, thời điểm gọi, HTTP status, số bản ghi, dung lượng, sha256, thời gian, số lần thử) |
| Nhật ký lời gọi | `etl_log.api_call`; watermark chuỗi Banco Central: `etl_log.watermark` (`api.bcb_sgs_1`, `api.bcb_sgs_433`) |
| Staging | schema `api`: `stg_api_ibge_estado`, `_municipio`, `_populacao`, `_pib`, `_ipca`, `stg_api_bcb_serie`, `stg_api_holiday`, `stg_api_weather_station`, `_daily` |
| ODS | `ods.ibge_municipio`, `ibge_population`, `ibge_gdp`, `fx_usd_brl`, `ipca_month`, `holiday_official`, `weather_daily`, `city_ibge_match` |
| Kho | `dw.dim_geography` (cột IBGE), `dw.dim_date` (tỷ giá, IPCA, ngày lễ), `dw.fact_state_year` |
| Mart | schema `mart_market` |
| Hạt giống ghép tay | `seeds/city_ibge_override.csv` |

## Cách hoạt động

- **Collector** (`collect.py`, `http.py`): `requests` có thử lại tối đa 5 lần với chờ tăng dần (1,5 / 3 / 6 / 12 giây) cho lỗi mạng và HTTP 429, 5xx; timeout; khoảng cách tối thiểu giữa hai lời gọi tới cùng một máy chủ; User-Agent chung (không có email cá nhân). Mã bảng và mã biến của IBGE được đối chiếu với metadata của chính API trước khi lấy dữ liệu.
- **Idempotent và tăng dần:** chạy lại cùng ngày ghi đè cùng file (không nhân đôi); chuỗi Banco Central chỉ xin phần sau watermark; danh mục và dân số IBGE thay toàn bộ trong một transaction. Staging nạp bằng `TRUNCATE + COPY` hoặc upsert theo khoá tự nhiên.
- **Lỗi API:** ghi vào `etl_log.api_call` và `etl_log.job_run` (`api.collect`), nguồn lỗi không chặn nguồn khác; pipeline chính vẫn chạy và các cột mới của kho giữ NULL.
- **Ghép thành phố Olist ↔ đô thị IBGE** (`match.py`): bốn tầng, đếm tỉ lệ sau từng tầng (`etl_log.api_match_stat`): khớp đúng, sau `unaccent` và chuẩn hoá, fuzzy (`rapidfuzz`, ngưỡng 95 và ứng viên thứ hai thấp hơn ít nhất 10 điểm), bảng ghép tay. Cặp không khớp ghi `etl_log.rejected_rows` kèm lý do.

# CLAUDE.md – Olist DW & BI (bài tập lớn môn Kho dữ liệu & Kinh doanh thông minh, HUST)

File hướng dẫn cho Claude Code; thành viên nhóm không cần đọc.

## Trạng thái hiện tại (cập nhật 27/11/2026) – đọc đầu tiên

- **Session mới: đọc `handoff/2026-11-27-chuyen-session.md` trước.** Nó ghi trạng thái `main`, các prompt P8–P12g đã chạy, quy ước và lệnh hay dùng.
- Kho, ETL, lakehouse, API, báo cáo LaTeX, 4 dashboard (thiết kế, PBIP sinh sẵn) đã xong; bộ Beamer (`slides/`) giữ nguyên nhưng không còn dùng để thuyết trình.
- Slide thuyết trình mới là **pptx** theo `docs/prompts/P13-slide-pptx.md` và `slides-pptx/template/`; P13 chưa chạy, khi chạy dừng sau bước 1 cho Phú duyệt.
- Đang chờ: nhóm nộp slide vào `slides-pptx/nop/Nguoi-X`; ảnh D8 `4_D8_mot_trang.png`; file ghép Power BI `powerbi/DB_nhom_19_half_done.pbix` (đang làm dở); Publish to web bị tenant HUST chặn.
- Không commit `.pbix`, `attach/`, `.env`; file Power BI Desktop tự lưu đè trong `powerbi/olist_base/` chỉ commit khi có thay đổi thật (lineageTag, định dạng, đường dẫn thì restore).

## Dự án là gì
Xây kho dữ liệu chủ đề **Order Management** trên bộ Olist Brazilian E-Commerce, tích hợp thêm bộ **Olist Marketing Funnel**
(nối qua `seller_id`). Sản phẩm cuối: PostgreSQL DW chạy được end-to-end, 4 dashboard Power BI, báo cáo LaTeX > 100 trang
và slide > 100 trang. Bản nháp đủ (báo cáo, slide, dashboard) trước **29/11**; báo cáo trước lớp vào **tuần 12 (30/11–6/12/2026)**;
phần code phải xong trước **21/11**, dữ liệu xuất cho Power BI phải có bản đầu tiên trước **18/11**.

**Đặc tả schema đầy đủ nằm ở `docs/DW_DESIGN.md` – đọc file đó trước khi viết bất kỳ DDL/ETL nào.**
Không tự ý đổi tên bảng/cột so với đặc tả. Nếu thấy đặc tả sai hoặc thiếu, dừng lại, nêu rõ vấn đề và đề xuất sửa `docs/DW_DESIGN.md` trước.

## Ai làm gì và nơi chạy code
- Phú là người duy nhất viết và chạy code cùng Claude Code; database và code nằm trên máy của Phú.
- Cả nhóm cùng dựng dashboard Power BI, viết báo cáo LaTeX và làm slide **từ các file trong `handoff/`**; không chia vai theo người.

Hệ quả: database nằm trên một máy. Mọi thứ dashboard, báo cáo và slide cần (số liệu, bảng mẫu, hình, dữ liệu cho Power BI)
phải được xuất sẵn ra file trong repo hoặc thư mục chia sẻ. Handoff tự giải thích được: nêu thuật ngữ khi dùng lần đầu, không đòi hỏi truy cập database.

## Môi trường (không dùng Docker)
- PostgreSQL 18 (16+ đều chạy được) **cài trực tiếp** trên máy của Phú (installer EnterpriseDB). Extension bắt buộc: `unaccent` (có sẵn).
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
sql/25_api/                     # P9: staging schema api (stg_api_*)
sql/30_ods/                     # DDL + procedure làm sạch
sql/40_dw/                      # DDL dim/fact + procedure nạp
sql/50_mart/                    # view mart_*
sql/60_olap_examples/           # truy vấn minh hoạ roll-up, drill-down, slice, dice, pivot (ROLAP)
sql/70_geo/                     # phần mở rộng địa lý: haversine SQL (khoảng cách seller → khách)
sql/90_tests/                   # truy vấn kiểm thử chất lượng
etl/                            # package Python: config, db, setup_db, log, load_source, simulate_increment, extract, run_pipeline, run_tests
api_ingest/                     # P9: collector API (collect, http, stage, ods, match, run), README.md; tests/ = pytest
scripts/                        # report_stats.py, export_samples.py, export_powerbi.py, eda/*.py, benchmark.py
powerbi/                        # measures.md (DAX), model.md (quan hệ, phân cấp), theme.json – nhóm dùng để dựng trong Power BI
powerbi/olist_base/             # dự án Power BI dạng PBIP (TMDL + PBIR) sinh sẵn bằng scripts/gen_pbip.py; README.md hướng dẫn mở, Refresh, lưu .pbix
exports/powerbi/                # CSV xuất từ dw/mart/etl_log cho Power BI
handoff/                        # bàn giao cho cả nhóm (markdown)
huong-dan/                      # hướng dẫn dùng chung: lộ trình đọc, pipeline bằng lời, thuật ngữ, từ điển dữ liệu, hỏi đáp, DB1-DB4; phan-viec/ = hướng dẫn từng người
report/                         # báo cáo LaTeX (XeLaTeX): chapters/ viết tay, tables/ sinh từ database (scripts/export_latex.py)
slides/                         # slide Beamer theme HUST (LuaLaTeX): sections/ xếp theo barem, mỗi file một chủ (sửa tay từ P8; không chạy lại gen_beamer.py), hust-theme/, thu-mot-phan.tex (biên dịch thử một file)
figures/                        # hình xuất ra cho báo cáo (png, 200 dpi)
```

## Quy ước
- Schema theo lớp: `oltp`, `crm`, `staging`, `ods`, `dw`, `mart_sales`, `mart_fulfillment`, `mart_cx`, `mart_acquisition`, `etl_log`
- snake_case; tiền tố `stg_`, `dim_`, `fact_`, `v_`; surrogate key `<tên>_key`; `date_key` = int `yyyymmdd`; dòng Unknown key `-1`
- Tiền: `numeric(12,2)`; zip: `char(5)` zero-padded
- Slide: theo `slides/QUY-TAC-TRINH-BAY.md`; trước khi commit slide chạy `python scripts/kiem_tra_slide.py --strict` (0 LỖI) và xem ảnh `--anh`.
- File SQL đánh số thứ tự chạy (`010_...sql`), idempotent (`CREATE ... IF NOT EXISTS`, `CREATE OR REPLACE`), chạy lại không lỗi
- Mỗi job ETL ghi `etl_log.job_run`; dòng bị loại ghi `etl_log.rejected_rows` kèm lý do — **không bao giờ âm thầm bỏ dữ liệu**
- Comment SQL/Python bằng tiếng Anh ngắn gọn; `handoff/`, `README.md`, `powerbi/*.md` viết bằng **tiếng Việt**
- Tài liệu viết giọng trung lập cho mọi người đọc; không phân loại người đọc theo trình độ hay vai trò.
- CSV xuất cho Power BI: UTF-8 có BOM, dấu phân cách `,`, số thập phân dấu `.`, ngày dạng `YYYY-MM-DD`, tên file = tên bảng

## Cách làm việc
- Làm theo từng phase trong prompt được giao; cuối phase **chạy thật** và kiểm tra kết quả (số dòng, test), không chỉ viết code
- Không đoán số liệu: mọi con số đưa vào handoff phải lấy từ truy vấn thật
- Sau mỗi phase viết `handoff/<yyyy-mm-dd>-<phase>.md` theo mẫu dưới đây và commit
- Ưu tiên đơn giản, chạy được trên laptop sinh viên (8 GB RAM); bảng lớn nhất là geolocation ~1 triệu dòng

## Mẫu handoff (dùng để viết báo cáo, vẽ sơ đồ, dựng dashboard)
```markdown
# <Phase> – <ngày>
## Đã làm (giải thích bằng lời; nêu thuật ngữ khi dùng lần đầu)
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
- `python -m etl.run_pipeline [--mode full|incremental] [--no-export]` – chạy staging → ods → dim → fact → tests → snapshot → export Power BI
- `python -m api_ingest.run --source all|ibge|bcb|holidays|weather [--offline] [--fetch-only]` – P9: gọi API công khai (IBGE, Banco Central, BrasilAPI, Open-Meteo) → landing zone `data/raw/api/` → staging `api` → ODS → ghép đô thị; `python -m etl.run_pipeline --with-api [--api-offline]` đưa vào kho (`dim_geography`, `dim_date`, `fact_state_year`, `mart_market`); `python scripts/p9_results.py` – số liệu, bảng, hình chương 5.2 → `handoff/2026-11-18-P9-results.md`, `report/tables/p9_*.tex`, `figures/5-2_*.png`; `python -m pytest tests -q` – kiểm thử collector
- `python -m etl.simulate_increment [--until 2018-01-31]` – chèn thêm dữ liệu mới vào nguồn (mặc định +1 tháng)
- `python scripts/replay_increments.py` – lặp simulate + `run_pipeline --mode incremental` tới hết dữ liệu nguồn (in bảng các đợt)
- `python scripts/compare_databases.py --a olist_dw --b <db full> [--keys]` – so sánh hai database kho (số dòng, tổng tiền, checksum; `--keys` so cả giá trị khoá thay thế, chỉ dùng cho hai bản dựng cùng code và cùng đường nạp)
- `python scripts/run_olap_examples.py` – chạy 5 thao tác OLAP ở `sql/60_olap_examples/`, sinh `handoff/olap-examples.md`
- `python scripts/gen_phan_viec.py` – điền các khối sinh tự động của `huong-dan/phan-viec/*.md` (bảng slide đang có đọc từ `slides/sections/*.tex`, số `	odo` và số trang báo cáo, câu hỏi đáp từ `huong-dan/04-cau-hoi-van-dap.md`); chạy lại sau khi sửa slide hoặc biên dịch lại báo cáo
- `python scripts/gen_pbip.py [--no-csv]` – sinh `powerbi/olist_base/` (dự án PBIP: mô hình, quan hệ, measure, báo cáo 6 trang trống) từ `powerbi/model.md`, `measures.md`, `theme.json` và kiểm tra (measure, quan hệ, kiểu cột, JSON schema); chạy sau `gen_powerbi_docs.py`
- `python scripts/gen_powerbi_docs.py` – cập nhật giá trị kỳ vọng trong `powerbi/measures.md` và phụ lục M trong `powerbi/model.md`
- `python scripts/rebuild_all.py [--drop]` – dựng lại TOÀN BỘ bằng một lệnh (setup → nạp nguồn → pipeline full → 11 đợt tăng dần → test → xuất CSV), ghi `handoff/rebuild-report.md`
- `python scripts/benchmark.py` – benchmark gọn (oltp vs dw, index FK, view vs materialized view) → `handoff/benchmark.md`, `figures/3-5-1_benchmark.png`
- `python scripts/geo_analysis.py` – khoảng cách seller → khách vs freight / lead time → `handoff/geo-distance.md`, `figures/3-5-2_*.png`
- `python scripts/export_latex.py` – sinh `report/tables/*.tex`, `report/code/*.sql` từ database; báo cáo: `cd report && latexmk -xelatex main.tex`; zip Overleaf: `python scripts/make_overleaf_zip.py`
- `python scripts/gen_beamer.py` – (**đã lỗi thời sau P8, không chạy**: sinh theo cấu trúc cũ) sinh `slides/sections/*.tex` từ `slides/slide-script.md`; slide: `cd slides && latexmk -lualatex main.tex` (bản có ghi chú: `slides-notes.tex`); zip: `python scripts/make_slides_zip.py`
- `python -m etl.test_orphan_retry` – kịch bản thử lại dòng mồ côi (chạy trong transaction rồi rollback)
- `python scripts/export_powerbi.py` – xuất CSV cho Power BI vào `exports/powerbi/`
- `python scripts/report_stats.py` – sinh `handoff/stats.md` (số dòng mọi bảng, từng dim và từng fact)
- `python -m etl.run_tests [--only ods|dim|fact]` – chạy kiểm thử `sql/90_tests/*.sql`, ghi `etl_log.dq_check`
- `python scripts/export_samples.py` – sinh `handoff/before-after-samples.md` + `figures/3-4-3_before_after_*.png`
- `python scripts/gen_mapping.py` – sinh `docs/mapping.csv` và `docs/mapping_oltp_olap.md` (nguồn → đích → phép biến đổi, gồm dim và fact)
- `python scripts/eda/run_all.py` – chạy toàn bộ EDA (P1) trên `olist_full`: sinh `handoff/{profiling,data-quality,distributions,correlations,funnel,design-questions,excel-toolpak-guide}.md`, `figures/3-3-1_*.png`, `exports/eda_sample.xlsx`
- `python scripts/eda/run_all.py` (từ P8 còn chạy thêm) – `source_profile.py` (tần suất, taxonomy), `p8_outliers.py` (IQR, iForest), `p8_association.py` (Cramér's V, η), `p8_seasonality.py` (STL), `p8_describe.py` (thống kê đặc trưng + sheet `python_doi_chieu` của `exports/eda_sample.xlsx`), `p8_dictionary.py` (từ điển nguồn) → `handoff/2026-11-14-P8-eda.md`, `figures/3-1_*.png`, `2-4_*.png`
- `python scripts/gen_drawio.py` – sinh `docs/diagrams/*.drawio` và PNG nháp (BẢN NHÁP) cho data flow, ERD tô màu, kiến trúc theo lớp, data model logic / vật lý / mart (dùng `scripts/diagram_kit.py`, `scripts/drawio_p8.py`)
- `python scripts/p8_layers.py | p8_business.py | p8_mapping_summary.py | p8_dimensions.py | p8_etl.py` – bảng và số liệu P8 từ database → `report/tables/p8_*.tex`, `handoff/2026-11-14-P8-*.md`; `python scripts/gen_dashboard_docs.py` – (chạy sau `gen_powerbi_docs.py`) sinh `huong-dan/dashboards/DB1-DB4.md` và `README.md` (ma trận checklist); `python scripts/p8b_dashboard_tables.py` – bảng thống kê và ma trận cho chương 4; `python scripts/sync_figures.py` – chép `figures/` sang `report/figures`, `slides/figures`

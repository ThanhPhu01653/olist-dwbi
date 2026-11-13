# P9 – Mở rộng 2: Thu thập dữ liệu thực tế từ API để làm giàu kho

Trước khi làm:
- Đọc `CLAUDE.md`, `docs/DW_DESIGN.md`, `handoff/2026-11-14-P8.md`.
- Làm trên nhánh `phase/P9-api`; commit sau mỗi bước; xong thì merge vào `main` và push.
- Nếu hết lượt giữa chừng: dừng sau bước đang làm, ghi tiến độ vào handoff, rồi commit.

## Mục tiêu
Bộ Olist chỉ có dữ liệu nội bộ của sàn. Bước này lấy dữ liệu công khai, có thật, của Brazil qua API để làm giàu kho, rồi trả lời các câu hỏi Olist không tự trả lời được:
- doanh thu trên đầu người theo bang và thành phố;
- tăng trưởng thực sau khi trừ lạm phát;
- GMV quy đổi USD;
- ngày lễ chính thức;
- (tuỳ chọn) thời tiết có làm giao trễ không.

Trình bày theo ý thầy: **kiến trúc → triển khai → kết quả**. Mọi số liệu lấy từ lần chạy thật.

Phần này độc lập với Docker: chạy được ngay trên PostgreSQL hiện có. P10 (Lakehouse) sẽ dùng lại collector này để đưa JSON thô vào landing zone.

## Nguồn API (đều công khai, không cần khoá)
Kiểm tra từng endpoint bằng lời gọi thật trước khi viết code. Mã bảng, mã chuỗi phải tra trong metadata của chính API và ghi lại; KHÔNG đoán.

1. **IBGE Localidades** (`servicodados.ibge.gov.br/api/v1/localidades`):
   - danh sách bang và khoảng 5.570 đô thị;
   - phân cấp chính thức: vùng → bang → mesorregião → microrregião → đô thị, kèm mã IBGE.
2. **IBGE Agregados / SIDRA** (`servicodados.ibge.gov.br/api/v3/agregados`):
   - ước tính dân số theo đô thị cho 2016–2018;
   - (nếu có) PIB theo đô thị, PIB bình quân đầu người.
3. **Banco Central do Brasil – SGS** (`api.bcb.gov.br/dados/serie/bcdata.sgs.<mã>/dados`):
   - tỷ giá USD/BRL theo ngày;
   - IPCA theo tháng (lạm phát).
   - Có thể thêm lãi suất Selic.
4. **BrasilAPI – feriados** (`brasilapi.com.br/api/feriados/v1/<năm>`):
   - ngày lễ quốc gia 2016–2018;
   - đối chiếu với cờ ngày lễ đang có trong `dim_date` (thư viện `holidays`).
5. **(Tuỳ chọn) Open-Meteo Archive:**
   - lượng mưa theo ngày tại 27 thủ phủ bang, 2016–2018.

## Bước 1 – Thiết kế
Viết `docs/THU_THAP_API.md` gồm:
- **Bài toán:** câu hỏi nào Olist không trả lời được.
- **Bảng nguồn API:** endpoint | dữ liệu | định dạng | tần suất cập nhật thật của nguồn | giới hạn gọi | giấy phép/điều khoản.
- **Kiến trúc** (sơ đồ Mermaid xuất PNG `figures/5-2_kien_truc_api.png`, kèm `.drawio`):
  - collector → landing zone JSON thô → staging (schema `api`) → ODS chuẩn hoá và ghép → DW (làm giàu dimension, thêm fact) → mart → Power BI.
- **Bảng tần suất thu thập đề xuất:** tỷ giá hằng ngày, IPCA hằng tháng, dân số hằng năm, ngày lễ hằng năm, danh mục đô thị khi IBGE cập nhật.
- **Thay đổi schema:** liệt kê đủ. Thêm dòng nhật ký quyết định vào `DW_DESIGN.md`.

## Bước 2 – Collector (`api_ingest/`)
- Python `requests` + retry có backoff, timeout, giới hạn tốc độ, User-Agent chung (không dùng email cá nhân).
- **Landing zone:**
  - ghi JSON thô nguyên văn vào `data/raw/api/<nguồn>/<ngày chạy>/…json` (không commit);
  - kèm file manifest: URL, thời điểm gọi, HTTP status, số bản ghi, checksum.
- **Idempotent và tăng dần:**
  - chạy lại không nhân đôi;
  - tỷ giá, IPCA chỉ lấy phần mới từ mốc đã có (watermark);
  - danh mục và dân số thay toàn bộ có kiểm soát.
- **Ghi log:** mỗi lần chạy ghi `etl_log.job_run`. Lỗi gọi API ghi rõ, không làm hỏng pipeline chính.
- **Lệnh:**
  - `python -m api_ingest.run --source all|ibge|bcb|holidays|weather`;
  - thêm bước tuỳ chọn `--with-api` vào `etl.run_pipeline`.

## Bước 3 – Staging và ODS (SQL procedure, giữ phong cách dự án)
- **Staging:** schema `api` gồm các bảng `stg_api_*`, nạp từ JSON (bóc JSON bằng SQL hoặc Python).
- **Ghép thành phố Olist ↔ đô thị IBGE theo (bang, tên)**, đi qua từng tầng và ĐẾM tỉ lệ khớp sau mỗi tầng (đây là kết quả chính):
  1. khớp đúng;
  2. sau `unaccent` + chữ thường + bỏ ký tự thừa;
  3. fuzzy (`rapidfuzz` hoặc `pg_trgm`) với ngưỡng ghi rõ, chỉ nhận khi duy nhất một ứng viên;
  4. bảng ghép tay `seeds/city_ibge_override.csv` cho phần còn lại có thể xác định.
- **Không khớp:** dòng không khớp ghi `etl_log.rejected_rows` kèm lý do. Không bỏ âm thầm.
- **Ngày lễ:** đối chiếu BrasilAPI với cờ ngày lễ hiện có; báo chênh lệch.

## Bước 4 – Làm giàu kho (thêm cột, không đổi khoá)
Mọi thay đổi ghi vào `DW_DESIGN.md` và từ điển dữ liệu; thêm test.

- **`dim_geography`:** thêm `ibge_municipio_code`, `microrregiao`, `mesorregiao`, `populacao_<năm>`, `match_method`.
  - Phân cấp chiều khái niệm mới: vùng → bang → mesorregião → microrregião → đô thị → zip.
  - Cập nhật mục 3.4 của báo cáo.
- **`dim_date`:** thêm `usd_brl` (ngày không giao dịch lấy giá ngày làm việc gần nhất trước đó), `ipca_index` (chỉ số luỹ kế, mốc tháng đầu kỳ = 100), `is_holiday_official`, `holiday_name_official`.
- **Bảng mới `dw.fact_state_year`:** periodic snapshot, grain = bang × năm. Gồm dân số, PIB (nếu có), GMV, số đơn, số khách, số seller của Olist.
- **Mart / view mới:**
  - GMV mỗi 1.000 dân theo bang và theo đô thị lớn;
  - GMV quy USD theo tháng;
  - GMV thực (giá cố định) và tăng trưởng thực so với danh nghĩa;
  - (tuỳ chọn) tỉ lệ giao trễ theo mức mưa ngày giao.
- **Khoá:** giữ cố định giữa các lần dựng (ORDER BY khoá tự nhiên như đã sửa).
- **Kiểm tra:**
  - chạy `rebuild_all.py --drop`;
  - đối soát số dòng các bảng cũ không đổi, GMV vẫn 13.494.400,74;
  - test mới đều đạt.

## Bước 5 – Kết quả và phân tích
- **Bảng thu thập:** số lời gọi, thời gian, số bản ghi, dung lượng JSON theo từng nguồn.
- **Ghép đô thị:**
  - tỉ lệ khớp theo từng tầng;
  - số zip / thành phố được gán mã IBGE;
  - vài ví dụ tên lệch đã sửa được.
- **Phát hiện:**
  - top / bottom bang theo GMV mỗi 1.000 dân;
  - so sánh với xếp hạng theo GMV tuyệt đối;
  - tăng trưởng 2017 → 2018 danh nghĩa và thực;
  - GMV USD;
  - ngày lễ có ảnh hưởng số đơn không.
- **Hình:** `figures/5-2_*.png`, gồm bản đồ hoặc bar theo bang, line danh nghĩa so với thực, biểu đồ tỉ lệ khớp theo tầng. Ảnh D8 do Phú chụp sau khi dựng.
- **Power BI – dashboard D8 "Thị trường Brazil"** (thuộc chương 5, Phú dựng; KHÔNG sửa DB1–DB4 của nhóm):
  - xuất lại CSV (`export_powerbi.py`); cập nhật `powerbi/model.md` và `measures.md` (GMV mỗi 1.000 dân, GMV USD, GMV thực, tăng trưởng thực);
  - viết `huong-dan/dashboards/D8.md` theo mẫu DB1–DB4, gồm:
    - bản đồ GMV mỗi 1.000 dân theo bang, drill xuống đô thị lớn;
    - xếp hạng bang theo đầu người so với theo GMV tuyệt đối;
    - đường GMV danh nghĩa so với GMV thực, và GMV USD theo tháng;
    - thẻ KPI;
    - slicer năm / vùng;
    - bảng giá trị kỳ vọng;
  - cột mới thêm vào `dim_geography` và `dim_date` không được làm đổi số của DB1–DB4. Chạy lại bảng giá trị kỳ vọng của DB1–DB4 để chứng minh.

## Bước 6 – Kiểm thử
Thêm vào `sql/90_tests` và `pytest` cho `api_ingest`. Các test cần có:
- **Collector:** chạy lại không nhân đôi.
- **Dữ liệu API:**
  - tỷ giá không thiếu ngày làm việc;
  - IPCA đủ tháng.
- **Ghép đô thị:**
  - mã IBGE hợp lệ;
  - không zip nào bị gán 2 đô thị.
- **Bảng mới:** `fact_state_year` khớp tổng GMV.

## Bước 7 – Tài liệu và bàn giao
- **Handoff:** viết `handoff/2026-11-xx-P9-api.md` theo mẫu, gồm số liệu thật và đoạn nháp cho mục 5.2.
- **Báo cáo:** điền `report/chapters/5-2-thu-thap-api.tex` theo thứ tự bài toán → kiến trúc → triển khai → kết quả.
- **Slide:** điền phần API trong `slides/sections/04-mo-rong.tex`, khoảng 10–15 slide; mỗi bước có minh chứng (output collector, manifest, bảng tỉ lệ khớp).
- **Vấn đáp:** thêm câu hỏi vào `huong-dan/04-cau-hoi-van-dap.md`:
  - vì sao chọn các API này;
  - xử lý tên thành phố lệch thế nào;
  - fuzzy có ghép sai không;
  - API lỗi thì sao;
  - tần suất cập nhật.
- **README:** viết `api_ingest/README.md`, chạy bằng vài lệnh, có bản PowerShell.

## Báo lại cho Phú
- Số bản ghi theo nguồn.
- Tỉ lệ ghép theo tầng.
- Các phát hiện chính có số.
- Danh sách cột và bảng mới.
- Số test đạt.
- CSV nào thay đổi (để tải lại lên Drive).
- Phần tuỳ chọn đã làm.

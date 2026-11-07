# Dữ liệu xuất cho Power BI – cách lấy

Bộ CSV đủ dữ liệu (đến 11/2018) nặng khoảng **79 MB** (> 50 MB) nên **không đưa lên GitHub** (`exports/powerbi/*.csv` nằm trong `.gitignore`).
Cả thư mục `exports/powerbi/` được chia sẻ qua Google Drive:

**Link Google Drive:** _(Phú dán link vào đây sau khi tải thư mục lên)_

Cách dùng:
1. Tải cả thư mục `powerbi` từ link trên về máy (giữ nguyên tên file, không đổi tên).
2. Trong Power BI Desktop chọn nguồn là thư mục đó (hoặc từng file CSV, *File origin* = UTF-8). Danh sách file, cột, khoá nối: `exports/powerbi/README.md` (file này có trong git).
3. Mỗi lần Phú chạy lại pipeline và tải lại thư mục, **tên file không đổi** nên chỉ cần bấm **Refresh** trong Power BI, không phải dựng lại mô hình.

Khi chạy lại pipeline (máy có database): `python scripts/export_powerbi.py` (hoặc `python -m etl.run_pipeline --mode incremental`, bước cuối tự xuất) ghi lại toàn bộ `exports/powerbi/`.

## File mới ở P6 (cần tải bổ sung lên Drive)
Bản xuất P6 gồm **35 file CSV**. 22 file cũ (10 `dim_*`, 6 `fact_*`, `job_run` và 5 file giám sát ETL của P5) **giữ nguyên tên và cột** (nội dung được ghi đè bằng lần xuất mới, kết quả giống P5 vì dữ liệu không đổi). **13 file mới** là các view data mart, tổng 9.7 MB:

| File mới | Số dòng | Dung lượng |
| --- | ---: | ---: |
| v_sales_daily.csv | 614 | 0.05 MB |
| v_sales_category_month.csv | 1,282 | 0.10 MB |
| v_sales_state_month.csv | 558 | 0.04 MB |
| v_category_pareto.csv | 74 | 0.01 MB |
| v_fulfillment_state_month.csv | 565 | 0.04 MB |
| v_status_funnel.csv | 125 | 0.01 MB |
| v_review_vs_delay.csv | 105 | 0.01 MB |
| v_payment_mix_month.csv | 90 | 0.01 MB |
| v_customer_rfm.csv | 94,983 | 8.91 MB |
| v_customer_cohort.csv | 220 | 0.01 MB |
| v_funnel_by_origin_month.csv | 113 | 0.01 MB |
| v_seller_scorecard.csv | 3,095 | 0.56 MB |
| v_seller_by_channel.csv | 7 | 0.00 MB |

Chỉ cần tải 13 file này lên cùng thư mục `powerbi` trên Drive (hoặc tải lại cả thư mục). Cách nạp chúng vào Power BI: `powerbi/model.md`, mục 3 và Phụ lục.

## File mới ở P7 (cần tải bổ sung lên Drive)
Bản xuất hiện có **37 file CSV**. Ngoài 35 file ở P6 (tên và cột không đổi), có **2 file mới** cho bản đồ của dashboard D4:

| File mới | Số dòng | Dung lượng |
| --- | ---: | ---: |
| v_geo_state.csv | 27 | 0.00 MB |
| v_geo_zip.csv | 14,889 | 1.11 MB |

Cả thư mục `powerbi` (37 file) tải lại một lần là đủ. Cách nạp: `powerbi/model.md`, mục 3 (hàm `fnCsv`); bảng rời, đặt `latitude`/`longitude` ở Data category.

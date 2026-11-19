# ETL: tách pipeline lõi (chương 3) và bước API (chương 5) – 2026-11-19

## Đã làm
- Từ P9, mỗi lô của `python -m etl.run_pipeline --with-api` chạy thêm bước API (thu nhận, ghép đô thị, làm giàu `dim_geography`/`dim_date`, `fact_state_year`) và 20 phép kiểm thử API. Số liệu trong `etl_log` vì thế gồm cả hai phần.
- Các bảng ở mục 3.3 của báo cáo (`report/tables/p8_etl_*.tex`, `p8b_etl_*.tex`) và hình `3-3_etl_jobs.png` được sinh lại bằng `python scripts/p8_etl.py`, nay **chỉ tính phần lõi**: bỏ job lớp `api`/`api_ods`, ba job làm giàu (`dw.enrich_dim_geography`, `dw.enrich_dim_date`, `dw.load_fact_state_year`), 20 phép kiểm thử API và 11 cột API thêm vào hai dimension. Thời gian bước API được trừ ra khỏi thời gian lô.
- Kiểm chứng: số dòng, số cột, số test của các bảng lõi **trùng từng số** với bản đã commit trước P9; chỉ cột "Thời gian (giây)" của bảng các đợt nạp đổi (xem dưới).
- Phần API tách riêng ở mục "Tách thời gian" của `handoff/2026-11-14-P8-etl.md` (sinh tự động).
- Đo thêm một lần dựng lại **không có API** trong một database tạm (`olist_core_noapi`; `olist_dw` không bị đụng, không xuất CSV) để có số thời gian lõi không phụ thuộc vào cách trừ. Database tạm đã xoá sau khi đo.

## Số liệu (từ etl_log của hai lần chạy)
**Thời gian mỗi lô (giây).** "Lõi (tách)" là thời gian lô trong `olist_dw` trừ bước API; "Lõi (đo)" là lần dựng lại không API.

| Đợt | Lô (olist_dw) | Có API | Bước API | Lõi (tách) | Lõi (đo, không API) |
| --- | ---: | ---: | ---: | ---: | ---: |
| đầu | 2 | 72,2 | 4,0 | 68,2 | 56,2 |
| 1 | 7 | 27,8 | 4,1 | 23,7 | 22,7 |
| 2 | 12 | 27,8 | 3,2 | 24,6 | 23,5 |
| 3 | 17 | 31,6 | 3,8 | 27,8 | 26,0 |
| 4 | 22 | 29,4 | 3,6 | 25,8 | 26,4 |
| 5 | 27 | 30,1 | 4,1 | 26,0 | 25,0 |
| 6 | 32 | 30,5 | 4,1 | 26,4 | 26,5 |
| 7 | 37 | 32,2 | 4,3 | 27,9 | 27,5 |
| 8 | 42 | 33,6 | 4,3 | 29,3 | 27,1 |
| 9 | 47 | 42,6 | 6,6 | 36,0 | 22,8 |
| 10 | 52 | 26,2 | 4,4 | 21,8 | 22,4 |
| 11 | 57 | 26,3 | 4,3 | 22,0 | 22,3 |

| 11 đợt tăng dần (nhỏ nhất / trung bình / lớn nhất) | Giây |
| --- | --- |
| Có API | 26,2 / 30,7 / 42,6 |
| Bước API | 3,2 / 4,3 / 6,6 |
| Lõi, tách từ `etl_log` | 21,8 / 26,5 / 36,0 |
| Lõi, đo lại không API | 22,3 / 24,7 / 27,5 |

Lưu ý: đợt 9 (lô 47) có thời gian kiểm thử 22,7 giây so với 14–16 giây ở các đợt khác (máy bận lúc chạy), nên cả cột "Có API" lẫn "Lõi (tách)" đều cao ở đợt này; lần đo không API (22,8 giây) không bị ảnh hưởng. Khi cần một khoảng gọn cho tiêu đề slide, dùng **lõi 22–28 giây**.

**Dựng lại toàn bộ (giây).**

| Bước | Có API (`rebuild-report.md`) | Không API (đo lại) |
| --- | ---: | ---: |
| setup_db | 3,3 | 1,4 |
| nạp nguồn ban đầu | 15,3 | 15,7 |
| pipeline full | 73,2 | 57,2 |
| 11 đợt tăng dần | 367,4 | 298,9 |
| pipeline cuối (kiểm thử; có API còn xuất 45 CSV) | 40,8 | 22,8 |
| **Cộng các bước trên** | **500,0** | **396,0** |

- Hai cột cùng điều kiện: bỏ bước xoá database và bước nạp `olist_full` (25,0 giây, chỉ cần cho EDA). Tổng thời gian của lần có API ghi trong `rebuild-report.md` là 540 giây, gồm cả hai bước đó.
- Số cũ **443 giây** (trước P9) gồm nạp `olist_full` và xuất 37 CSV, không so sánh trực tiếp với hai cột trên.
- Chênh lệch 104 giây giữa hai cột: `etl_log` ghi riêng bước API cộng 20 phép kiểm thử cho 13 lô là khoảng 51 giây (46,0 giây job + 13 × 0,4 giây test); phần còn lại là xuất 8 CSV mới và khác biệt tải máy giữa hai lần chạy (cộng thời gian 13 lô `pipeline.*`: 447,9 giây so với 350,2 giây). Vì vậy dùng cột "Không API" làm số lõi, và chỉ đọc cột "Có API" như cận trên.

**Kiểm thử.**

| | Số phép | Đạt |
| --- | ---: | ---: |
| Kho (chương 3) | 136 | 136 |
| Đối chiếu EDA (chỉ báo cáo) | 6 | 6 |
| API (chương 5, `050_api_tests.sql`) | 20 | 20 |
| Tổng ghi vào `dq_check` mỗi lô | 162 | 162 |

(Con số 156 dùng ở các tài liệu P9 là 136 + 20, chưa tính 6 phép EDA.) 20 phép kiểm thử API chạy riêng mất khoảng 0,4 giây (trung vị 5 lần).

## Lỗi tìm thấy khi đo
- Chạy pipeline **không có `--with-api`** từng trượt ở test cuối của `050_api_tests.sql` (`mart_market.v_gmv_per_capita_city`): thiếu điều kiện "chưa nạp API thì đạt" như các phép còn lại. Đã sửa (commit `89fa340`); sau khi sửa, lần dựng lại không API đạt đủ test.

## Việc cho nhóm
- Người 3: cập nhật S78, S82, S105, S110 theo dòng K21 trong `huong-dan/phan-viec/Nguoi-3.md`. Không sửa `slides/sections/02b-*.tex` và `report/chapters/3-3-*.tex` ở phía code; phần chữ ở mục 3.3 (ví dụ "mỗi đợt 21–28 giây", "443 giây") vẫn là số cũ cho tới khi Người 3 sửa.
- Bảng `report/tables/p8b_etl_batches.tex` (cột "Thời gian (giây)") đã sinh lại theo số lõi tách từ `etl_log`; nếu muốn dùng số đo không API thì lấy từ bảng ở trên.

# Kiểm chứng tái lập – chạy lại từ đầu bằng `python scripts/rebuild_all.py --drop` (2026-11-05 20:26)

| Bước | Thời gian (giây) | Kết quả (dòng cuối) |
| --- | ---: | --- |
| drop olist_dw + olist_full | 0.4 | dropped |
| setup_db (schemas, DDL, procedures, views) | 1.8 | Setup done. |
| load_source --initial (olist_dw, to 2017-12-31) | 15.3 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| load_source --full (olist_full) | 24.0 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| run_pipeline --mode full (initial state) | 57.0 | pipeline full trên dữ liệu đến 2017-12-31: 55.9s |
| replay_increments (11 x simulate + incremental) | 276.7 |  11 đợt hằng tháng (01/2018 → 11/2018); sau đợt cuối: 8.000 MQL, 842 deal, 380 seller có đơn, 99.441 đơn, GMV 13.494.400,74 |
| run_pipeline --mode incremental (tests + export_powerbi) | 29.5 | tests: 130/130 đạt, 0 lỗi; đối chiếu EDA 5/5 khớp |

**Tổng thời gian: 413 giây (6.9 phút).** Kết quả: THÀNH CÔNG.

So sánh với trạng thái trước khi xoá: 16/16 bảng dim/fact khớp tín hiệu trước khi xoá (số dòng, tổng tiền, checksum nội dung).

Ghi chú: sau lần dựng lại này thêm 3 test cho view khoảng cách và hàm haversine; chạy lại `python -m etl.run_tests` cho **133/133 đạt** và 5/5 đối chiếu EDA khớp. Tổng kết số dòng (trạng thái cuối, giống trước khi xoá): `handoff/00-TONG-QUAN.md` mục 2–3.

# Kiểm chứng tái lập – chạy lại từ đầu bằng `python scripts/rebuild_all.py --drop` (2026-11-08 13:43)

| Bước | Thời gian (giây) | Kết quả (dòng cuối) |
| --- | ---: | --- |
| drop olist_dw + olist_full | 0.6 | dropped |
| setup_db (schemas, DDL, procedures, views) | 1.8 | Setup done. |
| load_source --initial (olist_dw, to 2017-12-31) | 15.5 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| load_source --full (olist_full) | 24.0 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| run_pipeline --mode full (initial state) | 55.8 | tests: 136/136 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 54.7s |
| replay_increments (11 x simulate + incremental) | 287.1 | 11 đợt hằng tháng (01/2018 → 11/2018); sau đợt cuối: 8,000 MQL, 842 deal, 379 seller có đơn bán được, 99,441 đơn, GMV 13,494,400.74 |
| run_pipeline --mode incremental (tests + export_powerbi) | 30.5 | tests: 136/136 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 29.3s |

**Tổng thời gian: 443 giây (7.4 phút).** Kết quả: THÀNH CÔNG.

So sánh với trạng thái trước khi xoá: 16/16 bảng dim/fact khớp tín hiệu trước khi xoá (số dòng, tổng tiền, checksum nội dung, checksum giá trị khoá thay thế).

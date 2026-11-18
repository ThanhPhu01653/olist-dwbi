# Kiểm chứng tái lập – chạy lại từ đầu bằng `python scripts/rebuild_all.py --drop` (2026-11-18 15:12)

| Bước | Thời gian (giây) | Kết quả (dòng cuối) |
| --- | ---: | --- |
| drop olist_dw + olist_full | 0.5 | dropped |
| setup_db (schemas, DDL, procedures, views) | 3.3 | Setup done. |
| load_source --initial (olist_dw, to 2017-12-31) | 15.3 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| load_source --full (olist_full) | 25.0 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| run_pipeline --mode full (initial state) | 73.2 | tests: 156/156 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 72.2s |
| replay_increments (11 x simulate + incremental) | 367.4 | 11 đợt hằng tháng (01/2018 → 11/2018); sau đợt cuối: 8,000 MQL, 842 deal, 379 seller có đơn bán được, 99,441 đơn, GMV 13,494,400.74 |
| run_pipeline --mode incremental (tests + export_powerbi) | 40.8 | tests: 156/156 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 37.6s |

**Tổng thời gian: 540 giây (9.0 phút).** Kết quả: THÀNH CÔNG.

So sánh với trạng thái trước khi xoá: 16/16 bảng dim/fact khớp tín hiệu trước khi xoá (số dòng, tổng tiền, checksum nội dung, checksum giá trị khoá thay thế).

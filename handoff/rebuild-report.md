# Kiểm chứng tái lập – chạy lại từ đầu bằng `python scripts/rebuild_all.py --drop` (2026-11-08 00:04)

| Bước | Thời gian (giây) | Kết quả (dòng cuối) |
| --- | ---: | --- |
| drop olist_dw + olist_full | 0.6 | dropped |
| setup_db (schemas, DDL, procedures, views) | 2.1 | Setup done. |
| load_source --initial (olist_dw, to 2017-12-31) | 14.8 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| load_source --full (olist_full) | 23.2 | Rejected rows logged in etl_log.rejected_rows: 0 (batch 1) |
| run_pipeline --mode full (initial state) | 53.3 | tests: 136/136 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 52.4s |
| replay_increments (11 x simulate + incremental) | 275.3 | 11 đợt hằng tháng (01/2018 → 11/2018); sau đợt cuối: 8,000 MQL, 842 deal, 379 seller có đơn bán được, 99,441 đơn, GMV 13,494,400.74 |
| run_pipeline --mode incremental (tests + export_powerbi) | 30.1 | tests: 136/136 đạt, 0 lỗi; đối chiếu EDA 6/6 khớp; pipeline 29.2s |

**Tổng thời gian: 407 giây (6.8 phút).** Kết quả: THÀNH CÔNG.

So sánh với trạng thái trước khi xoá: 16/16 bảng dim/fact khớp tín hiệu trước khi xoá (số dòng, tổng tiền, checksum nội dung).

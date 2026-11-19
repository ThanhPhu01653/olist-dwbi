# P10 – Time travel Iceberg (Bước 7)

Sinh bởi `lakehouse/scripts/time_travel.py`; số lấy từ lần chạy thật.

## 1. Lịch sử snapshot của bảng thật `silver.orders` (chỉ đọc)
Bảng có 31 snapshot (mỗi micro-batch của luồng Spark tạo một hoặc hai snapshot khi MERGE). Ba snapshot đại diện:
| snapshot_id | committed_at (UTC) | operation | tổng số dòng ghi trong snapshot |
| --- | --- | --- | --- |
| 2157968849829820024 | 2026-11-19 07:22:00 | append | 307 |
| 5131277747140695887 | 2026-11-19 07:44:57 | overwrite | 49.721 |
| 5387172661905269450 | 2026-11-19 07:59:12 | overwrite | 99.441 |

Đọc lại từng phiên bản cũ bằng `FOR VERSION AS OF` (số đơn tại thời điểm đó, không đụng dữ liệu hiện tại):
| snapshot_id | committed_at (UTC) | số đơn đọc được | giây |
| --- | --- | --- | --- |
| 2157968849829820024 | 2026-11-19 07:22:00 | 307 | 0.04 |
| 5131277747140695887 | 2026-11-19 07:44:57 | 49.721 | 0.08 |
| 5387172661905269450 | 2026-11-19 07:59:12 | 99.441 | 0.07 |

Cũng đọc được theo thời gian: `FOR TIMESTAMP AS OF TIMESTAMP '2026-11-19 07:44:57 UTC'` trả về 46.830 đơn (hiện tại 99.441 đơn).

## 2. Sửa nhầm rồi rollback (trên bản sao `ops.orders_tt`)
Bản sao: 99.441 đơn, 625 đơn ở trạng thái `canceled`; snapshot ban đầu `8427760783211712241`.
Thao tác nhầm: `UPDATE ... SET order_status = 'canceled' WHERE order_status = 'delivered'` → 97.103 đơn `canceled` (snapshot mới `1786134249791103388`).
Phiên bản cũ vẫn còn nguyên: đọc `FOR VERSION AS OF 8427760783211712241` thấy 625 đơn `canceled`.
`CALL iceberg.system.rollback_to_snapshot('ops', 'orders_tt', 8427760783211712241)` mất 0.05 giây (chỉ đổi con trỏ metadata, không chép dữ liệu); sau đó `canceled` = 625, đúng bằng trước khi sửa: **đúng**.
So với bảng gốc `silver.orders` sau rollback: số dòng khác nhau = 0.

## 3. "Đơn này ở trạng thái nào lúc T?" (`silver.order_status_history`, dạng SCD2)
Đơn `00010242fe8c5a6d1ba2dd792cb16214` có 4 phiên bản trạng thái:
| status | valid_from | valid_to | is_current |
| --- | --- | --- | --- |
| created | 2017-09-13 08:59:02.000000 UTC | 2017-09-13 09:45:35.000000 UTC | False |
| approved | 2017-09-13 09:45:35.000000 UTC | 2017-09-19 18:34:16.000000 UTC | False |
| shipped | 2017-09-19 18:34:16.000000 UTC | 2017-09-20 23:43:48.000000 UTC | False |
| delivered | 2017-09-20 23:43:48.000000 UTC |  | True |

Truy vấn `valid_from <= T < valid_to` với T = 2017-09-19 18:34:16 UTC trả về trạng thái `shipped`.

## 4. Tiến hoá lược đồ (trên bản sao)
`ALTER TABLE ... ADD COLUMN note varchar` không ghi lại dữ liệu cũ: cột mới có 0 giá trị khác NULL trên 99.441 dòng (đọc bình thường, file Parquet cũ giữ nguyên).
`DROP COLUMN note` cũng chỉ đổi metadata. Iceberg theo dõi cột bằng ID chứ không bằng tên hay vị trí, nên thêm/bớt cột không làm hỏng các snapshot cũ.

## 5. Thống kê bảng
`silver.orders`: 104 file dữ liệu, 6.7 MiB, 99.441 dòng (file của snapshot hiện tại; các snapshot cũ còn giữ thêm file riêng cho tới khi dọn bằng expire_snapshots).
| column_name | data_size | distinct_values_count | nulls_fraction | row_count | low_value |
| --- | --- | --- | --- | --- | --- |
| order_id | 4778554.0 |  | 0.0 |  |  |
| customer_id | 4841785.0 |  | 0.0 |  |  |
| order_status | 61927.0 |  | 0.0 |  |  |
| order_purchase_timestamp |  |  | 0.0 |  | 2016-09-04 21:15:19.000 UTC |
| order_approved_at |  |  | 0.0016089942780140988 |  | 2016-09-15 12:16:38.000 UTC |
| order_delivered_carrier_date |  |  | 0.017930229985619613 |  | 2016-10-08 10:34:01.000 UTC |

Đã xoá bản sao `ops.orders_tt`; `silver.orders` không bị thay đổi trong suốt phần này.

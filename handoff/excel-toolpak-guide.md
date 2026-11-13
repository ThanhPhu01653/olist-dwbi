# Hướng dẫn Excel Data Analysis ToolPak (cho nhóm)

*Sinh tự động bởi `scripts/eda/excel_export.py` trên database `olist_full`; chạy lại script để cập nhật số liệu.*

Môn học yêu cầu đa dạng công cụ phân tích: ngoài Power BI, dùng Excel Data Analysis ToolPak cho thống kê mô tả, tương quan, histogram.

## File dữ liệu

- `exports/eda_sample.xlsx`, sheet **du_lieu**: 5.000 đơn đã giao (mẫu cố định từ 94.420 đơn đủ điều kiện), 21 cột, **không có ô trống**.
- Cột A–G là chữ / ngày (order_id, purchase_date, purchase_month, customer_state, region, payment_type_main, delay_group).
- **Cột H–U là 14 cột số liên tiếp** (items … review_score) để ToolPak dùng một vùng chọn duy nhất: `H1:U5001` (dòng 1 là tiêu đề).
- Sheet **mo_ta_cot**: ý nghĩa, đơn vị từng cột. Sheet **thong_tin**: nguồn và cách lấy mẫu.

## Bước 0 – Bật ToolPak (làm một lần)

1. Excel → **File → Options → Add-ins**.
2. Ô *Manage* chọn **Excel Add-ins** → bấm **Go…**.
3. Tích **Analysis ToolPak** → **OK**. (Mac: *Tools → Excel Add-ins…* → tích Analysis ToolPak.)
4. Tab **Data** xuất hiện nút **Data Analysis** ở góc phải.

## Bước 1 – Descriptive Statistics (thống kê mô tả)

1. Data → **Data Analysis** → **Descriptive Statistics** → OK.
2. *Input Range*: `du_lieu!$H$1:$U$5001`; *Grouped By*: Columns; tích **Labels in first row**.
3. *Output Range*: chọn ô trống ở sheet mới (ví dụ `thong_ke!$A$1`); tích **Summary statistics** và **Confidence Level for Mean 95%**.
4. OK. Kết quả có 14 cột, mỗi cột gồm Mean, Standard Error, Median, Mode, Standard Deviation, Sample Variance, Kurtosis, Skewness, Range, Min, Max, Sum, Count.
5. **Đối chiếu** (phải khớp):

| Biến | Mean | Median | Standard Deviation | Min | Max | Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| price_total | 138,22 | 85,00 | 204,06 | 4,99 | 4.799,00 | 5.000 |
| freight_total | 22,56 | 17,04 | 18,85 | 0,00 | 271,50 | 5.000 |
| lead_days | 12,43 | 10,29 | 8,86 | 1,02 | 167,60 | 5.000 |
| delay_days | -12,00 | -12,00 | 9,66 | -75,00 | 138,00 | 5.000 |
| review_score | 4,15 | 5,00 | 1,29 | 1,00 | 5,00 | 5.000 |

## Bước 2 – Correlation (tương quan Pearson)

1. Data Analysis → **Correlation** → OK.
2. *Input Range*: `du_lieu!$H$1:$U$5001`; Columns; tích **Labels in first row**; *Output Range*: sheet mới (`tuong_quan!$A$1`).
3. Được ma trận 14 × 14. Tô màu bằng *Home → Conditional Formatting → Color Scales* (xanh dương – trắng – đỏ, cố định −1…1).
4. **Đối chiếu**:

| Cặp biến | Hệ số Pearson (Excel Correlation) |
| --- | ---: |
| delay_days – review_score | -0,237 |
| lead_days – review_score | -0,311 |
| price_total – payment_total | 0,997 |
| freight_total – weight_total_g | 0,648 |
| transit_days – lead_days | 0,920 |

Lưu ý: Excel dùng hệ số **Pearson**, còn hình `figures/3-3-1_correlation_matrix.png` dùng **Spearman** (theo thứ hạng, hợp với dữ liệu lệch phải), nên các hệ số khác nhau. Cả hai cùng cho thấy trễ giao hàng làm điểm review giảm.

## Bước 3 – Histogram (phân phối thời gian giao hàng)

1. Ở sheet mới, ô `A1` gõ `Bin`, rồi `A2:A13` gõ 5, 10, 15, …, 60 (bước 5 ngày).
2. Data Analysis → **Histogram** → OK. *Input Range*: `du_lieu!$R$1:$R$5001` (lead_days); *Bin Range*: `A1:A13`; tích **Labels**.
3. *Output Range*: `C1`; tích **Chart Output** (và **Pareto** nếu muốn). OK.
4. Đổi tên trục: X = “Lead time (ngày)”, Y = “Số đơn”; xoá khoảng cách giữa cột (Format Data Series → Gap Width = 0%).
5. **Đối chiếu** số đơn theo khoảng (khoảng cuối “More” = trên 60 ngày):

| Bin (Excel) | Khoảng lead_days (ngày) | Số đơn |
| --- | --- | ---: |
| 5 | ≤ 5 | 706 |
| 10 | > 5 và ≤ 10 | 1.683 |
| 15 | > 10 và ≤ 15 | 1.253 |
| 20 | > 15 và ≤ 20 | 624 |
| 25 | > 20 và ≤ 25 | 336 |
| 30 | > 25 và ≤ 30 | 183 |
| 35 | > 30 và ≤ 35 | 101 |
| 40 | > 35 và ≤ 40 | 42 |
| 45 | > 40 và ≤ 45 | 38 |
| 50 | > 45 và ≤ 50 | 15 |
| 55 | > 50 và ≤ 55 | 7 |
| 60 | > 55 và ≤ 60 | 4 |
| More | > 60 | 8 |

## Bước 4 (tuỳ chọn) – Regression: điểm review theo số ngày trễ

1. Data Analysis → **Regression** → OK.
2. *Input Y Range*: `du_lieu!$U$1:$U$5001` (review_score); *Input X Range*: `du_lieu!$S$1:$S$5001` (delay_days); tích **Labels**.
3. *Output Range*: sheet mới. OK.
4. **Đối chiếu**: hệ số dốc (X Variable 1) ≈ -0,0317 điểm review cho mỗi ngày trễ thêm; R Square ≈ 0,056.
5. Gợi ý nhận xét: trong mẫu, đơn giao trễ có điểm TB 2,47 so với 4,26 của đơn không trễ (cột `is_late`).

## Gợi ý đưa vào báo cáo (mục 3.3.1 / công cụ phân tích)

- Chụp ảnh bảng Descriptive Statistics, ma trận Correlation (có tô màu) và biểu đồ Histogram; đặt tên `figures/3-3-1_excel_<tên>.png`.
- Nói rõ đây là **mẫu 5.000 đơn**, số liệu toàn bộ nằm ở `handoff/distributions.md` và `handoff/correlations.md`.

<!-- p8:start -->
## Đối chiếu với số tính bằng Python (P8)

Sheet **python_doi_chieu** trong `exports/eda_sample.xlsx` (thêm ở P8, sinh bởi `scripts/eda/p8_describe.py`) chứa số đã tính sẵn bằng Python trên đúng 5.000 dòng của sheet `du_lieu`. Sau khi chạy **Descriptive Statistics** ở Bước 1, đối chiếu từng biến:

| Excel ToolPak | Cột trong python_doi_chieu | Ghi chú |
| --- | --- | --- |
| Mean | Mean | khớp đến chữ số thập phân hiển thị |
| Median | Median | |
| Standard Deviation | Std (n-1) | ToolPak dùng độ lệch chuẩn mẫu (n − 1) |
| Skewness | Skewness | cùng định nghĩa với hàm SKEW của Excel |
| Kurtosis | Kurtosis (excess) | cùng định nghĩa với hàm KURT; bằng 0 với phân phối chuẩn |
| Minimum / Maximum | Min / Max | |

Số khớp với bảng đối chiếu ở Bước 1 (ví dụ price_total: trung bình 138,22, độ lệch chuẩn 204,06).

Bảng thống kê đặc trưng trên **toàn bộ dữ liệu** (không chỉ mẫu) nằm ở `handoff/2026-11-14-P8-eda.md`, mục D4.
<!-- p8:end -->

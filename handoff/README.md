# handoff/ – nhật ký kỹ thuật theo phase

Thư mục này ghi lại từng phase của dự án (đã làm gì, số liệu, đoạn nháp báo cáo, gợi ý slide, SQL tiêu biểu). Dùng để **tra số liệu** và **lấy đoạn nháp** khi viết báo cáo, làm slide. Điểm vào của toàn bộ tài liệu là [`../huong-dan/00-BAT-DAU-TU-DAY.md`](../huong-dan/00-BAT-DAU-TU-DAY.md) (có bản đồ tài liệu).

## 1. Theo phase
| File | Nội dung |
| --- | --- |
| [`00-TONG-QUAN.md`](00-TONG-QUAN.md) | Tổng quan số liệu và phát hiện; bảng "mục báo cáo → file nguồn → hình" |
| [`2026-11-05-P0.md`](2026-11-05-P0.md) | P0: dựng môi trường, mô phỏng hai hệ thống nguồn (`oltp`, `crm`) |
| [`2026-11-05-P1.md`](2026-11-05-P1.md) | P1: profiling và khám phá dữ liệu (EDA) |
| [`2026-11-05-P2.md`](2026-11-05-P2.md) | P2: staging và ODS, quy tắc làm sạch |
| [`2026-11-05-P3.md`](2026-11-05-P3.md) | P3: 10 bảng dimension |
| [`2026-11-05-P4.md`](2026-11-05-P4.md) | P4: 6 bảng fact, kiểm thử, dữ liệu đầu tiên cho Power BI |
| [`2026-11-05-P5.md`](2026-11-05-P5.md) | P5: nạp tăng dần, điều phối pipeline, giám sát ETL |
| [`2026-11-05-P6.md`](2026-11-05-P6.md) | P6: data mart, thao tác OLAP, đặc tả Power BI |
| [`2026-11-05-P7-perf.md`](2026-11-05-P7-perf.md) | P7-A: hiệu năng (benchmark gọn) |
| [`2026-11-05-P7-geo.md`](2026-11-05-P7-geo.md) | P7-B: khoảng cách địa lý bằng haversine SQL (không PostGIS) |
| [`2026-11-14-P8.md`](2026-11-14-P8.md) | P8: sắp lại báo cáo và slide theo barem; bổ sung khảo sát, EDA, kiến trúc, ETL, chiều khái niệm, data model, dashboard |
| [`2026-11-14-P8b.md`](2026-11-14-P8b.md) | P8b: gộp bộ dashboard từ 7 xuống 4 (DB1–DB4); giám sát ETL thành bảng ở mục 3.3 |
| [`2026-11-14-P8c.md`](2026-11-14-P8c.md) | P8c: dự án Power BI gốc dạng PBIP (`powerbi/olist_base/`): mô hình, quan hệ, measure, báo cáo trống |
| [`2026-11-14-P8-eda.md`](2026-11-14-P8-eda.md) | P8-D: ngoại lai, Cramér's V và η, STL, thống kê đặc trưng, từ điển nguồn (số liệu và nhận xét từng hình) |
| [`2026-11-14-P8-source.md`](2026-11-14-P8-source.md), [`-layers`](2026-11-14-P8-layers.md), [`-mapping-summary`](2026-11-14-P8-mapping-summary.md), [`-dimensions`](2026-11-14-P8-dimensions.md), [`-etl`](2026-11-14-P8-etl.md) | P8-C, E: tần suất và taxonomy dữ liệu nguồn, các lớp kiến trúc, tổng hợp mapping, hệ thống chiều khái niệm, ETL |

## 2. Bảng số liệu sinh tự động
Do script sinh từ database; không sửa tay (chạy lại script để cập nhật).
| File | Nội dung | Script |
| --- | --- | --- |
| [`profiling.md`](profiling.md) | Số dòng, kiểu, tỷ lệ NULL của 11 bảng nguồn | `scripts/eda/run_all.py` |
| [`data-quality.md`](data-quality.md) | Đếm từng lỗi dữ liệu nguồn | `scripts/eda/run_all.py` |
| [`distributions.md`](distributions.md) | Phân phối giá, thời gian giao, Pareto | `scripts/eda/run_all.py` |
| [`correlations.md`](correlations.md) | Tương quan; điểm review theo mức trễ | `scripts/eda/run_all.py` |
| [`funnel.md`](funnel.md) | Marketing funnel: MQL → deal → seller có đơn | `scripts/eda/run_all.py` |
| [`design-questions.md`](design-questions.md) | Số liệu cho các câu hỏi thiết kế a–f | `scripts/eda/run_all.py` |
| [`excel-toolpak-guide.md`](excel-toolpak-guide.md) | Hướng dẫn Excel Data Analysis ToolPak trên `exports/eda_sample.xlsx` | `scripts/eda/run_all.py` |
| [`stats.md`](stats.md) | Số dòng mọi bảng của kho, từng dim và fact | `scripts/report_stats.py` |
| [`before-after-samples.md`](before-after-samples.md) | Mẫu bản ghi trước / sau khi làm sạch | `scripts/export_samples.py` |
| [`olap-examples.md`](olap-examples.md) | Kết quả 5 thao tác OLAP | `scripts/run_olap_examples.py` |
| [`benchmark.md`](benchmark.md) | Benchmark oltp và dw, index, materialized view | `scripts/benchmark.py` |
| [`geo-distance.md`](geo-distance.md) | Khoảng cách seller → khách so với phí vận chuyển, lead time | `scripts/geo_analysis.py` |
| [`rebuild-report.md`](rebuild-report.md) | Kết quả dựng lại toàn bộ từ đầu bằng một lệnh | `scripts/rebuild_all.py` |

## 3. Khác
- [`../huong-dan/`](../huong-dan/) – hướng dẫn chung, từ điển dữ liệu, hỏi đáp, hướng dẫn DB1–DB4.
- [`../powerbi/`](../powerbi/) – mô hình Power BI và DAX.
- [`../docs/DW_DESIGN.md`](../docs/DW_DESIGN.md) – đặc tả schema và nhật ký quyết định.

Mẫu một file handoff: *Đã làm* → *Số liệu* → *Hình / file xuất* → *Việc cho nhóm* → *Đoạn nháp cho báo cáo* → *Gợi ý slide* → *SQL / code tiêu biểu* → *Vấn đề còn mở*.

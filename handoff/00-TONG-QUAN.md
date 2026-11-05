# Tổng quan dự án sau P0–P4 (cập nhật 05/11/2026)

*Dành cho cả nhóm, không cần biết lập trình. Mọi số liệu lấy từ truy vấn thật; chi tiết và cách truy ngược nằm ở các file `handoff/2026-11-05-P0.md` … `P4.md`. Hình hiển thị ngay trong trang này khi mở trên GitHub.*

## 1. Dự án đang làm gì
Xây **kho dữ liệu** cho chủ đề **Quản lý đơn hàng** của Olist (sàn kết nối người bán nhỏ với các sàn TMĐT lớn ở Brazil), cộng thêm quy trình **thu hút người bán (seller)** từ bộ dữ liệu Marketing Funnel. Kho dữ liệu giúp trả lời: doanh thu bao nhiêu, đơn đi mất bao lâu ở từng chặng, giao trễ ảnh hưởng đánh giá ra sao, seller đến từ kênh marketing nào thì bán tốt.

Hiện tại hai hệ thống nguồn, các tầng staging, làm sạch (ODS) và kho dữ liệu (10 chiều + 6 bảng fact) đã xây xong và chạy được; đã có bản dữ liệu đầu tiên cho Power BI (xem mục *Tiến độ* ngay bên dưới). Còn lại: nạp tăng dần (P5), data mart/OLAP (P6), mở rộng (P7).

## Tiến độ (cập nhật sau P4)
| Phase | Nội dung | Trạng thái |
| --- | --- | --- |
| P0 | Dựng 2 hệ thống nguồn (`oltp`, `crm`), nạp dữ liệu | Xong |
| P1 | Khám phá dữ liệu (EDA), câu hỏi thiết kế a–f | Xong |
| P2 | Staging và ODS (làm sạch, 42 dòng bị loại có ghi lý do) | Xong |
| P3 | 10 bảng chiều (dimension), SCD2 cho khách | Xong |
| P4 | 6 bảng fact, 112 phép kiểm thử đạt, **bản đầu dữ liệu cho Power BI** | Xong |
| P5 | Nạp tăng dần theo tháng, điều phối, giám sát ETL | Chưa làm |
| P6 | Data mart, ví dụ OLAP, đặc tả Power BI, xuất bản cuối | Chưa làm |
| P7 | Mở rộng: hiệu năng + địa lý | Chưa làm |

**Số dòng hiện có trong `olist_dw`** (dữ liệu nạp ban đầu, đến 31/12/2017; cột phải là số dòng khi nạp đủ toàn bộ dữ liệu, đã kiểm chứng tạm thời):

| Bảng | Nạp ban đầu | Nạp đủ dữ liệu |
| --- | ---: | ---: |
| dim_date | 1.462 | 1.462 |
| dim_geography | 19.108 | 19.178 |
| dim_customer (SCD2) | 44.118 | 96.339 |
| dim_seller | 3.098 | 3.558 |
| dim_product | 32.952 | 32.952 |
| dim_order_status / dim_payment_type / dim_lead_origin | 9 / 6 / 11 | 9 / 6 / 11 |
| dim_lead_profile / dim_sales_rep | 4 / 7 | 503 / 55 |
| fact_order_item | 51.234 | 112.650 |
| fact_order_fulfillment | 45.430 | 99.441 |
| fact_payment | 47.871 | 103.886 |
| fact_review | 45.370 | 99.224 |
| fact_lead_funnel | 2.002 | 8.000 |
| fact_seller_monthly | 13.548 | 36.583 |

(Số dòng dim gồm dòng Unknown key −1. Tổng `price` của fact khớp từng đồng với file CSV nguồn: nạp đủ dữ liệu 13.591.643,70 BRL. Chi tiết: `handoff/2026-11-05-P4.md` và `handoff/stats.md`.)

**File CSV cho Power BI**: thư mục `exports/powerbi/` (17 file, khoảng 34 MB, UTF-8 có BOM); `exports/powerbi/README.md` liệt kê từng file, cột và khoá nối. Đây là bản **đầu tiên** dựa trên dữ liệu đến 31/12/2017; bản đầy đủ (đến 08/2018) sẽ có sau P5 và có thể phải chia sẻ qua Google Drive vì vượt 50 MB.

## 2. Hai hệ thống nguồn và số liệu
| Hệ thống | Nội dung | Số bảng | Số dòng | Giai đoạn |
| --- | --- | ---: | ---: | --- |
| **Bán hàng (OLTP)** | đơn hàng, dòng hàng, thanh toán, đánh giá, khách, seller, sản phẩm, toạ độ địa lý | 9 | 1.550.922 | đơn từ 09/2016 đến 10/2018 |
| **CRM / Marketing** | 8.000 khách tiềm năng (MQL) và 842 thương vụ đã chốt thành seller | 2 | 8.842 | MQL từ 06/2017 đến 05/2018 |
| **Tổng** | 11 file CSV, 121,18 MB | 11 | 1.559.764 | |

- Hai hệ thống **chỉ gặp nhau ở mã người bán** (`seller_id`) và không có khoá ngoại giữa chúng; liên kết được làm trong kho dữ liệu.
- Có hai database: `olist_full` (toàn bộ dữ liệu, dùng để khám phá) và `olist_dw` (chỉ dữ liệu đến 31/12/2017: 1.273.620 dòng; phần còn lại 286.144 dòng sẽ được "đổ thêm" từng tháng để minh hoạ cập nhật tăng dần).
- Quy mô nghiệp vụ: 99.441 đơn, 96.096 khách thật, 3.095 seller, 32.951 sản phẩm thuộc 73 danh mục, tổng GMV (giá trị hàng bán không tính đơn hủy) 13,49 triệu BRL.

## 3. Năm phát hiện đáng chú ý nhất

### 1) Giao trễ làm điểm đánh giá sụp
Đơn giao sớm có điểm review trung bình **4,29**; trễ 1–3 ngày còn **3,29**; trễ 4–7 ngày **2,11**; trễ hơn 7 ngày chỉ **1,70** (79,2% review tiêu cực, so với 9,2% ở đơn giao sớm).

![Điểm review theo mức trễ](../figures/3-3-1_delay_vs_review.png)

### 2) Trễ giao hàng tập trung ở miền Bắc / Đông Bắc, còn ngày dự kiến thì quá rộng rãi
Toàn quốc chỉ **6,8%** đơn trễ và **91,9%** đơn giao sớm hơn dự kiến (trung vị sớm 12 ngày). Nhưng lead time trung vị là **20,2 ngày** ở vùng Norte so với **8,7 ngày** ở Sudeste (gấp 2,3 lần), và bang AL trễ tới **21,4%** đơn.

![Tỷ lệ giao trễ theo bang](../figures/3-3-1_late_rate_by_state.png)

### 3) Funnel marketing chỉ nối được với một phần bán hàng
Trong 842 thương vụ đã chốt, chỉ **380 seller (45,1%)** có đơn hàng trong hệ thống bán hàng; **462 (54,9%)** không có mặt. Nhóm 380 seller này tạo **674.005 BRL = 4,99%** GMV toàn sàn. Tỷ lệ chốt chung là 10,5% (cao nhất ở `paid_search` 12,3%, thấp nhất ở `email` 3,0%).

![Seller của funnel có đơn hàng](../figures/3-3-1_funnel_seller_overlap.png)

### 4) Quy luật 80/20 rất rõ ở danh mục, và seller thì phân tán
**18/74 danh mục (24,3%)** tạo 80% GMV (đứng đầu `health_beauty`, 9,3%). **540/3.053 seller (17,7%)** tạo 80% GMV, nhưng 5 seller lớn nhất chỉ chiếm 7,7%, tức không phụ thuộc vào vài seller.

![Pareto GMV theo danh mục](../figures/3-3-1_pareto_category.png)

### 5) Bảng toạ độ địa lý "bẩn" nhất: 1 triệu dòng nhưng chỉ 19.015 mã bưu chính
**93,5%** mã bưu chính có nhiều toạ độ khác nhau, **26,2%** dòng trùng hoàn toàn, **7,3%** tên thành phố lệch dấu (ví dụ "são paulo" 24.918 dòng). Tổng cộng đo được **45 loại lỗi** có ít nhất một dòng bị ảnh hưởng; ODS phải xử lý hết, không xoá dữ liệu.

![Các lỗi dữ liệu đo được](../figures/3-3-1_data_quality.png)

Ngoài ra: dữ liệu đơn hàng dùng được là **01/2017–08/2018** (99,6% số đơn; 2016 chỉ 329 đơn, 09–10/2018 chỉ 20 đơn); mã bưu chính trong bản dữ liệu này **không** bị mất số 0 đầu như dự đoán ban đầu.

## 4. Danh sách hình (thư mục `figures/`)
| Hình | Mô tả | Mục báo cáo |
| --- | --- | --- |
| `3-2-4_erd_oltp.png` | ERD hai hệ thống nguồn (**chưa có**, cả nhóm tạo từ `docs/erd_oltp.mmd` bằng mermaid.live) | 3.2.4 |
| `3-3-1_null_heatmap.png` | Tỷ lệ ô rỗng của mọi cột | 3.3.1 |
| `3-3-1_data_quality.png` | Các lỗi dữ liệu đo được, xếp theo tỷ lệ | 3.3.1 |
| `3-3-1_distributions_numeric.png` | Histogram + boxplot: giá, phí vận chuyển, thanh toán, lead time, delay_days | 3.3.1 |
| `3-3-1_pareto_category.png`, `3-3-1_pareto_seller.png` | Quy luật 80/20 theo danh mục và theo seller | 3.3.1 |
| `3-3-1_orders_per_month.png` | Số đơn theo tháng (2016 thưa, 09–10/2018 trống) | 3.3.1 |
| `3-3-1_review_score.png` | Phân bố điểm đánh giá | 3.3.1 |
| `3-3-1_correlation_matrix.png` | Ma trận tương quan Spearman | 3.3.1 |
| `3-3-1_delay_vs_review.png` | Điểm review theo mức trễ | 3.3.1 |
| `3-3-1_freight_vs_weight.png` | Phí vận chuyển theo cân nặng | 3.3.1 |
| `3-3-1_lead_time_by_region.png`, `3-3-1_late_rate_by_state.png` | Lead time theo vùng; tỷ lệ trễ theo bang | 3.3.1 |
| `3-3-1_funnel_mql_by_month.png`, `3-3-1_funnel_win_rate_by_origin.png` | MQL theo tháng và kênh; tỷ lệ chốt theo kênh | 3.3.1 |
| `3-3-1_funnel_days_to_close.png`, `3-3-1_funnel_business_segment.png` | Thời gian chốt deal; 10 phân khúc nhiều deal nhất | 3.3.1 |
| `3-3-1_funnel_seller_overlap.png` | Seller của funnel có / không có đơn hàng | 3.3.1 |

Chi tiết số liệu từng hình: `handoff/profiling.md`, `data-quality.md`, `distributions.md`, `correlations.md`, `funnel.md`. Dữ liệu cho Excel: `exports/eda_sample.xlsx`.

## 5. Câu hỏi thiết kế cần chốt ngày 12/11 (kèm khuyến nghị)
Chi tiết, các phương án và bảng số liệu ở `handoff/design-questions.md`.

| Câu | Vấn đề | Số liệu chính | Khuyến nghị |
| --- | --- | --- | --- |
| a | `dim_customer` dùng SCD2 hay SCD1? | chỉ 250/96.096 khách (0,26%) đổi mã bưu chính; SCD2 thêm 256 dòng (+0,27%) | **Giữ SCD2** – rẻ, và là ví dụ SCD thật để trình bày |
| b | Độ sâu dashboard D6 (thu hút seller) | 380/842 deal có đơn; GMV 4,99% sàn | **2 trang**: funnel theo kênh + seller từ funnel; gộp kênh, luôn ghi cỡ mẫu |
| c | `fact_seller_monthly` dày đặc hay thưa? | dày đặc 36.583 dòng, thưa 16.441 dòng | **Dày đặc** (đo được seller ngừng bán, dữ liệu vẫn rất nhỏ) |
| d | Bảng nhóm ngành hàng | 73 danh mục → 12 nhóm; 2 danh mục thiếu bản dịch (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) | **Dùng 12 nhóm đề xuất** (`docs/category_group_draft.csv`); nhóm duyệt các mục tranh luận (`relogios_presentes`, `cool_stuff`, `pet_shop`…) |
| e | Mã bưu chính của khách/seller thiếu trong bảng toạ độ | 157 mã của khách + 7 mã của seller; chỉ 0,28% số đơn bị ảnh hưởng | **Tạo dòng địa lý từ thành phố/bang, toạ độ để trống** |
| f | Mốc tách dữ liệu nạp ban đầu (đang chờ review) | mốc 2017-12-31: 45.430 đơn, 2.002 MQL, 3 deal, còn 8 đợt cập nhật | **Giữ 2017-12-31** |

## 6. Việc tiếp theo của nhóm (chưa gán người)
Cả nhóm cùng làm dashboard Power BI, báo cáo và slide từ các file trong `handoff/`. Phân công cụ thể sẽ làm sau.

| Việc | Nguồn | Hạn gợi ý |
| --- | --- | --- |
| Dự họp chốt thiết kế ngày 12/11 với bảng câu hỏi ở mục 5 | `design-questions.md` | 12/11 |
| Vẽ các sơ đồ (ERD nguồn, hệ thống chiều, data model logic/vật lý, constellation) bằng draw.io | `docs/*.mmd`, mục "Việc cho nhóm" trong từng file phase | trước 21/11 |
| Nạp CSV vào Power BI, tạo quan hệ và phân cấp | `exports/powerbi/README.md`, `2026-11-05-P4.md` | từ 18/11 |
| Chạy Excel Data Analysis ToolPak, chụp ảnh kết quả | `excel-toolpak-guide.md`, `exports/eda_sample.xlsx` | trước 21/11 |
| Viết các mục báo cáo 3.2.3, 3.2.4, 3.3.1, 3.3.3, 3.3.4, 3.4.2–3.4.3 từ các đoạn nháp | `2026-11-05-P0.md` … `P4.md` | trước báo cáo tuần 12 (30/11–6/12) |
| Dựng slide theo "Gợi ý slide" trong từng file phase | `2026-11-05-P0.md` … `P4.md` | trước báo cáo tuần 12 |
| Kiểm tra ngẫu nhiên số liệu trong handoff | mọi file | liên tục |

## 7. Danh mục file trong `handoff/`
| File | Nội dung |
| --- | --- |
| `00-TONG-QUAN.md` | trang này |
| `2026-11-05-P0.md` | dựng 2 hệ thống nguồn: số bảng, số dòng, dung lượng, đoạn nháp 3.2.3 và 3.2.4 |
| `2026-11-05-P1.md` | EDA: mô tả từng hình, đoạn nháp 3.3.1, gợi ý slide |
| `2026-11-05-P2.md` | staging và ODS: quy tắc làm sạch, đối soát số dòng |
| `2026-11-05-P3.md` | 10 bảng chiều: grain, phân cấp, SCD |
| `2026-11-05-P4.md` | 6 bảng fact, kiểm thử, hướng dẫn nạp CSV vào Power BI |
| `before-after-samples.md` | mẫu dữ liệu trước/sau làm sạch |
| `profiling.md`, `data-quality.md`, `distributions.md`, `correlations.md`, `funnel.md` | bảng số liệu chi tiết của EDA (sinh tự động) |
| `design-questions.md` | câu hỏi thiết kế a–f kèm số liệu, phương án, khuyến nghị |
| `excel-toolpak-guide.md` | hướng dẫn Excel ToolPak |
| `stats.md` | số dòng mọi bảng, các chiều (phân cấp, dòng mẫu), các fact (measure, tổng) |

Ngoài `handoff/`: `docs/mapping_oltp_olap.md` (ánh xạ cột nguồn → đích), `docs/erd_dw.mmd`, `docs/erd_dw_marts.mmd` (sơ đồ kho, dán vào mermaid.live), `exports/powerbi/` (dữ liệu cho Power BI).

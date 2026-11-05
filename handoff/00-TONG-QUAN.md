# Tổng quan dự án sau P0–P1 (cập nhật 05/11/2026)

*Dành cho cả nhóm, không cần biết lập trình. Mọi số liệu lấy từ truy vấn thật; chi tiết và cách truy ngược nằm ở `handoff/2026-11-05-P0.md` và `handoff/2026-11-05-P1.md`. Hình hiển thị ngay trong trang này khi mở trên GitHub.*

## 1. Dự án đang làm gì
Xây **kho dữ liệu** cho chủ đề **Quản lý đơn hàng** của Olist (sàn kết nối người bán nhỏ với các sàn TMĐT lớn ở Brazil), cộng thêm quy trình **thu hút người bán (seller)** từ bộ dữ liệu Marketing Funnel. Kho dữ liệu giúp trả lời: doanh thu bao nhiêu, đơn đi mất bao lâu ở từng chặng, giao trễ ảnh hưởng đánh giá ra sao, seller đến từ kênh marketing nào thì bán tốt.

Hiện tại hai hệ thống nguồn đã dựng xong và đã nạp dữ liệu; dữ liệu đã được khám phá kỹ. Chưa xây các tầng làm sạch (ODS) và kho (DW).

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
| `3-2-4_erd_oltp.png` | ERD hai hệ thống nguồn (**chưa có**, KT2 tạo từ `docs/erd_oltp.mmd`) | 3.2.4 |
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

## 6. Việc tiếp theo của từng người
| Ai | Việc | Hạn gợi ý |
| --- | --- | --- |
| **KT1 (Phú)** | Sau buổi chốt 12/11: cập nhật `docs/DW_DESIGN.md` theo quyết định; làm P2 (staging + ODS, 14/11), P3 (dimension, 16/11), P4 (fact + kiểm thử, xuất bản đầu cho Power BI, 18/11) | 12/11 → 18/11 |
| **KT2** | (1) Tạo `figures/3-2-4_erd_oltp.png` từ `docs/erd_oltp.mmd` trên mermaid.live rồi vẽ lại bằng draw.io, gạch chân các cột sẽ dùng sang OLAP; (2) đọc `design-questions.md` và duyệt bảng nhóm ngành hàng; (3) lập source-to-target mapping dựa trên bảng lỗi trong `data-quality.md`; (4) kiểm tra ngẫu nhiên số liệu trong handoff | trước 12/11 |
| **KT3** | (1) Chạy Excel Data Analysis ToolPak theo `handoff/excel-toolpak-guide.md` trên `exports/eda_sample.xlsx`, chụp ảnh kết quả; (2) chọn KPI và bộ lọc cho dashboard dựa trên các phát hiện 1–3 (lọc 01/2017–08/2018, nhóm trễ, vùng/bang, nhóm kênh); (3) định cỡ trang D6 theo câu b; (4) chuẩn bị dựng Power BI khi có dữ liệu xuất ngày 18/11 | 12/11 → 18/11 |
| **VB1** | Viết mục 3.2.3 và 3.2.4 (từ `2026-11-05-P0.md`), mục 3.3.1 (từ đoạn nháp trong `2026-11-05-P1.md`) | trước báo cáo tuần 12 (30/11–6/12) |
| **VB2** | Dựng 8–10 slide EDA theo gợi ý trong `2026-11-05-P1.md` và 3 slide về hệ thống nguồn theo `2026-11-05-P0.md` | trước báo cáo tuần 12 |
| **Cả nhóm** | Dự họp chốt thiết kế ngày 12/11 với bảng câu hỏi ở mục 5 | 12/11 |

## 7. Danh mục file trong `handoff/`
| File | Nội dung |
| --- | --- |
| `00-TONG-QUAN.md` | trang này |
| `2026-11-05-P0.md` | dựng 2 hệ thống nguồn: số bảng, số dòng, dung lượng, đoạn nháp 3.2.3 và 3.2.4 |
| `2026-11-05-P1.md` | EDA: mô tả từng hình, đoạn nháp 3.3.1, gợi ý slide |
| `profiling.md`, `data-quality.md`, `distributions.md`, `correlations.md`, `funnel.md` | bảng số liệu chi tiết của EDA (sinh tự động) |
| `design-questions.md` | câu hỏi thiết kế a–f kèm số liệu, phương án, khuyến nghị |
| `excel-toolpak-guide.md` | hướng dẫn Excel ToolPak cho KT3 |
| `stats.md` | số dòng, số cột, dung lượng các bảng nguồn |

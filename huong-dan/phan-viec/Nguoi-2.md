# Người 2 – Dữ liệu nguồn, ERD OLTP, khám phá dữ liệu và dashboard DB2

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io): [`README.md`](README.md). File này chỉ nói phần của Người 2.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | **2.4 Dữ liệu nguồn** · **2.5 ERD OLTP** · **3.1 Khám phá dữ liệu** |
| File slide | `slides/sections/01b-du-lieu-nguon-erd.tex` (2.4–2.5) và `slides/sections/02a-kham-pha.tex` (3.1) |
| Sơ đồ draw.io | `2-4_data_taxonomy`, `2-4_data_flow_hien_trang`, `2-4_data_flow_de_xuat`, `2-5_erd_oltp_gach_chan`, `2-5_data_flow_oltp_olap` |
| Dashboard | **DB2 Giao hàng và trải nghiệm khách** (vận hành + thống kê, có Key Influencers) |
| Việc riêng | chạy Excel ToolPak trên `eda_sample.xlsx`, chụp ảnh đối chiếu với sheet `python_doi_chieu` |
| Thuyết trình | khảo sát 2.4–2.5 và khám phá dữ liệu; khoảng **8 slide nói** (điều chỉnh theo thời lượng chung của nhóm) |
| Báo cáo (giai đoạn 2) | `2-4-du-lieu-nguon.tex`, `2-5-erd-oltp.tex`, `3-1-kham-pha.tex` |

## 2. Barem chấm gì ở phần này

Các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu của thầy; dòng đỏ là chỗ nhóm khác bị trừ điểm):

**Nguồn dữ liệu**
- Quy mô dữ liệu (dung lượng, số dòng).
- Data flow của các hệ thống CNTT: **trên mũi tên là các thông tin chứ không phải hành động** (ví dụ sai: "lưu đánh giá đơn hàng").
- Tần suất cập nhật dữ liệu mới (dạng biểu đồ theo thời gian) → đề xuất lựa chọn công nghệ xử lý.
- Cây phân loại dữ liệu (data taxonomy) **có ví dụ**.

**ERD OLTP / mô hình dữ liệu nguồn**
- Trình bày: bố cục.
- Màu sắc phân loại, **gạch chân các trường quan trọng** để xây dựng data model đa chiều.

**Data exploration**
- Biểu đồ **đa dạng**; bình luận phân tích các biểu đồ (tóm tắt thông tin trên slide).
- Đánh giá chất lượng dữ liệu.
- Xác định phân phối (histogram, Pareto chart).
- Thống kê đặc trưng (ví dụ Data Analysis Tool của Excel).
- Phân tích tương quan (ví dụ scatter chart); **công thức phân tích tương quan với giá trị rời rạc** phải rõ ràng.
- Phân tích khuynh hướng, mùa vụ.

**Dashboard (liên quan DB2):** phân tích theo dòng thời gian; drill-through và tooltip để phân tích chi tiết; định dạng có điều kiện cảnh báo bằng DAX.

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Hệ thống / quy mô dữ liệu (slide 23–36) | 4,5 | thông tin chung, quy mô từng bảng; biểu đồ tần suất và khối lượng cập nhật, công nghệ đề xuất theo tần suất; taxonomy master / transaction / interaction / reference có ví dụ giá trị thật; data flow hiện trạng và đề xuất, danh mục các luồng, bảng các lớp; đánh giá chất lượng sơ bộ | đã có tần suất, taxonomy, data flow (bản nháp). **Cần làm:** trang danh mục luồng; trang đánh giá chất lượng sơ bộ; vẽ lại bằng draw.io |
| ERD OLTP (slide 37–41) | 5 | ERD vật lý; bảng các quan hệ; gạch chân cột dùng sang OLAP; tổng hợp mapping; data flow OLTP → OLAP | đã có ERD gạch chân, mapping 65/71 cột, data flow OLTP → OLAP. **Cần làm:** bảng các quan hệ (bảng cha → bảng con, khoá, bội số); vẽ lại |
| Data Exploration (slide 43–105) | 4 | 6 bước: chất lượng (lỗi chia 3 nhóm, ngoại lai, dư thừa, toàn vẹn tham chiếu); từ điển dữ liệu; phân bố và Pareto; thống kê đặc trưng bằng Excel và R đối chiếu Python; tương quan fact–fact / dim–fact / dim–dim; khuynh hướng, mùa vụ có STL | đã có đủ 6 bước, ngoại lai IQR + Isolation Forest, Cramér's V và η, STL, file ToolPak. **Cần làm hơn nhóm 6** (nhóm 6 mất điểm dù có 63 slide): mỗi biểu đồ một câu nhận xét; công thức rõ cho biến rời rạc; số ngoại lai theo từng biến và số dòng không trùng; ảnh đối chiếu ToolPak với Python |

Không được chép câu chữ, số liệu hay hình của nhóm 6.

## 3. Kiến thức cần nắm

**Quy mô và tần suất cập nhật (2.4).** Dữ liệu nguồn: 11 bảng, 121,18 MB, 1.559.764 dòng; hệ thống bán hàng `oltp` (9 bảng, 1.550.922 dòng) và hệ thống marketing `crm` (2 bảng, 8.842 dòng). Bảng toạ độ `geolocation` chiếm 64% số dòng (1.000.163) nhưng chỉ đại diện 19.015 mã bưu chính. Tần suất cập nhật quyết định công nghệ xử lý: đơn hàng trung bình 163 đơn/ngày, đỉnh 1.176 đơn ngày Black Friday 24/11/2017 (gấp 7,2 lần trung bình); khối lượng nhỏ nên lô hằng ngày bằng procedure PostgreSQL là đủ; luồng thời gian thực (CDC + Kafka) chỉ cần nếu đội sales muốn phản hồi nhanh với MQL (đưa vào chương 5). Bảng chi tiết từng bảng: `handoff/2026-11-14-P8-source.md`.

**Data taxonomy (cây phân loại dữ liệu).** Chia 11 bảng thành 4 nhóm: *dữ liệu chủ* (master: customers, sellers, products), *giao dịch* (orders, order_items, order_payments), *tương tác* (order_reviews, mql, closed_deals), *tham chiếu* (geolocation, product_category_name_translation). Phải kèm ví dụ giá trị thật của từng nhóm.

**Data flow ở mức hệ thống CNTT.** Sơ đồ các hệ thống và thông tin truyền giữa chúng: **mũi tên ghi thông tin được truyền** ("thông tin đơn", "trạng thái giao", "điểm đánh giá", "lead"), **không ghi hành động** ("lưu đánh giá"). Hiện trạng: hai hệ thống bán hàng và CRM tách rời, chỉ gặp nhau ở `seller_id`. Đề xuất: nguồn → staging → ODS → kho → mart → BI, có nhật ký ETL giám sát. Hai sơ đồ phải khác nhau rõ.

**ERD OLTP và gạch chân.** ERD là sơ đồ bảng và khoá. Cột nào của nguồn được dùng sang kho (OLAP) thì **gạch chân**: 65 trong 71 cột nguồn được gạch chân; bảng `oltp.geolocation` còn 5/6 cột (bỏ `id`). Màu theo nhóm dữ liệu (master, giao dịch, tương tác, tham chiếu). Bảng mapping nguồn → đích → phép biến đổi: `docs/mapping_oltp_olap.md`.

**Chất lượng dữ liệu.** Khám phá đo được **45 loại lỗi** (chia ba nhóm: khoá và định dạng, thiếu, logic) và nhiều tỷ lệ rỗng: `review_comment_title` rỗng 88,34%, `review_comment_message` 58,70%, `order_delivered_customer_date` rỗng 2,98%. Bảng toạ độ bẩn nhất: 93,5% mã bưu chính có nhiều toạ độ khác nhau, 26,2% dòng trùng hoàn toàn. Xử lý nằm ở tầng ODS (mục 3.3 của Người 3): không xoá âm thầm, mọi dòng bị loại có lý do.

**Phân phối và Pareto.** Giá, phí vận chuyển, lead time đều lệch phải (đuôi phải dài). **Pareto 80/20**: sắp mục theo giá trị giảm dần, cộng dồn tỷ lệ, xem bao nhiêu mục tạo 80%. Danh mục: **18/74 danh mục (24,3%) tạo 80% GMV**, dẫn đầu `health_beauty` 9,3%; seller phân tán hơn: 540 seller tạo 80% GMV, 5 seller lớn nhất chỉ 7,7%.

**Ngoại lai.** *IQR*: một giá trị là ngoại lai nếu ngoài khoảng [Q1 − 1,5·IQR, Q3 + 1,5·IQR] (IQR = Q3 − Q1, khoảng giữa của 50% dữ liệu). *Isolation Forest*: rừng cây cô lập điểm bằng cách chia ngẫu nhiên; điểm bị cô lập sau ít lần chia là ngoại lai (nhóm dùng `contamination = 0,05`, `random_state = 42`, mô hình một chiều cho từng biến). Trên 5 biến (giá, phí vận chuyển, cân nặng, lead time, số ngày trễ): IQR 45.568, Isolation Forest 26.212, **giao nhau 24.213** (cộng các biến, có thể trùng dòng). Ví dụ: 12.134 dòng có phí vận chuyển ngoại lai, cân nặng trung vị 5.700 g so với 700 g của toàn bộ. **Nhóm giữ toàn bộ ngoại lai** vì đó là ngoại lai hợp lệ (hàng đắt, hàng nặng, giao xa, giao chậm thật); loại đi sẽ làm sai GMV và che mất vấn đề giao hàng. Chi tiết: `handoff/2026-11-14-P8-eda.md` mục D1.

**Tương quan cho biến rời rạc: Cramér's V và η.**
- *Cramér's V* đo liên hệ giữa **hai biến phân loại** từ bảng chéo: $V = \sqrt{\varphi^2 / \min(r-1, k-1)}$ với $\varphi^2 = \chi^2/n$ ($r$ hàng, $k$ cột, $n$ quan sát); nhóm dùng hiệu chỉnh Bergsma để bớt chệch khi mẫu có nhiều nhóm. V từ 0 (độc lập) đến 1 (phụ thuộc hoàn toàn). Ví dụ: giao trễ và nhóm điểm review có **V = 0,403**, lớn nhất trong các cặp.
- *Tỉ số tương quan η* đo liên hệ giữa **một biến phân loại và một biến số**: $\eta = \sqrt{SS_{giữa\ nhóm} / SS_{tổng}}$. Ví dụ: điểm review theo cờ giao trễ có **η = 0,392**.
- *Pearson hoặc Spearman* dùng cho hai biến số (ví dụ giá và phí vận chuyển, Spearman 0,43). Công thức đầy đủ: `handoff/2026-11-14-P8-eda.md` mục D2.

**Khuynh hướng và mùa vụ (STL).** STL tách chuỗi thời gian thành xu hướng $T_t$, mùa vụ $S_t$ và phần dư $R_t$: $y_t = T_t + S_t + R_t$. Độ mạnh xu hướng $F_T = \max(0, 1 - \mathrm{Var}(R)/\mathrm{Var}(T+R))$ và mùa vụ $F_S = \max(0, 1 - \mathrm{Var}(R)/\mathrm{Var}(S+R))$. Số đơn theo ngày (chu kỳ 7 ngày): xu hướng mạnh 0,73, mùa vụ tuần 0,22. Dữ liệu chưa đủ hai năm nên **không kết luận mùa vụ theo năm**.

**Thống kê đặc trưng và đối chiếu công cụ.** Thống kê mô tả (trung bình, trung vị, độ lệch chuẩn, độ lệch phân phối, độ nhọn) tính bằng Python và đối chiếu với Excel Data Analysis ToolPak trên cùng mẫu 5.000 đơn đã giao; hai công cụ phải cho cùng số (ví dụ `price_total`: trung bình 138,22, trung vị 85,00, độ lệch chuẩn 204,06). Đây là yêu cầu "đa dạng công cụ" của môn.

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn | Dùng ở |
| --- | --- | --- | --- |
| Quy mô nguồn | 11 bảng, 121,18 MB, 1.559.764 dòng; oltp 1.550.922, crm 8.842 | `handoff/profiling.md`; `stats.md` | S33 |
| Tần suất cập nhật | 163 đơn/ngày; đỉnh 1.176 (24/11/2017); nạp ban đầu 45.430 đơn rồi 11 đợt hằng tháng | `handoff/2026-11-14-P8-source.md` | S37, S127 |
| Taxonomy | 4 nhóm, 11 bảng | `handoff/2026-11-14-P8-source.md` mục 2 | S128 |
| Mapping | 65/71 cột đi sang OLAP | `handoff/2026-11-14-P8-mapping-summary.md` | S131 |
| Lỗi dữ liệu | 45 loại lỗi; tỷ lệ rỗng từng cột | `handoff/data-quality.md`, `profiling.md` | S38, S39 |
| Phân bố, Pareto | 18/74 danh mục tạo 80% GMV; 540 seller tạo 80% | `handoff/distributions.md` | S43, S44 |
| Tương quan | Cramér's V 0,403; η 0,392 | `handoff/2026-11-14-P8-eda.md` mục D2 | S134 |
| Ngoại lai | 24.213 (giao nhau) | `handoff/2026-11-14-P8-eda.md` mục D1 | S133 |
| STL | xu hướng 0,73; mùa vụ tuần 0,22 | `handoff/2026-11-14-P8-eda.md` mục D3 | S135 |
| Từ điển nguồn | mô tả cột 11 bảng | `huong-dan/06-tu-dien-du-lieu-nguon.md` | slide từ điển |
| ToolPak | file mẫu 5.000 đơn, sheet `du_lieu`, `mo_ta_cot`, `thong_tin`, `python_doi_chieu` | `exports/eda_sample.xlsx`; `handoff/excel-toolpak-guide.md` | slide đối chiếu |

Hình: `figures/2-4_*.png` (4 hình), `2-5_*.png` (2 hình), `3-1_*.png` (10 hình mới của P8), `3-3-1_*.png` (17 hình EDA), `3-4-3_before_after_geolocation.png`, `3-5-2_distance_vs_*.png`.

## 5. Danh sách slide đề xuất

**Các slide đang có** (bảng do script đọc từ file `.tex`):

<!-- SLIDES:01b-du-lieu-nguon-erd.tex,02a-kham-pha.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 32 | Phạm vi: dữ liệu 01/2017–08/2018 chiếm 99,6% số đơn nên được dùng cho xu hướng | 2016 chỉ 329 đơn; 09–10/2018 chỉ 20 đơn | `3-3-1_orders_per_month.png` | đã có |
| 2 | 33 | Hai hệ thống nguồn có 11 bảng, 121 MB và 1.559.764 dòng | oltp 9 bảng 1.550.922 dòng; crm 2 bảng 8.842 dòng | bảng | đã có |
| 3 | 34 | Bảng toạ độ chiếm 64% số dòng nhưng chỉ đại diện 19.015 mã bưu chính | 1.000.163 dòng geolocation | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng nguồn (làm nổi dòng geolocation) |
| 4 | 37 | Luồng dữ liệu và tần suất cập nhật: nạp ban đầu 45.430 đơn rồi 11 đợt hằng tháng | Tổng 286.144 bản ghi mới qua 11 đợt | `3-4-1_pipeline.png` | đã có |
| 5 | 127 | Trung bình 163 đơn mỗi ngày, đỉnh 1.176 đơn ngày Black Friday: lô hằng ngày là đủ | Cửa sổ 01/2017–08/2018: 163 đơn, 185 dòng hàng, 13 MQL, 1,3 deal mỗi ngày; Bảng tần suất đề xuất công nghệ: lô hằng ngày bằng procedure PostgreSQL; gầ | `2-4_tan_suat_cap_nhat.png` | đã có |
| 6 | 128 | Cây phân loại dữ liệu chia 11 bảng thành 4 nhóm: chủ, giao dịch, tương tác, tham chiếu | Mỗi bảng kèm hai cột tiêu biểu và giá trị thật; Phân loại thêm theo kiểu dữ liệu, độ nhạy cảm (định danh, vị trí) và tính biến động | `2-4_data_taxonomy.png` | đã có |
| 7 | 129 | Data flow hiện trạng: mũi tên ghi thông tin được truyền, hai hệ thống nguồn tách rời | Thông tin đơn, trạng thái giao, thanh toán, điểm đánh giá, lead; Marketing funnel (SDR, SR) tách khỏi hệ thống bán hàng | `2-4_data_flow_hien_trang.png` | đã có |
| 8 | 130 | Data flow đề xuất: nguồn, staging, ODS, kho, mart và BI, có nhật ký ETL giám sát | Bảng lớp, thành phần, công nghệ, tần suất, ghi chú ở báo cáo; Điều phối bằng một lệnh Python, biến đổi bằng PL/pgSQL | `2-4_data_flow_de_xuat.png` | đã có |
| 9 | 35 | ERD hệ thống bán hàng: chín bảng nối quanh đơn hàng | orders → items, payments, reviews; customers, sellers, products | `3-2-4_erd_oltp.png` | đã có |
| 10 | 36 | Các cột được gạch chân trên ERD là cột đi sang kho, kèm ghi chú mapping | Ví dụ: order_purchase_timestamp → purchase_date_key, price → price | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: ERD đã gạch chân (vẽ lại) |
| 11 | 131 | ERD tô màu theo nhóm dữ liệu: 65 trong 71 cột nguồn được gạch chân vì đi sang OLAP | Gạch chân suy ra từ bảng mapping nguồn → ODS → kho; 6 cột không dùng: geolocation.id, 3 thuộc tính sản phẩm, 2 thuộc tính khai báo của deal | `2-5_erd_oltp_gach_chan.png` | đã có |
| 12 | 132 | Luồng OLTP sang OLAP cho thấy bảng nguồn nào nuôi dimension nào và fact nào | Bảng tổng hợp mapping theo bảng nguồn ở báo cáo mục 2.5; Mapping đầy đủ từng cột ở Phụ lục C | `2-5_data_flow_oltp_olap.png` | đã có |
| 13 | 38 | Khám phá dữ liệu đo được 45 loại lỗi cần xử lý ở ODS | Cột thiếu, mốc thời gian sai thứ tự, tên thành phố lệch dấu, trùng lặp | `3-3-1_data_quality.png` | đã có |
| 14 | 39 | Tỷ lệ ô rỗng cho thấy cột nào cần điền unknown | Cột review và ngày giao có nhiều ô rỗng hợp lệ | `3-3-1_null_heatmap.png` | đã có |
| 15 | 40 | Bảng toạ độ bẩn nhất: 93,5% mã bưu chính có nhiều toạ độ, 26,2% dòng trùng hoàn toàn | 7,3% tên thành phố lệch dấu; 42 điểm ngoài lãnh thổ Brazil | `3-4-3_before_after_geolocation.png` | đã có |
| 16 | 41 | Phân bố giá, phí vận chuyển và lead time đều lệch phải | Nhiều giá trị lớn bất thường ở phí vận chuyển | `3-3-1_distributions_numeric.png` | đã có |
| 17 | 42 | Dữ liệu đơn dùng được là 01/2017–08/2018, hai đầu rất thưa | 2016 chỉ 329 đơn; 09–10/2018 chỉ 20 đơn | `3-3-1_orders_per_month.png` | đã có |
| 18 | 43 | 18/74 danh mục (24,3%) tạo 80% GMV, dẫn đầu health_beauty 9,3% | Quy luật Pareto theo danh mục | `3-3-1_pareto_category.png` | đã có |
| 19 | 44 | Seller thì phân tán hơn: 540 seller tạo 80% GMV, 5 seller lớn nhất chỉ 7,7% | Doanh thu không phụ thuộc vài seller | `3-3-1_pareto_seller.png` | đã có |
| 20 | 45 | Giao trễ làm điểm review rơi từ 4,29 xuống 1,70 và 79,2% review tiêu cực | Đơn trễ chiếm 6,5% số review nhưng tạo 27,4% review tiêu cực | `3-3-1_delay_vs_review.png` | đã có |
| 21 | 46 | Trễ tập trung ở Bắc và Đông Bắc: Nordeste trễ 12,8%, Norte lead time 22,6 ngày | Sudeste chỉ 6,1% trễ, lead time 10,7 ngày | `3-3-1_late_rate_by_state.png` | đã có |
| 22 | 47 | Chỉ 380/842 deal (45,1%) có đơn: funnel và bán hàng chỉ giao nhau một phần | 380 seller tạo 674.005 BRL, 4,99% GMV; 380 là số seller có đơn ở mọi trạng thái; kho chỉ tính đơn không bị huỷ nên có 379 seller (45,0%) | `3-3-1_funnel_seller_overlap.png` | đã có |
| 23 | 48 | Sáu quyết định thiết kế đến từ khám phá dữ liệu | SCD2 khách (0,26% đổi zip); DB4 hai trang (cộng trang chi tiết); snapshot seller dày đặc; 13 nhóm ngành; zip thiếu toạ độ vẫn có dòng; mốc nạp 2017-12 | bảng | đã có |
| 24 | 107 | Mở rộng địa lý: hàm haversine SQL thuần tính khoảng cách seller → khách cho 112.650 dòng hàng | 555 dòng (0,49%) thiếu toạ độ vẫn được giữ lại với giá trị trống | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: đoạn SQL dw.haversine_ |
| 25 | 108 | Khoảng cách tăng từ dưới 100 km lên trên 1.000 km làm phí vận chuyển gấp 2,7 lần và lead time gấp 2,9 lần | Phí 11,75 → 31,65 BRL; lead time 6,5 → 19,0 ngày; trễ 4,5% → 10,3% | `3-5-2_distance_vs_freight.png`, `3-5-2_distance_vs_leadtime.png` | đã có |
| 26 | 109 | Haversine thuần đủ cho khoảng cách điểm–điểm; PostGIS cần khi truy vấn bán kính hoặc đa giác | GiST chỉ mục không gian; haversine sai số tối đa 0,5% | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng so sánh (report/chapters/3-1-kham-pha |
| 27 | 133 | Hai phương pháp cùng đánh dấu 24.213 ngoại lai; nhóm giữ vì đó là ngoại lai hợp lệ | IQR đánh dấu 45.568, Isolation Forest (contamination 0,05, random_state 42) 26.212; Phí cao đi với hàng nặng (trung vị 5.700 g so với 700 g); 76,9% đơ | `3-1_outliers_boxplot.png` | đã có |
| 28 | 134 | Cramér's V lớn nhất 0,403 (giao trễ và nhóm review); tỉ số tương quan review theo cờ trễ 0,392 | V hiệu chỉnh Bergsma cho cặp biến phân loại; cho biến phân loại và biến số; Vùng khách – vùng seller V = 0,072: gần như độc lập | `3-1_cramer_v_heatmap.png` | đã có |
| 29 | 135 | STL: xu hướng mạnh 0,73, mùa vụ tuần 0,22; dưới 2 năm nên không kết luận mùa vụ theo năm | F = (0, 1 - Var(R)/Var(S+R)); Black Friday 24/11/2017: 1.176 đơn, gấp 6,6 lần trung bình tháng 11 | `3-1_stl_daily.png` | đã có |

*29 frame trong `01b-du-lieu-nguon-erd.tex`, `02a-kham-pha.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm** (theo `docs/doi-chieu-nhom6.md`):

| STT mới | Tiêu đề đề xuất (câu kết luận có số) | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| M1 | Danh mục luồng dữ liệu: mỗi luồng có nguồn → đích, thông tin truyền và tần suất | bảng luồng (đơn, thanh toán, đánh giá, MQL, deal …) khớp hai sơ đồ data flow | bảng | `handoff/2026-11-14-P8-source.md` mục 1; `huong-dan/01-pipeline-bang-loi.md` | cần làm |
| M2 | Đánh giá chất lượng sơ bộ trước khám phá: `review_comment_title` rỗng 88,34%, 93,5% mã bưu chính có nhiều toạ độ | tóm tắt chất lượng từng bảng nguồn trước khi vào EDA | bảng hoặc `3-3-1_null_heatmap.png` | `handoff/profiling.md`, `data-quality.md` | cần làm |
| M3 | Bảng các quan hệ của ERD: bảng cha → bảng con, khoá, bội số | mỗi quan hệ một dòng | bảng | `docs/erd_oltp.mmd`; `sql/10_source` | cần làm |
| M4 | Từ điển dữ liệu nguồn: mỗi cột có kiểu, ý nghĩa, ví dụ | một đến hai trang theo nhóm bảng | bảng | `huong-dan/06-tu-dien-du-lieu-nguon.md` | cần làm |
| M5 | Thống kê đặc trưng bằng Python khớp Excel ToolPak trên 5.000 đơn | trung bình, trung vị, độ lệch chuẩn của 5 biến | bảng đối chiếu hai công cụ | `exports/eda_sample.xlsx` (sheet `python_doi_chieu`) | cần làm |
| M6 | Ảnh Excel ToolPak: Descriptive Statistics, Correlation, Histogram cho cùng kết quả | ảnh chụp ToolPak cạnh ảnh Python | 2 ảnh chụp | `handoff/excel-toolpak-guide.md` | cần làm (việc riêng) |
| M7 | Công thức Cramér's V và η cho biến rời rạc, kèm ví dụ số | công thức, ý nghĩa, V = 0,403 và η = 0,392 | công thức + `3-1_cramer_v_heatmap.png` | `handoff/2026-11-14-P8-eda.md` mục D2 | bổ sung vào S134 |

Mỗi biểu đồ EDA cần **một câu nhận xét** ngay trên slide (phần "Nội dung chính" của các slide 3.1 hiện còn ngắn; nhóm 6 mất điểm vì không có nhận xét). Cần thêm loại biểu đồ cho "đa dạng": đã có histogram, boxplot, hexbin, heatmap, Pareto, scatter, đường; kiểm tra không lặp một loại.

Khối lượng: 12 slide 2.4–2.5 + 17 slide 3.1 = 29 slide đang có, thêm 6–7 slide (M1–M7) = **khoảng 36 slide** trong hai file của bạn. **Chọn 8 slide để nói** (khoảng 9 phút):

| Thứ tự nói | Slide (cột S) | Ý chính |
| ---: | --- | --- |
| 1 | S33 | Quy mô: 11 bảng, 121 MB, 1,56 triệu dòng |
| 2 | S128 (taxonomy) và M1 | Cây phân loại và danh mục luồng |
| 3 | S129, S130 | Data flow hiện trạng so với đề xuất |
| 4 | S131 | ERD gạch chân: 65/71 cột đi sang OLAP |
| 5 | S38 và M2 | Chất lượng: 45 loại lỗi |
| 6 | S43, S45 | Pareto và giao trễ kéo điểm review từ 4,29 xuống 1,70 |
| 7 | S133, S134 | Ngoại lai (24.213) và tương quan rời rạc (V = 0,403) |
| 8 | S135, M5 | STL (không kết luận mùa vụ năm) và đối chiếu ToolPak |

## 6. Sơ đồ draw.io

Quy ước chung (màu, font, xuất PNG): `README.md` mục 5. Nộp `.drawio` và PNG vào `03_drawio`.

| Hình | Phải thể hiện | Bản nháp | Lỗi thầy hay bắt |
| --- | --- | --- | --- |
| `2-4_data_taxonomy.png` | cây phân loại 11 bảng thành master / giao dịch / tương tác / tham chiếu, **kèm ví dụ giá trị thật** của từng nhóm | `figures/2-4_data_taxonomy.png` (không có `.drawio`: vẽ mới theo hình nháp) | cây phân loại thiếu ví dụ |
| `2-4_data_flow_hien_trang.png` | các hệ thống CNTT hiện có (sàn, đơn hàng, thanh toán, vận chuyển, đánh giá, marketing funnel SDR/SR) và **thông tin** truyền giữa chúng | `docs/diagrams/data-flow-hien-trang.drawio` | ghi **hành động** trên mũi tên thay vì thông tin |
| `2-4_data_flow_de_xuat.png` | nguồn → staging → ODS → kho → mart → BI, nhật ký ETL giám sát; thông tin trên mũi tên | `docs/diagrams/data-flow-de-xuat.drawio` | như trên; không khác hiện trạng |
| `2-5_erd_oltp_gach_chan.png` | ERD hai hệ thống nguồn, **gạch chân cột dùng sang OLAP**, màu theo nhóm dữ liệu, khoá chính và khoá ngoại | `docs/diagrams/erd-oltp-tomau.drawio` | bố cục rối; không gạch chân; không phân màu |
| `2-5_data_flow_oltp_olap.png` | bảng nguồn nào nuôi dimension nào và fact nào | `docs/diagrams/data-flow-oltp-olap.drawio` | mũi tên ghi hành động |

## 7. Dashboard DB2 – Giao hàng và trải nghiệm khách

Hướng dẫn đầy đủ: [`../dashboards/DB2.md`](../dashboards/DB2.md). Cách mở file, lưu, Refresh, đối chiếu số, chụp ảnh: `README.md` mục 3.

**Câu hỏi trả lời:** đơn mất bao lâu ở từng chặng (duyệt → bàn giao → giao); tỷ lệ giao trễ và hủy, vùng/bang nào chậm nhất; Olist hứa bao nhiêu ngày so với thực tế; khách hài lòng không và vì sao (giao trễ có kéo điểm review xuống không); cơ cấu thanh toán; khách có quay lại mua không.

**Các trang:** trang 1 *Giao hàng* (thẻ On-time rate, Avg lead days, Avg promised days, Promised vs actual, Cancel rate; phễu trạng thái từ `v_status_funnel`; cột chồng thời gian từng chặng; bản đồ hoặc thanh Late rate theo bang; số đơn theo `Delay bucket`); trang 2 *Trải nghiệm khách* (Avg review, % negative, Repeat customer rate; điểm theo mức trễ từ `v_review_vs_delay`; donut thanh toán; RFM; cohort); trang 3 *Key Influencers*; trang tooltip `Tooltip_Muc_tre`.

**Measure chính** (thư mục `DB2 Giao hàng và trải nghiệm khách`, thư mục con *Xử lý đơn*, *Thanh toán*, *Review và khách hàng*): Orders placed, Cancel rate, On-time rate, Late rate, Avg lead days, Avg promised days, Promised vs actual (days), Avg review, % negative, Repeat customer rate, Payment value, Payment share; màu `Color On-time rate`, `Color Cancel rate`, `Color Avg review`, `Color % negative`, `Color promised vs actual`.

**Checklist phải đạt:** ≥ 4 loại biểu đồ; định dạng số (Orders placed `K`, Payment value `M`, phần trăm 1 chữ số); tiêu đề dạng câu hỏi; màu đỏ chỉ để cảnh báo; định dạng có điều kiện (thẻ, bản đồ Late rate, cohort color scale); slicer phân cấp Năm → Quý → Tháng và Vùng → Bang; OLAP drill-down (Vùng → Bang → Thành phố; cohort năm → tháng); tooltip `Tooltip_Muc_tre` và tooltip theo bang; **Key Influencers (chỉ DB2 làm)**; publish và QR (làm khi ghép bộ chung).

**Các bước dựng:**
1. Mở `olist_base.pbix`, *Save as* `DB2_giao-hang.pbix`; Refresh (`README.md` mục 3).
2. Trang 1: bộ lọc trang `dim_date[InWindow] = TRUE`; thẻ KPI từ thư mục DB2; so số với bảng kỳ vọng.
3. Phễu `v_status_funnel` (`stage` sắp theo `stage_no`, lọc `in_window`); cột chồng Avg approval hours, Avg handling days, Avg transit days theo `year_month`; Late rate theo `state_code`; cột `Delay bucket` (cột tính toán đã có sẵn trong `fact_order_fulfillment`).
4. Trang 2: thẻ; `v_review_vs_delay` (trục `delay_bucket` sắp theo `delay_bucket_no`, giá trị `avg_score`); donut `display_name` × Payment value; RFM `v_customer_rfm[segment]`; cohort từ `v_customer_cohort` (color scale).
5. **Trang 3 (Key Influencers):** các cột tính toán `Review type`, `Delay days (order)`, `Lead days (order)`, `Promised days (order)`, `Freight (order)`, `Order value (order)`, `Item count (order)` đã nằm sẵn trong `fact_review` của `olist_base`. Chèn visual *Key influencers*: *Analyze* = `fact_review[Review type]`, *What influences Review type to be* = Tiêu cực; *Explain by* = `delivered_late`, `Delay days (order)`, `Lead days (order)`, `Promised days (order)`, `Freight (order)`, `Order value (order)`, `Item count (order)`, `has_comment_message`, `dim_customer[state_code]`, `dim_date[year_quarter]` (`powerbi/model.md` mục 8). Ghi lại các yếu tố đứng đầu mà visual trả về. Ghi chú trên trang: "mô hình thống kê tự động, cho biết yếu tố đi kèm, không chứng minh nhân quả".
6. Định dạng có điều kiện bằng các measure `Color …`; tooltip `Tooltip_Muc_tre` (số review, điểm TB, % tiêu cực theo nhóm trễ).
7. Slicer: `year_month`, `region`, `order_status`; slicer phân cấp.
8. Đối chiếu với mục 9 của `DB2.md`; đánh dấu checklist mục 10.

**Giá trị kỳ vọng để tự kiểm** (cửa sổ 2017-01 → 2018-08): Orders placed 99,092; Cancel rate 1.19%; On-time rate 93.2%; Late rate 6.8%; Avg lead days 12.5; Avg promised days 24.3; Promised vs actual 11.7; Avg review 4.09; % negative 14.6%; Repeat customer rate 3.11%.

**Câu chuyện khi demo (3 điểm, có số):**
1. Olist hứa trung bình 24,4 ngày nhưng giao 12,6 ngày: sớm hơn lời hứa 11,8 ngày; vì ngày dự kiến quá rộng nên đúng hạn 93,2% dễ đạt. Đúng hạn tụt còn 87,6% ở 11/2017 (Black Friday).
2. Điểm review tụt theo mức trễ: 4,29 (giao sớm) → 3,29 (trễ 1–3 ngày) → 2,10 (4–7 ngày) → 1,70 (trên 7 ngày); đơn trễ chỉ 6,5% số review nhưng tạo 27,4% review tiêu cực.
3. Key Influencers: giao trễ là yếu tố đứng đầu đi kèm review tiêu cực (kỳ vọng từ EDA; **xác nhận lại bằng kết quả thật của visual trước khi nói**).

**Ảnh cần chụp:** `4_DB2_trang1_giao_hang.png`, `4_DB2_trang2_trai_nghiem.png`, `4_DB2_key_influencers.png`, `4_DB2_tooltip.png`; kèm 3–5 câu nhận xét có số cho mỗi ảnh gửi Người 4.

## 8. Việc riêng: Excel ToolPak

Hướng dẫn từng bước: `handoff/excel-toolpak-guide.md` (bật ToolPak, Descriptive Statistics, Correlation, Histogram trên `exports/eda_sample.xlsx`, sheet `du_lieu`, vùng `H1:U5001`). Làm theo thứ tự:
1. Bật ToolPak (File → Options → Add-ins → Analysis ToolPak).
2. Chạy Descriptive Statistics, Correlation, Histogram; mỗi lần chụp ảnh kết quả.
3. So với sheet `python_doi_chieu` (số của Python) và với bảng đối chiếu trong guide (ví dụ `price_total` trung bình 138,22, độ lệch chuẩn 204,06). Hai công cụ phải khớp; nếu lệch, ghi lại và báo lên nhóm.
4. Đặt ảnh vào `04_Docs/tex-nop/figures/` (ví dụ `3-1_toolpak_descriptive.png`) và dùng ở slide M5, M6.

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này:

<!-- QA:19,20,21,29,39,41,42,43,45,46 -->
**Q19. Dữ liệu nguồn có những lỗi gì và xử lý ra sao?**
EDA đo được 45 loại lỗi. Ví dụ: 1.411 đơn (1,4%) có ít nhất một cờ lỗi (1.359 đơn bàn giao trước khi duyệt, 166 bàn giao trước ngày mua, 23 giao trước bàn giao); các khoảng thời gian âm được đặt trống và đếm lại, **không xoá đơn**. Cột phân loại trống thành `unknown`. Toàn bộ nằm ở `etl_log` (`rejected_rows`, `fact_load_issue`).

**Q20. Xử lý bảng geolocation 1 triệu dòng như thế nào?**
1.000.163 dòng nhưng chỉ 19.015 mã bưu chính (93,5% zip có nhiều toạ độ khác nhau, 26,2% dòng trùng hoàn toàn, tên thành phố lệch dấu). ODS lọc điểm trong khung Brazil (loại 42 điểm ngoài khung, ghi `rejected_rows`), gom theo zip lấy **trung vị** vĩ/kinh độ và **mode** thành phố/bang đã chuẩn hoá (`lower(unaccent(trim()))`). Mọi zip vẫn có dòng trong `dim_geography`, kể cả zip không có toạ độ (vĩ/kinh độ để trống). Có hai con số cần phân biệt: **5 zip** có trong geolocation nhưng mọi điểm đều nằm ngoài khung Brazil, và **167 zip** không có toạ độ nói chung, gồm 5 zip trên cộng 162 zip có ở customers/sellers nhưng không có trong geolocation (157 zip khách + 7 zip seller, 2 zip trùng). Tính cả dòng Unknown `-1` thì có 168 dòng `dim_geography` với toạ độ trống.

**Q21. Review bị lặp `review_id` xử lý thế nào?**
Có 789 `review_id` xuất hiện ở nhiều đơn nên không dùng làm khoá chính; khoá là cặp (`review_id`, `order_id`) (99.224 dòng), và ODS khử trùng giữ bản có `review_answer_timestamp` mới nhất nếu có trùng cặp.

**Q29. Pareto 80/20 cho kết quả gì?**
18/74 danh mục (24,3%) tạo 80% GMV, đứng đầu `health_beauty` 9,31%. Với seller, 540/3.053 seller có đơn bán được (17,7%) tạo 80% GMV nhưng 5 seller lớn nhất chỉ chiếm 7,7%: doanh thu **phân tán**, không phụ thuộc vài seller.

**Q39. Vì sao không dùng PostGIS và khoảng cách địa lý tính thế nào?**
Quyết định thiết kế ngày 05/11 (ghi trong nhật ký của `DW_DESIGN.md`): không dùng PostGIS, khoảng cách seller → khách tính bằng công thức haversine viết thành hàm SQL thuần `dw.haversine_km` trên cột `latitude`/`longitude`, và `dim_geography` không có cột `geometry`. Lý do: bài toán chỉ cần khoảng cách điểm–điểm cho 112 nghìn cặp seller–khách, hàm SQL thuần đủ và không thêm extension nào phải cài. Kết quả: khoảng cách TB 598 km, khoảng cách tăng từ < 100 km lên > 1.000 km thì phí vận chuyển 11,75 → 31,65 BRL và lead time 6,5 → 19,0 ngày (Spearman 0,63 và 0,54). PostGIS sẽ cần khi muốn truy vấn bán kính hoặc vùng đa giác (chỉ mục GiST).

**Q41. Ngoại lai được phát hiện thế nào và vì sao không loại?**
Nhóm dùng hai phương pháp: **IQR** (ngoại lai nếu ngoài [Q1 − 1,5·IQR, Q3 + 1,5·IQR]) và **Isolation Forest** (`contamination = 0,05`, `random_state = 42`, mô hình một chiều) trên 5 biến: giá, phí vận chuyển, cân nặng, lead time và số ngày trễ. Cộng 5 biến, IQR đánh dấu 45.568 giá trị, iForest 26.212 và 24.213 giá trị cả hai cùng đánh dấu. **Giữ** vì là ngoại lai hợp lệ: 12.134 dòng có phí cao có cân nặng trung vị 5.700 g (so với 700 g toàn bộ) và 76,9% đơn có lead time ngoại lai đều trễ so với ngày dự kiến. Chỉ 8 dòng hàng có cân nặng bằng 0 g là lỗi dữ liệu, được giữ dòng nhưng không dùng cân nặng. Xem thêm: báo cáo mục 3.1.

**Q42. Cramér's V và tỉ số tương quan η là gì, công thức ra sao?**
V đo liên hệ giữa **hai biến phân loại**: $V = \sqrt{\varphi^2 / \min(r-1, k-1)}$ với $\varphi^2 = \chi^2/n$; nhóm dùng hiệu chỉnh Bergsma ($\tilde\varphi^2 = \max(0, \varphi^2 - (k-1)(r-1)/(n-1))$, $\tilde r = r - (r-1)^2/(n-1)$, $\tilde k = k - (k-1)^2/(n-1)$, $\tilde V = \sqrt{\tilde\varphi^2/\min(\tilde k-1, \tilde r-1)}$) để không phóng đại khi bảng chéo lớn. η đo liên hệ giữa **biến phân loại và biến số**: $\eta = \sqrt{\sum_g n_g(\bar x_g - \bar x)^2 / \sum_i (x_i - \bar x)^2}$, và η² là tỉ lệ phương sai do nhóm giải thích. Thang đọc: < 0,1 không đáng kể; 0,1–0,3 yếu; 0,3–0,5 vừa; > 0,5 mạnh. Kết quả: V lớn nhất là 0,403 giữa cờ giao trễ và nhóm review; η của điểm review theo cờ trễ là 0,392 (η² = 0,154). Spearman chỉ dùng cho hai biến số hoặc thứ bậc.

**Q43. STL là gì và độ mạnh xu hướng, mùa vụ tính thế nào? Có kết luận mùa vụ theo năm không?**
STL tách chuỗi thành xu hướng, mùa vụ và phần dư: $y_t = T_t + S_t + R_t$. Độ mạnh $F_T = \max(0, 1 - \mathrm{Var}(R)/\mathrm{Var}(T+R))$ và $F_S = \max(0, 1 - \mathrm{Var}(R)/\mathrm{Var}(S+R))$. Số đơn theo ngày (chu kỳ 7 ngày): $F_T = 0{,}734$, $F_S = 0{,}223$ (thứ Hai nhiều đơn nhất, thứ Bảy ít nhất). **Không kết luận mùa vụ theo năm**: dữ liệu dưới 2 năm (20 tháng đủ dữ liệu 2017-01 → 2018-08), STL chu kỳ 12 cho $F_S = 0{,}800$ nhưng mỗi tháng chỉ xuất hiện một hoặc hai lần nên không tách được khỏi xu hướng tăng; chỉ ghi nhận Black Friday 24/11/2017 (1.176 đơn, gấp 6,6 lần trung bình tháng 11).

**Q45. Data taxonomy của dữ liệu nguồn là gì?**
Cây phân loại 11 bảng thành 4 nhóm: **dữ liệu chủ** (customers, sellers, products), **dữ liệu giao dịch** (orders, order_items, order_payments), **dữ liệu tương tác** (order_reviews, mql, closed_deals) và **dữ liệu tham chiếu** (geolocation, product_category_name_translation); mỗi bảng có giá trị thật làm ví dụ và được phân loại thêm theo kiểu dữ liệu, độ nhạy cảm (định danh, vị trí) và tính biến động. Nhờ đó chọn được cách nạp: bảng biến động cao (orders) nạp tăng dần theo watermark, bảng tĩnh (geolocation, bản dịch) nạp lại toàn phần. Xem thêm: hình `figures/2-4_data_taxonomy.png`.

**Q46. Data flow giữa các hệ thống CNTT hiện trạng và đề xuất khác nhau thế nào?**
Hiện trạng: marketplace, hệ thống đơn hàng, thanh toán, vận chuyển, đánh giá và marketing funnel (SDR, SR) truyền cho nhau **thông tin** (thông tin đơn, trạng thái giao, thông tin thanh toán, điểm đánh giá, lead); hai hệ thống bán hàng và CRM tách rời, chỉ gặp nhau qua `seller_id`. Đề xuất: nguồn → staging → ODS → kho → mart → BI, có `etl_log` giám sát; mỗi lô full hoặc tăng dần. Với khối lượng trung bình 163 đơn/ngày (đỉnh 1.176 ngày Black Friday), lô hằng ngày bằng procedure PostgreSQL là đủ; nếu cần gần thời gian thực thì thêm CDC + Kafka (chương 5).
<!-- /QA -->

Câu mới:

**Q-M1. Vì sao dùng lô hằng ngày mà không dùng luồng thời gian thực?**
Đơn hàng trung bình 163 đơn mỗi ngày, đỉnh 1.176 đơn ngày Black Friday: khối lượng nhỏ nên một lô hằng ngày bằng procedure PostgreSQL xử lý trong vài giây. Luồng thời gian thực (CDC + Kafka) chỉ cần nếu đội sales phải phản hồi MQL ngay; nhóm đưa vào hướng mở rộng. Xem `handoff/2026-11-14-P8-source.md`.

**Q-M2. Excel ToolPak và Python cho cùng kết quả không?**
Có, trên cùng mẫu 5.000 đơn đã giao: ví dụ `price_total` trung bình 138,22, trung vị 85,00, độ lệch chuẩn 204,06 ở cả hai công cụ. Sheet `python_doi_chieu` của `eda_sample.xlsx` chứa số của Python để đối chiếu.

**Q-M3. Vì sao hai biến phân loại không dùng hệ số Pearson?**
Pearson chỉ đo quan hệ tuyến tính giữa hai biến số. Với biến phân loại (giao trễ hay không, nhóm điểm review) dùng Cramér's V từ bảng chéo; với một biến phân loại và một biến số (điểm review theo cờ trễ) dùng tỉ số tương quan η.

**Q-M4. Vì sao ERD có 65/71 cột được gạch chân?**
Cột được gạch chân là cột đi sang kho; 6 cột còn lại không dùng, ví dụ `geolocation.id` và hai cột khai báo của `closed_deals` (`declared_monthly_revenue`, `declared_product_catalog_size`). Danh sách đầy đủ ở `handoff/2026-11-14-P8-mapping-summary.md`.

**Q-M5. Key Influencers cho kết quả gì và có chứng minh giao trễ gây review xấu không?**
Visual cho biết yếu tố nào đi kèm review tiêu cực mạnh nhất (kỳ vọng: giao trễ). Đó là liên hệ thống kê, không chứng minh nhân quả; nhóm ghi chú trên trang dashboard.

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Viết dựa trên slide của mình. Số trang hiện tại: <!-- PAGES:2.4,2.5,3.1 -->mục 2.4: trang 14–19 (6 trang); mục 2.5: trang 20–23 (4 trang); mục 3.1: trang 24–39 (16 trang); tổng 26 trang<!-- /PAGES -->.

Các `\todo` hiện có (đếm từ mã nguồn):

<!-- TODOS:2-4-du-lieu-nguon.tex,2-5-erd-oltp.tex,3-1-kham-pha.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/2-4-du-lieu-nguon.tex` | 2 | 1. Nhóm nêu rõ tần suất cập nhật giả định của hệ thống thực (ví dụ đơn hàng cập nhật liên tục, kho cập nhật hằng ngày) và dung lượng mỗi lần cập nhật.<br>2. Nhóm vẽ lại hai sơ đồ luồng dữ liệu bằng draw.io từ docs/diagrams/data-flow-hien-trang.drawio và data-flow-de-xuat.drawio (giữ tên file hình); kiểm tra tên các hệ thống ngoài (marketplace, vận chuyển, thanh toá… |
| `report/chapters/2-5-erd-oltp.tex` | 2 | 1. Yêu cầu của môn: trên ERD OLTP gạch chân các trường dữ liệu sẽ dùng sang OLAP và ghi chú mapping tương ứng. Vẽ lại ERD bằng draw.io từ hình nháp, gạch chân các cột dùng và ghi chú (bảng mapping đầy đủ ở Phụ lục…<br>2. Nhóm vẽ lại ERD bằng draw.io từ docs/diagrams/erd-oltp-tomau.drawio (giữ tên file hình 2-5_erd_oltp_gach_chan.png) và sơ đồ data flow OLTP sang OLAP từ docs/diagrams/data-flow-oltp-olap.drawio. |
| `report/chapters/3-1-kham-pha.tex` | 3 | 1. Chọn các hình cần đưa vào thân báo cáo (các hình còn lại chuyển sang phụ lục); thêm hình 3-3-1_funnel_* khác nếu cần. Bổ sung kết quả Excel Data Analysis ToolPak (thống kê mô tả, tương quan) theo hướng dẫn hand…<br>2. Nhóm bổ sung phần lý thuyết cơ sở dữ liệu địa lý (mô hình vector/raster, kiểu dữ liệu không gian, chỉ mục không gian) từ tài liệu PostGIS postgis_docs và công thức haversine sinnott1984; thêm bản đồ bong bóng t…<br>3. Nhóm chạy Data Analysis ToolPak trên exports/eda_sample.xlsx (Descriptive Statistics, Correlation, Histogram), chụp ảnh kết quả và so với sheet python_doi_chieu trước khi đưa vào báo cáo. |
| **Tổng** | **7** | |
<!-- /TODOS -->

## 11. Checklist trước khi nộp

| Việc | Xong |
| --- | --- |
| 5 sơ đồ draw.io vẽ lại, xuất PNG đúng tên, nộp `03_drawio` | ☐ |
| Bản nháp slide `01b-du-lieu-nguon-erd.tex`, `02a-kham-pha.tex` (thêm M1–M7, câu nhận xét cho mỗi biểu đồ) | ☐ |
| Ảnh ToolPak (việc riêng) | ☐ |
| Bản đầu DB2; ảnh `4_DB2_*.png` và 3–5 câu nhận xét gửi Người 4 | ☐ |
| 3–5 câu bài học gửi Người 4 (về dữ liệu: ngày dự kiến quá rộng, toạ độ bẩn, ngoại lai giữ lại) | ☐ |
| Slide và DB2 xong; nộp `.tex` và hình mới vào `04_Docs/tex-nop/` | ☐ |
| Tập, bấm giờ, tổng duyệt | ☐ |

Trước khi nộp slide: không còn khung đỏ `CHÈN HÌNH` (tìm `khungchen`); tiêu đề là câu kết luận có số; mỗi biểu đồ EDA có một câu nhận xét; mỗi slide có `\muc{...}`; biên dịch bằng `thu-mot-phan.tex` không lỗi.
Trước khi nộp dashboard: mọi mục checklist DB2 (mục 10 của `DB2.md`) đã đánh dấu; số khớp mục 9; kết quả Key Influencers đã ghi lại.

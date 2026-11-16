# Người 4 – Chương Dashboard, bài học tổng kết và dashboard DB4

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io): [`README.md`](README.md). File này chỉ nói phần của Người 4. Người 4 vừa dựng DB4, vừa là người **tổng hợp** phần dashboard của cả nhóm: nhận ảnh và nhận xét của DB1–DB3, nhận bài học của mọi người.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | **Ch.4 Dashboard và BI**: bản đồ bộ dashboard, giới thiệu và demo 4 dashboard, publish và QR; **bài học tổng kết** của cả nhóm |
| File slide | `slides/sections/03-dashboard.tex` (23 frame đang có) |
| Sơ đồ draw.io | **bản đồ bộ dashboard** (vẽ mới; đề xuất tên `4_ban_do_bo_dashboard.png`) |
| Dashboard | **DB4 Thu hút và hiệu quả seller** (funnel; drill-through sang chi tiết seller) |
| Việc riêng | gom bài học của cả nhóm; kiểm tra checklist của cả 4 dashboard |
| Thuyết trình | dashboard và bài học tổng kết; khoảng **7 slide nói** (điều chỉnh theo thời lượng chung của nhóm) |
| Báo cáo (giai đoạn 2) | `4-dashboard.tex` (20 `\todo`, nhiều nhất trong báo cáo) |

Slide DB1–DB3 trong `03-dashboard.tex` do bạn viết, từ **ảnh chụp và 3–5 câu nhận xét** mà Người 1, 2, 3 gửi.

## 2. Barem chấm gì ở phần này

Các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu của thầy; dòng đỏ là chỗ nhóm khác bị trừ điểm):

**Dashboard**
- Số lượng dashboard (4 dashboard).
- Màu sắc, bố cục hài hoà.
- Phân tích chi tiết dạng **storytelling**.
- Tiêu đề, đồ thị, icon minh hoạ, menu.
- **Đơn vị tính trên dashboard; định dạng số có nghĩa** (ví dụ 1000 → 1,000; 12.39% → 12%; số đơn hàng 12K → 12.3K) (bị trừ).
- Các định dạng có điều kiện cảnh báo, sử dụng các hàm DAX.
- **Phân tích OLAP** (slicer, drill-down) (bị trừ).
- **Phân tích theo dòng thời gian để phát hiện tính mùa, xu thế, dự báo** (bị trừ).
- **Sử dụng drill-through, tooltip để phân tích chi tiết** (bị trừ).
- Public dashboard lên web (ai cũng xem được, không cần đăng nhập).

**Bài học tổng kết** (cột riêng trong bảng điểm; ví dụ điểm của nhóm khác: 3 đến 4).

**Điểm bổ sung (hướng mở rộng):** do Phú phụ trách (chương 5).

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Dashboard (slide 135–147) | 3,5 | bảng KPI theo dashboard; thống kê bộ dashboard; publish và QR; mỗi dashboard một trang tình huống rồi một trang dashboard; trang kỹ thuật dùng | **nhóm 6 thấp nhất ở mục này.** Hơn: đủ checklist của thầy (định dạng số, OLAP, dự báo, drill-through, tooltip, định dạng có điều kiện); mỗi dashboard kể một câu chuyện có số. Cần làm: trang tình huống trước mỗi dashboard; kiểm tra 4 dashboard đủ checklist |
| Bài học (slide 148–150, 235–237) | 4 | bài học về chỉ số và về quy trình; tổng kết quy trình, kiến thức và công cụ | đã có bản nháp bằng ví dụ thật. Cần làm: mỗi bài học gồm **vấn đề → con số → cách xử lý** |

Không được chép câu chữ, số liệu hay hình của nhóm 6.

## 3. Kiến thức cần nắm

**Bốn dashboard và vì sao chia như vậy.** Bộ dashboard gộp từ 7 dashboard ở bản trước để mỗi người phụ trách một dashboard; mỗi dashboard thuộc một loại mà môn học yêu cầu:

| Dashboard | Loại | Điểm checklist nổi bật |
| --- | --- | --- |
| DB1 Tổng quan và doanh thu | theo dòng thời gian | **dự báo** |
| DB2 Giao hàng và trải nghiệm khách | vận hành + thống kê | **Key Influencers** |
| DB3 Địa lý và phí vận chuyển | OLAP | **drill-down Vùng → Bang → Thành phố**, drill-through chi tiết bang, tooltip |
| DB4 Thu hút và hiệu quả seller | vận hành, funnel | drill-through chi tiết seller |

Giám sát chất lượng dữ liệu và ETL **không còn là dashboard**: là bảng ở mục 3.3 của báo cáo. Dashboard Thị trường Brazil (dữ liệu API, D8) thuộc chương 5 (Phú).

**Các khái niệm của checklist** (dùng khi giới thiệu và demo):
- **Định dạng số rút gọn:** GMV `13.5M` (triệu), số đơn `98.2K` (nghìn), phần trăm một chữ số `93.2%`; luôn ghi đơn vị (BRL, ngày, %) ở tiêu đề hoặc nhãn trục.
- **Tiêu đề dạng câu hỏi:** mỗi visual có tiêu đề là câu hỏi nó trả lời ("Doanh thu tăng hay giảm so với tháng trước?").
- **Màu đỏ chỉ để cảnh báo:** đỏ chỉ xuất hiện qua định dạng có điều kiện khi giá trị xấu; bảng màu dữ liệu không có đỏ.
- **Định dạng có điều kiện bằng DAX:** measure trả về mã màu (`Color On-time rate`: dưới 90% đỏ, dưới 95% vàng, còn lại xanh) gắn vào thẻ, cột, bản đồ.
- **Drill-down / roll-up (OLAP):** đi xuống / lên một cấp trong phân cấp (Vùng → Bang → Thành phố). **Drill-through:** chuột phải một điểm để **sang trang khác** chi tiết hơn (DB3: chi tiết bang; DB4: chi tiết seller). **Tooltip:** di chuột hiện một trang nhỏ. Phân biệt ba thao tác này vì thầy hay hỏi.
- **Dự báo:** line chart theo tháng có đường dự báo 3 điểm, tin cậy 95%; dữ liệu 20 tháng nên chỉ để thấy hướng đi.
- **Key Influencers:** visual AI của Power BI cho biết yếu tố nào đi kèm kết quả (review tiêu cực); là liên hệ thống kê, không chứng minh nhân quả.
- **Publish to web:** công khai, ai có link đều xem được; dữ liệu Olist là dữ liệu công khai nên chấp nhận; một số tài khoản trường tắt mục này (phương án dự phòng: xuất PDF/PowerPoint và chụp ảnh).

**Storytelling với dashboard.** Mỗi dashboard kể một câu chuyện có số theo ba bước: tình huống (ai cần biết gì), phát hiện (con số), hành động (nên làm gì). Ví dụ DB2: Olist hứa 24,4 ngày nhưng giao 12,6 ngày (sớm hơn 11,8 ngày), nên "đúng hạn 93,2%" dễ đạt; điểm review tụt 4,29 → 1,70 theo mức trễ; hành động: đặt ngày hứa sát thực tế và theo dõi chặng vận chuyển (9,3 ngày).

**Bài học tổng kết.** Mỗi bài học theo khuôn **vấn đề → con số → cách xử lý**. Nhóm có sẵn các bài học có số thật (kiểm tra lại số trước khi nói):
- *Chỉ số:* **GMV có hai cách đo** (13,49 so với 13,59 triệu BRL) → định nghĩa mỗi KPI một lần bằng DAX và đối chiếu với SQL. **Review đúng hạn 4,21 sửa thành 4,29**: đơn chưa giao cũng có `delivered_late = 0` nên phải thêm điều kiện `is_delivered = 1`.
- *Dữ liệu:* ngày dự kiến giao quá rộng (hứa 24,4 ngày, thực tế 12,6) nên đúng hạn 93,2% không phản ánh trải nghiệm → thêm KPI hứa so với thực tế. 380 so với 379 seller: khác phạm vi đơn (có hay không tính đơn *Failed*).
- *Quy trình:* không xoá âm thầm (42 dòng toạ độ ngoài Brazil bị loại có ghi lý do); chọn grain trước khi vẽ bảng fact; dựng lại toàn bộ bằng một lệnh trong 443 giây cho kết quả giống hệt.
- *Công cụ và làm việc nhóm:* nhóm bổ sung (mục 8).

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn | Dùng ở |
| --- | --- | --- | --- |
| Bốn dashboard, ma trận checklist | 4 dashboard × 11 mục | `huong-dan/dashboards/README.md` | S89, S143 |
| Thống kê bộ dashboard (số **thiết kế**) | 10 trang chính, 4 tooltip, 68 visual, 23 slicer, 56 measure | `report/tables/p8b_dashboard_stats.tex`; thay bằng số thật sau khi dựng | báo cáo 4.1.5 |
| Mô hình Power BI | 38 bảng, 32 quan hệ, 65 measure | `powerbi/olist_base/README.md`; `handoff/2026-11-14-P8c.md` | S90 |
| Kỳ vọng từng dashboard | bảng giá trị mục 9 của `DB1.md` … `DB4.md` | `huong-dan/dashboards/` | đối chiếu |
| Insight từng dashboard | mục 8 của `DB1.md` … `DB4.md` | `huong-dan/dashboards/` | slide DB1–DB4 |
| Funnel (DB4) | 8.000 → 842 → 379; chốt TB 48,5 ngày; đến đơn đầu 51,9 ngày | `DB4.md` mục 8 | S103–S104, S147 |
| Giới hạn dữ liệu | GMV hai cách đo; 380/379 | `huong-dan/05-nghiep-vu-nhap.md` mục 13 | S144 |
| Bài học nháp | S112, S144 | `slides/slide-script.md`; `report/chapters/06-ket-luan.tex` | slide bài học |

Hình: ảnh chụp dashboard `4_DBx_<mô-tả>.png` (nhóm chụp), `figures/2-3_cay_phan_tich_DB1…DB4.png` (cây phân tích), `figures/4_qr_dashboard.png` (tạo sau khi publish).

## 5. Danh sách slide đề xuất

**Các slide đang có** (bảng do script đọc từ file `.tex`; hầu hết là khung chờ ảnh dashboard):

<!-- SLIDES:03-dashboard.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 89 | Bốn dashboard theo bốn loại: dòng thời gian có dự báo, thống kê, OLAP và vận hành | DB1 Tổng quan và doanh thu DB2 Giao hàng và trải nghiệm khách DB3 Địa lý và phí vận chuyển DB4 Thu hút và hiệu quả seller | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng 4 dashboard (huong-dan/dashboards/ |
| 2 | 90 | Mô hình Power BI có 16 bảng và 32 quan hệ, mỗi fact một quan hệ ngày hoạt động | Quan hệ còn lại không hoạt động | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: ảnh chụp Model view |
| 3 | 91 | Role-playing date và DAX tăng trưởng: GMV tháng 11/2017 tăng 52,1% so với tháng 10 | USERELATIONSHIP, DATEADD, SAMEPERIODLASTYEAR | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: đoạn DAX (powerbi/measures.md |
| 4 | 92 | Chủ đề màu thống nhất: xanh là tốt, vàng cần chú ý, đỏ là xấu | powerbi/theme.json; ngưỡng cảnh báo on-time 90%/95% | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: ảnh chụp theme |
| 5 | 93 | DB1 trang 1: GMV 13,49 triệu BRL, 98.199 đơn, đúng hạn 93,2%, review 4,09 | Thẻ KPI, đường GMV theo tháng, cột MoM, thanh theo vùng, treemap ngành | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB1 trang 1 |
| 6 | 94 | DB1 trang 1: tháng 11/2017 là đỉnh 1,0 triệu BRL, Sudeste 65% GMV, có đường dự báo | Black Friday 152.654 BRL trong một ngày | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB1 trang 1 |
| 7 | 95 | DB1 trang 2: 18 danh mục tạo 80% GMV; Home & Furniture dẫn đầu 22,8% | Treemap, ma trận drill, Pareto, scatter AOV – freight | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB1 trang 2 |
| 8 | 96 | DB1 trang 2: phí vận chuyển nặng ở hàng giá thấp và ở vùng xa | Freight ratio 16,6% toàn sàn | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: ảnh chụp DB1 trang 2 (scatter) |
| 9 | 97 | DB2 trang 1: lead time 12,6 ngày, phễu trạng thái và tỷ lệ trễ theo bang | Funnel, cột chồng từng chặng, bản đồ trễ | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB2 trang 1 |
| 10 | 98 | DB2 trang 1: Olist hứa 24,4 ngày, giao 12,6 ngày, sớm hơn lời hứa 11,8 ngày | Đúng hạn tụt 87,6% ở Black Friday 11/2017 và 81,0% ở 03/2018 | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB2 trang 1 |
| 11 | 101 | DB2 trang 2: review 4,09, 14,7% tiêu cực, chỉ 3,1% khách quay lại | Cột điểm theo nhóm trễ, donut thanh toán, RFM, cohort | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB2 trang 2 |
| 12 | 102 | DB2 trang 2: thẻ tín dụng 78,3% giá trị thanh toán, trả góp trung bình 3,5 kỳ | 66,9% giao dịch thẻ trả góp nhiều kỳ | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB2 trang 2 |
| 13 | 145 | DB2 trang 3: Key Influencers cho biết yếu tố nào đi kèm review tiêu cực | Kỳ vọng từ khám phá dữ liệu: giao trễ đứng đầu (Cramér's V 0,403; 0,392); Mô hình thống kê tự động, không chứng minh nhân quả | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB2 trang 3 (Key Influencers) |
| 14 | 99 | DB3 trang 1: Sudeste 65,4% GMV, Norte và Nordeste chịu phí vận chuyển 22% | Bản đồ bong bóng, ma trận phân cấp, GMV khách và seller | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB3 trang 1 |
| 15 | 100 | DB3 trang 1: 36% dòng hàng có seller và khách cùng bang; drill-down vùng đến thành phố | Khoảng cách TB 598 km | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB3 trang 1 |
| 16 | 146 | DB3 trang 2: drill-through từ một bang sang trang chi tiết bang, kèm tooltip theo bang | Chuột phải một bang → Drill through → Chi tiết bang; Thẻ GMV, Freight ratio, Avg lead days, Late rate; bảng theo thành phố | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB3 trang 2 (Chi tiết bang) |
| 17 | 103 | DB4 trang 1: tỷ lệ chốt theo kênh từ 2,7% (other) đến 16,7% (unknown) | Phễu MQL → deal → seller có đơn; thời gian chốt | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB4 trang 1 TRANG 1 |
| 18 | 104 | DB4 trang 2: seller từ funnel chỉ tạo 4,99% GMV; kênh nhỏ được cảnh báo mẫu nhỏ | Scorecard seller, GMV/seller theo kênh | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB4 trang 2 TRANG 2 |
| 19 | 147 | DB4 trang 3: drill-through sang chi tiết seller cho thấy tháng seller ngừng bán | Trường drill-through dim_seller[seller_id]; Đường GMV theo tháng nhờ snapshot dày đặc, kèm cảnh báo mẫu nhỏ | khung chờ | cần ảnh: CHÈN ẢNH CHỤP DB4 trang 3 (Chi tiết seller) |
| 20 | 106 | Publish to web chia sẻ cả bốn dashboard bằng một liên kết công khai và mã QR | Dữ liệu Olist công khai nên chấp nhận được | khung chờ | cần ảnh: CHÈN HÌNH: ảnh Publish to web và mã QR của link |
| 21 | 143 | Checklist chung: dự báo ở DB1, Key Influencers ở DB2, OLAP và drill-through ở DB3, DB4 | Số đơn 12.3K, tiền 13.5M, phần trăm một chữ số thập phân; Màu đỏ chỉ để cảnh báo; theme không còn đỏ trong màu dữ liệu | – | đã có |
| 22 | 112 | Bài học: không xóa âm thầm, chọn grain trước, định nghĩa KPI một lần | Mô hình chiều đáng dùng vì nhất quán, tốc độ đến từ materialized view và index | – | đã có |
| 23 | 144 | Bài học chỉ số: GMV 13,49 so với 13,59 triệu, review đúng hạn 4,21 sửa thành 4,29 | Chọn một định nghĩa và ghi cạnh con số; 380 so với 379 seller; Sửa ở ETL (cột is_delivered), không sửa ở BI | – | đã có |

*23 frame trong `03-dashboard.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm hoặc sửa** (theo `docs/doi-chieu-nhom6.md`):

| STT mới | Tiêu đề đề xuất (câu kết luận có số) | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| D1 | Bốn dashboard trả lời bốn nhóm câu hỏi: doanh thu, giao hàng và khách, địa lý, thu hút seller (thay khung chờ S89) | bản đồ bộ dashboard: loại, câu hỏi, KPI chính, người dùng | sơ đồ draw.io `4_ban_do_bo_dashboard.png` | `huong-dan/dashboards/README.md` | cần làm |
| D2 | Tình huống DB1: ban điều hành cần biết doanh thu tăng hay giảm | ai xem, câu hỏi, tần suất; trước slide DB1 | – | `DB1.md` mục 2 | cần làm |
| D3 | Tình huống DB2: Olist hứa 24,4 ngày nhưng giao 12,6 ngày, vậy khách có hài lòng? | như trên | – | `DB2.md` mục 2, 8 | cần làm |
| D4 | Tình huống DB3: phí vận chuyển nặng ở vùng xa, ai chịu? | như trên | – | `DB3.md` mục 2, 8 | cần làm |
| D5 | Tình huống DB4: 8.000 MQL chỉ ra 379 seller bán được, kênh nào đáng đầu tư? | như trên | – | `DB4.md` mục 2, 8 | cần làm |
| D6 | Trang kỹ thuật dùng: mô hình 38 bảng, 32 quan hệ, 65 measure (sửa S90 "16 bảng") | số liệu mô hình hiện tại | – | `powerbi/olist_base/README.md` | sửa slide có sẵn |
| D7 | Bài học về quy trình, kiến thức, công cụ của cả nhóm (mỗi bài học: vấn đề → con số → xử lý) | 3 slide tổng kết sau khi gom bài học | bảng | mục 8 của file này | cần làm (sau 26/11) |
| D8 | Mã QR: quét để xem 4 dashboard công khai (S106) | link public và QR | `figures/4_qr_dashboard.png` | sau khi publish | cần ảnh QR |

Khối lượng: 23 slide đang có + 8 slide thêm (D1–D8) = **khoảng 31 slide** trong file của bạn. Các slide DB1–DB4 theo từng dashboard (khoảng 3–5 slide mỗi dashboard) là slide chi tiết; khi trình bày thực tế chủ yếu **demo trên Power BI** (hoặc qua QR). **Chọn 7 slide để nói** (khoảng 9 phút):

| Thứ tự nói | Slide (cột S) | Ý chính |
| ---: | --- | --- |
| 1 | S89 và D1 | Bản đồ bộ dashboard: bốn dashboard, bốn loại |
| 2 | S93 hoặc S94, rồi demo DB1 | Tình huống DB1, GMV, dự báo |
| 3 | S98 hoặc S145, rồi demo DB2 | Hứa 24,4 so với giao 12,6 ngày; Key Influencers |
| 4 | S100 hoặc S146, rồi demo DB3 | Drill-down Vùng → Bang → Thành phố, drill-through |
| 5 | S103 hoặc S147, rồi demo DB4 | Funnel 8.000 → 842 → 379; drill-through seller |
| 6 | S143, S106 và D8 | Checklist đạt đủ, publish và QR |
| 7 | S112, S144 và D7 | Bài học tổng kết |

## 6. Sơ đồ draw.io: bản đồ bộ dashboard

Quy ước chung (màu, font, xuất PNG): `README.md` mục 5.

- **Phải thể hiện:** bốn khối DB1–DB4; mỗi khối ghi **loại** (dòng thời gian, thống kê, OLAP, vận hành), **câu hỏi chính**, **KPI chính** (ví dụ DB1: GMV 13,49 triệu BRL; DB2: On-time rate 93,2%; DB3: Freight ratio 16,6%; DB4: MQL to won rate 10,5%), người dùng và số trang; các **liên kết giữa dashboard** (drill-through DB3 → trang Chi tiết bang, DB4 → trang Chi tiết seller; dùng chung một mô hình 38 bảng, 65 measure) và **điểm checklist** của từng dashboard (dự báo ở DB1, Key Influencers ở DB2, drill-down ở DB3…). Dạng sơ đồ cấu trúc (khối và liên kết), không vẽ thành luồng dữ liệu.
- **Bản nháp:** chưa có; vẽ mới. Tài liệu nguồn: `huong-dan/dashboards/README.md` (bảng loại và ma trận), `DB1.md` … `DB4.md` (câu hỏi, KPI).
- **Màu:** dùng bảng màu chung ở `README.md` mục 5; mỗi dashboard một màu phụ (xanh dương, cam, xanh lá, tím) và nhắc lại đúng quy ước **đỏ chỉ để cảnh báo** (không dùng đỏ cho khối).
- **Lỗi thầy hay bắt:** không có menu/điều hướng, không thấy mối liên hệ giữa các dashboard; không nêu loại phân tích (dòng thời gian, OLAP…).

## 7. Dashboard DB4 – Thu hút và hiệu quả seller

Hướng dẫn đầy đủ: [`../dashboards/DB4.md`](../dashboards/DB4.md). Cách mở file, lưu, Refresh, đối chiếu số, chụp ảnh: `README.md` mục 3.

**Câu hỏi trả lời:** bao nhiêu % MQL được chốt, theo kênh; chốt deal và có đơn đầu tiên mất bao lâu; seller từ funnel đóng góp GMV bao nhiêu, giao trễ và review ra sao; seller nào GMV cao nhưng hay trễ. **Luôn ghi cỡ mẫu.**

**Các trang:** trang 1 *Funnel theo kênh* (funnel MQLs → Won deals → Sellers with first sale; thanh MQL to won rate theo origin; cột Avg days to close theo nhóm kênh; đường MQLs theo tháng; thẻ Won to first sale rate, Avg days won to first sale, Seller GMV first 90d); trang 2 *Seller từ funnel và hiệu suất* (bảng `v_seller_scorecard` lọc `is_from_funnel`, cột GMV/seller theo kênh từ `v_seller_by_channel` kèm cảnh báo mẫu nhỏ, scatter GMV – late rate, thẻ deal chốt chưa bán = 462; **ghi "toàn bộ giai đoạn" vì dùng bảng mart không lọc ngày**); trang 3 *Chi tiết seller* (drill-through theo `dim_seller[seller_id]`); trang tooltip `Tooltip_Kenh`.

**Measure chính** (thư mục `DB4 Thu hút và hiệu quả seller`, thư mục con *Thu hút seller* và *Hiệu suất seller*): MQLs, Won deals, MQL to won rate, Avg days to close, Sellers with first sale, Won to first sale rate, Avg days won to first sale, Seller GMV first 90d, Active sellers, Seller GMV (monthly), Seller late rate, Small sample warning.

**Checklist phải đạt:** ≥ 4 loại biểu đồ (bar, card, column, funnel, line, scatter, table); định dạng số; tiêu đề dạng câu hỏi; màu đỏ chỉ để cảnh báo (`late_rate_pct` > 10%, cảnh báo mẫu nhỏ); định dạng có điều kiện (`late_rate_pct`, `small_sample`, `avg_review_score`); slicer phân cấp Nhóm kênh → Origin; drill (Origin → Nhóm kênh; bảng seller theo bang); **drill-through trang Chi tiết seller**; tooltip `Tooltip_Kenh`; publish và QR (làm khi ghép bộ chung).

**Các bước dựng:**
1. Mở `olist_base.pbix`, *Save as* `DB4_thu-hut-seller.pbix`; Refresh.
2. Trang 1: bộ lọc `InWindow = TRUE`; funnel; thanh `MQL to won rate` theo `dim_lead_origin[origin]`; cột Avg days to close theo `channel_group`; đường MQLs theo `year_month` tách theo `channel_group`; ba thẻ.
3. Trang 2: bảng seller từ `v_seller_scorecard` (lọc `is_from_funnel = TRUE`) và **bảng drill-through** dùng `dim_seller[seller_id]`, `dim_seller[acquisition_channel]`, `Seller GMV (monthly)`, `Seller late rate` (bảng này có quan hệ với `fact_seller_monthly`, nên drill-through lọc đúng; `v_seller_scorecard` là bảng rời, chỉ để hiển thị điểm review); cột GMV/seller theo kênh có `selling_sellers` và `small_sample`; scatter; thẻ `Won deals − Sellers with first sale` (462).
4. Định dạng có điều kiện: `late_rate_pct` đỏ khi > 10%; `small_sample = TRUE` chữ xám; `avg_review_score` theo `Color Avg review`.
5. **Trang 3 Chi tiết seller:** *Page type = Drillthrough*, trường drill-through `dim_seller[seller_id]`; thẻ seller_id, kênh, bang, Seller GMV (monthly), Seller late rate; đường GMV theo `year_month` (thấy tháng seller ngừng bán nhờ snapshot dày đặc); bảng tháng – số đơn – số đơn trễ; `Small sample warning`; nút Back. Kiểm tra: chuột phải một seller ở trang 2 → *Drill through* → *Chi tiết seller*.
6. Tooltip `Tooltip_Kenh` (MQLs, Won deals, MQL to won rate, cỡ mẫu), gán cho thanh `MQL to won rate`.
7. Đối chiếu mục 9 của `DB4.md`; đánh dấu checklist mục 10.
(Trang `DB4 Chi tiết seller` đã có sẵn trống trong `olist_base.pbix`; nếu chưa gán trường `seller_id` thì tự đặt ở bước 5.)

**Giá trị kỳ vọng để tự kiểm** (cửa sổ 2017-01 → 2018-08 = toàn bộ giai đoạn cho funnel): MQLs 8,000; Won deals 842; MQL to won rate 10.5%; Avg days to close 48.5; Sellers with first sale 379; Won to first sale rate 45.0%; Avg days won to first sale 51.9; Seller GMV first 90d 538,271.72; Seller GMV (monthly) 13,449,529.68; Seller late rate 6.7%.

**Câu chuyện khi demo (3 điểm, có số):**
1. 8.000 MQL → 842 deal (10,5%) → 379 seller có đơn bán được (45,0% số đã chốt); 462 deal chốt nhưng chưa bán.
2. Tỷ lệ chốt theo kênh: `unknown` 16,7%, `paid_search` 12,3%, `organic_search` 11,8%; thấp nhất `email` 3,0% (493 MQL) và `other` 2,7% (150 MQL, mẫu nhỏ).
3. Seller từ funnel chỉ tạo khoảng 5% GMV của sàn; kênh nhỏ (Email 6 seller, Other 2 seller) bị gắn cảnh báo mẫu nhỏ; GMV/seller cao nhất ở nhóm Unknown (2.526 BRL, 85 seller) nên khi so sánh phải nói cỡ mẫu.

**Ảnh cần chụp:** `4_DB4_trang1_funnel.png`, `4_DB4_trang2_seller.png`, `4_DB4_chi_tiet_seller.png`, `4_DB4_tooltip.png`.

## 8. Việc riêng

### 8.1. Gom bài học của cả nhóm
1. **Nhắc từng người** (Người 1, 2, 3, Phú) gửi 3–5 câu bài học theo đúng khuôn: *vấn đề* (chuyện gì đã xảy ra) → *con số* (đo được bao nhiêu) → *cách xử lý* (đã làm gì, lần sau làm gì).
2. **Gom** vào một bảng, xếp ba nhóm: *chỉ số* (cách đo sai, định nghĩa), *dữ liệu và quy trình* (làm sạch, ETL, thiết kế), *công cụ và làm việc nhóm* (Git, Power BI, Overleaf, phân công).
3. **Bỏ trùng** (hai người cùng nêu "định nghĩa KPI một lần" thì gộp một dòng); **kiểm tra từng con số** với `handoff/` hoặc kỳ vọng ở `DBx.md`; con số không có nguồn thì bỏ hoặc hỏi lại người viết.
4. **Chọn 6–8 bài học** cho slide (nhóm 6 có 3 slide bài học về chỉ số và quy trình cộng tổng kết ba mặt: quy trình, kiến thức, công cụ). Mỗi slide: tiêu đề là câu kết luận ("Một KPI phải có đúng một định nghĩa: GMV hai cách đo lệch 0,1 triệu BRL"), bên dưới vấn đề → con số → xử lý.
5. Kết quả dùng cho chương kết luận (`06-ket-luan.tex` mục *Bài học kinh nghiệm*) và phần `Bài học` trong `4-dashboard.tex` (có `\todo` yêu cầu bổ sung bài học về làm việc nhóm).

### 8.2. Kiểm tra checklist của cả 4 dashboard
1. Mở `huong-dan/dashboards/README.md` (ma trận mục checklist × DB1–DB4) và mục 10 của từng `DBx.md`.
2. Với mỗi file `DBx_<tên>.pbix` (lấy từ `02_Dashboard`): mở từng mục, **thử thật** (bấm drill-down, chuột phải drill-through, di chuột tooltip, xem dự báo) và đánh dấu.
3. Lập bảng đạt / chưa đạt:

| Mục checklist | DB1 | DB2 | DB3 | DB4 | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| Định dạng số | ☐ | ☐ | ☐ | ☐ | |
| Tiêu đề dạng câu hỏi | ☐ | ☐ | ☐ | ☐ | |
| Màu đỏ chỉ để cảnh báo | ☐ | ☐ | ☐ | ☐ | |
| Định dạng có điều kiện | ☐ | ☐ | ☐ | ☐ | |
| Slicer phân cấp | ☐ | ☐ | ☐ | ☐ | |
| OLAP drill-down / roll-up | ☐ | ☐ | ☐ | ☐ | |
| Drill-through | – | – | ☐ | ☐ | |
| Tooltip | ☐ | ☐ | ☐ | ☐ | |
| Chuỗi thời gian có dự báo | ☐ | – | – | – | |
| Key Influencers | – | ☐ | – | – | |
| Publish web và mã QR | ☐ | ☐ | ☐ | ☐ | |
| Số liệu khớp bảng kỳ vọng (mục 9) | ☐ | ☐ | ☐ | ☐ | |

4. Mục chưa đạt: báo người dựng dashboard đó để sửa. Cập nhật bảng "Thống kê bộ dashboard" ở báo cáo 4.1.5 bằng số thật (số trang, visual, slicer, measure đếm trong từng file `.pbix`).

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này:

<!-- QA:33,34,36,37,38 -->
**Q33. Vì sao tỷ lệ đúng hạn cao (93,2%) mà review vẫn tệ ở đơn trễ?**
Trễ chỉ chiếm 6,8% đơn nhưng tác động rất mạnh: điểm review 4,29 (giao sớm) → 3,29 (trễ 1–3 ngày) → 2,10 (4–7 ngày) → 1,70 (trên 7 ngày) (số ở kho tính trên từng review: 1.756 review ở nhóm 4–7 ngày; bản EDA `handoff/correlations.md` tính mỗi đơn một lần, 1.748 đơn, nên ra 2,11; nhóm giao sớm 4,29 và nhóm trễ trên 7 ngày 1,70 giống nhau ở cả hai cách tính); 79,2% review tiêu cực ở nhóm trễ trên 7 ngày. Các đơn trễ chiếm 6,5% số review nhưng tạo ra 27,4% số review tiêu cực (4.000/14.575). Trung bình toàn sàn che mất nhóm nhỏ nhưng "đau".

**Q34. Ngày hứa giao so với thực tế cho thấy điều gì?**
Olist hứa trung bình 24,4 ngày nhưng giao thực tế 12,6 ngày: giao sớm hơn lời hứa 11,8 ngày; 91,9% đơn giao sớm hơn dự kiến. Ngày dự kiến quá rộng nên "đúng hạn" dễ đạt; vì vậy dashboard DB2 thêm KPI so sánh số ngày hứa với số ngày thực tế.

**Q36. Role-playing date trong Power BI làm thế nào?**
Mỗi fact có một quan hệ ngày Active (ví dụ ngày mua) và các quan hệ Inactive; muốn tính theo ngày giao, dùng `CALCULATE([Delivered orders], USERELATIONSHIP(fact_order_fulfillment[delivered_date_key], dim_date[date_key]))`. Tránh ambiguous path và vẫn dùng một bảng ngày.

**Q37. Làm sao bảo đảm số trên dashboard đúng?**
Mọi measure có **giá trị kỳ vọng tính bằng SQL** trong `powerbi/measures.md` cho 4 phạm vi thời gian (ví dụ GMV toàn bộ 13.494.400,74; Orders 98.199; AOV 137,42). Người dựng đối chiếu từng measure; số lệch thì sửa measure hoặc quan hệ.

**Q38. Những giới hạn của dự án?**
(1) Nạp tăng dần chỉ mô phỏng bản ghi mới với trạng thái cuối, không có đơn đổi trạng thái giữa chừng; (2) cơ chế thử lại mồ côi mới chứng minh bằng test; (3) toạ độ theo mã bưu chính (không phải địa chỉ), haversine là đường chim bay (sai số ≤ 0,5%); (4) dữ liệu 2016 và cuối 2018 thưa; (5) chỉ 45,1% deal có đơn nên so sánh theo kênh nhỏ (kênh Email chỉ 6 seller có đơn, đánh dấu mẫu nhỏ); (6) benchmark gọn trên một laptop.
<!-- /QA -->

Câu mới (dashboard và bài học):

**Q-D1. Vì sao chỉ 4 dashboard?**
Mỗi dashboard thuộc một loại mà môn học yêu cầu và trả lời một nhóm câu hỏi: DB1 theo dòng thời gian có dự báo, DB2 vận hành và thống kê (Key Influencers), DB3 OLAP (drill-down, drill-through), DB4 vận hành funnel. Bộ ban đầu có 7 dashboard; nhóm gộp lại để mỗi dashboard sâu hơn và đủ checklist. Giám sát ETL chuyển thành bảng ở mục 3.3.

**Q-D2. Drill-down, drill-through và tooltip khác nhau thế nào?**
Drill-down đi xuống một cấp trong phân cấp ngay trên visual (Vùng → Bang → Thành phố). Drill-through chuyển sang một trang khác chi tiết hơn, giữ bộ lọc (DB3: chi tiết bang; DB4: chi tiết seller). Tooltip là trang nhỏ hiện khi di chuột.

**Q-D3. Dự báo có đáng tin không?**
Chỉ để thấy hướng đi: dữ liệu có 20 tháng, chưa đủ hai chu kỳ năm để kết luận mùa vụ; nhóm ghi chú cạnh biểu đồ và dùng khoảng tin cậy 95%.

**Q-D4. Màu đỏ dùng khi nào?**
Chỉ để cảnh báo qua định dạng có điều kiện (On-time rate dưới 90%, Cancel rate trên 2%, Freight ratio trên 25%, `late_rate_pct` trên 10%); bảng màu dữ liệu của chủ đề không có đỏ nên đỏ luôn có nghĩa là xấu.

**Q-D5. Publish to web công khai có an toàn không?**
Ai có link đều xem được. Dữ liệu Olist là dữ liệu công khai nên chấp nhận; không đưa dữ liệu thật của người khác lên. Nếu tài khoản bị tắt mục này, phương án dự phòng là xuất PDF/PowerPoint và chụp ảnh.

**Q-D6. Vì sao DB4 phải ghi cỡ mẫu?**
Kênh Email chỉ có 6 seller có đơn và Other 2 seller; so sánh GMV/seller giữa nhóm 85 seller và nhóm 2 seller dễ gây hiểu nhầm. Measure `Small sample warning` hiện cảnh báo khi dưới 30 seller.

**Q-D7. Bài học quan trọng nhất của nhóm?**
Một KPI phải có đúng một định nghĩa: GMV có hai cách đo (13,49 và 13,59 triệu BRL); "review đúng hạn" ban đầu ra 4,21 vì tính cả đơn chưa giao, sửa thành 4,29. Và không xoá âm thầm dữ liệu: 42 dòng toạ độ ngoài Brazil bị loại đều có lý do trong nhật ký.

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Viết dựa trên slide của mình. Số trang hiện tại: <!-- PAGES:4.1 -->mục 4.1: trang 67–79 (13 trang)<!-- /PAGES -->.

Các `\todo` hiện có (đếm từ mã nguồn; phần lớn là chèn ảnh chụp dashboard thay khung trống và kiểm tra nhận xét):

<!-- TODOS:4-dashboard.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/4-dashboard.tex` | 20 | 1. Chèn ảnh chụp DB1 trang 1 (xuất PNG từ Power BI, đặt tên 4_DB1_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB1.md mục 3–6).<br>2. Nhóm kiểm tra các nhận xét của DB1 trang 1 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>3. Chèn ảnh chụp DB1 trang 2 (xuất PNG từ Power BI, đặt tên 4_DB1_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB1.md mục 3–6).<br>4. Nhóm kiểm tra các nhận xét của DB1 trang 2 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>5. Dự báo trên Power BI chỉ để thấy hướng đi vì dữ liệu chỉ có 20 tháng; ghi chú cạnh biểu đồ, không kết luận mùa vụ theo năm (mục sec:mua-vu).<br>6. Chèn ảnh chụp DB2 trang 1 (xuất PNG từ Power BI, đặt tên 4_DB2_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB2.md mục 3–6).<br>7. Nhóm kiểm tra các nhận xét của DB2 trang 1 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>8. Chèn ảnh chụp DB2 trang 2 (xuất PNG từ Power BI, đặt tên 4_DB2_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB2.md mục 3–6).<br>9. Nhóm kiểm tra các nhận xét của DB2 trang 2 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>10. Người 2 dựng trang Key Influencers theo powerbi/model.md mục 8 (cột tính toán LOOKUPVALUE), ghi lại các yếu tố đứng đầu mà visual trả về và so với kỳ vọng ở trên.<br>11. Chèn ảnh chụp DB3 trang 1 (xuất PNG từ Power BI, đặt tên 4_DB3_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB3.md mục 3–6).<br>12. Nhóm kiểm tra các nhận xét của DB3 trang 1 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>13. Người 3 dựng trang drill-through và tooltip, chụp ảnh thao tác drill-down vùng đến thành phố.<br>14. Chèn ảnh chụp DB4 trang 1–2 (xuất PNG từ Power BI, đặt tên 4_DB4_….png) thay cho khung trống; mô tả bố cục, slicer, định dạng có điều kiện đã dùng (xem huong-dan/dashboards/DB4.md mục 3–6).<br>15. Nhóm kiểm tra các nhận xét của DB4 trang 1–2 trên dashboard thực tế rồi viết lại bằng lời của nhóm.<br>16. Người 4 dựng trang drill-through chi tiết seller và chụp ảnh.<br>17. Nhóm cập nhật bảng thống kê bằng số thật sau khi dựng xong trên Power BI (số trang, số biểu đồ, số slicer, số measure) và liệt kê các loại biểu đồ đã dùng.<br>18. Nhóm đánh dấu từng mục checklist (mục 10 của DB*.md) sau khi dựng dashboard trên Power BI, chụp ảnh drill-through, tooltip, Key Influencers và đường dự báo.<br>19. Nhóm publish báo cáo, dán link và đặt mã QR vào figures/4_qr_dashboard.png (cũng đặt vào slide cuối).<br>20. Nhóm bổ sung bài học về làm việc nhóm, công cụ (Git, Power BI) và khó khăn thực tế khi dựng dashboard; viết lại các ý trên bằng lời của nhóm. |
| **Tổng** | **20** | |
<!-- /TODOS -->

## 11. Checklist trước khi nộp

| Việc | Xong |
| --- | --- |
| Sơ đồ bản đồ bộ dashboard vẽ bằng draw.io, nộp `03_drawio` | ☐ |
| Bản nháp `03-dashboard.tex` (thêm D1–D8; khung chờ giữ lại nếu chưa có ảnh) | ☐ |
| Bản đầu DB4; nhận ảnh `4_DB1…DB3_*.png` và 3–5 câu nhận xét của Người 1, 2, 3 | ☐ |
| Nhận bài học từ mọi người; gom và chọn 6–8 bài học | ☐ |
| Slide và DB4 xong; kiểm tra checklist 4 dashboard; thay mọi khung chờ bằng ảnh; nộp `.tex` và hình vào `04_Docs/tex-nop/` | ☐ |
| Tập (gồm demo trực tiếp và phương án dự phòng nếu mất mạng: ảnh chụp), bấm giờ, tổng duyệt | ☐ |

Trước khi nộp slide: không còn khung đỏ `CHÈN ẢNH CHỤP` (tìm `khungchen`); ảnh đúng tên `4_DBx_<mô-tả>.png`; mỗi slide dashboard có tiêu đề là câu kết luận có số khớp bảng kỳ vọng; mỗi slide có `\muc{...}`; biên dịch bằng `thu-mot-phan.tex` không lỗi.

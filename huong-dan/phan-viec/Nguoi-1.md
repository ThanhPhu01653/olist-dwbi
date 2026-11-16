# Người 1 – Nghiệp vụ, yêu cầu, KPI và dashboard DB1

Chung cho cả nhóm (Drive, Power BI, Overleaf, draw.io, cách hỏi Phú): [`README.md`](README.md). File này chỉ nói phần của Người 1.

## 1. Phần của bạn

| Hạng mục | Nội dung |
| --- | --- |
| Mục barem (báo cáo / slide) | Ch.1 lý thuyết rút gọn · **2.1 Nghiệp vụ** · **2.2 Yêu cầu** · **2.3 KPI và cây phân tích** |
| File slide | `slides/sections/01a-nghiep-vu-yeu-cau.tex` (2.1–2.3). Hai frame lý thuyết rút gọn nằm trong `00-mo-dau.tex` (nhãn `Mở đầu · lý thuyết rút gọn`): sửa đúng hai frame đó và báo Phú, vì file có hai người cùng sửa |
| Sơ đồ draw.io | `3-2-1_bpmn_don_hang.png`, `3-2-2_bpmn_thu_hut_seller.png` |
| Dashboard | **DB1 Tổng quan và doanh thu** (theo dòng thời gian, có dự báo) |
| Thuyết trình | khảo sát 2.1–2.3; giả định **khoảng 7 phút, 6–7 slide nói** (thời lượng chính thức chưa có, xem `README.md` mục 2) |
| Báo cáo (giai đoạn 2) | `01-tong-quan-ly-thuyet.tex`, `2-1-nghiep-vu.tex`, `2-2-yeu-cau.tex`, `2-3-kpi.tex` |

## 2. Barem chấm gì ở phần này

Các dòng thầy kiểm tra (trích từ bảng nhận xét mẫu của thầy; dòng đỏ là chỗ nhóm khác bị trừ điểm):

**Khảo sát – Nghiệp vụ**
- Quy trình cho bài toán: khảo sát lĩnh vực, có quy trình và đề xuất cho hệ thống mới.
- Liên kết: dashboard sẽ phân tích ở đâu trên quy trình.
- Các chỉ số, khía cạnh cần quan tâm tại các bước trên quy trình.
- Mô hình kinh doanh; liên kết dashboard sẽ phân tích ở đâu trên mô hình kinh doanh.
- Cây nghiệp vụ.

**Khảo sát – Yêu cầu**
- Yêu cầu phân tích tổng thể: mô tả theo các chủ điểm; minh hoạ bằng mindmap.
- Yêu cầu phân tích chi tiết: cây phân tích dashboard.

**Dashboard (liên quan DB1):** đơn vị tính và định dạng số (12.39% → 12%; 12K → 12.3K); định dạng có điều kiện cảnh báo bằng DAX; phân tích theo dòng thời gian để thấy mùa, xu thế và dự báo.

Đối chiếu với nhóm 6 (`docs/doi-chieu-nhom6.md`, thang 5):

| Mục | Nhóm 6 | Nhóm 6 làm gì | Mình làm hơn / cần làm |
| --- | ---: | --- | --- |
| Quy trình nghiệp vụ (slide 4–14) | 5 | 4 quy trình, mỗi quy trình con một trang BPMN; bảng điểm phân tích (bước → dashboard → KPI → khía cạnh); cây nghiệp vụ; Business Model Canvas; bảng nối khối Canvas → câu hỏi → chỉ số → dashboard | đã có 2 BPMN, Canvas, cây nghiệp vụ, bảng A1–A11 và bảng Canvas → dashboard trỏ tới DB1–DB4. **Cần làm:** tách mỗi quy trình con thành một trang; đánh dấu A1… ngay trên hình BPMN |
| Requirement (slide 15–22) | 4,5 | hiện trạng → yêu cầu cải tiến (chức năng và phi chức năng); đối tượng × câu hỏi × dashboard × tần suất; bảng chủ điểm – khía cạnh – chỉ số; cây yêu cầu; cây phân tích từng dashboard; trang lưu ý giới hạn dữ liệu | đã có cây yêu cầu, 4 cây phân tích, bảng KPI. **Cần làm:** yêu cầu phi chức năng; trang giới hạn dữ liệu dạng vấn đề → cách xử lý |

Hạn chế của nhóm 6 ở dashboard (3,5 điểm, thấp nhất): thiếu checklist (định dạng số, OLAP, dự báo, drill-through, tooltip). Với DB1, phần **dự báo** và **định dạng số** là chỗ ghi điểm.

Không được chép câu chữ, số liệu hay hình của nhóm 6; chỉ học cách trình bày.

## 3. Kiến thức cần nắm

**Quy trình nghiệp vụ và BPMN.** BPMN là sơ đồ ký hiệu chuẩn mô tả các bước của một quy trình, ai làm bước nào, bước nào sinh dữ liệu. Olist có hai quy trình trong bài toán:
- *Xử lý đơn:* đặt hàng và thanh toán → duyệt thanh toán (trung bình 10,3 giờ) → seller chuẩn bị và bàn giao cho vận chuyển (2,9 ngày) → vận chuyển và giao (9,3 ngày) → khách đánh giá; nhánh hủy hoặc không khả dụng (1.234 đơn, 1,24%).
- *Thu hút seller:* khách tiềm năng để lại thông tin (MQL) → SDR sàng lọc, SR tư vấn → chốt thương vụ → seller bán đơn đầu tiên.
Mỗi mốc thời gian của quy trình là một cột trong kho và kho biến hiệu hai mốc thành chỉ số (lead time 12,6 ngày). Vì vậy BPMN không chỉ vẽ cho đẹp: **các điểm thu thập dữ liệu** và **điểm phân tích A1–A11** phải nằm ngay trên hình.

**Business Model Canvas (BMC).** Bảng 9 ô mô tả cách doanh nghiệp tạo giá trị: phân khúc khách hàng, giá trị đề xuất, kênh, quan hệ khách hàng, dòng doanh thu, nguồn lực, hoạt động, đối tác, cấu trúc chi phí. Với Olist: giá trị đề xuất là "một hợp đồng, nhiều sàn" cho seller nhỏ. Thầy muốn thấy **mỗi ô dẫn tới một câu hỏi quản trị, một chỉ số và một dashboard** (`huong-dan/05-nghiep-vu-nhap.md` mục 9). Lưu ý nói thẳng: dữ liệu không có doanh thu hay chi phí marketing của Olist, nên ô dòng doanh thu và cấu trúc chi phí chỉ dùng GMV và phí vận chuyển (16,6% giá hàng) làm chỉ số thay thế.

**Cây nghiệp vụ và cây yêu cầu.** Cây nghiệp vụ gom hoạt động của doanh nghiệp thành nhóm (Olist: 5 nhóm). Cây yêu cầu đi từ chủ điểm (6 chủ điểm: bán hàng, xử lý đơn, thanh toán, trải nghiệm khách, seller, thu hút seller) xuống câu hỏi cụ thể rồi xuống chiều cần phân tích (thời gian, địa lý, sản phẩm…). **Cây phân tích từng dashboard** đi từ mục tiêu → câu hỏi → KPI → chiều.

**KPI và định nghĩa duy nhất.** Mỗi KPI có đúng một định nghĩa DAX (bảng KPI 19 chỉ số, `powerbi/measures.md`):
- **GMV** = tổng giá hàng của đơn không thuộc nhóm *Failed* (canceled và unavailable) = 13.494.400,74 BRL; tổng giá hàng mọi đơn là 13,59 triệu, hai con số này khác nhau có chủ ý.
- **Orders** (đơn có doanh thu) = 98.199, khác **Orders placed** (mọi đơn đã đặt) = 99.441.
- **AOV** = GMV ÷ Orders = 137,42 BRL. **Freight ratio** = phí vận chuyển ÷ giá hàng = 16,6%.
- **MoM** (so với tháng trước) và **YoY** (so với cùng kỳ năm trước): tháng 11/2017 tăng 52,1% so với 10/2017 (Black Friday 24/11/2017); tháng 8/2018 tăng 49,4% so với 8/2017.
- **On-time rate** 93,2% nhưng Olist hứa trung bình 24,4 ngày và giao 12,6 ngày: ngày dự kiến quá rộng nên cần thêm KPI *Promised vs actual* (11,8 ngày).
- **Funnel:** 8.000 MQL → 842 deal đã chốt (10,5%) → 379 seller có đơn bán được (45,0% số deal chốt); 462 deal chưa bán gì (bản khám phá dữ liệu đếm 380 seller vì tính cả đơn bị hủy; kho đếm 379 vì chỉ tính đơn không thuộc *Failed*).

**Giới hạn dữ liệu.** Nói trước giới hạn để KPI không bị hiểu sai: dữ liệu 2016 chỉ 329 đơn và tháng 09–10/2018 chỉ 20 đơn, nên so sánh theo thời gian chỉ dùng cửa sổ 2017-01 → 2018-08 (99,6% số đơn); một đơn có thể có nhiều review; so sánh theo kênh có cỡ mẫu nhỏ.

**Chuỗi thời gian và dự báo (DB1).** Biểu đồ đường GMV theo tháng, thêm đường cùng kỳ năm trước và dự báo 3 điểm (Analytics → Forecast, tin cậy 95%). Dữ liệu chỉ 20 tháng nên dự báo chỉ để thấy hướng đi, không kết luận mùa vụ theo năm (báo cáo mục 3.1).

## 4. Số liệu và hình có sẵn

| Số liệu | Giá trị | Nguồn |
| --- | --- | --- |
| Quy mô | 3.095 seller, 99.441 đơn, GMV 13,49 triệu BRL | `handoff/00-TONG-QUAN.md` mục 5 |
| Xử lý đơn | duyệt 10,3 giờ; bàn giao 2,9 ngày; vận chuyển 9,3 ngày; lead time 12,6 ngày; hủy 1,24% | `huong-dan/dashboards/DB2.md` mục 8–9 |
| Funnel | 8.000 MQL → 842 (10,5%) → 379 (45,0%); chốt TB 48,5 ngày; đến đơn đầu 51,9 ngày | `huong-dan/dashboards/DB4.md` mục 8–9; `handoff/funnel.md` |
| Điểm phân tích | A1–A11 (bước → dashboard → KPI → khía cạnh) | `huong-dan/05-nghiep-vu-nhap.md` mục 8 |
| Canvas → dashboard | 9 khối, mỗi khối một câu hỏi, chỉ số, dashboard | `huong-dan/05-nghiep-vu-nhap.md` mục 9 |
| Hiện trạng → cải tiến | 8 cặp | `huong-dan/05-nghiep-vu-nhap.md` mục 10 |
| Đối tượng dùng, chủ điểm | 6 nhóm người dùng; bảng chủ điểm – khía cạnh – chỉ số | `huong-dan/05-nghiep-vu-nhap.md` mục 11–12 |
| Giới hạn dữ liệu | 5 giới hạn | `huong-dan/05-nghiep-vu-nhap.md` mục 13 |
| KPI | 19 chỉ số, DAX, giá trị kỳ vọng | `powerbi/measures.md` |

Hình: `figures/3-2-1_bpmn_don_hang.png`, `3-2-2_bpmn_thu_hut_seller.png`, `3-2-3_business_model_canvas.png`, `3-2-5_cay_nghiep_vu.png`, `3-2-6_cay_yeu_cau_phan_tich.png`, `2-3_cay_phan_tich_DB1.png` … `DB4.png` (đều là bản nháp, bạn vẽ lại/chỉnh).

## 5. Danh sách slide đề xuất

**Các slide đang có trong `01a-nghiep-vu-yeu-cau.tex`** (bảng dưới do script đọc từ file `.tex`; nội dung chính rút từ các gạch đầu dòng của frame):

<!-- SLIDES:01a-nghiep-vu-yeu-cau.tex -->
| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 13 | Olist kết nối người bán nhỏ với các sàn lớn: 3.095 seller bán 99.441 đơn trong 2 năm | Dữ liệu Brazil, 09/2016–10/2018; hai bộ Kaggle | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: ảnh/logo Olist |
| 2 | 14 | Mô hình kinh doanh hai phía: seller được thu hút, người mua mua qua sàn | Business Model Canvas 9 ô (bản nháp) | `3-2-3_business_model_canvas.png` | đã có, nhóm xác nhận |
| 3 | 15 | Giá trị đề xuất: một hợp đồng, nhiều sàn; dữ liệu cho thấy phí vận chuyển bằng 16,6% giá hàng | Giá trị cho seller và cho người mua; chi phí chính là vận chuyển và hậu cần | `3-2-3_business_model_canvas.png` | đã có |
| 4 | 16 | Bài toán: hiểu hiệu suất đơn hàng và hiệu quả thu hút seller từ hai hệ thống rời nhau | Hai hệ thống chỉ gặp nhau ở seller_id | `3-2-4_erd_oltp.png` | đã có |
| 5 | 17 | Sáu nhóm câu hỏi phân tích bao trùm bán hàng, vận hành, khách hàng và thu hút seller | Bán hàng xử lý đơn thanh toán trải nghiệm khách seller thu hút seller | `3-2-6_cay_yeu_cau_phan_tich.png` | đã có |
| 6 | 18 | Kho phục vụ hai quy trình nghiệp vụ: xử lý đơn và thu hút seller | Chung chiều seller và ngày | `3-3-4_constellation.png` | đã có |
| 7 | 19 | Đơn hàng đi qua bốn mốc thời gian và có thể bị hủy hoặc không khả dụng | Đặt → duyệt → bàn giao vận chuyển → giao → đánh giá; 1.234 đơn Failed (1,24%) | `3-2-1_bpmn_don_hang.png` | đã có |
| 8 | 20 | Mỗi mốc của quy trình là một cột thời gian mà kho biến thành chỉ số | approval_hours 10,3 giờ handling_days 2,9 ngày transit_days 9,3 ngày lead_days 12,6 ngày | bảng | đã có |
| 9 | 21 | Kho thu thập dữ liệu ở bảy điểm của quy trình đơn hàng | Ô vàng trên BPMN: đặt, duyệt, bàn giao, giao, đánh giá, hủy, thanh toán | `3-2-1_bpmn_don_hang.png` | đã có |
| 10 | 22 | Quy trình thu hút seller đi từ MQL đến seller có đơn, trung bình mất 100 ngày | Liên hệ → chốt (TB 48,5 ngày) → đơn đầu (TB 51,9 ngày) | `3-2-2_bpmn_thu_hut_seller.png` | đã có |
| 11 | 23 | Phễu thu hút: 8.000 MQL → 842 deal (10,5%) → 379 seller có đơn bán được (45,0% số deal) | 462 deal đã chốt nhưng chưa bán gì | `3-3-1_funnel_seller_overlap.png` | đã có |
| 12 | 24 | Cây nghiệp vụ gom hoạt động của Olist thành năm nhóm | Thu hút seller quản lý đơn hàng chăm sóc khách quản lý seller quản trị dữ liệu | `3-2-5_cay_nghiep_vu.png` | đã có |
| 13 | 122 | Mười một điểm phân tích A1–A11 gắn mỗi bước của quy trình với dashboard và KPI | A1–A6 trên quy trình đơn: đặt hàng và thanh toán, duyệt, bàn giao, giao hàng, đánh giá, hủy; A7–A10 trên quy trình seller: MQL, SDR và SR, chốt deal,  | – | đã có |
| 14 | 123 | Mỗi khối Business Model Canvas dẫn tới một câu hỏi quản trị, một chỉ số và một dashboard | Giá trị đề xuất → giao đúng hạn và đủ rẻ? → On-time rate, Freight ratio 16,6% → DB2, DB3; Kênh → kênh nào đưa về seller chốt được? → MQL to won rate → | – | đã có |
| 15 | 25 | Cây yêu cầu phân tích đi từ sáu chủ điểm đến các câu hỏi cụ thể | Chủ điểm → câu hỏi → chiều cần quan tâm | `3-2-6_cay_yeu_cau_phan_tich.png` | đã có |
| 16 | 26 | Bán hàng: GMV cần tăng trưởng MoM, YoY và quy luật 80/20 | GMV 13,49 triệu BRL; AOV 137,42 BRL | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng chủ điểm bán hàng (3.2.2) |
| 17 | 27 | Xử lý đơn: không chỉ hỏi "đúng hạn không" mà hỏi "hứa so với thực tế chênh bao nhiêu" | Đúng hạn 93,2% nhưng hứa 24,4 ngày, thực tế 12,6 ngày | khung chờ | cần ảnh: CHÈN HÌNH / BẢNG: bảng chủ điểm xử lý đơn |
| 18 | 28 | Trải nghiệm khách: giao trễ là yếu tố kéo điểm review xuống mạnh nhất | Điểm 4,29 khi giao sớm, 1,70 khi trễ trên 7 ngày | `3-3-1_delay_vs_review.png` | đã có |
| 19 | 29 | Thu hút seller: câu hỏi là kênh nào chuyển đổi tốt và seller từ funnel bán ra sao | Tỷ lệ chốt theo kênh từ 2,7% đến 16,7% | `3-3-1_funnel_win_rate_by_origin.png` | đã có |
| 20 | 124 | Tám điểm hiện trạng của hệ thống nguồn dẫn tới tám yêu cầu cải tiến cho kho dữ liệu | Hai hệ thống rời nhau, chỉ gặp qua seller_id → chiều dùng chung dim_seller; Trạng thái đơn không có lịch sử mốc → snapshot tích luỹ 5 mốc | – | đã có |
| 21 | 125 | Sáu nhóm người dùng, mỗi nhóm có câu hỏi, dashboard và tần suất xem riêng | Ban điều hành → DB1 (hằng tuần, hằng tháng); quản lý kinh doanh → DB1; Vận hành và logistics → DB2, DB3 (hằng ngày đến hằng tuần); chăm sóc khách hàng | – | đã có |
| 22 | 30 | Bảng KPI chính gồm 19 chỉ số, mỗi chỉ số có một định nghĩa DAX duy nhất | GMV, Orders, AOV, on-time, lead time, review, repeat, MQL→seller... | bảng | đã có |
| 23 | 31 | Bốn dashboard có bốn cây phân tích từ mục tiêu đến chỉ số và chiều | Bốn cây phân tích DB1–DB4 | `2-3_cay_phan_tich_DB1.png`, `2-3_cay_phan_tich_DB2.png`, `2-3_cay_phan_tich_DB3.png`, `2-3_cay_phan_tich_DB4.png` | đã có |
| 24 | 126 | Năm giới hạn của dữ liệu làm một KPI có hai con số: GMV 13,49 so với 13,59 triệu BRL | GMV loại đơn Failed 13.494.400,74; tổng giá hàng mọi đơn 13.591.643,70 BRL; Orders 98.199 so với Orders placed 99.441 (chênh 1.242 đơn); 380 so với 37 | – | đã có |

*24 frame trong `01a-nghiep-vu-yeu-cau.tex` (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*
<!-- /SLIDES -->

**Slide cần thêm** (theo `docs/doi-chieu-nhom6.md`). Số trong tiêu đề lấy từ `huong-dan/dashboards/DB2.md`, `DB4.md` và `huong-dan/05-nghiep-vu-nhap.md`; số chưa có nguồn đánh dấu *nhóm bổ sung*.

| STT mới | Tiêu đề đề xuất (câu kết luận có số) | Nội dung chính | Hình / bảng | Nguồn số liệu | Trạng thái |
| ---: | --- | --- | --- | --- | --- |
| N1 | Đặt hàng và thanh toán (A1): 103.886 lần thanh toán cho 99.441 đơn, thẻ tín dụng chiếm 78,3% giá trị | bước đầu của quy trình đơn; chỉ số GMV, Orders, AOV, cơ cấu thanh toán | BPMN cắt riêng bước này, dấu A1 | `DB2.md` mục 8 (ý 8); `handoff/00-TONG-QUAN.md` | cần làm |
| N2 | Duyệt và bàn giao (A2–A3): duyệt trung bình 10,3 giờ, seller bàn giao sau 2,9 ngày | hai bước đầu tiên do hệ thống và seller làm; 1.359 đơn bàn giao trước khi duyệt được gắn cờ | BPMN riêng bước này, dấu A2, A3 | `DB2.md` mục 8 (ý 2, ghi chú) | cần làm |
| N3 | Giao hàng và đánh giá (A4–A6): vận chuyển 9,3 ngày, review 4,09, hủy 1,24% | bước dài nhất và bước tạo điểm review | BPMN riêng bước này, dấu A4–A6 | `DB2.md` mục 8–9 | cần làm |
| N4 | Yêu cầu phi chức năng: làm mới hằng ngày, truy vấn mart nhanh, ẩn dữ liệu định danh | thời gian làm mới (lô hằng ngày, xem S127), thời gian phản hồi (materialized view làm mới 2 giây, xem S84), ẩn dữ liệu định danh | bảng yêu cầu | `handoff/2026-11-05-P6.md`, `P7-perf.md`; phần ẩn định danh: *nhóm bổ sung* | cần làm |
| N5 | Năm giới hạn của dữ liệu: vấn đề → cách xử lý (sửa slide S126) | GMV hai cách đo (13,49 so với 13,59 triệu BRL); Orders 98.199 so với Orders placed 99.441; 380 so với 379 seller; 2016 thưa và 09/2018 bị cắt; đơn có nhiều review | bảng vấn đề → cách xử lý | `huong-dan/05-nghiep-vu-nhap.md` mục 13 | sửa slide có sẵn |
| N6 | DB1 trang 1: GMV tăng 52,1% ở 11/2017 và có đường dự báo 3 tháng | tình huống trước dashboard: ban điều hành cần biết doanh thu tăng hay giảm | ảnh `4_DB1_trang1_tong_quan.png` (gửi Người 4 dùng ở `03-dashboard.tex`) | `DB1.md` mục 8 | gửi ảnh và 3–5 câu cho Người 4 hạn 25/11 |

Khối lượng: 24 slide đang có + 5 slide thêm (N1–N5) = **29 slide** trong file của bạn, cộng 2 slide lý thuyết ở phần mở đầu. **Chọn 6–7 slide để nói** trong khoảng 7 phút, còn lại là slide chi tiết để trả lời câu hỏi và để báo cáo dùng lại:

| Thứ tự nói | Slide (cột S) | Ý chính |
| ---: | --- | --- |
| 1 | S16 | Bài toán: hai hệ thống nguồn rời nhau, chỉ gặp nhau ở `seller_id` |
| 2 | S19 và N1–N3 | Quy trình xử lý đơn trên BPMN, điểm A1–A6 |
| 3 | S22, S23 | Quy trình thu hút seller và phễu 8.000 → 842 → 379 |
| 4 | S122, S123 | A1–A11 và Canvas → dashboard: dashboard phân tích ở đâu |
| 5 | S124, N4 | Hiện trạng → yêu cầu cải tiến; yêu cầu phi chức năng |
| 6 | S31, S126 | 4 cây phân tích và 5 giới hạn dữ liệu |

## 6. Sơ đồ draw.io

Quy ước chung (màu, font, xuất PNG): `README.md` mục 6. Nộp `.drawio` và PNG vào `03_drawio`.

**`3-2-1_bpmn_don_hang.png` (quy trình xử lý đơn)**
- Phải thể hiện: các bước đặt hàng và thanh toán → duyệt → bàn giao → giao → đánh giá, nhánh hủy; ai làm bước nào (khách, Olist, seller, đơn vị vận chuyển); **điểm thu thập dữ liệu** (ô vàng) và **các điểm phân tích A1–A6** gắn đúng bước, mỗi điểm ghi dashboard và KPI.
- Bản nháp: `figures/3-2-1_bpmn_don_hang.png` (nguồn `huong-dan/05-nghiep-vu-nhap.md` mục 1; sơ đồ Mermaid trong file đó).
- Quy ước: dùng đúng ký hiệu BPMN (sự kiện bắt đầu và kết thúc, tác vụ, cổng quyết định, làn bơi theo vai trò); nhóm 6 tách mỗi quy trình con thành một trang, mình xuất thêm các hình cắt riêng cho N1–N3.
- Lỗi thầy hay bắt: quy trình không liên kết với dashboard ("dashboard sẽ phân tích ở đâu trên quy trình"); không nêu chỉ số và khía cạnh tại từng bước.

**`3-2-2_bpmn_thu_hut_seller.png` (quy trình thu hút seller)**
- Phải thể hiện: MQL → SDR sàng lọc → SR tư vấn → chốt thương vụ → seller bán đơn đầu tiên; điểm A7–A10.
- Bản nháp: `figures/3-2-2_bpmn_thu_hut_seller.png`; mục 2 của `huong-dan/05-nghiep-vu-nhap.md`.
- Lỗi thầy hay bắt: như trên; thêm: đề xuất cho hệ thống mới (nối funnel với bán hàng qua `dim_seller`).

Ngoài hai sơ đồ draw.io, các hình `3-2-3_business_model_canvas.png`, `3-2-5_cay_nghiep_vu.png`, `3-2-6_cay_yeu_cau_phan_tich.png` và `2-3_cay_phan_tich_DB1…DB4.png` là bản nháp sinh tự động; vẽ lại nếu muốn thống nhất kiểu trình bày (giữ tên file).

## 7. Dashboard DB1 – Tổng quan và doanh thu

Hướng dẫn đầy đủ: [`../dashboards/DB1.md`](../dashboards/DB1.md). Cách mở file, lưu, Refresh, đối chiếu số, chụp ảnh: `README.md` mục 4.

**Câu hỏi trả lời:** doanh thu bao nhiêu, tăng hay giảm so với tháng trước và cùng kỳ năm trước; giao hàng có đúng hạn, tỷ lệ hủy; khách hài lòng không; vùng và nhóm ngành nào đóng góp nhiều; bao nhiêu danh mục tạo 80% GMV (Pareto); AOV và phí vận chuyển theo ngành.

**Các trang:** trang 1 *Tổng quan* (6 thẻ KPI, đường GMV theo tháng có GMV cùng kỳ và dự báo, cột tăng trưởng MoM, cột ngang GMV theo vùng, treemap nhóm ngành, đồng hồ On-time rate); trang 2 *Doanh thu theo sản phẩm* (treemap, Pareto từ `v_category_pareto`, matrix hierarchy Product × quý, scatter AOV – Freight ratio); trang tooltip `Tooltip_Thang`.

**Measure chính** (thư mục `DB1 Tổng quan và doanh thu`): GMV, Orders, AOV, Items, Freight, Freight ratio, GMV last month, GMV MoM %, GMV last year, GMV YoY %, GMV YTD; dùng thêm On-time rate, Avg review, Cancel rate từ thư mục DB2; màu `Color growth`, `Color On-time rate`, `Color Avg review`, `Color Cancel rate`, `Color Freight ratio`.

**Checklist phải đạt** (ma trận chung ở `../dashboards/README.md`): ≥ 4 loại biểu đồ; định dạng số (GMV `13.5M`, Orders `98.2K`, phần trăm 1 chữ số); tiêu đề dạng câu hỏi; màu đỏ chỉ để cảnh báo; định dạng có điều kiện (thẻ, cột tăng trưởng, color scale matrix); slicer phân cấp Năm → Quý → Tháng; OLAP drill-down (đường theo Năm → Quý → Tháng, treemap/matrix Nhóm ngành → Danh mục → Sản phẩm); tooltip; **chuỗi thời gian có dự báo (chỉ DB1 làm)**; publish web và mã QR (Phú làm).

**Các bước dựng:**
1. Mở `olist_base.pbix`, *Save as* `DB1_tong-quan.pbix`; kiểm tra `DataFolder` và Refresh (`README.md` mục 4).
2. Trang 1: đặt bộ lọc trang `dim_date[InWindow] = TRUE`; dựng 6 thẻ, kéo measure từ thư mục DB1; so số với bảng kỳ vọng (GMV 13,449,529.68 và Orders 97,905 trong cửa sổ; 13,494,400.74 và 98,199 toàn bộ).
3. Đường GMV theo `dim_date[year_month]` + `GMV last year`; bật *Analytics → Forecast* (3 điểm, 95%) và ghi chú "dữ liệu 20 tháng, chỉ để thấy hướng đi".
4. Cột `GMV MoM %` tô màu theo `Color growth`; bar chart vùng; treemap nhóm ngành; gauge On-time rate với mục tiêu 95%.
5. Trang 2: treemap, Pareto (cột `gmv`, đường `cum_share_pct`, màu theo `abc_class`), matrix hierarchy Product × `year_quarter`, scatter AOV – Freight ratio.
6. Định dạng có điều kiện: field value theo các measure `Color …`; matrix color scale.
7. Slicer `year` (nút), `region`, `year_quarter`, `category_group`; slicer phân cấp Năm → Quý → Tháng.
8. Tooltip: trang `Tooltip_Thang` (4 thẻ), gán cho đường GMV và cột tăng trưởng.
9. Đối chiếu từng thẻ với mục 9 của `DB1.md`; đánh dấu checklist mục 10.

**Giá trị kỳ vọng để tự kiểm** (cửa sổ 2017-01 → 2018-08): GMV 13,449,529.68; Orders 97,905; AOV 137.37; Freight ratio 16.6%; Cancel rate 1.19%; On-time rate 93.2%; Avg review 4.09. Tháng 2017-11: GMV 1,003,862.14, MoM +52.1%.

**Câu chuyện khi demo (3 điểm, có số):**
1. GMV tăng từ 120.098 BRL (01/2017) lên 1.003.862 BRL (11/2017) nhờ Black Friday (một ngày 152.654 BRL, gấp 5,2 lần ngày thường); từ 03/2018 đi ngang 0,85–0,99 triệu nhưng cao hơn cùng kỳ năm trước (05/2018 +97,3%).
2. Thị trường tập trung: Sudeste 65,4% GMV, Norte 2,5%; 18/74 danh mục tạo 80% GMV.
3. Giao đúng hạn 93,2% nhưng tụt còn 87,6% ở tháng Black Friday: tải cao làm giao chậm.

**Ảnh cần chụp (gửi Người 4 và `02_Dashboard`):** `4_DB1_trang1_tong_quan.png`, `4_DB1_trang2_san_pham.png`, `4_DB1_du_bao.png` (đường GMV có vùng dự báo), `4_DB1_tooltip.png`. Kèm 3–5 câu nhận xét có số cho mỗi ảnh (hạn 25/11).

## 8. Việc riêng
Không có việc riêng ngoài các mục trên. Hai việc dễ bỏ sót: (1) vẽ lại hoặc kiểm tra bốn cây phân tích `2-3_cay_phan_tich_DB1…DB4.png` (báo cáo 2.3 có `\todo` yêu cầu); (2) viết hai slide lý thuyết rút gọn ở phần mở đầu, chỉ giữ phần phục vụ các chương sau (barem không có mục lý thuyết).

## 9. Câu hỏi có thể bị hỏi

Các câu từ `huong-dan/04-cau-hoi-van-dap.md` thuộc phần này:

<!-- QA:1,23,24,35 -->
**Q1. Vì sao chọn chủ đề Order Management và ghép thêm Marketing Funnel?**
Order Management theo Kimball có đủ giao dịch đơn, chu trình xử lý đơn, thanh toán và đánh giá. Ghép thêm Marketing Funnel (8.000 MQL, 842 deal) cho **hai hệ thống nguồn** và một quy trình thứ hai (thu hút seller), nối qua `seller_id`, nên trả lời được câu hỏi xuyên quy trình: seller đến từ kênh nào thì bán tốt. *Xem thêm: `docs/DW_DESIGN.md` mục 1.*

**Q23. GMV khác tổng giá hàng thế nào?**
GMV = Σ `price` của đơn **không** thuộc nhóm Failed (canceled, unavailable) = 13.494.400,74; tổng giá hàng mọi đơn = 13.591.643,70; chênh 97.242,96 là hàng của 1.234 đơn Failed. Dùng GMV làm KPI vì đơn hủy không tạo doanh thu.

**Q24. Vì sao 462 deal đã chốt lại không có đơn?**
Trong 842 deal, chỉ 380 seller (45,1%) có đơn trong hệ thống bán hàng (mọi trạng thái đơn); nếu chỉ tính đơn không thuộc nhóm Failed (huỷ / không có sẵn) thì còn 379 seller (45,0%) có đơn bán được, là số `Sellers with first sale` trên dashboard. Đây là một **kết quả phân tích**, không phải lỗi: các seller này vẫn có dòng trong `dim_seller` (địa chỉ Unknown, `is_from_funnel = true`) và dashboard DB4 hiển thị như một kết quả.

**Q35. Vì sao chọn cửa sổ thời gian 2017-01 → 2018-08?**
Dữ liệu 2016 chỉ 329 đơn và 09–10/2018 chỉ 20 đơn nên xu hướng và MoM/YoY bị méo; cửa sổ này chứa 99,6% số đơn. Cột `InWindow` trong `dim_date` làm bộ lọc trang cho DB1–DB4.
<!-- /QA -->

Câu mới (phần nghiệp vụ, yêu cầu, KPI chưa có trong file hỏi đáp chung):

**Q-N1. Quy trình nghiệp vụ nào kho phục vụ và dashboard phân tích ở đâu trên quy trình?**
Hai quy trình: xử lý đơn và thu hút seller. Mười một điểm phân tích A1–A11 gắn bước của quy trình với dashboard và KPI: ví dụ A2 (duyệt thanh toán, 10,3 giờ) và A4 (giao hàng, lead time 12,6 ngày) ở DB2, A7–A10 (MQL đến đơn đầu tiên) ở DB4. Xem `huong-dan/05-nghiep-vu-nhap.md` mục 8.

**Q-N2. Business Model Canvas giúp gì cho thiết kế kho?**
Mỗi khối Canvas đặt một câu hỏi quản trị và một chỉ số. Ví dụ khối *giá trị đề xuất* hỏi "giao đúng hạn và đủ rẻ?" và dùng On-time rate (93,2%), Freight ratio (16,6%), dẫn tới DB2 và DB3. Dữ liệu không có doanh thu hay chi phí marketing của Olist nên ô doanh thu và chi phí chỉ dùng GMV và phí vận chuyển thay thế.

**Q-N3. Vì sao Orders (98.199) khác Orders placed (99.441)?**
Orders chỉ đếm đơn có doanh thu (loại nhóm *Failed*: 1.234 đơn bị hủy hoặc không khả dụng); Orders placed đếm mọi đơn. Cùng cơ chế làm GMV (13,49 triệu BRL) nhỏ hơn tổng giá hàng của mọi đơn (13,59 triệu). Mỗi KPI có một định nghĩa DAX duy nhất để tránh hai báo cáo cho hai con số.

**Q-N4. Vì sao có 380 seller ở phần khám phá dữ liệu nhưng 379 ở dashboard?**
380 là số seller của funnel có đơn ở mọi trạng thái; trong kho `first_sale_date` chỉ tính đơn không thuộc *Failed* nên ra 379. Dashboard DB4 dùng 379 (`handoff/00-TONG-QUAN.md` mục 6, phát hiện 3).

**Q-N5. Yêu cầu phi chức năng của hệ thống gồm gì?**
Làm mới dữ liệu hằng ngày (lô hằng ngày là đủ vì trung bình 163 đơn mỗi ngày), truy vấn data mart nhanh (materialized view làm mới trong khoảng 2 giây), và ẩn dữ liệu định danh khi publish. Chi tiết phần ẩn định danh: nhóm xác nhận trước khi nói.

**Q-N6. Dự báo trên DB1 đáng tin đến đâu?**
Chỉ để thấy hướng đi: dữ liệu có 20 tháng (2017-01 → 2018-08), chưa đủ hai chu kỳ năm nên không kết luận mùa vụ theo năm (STL ở mục 3.1: xu hướng mạnh 0,73, mùa vụ tuần 0,22).

## 10. Giai đoạn 2 (sau thuyết trình): viết báo cáo

Viết dựa trên slide của mình. Số trang hiện tại: <!-- PAGES:1,2.1,2.2,2.3 -->chương 1: trang 1–4 (4 trang); mục 2.1: trang 5–8 (4 trang); mục 2.2: trang 9–10 (2 trang); mục 2.3: trang 11–13 (3 trang); tổng 13 trang<!-- /PAGES -->. Chương 1 hiện là bản khung; `\todo` yêu cầu viết lại bằng lời của nhóm và rút gọn còn khoảng 10 trang.

Các `\todo` hiện có (đếm từ mã nguồn):

<!-- TODOS:01-tong-quan-ly-thuyet.tex,2-1-nghiep-vu.tex,2-2-yeu-cau.tex,2-3-kpi.tex -->
| File | Số `\todo` | Nội dung các `\todo` |
| --- | ---: | --- |
| `report/chapters/01-tong-quan-ly-thuyet.tex` | 3 | 1. Rút gọn chương này còn khoảng 10 trang (barem không có mục lý thuyết; chỉ giữ phần phục vụ các chương sau).<br>2. Chương 1 chỉ có khung: nhóm tự viết văn bản từ các ý chính bên dưới, trích dẫn nguồn đã đọc. Các trích dẫn dưới đây là gợi ý trong refs.bib; kiểm tra lại trang/phiên bản trước khi dùng. Tham chiếu nội dung môn …<br>3. Chương 2 chỉ có khung: nhóm tự viết văn bản từ các ý chính bên dưới và trích nguồn đã đọc; các mục tương ứng nội dung môn học (chương 6, 8). |
| `report/chapters/2-1-nghiep-vu.tex` | 4 | 1. Viết 2–3 câu về mục tiêu và phạm vi bài toán theo cách của nhóm; thêm 1 đoạn giới thiệu Olist từ nguồn công khai (trích dẫn nguồn đã đọc).<br>2. Nhóm kiểm tra và sửa Business Model Canvas, đặc biệt ô dòng doanh thu và đối tác chính: chỉ có suy luận, cần dẫn chứng từ nguồn công khai về Olist (dữ liệu chỉ có giá hàng và phí vận chuyển, không có doanh thu …<br>3. Nhóm đọc, sửa cho đúng cách hiểu nghiệp vụ và vẽ lại BPMN bằng draw.io (đúng ký hiệu BPMN), giữ nguyên các điểm thu thập dữ liệu. Nguồn nháp: huong-dan/05-nghiep-vu-nhap.md.<br>4. Nhóm kiểm tra các câu hỏi quản trị theo cách hiểu nghiệp vụ của nhóm; nguồn nháp: huong-dan/05-nghiep-vu-nhap.md mục 8, 9. |
| `report/chapters/2-2-yeu-cau.tex` | 1 | 1. Nhóm bổ sung hoặc điều chỉnh yêu cầu phân tích theo cách trình bày trên lớp (theo chủ điểm, khía cạnh, dạng cây). |
| `report/chapters/2-3-kpi.tex` | 1 | 1. Người 1 vẽ lại bốn cây phân tích bằng draw.io nếu muốn thống nhất kiểu trình bày (giữ tên file hình 2-3_cay_phan_tich_DB1 đến DB4); thêm bảng KPI đầy đủ theo định nghĩa trong docs/DW_DESIGN.md mục 9 (công thức,… |
| **Tổng** | **9** | |
<!-- /TODOS -->

## 11. Checklist trước khi nộp và mốc hạn

| Hạn | Việc | Xong |
| --- | --- | --- |
| 23/11 | BPMN vẽ lại bằng draw.io (đúng ký hiệu, có A1–A11, điểm thu thập dữ liệu) và nộp `03_drawio` | ☐ |
| 23/11 | Bản nháp slide `01a-nghiep-vu-yeu-cau.tex` (thêm N1–N5, thay khung đỏ bằng hình) | ☐ |
| 25/11 | Bản đầu DB1; ảnh `4_DB1_*.png` và 3–5 câu nhận xét gửi Người 4 | ☐ |
| 26/11 | 3–5 câu bài học gửi Người 4 (bài học về chỉ số: GMV hai cách đo; về quy trình) | ☐ |
| 27/11 | Slide và DB1 xong; nộp `.tex` và hình mới vào `04_Docs/tex-nop/` | ☐ |
| 28–29/11 | Tập 7 phút, bấm giờ, tổng duyệt | ☐ |

Trước khi nộp slide: không còn khung đỏ `CHÈN HÌNH` (tìm `khungchen` trong file); mọi tiêu đề là câu kết luận có số; mỗi slide có nhãn `\muc{...}`; số trong tiêu đề khớp bảng kỳ vọng; biên dịch bằng `thu-mot-phan.tex` không lỗi.
Trước khi nộp dashboard: mọi mục checklist DB1 (mục 10 của `DB1.md`) đã đánh dấu; số khớp mục 9; ảnh đặt đúng tên.

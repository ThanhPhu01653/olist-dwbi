# Kịch bản slide – xếp theo barem (113 slide cũ + 7 khung mở rộng, 10 slide dự phòng)

*Dùng được cho PowerPoint lẫn Beamer: mỗi slide là một mục `###` gồm **tiêu đề (câu kết luận có số)**, 1–3 dòng nội dung, **hình** (đường dẫn trong `figures/`, `docs/diagrams/` hoặc "ảnh chụp dashboard Dx") và **ghi chú người nói** (2–3 câu). Số liệu lấy từ kho ở trạng thái cuối (99.441 đơn, GMV 13.494.400,74 BRL) và khớp `handoff/00-TONG-QUAN.md`; chi tiết ở các file `handoff/` và `huong-dan/`.*
*Cách dùng: PowerPoint → mỗi `###` là một slide (dòng tiêu đề = title, gạch đầu dòng = nội dung, "Hình" = ảnh, "Nói" = phần Notes). Beamer → mỗi `###` là một `\begin{frame}{tiêu đề}`; ảnh bằng `\includegraphics{figures/...}`, "Nói" đưa vào `\note{...}`.*
*Thời lượng gợi ý: 30–45 phút (≈ 20 giây/slide cho phần lý thuyết, 40 giây cho slide kết quả); phần nào lược được ghi "(lược)" trong ghi chú.*

Ký hiệu: **[nhóm xác nhận]** = nội dung cần nhóm kiểm tra hoặc thay bằng ảnh thật sau khi dựng dashboard.

*Sau P8 các slide được xếp lại theo barem (khảo sát → phân tích và thiết kế → dashboard → mở rộng → tổng kết). Số `Sxx` giữ nguyên số cũ để tra ghi chú và câu hỏi đáp; thứ tự trình bày là thứ tự các mục dưới đây. Slide lý thuyết S06–S12 chuyển sang phụ lục (file `sections/99-du-phong.tex`). Mỗi slide hiện nhãn mục barem ở góc trên bên phải.*

---
## MỞ ĐẦU – tiêu đề, mục lục, tối đa 2 slide lý thuyết (file `sections/00-mo-dau.tex`)

### S01. Xây kho dữ liệu và BI cho 99.441 đơn hàng thương mại điện tử Olist
- Học phần MI4214 – Kho dữ liệu và Kinh doanh thông minh; nhóm …; giảng viên …
- Hình: logo trường (chèn) + `figures/3-3-4_constellation.png` (làm nền mờ)
- Nói: Chúng em xây một kho dữ liệu hoàn chỉnh từ hai bộ dữ liệu Olist: nguồn, ETL, kho hình sao, data mart và bảy dashboard Power BI. Bài trình bày đi từ bài toán đến kết quả và bài học.

### S02. Bài trình bày gồm năm phần theo thứ tự khảo sát, phân tích thiết kế, dashboard, mở rộng và tổng kết
- 2 Khảo sát · 3 Phân tích và thiết kế · 4 Dashboard và bài học · 5 Mở rộng · 6 Kết luận (mỗi slide hiện mục barem ở góc)
- Hình: không (danh sách đánh số)
- Nói: Mỗi phần có số liệu thật từ kho; cuối mỗi phần nhóm nêu điều học được.

### S03. Dự án trong một trang: 1,56 triệu dòng nguồn thành 6 fact, 17 view mart và 7 dashboard
- 2 hệ thống nguồn → staging → ODS → kho (10 chiều + 6 fact) → 4 data mart → Power BI
- Hình: `figures/3-4-1_pipeline.png`
- Nói: Toàn bộ dựng lại từ đầu bằng một lệnh trong khoảng 7 phút và cho kết quả giống hệt; 136 phép kiểm thử đạt. Đây là bức tranh để quay lại khi cần.

### S04. Kho dữ liệu là nơi tích hợp dữ liệu hướng chủ đề, biến thiên theo thời gian và không bị ghi đè
- Bốn đặc tính của Inmon: hướng chủ đề, tích hợp, biến thiên theo thời gian, không biến động
- Hình: sơ đồ 4 ô (vẽ)
- Nói: Ở dự án này chủ đề là quản lý đơn hàng; tích hợp hai nguồn bán hàng và marketing; lịch sử khách được giữ bằng SCD2. [nhóm viết theo giáo trình]

### S05. OLTP tối ưu ghi từng giao dịch, OLAP tối ưu đọc và tổng hợp
- OLTP: 9 bảng chuẩn hóa; OLAP: một fact nối các chiều
- Hình: bảng so sánh OLTP/OLAP (vẽ) + `figures/3-2-4_erd_oltp.png`
- Nói: Cùng một câu hỏi "GMV theo bang theo tháng" cần nối ba bảng ở nguồn nhưng chỉ nối một fact với hai chiều ở kho.

---
## PHẦN 2 – Khảo sát (file `sections/01-khao-sat.tex`)

#### 2.1 Nghiệp vụ

### S13. Olist kết nối người bán nhỏ với các sàn lớn: 3.095 seller bán 99.441 đơn trong 2 năm
- Dữ liệu Brazil, 09/2016–10/2018; hai bộ Kaggle
- Hình: ảnh/logo Olist [nhóm xác nhận]
- Nói: Nhóm tìm hiểu Olist từ nguồn công khai; [nhóm bổ sung số liệu doanh nghiệp từ nguồn đã đọc].

### S14. Mô hình kinh doanh hai phía: seller được thu hút, người mua mua qua sàn
- Business Model Canvas 9 ô (bản nháp)
- Hình: `figures/3-2-3_business_model_canvas.png`
- Nói: Ô doanh thu là suy luận, dữ liệu không có doanh thu của Olist. [nhóm xác nhận]

### S15. Giá trị đề xuất: một hợp đồng, nhiều sàn; dữ liệu cho thấy phí vận chuyển bằng 16,6% giá hàng
- Giá trị cho seller và cho người mua; chi phí chính là vận chuyển và hậu cần
- Hình: `figures/3-2-3_business_model_canvas.png` (phóng ô 2, 5, 9)
- Nói: GMV 13,49 triệu BRL, phí vận chuyển 2,24 triệu BRL.

### S16. Bài toán: hiểu hiệu suất đơn hàng và hiệu quả thu hút seller từ hai hệ thống rời nhau
- Hai hệ thống chỉ gặp nhau ở `seller_id`
- Hình: `figures/3-2-4_erd_oltp.png`
- Nói: Giá trị của kho là tích hợp để trả lời câu hỏi xuyên quy trình.

### S17. Sáu nhóm câu hỏi phân tích bao trùm bán hàng, vận hành, khách hàng và thu hút seller
- Bán hàng · xử lý đơn · thanh toán · trải nghiệm khách · seller · thu hút seller
- Hình: `figures/3-2-6_cay_yeu_cau_phan_tich.png`
- Nói: Mỗi nhóm trở thành một hoặc nhiều dashboard.

### S18. Kho phục vụ hai quy trình nghiệp vụ: xử lý đơn và thu hút seller
- Chung chiều seller và ngày
- Hình: `figures/3-3-4_constellation.png`
- Nói: Chiều seller là "chiếc cầu" nối hai quy trình.

### S19. Đơn hàng đi qua bốn mốc thời gian và có thể bị hủy hoặc không khả dụng
- Đặt → duyệt → bàn giao vận chuyển → giao → đánh giá; 1.234 đơn Failed (1,24%)
- Hình: `figures/3-2-1_bpmn_don_hang.png`
- Nói: BPMN nháp; [nhóm vẽ lại bằng draw.io].

### S20. Mỗi mốc của quy trình là một cột thời gian mà kho biến thành chỉ số
- `approval_hours` 10,3 giờ · `handling_days` 2,9 ngày · `transit_days` 9,3 ngày · `lead_days` 12,6 ngày
- Hình: bảng các mốc (3.2.1)
- Nói: Chặng vận chuyển dài nhất; chặng seller bàn giao gần 3 ngày.

### S21. Kho thu thập dữ liệu ở bảy điểm của quy trình đơn hàng
- Ô vàng trên BPMN: đặt, duyệt, bàn giao, giao, đánh giá, hủy, thanh toán
- Hình: `figures/3-2-1_bpmn_don_hang.png` (đánh dấu điểm thu thập)
- Nói: Đây là chỗ hệ thống phân tích "bám" vào quy trình.

### S22. Quy trình thu hút seller đi từ MQL đến seller có đơn, trung bình mất 100 ngày
- Liên hệ → chốt (TB 48,5 ngày) → đơn đầu (TB 51,9 ngày)
- Hình: `figures/3-2-2_bpmn_thu_hut_seller.png`
- Nói: Hai khoảng thời gian này là hai chỉ số của fact lead funnel.

### S23. Phễu thu hút: 8.000 MQL → 842 deal (10,5%) → 379 seller có đơn bán được (45,0% số deal)
- 462 deal đã chốt nhưng chưa bán gì
- Hình: `figures/3-3-1_funnel_seller_overlap.png`
- Nói: Đây là kết quả phân tích, không phải lỗi dữ liệu.

### S24. Cây nghiệp vụ gom hoạt động của Olist thành năm nhóm
- Thu hút seller · quản lý đơn hàng · chăm sóc khách · quản lý seller · quản trị dữ liệu
- Hình: `figures/3-2-5_cay_nghiep_vu.png`
- Nói: Kho chủ yếu phục vụ nhóm quản lý đơn hàng và thu hút seller.

#### 2.2 Yêu cầu phân tích

### S25. Cây yêu cầu phân tích đi từ sáu chủ điểm đến các câu hỏi cụ thể
- Chủ điểm → câu hỏi → chiều cần quan tâm
- Hình: `figures/3-2-6_cay_yeu_cau_phan_tich.png`
- Nói: Cây này là cơ sở thiết kế fact, dimension và dashboard.

### S26. Bán hàng: GMV cần tăng trưởng MoM, YoY và quy luật 80/20
- GMV 13,49 triệu BRL; AOV 137,42 BRL
- Hình: bảng chủ điểm bán hàng (3.2.2)
- Nói: GMV không tính đơn hủy để phản ánh doanh thu thật.

### S27. Xử lý đơn: không chỉ hỏi "đúng hạn không" mà hỏi "hứa so với thực tế chênh bao nhiêu"
- Đúng hạn 93,2% nhưng hứa 24,4 ngày, thực tế 12,6 ngày
- Hình: bảng chủ điểm xử lý đơn
- Nói: Vì ngày dự kiến rất rộng nên nhóm thêm KPI ngày hứa so với ngày giao thực tế.

### S28. Trải nghiệm khách: giao trễ là yếu tố kéo điểm review xuống mạnh nhất
- Điểm 4,29 khi giao sớm, 1,70 khi trễ trên 7 ngày
- Hình: `figures/3-3-1_delay_vs_review.png`
- Nói: Đây là phát hiện trung tâm của dashboard D5.

### S29. Thu hút seller: câu hỏi là kênh nào chuyển đổi tốt và seller từ funnel bán ra sao
- Tỷ lệ chốt theo kênh từ 2,7% đến 16,7%
- Hình: `figures/3-3-1_funnel_win_rate_by_origin.png`
- Nói: Luôn nêu cỡ mẫu vì nhiều kênh chỉ có vài chục seller.

#### 2.3 KPI và dashboard

### S30. Bảng KPI chính gồm 19 chỉ số, mỗi chỉ số có một định nghĩa DAX duy nhất
- GMV, Orders, AOV, on-time, lead time, review, repeat, MQL→seller…
- Hình: bảng KPI (`report/tables/kpi.tex`)
- Nói: Giá trị trong bảng tính bằng SQL và dùng để đối chiếu với Power BI.

### S31. Mỗi dashboard có một cây phân tích từ mục tiêu đến chỉ số và chiều
- Bảy cây phân tích D1–D7
- Hình: `figures/3-2-7_cay_phan_tich_D1.png` … `D7.png` (lưới 7 ô)
- Nói: Ví dụ D3: mục tiêu giám sát giao hàng, chỉ số on-time, promised vs actual, chiều vùng và nhóm trễ.

#### 2.4 Dữ liệu nguồn (quy mô, tần suất, luồng dữ liệu)

### S32. Phạm vi: dữ liệu 01/2017–08/2018 chiếm 99,6% số đơn nên được dùng cho xu hướng
- 2016 chỉ 329 đơn; 09–10/2018 chỉ 20 đơn
- Hình: `figures/3-3-1_orders_per_month.png`
- Nói: Bộ lọc InWindow trong Power BI cố định cửa sổ này cho D1–D6.

### S33. Hai hệ thống nguồn có 11 bảng, 121 MB và 1.559.764 dòng
- oltp 9 bảng 1.550.922 dòng; crm 2 bảng 8.842 dòng
- Hình: bảng nguồn (`report/tables/src_tables.tex`)
- Nói: Vượt tiêu chí kích thước dữ liệu của môn (trên 100 MB).

### S34. Bảng toạ độ chiếm 64% số dòng nhưng chỉ đại diện 19.015 mã bưu chính
- 1.000.163 dòng geolocation
- Hình: bảng nguồn (làm nổi dòng geolocation)
- Nói: Đây là bảng cần xử lý nhiều nhất ở ODS.

### S37. Luồng dữ liệu và tần suất cập nhật: nạp ban đầu 45.430 đơn rồi 11 đợt hằng tháng
- Tổng 286.144 bản ghi mới qua 11 đợt
- Hình: `figures/3-4-1_pipeline.png`
- Nói: Dữ liệu Kaggle là ảnh tĩnh nên nhóm mô phỏng cập nhật.

#### 2.5 ERD OLTP

### S35. ERD hệ thống bán hàng: chín bảng nối quanh đơn hàng
- orders → items, payments, reviews; customers, sellers, products
- Hình: `figures/3-2-4_erd_oltp.png`
- Nói: `customer_id` được sinh riêng cho từng đơn nên cần `customer_unique_id` để nhận ra khách thật.

### S36. Các cột được gạch chân trên ERD là cột đi sang kho, kèm ghi chú mapping
- Ví dụ: `order_purchase_timestamp` → `purchase_date_key`, `price` → `price`
- Hình: ERD đã gạch chân (vẽ lại) [nhóm hoàn thiện]
- Nói: Bảng mapping đầy đủ 108 dòng ODS → kho nằm ở phụ lục.

---
## PHẦN 3 – Phân tích và thiết kế (file `sections/02-phan-tich-thiet-ke.tex`)

#### 3.1 Khám phá dữ liệu (gồm khoảng cách địa lý)

### S38. Khám phá dữ liệu đo được 45 loại lỗi cần xử lý ở ODS
- Cột thiếu, mốc thời gian sai thứ tự, tên thành phố lệch dấu, trùng lặp
- Hình: `figures/3-3-1_data_quality.png`
- Nói: Không loại lỗi nào bằng cách xóa dữ liệu.

### S39. Tỷ lệ ô rỗng cho thấy cột nào cần điền `unknown`
- Cột review và ngày giao có nhiều ô rỗng hợp lệ
- Hình: `figures/3-3-1_null_heatmap.png`
- Nói: Ô rỗng của ngày giao đa phần là đơn chưa giao hoặc bị hủy.

### S40. Bảng toạ độ bẩn nhất: 93,5% mã bưu chính có nhiều toạ độ, 26,2% dòng trùng hoàn toàn
- 7,3% tên thành phố lệch dấu; 42 điểm ngoài lãnh thổ Brazil
- Hình: `figures/3-4-3_before_after_geolocation.png`
- Nói: Giải pháp: lọc khung Brazil, lấy trung vị toạ độ và mode tên thành phố theo zip.

### S41. Phân bố giá, phí vận chuyển và lead time đều lệch phải
- Nhiều giá trị lớn bất thường ở phí vận chuyển
- Hình: `figures/3-3-1_distributions_numeric.png`
- Nói: Vì vậy dùng trung vị và Spearman khi cần.

### S42. Dữ liệu đơn dùng được là 01/2017–08/2018, hai đầu rất thưa
- 2016 chỉ 329 đơn; 09–10/2018 chỉ 20 đơn
- Hình: `figures/3-3-1_orders_per_month.png`
- Nói: Quyết định lọc thời gian đưa vào Power BI.

### S43. 18/74 danh mục (24,3%) tạo 80% GMV, dẫn đầu `health_beauty` 9,3%
- Quy luật Pareto theo danh mục
- Hình: `figures/3-3-1_pareto_category.png`
- Nói: Danh mục được gom thành 13 nhóm ngành hàng.

### S44. Seller thì phân tán hơn: 540 seller tạo 80% GMV, 5 seller lớn nhất chỉ 7,7%
- Doanh thu không phụ thuộc vài seller
- Hình: `figures/3-3-1_pareto_seller.png`
- Nói: Khác với danh mục, rủi ro tập trung vào seller thấp.

### S45. Giao trễ làm điểm review rơi từ 4,29 xuống 1,70 và 79,2% review tiêu cực
- Đơn trễ chiếm 6,5% số review nhưng tạo 27,4% review tiêu cực
- Hình: `figures/3-3-1_delay_vs_review.png`
- Nói: Trung bình toàn sàn che mất nhóm nhỏ nhưng đau.

### S46. Trễ tập trung ở Bắc và Đông Bắc: Nordeste trễ 12,8%, Norte lead time 22,6 ngày
- Sudeste chỉ 6,1% trễ, lead time 10,7 ngày
- Hình: `figures/3-3-1_late_rate_by_state.png`
- Nói: Địa lý quyết định trải nghiệm giao hàng.

### S47. Chỉ 380/842 deal (45,1%) có đơn: funnel và bán hàng chỉ giao nhau một phần
- 380 seller tạo 674.005 BRL, 4,99% GMV
- 380 là số seller có đơn ở mọi trạng thái; kho chỉ tính đơn không bị huỷ nên có 379 seller (45,0%)
- Hình: `figures/3-3-1_funnel_seller_overlap.png`
- Nói: Quyết định D6 hiển thị cả nhóm "chốt nhưng chưa bán".

### S48. Sáu quyết định thiết kế đến từ khám phá dữ liệu
- SCD2 khách (0,26% đổi zip); D6 hai trang; snapshot seller dày đặc; 13 nhóm ngành; zip thiếu toạ độ vẫn có dòng; mốc nạp 2017-12-31
- Hình: bảng quyết định (`handoff/00-TONG-QUAN.md` mục 7)
- Nói: Mỗi quyết định có số liệu trong `handoff/design-questions.md`.

### S107. Mở rộng địa lý: hàm haversine SQL thuần tính khoảng cách seller → khách cho 112.650 dòng hàng
- 555 dòng (0,49%) thiếu toạ độ vẫn được giữ lại với giá trị trống
- Hình: đoạn SQL `dw.haversine_km` (Phụ lục B)
- Nói: São Paulo – Rio tính ra 360,9 km, gần với thực tế.

### S108. Khoảng cách tăng từ dưới 100 km lên trên 1.000 km làm phí vận chuyển gấp 2,7 lần và lead time gấp 2,9 lần
- Phí 11,75 → 31,65 BRL; lead time 6,5 → 19,0 ngày; trễ 4,5% → 10,3%
- Hình: `figures/3-5-2_distance_vs_freight.png`, `figures/3-5-2_distance_vs_leadtime.png`
- Nói: Tương quan Spearman 0,63 với phí và 0,54 với lead time; đó là tương quan, không phải nhân quả.

### S109. Haversine thuần đủ cho khoảng cách điểm–điểm; PostGIS cần khi truy vấn bán kính hoặc đa giác
- GiST chỉ mục không gian; haversine sai số tối đa 0,5%
- Hình: bảng so sánh (`report/chapters/3-1-kham-pha.tex`)
- Nói: Nhóm không cài PostGIS nên chọn giải pháp thuần SQL.

#### 3.2 Kiến trúc

### S49. Kiến trúc sáu lớp từ hai hệ thống nguồn đến bảy dashboard
- oltp/crm → staging → ODS → kho → data mart → Power BI; etl_log giám sát
- Hình: `docs/diagrams/kien-truc-cac-lop.drawio` (logo PostgreSQL, Python, Power BI, GitHub) [nhóm hoàn thiện]
- Nói: Mỗi lớp có một việc và một cách kiểm tra riêng.

### S50. Tách lớp giúp đối soát: staging = ODS + dòng bị loại cho mọi bảng
- Chỗ nào hỏng biết ngay lớp nào
- Hình: bảng đối soát (handoff P2)
- Nói: Không phải lấy lại dữ liệu từ nguồn khi ODS lỗi.

### S51. Công nghệ: PostgreSQL 18, Python 3.11, SQL procedure, Power BI, Git
- Không Docker, không PostGIS; điều phối bằng một lệnh
- Hình: logo công nghệ (chèn)
- Nói: Chạy được trên laptop sinh viên 8 GB.

#### 3.3 ETL (gồm đối soát, nạp tăng dần, dựng lại toàn bộ)

### S52. ODS là lớp làm sạch trung gian: 18 bảng, 678.183 dòng, mọi lỗi có cờ hoặc lý do
- Zip thành 5 chữ số, thành phố bỏ dấu, `NULL` thành `unknown`, khử trùng review
- Hình: bảng lỗi và xử lý (`report/tables/dq_errors.tex`)
- Nói: 1.411 đơn (1,4%) có ít nhất một cờ chất lượng.

### S67. Một lệnh chạy sáu bước ETL và ghi lại từng bước
- extract → ODS → dim → fact → mart → tests → snapshot → export
- Hình: `docs/diagrams/pipeline-etl.drawio`
- Nói: Mỗi bước ghi `job_run`; lỗi thì dừng và đánh dấu failed.

### S68. Extract chỉ lấy dòng chưa có: đơn theo watermark, bảng nhỏ theo khoá
- Chế độ full 52 giây; incremental khoảng 22 giây
- Hình: `figures/3-4-1_pipeline.png`
- Nói: MQL và deal không dùng watermark ngày vì deal có thể đến trước MQL.

### S69. ODS xử lý lỗi theo ba cách: chuẩn hóa, gắn cờ hoặc loại có lý do
- 1.359 đơn bàn giao trước khi duyệt được gắn cờ, không xóa
- Hình: bảng lỗi (`report/tables/dq_errors.tex`)
- Nói: Khoảng thời gian âm đặt NULL ở fact và được đếm lại.

### S70. Trước và sau ETL: bảng đơn hàng có thêm cờ lỗi và kiểu dữ liệu chuẩn
- Ví dụ trước/sau
- Hình: `figures/3-4-3_before_after_orders.png`
- Nói: Cùng 99.441 đơn nhưng thêm `dq_flags`.

### S71. Trước và sau ETL: sản phẩm và seller được chuẩn hóa tên cột và thành phố
- `*_lenght` → `*_length`; thành phố bỏ dấu, chữ thường
- Hình: `figures/3-4-3_before_after_products.png`, `figures/3-4-3_before_after_sellers.png`
- Nói: Hai hình cùng một slide.

### S72. Trước và sau ETL: 1.000.163 dòng toạ độ gom thành 19.178 mã bưu chính
- Trung vị toạ độ, mode thành phố
- Hình: `figures/3-4-3_before_after_geolocation.png`
- Nói: 42 điểm ngoài Brazil được ghi vào bảng loại.

### S73. Trước và sau ETL: MQL và deal có giá trị trống thành `unknown`
- `origin` rỗng → `unknown`; doanh thu khai báo 0 gắn cờ
- Hình: `figures/3-4-3_before_after_mql.png`, `figures/3-4-3_before_after_closed_deals.png`
- Nói: Không đoán giá trị, chỉ đánh dấu.

### S74. Đối soát số dòng: nguồn = staging = ODS + loại, và tổng tiền khớp từng đồng
- Σ price 13.591.643,70 BRL = file CSV
- Hình: bảng đối soát (handoff P4)
- Nói: Chênh lệch nếu có phải giải thích được bằng `rejected_rows`.

### S75. SCD2 được nạp bằng window function: mỗi lần zip đổi mở một phiên bản mới
- `lag(zip)` so với đơn trước; `effective_from` = ngày mua
- Hình: đoạn SQL (Phụ lục B, `code/scd2_dim_customer.sql`)
- Nói: Khoá thay thế cũ không đổi khi chạy lại.

### S76. Nạp fact: tra khoá theo phiên bản có hiệu lực, khoảng thời gian âm thành NULL
- 1.359 đơn có `handling_days` âm (bàn giao trước khi duyệt) được đặt NULL và đếm
- Hình: bảng `fact_load_issue`
- Nói: Tra không thấy thì dùng −1 và ghi nhận.

### S77. Nạp tăng dần mô phỏng: 11 đợt hằng tháng, tổng 286.144 bản ghi mới
- `simulate_increment` rồi `run_pipeline --mode incremental`
- Hình: `figures/3-4-1_pipeline.png` (nhấn nhánh incremental)
- Nói: Đơn vào với trạng thái cuối; đó là giới hạn của mô phỏng.

### S78. Mỗi đợt chạy 20–26 giây, trong đó kiểm thử chiếm hơn một nửa
- Bảng 11 đợt: bản ghi mới, thời gian
- Hình: bảng đợt (`report/tables/increments.tex`)
- Nói: Đợt 1–8 mang 99,95% bản ghi mới; ba đợt cuối mang nốt 20 đơn và 50 deal.

### S79. Funnel lấp đầy dần: MQL 2.002 → 8.000, deal 3 → 842, seller có đơn 0 → 379
- Số liệu mỗi đợt từ `batch_metrics`
- Hình: biểu đồ đường từ `batch_metrics` (dashboard D7)
- Nói: Đây là điểm trình bày của nạp tăng dần.

### S80. Kết quả incremental trùng nạp full: 16/16 bảng khớp số dòng, tổng tiền và nội dung
- So sánh bằng checksum trên khoá tự nhiên
- Hình: bảng so sánh (`handoff/2026-11-05-P5.md`)
- Nói: Khoá thay thế khác nhau nên so sánh qua khoá tự nhiên.

### S81. Dòng mồ côi được thử lại ở đợt sau, nhưng cơ chế mới được chứng minh bằng kiểm thử
- Kịch bản deal `b91cf88…` trên bản sao trong giao dịch rồi hoàn tác
- Hình: sơ đồ 3 bước (loại → cha đến → nạp lại)
- Nói: Trong 11 đợt thật không có dòng mồ côi nào; nhóm nói thẳng điều này.

### S82. 136 phép kiểm thử đạt 100%, cộng 6 phép đối chiếu với khám phá dữ liệu
- Số dòng, tổng tiền, grain, khoá ngoại, SCD2, mart khớp fact
- Hình: bảng nhóm kiểm thử
- Nói: Chạy sau mỗi lần pipeline, lưu `etl_log.dq_check`.

### S83. Nhật ký `etl_log` cho biết mỗi lô chạy gì, mất bao lâu, loại bao nhiêu dòng
- `job_run`, `rejected_rows`, `dq_check`, `batch_metrics`
- Hình: ảnh chụp dashboard D7 [nhóm chèn]
- Nói: D7 là dashboard giám sát hệ thống.

### S110. Dựng lại toàn bộ dự án từ đầu mất 443 giây và cho kết quả giống hệt
- Xóa hai database, chạy một lệnh, 16/16 bảng khớp
- Hình: bảng `report/tables/rebuild.tex`
- Nói: Khả năng tái lập là bằng chứng độ tin cậy của pipeline.

#### 3.4 Hệ thống chiều khái niệm

### S57. Mười bảng chiều với số dòng từ 6 đến 96.339
- dim_date 1.828; geography 19.178; customer 96.339; seller 3.558; product 32.952; …
- Hình: bảng chiều (`report/tables/dims.tex`)
- Nói: Mỗi chiều có đúng một dòng Unknown, được kiểm thử.

### S58. Hệ thống chiều khái niệm: phân cấp ngày, địa lý, sản phẩm, seller, khách
- Ngày → tháng → quý → năm; zip → thành phố → bang → vùng
- Hình: sơ đồ phân cấp (vẽ) [nhóm hoàn thiện]
- Nói: Phân cấp là cơ sở của roll-up và drill-down.

### S59. SCD2 giữ lịch sử địa chỉ: 96.096 khách thành 96.339 dòng, 236 khách đổi zip
- Đơn cũ vẫn trỏ về địa chỉ lúc mua
- Hình: bảng 2 phiên bản của một khách (`huong-dan/01-pipeline-bang-loi.md`)
- Nói: Ví dụ khách `570eb70f…` đổi zip ngày 09/11/2017; đơn 24/10 thuộc phiên bản 1.

### S60. `dim_seller` là chiều dùng chung: nối bán hàng với funnel qua `seller_id`
- 462 seller chỉ có trong CRM vẫn có dòng, địa chỉ Unknown
- Hình: bảng ví dụ seller (`huong-dan/01-pipeline-bang-loi.md`)
- Nói: `first_sale_date` được điền sau khi nạp fact.

### S61. Chiều rác và role-playing giúp fact gọn mà vẫn đủ thông tin
- `dim_lead_profile` gom 7 thuộc tính thành 503 tổ hợp; `dim_date` đóng 5 vai ở fulfillment
- Hình: bảng ví dụ hai kỹ thuật
- Nói: Trong Power BI, vai trò ngày dùng quan hệ không hoạt động và `USERELATIONSHIP`.

### S66. Dòng Unknown −1 và khoá thay thế bảo đảm fact không bao giờ có khoá rỗng
- Mọi lỗi tra khoá được ghi `fact_load_issue`
- Hình: bảng `dim_seller` dòng −1
- Nói: Nhờ đó ETL không làm rơi dòng khi chiều thiếu.

#### 3.5 Data model OLAP (logic, vật lý, mart, OLAP, hiệu năng)

### S53. Bus matrix: sáu fact dùng chung các chiều ngày, seller, khách, địa lý
- Seller là chiều dùng chung của hai quy trình
- Hình: bus matrix (`docs/DW_DESIGN.md` mục 4, vẽ lại)
- Nói: Bus matrix cho thấy chiều nào được dùng lại ở đâu.

### S54. Mô hình constellation: bốn mart, sáu fact (cam), mười chiều (xanh)
- Khung = data mart
- Hình: `figures/3-3-4_constellation.png` / `docs/diagrams/data-model-theo-mart.drawio`
- Nói: Fact màu cam, chiều màu xanh đúng yêu cầu trình bày.

### S55. Data model logic: mỗi fact nối đúng các chiều theo bus matrix
- Ví dụ `fact_order_item` nối 6 chiều với 2 vai địa lý
- Hình: `figures/3-3-4_erd_dw.png`
- Nói: Địa lý có hai vai: khách và seller.

### S56. Data model vật lý: khoá chính theo grain, khoá ngoại có index, 112.650 dòng hàng
- Mọi khoá ngoại NOT NULL, dòng Unknown −1
- Hình: `figures/3-3-4_erd_dw.png` (kèm kiểu dữ liệu) [nhóm hoàn thiện]
- Nói: Tiền `numeric(12,2)`, khoá `<tên>_key`, ngày `yyyymmdd`.

### S62. Sáu fact thuộc đủ ba loại của Kimball
- Transaction ×3, accumulating ×2, periodic ×1
- Hình: bảng fact (`report/tables/facts.tex`)
- Nói: Tổng 459.784 dòng fact (99.441 + 112.650 + 103.886 + 99.224 + 8.000 + 36.583).

### S63. `fact_order_fulfillment` là accumulating snapshot: một đơn một dòng, cập nhật theo mốc
- Mốc chưa xảy ra có khoá −1; thời gian từng chặng tính sẵn
- Hình: dòng ví dụ (`huong-dan/01-pipeline-bang-loi.md`)
- Nói: Nếu dùng transaction fact phải ghép nhiều dòng mới tính được lead time.

### S64. `fact_lead_funnel` ghi lại hành trình MQL: ba mốc ngày và hai khoảng thời gian
- `days_to_close` TB 48,5; `days_won_to_first_sale` TB 51,9
- Hình: dòng ví dụ MQL
- Nói: Cũng là accumulating snapshot, 8.000 dòng.

### S65. `fact_seller_monthly` lưu dày đặc 36.583 dòng để thấy seller ngừng bán
- Dày đặc so với thưa: 36.583 và 16.441 dòng
- Hình: bảng 4 tháng đầu của một seller
- Nói: Tháng không có đơn vẫn có dòng với `orders = 0`.

### S84. Bốn data mart gồm 17 view, trong đó 4 là materialized view làm mới trong 2 giây
- Sales, fulfillment, cx, acquisition
- Hình: bảng mart (`report/tables/marts.tex`)
- Nói: Mart được làm mới tự động ở bước mart của pipeline.

### S85. Roll-up và drill-down: GMV 2017 là 6,11 triệu, 2018 là 7,34 triệu; ngày Black Friday cao gấp 5,2 lần
- Quý 4/2017: 2,41 triệu BRL; 24/11/2017: 152.654 BRL
- Hình: bảng roll-up (`report/tables/olap_rollup.tex`)
- Nói: Roll-up dùng `ROLLUP`, drill-down thêm cấp vào `GROUP BY`.

### S86. Slice, dice và pivot: vùng Sudeste chiếm 64,3% GMV năm 2017
- Dice Sudeste × Home & Furniture × quý 4: SP 199.179 BRL
- Hình: bảng pivot (`report/tables/olap_pivot.tex`)
- Nói: Pivot bằng tổng có điều kiện `FILTER`.

### S87. Chọn ROLAP vì dữ liệu nhỏ, kho luôn tươi và Power BI làm lớp ngữ nghĩa
- Khác MOLAP: không phải xử lý lại khối khi nạp dữ liệu
- Hình: bảng ROLAP vs MOLAP (`handoff/olap-examples.md`)
- Nói: Đây là lý do lựa chọn đã nêu ở phần 1.

### S88. Star schema chỉ nhanh hơn OLTP 1,0–1,6 lần; tốc độ lớn đến từ materialized view và index
- Chọn lọc một seller nhanh gấp 9 lần nhờ index; materialized view dưới 1 ms so với 150–750 ms
- Hình: `figures/3-5-1_benchmark.png`
- Nói: Không phóng đại: giá trị chính của mô hình chiều là truy vấn đơn giản và số liệu nhất quán.

---
## PHẦN 4 – Dashboard và bài học (file `sections/03-dashboard.tex`)

### S89. Bảy dashboard chia thành bốn loại: thời gian, OLAP, vận hành, thống kê
- D1 Executive · D2 Sales · D3 Fulfillment · D4 Geography · D5 Customer · D6 Seller · D7 ETL monitor
- Hình: bảng 7 dashboard (`huong-dan/dashboards/`)
- Nói: Mỗi dashboard dùng nhiều loại biểu đồ, slicer và định dạng có điều kiện.

### S90. Mô hình Power BI có 16 bảng và 32 quan hệ, mỗi fact một quan hệ ngày hoạt động
- Quan hệ còn lại không hoạt động
- Hình: ảnh chụp Model view [nhóm chèn]
- Nói: Tham số `DataFolder` giúp đổi máy chỉ cần sửa một giá trị.

### S91. Role-playing date và DAX tăng trưởng: GMV tháng 11/2017 tăng 52,1% so với tháng 10
- `USERELATIONSHIP`, `DATEADD`, `SAMEPERIODLASTYEAR`
- Hình: đoạn DAX (`powerbi/measures.md`)
- Nói: Mọi measure đối chiếu với bảng giá trị kỳ vọng từ SQL.

### S92. Chủ đề màu thống nhất: xanh là tốt, vàng cần chú ý, đỏ là xấu
- `powerbi/theme.json`; ngưỡng cảnh báo on-time 90%/95%
- Hình: ảnh chụp theme [nhóm chèn]
- Nói: Cùng một quy ước màu trên mọi dashboard.

### S93. D1 Executive: GMV 13,49 triệu BRL, 98.199 đơn, đúng hạn 93,2%, review 4,09
- Thẻ KPI, đường GMV theo tháng, cột MoM, thanh theo vùng, treemap ngành
- Hình: ảnh chụp dashboard D1 [nhóm chèn]
- Nói: Trang tổng quan cho lãnh đạo.

### S94. D1 cho thấy tháng 11/2017 là đỉnh (1,0 triệu BRL) và Sudeste chiếm 65% GMV
- Black Friday 152.654 BRL trong một ngày
- Hình: ảnh chụp dashboard D1 [nhóm chèn]
- Nói: Từ 03/2018 GMV đi ngang nhưng cao hơn cùng kỳ (05/2018 +97%).

### S95. D2 Sales và Product: 18 danh mục tạo 80% GMV; Home & Furniture dẫn đầu 22,8%
- Treemap, ma trận drill, Pareto, scatter AOV – freight
- Hình: ảnh chụp dashboard D2 [nhóm chèn]
- Nói: Drill từ nhóm ngành xuống danh mục.

### S96. D2 cho thấy phí vận chuyển nặng ở hàng giá thấp và ở vùng xa
- Freight ratio 16,6% toàn sàn
- Hình: ảnh chụp D2 (scatter) [nhóm chèn]
- Nói: Danh mục nhẹ giá thấp bị phí vận chuyển ăn vào nhiều nhất.

### S97. D3 Order Fulfillment: lead time 12,6 ngày, phễu trạng thái và tỷ lệ trễ theo bang
- Funnel, cột chồng từng chặng, bản đồ trễ
- Hình: ảnh chụp dashboard D3 [nhóm chèn]
- Nói: KPI "hứa so với thực tế" nằm trên đầu trang.

### S98. D3 cho thấy Olist hứa 24,4 ngày nhưng giao 12,6 ngày: sớm hơn lời hứa 11,8 ngày
- Đúng hạn tụt 87,6% ở Black Friday 11/2017 và 81,0% ở 03/2018
- Hình: ảnh chụp dashboard D3 [nhóm chèn]
- Nói: Tải cao làm giao chậm dù trung bình vẫn "đúng hạn".

### S99. D4 Geography và Freight: Sudeste 65,4% GMV, Norte và Nordeste chịu phí vận chuyển 22%
- Bản đồ bong bóng, ma trận phân cấp, GMV khách và seller
- Hình: ảnh chụp dashboard D4 [nhóm chèn]
- Nói: Dùng `v_geo_state` và `v_geo_zip` cho bản đồ.

### S100. D4 cho thấy 36% dòng hàng có seller và khách cùng bang
- Khoảng cách TB 598 km
- Hình: ảnh chụp dashboard D4 [nhóm chèn]
- Nói: Mô hình vai trò địa lý seller cho phép so sánh hai phía.

### S101. D5 Customer Experience: điểm review 4,09; 14,7% review tiêu cực; chỉ 3,1% khách quay lại
- Cột điểm theo nhóm trễ, donut thanh toán, RFM, cohort
- Hình: ảnh chụp dashboard D5 [nhóm chèn]
- Nói: Có sáu phân khúc RFM trên 94.983 khách.

### S102. D5: thẻ tín dụng chiếm 78,3% giá trị thanh toán và trả góp trung bình 3,5 kỳ
- 66,9% giao dịch thẻ trả góp nhiều kỳ
- Hình: ảnh chụp dashboard D5 (donut) [nhóm chèn]
- Nói: Boleto chiếm 17,9%.

### S103. D6 trang 1: tỷ lệ chốt theo kênh từ 2,7% (other) đến 16,7% (unknown)
- Phễu MQL → deal → seller có đơn; thời gian chốt
- Hình: ảnh chụp dashboard D6 trang 1 [nhóm chèn]
- Nói: Luôn kèm cỡ mẫu: email chỉ 493 MQL.

### S104. D6 trang 2: seller từ funnel chỉ tạo 4,99% GMV; kênh nhỏ được cảnh báo mẫu nhỏ
- Scorecard seller, GMV/seller theo kênh
- Hình: ảnh chụp dashboard D6 trang 2 [nhóm chèn]
- Nói: Email chỉ có 6 seller có đơn nên đánh dấu mẫu nhỏ.

### S105. D7 giám sát ETL: 11 đợt chạy 20–26 giây, 136 test đạt 100%
- Thời gian theo lô, funnel lấp đầy dần, dòng bị loại theo lý do
- Hình: ảnh chụp dashboard D7 [nhóm chèn]
- Nói: Dòng bị loại duy nhất là 42 điểm toạ độ.

### S106. Publish to web chia sẻ cả bảy dashboard bằng một liên kết công khai
- Dữ liệu Olist công khai nên chấp nhận được
- Hình: ảnh màn hình Publish to web [nhóm chèn]
- Nói: Nếu tài khoản bị chặn thì dùng PDF xuất từ Power BI.

### S112. Bài học: không xóa âm thầm, chọn grain trước, định nghĩa KPI một lần
- Mô hình chiều đáng dùng vì nhất quán, tốc độ đến từ materialized view và index
- Hình: không
- Nói: [nhóm bổ sung bài học làm việc nhóm].

---
## PHẦN 5 – Mở rộng (file `sections/04-mo-rong.tex`; khung, P9 và P10 điền)

---
## PHẦN 6 – Tổng kết (file `sections/05-tong-ket.tex`)

### S111. Kết quả: một kho dữ liệu chạy được từ đầu đến cuối với 136 kiểm thử đạt và bảy dashboard
- 10 chiều, 6 fact, 17 view mart; 99.441 đơn; GMV 13,49 triệu BRL
- Hình: `figures/3-3-4_constellation.png`
- Nói: Tổng kết các con số chính của dự án.

### S113. Hạn chế và hướng phát triển: trạng thái trung gian của đơn, PostGIS, lịch chạy tự động
- Mô phỏng cập nhật chỉ thêm bản ghi mới; cơ chế thử lại mồ côi mới được chứng minh bằng test
- Hình: không
- Nói: Nhóm nói rõ giới hạn để kết quả đáng tin.

#### 5.1 Data lakehouse (khung, P10 điền)
- S115. Kiến trúc lakehouse · S116. Triển khai · S117. Kết quả

#### 5.2 Thu thập dữ liệu thực tế từ API (khung, P9 điền)
- S118. Bài toán · S119. Kiến trúc · S120. Triển khai · S121. Kết quả

### S114. Cảm ơn và hỏi đáp
- Thành viên nhóm; liên kết dashboard (Publish to web) [nhóm chèn]
- Hình: mã QR tới dashboard [nhóm chèn]
- Nói: Nhóm sẵn sàng trả lời; các slide dự phòng B01–B10 dùng khi cần.

---
## PHỤ LỤC – slide lý thuyết rút khỏi bài trình bày chính
- S06–S12 (Kimball và Inmon, mô hình chiều, ba loại fact và SCD, ETL, năm thao tác OLAP, MOLAP/ROLAP/HOLAP, BI): giữ làm slide dự phòng khi được hỏi lý thuyết.

---
## 10 CÂU VẤN ĐÁP DỄ GẶP NHẤT VÀ SLIDE DỰ PHÒNG
*Câu trả lời đầy đủ (kèm số liệu) ở `huong-dan/04-cau-hoi-van-dap.md`; số trong ngoặc là câu số.*

| Slide dự phòng | Câu hỏi | Trả lời ngắn (đọc từ slide) | Slide chính liên quan |
| --- | --- | --- | --- |
| B01 | Vì sao `fact_order_fulfillment` là accumulating snapshot? (3) | Đơn đi qua nhiều mốc; một dòng, cập nhật theo mốc; lead time tính sẵn (approval 10,3 giờ, handling 2,9 ngày, transit 9,3 ngày) | S63 |
| B02 | Vì sao chọn ROLAP mà không MOLAP? (25) | PostgreSQL không có khối đa chiều, dữ liệu nhỏ, kho luôn tươi, Power BI là lớp ngữ nghĩa | S11, S87 |
| B03 | SCD2 hoạt động thế nào? (6) | Mỗi lần zip đổi mở phiên bản mới; 96.096 khách → 96.339 dòng; fact tra theo ngày mua | S59, S75 |
| B04 | Xử lý 1 triệu dòng geolocation ra sao? (20) | Lọc khung Brazil (loại 42), trung vị toạ độ, mode thành phố, 19.015 zip; zip chỉ có toạ độ ngoài khung vẫn có dòng | S40, S72 |
| B05 | Vì sao đúng hạn 93,2% mà review đơn trễ vẫn tệ? (33) | Trễ chỉ 6,8% đơn nhưng tạo 27,4% review tiêu cực; điểm 4,29 → 1,70; ngày dự kiến quá rộng | S45, S98 |
| B06 | Vì sao star schema chỉ nhanh hơn OLTP 1,0–1,6 lần mà vẫn đáng dùng? (30) | Dữ liệu nhỏ; giá trị là truy vấn đơn giản, KPI nhất quán; tốc độ từ materialized view và index | S88 |
| B07 | Làm sao biết nạp tăng dần đúng? (13) | So với nạp full: 16/16 bảng khớp số dòng, tổng tiền, checksum; chạy lại một đợt cho 0 dòng mới | S80 |
| B08 | GMV khác tổng giá hàng thế nào? (23) | GMV loại đơn Failed: 13.494.400,74 so với 13.591.643,70 | S26, S30 |
| B09 | Dòng mồ côi được xử lý ra sao? (15) | Loại kèm lý do, thử lại ở đợt sau; mới chứng minh bằng test | S81 |
| B10 | Ngày hứa giao so với thực tế cho thấy điều gì? (34) | Hứa 24,4, thực tế 12,6: sớm 11,8 ngày; 91,9% đơn giao sớm | S27, S98 |

### B01–B10 (nội dung slide dự phòng)
Mỗi slide dự phòng B01–B10 dùng đúng một dòng tương ứng ở bảng trên làm tiêu đề (câu hỏi) và nội dung (trả lời ngắn), thêm hình của slide chính liên quan (cột cuối) để người trình bày chuyển nhanh khi bị hỏi.

# 04 – 40 câu giảng viên có thể hỏi (kèm trả lời có số liệu)

*Số liệu từ `olist_dw` ở trạng thái cuối (99.441 đơn, GMV 13.494.400,74 BRL). Mỗi câu trả lời 2–4 câu để nói được trong 30–60 giây; phần "Xem thêm" chỉ nơi có bằng chứng.*

## A. Thiết kế mô hình (10 câu)
**1. Vì sao chọn chủ đề Order Management và ghép thêm Marketing Funnel?**
Order Management theo Kimball có đủ giao dịch đơn, chu trình xử lý đơn, thanh toán và đánh giá. Ghép thêm Marketing Funnel (8.000 MQL, 842 deal) cho **hai hệ thống nguồn** và một quy trình thứ hai (thu hút seller), nối qua `seller_id`, nên trả lời được câu hỏi xuyên quy trình: seller đến từ kênh nào thì bán tốt. *Xem thêm: `docs/DW_DESIGN.md` mục 1.*

**2. Grain của từng bảng fact là gì và vì sao chọn như vậy?**
`fact_order_item` = 1 dòng hàng của 1 đơn (112.650 dòng) vì giá và phí vận chuyển nằm ở mức dòng hàng; `fact_order_fulfillment` = 1 đơn (99.441); `fact_payment` = 1 lần thanh toán (103.886); `fact_review` = 1 review (99.224); `fact_lead_funnel` = 1 MQL (8.000); `fact_seller_monthly` = 1 seller × 1 tháng (36.583). Grain mịn nhất cho phép cộng lên mọi cấp.

**3. Vì sao `fact_order_fulfillment` là accumulating snapshot?**
Một đơn đi qua nhiều mốc (mua → duyệt → bàn giao → giao, kèm ngày dự kiến) và ta muốn đo thời gian giữa các mốc trên **một dòng** (`approval_hours` 10,3 giờ, `handling_days` 2,9 ngày, `transit_days` 9,3 ngày). Dòng được cập nhật (upsert theo `order_id`) khi đơn sang mốc mới; mốc chưa xảy ra có khoá ngày −1. Nếu dùng transaction fact thì phải tự ghép nhiều dòng để tính khoảng thời gian.

**4. Vì sao có thêm `fact_seller_monthly` kiểu periodic snapshot và vì sao lưu dày đặc?**
Để theo dõi hiệu suất seller theo tháng mà không phải tính lại từ 112 nghìn dòng hàng (scorecard nhanh gấp đôi). Dày đặc (36.583 dòng thay vì 16.441 dòng thưa) để **thấy được seller ngừng bán** (tháng `orders = 0`), điều mà bảng thưa che mất.

**5. `dim_seller` là conformed dimension nghĩa là gì?**
Cùng một bảng chiều được cả hai quy trình dùng: `fact_order_item` (bán hàng) và `fact_lead_funnel`/`fact_seller_monthly` (thu hút seller). Nhờ đó nối được "kênh thu hút → GMV": kênh Paid có 204 seller, 103 seller có đơn, GMV 153.720 BRL. Seller chỉ có trong CRM (462 deal chưa bán) vẫn có dòng với địa chỉ Unknown.

**6. SCD2 hoạt động thế nào trên dữ liệu này?**
Mỗi `customer_id` trong nguồn sinh ra cho từng đơn, nên khách thật (`customer_unique_id`) có thể đổi mã bưu chính qua các đơn. Kho sắp đơn theo thời gian; mỗi lần zip đổi thì mở **phiên bản mới** (`effective_from` = ngày mua, bản cũ `effective_to` = ngày trước). Kết quả: 96.096 khách → 96.338 phiên bản (96.339 dòng kể cả dòng Unknown `-1`); 236 khách có ≥ 2 phiên bản (nhiều nhất 4). Fact tra `customer_key` theo phiên bản có hiệu lực **tại ngày mua** nên báo cáo địa lý theo lịch sử vẫn đúng. *Xem thêm: `01-pipeline-bang-loi.md` mục 2.*

**7. Vì sao chọn SCD2 cho khách khi chỉ 0,26% khách đổi zip?**
Vì chi phí thấp (thêm 242 dòng so với 96.096 khách, +0,25%) mà có ví dụ SCD2 thật trên dữ liệu thật để minh hoạ cho báo cáo. Quyết định ghi trong nhật ký của `DW_DESIGN.md`.

**8. Role-playing dimension là gì, dự án dùng ở đâu?**
Một bảng chiều đóng nhiều vai. `dim_date` có 5 vai trong `fact_order_fulfillment` (mua, duyệt, bàn giao, giao, dự kiến) và 3 vai trong `fact_lead_funnel`; `dim_geography` có vai khách và vai seller; `dim_sales_rep` có vai SDR/SR. Trong SQL: join nhiều lần; trong Power BI: một quan hệ Active + các quan hệ Inactive gọi bằng `USERELATIONSHIP`.

**9. Junk dimension dùng để làm gì ở đây?**
Deal có 7 thuộc tính nhỏ (phân khúc, loại lead, hồ sơ hành vi, loại hình, có công ty, có GTIN, tồn kho). Gom thành `dim_lead_profile` (503 tổ hợp) thay vì rải 7 cột vào fact giúp fact gọn, và nhóm/lọc bằng một khoá.

**10. Vì sao dùng khoá thay thế thay vì dùng mã nguồn?**
Mã nguồn là chuỗi 32 ký tự và có thể thay đổi/không duy nhất giữa hệ thống; khoá số nguyên nhỏ, join nhanh, và **bắt buộc** cho SCD2 (một khách nhiều dòng). Mỗi chiều có dòng Unknown `-1` để fact không bao giờ có khoá rỗng.

## B. ETL và nạp dữ liệu (8 câu)
**11. Kiến trúc các lớp và vai trò từng lớp?**
Nguồn (`oltp`, `crm`) → staging (bản sao thô + mã lô) → ODS (làm sạch, cờ lỗi) → dw (hình sao) → mart (tổng hợp) → Power BI. Tách lớp để chỗ nào hỏng biết ngay, có thể đối soát số dòng từng lớp: staging 1.559.764 = ODS + dòng bị loại. *Xem thêm: `01-pipeline-bang-loi.md`.*

**12. Nạp tăng dần được mô phỏng và thực hiện thế nào?**
Dữ liệu Kaggle là ảnh tĩnh, nên nạp ban đầu đến 31/12/2017 (45.430 đơn) rồi `simulate_increment` đổ thêm **11 đợt hằng tháng** (01–11/2018, tổng 286.144 bản ghi). Mỗi đợt `extract` chỉ lấy dòng chưa có ở staging (đơn theo watermark thời gian), dimension cập nhật theo SCD, fact giao dịch thêm dòng, snapshot được upsert/tính lại. Mỗi đợt mất khoảng 20 giây gồm cả test.

**13. Làm sao biết kết quả nạp tăng dần đúng?**
Nạp full toàn bộ nguồn vào một database riêng rồi so với database sau 11 đợt bằng checksum nội dung trên khoá tự nhiên: **16/16 bảng dim/fact khớp** số dòng, tổng tiền và nội dung. Ngoài ra chạy lại một đợt đã chạy cho 0 dòng chèn, 0 cập nhật (idempotent).

**14. Watermark là gì và dự án dùng thế nào?**
Là mốc "đã nạp đến đâu" (`etl_log.watermark`). Đơn hàng dùng mốc `order_purchase_timestamp` + loại trừ dòng đã có. Riêng `mql` và `closed_deals` **không** dùng watermark ngày vì CRM có thể ghi deal trước ngày liên hệ đầu của lead (deal `b91cf88…`: chốt 06/03, liên hệ 08/03), watermark ngày sẽ bỏ sót.

**15. Dòng mồ côi (orphan) được xử lý ra sao?**
Dòng con thiếu dòng cha bị loại kèm lý do `orphan:…` ở `rejected_rows`, nhưng **được thử lại** ở các đợt sau khi cha đã tới và biến mất khỏi danh sách loại. Thành thật: cơ chế này **mới được chứng minh bằng kịch bản test** (`etl.test_orphan_retry`, 3/3 đạt); trong 11 đợt thật không có dòng mồ côi nào vì nguồn luôn nạp cha trước.

**16. Pipeline xử lý lỗi và ghi nhận thế nào?**
Mỗi job ghi `etl_log.job_run` (thời gian, đọc/chèn/cập nhật/loại, trạng thái) bằng một kết nối riêng tự commit, nên dòng `failed` vẫn còn sau khi dữ liệu bị rollback. Lỗi đầu tiên dừng cả lần chạy: job lỗi và dòng `pipeline.<mode>` ghi `failed` kèm thông báo, tiến trình thoát mã 1. Về transaction, theo code (`etl/procs.py`, `etl/load_dw.py`, `etl/extract.py`, `etl/run_pipeline.py`): **transaction bao theo từng lớp, không bao cả lần chạy**. Bước extract (mọi bảng staging) là một transaction; mỗi lớp ODS (11 thủ tục), nhóm dimension (9 thủ tục) và nhóm fact (7 thủ tục) được gọi qua `call_procedures` trên một kết nối và chỉ `commit` sau thủ tục cuối, nên một thủ tục lỗi thì cả lớp đó rollback; bước làm mới materialized view là một transaction riêng. Các bước phụ (nạp seed, dựng `dim_date`, `ods.truncate_data()` và `dw.reset_dims()` ở chế độ full) tự commit riêng. Hệ quả: lỗi ở lớp fact không làm mất ODS và dimension đã commit, nhưng lớp fact không bị nạp nửa chừng; chạy lại pipeline sẽ nạp lại từ đầu lớp đó. Lưu ý khi đọc `job_run` sau một lần lỗi: các dòng `success` của thủ tục chạy trước thủ tục lỗi trong cùng lớp vẫn còn (vì ghi bằng kết nối riêng) dù dữ liệu của chúng đã bị rollback; dòng `failed` cho biết lớp nào hỏng.

**17. Vì sao biến đổi bằng SQL procedure thay vì pandas?**
Dữ liệu nằm sẵn trong PostgreSQL, xử lý theo tập hợp (window function, upsert) nhanh và ngắn hơn; Python chỉ điều phối và COPY. Nạp full toàn bộ 1,56 triệu dòng nguồn vào kho mất khoảng 1,5 phút.

**18. Dựng lại toàn bộ dự án mất bao lâu và có tái lập không?**
Một lệnh `python scripts/rebuild_all.py --drop` xoá hai database và dựng lại từ CSV: **407 giây (6,8 phút)**; kết quả giống hệt trước khi xoá (16/16 bảng khớp checksum), 130/130 test đạt khi dựng (133 sau khi thêm test địa lý).

## C. Chất lượng dữ liệu (6 câu)
**19. Dữ liệu nguồn có những lỗi gì và xử lý ra sao?**
EDA đo được 45 loại lỗi. Ví dụ: 1.411 đơn (1,4%) có ít nhất một cờ lỗi (1.359 đơn bàn giao trước khi duyệt, 166 bàn giao trước ngày mua, 23 giao trước bàn giao); các khoảng thời gian âm được đặt trống và đếm lại, **không xoá đơn**. Cột phân loại trống thành `unknown`. Toàn bộ nằm ở `etl_log` (`rejected_rows`, `fact_load_issue`).

**20. Xử lý bảng geolocation 1 triệu dòng như thế nào?**
1.000.163 dòng nhưng chỉ 19.015 mã bưu chính (93,5% zip có nhiều toạ độ khác nhau, 26,2% dòng trùng hoàn toàn, tên thành phố lệch dấu). ODS lọc điểm trong khung Brazil (loại 42 điểm ngoài khung, ghi `rejected_rows`), gom theo zip lấy **trung vị** vĩ/kinh độ và **mode** thành phố/bang đã chuẩn hoá (`lower(unaccent(trim()))`). Mọi zip vẫn có dòng trong `dim_geography`, kể cả zip không có toạ độ (vĩ/kinh độ để trống). Có hai con số cần phân biệt: **5 zip** có trong geolocation nhưng mọi điểm đều nằm ngoài khung Brazil, và **167 zip** không có toạ độ nói chung, gồm 5 zip trên cộng 162 zip có ở customers/sellers nhưng không có trong geolocation (157 zip khách + 7 zip seller, 2 zip trùng). Tính cả dòng Unknown `-1` thì có 168 dòng `dim_geography` với toạ độ trống.

**21. Review bị lặp `review_id` xử lý thế nào?**
Có 789 `review_id` xuất hiện ở nhiều đơn nên không dùng làm khoá chính; khoá là cặp (`review_id`, `order_id`) (99.224 dòng), và ODS khử trùng giữ bản có `review_answer_timestamp` mới nhất nếu có trùng cặp.

**22. Bạn kiểm tra chất lượng kho bằng cách nào?**
136 phép kiểm thử chạy sau mỗi lần pipeline và lưu ở `etl_log.dq_check`: đối soát số dòng nguồn → ODS → kho (chênh = dòng bị loại), tổng tiền (Σ price kho = 13.591.643,70 = file CSV), khoá ngoại hợp lệ, grain không trùng, SCD2 không chồng thời gian, mart khớp fact. Thêm 6 phép đối chiếu với EDA (chỉ báo cáo) như 380 seller có đơn và GMV 13,49 triệu.

**23. GMV khác tổng giá hàng thế nào?**
GMV = Σ `price` của đơn **không** thuộc nhóm Failed (canceled, unavailable) = 13.494.400,74; tổng giá hàng mọi đơn = 13.591.643,70; chênh 97.242,96 là hàng của 1.234 đơn Failed. Dùng GMV làm KPI vì đơn hủy không tạo doanh thu.

**24. Vì sao 462 deal đã chốt lại không có đơn?**
Trong 842 deal, chỉ 380 seller (45,1%) có đơn trong hệ thống bán hàng (mọi trạng thái đơn); nếu chỉ tính đơn không thuộc nhóm Failed (huỷ / không có sẵn) thì còn 379 seller (45,0%) có đơn bán được, là số `Sellers with first sale` trên dashboard. Đây là một **kết quả phân tích**, không phải lỗi: các seller này vẫn có dòng trong `dim_seller` (địa chỉ Unknown, `is_from_funnel = true`) và dashboard D6 hiển thị như một kết quả.

## D. OLAP và mô hình phân tích (5 câu)
**25. Vì sao chọn ROLAP mà không dùng MOLAP?**
Dùng PostgreSQL (không có SSAS); dữ liệu vài trăm nghìn dòng fact nên SQL trả lời dưới 1 giây; kho luôn "tươi" sau mỗi lần nạp tăng dần mà không phải xử lý lại khối đa chiều; Power BI (Import + DAX) làm lớp ngữ nghĩa. MOLAP đổi lại tính sẵn tổng hợp (nhanh hơn) nhưng cần bước process và tốn dung lượng. *Xem: `handoff/olap-examples.md`.*

**26. Minh hoạ roll-up và drill-down trên dữ liệu thật?**
Roll-up bằng `GROUP BY ROLLUP (year, year_quarter)`: GMV 2017 = 6.108.492,27, 2018 = 7.341.182,41. Drill-down: năm 2017 → quý 4 → tháng 11/2017 → ngày; ngày cao nhất là **24/11/2017 (Black Friday) 152.654 BRL**, gấp 5,2 lần GMV trung bình các ngày khác trong tháng.

**27. Slice và dice khác nhau thế nào? Ví dụ?**
Slice cố định **một** chiều: năm 2017 → vùng Sudeste chiếm 64,3% GMV. Dice giới hạn **nhiều** chiều: Sudeste × Home & Furniture × quý 4/2017 → SP 199.179, RJ 76.525, MG 54.125 BRL.

**28. Pivot làm thế nào khi PostgreSQL không có từ khoá PIVOT?**
Dùng tổng có điều kiện `sum(price) FILTER (WHERE d.year = 2017)` để mỗi năm thành một cột (GMV vùng × năm); có thể dùng `crosstab()` của extension `tablefunc` nhưng dự án không cài.

**29. Pareto 80/20 cho kết quả gì?**
18/74 danh mục (24,3%) tạo 80% GMV, đứng đầu `health_beauty` 9,31%. Với seller, 540/3.053 seller có đơn bán được (17,7%) tạo 80% GMV nhưng 5 seller lớn nhất chỉ chiếm 7,7%: doanh thu **phân tán**, không phụ thuộc vài seller.

## E. Hiệu năng (3 câu)
**30. Vì sao star schema chỉ nhanh hơn OLTP 1,0–1,6 lần mà vẫn đáng dùng?**
Dữ liệu còn nhỏ (112 nghìn dòng hàng) và các truy vấn quét gần hết bảng nên chi phí chủ yếu là gom nhóm, không phải join (GMV theo bang × tháng: 657 ms → 506 ms). Giá trị của star schema là **truy vấn đơn giản, nhất quán** (một định nghĩa KPI), tính sẵn (`lead_days`, `delay_days`) và tạo nền cho snapshot/mart; khi dữ liệu lớn hơn nhiều, khoảng cách mới rõ.

**31. Index khoá ngoại và materialized view cải thiện thế nào?**
Index khoá ngoại không đổi truy vấn quét toàn bộ nhưng làm tra cứu một seller **nhanh gấp 9 lần** (0,8 so với 7,3 ms). Materialized view đọc dưới 1 ms (0,04 ms) so với 150–750 ms khi view thường tính lại, đổi lại phải làm mới (≈ 2 giây mỗi lần pipeline).

**32. Vì sao scorecard seller trong dw không nhanh hơn oltp?**
Cả hai đều phải đếm distinct đơn và join review ở mức dòng hàng (≈ 380 ms). Chỉ khi dùng snapshot `fact_seller_monthly` (view scorecard) mới giảm còn ≈ 187 ms, và materialized view còn 0,28 ms: đây là lý do tồn tại của fact snapshot.

## F. Dashboard và Power BI (5 câu)
**33. Vì sao tỷ lệ đúng hạn cao (93,2%) mà review vẫn tệ ở đơn trễ?**
Trễ chỉ chiếm 6,8% đơn nhưng tác động rất mạnh: điểm review 4,29 (giao sớm) → 3,29 (trễ 1–3 ngày) → 2,10 (4–7 ngày) → 1,70 (trên 7 ngày) (số ở kho tính trên từng review: 1.756 review ở nhóm 4–7 ngày; bản EDA `handoff/correlations.md` tính mỗi đơn một lần, 1.748 đơn, nên ra 2,11; nhóm giao sớm 4,29 và nhóm trễ trên 7 ngày 1,70 giống nhau ở cả hai cách tính); 79,2% review tiêu cực ở nhóm trễ trên 7 ngày. Các đơn trễ chiếm 6,5% số review nhưng tạo ra 27,4% số review tiêu cực (4.000/14.575). Trung bình toàn sàn che mất nhóm nhỏ nhưng "đau".

**34. Ngày hứa giao so với thực tế cho thấy điều gì?**
Olist hứa trung bình 24,4 ngày nhưng giao thực tế 12,6 ngày: giao sớm hơn lời hứa 11,8 ngày; 91,9% đơn giao sớm hơn dự kiến. Ngày dự kiến quá rộng nên "đúng hạn" dễ đạt; vì vậy dashboard D3 thêm KPI so sánh số ngày hứa với số ngày thực tế.

**35. Vì sao chọn cửa sổ thời gian 2017-01 → 2018-08?**
Dữ liệu 2016 chỉ 329 đơn và 09–10/2018 chỉ 20 đơn nên xu hướng và MoM/YoY bị méo; cửa sổ này chứa 99,6% số đơn. Cột `InWindow` trong `dim_date` làm bộ lọc trang cho D1–D6.

**36. Role-playing date trong Power BI làm thế nào?**
Mỗi fact có một quan hệ ngày Active (ví dụ ngày mua) và các quan hệ Inactive; muốn tính theo ngày giao, dùng `CALCULATE([Delivered orders], USERELATIONSHIP(fact_order_fulfillment[delivered_date_key], dim_date[date_key]))`. Tránh ambiguous path và vẫn dùng một bảng ngày.

**37. Làm sao bảo đảm số trên dashboard đúng?**
Mọi measure có **giá trị kỳ vọng tính bằng SQL** trong `powerbi/measures.md` cho 4 phạm vi thời gian (ví dụ GMV toàn bộ 13.494.400,74; Orders 98.199; AOV 137,42). Người dựng đối chiếu từng measure; số lệch thì sửa measure hoặc quan hệ.

## G. Giới hạn và hướng phát triển (3 câu)
**38. Những giới hạn của dự án?**
(1) Nạp tăng dần chỉ mô phỏng bản ghi mới với trạng thái cuối, không có đơn đổi trạng thái giữa chừng; (2) cơ chế thử lại mồ côi mới chứng minh bằng test; (3) toạ độ theo mã bưu chính (không phải địa chỉ), haversine là đường chim bay (sai số ≤ 0,5%); (4) dữ liệu 2016 và cuối 2018 thưa; (5) chỉ 45,1% deal có đơn nên so sánh theo kênh nhỏ (kênh Email chỉ 6 seller có đơn, đánh dấu mẫu nhỏ); (6) benchmark gọn trên một laptop.

**39. Vì sao không dùng PostGIS và khoảng cách địa lý tính thế nào?**
Quyết định thiết kế ngày 05/11 (ghi trong nhật ký của `DW_DESIGN.md`): không dùng PostGIS, khoảng cách seller → khách tính bằng công thức haversine viết thành hàm SQL thuần `dw.haversine_km` trên cột `latitude`/`longitude`, và `dim_geography` không có cột `geometry`. Lý do: bài toán chỉ cần khoảng cách điểm–điểm cho 112 nghìn cặp seller–khách, hàm SQL thuần đủ và không thêm extension nào phải cài. Kết quả: khoảng cách TB 598 km, khoảng cách tăng từ < 100 km lên > 1.000 km thì phí vận chuyển 11,75 → 31,65 BRL và lead time 6,5 → 19,0 ngày (Spearman 0,63 và 0,54). PostGIS sẽ cần khi muốn truy vấn bán kính hoặc vùng đa giác (chỉ mục GiST).

**40. Nếu mở rộng, bạn sẽ làm gì tiếp?**
Thêm trạng thái trung gian của đơn (CDC thật) và lịch chạy tự động; chuyển toạ độ sang PostGIS khi cần truy vấn không gian; phân vùng `fact_order_item` theo năm khi dữ liệu lớn; thêm chiều khuyến mãi/sản phẩm theo thời gian (SCD cho giá); và đo hiệu năng nhiều người dùng đồng thời.

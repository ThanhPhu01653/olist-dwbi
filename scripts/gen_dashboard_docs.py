"""Generate huong-dan/dashboards/DB1.md ... DB4.md and README.md (P8b: four dashboards, merged from the former D1-D7).

    python scripts/gen_powerbi_docs.py       # first: expected values per dashboard in powerbi/measures.md
    python scripts/gen_dashboard_docs.py
SRC below holds the narrative blocks of the former seven dashboards (goal, layout grid, slicers, insights); DB1-DB4 merge them as
DB1 = D1 + D2, DB2 = D3 + D5, DB3 = D4, DB4 = D6 and add the new pages (tooltips, Key Influencers, drill-through pages).
The "expected values" tables of each dashboard are copied from the generated section 7 of powerbi/measures.md (SQL on olist_dw).
D7 (data quality and ETL monitor) is no longer a dashboard: its numbers are in report section 3.3 (scripts/p8_etl.py).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

M = "powerbi/measures.md"
COMMON_FILTER = "Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08)."

SRC = {
    "D1": dict(
        title="D1 – Executive Overview", kind="Theo thời gian",
        goal="Cho lãnh đạo thấy sức khoẻ toàn doanh nghiệp trong một trang: doanh thu, giao hàng, hài lòng, và xu hướng theo tháng.",
        questions=["Doanh thu (GMV) bao nhiêu, tăng hay giảm so với tháng trước và cùng kỳ năm trước?", "Giao hàng có đúng hạn không, tỷ lệ hủy bao nhiêu?", "Khách hài lòng không (điểm review)?",
                   "Vùng nào và nhóm ngành nào đóng góp nhiều nhất?"],
        kpis=[("GMV", "doanh thu hàng bán (không tính đơn Failed)"), ("Orders", "số đơn có doanh thu"), ("AOV", "giá trị TB mỗi đơn"), ("On-time rate", "tỷ lệ giao đúng hạn"),
              ("Avg review", "điểm review TB"), ("Cancel rate", "tỷ lệ hủy"), ("GMV MoM %", "tăng trưởng so với tháng trước"), ("GMV YoY %", "tăng trưởng so với cùng kỳ năm trước"),
              ("GMV last year", "đường so sánh cùng kỳ")],
        grid=[("1", "1–2", "Card", "GMV (+ `GMV MoM %` làm chú thích, màu `Color growth`)"), ("1", "3–4", "Card", "Orders"), ("1", "5–6", "Card", "AOV"),
              ("1", "7–8", "Card", "On-time rate (màu `Color On-time rate`)"), ("1", "9–10", "Card", "Avg review (màu `Color Avg review`)"), ("1", "11–12", "Card", "Cancel rate (màu `Color Cancel rate`)"),
              ("2", "1–8", "Line chart (đường)", "trục `dim_date[year_month]`; giá trị `GMV` và `GMV last year`"), ("2", "9–12", "Clustered column (cột)", "`GMV MoM %` theo tháng, màu theo `Color growth`"),
              ("3", "1–4", "Bar chart ngang", "`GMV` theo `dim_geography[region]`"), ("3", "5–8", "Treemap", "`GMV` theo `dim_product[category_group]`"),
              ("3", "9–12", "Gauge hoặc KPI visual", "`On-time rate` với mục tiêu 95%")],
        slicers=["`dim_date[year]` (dạng nút)", "`dim_geography[region]` (danh sách)", "`dim_order_status[status_group]` (mặc định bỏ chọn; GMV vốn đã loại Failed)"],
        drill=["Line chart: Date hierarchy Năm → Quý → Tháng (mũi tên drill-down)", "Treemap: nhóm ngành → danh mục (`Product` hierarchy)"],
        cf=["Cards On-time rate / Avg review / Cancel rate: **Field value** theo `Color …` (xanh / vàng / đỏ)", "Cột `GMV MoM %`: xanh nếu dương, đỏ nếu âm (`Color growth`)"],
        dax=[("Tăng trưởng và cảnh báo", "GMV last month = CALCULATE ( [GMV], DATEADD ( dim_date[full_date], -1, MONTH ) )\nGMV MoM % = DIVIDE ( [GMV] - [GMV last month], [GMV last month] )\nAlert text = (xem powerbi/measures.md mục 9)")],
        measures=["GMV", "Orders", "AOV", "On-time rate", "Avg review", "Cancel rate", "Freight ratio", "Orders placed"],
        insights=["GMV tăng từ 120.098 BRL (01/2017) lên **1.003.862 BRL (11/2017)**, tháng cao nhất; **+52,1% so với 10/2017** nhờ Black Friday 24/11/2017 (một ngày 152.654 BRL, gấp 5,2 lần ngày thường trong tháng).",
                  "Từ 03/2018 GMV đi ngang quanh 0,85–0,99 triệu BRL/tháng, nhưng vẫn **cao hơn cùng kỳ năm trước**: 05/2018 +97,3%, 08/2018 +49,4%.",
                  "**Vùng Sudeste chiếm 65,4% GMV** (8,79 / 13,45 triệu BRL trong cửa sổ), Norte chỉ 2,5%: thị trường tập trung rất mạnh.",
                  "Giao đúng hạn 93,2% nhưng **tụt còn 87,6% ở 11/2017** (tháng Black Friday) và 81,0% ở 03/2018: tải cao làm giao chậm.",
                  "Nhóm ngành hàng dẫn đầu: Home & Furniture 22,8% GMV, tiếp theo Gifts & Others và Electronics & Computers (14,0% mỗi nhóm)."],
        extra="Chân trang ghi: *GMV không gồm đơn hủy / không khả dụng; số liệu BRL; giai đoạn 2017-01 → 2018-08.*"),
    "D2": dict(
        title="D2 – Sales & Product", kind="Theo thời gian, OLAP",
        goal="Đào sâu doanh số theo sản phẩm: ngành hàng nào bán chạy, quy luật 80/20, giá và phí vận chuyển theo ngành.",
        questions=["Nhóm ngành / danh mục nào tạo nhiều GMV nhất và thay đổi thế nào theo quý?", "Bao nhiêu danh mục tạo 80% GMV (Pareto)?", "AOV và phí vận chuyển của từng ngành ra sao?"],
        kpis=[("GMV", "doanh thu"), ("Items", "số dòng hàng đã bán"), ("AOV", "giá trị TB mỗi đơn"), ("Freight ratio", "phí vận chuyển / giá hàng"), ("Avg items per order", "số dòng hàng TB mỗi đơn")],
        grid=[("1", "1–3", "Card", "GMV"), ("1", "4–6", "Card", "Items"), ("1", "7–9", "Card", "AOV"), ("1", "10–12", "Card", "Freight ratio"),
              ("2", "1–5", "Treemap", "`dim_product[category_group]` → `GMV`"), ("2", "6–12", "Combo cột + đường (Pareto)", "bảng `v_category_pareto`: trục `category_name_en` (sắp theo `gmv_rank`), cột `gmv`, đường `cum_share_pct`; màu theo `abc_class`"),
              ("3", "1–7", "Matrix", "hàng: hierarchy Product; cột `dim_date[year_quarter]`; giá trị `GMV`, `Items`, `AOV`"), ("3", "8–12", "Scatter", "x `AOV`, y `Freight ratio`, chi tiết `category_group`, kích thước `GMV`")],
        slicers=["`dim_date[year_quarter]`", "`dim_product[category_group]`", "`dim_product[size_class]`", "`dim_geography[state_code]`"],
        drill=["Matrix và treemap: hierarchy Product (nhóm ngành → danh mục → sản phẩm)", "Matrix: mở cột Quý → Tháng"],
        cf=["Matrix: **color scale** (nền) trên `GMV`", "Pareto: cột tô theo hạng A/B/C (A xanh, B vàng, C xám)", "Scatter: điểm có `Freight ratio` > 25% màu đỏ (`Color Freight ratio`)"],
        dax=[("Tỷ trọng và luỹ kế (nếu không dùng bảng mart)", "GMV share = DIVIDE ( [GMV], CALCULATE ( [GMV], ALL ( dim_product ) ) )\nAvg items per order = DIVIDE ( [Items], [Orders] )")],
        measures=["GMV", "Orders", "Items", "AOV", "Freight", "Freight ratio"],
        insights=["**18/74 danh mục (24,3%) tạo 80% GMV**; đứng đầu `health_beauty` (9,31%).", "Home & Furniture dẫn đầu với 3,07 triệu BRL (22,8% GMV trong cửa sổ).",
                  "AOV toàn sàn 137,42 BRL; phí vận chuyển chiếm 16,6% giá hàng, nhưng **nặng hơn ở hàng giá thấp** (xem scatter AOV – Freight ratio).",
                  "Doanh số theo quý tăng rõ: quý 4/2017 là 2,41 triệu BRL so với 0,73 triệu ở quý 1/2017.", "Quy luật 80/20 ở seller yếu hơn: 540/3.053 seller (17,7%) tạo 80% GMV nhưng 5 seller lớn nhất chỉ chiếm 7,7%."],
        extra=""),
    "D3": dict(
        title="D3 – Order Fulfillment", kind="Vận hành",
        goal="Theo dõi chu trình xử lý đơn: mỗi chặng mất bao lâu, vùng nào chậm, lời hứa giao hàng có sát thực tế không.",
        questions=["Đơn mất bao lâu ở từng chặng (duyệt → bàn giao → giao)?", "Tỷ lệ giao trễ và hủy là bao nhiêu, vùng/bang nào chậm nhất?", "Ngày hứa giao so với ngày giao thực tế chênh bao nhiêu?"],
        kpis=[("On-time rate / Late rate", "đúng hạn / trễ"), ("Avg lead days", "mua → giao"), ("Avg approval hours", "mua → duyệt"), ("Avg handling days", "duyệt → bàn giao"), ("Avg transit days", "bàn giao → giao"),
              ("Avg promised days", "số ngày hứa giao"), ("Promised vs actual (days)", "**KPI ngày hứa giao so với thực tế** (dương = giao sớm hơn lời hứa)"), ("Early delivery rate", "đơn giao sớm hơn dự kiến"), ("Cancel rate", "tỷ lệ hủy")],
        grid=[("1", "1–3", "Card", "On-time rate (`Color On-time rate`)"), ("1", "4–6", "Card", "Avg lead days"), ("1", "7–9", "Card", "Avg promised days"), ("1", "10–12", "Card", "Promised vs actual (days) (`Color promised vs actual`)"),
              ("2", "1–4", "Funnel", "bảng `v_status_funnel` (lọc `in_window`): `stage` (sắp theo `stage_no`) → `orders`"), ("2", "5–12", "Stacked column", "trục `year_month`; giá trị `Avg handling days`, `Avg transit days` (và `Avg approval hours` ở trục phụ hoặc đổi sang ngày)"),
              ("3", "1–6", "Map hoặc bar chart", "`Late rate` theo `dim_geography[state_code]`, màu theo `Color On-time rate`"), ("3", "7–12", "Clustered column", "`Avg promised days` và `Avg lead days` theo `dim_geography[region]`"),
              ("4", "1–6", "Column", "số đơn theo cột tính toán `fact_order_fulfillment[Delay bucket]`"), ("4", "7–12", "Table", "bang, đơn đã giao, `Late rate`, `Avg lead days`, `Cancel rate` (conditional formatting)")],
        slicers=["`dim_date[year_month]`", "`dim_geography[region]`", "`dim_order_status[order_status]`", "`dim_product[category_group]` (tuỳ chọn)"],
        drill=["Bản đồ / bảng: hierarchy Geography (vùng → bang → thành phố)", "Drill-through sang trang chi tiết đơn (tuỳ chọn)"],
        cf=["Card và bảng: màu theo `Color On-time rate`, `Color Cancel rate`, `Color promised vs actual`", "Bản đồ: thang màu từ xanh đến đỏ theo `Late rate`"],
        dax=[("KPI ngày hứa giao so với thực tế", "Promised vs actual (days) =\nAVERAGEX ( FILTER ( fact_order_fulfillment, fact_order_fulfillment[is_delivered] = 1\n    && NOT ISBLANK ( fact_order_fulfillment[lead_days] ) && NOT ISBLANK ( fact_order_fulfillment[promised_days] ) ),\n    fact_order_fulfillment[promised_days] - fact_order_fulfillment[lead_days] )"),
             ("Role-playing date: đơn theo ngày giao", "Delivered orders by delivery date =\nCALCULATE ( [Delivered orders], USERELATIONSHIP ( fact_order_fulfillment[delivered_date_key], dim_date[date_key] ) )")],
        measures=["Orders placed", "Delivered orders", "Late orders", "On-time rate", "Early delivery rate", "Avg lead days", "Avg approval hours", "Avg handling days", "Avg transit days",
                  "Avg promised days", "Avg delay days", "Promised vs actual (days)", "Failed orders", "Cancel rate"],
        insights=["Olist **hứa TB 24,4 ngày nhưng giao thực tế 12,6 ngày**: giao sớm hơn lời hứa 11,8 ngày, 91,9% đơn giao sớm hơn dự kiến → \"đúng hạn\" 93,2% dễ đạt vì ngày dự kiến quá rộng.",
                  "Chặng dài nhất là **vận chuyển (9,3 ngày)**, bàn giao của seller 2,9 ngày, duyệt 10,3 giờ.", "**Nordeste trễ nhiều nhất (12,8%)**, Sudeste 6,1%; Norte có lead time dài nhất (22,6 ngày so với 10,7 ngày ở Sudeste). Bang MA trễ 17,4%.",
                  "Đúng hạn tụt từ 95,8% (10/2017) xuống **87,6% (11/2017, Black Friday)** và 81,0% (03/2018): đợt cao điểm làm vận chuyển quá tải.", "Tỷ lệ hủy / không khả dụng toàn sàn chỉ 1,24% (1.234 đơn)."],
        extra="Lưu ý: 1.359 đơn có `carrier_before_approved` (bàn giao trước khi duyệt) nên `handling_days` của các đơn này để trống; cờ lỗi nằm ở `etl_log.fact_load_issue`."),
    "D4": dict(
        title="D4 – Geography & Freight", kind="OLAP",
        goal="Cho thấy doanh số và phí vận chuyển phân bố theo địa lý, và quan hệ giữa khoảng cách, phí vận chuyển và thời gian giao.",
        questions=["GMV tập trung ở vùng / bang nào?", "Phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng?", "Seller và khách xa nhau bao nhiêu và điều đó ảnh hưởng freight và lead time ra sao?"],
        kpis=[("GMV", "doanh thu"), ("Freight", "phí vận chuyển"), ("Freight ratio", "freight / giá hàng"), ("Avg lead days", "thời gian giao TB"), ("GMV by seller state", "GMV theo địa lý seller (role-playing)")],
        grid=[("1", "1–4", "Card", "GMV; Freight ratio"), ("1", "5–8", "Card", "Avg lead days"), ("1", "9–12", "Card", "Số bang / zip có đơn (đếm `dim_geography[state_code]`)"),
              ("2", "1–7", "Map (bản đồ bong bóng)", "vị trí `latitude`/`longitude` của `dim_geography` (hoặc bảng `v_geo_state`); kích thước `GMV`; màu `Freight ratio`"),
              ("2", "8–12", "Bar chart", "`Freight ratio` theo `state_code` (top 10), màu theo `Color Freight ratio`"),
              ("3", "1–6", "Matrix", "hierarchy Geography (vùng → bang → thành phố); giá trị `GMV`, `Freight`, `Freight ratio`, `Avg lead days`"),
              ("3", "7–12", "Clustered column", "`GMV` (địa lý khách) cạnh `GMV by seller state` (địa lý seller) theo `region`")],
        slicers=["`dim_date[year]`", "`dim_product[category_group]`", "`dim_product[size_class]`", "`dim_geography[region]`"],
        drill=["Hierarchy Geography: Vùng → Bang → Thành phố → Zip", "Bản đồ: drill từ bang xuống thành phố"],
        cf=["Matrix: data bars trên `GMV`; màu `Freight ratio` theo `Color Freight ratio`", "Bản đồ: màu bong bóng theo `Freight ratio`"],
        dax=[("Địa lý seller bằng USERELATIONSHIP", "GMV by seller state =\nCALCULATE ( [GMV], USERELATIONSHIP ( fact_order_item[seller_geography_key], dim_geography[geography_key] ) )")],
        measures=["GMV", "Orders", "Freight", "Freight ratio", "Avg lead days"],
        insights=["**Sudeste 65,4% GMV, Sul 14,4%, Nordeste 11,4%, Centro-Oeste 6,4%, Norte 2,5%.**", "Phí vận chuyển nặng ở vùng xa: **Norte 22,7% và Nordeste 21,7% giá hàng so với 15,2% ở Sudeste**.",
                  "Từ dưới 100 km lên trên 1.000 km, phí vận chuyển TB tăng 11,75 → 31,65 BRL và lead time 6,5 → 19,0 ngày (xem `handoff/geo-distance.md`).",
                  "Seller và khách **cùng bang ở 36,1%** dòng hàng; khoảng cách TB 598 km (trung vị 433 km).", "555 dòng hàng (0,49%) không tính được khoảng cách vì thiếu toạ độ; cần ghi chú trên trang."],
        extra="Mart hỗ trợ: `v_geo_state` (27 bang), `v_geo_zip` (14.889 zip), `v_shipping_distance` (khoảng cách từng dòng hàng, không xuất CSV)."),
    "D5": dict(
        title="D5 – Customer Experience", kind="Thống kê",
        goal="Hiểu trải nghiệm khách hàng: điểm đánh giá, ảnh hưởng của giao trễ, cơ cấu thanh toán, khách quay lại.",
        questions=["Điểm review TB bao nhiêu, bao nhiêu % tiêu cực?", "Giao trễ làm điểm review giảm thế nào?", "Khách thanh toán bằng gì, trả góp bao nhiêu kỳ?", "Bao nhiêu khách quay lại; phân khúc RFM và cohort?"],
        kpis=[("Avg review", "điểm review TB"), ("% negative", "% review tiêu cực (≤ 2 điểm)"), ("Avg review - late delivery / on time", "điểm TB đơn trễ / không trễ"), ("Payment value / Payment share", "giá trị và tỷ trọng thanh toán"),
              ("Avg installments", "số kỳ trả góp"), ("Repeat customer rate", "khách quay lại (≥ 2 đơn)")],
        grid=[("1", "1–3", "Card", "Avg review (`Color Avg review`)"), ("1", "4–6", "Card", "% negative (`Color % negative`)"), ("1", "7–9", "Card", "Repeat customer rate"), ("1", "10–12", "Card", "Avg installments"),
              ("2", "1–6", "Clustered column", "bảng `v_review_vs_delay`: trục `delay_bucket` (sắp theo `delay_bucket_no`), giá trị `avg_score`"), ("2", "7–12", "Column", "`fact_review[review_score]` → `Reviews` (phân bố 1–5 sao)"),
              ("3", "1–4", "Donut", "`dim_payment_type[display_name]` → `Payment value`"), ("3", "5–8", "Bar chart", "bảng `v_customer_rfm`: `segment` → đếm `customer_unique_id`"),
              ("3", "9–12", "Matrix (heatmap)", "bảng `v_customer_cohort`: hàng `cohort_month`, cột `months_since`, giá trị `retention_pct` (color scale)")],
        slicers=["`dim_date[year_month]`", "`dim_geography[region]`", "`dim_payment_type[payment_group]`"],
        drill=["Cohort: drill từ năm xuống tháng", "Bảng RFM: drill-through sang danh sách khách (ẩn mã nếu cần)"],
        cf=["Card review: theo `Color Avg review`, `Color % negative`", "Cohort: **color scale** trắng → xanh đậm", "Cột `avg_score` theo nhóm trễ: màu đỏ nếu < 3"],
        dax=[("Tách điểm review theo giao trễ", "Avg review - late delivery = CALCULATE ( [Avg review], fact_review[is_delivered] = 1, fact_review[delivered_late] = 1 )\nAvg review - on time = CALCULATE ( [Avg review], fact_review[is_delivered] = 1, fact_review[delivered_late] = 0 )"),
             ("Khách quay lại", "Repeat customers =\nCOUNTROWS ( FILTER ( VALUES ( dim_customer[customer_unique_id] ), CALCULATE ( COUNTROWS ( fact_order_fulfillment ) ) >= 2 ) )")],
        measures=["Reviews", "Avg review", "% negative", "Avg review - late delivery", "Avg review - on time", "Payments", "Payment value", "Avg installments", "Customers", "Repeat customers", "Repeat customer rate"],
        insights=["**Điểm review tụt theo mức trễ: 4,29 (giao sớm) → 3,29 (trễ 1–3 ngày) → 2,10 (4–7) → 1,70 (trên 7 ngày)**; % tiêu cực tăng 9,2% → 79,2%.", "Đơn trễ chỉ chiếm 6,5% số review nhưng tạo **27,4% số review tiêu cực** (4.000/14.575).",
                  "Thẻ tín dụng chiếm **78,3% giá trị thanh toán**, boleto 17,9%; thẻ trả góp TB 3,5 kỳ và 66,9% giao dịch thẻ trả góp nhiều kỳ.", "Chỉ **3,12% khách mua lại** (2.997/96.096); cohort cho thấy tỷ lệ quay lại sau 1 tháng chỉ ~0,5%.",
                  "RFM: 94.983 khách; \"Ngủ đông\" 36.957 và \"Khách mới\" 36.752 chiếm gần hết; chỉ 129 khách Champions."],
        extra=""),
    "D6": dict(
        title="D6 – Seller Acquisition & Performance (2 trang)", kind="Vận hành",
        goal="Đo hiệu quả thu hút seller: kênh nào chuyển đổi tốt, chốt deal mất bao lâu, seller từ funnel có bán được không (luôn ghi cỡ mẫu).",
        questions=["Bao nhiêu % MQL được chốt, theo kênh?", "Chốt deal và có đơn đầu tiên mất bao lâu?", "Seller từ funnel đóng góp GMV bao nhiêu, giao trễ và review ra sao?", "Seller nào GMV cao nhưng hay trễ?"],
        kpis=[("MQLs", "số khách tiềm năng"), ("Won deals", "đã chốt"), ("MQL to won rate", "tỷ lệ chốt"), ("Avg days to close", "ngày liên hệ → chốt"), ("Sellers with first sale", "seller đã có đơn"),
              ("Won to first sale rate", "đã chốt → có đơn"), ("Avg days won to first sale", "chốt → đơn đầu"), ("Seller GMV first 90d", "GMV 90 ngày đầu"), ("Small sample warning", "cảnh báo mẫu nhỏ")],
        grid=[("Trang 1", "1–5", "Funnel", "`MQLs` → `Won deals` → `Sellers with first sale`"), ("Trang 1", "6–12", "Bar chart", "`MQL to won rate` theo `dim_lead_origin[origin]` (kèm `MQLs` ở tooltip)"),
              ("Trang 1", "1–4", "Card", "Won to first sale rate; Avg days won to first sale; Seller GMV first 90d"), ("Trang 1", "5–8", "Column", "`Avg days to close` theo `dim_lead_origin[channel_group]`"),
              ("Trang 1", "9–12", "Line chart", "`MQLs` theo `year_month` (tháng liên hệ đầu), tách theo `channel_group`"),
              ("Trang 2", "1–6", "Table", "`v_seller_scorecard` lọc `is_from_funnel = TRUE`: `seller_id`, `acquisition_channel`, `orders`, `gmv`, `late_rate_pct`, `avg_review_score`, `small_sample`"),
              ("Trang 2", "7–12", "Column + chữ", "`v_seller_by_channel`: `acquisition_channel` → `gmv_per_selling_seller`; `selling_sellers` và `small_sample` hiện kèm"),
              ("Trang 2", "1–6", "Scatter", "`v_seller_scorecard`: x `gmv`, y `late_rate_pct`, kích thước `orders` (seller GMV cao nhưng hay trễ)"), ("Trang 2", "7–12", "Card", "Won deals − Sellers with first sale = deal chốt nhưng chưa bán (462)")],
        slicers=["`dim_lead_origin[channel_group]`", "`dim_lead_profile[business_segment]`", "`v_seller_scorecard[acquisition_channel]`, `[state_code]` (trang 2)"],
        drill=["Origin → kênh (hierarchy Lead origin)", "Bảng seller: drill-through sang `fact_seller_monthly` của seller (đường GMV theo tháng)"],
        cf=["Cột `late_rate_pct`: đỏ nếu > 10%", "`small_sample = TRUE`: chữ xám và dòng cảnh báo `Small sample warning`", "Cột `avg_review_score`: xanh/vàng/đỏ theo `Color Avg review`"],
        dax=[("Cảnh báo mẫu nhỏ", "Small sample warning = IF ( [Active sellers] < 30, \"⚠ Mẫu nhỏ (dưới 30 seller)\", \"\" )"),
             ("Role-playing date: deal theo ngày chốt", "Won deals by won date = CALCULATE ( [Won deals], USERELATIONSHIP ( fact_lead_funnel[won_date_key], dim_date[date_key] ) )")],
        measures=["MQLs (theo tháng liên hệ đầu)", "Won deals", "MQL to won rate", "Avg days to close", "Sellers with first sale", "Won to first sale rate", "Avg days won to first sale", "Seller GMV first 90d",
                  "Active sellers (fact_seller_monthly)", "Seller late rate"],
        insights=["**8.000 MQL → 842 deal (10,5%) → 379 seller có đơn bán được (45,0% số đã chốt, tức 4,74% MQL)**; 462 deal chốt nhưng chưa bán.", "Tỷ lệ chốt theo origin: `unknown` 16,7%, `paid_search` 12,3%, `organic_search` 11,8%… thấp nhất `email` 3,0% (493 MQL) và `other` 2,7% (150 MQL).",
                  "Thời gian chốt TB 48,5 ngày (Social 61,0; Paid 55,0; Organic 45,9; Unknown 41,9); từ chốt đến đơn đầu TB 51,9 ngày.",
                  "Seller từ funnel chỉ tạo ~5% GMV: kênh Organic 153 seller có đơn (GMV 246.767), Unknown 85 (214.726), Paid 103 (153.720), Social 31, Email 6 (**mẫu nhỏ**), Other 2 (**mẫu nhỏ**).",
                  "Seller Unknown có **GMV/seller cao nhất (2.526 BRL)** trong các nhóm funnel nhưng mẫu 85 seller; Organic chỉ 1.613 BRL/seller – cần nói rõ cỡ mẫu khi so sánh."],
        extra="Trang 2 dùng bảng mart (toàn bộ giai đoạn, không lọc ngày): ghi rõ trên tiêu đề."),
}

# ======================================================================================================================
# P8b: the dashboard set is DB1-DB4 (merged from the seven blocks above; D7 is dropped: its numbers go to report section 3.3)
# ======================================================================================================================
SYM = {"yes": "✓", "no": "–"}

# checklist items (README matrix rows)
ITEMS = [
    ("Định dạng số", "mọi số dùng đơn vị rút gọn và dấu phân cách; phần trăm 1 chữ số thập phân", "số đơn 12.3K; tiền 13.5M; 12,4%"),
    ("Tiêu đề dạng câu hỏi", "mỗi visual có tiêu đề là câu hỏi mà nó trả lời", "\"GMV tháng này tăng hay giảm so với tháng trước?\""),
    ("Màu đỏ chỉ để cảnh báo", "đỏ chỉ ở giá trị xấu hoặc vượt ngưỡng; màu dữ liệu của chủ đề không có đỏ", "`powerbi/theme.json`"),
    ("Định dạng có điều kiện", "measure DAX trả về màu (`Color …`) cho card, bảng, bản đồ", "`powerbi/measures.md` mục 6"),
    ("Slicer phân cấp", "slicer theo phân cấp (Năm → Quý → Tháng; Vùng → Bang; Nhóm kênh → Origin)", "hierarchy trong `powerbi/model.md`"),
    ("OLAP drill-down / roll-up", "biểu đồ, ma trận, bản đồ có drill-down và drill-up theo phân cấp", "DB3: Vùng → Bang → Thành phố → Zip"),
    ("Drill-through", "chuột phải một điểm để sang trang chi tiết", "DB3: chi tiết bang; DB4: chi tiết seller"),
    ("Tooltip", "di chuột hiện trang tooltip", "`Tooltip_Thang`, `Tooltip_Muc_tre`, `Tooltip_Bang`, `Tooltip_Kenh`"),
    ("Chuỗi thời gian có dự báo", "line chart theo tháng có đường dự báo (Analytics → Forecast)", "DB1: GMV theo tháng"),
    ("Thống kê: Key Influencers", "visual AI cho biết yếu tố nào đi kèm kết quả cần giải thích", "DB2: review tiêu cực"),
    ("Publish web và mã QR", "publish công khai (không cần đăng nhập) và mã QR của link", "`powerbi/model.md` mục 9"),
]
# 1 = dashboard satisfies the item (yes), 0 = not applicable
MATRIX = {
    "DB1": [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
    "DB2": [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1],
    "DB3": [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
    "DB4": [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1],
}

FMT = {
    "DB1": [("GMV", "tiền", '`#,0.0,,"M"` → 13.5M'), ("Orders, Items", "số", '`#,0.0,"K"` → 98.2K'), ("AOV", "tiền", "`#,0.0` → 137.4"), ("On-time rate, Cancel rate, Freight ratio", "phần trăm", "`0.0%` → 93.2%"),
            ("Avg review", "điểm", "`0.00` → 4.09"), ("GMV MoM %, GMV YoY %", "phần trăm", "`+0.0%;-0.0%`")],
    "DB2": [("Avg lead days, Avg promised days, Promised vs actual", "ngày", "`0.0` → 12.6"), ("On-time rate, Late rate, Cancel rate, % negative, Repeat customer rate", "phần trăm", "`0.0%`"),
            ("Orders placed, Reviews", "số", '`#,0.0,"K"`'), ("Avg review", "điểm", "`0.00`"), ("Payment value", "tiền", '`#,0.0,,"M"`'), ("Avg installments", "số kỳ", "`0.0`")],
    "DB3": [("GMV theo bang", "tiền", '`#,0.0,"K"` hoặc `#,0.0,,"M"`'), ("Freight ratio, Late rate", "phần trăm", "`0.0%`"), ("Avg lead days", "ngày", "`0.0`"), ("Khoảng cách", "km", "`#,0`")],
    "DB4": [("MQLs, Won deals", "số", "`#,0`"), ("MQL to won rate, Won to first sale rate, Seller late rate", "phần trăm", "`0.0%`"), ("Avg days to close, Avg days won to first sale", "ngày", "`0.0`"),
            ("Seller GMV (monthly), Seller GMV first 90d", "tiền", '`#,0.0,"K"`')],
}

FILTER_DB = "Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08)."

DB = {
    "DB1": dict(
        title="DB1 – Tổng quan và doanh thu", kind="Theo dòng thời gian, có dự báo", builder="Người 1",
        goal="Cho thấy sức khoẻ doanh thu của sàn trong một dashboard: doanh thu, giao hàng, hài lòng và xu hướng theo tháng (kèm dự báo), rồi đào sâu doanh số theo sản phẩm: ngành hàng nào bán chạy, quy luật 80/20, giá và phí vận chuyển theo ngành.",
        sources=["D1", "D2"],
        users=[("Ban điều hành", "Doanh thu có tăng không? Giao hàng và khách hàng ra sao?", "hằng tuần, hằng tháng"), ("Quản lý kinh doanh và danh mục", "Nhóm ngành nào bán chạy; giá và phí vận chuyển theo ngành?", "hằng tuần")],
        pages=[("Trang 1 – Tổng quan", "D1", None), ("Trang 2 – Doanh thu theo sản phẩm", "D2", None)],
        extra_pages=[("Trang tooltip `Tooltip_Thang`", [("1", "1–12", "Card ×4", "`GMV`, `Orders`, `AOV`, `On-time rate` theo tháng đang trỏ (*Page size = Tooltip*, *Allow use as tooltip = On*)")])],
        drill_extra=["Chuỗi thời gian có dự báo: line chart `GMV` theo `dim_date[year_month]` → ngăn *Analytics* → *Forecast* → *Forecast length = 3 điểm*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng nên dự báo chỉ để thấy hướng đi; ghi chú cạnh biểu đồ (xem báo cáo mục 3.1: chưa đủ cơ sở kết luận mùa vụ theo năm).",
                     "Tooltip: gán `Tooltip_Thang` cho đường GMV và cột `GMV MoM %`; gán một tooltip theo nhóm ngành cho treemap (GMV, Items, AOV, Freight ratio)."],
        slicer_hier=["Slicer thời gian dạng phân cấp: `dim_date` Năm → Quý → Tháng (trang 1 dùng `year`, trang 2 dùng `year_quarter`)"],
        insights_extra=[]),
    "DB2": dict(
        title="DB2 – Giao hàng và trải nghiệm khách", kind="Vận hành và thống kê (Key Influencers)", builder="Người 2",
        goal="Theo dõi chu trình xử lý đơn (mỗi chặng mất bao lâu, vùng nào chậm, lời hứa giao có sát thực tế không), hiểu trải nghiệm khách (điểm review, ảnh hưởng của giao trễ, thanh toán, khách quay lại) và dùng Key Influencers để chỉ ra yếu tố đi kèm review tiêu cực.",
        sources=["D3", "D5"],
        users=[("Quản lý vận hành và logistics", "Chặng nào chậm; bang nào trễ nhiều; ngày hứa so với thực tế?", "hằng ngày đến hằng tuần"), ("Chăm sóc khách hàng", "Vì sao review thấp; khách nào quay lại; thanh toán ra sao?", "hằng tuần")],
        pages=[("Trang 1 – Giao hàng", "D3", None), ("Trang 2 – Trải nghiệm khách", "D5", None)],
        extra_pages=[("Trang 3 – Yếu tố ảnh hưởng đến review tiêu cực (Key Influencers)",
                      [("1", "1–9", "Key influencers (visual AI)", "*Analyze* `fact_review[Review type]` = **Tiêu cực**; *Explain by* `fact_review[delivered_late]`, `Delay days (order)`, `Lead days (order)`, `Promised days (order)`, `Freight (order)`, `Order value (order)`, `Item count (order)`, `fact_review[has_comment_message]`, `dim_customer[state_code]`, `dim_date[year_quarter]`"),
                       ("1", "10–12", "Card ×3", "`% negative`; `Avg review - late delivery`; `Avg review - on time`"),
                       ("2", "1–12", "Văn bản", "chú thích: \"mô hình thống kê tự động, cho thấy yếu tố đi kèm review tiêu cực, không chứng minh nhân quả\"")]),
                     ("Trang tooltip `Tooltip_Muc_tre`", [("1", "1–12", "Card + cột", "số review, điểm TB, % tiêu cực theo nhóm trễ (gán vào cột `v_review_vs_delay`)")])],
        key_influencers=True,
        drill_extra=["Key Influencers: thêm 7 cột tính toán vào `fact_review` bằng `LOOKUPVALUE` theo `order_id` (mã DAX ở `powerbi/model.md` mục 8, DB2 trang 3). Kỳ vọng từ khám phá dữ liệu: giao trễ là yếu tố liên hệ mạnh nhất với review tiêu cực (Cramér's V 0,403; η của điểm review theo cờ trễ 0,392); sau khi dựng, ghi các yếu tố đứng đầu mà visual trả về vào báo cáo.",
                     "Tooltip: gán `Tooltip_Muc_tre` cho cột điểm review theo nhóm trễ; gán một tooltip theo bang (Late rate, Avg lead days, Orders) cho bản đồ ở trang 1."],
        slicer_hier=["Slicer thời gian dạng phân cấp `dim_date` Năm → Quý → Tháng và slicer địa lý Vùng → Bang"],
        insights_extra=["**Key Influencers** (kỳ vọng, cần xác nhận sau khi dựng): giao trễ đứng đầu các yếu tố đi kèm review tiêu cực; theo khám phá dữ liệu, tỷ lệ review tiêu cực là 12,8% ở đơn đã giao so với 76,7% ở đơn hủy (số trong `handoff/2026-11-14-P8-eda.md`)."]),
    "DB3": dict(
        title="DB3 – Địa lý và phí vận chuyển", kind="OLAP", builder="Người 3",
        goal="Cho thấy doanh số và phí vận chuyển phân bố theo địa lý với drill-down Vùng → Bang → Thành phố, và quan hệ giữa khoảng cách, phí vận chuyển và thời gian giao; có trang drill-through chi tiết từng bang và tooltip.",
        sources=["D4"],
        users=[("Quản lý vận hành và logistics", "Phí vận chuyển chiếm bao nhiêu % giá hàng theo vùng; bang nào giao chậm?", "hằng ngày đến hằng tuần"), ("Quản lý kinh doanh", "GMV tập trung ở vùng, bang nào?", "hằng tháng")],
        pages=[("Trang 1 – Địa lý và phí vận chuyển", "D4", None)],
        extra_pages=[("Trang 2 – Chi tiết bang (drill-through)",
                      [("1", "1–12", "Card ×5", "`GMV`, `Orders`, `Freight ratio`, `Avg lead days`, `Late rate` của bang đang chọn"),
                       ("2", "1–6", "Table", "`dim_geography[city]` → `GMV`, `Freight ratio`, `Avg lead days` (thành phố của bang)"),
                       ("2", "7–12", "Clustered column", "`GMV` theo `dim_date[year_month]` của bang"),
                       ("3", "1–12", "Line chart", "`Avg lead days` theo `dim_date[year_month]` của bang"),
                       ("3", "12", "Button", "nút Back (*Insert → Buttons → Back*)")]),
                     ("Trang tooltip `Tooltip_Bang`", [("1", "1–12", "Card ×4", "`GMV`, `Freight ratio`, `Avg lead days`, `Late rate` theo bang đang trỏ")])],
        drill_extra=["Drill-through: trang *Chi tiết bang* có trường drill-through `dim_geography[state_code]` (*Keep all filters*); chuột phải một bang ở bản đồ, thanh hoặc ma trận → *Drill through* → *Chi tiết bang*.",
                     "Tooltip: gán `Tooltip_Bang` cho bản đồ và thanh `Freight ratio` theo bang."],
        slicer_hier=["Slicer địa lý dạng phân cấp `dim_geography` Vùng → Bang"],
        insights_extra=[]),
    "DB4": dict(
        title="DB4 – Thu hút và hiệu quả seller", kind="Vận hành (funnel)", builder="Người 4",
        goal="Đo hiệu quả thu hút seller (2 trang): kênh nào chuyển đổi tốt, chốt deal mất bao lâu, seller từ funnel có bán được không (luôn ghi cỡ mẫu); trang thứ ba là trang drill-through chi tiết từng seller.",
        sources=["D6"],
        users=[("Quản lý seller và đội sales (SDR, SR)", "Kênh nào chuyển đổi tốt; seller từ funnel bán ra sao?", "hằng tuần, hằng tháng")],
        pages=[("Trang 1 – Funnel theo kênh", "D6", "Trang 1"), ("Trang 2 – Seller từ funnel và hiệu suất", "D6", "Trang 2")],
        extra_pages=[("Trang 3 – Chi tiết seller (drill-through)",
                      [("1", "1–12", "Card ×5", "`dim_seller[seller_id]`, `[acquisition_channel]`, `[state_code]`; `Seller GMV (monthly)`; `Seller late rate`"),
                       ("2", "1–8", "Line chart", "`Seller GMV (monthly)` theo `dim_date[year_month]` (thấy tháng seller ngừng bán nhờ snapshot dày đặc)"),
                       ("2", "9–12", "Table", "tháng, số đơn, số đơn trễ của seller (`fact_seller_monthly`)"),
                       ("3", "1–11", "Card", "`Small sample warning`"), ("3", "12", "Button", "nút Back")]),
                     ("Trang tooltip `Tooltip_Kenh`", [("1", "1–12", "Card ×4", "`MQLs`, `Won deals`, `MQL to won rate`, cỡ mẫu theo kênh đang trỏ")])],
        drill_extra=["Drill-through: trang *Chi tiết seller* có trường drill-through `dim_seller[seller_id]`; ở trang 2, bảng `dim_seller[seller_id]` + `Seller GMV (monthly)` + `Seller late rate` có quan hệ với `fact_seller_monthly` nên chuột phải một seller → *Drill through* lọc đúng (bảng `v_seller_scorecard` là bảng rời, chỉ dùng để hiển thị điểm review).",
                     "Tooltip: gán `Tooltip_Kenh` cho thanh `MQL to won rate` theo origin."],
        slicer_hier=["Slicer kênh dạng phân cấp `dim_lead_origin` Nhóm kênh → Origin"],
        insights_extra=[]),
}


def grid_rows(src: str, page: str | None) -> list:
    g = SRC[src]["grid"]
    return [r for r in g if page is None or r[0] == page]


def expected_section(db: str) -> str:
    """Copy the table(s) of this dashboard from the generated block of powerbi/measures.md (section 7)."""
    lines = (ROOT / "powerbi" / "measures.md").read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(f"### {db} "))
    j = next((k for k in range(i + 1, len(lines)) if lines[k].startswith("### DB") or lines[k].startswith("<!-- EXPECTED:END")), len(lines))
    body = [l for l in lines[i + 1 : j]]
    while body and not body[-1].strip():
        body.pop()
    if db == "DB4":
        body = [l for l in body if not l.startswith("Ghi chú:")]
    return "\n".join(body).strip("\n")


def page_table(rows) -> list:
    return ["| Hàng | Cột (trong 12) | Visual | Trường / measure |", "| --- | --- | --- | --- |"] + [f"| {str(r).replace('Trang 1', '1').replace('Trang 2', '2')} | {c} | {v} | {f} |" for r, c, v, f in rows]


def build(key: str) -> str:
    d = DB[key]
    srcs = [SRC[s] for s in d["sources"]]
    md = [f"# {d['title']}", "",
          f"*Loại: {d['kind']}. Người dựng: {d['builder']} (Phú dựng file gốc, tổng hợp và chỉnh sửa). Dựng theo `powerbi/model.md` (mục 8); công thức DAX ở `{M}`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/2-3_cay_phan_tich_{key}.png`).*", "",
          "## 1. Mục tiêu", "", d["goal"], "",
          "## 2. Câu hỏi trả lời, người dùng và tần suất xem", ""]
    qs = [q for s in srcs for q in s["questions"]]
    md += [f"- {q}" for q in qs] + ["", "| Người dùng | Câu hỏi | Tần suất xem |", "| --- | --- | --- |"] + [f"| {a} | {b} | {c} |" for a, b, c in d["users"]]
    # pages
    md += ["", "## 3. Bố cục từng trang", "", "Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng là một visual. " + (FILTER_DB if key != "" else "")]
    for title, src, pg in d["pages"]:
        md += ["", f"### {title}", ""] + page_table(grid_rows(src, pg))
    for title, rows in d["extra_pages"]:
        md += ["", f"### {title}", ""] + page_table(rows)
    # visuals, measures, slicers
    md += ["", "## 4. Visual, measure, slicer", "", "**KPI và measure dùng**", "", "| Measure | Ý nghĩa |", "| --- | --- |"]
    seen = set()
    for s in srcs:
        for a, b in s["kpis"]:
            if a not in seen:
                seen.add(a)
                md.append(f"| **{a}** | {b} |")
    md += ["", f"Mã DAX đầy đủ từng measure: `{M}`. Màu cảnh báo: các measure `Color …` ở mục 6 của file đó.", "", "**Slicer và bộ lọc**", ""]
    sl = []
    for s in srcs:
        for x in s["slicers"]:
            if x not in sl:
                sl.append(x)
    md += [f"- {x}" for x in sl] + [f"- {x}" for x in d["slicer_hier"]] + [f"- {FILTER_DB}"]
    # drill
    md += ["", "## 5. Drill-down, drill-through, tooltip", ""]
    dr = []
    for s in srcs:
        for x in s["drill"]:
            if x not in dr:
                dr.append(x)
    md += [f"- {x}" for x in dr] + [f"- {x}" for x in d["drill_extra"]]
    # conditional formatting + DAX
    md += ["", "## 6. Định dạng có điều kiện và DAX đặc biệt", ""]
    cf = []
    for s in srcs:
        for x in s["cf"]:
            if x not in cf:
                cf.append(x)
    md += [f"- {x}" for x in cf] + [""]
    for s in srcs:
        for t, code in s["dax"]:
            md += [f"**{t}**", "", "```dax", code, "```", ""]
    # checklist coverage
    md += ["## 7. Đáp ứng checklist", "", f"Checklist chung ở [`README.md`](README.md); ma trận mục × dashboard ở đó.", "",
           "| Mục checklist | Đáp ứng | Cách đáp ứng trong " + key + " |", "| --- | --- | --- |"]
    how = checklist_how(key, d, sl, dr)
    for (name, _, _), ok, h in zip(ITEMS, MATRIX[key], how):
        md.append(f"| {name} | {SYM['yes'] if ok else SYM['no']} | {h} |")
    md += ["", "**Định dạng số** (*Measure tools → Format → Custom* hoặc *Display units* của visual):", "", "| Chỉ số | Loại | Định dạng |", "| --- | --- | --- |"] + [f"| {a} | {b} | {c} |" for a, b, c in FMT[key]]
    md += ["", "**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):", ""] + [f"- {q if q.endswith('?') else q + '?'}" for q in qs]
    # insights
    md += ["", "## 8. Insight gợi ý (có số thật, để viết vào báo cáo và slide)", ""]
    ins = [t for s in srcs for t in s["insights"]] + d["insights_extra"]
    md += [f"{i}. {t}" for i, t in enumerate(ins, 1)]
    for s in srcs:
        if s["extra"]:
            md += ["", s["extra"]]
    # expected values
    md += ["", "## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)", "",
           "Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc. Sinh bởi `python scripts/gen_powerbi_docs.py` rồi chạy lại `python scripts/gen_dashboard_docs.py`.", "",
           expected_section(key)]
    # build checklist
    charts = sorted({g[2].split(" (")[0] for s in d["pages"] for g in grid_rows(s[1], s[2])})
    md += ["", "## 10. Checklist dựng (đánh dấu khi xong)", ""]
    md += [f"- [ ] **Đa dạng biểu đồ (≥ 4 loại)**: " + ", ".join(charts)]
    md += [f"- [ ] **{name}**: {how[i]}" for i, (name, _, _) in enumerate(ITEMS) if MATRIX[key][i]]
    md += ["- [ ] **Số liệu khớp bảng giá trị kỳ vọng ở mục 9**: đối chiếu từng card", "- [ ] **Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang**",
           f"- [ ] **Ảnh chụp**: đặt tên `4_{key}_<mô-tả>.png` (ví dụ `4_{key}_trang1_tong_quan.png`) vào `figures/`"]
    return "\n".join(md) + "\n"


def checklist_how(key, d, slicers, drills):
    t = {
        "DB1": ["xem bảng định dạng bên dưới", "xem danh sách tiêu đề bên dưới", "mục 6: đỏ chỉ ở định dạng có điều kiện (cột `GMV MoM %` âm, `Freight ratio` > 25%)", "Card On-time rate, Avg review, Cancel rate; cột tăng trưởng; matrix color scale",
                "slicer Năm → Quý → Tháng", "line chart Năm → Quý → Tháng; treemap và matrix Nhóm ngành → Danh mục → Sản phẩm", "không áp dụng (drill-through nằm ở DB3, DB4)", "`Tooltip_Thang` và tooltip theo nhóm ngành",
                "line chart GMV theo tháng có *Forecast* 3 điểm, tin cậy 95%", "không áp dụng (Key Influencers ở DB2)", "cùng báo cáo với các dashboard khác (`powerbi/model.md` mục 9)"],
        "DB2": ["xem bảng định dạng bên dưới", "xem danh sách tiêu đề bên dưới", "mục 6: đỏ chỉ ở định dạng có điều kiện (trễ, hủy, điểm review thấp)", "Card On-time rate, Cancel rate, Avg review; bản đồ Late rate; cohort color scale",
                "slicer Năm → Quý → Tháng và Vùng → Bang", "bản đồ / bảng Geography Vùng → Bang → Thành phố; cohort năm → tháng", "không áp dụng (drill-through nằm ở DB3, DB4)", "`Tooltip_Muc_tre` và tooltip theo bang",
                "không áp dụng (dự báo ở DB1)", "trang 3: visual Key influencers cho `Review type` = Tiêu cực", "cùng báo cáo với các dashboard khác"],
        "DB3": ["xem bảng định dạng bên dưới", "xem danh sách tiêu đề bên dưới", "mục 6: đỏ chỉ ở màu `Freight ratio` cao", "matrix data bars, màu `Freight ratio`; bản đồ màu bong bóng",
                "slicer Vùng → Bang", "**OLAP chính**: Vùng → Bang → Thành phố → Zip trên bản đồ và ma trận, drill-down và roll-up", "trang *Chi tiết bang* (trường `state_code`)", "`Tooltip_Bang`",
                "không áp dụng (dự báo ở DB1)", "không áp dụng (Key Influencers ở DB2)", "cùng báo cáo với các dashboard khác"],
        "DB4": ["xem bảng định dạng bên dưới", "xem danh sách tiêu đề bên dưới", "mục 6: đỏ chỉ ở `late_rate_pct` > 10% và cảnh báo mẫu nhỏ", "`late_rate_pct`, `small_sample`, `avg_review_score` theo `Color …`",
                "slicer Nhóm kênh → Origin", "drill Origin → Nhóm kênh; bảng seller drill theo bang", "trang *Chi tiết seller* (trường `seller_id`)", "`Tooltip_Kenh`",
                "không áp dụng (dự báo ở DB1)", "không áp dụng (Key Influencers ở DB2)", "cùng báo cáo với các dashboard khác"],
    }
    return t[key]


README = """# Hướng dẫn dựng dashboard: DB1–DB4 và checklist chung

Bộ dashboard Power BI gồm **4 dashboard** (gộp từ 7 dashboard ở bản trước, quyết định ngày 13/11). Mỗi dashboard thuộc một loại mà môn học yêu cầu và do một thành viên dựng; Phú làm file `.pbix` gốc, tổng hợp và chỉnh sửa.

| Dashboard | Loại | Người dựng | Hướng dẫn |
| --- | --- | --- | --- |
| DB1 – Tổng quan và doanh thu | Theo dòng thời gian (có dự báo) | Người 1 | [`DB1.md`](DB1.md) |
| DB2 – Giao hàng và trải nghiệm khách | Vận hành + thống kê (Key Influencers) | Người 2 | [`DB2.md`](DB2.md) |
| DB3 – Địa lý và phí vận chuyển | OLAP; drill-down Vùng → Bang → Thành phố; drill-through; tooltip | Người 3 | [`DB3.md`](DB3.md) |
| DB4 – Thu hút và hiệu quả seller (2 trang + trang chi tiết) | Vận hành; funnel; drill-through sang chi tiết seller | Người 4 | [`DB4.md`](DB4.md) |

- **Giám sát chất lượng dữ liệu và ETL** không còn là dashboard: số liệu được trình bày ở mục 3.3 của báo cáo (bảng kết quả nạp và giám sát).
- **Thị trường Brazil (dữ liệu API)** thuộc chương 5 (P9); trang này chỉ để chỗ.
- **DB1 trên Superset** (chương 5) làm sau; xem `5-1-lakehouse.tex`.

## 1. Checklist chung

| Mục | Yêu cầu | Ví dụ / nơi xem |
| --- | --- | --- |
{items}

## 2. Ma trận đáp ứng (mục checklist × dashboard)

Ký hiệu: **✓** dashboard đáp ứng mục đó; **–** không áp dụng (đã có dashboard khác đáp ứng).

{matrix}

Mỗi mục có ít nhất một dashboard đáp ứng: dự báo ở DB1, Key Influencers ở DB2, OLAP drill-down ở DB3, drill-through ở DB3 và DB4. Định dạng số, tiêu đề câu hỏi, màu đỏ cảnh báo và định dạng có điều kiện áp dụng cho cả bốn dashboard.

## 3. Hướng dẫn chi tiết

**Định dạng số.** Chọn visual → *Format → Display units* (Thousands, Millions) và *Value decimal places = 1*; với measure dùng *Measure tools → Format → Custom*: `#,0.0,,"M"` (triệu), `#,0.0,"K"` (nghìn), `0.0%` (phần trăm một chữ số thập phân). Dấu phân cách hàng nghìn bật ở *Format → Value*. Luôn ghi đơn vị (BRL, ngày, %) ở tiêu đề hoặc nhãn trục.

**Tiêu đề dạng câu hỏi.** Mỗi visual có tiêu đề là câu hỏi nó trả lời (mục 7 của từng DB*.md có danh sách); tiêu đề trang cũng là câu hỏi chính của dashboard.

**Màu đỏ chỉ để cảnh báo.** Đỏ (`bad` trong `theme.json`) chỉ dùng cho giá trị xấu hoặc vượt ngưỡng qua định dạng có điều kiện; bảng màu dữ liệu của chủ đề không còn đỏ.

**Định dạng có điều kiện.** Dùng measure DAX trả về mã màu (`Color On-time rate`, `Color Cancel rate`…, xem `powerbi/measures.md` mục 6) và gán qua *Conditional formatting → Field value*.

**Slicer phân cấp và OLAP drill-down.** Slicer thời gian: kéo `Năm → Quý → Tháng` vào một slicer (kiểu phân cấp); slicer địa lý: `Vùng → Bang`. Với biểu đồ, ma trận và bản đồ, bật *Drill* (mũi tên) và *Expand all down one level in the hierarchy*; thao tác này tương ứng roll-up và drill-down của OLAP (`sql/60_olap_examples/`).

**Drill-through.** Tạo trang chi tiết, kéo trường cần lọc vào ô *Drill through → Add drill-through fields here*; người xem chuột phải một điểm → *Drill through*. Nút Back được thêm tự động hoặc chèn bằng *Insert → Buttons → Back*. DB3: trang Chi tiết bang; DB4: trang Chi tiết seller.

**Tooltip.** Tạo trang mới, *Format → Page information → Allow use as tooltip = On*, *Page size = Tooltip*; đặt vài visual nhỏ (card, cột); ở visual nguồn, *Format → Tooltips → Type = Report page* và chọn trang tooltip.

**Chuỗi thời gian có dự báo (DB1).** Chọn line chart GMV theo tháng → ngăn *Analytics* → *Forecast → Add* → *Forecast length = 3 points*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng (2017-01 → 2018-08) và mùa vụ theo năm chưa đủ dữ liệu để kết luận (báo cáo mục 3.1), nên dự báo chỉ để thấy hướng đi; ghi chú cạnh biểu đồ.

**Key Influencers (DB2).** Visual AI của Power BI: chọn *Key influencers*, đặt *Analyze* và *Explain by* theo `powerbi/model.md` mục 8 (DB2 trang 3). Kết quả cho biết yếu tố nào đi kèm review tiêu cực; không chứng minh nhân quả.

**Publish web và mã QR.** Publish theo `powerbi/model.md` mục 9 (File → Embed report → Publish to web). Mã QR: mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc công cụ tạo QR bất kỳ), lưu ảnh `figures/4_qr_dashboard.png` (nhóm tạo sau khi publish) và đặt vào slide cuối và báo cáo.

## 4. Trạng thái
Chưa có file `.pbix` nào được dựng ở thời điểm P8b; các mục trong ma trận là yêu cầu cho người dựng. Sau khi dựng, đánh dấu từng mục ở mục 10 của DB*.md và đặt ảnh chụp tên `4_DBx_<mô-tả>.png` vào `figures/`.
"""


def main() -> None:
    out_dir = ROOT / "huong-dan" / "dashboards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for key in DB:
        (out_dir / f"{key}.md").write_text(build(key), encoding="utf-8", newline="\n")
        print("written", f"huong-dan/dashboards/{key}.md")
    items = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in ITEMS)
    mat = "| Mục checklist | " + " | ".join(DB) + " |\n| --- | " + " | ".join("---" for _ in DB) + " |\n" + "\n".join(
        f"| {ITEMS[i][0]} | " + " | ".join(SYM["yes"] if MATRIX[k][i] else SYM["no"] for k in DB) + " |" for i in range(len(ITEMS)))
    (out_dir / "README.md").write_text(README.replace("{items}", items).replace("{matrix}", mat), encoding="utf-8", newline="\n")
    print("written huong-dan/dashboards/README.md")


if __name__ == "__main__":
    main()

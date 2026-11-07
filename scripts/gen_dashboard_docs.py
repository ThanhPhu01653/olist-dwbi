"""Generate huong-dan/dashboards/D1.md ... D7.md (one guide per dashboard).

    python scripts/gen_dashboard_docs.py
The narrative (goal, layout, insights) is defined below; the "expected values" table of each dashboard is copied from the table that
scripts/gen_powerbi_docs.py writes into powerbi/measures.md (so it always comes from SQL on olist_dw); D7 numbers are queried here.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from etl import config
from etl.db import get_engine

M = "powerbi/measures.md"
COMMON_FILTER = "Bộ lọc trang `dim_date[InWindow] = TRUE` (2017-01 → 2018-08)."

D = {
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
    "D7": dict(
        title="D7 – Data Quality & ETL Monitor", kind="Vận hành hệ thống",
        goal="Giám sát pipeline: mỗi lô chạy bao lâu, nạp bao nhiêu dòng, bao nhiêu dòng bị loại và vì sao, kiểm thử có đạt không, funnel \"lấp đầy dần\" qua các đợt.",
        questions=["Pipeline chạy có ổn định và mất bao lâu mỗi đợt?", "Bao nhiêu dòng bị loại, lý do?", "Bao nhiêu phép kiểm thử đạt?", "Số MQL, deal, seller có đơn thay đổi ra sao qua các đợt?"],
        kpis=[("duration_sec", "thời gian chạy mỗi lô (`v_run_summary`)"), ("pass_pct", "% test đạt (`v_dq_summary`)"), ("row_count", "số dòng bị loại (`v_rejected_summary`)"),
              ("mql, deals_won, sellers_with_sale, gmv", "chỉ số mỗi lô (`batch_metrics`)")],
        grid=[("1", "1–3", "Card", "`pass_pct` của lô mới nhất (`v_dq_summary`)"), ("1", "4–6", "Card", "số test đạt / tổng"), ("1", "7–9", "Card", "tổng dòng bị loại (`v_rejected_summary[row_count]`)"), ("1", "10–12", "Card", "số lô (đếm `v_run_summary[batch_id]`)"),
              ("2", "1–6", "Clustered column", "`v_run_summary`: `batch_id` → `duration_sec` (lọc `mode = incremental`)"), ("2", "7–12", "Line chart", "`batch_metrics`: `batch_id` → `mql`, `deals_won`, `sellers_with_sale` (funnel lấp đầy dần)"),
              ("3", "1–6", "Table", "`v_run_summary`: `batch_id`, `mode`, `started_at`, `duration_sec`, `status`, `staging_rows`, `ods_inserted`, `ods_rejected`, `dw_inserted`, `dw_updated`"),
              ("3", "7–12", "Bar chart", "`v_rejected_summary`: `reason` → `row_count`; bên cạnh bảng `fact_load_issue`")],
        slicers=["`v_run_summary[mode]` (full / incremental)", "`v_run_summary[status]`", "khoảng `batch_id`"],
        drill=["Bảng lô: drill-through sang `job_run` của lô (từng job)"],
        cf=["`status = failed` đỏ, `success` xanh", "`pass_pct` < 100 đỏ", "`duration_sec` > 30 vàng"],
        dax=[("Tỷ lệ test đạt của lô mới nhất", "Latest pass pct = CALCULATE ( MAX ( v_dq_summary[pass_pct] ), FILTER ( ALL ( v_dq_summary ), v_dq_summary[batch_id] = MAX ( v_dq_summary[batch_id] ) ) )")],
        measures=[],
        insights=["11 đợt tăng dần, mỗi đợt **~20–26 giây** (gồm kiểm thử ~11–15 giây).", "**Funnel lấp đầy dần**: MQL 2.002 → 8.000 (đủ từ đợt 5), deal chốt 3 → 842, seller của funnel có đơn 0 → 379 (đủ từ đợt 8).",
                  "Dòng bị loại: chỉ **42 điểm toạ độ ngoài Brazil**; không có dòng mồ côi; các khoảng thời gian âm được đặt trống và đếm ở `fact_load_issue` (1.359 `handling_days`, 23 `transit_days`, 1 `days_to_close`).",
                  "136 phép kiểm thử đạt 100% và 6/6 đối chiếu EDA khớp ở lô cuối."],
        extra="D7 **không** lọc thời gian 2017–2018 (dữ liệu giám sát theo lô, không theo ngày bán)."),
}

CHECKLIST = [
    ("Đa dạng biểu đồ (≥ 4 loại khác nhau)", "dùng ít nhất: {charts}"),
    ("Slicer (≥ 3, có nút / danh sách / khoảng)", "{slicers}"),
    ("Drill-down / hierarchy", "{drill}"),
    ("Định dạng có điều kiện", "{cf}"),
    ("DAX tăng trưởng và cảnh báo", "{dax}"),
    ("Tiêu đề, chú thích nguồn, đơn vị (BRL), bộ lọc thời gian ghi rõ", "{filt}"),
    ("Số liệu khớp bảng giá trị kỳ vọng ở mục 9", "đối chiếu từng card"),
    ("Màu theo `powerbi/theme.json`; font Segoe UI; không quá 6–8 visual một trang", ""),
]


def expected_rows(names: list[str]) -> str:
    lines = (ROOT / "powerbi" / "measures.md").read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("| Measure |"))
    head = lines[i:i + 2]
    body = {l.split("|")[1].strip(): l for l in lines[i + 2:] if l.startswith("|")}
    return "\n".join(head + [body[n] for n in names if n in body])


def d7_expected() -> str:
    with get_engine(config.DB_NAME).connect() as c:
        q = c.execute(text("SELECT checks, passed, failed, pass_pct, eda_checks, eda_match FROM etl_log.v_dq_summary ORDER BY batch_id DESC LIMIT 1")).one()
        runs = c.execute(text("SELECT count(*), min(duration_sec), round(avg(duration_sec), 1), max(duration_sec) FROM etl_log.v_run_summary WHERE mode = 'incremental' AND staging_rows > 0")).one()
        rej = c.execute(text("SELECT coalesce(sum(row_count), 0) FROM etl_log.v_rejected_summary")).scalar_one()
        bm = c.execute(text("SELECT min(mql), max(mql), min(deals_won), max(deals_won), min(sellers_with_sale), max(sellers_with_sale), max(gmv) FROM etl_log.batch_metrics")).one()
        iss = c.execute(text("SELECT detail, CASE WHEN fact_table = 'fact_lead_funnel' THEN max(row_count) ELSE sum(row_count) END AS n FROM etl_log.fact_load_issue GROUP BY fact_table, detail ORDER BY 2 DESC")).fetchall()
    rows = [("Số phép kiểm thử ở lô mới nhất (checks / đạt / lỗi)", f"{q[0]} / {q[1]} / {q[2]}"), ("`pass_pct` lô mới nhất", f"{q[3]}"), ("Đối chiếu EDA (khớp / tổng)", f"{q[5]} / {q[4]}"),
            ("Số lô tăng dần (`mode = incremental`, có dữ liệu mới)", f"{runs[0]}"), ("Thời gian mỗi lô: nhỏ nhất / TB / lớn nhất (giây)", f"{runs[1]} / {runs[2]} / {runs[3]}"),
            ("Tổng `row_count` ở `v_rejected_summary`", f"{int(rej):,}"), ("`batch_metrics`: MQL nhỏ nhất → lớn nhất", f"{bm[0]:,} → {bm[1]:,}"),
            ("`batch_metrics`: deal chốt nhỏ nhất → lớn nhất", f"{bm[2]:,} → {bm[3]:,}"), ("`batch_metrics`: seller có đơn nhỏ nhất → lớn nhất", f"{bm[4]:,} → {bm[5]:,}"),
            ("`batch_metrics`: GMV lớn nhất (BRL)", f"{float(bm[6]):,.2f}")] + [(f"`fact_load_issue`: {d}", f"{n:,}") for d, n in iss]
    return "| Chỉ số | Giá trị |\n| --- | ---: |\n" + "\n".join(f"| {a} | {b} |" for a, b in rows) + "\n\n*Số theo lần chạy cuối; số lô và thời gian có thể thay đổi nếu chạy pipeline thêm lần nữa.*"


def main() -> None:
    out_dir = ROOT / "huong-dan" / "dashboards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, d in D.items():
        charts = sorted({g[2].split(" (")[0] for g in d["grid"]})
        md = [f"# {d['title']}", "", f"*Loại: {d['kind']}. Dựng theo `powerbi/model.md`; công thức DAX ở `{M}`. Cây phân tích: `huong-dan/05-nghiep-vu-nhap.md` mục 6 (hình `figures/3-2-7_cay_phan_tich_{key}.png`).*", "",
              "## 1. Mục tiêu", "", d["goal"], "", "## 2. Câu hỏi dashboard trả lời", ""] + [f"- {q}" for q in d["questions"]]
        md += ["", "## 3. KPI và measure dùng", "", "| Measure | Ý nghĩa |", "| --- | --- |"] + [f"| **{a}** | {b} |" for a, b in d["kpis"]]
        md += ["", f"Mã DAX đầy đủ từng measure: `{M}`. Màu cảnh báo: các measure `Color …` ở mục 9 của file đó.", "", "## 4. Bố cục phác thảo (lưới 12 cột)", "",
               "Trang 16:9 chia 12 cột; số hàng là thứ tự từ trên xuống. Mỗi dòng dưới đây là một visual.", "", "| Hàng | Cột (trong 12) | Visual | Trường / measure |", "| --- | --- | --- | --- |"]
        md += [f"| {r} | {c} | {v} | {f} |" for r, c, v, f in d["grid"]]
        md += ["", "## 5. Slicer và bộ lọc", ""] + [f"- {s}" for s in d["slicers"]] + [f"- {COMMON_FILTER if key != 'D7' else 'Không lọc thời gian (dữ liệu theo lô).'}", "", "## 6. Drill", ""] + [f"- {s}" for s in d["drill"]]
        md += ["", "## 7. Conditional formatting", ""] + [f"- {s}" for s in d["cf"]]
        md += ["", "## 8. DAX đặc biệt", ""]
        for t, code in d["dax"]:
            md += [f"**{t}**", "", "```dax", code, "```", ""]
        md += ["## 9. Bảng giá trị kỳ vọng (SQL trên trạng thái cuối, để đối chiếu số trên Power BI)", "",
               ("Cột **Cửa sổ 2017-01 → 2018-08** là số khi bật bộ lọc trang `InWindow`; cột **Toàn bộ dữ liệu** khi bỏ lọc." if key != "D7" else "Chạy lại `python scripts/gen_dashboard_docs.py` để cập nhật."), "",
               expected_rows(d["measures"]) if d["measures"] else d7_expected(), "", "## 10. Insight gợi ý (có số thật, để viết vào báo cáo và slide)", ""]
        md += [f"{i}. {t}" for i, t in enumerate(d["insights"], 1)]
        if d["extra"]:
            md += ["", d["extra"]]
        md += ["", "## 11. Checklist yêu cầu của giảng viên", ""]
        fill = dict(charts=", ".join(charts), slicers="; ".join(d["slicers"][:3]), drill="; ".join(d["drill"][:2]), cf="; ".join(d["cf"][:2]),
                    dax="; ".join(t for t, _ in d["dax"]) + " (xem mục 8)", filt=COMMON_FILTER if key != "D7" else "không lọc thời gian")
        md += [f"- [ ] **{a}**" + (f": {b.format(**fill)}" if b else "") for a, b in CHECKLIST]
        (out_dir / f"{key}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print("written", f"huong-dan/dashboards/{key}.md")


if __name__ == "__main__":
    main()

-- DRILL-DOWN: go from a coarse level to a FINER level of the same hierarchy by adding the next level to GROUP BY and filtering the parent value.
-- Path 1 (time): year -> quarter -> month -> day.  Path 2 (geography): region -> state -> city.

-- QUERY: Drill-down thời gian, bước 1: GMV theo năm
SELECT d.year, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year ORDER BY d.year;

-- QUERY: Drill-down thời gian, bước 2: mở năm 2017 thành các quý
SELECT d.year_quarter, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_quarter ORDER BY d.year_quarter;

-- QUERY: Drill-down thời gian, bước 3: mở quý 4/2017 thành các tháng
SELECT d.year_month, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_quarter = '2017-Q4'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month ORDER BY d.year_month;

-- QUERY: Drill-down thời gian, bước 4: mở tháng 11/2017 thành các ngày (10 ngày GMV cao nhất; có Black Friday 24/11)
SELECT d.full_date, d.day_name, d.is_black_friday, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_month = '2017-11'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.full_date, d.day_name, d.is_black_friday ORDER BY gmv DESC LIMIT 10;

-- QUERY: Drill-down địa lý: vùng Sudeste -> bang SP -> 5 thành phố có GMV cao nhất
SELECT g.state_code, g.city, round(sum(f.price), 2) AS gmv, count(DISTINCT f.order_id) AS orders FROM dw.fact_order_item f
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste' AND g.state_code = 'SP'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.state_code, g.city ORDER BY gmv DESC LIMIT 5;

-- SLICE: fix ONE dimension to a single value (here year = 2017) and look at the remaining dimensions.
-- The result is a "slice" of the cube with one dimension removed.

-- QUERY: Slice năm 2017: GMV theo tháng
SELECT d.year_month, count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month ORDER BY d.year_month;

-- QUERY: Slice năm 2017: GMV theo vùng (cùng lát cắt, nhìn theo chiều địa lý)
SELECT g.region, round(sum(f.price), 2) AS gmv, round(100.0 * sum(f.price) / sum(sum(f.price)) OVER (), 1) AS pct FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.region ORDER BY gmv DESC;

-- QUERY: Slice năm 2017: GMV theo nhóm ngành hàng
SELECT p.category_group, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_group ORDER BY gmv DESC;

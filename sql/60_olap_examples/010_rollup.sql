-- ROLL-UP: aggregate to a COARSER level of a hierarchy (day -> month -> quarter -> year; zip -> state -> region).
-- ROLLUP(a, b) adds subtotals for (a, b), (a) and the grand total. GROUPING(col) = 1 marks a subtotal row. GROUPING SETS and CUBE give custom / all combinations.
-- Measure: GMV = sum of price of orders not in status group 'Failed'.

-- QUERY: Roll-up thời gian bằng ROLLUP: quý -> năm -> tổng (GMV, 2017-2018)
SELECT CASE WHEN GROUPING(d.year) = 1 THEN 'Tổng' ELSE d.year::text END AS nam,
       CASE WHEN GROUPING(d.year_quarter) = 1 THEN '(cả năm)' ELSE d.year_quarter END AS quy,
       count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
WHERE d.year IN (2017, 2018)
GROUP BY ROLLUP (d.year, d.year_quarter)
ORDER BY GROUPING(d.year), d.year, GROUPING(d.year_quarter), d.year_quarter;

-- QUERY: Roll-up địa lý bằng ROLLUP: bang -> vùng -> tổng (GMV theo bang của khách; chỉ bang có GMV > 500.000)
SELECT CASE WHEN GROUPING(g.region) = 1 THEN 'Tổng' ELSE g.region END AS vung,
       CASE WHEN GROUPING(g.state_code) = 1 THEN '(cả vùng)' ELSE g.state_code END AS bang,
       round(sum(f.price), 2) AS gmv, count(DISTINCT f.order_id) AS orders
FROM dw.fact_order_item f
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY ROLLUP (g.region, g.state_code)
HAVING GROUPING(g.region) = 1 OR GROUPING(g.state_code) = 1 OR sum(f.price) > 500000
ORDER BY GROUPING(g.region), g.region, GROUPING(g.state_code), sum(f.price) DESC;

-- QUERY: GROUPING SETS: bốn góc nhìn trong MỘT truy vấn (theo năm, theo vùng, theo nhóm ngành hàng, tổng)
SELECT CASE WHEN GROUPING(d.year) = 0 THEN 'Năm ' || d.year WHEN GROUPING(g.region) = 0 THEN 'Vùng ' || g.region
            WHEN GROUPING(p.category_group) = 0 THEN 'Ngành ' || p.category_group ELSE 'Tổng' END AS nhom,
       round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY GROUPING SETS ((d.year), (g.region), (p.category_group), ())
ORDER BY GROUPING(d.year), GROUPING(g.region), GROUPING(p.category_group), gmv DESC;

-- QUERY: CUBE: mọi tổ hợp tổng con của (năm, vùng) - 4 loại dòng: chi tiết, theo năm, theo vùng, tổng
SELECT coalesce(d.year::text, 'Tất cả năm') AS nam, coalesce(g.region, 'Tất cả vùng') AS vung, round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year IN (2017, 2018)
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY CUBE (d.year, g.region)
ORDER BY GROUPING(d.year), d.year, GROUPING(g.region), gmv DESC;

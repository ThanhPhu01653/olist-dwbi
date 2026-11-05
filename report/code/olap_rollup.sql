SELECT CASE WHEN GROUPING(d.year) = 1 THEN 'Tổng' ELSE d.year::text END AS nam,
       CASE WHEN GROUPING(d.year_quarter) = 1 THEN '(cả năm)' ELSE d.year_quarter END AS quy,
       count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
WHERE d.year IN (2017, 2018)
GROUP BY ROLLUP (d.year, d.year_quarter)
ORDER BY GROUPING(d.year), d.year, GROUPING(d.year_quarter), d.year_quarter;

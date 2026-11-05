SELECT g.region AS vung,
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2016), 0), 2) AS "2016",
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2017), 0), 2) AS "2017",
       round(coalesce(sum(f.price) FILTER (WHERE d.year = 2018), 0), 2) AS "2018",
       round(sum(f.price), 2) AS tong
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY g.region ORDER BY tong DESC;

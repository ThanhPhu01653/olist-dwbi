-- PIVOT: turn the values of one dimension into COLUMNS. PostgreSQL has no PIVOT keyword: use conditional aggregation
-- sum(...) FILTER (WHERE ...) (or the crosstab() function of the tablefunc extension, not installed here).

-- QUERY: Pivot vùng x năm (GMV): mỗi năm là một cột
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

-- QUERY: Pivot nhóm ngành hàng x quý của 2017 (tỷ trọng GMV theo hàng, %)
SELECT p.category_group AS nhom_nganh,
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q1') / sum(f.price), 1) AS "Q1",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q2') / sum(f.price), 1) AS "Q2",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q3') / sum(f.price), 1) AS "Q3",
       round(100.0 * sum(f.price) FILTER (WHERE d.year_quarter = '2017-Q4') / sum(f.price), 1) AS "Q4",
       round(sum(f.price), 2) AS gmv_2017
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year = 2017
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_group ORDER BY gmv_2017 DESC;

-- QUERY: Pivot hình thức thanh toán x năm (số lần thanh toán)
SELECT pt.display_name AS hinh_thuc,
       count(*) FILTER (WHERE d.year = 2017) AS "2017", count(*) FILTER (WHERE d.year = 2018) AS "2018", count(*) AS tong
FROM dw.fact_payment f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_payment_type pt ON pt.payment_type_key = f.payment_type_key
GROUP BY pt.display_name ORDER BY tong DESC;

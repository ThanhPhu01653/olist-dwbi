-- DICE: select a SUB-CUBE by restricting SEVERAL dimensions at once (here region = Sudeste x category group = Home & Furniture x quarter 4).

-- QUERY: Dice Sudeste x Home & Furniture x quý 4 (mọi năm có dữ liệu: 2016, 2017; quý 4/2018 chưa có): GMV theo quý và bang
SELECT d.year_quarter, g.state_code, count(DISTINCT f.order_id) AS orders, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.quarter = 4
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste'
JOIN dw.dim_product p ON p.product_key = f.product_key AND p.category_group = 'Home & Furniture'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_quarter, g.state_code ORDER BY d.year_quarter, gmv DESC;

-- QUERY: Dice như trên nhưng chỉ quý 4/2017: 5 danh mục bán chạy nhất trong sub-cube
SELECT p.category_name_en, count(*) AS items, round(sum(f.price), 2) AS gmv FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key AND d.year_quarter = '2017-Q4'
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key AND g.region = 'Sudeste'
JOIN dw.dim_product p ON p.product_key = f.product_key AND p.category_group = 'Home & Furniture'
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY p.category_name_en ORDER BY gmv DESC LIMIT 5;

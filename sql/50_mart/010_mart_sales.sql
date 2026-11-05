-- setup: required
-- Data mart "sales" (DW_DESIGN section 8). GMV, orders and AOV count only orders that are NOT in status group 'Failed' (KPI definition, section 9).
-- Marts are read-only layers on top of dw; plain views unless a query needs > 1 s (then MATERIALIZED VIEW refreshed by dw.refresh_marts).
-- in_window = year_month between 2017-01 and 2018-08 (the period dashboards use; 2016 and 09-10/2018 are almost empty).

CREATE OR REPLACE VIEW mart_sales.v_sales_daily AS
SELECT d.date_key, d.full_date, d.year, d.quarter, d.year_month, d.is_weekend, d.is_holiday_br, d.is_black_friday,
       (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       count(DISTINCT f.order_id) AS orders, count(*) AS items,
       sum(f.price) AS gmv, sum(f.freight_value) AS freight,
       round(sum(f.price) / nullif(count(DISTINCT f.order_id), 0), 2) AS aov
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.date_key, d.full_date, d.year, d.quarter, d.year_month, d.is_weekend, d.is_holiday_br, d.is_black_friday;

CREATE OR REPLACE VIEW mart_sales.v_sales_category_month AS
SELECT d.year_month, d.year, d.quarter, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       p.category_group, p.category_name_en,
       count(DISTINCT f.order_id) AS orders, count(*) AS items, sum(f.price) AS gmv, sum(f.freight_value) AS freight,
       round(sum(f.price) / count(*), 2) AS avg_item_price
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_product p ON p.product_key = f.product_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month, d.year, d.quarter, p.category_group, p.category_name_en;

CREATE OR REPLACE VIEW mart_sales.v_sales_state_month AS
SELECT d.year_month, d.year, d.quarter, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       g.region, g.state_code, g.state_name,
       count(DISTINCT f.order_id) AS orders, count(*) AS items, sum(f.price) AS gmv, sum(f.freight_value) AS freight,
       round(sum(f.freight_value) / nullif(sum(f.price), 0), 4) AS freight_ratio
FROM dw.fact_order_item f
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
GROUP BY d.year_month, d.year, d.quarter, g.region, g.state_code, g.state_name;

-- Pareto (80/20) of GMV by product category over the whole period: class A = first 80% of GMV, B = up to 95%, C = the rest
CREATE OR REPLACE VIEW mart_sales.v_category_pareto AS
WITH c AS (
    SELECT p.category_group, p.category_name_en, sum(f.price) AS gmv, count(DISTINCT f.order_id) AS orders, count(*) AS items
    FROM dw.fact_order_item f
    JOIN dw.dim_product p ON p.product_key = f.product_key
    JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
    GROUP BY p.category_group, p.category_name_en),
r AS (
    SELECT c.*, row_number() OVER (ORDER BY gmv DESC, category_name_en) AS gmv_rank,
           100.0 * gmv / sum(gmv) OVER () AS share_pct,
           100.0 * sum(gmv) OVER (ORDER BY gmv DESC, category_name_en) / sum(gmv) OVER () AS cum_share_pct
    FROM c)
SELECT gmv_rank, category_group, category_name_en, orders, items, gmv, round(share_pct, 2) AS share_pct, round(cum_share_pct, 2) AS cum_share_pct,
       CASE WHEN cum_share_pct - share_pct < 80 THEN 'A' WHEN cum_share_pct - share_pct < 95 THEN 'B' ELSE 'C' END AS abc_class
FROM r;

COMMENT ON SCHEMA mart_sales IS 'Data mart bán hàng: GMV, đơn, AOV theo ngày / danh mục / bang';
COMMENT ON VIEW mart_sales.v_sales_daily IS 'GMV, số đơn, số dòng hàng, phí vận chuyển, AOV theo ngày mua (chỉ đơn không thuộc nhóm Failed)';
COMMENT ON VIEW mart_sales.v_sales_category_month IS 'GMV, đơn, dòng hàng theo tháng x nhóm ngành hàng x danh mục (số đơn không cộng được giữa các danh mục)';
COMMENT ON VIEW mart_sales.v_sales_state_month IS 'GMV, đơn, phí vận chuyển, tỷ lệ freight/price theo tháng x bang của khách';
COMMENT ON VIEW mart_sales.v_category_pareto IS 'Pareto 80/20 của GMV theo danh mục: xếp hạng, tỷ trọng, tỷ trọng luỹ kế, hạng A/B/C';

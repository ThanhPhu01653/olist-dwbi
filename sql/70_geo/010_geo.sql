-- setup: required
-- Geography extension WITHOUT PostGIS (CLAUDE.md decision 05/11): distances come from the haversine formula on latitude / longitude.

-- Great-circle distance in km between two points (degrees). Earth radius 6371.0088 km (mean radius). NULL if any coordinate is NULL.
CREATE OR REPLACE FUNCTION dw.haversine_km(lat1 double precision, lng1 double precision, lat2 double precision, lng2 double precision)
RETURNS double precision LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
    SELECT CASE WHEN lat1 IS NULL OR lng1 IS NULL OR lat2 IS NULL OR lng2 IS NULL THEN NULL
                ELSE 2 * 6371.0088 * asin(sqrt(least(1.0, power(sin(radians(lat2 - lat1) / 2), 2)
                                                           + cos(radians(lat1)) * cos(radians(lat2)) * power(sin(radians(lng2 - lng1) / 2), 2)))) END $$;
COMMENT ON FUNCTION dw.haversine_km(double precision, double precision, double precision, double precision) IS
    'Khoảng cách đường tròn lớn (km) giữa hai toạ độ (độ) bằng công thức haversine, bán kính 6371,0088 km; NULL nếu thiếu toạ độ';

-- Distance seller -> customer for EVERY order item. Items whose seller zip or customer zip has no coordinates keep a row with distance_km = NULL
-- (has_distance = false) so the number of dropped pairs is visible: SELECT count(*) FILTER (WHERE NOT has_distance) FROM mart_fulfillment.v_shipping_distance.
CREATE OR REPLACE VIEW mart_fulfillment.v_shipping_distance AS
SELECT f.order_id, f.order_item_id, f.seller_key, sg.state_code AS seller_state, cg.state_code AS customer_state, cg.region AS customer_region,
       d.distance_km, (d.distance_km IS NOT NULL) AS has_distance,
       CASE WHEN d.distance_km IS NULL THEN 'Không có toạ độ' WHEN d.distance_km < 100 THEN '0-100 km' WHEN d.distance_km < 500 THEN '100-500 km'
            WHEN d.distance_km < 1000 THEN '500-1000 km' ELSE 'Trên 1000 km' END AS distance_band,
       CASE WHEN d.distance_km IS NULL THEN 0 WHEN d.distance_km < 100 THEN 1 WHEN d.distance_km < 500 THEN 2 WHEN d.distance_km < 1000 THEN 3 ELSE 4 END AS distance_band_no,
       f.price, f.freight_value, round(f.freight_value / nullif(f.price, 0), 4) AS freight_ratio,
       o.lead_days, o.delay_days, o.is_delivered, o.is_late, os.status_group
FROM dw.fact_order_item f
JOIN dw.dim_geography sg ON sg.geography_key = f.seller_geography_key
JOIN dw.dim_geography cg ON cg.geography_key = f.customer_geography_key
JOIN dw.fact_order_fulfillment o ON o.order_id = f.order_id
JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key
CROSS JOIN LATERAL (SELECT dw.haversine_km(sg.latitude, sg.longitude, cg.latitude, cg.longitude) AS distance_km) d;
COMMENT ON VIEW mart_fulfillment.v_shipping_distance IS
    'Khoảng cách seller -> khách (km, haversine) cho từng dòng hàng, nhóm 0-100 / 100-500 / 500-1000 / trên 1000 km; distance_km NULL nếu thiếu toạ độ (has_distance = false)';

-- Map data for Power BI: one row per state / per zip that has coordinates (latitude and longitude of the zip are the median of its points).
CREATE OR REPLACE VIEW mart_sales.v_geo_state AS
WITH z AS (SELECT state_code, avg(latitude) AS lat, avg(longitude) AS lng, count(*) AS zips FROM dw.dim_geography WHERE latitude IS NOT NULL AND geography_key <> -1 GROUP BY state_code),
c AS (
    SELECT g.state_code, count(DISTINCT f.order_id) AS orders, sum(f.price) AS gmv, sum(f.freight_value) AS freight
    FROM dw.fact_order_item f JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
    JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed' GROUP BY g.state_code),
cu AS (SELECT g.state_code, count(DISTINCT dc.customer_unique_id) AS customers FROM dw.dim_customer dc JOIN dw.dim_geography g ON g.geography_key = dc.geography_key
       WHERE dc.customer_key <> -1 GROUP BY g.state_code),
sl AS (SELECT g.state_code, count(*) AS sellers FROM dw.dim_seller s JOIN dw.dim_geography g ON g.geography_key = s.geography_key WHERE s.seller_key <> -1 GROUP BY g.state_code),
ful AS (SELECT g.state_code, round(avg(o.lead_days) FILTER (WHERE o.is_delivered = 1), 2) AS avg_lead_days,
               round(100.0 * sum(o.is_late) / nullif(sum(o.is_delivered), 0), 2) AS late_rate_pct
        FROM dw.fact_order_fulfillment o JOIN dw.dim_geography g ON g.geography_key = o.customer_geography_key GROUP BY g.state_code)
SELECT r.state_code, r.state_name, r.region, round(z.lat::numeric, 5) AS latitude, round(z.lng::numeric, 5) AS longitude, z.zips AS zips_with_coordinates,
       coalesce(cu.customers, 0) AS customers, coalesce(c.orders, 0) AS orders, coalesce(c.gmv, 0) AS gmv, round(c.freight / nullif(c.gmv, 0), 4) AS freight_ratio,
       coalesce(sl.sellers, 0) AS sellers, ful.avg_lead_days, ful.late_rate_pct
FROM (SELECT DISTINCT state_code, state_name, region FROM dw.dim_geography WHERE geography_key <> -1 AND state_code IS NOT NULL) r
LEFT JOIN z USING (state_code) LEFT JOIN c USING (state_code) LEFT JOIN cu USING (state_code) LEFT JOIN sl USING (state_code) LEFT JOIN ful USING (state_code);
COMMENT ON VIEW mart_sales.v_geo_state IS 'Dữ liệu bản đồ theo bang: toạ độ tâm (trung bình các zip có toạ độ), số khách, đơn, GMV, freight ratio, số seller, lead time, tỷ lệ trễ';

CREATE OR REPLACE VIEW mart_sales.v_geo_zip AS
WITH c AS (
    SELECT f.customer_geography_key AS gk, count(DISTINCT f.order_id) AS orders, sum(f.price) AS gmv
    FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed' GROUP BY f.customer_geography_key),
sl AS (SELECT s.geography_key AS gk, count(*) AS sellers FROM dw.dim_seller s WHERE s.seller_key <> -1 GROUP BY s.geography_key)
SELECT g.zip_code_prefix, g.city, g.state_code, g.region, g.latitude, g.longitude, coalesce(c.orders, 0) AS customer_orders, coalesce(c.gmv, 0) AS customer_gmv,
       coalesce(sl.sellers, 0) AS sellers
FROM dw.dim_geography g LEFT JOIN c ON c.gk = g.geography_key LEFT JOIN sl ON sl.gk = g.geography_key
WHERE g.latitude IS NOT NULL AND g.geography_key <> -1 AND (c.gk IS NOT NULL OR sl.gk IS NOT NULL);
COMMENT ON VIEW mart_sales.v_geo_zip IS 'Dữ liệu bản đồ theo zip có toạ độ và có khách hoặc seller: toạ độ, thành phố, số đơn và GMV phía khách, số seller';

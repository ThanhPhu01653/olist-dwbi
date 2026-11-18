-- setup: required
-- P9: mart_market = market view built with public API data (IBGE population and GDP, Banco Central USD/BRL and IPCA, BrasilAPI holidays,
-- Open-Meteo rain). Feeds dashboard D8 "Thi truong Brazil" (chapter 5). Plain views: the tables behind them are small.
-- GMV keeps the project definition: price of orders that are not in the Failed status group.

-- ---------------------------------------------------------------- GMV per 1,000 inhabitants by state and year (nominal BRL)
CREATE OR REPLACE VIEW mart_market.v_gmv_per_capita_state AS
SELECT d.year, s.state_code, s.state_name, s.region, s.population, s.gdp_thousand_brl, s.gmv, s.orders, s.customers, s.sellers,
       round(s.gmv / nullif(s.population, 0) * 1000, 2) AS gmv_per_1000_pop,
       round(s.orders::numeric / nullif(s.population, 0) * 1000, 3) AS orders_per_1000_pop,
       round(s.gmv / nullif(s.gdp_thousand_brl * 1000, 0) * 100000, 4) AS gmv_per_100k_gdp,        -- BRL of Olist GMV per 100,000 BRL of state GDP
       rank() OVER (PARTITION BY s.year_date_key ORDER BY s.gmv / nullif(s.population, 0) DESC NULLS LAST) AS rank_per_capita,
       rank() OVER (PARTITION BY s.year_date_key ORDER BY s.gmv DESC) AS rank_gmv
FROM dw.fact_state_year s JOIN dw.dim_date d ON d.date_key = s.year_date_key;

-- ---------------------------------------------------------------- GMV per 1,000 inhabitants by IBGE municipality (customer city) and year
CREATE OR REPLACE VIEW mart_market.v_gmv_per_capita_city AS
WITH sales AS (
    SELECT d.year, g.ibge_municipio_code AS ibge_code, sum(f.price) AS gmv, count(DISTINCT f.order_id) AS orders
    FROM dw.fact_order_item f
    JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
    JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
    JOIN dw.dim_geography g ON g.geography_key = f.customer_geography_key
    WHERE g.ibge_municipio_code IS NOT NULL GROUP BY d.year, g.ibge_municipio_code)
SELECT s.year, m.ibge_code, m.name AS city, m.state_code, m.mesorregiao, m.microrregiao, p.population, s.gmv, s.orders,
       round(s.gmv / nullif(p.population, 0) * 1000, 2) AS gmv_per_1000_pop,
       rank() OVER (PARTITION BY s.year ORDER BY s.gmv / nullif(p.population, 0) DESC NULLS LAST) AS rank_per_capita,
       rank() OVER (PARTITION BY s.year ORDER BY s.gmv DESC) AS rank_gmv
FROM sales s JOIN ods.ibge_municipio m ON m.ibge_code = s.ibge_code
LEFT JOIN ods.ibge_population p ON p.ibge_code = s.ibge_code AND p.year = s.year;

-- ---------------------------------------------------------------- GMV in USD by month (each item converted at the rate of its purchase day)
CREATE OR REPLACE VIEW mart_market.v_gmv_usd_month AS
SELECT d.year_month, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window,
       sum(f.price) AS gmv_brl, round(sum(f.price / d.usd_brl), 2) AS gmv_usd,
       round(sum(f.price) / nullif(sum(f.price / d.usd_brl), 0), 4) AS avg_usd_brl,
       round(avg(d.usd_brl), 4) AS month_avg_rate
FROM dw.fact_order_item f
JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
WHERE d.usd_brl IS NOT NULL GROUP BY d.year_month;

-- ---------------------------------------------------------------- nominal vs real GMV by month (real = at January 2016 prices, deflated by the IPCA index)
CREATE OR REPLACE VIEW mart_market.v_gmv_real_month AS
WITH m AS (
    SELECT d.year_month, min(d.full_date) AS first_day, (d.year_month BETWEEN '2017-01' AND '2018-08') AS in_window, max(d.ipca_index) AS ipca_index,
           coalesce(sum(f.price) FILTER (WHERE os.status_group <> 'Failed'), 0) AS gmv_nominal
    FROM dw.dim_date d
    LEFT JOIN dw.fact_order_item f ON f.purchase_date_key = d.date_key
    LEFT JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key
    WHERE d.date_key <> -1 AND d.full_date BETWEEN DATE '2016-01-01' AND DATE '2018-12-31' GROUP BY d.year_month)
SELECT year_month, in_window, ipca_index, gmv_nominal, round(gmv_nominal * 100 / ipca_index, 2) AS gmv_real,
       round((gmv_nominal / nullif(lag(gmv_nominal, 12) OVER w, 0) - 1) * 100, 1) AS nominal_yoy_pct,
       round(((gmv_nominal / ipca_index) / nullif(lag(gmv_nominal / ipca_index, 12) OVER w, 0) - 1) * 100, 1) AS real_yoy_pct
FROM m WINDOW w AS (ORDER BY year_month);

-- ---------------------------------------------------------------- official holidays (BrasilAPI) vs the Python 'holidays' flag, and their effect on orders
CREATE OR REPLACE VIEW mart_market.v_holiday_diff AS
SELECT d.full_date, d.day_name, d.is_holiday_official, d.holiday_name_official, d.is_holiday_br, d.holiday_name AS holiday_name_lib,
       CASE WHEN d.is_holiday_official AND NOT d.is_holiday_br THEN 'only BrasilAPI'
            WHEN d.is_holiday_br AND NOT d.is_holiday_official THEN 'only holidays library' ELSE 'both' END AS agreement
FROM dw.dim_date d WHERE d.date_key <> -1 AND (d.is_holiday_official OR d.is_holiday_br);

CREATE OR REPLACE VIEW mart_market.v_holiday_effect AS
WITH day AS (
    SELECT d.full_date, d.is_weekend, d.is_holiday_official, d.holiday_name_official,
           count(DISTINCT f.order_id) FILTER (WHERE os.status_group <> 'Failed') AS orders,
           coalesce(sum(f.price) FILTER (WHERE os.status_group <> 'Failed'), 0) AS gmv
    FROM dw.dim_date d
    LEFT JOIN dw.fact_order_item f ON f.purchase_date_key = d.date_key
    LEFT JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key
    WHERE d.date_key <> -1 AND d.full_date BETWEEN DATE '2017-01-01' AND DATE '2018-08-31' AND NOT d.is_black_friday GROUP BY d.full_date, d.is_weekend, d.is_holiday_official, d.holiday_name_official)
SELECT CASE WHEN is_weekend THEN 'weekend' ELSE 'weekday' END AS day_type, is_holiday_official, count(*) AS days,
       round(avg(orders), 1) AS avg_orders_per_day, round(avg(gmv), 2) AS avg_gmv_per_day
FROM day GROUP BY is_weekend, is_holiday_official;

-- ---------------------------------------------------------------- (optional source) late delivery rate by rain on the delivery day at the state capital
CREATE OR REPLACE VIEW mart_market.v_late_by_rain AS
SELECT CASE WHEN w.precip_mm = 0 THEN '0 mm' WHEN w.precip_mm < 5 THEN '0-5 mm' WHEN w.precip_mm < 20 THEN '5-20 mm' ELSE '20 mm or more' END AS rain_bucket,
       CASE WHEN w.precip_mm = 0 THEN 1 WHEN w.precip_mm < 5 THEN 2 WHEN w.precip_mm < 20 THEN 3 ELSE 4 END AS rain_bucket_no,
       count(*) AS delivered_orders, sum(o.is_late) AS late_orders, round(100.0 * sum(o.is_late) / count(*), 2) AS late_rate_pct
FROM dw.fact_order_fulfillment o
JOIN dw.dim_date dd ON dd.date_key = o.delivered_date_key
JOIN dw.dim_geography g ON g.geography_key = o.customer_geography_key
JOIN ods.weather_daily w ON w.state_code = g.state_code AND w.obs_date = dd.full_date
WHERE o.is_delivered = 1 AND o.delivered_date_key <> -1 AND dd.year_month BETWEEN '2017-01' AND '2018-08'
GROUP BY 1, 2;

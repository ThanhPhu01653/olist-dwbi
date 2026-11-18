-- P9 tests: public API data (IBGE, Banco Central, BrasilAPI), the city match, the enriched dimensions, fact_state_year and mart_market.
-- When the API data has not been loaded (no landing zone) every check passes with 'API data not loaded'.
-- Returns (check_name, target_table, expected, actual, passed).
WITH apiflag AS (SELECT EXISTS (SELECT 1 FROM ods.ibge_municipio) AS loaded),
g AS (SELECT sum(f.price) AS gmv, count(DISTINCT f.order_id) AS orders
      FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'),
-- weekdays that are not official holidays but have no own quotation (rate copied from an earlier day), 2016-01-01 .. 2018-12-31
nobiz AS (
    SELECT count(*) AS n FROM ods.fx_usd_brl f
    WHERE f.rate_date BETWEEN DATE '2016-01-01' AND DATE '2018-12-31' AND extract(isodow FROM f.rate_date) < 6 AND NOT f.is_business_day
      AND NOT EXISTS (SELECT 1 FROM ods.holiday_official h WHERE h.holiday_date = f.rate_date)),
-- IBGE IPCA index (base Dec 1993) rescaled to the first month = 100, compared with our chained index
ibge AS (
    SELECT max(abs(o.ipca_index - 100 * i.idx / i0.idx)) AS max_diff
    FROM ods.ipca_month o
    JOIN (SELECT to_date(period, 'YYYYMM') AS m, index_raw::numeric AS idx FROM api.stg_api_ibge_ipca) i ON i.m = o.month_date
    CROSS JOIN (SELECT index_raw::numeric AS idx FROM api.stg_api_ibge_ipca ORDER BY period LIMIT 1) i0)
SELECT 'API: collected data loaded or skipped' AS check_name, 'ods.ibge_municipio' AS target_table, 'ok' AS expected,
       CASE WHEN loaded THEN 'municipalities loaded' ELSE 'API data not loaded' END AS actual, true AS passed FROM apiflag
UNION ALL SELECT 'API: IBGE has 27 states with a valid municipality code (7 digits, first 2 = state code)', 'ods.ibge_municipio', '27 / 0 invalid',
       (SELECT count(DISTINCT state_code) FROM ods.ibge_municipio) || ' / ' || (SELECT count(*) FROM ods.ibge_municipio WHERE ibge_code NOT BETWEEN 1000000 AND 5999999 OR ibge_code / 100000 <> state_ibge_code) || ' invalid',
       (SELECT NOT loaded FROM apiflag) OR ((SELECT count(DISTINCT state_code) FROM ods.ibge_municipio) = 27 AND (SELECT count(*) FROM ods.ibge_municipio WHERE ibge_code NOT BETWEEN 1000000 AND 5999999 OR ibge_code / 100000 <> state_ibge_code) = 0)
UNION ALL SELECT 'API: IBGE population 2016-2018 present for at least 5,570 municipalities', 'ods.ibge_population', '>= 5570 per year',
       (SELECT min(c)::text FROM (SELECT count(*) AS c FROM ods.ibge_population GROUP BY year) x),
       (SELECT NOT loaded FROM apiflag) OR (SELECT min(c) >= 5570 AND count(*) = 3 FROM (SELECT count(*) AS c FROM ods.ibge_population GROUP BY year) x)
UNION ALL SELECT 'API: USD/BRL has a rate for every calendar day 2016-01-01 .. 2020-12-31', 'dw.dim_date', '1827 days with a rate',
       (SELECT count(*) FROM dw.dim_date WHERE date_key <> -1 AND usd_brl IS NOT NULL)::text,
       (SELECT NOT loaded FROM apiflag) OR (SELECT count(*) = 1827 FROM dw.dim_date WHERE date_key <> -1 AND usd_brl IS NOT NULL)
UNION ALL SELECT 'API: USD/BRL has no missing business day (every weekday that is not an official holiday has its own quotation, 2016-2018)', 'ods.fx_usd_brl', '0 weekdays without quotation',
       (SELECT n FROM nobiz)::text || ' weekdays', (SELECT NOT loaded FROM apiflag) OR (SELECT n = 0 FROM nobiz)
UNION ALL SELECT 'API: IPCA has all 60 months 2016-01 .. 2020-12 and the first index is 100', 'ods.ipca_month', '60 months, first = 100',
       (SELECT count(*) || ' months, first = ' || min(ipca_index) FILTER (WHERE month_date = DATE '2016-01-01') FROM ods.ipca_month),
       (SELECT NOT loaded FROM apiflag) OR (SELECT count(*) = 60 AND count(DISTINCT date_trunc('month', month_date)) = 60 AND min(ipca_index) FILTER (WHERE month_date = DATE '2016-01-01') = 100 FROM ods.ipca_month)
UNION ALL SELECT 'API: our chained IPCA index agrees with the IBGE index series within 0.5 points', 'ods.ipca_month', 'max difference <= 0.5',
       'max difference ' || round((SELECT max_diff FROM ibge), 3), (SELECT NOT loaded FROM apiflag) OR (SELECT max_diff <= 0.5 FROM ibge)
UNION ALL SELECT 'API: every matched dim_geography row has a valid IBGE code of the same state', 'dw.dim_geography', '0 invalid',
       (SELECT count(*) FROM dw.dim_geography g LEFT JOIN ods.ibge_municipio m ON m.ibge_code = g.ibge_municipio_code
        WHERE g.ibge_municipio_code IS NOT NULL AND (m.ibge_code IS NULL OR m.state_code <> g.state_code))::text,
       (SELECT NOT loaded FROM apiflag) OR (SELECT count(*) = 0 FROM dw.dim_geography g LEFT JOIN ods.ibge_municipio m ON m.ibge_code = g.ibge_municipio_code
        WHERE g.ibge_municipio_code IS NOT NULL AND (m.ibge_code IS NULL OR m.state_code <> g.state_code))
UNION ALL SELECT 'API: no zip is assigned two municipalities (one IBGE code per zip and per (state, city))', 'dw.dim_geography', '0 zips / 0 cities',
       (SELECT count(*) FROM (SELECT zip_code_prefix FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL GROUP BY zip_code_prefix HAVING count(DISTINCT ibge_municipio_code) > 1) a) || ' zips / '
       || (SELECT count(*) FROM (SELECT state_code, city FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL GROUP BY state_code, city HAVING count(DISTINCT ibge_municipio_code) > 1) b) || ' cities',
       (SELECT NOT loaded FROM apiflag) OR ((SELECT count(*) FROM (SELECT zip_code_prefix FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL GROUP BY zip_code_prefix HAVING count(DISTINCT ibge_municipio_code) > 1) a) = 0
        AND (SELECT count(*) FROM (SELECT state_code, city FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL GROUP BY state_code, city HAVING count(DISTINCT ibge_municipio_code) > 1) b) = 0)
UNION ALL SELECT 'API: at least 95% of the zip codes are matched to an IBGE municipality', 'dw.dim_geography', '>= 95%',
       (SELECT round(100.0 * count(*) FILTER (WHERE ibge_municipio_code IS NOT NULL) / count(*), 1) || '%' FROM dw.dim_geography WHERE geography_key <> -1),
       (SELECT NOT loaded FROM apiflag) OR (SELECT 100.0 * count(*) FILTER (WHERE ibge_municipio_code IS NOT NULL) / count(*) >= 95 FROM dw.dim_geography WHERE geography_key <> -1)
UNION ALL SELECT 'API: every dim_geography row of the state has the same population of its municipality (2017 total of the matched rows is not null)', 'dw.dim_geography', '0 matched rows without population',
       (SELECT count(*) FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL AND populacao_2017 IS NULL)::text,
       (SELECT NOT loaded FROM apiflag) OR (SELECT count(*) = 0 FROM dw.dim_geography WHERE ibge_municipio_code IS NOT NULL AND populacao_2017 IS NULL)
UNION ALL SELECT 'API: official holidays flagged in dim_date = distinct BrasilAPI dates', 'dw.dim_date', (SELECT count(DISTINCT holiday_date) FROM ods.holiday_official)::text,
       (SELECT count(*) FROM dw.dim_date WHERE is_holiday_official)::text,
       (SELECT NOT loaded FROM apiflag) OR (SELECT count(*) FROM dw.dim_date WHERE is_holiday_official) = (SELECT count(DISTINCT holiday_date) FROM ods.holiday_official)
UNION ALL SELECT 'fact_state_year: sum(gmv) = GMV of fact_order_item', 'dw.fact_state_year', (SELECT gmv FROM g)::text, sum(gmv)::text, sum(gmv) = (SELECT gmv FROM g) FROM dw.fact_state_year
UNION ALL SELECT 'fact_state_year: sum(orders) = orders with revenue', 'dw.fact_state_year', (SELECT orders FROM g)::text, sum(orders)::text, sum(orders) = (SELECT orders FROM g) FROM dw.fact_state_year
UNION ALL SELECT 'fact_state_year: 27 states for every year of the order data', 'dw.fact_state_year', '27 x years',
       count(*) || ' rows, ' || count(DISTINCT year_date_key) || ' years', count(*) = 27 * count(DISTINCT year_date_key) FROM dw.fact_state_year
UNION ALL SELECT 'fact_state_year: population of Brazil 2017 equals the sum of the municipalities of ods.ibge_population', 'dw.fact_state_year',
       (SELECT sum(population)::text FROM ods.ibge_population WHERE year = 2017),
       (SELECT sum(population)::text FROM dw.fact_state_year WHERE year_date_key = 20170101),
       (SELECT NOT loaded FROM apiflag) OR (SELECT sum(population) FROM ods.ibge_population WHERE year = 2017) = (SELECT sum(population) FROM dw.fact_state_year WHERE year_date_key = 20170101)
UNION ALL SELECT 'mart_market.v_gmv_per_capita_state: sum(gmv) = GMV', 'mart_market.v_gmv_per_capita_state', (SELECT gmv FROM g)::text, sum(gmv)::text, sum(gmv) = (SELECT gmv FROM g) FROM mart_market.v_gmv_per_capita_state
UNION ALL SELECT 'mart_market.v_gmv_real_month: sum(gmv_nominal) = GMV (2016-01 .. 2018-12)', 'mart_market.v_gmv_real_month', (SELECT gmv FROM g)::text, sum(gmv_nominal)::text,
       (SELECT NOT loaded FROM apiflag) OR sum(gmv_nominal) = (SELECT gmv FROM g) FROM mart_market.v_gmv_real_month
UNION ALL SELECT 'mart_market.v_gmv_usd_month: sum(gmv_brl) = GMV', 'mart_market.v_gmv_usd_month', (SELECT gmv FROM g)::text, sum(gmv_brl)::text,
       (SELECT NOT loaded FROM apiflag) OR sum(gmv_brl) = (SELECT gmv FROM g) FROM mart_market.v_gmv_usd_month
UNION ALL SELECT 'mart_market.v_gmv_per_capita_city: sum(gmv) = GMV of the zips matched to a municipality', 'mart_market.v_gmv_per_capita_city',
       (SELECT sum(f.price)::text FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
        JOIN dw.dim_geography x ON x.geography_key = f.customer_geography_key WHERE x.ibge_municipio_code IS NOT NULL), sum(gmv)::text,
       sum(gmv) = (SELECT sum(f.price) FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'
                   JOIN dw.dim_geography x ON x.geography_key = f.customer_geography_key WHERE x.ibge_municipio_code IS NOT NULL) FROM mart_market.v_gmv_per_capita_city

-- setup: required
-- P9: enrich the warehouse with public API data (DW_DESIGN.md log 18/11): new columns on dim_geography and dim_date (no key changes),
-- new periodic snapshot dw.fact_state_year (grain: state x year). Everything is NULL / empty when the API data has not been loaded,
-- so the sales pipeline and the four dashboards DB1-DB4 behave exactly as before.

-- ---------------------------------------------------------------- dim_geography: IBGE hierarchy, population, match method
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS ibge_municipio_code int;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS microrregiao text;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS mesorregiao text;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS populacao_2016 int;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS populacao_2017 int;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS populacao_2018 int;
ALTER TABLE dw.dim_geography ADD COLUMN IF NOT EXISTS match_method text;   -- exact | normalized | fuzzy | override | unmatched (NULL if the API data is not loaded)

-- ---------------------------------------------------------------- dim_date: exchange rate, price index, official holidays
ALTER TABLE dw.dim_date ADD COLUMN IF NOT EXISTS usd_brl numeric(10,4);               -- BRL per USD; days without a quotation take the last business day
ALTER TABLE dw.dim_date ADD COLUMN IF NOT EXISTS ipca_index numeric(14,6);            -- IPCA price index, first month of the series (2016-01) = 100
ALTER TABLE dw.dim_date ADD COLUMN IF NOT EXISTS is_holiday_official boolean;         -- BrasilAPI national holiday
ALTER TABLE dw.dim_date ADD COLUMN IF NOT EXISTS holiday_name_official text;

-- ---------------------------------------------------------------- fact_state_year (periodic snapshot)
CREATE TABLE IF NOT EXISTS dw.fact_state_year (
    year_date_key int NOT NULL REFERENCES dw.dim_date (date_key),             -- 1 January of the year
    state_code char(2) NOT NULL, state_name text NOT NULL, region text NOT NULL,
    population bigint,                                                        -- IBGE estimate, sum of the municipalities of the state
    gdp_thousand_brl numeric(18,0),                                           -- IBGE municipal GDP at current prices, sum over the state
    gmv numeric(14,2) NOT NULL, orders int NOT NULL, customers int NOT NULL, sellers int NOT NULL,
    etl_batch_id bigint NOT NULL,
    PRIMARY KEY (year_date_key, state_code));

CREATE OR REPLACE PROCEDURE dw.enrich_dim_geography(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                    INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM dw.dim_geography WHERE geography_key <> -1;
    WITH x AS (
        SELECT g.geography_key, m.ibge_code, i.microrregiao, i.mesorregiao,
               p16.population AS p16, p17.population AS p17, p18.population AS p18,
               CASE WHEN EXISTS (SELECT 1 FROM ods.ibge_municipio) THEN coalesce(m.method, 'unmatched') END AS method
        FROM dw.dim_geography g
        LEFT JOIN ods.city_ibge_match m ON m.state_code = g.state_code AND m.city = g.city
        LEFT JOIN ods.ibge_municipio i ON i.ibge_code = m.ibge_code
        LEFT JOIN ods.ibge_population p16 ON p16.ibge_code = m.ibge_code AND p16.year = 2016
        LEFT JOIN ods.ibge_population p17 ON p17.ibge_code = m.ibge_code AND p17.year = 2017
        LEFT JOIN ods.ibge_population p18 ON p18.ibge_code = m.ibge_code AND p18.year = 2018
        WHERE g.geography_key <> -1)
    UPDATE dw.dim_geography g
    SET ibge_municipio_code = x.ibge_code, microrregiao = x.microrregiao, mesorregiao = x.mesorregiao,
        populacao_2016 = x.p16, populacao_2017 = x.p17, populacao_2018 = x.p18, match_method = x.method, dw_updated_at = now()
    FROM x
    WHERE g.geography_key = x.geography_key
      AND (g.ibge_municipio_code, g.microrregiao, g.mesorregiao, g.populacao_2016, g.populacao_2017, g.populacao_2018, g.match_method)
          IS DISTINCT FROM (x.ibge_code, x.microrregiao, x.mesorregiao, x.p16, x.p17, x.p18, x.method);
    GET DIAGNOSTICS p_updated = ROW_COUNT;
    p_inserted := 0; p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE dw.enrich_dim_date(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                               INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM dw.dim_date WHERE date_key <> -1;
    WITH hol AS (SELECT holiday_date, string_agg(DISTINCT name, ' / ' ORDER BY name) AS names FROM ods.holiday_official GROUP BY holiday_date),
    x AS (
        SELECT d.date_key, f.usd_brl, i.ipca_index,
               CASE WHEN EXISTS (SELECT 1 FROM ods.holiday_official) THEN (h.holiday_date IS NOT NULL) END AS is_off,
               h.names
        FROM dw.dim_date d
        LEFT JOIN ods.fx_usd_brl f ON f.rate_date = d.full_date
        LEFT JOIN ods.ipca_month i ON i.month_date = date_trunc('month', d.full_date)::date
        LEFT JOIN hol h ON h.holiday_date = d.full_date
        WHERE d.date_key <> -1)
    UPDATE dw.dim_date d
    SET usd_brl = x.usd_brl, ipca_index = x.ipca_index, is_holiday_official = x.is_off, holiday_name_official = x.names, dw_updated_at = now()
    FROM x
    WHERE d.date_key = x.date_key
      AND (d.usd_brl, d.ipca_index, d.is_holiday_official, d.holiday_name_official) IS DISTINCT FROM (x.usd_brl, x.ipca_index, x.is_off, x.names);
    GET DIAGNOSTICS p_updated = ROW_COUNT;
    p_inserted := 0; p_rejected := 0;
END $$;

-- one row per state x year (every state, every year of the order data), recomputed from the facts and the IBGE ODS on every run
CREATE OR REPLACE PROCEDURE dw.load_fact_state_year(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                    INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM dw.fact_order_item;
    DELETE FROM dw.fact_state_year;
    INSERT INTO dw.fact_state_year (year_date_key, state_code, state_name, region, population, gdp_thousand_brl, gmv, orders, customers, sellers, etl_batch_id)
    WITH yrs AS (
        SELECT y, (y * 10000 + 101) AS year_date_key FROM generate_series(
            (SELECT min(d.year) FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key),
            (SELECT max(d.year) FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key)) y),
    it AS (   -- sold items (not Failed) with the year, the customer state and the seller state
        SELECT d.year AS y, f.order_id, gc.state_code AS cust_state, gs.state_code AS sell_state, f.price, c.customer_unique_id, f.seller_key
        FROM dw.fact_order_item f
        JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
        JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
        JOIN dw.dim_geography gc ON gc.geography_key = f.customer_geography_key
        JOIN dw.dim_geography gs ON gs.geography_key = f.seller_geography_key
        JOIN dw.dim_customer c ON c.customer_key = f.customer_key),
    sales AS (SELECT y, cust_state AS st, sum(price) AS gmv, count(DISTINCT order_id) AS orders, count(DISTINCT customer_unique_id) AS customers
              FROM it GROUP BY y, cust_state),
    sellers AS (SELECT y, sell_state AS st, count(DISTINCT seller_key) AS sellers FROM it GROUP BY y, sell_state),
    pop AS (SELECT m.state_code AS st, p.year AS y, sum(p.population) AS population
            FROM ods.ibge_population p JOIN ods.ibge_municipio m USING (ibge_code) GROUP BY m.state_code, p.year),
    gdp AS (SELECT m.state_code AS st, p.year AS y, sum(p.gdp_thousand_brl) AS gdp
            FROM ods.ibge_gdp p JOIN ods.ibge_municipio m USING (ibge_code) GROUP BY m.state_code, p.year)
    SELECT yrs.year_date_key, r.state_code, r.state_name, r.region, pop.population, gdp.gdp,
           coalesce(s.gmv, 0), coalesce(s.orders, 0), coalesce(s.customers, 0), coalesce(sl.sellers, 0), p_batch_id
    FROM yrs CROSS JOIN ods.ref_state_region r
    LEFT JOIN sales s ON s.y = yrs.y AND s.st = r.state_code
    LEFT JOIN sellers sl ON sl.y = yrs.y AND sl.st = r.state_code
    LEFT JOIN pop ON pop.y = yrs.y AND pop.st = r.state_code
    LEFT JOIN gdp ON gdp.y = yrs.y AND gdp.st = r.state_code
    ORDER BY yrs.year_date_key, r.state_code;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_updated := 0; p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- metadata (Vietnamese comments)
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN SELECT * FROM (VALUES
        ('dim_geography', 'ibge_municipio_code', 'Mã đô thị IBGE (7 chữ số) ghép từ (bang, thành phố); NULL nếu chưa ghép hoặc chưa nạp dữ liệu API'),
        ('dim_geography', 'microrregiao', 'Microrregião IBGE của đô thị'), ('dim_geography', 'mesorregiao', 'Mesorregião IBGE của đô thị'),
        ('dim_geography', 'populacao_2016', 'Dân số ước tính 2016 của đô thị (IBGE); cùng giá trị cho mọi zip của đô thị, không cộng theo zip'),
        ('dim_geography', 'populacao_2017', 'Dân số ước tính 2017 của đô thị (IBGE)'), ('dim_geography', 'populacao_2018', 'Dân số ước tính 2018 của đô thị (IBGE)'),
        ('dim_geography', 'match_method', 'Tầng ghép đô thị: exact | normalized | fuzzy | override | unmatched; NULL nếu chưa nạp dữ liệu API'),
        ('dim_date', 'usd_brl', 'Tỷ giá USD/BRL (Banco Central, chuỗi SGS 1, giá bán); ngày không giao dịch lấy giá ngày làm việc gần nhất trước đó'),
        ('dim_date', 'ipca_index', 'Chỉ số giá IPCA, tháng đầu kỳ (2016-01) = 100, nối theo biến động tháng (SGS 433); mọi ngày của một tháng cùng giá trị'),
        ('dim_date', 'is_holiday_official', 'Ngày lễ quốc gia theo BrasilAPI (so với is_holiday_br của thư viện holidays)'),
        ('dim_date', 'holiday_name_official', 'Tên ngày lễ theo BrasilAPI'),
        ('fact_state_year', NULL, 'Fact periodic snapshot: 1 bang x 1 năm (27 bang x các năm có đơn); dân số và PIB từ IBGE, GMV, đơn, khách, seller của Olist'),
        ('fact_state_year', 'year_date_key', 'Ngày 1/1 của năm -> dim_date'), ('fact_state_year', 'state_code', 'Bang (theo địa lý của khách cho GMV, đơn, khách; theo địa lý seller cho sellers)'),
        ('fact_state_year', 'population', 'Dân số ước tính của bang (tổng các đô thị, IBGE SIDRA 6579); NULL nếu chưa nạp API'),
        ('fact_state_year', 'gdp_thousand_brl', 'PIB giá hiện hành của bang (tổng PIB đô thị, IBGE SIDRA 5938), nghìn BRL; NULL nếu chưa có'),
        ('fact_state_year', 'gmv', 'Σ price của đơn không bị Failed, theo bang của khách và năm mua (khớp định nghĩa GMV)'),
        ('fact_state_year', 'orders', 'Số đơn có doanh thu'), ('fact_state_year', 'customers', 'Số khách thật (customer_unique_id) có đơn có doanh thu'),
        ('fact_state_year', 'sellers', 'Số seller có đơn có doanh thu, theo bang của seller'),
        ('fact_state_year', 'etl_batch_id', 'Lô ETL đã tính')
    ) AS t(tbl, col, cmt)
    LOOP
        IF r.col IS NULL THEN
            EXECUTE format('COMMENT ON TABLE dw.%I IS %L', r.tbl, r.cmt);
        ELSE
            EXECUTE format('COMMENT ON COLUMN dw.%I.%I IS %L', r.tbl, r.col, r.cmt);
        END IF;
    END LOOP;
END $$;

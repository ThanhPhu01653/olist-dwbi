-- setup: required
-- P9: ODS of the public API data. Typed and cleaned copies of api.stg_api_*, plus the match "Olist (state, city) -> IBGE municipality".
-- Layer name in etl_log.job_run is 'api_ods' so the existing monitoring numbers of the sales pipeline (v_run_summary) do not change.

-- lower case, no accents, every run of non-alphanumeric characters (spaces, hyphens, apostrophes, dots) becomes one space
CREATE OR REPLACE FUNCTION ods.name_key(p_name text) RETURNS text LANGUAGE sql STABLE AS $$
    SELECT nullif(btrim(regexp_replace(lower(unaccent(p_name)), '[^a-z0-9]+', ' ', 'g')), '')
$$;

CREATE TABLE IF NOT EXISTS ods.ibge_municipio (
    ibge_code int PRIMARY KEY, name text NOT NULL, name_key text NOT NULL, state_code char(2) NOT NULL, state_ibge_code int,
    microrregiao text, mesorregiao text, etl_batch_id bigint);
CREATE INDEX IF NOT EXISTS ix_ods_ibge_municipio_key ON ods.ibge_municipio (state_code, name_key);

CREATE TABLE IF NOT EXISTS ods.ibge_population (
    ibge_code int NOT NULL, year int NOT NULL, population bigint NOT NULL, etl_batch_id bigint, PRIMARY KEY (ibge_code, year));
CREATE TABLE IF NOT EXISTS ods.ibge_gdp (
    ibge_code int NOT NULL, year int NOT NULL, gdp_thousand_brl numeric(18,0) NOT NULL, etl_batch_id bigint, PRIMARY KEY (ibge_code, year));

CREATE TABLE IF NOT EXISTS ods.fx_usd_brl (               -- one row per calendar day 2016-01-01 .. 2020-12-31, forward filled from the last business day
    rate_date date PRIMARY KEY, usd_brl numeric(10,4) NOT NULL, rate_source_date date NOT NULL, is_business_day boolean NOT NULL, etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.ipca_month (               -- first month of the series = 100, then chained with the monthly change
    month_date date PRIMARY KEY, change_pct numeric(8,4) NOT NULL, ipca_index numeric(14,6) NOT NULL, etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.holiday_official (holiday_date date NOT NULL, name text NOT NULL, type text, etl_batch_id bigint, PRIMARY KEY (holiday_date, name));

CREATE TABLE IF NOT EXISTS ods.weather_station (state_code char(2) PRIMARY KEY, city text NOT NULL, latitude double precision, longitude double precision, etl_batch_id bigint);
CREATE TABLE IF NOT EXISTS ods.weather_daily (state_code char(2) NOT NULL, obs_date date NOT NULL, precip_mm numeric(7,2) NOT NULL, etl_batch_id bigint, PRIMARY KEY (state_code, obs_date));

CREATE TABLE IF NOT EXISTS ods.city_ibge_match (
    state_code char(2) NOT NULL, city text NOT NULL, ibge_code int NOT NULL REFERENCES ods.ibge_municipio (ibge_code),
    method text NOT NULL CHECK (method IN ('exact', 'normalized', 'fuzzy', 'override')), score numeric(5,1), etl_batch_id bigint,
    PRIMARY KEY (state_code, city));

-- distinct (state, city) pairs of every zip of the sales data, built exactly like dw.load_dim_geography (geolocation first, then customers / sellers)
CREATE OR REPLACE VIEW ods.v_geo_city_pair AS
WITH other AS (
    SELECT zip, mode() WITHIN GROUP (ORDER BY city) AS city, mode() WITHIN GROUP (ORDER BY st) AS st
    FROM (SELECT zip_code_prefix AS zip, city, state_code AS st FROM ods.customers
          UNION ALL SELECT zip_code_prefix, city, state_code FROM ods.sellers) u
    WHERE zip IS NOT NULL GROUP BY zip),
z AS (
    SELECT coalesce(g.zip_code_prefix, o.zip) AS zip, coalesce(g.city, o.city) AS city, coalesce(g.state_code, o.st) AS st
    FROM ods.geolocation_zip g FULL JOIN other o ON o.zip = g.zip_code_prefix)
SELECT st AS state_code, city, count(*)::int AS zips FROM z WHERE city IS NOT NULL AND st IS NOT NULL GROUP BY st, city;

-- ---------------------------------------------------------------- IBGE: municipalities, population, GDP
CREATE OR REPLACE PROCEDURE ods.load_api_ibge(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE n_pop bigint; n_gdp bigint;
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE job_name = 'ods.load_api_ibge';   -- recomputed from the full staging on every run: keep only the latest list
    SELECT (SELECT count(*) FROM api.stg_api_ibge_municipio) + (SELECT count(*) FROM api.stg_api_ibge_populacao)
           + (SELECT count(*) FROM api.stg_api_ibge_pib) INTO p_read;
    TRUNCATE ods.city_ibge_match, ods.ibge_municipio, ods.ibge_population, ods.ibge_gdp;
    INSERT INTO ods.ibge_municipio (ibge_code, name, name_key, state_code, state_ibge_code, microrregiao, mesorregiao, etl_batch_id)
    SELECT ibge_code, nome, ods.name_key(nome), uf_sigla, uf_code, microrregiao_nome, mesorregiao_nome, p_batch_id
    FROM api.stg_api_ibge_municipio WHERE uf_sigla IS NOT NULL ORDER BY ibge_code;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    INSERT INTO ods.ibge_population (ibge_code, year, population, etl_batch_id)
    SELECT ibge_code, year, value_raw::bigint, p_batch_id FROM api.stg_api_ibge_populacao WHERE value_raw ~ '^[0-9]+$';
    GET DIAGNOSTICS n_pop = ROW_COUNT;
    INSERT INTO ods.ibge_gdp (ibge_code, year, gdp_thousand_brl, etl_batch_id)
    SELECT ibge_code, year, value_raw::numeric, p_batch_id FROM api.stg_api_ibge_pib WHERE value_raw ~ '^[0-9]+$';
    GET DIAGNOSTICS n_gdp = ROW_COUNT;
    p_inserted := p_inserted + n_pop + n_gdp;
    -- values the API itself marks as not available ('...', '-', 'X'): kept out of the numbers, never silently
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_api_ibge', 'api.stg_api_ibge_populacao', 'value not available in the API (' || value_raw || ')',
           jsonb_build_object('ibge_code', ibge_code, 'year', year, 'value', value_raw)
    FROM api.stg_api_ibge_populacao WHERE value_raw !~ '^[0-9]+$' OR value_raw IS NULL;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_api_ibge', 'api.stg_api_ibge_pib', 'value not available in the API (' || coalesce(value_raw, 'null') || ')',
           jsonb_build_object('ibge_code', ibge_code, 'year', year, 'value', value_raw)
    FROM api.stg_api_ibge_pib WHERE value_raw !~ '^[0-9]+$' OR value_raw IS NULL;
    SELECT count(*) INTO p_rejected FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_api_ibge';
END $$;

-- ---------------------------------------------------------------- Banco Central: USD/BRL (daily, forward filled) and IPCA (monthly, chained index)
CREATE OR REPLACE PROCEDURE ods.load_api_fx(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE job_name = 'ods.load_api_fx';   -- recomputed from the full staging on every run: keep only the latest list
    SELECT count(*) INTO p_read FROM api.stg_api_bcb_serie WHERE series_code = 1;
    TRUNCATE ods.fx_usd_brl;
    -- days without a quotation (weekends, holidays) take the rate of the closest earlier business day
    INSERT INTO ods.fx_usd_brl (rate_date, usd_brl, rate_source_date, is_business_day, etl_batch_id)
    SELECT d::date, r.v, r.dt, (r.dt = d::date), p_batch_id
    FROM generate_series(DATE '2016-01-01', DATE '2020-12-31', INTERVAL '1 day') d
    JOIN LATERAL (SELECT ref_date AS dt, value_raw::numeric AS v FROM api.stg_api_bcb_serie
                  WHERE series_code = 1 AND ref_date <= d::date AND value_raw ~ '^[0-9.]+$' ORDER BY ref_date DESC LIMIT 1) r ON true
    ORDER BY d;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_api_fx', 'api.stg_api_bcb_serie', 'rate is not a number', jsonb_build_object('ref_date', ref_date, 'value', value_raw)
    FROM api.stg_api_bcb_serie WHERE series_code = 1 AND (value_raw IS NULL OR value_raw !~ '^[0-9.]+$');
    p_rejected := (SELECT count(*) FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_api_fx');
END $$;

CREATE OR REPLACE PROCEDURE ods.load_api_ipca(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE job_name = 'ods.load_api_ipca';   -- recomputed from the full staging on every run: keep only the latest list
    SELECT count(*) INTO p_read FROM api.stg_api_bcb_serie WHERE series_code = 433;
    TRUNCATE ods.ipca_month;
    -- index(first month) = 100; index(m) = 100 * product of (1 + change/100) over the months after the first up to m
    INSERT INTO ods.ipca_month (month_date, change_pct, ipca_index, etl_batch_id)
    SELECT ref_date, value_raw::numeric,
           round((100 * exp(coalesce(sum(ln(1 + value_raw::numeric / 100)) FILTER (WHERE rn > 1) OVER (ORDER BY ref_date), 0)))::numeric, 6), p_batch_id
    FROM (SELECT ref_date, value_raw, row_number() OVER (ORDER BY ref_date) AS rn
          FROM api.stg_api_bcb_serie WHERE series_code = 433 AND value_raw ~ '^-?[0-9.]+$') s
    ORDER BY ref_date;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_api_ipca', 'api.stg_api_bcb_serie', 'change is not a number', jsonb_build_object('ref_date', ref_date, 'value', value_raw)
    FROM api.stg_api_bcb_serie WHERE series_code = 433 AND (value_raw IS NULL OR value_raw !~ '^-?[0-9.]+$');
    p_rejected := (SELECT count(*) FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_api_ipca');
END $$;

-- ---------------------------------------------------------------- BrasilAPI holidays and Open-Meteo weather
CREATE OR REPLACE PROCEDURE ods.load_api_holidays(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM api.stg_api_holiday;
    TRUNCATE ods.holiday_official;
    INSERT INTO ods.holiday_official (holiday_date, name, type, etl_batch_id)
    SELECT holiday_date, btrim(name), type, p_batch_id FROM api.stg_api_holiday ORDER BY holiday_date, name;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE ods.load_api_weather(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE job_name = 'ods.load_api_weather';   -- recomputed from the full staging on every run: keep only the latest list
    SELECT count(*) INTO p_read FROM api.stg_api_weather_daily;
    TRUNCATE ods.weather_station, ods.weather_daily;
    INSERT INTO ods.weather_station (state_code, city, latitude, longitude, etl_batch_id)
    SELECT state_code, city, latitude, longitude, p_batch_id FROM api.stg_api_weather_station ORDER BY state_code;
    INSERT INTO ods.weather_daily (state_code, obs_date, precip_mm, etl_batch_id)
    SELECT state_code, obs_date, precip_raw::numeric, p_batch_id FROM api.stg_api_weather_daily WHERE precip_raw ~ '^-?[0-9.]+$' ORDER BY state_code, obs_date;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_api_weather', 'api.stg_api_weather_daily', 'no precipitation value that day',
           jsonb_build_object('state_code', state_code, 'obs_date', obs_date)
    FROM api.stg_api_weather_daily WHERE precip_raw IS NULL OR precip_raw !~ '^-?[0-9.]+$';
    p_rejected := (SELECT count(*) FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_api_weather');
END $$;

-- ---------------------------------------------------------------- city match, tiers 1 and 2 (SQL); tiers 3 (fuzzy) and 4 (override) run in api_ingest/match.py
-- tier 1 "exact": the Olist city equals the IBGE name in lower case (same state, character for character)
-- tier 2 "normalized": equal after removing accents and extra characters (apostrophes, hyphens, double spaces); only if the key is unique in the state
CREATE OR REPLACE PROCEDURE ods.match_city_exact(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE n1 bigint; n2 bigint;
BEGIN
    SELECT count(*) INTO p_read FROM ods.v_geo_city_pair;
    TRUNCATE ods.city_ibge_match;
    INSERT INTO ods.city_ibge_match (state_code, city, ibge_code, method, score, etl_batch_id)
    SELECT p.state_code, p.city, m.ibge_code, 'exact', 100, p_batch_id
    FROM ods.v_geo_city_pair p JOIN ods.ibge_municipio m ON m.state_code = p.state_code AND lower(m.name) = p.city
    ORDER BY p.state_code, p.city
    ON CONFLICT DO NOTHING;
    GET DIAGNOSTICS n1 = ROW_COUNT;
    INSERT INTO ods.city_ibge_match (state_code, city, ibge_code, method, score, etl_batch_id)
    SELECT p.state_code, p.city, k.ibge_code, 'normalized', 100, p_batch_id
    FROM ods.v_geo_city_pair p
    JOIN (SELECT state_code, name_key, min(ibge_code) AS ibge_code FROM ods.ibge_municipio GROUP BY state_code, name_key HAVING count(*) = 1) k
         ON k.state_code = p.state_code AND k.name_key = ods.name_key(p.city)
    WHERE NOT EXISTS (SELECT 1 FROM ods.city_ibge_match x WHERE x.state_code = p.state_code AND x.city = p.city)
    ORDER BY p.state_code, p.city;
    GET DIAGNOSTICS n2 = ROW_COUNT;
    p_inserted := n1 + n2;
    p_rejected := 0;
END $$;

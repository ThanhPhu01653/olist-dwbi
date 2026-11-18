-- setup: required
-- P9: staging of the public API data (schema api). Raw copies of the JSON landed in data/raw/api/<source>/<run date>/ (api_ingest).
-- Values stay as the API returned them (text where the API uses text such as '-' or '...'); parsing and typing happen in ODS.

CREATE TABLE IF NOT EXISTS api.stg_api_ibge_estado (            -- IBGE Localidades /estados
    ibge_code int PRIMARY KEY, sigla char(2) NOT NULL, nome text NOT NULL, regiao_code int, regiao_sigla text, regiao_nome text,
    load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS api.stg_api_ibge_municipio (         -- IBGE Localidades /municipios (hierarchy region > state > mesoregion > microregion > municipality)
    ibge_code int PRIMARY KEY, nome text NOT NULL, uf_code int, uf_sigla char(2),
    microrregiao_code int, microrregiao_nome text, mesorregiao_code int, mesorregiao_nome text,
    imediata_code int, imediata_nome text, intermediaria_code int, intermediaria_nome text,
    load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS api.stg_api_ibge_populacao (         -- IBGE SIDRA aggregate 6579, variable 9324 (estimated resident population)
    ibge_code int NOT NULL, year int NOT NULL, value_raw text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (ibge_code, year));

CREATE TABLE IF NOT EXISTS api.stg_api_ibge_pib (               -- IBGE SIDRA aggregate 5938, variable 37 (GDP at current prices, thousand BRL)
    ibge_code int NOT NULL, year int NOT NULL, value_raw text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (ibge_code, year));

CREATE TABLE IF NOT EXISTS api.stg_api_bcb_serie (              -- Banco Central SGS: series 1 (USD sell rate, daily) and 433 (IPCA monthly change, %)
    series_code int NOT NULL, ref_date date NOT NULL, value_raw text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (series_code, ref_date));

CREATE TABLE IF NOT EXISTS api.stg_api_holiday (                -- BrasilAPI /feriados/v1/<year>
    holiday_date date NOT NULL, name text NOT NULL, type text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (holiday_date, name));

CREATE TABLE IF NOT EXISTS api.stg_api_weather_station (        -- Open-Meteo geocoding: the capital of each state (optional source)
    state_code char(2) PRIMARY KEY, city text NOT NULL, latitude double precision, longitude double precision,
    load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now());

CREATE TABLE IF NOT EXISTS api.stg_api_weather_daily (          -- Open-Meteo archive: daily precipitation (mm) at the capital (optional source)
    state_code char(2) NOT NULL, obs_date date NOT NULL, precip_raw text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (state_code, obs_date));

CREATE TABLE IF NOT EXISTS api.stg_api_ibge_ipca (              -- IBGE SIDRA aggregate 1737 (IPCA): used to cross-check Banco Central series 433
    period char(6) PRIMARY KEY, var_raw text, index_raw text, load_batch_id bigint, loaded_at timestamptz NOT NULL DEFAULT now());

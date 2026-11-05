-- setup: required
-- ETL monitoring tables (DW_DESIGN.md section 11). Feeds dashboard D7.

-- Batch ids come from one sequence so every pipeline run / load has a unique number.
CREATE SEQUENCE IF NOT EXISTS etl_log.batch_seq;

CREATE TABLE IF NOT EXISTS etl_log.job_run (
    run_id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id       bigint      NOT NULL,
    job_name       text        NOT NULL,
    layer          text        NOT NULL,        -- source | staging | ods | dw | mart | test
    target_table   text,
    started_at     timestamptz NOT NULL DEFAULT now(),
    finished_at    timestamptz,
    status         text        NOT NULL DEFAULT 'running'
                   CHECK (status IN ('running', 'success', 'failed')),
    rows_read      bigint      NOT NULL DEFAULT 0,
    rows_inserted  bigint      NOT NULL DEFAULT 0,
    rows_updated   bigint      NOT NULL DEFAULT 0,
    rows_rejected  bigint      NOT NULL DEFAULT 0,
    message        text
);
CREATE INDEX IF NOT EXISTS ix_job_run_batch ON etl_log.job_run (batch_id);

CREATE TABLE IF NOT EXISTS etl_log.rejected_rows (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id      bigint      NOT NULL,
    job_name      text        NOT NULL,
    source_table  text        NOT NULL,
    reason        text        NOT NULL,
    record        jsonb       NOT NULL,         -- the rejected row, as read from the source
    logged_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_rejected_rows_batch ON etl_log.rejected_rows (batch_id);

CREATE TABLE IF NOT EXISTS etl_log.watermark (
    source_table  text PRIMARY KEY,
    last_value    timestamptz,
    updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS etl_log.dq_check (
    batch_id      bigint      NOT NULL,
    check_name    text        NOT NULL,
    target_table  text,
    expected      text,
    actual        text,
    passed        boolean     NOT NULL,
    checked_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_dq_check_batch ON etl_log.dq_check (batch_id);

-- Lookups that fell back to the Unknown member (-1) and time intervals set to NULL while loading facts (never silent).
CREATE TABLE IF NOT EXISTS etl_log.fact_load_issue (
    batch_id      bigint      NOT NULL,
    fact_table    text        NOT NULL,
    issue_type    text        NOT NULL,         -- unknown_member | negative_interval
    detail        text        NOT NULL,         -- column / interval concerned
    row_count     bigint      NOT NULL,
    logged_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_fact_load_issue_batch ON etl_log.fact_load_issue (batch_id);

-- Key figures of the warehouse after every pipeline run (shows the funnel and the sales filling up batch by batch; dashboard D7).
CREATE TABLE IF NOT EXISTS etl_log.batch_metrics (
    batch_id        bigint PRIMARY KEY,
    taken_at        timestamptz NOT NULL DEFAULT now(),
    mode            text,
    orders          bigint, order_items bigint, gmv numeric(14,2),
    mql             bigint, deals_won bigint, sellers_with_sale bigint,
    customers       bigint, customer_versions bigint, sellers bigint
);

-- One row per batch: mode, duration, rows per layer. The pipeline writes one 'pipeline.<mode>' row per run.
CREATE OR REPLACE VIEW etl_log.v_run_summary AS
SELECT j.batch_id,
       coalesce(max(replace(j.job_name, 'pipeline.', '')) FILTER (WHERE j.layer = 'pipeline'), max(split_part(j.job_name, '.', 1))) AS mode,
       min(j.started_at) AS started_at, max(j.finished_at) AS finished_at,
       round(extract(epoch FROM max(j.finished_at) - min(j.started_at))::numeric, 1) AS duration_sec,
       CASE WHEN bool_or(j.status = 'failed') THEN 'failed' WHEN bool_or(j.status = 'running') THEN 'running' ELSE 'success' END AS status,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'source'), 0) AS source_rows,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'staging'), 0) AS staging_rows,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'ods' AND j.job_name NOT LIKE 'seeds.%'), 0) AS ods_inserted,
       coalesce(sum(j.rows_rejected) FILTER (WHERE j.layer = 'ods'), 0) AS ods_rejected,
       coalesce(sum(j.rows_inserted) FILTER (WHERE j.layer = 'dw'), 0) AS dw_inserted,
       coalesce(sum(j.rows_updated) FILTER (WHERE j.layer = 'dw'), 0) AS dw_updated,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.layer = 'staging'), 0)::numeric, 1) AS staging_sec,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.layer = 'ods'), 0)::numeric, 1) AS ods_sec,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.layer = 'dw'), 0)::numeric, 1) AS dw_sec,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.layer = 'test'), 0)::numeric, 1) AS test_sec,
       round(coalesce(sum(extract(epoch FROM j.finished_at - j.started_at)) FILTER (WHERE j.layer = 'mart'), 0)::numeric, 1) AS mart_sec
FROM etl_log.job_run j
GROUP BY j.batch_id;

-- One row per batch that ran tests. The 'EDA:' cross-check rows are report only and are counted separately.
CREATE OR REPLACE VIEW etl_log.v_dq_summary AS
SELECT batch_id,
       count(*) FILTER (WHERE check_name NOT LIKE 'EDA:%') AS checks,
       count(*) FILTER (WHERE check_name NOT LIKE 'EDA:%' AND passed) AS passed,
       count(*) FILTER (WHERE check_name NOT LIKE 'EDA:%' AND NOT passed) AS failed,
       round(100.0 * avg(passed::int) FILTER (WHERE check_name NOT LIKE 'EDA:%'), 1) AS pass_pct,
       count(*) FILTER (WHERE check_name LIKE 'EDA:%') AS eda_checks,
       count(*) FILTER (WHERE check_name LIKE 'EDA:%' AND passed) AS eda_match,
       min(checked_at) AS checked_at
FROM etl_log.dq_check GROUP BY batch_id;

-- Rows kept out of the warehouse, by batch / job / reason (the rows themselves stay in etl_log.rejected_rows).
CREATE OR REPLACE VIEW etl_log.v_rejected_summary AS
SELECT batch_id, job_name, source_table, reason, count(*) AS row_count, max(logged_at) AS last_logged_at
FROM etl_log.rejected_rows GROUP BY batch_id, job_name, source_table, reason;

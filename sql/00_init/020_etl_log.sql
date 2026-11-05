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

-- setup: required
-- One schema per layer (see CLAUDE.md / DW_DESIGN.md section 3).
CREATE SCHEMA IF NOT EXISTS oltp;              -- source system 1: sales (simulated)
CREATE SCHEMA IF NOT EXISTS crm;               -- source system 2: CRM / marketing (simulated)
CREATE SCHEMA IF NOT EXISTS staging;           -- raw copies, stg_*
CREATE SCHEMA IF NOT EXISTS ods;               -- cleaned operational data store
CREATE SCHEMA IF NOT EXISTS dw;                -- star schema: dim_* + fact_*
CREATE SCHEMA IF NOT EXISTS mart_sales;
CREATE SCHEMA IF NOT EXISTS mart_fulfillment;
CREATE SCHEMA IF NOT EXISTS mart_cx;
CREATE SCHEMA IF NOT EXISTS mart_acquisition;
CREATE SCHEMA IF NOT EXISTS etl_log;           -- job monitoring

-- setup: required
-- ODS = cleaned operational data store (DW_DESIGN 2.3). Idempotent: CREATE ... IF NOT EXISTS.

-- ---------- reference tables (loaded from seeds/*.csv by etl/load_seeds.py) ----------
CREATE TABLE IF NOT EXISTS ods.ref_state_region (
    state_code char(2) PRIMARY KEY, state_name text NOT NULL, region text NOT NULL);
CREATE TABLE IF NOT EXISTS ods.ref_category_translation_extra (
    product_category_name text PRIMARY KEY, product_category_name_english text NOT NULL);
CREATE TABLE IF NOT EXISTS ods.ref_category_group (
    product_category_name text PRIMARY KEY, category_group text NOT NULL);
CREATE TABLE IF NOT EXISTS ods.ref_lead_origin_group (
    origin text PRIMARY KEY, channel_group text NOT NULL);
CREATE TABLE IF NOT EXISTS ods.ref_payment_type (
    payment_type text PRIMARY KEY, payment_group text NOT NULL, display_name text NOT NULL);
CREATE TABLE IF NOT EXISTS ods.ref_order_status (
    order_status text PRIMARY KEY, status_group text NOT NULL, is_final boolean NOT NULL);

-- ---------- cleaned tables ----------
CREATE TABLE IF NOT EXISTS ods.category_translation (
    product_category_name text PRIMARY KEY, product_category_name_english text, etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.products (
    product_id char(32) PRIMARY KEY,
    product_category_name text NOT NULL,            -- empty -> 'unknown'
    name_length integer, description_length integer, photos_qty integer,   -- renamed from *_lenght
    weight_g integer, length_cm integer, height_cm integer, width_cm integer,
    dq_missing_dimensions boolean NOT NULL DEFAULT false,
    etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.sellers (
    seller_id char(32) PRIMARY KEY, zip_code_prefix char(5), city text, state_code char(2), etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.customers (
    customer_id char(32) PRIMARY KEY, customer_unique_id char(32) NOT NULL,
    zip_code_prefix char(5), city text, state_code char(2), etl_batch_id bigint);
CREATE INDEX IF NOT EXISTS ix_ods_customers_unique ON ods.customers (customer_unique_id);

CREATE TABLE IF NOT EXISTS ods.customer_map (
    customer_id char(32) PRIMARY KEY, customer_unique_id char(32) NOT NULL, etl_batch_id bigint);

-- one row per zip: median coordinates, mode city/state (after bounding-box filter).
-- A zip whose points all lie outside the bbox is kept with NULL coordinates and n_points = 0 (decision "e": never lose a zip).
CREATE TABLE IF NOT EXISTS ods.geolocation_zip (
    zip_code_prefix char(5) PRIMARY KEY, latitude double precision, longitude double precision,
    city text, state_code char(2), n_points integer NOT NULL, etl_batch_id bigint);

CREATE TABLE IF NOT EXISTS ods.orders (
    order_id char(32) PRIMARY KEY, customer_id char(32) NOT NULL, order_status text NOT NULL,
    order_purchase_timestamp timestamp NOT NULL, order_approved_at timestamp,
    order_delivered_carrier_date timestamp, order_delivered_customer_date timestamp,
    order_estimated_delivery_date timestamp,
    dq_flags text[] NOT NULL DEFAULT '{}', dq_flag_count integer NOT NULL DEFAULT 0, etl_batch_id bigint);
CREATE INDEX IF NOT EXISTS ix_ods_orders_customer ON ods.orders (customer_id);

CREATE TABLE IF NOT EXISTS ods.order_items (
    order_id char(32) NOT NULL, order_item_id integer NOT NULL, product_id char(32) NOT NULL, seller_id char(32) NOT NULL,
    shipping_limit_date timestamp, price numeric(12,2), freight_value numeric(12,2), etl_batch_id bigint,
    PRIMARY KEY (order_id, order_item_id));

CREATE TABLE IF NOT EXISTS ods.order_payments (
    order_id char(32) NOT NULL, payment_sequential integer NOT NULL, payment_type text,
    payment_installments integer NOT NULL, payment_value numeric(12,2),
    dq_flags text[] NOT NULL DEFAULT '{}', etl_batch_id bigint,
    PRIMARY KEY (order_id, payment_sequential));

CREATE TABLE IF NOT EXISTS ods.order_reviews (
    review_id char(32) NOT NULL, order_id char(32) NOT NULL, review_score smallint,
    review_comment_title text, review_comment_message text,
    review_creation_date timestamp, review_answer_timestamp timestamp, etl_batch_id bigint,
    PRIMARY KEY (review_id, order_id));

CREATE TABLE IF NOT EXISTS ods.mql (
    mql_id char(32) PRIMARY KEY, first_contact_date date NOT NULL, landing_page_id char(32),
    origin text NOT NULL, etl_batch_id bigint);          -- NULL origin -> 'unknown'

CREATE TABLE IF NOT EXISTS ods.closed_deals (
    mql_id char(32) PRIMARY KEY, seller_id char(32) NOT NULL, sdr_id char(32), sr_id char(32), won_date timestamp NOT NULL,
    business_segment text NOT NULL, lead_type text NOT NULL, lead_behaviour_profile text NOT NULL, business_type text NOT NULL,
    has_company text NOT NULL, has_gtin text NOT NULL, average_stock text NOT NULL,   -- 'true' / 'false' / 'unknown'
    declared_product_catalog_size numeric(12,1), declared_monthly_revenue numeric(14,2),
    dq_flags text[] NOT NULL DEFAULT '{}', etl_batch_id bigint);
CREATE INDEX IF NOT EXISTS ix_ods_closed_deals_seller ON ods.closed_deals (seller_id);

COMMENT ON SCHEMA ods IS 'Operational Data Store: dữ liệu nguồn đã làm sạch, chuẩn hoá, có cờ chất lượng dq_flags';
COMMENT ON TABLE ods.geolocation_zip IS '1 dòng / zip: toạ độ median sau khi lọc bbox Brazil, city/state theo mode';
COMMENT ON TABLE ods.customer_map IS 'Ánh xạ customer_id (sinh theo từng đơn) -> customer_unique_id (khách thật)';
COMMENT ON COLUMN ods.orders.dq_flags IS 'Danh sách lỗi dữ liệu phát hiện trên đơn (mốc thời gian sai thứ tự, thiếu ngày...)';

-- upgrade for databases created before this rule (idempotent)
ALTER TABLE ods.geolocation_zip ALTER COLUMN latitude DROP NOT NULL;
ALTER TABLE ods.geolocation_zip ALTER COLUMN longitude DROP NOT NULL;

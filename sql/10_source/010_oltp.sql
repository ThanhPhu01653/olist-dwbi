-- setup: required
-- Source system 1: sales OLTP (Kaggle olistbr/brazilian-ecommerce).
-- Column names are kept exactly as in the CSV files, including the misspelt *_lenght columns:
-- that is a trait of the source system and is fixed later in the ODS layer, not here.
-- The source is deliberately "dirty": no cleaning, no NOT NULL on attributes the CSV leaves empty.

CREATE TABLE IF NOT EXISTS oltp.product_category_name_translation (
    product_category_name          text PRIMARY KEY,
    product_category_name_english  text
);

-- NOTE: no FK from products.product_category_name to the translation table.
-- The CSV has categories without a translation (and empty categories), which is a known source defect.
CREATE TABLE IF NOT EXISTS oltp.products (
    product_id                  char(32) PRIMARY KEY,
    product_category_name       text,
    product_name_lenght         integer,
    product_description_lenght  integer,
    product_photos_qty          integer,
    product_weight_g            integer,
    product_length_cm           integer,
    product_height_cm           integer,
    product_width_cm            integer
);

CREATE TABLE IF NOT EXISTS oltp.sellers (
    seller_id              char(32) PRIMARY KEY,
    seller_zip_code_prefix text,
    seller_city            text,
    seller_state           text
);

-- customer_id is generated per order (1 customer_id = 1 order); the real person is customer_unique_id.
CREATE TABLE IF NOT EXISTS oltp.customers (
    customer_id              char(32) PRIMARY KEY,
    customer_unique_id       char(32) NOT NULL,
    customer_zip_code_prefix text,
    customer_city            text,
    customer_state           text
);
CREATE INDEX IF NOT EXISTS ix_customers_unique_id ON oltp.customers (customer_unique_id);

-- No natural key: the same zip prefix appears many times with different coordinates.
-- "id" is a technical key added by the simulation only.
CREATE TABLE IF NOT EXISTS oltp.geolocation (
    id                          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    geolocation_zip_code_prefix text,
    geolocation_lat             double precision,
    geolocation_lng             double precision,
    geolocation_city            text,
    geolocation_state           text
);
CREATE INDEX IF NOT EXISTS ix_geolocation_zip ON oltp.geolocation (geolocation_zip_code_prefix);

CREATE TABLE IF NOT EXISTS oltp.orders (
    order_id                       char(32) PRIMARY KEY,
    customer_id                    char(32) NOT NULL REFERENCES oltp.customers (customer_id),
    order_status                   text     NOT NULL,
    order_purchase_timestamp       timestamp NOT NULL,
    order_approved_at              timestamp,
    order_delivered_carrier_date   timestamp,
    order_delivered_customer_date  timestamp,
    order_estimated_delivery_date  timestamp
);
CREATE INDEX IF NOT EXISTS ix_orders_customer ON oltp.orders (customer_id);
CREATE INDEX IF NOT EXISTS ix_orders_purchase ON oltp.orders (order_purchase_timestamp);

CREATE TABLE IF NOT EXISTS oltp.order_items (
    order_id             char(32) NOT NULL REFERENCES oltp.orders (order_id),
    order_item_id        integer  NOT NULL,
    product_id           char(32) NOT NULL REFERENCES oltp.products (product_id),
    seller_id            char(32) NOT NULL REFERENCES oltp.sellers (seller_id),
    shipping_limit_date  timestamp,
    price                numeric(12,2),
    freight_value        numeric(12,2),
    PRIMARY KEY (order_id, order_item_id)
);
CREATE INDEX IF NOT EXISTS ix_order_items_product ON oltp.order_items (product_id);
CREATE INDEX IF NOT EXISTS ix_order_items_seller  ON oltp.order_items (seller_id);

CREATE TABLE IF NOT EXISTS oltp.order_payments (
    order_id              char(32) NOT NULL REFERENCES oltp.orders (order_id),
    payment_sequential    integer  NOT NULL,
    payment_type          text,
    payment_installments  integer,
    payment_value         numeric(12,2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- review_id alone is NOT unique in the source (the same review_id is attached to several orders),
-- so the key is the pair (review_id, order_id), which is unique in the data.
CREATE TABLE IF NOT EXISTS oltp.order_reviews (
    review_id                char(32) NOT NULL,
    order_id                 char(32) NOT NULL REFERENCES oltp.orders (order_id),
    review_score             smallint,
    review_comment_title     text,
    review_comment_message   text,
    review_creation_date     timestamp,
    review_answer_timestamp  timestamp,
    PRIMARY KEY (review_id, order_id)
);
CREATE INDEX IF NOT EXISTS ix_order_reviews_order ON oltp.order_reviews (order_id);

COMMENT ON SCHEMA oltp IS 'Simulated sales system (Olist Brazilian E-Commerce)';
COMMENT ON TABLE oltp.geolocation IS 'No natural key; id is a technical key added by the simulation';
COMMENT ON TABLE oltp.order_reviews IS 'review_id repeats across orders; PK is (review_id, order_id)';

-- setup: required
-- ODS load procedures: ods.load_<table>(batch_id) clean the staging rows of one batch (staging.load_batch_id = batch_id).
-- Each returns (rows_read, rows_inserted, rows_rejected) through INOUT parameters; the Python runner writes etl_log.job_run.
-- Rows that cannot be loaded (orphans, duplicates, missing required values) go to etl_log.rejected_rows - never silently dropped.
-- Re-running a batch is safe: rejected_rows of that batch+job are replaced, inserts use ON CONFLICT DO NOTHING.

CREATE OR REPLACE FUNCTION ods.clean_zip(z text) RETURNS char(5) LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE WHEN nullif(regexp_replace(coalesce(z, ''), '\D', '', 'g'), '') IS NULL THEN NULL
                ELSE left(lpad(regexp_replace(z, '\D', '', 'g'), 5, '0'), 5) END
$$;

CREATE OR REPLACE FUNCTION ods.clean_city(c text) RETURNS text LANGUAGE sql STABLE AS $$
    SELECT nullif(lower(unaccent(trim(c))), '')
$$;

CREATE OR REPLACE FUNCTION ods.clean_state(s text) RETURNS char(2) LANGUAGE sql IMMUTABLE AS $$
    SELECT nullif(left(upper(trim(s)), 2), '')::char(2)
$$;

-- empty the cleaned tables (reference tables are reloaded from seeds separately)
CREATE OR REPLACE PROCEDURE ods.truncate_data() LANGUAGE plpgsql AS $$
BEGIN
    TRUNCATE ods.category_translation, ods.products, ods.sellers, ods.customers, ods.customer_map, ods.geolocation_zip,
             ods.orders, ods.order_items, ods.order_payments, ods.order_reviews, ods.mql, ods.closed_deals;
END $$;

-- ---------------------------------------------------------------- category translation
CREATE OR REPLACE PROCEDURE ods.load_category_translation(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                          INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_category_translation';
    SELECT count(*) INTO p_read FROM staging.stg_product_category_name_translation WHERE load_batch_id = p_batch_id;
    INSERT INTO ods.category_translation
    SELECT trim(product_category_name), trim(product_category_name_english), p_batch_id
    FROM staging.stg_product_category_name_translation WHERE load_batch_id = p_batch_id
    ON CONFLICT (product_category_name) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- products
CREATE OR REPLACE PROCEDURE ods.load_products(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                              INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_products';
    SELECT count(*) INTO p_read FROM staging.stg_products WHERE load_batch_id = p_batch_id;
    INSERT INTO ods.products
    SELECT product_id, coalesce(nullif(trim(product_category_name), ''), 'unknown'),
           product_name_lenght, product_description_lenght, product_photos_qty,
           product_weight_g, product_length_cm, product_height_cm, product_width_cm,
           (product_weight_g IS NULL OR product_weight_g = 0 OR product_length_cm IS NULL
            OR product_height_cm IS NULL OR product_width_cm IS NULL),
           p_batch_id
    FROM staging.stg_products WHERE load_batch_id = p_batch_id
    ON CONFLICT (product_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- sellers
CREATE OR REPLACE PROCEDURE ods.load_sellers(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                             INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_sellers';
    SELECT count(*) INTO p_read FROM staging.stg_sellers WHERE load_batch_id = p_batch_id;
    INSERT INTO ods.sellers
    SELECT seller_id, ods.clean_zip(seller_zip_code_prefix), ods.clean_city(seller_city), ods.clean_state(seller_state), p_batch_id
    FROM staging.stg_sellers WHERE load_batch_id = p_batch_id
    ON CONFLICT (seller_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- customers (+ customer_map)
CREATE OR REPLACE PROCEDURE ods.load_customers(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                               INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_customers';
    SELECT count(*) INTO p_read FROM staging.stg_customers WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_customers', 'staging.stg_customers', 'missing customer_unique_id',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_customers s WHERE load_batch_id = p_batch_id AND nullif(trim(customer_unique_id), '') IS NULL;
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    INSERT INTO ods.customers
    SELECT customer_id, customer_unique_id, ods.clean_zip(customer_zip_code_prefix), ods.clean_city(customer_city),
           ods.clean_state(customer_state), p_batch_id
    FROM staging.stg_customers WHERE load_batch_id = p_batch_id AND nullif(trim(customer_unique_id), '') IS NOT NULL
    ON CONFLICT (customer_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    INSERT INTO ods.customer_map
    SELECT customer_id, customer_unique_id, p_batch_id FROM ods.customers WHERE etl_batch_id = p_batch_id
    ON CONFLICT (customer_id) DO NOTHING;
END $$;

-- ---------------------------------------------------------------- geolocation -> 1 row per zip
CREATE OR REPLACE PROCEDURE ods.load_geolocation_zip(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                     INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_geolocation_zip';
    SELECT count(*) INTO p_read FROM staging.stg_geolocation WHERE load_batch_id = p_batch_id;
    -- points outside the Brazil bounding box (or without coordinates) are rejected, not aggregated
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_geolocation_zip', 'staging.stg_geolocation', 'coordinates outside Brazil bounding box',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_geolocation s
    WHERE load_batch_id = p_batch_id
      AND NOT (geolocation_lat BETWEEN -33.75 AND 5.27 AND geolocation_lng BETWEEN -73.99 AND -34.79);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    -- recompute every zip touched by this batch from ALL its valid staging points
    -- (MATERIALIZED CTEs: the planner otherwise repeats the semi-join per row and the step never finishes)
    CREATE TEMP TABLE IF NOT EXISTS tmp_geo_zips (z char(5)) ON COMMIT DROP;
    TRUNCATE tmp_geo_zips;
    INSERT INTO tmp_geo_zips SELECT DISTINCT ods.clean_zip(geolocation_zip_code_prefix) FROM staging.stg_geolocation WHERE load_batch_id = p_batch_id;
    DELETE FROM ods.geolocation_zip g USING tmp_geo_zips t WHERE g.zip_code_prefix = t.z;
    INSERT INTO ods.geolocation_zip
    WITH pts AS MATERIALIZED (
        SELECT ods.clean_zip(geolocation_zip_code_prefix) AS z, geolocation_lat AS lat, geolocation_lng AS lng,
               ods.clean_city(geolocation_city) AS city, ods.clean_state(geolocation_state) AS st
        FROM staging.stg_geolocation
        WHERE geolocation_lat BETWEEN -33.75 AND 5.27 AND geolocation_lng BETWEEN -73.99 AND -34.79)
    SELECT p.z, percentile_cont(0.5) WITHIN GROUP (ORDER BY p.lat), percentile_cont(0.5) WITHIN GROUP (ORDER BY p.lng),
           mode() WITHIN GROUP (ORDER BY p.city), mode() WITHIN GROUP (ORDER BY p.st), count(*), p_batch_id
    FROM pts p JOIN tmp_geo_zips t ON t.z = p.z
    GROUP BY p.z;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;      -- number of zip rows written
END $$;

-- ---------------------------------------------------------------- orders
CREATE OR REPLACE PROCEDURE ods.load_orders(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                            INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_orders';
    SELECT count(*) INTO p_read FROM staging.stg_orders WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_orders', 'staging.stg_orders', 'orphan: customer_id not in ods.customers',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_orders s
    WHERE load_batch_id = p_batch_id AND NOT EXISTS (SELECT 1 FROM ods.customers c WHERE c.customer_id = s.customer_id);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    INSERT INTO ods.orders
    SELECT f.order_id, f.customer_id, f.order_status, f.order_purchase_timestamp, f.order_approved_at, f.order_delivered_carrier_date,
           f.order_delivered_customer_date, f.order_estimated_delivery_date, f.flags, cardinality(f.flags), p_batch_id
    FROM (SELECT s.order_id, s.customer_id, lower(trim(s.order_status)) AS order_status, s.order_purchase_timestamp, s.order_approved_at,
                 s.order_delivered_carrier_date, s.order_delivered_customer_date, s.order_estimated_delivery_date,
                 array_remove(ARRAY[
                     CASE WHEN s.order_approved_at < s.order_purchase_timestamp THEN 'approved_before_purchase' END,
                     CASE WHEN s.order_delivered_carrier_date < s.order_purchase_timestamp THEN 'carrier_before_purchase' END,
                     CASE WHEN s.order_delivered_carrier_date < s.order_approved_at THEN 'carrier_before_approved' END,
                     CASE WHEN s.order_delivered_customer_date < s.order_delivered_carrier_date THEN 'delivered_before_carrier' END,
                     CASE WHEN s.order_delivered_customer_date < s.order_purchase_timestamp THEN 'delivered_before_purchase' END,
                     CASE WHEN s.order_estimated_delivery_date < s.order_purchase_timestamp THEN 'estimated_before_purchase' END,
                     CASE WHEN s.order_status = 'delivered' AND s.order_delivered_customer_date IS NULL THEN 'delivered_without_date' END,
                     CASE WHEN s.order_status = 'delivered' AND s.order_delivered_carrier_date IS NULL THEN 'delivered_without_carrier_date' END,
                     CASE WHEN s.order_status = 'delivered' AND s.order_approved_at IS NULL THEN 'delivered_without_approval' END,
                     CASE WHEN s.order_status <> 'delivered' AND s.order_delivered_customer_date IS NOT NULL THEN 'delivery_date_but_not_delivered' END
                 ], NULL) AS flags
          FROM staging.stg_orders s
          WHERE s.load_batch_id = p_batch_id AND EXISTS (SELECT 1 FROM ods.customers c WHERE c.customer_id = s.customer_id)) f
    ON CONFLICT (order_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

-- ---------------------------------------------------------------- order items
CREATE OR REPLACE PROCEDURE ods.load_order_items(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                 INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_order_items';
    SELECT count(*) INTO p_read FROM staging.stg_order_items WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_order_items', 'staging.stg_order_items',
           CASE WHEN o.order_id IS NULL THEN 'orphan: order_id not in ods.orders'
                WHEN p.product_id IS NULL THEN 'orphan: product_id not in ods.products'
                ELSE 'orphan: seller_id not in ods.sellers' END,
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_order_items s
    LEFT JOIN ods.orders o ON o.order_id = s.order_id
    LEFT JOIN ods.products p ON p.product_id = s.product_id
    LEFT JOIN ods.sellers l ON l.seller_id = s.seller_id
    WHERE s.load_batch_id = p_batch_id AND (o.order_id IS NULL OR p.product_id IS NULL OR l.seller_id IS NULL);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    INSERT INTO ods.order_items
    SELECT s.order_id, s.order_item_id, s.product_id, s.seller_id, s.shipping_limit_date, s.price, s.freight_value, p_batch_id
    FROM staging.stg_order_items s
    JOIN ods.orders o ON o.order_id = s.order_id
    JOIN ods.products p ON p.product_id = s.product_id
    JOIN ods.sellers l ON l.seller_id = s.seller_id
    WHERE s.load_batch_id = p_batch_id
    ON CONFLICT (order_id, order_item_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

-- ---------------------------------------------------------------- order payments
CREATE OR REPLACE PROCEDURE ods.load_order_payments(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                    INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_order_payments';
    SELECT count(*) INTO p_read FROM staging.stg_order_payments WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_order_payments', 'staging.stg_order_payments', 'orphan: order_id not in ods.orders',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_order_payments s
    WHERE load_batch_id = p_batch_id AND NOT EXISTS (SELECT 1 FROM ods.orders o WHERE o.order_id = s.order_id);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    INSERT INTO ods.order_payments
    SELECT s.order_id, s.payment_sequential, lower(trim(s.payment_type)), greatest(coalesce(s.payment_installments, 1), 1), s.payment_value,
           array_remove(ARRAY[
               CASE WHEN coalesce(s.payment_installments, 0) = 0 THEN 'installments_zero_set_to_1' END,
               CASE WHEN lower(trim(s.payment_type)) = 'not_defined' THEN 'payment_type_not_defined' END,
               CASE WHEN s.payment_value = 0 THEN 'payment_value_zero' END], NULL),
           p_batch_id
    FROM staging.stg_order_payments s
    WHERE s.load_batch_id = p_batch_id AND EXISTS (SELECT 1 FROM ods.orders o WHERE o.order_id = s.order_id)
    ON CONFLICT (order_id, payment_sequential) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

-- ---------------------------------------------------------------- order reviews (dedupe on (review_id, order_id))
CREATE OR REPLACE PROCEDURE ods.load_order_reviews(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                   INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v_dup bigint;
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_order_reviews';
    SELECT count(*) INTO p_read FROM staging.stg_order_reviews WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_order_reviews', 'staging.stg_order_reviews', 'orphan: order_id not in ods.orders',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_order_reviews s
    WHERE load_batch_id = p_batch_id AND NOT EXISTS (SELECT 1 FROM ods.orders o WHERE o.order_id = s.order_id);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    -- keep the row with the latest answer timestamp for each (review_id, order_id); log the others
    CREATE TEMP TABLE IF NOT EXISTS tmp_rev ON COMMIT DROP AS SELECT * FROM staging.stg_order_reviews WHERE false;
    TRUNCATE tmp_rev;
    ALTER TABLE tmp_rev ADD COLUMN IF NOT EXISTS rn integer;
    INSERT INTO tmp_rev
    SELECT s.*, row_number() OVER (PARTITION BY s.review_id, s.order_id
                                   ORDER BY s.review_answer_timestamp DESC NULLS LAST, s.review_creation_date DESC NULLS LAST)
    FROM staging.stg_order_reviews s
    WHERE s.load_batch_id = p_batch_id AND EXISTS (SELECT 1 FROM ods.orders o WHERE o.order_id = s.order_id);
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_order_reviews', 'staging.stg_order_reviews', 'duplicate (review_id, order_id)',
           to_jsonb(t) - 'load_batch_id' - 'loaded_at' - 'rn'
    FROM tmp_rev t WHERE rn > 1;
    GET DIAGNOSTICS v_dup = ROW_COUNT;
    p_rejected := p_rejected + v_dup;
    INSERT INTO ods.order_reviews
    SELECT review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date,
           review_answer_timestamp, p_batch_id
    FROM tmp_rev WHERE rn = 1
    ON CONFLICT (review_id, order_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

-- ---------------------------------------------------------------- MQL
CREATE OR REPLACE PROCEDURE ods.load_mql(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                         INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_mql';
    SELECT count(*) INTO p_read FROM staging.stg_mql WHERE load_batch_id = p_batch_id;
    INSERT INTO ods.mql
    SELECT mql_id, first_contact_date, landing_page_id, coalesce(nullif(lower(trim(origin)), ''), 'unknown'), p_batch_id
    FROM staging.stg_mql WHERE load_batch_id = p_batch_id
    ON CONFLICT (mql_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- closed deals
CREATE OR REPLACE PROCEDURE ods.load_closed_deals(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                  INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_closed_deals';
    SELECT count(*) INTO p_read FROM staging.stg_closed_deals WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_closed_deals', 'staging.stg_closed_deals', 'orphan: mql_id not in ods.mql',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_closed_deals s
    WHERE load_batch_id = p_batch_id AND NOT EXISTS (SELECT 1 FROM ods.mql m WHERE m.mql_id = s.mql_id);
    GET DIAGNOSTICS p_rejected = ROW_COUNT;
    INSERT INTO ods.closed_deals
    SELECT s.mql_id, s.seller_id, s.sdr_id, s.sr_id, s.won_date,
           coalesce(nullif(trim(s.business_segment), ''), 'unknown'), coalesce(nullif(trim(s.lead_type), ''), 'unknown'),
           coalesce(nullif(trim(s.lead_behaviour_profile), ''), 'unknown'), coalesce(nullif(trim(s.business_type), ''), 'unknown'),
           coalesce(s.has_company::text, 'unknown'), coalesce(s.has_gtin::text, 'unknown'), coalesce(nullif(trim(s.average_stock), ''), 'unknown'),
           s.declared_product_catalog_size, s.declared_monthly_revenue,
           array_remove(ARRAY[
               CASE WHEN s.declared_monthly_revenue = 0 THEN 'declared_revenue_zero' END,
               CASE WHEN s.declared_product_catalog_size = 0 THEN 'declared_catalog_zero' END,
               CASE WHEN s.won_date::date < m.first_contact_date THEN 'won_before_first_contact' END], NULL),
           p_batch_id
    FROM staging.stg_closed_deals s JOIN ods.mql m ON m.mql_id = s.mql_id
    WHERE s.load_batch_id = p_batch_id
    ON CONFLICT (mql_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

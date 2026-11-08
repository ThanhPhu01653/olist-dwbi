-- setup: required
-- Dimension load procedures dw.load_dim_<name>(batch_id) -> INOUT (rows_read, rows_inserted, rows_updated, rows_rejected).
-- All are idempotent: they rebuild the desired state from ODS and only insert / update what differs.
-- dim_date is built by etl/build_dim_date.py (calendar + Brazilian holidays from the Python 'holidays' package).

-- ---------------------------------------------------------------- dim_geography (union of zips of geolocation, customers, sellers)
CREATE OR REPLACE PROCEDURE dw.load_dim_geography(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                  INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE tmp_geo ON COMMIT DROP AS
    WITH other AS (
        SELECT zip, mode() WITHIN GROUP (ORDER BY city) AS city, mode() WITHIN GROUP (ORDER BY st) AS st
        FROM (SELECT zip_code_prefix AS zip, city, state_code AS st FROM ods.customers
              UNION ALL SELECT zip_code_prefix, city, state_code FROM ods.sellers) u
        WHERE zip IS NOT NULL GROUP BY zip)
    SELECT coalesce(g.zip_code_prefix, o.zip) AS zip, coalesce(g.city, o.city) AS city, coalesce(g.state_code, o.st) AS st,
           g.latitude, g.longitude
    FROM ods.geolocation_zip g FULL JOIN other o ON o.zip = g.zip_code_prefix;
    SELECT count(*) INTO p_read FROM tmp_geo;
    WITH up AS (
        INSERT INTO dw.dim_geography (zip_code_prefix, city, state_code, state_name, region, latitude, longitude)
        SELECT t.zip, t.city, t.st, coalesce(r.state_name, 'Unknown'), coalesce(r.region, 'Unknown'), t.latitude, t.longitude
        FROM tmp_geo t LEFT JOIN ods.ref_state_region r ON r.state_code = t.st
        ORDER BY t.zip                                   -- fixed order => the same surrogate keys on every rebuild
        ON CONFLICT (zip_code_prefix) DO UPDATE
            SET city = EXCLUDED.city, state_code = EXCLUDED.state_code, state_name = EXCLUDED.state_name, region = EXCLUDED.region,
                latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude, dw_updated_at = now()
            WHERE (dw.dim_geography.city, dw.dim_geography.state_code, dw.dim_geography.state_name, dw.dim_geography.region,
                   dw.dim_geography.latitude, dw.dim_geography.longitude)
                  IS DISTINCT FROM (EXCLUDED.city, EXCLUDED.state_code, EXCLUDED.state_name, EXCLUDED.region, EXCLUDED.latitude, EXCLUDED.longitude)
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- dim_customer, SCD type 2 on the zip of the customer
-- Versions are derived from the order history of each customer_unique_id: a new version opens when the zip differs from
-- the previous order (effective_from = purchase date of that order; first version starts at 1900-01-01).
-- Re-running recomputes the versions of the customers touched by the batch; existing versions are matched on
-- (customer_unique_id, effective_from), so surrogate keys already used by facts never change.
CREATE OR REPLACE PROCEDURE dw.load_dim_customer(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                 INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(DISTINCT customer_unique_id) INTO p_read FROM ods.customers WHERE etl_batch_id = p_batch_id;
    CREATE TEMP TABLE tmp_cust_ver ON COMMIT DROP AS
    WITH aff AS (SELECT DISTINCT customer_unique_id AS uid FROM ods.customers WHERE etl_batch_id = p_batch_id),
    ev AS (
        SELECT c.customer_unique_id AS uid, c.zip_code_prefix AS zip, c.city, c.state_code AS st, o.order_purchase_timestamp AS ts, o.order_id
        FROM ods.customers c JOIN aff ON aff.uid = c.customer_unique_id LEFT JOIN ods.orders o ON o.customer_id = c.customer_id),
    ord AS (
        SELECT ev.*, lag(zip) OVER w AS pz, row_number() OVER w AS rn
        FROM ev WINDOW w AS (PARTITION BY uid ORDER BY ts NULLS FIRST, order_id)),
    chg AS (   -- opening events; if several open on the same day keep the last one
        SELECT ord.*, row_number() OVER (PARTITION BY uid, coalesce(ts::date, DATE '1900-01-01') ORDER BY rn DESC) AS dup
        FROM ord WHERE rn = 1 OR zip IS DISTINCT FROM pz),
    stt AS (SELECT uid, zip, city, st, ts::date AS d, rn FROM chg WHERE dup = 1),
    ver AS (
        SELECT uid, zip, city, st, row_number() OVER w AS vn,
               CASE WHEN row_number() OVER w = 1 THEN DATE '1900-01-01' ELSE d END AS eff_from, lead(d) OVER w AS nxt
        FROM stt WINDOW w AS (PARTITION BY uid ORDER BY rn))
    SELECT uid, zip, city, st, vn, eff_from, coalesce(nxt - 1, DATE '9999-12-31') AS eff_to, (nxt IS NULL) AS is_cur FROM ver;

    INSERT INTO dw.dim_customer (customer_unique_id, zip_code_prefix, city, state_code, geography_key, effective_from, effective_to, is_current, version_no)
    SELECT v.uid, v.zip, v.city, v.st, coalesce(g.geography_key, -1), v.eff_from, v.eff_to, v.is_cur, v.vn
    FROM tmp_cust_ver v LEFT JOIN dw.dim_geography g ON g.zip_code_prefix = v.zip
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_customer d WHERE d.customer_unique_id = v.uid AND d.effective_from = v.eff_from)
    ORDER BY v.uid, v.eff_from;                          -- fixed order => the same surrogate keys on every rebuild
    GET DIAGNOSTICS p_inserted = ROW_COUNT;

    UPDATE dw.dim_customer d
    SET effective_to = v.eff_to, is_current = v.is_cur, version_no = v.vn, dw_updated_at = now()
    FROM tmp_cust_ver v
    WHERE d.customer_unique_id = v.uid AND d.effective_from = v.eff_from
      AND (d.effective_to, d.is_current, d.version_no) IS DISTINCT FROM (v.eff_to, v.is_cur, v.vn);
    GET DIAGNOSTICS p_updated = ROW_COUNT;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- dim_seller, SCD type 1, conformed (sales + CRM)
-- Sellers that exist only in closed_deals still get a row (unknown address, is_from_funnel = true).
-- first_sale_date is filled later by the fact load (P4) and is never overwritten here.
CREATE OR REPLACE PROCEDURE dw.load_dim_seller(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                               INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE tmp_seller ON COMMIT DROP AS
    SELECT s.seller_id, s.zip_code_prefix AS zip, s.city, s.state_code AS st FROM ods.sellers s
    UNION ALL
    SELECT d.seller_id, NULL, NULL, NULL FROM ods.closed_deals d WHERE NOT EXISTS (SELECT 1 FROM ods.sellers s WHERE s.seller_id = d.seller_id);
    SELECT count(*) INTO p_read FROM tmp_seller;
    WITH up AS (
        INSERT INTO dw.dim_seller (seller_id, zip_code_prefix, city, state_code, geography_key, is_from_funnel, mql_id, acquisition_origin,
                                   acquisition_channel, business_segment, lead_type, business_type, won_date)
        SELECT t.seller_id, t.zip, coalesce(t.city, 'unknown'), t.st, coalesce(g.geography_key, -1), d.mql_id IS NOT NULL, d.mql_id,
               coalesce(m.origin, 'not_from_funnel'),
               CASE WHEN d.mql_id IS NULL THEN 'Not from funnel' ELSE coalesce(og.channel_group, 'Unknown') END,
               d.business_segment, d.lead_type, d.business_type, d.won_date::date
        FROM tmp_seller t
        LEFT JOIN dw.dim_geography g ON g.zip_code_prefix = t.zip
        LEFT JOIN ods.closed_deals d ON d.seller_id = t.seller_id
        LEFT JOIN ods.mql m ON m.mql_id = d.mql_id
        LEFT JOIN ods.ref_lead_origin_group og ON og.origin = m.origin
        ORDER BY t.seller_id                             -- fixed order => the same surrogate keys on every rebuild
        ON CONFLICT (seller_id) DO UPDATE
            SET zip_code_prefix = EXCLUDED.zip_code_prefix, city = EXCLUDED.city, state_code = EXCLUDED.state_code,
                geography_key = EXCLUDED.geography_key, is_from_funnel = EXCLUDED.is_from_funnel, mql_id = EXCLUDED.mql_id,
                acquisition_origin = EXCLUDED.acquisition_origin, acquisition_channel = EXCLUDED.acquisition_channel,
                business_segment = EXCLUDED.business_segment, lead_type = EXCLUDED.lead_type, business_type = EXCLUDED.business_type,
                won_date = EXCLUDED.won_date, dw_updated_at = now()
            WHERE (dw.dim_seller.zip_code_prefix, dw.dim_seller.city, dw.dim_seller.state_code, dw.dim_seller.geography_key, dw.dim_seller.is_from_funnel,
                   dw.dim_seller.mql_id, dw.dim_seller.acquisition_origin, dw.dim_seller.acquisition_channel, dw.dim_seller.business_segment,
                   dw.dim_seller.lead_type, dw.dim_seller.business_type, dw.dim_seller.won_date)
                  IS DISTINCT FROM (EXCLUDED.zip_code_prefix, EXCLUDED.city, EXCLUDED.state_code, EXCLUDED.geography_key, EXCLUDED.is_from_funnel,
                                    EXCLUDED.mql_id, EXCLUDED.acquisition_origin, EXCLUDED.acquisition_channel, EXCLUDED.business_segment,
                                    EXCLUDED.lead_type, EXCLUDED.business_type, EXCLUDED.won_date)
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- dim_product
CREATE OR REPLACE PROCEDURE dw.load_dim_product(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.products;
    WITH up AS (
        INSERT INTO dw.dim_product (product_id, category_name_pt, category_name_en, category_group, weight_g, length_cm, height_cm, width_cm,
                                    volume_cm3, size_class, photos_qty, name_length, description_length)
        SELECT p.product_id, p.product_category_name,
               coalesce(t.product_category_name_english, x.product_category_name_english, p.product_category_name),
               coalesce(gr.category_group, 'Unknown'), p.weight_g, p.length_cm, p.height_cm, p.width_cm,
               CASE WHEN p.length_cm IS NULL OR p.height_cm IS NULL OR p.width_cm IS NULL THEN NULL
                    ELSE p.length_cm::bigint * p.height_cm * p.width_cm END,
               CASE WHEN p.weight_g IS NULL OR p.weight_g = 0 THEN 'Unknown' WHEN p.weight_g < 500 THEN 'S' WHEN p.weight_g < 2000 THEN 'M'
                    WHEN p.weight_g < 10000 THEN 'L' ELSE 'XL' END,
               p.photos_qty, p.name_length, p.description_length
        FROM ods.products p
        LEFT JOIN ods.category_translation t ON t.product_category_name = p.product_category_name
        LEFT JOIN ods.ref_category_translation_extra x ON x.product_category_name = p.product_category_name
        LEFT JOIN ods.ref_category_group gr ON gr.product_category_name = p.product_category_name
        ORDER BY p.product_id                            -- fixed order => the same surrogate keys on every rebuild
        ON CONFLICT (product_id) DO UPDATE
            SET category_name_pt = EXCLUDED.category_name_pt, category_name_en = EXCLUDED.category_name_en, category_group = EXCLUDED.category_group,
                weight_g = EXCLUDED.weight_g, length_cm = EXCLUDED.length_cm, height_cm = EXCLUDED.height_cm, width_cm = EXCLUDED.width_cm,
                volume_cm3 = EXCLUDED.volume_cm3, size_class = EXCLUDED.size_class, photos_qty = EXCLUDED.photos_qty,
                name_length = EXCLUDED.name_length, description_length = EXCLUDED.description_length, dw_updated_at = now()
            WHERE (dw.dim_product.category_name_pt, dw.dim_product.category_name_en, dw.dim_product.category_group, dw.dim_product.weight_g,
                   dw.dim_product.length_cm, dw.dim_product.height_cm, dw.dim_product.width_cm, dw.dim_product.size_class)
                  IS DISTINCT FROM (EXCLUDED.category_name_pt, EXCLUDED.category_name_en, EXCLUDED.category_group, EXCLUDED.weight_g,
                                    EXCLUDED.length_cm, EXCLUDED.height_cm, EXCLUDED.width_cm, EXCLUDED.size_class)
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- small reference-based dimensions
CREATE OR REPLACE PROCEDURE dw.load_dim_order_status(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                     INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.ref_order_status;
    WITH up AS (
        INSERT INTO dw.dim_order_status (order_status, status_group, is_final)
        SELECT order_status, status_group, is_final FROM ods.ref_order_status ORDER BY order_status
        ON CONFLICT (order_status) DO UPDATE SET status_group = EXCLUDED.status_group, is_final = EXCLUDED.is_final, dw_updated_at = now()
            WHERE (dw.dim_order_status.status_group, dw.dim_order_status.is_final) IS DISTINCT FROM (EXCLUDED.status_group, EXCLUDED.is_final)
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE dw.load_dim_payment_type(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                     INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.ref_payment_type;
    WITH up AS (
        INSERT INTO dw.dim_payment_type (payment_type, payment_group, display_name)
        SELECT payment_type, payment_group, display_name FROM ods.ref_payment_type ORDER BY payment_type
        ON CONFLICT (payment_type) DO UPDATE SET payment_group = EXCLUDED.payment_group, display_name = EXCLUDED.display_name, dw_updated_at = now()
            WHERE (dw.dim_payment_type.payment_group, dw.dim_payment_type.display_name) IS DISTINCT FROM (EXCLUDED.payment_group, EXCLUDED.display_name)
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE dw.load_dim_lead_origin(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                    INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.ref_lead_origin_group;
    WITH up AS (
        INSERT INTO dw.dim_lead_origin (origin, channel_group)
        SELECT origin, channel_group FROM ods.ref_lead_origin_group ORDER BY origin
        ON CONFLICT (origin) DO UPDATE SET channel_group = EXCLUDED.channel_group, dw_updated_at = now()
            WHERE dw.dim_lead_origin.channel_group IS DISTINCT FROM EXCLUDED.channel_group
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- junk dimension of deal attributes, sales reps
CREATE OR REPLACE PROCEDURE dw.load_dim_lead_profile(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                     INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.closed_deals;
    INSERT INTO dw.dim_lead_profile (business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock)
    SELECT DISTINCT business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock FROM ods.closed_deals
    ORDER BY business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock
    ON CONFLICT (business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_updated := 0;
    p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE dw.load_dim_sales_rep(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                  INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(*) INTO p_read FROM ods.closed_deals;
    INSERT INTO dw.dim_sales_rep (rep_id, rep_role)
    SELECT rep_id, rep_role FROM (
        SELECT sdr_id AS rep_id, 'SDR' AS rep_role FROM ods.closed_deals WHERE sdr_id IS NOT NULL
        UNION SELECT sr_id, 'SR' FROM ods.closed_deals WHERE sr_id IS NOT NULL) r
    ORDER BY rep_role, rep_id                            -- fixed order => the same surrogate keys on every rebuild
    ON CONFLICT (rep_id, rep_role) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
    p_updated := 0;
    p_rejected := 0;
END $$;

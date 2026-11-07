-- setup: required
-- Fact load procedures dw.load_fact_<name>(batch_id) -> INOUT (rows_read, rows_inserted, rows_updated, rows_rejected).
-- Order of execution (etl/load_dw.py): fact_order_item -> fact_payment -> fact_order_fulfillment -> fact_review
--   -> dim_seller.first_sale_date -> fact_lead_funnel -> fact_seller_monthly.
-- All are idempotent UPSERTs (a row is only rewritten when a column other than etl_batch_id changed). Scope of one run:
--   order-level facts take the ODS rows loaded by the batch (full mode: everything), lead funnel and seller monthly are
--   small and are recomputed completely each time (their values depend on facts that may arrive in later batches).
-- No FK is ever NULL: a failed lookup becomes the Unknown member (-1) and is counted in etl_log.fact_load_issue;
-- a negative time interval (source error) becomes NULL and is counted there too.

-- date -> yyyymmdd key, -1 when the value is NULL or outside the range of dim_date (2016-01-01 .. 2020-12-31)
CREATE OR REPLACE FUNCTION dw.date_key(ts timestamp) RETURNS int LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE WHEN ts IS NULL OR ts::date NOT BETWEEN DATE '2016-01-01' AND DATE '2020-12-31' THEN -1
                ELSE to_char(ts, 'YYYYMMDD')::int END $$;

CREATE OR REPLACE PROCEDURE dw.log_fact_issue(p_batch_id bigint, p_fact text, p_type text, p_detail text, p_rows bigint)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_rows > 0 THEN
        INSERT INTO etl_log.fact_load_issue (batch_id, fact_table, issue_type, detail, row_count) VALUES (p_batch_id, p_fact, p_type, p_detail, p_rows);
    END IF;
END $$;

-- ---------------------------------------------------------------- fact_order_item (transaction)
CREATE OR REPLACE PROCEDURE dw.load_fact_order_item(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                    INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v record;
BEGIN
    DELETE FROM etl_log.fact_load_issue WHERE batch_id = p_batch_id AND fact_table = 'fact_order_item';   -- re-running a batch must not double-count
    CREATE TEMP TABLE tmp_foi ON COMMIT DROP AS
    SELECT i.order_id, i.order_item_id,
           dw.date_key(o.order_purchase_timestamp) AS purchase_date_key,
           dw.date_key(i.shipping_limit_date) AS shipping_limit_date_key, (i.shipping_limit_date IS NOT NULL) AS has_ship,
           coalesce(dc.customer_key, -1) AS customer_key, coalesce(dc.geography_key, -1) AS customer_geography_key,
           coalesce(s.geography_key, -1) AS seller_geography_key, coalesce(s.seller_key, -1) AS seller_key,
           coalesce(p.product_key, -1) AS product_key, coalesce(os.order_status_key, -1) AS order_status_key,
           i.price, i.freight_value, i.price + i.freight_value AS item_total
    FROM ods.order_items i
    JOIN ods.orders o ON o.order_id = i.order_id
    JOIN ods.customers c ON c.customer_id = o.customer_id
    LEFT JOIN dw.dim_customer dc ON dc.customer_unique_id = c.customer_unique_id
                                 AND o.order_purchase_timestamp::date BETWEEN dc.effective_from AND dc.effective_to
    LEFT JOIN dw.dim_seller s ON s.seller_id = i.seller_id
    LEFT JOIN dw.dim_product p ON p.product_id = i.product_id
    LEFT JOIN dw.dim_order_status os ON os.order_status = o.order_status
    WHERE i.etl_batch_id = p_batch_id;
    SELECT count(*) INTO p_read FROM tmp_foi;

    WITH up AS (
        INSERT INTO dw.fact_order_item AS t (order_id, order_item_id, purchase_date_key, shipping_limit_date_key, customer_key, customer_geography_key,
               seller_geography_key, seller_key, product_key, order_status_key, price, freight_value, item_total, etl_batch_id)
        SELECT order_id, order_item_id, purchase_date_key, shipping_limit_date_key, customer_key, customer_geography_key,
               seller_geography_key, seller_key, product_key, order_status_key, price, freight_value, item_total, p_batch_id FROM tmp_foi
        ON CONFLICT (order_id, order_item_id) DO UPDATE
            SET purchase_date_key = EXCLUDED.purchase_date_key, shipping_limit_date_key = EXCLUDED.shipping_limit_date_key,
                customer_key = EXCLUDED.customer_key, customer_geography_key = EXCLUDED.customer_geography_key,
                seller_geography_key = EXCLUDED.seller_geography_key, seller_key = EXCLUDED.seller_key, product_key = EXCLUDED.product_key,
                order_status_key = EXCLUDED.order_status_key, price = EXCLUDED.price, freight_value = EXCLUDED.freight_value,
                item_total = EXCLUDED.item_total, etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;

    SELECT count(*) FILTER (WHERE customer_key = -1) AS customer, count(*) FILTER (WHERE customer_geography_key = -1) AS cust_geo,
           count(*) FILTER (WHERE seller_geography_key = -1) AS seller_geo, count(*) FILTER (WHERE seller_key = -1) AS seller,
           count(*) FILTER (WHERE product_key = -1) AS product, count(*) FILTER (WHERE order_status_key = -1) AS status,
           count(*) FILTER (WHERE purchase_date_key = -1) AS purchase_date, count(*) FILTER (WHERE has_ship AND shipping_limit_date_key = -1) AS ship_date
    INTO v FROM tmp_foi;
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'customer_key', v.customer);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'customer_geography_key', v.cust_geo);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'seller_geography_key', v.seller_geo);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'seller_key', v.seller);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'product_key', v.product);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'order_status_key', v.status);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'purchase_date_key', v.purchase_date);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_item', 'unknown_member', 'shipping_limit_date_key', v.ship_date);
END $$;

-- ---------------------------------------------------------------- fact_payment (transaction)
CREATE OR REPLACE PROCEDURE dw.load_fact_payment(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                 INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v record;
BEGIN
    DELETE FROM etl_log.fact_load_issue WHERE batch_id = p_batch_id AND fact_table = 'fact_payment';   -- re-running a batch must not double-count
    CREATE TEMP TABLE tmp_fpay ON COMMIT DROP AS
    SELECT p.order_id, p.payment_sequential, dw.date_key(o.order_purchase_timestamp) AS purchase_date_key,
           coalesce(dc.customer_key, -1) AS customer_key, coalesce(pt.payment_type_key, -1) AS payment_type_key,
           p.payment_installments, p.payment_value
    FROM ods.order_payments p
    JOIN ods.orders o ON o.order_id = p.order_id
    JOIN ods.customers c ON c.customer_id = o.customer_id
    LEFT JOIN dw.dim_customer dc ON dc.customer_unique_id = c.customer_unique_id
                                 AND o.order_purchase_timestamp::date BETWEEN dc.effective_from AND dc.effective_to
    LEFT JOIN dw.dim_payment_type pt ON pt.payment_type = p.payment_type
    WHERE p.etl_batch_id = p_batch_id;
    SELECT count(*) INTO p_read FROM tmp_fpay;

    WITH up AS (
        INSERT INTO dw.fact_payment AS t (order_id, payment_sequential, purchase_date_key, customer_key, payment_type_key, payment_installments,
                                          payment_value, etl_batch_id)
        SELECT order_id, payment_sequential, purchase_date_key, customer_key, payment_type_key, payment_installments, payment_value, p_batch_id
        FROM tmp_fpay
        ON CONFLICT (order_id, payment_sequential) DO UPDATE
            SET purchase_date_key = EXCLUDED.purchase_date_key, customer_key = EXCLUDED.customer_key, payment_type_key = EXCLUDED.payment_type_key,
                payment_installments = EXCLUDED.payment_installments, payment_value = EXCLUDED.payment_value, etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;

    SELECT count(*) FILTER (WHERE customer_key = -1) AS customer, count(*) FILTER (WHERE payment_type_key = -1) AS ptype,
           count(*) FILTER (WHERE purchase_date_key = -1) AS pdate INTO v FROM tmp_fpay;
    CALL dw.log_fact_issue(p_batch_id, 'fact_payment', 'unknown_member', 'customer_key', v.customer);
    CALL dw.log_fact_issue(p_batch_id, 'fact_payment', 'unknown_member', 'payment_type_key', v.ptype);
    CALL dw.log_fact_issue(p_batch_id, 'fact_payment', 'unknown_member', 'purchase_date_key', v.pdate);
END $$;

-- ---------------------------------------------------------------- fact_order_fulfillment (accumulating snapshot, UPSERT by order_id)
-- Orders in scope = orders loaded by the batch + orders that received items / payments in the batch.
-- Intervals are computed from the original timestamps; a negative value (source error) is stored as NULL, counted in
-- etl_log.fact_load_issue and added to dq_flag_count (on top of the flags ODS already set on the order).
CREATE OR REPLACE PROCEDURE dw.load_fact_order_fulfillment(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                           INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v record;
BEGIN
    DELETE FROM etl_log.fact_load_issue WHERE batch_id = p_batch_id AND fact_table = 'fact_order_fulfillment';   -- re-running a batch must not double-count
    CREATE TEMP TABLE tmp_fof_scope ON COMMIT DROP AS
    SELECT order_id FROM ods.orders WHERE etl_batch_id = p_batch_id
    UNION SELECT order_id FROM ods.order_items WHERE etl_batch_id = p_batch_id
    UNION SELECT order_id FROM ods.order_payments WHERE etl_batch_id = p_batch_id;
    CREATE UNIQUE INDEX ON tmp_fof_scope (order_id);

    CREATE TEMP TABLE tmp_fof ON COMMIT DROP AS
    WITH it AS (
        SELECT i.order_id, count(*) AS item_count, count(DISTINCT i.seller_id) AS seller_count, sum(i.price) AS order_value, sum(i.freight_value) AS freight_total
        FROM ods.order_items i JOIN tmp_fof_scope sc ON sc.order_id = i.order_id GROUP BY i.order_id),
    pm AS (
        SELECT p.order_id, sum(p.payment_value) AS payment_total
        FROM ods.order_payments p JOIN tmp_fof_scope sc ON sc.order_id = p.order_id GROUP BY p.order_id),
    base AS (
        SELECT o.order_id, o.order_status, o.dq_flag_count AS ods_flags,
               o.order_purchase_timestamp AS purchase_ts, o.order_approved_at AS approved_ts, o.order_delivered_carrier_date AS carrier_ts,
               o.order_delivered_customer_date AS delivered_ts, o.order_estimated_delivery_date AS estimated_ts,
               coalesce(dc.customer_key, -1) AS customer_key, coalesce(dc.geography_key, -1) AS customer_geography_key,
               coalesce(os.order_status_key, -1) AS order_status_key,
               extract(epoch FROM o.order_approved_at - o.order_purchase_timestamp) / 3600.0 AS approval_raw,
               extract(epoch FROM o.order_delivered_carrier_date - o.order_approved_at) / 86400.0 AS handling_raw,
               extract(epoch FROM o.order_delivered_customer_date - o.order_delivered_carrier_date) / 86400.0 AS transit_raw,
               extract(epoch FROM o.order_delivered_customer_date - o.order_purchase_timestamp) / 86400.0 AS lead_raw,
               o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date AS delay_days,
               o.order_estimated_delivery_date::date - o.order_purchase_timestamp::date AS promised_raw,
               coalesce(it.item_count, 0) AS item_count, coalesce(it.seller_count, 0) AS seller_count,
               coalesce(it.order_value, 0) AS order_value, coalesce(it.freight_total, 0) AS freight_total, coalesce(pm.payment_total, 0) AS payment_total
        FROM tmp_fof_scope sc
        JOIN ods.orders o ON o.order_id = sc.order_id
        JOIN ods.customers c ON c.customer_id = o.customer_id
        LEFT JOIN dw.dim_customer dc ON dc.customer_unique_id = c.customer_unique_id
                                     AND o.order_purchase_timestamp::date BETWEEN dc.effective_from AND dc.effective_to
        LEFT JOIN dw.dim_order_status os ON os.order_status = o.order_status
        LEFT JOIN it ON it.order_id = o.order_id
        LEFT JOIN pm ON pm.order_id = o.order_id)
    SELECT b.*,
           (b.order_status = 'delivered' AND b.delivered_ts IS NOT NULL)::int AS is_delivered,
           coalesce((b.approval_raw < 0)::int, 0) + coalesce((b.handling_raw < 0)::int, 0) + coalesce((b.transit_raw < 0)::int, 0)
           + coalesce((b.lead_raw < 0)::int, 0) + coalesce((b.promised_raw < 0)::int, 0) AS neg_count
    FROM base b;
    SELECT count(*) INTO p_read FROM tmp_fof;

    WITH up AS (
        INSERT INTO dw.fact_order_fulfillment AS t
        SELECT order_id, customer_key, customer_geography_key, order_status_key,
               dw.date_key(purchase_ts), dw.date_key(approved_ts), dw.date_key(carrier_ts), dw.date_key(delivered_ts), dw.date_key(estimated_ts),
               purchase_ts, approved_ts, carrier_ts, delivered_ts, estimated_ts,
               CASE WHEN approval_raw >= 0 THEN round(approval_raw::numeric, 2) END, CASE WHEN handling_raw >= 0 THEN round(handling_raw::numeric, 2) END,
               CASE WHEN transit_raw >= 0 THEN round(transit_raw::numeric, 2) END, CASE WHEN lead_raw >= 0 THEN round(lead_raw::numeric, 2) END,
               delay_days, CASE WHEN promised_raw >= 0 THEN promised_raw END,
               is_delivered, coalesce((is_delivered = 1 AND delay_days > 0)::int, 0), (order_status = 'canceled')::int,
               item_count, seller_count, order_value, freight_total, payment_total,
               ods_flags + neg_count, p_batch_id
        FROM tmp_fof
        ON CONFLICT (order_id) DO UPDATE
            SET customer_key = EXCLUDED.customer_key, customer_geography_key = EXCLUDED.customer_geography_key, order_status_key = EXCLUDED.order_status_key,
                purchase_date_key = EXCLUDED.purchase_date_key, approved_date_key = EXCLUDED.approved_date_key, carrier_date_key = EXCLUDED.carrier_date_key,
                delivered_date_key = EXCLUDED.delivered_date_key, estimated_date_key = EXCLUDED.estimated_date_key,
                purchase_ts = EXCLUDED.purchase_ts, approved_ts = EXCLUDED.approved_ts, carrier_ts = EXCLUDED.carrier_ts,
                delivered_ts = EXCLUDED.delivered_ts, estimated_ts = EXCLUDED.estimated_ts,
                approval_hours = EXCLUDED.approval_hours, handling_days = EXCLUDED.handling_days, transit_days = EXCLUDED.transit_days,
                lead_days = EXCLUDED.lead_days, delay_days = EXCLUDED.delay_days, promised_days = EXCLUDED.promised_days,
                is_delivered = EXCLUDED.is_delivered, is_late = EXCLUDED.is_late, is_canceled = EXCLUDED.is_canceled,
                item_count = EXCLUDED.item_count, seller_count = EXCLUDED.seller_count, order_value = EXCLUDED.order_value,
                freight_total = EXCLUDED.freight_total, payment_total = EXCLUDED.payment_total, dq_flag_count = EXCLUDED.dq_flag_count,
                etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;

    SELECT count(*) FILTER (WHERE customer_key = -1) AS customer, count(*) FILTER (WHERE customer_geography_key = -1) AS cust_geo,
           count(*) FILTER (WHERE order_status_key = -1) AS status, count(*) FILTER (WHERE approval_raw < 0) AS n_appr,
           count(*) FILTER (WHERE handling_raw < 0) AS n_hand, count(*) FILTER (WHERE transit_raw < 0) AS n_trans,
           count(*) FILTER (WHERE lead_raw < 0) AS n_lead, count(*) FILTER (WHERE promised_raw < 0) AS n_prom,
           count(*) FILTER (WHERE dw.date_key(purchase_ts) = -1) AS d_purch,
           count(*) FILTER (WHERE approved_ts IS NOT NULL AND dw.date_key(approved_ts) = -1) AS d_appr,
           count(*) FILTER (WHERE carrier_ts IS NOT NULL AND dw.date_key(carrier_ts) = -1) AS d_carr,
           count(*) FILTER (WHERE delivered_ts IS NOT NULL AND dw.date_key(delivered_ts) = -1) AS d_deliv,
           count(*) FILTER (WHERE estimated_ts IS NOT NULL AND dw.date_key(estimated_ts) = -1) AS d_est
    INTO v FROM tmp_fof;
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'customer_key', v.customer);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'customer_geography_key', v.cust_geo);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'order_status_key', v.status);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'purchase_date_key', v.d_purch);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'approved_date_key (value outside dim_date)', v.d_appr);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'carrier_date_key (value outside dim_date)', v.d_carr);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'delivered_date_key (value outside dim_date)', v.d_deliv);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'unknown_member', 'estimated_date_key (value outside dim_date)', v.d_est);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'negative_interval', 'approval_hours', v.n_appr);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'negative_interval', 'handling_days', v.n_hand);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'negative_interval', 'transit_days', v.n_trans);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'negative_interval', 'lead_days', v.n_lead);
    CALL dw.log_fact_issue(p_batch_id, 'fact_order_fulfillment', 'negative_interval', 'promised_days', v.n_prom);
END $$;

-- ---------------------------------------------------------------- fact_review (transaction); delivered_late comes from fact_order_fulfillment
CREATE OR REPLACE PROCEDURE dw.load_fact_review(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v record;
BEGIN
    DELETE FROM etl_log.fact_load_issue WHERE batch_id = p_batch_id AND fact_table = 'fact_review';   -- re-running a batch must not double-count
    CREATE TEMP TABLE tmp_frev ON COMMIT DROP AS
    SELECT r.review_id, r.order_id, dw.date_key(r.review_creation_date) AS creation_key, dw.date_key(r.review_answer_timestamp) AS answer_key,
           (r.review_creation_date IS NOT NULL) AS has_creation, (r.review_answer_timestamp IS NOT NULL) AS has_answer,
           coalesce(dc.customer_key, -1) AS customer_key, r.review_score,
           (nullif(trim(r.review_comment_title), '') IS NOT NULL)::int AS has_title,
           (nullif(trim(r.review_comment_message), '') IS NOT NULL)::int AS has_message,
           coalesce(length(nullif(trim(r.review_comment_message), '')), 0) AS comment_length,
           extract(epoch FROM r.review_answer_timestamp - r.review_creation_date) / 3600.0 AS response_raw,
           coalesce(f.is_late, 0) AS delivered_late, coalesce(f.is_delivered, 0)::smallint AS is_delivered, (f.order_id IS NULL) AS no_fulfillment
    FROM ods.order_reviews r
    JOIN ods.orders o ON o.order_id = r.order_id
    JOIN ods.customers c ON c.customer_id = o.customer_id
    LEFT JOIN dw.dim_customer dc ON dc.customer_unique_id = c.customer_unique_id
                                 AND o.order_purchase_timestamp::date BETWEEN dc.effective_from AND dc.effective_to
    LEFT JOIN dw.fact_order_fulfillment f ON f.order_id = r.order_id
    WHERE r.etl_batch_id = p_batch_id;
    SELECT count(*) INTO p_read FROM tmp_frev;

    WITH up AS (
        INSERT INTO dw.fact_review AS t (review_id, order_id, review_creation_date_key, review_answer_date_key, customer_key, review_score, is_negative,
                                         has_comment_title, has_comment_message, comment_length, response_hours, delivered_late, is_delivered, etl_batch_id)
        SELECT review_id, order_id, creation_key, answer_key, customer_key, review_score, (review_score <= 2)::int, has_title, has_message,
               comment_length, CASE WHEN response_raw >= 0 THEN round(response_raw::numeric, 2) END, delivered_late, is_delivered, p_batch_id
        FROM tmp_frev
        ON CONFLICT (review_id, order_id) DO UPDATE
            SET review_creation_date_key = EXCLUDED.review_creation_date_key, review_answer_date_key = EXCLUDED.review_answer_date_key,
                customer_key = EXCLUDED.customer_key, review_score = EXCLUDED.review_score, is_negative = EXCLUDED.is_negative,
                has_comment_title = EXCLUDED.has_comment_title, has_comment_message = EXCLUDED.has_comment_message,
                comment_length = EXCLUDED.comment_length, response_hours = EXCLUDED.response_hours,
                delivered_late = EXCLUDED.delivered_late, is_delivered = EXCLUDED.is_delivered, etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;

    SELECT count(*) FILTER (WHERE customer_key = -1) AS customer, count(*) FILTER (WHERE has_creation AND creation_key = -1) AS c_date,
           count(*) FILTER (WHERE has_answer AND answer_key = -1) AS a_date, count(*) FILTER (WHERE response_raw < 0) AS n_resp,
           count(*) FILTER (WHERE no_fulfillment) AS no_ful
    INTO v FROM tmp_frev;
    CALL dw.log_fact_issue(p_batch_id, 'fact_review', 'unknown_member', 'customer_key', v.customer);
    CALL dw.log_fact_issue(p_batch_id, 'fact_review', 'unknown_member', 'review_creation_date_key (value outside dim_date)', v.c_date);
    CALL dw.log_fact_issue(p_batch_id, 'fact_review', 'unknown_member', 'review_answer_date_key (value outside dim_date)', v.a_date);
    CALL dw.log_fact_issue(p_batch_id, 'fact_review', 'unknown_member', 'delivered_late, is_delivered (no fulfillment row, set to 0)', v.no_ful);
    CALL dw.log_fact_issue(p_batch_id, 'fact_review', 'negative_interval', 'response_hours', v.n_resp);
END $$;

-- ---------------------------------------------------------------- dim_seller.first_sale_date (after fact_order_item)
-- purchase date of the first order of the seller that is NOT in status group Failed (a canceled / unavailable order is not a sale; same scope as GMV, DW_DESIGN 6.4)
CREATE OR REPLACE PROCEDURE dw.load_dim_seller_first_sale(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                          INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(DISTINCT f.seller_key) INTO p_read
    FROM dw.fact_order_item f JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
    WHERE f.seller_key <> -1;
    -- sellers whose orders are all Failed get NULL (also clears a date set by an earlier run)
    UPDATE dw.dim_seller s SET first_sale_date = m.d, dw_updated_at = now()
    FROM dw.dim_seller s0
    LEFT JOIN (SELECT f.seller_key, min(dd.full_date) AS d
               FROM dw.fact_order_item f
               JOIN dw.dim_date dd ON dd.date_key = f.purchase_date_key
               JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
               WHERE f.seller_key <> -1 GROUP BY f.seller_key) m ON m.seller_key = s0.seller_key
    WHERE s.seller_key = s0.seller_key AND s.seller_key <> -1 AND s.first_sale_date IS DISTINCT FROM m.d;
    GET DIAGNOSTICS p_updated = ROW_COUNT;
    p_inserted := 0;
    p_rejected := 0;
END $$;

-- ---------------------------------------------------------------- fact_lead_funnel (accumulating snapshot, recomputed completely)
-- seller_gmv_first_90d = Σ price of non-Failed orders of the seller bought in the 90 days starting on the first-sale date (days 0..89).
CREATE OR REPLACE PROCEDURE dw.load_fact_lead_funnel(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                     INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    v record;
BEGIN
    DELETE FROM etl_log.fact_load_issue WHERE batch_id = p_batch_id AND fact_table = 'fact_lead_funnel';   -- re-running a batch must not double-count
    CREATE TEMP TABLE tmp_gmv90 ON COMMIT DROP AS
    SELECT f.seller_key, sum(f.price) AS gmv
    FROM dw.fact_order_item f
    JOIN dw.dim_seller s ON s.seller_key = f.seller_key AND s.first_sale_date IS NOT NULL AND s.is_from_funnel
    JOIN dw.dim_date dd ON dd.date_key = f.purchase_date_key
    JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key AND os.status_group <> 'Failed'
    WHERE dd.full_date >= s.first_sale_date AND dd.full_date < s.first_sale_date + 90
    GROUP BY f.seller_key;

    CREATE TEMP TABLE tmp_flf ON COMMIT DROP AS
    SELECT m.mql_id, m.landing_page_id, dw.date_key(m.first_contact_date::timestamp) AS first_contact_key,
           CASE WHEN d.mql_id IS NULL THEN -1 ELSE dw.date_key(d.won_date) END AS won_key,
           CASE WHEN s.first_sale_date IS NULL THEN -1 ELSE dw.date_key(s.first_sale_date::timestamp) END AS first_sale_key,
           coalesce(lo.lead_origin_key, -1) AS lead_origin_key,
           coalesce(lp.lead_profile_key, -1) AS lead_profile_key,
           coalesce(s.seller_key, -1) AS seller_key, coalesce(sdr.sales_rep_key, -1) AS sdr_key, coalesce(sr.sales_rep_key, -1) AS sr_key,
           (d.mql_id IS NOT NULL)::int AS is_won, (s.first_sale_date IS NOT NULL)::int AS has_first_sale,
           d.won_date::date - m.first_contact_date AS close_raw, s.first_sale_date - d.won_date::date AS sale_raw,
           d.declared_product_catalog_size, d.declared_monthly_revenue,
           CASE WHEN s.first_sale_date IS NULL THEN NULL ELSE coalesce(g.gmv, 0) END AS gmv90,
           (d.mql_id IS NOT NULL AND s.seller_id IS NULL) AS no_seller,
           (d.mql_id IS NOT NULL AND lp.lead_profile_key IS NULL) AS no_profile,
           (d.sdr_id IS NOT NULL AND sdr.sales_rep_key IS NULL) AS no_sdr, (d.sr_id IS NOT NULL AND sr.sales_rep_key IS NULL) AS no_sr
    FROM ods.mql m
    LEFT JOIN dw.dim_lead_origin lo ON lo.origin = m.origin
    LEFT JOIN ods.closed_deals d ON d.mql_id = m.mql_id
    LEFT JOIN dw.dim_seller s ON s.seller_id = d.seller_id
    LEFT JOIN dw.dim_lead_profile lp ON lp.business_segment = d.business_segment AND lp.lead_type = d.lead_type
         AND lp.lead_behaviour_profile = d.lead_behaviour_profile AND lp.business_type = d.business_type
         AND lp.has_company = d.has_company AND lp.has_gtin = d.has_gtin AND lp.average_stock = d.average_stock
    LEFT JOIN dw.dim_sales_rep sdr ON sdr.rep_id = d.sdr_id AND sdr.rep_role = 'SDR'
    LEFT JOIN dw.dim_sales_rep sr ON sr.rep_id = d.sr_id AND sr.rep_role = 'SR'
    LEFT JOIN tmp_gmv90 g ON g.seller_key = s.seller_key;
    SELECT count(*) INTO p_read FROM tmp_flf;

    WITH up AS (
        INSERT INTO dw.fact_lead_funnel AS t
        SELECT mql_id, landing_page_id, first_contact_key, won_key, first_sale_key, lead_origin_key, lead_profile_key, seller_key, sdr_key, sr_key,
               is_won, has_first_sale, CASE WHEN close_raw >= 0 THEN close_raw END, CASE WHEN sale_raw >= 0 THEN sale_raw END,
               declared_product_catalog_size, declared_monthly_revenue, gmv90, p_batch_id
        FROM tmp_flf
        ON CONFLICT (mql_id) DO UPDATE
            SET landing_page_id = EXCLUDED.landing_page_id, first_contact_date_key = EXCLUDED.first_contact_date_key, won_date_key = EXCLUDED.won_date_key,
                first_sale_date_key = EXCLUDED.first_sale_date_key, lead_origin_key = EXCLUDED.lead_origin_key, lead_profile_key = EXCLUDED.lead_profile_key,
                seller_key = EXCLUDED.seller_key, sdr_key = EXCLUDED.sdr_key, sr_key = EXCLUDED.sr_key, is_won = EXCLUDED.is_won,
                has_first_sale = EXCLUDED.has_first_sale, days_to_close = EXCLUDED.days_to_close, days_won_to_first_sale = EXCLUDED.days_won_to_first_sale,
                declared_product_catalog_size = EXCLUDED.declared_product_catalog_size, declared_monthly_revenue = EXCLUDED.declared_monthly_revenue,
                seller_gmv_first_90d = EXCLUDED.seller_gmv_first_90d, etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;

    SELECT count(*) FILTER (WHERE lead_origin_key = -1) AS origin, count(*) FILTER (WHERE no_seller) AS seller, count(*) FILTER (WHERE no_profile) AS prof,
           count(*) FILTER (WHERE no_sdr) AS sdr, count(*) FILTER (WHERE no_sr) AS sr,
           count(*) FILTER (WHERE close_raw < 0) AS n_close, count(*) FILTER (WHERE sale_raw < 0) AS n_sale
    INTO v FROM tmp_flf;
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'unknown_member', 'lead_origin_key', v.origin);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'unknown_member', 'seller_key (won deal)', v.seller);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'unknown_member', 'lead_profile_key (won deal)', v.prof);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'unknown_member', 'sdr_key (deal has sdr_id)', v.sdr);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'unknown_member', 'sr_key (deal has sr_id)', v.sr);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'negative_interval', 'days_to_close (won before first contact)', v.n_close);
    CALL dw.log_fact_issue(p_batch_id, 'fact_lead_funnel', 'negative_interval', 'days_won_to_first_sale (sold before won)', v.n_sale);
END $$;

-- ---------------------------------------------------------------- fact_seller_monthly (periodic snapshot, dense, recomputed completely)
-- One row per seller and month from the seller's first month with an order to the last month with any order in the data.
-- orders / items / canceled / delivered / late count every order; gmv and freight exclude Failed orders (KPI "GMV", DW_DESIGN 9).
-- months_since_first_sale is counted from the month of dim_seller.first_sale_date (first non-Failed order): negative in earlier months that
-- only hold Failed orders, NULL for sellers that never had a non-Failed order.
CREATE OR REPLACE PROCEDURE dw.load_fact_seller_monthly(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                        INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE tmp_fsm_it ON COMMIT DROP AS
    SELECT f.seller_key, date_trunc('month', dd.full_date)::date AS m, f.order_id, f.price, f.freight_value, os.status_group
    FROM dw.fact_order_item f
    JOIN dw.dim_date dd ON dd.date_key = f.purchase_date_key
    JOIN dw.dim_order_status os ON os.order_status_key = f.order_status_key
    WHERE f.seller_key <> -1 AND f.purchase_date_key <> -1;

    CREATE TEMP TABLE tmp_fsm_ord ON COMMIT DROP AS      -- one row per (seller, month, order)
    SELECT i.seller_key, i.m, i.order_id, coalesce(max(fo.is_delivered), 0) AS is_delivered, coalesce(max(fo.is_late), 0) AS is_late,
           coalesce(max(fo.is_canceled), 0) AS is_canceled
    FROM tmp_fsm_it i LEFT JOIN dw.fact_order_fulfillment fo ON fo.order_id = i.order_id
    GROUP BY i.seller_key, i.m, i.order_id;

    CREATE TEMP TABLE tmp_fsm ON COMMIT DROP AS
    WITH sel AS (SELECT seller_key, min(m) AS first_m FROM tmp_fsm_it GROUP BY seller_key),
    lastm AS (SELECT max(m) AS last_m FROM tmp_fsm_it),
    grid AS (SELECT s.seller_key, s.first_m, gs::date AS m FROM sel s CROSS JOIN lastm l, generate_series(s.first_m::timestamp, l.last_m::timestamp, interval '1 month') gs),
    a_it AS (
        SELECT seller_key, m, count(*) AS items, sum(price) FILTER (WHERE status_group <> 'Failed') AS gmv,
               sum(freight_value) FILTER (WHERE status_group <> 'Failed') AS freight
        FROM tmp_fsm_it GROUP BY seller_key, m),
    a_ord AS (
        SELECT seller_key, m, count(*) AS orders, sum(is_delivered) AS delivered_orders, sum(is_late) AS late_orders, sum(is_canceled) AS canceled_orders
        FROM tmp_fsm_ord GROUP BY seller_key, m),
    a_rev AS (
        SELECT o.seller_key, o.m, avg(r.review_score) AS avg_score
        FROM tmp_fsm_ord o JOIN dw.fact_review r ON r.order_id = o.order_id GROUP BY o.seller_key, o.m)
    SELECT to_char(g.m, 'YYYYMMDD')::int AS month_date_key, g.seller_key,
           coalesce(ao.orders, 0) AS orders, coalesce(ai.items, 0) AS items, coalesce(ai.gmv, 0) AS gmv, coalesce(ai.freight, 0) AS freight,
           coalesce(ao.delivered_orders, 0) AS delivered_orders, coalesce(ao.late_orders, 0) AS late_orders,
           CASE WHEN ao.delivered_orders > 0 THEN round(ao.late_orders::numeric / ao.delivered_orders, 4) END AS late_rate,
           coalesce(ao.canceled_orders, 0) AS canceled_orders, round(ar.avg_score, 2) AS avg_review_score,
           (coalesce(ao.orders, 0) > 0)::int AS is_active,
           CASE WHEN ds.first_sale_date IS NOT NULL THEN
               ((extract(year FROM g.m) - extract(year FROM ds.first_sale_date)) * 12 + extract(month FROM g.m) - extract(month FROM ds.first_sale_date))::int END AS months_since_first_sale
    FROM grid g
    JOIN dw.dim_seller ds ON ds.seller_key = g.seller_key
    LEFT JOIN a_it ai ON ai.seller_key = g.seller_key AND ai.m = g.m
    LEFT JOIN a_ord ao ON ao.seller_key = g.seller_key AND ao.m = g.m
    LEFT JOIN a_rev ar ON ar.seller_key = g.seller_key AND ar.m = g.m;
    SELECT count(*) INTO p_read FROM tmp_fsm;

    WITH up AS (
        INSERT INTO dw.fact_seller_monthly AS t
        SELECT month_date_key, seller_key, orders, items, gmv, freight, delivered_orders, late_orders, late_rate, canceled_orders, avg_review_score,
               is_active, months_since_first_sale, p_batch_id
        FROM tmp_fsm
        ON CONFLICT (month_date_key, seller_key) DO UPDATE
            SET orders = EXCLUDED.orders, items = EXCLUDED.items, gmv = EXCLUDED.gmv, freight = EXCLUDED.freight,
                delivered_orders = EXCLUDED.delivered_orders, late_orders = EXCLUDED.late_orders, late_rate = EXCLUDED.late_rate,
                canceled_orders = EXCLUDED.canceled_orders, avg_review_score = EXCLUDED.avg_review_score, is_active = EXCLUDED.is_active,
                months_since_first_sale = EXCLUDED.months_since_first_sale, etl_batch_id = EXCLUDED.etl_batch_id
            WHERE to_jsonb(t) - 'etl_batch_id' IS DISTINCT FROM to_jsonb(EXCLUDED) - 'etl_batch_id'
        RETURNING (xmax = 0) AS ins)
    SELECT count(*) FILTER (WHERE ins), count(*) FILTER (WHERE NOT ins) INTO p_inserted, p_updated FROM up;
    p_rejected := 0;
END $$;

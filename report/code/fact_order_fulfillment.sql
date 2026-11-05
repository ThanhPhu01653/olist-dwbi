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
    -- ... (rút gọn, xem file nguồn)
END $$;

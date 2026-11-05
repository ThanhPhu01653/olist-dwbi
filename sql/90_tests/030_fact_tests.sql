-- Fact tests (DW_DESIGN section 13). Returns (check_name, target_table, expected, actual, passed).
-- Rejected rows are counted only for the batches present in staging (the ones that produced the current ODS content).
WITH rej AS (
    SELECT job_name, count(*) AS n,
           coalesce(sum((record ->> 'price')::numeric), 0) AS price, coalesce(sum((record ->> 'freight_value')::numeric), 0) AS freight,
           coalesce(sum((record ->> 'payment_value')::numeric), 0) AS pay
    FROM etl_log.rejected_rows
    WHERE batch_id IN (SELECT load_batch_id FROM staging.stg_orders UNION SELECT load_batch_id FROM staging.stg_order_items
                       UNION SELECT load_batch_id FROM staging.stg_order_payments UNION SELECT load_batch_id FROM staging.stg_order_reviews)
    GROUP BY job_name),
mo AS (   -- months of the periodic snapshot
    SELECT seller_key, count(*) AS n, min(to_date(month_date_key::text, 'YYYYMMDD')) AS first_m, max(to_date(month_date_key::text, 'YYYYMMDD')) AS last_m
    FROM dw.fact_seller_monthly GROUP BY seller_key),
gl AS (SELECT max(to_date(month_date_key::text, 'YYYYMMDD')) AS last_m FROM dw.fact_seller_monthly),
fk_cols AS (   -- every *_key column of the fact tables
    SELECT c.table_name, c.column_name, c.is_nullable
    FROM information_schema.columns c
    WHERE c.table_schema = 'dw' AND c.table_name LIKE 'fact\_%' AND c.column_name LIKE '%\_key')
-- ------------------------------------------------ row counts: oltp -> staging -> ods -> dw (difference = rejected rows)
SELECT 'fact_order_item rows = ods.order_items' AS check_name, 'dw.fact_order_item' AS target_table, (SELECT count(*) FROM ods.order_items)::text AS expected,
       count(*)::text AS actual, count(*) = (SELECT count(*) FROM ods.order_items) AS passed FROM dw.fact_order_item
UNION ALL
SELECT 'oltp.order_items = fact_order_item + rejected', 'dw.fact_order_item', (SELECT count(*) FROM oltp.order_items)::text,
       (count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_items'), 0))::text,
       (SELECT count(*) FROM oltp.order_items) = count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_items'), 0) FROM dw.fact_order_item
UNION ALL
SELECT 'oltp.orders = fact_order_fulfillment + rejected', 'dw.fact_order_fulfillment', (SELECT count(*) FROM oltp.orders)::text,
       (count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_orders'), 0))::text,
       (SELECT count(*) FROM oltp.orders) = count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_orders'), 0) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'oltp.order_payments = fact_payment + rejected', 'dw.fact_payment', (SELECT count(*) FROM oltp.order_payments)::text,
       (count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_payments'), 0))::text,
       (SELECT count(*) FROM oltp.order_payments) = count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_payments'), 0) FROM dw.fact_payment
UNION ALL
SELECT 'oltp.order_reviews = fact_review + rejected', 'dw.fact_review', (SELECT count(*) FROM oltp.order_reviews)::text,
       (count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_reviews'), 0))::text,
       (SELECT count(*) FROM oltp.order_reviews) = count(*) + coalesce((SELECT n FROM rej WHERE job_name = 'ods.load_order_reviews'), 0) FROM dw.fact_review
UNION ALL
SELECT 'crm.mql = fact_lead_funnel (one row per MQL)', 'dw.fact_lead_funnel', (SELECT count(*) FROM crm.mql)::text, count(*)::text,
       (SELECT count(*) FROM crm.mql) = count(*) FROM dw.fact_lead_funnel
UNION ALL
-- ------------------------------------------------ money reconciliation
SELECT 'sum(price) oltp = fact_order_item + rejected', 'dw.fact_order_item', (SELECT sum(price) FROM oltp.order_items)::text,
       (sum(price) + coalesce((SELECT price FROM rej WHERE job_name = 'ods.load_order_items'), 0))::text,
       (SELECT sum(price) FROM oltp.order_items) = sum(price) + coalesce((SELECT price FROM rej WHERE job_name = 'ods.load_order_items'), 0) FROM dw.fact_order_item
UNION ALL
SELECT 'sum(freight_value) oltp = fact_order_item + rejected', 'dw.fact_order_item', (SELECT sum(freight_value) FROM oltp.order_items)::text,
       (sum(freight_value) + coalesce((SELECT freight FROM rej WHERE job_name = 'ods.load_order_items'), 0))::text,
       (SELECT sum(freight_value) FROM oltp.order_items) = sum(freight_value) + coalesce((SELECT freight FROM rej WHERE job_name = 'ods.load_order_items'), 0) FROM dw.fact_order_item
UNION ALL
SELECT 'sum(payment_value) oltp = fact_payment + rejected', 'dw.fact_payment', (SELECT sum(payment_value) FROM oltp.order_payments)::text,
       (sum(payment_value) + coalesce((SELECT pay FROM rej WHERE job_name = 'ods.load_order_payments'), 0))::text,
       (SELECT sum(payment_value) FROM oltp.order_payments) = sum(payment_value) + coalesce((SELECT pay FROM rej WHERE job_name = 'ods.load_order_payments'), 0) FROM dw.fact_payment
UNION ALL
SELECT 'item_total = price + freight_value on every row', 'dw.fact_order_item', '0', count(*)::text, count(*) = 0 FROM dw.fact_order_item WHERE item_total <> price + freight_value
UNION ALL
SELECT 'fulfillment.order_value = sum(fact_order_item.price)', 'dw.fact_order_fulfillment', (SELECT sum(price) FROM dw.fact_order_item)::text, sum(order_value)::text,
       sum(order_value) = (SELECT sum(price) FROM dw.fact_order_item) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'fulfillment.freight_total = sum(fact_order_item.freight_value)', 'dw.fact_order_fulfillment', (SELECT sum(freight_value) FROM dw.fact_order_item)::text, sum(freight_total)::text,
       sum(freight_total) = (SELECT sum(freight_value) FROM dw.fact_order_item) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'fulfillment.payment_total = sum(fact_payment.payment_value)', 'dw.fact_order_fulfillment', (SELECT sum(payment_value) FROM dw.fact_payment)::text, sum(payment_total)::text,
       sum(payment_total) = (SELECT sum(payment_value) FROM dw.fact_payment) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'fulfillment.item_count = number of fact_order_item rows', 'dw.fact_order_fulfillment', (SELECT count(*) FROM dw.fact_order_item)::text, sum(item_count)::text,
       sum(item_count) = (SELECT count(*) FROM dw.fact_order_item) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'fact_seller_monthly.gmv = GMV of fact_order_item (orders not Failed)', 'dw.fact_seller_monthly',
       (SELECT coalesce(sum(f.price), 0) FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key
        WHERE s.status_group <> 'Failed' AND f.seller_key <> -1 AND f.purchase_date_key <> -1)::text, coalesce(sum(gmv), 0)::text,
       coalesce(sum(gmv), 0) = (SELECT coalesce(sum(f.price), 0) FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key
                                WHERE s.status_group <> 'Failed' AND f.seller_key <> -1 AND f.purchase_date_key <> -1) FROM dw.fact_seller_monthly
UNION ALL
SELECT 'fact_seller_monthly.items = number of fact_order_item rows', 'dw.fact_seller_monthly',
       (SELECT count(*) FROM dw.fact_order_item WHERE seller_key <> -1 AND purchase_date_key <> -1)::text, coalesce(sum(items), 0)::text,
       coalesce(sum(items), 0) = (SELECT count(*) FROM dw.fact_order_item WHERE seller_key <> -1 AND purchase_date_key <> -1) FROM dw.fact_seller_monthly
UNION ALL
-- ------------------------------------------------ grain, keys
SELECT 'unique grain (order_id, order_item_id)', 'dw.fact_order_item', '0', (count(*) - count(DISTINCT (order_id, order_item_id)))::text,
       count(*) = count(DISTINCT (order_id, order_item_id)) FROM dw.fact_order_item
UNION ALL
SELECT 'unique grain (order_id)', 'dw.fact_order_fulfillment', '0', (count(*) - count(DISTINCT order_id))::text, count(*) = count(DISTINCT order_id) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'unique grain (order_id, payment_sequential)', 'dw.fact_payment', '0', (count(*) - count(DISTINCT (order_id, payment_sequential)))::text,
       count(*) = count(DISTINCT (order_id, payment_sequential)) FROM dw.fact_payment
UNION ALL
SELECT 'unique grain (review_id, order_id)', 'dw.fact_review', '0', (count(*) - count(DISTINCT (review_id, order_id)))::text,
       count(*) = count(DISTINCT (review_id, order_id)) FROM dw.fact_review
UNION ALL
SELECT 'unique grain (mql_id)', 'dw.fact_lead_funnel', '0', (count(*) - count(DISTINCT mql_id))::text, count(*) = count(DISTINCT mql_id) FROM dw.fact_lead_funnel
UNION ALL
SELECT 'unique grain (month, seller)', 'dw.fact_seller_monthly', '0', (count(*) - count(DISTINCT (month_date_key, seller_key)))::text,
       count(*) = count(DISTINCT (month_date_key, seller_key)) FROM dw.fact_seller_monthly
UNION ALL
SELECT 'no nullable *_key column in any fact', 'dw.fact_*', '0', count(*)::text, count(*) = 0 FROM fk_cols WHERE is_nullable = 'YES'
UNION ALL
SELECT 'every *_key column of a fact has a validated FOREIGN KEY (no key points to a missing dimension row)', 'dw.fact_*', '0', count(*)::text, count(*) = 0
FROM fk_cols k
WHERE NOT EXISTS (SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid JOIN pg_namespace n ON n.oid = t.relnamespace
                  JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
                  WHERE c.contype = 'f' AND c.convalidated AND n.nspname = 'dw' AND t.relname = k.table_name AND a.attname = k.column_name)
UNION ALL
SELECT 'no Unknown member (-1) in mandatory lookups of fact_order_item', 'dw.fact_order_item', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_item WHERE -1 IN (purchase_date_key, customer_key, customer_geography_key, seller_geography_key, seller_key, product_key, order_status_key)
UNION ALL
SELECT 'no Unknown member (-1) in mandatory lookups of fact_order_fulfillment / fact_payment / fact_review', 'dw.fact_order_fulfillment', '0', x.n::text, x.n = 0
FROM (SELECT (SELECT count(*) FROM dw.fact_order_fulfillment WHERE -1 IN (purchase_date_key, estimated_date_key, customer_key, customer_geography_key, order_status_key))
           + (SELECT count(*) FROM dw.fact_payment WHERE -1 IN (purchase_date_key, customer_key, payment_type_key))
           + (SELECT count(*) FROM dw.fact_review WHERE -1 IN (review_creation_date_key, customer_key)) AS n) x
UNION ALL
SELECT 'fact_order_item.customer_key is the SCD2 version in force on the purchase date', 'dw.fact_order_item', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_item f JOIN dw.dim_customer c ON c.customer_key = f.customer_key JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
WHERE d.full_date NOT BETWEEN c.effective_from AND c.effective_to
UNION ALL
SELECT 'fact_order_item.customer_key of the same order equals fact_order_fulfillment.customer_key', 'dw.fact_order_item', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_item f JOIN dw.fact_order_fulfillment o ON o.order_id = f.order_id WHERE f.customer_key <> o.customer_key
UNION ALL
-- ------------------------------------------------ fulfillment logic
SELECT 'no negative duration stored in fact_order_fulfillment', 'dw.fact_order_fulfillment', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_fulfillment WHERE approval_hours < 0 OR handling_days < 0 OR transit_days < 0 OR lead_days < 0 OR promised_days < 0
UNION ALL
SELECT 'is_late = 1 only for delivered orders with delay_days > 0 (and vice versa)', 'dw.fact_order_fulfillment', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_fulfillment WHERE is_late <> CASE WHEN is_delivered = 1 AND delay_days > 0 THEN 1 ELSE 0 END
UNION ALL
SELECT 'is_delivered = status delivered with a delivery date', 'dw.fact_order_fulfillment', (SELECT count(*) FROM ods.orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL)::text,
       sum(is_delivered)::text, sum(is_delivered) = (SELECT count(*) FROM ods.orders WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL) FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'is_canceled = status canceled', 'dw.fact_order_fulfillment', (SELECT count(*) FROM ods.orders WHERE order_status = 'canceled')::text, sum(is_canceled)::text,
       sum(is_canceled) = (SELECT count(*) FROM ods.orders WHERE order_status = 'canceled') FROM dw.fact_order_fulfillment
UNION ALL
SELECT 'milestone date key is -1 exactly when the timestamp is missing', 'dw.fact_order_fulfillment', '0', count(*)::text, count(*) = 0
FROM dw.fact_order_fulfillment WHERE (approved_ts IS NULL) <> (approved_date_key = -1) OR (carrier_ts IS NULL) <> (carrier_date_key = -1)
   OR (delivered_ts IS NULL) <> (delivered_date_key = -1) OR (estimated_ts IS NULL) <> (estimated_date_key = -1)
UNION ALL
SELECT 'seller_count <= item_count; orders with item_count = 0 are exactly the ods orders without item rows', 'dw.fact_order_fulfillment',
       (SELECT count(*) FROM ods.orders o WHERE NOT EXISTS (SELECT 1 FROM ods.order_items i WHERE i.order_id = o.order_id))::text,
       count(*) FILTER (WHERE item_count = 0)::text,
       count(*) FILTER (WHERE seller_count > item_count) = 0
       AND count(*) FILTER (WHERE item_count = 0) = (SELECT count(*) FROM ods.orders o WHERE NOT EXISTS (SELECT 1 FROM ods.order_items i WHERE i.order_id = o.order_id))
FROM dw.fact_order_fulfillment
UNION ALL
-- ------------------------------------------------ review, seller, funnel, monthly snapshot
SELECT 'fact_review.delivered_late = fact_order_fulfillment.is_late', 'dw.fact_review', '0', count(*)::text, count(*) = 0
FROM dw.fact_review r JOIN dw.fact_order_fulfillment o ON o.order_id = r.order_id WHERE r.delivered_late <> o.is_late
UNION ALL
SELECT 'fact_review.is_negative = (review_score <= 2)', 'dw.fact_review', '0', count(*)::text, count(*) = 0
FROM dw.fact_review WHERE is_negative <> (review_score <= 2)::int
UNION ALL
SELECT 'dim_seller.first_sale_date = earliest purchase date in fact_order_item', 'dw.dim_seller', '0', count(*)::text, count(*) = 0
FROM dw.dim_seller s LEFT JOIN (SELECT f.seller_key, min(d.full_date) AS d FROM dw.fact_order_item f JOIN dw.dim_date d ON d.date_key = f.purchase_date_key
                                 WHERE f.seller_key <> -1 GROUP BY f.seller_key) m ON m.seller_key = s.seller_key
WHERE s.seller_key <> -1 AND s.first_sale_date IS DISTINCT FROM m.d
UNION ALL
SELECT 'fact_lead_funnel: is_won = 1 <=> won_date_key <> -1 <=> seller_key <> -1', 'dw.fact_lead_funnel', '0', count(*)::text, count(*) = 0
FROM dw.fact_lead_funnel WHERE (is_won = 1) <> (won_date_key <> -1) OR (is_won = 1) <> (seller_key <> -1)
UNION ALL
SELECT 'fact_lead_funnel: is_won total = rows of ods.closed_deals', 'dw.fact_lead_funnel', (SELECT count(*) FROM ods.closed_deals)::text, sum(is_won)::text,
       sum(is_won) = (SELECT count(*) FROM ods.closed_deals) FROM dw.fact_lead_funnel
UNION ALL
SELECT 'fact_lead_funnel: has_first_sale = 1 <=> first_sale_date_key <> -1; needs is_won', 'dw.fact_lead_funnel', '0', count(*)::text, count(*) = 0
FROM dw.fact_lead_funnel WHERE (has_first_sale = 1) <> (first_sale_date_key <> -1) OR (has_first_sale = 1 AND is_won = 0)
UNION ALL
SELECT 'fact_lead_funnel: no Unknown origin; no negative days_to_close', 'dw.fact_lead_funnel', '0', count(*)::text, count(*) = 0
FROM dw.fact_lead_funnel WHERE lead_origin_key = -1 OR days_to_close < 0 OR days_won_to_first_sale < 0
UNION ALL
SELECT 'fact_lead_funnel: won deals have profile, SDR and SR rows (not -1)', 'dw.fact_lead_funnel', '0', count(*)::text, count(*) = 0
FROM dw.fact_lead_funnel WHERE is_won = 1 AND (lead_profile_key = -1 OR sdr_key = -1 OR sr_key = -1)
UNION ALL
SELECT 'fact_lead_funnel: seller_gmv_first_90d only for sellers with a first sale', 'dw.fact_lead_funnel', '0', count(*)::text, count(*) = 0
FROM dw.fact_lead_funnel WHERE (seller_gmv_first_90d IS NOT NULL) <> (has_first_sale = 1)
UNION ALL
SELECT 'fact_seller_monthly is dense: first month of the seller .. last month of the data, no gaps', 'dw.fact_seller_monthly', '0', count(*)::text, count(*) = 0
FROM mo CROSS JOIN gl
WHERE mo.last_m <> gl.last_m OR mo.n <> ((extract(year FROM gl.last_m) - extract(year FROM mo.first_m)) * 12 + extract(month FROM gl.last_m) - extract(month FROM mo.first_m) + 1)
UNION ALL
SELECT 'fact_seller_monthly: every seller with items has a monthly row, first month = first sale month', 'dw.fact_seller_monthly', '0', count(*)::text, count(*) = 0
FROM dw.dim_seller s LEFT JOIN mo ON mo.seller_key = s.seller_key
WHERE s.first_sale_date IS NOT NULL AND (mo.seller_key IS NULL OR mo.first_m <> date_trunc('month', s.first_sale_date)::date)
UNION ALL
SELECT 'fact_seller_monthly: is_active <=> orders > 0; late_orders <= delivered_orders', 'dw.fact_seller_monthly', '0', count(*)::text, count(*) = 0
FROM dw.fact_seller_monthly WHERE (is_active = 1) <> (orders > 0) OR late_orders > delivered_orders OR (orders = 0 AND (items <> 0 OR gmv <> 0))

-- Mart tests: every mart must reconcile with the facts it summarises. Returns (check_name, target_table, expected, actual, passed).
WITH g AS (
    SELECT sum(f.price) AS gmv FROM dw.fact_order_item f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key AND s.status_group <> 'Failed'),
nf AS (   -- orders used by RFM / cohort: not Failed and with items
    SELECT f.customer_key, f.order_id FROM dw.fact_order_fulfillment f JOIN dw.dim_order_status s ON s.order_status_key = f.order_status_key
    WHERE s.status_group <> 'Failed' AND f.item_count > 0 AND f.customer_key <> -1)
SELECT 'v_sales_daily: sum(gmv) = GMV of fact_order_item' AS check_name, 'mart_sales.v_sales_daily' AS target_table, (SELECT gmv FROM g)::text AS expected,
       sum(gmv)::text AS actual, sum(gmv) = (SELECT gmv FROM g) AS passed FROM mart_sales.v_sales_daily
UNION ALL SELECT 'v_sales_category_month: sum(gmv) = GMV', 'mart_sales.v_sales_category_month', (SELECT gmv FROM g)::text, sum(gmv)::text, sum(gmv) = (SELECT gmv FROM g) FROM mart_sales.v_sales_category_month
UNION ALL SELECT 'v_sales_state_month: sum(gmv) = GMV', 'mart_sales.v_sales_state_month', (SELECT gmv FROM g)::text, sum(gmv)::text, sum(gmv) = (SELECT gmv FROM g) FROM mart_sales.v_sales_state_month
UNION ALL SELECT 'v_category_pareto: sum(gmv) = GMV and cumulative share ends at 100', 'mart_sales.v_category_pareto', (SELECT gmv FROM g)::text, sum(gmv)::text,
       sum(gmv) = (SELECT gmv FROM g) AND max(cum_share_pct) = 100 FROM mart_sales.v_category_pareto
UNION ALL SELECT 'v_fulfillment_order: one row per order', 'mart_fulfillment.v_fulfillment_order', (SELECT count(*) FROM dw.fact_order_fulfillment)::text, count(*)::text,
       count(*) = (SELECT count(*) FROM dw.fact_order_fulfillment) FROM mart_fulfillment.v_fulfillment_order
UNION ALL SELECT 'v_fulfillment_state_month: sum(orders) = orders; sum(late_orders) = late orders', 'mart_fulfillment.v_fulfillment_state_month',
       (SELECT count(*) || ' / ' || sum(is_late) FROM dw.fact_order_fulfillment), sum(orders) || ' / ' || sum(late_orders),
       sum(orders) = (SELECT count(*) FROM dw.fact_order_fulfillment) AND sum(late_orders) = (SELECT sum(is_late) FROM dw.fact_order_fulfillment) FROM mart_fulfillment.v_fulfillment_state_month
UNION ALL SELECT 'v_status_funnel: stage 1 (placed) = orders; stage 4 (delivered) = delivered orders', 'mart_fulfillment.v_status_funnel',
       (SELECT count(*) || ' / ' || sum(is_delivered) FROM dw.fact_order_fulfillment), sum(orders) FILTER (WHERE stage_no = 1) || ' / ' || sum(orders) FILTER (WHERE stage_no = 4),
       sum(orders) FILTER (WHERE stage_no = 1) = (SELECT count(*) FROM dw.fact_order_fulfillment) AND sum(orders) FILTER (WHERE stage_no = 4) = (SELECT sum(is_delivered) FROM dw.fact_order_fulfillment)
FROM mart_fulfillment.v_status_funnel
UNION ALL SELECT 'v_payment_mix_month: sum(payment_value) = fact_payment', 'mart_cx.v_payment_mix_month', (SELECT sum(payment_value) FROM dw.fact_payment)::text, sum(payment_value)::text,
       sum(payment_value) = (SELECT sum(payment_value) FROM dw.fact_payment) FROM mart_cx.v_payment_mix_month
UNION ALL SELECT 'v_review_vs_delay: reviews = reviews of delivered orders', 'mart_cx.v_review_vs_delay',
       (SELECT count(*) FROM dw.fact_review r JOIN dw.fact_order_fulfillment o ON o.order_id = r.order_id AND o.is_delivered = 1 AND o.delay_days IS NOT NULL)::text, sum(reviews)::text,
       sum(reviews) = (SELECT count(*) FROM dw.fact_review r JOIN dw.fact_order_fulfillment o ON o.order_id = r.order_id AND o.is_delivered = 1 AND o.delay_days IS NOT NULL) FROM mart_cx.v_review_vs_delay
UNION ALL SELECT 'v_customer_rfm: one row per customer; sum(frequency) = orders (not Failed, with items)', 'mart_cx.v_customer_rfm',
       (SELECT count(DISTINCT c.customer_unique_id) || ' / ' || (SELECT count(*) FROM nf) FROM nf JOIN dw.dim_customer c USING (customer_key)), count(*) || ' / ' || sum(frequency),
       count(*) = (SELECT count(DISTINCT c.customer_unique_id) FROM nf JOIN dw.dim_customer c USING (customer_key)) AND sum(frequency) = (SELECT count(*) FROM nf) FROM mart_cx.v_customer_rfm
UNION ALL SELECT 'v_customer_cohort: sum of cohort sizes (month 0) = customers in v_customer_rfm', 'mart_cx.v_customer_cohort', (SELECT count(*) FROM mart_cx.v_customer_rfm)::text,
       sum(cohort_size)::text, sum(cohort_size) = (SELECT count(*) FROM mart_cx.v_customer_rfm) FROM mart_cx.v_customer_cohort WHERE months_since = 0
UNION ALL SELECT 'v_funnel_by_origin_month: sum(mqls) = fact_lead_funnel rows; sum(won) = sum(is_won)', 'mart_acquisition.v_funnel_by_origin_month',
       (SELECT count(*) || ' / ' || sum(is_won) FROM dw.fact_lead_funnel), sum(mqls) || ' / ' || sum(won),
       sum(mqls) = (SELECT count(*) FROM dw.fact_lead_funnel) AND sum(won) = (SELECT sum(is_won) FROM dw.fact_lead_funnel) FROM mart_acquisition.v_funnel_by_origin_month
UNION ALL SELECT 'v_seller_scorecard: one row per seller with sales; sum(gmv) = sum(fact_seller_monthly.gmv)', 'mart_acquisition.v_seller_scorecard',
       (SELECT count(DISTINCT seller_key) || ' / ' || sum(gmv) FROM dw.fact_seller_monthly), count(*) || ' / ' || sum(gmv),
       count(*) = (SELECT count(DISTINCT seller_key) FROM dw.fact_seller_monthly) AND sum(gmv) = (SELECT sum(gmv) FROM dw.fact_seller_monthly) FROM mart_acquisition.v_seller_scorecard
UNION ALL SELECT 'v_seller_by_channel: sum(sellers) = dim_seller rows (without Unknown); sum(gmv) = scorecard', 'mart_acquisition.v_seller_by_channel',
       (SELECT count(*) FROM dw.dim_seller WHERE seller_key <> -1) || ' / ' || (SELECT sum(gmv) FROM mart_acquisition.v_seller_scorecard), sum(sellers) || ' / ' || sum(gmv),
       sum(sellers) = (SELECT count(*) FROM dw.dim_seller WHERE seller_key <> -1) AND sum(gmv) = (SELECT sum(gmv) FROM mart_acquisition.v_seller_scorecard) FROM mart_acquisition.v_seller_by_channel

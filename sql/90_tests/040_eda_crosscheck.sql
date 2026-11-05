-- "EDA cross-check" (report only): compares the final warehouse with the numbers measured in the EDA (P1) on the full data set.
-- etl/run_tests.py stores these rows in etl_log.dq_check but they never fail the pipeline.
-- The comparison only makes sense when ALL source data has been loaded (99,441 orders, 8,000 MQL, 842 deals);
-- before that the rows say 'skipped' and count as matching.
WITH complete AS (
    SELECT (SELECT count(*) FROM oltp.orders) = 99441 AND (SELECT count(*) FROM crm.mql) = 8000 AND (SELECT count(*) FROM crm.closed_deals) = 842 AS ok),
v AS (
    SELECT 'EDA: sellers of funnel deals with a first sale = 380' AS check_name, 'dw.fact_lead_funnel' AS target_table, '380' AS expected,
           (SELECT sum(has_first_sale) FROM dw.fact_lead_funnel)::text AS actual,
           (SELECT sum(has_first_sale) FROM dw.fact_lead_funnel) = 380 AS match
    UNION ALL SELECT 'EDA: GMV (orders not Failed) is about 13.49 million BRL', 'dw.fact_order_item', '13.49 million',
           (SELECT round(sum(f.price) / 1e6, 3) FROM dw.fact_order_item f JOIN dw.dim_order_status s USING (order_status_key) WHERE s.status_group <> 'Failed')::text || ' million',
           (SELECT round(sum(f.price) / 1e6, 2) FROM dw.fact_order_item f JOIN dw.dim_order_status s USING (order_status_key) WHERE s.status_group <> 'Failed') = 13.49
    UNION ALL SELECT 'EDA: dim_customer has 96,339 rows (SCD2)', 'dw.dim_customer', '96339', (SELECT count(*) FROM dw.dim_customer)::text,
           (SELECT count(*) FROM dw.dim_customer) = 96339
    UNION ALL SELECT 'EDA: fact_seller_monthly has 36,583 rows (dense)', 'dw.fact_seller_monthly', '36583', (SELECT count(*) FROM dw.fact_seller_monthly)::text,
           (SELECT count(*) FROM dw.fact_seller_monthly) = 36583
    UNION ALL SELECT 'EDA: 842 closed deals (won)', 'dw.fact_lead_funnel', '842', (SELECT sum(is_won) FROM dw.fact_lead_funnel)::text,
           (SELECT sum(is_won) FROM dw.fact_lead_funnel) = 842)
SELECT v.check_name, v.target_table, v.expected, CASE WHEN c.ok THEN v.actual ELSE 'skipped (source not fully loaded yet; measured ' || v.actual || ')' END,
       NOT c.ok OR v.match
FROM v CROSS JOIN complete c

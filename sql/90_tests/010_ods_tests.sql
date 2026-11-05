-- ODS tests: row reconciliation staging = ods + rejected, and cleaning rules. Returns (check_name, target_table, expected, actual, passed).
WITH batches AS (
    SELECT load_batch_id AS b FROM staging.stg_orders UNION SELECT load_batch_id FROM staging.stg_customers
    UNION SELECT load_batch_id FROM staging.stg_order_items UNION SELECT load_batch_id FROM staging.stg_order_payments
    UNION SELECT load_batch_id FROM staging.stg_order_reviews UNION SELECT load_batch_id FROM staging.stg_sellers
    UNION SELECT load_batch_id FROM staging.stg_products UNION SELECT load_batch_id FROM staging.stg_geolocation
    UNION SELECT load_batch_id FROM staging.stg_product_category_name_translation UNION SELECT load_batch_id FROM staging.stg_mql
    UNION SELECT load_batch_id FROM staging.stg_closed_deals),
rej AS (SELECT job_name, count(*) AS n FROM etl_log.rejected_rows WHERE batch_id IN (SELECT b FROM batches) GROUP BY job_name),
recon AS (
    SELECT 'ods.orders' AS t, (SELECT count(*) FROM staging.stg_orders) AS stg, (SELECT count(*) FROM ods.orders) AS ods, 'ods.load_orders' AS job
    UNION ALL SELECT 'ods.customers', (SELECT count(*) FROM staging.stg_customers), (SELECT count(*) FROM ods.customers), 'ods.load_customers'
    UNION ALL SELECT 'ods.order_items', (SELECT count(*) FROM staging.stg_order_items), (SELECT count(*) FROM ods.order_items), 'ods.load_order_items'
    UNION ALL SELECT 'ods.order_payments', (SELECT count(*) FROM staging.stg_order_payments), (SELECT count(*) FROM ods.order_payments), 'ods.load_order_payments'
    UNION ALL SELECT 'ods.order_reviews', (SELECT count(*) FROM staging.stg_order_reviews), (SELECT count(*) FROM ods.order_reviews), 'ods.load_order_reviews'
    UNION ALL SELECT 'ods.sellers', (SELECT count(*) FROM staging.stg_sellers), (SELECT count(*) FROM ods.sellers), 'ods.load_sellers'
    UNION ALL SELECT 'ods.products', (SELECT count(*) FROM staging.stg_products), (SELECT count(*) FROM ods.products), 'ods.load_products'
    UNION ALL SELECT 'ods.category_translation', (SELECT count(*) FROM staging.stg_product_category_name_translation), (SELECT count(*) FROM ods.category_translation), 'ods.load_category_translation'
    UNION ALL SELECT 'ods.mql', (SELECT count(*) FROM staging.stg_mql), (SELECT count(*) FROM ods.mql), 'ods.load_mql'
    UNION ALL SELECT 'ods.closed_deals', (SELECT count(*) FROM staging.stg_closed_deals), (SELECT count(*) FROM ods.closed_deals), 'ods.load_closed_deals'
    -- geolocation: every staging point is either aggregated into a zip (sum of n_points) or rejected
    UNION ALL SELECT 'ods.geolocation_zip', (SELECT count(*) FROM staging.stg_geolocation), (SELECT coalesce(sum(n_points), 0) FROM ods.geolocation_zip), 'ods.load_geolocation_zip')
SELECT 'staging = ods + rejected' AS check_name, t AS target_table, stg::text AS expected, (ods + coalesce(r.n, 0))::text AS actual,
       stg = ods + coalesce(r.n, 0) AS passed
FROM recon LEFT JOIN rej r ON r.job_name = recon.job
UNION ALL
SELECT 'zip is exactly 5 digits', 'ods.customers', '0', count(*)::text, count(*) = 0 FROM ods.customers WHERE zip_code_prefix !~ '^[0-9]{5}$'
UNION ALL
SELECT 'zip is exactly 5 digits', 'ods.sellers', '0', count(*)::text, count(*) = 0 FROM ods.sellers WHERE zip_code_prefix !~ '^[0-9]{5}$'
UNION ALL
SELECT 'zip is exactly 5 digits', 'ods.geolocation_zip', '0', count(*)::text, count(*) = 0 FROM ods.geolocation_zip WHERE zip_code_prefix !~ '^[0-9]{5}$'
UNION ALL
SELECT 'city normalised (lower, unaccent, trim)', 'ods.customers', '0', count(*)::text, count(*) = 0 FROM ods.customers WHERE city <> ods.clean_city(city)
UNION ALL
SELECT 'city normalised (lower, unaccent, trim)', 'ods.geolocation_zip', '0', count(*)::text, count(*) = 0 FROM ods.geolocation_zip WHERE city <> ods.clean_city(city)
UNION ALL
SELECT 'coordinates inside Brazil bbox', 'ods.geolocation_zip', '0', count(*)::text, count(*) = 0
FROM ods.geolocation_zip WHERE NOT (latitude BETWEEN -33.75 AND 5.27 AND longitude BETWEEN -73.99 AND -34.79)
UNION ALL
SELECT 'no empty product category', 'ods.products', '0', count(*)::text, count(*) = 0 FROM ods.products WHERE nullif(trim(product_category_name), '') IS NULL
UNION ALL
SELECT 'no *_lenght column left', 'ods.products', '0', count(*)::text, count(*) = 0
FROM information_schema.columns WHERE table_schema = 'ods' AND position('lenght' in column_name) > 0
UNION ALL
SELECT 'installments >= 1', 'ods.order_payments', '0', count(*)::text, count(*) = 0 FROM ods.order_payments WHERE payment_installments < 1
UNION ALL
SELECT 'dq_flag_count = cardinality(dq_flags)', 'ods.orders', '0', count(*)::text, count(*) = 0 FROM ods.orders WHERE dq_flag_count <> cardinality(dq_flags)
UNION ALL
SELECT 'mql origin never null', 'ods.mql', '0', count(*)::text, count(*) = 0 FROM ods.mql WHERE origin IS NULL
UNION ALL
SELECT 'every order has a customer in ods.customer_map', 'ods.orders', '0', count(*)::text, count(*) = 0
FROM ods.orders o WHERE NOT EXISTS (SELECT 1 FROM ods.customer_map m WHERE m.customer_id = o.customer_id)
UNION ALL
SELECT 'seeds loaded (6 ref tables not empty)', 'ods.ref_*', '6', (
    (SELECT (count(*) > 0)::int FROM ods.ref_state_region) + (SELECT (count(*) > 0)::int FROM ods.ref_category_group)
  + (SELECT (count(*) > 0)::int FROM ods.ref_lead_origin_group) + (SELECT (count(*) > 0)::int FROM ods.ref_payment_type)
  + (SELECT (count(*) > 0)::int FROM ods.ref_order_status) + (SELECT (count(*) > 0)::int FROM ods.ref_category_translation_extra))::text,
  ((SELECT (count(*) > 0)::int FROM ods.ref_state_region) + (SELECT (count(*) > 0)::int FROM ods.ref_category_group)
  + (SELECT (count(*) > 0)::int FROM ods.ref_lead_origin_group) + (SELECT (count(*) > 0)::int FROM ods.ref_payment_type)
  + (SELECT (count(*) > 0)::int FROM ods.ref_order_status) + (SELECT (count(*) > 0)::int FROM ods.ref_category_translation_extra)) = 6

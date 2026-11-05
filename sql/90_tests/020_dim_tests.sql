-- Dimension tests (DW_DESIGN section 13). Returns (check_name, target_table, expected, actual, passed).
WITH unknown_rows AS (
    SELECT 'dim_date' AS t, count(*) AS n FROM dw.dim_date WHERE date_key = -1
    UNION ALL SELECT 'dim_geography', count(*) FROM dw.dim_geography WHERE geography_key = -1
    UNION ALL SELECT 'dim_customer', count(*) FROM dw.dim_customer WHERE customer_key = -1
    UNION ALL SELECT 'dim_seller', count(*) FROM dw.dim_seller WHERE seller_key = -1
    UNION ALL SELECT 'dim_product', count(*) FROM dw.dim_product WHERE product_key = -1
    UNION ALL SELECT 'dim_order_status', count(*) FROM dw.dim_order_status WHERE order_status_key = -1
    UNION ALL SELECT 'dim_payment_type', count(*) FROM dw.dim_payment_type WHERE payment_type_key = -1
    UNION ALL SELECT 'dim_lead_origin', count(*) FROM dw.dim_lead_origin WHERE lead_origin_key = -1
    UNION ALL SELECT 'dim_lead_profile', count(*) FROM dw.dim_lead_profile WHERE lead_profile_key = -1
    UNION ALL SELECT 'dim_sales_rep', count(*) FROM dw.dim_sales_rep WHERE sales_rep_key = -1),
cust AS (   -- SCD2 helper
    SELECT customer_unique_id AS uid, effective_from AS f, effective_to AS t, is_current,
           lead(effective_from) OVER (PARTITION BY customer_unique_id ORDER BY effective_from) AS next_from
    FROM dw.dim_customer WHERE customer_key <> -1)
SELECT 'exactly one Unknown row (key -1)' AS check_name, 'dw.' || t AS target_table, '1' AS expected, n::text AS actual, n = 1 AS passed FROM unknown_rows
UNION ALL
SELECT 'dim_date covers 2016-01-01..2020-12-31 (1827 days + Unknown)', 'dw.dim_date', '1828', count(*)::text, count(*) = 1828 FROM dw.dim_date
UNION ALL
SELECT 'dim_date: 3 Black Fridays in 2016-2018', 'dw.dim_date', '3', count(*)::text, count(*) = 3 FROM dw.dim_date WHERE is_black_friday AND year BETWEEN 2016 AND 2018
UNION ALL
SELECT 'dim_date: Black Friday dates are 2016-11-25, 2017-11-24, 2018-11-23', 'dw.dim_date', '3',
       count(*)::text, count(*) = 3 FROM dw.dim_date WHERE full_date IN (DATE '2016-11-25', DATE '2017-11-24', DATE '2018-11-23') AND is_black_friday
UNION ALL
SELECT 'dim_geography: every customer / seller zip has a row', 'dw.dim_geography', '0', count(*)::text, count(*) = 0
FROM (SELECT zip_code_prefix FROM ods.customers UNION SELECT zip_code_prefix FROM ods.sellers) z
WHERE z.zip_code_prefix IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dw.dim_geography g WHERE g.zip_code_prefix = z.zip_code_prefix)
UNION ALL
SELECT 'dim_geography: rows = distinct zips of geolocation + customers + sellers (+ Unknown)', 'dw.dim_geography',
       ((SELECT count(*) FROM (SELECT zip_code_prefix FROM ods.geolocation_zip UNION SELECT zip_code_prefix FROM ods.customers
                               UNION SELECT zip_code_prefix FROM ods.sellers) u WHERE zip_code_prefix IS NOT NULL) + 1)::text,
       (SELECT count(*) FROM dw.dim_geography)::text,
       (SELECT count(*) FROM (SELECT zip_code_prefix FROM ods.geolocation_zip UNION SELECT zip_code_prefix FROM ods.customers
                              UNION SELECT zip_code_prefix FROM ods.sellers) u WHERE zip_code_prefix IS NOT NULL) + 1 = (SELECT count(*) FROM dw.dim_geography)
UNION ALL
SELECT 'dim_geography: known state has region (no Unknown region)', 'dw.dim_geography', '0', count(*)::text, count(*) = 0
FROM dw.dim_geography WHERE geography_key <> -1 AND region = 'Unknown'
UNION ALL
SELECT 'dim_geography: hierarchy 5 regions', 'dw.dim_geography', '5', count(DISTINCT region)::text, count(DISTINCT region) = 5
FROM dw.dim_geography WHERE geography_key <> -1
UNION ALL
SELECT 'dim_customer: one current version per customer_unique_id', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM (SELECT customer_unique_id FROM dw.dim_customer WHERE customer_key <> -1 GROUP BY 1 HAVING count(*) FILTER (WHERE is_current) <> 1) x
UNION ALL
SELECT 'dim_customer: no overlapping validity ranges', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM cust WHERE next_from IS NOT NULL AND t >= next_from
UNION ALL
SELECT 'dim_customer: ranges are contiguous (effective_to + 1 = next effective_from)', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM cust WHERE next_from IS NOT NULL AND t + 1 <> next_from
UNION ALL
SELECT 'dim_customer: current version ends 9999-12-31 and only the current one does', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM cust WHERE (is_current AND t <> DATE '9999-12-31') OR (NOT is_current AND t = DATE '9999-12-31')
UNION ALL
SELECT 'dim_customer: every customer_unique_id of ods.customers is present', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM (SELECT DISTINCT customer_unique_id FROM ods.customers) c WHERE NOT EXISTS (SELECT 1 FROM dw.dim_customer d WHERE d.customer_unique_id = c.customer_unique_id)
UNION ALL
SELECT 'dim_customer: every order maps to exactly one version at its purchase date', 'dw.dim_customer', '0', count(*)::text, count(*) = 0
FROM (SELECT o.order_id FROM ods.orders o JOIN ods.customers c USING (customer_id)
      LEFT JOIN dw.dim_customer d ON d.customer_unique_id = c.customer_unique_id
           AND o.order_purchase_timestamp::date BETWEEN d.effective_from AND d.effective_to
      GROUP BY o.order_id HAVING count(d.customer_key) <> 1) x
UNION ALL
SELECT 'dim_seller: every seller of ods.sellers and every deal seller is present', 'dw.dim_seller', '0', count(*)::text, count(*) = 0
FROM (SELECT seller_id FROM ods.sellers UNION SELECT seller_id FROM ods.closed_deals) s
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_seller d WHERE d.seller_id = s.seller_id)
UNION ALL
SELECT 'dim_seller: is_from_funnel rows = closed deals', 'dw.dim_seller', (SELECT count(*) FROM ods.closed_deals)::text,
       count(*)::text, count(*) = (SELECT count(*) FROM ods.closed_deals) FROM dw.dim_seller WHERE is_from_funnel
UNION ALL
SELECT 'dim_seller: not-from-funnel sellers have channel Not from funnel', 'dw.dim_seller', '0', count(*)::text, count(*) = 0
FROM dw.dim_seller WHERE seller_key <> -1 AND ((NOT is_from_funnel) <> (acquisition_origin = 'not_from_funnel'))
UNION ALL
SELECT 'dim_product: one row per ods.products (+ Unknown)', 'dw.dim_product', ((SELECT count(*) FROM ods.products) + 1)::text,
       count(*)::text, count(*) = (SELECT count(*) FROM ods.products) + 1 FROM dw.dim_product
UNION ALL
SELECT 'dim_product: every product has a category group from the 13-group seed', 'dw.dim_product', '0', count(*)::text, count(*) = 0
FROM dw.dim_product WHERE product_key <> -1 AND (category_group IS NULL OR category_group NOT IN (SELECT category_group FROM ods.ref_category_group))
UNION ALL
SELECT 'dim_product: size_class in (S, M, L, XL, Unknown)', 'dw.dim_product', '0', count(*)::text, count(*) = 0
FROM dw.dim_product WHERE size_class NOT IN ('S', 'M', 'L', 'XL', 'Unknown')
UNION ALL
SELECT 'dim_product: every product has an English category name', 'dw.dim_product', '0', count(*)::text, count(*) = 0
FROM dw.dim_product WHERE category_name_en IS NULL
UNION ALL
SELECT 'dim_order_status: 8 statuses + Unknown', 'dw.dim_order_status', '9', count(*)::text, count(*) = 9 FROM dw.dim_order_status
UNION ALL
SELECT 'dim_order_status: every order status of ods.orders is known', 'dw.dim_order_status', '0', count(*)::text, count(*) = 0
FROM (SELECT DISTINCT order_status FROM ods.orders) s WHERE NOT EXISTS (SELECT 1 FROM dw.dim_order_status d WHERE d.order_status = s.order_status)
UNION ALL
SELECT 'dim_payment_type: 5 types + Unknown', 'dw.dim_payment_type', '6', count(*)::text, count(*) = 6 FROM dw.dim_payment_type
UNION ALL
SELECT 'dim_payment_type: every payment type of ods.order_payments is known', 'dw.dim_payment_type', '0', count(*)::text, count(*) = 0
FROM (SELECT DISTINCT payment_type FROM ods.order_payments) s WHERE NOT EXISTS (SELECT 1 FROM dw.dim_payment_type d WHERE d.payment_type = s.payment_type)
UNION ALL
SELECT 'dim_lead_origin: 10 origins + Unknown; unknown is its own channel group', 'dw.dim_lead_origin', '11', count(*)::text,
       count(*) = 11 AND bool_and(channel_group = 'Unknown') FILTER (WHERE origin = 'unknown') FROM dw.dim_lead_origin
UNION ALL
SELECT 'dim_lead_origin: every MQL origin is known', 'dw.dim_lead_origin', '0', count(*)::text, count(*) = 0
FROM (SELECT DISTINCT origin FROM ods.mql) s WHERE NOT EXISTS (SELECT 1 FROM dw.dim_lead_origin d WHERE d.origin = s.origin)
UNION ALL
SELECT 'dim_lead_profile: one row per distinct deal profile (+ Unknown)', 'dw.dim_lead_profile',
       ((SELECT count(*) FROM (SELECT DISTINCT business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin, average_stock
                               FROM ods.closed_deals) d) + 1)::text, count(*)::text,
       count(*) = (SELECT count(*) FROM (SELECT DISTINCT business_segment, lead_type, lead_behaviour_profile, business_type, has_company, has_gtin,
                                                         average_stock FROM ods.closed_deals) d) + 1 FROM dw.dim_lead_profile
UNION ALL
SELECT 'dim_sales_rep: SDR and SR ids of ods.closed_deals are all present', 'dw.dim_sales_rep', '0', count(*)::text, count(*) = 0
FROM (SELECT sdr_id AS id, 'SDR' AS r FROM ods.closed_deals WHERE sdr_id IS NOT NULL UNION SELECT sr_id, 'SR' FROM ods.closed_deals WHERE sr_id IS NOT NULL) s
WHERE NOT EXISTS (SELECT 1 FROM dw.dim_sales_rep d WHERE d.rep_id = s.id AND d.rep_role = s.r)
UNION ALL
SELECT 'role-playing date views exist (11)', 'dw.v_dim_*_date', '11', count(*)::text, count(*) = 11
FROM information_schema.views WHERE table_schema = 'dw' AND table_name LIKE 'v_dim\_%\_date'
UNION ALL
SELECT 'dim_geography: rows = distinct zips of STAGING geolocation (all points, even outside bbox) + customers + sellers (+ Unknown)', 'dw.dim_geography',
       (SELECT count(*) + 1 FROM (SELECT ods.clean_zip(geolocation_zip_code_prefix) AS z FROM staging.stg_geolocation
                                  UNION SELECT zip_code_prefix FROM ods.customers UNION SELECT zip_code_prefix FROM ods.sellers) u WHERE z IS NOT NULL)::text,
       (SELECT count(*) FROM dw.dim_geography)::text,
       (SELECT count(*) + 1 FROM (SELECT ods.clean_zip(geolocation_zip_code_prefix) AS z FROM staging.stg_geolocation
                                  UNION SELECT zip_code_prefix FROM ods.customers UNION SELECT zip_code_prefix FROM ods.sellers) u WHERE z IS NOT NULL)
       = (SELECT count(*) FROM dw.dim_geography)
UNION ALL
SELECT 'dim_geography: latitude/longitude are NULL exactly for zips without any in-bbox coordinate (decision e)', 'dw.dim_geography',
       (SELECT count(*) FROM (SELECT zip_code_prefix FROM ods.customers UNION SELECT zip_code_prefix FROM ods.sellers
                              UNION SELECT ods.clean_zip(geolocation_zip_code_prefix) FROM staging.stg_geolocation) u
        WHERE zip_code_prefix IS NOT NULL AND NOT EXISTS (SELECT 1 FROM staging.stg_geolocation s WHERE ods.clean_zip(s.geolocation_zip_code_prefix) = u.zip_code_prefix
                       AND s.geolocation_lat BETWEEN -33.75 AND 5.27 AND s.geolocation_lng BETWEEN -73.99 AND -34.79))::text,
       (SELECT count(*) FROM dw.dim_geography WHERE geography_key <> -1 AND latitude IS NULL)::text,
       (SELECT count(*) FROM (SELECT zip_code_prefix FROM ods.customers UNION SELECT zip_code_prefix FROM ods.sellers
                              UNION SELECT ods.clean_zip(geolocation_zip_code_prefix) FROM staging.stg_geolocation) u
        WHERE zip_code_prefix IS NOT NULL AND NOT EXISTS (SELECT 1 FROM staging.stg_geolocation s WHERE ods.clean_zip(s.geolocation_zip_code_prefix) = u.zip_code_prefix
                       AND s.geolocation_lat BETWEEN -33.75 AND 5.27 AND s.geolocation_lng BETWEEN -73.99 AND -34.79))
       = (SELECT count(*) FROM dw.dim_geography WHERE geography_key <> -1 AND latitude IS NULL)
UNION ALL
SELECT 'dim_geography: latitude and longitude are NULL together', 'dw.dim_geography', '0', count(*)::text, count(*) = 0
FROM dw.dim_geography WHERE (latitude IS NULL) <> (longitude IS NULL)

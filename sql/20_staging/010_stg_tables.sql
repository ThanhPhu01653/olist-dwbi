-- setup: required
-- Staging = raw copy of every source table + load_batch_id + loaded_at. No cleaning, no constraints.
-- Tables accumulate across incremental batches; a full extract truncates and reloads them.
DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT * FROM (VALUES
            ('oltp', 'orders',                            'order_id'),
            ('oltp', 'order_items',                       'order_id'),
            ('oltp', 'order_payments',                    'order_id'),
            ('oltp', 'order_reviews',                     'order_id'),
            ('oltp', 'customers',                         'customer_id'),
            ('oltp', 'sellers',                           'seller_id'),
            ('oltp', 'products',                          'product_id'),
            ('oltp', 'geolocation',                       'geolocation_zip_code_prefix'),
            ('oltp', 'product_category_name_translation', 'product_category_name'),
            ('crm',  'mql',                               'mql_id'),
            ('crm',  'closed_deals',                      'mql_id')
        ) AS t(src_schema, src_table, key_col)
    LOOP
        -- LIKE copies column names, types and NOT NULL, but no keys / identity / defaults.
        EXECUTE format('CREATE TABLE IF NOT EXISTS staging.stg_%I (LIKE %I.%I)', r.src_table, r.src_schema, r.src_table);
        EXECUTE format('ALTER TABLE staging.stg_%I ADD COLUMN IF NOT EXISTS load_batch_id bigint', r.src_table);
        EXECUTE format('ALTER TABLE staging.stg_%I ADD COLUMN IF NOT EXISTS loaded_at timestamptz NOT NULL DEFAULT now()', r.src_table);
        EXECUTE format('CREATE INDEX IF NOT EXISTS ix_stg_%s_batch ON staging.stg_%I (load_batch_id)', r.src_table, r.src_table);
        EXECUTE format('CREATE INDEX IF NOT EXISTS ix_stg_%s_key ON staging.stg_%I (%I)', r.src_table, r.src_table, r.key_col);
        EXECUTE format('COMMENT ON TABLE staging.stg_%I IS %L', r.src_table,
                       'Bản sao thô của ' || r.src_schema || '.' || r.src_table || ' (kèm load_batch_id, loaded_at); chưa làm sạch');
    END LOOP;
END $$;

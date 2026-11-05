CREATE OR REPLACE PROCEDURE ods.load_closed_deals(p_batch_id bigint, INOUT p_read bigint DEFAULT 0,
                                                  INOUT p_inserted bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM etl_log.rejected_rows WHERE batch_id = p_batch_id AND job_name = 'ods.load_closed_deals';
    CALL ods.take_orphans('ods.load_closed_deals', p_batch_id);
    SELECT count(*) INTO p_read FROM staging.stg_closed_deals WHERE load_batch_id = p_batch_id;
    INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record)
    SELECT p_batch_id, 'ods.load_closed_deals', 'staging.stg_closed_deals', 'orphan: mql_id not in ods.mql',
           to_jsonb(s) - 'load_batch_id' - 'loaded_at'
    FROM staging.stg_closed_deals s
    WHERE (s.load_batch_id = p_batch_id OR EXISTS (SELECT 1 FROM tmp_orphans t WHERE t.job = 'ods.load_closed_deals' AND t.rec ->> 'mql_id' = s.mql_id::text)) AND NOT EXISTS (SELECT 1 FROM ods.mql m WHERE m.mql_id = s.mql_id);
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
    WHERE (s.load_batch_id = p_batch_id OR EXISTS (SELECT 1 FROM tmp_orphans t WHERE t.job = 'ods.load_closed_deals' AND t.rec ->> 'mql_id' = s.mql_id::text))
    ON CONFLICT (mql_id) DO NOTHING;
    GET DIAGNOSTICS p_inserted = ROW_COUNT;
END $$;

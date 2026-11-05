-- setup: required
-- Refresh of the MATERIALIZED views of the marts (plain views are always current). Called by etl/run_pipeline.py between fact and tests.
-- Returns (rows_read = rows in all materialized views after refresh, inserted/updated/rejected = 0).
CREATE OR REPLACE PROCEDURE dw.refresh_marts(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                             INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
DECLARE
    mv text;
    n bigint;
BEGIN
    p_read := 0;
    -- order matters: v_seller_by_channel reads v_seller_scorecard
    FOREACH mv IN ARRAY ARRAY['mart_cx.v_customer_rfm', 'mart_cx.v_customer_cohort', 'mart_acquisition.v_seller_scorecard', 'mart_acquisition.v_seller_by_channel']
    LOOP
        EXECUTE 'REFRESH MATERIALIZED VIEW ' || mv;
        EXECUTE 'SELECT count(*) FROM ' || mv INTO n;
        p_read := p_read + n;
    END LOOP;
    p_inserted := 0; p_updated := 0; p_rejected := 0;
END $$;

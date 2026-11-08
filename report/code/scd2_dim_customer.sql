CREATE OR REPLACE PROCEDURE dw.load_dim_customer(p_batch_id bigint, INOUT p_read bigint DEFAULT 0, INOUT p_inserted bigint DEFAULT 0,
                                                 INOUT p_updated bigint DEFAULT 0, INOUT p_rejected bigint DEFAULT 0)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT count(DISTINCT customer_unique_id) INTO p_read FROM ods.customers WHERE etl_batch_id = p_batch_id;
    CREATE TEMP TABLE tmp_cust_ver ON COMMIT DROP AS
    WITH aff AS (SELECT DISTINCT customer_unique_id AS uid FROM ods.customers WHERE etl_batch_id = p_batch_id),
    ev AS (
        SELECT c.customer_unique_id AS uid, c.zip_code_prefix AS zip, c.city, c.state_code AS st, o.order_purchase_timestamp AS ts, o.order_id
        FROM ods.customers c JOIN aff ON aff.uid = c.customer_unique_id LEFT JOIN ods.orders o ON o.customer_id = c.customer_id),
    ord AS (
        SELECT ev.*, lag(zip) OVER w AS pz, row_number() OVER w AS rn
        FROM ev WINDOW w AS (PARTITION BY uid ORDER BY ts NULLS FIRST, order_id)),
    chg AS (   -- opening events; if several open on the same day keep the last one
        SELECT ord.*, row_number() OVER (PARTITION BY uid, coalesce(ts::date, DATE '1900-01-01') ORDER BY rn DESC) AS dup
        FROM ord WHERE rn = 1 OR zip IS DISTINCT FROM pz),
    stt AS (SELECT uid, zip, city, st, ts::date AS d, rn FROM chg WHERE dup = 1),
    ver AS (
        SELECT uid, zip, city, st, row_number() OVER w AS vn,
               CASE WHEN row_number() OVER w = 1 THEN DATE '1900-01-01' ELSE d END AS eff_from, lead(d) OVER w AS nxt
        FROM stt WINDOW w AS (PARTITION BY uid ORDER BY rn))
    SELECT uid, zip, city, st, vn, eff_from, coalesce(nxt - 1, DATE '9999-12-31') AS eff_to, (nxt IS NULL) AS is_cur FROM ver;

    INSERT INTO dw.dim_customer (customer_unique_id, zip_code_prefix, city, state_code, geography_key, effective_from, effective_to, is_current, version_no)
    SELECT v.uid, v.zip, v.city, v.st, coalesce(g.geography_key, -1), v.eff_from, v.eff_to, v.is_cur, v.vn
    FROM tmp_cust_ver v LEFT JOIN dw.dim_geography g ON g.zip_code_prefix = v.zip
    WHERE NOT EXISTS (SELECT 1 FROM dw.dim_customer d WHERE d.customer_unique_id = v.uid AND d.effective_from = v.eff_from)
    ORDER BY v.uid, v.eff_from;                          -- fixed order => the same surrogate keys on every rebuild
    GET DIAGNOSTICS p_inserted = ROW_COUNT;

    UPDATE dw.dim_customer d
    SET effective_to = v.eff_to, is_current = v.is_cur, version_no = v.vn, dw_updated_at = now()
    FROM tmp_cust_ver v
    WHERE d.customer_unique_id = v.uid AND d.effective_from = v.eff_from
      AND (d.effective_to, d.is_current, d.version_no) IS DISTINCT FROM (v.eff_to, v.is_cur, v.vn);
    GET DIAGNOSTICS p_updated = ROW_COUNT;
    p_rejected := 0;
END $$;

CREATE OR REPLACE PROCEDURE ods.take_orphans(p_job text, p_batch_id bigint) LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS tmp_orphans (job text, rec jsonb) ON COMMIT DROP;
    DELETE FROM tmp_orphans WHERE job = p_job;
    INSERT INTO tmp_orphans SELECT job_name, record FROM etl_log.rejected_rows WHERE job_name = p_job AND reason LIKE 'orphan:%' AND batch_id <> p_batch_id;
    DELETE FROM etl_log.rejected_rows WHERE job_name = p_job AND reason LIKE 'orphan:%' AND batch_id <> p_batch_id;
END $$;

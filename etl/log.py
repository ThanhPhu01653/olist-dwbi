"""Write ETL monitoring records to etl_log.* (own autocommit connection, so logs survive rollbacks)."""
from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass

import pandas as pd
from psycopg2.extras import Json, execute_values
from sqlalchemy import text
from sqlalchemy.engine import Engine


def new_batch_id(engine: Engine) -> int:
    with engine.begin() as conn:
        return conn.execute(text("SELECT nextval('etl_log.batch_seq')")).scalar_one()


@dataclass
class JobRun:
    engine: Engine
    run_id: int
    batch_id: int
    job_name: str
    rows_read: int = 0
    rows_inserted: int = 0
    rows_updated: int = 0
    rows_rejected: int = 0
    message: str | None = None

    def log_rejected(self, source_table: str, reason: str, rows: pd.DataFrame) -> None:
        """Store rejected source rows (one jsonb record each) in etl_log.rejected_rows."""
        if rows.empty:
            return
        records = [
            (self.batch_id, self.job_name, source_table, reason, Json(json.loads(r)))
            for r in rows.to_json(orient="records", lines=True).splitlines()
        ]
        raw = self.engine.raw_connection()
        try:
            with raw.cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO etl_log.rejected_rows (batch_id, job_name, source_table, reason, record) VALUES %s",
                    records,
                )
            raw.commit()
        finally:
            raw.close()
        self.rows_rejected += len(records)


@contextmanager
def job_run(engine: Engine, batch_id: int, job_name: str, layer: str, target_table: str | None = None):
    """Context manager: inserts a 'running' row, then closes it as 'success' or 'failed'."""
    with engine.begin() as conn:
        run_id = conn.execute(
            text(
                "INSERT INTO etl_log.job_run (batch_id, job_name, layer, target_table) "
                "VALUES (:b, :j, :l, :t) RETURNING run_id"
            ),
            {"b": batch_id, "j": job_name, "l": layer, "t": target_table},
        ).scalar_one()
    run = JobRun(engine, run_id, batch_id, job_name)
    status, error = "success", None
    try:
        yield run
    except BaseException as exc:  # also log KeyboardInterrupt, then re-raise
        status, error = "failed", f"{type(exc).__name__}: {exc}"
        raise
    finally:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE etl_log.job_run SET finished_at = now(), status = :s, rows_read = :r, "
                    "rows_inserted = :i, rows_updated = :u, rows_rejected = :x, message = :m WHERE run_id = :id"
                ),
                {
                    "s": status, "r": run.rows_read, "i": run.rows_inserted, "u": run.rows_updated,
                    "x": run.rows_rejected, "m": error or run.message, "id": run_id,
                },
            )

"""Call SQL load procedures (ods.load_*, dw.load_*) and record each call in etl_log.job_run."""
from __future__ import annotations

from sqlalchemy.engine import Engine

from .log import job_run


def call_procedures(engine: Engine, batch_id: int, layer: str, procs: list[tuple[str, str]], counters: int = 3) -> list[dict]:
    """procs: [(procedure name, target table)]. Procedures take (batch_id, INOUT counters...) and return them:
    counters=3 -> (read, inserted, rejected) for ods.*;  counters=4 -> (read, inserted, updated, rejected) for dw.*.
    All calls run in one transaction: any failure rolls the whole layer back."""
    out = []
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for name, target in procs:
            with job_run(engine, batch_id, name, layer, target) as run:
                cur.execute(f"CALL {name}(%s{', 0' * counters})", (batch_id,))
                row = cur.fetchone()
                if counters == 4:
                    read, inserted, updated, rejected = row
                else:
                    (read, inserted, rejected), updated = row, 0
                run.rows_read, run.rows_inserted, run.rows_updated, run.rows_rejected = read, inserted, updated, rejected
                out.append({"proc": name, "read": read, "inserted": inserted, "updated": updated, "rejected": rejected})
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return out

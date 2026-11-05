"""Call SQL load procedures (ods.load_*, dw.load_*) and record each call in etl_log.job_run."""
from __future__ import annotations

from sqlalchemy.engine import Engine

from .log import job_run


def call_procedures(engine: Engine, batch_id: int, layer: str, procs: list[tuple[str, str]], extra_args: str = "") -> list[dict]:
    """procs: [(procedure name, target table)]. Each procedure has signature (batch_id, INOUT read, INOUT inserted, INOUT rejected)
    and returns those three counters. All calls run in one transaction: any failure rolls the whole layer back."""
    out = []
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for name, target in procs:
            with job_run(engine, batch_id, name, layer, target) as run:
                cur.execute(f"CALL {name}(%s, 0, 0, 0)", (batch_id,))
                read, inserted, rejected = cur.fetchone()
                run.rows_read, run.rows_inserted, run.rows_rejected = read, inserted, rejected
                out.append({"proc": name, "read": read, "inserted": inserted, "rejected": rejected})
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return out

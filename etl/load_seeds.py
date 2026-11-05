"""Load seeds/*.csv into the ods.ref_* tables (small tables: TRUNCATE + COPY, idempotent)."""
from __future__ import annotations

import io

import pandas as pd
from sqlalchemy.engine import Engine

from . import config
from .log import job_run

SEEDS_DIR = config.ROOT / "seeds"
SEEDS = {
    "state_region.csv": "ods.ref_state_region",
    "category_translation_extra.csv": "ods.ref_category_translation_extra",
    "category_group.csv": "ods.ref_category_group",
    "lead_origin_group.csv": "ods.ref_lead_origin_group",
    "payment_type.csv": "ods.ref_payment_type",
    "order_status.csv": "ods.ref_order_status",
}


def load_seeds(engine: Engine, batch_id: int) -> dict[str, int]:
    counts = {}
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        for fname, table in SEEDS.items():
            with job_run(engine, batch_id, f"seeds.{fname}", "ods", table) as run:
                df = pd.read_csv(SEEDS_DIR / fname, dtype=str, keep_default_na=False)
                cur.execute(f"TRUNCATE {table}")
                buf = io.StringIO()
                df.to_csv(buf, index=False, header=False, lineterminator="\n")
                buf.seek(0)
                cur.copy_expert(f"COPY {table} ({', '.join(df.columns)}) FROM STDIN WITH (FORMAT csv)", buf)
                run.rows_read = run.rows_inserted = counts[table] = len(df)
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()
    return counts

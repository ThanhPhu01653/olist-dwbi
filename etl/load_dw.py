"""Load the warehouse dimensions (full reset or incremental upsert). Facts are added in P4."""
from __future__ import annotations

from sqlalchemy.engine import Engine

from .build_dim_date import build_dim_date
from .procs import call_procedures

DIM_PROCS = [
    ("dw.load_dim_geography", "dw.dim_geography"),
    ("dw.load_dim_customer", "dw.dim_customer"),     # after geography (geography_key lookup)
    ("dw.load_dim_seller", "dw.dim_seller"),         # after geography
    ("dw.load_dim_product", "dw.dim_product"),
    ("dw.load_dim_order_status", "dw.dim_order_status"),
    ("dw.load_dim_payment_type", "dw.dim_payment_type"),
    ("dw.load_dim_lead_origin", "dw.dim_lead_origin"),
    ("dw.load_dim_lead_profile", "dw.dim_lead_profile"),
    ("dw.load_dim_sales_rep", "dw.dim_sales_rep"),
]


def load_dimensions(engine: Engine, batch_id: int, mode: str) -> dict:
    if mode == "full":
        with engine.begin() as conn:
            conn.exec_driver_sql("CALL dw.reset_dims()")
    n_date = build_dim_date(engine, batch_id)
    res = call_procedures(engine, batch_id, "dw", DIM_PROCS, counters=4)
    return {"dim_date": n_date, "inserted": sum(r["inserted"] for r in res), "updated": sum(r["updated"] for r in res)}

"""Load the warehouse dimensions (full reset or incremental upsert) and the facts."""
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

# order matters: order_item -> payment -> fulfillment -> review (needs fulfillment.is_late) -> seller.first_sale_date -> funnel -> seller monthly
FACT_PROCS = [
    ("dw.load_fact_order_item", "dw.fact_order_item"),
    ("dw.load_fact_payment", "dw.fact_payment"),
    ("dw.load_fact_order_fulfillment", "dw.fact_order_fulfillment"),
    ("dw.load_fact_review", "dw.fact_review"),
    ("dw.load_dim_seller_first_sale", "dw.dim_seller"),
    ("dw.load_fact_lead_funnel", "dw.fact_lead_funnel"),
    ("dw.load_fact_seller_monthly", "dw.fact_seller_monthly"),
]


def load_facts(engine: Engine, batch_id: int) -> dict:
    res = call_procedures(engine, batch_id, "dw", FACT_PROCS, counters=4)
    return {"inserted": sum(r["inserted"] for r in res), "updated": sum(r["updated"] for r in res)}


def load_dimensions(engine: Engine, batch_id: int, mode: str) -> dict:
    if mode == "full":
        with engine.begin() as conn:
            conn.exec_driver_sql("CALL dw.reset_dims()")
    n_date = build_dim_date(engine, batch_id)
    res = call_procedures(engine, batch_id, "dw", DIM_PROCS, counters=4)
    return {"dim_date": n_date, "inserted": sum(r["inserted"] for r in res), "updated": sum(r["updated"] for r in res)}

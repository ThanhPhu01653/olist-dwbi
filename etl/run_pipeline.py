"""Orchestrate the warehouse pipeline:  python -m etl.run_pipeline --mode full|incremental

One batch_id per run; every stage writes etl_log.job_run and the whole run is one 'pipeline.<mode>' row. The first error stops the
run: the failing job and the pipeline row get status 'failed' with the message, the exit code is 1.
    extract (oltp/crm -> staging) -> seeds -> ods -> dim -> fact -> tests -> snapshot (etl_log.batch_metrics) -> export_powerbi
Data marts (P6) will be added between fact and tests. --no-export skips the CSV export (used while replaying many batches).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time

from sqlalchemy import text

from . import config
from .db import get_engine
from .extract import extract
from .load_dw import load_dimensions, load_facts
from .load_seeds import load_seeds
from .log import job_run, new_batch_id
from .procs import call_procedures
from .run_tests import run_tests

# parents first (FK checks inside the procedures look at already loaded ODS rows)
ODS_PROCS = [
    ("ods.load_category_translation", "ods.category_translation"),
    ("ods.load_products", "ods.products"),
    ("ods.load_sellers", "ods.sellers"),
    ("ods.load_geolocation_zip", "ods.geolocation_zip"),
    ("ods.load_customers", "ods.customers"),
    ("ods.load_orders", "ods.orders"),
    ("ods.load_order_items", "ods.order_items"),
    ("ods.load_order_payments", "ods.order_payments"),
    ("ods.load_order_reviews", "ods.order_reviews"),
    ("ods.load_mql", "ods.mql"),
    ("ods.load_closed_deals", "ods.closed_deals"),
]

SNAPSHOT_SQL = """
INSERT INTO etl_log.batch_metrics (batch_id, mode, orders, order_items, gmv, mql, deals_won, sellers_with_sale, customers, customer_versions, sellers)
SELECT :b, :m,
       (SELECT count(*) FROM dw.fact_order_fulfillment), (SELECT count(*) FROM dw.fact_order_item),
       (SELECT coalesce(sum(f.price), 0) FROM dw.fact_order_item f JOIN dw.dim_order_status s USING (order_status_key) WHERE s.status_group <> 'Failed'),
       (SELECT count(*) FROM dw.fact_lead_funnel), (SELECT coalesce(sum(is_won), 0) FROM dw.fact_lead_funnel),
       (SELECT coalesce(sum(has_first_sale), 0) FROM dw.fact_lead_funnel),
       (SELECT count(DISTINCT customer_unique_id) FROM dw.dim_customer WHERE customer_key <> -1), (SELECT count(*) FROM dw.dim_customer WHERE customer_key <> -1),
       (SELECT count(*) FROM dw.dim_seller WHERE seller_key <> -1)
ON CONFLICT (batch_id) DO UPDATE SET taken_at = now(), mode = EXCLUDED.mode, orders = EXCLUDED.orders, order_items = EXCLUDED.order_items, gmv = EXCLUDED.gmv,
    mql = EXCLUDED.mql, deals_won = EXCLUDED.deals_won, sellers_with_sale = EXCLUDED.sellers_with_sale, customers = EXCLUDED.customers,
    customer_versions = EXCLUDED.customer_versions, sellers = EXCLUDED.sellers
"""


def run_pipeline(mode: str, database: str, only_tests: str | None = None, export: bool = True) -> dict:
    engine = get_engine(database)
    batch = new_batch_id(engine)
    summary: dict = {"batch": batch, "mode": mode, "stages": {}, "fails": []}
    t_all = time.perf_counter()

    def stage(name):
        t0 = time.perf_counter()
        return lambda info: summary["stages"].__setitem__(name, {"seconds": round(time.perf_counter() - t0, 1), **info})

    with job_run(engine, batch, f"pipeline.{mode}", "pipeline") as pipe:
        done = stage("extract")
        res = extract(engine, batch, mode)
        done({"rows": sum(r["rows"] for r in res)})

        done = stage("seeds")
        done({"rows": sum(load_seeds(engine, batch).values())})

        done = stage("ods")
        if mode == "full":
            with engine.begin() as conn:
                conn.exec_driver_sql("CALL ods.truncate_data()")
        res = call_procedures(engine, batch, "ods", ODS_PROCS)
        done({"inserted": sum(r["inserted"] for r in res), "rejected": sum(r["rejected"] for r in res)})

        done = stage("dim")
        done(load_dimensions(engine, batch, mode))

        done = stage("fact")
        done(load_facts(engine, batch))

        done = stage("tests")
        with job_run(engine, batch, "tests.run", "test") as tr:
            passed, failed, fails = run_tests(engine, batch, only_tests)
            tr.rows_read, tr.rows_rejected = passed + failed, failed
        done({"passed": passed, "failed": failed, "eda": "%d/%d" % run_tests.last_info})
        summary["fails"] = fails

        with engine.begin() as conn:
            conn.execute(text(SNAPSHOT_SQL), {"b": batch, "m": mode})

        if export and not fails:
            done = stage("export")
            r = subprocess.run([sys.executable, str(config.ROOT / "scripts" / "export_powerbi.py"), "--database", database],
                               capture_output=True, text=True, cwd=config.ROOT)
            if r.returncode != 0:
                raise RuntimeError("export_powerbi failed: " + (r.stderr or r.stdout)[-500:])
            done({"files": r.stdout.count(".csv:")})
        pipe.rows_inserted = sum(s.get("inserted", 0) for s in summary["stages"].values() if isinstance(s.get("inserted", 0), int))
        pipe.rows_rejected = failed
    summary["seconds"] = round(time.perf_counter() - t_all, 1)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--database", default=config.DB_NAME)
    parser.add_argument("--only-tests", help="run only the test files whose name contains this text")
    parser.add_argument("--no-export", action="store_true", help="skip exports/powerbi CSV export")
    args = parser.parse_args()
    try:
        s = run_pipeline(args.mode, args.database, args.only_tests, export=not args.no_export)
    except Exception as exc:    # the failing job already has status 'failed' in etl_log.job_run
        print(f"PIPELINE FAILED ({args.mode}): {type(exc).__name__}: {str(exc)[:600]}", file=sys.stderr)
        sys.exit(1)
    print(f"pipeline {s['mode']} batch {s['batch']}: " + "; ".join(f"{k} {v}" for k, v in s["stages"].items()) + f"; total {s['seconds']}s")
    for f in s["fails"]:
        print(f"  FAIL [{f['file']}] {f['check']} on {f['table']}: expected {f['expected']}, actual {f['actual']}")
    sys.exit(1 if s["fails"] else 0)


if __name__ == "__main__":
    main()

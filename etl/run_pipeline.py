"""Orchestrate the warehouse pipeline:  python -m etl.run_pipeline --mode full|incremental

Stages run in order, one batch_id per run, every job writes etl_log.job_run; any error stops the run (status 'failed').
    extract (oltp/crm -> staging) -> seeds -> ods -> [dim] -> tests
Later phases add fact / mart / export stages to STAGES.
"""
from __future__ import annotations

import argparse
import sys
import time

from . import config
from .db import get_engine
from .extract import extract
from .load_dw import load_dimensions
from .load_seeds import load_seeds
from .log import new_batch_id
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


def run_pipeline(mode: str, database: str, only_tests: str | None = None) -> dict:
    engine = get_engine(database)
    batch = new_batch_id(engine)
    summary: dict = {"batch": batch, "mode": mode, "stages": {}}
    t_all = time.perf_counter()

    def stage(name):
        t0 = time.perf_counter()
        return lambda info: summary["stages"].__setitem__(name, {"seconds": round(time.perf_counter() - t0, 1), **info})

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

    done = stage("tests")
    passed, failed, fails = run_tests(engine, batch, only_tests)
    done({"passed": passed, "failed": failed})
    summary["fails"] = fails
    summary["seconds"] = round(time.perf_counter() - t_all, 1)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["full", "incremental"], default="full")
    parser.add_argument("--database", default=config.DB_NAME)
    parser.add_argument("--only-tests", help="run only the test files whose name contains this text")
    args = parser.parse_args()
    s = run_pipeline(args.mode, args.database, args.only_tests)
    print(f"pipeline {s['mode']} batch {s['batch']}: " + "; ".join(f"{k} {v}" for k, v in s["stages"].items()) + f"; total {s['seconds']}s")
    for f in s["fails"]:
        print(f"  FAIL [{f['file']}] {f['check']} on {f['table']}: expected {f['expected']}, actual {f['actual']}")
    sys.exit(1 if s["fails"] else 0)


if __name__ == "__main__":
    main()
